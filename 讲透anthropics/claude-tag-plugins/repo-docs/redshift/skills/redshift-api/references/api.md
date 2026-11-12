# Amazon Redshift Data API — Action Reference

Endpoint: `https://redshift-data.${AWS_DEFAULT_REGION}.amazonaws.com/`. All calls are `POST /` with:

```
Content-Type: application/x-amz-json-1.1
X-Amz-Target: RedshiftData.<Action>
Authorization: placeholder    # the runtime replaces this with a real AWS request signature
```

(For reference: the AWS CLI's `aws redshift-data <action>` wraps these same shapes with kebab-case
flags, but it is not available in this runtime — use the raw HTTP form shown here.) Official docs:
`https://docs.aws.amazon.com/redshift-data/latest/APIReference/`.

## Table of contents

- [Connection fields](#connection-fields)
- [ExecuteStatement](#executestatement)
- [BatchExecuteStatement](#batchexecutestatement)
- [DescribeStatement](#describestatement)
- [GetStatementResult](#getstatementresult)
- [CancelStatement](#cancelstatement)
- [ListStatements](#liststatements)
- [ListDatabases / ListSchemas / ListTables / DescribeTable](#catalog-actions)
- [SqlParameter](#sqlparameter)
- [ColumnMetadata](#columnmetadata)
- [Field typing in results](#field-typing-in-results)
- [Sessions](#sessions)
- [Quotas](#quotas)
- [IAM permissions](#iam-permissions)

---

## Connection fields

Every action that connects to the database accepts exactly **one** target and one auth method:

- **`ClusterIdentifier`** (`--cluster-identifier`) — Provisioned cluster. Pair with `DbUser` or `SecretArn`.
- **`WorkgroupName`** (`--workgroup-name`) — Serverless. Auth is IAM; optionally pair with `SecretArn`.
- **`DbUser`** (`--db-user`) — Temp credentials via `GetClusterCredentials`. Provisioned only.
- **`SecretArn`** (`--secret-arn`) — Secrets Manager secret with `{username,password}`. Either target.
- **`Database`** (`--database`) — Required. The database to connect through.

Passing both `ClusterIdentifier` and `WorkgroupName`, or a `DbUser` with a `WorkgroupName`, returns
`ValidationException`.

## ExecuteStatement

Request:

```json
{
  "ClusterIdentifier": "my-cluster", "Database": "dev", "DbUser": "me",
  "Sql": "SELECT * FROM t WHERE id = :id",
  "Parameters": [{"name": "id", "value": "42"}],
  "StatementName": "lookup-t",
  "WithEvent": false,
  "ClientToken": "c2f0...-idempotency-uuid",
  "ResultFormat": "JSON",
  "SessionId": "optional-existing-session",
  "SessionKeepAliveSeconds": 300
}
```

Response:
`{"Id": "...", "ClusterIdentifier", "WorkgroupName", "Database", "DbUser", "DbGroups", "CreatedAt", "SecretArn", "SessionId"}`
(`ClusterIdentifier` for provisioned, `WorkgroupName` for Serverless — only the one you connected
with is returned).

- `WithEvent: true` publishes an EventBridge event when the statement finishes.
- `ClientToken` is an idempotency key (1–64 chars) — a retry with the same token within 8 hours
  returns the original `Id` instead of running twice.
- `ResultFormat`: `JSON` (default) or `CSV`. CSV results are fetched with `GetStatementResultV2`.
- `SessionKeepAliveSeconds` (0–86400) opens a reusable session; pass the returned `SessionId` on
  later calls to run in the same session (reuses temp tables, `SET` state, etc.).
- `StatementName` max length is 500.

## BatchExecuteStatement

Same connection fields plus:

```json
{"Sqls": ["CREATE TEMP TABLE tmp AS SELECT 1", "SELECT * FROM tmp"], "StatementName": "batch"}
```

Runs up to 40 statements as a single transaction. Response is the same `{"Id": "..."}`. The parent
`Id` in `DescribeStatement` returns a `SubStatements[]` array; each sub-statement has its own `Id`
for `GetStatementResult` (the sub-statement IDs are the parent ID with a `:1`, `:2`, ... suffix).

`Parameters` is accepted on batch too: one array shared by every statement in the batch. Each
statement can use a subset, but every parameter must be referenced by at least one statement.

## DescribeStatement

Request: `{"Id": "..."}`.

Response:

```json
{
  "Id": "...", "Status": "FINISHED", "ClusterIdentifier": "...", "Database": "dev",
  "CreatedAt": 1716000000.0, "UpdatedAt": 1716000005.0,
  "Duration": 3141592653, "ResultRows": 1234, "ResultSize": 65536,
  "HasResultSet": true, "RedshiftPid": 12345, "RedshiftQueryId": 678,
  "QueryString": "SELECT ...", "QueryParameters": [...],
  "Error": "", "SubStatements": [{"Id": "...", "Status": "FINISHED", "HasResultSet": true, ...}],
  "SessionId": "..."
}
```

- `Status`: `SUBMITTED` → `PICKED` → `STARTED` → one of `FINISHED` / `FAILED` / `ABORTED`.
- `Duration` is **nanoseconds**.
- `ResultRows` is `-1` until the statement finishes.
- `HasResultSet: false` for DDL/DML (INSERT, UPDATE, CREATE, etc.) — nothing to fetch.
- `Error` is empty on success; carries the SQL error message on `FAILED`.
- `RedshiftQueryId` cross-references `SYS_QUERY_HISTORY` / `STL_QUERY` for query tuning.

## GetStatementResult

Request: `{"Id": "...", "NextToken": "..."}`.

Response:

```json
{
  "ColumnMetadata": [{"name": "id", "typeName": "int8", "nullable": 0, ...}],
  "Records": [
    [{"longValue": 42}, {"stringValue": "foo"}, {"isNull": true}]
  ],
  "TotalNumRows": 1234,
  "NextToken": "..."
}
```

For sub-statements of a batch, pass the **sub-statement's** `Id`.

`GetStatementResultV2` takes the same request and is required when the statement was submitted with
`ResultFormat: "CSV"`. Its `Records` is an array of `{"CSVRecords": "<csv text>"}` chunks (~1 MB
each, up to 15 MB per page; `NextToken` pages the rest), plus a top-level `"ResultFormat": "CSV"`.

## CancelStatement

Request: `{"Id": "..."}`. Response: `{"Status": true}`. Best-effort; does not guarantee the query
stopped. Verify with `DescribeStatement`.

## ListStatements

Request:

```json
{"StatementName": "prefix", "Status": "FINISHED", "RoleLevel": true, "MaxResults": 50, "NextToken": "...", "Database": "dev", "ClusterIdentifier": "..."}
```

- `StatementName` matches by **prefix** (case-sensitive).
- `Status`: `SUBMITTED`, `PICKED`, `STARTED`, `FINISHED`, `FAILED`, `ABORTED`, `ALL`. Omitted → only
  finished statements are returned.
- `RoleLevel` defaults to `true` (statements run by any session assuming the same IAM role); `false`
  restricts to the current IAM session.
- `MaxResults`: 0–100.
- Response:
  `{"Statements": [{"Id", "QueryString", "QueryStrings", "Status", "StatementName", "CreatedAt", "UpdatedAt", "QueryParameters", "IsBatchStatement", "SessionId", "SecretArn", "ResultFormat"}], "NextToken"}`.

## Catalog actions

All take the connection fields plus pagination (`MaxResults`, `NextToken`):

- **`ListDatabases`** — `{"Databases": ["dev", "prod", ...]}`
- **`ListSchemas`** — `SchemaPattern`, `ConnectedDatabase` — `{"Schemas": ["public", ...]}`
- **`ListTables`** — `SchemaPattern`, `TablePattern`, `ConnectedDatabase` — `{"Tables": [{"name", "schema", "type"}]}`
- **`DescribeTable`** — `Schema`, `Table`, `ConnectedDatabase` — `{"TableName", "ColumnList": [ColumnMetadata...]}`

Patterns use SQL `LIKE` wildcards (`%`, `_`). `ConnectedDatabase` lets you browse a different
database than the one you connect through (cross-database queries). `DescribeTable` is paginated — a
table with many columns can span pages.

## SqlParameter

`Parameters` is an array of `{"name": "x", "value": "..."}`. The SQL references them as `:x`. All
values are **strings**; Redshift casts them to the column's type. NULL cannot be passed as a
parameter — use a literal `NULL` in the SQL.

```json
"Parameters": [
  {"name": "start", "value": "2024-01-01"},
  {"name": "limit", "value": "100"}
]
```

Parameter names are case-sensitive and must match `[0-9a-zA-Z_]+`.

## ColumnMetadata

```json
{
  "name": "id", "label": "id", "typeName": "int8",
  "nullable": 0, "precision": 19, "scale": 0, "length": 0,
  "columnDefault": null, "isCaseSensitive": false, "isCurrency": false,
  "isSigned": true, "schemaName": "public", "tableName": "events"
}
```

`typeName` is the Redshift/Postgres type name: `int2`/`int4`/`int8`, `float4`/`float8`, `numeric`,
`varchar`/`bpchar`/`text`, `bool`, `date`, `time`/`timetz`, `timestamp`/`timestamptz`, `super`,
`geometry`, `hllsketch`, `varbyte`. `nullable` is `0` (NOT NULL) or `1`.

## Field typing in results

Each cell in `Records[]` is a single-key object whose key tells you the JSON type:

- **`stringValue`** (string) — varchar, char, text, date, timestamp, numeric, super
- **`longValue`** (number (int)) — int2, int4, int8
- **`doubleValue`** (number (float)) — float4, float8
- **`booleanValue`** (boolean) — bool
- **`blobValue`** (string (base64)) — varbyte
- **`isNull`** (`true`) — any NULL

Timestamps come back as `stringValue` in `YYYY-MM-DD HH:MM:SS[.ffffff]` form (no `T`, no zone for
`timestamp`; with offset for `timestamptz`). `super` (semi-structured) comes back as a JSON string
in `stringValue`.

## Sessions

Pass `SessionKeepAliveSeconds` on `ExecuteStatement` / `BatchExecuteStatement` to open a reusable
session. The response carries a `SessionId`. Later calls that pass the same `SessionId` reuse the
connection — temp tables, `SET search_path`, `SET statement_timeout`, etc. persist. When you pass
`SessionId`, you may omit the connection fields (they're implied).

Sessions time out after `SessionKeepAliveSeconds` of inactivity (max 24 h, and a hard 24 h lifetime
after which in-progress queries are killed). A session runs one query at a time — wait for the
previous statement to finish before submitting the next with the same `SessionId`. Up to 500
sessions per cluster/workgroup; exceeding that returns `ActiveSessionsExceededException`. There's no
explicit close — just stop using it.

## Quotas

- **Active statements (`SUBMITTED`/`STARTED`)** — 500 per cluster / workgroup
- **Query string size** — 100 KB
- **Result size** — 500 MB after gzip compression (use `LIMIT` or `UNLOAD` to S3 for larger)
- **Result row size** — 64 KB
- **Result retention** — 24 hours
- **Statement duration** — 24 hours
- **Statements per `BatchExecuteStatement`** — 40
- **`ClientToken` idempotency window** — 8 hours
- **Sessions** — 500 per cluster / workgroup, 24 h max lifetime, one query at a time
- **API rate (TPS, non-adjustable)** — `DescribeStatement` 100 · `ExecuteStatement` 30 · `GetStatementResult` 20 · `BatchExecuteStatement` 20 · all other actions 3

## IAM permissions

The calling identity needs, depending on setup:

- `redshift-data:ExecuteStatement`, `:DescribeStatement`, `:GetStatementResult`, `:CancelStatement`,
  `:ListStatements`, `:ListDatabases`, `:ListSchemas`, `:ListTables`, `:DescribeTable`,
  `:BatchExecuteStatement` — on the cluster or workgroup ARN.
- **Provisioned + `DbUser`:** `redshift:GetClusterCredentials` (or `GetClusterCredentialsWithIAM`)
  on `dbuser:<region>:<account>:<cluster>/<dbuser>` and `dbname:.../<database>`.
- **Serverless:** `redshift-serverless:GetCredentials` on the workgroup ARN.
- **Secrets Manager:** `secretsmanager:GetSecretValue` on the secret ARN.

A `ValidationException` about credentials usually means the `redshift-data:*` permission is present
but the credential-retrieval permission isn't.
