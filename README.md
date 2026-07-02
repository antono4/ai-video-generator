# 🎬 AI Video Creator Agent

Aplikasi web modern yang menghasilkan video pendek dari teks prompt menggunakan kecerdasan buatan. Aplikasi ini membuat script video, membuat gambar untuk setiap adegan, dan merakitnya menjadi video MP4 vertikal (9:16) yang cocok untuk Shorts/Reels/TikTok.

![Dark Glassmorphism UI](https://via.placeholder.com/800x450/0a0e17/6366f1?text=AI+Video+Creator)

## ✨ Fitur

- **🎬 Script Generation** - Pembuatan script video dengan AI
- **🖼️ Image Generation** - Membuat gambar adegan (dengan integrasi DALL-E, Leonardo AI)
- **🎥 Video Assembly** - Menggabungkan gambar dengan text overlay menjadi MP4
- **📱 Mobile-First** - Format vertikal 9:16 optimized untuk Shorts/Reels
- **🌙 Dark Glassmorphism UI** - Aesthetic dashboard premium
- **⚡ Real-time Progress** - Update status langsung saat generate video
- **📊 Preview & Download** - Lihat dan unduh video langsung

---

## 🚀 Cara Instalasi

### Prasyarat
- Python 3.8 atau lebih tinggi
- Git
- Koneksi internet (untuk fitur AI penuh, opsional)

### Langkah 1: Clone Repository

```bash
git clone https://github.com/antono4/ai-video-generator.git
cd ai-video-generator
```

### Langkah 2: Setup Python Environment

```bash
cd backend

# Buat virtual environment
python3 -m venv venv

# Aktifkan virtual environment
# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### Langkah 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Langkah 4: Jalankan Server

```bash
# Cara 1: Menggunakan script startup
chmod +x start.sh
./start.sh

# Cara 2: Jalankan manual
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Langkah 5: Buka di Browser

```
http://localhost:8000
```

---

## 📖 Cara Penggunaan

### 1. Halaman Utama

Saat membuka aplikasi, Anda akan melihat antarmuka Dark Glassmorphism dengan:
- **Area input** untuk memasukkan topik video
- **Pilihan durasi** video (15, 30, 60, atau 90 detik)
- **Pilihan gaya** visual (Cinematic, Animated, Realistic, Abstract)
- **Tombol Generate Video** untuk memulai

### 2. Membuat Video

#### Langkah 1: Masukkan Topik
Di textarea, masukkan topik atau deskripsi video yang ingin Anda buat.

**Contoh:**
```
The future of artificial intelligence in healthcare
```
atau dalam Bahasa Indonesia:
```
Masa depan kecerdasan buatan dalam perawatan kesehatan
```

#### Langkah 2: Pilih Durasi
Pilih durasi video dari dropdown:
- **15 detik** - Video pendek, 3 adegan
- **30 detik** - Video sedang, 6 adegan (recommended)
- **60 detik** - Video panjang, 12 adegan
- **90 detik** - Video sangat panjang, 18 adegan

#### Langkah 3: Pilih Gaya
Pilih gaya visual untuk video:
- **Cinematic** - Gaya film dengan pencahayaan dramatis
- **Animated** - Gaya animasi kartun
- **Realistic** - Foto realistis
- **Abstract** - Gaya seni abstrak

#### Langkah 4: Klik Generate
Klik tombol **"Generate Video"** untuk memulai proses.

### 3. Proses Pembuatan Video

Setelah klik Generate, Anda akan melihat progress:
- **Progress Step 1: Generating Script** - AI membuat script video
- **Progress Step 2: Creating Images** - AI membuat gambar untuk setiap adegan  
- **Progress Step 3: Assembling Video** - Semua digabungkan menjadi video MP4

### 4. Preview dan Download

Setelah video selesai:
- Video akan muncul di player
- Klik **Play** untuk preview
- Klik **Download Video** untuk menyimpan
- Klik **Create New Video** untuk membuat video baru

---

## 🔧 Konfigurasi (Opsional)

### API Keys

Jika Anda ingin menggunakan AI yang sebenarnya, buat file `.env`:

```bash
cp .env.example .env
```

Edit `.env` dan tambahkan API key:

| Service | Key | Fungsi |
|---------|-----|--------|
| OpenAI | `OPENAI_API_KEY` | GPT-4 untuk script + DALL-E untuk gambar |
| Google | `GOOGLE_API_KEY` | Alternatif untuk script (Gemini) |
| Leonardo AI | `LEONARDO_API_KEY` | Alternatif untuk gambar |

> ⚠️ **Catatan:** Aplikasi dapat berjalan **tanpa API key** menggunakan mode demo.

### Mengubah Resolusi Video

Edit `backend/services/video_assembler.py`:

```python
# Format 9:16 vertikal (Shorts/Reels)
self.width = 1080
self.height = 1920
self.fps = 24
```

---

## 🔌 API Endpoints

| Endpoint | Method | Deskripsi |
|----------|--------|-----------|
| `/api/create-video` | POST | Pipeline lengkap (script → gambar → video) |
| `/api/generate-script` | POST | Generate script saja |
| `/api/generate-images` | POST | Generate gambar saja |
| `/api/generate-video` | POST | Gabung jadi video saja |
| `/api/status/{job_id}` | GET | Cek status job |
| `/api/download/{filename}` | GET | Download video |

### Contoh Request API

```bash
# Create video lengkap
curl -X POST http://localhost:8000/api/create-video \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Beautiful mountain landscapes",
    "duration": 30,
    "style": "cinematic"
  }'
```

---

## 🎨 Format Output

Video yang dihasilkan memiliki spesifikasi:
- **Resolusi:** 1080x1920 piksel (9:16 vertikal)
- **Format:** MP4 (H.264)
- **Frame Rate:** 24 FPS
- **Orientasi:** Vertikal (optimized untuk TikTok, Reels, Shorts)

---

## 🛠️ Troubleshooting

### Error: "FFmpeg not found"
```bash
# Ubuntu/Debian:
sudo apt install ffmpeg

# Mac:
brew install ffmpeg

# Windows: Download dari https://ffmpeg.org/download.html
```

### Server tidak bisa diakses
```bash
# Cek port 8000
lsof -i :8000

# Coba port berbeda
python -m uvicorn main:app --port 8080
```

### Video tidak muncul
- Cek folder `backend/output/`
- Pastikan video file sudah ter-generate
- Refresh browser

---

## 📁 Struktur Project

```
ai-video-creator/
├── backend/
│   ├── main.py                    # FastAPI server
│   ├── routes/
│   │   ├── video.py               # Video generation endpoints
│   │   └── status.py              # Job status tracking
│   ├── services/
│   │   ├── script_generator.py    # LLM script generation
│   │   ├── image_generator.py      # AI image generation
│   │   └── video_assembler.py     # MoviePy video assembly
│   ├── output/                    # Generated videos & frames
│   ├── requirements.txt
│   └── .env / .env.example
├── frontend/
│   ├── index.html                 # Main application page
│   ├── styles.css                  # Dark Glassmorphism styles
│   └── app.js                     # Frontend JavaScript
├── start.sh                       # Startup script
└── README.md
```

---

## 💡 Tips Penggunaan

1. **Topik yang Jelas** - Semakin spesifik topik, semakin baik hasil video
2. **Durasi Optimal** - 30 detik adalah pilihan terbaik untuk kebanyakan penggunaan
3. **Gaya Cinematic** - Cocok untuk topik serius dan profesional
4. **Tunggu Process** - Pembuatan video membutuhkan waktu, harap tunggu sampai selesai
5. **API Key** - Untuk hasil terbaik, gunakan API key OpenAI atau Google

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **MoviePy** - Video processing dan assembly
- **Pillow** - Image manipulation
- **OpenAI SDK** - GPT-4 untuk script generation
- **Google Generative AI** - Gemini untuk script generation

### Frontend
- **Vanilla JavaScript** - No framework dependencies
- **CSS3** - Custom animations dan glassmorphism effects
- **HTML5** - Semantic markup

---

## 🌐 Dukungan Browser

- ✅ Chrome (disarankan)
- ✅ Firefox
- ✅ Safari
- ✅ Edge

---

## 📝 License

MIT License - Bebas digunakan dan dimodifikasi.

---

Built with ❤️ using FastAPI, Gemini, dan MoviePy
