import socket
import threading

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
