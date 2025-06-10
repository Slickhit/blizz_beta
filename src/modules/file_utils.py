import os
from pathlib import Path


def read_own_code(filepath):
    """Reads the content of a file from the project directory.

    The provided path is normalized and validated to ensure it remains within
    the project root to prevent path traversal attacks.
    """
    # Determine the project root (two levels up from this file: src/modules)
    project_root = Path(__file__).resolve().parent.parent

    # Normalize the requested path relative to the project root
    normalized_path = (project_root / filepath).resolve()

    # Validate that the normalized path is still within the project directory
    try:
        normalized_path.relative_to(project_root)
    except ValueError:
        return "Error: Invalid file path."

    if not normalized_path.exists():
        return f"Error: {filepath} not found."

    try:
        with normalized_path.open("r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"
