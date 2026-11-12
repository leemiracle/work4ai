# Rust Ingest Source Policy Inventory

Status date: 2026-05-27

This inventory documents the maintained Rust ingest sources after removing the
legacy JSON constructor. The goal is to keep Arrow and `ANDData` ownership
separate unless a policy has an explicit parity contract.

## Current Ingest Owners

| Source | Entry point | Role |
|---|---|---|
| Arrow IPC | `RustFeaturizer.from_arrow_paths(...)` | Production raw Arrow constructor for selected rows. |
| `ANDData` | `RustFeaturizer.from_dataset(...)` | Python-reference, training/eval, parity, and compatibility constructor. |

Shared Arrow staging is split across two files: the `StageSignatureInput` and
`StagePaperInput` structs live in `s2and_rust/src/lib.rs`, while the
`preprocess_stage_papers(...)` and `preprocess_stage_signatures(...)`
functions live in `s2and_rust/src/ingest_dataset.rs`. Production Arrow rows
are runtime preprocessing inputs. `ANDData` intentionally reads mostly
precomputed Python fields unless a field is missing and must be recomputed
for compatibility.

## Policy Matrix

| Policy | Arrow | `ANDData` |
|---|---|---|
| Unidecode | Eagerly preloads a char map for selected signatures, needed papers, and paper authors through `ensure_unidecode_for_raw_arrow_inputs(...)`; Rust owns production text normalization. | Lazily preloads only when existing preprocessed fields or counters are missing and must be recomputed. |
| Language | Detects locally from raw title when `predicted_language` is null. A non-null `predicted_language` is a producer-owned cached/compatibility override; missing `is_reliable` defaults to `false`. | Preserves existing `predicted_language`; detects only for in-signature papers missing language. |
| Name normalization | Recomputes first, middle, and last normalization from Arrow name inputs through shared stage helpers. | Reads normalized name fields from Python objects and recomputes only missing pieces. |
| Name counts | Uses `name_counts_index` when present; rejects a `name_counts.arrow` path without the index. | Reads attached `author_info_name_counts`; overlay is handled later by `update_signature_name_counts(...)`. |
| Name tuples | Uses the explicit Python `name_tuples` argument/default text file; Arrow path-bundle alias overrides are rejected by production validation. | Reads `dataset.name_tuples`. |
| Paper authors | Requires a separate `paper_authors` table, requires non-null positions, sorts by position, and rejects duplicate `(paper_id, position)`. | Reads Python paper-author objects/tuples with required positions; preserves the Python-provided order. |
| Signature positions | Nullable Arrow position defaults to `0` with telemetry. | Requires `author_info_position` to extract as an integer. |
| Reference features | Not part of the Arrow production constructor. | Supports reference features by consuming existing `reference_details` counters. |
| `preprocess=false` | Still normalizes titles/authors and builds title word ngrams; skips title char, venue, journal, affiliation, and coauthor ngrams. | Paper recomputation follows `preprocess`; signature fallback can still compute missing coauthor/affiliation ngrams from existing Python fields. |
| Filtering and order | Optional requested `signature_ids` are deduplicated in requested order; absent ids sort all loaded signatures. Papers, paper authors, SPECTER, and seed constraints are filtered to selected rows. | Loads all dataset signatures and sorts ids; uses dataset-level seed maps. |
| SPECTER | Reads fixed-size-list Arrow rows for needed papers; missing rows count as missing embeddings. | Uses `dataset.specter_embeddings` when present; missing rows count as missing embeddings. |

## Safe Reuse Candidates

- Arrow staging helpers are the authority for production file-backed ingest and
  local preprocessing from raw Arrow inputs.
- `ANDData` should keep consuming Python-owned precomputed state unless a
  focused parity test proves a field can be recomputed in Rust without drift.

## Do Not Merge Without A Decision

- Do not route `from_dataset(...)` through the shared Arrow stage helpers
  without deciding how much precomputed Python state to preserve. Its purpose is
  to load `ANDData`, not to re-run full raw ingest.
- Do not merge paper-author policies unless the repo explicitly chooses whether
  `ANDData` should become as strict as Arrow's non-null/unique position rules.
- Do not require production Arrow producers to send Python-preprocessed
  language fields. If language parity is required, fix or validate the local
  Rust detector rather than moving Python preprocessing into the producer
  contract.

## Verification Targets

Before any code deduplication, keep these focused tests in scope:

- `tests/test_rust_from_dataset_contract.py`
- `tests/test_raw_block_candidate_plan_arrow.py`
- Rust unit tests in `s2and_rust/src/lib.rs`

## Last Revalidation

Status 2026-05-27: this policy inventory was rechecked against the current
Arrow validation, Rust ingest, and `ANDData` compatibility code paths. The
current lightweight regression command is:

```powershell
uv run pytest -q tests/test_rust_surface_contract.py tests/test_rust_capabilities.py tests/test_arrow_inputs.py
```
