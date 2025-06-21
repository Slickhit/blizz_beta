from . import chat_db


def summarize_messages(chat_id: int, messages) -> None:
    """Create a naive summary of the provided messages and store it."""
    text = " ".join(m[1] for m in messages)
    summary = text[:200]
    chat_db.record_summary(chat_id, summary)
