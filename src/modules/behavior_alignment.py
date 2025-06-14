import difflib
from typing import List, Tuple

from modules import event_logger
from config.config_loader import load_neocortex_config


def _behavior_log_text(events: List[dict]) -> str:
    lines = []
    for e in events:
        typ = e.get("type", "")
        details = str(e.get("details", ""))
        lines.append(f"{typ} {details}")
    return " \n".join(lines)


def evaluate_alignment(threshold: float = 0.3) -> Tuple[bool, float]:
    """Compare recent behaviour with configured goal."""
    config = load_neocortex_config()
    goal = config.get("system_goal", "")
    if not goal:
        return True, 1.0
    events = event_logger.load_events()
    text = _behavior_log_text(events[-50:])
    ratio = difflib.SequenceMatcher(None, goal, text).ratio()
    aligned = ratio >= threshold
    if not aligned:
        event_logger.log_event(
            "alignment_warning", {"score": ratio, "goal": goal}
        )
    return aligned, ratio
