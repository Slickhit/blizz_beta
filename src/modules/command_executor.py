import os
import subprocess

def execute_command(command):
    """Execute shell commands securely."""
    restricted_commands = ["rm", "shutdown", "reboot"]

    if any(cmd in command for cmd in restricted_commands):
        return "Error: Command not allowed."

    if command.startswith("cd"):
        try:
            path = command.split(" ", 1)[1]
            os.chdir(path)
            return f"Changed directory to {os.getcwd()}"
        except Exception as e:
            return f"Error changing directory: {e}"

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return f"Command execution error: {e}"
