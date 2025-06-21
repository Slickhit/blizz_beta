import os
import subprocess
import logging
import ast
from langchain_openai import ChatOpenAI
from modules.file_utils import read_own_code  # ✅ FIXED! Now correctly importing from file_utils.py

logger = logging.getLogger(__name__)

model = ChatOpenAI(model="gpt-4o")


def self_improve_code(file_path):
    """Reads its own code, asks AI for improvements, validates it, and updates itself."""
    code = read_own_code(file_path)

    # ✅ If the file is empty or missing, return an error
    if "Error:" in code or not code.strip():
        return f"Error: Could not read {file_path}. Make sure the file exists and contains valid code."

    prompt = f"""You are an AI assistant that enhances Python code.
The following is the existing Python code that needs improvement:

```
{code}
```

### IMPORTANT RULES:
- ONLY return Python code. NO explanations, NO markdown formatting.
- Ensure the code runs correctly with NO syntax errors.
- Keep all existing functions and structures intact.
- Fix any inefficiencies, improve performance, and add security if needed.
- DO NOT return anything except pure Python code.
"""

    # Get AI-generated code
    improved_code = model.invoke(prompt).content

    # ✅ Log AI output for debugging
    base_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(base_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "ai_generated_code.py")
    with open(log_path, "w", encoding="utf-8") as log_file:
        log_file.write(improved_code)

    logger.debug("AI-generated code saved to %s", log_path)

    # ✅ Fix bad characters before processing
    improved_code = improved_code.replace("’", "'")  # Replace curly quotes with normal ones
    improved_code = improved_code.replace("“", '"').replace("”", '"')  # Fix curly double quotes

    # ✅ Validate the new code before overwriting
    try:
        compile(improved_code, "<string>", 'exec')  # Check for syntax errors
    except SyntaxError as e:
        logger.debug("AI-generated code caused a syntax error at line: %s", e.lineno)
        return f"Error: AI-generated code has syntax errors! {e}"

    return modify_own_code(file_path, improved_code)


def create_and_execute_script(script_name, script_content):
    """Creates a Bash script, writes content, and executes it."""
    script_path = os.path.join(os.getcwd(), script_name)

    try:
        # Write the script to a file
        with open(script_path, "w", encoding="utf-8") as script_file:
            script_file.write(script_content)

        # Make the script executable
        os.chmod(script_path, 0o755)

        # Execute the script
        result = subprocess.run(["bash", script_path], capture_output=True, text=True)
        return result.stdout.strip() or result.stderr.strip()

    except Exception as e:
        logger.error("Error executing script %s: %s", script_name, e)
        return f"Error executing script: {e}"


def modify_own_code(filepath, new_code):
    """Writes modifications to the bot's own source code after validation."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    target_path = os.path.join(base_dir, filepath)

    if not os.path.exists(target_path):
        logger.error("File not found: %s", filepath)
        return f"Error: {filepath} not found."

    try:
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(new_code)
        return f"Successfully updated {filepath}."
    except Exception as e:
        logger.error("Error writing file %s: %s", filepath, e)
        return f"Error writing file: {e}"


def analyze_code_for_improvements(file_path):
    """Return simple metrics highlighting potential refactors."""
    code = read_own_code(file_path)
    if "Error:" in code:
        return code
    tree = ast.parse(code)
    long_functions = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            lines = (node.end_lineno or 0) - (node.lineno or 0)
            if lines > 20:
                long_functions.append((node.name, lines))
    suggestions = []
    for name, length in long_functions:
        suggestions.append(f"Function '{name}' is {length} lines long; consider refactoring.")
    if not suggestions:
        suggestions.append("No obvious improvements detected.")
    return "\n".join(suggestions)
