import os
import json
import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from models.custom_memory import CustomMemory

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Initialize memory and the language model
memory = CustomMemory()  # Make sure this module has methods to get and update memory
model_name = "o1-mini"
processing_bot = ChatOpenAI(model=model_name)

# File to store processed memory
PROCESSED_MEMORY_FILE = os.path.join(os.path.dirname(__file__), "../models/processed_memory.json")


def load_raw_memory():
    """
    Load raw memory data using CustomMemory.
    """
    try:
        return memory.load_memory()
    except Exception as e:
        logger.error("Error loading memory: %s", e)
        return {}


def process_memory():
    """
    Process raw memory into structured data.
    Extracts personal data from conversation and stores it as JSON.
    """
    raw_memory = load_raw_memory()
    if not raw_memory:
        logger.info("No memory found to process.")
        return

    # Wrap list memory into a dictionary if needed.
    if isinstance(raw_memory, list):
        raw_memory = {"conversation_history": raw_memory}

    # Build conversation text for the prompt.
    conversation_history = raw_memory.get("conversation_history", [])
    conversation_text = "\n".join(
        [f"User: {entry.get('user', '')}\nBot: {entry.get('bot', '')}" for entry in conversation_history]
    )

    prompt = f"""
You are a memory processor. Extract any mention of the user's name in the conversation
that follows the pattern 'my name is X'. Return JSON with the schema:
{{ "personal_data": {{ "name": "...extracted name..." }} }}

Conversation:
{conversation_text}
    """
    # Invoke the language model with the prompt.
    ai_response = processing_bot.invoke(prompt)

    try:
        extracted_data = json.loads(ai_response.content)
    except json.JSONDecodeError:
        extracted_data = {}

    structured_data = {
        "personal_data": extracted_data.get("personal_data", {}),
        "preferences": raw_memory.get("preferences", {}),
        "conversation_history": conversation_history
    }

    # Save the processed memory.
    with open(PROCESSED_MEMORY_FILE, "w") as f:
        json.dump(structured_data, f, indent=4)

    logger.info("Memory successfully processed and stored.")


def retrieve_processed_memory():
    """
    Retrieve and return the structured memory data.
    """
    try:
        with open(PROCESSED_MEMORY_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning("No processed memory found.")
        return {}


def chat_loop():
    """
    A simple chat loop that uses the language model for responses.
    The loop also demonstrates where you might update the memory.
    """
    print("Hello again! I'm here to chat whenever you're ready.")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break

        # (Optional) Update your raw memory with the new user input.
        # If your CustomMemory module provides a method like add_message, use it.
        # Example:
        # memory.add_message({"user": user_input, "bot": ""})

        # Create a prompt for the bot.
        # In a full implementation, you might include recent conversation history.
        bot_prompt = f"{user_input}"
        bot_response = processing_bot.invoke(bot_prompt)
        bot_message = bot_response.content.strip()

        print(f"Bot: {bot_message}")

        # (Optional) Now that you have the bot response, update memory.
        # Example:
        # memory.add_message({"user": user_input, "bot": bot_message})

        # If you want to process memory after every interaction (or periodically),
        # you could call process_memory() here. Otherwise, you can defer it.
        # For demonstration, we'll process memory after each exchange:
        process_memory()


def main():
    """
    Process memory initially and then start the chat loop.
    """
    process_memory()  # Process memory once at startup.
    chat_loop()


if __name__ == "__main__":
    main()
