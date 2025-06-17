import json
from executor import run_cmd
from chat_engine import chat
from sniper_runner import run_sniper, get_scan


def handle_input(prompt: str):
    if prompt.startswith("run "):
        return run_cmd(prompt[4:])
    elif prompt.startswith("sniper "):
        ip = prompt.split(" ")[1]
        return run_sniper(ip)
    elif prompt.startswith("recall "):
        ip = prompt.split(" ")[1]
        return get_scan(ip)
    else:
        return chat(prompt)


def main():
    print("BlizzNetic ready. Type your command.")
    while True:
        user_input = input("[SYSTEM_OPERATOR] >> ")
        if user_input in ["exit", "quit"]:
            break
        response = handle_input(user_input)
        if isinstance(response, str):
            print(response)
        else:
            print(json.dumps(response, indent=2))


if __name__ == "__main__":
    main()
