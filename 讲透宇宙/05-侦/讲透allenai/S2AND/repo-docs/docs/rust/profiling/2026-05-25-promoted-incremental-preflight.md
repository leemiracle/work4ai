# Promoted Incremental Profiling Preflight (2026-05-25)

Date: 2026-05-25

## Goal

Prepare the next profiling pass for Arrow promoted-incremental inference. The
work-plan target is Arrow read/summary construction and reusable component
summaries on a realistic
`s2and_and_big_blocks_linker_dataset_20260525` workload. That directory
name is canonical even when its contents are refreshed.

## Tiny Preflight

Command:

```powershell
uv run pytest -q tests/test_eval_prod_models.py::test_pubmed_specter2_arrow_fixture_incremental_smoke_matches_expected_b3
```

Result:

- `1 passed`
- Existing `hyperopt` / `pkg_resources` deprecation warning only.

The fixture exercises `Clusterer.predict_incremental(...)` through the promoted
Arrow/Rust path on `tests/fixtures/arrow/pubmed_specter2`. The test asserts
`arrow_promoted_incremental == 1`, `seed_setup_cluster_seeds_source == "arrow"`,
`seed_arrow_reused_source == 1`, total query count `127`, nonzero candidate
rows, and the expected B3 score.

## Full-Run Decision

The local checkout uses:

- `s2and/data/s2and_and_big_blocks_linker_dataset_20260525`

That local path is the canonical Arrow replay/profiling source of truth. The
legacy `scripts/_rust_suite/big_block_incremental_cmd.py` JSON/`ANDData`
measurement path was removed; it was not a valid benchmark for the Arrow-only
promoted-incremental performance target.

## Profiling Runner

Use the Arrow-only promoted incremental profiler:

```powershell
uv run python scripts/rust_suite.py promoted-incremental-arrow-profile --dataset pubmed --query-limit 25 --runs 5 --output-dir scratch/promoted_incremental_arrow_profile --write-json scratch/promoted_incremental_arrow_profile/pubmed.json
```

Use `--full-run` only for intentionally large query batches.
