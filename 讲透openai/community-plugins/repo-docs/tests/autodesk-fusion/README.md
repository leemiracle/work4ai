# Autodesk Fusion marketplace tests

Run the cold package suite from the repository root with Node.js 22.19 or newer:

```sh
npm run test:autodesk-fusion:package
```

This suite uses only Node built-ins and the committed plugin distribution. It
does not install dependencies, build the plugin, launch Autodesk, contact cloud
or model services, access a credential vault, or install a Codex plugin. Each
runtime receives an explicit CLI-created fixture profile whose state and output
paths are redirected to a disposable private directory before startup. The
environment does not inherit the user's Fusion profile or Node preload options.
These are the default synthetic provider's contracts, not a test of a missing
`FUSION_PROFILE` against the user's home directory.

The layout follows the repository's other companion suites:

- `unit/` binds the marketplace entry to its manifest, optional authentication,
  real packaged launcher, first safe prompt, skill metadata and local links, and
  checks that a CLI timeout terminates a test-owned child that ignores SIGTERM.
- `integration/` copies the installable package into a path containing spaces,
  without TypeScript source, tests or `node_modules`, then uses actual JSON-RPC
  over MCP stdio. It checks inspection, unchanged preparation, an authorized
  parameter edit and independent readback, no replay across restart, synthetic
  artifact hashes/provenance, incomplete handoff review, and CLI behavior.
- `security/` checks rejected arbitrary operations, caller approval injection,
  path traversal, absent cloud/native authority, stale or mismatched plans,
  trusted read/mutation restrictions, Manage draft denial without cloud access,
  and changed compiled-bundle rejection.
- `support/` contains the bounded dependency-free stdio client and test-owned
  package/profile cleanup. It does not emulate the Fusion server or its results.

The master command keeps the plugin's deeper suites:

```sh
npm --prefix plugins/autodesk-fusion ci --ignore-scripts
npm run test:autodesk-fusion
```

Use Python 3.12 or newer for the development API/bridge contract suite; set
`FUSION_TEST_PYTHON` to an explicit interpreter when the default `python3`
(`python` on Windows) is unavailable. The cold package tests and normal Codex
startup require neither Python nor development dependencies.

The master suite validates committed package bytes, runs these cold package
checks, builds/typechecks/tests the implementation using its declared development
dependencies, and validates the rebuilt distribution. The repository marketplace
runner discovers the matching master command from the catalog. See the
[plugin qualification guide](../../plugins/autodesk-fusion/docs/qualification.md)
and [implementation status](../../plugins/autodesk-fusion/docs/autodesk-fusion-implementation-status.md)
for the separately tracked platform and live gates.

The STEP fixture is explicitly a protocol sample, not CAD geometry. Analytic box
measurements and successful MCP calls do not qualify the Autodesk kernel, CAM,
cloud recipes, enterprise accounts, actual installed-Codex routing, or engineering
release. These companion checks neither replace the deep tests nor promote their
licensed-provider and platform skips into passes. CI results must be reported
separately after CI runs.

The single `Autodesk Fusion E2E` job in
`.github/workflows/autodesk-fusion.yml` invokes this root master sequentially on
Node 22.19, 24 and 26 on macOS. Cold-package verification, the runtime dependency
audit, a pinned host native source build and its receipt upload are steps in that
same job. There are no separate Autodesk platform or native-build jobs. See
[AGENTS.md](../../AGENTS.md) for this repository convention. Marketplace CI calls
the catalog-discovered masters, so adding a catalog entry without its matching
test command fails the shared gate. Host CI does not qualify other operating
systems; use the same master command on those hosts for platform evidence.
