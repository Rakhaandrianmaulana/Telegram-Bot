import logging
import os
import utils  # File utilitas kita

from dotenv import load_dotenv
from telegram import Update, constants
from telegram.error import BadRequest, TelegramError
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Mengatur logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Memuat variabel dari file .env
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    logger.error("TELEGRAM_TOKEN atau GEMINI_API_KEY tidak ditemukan di .env file!")
    exit()

# --- (PERUBAHAN DI SINI) ---
# Konfigurasi Gemini API saat bot pertama kali jalan
if not utils.configure_gemini(GEMINI_API_KEY):
    logger.error(
        "API Key Gemini GAGAL dikonfigurasi. "
        "Bot akan tetap jalan, tapi perintah /ai akan gagal."
    )
else:
    logger.info("API Key Gemini berhasil dikonfigurasi.")
# --- (AKHIR PERUBAHAN) ---


# --- PENANGAN PERINTAH ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mengirim pesan selamat datang saat /start."""
    user = update.effective_user
    username = user.username or user.first_name
    
    # Daftarkan pengguna ke database
    utils.get_user(user.id, username)
    
    welcome_text = f"Halo, @{username}!\nSelamat datang di Bot Canggih. Silakan pilih menu."
    keyboard = utils.main_menu_keyboard()
    await update.message.reply_text(welcome_text, reply_markup=keyboard)

async def ai(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menangani perintah /ai [prompt]."""
    # (Tidak ada perubahan di fungsi ini, sudah aman)
    
    user = update.effective_user
    prompt = " ".join(context.args)

    if not prompt:
        await update.message.reply_text(
            "Silakan berikan prompt setelah /ai.\nContoh:\n`/ai Jelaskan apa itu black hole?`",
            parse_mode=constants.ParseMode.MARKDOWN
        )
        return

    loading_msg = await update.message.reply_text("🧠 Sedang memproses permintaan AI Anda... Mohon tunggu.")
    
    # 1. Dapatkan respon dari API (sekarang pakai library google.genai)
    response_text = await utils.call_gemini_api(prompt)
    
    # 2. Kirim respon
    
    # Cek jika ini pesan error dari utils.py
    if response_text.startswith("ERROR:"):
        logger.error(f"Fungsi AI mengembalikan error: {response_text}")
        await loading_msg.edit_text(response_text)
        return

    # Jika BUKAN error, coba kirim sebagai MARKDOWN
    try:
        await loading_msg.edit_text(response_text, parse_mode=constants.ParseMode.MARKDOWN)
    
    except (BadRequest, TelegramError) as e:
        # JIKA GAGAL PARSING (Error "Can't parse entities")
        if "Can't parse entities" in str(e):
            logger.warning(f"Gagal parse Markdown dari AI: {e}. Mengirim sebagai plain text.")
            try:
                # Fallback: Kirim sebagai teks biasa (plain text)
                await loading_msg.edit_text(response_text)
            except Exception as e_fallback:
                logger.error(f"Gagal mengirim fallback plain text: {e_fallback}")
                await loading_msg.edit_text("Maaf, terjadi error ganda. Respon AI tidak bisa ditampilkan.")
        else:
            # Error Telegram lainnya
            logger.error(f"Error Telegram saat mengirim: {e}")
            await loading_msg.edit_text(f"Maaf, terjadi kesalahan Telegram: {e}")
            
    except Exception as e:
        # Error lain
        logger.error(f"Error tidak dikenal saat mengirim pesan: {e}")
        await loading_msg.edit_text(f"Maaf, terjadi kesalahan tak terduga saat mengirim: {e}")


# --- PENANGAN PESAN ---
# (Tidak ada perubahan di sini)
async def message_counter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message and update.message.text and update.message.chat.type == 'private':
        user = update.effective_user
        utils.update_message_count(user.id, user.username or user.first_name)

# --- PENANGAN TOMBOL (CALLBACK QUERY) ---
# (Tidak ada perubahan di sini)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_info = query.from_user
    user = utils.get_user(user_info.id, user_info.username or user_info.first_name)

    text = ""
    keyboard = None
    parse_mode = constants.ParseMode.MARKDOWN

    if data == "my_info":
        text = (
            f"--- Info Akun Anda ---\n\n"
            f"👤 **Username:** @{user.get('username', 'N/A')}\n"
            f"🔢 **User ID:** `{user.get('id')}`\n"
            f"💬 **Total Pesan:** {user.get('message_count', 0)}\n"
            f"🗓 **Terdaftar:** {user.get('registered_at', 'N/A').split('T')[0]}"
        )
        keyboard = utils.back_menu_keyboard('main_menu')

    elif data == "ai_help":
        text = (
            "**Bantuan Fitur AI (Gemini)**\n\n"
            "Kirim perintah dengan format:\n"
            "`/ai [pertanyaan Anda]`\n\n"
            "Contoh:\n"
            "`/ai Siapa penemu Python?`\n\n"
            "Bot akan merespon dengan jawaban yang dihasilkan oleh AI."
        )
        keyboard = utils.back_menu_keyboard('main_menu')

    elif data == "about_bot":
        text = (
            "**Bot Canggih v1.0 (Python)**\n\n"
            "Dibuat dengan `python-telegram-bot`.\n"
            "Fitur:\n"
            "- Async & Non-blocking\n"
            "- Database JSON (`database.json`)\n"
            "- Integrasi Gemini AI (via `google.genai`)" # <-- Diupdate
        )
        keyboard = utils.back_menu_keyboard('main_menu')

    elif data == "main_menu":
        text = "Menu Utama:"
        keyboard = utils.main_menu_keyboard()
        parse_mode = None

    try:
        await query.edit_message_text(
            text, 
            reply_markup=keyboard,
            parse_mode=parse_mode
        )
    except BadRequest as e:
        if "Message is not modified" in str(e):
            pass
        else:
            logger.warning(f"Error di button_handler (fallback ke plain): {e}")
            try:
                await query.edit_message_text(text, reply_markup=keyboard)
            except Exception as e_fallback:
                logger.error(f"Gagal fallback button_handler: {e_fallback}")


# --- FUNGSI UTAMA ---
# (Tidak ada perubahan di sini)
def main() -> None:
    """Mulai bot."""
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ai", ai))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, message_counter)
    )

    logger.info("Bot sedang berjalan...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

