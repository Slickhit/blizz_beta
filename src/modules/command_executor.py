import os
import subprocess
import shlex
import logging
from modules import event_logger
from modules import context
from modules import context

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

    event_logger.log_event("command_received", {"command": command})

    try:
        command_parts = shlex.split(command)
    except ValueError as e:
        event_logger.log_event("command_error", {"command": command, "error": str(e)})
        context.set_last(None, None)
        return f"Error parsing command: {e}"

    if not command_parts:
        event_logger.log_event("command_error", {"command": command, "error": "no command"})
        context.set_last(None, None)
        return "Error: No command provided."

    logger.debug("Command received: %s", command_parts[0])
    logger.debug("Allowed commands: %s", allowed_commands)

    if command_parts[0] not in allowed_commands:
        event_logger.log_event("command_blocked", {"command": command_parts[0]})
        context.set_last(None, None)
        return f"Error: Command '{command_parts[0]}' not allowed."

    # ✅ If `self_improve` is called, run the function
    if command_parts[0] == "self_improve":
        if len(command_parts) < 2:
            event_logger.log_event("command_error", {"command": command, "error": "missing file"})
            context.set_last(None, None)
            return "Usage: self_improve <file_path>"
        self_improve = lazy_import_self_improvement()  # ✅ Import only when needed
        result = self_improve.self_improve_code(command_parts[1])
        event_logger.log_event("self_improve", {"file": command_parts[1], "result": result})
        context.set_last("self_improve", result)
        return result

    if command_parts[0] == "scan":
        from modules import port_scanner  # Local import to avoid overhead
        if len(command_parts) < 2:
            event_logger.log_event("command_error", {"command": command, "error": "missing target"})
            context.set_last(None, None)
            return "Usage: scan <target> [--ports 80,443] [--method METHOD]"
        target = command_parts[1]
        ports = None
        method = "default"
        if "--ports" in command_parts:
            idx = command_parts.index("--ports")
            if idx + 1 >= len(command_parts):
                context.set_last(None, None)
                return "Usage: scan <target> [--ports 80,443] [--method METHOD]"
            try:
                ports = [int(p) for p in command_parts[idx + 1].split(',') if p.strip()]
            except ValueError:
                context.set_last(None, None)
                return "Error: ports must be integers"
        if "--method" in command_parts:
            idx = command_parts.index("--method")
            if idx + 1 >= len(command_parts):
                context.set_last(None, None)
                return "Usage: scan <target> [--ports 80,443] [--method METHOD]"
            method = command_parts[idx + 1]
        elif "--nmap" in command_parts:
            method = "nmap"
        elif "--threader" in command_parts:
            method = "threader"
        open_ports = port_scanner.scan_target(target, ports, method=method)
        if open_ports:
            msg = f"Open ports on {target}: {', '.join(map(str, open_ports))}"
        else:
            msg = f"No open ports found on {target}"
        port_scanner.interactive_menu(open_ports)
        event_logger.log_event("scan", {"target": target, "ports": open_ports})
        context.set_last("scan", msg)
        return msg

    for arg in command_parts[1:]:
        if any(symbol in arg for symbol in [';', '&', '|', '$', '>', '<']):
            event_logger.log_event("command_error", {"command": command, "error": "invalid chars"})
            context.set_last(None, None)
            return "Error: Invalid characters in arguments."

    try:
        result = subprocess.run(command_parts, shell=False, capture_output=True, text=True)
        output = result.stdout.strip() or result.stderr.strip()
        event_logger.log_event("command_executed", {"command": command_parts[0], "output": output})
        context.set_last(command_parts[0], output)
        return output
    except Exception as e:
        logger.error("Command execution error: %s", e)
        event_logger.log_event("command_error", {"command": command_parts[0], "error": str(e)})
        context.set_last(command_parts[0], f"Command execution error: {e}")
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
