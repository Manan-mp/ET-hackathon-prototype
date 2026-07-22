"""Citizen Fraud Shield — FastAPI application."""

from __future__ import annotations

import json
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

import db
import llm_client
from models import (
    AnalyzeRequest,
    AnalyzeResponse,
    ErrorResponse,
    SessionSummary,
    TranslateRequest,
    TranslateResponse,
)
from sample_transcripts import SAMPLES


# ── Lifespan ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    yield


# ── App ──────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Citizen Fraud Shield",
    description="AI-powered detector for digital-arrest scams.",
    version="1.0.0",
    lifespan=lifespan,
)


# ── API Routes ───────────────────────────────────────────────────────────────

@app.post(
    "/api/analyze",
    response_model=AnalyzeResponse,
    responses={500: {"model": ErrorResponse}},
)
async def analyze(req: AnalyzeRequest):
    """Analyze a transcript for digital-arrest scam patterns."""
    try:
        result = await llm_client.analyze_transcript(req.transcript)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    session_id = uuid.uuid4().hex[:12]

    # Log to SQLite
    try:
        db.log_session(
            session_id=session_id,
            verdict=result["verdict"],
            confidence=result["confidence"],
            transcript=req.transcript,
            red_flags_json=json.dumps(result["red_flags"]),
            recommended_action=result["recommended_action"],
        )
    except Exception:
        pass  # Don't fail the request if logging fails

    return AnalyzeResponse(
        verdict=result["verdict"],
        confidence=result["confidence"],
        red_flags=result["red_flags"],
        recommended_action=result["recommended_action"],
        session_id=session_id,
    )


@app.get("/api/sessions", response_model=list[SessionSummary])
async def get_sessions(limit: int = 20):
    """Return recent analyzed sessions for the dashboard."""
    return db.get_recent_sessions(limit=limit)


@app.get("/api/samples")
async def get_samples():
    """Return pre-written sample transcripts for the demo buttons."""
    return SAMPLES


@app.post(
    "/api/translate",
    response_model=TranslateResponse,
    responses={500: {"model": ErrorResponse}},
)
async def translate(req: TranslateRequest):
    """Translate text into a target language using Gemini."""
    try:
        result = await llm_client.translate_text(req.text, req.language)
        return TranslateResponse(**result)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Serve Frontend ───────────────────────────────────────────────────────────

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return FileResponse("static/index.html")
