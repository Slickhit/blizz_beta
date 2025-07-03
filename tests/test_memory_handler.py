import types
import modules.memory_handler as memory_handler


def test_neuron_advice_includes_commands(monkeypatch):
    config = {
        "meta_bot": {"name": "N"},
        "memory_retrieval": {"recent_limit": 2},
    }
    conversation = [{"user": "hi", "bot": "hello"}]
    monkeypatch.setattr(memory_handler, "load_events", lambda: [{"timestamp": "t1", "type": "cmd"}])
    fake_context = types.SimpleNamespace(get_history=lambda limit: [("ls", "out", 0.0), ("pwd", "/root", 0.0)][-limit:])
    monkeypatch.setattr(memory_handler, "context", fake_context)

    captured = {}

    class FakeBot:
        def invoke(self, prompt):
            captured["prompt"] = prompt
            return types.SimpleNamespace(content="guidance")

    monkeypatch.setattr(memory_handler, "neuron_bot", FakeBot())

    result = memory_handler.neuron_advice("next", conversation, config)
    assert result == "guidance"
    assert "ls: out" in captured["prompt"]
    assert "User: hi" in captured["prompt"]
