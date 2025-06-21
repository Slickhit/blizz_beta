"""Track recently executed shell commands for contextual replies."""
import time

last_command: str | None = None
last_output: str | None = None
last_timestamp: float | None = None
command_history: list[tuple[str | None, str | None, float]] = []


def set_last(command: str | None, output: str | None) -> None:
    """Store the last executed command, its output, and a timestamp."""
    global last_command, last_output, last_timestamp, command_history
    last_command = command
    last_output = output
    last_timestamp = time.time() if command else None
    if command:
        command_history.append((command, output, last_timestamp))


def get_last() -> tuple[str | None, str | None, float | None]:
    """Return the last executed command, its output, and the timestamp."""
    return last_command, last_output, last_timestamp


def get_history(limit: int | None = None) -> list[tuple[str | None, str | None, float]]:
    """Return a list of past commands up to ``limit`` entries."""
    if limit is None:
        return command_history
    return command_history[-limit:]
