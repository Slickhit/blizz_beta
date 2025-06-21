from __future__ import annotations

from typing import List, Optional

from models.custom_memory import CustomMemory
from modules.event_logger import load_events

# Optional import of tkinter and curses only when needed
try:  # pragma: no cover - optional dependency
    import tkinter as tk
    from tkinter.scrolledtext import ScrolledText
except Exception:  # pragma: no cover
    tk = None
    ScrolledText = None

try:  # pragma: no cover - optional dependency
    import curses
except Exception:  # pragma: no cover
    curses = None


class DashboardData:
    """Container for aggregated dashboard data."""

    def __init__(self, events: List[dict], history: List[dict], scan_ports: List[int]):
        self.events = events
        self.history = history
        self.scan_ports = scan_ports


def _load_conversation_history(limit: int) -> List[dict]:
    memory = CustomMemory()
    data = memory.load_memory()
    if isinstance(data, dict):
        history = data.get("conversation_history", [])
    else:
        history = data
    return history[-limit:]


def gather_data(event_limit: int = 10, history_limit: int = 5) -> DashboardData:
    """Gather recent events, conversation history and scan results."""
    events = load_events()[-event_limit:]
    history = _load_conversation_history(history_limit)
    # Get last scan event if available
    last_scan = next((e for e in reversed(events) if e.get("type") == "scan"), None)
    scan_ports = []
    if last_scan:
        scan_ports = last_scan.get("details", {}).get("ports", [])
    return DashboardData(events, history, scan_ports)


class BaseDashboard:
    """Abstract dashboard interface."""

    def refresh(self) -> None:  # pragma: no cover - to be implemented
        raise NotImplementedError


class GUIDashboard(BaseDashboard):
    """Tkinter based dashboard widget."""

    def __init__(self, parent: tk.Misc) -> None:
        if tk is None:
            raise RuntimeError("Tkinter is not available")
        self.frame = tk.Frame(parent, bg="#1e1e1e")
        opts = {"font": ("Courier New", 10), "fg": "#00ffcc", "bg": "#1e1e1e"}
        self.event_box = ScrolledText(self.frame, width=80, height=10, state="disabled", **opts)
        self.event_box.pack(padx=10, pady=5)
        self.history_box = ScrolledText(self.frame, width=80, height=10, state="disabled", **opts)
        self.history_box.pack(padx=10, pady=5)
        self.scan_label = tk.Label(self.frame, text="", **opts)
        self.scan_label.pack(padx=10, pady=5, anchor="w")
        refresh_btn = tk.Button(self.frame, text="Refresh", command=self.refresh, **opts)
        refresh_btn.pack(padx=10, pady=5, anchor="e")
        self.refresh()

    def _set_text(self, widget: ScrolledText, text: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, text)
        widget.configure(state="disabled")

    def refresh(self) -> None:
        data = gather_data()
        events_text = "\n".join(f"{e.get('timestamp','')}: {e.get('type','')}" for e in data.events)
        self._set_text(self.event_box, events_text)
        conv_lines = []
        for m in data.history:
            conv_lines.append(f"User: {m.get('user','')}")
            conv_lines.append(f"Bot: {m.get('bot','')}")
        self._set_text(self.history_box, "\n".join(conv_lines))
        if data.scan_ports:
            text = "Last scan ports: " + ", ".join(map(str, data.scan_ports))
        else:
            text = "No recent scan"
        self.scan_label.configure(text=text)


class CursesDashboard(BaseDashboard):
    """Curses based dashboard interface."""

    def __init__(self) -> None:
        if curses is None:
            raise RuntimeError("curses is not available")
        self.screen: Optional[curses.window] = None

    def start(self) -> None:
        curses.wrapper(self._run)

    def _run(self, stdscr: "curses.window") -> None:
        self.screen = stdscr
        curses.curs_set(0)
        stdscr.nodelay(False)
        self.refresh()
        while True:
            ch = stdscr.getch()
            if ch in (ord("q"), ord("Q")):
                break
            if ch in (ord("r"), ord("R")):
                self.refresh()

    def refresh(self) -> None:
        if self.screen is None:
            return
        data = gather_data()
        self.screen.clear()
        y = 0
        self.screen.addstr(y, 0, "=== Dashboard ===")
        y += 2
        self.screen.addstr(y, 0, "Recent Events:")
        y += 1
        for e in data.events:
            self.screen.addstr(y, 2, f"{e.get('timestamp','')}: {e.get('type','')}")
            y += 1
        y += 1
        self.screen.addstr(y, 0, "Recent Conversation:")
        y += 1
        for m in data.history:
            self.screen.addstr(y, 2, f"User: {m.get('user','')}")
            y += 1
            self.screen.addstr(y, 2, f"Bot: {m.get('bot','')}")
            y += 1
        y += 1
        if data.scan_ports:
            scan_text = ", ".join(map(str, data.scan_ports))
        else:
            scan_text = "No recent scan"
        self.screen.addstr(y, 0, f"Last scan: {scan_text}")
        y = curses.LINES - 1
        self.screen.addstr(y, 0, "Press r to refresh, q to quit")
        self.screen.refresh()


_active_dashboard: Optional[BaseDashboard] = None


def set_active_dashboard(dash: BaseDashboard) -> None:
    """Register the currently active dashboard."""
    global _active_dashboard
    _active_dashboard = dash


def refresh_dashboard() -> None:
    """Refresh the registered dashboard if any."""
    if _active_dashboard is not None:
        try:
            _active_dashboard.refresh()
        except Exception:
            pass
