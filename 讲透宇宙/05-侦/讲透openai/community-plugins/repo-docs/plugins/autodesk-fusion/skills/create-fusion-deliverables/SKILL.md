---
name: create-fusion-deliverables
description: Stage and verify Fusion exports, drawing PDFs, flat-pattern DXF, viewport images and local renders. Use for engineering deliverables, not automatic publication or release.
---

Inspect source identity, configuration, references, units and output purpose. Discover the exact supported export variant and information-loss limits.

Use `fusion_artifact_prepare` with an approved root alias and filename, then execute the unchanged plan through `fusion_artifact_generate`. STL units/refinement are explicit; local F3D is not an external assembly package. Existing PDF export does not imply drawing-authoring support. Never pass raw paths, overwrite candidates or use an empty render destination.

Poll pending jobs with `fusion_job_status`. A partial file is not completion. Inspect artifact hashes, sizes, structural checks and limitations with `fusion_artifact_inspect`.

Approved STEP/F3D round trips use `documents.import` into a new document and numerical measurements. A new document is not a parser sandbox; hostile inputs need a separate qualified environment.

Return evidence actually obtained. Screenshots and signatures do not prove geometry. HTML setup sheets remain quarantined active content; do not automatically open, publish, send or release them. See [qualification](../../docs/qualification.md).
