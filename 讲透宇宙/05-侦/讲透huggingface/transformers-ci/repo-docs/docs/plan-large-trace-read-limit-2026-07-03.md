# Plan: large shard traces exceed Tempo's read-path limit (tests_torch vanishes)

**Date:** 2026-07-03
**Status:** immediate mitigation shipped; source-side reduction IMPLEMENTED
(one-span-per-test via `span_pruning`, PR #12 — 85% fewer spans measured
end-to-end). Band-aid revert pending prod confirmation of small traces.

## Symptom

`tests_torch` (and, for large runs, whichever job produces the biggest shard
traces) is missing from the **Jobs** table on the by-run dashboard and from the
`/run` drill-down, even though the job ran and its traces are in Tempo.

Reproduced on run `28653280321:1`: GitHub ran all 8 `tests_torch` shards
(success); Tempo search/tag-values list `tests_torch`; but the Prometheus
`pytest_run_job_*` series and the persisted run store (`28653280321_1.json.gz`,
47,276 rows) both contain the same 14 jobs with **no `tests_torch`**.

## Root cause

The exporter turns a trace into rows by fetching it whole via
`GET /api/traces/{id}`. A `tests_torch` shard trace is **~36 MB / ~100k spans**
(post span-id-collision-fix — before the fix duplicate span_ids collapsed a
shard to ~6k spans, which stayed under the limit). Tempo's querier assembles the
whole trace and sends it to the query-frontend in **one gRPC message**, capped
by `server.grpc_server_max_send_msg_size` = **16 MiB** (the Tempo default). So:

```
GET /api/traces/{id}
→ HTTP 500  "response larger than the max (36329178 vs 16777216)"
```

`_fetch_trace_with_settled` catches the error and returns `None`, so the trace
is **never shaped**. Both the Prometheus roll-up (`extract_run_rollup_metrics`)
and the run store (`persist_settled_runs`) consume the shaped `extracted` set,
so the whole job disappears from both, identically — while the job's tiny setup
traces (1752 B) fetch fine but carry no test rows.

Ingestion was already raised to 64 MiB (`max_bytes_per_trace`,
`max_recv_msg_size_mib`, `max_request_body_size`); only the **read/gRPC-send**
path was left at 16 MiB.

**Blast radius:** ~27.6k trace-by-id HTTP 500s / 24h (~17% of all reads) — it
drops the biggest job from *every* large run, not one PR.

## Shipped mitigation (this change)

Reading a giant trace back turned out to require raising limits at **three**
layers — each one uncovered the next:

1. **Tempo read limit** — `deploy/helm/templates/tempo.yaml`. The 16 MiB cap was
   NOT `server.grpc_server_max_send_msg_size` (raised that too, needed for the
   frontend's receive side) but **`querier.frontend_worker.grpc_client_config.max_send_msg_size`**
   — the querier→frontend hop, whose send side defaults to 16 MiB while its recv
   already defaults to 100 MiB. Raised both to 64 MiB. Verified: the 36 MB trace
   that 500'd now returns 200. Requires a `tempo-0` restart (ConfigMap change
   alone does NOT roll a StatefulSet pod).
2. **Exporter HTTP timeout** — `values.yaml` `config.httpTimeout` 10s → 45s. A
   40–65 MB trace takes ~10s+ to assemble in-cluster; at 10s the fetch timed out
   right at the edge, so the trace would still be dropped (now as `timeout`).
3. **Exporter memory** — `env/private.yaml` limit 2Gi → 4Gi. Parsing a 40–65 MB
   trace costs several hundred MB; up to `fetchConcurrency` (4) parse at once on
   top of the ~1.4 GiB caches. At 2Gi a big run OOM-killed the exporter.
4. **Render cadence** — `values.yaml` `config.traceRefetchSeconds` 300s → 900s.
   Once the exporter actually downloaded the big traces, render jumped ~10s →
   ~300–330s, at/above the 300s refetch interval → the whole window re-fetches
   every cycle and render spirals. 900s sits above render, below lookback/2.
5. **Visibility** — `pytest_trace_exporter_trace_fetch_errors_total{reason=...}`
   (exporter) + a "Trace read failures — dropped jobs (too_large)" panel on the
   CI Health dashboard, cross-checked against
   `tempo_request_duration_seconds_count{route="api_traces_traceid",status_code=~"5.."}`.

### Caveat — the mitigation is a moving ceiling (this is the point)

Every layer above is a band-aid, and layer 4 shows the cost is already biting:
downloading + parsing 40–65 MB traces makes the exporter's render ~30× slower
(metrics now refresh every ~5 min) and holds far more RAM. tests_torch will keep
growing; at 60–100 MB we hit the limits again *and* Tempo/exporter RSS pressure
(Tempo already OOM-restarted at the 8Gi→16Gi bump). **The render-time blowup is
the signal that the durable fix below is now required, not optional.**

## Source-side reduction — RECOMMENDED FIX (studied 2026-07-03)

**Emit one span per test (the protocol span); suppress the `::setup` / `::call`
/ `::teardown` phase spans and the fixture spans.**

### Why this one

Measured a real shard trace (tests_generate, 5.8 MB, 7647 spans, 1291 tests):

| span kind | count | share | used by our dashboards? |
|---|---|---|---|
| test **protocol** span (`name == nodeid`) | ~1291 | 17% | **YES — the only one** |
| `::setup` / `::call` / `::teardown` (span_type=`test`) | ~3861 | 50% | no |
| fixture spans (span_type=`fixture`) | ~2486 | 33% | no |

The exporter reads **only** the protocol span: `extract_trace_rows` requires
`span_type == "test"` **and** `operation_name == nodeid` (trace_exporter.py:1686);
`extract_failure_details` filters the same way (:241). The other ~83% of spans
exist solely for the Tempo waterfall view. Dropping them:

- **~83% smaller traces** → a ~50 MB tests_torch shard → ~8.5 MB, under the
  16 MiB read limit with headroom for growth.
- **No topology change** (still one trace/shard), **no exporter change**, **no
  increase in trace count / Tempo cardinality**.
- **No metric/dashboard/failure-view regression.** Pass/fail status lands on the
  protocol span via `pytest_runtest_logreport` (fires after each phase span
  closes, when the protocol span is current). Exception tracebacks: with the
  `::call` span gone, `pytest_exception_interact`'s `get_current_span()` is the
  protocol span, so `record_exception` lands there — exactly where
  `extract_failure_details` looks.
- **Lets us revert the band-aids** (httpTimeout 45→10, mem 4→2 Gi, refetch
  900→300, and even the Tempo gRPC bump) once trace sizes are proven small,
  restoring the ~10s render.
- **Cost:** the Tempo trace waterfall loses per-phase/per-fixture timing for a
  test — a rarely-used debugging nicety.

### Implementation

In `pytest_configure` (next to `id_generator.install()`), monkeypatch the
pytest-opentelemetry plugin (`PerTestOpenTelemetryPlugin` /
`OpenTelemetryPlugin`) to make these hookwrappers a plain `yield` (no span):
`pytest_runtest_setup`, `pytest_runtest_call`, `pytest_runtest_teardown`,
`pytest_fixture_setup`. Keep `pytest_runtest_protocol` (per-test span), the
session/run span, `pytest_exception_interact`, `pytest_runtest_logreport`.
Same install mechanism as `id_generator` (class-method patch, before first span).

### Validation before rollout

Run one real shard (staging or local `-n 8` xdist) and confirm: (1) the shard's
trace is single-digit MB; (2) `GET /api/traces/{id}` returns 200; (3) a failing
test still shows ERROR in the Jobs table and a full traceback on `/failure`;
(4) test counts per job match. Then repoint prod and revert the band-aids.

### Why not the alternatives

- **Per-worker traces** (drop the shared trace via patching
  `XdistOpenTelemetryPlugin.pytest_configure_node` context injection — note
  merely unsetting `TRACEPARENT` does NOT work; the plugin re-injects the
  controller context into every worker's `workerinput`, :298). Content-preserving
  ÷8 → ~6 MB, but multiplies trace count 8× (heavier Tempo + exporter
  enumeration) and needs care to nest a worker's tests under a fresh per-worker
  root rather than one-trace-per-test. Keep as a follow-on only if per-test spans
  still grow past the limit.
- **TraceQL span-paging in the exporter** (never fetch whole traces): biggest
  rework; unnecessary once traces are ~8 MB.

## Verification

- After deploy: `curl .../api/traces/<big tests_torch id>` returns 200.
- `pytest_trace_exporter_trace_fetch_errors_total{reason="too_large"}` stops
  climbing; the CI Health panel goes flat.
- A fresh large run shows `tests_torch` in the Jobs table and `/run` table.
