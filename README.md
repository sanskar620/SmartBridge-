# ⌂ Gruha Alankara — AI Interior Design Platform

> Transform any room into a masterpiece using AI analysis, style recommendations, and AR furniture visualization.

---

## ✨ Features

- 📸 **Room Upload & AI Analysis** — Upload a room photo; AI detects style, lighting, and space utilization
- 🛋️ **Furniture Recommendations** — Curated product matches filtered by detected style and room size
- 🪄 **AR Designer** — Place virtual furniture on your room image using WebGL (Three.js)
- 🤖 **Buddy AI Chat** — Chat with an interior design assistant for advice and bookings
- 🎙️ **Voice Input** — Speak your design queries using the mic button

---

## 🗂️ Project Structure

```
SmartBridge Project/
├── index.html          # Frontend — main page
├── style.css           # Frontend — styles
├── script.js           # Frontend — logic
├── vercel.json         # Vercel deploy config (static frontend)
├── .gitignore
└── backend/            # Flask REST API
    ├── app.py          # Application entry point
    ├── config.py       # Configuration
    ├── requirements.txt
    ├── ai/             # NLP, voice, and Buddy agent
    ├── routes/         # Flask blueprints (upload, design, booking, voice)
    ├── models/         # SQLAlchemy models
    ├── services/       # Business logic services
    ├── database/       # DB init + SQLite file
    └── storage/        # Uploaded & generated images (runtime)
```

---

## 🚀 Running Locally

### 1. Set up Python environment

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Start the backend server

```bash
python app.py
```

Server runs at **http://localhost:5000**

### 3. Open the frontend

Open `index.html` directly in a browser **or** navigate to `http://localhost:5000` (Flask serves it).

---

## ☁️ Deployment

### Frontend → Vercel (static)

1. Push this repo to GitHub
2. Go to [vercel.com](https://vercel.com) → **New Project** → Import your repo
3. Vercel auto-detects `vercel.json` and deploys the static frontend

> **Note:** After deploying, update the API base URL in `script.js` to point to your hosted backend URL.

### Backend → Render / Railway / any Python host

1. Set `DEBUG = False` in `config.py` for production
2. Add a `SECRET_KEY` environment variable on your host
3. Deploy the `backend/` folder as a Python/Flask app, start command: `python app.py`

---

## 🔑 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `gruha-alankara-secret-key-change-in-production` | Flask secret key — **change this in production** |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, Vanilla JS, Three.js |
| Backend | Python 3, Flask, Flask-SQLAlchemy |
| Database | SQLite |
| AI/ML | transformers, scikit-learn, OpenCV, Pillow |
| Voice | SpeechRecognition, gTTS |
| LLM Chain | LangChain |

---

## 📄 License

MIT © 2025 Gruha Alankara
