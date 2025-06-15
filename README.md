# Blizz Beta

Blizz Beta is a simple terminal-based chat assistant that stores conversation history and can process that memory between sessions. The project is organized inside the `src/` directory and relies on a few configuration files to control how the bot behaves.

## Setup

1. Create and activate a Python 3 virtual environment (optional but recommended).
2. Install dependencies (or install the package):
   ```bash
   pip install -e .
   ```
   This installs `blizz` as a command line tool along with its
   dependencies (`langchain-openai` and `python-dotenv`).

Environment variables can be defined in a `.env` file and are loaded automatically when the application starts.

## Usage

Run `blizz` to launch the interface and start chatting:

```bash
./blizz
```

To open the graphical interface, run:
To open the graphical interface, run:

```bash
./blizz --gui
```

This launches the window immediately without requiring a subcommand. If you prefer, the subcommand style also works:

```bash
./blizz gui
```

This command automatically checks for Tkinter and attempts to install it if needed. If installation fails, install your platform’s Tkinter package (often `python3-tk` on Debian/Ubuntu) and re-run the command. The older syntax `./blizz gui` still works as well.


When it runs, a window appears showing the chat log, an input box and extra
panes for suggestions and guidance.

For a full list of commands and options run `./blizz --help`.

You can also run the built-in port scanner from the command line or from inside
the chat session. To scan from the command line use:

```bash
./blizz scan <target> [--method nmap]
```

Within the chat you can trigger the same scanner by prefixing the command with
an exclamation mark:

```text
!scan <target> [--ports 80,443] [--method threader|nmap|async]
```

After scanning, an interactive menu lets you display common service names or
basic recon tips for the detected ports. Use this only on systems you have
explicit permission to test.

The scanner now supports additional methods. Use `--method threader` to
emulate the behaviour of the threader3000 project, `--method nmap` to invoke
the `nmap` utility, or `--method async` for an asyncio-based implementation.

The script displays a welcome banner, processes any stored memory, and then enters a chat loop where you can interact with the bot. Type `exit` to leave the chat.

## Configuration Files

Several files control various aspects of the system:

- `src/config/neocortex.json` – main configuration for the bot (model selection, memory limits, greeting behaviour, etc.). Set `"use_emoji": true` to append a friendly emoji to every reply.
- `src/config/interface_config.json` – settings for the terminal interface such as the banner text and welcome message.
- `src/models/memory.json` – raw conversation history saved across sessions.
- `src/models/processed_memory.json` – structured data produced by the memory processor.
- `config.cfg` – example configuration for a spaCy training pipeline (not required to run the chat bot).

Adjust these files to customise how the bot behaves or how memory is handled.

## Memory and Event Files

The assistant stores conversation history and processing results in JSON files
located under `src/models/`:

- `memory.json` holds raw chat messages. Each entry has `user` and `bot`
  fields.
- `processed_memory.json` contains structured data extracted from the raw
  history along with recent events.
- `event_log.json` records command executions and system events. Each entry
  includes a timestamp, type and details object.

These files are rewritten as the bot runs and are safe to delete if you want to
start fresh.

## Introspection Utilities

New modules under `src/modules` provide self-monitoring features:

- `state_reflector.py` summarizes active modules, recent tasks and configuration drift.
- `behavior_alignment.py` checks recent behavior against the configured `system_goal`.
- `feedback_loop.py` analyzes the event log for repeated errors.
- `documentation_generator.py` can regenerate this README with basic details from the current configuration.

