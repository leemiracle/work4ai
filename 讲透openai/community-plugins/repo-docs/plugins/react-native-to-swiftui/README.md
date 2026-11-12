# React Native to SwiftUI

Modernize one bounded React Native or Expo feature slice into native SwiftUI with an evidence trail, not a generic transpiler.

Version 0.1 starts with a read-only behavioral contract, ports only an explicitly approved slice, keeps reusable domain behavior in pure Swift, verifies deterministic checks, and finishes with an App Store-readiness preflight. It puts the contract before code and does not promise App Store approval.

## Safe first run

```text
Use $plan-react-native-port to inspect only the declared React Native feature and propose a SwiftUI parity contract. Do not edit files yet.
```

Declare the smallest feature boundary you want inspected: concrete source files or a route/component, the intended iOS target module, the backend/API contract it must preserve, the relevant license or asset provenance, and what “parity” means for that slice. If any of those are unclear, the planning skill stops and names the missing decision instead of guessing.

## Workflow

1. `$plan-react-native-port` reads only the declared React Native/Expo slice and directly necessary imports, then returns a behavioral parity contract. It never edits files.
2. A human reviews and explicitly approves one feature slice, its contract, and one target directory/module.
3. `$port-react-native-slice` writes only inside that declared target directory. It reimplements behavior from the contract, keeps pure Swift domain logic separate from SwiftUI/UIKit, adds deterministic checks, and leaves unrelated Swift files alone.
4. `$verify-swiftui-parity` runs deterministic checks first, then Xcode, Simulator, and XCUITest gates when the local toolchain is already available.
5. `$audit-ios-readiness` performs a read-only release preflight and reports pass, warning, failure, blocked, and human-decision items without claiming guaranteed acceptance.

The bundled dependency-free helper, `scripts/native-port.mjs`, makes those boundaries machine-checkable. Its `plan` command emits a read-only draft with `readOnly: true` and `writesPerformed: false`; `authorize-write` authorizes only approved relative paths and still performs no writes; `verify` checks pure-Swift/UI/UI-test boundaries; `toolchain` reports `XCODE_TOOLCHAIN_UNAVAILABLE` rather than installing anything; and `audit` emits a preflight-only result with `guaranteedApproval: false`.

The helper's `verify` result is structural, deterministic evidence only; it
does not by itself prove behavioral parity. Run the approved project's domain
tests and XCUITest path when the target, scheme, and Apple toolchain are
available.

## Required inputs and stop conditions

Provide:

- the exact React Native or Expo feature files, route, or component tree allowed for inspection;
- one explicit SwiftUI target directory and target module;
- the approved parity contract or permission to create it read-only first;
- the backend request, response, persistence, authentication, and error contract used by the slice;
- licensing and provenance for source, assets, fonts, and dependencies;
- the behaviors, accessibility expectations, and intentional native adaptations that define parity.

The skills stop before implementation when source scope, target module, backend contract, licensing, or parity expectations are ambiguous. They also stop rather than overwrite unrelated Swift files, invent APIs, copy unlicensed assets, or expand a one-slice request into a whole-app rewrite.

## Permissions and authentication

Capabilities: `Read` and `Write`. This plugin has no MCP server, app dependency, external account, token, or credential flow. Its marketplace authentication policy is `ON_USE`, but using it does not require an account sign-in or credential exchange. It needs read access to the explicitly declared source and write access only to the explicitly declared target directory during an approved port. The planning and readiness-audit flows are read-only.

## Data boundary

Do not paste secrets, customer data, private repository links, or proprietary assets into a prompt. The plugin does not copy source, assets, submodules, generated artifacts, caches, or private links into its own package. Use owned synthetic fixtures for examples and tests. A port should preserve only observed behavior and approved contracts, with new or properly licensed implementation material.

Do not overwrite unrelated Swift files. Stop when ownership is unclear, and keep every approved write inside the explicit target directory.

## Toolchain behavior

Deterministic checks should run without a simulator whenever the target supports them. If Xcode, a selected simulator runtime, XCUITest, or another required Apple tool is missing, the verification skill reports a clear blocked gate and the missing prerequisite. It never installs Xcode, XcodeGen, Simulator runtimes, dependencies, or accepts Apple licenses for you.

When platform verification is available, keep build outputs and derived data inside the declared target directory or another explicitly approved disposable location. Do not mutate source merely to make a platform gate run.

## Accessibility

Parity includes usable semantics, not just screenshots. The contract and verification pass should cover meaningful labels and hints for interactive controls, focus order, Dynamic Type behavior, contrast, reduced-motion behavior where relevant, keyboard or switch-control reachability where relevant, and deterministic identifiers for the approved UI path.

Native adaptations are welcome when they are explicit in the contract—for example, replacing a JavaScript sharing dependency with an Apple-native system surface. Keep business rules, state transitions, validation, and deterministic serialization in pure Swift modules that do not import SwiftUI or UIKit; keep views and platform adapters thin.

## Limitations

- v0.1 ports one approved slice at a time; it does not translate an entire app or claim automatic syntax conversion.
- It does not infer undocumented backend behavior, recreate third-party services, or resolve licensing for you.
- It does not guarantee visual pixel parity, performance parity, App Store approval, signing, provisioning, or App Store Connect acceptance.
- Simulator and XCUITest evidence depend on an already configured local Apple toolchain.
- The readiness preflight is a useful local check, not a substitute for current Apple documentation, archive validation, TestFlight, legal review, or human App Review.

## Install and verify

From a reviewed checkout of this marketplace:

```sh
codex plugin marketplace add .
codex plugin add react-native-to-swiftui@community-plugins
```

After installation, start a new Codex task and use the safe first prompt above. Contributors can validate this package from the marketplace root:

```sh
npm run validate:react-native-to-swiftui
npm run test:react-native-to-swiftui
```

No network connection, production project, or private repository is required for the bundled synthetic-fixture checks.
