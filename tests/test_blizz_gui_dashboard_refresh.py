import types

import blizz_gui
from modules import dashboard


def test_handle_response_triggers_dashboard_refresh(monkeypatch):
    called = {"refreshed": False}

    def fake_refresh():
        called["refreshed"] = True

    monkeypatch.setattr(dashboard, "refresh_dashboard", fake_refresh)

    dummy_gui = types.SimpleNamespace(dashboard=object())
    session = types.SimpleNamespace(
        update_displays=lambda *a, **k: None,
        append_history=lambda *a, **k: None,
        gui=dummy_gui,
    )

    blizz_gui.ChatSession._handle_response(session, "hi", "logic")

    assert called["refreshed"]
