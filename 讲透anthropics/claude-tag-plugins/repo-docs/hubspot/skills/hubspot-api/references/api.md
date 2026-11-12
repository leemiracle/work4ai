# HubSpot CRM API — Endpoint Reference

Request setup (bearer header, `hsapi()` helper) and the v3/v4 → date-based version timeline are in
`../SKILL.md`, section Request setup. Don't mix `v3`/`v4` and date-based path forms in one workflow.

Official docs: `https://developers.hubspot.com/docs/api-reference/latest/crm/understanding-the-crm`.

## Table of contents

- [Object CRUD (v3)](#object-crud-v3)
- [Search](#search)
- [Batch](#batch)
- [Default properties per object type](#default-properties-per-object-type)
- [Associations (v4)](#associations-v4)
- [Built-in association type IDs](#built-in-association-type-ids)
- [Properties API](#properties-api)
- [Pipelines](#pipelines)
- [Owners](#owners)
- [Custom object schemas](#custom-object-schemas)
- [Lists](#lists)
- [Engagements](#engagements)

---

## Object CRUD (v3)

Same shape for `contacts`, `companies`, `deals`, `tickets`, `products`, `line_items`, `quotes`,
`calls`, `emails`, `meetings`, `notes`, `tasks`, `communications`, `feedback_submissions`, `leads`,
`goals`, `orders`, `carts`, and any custom object (`2-<n>` or `p_<name>`).

- **`GET /crm/v3/objects/{type}`** — List. Params: `limit` (≤100), `after`, `properties` (comma-sep), `propertiesWithHistory`, `associations` (comma-sep of object types), `archived`.
- **`POST /crm/v3/objects/{type}`** — Create. Body: `{properties, associations?}`.
- **`GET /crm/v3/objects/{type}/{id}`** — Read one. Params: `properties`, `propertiesWithHistory`, `associations`, `archived`, `idProperty`.
- **`PATCH /crm/v3/objects/{type}/{id}`** — Update. Body: `{properties}`. Param: `idProperty`.
- **`DELETE /crm/v3/objects/{type}/{id}`** — Archive (soft-delete, ~90 days in recycle bin).
- **`POST /crm/v3/objects/{type}/merge`** — Merge two records. Body: `{"primaryObjectId","objectIdToMerge"}`.
- **`POST /crm/v3/objects/{type}/gdpr-delete`** — Permanent GDPR delete. Body: `{objectId}` or `{idProperty, objectId}`. Irreversible.

**Object type IDs** (interchangeable with names in the URL): contacts `0-1`, companies `0-2`, deals
`0-3`, tickets `0-5`, products `0-7`, line_items `0-8`, quotes `0-14`, calls `0-48`, emails `0-49`,
meetings `0-47`, notes `0-46`, tasks `0-27`, communications `0-18`, feedback_submissions `0-19`,
leads `0-136`.

## Search

- **`POST /crm/v3/objects/{type}/search`** — Body: `{filterGroups?, sorts?, query?, properties?, limit? (≤200), after?}`. Sorts: one `{propertyName, direction}`.

AND/OR semantics, the 5/6/18 filter caps, the 10,000-result ceiling, and the eventual-consistency
caveat are in `../SKILL.md`, operation 6 (Search records).

Filter operators: `EQ`, `NEQ`, `LT`, `LTE`, `GT`, `GTE`, `BETWEEN` (`value` + `highValue`), `IN` /
`NOT_IN` (`values: [...]` — for string properties the values **must be lowercase** or they silently
match nothing), `HAS_PROPERTY`, `NOT_HAS_PROPERTY`, `CONTAINS_TOKEN` (whole-word; `*` wildcard
prefix/suffix), `NOT_CONTAINS_TOKEN`. Date values are ISO-8601 or epoch millis.

Default searchable properties for `query`: contacts → `firstname`, `lastname`, `email`, `phone`,
`hs_additional_emails`, `fax`, `mobilephone`, `company`, `hs_marketable_until_renewal`; companies →
`name`, `domain`, `website`, `phone`; deals → `dealname`, `pipeline`, `dealstage`, `description`,
`dealtype`; tickets → `subject`, `content`, `hs_pipeline_stage`, `hs_ticket_category`,
`hs_ticket_id`.

## Batch

All under `/crm/v3/objects/{type}/batch/`. Each call's success/failure is per-input — read `status`
and `errors` in the response.

- **`POST batch/read`** (max 100 inputs) — Body: `{inputs:[{id}], properties, propertiesWithHistory?, idProperty?}`.
- **`POST batch/create`** (max 100 inputs) — Body: `{inputs:[{properties, associations?}]}`.
- **`POST batch/update`** (max 100 inputs) — Body: `{inputs:[{id, properties, idProperty?}]}`.
- **`POST batch/upsert`** (max 100 inputs) — Body: `{inputs:[{idProperty, id, properties}]}`. Create-or-update keyed on a unique property.
- **`POST batch/archive`** (max 100 inputs) — Body: `{inputs:[{id}]}`.

## Default properties per object type

Properties returned when you don't pass `properties=`. Use these as a starting point; always pass
`properties=` explicitly in real usage.

- **contacts** — Always returned: `hs_object_id`, `createdate`, `lastmodifieddate`, `email`, `firstname`, `lastname`. Notable others to request: `phone`, `company`, `jobtitle`, `lifecyclestage`, `hs_lead_status`, `hubspot_owner_id`, `hs_analytics_source`, `city`, `state`, `country`
- **companies** — Always returned: `hs_object_id`, `createdate`, `hs_lastmodifieddate`, `name`, `domain`. Notable others to request: `industry`, `numberofemployees`, `annualrevenue`, `city`, `state`, `country`, `hubspot_owner_id`, `lifecyclestage`, `type`
- **deals** — Always returned: `hs_object_id`, `createdate`, `hs_lastmodifieddate`, `dealname`, `amount`, `closedate`, `pipeline`, `dealstage`. Notable others to request: `dealtype`, `hubspot_owner_id`, `hs_deal_stage_probability`, `hs_forecast_amount`, `hs_is_closed`, `hs_is_closed_won`
- **tickets** — Always returned: `hs_object_id`, `createdate`, `hs_lastmodifieddate`, `subject`, `content`, `hs_pipeline`, `hs_pipeline_stage`, `hs_ticket_priority`. Notable others to request: `hs_ticket_category`, `hubspot_owner_id`, `source_type`, `hs_resolution`, `closed_date`

## Associations (v4)

- **`GET /crm/v4/objects/{from}/{id}/associations/{to}`** — List associated record IDs + types. Params: `limit`, `after`.
- **`PUT /crm/v4/objects/{from}/{fromId}/associations/{to}/{toId}`** — Associate. Body: `[{associationCategory, associationTypeId}]`. Idempotent.
- **`PUT /crm/v4/objects/{from}/{fromId}/associations/default/{to}/{toId}`** — Associate with the default (unlabeled) type. No body.
- **`DELETE /crm/v4/objects/{from}/{fromId}/associations/{to}/{toId}`** — Remove all associations between the two records.
- **`GET /crm/v4/associations/{from}/{to}/labels`** — Discover type IDs and labels between two object types.
- **`POST / PUT / DELETE /crm/v4/associations/{from}/{to}/labels`** — Create / rename / delete a custom label.
- **`POST /crm/v4/associations/{from}/{to}/batch/read`** — Body: `{inputs:[{id}]}`. Max 1000.
- **`POST /crm/v4/associations/{from}/{to}/batch/create`** — Body: `{inputs:[{from:{id}, to:{id}, types:[...]}]}`. Max 2000.
- **`POST /crm/v4/associations/{from}/{to}/batch/archive`** — Body: `{inputs:[{from:{id}, to:[{id}]}]}`.

`associationCategory` is `HUBSPOT_DEFINED` for built-in types, `USER_DEFINED` for custom labels.

## Built-in association type IDs

The IDs are directional — `contact_to_company` ≠ `company_to_contact`. This list covers the common
pairs, but **when in doubt, discover the IDs live** from
`GET /crm/v4/associations/{from}/{to}/labels` — a stale or misremembered ID silently links the wrong
records, and the account may also define custom labels not listed here.

- **contact → company (primary)** — 1
- **company → contact (primary)** — 2
- **contact → company** — 279
- **company → contact** — 280
- **deal → contact** — 3
- **contact → deal** — 4
- **deal → company (primary)** — 5
- **company → deal (primary)** — 6
- **deal → company** — 341
- **company → deal** — 342
- **ticket → contact** — 16
- **contact → ticket** — 15
- **ticket → company (primary)** — 26
- **company → ticket (primary)** — 25
- **ticket → company** — 339
- **company → ticket** — 340
- **ticket → deal** — 28
- **deal → ticket** — 27
- **deal → line_item** — 19
- **line_item → deal** — 20
- **quote → deal** — 64
- **deal → quote** — 63
- **call → contact** — 194
- **note → contact** — 202
- **task → contact** — 204
- **meeting → contact** — 200
- **email → contact** — 198

## Properties API

- **`GET /crm/v3/properties/{type}`** — All properties for an object type. Param: `archived`.
- **`GET /crm/v3/properties/{type}/{name}`** — One property's full definition (incl. `options[]`).
- **`POST /crm/v3/properties/{type}`** — Create a custom property. Body: `{name, label, type, fieldType, groupName, options?}`.
- **`PATCH /crm/v3/properties/{type}/{name}`** — Update.
- **`GET / POST /crm/v3/properties/{type}/groups`** — Property groups.
- **`POST /crm/v3/properties/{type}/batch/read`** — Body: `{inputs:[{name}]}`.

Property `type` ∈ `string`, `number`, `date`, `datetime`, `enumeration`, `bool`, `phone_number`.
`fieldType` ∈ `text`, `textarea`, `number`, `date`, `select`, `radio`, `checkbox`,
`booleancheckbox`, `file`, `html`, `phonenumber`, `calculation_equation`.

## Pipelines

- **`GET /crm/v3/pipelines/{type}`** — All pipelines + stages. `{type}` is `deals` or `tickets`.
- **`GET / PATCH / DELETE /crm/v3/pipelines/{type}/{id}`** — One pipeline.
- **`POST /crm/v3/pipelines/{type}`** — Create. Body: `{label, displayOrder, stages}`.
- **`GET / POST /crm/v3/pipelines/{type}/{id}/stages`** — Stages.
- **`GET / PATCH / DELETE /crm/v3/pipelines/{type}/{id}/stages/{stageId}`** — One stage.

Stage objects have `id`, `label`, `displayOrder`, `metadata` (`{probability}` for deals,
`{ticketState}` — `OPEN` or `CLOSED` — for tickets). The `id`, not the `label`, is what you write
into the record's `dealstage` / `hs_pipeline_stage` property.

## Owners

- **`GET /crm/v3/owners`** — List users who can own records. Params: `email`, `limit`, `after`, `archived`.
- **`GET /crm/v3/owners/{id}`** — One owner. Param: `idProperty` = `id` (default) or `userId`.

Owner `id` (not `userId`) is what you write into `hubspot_owner_id`.

## Custom object schemas

- **`GET /crm-object-schemas/v3/schemas`** — List custom object schemas.
- **`GET /crm-object-schemas/v3/schemas/{id}`** — One schema: `objectTypeId` (`2-<n>`), `fullyQualifiedName` (`p_<name>`), `properties`, `associations`, `primaryDisplayProperty`, `requiredProperties`.
- **`POST /crm-object-schemas/v3/schemas`** — Create.
- **`PATCH / DELETE /crm-object-schemas/v3/schemas/{id}`** — Update / delete.

Once defined, CRUD the records with `/crm/v3/objects/{objectTypeId}` or `/crm/v3/objects/p_{name}`.

## Lists

Lists (v3) group contacts/companies/etc. for marketing segmentation.

- **`POST /crm/v3/lists/search`** — Find lists by name. Body: `{query, offset, count}`.
- **`GET /crm/v3/lists/{listId}`** — List details.
- **`GET /crm/v3/lists/{listId}/memberships`** — Record IDs in the list. Params: `limit`, `after`.
- **`PUT /crm/v3/lists/{listId}/memberships/add`** — Body: `[recordId, ...]`. MANUAL and SNAPSHOT lists only (not DYNAMIC).
- **`PUT /crm/v3/lists/{listId}/memberships/remove`** — Body: `[recordId, ...]`. MANUAL and SNAPSHOT lists only (not DYNAMIC).

## Engagements

Calls, emails, meetings, notes, and tasks are CRM objects — use the generic v3 object endpoints
(`/crm/v3/objects/calls`, `/crm/v3/objects/notes`, etc.). Their key properties:

- **notes** — `hs_note_body`, `hs_timestamp`
- **tasks** — `hs_task_subject`, `hs_task_body`, `hs_task_status` (`NOT_STARTED`/`COMPLETED`/...), `hs_task_priority`, `hs_task_type`, `hs_timestamp`
- **calls** — `hs_call_title`, `hs_call_body`, `hs_call_duration` (ms), `hs_call_direction`, `hs_call_status`, `hs_timestamp`
- **emails** — `hs_email_subject`, `hs_email_text`, `hs_email_html`, `hs_email_direction`, `hs_email_status`, `hs_timestamp`
- **meetings** — `hs_meeting_title`, `hs_meeting_body`, `hs_meeting_start_time`, `hs_meeting_end_time`, `hs_meeting_outcome`, `hs_timestamp`

`hs_timestamp` is required on create (ISO-8601 or epoch ms). Associate to the contact/company/deal
via the `associations` array on create or the v4 associations API afterward.
