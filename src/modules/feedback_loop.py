from collections import Counter
from typing import Dict, List

from modules import event_logger


def _recent_errors(events: List[dict]) -> Counter:
    error_types = [e["type"] for e in events if "error" in e.get("type", "")]
    return Counter(error_types)


def analyze_feedback(threshold: int = 3) -> Dict[str, int]:
    """Analyze event logs and suggest improvements when errors repeat."""
    events = event_logger.load_events()
    counts = _recent_errors(events[-100:])
    suggestions: Dict[str, int] = {}
    for err_type, count in counts.items():
        if count >= threshold:
            suggestions[err_type] = count
            event_logger.log_event(
                "feedback_suggestion", {"error": err_type, "count": count}
            )
    return suggestions
