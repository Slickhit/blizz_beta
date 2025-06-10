import os


def read_own_code(filepath):
    """Reads the content of a file from the project directory.

    The provided path is normalized and validated to ensure it remains within
    the project root to prevent path traversal attacks.
    """
    # Determine the project root (two levels up from this file: src/modules)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    # Normalize the requested path relative to the project root
    normalized_path = os.path.abspath(os.path.join(project_root, filepath))

    # Validate that the normalized path is still within the project directory
    if not normalized_path.startswith(project_root):
        return "Error: Invalid file path."

    if not os.path.exists(normalized_path):
        return f"Error: {filepath} not found."

    try:
        with open(normalized_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"
