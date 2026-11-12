<!-- source: DeepWiki mcp.deepwiki.com · repo heygen-com/hyperframes · page 13 Infrastructure and Contributing · fetched 2026-11-02 -->

# Infrastructure and Contributing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.fallowrc.jsonc](.fallowrc.jsonc)
- [.github/actions/install-ffmpeg-windows/action.yml](.github/actions/install-ffmpeg-windows/action.yml)
- [.github/actions/prepare-ffmpeg-bin/action.yml](.github/actions/prepare-ffmpeg-bin/action.yml)
- [.github/actions/release-only-diff/action.yml](.github/actions/release-only-diff/action.yml)
- [.github/workflows/catalog-previews.yml](.github/workflows/catalog-previews.yml)
- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [.github/workflows/docs.yml](.github/workflows/docs.yml)
- [.github/workflows/fast-video-validation.yml](.github/workflows/fast-video-validation.yml)
- [.github/workflows/lambda-arm64-image.yml](.github/workflows/lambda-arm64-image.yml)
- [.github/workflows/player-perf.yml](.github/workflows/player-perf.yml)
- [.github/workflows/player-safari.yml](.github/workflows/player-safari.yml)
- [.github/workflows/preview-regression.yml](.github/workflows/preview-regression.yml)
- [.github/workflows/regression.yml](.github/workflows/regression.yml)
- [.github/workflows/windows-render.yml](.github/workflows/windows-render.yml)
- [bun.lock](bun.lock)
- [lefthook.yml](lefthook.yml)
- [package.json](package.json)
- [packages/engine/vitest.config.ts](packages/engine/vitest.config.ts)
- [scripts/check-test-reachability.mjs](scripts/check-test-reachability.mjs)
- [scripts/check-test-reachability.test.mjs](scripts/check-test-reachability.test.mjs)
- [scripts/ci/release-only-diff.mjs](scripts/ci/release-only-diff.mjs)
- [scripts/ci/release-only-diff.test.mjs](scripts/ci/release-only-diff.test.mjs)

</details>



## Purpose and Scope

This page maps the infrastructure that supports the HyperFrames monorepo: workspace builds, code-quality checks, CI workflows, release-related scripts, documentation validation, and contribution practices. It is an overview; use the child pages for implementation details and step-by-step guidance.

The root package defines `packages/*` as Bun workspaces and provides shared build, lint, format, test, and release-related scripts. For details, see [Monorepo Setup and Build System](#13.1). [package.json:1-29]()

Sources: [package.json:1-29]()

---

## Monorepo and Build System

The root `package.json` coordinates workspace builds and developer commands. The build script orders package builds across dependencies, while separate scripts expose tasks such as Studio development, runtime builds, and packed-manifest verification. The lockfile records the workspace packages and shared development tools. [package.json:8-21](), [bun.lock:1-27]()

Repository-level checks combine linting, formatting, tests, and targeted verification scripts. Lefthook runs selected checks during commits, including staged-file linting and formatting, TypeScript checks, and a Fallow audit. For details, see [Monorepo Setup and Build System](#13.1). [package.json:29-58](), [lefthook.yml:1-47]()

Sources: [package.json:8-21](), [package.json:29-58](), [bun.lock:1-27](), [lefthook.yml:1-47]()

---

## CI/CD and Release Process

GitHub Actions workflows validate changes at different scopes. The main CI workflow detects changed paths and includes test-reachability checks; dedicated workflows cover regression testing, preview parity, Windows rendering, player performance, catalog previews, and documentation validation. [`.github/workflows/ci.yml:1-14`](), [`.github/workflows/regression.yml:1-36`](), [`.github/workflows/preview-regression.yml:1-20`](), [`.github/workflows/windows-render.yml:1-40`](), [`.github/workflows/player-perf.yml:1-20`](), [`.github/workflows/catalog-previews.yml:1-27`](), [`.github/workflows/docs.yml:1-37`]()

The root scripts expose release preparation, version updates, and changelog drafting. For the fixed-version release workflow and publication details, see [CI/CD and Release Process](#13.2). [package.json:19-24]()

Sources: [`.github/workflows/ci.yml:1-14`](), [`.github/workflows/regression.yml:1-36`](), [`.github/workflows/preview-regression.yml:1-20`](), [`.github/workflows/windows-render.yml:1-40`](), [`.github/workflows/player-perf.yml:1-20`](), [`.github/workflows/catalog-previews.yml:1-27`](), [`.github/workflows/docs.yml:1-37`](), [package.json:19-24]()

### Infrastructure Flow: Local Changes to CI Checks

```mermaid
flowchart LR
    subgraph "Contributor Workflow"
        "LocalEdit"["Local code or docs change"]
        "Lefthook"["lefthook.yml"]
        "RootScripts"["package.json scripts"]
    end
    subgraph "GitHub Actions"
        "ChangeDetection"["ci.yml changes job"]
        "TargetedWorkflows"["regression.yml / preview-regression.yml / player-perf.yml"]
        "DocsValidation"["docs.yml validate job"]
    end
    "LocalEdit" --> "Lefthook"
    "Lefthook" --> "RootScripts"
    "LocalEdit" --> "ChangeDetection"
    "ChangeDetection" --> "TargetedWorkflows"
    "LocalEdit" --> "DocsValidation"
```

Sources: [lefthook.yml:1-47](), [package.json:29-58](), [`.github/workflows/ci.yml:73-93`](), [`.github/workflows/regression.yml:38-48`](), [`.github/workflows/preview-regression.yml:21-27`](), [`.github/workflows/player-perf.yml:21-27`](), [`.github/workflows/docs.yml:39-70`]()

For workflow triggers, path filters, regression sharding, and release orchestration, see [CI/CD and Release Process](#13.2).

Sources: [`.github/workflows/ci.yml:73-93`](), [`.github/workflows/regression.yml:38-48`]()

---

## Documentation Site

The `docs.yml` workflow validates documentation changes, checks that schemas are synchronized, verifies CLI command coverage, runs Mintlify validation, and checks links and redirects. Documentation validation is connected to changes under `docs/` and related schema and CLI files. For the docs structure and authoring details, see [Documentation Site](#13.3). [`.github/workflows/docs.yml:11-70`]()

Sources: [`.github/workflows/docs.yml:11-70`]()

---

## Contributing Guide

The repository provides shared commands for building, linting, formatting, and running tests. Lefthook runs commit-time checks, including formatting, type checks, Fallow auditing, large-file checks, and commit-message validation. Consult [Contributing Guide](#13.4) for contribution workflow, coding conventions, registry changes, and PR guidance. [package.json:12-58](), [lefthook.yml:1-73]()

Sources: [package.json:12-58](), [lefthook.yml:1-73]()

### Contributor Path: Guidance to Repository Checks

```mermaid
flowchart LR
    subgraph "Natural Language Space"
        "ContributionGuidance"["Contribution guidance"]
        "BuildAndTest"["Build and test changes"]
        "ReviewReady"["Changes ready for review"]
    end
    subgraph "Code Entity Space"
        "CONTRIBUTING"["CONTRIBUTING.md"]
        "RootPackage"["package.json"]
        "HookConfig"["lefthook.yml"]
        "CIChecks"[".github/workflows/ci.yml"]
    end
    "ContributionGuidance" --> "CONTRIBUTING"
    "BuildAndTest" --> "RootPackage"
    "BuildAndTest" --> "HookConfig"
    "ReviewReady" --> "CIChecks"
```

Sources: [package.json:12-58](), [lefthook.yml:1-73](), [`.github/workflows/ci.yml:1-14`]()

---

## Navigation

- [Monorepo Setup and Build System](#13.1) — Workspace setup, build tooling, and repository checks.
- [CI/CD and Release Process](#13.2) — Workflow design, regression jobs, and release process.
- [Documentation Site](#13.3) — Docs navigation, validation, generated catalog content, and authoring conventions.
- [Contributing Guide](#13.4) — Contribution workflow, development practices, and registry contributions.

Sources: [package.json:8-29](), [`.github/workflows/ci.yml:1-14`](), [`.github/workflows/docs.yml:11-70`]()

---

