from __future__ import annotations

import re

from . import GuidancePlugin


class ReconPlugin(GuidancePlugin):
    """Hints for reconnaissance tools like Sn1per."""

    def handle(self, command: str, output: str) -> str | None:
        if command.split()[0] != "sniper":
            return None
        match = re.search(r"(scan_logs/\S+\.json)", output)
        if match:
            return f"Sn1per results saved to {match.group(1)}"
        return None
