import json
import os
import httpx  # Pustaka HTTP async, modern pengganti 'requests'
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

DB_PATH = "database.json"

# --- FUNGSI DATABASE (JSON) ---

def load_database() -> dict:
    """Memuat database dari file. Jika tidak ada, buat baru."""
    if not os.path.exists(DB_PATH):
        save_database({})
        return {}
    
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error memuat database: {e}. Membuat database baru.")
        save_database({})
        return {}

def save_database(data: dict) -> None:
    """Menyimpan data ke file database JSON."""
    try:
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Error menyimpan database: {e}")

def get_user(user_id: int, username: str) -> dict:
    """Mendapatkan data pengguna. Jika tidak ada, buat baru."""
    db = load_database()
    user_id_str = str(user_id)  # Kunci JSON harus string
    
    if user_id_str not in db:
        db[user_id_str] = {
            "id": user_id,
            "username": username,
            "message_count": 0,
            "registered_at": datetime.now().isoformat()
        }
        save_database(db)
        
    return db[user_id_str]

def update_message_count(user_id: int, username: str) -> None:
    """Menambah hitungan pesan untuk pengguna."""
    db = load_database()
    user_id_str = str(user_id)
    
    # Pastikan pengguna ada
    user = get_user(user_id, username) 
    
    user["message_count"] = user.get("message_count", 0) + 1
    db[user_id_str] = user
    save_database(db)

# --- FUNGSI API (Gemini) ---

async def call_gemini_api(prompt: str, api_key: str) -> str:
    """Memanggil API Gemini (Flash model) secara asynchronous."""
    
    # Gunakan model Flash terbaru yang cepat
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
        ]
    }
    
    # Gunakan httpx.AsyncClient untuk panggilan non-blocking
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=60.0)
            
            # Memeriksa error HTTP (spt 404, 500, 403)
            response.raise_for_status() 
            
            data = response.json()
            
            # Ekstrak teks dari respon
            if "candidates" in data and data["candidates"]:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            elif "promptFeedback" in data:
                return f"Permintaan diblokir. Alasan: {data['promptFeedback']['blockReason']}"
            else:
                return "Maaf, AI tidak memberikan respon yang valid."
                
        except httpx.HTTPStatusError as e:
            # Error spesifik dari API (cth: API key salah)
            return f"Error API: {e.response.status_code} - {e.response.text}"
        except Exception as e:
            # Error lainnya (cth: timeout, koneksi)
            return f"Error saat menghubungi API: {e}"

# --- DEFINISI KEYBOARD ---

def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Membuat keyboard untuk menu utama."""
    keyboard = [
        [
            InlineKeyboardButton("👤 Info Saya", callback_data="my_info"),
            InlineKeyboardButton("🤖 Tanya AI", callback_data="ai_help")
        ],
        [
            InlineKeyboardButton("ℹ️ Tentang Bot", callback_data="about_bot")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def back_menu_keyboard(callback_data: str) -> InlineKeyboardMarkup:
    """Membuat keyboard dengan tombol 'Kembali'."""
    keyboard = [
        [
            InlineKeyboardButton("⬅️ Kembali", callback_data=callback_data)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
