"""Track the last executed shell command for contextual replies."""
import time

last_command: str | None = None
last_output: str | None = None
last_timestamp: float | None = None


def set_last(command: str | None, output: str | None) -> None:
    """Store the last executed command, its output, and a timestamp."""
    global last_command, last_output, last_timestamp
    last_command = command
    last_output = output
    last_timestamp = time.time() if command else None


def get_last() -> tuple[str | None, str | None, float | None]:
    """Return the last executed command, its output, and the timestamp."""
    return last_command, last_output, last_timestamp
