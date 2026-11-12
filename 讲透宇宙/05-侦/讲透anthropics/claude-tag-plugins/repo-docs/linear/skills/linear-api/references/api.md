# Linear GraphQL API — Reference

Single endpoint: `POST https://api.linear.app/graphql`. Headers:

```
Authorization: ${LINEAR_API_KEY}       # personal API key — NO "Bearer" prefix
Content-Type: application/json
```

(OAuth2 tokens use `Authorization: Bearer <token>` instead.)

Official docs: `https://linear.app/developers`. Schema reference:
`https://studio.apollographql.com/public/Linear-API/variant/current/schema/reference`.

## Table of contents

- [Query grammar](#query-grammar)
- [Filter operators](#filter-operators)
- [Issues](#issues)
- [Comments & reactions](#comments--reactions)
- [Teams & workflow states](#teams--workflow-states)
- [Projects & milestones](#projects--milestones)
- [Cycles](#cycles)
- [Labels](#labels)
- [Users & organization](#users--organization)
- [Documents & project updates](#documents--project-updates)
- [Attachments](#attachments)
- [Notifications & favorites](#notifications--favorites)
- [Webhooks](#webhooks)
- [Schema introspection](#schema-introspection)

---

## Query grammar

All list fields are **connections**: they take `first`/`after` (or `last`/`before`), `orderBy`, and
`filter`, and return `{ nodes [...], pageInfo { hasNextPage endCursor } }`.

```graphql
issues(
  first: 50              # page size, max 250
  after: "cursor"        # from pageInfo.endCursor
  orderBy: updatedAt     # createdAt | updatedAt
  filter: { ... }        # see Filter operators
  includeArchived: false
) { nodes { ... } pageInfo { hasNextPage endCursor } }
```

Connections expose only `edges`, `nodes`, and `pageInfo` — there is **no `totalCount`** on any
Linear connection type. To count, paginate and count `nodes`. Exception: the search payloads
(`searchIssues`, `searchProjects`, `searchDocuments`) do return `totalCount`.

Mutations take an `input` object and return `{ success, lastSyncId, <object> }`. Always check
`success`.

## Filter operators

Comparators wrap each field: `{ field: { op: value } }`.

- **`eq` / `neq`** (all) — `{ priority: { eq: 1 } }`
- **`in` / `nin`** (all) — `{ state: { type: { nin: ["completed","canceled"] } } }`
- **`lt` / `lte` / `gt` / `gte`** (number, date) — `{ createdAt: { gt: "2025-01-01" } }`
- **`contains` / `notContains`** (string) — `{ title: { contains: "crash" } }`
- **`containsIgnoreCase`** (string) — `{ title: { containsIgnoreCase: "Crash" } }`
- **`startsWith` / `endsWith`** (string) — `{ title: { startsWith: "Crash" } }`
- **`null`** (all) — `{ assignee: { null: true } }`, unassigned

Relation filters nest: `{ team: { key: { eq: "ENG" } } }`,
`{ assignee: { email: { eq: "a@b.c" } } }`.

Boolean logic: `{ and: [ {...}, {...} ] }`, `{ or: [ {...}, {...} ] }`. Top-level fields in one
filter object are implicitly AND'd.

Collection filters (on has-many relations): `{ labels: { some: { name: { eq: "bug" } } } }`,
`{ labels: { every: {...} } }`, `{ labels: { length: { eq: 0 } } }`.

## Issues

### Reads

- **`issue(id: "ENG-123")`** — Fetch one by UUID or human identifier.
- **`issues(filter, orderBy, first, after)`** — Workspace-wide list.
- **`searchIssues(term, first, after, filter, includeComments)`** — Full-text search.
- **`issueSearch(query, first, after)`** — Older search field, same idea.
- **`viewer { assignedIssues(...) createdIssues(...) }`** — Your issues.
- **`team(id) { issues(...) }`** — Per-team.
- **`project(id) { issues(...) }`** — Per-project.
- **`cycle(id) { issues(...) }`** — Per-cycle.

Key `Issue` fields: `id`, `identifier`, `number`, `title`, `description` (Markdown),
`descriptionState` (ProseMirror), `url`, `branchName` (suggested git branch), `priority` (0–4),
`priorityLabel`, `estimate`, `sortOrder`, `dueDate`, `slaStartedAt`, `createdAt`, `updatedAt`,
`completedAt`, `canceledAt`, `archivedAt`, `triagedAt`, `snoozedUntilAt`,
`state { id name type color position }`, `assignee`, `creator`, `subscribers`, `team`, `project`,
`projectMilestone`, `cycle`, `parent`, `children`, `labels`, `comments`, `attachments`, `relations`
(blocks / blockedBy / related / duplicate), `history`.

### Mutations

- **`issueCreate(input)`** — `teamId` (required), `title` (required), `description`, `priority`, `stateId`, `assigneeId`, `labelIds`, `projectId`, `cycleId`, `parentId`, `estimate`, `dueDate`, `subscriberIds`, `sortOrder`.
- **`issueUpdate(id, input)`** — Any subset of the above.
- **`issueDelete(id)`** — Soft delete (moves to trash).
- **`issueArchive(id)` / `issueUnarchive(id)`** — Archive / restore.
- **`issueBatchCreate(input: {issues: [...]})`** — Bulk create.
- **`issueBatchUpdate(ids, input)`** — Bulk update.
- **`issueAddLabel(id, labelId)` / `issueRemoveLabel(id, labelId)`** — Toggle one label.
- **`issueRelationCreate(input: {issueId, relatedIssueId, type})`** — `type` ∈ `blocks`, `duplicate`, `related`, `similar`.
- **`issueSubscribe(id, userId)` / `issueUnsubscribe(id, userId)`** — Subscriptions.

To move an issue to a state ("In Progress", "Done"), set `stateId` to the workflow state's UUID —
look it up per team via `team { states { nodes { id name type } } }`.

## Comments & reactions

- **`comment(id)`** — One comment.
- **`issue(id) { comments(first:) { nodes { id body user createdAt reactions } } }`** — Issue comments.
- **`commentCreate(input: {issueId, body, parentId})`** — `body` is Markdown. `parentId` for threaded replies.
- **`commentUpdate(id, input: {body})`** — Edit.
- **`commentDelete(id)`** — Delete.
- **`reactionCreate(input: {commentId | issueId | projectUpdateId, emoji})`** — Add 👍 etc. `emoji` is the shortcode (`"+1"`).
- **`reactionDelete(id)`** — Remove.

## Teams & workflow states

- **`teams(filter, first)`** — List teams.
- **`team(id)`** — By UUID **or key** (`team(id: "ENG")` works).
- **`team { id key name description icon color visibility cyclesEnabled defaultIssueState triageEnabled }`** — Settings. (`private` is deprecated — use `visibility`.)
- **`team { states { nodes { id name type color position } } }`** — Workflow states. `type` ∈ `backlog`, `unstarted`, `started`, `completed`, `canceled`, `triage`, `duplicate`.
- **`team { members { nodes } memberships { nodes } }`** — Team membership.
- **`team { labels { nodes } }`** — Team-scoped labels.
- **`team { activeCycle cycles(filter, first) }`** — Cycle accessors (`currentCycle` / `previousCycle` do not exist).
- **`teamCreate(input)` / `teamUpdate(id, input)` / `teamDelete(id)`** — Manage teams.
- **`workflowStateCreate(input: {teamId, name, type, color, position})`** — New state.
- **`workflowStateUpdate(id, input)` / `workflowStateArchive(id)`** — Manage states.

## Projects & milestones

- **`projects(filter, first)`** — List. `ProjectFilter` supports `status`, `health`, `lead`, `members`, `accessibleTeams`, date fields.
- **`project(id)`** — One project.
- **`project { id name description status { name type } health progress startDate targetDate completedAt url color icon lead members teams issues projectMilestones projectUpdates documents }`** — Key fields. `status.type` ∈ `backlog`, `planned`, `started`, `paused`, `completed`, `canceled`. `health` ∈ `onTrack`, `atRisk`, `offTrack`. The old string `state` field is deprecated on the `Project` type — use `status`.
- **`projectCreate(input: {name, teamIds, description, statusId, leadId, memberIds, startDate, targetDate})`** — Create.
- **`projectUpdate(id, input)`** — Update.
- **`projectDelete(id)` / `projectUnarchive(id)`** — Trash / restore (`projectArchive` is deprecated — use `projectDelete`).
- **`projectMilestone(id)` / `project { projectMilestones }`** — Milestones.
- **`projectMilestoneCreate(input: {projectId, name, targetDate})`** — Create milestone.

## Cycles

- **`cycles(filter, first)`** — List.
- **`cycle(id)`** — One cycle.
- **`cycle { id number name startsAt endsAt completedAt progress scopeHistory completedScopeHistory issueCountHistory issues uncompletedIssuesUponClose }`** — Key fields.
- **`team { activeCycle }`** — The running cycle.
- **`cycleCreate(input: {teamId, startsAt, endsAt, name})`** — Create (usually auto-created).
- **`cycleUpdate(id, input)`** — Rename, edit dates.

## Labels

- **`issueLabels(filter, first)`** — Workspace labels (team-scoped if `team` filter given).
- **`issueLabel(id)`** — One.
- **`issueLabelCreate(input: {name, color, teamId, parentId, description})`** — `teamId` null = workspace label. `parentId` for label groups.
- **`issueLabelUpdate(id, input)` / `issueLabelDelete(id)`** — Manage.

## Users & organization

- **`viewer`** — The authenticated user. Fields: `id`, `name`, `displayName`, `email`, `avatarUrl`, `active`, `admin`, `isMe`, `teams`, `assignedIssues`, `createdIssues`, `teamMemberships`.
- **`users(filter, first, includeDisabled)`** — Workspace members.
- **`user(id)`** — One user.
- **`organization`** — Workspace. Fields: `id`, `name`, `urlKey`, `logoUrl`, `subscription`, `userCount`, `createdIssueCount`, `periodUploadVolume`, `teams`, `users`, `labels`, `templates`, `integrations`.
- **`userSettings`** — Your preferences, notification settings, etc.

## Documents & project updates

- **`documents(filter, first)` / `document(id)`** — Project/team docs. `content` is Markdown.
- **`documentCreate(input: {title, content, projectId | issueId})`** — Create.
- **`documentUpdate(id, input)` / `documentDelete(id)`** — Manage.
- **`projectUpdates(filter)` / `projectUpdate(id)`** — Status-update posts. Fields: `body`, `health`, `user`, `project`, `createdAt`.
- **`projectUpdateCreate(input: {projectId, body, health})`** — Post an update.
- **`initiatives(filter)` / `initiative(id)`** — Cross-project groupings.

## Attachments

- **`attachment(id)` / `attachmentsForURL(url)`** — Look up.
- **`issue(id) { attachments { nodes { id title subtitle url metadata sourceType } } }`** — On an issue.
- **`attachmentCreate(input: {issueId, title, subtitle, url, iconUrl, metadata})`** — Link an external URL (a PR, a doc, a ticket). `url` is unique per issue — creating twice updates.
- **`attachmentLinkURL(issueId, url, title)`** — Shorthand for the above.
- **`attachmentLinkGitHubPR(issueId, url)`** — Typed link for GitHub PRs. Also `attachmentLinkGitLabMR`, `attachmentLinkSlack`, `attachmentLinkZendesk`, etc.
- **`attachmentDelete(id)`** — Remove.
- **`fileUpload(contentType, filename, size)`** — Get a pre-signed upload URL for binary attachments. Returns `{ uploadFile { uploadUrl assetUrl headers } }` — PUT the bytes to `uploadUrl`, then reference `assetUrl`.

## Notifications & favorites

- **`notifications(filter, first)`** — Your inbox. Fields on `IssueNotification`: `type`, `readAt`, `snoozedUntilAt`, `issue`, `comment`, `actor`.
- **`notificationMarkReadAll(input)`** — Mark all read.
- **`notificationUpdate(id, input: {readAt, snoozedUntilAt})`** — Mark one read / snooze.
- **`notificationArchive(id)`** — Archive.
- **`favorites(first)`** — Your starred issues/projects/etc.
- **`favoriteCreate(input: {issueId | projectId | cycleId | labelId | documentId})`** — Star.
- **`favoriteDelete(id)`** — Unstar.

## Webhooks

- **`webhooks(first)` / `webhook(id)`** — List / get.
- **`webhookCreate(input: {url, teamId, allPublicTeams, resourceTypes, secret, enabled, label})`** — `resourceTypes` ∈ `Issue`, `Comment`, `Project`, `Cycle`, `IssueLabel`, `Reaction`, `ProjectUpdate`, `Document`, `Attachment`, `User`.
- **`webhookUpdate(id, input)` / `webhookDelete(id)`** — Manage.

Deliveries are `POST` with a JSON body
`{ action, type, actor, data, updatedFrom, url, createdAt, organizationId, webhookId, webhookTimestamp }`.
Verify the `Linear-Signature` header (hex HMAC-SHA256 of the raw body with `secret`).

## Schema introspection

Discover any type's fields:

```graphql
{ __type(name: "Issue") { fields { name type { name kind ofType { name } } } } }
```

List all queryable root fields:

```graphql
{ __schema { queryType { fields { name description } } mutationType { fields { name } } } }
```

---

## Cross-cutting notes

**IDs.** Mutations always want UUIDs. `issue(id:)` and `team(id:)` accept human-readable identifiers
as a convenience, but `issueId` / `teamId` inputs do not. Fetch the UUID first.

**Markdown everywhere.** `Issue.description`, `Comment.body`, `Document.content`,
`ProjectUpdate.body` are all Markdown. Linear also stores a ProseMirror `descriptionState` — write
Markdown and let Linear convert.

**Soft deletes.** `*Delete` mutations trash (recoverable for 30 days); `*Archive` archives
(recoverable indefinitely). Use `includeArchived: true` on connections to see archived records.

**`lastSyncId`.** Mutations return a `lastSyncId` you can use with Linear's sync APIs for
incremental replication — ignore it for one-off calls.
