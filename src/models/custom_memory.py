import json
import os

from config.config_loader import load_neocortex_config

class CustomMemory:
    def __init__(self, memory_file=os.path.join(os.path.dirname(__file__), "memory.json")):
        self.memory_file = memory_file
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, "w") as f:
                json.dump([], f)

    def save_context(self, user_input, bot_response):
        config = load_neocortex_config()
        memory_limit = config.get("memory_limit")

        with open(self.memory_file, "r") as f:
            data = json.load(f)

        new_entry = {"user": user_input, "bot": bot_response}

        if isinstance(data, list):
            data.append(new_entry)
            if isinstance(memory_limit, int) and len(data) > memory_limit:
                data = data[-memory_limit:]
        elif isinstance(data, dict) and "conversation_history" in data:
            history = data["conversation_history"]
            history.append(new_entry)
            if isinstance(memory_limit, int) and len(history) > memory_limit:
                history = history[-memory_limit:]
            data["conversation_history"] = history
        else:
            data = [new_entry]

        with open(self.memory_file, "w") as f:
            json.dump(data, f, indent=4)

    def load_memory(self):
        with open(self.memory_file, "r") as f:
            return json.load(f)

    def clear_memory(self):
        with open(self.memory_file, "w") as f:
            json.dump([], f)
