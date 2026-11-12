# BigQuery REST API — Endpoint Reference

All endpoints are rooted at `https://bigquery.googleapis.com/bigquery/v2`. Most are project-scoped: `/projects/{project}/...`. Headers on every request (the bearer value is injected by the runtime — a placeholder is fine):

```
Authorization: Bearer ${BQ_TOKEN}
Content-Type: application/json      # on any request with a body
```

Official docs: `https://cloud.google.com/bigquery/docs/reference/rest`.

## Table of contents

- [Jobs](#jobs)
- [Query job configuration](#query-job-configuration)
- [Other job types](#other-job-types-load--extract--copy)
- [Datasets](#datasets)
- [Tables](#tables)
- [Table data](#table-data)
- [Routines, models, policies](#routines-models-policies)
- [Cross-cutting notes](#cross-cutting-notes)

---

## Jobs

- **`POST /projects/{p}/queries`** — `jobs.query`, sync query. Body: `{"query","useLegacySql":false,"timeoutMs","maxResults","dryRun","parameterMode","queryParameters","defaultDataset":{"projectId","datasetId"},"labels"}`.
- **`GET /projects/{p}/queries/{jobId}`** — `jobs.getQueryResults`, fetch/page results. Params: `location`, `maxResults`, `pageToken`, `startIndex`, `timeoutMs`.
- **`POST /projects/{p}/jobs`** — `jobs.insert`, async submit. Body: `{"configuration":{...},"jobReference":{"projectId","jobId","location"}}`. Supplying `jobId` makes the insert idempotent.
- **`GET /projects/{p}/jobs/{jobId}`** — `jobs.get`, poll status. Param: `location`. Returns `status.state` (`PENDING`/`RUNNING`/`DONE`), `status.errorResult`, `status.errors[]`, `statistics`.
- **`POST /projects/{p}/jobs/{jobId}/cancel`** — `jobs.cancel`. Param: `location`. Best-effort.
- **`DELETE /projects/{p}/jobs/{jobId}/delete`** — `jobs.delete`, remove metadata for a finished job. Param: `location`.
- **`GET /projects/{p}/jobs`** — `jobs.list`. Params: `allUsers`, `maxResults`, `pageToken`, `projection` (`minimal`/`full`), `stateFilter` (`pending`/`running`/`done`), `minCreationTime`, `maxCreationTime`, `parentJobId`.

`statistics.query` on a finished query job carries `totalBytesProcessed`, `totalBytesBilled`,
`cacheHit`, `totalSlotMs`, `numDmlAffectedRows`, and a `queryPlan` stage breakdown.

## Query job configuration

The `configuration.query` object on `jobs.insert`:

```json
{
  "configuration": {
    "query": {
      "query": "SELECT ...",
      "useLegacySql": false,
      "parameterMode": "NAMED",
      "queryParameters": [
        {"name": "x", "parameterType": {"type": "INT64"}, "parameterValue": {"value": "42"}}
      ],
      "destinationTable": {"projectId": "p", "datasetId": "d", "tableId": "t"},
      "createDisposition": "CREATE_IF_NEEDED",
      "writeDisposition": "WRITE_TRUNCATE",
      "priority": "INTERACTIVE",
      "allowLargeResults": false,
      "maximumBytesBilled": "1000000000",
      "defaultDataset": {"projectId": "p", "datasetId": "d"}
    },
    "dryRun": false,
    "labels": {"team": "data"},
    "jobTimeoutMs": "600000"
  }
}
```

- `createDisposition`: `CREATE_IF_NEEDED` (default) or `CREATE_NEVER`.
- `writeDisposition`: `WRITE_EMPTY` (default — fails if destination has data), `WRITE_TRUNCATE`,
  `WRITE_APPEND`.
- `priority`: `INTERACTIVE` (default, counts against concurrent-query limit) or `BATCH` (queued, no
  concurrency limit, may wait).
- `maximumBytesBilled`: hard cap — job fails rather than exceed it. A cheap guardrail.
- Array/struct parameters use `parameterType.arrayType` / `parameterType.structTypes` and
  `parameterValue.arrayValues` / `parameterValue.structValues`.

## Other job types (load / extract / copy)

Set exactly one of `configuration.query`, `.load`, `.extract`, `.copy`:

- **`load`** — Ingest from GCS → table. Key fields: `sourceUris:["gs://..."]`, `destinationTable`, `sourceFormat` (`CSV`/`NEWLINE_DELIMITED_JSON`/`PARQUET`/`AVRO`/`ORC`), `schema`, `autodetect`, `writeDisposition`, `skipLeadingRows`, `fieldDelimiter`.
- **`extract`** — Export table → GCS. Key fields: `sourceTable`, `destinationUris:["gs://bucket/prefix-*.csv"]`, `destinationFormat`, `compression` (`GZIP`/`NONE`). Use `*` in the URI for sharded output.
- **`copy`** — Table → table. Key fields: `sourceTable` or `sourceTables[]`, `destinationTable`, `writeDisposition`, `operationType` (`COPY`/`SNAPSHOT`/`RESTORE`/`CLONE`).

## Datasets

- **`GET /projects/{p}/datasets`** — List. Params: `all` (include hidden), `filter` (`labels.key:value`), `maxResults`, `pageToken`.
- **`GET /projects/{p}/datasets/{d}`** — One dataset: `location`, `defaultTableExpirationMs`, `access[]` (ACLs), `labels`.
- **`POST /projects/{p}/datasets`** — Create. Body: `{"datasetReference":{"projectId","datasetId"},"location":"US","description","defaultTableExpirationMs","labels"}`.
- **`PATCH /projects/{p}/datasets/{d}`** — Partial update. Send only the fields you change.
- **`PUT /projects/{p}/datasets/{d}`** — Full replace.
- **`DELETE /projects/{p}/datasets/{d}`** — Delete. Param: `deleteContents=true` to drop tables too.

## Tables

- **`GET /projects/{p}/datasets/{d}/tables`** — List. Params: `maxResults`, `pageToken`. Returns lightweight summaries.
- **`GET /projects/{p}/datasets/{d}/tables/{t}`** — Full metadata: `schema`, `numRows`, `numBytes`, `timePartitioning`, `rangePartitioning`, `clustering`, `type`, `view.query`, `materializedView.query`, `externalDataConfiguration`. Param: `selectedFields` to trim the response.
- **`POST /projects/{p}/datasets/{d}/tables`** — Create. Body: `{"tableReference":{...},"schema":{"fields":[...]},"timePartitioning":{"type":"DAY","field":"ts"},"clustering":{"fields":["a","b"]}}`. For a view, set `"view":{"query":"...","useLegacySql":false}` instead of `schema`.
- **`PATCH /projects/{p}/datasets/{d}/tables/{t}`** — Partial update (e.g., add columns by sending a superset schema).
- **`PUT /projects/{p}/datasets/{d}/tables/{t}`** — Full replace.
- **`DELETE /projects/{p}/datasets/{d}/tables/{t}`** — Delete.

Schema field:
`{"name","type","mode":"NULLABLE"|"REQUIRED"|"REPEATED","description","fields":[...]}`. `type` is
one of `STRING`, `INT64`, `FLOAT64`, `NUMERIC`, `BIGNUMERIC`, `BOOL`, `BYTES`, `DATE`, `DATETIME`,
`TIME`, `TIMESTAMP`, `GEOGRAPHY`, `JSON`, `RANGE`, `RECORD` (struct — has nested `fields`). Array =
any type with `mode: "REPEATED"`.

## Table data

- **`GET /projects/{p}/datasets/{d}/tables/{t}/data`** — `tabledata.list`, read rows in storage order, no query cost. Params: `maxResults`, `pageToken`, `startIndex`, `selectedFields`. Uses `pageToken` OR `startIndex`, not both.
- **`POST /projects/{p}/datasets/{d}/tables/{t}/insertAll`** — Streaming insert. Body: `{"rows":[{"insertId":"dedupe-key","json":{"col":"val"}}]}`. Returns per-row `insertErrors`. Not transactional.

## Routines, models, policies

- **`GET/POST /projects/{p}/datasets/{d}/routines`** — UDFs and stored procedures.
- **`GET/PUT/DELETE /projects/{p}/datasets/{d}/routines/{r}`** — One routine.
- **`GET /projects/{p}/datasets/{d}/models`** — BQML models.
- **`GET/PATCH/DELETE /projects/{p}/datasets/{d}/models/{m}`** — One model.
- **`GET /projects/{p}/datasets/{d}/tables/{t}/rowAccessPolicies`** — Row-level security policies.

---

## Cross-cutting notes

**Billing project vs. data project.** The project in the URL (`/projects/{p}/jobs`) is the *billing*
project — it pays for the query and needs `bigquery.jobs.create`. The data can live in a different
project, referenced via fully-qualified table names in the SQL. `403 accessDenied` often means you
have permission on one but not the other.

**Location pinning.** Jobs run in the location of the data they touch. Once a job exists, every
`jobs.get` / `getQueryResults` / `jobs.cancel` call must pass the same `?location=`. Missing or
wrong location returns `404 notFound`, which is misleading.

**Cell encoding.** Every row value is a string inside `{"v": "..."}` regardless of column type —
`INT64` is `"42"`, `BOOL` is `"true"`, `TIMESTAMP` is a float seconds-since-epoch string like
`"1.7234567e9"`, repeated fields are `{"v": [{"v": ...}]}`, and structs nest as
`{"v": {"f": [...]}}`. Parse with the schema, not by eyeballing.

**Destructive operations.** Dataset/table/routine/model `DELETE` and `WRITE_TRUNCATE` are
irreversible — confirm the fully-qualified target (and prefer a `dryRun` or `SELECT` first) before
issuing them.

**Idempotency.** `jobs.insert` is idempotent *if you supply `jobReference.jobId`* — retrying with
the same ID returns the existing job instead of creating a duplicate. `jobs.query` and `insertAll`
are not idempotent; `insertAll` supports per-row `insertId` for best-effort dedup.

**`jobs.query` vs `jobs.insert`** — when to use which is covered in `../SKILL.md` (intro and the
Core operations section).
