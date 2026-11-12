<!-- source: DeepWiki mcp.deepwiki.com · repo OpenHands/OpenHands · page 1 Overview · fetched 2026-10-30 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.release-please-manifest.json](.release-please-manifest.json)
- [AGENTS.md](AGENTS.md)
- [README.md](README.md)
- [README.windows.md](README.windows.md)
- [__tests__/components/onboarding/onboarding-preview.test.ts](__tests__/components/onboarding/onboarding-preview.test.ts)
- [__tests__/components/shared/modals/modal-backdrop.test.tsx](__tests__/components/shared/modals/modal-backdrop.test.tsx)
- [__tests__/hooks/use-telemetry.test.tsx](__tests__/hooks/use-telemetry.test.tsx)
- [__tests__/scripts/dev-safe.test.ts](__tests__/scripts/dev-safe.test.ts)
- [config/defaults.json](config/defaults.json)
- [helm/agent-canvas/Chart.yaml](helm/agent-canvas/Chart.yaml)
- [package-lock.json](package-lock.json)
- [package.json](package.json)
- [scripts/check-sdk-version-sync.mjs](scripts/check-sdk-version-sync.mjs)
- [scripts/dev-safe.mjs](scripts/dev-safe.mjs)
- [specs/canvas-extensions.md](specs/canvas-extensions.md)
- [src/api/canvas-extensions-service.test.ts](src/api/canvas-extensions-service.test.ts)
- [src/api/canvas-extensions-service.ts](src/api/canvas-extensions-service.ts)
- [src/components/features/analytics/telemetry-consent-banner.tsx](src/components/features/analytics/telemetry-consent-banner.tsx)
- [src/components/features/canvas-extensions/canvas-extension-card.tsx](src/components/features/canvas-extensions/canvas-extension-card.tsx)
- [src/components/features/canvas-extensions/canvas-extensions-runtime.test.tsx](src/components/features/canvas-extensions/canvas-extensions-runtime.test.tsx)
- [src/components/features/canvas-extensions/canvas-extensions-runtime.tsx](src/components/features/canvas-extensions/canvas-extensions-runtime.tsx)
- [src/components/features/onboarding/onboarding-preview.ts](src/components/features/onboarding/onboarding-preview.ts)
- [src/components/shared/modals/modal-backdrop.tsx](src/components/shared/modals/modal-backdrop.tsx)
- [src/fixtures/canvas-extensions/demo-page/extension.js](src/fixtures/canvas-extensions/demo-page/extension.js)
- [src/hooks/use-telemetry.ts](src/hooks/use-telemetry.ts)
- [src/lib/index.ts](src/lib/index.ts)
- [src/types/canvas-extension.ts](src/types/canvas-extension.ts)
- [tests/e2e/mock-llm/canvas-extensions/mock-llm-canvas-extensions.spec.ts](tests/e2e/mock-llm/canvas-extensions/mock-llm-canvas-extensions.spec.ts)

</details>



## Purpose and Scope

This document provides a high-level introduction to the **Agent Canvas** (`@openhands/agent-canvas`) codebase. Agent Canvas is the React/TypeScript developer control center for the OpenHands ecosystem [README.md:3-11](). It serves as a unified frontend for managing coding agents (such as OpenHands, Claude Code, Codex, and Gemini) and orchestrating automated engineering workflows across local, remote, and cloud backends [README.md:10-11]().

Agent Canvas turns coding agents into a self-hosted, always-on engineering team capable of generating reports, responding to webhooks, and decomposing GitHub issues into tasks [README.md:33-36]().

**Related Pages**:
- For detailed system boundaries and the three-service stack, see [Architecture Overview](#1.1)
- For terminology (Backends, ACP, MCP, Workspaces), see [Key Concepts](#1.2)
- For npm packaging, CLI usage, and library entrypoints, see [Packaging and Distribution](#1.3)

Sources: [README.md:3-36](), [package.json:1-11]()

---

## System Architecture

Agent Canvas operates as part of a multi-service stack. It is responsible for the user interface and state management, while delegating agent execution and automation logic to specialized backends.

### The Three-Service Stack

The system typically runs as three coordinated services, often orchestrated via a path-based ingress proxy [config/defaults.json:15-21]():

1.  **Frontend (Agent Canvas)**: The React SPA that provides the "Control Center" UI [README.md:33-36]().
2.  **Agent Server**: A Python-based service (from `software-agent-sdk`) that executes agents and tools in sandboxed environments [AGENTS.md:30-36]().
3.  **Automation Backend**: A service that manages scheduled tasks and webhook-triggered workflows [AGENTS.md:30-36]().

### Natural Language to Code Entity Mapping

The following diagram bridges user-facing concepts to the specific code entities that implement them:

```mermaid
graph TD
    subgraph "Natural_Language_Space"
        User[""I want to start a chat""]
        UserBackend[""Connect to my local machine""]
        UserAutomation[""Run this on a schedule""]
    end

    subgraph "Code_Entity_Space"
        User -->|starts| OHConvSvc[""AgentServerConversationService [src/api/agent-server-conversation-service.ts]""]
        UserBackend -->|stored in| Reg[""BackendRegistry [src/api/backend-registry/storage.ts]""]
        UserAutomation -->|managed by| AutoSvc[""AutomationService [src/api/automation-service.api.ts]""]
    end

    OHConvSvc -->|WebSocket| WS[""ConversationWebSocketContext [src/context/websocket-context.tsx]""]
    Reg -->|Active State| Active[""ActiveBackendContext [src/api/backend-registry/active-store.ts]""]
```

Sources: [README.md:33-46](), [config/defaults.json:15-21](), [AGENTS.md:30-37]()

---

## Core System Components

### Frontend Technology Stack

The frontend is a modern React application utilizing Vite for builds and React Router 7 for navigation [package.json:22-74]().

| Technology | Role | Source Citation |
|------------|------|-----------------|
| **React 19** | UI Library | [package.json:50-51]() |
| **React Router 7** | Routing & Framework | [package.json:28-29]() |
| **Zustand** | Client State Management | [package.json:73]() |
| **TanStack Query** | Server State & Caching | [package.json:31]() |
| **Tailwind CSS** | Styling | [package.json:30]() |
| **HeroUI** | Component Library | [package.json:23]() |

### API and Integration Layer

Agent Canvas strictly separates UI logic from backend communication. It uses a typed client to interact with the agent-server to ensure type safety and architectural consistency [AGENTS.md:30-37]().

*   **@openhands/typescript-client**: The sanctioned client library to communicate with the agent-server [package.json:27]().
*   **Backend Registry**: Manages multiple backend connections (Local vs Cloud) [src/api/backend-registry/storage.ts]().
*   **Ingress Proxy**: A Node.js script that routes traffic between the frontend and various backend services [config/defaults.json:15-21]().

Sources: [package.json:22-74](), [AGENTS.md:30-37](), [config/defaults.json:15-21]()

---

## Deployment and Distribution

Agent Canvas is highly portable and can be deployed in several environments:

```mermaid
graph LR
    subgraph "Distribution_Formats"
        NPM[""@openhands/agent-canvas (NPM)""]
        Docker[""ghcr.io/openhands/agent-canvas (Docker)""]
        Electron[""Desktop App (macOS/Windows)""]
    end

    NPM -->|npx agent-canvas| Local[""Local Machine""]
    Docker -->|docker run| Container[""Sandboxed Environment""]
    Electron -->|Native App| Desktop[""Developer Workstation""]
```

### Key Version Pins
The system maintains strict versioning for its constituent services to ensure compatibility:
*   **Agent Server**: `1.54.0` [config/defaults.json:3-7]()
*   **Automation**: `1.19.3` [config/defaults.json:3-7]()
*   **Agent Canvas**: `1.27.0` [config/defaults.json:3-7]()

Sources: [README.md:70-101](), [package.json:1-3](), [config/defaults.json:3-7]()

---

## Development Workflow

The project provides several entry points for development, ranging from a full-stack experience to mock-based testing [package.json:75-96]():

*   `npm run dev`: Launches the full stack including automation [package.json:76]().
*   `npm run dev:minimal`: Launches a safe mode without the automation backend [package.json:79]().
*   `npm run dev:mock`: Launches the frontend using mock mode for offline development [package.json:81]().
*   `npm run test:e2e:mock-llm`: Runs Playwright tests against a simulated LLM environment [package.json:88]().

Sources: [package.json:75-96](), [scripts/dev-safe.mjs:1-30]()

---

