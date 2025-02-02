import json
import os

class CustomMemory:
    def __init__(self, memory_file="custom_memory.json"):
        self.memory_file = memory_file
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, "w") as f:
                json.dump({}, f)  # Use an empty dictionary instead of a list

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

        data[category][key] = value  # Store data as key-value pairs

        with open(self.memory_file, "w") as f:
            json.dump(data, f, indent=4)

    def load_memory(self):
        """Load stored memory."""
        try:
            with open(self.memory_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def retrieve_category(self, category):
        """Retrieve specific category of data."""
        data = self.load_memory()
        return data.get(category, {})  # Return empty dict if category doesn't exist

    def clear_memory(self):
        """Reset all stored memory."""
        with open(self.memory_file, "w") as f:
            json.dump({}, f)
