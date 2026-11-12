<!-- source: DeepWiki mcp.deepwiki.com · repo OpenHands/OpenHands · page 15 Testing Infrastructure · fetched 2026-10-30 -->

# Testing Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [.github/workflows/docker.yml](.github/workflows/docker.yml)
- [.github/workflows/mock-llm-docker-e2e.yml](.github/workflows/mock-llm-docker-e2e.yml)
- [.github/workflows/mock-llm-e2e.yml](.github/workflows/mock-llm-e2e.yml)
- [.github/workflows/sdk-version-sync.yml](.github/workflows/sdk-version-sync.yml)
- [.screenshots/progress-event-fix.png](.screenshots/progress-event-fix.png)
- [__tests__/api/backend-registry/active-store.test.ts](__tests__/api/backend-registry/active-store.test.ts)
- [__tests__/api/backend-registry/storage.test.ts](__tests__/api/backend-registry/storage.test.ts)
- [__tests__/api/backend-registry/url-selection.test.ts](__tests__/api/backend-registry/url-selection.test.ts)
- [__tests__/api/to-app-conversation-session-key.test.ts](__tests__/api/to-app-conversation-session-key.test.ts)
- [__tests__/contexts/active-backend-context.test.tsx](__tests__/contexts/active-backend-context.test.tsx)
- [__tests__/hooks/use-backend-scoped-path.test.tsx](__tests__/hooks/use-backend-scoped-path.test.tsx)
- [__tests__/scripts/check-sdk-version-sync.test.ts](__tests__/scripts/check-sdk-version-sync.test.ts)
- [__tests__/vitest-setup-progress-event.test.ts](__tests__/vitest-setup-progress-event.test.ts)
- [docker/Dockerfile](docker/Dockerfile)
- [playwright.mock-llm-docker.config.ts](playwright.mock-llm-docker.config.ts)
- [playwright.mock-llm.config.ts](playwright.mock-llm.config.ts)
- [scripts/docker-build.mjs](scripts/docker-build.mjs)
- [specs/backend-management.md](specs/backend-management.md)
- [src/api/backend-registry/active-store.ts](src/api/backend-registry/active-store.ts)
- [src/api/backend-registry/auth.ts](src/api/backend-registry/auth.ts)
- [src/api/backend-registry/default-backend.ts](src/api/backend-registry/default-backend.ts)
- [src/api/backend-registry/storage.ts](src/api/backend-registry/storage.ts)
- [src/api/backend-registry/types.ts](src/api/backend-registry/types.ts)
- [src/api/backend-registry/url-selection.ts](src/api/backend-registry/url-selection.ts)
- [src/contexts/active-backend-context.tsx](src/contexts/active-backend-context.tsx)
- [tests/e2e/mock-llm/automations/mock-llm-automation.spec.ts](tests/e2e/mock-llm/automations/mock-llm-automation.spec.ts)
- [tests/e2e/mock-llm/reporters/done-marker-reporter.ts](tests/e2e/mock-llm/reporters/done-marker-reporter.ts)
- [tests/e2e/mock-llm/scripts/render-mock-llm-report.mjs](tests/e2e/mock-llm/scripts/render-mock-llm-report.mjs)
- [tests/e2e/mock-llm/utils/mock-llm-helpers.ts](tests/e2e/mock-llm/utils/mock-llm-helpers.ts)
- [vitest.setup.ts](vitest.setup.ts)

</details>



This document outlines the testing strategy, mock infrastructure, and End-to-End (E2E) setup for Agent Canvas. The infrastructure is designed to provide high confidence in both individual components and full-stack integration without requiring expensive LLM credentials for routine verification.

For detailed information on specific testing tiers, see the following child pages:
- [Unit and Component Testing](#15.1) — Document Vitest setup, MSW mock handlers (settings, conversation, automation, git, mcp, workspaces, agent-profiles), test-utils, the no-direct-agent-server-calls architectural test, and lint-rule tests.
- [E2E Testing with Mock LLM](#15.2) — Document the mock-LLM E2E framework: playwright configs, mock-llm-server.py, helpers, DoneMarkerReporter, test specs, live/live-acp suites, and PR report rendering.
- [Development Workflow](#15.3) — Document day-to-day development: local setup, agent-server version selection env vars, PR governance (templates, check_pr_description.py, issue readiness), code quality tooling, and release checklists.
- [Agent Skills and Verification Harness](#15.4) — Document the .agents/skills directory: domain guides (frontend-development, frontend-api-contracts, local-stack-runtime, desktop-electron, telemetry-analytics, e2e-testing, release), and the verify-openhands skill with its feature map and control-openhands.mjs / browser-daemon.mjs browser automation scripts.

## Testing Strategy Overview

Agent Canvas employs a multi-layered testing approach to ensure stability across its React frontend and the underlying agent-server/automation backends.

```mermaid
graph TD
    subgraph "Verification Layers"
        [UT/"Unit Tests (Vitest)"] --> [CT/"Component Tests (React Testing Library)"]
        [CT/"Component Tests (React Testing Library)"] --> [E2E/"E2E Tests (Playwright + Mock LLM)"]
    end

    subgraph "Infrastructure"
        [MSW/"MSW Handlers"] -.-> |"Mocks API"| [UT/"Unit Tests (Vitest)"]
        [ML/"Mock LLM Server"] -.-> |"Mocks Inference"| [E2E/"E2E Tests (Playwright + Mock LLM)"]
    end

    [E2E/"E2E Tests (Playwright + Mock LLM)"] -- "Reports" --> [DR/"DoneMarkerReporter"]
```

**Sources:** [playwright.mock-llm.config.ts:1-19](), [vitest.setup.ts:153-157]()

## Mock Infrastructure

The codebase provides two primary mock systems to facilitate isolated testing.

### API Mocking (MSW)
For unit and component tests, Agent Canvas uses **Mock Service Worker (MSW)** to intercept network requests at the service layer. This allows testing UI states (loading, error, success) without a running backend. The `server` instance is initialized in `vitest.setup.ts` [vitest.setup.ts:3-3]() and reset after each test [vitest.setup.ts:1-5]().

### Mock LLM Server
For E2E tests, a dedicated Python-based **Mock LLM Server** is used [playwright.mock-llm.config.ts:118-125](). It leverages `openhands-sdk` to simulate agent behavior without calling real LLM providers. In CI, this server is installed into a dedicated virtual environment (`.mock-llm-venv`) to avoid dependency conflicts [.github/workflows/mock-llm-e2e.yml:76-79]().

**Sources:** [vitest.setup.ts:3-5](), [.github/workflows/mock-llm-e2e.yml:73-79]()

## E2E Test Setup

The E2E suite uses Playwright to orchestrate a full-stack environment. The configuration launches multiple processes to simulate a production environment:

1.  **Mock LLM Server**: Scripted inference backend [playwright.mock-llm.config.ts:118-125]().
2.  **Agent Canvas Stack**: The production `bin/agent-canvas.mjs` entrypoint, which bundles the frontend, agent-server, and automation backend [playwright.mock-llm.config.ts:127-160]().
3.  **Public Mode Server**: A secondary instance running on `MOCK_LLM_PUBLIC_MODE_PORT` to test authentication-required scenarios [playwright.mock-llm.config.ts:39-40]().

### System Entity Map: E2E Environment

```mermaid
graph LR
    subgraph "Playwright Test Runner"
        [TH/"mock-llm-helpers.ts"]
        [SPEC/"*.spec.ts"]
    end

    subgraph "System Under Test (Docker or Local)"
        [ING/"Ingress Proxy (Port 18300)"]
        [AS/"Agent Server (uvx/pip)"]
        [AUTO/"Automation Backend (uvx/pip)"]
    end

    [SPEC/"*.spec.ts"] -- "Browser Actions" --> [ING/"Ingress Proxy (Port 18300)"]
    [ING/"Ingress Proxy (Port 18300)"] -- "/api/*" --> [AS/"Agent Server (uvx/pip)"]
    [ING/"Ingress Proxy (Port 18300)"] -- "/api/automation/*" --> [AUTO/"Automation Backend (uvx/pip)"]
    [AS/"Agent Server (uvx/pip)"] -- "Inference" --> [ML/"Mock LLM Server (Port 9999)"]
    [TH/"mock-llm-helpers.ts"] -- "Setup Trajectory" --> [ML/"Mock LLM Server (Port 9999)"]
```

**Sources:** [playwright.mock-llm.config.ts:28-40](), [playwright.mock-llm-docker.config.ts:44-54]()

## CI/CD Integration

The testing infrastructure is integrated into GitHub Actions via several specialized workflows:

| Workflow | Purpose | Key Files |
| :--- | :--- | :--- |
| **CI** | Lints, unit tests, and builds the app/library. | [.github/workflows/ci.yml:1-82]() |
| **Mock-LLM E2E** | Runs E2E specs against the `bin/agent-canvas.mjs` stack. | [.github/workflows/mock-llm-e2e.yml:1-60]() |
| **Mock-LLM Docker E2E** | Validates the all-in-one Docker image using the same specs. | [.github/workflows/mock-llm-docker-e2e.yml:1-82]() |
| **Docker** | Builds multi-arch images (amd64/arm64) for GHCR. | [.github/workflows/docker.yml:45-63]() |

### Test Lifecycle and Cleanup
To ensure test isolation, the infrastructure performs aggressive cleanup:
*   **Vitest**: Drains pending MSW callbacks and microtasks in `afterEach` and `afterAll` to prevent `ReferenceError: ProgressEvent is not defined` [vitest.setup.ts:63-137]().
*   **E2E**: The `STATE_DIR` (`.tmp/mock-llm-state`) and `AUTOMATION_DB_DIR` are recursively removed before the stack starts [playwright.mock-llm.config.ts:48-53](), [playwright.mock-llm.config.ts:139-142]().
*   **PR Artifacts**: A dedicated workflow removes temporary artifacts after completion [.github/workflows/ci.yml:83-104]().

**Sources:** [vitest.setup.ts:63-137](), [playwright.mock-llm.config.ts:48-53](), [.github/workflows/ci.yml:83-104]()

---

