# Citizen Fraud Shield 🛡️

**AI-powered detector for "digital arrest" scams** — built for the ET AI Hackathon 2026 (Problem Statement 6: AI for Digital Public Safety).

## What It Does

Citizens paste a suspicious call/message transcript and get an instant AI-powered risk assessment:
- **Risk Verdict**: SAFE / SUSPICIOUS / HIGH-RISK SCAM
- **Confidence Score** (0-100)
- **Specific Red Flags** detected with evidence from the transcript
- **Recommended Action** in plain language
- **Multi-language translation** of the advisory (Hindi, Tamil, Telugu, Bengali)

## Quick Start

### 1. Install dependencies

```bash
cd citizen-fraud-shield
pip install -r requirements.txt
```

### 2. Set your Gemini API key

```bash
export GEMINI_API_KEY=your_api_key_here
```

### 3. Run the server

```bash
uvicorn main:app --reload
```

### 4. Open the app

Visit [http://localhost:8000](http://localhost:8000) in your browser.

## Architecture

```
User → Frontend (HTML/JS/Tailwind) → FastAPI → Gemini 2.5 Flash → SQLite Log → Dashboard
```

## API Endpoints

| Method | Path             | Description                          |
|--------|------------------|--------------------------------------|
| POST   | `/api/analyze`   | Analyze a transcript for scam patterns |
| GET    | `/api/sessions`  | List recent analyzed sessions        |
| GET    | `/api/samples`   | Get pre-written demo scenarios       |
| POST   | `/api/translate` | Translate advisory text              |
| GET    | `/`              | Serve the frontend                   |

## Tech Stack

- **Backend**: FastAPI + Python 3.12
- **LLM**: Google Gemini 2.5 Flash
- **Database**: SQLite
- **Frontend**: HTML + Vanilla JS + Tailwind CSS (CDN)

## Project Structure

```
citizen-fraud-shield/
├── main.py                  # FastAPI app, routes
├── llm_client.py            # Gemini API wrapper + prompt template
├── models.py                # Pydantic v2 schemas
├── db.py                    # SQLite session logging
├── sample_transcripts.py    # Demo scenario strings
├── static/
│   └── index.html           # Single-page frontend
├── requirements.txt
└── README.md
```
