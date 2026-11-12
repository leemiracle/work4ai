# Synthetic fixture

This fixture is original synthetic data authored for ReviewOps v0.1.0 tests.
It contains no customer code, prompts, diffs, comments, logs, URLs, accounts,
credentials, provider responses, or real prices. It is licensed under
Apache-2.0 with the rest of this plugin.

## What it covers

- one `PORTABLE_CORE_MODEL` lane with a model-only allowed difference axis and
  one compatible `BEST_SYSTEM` lane for a holistic reference-architecture
  decision;
- 20 paired opaque synthetic cases with two balanced replicates for
  `baseline` and `candidate-a`;
- source-neutral export wrappers that normalize to canonical run records;
- declared pairing, leakage, blinding, randomized-order, human
  high/critical adjudication, and disagreement evidence;
- versioned root-cause labels including a critical denominator, two risk
  slices, a fixed rubric, a dated fully loaded pricing snapshot, and a
  conservative decision policy;
- preserved controller, validator, dedupe, and posting contract IDs;
- optional generic workflow and prompt files kept only for bounded secondary
  diagnostic tests, not declared by the default config.

The candidate has the same accepted synthetic root-cause findings as the
baseline but lower declared cost and latency. That exercises deterministic
normalization, validity, Pareto, and shadow-reference paths without making a
real-world quality claim.

## Files

| Path                                               | Role                                                                   |
| -------------------------------------------------- | ---------------------------------------------------------------------- |
| `reviewops.config.json`                            | Fixed fixture-relative lane bundle and limits.                         |
| `benchmark/benchmark-manifest.json`                | Portable-core lane, slice taxonomy, preserved contracts, and receipts. |
| `benchmark/eval-protocol.json`                     | Portable-core pairing, held constants, leakage controls, and claim.    |
| `benchmark/adjudication-protocol.json`             | Portable-core blinding, review, independence, and disagreement.        |
| `benchmark/best-system-manifest.json`              | Compatible holistic lane manifest for recommendation coverage.         |
| `benchmark/best-system-eval-protocol.json`         | Holistic lane pairing, controls, leakage, and claim.                   |
| `benchmark/best-system-adjudication-protocol.json` | Holistic lane blinding and adjudication evidence.                      |
| `benchmark/candidate-baseline.json`                | Baseline architecture contract.                                        |
| `benchmark/candidate-a.json`                       | Candidate architecture contract.                                       |
| `benchmark/case-labels.jsonl`                      | Versioned synthetic root-cause truth and risk slices.                  |
| `benchmark/rubric.json`                            | Scoring and severity contract.                                         |
| `benchmark/pricing.json`                           | Dated fully loaded integer-micros cost basis.                          |
| `benchmark/decision-policy.json`                   | Conservative shadow-only decision gates.                               |
| `exports/review-runs.jsonl`                        | Source-neutral export wrappers with nested canonical records.          |

## Expected contract behavior

- `validate-config --fixture synthetic` validates the fixed lane bundle.
- `normalize --fixture synthetic` reports 80 accepted records per lane and no
  rejected records.
- `audit-eval --fixture synthetic` reports both declared lanes and their
  validity gates without turning declarations into runtime proof.
- `benchmark --fixture synthetic` reports 20 paired cases and root-cause-aware
  metrics for each eligible lane.
- `recommend-architecture --fixture synthetic` can emit only a
  shadow/no-posting recommendation; it never authorizes a production change.

These are fixture expectations, not evidence about any real reviewer,
provider, model, repository, or production deployment.

## Structural receipts

The manifest carries deterministic shape-only SHA-256 receipts for the export,
manifest, protocols, candidates, rubric, pricing snapshot, and labels. The
CLI recomputes them before scoring and fails closed on missing or mismatched
receipts. They are structural receipts, not hashes of private content.
