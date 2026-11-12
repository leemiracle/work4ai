# Sentry REST API — Endpoint Reference

All requests go to `${SENTRY_URL}/api/0/` with:

```
Authorization: Bearer ${SENTRY_TOKEN}
Content-Type: application/json     # on any request with a body
```

Official docs: `https://docs.sentry.io/api/`.

Path conventions:
- `{org}` — organization **slug** (string, e.g. `acme`)
- `{project}` — project **slug** (string, e.g. `backend`)
- `{issue_id}` — issue **numeric ID**
- `{event_id}` — event's 32-hex-char ID

Most endpoints accept a trailing slash; a few require it.

## Table of contents

- [Organizations](#organizations)
- [Projects](#projects)
- [Issues](#issues)
- [Events](#events)
- [Discover / events search](#discover--events-search)
- [Releases & deploys](#releases--deploys)
- [Stats](#stats)
- [Teams & members](#teams--members)
- [Alert rules](#alert-rules)
- [SDK keys & client config](#sdk-keys--client-config)

---

## Organizations

- **`GET /api/0/organizations/`** — Orgs the token can see.
- **`GET /api/0/organizations/{org}/`** — Org details.
- **`GET /api/0/organizations/{org}/projects/`** — Projects in org. Params: `cursor`, `query`.
- **`GET /api/0/organizations/{org}/repos/`** — Linked source repos (for commit/release linking).
- **`GET /api/0/organizations/{org}/environments/`** — Environments seen across the org.
- **`GET /api/0/organizations/{org}/tags/{key}/values/`** — Distinct values for a tag key org-wide.

## Projects

- **`GET /api/0/projects/`** — All projects the token can access (cross-org).
- **`GET/PUT/DELETE /api/0/projects/{org}/{project}/`** — One project. PUT body: `{"name","slug","platform","subjectPrefix","resolveAge"}` etc.
- **`GET/POST /api/0/projects/{org}/{project}/keys/`** — Client DSNs.
- **`GET /api/0/projects/{org}/{project}/environments/`** — Environments this project has reported.
- **`GET /api/0/projects/{org}/{project}/releases/`** — Releases scoped to the project.
- **`GET /api/0/projects/{org}/{project}/users/`** — Users seen in error events. Param: `query` (email/id/ip/username).
- **`GET /api/0/projects/{org}/{project}/stats/`** — Event counts over time. Params: `stat` (`received`/`rejected`/`blacklisted`), `since`, `until`, `resolution` (`10s`/`1h`/`1d`).
- **`GET /api/0/projects/{org}/{project}/filters/`** — Inbound data filters.

## Issues

Two entry points with the same query grammar: org-wide and per-project.

- **`GET /api/0/organizations/{org}/issues/`** — Search across org. Params: `query`, `sort` (`date`/`new`/`freq`/`user`/`trends`/`inbox`/`recommended`), `statsPeriod` (e.g. `24h`, `14d`), `start`/`end` (ISO-8601, alternative to statsPeriod), `project` (numeric ID or slug, repeatable), `environment` (repeatable), `cursor`, `limit` (≤100), `shortIdLookup=1` to allow bare short IDs in `query`.
- **`GET /api/0/projects/{org}/{project}/issues/`** — Same, project-scoped.
- **`GET /api/0/organizations/{org}/issues/{issue_id}/`** — One issue. Includes `stats` (24h/30d series), `firstRelease`, `lastRelease`, `activity`, `userReportCount`.
- **`PUT /api/0/organizations/{org}/issues/{issue_id}/`** — Update. Body: `{"status":"resolved"|"resolvedInNextRelease"|"unresolved"|"ignored","statusDetails":{...},"assignedTo":"user@x"|"team:<team_id>","hasSeen":bool,"isBookmarked":bool,"isSubscribed":bool,"isPublic":bool}`. The numeric team id comes from `GET /api/0/organizations/{org}/teams/`.
- **`DELETE /api/0/organizations/{org}/issues/{issue_id}/`** — Delete (async).
- **`PUT/DELETE /api/0/organizations/{org}/issues/`** — Bulk. Pass `?id=1&id=2` or `?query=is:ignored` to select. Same PUT body as single.
- **`GET /api/0/organizations/{org}/issues/{issue_id}/events/`** — Events in the group. Params: `query` (filter within the group), `environment`, `statsPeriod`, `cursor`, `per_page`, `full=true` (include stack traces in list), `sample=true` (pseudo-random order).
- **`GET /api/0/organizations/{org}/issues/{issue_id}/events/latest/`** — Latest event. Also `oldest/`, `recommended/`.
- **`GET /api/0/organizations/{org}/issues/{issue_id}/tags/`** — Tag keys with counts.
- **`GET /api/0/organizations/{org}/issues/{issue_id}/tags/{key}/`** — Top values for one tag.
- **`GET /api/0/organizations/{org}/issues/{issue_id}/tags/{key}/values/`** — All values (paginated).
- **`GET /api/0/organizations/{org}/issues/{issue_id}/hashes/`** — Grouping hashes (for un-merge).
- **`GET/POST /api/0/organizations/{org}/issues/{issue_id}/comments/`** — Notes. POST body: `{"text": "..."}`.

**Issue search grammar (same as UI):**
`is:unresolved|resolved|ignored|assigned|unassigned|for_review`, `level:error|warning|info`,
`assigned:me|user@x|team:slug`, `release:<version>|latest`, `environment:<env>`,
`firstSeen:>2024-01-01`, `lastSeen:-24h`, `age:-24h`, `timesSeen:>100`, `has:<tag>`, `!has:<tag>`,
arbitrary `tagKey:tagValue`, free text for message search.

**statusDetails options:**
- resolve: `{"inRelease":"ver"}`, `{"inNextRelease":true}`,
  `{"inCommit":{"repository":"o/r","commit":"sha"}}`
- ignore: `{"ignoreDuration":<min>}`, `{"ignoreCount":N}`, `{"ignoreWindow":<min>}`,
  `{"ignoreUserCount":N}`, `{"ignoreUserWindow":<min>}`

## Events

- **`GET /api/0/projects/{org}/{project}/events/`** — Raw event stream. Param: `full=true`.
- **`GET /api/0/projects/{org}/{project}/events/{event_id}/`** — One event, full payload including `entries[]` (exception, breadcrumbs, request, threads), `tags`, `contexts`, `sdk`.
- **`GET /api/0/organizations/{org}/eventids/{event_id}/`** — Resolve an event ID to its project + issue.

Event `entries[]` is a list of typed sections. The exception section:
```json
{"type": "exception", "data": {"values": [
  {"type": "ValueError", "value": "...", "module": "...",
   "stacktrace": {"frames": [{"filename","function","lineNo","colNo","context","vars","inApp"}, ...]}}
]}}
```
Frames are ordered **outermost → innermost** (the crash site is `frames[-1]`).

## Discover / events search

Cross-project, column-selectable event queries (the "Discover" / "Explore" feature in the UI).

- **`GET /api/0/organizations/{org}/events/`** — Params: `field` (repeatable, e.g. `title`, `count()`, `p95(transaction.duration)`), `query`, `sort`, `per_page`, `statsPeriod` or `start`/`end`, `project`, `environment`, `dataset` (`errors`/`logs`/`profile_functions`/`spans`/`tracemetrics`/`uptime_results`; `transactions`/`discover` are legacy).
- **`GET /api/0/organizations/{org}/events-stats/`** — Time-series. Params as above plus `interval`, `yAxis` (repeatable aggregate).
- **`GET /api/0/organizations/{org}/events-meta/`** — Count matching events (`{"count": N}`).

## Releases & deploys

- **`GET /api/0/organizations/{org}/releases/`** — Params: `query`, `per_page`, `cursor`, `project`.
- **`POST /api/0/organizations/{org}/releases/`** — Body: `{"version","projects":["slug"],"refs":[{"repository","commit","previousCommit"}],"dateReleased"}`.
- **`GET/PUT/DELETE /api/0/organizations/{org}/releases/{version}/`** — One release.
- **`GET /api/0/organizations/{org}/releases/{version}/commits/`** — Commits in the release. There is no POST on this path; attach commits via the `commits` / `refs` arrays on the release create/update body.
- **`GET /api/0/organizations/{org}/releases/{version}/commitfiles/`** — Changed files.
- **`GET/POST /api/0/organizations/{org}/releases/{version}/deploys/`** — Deploys. POST body: `{"environment","name","url","dateStarted","dateFinished"}`.
- **`GET/POST /api/0/organizations/{org}/releases/{version}/files/`** — Source maps / debug files. POST is `multipart/form-data`.
- **`GET /api/0/organizations/{org}/sessions/`** — Release health (crash-free rate). Params: `field` (e.g. `sum(session)`, `crash_free_rate(session)`), `groupBy`, `interval`, `statsPeriod`.

## Stats

- **`GET /api/0/organizations/{org}/stats_v2/`** — Params: `statsPeriod` or `start`/`end`, `interval` (`1h`/`1d`), `groupBy` (**required**, repeatable: `project`/`outcome`/`reason`/`category`), `field` (**required**: `sum(quantity)`/`sum(times_seen)`), `category` (`error`/`transaction`/`attachment`/`replay`/`profile`/`monitor`), `project`, `outcome`.
- **`GET /api/0/projects/{org}/{project}/stats/`** — Legacy project event counts.

## Teams & members

- **`GET/POST /api/0/organizations/{org}/teams/`** — Teams. POST body: `{"name","slug"}`.
- **`GET/PUT/DELETE /api/0/teams/{org}/{team}/`** — One team.
- **`GET /api/0/teams/{org}/{team}/members/`** — Team membership.
- **`GET/POST /api/0/teams/{org}/{team}/projects/`** — Projects assigned to the team.
- **`GET /api/0/organizations/{org}/members/`** — Org members with roles.
- **`GET /api/0/organizations/{org}/users/`** — Members with linked team info.

## Alert rules

Two types: **issue alerts** (rule-based, per project) and **metric alerts** (threshold on an
aggregate, org-scoped).

- **`GET/POST /api/0/projects/{org}/{project}/rules/`** — Issue alert rules. Body has `conditions[]`, `filters[]`, `actions[]`, `frequency`, `actionMatch`.
- **`GET/PUT/DELETE /api/0/projects/{org}/{project}/rules/{rule_id}/`** — One issue alert rule.
- **`GET/POST /api/0/organizations/{org}/alert-rules/`** — Metric alert rules. Body: `{"name","dataset","query","aggregate","timeWindow","thresholdType","triggers":[{"label","alertThreshold","actions":[...]}]}`.
- **`GET/PUT/DELETE /api/0/organizations/{org}/alert-rules/{rule_id}/`** — One metric alert rule.

## SDK keys & client config

- **`GET/POST /api/0/projects/{org}/{project}/keys/`** — Client keys (DSNs). Each has `dsn.public`, `dsn.secret`, `rateLimit`.
- **`GET/PUT/DELETE /api/0/projects/{org}/{project}/keys/{key_id}/`** — One key. PUT body: `{"isActive":bool,"rateLimit":{"count","window"}}`.

---

## Cross-cutting notes

**Slugs vs IDs.** Organizations and projects are addressed by **slug** in the URL. Issues, events,
rules, members are addressed by **numeric/hex ID**. Cross-org endpoints that filter by project
(`issues/`, `events/`, `stats_v2/`) accept either the **numeric project ID** or the slug in the
`project` param per current docs; pass the numeric ID for robustness across older self-hosted
versions. Fetch IDs from `/api/0/organizations/{org}/projects/`.

**Time filters.** `statsPeriod` (relative: `1h`, `24h`, `14d`, `90d`) and `start`/`end` (ISO-8601)
are mutually exclusive. Most endpoints default to 14 days. `start`/`end` unlocks ranges longer than
`statsPeriod`'s cap.

**Cursor pagination.** Every list endpoint returns a `Link` header (mechanics in `../SKILL.md`
section Pagination). Don't hand-construct cursors; follow the `rel="next"` URL verbatim.

**Token scopes.** Organization auth tokens can be scoped to specific permission sets. Common scopes:
`org:read`, `project:read`, `project:write`, `event:read`, `event:write`, `member:read`,
`alerts:read`, `alerts:write`.

**Destructive operations.** `DELETE` on issues is async and cannot be undone. Bulk PUT with `query=`
as the selector (instead of `id=`) affects every matching issue — double-check the query scope first
with a GET.
