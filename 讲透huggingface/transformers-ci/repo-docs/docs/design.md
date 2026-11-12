# Design Overview

How a pytest run becomes a Grafana dashboard (and a public dataset), and where
each piece of code sits. For module-internal detail read the docstring at the top of each file in
`src/transformersci/otel/` and `src/transformersci/publish/`.

## 1. The shape of the system

The system is split into a **producer** side (runs inside the CI job, emits
telemetry) and **consumer** side(s) that read it back out. Nothing is shared
between them except the backends in the middle — the producer writes to Tempo;
the consumers read from Tempo. There are two consumers: the live exporter
(`otel/`) that drives Grafana, and the data publisher (`publish/`) that ships a
public dataset.

```
   CI job (pytest)                  observability stack
 ┌───────────────────┐         ┌──────────────────────────────┐
 │ cli.py wraps      │  OTLP   │ Tempo (trace store, durable) │
 │ pytest, sets OTel │ ───────▶│                              │
 │ resource attrs +  │         └───────┬──────────────┬───────┘
 │ trace context     │                 │ /api/search  │ (same client,
 │                   │                 │ /api/traces  │  wider window)
 │ resource_plugin   │  JSONL          ▼              ▼
 │ samples CPU/mem/  │ ──────┐  ┌───────────────┐  ┌──────────────────┐
 │ GPU per test, and │       │  │ trace_exporter│  │ publish/main.py  │
 │ mirrors spans to  │       └─▶│ render Prom   │  │ shape → Parquet  │
 │ a staging backend │ (on box) │ /metrics      │  │ + raw trace JSON │
 └───────────────────┘          └──────┬────────┘  └────────┬─────────┘
                                       │ scrape             │ hf sync
                                       ▼                    ▼
                               ┌───────────────┐   ┌──────────────────┐
                               │ Prometheus →  │   │ HF bucket        │
                               │ Grafana       │   │ (public dataset) │
                               └───────────────┘   └──────────────────┘
```

## 2. Producer side — emitting telemetry

### `cli.py` — `transformersci-otel`
Every CI pytest invocation runs through this wrapper. Its job is to make a test
run show up as a single, well-labeled trace:

- **Endpoint/transport resolution** — reads the standard `OTEL_*` env vars,
  normalizes protocol (`grpc`/`http`), picks the matching exporter, and can
  preflight-ping the collector.
- **CI metadata** — detects the provider (GitHub Actions / CircleCI / local) and
  extracts repository, PR number/URL, and workflow/job run IDs, folding them
  into OTel **resource attributes** (e.g. `transformers.test.run.id`,
  `transformers.test.job`). These attributes are what the dashboards group and
  label on downstream.
- **Trace context** — generates or inherits a W3C `traceparent` so all of a
  run's spans share one trace id.
- **Exec** — builds the child environment + argv and execs pytest.

### `resource_plugin.py` — pytest plugin
Loaded into the test session itself. Two independent jobs:

- **Per-test resource sampling** — samples CPU/memory (and GPU via torch when
  present) around each test and appends one JSONL row per test to a metrics file
  on the box. This is kept **out of the spans** deliberately: bulky time-series
  samples would bloat traces, so they ride a side channel that the exporter
  reads back later.
- **Staging span mirror** — installs a *second* span processor so spans are
  shipped to a staging backend on top of the primary export, with its own
  endpoint/headers/protocol. (gRPC requires lowercase header keys — the
  `authorization` casing fix lives here.)

### `debug_exporter.py` — opt-in diagnostic
Monkeypatches the span exporter's `export()` to log every attempt (span count,
result/exception, duration, protocol, endpoint) to stderr. Used only while
debugging "are spans actually leaving the box"; off in steady state.

## 3. Backends in the middle

- **Tempo** is the durable trace store and the single source of truth for the
  consumer. The exporter holds no trace state of its own.
- **Resource JSONL file** lives on the exporter's `/data` volume and carries the
  per-test resource samples the plugin wrote.
- **Prometheus** scrapes the exporter's `/metrics`; its TSDB is the durable
  store of the derived time-series. **Grafana** renders the dashboards.

## 4. Consumer side — `trace_exporter.py`

A long-running HTTP service. Prometheus scrapes `/metrics`; the body is derived
entirely from Tempo each cycle, so the exporter is effectively stateless. The
pipeline:

1. **Fetch & shape** — search Tempo for trace ids in the lookback window, fetch
   each, and convert OTLP JSON into Jaeger-shaped dicts the extractors expect. A
   **dual-bounded LRU** (entry count *and* serialized-byte budget) memoizes
   *settled* (immutable, aged-out) traces so a long replay can't grow RSS
   without limit.
2. **GitHub enrichment** — cached, rate-limit-aware lookups of PR title/state,
   reviews, and commit messages, used to label runs.
3. **Metric extraction** — a family of `extract_*` functions producing per-test
   durations, per-run roll-ups, PR info/state gauges, averages, and resource
   metrics (read from the plugin's JSONL).
4. **Self-observability** — the exporter emits its own `up`, render duration,
   RSS, and last-render timestamp so its health is visible on the CI dashboard
   even when CI is idle.
5. **Render, publish & serve** — see below.

### Why rendering is decoupled from scraping
A single render does a multi-second Tempo search + fetch/shape of the whole
window. Doing that inside the scrape handler made scrapes exceed Prometheus's
`scrape_timeout` (the target went down with "context deadline exceeded" and
nothing landed). So:

- A **background thread** (`_refresh_loop`) renders on its own cadence and never
  holds a lock during the slow work.
- The rendered payload is **published to a disk file atomically** (write a
  sibling temp file → `fsync` → `os.replace` → directory `fsync`). The file
  lives on the persistent `/data` volume.
- `/metrics` **streams that file**, opening the fd first so a mid-serve
  `os.replace` can't tear the response.

This design is crash-safe by construction: the Prometheus payload is *derived*
data (Tempo + Prometheus's TSDB are the durable stores), so the only real risks
are a torn body and a gap with nothing to serve. Atomic publish removes the
first; persisting the last-good file across restarts removes the second — after
a crash the exporter serves the last complete payload immediately while it
re-renders. The trade-off is stale-but-complete data until the next render,
which the embedded `pytest_trace_exporter_last_render_timestamp_seconds` gauge
makes observable (alert on `time() - that`).

### `/failure`
A secondary endpoint that renders a single trace's failure details (stack trace,
GitHub source links) as HTML, for drill-down from the dashboard.

## 5. Second consumer — `transformersci.publish`

The other thing that reads Tempo is the **public data publisher**: a one-shot
job (run hourly by a docker sidecar's cron) that turns the same raw traces into
a public, daily-partitioned dataset on the `transformers-ci-telemetry` HF
bucket, so anyone can build apps on CI test data without access to the internal
stack. Tempo — *not* Prometheus — is the source: it wants raw per-test rows, not
pre-aggregated series, and it reuses the exporter's Tempo client
(`search_trace_ids` / `get_trace`) over a much wider window than the live scrape.

One cycle (`main.run_cycle`):

1. **Fetch the window** — `tempo_window.iter_window_traces` streams settled
   traces over a wide lookback (default 48h, across one or more service names).
2. **Shape** — `tables.shape_trace_rows` derives two daily-partitioned tables:
   `test_rows` (one row per test, carrying the *full untruncated* stacktrace) and
   `run_rollups` (one row per run/job). Row building is pure-python; only
   `write_parquet` touches pyarrow, lazily.
3. **Write partitions** — rows stream straight to per-day Parquet via a bounded
   `StreamingPartitionWriter`, and each raw trace JSON is written to its day
   partition then dropped. Streaming write-and-drop is what keeps the sidecar
   under its memory cap (materialising a whole window of multi-MB traces is what
   OOM-killed it).
4. **Document** — `data_card.render_data_card` writes the bucket's `README.md`
   and `manifest.write_manifest` writes the machine-readable `current_view.json`.
5. **Sync** — with `--sync`, push the staging dir to the bucket via `hf sync`
   (auth from `HF_TOKEN`); only changed files upload.

The cycle is **idempotent**: re-deriving and overwriting whole day partitions is
safe because settled traces are immutable, so a day stabilises once it ages past
the window and is never rewritten.

## 6. Tuning knobs

Both services are configured entirely via environment (see `docker-compose.yml`
for the deployed defaults).

**Exporter (`otel/`):**

| Env var | Purpose |
|---|---|
| `PYTEST_TRACE_EXPORTER_LOOKBACK` | How far back to search Tempo each render. |
| `PYTEST_TRACE_EXPORTER_LIMIT` | Max traces fetched per render. |
| `PYTEST_TRACE_EXPORTER_FETCH_CONCURRENCY` | Parallel Tempo fetches (kept low so single-node Tempo doesn't OOM). |
| `PYTEST_TRACE_EXPORTER_TRACE_CACHE_MAX` / `_MAX_BYTES` | Dual bound on the settled-trace LRU. |
| `PYTEST_TRACE_EXPORTER_TRACE_SETTLE_SECONDS` | Age at which a trace is treated as immutable and cacheable. |
| `PYTEST_TRACE_EXPORTER_PAYLOAD_FILE` | Where the rendered `/metrics` payload is published (persistent volume). |
| `PYTEST_TRACE_EXPORTER_CACHE_SECONDS` | Background render interval. |
| `PYTEST_GITHUB_TOKEN` | Authenticates GitHub enrichment (raises rate limit 60→5000/hr). |

**Publisher (`publish/`):**

| Env var | Purpose |
|---|---|
| `PUBLISH_WINDOW` | Tempo lookback per cycle (default `48h`). |
| `PUBLISH_LIMIT` | Max traces fetched per cycle (default 5000). |
| `PUBLISH_SERVICE_NAMES` | Comma-separated service names to publish (one publisher can cover several emitters). |
| `PUBLISH_ROW_BATCH` | Rows buffered per day before a Parquet row group is flushed (bounds peak memory). |
| `PUBLISH_STAGING_DIR` / `HF_BUCKET_URI` | Local staging dir and `hf://` destination. |
| `HF_TOKEN` | Auth for `hf sync`. |
