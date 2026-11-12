---
name: port-react-native-slice
description: Port one explicitly approved React Native or Expo feature slice into a declared SwiftUI target while preserving its parity contract.
---

# Port a React Native Slice

Implement one approved vertical slice from an existing parity contract. Reimplement behavior deliberately; do not perform generic JSX-to-Swift translation.

## Safety contract

Before writing, require:

- one explicitly approved feature slice and its current parity contract;
- one explicit target directory and target module;
- an approved backend contract and licensing/provenance decision;
- permission to change the named files or create named files inside the target directory.

Stop without edits if source scope, target module, backend contract, licensing, parity expectations, or file ownership is ambiguous. A broad request such as “port the app” is not approval for multiple slices.

## Write boundary

- Resolve the declared target directory before editing and keep every source, test, fixture, cache, and generated output write inside it or an explicitly approved disposable verification directory.
- Do not write into the React Native source, plugin package, repository root, sibling modules, home directory, or unrelated paths.
- Do not overwrite unrelated Swift files. Inspect a candidate file first; if it contains unrelated behavior or ownership is unclear, stop and propose a narrower patch or a new file within the target.
- Do not install Xcode, XcodeGen, Simulator runtimes, packages, or accept Apple licenses.
- Do not copy source, assets, submodules, private links, credentials, generated artifacts, or customer data. Use original or properly licensed assets and synthetic fixture data.
- Before editing, run the bundled `scripts/native-port.mjs authorize-write` guardrail when available. It performs no writes and must authorize every approved relative file; a refusal is a stop condition.

## Implementation shape

1. Map each approved contract behavior to a small Swift implementation unit.
2. Put validation, state transitions, parsing, deterministic serialization, and business rules in pure Swift types or modules with no `SwiftUI` or `UIKit` import.
3. Keep SwiftUI views thin: render domain state, emit intents, and delegate platform work to narrow adapters.
4. Keep UIKit or other Apple framework bridges isolated at the edge, such as sharing, permissions, or lifecycle adapters.
5. Preserve the approved backend request/response, authentication, caching, persistence, error, and offline behavior. Never invent an endpoint, schema, credential flow, or side effect.
6. Implement approved native adaptations only when the contract explains their behavioral equivalence or intentional difference.
7. Add deterministic checks for each material domain invariant and stable synthetic fixtures for the approved path. Prefer fixed clocks, seeded randomness, stable IDs, and explicit locale/time-zone inputs.
8. Add accessibility semantics and stable identifiers called for by the contract.

## Verification during the port

Run the smallest deterministic checks that do not require new installations. If an available Xcode/Simulator/XCUITest gate is requested, keep its derived data under the allowed boundary. If a prerequisite is missing, report the exact blocked gate; do not install, download, accept a license, or claim it passed.

## Completion report

Report:

- files changed, all relative to the explicit target directory;
- contract behaviors implemented, adapted, deferred, or blocked;
- pure-Swift domain boundaries and platform adapters;
- deterministic checks run and their results;
- platform gates run, skipped, failed, or blocked;
- remaining parity, accessibility, licensing, backend, and release risks.

Do not describe the slice as complete when a required contract behavior has no evidence.
