import os
import json
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def load_neocortex_config():
    """Load main bot configuration from a JSON file."""
    config_file = os.path.join(os.path.dirname(__file__), "neocortex.json")
    try:
        with open(config_file, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        logger.error("Error loading config: %s", e)
        return {}

def init_environment():
    """Load environment variables and create required directories."""
    load_dotenv()
    LOG_DIR = "./logs"
    os.makedirs(LOG_DIR, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(LOG_DIR, "app.log")),
            logging.StreamHandler()
        ]
    )
    logger.info("Environment initialized")
