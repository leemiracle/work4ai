<!-- source: DeepWiki mcp.deepwiki.com · repo kreneskyp/ix · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/FizzBuzzExample.gif](docs/FizzBuzzExample.gif)
- [docs/chat.png](docs/chat.png)
- [docs/chat_interactions.png](docs/chat_interactions.png)
- [docs/create_task.png](docs/create_task.png)
- [ix/api/artifacts/endpoints.py](ix/api/artifacts/endpoints.py)
- [ix/api/artifacts/types.py](ix/api/artifacts/types.py)
- [ix/api/tests/test_artifacts.py](ix/api/tests/test_artifacts.py)
- [ix/runnable/tests/__init__.py](ix/runnable/tests/__init__.py)
- [ix/server/fast_api.py](ix/server/fast_api.py)
- [ix/server/settings.py](ix/server/settings.py)
- [ix/server/test_settings.py](ix/server/test_settings.py)
- [ix/task_log/fixtures/dev_data.json~](ix/task_log/fixtures/dev_data.json~)
- [ix/task_log/migrations/0011_artifact_group_artifact_user.py](ix/task_log/migrations/0011_artifact_group_artifact_user.py)

</details>



## Purpose and Scope

IX is a platform for designing, deploying, and managing autonomous and semi-autonomous LLM-powered agents and workflows. This page provides a high-level overview of the IX platform architecture, core components, and system design. It covers the fundamental concepts and technical structure needed to understand how IX enables visual no-code agent creation, multi-agent orchestration, and scalable AI workflow execution.

For detailed information about specific subsystems, see [Core Architecture](#3), [API Reference](#4), and [Frontend Documentation](#5). For setup and deployment instructions, see [Getting Started](#2).

## Platform Architecture

IX is built as a modern web application with a React frontend, Django/FastAPI backend, and distributed task execution system. The platform integrates deeply with LangChain to provide a visual interface for building AI agent workflows.

### System Overview

```mermaid
graph TB
    subgraph "Frontend Layer"
        ChainEditor["Chain Graph Editor<br/>(React)"]
        ChatInterface["Chat Interface<br/>(React)"]
        UIComponents["UI Components<br/>(React)"]
    end
    
    subgraph "API Layer"
        FastAPI["FastAPI Application<br/>ix.server.fast_api"]
        Django["Django Application<br/>ix.server"]
        GraphQL["GraphQL Schema<br/>ix.schema"]
    end
    
    subgraph "Core Services"
        ChainLoader["Chain Loader<br/>ix.chains.loaders"]
        AgentProcess["Agent Process<br/>ix.agents.process"]
        TaskLog["Task Logging<br/>ix.task_log"]
        IxHandler["Callback Handler<br/>ix.runnable_log"]
    end
    
    subgraph "LangChain Integration"
        NodeTypes["Component Registry<br/>ix.chains.fixtures"]
        Runnables["LangChain Runnables"]
        Tools["Agent Tools"]
        LLMProviders["LLM Providers<br/>(OpenAI, Anthropic)"]
    end
    
    subgraph "Infrastructure"
        PostgreSQL[("PostgreSQL<br/>Database")]
        Redis[("Redis<br/>Cache & Broker")]
        Celery["Celery Workers<br/>Background Tasks"]
        Vault["HashiCorp Vault<br/>Secret Management"]
    end
    
    ChainEditor --> FastAPI
    ChatInterface --> FastAPI
    FastAPI --> Django
    Django --> GraphQL
    
    FastAPI --> ChainLoader
    FastAPI --> AgentProcess
    AgentProcess --> TaskLog
    AgentProcess --> IxHandler
    
    ChainLoader --> NodeTypes
    ChainLoader --> Runnables
    AgentProcess --> Tools
    Runnables --> LLMProviders
    
    Django --> PostgreSQL
    TaskLog --> PostgreSQL
    AgentProcess --> Redis
    AgentProcess --> Celery
    
    Celery --> Redis
    Django --> Vault
```

Sources: [ix/server/fast_api.py:1-95](), [ix/server/settings.py:1-268](), [README.md:30-87]()

## Core Concepts

### Chains
Chains are visual workflows that define the logic and flow of AI agent operations. They are built using a graph-based editor and executed through the LangChain framework.

### Agents  
Agents are autonomous entities that can execute chains, use tools, and interact with users through chat interfaces. Multiple agents can collaborate within a single conversation.

### Components
Components are LangChain-compatible building blocks (LLMs, tools, memory systems, etc.) that can be visually connected in the chain editor to create complex workflows.

### Tasks
Tasks represent individual execution instances of agent operations, providing logging, artifact management, and conversation history.

## API Structure

IX exposes its functionality through both REST and GraphQL APIs, organized into distinct routers for different domains:

```mermaid
graph LR
    subgraph "FastAPI Routers"
        ChainsAPI["chains_router<br/>/chains/"]
        AgentsAPI["agents_router<br/>/agents/"]
        ChatsAPI["chats_router<br/>/chats/"]
        ArtifactsAPI["artifacts_router<br/>/artifacts/"]
        ComponentsAPI["components_router<br/>/components/"]
        EditorAPI["editor_router<br/>/editor/"]
        SecretsAPI["secrets_router<br/>/secrets/"]
        SkillsAPI["skills_router<br/>/skills/"]
        WorkspaceAPI["workspace_router<br/>/workspace/"]
        DataAPI["data_router<br/>/data/"]
        DatasourcesAPI["datasources_router<br/>/datasources/"]
        RunnableLogAPI["runnable_log_router<br/>/runnable_log/"]
    end
    
    subgraph "GraphQL API"
        TaskManagement["Task Management"]
        Subscriptions["Real-time Subscriptions"]
        Artifacts["Artifact Queries"]
    end
    
    subgraph "Core Models"
        Chain[("Chain")]
        ChainNode[("ChainNode")]
        ChainEdge[("ChainEdge")]
        Agent[("Agent")]
        Chat[("Chat")]
        Task[("Task")]
        TaskLogMessage[("TaskLogMessage")]
        Artifact[("Artifact")]
    end
    
    ChainsAPI --> Chain
    ChainsAPI --> ChainNode
    ChainsAPI --> ChainEdge
    AgentsAPI --> Agent
    ChatsAPI --> Chat
    ArtifactsAPI --> Artifact
    
    TaskManagement --> Task
    TaskManagement --> TaskLogMessage
    Subscriptions --> Task
    Artifacts --> Artifact
```

Sources: [ix/server/fast_api.py:8-38](), [ix/api/artifacts/endpoints.py:1-122]()

## Data Models and Relationships

The IX platform uses a relational data model centered around chains, agents, tasks, and artifacts:

```mermaid
erDiagram
    Chain ||--o{ ChainNode : contains
    Chain ||--o{ ChainEdge : defines_flow
    Chain ||--o{ Agent : executed_by
    Agent ||--o{ Chat : participates_in
    Chat ||--|| Task : creates
    Task ||--o{ TaskLogMessage : logs
    Task ||--o{ Artifact : generates
    User ||--o{ Chain : owns
    User ||--o{ Agent : owns
    User ||--o{ Chat : owns
    User ||--o{ Task : owns
    User ||--o{ Artifact : owns
    
    Chain {
        uuid id
        string name
        string description
        json config
        uuid user_id
        uuid group_id
    }
    
    ChainNode {
        uuid id
        uuid chain_id
        string class_path
        json config
        json position
    }
    
    ChainEdge {
        uuid id
        uuid chain_id
        uuid source_id
        uuid target_id
        string key
    }
    
    Agent {
        uuid id
        string name
        string purpose
        uuid chain_id
        uuid user_id
    }
    
    Task {
        uuid id
        uuid agent_id
        uuid user_id
        string status
        json inputs
        json outputs
    }
    
    Artifact {
        uuid id
        uuid task_id
        string name
        string artifact_type
        json storage
        uuid user_id
    }
```

Sources: [ix/task_log/migrations/0011_artifact_group_artifact_user.py:1-33](), [ix/api/artifacts/types.py:1-40]()

## Execution Flow

When a user interacts with an agent through the chat interface, IX follows this execution pattern:

```mermaid
sequenceDiagram
    participant User
    participant ChatInterface as "Chat Interface"
    participant FastAPI as "FastAPI"
    participant Celery as "Celery Worker"
    participant ChainLoader as "Chain Loader"
    participant AgentProcess as "Agent Process"
    participant LangChain as "LangChain Runtime"
    participant Database as "PostgreSQL"
    
    User->>ChatInterface: "Send message"
    ChatInterface->>FastAPI: "POST /chats/{id}/messages"
    FastAPI->>Database: "Create Task record"
    FastAPI->>Celery: "Queue agent task"
    
    Celery->>AgentProcess: "Execute agent"
    AgentProcess->>ChainLoader: "load_chain()"
    ChainLoader->>Database: "Load chain definition"
    ChainLoader->>LangChain: "Build runnable graph"
    
    LangChain->>AgentProcess: "Execute workflow"
    AgentProcess->>Database: "Log task messages"
    AgentProcess->>Database: "Save artifacts"
    
    AgentProcess->>FastAPI: "Stream response"
    FastAPI->>ChatInterface: "WebSocket updates"
    ChatInterface->>User: "Display response"
```

Sources: [ix/server/fast_api.py:1-95](), [ix/server/settings.py:193-196]()

## Component Integration

IX provides a component configuration layer that maps LangChain components to visual node types in the chain editor:

```mermaid
graph TD
    subgraph "Component Definition"
        Fixtures["Node Type Fixtures<br/>ix.chains.fixtures"]
        Registry["Component Registry"]
        Schemas["JSON Schema Definitions"]
    end
    
    subgraph "Visual Editor"
        NodePalette["Component Palette"]
        GraphEditor["Visual Graph Editor"]
        ConfigForms["Dynamic Configuration Forms"]
    end
    
    subgraph "Runtime Execution"
        FlowPlaceholders["Flow Placeholders"]
        ChainLoader["Chain Loader"]
        LangChainRunnables["LangChain Runnables"]
    end
    
    Fixtures --> Registry
    Registry --> NodePalette
    Registry --> ConfigForms
    Schemas --> ConfigForms
    
    GraphEditor --> FlowPlaceholders
    FlowPlaceholders --> ChainLoader
    ChainLoader --> LangChainRunnables
    
    Registry --> ChainLoader
```

Sources: [README.md:82-87](), [ix/server/settings.py:288-289]()

This architecture enables IX to provide a visual, no-code interface for building sophisticated AI agent workflows while maintaining the full power and flexibility of the LangChain ecosystem.

---

