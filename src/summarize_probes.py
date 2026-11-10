"""Summarize measured closeout probes without printing request or response bodies."""
from collections import defaultdict
import json
from statistics import mean, median, quantiles
from run_manifest import ROOT, write_manifest


def summarize(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[row["probe"]].append(row)
    summary = {}
    for label, group in groups.items():
        result = {"attempted": len(group), "http_statuses": [r.get("http_status") for r in group]}
        successful = [r for r in group if r.get("http_status") == 200]
        if label.startswith("generation_"):
            successful = [r for r in successful if r.get("non_reasoning_output_tokens", 0) >= 1500]
        if successful:
            times = [r["wall_seconds"] for r in successful]
            result.update(measured=len(successful), wall_mean=mean(times), wall_min=min(times),
                          wall_p50=median(times), wall_max=max(times))
            result["wall_p95"] = quantiles(times, n=100, method="inclusive")[94] if len(times) > 1 else None
            result["tokens_per_wall_second"] = [r.get("non_reasoning_tokens_per_wall_second") for r in successful]
            result["visible_output_tokens"] = [r.get("non_reasoning_output_tokens") for r in successful]
            result["output_tokens"] = [r["usage"].get("completion_tokens") for r in successful]
            result["reasoning_tokens"] = [(r["usage"].get("completion_tokens_details") or {}).get("reasoning_tokens")
                                          for r in successful]
            result["service_ttft_ms"] = [(r["usage"].get("latency_checkpoint") or {}).get("service_ttft_ms")
                                         for r in successful]
        if label.startswith("close_reasoning"):
            result["correct"] = sum(r.get("correct", False) for r in successful)
        if label.startswith("seed_"):
            result["unique_reply_hashes"] = len({r.get("reply_sha256") for r in successful})
            result["errors"] = [r.get("error_code") for r in group if r.get("http_status") != 200]
        if "simultaneous" in label or "distinct_suffix" in label:
            result["cached_uncached"] = []
            for r in successful:
                cached = r["usage"]["prompt_tokens_details"].get("cached_tokens")
                total = r["usage"]["prompt_tokens"]
                result["cached_uncached"].append([cached, total - cached if cached is not None else None])
        summary[label] = result
    calibrations = []
    for control, document in zip(rows, rows[1:]):
        if control["probe"] != "calibration_control" or not document["probe"].startswith("calibration_"):
            continue
        if control.get("http_status") != 200 or document.get("http_status") != 200:
            continue
        observed = document["usage"]["prompt_tokens"] - control["usage"]["prompt_tokens"]
        estimate = document["bytes_div_4"]
        calibrations.append({"complexity": document["probe"].split("_")[-1], "observed_tokens": observed,
                             "bytes_div_4": estimate, "signed_percent_error": 100 * (estimate - observed) / observed})
    return {"groups": summary, "calibration": calibrations}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generation-only", action="store_true")
    args = parser.parse_args()
    stem = "azure-generation" if args.generation_only else "azure-closeout"
    path = ROOT / "reports" / f"{stem}.json"
    report = json.loads(path.read_text())
    summary = summarize(report["rows"])
    (ROOT / "reports" / f"{stem}-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    if not (ROOT / "reports" / f"{stem}-manifest.json").exists():
        write_manifest(ROOT / "reports" / f"{stem}-manifest.json", report, None)
