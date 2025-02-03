import os
import subprocess
import shlex


def lazy_import_self_improvement():
    """Avoid circular import by importing only when needed."""
    import modules.self_improvement as self_improve
    return self_improve


def execute_command(command):
    """Secure command execution using a whitelist approach."""
    allowed_commands = ["ls", "pwd", "whoami", "df", "free", "uptime", "echo", "cat", "self_improve"]

    command_parts = command.split()

    print(f"[DEBUG] Command received: {command_parts[0]}")  # ✅ Debugging print
    print(f"[DEBUG] Allowed commands: {allowed_commands}")  # ✅ Debugging print

    if command_parts[0] not in allowed_commands:
        return f"Error: Command '{command_parts[0]}' not allowed."

    # ✅ If `self_improve` is called, run the function
    if command_parts[0] == "self_improve":
        if len(command_parts) < 2:
            return "Usage: self_improve <file_path>"
        self_improve = lazy_import_self_improvement()  # ✅ Import only when needed
        return self_improve.self_improve_code(command_parts[1])

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return f"Command execution error: {e}"


def read_own_code(filepath):
    """Reads the content of a file from the bot's own directory."""
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Get current directory
    target_path = os.path.join(base_dir, filepath)

    if not os.path.exists(target_path):
        return f"Error: {filepath} not found."

    try:
        with open(target_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"
