from collections import Counter
from typing import Dict, Iterable, List

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


def generate_suggestions(threshold: int = 2) -> List[str]:
    """Return tactical guidance strings based on recent events."""
    events = event_logger.load_events()
    recent = events[-20:]
    suggestions: List[str] = []

    # Repeated errors
    counts = _recent_errors(recent)
    for err_type, count in counts.items():
        if count >= threshold:
            suggestions.append(
                f"You have {count} recent {err_type} events. Check your commands."
            )

    # Latest scan results
    for entry in reversed(recent):
        if entry.get("type") == "scan":
            ports = entry.get("details", {}).get("ports", [])
            if ports:
                try:
                    from modules.port_scanner import recon_suggestions_str

                    suggestions.append(recon_suggestions_str(ports))
                except Exception:
                    pass
            break

    return suggestions
