# Paper results data

Aggregated, plot-ready tables behind the figures in the paper. They are consumed by the
scripts in [`../scripts/`](../scripts) — run `python scripts/make_all_figs.py` to
regenerate every figure into `figs/`.

All surprisal values are magnitudes `|empirical_posterior - prior|` in `[0, 1]`; a
hypothesis counts as a **non-stationary surprisal** when the delta `>= 0.3`.

## Tables

| File | Granularity | Description |
| --- | --- | --- |
| `search_surprisals.csv` | one row per (dataset, search mode, run, evaluated hypothesis) | Static (`offline_delta`) vs. non-stationary (`icl_delta`) surprisals along each search trajectory. Used by the search and belief-distribution figures. |
| `context_surprisals.csv` | one row per (dataset, run, evaluated hypothesis) | Offline-dedupe runs comparing context representations (`offline_delta` vs. the `icl_*_delta` columns). Used by the spurious-surprisal figures. |
| `search_diversity.csv` | one row per (dataset, mode, run) | Hypothesis-diversity metrics. Used by the diversity figures. |
| `topk_effort_surprisals.csv` | one row per (source, shuffle seed, in-context index) | Per-hypothesis static/ICL deltas and token usage across top-k context sizes and reasoning efforts. Used by the appendix top-k / reasoning-effort figures. |

## Columns

**`search_surprisals.csv`**
- `dataset`, `mode`, `run` — discovery domain, search variant, repeat.
- `order_id` — evaluation index within a run (1..N).
- `offline_delta` — static-prior surprisal; `icl_delta` — non-stationary (ICL) surprisal.
- `prior`, `empirical_posterior`, `icl_prior` — mean beliefs (∈ [0,1]).
- `icl_prior_change` — `icl_prior - prior`.
- `is_duplicate`, `is_imputed` — bookkeeping flags (duplicates have deltas zeroed).

**`context_surprisals.csv`**
- `dataset`, `run`, `order_id`, `is_imputed`, `is_duplicate` — as above.
- `offline_delta` and `*_delta` (e.g. `icl_top10_delta`, `icl_default_delta`,
  `icl_top10_mem0_delta`) — surprisal per context representation.

**`search_diversity.csv`**
- `dataset`, `mode`, `run`.
- `n_unique_hypotheses`, `mean_pairwise_cosine`, `pca_hull_volume` — diversity metrics
  (higher count/volume = more diverse; lower cosine = more diverse).

**`topk_effort_surprisals.csv`**
- `source` — one of `minimal`/`low`/`medium`/`high` (reasoning effort) or
  `low`/`low-top1`/`low-top5`/`low-top25`/`low-top50` (top-k context size).
- `seed`, `n_in_context` — shuffle seed and number of in-context examples.
- `delta_offline`, `delta_icl`, `total_tokens`, `completion_tokens`.

## Provenance

These tables are slimmed aggregates of the raw MCTS evaluation runs. Regeneration from the
raw runs is a maintainer task (the raw runs are not part of this repo); see the
maintainer notes if present.
