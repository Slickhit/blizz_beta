import socket
import threading
import asyncio

import modules.port_scanner as port_scanner


def _start_dummy_server(host="localhost"):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, 0))
    server.listen(1)
    port = server.getsockname()[1]
    thread = threading.Thread(target=server.accept, daemon=True)
    thread.start()
    return server, port


def test_scan_detects_open_port():
    server, port = _start_dummy_server()
    try:
        result = port_scanner.scan_target("localhost", [port])
        assert port in result
    finally:
        server.close()


def test_scan_closed_port():
    result = port_scanner.scan_target("localhost", [65534])
    assert result == []


def test_threader_scan(monkeypatch):
    server, port = _start_dummy_server()
    monkeypatch.setattr(port_scanner, "interactive_menu", lambda ports: None)
    try:
        result = port_scanner.scan_target("localhost", [port], method="threader")
        assert port in result
    finally:
        server.close()


def test_async_scan(monkeypatch):
    server, port = _start_dummy_server()
    monkeypatch.setattr(port_scanner, "interactive_menu", lambda ports: None)
    try:
        result = port_scanner.scan_target("localhost", [port], method="async")
        assert port in result
    finally:
        server.close()


def test_async_scan_with_existing_loop(monkeypatch):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    server, port = _start_dummy_server()
    monkeypatch.setattr(port_scanner, "interactive_menu", lambda ports: None)
    try:
        result = port_scanner.scan_target("localhost", [port], method="async")
        assert port in result
    finally:
        server.close()
        loop.close()
        asyncio.set_event_loop(None)
