import unittest
from src.heldout_gate import RULES, aggregate


class GateTest(unittest.TestCase):
    def test_failure_survives_aggregation(self):
        values = {metric: 1 if rule == "min" else 0 for metric, rule in RULES.items()}
        runs = [dict(values) for _ in range(5)]
        runs[2]["recall"] = .89
        result = aggregate(runs, {"runs": 5, "thresholds": values | {"recall": .90}})
        self.assertGreater(result["recall"]["mean"], .90)
        self.assertEqual(result["recall"]["failed_runs"], [3])

    def test_gate_suppresses_detailed_evaluator_output(self):
        from hashlib import sha256
        import json
        from pathlib import Path
        import sys
        import tempfile
        from unittest.mock import patch
        from src import heldout_gate

        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            workspace, sealed = base / "workspace", base / "sealed"
            sealed.mkdir()
            (workspace / "reports").mkdir(parents=True)
            (workspace / "runs").mkdir()
            (sealed / "document").write_bytes(b"synthetic document")
            (sealed / "key").write_bytes(b"synthetic key")
            manifest = {"test": [{
                "docx_sha256": sha256(b"synthetic document").hexdigest(),
                "key_sha256": sha256(b"synthetic key").hexdigest(),
            }]}
            (workspace / "reports" / "census.json").write_text(json.dumps(manifest))
            values = {metric: 1 if rule == "min" else 0 for metric, rule in RULES.items()}
            evaluator = base / "evaluator.py"
            evaluator.write_text(
                "import json, sys\n"
                "print('private detail', file=sys.stderr)\n"
                f"print(json.dumps({values | {'private_detail': 'private detail'}!r}))\n"
            )
            config = {"runs": 5, "gate_timeout_seconds": 10, "thresholds": values}
            with patch.object(heldout_gate, "ROOT", workspace), patch.object(
                heldout_gate, "load_config", return_value=(config, b"synthetic config")
            ), patch.object(sys, "argv", ["gate", str(sealed), str(evaluator)]):
                with self.assertRaises(SystemExit) as exit_result:
                    heldout_gate.main()
            self.assertEqual(exit_result.exception.code, 0)
            report = next((workspace / "reports").glob("heldout-*.json")).read_text()
            log = (workspace / "runs" / "heldout-gate.jsonl").read_text()
            self.assertNotIn("private detail", report + log)
            self.assertEqual(sum(json.loads(line)["status"] == "started"
                                 for line in log.splitlines()), 5)
