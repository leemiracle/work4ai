# Parametric CAD feature contracts

These operations extend the CAD06 feature family in the [implementation plan](autodesk-fusion-360-plugin-implementation-plan.md). They use released Fusion Python APIs through the same reviewed desktop handler, scoped plans and durable execution receipts as the existing features. They do not establish licensed kernel correctness or enable managed writes without a current, operation-specific qualification.

The generated [operation catalog](operation-catalog.json) is authoritative for request shapes and bounds. Native Fusion must be running, the selected document must be active and editable, and its parametric timeline must be at the end. The handler does not convert design mode, break references, move the timeline, unwrap occurrence proxies or silently choose another component.

## Added operations

All six use `local_edit`. Names are optional and bounded to 256 characters. Body, face and path arrays are bounded to 100 unique resolved entities; loft accepts 2–20 ordered profiles. These are plugin limits, not Autodesk capacity guarantees.

| Operation | Required inputs | Admitted variant |
| --- | --- | --- |
| `construction_planes.offset` | `plane_id`, `distance` | Parametric offset from a native construction plane or planar BRep face. Signed dimensional expressions are preserved. |
| `features.sweep` | `profile_id`, `path_entity_ids`, `operation` | One computed closed sketch profile, full open path, solid output, perpendicular orientation, zero taper/twist, no guides. Path sources are native sketch lines or BRep edges. |
| `features.loft` | `profile_ids`, `operation` | Ordered computed sketch profiles in one component; solid, nonclosed loft, free section conditions and no rails. Different section sketches are expected and permitted. |
| `features.draft` | `face_ids`, `plane_id`, `angle` | One persistent solid body, single-angle draft. Optional `symmetric`, `direction_flipped` and `tangent_chain` booleans default to false. |
| `features.split_body` | `body_ids`, `splitting_tool_id`, `extend_tool` | Persistent solid targets and one construction plane, planar BRep face or persistent surface-body cutter. The extension flag is required. |
| `features.mirror` | `body_ids`, `plane_id` | Persistent solid bodies mirrored around a construction plane or planar face, with combining disabled and originals retained. |

Sweep and loft accept `operation: new_body | join | cut | intersect`. `participant_body_ids` is mandatory for cut/intersect and invalid for new-body/join. Participants must be persistent native solids in the same editable component. Join requires exactly one solid body in that component; use new-body creation followed by explicit `features.combine` when the target would otherwise be ambiguous. Autodesk's default cut/intersect participation is broader than this contract, so the handler supplies the selected bodies and verifies that the transient input retains exactly that set before adding the feature. Null, expanded or substituted participation is rejected. [Sweep participants](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/SweepFeatureInput_participantBodies.htm), [loft participants](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/LoftFeatureInput_participantBodies.htm).

## Selection, geometry and state

Resolve handles from current inspection or successful producer results. Handles retain document, configuration, type, occurrence context and geometry observation; they are not persistent cross-session identifiers. Reinspect after a topology or construction-geometry change. A token that resolves to zero or multiple objects is not a usable selection.

Construction planes and axes expose their owner through `.component`. Their geometry is defined in the object's assembly context. The handler fingerprints finite plane origins/normals and axis origins/directions, including origin and custom construction geometry in its bounded document observation. Orientation signs are retained because offsets and pull directions depend on them. Missing or invalid geometry cannot silently supply a usable freshness token. [ConstructionPlane](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ConstructionPlane.htm), [ConstructionAxis](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ConstructionAxis.htm).

Construction-geometry summaries include an opaque entity handle, geometry fingerprint, centimeter origin, normal or direction and explicit frame. A native object's component frame is not an occurrence transform or a root-assembly coordinate. State observation does not refresh old selected handles; reading a new document state cannot make a stale plane or axis selection current.

This remains an observed-state contract, not an Autodesk editing lock. Other clients and user actions can change the model. The handler rechecks the document immediately before persistent mutation, and the broker binds every plan to its source state, profile, handler and compiled contract.

## Behavior that callers must preserve

**Offset planes.** The handler uses `ConstructionPlanes.createInput()`, `setByOffset(reference, ValueInput)` and `add()`. Positive, negative and zero offsets are dimensional expressions evaluated by Fusion; unitless numeric literals are rejected. The reference and new plane stay in the same component, avoiding an implicit cross-component creation occurrence. Returned plane handles can feed `sketches.create`. No unparameterized `setByPlane` or base-feature edit is substituted. [Offset input](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ConstructionPlaneInput_setByOffset.htm), [plane creation](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ConstructionPlanes_add.htm).

**Sweep.** The path is constructed from the explicit source collection with chaining disabled. The returned path must be valid, open and contain exactly those source entities. Fusion orders a path by connectivity; input-array order is not promised. Closed/disconnected paths and implicit additions fail before feature creation. The full-path distance settings are dimensionless fractions of one, not millimeters or centimeters. [Path creation](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Path_create.htm), [Path](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Path.htm), [SweepFeatureInput](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/SweepFeatureInput.htm).

**Loft.** Profiles must be actual computed members of their parent sketch's profile collection; the handler does not invent a `Profile.isClosed` property or accept an open profile manufactured outside that collection. Sketch computation must not be deferred. Sections are added in the requested order. Surface lofts, point sections, centerlines, rails, tangent/smooth section conditions and closed lofts remain outside this variant. [Profile](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Profile.htm), [LoftSections.add](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/LoftSections_add.htm), [LoftSection](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/LoftSection.htm).

**Draft.** The API receives a Python face list, preserving order. Autodesk derives its picked point from the first face's `pointOnFace`; the request does not control an arbitrary picked point. Only the pull-plane face must be planar, not every drafted face. The plugin admits signed nonzero angles whose magnitude is below 90 degrees. Angle sign and direction flip jointly control the result; positive does not universally mean adding or removing material. Tangent chaining can add connected faces, and symmetric draft splits faces at the parting plane, so those flags are meaningful scope choices. Two-angle draft is not included. [Draft input](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/DraftFeatures_createInput.htm), [single-angle settings](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/DraftFeatureInput_setSingleAngle.htm), [direction flip](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/DraftFeatureInput_isDirectionFlipped.htm).

**Split.** One target body is passed directly; multiple targets use one ObjectCollection. The cutter must share the native editable component and cannot be the same object as a target. A planar face belonging to a target body is a distinct explicit selection and is permitted; actual intersection still requires kernel validation. Surface cutters must be persistent non-solid bodies with faces. `extend_tool: true` authorizes extension when Fusion can perform it, without guaranteeing intersection. No unsplit copy is made and no result side is discarded. Multiple targets do not imply atomic success or exactly two output bodies. [Split input](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/SplitBodyFeatures_createInput.htm), [split settings](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/SplitBodyFeatureInput.htm).

**Mirror.** Bodies use an ObjectCollection even for a single target, and `isCombine` is always false. Originals remain and mirrored bodies remain separate; overlapping solids are possible. Feature/occurrence mirrors, stitching and automatic joining are not supplied. A later combine requires its own reviewed plan. [Mirror input](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/MirrorFeatures_createInput.htm), [combine behavior](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/MirrorFeatureInput_isCombine.htm).

## Dependent workflow and recovery

For a loft constructed from scratch:

1. Inspect the exact design and native component, then resolve a support plane by current geometry and context.
2. Create the first sketch/profile and an explicitly offset construction plane. Verify each returned handle and state.
3. Create the second sketch on the returned plane and draw its intended closed section. Reinspect its computed profile.
4. Prepare a loft with the ordered profile handles and explicit operation/participants. Execute only its unchanged plan hash under the existing grant.
5. Inspect resulting bodies, dimensions, material, feature health and unrelated state. Save or export only through separately authorized operations.

Successful feature output identifies bodies reported by Fusion as created or modified; it does not label every returned body as new. New-body/join and the body draft/split/mirror variants check for nonempty persistent solid output. Cut/intersect can remove all participating geometry, so an empty reported-body list is retained with its verification limitation. These checks are not geometric fidelity or engineering approval. [Feature body semantics](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/MirrorFeature_bodies.htm).

An invalid transient input prevents the persistent add. An exception or null result during add can have an unknown outcome. Once a feature or plane has been added, a naming or readback failure retains the effect and reports partial completion. Reconcile the exact document and receipt before any further write. There is no automatic undo, feature deletion, blind replay or claim of transactionality across the sequence.

## Required live qualification

The synthetic bracket does not simulate these six operations. It must return `FIXTURE_UNSUPPORTED` without changing its parameters. Python and protocol tests establish argument, scope, freshness and failure contracts only.

The [workflow corpus](workflow-evaluation.md) includes additional licensed-desktop cases for these features. Qualify each enabled argument variant on the recorded Fusion/OS/provider/handler/compiled contract. Use independent geometric oracles, including:

| Synthetic engineering fixture | Required real-kernel evidence |
| --- | --- |
| Signed offset plane | Expected origin, normal, component frame and parametric dependency; metric/imperial equivalence and stale-handle rejection after reference movement |
| Radius 2 mm circular section on a straight 30 mm sweep path | Expected solid volume `120π mm³`, path membership, bounds/placement and preserved unrelated bodies; compare explicit cut/intersect participants separately |
| Coaxial circular loft sections of radius 2 mm and 4 mm, separated by 30 mm | Frustum geometry and volume `280π mm³`, section order, free conditions, history and unchanged unrelated geometry |
| Single-angle 5-degree draft | Measured intended signed orientation, neutral/parting-plane behavior, exact body scope and separate tangent/symmetric/flip variants; do not infer direction from the angle's sign alone |
| 20 × 10 × 4 mm cuboid split at x = 8 mm | Result volumes 320 and 480 mm³, total 800 mm³, expected bounds, retained pieces and no implicit original copy |
| Cuboid x = 10–20, y = 0–5, z = 0–2 mm mirrored across YZ | Original retained, separate mirrored solid at x = −20–−10 mm, 100 mm³ per body, intended orientation/material and no join |

Fixture tolerances must be declared by the test owner before execution and retained with failures. The table is an acceptance specification, not a measured result. Also test wrong documents/configurations, proxies and references, temporary or surface targets, stale or unobservable construction geometry, invalid profiles/paths, rejected input setters, concurrent edits and interrupted adds. No test report automatically writes an engineering qualification or permits production use.
