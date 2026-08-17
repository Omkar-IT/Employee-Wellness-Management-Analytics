# 🧠 MoodMentor — Employee Wellness Management Analytics

> An AI-powered employee wellness analytics platform built for **Infosys Springboard**
> — Milestone 4: Final Integration, Testing & Enhancement 🎯

MoodMentor helps organizations understand and support employee wellbeing by combining
mood tracking, journaling, NLP-driven sentiment/emotion analysis, and personalized
recommendations into a single, easy-to-use dashboard.

---

## ✨ Overview

MoodMentor lets employees log their daily mood, write journal entries, and track
stress, sleep, and workload — while an AI pipeline analyzes text for sentiment and
emotion, generates weekly wellness reports, and offers a supportive chatbot for
day-to-day check-ins. Managers get an aggregated, privacy-conscious view of team
wellness trends.

---

## 🏗️ Architecture

```
Employee Wellness Management Analytics/
├── frontend/          🎨 Streamlit UI
├── backend/            ⚙️ FastAPI service + database logic
├── models/             🤖 NLP pipeline
├── Milestone4/          📋 Integration notes & testing checklist
├── screenshots/          🖼️ App screenshots for submission
├── requirements.txt     📦 Python dependencies
├── .gitignore            🚫 Excluded files (secrets, caches)
└── README.md              📖 You are here
```

| Layer | Folder | Key Files | Responsibility |
|---|---|---|---|
| 🎨 **Frontend** | `frontend/` | `app.py`, `welcome_image.py` | Streamlit UI — login, dashboard, journal, weekly report |
| ⚙️ **Backend** | `backend/` | `backend.py`, `db.py`, `auth.py`, `email_utils.py`, `weekly_report.py` | FastAPI service, PostgreSQL access, JWT/OTP auth, email delivery, wellness scoring & PDF generation |
| 🤖 **Models** | `models/` | `nlp_pipeline.py` | Language detection, sentiment analysis, emotion classification, wellness chatbot |
| 📋 **Milestone4** | `Milestone4/` | notes | Final integration & testing documentation |
| 🖼️ **Screenshots** | `screenshots/` | `.png` files | Visual proof of implemented features |

---

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| 🎨 Frontend | Streamlit |
| ⚙️ Backend | FastAPI, Uvicorn |
| 🗄️ Database | PostgreSQL (hosted on Neon) |
| 🔐 Authentication | JWT, bcrypt password hashing, email OTP verification |
| 💬 Sentiment Analysis | VADER |
| 😊 Emotion Classification | Fine-tuned BERT (GoEmotions dataset) |
| 🌍 Language Support | langdetect, deep-translator, spaCy |
| 🤖 Conversational AI | Qwen2.5-0.5B-Instruct |
| 📷 Facial Emotion Detection | DeepFace |
| 📊 Reporting | Matplotlib, ReportLab (PDF generation) |
| ☁️ Deployment (dev) | Google Colab + ngrok |

---

## 🔑 Environment Variables

⚠️ **Never committed to the repository** — configured locally via `.env` (excluded by `.gitignore`).

| Variable | Purpose |
|---|---|
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | PostgreSQL connection |
| `JWT_SECRET` | Signing authentication tokens |
| `SMTP_EMAIL`, `SMTP_APP_PASSWORD` | Sending OTP verification emails |
| `NGROK_AUTHTOKEN` | Exposing the app publicly during development |

---

## 🚀 Getting Started (Google Colab)

1. **Install dependencies & load secrets**
   Run the setup/install cell, then the `%%writefile` cells to generate:
   `db.py` → `auth.py` → `email_utils.py` → `weekly_report.py` → `app.py` → `nlp_pipeline.py` → `backend.py`

2. **Start the backend**
   ```bash
   uvicorn backend:app --host 0.0.0.0 --port 8000
   ```

3. **Start the frontend**
   ```bash
   streamlit run app.py --server.port 8501
   ```

4. **Expose the app**
   Use ngrok to generate a public URL and share it for testing/demo purposes. 🌐

---

## ✅ Features Implemented (Milestone 4)

### 🔄 End-to-End Pipeline
Text Input → Preprocessing → Sentiment & Emotion Analysis → Recommendation → PostgreSQL Storage → Weekly Report

### 🔐 Authentication & Security
- JWT-based session management
- bcrypt password hashing
- Email OTP verification for signup & password reset

### 📊 Enhanced Dashboard
- 📅 Date-range filters
- 😊 Emotion & sentiment filters
- 🔍 Search functionality
- 📈 Historical emotional trend visualizations
- 📄 PDF export
- 📑 CSV export

### 🧭 Weekly Wellness Scoring
A composite score built from real, stored data across:
- 🙂 Daily mood
- ✍️ Journal-derived emotion
- 💬 Sentiment
- 😰 Stress level
- 😴 Sleep hours
- 💼 Workload
- 📓 Journal consistency

*(Missing data points are never treated as zero — weights are redistributed dynamically.)*

### 🎯 Recommendation System
- Tested across multiple detected emotional states
- Validated for relevance to detected emotion/sentiment
- Supports feedback collection for continuous improvement

### 📷 Face-Based Emotion Detection
Real-time facial emotion recognition powered by DeepFace.

### 💬 Wellness Support Chatbot
Conversational support powered by Qwen2.5-0.5B-Instruct, with a **crisis-keyword safety fallback** that redirects to appropriate resources instead of generating a free-form reply in sensitive situations.

---

## 🧪 Testing Coverage

✔️ Valid, invalid, empty, multilingual, and edge-case text inputs
✔️ User registration, login, authentication & session handling
✔️ API endpoints, error handling & database operations
✔️ Full end-to-end integration across all modules

---

## 📌 Notes

- This project was developed as part of the **Infosys Springboard Employee
  Wellness Management Analytics** internship program (Team C).
- The chatbot is a wellness support tool and **not a substitute for professional
  medical or mental health advice**.

---

<p align="center">Made with ❤️ for a healthier, happier workplace</p>
