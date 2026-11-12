---
name: asana-api
description: Read and manage Asana tasks, projects, sections, comments, and workspaces. Use this whenever the user wants to list or search tasks, create or update a task, complete a task, comment on a task, move tasks between projects or sections, look up a project or workspace, or ask "what's on my Asana list" — even if they don't say "API". Also use it for any app.asana.com URL or an Asana task/project gid. Always start from this skill when interacting with this service — its bundled scripts and recipes are the fastest path.
---

Asana's REST API is rooted at `https://app.asana.com/api/1.0`. Three things are true of every call:
every object is identified by a string **`gid`** (global id), every response wraps its payload in a
top-level `data` key, and write bodies wrap their fields in `data` too. Most reads return a
**compact** record (`gid`, `name`, `resource_type`) — ask for more with `opt_fields`.

Resources nest predictably: a **workspace** (an *organization* if it has one) holds **projects** and
**users**; a **project** holds **sections** and **tasks**; a **task** carries comments and activity
as **stories**, plus subtasks, tags, attachments, and custom fields.

## Request setup

Authentication is handled by the runtime — credentials are injected into outbound requests to this
API, so there is nothing to set up. Do not try to create, mint, refresh, or validate tokens or keys.
Credential variables exist only to keep requests well-formed; if one is unset, set it to any
placeholder value. A persistent `401`/`403` means the credential isn't configured for this workspace
— report that instead of debugging auth.

Requests use a bearer token. The base URL is fixed (not per-instance), but workspace/project/task
gids are real and part of the path:

```bash
export ASANA_TOKEN="placeholder"                 # injected by the runtime; any value works
export ASANA_BASE="https://app.asana.com/api/1.0"
```

Define a helper once per session:

```bash
asana() { curl -sS -H "Authorization: Bearer ${ASANA_TOKEN}" \
  -H "Accept: application/json" -H "Content-Type: application/json" "$@"; }
```

**Sanity check** — confirm the token works and find your workspace gids:

```bash
asana "${ASANA_BASE}/users/me?opt_fields=name,email,workspaces.name" \
  | jq '.data | {gid, name, email, workspaces: [.workspaces[]? | {gid, name}]}'
# 200 with your user + workspaces → wired up. 401 → credential not configured; report it.
```

## Response conventions

Three patterns repeat across every endpoint below — stated once so the recipes stay short:

- **The `data` envelope.** Reads return `{"data": ...}` (object or array); writes send
  `{"data": {...}}` and return the result under `data`. An error replaces `data` with `errors` (see
  Error handling). Project `.data`, and check `.errors` when it's missing.
- **`gid`, not name.** Everything is referenced by its string `gid` — resolve names to gids first
  (workspaces, projects, users, tags; recipe 9).
- **`opt_fields` for fields.** Compact records carry only `gid`, `name`, `resource_type`. Add a
  comma-separated `opt_fields` to expand, with dot-notation for relations
  (`assignee.name`, `memberships.section.name`); `gid` is always returned. On POST/PUT, nest options
  in an `options` object beside `data`.

## Core operations

### 1. List tasks (`scripts/asana_tasks.sh`)

Run through the bundled script (path is relative to this skill's directory): it GETs `/tasks`
filtered by project, tag, section, or assignee+workspace, sends an `opt_fields` list, follows
`next_page.offset` through every page, and emits TSV or JSONL.

```bash
scripts/asana_tasks.sh --project 1201234567890123 --limit 200
scripts/asana_tasks.sh --assignee me --workspace 1209876543210987 --completed-since now
```

- Exactly one selector is required: `--project GID`, `--tag GID`, `--section GID`, or
  `--assignee GID --workspace GID` (assignee needs a workspace). `--assignee me` resolves the caller
  via `/users/me`.
- `--completed-since WHEN` — ISO 8601, or `now` to show only incomplete tasks (omit to include all).
- `--fields LIST` — `opt_fields` to request. The TSV columns are fixed (gid, name, completed,
  assignee, due_on, permalink_url); extra fields appear only in `--json` output.
- `--limit N` caps tasks fetched (default 100, `0` = everything); `--page-size N` sets the
  per-request page (1-100, default 100). Fetched count and any truncation warning go to stderr.
- `--json` emits one raw task object per line instead of TSV.
- Exit codes: `0` success, `1` request failed / API error / bad arguments (the API's own
  `errors[].message` is printed to stderr).

If the script errors, read it — it's plain `curl` + `jq` — and debug against `references/api.md`.

### 2. Get one task

```bash
asana "${ASANA_BASE}/tasks/TASK_GID?opt_fields=name,notes,completed,assignee.name,due_on,projects.name,tags.name,parent.name,num_subtasks,custom_fields.name,custom_fields.display_value,permalink_url" \
  | jq '.data'
```

With no `opt_fields` you get only the compact record. Read a task's comments with recipe 5.

### 3. Create a task

Fields nest under `data`. One of `workspace`, `projects`, or `parent` is required (a standalone task
needs a `workspace`).

```bash
asana -X POST "${ASANA_BASE}/tasks" -d '{
  "data": {
    "name": "Draft the launch checklist",
    "notes": "Plain-text body. Use html_notes for rich text.",
    "workspace": "1209876543210987",
    "projects": ["1201234567890123"],
    "assignee": "me",
    "due_on": "2026-06-15",
    "followers": ["1200000000000001"]
  }
}' | jq '.data | {gid, name, permalink_url}'
```

`assignee` and `followers` take user gids (or `me`); `due_on` is a date, `due_at` an ISO 8601
timestamp. Use `html_notes` for rich text (Asana's HTML subset). Custom-field values go in
`custom_fields: {"FIELD_GID": value}`.

### 4. Update or complete a task

PUT replaces only the fields you send (still wrapped in `data`). You complete a task by setting
`completed` — there is no separate endpoint.

```bash
asana -X PUT "${ASANA_BASE}/tasks/TASK_GID" -d '{"data": {"completed": true}}' \
  | jq '.data | {gid, completed, completed_at}'
asana -X PUT "${ASANA_BASE}/tasks/TASK_GID" -d '{"data": {"name": "Revised", "due_on": "2026-07-01"}}'
```

Delete: `asana -X DELETE "${ASANA_BASE}/tasks/TASK_GID"` — returns an empty `data: {}`; the task
goes to the trash.

### 5. Comment on a task / read its activity (stories)

Stories are a task's comments plus system activity. Only comment stories can be created.

```bash
# add a comment
asana -X POST "${ASANA_BASE}/tasks/TASK_GID/stories" \
  -d '{"data": {"text": "Reproduced on main."}}' | jq '.data | {gid, created_at}'

# read comments only (filter out system activity client-side)
asana "${ASANA_BASE}/tasks/TASK_GID/stories?opt_fields=resource_subtype,text,created_by.name,created_at" \
  | jq '.data[] | select(.resource_subtype=="comment_added") | {by: .created_by.name, text, created_at}'
```

Use `html_text` instead of `text` for a rich-text comment.

### 6. Search tasks in a workspace (premium)

Advanced search lives at the workspace and is **premium-only**. It does **not** offset-paginate
(results are unstable, capped at 100) — narrow with filters, or sort by `created_at` and page
manually with `created_at.before`. For plain "tasks in a project / mine", prefer the list script
(recipe 1): it pages fully and works on free plans.

```bash
asana -G "${ASANA_BASE}/workspaces/WORKSPACE_GID/tasks/search" \
  --data-urlencode "text=launch" \
  --data-urlencode "assignee.any=me" \
  --data-urlencode "completed=false" \
  --data-urlencode "sort_by=modified_at" \
  --data-urlencode "opt_fields=name,assignee.name,due_on,permalink_url" \
  | jq '.data[] | {gid, name, due_on}'
```

### 7. Projects and sections

```bash
asana -G "${ASANA_BASE}/projects" --data-urlencode "workspace=WORKSPACE_GID" \
  --data-urlencode "archived=false" --data-urlencode "opt_fields=name,owner.name" \
  | jq '.data[] | {gid, name}'
asana "${ASANA_BASE}/projects/PROJECT_GID?opt_fields=name,notes,owner.name,members.name" | jq '.data'
asana "${ASANA_BASE}/projects/PROJECT_GID/sections?opt_fields=name" | jq '.data[] | {gid, name}'
```

### 8. Move a task between projects and sections

A task belongs to projects via *memberships*. Dedicated POSTs add, remove, or place it in a section.
Each returns an empty `data: {}` on success.

```bash
asana -X POST "${ASANA_BASE}/tasks/TASK_GID/addProject" \
  -d '{"data": {"project": "PROJECT_GID", "section": "SECTION_GID"}}'
asana -X POST "${ASANA_BASE}/tasks/TASK_GID/removeProject" -d '{"data": {"project": "PROJECT_GID"}}'
asana -X POST "${ASANA_BASE}/sections/SECTION_GID/addTask" -d '{"data": {"task": "TASK_GID"}}'
```

### 9. Find workspaces, users, and projects (gid lookup)

Everything is referenced by `gid` — resolve names to gids here.

```bash
asana "${ASANA_BASE}/workspaces?opt_fields=name,is_organization" | jq '.data[] | {gid, name}'
asana -G "${ASANA_BASE}/users" --data-urlencode "workspace=WORKSPACE_GID" \
  --data-urlencode "opt_fields=name,email" | jq '.data[] | {gid, name, email}'
asana "${ASANA_BASE}/users/me?opt_fields=name,email,workspaces.name" | jq '.data'
```

### 10. Subtasks, tags, and attachments

```bash
asana "${ASANA_BASE}/tasks/TASK_GID/subtasks?opt_fields=name,completed" | jq '.data[] | {gid, name}'
asana -X POST "${ASANA_BASE}/tasks/TASK_GID/subtasks" -d '{"data": {"name": "A subtask"}}' | jq '.data.gid'
asana "${ASANA_BASE}/workspaces/WORKSPACE_GID/tags?opt_fields=name" | jq '.data[] | {gid, name}'
asana -X POST "${ASANA_BASE}/tasks/TASK_GID/addTag" -d '{"data": {"tag": "TAG_GID"}}'
asana "${ASANA_BASE}/tasks/TASK_GID/attachments?opt_fields=name,download_url" | jq '.data[] | {gid, name}'
```

Upload an attachment with multipart form data (not JSON) — see `references/api.md`, section
Attachments. Set a custom field in a task PUT with
`{"data": {"custom_fields": {"FIELD_GID": value}}}`.

## Pagination

- **Offset token.** Collection GETs (`/tasks`, `/projects`, `/users`, `/stories`, ...) take `limit`
  (1-100) and return a `next_page` object when more remain: `{"offset": "...", "path": "...",
  "uri": "..."}`. Pass `next_page.offset` back as `?offset=...`; stop when `next_page` is `null`.
  The offset is **opaque** and expires — only reuse one the API handed you, never construct it.
  `scripts/asana_tasks.sh` does this for tasks.
- **No offset on search.** `/workspaces/{gid}/tasks/search` ignores `offset` and caps at 100
  unstable-ordered results — sort by `created_at` and page with `created_at.before` (recipe 6).
- Very large result sets (tens of thousands) can return `400` with a truncation message — narrow the
  query rather than retrying.

## Rate limits

Limits are per workspace + token, per minute:

- **150 requests/min** on free plans, **1500/min** on paid. Search is **60/min**.
- Concurrency: **50** simultaneous GETs, **15** simultaneous writes. Duplication/export jobs are
  capped at 5 concurrent per user.
- A separate cost-based limiter can reject expensive graph traversals; most callers never hit it.

On `429`, sleep the `Retry-After` seconds (default ~30 if absent) and retry with backoff — don't
tighten the poll interval.

## Error handling

Every error replaces `data` with `errors`: `{"errors": [{"message": "...", "help": "...", "phrase":
"..."}]}` (`phrase` appears only on 500s, for support). Check `.errors` before projecting `.data`.

- **`400`** — Bad request: missing/malformed parameter, a bad `data` envelope, or a result set too large to return. The `message` names the cause.
- **`401`** — Credential missing or rejected. Check `ASANA_TOKEN` is set at all (any value works). If it persists, the credential isn't configured for this workspace — report it.
- **`402`** — Payment required: the feature needs a premium org (e.g. task search, some custom-field operations).
- **`403`** — Forbidden: the token's user lacks access to that object.
- **`404`** — Not found: wrong `gid` or non-existent object; some private objects may also surface as `404` rather than `403`.
- **`429`** — Rate limited. Sleep per `Retry-After`, then retry with backoff.
- **`451`** — Unavailable for legal reasons (embargoed IP).
- **`5xx`** — Asana-side. Retry reads with backoff; quote `errors[].phrase` if you escalate.

## Going deeper

`references/api.md` has the fuller catalog — the complete task fields/memberships model,
`html_notes`/`html_text` markup, sections and reordering, dependencies, custom fields and enum
options, attachments (multipart upload), tags, teams and portfolios, project statuses, webhooks (the
`X-Hook-Secret` handshake), the batch API, and audit-log events. Read it for an endpoint not covered
above, or the exact body shape for a write.
