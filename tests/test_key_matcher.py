import unittest
from src.matcher import match_to_key


class KeyMatcherTests(unittest.TestCase):
    def test_source_resolver_and_relation_endpoint_alignment(self):
        source = {"doc": "synthetic", "locator": "paragraph", "quote": "short evidence"}
        span = dict(block="x", start=0, end=8)
        key = {
            "items": [dict(id="a", category="actor", sources=[source]),
                      dict(id="b", category="rule", requirement_ids=["R"])],
            "relations": [dict(source="a", target="b", type="owns")],
        }
        predictions = {
            "items": [dict(id="x", category="actor", spans=[span]),
                      dict(id="y", category="rule", requirement_ids=["R"])],
            "relations": [dict(source="x", target="y", type="owns")],
        }
        self.assertEqual(match_to_key(predictions, key, lambda entry: {source["quote"]: span}.get(entry["quote"])),
                         {"items": [(0, 0, 1), (1, 1, 1)], "relations": [(0, 0, 1)]})

