# headvis

> **Reference implementation.** This repository is not maintained and not accepting contributions. Report security issues to security@anthropic.com; we do not commit to fixes or timelines.

A visualization tool for attention heads in transformer language models. Pick a head, see its top-activating sequences across your dataset, its attention patterns, per-head metrics (induction score, previous-token score, entropy, …), and a PCA/UMAP projection of its Q/K/O/V space. Optionally decompose individual attention edges into contributing sparse-dictionary feature pairs.

The frontend is static-first — once `data/` is populated it serves from disk with no backend. A backend unlocks live operations (custom prompts, live attribution compute) but is optional.

## Quick start

```bash
npm install
npm run build
```

Serve `dist/` alongside a populated `data/` directory (see below).

## Populating `data/` — using Claude

`data_pipeline.py` and `server.py` are skeletons with the data-format contracts fully specified in docstrings. The intended workflow is to hand them to Claude Code with your model and dataset:

> Here's `data_pipeline.py` from the headvis repo. I want to run it against `gpt2` from HuggingFace using the `openwebtext` dataset, studying layers 5 and 8 across all heads. Implement the `NotImplementedError` functions and run the pipeline.

Claude reads the docstrings (which are the spec), implements the model-specific forward-pass and tokenization bits using `transformers` + `datasets`, and runs it. The output-format contracts are exact — as long as the JSON shapes match, the frontend works.

The same applies to `server.py` for the backend:

> Implement `add_custom_sequence` and `project_to_umap` in `server.py` for the same gpt2 setup. Leave the attribution endpoints stubbed (I don't have an SAE).

## Architecture

```
┌─────────────────────────────────┐
│  data_pipeline.py  (run once)   │──→  data/config.json
│                                 │     data/scatter_data.json
│  dataset scan → attention →     │     data/heads/L{l}H{h}.json
│  metrics, decile sampling,      │     data/umap/L{l}H{h}.json
│  PCA/UMAP fit                   │     data/umap/sequences.json
└─────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐          ┌──────────────────────────────┐
│  Svelte frontend (src/)         │ ◀──────▶ │  server.py  (optional)       │
│                                 │   POST   │                              │
│  static read from data/         │          │  live attribution,           │
│  optional runtime POST          │          │  custom-prompt ingestion,    │
│                                 │          │  UMAP point projection       │
└─────────────────────────────────┘          └──────────────────────────────┘
```

## Implementation

### `data_pipeline.py` — offline

Walks your dataset, computes attention per head, produces the static `data/` tree. Every metric is a closed-form reduction over the attention matrix — the `logit_*` trio need pre-softmax QK scores (hook the attention module or recompute `Q @ K.T`), everything else runs on post-softmax weights.

| function | produces | model required |
|---|---|---|
| `compute_head_metrics` | scatter-plot coordinates | yes (attention) |
| `sample_by_decile` | `heads/L{l}H{h}.json` sequences array | yes (attention) |
| `compute_projection_cloud` | `umap/L{l}H{h}.json` | yes (Q/K/O/V vectors) |
| `compute_qk_distance_histogram`, `compute_top_tokens` | derived stats | no (pure transforms) |
| `write_*` | JSON serialization | no |

Framework-agnostic parts (decile bucketing, COO sparsification, histogram binning, JSON writing) are pure data transforms — implementable once and reusable. Only the attention-extraction and vector-extraction bits depend on your model framework.

### `server.py` — runtime

Six endpoints. The frontend runs fully static without any of them.

| endpoint | unlocks | needs |
|---|---|---|
| `add_custom_sequence` | type any prompt, see its attention | model + tokenizer |
| `delete_custom_sequence` | delete button on custom prompts | file I/O only |
| `project_to_umap` | "where does this prompt sit in the PCA cloud?" | model + saved PCA rotation |
| `save_umap_clusters` | persist user-lassoed cluster labels | file I/O only |
| `qk_attributions`, `ov_attributions` | decompose an attention edge into feature pairs | sparse feature dictionary (SAE/transcoder) |

The two file-I/O-only endpoints are implementable with no model. The attribution endpoints need a trained sparse dictionary — see [SAELens](https://github.com/jbloomAus/SAELens) if you don't have one. Everything else is a single forward pass.

**Side-effect contract:** endpoints that produce durable results write them into `data/` so the next load hits the cache. The frontend tries `data/attributions/{qk,ov}/L{l}H{h}S{seq}Q{q}K{k}.json` before POSTing.

**The `context` blob:** `data/server_config.json` has a `context` field that the frontend forwards verbatim on every POST. It never interprets the contents — put whatever your implementation needs in there (model path, cache dir, etc.). Frontend in static-only mode when `server_config.json` is `{}` or missing.

### Data format details

Every JSON schema is in the docstrings of `data_pipeline.py`. A few that trip people up:

- **Sparse attention** — `attention_indices` are flat COO indices: `idx = q * seq_len + k`. Values are parallel. Store top-K per row or above a threshold; dense matrices blow up file sizes.
- **Intervals** — `interval=10` is the highest-activation decile, `interval=1` the lowest. 1-indexed. `interval=-1` (URL param) means the custom-sequences view.
- **Position 0** — the frontend's max-reductions skip row 0 and column 0 (see `src/lib/sparse.js`). Your `max_activation` should do the same.
- **`views` key** — if you only fit PCA, omit the `views` key from the UMAP JSON entirely; the frontend auto-selects PCA mode when `views` is absent.

## Deep linking

The frontend supports URL state: `?layer=L&head=H&tab=T&interval=N`. For a specific attribution: `?layer=L&head=H&attr=qk&seq=ID&qpos=P&kpos=P`. See `src/Index.svelte` for the full param list.
