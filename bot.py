import logging
import os
import utils  # File utilitas kita

from dotenv import load_dotenv
from telegram import Update, constants
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
    user = update.effective_user
    prompt = " ".join(context.args)

    if not prompt:
        await update.message.reply_text(
            "Silakan berikan prompt setelah /ai.\nContoh:\n`/ai Jelaskan apa itu black hole?`",
            parse_mode=constants.ParseMode.MARKDOWN
        )
        return

    # Kirim pesan "loading"
    loading_msg = await update.message.reply_text("🧠 Sedang memproses permintaan AI Anda... Mohon tunggu.")
    
    try:
        # Panggil API Gemini (secara asynchronous)
        response_text = await utils.call_gemini_api(prompt, GEMINI_API_KEY)
        
        # Edit pesan "loading" dengan hasil
        await loading_msg.edit_text(response_text, parse_mode=constants.ParseMode.MARKDOWN)
        
    except Exception as e:
        logger.error(f"Error memanggil Gemini: {e}")
        await loading_msg.edit_text(f"Maaf, terjadi kesalahan saat menghubungi AI: {e}")

# --- PENANGAN PESAN ---

async def message_counter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menghitung setiap pesan non-perintah dari pengguna."""
    # Pastikan itu adalah pesan teks dan bukan dari grup
    if update.message and update.message.text and update.message.chat.type == 'private':
        user = update.effective_user
        # Update hitungan pesan di database
        utils.update_message_count(user.id, user.username or user.first_name)

# --- PENANGAN TOMBOL (CALLBACK QUERY) ---

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menangani semua klik tombol inline."""
    query = update.callback_query
    await query.answer()  # Wajib untuk memberitahu Telegram
    
    data = query.data
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    
    user_info = query.from_user
    user = utils.get_user(user_info.id, user_info.username or user_info.first_name)

    if data == "my_info":
        info_text = (
            f"--- Info Akun Anda ---\n\n"
            f"👤 **Username:** @{user.get('username', 'N/A')}\n"
            f"🔢 **User ID:** `{user.get('id')}`\n"
            f"💬 **Total Pesan:** {user.get('message_count', 0)}\n"
            f"🗓 **Terdaftar:** {user.get('registered_at', 'N/A').split('T')[0]}"
        )
        await query.edit_message_text(
            info_text, 
            reply_markup=utils.back_menu_keyboard('main_menu'),
            parse_mode=constants.ParseMode.MARKDOWN
        )

    elif data == "ai_help":
        ai_help_text = (
            "**Bantuan Fitur AI (Gemini)**\n\n"
            "Kirim perintah dengan format:\n"
            "`/ai [pertanyaan Anda]`\n\n"
            "Contoh:\n"
            "`/ai Siapa penemu Python?`\n\n"
            "Bot akan merespon dengan jawaban yang dihasilkan oleh AI."
        )
        await query.edit_message_text(
            ai_help_text, 
            reply_markup=utils.back_menu_keyboard('main_menu'),
            parse_mode=constants.ParseMode.MARKDOWN
        )

    elif data == "about_bot":
        about_text = (
            "**Bot Canggih v1.0 (Python)**\n\n"
            "Dibuat dengan `python-telegram-bot`.\n"
            "Fitur:\n"
            "- Async & Non-blocking\n"
            "- Database JSON (`database.json`)\n"
            "- Integrasi Gemini AI (via `httpx`)"
        )
        await query.edit_message_text(
            about_text, 
            reply_markup=utils.back_menu_keyboard('main_menu'),
            parse_mode=constants.ParseMode.MARKDOWN
        )

    elif data == "main_menu":
        await query.edit_message_text(
            "Menu Utama:", 
            reply_markup=utils.main_menu_keyboard()
        )

# --- FUNGSI UTAMA ---

def main() -> None:
    """Mulai bot."""
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Tambahkan penangan
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ai", ai))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Penangan pesan untuk menghitung pesan (harus setelah perintah)
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, message_counter)
    )

    logger.info("Bot sedang berjalan...")
    # Jalankan bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
