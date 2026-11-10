"""Draft label normalization and labelled-only scoring."""
from collections import Counter
from statistics import mean

IDENTITY_FIELDS = {
    "items": ("id", "category"),
    "relations": ("source", "target", "type", "classification"),
    "conflicts": ("id", "type", "genuine_conflict"),
    "verification": ("claim", "expected_verdict"),
    "structured_requirements": ("requirement_id", "label_id"),
    "negative_controls": ("type", "statement"),
    "missing_information": ("id",),
}


def adapt(key):
    if key["annotation_status"] != "synthetic_draft_requires_human_review":
        raise ValueError("Unexpected annotation status")
    if any(key["complete_" + field] is not False for field in ("attributes", "sources", "relations")):
        raise ValueError("Unexpected completeness declaration")
    return {group: [dict(row) for row in key[group]] for group in IDENTITY_FIELDS}


def score_aligned(gold, predictions):
    """Score pre-aligned predictions using reviewer-adjudicated label identities.

    An unmatched output is unlabelled. Negative-control matches are violations.
    """
    result = {}
    for group, fields in IDENTITY_FIELDS.items():
        expected = Counter(tuple(row[field] for field in fields) for row in gold[group])
        proposed = Counter(tuple(row[field] for field in fields) for row in predictions.get(group, ()))
        matched = sum((expected & proposed).values())
        total = sum(expected.values())
        result[group] = {
            "labelled": total,
            "matched": matched,
            "recall": matched / total if total and group != "negative_controls" else None,
        }
    return result


def summarize(values, run_count):
    if len(values) != run_count:
        raise ValueError("Incorrect number of runs")
    return {"mean": mean(values), "min": min(values), "max": max(values)}
