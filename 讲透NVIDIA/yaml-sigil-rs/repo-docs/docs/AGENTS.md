# Documentation

These instructions supplement the repository-root
[`AGENTS.md`](../AGENTS.md) for work under `docs/`.

Keep implementation guides aligned with the code and tests in the same
change. Check the following triggers even when the implementation change
does not directly edit a Markdown file.

## Update triggers

| Document | Update when |
|----------|-------------|
| [`yaml-facade.md`](./yaml-facade.md) | Signature-document parsing, canonical serialization, the public Serde representation, the YAML facade example, or its consumer tests change. |
| [`protobuf-facade.md`](./protobuf-facade.md) | Public protobuf facade operations, wire interoperability, the Prost example dependency or message declarations, or the core-only consumer tests change. |
| [`crypto-providers.md`](./crypto-providers.md) | Public crypto types, adapter contracts, qualified or unqualified behavior, async semantics, key binding, error mapping, resource admission, integration examples, qualification call counts, operation costs, or regression coverage change. Update its three-path checklist with the evidence and remaining integrator responsibilities. |
| [`conformance-validation.md`](./conformance-validation.md) | Fixtures, fixture mappings, expected outcomes, ignored tests, advertised profiles, specification imports, attribution-only imports, public APIs exercised by conformance, or deliberate divergences change. Name the affected paths, expected outcomes, and divergence reasons. |
| [`yaml-backend-evaluation.md`](./yaml-backend-evaluation.md) | The current YAML backend, configuration, parser budgets, public Serde boundary, or interoperability evidence changes. Update the sections describing the current implementation and validation. Preserve historical evaluations as dated findings; label corrections or new evaluations explicitly. |

For a new guide, add its update triggers here and link it from the relevant
README or existing guide. For a removed or renamed guide, update this table
and incoming links in the same change. Keep README indexes and summaries
short; link to the guide that owns the detailed explanation.

## Evidence and scope

Distinguish runtime enforcement, repository regression tests, and claims an
integrator must establish for its own adapter or deployment. Keep tested and
untested behavior explicit. A finite qualification suite is narrower evidence
than complete conformance, and an optional whole-artifact limit is operational
policy. Neither changes the specification's requirements.

Name the owning crate or external contract when describing an API. Keep
public API examples synchronized with compiling rustdoc or executable example
coverage. Follow [`examples/AGENTS.md`](../examples/AGENTS.md) when changing
runnable examples and their index.

Prefer each implementation crate's `v1alpha1` namespace in guides. Explain
that default paths name the same definitions and that specification versions
are separate from crate SemVer. For bindings, document the generated
JavaScript namespace as well as the Rust surface and keep examples aligned
with the generated-API tests.

Run the repository Markdown check for documentation changes. When prose
claims a runtime behavior or test outcome changed, run the corresponding
focused tests and the repository's required validation. Keep historical
results and current evidence distinguishable.
