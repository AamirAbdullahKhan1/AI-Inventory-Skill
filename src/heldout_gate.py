"""Emit aggregate held-out results from a trusted, gate-only evaluator."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
from statistics import mean
import subprocess
import sys

if __package__:
    from .p0_config import load_config
else:
    from p0_config import load_config
import uuid


ROOT = Path(__file__).resolve().parents[1]
RULES = {
    "recall": "min", "attribute_error": "max", "unsupported": "max",
    "conflict_and_mutation_recall": "min", "disposition_coverage": "min",
    "resolved_evidence": "min", "false_merges": "max", "duplicate_keys": "max",
    "contradicted_absences": "max",
}


def aggregate(runs, config):
    if len(runs) != config["runs"]:
        raise ValueError("Unexpected run count")
    result = {}
    for metric, direction in RULES.items():
        values = [run[metric] for run in runs]
        if not all(type(value) in (int, float) and math.isfinite(value) and value >= 0
                   for value in values):
            raise ValueError("Invalid aggregate input")
        threshold = config["thresholds"][metric]
        failing = [i + 1 for i, value in enumerate(values)
                   if (value < threshold if direction == "min" else value > threshold)]
        result[metric] = {"mean": mean(values), "min": min(values), "max": max(values),
                          "failed_runs": failing}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sealed_directory", type=Path)
    parser.add_argument("evaluator", type=Path, help="Trusted evaluator implementing the gate protocol")
    args = parser.parse_args()
    sealed = args.sealed_directory.resolve(strict=True)
    evaluator = args.evaluator.resolve(strict=True)
    if sealed.is_relative_to(ROOT) or ROOT.is_relative_to(sealed):
        parser.error("Held-out directory must be outside the workspace")
    config, config_bytes = load_config()
    expected = sorted(d[k] for d in json.loads((ROOT / "reports/census.json").read_text())["test"]
                      for k in ("docx_sha256", "key_sha256"))
    actual = sorted(hashlib.sha256(p.read_bytes()).hexdigest() for p in sealed.iterdir()
                    if p.is_file() and not p.is_symlink())
    if actual != expected:
        parser.error("Held-out hashes do not match the frozen split")
    run_id = uuid.uuid4().hex
    log = ROOT / "runs" / "heldout-gate.jsonl"

    def audit(status, index=None):
        with log.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"gate_id": run_id, "run": index, "status": status,
                                "utc": datetime.now(timezone.utc).isoformat()}) + "\n")

    runs = []
    for index in range(1, config["runs"] + 1):
        audit("started", index)
        try:
            completed = subprocess.run(
                [sys.executable, str(evaluator), str(sealed), str(index)],
                cwd=sealed, capture_output=True, check=True, timeout=config["gate_timeout_seconds"],
            )
            runs.append(json.loads(completed.stdout))
        except (OSError, subprocess.SubprocessError, ValueError):
            audit("failed", index)
            raise SystemExit("Held-out evaluator failed. Detailed output suppressed.") from None
        audit("completed", index)
    try:
        metrics = aggregate(runs, config)
    except (ValueError, KeyError, TypeError):
        audit("invalid_metrics")
        raise SystemExit("Held-out evaluator returned invalid aggregate metrics.") from None
    report = {"gate_id": run_id, "config_sha256": hashlib.sha256(config_bytes).hexdigest(),
              "evaluator_sha256": hashlib.sha256(evaluator.read_bytes()).hexdigest(), "metrics": metrics}
    (ROOT / "reports" / f"heldout-{run_id}.json").write_text(json.dumps(report, indent=2) + "\n")
    failed = any(row["failed_runs"] for row in metrics.values())
    audit("gate_failed" if failed else "gate_passed")
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
