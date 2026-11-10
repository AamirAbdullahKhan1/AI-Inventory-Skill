import unittest
from src.matcher import match, score_pair


class MatcherTests(unittest.TestCase):
    def test_alias_paraphrase_and_near_miss(self):
        key = dict(category="actor", name="Operator", aliases=["Duty officer"])
        self.assertEqual(match([dict(category="actor", name="duty officer")], [key]), [(0, 0, .75)])
        self.assertEqual(match([dict(category="actor", name="duty office")], [key]), [])

    def test_duplicate_and_merged(self):
        a = dict(category="rule", requirement_ids=["A"])
        b = dict(category="rule", requirement_ids=["B"])
        self.assertEqual(match([a, a], [a]), [])
        self.assertEqual(match([dict(category="rule", requirement_ids=["A", "B"])], [a, b]), [])

    def test_split_partial_and_monotone(self):
        def record(start, end):
            return dict(category="rule", spans=[dict(block="block", start=start, end=end)])
        key = record(0, 10)
        self.assertLess(score_pair(record(0, 3), key), score_pair(record(0, 7), key))
        self.assertEqual(match([record(0, 3), record(3, 10)], [key]), [(1, 0, .7)])

    def test_directed_relation(self):
        relation = dict(category="relation", source="A", target="B", type="precedes")
        self.assertEqual(match([relation], [relation]), [(0, 0, 1)])
        self.assertEqual(match([dict(relation, source="B", target="A")], [relation]), [])
