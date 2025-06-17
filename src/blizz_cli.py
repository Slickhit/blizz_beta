import argparse
import importlib
import subprocess
import sys
from typing import List

from main import main as run_chat
from modules.port_scanner import scan_target, interactive_menu


def parse_ports(port_str: str) -> List[int]:
    return [int(p) for p in port_str.split(",") if p.strip()]


def ensure_gui_dependencies() -> None:
    """Ensure Tkinter is available for the GUI."""
    try:
        importlib.import_module("tkinter")
        return
    except ModuleNotFoundError:
        print("Tkinter not found. Attempting to install...", file=sys.stderr)
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "tk"])
            importlib.import_module("tkinter")
            return
        except Exception:
            print(
                "Automatic installation failed. Install 'python3-tk' or your platform's Tkinter package.",
                file=sys.stderr,
            )
            raise


def main() -> None:
    # Handle the global --gui flag before parsing subcommands so it can be used
    # on its own without requiring "chat" or another command.
    if "--gui" in sys.argv:
        ensure_gui_dependencies()
        from blizz_gui import main as launch_gui

        launch_gui()
        return

    parser = argparse.ArgumentParser(
        prog="blizz", description="Blizz command line interface"
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch the graphical interface",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("chat", help="Start chat (default)")

    # Register the GUI launcher so `blizz gui` works from the CLI
    subparsers.add_parser("gui", help="Launch the GUI")
    scan_parser = subparsers.add_parser("scan", help="Run a simple port scanner")
    scan_parser.add_argument("target", help="Target host or IP")
    scan_parser.add_argument(
        "--ports", help="Comma-separated list of ports", default=None
    )
    scan_parser.add_argument(
        "--method",
        choices=["default", "threader", "nmap", "async"],
        default="default",
        help="Scanning method to use",
    )

    args = parser.parse_args()

    if args.gui:
        ensure_gui_dependencies()
        from blizz_gui import main as launch_gui
        launch_gui()
        return

    if args.command == "scan":
        ports = parse_ports(args.ports) if args.ports else None
        open_ports = scan_target(args.target, ports, method=args.method)
        if open_ports:
            print(f"Open ports on {args.target}: {', '.join(map(str, open_ports))}")
        else:
            print(f"No open ports found on {args.target}")
        interactive_menu(open_ports)
    elif args.command == "gui":
        ensure_gui_dependencies()
        from blizz_gui import main as launch_gui
        launch_gui()
    else:
        run_chat()


if __name__ == "__main__":
    main()
