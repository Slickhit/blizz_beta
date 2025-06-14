import json
import os

README_TEMPLATE = """# Blizz Beta\n\n"""


def generate_readme(output_path: str = "README.md") -> None:
    """Generate a very small README snippet from config."""
    config_file = os.path.join(os.path.dirname(__file__), "../config/neocortex.json")
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception:
        config = {}

    text = README_TEMPLATE
    text += "System goal: " + config.get("system_goal", "N/A") + "\n"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
