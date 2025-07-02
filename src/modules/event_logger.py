import os
import json
from datetime import datetime

EVENT_LOG_FILE = os.path.join(os.path.dirname(__file__), "../models/event_log.json")


def _load_events():
    """Load existing events from file."""
    if os.path.exists(EVENT_LOG_FILE):
        try:
            with open(EVENT_LOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []


def load_events():
    """Public helper to retrieve all logged events."""
    return _load_events()


def log_event(event_type: str, details: dict | None = None) -> None:
    """Append a new event entry to the event log."""
    events = _load_events()
    events.append(
        {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "type": event_type,
            "details": details or {},
        }
    )
    os.makedirs(os.path.dirname(EVENT_LOG_FILE), exist_ok=True)
    with open(EVENT_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=4)


def log_feedback(rating: int | str, notes: str | None = None) -> None:
    """Convenience helper to log user feedback events."""
    details = {"rating": rating}
    if notes:
        details["notes"] = notes
    log_event("user_feedback", details)

