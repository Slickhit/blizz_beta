import json
import os
import sys
from typing import Any, Dict, List

from modules import event_logger

STATE_FILE = os.path.join(os.path.dirname(__file__), "../models/config_state.json")


def _load_state() -> Dict[str, Any]:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}


def _save_state(state: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)


def check_config_drift() -> Dict[str, Dict[str, str]]:
    """Return a mapping of config files that changed since last check."""
    tracked_files = [
        os.path.join(os.path.dirname(__file__), "../config/neocortex.json"),
        os.path.join(os.path.dirname(__file__), "../config/interface_config.json"),
    ]
    previous = _load_state().get("config_hashes", {})
    current: Dict[str, str] = {}
    deltas: Dict[str, Dict[str, str]] = {}
    for path in tracked_files:
        if not os.path.exists(path):
            continue
        with open(path, "rb") as f:
            data = f.read()
        digest = str(hash(data))
        current[path] = digest
        if previous.get(path) and previous[path] != digest:
            deltas[path] = {"old": previous[path], "new": digest}
    _save_state({"config_hashes": current})
    return deltas


def reflect_on_state(recent: int = 10) -> Dict[str, Any]:
    """Summarize active modules, recent events and config drift."""
    summary: Dict[str, Any] = {
        "active_modules": list(sys.modules.keys()),
        "recent_tasks": event_logger.load_events()[-recent:],
        "config_deltas": check_config_drift(),
    }
    event_logger.log_event("state_reflection", summary)
    return summary
