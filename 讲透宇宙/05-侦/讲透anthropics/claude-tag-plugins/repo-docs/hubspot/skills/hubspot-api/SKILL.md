---
name: hubspot-api
description: Read, create, update, search, and associate HubSpot CRM records — contacts, companies, deals, tickets, and custom objects. Use this whenever the user wants to look up a contact, create a deal, update a company, search the CRM, link two records, or asks "what's in HubSpot" — even if they don't say "API". Also use it for any URL under app.hubspot.com or a mention of a HubSpot object/record ID. Always start from this skill when interacting with this service — its bundled scripts and recipes are the fastest path.
---

HubSpot's CRM API (v3) is uniform across object types: every object lives under `https://api.hubapi.com/crm/v3/objects/{objectType}` and supports the same basic/search/batch/association operations.

(HubSpot is rolling out date-based path versions — `/crm/objects/2026-03/...` — as the successor naming. The `v3`/`v4` paths below all still work; HubSpot has announced `v4` becomes unsupported on 2027-03-30 and `v3`'s end-of-support date is not yet set. No migration is required for now.)

**Key concepts:**

- **Object types** are identified by name (`contacts`, `companies`, `deals`, `tickets`) or by numeric
  `objectTypeId` (`0-1`, `0-2`, `0-3`, `0-5`). Custom objects are `2-<n>` or their `p_<name>` alias.
  Either form works in the URL.
- **Properties are opt-in on reads.** List/get calls return only a handful of default properties
  (`hs_object_id`, `createdate`, `lastmodifieddate`, and per-type defaults like `email` / `firstname`
  for contacts). Always pass `properties=` with a comma-separated list of the fields you actually
  need, or you'll get records that look empty.
- **Each object type has its own primary display property and dedup key.** Contacts dedup on `email`;
  companies on `domain`; deals and tickets have no dedup. Know the key before creating.
- **Associations are typed.** The common ones (`contact_to_company`, `deal_to_contact`, etc.) have
  built-in type IDs. You can also define custom association labels.

## Request setup

Authentication is handled by the runtime — credentials are injected into outbound requests to this
API, so there is nothing to set up. Do not try to create, mint, refresh, or validate tokens or keys.
Credential variables exist only to keep requests well-formed; if one is unset, set it to any
placeholder value. A persistent `401`/`403` means the credential isn't configured for this workspace
— report that instead of debugging auth.

Every request carries a bearer header. The configured credential has a set of scopes
(`crm.objects.contacts.read`, `crm.objects.deals.write`, etc.) that control what it can touch.

```bash
export HUBSPOT_ACCESS_TOKEN="placeholder"   # injected by the runtime; any value works
```

**Sanity check** — confirm the workspace is wired up:

```bash
curl -sS "https://api.hubapi.com/crm/v3/objects/contacts?limit=1" \
  -H "Authorization: Bearer ${HUBSPOT_ACCESS_TOKEN}" | jq .
```

A `403` means the request authenticated but the configured credential lacks the scope for what you
tried.

For brevity the recipes below use a helper. Define it once, or copy the `-H` flag onto each `curl`:

```bash
hsapi() { curl -sS "$@" -H "Authorization: Bearer ${HUBSPOT_ACCESS_TOKEN}" -H "Content-Type: application/json"; }
```

## Core operations

The operations below use `contacts`, but the same paths work for `companies`, `deals`, `tickets`,
and any custom object — just swap the `{objectType}` segment.

### 1. List records

Cursor-paginated, property-filtered, no search.

```bash
hsapi -G "https://api.hubapi.com/crm/v3/objects/contacts" \
  --data-urlencode "limit=50" \
  --data-urlencode "properties=email,firstname,lastname,lifecyclestage,hubspot_owner_id" \
  --data-urlencode "archived=false" | jq '.results[] | {id, props: .properties}'
```

On failure the response is `{"status":"error", "message":..., "category":...}` and has no `.results`
— see Error handling. Guard once if scripting (`jq 'if .results then … else . end'`); the recipes
below show the bare projection for clarity.

Add `associations=companies,deals` to inline association IDs for each record.

### 2. Get one record

```bash
hsapi -G "https://api.hubapi.com/crm/v3/objects/contacts/CONTACT_ID" \
  --data-urlencode "properties=email,firstname,lastname,phone,company" \
  --data-urlencode "associations=companies,deals" | jq .
```

To fetch by a unique property instead of internal ID (e.g. by email), add `idProperty=email` and put
the email in the path:

```bash
hsapi -G "https://api.hubapi.com/crm/v3/objects/contacts/alice@example.com" \
  --data-urlencode "idProperty=email" \
  --data-urlencode "properties=email,firstname,lastname" | jq .
```

### 3. Create a record

```bash
hsapi -X POST "https://api.hubapi.com/crm/v3/objects/contacts" \
  -d '{
    "properties": {
      "email": "alice@example.com",
      "firstname": "Alice",
      "lastname": "Nguyen",
      "lifecyclestage": "lead"
    }
  }' | jq 'if .status == "error" then . else {id, createdAt} end'
```

To create **and associate** in one call, add an `associations` array:

```bash
hsapi -X POST "https://api.hubapi.com/crm/v3/objects/deals" \
  -d '{
    "properties": {
      "dealname": "Acme expansion",
      "pipeline": "default",
      "dealstage": "appointmentscheduled",
      "amount": "15000"
    },
    "associations": [
      {"to": {"id": "COMPANY_ID"}, "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 341}]}
    ]
  }' | jq .
```

`341` is `deal_to_company`. See the association-type table in `references/api.md`, or discover them
live (op 8).

### 4. Update a record

`PATCH` only the properties you want to change. Everything else is untouched.

```bash
hsapi -X PATCH "https://api.hubapi.com/crm/v3/objects/contacts/CONTACT_ID" \
  -d '{"properties": {"lifecyclestage": "marketingqualifiedlead", "phone": "+1-555-0100"}}'
```

Updating by unique property works the same as reading — append `?idProperty=email` and put the email
in the path.

### 5. Archive / delete a record

HubSpot "deletes" are soft (the record goes to the recycle bin for ~90 days). Success is a `204`
with an empty body, so print the status code:

```bash
hsapi -X DELETE "https://api.hubapi.com/crm/v3/objects/contacts/CONTACT_ID" -w '\n%{http_code}\n'
```

Batch delete: `POST /crm/v3/objects/contacts/batch/archive` with `{"inputs": [{"id": "..."}, ...]}`.

### 6. Search records (`scripts/hs_search.sh`)

Search any object type through the bundled script (path is relative to this skill's directory): it
builds the `filterGroups`/`sorts`/`query` body, posts to `/crm/v3/objects/{type}/search`, follows
`paging.next.after` through every page, and emits TSV or JSONL.

```bash
scripts/hs_search.sh --object contacts \
  --filter lifecyclestage:EQ:lead \
  --filter createdate:GTE:2024-01-01T00:00:00Z \
  --sort createdate:desc --limit 200
```

- `--object TYPE` (required) is `contacts`, `companies`, `deals`, `tickets`, or any object type
  name / `objectTypeId`. Instance specifics come from `HUBSPOT_ACCESS_TOKEN` above.
- `--filter PROP:OP:VALUE` (repeatable) ANDs filters in one `filterGroup`. `OP` is uppercased;
  `IN` / `NOT_IN` take a comma list (`dealstage:IN:won,lost` → `values`; for string properties
  the values must be lowercase), `BETWEEN` takes `low,high` (`amount:BETWEEN:100,500` → `value` +
  `highValue`), `HAS_PROPERTY` / `NOT_HAS_PROPERTY` take no value. `--query TEXT` adds a free-text
  phrase match.
- `--properties LIST` drives both the request and the TSV columns; defaults are per-type
  (`email,firstname,lastname,createdate` for contacts, etc.) and required for any other type.
  `--sort PROP[:desc]` orders results.
- `--limit N` caps fetched rows (default 100, `0` = everything — search hard-caps at 10,000
  results); `--page-size N` (max 200); `--json` emits one JSON object per record instead of TSV
  with a header. Total match count and row counts go to stderr.
- Exit codes: `0` success, `1` request failed or API error (`category` and `message` on stderr) or
  bad arguments.

If the script errors, read it — it's plain `curl` + `jq` — and debug against `references/api.md`.

The script emits one ANDed `filterGroup`. For ORed groups, post the raw body via `hsapi` — limits
are 5 groups, 6 filters per group, **18 filters total**. Search is eventually consistent: a record
created or updated seconds ago may not appear yet — use a direct `GET` by ID for read-after-write.

### 7. Batch read / create / update / upsert

The `batch/*` endpoints trade one round trip for up to 100 records (some are lower — see
`references/api.md`). All five verbs follow the same `{"inputs": [...]}` shape.

```bash
# batch read by id
hsapi -X POST "https://api.hubapi.com/crm/v3/objects/contacts/batch/read" \
  -d '{"inputs": [{"id": "101"}, {"id": "102"}], "properties": ["email", "firstname"]}'

# upsert by a unique property (create if new, update if the key matches)
hsapi -X POST "https://api.hubapi.com/crm/v3/objects/contacts/batch/upsert" \
  -d '{"inputs": [{"idProperty": "email", "id": "a@x.com", "properties": {"firstname": "Alice"}}]}'
```

`batch/create` and `batch/update` take `{"inputs": [{"properties": {...}}]}` and
`{"inputs": [{"id": "...", "properties": {...}}]}` respectively.

### 8. List and create associations

Use the v4 associations endpoints — they're newer and carry the label/type info you actually want.
They coexist with v3.

```bash
# what's associated with this contact?
hsapi "https://api.hubapi.com/crm/v4/objects/contacts/CONTACT_ID/associations/companies" | jq '.results'

# discover association type ids between two object types
hsapi "https://api.hubapi.com/crm/v4/associations/contacts/companies/labels" | jq '.results'

# create an association (PUT — idempotent)
hsapi -X PUT "https://api.hubapi.com/crm/v4/objects/contacts/CONTACT_ID/associations/companies/COMPANY_ID" \
  -d '[{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 1}]'

# remove (204 on success, empty body)
hsapi -X DELETE "https://api.hubapi.com/crm/v4/objects/contacts/CONTACT_ID/associations/companies/COMPANY_ID" -w '\n%{http_code}\n'
```

### 9. Discover properties (schema)

Read the property catalog for an object type to learn field names, types, and `options` for
enumerated fields (pipelines, stages, lifecycle stages, etc.). Do this before creating or filtering
— guessing property names is the most common source of `400` errors.

```bash
hsapi "https://api.hubapi.com/crm/v3/properties/contacts" | \
  jq '.results[] | {name, label, type, fieldType, options: (.options | length)}'

# one property with its option values
hsapi "https://api.hubapi.com/crm/v3/properties/deals/dealstage" | jq '{name, options: [.options[] | {label, value}]}'
```

### 10. Pipelines and stages

Deals and tickets live in pipelines with ordered stages. Stage and pipeline **IDs** (not labels) are
what go in `dealstage` / `hs_pipeline_stage` properties.

```bash
hsapi "https://api.hubapi.com/crm/v3/pipelines/deals" | \
  jq '.results[] | {id, label, stages: [.stages[] | {id, label, displayOrder}]}'
```

## Pagination

List endpoints (`GET /crm/v3/objects/{type}`, property lists, association lists) and search
(`POST .../search`) both use cursor pagination: response carries `paging.next.after` when more
results exist; pass it back as `after` (query param for GET, body field for search). `limit` maxes
at 100 for list, 200 for search; search is additionally hard-capped at **10,000 total results** per
query — narrow the filter if you need more. An error body has no `.paging` — bound any loop and
break on `.status == "error"`.

## Rate limits

Private-app tokens get **100 requests per 10 seconds** on Free/Starter accounts and **190 per 10
seconds** on Professional/Enterprise (plus daily caps that scale with the account tier). Search
endpoints are limited to **5 requests per second per account** and their responses do not carry the
rate-limit headers. Every other response carries:

```
X-HubSpot-RateLimit-Max          requests allowed per interval
X-HubSpot-RateLimit-Remaining    requests left in the current interval
X-HubSpot-RateLimit-Interval-Milliseconds   interval length
X-HubSpot-RateLimit-Daily / -Daily-Remaining
```

On `429`, sleep for `X-HubSpot-RateLimit-Interval-Milliseconds` (or ~10s if absent) and retry.
Prefer batch endpoints — one batch call of 100 records counts as one request.

## Error handling

Errors are JSON: `{"status": "error", "message": "...", "correlationId": "...", "category": "..."}`.
Check `.status` before projecting `.results` / `.id` — the error envelope has neither and a bare
projection prints nulls. Always surface `message` and `category`.

- **`400` `VALIDATION_ERROR`** — Bad property name/value, malformed filter, wrong enum value. Read `errors[]` — it names the offending field. Check the property catalog (op 9).
- **`401` `INVALID_AUTHENTICATION`** — Credential missing or rejected. Check `HUBSPOT_ACCESS_TOKEN` is set at all; if it persists, the credential isn't configured for this workspace — report it.
- **`403` `MISSING_SCOPES`** — The configured credential lacks the scope for this endpoint. The message names the missing scope — report it.
- **`404` `OBJECT_NOT_FOUND`** — Bad ID, wrong `objectType`, or record was deleted/archived. Try `archived=true`.
- **`409` `CONFLICT`** — Duplicate on a unique key (e.g., creating a contact with an existing email). Switch to upsert or patch the existing record.
- **`429` `RATE_LIMITS`** — The body's `policyName` says which limit you hit: a secondly/burst policy → sleep per `X-HubSpot-RateLimit-Interval-Milliseconds`, retry; `DAILY` → stop, it resets at midnight account-local time.
- **`5xx`** — Transient. Retry with backoff.

## Going deeper

`references/api.md` has the fuller endpoint catalog — the complete default-property lists per object
type, the built-in association type ID table, batch limits, the owners/pipelines/properties
management endpoints, custom object schemas, lists, and the engagement object types (notes, calls,
tasks, meetings, emails). Read it when you need an endpoint or ID not covered above.
