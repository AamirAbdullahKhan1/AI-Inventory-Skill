# P0 closeout

| Item | Evidence |
|---|---|
| 1. Matcher | VERIFIED on synthetic tests. 25 of 25 accepted matches in the 50 hand-labelled synthetic pairs were correct, with 25 negatives rejected. The sample exercises name identity and near misses. Separate tests exercise aliases, source spans, split and merged predictions, duplicate abstention, monotone overlap scores, and directed relations after endpoint alignment. Corpus matcher precision is unmeasured. |
| 7. Key schema | VERIFIED from all 15 development keys. The shape inventory covers 114 observed JSON paths and types, with dynamic keys grouped. No held-out key was decoded. |
| 8. Held-out gate | VERIFIED aggregate calculation and preservation of individual failures using synthetic metrics. The command checks the frozen file hashes and audits evaluator runs. No held-out members were copied. A real invocation requires the external directory and a trusted evaluator. The wrapper does not sandbox that evaluator. |
| 9. Secrets | VERIFIED using the exact configured key and encoded variants across workspace files and Git patch history. The credential store itself is excluded. Endpoint userinfo was absent. See the final scan report for the artifact count. |
| 10. Config and manifests | VERIFIED validation for P0 settings and per-call token ledger tests. The closeout probe started before the first commit. Request, config and schema hashes are available. There is no commit ID at run start. The probe source hash in the original closeout result was taken at exit after the file had been edited, so the manifest must not use it as a run-start fingerprint. Future probes capture it at startup. |

Existing extraction targets and budget guardrails remain in force. P0 synthetic latency and token measurements do not establish production document compliance.

## Azure closeout probes

**2. VERIFIED acceptance and task results.** Low and medium each returned HTTP 200 and the exact expected conflict decision on all five runs. The different reported reasoning-token distributions are consistent with the setting taking effect. Whether the service independently enforces the parameter on every call is INFERRED, since the response does not echo effective effort.

| Effort | Correct | Reasoning tokens mean/min/max | Output tokens mean/min/max | Wall seconds mean/min/max |
|---|---:|---:|---:|---:|
| Low | 5/5 | 5.6 / 0 / 13 | 19.2 / 10 / 29 | 2.569 / 2.125 / 2.766 |
| Medium | 5/5 | 16.6 / 8 / 25 | 32.6 / 24 / 41 | 3.194 / 2.546 / 3.766 |

**4. VERIFIED nondeterminism in this test.** Both seed values returned HTTP 200 on all three repetitions, with three distinct reply hashes at each fixed seed. The test cannot establish whether the seed influenced sampling. Use repeats and, where a consensus is needed, voting. Keep individual run failures visible.

**5. VERIFIED cache reporting.** In the cold-start pair with distinct suffixes, one call reported 0 cached and 2,790 uncached tokens, and the other reported 2,775 cached and 15 uncached tokens. Both warm calls with new suffixes reported 2,775 cached and 15 uncached tokens. A single cold-start pair cannot establish an expected cold-hit rate.

**6. VERIFIED sample calibration.** Azure input tokens for a matched control were subtracted from each body request. The source representation concatenated body text runs as used by the census. The estimate overcounted by 5.83% to 7.33% on these three development documents. This range describes this sample and is not a corpus-wide error bound.

| Complexity | Azure body token estimate | UTF-8 bytes / 4 | Signed error |
|---|---:|---:|---:|
| Low | 2,167 | 2,325.75 | +7.33% |
| Medium | 3,991 | 4,256.00 | +6.64% |
| High | 5,645 | 5,974.00 | +5.83% |

The original closeout batch returned 41 HTTP 200 responses and reported 8,325 cached input tokens, 16,167 uncached input tokens, and 36,544 output tokens, of which 36,190 were reasoning tokens. The repeated-word generation task produced zero non-reasoning output tokens in all 14 attempts. Those calls are excluded from speed statistics. The replacement task requests varied fictional field-guide entries with two explicit output budgets.

**3. VERIFIED attempts and output-budget exhaustion.** The varied-content rerun made 14 generation calls at concurrency 1, 2 and 4 with completion budgets of 1,800 and 2,400. All returned HTTP 200 and finish reason length. Azure accounted for all 29,400 generation completion tokens as reasoning and reported zero non-reasoning output tokens. No response qualified for the 1,500-token minimum. Visible generation speed and valid long-output latency percentiles remain unmeasured. The table below records wall time for the failed generation attempts and the service-reported TTFT diagnostic, which is not visible-output TTFT. P95 is descriptive and omitted for single-call cells.

| Concurrency | Completion budget | Calls | Qualified | Wall p50 seconds | Wall p95 seconds | Service TTFT range ms |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1,800 | 1 | 0 | 57.610 | unavailable | 771 |
| 1 | 2,400 | 1 | 0 | 74.515 | unavailable | 1,496 |
| 2 | 1,800 | 2 | 0 | 56.907 | 57.132 | 749-1,662 |
| 2 | 2,400 | 2 | 0 | 79.039 | 79.495 | 659-868 |
| 4 | 1,800 | 4 | 0 | 58.743 | 62.741 | 820-877 |
| 4 | 2,400 | 4 | 0 | 78.320 | 81.461 | 629-1,073 |

The service measurements do not establish why these requests exhausted their budgets. Neither short-call speed nor reasoning-only throughput is suitable for the document runtime budget. No budget revision is proposed. The P1 gate was not opened.
