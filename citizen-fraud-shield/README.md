# Citizen Fraud Shield

AI-powered detector for digital arrest scam calls and messages. This project was built for an online hackathon submission focused on digital public safety.

## Live Demo

Add the deployed application URL here:

```text
https://et-hackathon-prototype.onrender.com/
```
Judges can test the project by opening the live URL, pasting a suspicious call or message transcript, and clicking the analyze button.

## Problem

Digital arrest scams are fraud attempts where criminals impersonate officials from agencies such as Police, CBI, ED, Customs, RBI, TRAI, or similar authorities. They pressure citizens with fake legal threats, demand secrecy, keep victims on calls, and often ask for money transfers or sensitive information.

## Solution

Citizen Fraud Shield analyzes a user-provided transcript or message and returns:

- Risk verdict: SAFE, SUSPICIOUS, or HIGH-RISK SCAM
- Confidence score from 0 to 100
- Specific red flags found in the text
- Plain-language recommended action
- Translation of the advisory into selected Indian languages
- Recent analysis dashboard for demo review

## Tech Stack

- Backend: FastAPI and Python
- LLM: Google Gemini 2.5 Flash
- Database: SQLite
- Frontend: HTML, Tailwind CSS, and vanilla JavaScript

## Project Structure

```text
citizen-fraud-shield/
|-- main.py
|-- llm_client.py
|-- models.py
|-- db.py
|-- sample_transcripts.py
|-- static/
|   `-- index.html
|-- requirements.txt
|-- runtime.txt
|-- .env.example
`-- README.md
```

## Local Setup

1. Create and activate a virtual environment.

```bash
cd citizen-fraud-shield
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Create the local environment file.

```bash
cp .env.example .env
```

4. Add your Gemini API key to `.env`.

```text
GEMINI_API_KEY=your_gemini_api_key_here
```

5. Run the application.

```bash
uvicorn main:app --reload
```

6. Open the local app.

```text
http://localhost:8000
```

## Deployment

The repository includes `render.yaml` for deployment on Render.

Recommended deployment steps:

1. Push the repository to GitHub.
2. Create a new Blueprint deployment on Render.
3. Connect the repository.
4. Set the environment variable `GEMINI_API_KEY` in Render.
5. Deploy the service.
6. Add the deployed URL to the Live Demo section before submitting.

Render will use:

```text
Build command: pip install -r requirements.txt
Start command: uvicorn main:app --host 0.0.0.0 --port $PORT
Root directory: citizen-fraud-shield
```

## API Endpoints

| Method | Path | Description |
| --- | --- | --- |
| POST | `/api/analyze` | Analyze a transcript for scam patterns |
| GET | `/api/sessions` | Return recent analysis sessions |
| GET | `/api/samples` | Return sample demo transcripts |
| POST | `/api/translate` | Translate the recommended advisory |
| GET | `/` | Serve the web interface |

## Security Notes

- The Gemini API key is loaded from an environment variable.
- The local `.env` file is ignored by Git.
- Runtime SQLite data is ignored by Git.
- Python cache files, virtual environments, and OS files are ignored by Git.
- The app limits request sizes and dashboard query limits to reduce accidental misuse during judging.

## Judge Testing Guide

Use one of the sample scenarios in the interface or paste a custom transcript such as:

```text
I am calling from the cyber crime department. Your Aadhaar has been linked to illegal activity. Do not disconnect this call. You are under digital arrest and must transfer money for verification.
```

Expected behavior:

- The app should classify the message as high risk or suspicious.
- It should list red flags such as impersonation, urgency, digital arrest threat, and money transfer demand.
- It should provide a recommended action advising the user not to pay and to report the incident.
