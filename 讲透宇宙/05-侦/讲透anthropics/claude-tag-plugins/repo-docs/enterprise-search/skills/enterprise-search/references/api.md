# Glean Client REST API — Endpoint Reference

All requests are `POST` with a JSON body to `${GLEAN_BASE_URL}/rest/api/v1/...` with these
headers:

```
Authorization: Bearer ${GLEAN_API_TOKEN}
Content-Type: application/json
```

Official docs: `https://developers.glean.com/api/client-api/search/overview`. This reference
covers the three endpoints the skill uses; Glean's full Client API has many more (chat,
collections, people, autocomplete) that Glean-compatible backends may not implement.

## Table of contents

- [POST /rest/api/v1/search](#post-restapiv1search)
- [POST /rest/api/v1/getdocuments](#post-restapiv1getdocuments)
- [POST /rest/api/v1/feedback](#post-restapiv1feedback)
- [Datasource names](#datasource-names)
- [Error shapes](#error-shapes)

## POST /rest/api/v1/search

Retrieve ranked results from the index for a query and optional filters.

### Request

| Field | Type | Notes |
|---|---|---|
| `query` | string | The search terms. Required for meaningful results. |
| `pageSize` | integer | How many results to return. Servers may return fewer. |
| `cursor` | string | Opaque pagination token from a previous response. Omit for page 1. |
| `requestOptions` | object | Filters and hints — see below. |
| `timeoutMillis` | integer | Server-side timeout; `408` if exceeded. |
| `maxSnippetSize` | integer | Hint for snippet length in characters. |
| `disableSpellcheck` | boolean | Don't auto-correct the query. |

`requestOptions`:

| Field | Type | Notes |
|---|---|---|
| `datasourceFilter` | string | Restrict to one source app (e.g. `"slack"`). |
| `datasourcesFilter` | array of string | Restrict to several source apps. |
| `facetFilters` | array of FacetFilter | Structured filters — entries are AND'd. |
| `facetBucketSize` | integer | Required by real Glean (max facet buckets to return). Always include it; harmless on backends that ignore facets. |

`FacetFilter`:

| Field | Type | Notes |
|---|---|---|
| `fieldName` | string | Facet to filter on. `datasource` is universally supported; real Glean also supports `type`, `tag`, `author`, `last_updated_at`, and datasource-specific facets. |
| `values` | array | `{"value": "...", "relationType": "EQUALS"}`. Values within one filter are OR'd. `relationType` is one of `EQUALS`, `ID_EQUALS`, `LT`, `GT`, `NOT_EQUALS`. |

### Response

| Field | Type | Notes |
|---|---|---|
| `results` | array of SearchResult | Ranked best-first. |
| `trackingToken` | string | Search-level token. |
| `requestID` | string | For correlating server logs. |
| `cursor` | string | Pass back verbatim for the next page. Absent on the last page. |
| `hasMoreResults` | boolean | Whether another page exists. |
| `backendTimeMillis` | integer | Server processing time. |
| `facetResults` | array | Facet bucket counts (real Glean; optional elsewhere). |

`SearchResult`:

| Field | Type | Notes |
|---|---|---|
| `trackingToken` | string | Per-result token — keep it for feedback. |
| `title` | string | Document title. |
| `url` | string | Permalink to the document in its source system. |
| `snippets` | array | `{"text": "...", "snippet": "..."}` — match-centered preview. Prefer `text`; `snippet` is **deprecated** and may contain highlight markers. |
| `document` | Document | See below. |

`Document`:

| Field | Type | Notes |
|---|---|---|
| `id` | string | Index-wide document ID — what `/getdocuments` takes. |
| `datasource` | string | Source app name (see [Datasource names](#datasource-names)). |
| `docType` | string | Datasource-specific type. |
| `title` | string | |
| `url` | string | |
| `metadata` | object | `datasource`, `documentId`, `createTime`, `updateTime`, `author`, ... |

### Example

```bash
curl -sS "${GLEAN_BASE_URL}/rest/api/v1/search" \
  -H "Authorization: Bearer ${GLEAN_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "vacation policy",
    "pageSize": 5,
    "requestOptions": {
      "facetBucketSize": 10,
      "datasourcesFilter": ["confluence", "gdrive"]
    }
  }' | jq '{
    hits: [.results[] | {title, url, datasource: .document.datasource, id: .document.id}],
    cursor, hasMoreResults
  }'
```

## POST /rest/api/v1/getdocuments

Fetch full document details (including text content) by document ID.

### Request

| Field | Type | Notes |
|---|---|---|
| `documentSpecs` | array | Required. Each entry is `{"id": "..."}` (preferred) or `{"url": "..."}` (real Glean only). |
| `includeFields` | array of string | `["DOCUMENT_CONTENT"]` asks for full text. Real Glean omits content unless requested; compatible backends may always include it. |

### Response

`documents` is an object keyed by the requested id/url. Each value is the `Document` object **directly** (no wrapper):

```json
{"id": "...", "title": "...", "url": "...", "datasource": "...", "docType": "...",
 "content": {"fullTextList": ["...", "..."]}, "metadata": {...}}
```

or, when the document is missing / not visible to the caller, an error entry whose `error` is a plain string:

```json
{"error": "Document not found"}
```

`content.fullTextList` is the document's plain text in reading order, split into segments
(sections or chunks — segment boundaries are backend-specific; concatenate for the full text).

### Example

```bash
curl -sS "${GLEAN_BASE_URL}/rest/api/v1/getdocuments" \
  -H "Authorization: Bearer ${GLEAN_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"documentSpecs": [{"id": "12345"}], "includeFields": ["DOCUMENT_CONTENT"]}' \
  | jq -r '.documents["12345"] |
      if .error then "ERROR: \(.error)"
      else .content.fullTextList | join("\n")
      end'
```

## POST /rest/api/v1/feedback

Report user/agent actions on search results so the ranker can learn.

### Request

| Field | Type | Notes |
|---|---|---|
| `event` | string | Required. `UPVOTE`, `DOWNVOTE`, `CLICK`, `VIEW`, `DISMISS`, `SEEN`, ... |
| `trackingTokens` | array of string | Required. Per-result tokens from search results. |

Events the skill uses:

| Event | Meaning |
|---|---|
| `UPVOTE` / `CLICK` / `VIEW` | The result was useful — you read it and relied on it. |
| `DOWNVOTE` / `DISMISS` | The result was not useful — you opened or considered it and rejected it. |
| `SEEN` | Impression only. Usually unnecessary — backends record impressions at search time. |

### Response

`200` with an empty body (real Glean) or `{"status": "ok", "recorded": N}` (compatible
backends). Either way, 2xx means recorded.

### Example

```bash
curl -sS "${GLEAN_BASE_URL}/rest/api/v1/feedback" \
  -H "Authorization: Bearer ${GLEAN_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"event": "UPVOTE", "trackingTokens": ["token-from-search-result"]}' \
  -w '%{http_code}\n' -o /dev/null
```

## Datasource names

Datasource values are lowercase app names. Common ones:

| Datasource | Source |
|---|---|
| `gdrive` | Google Drive |
| `slack` | Slack |
| `confluence` | Atlassian Confluence |
| `jira` | Atlassian Jira |
| `github` | GitHub |
| `gmail` | Gmail |
| `salesforce` | Salesforce |
| `notion` | Notion |
| `linear` | Linear |
| `asana` | Asana |

Backends may expose additional internal datasource names (wikis, ticketing, people
directories). When a datasource filter returns nothing, retry without the filter — the
backend may use a different name for that source than real Glean does.

## Error shapes

| Status | Meaning | Body |
|---|---|---|
| `400` | Malformed request (bad cursor, missing required field) | usually empty or unstructured on real Glean; compatible backends may return `{"detail": "..."}` |
| `401` / `403` | Credential not configured or lacks access | `403` on `/search` returns an `ErrorInfo` object — see below |
| `408` | Search timed out | retry with a narrower query or a datasource filter |
| `422` | Query invalid (unparseable operators, unknown enum value) | `ErrorInfo` object — see below |
| `429` | Rate limited | back off and retry once |

Real Glean's structured error body (`/search` `403` and `422`) is an `ErrorInfo` object:

```json
{"errorMessages": [{"source": "...", "errorMessage": "..."}]}
```

Other 4xx responses (and all `/getdocuments` errors) have no published body schema and may be empty or plain text. Compatible backends sometimes return `{"detail": "..."}` instead — treat that as a backend convention, not part of Glean's spec.

An HTML body (rather than JSON) on any status almost always means `GLEAN_BASE_URL` points at the web UI host instead of the API/backend host.
