# Qualified reference Automation recipe

This directory contains a **disabled** reference for producing a parameterized plate from an existing, reviewed Fusion design. It is an onboarding starting point, not a preapproved tenant deployment. The shipped source fails before opening a document because `REVIEW_BINDINGS` is null. The manifest is an object with `enabled: false`, not the registry array accepted by `cloud.recipesFile`.

Use the candidate for design configuration, engineering review, or product configuration workflows. Do not use it to approve manufacturing release, update ERP/PLM records, post NC, or transfer anything to equipment.

## What the recipe does

The reviewed template must be a plain, unconfigured, parametric design containing one solid body, no component occurrences or linked design references, a healthy timeline, and four length user parameters with these exact names:

| Input | Fusion user parameter | Permitted millimetres |
| --- | --- | --- |
| `width_mm` | `Width` | 20–200 |
| `height_mm` | `Height` | 20–200 |
| `thickness_mm` | `Thickness` | 2–20 |
| `hole_diameter_mm` | `HoleDiameter` | 2–20 |

The template author must bind those parameters to the plate geometry; a parameter name alone does not establish that relationship. The recipe also rejects proportions with insufficient edge clearance or excessive thickness. Independent geometry/dimensional checks remain required.

The source opens the full frozen Data Management version URN, compares the returned item/version/project, rejects linked child references, checks the approved same-hub destination folder, resolves all required user parameters before changing any, recomputes, checks every timeline state and one positive-volume solid, and reads parameter values back. It calls `saveAs` once with a request-specific name and waits a bounded time for a different, completed DataFile. A saved candidate still reports `candidate_saved_unverified`. Save uncertainty is never converted to rollback or a guessed version ID.

The new output item/version does not exist before saving and cannot be frozen in advance. The folder identity and source version are pinned; the new item and version are recorded only after provider readback. No existing destination file is overwritten. Document processing completion is not proof of downstream Manufacturing Data Model indexing or release.

## Verified API sources and remaining qualification

The [current Autodesk TypeScript manual](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/TypeScriptSpecific_UM.htm) specifies `@adsk/fusion/automation` for service scripts and an exported `run` lifecycle. That page also contains a preview warning associated with TypeScript desktop capabilities. The reference uses the documented service module; it is not included in the plugin's Node.js typecheck, and no service `.d.ts` is fabricated or distributed here.

The [pinned Autodesk configurator source](https://github.com/autodesk-platform-services/aps-configurator-fusion/blob/9b7e21de2759ece63c7824ec60ca0ae625966057/services/da-script-setparams.ts) uses the older `@adsk/fas` import and demonstrates `adsk.parameters`, `adsk.result`, parameter editing and `saveAs`. Its setup and token handling are not copied: the sample logs request bodies, and its returned version ID remains null because upload-event handling is commented out. The reference uses safe diagnostics and bounded readback. The parameter/result channels and exported entry point must still be checked against the selected current service declarations and runtime; the two import names are not declared interchangeable.

Autodesk explicitly documents that [findFileById accepts the Data Management version URN, including `?version=N`](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Data_findFileById.htm). Other reviewed calls are [findFolderById](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Data_findFolderById.htm), [DataFile identity and child references](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/DataFile.htm), [userParameters](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Design_userParameters.htm), [unit evaluation](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/UnitsManager_evaluateExpression.htm), [saveAs](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Document_saveAs.htm), and [isComplete](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/DataFile_isComplete.htm). [computeAll](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Design_computeAll.htm) does not guarantee feature health; the source additionally checks [TimelineObject.healthState](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/TimelineObject_healthState.htm).

Authentication must follow the [July 2026 Fusion Automation authorization paths](https://aps.autodesk.com/blog/use-fusion-automation-api-without-pat): this reference expects an enterprise app-plus-user service, or a separately qualified constrained public-client activity. It does not accept a PAT, distribute a client secret, or inherit native Autodesk MCP grants.

## Administrator activation procedure

1. Copy this directory into a private deployment workspace. Obtain Autodesk-generated **service** TypeScript declarations for the intended engine/module, retain their exact version and SHA-256, and typecheck this source with those declarations and their generated module configuration. Verify `adsk.parameters`, `adsk.result`, the exported `run` lifecycle and every required service API. Do not add `any` declarations or switch import names solely to make the compiler pass.
2. Create and review a disposable plain plate template with the four parameters above. Freeze its tenant, hub, project, item, exact version URN and Data Management version-resource fingerprint. Confirm that it is not configured and has no linked dependencies. Use a dedicated same-hub candidate folder with a reviewed immutable folder identity and an approved project; record its access-control and retention review. Folders have identities, not file versions.
3. Fill `reviewBindings` and all applicable `activationRequirements` in the manifest. Replace only the null `REVIEW_BINDINGS` literal in the copied source with the reviewed bindings. This changes executable source and must be reviewed, typechecked and hashed again. The source version and destination folder are embedded in those installed bytes, not selected through arbitrary URLs or parameter expressions.
4. Publish or select a reviewed tenant activity using the exact source hash and selected engine. Resolve its numbered version and full definition hash. Record all app-bundle aliases, versions, definition hashes and package hashes if the activity uses bundles. Keep the same command/argument contract as the script: `TaskScript` contains the reviewed source and `TaskParameters` is the plugin's data envelope. The activity must not call exported `run` a second time. Qualify the legacy parameter/result channel if the selected service still requires it.
5. Configure independent Autodesk grants through the pinned enterprise adapter. This source requires the `app_with_user` path because it reads and saves Fusion project data. For public PKCE, instead provide a publisher signature **and** evidence that the provider constrains recipe, data scope and budget. A signature on a generic `TaskScript` activity does not provide that authority boundary. App-only compute cannot use this reference's user project data.
6. Establish a current estimated cost model and explicit profile admission budget. Keep `maxAttempts: 1`, one variant per workitem, bounded numeric inputs, a 300-second processing limit and sufficient delegated-token lifetime. `Autodesk.Fusion+Latest` rolls. Alias revalidation does not eliminate repointing races, estimates are not hard billing caps, and script/cloud-save byte limits are not provider-enforced storage ceilings.
7. Run an explicitly approved disposable live canary. Confirm the source version was not overwritten, exactly one new item/version was created in the pinned folder, all four parameters and dimensions are correct after reopening, there are no timeline warnings, and timeout/cancel behavior preserves uncertain outcomes. Configure the three named output validators and a final actual-cost billing reconciler. Retain their evidence; do not replace them with a success boolean or a model-supplied amount.
8. Produce a private active registry **array** containing the completed `recipe` object only. Set `script.source` to the exact reviewed source bytes, `script.sha256` to their SHA-256, `script.typeDefinitionsVersion` to the qualified service definition identity, and all activity/source/destination/cost fields to their reviewed values. The bundled template contains null values deliberately rejected by `validateAutomationRecipe`. Set `cloud.recipesFile` to that private registry and restart; registry changes invalidate the running coordinator and previously prepared plans.

Changes to source versions, source geometry, parameter mapping, destination, module, service declarations, activity/bundles, authorization mode or validation contract require new qualification and a new recipe version. A configured design or assembly needs its own reviewed recipe; extending this reference's scope without that review is unsupported.

## Running a qualified recipe

Discover approved IDs and freeze the version resource through `fusion_data_search` with `data.version`. Prepare using `fusion_cloud_job_prepare`, the recipe ID `parameterized-plate`, the four numeric inputs, one frozen source, `variantCount: 1`, and `destinationAlias: candidate-designs`. The source tuple must match the administrator's installed source bindings exactly. The returned plan includes its immutable request hash, activity evidence, destination and estimated reservation.

Submit only that stored plan through `fusion_cloud_job_submit`. Poll the stored job ID. Provider success remains `validating`; invoke `fusion_cloud_job_validate` only to run the configured host validator. `fusion_cloud_job_settle` runs the configured billing reconciler against a confirmed terminal provider job. Neither accepts caller-supplied pass/fail results or prices. The CLI equivalents are `cloud-prepare --request`, `cloud-submit --job --hash --key`, `cloud-job --job`, `cloud-validate --job`, and `cloud-settle --job`, with the same scoped profile.

`adsk.result` is a service result channel, not a guarantee that every Automation REST status response exposes that payload. The trusted validator must qualify result retrieval or locate the exact candidate in the pinned folder using the stored request identity and independent item/version evidence. Do not identify an output by display name alone. If any submission/save/result association is uncertain, retain its reservation and reconcile before making another plan.

## Local evidence

`tests/recipe-reference.test.mjs` transpiles this source and supplies an explicit synthetic Fusion API contract to test disabled activation, exact identities, input bounds, missing parameters, feature failures, save uncertainty and safe output. It does not substitute for Autodesk typechecking, Fusion kernel geometry, credentials, live billable work, or the enterprise validation/billing integration.
