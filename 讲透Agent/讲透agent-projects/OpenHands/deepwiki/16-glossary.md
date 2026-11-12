<!-- source: DeepWiki mcp.deepwiki.com · repo OpenHands/OpenHands · page 16 Glossary · fetched 2026-10-30 -->

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.release-please-manifest.json](.release-please-manifest.json)
- [AGENTS.md](AGENTS.md)
- [README.md](README.md)
- [README.windows.md](README.windows.md)
- [__tests__/api/agent-server-adapter.test.ts](__tests__/api/agent-server-adapter.test.ts)
- [__tests__/api/agent-server-conversation-service.test.ts](__tests__/api/agent-server-conversation-service.test.ts)
- [__tests__/api/cloud/settings-service.test.ts](__tests__/api/cloud/settings-service.test.ts)
- [__tests__/api/settings-service.test.ts](__tests__/api/settings-service.test.ts)
- [__tests__/api/use-create-conversation-metadata.test.ts](__tests__/api/use-create-conversation-metadata.test.ts)
- [__tests__/components/features/settings/mcp-settings/mcp-server-form.validation.test.tsx](__tests__/components/features/settings/mcp-settings/mcp-server-form.validation.test.tsx)
- [__tests__/hooks/mutation/use-create-conversation.test.tsx](__tests__/hooks/mutation/use-create-conversation.test.tsx)
- [__tests__/hooks/mutation/use-switch-llm-profile-and-log.test.tsx](__tests__/hooks/mutation/use-switch-llm-profile-and-log.test.tsx)
- [__tests__/scripts/dev-safe.test.ts](__tests__/scripts/dev-safe.test.ts)
- [__tests__/utils/mcp-config.test.ts](__tests__/utils/mcp-config.test.ts)
- [config/defaults.json](config/defaults.json)
- [helm/agent-canvas/Chart.yaml](helm/agent-canvas/Chart.yaml)
- [package-lock.json](package-lock.json)
- [package.json](package.json)
- [scripts/check-sdk-version-sync.mjs](scripts/check-sdk-version-sync.mjs)
- [scripts/dev-safe.mjs](scripts/dev-safe.mjs)
- [specs/llm-defaults.md](specs/llm-defaults.md)
- [src/api/agent-server-adapter.ts](src/api/agent-server-adapter.ts)
- [src/api/cloud/settings-service.api.ts](src/api/cloud/settings-service.api.ts)
- [src/api/conversation-metadata-store.ts](src/api/conversation-metadata-store.ts)
- [src/api/conversation-service/agent-server-conversation-service.api.ts](src/api/conversation-service/agent-server-conversation-service.api.ts)
- [src/api/conversation-service/agent-server-conversation-service.types.ts](src/api/conversation-service/agent-server-conversation-service.types.ts)
- [src/api/settings-service/settings-service.api.ts](src/api/settings-service/settings-service.api.ts)
- [src/components/features/automations/built-in-integration-choice-modal.tsx](src/components/features/automations/built-in-integration-choice-modal.tsx)
- [src/hooks/mutation/use-create-conversation.ts](src/hooks/mutation/use-create-conversation.ts)
- [src/hooks/mutation/use-switch-llm-profile-and-log.ts](src/hooks/mutation/use-switch-llm-profile-and-log.ts)
- [src/hooks/query/use-native-git-integrations.ts](src/hooks/query/use-native-git-integrations.ts)
- [src/i18n/translation.json](src/i18n/translation.json)
- [src/mocks/settings-handlers.ts](src/mocks/settings-handlers.ts)
- [src/services/settings.ts](src/services/settings.ts)
- [src/types/mcp-server.ts](src/types/mcp-server.ts)
- [src/types/settings.ts](src/types/settings.ts)
- [src/utils/mcp-config.ts](src/utils/mcp-config.ts)
- [src/utils/mcp-installed-servers.ts](src/utils/mcp-installed-servers.ts)
- [src/utils/mcp-server-name.ts](src/utils/mcp-server-name.ts)
- [tests/e2e/mock-llm/mcp/mock-llm-mcp-github.spec.ts](tests/e2e/mock-llm/mcp/mock-llm-mcp-github.spec.ts)
- [tests/e2e/support/onboarding-helpers.ts](tests/e2e/support/onboarding-helpers.ts)

</details>



This glossary defines codebase-specific terms, jargon, and abbreviations used throughout the Agent Canvas project. It is intended for onboarding engineers to bridge the gap between high-level concepts and their technical implementations within the React frontend and its associated orchestration scripts.

## System Architecture Concepts

Agent Canvas is a multi-service stack comprising the React frontend, an agent-server, and an automation backend.

| Term | Definition | Code Pointer |
| :--- | :--- | :--- |
| **Agent Canvas** | The React/TypeScript frontend application. | [package.json:2-4]() |
| **Agent Server** | The Python-based backend providing the REST/WebSocket API for agent execution. | [config/defaults.json:3-7]() |
| **Automation Backend** | Service managing scheduled tasks, webhooks, and long-running agent workflows. | [config/defaults.json:3-7]() |
| **Ingress Proxy** | A Node.js proxy that routes traffic between the frontend and various backends. | [scripts/dev-safe.mjs:31-40]() |
| **Runtime Services Info** | A JSON block describing reachable backend URLs injected into the agent's prompt. | [src/api/agent-server-adapter.ts:176-185]() |

### Implementation Mapping: Stack Orchestration
This diagram shows how the dev scripts associate system components with their corresponding processes and ports.

**Diagram: "Stack Orchestration Mapping"**
```mermaid
graph TD
    subgraph "Natural_Language_Space"
        "Dev_Stack"["Dev Stack"]
        "Proxy"["Ingress Proxy"]
        "Server"["Agent Server"]
    end

    subgraph "Code_Entity_Space"
        "Dev_Stack" --> "Dev_Safe"["scripts/dev-safe.mjs"]
        "Dev_Stack" --> "Dev_Automation"["scripts/dev-with-automation.mjs"]
        "Proxy" --> "Proxy_Port"["config/defaults.json"]
        "Server" --> "Server_Port"["config/defaults.json"]
    end
```
**Sources:** [scripts/dev-safe.mjs:31-48](), [config/defaults.json:15-21]()

---

## Agent and Protocol Concepts

Concepts related to how AI agents are defined and the protocols they use to communicate.

*   **ACP (Agent Client Protocol):** A standardized protocol for interacting with AI agents like Claude Code or Gemini CLI. [src/api/agent-server-adapter.ts:1-10]()
*   **Agent Kind:** A discriminator identifying the agent type (e.g., `CodeActAgent` for OpenHands vs. `ACPAgent` for ACP providers). [src/api/agent-server-adapter.ts:112-130]()
*   **MCP (Model Context Protocol):** Used for connecting agents to external tools and data sources. [src/types/mcp-server.ts:1-10]()
*   **LLM Profile:** A named configuration containing a specific model, API key, and base URL. [src/services/settings.ts:1-20]()

### Implementation Mapping: Agent Logic
The following diagram maps agent concepts to specific adapter logic and settings structures.

**Diagram: "Agent Logic Mapping"**
```mermaid
graph TD
    subgraph "Natural_Language_Space"
        "Agent_Type"["Agent Kind"]
        "ACP_Config"["ACP Settings"]
        "Start_Request"["Conversation Start"]
    end

    subgraph "Code_Entity_Space"
        "Agent_Type" --> "AgentKind_Enum"["src/types/settings.ts"]
        "ACP_Config" --> "ACP_Providers"["src/constants/acp-providers.ts"]
        "Start_Request" --> "Build_Req_Fn"["src/api/agent-server-adapter.ts:buildStartConversationRequest"]
        "Build_Req_Fn" --> "Client_Tools"["src/api/canvas-ui-client-tool.ts"]
    end
```
**Sources:** [src/api/agent-server-adapter.ts:112-150](), [src/types/settings.ts:1-15](), [src/api/canvas-ui-client-tool.ts:1-20]()

---

## Backend and Connectivity

Terminology for managing connections to different agent-server instances.

*   **Local Backend:** An agent-server running on the user's machine (typically via `uvx`). [src/api/backend-registry/active-store.ts:1-15]()
*   **Cloud Backend:** An agent-server managed by OpenHands Cloud, requiring OAuth/Device Flow. [src/api/backend-registry/auth.ts:1-15]()
*   **Backend Registry:** The frontend system that persists and manages multiple backend connections. [src/api/backend-registry/active-store.ts:1-10]()
*   **Session API Key:** A temporary, auto-generated key used for authenticating the frontend to the local stack. [scripts/dev-safe.mjs:64-85]()

| Term | Implementation | Role |
| :--- | :--- | :--- |
| **Backend Health** | `useBackendsHealth` | Hook that polls backend status and manages circuit breaking. |
| **Active Store** | `src/api/backend-registry/active-store.ts` | Zustand store for the currently selected backend. |
| **Auth Headers** | `buildAuthHeaders` | Injects `Authorization` or `X-Session-Api-Key` into requests. [src/api/backend-registry/auth.ts:1-18]() |

**Sources:** [scripts/dev-safe.mjs:64-85](), [src/api/backend-registry/active-store.ts:1-20](), [src/api/backend-registry/auth.ts:1-18]()

---

## Conversation Lifecycle

The lifecycle of a user's interaction with an agent.

*   **Conversation Metadata Store:** A local storage mechanism for persisting frontend-only UI state (like tab selection). [src/api/conversation-metadata-store.ts:1-25]()
*   **Event Store:** A Zustand store that accumulates streaming events from the WebSocket. [src/api/agent-server-adapter.ts:1-10]()
*   **Streaming Delta:** An efficient event format where the agent sends partial updates (deltas) instead of full messages. [src/api/agent-server-adapter.ts:100-115]()
*   **Workspace:** The directory context where the agent executes commands. [src/api/agent-server-config.ts:1-25]()

**Sources:** [src/api/agent-server-adapter.ts:100-115](), [src/api/conversation-metadata-store.ts:1-25](), [src/api/agent-server-config.ts:1-25]()

---

## Abbreviations

*   **ACP:** Agent Client Protocol. [src/api/agent-server-adapter.ts:1-10]()
*   **MCP:** Model Context Protocol. [src/types/mcp-server.ts:1-10]()
*   **LLM:** Large Language Model. [src/api/agent-server-adapter.ts:120-135]()
*   **GHCR:** GitHub Container Registry (where images are hosted). [config/defaults.json:10-15]()
*   **MSW:** Mock Service Worker (used for testing). [__tests__/api/agent-server-adapter.test.ts:1-20]()
*   **UV / UVX:** Python package and tool runner used for backend orchestration. [scripts/dev-safe.mjs:64-75]()

**Sources:** [src/api/agent-server-adapter.ts:1-135](), [config/defaults.json:10-15](), [scripts/dev-safe.mjs:64-75]()