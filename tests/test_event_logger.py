import json
import modules.event_logger as event_logger


def test_log_event(tmp_path, monkeypatch):
    log_file = tmp_path / "events.json"
    monkeypatch.setattr(event_logger, "EVENT_LOG_FILE", str(log_file))
    event_logger.log_event("test", {"foo": "bar"})
    events = event_logger.load_events()
    assert events[0]["type"] == "test"
    assert events[0]["details"] == {"foo": "bar"}
