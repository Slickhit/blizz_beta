import os
import json
from dotenv import load_dotenv

def load_neocortex_config():
    """Load main bot configuration from a JSON file."""
    config_file = os.path.join(os.path.dirname(__file__), "neocortex.json")
    try:
        with open(config_file, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

def init_environment():
    """Load environment variables and create required directories."""
    load_dotenv()
    LOG_DIR = "./logs"
    os.makedirs(LOG_DIR, exist_ok=True)
