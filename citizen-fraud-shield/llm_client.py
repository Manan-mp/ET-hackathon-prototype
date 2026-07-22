"""Gemini API wrapper for scam classification and translation."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from google import genai
from google.genai import types
from dotenv import load_dotenv

# ── Client Initialization ────────────────────────────────────────────────────

load_dotenv(dotenv_path=Path(__file__).with_name(".env"))

_client: genai.Client | None = None

MODEL = "gemini-2.5-flash"


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY environment variable is not set. "
                "Add it to citizen-fraud-shield/.env or export it before running."
            )
        _client = genai.Client(api_key=api_key)
    return _client


# ── System Prompt ────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """\
You are a fraud-pattern classifier specializing in "digital arrest" scams — a \
rapidly growing cybercrime pattern in India where fraudsters impersonate officials \
from CBI, ED, Customs, Police, RBI, TRAI, or other government agencies. They trap \
victims on prolonged video/voice calls, threaten immediate arrest or legal action, \
and extort money through bank transfers, UPI, or OTP theft.

These scam patterns have been widely documented by the Ministry of Home Affairs (MHA), \
which reports that victims lost Rs 1,776 crore in the first 9 months of 2024 alone.

## Your Task
Analyze the provided transcript or description of a call/message and classify it.

## Red-Flag Patterns to Check
- Claims of being a CBI / ED / Customs / Police / RBI / TRAI official
- Threats of "digital arrest", warrant, or immediate legal action
- Demands to stay on video call continuously / isolation instructions
- Urgency + secrecy ("don't tell anyone", "don't hang up")
- Requests for money transfer, OTP, UPI PIN, or "verification" payments
- Fake caller ID / spoofed government number claims
- Requests to download remote-access apps (AnyDesk, TeamViewer, QuickSupport)
- Mention of Aadhaar / PAN linked to criminal activity as a scare tactic
- Threats involving family members
- Claims about frozen bank accounts requiring immediate "verification"

## Classification Rules
- **SAFE**: The transcript shows no scam indicators; it appears to be a legitimate call/message.
- **SUSPICIOUS**: Some indicators are present but the transcript is ambiguous. Lean toward SUSPICIOUS rather than a confident SAFE or HIGH-RISK SCAM when uncertain.
- **HIGH-RISK SCAM**: Multiple strong scam indicators are clearly present.

Be conservative: if ambiguous, classify as SUSPICIOUS and state your uncertainty.

## Output Format
Return ONLY a valid JSON object (no markdown fences, no extra text) matching this schema:

{
  "verdict": "SAFE" | "SUSPICIOUS" | "HIGH-RISK SCAM",
  "confidence": <integer 0-100>,
  "red_flags": [
    {"flag": "<short label>", "explanation": "<evidence from the transcript>"}
  ],
  "recommended_action": "<plain-language guidance for the citizen>"
}

## Few-Shot Examples

### Example 1 — HIGH-RISK SCAM
Transcript: "I am Inspector Vikram from CBI Delhi. Your Aadhaar has been used to open 12 bank accounts for money laundering. An arrest warrant is ready. Stay on this video call — you are under digital arrest. Transfer Rs 2,00,000 to the RBI verification account immediately or armed police will come to your home in 20 minutes. Do not call anyone."

Response:
{"verdict": "HIGH-RISK SCAM", "confidence": 97, "red_flags": [{"flag": "Impersonation of CBI official", "explanation": "Caller claims to be 'Inspector Vikram from CBI Delhi' — real CBI officers do not cold-call citizens."}, {"flag": "Digital arrest threat", "explanation": "Caller states the victim is 'under digital arrest' — this is not a real legal concept."}, {"flag": "Demand for money transfer", "explanation": "Demands Rs 2,00,000 to an 'RBI verification account' — RBI does not operate such accounts."}, {"flag": "Isolation instructions", "explanation": "Instructs victim 'do not call anyone' to prevent them from seeking help."}, {"flag": "Urgency and intimidation", "explanation": "Threatens 'armed police will come in 20 minutes' to create panic."}], "recommended_action": "Hang up immediately. This is a well-known digital arrest scam. Real CBI officers never conduct arrests over video calls, and there is no such thing as 'digital arrest' in Indian law. Do NOT transfer any money. Report this at cybercrime.gov.in or call the National Cyber Crime Helpline at 1930."}

### Example 2 — SAFE
Transcript: "Hi, this is Priya from Flipkart delivery. Your order #FL123456 is out for delivery and will arrive between 2-4 PM today. The delivery person will call you when they are nearby. Thank you for shopping with Flipkart."

Response:
{"verdict": "SAFE", "confidence": 92, "red_flags": [], "recommended_action": "This appears to be a routine delivery notification. No action needed. If you did not place an order, you can verify by checking your Flipkart app directly."}
"""


# ── Core Analysis Function ───────────────────────────────────────────────────

def _extract_json(text: str) -> dict:
    """Extract JSON from the LLM response, handling markdown fences if present."""
    # Try direct parse first
    text = text.strip()
    # Remove markdown code fences if the model wraps them
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


async def analyze_transcript(transcript: str) -> dict:
    """Send a transcript to Gemini for scam classification. Returns parsed dict."""
    client = _get_client()

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=transcript,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.2,  # Low temperature for consistent classification
                max_output_tokens=2048,
            ),
        )
        raw = response.text
        if not raw:
            raise ValueError("Empty response from Gemini API")

        result = _extract_json(raw)

        # Validate expected fields
        for key in ("verdict", "confidence", "red_flags", "recommended_action"):
            if key not in result:
                raise ValueError(f"Missing required field '{key}' in LLM response")

        # Normalize verdict
        result["verdict"] = result["verdict"].upper().strip()
        if result["verdict"] not in ("SAFE", "SUSPICIOUS", "HIGH-RISK SCAM"):
            result["verdict"] = "SUSPICIOUS"  # fallback

        # Clamp confidence
        result["confidence"] = max(0, min(100, int(result["confidence"])))

        return result

    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse LLM response as JSON: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Gemini API call failed: {e}") from e


# ── Translation Function ────────────────────────────────────────────────────

TRANSLATE_PROMPT = """\
Translate the following text into {language}. Return ONLY a JSON object:
{{"translated_text": "<translated text>", "language": "{language}"}}

Text to translate:
{text}
"""


async def translate_text(text: str, language: str) -> dict:
    """Translate text using Gemini. Returns {"translated_text": ..., "language": ...}."""
    client = _get_client()

    try:
        prompt = TRANSLATE_PROMPT.format(language=language, text=text)
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=2048,
            ),
        )
        raw = response.text
        if not raw:
            raise ValueError("Empty response from Gemini API")
        return _extract_json(raw)

    except Exception as e:
        raise RuntimeError(f"Translation failed: {e}") from e
