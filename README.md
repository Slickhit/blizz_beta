# Blizz Beta

Blizz Beta is a simple terminal-based chat assistant that stores conversation history and can process that memory between sessions. The project is organized inside the `src/` directory and relies on a few configuration files to control how the bot behaves.

## Setup

1. Create and activate a Python 3 virtual environment (optional but recommended).
2. Install dependencies from `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
   The requirements currently include `langchain-openai` and `python-dotenv`.

Environment variables can be defined in a `.env` file and are loaded automatically when the application starts.

## Usage

Run `blizz` to launch the interface and start chatting:

```bash
./blizz
```

You can also run the built-in port scanner from the command line or from inside
the chat session. To scan from the command line use:

```bash
./blizz scan <target> [--method nmap]
```

Within the chat you can trigger the same scanner by prefixing the command with
an exclamation mark:

```text
!scan <target> [--ports 80,443] [--method threader|nmap]
```

After scanning, an interactive menu lets you display common service names or
basic recon tips for the detected ports. Use this only on systems you have
explicit permission to test.

The scanner now supports additional methods. Use `--method threader` to
emulate the behaviour of the threader3000 project or `--method nmap` to invoke
the `nmap` utility for more detailed results.

The script displays a welcome banner, processes any stored memory, and then enters a chat loop where you can interact with the bot. Type `exit` to leave the chat.

## Configuration Files

Several files control various aspects of the system:

- `src/config/neocortex.json` – main configuration for the bot (model selection, memory limits, greeting behaviour, etc.).
- `src/config/interface_config.json` – settings for the terminal interface such as the banner text and welcome message.
- `src/models/memory.json` – raw conversation history saved across sessions.
- `src/models/processed_memory.json` – structured data produced by the memory processor.
- `config.cfg` – example configuration for a spaCy training pipeline (not required to run the chat bot).

Adjust these files to customise how the bot behaves or how memory is handled.

