# Generated desktop support matrix

Generated from the shipped typed operation registry. “Implemented” means an actual reviewed handler exists. It does not establish installed entitlement, kernel correctness or live qualification. Exact argument schemas are in `operation-catalog.json` and the MCP discovery tool.

| Operation | Effect | Implemented variant / API | Live qualification |
| --- | --- | --- | --- |
| `documents.list` | read | [List open documents and session identity](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Documents.htm) | Required |
| `documents.import` | local_edit | [Import a reviewed STEP or F3D source into a new document](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ImportManager_importToNewDocument.htm) — Runs the Autodesk parser in the Fusion process. A new document is not a parser security sandbox; only explicitly trusted inputs are allowed. | Required |
| `documents.create` | local_edit | [Create an unsaved Fusion design](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Documents_add.htm) | Required |
| `documents.open` | local_edit | [Open an explicitly pinned cloud file](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Documents_open.htm) | Required |
| `documents.activate` | local_edit | [Activate the selected open document](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Document_activate.htm) | Required |
| `documents.close` | local_edit | [Close an unmodified document without discarding edits](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Document_close.htm) | Required |
| `documents.save` | cloud_write | [Save the selected state to Autodesk cloud storage](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Document_save.htm) — Save acknowledgement is not cloud translation/index completion. | Required |
| `document.inspect` | read | [Inspect structure, units, state and feature health](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Design.htm) | Required |
| `bom.inspect` | read | [Inspect the desktop occurrence structure and explicit BOM limitations](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Component_allOccurrences.htm) — Desktop occurrence structure does not imply MFGDM BOM override quantities or released PLM authority. | Required |
| `parameters.list` | read | [List user and model parameters](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Design_allParameters.htm) | Required |
| `parameters.set` | local_edit | [Atomically update a batch of parameter expressions](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Design_modifyParameters.htm) | Required |
| `parameters.add` | local_edit | [Add a named user parameter](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/UserParameters_add.htm) | Required |
| `entities.find` | read | [Resolve bounded typed entity candidates](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Design_findEntityByToken.htm) | Required |
| `geometry.measure` | read | [Measure physical properties, bounds, distances or angles](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/MeasureManager.htm) | Required |
| `geometry.check` | read | [Inspect feature health or static interference](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Design_analyzeInterference.htm) | Required |
| `sketches.create` | local_edit | [Create a sketch on an explicit plane](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Sketches_add.htm) | Required |
| `sketches.draw` | local_edit | [Draw unit-aware sketch curves](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/SketchCurves.htm) | Required |
| `sketches.dimension` | local_edit | [Add a driving sketch dimension](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/SketchDimensions.htm) — Distance takes two sketch point IDs; diameter/radial take one sketch circle ID from the exact selected sketch. | Required |
| `sketches.constrain` | local_edit | [Apply explicit typed geometric sketch constraints](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/GeometricConstraints.htm) | Required |
| `features.extrude` | local_edit | [Create a parametric extrude feature](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ExtrudeFeatures.htm) | Required |
| `features.revolve` | local_edit | [Create a parametric revolve feature](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/RevolveFeatures.htm) | Required |
| `construction_planes.offset` | local_edit | [Create a parametric offset construction plane](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ConstructionPlaneInput_setByOffset.htm) — Uses a native construction plane or planar face in the same editable component. Signed, unit-aware offset; no design-mode conversion or implicit occurrence transform. | Required |
| `features.sweep` | local_edit | [Sweep one closed sketch profile along an explicit open path](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/SweepFeatures_createInput.htm) — Solid full-path sweep, perpendicular orientation, zero twist/taper, no guides. Native sketch lines or BRep edges only; exact path membership is checked without automatic chain expansion. Fusion determines connected path order. Cut/intersect require explicit bodies; join requires a single-body component. | Required |
| `features.loft` | local_edit | [Loft ordered closed sketch profiles into a solid](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/LoftSections_add.htm) — Two to twenty ordered native computed sketch profiles in one component; solid, nonclosed loft with free section conditions and no rails. Cut/intersect require explicit bodies; join requires a single-body component. | Required |
| `features.draft` | local_edit | [Apply a single-angle draft to explicitly selected solid-body faces](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/DraftFeatures_createInput.htm) — Faces must belong to one persistent solid body. Signed, nonzero angle with magnitude below 90 degrees is a plugin limit. Flags default false; tangent chaining may include connected faces and symmetric mode splits at the parting plane. Fusion uses the first face pointOnFace, not a caller-picked point; angle sign and direction flip jointly control direction. | Required |
| `features.split_body` | local_edit | [Split selected solid bodies with an explicit native cutting tool](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/SplitBodyFeatures_createInput.htm) — Same-component persistent solid targets and a construction plane, planar face or persistent surface-body cutter. Extension is explicit and may not succeed. No copy of unsplit originals, deletion of pieces or guaranteed resulting body count; multiple targets are not an atomic transaction. | Required |
| `features.mirror` | local_edit | [Mirror solid bodies as separate parametric bodies](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/MirrorFeatures_createInput.htm) — Same-component persistent native solid bodies and a construction plane or planar face. isCombine is always false: originals remain, mirrored bodies stay separate, and overlap is possible. Feature/occurrence mirrors and implicit joins are outside this variant. | Required |
| `features.hole` | local_edit | [Create blind holes on a planar face](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/HoleFeatures.htm) | Required |
| `features.fillet` | local_edit | [Fillet selected edge sets](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/FilletFeatures.htm) | Required |
| `features.chamfer` | local_edit | [Chamfer selected edge sets](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ChamferFeatures_createInput2.htm) | Required |
| `features.shell` | local_edit | [Shell selected body faces](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ShellFeatures.htm) | Required |
| `features.combine` | local_edit | [Combine explicitly selected bodies](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/CombineFeatures.htm) | Required |
| `features.pattern` | local_edit | [Create a circular BRep body pattern](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/CircularPatternFeatures.htm) — This reviewed variant patterns BRep bodies; feature and occurrence patterns require separate handlers. | Required |
| `components.create` | local_edit | [Create an occurrence with a new component](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Occurrences_addNewComponent.htm) | Required |
| `components.insert` | local_edit | [Insert an explicitly versioned external component](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Occurrences_addByInsert.htm) | Required |
| `components.transform` | local_edit | [Change an occurrence transform in its parent frame](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Occurrence_transform2.htm) | Required |
| `joints.create` | local_edit | [Create an as-built rigid joint](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/AsBuiltJoints.htm) | Required |
| `configurations.list` | read | [Inspect configuration rows and editability](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ConfigurationTopTable.htm) | Required |
| `configurations.activate` | local_edit | [Activate an existing configuration row](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ConfigurationRow_activate.htm) | Required |
| `materials.list` | read | [Inspect available materials](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/MaterialLibraries.htm) | Required |
| `materials.assign` | local_edit | [Assign a pinned physical material definition](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/BRepBody_material.htm) — Use the current engineering_sha256 from materials.list; same-ID library property changes invalidate assignment. | Required |
| `exports.generate` | local_artifact | [Export STEP, STL or a local Fusion archive](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ExportManager.htm) | Required |
| `drawings.export_pdf` | local_artifact | [Export all sheets of an existing drawing](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/DrawingExportManager.htm) | Required |
| `view.capture` | local_artifact | [Capture the current viewport without changing fit](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Viewport_saveAsImageFile.htm) | Required |
| `render.start` | local_artifact | [Start a local render to an explicit local destination](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Rendering_startLocalRender.htm) | Required |
| `render.status` | read | [Read a local render future](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/RenderFuture.htm) — Use the durable plugin job ID from render.start, not the raw session-scoped Fusion future ID. | Required |
| `cam.inspect` | read | [Inspect setups, operations and generation state](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/CAM.htm) | Required |
| `cam.setup_schema` | read | [Discover typed milling setup inputs and required safety fields](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Setups_createInput.htm) | Required |
| `cam.operation_schema` | read | [Discover typed parameters and entitlement for a milling strategy](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Operations_createInput.htm) | Required |
| `cam.setup_create` | local_edit | [Create a milling setup with explicit stock and fixtures](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Setups.htm) | Required |
| `cam.operation_create` | local_edit | [Create an entitled operation with typed parameters](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Operations_createInput.htm) — Managed mode requires a tool selected by full definition hash from a pinned library. Raw tool_json is an assisted-mode input. | Required |
| `cam.tools_list` | read | [Inspect tools in an approved pinned tool library](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ToolLibrary.htm) | Required |
| `cam.machining_time` | read | [Estimate machining time with explicit feed assumptions](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/CAM_getMachiningTime.htm) — Estimated time is not a measured cycle time, commercial quote or machine capability guarantee. | Required |
| `cam.setup_sheet` | local_artifact | [Generate a local HTML setup-sheet review package](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/CAM_generateSetupSheet.htm) — Review artifact only; no browser launch, sending or manufacturing signoff. | Required |
| `cam.template_apply` | local_edit | [Apply a pinned reviewed CAM template](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Setup_createFromCAMTemplate2.htm) | Required |
| `cam.generate` | local_edit | [Generate selected toolpaths and track the future](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/CAM_generateToolpath.htm) | Required |
| `cam.status` | read | [Read a toolpath generation future](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/GenerateToolpathFuture.htm) — Use the durable plugin job ID from cam.generate or cam.nc_post, not the raw session-scoped Fusion future ID. | Required |
| `cam.nc_post` | local_artifact | [Post an operator-reviewed NC candidate to quarantine](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/NCProgram_postProcess.htm) — Requires pinned post, machine and operator evidence; never transfers to equipment. | Required |
| `flatpattern.create` | local_edit | [Create a flat pattern from a stationary face](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Component_createFlatPattern.htm) | Required |
| `flatpattern.export` | local_artifact | [Export an existing sheet-metal flat pattern as DXF](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ExportManager_createDXFFlatPatternExportOptions.htm) | Required |

## Explicit boundaries

| Family | Status | Reason |
| --- | --- | --- |
| drawings.author | research_only | Automatic drawing creation is preview; existing drawing PDF export has its own released path. |
| electronics | research_only | Preview inspection is not unrestricted schematic/PCB authoring or fresh ERC/DRC execution. |
| simulation | human_handoff | Insider simulation APIs are not a released supported solver interface. |
| generative_design | human_handoff | No qualified public generation/solve API is advertised. |
| manufacturing.release | human_handoff | No structured machine collision proof or physical machine control is implemented. |
| sheet_metal.advanced | research_only | Released collection access is not authoring; fold/convert/join variants require separate API qualification. |
| ui.arbitrary | assisted_only | Native raw tools are outside the typed managed facade. They cannot provide managed-policy guarantees. |
| released_variants_outside_registry | not_implemented_in_typed_facade | Guided/surface/solid-body sweep and loft variants, two-angle draft, feature/occurrence mirrors, general surface/direct geometry authoring, motion-joint variants, appearance editing, hem/Form/mesh exchange, turning/multi-axis/additive and administration require additional reviewed handlers and live qualification. The assisted native route is separate broad authority. |

Cloud read/property/BOM/Automation/enterprise extension contracts are documented in the enterprise guide and exposed by their own discovery tools. Data and compute availability requires its own credentials, scopes, schema/recipe and account qualification. Preview APIs do not count as production coverage.

The implementation plan remains the broader roadmap. This registry does not claim every Fusion UI command, extension, API variant, business-system transition or machine process.
