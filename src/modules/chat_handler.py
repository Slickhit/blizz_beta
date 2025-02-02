from langchain_openai import ChatOpenAI
from config.config_loader import load_neocortex_config
from modules.memory_handler import retrieve_processed_memory, neuron_advice, process_memory
from models.custom_memory import CustomMemory
memory = CustomMemory()


def handle_user_input(user_input):
    """Process a single exchange and return the bot's response."""
    structured_memory = retrieve_processed_memory()
    conversation_history = structured_memory.get("conversation_history", [])
    
    # Get guidance from Neuron
    guidance = neuron_advice(user_input, conversation_history, load_neocortex_config())
    combined_prompt = f"Neuron's guidance: {guidance}\n\nUser: {user_input}\nBot:"

    # Get AI response
    model_name = load_neocortex_config().get("model", "gpt-4o")
    main_bot = ChatOpenAI(model=model_name)
    response = main_bot.invoke(combined_prompt)

    # Save conversation context
    memory.save_context(user_input, response.content)
    return response.content

def chat_loop():
    """Main chat loop that handles each conversation exchange."""
    exchange_count = 0
    process_frequency = 3  # Process memory every 3 exchanges

    # Print the dynamic greeting from the bot
    greeting = "Hello! How can I assist you today?"  # Replace with actual dynamic greeting logic
    print("[NEURAL-BOT] >>", greeting)

    while True:
        user_input = input("[SYSTEM_OPERATOR] >> ")
        if user_input.lower() == "exit":
            print("[NEURAL-BOT] >> Exiting secure terminal. Goodbye!")
            break

        bot_response = handle_user_input(user_input)
        exchange_count += 1

        if exchange_count % process_frequency == 0:
            process_memory()

        print("[NEURAL-BOT] >>", bot_response)
