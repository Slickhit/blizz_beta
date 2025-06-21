import socket
import subprocess
import threading
import queue
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Iterable, List, Tuple

# Remember the last scanned target so the interactive menu can
# run additional scans without changing its signature.
_last_target: str | None = None

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


def threader_scan(
    target: str,
    ports: Iterable[int] | None = None,
    timeout: float = 0.5,
    thread_count: int = 500,
) -> List[int]:
    """Scan ports using a queue-based thread pool similar to threader3000."""
    if ports is None:
        ports = range(1, 1025)

    open_ports: List[int] = []
    q: "queue.Queue[int]" = queue.Queue()
    for p in ports:
        q.put(p)

    def worker() -> None:
        while True:
            try:
                port = q.get_nowait()
            except queue.Empty:
                break
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                if sock.connect_ex((target, port)) == 0:
                    open_ports.append(port)
            q.task_done()

    threads = []
    for _ in range(min(thread_count, q.qsize())):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        threads.append(t)

    q.join()
    return sorted(open_ports)


async def asyncio_scan(
    target: str,
    ports: Iterable[int] | None = None,
    timeout: float = 0.5,
) -> List[int]:
    """Asynchronously scan ports using asyncio."""
    if ports is None:
        ports = range(1, 1025)

    open_ports: List[int] = []

    async def check(port: int) -> None:
        try:
            conn = asyncio.open_connection(target, port)
            reader, writer = await asyncio.wait_for(conn, timeout=timeout)
            writer.close()
            await writer.wait_closed()
            open_ports.append(port)
        except Exception:
            pass

    await asyncio.gather(*(check(p) for p in ports))
    return sorted(open_ports)


def nmap_scan(target: str, ports: Iterable[int] | None = None) -> List[int]:
    """Run nmap to detect open ports. Returns list of ports or empty on error."""
    port_arg = ",".join(map(str, ports)) if ports else "1-1024"
    try:
        result = subprocess.run(
            ["nmap", "-p", port_arg, target], capture_output=True, text=True
        )
    except FileNotFoundError:
        print("Error: nmap is not installed.")
        return []

    open_ports: List[int] = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if "/tcp" in line and "open" in line:
            try:
                open_ports.append(int(line.split("/")[0]))
            except (ValueError, IndexError):
                continue
    return sorted(open_ports)


def scan_target(
    target: str,
    ports: Iterable[int] | None = None,
    timeout: float = 0.5,
    max_workers: int = 100,
    method: str = "default",
) -> List[int]:
    """Scan target host for open TCP ports.

    Args:
        target: Hostname or IP address to scan.
        ports: Iterable of ports to check. Defaults to 1-1024.
        timeout: Timeout for each connection attempt in seconds.

    Returns:
        List of open ports.
    """
    global _last_target
    _last_target = target

    if method == "nmap":
        return nmap_scan(target, ports)

    if method == "threader":
        return threader_scan(target, ports, timeout, max_workers)

    if method == "async":
        return asyncio.run(asyncio_scan(target, ports, timeout))

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


def recon_suggestions_str(open_ports: Iterable[int]) -> str:
    """Return recon tips as a formatted string."""
    lines = []
    for port in open_ports:
        name, tip = SERVICE_TIPS.get(port, ("Unknown", "No tips available."))
        lines.append(f"- {port} ({name}): {tip}")
    return "\n".join(lines)


def interactive_menu(open_ports: List[int]) -> None:
    """Display a simple post-scan menu for educational purposes."""
    if not open_ports:
        print("No open ports to analyze.")
        return

    while True:
        print("\nWhat would you like to do?")
        print("[1] Print common service behavior")
        print("[2] Print recon tips for each service")
        print("[3] Run nmap scan for more details")
        print("[4] Exit")
        choice = input("> ").strip()
        if choice == "1":
            describe_services(open_ports)
        elif choice == "2":
            recon_suggestions(open_ports)
        elif choice == "3":
            if _last_target:
                detailed = nmap_scan(_last_target, open_ports)
                if detailed:
                    print(
                        f"nmap detected open ports: {', '.join(map(str, detailed))}"
                    )
                else:
                    print("nmap found no open ports.")
            else:
                print("No target available for nmap scan.")
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please select 1, 2, 3, or 4.")
