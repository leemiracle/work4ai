# React Native to SwiftUI tests

The React Native to SwiftUI suite is synthetic, offline, and deterministic.
It validates a bounded contract-first workflow without copying any application
source, requiring credentials, or installing Apple tooling.

Run from the repository root:

```sh
npm run test:react-native-to-swiftui
```

That command is the plugin's master suite. CI keeps the cold copied-package
check, Node 22.19/24/26 compatibility runs, synthetic Swift-demo E2E, and
conditional Apple-toolchain preflight inside one `React Native to SwiftUI E2E`
job instead of splitting one plugin across multiple required checks.

Tests are grouped by execution boundary:

- `unit/` checks manifest, catalog, skill metadata, and public README contracts;
- `integration/` exercises the no-write CLI, one synthetic Swift-demo E2E,
  happy and fail-closed flows, Apple-toolchain failure behavior, and
  copied-package execution;
- `security/` keeps private-material, cache, symlink, read-only planning, and
  write-boundary checks easy to audit separately.

The fixture contains only owned neutral counter examples. It contains no
customer data, credentials, private URLs, copied source, assets, submodules,
or generated artifacts.

## Required qualification coverage

Before release, the suite must demonstrate:

- manifest, marketplace, path, capability, and explicit-skill consistency;
- a read-only planning flow that mutates no declared source;
- approved-contract completeness for source scope, target module, backend,
  licensing, parity expectations, and allowed write paths;
- fail-closed ambiguous source and ambiguous target cases;
- containment of every requested write inside one explicit target directory;
- pure-Swift domain boundaries and structural SwiftUI/UI-test evidence;
- clear missing-Xcode behavior without installation or license acceptance;
- App Store-readiness output that remains a preflight, not approval;
- copied-package execution without the parent checkout or `node_modules`.

## Qualification record

Local qualification on 2026-08-25:

- `npm run test:react-native-to-swiftui`: 18 passed, 0 failed;
- `npm run validate:react-native-to-swiftui`,
  `npm run validate:marketplace`, `npm run test:marketplace`, and
  `npm run validate`: passed;
- local Apple-platform execution was blocked with
  `XCODE_TOOLCHAIN_UNAVAILABLE`; no installation was attempted.

CI results remain unclaimed until CI actually completes.
