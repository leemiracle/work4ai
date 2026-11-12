# Datadog REST API — Endpoint Reference

All requests go to `${DD_API}` (e.g. `https://api.datadoghq.com`) with these headers:

```
DD-API-KEY: ${DD_API_KEY}
DD-APPLICATION-KEY: ${DD_APP_KEY}      # required for nearly all endpoints below
Content-Type: application/json          # on any request with a body
```

Substitute your org's site (`us3.`, `us5.`, `datadoghq.eu`, `ap1.`, `ap2.`, `ddog-gov.com`) if not
US1. The official docs live at `https://docs.datadoghq.com/api/latest/`.

Many query params below are bracketed (`page[size]`, `filter[query]`, …) — the `ddog` helper's `-g`
handles this. See `../SKILL.md` → Request setup for the `curl -g` / percent-encoding requirement.

## Table of contents

- [Validation & org](#validation--org)
- [Metrics](#metrics)
- [Logs](#logs)
- [Monitors](#monitors)
- [Downtime](#downtime)
- [Dashboards](#dashboards)
- [SLOs](#slos)
- [Events](#events)
- [APM / Traces](#apm--traces)
- [Incidents](#incidents)
- [Notebooks](#notebooks)
- [Hosts & Tags](#hosts--tags)
- [Users & Teams](#users--teams)
- [RUM](#rum)

---

## Validation & org

- **`GET /api/v1/validate`** — Validate `DD-API-KEY`. Returns `{"valid": true}`. App key not required.
- **`GET /api/v1/org`** — Your org's settings and ID.
- **`GET /api/v2/api_keys`** — List API keys (requires admin app key).

## Metrics

- **`GET /api/v1/query`** — Time-series query. Params: `from` (unix s), `to` (unix s), `query` (metric syntax).
- **`GET /api/v1/metrics`** — List actively-reporting metric names. Param: `from` (unix s).
- **`GET /api/v1/search`** — **Deprecated**, use `/api/v2/metrics` instead. Search metrics. Param: `q=metrics:<prefix>`.
- **`GET /api/v2/metrics`** — List tag-configured / queryable metrics. Params: `filter[configured]`, `filter[tags_configured]`, `filter[queried]`, `window[seconds]`. Bracketed params need `curl -g`.
- **`GET /api/v2/metrics/{name}/tags`** — Tags configured on a metric.
- **`GET /api/v2/metrics/{name}/all-tags`** — All tag keys/values actively reporting.
- **`POST /api/v1/series`** — **Submit** custom metrics. Body: `{"series":[{"metric":"x","points":[[ts,val]],"type":"gauge","tags":[...]}]}`. Only `DD-API-KEY` needed.
- **`POST /api/v2/query/timeseries`** — Newer query interface, accepts multiple queries and formulas in one call. Body: `{"data":{"type":"timeseries_request","attributes":{"from":<ms>,"to":<ms>,"queries":[{"data_source":"metrics","name":"a","query":"avg:..."}],"formulas":[{"formula":"a"}]}}}`. Each query needs a `name` that the `formulas[]` array references; pass `{"formula":"<name>"}` for a passthrough.

Metric query syntax:
`space_agg:metric.name{tag:val, tag2:val2} by {group}.rollup(method, interval)`. Space aggregators:
`avg`, `sum`, `min`, `max`, `count`. Arithmetic (`a / b * 100`) and functions (`rate()`, `diff()`,
`ewma_10()`) work like in the UI.

## Logs

All logs endpoints are v2 and take `POST` with a JSON body.

- **`POST /api/v2/logs/events/search`** — Search raw logs. Body: `{"filter":{"query","from","to","indexes":["main"]},"sort":"-timestamp","page":{"limit":50,"cursor":"..."}}`.
- **`GET /api/v2/logs/events`** — Same search via query params: `filter[query]`, `filter[from]`, `filter[to]`, `sort`, `page[cursor]`, `page[limit]`.
- **`POST /api/v2/logs/analytics/aggregate`** — Bucket logs by facet. Body: `{"filter":{...},"compute":[{"aggregation":"count"}|{"aggregation":"avg","metric":"@duration"}],"group_by":[{"facet":"service","limit":10,"sort":{"aggregation":"count","order":"desc"}}]}`.
- **`GET /api/v1/logs/config/indexes`** — List log indexes and their retention/filters.
- **`POST /api/v2/logs`** — **Ingest** logs. Uses `http-intake.logs.${DD_SITE}` host, not `api.`.

Query syntax: `service:web status:error @http.status_code:>=500 "exact phrase" -excluded`. `@`
prefix = log attribute, no prefix = reserved (service, status, host, source).

Aggregation functions: `count`, `cardinality`, `avg`, `sum`, `min`, `max`, `median`,
`pc75`/`pc90`/`pc95`/`pc98`/`pc99`.

## Monitors

- **`GET /api/v1/monitor`** — List all monitors. Params: `monitor_tags`, `tags`, `name`, `group_states` (`all`/`alert`/`warn`/`no data`), `with_downtimes`, `page`, `page_size`.
- **`GET /api/v1/monitor/{id}`** — One monitor. Param: `group_states`.
- **`GET /api/v1/monitor/search`** — Faceted search. Params: `query` (e.g. `status:alert team:foo`), `page`, `per_page`, `sort` (e.g. `status,asc`). Returns `monitors[]` + `metadata`.
- **`GET /api/v1/monitor/groups/search`** — Same, but per alert group.
- **`POST /api/v1/monitor`** — Create. Body: `{"type":"metric alert","query":"avg(last_5m):...> 0.8","name":"...","message":"@slack-oncall","options":{"thresholds":{"critical":0.8,"warning":0.6},"notify_no_data":false,"renotify_interval":0}}`.
- **`PUT /api/v1/monitor/{id}`** — Update. Send partial body — only the fields you change.
- **`DELETE /api/v1/monitor/{id}`** — Delete. Check `/api/v1/monitor/can_delete?monitor_ids=1,2` first if the monitor might be referenced by SLOs or composites.
- **`POST /api/v1/monitor/{id}/mute`** — **Legacy, removed from the API reference.** Still responds. Body: `{"scope":"host:foo","end":<unix_s>}`. Prefer a v2 downtime with `monitor_identifier.monitor_id`.
- **`POST /api/v1/monitor/{id}/unmute`** — **Legacy, removed from the API reference.** Still responds. Body: `{"scope":"...","all_scopes":false}`. Prefer cancelling the v2 downtime.
- **`POST /api/v1/monitor/validate`** — Validate a monitor body without creating it. Same body as create.

Monitor `type` values: `metric alert`, `query alert`, `service check`, `log alert`,
`trace-analytics alert`, `slo alert`, `event-v2 alert`, `composite`, `process alert`, `rum alert`,
`ci-pipelines alert`, `audit alert`, `database-monitoring alert`.

`overall_state` values: `OK`, `Alert`, `Warn`, `No Data`, `Skipped`, `Unknown`, `Ignored`.

## Downtime

Scheduled downtime suppresses monitor notifications. The v1 `/api/v1/downtime` endpoints are
deprecated — use v2. This is also the documented way to mute a single monitor: set
`monitor_identifier` to `{"monitor_id": <id>}`.

- **`GET /api/v2/downtime`** — List. Params: `current_only`, `include=created_by,monitor`.
- **`POST /api/v2/downtime`** — Create. Body: `{"data":{"type":"downtime","attributes":{"scope":"env:prod","schedule":{"start":"...","end":"..."},"monitor_identifier":{"monitor_tags":["*"]}}}}`. `scope` and `monitor_identifier` are required; `monitor_identifier` is `{"monitor_id":<id>}` or `{"monitor_tags":[...]}`. Schedule timestamps are ISO-8601 with a zero UTC offset.
- **`GET/PATCH/DELETE /api/v2/downtime/{id}`** — Fetch / update / cancel. DELETE returns `204 No Content` — add `-w '\n%{http_code}\n'` to see success.
- **`GET /api/v2/monitor/{monitor_id}/downtime_matches`** — Active downtimes affecting a monitor.

## Dashboards

- **`GET /api/v1/dashboard`** — List, returns lightweight summaries under `dashboards[]`.
- **`GET /api/v1/dashboard/{id}`** — Full dashboard JSON including `widgets[]` with their queries.
- **`POST /api/v1/dashboard`** — Create. Body: `{"title","layout_type":"ordered"|"free","widgets":[...]}`.
- **`PUT /api/v1/dashboard/{id}`** — **Full replace.** GET → mutate → PUT the whole doc.
- **`DELETE /api/v1/dashboard/{id}`** — Delete.
- **`GET /api/v1/dashboard/lists/manual`** — Dashboard lists.
- **`GET /api/v1/dashboard/public/{token}`** — Shared (public) dashboard by token.

Dashboard IDs are short alpha strings (`abc-def-ghi`), visible in the URL, not the title.

## SLOs

- **`GET /api/v1/slo`** — List. Params: `ids`, `query`, `tags_query`, `metrics_query`, `limit`, `offset`.
- **`GET /api/v1/slo/{id}`** — One SLO. Param: `with_configured_alert_ids`.
- **`GET /api/v1/slo/{id}/history`** — Uptime over a window. Params: `from_ts`, `to_ts` (unix s), `target`, `apply_correction`.
- **`POST /api/v1/slo`** — Create.
- **`PUT/DELETE /api/v1/slo/{id}`** — Update / delete.
- **`GET /api/v1/slo/{id}/corrections`** — Status corrections.
- **`GET /api/v1/slo/search`** — Faceted search. Params: `query`, `page[size]`, `page[number]`.

SLO `type` is `metric`, `monitor`, or `time_slice`. Thresholds:
`[{"timeframe":"30d","target":99.9,"warning":99.95}]`.

## Events

- **`GET /api/v1/events`** — Query stream. Params: `start`, `end` (unix s), `priority`, `sources`, `tags`, `unaggregated`.
- **`GET /api/v1/events/{id}`** — One event.
- **`POST /api/v1/events`** — Post an event. Body: `{"title","text","tags":[],"alert_type":"info"|"warning"|"error"|"success","priority":"normal"|"low","aggregation_key","source_type_name","date_happened":<unix_s>}`. Only `DD-API-KEY` required.
- **`POST /api/v2/events/search`** — Search. Body: `{"filter":{"query","from","to"},"sort":"-timestamp","page":{"limit","cursor"}}`.
- **`GET /api/v2/events`** — Same search via `filter[query]` etc. query params.

## APM / Traces

- **`POST /api/v2/spans/events/search`** — Search spans. Body wrapped in JSON:API envelope: `{"data":{"type":"search_request","attributes":{"filter":{"query","from","to"},"sort","page":{"limit","cursor"}}}}`.
- **`GET /api/v2/spans/events`** — Same via `filter[query]` etc. query params.
- **`POST /api/v2/spans/analytics/aggregate`** — Aggregate spans. Same envelope; `attributes.compute`, `attributes.group_by` like log aggregation.
- **`GET/POST /api/v2/services/definitions`** — Service Catalog definitions (owner, team, links, contacts). Param: `schema_version`.

Span query syntax mirrors logs: `service:web resource_name:"GET /users" @http.status_code:>=500`. To
reconstruct a trace, search with `trace_id:<id>` and sort by `timestamp`.

## Incidents

Unstable/beta endpoints — shapes may shift.

- **`GET /api/v2/incidents`** — List. Params: `page[size]`, `page[offset]`, `include=users`.
- **`GET /api/v2/incidents/{id}`** — One incident.
- **`POST /api/v2/incidents`** — Create. Body: `{"data":{"type":"incidents","attributes":{"title","customer_impacted":false,"fields":{"severity":{"type":"dropdown","value":"SEV-3"}}}}}`.
- **`PATCH /api/v2/incidents/{id}`** — Update fields / state transitions.
- **`GET/PATCH /api/v2/incidents/{id}/attachments`** — Postmortem links etc.
- **`GET /api/v2/incidents/{id}/relationships/todos`** — Incident todo items.
- **`GET /api/v2/incidents/search`** — Param: `query` (e.g. `state:active severity:SEV-1`).

## Notebooks

- **`GET /api/v1/notebooks`** — List. Params: `author_handle`, `query`, `is_template`, `type`, `count`, `start`.
- **`GET /api/v1/notebooks/{id}`** — One notebook with all cells.
- **`POST /api/v1/notebooks`** — Create. Body: `{"data":{"type":"notebooks","attributes":{"name","cells":[...],"time":{"live_span":"1h"}}}}`.
- **`PUT /api/v1/notebooks/{id}`** — **Full replace**, same caveat as dashboards.
- **`DELETE /api/v1/notebooks/{id}`** — Delete.

## Hosts & Tags

- **`GET /api/v1/hosts`** — List hosts. Params: `filter`, `sort_field`, `sort_dir`, `start`, `count`, `from`, `include_muted_hosts_data`.
- **`GET /api/v1/hosts/totals`** — Active / up counts.
- **`POST /api/v1/host/{name}/mute`** — Mute a host. Body: `{"end":<unix_s>,"message":"..."}`.
- **`POST /api/v1/host/{name}/unmute`** — Unmute.
- **`GET /api/v1/tags/hosts`** — All tags by host.
- **`GET/POST/PUT/DELETE /api/v1/tags/hosts/{host}`** — Tags for one host.

## Users & Teams

- **`GET /api/v2/users`** — List. Params: `page[size]`, `page[number]`, `sort`, `filter`, `filter[status]`.
- **`GET /api/v2/users/{id}`** — One user.
- **`GET /api/v2/current_user`** — Who the app key belongs to.
- **`GET /api/v2/team`** — List teams.
- **`GET /api/v2/team/{id}/memberships`** — Team membership.
- **`GET /api/v2/roles`** — RBAC roles.

## RUM

- **`POST /api/v2/rum/events/search`** — Search RUM events (sessions/views/actions/errors/resources). Body: `{"filter":{"query","from","to"},"sort","page"}`.
- **`POST /api/v2/rum/analytics/aggregate`** — Aggregate RUM events. Same shape as log aggregation.
- **`GET /api/v2/rum/applications`** — List RUM applications.
- **`GET/POST /api/v2/rum/config/metrics`** — Custom RUM-based metrics.

Query: `@type:error @application.id:<id> @error.source:source`.

---

## Cross-cutting notes

**JSON:API envelope.** v2 collection endpoints (incidents, users, downtime, notebooks, spans) wrap
payloads as `{"data": {"type": "...", "attributes": {...}}}` or `{"data": [...]}` on lists. v2
logs/events search use a flat `{"filter": ..., "page": ...}` shape. When you get a `400`, check
whether you're missing or over-including the envelope.

**Timestamps.** v1 endpoints generally want Unix **seconds**. v2 filter objects accept
`now`/`now-1h`, ISO-8601, or Unix **milliseconds**. The `/api/v2/query/timeseries` body wants
milliseconds. Mixing these up is the most common silent-wrong-result bug.

**Idempotency.** None of the write endpoints are idempotent. Posting an event or creating a monitor
twice creates two. Check for existence first if a retry is possible.

**Permissions.** App keys inherit the creating user's role. Common `403` causes: a read-only user
trying to mutate, an org-scoped key in the wrong org, or a key lacking the `logs_read_data` /
`monitors_write` / `incidents_read` RBAC permission.
