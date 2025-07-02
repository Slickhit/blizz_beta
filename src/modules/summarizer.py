from datetime import datetime
from typing import Iterable, List

from . import chat_db, memory_db
from .embedding_utils import embed_text


def summarize_text(text: str, max_length: int = 100, min_length: int = 30) -> str:
    """Summarize ``text`` using transformers if available, else a simple truncation."""
    try:
        from transformers import pipeline

        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        result = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
        return result[0]["summary_text"]
    except Exception:
        return text[:max_length]


def summarize_messages(chat_id: int, messages: Iterable[tuple[str, str]]) -> None:
    """Summarize messages for a chat and store the result."""
    text = " ".join(m[1] for m in messages)
    summary = summarize_text(text)
    chat_db.record_summary(chat_id, summary)


def summarize_and_store(user_id: str, raw_input: str, tags: List[str] | None = None) -> None:
    """Summarize ``raw_input`` and store it with an embedding for later retrieval."""
    summary = summarize_text(raw_input)
    embedding = embed_text(summary)
    timestamp = datetime.utcnow().isoformat() + "Z"
    memory_db.add_entry(user_id, timestamp, raw_input, summary, embedding, tags or [])


def retrieve_relevant(query: str, k: int = 5) -> List[str]:
    """Retrieve summaries most relevant to ``query``."""
    vec = embed_text(query)
    results = memory_db.search(vec, k)
    return [r["summary"] for r in results]

