import json
import os

class CustomMemory:
    def __init__(self, memory_file="custom_memory.json"):
        self.memory_file = memory_file
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, "w") as f:
                json.dump({}, f)  # Store as an empty dictionary

    def save_context(self, category, key, value):
        """Save categorized data in memory."""
        try:
            with open(self.memory_file, "r") as f:
                data = json.load(f)
                if not isinstance(data, dict):  # Ensure it's a dictionary
                    data = {}
        except (json.JSONDecodeError, FileNotFoundError):
            data = {}

        if category not in data:
            data[category] = {}

        data[category][key] = value  # Store as key-value pairs

        with open(self.memory_file, "w") as f:
            json.dump(data, f, indent=4)

    def load_memory(self):
        """Load stored memory, ensuring it's always a list of conversations."""
        try:
            with open(self.memory_file, "r") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def retrieve_category(self, category):
        """Retrieve a specific category of stored data."""
        memory_data = {}
        try:
            with open(self.memory_file, "r") as f:
                data = json.load(f)
                if isinstance(data, dict) and category in data:
                    memory_data = data[category]
        except (json.JSONDecodeError, FileNotFoundError):
            pass
        return memory_data

    def clear_memory(self):
        """Reset all stored memory."""
        with open(self.memory_file, "w") as f:
            json.dump({}, f)
