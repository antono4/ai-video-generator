# AI Video Creator Agent

A modern web application that generates short videos from text prompts using AI. The app creates video scripts, generates scene images, and assembles them into vertical (9:16) MP4 videos suitable for Shorts/Reels.

![Dark Glassmorphism UI](https://via.placeholder.com/800x450/0a0e17/6366f1?text=AI+Video+Creator)

## ✨ Features

- **🎬 Script Generation** - AI-powered video script creation from text prompts
- **🖼️ Image Generation** - Create scene images (with API integration for DALL-E, Leonardo AI)
- **🎥 Video Assembly** - Stitch images with text overlays into MP4 videos
- **📱 Mobile-First** - 9:16 vertical format optimized for Shorts/Reels
- **🌙 Dark Glassmorphism UI** - Premium SaaS dashboard aesthetic
- **⚡ Real-time Progress** - Live status updates during video generation

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **MoviePy** - Video processing and assembly
- **Pillow** - Image manipulation
- **OpenAI SDK** - GPT-4 for script generation
- **Google Generative AI** - Gemini for script generation

### Frontend
- **Vanilla JavaScript** - No framework dependencies
- **CSS3** - Custom animations and glassmorphism effects
- **HTML5** - Semantic markup

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- API Keys (optional for demo mode)

### Installation

1. **Clone and navigate to the project:**
```bash
cd ai-video-creator
```

2. **Set up Python environment:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment (optional):**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

4. **Start the backend:**
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

5. **Access the application:**
Open `http://localhost:8000` in your browser

Or use the startup script:
```bash
chmod +x start.sh
./start.sh
```

## 🔑 API Keys (Optional)

The application works in demo mode without API keys. For production use:

| Service | Key | Purpose |
|---------|-----|---------|
| OpenAI | `OPENAI_API_KEY` | Script generation (GPT-4) + Image generation (DALL-E 3) |
| Google | `GOOGLE_API_KEY` | Alternative script generation (Gemini Pro) |
| Leonardo AI | `LEONARDO_API_KEY` | Alternative image generation |

## 📁 Project Structure

```
ai-video-creator/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── routes/
│   │   ├── video.py         # Video generation endpoints
│   │   └── status.py        # Job status tracking
│   ├── services/
│   │   ├── script_generator.py  # LLM script generation
│   │   ├── image_generator.py   # AI image generation
│   │   └── video_assembler.py   # MoviePy video assembly
│   ├── output/              # Generated videos and frames
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── index.html           # Main application page
│   ├── styles.css           # Dark Glassmorphism styles
│   ├── app.js               # Frontend JavaScript
│   └── package.json
├── start.sh                 # Startup script
└── README.md
```

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/generate-script` | POST | Generate video script from prompt |
| `/api/generate-images` | POST | Generate images for script scenes |
| `/api/generate-video` | POST | Assemble video from images |
| `/api/create-video` | POST | Full pipeline (script → images → video) |
| `/api/status/{job_id}` | GET | Check job status |
| `/api/download/{filename}` | GET | Download generated video |

### Example Request

```bash
curl -X POST http://localhost:8000/api/create-video \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "The future of space exploration",
    "duration": 30,
    "style": "cinematic"
  }'
```

## 🎨 UI Features

- **Dark Glassmorphism Design** - Translucent panels with blur effects
- **Animated Background** - Floating gradients and grid overlay
- **3D Hover Effects** - Perspective transforms on interactive elements
- **Progress Steps** - Visual workflow with script → images → video stages
- **Toast Notifications** - Non-intrusive status updates
- **Responsive Layout** - Mobile-first design

## 📹 Output Format

- **Resolution:** 1080x1920 (9:16 vertical)
- **Format:** MP4 (H.264)
- **Frame Rate:** 24 FPS
- **Quality:** Medium preset, CRF 23

## 🔧 Configuration

Edit `backend/.env` to customize:

```env
# Server
HOST=0.0.0.0
PORT=8000

# API Keys
OPENAI_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here

# Output
OUTPUT_DIR=./output
```

## 📝 License

MIT License - Feel free to use and modify.

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

---

Built with ❤️ using FastAPI, Gemini, and MoviePy
