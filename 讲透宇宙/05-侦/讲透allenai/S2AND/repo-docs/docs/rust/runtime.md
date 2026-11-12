# Rust Runtime Contract

Status date: 2026-05-25

This document defines the operational contract for the Rust extension: backend
resolution, stage defaults, failure semantics, verification gates, and the risk
register. Active benchmark baselines live in `baselines.md`.

---

## Goal

Primary Rust gate commands are the canonical `scripts/rust_suite.py` workflows
documented in [baselines.md](baselines.md):

```
uv run python scripts/rust_suite.py compare ...
uv run python scripts/rust_suite.py transfer-mini ...
uv run python scripts/rust_suite.py stress-rebuild ...
```

Archived transfer scripts are historical and are not the primary runtime gate.

Project goals:
1. Keep quality parity with Python.
2. Keep or improve latency on maintained train/eval workloads.
3. Keep Rust peak RSS non-regressed vs Python (inference and train/eval).
4. Respect install-aware runtime defaults: `s2and` => Python; `s2and[rust]` => Rust on beneficial stages.
5. Keep rollback controls and explicit-Rust override behavior.
6. Reach full train/eval + inference Rust unification only after all gates pass.

---

## Runtime contract

| Install | Default runtime |
|---|---|
| `uv pip install s2and` | Python end-to-end |
| `uv pip install "s2and[rust]"` | Rust for beneficial stages (when extension is importable and core-capable) |

Python path remains available via explicit backend and stage overrides at any time.

### Backend resolution

- `S2AND_BACKEND` accepts: `python`, `rust`, `auto`.
- Unset `S2AND_BACKEND` resolves as `auto`.
- `auto` behavior:
  - If Rust core capability is unavailable: resolve to Python.
  - If Rust core capability is available: resolve to Rust.
- Invalid values raise `ValueError`.
- Capability detection is centralized in `s2and/runtime.py`.
- Core runtime capability requires extension importability plus the current
  Rust markers used by production Arrow paths: direct Arrow ingest, indexed
  featurization, constraints, seed updates, and name-count index support.
  `ANDData`/`from_dataset` remains the maintained compatibility, training,
  benchmark, and parity surface; it is not the production inference authority.

### Stage defaults (resolved backend = `rust`)

| Stage | Default |
|---|---|
| `ingest_preprocess` | Rust |
| `constraints` | Rust |
| `pair_featurization` | Rust |

- Direct Arrow inputs are the production inference boundary. Rust production
  prediction fails fast when required Arrow paths are incomplete.
- Train/eval and classic `ANDData` payloads use `from_dataset`.
- `S2AND_BACKEND` controls all stages uniformly.

### Failure semantics

| Backend | Failure behavior |
|---|---|
| Explicit `python` | Zero Rust calls; any Rust code paths are unreachable. |
| Explicit `rust` | Strict fail-fast on any Rust-stage execution error. |
| `auto` (resolved to Python) | Python only; no Rust fallback needed. |
| `auto` (resolved to Rust) | Fail-fast on runtime Rust-stage errors. Fallback only happens during initial backend resolution. |

---

## Verification gates

These gates must pass before promoting any Rust defaults further.

| Gate | Threshold |
|---|---|
| Quality parity | No metric regression beyond `1e-6` absolute on maintained parity tests |
| Latency | No regression worse than `+5%` vs Python baseline on maintained workloads |
| Peak RSS | No regression worse than `+5%` vs Python baseline on maintained workloads |
| CI release | Both `py-only` and `rust-enabled` CI lanes green |
| Full-unification | Train/eval and inference both pass latency + RSS gates before removing mode-specific path logic |

---

## Unification status

**Already unified** (train/eval and inference):
1. `constraints` stage backend selection and Rust execution.
2. `pair_featurization` hot path (`many_pairs_featurize` Rust batch path).
3. Rust featurizer cache/build lifecycle core machinery.

**Intentionally divergent** (by design):
1. Direct Arrow inference uses typed runtime files that train/eval does not
   require.
2. Classic train/eval still starts from `ANDData`; production file-backed
   inference starts from Arrow artifacts.

---

## Cache semantics

- Public `use_cache` remains the pair-feature persistent-cache knob across training and inference.
- `use_cache=True` enables the pair-feature SQLite cache.
- Same-process Rust featurizer reuse is independent of `use_cache`.
- See [../caching.md](../caching.md) for the full cache layout and operational guidance.

---

## Implementation notes

Key design decisions and their rationale (in order of implementation):

- **Batch constraint APIs** (`get_constraints_matrix_indexed`,
  `get_constraints_block_upper_triangle_indexed`): integrated across
  `distance_matrix_helper` and `_predict_incremental_helper`.
- **Compact `CounterData`**: replaced `HashMap<String, f64>` with `Vec<(u64, f32)>` sorted by
  FNV-1a 64-bit hash; `counter_jaccard_data` uses binary search. ~400 MB savings on kisti.
  Disk-cache version bumped to 5. Note: 64-bit birthday collision risk is very low at million-scale
  keys (~2.7e-8 at 1M; ~2.7e-6 at 10M), but a collision would merge counts silently.
- **Windows memory budgeting without `psutil`**: total RAM via `GlobalMemoryStatusEx`; RSS via
  `GetProcessMemoryInfo` (working set).
- **Training-mode deferred paper preprocessing**: capability-gated via
  `SUPPORTS_FROM_DATASET_PAPER_PREPROCESS` (see dedicated section below).
- **L1b cleanup boundary**: `scripts/transfer_experiment_seed_paper.py` runs targeted
  `evict_rust_featurizer(dataset)` + `gc.collect()` after LightGBM fit; emits
  `Telemetry: post_rust_cleanup ...`.
- **Rust batch chunk-budget control**: max chunk budget 256 MB; startup fixed-overhead calibration
  hardened with page-touch probe and conservative adoption (never decreases `fixed_overhead_bytes`).

---

## Training-mode deferred paper preprocessing

In training/eval mode, S2AND can skip Python paper preprocessing (`preprocess_papers_parallel`) and let Rust
`RustFeaturizer.from_dataset` compute missing paper-derived fields from raw strings. This targets the GIL-bound
`preprocess_paper_1` bottleneck on Windows and reduces wall time when the Rust backend is enabled.

This section describes the training/eval `from_dataset` bypass.

### Gating (when Python paper preprocessing is skipped)

Python skips `preprocess_papers_parallel` only when all of the following hold:

- Backend resolves to Rust (`S2AND_BACKEND=rust` or `auto` resolved to Rust).
- `preprocess=True`.
- Rust build path is `from_dataset` (training/eval mode).
- Rust extension exposes `RustFeaturizer.SUPPORTS_FROM_DATASET_PAPER_PREPROCESS`.
- `compute_reference_features=False` (reference-details preprocessing remains Python-only).

Code pointers:
- Lifecycle decision: `s2and/rust_lifecycle.py` (`build_rust_lifecycle_policy`, field `skip_python_paper_preprocess`).
- Python skip behavior: `s2and/data.py` (skips `preprocess_papers_parallel` when `skip_python_paper_preprocess=True`).
- Capability probe: `s2and/runtime.py` (`detect_rust_runtime_capabilities`, field `from_dataset_paper_preprocess_available`).
- Rust ingestion + deferred compute: `s2and_rust/src/lib.rs` (`RustFeaturizer.from_dataset`,
  `FROM_DATASET_PAPER_PREPROCESS_CHUNK_SIZE=4096`).

### How to verify (when touched)

Maintenance checklist:
1. Build release extension: `uv run maturin develop -m s2and_rust/Cargo.toml --release`
2. Run focused tests:
   - `uv run pytest -q tests/test_rust_from_dataset_contract.py tests/test_preprocess_papers_parallel_defaults.py tests/test_rust_lifecycle.py tests/test_rust_capabilities.py`
3. Optional: rerun transfer-mini compare and write the JSON under `scratch/baselines_YYYYMMDD/` (see `baselines.md`).

Current watchlist items for this area are tracked in
[../work_plan.md](../work_plan.md), especially the reference-feature training
gate and blocked normalization migration.

---

## Verification commands

**Full tests, Python only:**
```
uv sync --extra dev --frozen
S2AND_BACKEND=python uv run pytest -q
```

**Full tests, Rust enabled:**
```
uv sync --extra dev --extra rust --frozen
uv run maturin develop -m s2and_rust/Cargo.toml
uv run pytest -q
```

**Runtime policy coverage:**
```
uv run pytest -q tests/test_runtime.py tests/test_rust_lifecycle.py
```
