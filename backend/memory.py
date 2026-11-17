"""
Conversational Memory Store with SQLite Persistence for GeetaGPT.
Persists conversation history across sessions, server restarts, and browser refreshes.
"""

import os
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

DB_PATH = os.path.join(os.path.dirname(__file__), "../../chat_history.sqlite3")


def init_db():
    """Initialize SQLite database for chat history."""
    Path(os.path.dirname(DB_PATH)).mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                agent TEXT,
                sources TEXT,
                timestamp TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_session_id ON messages(session_id)"
        )
        conn.commit()


init_db()


def add_message(
    session_id: str,
    role: str,
    content: str,
    agent: str = None,
    sources: List[str] = None
):
    """Save a single message to persistent history."""
    sources_json = json.dumps(sources or [])
    now = datetime.now().strftime("%I:%M %p")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO messages (session_id, role, content, agent, sources, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (session_id, role, content, agent, sources_json, now)
        )
        conn.commit()


def get_history(session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieve full history for a session (for UI restoration)."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT role, content, agent, sources, timestamp
            FROM messages
            WHERE session_id = ?
            ORDER BY id ASC
            LIMIT ?
            """,
            (session_id, limit)
        )
        rows = cursor.fetchall()

    messages = []
    for r in rows:
        messages.append({
            "role": r["role"],
            "content": r["content"],
            "agent": r["agent"],
            "sources": json.loads(r["sources"]) if r["sources"] else [],
            "timestamp": r["timestamp"]
        })
    return messages


def get_llm_context(session_id: str, max_turns: int = 6) -> List[Dict[str, str]]:
    """
    Get the last N dialogue turns in OpenAI format:
    [{role: 'user', content: ...}, {role: 'assistant', content: ...}]
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        # Retrieve the most recent 2 * max_turns messages
        cursor.execute(
            """
            SELECT role, content
            FROM messages
            WHERE session_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (session_id, max_turns * 2)
        )
        rows = cursor.fetchall()

    # Reverse to restore chronological order
    rows = list(reversed(rows))
    return [{"role": r["role"], "content": r["content"]} for r in rows]


def clear_history(session_id: str):
    """Clear memory for a given session."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        conn.commit()

