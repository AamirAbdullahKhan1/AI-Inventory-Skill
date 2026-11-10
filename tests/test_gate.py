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
