import time

last_command = None
last_output = None
last_timestamp = None


def set_last(command: str | None, output: str | None) -> None:
    """Store the last executed command, its output, and the timestamp."""
    global last_command, last_output, last_timestamp
    last_command = command
    last_output = output
    last_timestamp = time.time() if command else None


def get_last() -> tuple[str | None, str | None, float | None]:
    """Return the last executed command, its output, and timestamp."""
    return last_command, last_output, last_timestamp
