<!-- source: DeepWiki mcp.deepwiki.com · repo coze-dev/coze-studio · page 10 Glossary · fetched 2026-10-29 -->

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude/agents/frontend-infrastructure-expert.md](.claude/agents/frontend-infrastructure-expert.md)
- [.gitattributes](.gitattributes)
- [.github/CODEOWNERS](.github/CODEOWNERS)
- [README.md](README.md)
- [backend/api/model/base/base.go](backend/api/model/base/base.go)
- [backend/api/model/coze/api.go](backend/api/model/coze/api.go)

</details>



This page provides definitions for codebase-specific terms, jargon, and domain concepts used throughout Coze Studio. It serves as a technical reference for onboarding engineers to understand the implementation and data flow associated with these terms.

## Core Domain Concepts

### Agent (Intelligence)
In the Coze Studio context, an "Agent" is often referred to in the backend code as **Intelligence**. It represents the core AI entity consisting of prompts, tools, and configurations.
* **Implementation**: The backend manages agents via the `IntelligenceService`, which handles draft creation, updates, and publishing.
* **Code Pointer**: [backend/api/model/app/intelligence/intelligence.go:27-29]() defines the interface for managing these entities.
* **Sources**: [backend/api/model/coze/api.go:27-29](), [README.md:32-32]()

### Bot IDE
The frontend environment where users configure agents. It is divided into several specialized packages to manage the complex state of an AI editor.
* **Key Components**:
    * `bot-editor-context-store`: Manages the global state of the editor.
    * `bot-config-area`: Handles the configuration UI for prompts and settings.
    * `chat-debug-area`: The preview and testing pane.
* **Sources**: [.github/CODEOWNERS:66-72]()

### IDL (Interface Definition Layer)
The contract between frontend and backend. Coze Studio uses **Thrift** to define APIs, which are then compiled into Go code for the backend and TypeScript types for the frontend.
* **Implementation**: Thrift files are processed to generate Go structures and service clients. The `Base` struct provides common fields like `LogID` and `TrafficEnv`.
* **Code Pointer**: [backend/api/model/base/base.go:200-207]() shows the base metadata included in every request.
* **Sources**: [backend/api/model/coze/api.go:1-25](), [backend/api/model/base/base.go:1-13](), [.github/CODEOWNERS:26-26]()

---

## Technical Terms & Jargon

### FlowGram
The visual engine used for building AI workflows. It provides the canvas, node rendering, and state management for the "Workflow" feature.
* **Packages**: `packages/common/flowgram-adapter/` serves as the bridge between the generic FlowGram engine and Coze-specific business logic.
* **Sources**: [.github/CODEOWNERS:59-60]()

### Eino
The backend AI orchestration framework used to execute complex logic, such as agent runs and workflow node execution. It acts as the "brain" for processing AI requests.
* **Sources**: [README.md:27-27]()

### Slardar & Tea
Internal monitoring and reporting abstractions.
* **Slardar**: Used for performance monitoring and error tracking (TTI, exceptions).
* **Tea**: Used for event tracking and user behavior analytics.
* **Sources**: [.github/CODEOWNERS:12-12](), [.github/CODEOWNERS:36-39](), [.github/CODEOWNERS:53-54]()

---

## System Architecture Mapping

The following diagrams bridge the gap between natural language concepts used in the UI and the specific code entities that implement them.

### Mapping: Agent Development to Code Entities

This diagram shows how a user's action in the "Agent IDE" translates to backend service calls and data structures defined in the generated models.

```mermaid
graph TD
    subgraph "Frontend_React_Zustand"
        ["UI:Agent_IDE_UI"] -- "updates state" --> ["bot-editor-context-store"]
        ["bot-editor-context-store"] -- "calls" --> ["bot-api:arch"]
    end

    subgraph "Interface_Thrift_IDL"
        ["bot-api:arch"] -- "Thrift/HTTP" --> ["IntelligenceService:IDL"]
    end

    subgraph "Backend_Go_Hertz"
        ["IntelligenceService:IDL"] -- "implements" --> ["IntelligenceServiceClient"]
        ["IntelligenceServiceClient"] -- "logic" --> ["IntelligenceService:Interface"]
    end

    ["IntelligenceService:Interface"] -- "uses" --> ["api/model/app/intelligence"]
```
**Sources**: [backend/api/model/app/intelligence/intelligence.go:27-33](), [backend/api/model/coze/api.go:27-33](), [.github/CODEOWNERS:9-10](), [.github/CODEOWNERS:67-67]()

### Mapping: Infrastructure to Service Logic

This diagram associates the infrastructure components defined in the deployment layer with the backend adapter logic and generated models.

```mermaid
graph LR
    subgraph "Infrastructure_Layer"
        ["MySQL:RDB"]
        ["Milvus:Vector"]
        ["Redis:Cache"]
    end

    subgraph "Backend_Adapters_infra"
        ["GORM:ORM"]
        ["vector-store:adapter"]
        ["rdb:adapter"]
    end

    subgraph "Domain_Logic"
        ["KNOWLEDGE:Domain"]
        ["MEMORY:Domain"]
    end

    ["KNOWLEDGE:Domain"] -- "uses" --> ["api/model/data/knowledge"]
    ["MEMORY:Domain"] -- "uses" --> ["api/model/data/variable"]
    
    ["KNOWLEDGE:Domain"] --> ["vector-store:adapter"]
    ["vector-store:adapter"] --> ["Milvus:Vector"]
    ["MEMORY:Domain"] --> ["rdb:adapter"]
    ["rdb:adapter"] --> ["MySQL:RDB"]
    ["MEMORY:Domain"] --> ["GORM:ORM"]
    ["GORM:ORM"] --> ["MySQL:RDB"]
```
**Sources**: [README.md:27-27](), [backend/api/model/coze/api.go:14-16](), [.github/CODEOWNERS:102-102]()

---

## Glossary Table

| Term | Definition | Relevant Code Location |
| :--- | :--- | :--- |
| **Rush** | The monorepo management tool used to handle the `frontend/` workspace and dependency graph. | `rush.json` |
| **Hertz** | The high-performance Go HTTP framework used for the backend API server. | `backend/main.go` |
| **Kitex / Thriftgo** | Tools used to generate Go code from Thrift IDL files for service communication. | [backend/api/model/coze/api.go:1-3]() |
| **Knowledge** | The RAG (Retrieval-Augmented Generation) subsystem involving document parsing and vector search. | `packages/data/knowledge/` |
| **Plugin** | External tools or APIs that an Agent can call. Managed via OAuth and encrypted tokens. | `packages/agent-ide/tool/` |
| **Workspace / Space** | A logical container for a user's agents, workflows, and datasets. | `packages/foundation/space-store/` |
| **TrafficEnv** | Metadata used to route requests to specific environments or toggle feature flags. | [backend/api/model/base/base.go:10-13]() |

**Sources**: [README.md:20-27](), [backend/api/model/base/base.go:10-13](), [.github/CODEOWNERS:30-30](), [.github/CODEOWNERS:94-95](), [.gitattributes:1-6]()

---

## Development Abbreviations

* **DDD**: Domain-Driven Design. The backend follows this architecture (api, application, domain, infra).
* **RAG**: Retrieval-Augmented Generation. Implemented within the "Knowledge" feature.
* **TTI**: Time to Interactive. Tracked by `report-tti` in the frontend arch layer.
* **IDL**: Interface Definition Language. Specifically refers to the Thrift files in `idl/`.
* **FE-Infra**: Frontend Infrastructure. Handled by a specialized AI agent for build tool configuration.

**Sources**: [README.md:27-27](), [.github/CODEOWNERS:111-111](), [.claude/agents/frontend-infrastructure-expert.md:2-3]()