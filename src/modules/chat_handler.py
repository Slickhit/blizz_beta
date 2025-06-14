import random
import time
from langchain_openai import ChatOpenAI
from config.config_loader import load_neocortex_config
from modules.memory_handler import retrieve_processed_memory, neuron_advice, process_memory
from models.custom_memory import CustomMemory
from modules.command_executor import execute_command
from modules import event_logger

memory = CustomMemory()

# Initialize AI model ONCE (instead of every function call)
model_name = load_neocortex_config().get("model", "gpt-4o")
main_bot = ChatOpenAI(model=model_name)

# Dynamic greeting system
greetings = [
    "Yo, what’s good?",
    "Back at it again—what’s the move?",
    "Ayy, welcome back! Need something hacked?",
    "BlizzNetic online—what’s up?"
]

def handle_user_input(user_input):
    """Process a single exchange and return the bot's response."""
    structured_memory = retrieve_processed_memory()
    conversation_history = structured_memory.get("conversation_history", [])
    event_logger.log_event("user_input", {"text": user_input})

    # Get guidance from Neuron
    guidance = neuron_advice(user_input, conversation_history, load_neocortex_config())
    combined_prompt = f"Neuron's guidance: {guidance}\n\nUser: {user_input}\nBot:"

    # Use the pre-initialized AI model
    response = main_bot.invoke(combined_prompt)

    # Save conversation context
    memory.save_context(user_input, response.content)
    event_logger.log_event("bot_response", {"text": response.content})
    return response.content

def chat_loop():
    """Main chat loop that handles each conversation exchange."""
    exchange_count = 0
    process_frequency = 3  # Process memory every 3 exchanges
    last_memory_process = time.time()

    event_logger.log_event("session_start")

    # Print a dynamic greeting
    print("[NEURAL-BOT] >> BlizzNetic online—what’s up?")

    while True:
        user_input = input("[SYSTEM_OPERATOR] >> ")
        if user_input.lower() == "exit":
            print("[NEURAL-BOT] >> Exiting secure terminal. Goodbye!")
            event_logger.log_event("session_end")
            break

        # ✅ Ensure system commands are detected
        if user_input.startswith("!"):
            command = user_input[1:].strip()  # Remove "!" and extra spaces
            bot_response = execute_command(command)
        else:
            bot_response = handle_user_input(user_input)

        exchange_count += 1

        # Process memory every 3 exchanges OR every 60 seconds
        if (time.time() - last_memory_process > 60) or (exchange_count % process_frequency == 0):
            process_memory()
            last_memory_process = time.time()

        print("[NEURAL-BOT] >>", bot_response)
        event_logger.log_event("exchange", {"count": exchange_count})
