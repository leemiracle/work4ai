---
name: redshift-api
description: Run SQL against Amazon Redshift — submit statements, poll status, page through results, and browse databases/schemas/tables. Use this whenever the user wants to query Redshift (provisioned cluster or Serverless), ask "what tables are in this schema", check a query's status, or mentions `redshift-data`, a Redshift cluster identifier / workgroup name, or a `redshift-data.{region}.amazonaws.com` endpoint. Always start from this skill when interacting with this service — its bundled scripts and recipes are the fastest path.
---

In the Amazon Redshift Data API, every call is a `POST` to `https://redshift-data.<region>.amazonaws.com/` with
`Content-Type: application/x-amz-json-1.1` and `X-Amz-Target: RedshiftData.<Action>` — there are no
REST-style paths. The API is fully asynchronous: submit a statement, get back an `Id`, poll
`DescribeStatement` until done, then page results with `GetStatementResult` —
`scripts/rs_query.sh` (operation 1) drives that loop for you. The same calls work against
provisioned clusters and Serverless; only the connection-target field differs.

## Request setup

Authentication is handled by the runtime — requests to this API are signed with credentials
configured for the workspace, so there is nothing to set up. Do not try to obtain AWS keys or sign
requests yourself. A persistent `AccessDeniedException` means the credential isn't configured for
this workspace — report that instead of debugging auth.

Two pieces of configuration are real and required:

**1. Region** — it's part of the endpoint hostname:

```bash
export AWS_DEFAULT_REGION="us-east-1"        # the region your cluster / workgroup is in
```

**2. Connection target** — which cluster/workgroup and database the Data API connects to. Pick one
and put the matching JSON fields in `RS_TARGET`; the recipes below merge it into each request body:

- **Serverless** — pass `WorkgroupName`. The configured identity is mapped to a database user.
  Simplest.
- **Provisioned, temporary credentials** — pass `ClusterIdentifier` and `DbUser`. The Data API
  resolves database credentials under the hood.
- **Provisioned or Serverless, Secrets Manager** — pass `SecretArn` pointing to a secret that holds
  the database login.

Set whichever applies once:

```bash
export RS_DATABASE="dev"
# Serverless:
export RS_TARGET='{"WorkgroupName": "my-workgroup"}'
# — or provisioned + temp creds:
# export RS_TARGET='{"ClusterIdentifier": "my-cluster", "DbUser": "my_user"}'
# — or either + Secrets Manager:
# export RS_TARGET='{"ClusterIdentifier": "my-cluster", "SecretArn": "arn:aws:secretsmanager:us-east-1:123456789012:secret:rs-creds-AbCdEf"}'
```

**The helper used below.** One function wraps the endpoint, the headers, and the action name. The
`Authorization` header is a placeholder — the runtime replaces it with a real signature.

```bash
rsapi() {
  local action="$1"
  curl -sS "https://redshift-data.${AWS_DEFAULT_REGION}.amazonaws.com/" \
    -H "Content-Type: application/x-amz-json-1.1" \
    -H "X-Amz-Target: RedshiftData.${action}" \
    -H "Authorization: placeholder" \
    -d "${2:?rsapi needs a JSON body as the second argument}"
}
```

**Sanity check** — list databases. A `200` with a `Databases` array confirms the workspace is wired
up and the connection target is right. An error names which layer failed.

```bash
rsapi ListDatabases "$(jq -n --argjson t "$RS_TARGET" --arg db "$RS_DATABASE" \
  '$t + {Database: $db}')" | jq .
```

## Core operations

Every action that connects to the database takes the same merged target body —
`$t + {Database: $db, ...}`. Errors come back as `{"__type": "<Exception>", "message": "..."}`
instead of the expected shape; on any call, an absent top-level field (`Id`, `Status`, `Records`, …)
means you got the error envelope — print it and stop.

### 1. Run a query (`scripts/rs_query.sh`)

Run SQL through the bundled script (path is relative to this skill's directory): it submits with
`ExecuteStatement`, polls `DescribeStatement` to a terminal state, pages `GetStatementResult` on
`NextToken`, and decodes the typed one-key cell objects.

```bash
scripts/rs_query.sh \
  'SELECT event_name, COUNT(*) AS n FROM public.events
   WHERE event_date >= :start GROUP BY 1 ORDER BY 2 DESC LIMIT 20' \
  --param start=2024-01-01 --name top-events
```

- SQL is one argument (or stdin). Instance specifics come from `AWS_DEFAULT_REGION` / `RS_TARGET` /
  `RS_DATABASE` above; `--database` overrides the database.
- `--param NAME=VALUE` (repeatable) binds `:NAME` placeholders — values are always strings; the
  database casts them. `--name` sets `StatementName` so the query shows up in `ListStatements`.
- `--max-rows N` caps fetched rows (default 10000, `0` = everything); `--json` emits one JSON object
  per row instead of TSV with a header. Statement id, status, duration, and row counts go to stderr.
- Exit codes: `0` success, `1` submit failed or SQL `FAILED`/`ABORTED` (the API's own message on
  stderr), `2` gave up waiting after `--max-wait` seconds (default 600) — the statement id is on
  stderr; resume it with operation 2.

If the script errors, read it — it's plain `curl` + `jq` — and debug against `references/api.md`.
For `BatchExecuteStatement` and sub-statement results, session reuse (`SessionKeepAliveSeconds` /
`SessionId`), `ResultFormat: CSV`, cancelling, or catalog browsing, use the actions below.

### 2. Resume a statement by id (`DescribeStatement` → `GetStatementResult`)

When the script exits 2 (timeout) or you have a statement id from elsewhere, poll and fetch
directly:

```bash
rsapi DescribeStatement "$(jq -n --arg id "$ID" '{Id: $id}')" \
  | jq '{Status, Duration, ResultRows, HasResultSet, Error}'
rsapi GetStatementResult "$(jq -n --arg id "$ID" '{Id: $id}')" \
  | jq -r '.Records[]? | [.[] | if .isNull then null else to_entries[0].value end] | @tsv'
```

- `Status` ∈ `SUBMITTED`, `PICKED`, `STARTED`, `FINISHED`, `FAILED`, `ABORTED`. Only `FINISHED`
  with `HasResultSet: true` has rows; `FAILED` carries the SQL error in `.Error`. `Duration` is
  **nanoseconds**.
- Result cells are typed one-key objects (see the gotcha under Error handling); column names/types
  are in `.ColumnMetadata` on the first page. Further pages follow `NextToken` — no page-size knob;
  `DescribeStatement.ResultRows` is the total up front.

### 3. Cancel a running statement (`CancelStatement`)

```bash
rsapi CancelStatement "$(jq -n --arg id "$ID" '{Id: $id}')" | jq .
# {"Status": true} on success — best-effort, check DescribeStatement to confirm.
```

### 4. Run multiple statements in one call (`BatchExecuteStatement`)

All statements run in one transaction — all commit or all roll back.

```bash
rsapi BatchExecuteStatement "$(jq -n --argjson t "$RS_TARGET" --arg db "$RS_DATABASE" '$t + {
    Database: $db,
    Sqls: ["CREATE TEMP TABLE tmp AS SELECT 1 AS x", "SELECT * FROM tmp"]
  }')" | jq '{Id}'
```

`DescribeStatement` on the parent `Id` returns a `SubStatements[]` array. Each sub-statement has its
own `Id` (the parent ID with a `:1`, `:2`, … suffix), `Status`, and `HasResultSet` — fetch each
sub-statement's results with its own `GetStatementResult` call.

### 5. List recent statements (`ListStatements`)

```bash
rsapi ListStatements '{"MaxResults": 20, "Status": "ALL"}' \
  | jq '.Statements[] | {Id, StatementName, Status, QueryString: (.QueryString[0:80]), CreatedAt}'
```

`Status` filter: `SUBMITTED`, `PICKED`, `STARTED`, `FINISHED`, `FAILED`, `ABORTED`, `ALL` — **only
finished statements are listed if you omit it**. `MaxResults` 0–100. `RoleLevel` defaults to `true`
(includes statements from anyone assuming the same IAM role); set `false` to see only this session's.

### 6. Browse the catalog (`ListDatabases` / `ListSchemas` / `ListTables` / `DescribeTable`)

All four take the merged target body. Patterns use SQL `LIKE` wildcards (`%`, `_`).

- **`ListDatabases`** — `Databases[]` (strings)
- **`ListSchemas`** — `SchemaPattern` (optional) — `Schemas[]` (strings)
- **`ListTables`** — `SchemaPattern`, `TablePattern` — `Tables[] {schema, name, type}` — `type` ∈ `TABLE`/`VIEW`/`SYSTEM TABLE`/`GLOBAL TEMPORARY`/`LOCAL TEMPORARY`/`ALIAS`/`SYNONYM`
- **`DescribeTable`** — `Schema`, `Table` — `ColumnList[] {name, typeName, nullable, length, precision}`

```bash
rsapi ListTables "$(jq -n --argjson t "$RS_TARGET" --arg db "$RS_DATABASE" \
  '$t + {Database: $db, SchemaPattern: "public", TablePattern: "ev%"}')" | jq '.Tables'
```

JSON field names are PascalCase (`WorkgroupName`, not `workgroup-name`). All four are paginated
(`NextToken`). See `references/api.md` for every action's body shape.

## Pagination

`GetStatementResult`, `ListStatements`, `ListDatabases`, `ListSchemas`, `ListTables`, and
`DescribeTable` all use the same scheme: the response carries `NextToken` when there's more; pass it
back as `NextToken` in the next request body. Stop when it's absent.

## Rate limits

- **Active statements** — up to 500 active (`SUBMITTED`/`STARTED`) per cluster or workgroup. Excess
  submits fail with `ActiveStatementsExceededException`.
- **Result size** — 500 MB per statement (after gzip) and 64 KB per row. Larger results fail; add a
  `LIMIT` or use `UNLOAD ... TO 's3://...'`.
- **Result retention** — 24 hours; after that `GetStatementResult` returns
  `ResourceNotFoundException`.
- **Statement duration** — 24 hours max. **Query string** — 100 KB max.
- **API rate** — fixed, non-adjustable TPS quotas per account/region: `DescribeStatement` 100,
  `ExecuteStatement` 30, `GetStatementResult` 20, `BatchExecuteStatement` 20, and only **3 TPS** for
  `CancelStatement`, `ListStatements`, `ListDatabases`, `ListSchemas`, `ListTables`, `DescribeTable`.
  Exceeding one returns `ThrottlingException` (HTTP 400) — back off and don't poll in a hot loop.

## Error handling

Errors return as `{"__type": "<Exception>", "message": "..."}` (HTTP 400/403/500). The `__type`
field is the discriminator.

- **`ValidationException` (400)** — Bad parameters. Common: passing both `ClusterIdentifier` and `WorkgroupName`, or neither; missing `Database`; wrong field casing.
- **`ActiveStatementsExceededException` (400)** — Too many in flight. `ListStatements` `{"Status":"STARTED"}` shows what's running.
- **`ActiveSessionsExceededException` (400)** — >500 open sessions. Stop passing `SessionKeepAliveSeconds` or wait for idle ones to expire.
- **`ExecuteStatementException` (500)** — Submission failed before the DB saw it — wrong cluster/workgroup name, unreachable cluster, bad `DbUser`. Check `RS_TARGET`.
- **`ResourceNotFoundException` (400)** — Statement ID unknown or > 24 h old.
- **`BatchExecuteStatementException` (500)** — One statement in the batch failed; whole transaction rolled back. Check `SubStatements[].Error`.
- **`DatabaseConnectionException` / `QueryTimeoutException`** — A catalog call couldn't reach the database or timed out. Check the target is up; retry.
- **`AccessDeniedException` (403)** — Credential needs `redshift-data:*` on the cluster/workgroup ARN plus, depending on connection mode, `redshift:GetClusterCredentials` / `redshift-serverless:GetCredentials` / `secretsmanager:GetSecretValue`. Report which is missing.
- **`InternalServerException` (500)** — `ExecuteStatement` is **not idempotent** unless you pass a `ClientToken` — check `ListStatements` before retrying a write.
- **`Status: FAILED` on `DescribeStatement`** — SQL failed after submission. Read `.Error` for the SQL message.

Two gotchas:

- **`ExecuteStatement` returning 200 ≠ the query succeeded.** SQL errors only surface later as
  `Status: FAILED` on `DescribeStatement`. Always poll before fetching results.
- **Cell values are typed one-key objects**, not bare values. `longValue` is a JSON number,
  `isNull: true` is a distinct shape. A naive `.value` read returns nothing, and chaining jq `//`
  across the typed keys breaks on `false`/`0`. Use `to_entries[0].value`.

## Going deeper

`references/api.md` has the complete catalog — every action's request/response shape in PascalCase
for raw HTTP, the `SqlParameter` binding format, the `ColumnMetadata` fields, `SubStatementData` for
batches, session reuse (`SessionKeepAliveSeconds` / `SessionId`), and the quota table. Read it when
you need an action not covered above or the exact raw-HTTP body shape.
