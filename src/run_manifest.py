"""Build a reproducibility manifest from a credential-free usage ledger."""
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]



def ledger(rows):
    result = []
    for row in rows:
        usage = row.get("usage") or {}
        cached = (usage.get("prompt_tokens_details") or {}).get("cached_tokens")
        input_tokens = usage.get("prompt_tokens")
        result.append({
            "stage": row["probe"], "prompt_and_parameters_sha256": row["request_sha256"],
            "model": row.get("model"), "http_status": row.get("http_status"),
            "attempts": row["attempts"], "wall_seconds": row["wall_seconds"],
            "cached_input": cached,
            "uncached_input": input_tokens - cached if input_tokens is not None and cached is not None else None,
            "output": usage.get("completion_tokens"),
            "reasoning": (usage.get("completion_tokens_details") or {}).get("reasoning_tokens"),
        })
    return result


def manifest(report, revision):
    return {
        "code_revision_at_run_start": revision,
        "config_sha256": report["config_sha256"],
        "schema_sha256": report["schema_sha256"],
        "probe_source_sha256": report["probe_source_sha256"],
        "service_models": sorted({row["model"] for row in report["rows"] if row.get("model")}),
        "token_ledger": ledger(report["rows"]),
    }


def code_revision():
    result = subprocess.run(["git", "rev-parse", "--verify", "HEAD"], cwd=ROOT,
                            capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else None


def write_manifest(path, report, revision):
    path.write_text(json.dumps(manifest(report, revision), indent=2) + "\n", encoding="utf-8")
