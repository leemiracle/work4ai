# Snowflake SQL API v2 — Endpoint Reference

Base URL: `https://${SNOWFLAKE_ACCOUNT}.snowflakecomputing.com`. Required headers on every request:

```
Authorization: Bearer ${SNOWFLAKE_TOKEN}
X-Snowflake-Authorization-Token-Type: KEYPAIR_JWT | OAUTH | PROGRAMMATIC_ACCESS_TOKEN   # optional — omit and Snowflake infers the type from the token
Content-Type: application/json
Accept: application/json
User-Agent: <name>/<version>              # required — requests without one are rejected
```

Official docs: `https://docs.snowflake.com/en/developer-guide/sql-api/`.

## Table of contents

- [Endpoints](#endpoints)
- [Request body](#request-body-post-apiv2statements)
- [Response body](#response-body)
- [Result metadata & partitions](#result-metadata--partitions)
- [Bindings](#bindings)
- [Session parameters](#session-parameters)
- [Multi-statement requests](#multi-statement-requests)
- [Cross-cutting notes](#cross-cutting-notes)

---

## Endpoints

- **`POST /api/v2/statements`** — Submit a statement. Query params: `requestId` (UUID, for idempotency), `retry` (`true` to dedupe against a prior `requestId`), `async` (`true` to return `202` immediately), `nullable` (default `true` — SQL NULLs come back as JSON `null`; set `false` to get the string `"null"` instead). Body: see below.
- **`GET /api/v2/statements/{handle}`** — Poll status / fetch results. Query params: `partition` (0-indexed int; omit for 0), `requestId`. Returns `200` with data, `202` still running, `422` failed, `404` handle unknown or expired.
- **`POST /api/v2/statements/{handle}/cancel`** — Cancel. Best-effort; returns `200` whether or not cancellation took. Query param: `requestId`.

That's the whole surface. Catalog browsing, warehouse management, user management, etc. are all done
through `SHOW`, `DESCRIBE`, `INFORMATION_SCHEMA`, and `ACCOUNT_USAGE` queries run via
`POST /api/v2/statements`.

## Request body (POST /api/v2/statements)

```json
{
  "statement": "SELECT ...",
  "timeout": 45,
  "database": "MY_DB",
  "schema": "PUBLIC",
  "warehouse": "MY_WH",
  "role": "ANALYST",
  "bindings": { "1": {"type": "TEXT", "value": "abc"} },
  "parameters": { "TIMEZONE": "UTC", "QUERY_TAG": "sql-api", "MULTI_STATEMENT_COUNT": "1" },
  "resultSetMetaData": { "format": "jsonv2" }
}
```

- **`statement`** (string) — Required. One SQL statement, or `;`-separated with `MULTI_STATEMENT_COUNT`.
- **`timeout`** (int (seconds)) — Max statement *execution* time — a statement that exceeds it is cancelled (`408`). Default is the account's `STATEMENT_TIMEOUT_IN_SECONDS`; `0` = the maximum (604800 s). Independent of the fixed ~45 s window the POST blocks before falling back to `202`.
- **`database`, `schema`, `warehouse`, `role`** (string) — Session context. Fall back to the user's defaults. Case-sensitive only if the object was created with a quoted lowercase name.
- **`bindings`** (object) — 1-indexed string-keyed map of `{type, value}`. See Bindings below.
- **`parameters`** (object) — Session parameters (all values are strings). See Session parameters below.
- **`resultSetMetaData.format`** (string) — Ignored by the `/api/v2/` endpoints — the response always reports `"jsonv2"`. Don't bother setting it.

## Response body

On `200` (or `202`):

```json
{
  "resultSetMetaData": {
    "numRows": 1234,
    "format": "jsonv2",
    "rowType": [
      {"name": "COL_A", "type": "fixed", "scale": 0, "precision": 38, "nullable": true, "length": null}
    ],
    "partitionInfo": [
      {"rowCount": 1000, "uncompressedSize": 524288},
      {"rowCount": 234,  "uncompressedSize": 122880}
    ]
  },
  "data": [ ["1", "foo"], ["2", "bar"] ],
  "code": "090001",
  "statementStatusUrl": "/api/v2/statements/01b2...?requestId=...",
  "requestId": "...",
  "sqlState": "00000",
  "statementHandle": "01b2abcd-0000-1234-0000-00000abc1234",
  "message": "Statement executed successfully.",
  "createdOn": 1716000000000
}
```

On `422` (failure) the same envelope appears but `data` is absent, `code`/`sqlState`/`message` carry
the error, and `resultSetMetaData` may be absent.

On `202` the body has `code: "333334"`, `statementStatusUrl`, `statementHandle`, and a `message`
like "Asynchronous execution in progress."

## Result metadata & partitions

`rowType[]` entries describe each column. `type` is one of:

`fixed` (DECIMAL/NUMBER/INT), `real` (FLOAT/DOUBLE), `text` (VARCHAR/STRING), `binary`, `boolean`,
`date`, `time`, `timestamp_ltz`, `timestamp_ntz`, `timestamp_tz`, `variant`, `object`, `array`,
`geography`, `geometry`, `vector`.

`data[]` cells are **always JSON strings** regardless of `type`, with these encodings:

- `fixed`/`real`: numeric string (`"42"`, `"3.14"`).
- `binary`: hex string.
- `boolean`: `"true"` / `"false"`.
- `date`: integer days since epoch as a string (`"18262"`).
- `time` / `timestamp_ltz` / `timestamp_ntz`: seconds since epoch (or midnight, for `time`) with 9
  decimal places (`"82919.000000000"`).
- `timestamp_tz`: same, followed by a space and an encoded timezone offset — subtract 1440 to get
  the offset in minutes (`"1616173619.000000000 1500"` → offset 60, i.e. `+0100`).
- `variant`/`object`/`array`: a JSON string you can parse with another `jq` pass.
- NULL: `null` (or the string `"null"` if you set `nullable=false`).

`partitionInfo[]` has one entry per result partition. Partition 0 is returned inline with the `200`;
fetch the rest via `?partition=N`. Partition responses after the first are gzip-compressed
(`Content-Encoding: gzip`) and contain only `data` — no metadata. Partitions are immutable and
independently fetchable for 24 hours.

## Bindings

1-indexed, string-keyed object. Values are always strings; `type` tells Snowflake how to coerce
them. Positional placeholders in the SQL are `?` — the bindings keys `"1"`, `"2"`, … map to the
first, second, … `?` in order. Named and `:1`-style numeric placeholders are not supported in the
SQL API, and bindings are not supported in multi-statement requests.

- **`FIXED`** (INTEGER/NUMBER) — decimal string
- **`REAL`** (FLOAT) — decimal string
- **`TEXT`** (VARCHAR) — raw string
- **`BINARY`** (BINARY) — hex-encoded string
- **`BOOLEAN`** (BOOLEAN) — `"true"` / `"false"`
- **`DATE`** (DATE) — milliseconds since epoch, as a string
- **`TIME`** / **`TIMESTAMP_LTZ`** / **`TIMESTAMP_NTZ`** — nanoseconds since epoch, as a string
- **`TIMESTAMP_TZ`** — `"<nanoseconds-since-epoch> <offset-minutes>"`

To bind a human-readable date/time literal, use type `TEXT` and let Snowflake auto-detect the
format.

Array bindings (`INSERT ... VALUES (?)` batched) set `"value"` to a JSON array of strings.

## Session parameters

Passed as string values in the `parameters` object. Commonly useful ones:

- **`MULTI_STATEMENT_COUNT`** (`"1"`) — Number of statements in the request. `"0"` = any.
- **`QUERY_TAG`** (`""`) — Free text attached to the query for auditing (`QUERY_HISTORY.QUERY_TAG`).
- **`TIMEZONE`** (account default) — Session timezone for `TIMESTAMP_LTZ` / `CURRENT_TIMESTAMP`.
- **`STATEMENT_TIMEOUT_IN_SECONDS`** (account default) — Server-side hard cap on statement runtime.
- **`BINARY_OUTPUT_FORMAT`** (`HEX`) — `HEX` or `BASE64` for binary columns.
- **`DATE_OUTPUT_FORMAT` / `TIME_OUTPUT_FORMAT` / `TIMESTAMP_*_OUTPUT_FORMAT`** (account default) — Only affects cast-to-string, not the raw `data[]` encoding.
- **`USE_CACHED_RESULT`** (`"true"`) — Set `"false"` to bypass the result cache.

## Multi-statement requests

Set `MULTI_STATEMENT_COUNT` to the count (or `"0"` for any). The `200`/`202` returns a **parent**
`statementHandle` plus a `statementHandles[]` array of child handles. Poll / fetch each child
separately. The parent handle's `GET` returns per-child status but no data.

```json
{
  "statementHandle": "01b2...",
  "statementHandles": ["01b2-child1", "01b2-child2"]
}
```

DDL + DML + SELECT can be mixed. Temp tables created in statement 1 are visible in statement 2.
`BEGIN` / `COMMIT` / `ROLLBACK`, `USE`, `ALTER SESSION`, session-variable assignment, and temporary
table/stage creation are *only* supported inside a multi-statement request.

## Cross-cutting notes

**Statement handle lifetime.** Results are retained for 24 hours. After that, `GET` returns `404`
and the only way to reproduce the result is to re-run the SQL.

**Idempotency.** POSTs are not idempotent by default. Use `requestId` on the first attempt and
`requestId` + `retry=true` on retries — Snowflake dedupes against the request ID for 24 hours.

**Case sensitivity.** Unquoted identifiers are uppercased. `"my_table"` (quoted, lowercase) is a
different object from `my_table` / `MY_TABLE`. If a table "doesn't exist," check quoting first.

**Warehouse billing.** Per-second while a warehouse is running, with a 60-second minimum each time
the warehouse starts or resumes (auto-resume from suspended counts). Queries on an already-running
warehouse do not each incur a 60-second minimum. A suspended warehouse auto-resumes on the first
query and auto-suspends after idle. Prefer `XSMALL` for metadata / small scans.

**`422` ≠ "bad request."** Snowflake uses `422 Unprocessable Entity` for *SQL-level* failures
(syntax error, object not found, permission denied on a table) — the HTTP request was well-formed
but the statement failed. Read `message` and `sqlState`, don't retry blindly.

**Result cache.** Identical queries from the same role hit the result cache for free (no warehouse
time). `USE_CACHED_RESULT=false` disables this when you need fresh data.

**Unsupported statements.** `PUT` and `GET` (stage file transfer) do not work through the SQL API —
use a driver for those. Some stored procedures that return Arrow-format result sets also fail.
