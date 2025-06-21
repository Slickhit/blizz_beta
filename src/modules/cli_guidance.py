import re
from modules.port_scanner import recon_suggestions_str, SERVICE_TIPS


def _parse_scan_output(output: str) -> list[int]:
    match = re.search(r"ports? on .*?:\s*([0-9 ,]+)", output)
    if not match:
        return []
    ports: list[int] = []
    for p in re.findall(r"\d+", match.group(1)):
        try:
            port = int(p)
            if 0 < port <= 65535:
                ports.append(port)
        except ValueError:
            continue
    return ports


def synthesize_guidance(command: str, output: str) -> str:
    """Create a short hint for the given CLI command output."""
    cmd = command.split()[0] if command else ""

    if cmd == "scan":
        ports = _parse_scan_output(output)
        if ports:
            tips = recon_suggestions_str(ports)
            return f"Open ports found: {', '.join(map(str, ports))}\n{tips}"
        return "Scan finished. No open ports detected."

    if cmd == "sniper":
        match = re.search(r"(scan_logs/\S+\.json)", output)
        if match:
            return f"Sn1per results saved to {match.group(1)}"

    # Generic fallback: show first line of output
    first_line = output.strip().splitlines()[0] if output.strip() else ""
    if first_line:
        return f"Command output: {first_line}"
    return ""
