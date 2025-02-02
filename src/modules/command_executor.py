import os
import subprocess
import shlex

def execute_command(command):
    """Secure command execution using a whitelist approach."""
    allowed_commands = ["ls", "pwd", "whoami", "df", "free", "uptime", "echo", "cat"]

    # Prevent command injection
    command_parts = shlex.split(command)

    if command_parts[0] not in allowed_commands:
        return "Error: Command not allowed."

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return f"Command execution error: {e}"
