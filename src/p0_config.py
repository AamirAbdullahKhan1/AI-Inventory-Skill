"""Shared P0 configuration validation."""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_config():
    raw = (ROOT / "configs/p0.json").read_bytes()
    data = json.loads(raw)
    for value in (data["runs"], data["gate_timeout_seconds"], data["azure"]["concurrency"],
                  data["azure"]["timeout_seconds"], data["azure"]["max_attempts"]):
        if type(value) is not int or value < 1:
            raise ValueError("Expected positive integer configuration")
    if data["runs"] < 5 or type(data["seed"]) is not int:
        raise ValueError("Expected at least five runs and an integer seed")
    for value in (*data["budgets"].values(), *data["thresholds"].values()):
        if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
            raise ValueError("Expected finite, nonnegative metric configuration")
    if data["azure"]["reasoning_effort"] not in {"low", "medium", "high"}:
        raise ValueError("Unsupported reasoning effort")
    return data, raw
