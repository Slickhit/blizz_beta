import time
import os
import json
import spacy
import subprocess
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from custom_memory import CustomMemory

# Load the .env file
load_dotenv()

# Define log directory
LOG_DIR = "./logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Load spaCy model for NLU
nlp = spacy.load("en_core_web_sm")

# Initialize custom memory
memory = CustomMemory()

# Load configuration from neocortex.json
CONFIG_FILE = "neocortex.json"
def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

config = load_config()

# Initialize GPT-4o for both main bot and Neuron (meta-bot)
model_name = config.get("model", "gpt-4o")
main_bot = ChatOpenAI(model=model_name)
neuron_bot = ChatOpenAI(model=model_name)

def archivist_decide(user_input, conversation_history):
    """Archivist bot decides what gets saved and how."""

    # Ensure conversation_history is a list of dicts
    if not isinstance(conversation_history, list):
        conversation_history = []

    archivist_prompt = (
        "You are The Archivist, an internal AI responsible for storing user data efficiently.\n"
        "Analyze the latest user input and decide:\n"
        "- If it's personal data (name, preferences, important facts).\n"
        "- If it's a general conversation.\n"
        "- If it's a command.\n"
        "Then, categorize it accordingly for future retrieval.\n\n"
        f"User input: {user_input}\n"
        f"### Recent Conversation History (last 10 messages):\n"
        + "\n".join(
            [
                f"User: {entry.get('user', '')}\nBot: {entry.get('bot', '')}"
                for entry in conversation_history[-10:]
            ]
        )
        + "\n\nOutput format: {\"category\": \"category_name\", \"key\": \"key_name\", \"value\": \"value\"}"
    )

    response = neuron_bot.invoke(archivist_prompt)

    try:
        categorization = json.loads(response.content)  # Ensure response is valid JSON
        print("Archivist Decision:", categorization)  # Debugging output
        return categorization if isinstance(categorization, dict) else None
    except (json.JSONDecodeError, TypeError):
        print("Archivist Failed to Categorize Input")  # Debugging
        return None  # If it doesn't return valid JSON, ignore storing it

def neuron_advice(user_input, conversation_history):
    """Neuron (meta-bot) analyzes memory and suggests a response strategy."""
    meta_bot_config = config.get("meta_bot", {})
    recent_limit = int(config.get("memory_retrieval", {}).get("recent_limit", 5) or 5)

    # Ensure conversation_history is a list of dicts
    if not isinstance(conversation_history, list):
        conversation_history = []

    neuron_prompt = (
        f"You are {meta_bot_config.get('name', 'Neuron')}, an internal advisor.\n"
        f"Your role: {meta_bot_config.get('role', 'Internal advisor for the bot.')}\n"
        f"Your purpose: {meta_bot_config.get('purpose', 'Guide the main bot with memory filtering and pacing.')}\n\n"
        f"### Conversation History (last {recent_limit} messages):\n"
        + "\n".join(
            [
                f"User: {entry.get('user', '')}\nBot: {entry.get('bot', '')}"
                for entry in conversation_history[-recent_limit:]
            ]
        )
        + f"\n\nUser's latest input: {user_input}\n"
        "Provide guidance on how the main bot should respond, focusing on relevance, pacing, and engagement."
    )
    response = neuron_bot.invoke(neuron_prompt)
    return response.content.strip()

def generate_dynamic_greeting():
    """Neuron generates a smart greeting based on recent conversations."""
    if config.get("greeting_message") == "dynamic":
        raw_history = memory.load_memory()
        # Ensure conversation_history is a list of dicts
        conversation_history = raw_history if isinstance(raw_history, list) else []
        recent_limit = int(config.get("memory_retrieval", {}).get("recent_limit", 5) or 5)

        neuron_prompt = (
            "You are an internal AI assistant named Neuron. Your task is to generate a natural and context-aware greeting based on the user's past interactions.\n\n"
            f"### Recent Conversation History (last {recent_limit} messages):\n"
            + "\n".join(
                [
                    f"User: {entry.get('user', '')}\nBot: {entry.get('bot', '')}"
                    for entry in conversation_history[-recent_limit:]
                ]
            )
            + "\n\nGenerate a short and relevant greeting based on past discussions."
        )

        response = neuron_bot.invoke(neuron_prompt)
        return response.content.strip()

    return config.get("greeting_message", "Hello! How can I assist you today?")

def main():
    """Main function to interact with the bot."""
    print(generate_dynamic_greeting())

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("Peace Out!")
            break

        raw_history = memory.load_memory()
        # Ensure conversation_history is a list of dicts
        conversation_history = raw_history if isinstance(raw_history, list) else []

        # Explicitly capture name input
        if "my name is" in user_input.lower():
            name = user_input.lower().replace("my name is", "").strip()
            memory.save_context("personal_data", "name", name)
            print(f"Bot: Nice to meet you, {name}!")
            continue

        # Check if it's a memory retrieval question
        if "what's my name" in user_input.lower():
            stored_name = memory.retrieve_category("personal_data").get("name")
            if stored_name:
                print(f"Bot: Your name is {stored_name}.")
            else:
                print("Bot: I don't seem to have your name saved yet. What's your name?")
            continue

        if "what do you know about me" in user_input.lower():
            stored_data = memory.retrieve_category("personal_data")
            if stored_data:
                details = ", ".join([f"{k}: {v}" for k, v in stored_data.items()])
                print(f"Bot: Here's what I know about you: {details}.")
            else:
                print("Bot: I don't seem to have much info saved yet. Want to tell me more?")
            continue

        categorization = archivist_decide(user_input, conversation_history)

        if categorization:
            memory.save_context(
                categorization["category"],
                categorization["key"],
                categorization["value"]
            )

        neuron_guidance = neuron_advice(user_input, conversation_history)
        combined_prompt = f"Neuron's guidance: {neuron_guidance}\n\nUser: {user_input}\nBot:"
        response = main_bot.invoke(combined_prompt)

        # Store the new user-bot exchange as a dictionary
        new_entry = {"user": user_input, "bot": response.content}
        # Use a unique key to avoid overwriting old entries. Adjust if your memory system differs.
        timestamp_key = str(time.time())
        memory.save_context("conversation", timestamp_key, new_entry)

        print(f"Bot: {response.content}")

if __name__ == "__main__":
    main()
