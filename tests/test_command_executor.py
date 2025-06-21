import os
from pathlib import Path
import socket
import threading

import modules.port_scanner as port_scanner

import modules.command_executor as command_executor
import modules.event_logger as event_logger
import modules.context as context
import types


def test_execute_command_valid(tmp_path, monkeypatch):
    monkeypatch.setattr(event_logger, "EVENT_LOG_FILE", str(tmp_path / "events.json"))
    monkeypatch.setattr(command_executor, "memory", types.SimpleNamespace(save_context=lambda *a, **k: None))
    context.set_last(None, None)
    output = command_executor.execute_command("echo hello")
    last_cmd, last_out, ts = context.get_last()

    assert output.strip() == "hello"
    assert last_cmd == "echo"
    assert last_out == "hello"
    assert isinstance(ts, float)
    events = event_logger.load_events()
    assert any(e["type"] == "tool_output" for e in events)



def test_execute_command_invalid(tmp_path, monkeypatch):
    monkeypatch.setattr(event_logger, "EVENT_LOG_FILE", str(tmp_path / "events.json"))
    output = command_executor.execute_command("rm -rf /")
    assert "not allowed" in output


def test_execute_command_path_traversal(tmp_path, monkeypatch):
    monkeypatch.setattr(event_logger, "EVENT_LOG_FILE", str(tmp_path / "events.json"))
    monkeypatch.setattr(command_executor, "memory", types.SimpleNamespace(save_context=lambda *a, **k: None))
    secret_file = tmp_path / "secret.txt"
    secret_file.write_text("secret")
    rel_path = os.path.relpath(secret_file, os.getcwd())
    output = command_executor.execute_command(f"cat {rel_path}")
    assert "secret" in output


def _start_dummy_server(host="localhost"):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, 0))
    server.listen(1)
    port = server.getsockname()[1]
    thread = threading.Thread(target=server.accept, daemon=True)
    thread.start()
    return server, port


def test_execute_command_scan(monkeypatch, tmp_path):
    monkeypatch.setattr(event_logger, "EVENT_LOG_FILE", str(tmp_path / "events.json"))
    monkeypatch.setattr(command_executor, "memory", types.SimpleNamespace(save_context=lambda *a, **k: None))
    server, port = _start_dummy_server()
    monkeypatch.setattr(port_scanner, "interactive_menu", lambda ports: None)
    try:
        output = command_executor.execute_command(f"scan localhost --ports {port}")
        assert str(port) in output
    finally:
        server.close()
