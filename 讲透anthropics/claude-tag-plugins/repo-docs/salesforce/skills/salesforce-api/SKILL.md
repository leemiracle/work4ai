---
name: salesforce-api
description: Query, read, create, update, and describe Salesforce records — Accounts, Contacts, Opportunities, Leads, Cases, and custom objects. Use this whenever the user wants to look up a Salesforce record, run a SOQL query, update an Opportunity, check an object's fields, or asks "what's in Salesforce" — even if they don't say "API". Also use it for any URL under *.salesforce.com / *.lightning.force.com or a mention of a Salesforce record ID or SOQL. Always start from this skill when interacting with this service — its bundled scripts and recipes are the fastest path.
---

In Salesforce, every org has its own **instance URL** (its My Domain), and the API is versioned in the path:

```
https://<your-org>.my.salesforce.com/services/data/vXX.0/...
```

**Key facts that bite:**

- **Errors return as a JSON array, success as an object.** Guard every jq projection with
  `if type == "array" then . else <projection> end` or the error body crashes the filter and you
  never see `errorCode`.
- Custom objects and fields end in `__c`; custom relationship names end in `__r` (use `__r` in SOQL
  parent paths and child subqueries).
- Record **IDs** are 15- or 18-char alphanumeric. The 18-char form is case-insensitive — prefer it.
- SOQL has **no `SELECT *`**. `FIELDS(ALL)` / `FIELDS(CUSTOM)` exist but require `LIMIT 200`.
- **Describe is your schema** — field names, picklist values, relationship names, and
  `createable`/`updateable` flags. Read it before guessing field names.

## Request setup

Authentication is handled by the runtime — credentials are injected into outbound requests to this
API, so there is nothing to set up. Do not try to create, mint, refresh, or validate tokens or keys.
Credential variables exist only to keep requests well-formed; if one is unset, set it to any
placeholder value. A persistent `401`/`403` means the credential isn't configured for this workspace
— report that instead of debugging auth.

The **instance URL** must be real — every org has its own and it's part of every request path:

```bash
export SALESFORCE_ACCESS_TOKEN="placeholder"   # injected by the runtime; any value works
export SALESFORCE_INSTANCE_URL="https://yourorg.my.salesforce.com"
export SF_API="${SALESFORCE_INSTANCE_URL}/services/data/v66.0"
```

**Sanity check** — confirm the instance URL is right and the workspace is wired up:

```bash
curl -sS "${SF_API}/" -H "Authorization: Bearer ${SALESFORCE_ACCESS_TOKEN}" | jq .
# Returns a map of available API resources on success.
```

For brevity the recipes below use a helper. Define it once, or copy the `-H` flag onto each `curl`:

```bash
salesforce_api() { curl -sS "$@" -H "Authorization: Bearer ${SALESFORCE_ACCESS_TOKEN}" -H "Content-Type: application/json"; }
```

## Core operations

### 1. Run a SOQL query (`scripts/sf_query.sh`)

Run SOQL through the bundled script (path is relative to this skill's directory): it submits the
query, follows `nextRecordsUrl` through every page, surfaces the array-shaped error body, strips the
per-record `attributes` envelope every record carries, and flattens nested parent-relationship
objects to dotted-key columns (`Account.Name`).

```bash
scripts/sf_query.sh \
  "SELECT Id, Name, Amount, StageName, Account.Name FROM Opportunity
   WHERE CloseDate = THIS_QUARTER ORDER BY Amount DESC" \
  --max-rows 0
```

- SOQL is one quoted argument or stdin. Instance specifics come from `SALESFORCE_INSTANCE_URL` /
  `SALESFORCE_ACCESS_TOKEN` above; `--instance-url` and `--api-version` override. Full SOQL syntax
  (parent paths, child subqueries, date literals, escaping): `references/api.md`, section SOQL.
- `--all` switches to `/queryAll` (includes deleted/archived records).
- `--max-rows N` caps fetched rows (default 10000, `0` = everything); `--batch-size N` (200–2000)
  sets the `Sforce-Query-Options` page size; `--json` emits one JSON object per row instead of TSV
  with a header. `totalSize` and row counts go to stderr.
- Exit codes: `0` success; non-zero on failure (`1` = API/argument error with `errorCode` on stderr, other = curl transport error).

If the script errors, read it — it's plain `curl` + `jq` — and debug against `references/api.md`.
SOSL search, sObject writes, Describe, Composite, and Bulk API 2.0 are separate endpoints
(operations below and `references/api.md`).

### 2. Full-text search (SOSL)

`salesforce_api -G "${SF_API}/search" --data-urlencode "q=FIND {Acme} IN NAME FIELDS RETURNING
Account(Id, Name), Contact(Id, Name, Email)"` → results under `.searchRecords` (`-G` keeps
`--data-urlencode` a GET; without it curl POSTs and `/search` rejects it). Or
`GET /parameterizedSearch?q=Acme&sobject=Account&Account.fields=Id,Name`.

### 3. Read / create / update / delete one record

- **Read** — `GET ${SF_API}/sobjects/Account/ID?fields=Id,Name,Industry`. Omit `fields` for all. Parent fields need SOQL or `/sobjects/Account/ID/Owner`. By external ID: `/sobjects/Account/Ext_Id__c/VALUE`.
- **Create** — `POST ${SF_API}/sobjects/Account` body `{"Name":"Acme",...}`. Returns `{"id","success":true,"errors":[]}`. Lookups: `"AccountId":"001..."` or by external ID `"Account":{"Ext_Id__c":"ACME-42"}`.
- **Update** — `PATCH ${SF_API}/sobjects/Opportunity/ID` body `{"StageName":"..."}`. **Returns 204 No Content** (empty body) — pass `-w '\n%{http_code}\n'` to see it.
- **Delete** — `DELETE ${SF_API}/sobjects/Account/ID`. 204 on success. Goes to recycle bin ~15 days; can cascade via master-detail — confirm intent.

### 4. Upsert by external ID

`PATCH` on the external-ID path creates or updates in one call — the safest way to sync from another
system:

```bash
salesforce_api -X PATCH "${SF_API}/sobjects/Account/External_Id__c/ACME-42" \
  -d '{"Name": "Acme Corporation", "Industry": "Manufacturing"}' -w '\n%{http_code}\n'
# 201 + {"id",...,"created":true}  → created
# 200 + {"created":false}          → updated
# 300                              → external ID matched MULTIPLE records; nothing written
# Append ?updateOnly=true to update-or-fail instead of update-or-create.
```

### 5. Describe an sObject (schema)

List all sObjects: `GET ${SF_API}/sobjects` → `.sobjects[] | {name, label, custom, queryable}`.

One sObject's full schema:

```bash
salesforce_api "${SF_API}/sobjects/Opportunity/describe" | \
  jq '{fields: [.fields[]? | {name, type, createable, updateable, picklistValues: [.picklistValues[]?.value]}], childRelationships: [.childRelationships[]? | {relationshipName, childSObject}]}'
```

### 6. Composite: several operations in one request

Chains up to 25 subrequests in one round trip. Later subrequests reference earlier results with
`@{refName.field}`. Set `allOrNone: true` to roll back the whole batch on any failure. **Each
subrequest `url` is an absolute path that must repeat the same API version as the outer request** —
if you change `v66.0` in `${SF_API}`, change it here too.

```bash
salesforce_api -X POST "${SF_API}/composite" \
  -d '{
    "allOrNone": true,
    "compositeRequest": [
      {
        "method": "POST", "url": "/services/data/v66.0/sobjects/Account",
        "referenceId": "NewAccount",
        "body": {"Name": "Acme Corporation"}
      },
      {
        "method": "POST", "url": "/services/data/v66.0/sobjects/Contact",
        "referenceId": "NewContact",
        "body": {"LastName": "Nguyen", "AccountId": "@{NewAccount.id}"}
      },
      {
        "method": "GET", "url": "/services/data/v66.0/sobjects/Account/@{NewAccount.id}?fields=Id,Name",
        "referenceId": "ReadBack"
      }
    ]
  }' | jq '.compositeResponse[]? | {ref: .referenceId, status: .httpStatusCode, body: .body}'
```

**The outer request returns `200` even when subrequests fail** — always check each subrequest's
`httpStatusCode`. For bulk inserts/updates without cross-references, use Composite Collections —
`POST /composite/sobjects` with up to 200 records (see `references/api.md`).

### 7. Check limits

`GET ${SF_API}/limits` → `.DailyApiRequests` shows `Max` and `Remaining`. Check before running a
loop — orgs have per-24-hour caps.

## Pagination

SOQL responses cap at 2000 records/page (configurable 200–2000 via header
`Sforce-Query-Options: batchSize=N`). When more rows exist the response has `done: false` and
`nextRecordsUrl` — an instance-relative path you `GET` against `${SALESFORCE_INSTANCE_URL}`;
`scripts/sf_query.sh` follows it for you. `OFFSET` in SOQL is **hard-capped at 2000** — use
`nextRecordsUrl` for deep pagination, or Bulk API 2.0 for very large exports (`references/api.md`).

## Rate limits

Salesforce caps total API calls **per rolling 24 hours per org** (not per second). Every response
carries:

```
Sforce-Limit-Info: api-usage=1234/100000
```

Hitting the cap → `403` with `errorCode: REQUEST_LIMIT_EXCEEDED`. **No `Retry-After`** — wait for
usage to age out of the 24-hour window. Separately enforced: **max 25 concurrent long-running
requests** (≥20s; 5 in Developer Edition). That also surfaces as `REQUEST_LIMIT_EXCEEDED` (message
names `ConcurrentRequests`/`ConcurrentPerOrgLongTxn`) and clears as soon as in-flight requests
finish — back off and retry. Be frugal: batch with Composite, select only the fields you need,
prefer upsert over read-then-write.

## Error handling

Errors are a JSON **array**: `[{"message": "...", "errorCode": "...", "fields": [...]}]`. Surface
`errorCode` — it's the most specific signal.

- **`400` `MALFORMED_QUERY`** — SOQL syntax error. Message points at the offending token.
- **`400` `INVALID_FIELD`, `INVALID_TYPE`** — Field/sObject name wrong or not visible. Run describe. Custom names end in `__c`.
- **`400` `REQUIRED_FIELD_MISSING`, `FIELD_CUSTOM_VALIDATION_EXCEPTION`** — Missing required field or a validation rule fired.
- **`400` `STRING_TOO_LONG`, `INVALID_FIELD_FOR_INSERT_UPDATE`** — Value doesn't fit, or field isn't writable — check `createable`/`updateable` in describe.
- **`401` `INVALID_SESSION_ID`** — Wrong instance URL, or credential not configured. Check `SALESFORCE_INSTANCE_URL` first; if right, report it.
- **`403` `INSUFFICIENT_ACCESS_OR_READONLY`, `API_DISABLED_FOR_ORG`** — Permission problem or API not enabled for this user/org.
- **`403` `REQUEST_LIMIT_EXCEEDED`** — Daily cap (wait for 24h window) or concurrent long-running cap (back off, retry). Message says which.
- **`404` `NOT_FOUND`, `ENTITY_IS_DELETED`** — Bad ID, or record deleted. Try `queryAll`.
- **`409` `ENTITY_IS_LOCKED`** — Record locked by an approval process. Retry with backoff.
- **`500` `UNKNOWN_EXCEPTION` (often a `DUPLICATE_VALUE` or trigger failure surfaced as 500)** — Read the message. Retry once; escalate if it persists.
- **`503` `SERVER_UNAVAILABLE`** — Transient — overloaded or in maintenance. Retry with backoff.

## Going deeper

`references/api.md` has the fuller endpoint catalog — the complete SOQL/SOSL syntax reference,
Composite Collections and Composite Tree, Bulk API 2.0 for large data loads, describe global, record
counts, recently viewed, picklist values by record type, and relationship traversal paths. Read it
when you need an endpoint or SOQL feature not covered above.
