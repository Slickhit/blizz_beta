"""Nightly fine-tuning trigger."""

import os
import subprocess
from modules import event_logger


def run() -> None:
    script = os.path.join(os.path.dirname(__file__), "../ml/nightly_retrain.sh")
    try:
        subprocess.run(["bash", script], check=True)
        event_logger.log_event("fine_tune_complete", {})
    except Exception as e:
        event_logger.log_event("fine_tune_error", {"error": str(e)})

