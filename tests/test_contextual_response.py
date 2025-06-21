import modules.context as context
import modules.chat_handler as chat_handler
import modules.command_executor as command_executor
import modules.event_logger as event_logger


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


def test_generate_contextual_response_history(monkeypatch):
    monkeypatch.setattr(chat_handler, "load_neocortex_config", lambda: {"memory_retrieval": {"recent_limit": 5}})
    monkeypatch.setattr(chat_handler, "retrieve_processed_memory", lambda: {"conversation_history": []})
    context.set_last("pwd", "/root")
    context.set_last("ls", "file1\nfile2")
    resp = chat_handler.generate_contextual_response("show me the files")
    assert "file1" in resp
