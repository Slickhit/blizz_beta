# Blizz Beta

Blizz Beta is a security focused terminal assistant.  It stores conversation
history, processes that memory for context and can execute limited system
commands.  The project lives in the `src/` directory and is driven by a few
JSON configuration files.  A mission statement located in
`src/models/bot_mission.json` is injected into every prompt so the assistant is
aware of its hacking mindset.

For authorized testing only.

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

```bash
./blizz --gui
```

This launches the window immediately without requiring a subcommand. If you prefer, the subcommand style also works:

```bash
./blizz gui
```

This command automatically checks for Tkinter and attempts to install it if needed. If installation fails, install your platform’s Tkinter package (often `python3-tk` on Debian/Ubuntu) and re-run the command. The older syntax `./blizz gui` still works as well.


When it runs, a window appears showing the chat log, an input box and extra
panes for suggestions and guidance. Press **Enter** anywhere in the window to
send your message or click the **Send** button.

The header now provides two extra buttons:
- **New Chat** starts a fresh session in a new tab.
- **Scan** opens a prompt to run the built-in port scanner on a host of your choice.

CLI actions capture their stdout or stderr. The output is stored in `event_log.json` and summarized so you can reference it later in the conversation. The guidance pane updates automatically after each action, showing relevant tips as they are generated.

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


The script displays a welcome banner, processes any stored memory, and then
enters a chat loop where you can interact with the bot. Type `exit` to leave the
chat.

## Command Manual

Blizz Beta recognises a few commands both from the main chat loop and from the
minimal `simple_main.py` interface:

- `!<command>` or `run <command>` – execute a whitelisted shell command.
- `!scan` or `blizz scan` – run the integrated port scanner. Optional flags:
  `--ports`, `--method threader|nmap|async`.
- `sniper <ip>` – launch the external Sn1per tool and save the JSON output.
- `recall <ip>` – print the last Sn1per scan for the given IP.

The exclamation mark form works inside the normal chat loop, while the `run`,
`sniper`, and `recall` syntax is available in the barebones CLI found in
`simple_main.py`.

## Configuration Files

Several files control various aspects of the system:

- `src/config/neocortex.json` – main configuration for the bot (model selection, memory limits, greeting behaviour, etc.). Set `"use_emoji": true` to append a friendly emoji to every reply.
- `src/config/interface_config.json` – settings for the terminal interface such as the banner text and welcome message.
- `src/config/features.json` – list of built-in capabilities used by `self_awareness.py`.
- `src/models/memory.json` – raw conversation history saved across sessions.
- `src/models/processed_memory.json` – structured data produced by the memory processor.
- `src/models/bot_mission.json` – mission statement injected into prompts.
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
- `memory_store.db` stores summarized messages and their vector embeddings for
  semantic search.

These files are rewritten as the bot runs and are safe to delete if you want to
start fresh.

## Introspection Utilities

New modules under `src/modules` provide self-monitoring features:

- `state_reflector.py` summarizes active modules, recent tasks and configuration drift.
- `behavior_alignment.py` checks recent behavior against the configured `system_goal`.
- `feedback_loop.py` analyzes the event log for repeated errors.
- `documentation_generator.py` can regenerate this README with basic details from the current configuration.
- `self_awareness.py` lists available features from `src/config/features.json`.

