# Human adjudication

Select one development document per complexity level with the configured seed, sampling without replacement from the manifest entries after sorting by document ID. Review all labelled conflicts, verification claims, negative controls and missing-information entries in those documents, plus a seeded sample of ordinary items. Add atomic clauses only when a reviewer can resolve the source span and explicitly label the modality, polarity and scope.

For unsupported-claim review, sample model records absent from the aligned keys. Stratify by mode, complexity and record category and record the candidate population and sampling rate. An absent draft label is eligible for review. It carries no implied verdict.

Record each adjudication as a separate JSONL row with run ID, document revision, mode, record or label ID, reviewer verdict, source spans and rationale. Verdicts distinguish supported, unsupported, ambiguous and key error. Report adjudicated denominators and unresolved samples separately. Keep the source keys immutable. Held-out detailed adjudication is reserved for the user and stored outside this repository.
