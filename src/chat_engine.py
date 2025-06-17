import openai
import os
import json

MISSION_FILE = os.path.join(os.path.dirname(__file__), "models", "bot_mission.json")
try:
    with open(MISSION_FILE, "r", encoding="utf-8") as f:
        BOT_MISSION = json.load(f).get("motivation", "")
except Exception:
    BOT_MISSION = ""


def chat(prompt: str) -> str:
    """Send a prompt to OpenAI and return the response text."""
    openai.api_key = os.environ.get("OPENAI_API_KEY", "")
    system_prompt = ""
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "system.txt")
    try:
        with open(prompt_path, "r") as f:
            system_prompt = f.read()
    except FileNotFoundError:
        system_prompt = "You are a helpful assistant."

    # Inject mission statement into the system prompt
    if BOT_MISSION:
        system_prompt = f"{BOT_MISSION}\n\n{system_prompt}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]

    response = openai.ChatCompletion.create(model="gpt-4", messages=messages)
    return response["choices"][0]["message"]["content"]
