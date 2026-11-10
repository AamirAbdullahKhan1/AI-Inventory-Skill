import unittest
from src.evaluation import IDENTITY_FIELDS, adapt, score_aligned, summarize


class EvaluationTest(unittest.TestCase):
    def test_null_round_trip_and_corruption(self):
        key = {
            "annotation_status": "synthetic_draft_requires_human_review",
            **{"complete_" + field: False for field in ("attributes", "sources", "relations")},
            **{group: [{field: field for field in fields}] for group, fields in IDENTITY_FIELDS.items()},
        }
        gold = adapt(key)
        empty = score_aligned(gold, {})
        predictions = {group: [dict(row) for row in rows] for group, rows in gold.items()
                       if group != "negative_controls"}
        full = score_aligned(gold, predictions)
        for group in predictions:
            self.assertEqual(empty[group]["recall"], 0)
            self.assertEqual(full[group]["recall"], 1)
        predictions["verification"][0]["expected_verdict"] = "corrupt"
        predictions["negative_controls"] = gold["negative_controls"]
        corrupted = score_aligned(gold, predictions)
        self.assertEqual(corrupted["verification"]["recall"], 0)
        self.assertEqual(corrupted["negative_controls"]["matched"], 1)

    def test_five_run_summary(self):
        self.assertEqual(summarize([0, 0.25, 0.5, 0.75, 1], 5),
                         {"mean": 0.5, "min": 0, "max": 1})


if __name__ == "__main__":
    unittest.main()
