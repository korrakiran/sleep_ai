# Sleep Paralysis AI

> AI-powered health app that tracks daytime behaviour and predicts sleep paralysis episodes using Machine Learning.

![Tech Stack](https://img.shields.io/badge/Flask-3.0-blue) ![ML](https://img.shields.io/badge/scikit--learn-RandomForest-orange) ![PWA](https://img.shields.io/badge/PWA-installable-green)

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 Auth | JWT-based signup / login |
| 📝 Daily Tracker | Log stress, sleep, screen time, horror, caffeine, activity |
| 🤖 ML Prediction | RandomForest risk classifier + episode time regressor |
| ⏰ Smart Alarm | Auto-scheduled 30 min before predicted REM phase |
| 📊 Dashboard | Animated gauge, Chart.js graphs, AI insights |
| 💡 AI Insights | Personalised health recommendations |
| 📱 PWA | Installable on iPhone/Android from browser |

---

## 🗂 Folder Structure

```
sleep-paralysis-ai/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # App factory
│   │   ├── models/database.py   # SQLAlchemy models
│   │   ├── routes/              # auth, tracker, prediction, alarm, insights
│   │   └── ml/
│   │       ├── trainer.py       # RandomForest training + prediction
│   │       ├── insights.py      # AI Insights engine
│   │       └── models/          # Saved .pkl files (auto-generated)
│   ├── run.py                   # Flask entry point
│   ├── requirements.txt
│   └── .env                     # ← Set your variables here
├── frontend/
│   ├── index.html               # SPA with all screens
│   ├── styles.css               # Dark glassmorphism design
│   ├── app.js                   # All logic (auth, charts, API)
│   └── manifest.json            # PWA manifest
├── seed.py                      # Create demo user
├── Procfile                     # Render/Heroku deploy
├── .gitignore
└── README.md
```

---

## ⚙️ Environment Variables (backend/.env)

```env
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
DATABASE_URL=sqlite:///sleep_paralysis.db
CORS_ORIGINS=http://localhost:3000,http://localhost:5000
MODEL_PATH=ml/models/
PORT=5000
```

---

## 🚀 Running Locally (Step by Step)

### 1 — Backend

```bash
cd sleep-paralysis-ai/backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python ../run.py
```

> ML models train automatically on first launch (~10 seconds).  
> API runs at **http://localhost:5000**

### 2 — Seed Demo Data (optional)

```bash
# From project root
python seed.py
```

Login with: `demo@sleep.ai` / `demo1234`

### 3 — Frontend

```bash
cd frontend
# Any static server works:
npx serve .
# OR Python:
python -m http.server 3000
```

Open **http://localhost:3000** in your browser.

### 4 — Install as Mobile App (PWA)

- **iPhone**: Open in Safari → Share → "Add to Home Screen"
- **Android**: Open in Chrome → Menu → "Install App" / "Add to Home Screen"

---

## 🌐 API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/signup` | No | Create account |
| POST | `/api/auth/login` | No | Login → JWT |
| GET | `/api/auth/profile` | Yes | Get profile |
| POST | `/api/tracker/log` | Yes | Submit daily log |
| GET | `/api/tracker/logs` | Yes | Get logs |
| GET | `/api/tracker/stats` | Yes | Aggregated stats |
| POST | `/api/predict/analyze` | Yes | Run ML prediction |
| GET | `/api/predict/latest` | Yes | Latest prediction |
| GET | `/api/predict/history` | Yes | Prediction history |
| GET | `/api/alarm/` | Yes | Get alarms |
| POST | `/api/alarm/create` | Yes | Create alarm |
| PUT | `/api/alarm/{id}/dismiss` | Yes | Dismiss alarm |
| GET | `/api/insights/tips` | No | General tips |
| GET | `/api/health` | No | Health check |

---

## ☁️ Deploying to Render

1. Push to GitHub
2. Create new **Web Service** on [render.com](https://render.com)
3. Set **Build Command**: `pip install -r backend/requirements.txt`
4. Set **Start Command**: `gunicorn --chdir backend run:app`
5. Add environment variables from `.env` in the Render dashboard
6. Deploy!

---

## 🧠 ML Model Details

| Model | Algorithm | Target | Accuracy |
|---|---|---|---|
| Risk Classifier | RandomForest (200 trees) | Low/Medium/High | ~85% |
| Episode Regressor | RandomForest (200 trees) | Hour of episode | MAE ~0.4h |

**Features used**: stress level, horror exposure, screen time, sleep hours, caffeine, physical activity, bedtime hour, nap taken, sleep position

---

## 📱 Demo Credentials

```
Email:    demo@sleep.ai
Password: demo1234
```

---

*Built with Flask + scikit-learn + vanilla JS. Designed for hackathons & portfolios.*
