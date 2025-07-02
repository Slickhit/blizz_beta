import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List

_DB_PATH = Path(__file__).resolve().parent.parent / "models" / "memory_store.db"
_connection: sqlite3.Connection | None = None


def _get_conn() -> sqlite3.Connection:
    global _connection
    if _connection is None:
        _connection = sqlite3.connect(_DB_PATH)
        _connection.execute(
            """CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            timestamp TEXT,
            raw_input TEXT,
            summary TEXT,
            embedding TEXT,
            tags TEXT
        )"""
        )
        _connection.commit()
    return _connection


def init_db(db_path: str | None = None) -> None:
    """Initialise the database (for testing or custom location)."""
    global _connection, _DB_PATH
    if db_path:
        _DB_PATH = Path(db_path)
        _connection = None
    _get_conn()


def add_entry(
    user_id: str,
    timestamp: str,
    raw_input: str,
    summary: str,
    embedding: List[float],
    tags: List[str] | None = None,
) -> None:
    conn = _get_conn()
    conn.execute(
        "INSERT INTO memory (user_id, timestamp, raw_input, summary, embedding, tags) VALUES (?, ?, ?, ?, ?, ?)",
        (
            user_id,
            timestamp,
            raw_input,
            summary,
            json.dumps(embedding),
            json.dumps(tags or []),
        ),
    )
    conn.commit()


def _all_entries() -> List[Dict[str, Any]]:
    conn = _get_conn()
    cur = conn.execute(
        "SELECT user_id, timestamp, raw_input, summary, embedding, tags FROM memory"
    )
    entries = []
    for row in cur.fetchall():
        entries.append(
            {
                "user_id": row[0],
                "timestamp": row[1],
                "raw_input": row[2],
                "summary": row[3],
                "embedding": json.loads(row[4]),
                "tags": json.loads(row[5]),
            }
        )
    return entries


def search(query_embedding: List[float], k: int = 5) -> List[Dict[str, Any]]:
    """Return up to ``k`` entries sorted by dot-product similarity."""
    entries = _all_entries()
    if not entries:
        return []

    def score(entry: Dict[str, Any]) -> float:
        emb = entry["embedding"]
        n = min(len(query_embedding), len(emb))
        return sum(query_embedding[i] * emb[i] for i in range(n))

    return sorted(entries, key=score, reverse=True)[:k]

