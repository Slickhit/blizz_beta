import json
import os

FEATURES_FILE = os.path.join(os.path.dirname(__file__), "../config/features.json")


def _load_features():
    """Load feature list from ``FEATURES_FILE``."""
    if os.path.exists(FEATURES_FILE):
        try:
            with open(FEATURES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("features", [])
        except Exception:
            return []
    return []


def load_features():
    """Public helper to return features from the JSON file."""
    return _load_features()


def describe_features() -> str:
    """Return a formatted feature list."""
    feats = load_features()
    if not feats:
        return "No feature data available."
    return "\n".join(f"- {f}" for f in feats)
