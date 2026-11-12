<!-- source: DeepWiki mcp.deepwiki.com · repo deepseek-ai/deepseek-harness · page 8 Testing & Quality Infrastructure · fetched 2026-10-27 -->

# Testing & Quality Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.agents/notes/implemented/process/2026-07-21-serial-cross-platform-ci-reference.i18n.yaml](.agents/notes/implemented/process/2026-07-21-serial-cross-platform-ci-reference.i18n.yaml)
- [.agents/notes/implemented/process/2026-07-21-serial-cross-platform-ci-reference.md](.agents/notes/implemented/process/2026-07-21-serial-cross-platform-ci-reference.md)
- [.agents/notes/implemented/process/2026-07-21-serial-cross-platform-ci-reference.zh.md](.agents/notes/implemented/process/2026-07-21-serial-cross-platform-ci-reference.zh.md)
- [.agents/notes/implemented/process/2026-07-26-ci-failover-runbook.i18n.yaml](.agents/notes/implemented/process/2026-07-26-ci-failover-runbook.i18n.yaml)
- [.agents/notes/implemented/process/2026-07-26-ci-failover-runbook.md](.agents/notes/implemented/process/2026-07-26-ci-failover-runbook.md)
- [.agents/notes/implemented/process/2026-07-26-ci-failover-runbook.zh.md](.agents/notes/implemented/process/2026-07-26-ci-failover-runbook.zh.md)
- [.agents/notes/implemented/process/2026-08-08-native-windows-pull-request-ci.i18n.yaml](.agents/notes/implemented/process/2026-08-08-native-windows-pull-request-ci.i18n.yaml)
- [.agents/notes/implemented/process/2026-08-08-native-windows-pull-request-ci.md](.agents/notes/implemented/process/2026-08-08-native-windows-pull-request-ci.md)
- [.agents/notes/implemented/process/2026-08-08-native-windows-pull-request-ci.zh.md](.agents/notes/implemented/process/2026-08-08-native-windows-pull-request-ci.zh.md)
- [.github/AGENTS.md](.github/AGENTS.md)
- [.github/workflows/build-exe-for-python-sdk.yml](.github/workflows/build-exe-for-python-sdk.yml)
- [.github/workflows/ci-master.yml](.github/workflows/ci-master.yml)
- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [.github/workflows/docs-pages.yml](.github/workflows/docs-pages.yml)
- [.github/workflows/e2e.yml](.github/workflows/e2e.yml)
- [.github/workflows/pi-ai-provider-e2e.yml](.github/workflows/pi-ai-provider-e2e.yml)
- [.github/workflows/sandbox.yml](.github/workflows/sandbox.yml)
- [.gitlab-ci.yml](.gitlab-ci.yml)
- [AGENTS.md](AGENTS.md)
- [docs/development.i18n.yaml](docs/development.i18n.yaml)
- [docs/development.md](docs/development.md)
- [docs/development.zh.md](docs/development.zh.md)
- [package.json](package.json)
- [packages/README.i18n.yaml](packages/README.i18n.yaml)
- [packages/README.md](packages/README.md)
- [packages/README.zh.md](packages/README.zh.md)
- [packages/llm/llm-pi-ai/tests/provider-apis.e2e.ts](packages/llm/llm-pi-ai/tests/provider-apis.e2e.ts)
- [packages/sandbox/sandbox-local/tests/packed-install.e2e.ts](packages/sandbox/sandbox-local/tests/packed-install.e2e.ts)
- [scripts/AGENTS.md](scripts/AGENTS.md)
- [scripts/ci-compatible-selfhosted.spec.ts](scripts/ci-compatible-selfhosted.spec.ts)
- [scripts/ci-workflow.spec.ts](scripts/ci-workflow.spec.ts)
- [scripts/run-gates.spec.ts](scripts/run-gates.spec.ts)
- [scripts/run-gates.ts](scripts/run-gates.ts)
- [tsconfig.json](tsconfig.json)
- [vitest.config.ts](vitest.config.ts)

</details>



The DeepSeek Harness (`dsh`) incorporates a comprehensive testing and quality infrastructure to ensure robust correctness, consistency across platforms, and maintainable code quality [docs/development.md:1-5](). Its strategy enforces a strict per-file 100% coverage requirement on core packages, efficiently balances fast developer feedback with reliable end-to-end testing, and orchestrates a resilient CI/CD pipeline with failover capabilities and multi-platform validation [.github/workflows/ci.yml:27-41]().

This page provides a high-level overview of the testing tiers and quality gates, detailing how they interconnect within the development and CI environments. Detailed technical treatments are delegated to the child pages.

Sources: [docs/development.md:1-5](), [.github/workflows/ci.yml:27-41]()

---

## Unit & Integration Testing

Core correctness guarantees come from a Vitest-based test framework that enforces 100% line coverage in every source file across packages [vitest.config.ts:10-14](). The testing configuration carefully distinguishes thread-safe tests from those requiring a process-bound environment due to global state or side-effect sensitivities. Custom reporters output precise locations for uncovered code, while partitioned test execution shards suites within CI jobs using environment variables like `DSH_COVERAGE_PARTITIONS` [scripts/run-gates.spec.ts:167-175]().

For detailed configuration, thread-safe vs. process-bound splits, per-file coverage rules, snapshot testing, and test-support packages, see [Unit & Integration Testing](#8.1).

Sources: [vitest.config.ts:10-14](), [scripts/run-gates.spec.ts:167-175]()

---

## Browser E2E Testing

Higher-level validations are conducted via Playwright-driven end-to-end browser tests. These run in the hermetic `launchWebScaffold` environment which composes minimal web apps using layered patches and the vendored loader for deterministic UI behavior. Key aspects include a determinism barrier that synchronizes host idle waits with browser polling, and aria snapshot goldens to maintain UI consistency.

For further details on the E2E framework, test modes, and web snapshot CI gates, see [Browser E2E Testing](#8.2).

Sources: [package.json:62-81]()

---

## CI/CD Pipeline & Quality Gates

The CI/CD pipeline leverages GitHub Actions extensively, focusing on low-latency feedback and robustness via dedicated enterprise runners with transparent failover to on-premises self-hosted pools [.github/workflows/ci.yml:27-41](). The pipeline runs static gates (`node-24`), coverage sharding (`node-24-coverage`), consumer builds, and multi-platform validation including Wine and native Windows gates [scripts/run-gates.ts:18-37]().

For complete details on workflow structures, coverage partitions, failover runbooks, and release pipelines, see [CI/CD Pipeline](#8.3).

Sources: [.github/workflows/ci.yml:27-41](), [scripts/run-gates.ts:18-37]()

---

## Performance Benchmarks & Budgets

Performance management relies on dedicated benchmark suites housed in the `benchmarks/` workspace, covering agent-continuation, session-open, conversation-fold, and long-session-browser scenarios [AGENTS.md:72](). These are paired with frontend performance budgets and runtime performance gates to prevent regressions.

For details on benchmark suites, memory pressure tests, and performance gates, see [Performance Benchmarks & Budgets](#8.4).

Sources: [AGENTS.md:72](), [package.json:63-65]()

---

## Quality Infrastructure Architecture

The diagrams below bridge natural language intent to code entities and configuration files within the testing and CI infrastructure.

### Quality Gate Flow Overview

```mermaid
graph TD
  subgraph "Natural Language Space"
    DEV_CMD["Developer Command (`pnpm run check:ci`, `test:coverage`)"]
    CI_V["CI Aggregate Verdict (`all-checks-passed`)"]
  end

  subgraph "Code Entity Space (Scripts & Configs)"
    V_CFG["`vitest.config.ts`"]
    RUN_G["`scripts/run-gates.ts` (`Mode`, `Gate`, `runGates`)"]
    CI_SPEC["`scripts/ci-workflow.spec.ts`"]
  end

  subgraph "CI/CD Infrastructure (.github/workflows)"
    CI_MAIN["`.github/workflows/ci.yml`"]
    JOB_N24["Job: `node-24` (static analysis)"]
    JOB_COV["Job: `node-24-coverage` (coverage partitions)"]
    JOB_CONS["Job: `node-24-consumers`"]
    JOB_VERDICT["Verdict Aggregation"]
  end

  DEV_CMD --> RUN_G
  RUN_G --> V_CFG
  V_CFG --> JOB_N24
  CI_SPEC --> CI_MAIN
  JOB_N24 --> JOB_VERDICT
  JOB_COV --> JOB_VERDICT
  JOB_CONS --> JOB_VERDICT
  JOB_VERDICT --> CI_V
```

This diagram maps developer commands and CI aggregates to runner scripts (`scripts/run-gates.ts`), Vitest configurations (`vitest.config.ts`), and workflow definitions (`.github/workflows/ci.yml`).

Sources: [scripts/run-gates.ts:18-58](), [scripts/ci-workflow.spec.ts:72-92](), [.github/workflows/ci.yml:42-134]()

### CI Failover & Worker Environment Mapping

```mermaid
graph LR
  subgraph "Natural Language Space"
    FAILOVER_REQ["Failover Request (Runner Outage)"]
    COVERAGE_SHARD["Coverage Sharding Configuration"]
  end

  subgraph "Code Entity Space (Environment & Configs)"
    FAIL_L["`DSH_CI_FAILOVER_LINUX` repository variable"]
    FAIL_W["`DSH_CI_FAILOVER_WINDOWS` repository variable"]
    WORKER_ENV["`ciWorkerEnvironment()` in `scripts/run-gates.ts`"]
    TIMEOUT_ENV["`DSH_COVERAGE_TEST_TIMEOUT_MS`"]
  end

  subgraph "CI Job Entities (.github/workflows/ci.yml)"
    JOB_NODE24["`node-24` job"]
    JOB_COV["`node-24-coverage` job"]
  end

  FAILOVER_REQ --> FAIL_L
  FAILOVER_REQ --> FAIL_W
  FAIL_L --> JOB_NODE24
  FAIL_L --> JOB_COV
  WORKER_ENV --> JOB_COV
  TIMEOUT_ENV --> JOB_COV
```

This diagram illustrates how repository-level variables (`DSH_CI_FAILOVER_LINUX`) and environment adjusters (`ciWorkerEnvironment()`, `DSH_COVERAGE_TEST_TIMEOUT_MS`) configure workflow execution for resilience and sharding.

Sources: [.github/workflows/ci.yml:27-56,111-133](), [scripts/run-gates.ts:100-103]()

---

## Related Pages

- [Unit & Integration Testing](#8.1) — Vitest configuration, thread-safe vs. process-bound project split, 100% perFile coverage, snapshot testing for session logs, the ACP snapshot harness, and test-support packages.
- [Browser E2E Testing](#8.2) — The launchWebScaffold hermetic test environment, replay/record/refresh modes, Playwright scenarios, aria snapshot goldens, the determinism barrier, and the web snapshot CI gate.
- [CI/CD Pipeline](#8.3) — GitHub Actions workflow structure: node-24 primary job, coverage partitions, consumers, Wine and native Windows gates, failover runbook, release/publish workflows, issue and review-ownership automation.
- [Performance Benchmarks & Budgets](#8.4) — The benchmarks/ workspace: agent-continuation, session-open, conversation-fold, long-session-browser suites; frontend performance budgets and the session-open performance gate.

Sources: [AGENTS.md:68-72](), [package.json:58-81]()

---

