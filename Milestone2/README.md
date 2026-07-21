# Milestone 2: NLP Text Preprocessing Pipeline 📝

## Project Objective
The objective of this milestone is to build a robust Natural Language Processing (NLP) text preprocessing pipeline. This pipeline cleans, normalizes, and transforms raw multilingual textual data into a structured format, laying the groundwork for downstream sentiment analysis and emotion classification in the Employee Wellness Management Analytics project.

## NLP Pipeline Overview
This pipeline systematically processes raw text through a series of transformations:
1. **Input Handling:** Accepts direct text or file uploads (`.txt`, `.csv`).
2. **Language Detection:** Identifies the language of the text.
3. **Cleaning & Normalization:** Removes noise such as URLs, emails, HTML tags, punctuation, and numbers, while normalizing Unicode characters.
4. **Emoji Handling:** Extracts emojis for potential emotion analysis before removing them from the text.
5. **Linguistic Processing:** Tokenizes text, removes language-specific stop-words, and applies lemmatization to reduce words to their base forms.

## Technologies and Libraries Used
* **Environment:** Google Colaboratory (Python 3)
* **Libraries:** `pandas`, `re`, `string`, `unicodedata`, `langdetect`, `emoji`, `nltk`, `spacy`

## Google Colab Setup Instructions
1. Open [Google Colab](https://colab.research.google.com/).
2. Upload the `NLP_Preprocessing_Pipeline.ipynb` notebook.
3. Run the first cell to install the required dependencies (`!pip install langdetect emoji spacy`).
4. Execute the cells sequentially. When prompted, you can either type text directly or upload a `.txt`/`.csv` file.

## Preprocessing Workflow
1. **Unicode Normalization:** Converts text to NFKD format.
2. **Noise Removal:** Regex patterns strip out URLs, emails, and HTML tags.
3. **Emoji Extraction & Removal:** Emojis are captured into a list and then stripped from the main string.
4. **Punctuation & Number Removal:** Strips non-alphabetic characters.
5. **Lowercasing:** Standardizes the text case.
6. **Tokenization:** Splits sentences into individual words.
7. **Stop-word Removal:** Uses NLTK/SpaCy corpora matching the detected language to remove common, non-impactful words.
8. **Lemmatization:** Converts words to their dictionary root form.

## Sample Input and Output
* **Original Text:** `"I am feeling great today! 😁 Check out my blog: http://wellness.com. Étudiants, 12345!"`
* **Detected Language:** `en`
* **Final Preprocessed Text:** `['feel', 'great', 'today', 'etudiant']`

## Observations
* **Multilingual Handling:** The pipeline successfully adapts its stop-word lists based on the `langdetect` output. 
* **Emojis:** Extracting emojis prior to punctuation removal is crucial, as they contain high semantic value for emotion classification.
