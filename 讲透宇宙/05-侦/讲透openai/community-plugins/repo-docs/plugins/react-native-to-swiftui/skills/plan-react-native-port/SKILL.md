---
name: plan-react-native-port
description: Inspect a declared React Native or Expo feature slice and produce a read-only SwiftUI behavioral parity contract before any implementation.
---

# Plan a React Native Port

Turn one explicitly declared React Native or Expo feature into a reviewable SwiftUI parity contract. This is a planning skill, not a transpiler and not permission to edit.

## Safety contract

- Do not edit files.
- Do not create, edit, delete, rename, format, generate, install, build, or commit files.
- Do not run commands that write caches, lockfiles, build products, or derived data.
- Inspect only the declared feature files and the smallest set of directly imported files needed to understand that feature. Do not crawl the whole repository.
- Treat the source as a behavioral reference. Do not copy source, assets, submodules, private links, credentials, generated artifacts, or customer data into any output.
- When available, use the bundled `scripts/native-port.mjs plan` guardrail for declared files. Its expected result is `readOnly: true` and `writesPerformed: false`; do not proceed if it reports ambiguity.

## Required declaration

Before inspecting, require all of:

- an exact source boundary: files, route, component, or directory plus its allowed direct imports;
- the intended SwiftUI target directory and target module;
- the backend contract for this slice, including request/response shapes, auth assumptions, persistence, errors, and offline behavior;
- source, asset, font, and dependency licensing/provenance;
- the parity expectations and any approved native adaptations.

If source scope, target module, backend contract, licensing, or parity expectations are missing or ambiguous, stop. Return a short missing-input list and no implementation advice that assumes an answer.

## Inspection method

1. Inventory the declared screens, components, state holders, hooks, navigation entry points, platform APIs, and directly used dependencies.
2. Trace observable user journeys, state transitions, validation, loading/empty/error states, persistence, network calls, permissions, and analytics only within the declared scope.
3. Separate behavior from implementation details. Record what a user or backend can observe; do not preserve incidental JavaScript structure.
4. Identify dependencies that should remain, be replaced by native APIs, or be deferred. State the reason and the parity impact.
5. Identify pure domain rules that can live in Swift without importing SwiftUI or UIKit.
6. Propose deterministic checks for each material invariant, including seeded randomness, fixed clocks, fixture data, or stable serialization where needed.
7. Record accessibility expectations: labels, hints, traits, focus order, Dynamic Type, contrast, reduced motion, and deterministic UI identifiers for the approved path.

## Contract output

Return a compact contract with:

- declared scope and excluded scope;
- target directory/module and allowed write boundary for a later port;
- user journeys and state-transition table;
- backend, persistence, permissions, and error contract;
- parity requirements and intentional native adaptations;
- pure-Swift domain candidates versus SwiftUI/UIKit adapters;
- deterministic check matrix and available platform gates;
- accessibility acceptance criteria;
- licensing/provenance findings;
- unresolved questions, explicit deferrals, and a go/no-go recommendation.

End by asking for explicit approval of exactly one feature slice, the contract, and the target directory/module before `$port-react-native-slice` may write anything.
