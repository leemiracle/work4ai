# Asana REST API — Endpoint Reference

All endpoints are rooted at `https://app.asana.com/api/1.0`. Every request carries
`Authorization: Bearer ${ASANA_TOKEN}` (the value is injected by the runtime — a placeholder is
fine) and `Accept: application/json`; write requests add `Content-Type: application/json`.

Reads return `{"data": ...}`; writes send `{"data": {...}}` and may add an `{"options": {...}}`
sibling (`opt_fields`, `opt_pretty`). Errors return `{"errors": [...]}`. Objects are keyed by string
`gid`. Compact records carry only `gid`, `name`, `resource_type` — expand with `opt_fields`.

Official docs: `https://developers.asana.com/reference/rest-api-reference`.

## Table of contents

- [Users & workspaces](#users--workspaces)
- [Projects & sections](#projects--sections)
- [Tasks](#tasks)
- [Task search](#task-search)
- [Stories (comments & activity)](#stories-comments--activity)
- [Subtasks & dependencies](#subtasks--dependencies)
- [Tags](#tags)
- [Attachments](#attachments)
- [Custom fields](#custom-fields)
- [Teams & portfolios](#teams--portfolios)
- [Webhooks](#webhooks)
- [Batch API](#batch-api)
- [Audit log events](#audit-log-events)
- [Cross-cutting notes](#cross-cutting-notes)

---

## Users & workspaces

- **`GET /users/me`** — The authenticated user. Add `opt_fields=name,email,workspaces.name` to get the workspaces they belong to.
- **`GET /users`** — Users in a workspace. Params: `workspace` (required), `opt_fields`.
- **`GET /users/{user_gid}`** — One user. `user_gid` may be `me` or an email address.
- **`GET /workspaces`** — Workspaces and organizations the caller belongs to.
- **`GET /workspaces/{workspace_gid}`** — One workspace. `is_organization` distinguishes an org from a bare workspace.
- **`GET /workspaces/{workspace_gid}/users`** — Members of a workspace.

## Projects & sections

- **`GET /projects`** — List. Params: `workspace` or `team`, `archived` (bool), `opt_fields`.
- **`GET /projects/{project_gid}`** — One project: `name`, `notes`, `owner`, `members`, `current_status_update`, `due_on`, `public`, `color`.
- **`POST /projects`** — Create. Body `data`: `name`, `workspace` (or `team`), `notes`, `public`, `color`, `default_view`.
- **`PUT /projects/{project_gid}`** — Update (send only changed fields under `data`).
- **`DELETE /projects/{project_gid}`** — Delete the project.
- **`GET /projects/{project_gid}/tasks`** — Tasks in a project (offset-paginated); same rows as `GET /tasks?project=`.
- **`GET /projects/{project_gid}/sections`** — Sections, in board/list order.
- **`POST /projects/{project_gid}/sections`** — Create a section. Body `data`: `name`, optional `insert_before`/`insert_after`.
- **`GET /sections/{section_gid}`** — One section. **`PUT`** to rename, **`DELETE`** to remove.
- **`POST /sections/{section_gid}/addTask`** — Move a task into the section. Body `data`: `task`, optional `insert_before`/`insert_after`.
- **`GET /projects/{project_gid}/project_statuses`** — Status updates posted on a project.

## Tasks

- **`GET /tasks`** — Multiple tasks. Requires `project` OR `tag` OR `section` OR (`assignee` + `workspace`). Optional `completed_since`, `modified_since`, `opt_fields`. `scripts/asana_tasks.sh` drives this.
- **`GET /tasks/{task_gid}`** — One task; expand with `opt_fields`.
- **`POST /tasks`** — Create. Body `data` requires `workspace` OR `projects` OR `parent`, plus any of `name`, `notes`/`html_notes`, `assignee`, `due_on`/`due_at`, `start_on`, `followers`, `custom_fields`.
- **`PUT /tasks/{task_gid}`** — Update or complete (`{"data":{"completed":true}}`); replaces only sent fields.
- **`DELETE /tasks/{task_gid}`** — Delete (moves the task to the trash).
- **`POST /tasks/{task_gid}/addProject`** — Add to a project. Body `data`: `project`, optional `section`, `insert_before`/`insert_after`.
- **`POST /tasks/{task_gid}/removeProject`** — Remove from a project. Body `data`: `project`.
- **`POST /tasks/{task_gid}/addFollowers`** / **`POST /tasks/{task_gid}/removeFollowers`** — Body `data`: `followers` (user gids).
- **`POST /tasks/{task_gid}/setParent`** — Re-parent a task. Body `data`: `parent`, optional positioning.
- **`GET /tasks/{task_gid}/projects`** — Projects a task belongs to.

Key task fields (request via `opt_fields`): `name`, `notes`, `html_notes`, `completed`,
`completed_at`, `assignee`, `assignee_status`, `due_on`, `due_at`, `start_on`, `projects`,
`memberships` (project + section), `parent`, `num_subtasks`, `tags`, `custom_fields`,
`dependencies`, `dependents`, `followers`, `permalink_url`, `created_at`, `modified_at`.

## Task search

- **`GET /workspaces/{workspace_gid}/tasks/search`** — Advanced search, **premium only**. Filters: `text`, `assignee.any`/`.not`, `projects.any`/`.all`/`.not`, `sections.any`, `tags.any`, `completed`, `due_on`/`due_on.before`/`.after`, `created_at.*`, `modified_at.*`, `is_subtask`, and custom-field predicates `custom_fields.{gid}.*`. Sort: `sort_by` (`due_date`, `created_at`, `completed_at`, `modified_at`, `likes`), `sort_ascending`. No offset pagination; max 100 unstable-ordered results — page manually by sorting on `created_at` and adding `created_at.before`.

## Stories (comments & activity)

- **`GET /tasks/{task_gid}/stories`** — Comments and system activity (offset-paginated). Each story has `type` (`comment`/`system`), `resource_subtype` (e.g. `comment_added`), `text`/`html_text`, `created_by`, `created_at`.
- **`POST /tasks/{task_gid}/stories`** — Add a comment. Body `data`: `text` (plain) or `html_text` (rich). Only comment stories can be created; returns `201`.
- **`GET /stories/{story_gid}`** — One story.
- **`PUT /stories/{story_gid}`** — Edit your own comment. **`DELETE /stories/{story_gid}`** — delete it.

## Subtasks & dependencies

- **`GET /tasks/{task_gid}/subtasks`** — Subtasks of a task.
- **`POST /tasks/{task_gid}/subtasks`** — Create a subtask. Body `data`: `name`, etc. (inherits the parent's workspace).
- **`POST /tasks/{task_gid}/addDependencies`** / **`addDependents`** — Body `data`: `dependencies`/`dependents` (task gids). `removeDependencies`/`removeDependents` are the counterparts.

## Tags

- **`GET /workspaces/{workspace_gid}/tags`** — Tags in a workspace.
- **`POST /tags`** — Create. Body `data`: `name`, `workspace`.
- **`GET /tasks/{task_gid}/tags`** — A task's tags.
- **`POST /tasks/{task_gid}/addTag`** / **`POST /tasks/{task_gid}/removeTag`** — Body `data`: `tag` (gid).
- **`GET /tags/{tag_gid}/tasks`** — Tasks carrying a tag.

## Attachments

- **`GET /tasks/{task_gid}/attachments`** — Attachments on a task (`name`, `download_url`, `view_url`, `host`).
- **`GET /attachments/{attachment_gid}`** — One attachment's metadata.
- **`POST /attachments`** — Upload. Use `multipart/form-data`, **not** JSON: `-F "parent=TASK_GID" -F "file=@/path/to/file"`. To attach an external link instead, send form fields `resource_subtype=external`, `parent`, `url`, `name`.

## Custom fields

- **`GET /workspaces/{workspace_gid}/custom_fields`** — Custom fields defined in a workspace.
- **`GET /custom_fields/{custom_field_gid}`** — One field, including `enum_options`.
- **`POST /custom_fields/{custom_field_gid}/enum_options`** — Add an enum option.
- Set values on a task via `PUT /tasks/{gid}` with `data.custom_fields` = `{"{field_gid}": value}` — `value` is a string/number, an enum-option `gid`, or `null` to clear.

## Teams & portfolios

- **`GET /organizations/{workspace_gid}/teams`** — Teams in an organization.
- **`GET /users/{user_gid}/teams`** — A user's teams. Param: `organization` (required).
- **`GET /teams/{team_gid}`** — One team. **`GET /teams/{team_gid}/projects`** — its projects.
- **`GET /portfolios`** — Portfolios. Params: `workspace`, `owner` (both required).
- **`GET /portfolios/{portfolio_gid}/items`** — Projects/portfolios inside a portfolio.

## Webhooks

- **`POST /webhooks`** — Create. Body `data`: `resource` (gid to watch), `target` (your HTTPS URL), optional `filters`. Asana sends a handshake `POST` to `target` with an `X-Hook-Secret` header — echo that header back with `200` to confirm. Later deliveries carry `X-Hook-Signature` (HMAC-SHA256 of the body).
- **`GET /webhooks`** — List. Param: `workspace` (required).
- **`GET /webhooks/{webhook_gid}`** — One webhook. **`DELETE /webhooks/{webhook_gid}`** — remove it.

## Batch API

- **`POST /batch`** — Up to 10 sub-requests in one call. Body `data.actions[]`: each is `{relative_path, method, data?, options?}`, with `relative_path` rooted at `/api/1.0`. Returns an array of `{status_code, body, headers}` in request order. Each action counts as a separate request against the standard per-minute rate limiter and the concurrent request limiter (a 10-action batch consumes 10 requests); the whole batch returns `429` if any action would exceed limits.

## Audit log events

- **`GET /workspaces/{workspace_gid}/audit_log_events`** — Organization audit trail (Enterprise). Params: `start_at`, `end_at`, `event_type`, `actor_type`, `actor_gid`, `resource_gid`. Streams via `next_page` even when momentarily empty.

---

## Cross-cutting notes

**The `data` envelope.** Reads return `{"data": ...}`; writes send `{"data": {...}}` and return the
result under `data`. Errors return `{"errors": [{"message","help","phrase"}]}` with no `data`.
Always read `.data` (or check `.errors`), never the top level.

**`gid`, not name or `id`.** Resources are referenced by their string `gid`; the legacy numeric `id`
is gone. Resolve names to gids via the list endpoints (workspaces, projects, users, tags) before
referencing them.

**`opt_fields` / `opt_pretty`.** Responses are *compact* (`gid`, `name`, `resource_type`) unless you
pass `opt_fields` — a comma-separated list using dot-notation for relations (`assignee.name`,
`memberships.section.name`) and a `(a|b)` group operator. `gid` is always present. On GET, append to
the query string; on POST/PUT, nest under an `options` object beside `data`. `opt_pretty=true`
indents the JSON (development only).

**Dates.** `due_on` and `start_on` are dates (`YYYY-MM-DD`); `due_at` is an ISO 8601 timestamp.
`completed_since` and `modified_since` accept ISO 8601 or the literal `now`.

**Rich text.** `html_notes` (tasks) and `html_text` (stories) use Asana's HTML subset — a restricted
tag set wrapped in a single `<body>…</body>`. Plain `notes`/`text` are unformatted.

**`me`.** Most user-valued params accept the literal `me` for the authenticated user
(`assignee=me`, `assignee.any=me`).

**Pagination & limits.** Collection GETs page via `limit` (1-100) plus an opaque `offset` from
`next_page` (see `SKILL.md`, Pagination). Search does not paginate. Rate limits are per
workspace + token: 150/min free, 1500/min paid, 60/min for search, plus a cost-based limiter; `429`
carries `Retry-After`.
