---
name: bigquery-api
description: Run SQL against Google BigQuery and browse its catalog — submit queries (sync or async), poll job status, page through results, list datasets/tables, and read table schemas. Use this whenever the user wants to query a BigQuery table, ask "what's in this dataset", check a BigQuery job's status, or mentions bigquery.googleapis.com or a `project.dataset.table` path. Always start from this skill when interacting with this service — its bundled scripts and recipes are the fastest path.
---

BigQuery's REST API (`bigquery.googleapis.com/bigquery/v2`) lets you run SQL, inspect jobs, and browse datasets and table schemas with plain `curl` — no SDK required.

The central concept is a **job**. Every query runs as a job in a **project** (the project is billed, and is not necessarily where the data lives). Under the hood a query runs one of two ways — `scripts/bq_query.sh` (operation 1) drives this for you:

- **Synchronous** (`jobs.query`) — one POST that blocks up to a timeout and returns rows inline if the query finishes in time.
- **Asynchronous** (`jobs.insert` → `jobs.get` → `jobs.getQueryResults`) — submit, poll, then page results. The route you use directly for destination tables, `BATCH` priority, or load/extract/copy jobs.

Everything else (datasets, tables, schemas) is a simple GET.

## Request setup

Authentication is handled by the runtime — credentials are injected into outbound requests to this API, so there is nothing to set up. Do not try to create, mint, refresh, or validate tokens or keys. Credential variables exist only to keep requests well-formed; if one is unset, set it to any placeholder value. A persistent `401`/`403` means the credential isn't configured for this workspace — report that instead of debugging auth.

Every request carries `Authorization: Bearer ...` and is rooted at a **billing project**:

```bash
export GCP_PROJECT="my-project"   # the project that pays for queries — must be real
export BQ_TOKEN="placeholder"     # injected by the runtime; any value works
```

Define a helper to avoid repeating the base URL and auth header on every call:

```bash
export BQ="https://bigquery.googleapis.com/bigquery/v2/projects/${GCP_PROJECT}"
bq_curl() { curl -sS "$@" -H "Authorization: Bearer ${BQ_TOKEN}"; }
```

**Sanity check** — confirm the project is right and the workspace is wired up:

```bash
bq_curl "${BQ}/datasets?maxResults=1" | jq .
# 200 with a "datasets" array on success (the key is omitted entirely when the project
# has no datasets — that's still a success); 401/403 otherwise.
```

## Core operations

### 1. Run a query (`scripts/bq_query.sh`)

Run SQL through the bundled script (path is relative to this skill's directory): it submits the
query, polls until done with `location` threaded through, pages through every result page, and
decodes the `f`/`v` cell encoding for scalar columns (nested/repeated columns are emitted as raw
`f`/`v` JSON — post-process with `jq` if you need them flattened).

```bash
scripts/bq_query.sh \
  'SELECT name, SUM(number) AS total
   FROM `bigquery-public-data.usa_names.usa_1910_current`
   WHERE state = @state GROUP BY name ORDER BY total DESC LIMIT 10' \
  --param state=STRING:CA --max-gb 5
```

- SQL is one argument (single-quote it so backticked table names survive the shell) or stdin.
  Instance specifics come from `GCP_PROJECT` / `BQ_TOKEN` above; `--project` overrides the billing
  project.
- `--param NAME=TYPE:VALUE` (repeatable) sends named query parameters — prefer it over
  interpolating values into the SQL string.
- `--dry-run` prints the bytes a query would scan without running it; `--max-gb N` makes the query
  fail rather than scan more than N GiB.
- `--max-rows N` caps fetched rows (default 10000, `0` = everything); `--json` emits one JSON
  object per row instead of TSV with a header. Job ID, bytes scanned, and row counts go to stderr.
- Exit codes: `0` success, `1` request or query failed (API message on stderr), `2` gave up waiting
  after `--max-wait` seconds (default 600) — the job ID is on stderr; poll it with the endpoints
  below.

If the script errors, read it — it's plain `curl` + `jq` — and debug against `references/api.md`.
For array/struct parameters, destination tables or write disposition, `BATCH` priority, or
non-query jobs (load/extract/copy), use `jobs.insert` directly (next operation).

### 2. Submit a job directly (`jobs.insert` → `jobs.get`)

When you need a destination table, write disposition, `BATCH` priority, or a non-query job
(load/extract/copy), submit the job yourself and poll. `POST ${BQ}/jobs` returns immediately with a
`jobReference`:

```bash
JOB=$(bq_curl -X POST "${BQ}/jobs" -H "Content-Type: application/json" \
  -d '{"configuration": {"query": {"query": "SELECT ...", "useLegacySql": false}}}')
JOB_ID=$(jq -r '.jobReference.jobId // empty' <<<"$JOB")
LOCATION=$(jq -r '.jobReference.location // empty' <<<"$JOB")
```

Then poll `GET ${BQ}/jobs/${JOB_ID}?location=${LOCATION}` until `.status.state` is `DONE` — sleep
between calls and bound the loop (`scripts/bq_query.sh` is the reference implementation). The full
`configuration.query` body — destination table, write disposition, `maximumBytesBilled`, priority,
parameters — is in `references/api.md`, section Query job configuration.

- If `JOB_ID` came back empty the insert itself failed; surface `.error` instead of polling.
- Always pass `location` back when polling — a job is pinned to the location it ran in, and
  omitting it can 404 for non-US datasets.
- A `DONE` job can still have failed: check `.status.errorResult` before fetching results.
- Fetch a query job's rows with `GET ${BQ}/queries/${JOB_ID}?location=${LOCATION}&maxResults=1000` —
  cells come back as `{"f": [{"v": "..."}]}` in schema order (column names in
  `.schema.fields[].name`); more pages follow `.pageToken` (see Pagination).

### 3. Cancel a running job

```bash
bq_curl -X POST "${BQ}/jobs/${JOB_ID}/cancel?location=${LOCATION}" | jq '.job.status // .error'
```

Cancellation is best-effort; poll `jobs.get` to confirm.

### 4. List recent jobs

```bash
bq_curl "${BQ}/jobs?maxResults=20&projection=full&allUsers=false&stateFilter=done" \
  | jq '.jobs[]? | {id: .jobReference.jobId, state: .status.state, query: (.configuration.query.query // "" | .[0:80]), bytes: .statistics.query.totalBytesProcessed}'
```

### 5. List datasets

```bash
bq_curl "${BQ}/datasets?maxResults=100" \
  | jq '.datasets[]? | {id: .datasetReference.datasetId, location}'
```

Pass `?all=true` to include hidden datasets. For a different project's datasets, swap the project in the URL (you need `bigquery.datasets.get` there).

### 6. List tables in a dataset

```bash
DATASET="my_dataset"
bq_curl "${BQ}/datasets/${DATASET}/tables?maxResults=100" \
  | jq '.tables[]? | {id: .tableReference.tableId, type, creationTime}'
```

`type` is `TABLE`, `VIEW`, `EXTERNAL`, `MATERIALIZED_VIEW`, or `SNAPSHOT`.

### 7. Get a table's schema and size

```bash
TABLE="events"
bq_curl "${BQ}/datasets/${DATASET}/tables/${TABLE}" \
  | jq '{rows: .numRows, bytes: .numBytes, partitioning: .timePartitioning, schema: [.schema.fields[]? | {name, type, mode}]}'
```

Nested columns appear as `type: "RECORD"` with their own `fields[]` — recurse if you need the full tree.

### 8. Preview table rows without a query (`tabledata.list`)

Reads rows directly from storage — no query job, no bytes-scanned cost.

```bash
bq_curl "${BQ}/datasets/${DATASET}/tables/${TABLE}/data?maxResults=10" \
  | jq '.rows[]?.f | map(.v)'
```

## Pagination

Every list-style endpoint uses the same scheme: the response carries a token when there's more, and you pass it back as `?pageToken=` on the next call. Stop when the field is absent. `maxResults` caps a single page; the actual API ceilings are size-based (~10 MB per `tabledata.list` page, ~20 MB per `getQueryResults` page) rather than a fixed row count — the bundled script defaults to 1000 rows per page.

The response field name is not uniform — check which one your endpoint returns:

- `pageToken` — `jobs.query`, `jobs.getQueryResults`, `tabledata.list`.
- `nextPageToken` — `datasets.list`, `tables.list`, `jobs.list`, `routines.list`, `models.list`.

Reading `.pageToken` on a `datasets.list` response silently yields `null` and you get one page.

Query results add one wrinkle: `jobs.query` and `jobs.getQueryResults` also return `totalRows`, which is the full count even when a single page is smaller — use it to size progress bars, not as a stop condition.

## Rate limits & quotas

BigQuery enforces per-project quotas rather than per-request rate limits. The ones you'll hit:

- **Concurrent queries**: BigQuery decides how many queries run at once (dynamic concurrency) and queues the rest — up to 1,000 queued interactive queries per project per region. Past that, submits fail with `quotaExceeded` / `jobRateLimitExceeded`.
- **API requests**: most methods are capped at ~100 requests per second per user per method (`jobs.get` and `tabledata.list` allow more) — poll with a `sleep`, not a hot loop.
- **On-demand bytes scanned** and **slot-time** quotas depend on your billing model.

`429` and `403 rateLimitExceeded` / `quotaExceeded` responses carry a retryable reason in `error.errors[].reason`. Back off exponentially and retry; don't tighten the poll interval.

## Error handling

Every error response is `{"error": {"code": N, "message": "...", "errors": [{"reason": "..."}]}}` — check `.error` before projecting. The `reason` string is the most useful field.

- `401` — Credential missing or rejected. Check `BQ_TOKEN` is set at all (any value works). If it persists, the credential isn't configured for this workspace — report it.
- `403 accessDenied` — Caller lacks permission on the project/dataset. Check which project is in the URL (billing project) vs. which project owns the data — they can differ. Grant `roles/bigquery.dataViewer` on the data, `roles/bigquery.jobUser` on the billing project.
- `404 notFound` — Job, dataset, or table doesn't exist, or you omitted `location` on a job lookup. Double-check the full reference (`project.dataset.table`). Always pass `?location=` on `jobs.get` / `getQueryResults`.
- `400 invalidQuery` — SQL error. The `message` carries line/column. Remember `useLegacySql: false`.
- job `status.errorResult` — Query ran but failed. A job can be `DONE` and still failed — always check `status.errorResult` before fetching results.
- `5xx` / `backendError` — Transient Google-side. Retry with backoff. Safe for read jobs; for write jobs, check whether the first attempt actually ran before retrying.

## Going deeper

`references/api.md` has the fuller endpoint catalog — the job configuration object in detail (destination tables, write disposition, load/extract/copy jobs), dataset and table create/update, routines, and row-level access policies. Read it when you need an endpoint not covered above or the exact body shape for a write.
