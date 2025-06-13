import sys
from pathlib import Path
import types

# Ensure the src directory is in the path for imports
SRC_PATH = Path(__file__).resolve().parents[1] / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

# Provide stub modules if dependencies are missing
if 'dotenv' not in sys.modules:
    dotenv = types.ModuleType('dotenv')
    def load_dotenv():
        pass
    dotenv.load_dotenv = load_dotenv
    sys.modules['dotenv'] = dotenv

if 'langchain_openai' not in sys.modules:
    langchain_openai = types.ModuleType('langchain_openai')
    class ChatOpenAI:
        def __init__(self, *args, **kwargs):
            pass
        def invoke(self, prompt):
            return types.SimpleNamespace(content='')
    langchain_openai.ChatOpenAI = ChatOpenAI
    sys.modules['langchain_openai'] = langchain_openai
