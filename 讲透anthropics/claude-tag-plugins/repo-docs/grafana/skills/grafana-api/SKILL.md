---
name: grafana-api
description: Work with a Grafana instance — search and read dashboards, run datasource queries (Prometheus, Loki, PostgreSQL, etc.), inspect alert rules and silences, post annotations, and manage folders. Use this whenever the user mentions a Grafana dashboard, panel, or alert; pastes a Grafana URL; asks "what does this dashboard show", "query this metric in Grafana", "is this alert firing", "silence this alert", or wants to create/export a dashboard — even if they don't say "API". Always start from this skill when interacting with this service — its bundled scripts and recipes are the fastest path.
---

Grafana's base URL is the instance: Grafana Cloud at `https://<your-org>.grafana.net`, or self-hosted at
wherever the org runs it (e.g. `https://grafana.example.com`). The API surface is the same; only the
base URL differs.

**Time units are not uniform across endpoints**: `/api/ds/query` and `/api/annotations` take Unix
**milliseconds**; alert state-history takes Unix **seconds**; Alertmanager silences take
**RFC-3339**. Mixing them returns empty results, not errors.

## Request setup

Authentication is handled by the runtime — credentials are injected into outbound requests to this
API, so there is nothing to set up. Do not try to create, mint, refresh, or validate tokens or keys.
Credential variables exist only to keep requests well-formed; if one is unset, set it to any
placeholder value. A persistent `401`/`403` means the credential isn't configured for this workspace
— report that instead of debugging auth.

The instance URL must be real — it's part of every request path:

```bash
export GRAFANA_URL="https://grafana.example.com"   # no trailing slash
export GRAFANA_TOKEN="placeholder"                 # injected by the runtime; any value works
```

Every request:

```bash
curl -sS "${GRAFANA_URL}/api/..." -H "Authorization: Bearer ${GRAFANA_TOKEN}"
```

**Sanity check** — confirm the URL is right and the workspace is wired up:

```bash
curl -sS -w '\nHTTP %{http_code}\n' "${GRAFANA_URL}/api/user" -H "Authorization: Bearer ${GRAFANA_TOKEN}"
# 200 → the current user/service account. 401 → {"message":"Unauthorized"} — report it, don't debug auth.
# Service accounts also work: /api/org returns the current org.
```

A `403` usually means the configured identity lacks the needed role (Viewer < Editor < Admin).
Datasource queries and dashboard reads only need Viewer.

Helper used below (optional):

```bash
grafana() { curl -sS "$@" -H "Authorization: Bearer ${GRAFANA_TOKEN}"; }
```

## Core operations

### 1. Search dashboards and folders

```bash
grafana "${GRAFANA_URL}/api/search" -G \
  --data-urlencode "query=api latency" \
  --data-urlencode "type=dash-db" \
  --data-urlencode "limit=50" | jq '.[] | {uid, title, folderTitle, url}'
```

`type` is `dash-db` (dashboards) or `dash-folder` (folders); omit it for both. Also: `tag=`,
`folderUIDs=`, `starred=true`.

### 2. Get a dashboard by UID

The UID is the short string in the dashboard URL: `.../d/<uid>/<slug>`.

```bash
grafana "${GRAFANA_URL}/api/dashboards/uid/abc123xy" | \
  jq '{title: .dashboard.title, folder: .meta.folderTitle, panels: [.dashboard.panels[]? | {id, title, type}]}'
```

Each panel's PromQL/LogQL/SQL is under `.dashboard.panels[].targets`. A bad UID returns
`{"message":"Dashboard not found"}` (404).

### 3. Run a datasource query

This is how you ask the same questions a panel asks. First find the datasource UID:

```bash
grafana "${GRAFANA_URL}/api/datasources" | jq '.[] | {uid, name, type}'
```

Then POST to `/api/ds/query`. The `queries[]` shape depends on the datasource `type`; this is a
Prometheus example:

```bash
NOW_MS=$(( $(date +%s) * 1000 )); FROM_MS=$(( NOW_MS - 3600000 ))
grafana -X POST "${GRAFANA_URL}/api/ds/query" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "'"${FROM_MS}"'",
    "to": "'"${NOW_MS}"'",
    "queries": [{
      "refId": "A",
      "datasource": {"uid": "<datasource_uid>"},
      "expr": "sum(rate(http_requests_total{job=\"api\"}[5m])) by (status)",
      "intervalMs": 30000,
      "maxDataPoints": 500
    }]
  }' | jq '.results.A.error // .results.A.frames[0].data.values'
```

For Loki, use `"expr": "{job=\"api\"} |= \"error\""` and optionally `"queryType": "range"`. For SQL
datasources, use `"rawSql": "SELECT ..."` and `"format": "table"`.

Responses are Grafana **data frames**: `results.<refId>.frames[]` with parallel column arrays in
`data.values` and column metadata in `schema.fields`. **On a datasource-side failure `frames` is
empty and the error from Prometheus/Loki/SQL is embedded in `results.<refId>.error`** — the HTTP
status may still be 200 or 500, so check that field rather than relying on status alone.

### 4. List alert rules

Two surfaces with different jobs:

```bash
# live STATE (firing/pending/inactive) — read-only
grafana "${GRAFANA_URL}/api/prometheus/grafana/api/v1/rules" | \
  jq '.data.groups[]? | {folder: .file, group: .name, rules: [.rules[] | {name, state, health}]}'

# DEFINITIONS (query, condition, labels, for-duration) — full CRUD, no runtime state
grafana "${GRAFANA_URL}/api/v1/provisioning/alert-rules" | jq '.[] | {uid, title, folderUID, condition}'
```

The `grafana` segment in the first path is the literal `{am_name}` for the built-in Alertmanager;
external Alertmanagers use their datasource UID. Resources written via the provisioning API are
locked in the UI unless you send `X-Disable-Provenance: true` on the write.

### 5. Silences

`startsAt`/`endsAt` are RFC-3339 (`date -u +%Y-%m-%dT%H:%M:%SZ`).

```bash
# active silences
grafana "${GRAFANA_URL}/api/alertmanager/grafana/api/v2/silences" | \
  jq '.[] | select(.status.state=="active") | {id, comment, matchers, endsAt}'

# create a 2-hour silence matching a label
# GNU date; on BSD/macOS use: date -u -v+2H +%Y-%m-%dT%H:%M:%SZ
START=$(date -u +%Y-%m-%dT%H:%M:%SZ)
END=$(date -u -d "+2 hours" +%Y-%m-%dT%H:%M:%SZ)
grafana -X POST "${GRAFANA_URL}/api/alertmanager/grafana/api/v2/silences" \
  -H "Content-Type: application/json" \
  -d '{
    "matchers": [{"name": "alertname", "value": "HighErrorRate", "isRegex": false, "isEqual": true}],
    "startsAt": "'"${START}"'", "endsAt": "'"${END}"'",
    "createdBy": "api", "comment": "investigating"
  }'
# success → {"silenceID": "..."}

# expire a silence
grafana -X DELETE "${GRAFANA_URL}/api/alertmanager/grafana/api/v2/silence/<silence_id>"
```

### 6. Annotations

`time`/`timeEnd` are Unix milliseconds.

```bash
grafana -X POST "${GRAFANA_URL}/api/annotations" -H "Content-Type: application/json" \
  -d '{"time": '"$(( $(date +%s) * 1000 ))"', "tags": ["deploy","api"], "text": "Deployed v2.3.1"}'

grafana "${GRAFANA_URL}/api/annotations?from=${FROM_MS}&to=${NOW_MS}&tags=deploy" | jq .
```

### 7. Folders

```bash
grafana "${GRAFANA_URL}/api/folders" | jq '.[] | {uid, title}'
grafana -X POST "${GRAFANA_URL}/api/folders" -H "Content-Type: application/json" -d '{"title": "Team API"}'
```

### 8. Create or update a dashboard

```bash
grafana -X POST "${GRAFANA_URL}/api/dashboards/db" \
  -H "Content-Type: application/json" \
  -d '{
    "dashboard": {"uid": null, "title": "My Dashboard", "panels": [], "schemaVersion": 41},
    "folderUid": "<folder_uid>",
    "overwrite": false,
    "message": "created via API"
  }'
```

To **update**: `GET` the dashboard first and send the **whole JSON back** with your change applied —
this endpoint replaces the dashboard. Set `dashboard.uid` to the existing UID and either include the
current `dashboard.version` (Grafana returns `412` on mismatch) or set `overwrite: true`.

## Pagination

`/api/search` and `/api/folders` use `limit` + `page` query params (1-indexed). `/api/search`
defaults to 1000 and caps at 5000. `/api/annotations` has `limit` (default 100) but no `page` —
narrow the `from`/`to` window instead. Alertmanager endpoints are not paginated. When you hit a cap,
narrow with `query=`, `tag=`, or `folderUIDs=` instead of paging through everything.

## Rate limits

Self-hosted Grafana has no built-in per-token rate limits by default. Grafana Cloud may return
`429` on heavy API or query traffic — limits vary by plan and endpoint, so honor `Retry-After`
if present, otherwise back off.
**`/api/ds/query` is the expensive path**: each call fans out to the underlying database, so batch
multiple `queries[]` into one request instead of looping.

## Error handling

Error bodies always carry `"message"` (sometimes `"messageId"`/`"traceID"`). Service-specific cases:

- **`412`** — Version conflict on dashboard save. `GET` the latest, reapply your change, include `version`, or set `overwrite: true`.
- **`200`/`500` on `/api/ds/query`** — Datasource-side failure. The Prometheus/Loki/SQL error is embedded in `results.<refId>.error`; `frames` is empty.
- **`403`** — Insufficient role. Viewer < Editor < Admin; folder-level permissions also apply.

`401` → credential not configured for this workspace (report, don't debug). UIDs are case-sensitive
short strings, not titles.

## Going deeper

`references/api.md` has the full endpoint catalog — dashboards, folders, datasources, ds/query
per-datasource shapes, the full unified-alerting surface (alert rules, contact points, notification
policies, mute timings, Alertmanager), annotations, snapshots, orgs/users/teams, service accounts,
and short URLs. Read it when you need an endpoint beyond the ones above.
