import socket
from typing import Iterable, List


def scan_target(
    target: str, ports: Iterable[int] | None = None, timeout: float = 0.5
) -> List[int]:
    """Scan target host for open TCP ports.

    Args:
        target: Hostname or IP address to scan.
        ports: Iterable of ports to check. Defaults to 1-1024.
        timeout: Timeout for each connection attempt in seconds.

    Returns:
        List of open ports.
    """
    if ports is None:
        ports = range(1, 1025)

    open_ports: List[int] = []
    for port in ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            try:
                sock.connect((target, port))
            except (socket.timeout, ConnectionRefusedError, OSError):
                continue
            else:
                open_ports.append(port)
    return open_ports
