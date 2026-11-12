# Fusion Manage review drafts

`fusion_manage_item_draft_prepare` and `fusion_manage_item_draft_inspect` expose the Manage draft workflow to Codex through the MCP server. They use the existing scoped APS adapter to read a workspace schema and item, then retain or inspect a local review record. They never create or update a Manage item, publish a BOM, advance a lifecycle, notify a reviewer or grant release approval.

These tools require a `managed` or `assisted` cloud profile and separately qualified user-delegated Autodesk authorization. The synthetic fixture has no cloud authority. Native Data MCP credentials are not reused. The existing adapter requires `data:read`, an authorization-code grant, the exact configured Manage tenant and an allowlisted workspace. The target application's scopes, tenant access, license and user role still need live qualification; a configured profile or a successful protocol test does not establish them.

Autodesk's [Manage authorization tutorial](https://help.autodesk.com/cloudhelp/ENU/FLC-RestAPI/files/FLC_RestAPI_v3_API_3_legged_Tutorial_html.htm) documents the authorization-code flow, bearer authorization, tenant hostname and `x-tenant` header. It does not establish the required scope set for every customer application. This implementation retains its existing conservative scope requirement without expanding authorization.

## Owner-controlled field rules

The profile owner configures `cloud.manage` with the exact tenant and workspace IDs, then optionally supplies `cloud.manageDraftSchemas`. The latter is a registry of at most 100 unique tenant/workspace entries. It is absent by default and cannot be supplied or overridden by a tool request. Missing or out-of-scope rules block preparation before provider reads.

Each registry entry contains:

| Field | Contract |
| --- | --- |
| `tenant` | Exact configured Manage tenant hostname label |
| `workspaceId` | Positive safe integer in `cloud.manage.workspaceIds` |
| `schemaFingerprint` | SHA-256 returned by the scoped `manage.fields` read, after the owner reviews that response |
| `fields` | One to 200 uniquely identified field rules |

Every field rule has `fieldId`, `type` (`string`, `number` or `boolean`), `allowNull`, `allowDraftUpdate` and `lifecycle`. A lifecycle field cannot enable draft updates. String rules may set `maxLength` up to 8,192; without it the draft adapter allows 4,096 characters. Numeric rules may set finite `minimum` and `maximum`, in that order. Rules do not infer types or authority from labels, field names or a model-generated schema. Lists, relationship objects, computed values and tenant-specific complex fields require a separately qualified mapping; they are not coerced into scalar values.

Use `fusion_data_operations_list` and `fusion_data_search` with `manage.fields` to obtain the current scoped schema observation. Its fingerprint binds the complete provider response, not an independently signed schema. A later difference, including metadata changes, requires renewed owner review. Do not insert an invented fingerprint just to enable the tool.

The adapter retains the `/api/v3/workspaces/{workspaceId}/fields` route identified in Autodesk's [historical release notes](https://help.autodesk.com/cloudhelp/CHS/PLM-360-WhatIsNew/files/WN-OLD-RELNOTES.htm), which also describe derived-field metadata. That historical reference is not a current tenant schema or a scalar-type mapping. Verify the real response in the intended tenant before authorizing field rules.

## Prepare and inspect

Preparation accepts only `workspace_id`, `item_id` and one to 100 unique scalar changes. For example, this is a synthetic request shape, not a preauthorized workspace or field:

```json
{
  "workspace_id": 10,
  "item_id": 3,
  "changes": [
    {
      "field_id": "DESCRIPTION",
      "after": "Candidate description for engineering review",
      "source_ref": "review-package:example"
    }
  ]
}
```

The actual target and field must match the owner's registry. `source_ref` is a bounded caller assertion. It is not resolved as a file, URL, plan or approved engineering record, and every review reports `source_references_verified: false`. Credential-bearing requested values or references are rejected rather than silently changed by redaction.

Preparation validates the request and owner rules before reading Manage. It binds the exact profile, cloud scope, account/grant context, selected field rules, requested values, workspace-schema fingerprint, item fingerprint and observed ETag. The local lifetime uses the existing trusted `policy.planMaxAgeMs`; the tool cannot extend it. Scoped GETs are sequential observations, not a provider transaction or atomic item/schema snapshot.

The returned opaque ID has the form `managedraft_<UUID>`. Pass that exact ID as `draft_id` to `fusion_manage_item_draft_inspect`. Inspection verifies the original local record, rechecks its account/profile/schema context, and compares fresh scoped GET results with the stored item, schema and ETag. It does not rewrite the record, refresh expiry, rerun a mutation or create a new draft. Changed, expired, missing or malformed evidence fails explicitly. Prepare a new draft only after reviewing the changed source and authority.

## Evidence and limits

Three hashes have different meanings:

- `record_hash` binds the complete private local record, including configuration and expiry.
- `stored_draft_hash` preserves the SDK draft's original content binding.
- `review_hash` binds the exact sanitized `review` JSON value returned to the caller. `review_redacted` shows whether that projection differs from the stored draft.

Provider item data remains an opaque nested response. Autodesk's [item GET reference](https://help.autodesk.com/cloudhelp/ENU/FLC/files/Resource-Endoints/Item-API/v3workspaces%7BworkspaceId%7Ditems%7BitemId%7D/v3workspaces%7BworkspaceId%7Ditems%7BitemId%7D/FLC_Resource_Endoints_Item_API_v3workspaces_workspaceId_items_itemId_v3workspaces_workspaceId_items_itemId_GET_html.html) documents item/workspace links and fields within sections. The plugin does not present a flattened field-value map as though it were that schema. Credentials and sensitive URL components are sanitized in review output; a hash is not a signature, review decision or verification of the caller's source assertions. The record remains a draft with publication and release disabled, and no live qualification is inferred.

Local storage/audit failures can leave an uncertain local receipt even though no Manage write occurred. Such errors retain the allocated draft ID for reconciliation. Do not equate a failed response with proof that no local record exists, and do not automatically generate another copy. A changed authorization context can prevent further inspection until the owner reviews the situation.

[Retention planning](retention.md) recognizes the immutable draft and its preparation audit as a protected dependency group. Expiry never makes either record eligible for removal. Retention inspection is local metadata only and does not refresh Manage state.

Publication requires a separately implemented and qualified destination adapter with current-state checks, tenant-specific field mapping and explicit release authority. The [enterprise guide](enterprise.md) describes the existing credential and deployment boundaries. The automated tests exercise protocol fixtures and synthetic API replies; they are separate from actual Autodesk tenant, role and workflow qualification.
