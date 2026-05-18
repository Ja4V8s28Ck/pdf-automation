# Manufacturing Document Digitization

AI-powered web application that digitizes handwritten manufacturing operational documents into structured, reviewable records with validation workflows and analytics.

## Features

- **Document Upload** — Upload images or PDFs of manufacturing operational documents
- **AI-Based Extraction** — Uses Google Gemini Vision API to extract structured data from handwritten forms
- **Review Workflow** — Edit, correct, and approve extracted records
- **Confidence Scoring** — Per-field confidence indicators highlighting uncertain extractions
- **Validation & Exception Handling** — Business rules flag missing, invalid, or suspicious values
- **Dashboard & Analytics** — Shift-wise, machine-wise, and status summaries with charts
- **Search & History** — Find past uploads and records by any field

## Tech Stack

- **Frontend/Backend**: Streamlit (Python)
- **AI/OCR**: Google Gemini 2.0 Flash API
- **Database**: SQLite via SQLAlchemy ORM
- **Charts**: Plotly

## Setup

1. Clone the repo:
   ```bash
   git clone <repo-url>
   cd pdf-automation
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your Gemini API key:
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```
   Get a key at: https://aistudio.google.com/apikey

4. Run the app:
   ```bash
   streamlit run app.py
   ```

5. Open http://localhost:8501 in your browser

## Project Structure

```
├── app.py                  # Main entry point with navigation
├── pages/
│   ├── 01_Upload.py        # Document upload & extraction
│   ├── 02_Review.py        # Review & edit extracted data
│   ├── 03_Dashboard.py     # Analytics & insights
│   └── 04_History.py       # Search & upload history
├── utils/
│   ├── config.py           # App configuration
│   ├── database.py         # SQLAlchemy models & operations
│   ├── extraction.py       # Gemini API integration
│   └── validation.py       # Business rules & validation
├── requirements.txt
├── .env.example
└── AGENTS.md
```

## Workflow

1. **Upload** → Upload a document image/PDF
2. **Extract** → AI extracts structured data with confidence scores
3. **Review** → Edit/correct data, view validation flags, save approved records
4. **Analyze** → Dashboard shows operational insights
5. **Search** → Find and revisit any past record

## Assumptions & Tradeoffs

- **Gemini API dependency**: Extraction quality depends on Gemini's vision capabilities. For production, consider fine-tuning or adding Tesseract as fallback.
- **SQLite**: Used for simplicity. Migrate to PostgreSQL for multi-user production deployment.
- **Single-user**: No authentication implemented. Add auth for multi-user workflows.
- **File storage**: Local filesystem. Use S3/GCS with Docker volumes for production.
- **PDF handling**: Images extracted from PDFs may need preprocessing. Current implementation handles direct image uploads best.
