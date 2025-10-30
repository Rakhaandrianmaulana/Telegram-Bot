import json
import logging
import os
import google.generativeai as genai  # <-- Import library resmi
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Konfigurasi logger
logger = logging.getLogger(__name__)

DB_FILE = "database.json"

# --- FUNGSI DATABASE ---
# (Tidak ada perubahan di sini, semua sama)

def load_database() -> dict:
    """Memuat database dari file JSON."""
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"users": {}}
    except json.JSONDecodeError:
        return {"users": {}}  # File rusak, mulai baru

def save_database(data: dict):
    """Menyimpan data ke file JSON."""
    try:
        with open(DB_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Gagal menyimpan database: {e}")

def get_user(user_id: int, username: str) -> dict:
    """Mendapatkan data pengguna, membuat baru jika belum ada."""
    db = load_database()
    user_id_str = str(user_id)
    
    if user_id_str not in db["users"]:
        db["users"][user_id_str] = {
            "id": user_id,
            "username": username,
            "registered_at": datetime.now().isoformat(),
            "message_count": 0
        }
        save_database(db)
        logger.info(f"Pengguna baru terdaftar: {username} (ID: {user_id})")
        
    return db["users"][user_id_str]

def update_message_count(user_id: int, username: str):
    """Menambah hitungan pesan pengguna."""
    db = load_database()
    user_id_str = str(user_id)
    
    # Pastikan pengguna ada di db (panggilan get_user membuat jika tidak ada)
    user = get_user(user_id, username) 
    
    user["message_count"] = user.get("message_count", 0) + 1
    db["users"][user_id_str] = user
    save_database(db)


# --- FUNGSI PANGGILAN API (BARU) ---

def configure_gemini(api_key: str) -> bool:
    """Mengkonfigurasi API key Gemini saat bot startup."""
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        logger.error(f"Gagal mengkonfigurasi Gemini (API Key salah?): {e}")
        return False

async def call_gemini_api(prompt: str) -> str:
    """
    Memanggil Google Gemini API menggunakan library resmi (asynchronous).
    Fungsi ini TIDAK melempar Exception, tapi mengembalikan string "ERROR:".
    """
    try:
        # Gunakan model 'flash' yang gratis dan cepat.
        # Anda benar, 'gemini-1.5-flash-latest' adalah nama yang tepat untuk free tier.
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        # Panggil secara asynchronous (jauh lebih baik dari `httpx` manual)
        response = await model.generate_content_async(prompt)
        
        # Cek jika respon diblokir oleh safety settings
        if not response.candidates:
            logger.warning(f"Respon Gemini diblokir (safety setting). Prompt: {prompt}")
            return "ERROR: Respon dari AI diblokir karena alasan keamanan (safety settings)."

        # Cek jika teksnya kosong
        if not response.text:
            logger.warning(f"Respon Gemini kosong. Response: {response}")
            return "ERROR: AI memberikan respon kosong."

        return response.text

    except Exception as e:
        # Tangkapan error umum (misal: API key salah, server down)
        logger.error(f"Error tidak terduga di call_gemini_api (google.genai): {e}")
        # Mengembalikan string error, BUKAN exception
        return f"ERROR: Terjadi kesalahan internal saat memanggil library AI: {e}"


# --- FUNGSI KEYBOARD ---
# (Tidak ada perubahan di sini, semua sama)

def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Membuat keyboard menu utama."""
    keyboard = [
        [InlineKeyboardButton("📊 Info Saya", callback_data="my_info")],
        [
            InlineKeyboardButton("🤖 Bantuan AI", callback_data="ai_help"),
            InlineKeyboardButton("ℹ️ Tentang Bot", callback_data="about_bot")
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

def back_menu_keyboard(callback_data: str = "main_menu") -> InlineKeyboardMarkup:
    """Membuat keyboard dengan tombol 'Kembali'."""
    keyboard = [
        [InlineKeyboardButton("« Kembali ke Menu", callback_data=callback_data)]
    ]
    return InlineKeyboardMarkup(keyboard)

