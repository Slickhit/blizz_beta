import os
import json
from models.custom_memory import CustomMemory
from modules.memory_processor import process_memory, retrieve_processed_memory
from modules.event_logger import load_events
memory = CustomMemory()

def get_recent_events(limit):
    events = load_events()[-limit:]
    return "\n".join([f"{e.get('timestamp','')}: {e.get('type','')}" for e in events])

def get_recent_conversation(history, limit):
    """Extract and format the last few messages from conversation history."""
    recent = history[-limit:] if len(history) >= limit else history
    return "\n".join([f"User: {msg.get('user', '')}\nBot: {msg.get('bot', '')}" for msg in recent])

def neuron_advice(user_input, conversation_history, config):
    """Get Neuron's guidance based on recent conversation."""
    meta_bot_config = config.get("meta_bot", {})
    recent_limit = config.get("memory_retrieval", {}).get("recent_limit", 5)
    recent_history = get_recent_conversation(conversation_history, recent_limit)
    recent_events = get_recent_events(recent_limit)
    
    prompt = (
        f"You are {meta_bot_config.get('name', 'Neuron')}, an internal advisor.\n"
        f"Your role: {meta_bot_config.get('role', 'Internal advisor for the bot.')}\n"
        f"Your purpose: {meta_bot_config.get('purpose', 'Guide the main bot with memory filtering and pacing.')}\n\n"
        f"### Conversation History (last {recent_limit} messages):\n"
        f"{recent_history}\n\n"
        f"### Recent Events:\n{recent_events}\n\n"
        f"User's latest input: {user_input}\n"
        "Provide guidance on how the main bot should respond, focusing on relevance, pacing, and engagement."
    )
    return prompt  # In the original, it calls neuron_bot.invoke(prompt).content

def generate_dynamic_greeting(config):
    """Generate a context-aware greeting based on recent interactions."""
    structured_memory = retrieve_processed_memory()
    conversation_history = structured_memory.get("conversation_history", [])
    recent_limit = config.get("memory_retrieval", {}).get("recent_limit", 5)
    
    if config.get("greeting_message") == "dynamic":
        recent_history = get_recent_conversation(conversation_history, recent_limit)
        prompt = (
            "You are an internal AI assistant named Neuron. Your task is to generate a natural, context-aware greeting "
            "based on the user's past interactions.\n\n"
            f"### Recent Conversation History (last {recent_limit} messages):\n"
            f"{recent_history}\n\n"
            "Generate a short, relevant greeting based on past discussions."
        )
        return prompt  # In the original, it calls neuron_bot.invoke(prompt).content.strip()
    
    return config.get("greeting_message", "Hello! How can I assist you today?")
