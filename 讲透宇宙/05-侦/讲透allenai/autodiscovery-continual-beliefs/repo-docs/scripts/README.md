# Figure-reproduction scripts

Standalone scripts that regenerate every figure in the paper from the committed, plot-ready
CSV tables in [`paper_results/`](../paper_results). No raw run data, notebooks, or cloud
access is required.

## Usage

```sh
pip install -e .                         # installs pandas, matplotlib, seaborn
python scripts/make_all_figs.py          # regenerate all figures into figs/
python scripts/fig_search_main_bar.py    # ...or a single figure
```

Outputs are written to `figs/` (override with `AUTODS_FIG_OUT`); data is read from
`paper_results/` (override with `AUTODS_FIG_DATA`).

## Figure → script → data

| Figure (`figs/*.pdf`) | Script | Data file (`paper_results/`) |
| --- | --- | --- |
| `hypothesis_belief_distribution` | `fig_hypothesis_belief_distribution.py` | `search_surprisals.csv` |
| `search_static_vs_nonstationary` | `fig_search_static_vs_nonstationary.py` | `search_surprisals.csv` |
| `search-all` | `fig_search_all.py` | `search_surprisals.csv` |
| `search-main-bar` | `fig_search_main_bar.py` | `search_surprisals.csv` |
| `search-ablation-bar` | `fig_search_ablation_bar.py` | `search_surprisals.csv` |
| `belief_update_filtering_analysis` | `fig_belief_update_filtering_analysis.py` | `search_surprisals.csv` |
| `search-diversity` | `fig_search_diversity.py` | `search_diversity.csv` |
| `search-diversity-cosine` | `fig_search_diversity_cosine.py` | `search_diversity.csv` |
| `spurious_surprisal` | `fig_spurious_surprisal.py` | `context_surprisals.csv` |
| `spurious_surprisal_topk_breakdown` | `fig_spurious_surprisal_topk_breakdown.py` | `context_surprisals.csv` |
| `icl_top_k_reduction_tokens` | `fig_icl_top_k_reduction_tokens.py` | `topk_effort_surprisals.csv` |
| `icl_top_k_total_surprisals_tokens` | `fig_icl_top_k_total_surprisals_tokens.py` | `topk_effort_surprisals.csv` |
| `spurious_surprisal_long_horizon_cost` | `fig_spurious_surprisal_long_horizon_cost.py` | `topk_effort_surprisals.csv` |

See [`paper_results/README.md`](../paper_results/README.md) for the data dictionary.

## Shared modules

- `_figlib.py` — paths, plotting/output helpers, CSV loaders.
- `_netstats.py`, `_evalicl.py`, `_diversity.py` — cumulative-surprisal / aggregation helpers
  shared by the figures derived from each source.

> Note: `icl_top_k_reduction_tokens.pdf` and `icl_top_k_total_surprisals_tokens.pdf` render
> the same total-surprisal plot; the former matches the filename used in the paper appendix.
