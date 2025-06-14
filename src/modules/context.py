last_command = None
last_output = None


def set_last(command: str | None, output: str | None) -> None:
    """Store the last executed command and its output."""
    global last_command, last_output
    last_command = command
    last_output = output


def get_last() -> tuple[str | None, str | None]:
    """Return the last executed command and its output."""
    return last_command, last_output
