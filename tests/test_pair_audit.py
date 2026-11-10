"""Hand-authored pair audit. Synthetic examples do not estimate corpus precision."""
import unittest
from src.matcher import match


# Each row is manually labelled for semantic identity before running the matcher.
PAIRS = [
    ("Duty officer", "Duty officer", True), ("Duty officer", "Duty office", False),
    ("Lab technician", "Lab technician", True), ("Lab technician", "Lab manager", False),
    ("Checkout clerk", "Checkout clerk", True), ("Checkout clerk", "Warehouse clerk", False),
    ("Museum guide", "Museum guide", True), ("Museum guide", "Museum guest", False),
    ("Stage manager", "Stage manager", True), ("Stage manager", "Stage performer", False),
    ("Route planner", "Route planner", True), ("Route planner", "Route passenger", False),
    ("approve renewal", "approve renewal", True), ("approve renewal", "deny renewal", False),
    ("book slot", "book slot", True), ("book slot", "cancel slot", False),
    ("read record", "read record", True), ("read record", "erase record", False),
    ("upload receipt", "upload receipt", True), ("upload receipt", "download receipt", False),
    ("check inventory", "check inventory", True), ("check inventory", "adjust inventory", False),
    ("send reminder", "send reminder", True), ("send reminder", "send payment", False),
    ("lock gate", "lock gate", True), ("lock gate", "unlock gate", False),
    ("Room 2", "Room 2", True), ("Room 2", "Room 3", False),
    ("invoice draft", "invoice draft", True), ("invoice draft", "final invoice", False),
    ("training roster", "training roster", True), ("training roster", "payroll roster", False),
    ("spring schedule", "spring schedule", True), ("spring schedule", "summer schedule", False),
    ("night shift", "night shift", True), ("night shift", "day shift", False),
    ("weekly reconciliation", "weekly reconciliation", True),
    ("weekly reconciliation", "monthly reconciliation", False),
    ("cold storage", "cold storage", True), ("cold storage", "dry storage", False),
    ("north entrance", "north entrance", True), ("north entrance", "south entrance", False),
    ("hold reservation", "hold reservation", True), ("hold reservation", "release reservation", False),
    ("accept parcel", "accept parcel", True), ("accept parcel", "reject parcel", False),
    ("recount ballots", "recount ballots", True), ("recount ballots", "publish ballots", False),
    ("record consent", "record consent", True), ("record consent", "withdraw consent", False),
]


class PairAuditTest(unittest.TestCase):
    def test_hand_labelled_pairs(self):
        self.assertEqual(len(PAIRS), 50)
        for label, prediction, expected in PAIRS:
            with self.subTest(label=label, prediction=prediction):
                matches = match([{"category": "entity", "name": prediction}],
                                [{"category": "entity", "name": label}])
                self.assertEqual(bool(matches), expected)
