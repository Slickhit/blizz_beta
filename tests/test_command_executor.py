import os
from pathlib import Path
import socket
import threading

import modules.port_scanner as port_scanner

import modules.command_executor as command_executor
import modules.event_logger as event_logger
import modules.context as context


def test_execute_command_valid(tmp_path, monkeypatch):
    monkeypatch.setattr(event_logger, "EVENT_LOG_FILE", str(tmp_path / "events.json"))
    context.set_last(None, None)
    output = command_executor.execute_command("echo hello")
    assert output.strip() == "hello"
    assert context.get_last() == ("echo", "hello")


def test_execute_command_invalid(tmp_path, monkeypatch):
    monkeypatch.setattr(event_logger, "EVENT_LOG_FILE", str(tmp_path / "events.json"))
    output = command_executor.execute_command("rm -rf /")
    assert "not allowed" in output


def test_execute_command_path_traversal(tmp_path, monkeypatch):
    monkeypatch.setattr(event_logger, "EVENT_LOG_FILE", str(tmp_path / "events.json"))
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
    server, port = _start_dummy_server()
    monkeypatch.setattr(port_scanner, "interactive_menu", lambda ports: None)
    try:
        output = command_executor.execute_command(f"scan localhost --ports {port}")
        assert str(port) in output
    finally:
        server.close()
