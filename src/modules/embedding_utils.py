import string
from typing import List


def embed_text(text: str) -> List[float]:
    """Return a vector embedding for the given text."""
    try:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer("all-MiniLM-L6-v2")
        return model.encode(text).tolist()
    except Exception:
        # Fallback: simple letter frequency vector
        counts = [0] * 26
        for ch in text.lower():
            if ch in string.ascii_lowercase:
                counts[ord(ch) - 97] += 1
        total = sum(counts) or 1
        return [c / total for c in counts]
