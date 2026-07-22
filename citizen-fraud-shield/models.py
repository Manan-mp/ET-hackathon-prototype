"""Pydantic v2 request/response schemas for the Citizen Fraud Shield API."""

from __future__ import annotations

from pydantic import BaseModel, Field


# ── Request ──────────────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    transcript: str = Field(
        ...,
        min_length=10,
        description="The call/message transcript or description to analyze.",
    )


# ── Response sub-models ─────────────────────────────────────────────────────

class RedFlag(BaseModel):
    flag: str = Field(..., description="Short label for the red-flag pattern.")
    explanation: str = Field(
        ..., description="Evidence from the transcript supporting this flag."
    )


class AnalyzeResponse(BaseModel):
    verdict: str = Field(
        ..., description="SAFE | SUSPICIOUS | HIGH-RISK SCAM"
    )
    confidence: int = Field(
        ..., ge=0, le=100, description="Confidence score 0-100."
    )
    red_flags: list[RedFlag] = Field(default_factory=list)
    recommended_action: str = Field(
        ..., description="Plain-language guidance for the citizen."
    )
    session_id: str = Field(
        ..., description="Unique ID for this analysis session."
    )


class ErrorResponse(BaseModel):
    detail: str


# ── Session log (for the dashboard) ─────────────────────────────────────────

class SessionSummary(BaseModel):
    session_id: str
    timestamp: str
    verdict: str
    confidence: int
    snippet: str = Field(
        ..., description="First ~120 chars of the transcript for display."
    )


class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1)
    language: str = Field(..., description="Target language, e.g. 'Hindi', 'Tamil'")


class TranslateResponse(BaseModel):
    translated_text: str
    language: str
