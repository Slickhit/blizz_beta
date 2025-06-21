import sqlite3
from pathlib import Path
from datetime import datetime

_DB_PATH = Path(__file__).resolve().parent.parent / "models" / "chat_history.db"

_connection = None

def _get_conn():
    global _connection
    if _connection is None:
        _connection = sqlite3.connect(_DB_PATH)
        _connection.execute(
            "CREATE TABLE IF NOT EXISTS messages (chat_id INTEGER, timestamp TEXT, role TEXT, message TEXT)"
        )
        _connection.execute(
            "CREATE TABLE IF NOT EXISTS summaries (chat_id INTEGER, timestamp TEXT, summary_text TEXT)"
        )
        _connection.commit()
    return _connection


def record_message(chat_id: int, role: str, message: str) -> None:
    conn = _get_conn()
    conn.execute(
        "INSERT INTO messages (chat_id, timestamp, role, message) VALUES (?, ?, ?, ?)",
        (chat_id, datetime.utcnow().isoformat() + "Z", role, message),
    )
    conn.commit()


def get_messages(chat_id: int):
    conn = _get_conn()
    cur = conn.execute(
        "SELECT role, message FROM messages WHERE chat_id=? ORDER BY rowid", (chat_id,)
    )
    return cur.fetchall()


def delete_chat(chat_id: int) -> None:
    conn = _get_conn()
    conn.execute("DELETE FROM messages WHERE chat_id=?", (chat_id,))
    conn.execute("DELETE FROM summaries WHERE chat_id=?", (chat_id,))
    conn.commit()


def record_summary(chat_id: int, summary: str) -> None:
    conn = _get_conn()
    conn.execute(
        "INSERT INTO summaries (chat_id, timestamp, summary_text) VALUES (?, ?, ?)",
        (chat_id, datetime.utcnow().isoformat() + "Z", summary),
    )
    conn.commit()
