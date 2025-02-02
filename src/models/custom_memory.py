import json
import os

class CustomMemory:
    def __init__(self, memory_file=os.path.join(os.path.dirname(__file__), "memory.json")):
        self.memory_file = memory_file
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, "w") as f:
                json.dump([], f)

    def save_context(self, user_input, bot_response):
        with open(self.memory_file, "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            data.append({"user": user_input, "bot": bot_response})
        elif isinstance(data, dict) and "conversation_history" in data:
            data["conversation_history"].append({"user": user_input, "bot": bot_response})
        else:
            data = [{"user": user_input, "bot": bot_response}]
        with open(self.memory_file, "w") as f:
            json.dump(data, f, indent=4)

    def load_memory(self):
        with open(self.memory_file, "r") as f:
            return json.load(f)

    def clear_memory(self):
        with open(self.memory_file, "w") as f:
            json.dump([], f)
