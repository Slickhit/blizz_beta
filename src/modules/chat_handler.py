import random
import time
from langchain_openai import ChatOpenAI
from config.config_loader import load_neocortex_config
from modules.memory_handler import retrieve_processed_memory, neuron_advice, process_memory
from models.custom_memory import CustomMemory
from modules.command_executor import execute_command
from modules import event_logger
from modules import context

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


def generate_contextual_response(user_input: str) -> str | None:
    """Return a reply that references recent command outputs."""
    lower = user_input.lower()

    # Self-awareness shortcut
    if any(phrase in lower for phrase in (
        "what are your features",
        "what can you do",
        "list your capabilities",
        "your features",
        "your capabilities",
    )):
        from modules.self_awareness import describe_features
        return describe_features()

    config = load_neocortex_config()
    recent_limit = config.get("memory_retrieval", {}).get("recent_limit", 5)

    history = context.get_history(recent_limit)
    if not history:
        return None

    for cmd, out, _ts in reversed(history):
        if not cmd or not out:
            continue

        # Generic catch-all
        if any(w in lower for w in ("output", "result", cmd)):
            return out

        # Command-specific helpers
        if cmd == "pwd" and any(k in lower for k in ("where", "directory")):
            return f"You're currently in `{out}`."

        if cmd == "ls" and any(k in lower for k in ("file", "contents")):
            return f"Here are the files:\n{out}"

        if cmd == "whoami" and ("who am i" in lower or "user" in lower):
            return f"The system reports user `{out}`."

        if cmd == "scan" and "port" in lower:
            return out

    # Check conversation history for the last bot reply if requested
    structured_memory = retrieve_processed_memory()
    conv_history = structured_memory.get("conversation_history", [])
    if conv_history and any(k in lower for k in ("last message", "previous message")):
        return conv_history[-1].get("bot", "")

    return None

def handle_user_input(user_input):
    """Process a single exchange and return the bot's response."""
    config = load_neocortex_config()
    structured_memory = retrieve_processed_memory()
    conversation_history = structured_memory.get("conversation_history", [])
    event_logger.log_event("user_input", {"text": user_input})

    # Detect intent using the lightweight classifier
    try:
        from modules.intent_detection import get_intent
        intent = get_intent(user_input)
    except Exception:
        intent = None
    if intent:
        event_logger.log_event("intent_detected", {"intent": intent})

    # Get guidance from Neuron
    guidance = neuron_advice(user_input, conversation_history, config)
    combined_prompt = f"Neuron's guidance: {guidance}\n\nUser: {user_input}\nBot:"

    # Use the pre-initialized AI model
    response = main_bot.invoke(combined_prompt)

    response_text = response.content
    if config.get("use_emoji"):
        response_text += " 😊"

    # Save conversation context
    memory.save_context(user_input, response_text)
    event_logger.log_event("bot_response", {"text": response_text})
    return response_text

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
            ctx_resp = generate_contextual_response(user_input)
            if ctx_resp is not None:
                bot_response = ctx_resp
            else:
                bot_response = handle_user_input(user_input)

        exchange_count += 1

        # Process memory every 3 exchanges OR every 60 seconds
        if (time.time() - last_memory_process > 60) or (exchange_count % process_frequency == 0):
            process_memory()
            last_memory_process = time.time()

        print("[NEURAL-BOT] >>", bot_response)
        event_logger.log_event("exchange", {"count": exchange_count})
