# Split Comparison — Module Architecture

## Summary

`cosmos_curator.pipelines.video.split_comparison` compares two split-pipeline outputs over the columnar Lance
clip-metadata dataset (`<output_root>/lance/<version>`). It runs in two phases — **measure** (record raw per-side values
and diffs for every clip and caption window into durable Lance tables) and **eval** (apply tolerance/threshold policy to
those tables → issues + per-clip verdicts). Measurement runs on **Ray Data**, fanning the GPU-bound caption work across
one-GPU actors; a run always uses Ray and at least one GPU.

This document maps the module structure so a newcomer can navigate the package. The split pipeline emits one columnar
Lance dataset per output, so comparison is a single columnar scan in which only the caption embedding is heavy enough to
be worth distributing.

## Two phases

- **measure** (`measure.ray` driver over `measure.core` primitives, persisted by `store`): load both Lance datasets,
  compute clip-scalar diffs (vectorized, columnar) and caption-window diffs (the one expensive, GPU-bound step), and
  write `clip.lance` / `window.lance` + a provenance `manifest.json`. No thresholds are applied.
- **eval** (`eval`): apply `config`'s tolerances/threshold to the measurement tables → `issues.lance` +
  `clip_verdict.lance` + `eval.json`. It consumes the measurement tables, never the source, so it runs in-memory right
  after measure (locality) or standalone for fast re-evaluation under new thresholds (no GPU, no source IO).

Summary-level (`summary.json`) comparison is layered in via `summary`, which runs the package's `summary_loader` /
`summary_compare` over snapshots written into the measurements root.

## The measure engine

Measurement runs on Ray Data (`measure.ray.run`, the package's measure entry point). The pure measurement logic lives in
`measure.core` — the Ray actor body is `core.measure_window_batch`, the driver clip pass is
`core.clip_measurements_columnar`; `measure.ray` only adds scheduling around it.

- Both Lance tables are `ray.put` once; actors `ray.get` them zero-copy from the object store and `take` only their
  batch's rows from a tiny `(clip_uuid, idx_a, idx_b)` alignment index.
- Block count is derived from `--batch-size` (see `_stage_sizing`): many small blocks let Ray work-steal across actors,
  which removes the long tail from uneven per-clip caption work (most clips embed nothing; a few embed many).
- The driver's clip pass is cheap and columnar, so the only work that fans out is the caption embedding.

There is no single-process engine — a run always uses Ray and at least one GPU. What keeps the measurement logic testable
without a GPU or a Ray runtime is that the primitives live in the Ray-free `measure.core` (see
`tests/.../measure/test_core.py`), not a second engine.

## Module dependency graph (the shape)

```text
cli
 |-- measure.ray  --> measure.core --> load, measure.schema     <- measure: Ray driver over the Ray-free core
 |-- store        --> eval, measure.core, measure.schema
 |-- eval         --> measure.core, eval_schema
 +-- summary      --> store
```

It is a clean DAG (no cycles). The measure spine is `cli -> measure.ray -> measure.core -> load`; `measure.core` is the
shared hub (reached from `ray`, `eval`, and `store`). `cli`'s direct edges to `measure.core` / `load` only pull
types/constants (`Measurements`, `DEFAULT_LANCE_VERSION`), not logic, and `cli` imports `measure.ray` lazily so the
`--skip-measure` re-eval path never loads Ray.

## Precise edges (module → modules it imports/calls)

```text
cli            -> measure.ray*, measure.core, eval, store, summary, load   (* lazy, measure branch only)
measure.ray    -> measure.core, measure.schema, load
measure.core   -> measure.schema, load
measure.schema -> (leaf)
eval           -> measure.core, eval_schema
store          -> eval, measure.core, measure.schema
summary        -> store
load           -> (leaf)
eval_schema    -> (leaf)
```

## Module roles

| module | role | key entry |
|---|---|---|
| `cli` | parse args, run measure/eval phases, write outputs | `main` |
| `measure.ray` | the measure driver — Ray Data GPU-actor fan-out | `run` |
| `measure.core` | engine-agnostic primitives (clip diff, window/caption, rollups, stats, model opts) | `clip_measurements_columnar`, `measure_window_batch` |
| `measure.schema` | Arrow schemas for the clip / window measurement tables | — |
| `eval` | apply policy → issues + verdicts | `evaluate` |
| `store` | persist/read Lance datasets + manifest, snapshot summaries | `write_measurements`, `write_eval` |
| `summary` | summary.json comparison | `summary_issues` |
| `load` | read source clip-metadata Lance, project required columns | `load_clip_metadata` |
| `eval_schema` | Arrow schema for the per-clip verdict table | — |
| `config` | input contract (`SplitComparisonConfig` + policy types) | — |
| `result_model` | the `Issue` row contract + `ISSUE_SCHEMA` / `make_issue` | — |
| `caption_embedding` | load the caption model, batched cosine similarity | `load_caption_model`, `cosine_similarity_batch` |
| `summary_loader` / `summary_compare` / `summary_schema` | load + compare `summary.json` and its schema | — |

## External boundary

The comparison logic is self-contained in this package; everything it depends on outside itself is infrastructure:

```text
storage_utils, lance   <- load, store        (read source Lance; write measurement/eval Lance + JSON)
ray / ray.data         <- measure.ray        (only here -- the rest of the package is Ray-free)
pyarrow(.compute)      <- core, load, schema, eval, ...
sentence-transformers  <- caption_embedding  (the BGE caption model)
```

## Design properties worth knowing

- **`measure.core` is the Ray-free hub.** `ray`, `eval`, and `store` point at it; it points only at `load` /
  `measure.schema` and knows nothing about Ray. The dependency runs one way — `measure.ray` builds on `core`, never the
  reverse — which is exactly what keeps the measurement logic unit-testable without a GPU or a Ray runtime.
- **Lazy Ray isolation.** `import ray` lives only in `measure.ray`, which `cli` imports lazily inside its measure branch.
  So the `--skip-measure` re-eval path (and importing the `measure` package itself) never loads Ray Data.
- **Columnar clip convergence.** Clip-scalar measurement is one vectorized `pyarrow.compute` pass
  (`core.clip_measurements_columnar`) — a flat-scalar full-outer join that never materializes the nested caption text. Only
  the caption embedding is heavy, so that is all the actor pool distributes. (See `tests/.../measure/test_core.py` for the
  parity check against the reference per-row implementation.)
- **One batch knob.** `--batch-size` is both the GPU encode chunk and the Ray block-count target; smaller means more
  blocks and better load balancing.

## Arrow facts that shape the design

Verified properties that drive the columnar approach:

- **Zero-copy means slicing, not selection.** `Table.slice` returns a view; `take` / `filter` / `join` gather into new
  buffers and copy — like numpy basic slicing vs. fancy indexing.
- **`Table.join` rejects nested non-key columns.** The `windows` (`list<struct>`) column can't go through a relational
  join — which is why the columnar clip join projects each side to flat scalars first (windows → a `num_windows` length).
  `filter` / `take` / Arrow block transport all carry the nested column fine; the limit is the join op, not
  storage/transport.
- **Aligning the two independently-ordered outputs by `clip_uuid` is inherently a copy** (a gather/shuffle); there is no
  zero-copy view of "A's and B's rows for these clip_uuids".

## Not implemented

Clip-MP4 `VideoIndex` comparison — slow per-clip MP4 opens. If needed later, record `VideoIndex` into the clip Lance
upstream and compare it as just another column.
