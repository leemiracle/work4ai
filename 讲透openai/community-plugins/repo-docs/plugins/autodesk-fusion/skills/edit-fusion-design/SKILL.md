---
name: edit-fusion-design
description: Prepare, execute and verify authorized Fusion CAD changes using resolved entities, explicit units and state-bound plans. Use for reviewed parameter, sketch, feature, assembly or configuration operations.
---

Inspect the selected document and exact operation schema. Resolve design intent, units, frame, occurrence context and configuration. Generated configuration instances and external sources are not implicitly editable.

Prepare one operation with `fusion_changes_prepare`; review inputs, effects, state and policy blockers. Execute the unchanged hash with a unique idempotency key under the existing scoped grant. Prepare dependent operations only after inspecting the previous result. Parameter batches have documented local atomicity; feature sequences and cross-system writes do not.

Preserve driving constraints and parametric history. Never convert to direct mode, break references, fetch latest versions or interrupt an active command as a convenience.

For offset planes, sweep, loft, draft, split-body and mirror, read the [CAD feature contracts](../../docs/cad-features.md). Keep native geometry in one editable component, explicit cut/intersect participants, ordered loft sections and exact sweep-path membership. Mirror creates separate bodies; split does not preserve unsplit originals. Draft's optional tangent/symmetric flags expand its effect and must be part of the reviewed request. Reinspect changed construction planes or axes before using their handles.

Verify meaningful numerical postconditions and feature health. Reinspect stale state. For partial/unknown outcomes, inspect receipts and the model before any new write; never blindly replay. `fusion_recovery_prepare` does not silently undo user work.

Saving is a separate cloud effect. Unsupported variants stay explicit. Assisted native tools require their separate broad grant and have different guarantees. See [workflow](../../README.md).
