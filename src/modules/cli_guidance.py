from __future__ import annotations

"""Compatibility layer for CLI guidance."""

from guidance import manager


def synthesize_guidance(command: str, output: str) -> str:
    """Return guidance by delegating to the shared manager."""
    return manager.generate(command, output)
