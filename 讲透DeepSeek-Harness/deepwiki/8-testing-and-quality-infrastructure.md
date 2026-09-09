> 来源: [https://deepwiki.com/deepseek-ai/deepseek-harness/8-testing-and-quality-infrastructure](https://deepwiki.com/deepseek-ai/deepseek-harness/8-testing-and-quality-infrastructure)
> DeepWiki deepseek-ai/deepseek-harness

# Testing & Quality Infrastructure

  Relevant source files 
 - [.agents/notes/implemented/process/2026-07-27-worktree-local-lefthook.i18n.yaml](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/.agents/notes/implemented/process/2026-07-27-worktree-local-lefthook.i18n.yaml)
 - [.agents/notes/implemented/process/2026-07-27-worktree-local-lefthook.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/.agents/notes/implemented/process/2026-07-27-worktree-local-lefthook.md?plain=1)
 - [.agents/notes/implemented/process/2026-07-27-worktree-local-lefthook.zh.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/.agents/notes/implemented/process/2026-07-27-worktree-local-lefthook.zh.md?plain=1)
 - [.agents/notes/implemented/process/2026-08-08-native-windows-pull-request-ci.i18n.yaml](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/.agents/notes/implemented/process/2026-08-08-native-windows-pull-request-ci.i18n.yaml)
 - [.agents/notes/implemented/process/2026-08-08-native-windows-pull-request-ci.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/.agents/notes/implemented/process/2026-08-08-native-windows-pull-request-ci.md?plain=1)
 - [.agents/notes/implemented/process/2026-08-08-native-windows-pull-request-ci.zh.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/.agents/notes/implemented/process/2026-08-08-native-windows-pull-request-ci.zh.md?plain=1)
 - [.agents/notes/implemented/testing/2026-07-24-web-gui-browser-e2e-lane.i18n.yaml](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/.agents/notes/implemented/testing/2026-07-24-web-gui-browser-e2e-lane.i18n.yaml)
 - [.agents/notes/implemented/testing/2026-07-24-web-gui-browser-e2e-lane.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/.agents/notes/implemented/testing/2026-07-24-web-gui-browser-e2e-lane.md?plain=1)
 - [.agents/notes/implemented/testing/2026-07-24-web-gui-browser-e2e-lane.zh.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/.agents/notes/implemented/testing/2026-07-24-web-gui-browser-e2e-lane.zh.md?plain=1)
 - [.agents/notes/implemented/testing/2026-07-30-web-browser-snapshot-ci-gate.i18n.yaml](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/.agents/notes/implemented/testing/2026-07-30-web-browser-snapshot-ci-gate.i18n.yaml)
 - [.agents/notes/implemented/testing/2026-07-30-web-browser-snapshot-ci-gate.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/.agents/notes/implemented/testing/2026-07-30-web-browser-snapshot-ci-gate.md?plain=1)
 - [.agents/notes/implemented/testing/2026-07-30-web-browser-snapshot-ci-gate.zh.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/.agents/notes/implemented/testing/2026-07-30-web-browser-snapshot-ci-gate.zh.md?plain=1)
 - [.github/workflows/ci.yml](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/.github/workflows/ci.yml)
 - [.github/workflows/e2e.yml](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/.github/workflows/e2e.yml)
 - [AGENTS.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/AGENTS.md?plain=1)
 - [apps/web/tests/details-session-lifecycle.e2e.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/apps/web/tests/details-session-lifecycle.e2e.ts)
 - [apps/web/tests/hmr-live.e2e.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/apps/web/tests/hmr-live.e2e.ts)
 - [apps/web/tests/lifecycle-chrome.e2e.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/apps/web/tests/lifecycle-chrome.e2e.ts)
 - [apps/web/tests/live-interactions.e2e.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/apps/web/tests/live-interactions.e2e.ts)
 - [apps/web/tests/navigation-panes.e2e.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/apps/web/tests/navigation-panes.e2e.ts)
 - [apps/web/tests/queue-actions.e2e.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/apps/web/tests/queue-actions.e2e.ts)
 - [apps/web/tests/replay-round-trip.e2e.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/apps/web/tests/replay-round-trip.e2e.ts)
 - [apps/web/tests/seeded-history.e2e.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/apps/web/tests/seeded-history.e2e.ts)
 - [apps/web/tests/smoke-real.e2e.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/apps/web/tests/smoke-real.e2e.ts)
 - [apps/web/tests/startup-auto-selection.e2e.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/apps/web/tests/startup-auto-selection.e2e.ts)
 - [apps/web/tests/steering.e2e.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/apps/web/tests/steering.e2e.ts)
 - [apps/web/tests/subagent-interrupt.e2e.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/apps/web/tests/subagent-interrupt.e2e.ts)
 - [docs/cordis-primer.i18n.yaml](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/cordis-primer.i18n.yaml)
 - [docs/cordis-primer.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/cordis-primer.md?plain=1)
 - [docs/cordis-primer.zh.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/cordis-primer.zh.md?plain=1)
 - [docs/defensive-patterns.i18n.yaml](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/defensive-patterns.i18n.yaml)
 - [docs/defensive-patterns.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/defensive-patterns.md?plain=1)
 - [docs/defensive-patterns.zh.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/defensive-patterns.zh.md?plain=1)
 - [docs/development.i18n.yaml](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/development.i18n.yaml)
 - [docs/development.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/development.md?plain=1)
 - [docs/development.zh.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/development.zh.md?plain=1)
 - [docs/glossary.i18n.yaml](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/glossary.i18n.yaml)
 - [docs/glossary.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/glossary.md?plain=1)
 - [docs/glossary.zh.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/glossary.zh.md?plain=1)
 - [docs/testing.i18n.yaml](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/testing.i18n.yaml)
 - [docs/testing.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/testing.md?plain=1)
 - [docs/testing.zh.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/testing.zh.md?plain=1)
 - [package.json](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/package.json)
 - [packages/README.i18n.yaml](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/README.i18n.yaml)
 - [packages/README.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/README.md?plain=1)
 - [packages/README.zh.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/README.zh.md?plain=1)
 - [packages/boot/app-boot/tests/user-patches.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/boot/app-boot/tests/user-patches.spec.ts)
 - [packages/client/ui-agent-preset/src/client/AgentPresetSeat.module.css](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/ui-agent-preset/src/client/AgentPresetSeat.module.css)
 - [packages/client/ui-attachment/src/DropOverlay.module.css](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/ui-attachment/src/DropOverlay.module.css)
 - [packages/client/ui-attachment/src/DropOverlay.tsx](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/ui-attachment/src/DropOverlay.tsx)
 - [packages/client/ui-attachment/src/ImageLightbox.module.css](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/ui-attachment/src/ImageLightbox.module.css)
 - [packages/client/ui-conversation/src/client/queue/QueueDock.module.css](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/ui-conversation/src/client/queue/QueueDock.module.css)
 - [packages/client/ui-conversation/src/client/queue/QueueDock.tsx](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/ui-conversation/src/client/queue/QueueDock.tsx)
 - [packages/client/ui-conversation/src/client/skeleton/EmptyHero.tsx](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/ui-conversation/src/client/skeleton/EmptyHero.tsx)
 - [packages/client/ui-conversation/src/client/skeleton/HeroShell.module.css](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/ui-conversation/src/client/skeleton/HeroShell.module.css)
 - [packages/client/ui-settings-general/src/client/chrome.tsx](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/ui-settings-general/src/client/chrome.tsx)
 - [packages/client/ui-theme/src/styles/design-platform.css](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/ui-theme/src/styles/design-platform.css)
 - [packages/experimental/webworker-runtime/src/storage/tar.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/experimental/webworker-runtime/src/storage/tar.ts)
 - [packages/experimental/webworker-runtime/tests/node/crypto-globals.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/experimental/webworker-runtime/tests/node/crypto-globals.spec.ts)
 - [packages/experimental/webworker-runtime/tests/node/fs.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/experimental/webworker-runtime/tests/node/fs.spec.ts)
 - [packages/experimental/webworker-runtime/tests/storage/tar.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/experimental/webworker-runtime/tests/storage/tar.spec.ts)
 - [packages/schedule/schedule/tests/runtime.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/schedule/schedule/tests/runtime.spec.ts)
 - [scripts/ci-workflow.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/scripts/ci-workflow.spec.ts)
 - [scripts/install-lefthook.mjs](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/scripts/install-lefthook.mjs)
 - [scripts/install-lefthook.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/scripts/install-lefthook.spec.ts)
 - [scripts/run-gates.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/scripts/run-gates.spec.ts)
 - [scripts/run-gates.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/scripts/run-gates.ts)
 - [vitest.config.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/vitest.config.ts)
 
  The DeepSeek Harness (dsh) employs a comprehensive testing and quality infrastructure designed to uphold rigorous correctness, consistency, and cross-platform fidelity. It enforces a strict 100% per-file coverage requirement across core packages, balances rapid developer feedback with realistic end-to-end verification, and drives robust CI/CD automation that supports failover and multi-platform validation.

 This parent page provides a high-level overview of the testing tiers and quality gates and introduces how they connect. Detailed explanations of each aspect are delegated to dedicated child pages linked below.

 
---

 
## Testing Tiers & Strategy

 The testing framework follows a "real implementation over mock" philosophy, using mocks only at inherently non-deterministic boundaries such as LLM adapters, external network I/O, or clocks [apps/web/tests/scaffold.ts3-7](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/apps/web/tests/scaffold.ts#L3-L7)

 
### Unit & Integration Testing

 Core correctness is ensured by a Vitest-based test suite that enforces a hard 100% line coverage per source file for all packages. The Vitest configuration is optimized to separate thread-safe from process-bound tests, protecting stability where process-global state or environment sensitivity exists [vitest.config.ts137-154](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/vitest.config.ts#L137-L154)

 Key facets include:

 
 - **Exact Uncovered Locations Reporting:** A custom coverage reporter emits detailed `path:line:col` records where coverage lapses, aiding quick pinpointing of gaps [vitest.config.ts10-14](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/vitest.config.ts#L10-L14)
 - **Partitioned Coverage:** To scale tests on high-core runners efficiently, coverage instrumentation is sharded in-job using environment variables like `DSH_COVERAGE_PARTITIONS` [scripts/run-gates.spec.ts154-162](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/scripts/run-gates.spec.ts#L154-L162)
 - **Snapshot Testing:** Session logs and other agent outputs are tested via snapshotting to catch behavioral regressions in a lightweight, keyless manner [apps/web/tests/scaffold.ts7-12](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/apps/web/tests/scaffold.ts#L7-L12)
 
 For full details, see [Unit & Integration Testing](https://deepwiki.com/deepseek-ai/deepseek-harness/8.1-unit-and-integration-testing).

 
### Browser E2E Testing

 Higher-level browser tests exercise real UI compositions using Playwright. The `launchWebScaffold` hermetic test environment boots a minimal but realistic web app composition incorporating the vendored Loader and layered patches (`cordis.patch.yml`) to reliably exercise user interactions [apps/web/tests/scaffold.ts99-105](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/apps/web/tests/scaffold.ts#L99-L105)

 A "determinism barrier" uses host idle waits combined with browser polls to ensure UI state is stable before snapshotting, enabling CI to compare live browser output against golden aria snapshots faithfully [apps/web/tests/scaffold.ts25-27](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/apps/web/tests/scaffold.ts#L25-L27)

 For full details, see [Browser E2E Testing](https://deepwiki.com/deepseek-ai/deepseek-harness/8.2-browser-e2e-testing).

 
---

 
## CI/CD Infrastructure

 The CI pipeline is orchestrated chiefly through GitHub Actions workflows, emphasizing low latency and resilience by leveraging organization-owned 16-core runners with in-flight failover to on-premise self-hosted pools. Key elements include [scripts/ci-workflow.spec.ts59-93](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/scripts/ci-workflow.spec.ts#L59-L93) and [.agents/notes/implemented/process/2026-08-08-native-windows-pull-request-ci.md1-57](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/.agents/notes/implemented/process/2026-08-08-native-windows-pull-request-ci.md?plain=1#L1-L57):

 
### Dual Windows Strategy

 To maintain rapid Windows feedback without exhaustive blocking of Windows runner capacity, dsh uses a two-path approach:

 
 - **Wine-based Blocking Gate:** A required job named `windows` runs on `ubuntu-latest` with Wine. This job provides a fast signal validating the win32 toolchain signal essential for the aggregate verdict but does not run on native Windows [..2026-08-08-native-windows-pull-request-ci.md15](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/..2026-08-08-native-windows-pull-request-ci.md?plain=1#L15-L15)
 - **Native Windows Jobs:** An independent set of four non-blocking, parallel jobs (`windows-build`, `windows-coverage`, `windows-native-tests`, `windows-observational`) run on real Windows 2025 runners with full workspace symlinks and native PowerShell. These verify real NTFS, DACL, ConPTY, and native process behaviors [..2026-08-08-native-windows-pull-request-ci.md17-19](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/..2026-08-08-native-windows-pull-request-ci.md?plain=1#L17-L19)
 
 The blocking Wine gate remains a dependency for the `all checks passed` verdict, while the native Windows jobs provide detailed fidelity signals without delaying the final verdict.

 
### Failover & Scalability

 Failover repository variables `DSH_CI_FAILOVER_LINUX` and `DSH_CI_FAILOVER_WINDOWS` allow dynamic rerouting of Linux and Windows jobs to self-hosted runners (`vm-backup` and `dsh-win-ci` pools) without code changes or merges, enhancing CI resilience [scripts/ci-workflow.spec.ts27-38](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/scripts/ci-workflow.spec.ts#L27-L38)

 Workflows isolate pnpm and other tool setups per runner instance to avoid caching conflicts [scripts/ci-workflow.spec.ts10-56](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/scripts/ci-workflow.spec.ts#L10-L56) Coverage jobs partition test runs and support exempt-heavy suites that run non-instrumented tests concurrently to contain resource contention.

 For full details, see [CI/CD Pipeline](https://deepwiki.com/deepseek-ai/deepseek-harness/8.3-cicd-pipeline).

 
---

 
## Quality Gate Architecture

 This section presents key high-level diagrams linking human action, code entities, and CI jobs to illustrate how tests and gates compose into an integrated quality assurance system.

 
### Quality Gate Flow

 
```

```

 This flow shows how developer-initiated test runs involve scripts and config files that ultimately feed recognized jobs in the CI pipeline. The required verdict aggregates coverage, static, and Wine-based windows validation results. Native Windows jobs contribute non-blocking signals.

 **Sources:** [vitest.config.ts1-13](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/vitest.config.ts#L1-L13) [scripts/run-gates.ts1-114](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/scripts/run-gates.ts#L1-L114) [scripts/ci-workflow.spec.ts59-93](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/scripts/ci-workflow.spec.ts#L59-L93)

 
---

 
### CI Runner & Environment Mapping

 
```

```

 This diagram highlights how failover repository variables gate runner capacity allocation for Linux and Windows jobs. Partitioned coverage is explicitly enabled through environment features.

 **Sources:** [scripts/ci-workflow.spec.ts67-72](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/scripts/ci-workflow.spec.ts#L67-L72) [scripts/run-gates.spec.ts154-162](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/scripts/run-gates.spec.ts#L154-L162) [.agents/notes/implemented/process/2026-08-08-native-windows-pull-request-ci.md21-23](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/.agents/notes/implemented/process/2026-08-08-native-windows-pull-request-ci.md?plain=1#L21-L23)

 
---

 
## Related Pages

 
 - [Unit & Integration Testing](https://deepwiki.com/deepseek-ai/deepseek-harness/8.1-unit-and-integration-testing) — Vitest configuration split, 100% coverage enforcement, snapshot harnesses, and test support packages.
 - [Browser E2E Testing](https://deepwiki.com/deepseek-ai/deepseek-harness/8.2-browser-e2e-testing) — Hermetic `launchWebScaffold` environment, Playwright E2E scenarios, determinism barrier, and browser snapshot CI gate.
 - [CI/CD Pipeline](https://deepwiki.com/deepseek-ai/deepseek-harness/8.3-cicd-pipeline) — GitHub Actions workflow jobs, failover runbooks, Windows dual-path gating, and concurrency tuning.
 
 
---

 **Sources:**

 
 - [vitest.config.ts1-154](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/vitest.config.ts#L1-L154)
 - [apps/web/tests/scaffold.ts1-105](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/apps/web/tests/scaffold.ts#L1-L105)
 - [.agents/notes/implemented/process/2026-08-08-native-windows-pull-request-ci.md1-57](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/.agents/notes/implemented/process/2026-08-08-native-windows-pull-request-ci.md?plain=1#L1-L57)
 - [scripts/ci-workflow.spec.ts1-109](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/scripts/ci-workflow.spec.ts#L1-L109)
 - [scripts/run-gates.spec.ts90-168](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/scripts/run-gates.spec.ts#L90-L168)
