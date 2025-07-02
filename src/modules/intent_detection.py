"""Lightweight intent detection using a scikit-learn pipeline."""
from typing import Optional

# Helper to load the intent model lazily

def _predict(text: str) -> str:
    from ml import predict
    return predict.predict_intent(text)


def get_intent(text: str) -> Optional[str]:
    """Return the predicted intent for ``text``."""
    try:
        return _predict(text)
    except Exception:
        return None
