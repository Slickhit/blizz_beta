import json
import os
import subprocess
from datetime import datetime

SNIPER_OUTPUT_DIR = "scan_logs"


def run_sniper(ip: str):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(SNIPER_OUTPUT_DIR, exist_ok=True)
    output_file = f"{SNIPER_OUTPUT_DIR}/{ip}_{timestamp}.json"
    cmd = f"sniper -t {ip} -o {output_file} -f json"
    subprocess.run(cmd, shell=True)
    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            return json.load(f)
    return {"error": "Scan failed or output not generated."}


def list_scans():
    if not os.path.isdir(SNIPER_OUTPUT_DIR):
        return []
    return os.listdir(SNIPER_OUTPUT_DIR)


def get_scan(ip: str):
    if not os.path.isdir(SNIPER_OUTPUT_DIR):
        return None
    files = [f for f in os.listdir(SNIPER_OUTPUT_DIR) if f.startswith(ip)]
    if not files:
        return None
    latest = sorted(files)[-1]
    with open(os.path.join(SNIPER_OUTPUT_DIR, latest), "r") as f:
        return json.load(f)
