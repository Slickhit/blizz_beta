import os
from pathlib import Path

import modules.command_executor as command_executor


def test_execute_command_valid():
    output = command_executor.execute_command("echo hello")
    assert output.strip() == "hello"


def test_execute_command_invalid():
    output = command_executor.execute_command("rm -rf /")
    assert "not allowed" in output


def test_execute_command_path_traversal(tmp_path):
    secret_file = tmp_path / "secret.txt"
    secret_file.write_text("secret")
    rel_path = os.path.relpath(secret_file, os.getcwd())
    output = command_executor.execute_command(f"cat {rel_path}")
    assert "secret" in output
