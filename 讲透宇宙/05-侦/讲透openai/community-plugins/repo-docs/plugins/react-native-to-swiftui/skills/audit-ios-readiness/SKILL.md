---
name: audit-ios-readiness
description: Run a read-only App Store-readiness preflight for a declared iOS target without claiming approval or submitting anything.
---

# Audit iOS Readiness

Perform a bounded, read-only preflight for one declared iOS target after a port. This is an evidence-backed readiness report, not App Store approval.

## Required scope

Require the explicit target directory/module, bundle target or scheme when present, approved parity contract, backend/data-collection contract, and licensing/provenance record. Stop if the target, backend contract, licensing, or release expectations are ambiguous.

## Safety contract

- Do not edit metadata, entitlements, privacy manifests, assets, source, signing, provisioning, or App Store Connect records.
- Do not archive, upload, submit, notarize, create credentials, install tools, download runtimes, or accept Apple licenses.
- Do not request or expose certificates, profiles, tokens, customer data, private URLs, or production credentials.
- Inspect only the declared target and approved supporting files. Keep any optional logs under an explicitly approved disposable directory.
- Never state or imply guaranteed App Store approval.

## Preflight checks

Review what can be established locally:

- bundle identifier, version/build values, deployment target, supported devices, orientations, and required capabilities;
- `Info.plist` usage descriptions, privacy manifest declarations, tracking/data-collection claims, and backend/data-flow consistency;
- entitlements, background modes, networking/ATS choices, permissions, deep links, notifications, and account/deletion behavior when relevant;
- app icon, launch treatment, asset provenance, fonts, third-party SDK inventory, dependency licenses, and attribution;
- accessibility evidence for labels, traits, focus order, Dynamic Type, contrast, reduced motion, and assistive-technology reachability;
- release configuration, debug flags, logging, test hooks, crash paths, localization, and user-facing error/empty/offline states;
- available deterministic checks and any existing build, Simulator, or XCUITest evidence.

Consult current Apple documentation when a rule may have changed, and label an inference as such. Local checks cannot replace archive validation, App Store Connect metadata, TestFlight, legal review, or human App Review.

When available, use the bundled `scripts/native-port.mjs audit` guardrail for the bounded static pass. Treat its `preflightOnly: true` and `guaranteedApproval: false` fields as invariants, not as a substitute for the human release review below.

## Report format

Return:

1. scope and evidence inspected;
2. a table of `PASS`, `WARN`, `FAIL`, `BLOCKED`, or `NEEDS HUMAN` findings with evidence and the smallest next action;
3. privacy, permissions, accessibility, licensing, and backend-contract summaries;
4. platform gates already evidenced versus unavailable;
5. a release-owner checklist for human decisions;
6. an explicit conclusion: `preflight ready`, `preflight blocked`, or `not ready`.

Use `preflight ready` only when there are no local failures or blocked required gates; still say that it is not guaranteed App Store approval.
