# MoodMentor — Employee Wellness Management Analytics

AI-powered employee wellness analytics app built for Infosys Springboard
(Milestone 4: Final Integration, Testing & Enhancement).

## Architecture
- **frontend/** — Streamlit UI (`app.py`), login/dashboard/journal/weekly report
- **backend/** — FastAPI service (`backend.py`) + PostgreSQL access (`db.py`),
  auth/JWT/OTP (`auth.py`), email OTP delivery (`email_utils.py`),
  weekly wellness scoring & PDF report (`weekly_report.py`)
- **models/** — NLP pipeline (`nlp_pipeline.py`): language detection, VADER
  sentiment, fine-tuned BERT emotion classification (GoEmotions), and a
  Qwen2.5-0.5B-Instruct wellness chatbot
- **Milestone4/** — final integration notes / testing checklist
- **screenshots/** — dashboard & feature screenshots for submission

## Tech stack
Streamlit, FastAPI, PostgreSQL (Neon), JWT + bcrypt auth, VADER, BERT
(GoEmotions), Qwen2.5-0.5B-Instruct, deep-translator, spaCy, DeepFace.

## Environment variables (never committed — see `.env` locally)
`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `JWT_SECRET`,
`SMTP_EMAIL`, `SMTP_APP_PASSWORD`, `NGROK_AUTHTOKEN`

## Running (Google Colab)
1. Run the setup/install cell, then the `%%writefile` cells to generate
   `db.py`, `auth.py`, `email_utils.py`, `weekly_report.py`, `app.py`,
   `nlp_pipeline.py`, `backend.py`.
2. Run the backend: `uvicorn backend:app --host 0.0.0.0 --port 8000`
3. Run the frontend: `streamlit run app.py --server.port 8501`
4. Expose via ngrok for external access.

## Features implemented (Milestone 4)
- End-to-end pipeline: text input → preprocessing → sentiment/emotion → 
  recommendation → PostgreSQL → weekly report
- Auth: JWT sessions, bcrypt password hashing, email OTP verification
- Dashboard: date-range filters, emotion/sentiment filters, search,
  historical trend charts, PDF/CSV export
- Weekly wellness scoring across mood, journal emotion, sentiment,
  stress, sleep, workload, and journal consistency
- Face-based emotion detection (DeepFace)
- Wellness support chatbot (Qwen2.5-0.5B-Instruct) with crisis-keyword
  safety fallback