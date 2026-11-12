# Grafana HTTP API — Endpoint Reference

All requests go to `${GRAFANA_URL}` with:

```
Authorization: Bearer ${GRAFANA_TOKEN}
Content-Type: application/json     # on any request with a body
```

Official docs: `https://grafana.com/docs/grafana/latest/developer-resources/api-reference/http-api/`
(legacy `/api/` routes are catalogued under `.../http-api/api-legacy/`).

Grafana's API has grown organically, so paths aren't consistently versioned. Most live under
`/api/`. Starting with Grafana 13 these `/api/` routes are flagged as legacy in favor of
Kubernetes-style resource APIs under `/apis/<group>.grafana.app/...`, but the legacy routes are not
being disabled and remain fully operative — everything below works on current Grafana Cloud and
self-hosted instances. The unified-alerting provisioning endpoints are under
`/api/v1/provisioning/`. The Alertmanager-compatible endpoints are under
`/api/alertmanager/{am_name}/api/v2/`. The Prometheus-compatible read endpoints (for rule *state*)
are under `/api/prometheus/{am_name}/api/v1/`. `{am_name}` is `grafana` for the built-in
Alertmanager, or the datasource UID of an external one.

## Table of contents

- [Health & identity](#health--identity)
- [Search](#search)
- [Dashboards](#dashboards)
- [Folders](#folders)
- [Data sources](#data-sources)
- [Datasource queries (ds/query)](#datasource-queries-dsquery)
- [Alert rules (provisioning)](#alert-rules-provisioning)
- [Alert rule state](#alert-rule-state)
- [Contact points & notification policies](#contact-points--notification-policies)
- [Alertmanager: alerts, groups, silences](#alertmanager-alerts-groups-silences)
- [Annotations](#annotations)
- [Snapshots](#snapshots)
- [Orgs, users, teams, service accounts](#orgs-users-teams-service-accounts)
- [Short URLs](#short-urls)

---

## Health & identity

- **`GET /api/health`** — `{"database":"ok","version":"..."}`. No auth required.
- **`GET /api/user`** — Current authenticated user (or service account).
- **`GET /api/org`** — Current org for the token.
- **`GET /api/frontend/settings`** — Instance config (default datasource, feature toggles).

## Search

- **`GET /api/search`** — Params: `query`, `type` (`dash-db`/`dash-folder`), `tag` (repeatable), `folderUIDs` (repeatable), `starred`, `dashboardUIDs`, `limit` (≤5000), `page`, `sort` (`alpha-asc`/`alpha-desc`).
- **`GET /api/search/sorting`** — Available sort options.

## Dashboards

- **`GET /api/dashboards/uid/{uid}`** — Full dashboard JSON under `.dashboard`, plus `.meta` (folder, perms, version).
- **`POST /api/dashboards/db`** — Create or update. Body: `{"dashboard":{...},"folderUid":"...","overwrite":bool,"message":"..."}`. To update, put the existing `uid` and current `version` in `dashboard`. Returns `{"id","uid","url","status","version"}`. `412` on version conflict.
- **`DELETE /api/dashboards/uid/{uid}`** — Delete.
- **`GET /api/dashboards/uid/{uid}/versions`** — Version history. Params: `limit`, `start`.
- **`GET /api/dashboards/uid/{uid}/versions/{ver}`** — A specific version's full JSON.
- **`POST /api/dashboards/uid/{uid}/restore`** — Body: `{"version": N}`. (Not on the public Dashboard Versions docs page; present in Grafana source.)
- **`GET /api/dashboards/home`** — The org's home dashboard (returns `{"redirectUri": ...}` if one is set).
- **`GET /api/dashboards/tags`** — All tags with counts.
- **`GET/POST /api/dashboards/uid/{uid}/permissions`** — View/set folder- and dashboard-level ACLs.

## Folders

- **`GET /api/folders`** — List. Params: `limit` (default 1000, acts as page size), `page`, `parentUid` (nested folders).
- **`GET /api/folders/{uid}`** — One folder.
- **`POST /api/folders`** — Body: `{"uid":null,"title":"...","parentUid":"..."}`.
- **`PUT /api/folders/{uid}`** — Body: `{"title":"...","version":N,"overwrite":bool}`.
- **`DELETE /api/folders/{uid}`** — Param: `forceDeleteRules=true` to also delete alert rules inside.
- **`GET/POST /api/folders/{uid}/permissions`** — Folder ACL.

## Data sources

- **`GET /api/datasources`** — List all (needs datasource read permission). Each has `uid`, `name`, `type`, `url`, `isDefault`.
- **`GET /api/datasources/uid/{uid}`** — One datasource.
- **`GET /api/datasources/name/{name}`** — Lookup by name. URL-encode the name. Deprecated — prefer the `uid/` path.
- **`POST /api/datasources`** — Create. Body varies by `type` — include `type`, `name`, `url`, `access` (`proxy`/`direct`), `jsonData`, `secureJsonData`.
- **`PUT/DELETE /api/datasources/uid/{uid}`** — Update / delete.
- **`GET /api/datasources/uid/{uid}/health`** — Test the connection.
- **`GET/POST /api/datasources/uid/{uid}/resources/{path}`** — Proxied calls to the datasource's own API. For Prometheus: `.../resources/api/v1/metadata`, `.../resources/api/v1/label/__name__/values`, `.../resources/api/v1/series`.

## Datasource queries (ds/query)

`POST /api/ds/query` with body:

```json
{
  "from": "1700000000000",         // ms epoch, string or int. Relative like "now-1h" also works.
  "to": "now",
  "queries": [
    { "refId": "A", "datasource": {"uid": "<uid>"}, "intervalMs": 30000, "maxDataPoints": 500,
      ... per-datasource fields ... }
  ]
}
```

Multiple `queries[]` with different `refId`s run in one call. Per-datasource shapes:

- **`prometheus`** — `expr` (PromQL). `instant: true` for a point-in-time. `range: true` for a range query.
- **`loki`** — `expr` (LogQL). `queryType`: `range` or `instant`. `maxLines`.
- **`influxdb`** — `query` (InfluxQL) or `rawQuery`. Flux uses `query` with `queryType: "flux"`.
- **`elasticsearch`** — `query` (Lucene), `bucketAggs`, `metrics`, `timeField`.
- **`postgres` / `mysql` / `mssql`** — `rawSql`, `format`: `table` or `time_series`.
- **`cloudwatch`** — `namespace`, `metricName`, `dimensions`, `statistic`, `region`, `queryMode`.
- **`graphite`** — `target`.
- **`tempo`** — `query` (TraceQL), `queryType`.

Responses are Grafana data frames:
`{"results": {"<refId>": {"frames": [{"schema": {...}, "data": {"values": [[...], [...]]}}]}}}`. On
error, `results.<refId>.error` and `results.<refId>.errorSource` are set and `frames` is empty.

## Alert rules (provisioning)

Full CRUD on Grafana-managed alert rule **definitions**. Does not include live state.

- **`GET /api/v1/provisioning/alert-rules`** — All rules.
- **`GET /api/v1/provisioning/alert-rules/{uid}`** — One rule.
- **`POST /api/v1/provisioning/alert-rules`** — Create. Body: `{"title","folderUID","ruleGroup","condition","data":[{"refId","relativeTimeRange","datasourceUid","model":{...}}],"noDataState","execErrState","for","keepFiringFor","labels","annotations"}`. Header `X-Disable-Provenance: true` to allow UI edits afterward.
- **`PUT/DELETE /api/v1/provisioning/alert-rules/{uid}`** — Update / delete.
- **`GET/PUT /api/v1/provisioning/folder/{folderUid}/rule-groups/{group}`** — Whole rule group (shared interval).
- **`GET /api/v1/provisioning/alert-rules/export`** — YAML/HCL export. Param: `format=yaml`.

## Alert rule state

Read-only, Prometheus-compatible. This is where you find **what's firing right now**.

- **`GET /api/prometheus/grafana/api/v1/rules`** — All groups → rules with `state` (`firing`/`pending`/`inactive`), `health`, `lastEvaluation`, per-instance `alerts[]`. Params: `dashboard_uid`, `panel_id`, `rule_name`, `state` (repeatable).
- **`GET /api/prometheus/grafana/api/v1/alerts`** — Flat list of active alert instances.
- **`GET /api/v1/rules/history`** — State-change history. Params: `from`, `to` (unix s), `ruleUID`, `labels_<name>`.

Replace `grafana` with a datasource UID to read an **external** Alertmanager/Prometheus.

## Contact points & notification policies

- **`GET/POST /api/v1/provisioning/contact-points`** — List / create. Each has `uid`, `name`, `type` (`slack`/`email`/`pagerduty`/`webhook`/...), `settings`.
- **`PUT/DELETE /api/v1/provisioning/contact-points/{uid}`** — Update / delete.
- **`GET/PUT /api/v1/provisioning/policies`** — The notification routing tree. PUT replaces the whole tree — GET first.
- **`GET/POST /api/v1/provisioning/mute-timings`** — Time windows where notifications are suppressed.
- **`GET /api/v1/provisioning/templates`** — List notification message templates.
- **`PUT /api/v1/provisioning/templates/{name}`** — Create / update one template.

## Alertmanager: alerts, groups, silences

`{am}` is `grafana` or an external Alertmanager datasource UID.

- **`GET /api/alertmanager/{am}/api/v2/alerts`** — Active alerts. Params: `filter` (matcher, e.g. `alertname="X"`), `silenced`, `inhibited`, `active`.
- **`GET /api/alertmanager/{am}/api/v2/alerts/groups`** — Alerts grouped per notification policy.
- **`GET/POST /api/alertmanager/{am}/api/v2/silences`** — List / create. Body: `{"matchers":[{"name","value","isRegex","isEqual"}],"startsAt","endsAt","createdBy","comment"}`. Timestamps are RFC-3339.
- **`GET/DELETE /api/alertmanager/{am}/api/v2/silence/{id}`** — Fetch / expire a silence.
- **`GET /api/alertmanager/{am}/api/v2/status`** — Alertmanager config + version.

## Annotations

- **`GET /api/annotations`** — Params: `from`, `to` (ms epoch), `tags` (repeatable, AND), `type` (`annotation`/`alert`), `dashboardUID`, `panelId`, `limit` (default 100, no `page`).
- **`POST /api/annotations`** — Body: `{"time":<ms>,"timeEnd":<ms opt.>,"tags":[],"text":"...","dashboardUID":"...","panelId":N}`. Omit dashboard for a global annotation.
- **`POST /api/annotations/graphite`** — Graphite-format shim: `{"what","tags","when","data"}`.
- **`GET/PUT/PATCH/DELETE /api/annotations/{id}`** — CRUD on one.
- **`GET /api/annotations/tags`** — Tag suggestions with counts.

## Snapshots

- **`GET /api/dashboard/snapshots`** — List.
- **`POST /api/snapshots`** — Create from a dashboard JSON. Body: `{"dashboard":{...},"expires":<s>,"external":bool}`. Returns a share key.
- **`GET/DELETE /api/snapshots/{key}`** — Fetch / delete.

## Orgs, users, teams, service accounts

- **`GET /api/org`** — Current org.
- **`GET /api/org/users`** — Members of current org.
- **`GET /api/users/lookup?loginOrEmail=...`** — Resolve a user.
- **`GET /api/teams/search?query=...`** — Search teams.
- **`GET /api/teams/{id}/members`** — Team membership.
- **`GET /api/serviceaccounts/search`** — List service accounts.
- **`GET/POST /api/serviceaccounts/{id}/tokens`** — List / create tokens for a service account.

## Short URLs

- **`POST /api/short-urls`** — Body: `{"path": "d/abc/my-dash?from=...&to=..."}` (path only, no host). Returns `{"uid","url"}`. Useful for sharing a dashboard with a specific time range pinned.

---

## Cross-cutting notes

**Time units** are not uniform — see the top of `../SKILL.md`. Each endpoint above notes its own
unit inline (ms epoch, unix s, RFC-3339).

**UIDs vs IDs.** Newer endpoints use string UIDs; older ones use numeric IDs. Prefer UIDs — they
survive dashboard export/import across instances, numeric IDs don't. Where both exist (dashboards,
folders, datasources), use the `uid/` path.

**Provenance.** Resources created via the provisioning API are flagged as provisioned and the UI
refuses to edit them. Send the header `X-Disable-Provenance: true` on provisioning POST/PUT if
humans should be able to edit the result in the UI.

**Permissions.** Service account roles: `Viewer` (read dashboards + run datasource queries),
`Editor` (create/edit dashboards, annotations, silences), `Admin` (users, datasources, service
accounts). Folder-level permissions can grant more or less than the org role on specific folders.
