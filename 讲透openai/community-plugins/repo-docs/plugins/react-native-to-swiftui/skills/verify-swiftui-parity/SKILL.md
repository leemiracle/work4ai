---
name: verify-swiftui-parity
description: Verify one approved SwiftUI feature slice against its behavioral parity contract with deterministic and conditional Apple-platform checks.
---

# Verify SwiftUI Parity

Assess evidence for one approved SwiftUI slice. Verification is contract-driven: a similar-looking screen is not proof of parity.

## Required inputs

Require the approved parity contract, explicit target directory/module, named feature slice, expected deterministic checks, and any approved platform destinations. Stop if the contract, target, backend behavior, licensing status, or parity expectations are ambiguous.

## Safety contract

- Read only the contract, declared source evidence, and explicit target directory needed for this verification.
- Do not change source, rewrite snapshots, bless new baselines, install dependencies, download Simulator runtimes, accept Apple licenses, or alter signing.
- If a command creates build products, caches, screenshots, or logs, place them only under the explicit target directory or an explicitly approved disposable verification directory.
- Never use real credentials, customer data, private URLs, or production backends. Use approved synthetic fixtures or a declared safe local test endpoint.

## Verification order

1. Check contract completeness: every required behavior, intentional native adaptation, deferred item, backend rule, persistence rule, error state, and accessibility criterion must have an evidence path.
2. Run deterministic pure-Swift/domain checks first. Require stable fixtures and fixed seeds, clocks, identifiers, locale, and time zone where relevant.
3. Inspect architecture boundaries: domain code must not import SwiftUI/UIKit; views and platform adapters should remain thin.
4. Verify backend contract behavior with synthetic fixtures or declared safe test doubles, including success, empty, loading, failure, retry, auth, and offline cases required by the contract.
5. Verify accessibility evidence for labels, hints, traits, focus order, Dynamic Type, contrast, reduced motion, and stable identifiers that apply to the slice.
6. Use the bundled `scripts/native-port.mjs verify` guardrail when available. Its result is structural deterministic evidence, not proof of behavioral parity; then run the declared build/test gate with derived data inside the allowed boundary if Xcode is available and already licensed.
7. If a compatible Simulator runtime and destination are available, run the declared Simulator smoke and XCUITest path. Do not create, install, or download a missing runtime.

## Missing-toolchain behavior

Missing Xcode, Swift, an accepted Apple license, a Simulator runtime, a bootable destination, or XCUITest support is a clear `BLOCKED` platform gate, never a pass. The bundled `scripts/native-port.mjs toolchain` guardrail reports `XCODE_TOOLCHAIN_UNAVAILABLE` when appropriate. Name the exact missing prerequisite, preserve deterministic results already obtained, and provide the smallest human-run next step without performing installation or license acceptance.

## Result format

Return a table with one row per contract behavior or gate:

- status: `PASS`, `FAIL`, `BLOCKED`, or `NOT TESTED`;
- contract requirement;
- evidence command, fixture, file, or observation;
- mismatch or missing prerequisite;
- smallest next action.

Then summarize parity confidence, files/artifacts created inside the allowed boundary, skipped platform gates, and remaining risks. Do not claim full parity while required rows are failed, blocked, or untested.
