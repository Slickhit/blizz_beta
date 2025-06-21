from __future__ import annotations

import re

from modules.port_scanner import recon_suggestions_str
from . import GuidancePlugin


class ScanPlugin(GuidancePlugin):
    """Provide guidance for scan command output."""

    _port_regex = re.compile(r"ports? on .*?:\s*([0-9 ,]+)")

    def _parse_ports(self, output: str) -> list[int]:
        match = self._port_regex.search(output)
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

    def handle(self, command: str, output: str) -> str | None:  # noqa: D401
        """Handle scan command."""
        if command.split()[0] != "scan":
            return None
        ports = self._parse_ports(output)
        if ports:
            tips = recon_suggestions_str(ports)
            return f"Open ports found: {', '.join(map(str, ports))}\n{tips}"
        if "No open ports" in output:
            return "Scan finished. No open ports detected."
        return None
