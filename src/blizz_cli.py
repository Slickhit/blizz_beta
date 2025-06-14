import argparse
from typing import List

from main import main as run_chat
from modules.port_scanner import scan_target


def parse_ports(port_str: str) -> List[int]:
    return [int(p) for p in port_str.split(",") if p.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="blizz", description="Blizz command line interface"
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("chat", help="Start chat (default)")
    scan_parser = subparsers.add_parser("scan", help="Run a simple port scanner")
    scan_parser.add_argument("target", help="Target host or IP")
    scan_parser.add_argument(
        "--ports", help="Comma-separated list of ports", default=None
    )

    args = parser.parse_args()

    if args.command == "scan":
        ports = parse_ports(args.ports) if args.ports else None
        open_ports = scan_target(args.target, ports)
        if open_ports:
            print(f"Open ports on {args.target}: {', '.join(map(str, open_ports))}")
        else:
            print(f"No open ports found on {args.target}")
    else:
        run_chat()


if __name__ == "__main__":
    main()
