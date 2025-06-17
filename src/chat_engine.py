import os
import json
import openai

# --- optional “bot mission” override --------------------------
MISSION_FILE = os.path.join(os.path.dirname(__file__), "models", "bot_mission.json")
try:
    with open(MISSION_FILE, "r", encoding="utf-8") as f:
        BOT_MISSION = json.load(f).get("motivation", "")
except (FileNotFoundError, json.JSONDecodeError):
    BOT_MISSION = ""
# --------------------------------------------------------------


def chat(prompt: str) -> str:
    """Send a prompt to OpenAI and return the assistant’s reply."""
    openai.api_key = os.environ.get("OPENAI_API_KEY", "")

    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "system.txt")
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()
    except FileNotFoundError:
        system_prompt = "You are a helpful assistant."

    # Blend in the mission statement, if one exists
    if BOT_MISSION:
        system_prompt = f"{BOT_MISSION}\n\n{system_prompt}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": prompt},
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    return response["choices"][0]["message"]["content"]
