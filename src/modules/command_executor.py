import os
import subprocess
import shlex
import logging

logger = logging.getLogger(__name__)


def lazy_import_self_improvement():
    """Avoid circular import by importing only when needed."""
    import modules.self_improvement as self_improve
    return self_improve


def execute_command(command):
    """Secure command execution using a whitelist approach."""
    allowed_commands = [
        "ls",
        "pwd",
        "whoami",
        "df",
        "free",
        "uptime",
        "echo",
        "cat",
        "self_improve",
        "scan",
    ]

    try:
        command_parts = shlex.split(command)
    except ValueError as e:
        return f"Error parsing command: {e}"

    if not command_parts:
        return "Error: No command provided."

    logger.debug("Command received: %s", command_parts[0])
    logger.debug("Allowed commands: %s", allowed_commands)

    if command_parts[0] not in allowed_commands:
        return f"Error: Command '{command_parts[0]}' not allowed."

    # ✅ If `self_improve` is called, run the function
    if command_parts[0] == "self_improve":
        if len(command_parts) < 2:
            return "Usage: self_improve <file_path>"
        self_improve = lazy_import_self_improvement()  # ✅ Import only when needed
        return self_improve.self_improve_code(command_parts[1])

    if command_parts[0] == "scan":
        from modules import port_scanner  # Local import to avoid overhead
        if len(command_parts) < 2:
            return "Usage: scan <target> [--ports 80,443]"
        target = command_parts[1]
        ports = None
        if "--ports" in command_parts:
            idx = command_parts.index("--ports")
            if idx + 1 >= len(command_parts):
                return "Usage: scan <target> [--ports 80,443]"
            try:
                ports = [int(p) for p in command_parts[idx + 1].split(',') if p.strip()]
            except ValueError:
                return "Error: ports must be integers"
        open_ports = port_scanner.scan_target(target, ports)
        if open_ports:
            msg = f"Open ports on {target}: {', '.join(map(str, open_ports))}"
        else:
            msg = f"No open ports found on {target}"
        port_scanner.interactive_menu(open_ports)
        return msg

    for arg in command_parts[1:]:
        if any(symbol in arg for symbol in [';', '&', '|', '$', '>', '<']):
            return "Error: Invalid characters in arguments."

    try:
        result = subprocess.run(command_parts, shell=False, capture_output=True, text=True)
        return result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        logger.error("Command execution error: %s", e)
        return f"Command execution error: {e}"


def read_own_code(filepath):
    """Reads the content of a file from the bot's own directory."""
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Get current directory
    target_path = os.path.join(base_dir, filepath)

    if not os.path.exists(target_path):
        logger.error("File not found: %s", filepath)
        return f"Error: {filepath} not found."

    try:
        with open(target_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error("Error reading file %s: %s", filepath, e)
        return f"Error reading file: {e}"
