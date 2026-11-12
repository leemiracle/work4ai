# Qualification and evidence

The package separates implementation tests from Autodesk execution and engineering approval. A provider connection, schema enrollment, build hash, mock, screenshot or successful job submission cannot stand in for a licensed kernel, tenant or manufacturing check.

## Repeatable offline checks

Run `npm ci --ignore-scripts` and `npm run verify` in the plugin directory. The Node tests exercise real MCP servers/clients, a real local Python HTTP bridge, filesystem/process races and API doubles. Python tests exercise the fixed handlers with controlled Autodesk object doubles. Installed-package tests copy the distribution to a path containing spaces, remove source/dependencies, start its MCP server and complete an analytic fixture workflow.

Test the actual Codex client separately. Create a disposable private fixture profile, configure only this MCP server for the test, and preserve the exact package/contract and Codex versions. Ask Codex to inspect connection status and documents, read `fixture:param:width` in `fixture:bracket`, prepare/execute a change to `5 cm`, verify `50 mm`, then prepare/execute restoration of the exact original expression and read it back. Pass `args: {}` for `parameters.list`; the current fingerprint belongs in `expected_state`, not an invented `source_state` field. Keep shell and unrelated tools disabled. Record distinct idempotency keys, rejected attempts and actual completed tool results, not only the model's final statement. The fixture must report `live_fusion_verified: false` throughout. The observed `40 mm → 50 mm → 40 mm` round trip establishes client/tool control flow only. CLI consumption, marketplace installation in the desktop UI, a real Fusion session and engineering acceptance are separate checks.

Create a private fixture profile with `fusionctl profile-init`, then run:

```sh
node /absolute/plugin/scripts/fusionctl.mjs qualify --profile /private/profile/fixture.json --scenario /absolute/plugin/profiles/fixture-scenario.json
```

This changes one synthetic parameter, verifies analytic volume and explicitly restores the original expression. It does not validate CAD geometry.

## Licensed desktop scenario

Use a dedicated test workstation or disposable approved Fusion data, finish active commands/jobs, and capture the Fusion build, OS, architecture, Python runtime, plugin/contract hashes and transport enrollment. Do not make production documents a default test target.

The supplied `profiles/live-cad-scenario.json` is a narrow cuboid/STEP smoke test. It creates a new 20 × 30 × 40 mm solid, exports STEP and imports that exact generated artifact into a second new document. Before and after exchange it requires exactly one native root-component BRep body and zero occurrences, a solid with six faces and twelve edges, bounds from `[0, 0, 0]` to `[2, 3, 4]` cm, center of mass `[1, 1.5, 2]` cm, surface area 52 cm² and volume 24 cm³. The bounds and centroid checks also require explicit units and qualified component frames. These are fields returned by the reviewed handler, not inferred from the artifact extension or a successful export call.

It uses returned opaque references, asserts a single sketch profile before selecting it and checks exact body counts before any indexed body selection. The occurrence checks reject additional component instances in this deliberately simple fixture. Positional comparisons allow an absolute tolerance of `0.00001 cm`; area and volume allow `0.000001 cm²` and `0.000001 cm³`, respectively, each with an additional relative tolerance of `1e-8`. These are declared fixture acceptance criteria, not Autodesk accuracy guarantees. Do not silently relax tolerances after a failed run.

The workstation's new-document settings must yield a parametric design; this test does not change those settings or convert direct mode. It also expects STEP import to place this one body in the root component. A different import hierarchy fails this fixture and needs an explicitly qualified scenario, rather than choosing an arbitrary child body. The two unsaved test documents remain for deliberate review/cleanup; the scenario neither saves to cloud nor discards unsaved work.

A scenario definition is not a passing live report. This test covers metric feature inputs and their reported centimeter values, but **equivalent imperial feature creation remains a separate outstanding scenario**. It does not establish general shape equivalence, assembly preservation, material/mass or appearance preservation, editable feature-history round trips, other exchange formats, feature variants or large-model behavior. Surface area, bounds, topology counts and centroid strengthen this fixture's evidence without proving arbitrary BRep equivalence.

The additional offset-plane, sweep, loft, draft, split-body and mirror handlers have separate [CAD feature qualification requirements](cad-features.md). The cuboid/STEP smoke does not exercise them. Their API-double tests verify member types, preparation, freshness and failure reporting; each admitted variant still needs real geometry, topology, history and scope checks before an exact managed qualification can include it.

Use an expiring **assisted typed-operation test profile** to bootstrap qualification. Its `policy.operations` must explicitly include `documents.create`, `sketches.create`, `sketches.draw`, `features.extrude`, `exports.generate` and `documents.import`; effects are `local_edit` and `local_artifact`. Enable `allowUnsavedCreation` and `allowCreatedDocuments`, and configure the private `artifacts` root. Do not grant `native.invoke`, cloud compute or manufacturing release for this scenario. Managed mode can only run previously qualified write variants.

```sh
node /absolute/plugin/scripts/fusionctl.mjs qualify --live --profile /private/profile/fusion-test.json --scenario /absolute/plugin/profiles/live-cad-scenario.json
```

Only run after the exact transport has been enrolled/paired. A real report records the declared steps, input/result assertions, source/contract binding, failures and cleanup. Provider-reported Fusion execution is distinguished from independent verification. The harness never writes a passing qualification into the trusted profile automatically. A responsible engineer must assess fixture validity, assertions and applicability before an administrator enables corresponding managed operations.

The declarative format supports `read`, `change`, `artifact` and bounded `wait_job` steps, each with explicit assertions. References such as `{"$ref":"step#/result/data/entity_id"}` select earlier results using a bounded JSON pointer; there is no evaluator. Assertions support equality, finite numeric tolerance, field existence and minimum array/string length. Failed steps stop the main sequence; declared cleanup is attempted and recorded separately. A failed or unknown mutation is never silently replayed. New runs receive new IDs and must not be used to bypass an unresolved earlier outcome.

When result order is not guaranteed, select by an exact opaque identity instead of an array position. For example, the fixture's original width expression is captured with:

```json
{
  "$ref": "before#/data/parameters",
  "select": {
    "pointer": "/id",
    "equals": "fixture:param:width",
    "value_pointer": "/expression"
  }
}
```

Selection requires an array of at most 10,000 items and exactly one matching nonempty string ID. Missing, duplicate, malformed and reserved-key selections fail before the requested change is prepared. This is a JSON lookup, not JSONPath or an evaluator. Captured results remain available to explicitly scoped cleanup after a failed assertion. Any failed cleanup step appears in `cleanup.failed_step_ids` and forces `cleanup.review_required: true`, even if no documents or jobs remain. A negative assertion accepting a failed mutation receipt cannot turn failed restoration into successful cleanup.

## Separate required suites

| Qualification | Required evidence |
| --- | --- |
| CAD variants | Constrained/overconstrained sketches, parameter batch failure, unit conversions, all enabled feature variants, multiple documents, referenced assemblies, configured masters/instances, material drift, stale/split entity references and preserved timeline |
| Exchange | Each advertised format/option, real importer/exporter, shape/topology/units/mass/bounds, malformed input, translated assemblies and loss-of-information limits |
| Desktop lifecycle | Main-thread and idle-command behavior, native script module persistence, save acknowledgement vs data completion, document close, real restart/reconnect/update and proxy/certificate behavior |
| Windows/macOS | Installed paths and permissions, native credential binding, add-in loading/shutdown, supported Fusion build, Windows ACL/reparse behavior, OS updates and architecture-specific packaging |
| CAM | Entitled strategy, explicit stock/WCS/fixtures/feeds, real tool/holder/library copies, valid/outdated/empty toolpaths, exact post/machine equivalence/order, asynchronous posting, duplicate tools, operator verification and quarantined output |
| Cloud | Separate test tenants or equivalent isolation proof, CE eligibility, live current schemas, delegated/service authorization, account switch, expiration/revocation, pagination/index freshness, activity/runtime pinning and actual output validation |
| Cost/region | Account limits, provider processing cancellation, actual billing reconciliation, data region/egress/residency and whether any claimed provider hard ceiling is enforceable |
| Model evaluation | Frozen supported and ambiguous/unsupported/adversarial task sets, held-out prompts, repeated model runs, per-workflow success and independent authorization/safety scores |
| Performance and stability | Declared workstation and fixture sizes, measured control/provider latency, large-model pagination and bound failures, repeated reconnects, a 100-operation batch and multi-hour resource observation |
| Enterprise pilot | At least two representative workflows, engineering SME signoff, recipient/lifecycle authority, deployment/rollback/retention and helpdesk recovery |

No generic machine-collision result interface is advertised. Machine prove-out/release requires the responsible manufacturing process even when posting succeeds. Preview/Insider features remain separate research lanes. Test timeouts, skipped environment checks and missing credentials are incomplete evidence, not passes.

## Model evaluation release gate

Before claiming release qualification, evaluate at least 60 supported-task scenarios and 60 ambiguous, unsupported or adversarial scenarios across the advertised workflows. Use multiple paraphrases, at least three repeated model runs and a held-out set. Record the model/version, prompts, fixture provenance and plugin/provider binding so results can be reproduced. The [authored corpus and isolated MCP evaluation harness](workflow-evaluation.md) preserve these cases and distinguish locally executable synthetic scenarios from external engineering gates. The unit tests and the supplied cuboid scenario do not execute the model evaluation.

Score target/source interpretation, capability/provider selection and necessary clarification, units/scope/effects, engineering and artifact correctness, recovery and truthful reporting separately. Also record unnecessary approvals, tool calls, disclosure, time and cost. Measure unsafe or unauthorized effects independently of task completion so a successful-looking artifact cannot hide an access-control or manufacturing failure.

The original plan's proposed targets remain outstanding acceptance gates: at least 95% end-to-end success on the bounded supported-task set, every failure classified, 100% pass on deterministic authorization/tenant/unsafe-posting guard tests, and zero observed unauthorized destructive, disclosure or physical-control effects. Report per-workflow denominators and uncertainty; aggregate success must not mask a failing lane. These are targets, not measured results or a guarantee of zero future failures.

## Performance and large-model release gate

Measure plugin control overhead separately from Fusion recompute, cloud queues, model latency and network transfer. Record workstation specifications, OS/Fusion/provider versions, model and assembly complexity, network conditions, warm/cold state and sample counts. The following are proposed targets from the original plan, not claims established by the offline tests:

| Workload | Target and evidence required |
| --- | --- |
| Local schema/policy checks | p95 below 100 ms, excluding storage and provider calls |
| Local ledger status | p95 below 500 ms without a provider refresh |
| Connection/capability report | Initial response within 5 seconds for normally responding endpoints; bounded, actionable timeout otherwise |
| Small design inspection | p95 below 3 seconds on a declared reference fixture |
| Large-model inspection | Complete bounded pages within the supported limits; explicit incomplete/limit errors above them, with no silent omissions or unbounded traversal/output |
| Long operations | Prompt acknowledgement and usable status; record unavailable progress or cancellation instead of implying a safe kernel deadline |
| Stability | Repeated connect/disconnect, a 100-operation batch, large fixtures and multi-hour sessions without leaked event handlers, stale locks or unbounded memory growth |

The [local performance harness](performance.md) measures synthetic control and ledger behavior separately from the pending licensed Fusion and cloud performance lanes. Its short run does not satisfy the multi-hour session requirement.

Use increasing body, occurrence, parameter and CAM-operation counts, including fixtures at and above the documented scan/output limits. Pagination alone is not a scalability result: the current handler may still scan bounded source collections and observe document freshness before returning a page. Measure that work, response sizes and process/event-handler lifetime. Reset targets explicitly from measured baselines before making contractual promises; do not enforce an arbitrary deadline by interrupting a kernel operation without a safe cancellation contract. This performance qualification remains separate from synthetic timing tests.

See the repository validation status for actual results. Do not commit customer models, identity details, machine programs, access tokens, signed URLs or private test reports. Commit only sanitized synthetic evidence and aggregate counts.
