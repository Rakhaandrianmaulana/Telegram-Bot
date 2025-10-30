🤖 Bot Telegram Canggih (Python)Sebuah kerangka bot Telegram canggih yang dibuat dengan Python. Bot ini sepenuhnya asynchronous, menggunakan database JSON untuk persistensi data, dan terintegrasi dengan Google Gemini AI tanpa perlu library tambahan (hanya httpx).✨ Fitur UtamaIntegrasi AI Canggih: Terhubung langsung ke gemini-1.5-flash untuk respon AI yang cepat.Asynchronous Penuh: Dibangun di atas python-telegram-bot (v20+) dan httpx untuk performa non-blocking.Database JSON: Menyimpan data pengguna (ID, username, jumlah pesan) secara otomatis di database.json.Sistem Tombol Penuh: Navigasi yang ramah pengguna menggunakan inline keyboard.Manajemen Rahasia: Menggunakan file .env untuk menyimpan token dan API key dengan aman.⚙️ PrasyaratSebelum memulai, pastikan Anda telah memiliki:Python (v3.9+): Unduh PythonToken Bot Telegram: Dapatkan dari @BotFather di Telegram.API Key Google Gemini: Dapatkan secara gratis dari Google AI Studio.🚀 Panduan Instalasi & KonfigurasiIkuti langkah-langkah ini untuk menjalankan bot Anda.1. Dapatkan File ProyekPastikan Anda memiliki semua file proyek dalam satu folder:/folder-bot-anda
│
├── 📜 bot.py             # Logika utama bot
├── 🛠️ utils.py           # Fungsi bantuan (API, DB, Keyboard)
├── 📦 requirements.txt   # Daftar pustaka Python
├── 🔑 .env               # (File untuk rahasia Anda)
└── 📖 README.md          # File panduan ini
2. Buat Lingkungan Virtual (Virtual Environment)Sangat disarankan untuk menggunakan lingkungan virtual (venv) agar dependensi proyek Anda tidak tercampur.Buka terminal di folder proyek Anda dan jalankan:# Untuk MacOS / Linux
python3 -m venv venv
source venv/bin/activate

# Untuk Windows
python -m venv venv
.\venv\Scripts\activate
Terminal Anda sekarang akan diawali dengan (venv).3. Install DependensiInstall semua pustaka yang diperlukan (python-telegram-bot, httpx, python-dotenv) menggunakan file requirements.txt:# Pastikan (venv) Anda aktif
pip install -r requirements.txt
4. Konfigurasi Rahasia Anda (PENTING)Buat file bernama .env di folder yang sama (jika belum ada). Salin dan tempel format di bawah ini ke dalam file .env tersebut, lalu ganti dengan token dan key Anda yang sebenarnya.# ❗️ Ganti dengan nilai Anda yang sebenarnya
# JANGAN BAGIKAN FILE INI KEPADA SIAPAPUN

TELEGRAM_TOKEN="123456:ABC-DEF123456789"
GEMINI_API_KEY="AIzaSy...YOUR_GEMINI_KEY_HERE"
5. Jalankan BotSetelah semua dependensi terinstal dan file .env dikonfigurasi, jalankan bot:python bot.py
Jika tidak ada error, Anda akan melihat log di terminal:INFO:__main__:Bot sedang berjalan...
Bot Anda sekarang aktif! Buka Telegram dan kirim perintah /start.📁 Penjelasan Struktur FileFileDeskripsibot.pyFile Utama. Menangani semua handler (perintah, tombol, pesan) dan menjalankan bot.utils.pyFile Utilitas. Berisi semua fungsi "pembantu" seperti load_database(), call_gemini_api(), dan main_menu_keyboard().requirements.txtDependensi. Daftar semua pustaka Python yang dibutuhkan oleh proyek ini agar pip tahu apa yang harus diinstal..envRahasia. Menyimpan kredensial sensitif (Token & API Key) agar aman dan tidak terlihat di dalam kode.database.jsonDatabase. File ini akan dibuat otomatis saat pengguna pertama mengirim /start. Isinya adalah data pengguna yang terdaftar.
