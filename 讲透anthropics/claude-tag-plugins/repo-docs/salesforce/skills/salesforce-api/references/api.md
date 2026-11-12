# Salesforce REST API — Endpoint & SOQL Reference

All requests go to `${SALESFORCE_INSTANCE_URL}/services/data/vXX.0/` (this doc uses `v66.0`, the
Spring '26 release; `GET /services/data/` lists every version the org supports) with these headers:

```
Authorization: Bearer ${SALESFORCE_ACCESS_TOKEN}
Content-Type: application/json          # on any request with a body
```

Official docs: `https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/`.

## Table of contents

- [Discovery & org](#discovery--org)
- [Query (SOQL)](#query-soql)
- [SOQL syntax reference](#soql-syntax-reference)
- [Search (SOSL)](#search-sosl)
- [sObject CRUD](#sobject-crud)
- [Describe](#describe)
- [Composite](#composite)
- [Bulk API 2.0](#bulk-api-20)
- [Common sObjects & fields](#common-sobjects--fields)
- [Limits & headers](#limits--headers)

---

## Discovery & org

- **`GET /services/data/`** — List available API versions. No version segment.
- **`GET /services/data/vXX.0/`** — List resources for this version. Good auth sanity check.
- **`GET /limits`** — Org limits (`DailyApiRequests`, `DataStorageMB`, `DailyBulkApiBatches`, etc.) with `Max` and `Remaining`.
- **`GET /recent`** — Recently viewed records for the authenticated user. Param: `limit`.
- **`GET /limits/recordCount`** — Approximate record counts. Param: `sObjects` (comma-sep API names).
- **`GET /sobjects`** — Global describe — all sObject names, labels, flags.

## Query (SOQL)

- **`GET /query`** — Run SOQL. Param: `q`. Returns `{totalSize, done, records[], nextRecordsUrl?}`. Header `Sforce-Query-Options: batchSize=N` (200–2000) tunes page size.
- **`GET /queryAll`** — Same, but includes soft-deleted (`IsDeleted=true`) and archived records.
- **`GET /query/{queryLocator}`** — Next page. Or just `GET` the `nextRecordsUrl` verbatim — it's a full path.
- **`GET /query?explain=<soql>`** — Query plan (index usage, cost, cardinality). Use to diagnose slow/selective queries.

## SOQL syntax reference

```
SELECT fieldList [, (childSubquery)]
FROM objectType
[USING SCOPE filterScope]
[WHERE conditions]
[WITH SECURITY_ENFORCED]
[GROUP BY fieldGroupBy [HAVING condition]]
[ORDER BY fieldOrderBy [ASC|DESC] [NULLS {FIRST|LAST}]]
[LIMIT n]
[OFFSET n]                  -- max 2000, avoid for deep paging
[FOR {VIEW | REFERENCE | UPDATE}]
```

- **Field lists:** no `*`. `FIELDS(ALL)` / `FIELDS(CUSTOM)` / `FIELDS(STANDARD)` expand to groups of
  fields. `ALL` and `CUSTOM` require the result set to be bounded to ≤ 200 rows (`LIMIT 200` or an
  `Id IN (...)` list); `STANDARD` has no such cap. Exploration only.
- **Parent relationships (dot paths):** up to 5 levels. Standard lookups drop the `Id` suffix:
  `AccountId` → `Account.Name`. Custom lookups replace `__c` with `__r`: `Parent__c` →
  `Parent__r.Name`.
- **Child relationships (subqueries):** `SELECT Id, (SELECT Id, Email FROM Contacts) FROM Account`.
  The subquery `FROM` uses the **relationship name** (usually the plural), not the object name. Find
  it in the parent's `childRelationships[].relationshipName` via describe. Custom:
  `ChildObjects__r`. Nesting up to 5 levels (was 1 on older API versions).
- **Aggregates:** `COUNT()`, `COUNT(field)`, `COUNT_DISTINCT(field)`, `SUM()`, `AVG()`, `MIN()`,
  `MAX()`. With `GROUP BY`, the response records are `AggregateResult` with aliased fields (`expr0`,
  `expr1`, ... or `SELECT ... alias`). `GROUP BY ROLLUP(...)` / `CUBE(...)` for subtotals.
- **Operators:** `=`, `!=`, `<`, `<=`, `>`, `>=`, `LIKE` (`%` wildcard, strings only), `IN (...)`,
  `NOT IN (...)`, `INCLUDES` / `EXCLUDES` (multi-picklist). Combine with `AND` / `OR` / `NOT`, group
  with parentheses.
- **Semi/anti-joins:** `WHERE AccountId IN (SELECT AccountId FROM Opportunity WHERE ...)`.
- **Date literals:** `TODAY`, `YESTERDAY`, `TOMORROW`, `THIS_WEEK`, `LAST_WEEK`, `NEXT_WEEK`,
  `THIS_MONTH`, `LAST_MONTH`, `NEXT_MONTH`, `THIS_QUARTER`, `LAST_QUARTER`, `NEXT_QUARTER`,
  `THIS_YEAR`, `LAST_YEAR`, `NEXT_YEAR`, `THIS_FISCAL_QUARTER`, `THIS_FISCAL_YEAR`, `LAST_N_DAYS:n`,
  `NEXT_N_DAYS:n`, `N_DAYS_AGO:n`, `LAST_N_WEEKS:n`, `LAST_N_MONTHS:n`, `LAST_N_QUARTERS:n`,
  `LAST_N_YEARS:n`, `LAST_N_FISCAL_QUARTERS:n`. Literal dates are `YYYY-MM-DD` (date) or
  `YYYY-MM-DDThh:mm:ssZ` (datetime), unquoted.
- **Functions:** `CALENDAR_YEAR()`, `CALENDAR_MONTH()`, `CALENDAR_QUARTER()`, `DAY_IN_WEEK()`,
  `DAY_IN_MONTH()`, `DAY_IN_YEAR()`, `DAY_ONLY()`, `HOUR_IN_DAY()`, `FISCAL_YEAR()`,
  `FISCAL_QUARTER()`, `FORMAT()`, `CONVERTTIMEZONE()`, `toLabel()` (picklist label instead of API
  value), `convertCurrency()`.
- **`USING SCOPE`:** `everything`, `mine`, `mine_and_my_groups`, `my_territory`, `team`,
  `delegated`.
- **`WITH SECURITY_ENFORCED`:** enforces field- and object-level security; throws if the user can't
  see a referenced field.
- **`FOR UPDATE`:** locks the returned rows for the transaction. Rarely useful over REST.
- **Escaping:** inside string literals, escape `'` as `\'`, `\` as `\\`, `%` as `\%`, `_` as `\_`.

## Search (SOSL)

- **`GET /search`** — Raw SOSL. Param: `q`.
- **`GET /parameterizedSearch`** — Simpler form. Params: `q` (keyword), `sobject` (repeatable), `{Object}.fields`, `{Object}.where`, `{Object}.limit`, `in` (`ALL`/`NAME`/`EMAIL`/`PHONE`/`SIDEBAR`), `overallLimit`, `defaultLimit`.
- **`GET /search/scopeOrder`** — The user's pinned/frequently-used objects — useful defaults for search scope.
- **`GET /search/suggestions`** — Typeahead-style suggestions. Params: `q`, `sobject`.

SOSL: `FIND {term} [IN searchGroup] [RETURNING objSpec[, ...]] [WITH ...] [LIMIT n]`. `searchGroup`:
`ALL FIELDS`, `NAME FIELDS`, `EMAIL FIELDS`, `PHONE FIELDS`, `SIDEBAR FIELDS`. `objSpec`:
`Account(Id, Name WHERE Industry='Tech' ORDER BY Name LIMIT 10)`. Escape
`? & | ! { } [ ] ( ) ^ ~ * : \ " ' + -` in the search term with `\`. Multi-word: `{acme west}` is
AND; use `{acme OR apex}` for OR.

## sObject CRUD

- **`POST /sobjects/{type}`** — Create. Body: field map. Response: `{id, success, errors}`.
- **`GET /sobjects/{type}/{id}`** — Read. Param: `fields` (comma-sep; omit for all).
- **`PATCH /sobjects/{type}/{id}`** — Update. Returns `204 No Content`.
- **`DELETE /sobjects/{type}/{id}`** — Soft delete (recycle bin ~15 days). Returns `204`.
- **`GET / PATCH / DELETE /sobjects/{type}/{extField}/{extValue}`** — Read/upsert/delete by external ID. PATCH returns `201` (created) or `200` (updated), body includes `"created"`; `300` + matching records if the external ID isn't unique. `?updateOnly=true` to never create.
- **`GET /sobjects/{type}/{id}/{relationshipName}`** — Traverse a relationship — child records or parent record without SOQL.
- **`GET /sobjects/{type}/deleted`** — IDs deleted in a window. Params: `start`, `end` (ISO-8601, ≤30 days apart, ≤30 days old).
- **`GET /sobjects/{type}/updated`** — IDs updated in a window. Same params.
- **`GET /sobjects/{type}/{id}/richTextImageFields/{fieldName}/{contentRefId}`** — Download a rich-text image.

## Describe

- **`GET /sobjects`** — Global describe. Lightweight; per-object flags: `queryable`, `createable`, `updateable`, `deletable`, `custom`, `searchable`.
- **`GET /sobjects/{type}`** — Basic metadata + recent records + URLs.
- **`GET /sobjects/{type}/describe`** — Full schema — `fields[]` (with `type`, `length`, `createable`, `updateable`, `nillable`, `picklistValues`, `referenceTo`, `relationshipName`), `childRelationships[]`, `recordTypeInfos[]`. Heavy; cache it.
- **`GET /ui-api/object-info/{type}/picklist-values/{recordTypeId}`** — Picklist values scoped to a record type (describe gives the unscoped union). `012000000000000AAA` is the master record type.
- **`GET /sobjects/{type}/describe/approvalLayouts`** — Approval process layouts.
- **`GET /sobjects/{type}/describe/compactLayouts`** — Compact layout assignments.

## Composite

- **`POST /composite`** — Up to 25 subrequests with cross-references. Body: `{allOrNone?, collateSubrequests?, compositeRequest:[{method, url, referenceId, body?, httpHeaders?}]}`. Reference prior results with `@{RefId.fieldPath}`.
- **`POST / PATCH / DELETE /composite/sobjects`** — Collections: up to 200 records in one call, same or mixed `attributes.type`. `allOrNone` query param (DELETE) or body field (POST/PATCH). `POST` creates, `PATCH` updates (each record needs `Id`).
- **`GET /composite/sobjects/{type}`** — Batch read by IDs. Params: `ids` (comma-sep), `fields` (comma-sep).
- **`PATCH /composite/sobjects/{type}/{extField}`** — Collection upsert by external ID, up to 200 records.
- **`POST /composite/tree/{type}`** — Create a record plus nested children in one call (up to 200 total records, 5 levels deep). Body uses `records[]` with `attributes.referenceId` and nested relationship arrays.
- **`POST /composite/batch`** — Up to 25 **independent** subrequests (no cross-references, no transaction). Body: `{batchRequests:[{method, url, richInput?}], haltOnError?}`.
- **`POST /composite/graph`** — Multiple composite graphs in one call, each its own transaction.

## Bulk API 2.0

For loading or exporting tens of thousands to millions of rows. Asynchronous — create a job, upload
or wait, poll, download results.

- **`POST /jobs/ingest`** — Create an ingest job. Body: `{object, operation:"insert"|"update"|"upsert"|"delete"|"hardDelete", externalIdFieldName?, contentType:"CSV", lineEnding}`.
- **`PUT /jobs/ingest/{jobId}/batches`** — Upload CSV data. `Content-Type: text/csv`.
- **`PATCH /jobs/ingest/{jobId}`** — Body: `{state:"UploadComplete"}` to start processing, or `{state:"Aborted"}`.
- **`GET /jobs/ingest/{jobId}`** — Poll status (`JobComplete`, `Failed`, `InProgress`).
- **`GET /jobs/ingest/{jobId}/successfulResults`** — Processed rows (CSV). Also `/failedResults`, `/unprocessedrecords`.
- **`POST /jobs/query`** — Create a bulk query job. Body: `{operation:"query"|"queryAll", query:"SELECT ..."}`.
- **`GET /jobs/query/{jobId}`** — Poll status.
- **`GET /jobs/query/{jobId}/results`** — Download (CSV). Params: `locator`, `maxRecords`. Header `Sforce-Locator` paginates.

## Common sObjects & fields

- **`Account`** — `Name`, `Industry`, `Type`, `AnnualRevenue`, `NumberOfEmployees`, `BillingCity/State/Country`, `Website`, `Phone`, `OwnerId`, `ParentId`
- **`Contact`** — `FirstName`, `LastName`, `Email`, `Phone`, `Title`, `AccountId`, `OwnerId`, `MailingCity/State/Country`
- **`Opportunity`** — `Name`, `Amount`, `StageName`, `CloseDate`, `Probability`, `Type`, `LeadSource`, `AccountId`, `OwnerId`, `IsClosed`, `IsWon`, `ForecastCategory`
- **`Lead`** — `FirstName`, `LastName`, `Email`, `Company`, `Status`, `LeadSource`, `Rating`, `OwnerId`, `IsConverted`, `ConvertedAccountId`, `ConvertedContactId`, `ConvertedOpportunityId`
- **`Case`** — `CaseNumber` (auto), `Subject`, `Description`, `Status`, `Priority`, `Origin`, `Type`, `Reason`, `AccountId`, `ContactId`, `OwnerId`, `IsClosed`, `IsEscalated`
- **`Task`** — `Subject`, `Status`, `Priority`, `ActivityDate`, `WhoId` (Lead/Contact), `WhatId` (any object), `OwnerId`, `Description`
- **`Event`** — `Subject`, `StartDateTime`, `EndDateTime`, `Location`, `WhoId`, `WhatId`, `OwnerId`
- **`User`** — `Name`, `Email`, `Username`, `Alias`, `IsActive`, `ProfileId`, `UserRoleId`
- **`Campaign`** — `Name`, `Type`, `Status`, `StartDate`, `EndDate`, `IsActive`, `BudgetedCost`, `ActualCost`
- **`OpportunityLineItem`** — `OpportunityId`, `Product2Id`, `PricebookEntryId`, `Quantity`, `UnitPrice`, `TotalPrice`

Every sObject has `Id`, `CreatedDate`, `CreatedById`, `LastModifiedDate`, `LastModifiedById`,
`SystemModstamp`, `IsDeleted`.

## Limits & headers

- **`Sforce-Limit-Info`** — `api-usage=<used>/<max>`, rolling 24-hour API call budget.
- **`Sforce-Locator`** — Continuation token for bulk query results.

From `GET /limits` (all return `{Max, Remaining}`): `DailyApiRequests`, `DailyBulkApiBatches`,
`DailyBulkV2QueryJobs`, `DailyAsyncApexExecutions`, `DailyStreamingApiEvents`,
`HourlyTimeBasedWorkflow`, `DataStorageMB`, `FileStorageMB`, `SingleEmail`, `MassEmail`, and more.

Other hard limits that matter for API work: SOQL query length ≤ 100,000 characters, URI plus headers
≤ 16,384 bytes (the encoded `q` param counts — for very long SOQL use a Bulk API 2.0 query job, which
takes the SOQL in the POST body), `OFFSET` ≤ 2000, `LIMIT` on `FIELDS(ALL)` / `FIELDS(CUSTOM)`
queries ≤ 200, subquery nesting up to 5 levels (was 1 on older API versions), parent traversal 5
levels, Composite subrequests ≤ 25 (of
which ≤ 5 may be query or sObject-collections subrequests), Composite Collections ≤ 200 records,
concurrent long-running (≥ 20 s) requests ≤ 25.
