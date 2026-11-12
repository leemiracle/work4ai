<!-- source: DeepWiki mcp.deepwiki.com · repo OpenHands/OpenHands · page 14 API Layer and Service Adapters · fetched 2026-10-30 -->

# API Layer and Service Adapters

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [__tests__/api/agent-server-adapter.test.ts](__tests__/api/agent-server-adapter.test.ts)
- [__tests__/api/agent-server-conversation-service.test.ts](__tests__/api/agent-server-conversation-service.test.ts)
- [__tests__/api/mock-conversation-handlers.test.ts](__tests__/api/mock-conversation-handlers.test.ts)
- [__tests__/api/mock-workspaces-handlers.test.ts](__tests__/api/mock-workspaces-handlers.test.ts)
- [__tests__/api/use-create-conversation-metadata.test.ts](__tests__/api/use-create-conversation-metadata.test.ts)
- [__tests__/components/settings/agent-profiles/merge-agent-profile-save-input.test.ts](__tests__/components/settings/agent-profiles/merge-agent-profile-save-input.test.ts)
- [__tests__/hooks/mutation/use-create-conversation.test.tsx](__tests__/hooks/mutation/use-create-conversation.test.tsx)
- [__tests__/hooks/mutation/use-switch-llm-profile-and-log.test.tsx](__tests__/hooks/mutation/use-switch-llm-profile-and-log.test.tsx)
- [__tests__/utils/get-git-path.test.ts](__tests__/utils/get-git-path.test.ts)
- [src/api/README.md](src/api/README.md)
- [src/api/agent-server-adapter.ts](src/api/agent-server-adapter.ts)
- [src/api/conversation-metadata-store.ts](src/api/conversation-metadata-store.ts)
- [src/api/conversation-service/agent-server-conversation-service.api.ts](src/api/conversation-service/agent-server-conversation-service.api.ts)
- [src/api/conversation-service/agent-server-conversation-service.types.ts](src/api/conversation-service/agent-server-conversation-service.types.ts)
- [src/api/open-hands.types.ts](src/api/open-hands.types.ts)
- [src/hooks/mutation/use-create-conversation.ts](src/hooks/mutation/use-create-conversation.ts)
- [src/hooks/mutation/use-switch-llm-profile-and-log.ts](src/hooks/mutation/use-switch-llm-profile-and-log.ts)
- [src/hooks/query/use-unified-get-git-changes.ts](src/hooks/query/use-unified-get-git-changes.ts)
- [src/hooks/query/use-unified-git-diff.ts](src/hooks/query/use-unified-git-diff.ts)
- [src/i18n/translation.json](src/i18n/translation.json)
- [src/mocks/agent-profiles-handlers.ts](src/mocks/agent-profiles-handlers.ts)
- [src/mocks/conversation-handlers.ts](src/mocks/conversation-handlers.ts)
- [src/mocks/git-repository-handlers.ts](src/mocks/git-repository-handlers.ts)
- [src/mocks/handlers.ts](src/mocks/handlers.ts)
- [src/mocks/mcp-handlers.ts](src/mocks/mcp-handlers.ts)
- [src/mocks/workspaces-handlers.ts](src/mocks/workspaces-handlers.ts)
- [src/utils/get-git-path.ts](src/utils/get-git-path.ts)

</details>



## Purpose and Scope

The API Layer serves as the bridge between the React frontend and the backend services (Agent Server and Cloud API). It is responsible for normalizing data structures, managing authentication headers, and adapting frontend requests into the specific formats required by different backend versions and agent types (OpenHands vs. ACP) [src/api/agent-server-adapter.ts:1-60]().

This layer enforces a strict architectural constraint: **no direct `fetch` or `axios` calls to the agent-server are allowed** outside of these service adapters. All communication must flow through the typed clients provided by `@openhands/typescript-client` or the specialized adapters documented here.

This page provides a high-level overview of the service adapters. Detailed implementation details are located in the child pages:
- [Agent Server Adapter](#14.1) — Data normalization and conversation payload assembly.
- [Cloud API Proxy](#14.2) — Scoped routing and organization-aware cloud service implementations.
- [Config and Option Services](#14.3) — Feature flags, model discovery, and version compatibility.
- [Git Service API](#14.4) — Unified git operations across conversation and repository contexts.

---

## Service Architecture Overview

The API layer is organized into domain-specific services that consume the `@openhands/typescript-client`. It handles the transition from "Natural Language Space" (user queries and intents) to "Code Entity Space" (API payloads and WebSocket events).

### Diagram: Service Architecture & Data Flow

```mermaid
graph TD
    subgraph "Frontend UI Components"
        [useCreateConversation] --> [AgentServerConversationService]
        [useLlmProfiles] --> [ProfilesService]
    end

    subgraph "API Service Layer (Adapters)"
        [AgentServerConversationService] --> [AgentServerAdapter]
        [AgentServerAdapter] -- "buildStartConversationRequest" --> [ServerClient]
        [ProfilesService] --> [ProfilesClient]
        [AutomationService] --> [localAutomationAxios]
    end

    subgraph "Backend Services"
        [ServerClient] --> [AgentServer]
        [ProfilesClient] --> [AgentServer]
        [localAutomationAxios] --> [AutomationSidecar]
    end
```

**Sources**: [src/api/agent-server-adapter.ts:2-46](), [src/api/conversation-service/agent-server-conversation-service.api.ts:7-45](), [src/hooks/mutation/use-create-conversation.ts:2-17]()

### Diagram: Natural Language to Code Entity Translation

```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
        [UserQueryAndTaskIntent] --> [CreateConversationVariables]
    end

    subgraph "CodeEntitySpace"
        [CreateConversationVariables] --> [buildStartConversationRequest]
        [buildStartConversationRequest] --> [AppConversationStartRequest]
        [AppConversationStartRequest] --> [ConversationClient]
    end
```

**Sources**: [src/api/agent-server-adapter.ts:12-45](), [src/api/conversation-service/agent-server-conversation-service.types.ts:67-104](), [src/hooks/mutation/use-create-conversation.ts:34-55]()

---

## Agent Server Adapter

The `agent-server-adapter.ts` is the primary transformation layer for conversation data [src/api/agent-server-adapter.ts:1-60](). It handles the complexity of supporting two distinct agent architectures:
1.  **OpenHands Agents**: Direct `litellm` integration using `CodeActAgent` [src/api/agent-server-adapter.ts:112-130]().
2.  **ACP Agents**: Agent Client Protocol CLI subprocesses (e.g., Claude Code, Gemini CLI) [src/api/agent-server-adapter.ts:114-126]().

Key responsibilities include:
*   **Payload Assembly**: `buildStartConversationRequest` merges settings, secrets, and client tools into the wire format [src/api/agent-server-adapter.ts:12-46]().
*   **System Prompt Enrichment**: `buildRuntimeServicesSystemSuffix` injects `<RUNTIME_SERVICES>` info so the agent knows its environment URLs [src/api/agent-server-adapter.ts:176-182]().
*   **Data Normalization**: `toAppConversation` converts raw server `DirectConversationInfo` into a unified `AppConversation` format [src/api/agent-server-adapter.ts:33-37]().

For details, see [Agent Server Adapter](#14.1).

**Sources**: [src/api/agent-server-adapter.ts:1-60](), [src/api/conversation-service/agent-server-conversation-service.types.ts:150-183]()

---

## Cloud API Proxy

When Agent Canvas is running in "Cloud" mode, it interacts with a multi-tenant backend. The Cloud API Proxy manages the specific requirements of this environment, such as organization scoping and authentication.

*   **Request Scoping**: `callCloudProxy` manages requests to the cloud backend, ensuring proper headers like `X-Org-Id` are present [src/api/conversation-service/agent-server-conversation-service.api.ts:27-27]().
*   **Service Redirection**: `AgentServerConversationService` redirects calls to cloud-specific implementations (e.g., `createCloudAppConversation`) when a cloud backend is active [src/api/conversation-service/agent-server-conversation-service.api.ts:30-39]().
*   **Automation Scoping**: Automation services use pinned headers to ensure organization isolation for automated workflows [src/api/conversation-service/agent-server-conversation-service.api.ts:27-39]().

For details, see [Cloud API Proxy](#14.2).

**Sources**: [src/api/conversation-service/agent-server-conversation-service.api.ts:27-39]()

---

## Config and Option Services

These services manage the application's configuration state and the discovery of available LLM capabilities [src/api/agent-server-adapter.ts:22-29]().

*   **Environment Configuration**: Config utilities resolve the backend base URL and session API keys from environment variables [src/api/agent-server-adapter.ts:27-28]().
*   **Compatibility**: Compatibility checks verify version floors and validate bundled skill pins to prevent runtime errors between frontend and agent-server [src/api/agent-server-adapter.ts:24-26]().
*   **Runtime Services**: `fetchBackendRuntimeServicesInfo` probes endpoints to discover available backend services [src/api/agent-server-adapter.ts:15-15]().

For details, see [Config and Option Services](#14.3).

**Sources**: [src/api/agent-server-adapter.ts:22-29]()

---

## Git Service API

The Git Service bridges repository operations (listing, branching) with the agent's workspace [src/api/conversation-service/agent-server-conversation-service.api.ts:10-13]().

*   **Unified Access**: Provides a single interface for git operations whether they are performed via the Agent Server's internal git handlers or via direct repository APIs [src/api/conversation-service/agent-server-conversation-service.api.ts:9-13]().
*   **Metadata Persistence**: `useCreateConversation` persists repository and branch selection in the `conversation-metadata-store` upon successful creation [src/hooks/mutation/use-create-conversation.ts:28-32]().

For details, see [Git Service API](#14.4).

**Sources**: [src/api/conversation-service/agent-server-conversation-service.api.ts:9-13](), [src/hooks/mutation/use-create-conversation.ts:28-32]()

---

## Summary of Core Entities

| Service / Adapter | File Path | Role |
| :--- | :--- | :--- |
| `AgentServerConversationService` | `agent-server-conversation-service.api.ts` | Main entry point for conversation CRUD and file reading [src/api/conversation-service/agent-server-conversation-service.api.ts:9-13]() |
| `AgentServerAdapter` | `agent-server-adapter.ts` | Wire-format transformation, normalization, and skill injection [src/api/agent-server-adapter.ts:1-60]() |
| `CreateConversationMutation` | `use-create-conversation.ts` | Orchestrates conversation initialization and workspace metadata binding [src/hooks/mutation/use-create-conversation.ts:74-106]() |
| `LLMSubscriptionService` | `llm-subscription-service.ts` | Manages vendor-specific subscription status and LLM auth [src/api/agent-server-adapter.ts:55-60]() |

**Sources**: [src/api/agent-server-adapter.ts:1-60](), [src/api/conversation-service/agent-server-conversation-service.api.ts:9-13](), [src/hooks/mutation/use-create-conversation.ts:74-106]()

---

