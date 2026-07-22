"""SQLite session logging for analyzed transcripts."""

from __future__ import annotations

import sqlite3
import os
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(__file__), "sessions.db")


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the sessions table if it doesn't exist."""
    conn = _get_conn()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            session_id   TEXT PRIMARY KEY,
            timestamp    TEXT NOT NULL,
            verdict      TEXT NOT NULL,
            confidence   INTEGER NOT NULL,
            transcript   TEXT NOT NULL,
            red_flags    TEXT NOT NULL,
            recommended  TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def log_session(
    session_id: str,
    verdict: str,
    confidence: int,
    transcript: str,
    red_flags_json: str,
    recommended_action: str,
) -> None:
    """Insert a new analysis session."""
    conn = _get_conn()
    conn.execute(
        """
        INSERT INTO sessions (session_id, timestamp, verdict, confidence, transcript, red_flags, recommended)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            session_id,
            datetime.now(timezone.utc).isoformat(),
            verdict,
            confidence,
            transcript,
            red_flags_json,
            recommended_action,
        ),
    )
    conn.commit()
    conn.close()


def get_recent_sessions(limit: int = 20) -> list[dict]:
    """Return the most recent N sessions, newest first."""
    conn = _get_conn()
    rows = conn.execute(
        "SELECT session_id, timestamp, verdict, confidence, transcript FROM sessions ORDER BY timestamp DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    results = []
    for r in rows:
        snippet = r["transcript"][:120] + ("…" if len(r["transcript"]) > 120 else "")
        results.append(
            {
                "session_id": r["session_id"],
                "timestamp": r["timestamp"],
                "verdict": r["verdict"],
                "confidence": r["confidence"],
                "snippet": snippet,
            }
        )
    return results
