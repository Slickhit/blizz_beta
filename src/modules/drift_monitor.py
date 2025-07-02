"""Simple drift monitoring utilities."""

import statistics
from modules import event_logger


def check_latency(latencies: list[float], threshold: float = 5.0) -> None:
    if latencies and statistics.mean(latencies) > threshold:
        event_logger.log_event("latency_alert", {"average": statistics.mean(latencies)})

