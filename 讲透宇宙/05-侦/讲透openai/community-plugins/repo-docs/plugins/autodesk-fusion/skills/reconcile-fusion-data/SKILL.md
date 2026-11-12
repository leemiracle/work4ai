---
name: reconcile-fusion-data
description: Inspect scoped Autodesk data, compare versioned BOMs, and prepare ownership-aware drafts or approved custom-property changes. Not for implicit PLM release, membership changes or CAD geometry editing.
---

Discover `fusion_data_operations_list`, then use fixed scoped reads. Preserve tenant, hub/project, version or timestamp, composition, configuration, pagination and completeness. Native Data MCP and direct APS grants are separate.

Desktop occurrence structure, assembly relations and released enterprise BOMs are different observations. `fusion_bom_inspect` labels supplied snapshots; it does not invent overrides or freshness. Missing, null, excluded, suppressed and unknown quantities remain distinct.

Compare with `fusion_bom_compare`; match exact identities or explicit evidenced mappings, never names/part numbers alone. Preserve computed, override, PLM and ERP field authority.

Use `fusion_data_changes_prepare` for a local BOM draft or trusted product-owned property update. Supplied ownership rules cannot authorize publication. Property writes require trusted rules, current-state/read-back checks and explicit acceptance of the provider's atomic-concurrency limitation. Part numbers, structural BOM and release state are not generic custom properties.

For a Manage item draft, use `fusion_manage_item_draft_prepare` with exact workspace/item IDs and reviewed scalar changes, then `fusion_manage_item_draft_inspect` with its returned ID. The [Manage guide](../../docs/manage-drafts.md) describes the required owner-controlled field registry. Caller source references are unverified metadata; never provide schemas or approval flags, infer release authority, renew an expired draft, or claim that a local draft changed the Manage item.

Execute supported plans using unchanged hashes and unique keys. Reconcile partial/unknown outcomes before another write. Enterprise publication needs a qualified destination adapter; a draft is not approval. See [enterprise](../../docs/enterprise.md).
