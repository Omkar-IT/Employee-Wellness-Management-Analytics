# Milestone 3: Emotion Detection & Journal Analytics

## Project Objective
The objective of this milestone is to integrate emotion detection, sentiment scoring, and journal management with database persistence into the Employee Wellness Management platform. This allows the system to analyze daily journal entries, predict dominant emotions, and compute VADER sentiment scores to track employee well-being.

## Model Used
* **Emotion Detection:** `bhadresh-savani/bert-base-go-emotion` (Transformer-based BERT model)
* **Sentiment Analysis:** VADER (Valence Aware Dictionary and sEntiment Reasoner)
* **Text Preprocessing:** `spaCy`, `ftfy`, `langdetect`, `stopwordsiso`, and `deep-translator`.

## Emotion Detection Pipeline
1. User submits a journal entry or uploads a file via the Streamlit frontend.
2. The text passes through the NLP pipeline (normalization, language detection, emoji removal, translation to English, stopword removal, and lemmatization).
3. The cleaned English text is passed to the BERT Emotion pipeline to extract the dominant emotion from 28 GoEmotions labels mapped to 6 core app labels.

## Confidence Score Calculation
The confidence score is derived directly from the Hugging Face `pipeline` output. The model returns probability scores for all mapped labels, and the score corresponding to the dominant predicted emotion is extracted and stored as a percentage.

## Sentiment Analysis
The VADER analyzer computes polarity scores on the translated text, generating:
* Positive, Negative, and Neutral Scores.
* **Compound Score:** Stored in the PostgreSQL database and used to classify overall sentiment as Positive (>= 0.05), Negative (<= -0.05), or Neutral.

## Database Schema (PostgreSQL)
The `mood_logs` table schema handles persistence:
* `id` (SERIAL PRIMARY KEY)
* `user_id` (INTEGER FK to users table)
* `mood_date` (DATE)
* `sentiment` (VARCHAR) - Derived from VADER
* `emotion` (VARCHAR) - Derived from BERT
* `compound_score` (REAL)
* `confidence` (REAL)
* `journal_text` (TEXT)
* `source` (VARCHAR) - e.g., 'nlp' or 'manual'

## API Endpoints (FastAPI)
* `POST /analyze-text`: Accepts raw text from the Journal, runs the full NLP pipeline, and returns emotion and sentiment JSON data.
* `POST /analyze`: Accepts `.csv` or `.txt` file uploads, extracts text, runs the NLP pipeline, and returns analysis.
* `POST /chat`: Support chatbot endpoint utilizing Qwen2.5 to provide wellness responses.

## Sample Input & Output
**Input:** "I had a highly productive day today and felt great!"
**Output:** 
- Final Sentiment: Positive 😊 (Compound: 0.82)
- Final Emotion: Happy 😊 (Confidence: 96%)
- Emotion Distribution: Happy (0.96), Neutral (0.02), etc.

## Observations
* Integrating `stopwordsiso` allowed for dynamic, multi-lingual stopword removal without hardcoding lists.
* Loading the BERT emotion model via lazy-loading on the backend significantly improved repeated API call performance.