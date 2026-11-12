# PagerDuty API — Endpoint Reference

Request setup, auth headers, the `pagerduty()` curl helper, and the REST-vs-Events-v2 split: see
SKILL.md, section Request setup. One detail not covered there: OAuth user tokens use
`Authorization: Bearer <token>` instead of `Token token=`; everything else is identical.

Official docs: `https://developer.pagerduty.com/api-reference/`.

## Table of contents

- [Incidents](#incidents)
- [Alerts](#alerts)
- [Log entries](#log-entries)
- [Services & integrations](#services--integrations)
- [Escalation policies](#escalation-policies)
- [Schedules & overrides](#schedules--overrides)
- [On-calls](#on-calls)
- [Users & contact methods](#users--contact-methods)
- [Teams](#teams)
- [Priorities, tags, maintenance windows](#priorities-tags-maintenance-windows)
- [Business services & status dashboard](#business-services--status-dashboard)
- [Analytics](#analytics)
- [Events API v2](#events-api-v2)

---

## Incidents

- **`GET /incidents`** — List. Params: `statuses[]` (`triggered`/`acknowledged`/`resolved`), `service_ids[]`, `team_ids[]`, `user_ids[]` (currently assigned), `urgencies[]` (`high`/`low`), `since`/`until` (ISO-8601), `date_range=all`, `sort_by` (`created_at`/`resolved_at`/`urgency` + `:asc`/`:desc`), `incident_key`, `include[]` (`acknowledgers`/`assignees`/`escalation_policies`/`services`/`teams`/`priorities`/`first_trigger_log_entries`/`conference_bridge`), `limit`, `offset`.
- **`GET /incidents/{id}`** — One incident. `{id}` is the alphanumeric ID (`Q...`), not `incident_number`.
- **`POST /incidents`** — Create. Body: `{"incident":{"type":"incident","title","urgency":"high","service":{"id","type":"service_reference"},"priority":{"id","type":"priority_reference"},"escalation_policy":{"id","type":"escalation_policy_reference"},"assignments":[{"assignee":{"id","type":"user_reference"}}],"body":{"type":"incident_body","details"},"incident_key"}}`. Requires `From:`.
- **`PUT /incidents/{id}`** — Update. Body: `{"incident":{"type":"incident_reference","status":"acknowledged"|"resolved","urgency","escalation_level":N,"assignments":[...],"priority":{...},"title","resolution"}}`. Requires `From:`.
- **`PUT /incidents`** — Bulk update, body is `{"incidents":[{"id","type":"incident_reference","status",...},...]}`.
- **`POST /incidents/{id}/snooze`** — Body: `{"duration":<seconds>}`. Requires `From:`.
- **`PUT /incidents/{id}/merge`** — Body: `{"source_incidents":[{"id","type":"incident_reference"},...]}`. Merges sources into `{id}`.
- **`GET/POST /incidents/{id}/notes`** — Status update notes. POST body: `{"note":{"content":"..."}}`. Requires `From:`.
- **`POST /incidents/{id}/responder_requests`** — Add responders. Body: `{"requester_id","message","responder_request_targets":[{"responder_request_target":{"id","type":"user_reference"|"escalation_policy_reference"}}]}`. No GET — past requests show up as `responder_request_log_entry` in the incident's log entries.
- **`POST /incidents/{id}/status_updates`** — Send a status update to subscribers (if Status Dashboard is enabled). No GET — past updates appear as `status_update_log_entry` in the incident's log entries.
- **`GET /incidents/{id}/related_incidents`** — ML-grouped related incidents.
- **`GET /incidents/{id}/past_incidents`** — Past similar incidents.
- **`GET /incidents/count`** — Count matching incidents, same filters as list.

## Alerts

Alerts are the raw trigger events grouped under an incident.

- **`GET /incidents/{id}/alerts`** — Alerts for an incident. Params: `statuses[]` (`triggered`/`resolved`), `alert_key`, `sort_by`. Each alert's `body.details` / `body.cef_details` carry the originating monitoring system's payload.
- **`GET/PUT /incidents/{id}/alerts/{alert_id}`** — One alert. PUT to resolve or re-associate with a different incident.

## Log entries

- **`GET /log_entries`** — All log entries account-wide. Params: `since`/`until`, `is_overview` (true = only high-level: trigger/escalate/resolve), `team_ids[]`, `include[]` (`incidents`/`services`/`channels`).
- **`GET /log_entries/{id}`** — One log entry.
- **`GET /incidents/{id}/log_entries`** — Log entries scoped to an incident, the paging/ack/resolve timeline. Params: `is_overview`, `include[]`.

There is no per-user log-entries endpoint — to see what a user did, list `/log_entries` over a time
window and filter on `.agent.id` client-side.

Log entry `type` values: `trigger_log_entry`, `acknowledge_log_entry`, `unacknowledge_log_entry`,
`assign_log_entry`, `escalate_log_entry`, `notify_log_entry`, `resolve_log_entry`,
`snooze_log_entry`, `annotate_log_entry`, `responder_request_log_entry`, `status_update_log_entry`.
`notify_log_entry` has `.channel.type` (`sms`/`phone`/`email`/`push_notification`).

## Services & integrations

- **`GET /services`** — List. Params: `query`, `team_ids[]`, `include[]` (`escalation_policies`/`teams`/`integrations`), `sort_by` (`name`/`name:desc`).
- **`GET/PUT/DELETE /services/{id}`** — One service.
- **`POST /services`** — Create. Body: `{"service":{"type":"service","name","description","escalation_policy":{...},"alert_creation":"create_alerts_and_incidents","incident_urgency_rule":{...},"auto_resolve_timeout","acknowledgement_timeout"}}`.
- **`POST /services/{id}/integrations`** — Create an integration (a routing key for monitoring systems). Body: `{"integration":{"type":"events_api_v2_inbound_integration","name"}}`. There is no list GET — read a service's integrations via `GET /services/{id}?include[]=integrations`.
- **`GET/PUT /services/{id}/integrations/{iid}`** — One integration. The integration's `integration_key` is the routing key for the Events API.
- **`GET /service_dependencies/business_services/{id}`** — Dependencies of a business service.
- **`GET /service_dependencies/technical_services/{id}`** — Dependencies of a technical service.

## Escalation policies

- **`GET /escalation_policies`** — List. Params: `query`, `user_ids[]`, `team_ids[]`, `include[]` (`services`/`teams`/`targets`), `sort_by`.
- **`GET/PUT/DELETE /escalation_policies/{id}`** — One policy.
- **`POST /escalation_policies`** — Create. Body: `{"escalation_policy":{"type":"escalation_policy","name","num_loops":2,"escalation_rules":[{"escalation_delay_in_minutes":10,"targets":[{"id","type":"schedule_reference"|"user_reference"}]}]}}`.

`escalation_rules` are evaluated in order; each rule's `targets` are notified simultaneously, then
after `escalation_delay_in_minutes` the next rule fires if unacknowledged.

## Schedules & overrides

- **`GET /schedules`** — List. Params: `query`, `include[]` (`schedule_layers`).
- **`GET /schedules/{id}`** — One schedule. Params: `since`/`until` (ISO-8601) scope the rendered entries; `time_zone`. Response has `schedule_layers[]` (raw rotation config), `overrides_subschedule`, and `final_schedule` (what's actually in effect after overrides).
- **`POST /schedules`** — Create. Body has `schedule`: `{"type":"schedule","name","time_zone","schedule_layers":[{"start","rotation_virtual_start","rotation_turn_length_seconds":604800,"users":[{"user":{"id","type":"user_reference"}}]}]}`.
- **`PUT/DELETE /schedules/{id}`** — Update / delete.
- **`GET/POST /schedules/{id}/overrides`** — Overrides. POST body: `{"overrides":[{"start","end","user":{"id","type":"user_reference"}}]}`. GET params: `since`/`until` (required), `editable`, `overflow`.
- **`DELETE /schedules/{id}/overrides/{oid}`** — Remove an override.
- **`GET /schedules/{id}/users`** — Users in the schedule. Params: `since`/`until`.
- **`POST /schedules/preview`** — Dry-run a schedule definition to see the rendered rotation without creating it.

## On-calls

- **`GET /oncalls`** — Current on-call assignments. Params: `time_zone`, `user_ids[]`, `escalation_policy_ids[]`, `schedule_ids[]`, `since`/`until`, `earliest` (only the next on-call per policy), `include[]` (`escalation_policies`/`users`/`schedules`), `limit`, `offset`. Each result has `user`, `schedule` (may be null for direct user targets), `escalation_policy`, `escalation_level`, `start`, `end`.

## Users & contact methods

- **`GET /users`** — List. Params: `query` (name/email), `team_ids[]`, `include[]` (`contact_methods`/`notification_rules`/`teams`/`subdomains`).
- **`GET/PUT/DELETE /users/{id}`** — One user.
- **`GET /users/me`** — Current user (user-token auth only).
- **`GET/POST /users/{id}/contact_methods`** — Phone/SMS/email/push.
- **`GET/POST /users/{id}/notification_rules`** — Ordered rules: after N min, notify via contact method X at urgency Y. This is the ground truth for "why didn't I get paged."
- **`GET /oncalls?user_ids[]={id}`** — When this user is on call. There is no `/users/{id}/oncalls` endpoint — filter `/oncalls` with `user_ids[]` plus `since`/`until`, `escalation_policy_ids[]`.
- **`GET/DELETE /users/{id}/sessions`** — Active browser/app sessions (admin).

## Teams

- **`GET/POST /teams`** — List / create.
- **`GET/PUT/DELETE /teams/{id}`** — One team.
- **`GET /teams/{id}/members`** — Members with role.
- **`PUT/DELETE /teams/{id}/users/{uid}`** — Add / remove a user. PUT body: `{"role":"manager"|"responder"|"observer"}`.
- **`PUT/DELETE /teams/{id}/escalation_policies/{eid}`** — Associate / dissociate a policy.

## Priorities, tags, maintenance windows

- **`GET /priorities`** — Account priority levels (P1–P5). Use the returned `id` in incident priority references.
- **`GET/POST /tags`** — Account-wide tags.
- **`GET /{entity_type}/{id}/tags`** — Tags on a user/team/escalation_policy.
- **`GET/POST /maintenance_windows`** — Suppress incident creation for a service over a window. Body: `{"maintenance_window":{"type":"maintenance_window","start_time","end_time","description","services":[{"id","type":"service_reference"}]}}`.
- **`GET/PUT/DELETE /maintenance_windows/{id}`** — One window.

## Business services & status dashboard

- **`GET/POST /business_services`** — Business-level services (stakeholder-facing groupings).
- **`GET/PUT/DELETE /business_services/{id}`** — One business service.
- **`GET /business_services/impacts`** — Current impact state for business services.
- **`GET /status_dashboards`** — Configured status dashboards.

## Analytics

Note: analytics endpoints are available on some plan tiers only.

- **`POST /analytics/metrics/incidents/all`** — Aggregate incident metrics (MTTA, MTTR, counts). Body: `{"filters":{"created_at_start","created_at_end","service_ids"},"aggregate_unit":"day"|"week"|"month","time_zone"}`.
- **`POST /analytics/metrics/incidents/services`** — Per-service breakdown. Same body shape.
- **`POST /analytics/metrics/incidents/escalation_policies`** — Per-policy breakdown.
- **`POST /analytics/raw/incidents`** — Per-incident rows with derived metrics. Cursor-paginated: pass the response's `last` value back as `starting_after` in the next request body.
- **`POST /analytics/metrics/responders/all`** — Responder workload metrics.

## Events API v2

Base URL: `https://events.pagerduty.com`. No `Authorization` header — the `routing_key` in the body
authenticates.

- **`POST /v2/enqueue`** — Trigger/acknowledge/resolve an alert. See body below. Returns `202` with `{"status":"success","message":"Event processed","dedup_key":"..."}`.
- **`POST /v2/change/enqueue`** — Submit a change event (deploys, config changes). Body: `{"routing_key","payload":{"summary","source","timestamp","custom_details"},"links":[{"href","text"}]}`.

`/v2/enqueue` body:

```json
{
  "routing_key": "<32-hex-char integration key>",
  "event_action": "trigger" | "acknowledge" | "resolve",
  "dedup_key": "<unique per incident — events with the same key group>",
  "payload": {
    "summary": "Brief text shown in PD UI",
    "source": "Hostname or system identifier",
    "severity": "critical" | "error" | "warning" | "info",
    "timestamp": "2024-01-01T00:00:00Z",
    "component": "database",
    "group": "prod-us-east",
    "class": "high_latency",
    "custom_details": {"arbitrary": "json"}
  },
  "images": [{"src": "https://...", "href": "https://...", "alt": "..."}],
  "links": [{"href": "https://...", "text": "Runbook"}],
  "client": "My Monitoring System",
  "client_url": "https://..."
}
```

For `acknowledge` / `resolve`, only `routing_key`, `event_action`, and `dedup_key` are required.

---

## Cross-cutting notes

`From:` header on mutations, `{"id","type":"<x>_reference"}` body wrappers, bracket array params
and curl `-g`, pagination/offset caps, rate limits, and the error envelope: see SKILL.md
(operation 5, plus the Pagination, Rate limits, and Error handling sections).

**Token types.** Read-only account tokens cannot mutate anything. User tokens inherit the user's
role — a Limited User can only see what their teams own. OAuth-scoped tokens specify scopes at
creation (e.g. `incidents.read`, `schedules.read`).
