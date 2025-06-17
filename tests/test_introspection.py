import os
import modules.state_reflector as state_reflector
import modules.behavior_alignment as behavior_alignment
import modules.feedback_loop as feedback_loop


def test_check_config_drift(monkeypatch, tmp_path):
    cfg1 = tmp_path / "neocortex.json"
    cfg2 = tmp_path / "interface_config.json"
    cfg1.write_text("a")
    cfg2.write_text("b")

    monkeypatch.setattr(state_reflector, "STATE_FILE", str(tmp_path / "state.json"))

    orig_join = state_reflector.os.path.join

    def fake_join(base, rel):
        if rel.endswith("neocortex.json"):
            return str(cfg1)
        if rel.endswith("interface_config.json"):
            return str(cfg2)
        return orig_join(base, rel)

    monkeypatch.setattr(state_reflector.os.path, "join", fake_join)

    assert state_reflector.check_config_drift() == {}
    old_hash = str(hash(b"a"))
    cfg1.write_text("c")
    result = state_reflector.check_config_drift()
    new_hash = str(hash(b"c"))
    assert result[str(cfg1)] == {"old": old_hash, "new": new_hash}


def test_evaluate_alignment(monkeypatch):
    monkeypatch.setattr(behavior_alignment, "load_neocortex_config", lambda: {"system_goal": "be helpful"})
    events = [{"type": "bot_response", "details": {"text": "be helpful"}}]
    monkeypatch.setattr(behavior_alignment.event_logger, "load_events", lambda: events)
    monkeypatch.setattr(behavior_alignment.event_logger, "log_event", lambda *a, **k: None)
    aligned, score = behavior_alignment.evaluate_alignment(threshold=0.0)
    assert aligned
    assert score >= 0.0


def test_analyze_feedback(monkeypatch):
    events = [
        {"type": "command_error"},
        {"type": "command_error"},
        {"type": "other"},
    ]
    monkeypatch.setattr(feedback_loop.event_logger, "load_events", lambda: events)
    monkeypatch.setattr(feedback_loop.event_logger, "log_event", lambda *a, **k: None)
    result = feedback_loop.analyze_feedback(threshold=2)
    assert result == {"command_error": 2}
