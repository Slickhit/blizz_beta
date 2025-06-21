import modules.feedback_loop as feedback_loop

def test_generate_suggestions(monkeypatch):
    events = [
        {"type": "command_error", "details": {}},
        {"type": "command_error", "details": {}},
        {"type": "scan", "details": {"ports": [80]}},
    ]
    monkeypatch.setattr(feedback_loop.event_logger, "load_events", lambda: events)
    suggestions = feedback_loop.generate_suggestions(threshold=2)
    assert any("command_error" in s for s in suggestions)
    assert any("HTTP" in s for s in suggestions)

