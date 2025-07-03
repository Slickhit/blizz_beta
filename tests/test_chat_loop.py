import builtins
import types
import modules.chat_handler as chat_handler


def test_chat_loop_prints_logic(monkeypatch, capsys):
    inputs = iter(["hi", "exit"])
    monkeypatch.setattr(builtins, "input", lambda *_: next(inputs))
    monkeypatch.setattr(chat_handler, "generate_contextual_response", lambda *_: None)
    monkeypatch.setattr(chat_handler, "process_memory", lambda *a, **k: None)
    monkeypatch.setattr(chat_handler.memory_cache, "flush", lambda: None)
    monkeypatch.setattr(chat_handler.event_logger, "log_event", lambda *a, **k: None)

    def fake_handle(user_input):
        return {"final_response": "ok", "thought_process": "tp", "classifications": "c", "logic_notes": "ln"}

    monkeypatch.setattr(chat_handler, "handle_user_input", fake_handle)

    chat_handler.chat_loop()
    out = capsys.readouterr().out
    assert "[NEURAL-BOT] >> ok" in out
    assert "thought_process: tp" in out
    assert "classifications: c" in out
    assert "logic_notes: ln" in out
