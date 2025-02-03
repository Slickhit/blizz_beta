import os

def read_own_code(filepath):
    """Reads the content of a file from the bot's own directory."""
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Get current directory
    target_path = os.path.join(base_dir, filepath)

    if not os.path.exists(target_path):
        return f"Error: {filepath} not found."

    try:
        with open(target_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"
