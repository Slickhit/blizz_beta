import modules.context as context
import modules.chat_handler as chat_handler


def test_execute_command_valid(tmp_path, monkeypatch):
    monkeypatch.setattr(event_logger, "EVENT_LOG_FILE", str(tmp_path / "events.json"))
    context.set_last(None, None)
    output = command_executor.execute_command("echo hello")
    last_cmd, last_out, ts = context.get_last()

    assert output.strip() == "hello"
    assert last_cmd == "echo"
    assert last_out == "hello"
    assert isinstance(ts, float)



def test_generate_contextual_response_none():
    context.set_last(None, None)
    resp = chat_handler.generate_contextual_response("where am i?")
    assert resp is None
