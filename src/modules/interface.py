import os
import json
import logging

logger = logging.getLogger(__name__)

# ANSI escape codes for colors and styles
RESET   = "\033[0m"
BOLD    = "\033[1m"
CYAN    = "\033[96m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
MAGENTA = "\033[95m"

def load_interface_config(filepath):
    """Load interface configuration from a JSON file."""
    if not os.path.exists(filepath):
        logger.error("Configuration file '%s' not found.", filepath)
        return {}
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        logger.error("Error loading interface config: %s", e)
        return {}

def print_separator():
    """Print a horizontal separator."""
    print(YELLOW + "-" * 50 + RESET)

def print_header(header):
    """Print the colored header."""
    print_separator()
    title = header.get("title", "INTERFACE")
    subtitle = header.get("subtitle", "")
    user = header.get("user", "UNKNOWN")
    print(BOLD + CYAN + f"{title:^50}" + RESET)
    print(BOLD + CYAN + f"{subtitle:^50}" + RESET)
    print(BOLD + MAGENTA + f"User: {user:^38}" + RESET)
    print_separator()

def display_interface():
    """Display the interface header and welcome message."""
    config_path = os.path.join(os.path.dirname(__file__), "../config/interface_config.json")

    config_intf = load_interface_config(config_path)
    if not config_intf:
        return
    print_header(config_intf.get("header", {}))
    welcome_message = config_intf.get("welcome_message", "Hello!")
    print(BOLD + GREEN + f"{welcome_message:^50}" + RESET)
    print_separator()
