import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Iterable, List, Tuple

# Common service names and simple recon tips for educational use
SERVICE_TIPS: Dict[int, Tuple[str, str]] = {
    21: ("FTP", "Try anonymous login or inspect the banner for version info."),
    22: ("SSH", "Check for default credentials or weak key auth if permitted."),
    80: ("HTTP", "Browse the web interface or use curl to inspect pages."),
    443: ("HTTPS", "Similar to HTTP but over TLS; inspect certificates."),
    3306: ("MySQL", "Look for default credentials or test basic queries."),
}


def _scan_single_port(target: str, port: int, timeout: float) -> int | None:
    """Attempt to connect to a single TCP port.

    Returns the port number if open, otherwise ``None``.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        try:
            sock.connect((target, port))
        except (socket.timeout, ConnectionRefusedError, OSError):
            return None
        else:
            return port


def scan_target(
    target: str, ports: Iterable[int] | None = None, timeout: float = 0.5,
    max_workers: int = 100
) -> List[int]:
    """Scan target host for open TCP ports using threads.

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
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_scan_single_port, target, p, timeout): p for p in ports}
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                open_ports.append(result)
    return sorted(open_ports)


def describe_services(open_ports: Iterable[int]) -> None:
    """Print a list of open ports with their known services."""
    print("\nOpen Ports Detected:")
    for port in open_ports:
        name, _ = SERVICE_TIPS.get(port, ("Unknown", ""))
        print(f"- {port}: {name}")


def recon_suggestions(open_ports: Iterable[int]) -> None:
    """Print basic recon tips for each detected service."""
    print("\nRecon Tips:")
    for port in open_ports:
        name, tip = SERVICE_TIPS.get(port, ("Unknown", "No tips available."))
        print(f"- {port} ({name}): {tip}")


def interactive_menu(open_ports: List[int]) -> None:
    """Display a simple post-scan menu for educational purposes."""
    if not open_ports:
        print("No open ports to analyze.")
        return

    while True:
        print("\nWhat would you like to do?")
        print("[1] Print common service behavior")
        print("[2] Print recon tips for each service")
        print("[3] Exit")
        choice = input("> ").strip()
        if choice == "1":
            describe_services(open_ports)
        elif choice == "2":
            recon_suggestions(open_ports)
        elif choice == "3":
            break
        else:
            print("Invalid choice. Please select 1, 2, or 3.")
