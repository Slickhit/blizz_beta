import sys

import blizz_cli
import blizz_gui


def test_gui_command(monkeypatch):
    called = {"ran": False}

    def fake_run_gui():
        called["ran"] = True

    monkeypatch.setattr(blizz_gui, "main", fake_run_gui)
    monkeypatch.setattr(sys, "argv", ["blizz", "gui"])

    blizz_cli.main()

    assert called["ran"]
