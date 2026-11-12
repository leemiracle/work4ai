# Promoted Incremental Arrow Profile (2026-05-28)

Date: 2026-05-28 UTC

## Scope

Release-grade refresh of the
[2026-05-27 snapshot](2026-05-27-promoted-incremental-arrow.md), plus a
follow-up change that replaces the name-count index reader's `fs::read` with
memory-mapped IO. Uses the same canonical local bundle:

```text
s2and/data/s2and_and_big_blocks_linker_dataset_20260525
```

Same command shape as the previous snapshot (25 query signatures, 25 synthetic
seed clusters, 5 runs, `r agarwal`).

## Builds compared

| Build | Notes |
|---|---|
| baseline | `cargo build --release` on the working tree as of this run. Same crate state as before the mmap edit. |
| mmap | Same release build with the `name_counts.rs` change to mmap each `.bin` index via `memmap2` instead of loading it through `fs::read`. |

## Results

p50 over 5 runs, target block `r agarwal`:

| Metric | Baseline (release) | mmap | Delta |
|---|---:|---:|---:|
| `predict_seconds` p50 | 2.183 s | 2.012 s | **−7.9%** |
| `raw_arrow_window_plan_read_name_counts_secs` p50 | 0.775 s | 0.622 s | **−19.7%** |
| `raw_arrow_window_plan_metadata_reads_parallel_secs` p50 | 0.776 s | 0.622 s | −19.8% |
| `raw_arrow_window_featurizer_seconds` p50 | 0.996 s | 0.809 s | −18.8% |
| `peak_rss_gb` max | 3.84 GB | 3.02 GB | −21.4% |

The 2026-05-27 reading of `~11 s p50` was the debug-assertions cost. A clean
release build alone drops p50 to ~2.18 s on the same workload; the mmap
follow-up drops it further to ~2.01 s.

## Interpretation

- Name-count read remained the dominant parallel-reads pole after the release
  rebuild (0.775 s of a 2.18 s total — 35.5% of wall, ~100% of the parallel
  read pole). It is now ~31% of wall.
- The mmap change replaces a 1.85 GB fs::read + allocation + copy with a
  memory-mapped view of the four `.bin` files. The up-front records-section
  validation walk is preserved; it now touches only records-section pages
  (small) rather than forcing the full blob into a heap allocation. The
  reduction in peak RSS (~800 MB) reflects skipping the heap copy of the file
  bytes.
- Wall-time gain is +7.9%, just below the 10% policy threshold for continued
  optimization on this workload. The localized gain on the targeted timer is
  19.7% (and 21% on RSS), so the change is kept but no further work is
  scheduled here under the current policy.

## Artifacts

```text
scratch/promoted_incremental_arrow_profile/pubmed_baseline.json
scratch/promoted_incremental_arrow_profile/pubmed_mmap.json
```

## Caveats

- `run_metadata.git_dirty=true` (this profile run was taken from a working
  tree carrying the mmap edit and unrelated in-flight Rust changes); the
  release extension was rebuilt before each run. A future release-grade
  refresh from a clean worktree is still warranted before claiming this as a
  release performance number.
- `debug_assertions=false` for both builds.
