"""Match normalized predictions to draft labels without assuming label completeness."""
from collections import Counter


def normalize(value):
    return " ".join(str(value).casefold().split())


def score_pair(prediction, label):
    if prediction.get("category") != label.get("category"):
        return 0
    if prediction.get("category") == "relation":
        fields = ("source", "target", "type")
        return 1 if all(prediction.get(k) and prediction[k] == label.get(k) for k in fields) else 0
    ids = {normalize(x) for x in prediction.get("requirement_ids", ())}
    labelled_ids = {normalize(x) for x in label.get("requirement_ids", ())}
    if ids and labelled_ids and not ids & labelled_ids:
        return 0
    score = 1 if ids & labelled_ids else 0
    names = {normalize(x) for x in [prediction.get("name", ""), *prediction.get("aliases", ())] if x}
    labelled_names = {normalize(x) for x in [label.get("name", ""), *label.get("aliases", ())] if x}
    if names & labelled_names:
        score = max(score, 0.75)
    for left in prediction.get("spans", ()):
        for right in label.get("spans", ()):
            if left["block"] == right["block"]:
                overlap = min(left["end"], right["end"]) - max(left["start"], right["start"])
                union = max(left["end"], right["end"]) - min(left["start"], right["start"])
                if overlap > 0:
                    score = max(score, overlap / union)
    return score


def match(predictions, labels):
    """Conservative mutual-best one-to-one matching. Equal best scores abstain."""
    candidates = [(score_pair(pred, label), i, j)
                  for i, pred in enumerate(predictions) for j, label in enumerate(labels)]
    candidates = [(s, i, j) for s, i, j in candidates if s > 0]
    left_best, right_best = {}, {}
    for score, i, j in candidates:
        left_best[i] = max(left_best.get(i, 0), score)
        right_best[j] = max(right_best.get(j, 0), score)
    left_ties = Counter(i for s, i, j in candidates if s == left_best[i])
    right_ties = Counter(j for s, i, j in candidates if s == right_best[j])
    return [(i, j, s) for s, i, j in candidates if s == left_best[i] == right_best[j]
            and left_ties[i] == right_ties[j] == 1]


def match_to_key(predictions, key, resolve_source):
    """Resolve draft locator/quote pairs via the intake ledger before matching."""
    labels = []
    for row in key["items"]:
        spans = [resolve_source(source) for source in row.get("sources", ())]
        labels.append({**row, "spans": [span for span in spans if span is not None]})
    item_matches = match(predictions["items"], labels)
    endpoints = {predictions["items"][i]["id"]: labels[j]["id"] for i, j, _ in item_matches}
    predicted_relations = [
        {**row, "category": "relation", "source": endpoints.get(row["source"]),
         "target": endpoints.get(row["target"])}
        for row in predictions["relations"]
    ]
    relations = [{**row, "category": "relation"} for row in key["relations"]]
    return {"items": item_matches, "relations": match(predicted_relations, relations)}
