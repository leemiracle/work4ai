# Engineering evidence drafts

`fusion_handoff_prepare` assembles a local W12 engineering evidence draft from explicit requirements, selected desktop plans, current document observations, linked artifact receipts and review procedures. `fusion_handoff_inspect` compares that immutable draft with current source, plan and artifact evidence. Neither tool grants engineering approval, establishes regulatory compliance, runs an unavailable solver, notifies a reviewer or advances a release.

The evidence is limited to what the configured provider and stored receipts actually report. Synthetic fixture observations remain labeled synthetic. Provider observations, structural artifact checks and successful tool execution do not establish kernel, manufacturing or deployment qualification.

## Supported request

Only `title` is required. Omitted top-level arrays default to empty arrays. A draft without requirements or sources explicitly records those omissions.

| Field | Meaning and bound |
| --- | --- |
| `title` | Nonempty title, at most 300 characters. |
| `plan_ids` | Up to 100 distinct stored desktop plan IDs from this trusted profile. |
| `document_ids` | Up to 20 distinct explicit document IDs. Selected plans and typed checks also contribute source documents; the complete union must fit 20. |
| `requirements` | Up to 50 `{id, statement, reference?}` entries. Requirements are caller-supplied design intent, not independently authorized or certified requirements. |
| `assumptions` | Up to 50 `{id, statement, requirement_ids?}` entries. Assumptions remain unverified. |
| `reviewers` | Up to 30 `{id, label, role, requirement_ids?}` assignments. A label is metadata; it does not verify identity, notify anyone or record approval. |
| `checks` | Up to 50 typed read checks or manual procedures, described below. |
| `external_evidence` | Up to 50 `{id, description, reference, reported_sha256?, requirement_ids?}` references. References are not fetched; reported hashes are not verified. |

Requirement/check/reviewer/assumption/evidence IDs match `[A-Za-z][A-Za-z0-9_-]{0,63}`. Statements, descriptions and manual procedures are bounded to 4,000 characters. References are bounded to 2,048 characters. IDs and referenced lists must be unique, and requirement/reviewer links must resolve within the request. The complete request is bounded to 1 MiB and the normal finite-JSON depth/node limits. Unsupported fields such as `approved`, `solver_result`, `job_ids`, arbitrary scripts or publishing destinations are rejected.

The existing programmatic `engine.handoff(title, planIds)` call remains a compatibility shorthand. It creates a draft with selected plans and explicit missing-requirement/check gates; it does not invent acceptance criteria.

## Typed read checks and units

A typed check has this shape:

```json
{
  "id": "C_volume",
  "kind": "typed_read",
  "requirement_ids": ["R_volume"],
  "artifact_ids": [],
  "reviewer_id": "mechanical",
  "request": {
    "operation": "geometry.measure",
    "document_id": "fixture:bracket",
    "args": {
      "entity_ids": ["fixture:body:bracket"],
      "kind": "physical"
    }
  },
  "assertions": [
    {
      "kind": "numeric_range",
      "pointer": "/data/volume/value",
      "minimum": 3999,
      "maximum": 4001,
      "unit": { "pointer": "/data/volume/unit", "expected": "mm^3" }
    },
    { "kind": "equals", "pointer": "/data/analytic_fixture", "expected": true }
  ]
}
```

This example uses the synthetic fixture response shape. Discover and inspect the actual provider's operation schema, entity identities and returned value/unit fields before authoring a live check. Do not assume the fixture's fields or units match a live Fusion response.

Only `document.inspect`, `parameters.list`, `geometry.measure`, `geometry.check` and `cam.inspect` are admitted. Their arguments must pass the existing typed operation contract. A check requires 1–20 assertions. `requirement_ids` and `artifact_ids` default to empty arrays; `reviewer_id` is optional. The request requires a document ID and arguments, with an optional `expected_state`. A provided expected state is never replaced silently with a newer baseline.

`equals` compares a string, boolean or null. Numeric criteria use `numeric_range`, with at least one finite inclusive bound and an explicit unit pointer/expected string. The actual observed unit must match exactly; there is no inferred unit, numeric coercion or automatic conversion. Missing quantities or units, unsupported scalar types and observed strings longer than 2,000 characters remain unresolved. For array pointers, add identity comparisons when the item identity matters; a positional path alone does not establish which parameter or entity was measured. Pointers address bounded own JSON properties and cannot traverse reserved prototype keys or execute expressions.

The recorded status distinguishes `criteria_met`, `criteria_not_met` and `incomplete`. A met comparison is evidence of the supplied criterion only. It does not establish that the chosen criterion is sufficient for the engineering requirement.

## Manual work and pending jobs

Use a manual check when the required capability or trustworthy evidence is unavailable:

```json
{
  "id": "C_solver",
  "kind": "manual",
  "requirement_ids": ["R_load"],
  "reviewer_id": "mechanical",
  "procedure": "Run the qualified solver using the approved material, constraints and load case; retain the exact model revision and reviewed result report."
}
```

Manual checks remain `not_run`. Do not turn a caller's reported solver value, screenshot, drawing note, completed toolpath or unsigned approval statement into an automated result. External reports can be listed as unverified references with their reported hashes and required review.

Select the producing plan to retain pending or uncertain desktop job evidence. The manifest projects the already recorded job identity/status, completion marker, error outcome and effects from that plan. It does not poll the provider, make a session-scoped future durable in Fusion, or accept arbitrary job IDs/results as evidence. Use the existing job tools separately when an authorized fresh status read is needed, then prepare a new draft if the evidence changes.

## Source, plan and artifact freshness

Source documents are authorized before provider reads. Preparation observes each explicit source, binds every typed check to that fingerprint, then observes the sources again after collecting evidence. Fingerprints are bounded observations, not Autodesk document locks or universal revision counters.

Every source/check stores a `freshness` descriptor. It preserves valid handler `freshness_scope` objects and `freshness_gaps`, and records unavailable or malformed declarations. A known gap, malformed declaration, missing fingerprint, changed coverage or changed state blocks current use of dependent checks. The original scalar comparisons can remain in an incomplete check for diagnosis; they are not promoted back to a pass if a later observation becomes available.

Artifact IDs must belong to explicitly selected producing plans. Current linked evidence requires a completed version 2 receipt whose exact producer ID/hash, document, profile, handler/execution contract, preparation source and completion source all match the observed baseline. A byte-valid artifact from an older source, another document, an incomplete producer or unconfirmed completion remains historical/incomplete evidence. A legacy artifact does not gain version 2 provenance or a new validation grade. Equal file contents alone do not establish source identity or engineering fidelity.

The manifest retains each selected plan's immutable hash and complete record SHA-256. Prepared, pending, failed and unknown outcomes remain visible as unresolved plan evidence. Artifacts retain portable filenames, file hashes and declared validation/provenance metadata; host staging paths and artifact bytes are not copied into the package.

## Immutable inspection

Call `fusion_handoff_inspect` with `{ "handoff_id": "THE_RETURNED_ID" }`. Before any contextual document, plan or artifact reads, `verifyHandoffManifest(value)` checks the stored version 2 shape, byte/node/count bounds, unique IDs, reference relationships, scalar comparison consistency, required unresolved gates, false-only approval/qualification fields and content hash. It is a pure verifier also used by retention. It performs no I/O, migration, provider calls or release decision. A hash-consistent malformed record is still invalid. Older unsupported drafts are preserved without silent normalization or a new grade.

Inspection separately reports current source fingerprints/coverage, plan record hashes and statuses, and artifact receipt/producer bindings. A missing, replaced or changed plan—including newly uncertain outcomes—is reported; linked artifact checks become stale or unverifiable. Source coverage is checked again after local receipt verification. An originally incomplete/manual check stays incomplete/manual. Inspection neither reruns criteria nor rewrites the original draft. Collect new evidence into a new draft when appropriate, preserving the old record for comparison.

The current inspection includes `changed_or_unavailable_plan_ids`, `unresolved_plan_ids` and `stale_or_unverifiable_check_ids`, alongside individual rows. Read the unresolved gates and per-item outcomes rather than treating an empty list or a matching fingerprint as approval.

## Storage, redaction and boundaries

The complete stored/returned manifest is bounded to 4 MiB and finite JSON structure. Preparation can read at most 20 source baselines, 50 typed checks and 20 final source observations, plus at most 100 selected local plan/artifact records. Inspection does not poll provider jobs; it reads at most 20 initial and 20 final source observations plus the selected local records. Artifact reads retain their existing private-root, file-count, byte, symlink and content-validation limits. The package is a JSON evidence index, not a copy of every referenced file.

The shared redactor removes supported credential fields, signed query/fragment credentials and URL user information before the content hash and storage. The MCP response and later inspection use the same redactor. Assertion value/unit pointers that traverse a property hidden by that redactor are rejected before provider reads or draft creation; this rule also applies when validating stored drafts. For other pointers, any redaction change to the observed scalar, unit or expected criterion makes the comparison unresolved. Only sanitized values are retained, and equal redaction placeholders never establish equality of hidden values. Never put credentials in design intent or references. Redaction is a display/storage safeguard, not authorization to fetch an external URL or transmit the package.

Retention protects the draft and its source/plan/artifact dependencies; malformed or incompletely understood metadata must not gain disposal eligibility. Hashes detect changed content, but do not authenticate it against the local host owner. Only a separately authorized destination workflow and qualified responsible reviewer can make an external release decision. These tools perform no sending, publication, lifecycle transition or machine release.
