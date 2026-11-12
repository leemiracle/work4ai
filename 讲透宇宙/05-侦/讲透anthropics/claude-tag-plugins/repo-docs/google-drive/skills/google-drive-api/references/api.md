# Google Drive API v3 — Endpoint Reference

All requests go to `https://www.googleapis.com/drive/v3/` (or `/upload/drive/v3/` for content
uploads) with the header:

```
Authorization: Bearer ${GOOGLE_ACCESS_TOKEN}
Content-Type: application/json          # on any request with a JSON body
```

Official docs: `https://developers.google.com/workspace/drive/api/reference/rest/v3`.

**Every request should pass `fields=`** to select exactly the response fields you need — the default
field set is minimal. Use `fields=*` only when exploring, never in production loops. For
shared-drive files, pass `supportsAllDrives=true` on per-file calls that accept it
(get/update/copy/delete/download); `files.export` does not take the parameter.

## Table of contents

- [About & identity](#about--identity)
- [Files](#files)
- [Search query language](#search-query-language)
- [Export MIME types](#export-mime-types)
- [Uploads](#uploads)
- [Permissions](#permissions)
- [Comments & replies](#comments--replies)
- [Revisions](#revisions)
- [Shared drives](#shared-drives)
- [Changes](#changes)

---

## About & identity

- **`GET /about`** — Current user, storage quota, supported import/export formats. Useful params: `fields=user,storageQuota,exportFormats,importFormats`.

## Files

- **`GET /files`** — List / search. Params: `q`, `fields`, `orderBy`, `pageSize` (≤100; larger values are clamped), `pageToken`, `corpora` (`user` | `drive` | `allDrives` | `domain`), `driveId`, `includeItemsFromAllDrives`, `supportsAllDrives`, `spaces` (`drive` | `appDataFolder`).
- **`GET /files/{fileId}`** — File metadata. Params: `fields`, `supportsAllDrives`, `acknowledgeAbuse`. Add `?alt=media` to download binary content.
- **`GET /files/{fileId}/export`** — Export a Google Workspace file to another format. Param: `mimeType` (required). Max 10 MB.
- **`POST /files/{fileId}/download`** — Newer long-running-operation download: returns an `Operation` to poll, works for blobs and for exporting Workspace files (params: `mimeType`, `revisionId`). Prefer `?alt=media` / `export` for synchronous downloads.
- **`POST /files`** — Create a file (metadata-only). Body is a File resource: `name`, `mimeType`, `parents[]`, `description`, `properties{}`, `appProperties{}`. Use the `/upload` host to include content.
- **`PATCH /files/{fileId}`** — Update metadata. Body: File resource fields to change. Params: `addParents`, `removeParents`, `supportsAllDrives`. Content update uses the `/upload` host.
- **`POST /files/{fileId}/copy`** — Copy a file. Body: File resource for the copy (usually `name`, `parents[]`). Works on Workspace files too.
- **`DELETE /files/{fileId}`** — Permanently delete. Bypasses trash. Prefer `PATCH {"trashed": true}`.
- **`DELETE /files/trash`** — Empty the user's trash.
- **`GET /files/generateIds`** — Pre-allocate file IDs for later create calls. Params: `count`, `space`, `type`.
- **`POST /files/{fileId}/watch`** — Subscribe to changes via push channel (needs a publicly reachable webhook).
- **`GET /files/{fileId}/listLabels`** — List labels applied to a file.

**Key File resource fields** (include in `fields=` as needed): `id`, `name`, `mimeType`,
`description`, `starred`, `trashed`, `parents[]`, `webViewLink`, `webContentLink`, `iconLink`,
`thumbnailLink`, `createdTime`, `modifiedTime`, `viewedByMeTime`, `sharedWithMeTime`, `owners[]`,
`lastModifyingUser`, `shared`, `ownedByMe`, `capabilities{}`, `size`, `md5Checksum`, `sha1Checksum`,
`sha256Checksum`, `headRevisionId`, `exportLinks{}`, `appProperties{}`, `properties{}`, `driveId`,
`teamDriveId`, `shortcutDetails{}`.

## Search query language

The `q` param on `files.list`. Combine terms with `and` / `or`, negate with `not`, group with
parentheses. String literals use single quotes; escape `'` and `\` with `\`.

- **`name`** (`contains`, `=`, `!=`) — `name contains 'report'`
- **`fullText`** (`contains`) — `fullText contains '"exact phrase"'`
- **`mimeType`** (`contains`, `=`, `!=`) — `mimeType = 'application/pdf'`
- **`modifiedTime`** (`<=`, `<`, `=`, `!=`, `>`, `>=`) — `modifiedTime > '2024-01-01T12:00:00'`
- **`createdTime`** (same) — `createdTime >= '2024-06-01'`
- **`viewedByMeTime`** (same) — `viewedByMeTime > '2024-06-01'`
- **`trashed`** (`=`, `!=`) — `trashed = false`
- **`starred`** (`=`, `!=`) — `starred = true`
- **`parents`** (`in`) — `'FOLDER_ID' in parents`
- **`owners`** (`in`) — `'user@example.com' in owners`
- **`writers` / `readers`** (`in`) — `'user@example.com' in writers`
- **`sharedWithMe`** (`=`, `!=`) — `sharedWithMe = true`
- **`visibility`** (`=`, `!=`) — `visibility = 'anyoneWithLink'`
- **`properties`** (`has`) — `properties has { key='x' and value='y' }`
- **`appProperties`** (`has`) — `appProperties has { key='x' and value='y' }`
- **`shortcutDetails.targetId`** (`=`, `!=`) — `shortcutDetails.targetId = 'FILE_ID'`

`orderBy` values: `createdTime`, `folder`, `modifiedByMeTime`, `modifiedTime`, `name`,
`name_natural`, `quotaBytesUsed`, `recency`, `sharedWithMeTime`, `starred`, `viewedByMeTime`. Append
` desc` for descending, comma-separate for multiple keys: `folder,modifiedTime desc,name`.

## Export MIME types

`files.export` — source type → allowed targets:

- **Docs (`...apps.document`)** — `text/plain`, `text/markdown`, `text/html`, `application/zip` (HTML), `application/rtf`, `application/pdf`, `application/epub+zip`, `application/vnd.oasis.opendocument.text`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document` (.docx)
- **Sheets (`...apps.spreadsheet`)** — `text/csv` (first sheet), `text/tab-separated-values`, `application/pdf`, `application/zip` (HTML), `application/vnd.oasis.opendocument.spreadsheet`, `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` (.xlsx)
- **Slides (`...apps.presentation`)** — `text/plain`, `application/pdf`, `application/vnd.oasis.opendocument.presentation`, `application/vnd.openxmlformats-officedocument.presentationml.presentation` (.pptx)
- **Drawings (`...apps.drawing`)** — `image/png`, `image/jpeg`, `image/svg+xml`, `application/pdf`
- **Apps Script (`...apps.script`)** — `application/vnd.google-apps.script+json`

Also queryable live from `GET /about?fields=exportFormats`.

## Uploads

Three `uploadType` modes on the `/upload` host (`https://www.googleapis.com/upload/drive/v3/files`):

- **`media`** (≤5 MB, content only, no metadata) — `POST` or `PATCH` with `Content-Type: <file type>` and raw body.
- **`multipart`** (≤5 MB, metadata + content in one call) — `multipart/related` (or `-F` form parts). Part 1: JSON metadata, part 2: content.
- **`resumable`** (>5 MB, or network reliability matters) — 1) `POST ?uploadType=resumable` with metadata JSON and `X-Upload-Content-Type` / `X-Upload-Content-Length` headers. Response `Location` header is the session URI. 2) `PUT` the content (in one go or in 256 KiB-multiple chunks with `Content-Range`). 3) On interruption, `PUT` with `Content-Range: bytes */<total>` to query progress, then resume.

Resumable start:

```bash
# file size: wc -c is portable across GNU and BSD/macOS (stat -c %s is GNU-only)
SIZE=$(wc -c < demo.mp4 | tr -d ' ')

RESP=$(gdrive -X POST -i \
  "https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable&fields=id" \
  -H "Content-Type: application/json; charset=UTF-8" \
  -H "X-Upload-Content-Type: video/mp4" \
  -H "X-Upload-Content-Length: ${SIZE}" \
  -d '{"name":"demo.mp4","parents":["FOLDER_ID"]}')
SESSION_URI=$(printf '%s' "$RESP" | grep -i '^location:' | tr -d '\r' | awk '{print $2}')

# guard: no Location header means the session was not created — print the error and stop
if [ -z "$SESSION_URI" ]; then printf '%s\n' "$RESP" >&2; else
  curl -sS -X PUT "${SESSION_URI}" -H "Content-Type: video/mp4" --data-binary "@demo.mp4"
fi
```

## Permissions

- **`GET /files/{fileId}/permissions`** — List. Params: `fields`, `pageSize`, `pageToken`, `supportsAllDrives`, `includePermissionsForView` (`published`).
- **`POST /files/{fileId}/permissions`** — Create. Body: `{type, role, emailAddress | domain}`. Params: `sendNotificationEmail`, `emailMessage`, `transferOwnership`, `moveToNewOwnersRoot`, `supportsAllDrives`.
- **`GET / PATCH / DELETE /files/{fileId}/permissions/{permissionId}`** — Read / change role / revoke. PATCH body: `{role}`. Param `removeExpiration` clears an expiry.

`type`: `user`, `group`, `domain`, `anyone`. `role`: `owner`, `organizer`, `fileOrganizer`,
`writer`, `commenter`, `reader`. `expirationTime` (RFC 3339) is settable on `user` / `group`
permissions with role ≠ `owner`. Transferring ownership requires `transferOwnership=true` and
`role=owner`.

## Comments & replies

- **`GET /files/{fileId}/comments`** — List. Params: `fields` (must include comment subfields, e.g. `comments(id,content,author,resolved,replies)`), `pageSize`, `pageToken`, `includeDeleted`, `startModifiedTime`.
- **`POST /files/{fileId}/comments`** — Create. Body: `{"content": "..."}`. Optional `anchor` / `quotedFileContent` for anchored comments.
- **`GET / PATCH / DELETE /files/{fileId}/comments/{commentId}`** — Read / edit / delete.
- **`GET / POST /files/{fileId}/comments/{commentId}/replies`** — List / add a reply. Body: `{"content": "..."}` or `{"action": "resolve"}` / `{"action": "reopen"}`.
- **`GET / PATCH / DELETE .../replies/{replyId}`** — Per-reply ops.

Comment endpoints require an explicit `fields=` param — there is no default.

## Revisions

- **`GET /files/{fileId}/revisions`** — List. Params: `fields`, `pageSize`, `pageToken`.
- **`GET /files/{fileId}/revisions/{revisionId}`** — Metadata. `?alt=media` downloads that revision's content (binary files only).
- **`PATCH /files/{fileId}/revisions/{revisionId}`** — Body: `{"keepForever": true}` to pin, `{"published": true}` to publish (Workspace files).
- **`DELETE /files/{fileId}/revisions/{revisionId}`** — Delete a non-head revision.

## Shared drives

- **`GET /drives`** — List shared drives the user is a member of. Params: `pageSize`, `pageToken`, `q`, `useDomainAdminAccess`.
- **`GET / PATCH / DELETE /drives/{driveId}`** — Read / rename-or-restrict / delete a shared drive.
- **`POST /drives`** — Create. Requires a client-generated `requestId` query param for idempotency. Body: `{"name": "..."}`.
- **`POST /drives/{driveId}/hide` / `/unhide`** — Hide/unhide from the user's default view.

When working inside a shared drive, pass `driveId`, `corpora=drive`,
`includeItemsFromAllDrives=true`, `supportsAllDrives=true` on `files.list`, and
`supportsAllDrives=true` on per-file calls that accept it (get/update/copy/delete/download —
`files.export` does not).

## Changes

The changes feed is a cursor-based log of every modification visible to the user — the right way to
sync incrementally instead of re-listing.

- **`GET /changes/startPageToken`** — Get the initial cursor. Params: `driveId`, `supportsAllDrives`.
- **`GET /changes`** — Fetch changes since a cursor. Params: `pageToken` (required), `pageSize`, `includeRemoved`, `restrictToMyDrive`, `spaces`, `driveId`, `includeItemsFromAllDrives`, `supportsAllDrives`, `fields`. Response has `nextPageToken` (more pages) or `newStartPageToken` (caught up — store it for next time).
- **`POST /changes/watch`** — Push notifications for the changes feed.
