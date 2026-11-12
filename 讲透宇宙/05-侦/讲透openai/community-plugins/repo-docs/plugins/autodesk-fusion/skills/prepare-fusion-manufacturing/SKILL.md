---
name: prepare-fusion-manufacturing
description: Prepare qualified Fusion CAM setups, operations, toolpaths and quarantined NC candidates using explicit manufacturing assets and authority. Never controls physical equipment.
---

Inspect CAM and discover `cam.setup_schema` / `cam.operation_schema`. A compatible strategy is not entitlement proof. Use individually qualified variants.

Resolve stock, fixtures, WCS axes/origin, clearance, feeds/speeds, machine and units from approved inputs. Do not infer safety fields from hidden defaults. Select full tool/holder hashes using `cam.tools_list`; templates, libraries, posts and machines are reviewed privileged assets.

Prepare changes with `fusion_cam_changes_prepare`, execute within scope, then explicitly generate toolpaths and poll the durable job. Inspect actual operation validity and results. Generation is not collision verification; unsupported cancellation remains unsupported.

Machining-time calls require explicit rapid/feed/tool-change assumptions and return estimates. Setup sheets are review artifacts.

NC requires exact operation order, pinned post/machine/full tooling, and an unexpired operator verification record bound to current state. Use `fusion_nc_prepare` and `fusion_nc_generate`; changed inputs invalidate review. Keep Fail/duplicate-tool safeguards and quarantine. Never transfer/start equipment or claim a launched UI proves collision safety. See [enterprise boundaries](../../docs/enterprise.md).
