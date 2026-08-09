# Employee Wellness Management Analytics - MoodMentor

MoodMentor is an AI-powered emotional wellness assistant designed to help employees track their moods, journal their thoughts, and receive actionable, personalized wellness recommendations. 

## Project Architecture
This project is separated into a modular frontend and backend architecture:
*   **Frontend**: Built with Streamlit, featuring a responsive dashboard, mood calendar, journal input, and PDF report generation.
*   **Backend**: Powered by FastAPI, handling JWT authentication, OTP email verification, database routing, and API endpoints.
*   **Database**: PostgreSQL (hosted via Neon) storing users, mood logs, and authentication codes safely.
*   **NLP & ML Pipeline**: 
    *   Language Detection & Translation (`langdetect`, `deep-translator`)
    *   Sentiment Analysis (`vaderSentiment`)
    *   Emotion Classification (`bhadresh-savani/bert-base-go-emotion` via Hugging Face)
    *   Conversational Wellness Chat (`Qwen/Qwen2.5-0.5B-Instruct` via Hugging Face)

## Directory Structure
*   `/Milestone4` - Contains the master Google Colab notebook for end-to-end execution.
*   `/frontend` - Streamlit application (`app.py`).
*   `/backend` - FastAPI server, database connections, recommendation logic, and NLP pipeline.
*   `/models` - Details regarding the dynamically loaded Hugging Face and spaCy models.
*   `/screenshots` - Visual demonstrations of the working application.

## How to Run (Local or Colab)
1. Clone this repository.
2. Install the required dependencies from `/backend/requirements.txt`.
3. Set up a `.env` file in the backend directory with your PostgreSQL credentials, JWT secret, and SMTP app passwords.
4. Start the FastAPI backend: `uvicorn backend:app --host 0.0.0.0 --port 8000`
5. Start the Streamlit frontend: `streamlit run app.py`