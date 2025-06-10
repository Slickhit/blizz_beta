from modules.interface import display_interface
from config.config_loader import init_environment, load_neocortex_config
from modules.memory_handler import process_memory
from modules.chat_handler import chat_loop

def main():
    init_environment()
    display_interface()
    process_memory()
    chat_loop()

if __name__ == "__main__":
    main()
