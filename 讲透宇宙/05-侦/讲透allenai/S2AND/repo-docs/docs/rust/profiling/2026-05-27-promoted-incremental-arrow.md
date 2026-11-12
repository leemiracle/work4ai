# Promoted Incremental Arrow Profile (2026-05-27)

Date: 2026-05-27 UTC

## Scope

This snapshot backs the current Arrow-only promoted-incremental profiling claim
in `docs/work_plan.md`. It uses the canonical local replay/profiling bundle:

```text
s2and/data/s2and_and_big_blocks_linker_dataset_20260525
```

The command is bounded to 25 query signatures and 25 synthetic seed clusters
because this replay bundle has no `clusters` artifact.

## Command

```powershell
uv run python scripts/rust_suite.py promoted-incremental-arrow-profile `
  --dataset pubmed `
  --query-limit 25 `
  --max-seed-clusters 25 `
  --runs 5 `
  --synthetic-seeds-when-clusters-missing `
  --output-dir scratch/promoted_incremental_arrow_profile `
  --write-json scratch/promoted_incremental_arrow_profile/pubmed.json
```

Artifact:

```text
scratch/promoted_incremental_arrow_profile/pubmed.json
```

## Result

- Target block: `r agarwal`
- Profile signatures: 50
- Query signatures: 25
- Seed signatures: 25 synthetic
- Candidate rows: 625 p50
- Query batches: 1 p50
- Predict wall time: p50 11.15s, min 11.12s, max 11.63s
- Max RSS: 3.72 GB
- Final predicted peak delta: 18,712,216 bytes p50

Largest measured contributors in the Arrow telemetry:

- `raw_arrow_window_featurizer_seconds`: about 5.3 to 5.5s per run
- `raw_arrow_window_plan_read_name_counts_secs`: about 4.9 to 5.4s per run
- `raw_arrow_window_plan_metadata_reads_parallel_secs`: about 4.9 to 5.4s per run

## Caveats

This is operational evidence, not a release-grade promotion gate:

- `run_metadata.git_dirty=true`
- Rust extension `debug_assertions=true`

Use this snapshot to prioritize the next optimization target, not to make a
release performance claim. A release-grade refresh should first rebuild the
Rust extension in release mode and run from a clean worktree.
