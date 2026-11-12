---
name: linear-api
description: Read and manage Linear issues, projects, cycles, teams, comments, and labels. Use this whenever the user wants to list their issues, search issues, create or update an issue, move an issue between states, add a comment, check a project or cycle, look up a team, or ask "what's on my plate in Linear" — even if they don't say "API" or "GraphQL". Also use it for any linear.app URL or an issue identifier like "ENG-123". Always start from this skill when interacting with this service — its bundled scripts and recipes are the fastest path.
---

Linear has a **single GraphQL endpoint** — there is no REST API. Every read is a `query`, every
write is a `mutation`, and everything goes to one URL. Don't look for `/api/v1/issues`-style paths;
they don't exist.

```
POST https://api.linear.app/graphql
```

Two ID systems coexist:
- **UUID** (`id`) — what the API uses everywhere for lookups and mutations.
- **Identifier** (`identifier`, e.g. `ENG-123`) — the human-readable key shown in the UI. You can
  fetch an issue by identifier with `issue(id: "ENG-123")` (Linear accepts both).

## Request setup

Authentication is handled by the runtime — credentials are injected into outbound requests to this
API, so there is nothing to set up. Do not try to create, mint, refresh, or validate tokens or keys.
Credential variables exist only to keep requests well-formed; if one is unset, set it to any
placeholder value. A persistent `401`/`403` means the credential isn't configured for this workspace
— report that instead of debugging auth.

Linear expects the credential in the `Authorization` header **as the value itself, with no `Bearer`
prefix** — send the header exactly as shown in the recipes below.

```bash
export LINEAR_API_KEY="placeholder"    # injected by the runtime; any value works
```

**Sanity check** — confirm the workspace is wired up and see who the configured identity is:

```bash
curl -sS "https://api.linear.app/graphql" \
  -H "Authorization: ${LINEAR_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ viewer { id name email } }"}' | jq .
```

Define a helper once per session so you don't repeat the boilerplate. It takes a query string and an
optional variables JSON object:

```bash
linear_gql() {
  local query="$1" vars="${2:-null}"
  jq -n --arg q "$query" --argjson v "$vars" '{query:$q, variables:$v}' | \
  curl -sS "https://api.linear.app/graphql" \
    -H "Authorization: ${LINEAR_API_KEY}" \
    -H "Content-Type: application/json" \
    -d @-
}
```

**Always check `.errors` before trusting `.data`** — GraphQL returns HTTP `200` even on failures:

```bash
linear_gql '{ viewer { id } }' | jq 'if .errors then .errors else .data end'
```

## Core operations

### 1. Who am I / what's assigned to me

```bash
linear_gql '{
  viewer {
    id name email
    assignedIssues(first: 25, orderBy: updatedAt, filter: {state: {type: {nin: ["completed","canceled"]}}}) {
      nodes { identifier title state { name type } priority team { key } updatedAt }
    }
  }
}' | jq '.errors // .data.viewer'
```

Priority: `0` = no priority, `1` = Urgent, `2` = High, `3` = Medium, `4` = Low.

### 2. Search issues

```bash
linear_gql 'query($q: String!) {
  searchIssues(term: $q, first: 25) {
    nodes { identifier title state { name } assignee { name } team { key } priority url }
  }
}' '{"q": "login crash"}' | jq '.data.searchIssues.nodes'
```

### 3. Get one issue (by identifier or UUID)

```bash
linear_gql 'query($id: String!) {
  issue(id: $id) {
    id identifier title description url priority estimate
    state { name type }
    assignee { name email }
    creator { name }
    team { id key name }
    project { id name }
    cycle { id number name }
    labels { nodes { name color } }
    comments(first: 50) { nodes { body user { name } createdAt } }
    children { nodes { identifier title state { name } } }
    parent { identifier title }
    createdAt updatedAt dueDate
  }
}' '{"id": "ENG-123"}' | jq '.data.issue'
```

### 4. List and filter issues (`scripts/linear_issues.sh`)

List issues through the bundled script (path is relative to this skill's directory): it builds an
`IssueFilter` from flags, pages through `pageInfo.endCursor`, checks `.errors` on every response,
and emits TSV or JSONL.

```bash
scripts/linear_issues.sh --team ENG --state-type started --assignee me --limit 100
```

- All filter flags are optional and combine (AND): `--team KEY`, `--state NAME`, `--state-type
  TYPE` (one of `backlog` `unstarted` `started` `completed` `canceled` `triage` `duplicate`),
  `--assignee EMAIL` (or `me` — resolves the viewer id first), `--label NAME`. Instance specifics come from
  `LINEAR_API_KEY` above.
- `--query TEXT` does a case-insensitive substring match over title and description; combined with
  other flags it's wrapped as `and: [ {…flags}, {or: [title, description]} ]`.
- `--limit N` caps total issues fetched (default 50, `0` = everything); `--page-size N` (max 100)
  sets the per-page size; `--json` emits one JSON object per issue instead of TSV with a header
  (`identifier`, `title`, `state`, `assignee`, `updatedAt`, `url`). Row counts go to stderr.
- Exit codes: `0` success, `1` request failed, GraphQL `.errors`, or bad arguments — the API's own
  message and `extensions.code` are on stderr.

If the script errors, read it — it's plain `curl` + `jq` — and debug against `references/api.md`.

For filter shapes the flags don't cover — comparators like `lte`/`gte`, `or` groups, nested
`some`/`every` — pass the `filter` object yourself with `linear_gql`:

```bash
linear_gql 'query($teamKey: String!) {
  issues(first: 50, orderBy: updatedAt, filter: {
    team: { key: { eq: $teamKey } }
    priority: { lte: 2, gte: 1 }
    state: { type: { nin: ["completed", "canceled"] } }
  }) { nodes { identifier title priority state { name } assignee { name } } }
}' '{"teamKey": "ENG"}' | jq '.data.issues.nodes'
```

Full filter grammar: `references/api.md`, section Filter operators.

### 5. Create an issue

You need the team's UUID (not its key). Get it once (recipe 8), then:

```bash
linear_gql 'mutation($input: IssueCreateInput!) {
  issueCreate(input: $input) {
    success
    issue { id identifier url }
  }
}' '{"input": {
  "teamId": "TEAM_UUID",
  "title": "Crash on empty input",
  "description": "Steps to reproduce…\n\n1. …",
  "priority": 2,
  "assigneeId": "USER_UUID",
  "labelIds": ["LABEL_UUID"]
}}' | jq '.data.issueCreate'
```

`description` is **Markdown**.

### 6. Update an issue (change state, assignee, priority, …)

```bash
linear_gql 'mutation($id: String!, $input: IssueUpdateInput!) {
  issueUpdate(id: $id, input: $input) {
    success
    issue { identifier state { name } assignee { name } }
  }
}' '{"id": "ENG-123", "input": {"stateId": "STATE_UUID", "priority": 1}}' | jq '.data.issueUpdate'
```

To move to "Done" / "In Progress" / etc. you need the workflow **state UUID**, which is per-team
(recipe 8 shows how to list them).

### 7. Comment on an issue

```bash
linear_gql 'mutation($input: CommentCreateInput!) {
  commentCreate(input: $input) { success comment { id url } }
}' '{"input": {"issueId": "ISSUE_UUID", "body": "Reproduced on main — looking into it."}}' \
  | jq '.data.commentCreate'
```

`body` is Markdown. `issueId` must be the UUID, not the identifier — fetch it with recipe 3 first.

### 8. Discover teams, workflow states, labels, members

You'll need these UUIDs for create/update mutations.

```bash
linear_gql '{
  teams {
    nodes {
      id key name
      states { nodes { id name type position } }
      labels { nodes { id name color } }
      members { nodes { id name email } }
    }
  }
}' | jq '.data.teams.nodes'
```

State `type` ∈ `backlog`, `unstarted`, `started`, `completed`, `canceled`, `triage`, `duplicate`.

### 9. Projects and cycles

```bash
linear_gql '{
  projects(first: 25, orderBy: updatedAt, filter: {status: {type: {neq: "completed"}}}) {
    nodes {
      id name description progress targetDate url
      status { name type }
      lead { name }
      teams { nodes { key } }
      issues(first: 5) { nodes { identifier title state { name } } }
    }
  }
}' | jq '.data.projects.nodes'

# current cycle for a team
linear_gql 'query($teamId: String!) {
  team(id: $teamId) {
    activeCycle {
      id number name startsAt endsAt progress
      issues { nodes { identifier title state { name } assignee { name } } }
    }
  }
}' '{"teamId": "TEAM_UUID"}' | jq '.data.team.activeCycle'
```

Connections have no `totalCount` field — to count issues, paginate and count `nodes`, or read an
aggregate field like `team { issueCount }`. Exception: the search payloads (`searchIssues`,
`searchProjects`, `searchDocuments`) do return `totalCount`.

### 10. Recent activity across the workspace

```bash
linear_gql '{
  issues(first: 25, orderBy: updatedAt) {
    nodes { identifier title state { name } assignee { name } team { key } updatedAt }
  }
}' | jq '.data.issues.nodes'
```

## Pagination

Every list field (`issues`, `nodes`, `projects`, `comments`, …) is a **connection** with cursor
pagination. The response carries `pageInfo`:

```bash
linear_gql 'query($cursor: String) {
  issues(first: 50, after: $cursor, orderBy: createdAt) {
    pageInfo { hasNextPage endCursor }
    nodes { identifier title }
  }
}' '{"cursor": null}' | jq '.data.issues'
```

Loop: pass `pageInfo.endCursor` as `$cursor`, stop when `hasNextPage` is `false`. Also stop (and
print the body) if the response has `.errors` or the extracted cursor is empty or the literal string
`null` — otherwise an error envelope loops forever. Always bound the loop with a max page count.
`first` caps at **250** per page (default 50). For reverse pagination use `last` / `before`.

## Rate limits

Linear enforces **per-user request limits** and **complexity limits** (roughly proportional to how
many nodes a query could touch). Every response carries:

```
X-RateLimit-Requests-Limit / -Remaining / -Reset
X-Complexity
X-RateLimit-Complexity-Limit / -Remaining / -Reset
```

API-key auth gets 5,000 requests/hour and 3,000,000 complexity points/hour (OAuth apps: 5,000
requests and 2,000,000 points per user per hour); a single query may not exceed 10,000 points. When
you're over, Linear returns **HTTP `400`** (not `429`) with
`errors[].extensions.code: "RATELIMITED"`. The `-Reset` headers are **UTC epoch milliseconds** —
works on both BSD/macOS and GNU date:

```bash
sleep $(( reset_ms / 1000 - $(date +%s) + 1 ))   # reset_ms from X-RateLimit-Requests-Reset
```

To lower complexity, request fewer fields, cap `first:`, and don't deeply nest connections you don't
need (e.g. don't select `comments` on every issue in a list).

## Error handling

GraphQL returns HTTP `200` for most application errors — **always check the body's `errors[]`**.

- **HTTP `400` + `code: "GRAPHQL_VALIDATION_FAILED"`** — Schema validation failed (unknown field/type). `errors[].message` names the bad field — fix the query, don't debug quoting.
- **HTTP `500` + `code: "GRAPHQL_VALIDATION_FAILED"`** — GraphQL **syntax** error (unbalanced braces, etc.). `errors[].message` shows the parse position.
- **HTTP `401`** — Bad or missing API key. Check `LINEAR_API_KEY`. Personal keys go in `Authorization:` with **no** `Bearer` prefix.
- **HTTP `400` + `code: "RATELIMITED"`** — Rate or complexity limit hit. Sleep until `X-RateLimit-…-Reset` (epoch **ms**), retry; or simplify the query (fewer fields, smaller `first:`).
- **`errors[].extensions.code: "INVALID_INPUT"` / `"INPUT_ERROR"`** — Validation failed. `message` names the bad field. Common: passing a key (`ENG`) where a UUID is required, or a query over the 10,000-point complexity cap.
- **`errors[].extensions.code: "ENTITY_NOT_FOUND"`** — ID doesn't exist or not visible. Check the ID. API-key scope is workspace-wide but respects team/project access.
- **`errors[].message: "Cannot query field …"`** — Typo or schema mismatch. Field doesn't exist. Check spelling; use introspection (`references/api.md`).

Mutations return a `success` boolean even when HTTP and `errors` are clean — check it before
assuming the write landed.

## Going deeper

`references/api.md` has the fuller catalog: all major object types and their fields, the filter
operator grammar, webhook config, file attachments, reactions, notifications, favorites,
workspace/organization queries, and schema introspection. Read it when you need an object or
mutation not covered above, or when you need the exact input shape for a create/update.
