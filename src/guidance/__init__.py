from __future__ import annotations

from typing import List


class GuidancePlugin:
    """Base class for guidance plugins."""

    def handle(self, command: str, output: str) -> str | None:
        raise NotImplementedError


class GuidanceManager:
    """Dispatch command output to registered guidance plugins."""

    def __init__(self) -> None:
        self.plugins: List[GuidancePlugin] = []

    def register(self, plugin: GuidancePlugin) -> None:
        self.plugins.append(plugin)

    def load_builtin(self) -> None:
        """Register built-in plugins."""
        from . import scan, recon, exploit

        self.register(scan.ScanPlugin())
        self.register(recon.ReconPlugin())
        self.register(exploit.ExploitPlugin())

    def generate(self, command: str, output: str) -> str:
        for plugin in self.plugins:
            try:
                hint = plugin.handle(command, output)
            except Exception:
                hint = None
            if hint:
                return hint

        first_line = output.strip().splitlines()[0] if output.strip() else ""
        if first_line:
            return f"Command output: {first_line}"
        return ""


manager = GuidanceManager()
manager.load_builtin()

__all__ = ["GuidancePlugin", "GuidanceManager", "manager"]
