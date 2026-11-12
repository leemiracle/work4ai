# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/update-download-stats.yml](.github/workflows/update-download-stats.yml)
- [CHANGELOG.md](CHANGELOG.md)
- [README.md](README.md)
- [VERSION](VERSION)
- [assets/UI.png](assets/UI.png)
- [assets/arch.png](assets/arch.png)
- [assets/examples/ai-security-auditor.png](assets/examples/ai-security-auditor.png)
- [assets/examples/autonomous-engineering-team.png](assets/examples/autonomous-engineering-team.png)
- [assets/examples/deep-research-engine.png](assets/examples/deep-research-engine.png)
- [assets/examples/reactive-database-layer.png](assets/examples/reactive-database-layer.png)
- [assets/features-strip.png](assets/features-strip.png)
- [assets/github hero.png](assets/github hero.png)
- [control-plane/internal/templates/go/go.mod.tmpl](control-plane/internal/templates/go/go.mod.tmpl)
- [examples/python_agent_nodes/agentic_rag/requirements.txt](examples/python_agent_nodes/agentic_rag/requirements.txt)
- [examples/python_agent_nodes/documentation_chatbot/requirements.txt](examples/python_agent_nodes/documentation_chatbot/requirements.txt)
- [examples/python_agent_nodes/hello_world_rag/requirements.txt](examples/python_agent_nodes/hello_world_rag/requirements.txt)
- [sdk/python/CHANGELOG.md](sdk/python/CHANGELOG.md)
- [sdk/python/agentfield/__init__.py](sdk/python/agentfield/__init__.py)
- [sdk/python/pyproject.toml](sdk/python/pyproject.toml)
- [sdk/python/tests/test_execution_logger.py](sdk/python/tests/test_execution_logger.py)
- [sdk/typescript/package.json](sdk/typescript/package.json)

</details>



This document provides a high-level introduction to **AgentField**, an open-source control plane for autonomous AI agents, often described as "Kubernetes for AI Agents." AgentField treats AI agents as first-class backend services, providing infrastructure for routing, orchestration, state management, and cryptographic identity.

**Scope:** This page introduces the core architecture, key concepts, and fundamental components. For detailed implementation guides, see the SDK documentation ([Python SDK](#3), [TypeScript SDK](#4), [Go SDK](#5)). For deployment and production considerations, see [Deployment](#13).

---

## What is AgentField?

AgentField is backend infrastructure for autonomous AI systems. It provides a **control plane** (stateless Go service) that orchestrates **agent nodes** (Python/TypeScript/Go processes) across distributed environments. Unlike agent frameworks that bundle everything into monolithic scripts, AgentField treats agents as microservices with standard REST APIs.

**Key characteristics:**
- **Agent-as-Service model**: Each agent exposes HTTP endpoints for its capabilities.
- **Multi-language native**: Python, TypeScript, and Go SDKs with identical semantics.
- **Harness Orchestration**: Native support for delegating tasks to autonomous coding agents like Claude Code, Codex, and OpenCode [[README.md:21-25](), [sdk/python/pyproject.toml:53-72]()].
- **Built-in state**: Hierarchical memory with vector search, no external databases required.
- **Cryptographic identity**: W3C DIDs and Verifiable Credentials for trust and audit trails [[sdk/python/agentfield/did_auth.py:1-52]()].
- **Desktop Dashboard**: A Docker-Desktop-style companion app for managing nodes and local health [[CHANGELOG.md:14-34]()].

**Version**: 0.1.109-rc.6 [[VERSION:1]()]

Sources: [README.md:1-60](), [VERSION:1](), [CHANGELOG.md:9-14]()

---

## High-Level Architecture

```mermaid
graph TB
    subgraph "Developer & User Interface"
        Dev["Developer"]
        CLI["af CLI<br/>(Go binary)"]
        Desktop["AgentField Desktop<br/>(Electron App)"]
    end
    
    subgraph "Control Plane Layer (Go)"
        CP["Control Plane Server<br/>cmd/agentfield-server"]
        Router["AgentRouter<br/>internal/router"]
        Discovery["Discovery Service<br/>/api/v1/nodes"]
        Execution["Execution Engine<br/>/api/v1/execute"]
    end
    
    subgraph "Agent Node Layer (SDKs)"
        AgentPy["Python Agent<br/>agentfield.Agent"]
        AgentTs["TypeScript Agent<br/>@agentfield/sdk.Agent"]
        AgentGo["Go Agent<br/>agentfieldagent.New()"]
    end
    
    subgraph "Storage Subsystem"
        Storage["StorageProvider Interface"]
        SQLite["LocalStorage<br/>SQLite + BoltDB"]
        Postgres["PostgresStorage<br/>PostgreSQL + pgvector"]
    end
    
    subgraph "Intelligence & Coding"
        AI["AI Providers<br/>litellm / ai-sdk"]
        Harness["HarnessRunner<br/>ClaudeCode / Codex"]
    end
    
    Dev -->|"af server"| CLI
    Desktop -->|"IPC / af secrets"| CLI
    CLI --> CP
    
    CP --> Router
    CP --> Discovery
    CP --> Execution
    
    AgentPy -->|"POST /api/v1/nodes/register"| CP
    AgentTs -->|"POST /api/v1/nodes/register"| CP
    AgentGo -->|"POST /api/v1/nodes/register"| CP
    
    Execution -->|"POST /execute"| AgentPy
    Execution -->|"POST /execute"| AgentTs
    
    CP --> Storage
    Storage -->|"mode: local"| SQLite
    Storage -->|"mode: postgres"| Postgres
    
    AgentPy --> AI
    AgentPy --> Harness
    AgentTs --> AI
```

**Core components:**

| Component | Implementation | Source Pointer | Purpose |
|-----------|---------------|----------------|---------|
| **Control Plane** | Go service | `cmd/agentfield-server` | Stateless orchestration hub |
| **CLI** | `af` binary | `cmd/af` | Project scaffolding and secret management |
| **Desktop App** | Electron/React | `desktop/` | GUI for health and agent monitoring |
| **Python SDK** | `agentfield` | [sdk/python/agentfield/agent.py:1]() | Agent runtime and Pydantic integration |
| **TypeScript SDK** | `@agentfield/sdk` | [sdk/typescript/package.json:1]() | Agent runtime with AI SDK support |
| **Harness** | `HarnessRunner` | [sdk/python/agentfield/harness.py:1]() | Abstraction for autonomous coding agents |

Sources: [README.md:26-60](), [sdk/python/pyproject.toml:1-40](), [sdk/typescript/package.json:1-49](), [CHANGELOG.md:14-34]()

---

## Core Concepts

### Agents, Reasoners, and Skills

AgentField distinguishes between non-deterministic AI logic and deterministic tools:

```mermaid
graph LR
    Agent["Agent<br/>node_id: 'claims-processor'"]
    Reasoner["Reasoner<br/>@app.reasoner()"]
    Skill["Skill<br/>@app.skill()"]
    Harness["Harness<br/>HarnessConfig"]
    AI["AI Model<br/>app.ai()"]
    
    Agent --> Reasoner
    Agent --> Skill
    Reasoner --> AI
    Reasoner --> Skill
    Reasoner --> Harness
```

**Definitions:**

- **Agent**: A logical microservice grouping, identified by `node_id`. Defined via the `Agent` class [[sdk/python/agentfield/agent.py:1]()].
- **Reasoner**: AI-powered logic that uses LLMs to make decisions. Defined via `@app.reasoner()` [[sdk/python/agentfield/decorators.py:81]()].
- **Skills**: Deterministic functions for tools (API calls, DB writes). Defined via `@app.skill()` [[sdk/python/agentfield/agent.py:1]()].
- **Harness**: A specialized execution environment for high-autonomy coding agents like Claude Code [[sdk/python/agentfield/harness.py:1]()].

**Example in Python:**

```python
from agentfield import Agent, AIConfig

app = Agent(node_id="researcher", ai_config=AIConfig(model="anthropic/claude-3-5-sonnet"))

@app.skill()
def fetch_data(query: str):
    return {"data": "..."}

@app.reasoner()
async def research(topic: str):
    context = fetch_data(topic)
    return await app.ai(user=f"Analyze: {topic}", context=context)

app.run()
```

Sources: [README.md:58-99](), [sdk/python/agentfield/__init__.py:1-90]()

---

## System Architecture

AgentField follows a Hub-and-Spoke model where the Control Plane acts as the central router.

### Agent Lifecycle & Communication
1. **Registration**: Agents register their `ReasonerDefinition` and `SkillDefinition` with the control plane [[sdk/python/agentfield/types.py:11-12]()].
2. **Execution**: The control plane receives a request at `/api/v1/execute/{node}.{capability}` and proxies it to the agent node's callback URL.
3. **Identity**: Agents can use `DIDAuthenticator` to sign requests, ensuring only authorized callers can invoke capabilities [[sdk/python/agentfield/did_auth.py:45-52]()].

For details, see [System Architecture](#1.2).

### Storage & Memory
AgentField provides a `MemoryInterface` that abstracts away the storage layer [[sdk/python/agentfield/memory.py:1]()].
- **Local Mode**: Uses SQLite for workflows and BoltDB for key-value state.
- **Postgres Mode**: Uses PostgreSQL with `pgvector` for scalable RAG and unified storage.
- **Memory Scopes**: State is automatically partitioned into `workflow`, `session`, `actor`, and `global` scopes [[sdk/python/agentfield/types.py:10]()].

For details, see [Memory System](#7).

---

## Multi-Agent Coordination

Coordination is handled via `app.call()`, which routes requests through the control plane rather than direct peer-to-peer calls. This enables:
- **Distributed Fan-out**: One reasoner can call thousands of other agents in parallel using `asyncio.gather` [[README.md:85-93]()].
- **Workflow Tracing**: The control plane assigns `X-Workflow-ID` and `X-Execution-ID` headers to every call, allowing for full DAG visualization in the Dashboard UI.
- **Discovery**: Agents can use the `discover()` method to find other agents by tags or capabilities [[sdk/python/agentfield/client.py:1]()].

For details, see [Multi-Agent Coordination](#9).

---

## Getting Started

To begin building with AgentField:
1. **Install the CLI**: `curl -fsSL https://agentfield.ai/install.sh | bash` [[README.md:42]()].
2. **Initialize a Project**: `af init my-agent` [[README.md:48-52]()].
3. **Start the Server**: `af server` to launch the control plane and dashboard [[CHANGELOG.md:108-114]()].

For a full tutorial, see [Getting Started](#2).

Sources: [README.md:1-102](), [CHANGELOG.md:9-100]()

---

# Page: Core Concepts

# Core Concepts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/update-download-stats.yml](.github/workflows/update-download-stats.yml)
- [CHANGELOG.md](CHANGELOG.md)
- [README.md](README.md)
- [VERSION](VERSION)
- [assets/UI.png](assets/UI.png)
- [assets/arch.png](assets/arch.png)
- [assets/examples/ai-security-auditor.png](assets/examples/ai-security-auditor.png)
- [assets/examples/autonomous-engineering-team.png](assets/examples/autonomous-engineering-team.png)
- [assets/examples/deep-research-engine.png](assets/examples/deep-research-engine.png)
- [assets/examples/reactive-database-layer.png](assets/examples/reactive-database-layer.png)
- [assets/features-strip.png](assets/features-strip.png)
- [assets/github hero.png](assets/github hero.png)
- [control-plane/internal/templates/go/go.mod.tmpl](control-plane/internal/templates/go/go.mod.tmpl)
- [examples/python_agent_nodes/agentic_rag/requirements.txt](examples/python_agent_nodes/agentic_rag/requirements.txt)
- [examples/python_agent_nodes/documentation_chatbot/requirements.txt](examples/python_agent_nodes/documentation_chatbot/requirements.txt)
- [examples/python_agent_nodes/hello_world_rag/requirements.txt](examples/python_agent_nodes/hello_world_rag/requirements.txt)
- [sdk/python/CHANGELOG.md](sdk/python/CHANGELOG.md)
- [sdk/python/agentfield/__init__.py](sdk/python/agentfield/__init__.py)
- [sdk/python/pyproject.toml](sdk/python/pyproject.toml)
- [sdk/python/tests/test_execution_logger.py](sdk/python/tests/test_execution_logger.py)
- [sdk/typescript/package.json](sdk/typescript/package.json)

</details>



This page defines the fundamental building blocks of the AgentField system. Understanding these concepts is essential before deploying agents or integrating with the control plane.

**Scope:** This document covers the core terminology and architectural patterns used throughout AgentField. For detailed system architecture diagrams, see **1.2 System Architecture**. For specific SDK implementation details, see the Python SDK (**3.0**), TypeScript SDK (**4.0**), or Go SDK (**5.0**) sections.

---

## Control Plane

The **Control Plane** is the central orchestration hub for all agents in an AgentField deployment. It is a stateless service that acts as the "Kubernetes for AI Agents"—it does not execute agent logic itself but routes requests, tracks executions, manages registration, and provides observability.

**Key responsibilities:**
- **Agent Registration and Discovery:** Maintaining a registry of active nodes and their capabilities.
- **Request Routing:** Proxying execution calls to the correct agent node via HTTP.
- **Workflow Tracking:** Generating DAGs and tracking parent-child relationships between agent calls.
- **Memory Management:** Providing a centralized storage layer for cross-agent state.
- **Identity & Trust:** Issuing DIDs and verifying execution chains via Verifiable Credentials.

**Sources:** [README.md:27-52](), [CHANGELOG.md:18-29]()

---

## Agent Nodes

An **Agent Node** is an independent service (typically a container or serverless function) that hosts one or more capabilities. Each node is defined by an `Agent` class instance in the SDK.

**Lifecycle of an Agent Node:**
1. **Initialization:** The agent is instantiated with a unique `node_id` and version [sdk/python/agentfield/agent.py:107-120]().
2. **Registration:** On startup, the agent sends its manifest (reasoners, skills, and callback URL) to the Control Plane [sdk/python/agentfield/agent_field_handler.py:41-100]().
3. **Heartbeat:** The node maintains a background thread to send periodic liveness signals [sdk/python/agentfield/agent_field_handler.py:170-190]().
4. **Execution:** The node listens for incoming HTTP POST requests at `/execute` and routes them to the local function [sdk/python/agentfield/agent.py:311-355]().

```mermaid
graph TB
    subgraph "Code Entity Space (Python SDK)"
        AgentClass["Agent (agentfield/agent.py)"]
        Handler["AgentFieldHandler (agentfield/agent_field_handler.py)"]
        Client["AgentFieldClient (agentfield/client.py)"]
    end

    subgraph "Natural Language Space"
        Node["Agent Node"]
        CP["Control Plane"]
    end

    AgentClass -->|uses| Handler
    Handler -->|calls| Client
    Client -->|POST /api/v1/nodes/register| CP
    Node -- "Heartbeat" --> CP
    CP -- "Route Request" --> Node
```
**Sources:** [sdk/python/agentfield/agent.py:107-120](), [sdk/python/agentfield/agent_field_handler.py:41-100]()

---

## Reasoners vs. Skills

AgentField enforces a clean separation between non-deterministic AI logic and deterministic code.

### Reasoners
**Reasoners** are functions powered by LLMs. They handle high-level planning, synthesis, and decision-making.
- **Decorator:** `@app.reasoner()` [sdk/python/agentfield/decorators.py:81-81]()
- **Capability:** Access to `app.ai()` for LLM generation and structured output [README.md:72-93]().
- **Traceability:** Automatically logged as reasoning steps in the Control Plane dashboard.

### Skills
**Skills** are deterministic tools. They perform specific, repeatable actions like database queries, API calls, or file manipulations.
- **Decorator:** `@app.skill()` [sdk/python/agentfield/__init__.py:100-100]()
- **Constraint:** Should not contain LLM logic; used for execution of "decisions" made by reasoners.

**Sources:** [sdk/python/agentfield/types.py:11-12](), [README.md:58-99]()

---

## Memory Scopes

Memory in AgentField is hierarchical and scoped to the execution context. This allows agents to share state without manual key management.

| Scope | Implementation | Lifetime |
| :--- | :--- | :--- |
| **Workflow** | `workflow_id` | Persists for a single execution chain (DAG) |
| **Session** | `session_id` | Persists across multiple turns of a conversation |
| **Actor** | `actor_id` | Persists for a specific user or external entity |
| **Global** | `global` | Shared across all agents and all users |

**Data Flow:** When an agent calls `app.memory.get("key")`, the system performs a hierarchical lookup: **Workflow → Session → Actor → Global** [sdk/python/agentfield/agent.py:809-850]().

**Sources:** [sdk/python/agentfield/agent.py:809-904](), [sdk/python/agentfield/__init__.py:73-73]()

---

## Identity & Trust (DIDs & VCs)

AgentField uses cryptographic identities to ensure that every action in a multi-agent system is verifiable.

### Decentralized Identifiers (DIDs)
Every Agent Node and the Control Plane itself has a **DID** (e.g., `did:agentfield:node:researcher`). These are used to sign requests and verify the identity of the caller [sdk/python/agentfield/did_auth.py:45-52]().

### Verifiable Credentials (VCs)
When an agent completes a task, it can generate a **Verifiable Credential (VC)**. This is a signed statement containing the input hash, output hash, and the DIDs involved [sdk/python/agentfield/__init__.py:134-147]().
- **Purpose:** Audit trails and non-repudiation.
- **Verification:** The Control Plane verifies these signatures to ensure the execution chain hasn't been tampered with.

```mermaid
graph LR
    subgraph "Identity Space"
        DID["DID (did_auth.py)"]
        Crypto["Crypto (crypto.py)"]
        VC["VC (Verifiable Credential)"]
    end

    subgraph "Execution Space"
        Call["app.call()"]
        Sign["sign_request()"]
        Verify["DIDAuthenticator"]
    end

    Call -->|uses| Sign
    Sign -->|invokes| Crypto
    Crypto -->|produces| DID
    Verify -->|validates| VC
```
**Sources:** [sdk/python/agentfield/did_auth.py:45-52](), [sdk/python/agentfield/crypto.py:53-61]()

---

## Execution Context

The `ExecutionContext` is a transient object that carries metadata through the call stack. It is populated from incoming HTTP headers like `X-Workflow-ID`, `X-Session-ID`, and `X-Caller-DID` [sdk/python/agentfield/agent.py:683-708]().

**Key Functions:**
- `get_current_context()`: Retrieves the context for the current async task [sdk/python/agentfield/agent.py:683-708]().
- **Propagation:** When an agent calls `app.call()`, the SDK automatically attaches the current context headers to the outgoing request so the next agent in the chain remains part of the same workflow.

**Sources:** [sdk/python/agentfield/agent.py:683-708](), [sdk/python/agentfield/session_transport.py:74-80]()

---

# Page: System Architecture

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/update-download-stats.yml](.github/workflows/update-download-stats.yml)
- [README.md](README.md)
- [assets/UI.png](assets/UI.png)
- [assets/arch.png](assets/arch.png)
- [assets/examples/ai-security-auditor.png](assets/examples/ai-security-auditor.png)
- [assets/examples/autonomous-engineering-team.png](assets/examples/autonomous-engineering-team.png)
- [assets/examples/deep-research-engine.png](assets/examples/deep-research-engine.png)
- [assets/examples/reactive-database-layer.png](assets/examples/reactive-database-layer.png)
- [assets/features-strip.png](assets/features-strip.png)
- [assets/github hero.png](assets/github hero.png)
- [control-plane/cmd/af/main.go](control-plane/cmd/af/main.go)
- [control-plane/cmd/agentfield-server/main.go](control-plane/cmd/agentfield-server/main.go)
- [control-plane/config/agentfield.yaml](control-plane/config/agentfield.yaml)
- [control-plane/internal/config/config.go](control-plane/internal/config/config.go)
- [control-plane/internal/config/config_additional_test.go](control-plane/internal/config/config_additional_test.go)
- [control-plane/internal/server/middleware/auth.go](control-plane/internal/server/middleware/auth.go)
- [control-plane/internal/server/middleware/auth_admin_additional_test.go](control-plane/internal/server/middleware/auth_admin_additional_test.go)
- [control-plane/internal/server/middleware/auth_test.go](control-plane/internal/server/middleware/auth_test.go)
- [control-plane/internal/server/routes_admin.go](control-plane/internal/server/routes_admin.go)
- [control-plane/internal/server/routes_middleware.go](control-plane/internal/server/routes_middleware.go)
- [control-plane/internal/server/server.go](control-plane/internal/server/server.go)
- [control-plane/internal/server/server_additional_test.go](control-plane/internal/server/server_additional_test.go)
- [control-plane/internal/server/server_coverage_additional_test.go](control-plane/internal/server/server_coverage_additional_test.go)
- [deployments/helm/agentfield/templates/control-plane-deployment.yaml](deployments/helm/agentfield/templates/control-plane-deployment.yaml)
- [docs/ENVIRONMENT_VARIABLES.md](docs/ENVIRONMENT_VARIABLES.md)
- [tests/functional/docker/agentfield-test.yaml](tests/functional/docker/agentfield-test.yaml)

</details>



## Purpose and Scope

This document describes the technical architecture of AgentField's core infrastructure components: the Control Plane orchestration service, Agent Node runtime model, storage subsystems, and communication protocols. It explains how these components interact to provide a distributed, production-ready execution environment for AI agents.

AgentField follows a "Control Plane + Agent Node" model where the control plane handles orchestration, memory, and identity, while agent nodes (implemented via SDKs) handle reasoning and skill execution.

---

## High-Level Architecture

AgentField uses a **Control Plane + Agent Node** architecture where a central orchestration service coordinates multiple independent agent processes. This mirrors Kubernetes' control plane pattern but is optimized for AI agent workloads.

### System Components Diagram

```mermaid
graph TB
    subgraph "Developer Interface"
        CLI["af CLI<br/>(Go binary)"]
        DevSDK["SDK Code<br/>(Python/TypeScript/Go)"]
    end
    
    subgraph "Control Plane Service"
        AFServer["AgentFieldServer<br/>(Go/Gin)"]
        Router["gin.Engine<br/>(HTTP Router)"]
        AgentSvc["AgentService<br/>(Node Management)"]
        StatusMgr["StatusManager<br/>(Health & Presence)"]
        ExecHandler["ExecuteHandler<br/>(Reasoner Execution)"]
        DIDService["DIDService<br/>(Identity Management)"]
        VCService["VCService<br/>(Verifiable Credentials)"]
    end
    
    subgraph "Storage Layer"
        StorageProvider["StorageProvider Interface"]
        LocalStorage["LocalStorage<br/>(SQLite + BoltDB)"]
        PostgresStorage["PostgresStorage<br/>(PostgreSQL)"]
    end
    
    subgraph "Agent Node Process"
        AgentClass["Agent Class<br/>(SDK)"]
        Reasoners["@app.reasoner()"]
        Skills["@app.skill()"]
    end
    
    CLI --> Router
    DevSDK --> AgentClass
    
    AFServer --> Router
    Router --> AgentSvc
    Router --> StatusMgr
    Router --> ExecHandler
    Router --> DIDService
    Router --> VCService
    
    AgentSvc --> StorageProvider
    ExecHandler --> StorageProvider
    DIDService --> StorageProvider
    
    StorageProvider --> LocalStorage
    StorageProvider --> PostgresStorage
    
    AgentClass -.HTTP POST.-> Router
    ExecHandler -.HTTP POST.-> AgentClass
```

**Sources:** [control-plane/internal/server/server.go:47-104](), [control-plane/internal/server/server.go:107-175](), [README.md:27-52]()

---

## Control Plane Architecture

The Control Plane is a Go service built with the Gin framework. It acts as the central orchestrator for agent discovery, execution routing, and state management.

### Control Plane Components

| Component | Implementation | Purpose |
|-----------|---------------|---------|
| **HTTP Router** | `gin.Engine` | Routes API requests to handlers [control-plane/internal/server/server.go:139]() |
| **Agent Service** | `coreservices.AgentService` | Manages agent node lifecycle and registration [control-plane/internal/server/server.go:155]() |
| **Status Manager** | `services.StatusManager` | Tracks agent heartbeats and health transitions [control-plane/internal/server/server.go:169]() |
| **DID Service** | `services.DIDService` | Manages Decentralized Identifiers for agents [control-plane/internal/server/server.go:64]() |
| **VC Service** | `services.VCService` | Generates Verifiable Credentials for execution audits [control-plane/internal/server/server.go:65]() |
| **Agent Client** | `communication.HTTPAgentClient` | Communicates with remote agent nodes [control-plane/internal/server/server.go:145]() |
| **Storage Provider** | `storage.StorageProvider` | Interface for persistence (SQLite or Postgres) [control-plane/internal/server/server.go:49]() |

### Global Middleware Stack

The Control Plane applies a global middleware stack to all routes via `applyGlobalMiddleware()`:
1.  **CORS**: Configurable via `API.CORS` settings [control-plane/internal/server/routes_middleware.go:19-38]().
2.  **Request Logging**: Standard Gin logger [control-plane/internal/server/routes_middleware.go:40-52]().
3.  **Timeout**: 1-hour timeout for long-running agent executions [control-plane/internal/server/routes_middleware.go:54-62]().
4.  **API Key Auth**: Enforced via `middleware.APIKeyAuth` [control-plane/internal/server/routes_middleware.go:79-84]().
5.  **DID Auth**: Optional cryptographic identity verification [control-plane/internal/server/routes_middleware.go:89-102]().

**Sources:** [control-plane/internal/server/routes_middleware.go:18-110](), [control-plane/internal/server/middleware/auth.go:19-146]()

---

## Storage Layer

AgentField supports a dual-backend storage model defined in the `StorageConfig` [control-plane/internal/config/config.go:20]().

### Local Mode (Development)
- **Database**: SQLite for relational data (agents, executions, DIDs) [control-plane/config/agentfield.yaml:71]().
- **KV Store**: BoltDB for memory and state [control-plane/config/agentfield.yaml:72]().
- **Vector**: Local vector storage (enabled by default) [control-plane/config/agentfield.yaml:81]().

### Postgres Mode (Production)
- **Engine**: PostgreSQL with support for SSL and connection pooling [control-plane/config/agentfield.yaml:73-79]().
- **DSN**: Configurable via `AGENTFIELD_POSTGRES_URL` [control-plane/cmd/agentfield-server/main.go:111-124]().

**Sources:** [control-plane/config/agentfield.yaml:68-83](), [control-plane/cmd/agentfield-server/main.go:97-154]()

---

## Identity and Trust Model

AgentField bridges the gap between natural language agent definitions and cryptographic security using DIDs and VCs.

### Identity Flow Diagram

```mermaid
sequenceDiagram
    participant AgentNode as "Agent Node (SDK)"
    participant CP as "Control Plane (Go)"
    participant DID as "DIDService"
    participant VC as "VCService"
    participant DB as "StorageProvider"

    AgentNode->>CP: POST /api/v1/nodes/register
    CP->>DID: Resolve/Create Agent DID
    DID->>DB: StoreDID()
    CP-->>AgentNode: Registration Success (DID assigned)

    Note over AgentNode, CP: Execution Phase
    
    AgentNode->>CP: Request Cross-Agent Call
    CP->>VC: GenerateExecutionVC()
    VC->>DB: StoreExecutionVC()
    CP->>AgentNode: Forward Execution + VC
```

### Security Enforcement
- **API Key**: Required for all REST operations unless explicitly skipped [control-plane/internal/server/middleware/auth.go:121-135]().
- **Admin Token**: Required for sensitive operations via `X-Admin-Token` [control-plane/internal/server/middleware/auth.go:166-185]().
- **VC Requirements**: Can be configured to require VCs for registration, execution, and cross-agent calls [control-plane/config/agentfield.yaml:91-94]().

**Sources:** [control-plane/internal/server/middleware/auth.go:19-185](), [control-plane/config/agentfield.yaml:85-112]()

---

## Execution and Communication Patterns

### Request Context Propagation
The Control Plane propagates execution context using custom HTTP headers. Downstream SDKs and handlers use these to maintain workflow state:
- `X-Caller-Agent-ID`: Identifies the calling agent [control-plane/internal/server/middleware/auth.go:139]().
- `X-Agent-Node-ID`: Identifies the target node [control-plane/internal/server/middleware/auth.go:141]().

### Agent Heartbeats
Agent nodes must send periodic heartbeats. The `StatusManager` reconciles these heartbeats to determine node health [control-plane/internal/server/server.go:158-164](). If heartbeats exceed the `HeartbeatStaleThreshold`, the node is marked as unhealthy.

### Streaming and Events
AgentField supports real-time events via WebSockets and SSE for:
- Memory updates (`/api/v1/memory/events/ws`) [control-plane/internal/server/routes_middleware.go:132]().
- Execution logs (`/api/ui/v1/executions/:execution_id/logs/stream`) [control-plane/internal/server/routes_middleware.go:128]().
- Workflow events [control-plane/internal/server/routes_middleware.go:127]().

**Sources:** [control-plane/internal/server/server.go:157-175](), [control-plane/internal/server/routes_middleware.go:124-136](), [control-plane/internal/server/middleware/auth.go:139-143]()

---

# Page: Getting Started

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/release.yml](.github/workflows/release.yml)
- [.goreleaser.yml](.goreleaser.yml)
- [control-plane/internal/cli/agent_commands.go](control-plane/internal/cli/agent_commands.go)
- [control-plane/internal/cli/root.go](control-plane/internal/cli/root.go)
- [control-plane/internal/cli/root_test.go](control-plane/internal/cli/root_test.go)
- [control-plane/internal/core/services/dev_service.go](control-plane/internal/core/services/dev_service.go)
- [control-plane/internal/core/services/server_url.go](control-plane/internal/core/services/server_url.go)
- [control-plane/internal/packages/server_url.go](control-plane/internal/packages/server_url.go)
- [control-plane/internal/templates/docker/docker-compose.yml.tmpl](control-plane/internal/templates/docker/docker-compose.yml.tmpl)
- [deployments/helm/agentfield/values.yaml](deployments/helm/agentfield/values.yaml)
- [deployments/kubernetes/base/control-plane-deployment.yaml](deployments/kubernetes/base/control-plane-deployment.yaml)
- [docs/RELEASE.md](docs/RELEASE.md)
- [examples/python_agent_nodes/rag_evaluation/docker-compose.yml](examples/python_agent_nodes/rag_evaluation/docker-compose.yml)
- [examples/triggers-demo/docker-compose.yml](examples/triggers-demo/docker-compose.yml)
- [scripts/bump_version.py](scripts/bump_version.py)
- [scripts/install.ps1](scripts/install.ps1)
- [scripts/install.sh](scripts/install.sh)
- [scripts/tests/__init__.py](scripts/tests/__init__.py)
- [scripts/tests/test_bump_version.py](scripts/tests/test_bump_version.py)
- [sdk/go/ai/openrouter_attribution.go](sdk/go/ai/openrouter_attribution.go)

</details>



This page provides a quick start guide for installing AgentField and running your first agent. It covers the essential steps to go from zero to a working multi-agent system in minutes.

**Scope:** This is a practical guide focused on getting AgentField running locally. For detailed installation options, see [Installation](#2.1). For a complete tutorial on building agents, see [Your First Agent](#2.2). For control plane configuration, see [Running the Control Plane](#2.3).

---

## Prerequisites

Before starting, ensure you have:

- **Operating System:** macOS (Intel or Apple Silicon), Linux (x86_64 or ARM64), or Windows [control-plane/internal/cli/root.go:74-74]()
- **For Python agents:** Python 3.9 or later [.github/workflows/release.yml:60-60]()
- **For TypeScript agents:** Node.js 20 or later [.github/workflows/release.yml:61-61]()
- **For Go agents:** Go 1.25 or later [.github/workflows/release.yml:59-59]()
- **Network:** Internet connection for downloading binaries and dependencies

---

## Architecture Overview

AgentField uses a **control plane + agent node** architecture. This is fundamentally different from monolithic agent frameworks:

### Control Plane + Agent Node Model

```mermaid
graph TB
    Dev["Developer"]
    CLI["af CLI<br/>(Binary)"]
    
    subgraph "Terminal 1"
        CP["Control Plane<br/>Port 8080<br/>af server"]
        WebUI["Dashboard UI<br/>http://localhost:8080"]
        Storage["Storage<br/>(SQLite or PostgreSQL)"]
    end
    
    subgraph "Terminal 2"
        Agent["Agent Node<br/>Port 8001<br/>python main.py"]
        Reasoners["Reasoners<br/>@app.reasoner()"]
        Skills["Skills<br/>@app.skill()"]
    end
    
    subgraph "Terminal 3 (Optional)"
        Agent2["Another Agent<br/>Port 8002<br/>npm run dev"]
    end
    
    Dev -->|"af init my-agent"| CLI
    Dev -->|"af server"| CP
    CP --> WebUI
    CP --> Storage
    
    Agent -->|"HTTP + X-API-Key"| CP
    Agent --> Reasoners
    Agent --> Skills
    
    Agent2 -->|"HTTP + X-API-Key"| CP
    
    Dev -->|"curl POST /api/v1/execute"| CP
    CP -->|"Route request"| Agent
    CP -->|"Route request"| Agent2
```

**Key Points:**
- **Control Plane:** Stateless Go service that routes requests, tracks workflows, and provides observability [control-plane/internal/cli/root.go:39-42]()
- **Agent Nodes:** Independent processes (Python/TypeScript/Go) that register capabilities and handle execution [control-plane/internal/cli/agent_commands.go:41-41]()
- **Discovery:** Agents auto-register with control plane via `POST /api/v1/nodes/register` [control-plane/internal/cli/agent_commands.go:129-129]()

**Sources:** [control-plane/internal/cli/root.go:34-152](), [control-plane/internal/cli/agent_commands.go:37-78]()

---

## Quick Start (5 Minutes)

### Step 1: Install the CLI

```bash
# macOS and Linux
curl -fsSL https://agentfield.ai/install.sh | bash

# Windows (PowerShell)
iwr -useb https://agentfield.ai/install.ps1 | iex
```

This installs the `af` CLI tool to `~/.agentfield/bin` [scripts/install.sh:142-142]().

**Verification:**
```bash
af --version
```

**Sources:** [scripts/install.sh:1-134](), [scripts/install.ps1:1-64](), [control-plane/internal/cli/root.go:67-78]()

### Step 2: Initialize an Agent

```bash
af init my-agent --defaults
cd my-agent
```

The `init` command creates a project structure for your agent [control-plane/internal/cli/root.go:97-97]().

### Step 3: Start the Control Plane (Terminal 1)

```bash
af server
```

**Expected output:**
```
📊 Dashboard: http://localhost:8080
```

The control plane listens on port 8080 by default [control-plane/internal/cli/root.go:86-86](), [control-plane/internal/packages/server_url.go:13-13]().

### Step 4: Start Your Agent (Terminal 2)

```bash
# Python
python main.py
```

The agent will attempt to register with the control plane at `http://localhost:8080` [control-plane/internal/packages/server_url.go:6-14]().

---

## Quick Start Workflow

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant CLI as af CLI
    participant CP as Control Plane<br/>(Terminal 1)
    participant Agent as Agent Node<br/>(Terminal 2)
    
    Dev->>CLI: af --version
    CLI-->>Dev: v0.1.21
    
    Dev->>CLI: af init my-agent
    CLI-->>Dev: Creates project structure
    
    Note over CP: Terminal 1
    Dev->>CP: af server
    CP->>CP: Start HTTP server on :8080
    
    Note over Agent: Terminal 2
    Dev->>Agent: python main.py
    Agent->>CP: POST /api/v1/nodes/register
    CP-->>Agent: 200 OK
    Agent-->>Dev: Agent registered
```

**Sources:** [control-plane/internal/cli/root.go:143-149](), [control-plane/internal/cli/agent_commands.go:80-88]()

---

## Installation Options Summary

| Method | Description | Use Case |
|--------|-------------|----------|
| **Install Script** | One-line installer | Local development (recommended) [scripts/install.sh:4-6]() |
| **Staging** | Latest prerelease | Testing new features [docs/RELEASE.md:97-114]() |
| **Manual** | Raw binaries | Custom environments [docs/RELEASE.md:194-204]() |

For details, see [Installation](#2.1).

**Sources:** [docs/RELEASE.md:9-12](), [scripts/install.sh:15-43]()

---

## Common Commands Reference

| Command | Description |
|---------|-------------|
| `af --version` | Show CLI version [control-plane/internal/cli/root.go:63-63]() |
| `af init <name>` | Create new agent project [control-plane/internal/cli/root.go:97-97]() |
| `af server` | Start control plane [control-plane/internal/cli/root.go:143-143]() |
| `af server --port 9090` | Start on custom port [control-plane/internal/cli/root.go:86-86]() |
| `af server --backend-only` | Start without UI [control-plane/internal/cli/root.go:85-85]() |
| `af agent help` | Machine-friendly JSON reference [control-plane/internal/cli/root.go:42-42]() |

**Sources:** [control-plane/internal/cli/root.go:34-152]()

---

## Version Management

AgentField uses a two-tier release system:

| Environment | Version Format | Trigger |
|-------------|----------------|---------|
| **Staging** | `X.Y.Z-rc.N` | Push to main [docs/RELEASE.md:11-11]() |
| **Production** | `X.Y.Z` | Manual Dispatch [docs/RELEASE.md:12-12]() |

**Sources:** [docs/RELEASE.md:1-37](), [scripts/bump_version.py:89-118]()

---

## Next Steps

1. **[Installation](#2.1)** — Learn about advanced installation options and environment configuration.
2. **[Your First Agent](#2.2)** — Step-by-step tutorial creating a simple agent with one reasoner and one skill.
3. **[Running the Control Plane](#2.3)** — Understanding server configuration, storage modes, and the dashboard.

**Sources:** [control-plane/internal/cli/root.go:110-140]()

---

# Page: Installation

# Installation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/release.yml](.github/workflows/release.yml)
- [.goreleaser.yml](.goreleaser.yml)
- [control-plane/internal/templates/docker/docker-compose.yml.tmpl](control-plane/internal/templates/docker/docker-compose.yml.tmpl)
- [deployments/helm/agentfield/values.yaml](deployments/helm/agentfield/values.yaml)
- [deployments/kubernetes/base/control-plane-deployment.yaml](deployments/kubernetes/base/control-plane-deployment.yaml)
- [docs/RELEASE.md](docs/RELEASE.md)
- [examples/python_agent_nodes/rag_evaluation/docker-compose.yml](examples/python_agent_nodes/rag_evaluation/docker-compose.yml)
- [examples/triggers-demo/docker-compose.yml](examples/triggers-demo/docker-compose.yml)
- [scripts/bump_version.py](scripts/bump_version.py)
- [scripts/install.ps1](scripts/install.ps1)
- [scripts/install.sh](scripts/install.sh)
- [scripts/tests/__init__.py](scripts/tests/__init__.py)
- [scripts/tests/test_bump_version.py](scripts/tests/test_bump_version.py)
- [sdk/go/ai/openrouter_attribution.go](sdk/go/ai/openrouter_attribution.go)

</details>



This document covers the installation of the AgentField CLI tool (`af`) on your local system. The CLI tool provides commands to initialize agent projects, start the control plane server, and manage the AgentField development environment.

For guidance on creating your first agent after installation, see [Your First Agent](). For details on running the control plane server, see [Running the Control Plane]().

---

## Supported Platforms

AgentField provides pre-built binaries for the following platforms:

| Operating System | Architecture | Binary Name |
|-----------------|--------------|-------------|
| macOS | Intel (amd64) | `agentfield-darwin-amd64` |
| macOS | Apple Silicon (arm64) | `agentfield-darwin-arm64` |
| Linux | x86_64 (amd64) | `agentfield-linux-amd64` |
| Linux | ARM64 | `agentfield-linux-arm64` |
| Windows | x86_64 (amd64) | `agentfield-windows-amd64.exe` |

All binaries are statically compiled Go executables that include the embedded web UI and SQLite database support with FTS5 extensions.

Sources: [.goreleaser.yml:11-87](), [scripts/install.sh:144-193](), [scripts/install.ps1:66-83]()

---

## Quick Installation

### Unix/Linux/macOS

```bash
curl -fsSL https://agentfield.ai/install.sh | bash
```

This command downloads and executes the installation script, which:
- Detects your operating system and architecture
- Downloads the appropriate binary from GitHub Releases
- Verifies the SHA256 checksum
- Installs to `~/.agentfield/bin/`
- Creates a symlink `af` → `agentfield`
- Configures your shell's PATH

Sources: [scripts/install.sh:1-629]()

### Windows

```powershell
iwr -useb https://agentfield.ai/install.ps1 | iex
```

The PowerShell script performs similar operations:
- Detects architecture
- Downloads the Windows binary
- Verifies checksum
- Installs to `%USERPROFILE%\.agentfield\bin\`
- Creates `af.exe` hardlink or copy
- Updates user PATH environment variable

Sources: [scripts/install.ps1:1-399]()

---

## Installation Flow

```mermaid
flowchart TD
    Start["User executes install script"]
    DetectOS["detect_os()<br/>detect_arch()"]
    DetectOS --> |"os-arch"| GetVersion
    
    GetVersion["Determine version:<br/>$VERSION env var<br/>or get_latest_stable_version()"]
    GetVersion --> ConstructURL
    
    ConstructURL["Construct download URLs:<br/>github.com/.../releases/download/$VERSION/<br/>agentfield-$os-$arch"]
    ConstructURL --> Download
    
    Download["Download binary<br/>download_file()"]
    Download --> DownloadChecksum["Download checksums.txt"]
    DownloadChecksum --> Verify
    
    Verify["verify_checksum()<br/>Compare SHA256 hash"]
    Verify --> |"Match"| Install
    Verify --> |"Mismatch"| Error["Exit with error"]
    
    Install["install_binary()<br/>Copy to $INSTALL_DIR/<br/>Create symlink 'af'"]
    Install --> ConfigPath
    
    ConfigPath["configure_path()<br/>Add to shell config:<br/>~/.bashrc, ~/.zshrc, etc."]
    ConfigPath --> VerifyInstall
    
    VerifyInstall["verify_installation()<br/>Check binary is executable"]
    VerifyInstall --> Success["Print success message<br/>with next steps"]
    
    style Start fill:#f9f9f9
    style Success fill:#f9f9f9
    style Error fill:#f9f9f9
```

**Diagram: Installation Process Flow**

The install script follows a strict verification path to ensure binary integrity before installation.

Sources: [scripts/install.sh:553-626](), [scripts/install.ps1:333-396]()

---

## Platform Detection

The installation scripts use system commands to detect the platform:

```mermaid
flowchart LR
    UnameS["uname -s"]
    UnameM["uname -m"]
    
    UnameS --> OSMap
    UnameM --> ArchMap
    
    OSMap["OS Mapping:<br/>Darwin → darwin<br/>Linux → linux<br/>MINGW*/MSYS*/CYGWIN* → windows"]
    
    ArchMap["Arch Mapping:<br/>x86_64/amd64 → amd64<br/>aarch64/arm64 → arm64"]
    
    OSMap --> BinaryName["Binary name:<br/>agentfield-$os-$arch"]
    ArchMap --> BinaryName
    
    style OSMap fill:#f9f9f9
    style ArchMap fill:#f9f9f9
```

**Diagram: Platform Detection Logic**

Sources: [scripts/install.sh:143-193](), [scripts/install.ps1:66-83]()

---

## Version Management

### Production Installation (Default)

Installs the latest stable release:

```bash
curl -fsSL https://agentfield.ai/install.sh | bash
```

The script calls `get_latest_stable_version()` which queries the GitHub API:

```
GET https://api.github.com/repos/Agent-Field/agentfield/releases/latest
```

Sources: [scripts/install.sh:195-218]()

### Staging/Pre-release Installation

For testing pre-release versions:

```bash
curl -fsSL https://agentfield.ai/install.sh | bash -s -- --staging
```

This installs to a separate directory (`~/.agentfield-staging/bin`) and creates an `af-staging` symlink, allowing both production and staging versions to coexist.

The script calls `get_latest_prerelease_version()` to find the most recent pre-release from:

```
GET https://api.github.com/repos/Agent-Field/agentfield/releases
```

Sources: [scripts/install.sh:220-259](), [scripts/install.sh:34-82]()

### Version Pinning

To install a specific version:

```bash
VERSION=v0.1.21 curl -fsSL https://agentfield.ai/install.sh | bash
```

Sources: [docs/RELEASE.md:196-199]()

---

## Installation Artifacts

After successful installation, the following files exist on the filesystem:

```mermaid
graph TD
    Home["$HOME"]
    
    Home --> AgentField[".agentfield/"]
    AgentField --> Bin["bin/"]
    
    Bin --> Binary["agentfield<br/>(main executable)"]
    Bin --> Symlink["af → agentfield<br/>(symlink)"]
    
    Home --> ShellRC["Shell config:<br/>.bashrc / .zshrc / .config/fish/config.fish"]
    ShellRC --> PathEntry["export PATH=$HOME/.agentfield/bin:$PATH"]
    
    style Home fill:#f9f9f9
    style Binary fill:#f9f9f9
    style Symlink fill:#f9f9f9
```

**Diagram: Filesystem Layout After Installation**

### File Locations

| Component | Production Path | Staging Path |
|-----------|----------------|--------------|
| Install directory | `~/.agentfield/bin/` | `~/.agentfield-staging/bin/` |
| Main executable | `~/.agentfield/bin/agentfield` | `~/.agentfield-staging/bin/agentfield` |
| Symlink | `~/.agentfield/bin/af` | `~/.agentfield-staging/bin/af-staging` |
| PATH entry | Added to shell config | Added to shell config |

Sources: [scripts/install.sh:74-82](), [scripts/install.sh:347-384]()

---

## Checksum Verification

The installation script verifies binary integrity before installation:

1. Downloads `checksums.txt` from the release
2. Extracts the expected SHA256 hash for the platform-specific binary
3. Computes the actual SHA256 hash of the downloaded binary using `sha256sum` or `shasum -a 256`
4. Compares hashes and aborts installation if they don't match

Example `checksums.txt` format:

```
a1b2c3d4e5f6...  agentfield-darwin-amd64
f6e5d4c3b2a1...  agentfield-darwin-arm64
1a2b3c4d5e6f...  agentfield-linux-amd64
...
```

Sources: [scripts/install.sh:292-344](), [scripts/install.ps1:136-186]()

---

## PATH Configuration

The install script automatically configures your shell's PATH by detecting the shell type and modifying the appropriate configuration file:

| Shell | Config File |
|-------|-------------|
| bash | `~/.bashrc` (Linux) or `~/.bash_profile` (macOS) |
| zsh | `~/.zshrc` |
| fish | `~/.config/fish/config.fish` |

The script appends:

```bash
# AgentField CLI
export PATH="$HOME/.agentfield/bin:$PATH"
```

For staging installations, it uses the comment `# AgentField CLI (STAGING)`.

If the install directory is already in PATH, the script skips this step.

Sources: [scripts/install.sh:387-458]()

---

## Post-Installation

### Verification

After installation, reload your shell configuration:

```bash
source ~/.bashrc  # or ~/.zshrc, etc.
```

Verify the installation:

```bash
af --version
```

This should display version information from the `NewRootCommand()` function with embedded build metadata.

Sources: [scripts/install.sh:460-482]()

### Environment Variables

The installation process respects the following environment variables:

| Variable | Purpose | Default |
|----------|---------|---------|
| `VERSION` | Pin to specific version | `latest` |
| `STAGING` | Install staging release | `0` (false) |
| `AGENTFIELD_INSTALL_DIR` | Custom install directory | `~/.agentfield/bin` |
| `SKIP_PATH_CONFIG` | Skip PATH modification | `0` (false) |
| `VERBOSE` | Enable verbose output | `0` (false) |

Example:

```bash
VERBOSE=1 AGENTFIELD_INSTALL_DIR=/usr/local/bin curl -fsSL https://agentfield.ai/install.sh | bash
```

Sources: [scripts/install.sh:10-17](), [scripts/install.ps1:9-12]()

---

## Manual Installation

If you prefer not to use the automated installation script:

1. **Download the binary** from GitHub Releases. The release page provides installation instructions including manual download links. For example, to get `v0.1.21`:
   ```bash
   wget https://github.com/Agent-Field/agentfield/releases/download/v0.1.21/agentfield-linux-amd64
   ```

2. **Verify the checksum**:
   ```bash
   wget https://github.com/Agent-Field/agentfield/releases/download/v0.1.21/checksums.txt
   sha256sum -c checksums.txt --ignore-missing
   ```

3. **Make executable and move to PATH**:
   ```bash
   chmod +x agentfield-linux-amd64
   mv agentfield-linux-amd64 /usr/local/bin/agentfield
   ln -s /usr/local/bin/agentfield /usr/local/bin/af
   ```

Sources: [.goreleaser.yml:181-204](), [docs/RELEASE.md:190-192]()

---

## Binary Build Process

The AgentField CLI binary is built using GoReleaser in a multi-stage GitHub Actions workflow:

```mermaid
flowchart LR
    Source["Go source code<br/>control-plane/cmd/af"]
    WebUI["Web UI<br/>control-plane/web/client"]
    
    WebUI --> BuildUI["npm --prefix control-plane/web/client install<br/>npm --prefix control-plane/web/client run build"]
    BuildUI --> EmbedFS["Embedded in binary<br/>//go:embed directive"]
    
    Source --> GoReleaser["goreleaser build<br/>--id agentfield-$os-$arch"]
    EmbedFS --> GoReleaser
    
    GoReleaser --> |"CGO_ENABLED=1"| Binary["agentfield-$os-$arch"]
    
    Binary --> Sign["Generate SHA256<br/>checksums.txt"]
    Sign --> Release["GitHub Release<br/>+ PyPI + npm + Docker"]
    
    style Source fill:#f9f9f9
    style Binary fill:#f9f9f9
    style Release fill:#f9f9f9
```

**Diagram: Binary Build Pipeline**

Key build details:

- **Build tags**: `embedded`, `sqlite_fts5` enable embedded UI and full-text search
- **CGO**: Required for SQLite (set to `1`)
- **Cross-compilation**: Uses `aarch64-linux-gnu-gcc` for ARM64 on Linux
- **Embed web UI**: Built via `npm run build` in `control-plane/web/client/`
- **ldflags**: Inject version info with `-X main.version={{ .Version }}`

Sources: [.goreleaser.yml:1-88](), [.github/workflows/release.yml:191-280]()

---

## Uninstallation

To remove AgentField:

1. **Remove the binary directory**:
   ```bash
   rm -rf ~/.agentfield
   ```

2. **Remove PATH entry** from your shell configuration file:
   ```bash
   # Edit ~/.bashrc, ~/.zshrc, etc. and remove the AgentField CLI lines
   ```

3. **Optionally, remove configuration**:
   ```bash
   rm -rf ~/.config/agentfield  # if it exists
   ```

Sources: [scripts/install.sh:387-458]()

---

## Troubleshooting

### Issue: Checksum Verification Failed

**Error message:**
```
[ERROR] Checksum verification failed!
Expected: a1b2c3d4...
Got:      f6e5d4c3...
```

**Cause:** Corrupted download or network interruption.

**Solution:** Run the install script again. The script downloads to a temporary directory and cleans up on failure.

Sources: [scripts/install.sh:292-344]()

### Issue: Command Not Found After Installation

**Error message:**
```
bash: af: command not found
```

**Cause:** PATH not updated in current shell session.

**Solution:**
```bash
source ~/.bashrc  # or ~/.zshrc
# OR restart your terminal
```

Sources: [scripts/install.sh:453-458]()

### Issue: Permission Denied on macOS

**Error message:**
```
"agentfield" cannot be opened because the developer cannot be verified
```

**Cause:** macOS Gatekeeper quarantine attribute.

**Solution:** The install script automatically removes this attribute using `xattr -d com.apple.quarantine`. If it persists, manually run:
```bash
xattr -d com.apple.quarantine ~/.agentfield/bin/agentfield
```

Sources: [scripts/install.sh:369-377]()

### Issue: No Pre-release Found

**Error message:**
```
[ERROR] No prerelease version found
```

**Cause:** Attempting to install staging release when none exists.

**Solution:** Install a specific staging version:
```bash
VERSION=v0.1.19-rc.1 curl -fsSL https://agentfield.ai/install.sh | bash -s -- --staging
```

Sources: [scripts/install.sh:247-256]()

---

## Configuration File

While the CLI itself does not require a configuration file for basic operation, the control plane server can use a configuration file specified via the `--config` flag:

```bash
af --config /path/to/agentfield.yaml server
```

The configuration file path is stored in the `cfgFile` variable and accessed via `GetConfigFilePath()`.

Sources: []()

---

## Next Steps

After successful installation:

1. **Initialize your first agent project**: See [Your First Agent]().
2. **Start the control plane**: See [Running the Control Plane]().
3. **Explore SDK options**: See [Python SDK](), [TypeScript SDK](), or [Go SDK]().

Sources: []()

---

# Page: Your First Agent

# Your First Agent

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [control-plane/internal/cli/init.go](control-plane/internal/cli/init.go)
- [control-plane/internal/cli/init_test.go](control-plane/internal/cli/init_test.go)
- [control-plane/internal/templates/go/README.md.tmpl](control-plane/internal/templates/go/README.md.tmpl)
- [control-plane/internal/templates/python/README.md.tmpl](control-plane/internal/templates/python/README.md.tmpl)
- [control-plane/internal/templates/typescript/README.md.tmpl](control-plane/internal/templates/typescript/README.md.tmpl)
- [control-plane/tools/perf/nested_workflow_stress.py](control-plane/tools/perf/nested_workflow_stress.py)
- [deployments/README.md](deployments/README.md)
- [examples/README.md](examples/README.md)
- [examples/python_agent_nodes/hello_world/main.py](examples/python_agent_nodes/hello_world/main.py)
- [examples/python_agent_nodes/image_generation_hello_world/README.md](examples/python_agent_nodes/image_generation_hello_world/README.md)
- [examples/python_agent_nodes/rag_evaluation/README.md](examples/python_agent_nodes/rag_evaluation/README.md)
- [scripts/seed_workflows.py](scripts/seed_workflows.py)
- [sdk/python/agentfield/agent_cli.py](sdk/python/agentfield/agent_cli.py)

</details>



This page guides you through creating your first AgentField agent from scratch. You'll learn how to define reasoners (AI-powered functions) and skills (deterministic functions), start an agent server, and execute capabilities through the control plane.

**Prerequisites**: Complete [Installation](2.1) before proceeding. For information about starting and configuring the control plane, see [Running the Control Plane](2.3).

---

## Overview

An AgentField agent is a Python (FastAPI), TypeScript (Express), or Go HTTP server that:
1. Registers its capabilities (reasoners and skills) with the control plane on startup.
2. Exposes HTTP endpoints for execution.
3. Integrates with memory, identity, and workflow systems automatically.

This page demonstrates the minimal code required to create a working agent and execute its capabilities.

---

## Agent Anatomy

### Basic Structure

**Python Agent Structure:**

```mermaid
graph TB
    subgraph "Agent Node (Code Entity)"
        Agent["Agent Class [sdk/python/agentfield/agent.py]"]
        Agent --> Reasoners["@app.reasoner() [sdk/python/agentfield/agent.py:934-990]"]
        Agent --> Skills["@app.skill() [sdk/python/agentfield/agent.py:1021-1070]"]
        Agent --> Run["app.run() [sdk/python/agentfield/agent.py:1504-1530]"]
    end
    
    subgraph "Runtime Process"
        Run --> FastAPI["FastAPI Server [sdk/python/agentfield/agent_server.py]"]
        FastAPI --> Discovery["/discover"]
        FastAPI --> Execute["/execute"]
        FastAPI --> Health["/health"]
    end
    
    subgraph "Control Plane Integration"
        Discovery --> Register["POST /api/v1/nodes/register"]
        Execute --> Gateway["POST /api/v1/execute/&lt;target&gt;"]
    end
    
    Register -.->|"on startup"| Agent
    Gateway -.->|"routes requests"| Execute
```

**Sources:** [sdk/python/agentfield/agent.py:311-559](), [sdk/python/agentfield/agent.py:934-990](), [sdk/python/agentfield/agent.py:1021-1070](), [sdk/python/agentfield/agent.py:1504-1530]()

---

## Step 1: Create the Agent Project

You can initialize a project manually or use the `af init` command, which provides an interactive setup flow.

```bash
af init my-first-agent
```

The `af init` command (implemented in `control-plane/internal/cli/init.go`) will prompt you for the language (Python, TypeScript, or Go), author name, and email [control-plane/internal/cli/init.go:169-201]().

For this tutorial, create a file called `main.py`:

```python
import os
from agentfield import Agent, AIConfig
from pydantic import BaseModel

# Initialize agent
app = Agent(
    node_id="hello-world",
    agentfield_server=os.getenv("AGENTFIELD_URL", "http://localhost:8080"),
    ai_config=AIConfig(
        model="openai/gpt-4o-mini", 
        temperature=0.7
    ),
)

# ============= SKILL (DETERMINISTIC) =============
@app.skill()
def get_greeting(name: str) -> dict:
    """Returns a greeting template (deterministic - no AI)"""
    return {"message": f"Hello, {name}! Welcome to Agentfield."}

# ============= REASONERS (AI-POWERED) =============
class EmojiResult(BaseModel):
    """Simple schema for emoji addition"""
    text: str
    emoji: str

@app.reasoner()
async def add_emoji(text: str) -> EmojiResult:
    """Uses AI to add an appropriate emoji to text"""
    return await app.ai(
        user=f"Add one appropriate emoji to this greeting: {text}", 
        schema=EmojiResult
    )

@app.reasoner()
async def say_hello(name: str) -> dict:
    """Main entry point - orchestrates skill and reasoner."""
    # Step 1: Get greeting from skill (deterministic)
    greeting = get_greeting(name)

    # Step 2: Add emoji using AI (reasoner)
    result = await add_emoji(greeting["message"])

    return {"greeting": result.text, "emoji": result.emoji, "name": name}

if __name__ == "__main__":
    app.run(auto_port=True)
```

**Sources:** [examples/python_agent_nodes/hello_world/main.py:1-79](), [control-plane/internal/cli/init.go:169-201]()

---

## Step 2: Understanding the Code

### Agent Initialization

The `Agent` constructor performs these key initializations:

| Component | Purpose | File Reference |
|-----------|---------|----------------|
| `node_id` | Unique identifier for this agent node (e.g., "hello-world") | [examples/python_agent_nodes/hello_world/main.py:17]() |
| `agentfield_server` | URL of the control plane (default: http://localhost:8080) | [examples/python_agent_nodes/hello_world/main.py:18]() |
| `ai_config` | LLM configuration, using `AIConfig` to specify model and parameters | [examples/python_agent_nodes/hello_world/main.py:19-21]() |

### Reasoners vs. Skills

AgentField distinguishes between AI-driven reasoning and deterministic logic:

*   **Skills (`@app.skill()`)**: Used for deterministic functions. They do not have direct access to `app.ai()` and are intended for tools, API calls, or simple data transformations [examples/python_agent_nodes/hello_world/main.py:27-30]().
*   **Reasoners (`@app.reasoner()`)**: AI-powered functions. They can use `await app.ai()` to interact with LLMs and can return structured data using Pydantic models like `EmojiResult` [examples/python_agent_nodes/hello_world/main.py:43-49]().

### The Call Graph

In the example above, `say_hello` acts as an orchestrator. It calls a local skill and another local reasoner. AgentField automatically tracks this call graph as a workflow [examples/python_agent_nodes/hello_world/main.py:52-67]().

---

## Step 3: Agent Registration Flow

When you call `app.run()`, the agent starts a heartbeat and registers its capabilities with the control plane.

```mermaid
sequenceDiagram
    participant Agent as Agent Node [main.py]
    participant Server as AgentServer [sdk/python/agentfield/agent_server.py]
    participant CP as Control Plane [af server]
    
    Note over Agent: app.run(auto_port=True)
    
    Agent->>Server: Start FastAPI
    Server->>Server: Resolve callback_url
    
    Server->>CP: POST /api/v1/nodes/register
    Note over CP: Payload includes Node ID,<br/>Reasoners, and Skills metadata
    
    CP-->>Server: 200 OK (Registered)
    Server->>Server: Start Heartbeat Thread
    Note over Server: Sends health status every 30s
```

**Sources:** [sdk/python/agentfield/agent.py:1504-1530](), [examples/python_agent_nodes/hello_world/main.py:78]()

---

## Step 4: Starting and Testing

### 1. Start Control Plane
In your first terminal:
```bash
af server
```

### 2. Start Your Agent
In your second terminal:
```bash
export OPENAI_API_KEY="sk-..."
python main.py
```

### 3. Execute via CLI
The Python SDK includes an `AgentCLI` handler that allows you to run functions directly from the terminal for testing [sdk/python/agentfield/agent_cli.py:18-28]().

```bash
python main.py say_hello --name "Alice"
```

### 4. Execute via Control Plane (REST)
You can trigger the agent through the control plane's execution gateway:

```bash
curl -X POST http://localhost:8080/api/v1/execute/hello-world.say_hello \
  -H "Content-Type: application/json" \
  -d '{"input": {"name": "Alice"}}'
```

**Sources:** [examples/python_agent_nodes/hello_world/main.py:72-78](), [sdk/python/agentfield/agent_cli.py:204-209](), [control-plane/internal/templates/python/README.md.tmpl:27-31]()

---

## Multi-Provider Support

AgentField allows you to switch between AI providers with zero code changes by modifying the `model` string in `AIConfig` or environment variables.

| Provider | Model Example | Prefix |
|----------|--------------|--------|
| **LiteLLM** | `gpt-4o`, `anthropic/claude-3-opus` | (Default or provider/) |
| **OpenRouter** | `openrouter/google/gemini-2.0-flash` | `openrouter/` |

**Example switching via Environment:**
```bash
# Use GPT-4o-mini (OpenAI)
export SMALL_MODEL="openai/gpt-4o-mini"

# Use Gemini (via OpenRouter)
export SMALL_MODEL="openrouter/google/gemini-2.0-flash"
```

**Sources:** [examples/python_agent_nodes/image_generation_hello_world/README.md:19-31](), [examples/python_agent_nodes/hello_world/main.py:20]()

---

## Next Steps

Now that you have created a basic agent, you can explore more advanced patterns:

1.  **Organizing with Routers**: Use `AgentRouter` to split capabilities across multiple files [control-plane/internal/templates/python/README.md.tmpl:50-52]().
2.  **Using Memory**: Access `app.memory` to store state across executions.
3.  **Image Generation**: Use `app.ai_with_vision()` for multimodal tasks [examples/python_agent_nodes/image_generation_hello_world/README.md:173-178]().
4.  **Verifiable Credentials**: Enable cryptographic proof of execution [examples/README.md:18]().

---

# Page: Running the Control Plane

# Running the Control Plane

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [control-plane/cmd/af/main.go](control-plane/cmd/af/main.go)
- [control-plane/cmd/agentfield-server/main.go](control-plane/cmd/agentfield-server/main.go)
- [control-plane/config/agentfield.yaml](control-plane/config/agentfield.yaml)
- [control-plane/internal/cli/agent_commands.go](control-plane/internal/cli/agent_commands.go)
- [control-plane/internal/cli/root.go](control-plane/internal/cli/root.go)
- [control-plane/internal/cli/root_test.go](control-plane/internal/cli/root_test.go)
- [control-plane/internal/config/config.go](control-plane/internal/config/config.go)
- [control-plane/internal/config/config_additional_test.go](control-plane/internal/config/config_additional_test.go)
- [control-plane/internal/core/services/dev_service.go](control-plane/internal/core/services/dev_service.go)
- [control-plane/internal/core/services/server_url.go](control-plane/internal/core/services/server_url.go)
- [control-plane/internal/packages/server_url.go](control-plane/internal/packages/server_url.go)
- [control-plane/internal/server/middleware/auth.go](control-plane/internal/server/middleware/auth.go)
- [control-plane/internal/server/middleware/auth_admin_additional_test.go](control-plane/internal/server/middleware/auth_admin_additional_test.go)
- [control-plane/internal/server/middleware/auth_test.go](control-plane/internal/server/middleware/auth_test.go)
- [control-plane/internal/server/routes_admin.go](control-plane/internal/server/routes_admin.go)
- [control-plane/internal/server/routes_middleware.go](control-plane/internal/server/routes_middleware.go)
- [control-plane/internal/server/server.go](control-plane/internal/server/server.go)
- [control-plane/internal/server/server_additional_test.go](control-plane/internal/server/server_additional_test.go)
- [control-plane/internal/server/server_coverage_additional_test.go](control-plane/internal/server/server_coverage_additional_test.go)
- [deployments/helm/agentfield/templates/control-plane-deployment.yaml](deployments/helm/agentfield/templates/control-plane-deployment.yaml)
- [docs/ENVIRONMENT_VARIABLES.md](docs/ENVIRONMENT_VARIABLES.md)
- [tests/functional/docker/agentfield-test.yaml](tests/functional/docker/agentfield-test.yaml)

</details>



This page explains how to start and configure the AgentField control plane server, access the dashboard UI, and understand the available configuration options. The control plane is a Go-based orchestration service that manages agent registration, workflow execution, memory scopes, and identity.

For information about installing the `af` CLI tool, see [Installation](2.1). For details on the control plane's internal architecture and API endpoints, see [Server Configuration](6.1) and [API Endpoints](6.5).

---

## Starting the Control Plane

The control plane is started using the `af server` command. By default, it listens on port 8080 and automatically attempts to open the dashboard UI in your browser.

**Basic startup:**

```bash
af server
```

This command:
- Initializes the storage backend (SQLite by default) [control-plane/cmd/af/main.go:131-133]()
- Starts the HTTP server on port 8080 [control-plane/config/agentfield.yaml:2-2]()
- Launches the embedded UI [control-plane/cmd/af/main.go:154-163]()
- Opens http://localhost:8080 in your default browser [control-plane/cmd/af/main.go:196-213]()

**Sources:** [control-plane/cmd/af/main.go:53-219](), [control-plane/internal/cli/root.go:142-149]()

---

## Control Plane Startup Flow

The following diagram illustrates the initialization sequence from CLI invocation to the running HTTP server.

**Startup Sequence Diagram**
```mermaid
sequenceDiagram
    participant CLI as "af CLI"
    participant Root as "cli.NewRootCommand"
    participant Main as "runServer (main.go)"
    participant Server as "server.AgentFieldServer"
    participant Storage as "storage.StorageFactory"
    participant Router as "gin.Engine"

    CLI->>Root: "af server --port 8080"
    Root->>Main: "Execute runServer callback"
    Main->>Main: "loadConfig(cfgFilePath)"
    Main->>Main: "Apply flag overrides (port, storage-mode)"
    
    Main->>Server: "server.NewAgentFieldServer(cfg)"
    Server->>Storage: "CreateStorage(cfg.Storage)"
    Storage-->>Server: "Return StorageProvider (SQLite/Postgres)"
    
    Server->>Router: "Initialize Gin Router"
    Server->>Server: "applyGlobalMiddleware() (CORS, Auth, Logger)"
    Server->>Server: "setupRoutes() (API v1, UI, Health)"
    
    Main->>Server: "Start()"
    Server->>Router: "Run HTTP Listener"
    
    alt openBrowserFlag == true
        Main->>Main: "openBrowser(http://localhost:8080)"
    end
    
    Server-->>CLI: "Server running"
```

**Sources:** [control-plane/cmd/af/main.go:53-219](), [control-plane/internal/server/server.go:107-175](), [control-plane/internal/server/routes_middleware.go:18-110]()

---

## Command-Line Options

The `af` root command and the `server` subcommand support several flags for customizing behavior. Flags generally override values found in the `agentfield.yaml` configuration file.

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--port` | int | 8080 | HTTP server port (overrides config) |
| `--config` | string | - | Path to configuration file (e.g., `config/agentfield.yaml`) |
| `--open` | bool | true | Open browser to UI on startup |
| `--backend-only` | bool | false | Run only backend APIs, UI served separately |
| `--ui-dev` | bool | false | Run with UI development server (proxies to backend) |
| `--storage-mode` | string | local | Override storage backend (`local` or `postgres`) |
| `--postgres-url` | string | - | PostgreSQL connection URL (implies `--storage-mode=postgres`) |
| `--no-vc-execution`| bool | false | Disable Verifiable Credentials generation for executions |
| `--verbose`, `-v` | bool | false | Enable debug logging |

**Sources:** [control-plane/internal/cli/root.go:83-93](), [control-plane/cmd/af/main.go:64-151]()

---

## Storage Configuration

AgentField supports two primary storage modes, controlled by `AGENTFIELD_STORAGE_MODE` or the `storage.mode` config key.

### Local Mode (Default)
In `local` mode, the server uses SQLite for relational data and BoltDB for the key-value memory store.
- **Home Directory**: Defaults to `~/.agentfield` unless `AGENTFIELD_HOME` is set. [control-plane/internal/server/server.go:109-116]()
- **Database Path**: Created within the home directory. [control-plane/internal/server/server.go:118-121]()

### Postgres Mode
PostgreSQL is recommended for production and multi-node deployments.
- **Connection**: Configured via `AGENTFIELD_POSTGRES_URL` or individual host/port/user variables. [docs/ENVIRONMENT_VARIABLES.md:28-40]()
- **DSN Example**: `postgres://user:pass@localhost:5432/dbname?sslmode=disable`

**Sources:** [control-plane/internal/config/config.go:187-205](), [docs/ENVIRONMENT_VARIABLES.md:15-40]()

---

## Authentication and Security

The control plane implements multiple layers of security to protect the agent ecosystem.

**Authentication Architecture**
```mermaid
graph TD
    subgraph "Request Entry"
        Req["Incoming HTTP Request"]
    end

    subgraph "Middleware Stack"
        CORS["CORS Middleware"]
        Logger["Gin Logger"]
        Auth["middleware.APIKeyAuth"]
        DIDAuth["middleware.DIDAuthMiddleware"]
    end

    subgraph "Auth Logic"
        KeyCheck{"X-API-Key or Bearer?"}
        DIDCheck{"DID Signature Present?"}
        SkipCheck{"Is Public Route?"}
    end

    subgraph "Identity Context"
        AuthLevel["Set c.Set('auth_level', ...)"]
        CallerID["Set c.Set('caller_agent_id', ...)"]
    end

    Req --> CORS --> Logger --> Auth
    Auth --> SkipCheck
    SkipCheck -- Yes --> DIDAuth
    SkipCheck -- No --> KeyCheck
    
    KeyCheck -- Valid --> AuthLevel
    KeyCheck -- Invalid --> Reject[401 Unauthorized]
    
    DIDAuth --> DIDCheck
    DIDCheck -- Valid --> CallerID
    DIDCheck -- None/Invalid --> Continue["Continue to Handler"]
```

### API Key Authentication
If `AGENTFIELD_API_KEY` is set, the server enforces authentication via:
- `X-API-Key` header
- `Authorization: Bearer <token>` header
- `api_key` query parameter (restricted to specific streaming routes like `/api/v1/memory/events/ws`). [control-plane/internal/server/middleware/auth.go:101-120]()

### Verifiable Credentials (VC)
AgentField uses Decentralized Identifiers (DIDs) and VCs to secure agent-to-agent communication.
- **Execution VCs**: Can be disabled via `--no-vc-execution` for lower latency during development. [control-plane/cmd/af/main.go:147-151]()
- **DID Auth**: When enabled, the server validates cryptographic signatures on incoming requests to establish a trusted `caller_agent_id`. [control-plane/internal/server/routes_middleware.go:90-102]()

**Sources:** [control-plane/internal/server/middleware/auth.go:19-145](), [control-plane/internal/server/routes_middleware.go:64-102]()

---

## Accessing the Dashboard UI

The AgentField dashboard is a React application typically embedded directly into the Go binary.

- **URL**: `http://localhost:8080/ui/` (The root `/` redirects here). [control-plane/internal/server/middleware/auth.go:62-65]()
- **Embedded Mode**: The server uses `client.IsUIEmbedded()` to determine if it should serve pre-built assets from memory. [control-plane/cmd/af/main.go:161-163]()
- **Dev Mode**: If `--ui-dev` is used, the backend assumes a Vite server is running (usually on port 5173) and coordinates accordingly. [control-plane/cmd/af/main.go:198-210]()

### Key Dashboard Views
1. **Agents**: View registered nodes, their health status, and capabilities.
2. **Workflows**: Real-time tracking of agent executions and parent-child relationships.
3. **Memory**: Inspect the key-value store across different scopes (Workflow, Session, Actor, Global).
4. **Logs**: Stream real-time logs from remote agent nodes.

**Sources:** [control-plane/internal/server/server.go:52-56](), [control-plane/cmd/af/main.go:196-213]()

---

## Observability and Monitoring

The control plane provides several built-in mechanisms for health monitoring:

- **Metrics**: Standard Prometheus metrics are exposed at `/metrics`. [control-plane/internal/server/middleware/auth.go:55-58]()
- **Health Endpoint**: `/api/v1/health` provides a summary of the server and storage status. [control-plane/internal/server/middleware/auth.go:55-58]()
- **Structured Logging**: Controlled via `logging.level` (debug, info, warn, error). Payloads can be redacted using `redact_payloads: true` to prevent sensitive data from entering logs. [control-plane/internal/config/config.go:28-41]()
- **Telemetry**: Anonymous usage telemetry is enabled by default to report startup and execution status buckets. [control-plane/internal/config/config.go:46-53]()

**Sources:** [control-plane/config/agentfield.yaml:57-66](), [control-plane/internal/server/routes_middleware.go:40-52]()

---

# Page: Python SDK

# Python SDK

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [VERSION](VERSION)
- [control-plane/internal/handlers/execute_awaiter_status.go](control-plane/internal/handlers/execute_awaiter_status.go)
- [control-plane/internal/handlers/execute_awaiter_status_test.go](control-plane/internal/handlers/execute_awaiter_status_test.go)
- [control-plane/internal/templates/go/go.mod.tmpl](control-plane/internal/templates/go/go.mod.tmpl)
- [examples/python_agent_nodes/agentic_rag/requirements.txt](examples/python_agent_nodes/agentic_rag/requirements.txt)
- [examples/python_agent_nodes/documentation_chatbot/requirements.txt](examples/python_agent_nodes/documentation_chatbot/requirements.txt)
- [examples/python_agent_nodes/hello_world_rag/requirements.txt](examples/python_agent_nodes/hello_world_rag/requirements.txt)
- [sdk/python/CHANGELOG.md](sdk/python/CHANGELOG.md)
- [sdk/python/agentfield/__init__.py](sdk/python/agentfield/__init__.py)
- [sdk/python/agentfield/agent.py](sdk/python/agentfield/agent.py)
- [sdk/python/agentfield/async_execution_manager.py](sdk/python/agentfield/async_execution_manager.py)
- [sdk/python/agentfield/client.py](sdk/python/agentfield/client.py)
- [sdk/python/agentfield/exceptions.py](sdk/python/agentfield/exceptions.py)
- [sdk/python/agentfield/execution_state.py](sdk/python/agentfield/execution_state.py)
- [sdk/python/pyproject.toml](sdk/python/pyproject.toml)
- [sdk/python/tests/test_agent_call.py](sdk/python/tests/test_agent_call.py)
- [sdk/python/tests/test_agent_coverage_additions.py](sdk/python/tests/test_agent_coverage_additions.py)
- [sdk/python/tests/test_async_config.py](sdk/python/tests/test_async_config.py)
- [sdk/python/tests/test_async_execution.py](sdk/python/tests/test_async_execution.py)
- [sdk/python/tests/test_client_laser_push.py](sdk/python/tests/test_client_laser_push.py)
- [sdk/python/tests/test_execution_logger.py](sdk/python/tests/test_execution_logger.py)
- [sdk/python/tests/test_execution_state.py](sdk/python/tests/test_execution_state.py)
- [sdk/typescript/package.json](sdk/typescript/package.json)

</details>



The Python SDK (`agentfield`) provides a FastAPI-based framework for building AI agent nodes that integrate with the AgentField control plane. This SDK handles agent registration, reasoner/skill definitions, memory management, cross-agent communication, and optional identity/credential systems.

For TypeScript development, see [TypeScript SDK](#4). For Go development, see [Go SDK](#5). For control plane configuration, see [Control Plane](#6).

---

## Package Structure

The Python SDK is distributed via PyPI as `agentfield` and provides a FastAPI-based agent runtime with automatic registration, memory scoping, and multi-provider AI integration.

```mermaid
graph TB
    subgraph "Core Agent Runtime"
        Agent["Agent<br/>(FastAPI subclass)"]
        AgentRouter["AgentRouter<br/>(prefix-based composition)"]
        ExecutionContext["ExecutionContext<br/>(contextvars-based)"]
    end
    
    subgraph "Control Plane Communication"
        AgentFieldClient["AgentFieldClient<br/>(HTTP/WebSocket)"]
        AgentFieldHandler["AgentFieldHandler<br/>(registration/heartbeat)"]
    end
    
    subgraph "Memory System"
        MemoryClient["MemoryClient<br/>(HTTP API wrapper)"]
        MemoryInterface["MemoryInterface<br/>(app.memory facade)"]
        MemoryEventClient["MemoryEventClient<br/>(WebSocket events)"]
        ScopedMemoryClient["ScopedMemoryClient<br/>(workflow/session/actor/global)"]
    end
    
    subgraph "AI Integration"
        AgentAI["AgentAI<br/>(litellm wrapper)"]
        AIConfig["AIConfig<br/>(provider config)"]
    end
    
    subgraph "Identity & Credentials"
        DIDManager["DIDManager<br/>(W3C DID operations)"]
        VCGenerator["VCGenerator<br/>(execution attestation)"]
    end
    
    Agent --> AgentFieldClient
    Agent --> MemoryInterface
    Agent --> AgentAI
    Agent --> DIDManager
    Agent --> VCGenerator
    Agent --> AgentFieldHandler
    
    AgentRouter --> Agent
    
    MemoryInterface --> MemoryClient
    MemoryInterface --> MemoryEventClient
    MemoryClient --> ScopedMemoryClient
    
    AgentAI --> AIConfig
    
    AgentFieldHandler --> AgentFieldClient
```

**Sources:** [sdk/python/agentfield/__init__.py:1-90](), [sdk/python/agentfield/agent.py:1-76]()

---

## Installation

Install via pip from PyPI:

```bash
pip install agentfield
```

For development or specific harness capabilities:

```bash
# Development tools
pip install agentfield[dev]

# Harness for autonomous coding (Claude)
pip install agentfield[harness-claude]
```

| Dependency | Purpose | Required |
|------------|---------|----------|
| `fastapi` | HTTP API server framework | Yes |
| `uvicorn` | ASGI server | Yes |
| `requests` | Synchronous HTTP client | Yes |
| `pydantic>=2.0` | Data validation | Yes |
| `litellm` | Multi-provider AI integration | Yes |
| `psutil` | System metrics | Yes |
| `PyYAML>=6.0` | Configuration parsing | Yes |
| `aiohttp>=3.8` | Async HTTP operations | Yes |
| `websockets` | Memory event subscriptions | Yes |
| `cryptography` | DID and crypto operations | Yes |

**Sources:** [sdk/python/pyproject.toml:27-40](), [sdk/python/pyproject.toml:53-85]()

---

## Agent Class

The `Agent` class is the primary entry point for building agent nodes. It inherits from `FastAPI` to provide HTTP endpoints and integrates with the control plane for distributed workflows.

For details, see [Agent Class](#3.1).

### Initialization

```python
from agentfield import Agent

app = Agent(
    node_id="my_agent",
    agentfield_server="http://localhost:8080",
    version="1.0.0",
    auto_register=True,
    vc_enabled=True
)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `node_id` | `str` | Unique identifier for routing |
| `agentfield_server` | `str` | Control plane URL |
| `version` | `str` | Agent version string |
| `auto_register` | `bool` | Auto-register in serverless mode |
| `vc_enabled` | `bool` | Enable verifiable credentials |

**Sources:** [sdk/python/agentfield/agent.py:311-441]()

---

## Defining Reasoners

Reasoners are AI-powered functions that can make decisions, analyze data, or generate content. They are registered via the `@app.reasoner()` decorator.

For details, see [Defining Reasoners](#3.2).

```python
@app.reasoner(
    name="analyze_sentiment",
    tags=["nlp", "sentiment"]
)
async def analyze_sentiment(text: str) -> dict:
    result = await app.ai(
        prompt=f"Analyze the sentiment of: {text}",
        response_model={"sentiment": "str", "confidence": "float"}
    )
    return result
```

**Sources:** [sdk/python/agentfield/agent.py:113-133](), [sdk/python/agentfield/__init__.py:81]()

---

## Defining Skills

Skills are deterministic, non-AI functions for data transformation, API calls, or system operations. They represent the "tools" an agent can use.

For details, see [Defining Skills](#3.3).

```python
@app.skill(name="fetch_url")
def fetch_url(url: str) -> str:
    import requests
    return requests.get(url).text
```

**Sources:** [sdk/python/agentfield/agent.py:135-144]()

---

## AgentRouter

`AgentRouter` enables modular agent composition by organizing capabilities under path prefixes, similar to FastAPI's APIRouter.

For details, see [AgentRouter](#3.4).

```python
from agentfield import AgentRouter
router = AgentRouter(prefix="tools")

@router.skill()
def calculator(a: int, b: int) -> int:
    return a + b

app.include_router(router)
```

**Sources:** [sdk/python/agentfield/router.py:1-200]()

---

## Client & Communication

`AgentFieldClient` handles communication with the control plane, including discovery and execution of other agents.

For details, see [Client & Communication](#3.5).

```mermaid
graph LR
    Client["AgentFieldClient"]
    CP["Control Plane<br/>/api/v1"]
    
    Client -- "execute()" --> CP
    Client -- "discover_capabilities()" --> CP
    Client -- "request_approval()" --> CP
```

**Sources:** [sdk/python/agentfield/client.py:142-218]()

---

## Memory Interface

The memory system provides hierarchical key-value storage with multiple scopes: workflow, session, actor, and global.

For details, see [Memory Interface](#3.6).

```python
@app.reasoner()
async def remember_user(name: str):
    # Scoped automatically to current session
    await app.memory.set("user_name", name)
```

**Sources:** [sdk/python/agentfield/memory.py:1-700]()

---

## DID & Verifiable Credentials

AgentField uses W3C Decentralized Identifiers (DIDs) for cryptographic identity and Verifiable Credentials (VCs) for execution attestation.

For details, see [DID & Verifiable Credentials](#3.7).

```mermaid
graph TB
    subgraph "Identity Package"
        DIDM["DIDManager"]
        VCG["VCGenerator"]
    end
    
    DIDM -- "signs" --> Req["Request Headers"]
    VCG -- "attests" --> Exec["Execution VC"]
```

**Sources:** [sdk/python/agentfield/did_manager.py:1-338](), [sdk/python/agentfield/vc_generator.py:1-400]()

---

## Serverless Mode

Agents can run in serverless environments (AWS Lambda, etc.) using `handle_serverless()` to wrap the agent's logic.

For details, see [Serverless Mode](#3.8).

```python
def lambda_handler(event, context):
    return app.handle_serverless(event)
```

**Sources:** [sdk/python/agentfield/agent.py:578-769]()

---

# Page: Agent Class

# Agent Class

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [control-plane/internal/handlers/execute_awaiter_status.go](control-plane/internal/handlers/execute_awaiter_status.go)
- [control-plane/internal/handlers/execute_awaiter_status_test.go](control-plane/internal/handlers/execute_awaiter_status_test.go)
- [control-plane/internal/infrastructure/process/port_manager.go](control-plane/internal/infrastructure/process/port_manager.go)
- [control-plane/internal/services/ui_service.go](control-plane/internal/services/ui_service.go)
- [control-plane/pkg/types/types.go](control-plane/pkg/types/types.go)
- [control-plane/web/client/src/pages/AgentsPage.tsx](control-plane/web/client/src/pages/AgentsPage.tsx)
- [sdk/python/agentfield/agent.py](sdk/python/agentfield/agent.py)
- [sdk/python/agentfield/agent_server.py](sdk/python/agentfield/agent_server.py)
- [sdk/python/agentfield/async_execution_manager.py](sdk/python/agentfield/async_execution_manager.py)
- [sdk/python/agentfield/client.py](sdk/python/agentfield/client.py)
- [sdk/python/agentfield/exceptions.py](sdk/python/agentfield/exceptions.py)
- [sdk/python/agentfield/execution_state.py](sdk/python/agentfield/execution_state.py)
- [sdk/python/tests/test_agent_call.py](sdk/python/tests/test_agent_call.py)
- [sdk/python/tests/test_agent_coverage_additions.py](sdk/python/tests/test_agent_coverage_additions.py)
- [sdk/python/tests/test_agent_graceful_shutdown.py](sdk/python/tests/test_agent_graceful_shutdown.py)
- [sdk/python/tests/test_async_config.py](sdk/python/tests/test_async_config.py)
- [sdk/python/tests/test_async_execution.py](sdk/python/tests/test_async_execution.py)
- [sdk/python/tests/test_client_laser_push.py](sdk/python/tests/test_client_laser_push.py)
- [sdk/python/tests/test_execution_state.py](sdk/python/tests/test_execution_state.py)

</details>



This page documents the `Agent` class in the Python SDK, which is the primary interface for building agent nodes. For information about defining reasoners and skills using decorators, see [Defining Reasoners](#3.2) and [Defining Skills](#3.3). For memory operations, see [Memory Interface](#3.6). For DID and VC functionality, see [DID & Verifiable Credentials](#3.7).

The `Agent` class is defined in [sdk/python/agentfield/agent.py:311-1585]() and serves as the foundation for all agent implementations. It extends FastAPI to provide HTTP endpoints while integrating with the AgentField control plane for distributed AI workflows.

**Sources:** [sdk/python/agentfield/agent.py:311-356](), [sdk/python/agentfield/agent.py:519-527]()

---

## Class Overview and Inheritance

The `Agent` class inherits from FastAPI, making it both a web server and an agent node. This design enables automatic HTTP endpoint generation, OpenAPI schema support, and seamless integration with the AgentField ecosystem.

### Agent Component Architecture
```mermaid
graph TB
    ["FastAPI (Web Framework)"] --> [AgentNode]
    
    subgraph "Core Agent Entity"
    [AgentNode] --> [Handlers]
    [AgentNode] --> [Managers]
    [AgentNode] --> [Clients]
    end
    
    subgraph "sdk/python/agentfield/"
    [Handlers] --> AgentAI["AgentAI (AI operations)"]
    [Handlers] --> AgentCLI["AgentCLI (CLI interactions)"]
    [Handlers] --> AgentFieldHandler["AgentFieldHandler (Control plane comm)"]
    [Handlers] --> AgentWorkflow["AgentWorkflow (Workflow tracking)"]
    [Handlers] --> AgentServer["AgentServer (HTTP endpoints)"]
    
    [Managers] --> DIDManager["DIDManager (Identity management)"]
    [Managers] --> VCGenerator["VCGenerator (Credential generation)"]
    [Managers] --> AsyncExecutionManager["AsyncExecutionManager (Async tasks)"]
    
    [Clients] --> AgentFieldClient["AgentFieldClient (Control plane API)"]
    [Clients] --> MemoryClient["MemoryClient (Memory operations)"]
    [Clients] --> MemoryEventClient["MemoryEventClient (WebSocket events)"]
    [Clients] --> ConnectionManager["ConnectionManager (Resilient connectivity)"]
    end
```

**Sources:** [sdk/python/agentfield/agent.py:311-442](), [sdk/python/agentfield/agent.py:519-527](), [sdk/python/agentfield/agent_server.py:19-29]()

---

## Constructor Parameters

The `Agent` constructor accepts parameters to configure its identity and behavior:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `node_id` | `str` | Required | Unique identifier for this agent node |
| `agentfield_server` | `str` | `"http://localhost:8080"` | Control plane URL |
| `version` | `str` | `"1.0.0"` | Agent version string |
| `ai_config` | `Optional[AIConfig]` | `None` | AI/LLM configuration |
| `memory_config` | `Optional[MemoryConfig]` | `None` | Memory behavior configuration |
| `dev_mode` | `bool` | `False` | Enable verbose logging and debugging |
| `async_config` | `Optional[AsyncConfig]` | `None` | Async execution configuration |
| `callback_url` | `Optional[str]` | `None` | Explicit callback URL for control plane |
| `auto_register` | `bool` | `True` | Auto-register on first invocation |
| `api_key` | `Optional[str]` | `None` | API key for control plane authentication |

**Sources:** [sdk/python/agentfield/agent.py:357-442]()

---

## Handler and Client Systems

The `Agent` class delegates specific logic to specialized handlers and manages communication through clients.

### Initialization Sequence
```mermaid
sequenceDiagram
    participant User
    participant Agent as Agent Class [agent.py]
    participant Handler as AgentFieldHandler [agent_field_handler.py]
    participant Client as AgentFieldClient [client.py]
    participant Manager as AsyncExecutionManager [async_execution_manager.py]
    
    User->>Agent: Agent(node_id="test-agent")
    Agent->>Client: __init__(base_url, api_key)
    Agent->>Manager: __init__(base_url, config)
    Agent->>Handler: __init__(agent_instance)
    Agent->>Agent: setup_agentfield_routes()
    
    Note over Agent, Client: Lazy initialization of MemoryClient on first .memory access
```

**Sources:** [sdk/python/agentfield/agent.py:357-577](), [sdk/python/agentfield/client.py:147-171](), [sdk/python/agentfield/async_execution_manager.py:199-218]()

### Core Attributes

- `self.node_id`: Unique identifier for the agent node [sdk/python/agentfield/agent.py:444]().
- `self.client`: Instance of `AgentFieldClient` for control plane interactions [sdk/python/agentfield/agent.py:479]().
- `self._async_execution_manager`: Manages polling and state for long-running tasks [sdk/python/agentfield/agent.py:483]().
- `self._current_status`: Current lifecycle state (`AgentStatus.READY`, `BUSY`, etc.) [sdk/python/agentfield/agent.py:489]().

---

## Lifecycle and Server Management

### Status States

The agent moves through several lifecycle states defined in `AgentStatus` [sdk/python/agentfield/agent.py:489]():
- `STARTING`: Initializing components.
- `READY`: Registered and listening for requests.
- `BUSY`: Currently executing a reasoner or skill.
- `OFFLINE`: Shutting down or disconnected.

### Graceful Shutdown

The agent implements a graceful shutdown process to notify the control plane and clean up resources.

```mermaid
sequenceDiagram
    participant CP as Control Plane
    participant Srv as AgentServer [agent_server.py]
    participant Agt as Agent [agent.py]
    participant Mgr as AsyncExecutionManager [async_execution_manager.py]

    CP->>Srv: POST /shutdown
    Srv->>Agt: Set _shutdown_requested = True
    Srv->>Agt: Set status = OFFLINE
    Srv->>Agt: notify_graceful_shutdown()
    Agt->>Mgr: stop() (cancel in-flight tasks)
    Agt->>Agt: _cleanup_async_resources()
    Srv->>Srv: os._exit(0) after timeout
```

**Sources:** [sdk/python/agentfield/agent_server.py:163-192](), [sdk/python/tests/test_agent_graceful_shutdown.py:28-63](), [sdk/python/agentfield/async_execution_manager.py:311-325]()

---

## Async Execution and Call Logic

The `Agent.call()` method is the primary way agents interact with each other. It supports both synchronous and asynchronous execution patterns.

### Execution Flow
1. **Local Call**: If the target is the agent itself, it executes locally.
2. **Remote Call**: If `async_config.enable_async_execution` is true, it uses `execute_async` [sdk/python/agentfield/agent.py:1100-1150]().
3. **Polling**: The `AsyncExecutionManager` polls the control plane for results using adaptive intervals [sdk/python/agentfield/async_execution_manager.py:185-197]().
4. **Fallback**: If async execution fails with a transport error, it may fallback to synchronous execution [sdk/python/tests/test_agent_call.py:115-132]().

### Exception Handling in Calls
The SDK distinguishes between different failure modes to prevent unnecessary retries:
- `ExecutionFailedError`: The remote reasoner ran and returned an explicit failure. The SDK skips sync fallback to save budget [sdk/python/agentfield/exceptions.py:17-33]().
- `ExecutionTimeoutError`: The wait deadline was hit. Retrying via sync is skipped as it might double invocation costs [sdk/python/agentfield/exceptions.py:74-77]().
- `ExecutionCancelledError`: Explicit user intent to stop work; never retried [sdk/python/agentfield/exceptions.py:80-96]().

**Sources:** [sdk/python/agentfield/agent.py:1100-1150](), [sdk/python/agentfield/exceptions.py:1-152](), [sdk/python/tests/test_agent_call.py:101-112]()

---

## Human-in-the-loop: Pause and Resume

The `Agent.pause()` method allows a reasoner to suspend execution while waiting for human approval.

```python
result = await app.pause(
    approval_request_id="req-123",
    expires_in_hours=24
)
if result.approved:
    # continue execution
```

**Internal Mechanics:**
- The agent registers a future in the `_pause_manager` [sdk/python/tests/test_agent_coverage_additions.py:75-92]().
- It enters a `wait_for` loop that does not consume the active execution timeout budget [sdk/python/tests/test_async_execution.py:96-104]().
- When the control plane sends a resume webhook, the `_pause_manager` resolves the future with an `ApprovalResult` [sdk/python/agentfield/client.py:70-78]().

**Sources:** [sdk/python/agentfield/agent.py:1250-1300](), [sdk/python/tests/test_async_execution.py:96-153](), [sdk/python/tests/test_agent_coverage_additions.py:75-107]()

---

## Serverless Mode

For deployments like AWS Lambda, the `handle_serverless()` method processes incoming events without a long-running server.

- **Discovery**: Returns the agent's metadata, reasoners, and skills [sdk/python/tests/test_agent_coverage_additions.py:51-60]().
- **Execution**: Maps the event to a reasoner/skill call, sets up the `ExecutionContext`, and returns the result as a standard HTTP response [sdk/python/agentfield/agent.py:578-770]().

**Sources:** [sdk/python/agentfield/agent.py:578-770](), [sdk/python/tests/test_agent_coverage_additions.py:51-60]()

---

# Page: Defining Reasoners

# Defining Reasoners

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [control-plane/internal/handlers/execute_awaiter_status.go](control-plane/internal/handlers/execute_awaiter_status.go)
- [control-plane/internal/handlers/execute_awaiter_status_test.go](control-plane/internal/handlers/execute_awaiter_status_test.go)
- [sdk/python/agentfield/agent.py](sdk/python/agentfield/agent.py)
- [sdk/python/agentfield/async_execution_manager.py](sdk/python/agentfield/async_execution_manager.py)
- [sdk/python/agentfield/client.py](sdk/python/agentfield/client.py)
- [sdk/python/agentfield/decorator_metadata.py](sdk/python/agentfield/decorator_metadata.py)
- [sdk/python/agentfield/decorators.py](sdk/python/agentfield/decorators.py)
- [sdk/python/agentfield/exceptions.py](sdk/python/agentfield/exceptions.py)
- [sdk/python/agentfield/execution_state.py](sdk/python/agentfield/execution_state.py)
- [sdk/python/agentfield/router.py](sdk/python/agentfield/router.py)
- [sdk/python/tests/test_accepts_webhook.py](sdk/python/tests/test_accepts_webhook.py)
- [sdk/python/tests/test_agent_call.py](sdk/python/tests/test_agent_call.py)
- [sdk/python/tests/test_agent_coverage_additions.py](sdk/python/tests/test_agent_coverage_additions.py)
- [sdk/python/tests/test_async_config.py](sdk/python/tests/test_async_config.py)
- [sdk/python/tests/test_async_execution.py](sdk/python/tests/test_async_execution.py)
- [sdk/python/tests/test_client_laser_push.py](sdk/python/tests/test_client_laser_push.py)
- [sdk/python/tests/test_decorator_code_origin.py](sdk/python/tests/test_decorator_code_origin.py)
- [sdk/python/tests/test_execution_state.py](sdk/python/tests/test_execution_state.py)
- [sdk/python/tests/test_router.py](sdk/python/tests/test_router.py)
- [sdk/python/tests/test_trigger_param_binding.py](sdk/python/tests/test_trigger_param_binding.py)
- [sdk/python/tests/test_workflow_parent_child.py](sdk/python/tests/test_workflow_parent_child.py)

</details>



## Purpose and Scope

This document describes how to define **reasoners** in the Python SDK using the `@app.reasoner()` decorator. Reasoners are AI-powered functions that leverage large language models (LLMs) to perform intelligent reasoning tasks such as analysis, summarization, classification, and generation. They form the core cognitive capabilities of an AgentField agent.

For information about deterministic functions without AI capabilities, see [Defining Skills](3.3). For the underlying Agent class initialization and configuration, see [Agent Class](3.1). For accessing memory within reasoners, see [Memory Interface](3.6).

---

## What is a Reasoner?

A **reasoner** is a function decorated with `@app.reasoner()` that has access to AI models, memory, and execution context. Reasoners are registered with the AgentField control plane during agent startup and can be invoked via the execution gateway by other agents or external clients.

**Key Characteristics:**
- **AI-Powered**: Access to LLMs via `app.ai()` for intelligent reasoning.
- **Stateful**: Access to persistent memory via `app.memory`.
- **Context-Aware**: Access to execution metadata via `app.ctx`.
- **Schema-Validated**: Automatic input validation using Pydantic models [sdk/python/agentfield/agent.py:113-133]().
- **Triggerable**: Can be bound to external events or schedules [sdk/python/agentfield/decorators.py:88-123]().

**Diagram: Reasoner Architecture**

```mermaid
graph TB
    subgraph "Developer Code"
        DecoratorUsage["@app.reasoner(path='/analyze')"]
        FunctionDef["async def analyze(text: str)"]
    end
    
    subgraph "Agent Instance"
        ReasonerRegistry["agent._reasoner_registry: Dict[str, ReasonerEntry]"]
        ReasonerMethod["agent.reasoner() decorator"]
    end
    
    subgraph "Execution Environment"
        ExecutionContext["ExecutionContext<br/>workflow_id, session_id"]
        MemoryInterface["MemoryInterface<br/>app.memory"]
        AIHandler["AgentAI<br/>app.ai()"]
    end
    
    subgraph "Runtime Services"
        LLMProvider["AI Provider<br/>OpenAI, Anthropic, etc."]
        MemoryBackend["Memory Storage<br/>SQLite/PostgreSQL"]
        VCGenerator["VCGenerator<br/>Audit Trail"]
    end
    
    DecoratorUsage --> ReasonerMethod
    FunctionDef --> ReasonerMethod
    ReasonerMethod --> ReasonerRegistry
    
    FunctionDef --> ExecutionContext
    FunctionDef --> MemoryInterface
    FunctionDef --> AIHandler
    
    AIHandler --> LLMProvider
    MemoryInterface --> MemoryBackend
    ExecutionContext --> VCGenerator
```
**Sources:** [sdk/python/agentfield/agent.py:113-133](), [sdk/python/agentfield/agent.py:1081-1239](), [sdk/python/agentfield/decorators.py:77-170]()

---

## Basic Reasoner Definition

### Minimal Example

The simplest reasoner requires only a function decorated with `@app.reasoner()`:

```python
from agentfield import Agent

app = Agent(node_id="analyst")

@app.reasoner()
async def summarize_document(text: str) -> str:
    """Summarize the given text into 3 key points."""
    result = await app.ai(
        prompt=f"Summarize this text into 3 key points:\n\n{text}"
    )
    return result
```

### Decorator Parameters

The `@app.reasoner()` decorator accepts several configuration parameters to control behavior and metadata:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `path` | `str` | `None` | Custom API endpoint path for the reasoner [sdk/python/agentfield/decorators.py:115](). |
| `tags` | `List[str]` | `[]` | Tags for grouping and authorization [sdk/python/agentfield/decorators.py:116](). |
| `description` | `str` | Docstring | Human-readable description [sdk/python/agentfield/decorators.py:117](). |
| `triggers` | `List[Trigger]` | `None` | Typed bindings for events/schedules [sdk/python/agentfield/decorators.py:111-114](). |
| `vc_enabled` | `bool` | `None` | Override agent-level VC generation [sdk/python/agentfield/agent.py:124](). |
| `accepts_webhook`| `bool \| str`| `"warn"` | Controls if UI-managed triggers can invoke this [sdk/python/agentfield/agent.py:130](). |

**Sources:** [sdk/python/agentfield/agent.py:113-133](), [sdk/python/agentfield/decorators.py:77-170]()

---

## Triggers and Webhooks

Reasoners can be automatically invoked by the control plane based on external events or cron schedules.

### Event and Schedule Triggers

You can define triggers directly in the decorator or using "sugar" decorators:

```python
from agentfield import on_event, on_schedule

@app.reasoner()
@on_schedule("0 9 * * *") # Every day at 9 AM
async def daily_report(trigger=None):
    # 'trigger' receives a TriggerContext object
    pass

@app.reasoner()
@on_event("github", types=["push"])
async def handle_push(event: dict, trigger=None):
    # 'event' is the payload, 'trigger' is the context
    pass
```

### Parameter Binding Contract
When a trigger fires, the runtime follows a specific binding contract:
1. **Payload**: Bound to the first parameter that is NOT `trigger`, `webhook`, or `execution_context` [sdk/python/tests/test_trigger_param_binding.py:22-25]().
2. **Context**: Bound to parameters named `trigger` or `webhook` [sdk/python/tests/test_trigger_param_binding.py:16-20]().

**Sources:** [sdk/python/agentfield/decorators.py:172-208](), [sdk/python/tests/test_trigger_param_binding.py:1-31]()

---

## Accessing Execution Context

The `app.ctx` property provides access to the current `ExecutionContext`. This is vital for multi-agent workflows where tracking parentage is required.

```python
@app.reasoner()
async def process_task(data: str):
    ctx = app.ctx
    print(f"Workflow: {ctx.workflow_id}")
    print(f"Execution: {ctx.execution_id}")
    
    # Check if this was called by another agent
    if ctx.parent_execution_id:
        print(f"Called by: {ctx.parent_workflow_id}")
```

**Sources:** [sdk/python/agentfield/execution_context.py:37-42](), [sdk/python/agentfield/agent.py:918-959]()

---

## Organizing with AgentRouter

For large agents, use `AgentRouter` to group reasoners by prefix and tags, similar to FastAPI's `APIRouter`.

```python
from agentfield import AgentRouter

router = AgentRouter(prefix="/nlp", tags=["text-processing"])

@router.reasoner(path="/summarize")
async def summarize(text: str):
    return "..."

app.include_router(router)
```

**Diagram: Router to Agent Mapping**

```mermaid
graph LR
    subgraph "AgentRouter Instance"
        R_Reasoner["router.reasoner()"]
        R_Prefix["prefix: '/nlp'"]
        R_Tags["tags: ['text-processing']"]
    end
    
    subgraph "Agent Instance"
        A_Include["agent.include_router(router)"]
        A_Registry["agent._reasoner_registry"]
    end
    
    R_Reasoner --> A_Include
    A_Include --> A_Registry
    
    subgraph "Resulting Endpoint"
        Endpoint["/reasoners/nlp/summarize"]
    end
    
    A_Registry -.-> Endpoint
```
**Sources:** [sdk/python/agentfield/router.py:17-27](), [sdk/python/agentfield/router.py:30-86](), [sdk/python/agentfield/router.py:165-201]()

---

## Async Execution and Timeouts

By default, reasoners support asynchronous execution. If a reasoner takes a long time, the SDK can manage polling and status updates via the `AsyncExecutionManager` [sdk/python/agentfield/async_execution_manager.py:185-198]().

### Active vs. Wall-clock Timeouts
AgentField distinguishes between **active work** and **paused time** (e.g., waiting for human approval).
- **Active Timeout**: Bounded by `default_execution_timeout`. If the reasoner is doing CPU/IO work past this, it times out [sdk/python/tests/test_async_execution.py:195-198]().
- **Pause Clock**: When `app.pause()` is called, the timeout "clock" stops, so human response time doesn't consume the execution budget [sdk/python/tests/test_async_execution.py:96-104]().

### Reporting Failure
If a reasoner encounters a domain-level failure (e.g., "Budget Exhausted"), it should raise `ReasonerFailed`. This allows the agent to return a structured `result` even while marking the execution as `failed` [sdk/python/agentfield/exceptions.py:36-60]().

```python
from agentfield.exceptions import ReasonerFailed

@app.reasoner()
async def expensive_op():
    if budget < 0:
        raise ReasonerFailed("Out of credits", result={"partial": "data"})
```

**Sources:** [sdk/python/agentfield/async_execution_manager.py:185-198](), [sdk/python/agentfield/exceptions.py:36-60](), [sdk/python/tests/test_async_execution.py:96-111]()

---

## Verifiable Credentials (VCs)

Reasoners can generate VCs to provide a cryptographic audit trail of the reasoning process. This is controlled by the `vc_enabled` flag in the `ReasonerEntry` [sdk/python/agentfield/agent.py:124]().

- **Input Hashing**: The reasoner's input arguments are hashed.
- **Output Hashing**: The result is hashed.
- **Signature**: The agent signs the transition using its DID private key.

**Sources:** [sdk/python/agentfield/agent.py:113-133](), [sdk/python/agentfield/vc_generator.py]()

---

# Page: Defining Skills

# Defining Skills

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [control-plane/internal/handlers/execute_awaiter_status.go](control-plane/internal/handlers/execute_awaiter_status.go)
- [control-plane/internal/handlers/execute_awaiter_status_test.go](control-plane/internal/handlers/execute_awaiter_status_test.go)
- [sdk/python/agentfield/agent.py](sdk/python/agentfield/agent.py)
- [sdk/python/agentfield/async_execution_manager.py](sdk/python/agentfield/async_execution_manager.py)
- [sdk/python/agentfield/client.py](sdk/python/agentfield/client.py)
- [sdk/python/agentfield/decorator_metadata.py](sdk/python/agentfield/decorator_metadata.py)
- [sdk/python/agentfield/decorators.py](sdk/python/agentfield/decorators.py)
- [sdk/python/agentfield/exceptions.py](sdk/python/agentfield/exceptions.py)
- [sdk/python/agentfield/execution_state.py](sdk/python/agentfield/execution_state.py)
- [sdk/python/agentfield/router.py](sdk/python/agentfield/router.py)
- [sdk/python/tests/test_accepts_webhook.py](sdk/python/tests/test_accepts_webhook.py)
- [sdk/python/tests/test_agent_call.py](sdk/python/tests/test_agent_call.py)
- [sdk/python/tests/test_agent_coverage_additions.py](sdk/python/tests/test_agent_coverage_additions.py)
- [sdk/python/tests/test_async_config.py](sdk/python/tests/test_async_config.py)
- [sdk/python/tests/test_async_execution.py](sdk/python/tests/test_async_execution.py)
- [sdk/python/tests/test_client_laser_push.py](sdk/python/tests/test_client_laser_push.py)
- [sdk/python/tests/test_decorator_code_origin.py](sdk/python/tests/test_decorator_code_origin.py)
- [sdk/python/tests/test_execution_state.py](sdk/python/tests/test_execution_state.py)
- [sdk/python/tests/test_router.py](sdk/python/tests/test_router.py)
- [sdk/python/tests/test_trigger_param_binding.py](sdk/python/tests/test_trigger_param_binding.py)
- [sdk/python/tests/test_workflow_parent_child.py](sdk/python/tests/test_workflow_parent_child.py)

</details>



## Purpose and Scope

This page documents how to define and implement **skills** in the Python SDK. Skills are deterministic, non-AI-powered functions that perform specific operations like data fetching, formatting, calculations, or API calls. They complement reasoners (AI-powered functions) and provide reliable, predictable behavior.

For information about defining AI-powered functions, see [Defining Reasoners](#3.2). For organizing skills with routers, see [AgentRouter](#3.4). For accessing memory within skills, see [Memory Interface](#3.6).

---

## What are Skills?

Skills are **deterministic functions** that execute predictable operations without LLM inference. They provide:

- **Reliability**: No AI variability or token costs.
- **Speed**: No network calls to LLM providers.
- **Precision**: Exact computation and data manipulation.
- **Integration**: API calls, database queries, file operations.

**Key Distinction**: Skills execute logic directly, while reasoners delegate to LLMs for decision-making or generation. Internally, the SDK stores these in a `SkillEntry` dataclass which uses `__slots__` for memory efficiency.

| Aspect | Skills | Reasoners |
|--------|--------|-----------|
| **Execution** | Deterministic code | AI inference via LLM |
| **Cost** | No tokens | Consumes tokens |
| **Latency** | Milliseconds | Seconds (network + inference) |
| **Output** | Always predictable | Variable/creative |
| **Use Cases** | Data fetching, parsing, calculations | Analysis, generation, reasoning |

Sources: [sdk/python/agentfield/agent.py:135-144](), [sdk/python/agentfield/agent.py:312-354]()

---

## Basic Skill Definition

### The `@app.skill()` Decorator

Skills are defined using the `@app.skill()` decorator on regular Python functions. The decorator can be used with or without parentheses.

```python
from agentfield import Agent

app = Agent(node_id="my_agent")

@app.skill()
def format_currency(amount: float, currency: str = "USD") -> str:
    """Format a number as currency with proper symbols."""
    symbols = {"USD": "$", "EUR": "€", "GBP": "£"}
    symbol = symbols.get(currency, currency)
    return f"{symbol}{amount:,.2f}"

@app.skill()
async def fetch_weather(city: str) -> dict:
    """Fetch current weather data for a city."""
    import httpx
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.weather.com/current",
            params={"city": city}
        )
        return response.json()
```

**Both synchronous and asynchronous functions are supported**. The SDK automatically handles execution in the appropriate context during the `handle_execute` lifecycle.

Sources: [sdk/python/agentfield/agent.py:346-350](), [sdk/python/agentfield/agent.py:1456-1508]()

---

## Skill Lifecycle and Registration

### Skill Registration Flow

The following diagram illustrates how a skill moves from definition in code to being registered in the Control Plane.

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant Agent as "Agent Instance (agent.py)"
    participant Decorator as "@app.skill()"
    participant Registry as "SkillEntry (agent.py)"
    participant CP as "Control Plane (af server)"
    
    Dev->>Agent: "Create Agent instance"
    Dev->>Decorator: "Define skill"
    Decorator->>Decorator: "inspect.signature(func)"
    Decorator->>Registry: "Create SkillEntry"
    Note over Registry: "Stores id, func, input_types,<br/>output_type, tags, vc_enabled"
    
    Dev->>Agent: "app.serve()"
    Agent->>Agent: "_handle_discovery()"
    Agent->>CP: "POST /api/v1/nodes/register"
    Note over Agent,CP: "Payload includes skills metadata<br/>generated via _get_handler_schema"
    CP-->>Agent: "200 OK"
```

Sources: [sdk/python/agentfield/agent.py:135-144](), [sdk/python/agentfield/agent.py:444-448](), [sdk/python/agentfield/agent.py:1010-1045](), [sdk/python/agentfield/agent_field_handler.py:119-132]()

---

## Skill Metadata and Configuration

### Decorator Parameters

The `@app.skill()` decorator accepts configuration parameters that override default agent settings:

```python
@app.skill(
    tags=["data", "external"],
    description="Custom description for documentation",
    vc_enabled=True  # Override agent-level VC setting
)
def fetch_user_data(user_id: str) -> dict:
    """Fetch user profile from external API."""
    pass
```

### Skill Metadata Structure

Each registered skill generates metadata. The `SkillEntry` class facilitates this storage:

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Function name (e.g., `"fetch_user_data"`) |
| `input_types` | `Dict[str, tuple]` | (type, default) tuples extracted via `inspect` |
| `output_type` | `type` | The return type hint of the function |
| `tags` | `list[str]` | Categorization labels |
| `vc_enabled` | `bool` | Whether VCs are generated for this skill |

The `input_schema` is generated on-demand during discovery or execution using Pydantic's schema generation logic.

Sources: [sdk/python/agentfield/agent.py:135-144](), [sdk/python/agentfield/agent.py:447-451](), [sdk/python/agentfield/pydantic_utils.py:1-20]()

---

## Execution Context in Skills

### Accessing Context Services

Skills have access to the same execution context as reasoners via the `Agent` instance methods.

```python
@app.skill()
def store_computation_result(key: str, value: any) -> dict:
    # Access memory interface
    app.memory.set(f"results.{key}", value)
    
    # Access execution context metadata via get_current_context()
    ctx = app.ctx
    
    return {
        "stored": True,
        "workflow_id": ctx.workflow_id,
        "execution_id": ctx.execution_id
    }
```

### Available Context Properties

| Property | Type | Description |
|----------|------|-------------|
| `app.memory` | `MemoryInterface` | Scoped memory access (KV and Vector) |
| `app.ctx` | `ExecutionContext` | Current execution metadata (run_id, workflow_id) |
| `app.call()` | `method` | Method to call other agents/reasoners |

Sources: [sdk/python/agentfield/agent.py:809-916](), [sdk/python/agentfield/agent.py:918-959](), [sdk/python/agentfield/execution_context.py:15-50]()

---

## Skill Execution Architecture

This diagram bridges the "Natural Language Space" (invoking a capability) to the "Code Entity Space" (the actual SDK classes and functions).

```mermaid
graph TB
    subgraph "External/Control Plane"
        Request["POST /api/v1/execute"]
        CPClient["AgentFieldClient (client.py)"]
    end
    
    subgraph "Agent Node Runtime"
        Handler["AgentFieldHandler (agent_field_handler.py)"]
        Agent["Agent Class (agent.py)"]
        ExecContext["ExecutionContext (execution_context.py)"]
        Registry["SkillEntry (agent.py)"]
    end

    Request --> Handler
    Handler --> Agent
    Agent -- "lookup" --> Registry
    Agent -- "wrap" --> ExecContext
    ExecContext -- "execute" --> UserFunc["User defined @app.skill function"]
    
    UserFunc -- "state" --> Memory["MemoryInterface (memory.py)"]
    UserFunc -- "audit" --> VCGen["VCGenerator (vc_generator.py)"]
```

Sources: [sdk/python/agentfield/agent.py:1456-1508](), [sdk/python/agentfield/agent_field_handler.py:119-168](), [sdk/python/agentfield/client.py:142-171]()

---

## Input Validation and Pydantic Models

The SDK uses `convert_function_args` to transform incoming JSON payloads into the types specified in the skill's signature. If a `BaseModel` is used as an argument, it is automatically instantiated and validated.

```python
from pydantic import BaseModel

class ToolInput(BaseModel):
    query: str
    limit: int = 10

@app.skill()
def search_tool(params: ToolInput):
    # 'params' is a validated ToolInput instance here
    return {"results": []}
```

If validation fails, the SDK raises a `ValidationError` which is caught and returned as a 422 error by the `AgentFieldHandler`.

Sources: [sdk/python/agentfield/pydantic_utils.py:1-40](), [sdk/python/agentfield/agent.py:1510-1540]()

---

## Verifiable Credentials for Skills

Skills can participate in the VC system for cryptographic audit trails. When `vc_enabled` is true, the `Agent` uses the `VCGenerator` to sign the execution.

```python
@app.skill(vc_enabled=True)
def secure_operation(data: str):
    return {"status": "signed"}
```

The system generates an `ExecutionVC` containing:
1. **Subject**: The Agent's DID.
2. **Input Hash**: Deterministic hash of arguments.
3. **Output Hash**: Deterministic hash of the result.
4. **Context**: Workflow and Execution IDs.

Sources: [sdk/python/agentfield/vc_generator.py:82-161](), [sdk/python/agentfield/did_manager.py:87-145]()

---

## Skills in AgentRouter

`AgentRouter` allows for modular organization. Skills defined on a router are merged into the main `Agent` when `include_router()` is called.

```python
router = AgentRouter(prefix="tools", tags=["utility"])

@router.skill()
def echo(val: str):
    return val

app.include_router(router)
# Accessible externally as 'tools.echo'
```

The router automatically propagates tags and sanitizes prefixes to ensure consistent routing in the Control Plane.

Sources: [sdk/python/agentfield/router.py:88-116](), [sdk/python/agentfield/router.py:165-200]()

---

## Error Handling in Skills

When a skill raises an exception, the `Agent` catches it and wraps it in an `ExecuteError`.

- **Standard Exceptions**: (e.g., `ValueError`) are returned as failed executions.
- **`ReasonerFailed`**: Though primarily for reasoners, if raised in a skill, it allows preserving a partial `result` alongside the failure status.

Sources: [sdk/python/agentfield/agent.py:716-735](), [sdk/python/agentfield/exceptions.py:36-73]()

---

## Summary

Skills provide the deterministic backbone of an AgentField node.

- **Efficiency**: Uses `__slots__` and lazy schema generation.
- **Flexibility**: Supports sync/async, Pydantic models, and custom metadata.
- **Integration**: Deeply integrated with the `MemoryInterface` and `VCGenerator`.
- **Organization**: Can be namespaced using `AgentRouter`.

Sources: [sdk/python/agentfield/agent.py:135-144](), [sdk/python/agentfield/agent.py:444-451](), [sdk/python/agentfield/router.py:88-116]()

---

# Page: AgentRouter

# AgentRouter

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [sdk/python/agentfield/decorator_metadata.py](sdk/python/agentfield/decorator_metadata.py)
- [sdk/python/agentfield/decorators.py](sdk/python/agentfield/decorators.py)
- [sdk/python/agentfield/router.py](sdk/python/agentfield/router.py)
- [sdk/python/tests/test_accepts_webhook.py](sdk/python/tests/test_accepts_webhook.py)
- [sdk/python/tests/test_decorator_code_origin.py](sdk/python/tests/test_decorator_code_origin.py)
- [sdk/python/tests/test_router.py](sdk/python/tests/test_router.py)
- [sdk/python/tests/test_trigger_param_binding.py](sdk/python/tests/test_trigger_param_binding.py)
- [sdk/python/tests/test_workflow_parent_child.py](sdk/python/tests/test_workflow_parent_child.py)

</details>



## Purpose and Scope

The `AgentRouter` class provides a modular approach to organizing agent capabilities (reasoners and skills) by grouping them under common prefixes. It enables code organization through separation of concerns, allowing developers to split large agent implementations into logical submodules while maintaining a unified agent interface.

For information about defining reasoners, see [3.2 Defining Reasoners](). For information about defining skills, see [3.3 Defining Skills](). For the TypeScript equivalent, see [4.6 AgentRouter (TypeScript)]().

---

## Core Concepts

### Router as Capability Organizer

An `AgentRouter` functions similarly to FastAPI's `APIRouter` but is specifically designed for organizing agent capabilities:

- **Prefix Scoping**: All reasoners and skills registered on a router inherit a common prefix [sdk/python/agentfield/router.py:21]().
- **Modular Organization**: Split agent logic into focused routers (e.g., `data_router`, `analysis_router`).
- **Automatic Delegation**: Routers transparently proxy all `Agent` methods (like `ai()`, `call()`, `memory`, `note()`, `discover()`) to the attached agent instance [sdk/python/agentfield/router.py:119-151]().
- **Tag Propagation**: Tags applied to routers propagate and merge with tags on individual reasoners and skills [sdk/python/agentfield/router.py:51](), [sdk/python/agentfield/router.py:100]().
- **Workflow Tracking**: Router reasoners are wrapped to ensure that direct internal calls between reasoners are properly instrumented for workflow tracking [sdk/python/agentfield/router.py:54-60]().

**Sources:** [sdk/python/agentfield/router.py:17-27](), [sdk/python/agentfield/router.py:119-151]()

---

## Architecture Overview

### Router-Agent Relationship

The diagram below shows how an `Agent` acts as the root container while `AgentRouter` instances provide namespace isolation for logic.

```mermaid
graph TB
    subgraph "Agent Entity Space"
        Agent["Agent (node_id='research_agent')"]
        Router1["AgentRouter (prefix='web')"]
        Router2["AgentRouter (prefix='analysis')"]
    end

    subgraph "Code Entity Space"
        R1["@router1.reasoner() search()"]
        S1["@router1.skill() fetch()"]
        R2["@router2.reasoner() summarize()"]
    end
    
    Agent -- "include_router()" --> Router1
    Agent -- "include_router()" --> Router2
    
    Router1 -- "registers" --> R1
    Router1 -- "registers" --> S1
    Router2 -- "registers" --> R2
    
    R1 -- "router1.ai()" --> Agent
    R1 -- "router1.call('analysis.summarize')" --> Agent
```

**Sources:** [sdk/python/agentfield/router.py:17-27](), [sdk/python/agentfield/router.py:119-151]()

---

## Creating and Attaching Routers

### Basic Router Creation

```python
from agentfield import Agent, AgentRouter

app = Agent(node_id="research_agent")

# Create routers for different capability domains
web_router = AgentRouter(prefix="web", tags=["v1"])
analysis_router = AgentRouter(prefix="analysis")

# Attach routers to the agent
app.include_router(web_router)
app.include_router(analysis_router)
```

### Prefix and Path Resolution

The router normalizes paths by combining the router's `prefix` with the capability's `path`. If a capability path starts with `/`, it is treated as an absolute path and overrides the router prefix [sdk/python/agentfield/router.py:173-174]().

| Router Prefix | Capability Path | Resulting API Path |
|--------------|-----------------|--------------------|
| `"web"`      | `"search"`      | `/web/search`      |
| `"/web"`     | `None`          | `/web`             |
| `"group"`    | `"/reasoners/f"`| `/reasoners/f`     |
| `"group"`    | `"reasoners/f"` | `/reasoners/group/f`|

**Sources:** [sdk/python/agentfield/router.py:165-201](), [sdk/python/tests/test_router.py:95-108]()

---

## Defining Capabilities on Routers

### Reasoners on Routers

Reasoners on a router benefit from automatic workflow instrumentation. When one router reasoner calls another, the call is intercepted and routed through the agent's workflow handler [sdk/python/agentfield/router.py:57-60]().

```python
web_router = AgentRouter(prefix="web")

@web_router.reasoner(path="search")
async def search_webpage(query: str) -> dict:
    # Delegates to app.ai() via __getattr__
    result = await web_router.ai(prompt=f"Search: {query}")
    return {"result": result}

app.include_router(web_router)
```

### Skills on Routers

Skills are registered similarly but do not include the workflow wrapper, as they are intended to be deterministic atomic operations [sdk/python/agentfield/router.py:87-115]().

```python
@web_router.skill(tags=["network"])
def fetch_html(url: str) -> str:
    import requests
    return requests.get(url).text
```

**Sources:** [sdk/python/agentfield/router.py:30-85](), [sdk/python/agentfield/router.py:87-115]()

---

## Delegation to Parent Agent

### Method Proxying via `__getattr__`

The `AgentRouter` uses Python's `__getattr__` to proxy calls to the underlying `Agent` instance. This allows code inside a router to access all agent features without needing a direct reference to the `app` object [sdk/python/agentfield/router.py:119-151]().

```mermaid
sequenceDiagram
    participant R as AgentRouter
    participant A as Agent
    participant M as MemoryInterface

    Note over R: Call router.memory.set()
    R->>A: __getattr__('memory')
    A-->>R: Returns MemoryInterface
    R->>M: set(key, val)
```

| Router Proxy Call | Resulting Agent Operation |
|-------------------|---------------------------|
| `router.ai(...)`  | `agent.ai(...)`           |
| `router.call(...)`| `agent.call(...)`          |
| `router.memory`   | `agent.memory`            |
| `router.note(...)`| `agent.note(...)`          |

### Attachment Requirements

Accessing any delegated property before the router is attached to an agent via `app.include_router(router)` will raise an `AgentFieldClientError` [sdk/python/agentfield/router.py:141-144]().

**Sources:** [sdk/python/agentfield/router.py:119-151](), [sdk/python/tests/test_router.py:33-50]()

---

## Tag Propagation

Tags defined at the router level are prepended to tags defined at the function level.

```python
router = AgentRouter(tags=["base"])

@router.skill(tags=["extra"])
def my_skill():
    pass

# Resulting tags: ["base", "extra"]
```

**Sources:** [sdk/python/agentfield/router.py:51](), [sdk/python/agentfield/router.py:100](), [sdk/python/tests/test_router.py:52-74]()

---

## Workflow Tracking and Direct Calls

One of the primary technical advantages of `AgentRouter` is how it handles direct function calls. When a reasoner is defined on a router, the decorator returns a `wrapper`. This wrapper checks if the router has been attached to an agent and if the function is "tracked" [sdk/python/agentfield/router.py:54-60]().

If `router_a.reasoner_1` calls `router_a.reasoner_2()` directly:
1. The call hits the wrapper of `reasoner_2`.
2. The wrapper looks up the "tracked" version of the function in `_tracked_functions`.
3. It executes the tracked version, which ensures the call appears as a child node in the Control Plane workflow DAG [sdk/python/tests/test_workflow_parent_child.py:58-80]().

**Sources:** [sdk/python/agentfield/router.py:54-64](), [sdk/python/tests/test_workflow_parent_child.py:58-80]()

---

## Sources:
- [sdk/python/agentfield/router.py:1-201]()
- [sdk/python/tests/test_router.py:1-150]()
- [sdk/python/agentfield/decorators.py:125-170]()
- [sdk/python/tests/test_workflow_parent_child.py:58-109]()

---

# Page: Client & Communication

# Client & Communication

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [control-plane/internal/handlers/execute_awaiter_status.go](control-plane/internal/handlers/execute_awaiter_status.go)
- [control-plane/internal/handlers/execute_awaiter_status_test.go](control-plane/internal/handlers/execute_awaiter_status_test.go)
- [sdk/python/agentfield/agent.py](sdk/python/agentfield/agent.py)
- [sdk/python/agentfield/agent_field_handler.py](sdk/python/agentfield/agent_field_handler.py)
- [sdk/python/agentfield/async_execution_manager.py](sdk/python/agentfield/async_execution_manager.py)
- [sdk/python/agentfield/client.py](sdk/python/agentfield/client.py)
- [sdk/python/agentfield/connection_manager.py](sdk/python/agentfield/connection_manager.py)
- [sdk/python/agentfield/did_manager.py](sdk/python/agentfield/did_manager.py)
- [sdk/python/agentfield/exceptions.py](sdk/python/agentfield/exceptions.py)
- [sdk/python/agentfield/execution_state.py](sdk/python/agentfield/execution_state.py)
- [sdk/python/agentfield/vc_generator.py](sdk/python/agentfield/vc_generator.py)
- [sdk/python/tests/helpers.py](sdk/python/tests/helpers.py)
- [sdk/python/tests/test_agent_call.py](sdk/python/tests/test_agent_call.py)
- [sdk/python/tests/test_agent_coverage_additions.py](sdk/python/tests/test_agent_coverage_additions.py)
- [sdk/python/tests/test_agent_networking.py](sdk/python/tests/test_agent_networking.py)
- [sdk/python/tests/test_async_config.py](sdk/python/tests/test_async_config.py)
- [sdk/python/tests/test_async_execution.py](sdk/python/tests/test_async_execution.py)
- [sdk/python/tests/test_client.py](sdk/python/tests/test_client.py)
- [sdk/python/tests/test_client_laser_push.py](sdk/python/tests/test_client_laser_push.py)
- [sdk/python/tests/test_client_lifecycle.py](sdk/python/tests/test_client_lifecycle.py)
- [sdk/python/tests/test_connection_manager.py](sdk/python/tests/test_connection_manager.py)
- [sdk/python/tests/test_execution_state.py](sdk/python/tests/test_execution_state.py)
- [sdk/python/tests/test_vc_generator.py](sdk/python/tests/test_vc_generator.py)

</details>



This page documents the `AgentFieldClient` class, which provides the communication layer between Python SDK agents and the AgentField control plane. The client handles HTTP/WebSocket communication, authentication, agent registration, execution coordination, and service discovery.

---

## Overview

The `AgentFieldClient` is initialized automatically when you create an `Agent` instance. It manages all communication with the control plane, including agent node registration, execution routing, and service discovery.

**Architecture Diagram:**

```mermaid
graph TB
    Agent["Agent Instance<br/>(agent.py)"]
    Client["AgentFieldClient<br/>(client.py)"]
    CP["Control Plane<br/>localhost:8080"]
    
    Agent -->|"self.client"| Client
    
    Client -->|"register_agent()"| CP
    Client -->|"execute() / execute_async()"| CP
    Client -->|"discover_capabilities()"| CP
    Client -->|"send_enhanced_heartbeat()"| CP
    
    Client -.->|"X-API-Key header"| CP
    
    subgraph "Internal Components"
        AsyncMgr["AsyncExecutionManager"]
        ResultCache["ResultCache"]
        HttpClient["httpx.AsyncClient"]
    end
    
    Client --> AsyncMgr
    Client --> ResultCache
    Client --> HttpClient
```

**Sources:** [sdk/python/agentfield/client.py:142-175](), [sdk/python/agentfield/agent.py:479-482]()

---

## Client Initialization

The `AgentFieldClient` is typically initialized through the `Agent` constructor but can be used standalone for control-plane interactions.

**Configuration Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `base_url` | `str` | `"http://localhost:8080"` | Control plane URL |
| `api_key` | `Optional[str]` | `None` | Authentication key for `X-API-Key` header |
| `async_config` | `Optional[AsyncConfig]` | `None` | Async execution configuration (polling intervals, timeouts) |
| `did` | `Optional[str]` | `None` | Decentralized Identifier for DID-auth |
| `private_key_jwk` | `Optional[str]` | `None` | JWK for signing DID-auth requests |

**Sources:** [sdk/python/agentfield/client.py:147-154](), [sdk/python/agentfield/agent.py:479-482]()

---

## Authentication

The client supports two primary authentication modes:
1.  **API Key:** Uses the `X-API-Key` header for control plane access.
2.  **DID Auth:** Uses `DIDAuthenticator` to sign requests for agent-to-agent calls, ensuring cryptographic identity verification.

**Authentication Flow:**

```mermaid
sequenceDiagram
    participant Agent as "Agent (agent.py)"
    participant Client as "AgentFieldClient (client.py)"
    participant CP as "Control Plane"
    
    Note over Agent,CP: Initialization
    Agent->>Client: AgentFieldClient(api_key="secret", did="did:af:...")
    
    Note over Agent,CP: Request with DID-Auth
    Agent->>Client: execute("other.reasoner", {...})
    Client->>Client: _did_authenticator.sign_request()
    Client->>CP: POST /api/v1/execute/async/other.reasoner<br/>Headers: Authorization: Bearer <JWT>, X-API-Key: secret
    CP-->>Client: 202 Accepted
```

**Sources:** [sdk/python/agentfield/client.py:159-161](), [sdk/python/agentfield/client.py:218-220]()

---

## Agent Registration

Registration establishes the agent's identity and capabilities (reasoners/skills) with the control plane.

### Registration Method

The `register_agent` method transmits metadata, capability schemas, and deployment info.

```python
async def register_agent(
    self,
    node_id: str,
    reasoners: List[dict],
    skills: List[dict],
    base_url: str,
    discovery: Optional[Dict[str, Any]] = None,
    vc_metadata: Optional[Dict[str, Any]] = None,
    version: str = "1.0.0",
    agent_metadata: Optional[Dict[str, Any]] = None,
    tags: Optional[List[str]] = None,
    instance_id: Optional[str] = None,
) -> Tuple[bool, Optional[Dict[str, Any]]]:
```

**Sources:** [sdk/python/agentfield/client.py:500-512](), [sdk/python/agentfield/agent_field_handler.py:125-136]()

---

## Execution Methods

AgentField supports both asynchronous (polling-based) and synchronous execution.

### Execution Architecture

The `AgentFieldClient` uses an `AsyncExecutionManager` to handle high-concurrency polling with adaptive backoff.

```mermaid
sequenceDiagram
    participant Caller as "Agent Node"
    participant Client as "AgentFieldClient"
    participant AsyncMgr["AsyncExecutionManager"]
    participant CP as "Control Plane"
    
    Caller->>Client: execute("target.task", input)
    Client->>AsyncMgr: submit_execution(target, input)
    AsyncMgr->>CP: POST /api/v1/execute/async/target.task
    CP-->>AsyncMgr: 202 {execution_id: "exec-123"}
    
    loop Adaptive Polling
        AsyncMgr->>CP: GET /api/v1/executions/exec-123
        CP-->>AsyncMgr: {status: "running"}
        AsyncMgr->>AsyncMgr: sleep(backoff)
    end
    
    CP-->>AsyncMgr: {status: "succeeded", result: {...}}
    AsyncMgr-->>Client: result
    Client-->>Caller: result
```

### Async Execution (execute)

The `execute` method submits a task and waits for the result using the `AsyncExecutionManager`. It intelligently handles timeouts and retries.

**Sources:** [sdk/python/agentfield/client.py:574-620](), [sdk/python/agentfield/async_execution_manager.py:185-207]()

### Execution Error Handling

Specific exceptions distinguish between transport failures and logic failures:
-   `ExecutionFailedError`: The remote reasoner ran and explicitly returned a failed status.
-   `ExecutionTimeoutError`: The wait deadline was hit.
-   `ExecutionCancelledError`: Explicit user intent to stop the work.

**Sources:** [sdk/python/agentfield/exceptions.py:17-33](), [sdk/python/agentfield/exceptions.py:80-96]()

---

## Service Discovery

Discovery allows agents to find other agents, reasoners, or skills by ID, tags, or health status.

### Discovery Patterns

```mermaid
graph TB
    Query["Discovery Query"]
    
    Query --> ByAgent["Filter by Agent<br/>agent='researcher'"]
    Query --> ByCapability["Filter by Capability<br/>reasoner='summarize'"]
    Query --> ByTags["Filter by Tags<br/>tags=['nlp', 'production']"]
    
    ByAgent --> Result["DiscoveryResult"]
    ByCapability --> Result
    ByTags --> Result
    
    Result --> Format1["JSON Format<br/>(Full details)"]
    Result --> Format2["Compact Format<br/>(IDs only)"]
```

**Sources:** [sdk/python/agentfield/client.py:201-220]()

---

## Heartbeat & Lifecycle

Agents maintain their "Online" status via heartbeats and notify the control plane during shutdown.

### Enhanced Heartbeat

The `AgentFieldHandler` collects MCP server health and agent status to send an "enhanced" heartbeat.

```python
async def send_enhanced_heartbeat(
    self, node_id: str, heartbeat: HeartbeatData
) -> bool:
```

### Connection Management

The `ConnectionManager` handles resilient connectivity, including:
-   **Automatic Reconnection:** Retries registration if the control plane is down.
-   **Degraded Mode:** Allows agents to run locally without a control plane if configured.
-   **Health Checks:** Monitors the link to the control plane.

**Sources:** [sdk/python/agentfield/connection_manager.py:36-62](), [sdk/python/agentfield/agent_field_handler.py:170-185]()

---

## Context Propagation

The client automatically propagates execution context through HTTP headers. This ensures that `run_id`, `workflow_id`, and `session_id` are preserved across multi-agent calls.

**Propagation Headers:**

| Header | Purpose |
|--------|---------|
| `X-Run-ID` | Tracks the entire chain of executions |
| `X-Execution-ID` | Unique ID for the current execution step |
| `X-Workflow-ID` | Associates executions with a specific workflow instance |
| `X-Session-ID` | Scopes memory and state to a user session |

**Sources:** [sdk/python/agentfield/client.py:182-199](), [sdk/python/agentfield/execution_context.py:37-47]()

---

## Human-in-the-loop (Pause & Resume)

The client facilitates human-in-the-loop patterns by allowing reasoners to `pause` and wait for external approval.

### Approval Flow

1.  **Pause:** The agent calls `agent.pause()`, which registers a pause with the `_pause_manager`.
2.  **Request:** The client sends an approval request to the control plane.
3.  **Wait:** The reasoner execution thread suspends (without consuming active timeout budget).
4.  **Resume:** When a human approves via the dashboard, the control plane sends a webhook to the agent's `/approvals/resolve` endpoint, resuming the execution.

**Sources:** [sdk/python/agentfield/agent.py:1550-1600](), [sdk/python/tests/test_async_execution.py:96-115]()

---

# Page: Memory Interface

# Memory Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [sdk/python/agentfield/memory.py](sdk/python/agentfield/memory.py)
- [sdk/python/agentfield/memory_events.py](sdk/python/agentfield/memory_events.py)
- [sdk/python/tests/test_memory_scope_kwargs.py](sdk/python/tests/test_memory_scope_kwargs.py)
- [sdk/typescript/src/context/SkillContext.ts](sdk/typescript/src/context/SkillContext.ts)
- [sdk/typescript/src/memory/MemoryClient.ts](sdk/typescript/src/memory/MemoryClient.ts)
- [sdk/typescript/src/memory/MemoryEventClient.ts](sdk/typescript/src/memory/MemoryEventClient.ts)
- [sdk/typescript/src/memory/MemoryInterface.ts](sdk/typescript/src/memory/MemoryInterface.ts)
- [sdk/typescript/tests/memory_and_discovery.test.ts](sdk/typescript/tests/memory_and_discovery.test.ts)
- [sdk/typescript/tests/memory_event_client.test.ts](sdk/typescript/tests/memory_event_client.test.ts)
- [tests/functional/agents/memory_events_decorator_agent.py](tests/functional/agents/memory_events_decorator_agent.py)
- [tests/functional/tests/test_memory_events.py](tests/functional/tests/test_memory_events.py)

</details>



This page documents the Python SDK's memory interface, which provides persistent key-value storage with automatic scoping, hierarchical lookup, and real-time change notifications. The memory system enables agents to share state across distributed executions while maintaining isolation through four-tier scoping (workflow → session → actor → global).

For information about the TypeScript memory interface, see [4.5](). For the underlying control plane memory storage implementation, see [7](). For memory event subscriptions and WebSocket communication, see [7.4]().

---

## Core Concepts

The memory interface operates on a four-tier scoping hierarchy:

| Scope | Description | Typical Lifetime | Isolation Level |
|-------|-------------|------------------|-----------------|
| `workflow` | Single workflow execution | Minutes to hours | Highest - workflow-specific |
| `session` | User or conversation session | Hours to days | Session-specific |
| `actor` | Individual agent or user | Days to weeks | Actor-specific |
| `global` | Shared across all agents | Persistent | Lowest - system-wide |

**Hierarchical Lookup**: When retrieving data with `get()`, the system searches scopes in order (workflow → session → actor → global) and returns the first match found. This allows specific scopes to override more general ones. [sdk/python/agentfield/memory.py:47-56]()

**Automatic Scoping**: Memory operations automatically use the current execution context (workflow ID, session ID, actor ID) from HTTP headers propagated through the control plane. Explicit scope overrides are also supported. [sdk/python/agentfield/memory.py:150-171]()

Sources: [sdk/python/agentfield/memory.py:1-98]()

---

## Memory Interface Class

The primary developer-facing API is the `MemoryInterface` class, exposed as `app.memory` on agent instances.

```mermaid
graph TB
    subgraph "Developer API"
        AppMemory["app.memory<br/>(MemoryInterface)"]
    end
    
    subgraph "Memory Operations"
        SetOp["set(key, data)"]
        GetOp["get(key, default)"]
        DeleteOp["delete(key)"]
        ExistsOp["exists(key)"]
        VectorOps["set_vector()<br/>similarity_search()"]
    end
    
    subgraph "Scoped Access"
        SessionScope["session(session_id)<br/>→ ScopedMemoryClient"]
        ActorScope["actor(actor_id)<br/>→ ScopedMemoryClient"]
        WorkflowScope["workflow(workflow_id)<br/>→ ScopedMemoryClient"]
        GlobalScope["global_scope<br/>→ GlobalMemoryClient"]
    end
    
    subgraph "Event System"
        OnChange["@app.memory.on_change(patterns)<br/>Decorator for change notifications"]
    end
    
    AppMemory --> SetOp
    AppMemory --> GetOp
    AppMemory --> DeleteOp
    AppMemory --> ExistsOp
    AppMemory --> VectorOps
    
    AppMemory --> SessionScope
    AppMemory --> ActorScope
    AppMemory --> WorkflowScope
    AppMemory --> GlobalScope
    
    AppMemory --> OnChange
```

**Memory Interface Methods**
The `MemoryInterface` acts as a facade over the `MemoryClient`, providing a cleaner API for common operations while managing the `MemoryEventClient` for reactive programming. [sdk/python/agentfield/memory.py:571-581]()

Sources: [sdk/python/agentfield/memory.py:571-724]()

---

## Key-Value Operations

### Setting Values

```python
# Automatic scoping based on execution context
await app.memory.set("user_preference", "dark_mode")

# Explicit scope override
await app.memory.set("theme", "solarized", scope="session", scope_id="session-123")
```

The `set()` method stores JSON-serializable data with automatic scope detection based on execution context headers (`X-Workflow-ID`, `X-Session-ID`, `X-Actor-ID`). [sdk/python/agentfield/memory.py:187-205]()

**Implementation Flow**:

```mermaid
sequenceDiagram
    participant Reasoner as "Reasoner Function"
    participant MemInterface as "MemoryInterface"
    participant MemClient as "MemoryClient"
    participant HTTP as "AgentFieldClient<br/>_async_request()"
    participant API as "Control Plane API<br/>/api/v1/memory/set"
    
    Reasoner->>MemInterface: await memory.set(key, data)
    MemInterface->>MemClient: set(key, data, scope=None)
    MemClient->>MemClient: _build_headers()<br/>Extract X-Workflow-ID,<br/>X-Session-ID, X-Actor-ID
    MemClient->>HTTP: POST with headers
    HTTP->>API: {"key": "...", "data": "..."}
    API-->>HTTP: 200 OK
    HTTP-->>MemClient: Response
    MemClient-->>MemInterface: Success
    MemInterface-->>Reasoner: Complete
```

Sources: [sdk/python/agentfield/memory.py:132-171](), [sdk/python/agentfield/memory.py:187-228]()

### Getting Values

```python
# Hierarchical lookup across all scopes
value = await app.memory.get("user_preference", default="light_mode")

# Scope-specific lookup via scoped client
value = await app.memory.session("session-123").get("theme")
```

The `get()` method performs hierarchical lookup when no explicit scope is provided. The control plane searches workflow → session → actor → global and returns the first match. [sdk/python/agentfield/memory.py:47-56]()

**Hierarchical Lookup Diagram**:

```mermaid
graph TB
    GetRequest["get(key='user_preference')"]
    
    WorkflowCheck["Check workflow scope<br/>X-Workflow-ID from headers"]
    SessionCheck["Check session scope<br/>X-Session-ID from headers"]
    ActorCheck["Check actor scope<br/>X-Actor-ID from headers"]
    GlobalCheck["Check global scope"]
    
    ReturnValue["Return found value"]
    ReturnDefault["Return default"]
    
    GetRequest --> WorkflowCheck
    WorkflowCheck -->|Found| ReturnValue
    WorkflowCheck -->|Not Found| SessionCheck
    SessionCheck -->|Found| ReturnValue
    SessionCheck -->|Not Found| ActorCheck
    ActorCheck -->|Found| ReturnValue
    ActorCheck -->|Not Found| GlobalCheck
    GlobalCheck -->|Found| ReturnValue
    GlobalCheck -->|Not Found| ReturnDefault
```

Sources: [sdk/python/agentfield/memory.py:230-279](), [sdk/python/agentfield/memory.py:607-621]()

### Other Operations

| Method | Purpose | Returns |
|--------|---------|---------|
| `exists(key)` | Check if key exists in any scope | `bool` |
| `delete(key)` | Remove key from current scope | `None` |
| `list_keys(scope)` | List all keys in a specific scope | `List[str]` |

The `exists()` method [sdk/python/agentfield/memory.py:281-298]() attempts to retrieve the value and returns `True` if found, `False` otherwise.

The `delete()` method [sdk/python/agentfield/memory.py:300-324]() removes the key from the scope determined by execution context headers.

Sources: [sdk/python/agentfield/memory.py:281-355](), [sdk/python/agentfield/memory.py:624-642]()

---

## Vector Storage

The memory interface supports storing vector embeddings for similarity search operations, enabling RAG (Retrieval-Augmented Generation) applications.

### Storing Vectors

```python
# Store an embedding with metadata
embedding = [0.1, 0.2, 0.3, ...] 
await app.memory.set_vector(
    key="doc:readme",
    embedding=embedding,
    metadata={"title": "README", "type": "documentation"}
)
```

The `set_vector()` method [sdk/python/agentfield/memory.py:357-385]() accepts:
- `key`: Unique identifier for the vector
- `embedding`: Sequence of floats (list, tuple, or numpy array)
- `metadata`: Optional dict with filterable attributes

**Vector Normalization**: The `_vector_to_list()` helper [sdk/python/agentfield/memory.py:123-130]() converts numpy arrays and other sequence types to plain Python lists.

### Similarity Search

```python
# Search for similar vectors
query_embedding = [0.15, 0.22, 0.31, ...]
results = await app.memory.similarity_search(
    query_embedding=query_embedding,
    top_k=5,
    filters={"type": "documentation"}
)
```

The `similarity_search()` method [sdk/python/agentfield/memory.py:410-441]() performs cosine similarity search against stored vectors, returning the top-k most similar entries with their metadata and similarity scores.

Sources: [sdk/python/agentfield/memory.py:357-441](), [sdk/python/agentfield/memory.py:596-661]()

---

## Memory Events

The memory interface provides reactive event subscriptions using the `@memory.on_change()` decorator, enabling agents to respond to memory changes in real-time.

### Pattern Matching

Subscriptions support wildcard patterns for granular event filtering. [sdk/python/agentfield/memory_events.py:18-42]()

**Pattern Matching Examples**:

- **Exact Match**: `preferences.theme`
- **Wildcard Match**: `preferences.*` [tests/functional/agents/memory_events_decorator_agent.py:144]()
- **Nested Wildcard**: `settings.*.primary` [tests/functional/agents/memory_events_decorator_agent.py:148]()
- **Multi-Wildcard**: `features.*.flag.*` [tests/functional/agents/memory_events_decorator_agent.py:152]()

Sources: [sdk/python/agentfield/memory_events.py:18-82](), [tests/functional/agents/memory_events_decorator_agent.py:140-166]()

### Event Object Structure

Memory events provide comprehensive change information via the `MemoryChangeEvent` type. [sdk/python/agentfield/types.py:11]() (Note: Reference to types.py inferred from usage in memory_events.py).

| Property | Description |
|----------|-------------|
| `key` | Memory key that changed |
| `data` | New value (for set operations) |
| `action` | Operation type (set/delete) |
| `scope` | Memory scope (workflow/session/actor/global) |
| `scope_id` | Scope identifier (workflow ID, session ID, etc.) |
| `timestamp` | ISO 8601 timestamp |

Sources: [sdk/python/agentfield/memory_events.py:44-82](), [tests/functional/tests/test_memory_events.py:50-56]()

---

## Scoped Memory Clients

Factory methods return specialized clients that pin operations to a specific scope.

### Scope Accessors

| Method | Client Type | Description |
|--------|-------------|-------------|
| `app.memory.session(id)` | `ScopedMemoryClient` | Scoped to a specific conversation session. [sdk/python/agentfield/memory.py:675-687]() |
| `app.memory.actor(id)` | `ScopedMemoryClient` | Scoped to a specific actor across sessions. [sdk/python/agentfield/memory.py:689-699]() |
| `app.memory.workflow(id)` | `ScopedMemoryClient` | Scoped to a single execution run. [sdk/python/agentfield/memory.py:701-713]() |
| `app.memory.global_scope` | `GlobalMemoryClient` | Shared across all agents and sessions. [sdk/python/agentfield/memory.py:715-724]() |

### Scoped Event Subscriptions

Scoped clients provide an `on_change()` decorator that automatically filters for the client's scope and ID. [sdk/python/agentfield/memory.py:450-463]()

```python
session_memory = app.memory.session("session-123")

@session_memory.on_change("preferences.*")
async def handle_session_preference(event):
    # Only receives events for session-123
    pass
```

Sources: [sdk/python/agentfield/memory.py:357-569](), [sdk/python/agentfield/memory.py:675-724]()

---

## Context Propagation

Memory operations automatically extract execution context from HTTP headers to determine scoping.

```mermaid
sequenceDiagram
    participant CP as "Control Plane"
    participant Agent as "Agent HTTP Handler"
    participant Context as "ExecutionContext"
    participant MemClient as "MemoryClient"
    participant API as "Control Plane<br/>Memory API"
    
    CP->>Agent: POST /execute<br/>X-Workflow-ID: wf-123<br/>X-Session-ID: sess-456
    Agent->>Context: Extract headers
    Agent->>MemClient: Initialize with context
    
    MemClient->>MemClient: _build_headers()
    MemClient->>API: POST /api/v1/memory/set<br/>X-Workflow-ID: wf-123<br/>X-Session-ID: sess-456
    API-->>MemClient: 200 OK
```

### Header Mapping

The `_build_headers()` method [sdk/python/agentfield/memory.py:150-171]() converts execution context to HTTP headers:

| Context Property | HTTP Header |
|------------------|-------------|
| `workflow_id` | `X-Workflow-ID` |
| `session_id` | `X-Session-ID` |
| `actor_id` | `X-Actor-ID` |
| `agent_node_id` | `X-Agent-Node-ID` |

Sources: [sdk/python/agentfield/memory.py:150-171](), [sdk/python/agentfield/memory.py:55-75]() (Note: logic exists in both MemoryClient and base classes).

---

# Page: DID & Verifiable Credentials

# DID & Verifiable Credentials

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [sdk/python/agentfield/agent_discovery.py](sdk/python/agentfield/agent_discovery.py)
- [sdk/python/agentfield/agent_field_handler.py](sdk/python/agentfield/agent_field_handler.py)
- [sdk/python/agentfield/agent_pause.py](sdk/python/agentfield/agent_pause.py)
- [sdk/python/agentfield/agent_schema.py](sdk/python/agentfield/agent_schema.py)
- [sdk/python/agentfield/agent_serverless.py](sdk/python/agentfield/agent_serverless.py)
- [sdk/python/agentfield/agent_vc.py](sdk/python/agentfield/agent_vc.py)
- [sdk/python/agentfield/connection_manager.py](sdk/python/agentfield/connection_manager.py)
- [sdk/python/agentfield/did_manager.py](sdk/python/agentfield/did_manager.py)
- [sdk/python/agentfield/vc_generator.py](sdk/python/agentfield/vc_generator.py)
- [sdk/python/tests/helpers.py](sdk/python/tests/helpers.py)
- [sdk/python/tests/test_agent_networking.py](sdk/python/tests/test_agent_networking.py)
- [sdk/python/tests/test_client.py](sdk/python/tests/test_client.py)
- [sdk/python/tests/test_client_lifecycle.py](sdk/python/tests/test_client_lifecycle.py)
- [sdk/python/tests/test_connection_manager.py](sdk/python/tests/test_connection_manager.py)
- [sdk/python/tests/test_vc_generator.py](sdk/python/tests/test_vc_generator.py)

</details>



## Purpose and Scope

This document describes the Decentralized Identifier (DID) and Verifiable Credentials (VC) system in the AgentField Python SDK. It covers how agents register cryptographic identities, generate verifiable credentials for executions, and use them for audit trails and policy enforcement.

For information about agent initialization and basic configuration, see [Agent Class](3.1). For memory system integration, see [Memory Interface](3.6). For control plane DID/VC infrastructure, see [Identity & Trust](8).

---

## Overview

The AgentField DID/VC system provides cryptographic identity and execution attestation for agents, reasoners, and skills. It implements W3C standards for DIDs and Verifiable Credentials to create an immutable audit trail of all agent operations.

### Key Components

| Component | Purpose | Location |
|-----------|---------|----------|
| `DIDManager` | Manages DID registration and resolution | [sdk/python/agentfield/did_manager.py:59-68]() |
| `VCGenerator` | Creates and verifies verifiable credentials | [sdk/python/agentfield/vc_generator.py:53-62]() |
| `DIDIdentity` | Represents a DID with cryptographic keys | [sdk/python/agentfield/did_manager.py:18-27]() |
| `DIDIdentityPackage` | Complete identity package for an agent | [sdk/python/agentfield/did_manager.py:31-37]() |
| `ExecutionVC` | Verifiable credential for a single execution | [sdk/python/agentfield/vc_generator.py:19-36]() |
| `WorkflowVC` | Aggregated VC for an entire workflow | [sdk/python/agentfield/vc_generator.py:38-50]() |

Sources: [sdk/python/agentfield/did_manager.py:1-68](), [sdk/python/agentfield/vc_generator.py:1-62]()

---

## DID System Architecture

### Hierarchical DID Derivation

```mermaid
graph TB
    ServerDID["AgentField Server DID<br/>Root Identity"]
    
    AgentDID1["Agent DID<br/>researcher<br/>derivation_index: 1"]
    AgentDID2["Agent DID<br/>analyst<br/>derivation_index: 2"]
    
    ReasonerDID1["Component DID<br/>summarize reasoner<br/>derivation_index: 1"]
    SkillDID1["Component DID<br/>fetch_url skill<br/>derivation_index: 2"]
    
    ReasonerDID2["Component DID<br/>evaluate reasoner<br/>derivation_index: 1"]
    
    ServerDID --> AgentDID1
    ServerDID --> AgentDID2
    AgentDID1 --> ReasonerDID1
    AgentDID1 --> SkillDID1
    AgentDID2 --> ReasonerDID2
```

**Figure 1: Hierarchical DID Structure**

Each agent receives a complete identity package containing:
- **Agent DID**: Root identity for the agent node [sdk/python/agentfield/did_manager.py:34]()
- **Reasoner DIDs**: One DID per reasoner function [sdk/python/agentfield/did_manager.py:35]()
- **Skill DIDs**: One DID per skill function [sdk/python/agentfield/did_manager.py:36]()

Sources: [sdk/python/agentfield/did_manager.py:31-37]()

### DID Identity Structure

The `DIDIdentity` dataclass represents a single DID with its cryptographic materials:

| Field | Type | Description |
|-------|------|-------------|
| `did` | `str` | W3C-compliant DID string |
| `private_key_jwk` | `str` | Private key in JWK format |
| `public_key_jwk` | `str` | Public key in JWK format |
| `derivation_path` | `str` | Hierarchical derivation path |
| `component_type` | `str` | Type: "agent", "reasoner", or "skill" |
| `function_name` | `Optional[str]` | Name of the reasoner or skill |

Sources: [sdk/python/agentfield/did_manager.py:18-27]()

---

## DIDManager Usage

### Initialization

The `DIDManager` and `VCGenerator` are initialized via the `_AgentVCMixin` when an agent is created:

```python
# Initialization logic in _AgentVCMixin
self.did_manager = DIDManager(self.agentfield_server, self.node_id, self.api_key)
self.vc_generator = VCGenerator(self.agentfield_server, self.api_key)
```

Sources: [sdk/python/agentfield/agent_vc.py:10-28]()

### Agent Registration Flow

```mermaid
sequenceDiagram
    participant Agent as "Agent Instance"
    participant DIDMgr as "DIDManager"
    participant Server as "AgentField Server<br/>/api/v1/did/register"
    
    Agent->>DIDMgr: "register_agent(reasoners, skills)"
    DIDMgr->>Server: "POST /api/v1/did/register"
    Server-->>DIDMgr: "identity_package"
    DIDMgr->>DIDMgr: "_parse_identity_package()"
    DIDMgr-->>Agent: "success=True"
    
    Note over Agent: "self.did_enabled = True"
```

**Figure 2: DID Registration Sequence**

Sources: [sdk/python/agentfield/did_manager.py:93-145](), [sdk/python/agentfield/agent_field_handler.py:158-167]()

### Registration Method

```python
def register_agent(
    self, 
    reasoners: List[Dict[str, Any]], 
    skills: List[Dict[str, Any]]
) -> bool:
    """
    Register agent with AgentField Server and obtain DID identity package.
    """
```

The `register_agent` method prepares a payload containing the agent node ID and its components, sends it to the control plane, and populates the `identity_package` upon success. [sdk/python/agentfield/did_manager.py:93-147]()

Sources: [sdk/python/agentfield/did_manager.py:93-151]()

### Creating Execution Context

The `DIDExecutionContext` is a critical structure for tracking identity across the execution lifecycle. It includes a `parent_vc_id` field to enable VC chaining for trigger-driven runs. [sdk/python/did_manager.py:41-56]()

```python
did_context = app.did_manager.create_execution_context(
    execution_id="exec-123",
    workflow_id="wf-456",
    session_id="session-789",
    caller_function="summarize",
    target_function="fetch_url",
    parent_vc_id="vc-trigger-001"
)
```

Sources: [sdk/python/agentfield/did_manager.py:41-56](), [sdk/python/agentfield/did_manager.py:153-204]()

---

## Verifiable Credentials

### Execution VC Structure

```mermaid
graph LR
    ExecVC["ExecutionVC"]
    
    ExecVC --> VCID["vc_id: Unique identifier"]
    ExecVC --> ExecID["execution_id: Execution reference"]
    ExecVC --> WorkflowID["workflow_id: Workflow reference"]
    ExecVC --> IssuerDID["issuer_did: Component DID"]
    ExecVC --> TargetDID["target_did: Target component DID"]
    ExecVC --> CallerDID["caller_did: Calling component DID"]
    ExecVC --> InputHash["input_hash: SHA-256 of input"]
    ExecVC --> OutputHash["output_hash: SHA-256 of output"]
    ExecVC --> Sig["signature: Cryptographic proof"]
```

**Figure 3: ExecutionVC Structure**

Sources: [sdk/python/agentfield/vc_generator.py:19-36]()

### VC Metadata Generation

The agent produces a serializable VC policy snapshot for control-plane visibility using `_build_vc_metadata()`. This includes the global default and specific overrides for reasoners and skills. [sdk/python/agentfield/agent_vc.py:93-116]()

---

## VCGenerator Usage

### Generating Execution VCs

The `generate_execution_vc` method sends execution metadata, including hashed input/output data and duration, to the AgentField server to receive a signed credential. [sdk/python/agentfield/vc_generator.py:86-161]()

```python
# Internal async generation logic
async def _generate_vc_async(
    self,
    vc_generator,
    did_execution_context,
    function_name,
    input_data,
    output_data,
    status="success",
    duration_ms=0,
):
    # Calls vc_generator.generate_execution_vc internally
```

Sources: [sdk/python/agentfield/agent_vc.py:118-155](), [sdk/python/agentfield/vc_generator.py:86-161]()

### Workflow VC Chain

The system can retrieve a complete chain of credentials for a workflow, allowing for full auditability of every step taken by the agent. [sdk/python/agentfield/vc_generator.py:201-224]()

```python
chain = vc_generator.get_workflow_vc_chain(workflow_id="wf-123")
```

Sources: [sdk/python/agentfield/vc_generator.py:201-224]()

---

## Agent Integration

### VC Policy Resolution

The SDK uses a hierarchical resolution for VC settings:
1. **Component Override**: Specific `vc_enabled` setting on `@app.reasoner()` or `@app.skill()`. [sdk/python/agentfield/agent_vc.py:64-69]()
2. **Agent Default**: The `vc_enabled` value passed to the `Agent` constructor. [sdk/python/agentfield/agent_vc.py:46-48]()

### Registration with Status

The `ConnectionManager` utilizes `register_agent_with_status` to ensure the agent is correctly identified by the control plane, passing VC metadata during the registration heartbeat. [sdk/python/agentfield/connection_manager.py:136-149]()

```mermaid
graph TD
    CM["ConnectionManager"]
    Client["AgentFieldClient"]
    CP["Control Plane"]
    
    CM -->|register_agent_with_status| Client
    Client -->|POST /api/v1/nodes/register| CP
    CP -->|identity_package| Client
    Client --> CM
```

**Figure 4: Registration Data Flow**

Sources: [sdk/python/agentfield/connection_manager.py:106-172](), [sdk/python/agentfield/agent_vc.py:93-116]()

---

## Testing Utilities

The SDK includes comprehensive tests for identity management:
- **VC Generation**: Tests in `test_vc_generator.py` verify that `generate_execution_vc` correctly handles success, failure, and disabled states. [sdk/python/tests/test_vc_generator.py:20-61]()
- **Serialization**: Verifies that data is correctly base64 encoded for the VC payload. [sdk/python/tests/test_vc_generator.py:107-113]()
- **DID Registration**: `test_agent_networking.py` confirms that DID credentials are correctly wired to the HTTP client after registration. [sdk/python/tests/test_agent_networking.py:147-171]()

Sources: [sdk/python/tests/test_vc_generator.py:1-113](), [sdk/python/tests/test_agent_networking.py:147-171]()

---

# Page: Serverless Mode

# Serverless Mode

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [control-plane/internal/handlers/execute_awaiter_status.go](control-plane/internal/handlers/execute_awaiter_status.go)
- [control-plane/internal/handlers/execute_awaiter_status_test.go](control-plane/internal/handlers/execute_awaiter_status_test.go)
- [sdk/python/agentfield/agent.py](sdk/python/agentfield/agent.py)
- [sdk/python/agentfield/agent_discovery.py](sdk/python/agentfield/agent_discovery.py)
- [sdk/python/agentfield/agent_pause.py](sdk/python/agentfield/agent_pause.py)
- [sdk/python/agentfield/agent_schema.py](sdk/python/agentfield/agent_schema.py)
- [sdk/python/agentfield/agent_serverless.py](sdk/python/agentfield/agent_serverless.py)
- [sdk/python/agentfield/agent_vc.py](sdk/python/agentfield/agent_vc.py)
- [sdk/python/agentfield/async_execution_manager.py](sdk/python/agentfield/async_execution_manager.py)
- [sdk/python/agentfield/client.py](sdk/python/agentfield/client.py)
- [sdk/python/agentfield/exceptions.py](sdk/python/agentfield/exceptions.py)
- [sdk/python/agentfield/execution_state.py](sdk/python/agentfield/execution_state.py)
- [sdk/python/tests/test_agent_call.py](sdk/python/tests/test_agent_call.py)
- [sdk/python/tests/test_agent_coverage_additions.py](sdk/python/tests/test_agent_coverage_additions.py)
- [sdk/python/tests/test_async_config.py](sdk/python/tests/test_async_config.py)
- [sdk/python/tests/test_async_execution.py](sdk/python/tests/test_async_execution.py)
- [sdk/python/tests/test_client_laser_push.py](sdk/python/tests/test_client_laser_push.py)
- [sdk/python/tests/test_execution_state.py](sdk/python/tests/test_execution_state.py)

</details>



## Purpose and Scope

This document describes serverless deployment mode for AgentField agents, which enables agents to run in Function-as-a-Service (FaaS) environments like AWS Lambda, Azure Functions, Google Cloud Functions, and Cloud Run without maintaining persistent server processes.

Serverless mode provides an event-driven execution model where agents respond to discrete invocation events rather than running as long-lived HTTP servers. This contrasts with standard server mode where agents call `serve()` to start a persistent uvicorn server with heartbeat threads and WebSocket connections.

For deploying agents to traditional cloud infrastructure with persistent containers, see [Docker Deployment](#13.1) and [Railway Deployment](#13.2). For serverless deployment patterns specifically for TypeScript agents, see [Serverless Handler](#4.7).

---

## Architecture Comparison

Serverless mode fundamentally changes the agent lifecycle from a persistent service to an ephemeral function. The following diagram illustrates the architectural differences:

**Diagram: Agent Lifecycle Comparison**

```mermaid
graph TB
    subgraph Standard["Standard Server Mode"]
        Init1["Agent.__init__()"]
        Serve["AgentServer.serve()"]
        Reg1["AgentFieldHandler._register_agent()"]
        Heart["heartbeat_worker() thread"]
        WS["WebSocket connections"]
        Exec1["FastAPI /execute endpoint"]
        
        Init1 --> Serve
        Serve --> Reg1
        Serve --> Heart
        Serve --> WS
        Serve --> Exec1
        Heart -.->|"every 30s"| Reg1
    end
    
    subgraph Serverless["Serverless Mode"]
        Init2["Agent.__init__()"]
        Handler["Agent.handle_serverless(event)"]
        AutoReg["auto_register on first call"]
        Discover["_handle_discovery()"]
        Exec2["Direct function execution"]
        
        Init2 --> Handler
        Handler --> Discover
        Handler --> AutoReg
        Handler --> Exec2
        AutoReg -.->|"if auto_register=True"| Exec2
    end
    
    Lambda["Lambda/Cloud Function<br/>invocation event"] --> Handler
    HTTP["HTTP requests"] --> Exec1
```

**Key Architectural Differences**:

| Aspect | Standard Mode | Serverless Mode |
|--------|--------------|-----------------|
| Lifecycle | Long-lived process | Ephemeral function |
| Registration | At startup via `_register_agent()` | On-demand via `auto_register` |
| Heartbeats | Background thread every 30s | None |
| WebSocket | Persistent connections | Not supported |
| Invocation | HTTP requests to uvicorn | Cloud provider events |
| Port Binding | Binds to port (e.g., 8000) | No port binding |

**Sources**: [sdk/python/agentfield/agent.py:461-465](), [sdk/python/agentfield/agent.py:578-736]()

---

## Event Processing Flow

The `handle_serverless()` method processes events from serverless platforms and routes them to either the discovery or execution path. It handles the normalization of various event formats and manages the `ExecutionContext` lifecycle.

**Diagram: handle_serverless() Logic Flow**

```mermaid
sequenceDiagram
    participant Cloud as "Cloud Provider"
    participant Handler as "Agent.handle_serverless()"
    participant Discovery as "Agent._handle_discovery()"
    participant Registration as "AgentFieldHandler"
    participant Execution as "Reasoner/Skill Function"
    participant Context as "ExecutionContext"
    
    Cloud->>Handler: "Invocation event"
    
    Handler->>Handler: "Extract path/action"
    
    alt Discovery request
        Handler->>Discovery: "path='/discover'"
        Discovery-->>Handler: "Agent metadata"
        Handler-->>Cloud: "reasoners, skills, schemas"
    else Execution request
        Handler->>Handler: "Check auto_register"
        
        opt First execution
            Handler->>Registration: "_register_agent()"
            Registration-->>Handler: "agentfield_connected=True"
        end
        
        Handler->>Handler: "Set agentfield_connected=True"
        Handler->>Handler: "Force enable_async_execution=False"
        
        Handler->>Context: "Create ExecutionContext"
        Handler->>Execution: "Execute target function"
        
        alt Async function
            Execution->>Execution: "asyncio.run(func(**input))"
        else Sync function
            Execution->>Execution: "func(**input)"
        end
        
        Execution-->>Handler: "result"
        Handler-->>Cloud: "{statusCode: 200, body: result}"
    end
```

**Sources**: [sdk/python/agentfield/agent.py:578-736](), [sdk/python/agentfield/agent.py:649-651]()

---

## Discovery Endpoint

The discovery endpoint returns agent metadata that the control plane uses for registration. This enables the control plane to understand the agent's capabilities without the agent proactively registering.

### Discovery Request Detection

The handler recognizes discovery requests through multiple event formats:

```python
# Detection logic in handle_serverless
path = event.get("path") or event.get("rawPath") or ""
action = event.get("action", "")

if path == "/discover" or path.endswith("/discover") or action == "discover":
    return self._handle_discovery()
```

### Discovery Response Structure

The `_handle_discovery()` method returns a structured metadata payload derived from the agent's internal registries.

**Diagram: Metadata Extraction for Discovery**

```mermaid
graph TB
    HandleDisc["Agent._handle_discovery()"]
    
    HandleDisc --> NodeMeta["node_id, version, deployment_type='serverless'"]
    HandleDisc --> Reasoners["reasoners[] from _reasoner_registry"]
    HandleDisc --> Skills["skills[] from _skill_registry"]
    
    Reasoners --> R1["id"]
    Reasoners --> R2["input_schema (Pydantic)"]
    Reasoners --> R3["output_schema"]
    Reasoners --> R4["memory_config"]
    
    Skills --> S1["id"]
    Skills --> S2["input_schema"]
```

**Sources**: [sdk/python/agentfield/agent.py:737-769](), [sdk/python/agentfield/agent.py:113-144]()

---

## Execution Request Processing

Execution requests trigger reasoner or skill invocation. The handler supports multiple event formats for compatibility with different serverless platforms.

### Event Format Parsing

The handler extracts execution parameters from various event structures, prioritizing fields like `reasoner`, `target`, or `skill`.

| Purpose | Field Priority (first found wins) |
|---------|-----------------------------------|
| Target function | `reasoner` → `target` → `skill` → parsed from `path` |
| Input data | `input` → `input_data` |
| Execution context | `execution_context` → `executionContext` |

**Sources**: [sdk/python/agentfield/agent.py:653-668]()

### Execution Context Construction

The handler constructs an `ExecutionContext` with proper ID generation. In serverless mode, if a `run_id` is not provided, it defaults to the `workflow_id` or a new timestamp-based ID.

```python
# Logic from handle_serverless
exec_id = execution_context_data.get("execution_id", f"exec_{int(time.time() * 1000)}")
run_id = execution_context_data.get("run_id") or execution_context_data.get("workflow_id")
if not run_id:
    run_id = f"wf_{int(time.time() * 1000)}"
```

**Sources**: [sdk/python/agentfield/agent.py:681-708]()

---

## Auto-Registration

Serverless agents use lazy registration triggered on first invocation instead of startup registration. This pattern accommodates ephemeral execution environments.

### Configuration

Auto-registration is controlled by the `auto_register` constructor parameter in the `Agent` class.

```python
app = Agent(
    node_id="my_agent",
    auto_register=True,  # Enable auto-registration (default)
    agentfield_server="https://your-control-plane.com"
)
```

### Registration Behavior

1. First execution checks `self.auto_register` and `not self.agentfield_connected`.
2. Attempts registration via `AgentFieldHandler._register_agent()`.
3. Sets `agentfield_connected=True` to prevent repeated registration attempts within the same invocation.

**Sources**: [sdk/python/agentfield/agent.py:461-462](), [sdk/python/agentfield/agent.py:637-644]()

---

## Serverless Mode Constraints

Several features are disabled or modified in serverless mode to accommodate the stateless execution model.

### Disabled Features

- **Heartbeats**: The background heartbeat thread is not started.
- **WebSocket**: Persistent connections for memory events or terminal streaming are not supported.
- **Async Polling**: The agent forces `enable_async_execution = False` in `self.async_config`. This ensures that if the agent calls another agent, it uses the synchronous execution path rather than returning an execution ID and polling.

### Pause and Resume

While `Agent.pause()` is supported, in serverless mode it relies on the `_PauseManager` to wait for a webhook resolution within the function's execution timeout. If the cloud provider's timeout is reached before approval, the function will terminate.

**Sources**: [sdk/python/agentfield/agent.py:649-651](), [sdk/python/agentfield/agent_pause.py:49-116]()

---

## Cloud Provider Adapters

The `handle_serverless()` method accepts an optional `adapter` function to normalize cloud provider event formats.

```python
def handle_serverless(
    self, 
    event: dict, 
    adapter: Optional[Callable] = None
) -> dict:
```

The adapter receives the raw cloud provider event and should return a dictionary containing keys like `path`, `input`, and `execution_context`.

**Sources**: [sdk/python/agentfield/agent.py:619-626]()

---

## Memory and State Considerations

Serverless agents have limited memory and state management capabilities compared to standard mode.

### Memory Client Behavior

Memory operations work through the `MemoryClient`, which communicates with the control plane's storage layer via HTTP. However, real-time memory events (subscriptions) are not supported because they require a persistent WebSocket connection.

**Sources**: [sdk/python/agentfield/agent.py:809-916](), [sdk/python/agentfield/memory_events.py:79-421]()

### Execution Context Lifecycle

The `ExecutionContext` is created per invocation and cleared after execution using a `finally` block to ensure no state leakage between recycled function containers.

```python
# handle_serverless context management
self._current_execution_context = execution_context
try:
    # ... execution logic ...
finally:
    self._current_execution_context = None
    reset_execution_context()
```

**Sources**: [sdk/python/agentfield/agent.py:710-735](), [sdk/python/agentfield/execution_context.py:37-42]()

---

## Sources Summary

- Agent class and serverless handler: [sdk/python/agentfield/agent.py:461-769]()
- Metadata and Registries: [sdk/python/agentfield/agent.py:113-144]()
- Execution Context: [sdk/python/agentfield/execution_context.py:37-42]()
- Pause Management: [sdk/python/agentfield/agent_pause.py:49-116]()
- Client Execution: [sdk/python/agentfield/client.py:142-218]()

---

# Page: TypeScript SDK

# TypeScript SDK

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [control-plane/web/client/package-lock.json](control-plane/web/client/package-lock.json)
- [control-plane/web/client/package.json](control-plane/web/client/package.json)
- [control-plane/web/client/pnpm-lock.yaml](control-plane/web/client/pnpm-lock.yaml)
- [control-plane/web/client/src/components/ui/icon-bridge.tsx](control-plane/web/client/src/components/ui/icon-bridge.tsx)
- [control-plane/web/client/src/components/ui/icon.tsx](control-plane/web/client/src/components/ui/icon.tsx)
- [examples/benchmarks/100k-scale/mastra-bench/package-lock.json](examples/benchmarks/100k-scale/mastra-bench/package-lock.json)
- [examples/benchmarks/100k-scale/mastra-bench/package.json](examples/benchmarks/100k-scale/mastra-bench/package.json)
- [examples/python_agent_nodes/rag_evaluation/ui/package-lock.json](examples/python_agent_nodes/rag_evaluation/ui/package-lock.json)
- [examples/python_agent_nodes/rag_evaluation/ui/package.json](examples/python_agent_nodes/rag_evaluation/ui/package.json)
- [sdk/typescript/package-lock.json](sdk/typescript/package-lock.json)
- [sdk/typescript/src/agent/Agent.ts](sdk/typescript/src/agent/Agent.ts)
- [sdk/typescript/src/ai/AIClient.ts](sdk/typescript/src/ai/AIClient.ts)
- [sdk/typescript/src/client/AgentFieldClient.ts](sdk/typescript/src/client/AgentFieldClient.ts)
- [sdk/typescript/src/context/ReasonerContext.ts](sdk/typescript/src/context/ReasonerContext.ts)
- [sdk/typescript/src/index.ts](sdk/typescript/src/index.ts)
- [sdk/typescript/src/router/AgentRouter.ts](sdk/typescript/src/router/AgentRouter.ts)
- [sdk/typescript/src/triggers/factories.ts](sdk/typescript/src/triggers/factories.ts)
- [sdk/typescript/src/triggers/index.ts](sdk/typescript/src/triggers/index.ts)
- [sdk/typescript/src/triggers/types.ts](sdk/typescript/src/triggers/types.ts)
- [sdk/typescript/src/types/agent.ts](sdk/typescript/src/types/agent.ts)
- [sdk/typescript/src/types/reasoner.ts](sdk/typescript/src/types/reasoner.ts)
- [sdk/typescript/tests/agent.test.ts](sdk/typescript/tests/agent.test.ts)
- [sdk/typescript/tests/ai_client.test.ts](sdk/typescript/tests/ai_client.test.ts)
- [sdk/typescript/tests/triggers.test.ts](sdk/typescript/tests/triggers.test.ts)

</details>



The TypeScript SDK (`@agentfield/sdk`) provides a complete toolkit for building AI agents in Node.js environments. It handles agent registration, execution context management, AI provider integration, memory operations, and communication with the AgentField control plane.

This page covers the TypeScript-specific implementation. For the Python SDK, see [Python SDK](#3). For Go SDK, see [Go SDK](#5).

---

## Installation and Setup

The TypeScript SDK is published to npm as `@agentfield/sdk`. It requires Node.js 18.0.0 or higher.

```bash
npm install @agentfield/sdk
```

The package ships as an ES module with TypeScript type definitions included.

**Sources:** [sdk/typescript/package-lock.json:7-44](), [sdk/typescript/src/agent/Agent.ts:75-75]()

---

## Agent Class

The `Agent` class is the primary interface for creating and running agents. It manages reasoners, skills, HTTP server lifecycle, control plane registration, and execution contexts. For details, see [Agent Class](#4.1).

### Configuration

The `Agent` constructor accepts an `AgentConfig` object which defines its identity and connection parameters.

```typescript
interface AgentConfig {
  nodeId: string;                    // Unique identifier for this agent
  version?: string;                  // Agent version
  agentFieldUrl?: string;            // Control plane URL (default: http://localhost:8080)
  port?: number;                     // HTTP server port (default: 8001)
  host?: string;                     // Bind address (default: 0.0.0.0)
  aiConfig?: AIConfig;               // AI provider configuration
  memoryConfig?: MemoryConfig;       // Memory defaults
  didEnabled?: boolean;              // Enable DID system (default: true)
  deploymentType?: 'long_running' | 'serverless';
  asyncExecution?: boolean;          // Enable detached execution (default: true)
  executionBudgetMs?: number;        // Wall-clock budget for detached reasoners
}
```

**Sources:** [sdk/typescript/src/types/agent.ts:10-54](), [sdk/typescript/src/agent/Agent.ts:146-155]()

### Agent Lifecycle

The agent lifecycle involves initializing subsystems, registering with the control plane, and maintaining a heartbeat.

```mermaid
graph TB
    Constructor["Agent.constructor()"]
    Setup["Initialize Subsystems"]
    Serve["Agent.serve()"]
    Register["AgentFieldClient.register()"]
    Listen["Express.listen()"]
    Heartbeat["AgentFieldClient.heartbeat()"]
    Ready["Agent Node Ready"]
    Shutdown["Agent.shutdown()"]
    
    Constructor --> Setup
    Setup --> AIClient["AIClient"]
    Setup --> AgentFieldClient["AgentFieldClient"]
    Setup --> MemoryClient["MemoryClient"]
    Setup --> DidManager["DidManager"]
    
    Serve --> Register
    Register --> Listen
    Listen --> Heartbeat
    Heartbeat --> Ready
    
    Ready --> Shutdown
    Shutdown --> CloseServer["server.close()"]
    Shutdown --> StopHeartbeat["clearInterval(heartbeatTimer)"]
    
    style Constructor fill:#e1f5ff
    style Ready fill:#d4edda
    style Shutdown fill:#f8d7da
```

**Sources:** [sdk/typescript/src/agent/Agent.ts:146-258](), [sdk/typescript/src/client/AgentFieldClient.ts:170-196]()

---

## Reasoners and Skills

Agents expose capabilities through Reasoners and Skills. For details, see [Reasoners and Skills](#4.2).

### Reasoners
Reasoners are AI-powered functions defined with `agent.reasoner()`. They have access to the `AIClient` for LLM generation and can call other agents.

### Skills
Skills are deterministic functions defined with `agent.skill()`. They are used for tool execution and data processing without direct LLM access.

**Sources:** [sdk/typescript/src/agent/Agent.ts:113-114](), [sdk/typescript/src/types/reasoner.ts:1-20](), [sdk/typescript/src/types/skill.ts:1-12]()

---

## Execution Contexts

The SDK uses `ExecutionContext` to manage metadata and state for every invocation. For details, see [Execution Contexts](#4.3).

When an agent receives a request, it populates a `ReasonerContext` or `SkillContext` with execution metadata extracted from headers like `X-Execution-ID` and `X-Workflow-ID`.

```mermaid
graph TB
    Request["Incoming HTTP Request"]
    Extract["normalizeExecutionContext()"]
    Ctx["new ReasonerContext()"]
    Run["reasoner.handler(ctx)"]
    
    subgraph "Context Services"
        AI["ctx.ai()"]
        Mem["ctx.memory"]
        Call["ctx.call()"]
        Pause["ctx.pause()"]
    end
    
    Request --> Extract
    Extract --> Ctx
    Ctx --> Run
    Run --> AI
    Run --> Mem
    Run --> Call
    Run --> Pause
```

**Sources:** [sdk/typescript/src/agent/Agent.ts:92-108](), [sdk/typescript/src/context/ReasonerContext.ts:13-90](), [sdk/typescript/src/context/SkillContext.ts:9-52]()

---

## AI Client

The `AIClient` provides a unified interface to multiple LLM providers using the Vercel AI SDK. For details, see [AI Client](#4.4).

It supports providers such as OpenAI, Anthropic, Google, and DeepSeek, offering methods for text generation, streaming, and embeddings.

**Sources:** [sdk/typescript/src/ai/AIClient.ts:1-331](), [sdk/typescript/src/types/agent.ts:56-84]()

---

## Memory Interface

The `MemoryInterface` manages state across different scopes: `workflow`, `session`, `actor`, and `global`. For details, see [Memory Interface](#4.5).

It supports standard key-value operations as well as vector operations for RAG (Retrieval-Augmented Generation) workflows.

**Sources:** [sdk/typescript/src/memory/MemoryInterface.ts:1-226](), [sdk/typescript/src/types/agent.ts:86-91]()

---

## AgentRouter

The `AgentRouter` allows developers to modularize agent capabilities. For details, see [AgentRouter](#4.6).

Routers can be used to group related reasoners and skills under a common prefix, which are then included in the main agent using `agent.includeRouter()`.

**Sources:** [sdk/typescript/src/router/AgentRouter.ts:1-44](), [sdk/typescript/src/agent/Agent.ts:25-25]()

---

## Serverless Handler

The SDK includes a built-in handler for serverless environments. For details, see [Serverless Handler](#4.7).

By using `agent.handler()`, agents can be deployed to AWS Lambda or similar platforms. The handler normalizes incoming events and routes them to the appropriate reasoner or skill.

**Sources:** [sdk/typescript/src/agent/Agent.ts:516-578](), [sdk/typescript/src/types/agent.ts:218-221]()

---

# Page: Agent Class

# Agent Class

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [sdk/typescript/src/agent/Agent.ts](sdk/typescript/src/agent/Agent.ts)
- [sdk/typescript/src/ai/AIClient.ts](sdk/typescript/src/ai/AIClient.ts)
- [sdk/typescript/src/client/AgentFieldClient.ts](sdk/typescript/src/client/AgentFieldClient.ts)
- [sdk/typescript/src/context/ReasonerContext.ts](sdk/typescript/src/context/ReasonerContext.ts)
- [sdk/typescript/src/index.ts](sdk/typescript/src/index.ts)
- [sdk/typescript/src/router/AgentRouter.ts](sdk/typescript/src/router/AgentRouter.ts)
- [sdk/typescript/src/triggers/factories.ts](sdk/typescript/src/triggers/factories.ts)
- [sdk/typescript/src/triggers/index.ts](sdk/typescript/src/triggers/index.ts)
- [sdk/typescript/src/triggers/types.ts](sdk/typescript/src/triggers/types.ts)
- [sdk/typescript/src/types/agent.ts](sdk/typescript/src/types/agent.ts)
- [sdk/typescript/src/types/reasoner.ts](sdk/typescript/src/types/reasoner.ts)
- [sdk/typescript/tests/agent.test.ts](sdk/typescript/tests/agent.test.ts)
- [sdk/typescript/tests/ai_client.test.ts](sdk/typescript/tests/ai_client.test.ts)
- [sdk/typescript/tests/triggers.test.ts](sdk/typescript/tests/triggers.test.ts)

</details>



The `Agent` class in the TypeScript SDK is the primary interface for building agent nodes. It serves as both a web server (via Express) and a distributed agent node that integrates with the AgentField control plane.

The `Agent` class is defined in [sdk/typescript/src/agent/Agent.ts:110-1010]() and provides the foundation for registering capabilities, managing execution lifecycles, and interacting with the AgentField ecosystem.

**Sources:** [sdk/typescript/src/agent/Agent.ts:110-145](), [sdk/typescript/src/index.ts:1-33]()

---

## Class Architecture

The `Agent` class encapsulates several specialized registries and clients to manage different aspects of an AI agent's lifecycle.

```mermaid
graph TB
    subgraph "Agent Instance"
        Agent["Agent Class"]
        Express["Express App<br/>(HTTP Server)"]
        
        subgraph "Registries"
            RR["ReasonerRegistry"]
            SR["SkillRegistry"]
            CR["CancelRegistry"]
        end
        
        subgraph "Clients"
            AI["AIClient"]
            AF["AgentFieldClient"]
            Mem["MemoryClient"]
            DID["DidClient"]
        end
    end
    
    Agent --> Express
    Agent --> RR
    Agent --> SR
    Agent --> CR
    Agent --> AI
    Agent --> AF
    Agent --> Mem
    Agent --> DID
```

**Sources:** [sdk/typescript/src/agent/Agent.ts:110-145](), [sdk/typescript/src/agent/ReasonerRegistry.ts:1-20](), [sdk/typescript/src/agent/SkillRegistry.ts:1-20]()

---

## Configuration

The `Agent` constructor accepts an `AgentConfig` object [sdk/typescript/src/types/agent.ts:10-54]().

### Core Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `nodeId` | `string` | Required | Unique identifier for this agent node. |
| `agentFieldUrl`| `string` | `"http://localhost:8080"` | URL of the AgentField control plane. |
| `port` | `number` | `8001` | Port the agent's HTTP server listens on. |
| `aiConfig` | `AIConfig` | `undefined` | LLM provider and model settings. |
| `deploymentType`| `DeploymentType`| `"long_running"` | `"long_running"` or `"serverless"`. |
| `asyncExecution`| `boolean` | `true` | Enables detached, asynchronous execution. |
| `didEnabled` | `boolean` | `true` | Enables DID-based identity and signatures. |

**Sources:** [sdk/typescript/src/agent/Agent.ts:146-155](), [sdk/typescript/src/types/agent.ts:10-54]()

---

## Initialization Flow

When an `Agent` is instantiated, it initializes its internal services and prepares the Express application.

```mermaid
sequenceDiagram
    participant App as "User Code"
    participant Agent as "Agent Instance"
    participant Express as "Express Server"
    participant AF as "AgentFieldClient"
    
    App->>Agent: "new Agent(config)"
    Agent->>Agent: "Merge default config"
    Agent->>Express: "Initialize express()"
    Agent->>AF: "Initialize AgentFieldClient"
    Agent->>Agent: "Initialize registries (Reasoner, Skill, Cancel)"
    Agent->>Agent: "Register internal routes (/status, /discover, /execute)"
    Agent-->>App: "Agent instance ready"
```

**Sources:** [sdk/typescript/src/agent/Agent.ts:146-218](), [sdk/typescript/src/client/AgentFieldClient.ts:152-168]()

---

## Capability Registration

Agents expose functionality through **Reasoners** and **Skills**.

### Registering Reasoners
Reasoners are AI-powered handlers that receive a `ReasonerContext` [sdk/typescript/src/context/ReasonerContext.ts:13-179]().

```typescript
agent.reasoner("analyze", async (ctx) => {
  const sentiment = await ctx.ai("Analyze sentiment of: " + ctx.input.text);
  return { sentiment };
}, {
  description: "Analyzes text sentiment",
  tags: ["nlp"]
});
```

### Registering Skills
Skills are deterministic functions used for tools or data transformation [sdk/typescript/src/agent/Agent.ts:334-350]().

```typescript
agent.skill("format", (ctx) => {
  return ctx.input.value.toUpperCase();
});
```

**Sources:** [sdk/typescript/src/agent/Agent.ts:285-325](), [sdk/typescript/src/agent/Agent.ts:334-350](), [sdk/typescript/tests/agent.test.ts:7-14]()

---

## Lifecycle Methods

### Starting the Agent
The `serve()` method starts the HTTP server and registers the agent with the control plane [sdk/typescript/src/agent/Agent.ts:515-562]().

1. **Start Server**: Binds the Express app to the configured port.
2. **Register**: Sends the agent's manifest (reasoners, skills, metadata) to the control plane via `AgentFieldClient.register()` [sdk/typescript/src/client/AgentFieldClient.ts:170-177]().
3. **Heartbeat**: Starts a periodic timer to notify the control plane that the node is alive [sdk/typescript/src/agent/Agent.ts:544-555]().

### Stopping the Agent
The `stop()` method cleans up resources [sdk/typescript/src/agent/Agent.ts:577-584]().
- Clears the heartbeat timer.
- Closes the HTTP server.
- Notifies the control plane of the offline status.

**Sources:** [sdk/typescript/src/agent/Agent.ts:515-584](), [sdk/typescript/src/client/AgentFieldClient.ts:186-196]()

---

## Execution and Communication

### Cross-Agent Calls
Agents communicate using the `call()` method. If the target is local (same `nodeId`), it executes directly; otherwise, it dispatches via the control plane [sdk/typescript/src/agent/Agent.ts:408-460]().

```mermaid
graph LR
    subgraph "Agent.call(target, input)"
        Check["Target Node ID?"]
        Local["Execute Local Handler"]
        Remote["AgentFieldClient.execute()"]
        
        Check -- "Match" --> Local
        Check -- "No Match" --> Remote
    end
    
    Remote --> CP["Control Plane /api/v1/execute"]
```

**Sources:** [sdk/typescript/src/agent/Agent.ts:408-460](), [sdk/typescript/src/client/AgentFieldClient.ts:198-235](), [sdk/typescript/tests/agent.test.ts:56-62]()

### Execution Context
During execution, the SDK manages an `ExecutionContext` using asynchronous local storage. This allows handlers to access metadata like `executionId`, `workflowId`, and `sessionId` without passing them as arguments [sdk/typescript/src/context/ExecutionContext.ts:1-100]().

**Sources:** [sdk/typescript/src/context/ReasonerContext.ts:181-205](), [sdk/typescript/src/agent/Agent.ts:643-680]()

---

## Memory and Events

The `Agent` class provides a high-level interface for memory operations and real-time event watching.

- **`watchMemory(pattern, handler, options)`**: Registers a callback for memory changes matching a glob pattern [sdk/typescript/src/agent/Agent.ts:365-375]().
- **Memory Scopes**: Supports `workflow`, `session`, `actor`, and `global` scopes [sdk/typescript/src/types/agent.ts:91]().

**Sources:** [sdk/typescript/src/agent/Agent.ts:365-375](), [sdk/typescript/tests/agent.test.ts:64-92]()

---

## Serverless Support

For FaaS environments (AWS Lambda, etc.), the `handler()` method provides an adapter that translates serverless events into agent executions [sdk/typescript/src/agent/Agent.ts:592-628]().

```typescript
export const handler = agent.handler();
```

**Sources:** [sdk/typescript/src/agent/Agent.ts:592-628](), [sdk/typescript/src/types/agent.ts:192-221]()

---

# Page: Reasoners and Skills

# Reasoners and Skills

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [sdk/typescript/src/agent/Agent.ts](sdk/typescript/src/agent/Agent.ts)
- [sdk/typescript/src/ai/AIClient.ts](sdk/typescript/src/ai/AIClient.ts)
- [sdk/typescript/src/client/AgentFieldClient.ts](sdk/typescript/src/client/AgentFieldClient.ts)
- [sdk/typescript/src/context/ReasonerContext.ts](sdk/typescript/src/context/ReasonerContext.ts)
- [sdk/typescript/src/index.ts](sdk/typescript/src/index.ts)
- [sdk/typescript/src/router/AgentRouter.ts](sdk/typescript/src/router/AgentRouter.ts)
- [sdk/typescript/src/triggers/factories.ts](sdk/typescript/src/triggers/factories.ts)
- [sdk/typescript/src/triggers/index.ts](sdk/typescript/src/triggers/index.ts)
- [sdk/typescript/src/triggers/types.ts](sdk/typescript/src/triggers/types.ts)
- [sdk/typescript/src/types/agent.ts](sdk/typescript/src/types/agent.ts)
- [sdk/typescript/src/types/reasoner.ts](sdk/typescript/src/types/reasoner.ts)
- [sdk/typescript/tests/agent.test.ts](sdk/typescript/tests/agent.test.ts)
- [sdk/typescript/tests/ai_client.test.ts](sdk/typescript/tests/ai_client.test.ts)
- [sdk/typescript/tests/triggers.test.ts](sdk/typescript/tests/triggers.test.ts)

</details>



This page covers the definition, registration, and configuration of reasoners and skills in the TypeScript SDK. For information about the Agent class initialization and lifecycle, see [Agent Class](). For details on the execution context objects passed to handlers, see [Execution Contexts](). For the Python SDK equivalents, see [Defining Reasoners]() and [Defining Skills]().

## Overview

Reasoners and skills are the two types of capabilities that agents expose:

- **Reasoners**: AI-powered functions that use LLMs to process input and generate output. They have access to the AI client, memory, and workflow tracking.
- **Skills**: Deterministic functions that perform concrete operations like API calls, data transformation, or file I/O. They do not directly access AI models.

Both are registered on an `Agent` instance and become discoverable through the control plane. When invoked, they receive a context object that provides access to execution metadata, memory, and other agent services.

## Defining Reasoners

Reasoners are defined using the `agent.reasoner()` method, which registers a handler function with the `ReasonerRegistry`.

### Basic Reasoner Definition

```typescript
agent.reasoner<TInput, TOutput>(
  name: string,
  handler: ReasonerHandler<TInput, TOutput>,
  options?: ReasonerOptions
)
```

**Registration Flow Diagram**

```mermaid
graph LR
    Dev["Developer calls<br/>agent.reasoner()"]
    Method["Agent.reasoner()<br/>[Agent.ts:100-107]"]
    Registry["ReasonerRegistry<br/>[Agent.ts:113]"]
    Store["reasoners.register()<br/>stores definition"]
    Discovery["reasonerDefinitions()<br/>[Agent.ts:727-739]"]
    ControlPlane["Control Plane<br/>Registration"]
    
    Dev --> Method
    Method --> Registry
    Registry --> Store
    Store --> Discovery
    Discovery --> ControlPlane
```

**Sources:** [sdk/typescript/src/agent/Agent.ts:100-107](), [sdk/typescript/src/agent/Agent.ts:113](), [sdk/typescript/src/agent/Agent.ts:727-739]()

### Handler Signature

The `ReasonerHandler` receives a `ReasonerContext` and returns the output value:

```typescript
type ReasonerHandler<TInput, TOutput> = (
  ctx: ReasonerContext<TInput>
) => Promise<TOutput> | TOutput
```

The `ReasonerContext` provides access to:

| Property | Type | Description |
|----------|------|-------------|
| `input` | `TInput` | The input data passed to the reasoner |
| `aiClient` | `AIClient` | AI client for LLM calls |
| `memory` | `MemoryInterface` | Scoped memory access |
| `workflow` | `WorkflowReporter` | Workflow event publishing |
| `did` | `DidInterface` | DID and VC operations |
| `agent` | `Agent` | Reference to the parent agent |
| `executionId` | `string` | Unique execution identifier |
| `runId` | `string?` | Run identifier for grouping |
| `workflowId` | `string?` | Workflow identifier |
| `sessionId` | `string?` | Optional session scope ID |
| `actorId` | `string?` | Optional actor scope ID |
| `signal` | `AbortSignal` | Signal to short-circuit work if cancelled |

**Sources:** [sdk/typescript/src/context/ReasonerContext.ts:13-179](), [sdk/typescript/src/types/reasoner.ts:10-12]()

### Reasoner Options

The `ReasonerOptions` interface controls how the reasoner is presented to the control plane and how it behaves during execution.

| Option | Type | Purpose |
|--------|------|---------|
| `inputSchema` | `any` | JSON Schema for input validation |
| `outputSchema` | `any` | JSON Schema for output validation |
| `tags` | `string[]` | Discovery tags for filtering |
| `triggers` | `TriggerBinding[]` | Inbound event/cron bindings |
| `acceptsWebhook` | `boolean \| 'warn'` | Opt-in/out for webhook invocation |
| `requireRealtimeValidation` | `boolean` | Force control-plane signature verification |

**Sources:** [sdk/typescript/src/types/reasoner.ts:14-45]()

### Triggers and Events

Reasoners can be bound to external events (like Stripe or GitHub webhooks) or schedules (cron) using the `triggers` option.

```typescript
import { eventTrigger, scheduleTrigger } from "@agentfield/sdk";

agent.reasoner("handle_payment", handler, {
  triggers: [
    eventTrigger({
      source: "stripe",
      types: ["payment_intent.succeeded"],
      secretEnv: "STRIPE_WEBHOOK_SECRET",
    }),
    scheduleTrigger({ cron: "0 * * * *" }),
  ],
});
```

**Sources:** [sdk/typescript/src/triggers/factories.ts:1-18](), [sdk/typescript/src/triggers/types.ts:109-122]()

## Defining Skills

Skills are defined using the `agent.skill()` method, which registers a handler with the `SkillRegistry`.

### Basic Skill Definition

```typescript
agent.skill<TInput, TOutput>(
  name: string,
  handler: SkillHandler<TInput, TOutput>,
  options?: SkillOptions
)
```

**Sources:** [sdk/typescript/src/agent/Agent.ts:109-116]()

### Handler Signature

The `SkillHandler` receives a `SkillContext` and returns the output value:

```typescript
type SkillHandler<TInput, TOutput> = (
  ctx: SkillContext<TInput>
) => Promise<TOutput> | TOutput
```

The `SkillContext` provides:

| Property | Type | Description |
|----------|------|-------------|
| `input` | `TInput` | The input data passed to the skill |
| `memory` | `MemoryInterface` | Scoped memory access |
| `workflow` | `WorkflowReporter` | Workflow event publishing |
| `did` | `DidInterface` | DID and VC operations |
| `agent` | `Agent` | Reference to the parent agent |
| `executionId` | `string` | Unique execution identifier |

Note that `SkillContext` does not include `aiClient` since skills are deterministic operations.

**Sources:** [sdk/typescript/src/context/SkillContext.ts:1-30]()

## Registration and Discovery

When an agent registers with the control plane, it sends definitions for all reasoners and skills. These definitions are constructed by the `reasonerDefinitions()` and `skillDefinitions()` private methods.

**Discovery Payload Structure**

```mermaid
graph TB
    Agent["Agent Instance"]
    RegMethod["registerWithControlPlane()<br/>[Agent.ts:902-946]"]
    ReasonerDefs["reasonerDefinitions()<br/>[Agent.ts:727-739]"]
    SkillDefs["skillDefinitions()<br/>[Agent.ts:741-747]"]
    Payload["Registration Payload"]
    CP["Control Plane<br/>/api/v1/nodes/register"]
    
    Agent --> RegMethod
    RegMethod --> ReasonerDefs
    RegMethod --> SkillDefs
    ReasonerDefs --> Payload
    SkillDefs --> Payload
    Payload --> CP
    
    ReasonerDefs --> R1["reasoner: {<br/>id, input_schema,<br/>output_schema,<br/>triggers, tags}"]
    SkillDefs --> S1["skill: {<br/>id, input_schema,<br/>tags}"]
```

**Sources:** [sdk/typescript/src/agent/Agent.ts:902-946](), [sdk/typescript/src/agent/Agent.ts:727-747]()

## Organizing with AgentRouter

The `AgentRouter` class allows you to organize related reasoners and skills under a common prefix, making large agents more maintainable.

### AgentRouter Structure

```mermaid
graph TB
    Router["AgentRouter<br/>{prefix: 'nlp'}"]
    Agent["Agent Instance"]
    Include["agent.includeRouter(router)<br/>[Agent.ts:118-121]"]
    
    Router --> R1["router.reasoner('analyze')<br/>→ 'nlp_analyze'"]
    Router --> R2["router.reasoner('classify')<br/>→ 'nlp_classify'"]
    Router --> S1["router.skill('tokenize')<br/>→ 'nlp_tokenize'"]
    
    R1 --> Include
    R2 --> Include
    S1 --> Include
    
    Include --> Agent
    
    Agent --> RegR["ReasonerRegistry<br/>stores 'nlp_analyze'"]
    Agent --> RegS["SkillRegistry<br/>stores 'nlp_tokenize'"]
```

**Sources:** [sdk/typescript/src/router/AgentRouter.ts:1-44](), [sdk/typescript/src/agent/Agent.ts:118-121]()

## Execution Flow

When a reasoner or skill is invoked, the agent creates an `ExecutionContext` and dispatches to the appropriate handler.

**Invocation Flow Diagram**

```mermaid
sequenceDiagram
    participant CP as "Control Plane"
    participant HTTP as "Express Route<br/>/reasoners/:name"
    participant Agent as "Agent.executeReasoner()<br/>[Agent.ts:409-427]"
    participant Invoke as "executeInvocation()<br/>[Agent.ts:759-789]"
    participant Run as "runReasoner()<br/>[Agent.ts:791-848]"
    participant ExecCtx as "ExecutionContext"
    participant Handler as "ReasonerHandler"
    
    CP->>HTTP: POST /api/v1/reasoners/summarize
    HTTP->>Agent: executeReasoner(req, res, 'summarize')
    Agent->>Invoke: executeInvocation({targetName, targetType: 'reasoner'})
    Invoke->>Run: runReasoner(reasoner, params)
    Run->>ExecCtx: new ExecutionContext({input, metadata})
    ExecCtx->>Handler: await handler(new ReasonerContext(...))
    Handler-->>ExecCtx: result
    ExecCtx-->>Run: result
    Run-->>HTTP: res.json(result)
    HTTP-->>CP: 200 OK
```

**Sources:** [sdk/typescript/src/agent/Agent.ts:409-427](), [sdk/typescript/src/agent/Agent.ts:759-789](), [sdk/typescript/src/agent/Agent.ts:791-848]()

### Async Execution and Budget

If `asyncExecution` is enabled in `AgentConfig`, reasoners invoked with an `X-Execution-ID` are acknowledged with `202 Accepted` and run detached. The terminal result is delivered to the control plane via `POST /executions/{id}/status`. This allows for long-running operations and `ctx.pause()` calls.

**Sources:** [sdk/typescript/src/agent/Agent.ts:154-155](), [sdk/typescript/src/types/agent.ts:45-53]()

### Target Resolution

The `executeInvocation()` method resolves the target type:
1. If `targetType === 'skill'`, look up in `SkillRegistry`.
2. Otherwise, try `ReasonerRegistry` first.
3. If not found, fall back to `SkillRegistry`.
4. If still not found, throw `TargetNotFoundError`.

**Sources:** [sdk/typescript/src/agent/Agent.ts:759-789]()

## Type Safety

Both `reasoner()` and `skill()` methods accept generic type parameters for compile-time type checking:

```typescript
interface SummarizeInput {
  document: string;
}

interface SummarizeOutput {
  summary: string;
}

agent.reasoner<SummarizeInput, SummarizeOutput>(
  'summarize',
  async (ctx) => {
    // ctx.input is typed as SummarizeInput
    return { summary: '...' };
  }
);
```

**Sources:** [sdk/typescript/src/agent/Agent.ts:100-116](), [sdk/typescript/src/types/reasoner.ts:4-12](), [sdk/typescript/src/types/skill.ts:4-12]()

---

# Page: Execution Contexts

# Execution Contexts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [sdk/typescript/src/agent/Agent.ts](sdk/typescript/src/agent/Agent.ts)
- [sdk/typescript/src/ai/AIClient.ts](sdk/typescript/src/ai/AIClient.ts)
- [sdk/typescript/src/client/AgentFieldClient.ts](sdk/typescript/src/client/AgentFieldClient.ts)
- [sdk/typescript/src/context/ReasonerContext.ts](sdk/typescript/src/context/ReasonerContext.ts)
- [sdk/typescript/src/index.ts](sdk/typescript/src/index.ts)
- [sdk/typescript/src/router/AgentRouter.ts](sdk/typescript/src/router/AgentRouter.ts)
- [sdk/typescript/src/triggers/factories.ts](sdk/typescript/src/triggers/factories.ts)
- [sdk/typescript/src/triggers/index.ts](sdk/typescript/src/triggers/index.ts)
- [sdk/typescript/src/triggers/types.ts](sdk/typescript/src/triggers/types.ts)
- [sdk/typescript/src/types/agent.ts](sdk/typescript/src/types/agent.ts)
- [sdk/typescript/src/types/reasoner.ts](sdk/typescript/src/types/reasoner.ts)
- [sdk/typescript/tests/agent.test.ts](sdk/typescript/tests/agent.test.ts)
- [sdk/typescript/tests/ai_client.test.ts](sdk/typescript/tests/ai_client.test.ts)
- [sdk/typescript/tests/triggers.test.ts](sdk/typescript/tests/triggers.test.ts)

</details>



This document describes the execution context system in the TypeScript SDK. Execution contexts provide handlers with access to execution metadata, service clients, and lifecycle information during reasoner and skill invocations.

For information about defining reasoners and skills, see [Reasoners and Skills](#4.2). For memory operations available through contexts, see [Memory Interface](#4.5). For AI client usage, see [AI Client](#4.4).

---

## Overview

The TypeScript SDK provides three context types that encapsulate execution state and service access:

| Context Type | Purpose | Available To |
|--------------|---------|--------------|
| `ExecutionContext` | Base execution tracking with AsyncLocalStorage | Internal use, propagation |
| `ReasonerContext` | Full service access for AI operations | Reasoner handlers |
| `SkillContext` | Subset of services for deterministic operations | Skill handlers |

Contexts serve as dependency injection containers, providing type-safe access to AI clients, memory interfaces, workflow reporters, and DID systems without requiring explicit parameter passing through nested calls.

**Sources:** [sdk/typescript/src/agent/Agent.ts:29-31](), [sdk/typescript/src/context/ReasonerContext.ts:13-29](), [sdk/typescript/src/context/SkillContext.ts:9-25]()

---

## Context Type Hierarchy

### Service Availability Diagram
```mermaid
graph TB
    ExecutionContext["ExecutionContext<br/>(Base Tracking)"]
    ReasonerContext["ReasonerContext&lt;TInput&gt;<br/>(AI + Services)"]
    SkillContext["SkillContext&lt;TInput&gt;<br/>(Deterministic Services)"]
    
    ExecutionContext --> ReasonerContext
    ExecutionContext --> SkillContext
    
    ReasonerContext --> ai["ai(prompt): Promise&lt;T&gt;"]
    ReasonerContext --> aiStream["aiStream(prompt): AIStream"]
    ReasonerContext --> call["call(target, input)"]
    ReasonerContext --> discover["discover(options)"]
    ReasonerContext --> memory["memory: MemoryInterface"]
    ReasonerContext --> workflow["workflow: WorkflowReporter"]
    ReasonerContext --> did["did: DidInterface"]
    ReasonerContext --> aiClient["aiClient: AIClient"]
    ReasonerContext --> signal["signal: AbortSignal"]
    
    SkillContext --> call2["discover(options)"]
    SkillContext --> memory2["memory: MemoryInterface"]
    SkillContext --> workflow2["workflow: WorkflowReporter"]
    SkillContext --> did2["did: DidInterface"]
```

**Sources:** [sdk/typescript/src/context/ReasonerContext.ts:13-42](), [sdk/typescript/src/context/SkillContext.ts:9-35]()

---

## ExecutionContext

`ExecutionContext` is the internal base context that tracks execution state using Node.js `AsyncLocalStorage`. It enables automatic context propagation through asynchronous call chains without explicit parameter threading.

### Structure

```typescript
class ExecutionContext {
  input: any
  metadata: ExecutionMetadata
  req: express.Request
  res: express.Response
  agent: Agent
  
  static run<T>(context: ExecutionContext, fn: () => Promise<T>): Promise<T>
  static getCurrent(): ExecutionContext | undefined
}
```

### Execution Metadata

The `ExecutionMetadata` interface contains execution tracking identifiers propagated via HTTP headers. The `Agent` class provides a normalization utility to map snake_case headers from the Control Plane to camelCase SDK fields.

| Field | Header | Description |
|-------|--------|-------------|
| `executionId` | `X-Execution-ID` | Unique ID for this invocation |
| `runId` | `X-Run-ID` | Parent run ID (defaults to executionId) |
| `workflowId` | `X-Workflow-ID` | Workflow-level ID (defaults to runId) |
| `sessionId` | `X-Session-ID` | Optional session scope |
| `actorId` | `X-Actor-ID` | Optional actor/user scope |
| `parentExecutionId` | `X-Parent-Execution-ID` | ID of calling execution |
| `callerDid` | `X-Caller-DID` | DID of caller component |
| `targetDid` | `X-Target-DID` | DID of target component |
| `agentNodeDid` | `X-Agent-Node-DID` | DID of agent node |

**Sources:** [sdk/typescript/src/agent/Agent.ts:92-108](), [sdk/typescript/src/context/ExecutionContext.ts:5-10](), [sdk/typescript/src/client/AgentFieldClient.ts:29-44]()

---

## ReasonerContext

`ReasonerContext<TInput>` is the primary context provided to reasoner handlers. It includes all services needed for AI-powered operations and execution lifecycle management.

### Properties

```mermaid
graph LR
    ReasonerContext["ReasonerContext&lt;TInput&gt;"]
    
    ReasonerContext --> input["input: TInput<br/>(typed input data)"]
    ReasonerContext --> metadata["Execution Metadata<br/>(9 fields)"]
    ReasonerContext --> req["req: express.Request"]
    ReasonerContext --> res["res: express.Response"]
    ReasonerContext --> agent["agent: Agent"]
    ReasonerContext --> signal["signal: AbortSignal"]
    
    ReasonerContext --> services["Services"]
    services --> aiClient["aiClient: AIClient"]
    services --> memory["memory: MemoryInterface"]
    services --> workflow["workflow: WorkflowReporter"]
    services --> did["did: DidInterface"]
```

### Key Capabilities

| Property / Method | Type | Purpose |
|----------|------|---------|
| `ai()` | Method | Text generation or structured output with schema validation [sdk/typescript/src/context/ReasonerContext.ts:92-99]() |
| `aiWithTools()` | Method | Autonomous tool calling via discovery loop [sdk/typescript/src/context/ReasonerContext.ts:109-131]() |
| `pause()` | Method | Suspends execution for human-in-the-loop approval [sdk/typescript/src/context/ReasonerContext.ts:151-158]() |
| `signal` | `AbortSignal` | Short-circuits work if the Control Plane cancels the execution [sdk/typescript/src/context/ReasonerContext.ts:34-42]() |
| `memory` | `MemoryInterface` | Scoped KV and Vector storage [sdk/typescript/src/context/ReasonerContext.ts:31]() |

### Helper Methods

[sdk/typescript/src/context/ReasonerContext.ts:92-162]()

```typescript
// AI generation with automatic schema validation
ai<T>(prompt: string, options: AIRequestOptions & { schema: ZodSchema<T> }): Promise<T>

// Streaming AI responses
aiStream(prompt: string, options?: AIRequestOptions): Promise<AIStream>

// Cross-agent invocation
call(target: string, input: any): Promise<any>

// Capability discovery
discover(options?: DiscoveryOptions): Promise<DiscoveryResult>
```

**Sources:** [sdk/typescript/src/context/ReasonerContext.ts:13-179](), [sdk/typescript/src/agent/Agent.ts:133-144]()

---

## SkillContext

`SkillContext<TInput>` is provided to skill handlers. Skills are deterministic operations, so `SkillContext` excludes AI client access and complex workflow orchestration methods like `pause()`.

### Differences from ReasonerContext

| Feature | ReasonerContext | SkillContext |
|---------|----------------|--------------|
| `aiClient` property | ✅ Yes | ❌ No |
| `ai()` method | ✅ Yes | ❌ No |
| `aiWithTools()` | ✅ Yes | ❌ No |
| `pause()` method | ✅ Yes | ❌ No |
| `call()` method | ✅ Yes | ❌ No |
| `signal` (Abort) | ✅ Yes | ✅ Yes |
| `memory` property | ✅ Yes | ✅ Yes |
| `workflow` property | ✅ Yes | ✅ Yes |
| `did` property | ✅ Yes | ✅ Yes |

**Sources:** [sdk/typescript/src/context/SkillContext.ts:9-54]()

---

## Context Lifecycle

### Request Processing Flow

```mermaid
sequenceDiagram
    participant Client as "Control Plane / Client"
    participant Agent as "Agent.ts"
    participant ExecutionContext as "ExecutionContext.ts"
    participant ReasonerContext as "ReasonerContext.ts"
    participant Handler as "User Handler"
    
    Client->>Agent: POST /api/v1/execute/:target
    Agent->>Agent: normalizeExecutionContext(headers)
    Note over Agent: Extract X-Execution-ID, X-Workflow-ID, etc.
    
    Agent->>ExecutionContext: new ExecutionContext(...)
    Agent->>ReasonerContext: new ReasonerContext(...)
    
    Agent->>ExecutionContext: ExecutionContext.run(execCtx, async () => {...})
    Note over ExecutionContext: Establish AsyncLocalStorage scope
    
    ExecutionContext->>Handler: handler(ctx)
    Handler->>ReasonerContext: ctx.ai(prompt)
    Handler->>ReasonerContext: ctx.memory.set(key, value)
    
    Handler-->>ExecutionContext: return result
    ExecutionContext-->>Agent: return result
    Agent-->>Client: 200 OK / 202 Accepted
```

**Sources:** [sdk/typescript/src/agent/Agent.ts:92-108](), [sdk/typescript/src/context/ExecutionContext.ts:17-25]()

### Global Context Access

For code outside handler functions (e.g., utility modules), use `getCurrentContext()` to retrieve the active context from storage:

[sdk/typescript/src/context/ReasonerContext.ts:181-201]()

```typescript
import { getCurrentContext } from '@agentfield/sdk';

export async function logExecutionStep(msg: string) {
  const ctx = getCurrentContext();
  if (ctx) {
    ctx.logger.info(`[${ctx.executionId}] ${msg}`);
  }
}
```

---

## Serverless Context Handling

When deployed to serverless platforms, contexts are created from normalized event structures. The `Agent` provides adapters to convert platform-specific events (AWS Lambda, etc.) into `ServerlessEvent`.

### Metadata Merging

The SDK handles both `camelCase` and `snake_case` variants of execution metadata often found in cross-language (Python/TS) environments:

[sdk/typescript/src/agent/Agent.ts:92-108]()

```typescript
function normalizeExecutionContext(ctx: RawExecutionContext): Partial<ExecutionMetadata> {
  return {
    executionId: ctx.executionId ?? ctx.execution_id,
    runId: ctx.runId ?? ctx.run_id,
    workflowId: ctx.workflowId ?? ctx.workflow_id,
    // ... maps all 9 fields
  };
}
```

**Sources:** [sdk/typescript/src/types/agent.ts:192-208](), [sdk/typescript/src/agent/Agent.ts:92-108]()

---

## Summary of Metadata Headers

| SDK Field | HTTP Header | Internal Payload Key |
|-----------|-------------|----------------------|
| `executionId` | `X-Execution-ID` | `execution_id` |
| `runId` | `X-Run-ID` | `run_id` |
| `workflowId` | `X-Workflow-ID` | `workflow_id` |
| `sessionId` | `X-Session-ID` | `session_id` |
| `actorId` | `X-Actor-ID` | `actor_id` |
| `callerDid` | `X-Caller-DID` | `caller_did` |

**Sources:** [sdk/typescript/src/client/AgentFieldClient.ts:29-44](), [sdk/typescript/src/types/agent.ts:225-250]()

---

# Page: AI Client

# AI Client

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [control-plane/web/client/package-lock.json](control-plane/web/client/package-lock.json)
- [control-plane/web/client/package.json](control-plane/web/client/package.json)
- [control-plane/web/client/pnpm-lock.yaml](control-plane/web/client/pnpm-lock.yaml)
- [control-plane/web/client/src/components/ui/icon-bridge.tsx](control-plane/web/client/src/components/ui/icon-bridge.tsx)
- [control-plane/web/client/src/components/ui/icon.tsx](control-plane/web/client/src/components/ui/icon.tsx)
- [examples/benchmarks/100k-scale/mastra-bench/package-lock.json](examples/benchmarks/100k-scale/mastra-bench/package-lock.json)
- [examples/benchmarks/100k-scale/mastra-bench/package.json](examples/benchmarks/100k-scale/mastra-bench/package.json)
- [examples/python_agent_nodes/rag_evaluation/ui/package-lock.json](examples/python_agent_nodes/rag_evaluation/ui/package-lock.json)
- [examples/python_agent_nodes/rag_evaluation/ui/package.json](examples/python_agent_nodes/rag_evaluation/ui/package.json)
- [sdk/typescript/package-lock.json](sdk/typescript/package-lock.json)
- [sdk/typescript/src/agent/Agent.ts](sdk/typescript/src/agent/Agent.ts)
- [sdk/typescript/src/ai/AIClient.ts](sdk/typescript/src/ai/AIClient.ts)
- [sdk/typescript/src/client/AgentFieldClient.ts](sdk/typescript/src/client/AgentFieldClient.ts)
- [sdk/typescript/src/context/ReasonerContext.ts](sdk/typescript/src/context/ReasonerContext.ts)
- [sdk/typescript/src/index.ts](sdk/typescript/src/index.ts)
- [sdk/typescript/src/router/AgentRouter.ts](sdk/typescript/src/router/AgentRouter.ts)
- [sdk/typescript/src/triggers/factories.ts](sdk/typescript/src/triggers/factories.ts)
- [sdk/typescript/src/triggers/index.ts](sdk/typescript/src/triggers/index.ts)
- [sdk/typescript/src/triggers/types.ts](sdk/typescript/src/triggers/types.ts)
- [sdk/typescript/src/types/agent.ts](sdk/typescript/src/types/agent.ts)
- [sdk/typescript/src/types/reasoner.ts](sdk/typescript/src/types/reasoner.ts)
- [sdk/typescript/tests/agent.test.ts](sdk/typescript/tests/agent.test.ts)
- [sdk/typescript/tests/ai_client.test.ts](sdk/typescript/tests/ai_client.test.ts)
- [sdk/typescript/tests/triggers.test.ts](sdk/typescript/tests/triggers.test.ts)

</details>



The `AIClient` class in the TypeScript SDK provides a unified interface for interacting with Large Language Models (LLMs) from multiple providers. It handles text generation, structured output extraction, streaming responses, and embedding generation. The client abstracts provider-specific APIs behind a consistent interface and includes built-in rate limiting and retry logic.

For AI configuration at the agent level, see [AI Configuration](#10.2). For using AI within reasoners, see [Reasoners and Skills](#4.2).

---

## Overview

The `AIClient` class is located at [sdk/typescript/src/ai/AIClient.ts:76-332]() and serves as the primary interface for all AI operations in TypeScript agents. It is initialized within the `Agent` constructor at [sdk/typescript/src/agent/Agent.ts:160]() and exposed to execution contexts.

Key capabilities include:
- **Text generation**: Synchronous and streaming responses.
- **Structured output**: Type-safe extraction with Zod schemas and automatic JSON repair.
- **Embeddings**: Vector generation for RAG systems via `embed()` and `embedMany()`.
- **Multi-provider**: Unified API across OpenAI, Anthropic, Google, and others.
- **Resilience**: Automatic rate limit handling with exponential backoff and circuit breakers.

**Sources:** [sdk/typescript/src/ai/AIClient.ts:76-92](), [sdk/typescript/src/agent/Agent.ts:160-160]()

---

## Provider Architecture

### Supported Providers

The `AIClient` supports the following providers via dedicated AI SDK packages:

| Provider | Package | Models | Embeddings |
|----------|---------|--------|------------|
| `openai` | `@ai-sdk/openai` | GPT-4, GPT-3.5, etc. | ✓ |
| `anthropic` | `@ai-sdk/anthropic` | Claude 3.5, Claude 3 | ✗ |
| `google` | `@ai-sdk/google` | Gemini 2.0, Gemini 1.5 | ✓ |
| `mistral` | `@ai-sdk/mistral` | Mistral Large, etc. | ✓ |
| `groq` | `@ai-sdk/groq` | Llama 3.1, Mixtral | ✗ |
| `xai` | `@ai-sdk/xai` | Grok | ✗ |
| `deepseek` | `@ai-sdk/deepseek` | DeepSeek Chat | ✗ |
| `cohere` | `@ai-sdk/cohere` | Command R+ | ✓ |
| `openrouter` | `@ai-sdk/openai` (compatible) | 100+ models | ✓ |
| `ollama` | `@ai-sdk/openai` (compatible) | Local models | ✓ |

**Sources:** [sdk/typescript/src/ai/AIClient.ts:168-256](), [sdk/typescript/package-lock.json:12-20](), [sdk/typescript/tests/ai_client.test.ts:223-228]()

### Provider Factory Pattern

```mermaid
graph TB
    AIClient["AIClient"]
    buildModel["buildModel(options)"]
    buildEmbeddingModel["buildEmbeddingModel(options)"]
    
    AIClient --> buildModel
    AIClient --> buildEmbeddingModel
    
    buildModel --> providerSwitch{"provider type"}
    
    providerSwitch -->|"openai"| createOpenAI["createOpenAI()"]
    providerSwitch -->|"anthropic"| createAnthropic["createAnthropic()"]
    providerSwitch -->|"google"| createGoogle["createGoogleGenerativeAI()"]
    providerSwitch -->|"mistral"| createMistral["createMistral()"]
    providerSwitch -->|"groq"| createGroq["createGroq()"]
    providerSwitch -->|"xai"| createXai["createXai()"]
    providerSwitch -->|"deepseek"| createDeepSeek["createDeepSeek()"]
    providerSwitch -->|"cohere"| createCohere["createCohere()"]
    providerSwitch -->|"openrouter"| openrouterOpenAI["createOpenAI()<br/>baseURL: openrouter.ai"]
    providerSwitch -->|"ollama"| ollamaOpenAI["createOpenAI()<br/>baseURL: localhost:11434"]
    
    createOpenAI --> modelInstance["model(modelName)"]
    createAnthropic --> modelInstance
    createGoogle --> modelInstance
    createMistral --> modelInstance
    createGroq --> modelInstance
    createXai --> modelInstance
    createDeepSeek --> modelInstance
    createCohere --> modelInstance
    openrouterOpenAI --> modelInstance
    ollamaOpenAI --> modelInstance
    
    buildEmbeddingModel --> embeddingSwitch{"provider type"}
    embeddingSwitch -->|"openai/openrouter/ollama"| embeddingFn["openai.embedding(modelName)"]
    embeddingSwitch -->|"google"| textEmbeddingModel["google.textEmbeddingModel(modelName)"]
    embeddingSwitch -->|"mistral"| mistralEmbedding["mistral.textEmbeddingModel(modelName)"]
    embeddingSwitch -->|"cohere"| cohereEmbedding["cohere.textEmbeddingModel(modelName)"]
    embeddingSwitch -->|"anthropic/xai/deepseek/groq"| throwError["throw Error<br/>'not supported'"]
```

**Diagram: Provider Factory Pattern**

The `buildModel()` method at [sdk/typescript/src/ai/AIClient.ts:168-256]() creates provider-specific model instances. OpenRouter and Ollama use OpenAI-compatible endpoints. The `buildEmbeddingModel()` method at [sdk/typescript/src/ai/AIClient.ts:258-310]() handles embedding model creation, with four providers (Anthropic, xAI, DeepSeek, Groq) explicitly blocking embedding requests.

**Sources:** [sdk/typescript/src/ai/AIClient.ts:168-310](), [sdk/typescript/tests/ai_client.test.ts:101-220]()

---

## Text Generation

### Basic Generation

The `generate()` method provides synchronous text generation:

```typescript
async generate(prompt: string, options?: AIRequestOptions): Promise<string>
async generate<T>(prompt: string, options: AIRequestOptions & { schema: ZodSchema<T> }): Promise<T>
```

The method has two overloads: one for plain text responses and one for structured output with a Zod schema.

**Implementation Flow:**

```mermaid
sequenceDiagram
    participant Caller
    participant AIClient
    participant buildModel
    participant RateLimiter
    participant generateText
    participant Provider
    
    Caller->>AIClient: generate(prompt, options)
    AIClient->>buildModel: buildModel(options)
    buildModel->>Provider: createProvider(config)
    Provider-->>buildModel: model instance
    buildModel-->>AIClient: model
    
    AIClient->>AIClient: Check if schema provided
    
    alt No schema (text mode)
        AIClient->>RateLimiter: withRateLimitRetry(() => ...)
        RateLimiter->>generateText: generateText({ model, prompt, ... })
        generateText->>Provider: API call
        Provider-->>generateText: response
        generateText-->>RateLimiter: { text: "..." }
        RateLimiter-->>AIClient: response
        AIClient-->>Caller: response.text
    else Schema provided (structured)
        AIClient->>RateLimiter: withRateLimitRetry(() => ...)
        RateLimiter->>generateText: generateObject({ model, prompt, schema, ... })
        generateText->>Provider: API call with schema
        Provider-->>generateText: structured response
        generateText-->>RateLimiter: { object: {...} }
        RateLimiter-->>AIClient: response
        AIClient-->>Caller: response.object as T
    end
```

**Diagram: Text Generation Flow**

The implementation at [sdk/typescript/src/ai/AIClient.ts:93-131]() uses the `ai` SDK's `generateText()` function for plain text and `generateObject()` for structured output.

**Sources:** [sdk/typescript/src/ai/AIClient.ts:93-131](), [sdk/typescript/src/context/ReasonerContext.ts:92-99]()

### Request Options

The `AIRequestOptions` interface at [sdk/typescript/src/ai/AIClient.ts:53-67]() defines available configuration:

```typescript
interface AIRequestOptions {
  system?: string;              // System prompt
  schema?: ZodSchema<any>;      // For structured output
  model?: string;               // Override model
  temperature?: number;         // Sampling temperature
  maxTokens?: number;           // Max output tokens
  provider?: AIConfig['provider']; // Override provider
  mode?: 'auto' | 'json' | 'tool'; // Structured output mode
}
```

The `mode` option controls how structured output is generated:
- `'auto'`: Provider chooses (default, uses tool calling).
- `'json'`: Forces JSON mode (better compatibility).
- `'tool'`: Explicitly uses tool/function calling.

The default mode is `'json'` for better cross-provider compatibility, as noted at [sdk/typescript/src/ai/AIClient.ts:100-102]().

**Sources:** [sdk/typescript/src/ai/AIClient.ts:53-67](), [sdk/typescript/src/ai/AIClient.ts:98-117]()

---

## Structured Output

### JSON Repair

The `AIClient` includes automatic JSON repair for malformed responses:

```mermaid
graph LR
    ModelResponse["Model Response<br/>Raw Text"]
    repairJsonText["repairJsonText(text)"]
    strip1["Strip markdown<br/>code blocks"]
    extract["Extract JSON<br/>object/array"]
    removeCommas["Remove trailing<br/>commas"]
    validate["JSON.parse()<br/>validate"]
    
    ModelResponse --> repairJsonText
    repairJsonText --> strip1
    strip1 --> extract
    extract --> removeCommas
    removeCommas --> validate
    
    validate -->|valid| return["Return<br/>cleaned JSON"]
    validate -->|invalid| null["Return null"]
```

**Diagram: JSON Repair Pipeline**

The `repairJsonText()` function at [sdk/typescript/src/ai/AIClient.ts:26-51]() handles common issues:
- Strips markdown code blocks (````json ... ``` or ``` ... ````).
- Extracts JSON from surrounding text.
- Removes trailing commas before `}` or `]`.
- Validates with `JSON.parse()`.

This function is passed to `generateObject()` as `experimental_repairText` at [sdk/typescript/src/ai/AIClient.ts:113]().

**Sources:** [sdk/typescript/src/ai/AIClient.ts:26-51](), [sdk/typescript/src/ai/AIClient.ts:98-117]()

### Type Safety

Structured output uses Zod schemas for runtime validation and compile-time type inference. The `ZodSchema` type is defined at [sdk/typescript/src/ai/AIClient.ts:20]():

```typescript
export type ZodSchema<T> = z.Schema<T, z.ZodTypeDef, any>;
```

When a schema is provided, the `generate()` method returns the typed object directly, with the return type inferred from the schema.

**Sources:** [sdk/typescript/src/ai/AIClient.ts:20](), [sdk/typescript/src/ai/AIClient.ts:93-95]()

---

## Streaming

### Stream Interface

The `stream()` method provides token-by-token streaming:

```typescript
async stream(prompt: string, options?: AIRequestOptions): Promise<AIStream>

type AIStream = AsyncIterable<string>
```

The returned `AIStream` is an async iterable that yields text chunks as they arrive from the provider.

**Implementation:**

```mermaid
graph TB
    stream["stream(prompt, options)"]
    buildModel["buildModel(options)"]
    streamText["streamText({ model, prompt, ... })"]
    textStream["streamResult.textStream"]
    
    stream --> buildModel
    buildModel --> streamText
    streamText --> textStream
    textStream --> return["return AsyncIterable<string>"]
```

**Diagram: Streaming Flow**

The implementation at [sdk/typescript/src/ai/AIClient.ts:133-144]() uses the AI SDK's `streamText()` function and returns its `textStream` property.

**Usage in Context:**

The `ReasonerContext` exposes streaming via the `aiStream()` method at [sdk/typescript/src/context/ReasonerContext.ts:133-135]():

```typescript
aiStream(prompt: string, options?: AIRequestOptions): Promise<AIStream> {
  return this.aiClient.stream(prompt, options);
}
```

**Sources:** [sdk/typescript/src/ai/AIClient.ts:69](), [sdk/typescript/src/ai/AIClient.ts:133-144](), [sdk/typescript/src/context/ReasonerContext.ts:133-135]()

---

## Embeddings

### Embedding Methods

The `AIClient` provides two embedding methods at [sdk/typescript/src/ai/AIClient.ts:146-166]():

```typescript
async embed(value: string, options?: AIEmbeddingOptions): Promise<number[]>
async embedMany(values: string[], options?: AIEmbeddingOptions): Promise<number[][]>
```

Where `AIEmbeddingOptions` is defined at [sdk/typescript/src/ai/AIClient.ts:71-74]():

```typescript
interface AIEmbeddingOptions {
  model?: string;
  provider?: AIConfig['provider'];
}
```

### Provider Support

```mermaid
graph TB
    embed["embed(value, options)"]
    buildEmbeddingModel["buildEmbeddingModel(options)"]
    
    embed --> buildEmbeddingModel
    
    buildEmbeddingModel --> check{"Provider supports<br/>embeddings?"}
    
    check -->|No| throw["throw Error:<br/>'not supported for<br/>anthropic/xai/deepseek/groq'"]
    
    check -->|Yes| providerType{"Provider type"}
    
    providerType -->|"openai/openrouter/ollama"| openaiEmbed["openai.embedding(model)"]
    providerType -->|"google"| googleEmbed["google.textEmbeddingModel(model)"]
    providerType -->|"mistral"| mistralEmbed["mistral.textEmbeddingModel(model)"]
    providerType -->|"cohere"| cohereEmbed["cohere.textEmbeddingModel(model)"]
    
    openaiEmbed --> aiEmbed["embed({ model, value })"]
    googleEmbed --> aiEmbed
    mistralEmbed --> aiEmbed
    cohereEmbed --> aiEmbed
    
    aiEmbed --> withRetry["withRateLimitRetry()"]
    withRetry --> result["return embedding<br/>as number[]"]
```

**Diagram: Embedding Generation Flow**

The embedding check at [sdk/typescript/src/ai/AIClient.ts:263-266]() explicitly blocks providers that do not support standard embedding APIs.

Default embedding models:
- **OpenAI/OpenRouter/Ollama**: `text-embedding-3-small` [sdk/typescript/src/ai/AIClient.ts:259-260]().
- **Google/Mistral/Cohere**: Uses the model specified in config or passed in options.

**Sources:** [sdk/typescript/src/ai/AIClient.ts:146-166](), [sdk/typescript/src/ai/AIClient.ts:258-310](), [sdk/typescript/tests/ai_client.test.ts:222-298]()

---

## Rate Limiting

### StatelessRateLimiter

The `AIClient` integrates with the `StatelessRateLimiter` class for automatic retry on rate limit errors.

```mermaid
graph TB
    execute["API Call<br/>(generate/embed)"]
    withRetry["withRateLimitRetry(fn)"]
    limiter["StatelessRateLimiter"]
    executeWithRetry["executeWithRetry(fn)"]
    
    execute --> withRetry
    withRetry --> check{"enableRateLimitRetry?"}
    
    check -->|false| directCall["fn()"]
    check -->|true| limiter
    
    limiter --> executeWithRetry
    executeWithRetry --> attempt["Attempt API call"]
    
    attempt -->|Success| return["Return result"]
    attempt -->|Rate limit error| backoff["Exponential backoff"]
    backoff --> circuitCheck{"Circuit breaker<br/>threshold reached?"}
    
    circuitCheck -->|No| retry["Retry after delay"]
    circuitCheck -->|Yes| openCircuit["Open circuit<br/>for timeout period"]
    
    retry --> attempt
    openCircuit --> waitTimeout["Wait for<br/>circuit breaker timeout"]
    waitTimeout --> attempt
```

**Diagram: Rate Limiting and Retry Flow**

The retry logic is implemented at [sdk/typescript/src/ai/AIClient.ts:326-331](). It uses the `executeWithRetry` method of the limiter.

### Configuration

Rate limiter configuration is set in the `AIConfig` at [sdk/typescript/src/types/agent.ts:77-83]():

| Option | Default | Description |
|--------|---------|-------------|
| `enableRateLimitRetry` | `true` | Enable automatic retry. |
| `rateLimitMaxRetries` | `20` | Maximum retry attempts. |
| `rateLimitBaseDelay` | `1.0` | Initial delay (seconds). |
| `rateLimitMaxDelay` | `300.0` | Maximum delay (seconds). |
| `rateLimitJitterFactor` | `0.25` | Random jitter (0-1). |
| `rateLimitCircuitBreakerThreshold` | `10` | Failures before circuit opens. |
| `rateLimitCircuitBreakerTimeout` | `300` | Circuit open duration (seconds). |

**Sources:** [sdk/typescript/src/ai/AIClient.ts:312-331](), [sdk/typescript/src/types/agent.ts:77-83]()

---

## Configuration

### AIConfig Interface

The `AIClient` is configured via the `AIConfig` interface defined at [sdk/typescript/src/types/agent.ts:56-84]().

### Default Values

The constructor at [sdk/typescript/src/ai/AIClient.ts:80-91]() applies defaults using the spread operator. Provider and model defaults are applied lazily at request time in `buildModel()` and `buildEmbeddingModel()`.

**Sources:** [sdk/typescript/src/ai/AIClient.ts:80-91](), [sdk/typescript/src/ai/AIClient.ts:169-170](), [sdk/typescript/src/ai/AIClient.ts:259-260]()

---

## Usage in Contexts

### ReasonerContext Integration

The `ReasonerContext` class provides convenient access to AI operations:

```mermaid
graph TB
    ReasonerContext["ReasonerContext<TInput>"]
    ai["ai(prompt, options)"]
    aiStream["aiStream(prompt, options)"]
    
    AIClient["AIClient"]
    generate["generate(prompt, options)"]
    stream["stream(prompt, options)"]
    
    Agent["Agent"]
    
    ReasonerContext --> Agent
    ReasonerContext --> ai
    ReasonerContext --> aiStream
    
    ai --> generate
    aiStream --> stream
```

**Diagram: ReasonerContext-AIClient Connection**

The `ReasonerContext` at [sdk/typescript/src/context/ReasonerContext.ts:92-135]() exposes `ai()` and `aiStream()` which delegate to the `aiClient` property.

**Sources:** [sdk/typescript/src/context/ReasonerContext.ts:92-135](), [sdk/typescript/src/agent/Agent.ts:160-160]()

### Tool Calling Integration

The `ReasonerContext` also provides `aiWithTools()` at [sdk/typescript/src/context/ReasonerContext.ts:109-131](), which uses the `AIClient` to perform automated discovery and multi-turn tool execution.

**Sources:** [sdk/typescript/src/context/ReasonerContext.ts:109-131](), [sdk/typescript/src/ai/ToolCalling.ts:10-10]()

---

# Page: Memory Interface

# Memory Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [sdk/python/agentfield/memory.py](sdk/python/agentfield/memory.py)
- [sdk/python/agentfield/memory_events.py](sdk/python/agentfield/memory_events.py)
- [sdk/python/tests/test_memory_scope_kwargs.py](sdk/python/tests/test_memory_scope_kwargs.py)
- [sdk/typescript/src/agent/Agent.ts](sdk/typescript/src/agent/Agent.ts)
- [sdk/typescript/src/ai/AIClient.ts](sdk/typescript/src/ai/AIClient.ts)
- [sdk/typescript/src/client/AgentFieldClient.ts](sdk/typescript/src/client/AgentFieldClient.ts)
- [sdk/typescript/src/context/ReasonerContext.ts](sdk/typescript/src/context/ReasonerContext.ts)
- [sdk/typescript/src/context/SkillContext.ts](sdk/typescript/src/context/SkillContext.ts)
- [sdk/typescript/src/index.ts](sdk/typescript/src/index.ts)
- [sdk/typescript/src/memory/MemoryClient.ts](sdk/typescript/src/memory/MemoryClient.ts)
- [sdk/typescript/src/memory/MemoryEventClient.ts](sdk/typescript/src/memory/MemoryEventClient.ts)
- [sdk/typescript/src/memory/MemoryInterface.ts](sdk/typescript/src/memory/MemoryInterface.ts)
- [sdk/typescript/src/router/AgentRouter.ts](sdk/typescript/src/router/AgentRouter.ts)
- [sdk/typescript/src/triggers/factories.ts](sdk/typescript/src/triggers/factories.ts)
- [sdk/typescript/src/triggers/index.ts](sdk/typescript/src/triggers/index.ts)
- [sdk/typescript/src/triggers/types.ts](sdk/typescript/src/triggers/types.ts)
- [sdk/typescript/src/types/agent.ts](sdk/typescript/src/types/agent.ts)
- [sdk/typescript/src/types/reasoner.ts](sdk/typescript/src/types/reasoner.ts)
- [sdk/typescript/tests/agent.test.ts](sdk/typescript/tests/agent.test.ts)
- [sdk/typescript/tests/ai_client.test.ts](sdk/typescript/tests/ai_client.test.ts)
- [sdk/typescript/tests/memory_and_discovery.test.ts](sdk/typescript/tests/memory_and_discovery.test.ts)
- [sdk/typescript/tests/memory_event_client.test.ts](sdk/typescript/tests/memory_event_client.test.ts)
- [sdk/typescript/tests/triggers.test.ts](sdk/typescript/tests/triggers.test.ts)
- [tests/functional/agents/memory_events_decorator_agent.py](tests/functional/agents/memory_events_decorator_agent.py)
- [tests/functional/tests/test_memory_events.py](tests/functional/tests/test_memory_events.py)

</details>



This page documents the TypeScript SDK's memory interface, which provides persistent key-value storage with automatic scoping, hierarchical fallback, and vector operations for RAG. The memory system enables agents to share state across distributed executions while maintaining isolation through four-tier scoping (workflow → session → actor → global).

For information about the Python memory interface, see [3.6](). For the underlying control plane memory storage implementation, see [7]().

---

## Core Concepts

The memory interface operates on a four-tier scoping hierarchy defined in the TypeScript SDK types [sdk/typescript/src/types/agent.ts:91]():

| Scope | Description | Typical Lifetime | Isolation Level |
|-------|-------------|------------------|-----------------|
| `workflow` | Single workflow execution | Minutes to hours | Highest - workflow-specific |
| `session` | User or conversation session | Hours to days | Session-specific |
| `actor` | Individual agent or user | Days to weeks | Actor-specific |
| `global` | Shared across all agents | Persistent | Lowest - system-wide |

**Hierarchical Lookup**: When retrieving data with `get()`, the system resolves values from most specific to least specific: `workflow -> session -> actor -> global`. Values in narrower scopes override broader scopes for reads [sdk/python/agentfield/memory.py:49-56]().

**Context Propagation**: Memory operations automatically include execution context (workflow ID, session ID, actor ID) from headers propagated through the control plane [sdk/typescript/src/memory/MemoryClient.ts:52-75]().

Sources: [sdk/typescript/src/types/agent.ts:91](), [sdk/typescript/src/memory/MemoryClient.ts:52-75](), [sdk/python/agentfield/memory.py:4-64]()

---

## Class Architecture

The TypeScript memory system is built on a layered architecture that bridges high-level reasoner contexts to low-level HTTP and WebSocket clients.

```mermaid
graph TB
    subgraph "Context Layer"
        ReasonerCtx["ReasonerContext<br/>(ctx.memory)"]
    end
    
    subgraph "Interface Layer"
        MemInterface["MemoryInterface<br/>(Scoped Storage API)"]
    end
    
    subgraph "Client Layer"
        MemClient["MemoryClient<br/>(HTTP Operations)"]
        EventClient["MemoryEventClient<br/>(WebSocket & History)"]
    end
    
    subgraph "Control Plane Space"
        API_KV["/api/v1/memory/set<br/>/api/v1/memory/get"]
        API_Vector["/api/v1/memory/vector/search"]
        API_WS["/api/v1/memory/events/ws"]
    end
    
    ReasonerCtx --> MemInterface
    MemInterface --> MemClient
    MemInterface --> EventClient
    MemClient --> API_KV
    MemClient --> API_Vector
    EventClient --> API_WS
```

### Key Classes

| Class | Responsibility | File |
|-------|----------------|------|
| `MemoryInterface` | Provides the developer-facing API for scoped access and watching. | [sdk/typescript/src/memory/MemoryInterface.ts]() |
| `MemoryClient` | Handles low-level HTTP requests for KV and Vector operations. | [sdk/typescript/src/memory/MemoryClient.ts:117]() |
| `MemoryEventClient` | Manages WebSocket connections for real-time change notifications. | [sdk/typescript/src/memory/MemoryEventClient.ts:13]() |
| `MemoryClientBase` | Shared logic for header sanitization and scope-to-header mapping. | [sdk/typescript/src/memory/MemoryClientBase.ts:38]() |

Sources: [sdk/typescript/src/memory/MemoryClient.ts:38-117](), [sdk/typescript/src/memory/MemoryEventClient.ts:13](), [sdk/typescript/src/context/ReasonerContext.ts:84]()

---

## Memory Operations

### Key-Value Storage

The `MemoryClient` implements standard KV operations. It automatically maps scopes to specific `X-` headers to ensure the control plane routes data to the correct storage partition.

```mermaid
sequenceDiagram
    participant Reasoner as ReasonerContext
    participant Interface as MemoryInterface
    participant Client as MemoryClient
    participant AF as Control Plane
    
    Reasoner->>Interface: ctx.memory.set("key", data)
    Interface->>Client: set("key", data, { scope: "workflow" })
    Client->>Client: buildHeaders()
    Note right of Client: Maps scope to X-Workflow-ID
    Client->>AF: POST /api/v1/memory/set
    AF-->>Client: 200 OK
    Client-->>Interface: void
```

**Implementation Details**:
- **`set(key, data, options)`**: Stores JSON-serializable data [sdk/typescript/src/memory/MemoryClient.ts:123-130]().
- **`get<T>(key, options)`**: Retrieves data, returning `undefined` on 404 [sdk/typescript/src/memory/MemoryClient.ts:132-147]().
- **`listKeys(scope, options)`**: Lists keys available in a specific scope [sdk/typescript/src/memory/MemoryClient.ts:158-164]().

Sources: [sdk/typescript/src/memory/MemoryClient.ts:123-164]()

### Vector Operations (RAG)

The interface supports vector embeddings for similarity search, typically used in RAG workflows.

- **`setVector(key, embedding, metadata, options)`**: Stores a vector with optional metadata [sdk/typescript/src/memory/MemoryClient.ts:171-182]().
- **`searchVector(queryEmbedding, options)`**: Performs a similarity search. Supports `topK` and metadata `filters` [sdk/typescript/src/memory/MemoryClient.ts:193-205]().

Sources: [sdk/typescript/src/memory/MemoryClient.ts:171-205]()

---

## Scoped Access and Fallback

The `MemoryInterface` allows developers to explicitly target specific scopes or rely on the hierarchical fallback.

```typescript
// Automatic hierarchical lookup (workflow -> session -> actor -> global)
const theme = await ctx.memory.get("theme");

// Explicit scope targeting
await ctx.memory.workflow.set("step_result", 42);
await ctx.memory.session.set("user_mood", "happy");
await ctx.memory.global.set("system_status", "online");
```

### Header Mapping Table
The `MemoryClientBase` resolves these scopes to the following headers during the request [sdk/typescript/src/memory/MemoryClient.ts:52-88]():

| Scope | Header Used | Fallback Scope ID |
|-------|-------------|-------------------|
| `workflow` | `X-Workflow-ID` | `metadata.workflowId` |
| `session` | `X-Session-ID` | `metadata.sessionId` |
| `actor` | `X-Actor-ID` | `metadata.actorId` |
| `global` | (None) | `"global"` |

Sources: [sdk/typescript/src/memory/MemoryClient.ts:52-104](), [sdk/typescript/src/memory/MemoryInterface.ts]()

---

## Memory Events and Watching

Agents can subscribe to real-time memory changes using the `watchMemory` API or the `MemoryEventClient`.

### Real-time Change Notifications

The `MemoryEventClient` establishes a WebSocket connection to the control plane [sdk/typescript/src/memory/MemoryEventClient.ts:26](). It handles automatic reconnection with exponential backoff [sdk/typescript/src/memory/MemoryEventClient.ts:89-100]().

```mermaid
graph LR
    subgraph "Agent Node"
        Agent[Agent Class]
        Watcher["watchMemory('order.*')"]
        Dispatcher[dispatchMemoryEvent]
    end
    
    subgraph "Control Plane"
        WSServer["/api/v1/memory/events/ws"]
    end
    
    WSServer -- "JSON Event" --> Dispatcher
    Dispatcher -- "Pattern Match" --> Watcher
    Watcher -- "Callback" --> ReasonerCode["async (event) => { ... }"]
```

### Pattern Matching
The TypeScript SDK supports wildcard pattern matching for memory keys (e.g., `order.*` matches `order.123`). This is used in the `Agent.watchMemory` method [sdk/typescript/src/agent/Agent.ts:123]().

**Example Usage**:
```typescript
agent.watchMemory('user.preferences.*', async (event) => {
  console.log(`Preference ${event.key} changed to ${event.data}`);
}, { scope: 'session' });
```

### Event History
The `MemoryEventClient.history()` method allows querying past memory events with filters for `patterns`, `since` timestamps, and `scope` [sdk/typescript/src/memory/MemoryEventClient.ts:116-163]().

Sources: [sdk/typescript/src/memory/MemoryEventClient.ts:24-163](), [sdk/typescript/src/agent/Agent.ts:123](), [sdk/typescript/tests/agent.test.ts:64-92]()

---

## Implementation Flow: `ctx.memory.get()`

The following diagram illustrates the data flow from a Reasoner calling `get()` to the Control Plane.

```mermaid
sequenceDiagram
    participant R as Reasoner
    participant RCX as ReasonerContext
    participant MI as MemoryInterface
    participant MC as MemoryClient
    participant AX as Axios Instance
    
    R->>RCX: ctx.memory.get("key")
    RCX->>MI: get("key")
    MI->>MC: get("key", { metadata })
    MC->>MC: buildHeaders(metadata)
    Note over MC: X-Workflow-ID = metadata.workflowId
    MC->>AX: post("/api/v1/memory/get", { key })
    AX-->>MC: { data: { data: "value" } }
    MC-->>MI: "value"
    MI-->>RCX: "value"
    RCX-->>R: "value"
```

Sources: [sdk/typescript/src/context/ReasonerContext.ts:84](), [sdk/typescript/src/memory/MemoryClient.ts:132-147](), [sdk/typescript/src/memory/MemoryClient.ts:52-75]()

---

# Page: AgentRouter

# AgentRouter

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [sdk/typescript/src/agent/Agent.ts](sdk/typescript/src/agent/Agent.ts)
- [sdk/typescript/src/ai/AIClient.ts](sdk/typescript/src/ai/AIClient.ts)
- [sdk/typescript/src/client/AgentFieldClient.ts](sdk/typescript/src/client/AgentFieldClient.ts)
- [sdk/typescript/src/context/ReasonerContext.ts](sdk/typescript/src/context/ReasonerContext.ts)
- [sdk/typescript/src/index.ts](sdk/typescript/src/index.ts)
- [sdk/typescript/src/router/AgentRouter.ts](sdk/typescript/src/router/AgentRouter.ts)
- [sdk/typescript/src/triggers/factories.ts](sdk/typescript/src/triggers/factories.ts)
- [sdk/typescript/src/triggers/index.ts](sdk/typescript/src/triggers/index.ts)
- [sdk/typescript/src/triggers/types.ts](sdk/typescript/src/triggers/types.ts)
- [sdk/typescript/src/types/agent.ts](sdk/typescript/src/types/agent.ts)
- [sdk/typescript/src/types/reasoner.ts](sdk/typescript/src/types/reasoner.ts)
- [sdk/typescript/tests/agent.test.ts](sdk/typescript/tests/agent.test.ts)
- [sdk/typescript/tests/ai_client.test.ts](sdk/typescript/tests/ai_client.test.ts)
- [sdk/typescript/tests/triggers.test.ts](sdk/typescript/tests/triggers.test.ts)

</details>



## Purpose and Scope

The `AgentRouter` class provides a modular approach to organizing agent capabilities (reasoners and skills) by grouping them under common prefixes. It enables code organization through separation of concerns, allowing developers to split large agent implementations into logical submodules while maintaining a unified agent interface. This implementation exists in both the Python and TypeScript SDKs to ensure cross-language consistency in modular agent composition.

For information about defining reasoners, see [4.2 Reasoners and Skills](). For information about defining skills, see [4.2 Reasoners and Skills]().

---

## Core Concepts

### Router as Capability Organizer

An `AgentRouter` functions similarly to FastAPI's `APIRouter` or Express Routers but is specifically designed for organizing agent capabilities:

- **Prefix Scoping**: All reasoners and skills registered on a router inherit a common prefix, separated by an underscore (e.g., `prefix_capabilityName`). [sdk/typescript/src/router/AgentRouter.ts:45-55]()
- **Modular Organization**: Split agent logic into focused routers (e.g., `data_router`, `analysis_router`). [sdk/typescript/tests/agent.test.ts:44-54]()
- **Delegation Pattern**: Routers delegate core functionality (AI client, memory, discovery) to their parent agent once included. [sdk/typescript/src/agent/Agent.ts:146-170]()
- **Tag Propagation**: Tags applied to routers propagate to all capabilities registered on that router. [sdk/typescript/src/router/AgentRouter.ts:15-25]()

**Sources:** [sdk/typescript/src/router/AgentRouter.ts:1-60](), [sdk/typescript/tests/agent.test.ts:44-54]()

---

## Architecture Overview

### Router-Agent Relationship

The following diagram illustrates how the `AgentRouter` bridges the "Natural Language Space" (capability names) to the "Code Entity Space" (class instances and registries).

```mermaid
graph TB
    Agent["Agent Class<br/>(nodeId='research_agent')"]
    Router1["AgentRouter<br/>(prefix='web')"]
    Router2["AgentRouter<br/>(prefix='analysis')"]
    
    R_Registry["ReasonerRegistry"]
    S_Registry["SkillRegistry"]
    
    Agent -->|"includeRouter(Router1)"| Router1
    Agent -->|"includeRouter(Router2)"| Router2
    Agent --> R_Registry
    Agent --> S_Registry
    
    Router1 -->|"registers"| R1["reasoner: 'web_search'"]
    Router1 -->|"registers"| S1["skill: 'web_fetch'"]
    
    Router2 -->|"registers"| R2["reasoner: 'analysis_summarize'"]
    
    R1 -.->|"stored in"| R_Registry
    R2 -.->|"stored in"| R_Registry
    S1 -.->|"stored in"| S_Registry
    
    CP["Control Plane"]
    CP -->|"POST /execute/research_agent.web_search"| Agent
```

**Sources:** [sdk/typescript/src/agent/Agent.ts:113-114](), [sdk/typescript/src/router/AgentRouter.ts:45-60](), [sdk/typescript/tests/agent.test.ts:44-54]()

---

## Creating and Attaching Routers (TypeScript)

### Basic Router Usage

In TypeScript, routers are created using the `AgentRouter` class and attached via `agent.includeRouter()`.

```typescript
import { Agent, AgentRouter } from '@agentfield/sdk';

const agent = new Agent({ nodeId: 'research-agent' });

// Create a router with a prefix
const webRouter = new AgentRouter({ prefix: 'web' });

// Define capabilities on the router
webRouter.reasoner('search', async (ctx) => {
  // Logic here
  return { results: [] };
});

// Include the router in the main agent
agent.includeRouter(webRouter);
```

### Prefix Handling

The `AgentRouter` ensures that prefixes are correctly formatted. When capabilities are registered, the final name is constructed as `${prefix}_${name}`. [sdk/typescript/src/router/AgentRouter.ts:45-55]()

| Router Prefix | Capability Name | Registered Name |
|---------------|-----------------|-----------------|
| `web`         | `search`        | `web_search`    |
| `simulation`  | `run`           | `simulation_run`|

**Sources:** [sdk/typescript/src/router/AgentRouter.ts:1-20](), [sdk/typescript/tests/agent.test.ts:44-54]()

---

## Delegation to Parent Agent

### Property Delegation Flow

Routers act as proxies for the main `Agent` instance. This allows code within a router-defined reasoner to access shared services like the `AIClient` or `MemoryInterface`.

```mermaid
graph LR
    subgraph "Code Entity Space"
        Router["AgentRouter Instance"]
        Agent["Agent Instance"]
        AI["AIClient"]
        Mem["MemoryClient"]
    end

    Router -- "Delegates to" --> Agent
    Agent -- "Owns" --> AI
    Agent -- "Owns" --> Mem
    
    subgraph "Natural Language / API Space"
        AI_Call["ctx.ai()"]
        Mem_Call["ctx.memory.get()"]
    end

    AI_Call --> AI
    Mem_Call --> Mem
```

### Property Mapping

When a router is included in an agent, the agent's services become available to the router's context:

| Router Context Service | Agent Entity | Description |
|------------------------|--------------|-------------|
| `ctx.aiClient` | `agent.aiClient` | Access to LLM providers. [sdk/typescript/src/agent/Agent.ts:117]() |
| `ctx.memory` | `agent.memoryClient` | Scoped KV and vector storage. [sdk/typescript/src/agent/Agent.ts:119]() |
| `ctx.agent` | `agent` | Reference to the parent agent. [sdk/typescript/src/context/ReasonerContext.ts:28]() |

**Sources:** [sdk/typescript/src/agent/Agent.ts:110-145](), [sdk/typescript/src/context/ReasonerContext.ts:13-42]()

---

## Tag Propagation and Metadata

### Router-Level Tags

Tags defined at the `AgentRouter` level are automatically merged with tags defined on individual reasoners or skills. [sdk/typescript/src/router/AgentRouter.ts:15-25]()

```typescript
const secureRouter = new AgentRouter({ 
  prefix: 'secure', 
  tags: ['internal-only'] 
});

secureRouter.reasoner('audit', async (ctx) => { ... }, {
  tags: ['compliance']
});
```

In the example above, the `secure_audit` reasoner will be registered with both `['internal-only', 'compliance']` tags. This metadata is sent to the control plane during the registration phase via `AgentFieldClient.register()`. [sdk/typescript/src/client/AgentFieldClient.ts:170-177]()

**Sources:** [sdk/typescript/src/router/AgentRouter.ts:10-30](), [sdk/typescript/src/client/AgentFieldClient.ts:170-177]()

---

## Cross-Router Communication

Capabilities registered on different routers can communicate using the `ctx.call()` method. The target string must use the full registered name (including the prefix).

```typescript
// Inside a reasoner on 'analysis' router
const webData = await ctx.call('research-agent.web_search', { query: 'AgentField' });
```

The `agent.call()` method handles local routing if the `nodeId` matches the current agent, otherwise it dispatches the request to the control plane. [sdk/typescript/tests/agent.test.ts:56-62]()

**Sources:** [sdk/typescript/src/context/ReasonerContext.ts:137-139](), [sdk/typescript/tests/agent.test.ts:56-62]()

---

## Integration with Triggers

Routers also support the registration of triggers (webhooks or cron schedules) for their reasoners.

```typescript
import { eventTrigger } from '@agentfield/sdk';

webRouter.reasoner('handle_webhook', handler, {
  triggers: [
    eventTrigger({ source: 'github', types: ['push'] })
  ]
});
```

The `triggerToPayload` utility converts these definitions into the format expected by the Control Plane's `/api/v1/nodes/register` endpoint. [sdk/typescript/src/triggers/factories.ts:88-124]()

**Sources:** [sdk/typescript/src/triggers/factories.ts:88-124](), [sdk/typescript/src/types/reasoner.ts:30-45]()

---

# Page: Serverless Handler

# Serverless Handler

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/ts-node-examples/waiting-state/main.ts](examples/ts-node-examples/waiting-state/main.ts)
- [sdk/typescript/src/agent/Agent.ts](sdk/typescript/src/agent/Agent.ts)
- [sdk/typescript/src/agent/cancel.ts](sdk/typescript/src/agent/cancel.ts)
- [sdk/typescript/src/agent/pause.ts](sdk/typescript/src/agent/pause.ts)
- [sdk/typescript/src/ai/AIClient.ts](sdk/typescript/src/ai/AIClient.ts)
- [sdk/typescript/src/client/AgentFieldClient.ts](sdk/typescript/src/client/AgentFieldClient.ts)
- [sdk/typescript/src/context/ReasonerContext.ts](sdk/typescript/src/context/ReasonerContext.ts)
- [sdk/typescript/src/index.ts](sdk/typescript/src/index.ts)
- [sdk/typescript/src/router/AgentRouter.ts](sdk/typescript/src/router/AgentRouter.ts)
- [sdk/typescript/src/triggers/factories.ts](sdk/typescript/src/triggers/factories.ts)
- [sdk/typescript/src/triggers/index.ts](sdk/typescript/src/triggers/index.ts)
- [sdk/typescript/src/triggers/types.ts](sdk/typescript/src/triggers/types.ts)
- [sdk/typescript/src/types/agent.ts](sdk/typescript/src/types/agent.ts)
- [sdk/typescript/src/types/reasoner.ts](sdk/typescript/src/types/reasoner.ts)
- [sdk/typescript/tests/agent.test.ts](sdk/typescript/tests/agent.test.ts)
- [sdk/typescript/tests/agent_async_execution.test.ts](sdk/typescript/tests/agent_async_execution.test.ts)
- [sdk/typescript/tests/agent_pause.test.ts](sdk/typescript/tests/agent_pause.test.ts)
- [sdk/typescript/tests/agent_runtime_paths.test.ts](sdk/typescript/tests/agent_runtime_paths.test.ts)
- [sdk/typescript/tests/ai_client.test.ts](sdk/typescript/tests/ai_client.test.ts)
- [sdk/typescript/tests/triggers.test.ts](sdk/typescript/tests/triggers.test.ts)

</details>



The serverless handler provides a unified interface for deploying AgentField agents to serverless platforms like AWS Lambda, Azure Functions, Google Cloud Functions, Vercel, and Netlify. It handles event normalization, execution context propagation, and capability discovery for serverless environments where agents cannot run long-lived HTTP servers.

For long-running agent deployments using `agent.serve()`, see [TypeScript SDK Agent Class](). For general serverless deployment guidance, see [Serverless Deployment](). For the Python equivalent, see [Serverless Mode]().

---

## Handler Method

The `agent.handler()` method returns an `AgentHandler` function that can be exported as the entry point for serverless functions. It accepts an optional adapter function to transform platform-specific event formats into the normalized `ServerlessEvent` contract.

**Method Signature:**
`handler(adapter?: (event: any, context?: any) => ServerlessEvent): AgentHandler` [[sdk/typescript/src/agent/Agent.ts:123-134]()]

The returned `AgentHandler` has the signature:
[[sdk/typescript/src/types/agent.ts:218-221]()]

```typescript
type AgentHandler = (
  event: ServerlessEvent | http.IncomingMessage,
  res?: http.ServerResponse
) => Promise<ServerlessResponse | void> | ServerlessResponse | void
```

**Sources:** [sdk/typescript/src/agent/Agent.ts:123-134](), [sdk/typescript/src/types/agent.ts:192-208](), [sdk/typescript/src/types/agent.ts:218-221]()

---

## Handler Decision Flow

The handler automatically detects whether it's processing an HTTP request (Vercel/Netlify) or a generic serverless event (AWS Lambda/Cloud Functions) based on the presence of a response object with a `setHeader` method [[sdk/typescript/src/agent/Agent.ts:516-519]()].

**Handler Routing Logic**

```mermaid
graph TD
    Entry["handler(event, res?)"]
    CheckRes{"res provided and<br/>has setHeader method?"}
    HttpPath["handleHttpRequest(event, res)"]
    ExpressApp["Express app<br/>(this.app)"]
    ServerlessPath["handleServerlessEvent(event)"]
    AdapterCheck{"adapter<br/>provided?"}
    ApplyAdapter["normalized = adapter(event)"]
    DirectCast["normalized = event as ServerlessEvent"]
    ProcessEvent["Process normalized event"]
    
    Entry --> CheckRes
    CheckRes -->|Yes| HttpPath
    CheckRes -->|No| ServerlessPath
    HttpPath --> ExpressApp
    ServerlessPath --> AdapterCheck
    AdapterCheck -->|Yes| ApplyAdapter
    AdapterCheck -->|No| DirectCast
    ApplyAdapter --> ProcessEvent
    DirectCast --> ProcessEvent
```

**Sources:** [sdk/typescript/src/agent/Agent.ts:123-134](), [sdk/typescript/src/agent/Agent.ts:516-519](), [sdk/typescript/src/agent/Agent.ts:521-578]()

---

## ServerlessEvent Contract

The `ServerlessEvent` type defines a normalized event structure that abstracts differences between serverless platforms [[sdk/typescript/src/types/agent.ts:192-208]()].

| Field | Type | Description |
|-------|------|-------------|
| `path` | `string` | Request path (e.g., `/execute/summarize`) |
| `httpMethod` | `string` | HTTP method (POST, GET, etc.) |
| `headers` | `Record<string, string>` | HTTP headers for context propagation |
| `target` | `string` | Target reasoner/skill name |
| `reasoner` | `string` | Explicit reasoner name |
| `skill` | `string` | Explicit skill name |
| `type` | `'reasoner' \| 'skill'` | Target type |
| `body` | `any` | Request body (may be string or parsed object) |
| `input` | `any` | Direct input data |
| `executionContext` | `RawExecutionContext` | Execution metadata (camelCase) |

**Sources:** [sdk/typescript/src/types/agent.ts:192-208](), [sdk/typescript/src/types/agent.ts:225-249]()

---

## Adapter Pattern

Adapters transform platform-specific event formats into the `ServerlessEvent` contract [[sdk/typescript/src/types/agent.ts:216-216]()].

**Adapter Function Type:**
`type ServerlessAdapter = (event: any, context?: any) => ServerlessEvent`

**Example AWS Lambda Adapter:**
```typescript
function lambdaAdapter(event: any): ServerlessEvent {
  return {
    path: event.rawPath ?? event.path,
    httpMethod: event.requestContext?.http?.method ?? event.httpMethod,
    headers: event.headers ?? {},
    body: event.body,
    executionContext: {
      executionId: event.headers?.['x-execution-id']
    }
  };
}

export const handler = agent.handler(lambdaAdapter);
```

**Sources:** [sdk/typescript/src/types/agent.ts:216-216](), [sdk/typescript/src/agent/Agent.ts:123-134]()

---

## Event Normalization Pipeline

The handler normalizes incoming events through multiple stages to extract the target reasoner/skill name, input data, and execution metadata [[sdk/typescript/src/agent/Agent.ts:521-578]()].

**Event Processing Pipeline**

```mermaid
graph TB
    RawEvent["ServerlessEvent"]
    ParseBody["normalizeEventBody()"]
    ExtractInvocation["extractInvocationDetails()"]
    BuildMetadata["buildMetadataFromHeaders()"]
    MergeContext["mergeExecutionContext()"]
    ExecuteInvocation["executeInvocation()"]
    
    subgraph "Body Normalization"
        ParseBody
        BodyParsed["Parsed body object"]
    end
    
    subgraph "Invocation Extraction"
        ExtractInvocation
        PathTarget["parsePathTarget()"]
        NormalizeInput["normalizeInputPayload()"]
    end
    
    subgraph "Metadata Building"
        BuildMetadata
        DefaultIds["Generate IDs in buildMetadataFromHeaders"]
    end
    
    RawEvent --> ParseBody
    ParseBody --> BodyParsed
    RawEvent --> ExtractInvocation
    ExtractInvocation --> PathTarget
    ExtractInvocation --> NormalizeInput
    RawEvent --> BuildMetadata
    RawEvent --> MergeContext
    MergeContext --> ExecuteInvocation
    BuildMetadata --> ExecuteInvocation
    NormalizeInput --> ExecuteInvocation
```

**Sources:** [sdk/typescript/src/agent/Agent.ts:580-589](), [sdk/typescript/src/agent/Agent.ts:621-659](), [sdk/typescript/src/agent/Agent.ts:489-514](), [sdk/typescript/src/agent/Agent.ts:591-619]()

---

## Body Normalization

The `normalizeEventBody()` method handles various body formats and ensures the `input` field is properly extracted [[sdk/typescript/src/agent/Agent.ts:580-589]()].

**Normalization Logic:**
1. Parse string body to JSON if needed [[sdk/typescript/src/agent/Agent.ts:582-582]()].
2. If `event.input` is defined but parsed body doesn't have `input`, merge them [[sdk/typescript/src/agent/Agent.ts:585-585]()].
3. Return parsed body object.

**Sources:** [sdk/typescript/src/agent/Agent.ts:580-589]()

---

## Invocation Target Extraction

The `extractInvocationDetails()` method determines which reasoner or skill to invoke by checking multiple sources in priority order [[sdk/typescript/src/agent/Agent.ts:621-659]()].

**Priority Order for Target Name:**
1. Explicit `target` parameter [[sdk/typescript/src/agent/Agent.ts:622-622]()].
2. `parsePathTarget()` from the URL path [[sdk/typescript/src/agent/Agent.ts:627-627]()].
3. Query string parameters (`target`, `reasoner`, `skill`) [[sdk/typescript/src/agent/Agent.ts:631-633]()].
4. Event fields [[sdk/typescript/src/agent/Agent.ts:634-636]()].
5. Body fields [[sdk/typescript/src/agent/Agent.ts:637-639]()].

**Path Parsing:**
The `parsePathTarget()` method extracts targets from URL paths [[sdk/typescript/src/agent/Agent.ts:661-683]()]:
- `/reasoners/{name}` -> `reasoner` [[sdk/typescript/src/agent/Agent.ts:663-663]()]
- `/skills/{name}` -> `skill` [[sdk/typescript/src/agent/Agent.ts:668-668]()]
- `/execute/{name}` -> target name [[sdk/typescript/src/agent/Agent.ts:673-673]()]

**Sources:** [sdk/typescript/src/agent/Agent.ts:621-659](), [sdk/typescript/src/agent/Agent.ts:661-683]()

---

## Execution Context Propagation

Execution metadata flows through serverless invocations via HTTP headers and the `executionContext` field. The handler merges these sources [[sdk/typescript/src/agent/Agent.ts:591-619]()].

**Metadata Mapping:**
The `normalizeExecutionContext()` function maps both camelCase and snake_case fields to the standard `ExecutionMetadata` [[sdk/typescript/src/agent/Agent.ts:92-108]()].

| Header | Metadata Field |
|--------|----------------|
| `X-Execution-ID` | `executionId` |
| `X-Run-ID` | `runId` |
| `X-Workflow-ID` | `workflowId` |
| `X-Caller-DID` | `callerDid` |

**Sources:** [sdk/typescript/src/agent/Agent.ts:92-108](), [sdk/typescript/src/agent/Agent.ts:489-514](), [sdk/typescript/src/agent/Agent.ts:591-619]()

---

## Discovery Endpoint

Serverless agents must expose a `/discover` endpoint. The handler responds to `path === '/discover'` or `action === 'discover'` with the discovery payload [[sdk/typescript/src/agent/Agent.ts:525-530]()].

**Discovery Response Structure:**
The `discoveryPayload()` method generates the JSON response containing registered reasoners and skills [[sdk/typescript/src/agent/Agent.ts:749-757]()].

**Sources:** [sdk/typescript/src/agent/Agent.ts:525-530](), [sdk/typescript/src/agent/Agent.ts:749-757]()

---

## Deployment Types

The `deploymentType` configuration controls how the agent behaves.
- `long_running`: Uses heartbeats and auto-registration [[sdk/typescript/src/agent/Agent.ts:153-153]()].
- `serverless`: Designed for on-demand invocation [[sdk/typescript/src/types/agent.ts:8-8]()].

**Sources:** [sdk/typescript/src/agent/Agent.ts:153-153](), [sdk/typescript/src/types/agent.ts:8-8](), [sdk/typescript/src/types/agent.ts:28-28]()

---

## ServerlessResponse Contract

The handler returns a `ServerlessResponse` object for serverless invocations [[sdk/typescript/src/types/agent.ts:210-214]()].

**Response Structure:**
```typescript
interface ServerlessResponse {
  statusCode: number;
  headers?: Record<string, string>;
  body: any;
}
```

**Sources:** [sdk/typescript/src/types/agent.ts:210-214](), [sdk/typescript/src/agent/Agent.ts:565-577]()

---

# Page: Go SDK

# Go SDK

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/go_agent_nodes/go.mod](examples/go_agent_nodes/go.mod)
- [examples/go_agent_nodes/go.sum](examples/go_agent_nodes/go.sum)
- [sdk/go/agent/agent.go](sdk/go/agent/agent.go)
- [sdk/go/agent/agent_lifecycle.go](sdk/go/agent/agent_lifecycle.go)
- [sdk/go/agent/agent_test.go](sdk/go/agent/agent_test.go)
- [sdk/go/agent/cli.go](sdk/go/agent/cli.go)
- [sdk/go/agent/cli_test.go](sdk/go/agent/cli_test.go)
- [sdk/go/agent/pause.go](sdk/go/agent/pause.go)
- [sdk/go/agent/pause_test.go](sdk/go/agent/pause_test.go)
- [sdk/go/agent/version.go](sdk/go/agent/version.go)
- [sdk/go/ai/tool_calling.go](sdk/go/ai/tool_calling.go)
- [sdk/go/ai/tool_calling_test.go](sdk/go/ai/tool_calling_test.go)
- [sdk/go/go.mod](sdk/go/go.mod)
- [sdk/go/go.sum](sdk/go/go.sum)
- [sdk/go/harness/claudecode.go](sdk/go/harness/claudecode.go)
- [sdk/go/harness/coverage_branches_test.go](sdk/go/harness/coverage_branches_test.go)
- [sdk/go/harness/coverage_helpers_test.go](sdk/go/harness/coverage_helpers_test.go)
- [sdk/go/harness/parity_test.go](sdk/go/harness/parity_test.go)
- [sdk/go/harness/provider.go](sdk/go/harness/provider.go)
- [sdk/go/harness/result.go](sdk/go/harness/result.go)
- [sdk/go/harness/runner.go](sdk/go/harness/runner.go)
- [sdk/go/harness/runner_test.go](sdk/go/harness/runner_test.go)
- [sdk/go/harness/schema.go](sdk/go/harness/schema.go)

</details>



## Purpose and Scope

The Go SDK provides a robust, high-performance interface for building AgentField agents in Go. Unlike the Python and TypeScript SDKs which often focus on high-level AI abstractions, the Go SDK provides a comprehensive set of tools for building full-featured agents, including **Reasoners**, **Skills**, and advanced **Harness** orchestration for autonomous coding tasks.

**Related pages:**
- For detailed information on initializing agents, see [Agent Initialization](#5.1)
- For skill and reasoner registration patterns, see [Registering Skills](#5.2)

---

## Architecture Overview

The Go SDK implements the AgentField agent-as-service model. An `Agent` instance manages its own HTTP server to receive execution requests and a background client to maintain connectivity with the Control Plane.

### Bridge: Natural Language to Code Entity Space

The following diagram maps the logical concepts of an agent to the specific Go types and fields used in the SDK.

```mermaid
graph TD
    subgraph "Natural Language Space"
        AgentConcept["Agent Entity"]
        CapabilityConcept["Agent Capabilities"]
        ContextConcept["Execution Context"]
    end

    subgraph "Code Entity Space (sdk/go/agent)"
        AgentStruct["struct Agent"]
        ConfigStruct["struct Config"]
        ReasonerStruct["struct Reasoner"]
        ExecContext["struct ExecutionContext"]
    end

    AgentConcept --- AgentStruct
    CapabilityConcept --- ReasonerStruct
    ContextConcept --- ExecContext

    AgentStruct -->|"[agent.go:234]"| ConfigStruct
    AgentStruct -->|"[agent.go:240]"| ReasonerStruct
    ReasonerStruct -->|"[agent.go:124]"| HandlerFunc["type HandlerFunc"]
```
**Sources:** [sdk/go/agent/agent.go:121-153](), [sdk/go/agent/agent.go:233-260](), [sdk/go/agent/agent.go:33-51]()

### System Interaction Diagram

This diagram illustrates how the `Agent` struct interacts with the `Control Plane` via the `client.Client`.

```mermaid
sequenceDiagram
    participant App as "main.go"
    participant Agent as "agent.Agent [agent.go]"
    participant Client as "client.Client [client/client.go]"
    participant CP as "Control Plane"

    App->>Agent: New(Config) [agent.go:264]
    App->>Agent: RegisterReasoner(name, handler) [agent.go:374]
    App->>Agent: Initialize(ctx) [agent_lifecycle.go:20]
    Agent->>Client: RegisterNode(req) [client/client.go:62]
    Client->>CP: POST /api/v1/nodes
    CP-->>Agent: NodeRegistrationResponse
    
    loop Lease Loop [agent_lifecycle.go:120]
        Agent->>Client: RefreshLease(nodeID)
        Client->>CP: POST /api/v1/nodes/{id}/status
    end

    CP->>Agent: POST /execute (Execution Request)
    Agent->>Agent: handleExecution(w, r) [agent.go:731]
    Agent->>App: Invoke HandlerFunc [agent.go:58]
    App-->>Agent: Result
    Agent-->>CP: JSON Response
```
**Sources:** [sdk/go/agent/agent.go:264-340](), [sdk/go/agent/agent.go:731-800](), [sdk/go/agent/agent_lifecycle.go:20-100]()

---

## Core Components

### The Agent Instance
The `Agent` struct is the central coordinator. It is created using `agent.New(cfg)` and handles the lifecycle of the agent node, including registration, heartbeats (leases), and request routing.
**Sources:** [sdk/go/agent/agent.go:233-260]()

### Reasoners and Skills
In the Go SDK, capabilities are registered as **Reasoners**. A Reasoner is a named handler that can be invoked by the Control Plane. 
- **HandlerFunc**: The core logic of a capability, defined as `func(ctx context.Context, input map[string]any) (any, error)`.
- **Triggers**: Reasoners can be bound to external events (e.g., GitHub webhooks) or schedules (cron) using `WithTriggers`.
**Sources:** [sdk/go/agent/agent.go:58-58](), [sdk/go/agent/agent.go:122-153](), [sdk/go/agent/agent.go:188-202]()

### Harness Orchestration
The Go SDK includes a sophisticated `harness.Runner` for delegating tasks to autonomous coding agents like Claude Code or OpenCode. It supports:
- **Schema Validation**: Forcing the coding agent to return structured JSON.
- **Incremental Mode**: Building complex JSON objects field-by-field for higher reliability.
- **Provider Abstraction**: A unified interface for `opencode`, `claude-code`, `codex`, and `gemini`.
**Sources:** [sdk/go/harness/runner.go:21-33](), [sdk/go/harness/runner.go:53-158](), [sdk/go/harness/provider.go:5-14]()

---

## Feature Comparison

| Feature | Go SDK Implementation | Reference |
| :--- | :--- | :--- |
| **Identity** | W3C DIDs and Key Management | `sdk/go/did/` |
| **AI Integration** | `ai.Client` with multi-provider support | `sdk/go/ai/ai.go` |
| **Tool Calling** | Automated mapping of Reasoners to LLM tools | `sdk/go/ai/tool_calling.go` |
| **Harness** | Native CLI-based coding agent orchestration | `sdk/go/harness/runner.go` |
| **CLI Mode** | Built-in support for running reasoners via CLI | `sdk/go/agent/cli.go` |

---

## Quick Start Example

```go
package main

import (
	"context"
	"github.com/Agent-Field/agentfield/sdk/go/agent"
)

func main() {
	// 1. Initialize the Agent
	cfg := agent.Config{
		NodeID:        "my-go-agent",
		Version:       "1.0.0",
		AgentFieldURL: "http://localhost:8080",
	}
	a, _ := agent.New(cfg)

	// 2. Register a capability (Reasoner)
	a.RegisterReasoner("hello", func(ctx context.Context, input map[string]any) (any, error) {
		name, _ := input["name"].(string)
		return map[string]any{"message": "Hello " + name}, nil
	})

	// 3. Start the Agent
	a.Initialize(context.Background())
	a.Run()
}
```
**Sources:** [sdk/go/agent/agent.go:264-340](), [sdk/go/agent/agent.go:374-385]()

---

## Project Template

When using the `af` CLI to initialize a Go agent, the following structure is generated:

```text
my-agent/
├── go.mod              # Module definition [sdk/go/go.mod]
├── main.go             # Agent entry point using agent.New()
└── internal/           # Optional internal logic
```
**Sources:** [sdk/go/go.mod:1-9]()

---

## Installation

Add the Go SDK to your project using `go get`:

```bash
go get github.com/Agent-Field/agentfield/sdk/go
```
**Sources:** [sdk/go/go.mod:1-5]()

---

# Page: Agent Initialization

# Agent Initialization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/go_agent_nodes/go.mod](examples/go_agent_nodes/go.mod)
- [examples/go_agent_nodes/go.sum](examples/go_agent_nodes/go.sum)
- [sdk/go/agent/agent.go](sdk/go/agent/agent.go)
- [sdk/go/agent/agent_lifecycle.go](sdk/go/agent/agent_lifecycle.go)
- [sdk/go/agent/agent_test.go](sdk/go/agent/agent_test.go)
- [sdk/go/agent/cli.go](sdk/go/agent/cli.go)
- [sdk/go/agent/cli_test.go](sdk/go/agent/cli_test.go)
- [sdk/go/agent/pause.go](sdk/go/agent/pause.go)
- [sdk/go/agent/pause_test.go](sdk/go/agent/pause_test.go)
- [sdk/go/agent/version.go](sdk/go/agent/version.go)
- [sdk/go/ai/tool_calling.go](sdk/go/ai/tool_calling.go)
- [sdk/go/ai/tool_calling_test.go](sdk/go/ai/tool_calling_test.go)
- [sdk/go/go.mod](sdk/go/go.mod)
- [sdk/go/go.sum](sdk/go/go.sum)
- [sdk/go/harness/claudecode.go](sdk/go/harness/claudecode.go)
- [sdk/go/harness/coverage_branches_test.go](sdk/go/harness/coverage_branches_test.go)
- [sdk/go/harness/coverage_helpers_test.go](sdk/go/harness/coverage_helpers_test.go)
- [sdk/go/harness/parity_test.go](sdk/go/harness/parity_test.go)
- [sdk/go/harness/provider.go](sdk/go/harness/provider.go)
- [sdk/go/harness/result.go](sdk/go/harness/result.go)
- [sdk/go/harness/runner.go](sdk/go/harness/runner.go)
- [sdk/go/harness/runner_test.go](sdk/go/harness/runner_test.go)
- [sdk/go/harness/schema.go](sdk/go/harness/schema.go)

</details>



## Purpose and Scope

This page documents how to create and initialize agent nodes using the Go SDK. It covers the `agent.New()` constructor, configuration options, AI client setup, and the agent registration lifecycle with the control plane.

For information about registering skills and reasoners after initialization, see [Registering Skills](5.2). For Python SDK agent initialization, see [Agent Class](3.1). For TypeScript SDK initialization, see [Agent Class](4.1).

---

## Overview

The Go SDK provides the `agent` package for creating agent nodes that register with the AgentField control plane. Agent initialization is a two-step process:

1.  **Create the agent** with `agent.New()` and a `Config` struct.
2.  **Initialize and Run** the agent to register capabilities and begin serving requests.

```go
cfg := agent.Config{
    NodeID:        "go-researcher",
    Version:       "1.0.0",
    AgentFieldURL: "http://localhost:8001",
}

app, err := agent.New(cfg)
if err != nil {
    log.Fatal(err)
}

// Register reasoners/skills here...

if err := app.Initialize(context.Background()); err != nil {
    log.Fatal(err)
}
```

**Sources:** [sdk/go/agent/agent.go:273-280](), [sdk/go/agent/agent_test.go:25-45]()

---

## Agent Constructor

### The `New()` Function

The `agent.New()` function creates a new agent instance with the specified configuration [sdk/go/agent/agent.go:273]().

The constructor:
*   Validates the configuration (NodeID and Version are strictly required) [sdk/go/agent/agent_test.go:46-61]().
*   Applies default values for `TeamID` ("default"), `ListenAddress` (":8001"), and `LeaseRefreshInterval` (2 minutes) [sdk/go/agent/agent_test.go:101-114]().
*   Initializes the internal `httpClient` with a default `CallTimeout` of 15 seconds [sdk/go/agent/agent_test.go:73-85]().
*   Sets up the AI client if `AIConfig` is provided [sdk/go/agent/agent_test.go:116-131]().

**Sources:** [sdk/go/agent/agent.go:273-350](), [sdk/go/agent/agent_test.go:25-144]()

---

## Configuration Structure

### Config Fields

The `Config` struct defines the agent's identity, connection parameters, and AI settings:

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `NodeID` | `string` | **Yes** | Unique identifier for this agent node. |
| `Version` | `string` | **Yes** | Semantic version of the agent code. |
| `AgentFieldURL` | `string` | Yes | Control plane base URL (e.g., `http://localhost:8001`). |
| `TeamID` | `string` | No | Team ownership (defaults to "default"). |
| `ListenAddress` | `string` | No | Network address to bind (defaults to ":8001"). |
| `AIConfig` | `*ai.Config` | No | Configuration for LLM providers (OpenAI, Anthropic, etc.). |
| `CallTimeout` | `time.Duration`| No | Timeout for outgoing calls (defaults to 15s). |

**Sources:** [sdk/go/agent/agent.go:237-271](), [sdk/go/agent/agent_test.go:32-114]()

### Configuration Data Flow

```mermaid
graph TB
    Config["agent.Config"]
    
    Config --> NodeID["NodeID<br/>(Unique Identifier)"]
    Config --> AgentFieldURL["AgentFieldURL<br/>(Control Plane URL)"]
    Config --> AIConfig["AIConfig<br/>(Provider & Keys)"]
    Config --> ListenAddress["ListenAddress<br/>(Local Server Bind)"]
    
    NodeID --> RegReq["types.NodeRegistrationRequest"]
    AgentFieldURL --> Client["Internal AgentFieldClient"]
    AIConfig --> AIClient["ai.Client (LLM Access)"]
    ListenAddress --> HTTPServer["net/http Server"]
```

**Sources:** [sdk/go/agent/agent.go:237-271](), [sdk/go/agent/agent_test.go:231-252]()

---

## AI Client Setup

If the agent needs to use LLMs directly (e.g., within a Reasoner), the `AIConfig` must be populated during initialization. The Go SDK supports multiple providers through the `ai` package.

```go
cfg := agent.Config{
    // ... other config ...
    AIConfig: &ai.Config{
        Provider: "openai",
        Model:    "gpt-4o",
        APIKey:   "sk-...",
    },
}
```

When `AIConfig` is present, `agent.New()` initializes an `aiClient` that is accessible to handlers via the execution context.

**Sources:** [sdk/go/agent/agent.go:323-333](), [sdk/go/agent/agent_test.go:116-131]()

---

## Initialization Lifecycle

### Sequence Diagram: Agent Startup

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant Agent as "agent.Agent"
    participant CP as "Control Plane"
    
    Dev->>Agent: New(Config)
    Agent->>Agent: Validate & Set Defaults
    Agent->>Agent: Init AI Client (if Configured)
    
    Note over Dev, Agent: Register Reasoners & Skills
    
    Dev->>Agent: Initialize(ctx)
    Agent->>Agent: Start HTTP Listener
    Agent->>CP: POST /api/v1/nodes (Register)
    CP-->>Agent: 200 OK (NodeRegistrationResponse)
    
    loop Lease Loop
        Agent->>CP: POST /api/v1/nodes/{id}/status (Heartbeat)
        CP-->>Agent: 200 OK (LeaseResponse)
        Agent->>Agent: Sleep for LeaseSeconds
    end
```

**Sources:** [sdk/go/agent/agent_test.go:231-274](), [sdk/go/agent/agent.go:420-460]()

---

## Registration with Control Plane

### Node Registration

When `Initialize()` is called, the agent sends a `NodeRegistrationRequest` to the control plane. This includes the agent's ID, version, team, and its entire capability manifest (Reasoners and Skills).

**Key Code Entity:** `types.NodeRegistrationRequest`

The registration process:
1.  Calculates the `CallbackURL` if not explicitly provided [sdk/go/agent/agent.go:440]().
2.  Marshals all registered `reasoners` and `skills` into the request [sdk/go/agent/agent.go:445]().
3.  Sends the payload to the `/api/v1/nodes` endpoint [sdk/go/agent/agent_test.go:232-244]().

**Sources:** [sdk/go/agent/agent.go:420-460](), [sdk/go/agent/agent_test.go:231-274]()

### Lease and Heartbeat

After successful registration, the agent enters a "Lease Loop". It periodically sends heartbeats to the control plane to maintain its "Active" status. The interval is governed by `LeaseRefreshInterval` in the config or the `LeaseSeconds` returned by the server.

**Sources:** [sdk/go/agent/agent.go:462-500](), [sdk/go/agent/agent_test.go:245-251]()

---

## Execution Context

Every invocation of an agent's reasoner or skill is accompanied by an `ExecutionContext`. This context contains metadata about the current workflow, including:

*   **IDs**: `RunID`, `ExecutionID`, `WorkflowID` [sdk/go/agent/agent.go:34-41]().
*   **Identity**: `ActorID`, `CallerDID`, `TargetDID` [sdk/go/agent/agent.go:38-49]().
*   **Trace**: `Depth`, `ParentExecutionID` [sdk/go/agent/agent.go:36-42]().

This context is injected into the Go `context.Context` and can be retrieved within handlers to track state or perform cross-agent calls.

**Sources:** [sdk/go/agent/agent.go:33-51]()

---

## Environment Variables

The Go SDK respects several environment variables for configuration, particularly useful in containerized environments:

| Variable | Config Equivalent |
| :--- | :--- |
| `AGENTFIELD_URL` | `AgentFieldURL` |
| `AGENT_NODE_ID` | `NodeID` |
| `AGENT_TEAM_ID` | `TeamID` |
| `PORT` | Influences `ListenAddress` |

**Sources:** [sdk/go/agent/agent.go:15-21]() (Usage of `os` package), [sdk/go/agent/agent_test.go:12-16]()

---

# Page: Registering Skills

# Registering Skills

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/TESTING.md](docs/TESTING.md)
- [scripts/run-functional-tests.sh](scripts/run-functional-tests.sh)
- [sdk/go/agent/agent.go](sdk/go/agent/agent.go)
- [sdk/go/agent/agent_lifecycle.go](sdk/go/agent/agent_lifecycle.go)
- [sdk/go/agent/pause.go](sdk/go/agent/pause.go)
- [sdk/go/agent/pause_test.go](sdk/go/agent/pause_test.go)
- [sdk/go/agent/router.go](sdk/go/agent/router.go)
- [sdk/go/agent/router_test.go](sdk/go/agent/router_test.go)
- [sdk/go/agent/skill_registration_additional_test.go](sdk/go/agent/skill_registration_additional_test.go)
- [sdk/go/functional_test.go](sdk/go/functional_test.go)
- [sdk/go/harness/claudecode.go](sdk/go/harness/claudecode.go)
- [sdk/go/harness/coverage_branches_test.go](sdk/go/harness/coverage_branches_test.go)
- [sdk/go/harness/coverage_helpers_test.go](sdk/go/harness/coverage_helpers_test.go)
- [sdk/go/harness/parity_test.go](sdk/go/harness/parity_test.go)
- [sdk/go/harness/provider.go](sdk/go/harness/provider.go)
- [sdk/go/harness/result.go](sdk/go/harness/result.go)
- [sdk/go/harness/runner.go](sdk/go/harness/runner.go)
- [sdk/go/harness/runner_test.go](sdk/go/harness/runner_test.go)
- [sdk/go/harness/schema.go](sdk/go/harness/schema.go)
- [sdk/go/internal/testutil/testenv.go](sdk/go/internal/testutil/testenv.go)

</details>



## Purpose and Scope

This page documents how to register skills and reasoners in the Go SDK. In AgentField, **Skills** are deterministic, non-AI operations that an agent performs (e.g., API calls, calculations), while **Reasoners** are high-level handlers often involving AI logic. In the Go SDK, both are registered using the `Agent` instance before starting the server.

**Sources:** [sdk/go/agent/agent.go:121-153](), [sdk/go/agent/agent_lifecycle.go:126-184]()

---

## Code Entity Space to System Architecture

The following diagram bridges Go code entities to the system-level registration flow.

**Diagram: Go SDK Registration Flow**
```mermaid
graph TD
    subgraph "Code Entity Space"
        NewAgent["agent.New()"]
        RegisterSkill["agent.RegisterSkill()"]
        RegisterReasoner["agent.RegisterReasoner()"]
        AgentRun["agent.Run()"]
    end

    subgraph "System Architecture"
        CP["Control Plane<br/>NodeRegistrationRequest"]
        Server["HTTP Server<br/>/execute"]
    end

    NewAgent --> RegisterSkill
    NewAgent --> RegisterReasoner
    RegisterSkill --> AgentRun
    RegisterReasoner --> AgentRun
    
    AgentRun -->|"POST /api/v1/nodes/register"| CP
    AgentRun -->|"Listen"| Server
    
    style NewAgent fill:none
    style CP fill:none
    style Server fill:none
```

**Sources:** [sdk/go/agent/agent_lifecycle.go:79-124](), [sdk/go/agent/agent_lifecycle.go:126-217]()

---

## Registering Skills

Skills represent deterministic capabilities. They are defined by a name and a handler function.

### Skill Handler Signature
The skill handler follows the `HandlerFunc` type:
`type HandlerFunc func(ctx context.Context, input map[string]any) (any, error)` [sdk/go/agent/agent.go:58-58]()

### Implementation Example
```go
agent.RegisterSkill("get_weather", func(ctx context.Context, input map[string]any) (any, error) {
    city, _ := input["city"].(string)
    // Deterministic logic here
    return map[string]string{"temp": "22C", "city": city}, nil
})
```

**Sources:** [sdk/go/agent/agent.go:57-59](), [sdk/go/agent/agent_lifecycle.go:145-153]()

---

## Registering Reasoners

Reasoners are registered using `RegisterReasoner`. Unlike skills, reasoners in Go support extensive metadata via `ReasonerOption` decorators.

### Reasoner Options (Decorators)
Metadata can be attached to reasoners during registration to control behavior in the Control Plane:

| Function | Purpose |
|----------|---------|
| `WithInputSchema` | Defines the JSON schema for input validation [sdk/go/agent/agent.go:64-70]() |
| `WithOutputSchema` | Defines the JSON schema for output validation [sdk/go/agent/agent.go:73-79]() |
| `WithCLI` | Marks the reasoner as accessible via the `af` CLI [sdk/go/agent/agent.go:82-86]() |
| `WithTriggers` | Binds external event sources (Webhooks/Schedules) [sdk/go/agent/agent.go:188-202]() |
| `WithDescription` | Adds a human-readable description for the UI [sdk/go/agent/agent.go:104-108]() |

### Trigger Bindings
Go agents can declare that a reasoner should be triggered by external events:
- **EventTrigger**: Binds to sources like GitHub, Stripe, or generic webhooks [sdk/go/agent/agent.go:158-163]().
- **ScheduleTrigger**: Binds to a cron expression [sdk/go/agent/agent.go:168-171]().

**Sources:** [sdk/go/agent/agent.go:60-120](), [sdk/go/agent/agent.go:188-225]()

---

## Data Flow: Registration to Execution

When `agent.Run()` is called, the SDK aggregates all registered skills and reasoners into a `NodeRegistrationRequest` [sdk/go/agent/agent_lifecycle.go:155-184]().

**Diagram: Capability Registration Data Flow**
```mermaid
sequenceDiagram
    participant User as "Go App"
    participant SDK as "Agent Instance"
    participant CP as "Control Plane"

    User->>SDK: RegisterSkill("calc", fn)
    User->>SDK: RegisterReasoner("chat", fn, WithCLI())
    User->>SDK: Run(ctx)
    
    SDK->>SDK: Build types.NodeRegistrationRequest
    Note right of SDK: Includes ReasonerDefinition<br/>and SkillDefinition
    
    SDK->>CP: POST /api/v1/nodes/register
    CP-->>SDK: 200 OK (or pending_approval)
    
    Note over SDK: Starts HTTP Server on cfg.Port
```

**Sources:** [sdk/go/agent/agent_lifecycle.go:126-184](), [sdk/go/agent/agent_lifecycle.go:94-105]()

---

## Execution Context

Handlers receive a `context.Context` which contains execution metadata. This can be extracted into an `ExecutionContext` struct:

```go
// ExecutionContext captures headers like RunID and SessionID
type ExecutionContext struct {
    RunID             string
    ExecutionID       string
    SessionID         string
    ActorID           string
    // ...
}
```

This context allows the handler to be "aware" of its place in a larger workflow, enabling stateful memory access or multi-agent coordination.

**Sources:** [sdk/go/agent/agent.go:33-51]()

---

## Advanced: The Harness System

While skills are deterministic, Go agents can delegate complex autonomous tasks to the **Harness** system. The `harness.Runner` allows a Go agent to invoke "Coding Agents" (like Claude Code or OpenCode) to produce structured output based on a JSON schema.

### Harness Execution Pattern
1. **Initialize Runner**: `harness.NewRunner(options)` [sdk/go/harness/runner.go:28-33]().
2. **Run Task**: `runner.Run(ctx, prompt, schema, &dest, overrides)` [sdk/go/harness/runner.go:53-158]().
3. **Schema Enforcement**: The runner automatically handles prompt injection, output file tracking, and retries if the coding agent fails to produce valid JSON [sdk/go/harness/runner.go:140-144]().

**Sources:** [sdk/go/harness/runner.go:19-53](), [sdk/go/harness/result.go:49-71]()

---

# Page: Control Plane

# Control Plane

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [control-plane/cmd/af/main.go](control-plane/cmd/af/main.go)
- [control-plane/cmd/agentfield-server/main.go](control-plane/cmd/agentfield-server/main.go)
- [control-plane/config/agentfield.yaml](control-plane/config/agentfield.yaml)
- [control-plane/go.mod](control-plane/go.mod)
- [control-plane/go.sum](control-plane/go.sum)
- [control-plane/internal/config/config.go](control-plane/internal/config/config.go)
- [control-plane/internal/config/config_additional_test.go](control-plane/internal/config/config_additional_test.go)
- [control-plane/internal/server/middleware/auth.go](control-plane/internal/server/middleware/auth.go)
- [control-plane/internal/server/middleware/auth_admin_additional_test.go](control-plane/internal/server/middleware/auth_admin_additional_test.go)
- [control-plane/internal/server/middleware/auth_test.go](control-plane/internal/server/middleware/auth_test.go)
- [control-plane/internal/server/routes_admin.go](control-plane/internal/server/routes_admin.go)
- [control-plane/internal/server/routes_middleware.go](control-plane/internal/server/routes_middleware.go)
- [control-plane/internal/server/server.go](control-plane/internal/server/server.go)
- [control-plane/internal/server/server_additional_test.go](control-plane/internal/server/server_additional_test.go)
- [control-plane/internal/server/server_coverage_additional_test.go](control-plane/internal/server/server_coverage_additional_test.go)
- [deployments/docker/Dockerfile.control-plane](deployments/docker/Dockerfile.control-plane)
- [deployments/docker/Dockerfile.demo-go-agent](deployments/docker/Dockerfile.demo-go-agent)
- [deployments/docker/Dockerfile.go-agent](deployments/docker/Dockerfile.go-agent)
- [deployments/helm/agentfield/templates/control-plane-deployment.yaml](deployments/helm/agentfield/templates/control-plane-deployment.yaml)
- [docs/ENVIRONMENT_VARIABLES.md](docs/ENVIRONMENT_VARIABLES.md)
- [tests/functional/docker/agentfield-test.yaml](tests/functional/docker/agentfield-test.yaml)

</details>



The Control Plane is the central orchestration service in AgentField. It is a stateless Go-based HTTP server that manages agent discovery, routes execution requests between agents, tracks workflow state, and provides observability into the entire multi-agent system. The Control Plane does not execute agent logic itself—it coordinates and observes.

**Scope:** This page covers the Control Plane's architecture, core components, storage layer, API endpoints, and configuration. For details, see:
- [Server Configuration](#6.1) — Control plane startup options: `--port`, `--backend-only`, `--ui-dev`, `--no-vc-execution`, config files.
- [Storage Layer](#6.2) — `StorageProvider` interface, `LocalStorage` implementation, SQLite vs PostgreSQL modes.
- [Database Configuration](#6.3) — Configuring SQLite (WAL mode, pragmas) and PostgreSQL (connection pooling, FTS setup).
- [Agent Registration](#6.4) — How agents register with the control plane: capabilities, callback URLs, and discovery.
- [API Endpoints](#6.5) — Control plane REST API reference: `/api/v1/execute`, `/api/v1/nodes`, `/api/v1/memory`, etc.

---

## Architecture Overview

The Control Plane follows a hub-and-spoke architecture where it acts as the central coordination point for all agent nodes. It is designed to be stateless—all persistent state lives in the storage layer.

```mermaid
graph TB
    subgraph "Control Plane Process [AgentFieldServer]"
        Server["AgentFieldServer<br/>(internal/server/server.go)"]
        Router["HTTP Router<br/>(gin.Engine)"]
        Storage["StorageProvider<br/>(interfaces.go)"]
        StatusManager["StatusManager<br/>(services/status_manager.go)"]
        HealthMonitor["HealthMonitor<br/>(services/health_monitor.go)"]
        DIDService["DIDService<br/>(services/did_service.go)"]
    end
    
    subgraph "Storage Backends"
        SQLite["LocalStorage<br/>SQLite + BoltDB"]
        Postgres["LocalStorage<br/>PostgreSQL mode"]
    end
    
    subgraph "External Connections"
        AgentNodes["Agent Nodes<br/>(HTTPAgentClient)"]
        UIClients["Dashboard UI<br/>(Vite/React)"]
        APIClients["REST API Clients"]
    end
    
    Server --> Router
    Server --> Storage
    Server --> StatusManager
    Server --> HealthMonitor
    Server --> DIDService
    
    Storage -->|"mode=local"| SQLite
    Storage -->|"mode=postgres"| Postgres
    
    Router --> AgentNodes
    Router --> UIClients
    Router --> APIClients
    
    HealthMonitor --> AgentNodes
```

**Sources:**
- [control-plane/internal/server/server.go:47-104]()
- [control-plane/internal/server/server.go:123-134]()
- [control-plane/internal/config/config.go:17-25]()

---

## Core Components

### AgentFieldServer

The `AgentFieldServer` struct is the main entry point for the Control Plane. It orchestrates all subsystems and exposes HTTP/WebSocket endpoints via the `gin` framework [control-plane/internal/server/server.go:51]().

**Key Responsibilities:**
- **Lifecycle Management:** Creating infrastructure components like `ProcessManager` and `PortManager` [control-plane/internal/server/server.go:151-152]().
- **Agent Communication:** Initializing the `HTTPAgentClient` for dispatching requests to agent nodes [control-plane/internal/server/server.go:145]().
- **Status Coordination:** Using `StatusManager` to reconcile agent health and heartbeats [control-plane/internal/server/server.go:158-171]().
- **Identity:** Managing Decentralized Identifiers (DIDs) and Verifiable Credentials (VCs) via `didService` and `vcService` [control-plane/internal/server/server.go:64-65]().

**Sources:**
- [control-plane/internal/server/server.go:47-104]()
- [control-plane/internal/server/server.go:145-171]()

### Storage Provider Interface

The `StorageProvider` interface defines all persistence operations. The Control Plane uses a `StorageFactory` to instantiate the correct backend based on the `StorageConfig` [control-plane/internal/server/server.go:123-127]().

| Category | Purpose | Code Reference |
|----------|---------|----------------|
| **Local Mode** | SQLite for relations, BoltDB for KV | [control-plane/internal/config/config.go:193-197]() |
| **Postgres Mode** | Full PostgreSQL with connection pooling | [control-plane/internal/config/config.go:199-210]() |
| **Vector** | Embedding search (pgvector fallback) | [control-plane/internal/config/config.go:212-215]() |

For details, see [Storage Layer](#6.2).

---

## Server Configuration

The server is configured primarily through `control-plane/config/agentfield.yaml` and environment variables. Key startup options include:

- **Port:** Default `8080` [control-plane/config/agentfield.yaml:2]().
- **Authentication:** Enforced via `APIKeyAuth` middleware using `X-API-Key` or `Authorization: Bearer` [control-plane/internal/server/middleware/auth.go:19-146]().
- **CORS:** Configurable allowed origins, methods, and headers for browser clients [control-plane/internal/server/routes_middleware.go:19-38]().
- **Redaction:** `redact_payloads` (default `true`) prevents sensitive input/output data from appearing in logs [control-plane/internal/config/config.go:38-41]().

**Startup Logic:**
The entry point in `control-plane/cmd/af/main.go` parses flags like `--backend-only` and `--ui-dev` to toggle the embedded UI [control-plane/cmd/af/main.go:136-144]().

**Sources:**
- [control-plane/internal/config/config.go:17-151]()
- [control-plane/internal/server/middleware/auth.go:20-146]()
- [control-plane/cmd/af/main.go:53-219]()

---

## Security & Middleware

The Control Plane implements a robust middleware stack to protect the orchestration layer:

1. **API Key Auth:** Validates requests using constant-time comparison [control-plane/internal/server/middleware/auth.go:121]().
2. **DID Auth:** Optional cryptographic identity verification [control-plane/internal/server/routes_middleware.go:90-102]().
3. **Admin Auth:** Separate `X-Admin-Token` requirement for sensitive management routes [control-plane/internal/server/middleware/auth.go:166-185]().
4. **Timeout:** Global 1-hour timeout for long-running AI agent executions [control-plane/internal/server/routes_middleware.go:54-62]().

```mermaid
graph LR
    Request["Incoming Request"] --> CORS["CORS Middleware"]
    CORS --> Logger["Request Logger"]
    Logger --> Timeout["Timeout (1h)"]
    Timeout --> Auth["API Key Auth"]
    Auth --> DID["DID Auth (Optional)"]
    DID --> Handler["Route Handler"]
```

**Sources:**
- [control-plane/internal/server/routes_middleware.go:18-110]()
- [control-plane/internal/server/middleware/auth.go:1-186]()

---

## Agent Registration & Discovery

Agents register by providing their `node_id`, `callback_url`, and capabilities (reasoners and skills). The Control Plane tracks these in the registry and uses a `StatusManager` to monitor liveness via heartbeats [control-plane/internal/server/server.go:158-171]().

For details on the registration handshake and capability discovery, see [Agent Registration](#6.4).

**Sources:**
- [control-plane/internal/server/server.go:155-171]()
- [control-plane/internal/config/config.go:122-130]()

---

# Page: Server Configuration

# Server Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [control-plane/cmd/af/main.go](control-plane/cmd/af/main.go)
- [control-plane/cmd/agentfield-server/main.go](control-plane/cmd/agentfield-server/main.go)
- [control-plane/config/agentfield.yaml](control-plane/config/agentfield.yaml)
- [control-plane/internal/config/config.go](control-plane/internal/config/config.go)
- [control-plane/internal/config/config_additional_test.go](control-plane/internal/config/config_additional_test.go)
- [control-plane/internal/server/middleware/auth.go](control-plane/internal/server/middleware/auth.go)
- [control-plane/internal/server/middleware/auth_admin_additional_test.go](control-plane/internal/server/middleware/auth_admin_additional_test.go)
- [control-plane/internal/server/middleware/auth_test.go](control-plane/internal/server/middleware/auth_test.go)
- [control-plane/internal/server/routes_admin.go](control-plane/internal/server/routes_admin.go)
- [control-plane/internal/server/routes_middleware.go](control-plane/internal/server/routes_middleware.go)
- [control-plane/internal/server/server.go](control-plane/internal/server/server.go)
- [control-plane/internal/server/server_additional_test.go](control-plane/internal/server/server_additional_test.go)
- [control-plane/internal/server/server_coverage_additional_test.go](control-plane/internal/server/server_coverage_additional_test.go)
- [deployments/helm/agentfield/templates/control-plane-deployment.yaml](deployments/helm/agentfield/templates/control-plane-deployment.yaml)
- [docs/ENVIRONMENT_VARIABLES.md](docs/ENVIRONMENT_VARIABLES.md)
- [tests/functional/docker/agentfield-test.yaml](tests/functional/docker/agentfield-test.yaml)

</details>



This page documents how to configure and start the AgentField control plane server. It covers command-line flags, configuration files, environment variables, and runtime options for the core orchestration service.

---

## Overview

The AgentField control plane is the central orchestration hub. It is started using the `af server` command (or the legacy `agentfield-server` binary). It is a Go service built on the Gin web framework that manages agent registrations, execution routing, and cryptographic identity.

**Key Components:**
- **StorageProvider:** Interface for persistence (SQLite or PostgreSQL). [control-plane/internal/server/server.go:49-49]()
- **AgentService:** Manages agent lifecycle and process management. [control-plane/internal/server/server.go:155-155]()
- **StatusManager:** Unified status and health tracking for agent nodes. [control-plane/internal/server/server.go:168-168]()
- **DID/VC Services:** Handles identity and verifiable credential generation. [control-plane/internal/server/server.go:63-70]()

**Sources:** [control-plane/internal/server/server.go:46-104](), [control-plane/cmd/af/main.go:53-219]()

---

## Starting the Server

The server can be started via the unified CLI:

```bash
af server
```

Upon startup, the server initializes data directories (defaulting to `~/.agentfield`), sets up the storage provider, and begins listening for HTTP and gRPC traffic.

### Startup Sequence

```mermaid
sequenceDiagram
    participant CLI as af server
    participant Config as config.LoadConfig
    participant Factory as storage.StorageFactory
    participant Server as server.NewAgentFieldServer
    participant Gin as gin.Engine

    CLI->>Config: Load YAML & Env
    Config-->>CLI: Config Object
    CLI->>Factory: CreateStorage(cfg.Storage)
    Factory-->>CLI: StorageProvider (SQLite/Pg)
    CLI->>Server: NewAgentFieldServer(cfg)
    Server->>Server: applyGlobalMiddleware()
    Server->>Gin: Register Routes (/api/v1)
    CLI->>Server: Start()
    Server->>Gin: Run(port)
```

**Sources:** [control-plane/cmd/af/main.go:171-190](), [control-plane/internal/server/server.go:107-168](), [control-plane/internal/server/routes_middleware.go:18-110]()

---

## Command-Line Flags

The `af server` command (implemented via Cobra) supports several flags that override configuration file settings.

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--port` | int | 8080 | HTTP server port. [control-plane/cmd/af/main.go:64-67]() |
| `--config` | string | "" | Path to custom `agentfield.yaml`. [control-plane/cmd/af/main.go:57-57]() |
| `--backend-only` | bool | false | Disables the Web UI entirely. [control-plane/cmd/af/main.go:137-139]() |
| `--ui-dev` | bool | false | Proxies UI requests to Vite dev server (port 5173). [control-plane/cmd/af/main.go:140-144]() |
| `--no-vc-execution` | bool | false | Disables Verifiable Credential generation for executions. [control-plane/cmd/af/main.go:147-151]() |
| `--storage-mode` | string | "local" | Force storage mode (`local` or `postgres`). [control-plane/cmd/af/main.go:77-82]() |
| `--open` | bool | true | Automatically open the browser to the dashboard. [control-plane/cmd/af/main.go:195-213]() |

**Sources:** [control-plane/cmd/af/main.go:63-151](), [control-plane/cmd/agentfield-server/main.go:84-190]()

---

## Configuration File

The server primary configuration is defined in `agentfield.yaml`. The loader searches for this file in the current directory, `~/.agentfield/`, or `/etc/agentfield/`.

### Core Configuration Sections

| Section | Code Entity | Description |
|---------|-------------|-------------|
| `agentfield` | `AgentFieldConfig` | Port, timeouts, and execution queue settings. [control-plane/internal/config/config.go:70-82]() |
| `storage` | `StorageConfig` | Database mode and connection details. [control-plane/internal/config/config.go:20-20]() |
| `features.did` | `DIDConfig` | DID method, key rotation, and VC requirements. [control-plane/config/agentfield.yaml:85-105]() |
| `api.cors` | `CORSConfig` | Allowed origins and headers for the Gin router. [control-plane/config/agentfield.yaml:29-55]() |
| `logging` | `LoggingConfig` | Log level and payload redaction. [control-plane/internal/config/config.go:28-36]() |

**Sources:** [control-plane/internal/config/config.go:17-25](), [control-plane/config/agentfield.yaml:1-173]()

---

## Environment Variables

AgentField uses Viper to map environment variables to configuration keys using the `AGENTFIELD_` prefix and underscores for nesting.

| Environment Variable | Config Path | Description |
|----------------------|-------------|-------------|
| `AGENTFIELD_PORT` | `agentfield.port` | Server listen port. [control-plane/cmd/af/main.go:70-74]() |
| `AGENTFIELD_STORAGE_MODE` | `storage.mode` | `local` (SQLite) or `postgres`. [control-plane/cmd/af/main.go:85-88]() |
| `AGENTFIELD_POSTGRES_URL` | `storage.postgres.url` | Full PostgreSQL connection string. [control-plane/cmd/af/main.go:90-108]() |
| `AGENTFIELD_API_KEY` | `api.auth.api_key` | Global API key for endpoint protection. [control-plane/internal/server/middleware/auth.go:32-40]() |
| `AGENTFIELD_HOME` | N/A | Base directory for data/keys (default `~/.agentfield`). [control-plane/internal/server/server.go:109-116]() |

**Sources:** [docs/ENVIRONMENT_VARIABLES.md:1-130](), [control-plane/cmd/af/main.go:70-129]()

---

## Authentication and Security

The server enforces security through multiple layers of middleware applied in `applyGlobalMiddleware()`.

### API Key Authentication
Enforced via `middleware.APIKeyAuth`. It checks the `X-API-Key` header or `Authorization: Bearer` token.
- **Exemptions:** Health checks, metrics, public DID documents, and UI static files. [control-plane/internal/server/middleware/auth.go:54-71]()
- **Streaming:** Browser-based EventSource/WebSockets can use the `api_key` query parameter for specific allowlisted paths. [control-plane/internal/server/middleware/auth.go:117-119]()

### DID Authentication
When `features.did.authorization.did_auth_enabled` is true, the server validates `X-DID-Signature` and `X-Caller-DID` headers. [control-plane/internal/server/routes_middleware.go:90-102]()

### Admin Authentication
Routes under `/api/admin/v1` require an `X-Admin-Token` as configured in the `AuthorizationConfig`. [control-plane/internal/server/middleware/auth.go:166-185]()

**Sources:** [control-plane/internal/server/middleware/auth.go:19-146](), [control-plane/internal/server/routes_middleware.go:64-102]()

---

## UI Configuration

The control plane includes a React-based dashboard. Its behavior is controlled by the `ui` config block.

```mermaid
graph TD
    subgraph UI_Modes [UI Serving Modes]
        Embedded["'embedded' (Default)"]
        Dev["'dev'"]
        Disabled["'backend-only'"]
    end

    Embedded -->|Serves| Assets["Embedded client.IsUIEmbedded()"]
    Dev -->|Proxies| Vite["Vite Dev Server (Port 5173)"]
    Disabled -->|Returns| 404["No UI Routes"]
```

- **Embedded:** Static assets are bundled into the Go binary using `go:embed`. [control-plane/cmd/af/main.go:154-163]()
- **Dev Mode:** Useful for frontend development. The server proxies UI requests while maintaining API logic. [control-plane/cmd/af/main.go:140-144]()

**Sources:** [control-plane/cmd/af/main.go:136-163](), [control-plane/internal/config/config.go:61-67]()

---

## Storage Layer Setup

The server uses a `StorageFactory` to initialize the persistence layer.

### Local Mode (SQLite + BoltDB)
- **SQLite:** Stores structured data (agents, executions, workflows). [control-plane/config/agentfield.yaml:71-71]()
- **BoltDB:** Acts as the high-performance Key-Value store for agent memory. [control-plane/config/agentfield.yaml:72-72]()

### PostgreSQL Mode
- Recommended for production.
- Requires `pgvector` for vector memory operations. [control-plane/config/agentfield.yaml:80-82]()
- Configured via `AGENTFIELD_POSTGRES_URL` or individual host/port variables. [control-plane/cmd/af/main.go:90-129]()

**Sources:** [control-plane/internal/server/server.go:123-127](), [control-plane/config/agentfield.yaml:68-82]()

---

# Page: Storage Layer

# Storage Layer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [control-plane/internal/handlers/memory.go](control-plane/internal/handlers/memory.go)
- [control-plane/internal/handlers/memory_handler_test.go](control-plane/internal/handlers/memory_handler_test.go)
- [control-plane/internal/handlers/ui/dashboard.go](control-plane/internal/handlers/ui/dashboard.go)
- [control-plane/internal/handlers/ui/dashboard_aggregate.go](control-plane/internal/handlers/ui/dashboard_aggregate.go)
- [control-plane/internal/handlers/ui/dashboard_cache.go](control-plane/internal/handlers/ui/dashboard_cache.go)
- [control-plane/internal/handlers/ui/dashboard_format.go](control-plane/internal/handlers/ui/dashboard_format.go)
- [control-plane/internal/handlers/vector_memory.go](control-plane/internal/handlers/vector_memory.go)
- [control-plane/internal/handlers/vector_memory_test.go](control-plane/internal/handlers/vector_memory_test.go)
- [control-plane/internal/server/server_routes_test.go](control-plane/internal/server/server_routes_test.go)
- [control-plane/internal/storage/execution_records.go](control-plane/internal/storage/execution_records.go)
- [control-plane/internal/storage/local.go](control-plane/internal/storage/local.go)
- [control-plane/internal/storage/storage.go](control-plane/internal/storage/storage.go)
- [control-plane/internal/storage/time_parsing_test.go](control-plane/internal/storage/time_parsing_test.go)
- [control-plane/internal/storage/vector_store.go](control-plane/internal/storage/vector_store.go)
- [control-plane/internal/storage/vector_store_postgres.go](control-plane/internal/storage/vector_store_postgres.go)
- [control-plane/internal/storage/vector_store_sqlite.go](control-plane/internal/storage/vector_store_sqlite.go)
- [control-plane/pkg/types/execution.go](control-plane/pkg/types/execution.go)

</details>



The Storage Layer provides the persistence backend for the AgentField control plane. It abstracts database operations behind the `StorageProvider` interface and supports two operational modes: **local** mode using SQLite + BoltDB, and **postgres** mode using PostgreSQL. This layer handles agent registry, workflow executions, memory storage, DID/VC records, and all other persistent state.

For API endpoints that interact with storage, see [API Endpoints](#6.5). For database configuration details, see [Database Configuration](#6.3). For memory-specific operations, see [Memory System](#7).

**Sources:** [control-plane/internal/storage/storage.go:1-11]() [control-plane/internal/storage/local.go:1-30]()

## StorageProvider Interface

The `StorageProvider` interface defines the contract for all storage backends. It encompasses lifecycle management, execution tracking, workflow state, memory operations, agent registry, DID/VC management, and distributed locking.

```mermaid
graph TB
    subgraph "StorageProvider Interface"
        Lifecycle["Lifecycle Methods<br/>Initialize()<br/>Close()<br/>HealthCheck()"]
        Execution["Execution Operations<br/>StoreExecution()<br/>GetExecution()<br/>QueryExecutions()"]
        Workflow["Workflow Operations<br/>StoreWorkflowExecution()<br/>GetWorkflowExecution()<br/>QueryWorkflowExecutions()<br/>UpdateWorkflowExecution()"]
        Memory["Memory Operations<br/>SetMemory()<br/>GetMemory()<br/>DeleteMemory()<br/>ListMemory()"]
        Vector["Vector Operations<br/>SetVector()<br/>DeleteVector()<br/>SimilaritySearch()"]
        Agent["Agent Registry<br/>RegisterAgent()<br/>GetAgent()<br/>ListAgents()<br/>UpdateAgentHealth()"]
        DID["DID Registry<br/>StoreDID()<br/>GetDID()<br/>StoreAgentDID()<br/>StoreComponentDID()"]
        VC["VC Operations<br/>StoreExecutionVC()<br/>GetExecutionVC()<br/>StoreWorkflowVC()"]
        Lock["Distributed Locks<br/>AcquireLock()<br/>ReleaseLock()<br/>RenewLock()"]
        Event["Event Operations<br/>StoreEvent()<br/>GetEventHistory()<br/>PublishMemoryChange()"]
    end
    
    Lifecycle --> Implementation["LocalStorage<br/>NewLocalStorage()<br/>NewPostgresStorage()"]
    Execution --> Implementation
    Workflow --> Implementation
    Memory --> Implementation
    Vector --> Implementation
    Agent --> Implementation
    DID --> Implementation
    VC --> Implementation
    Lock --> Implementation
    Event --> Implementation
```

**Key interface method groups:**

| Category | Methods | Purpose |
|----------|---------|---------|
| Lifecycle | `Initialize()`, `Close()`, `HealthCheck()` | Database connection management [control-plane/internal/storage/storage.go:45-57]() |
| Executions | `StoreExecution()`, `GetExecution()`, `QueryExecutions()` | Agent execution records [control-plane/internal/storage/storage.go:59-71]() |
| Workflows | `StoreWorkflowExecution()`, `GetWorkflowExecution()`, `UpdateWorkflowExecution()` | Workflow state tracking [control-plane/internal/storage/storage.go:73-89]() |
| Memory | `SetMemory()`, `GetMemory()`, `DeleteMemory()`, `ListMemory()` | Key-value memory operations [control-plane/internal/handlers/memory.go:16-20]() |
| Vectors | `SetVector()`, `DeleteVector()`, `SimilaritySearch()` | Vector embeddings for RAG [control-plane/internal/handlers/memory.go:23-27]() |

**Sources:** [control-plane/internal/storage/storage.go:44-127]() [control-plane/internal/handlers/memory.go:16-28]()

## LocalStorage Implementation

The `LocalStorage` struct implements `StorageProvider` and operates in two distinct modes: **local** (SQLite + BoltDB) and **postgres** (PostgreSQL). It utilizes the `DBTX` interface to allow execution of queries against both standard database connections and active transactions.

```mermaid
graph TB
    subgraph "LocalStorage [Code Entity Space]"
        LS["LocalStorage struct"]
        LS --> SQLDB["sqlDatabase *sqlDatabase<br/>Internal SQL wrapper"]
        LS --> GORM["gormDB *gorm.DB<br/>ORM for schema/migrations"]
        LS --> BOLT["kvStore *bolt.DB<br/>BoltDB for local KV mode"]
        LS --> VEC["vectorStore vectorStore<br/>Backend for similarity search"]
    end

    subgraph "Data Access Pattern [Natural Language Space]"
        Upsert["UpdateWorkflowExecution"]
        Fetch["getWorkflowExecutionByID"]
        Scan["scanExecution"]
    end

    Upsert --> SQLDB
    Fetch --> SQLDB
    Scan --> SQLDB
```

**Key functions for Execution Tracking:**
- `CreateExecutionRecord`: Inserts a new execution row into the `executions` table [control-plane/internal/storage/execution_records.go:19-85]().
- `GetExecutionRecord`: Fetches a single execution by `execution_id` [control-plane/internal/storage/execution_records.go:88-110]().
- `UpdateExecutionRecord`: Applies an update callback atomically within a transaction [control-plane/internal/storage/execution_records.go:114-222]().
- `QueryExecutionRecords`: Runs a filtered query based on `ExecutionFilter` [control-plane/internal/storage/execution_records.go:225-260]().

**Sources:** [control-plane/internal/storage/execution_records.go:1-260]() [control-plane/internal/storage/local.go:69-160]()

## SQLite Mode vs PostgreSQL Mode

The system dynamically adapts its behavior based on the configured backend.

### SQLite Mode (Local)
In local mode, AgentField uses SQLite for relational data and BoltDB for key-value memory buckets.
- **Concurrency**: Configured with `WAL` (Write-Ahead Logging) to allow concurrent reads [control-plane/internal/storage/local.go:807-823]().
- **Vector Storage**: Implemented via `sqliteVectorStore`, which stores embeddings as blobs and performs in-memory similarity computation [control-plane/internal/storage/vector_store_sqlite.go:13-23]().
- **Key-Value**: Uses BoltDB buckets (e.g., `workflow`, `session`, `actor`) for memory operations [control-plane/internal/handlers/memory_handler_test.go:32-34]().

### PostgreSQL Mode
In PostgreSQL mode, all data resides in the relational database.
- **Concurrency**: Leverages PostgreSQL's native MVCC and connection pooling [control-plane/internal/storage/vector_store_postgres.go:15-25]().
- **Vector Storage**: Implemented via `postgresVectorStore`, utilizing the `pgvector` extension (using `::vector` and `::jsonb` casts) for efficient database-level similarity search [control-plane/internal/storage/vector_store_postgres.go:41-48]().
- **Memory**: Stores key-value data in a dedicated table rather than BoltDB buckets.

**Sources:** [control-plane/internal/storage/vector_store_sqlite.go:1-23]() [control-plane/internal/storage/vector_store_postgres.go:1-66]() [control-plane/internal/storage/local.go:807-823]()

## Vector Memory Layer

The Vector Storage system provides RAG capabilities across different scopes.

```mermaid
graph LR
    subgraph "Vector Operations [Code Entity Space]"
        SetV["SetVectorHandler"]
        GetV["GetVectorHandler"]
        SearchV["SimilaritySearchHandler"]
    end

    subgraph "Storage Implementation [Natural Language Space]"
        PGV["postgresVectorStore"]
        SLV["sqliteVectorStore"]
    end

    SetV --> PGV
    SetV --> SLV
    SearchV --> PGV
    SearchV --> SLV
```

### Distance Metrics
The system supports multiple distance metrics for vector similarity search:
- **Cosine Distance**: Default metric for similarity.
- **L2 (Euclidean)**: Supported via `VectorDistanceL2`.
- **Dot Product**: Supported via `VectorDistanceDot`.

In PostgreSQL, these map to specific operators like `<->` (L2), `<#>` (Dot), and `<=>` (Cosine) [control-plane/internal/storage/vector_store_postgres.go:238-250]().

### Similarity Search
The `Search` operation filters by `scope` and `scope_id` (e.g., a specific `workflow_id` or `session_id`) and can optionally apply metadata filters using JSONB operators in PostgreSQL [control-plane/internal/storage/vector_store_postgres.go:153-180]().

**Sources:** [control-plane/internal/handlers/vector_memory.go:39-86]() [control-plane/internal/storage/vector_store_postgres.go:238-250]() [control-plane/internal/storage/vector_store_sqlite.go:144-209]()

## Dashboard Aggregation

The Storage Layer provides specialized aggregation methods for the UI Dashboard. The `QueryRunSummaries` method aggregates individual execution records into `RunSummaryAggregation` objects [control-plane/internal/storage/storage.go:13-30]().

This aggregation calculates:
- Total executions per run.
- Status counts (Success vs Failure).
- Earliest and latest start times.
- Root execution details (Reasoner ID, Agent Node ID).

**Sources:** [control-plane/internal/storage/storage.go:13-30]() [control-plane/internal/handlers/ui/dashboard.go:108-120]() [control-plane/internal/storage/storage.go:106-109]()

---

# Page: Database Configuration

# Database Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [control-plane/internal/core/services/dev_service_test.go](control-plane/internal/core/services/dev_service_test.go)
- [control-plane/internal/events/events_test.go](control-plane/internal/events/events_test.go)
- [control-plane/internal/handlers/memory.go](control-plane/internal/handlers/memory.go)
- [control-plane/internal/handlers/memory_handler_test.go](control-plane/internal/handlers/memory_handler_test.go)
- [control-plane/internal/handlers/vector_memory.go](control-plane/internal/handlers/vector_memory.go)
- [control-plane/internal/handlers/vector_memory_test.go](control-plane/internal/handlers/vector_memory_test.go)
- [control-plane/internal/server/server_routes_test.go](control-plane/internal/server/server_routes_test.go)
- [control-plane/internal/storage/local.go](control-plane/internal/storage/local.go)
- [control-plane/internal/storage/local_cleanup_test.go](control-plane/internal/storage/local_cleanup_test.go)
- [control-plane/internal/storage/postgres_test.go](control-plane/internal/storage/postgres_test.go)
- [control-plane/internal/storage/storage.go](control-plane/internal/storage/storage.go)
- [control-plane/internal/storage/storage_parity_test.go](control-plane/internal/storage/storage_parity_test.go)
- [control-plane/internal/storage/vector_store.go](control-plane/internal/storage/vector_store.go)
- [control-plane/internal/storage/vector_store_postgres.go](control-plane/internal/storage/vector_store_postgres.go)
- [control-plane/internal/storage/vector_store_sqlite.go](control-plane/internal/storage/vector_store_sqlite.go)

</details>



## Purpose and Scope

This document describes how to configure the database backends used by the AgentField control plane. AgentField supports two storage modes: **SQLite** for local development and **PostgreSQL** for production deployments. This page covers connection parameters, performance tuning, schema initialization, and vector storage setup.

For information about the storage layer architecture and interfaces, see [Storage Layer](6.2). For general control plane configuration options, see [Server Configuration](6.1).

---

## Configuration Modes

AgentField's storage layer operates in one of two modes, determined by the `mode` field in the `StorageConfig`:

| Mode | Primary Database | Key-Value Store | Use Case |
|------|-----------------|-----------------|----------|
| `local` | SQLite | BoltDB | Development, single-node deployments |
| `postgres` | PostgreSQL | PostgreSQL tables | Production, distributed deployments |

The mode is typically set via the `AGENTFIELD_STORAGE_MODE` environment variable.

**Sources:** [control-plane/internal/storage/storage.go:207-213](), [control-plane/internal/storage/storage.go:260-272]()

---

## SQLite Configuration

### Database Path and Initialization

In `local` mode, the `LocalStorage` implementation handles SQLite initialization. It automatically converts relative paths to absolute paths and ensures the database directory exists.

```mermaid
graph TB
    Config["StorageConfig<br/>(mode: local)"]
    Init["initializeSQLite()"]
    PathValidate["Validate DatabasePath"]
    AbsPath["Convert to Absolute Path"]
    CreateDir["os.MkdirAll(dbDir, 0755)"]
    DSN["Construct DSN String"]
    OpenDB["sql.Open('sqlite3', dsn)"]
    SetPool["Configure Connection Pool"]
    SetPragmas["Execute PRAGMA Statements"]
    InitGorm["initGormDB()"]
    CreateSchema["createSchema()"]
    WALWorker["Start periodicWALCheckpoint()"]
    BoltDB["Open BoltDB at KVStorePath"]
    
    Config --> Init
    Init --> PathValidate
    PathValidate --> AbsPath
    AbsPath --> CreateDir
    CreateDir --> DSN
    DSN --> OpenDB
    OpenDB --> SetPool
    SetPool --> SetPragmas
    SetPragmas --> InitGorm
    InitGorm --> CreateSchema
    CreateSchema --> WALWorker
    WALWorker --> BoltDB
```

**Sources:** [control-plane/internal/storage/local.go:504-586]()

### WAL Mode and Performance Pragmas

The SQLite DSN is constructed with specific parameters optimized for the AgentField workflow engine, specifically utilizing Write-Ahead Logging (WAL) for concurrent read/write performance.

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `_journal_mode` | `WAL` | Enables concurrent reads and writes |
| `_synchronous` | `NORMAL` | Optimized for WAL mode durability |
| `_busy_timeout` | Configurable | Prevents "database is locked" errors during contention |
| `_foreign_keys` | `ON` | Enforces relational integrity |
| `_wal_autocheckpoint`| `1000` | Triggers automatic WAL checkpoints |

**Sources:** [control-plane/internal/storage/local.go:534-540](), [control-plane/internal/storage/local.go:557-567]()

### SQLite Vector Storage

When using SQLite, vector embeddings are stored in the `memory_vectors` table. Since SQLite lacks a native vector type, embeddings are encoded as binary blobs.

- **Encoding**: `encodeEmbedding` converts `[]float32` to little-endian bytes. [control-plane/internal/storage/vector_store.go:43-49]()
- **Search**: Performed via `sqliteVectorStore.Search`, which performs an exhaustive scan (flat search) and computes similarity in-memory using `computeSimilarity`. [control-plane/internal/storage/vector_store_sqlite.go:144-209]()

---

## PostgreSQL Configuration

### Connection Pooling and Management

PostgreSQL mode is implemented via `NewPostgresStorage`. It manages a connection pool using the standard library `sql.DB` with `pgx` as the driver.

```mermaid
graph LR
    subgraph "Connection Management"
        DSN["DSN / URL"]
        MaxOpen["MaxOpenConns (Default: 25)"]
        MaxIdle["MaxIdleConns (Default: 5)"]
        Lifetime["ConnMaxLifetime (Default: 30m)"]
    end

    subgraph "Storage Entities"
        ExecRec["types.Execution"]
        WFExec["types.WorkflowExecution"]
        KVStore["kv_store table"]
        VecStore["memory_vectors table"]
    end

    DSN --> MaxOpen
    MaxOpen --> MaxIdle
    MaxIdle --> Lifetime
    Lifetime --> ExecRec
    Lifetime --> WFExec
    Lifetime --> KVStore
    Lifetime --> VecStore
```

**Sources:** [control-plane/internal/storage/local.go:706-728](), [control-plane/internal/storage/postgres_test.go:25-33]()

### Automatic Database Creation

If the target database does not exist, the storage provider attempts to connect to the `AdminDatabase` (defaulting to `postgres`) to execute `CREATE DATABASE`.

**Sources:** [control-plane/internal/storage/local.go:730-800]()

### Full-Text Search (FTS) and Vectors

PostgreSQL mode leverages advanced features for agent performance:

1.  **FTS Setup**: Creates a `workflow_executions_fts` table and a GIN index on a `TSVECTOR` column to allow fast searching of workflow logs and metadata. [control-plane/internal/storage/local.go:973-1029]()
2.  **Vector Store**: Uses the `pgvector` extension. The `postgresVectorStore` handles `ON CONFLICT` upserts and similarity searches using native PostgreSQL operators like `<->` (L2) and `<=>` (Cosine). [control-plane/internal/storage/vector_store_postgres.go:27-65](), [control-plane/internal/storage/vector_store_postgres.go:238-250]()

---

## Memory and Vector Schema

The storage layer provides a unified interface for both standard memory and vector memory across both backends.

### Key-Value Store (Memory)
In PostgreSQL, memory is stored in the `kv_store` table, supporting multiple scopes (workflow, session, actor, global).

```sql
CREATE TABLE kv_store (
    scope TEXT NOT NULL,
    scope_id TEXT NOT NULL,
    key TEXT NOT NULL,
    value JSONB NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (scope, scope_id, key)
);
```
**Sources:** [control-plane/internal/storage/local.go:912-925]()

### Vector Storage (RAG Support)
Vector records include the embedding, metadata, and scope information.

```mermaid
classDiagram
    class VectorRecord {
        +string Scope
        +string ScopeID
        +string Key
        +[]float32 Embedding
        +map[string]interface Metadata
    }
    class vectorStore {
        <<interface>>
        +Set(ctx, record) error
        +Get(ctx, scope, id, key) *VectorRecord
        +Search(ctx, scope, id, query, topK, filters) []VectorSearchResult
    }
    VectorRecord --* vectorStore
```

**Sources:** [control-plane/internal/storage/vector_store.go:16-22](), [control-plane/pkg/types/types.go]() (implied)

---

## Initialization Flow

The `StorageFactory` determines the backend at runtime.

1.  **Factory Selection**: Based on `StorageConfig.Mode`. [control-plane/internal/storage/storage.go:260-307]()
2.  **Lifecycle**: `Initialize` is called, which triggers backend-specific setup (`initializeSQLite` or `initializePostgres`). [control-plane/internal/storage/local.go:504-586](), [control-plane/internal/storage/local.go:601-728]()
3.  **Schema Enforcement**: `createSchema` runs migrations, ensures tables, and creates indexes. [control-plane/internal/storage/local.go:826-858]()

**Sources:** [control-plane/internal/storage/local.go:504-858](), [control-plane/internal/storage/storage.go:260-307]()

---

# Page: Agent Registration

# Agent Registration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [control-plane/internal/core/services/agent_service.go](control-plane/internal/core/services/agent_service.go)
- [control-plane/internal/core/services/package_service.go](control-plane/internal/core/services/package_service.go)
- [control-plane/internal/handlers/nodes_register.go](control-plane/internal/handlers/nodes_register.go)
- [control-plane/internal/handlers/nodes_serverless_ssrf_test.go](control-plane/internal/handlers/nodes_serverless_ssrf_test.go)
- [control-plane/internal/observability/telemetry.go](control-plane/internal/observability/telemetry.go)
- [control-plane/internal/observability/telemetry_test.go](control-plane/internal/observability/telemetry_test.go)
- [control-plane/internal/packages/config_version_fixtures_test.go](control-plane/internal/packages/config_version_fixtures_test.go)
- [control-plane/internal/packages/go_runtime_test.go](control-plane/internal/packages/go_runtime_test.go)
- [control-plane/internal/packages/gointerp.go](control-plane/internal/packages/gointerp.go)
- [control-plane/internal/packages/installer.go](control-plane/internal/packages/installer.go)
- [control-plane/internal/packages/runner.go](control-plane/internal/packages/runner.go)
- [deployments/docker/README.md](deployments/docker/README.md)
- [deployments/docker/docker-compose.yml](deployments/docker/docker-compose.yml)
- [docs/installing-agent-nodes.md](docs/installing-agent-nodes.md)

</details>



## Purpose and Scope

This page documents how agent nodes register themselves with the AgentField control plane. Registration establishes the agent's identity, advertises its capabilities (reasoners and skills), and provides callback URLs for the control plane to invoke agent functions.

In the AgentField ecosystem, registration is the bridge between a standalone agent process (Node) and the central orchestration layer (Control Plane).

---

## Overview

Agent registration is the process by which an agent node announces itself to the control plane and declares:

- **Node Identity**: Unique `node_id` used for routing and discovery. [control-plane/internal/packages/installer.go:148-150]()
- **Capabilities**: A list of reasoners (AI-powered functions) and skills (deterministic functions) that the agent can perform. [control-plane/internal/packages/installer.go:163-172]()
- **Callback URLs**: The HTTP endpoint(s) where the control plane can reach the agent to trigger executions. [control-plane/internal/handlers/nodes_register.go:38-65]()
- **Metadata**: Version, author, description, and required environment variables. [control-plane/internal/packages/installer.go:101-126]()

Registration occurs automatically when an agent starts via the CLI (`af run`) or the SDK, but it can also be handled for serverless environments.

**Sources:** [control-plane/internal/packages/installer.go:101-172](), [control-plane/internal/handlers/nodes_register.go:38-65]()

---

## Registration Flow

The registration process involves the Control Plane validating the agent's reachability and persisting its manifest into the registry.

### High-Level Sequence

```mermaid
sequenceDiagram
    participant Agent as "Agent Node (Process)"
    participant CP_Reg as "Control Plane<br/>/api/v1/nodes/register"
    participant Storage as "RegistryStorage<br/>(installed.yaml)"
    participant PM as "ProcessManager"

    Note over Agent,PM: 1. Node Startup (af run)
    PM->>Agent: "Launch with PORT & AGENTFIELD_SERVER"
    Agent->>Agent: "Initialize SDK & Listen on PORT"
    
    Note over Agent,PM: 2. Registration Request
    Agent->>CP_Reg: "POST /api/v1/nodes/register"
    Note right of Agent: Payload includes node_id, <br/>capabilities, and callback_url
    
    Note over CP_Reg,Storage: 3. Validation & Persistence
    CP_Reg->>CP_Reg: "validateCallbackURL()"
    CP_Reg->>CP_Reg: "resolveCallbackCandidates()"
    CP_Reg->>Storage: "Update Runtime Info (Port, PID, Status)"
    Storage-->>CP_Reg: "Success"
    
    Note over CP_Reg,Agent: 4. Confirmation
    CP_Reg-->>Agent: "200 OK (Registration Successful)"
    Agent->>Agent: "Start Heartbeat Loop"
```

**Sources:** [control-plane/internal/core/services/agent_service.go:53-160](), [control-plane/internal/handlers/nodes_register.go:91-131](), [control-plane/internal/packages/runner.go:28-109]()

---

## Callback URL Discovery

The control plane must be able to reach the agent. Because agents often run in complex networking environments (Docker, NAT, Serverless), AgentField uses a discovery mechanism to find the best "Callback URL".

### Callback Candidate Resolution

When an agent registers, it provides a list of candidates. The control plane attempts to normalize and select the most viable one.

| Method | Description | Code Entity |
| :--- | :--- | :--- |
| **Preferred** | The URL explicitly provided by the agent SDK. | `discovery.Preferred` |
| **Candidates** | A list of alternative URLs (e.g., local IPs, container hostnames). | `discovery.Candidates` |
| **Client IP** | The IP address from which the registration request originated. | `clientIP` |
| **Normalization** | Rebuilding the URL to ensure correct scheme, host, and port. | `normalizeCandidate` |

**Sources:** [control-plane/internal/handlers/nodes_register.go:91-131](), [control-plane/internal/handlers/nodes_register.go:133-185]()

### Serverless SSRF Protection

For serverless agents, the control plane implements strict Serverless Service Request Forgery (SSRF) protection. The `invocation_url` is reconstructed from validated components to prevent attackers from using the control plane as a proxy to scan internal networks.

```mermaid
graph TD
    subgraph "Validation Logic: normalizeServerlessDiscoveryURL"
        Input["Raw Invocation URL"] --> Parse["url.Parse()"]
        Parse --> SchemeCheck{"Scheme == http/https?"}
        SchemeCheck -- "No" --> Reject["Reject Request"]
        SchemeCheck -- "Yes" --> HostCheck{"Host in Allowlist?"}
        HostCheck -- "No" --> Reject
        HostCheck -- "Yes" --> PathClean["Clean Path Traversal (..)"]
        PathClean --> Rebuild["Reassemble URL<br/>(No User-Info/Query/Fragment)"]
    end
    Rebuild --> Output["Safe Discovery URL"]
```

**Sources:** [control-plane/internal/handlers/nodes_register.go:215-229](), [control-plane/internal/handlers/nodes_register.go:235-267]()

---

## The Manifest: `agentfield-package.yaml`

The registration data is derived from the `PackageMetadata` struct, which represents the `agentfield-package.yaml` file.

### Key Registration Fields

| Field | YAML Key | Description |
| :--- | :--- | :--- |
| **Node ID** | `agent_node.node_id` | The unique ID used in the system. [control-plane/internal/packages/installer.go:148]() |
| **Capabilities** | `capabilities` | Defines `reasoners` and `skills`. [control-plane/internal/packages/installer.go:163-166]() |
| **Entrypoint** | `entrypoint.start` | The command used to launch the process. [control-plane/internal/packages/installer.go:130-136]() |
| **Healthcheck** | `entrypoint.healthcheck` | The path the control plane polls to verify readiness. [control-plane/internal/packages/installer.go:142]() |

**Sources:** [control-plane/internal/packages/installer.go:101-150](), [docs/installing-agent-nodes.md:35-86]()

---

## Implementation Details

### Runtime State Management

The control plane tracks the status of registered agents in a registry (usually `installed.yaml` in local mode).

```mermaid
classDiagram
    class InstalledPackage {
        +String Name
        +String Path
        +String Status
        +RuntimeInfo Runtime
    }
    class RuntimeInfo {
        +Int Port
        +Int PID
        +String LogFile
        +Time LastHeartbeat
    }
    class PackageMetadata {
        +String ConfigVersion
        +String Name
        +CapabilityConfig Capabilities
        +EntrypointConfig Entrypoint
    }
    InstalledPackage *-- RuntimeInfo
    InstalledPackage ..> PackageMetadata : parsed from
```

**Sources:** [control-plane/internal/core/services/agent_service.go:139-142](), [control-plane/internal/packages/installer.go:101-126](), [control-plane/internal/packages/runner.go:39-47]()

### Process Lifecycle and Registration

When `DefaultAgentService.RunAgent` is called:
1. It loads the registry to verify the agent is installed. [control-plane/internal/core/services/agent_service.go:64-73]()
2. It reconciles the process state (checking if the PID is still alive). [control-plane/internal/core/services/agent_service.go:79-86]()
3. It allocates a free port (defaulting to 8001 range). [control-plane/internal/core/services/agent_service.go:98-107]()
4. It launches the process and waits for the health check. [control-plane/internal/core/services/agent_service.go:121-135]()
5. Once healthy, the agent's runtime info is updated, marking it as "registered" and "running". [control-plane/internal/core/services/agent_service.go:139-142]()

**Sources:** [control-plane/internal/core/services/agent_service.go:53-160](), [control-plane/internal/packages/runner.go:112-137]()

---

## Registration Best Practices

1. **Unique Node IDs**: Ensure `node_id` is unique within your control plane to avoid routing collisions.
2. **Health Checks**: Implement the `/health` endpoint (or your custom `healthcheck` path) to return a 200 OK only when the agent is fully initialized.
3. **Environment Variables**: Use the `user_environment` section in the manifest to declare required secrets (like API keys). The control plane will ensure these are present before registration. [control-plane/internal/packages/installer.go:94-98]()
4. **Language Detection**: While the system can detect "go" or "python" automatically, explicitly setting `language` in the manifest is recommended for clarity. [control-plane/internal/packages/installer.go:112-118]()

**Sources:** [docs/installing-agent-nodes.md:41-86](), [control-plane/internal/packages/installer.go:53-98]()

---

# Page: API Endpoints

# API Endpoints

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [control-plane/internal/handlers/coverage_handlers_90_test.go](control-plane/internal/handlers/coverage_handlers_90_test.go)
- [control-plane/internal/handlers/did_handlers.go](control-plane/internal/handlers/did_handlers.go)
- [control-plane/internal/handlers/execute.go](control-plane/internal/handlers/execute.go)
- [control-plane/internal/handlers/execute_async_test.go](control-plane/internal/handlers/execute_async_test.go)
- [control-plane/internal/handlers/execute_status_update_test.go](control-plane/internal/handlers/execute_status_update_test.go)
- [control-plane/internal/handlers/execution_notes.go](control-plane/internal/handlers/execution_notes.go)
- [control-plane/internal/handlers/execution_notes_test.go](control-plane/internal/handlers/execution_notes_test.go)
- [control-plane/internal/handlers/execution_status_handler_test.go](control-plane/internal/handlers/execution_status_handler_test.go)
- [control-plane/internal/handlers/workflow_execution_events.go](control-plane/internal/handlers/workflow_execution_events.go)
- [control-plane/internal/handlers/workflow_execution_events_test.go](control-plane/internal/handlers/workflow_execution_events_test.go)
- [control-plane/internal/server/routes_core.go](control-plane/internal/server/routes_core.go)
- [control-plane/internal/server/routes_ui.go](control-plane/internal/server/routes_ui.go)
- [control-plane/internal/storage/retry_test.go](control-plane/internal/storage/retry_test.go)
- [control-plane/web/client/src/components/reasoners/ExecutionForm.tsx](control-plane/web/client/src/components/reasoners/ExecutionForm.tsx)
- [control-plane/web/client/src/components/runs/RunLifecycleMenu.tsx](control-plane/web/client/src/components/runs/RunLifecycleMenu.tsx)
- [control-plane/web/client/src/components/ui/auto-expanding-textarea.tsx](control-plane/web/client/src/components/ui/auto-expanding-textarea.tsx)
- [control-plane/web/client/src/pages/RunDetailPage.tsx](control-plane/web/client/src/pages/RunDetailPage.tsx)
- [control-plane/web/client/src/test/pages/RunDetailPage.test.tsx](control-plane/web/client/src/test/pages/RunDetailPage.test.tsx)
- [sdk/python/agentfield/agent_workflow.py](sdk/python/agentfield/agent_workflow.py)

</details>



## Purpose and Scope

This page documents the REST API endpoints exposed by the AgentField Control Plane. The Control Plane provides a unified HTTP/WebSocket API for agent registration, execution, memory management, identity, and observability. It acts as the orchestrator for the "Kubernetes for AI Agents" model, managing the lifecycle and communication between distributed agent nodes.

---

## API Overview

### Base URL and Versioning

The Control Plane serves all core agent-facing REST surface under the `/api/v1/` prefix [control-plane/internal/server/routes_core.go:25-27](). Browser-facing UI APIs are served under `/api/ui/v1` and `/api/ui/v2` [control-plane/internal/server/routes_ui.go:42-44]().

### Authentication and Authorization

When DID-based authorization is enabled, the Control Plane applies `PermissionCheckMiddleware` to both legacy and unified execution endpoints [control-plane/internal/server/routes_core.go:67-85](). Internal communication between the control plane and agents often utilizes an `InternalToken` sent as an `Authorization` header [control-plane/internal/handlers/execute.go:141-142]().

### Context Propagation Headers

The Control Plane propagates execution context to maintain workflow integrity and memory scoping [control-plane/internal/handlers/execute.go:110-116](). Key headers include:
* `X-Workflow-ID`: Unique identifier for the workflow.
* `X-Execution-ID`: Unique identifier for this specific execution.
* `X-Agent-Node-ID`: The ID of the node performing the work.

---

## Execution API

### Unified Execution

```
POST /api/v1/execute/:target
POST /api/v1/execute/async/:target
```

The unified execution endpoint routes requests to the appropriate agent and reasoner. The `:target` parameter typically follows the format `agent_id.reasoner_id`.

#### Request Structure (`ExecuteRequest`)
[control-plane/internal/handlers/execute.go:50-54]()
```json
{
  "input": { "key": "value" },
  "context": { "session_id": "..." },
  "webhook": {
    "url": "https://example.com/callback",
    "secret": "optional-secret"
  }
}
```

#### Synchronous Response (`ExecuteResponse`)
[control-plane/internal/handlers/execute.go:64-74]()
Returns HTTP 200 upon completion.

#### Asynchronous Response (`AsyncExecuteResponse`)
[control-plane/internal/handlers/execute.go:77-88]()
Returns HTTP 202 Accepted. If the internal async queue is full, it returns 503 Service Unavailable [control-plane/internal/handlers/execute_async_test.go:90-93]().

### Execution Status and Control

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/executions/:execution_id` | GET | Get current status, result, or error [control-plane/internal/server/routes_core.go:120]() |
| `/api/v1/executions/batch-status` | POST | Fetch multiple statuses at once [control-plane/internal/handlers/execute.go:111-113]() |
| `/api/v1/executions/:execution_id/status` | POST | Used by agents to update the control plane on progress [control-plane/internal/server/routes_core.go:123]() |
| `/api/v1/executions/:execution_id/cancel` | POST | Aborts an in-flight execution [control-plane/internal/server/routes_core.go:127]() |

### Execution Data Flow

This diagram maps the HTTP request flow to the internal Go structures and handlers.

```mermaid
sequenceDiagram
    participant Client
    participant Router["gin.Engine"]
    participant Handler["ExecuteHandlerWithARD"]
    participant Controller["executionController"]
    participant Agent["Agent Node (HTTP)"]

    Client->>Router: POST /api/v1/execute/node.reasoner
    Router->>Handler: Invoke Handler
    Handler->>Controller: prepareExecution()
    Controller->>Agent: Forward Request (POST /execute)
    Agent-->>Controller: JSON Result
    Controller->>Handler: Return Result
    Handler-->>Client: ExecuteResponse
```
**Sources:** [control-plane/internal/server/routes_core.go:110-114](), [control-plane/internal/handlers/execute.go:134-144]()

---

## Agent & Node Management

### Registration and Lifecycle

Agents register themselves to become discoverable and reachable by the control plane.

* **Register Node**: `POST /api/v1/nodes/register` [control-plane/internal/server/routes_core.go:39]().
* **Heartbeat**: `POST /api/v1/nodes/:node_id/heartbeat` [control-plane/internal/server/routes_core.go:44](). Agents must send periodic heartbeats to maintain a "healthy" status.
* **Status Lease**: `PATCH /api/v1/nodes/:node_id/status` [control-plane/internal/server/routes_core.go:57]().

### Discovery

* **Capabilities**: `GET /api/v1/discovery/capabilities` [control-plane/internal/server/routes_core.go:34]().
* **List Reasoners**: `GET /api/v1/reasoners` [control-plane/internal/server/routes_core.go:36]().

---

## UI and Observability API

The Control Plane provides a specialized API surface for the `web/client` dashboard under `/api/ui/v1`.

### Agent and Node Management (UI)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ui/v1/agents/packages` | GET | List available agent packages [control-plane/internal/server/routes_ui.go:57]() |
| `/api/ui/v1/nodes/summary` | GET | High-level overview of node health [control-plane/internal/server/routes_ui.go:97]() |
| `/api/ui/v1/nodes/:nodeId/logs` | GET | Proxy to fetch logs directly from an agent node [control-plane/internal/server/routes_ui.go:118]() |

### Execution and Workflow Observability

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ui/v1/executions/summary` | GET | Aggregated execution stats [control-plane/internal/server/routes_ui.go:149]() |
| `/api/ui/v1/executions/timeline` | GET | Hourly aggregated execution data [control-plane/internal/server/routes_ui.go:156]() |
| `/api/ui/v1/workflows/:id/vc-chain` | GET | Export the VC audit trail [control-plane/web/client/src/pages/RunDetailPage.tsx:106]() |

### UI Entity Mapping

This diagram associates UI components with the API endpoints they consume.

```mermaid
graph TD
    subgraph "Frontend (React)"
        RDP["RunDetailPage.tsx"]
        LC["RunLifecycleMenu.tsx"]
        EF["ExecutionForm.tsx"]
    end

    subgraph "Control Plane (Go)"
        UIA["routes_ui.go"]
        COREA["routes_core.go"]
    end

    RDP -- "GET /api/ui/v1/executions/:id/details" --> UIA
    RDP -- "GET /api/ui/v1/workflows/:id/vc-chain" --> UIA
    LC -- "POST /api/v1/executions/:id/pause" --> COREA
    EF -- "POST /api/v1/execute/:target" --> COREA
```
**Sources:** [control-plane/web/client/src/pages/RunDetailPage.tsx:101-107](), [control-plane/internal/server/routes_ui.go:163-167](), [control-plane/web/client/src/components/runs/RunLifecycleMenu.tsx:87-99]()

---

## Identity & DID API

AgentField implements W3C Decentralized Identifiers (DIDs) for secure agent identity.

* **Resolve DID**: `GET /api/v1/did/resolve/:did` [control-plane/internal/handlers/did_handlers.go:118](). This handles both `did:key` and `did:web` resolution [control-plane/internal/handlers/did_handlers.go:126-143]().
* **Rotate Key**: `POST /api/v1/did/key-agreement/rotate` [control-plane/internal/handlers/did_handlers.go:173](). Rotates an agent's X25519 encryption keys.

---

## Internal Event Handling

Agents can emit fire-and-forget events to the Control Plane to track local execution steps within a larger workflow.

* **Workflow Events**: `POST /api/v1/workflows/events` [control-plane/internal/handlers/workflow_execution_events.go:35]().
* This endpoint uses `WorkflowExecutionEventRequest` [control-plane/internal/handlers/workflow_execution_events.go:16-30]() to update or create execution records, ensuring the UI can render a complete DAG even for steps executed locally by an agent [control-plane/internal/handlers/workflow_execution_events.go:32-34]().

### Event Logic Flow
1. Agent emits `WorkflowExecutionEventRequest`.
2. Handler checks for existing `ExecutionID` [control-plane/internal/handlers/workflow_execution_events.go:46]().
3. If new, it calls `CreateExecutionRecord` [control-plane/internal/handlers/workflow_execution_events.go:53]().
4. If existing, it applies `applyEventToExecution` to update status, but guards against terminal state regression [control-plane/internal/handlers/workflow_execution_events.go:130-144]().

**Sources:** [control-plane/internal/handlers/workflow_execution_events.go:1-190]()

---

# Page: Memory System

# Memory System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [control-plane/internal/handlers/memory.go](control-plane/internal/handlers/memory.go)
- [control-plane/internal/handlers/memory_handler_test.go](control-plane/internal/handlers/memory_handler_test.go)
- [control-plane/internal/handlers/vector_memory.go](control-plane/internal/handlers/vector_memory.go)
- [control-plane/internal/handlers/vector_memory_test.go](control-plane/internal/handlers/vector_memory_test.go)
- [control-plane/internal/server/server_routes_test.go](control-plane/internal/server/server_routes_test.go)
- [control-plane/internal/storage/local.go](control-plane/internal/storage/local.go)
- [control-plane/internal/storage/storage.go](control-plane/internal/storage/storage.go)
- [control-plane/internal/storage/vector_store.go](control-plane/internal/storage/vector_store.go)
- [control-plane/internal/storage/vector_store_postgres.go](control-plane/internal/storage/vector_store_postgres.go)
- [control-plane/internal/storage/vector_store_sqlite.go](control-plane/internal/storage/vector_store_sqlite.go)
- [sdk/python/agentfield/memory.py](sdk/python/agentfield/memory.py)
- [sdk/python/agentfield/memory_events.py](sdk/python/agentfield/memory_events.py)
- [sdk/python/tests/test_memory_scope_kwargs.py](sdk/python/tests/test_memory_scope_kwargs.py)
- [sdk/typescript/src/context/SkillContext.ts](sdk/typescript/src/context/SkillContext.ts)
- [sdk/typescript/src/memory/MemoryClient.ts](sdk/typescript/src/memory/MemoryClient.ts)
- [sdk/typescript/src/memory/MemoryEventClient.ts](sdk/typescript/src/memory/MemoryEventClient.ts)
- [sdk/typescript/src/memory/MemoryInterface.ts](sdk/typescript/src/memory/MemoryInterface.ts)
- [sdk/typescript/tests/memory_and_discovery.test.ts](sdk/typescript/tests/memory_and_discovery.test.ts)
- [sdk/typescript/tests/memory_event_client.test.ts](sdk/typescript/tests/memory_event_client.test.ts)
- [tests/functional/agents/memory_events_decorator_agent.py](tests/functional/agents/memory_events_decorator_agent.py)
- [tests/functional/tests/test_memory_events.py](tests/functional/tests/test_memory_events.py)

</details>



The Memory System provides distributed, scoped key-value storage and vector search capabilities for AgentField agents. It enables agents to persist state, share data across execution contexts, and perform similarity searches for RAG (Retrieval-Augmented Generation) applications. The system supports four hierarchical scopes (workflow, session, actor, global), automatic context propagation via HTTP headers, and real-time change notifications via WebSocket.

For memory scope semantics and fallback behavior, see [Memory Scopes](#7.1). For basic storage operations, see [Key-Value Operations](#7.2). For vector embeddings and similarity search, see [Vector Storage](#7.3). For event subscriptions and pattern matching, see [Memory Events](#7.4). For execution context header propagation, see [Context Propagation](#7.5).

## Architecture Overview

The Memory System is organized into three primary layers: the developer-facing API, the HTTP client layer, and the storage backend.

### Memory System Layers

```mermaid
graph TB
    subgraph "Developer API Layer"
        MemoryInterface["MemoryInterface<br/>(Python/TypeScript)"]
        ScopedMemoryClient["ScopedMemoryClient"]
        GlobalMemoryClient["GlobalMemoryClient"]
    end
    
    subgraph "Client Layer"
        MemoryClient["MemoryClient"]
        MemoryEventClient["MemoryEventClient<br/>(WebSocket)"]
    end
    
    subgraph "Control Plane HTTP API"
        MemorySetEndpoint["/api/v1/memory/set"]
        MemoryGetEndpoint["/api/v1/memory/get"]
        MemoryDeleteEndpoint["/api/v1/memory/delete"]
        MemoryListEndpoint["/api/v1/memory/list"]
        VectorSetEndpoint["/api/v1/memory/vector/set"]
        VectorSearchEndpoint["/api/v1/memory/vector/search"]
        VectorDeleteEndpoint["/api/v1/memory/vector/delete"]
        EventsWebSocket["/api/v1/memory/events/ws"]
    end
    
    subgraph "Storage Backend"
        SQLiteKV["SQLite tables<br/>(local mode)"]
        BoltDB["BoltDB buckets<br/>(local mode)"]
        PostgresKV["PostgreSQL tables<br/>(production mode)"]
        VectorStore["pgvector extension<br/>(optional)"]
    end
    
    MemoryInterface --> MemoryClient
    ScopedMemoryClient --> MemoryClient
    GlobalMemoryClient --> MemoryClient
    MemoryInterface --> MemoryEventClient
    
    MemoryClient --> MemorySetEndpoint
    MemoryClient --> MemoryGetEndpoint
    MemoryClient --> MemoryDeleteEndpoint
    MemoryClient --> MemoryListEndpoint
    MemoryClient --> VectorSetEndpoint
    MemoryClient --> VectorSearchEndpoint
    MemoryClient --> VectorDeleteEndpoint
    
    MemoryEventClient --> EventsWebSocket
    
    MemorySetEndpoint --> SQLiteKV
    MemorySetEndpoint --> PostgresKV
    MemoryGetEndpoint --> SQLiteKV
    MemoryGetEndpoint --> PostgresKV
    
    VectorSetEndpoint --> BoltDB
    VectorSetEndpoint --> VectorStore
    VectorSearchEndpoint --> BoltDB
    VectorSearchEndpoint --> VectorStore
```

**Sources:** [sdk/python/agentfield/memory.py:132-150](), [sdk/typescript/src/memory/MemoryClient.ts:117-206](), [sdk/typescript/src/memory/MemoryInterface.ts:1-226](), [sdk/typescript/src/memory/MemoryEventClient.ts:13-29](), [control-plane/internal/handlers/memory.go:54-171]()

### Memory Client Class Hierarchy

```mermaid
classDiagram
    class MemoryClient {
        +agentfield_client: AgentFieldClient
        +execution_context: ExecutionContext
        +agent_node_id: str
        +set(key, data, scope, scope_id)
        +get(key, default, scope, scope_id)
        +delete(key, scope, scope_id)
        +exists(key, scope, scope_id)
        +list_keys(scope, scope_id)
        +set_vector(key, embedding, metadata, scope, scope_id)
        +similarity_search(query_embedding, top_k, scope, scope_id, filters)
        +delete_vector(key, scope, scope_id)
        -_build_headers(scope, scope_id)
    }
    
    class MemoryInterface {
        +memory_client: MemoryClient
        +events: MemoryEventClient
        +set(key, data)
        +get(key, default)
        +delete(key)
        +exists(key)
        +set_vector(key, embedding, metadata)
        +similarity_search(query_embedding, top_k, filters)
        +on_change(patterns)
        +session(session_id)
        +actor(actor_id)
        +workflow(workflow_id)
        +global_scope
    }
    
    class ScopedMemoryClient {
        +memory_client: MemoryClient
        +scope: str
        +scope_id: str
        +events: ScopedMemoryEventClient
        +set(key, data)
        +get(key, default)
        +delete(key)
        +exists(key)
        +list_keys()
        +set_vector(key, embedding, metadata)
        +delete_vector(key)
        +similarity_search(query_embedding, top_k, filters)
        +on_change(patterns)
    }
    
    class GlobalMemoryClient {
        +memory_client: MemoryClient
        +event_client: MemoryEventClient
        +set(key, data)
        +get(key, default)
        +delete(key)
        +exists(key)
        +list_keys()
        +set_vector(key, embedding, metadata)
        +delete_vector(key)
        +similarity_search(query_embedding, top_k, filters)
        +on_change(patterns)
    }
    
    class MemoryEventClient {
        +connect(patterns, scope, scope_id)
        +subscribe(patterns, callback, scope, scope_id)
        +history(options)
    }
    
    MemoryInterface --> MemoryClient
    MemoryInterface --> MemoryEventClient
    ScopedMemoryClient --> MemoryClient
    GlobalMemoryClient --> MemoryClient
```

**Sources:** [sdk/python/agentfield/memory.py:132-724](), [sdk/python/agentfield/memory_events.py:83-200]()

## Memory Scopes and Hierarchical Fallback

The Memory System organizes data into four hierarchical scopes that determine visibility and lifetime:

| Scope | Identifier Header | Lifetime | Use Case |
|-------|------------------|----------|----------|
| `workflow` | `X-Workflow-ID` | Duration of workflow execution | Temporary state for multi-agent workflows |
| `session` | `X-Session-ID` | Duration of user session | User-specific preferences and conversation history |
| `actor` | `X-Actor-ID` | Duration of actor interaction | Individual agent or entity state |
| `global` | None (implicit `"global"`) | Permanent | System-wide configuration and shared data |

### Hierarchical Lookup Order

When retrieving data without specifying an explicit scope, the system performs a hierarchical fallback search in the order: `workflow` → `session` → `actor` → `global`, returning the first match found.

```mermaid
sequenceDiagram
    participant App as "app.memory.get('key')"
    participant Interface as "MemoryInterface"
    participant Client as "MemoryClient"
    participant API as "Control Plane API"
    
    App->>Interface: get('user_preference')
    Interface->>Client: get(scope='workflow', scope_id='wf-123')
    Client->>API: POST /api/v1/memory/get<br/>X-Workflow-ID: wf-123
    API-->>Client: 404 Not Found
    
    Interface->>Client: get(scope='session', scope_id='sess-456')
    Client->>API: POST /api/v1/memory/get<br/>X-Session-ID: sess-456
    API-->>Client: 200 OK {data: "dark_mode"}
    
    Client-->>Interface: "dark_mode"
    Interface-->>App: "dark_mode"
```

**Sources:** [sdk/python/agentfield/memory.py:47-57](), [sdk/python/agentfield/memory.py:225-250](), [sdk/typescript/src/memory/MemoryClient.ts:77-104]()

## Developer-Facing API

The Memory System is accessed through the `memory` property on agent contexts. This property exposes a `MemoryInterface` instance that provides both automatic-scoped and explicitly-scoped operations.

### Python SDK API Surface

```python
# Automatic scoping based on execution context
await ctx.memory.set("user_name", "Alice")
name = await ctx.memory.get("user_name")
await ctx.memory.delete("user_name")

# Vector operations
await ctx.memory.set_vector("doc_chunk_1", [0.1, 0.2, 0.3])
results = await ctx.memory.similarity_search([0.1, 0.2, 0.4], top_k=5)

# Explicit scope access
session_memory = ctx.memory.session("session-123")
await session_memory.set("preference", "dark_mode")

# Global scope access
global_memory = ctx.memory.global_scope
await global_memory.set("feature_flag", True)
```

**Sources:** [sdk/python/agentfield/memory.py:571-724]()

### TypeScript SDK API Surface

```typescript
// Automatic scoping
await ctx.memory.set("user_name", "Alice");
const name = await ctx.memory.get<string>("user_name");

// Vector operations
await ctx.memory.setVector("doc_chunk_1", [0.1, 0.2, 0.3], { source: "manual.pdf" });
const results = await ctx.memory.searchVector([0.1, 0.2, 0.4], { topK: 5 });

// Explicit scope access
const sessionMemory = ctx.memory.session("session-123");
await sessionMemory.set("preference", "dark_mode");
```

**Sources:** [sdk/typescript/src/memory/MemoryInterface.ts:17-226](), [sdk/typescript/src/memory/MemoryClient.ts:117-206]()

## Context Propagation via HTTP Headers

The Memory System automatically propagates execution context through HTTP headers, ensuring that memory operations are scoped correctly without requiring explicit scope parameters in every call.

### Header-Based Scope Resolution

```mermaid
flowchart LR
    subgraph "Reasoner Execution"
        Context["ExecutionContext<br/>workflow_id='wf-123'<br/>session_id='sess-456'<br/>actor_id='user-789'"]
    end
    
    subgraph "Memory Client"
        BuildHeaders["_build_headers()"]
        Headers["X-Workflow-ID: wf-123<br/>X-Session-ID: sess-456<br/>X-Actor-ID: user-789<br/>X-Agent-Node-ID: agent-1"]
    end
    
    subgraph "HTTP Request"
        Request["POST /api/v1/memory/set<br/>{key: 'preference', data: 'value'}"]
    end
    
    subgraph "Control Plane"
        ParseHeaders["Parse scope headers"]
        DetermineScope["Determine scope:<br/>workflow (from X-Workflow-ID)"]
        Storage["Store in SQLite/Postgres"]
    end
    
    Context --> BuildHeaders
    BuildHeaders --> Headers
    Headers --> Request
    Request --> ParseHeaders
    ParseHeaders --> DetermineScope
    DetermineScope --> Storage
```

The following headers are recognized for scope resolution:

- `X-Workflow-ID`: Identifies the workflow scope
- `X-Session-ID`: Identifies the session scope  
- `X-Actor-ID`: Identifies the actor scope
- `X-Agent-Node-ID`: Identifies the agent performing the operation
- `X-Run-ID`: Alternative identifier for workflow scope
- `X-Execution-ID`: Tracks individual reasoner/skill executions

**Sources:** [sdk/python/agentfield/memory.py:150-171](), [sdk/typescript/src/memory/MemoryClient.ts:52-75](), [control-plane/internal/handlers/memory.go:187-192]()

## Storage Backend Mapping

The Memory System uses different storage backends depending on the deployment mode and data type.

### Key-Value Storage

| Deployment Mode | Backend | Tables/Schema |
|----------------|---------|---------------|
| Local (SQLite) | SQLite database | `memory_kvstore` table with columns: `scope`, `scope_id`, `key`, `data`, `created_at`, `updated_at` |
| Production (PostgreSQL) | PostgreSQL database | Same schema as SQLite with full-text search support |

### Vector Storage

| Deployment Mode | Backend | Implementation |
|----------------|---------|----------------|
| Local | SQLite/BoltDB | SQLite for metadata, BoltDB for binary embedding storage |
| Production | PostgreSQL with pgvector | `memory_vectors` table with `vector` column type and similarity search functions |

**Sources:** [control-plane/internal/storage/local.go:70-195](), [control-plane/internal/storage/vector_store_postgres.go:41-65](), [control-plane/internal/storage/storage.go:44-130]()

## Integration with Agent Contexts

The Memory System is accessible through both `ReasonerContext` and `SkillContext` objects, which are automatically provided when defining reasoners and skills.

### Python Integration

```python
@app.reasoner()
async def process_document(url: str, ctx):
    # Memory is available via ctx.memory
    await ctx.memory.set("last_processed_url", url)
    return {"status": "processed"}
```

**Sources:** [sdk/python/agentfield/memory.py:571-724]()

### TypeScript Integration

```typescript
agent.reasoner('process_document', async (ctx) => {
  // Memory is available via ctx.memory
  await ctx.memory.set('last_processed_url', ctx.input.url);
  return { status: 'processed' };
});
```

**Sources:** [sdk/typescript/src/context/SkillContext.ts:9-74](), [sdk/typescript/src/memory/MemoryInterface.ts:17-226]()

## Vector Operations for RAG Applications

The Memory System provides first-class support for vector embeddings, enabling RAG (Retrieval-Augmented Generation) patterns.

### Complete RAG Workflow

```mermaid
sequenceDiagram
    participant Agent as "Agent Reasoner"
    participant Memory as "MemoryInterface"
    participant AI as "AIClient"
    participant Storage as "Vector Storage"
    
    Note over Agent,Storage: Document Ingestion Phase
    Agent->>AI: embed(document_text)
    AI-->>Agent: embedding_vector
    Agent->>Memory: set_vector('doc_1', embedding, metadata)
    Memory->>Storage: Store vector with metadata
    
    Note over Agent,Storage: Query Phase
    Agent->>AI: embed(user_query)
    AI-->>Agent: query_embedding
    Agent->>Memory: similarity_search(query_embedding, top_k=5)
    Memory->>Storage: Perform similarity search (L2/Dot/Cosine)
    Storage-->>Memory: Top 5 results with scores
    Memory-->>Agent: [doc_1: 0.95, doc_3: 0.87, ...]
```

**Sources:** [control-plane/internal/storage/vector_store_postgres.go:153-228](), [sdk/python/agentfield/memory.py:326-354](), [sdk/typescript/src/memory/MemoryClient.ts:193-205]()

## Memory Events and Pattern Matching

The Memory System provides real-time change notifications via WebSocket connections. Agents can subscribe to memory changes using pattern matching decorators.

### Pattern Matching Syntax

| Pattern Type | Syntax | Example | Matches |
|-------------|--------|---------|---------|
| Exact | `"key.name"` | `"user.preferences.theme"` | Only `user.preferences.theme` |
| Single wildcard | `"prefix.*"` | `"user.preferences.*"` | `user.preferences.theme`, `user.preferences.color` |
| Multi wildcard | `"a.*.c"` | `"decorator.*.exact"` | `decorator.preferences.exact` |

**Sources:** [sdk/python/agentfield/memory_events.py:18-42](), [tests/functional/tests/test_memory_events.py:139-200]()

### Python Event Subscriptions

```python
@app.memory.on_change("user.preferences.*")
async def on_preference_change(event):
    print(f"Preference changed: {event.key} = {event.data}")
```

**Sources:** [sdk/python/agentfield/memory_events.py:83-200](), [tests/functional/tests/test_memory_events.py:154-161]()

### Event Object Structure

Memory events contain the following fields:

- `type`: Always `"memory_change"`
- `key`: Memory key that changed
- `scope`: Scope where change occurred (`workflow`, `session`, `actor`, `global`)
- `action`: Type of change (`set`, `delete`)
- `data`: New value (for `set` operations)
- `previous_data`: Previous value (for `delete` operations)
- `metadata`: Additional context (agent_id, actor_id, workflow_id)

**Sources:** [control-plane/internal/handlers/memory.go:179-192](), [sdk/python/agentfield/memory_events.py:182-200]()

---

# Page: Memory Scopes

# Memory Scopes

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [sdk/python/agentfield/memory.py](sdk/python/agentfield/memory.py)
- [sdk/python/agentfield/memory_events.py](sdk/python/agentfield/memory_events.py)
- [sdk/python/tests/test_memory_scope_kwargs.py](sdk/python/tests/test_memory_scope_kwargs.py)
- [sdk/typescript/src/context/SkillContext.ts](sdk/typescript/src/context/SkillContext.ts)
- [sdk/typescript/src/memory/MemoryClient.ts](sdk/typescript/src/memory/MemoryClient.ts)
- [sdk/typescript/src/memory/MemoryEventClient.ts](sdk/typescript/src/memory/MemoryEventClient.ts)
- [sdk/typescript/src/memory/MemoryInterface.ts](sdk/typescript/src/memory/MemoryInterface.ts)
- [sdk/typescript/tests/memory_and_discovery.test.ts](sdk/typescript/tests/memory_and_discovery.test.ts)
- [sdk/typescript/tests/memory_event_client.test.ts](sdk/typescript/tests/memory_event_client.test.ts)
- [tests/functional/agents/memory_events_decorator_agent.py](tests/functional/agents/memory_events_decorator_agent.py)
- [tests/functional/tests/test_memory_events.py](tests/functional/tests/test_memory_events.py)

</details>



This page documents AgentField's hierarchical memory scoping system, which enables automatic context isolation and data sharing across different levels of execution. Memory scopes determine the lifetime and visibility of stored data, allowing workflow-specific, session-specific, actor-specific, or globally shared memory.

For information about memory operations (set/get/delete), see [Key-Value Operations](#7.2). For vector storage and similarity search, see [Vector Storage](#7.3). For real-time change notifications, see [Memory Events](#7.4).

## Purpose and Scope Hierarchy

AgentField provides four memory scopes organized in a hierarchy:

| Scope | Lifetime | Visibility | Use Case |
|-------|----------|------------|----------|
| `workflow` | Single workflow execution | All agents in the workflow | Temporary execution state, intermediate results |
| `session` | User session across workflows | All workflows for that session | User preferences, conversation history |
| `actor` | Actor/entity lifetime | All sessions for that actor | Actor-specific context, learned behaviors |
| `global` | Permanent | All agents, all contexts | Shared configuration, system-wide data |

Memory operations automatically resolve to the appropriate scope based on execution context. When retrieving data, the system performs **hierarchical fallback**, searching workflow → session → actor → global until a value is found.

**Sources:** [sdk/python/agentfield/memory.py:4-64](), [sdk/typescript/src/memory/MemoryInterface.ts:36-38]()

---

## Scope Resolution and Context Propagation

### Automatic Scope Detection

Memory scopes are determined by HTTP headers propagated through the execution context:

```mermaid
graph TD
    Request["HTTP Request"] --> Headers["Execution Headers"]
    Headers --> WorkflowHeader["X-Workflow-ID"]
    Headers --> SessionHeader["X-Session-ID"]
    Headers --> ActorHeader["X-Actor-ID"]
    Headers --> NodeHeader["X-Agent-Node-ID"]
    
    WorkflowHeader --> WorkflowScope["workflow scope"]
    SessionHeader --> SessionScope["session scope"]
    ActorHeader --> ActorScope["actor scope"]
    
    WorkflowScope --> MemoryClient["MemoryClient._build_headers()"]
    SessionScope --> MemoryClient
    ActorScope --> MemoryClient
    
    MemoryClient --> APIRequest["POST /api/v1/memory/set"]
    
    NoHeaders["No headers = global scope"] --> GlobalScope["global scope"]
    GlobalScope --> APIRequest
```

**Sources:** [sdk/python/agentfield/memory.py:150-170](), [sdk/typescript/src/memory/MemoryClient.ts:52-75]()

### Header-to-Scope Mapping

The `MemoryClient` class (Python) and `MemoryClientBase` (TypeScript) map internal scope identifiers to HTTP headers:

```mermaid
graph LR
    XWorkflowID["X-Workflow-ID"] --> workflow["scope='workflow'<br/>scopeId=workflow_id"]
    XSessionID["X-Session-ID"] --> session["scope='session'<br/>scopeId=session_id"]
    XActorID["X-Actor-ID"] --> actor["scope='actor'<br/>scopeId=actor_id"]
    
    workflow --> StorageBackend["Storage Backend"]
    session --> StorageBackend
    actor --> StorageBackend
    
    ExplicitGlobal["scope='global'"] --> GlobalStorage["scopeId='global'<br/>Global Storage"]
    GlobalStorage --> StorageBackend
```

In TypeScript, `scopeToHeader()` [sdk/typescript/src/memory/MemoryClient.ts:77-88]() performs this mapping, while `resolveScopeId()` [sdk/typescript/src/memory/MemoryClient.ts:90-104]() determines the scope identifier from metadata. In Python, this is handled in `_build_headers` [sdk/python/agentfield/memory.py:150-170]().

**Sources:** [sdk/python/agentfield/memory.py:150-170](), [sdk/typescript/src/memory/MemoryClient.ts:77-104]()

---

## Hierarchical Fallback Mechanism

When reading data without explicit scope specification, the memory system searches multiple scopes in order.

### Fallback Order

```mermaid
sequenceDiagram
    participant Client as "memory.get('key')"
    participant Workflow as "workflow scope"
    participant Session as "session scope"
    participant Actor as "actor scope"
    participant Global as "global scope"
    
    Client->>Workflow: Search workflow scope first
    alt Found in workflow
        Workflow-->>Client: Return value
    else Not found
        Client->>Session: Search session scope
        alt Found in session
            Session-->>Client: Return value
        else Not found
            Client->>Actor: Search actor scope
            alt Found in actor
                Actor-->>Client: Return value
            else Not found
                Client->>Global: Search global scope
                alt Found in global
                    Global-->>Client: Return value
                else Not found
                    Global-->>Client: Return undefined/default
                end
            end
        end
    end
```

### Implementation Details

The TypeScript SDK explicitly implements the fallback logic in `getWithFallback<T>` [sdk/typescript/src/memory/MemoryInterface.ts:62-72](). It uses `getScopeOrder()` [sdk/typescript/src/memory/MemoryInterface.ts:191-210]() to construct the search sequence: `workflow` → `session` → `actor` → `global`.

In Python, the `MemoryClient.get` method [sdk/python/agentfield/memory.py:232-264]() performs the HTTP request. If no scope is provided, the AgentField server backend performs the hierarchical lookup and returns the most specific match.

**Sources:** [sdk/python/agentfield/memory.py:47-56](), [sdk/typescript/src/memory/MemoryInterface.ts:62-72, 191-210]()

---

## Memory Client Class Hierarchy

### Python SDK Structure

```mermaid
classDiagram
    class MemoryClient {
        +agentfield_client: AgentFieldClient
        +execution_context: ExecutionContext
        +agent_node_id: str
        +_build_headers(scope, scope_id) Dict
        +set(key, data, scope, scope_id)
        +get(key, default, scope, scope_id)
        +set_vector(key, embedding, metadata, scope, scope_id)
        +similarity_search(query_embedding, top_k, scope, scope_id)
        +delete(key, scope, scope_id)
        +list_keys(scope, scope_id)
    }
    
    class ScopedMemoryClient {
        +memory_client: MemoryClient
        +scope: str
        +scope_id: str
        +events: ScopedMemoryEventClient
        +set(key, data)
        +get(key, default)
        +exists(key)
        +delete(key)
        +list_keys()
        +set_vector(key, embedding, metadata)
        +similarity_search(query_embedding, top_k)
        +on_change(patterns)
    }
    
    class GlobalMemoryClient {
        +memory_client: MemoryClient
        +event_client: MemoryEventClient
        +set(key, data)
        +get(key, default)
        +exists(key)
        +delete(key)
        +list_keys()
        +set_vector(key, embedding, metadata)
        +similarity_search(query_embedding, top_k)
        +on_change(patterns)
    }
    
    class MemoryInterface {
        +memory_client: MemoryClient
        +events: MemoryEventClient
        +set(key, data)
        +get(key, default)
        +set_vector(key, embedding, metadata)
        +similarity_search(query_embedding, top_k)
        +session(session_id) ScopedMemoryClient
        +actor(actor_id) ScopedMemoryClient
        +workflow(workflow_id) ScopedMemoryClient
        +global_scope: GlobalMemoryClient
        +on_change(patterns)
    }
    
    MemoryInterface --> MemoryClient : uses
    MemoryInterface --> ScopedMemoryClient : creates
    MemoryInterface --> GlobalMemoryClient : creates
    ScopedMemoryClient --> MemoryClient : delegates to
    GlobalMemoryClient --> MemoryClient : delegates to
```

**Sources:** [sdk/python/agentfield/memory.py:132-150, 465-475, 570-580, 675-724]()

### TypeScript SDK Structure

```mermaid
classDiagram
    class MemoryClientBase {
        #http: AxiosInstance
        -defaultHeaders: Record~string,string~
        #buildHeaders(options)
        #resolveScopeId(scope, scopeId, metadata)
    }

    class MemoryClient {
        +set(key, data, options)
        +get~T~(key, options)
        +delete(key, options)
        +listKeys(scope, options)
        +exists(key, options)
        +setVector(key, embedding, metadata, options)
        +searchVector(queryEmbedding, options)
    }
    
    class MemoryInterface {
        -client: MemoryClient
        -eventClient: MemoryEventClient
        -aiClient: AIClient
        -defaultScope: MemoryScope
        -defaultScopeId: string
        -metadata: MemoryRequestMetadata
        +set(key, data, scope, scopeId)
        +get~T~(key, scope, scopeId)
        +getWithFallback~T~(key)
        +setVector(key, embedding, metadata, scope, scopeId)
        +searchVector(queryEmbedding, options)
        +workflow(scopeId) MemoryInterface
        +session(scopeId) MemoryInterface
        +actor(scopeId) MemoryInterface
        +globalScope: MemoryInterface
        -getScopeOrder() Array
        -cloneWithScope(scope, scopeId) MemoryInterface
    }
    
    MemoryClient --|> MemoryClientBase : extends
    MemoryInterface --> MemoryClient : uses
    MemoryInterface --> MemoryInterface : clones for scoped access
```

**Sources:** [sdk/typescript/src/memory/MemoryClient.ts:38-206](), [sdk/typescript/src/memory/MemoryInterface.ts:17-227]()

---

## Using Scoped Memory

### Explicit Scope Access

Both SDKs provide methods to obtain scoped memory interfaces. These "clone" the interface with a new default scope.

**Python:**
```python
# Accessing scoped clients
session_memory = app.memory.session("session-123")
actor_memory = app.memory.actor("user-456")
workflow_memory = app.memory.workflow("workflow-789")
global_memory = app.memory.global_scope

# Scoped operations (defaults to the specified scope)
await session_memory.set("user_preference", "dark_mode")
value = await session_memory.get("user_preference")
```

**TypeScript:**
```typescript
// Accessing scoped interfaces
const sessionMemory = memory.session("session-123");
const actorMemory = memory.actor("user-456");
const workflowMemory = memory.workflow("workflow-789");
const globalMemory = memory.globalScope;

// Scoped operations
await sessionMemory.set("user_preference", "dark_mode");
const value = await sessionMemory.get("user_preference");
```

**Sources:** [sdk/python/agentfield/memory.py:675-723](), [sdk/typescript/src/memory/MemoryInterface.ts:160-189]()

### Automatic Scoping from Context

When using the base `MemoryInterface` within a reasoner or skill, operations use the current execution context by default. In TypeScript, the `MemoryInterface` is initialized with metadata from the `ExecutionContext` [sdk/typescript/src/context/SkillContext.ts:87]().

```mermaid
graph TD
    ReasonerExecution["Reasoner Execution"] --> ExecutionContext["ExecutionContext<br/>workflow_id='wf-123'<br/>session_id='sess-456'"]
    
    ExecutionContext --> MemorySet["await memory.set('key', 'value')"]
    
    MemorySet --> DetermineScope["Determine scope from context"]
    
    DetermineScope --> UseWorkflow["Default: workflow scope<br/>Uses X-Workflow-ID header"]
    UseWorkflow --> StoredIn["Stored in workflow 'wf-123'"]
    
    MemoryGet["await memory.get('key')"] --> Fallback["Hierarchical fallback"]
    Fallback --> CheckWorkflow["1. Check workflow 'wf-123'"]
    CheckWorkflow --> Found1{Found?}
    Found1 -->|Yes| Return["Return value"]
    Found1 -->|No| CheckSession["2. Check session 'sess-456'"]
    CheckSession --> Found2{Found?}
    Found2 -->|Yes| Return
    Found2 -->|No| CheckGlobal["4. Check global"]
    CheckGlobal --> Found4{Found?}
    Found4 -->|Yes| Return
```

**Sources:** [sdk/python/agentfield/memory.py:583-642](), [sdk/typescript/src/memory/MemoryInterface.ts:41-72](), [sdk/typescript/src/context/SkillContext.ts:70-91]()

---

## Scope-Specific Operations

### Global Scope
Shared across all agents and sessions. Ideal for configuration or shared knowledge bases.
- **Python:** `agent.memory.global_scope` [sdk/python/agentfield/memory.py:721]()
- **TypeScript:** `memory.globalScope` [sdk/typescript/src/memory/MemoryInterface.ts:172]()

### Session Scope
Scoped to a single conversation. Cleared when the session ends.
- **Python:** `agent.memory.session(session_id)` [sdk/python/agentfield/memory.py:675]()
- **TypeScript:** `memory.session(scopeId)` [sdk/typescript/src/memory/MemoryInterface.ts:164]()

### Actor Scope
Scoped to a specific actor (user/agent) across sessions. Persists indefinitely.
- **Python:** `agent.memory.actor(actor_id)` [sdk/python/agentfield/memory.py:689]()
- **TypeScript:** `memory.actor(scopeId)` [sdk/typescript/src/memory/MemoryInterface.ts:168]()

### Workflow Scope
Scoped to a single execution run. Automatically removed when the run completes.
- **Python:** `agent.memory.workflow(workflow_id)` [sdk/python/agentfield/memory.py:701]()
- **TypeScript:** `memory.workflow(scopeId)` [sdk/typescript/src/memory/MemoryInterface.ts:160]()

---

## API Reference

### Key-Value Operations

| Method | Python | TypeScript |
|--------|--------|------------|
| Set | `await memory.set(key, data, scope=None, scope_id=None)` | `await memory.set(key, data, scope?, scopeId?)` |
| Get | `await memory.get(key, default=None, scope=None, scope_id=None)` | `await memory.get<T>(key, scope?, scopeId?)` |
| Delete | `await memory.delete(key, scope=None, scope_id=None)` | `await memory.delete(key, scope?, scopeId?)` |
| List Keys | `await memory.list_keys(scope=None, scope_id=None)` | `await memory.listKeys(scope?, scopeId?)` |

**Sources:** [sdk/python/agentfield/memory.py:187-355](), [sdk/typescript/src/memory/MemoryClient.ts:123-169]()

### Vector Operations

| Method | Python | TypeScript |
|--------|--------|------------|
| Set Vector | `await memory.set_vector(key, embedding, metadata=None, ...)` | `await memory.setVector(key, embedding, metadata?, ...)` |
| Search | `await memory.similarity_search(query_embedding, top_k=10, ...)` | `await memory.searchVector(queryEmbedding, options)` |

**Sources:** [sdk/python/agentfield/memory.py:357-450](), [sdk/typescript/src/memory/MemoryClient.ts:171-205]()

---

## Memory Events and Scopes

Memory events can be filtered by scope during subscription. This allows agents to listen for changes only within a specific session or globally.

```python
# Subscribing to events in a specific session (Python)
session_memory = agent.memory.session("my-session")

@session_memory.on_change("user.preferences.*")
async def handle_preference_change(event):
    print(f"Preference {event.key} changed to {event.data}")
```

**Sources:** [sdk/python/agentfield/memory_events.py:44-82](), [tests/functional/agents/memory_events_decorator_agent.py:160-166]()

---

# Page: Key-Value Operations

# Key-Value Operations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/python_agent_nodes/agentic_rag/README.md](examples/python_agent_nodes/agentic_rag/README.md)
- [examples/python_agent_nodes/agentic_rag/embedding_manager.py](examples/python_agent_nodes/agentic_rag/embedding_manager.py)
- [examples/python_agent_nodes/agentic_rag/sample_document.txt](examples/python_agent_nodes/agentic_rag/sample_document.txt)
- [examples/python_agent_nodes/agentic_rag/schemas.py](examples/python_agent_nodes/agentic_rag/schemas.py)
- [sdk/python/agentfield/logger.py](sdk/python/agentfield/logger.py)
- [sdk/python/agentfield/memory.py](sdk/python/agentfield/memory.py)
- [sdk/python/agentfield/memory_events.py](sdk/python/agentfield/memory_events.py)
- [sdk/python/tests/conftest.py](sdk/python/tests/conftest.py)
- [sdk/python/tests/test_cancel.py](sdk/python/tests/test_cancel.py)
- [sdk/python/tests/test_logger.py](sdk/python/tests/test_logger.py)
- [sdk/python/tests/test_memory_client_core.py](sdk/python/tests/test_memory_client_core.py)
- [sdk/python/tests/test_memory_flow_core.py](sdk/python/tests/test_memory_flow_core.py)
- [sdk/python/tests/test_memory_scope_kwargs.py](sdk/python/tests/test_memory_scope_kwargs.py)
- [sdk/typescript/src/context/SkillContext.ts](sdk/typescript/src/context/SkillContext.ts)
- [sdk/typescript/src/memory/MemoryClient.ts](sdk/typescript/src/memory/MemoryClient.ts)
- [sdk/typescript/src/memory/MemoryEventClient.ts](sdk/typescript/src/memory/MemoryEventClient.ts)
- [sdk/typescript/src/memory/MemoryInterface.ts](sdk/typescript/src/memory/MemoryInterface.ts)
- [sdk/typescript/tests/memory_and_discovery.test.ts](sdk/typescript/tests/memory_and_discovery.test.ts)
- [sdk/typescript/tests/memory_event_client.test.ts](sdk/typescript/tests/memory_event_client.test.ts)
- [tests/functional/agents/memory_events_decorator_agent.py](tests/functional/agents/memory_events_decorator_agent.py)
- [tests/functional/tests/test_memory_events.py](tests/functional/tests/test_memory_events.py)

</details>



This page documents the core CRUD operations for storing and retrieving scalar data in AgentField's memory system. Key-value operations provide a simple interface for persisting state across agent executions with automatic scoping based on execution context.

For information about vector embeddings and similarity search, see [Vector Storage](7.3). For real-time change notifications, see [Memory Events](7.4). For details on how execution context determines scope, see [Context Propagation](7.5).

## Overview

AgentField's memory system provides persistent key-value storage with four-tier hierarchical scoping: **Workflow** (Run), **Session**, **Actor**, and **Global** [sdk/python/agentfield/memory.py:7-45](). All memory operations are performed through the `MemoryInterface` class, which delegates to a `MemoryClient` that communicates with the control plane's HTTP API [sdk/python/agentfield/memory.py:132-149]().

**Key characteristics:**
- **Automatic scoping**: Memory operations use execution context headers to determine scope [sdk/python/agentfield/memory.py:150-171]().
- **Hierarchical fallback**: `get()` searches through scopes in order (workflow -> session -> actor -> global) until a value is found [sdk/python/agentfield/memory.py:47-56]().
- **JSON serialization**: All data is JSON-serialized for storage [sdk/python/agentfield/memory.py:193-205]().
- **Scope isolation**: Explicit scope access bypasses hierarchical lookup [sdk/python/agentfield/memory.py:84-91]().

## Architecture

The following diagram bridges the Natural Language concepts to the Code Entities responsible for memory operations.

**Code Entity Mapping**
```mermaid
graph TB
    subgraph "Agent Runtime (Natural Language Space)"
        Dev["Developer Code<br/>@agent.reasoner()"]
        MemInterface["MemoryInterface<br/>(sdk/python/agentfield/memory.py:571)"]
        ScopedMem["ScopedMemoryClient<br/>(sdk/python/agentfield/memory.py:357)"]
        GlobalMem["GlobalMemoryClient<br/>(sdk/python/agentfield/memory.py:466)"]
    end
    
    subgraph "SDK Layer (Code Space)"
        MemClient["MemoryClient<br/>(sdk/python/agentfield/memory.py:132)"]
        ExecCtx["ExecutionContext<br/>(sdk/python/agentfield/execution_context.py)"]
    end
    
    subgraph "Control Plane Endpoints"
        SetAPI["/api/v1/memory/set"]
        GetAPI["/api/v1/memory/get"]
        DeleteAPI["/api/v1/memory/delete"]
        ListAPI["/api/v1/memory/list"]
    end
    
    Dev --> MemInterface
    MemInterface --> MemClient
    MemInterface --> ScopedMem
    MemInterface --> GlobalMem
    ScopedMem --> MemClient
    GlobalMem --> MemClient
    
    MemClient --> ExecCtx
    MemClient --> SetAPI
    MemClient --> GetAPI
    MemClient --> DeleteAPI
    MemClient --> ListAPI
```
**Sources:** [sdk/python/agentfield/memory.py:1-149](), [sdk/typescript/src/memory/MemoryClient.ts:38-117](), [sdk/python/agentfield/memory.py:571-581]()

## Core Operations

### Setting Values

The `set()` operation stores a key-value pair with automatic scoping based on execution context.

#### Python Implementation
The `MemoryClient.set()` method constructs headers from execution context and sends a POST request to `/api/v1/memory/set` [sdk/python/agentfield/memory.py:187-230]().

```python
# Basic usage with automatic scoping
await app.memory.set("user_preference", {"theme": "dark"})

# Explicit scope
await app.memory.workflow("wf-123").set("status", "processing")
```

#### TypeScript Implementation
The `MemoryClient.set()` method mirrors the Python implementation using `axios` [sdk/typescript/src/memory/MemoryClient.ts:123-130]().

```typescript
// Basic usage with automatic scoping
await ctx.memory.set("user_preference", {theme: "dark"});
```

**Sources:** [sdk/python/agentfield/memory.py:187-230](), [sdk/typescript/src/memory/MemoryClient.ts:123-130]()

### Getting Values

The `get()` operation retrieves values with hierarchical fallback when using automatic scoping [sdk/python/agentfield/memory.py:47-56]().

#### Hierarchical Fallback Logic
When `get()` is called without explicit scope parameters, the SDK searches through scopes in order:
1. **Workflow** (Run)
2. **Session**
3. **Actor**
4. **Global**

The first non-null value found is returned [sdk/python/agentfield/memory.py:54-56]().

#### HTTP Request Flow
```mermaid
sequenceDiagram
    participant Agent as "Agent Code"
    participant MemIface as "MemoryInterface"
    participant MemClient as "MemoryClient"
    participant CP as "Control Plane (/api/v1/memory/get)"
    
    Agent->>MemIface: get("user_pref")
    Note over MemIface: Hierarchical fallback mode
    
    MemIface->>MemClient: get("user_pref", scope="workflow")
    MemClient->>CP: POST /memory/get (X-Workflow-ID: wf-123)
    CP-->>MemClient: 404 Not Found
    
    MemIface->>MemClient: get("user_pref", scope="session")
    MemClient->>CP: POST /memory/get (X-Session-ID: sess-456)
    CP-->>MemClient: 200 OK {"data": "{\"theme\":\"dark\"}"}
    MemClient-->>MemIface: {"theme": "dark"}
    MemIface-->>Agent: {"theme": "dark"}
```
**Sources:** [sdk/python/agentfield/memory.py:232-294](), [sdk/typescript/src/memory/MemoryClient.ts:132-147]()

### Deleting and Checking Existence

- **`delete()`**: Removes a key from the specified scope via `/api/v1/memory/delete` [sdk/python/agentfield/memory.py:326-355]().
- **`exists()`**: Checks if a key exists by performing a `get()` and checking for a non-None result [sdk/python/agentfield/memory.py:296-313]().
- **`listKeys()`**: Retrieves all keys within a specific scope via `/api/v1/memory/list` [sdk/python/agentfield/memory.py:440-463]().

**Sources:** [sdk/python/agentfield/memory.py:296-463](), [sdk/typescript/src/memory/MemoryClient.ts:149-170]()

## Scope-Specific Access

Both SDKs provide helper methods to create scoped memory clients that operate exclusively within a single scope.

| Method | Scope Type | Lifetime |
| :--- | :--- | :--- |
| `workflow(id)` | Workflow/Run | Cleared when workflow run completes [sdk/python/agentfield/memory.py:29-31]() |
| `session(id)` | Session | Cleared when conversation/session ends [sdk/python/agentfield/memory.py:17-19]() |
| `actor(id)` | Actor | Scoped to single actor across sessions [sdk/python/agentfield/memory.py:21-25]() |
| `global_scope` | Global | Shared across all agents and sessions [sdk/python/agentfield/memory.py:9-13]() |

**Sources:** [sdk/python/agentfield/memory.py:7-32](), [sdk/python/agentfield/memory.py:675-723]()

## Data Serialization

All data is JSON-serialized before storage. The `MemoryClient` validates serialization before sending the payload [sdk/python/agentfield/memory.py:216-220]().

**Python Example:**
```python
# Complex nested structures
await app.memory.set("complex", {
    "nested": {"array": [1, 2, 3]},
    "boolean": True
})
```

**TypeScript Example:**
```typescript
// Complex nested structures
await ctx.memory.set("complex", {
    nested: { array: [1, 2, 3] },
    boolean: true
});
```
**Sources:** [sdk/python/agentfield/memory.py:216-220](), [sdk/typescript/src/memory/MemoryClient.ts:123-130]()

## Context Header Propagation

Memory operations automatically include execution context headers that determine scope resolution. The `MemoryClient._build_headers()` method is central to this process [sdk/python/agentfield/memory.py:150-171]().

```mermaid
graph LR
    subgraph "ExecutionContext (sdk/python/agentfield/execution_context.py)"
        WID["X-Workflow-ID"]
        SID["X-Session-ID"]
        AID["X-Actor-ID"]
    end
    
    subgraph "MemoryClient (sdk/python/agentfield/memory.py)"
        BH["_build_headers()"]
    end
    
    WID --> BH
    SID --> BH
    AID --> BH
    BH --> FinalHeaders["HTTP Request Headers"]
```
**Sources:** [sdk/python/agentfield/memory.py:150-171](), [sdk/typescript/src/memory/MemoryClient.ts:52-75]()

## Error Handling

### 404 Not Found
When a key doesn't exist, the control plane returns HTTP 404. The Python SDK handles this by returning a `default` value (defaulting to `None`) [sdk/python/agentfield/memory.py:284-289](). The TypeScript SDK returns `undefined` [sdk/typescript/src/memory/MemoryClient.ts:142-144]().

### Serialization Errors
The Python SDK raises a `TypeError` if data is not JSON serializable before attempting the request [sdk/python/agentfield/memory.py:203-205]().

**Sources:** [sdk/python/agentfield/memory.py:203-289](), [sdk/typescript/src/memory/MemoryClient.ts:141-146]()

---

# Page: Vector Storage

# Vector Storage

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [control-plane/internal/handlers/memory.go](control-plane/internal/handlers/memory.go)
- [control-plane/internal/handlers/memory_handler_test.go](control-plane/internal/handlers/memory_handler_test.go)
- [control-plane/internal/handlers/vector_memory.go](control-plane/internal/handlers/vector_memory.go)
- [control-plane/internal/handlers/vector_memory_test.go](control-plane/internal/handlers/vector_memory_test.go)
- [control-plane/internal/server/server_routes_test.go](control-plane/internal/server/server_routes_test.go)
- [control-plane/internal/storage/local.go](control-plane/internal/storage/local.go)
- [control-plane/internal/storage/storage.go](control-plane/internal/storage/storage.go)
- [control-plane/internal/storage/vector_store.go](control-plane/internal/storage/vector_store.go)
- [control-plane/internal/storage/vector_store_postgres.go](control-plane/internal/storage/vector_store_postgres.go)
- [control-plane/internal/storage/vector_store_sqlite.go](control-plane/internal/storage/vector_store_sqlite.go)
- [sdk/python/agentfield/memory.py](sdk/python/agentfield/memory.py)
- [sdk/python/agentfield/memory_events.py](sdk/python/agentfield/memory_events.py)
- [sdk/python/tests/test_memory_scope_kwargs.py](sdk/python/tests/test_memory_scope_kwargs.py)
- [sdk/typescript/src/context/SkillContext.ts](sdk/typescript/src/context/SkillContext.ts)
- [sdk/typescript/src/memory/MemoryClient.ts](sdk/typescript/src/memory/MemoryClient.ts)
- [sdk/typescript/src/memory/MemoryEventClient.ts](sdk/typescript/src/memory/MemoryEventClient.ts)
- [sdk/typescript/src/memory/MemoryInterface.ts](sdk/typescript/src/memory/MemoryInterface.ts)
- [sdk/typescript/tests/memory_and_discovery.test.ts](sdk/typescript/tests/memory_and_discovery.test.ts)
- [sdk/typescript/tests/memory_event_client.test.ts](sdk/typescript/tests/memory_event_client.test.ts)
- [tests/functional/agents/memory_events_decorator_agent.py](tests/functional/agents/memory_events_decorator_agent.py)
- [tests/functional/tests/test_memory_events.py](tests/functional/tests/test_memory_events.py)

</details>



This page covers AgentField's vector storage system for semantic search and retrieval-augmented generation (RAG). Vector storage enables agents to store and search high-dimensional embeddings for similarity-based retrieval. For basic key-value operations, see [Key-Value Operations](#7.2). For organizing vector data across contexts, see [Memory Scopes](#7.1).

---

## Core Concepts

**Vector embeddings** are high-dimensional numerical representations of text, images, or other data that capture semantic meaning. AgentField stores these embeddings alongside metadata, enabling similarity-based search across agent memory.

### Use Cases

| Use Case | Description |
|----------|-------------|
| **Semantic Search** | Find documents or data similar to a query embedding |
| **RAG Systems** | Retrieve relevant context for LLM prompts |
| **Document Clustering** | Group similar content by embedding proximity |
| **Contextual Memory** | Store agent experiences as searchable vectors |

### Storage Architecture

The vector storage system is integrated into the `MemoryClient` and backed by the control plane's storage providers. It supports multiple backends including SQLite (via `vector_store_sqlite.go`) and PostgreSQL (via `vector_store_postgres.go` using the `pgvector` extension).

```mermaid
graph TB
    subgraph "Vector Storage Layer [control-plane]"
        VectorAPI["MemoryStorage Interface<br/>handlers/memory.go"]
        PostgresVS["postgresVectorStore<br/>storage/vector_store_postgres.go"]
        SqliteVS["sqliteVectorStore<br/>storage/vector_store_sqlite.go"]
    end
    
    subgraph "Memory Scopes"
        WorkflowVec["Workflow Vectors<br/>X-Workflow-ID"]
        SessionVec["Session Vectors<br/>X-Session-ID"]
        ActorVec["Actor Vectors<br/>X-Actor-ID"]
        GlobalVec["Global Vectors<br/>scope=global"]
    end
    
    subgraph "Client Operations [SDKs]"
        SetVec["setVector()<br/>MemoryClient.ts / memory.py"]
        SearchVec["searchVector()<br/>MemoryClient.ts / memory.py"]
        DelVec["deleteVector()<br/>MemoryClient.ts / memory.py"]
    end
    
    SetVec --> VectorAPI
    SearchVec --> VectorAPI
    DelVec --> VectorAPI
    
    VectorAPI --> PostgresVS
    VectorAPI --> SqliteVS
    
    PostgresVS --> WorkflowVec
    PostgresVS --> SessionVec
    PostgresVS --> ActorVec
    PostgresVS --> GlobalVec
```

**Sources:** [sdk/typescript/src/memory/MemoryClient.ts:171-205](), [control-plane/internal/handlers/memory.go:23-27](), [control-plane/internal/storage/vector_store_postgres.go:15-25](), [sdk/python/agentfield/memory.py:410-445]()

---

## Vector Operations

### Setting Vectors

Store embeddings with associated keys and metadata. The system automatically normalizes various input types (like numpy arrays or tuples) into float lists before transmission.

#### TypeScript
```typescript
// Set a vector with metadata [sdk/typescript/src/memory/MemoryClient.ts:171-182]
await memory.setVector(
  'doc:chunk-1',
  [0.1, 0.2, 0.3, ...],  // 384-dim embedding
  { 
    source: 'docs/api.md',
    section: 'Authentication'
  },
  { scope: 'global' }
);
```

#### Python
```python
# Set a vector with metadata [sdk/python/agentfield/memory.py:410-435]
await app.memory.set_vector(
    'doc:chunk-1',
    [0.1, 0.2, 0.3, ...],
    metadata={'source': 'docs/api.md'},
    scope='global'
)
```

**Implementation Details:**
The `MemoryClient` sends payloads to `/api/v1/memory/vector/set`. On the control plane, `SetVector` handles persistence. In PostgreSQL, this uses an `ON CONFLICT` clause to perform upserts.

**Sources:** [sdk/typescript/src/memory/MemoryClient.ts:171-182](), [sdk/python/agentfield/memory.py:410-435](), [control-plane/internal/storage/vector_store_postgres.go:41-49]()

---

### Searching Vectors

Perform similarity search using query embeddings. The control plane supports different distance metrics including Cosine (default), L2, and Dot Product.

#### TypeScript
```typescript
// Search for similar vectors [sdk/typescript/src/memory/MemoryClient.ts:193-205]
const results = await memory.searchVector(
  queryEmbedding,
  {
    topK: 5,
    filters: { source: 'docs/api.md' },
    scope: 'global'
  }
);
```

#### Python
```python
# Search for similar vectors [sdk/python/agentfield/memory.py:461-487]
results = await app.memory.search_vector(
    query_embedding,
    top_k=5,
    filters={'source': 'docs/api.md'},
    scope='global'
)
```

**Distance Metrics (PostgreSQL):**
AgentField translates metrics into native `pgvector` operators:
- **Cosine**: `1 - (mv.embedding <=> query_vec)`
- **L2**: `-(mv.embedding <-> query_vec)`
- **Dot Product**: `-(mv.embedding <#> query_vec)`

**Sources:** [control-plane/internal/storage/vector_store_postgres.go:238-250](), [sdk/typescript/src/memory/MemoryClient.ts:193-205](), [sdk/python/agentfield/memory.py:461-487]()

---

### Deleting Vectors

Vectors can be deleted individually by key or in bulk by prefix.

#### TypeScript
```typescript
// Delete single vector [sdk/typescript/src/memory/MemoryClient.ts:184-191]
await memory.deleteVector('doc:chunk-1', { scope: 'global' });
```

#### Python
```python
# Delete single vector [sdk/python/agentfield/memory.py:437-459]
await app.memory.delete_vector('doc:chunk-1', scope='global')

# Delete by prefix (useful for cleaning up document chunks)
await app.memory.delete_vectors_by_prefix('doc:', scope='global')
```

**Sources:** [sdk/typescript/src/memory/MemoryClient.ts:184-191](), [sdk/python/agentfield/memory.py:437-459](), [control-plane/internal/storage/vector_store_postgres.go:132-151]()

---

## Embedding Generation

### Via AI Providers
The SDKs integrate with the `AIClient` to generate embeddings from text before storing them.

| Provider | Embedding Support |
|----------|-------------------|
| **OpenAI** | Supported |
| **Google** | Supported |
| **Mistral** | Supported |
| **Cohere** | Supported |
| **Ollama** | Supported |

**Sources:** [sdk/typescript/src/ai/AIClient.ts:258-310]()

---

## Memory Scopes and Vectors

Vector storage respects AgentField's memory scope hierarchy. Scopes are enforced via HTTP headers and resolved on the control plane.

```mermaid
graph TD
    subgraph "Natural Language Concept"
        UserReq["Search my private notes"]
    end

    subgraph "Code Entity Space"
        Client["MemoryClient.searchVector()<br/>sdk/typescript/src/memory/MemoryClient.ts"]
        Header["X-Actor-ID Header<br/>buildHeaders()"]
        Handler["SimilaritySearch()<br/>handlers/memory.go"]
        Storage["postgresVectorStore.Search()<br/>storage/vector_store_postgres.go"]
        SQL["SELECT FROM memory_vectors<br/>WHERE scope = 'actor' AND scope_id = ?"]
    end

    UserReq --> Client
    Client --> Header
    Header --> Handler
    Handler --> Storage
    Storage --> SQL
```

**Scope Resolution:**
The control plane uses `resolveScope` to determine the active context. If a scope is not explicitly provided in the request body, it is inferred from the `X-Workflow-ID`, `X-Session-ID`, or `X-Actor-ID` headers.

**Sources:** [control-plane/internal/handlers/memory.go:79-84](), [sdk/typescript/src/memory/MemoryClient.ts:52-75](), [sdk/python/agentfield/memory.py:150-170]()

---

## API Reference

### MemoryClient Methods (TypeScript)

| Method | Signature | Description |
|--------|-----------|-------------|
| `setVector` | `(key, embedding, metadata?, options?)` | Store vector with metadata |
| `deleteVector` | `(key, options?)` | Delete vector by key |
| `searchVector` | `(queryEmbedding, options?)` | Similarity search |

**Sources:** [sdk/typescript/src/memory/MemoryClient.ts:117-206]()

### Memory Interface Methods (Python)

| Method | Signature | Description |
|--------|-----------|-------------|
| `set_vector` | `(key, embedding, metadata=None, scope=None)` | Store vector |
| `get_vector` | `(key, scope=None)` | Retrieve vector and metadata |
| `delete_vector` | `(key, scope=None)` | Remove vector |
| `search_vector` | `(query_embedding, top_k=10, filters=None, scope=None)` | Search vectors |

**Sources:** [sdk/python/agentfield/memory.py:410-510]()

### Storage Types (Go)

```go
type VectorRecord struct {
    Scope     string          `json:"scope"`
    ScopeID   string          `json:"scope_id"`
    Key       string          `json:"key"`
    Embedding []float32       `json:"embedding"`
    Metadata  map[string]any  `json:"metadata"`
    CreatedAt time.Time       `json:"created_at"`
    UpdatedAt time.Time       `json:"updated_at"`
}
```

**Sources:** [control-plane/pkg/types/memory.go]() (referenced via [control-plane/internal/handlers/memory.go:23]())

---

# Page: Memory Events

# Memory Events

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [control-plane/internal/handlers/memory_events.go](control-plane/internal/handlers/memory_events.go)
- [control-plane/internal/handlers/memory_events_test.go](control-plane/internal/handlers/memory_events_test.go)
- [control-plane/internal/handlers/reasoners_test.go](control-plane/internal/handlers/reasoners_test.go)
- [control-plane/internal/handlers/ui/dashboard_helpers_test.go](control-plane/internal/handlers/ui/dashboard_helpers_test.go)
- [control-plane/internal/handlers/ui/execution_helpers_test.go](control-plane/internal/handlers/ui/execution_helpers_test.go)
- [control-plane/internal/handlers/ui/execution_logs_handler_test.go](control-plane/internal/handlers/ui/execution_logs_handler_test.go)
- [control-plane/internal/handlers/ui/router_helpers_test.go](control-plane/internal/handlers/ui/router_helpers_test.go)
- [sdk/python/agentfield/memory.py](sdk/python/agentfield/memory.py)
- [sdk/python/agentfield/memory_events.py](sdk/python/agentfield/memory_events.py)
- [sdk/python/tests/test_memory_scope_kwargs.py](sdk/python/tests/test_memory_scope_kwargs.py)
- [sdk/typescript/src/context/SkillContext.ts](sdk/typescript/src/context/SkillContext.ts)
- [sdk/typescript/src/memory/MemoryClient.ts](sdk/typescript/src/memory/MemoryClient.ts)
- [sdk/typescript/src/memory/MemoryEventClient.ts](sdk/typescript/src/memory/MemoryEventClient.ts)
- [sdk/typescript/src/memory/MemoryInterface.ts](sdk/typescript/src/memory/MemoryInterface.ts)
- [sdk/typescript/tests/memory_and_discovery.test.ts](sdk/typescript/tests/memory_and_discovery.test.ts)
- [sdk/typescript/tests/memory_event_client.test.ts](sdk/typescript/tests/memory_event_client.test.ts)
- [tests/functional/agents/memory_events_decorator_agent.py](tests/functional/agents/memory_events_decorator_agent.py)
- [tests/functional/tests/test_memory_events.py](tests/functional/tests/test_memory_events.py)

</details>



Memory events provide real-time change notifications when memory values are updated or deleted across the AgentField system. This enables reactive workflows, state synchronization across agents, and event-driven architectures without polling.

For basic memory operations, see [Key-Value Operations](#7.2). For understanding memory scoping, see [Memory Scopes](#7.1).

---

## Overview

The memory event system uses WebSocket or Server-Sent Events (SSE) connections to push change notifications to subscribed agents in real-time. Agents can subscribe to specific memory keys using pattern matching, filter by scope, and react to both `set` and `delete` operations.

**Key capabilities:**
- **Pattern matching** - Subscribe using exact keys, wildcards, or nested patterns. [sdk/python/agentfield/memory_events.py:18-42]()
- **Scope filtering** - Listen to specific workflow, session, actor, or global scopes. [control-plane/internal/handlers/memory_events.go:66-68]()
- **Event History** - Retrieve past events using the history API. [control-plane/internal/handlers/memory_events.go:182-216]()
- **Decorator syntax** - Python SDK provides `@memory.on_change()` decorators. [sdk/python/agentfield/memory.py:445-462]()
- **Automatic reconnection** - WebSocket clients handle disconnects gracefully with exponential backoff. [sdk/typescript/src/memory/MemoryEventClient.ts:89-100]()

**Sources:** [sdk/python/agentfield/memory_events.py:1-110](), [sdk/typescript/src/memory/MemoryEventClient.ts:1-164]()

---

## Architecture

### Event Flow

```mermaid
graph TB
    Agent1["Agent 1<br/>memory.set(key, value)"]
    Agent2["Agent 2<br/>@memory.on_change(pattern)"]
    Agent3["Agent 3<br/>MemoryEventClient.onEvent(handler)"]
    
    ControlPlane["Control Plane Handler<br/>MemoryEventsHandler"]
    Storage["StorageProvider<br/>SubscribeToMemoryChanges"]
    
    Agent1 -->|"HTTP POST /api/v1/memory/set"| ControlPlane
    ControlPlane -->|"write & notify"| Storage
    
    Storage -.->|"Channel push"| ControlPlane
    ControlPlane -.->|"WebSocket/SSE push"| Agent2
    ControlPlane -.->|"WebSocket push"| Agent3
    
    Agent2 -->|"PatternMatcher"| Handler2["Memory Event Handler"]
    Agent3 -->|"callback"| Handler3["Event Callback"]
```

**Event Publication:**
1. Agent performs `memory.set()` via `MemoryClient`. [sdk/python/agentfield/memory.py:187-210]()
2. Control plane persists change via `StorageProvider`. [control-plane/internal/handlers/memory_events.go:20-23]()
3. The storage layer notifies the `MemoryEventsHandler` via a Go channel. [control-plane/internal/handlers/memory_events.go:71-72]()
4. Subscribed agents receive events via `WebSocketHandler` or `SSEHandler`. [control-plane/internal/handlers/memory_events.go:56-179]()
5. Pattern matching filters events to relevant handlers on the client side. [sdk/python/agentfield/memory_events.py:60-76]()

**Sources:** [control-plane/internal/handlers/memory_events.go:19-111](), [sdk/python/agentfield/memory.py:132-171](), [sdk/typescript/src/memory/MemoryEventClient.ts:13-38]()

---

## Event Structure

Each memory event is represented by the `MemoryChangeEvent` type:

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Unique event identifier. |
| `key` | `string` | Memory key that changed. |
| `scope` | `string` | Scope type: `workflow`, `session`, `actor`, or `global`. |
| `scope_id` | `string` | ID of the specific scope instance. |
| `action` | `string` | Operation type: `set` or `delete`. |
| `data` | `any` | New value (for `set` operations). |
| `previous_data` | `any` | Previous value (for `delete` operations). |
| `metadata` | `object` | Agent ID, workflow ID, timestamps, etc. |
| `timestamp` | `string` | ISO 8601 timestamp of the event. |

**Sources:** [sdk/python/agentfield/types.py:14-45](), [control-plane/internal/handlers/memory_events_test.go:113-124]()

---

## Pattern Matching

The system supports wildcard matching using the `PatternMatcher` utility. [sdk/python/agentfield/memory_events.py:18-42]()

### Pattern Types

| Pattern | Example Keys Matched | Description |
|---------|---------------------|-------------|
| `"user.theme"` | `user.theme` | Exact key match only. |
| `"user.*"` | `user.theme`, `user.lang` | Any key with prefix `user.` (matches single segment). |
| `"settings.*.mode"` | `settings.display.mode` | Nested wildcard between segments. |
| `"features.*.*.rollout"`| `features.beta.flag.rollout` | Multiple wildcard segments. |

**Matching Logic:**
- Patterns are converted to regular expressions internally. [sdk/python/agentfield/memory_events.py:33-35]()
- Wildcards (`*`) are treated as `.*` in regex context. [sdk/python/agentfield/memory_events.py:34]()
- The server-side also supports pattern filtering using Go's `filepath.Match`. [control-plane/internal/handlers/memory_events.go:97-101]()

**Sources:** [sdk/python/agentfield/memory_events.py:21-42](), [control-plane/internal/handlers/memory_events.go:39-53]()

---

## Python SDK: Decorator Subscriptions

The Python SDK uses `MemoryInterface` to manage subscriptions via decorators. [sdk/python/agentfield/memory.py:445-462]()

### Usage Examples

```python
# Basic subscription
@agent.memory.on_change("user.preferences.theme")
async def handle_theme_change(event):
    print(f"New theme: {event.data}")

# Wildcard pattern
@agent.memory.on_change("user.preferences.*")
async def handle_any_preference(event):
    print(f"Key {event.key} changed to {event.data}")

# Explicit scope subscription
@agent.memory.global_scope.on_change("config.*")
async def handle_global_config(event):
    print("Global config updated")
```

**Implementation Details:**
- The `@on_change` decorator wraps the callback and adds it to the `MemoryEventClient`. [sdk/python/agentfield/memory.py:445-462]()
- The `MemoryEventClient` manages the underlying WebSocket connection to the Control Plane. [sdk/python/agentfield/memory_events.py:83-105]()

**Sources:** [sdk/python/agentfield/memory.py:445-462](), [sdk/python/agentfield/memory_events.py:44-81]()

---

## TypeScript SDK: Handler Subscriptions

The TypeScript `MemoryEventClient` provides a functional approach to event handling. [sdk/typescript/src/memory/MemoryEventClient.ts:13-38]()

### Client Configuration

```typescript
import { MemoryEventClient } from '@agentfield/sdk';

const events = new MemoryEventClient('http://localhost:8080', {
  'X-Agent-Node-ID': 'my-node'
});

events.onEvent(async (event) => {
  console.log(`Received change for ${event.key}`);
});

events.start();
```

### Event History

The TypeScript SDK can also query historical events:

```typescript
const history = await events.history({
  patterns: ["user.*"],
  limit: 50,
  scope: "session",
  scopeId: "session-123"
});
```

**Sources:** [sdk/typescript/src/memory/MemoryEventClient.ts:31-38](), [sdk/typescript/src/memory/MemoryEventClient.ts:116-164]()

---

## Control Plane Implementation

The Control Plane manages subscriptions through the `MemoryEventsHandler`. [control-plane/internal/handlers/memory_events.go:20-23]()

### WebSocket and SSE Support

The server supports two protocols for real-time delivery:
1. **WebSockets**: Efficient bi-directional communication. [control-plane/internal/handlers/memory_events.go:56-111]()
2. **Server-Sent Events (SSE)**: Unidirectional streaming over HTTP. [control-plane/internal/handlers/memory_events.go:114-179]()

### Connection Lifecycle

```mermaid
sequenceDiagram
    participant Agent
    participant Handler as MemoryEventsHandler
    participant Storage as StorageProvider

    Agent->>Handler: GET /api/v1/memory/events/ws?patterns=user.*
    Handler->>Storage: SubscribeToMemoryChanges(ctx, scope, scopeID)
    Storage-->>Handler: eventChan (chan MemoryChangeEvent)
    Handler-->>Agent: Upgrade to WebSocket
    
    loop Every Change
        Storage->>Handler: New Event
        Handler->>Handler: Pattern Match (filepath.Match)
        Handler->>Agent: WriteJSON(event)
    end
```

**Sources:** [control-plane/internal/handlers/memory_events.go:56-111](), [control-plane/internal/handlers/memory_events_test.go:46-74]()

---

## Event History API

Historical events can be retrieved via `GET /api/v1/memory/events/history`. [control-plane/internal/handlers/memory_events.go:182-216]()

**Filter Parameters:**
- `scope`: Filter by scope type.
- `scope_id`: Filter by specific scope ID.
- `patterns`: Comma-separated list of wildcard patterns.
- `since`: ISO 8601 timestamp to fetch events after.
- `limit`: Maximum number of events to return.

**Sources:** [control-plane/internal/handlers/memory_events.go:187-206](), [sdk/typescript/src/memory/MemoryEventClient.ts:132-152]()

---

## Connection Management and Reconnection

The `MemoryEventClient` (both Python and TS) implements robust connection logic:
- **Sanitization**: Only specific headers (e.g., `Authorization`, `X-*`) are forwarded to the WebSocket handshake. [sdk/typescript/src/memory/MemoryEventClient.ts:102-113]()
- **Exponential Backoff**: If the connection drops, the client waits for an increasing delay (doubling each time, up to 30s) before retrying. [sdk/typescript/src/memory/MemoryEventClient.ts:89-100]()
- **Heartbeats**: The Control Plane monitors connection health via reader loops. [control-plane/internal/handlers/memory_events.go:80-89]()

**Sources:** [sdk/typescript/src/memory/MemoryEventClient.ts:89-100](), [sdk/python/agentfield/memory_events.py:101-105]()

---

# Page: Context Propagation

# Context Propagation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [sdk/python/agentfield/execution_context.py](sdk/python/agentfield/execution_context.py)
- [sdk/python/agentfield/memory.py](sdk/python/agentfield/memory.py)
- [sdk/python/agentfield/memory_events.py](sdk/python/agentfield/memory_events.py)
- [sdk/python/tests/integration/conftest.py](sdk/python/tests/integration/conftest.py)
- [sdk/python/tests/integration/test_agentfield_end_to_end.py](sdk/python/tests/integration/test_agentfield_end_to_end.py)
- [sdk/python/tests/test_execution_context_core.py](sdk/python/tests/test_execution_context_core.py)
- [sdk/python/tests/test_memory_scope_kwargs.py](sdk/python/tests/test_memory_scope_kwargs.py)
- [sdk/typescript/src/context/SkillContext.ts](sdk/typescript/src/context/SkillContext.ts)
- [sdk/typescript/src/memory/MemoryClient.ts](sdk/typescript/src/memory/MemoryClient.ts)
- [sdk/typescript/src/memory/MemoryEventClient.ts](sdk/typescript/src/memory/MemoryEventClient.ts)
- [sdk/typescript/src/memory/MemoryInterface.ts](sdk/typescript/src/memory/MemoryInterface.ts)
- [sdk/typescript/tests/memory_and_discovery.test.ts](sdk/typescript/tests/memory_and_discovery.test.ts)
- [sdk/typescript/tests/memory_event_client.test.ts](sdk/typescript/tests/memory_event_client.test.ts)
- [tests/functional/agents/memory_events_decorator_agent.py](tests/functional/agents/memory_events_decorator_agent.py)
- [tests/functional/tests/test_memory_events.py](tests/functional/tests/test_memory_events.py)

</details>



## Overview

Context propagation is the mechanism by which execution metadata flows transparently through distributed agent operations, enabling automatic memory scoping, workflow tracking, and event routing. When an agent execution is initiated, context headers capture workflow, session, actor, and execution identifiers. These headers are then automatically included in all downstream operations—memory reads/writes, cross-agent calls, and event subscriptions—without requiring explicit parameter passing by developers.

This document describes the HTTP header-based context propagation system and its integration with memory operations. For information about how context enables workflow tracking and DAG generation, see [Workflow Tracking](#9.3). For details on memory scoping behavior enabled by context, see [Memory Scopes](#7.1).

## Context Headers

AgentField uses a standardized set of HTTP headers to propagate execution context across distributed operations. All headers use the `X-` prefix convention for custom headers.

| Header Name | Purpose | Scope |
|------------|---------|-------|
| `X-Workflow-ID` | Identifies the top-level workflow instance | All operations within a workflow |
| `X-Session-ID` | Identifies a user or conversation session | All operations within a session |
| `X-Actor-ID` | Identifies the executing actor (user/bot/system) | All operations by that actor |
| `X-Agent-Node-ID` | Identifies the current agent node | Memory operations scoped to agent |
| `X-Execution-ID` | Unique identifier for a single execution | Single reasoner/skill invocation |
| `X-Run-ID` | Identifies a logical run grouping | Related executions in a batch |
| `X-Parent-Execution-ID` | Links to parent execution in call chain | Child executions in nested calls |
| `X-Caller-DID` | Decentralized Identifier of the caller | Security and identity verification |
| `X-Target-DID` | Decentralized Identifier of the target agent | Routing and identity verification |
| `X-AgentField-Replay-Mode`| Metadata for execution replay | Replay and debugging |

**Sources:** [sdk/python/agentfield/memory.py:150-171](), [sdk/python/agentfield/execution_context.py:130-185](), [sdk/typescript/src/memory/MemoryClient.ts:52-75]()

## Execution Context Capture

The `ExecutionContext` class captures incoming request headers and provides methods to reconstruct them for downstream operations. This context is automatically initialized when an agent receives an execution request from the control plane. In Python, this is managed via thread-local or context-variable storage to ensure availability within reasoner and skill functions.

```mermaid
graph TB
    IncomingReq["Incoming HTTP Request<br/>from Control Plane"]
    ExecContext["ExecutionContext<br/>(execution_context.py)"]
    ContextAttrs["Context Attributes"]
    ToHeaders["to_headers() method"]
    OutgoingHeaders["Outgoing HTTP Headers"]
    
    IncomingReq -->|"Extract headers"| ExecContext
    ExecContext -->|"Parse and store"| ContextAttrs
    
    ContextAttrs --> WorkflowID["workflow_id"]
    ContextAttrs --> SessionID["session_id"]
    ContextAttrs --> ActorID["actor_id"]
    ContextAttrs --> ExecutionID["execution_id"]
    ContextAttrs --> RunID["run_id"]
    ContextAttrs --> ParentExecID["parent_execution_id"]
    
    ContextAttrs -->|"Reconstruct"| ToHeaders
    ToHeaders -->|"Generate"| OutgoingHeaders
    
    OutgoingHeaders --> XWorkflow["X-Workflow-ID"]
    OutgoingHeaders --> XSession["X-Session-ID"]
    OutgoingHeaders --> XActor["X-Actor-ID"]
    OutgoingHeaders --> XExecution["X-Execution-ID"]
    OutgoingHeaders --> XRun["X-Run-ID"]
    OutgoingHeaders --> XParent["X-Parent-Execution-ID"]
```

**Sources:** [sdk/python/agentfield/execution_context.py:130-185](), [sdk/python/tests/test_execution_context_core.py:12-38](), [sdk/typescript/src/context/SkillContext.ts:70-91]()

## Client Context Propagation

The SDK clients maintain a reference to the active execution context and automatically merge context headers into all outgoing requests. The merge logic ensures that explicit overrides are respected while providing sensible defaults from the current execution environment.

### Header Merge Sequence

```mermaid
sequenceDiagram
    participant Caller as "Developer Code"
    participant Client as "MemoryClient / AgentFieldClient"
    participant Context as "ExecutionContext"
    participant Merged as "Final Headers Dict"
    
    Caller->>Client: memory.set(key, data)
    Client->>Context: context.to_headers()
    Context-->>Client: {"X-Workflow-ID": "wf-123", ...}
    
    Client->>Client: buildHeaders(options)
    Note over Client: In TS: buildHeaders() merges<br/>metadata into headers
    
    Client->>Merged: Add context headers
    
    alt Explicit Scope Override
        Caller->>Client: memory.set(key, data, scope="session", scope_id="s1")
        Client->>Merged: Map scope to header (X-Session-ID)
        Client->>Merged: Set header to "s1"
    end
    
    Merged-->>Client: Final merged headers
    Client->>Client: Make HTTP request with headers
```

**Key Implementation Details:**

1. **Python `MemoryClient`**: Merges context headers via `self.execution_context.to_headers()` [sdk/python/agentfield/memory.py:155]().
2. **TypeScript `MemoryClientBase`**: Implements `buildHeaders` to map `MemoryRequestMetadata` to `X-` headers [sdk/typescript/src/memory/MemoryClient.ts:52-75]().
3. **Scope Mapping**: Scopes like `workflow`, `session`, and `actor` are mapped to their respective `X-Workflow-ID`, `X-Session-ID`, and `X-Actor-ID` headers [sdk/typescript/src/memory/MemoryClient.ts:77-88]().

**Sources:** [sdk/python/agentfield/memory.py:150-171](), [sdk/typescript/src/memory/MemoryClient.ts:52-88](), [sdk/typescript/src/memory/MemoryInterface.ts:41-47]()

## Memory Context Integration

The `MemoryClient` integrates execution context into memory operations, enabling automatic scoping without explicit scope parameters. The `_build_headers()` (Python) or `buildHeaders()` (TS) method merges execution context with optional scope overrides.

### Memory Header Construction

```mermaid
graph TB
    MemOp["Memory Operation<br/>set(key, data, scope, scope_id)"]
    BuildHeaders["buildHeaders(options)"]
    ExecCtx["execution_context.to_headers()"]
    BaseHeaders["Base Context Headers"]
    
    MemOp -->|"Call"| BuildHeaders
    BuildHeaders -->|"Get context"| ExecCtx
    ExecCtx -->|"Return"| BaseHeaders
    
    BaseHeaders --> CheckAgent{"agent_node_id<br/>provided?"}
    CheckAgent -->|"Yes"| AddAgent["Add X-Agent-Node-ID"]
    CheckAgent -->|"No"| CheckScope
    
    AddAgent --> CheckScope{"scope_id<br/>parameter?"}
    
    CheckScope -->|"Yes"| MapScope["Map scope to header name"]
    CheckScope -->|"No"| Return["Return headers"]
    
    MapScope --> ScopeMap["scope='workflow' → X-Workflow-ID<br/>scope='session' → X-Session-ID<br/>scope='actor' → X-Actor-ID"]
    
    ScopeMap --> Override["Override header with scope_id"]
    Override --> Return
    
    Return -->|"Final headers"| HTTPReq["HTTP Request to /api/v1/memory/*"]
```

**Scope Override Logic:**

When a memory operation specifies an explicit `scope_id`, the corresponding context header is overridden:

- `scope="workflow"`, `scope_id="custom-wf-123"` → Sets `X-Workflow-ID: custom-wf-123` [sdk/python/agentfield/memory.py:162-168]()
- `scope="session"`, `scope_id="user-session-456"` → Sets `X-Session-ID: user-session-456` [sdk/typescript/src/memory/MemoryClient.ts:81-82]()

**Sources:** [sdk/python/agentfield/memory.py:150-171](), [sdk/typescript/src/memory/MemoryClient.ts:52-88](), [sdk/python/tests/test_memory_scope_kwargs.py:83-88]()

## End-to-End Context Flow

Context headers flow from initial execution through memory operations and event notifications. This allows the Control Plane to track the provenance of every memory write.

```mermaid
sequenceDiagram
    participant CP as "Control Plane"
    participant Agent as "Agent Node"
    participant MemClient as "MemoryClient"
    participant MemAPI as "Control Plane<br/>/api/v1/memory/*"
    participant EventBus as "Memory Event Bus"
    
    CP->>Agent: POST /execute
    Note over CP,Agent: X-Workflow-ID: wf-123<br/>X-Session-ID: session-456
    
    Agent->>MemClient: memory.set("key", "value")
    MemClient->>MemClient: buildHeaders()
    Note over MemClient: Includes context from incoming request
    
    MemClient->>MemAPI: POST /api/v1/memory/set
    Note over MemClient,MemAPI: X-Workflow-ID: wf-123<br/>X-Session-ID: session-456
    
    MemAPI->>MemAPI: Store with metadata
    MemAPI->>EventBus: Emit MemoryChangeEvent
    Note over MemAPI,EventBus: Event includes scope_id: "session-456"
    
    EventBus-->>Agent: WebSocket Event (if subscribed)
```

**Sources:** [sdk/python/agentfield/memory.py:187-210](), [sdk/typescript/src/memory/MemoryEventClient.ts:71-81](), [tests/functional/tests/test_memory_events.py:28-70]()

## Context in Event Subscriptions

Memory event clients (`MemoryEventClient`) also use context propagation to filter real-time updates. When connecting via WebSocket, the client forwards context headers to the server to enable server-side filtering of events.

### WebSocket Context Propagation

```mermaid
graph TB
    Sub["Agent Subscribes to Memory Events"]
    WSConnect["MemoryEventClient.connect()"]
    Headers["Forward Headers"]
    Query["Query Params"]
    
    Sub --> WSConnect
    WSConnect --> Headers
    WSConnect --> Query
    
    Headers -->|"Includes"| XWorkflow["X-Workflow-ID"]
    Headers -->|"Includes"| XSession["X-Session-ID"]
    Headers -->|"Includes"| XAPI["X-API-Key"]
    
    Query -->|"Includes"| P_Scope["scope=session"]
    Query -->|"Includes"| P_ScopeID["scope_id=session-456"]
    
    Headers & Query --> WSReq["GET /api/v1/memory/events/ws"]
```

**Key Implementation Details:**

1. **Python `MemoryEventClient`**: Connects using headers from `self.execution_context.to_headers()` [sdk/python/agentfield/memory_events.py:149-169]().
2. **TypeScript `MemoryEventClient`**: Sanitizes headers to only forward `X-` headers, `Authorization`, and `Cookie` to the WebSocket endpoint [sdk/typescript/src/memory/MemoryEventClient.ts:102-113]().
3. **Event History**: The `history()` method also propagates context headers to the REST endpoint to retrieve historical events for the current workflow or session [sdk/typescript/src/memory/MemoryEventClient.ts:127-130]().

**Sources:** [sdk/python/agentfield/memory_events.py:127-173](), [sdk/typescript/src/memory/MemoryEventClient.ts:102-113](), [sdk/typescript/src/memory/MemoryEventClient.ts:116-158]()

## Hierarchical Fallback and Context

The `MemoryInterface` uses context to perform hierarchical lookups. When `get()` is called without an explicit scope, the client attempts to resolve the key by traversing from the most specific scope (Workflow) to the broadest (Global), using the IDs found in the execution context.

### Lookup Order Resolution

The lookup order is determined by the `getScopeOrder()` (TS) or internal logic in Python:
1. **Workflow Scope**: Uses `X-Workflow-ID` or `X-Run-ID`.
2. **Session Scope**: Uses `X-Session-ID`.
3. **Actor Scope**: Uses `X-Actor-ID`.
4. **Global Scope**: Uses the constant `'global'`.

**Sources:** [sdk/typescript/src/memory/MemoryInterface.ts:191-209](), [sdk/python/agentfield/memory.py:47-56]()

## Header Sanitization and Normalization

To ensure reliable propagation across different HTTP clients (Axios, httpx, requests), the SDKs perform sanitization.

- **TypeScript**: `sanitizeHeaders` converts all values to strings and removes `undefined`/`null` [sdk/typescript/src/memory/MemoryClient.ts:106-113]().
- **Python**: `_build_headers` merges context and ensures required headers like `X-Agent-Node-ID` are present if available [sdk/python/agentfield/memory.py:150-171]().

**Sources:** [sdk/typescript/src/memory/MemoryClient.ts:106-113](), [sdk/python/agentfield/memory.py:150-171]()

---

# Page: Identity & Trust

# Identity & Trust

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [control-plane/internal/services/vc_chain.go](control-plane/internal/services/vc_chain.go)
- [control-plane/internal/services/vc_issuance.go](control-plane/internal/services/vc_issuance.go)
- [control-plane/internal/services/vc_resolution.go](control-plane/internal/services/vc_resolution.go)
- [control-plane/internal/services/vc_service.go](control-plane/internal/services/vc_service.go)
- [control-plane/internal/services/vc_service_test.go](control-plane/internal/services/vc_service_test.go)
- [control-plane/internal/services/vc_storage.go](control-plane/internal/services/vc_storage.go)
- [control-plane/internal/services/vc_validation.go](control-plane/internal/services/vc_validation.go)
- [control-plane/pkg/types/did_types.go](control-plane/pkg/types/did_types.go)
- [control-plane/web/client/src/hooks/useVCVerification.ts](control-plane/web/client/src/hooks/useVCVerification.ts)
- [control-plane/web/client/src/types/did.ts](control-plane/web/client/src/types/did.ts)
- [examples/ts-node-examples/init-example/package.json](examples/ts-node-examples/init-example/package.json)
- [sdk/typescript/src/did/DidClient.ts](sdk/typescript/src/did/DidClient.ts)
- [sdk/typescript/src/utils/httpAgents.ts](sdk/typescript/src/utils/httpAgents.ts)
- [sdk/typescript/tests/did_client_methods.test.ts](sdk/typescript/tests/did_client_methods.test.ts)
- [sdk/typescript/tests/integration.e2e.test.ts](sdk/typescript/tests/integration.e2e.test.ts)
- [sdk/typescript/tests/memory_performance.test.ts](sdk/typescript/tests/memory_performance.test.ts)
- [tests/functional/ts_agents/echo-agent.mjs](tests/functional/ts_agents/echo-agent.mjs)

</details>



This page documents AgentField's cryptographic identity and trust system, which provides verifiable provenance for agent executions through W3C-compliant Decentralized Identifiers (DIDs) and Verifiable Credentials (VCs). This system enables cryptographic proof of execution chains, infrastructure-level access control, and compliance-ready audit trails.

**Scope**: This page covers DID hierarchies, VC generation, storage schemas, and audit trail export. For agent-to-agent communication patterns that use these identities, see [Multi-Agent Coordination](#9). For memory and state management, see [Memory System](#7).

---

## Overview

AgentField implements a hierarchical identity system where cryptographic identities are deterministically derived from a root seed. Each execution produces a tamper-evident Verifiable Credential that can be aggregated into workflow-level VCs for compliance and audit purposes.

**Core Components**:
- **DID Registry**: W3C-compliant decentralized identifiers for server, agents, and components. [control-plane/pkg/types/did_types.go:8-17]()
- **VC Engine**: Generates cryptographically signed credentials for executions. [control-plane/internal/services/vc_issuance.go:15-136]()
- **Hierarchical Derivation**: Server → Agent → Component identity chains. [control-plane/pkg/types/did_types.go:19-60]()
- **Policy Enforcement**: Infrastructure-level access control using DIDs and VCs. [control-plane/internal/services/vc_service.go:49-59]()
- **Audit Trail**: Exportable VC chains with mathematical proof. [control-plane/internal/services/vc_chain.go:13-60]()

Sources: [control-plane/internal/services/vc_service.go:19-33](), [control-plane/pkg/types/did_types.go:1-132](), [sdk/typescript/src/did/DidClient.ts:9-112]()

---

## DID Hierarchical Architecture

AgentField uses a hierarchical DID architecture where each level is cryptographically derived from its parent. This allows for fine-grained identity management (down to individual reasoners and skills) while maintaining a single root of trust.

### Identity Model Mapping

```mermaid
graph TB
    subgraph "Natural Language Space"
        Server["Control Plane Server"]
        Node["Agent Node"]
        Func["Reasoner or Skill"]
    end

    subgraph "Code Entity Space (Types)"
        Registry["DIDRegistry<br/>(agentfield_server_id)"]
        AgentInfo["AgentDIDInfo<br/>(agent_node_id)"]
        CompInfo["ReasonerDIDInfo / SkillDIDInfo<br/>(function_name)"]
    end

    Server --- Registry
    Node --- AgentInfo
    Func --- CompInfo

    Registry -->|"derives"| AgentInfo
    AgentInfo -->|"derives"| CompInfo
```

**Identity Components**:
- **DIDRegistry**: Represents the master DID registry for an `af` server, containing the `MasterSeed` and `RootDID`. [control-plane/pkg/types/did_types.go:8-17]()
- **AgentDIDInfo**: Contains DID information for an agent node, including its `PublicKeyJWK` and `X25519PublicKeyJWK` for encryption. [control-plane/pkg/types/did_types.go:19-38]()
- **Component Info**: `ReasonerDIDInfo` and `SkillDIDInfo` represent the individual functions with their own DIDs and `DerivationPath`. [control-plane/pkg/types/did_types.go:40-60]()

Sources: [control-plane/pkg/types/did_types.go:8-60](), [control-plane/web/client/src/types/did.ts:3-34]()

---

## Decentralized Identifiers (DIDs)

AgentField implements W3C-compliant DIDs (primarily using the `did:key` method) to identify every actor in the system.

- **Derivation**: Keys are derived using hierarchical deterministic paths (e.g., `m/0` for agents, `m/1` for reasoners). [sdk/typescript/src/did/DidClient.ts:158-188]()
- **Registration**: Agents register their capabilities with the control plane via `DidClient.registerAgent` to receive an `IdentityPackage`. [sdk/typescript/src/did/DidClient.ts:132-156]()
- **Key Management**: The system supports key rotation for encryption keys (`X25519Epoch`) while maintaining the primary signing identity. [control-plane/pkg/types/did_types.go:25-32]()

For details, see [Decentralized Identifiers (DIDs)](#8.1).

Sources: [sdk/typescript/src/did/DidClient.ts:9-36](), [control-plane/pkg/types/did_types.go:19-38]()

---

## Verifiable Credentials (VCs)

Every execution in AgentField can generate a Verifiable Credential (VC) that serves as a tamper-evident record of what happened.

### Execution VC Workflow

```mermaid
graph LR
    subgraph "SDK (Agent Node)"
        Params["GenerateCredentialParams"]
        Client["DidClient.generateCredential()"]
    end

    subgraph "Control Plane (VCService)"
        Issue["GenerateExecutionVC()"]
        Hash["hashData()"]
        Sign["signVC()"]
        Persist["StoreExecutionVC()"]
    end

    Params --> Client
    Client -->|"POST /api/v1/execution/vc"| Issue
    Issue --> Hash
    Issue --> Sign
    Sign --> Persist
```

- **Hashing**: Input and output data are hashed (SHA-256) to ensure integrity without necessarily storing sensitive data in the VC document. [control-plane/internal/services/vc_service.go:137-145]()
- **Signing**: Credentials are signed using Ed25519 signatures (`Ed25519Signature2020`). [control-plane/internal/services/vc_issuance.go:73-85]()
- **Aggregation**: Individual `ExecutionVC` records are aggregated into a `WorkflowVC` to provide a summary of an entire session. [control-plane/internal/services/vc_issuance.go:138-177]()

For details, see [Verifiable Credentials](#8.2).

Sources: [control-plane/internal/services/vc_issuance.go:15-136](), [sdk/typescript/src/did/DidClient.ts:190-219](), [control-plane/pkg/types/did_types.go:71-107]()

---

## Policy Enforcement

The Identity & Trust system enables infrastructure-level access control. The control plane can be configured to require VCs for execution, effectively preventing unsigned or anonymous actors from invoking sensitive reasoners or skills.

- **Requirement Flags**: `RequireVCForExecution` and `PersistExecutionVC` control the enforcement levels. [control-plane/internal/services/vc_service.go:49-70]()
- **Verification**: The `VCService.VerifyVC` method checks signatures, expiry (`expirationDate`), and revocation status. [control-plane/internal/services/vc_validation.go:17-82]()
- **Revocation**: VCs can be checked against a revocation list in storage to invalidate credentials after issuance. [control-plane/internal/services/vc_validation.go:172-218]()

For details, see [Policy Enforcement](#8.3).

Sources: [control-plane/internal/services/vc_service.go:49-70](), [control-plane/internal/services/vc_validation.go:17-82]()

---

## Audit Trail Export

AgentField provides tools to export the complete provenance of a workflow. This is essential for compliance and debugging in complex multi-agent systems.

- **VC Chain**: The `GetWorkflowVCChain` method retrieves all execution VCs associated with a `workflow_id` and generates a `DIDResolutionBundle` for offline verification. [control-plane/internal/services/vc_chain.go:13-60]()
- **Status Summaries**: The system can generate lightweight summaries (`WorkflowVCStatusSummary`) for UI dashboards to show verification health across many workflows. [control-plane/internal/services/vc_service.go:72-135]()
- **Data Integrity**: Verification results include detailed scores and integrity checks (e.g., `hash_validation`, `signature_strength`). [control-plane/web/client/src/types/did.ts:235-244]()

For details, see [Audit Trail Export](#8.4).

Sources: [control-plane/internal/services/vc_chain.go:13-123](), [control-plane/internal/services/vc_service.go:72-135](), [control-plane/web/client/src/types/did.ts:246-270]()

---

# Page: Decentralized Identifiers (DIDs)

# Decentralized Identifiers (DIDs)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [control-plane/internal/services/vc_chain.go](control-plane/internal/services/vc_chain.go)
- [control-plane/internal/services/vc_issuance.go](control-plane/internal/services/vc_issuance.go)
- [control-plane/internal/services/vc_resolution.go](control-plane/internal/services/vc_resolution.go)
- [control-plane/internal/services/vc_service.go](control-plane/internal/services/vc_service.go)
- [control-plane/internal/services/vc_service_test.go](control-plane/internal/services/vc_service_test.go)
- [control-plane/internal/services/vc_storage.go](control-plane/internal/services/vc_storage.go)
- [control-plane/internal/services/vc_validation.go](control-plane/internal/services/vc_validation.go)
- [control-plane/pkg/types/did_types.go](control-plane/pkg/types/did_types.go)
- [control-plane/web/client/src/hooks/useVCVerification.ts](control-plane/web/client/src/hooks/useVCVerification.ts)
- [control-plane/web/client/src/types/did.ts](control-plane/web/client/src/types/did.ts)
- [examples/ts-node-examples/init-example/package.json](examples/ts-node-examples/init-example/package.json)
- [sdk/typescript/src/did/DidClient.ts](sdk/typescript/src/did/DidClient.ts)
- [sdk/typescript/src/utils/httpAgents.ts](sdk/typescript/src/utils/httpAgents.ts)
- [sdk/typescript/tests/did_client_methods.test.ts](sdk/typescript/tests/did_client_methods.test.ts)
- [sdk/typescript/tests/integration.e2e.test.ts](sdk/typescript/tests/integration.e2e.test.ts)
- [sdk/typescript/tests/memory_performance.test.ts](sdk/typescript/tests/memory_performance.test.ts)
- [tests/functional/ts_agents/echo-agent.mjs](tests/functional/ts_agents/echo-agent.mjs)

</details>



## Purpose and Scope

AgentField implements W3C Decentralized Identifiers (DIDs) to provide cryptographic identity for the entire agent execution stack. DIDs enable mathematical proof of agent provenance, execution integrity, and access control without relying on centralized identity providers.

This page covers the DID implementation, hierarchical derivation, registration process, and integration with agent execution. For credential generation and verification built on top of DIDs, see [Verifiable Credentials](#8.2).

**Scope:**
- Hierarchical DID derivation from server master seed to component identities.
- W3C DID specification compliance (Ed25519 signatures, JWK format).
- Registration and resolution protocols via `DIDService` and `DidClient`.
- Key management and storage in the Control Plane.

**Sources:** [control-plane/pkg/types/did_types.go:9-17](), [sdk/typescript/src/did/DidClient.ts:9-36]()

---

## DID Hierarchy

AgentField uses a three-tier hierarchical DID structure where each level derives cryptographic keys from its parent. This creates a verifiable chain of trust from the server root to individual reasoners and skills.

### Hierarchy Visualization

```mermaid
graph TB
    subgraph ServerTier["Server Tier"]
        ServerDID["AgentField Server DID<br/>Root Identity<br/>(Master Seed)"]
        MasterSeed["Master Seed<br/>(32 bytes, encrypted at rest)"]
    end
    
    subgraph AgentTier["Agent Tier"]
        Agent1["Agent DID<br/>did:key:z6M...<br/>Derivation: m/0"]
        AgentKeys["Agent Keys<br/>(Ed25519 + X25519)"]
    end
    
    subgraph ComponentTier["Component Tier"]
        Reasoner1["Reasoner DID<br/>did:key:z6M...<br/>Derivation: m/1"]
        Skill1["Skill DID<br/>did:key:z6M...<br/>Derivation: m/101"]
    end
    
    ServerDID --> MasterSeed
    MasterSeed -->|"Derive Agent"| Agent1
    Agent1 --> AgentKeys
    AgentKeys -->|"Derive Reasoner"| Reasoner1
    AgentKeys -->|"Derive Skill"| Skill1
```

**Sources:** [control-plane/pkg/types/did_types.go:9-60](), [sdk/typescript/tests/integration.e2e.test.ts:125-186]()

### Derivation Properties

| Level | Parent | Derivation Input | Purpose |
|-------|--------|------------------|---------|
| **Server** | None | Random master seed | Root identity for the AgentField instance. |
| **Agent** | Server | Agent Node ID | Primary identity for an agent node; supports Ed25519 (signing) and X25519 (encryption). |
| **Component** | Agent | Function Name | Specific identity for a Reasoner or Skill to sign its own outputs. |

**Sources:** [control-plane/pkg/types/did_types.go:20-38](), [control-plane/pkg/types/did_types.go:41-60]()

---

## W3C DID Specification Compliance

AgentField DIDs resolve to a DID document containing public key material and metadata. The system primarily uses the `did:key` method for simplicity and portability, but supports internal resolution of agent-specific metadata.

### DID Document Mapping
The system maps internal `AgentDIDInfo` and `ReasonerDIDInfo` to W3C-compliant `VCDocument` structures during verification.

```mermaid
classDiagram
    class AgentDIDInfo {
        +String DID
        +String AgentNodeID
        +RawMessage PublicKeyJWK
        +RawMessage X25519PublicKeyJWK
        +int X25519Epoch
        +Map Reasoners
        +Map Skills
    }
    class VCDocument {
        +String id
        +String issuer
        +VCCredentialSubject credentialSubject
        +VCProof proof
    }
    AgentDIDInfo ..> VCDocument : "Resolves to"
```

**Sources:** [control-plane/pkg/types/did_types.go:20-38](), [control-plane/web/client/src/types/did.ts:102-112]()

---

## DID Registration Process

Agents register with the Control Plane during initialization to obtain their `DIDIdentityPackage`. This package contains the private keys (JWK) the agent needs to sign Verifiable Credentials locally.

### Registration Data Flow

```mermaid
sequenceDiagram
    participant SDK as "SDK (DidClient)"
    participant CP as "Control Plane (DIDService)"
    participant Store as "Storage (SQLite/Postgres)"
    
    SDK->>CP: registerAgent(DIDRegistrationRequest)
    Note over CP: Derive Agent Keys from Master Seed
    Note over CP: Derive Component Keys from Agent Keys
    CP->>Store: Save AgentDIDInfo & ComponentDIDs
    CP-->>SDK: DIDIdentityPackage (includes private keys)
    Note over SDK: Store keys in memory for signing VCs
```

**Sources:** [sdk/typescript/src/did/DidClient.ts:132-156](), [control-plane/internal/services/vc_service_test.go:54-61]()

### SDK Registration (TypeScript)
The `DidClient` handles the communication with the Control Plane's `/api/v1/did/register` endpoint.

```typescript
// sdk/typescript/src/did/DidClient.ts:132-156
async registerAgent(request: DIDRegistrationRequest): Promise<DIDRegistrationResponse> {
  const payload = {
    agent_node_id: request.agentNodeId,
    reasoners: request.reasoners,
    skills: request.skills
  };
  const res = await this.http.post('/api/v1/did/register', payload);
  return {
    success: true,
    identityPackage: this.parseIdentityPackage(res.data.identity_package)
  };
}
```

---

## Key Management

AgentField uses Ed25519 elliptic curve cryptography for signing and X25519 for encryption. Keys are represented in JSON Web Key (JWK) format.

### Key Storage and Visibility

| Key Type | Storage Location | Visibility |
|----------|------------------|------------|
| **Master Seed** | Control Plane Database | Encrypted; never leaves server. |
| **Agent Private Key** | Agent Node Memory | Sent once during registration; never persisted in CP. |
| **Agent Public Key** | Control Plane Database | Public; used for VC verification. |
| **X25519 Key** | Agent Node Memory | Used for encrypted memory/communication; supports rotation via `X25519Epoch`. |

**Sources:** [control-plane/pkg/types/did_types.go:11](), [control-plane/pkg/types/did_types.go:24-32](), [sdk/typescript/src/did/DidClient.ts:9-16]()

---

## DID Resolution and Verification

The `VCService` in the control plane provides the logic for resolving DIDs and verifying signatures on documents.

### Verification Logic (`VCService.VerifyVC`)
1. **Resolve Issuer:** Fetch the `DIDIdentity` (public key) for the `issuer` field in the VC.
2. **Signature Check:** Use `ed25519.Verify` to check the `proofValue` against the canonicalized document.
3. **Validity Window:** Check `issuanceDate`, `notBefore`, and `expirationDate`.
4. **Revocation Check:** Query the storage provider to see if the DID or specific VC has been marked as `revoked`.

**Sources:** [control-plane/internal/services/vc_validation.go:18-82](), [control-plane/internal/services/vc_validation.go:172-218]()

```mermaid
graph TD
    VC[VC Document] --> Resolve[Resolve Issuer DID]
    Resolve --> PubKey[Fetch Public Key JWK]
    PubKey --> VerifySig[Verify Ed25519 Signature]
    VerifySig --> Window[Check Validity Window]
    Window --> Revoke[Check Revocation Status]
    Revoke --> Result{Valid?}
```

---

## Implementation Details

### Go Types: `AgentDIDInfo`
The core data structure for an agent's identity in the backend.
```go
// control-plane/pkg/types/did_types.go:20-38
type AgentDIDInfo struct {
	DID                string          `json:"did" db:"did"`
	AgentNodeID        string          `json:"agent_node_id" db:"agent_node_id"`
	PublicKeyJWK       json.RawMessage `json:"public_key_jwk" db:"public_key_jwk"`
	X25519PublicKeyJWK json.RawMessage `json:"x25519_public_key_jwk,omitempty" db:"x25519_public_key_jwk"`
	X25519Epoch        int             `json:"x25519_epoch,omitempty" db:"x25519_epoch"`
	Reasoners          map[string]ReasonerDIDInfo `json:"reasoners" db:"reasoners"`
	Skills             map[string]SkillDIDInfo    `json:"skills" db:"skills"`
}
```

### TypeScript Client: `DidClient`
The SDK component used by agents to interact with identity services.
```typescript
// sdk/typescript/src/did/DidClient.ts:114-126
export class DidClient {
  private readonly http: AxiosInstance;
  
  constructor(baseUrl: string, defaultHeaders?: Record<string, any>) {
    this.http = axios.create({
      baseURL: baseUrl.replace(/\/$/, ''),
      timeout: 30000,
    });
  }
  // ... methods for registration, VC generation, and verification
}
```

**Sources:** [control-plane/pkg/types/did_types.go:20-38](), [sdk/typescript/src/did/DidClient.ts:114-126]()

---

# Page: Verifiable Credentials

# Verifiable Credentials

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [control-plane/internal/services/vc_chain.go](control-plane/internal/services/vc_chain.go)
- [control-plane/internal/services/vc_issuance.go](control-plane/internal/services/vc_issuance.go)
- [control-plane/internal/services/vc_resolution.go](control-plane/internal/services/vc_resolution.go)
- [control-plane/internal/services/vc_service.go](control-plane/internal/services/vc_service.go)
- [control-plane/internal/services/vc_service_test.go](control-plane/internal/services/vc_service_test.go)
- [control-plane/internal/services/vc_storage.go](control-plane/internal/services/vc_storage.go)
- [control-plane/internal/services/vc_validation.go](control-plane/internal/services/vc_validation.go)
- [control-plane/pkg/types/did_types.go](control-plane/pkg/types/did_types.go)
- [control-plane/web/client/src/hooks/useVCVerification.ts](control-plane/web/client/src/hooks/useVCVerification.ts)
- [control-plane/web/client/src/types/did.ts](control-plane/web/client/src/types/did.ts)
- [sdk/python/agentfield/agent_discovery.py](sdk/python/agentfield/agent_discovery.py)
- [sdk/python/agentfield/agent_pause.py](sdk/python/agentfield/agent_pause.py)
- [sdk/python/agentfield/agent_schema.py](sdk/python/agentfield/agent_schema.py)
- [sdk/python/agentfield/agent_serverless.py](sdk/python/agentfield/agent_serverless.py)
- [sdk/python/agentfield/agent_vc.py](sdk/python/agentfield/agent_vc.py)

</details>



This page documents AgentField's Verifiable Credentials (VC) system, which provides cryptographic proof of agent executions and workflow completions. For information about the Decentralized Identity (DID) system that issues VCs, see [Decentralized Identifiers (DIDs)](8.1).

**Scope**: This document covers VC data structures, generation process, validation logic, and storage mechanisms within the Control Plane and SDKs.

## Overview

AgentField's Verifiable Credentials system creates cryptographic attestations for every execution and workflow. Each VC contains hashed input/output data, cryptographic signatures from issuing DIDs, and metadata about the execution context. VCs form an immutable audit trail that can be exported for compliance and verification.

**Two-Level VC Architecture**:
- **Execution VCs**: Generated for individual reasoner or skill executions.
- **Workflow VCs**: Aggregate multiple execution VCs to represent complete workflows.

Sources: [control-plane/internal/services/vc_service.go:19-24](), [control-plane/pkg/types/did_types.go:79-115]()

## VC Data Model

### Execution VC Structure

The `ExecutionVC` represents a single functional step in the system. It supports both standard executions and trigger events (e.g., external webhooks).

```mermaid
graph TB
    subgraph "Code Entity: ExecutionVC"
        VCID["vc_id (string)"]
        ExecID["execution_id (string)"]
        WorkflowID["workflow_id (string)"]
        
        subgraph "Identity Space"
            IssuerDID["issuer_did"]
            TargetDID["target_did"]
            CallerDID["caller_did"]
        end
        
        subgraph "Integrity Space"
            InputHash["input_hash (SHA-256)"]
            OutputHash["output_hash (SHA-256)"]
            Signature["signature (Ed25519)"]
        end
        
        VCDoc["vc_document (json.RawMessage)"]
        Kind["kind (execution | trigger_event)"]
    end
```

| Field | Type | Description |
|-------|------|-------------|
| `vc_id` | string | Unique identifier prefixed with `vc-` [control-plane/internal/services/vc_service.go:148-150]() |
| `issuer_did` | string | The DID of the component that signed/issued the VC. |
| `input_hash` | string | Base64 RawURLEncoding of SHA-256 input hash [control-plane/internal/services/vc_service.go:138-145]() |
| `kind` | string | Discriminates between `execution` and `trigger_event` [control-plane/pkg/types/did_types.go:112-115]() |
| `parent_vc_id` | *string | Pointer to a parent VC to enable cross-system audit chains [control-plane/pkg/types/did_types.go:97-98]() |

Sources: [control-plane/pkg/types/did_types.go:79-107](), [control-plane/internal/services/vc_service.go:138-150]()

### Workflow VC Structure

The `WorkflowVC` aggregates the state of a complete multi-step process.

| Field | Type | Description |
|-------|------|-------------|
| `workflow_vc_id` | string | Unique workflow VC identifier. |
| `component_vcs` | []string | Array of `vc_id`s for executions belonging to this workflow. |
| `status` | string | Aggregated status (e.g., `succeeded`). |
| `total_steps` | int | Count of total execution steps. |

Sources: [control-plane/pkg/types/did_types.go:118-132]()

## VC Generation Flow

### Execution VC Issuance

The `VCService.GenerateExecutionVC` function handles the creation of a signed credential after a reasoner or skill completes its task.

```mermaid
sequenceDiagram
    participant SDK as "Agent SDK (_AgentVCMixin)"
    participant VCS as "VCService (Control Plane)"
    participant DIDS as "DIDService"
    participant Storage as "VCStorage"

    SDK->>VCS: GenerateExecutionVC(ctx, input, output, status)
    VCS->>DIDS: ResolveDID(callerDID)
    Note over VCS: Hash Input/Output (SHA-256)
    Note over VCS: Create VCDocument (W3C Standard)
    VCS->>VCS: signVC(vcDoc, callerIdentity)
    VCS->>Storage: StoreExecutionVC()
    VCS-->>SDK: ExecutionVC object
```

**Generation Logic**:
1. **Hashing**: Input and output data are hashed using SHA-256 and Base64 encoded [control-plane/internal/services/vc_service.go:138-145]().
2. **Identity Resolution**: The `caller_did` is resolved to retrieve the public key for the `VerificationMethod` [control-plane/internal/services/vc_issuance.go:50-53]().
3. **Signature**: The document is signed using the issuer's identity [control-plane/internal/services/vc_issuance.go:73-76]().
4. **Persistence**: If `PersistExecutionVC` is enabled in `DIDConfig`, the record is saved to the database [control-plane/internal/services/vc_issuance.go:126-133]().

Sources: [control-plane/internal/services/vc_issuance.go:16-136](), [sdk/python/agentfield/agent_vc.py:118-155]()

## Verification and Validation

Verification is handled by `VCService.VerifyVC`, which performs several cryptographic and structural checks.

### Verification Steps
1. **Document Parsing**: Unmarshals the JSON into a `VCDocument` type [control-plane/internal/services/vc_validation.go:27-34]().
2. **Signature Verification**: Resolves the issuer's DID and validates the `Ed25519` signature [control-plane/internal/services/vc_validation.go:47-54]().
3. **Proof Purpose**: Ensures the `proofPurpose` is exactly `assertionMethod` [control-plane/internal/services/vc_validation.go:93-101]().
4. **Validity Window**: Checks `issuanceDate`, `notBefore`, and `expirationDate` against the current UTC time [control-plane/internal/services/vc_validation.go:104-170]().
5. **Revocation Check**: Queries the database to see if the VC or the associated execution has been marked as "revoked" [control-plane/internal/services/vc_validation.go:172-218]().

Sources: [control-plane/internal/services/vc_validation.go:18-82](), [control-plane/internal/services/vc_validation.go:104-170]()

## VC Chain Retrieval

To provide a complete audit trail, the `GetWorkflowVCChain` function assembles a bundle containing all execution VCs and a DID resolution bundle for offline verification.

```mermaid
graph LR
    subgraph "Workflow VC Chain"
        WVC["WorkflowVC"]
        EVC1["ExecutionVC 1"]
        EVC2["ExecutionVC 2"]
        Bundle["DIDResolutionBundle"]
    end
    
    WVC -.->|"aggregates"| EVC1
    WVC -.->|"aggregates"| EVC2
    EVC1 -.->|"issuer/target"| Bundle
    EVC2 -.->|"issuer/target"| Bundle
```

**DID Resolution Bundle**:
To allow consumers to verify signatures without calling the AgentField API for every DID, the system collects all unique DIDs in the chain and includes their `public_key_jwk` in a `DIDResolutionBundle` [control-plane/internal/services/vc_chain.go:63-123]().

Sources: [control-plane/internal/services/vc_chain.go:14-60](), [control-plane/internal/services/vc_chain.go:63-123]()

## Configuration and Policies

VC behavior is governed by the `DIDConfig` and `VCRequirements` structures.

| Flag | Purpose |
|------|---------|
| `Enabled` | Master switch for the DID/VC system [control-plane/internal/services/vc_service.go:37-39](). |
| `RequireVCForExecution` | If true, VCs are generated automatically upon reasoner completion [control-plane/internal/services/vc_service.go:58](). |
| `PersistExecutionVC` | Controls whether VCs are stored in the database or just returned to the caller [control-plane/internal/services/vc_service.go:69](). |
| `HashSensitiveData` | Enables SHA-256 hashing of input/output data in the VC document [control-plane/internal/services/vc_service.go:139](). |

Sources: [control-plane/internal/services/vc_service.go:49-70](), [control-plane/internal/services/vc_service_test.go:29-37]()

## Python SDK Integration

The Python SDK uses the `_AgentVCMixin` to manage VC generation asynchronously during agent execution.

- **Initialization**: Sets up `DIDManager` and `VCGenerator` [sdk/python/agentfield/agent_vc.py:10-29]().
- **Async Generation**: The `_generate_vc_async` method ensures that VC creation does not block the primary agent reasoner logic [sdk/python/agentfield/agent_vc.py:118-155]().
- **Precedence**: VC settings can be overridden at the reasoner or skill level [sdk/python/agentfield/agent_vc.py:50-69]().

Sources: [sdk/python/agentfield/agent_vc.py:10-155]()

---

# Page: Policy Enforcement

# Policy Enforcement

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [control-plane/.env.example](control-plane/.env.example)
- [control-plane/internal/handlers/admin/tag_approval.go](control-plane/internal/handlers/admin/tag_approval.go)
- [control-plane/internal/handlers/empty_input_test.go](control-plane/internal/handlers/empty_input_test.go)
- [control-plane/internal/handlers/reasoners.go](control-plane/internal/handlers/reasoners.go)
- [control-plane/internal/server/middleware/permission.go](control-plane/internal/server/middleware/permission.go)
- [control-plane/internal/server/middleware/permission_test.go](control-plane/internal/server/middleware/permission_test.go)
- [control-plane/internal/services/tag_approval_service.go](control-plane/internal/services/tag_approval_service.go)
- [control-plane/web/client/src/components/authorization/AgentTagsTab.tsx](control-plane/web/client/src/components/authorization/AgentTagsTab.tsx)
- [control-plane/web/client/src/utils/dateFormat.ts](control-plane/web/client/src/utils/dateFormat.ts)

</details>



## Purpose and Scope

Policy Enforcement in AgentField provides **infrastructure-level access control** mechanisms that prevent unauthorized agent actions through cryptographic identity verification and credential validation. Unlike prompt-based restrictions that rely on AI compliance, AgentField's policies are enforced at the execution layer before any agent code runs.

This document covers:
- API key authentication for basic access control.
- DID-based identity verification and tag-based access policies.
- VC-based execution policies and audit requirements.
- The tag approval workflow for agent onboarding.

**Sources:** [control-plane/internal/server/middleware/permission.go:81-87](), [control-plane/internal/services/tag_approval_service.go:45-50]()

---

## Policy Architecture Overview

AgentField enforces policies at three levels, creating a defense-in-depth security model:

```mermaid
graph TB
    subgraph "Client Layer"
        Client["External Client<br/>or Agent"]
    end
    
    subgraph "Authentication Layer"
        APIKey["API Key Validation<br/>X-API-Key header"]
    end
    
    subgraph "Identity & Governance Layer"
        DIDAuth["DIDAuthMiddleware<br/>Cryptographic Identity"]
        PermissionCheck["PermissionCheckMiddleware<br/>Tag-based Policies"]
        TagApproval["TagApprovalService<br/>Governance & VC Issuance"]
    end
    
    subgraph "Execution Layer"
        VCPolicy["VC Policy Check<br/>Credential requirements"]
        ExecuteHandler["ExecuteHandler<br/>handlers/reasoners.go"]
    end
    
    subgraph "Target Execution"
        Reasoner["Reasoner Function"]
        Skill["Skill Function"]
    end
    
    Client -->|"1. Request"| APIKey
    APIKey -->|"2. Valid key?"| DIDAuth
    DIDAuth -->|"3. Verified DID?"| PermissionCheck
    PermissionCheck -->|"4. Policy Match?"| VCPolicy
    VCPolicy -->|"5. Execute"| ExecuteHandler
    ExecuteHandler --> Reasoner
    ExecuteHandler --> Skill
    
    PermissionCheck -.->|"Reject (403)"| Client
    TagApproval -.->|"Issues VCs"| PermissionCheck
```

**Sources:** [control-plane/internal/server/middleware/permission.go:66-87](), [control-plane/internal/handlers/reasoners.go:45-50](), [control-plane/internal/services/tag_approval_service.go:194-206]()

---

## Tag-Based Access Control

AgentField uses a tag-based system for granular authorization. Agents are assigned "Tags" (e.g., `finance`, `pii-access`) which are verified via cryptographically signed Verifiable Credentials.

### Permission Middleware Flow

The `PermissionCheckMiddleware` is the primary enforcement point in the Control Plane. It evaluates whether a caller has permission to invoke a specific target function.

| Feature | Behavior |
|---------|----------|
| **Caller Identity** | Resolved strictly from verified DIDs. Identity headers (like `X-Caller-Agent-ID`) are ignored if not backed by DID verification. |
| **Tag Precedence** | VC-verified tags take precedence over registration-time tags. If a VC exists but verification fails, the system fails closed (empty tags). |
| **Default Deny** | If `AGENTFIELD_AUTHORIZATION_DEFAULT_DENY` is true, requests with no matching policy are rejected with 403 Forbidden. |
| **Lifecycle Blocking** | Agents in `pending_approval` status are blocked from receiving any calls. |

**Sources:** [control-plane/internal/server/middleware/permission.go:115-120](), [control-plane/internal/server/middleware/permission.go:132-139](), [control-plane/internal/server/middleware/permission.go:154-169](), [control-plane/internal/server/middleware/permission.go:178-189]()

### Policy Evaluation Logic

The `AccessPolicyServiceInterface` evaluates access based on the following tuple: `(caller_tags, target_tags, function_name, input_params)`.

```mermaid
sequenceDiagram
    participant C as Caller (Agent A)
    participant CP as Control Plane
    participant P as PolicyEngine
    participant T as Target (Agent B)

    C->>CP: POST /api/v1/execute/agentB.run
    CP->>CP: DIDAuthMiddleware verifies Caller DID
    CP->>CP: PermissionCheckMiddleware starts
    CP->>CP: Resolve Target Tags (Agent B)
    CP->>CP: Resolve Caller Tags (from VC or Registry)
    CP->>P: EvaluateAccess(callerTags, targetTags, "run", input)
    P-->>CP: PolicyEvaluationResult (Allowed=true)
    CP->>T: Forward Request
```

**Sources:** [control-plane/internal/server/middleware/permission.go:172-200](), [control-plane/internal/server/middleware/permission_test.go:65-75]()

---

## Tag Approval Workflow

Before an agent can participate in the ecosystem with privileged tags, it must pass through the Tag Approval workflow managed by `TagApprovalService`.

### Lifecycle Statuses

1.  **`pending_approval`**: The agent has registered with proposed tags that require manual review. It cannot receive execution requests.
2.  **`starting` / `active`**: Tags have been approved. The system issues a `AgentTagVC` signed by the Control Plane.
3.  **`offline`**: The agent is reachable but has been manually or automatically taken offline.

**Sources:** [control-plane/internal/handlers/reasoners.go:122-140](), [control-plane/internal/services/tag_approval_service.go:194-206]()

### Administrative Actions

Administrators use the `TagApprovalHandlers` to manage agent permissions:

- **Approve**: Transitions agent to `starting` and issues a signed VC containing the approved tags.
- **Reject**: Rejects proposed tags; agent remains in restricted state.
- **Revoke**: Moves an active agent back to `pending_approval` and revokes the existing Tag VC.

**Sources:** [control-plane/internal/handlers/admin/tag_approval.go:96-156](), [control-plane/internal/handlers/admin/tag_approval.go:199-216](), [control-plane/internal/services/tag_approval_service.go:35-36]()

---

## VC-Based Policy Enforcement

Verifiable Credentials (VCs) are used to provide cryptographic proof of execution and identity.

### Execution VC Generation

The `VCGenerator` (SDK-side) or Control Plane logic ensures that every execution produces a tamper-proof record.

```mermaid
graph LR
    subgraph "VC Generation Logic"
        Input["Input Data"] --> HashIn["SHA-256 Hash"]
        Output["Output Data"] --> HashOut["SHA-256 Hash"]
        Metadata["Context (DIDs, Workflow IDs)"]
    end
    
    HashIn --> VCDoc["VC Document"]
    HashOut --> VCDoc
    Metadata --> VCDoc
    VCDoc --> Sign["Cryptographic Signature"]
    Sign --> FinalVC["Final Verifiable Credential"]
```

**Sources:** [control-plane/internal/services/tag_approval_service.go:39-43](), [control-plane/internal/services/tag_approval_service.go:230-245]()

### Configuration Options

Policy enforcement behavior is controlled via environment variables and CLI flags:

| Variable / Flag | Description | Default |
|-----------------|-------------|---------|
| `AGENTFIELD_AUTHORIZATION_DEFAULT_DENY` | If true, denies any request not explicitly allowed by a policy. | `false` |
| `AGENTFIELD_AUTHORIZATION_ADMIN_TOKEN` | Token required for admin endpoints (tag approval). | - |
| `AGENTFIELD_AUTHORIZATION_INTERNAL_TOKEN` | Secret sent to agents to verify the Control Plane as the origin. | - |
| `--no-vc-execution` | CLI flag to bypass VC generation for performance/testing. | `false` |

**Sources:** [control-plane/.env.example:51-59](), [control-plane/internal/cli/root_test.go:50]()

---

## Implementation Details

### Handling Empty Inputs

The execution handlers (`ExecuteHandler` and `ExecuteReasonerHandler`) include specific logic to handle empty or nil input objects (`{}` or missing `input` field). This ensures that parameterless skills/reasoners do not fail validation while still maintaining strict JSON binding for policy evaluation.

**Sources:** [control-plane/internal/handlers/reasoners.go:100-108](), [control-plane/internal/handlers/empty_input_test.go:45-88]()

### UI Integration

The `AgentTagsTab` component in the Control Plane dashboard provides the interface for governance. It surfaces:
- **Proposed vs. Approved Tags**: Visualizing the delta between what the agent requested and what was granted.
- **Component-Level Tags**: Granular visibility into tags for specific Reasoners or Skills.
- **Relative Timestamps**: Using `formatRelativeTime` to track registration and approval history.

**Sources:** [control-plane/web/client/src/components/authorization/AgentTagsTab.tsx:182-211](), [control-plane/web/client/src/utils/dateFormat.ts:12-45]()

---

# Page: Audit Trail Export

# Audit Trail Export

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [control-plane/internal/services/vc_chain.go](control-plane/internal/services/vc_chain.go)
- [control-plane/internal/services/vc_issuance.go](control-plane/internal/services/vc_issuance.go)
- [control-plane/internal/services/vc_resolution.go](control-plane/internal/services/vc_resolution.go)
- [control-plane/internal/services/vc_service.go](control-plane/internal/services/vc_service.go)
- [control-plane/internal/services/vc_service_test.go](control-plane/internal/services/vc_service_test.go)
- [control-plane/internal/services/vc_storage.go](control-plane/internal/services/vc_storage.go)
- [control-plane/internal/services/vc_validation.go](control-plane/internal/services/vc_validation.go)
- [control-plane/pkg/types/did_types.go](control-plane/pkg/types/did_types.go)
- [control-plane/web/client/src/hooks/useVCVerification.ts](control-plane/web/client/src/hooks/useVCVerification.ts)
- [control-plane/web/client/src/types/did.ts](control-plane/web/client/src/types/did.ts)

</details>



**Purpose**: This document describes how to export cryptographically verifiable audit trails from AgentField workflows using the Verifiable Credential (VC) chain API. Audit trail export allows compliance teams and auditors to obtain tamper-proof records of agent executions with complete provenance information.

**Scope**: This page covers the implementation of the VC chain export service, the data structures for exported audit data, and the cryptographic verification logic. For information about how VCs are generated during execution, see [Verifiable Credentials (8.2)](). For DID hierarchy and identity management, see [Decentralized Identifiers (DIDs) (8.1)]().

---

## Overview

AgentField generates Verifiable Credentials (VCs) for every execution. These credentials form an immutable audit trail that can be exported via the Control Plane. The system aggregates individual `ExecutionVC` records into a `WorkflowVC` to provide a complete provenance graph of an AI agent's decision-making process.

**Sources**: [control-plane/internal/services/vc_service.go:19-24](), [control-plane/pkg/types/did_types.go:79-107]()

---

## VC Chain Export API

The primary interface for audit trail export is handled by the `VCService` in the control plane, which aggregates data for the UI and external auditors.

### Data Flow: From Storage to Export

```mermaid
graph TD
    subgraph "Request Layer"
        API["/api/ui/v1/workflows/{id}/vc-chain"]
    end

    subgraph "Service Layer (VCService)"
        ChainHandler["GetWorkflowVCChain(workflowID)"]
        BundleHandler["collectDIDResolutionBundle()"]
        DocGen["generateWorkflowVCDocument()"]
    end

    subgraph "Storage Layer (VCStorage)"
        Store["VCStorage"]
        DB[("StorageProvider<br/>(Postgres/SQLite)")]
    end

    API --> ChainHandler
    ChainHandler -->|Fetch VCs| Store
    Store --> DB
    ChainHandler --> BundleHandler
    ChainHandler --> DocGen
    ChainHandler -->|Response| API
```

**Sources**: [control-plane/internal/services/vc_chain.go:14-60](), [control-plane/internal/services/vc_storage.go:96-99]()

### Export Response Structure

The `WorkflowVCChainResponse` provides a comprehensive bundle for offline verification.

| Field | Type | Description |
|-------|------|-------------|
| `workflow_id` | string | The unique identifier of the workflow. |
| `component_vcs` | `[]ExecutionVC` | List of all individual execution credentials in the chain. |
| `workflow_vc` | `WorkflowVC` | The aggregate credential signing the entire chain. |
| `did_resolution_bundle` | `map[string]DIDResolutionEntry` | Public keys (JWKs) for all DIDs involved, allowing offline verification. |

**Sources**: [control-plane/internal/services/vc_chain.go:52-60](), [control-plane/web/client/src/types/did.ts:250-257]()

---

## Verifiable Credential Structure

### Execution VC (Atomic Audit Unit)

The `ExecutionVC` represents a single step in a workflow (e.g., a Reasoner execution or a Skill call).

```mermaid
classDiagram
    class ExecutionVC {
        +string vc_id
        +string execution_id
        +string workflow_id
        +string issuer_did
        +string caller_did
        +string target_did
        +string input_hash
        +string output_hash
        +string signature
        +string parent_vc_id
        +json vc_document
    }
    class VCDocument {
        +string id
        +string issuer
        +string issuanceDate
        +VCCredentialSubject credentialSubject
        +VCProof proof
    }
    ExecutionVC -- VCDocument : contains
```

**Sources**: [control-plane/pkg/types/did_types.go:79-107](), [control-plane/web/client/src/types/did.ts:38-56]()

### Input/Output Hashing

To protect privacy while ensuring integrity, the `VCService` can hash sensitive data.
- **Function**: `hashData(data []byte) string` [control-plane/internal/services/vc_service.go:138-145]()
- **Implementation**: Uses SHA-256 and encodes the result in Base64 Raw URL Encoding.
- **Configuration**: Controlled by `config.VCRequirements.HashSensitiveData` [control-plane/internal/services/vc_service.go:139-141]().

---

## Verification Logic

Exported audit trails can be verified using the `VerifyVC` logic. This ensures that the data has not been tampered with since the agent execution.

### Verification Sequence

```mermaid
sequenceDiagram
    participant V as VCService
    participant D as DIDService
    participant S as Storage

    V->>V: Parse VCDocument
    V->>D: ResolveDID(issuer)
    D-->>V: Issuer Public Key (JWK)
    V->>V: verifyVCSignature(doc, key)
    V->>V: verifyVCValidityWindow(issuanceDate)
    V->>S: verifyVCRevocation(vc_id)
    S-->>V: Status (Active/Revoked)
    Note over V: If all pass, VC is Authentic
```

**Sources**: [control-plane/internal/services/vc_validation.go:18-82](), [control-plane/internal/services/vc_validation.go:172-218]()

### Key Verification Steps:
1. **Signature Check**: Validates the Ed25519 signature against the issuer's public key [control-plane/internal/services/vc_validation.go:47-54]().
2. **Proof Purpose**: Ensures the VC was intended for `assertionMethod` [control-plane/internal/services/vc_validation.go:84-102]().
3. **Validity Window**: Checks `issuanceDate`, `notBefore`, and `expirationDate` [control-plane/internal/services/vc_validation.go:104-170]().
4. **Revocation Check**: Queries the database to ensure the VC status is not "revoked" [control-plane/internal/services/vc_validation.go:172-218]().

---

## Audit Trail Persistence

Audit trails are managed by the `VCStorage` class, which abstracts the underlying `StorageProvider` (SQLite or PostgreSQL).

### Storage Methods
- `StoreExecutionVC`: Persists individual execution VCs. It automatically calculates document size if not provided [control-plane/internal/services/vc_storage.go:38-78]().
- `StoreWorkflowVC`: Persists the aggregate workflow metadata [control-plane/internal/services/vc_storage.go:141-165]().
- `ListWorkflowVCStatusSummaries`: Provides high-level statistics (count, verified vs failed) for the dashboard [control-plane/internal/services/vc_service.go:73-135]().

**Sources**: [control-plane/internal/services/vc_storage.go:14-21](), [control-plane/internal/services/vc_service.go:100-134]()

---

## Frontend Integration

The AgentField UI uses React hooks to interact with the audit trail export system.

### Hooks Reference
- `useWorkflowVCChain(workflowId)`: Fetches the complete chain for visualization [control-plane/web/client/src/hooks/useVCVerification.ts:100-131]().
- `useVCVerification()`: Provides functions to verify a VC document locally in the browser [control-plane/web/client/src/hooks/useVCVerification.ts:21-54]().
- `useAuditTrail(workflowId)`: Specifically for displaying a human-readable log derived from VCs [control-plane/web/client/src/hooks/useVCVerification.ts:136-167]().

**Sources**: [control-plane/web/client/src/hooks/useVCVerification.ts:1-15]()

---

## Configuration

VC Export and generation are governed by the `DIDConfig` structure:

| Option | Default | Description |
|--------|---------|-------------|
| `Enabled` | `true` | Master switch for the DID/VC system. |
| `RequireVCForExecution` | `true` | If true, reasoners will fail if a VC cannot be generated. |
| `PersistExecutionVC` | `true` | Whether to save VCs to the database for future export. |
| `HashSensitiveData` | `true` | If true, actual input/output data is replaced by hashes in the VC. |

**Sources**: [control-plane/internal/services/vc_service.go:51-70](), [control-plane/internal/services/vc_service_test.go:29-37]()

---

# Page: Multi-Agent Coordination

# Multi-Agent Coordination

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [control-plane/internal/handlers/execute_awaiter_status.go](control-plane/internal/handlers/execute_awaiter_status.go)
- [control-plane/internal/handlers/execute_awaiter_status_test.go](control-plane/internal/handlers/execute_awaiter_status_test.go)
- [sdk/python/agentfield/agent.py](sdk/python/agentfield/agent.py)
- [sdk/python/agentfield/async_execution_manager.py](sdk/python/agentfield/async_execution_manager.py)
- [sdk/python/agentfield/client.py](sdk/python/agentfield/client.py)
- [sdk/python/agentfield/exceptions.py](sdk/python/agentfield/exceptions.py)
- [sdk/python/agentfield/execution_state.py](sdk/python/agentfield/execution_state.py)
- [sdk/python/tests/test_agent_call.py](sdk/python/tests/test_agent_call.py)
- [sdk/python/tests/test_agent_coverage_additions.py](sdk/python/tests/test_agent_coverage_additions.py)
- [sdk/python/tests/test_async_config.py](sdk/python/tests/test_async_config.py)
- [sdk/python/tests/test_async_execution.py](sdk/python/tests/test_async_execution.py)
- [sdk/python/tests/test_client_laser_push.py](sdk/python/tests/test_client_laser_push.py)
- [sdk/python/tests/test_execution_state.py](sdk/python/tests/test_execution_state.py)
- [sdk/typescript/src/agent/Agent.ts](sdk/typescript/src/agent/Agent.ts)
- [sdk/typescript/src/ai/AIClient.ts](sdk/typescript/src/ai/AIClient.ts)
- [sdk/typescript/src/client/AgentFieldClient.ts](sdk/typescript/src/client/AgentFieldClient.ts)
- [sdk/typescript/src/context/ReasonerContext.ts](sdk/typescript/src/context/ReasonerContext.ts)
- [sdk/typescript/src/index.ts](sdk/typescript/src/index.ts)
- [sdk/typescript/src/router/AgentRouter.ts](sdk/typescript/src/router/AgentRouter.ts)
- [sdk/typescript/src/triggers/factories.ts](sdk/typescript/src/triggers/factories.ts)
- [sdk/typescript/src/triggers/index.ts](sdk/typescript/src/triggers/index.ts)
- [sdk/typescript/src/triggers/types.ts](sdk/typescript/src/triggers/types.ts)
- [sdk/typescript/src/types/agent.ts](sdk/typescript/src/types/agent.ts)
- [sdk/typescript/src/types/reasoner.ts](sdk/typescript/src/types/reasoner.ts)
- [sdk/typescript/tests/agent.test.ts](sdk/typescript/tests/agent.test.ts)
- [sdk/typescript/tests/ai_client.test.ts](sdk/typescript/tests/ai_client.test.ts)
- [sdk/typescript/tests/triggers.test.ts](sdk/typescript/tests/triggers.test.ts)

</details>



Multi-agent coordination in AgentField enables agents to discover, communicate with, and orchestrate workflows across distributed agent nodes. This page covers the mechanisms for agent discovery, cross-agent communication, workflow tracking, and asynchronous execution patterns.

For information about agent registration and lifecycle management, see [Agent Registration](#6.4). For memory sharing across agents, see [Memory Scopes](#7.1). For identity and authorization between agents, see [Decentralized Identifiers (DIDs)](#8.1).

---

## Discovery Architecture

AgentField provides a centralized discovery service through the control plane that allows agents to query for available agents, reasoners, and skills across the ecosystem. Discovery operates through the `/api/v1/discovery/capabilities` endpoint and supports multiple query formats and filtering options.

### Discovery Flow Diagram

```mermaid
graph TB
    Agent1["Agent: researcher"]
    Agent2["Agent: analyst"]
    Agent3["Agent: writer"]
    CP["Control Plane<br/>/api/v1/discovery/capabilities"]
    Registry["Agent Registry<br/>RegisteredAgents Map"]
    
    Agent1 -->|"discover(tags=['data'])"| CP
    Agent2 -->|"discover(agent='writer')"| CP
    Agent3 -->|"discover(reasoner='analyze')"| CP
    
    CP --> Registry
    Registry --> CP
    
    CP -->|"DiscoveryResponse"| Agent1
    CP -->|"DiscoveryResponse"| Agent2
    CP -->|"DiscoveryResponse"| Agent3
    
    style CP fill:#f9f9f9
    style Registry fill:#f0f0f0
```

**Sources:** [sdk/python/agentfield/client.py:400-500](), [sdk/typescript/src/client/AgentFieldClient.ts:149-217](), [sdk/typescript/src/types/agent.ts:122-148]()

---

## Agent Discovery

### Discovery Methods

#### Python SDK

The Python Agent class exposes discovery through the `discover()` method, which delegates to the underlying `AgentFieldClient`:

```python
# Discover all available agents
result = app.discover()

# Discover agents by tags
result = app.discover(tags=["nlp", "summarization"])

# Discover specific reasoner
result = app.discover(reasoner="analyze_sentiment")

# Discover with schema information
result = app.discover(
    include_input_schema=True,
    include_output_schema=True,
    include_descriptions=True
)
```

**Sources:** [sdk/python/agentfield/agent.py:1200-1230]()

#### TypeScript SDK

The TypeScript Agent provides similar discovery capabilities:

```typescript
// Discover all capabilities
const result = await agent.discover();

// Filter by agent ID
const result = await agent.discover({ agent: 'analyst' });

// Filter by tags
const result = await agent.discover({ tags: ['finance', 'risk'] });

// Request compact format
const result = await agent.discover({ format: 'compact' });
```

**Sources:** [sdk/typescript/src/agent/Agent.ts:160-162](), [sdk/typescript/src/client/AgentFieldClient.ts:149-217]()

### Discovery Response Structure

```mermaid
classDiagram
    class DiscoveryResponse {
        +string discoveredAt
        +int totalAgents
        +int totalReasoners
        +int totalSkills
        +DiscoveryPagination pagination
        +AgentCapability[] capabilities
    }
    
    class AgentCapability {
        +string agentId
        +string baseUrl
        +string version
        +string healthStatus
        +string deploymentType
        +string lastHeartbeat
        +ReasonerCapability[] reasoners
        +SkillCapability[] skills
    }
    
    class ReasonerCapability {
        +string id
        +string description
        +string[] tags
        +object inputSchema
        +object outputSchema
        +string invocationTarget
    }
    
    class SkillCapability {
        +string id
        +string description
        +string[] tags
        +object inputSchema
        +string invocationTarget
    }
    
    class DiscoveryPagination {
        +int limit
        +int offset
        +bool hasMore
    }
    
    DiscoveryResponse --> AgentCapability
    DiscoveryResponse --> DiscoveryPagination
    AgentCapability --> ReasonerCapability
    AgentCapability --> SkillCapability
```

**Sources:** [sdk/typescript/src/types/agent.ts:93-148]()

### Discovery Filters and Options

| Filter | Type | Description |
|--------|------|-------------|
| `agent` / `nodeId` | string | Filter by single agent ID |
| `agentIds` / `nodeIds` | string[] | Filter by multiple agent IDs |
| `reasoner` | string | Filter for specific reasoner |
| `skill` | string | Filter for specific skill |
| `tags` | string[] | Filter by capability tags |
| `healthStatus` | string | Filter by agent health status |
| `includeInputSchema` | boolean | Include input schemas in response |
| `includeOutputSchema` | boolean | Include output schemas in response |
| `includeDescriptions` | boolean | Include capability descriptions |
| `includeExamples` | boolean | Include usage examples |
| `format` | string | Response format: `json`, `compact`, `xml` |
| `limit` | integer | Maximum results per page |
| `offset` | integer | Pagination offset |

**Sources:** [sdk/typescript/src/types/agent.ts:160-177]()

---

## Cross-Agent Communication

Agents communicate with each other through the control plane's execution gateway. The `call()` method provides a unified interface for both local and remote agent invocation, with automatic context propagation and workflow tracking.

### Call Method Architecture

```mermaid
graph TB
    AgentA["Agent: researcher"]
    AgentB["Agent: analyst"]
    CP["AgentFieldClient<br/>/api/v1/execute/target"]
    
    subgraph "Local Execution Path"
        LocalCheck["Target = self?"]
        LocalExec["Execute Locally<br/>No HTTP Request"]
    end
    
    subgraph "Remote Execution Path"
        RemoteExec["HTTP POST to Control Plane"]
        RouteLogic["Route to Target Agent"]
        TargetExec["Execute on Target Agent"]
    end
    
    AgentA -->|"call('analyst.evaluate')"| LocalCheck
    LocalCheck -->|"No"| RemoteExec
    LocalCheck -->|"Yes"| LocalExec
    
    RemoteExec --> CP
    CP --> RouteLogic
    RouteLogic --> AgentB
    AgentB --> TargetExec
    TargetExec -->|"Result"| CP
    CP -->|"Result"| AgentA
    
    style LocalCheck fill:#f9f9f9
    style CP fill:#f0f0f0
```

**Sources:** [sdk/python/agentfield/agent.py:1231-1350](), [sdk/typescript/src/agent/Agent.ts:260-351]()

### Local vs Remote Execution

The `call()` method automatically determines whether to execute locally or route through the control plane. In the Python SDK, it utilizes `_should_execute_locally` to avoid unnecessary network hops.

| Condition | Execution Path | HTTP Request |
|-----------|----------------|--------------|
| Target agent ID matches current agent | Local | No |
| Target agent ID is omitted and reasoner exists locally | Local | No |
| Target agent ID differs from current agent | Remote via Control Plane | Yes |

**Sources:** [sdk/python/agentfield/agent.py:1231-1260](), [sdk/typescript/src/agent/Agent.ts:260-267]()

---

## Execution Context Propagation

All cross-agent calls automatically propagate execution metadata through HTTP headers. This enables automatic workflow tracking, memory scoping, and identity verification.

### Propagated Context Headers

```mermaid
graph LR
    subgraph "Execution Metadata"
        ExecID["X-Execution-ID<br/>Unique per call"]
        RunID["X-Run-ID<br/>Initial workflow ID"]
        WorkflowID["X-Workflow-ID<br/>Current workflow"]
        ParentExec["X-Parent-Execution-ID<br/>Calling execution"]
    end
    
    subgraph "Scope Context"
        SessionID["X-Session-ID<br/>User session"]
        ActorID["X-Actor-ID<br/>Actor/user identifier"]
    end
    
    subgraph "Identity Context"
        CallerDID["X-Caller-DID<br/>Calling component DID"]
        TargetDID["X-Target-DID<br/>Target component DID"]
        AgentDID["X-Agent-Node-DID<br/>Agent node DID"]
    end
```

**Sources:** [sdk/python/agentfield/execution_context.py:50-150](), [sdk/typescript/src/client/AgentFieldClient.ts:29-44]()

### Context Access in Reasoners

In TypeScript, the `ReasonerContext` provides direct access to metadata and services:

```typescript
agent.reasoner('analyze', async (ctx) => {
  console.log(`Execution ID: ${ctx.executionId}`);
  // Use context for memory operations
  const history = await ctx.memory.get('analysis_history');
  // Context automatically propagates to nested calls
  const validation = await ctx.agent.call('validator.check', ctx.input);
  return { result: validation };
});
```

**Sources:** [sdk/typescript/src/context/ReasonerContext.ts:13-86]()

---

## Asynchronous Execution

AgentField supports long-running, asynchronous operations that can execute for minutes, hours, or days. Asynchronous execution uses webhooks for result delivery and supports timeout configuration.

### Async Execution Flow

```mermaid
sequenceDiagram
    participant Client as Client/Agent
    participant CP as Control Plane
    participant Agent as Target Agent
    participant Webhook as Webhook Endpoint
    
    Client->>CP: POST /api/v1/execute/target<br/>X-Async: true
    
    CP->>Agent: POST /execute (async)
    CP-->>Client: 202 Accepted<br/>{execution_id, status: 'queued'}
    
    Note over Agent: Long-running execution
    
    Agent->>CP: Execution Complete<br/>{status, result}
    CP->>Webhook: POST webhook_url<br/>{execution_id, result, status}
```

**Sources:** [sdk/python/agentfield/async_config.py:1-100](), [sdk/python/agentfield/async_execution_manager.py:185-220]()

### Polling and Timeouts

The `AsyncExecutionManager` in the Python SDK manages concurrent async executions with intelligent polling and adaptive intervals [sdk/python/agentfield/async_execution_manager.py:185-200](). In TypeScript, the `executionBudgetMs` configuration bounds the active-time wall-clock budget for detached reasoners [sdk/typescript/src/types/agent.ts:46-53]().

---

## Best Practices

1. **Prefer Local Execution**: Use `call()` with local targets to avoid network overhead when calling capabilities on the same node [sdk/python/agentfield/agent.py:1231-1260]().
2. **Handle Timeouts**: Use `ExecutionTimeoutError` to manage long-running cross-agent calls [sdk/python/agentfield/exceptions.py:74-77]().
3. **Use Webhooks**: For operations exceeding the synchronous dispatch ceiling, configure `AsyncConfig` with a `webhook_url` [sdk/python/agentfield/async_config.py:40-60]().
4. **Resilient Retries**: The SDK skips sync fallback for `ExecutionFailedError` to prevent doubling costs on deterministic failures [sdk/python/tests/test_agent_call.py:136-176]().

---

**Sources:**
- [sdk/python/agentfield/agent.py:1200-1400]()
- [sdk/typescript/src/agent/Agent.ts:110-155]()
- [sdk/python/agentfield/client.py:142-220]()
- [sdk/typescript/src/client/AgentFieldClient.ts:146-217]()
- [sdk/typescript/src/types/agent.ts:10-54]()
- [sdk/python/agentfield/async_execution_manager.py:185-220]()
- [sdk/python/agentfield/exceptions.py:17-96]()

---

# Page: Agent Discovery

# Agent Discovery

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [control-plane/internal/handlers/agentic/agent_summary.go](control-plane/internal/handlers/agentic/agent_summary.go)
- [control-plane/internal/handlers/agentic/agentic_test.go](control-plane/internal/handlers/agentic/agentic_test.go)
- [control-plane/internal/handlers/agentic/batch.go](control-plane/internal/handlers/agentic/batch.go)
- [control-plane/internal/handlers/agentic/coverage_additional_test.go](control-plane/internal/handlers/agentic/coverage_additional_test.go)
- [control-plane/internal/handlers/agentic/discover.go](control-plane/internal/handlers/agentic/discover.go)
- [control-plane/internal/handlers/agentic/helpers.go](control-plane/internal/handlers/agentic/helpers.go)
- [control-plane/internal/handlers/agentic/kb.go](control-plane/internal/handlers/agentic/kb.go)
- [control-plane/internal/handlers/agentic/query.go](control-plane/internal/handlers/agentic/query.go)
- [control-plane/internal/handlers/agentic/run_overview.go](control-plane/internal/handlers/agentic/run_overview.go)
- [control-plane/internal/handlers/agentic/status.go](control-plane/internal/handlers/agentic/status.go)
- [control-plane/internal/handlers/execute_awaiter_status.go](control-plane/internal/handlers/execute_awaiter_status.go)
- [control-plane/internal/handlers/execute_awaiter_status_test.go](control-plane/internal/handlers/execute_awaiter_status_test.go)
- [sdk/python/agentfield/agent.py](sdk/python/agentfield/agent.py)
- [sdk/python/agentfield/async_execution_manager.py](sdk/python/agentfield/async_execution_manager.py)
- [sdk/python/agentfield/client.py](sdk/python/agentfield/client.py)
- [sdk/python/agentfield/exceptions.py](sdk/python/agentfield/exceptions.py)
- [sdk/python/agentfield/execution_state.py](sdk/python/agentfield/execution_state.py)
- [sdk/python/tests/test_agent_call.py](sdk/python/tests/test_agent_call.py)
- [sdk/python/tests/test_agent_coverage_additions.py](sdk/python/tests/test_agent_coverage_additions.py)
- [sdk/python/tests/test_async_config.py](sdk/python/tests/test_async_config.py)
- [sdk/python/tests/test_async_execution.py](sdk/python/tests/test_async_execution.py)
- [sdk/python/tests/test_client_laser_push.py](sdk/python/tests/test_client_laser_push.py)
- [sdk/python/tests/test_execution_state.py](sdk/python/tests/test_execution_state.py)

</details>



## Purpose and Scope

Agent Discovery provides a query interface for agents to find and inspect other agents, reasoners, and skills registered with the AgentField control plane. This page documents the discovery API, filtering options, response formats, and SDK usage patterns.

For information about calling discovered capabilities, see [Cross-Agent Calls](#9.2). For details on agent registration, see [Agent Registration](#6.4).

---

## Discovery Overview

The discovery system allows agents to dynamically query the control plane for available capabilities at runtime. This enables agents to:

- Locate other agents by ID or health status
- Find reasoners and skills by name or tag
- Inspect capability schemas before invocation
- Build dynamic agent workflows based on available resources

**Discovery Flow**

```mermaid
sequenceDiagram
    participant Agent [Agent]
    participant SDK [SDK discover()]
    participant CP [Control Plane /api/v1/discovery/capabilities]
    participant Storage [StorageProvider]

    Agent->>SDK: "discover(options)"
    SDK->>CP: "GET /api/v1/discovery/capabilities?format=json&reasoner=summarize"
    CP->>Storage: "QueryRegisteredAgents(filters)"
    Storage-->>CP: "Agent capabilities"
    CP-->>SDK: "DiscoveryResponse"
    SDK-->>Agent: "DiscoveryResult"
```

**Sources:**
- [sdk/python/agentfield/client.py:142-300]()
- [sdk/python/agentfield/agent.py:1-100]()

---

## Discovery API Endpoint

The control plane exposes discovery at:

```
GET /api/v1/discovery/capabilities
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `format` | string | Response format: `json` (default), `compact`, `xml` |
| `agent` | string | Single agent/node ID filter |
| `agent_ids` | string | Comma-separated agent IDs |
| `reasoner` | string | Filter by reasoner name |
| `skill` | string | Filter by skill name |
| `tags` | string | Comma-separated tag list |
| `health_status` | string | Filter by health: `healthy`, `ready`, `degraded`, `offline` |
| `include_input_schema` | boolean | Include reasoner/skill input schemas |
| `include_output_schema` | boolean | Include reasoner output schemas |
| `include_descriptions` | boolean | Include capability descriptions |
| `include_examples` | boolean | Include usage examples |
| `limit` | integer | Pagination limit |
| `offset` | integer | Pagination offset |

**Sources:**
- [sdk/python/agentfield/client.py:201-272]()
- [control-plane/internal/handlers/agentic/helpers.go:85-98]()

---

## Discovery Response Formats

### JSON Format (Default)

Full structured response with complete capability metadata. In the Python SDK, this is handled via `DiscoveryResponse` and `AgentCapability` mappings.

**Response Structure:**

```mermaid
graph TB
    DR["DiscoveryResponse"]
    DR --> Meta["discovered_at<br/>total_agents<br/>total_reasoners<br/>total_skills"]
    DR --> Pagination["pagination<br/>• limit<br/>• offset<br/>• has_more"]
    DR --> Caps["capabilities[]"]
    
    Caps --> AC["AgentCapability"]
    AC --> AgentMeta["agent_id<br/>base_url<br/>version<br/>health_status<br/>deployment_type<br/>last_heartbeat"]
    AC --> Reasoners["reasoners[]"]
    AC --> Skills["skills[]"]
    
    Reasoners --> RC["ReasonerCapability<br/>• id<br/>• description<br/>• tags<br/>• input_schema<br/>• output_schema<br/>• examples<br/>• invocation_target"]
    
    Skills --> SC["SkillCapability<br/>• id<br/>• description<br/>• tags<br/>• input_schema<br/>• invocation_target"]
```

**Sources:**
- [sdk/python/agentfield/client.py:299-300]()
- [sdk/python/agentfield/types.py:56-62]()

### Compact Format

Minimal response optimized for low-latency discovery queries, using the `CompactDiscoveryResponse` class in Python.

**Response Structure:**

```python
# CompactDiscoveryResponse (Python SDK)
{
  "discovered_at": str,
  "reasoners": List[CompactCapability],
  "skills": List[CompactCapability]
}

# CompactCapability:
{
  "id": str,           # Reasoner/skill name
  "agent_id": str,     # Owner agent
  "target": str,       # Invocation target (agent.capability)
  "tags": List[str]    # Associated tags
}
```

**Sources:**
- [sdk/python/agentfield/client.py:14-16]()
- [sdk/python/agentfield/client.py:293-295]()

---

## Python SDK Usage

### Basic Discovery

The `Agent` class provides a high-level `discover()` method that delegates to the `AgentFieldClient`.

```python
from agentfield.agent import Agent

agent = Agent(node_id="orchestrator")

# Discover all capabilities
result = agent.discover()

# Access JSON response
if result.json:
    print(f"Found {result.json.total_agents} agents")
    for capability in result.json.capabilities:
        print(f"Agent: {capability.agent_id}")
        for reasoner in capability.reasoners:
            print(f"  Reasoner: {reasoner.invocation_target}")
```

### Discovery Client

The underlying `AgentFieldClient` in `sdk/python/agentfield/client.py` provides the actual implementation of `discover_capabilities`.

```python
from agentfield.client import AgentFieldClient

client = AgentFieldClient(base_url="http://localhost:8080")

result = client.discover_capabilities(
    agent_ids=["agent1", "agent2"],
    reasoner="analyze",
    limit=50,
    offset=0
)
```

**Sources:**
- [sdk/python/agentfield/client.py:142-300]()
- [sdk/python/agentfield/agent.py:2400-2450]() (inferred discovery method)

---

## Discovery Response Mapping

### Agent Capability Structure

```mermaid
graph LR
    subgraph "AgentCapability (Python SDK)"
        A["agent_id"]
        B["base_url"]
        C["version"]
        D["health_status"]
        E["deployment_type"]
        F["last_heartbeat"]
        R["reasoners[]"]
        S["skills[]"]
    end
    
    R --> R1["ReasonerCapability<br/>• id<br/>• description<br/>• tags<br/>• input_schema<br/>• output_schema<br/>• examples<br/>• invocation_target"]
    
    S --> S1["SkillCapability<br/>• id<br/>• description<br/>• tags<br/>• input_schema<br/>• invocation_target"]
```

**Sources:**
- [sdk/python/agentfield/client.py:299-300]()
- [sdk/python/agentfield/types.py:59-62]()

---

## Implementation Details

### Header Propagation and Security

Discovery requests propagate execution context headers to ensure that discovery results respect the current workflow's permissions and visibility.

```python
# sdk/python/agentfield/client.py
# Headers are sanitized and merged from the execution context
sanitized_headers = self._sanitize_header_values(headers)
```

The control plane uses `getAuthLevel` in `control-plane/internal/handlers/agentic/helpers.go` to determine the requester's permissions based on `X-API-Key` or `Authorization` headers.

**Sources:**
- [sdk/python/agentfield/client.py:201-216]()
- [control-plane/internal/handlers/agentic/helpers.go:69-82]()

### Async Context Integration

The discovery system is designed to work within the `AsyncExecutionManager` framework. While discovery itself is usually a synchronous GET request from the SDK's perspective, the results (invocation targets) are used to trigger async executions via `execute_async`.

```mermaid
graph TD
    subgraph "Code Entity Space"
        Discovery["AgentFieldClient.discover_capabilities()"]
        Result["DiscoveryResult"]
        AsyncExec["AsyncExecutionManager.execute_async()"]
        Poll["AsyncExecutionManager._polling_task()"]
    end

    subgraph "Natural Language Space"
        Query["'Find a summarizer'"]
        Target["'researcher.summarize'"]
        Run["'Run summary task'"]
    end

    Query --> Discovery
    Discovery --> Result
    Result --> Target
    Target --> AsyncExec
    AsyncExec --> Run
    Run --> Poll
```

**Sources:**
- [sdk/python/agentfield/client.py:142-300]()
- [sdk/python/agentfield/async_execution_manager.py:185-220]()
- [sdk/python/agentfield/execution_state.py:121-177]()

---

## Best Practices

1. **Filter Early**: Use `tags` and `reasoner` parameters to minimize the payload size returned by the control plane.
2. **Health Checks**: Always check `health_status` in the `DiscoveryResult` to avoid calling offline agents.
3. **Pagination**: For large environments, check `has_more` in the pagination metadata and use `offset` to iterate through results.
4. **Error Handling**: Catch `AgentFieldClientError` for network issues and `ExecuteError` for control-plane specific failures.

**Sources:**
- [sdk/python/agentfield/client.py:269-272]()
- [sdk/python/agentfield/exceptions.py:11-34]()
- [sdk/python/agentfield/execution_state.py:15-28]()

---

# Page: Cross-Agent Calls

# Cross-Agent Calls

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [control-plane/internal/handlers/execute_awaiter_status.go](control-plane/internal/handlers/execute_awaiter_status.go)
- [control-plane/internal/handlers/execute_awaiter_status_test.go](control-plane/internal/handlers/execute_awaiter_status_test.go)
- [sdk/python/agentfield/agent.py](sdk/python/agentfield/agent.py)
- [sdk/python/agentfield/async_execution_manager.py](sdk/python/agentfield/async_execution_manager.py)
- [sdk/python/agentfield/client.py](sdk/python/agentfield/client.py)
- [sdk/python/agentfield/exceptions.py](sdk/python/agentfield/exceptions.py)
- [sdk/python/agentfield/execution_state.py](sdk/python/agentfield/execution_state.py)
- [sdk/python/tests/test_agent_call.py](sdk/python/tests/test_agent_call.py)
- [sdk/python/tests/test_agent_coverage_additions.py](sdk/python/tests/test_agent_coverage_additions.py)
- [sdk/python/tests/test_async_config.py](sdk/python/tests/test_async_config.py)
- [sdk/python/tests/test_async_execution.py](sdk/python/tests/test_async_execution.py)
- [sdk/python/tests/test_client_laser_push.py](sdk/python/tests/test_client_laser_push.py)
- [sdk/python/tests/test_execution_state.py](sdk/python/tests/test_execution_state.py)
- [sdk/typescript/src/agent/Agent.ts](sdk/typescript/src/agent/Agent.ts)
- [sdk/typescript/src/ai/AIClient.ts](sdk/typescript/src/ai/AIClient.ts)
- [sdk/typescript/src/client/AgentFieldClient.ts](sdk/typescript/src/client/AgentFieldClient.ts)
- [sdk/typescript/src/context/ReasonerContext.ts](sdk/typescript/src/context/ReasonerContext.ts)
- [sdk/typescript/src/index.ts](sdk/typescript/src/index.ts)
- [sdk/typescript/src/router/AgentRouter.ts](sdk/typescript/src/router/AgentRouter.ts)
- [sdk/typescript/src/triggers/factories.ts](sdk/typescript/src/triggers/factories.ts)
- [sdk/typescript/src/triggers/index.ts](sdk/typescript/src/triggers/index.ts)
- [sdk/typescript/src/triggers/types.ts](sdk/typescript/src/triggers/types.ts)
- [sdk/typescript/src/types/agent.ts](sdk/typescript/src/types/agent.ts)
- [sdk/typescript/src/types/reasoner.ts](sdk/typescript/src/types/reasoner.ts)
- [sdk/typescript/tests/agent.test.ts](sdk/typescript/tests/agent.test.ts)
- [sdk/typescript/tests/ai_client.test.ts](sdk/typescript/tests/ai_client.test.ts)
- [sdk/typescript/tests/triggers.test.ts](sdk/typescript/tests/triggers.test.ts)

</details>



This page documents how agents invoke capabilities (reasoners and skills) on other agents using the `call()` method. Cross-agent calls enable distributed multi-agent workflows where agents coordinate by directly invoking each other's registered capabilities through the AgentField control plane.

For discovering available capabilities before calling them, see **9.1 Agent Discovery**. For understanding how workflows are tracked across calls, see **9.3 Workflow Tracking**. For asynchronous execution patterns, see **9.4 Asynchronous Execution**.

---

## Overview

Cross-agent calls allow one agent to invoke a reasoner or skill registered on another agent node. The AgentField SDK provides a unified `call()` method that:

1.  **Routes local calls directly** when the target is on the same agent node [sdk/python/agentfield/agent.py:1024-1150]().
2.  **Routes remote calls through the control plane** using the `AgentFieldClient` [sdk/typescript/src/agent/Agent.ts:337-351]().
3.  **Propagates execution context** automatically (Workflow ID, Session ID, etc.) across all calls [sdk/python/agentfield/agent.py:1150-1200]().
4.  **Maintains workflow lineage** by tracking parent-child relationships between executions [sdk/typescript/src/agent/Agent.ts:288-303]().

**Key Components:**
*   `Agent.call()` / `app.call()`: Unified SDK method for invoking capabilities [sdk/python/agentfield/agent.py:1024-1030]().
*   `AgentFieldClient.execute()`: Client used for remote execution dispatch [sdk/python/agentfield/client.py:198-217]().
*   `ExecutionContext`: Container for propagated metadata [sdk/typescript/src/context/ExecutionContext.ts:5-15]().

**Sources:** [sdk/python/agentfield/agent.py:1024-1200](), [sdk/typescript/src/agent/Agent.ts:260-351](), [sdk/python/agentfield/client.py:198-217]()

---

## Cross-Agent Call Flow

The following diagram illustrates how the SDK bridges "Natural Language Space" (the intent to call an analyst) with "Code Entity Space" (the `AgentFieldClient` and control plane routes).

### Cross-Agent Call Routing

```mermaid
sequenceDiagram
    participant A as "Agent [researcher]<br/>(agent.py / Agent.ts)"
    participant Client as "AgentFieldClient<br/>(client.py)"
    participant CP as "Control Plane<br/>/api/v1/execute"
    participant B as "Agent [analyst]<br/>(AgentServer)"
    
    Note over A: Reasoner executing
    
    A->>A: "app.call('analyst.evaluate', input)"
    
    alt Local Call (same node)
        A->>A: "Find local SkillEntry/ReasonerEntry"
        A->>A: "Execute via ExecutionContext.run()"
    else Remote Call (different node)
        A->>Client: "execute('analyst.evaluate', input, metadata)"
        Client->>CP: "POST /api/v1/execute/analyst.evaluate"
        Note over CP: "Route to agent 'analyst'"
        CP->>B: "POST /execute (with headers)"
        B->>B: "Handle via AgentFieldHandler"
        B-->>CP: "Return result"
        CP-->>Client: "Return JSON result"
        Client-->>A: "Return result to reasoner"
    end
```

**Sources:** [sdk/python/agentfield/agent.py:1024-1150](), [sdk/typescript/src/agent/Agent.ts:260-351](), [sdk/python/agentfield/client.py:198-228]()

---

## Target Resolution

The `call()` method accepts a target string in the format `agent_id.capability_name`.

### Target Format
*   **Full target**: `"analyst.evaluate"` → agent `analyst`, capability `evaluate`.
*   **Short target**: `"evaluate"` → current agent, capability `evaluate`.

### Implementation
The Python SDK uses `_parse_target()` to extract agent and capability names [sdk/python/agentfield/agent.py:2115-2152](). The TypeScript SDK implements similar logic in `parseTarget()` [sdk/typescript/src/agent/Agent.ts:893-906]().

**Sources:** [sdk/python/agentfield/agent.py:2115-2152](), [sdk/typescript/src/agent/Agent.ts:893-906]()

---

## Local vs Remote Call Decision

The SDK determines whether to execute locally or route through the control plane based on the target agent ID.

```mermaid
flowchart TD
    Start["app.call(target, input)"]
    Parse["Parse target into<br/>agent_id, capability_name"]
    CheckAgent{"agent_id matches<br/>node_id OR<br/>agent_id is None?"}
    
    Local["Local Call Path"]
    Remote["Remote Call Path"]
    
    FindLocal["Find local SkillEntry/ReasonerEntry"]
    FoundLocal{"Found?"}
    ExecLocal["Create ExecutionContext<br/>Execute locally<br/>Return result"]
    
    Client["AgentFieldClient.execute()"]
    CP["Control Plane Gateway"]
    ExecRemote["Remote Node execution"]
    
    NotFound["Raise TargetNotFoundError"]
    
    Start --> Parse
    Parse --> CheckAgent
    CheckAgent -->|Yes| Local
    CheckAgent -->|No| Remote
    
    Local --> FindLocal
    FindLocal --> FoundLocal
    FoundLocal -->|Yes| ExecLocal
    FoundLocal -->|No| NotFound
    
    Remote --> Client
    Client --> CP
    CP --> ExecRemote
```

**Sources:** [sdk/python/agentfield/agent.py:1024-1150](), [sdk/typescript/src/agent/Agent.ts:260-337]()

---

## Execution Context Propagation

All cross-agent calls automatically propagate execution metadata via HTTP headers to maintain workflow lineage.

### Propagated Metadata

| Metadata Field | Header Name | Description |
| :--- | :--- | :--- |
| `workflow_id` | `X-Workflow-ID` | Top-level workflow identifier [sdk/typescript/src/client/AgentFieldClient.ts:31]() |
| `run_id` | `X-Run-ID` | Specific run identifier [sdk/typescript/src/client/AgentFieldClient.ts:30]() |
| `execution_id` | `X-Execution-ID` | Unique ID for this specific execution [sdk/typescript/src/client/AgentFieldClient.ts:29]() |
| `parent_execution_id` | `X-Parent-Execution-ID` | ID of the calling execution [sdk/typescript/src/client/AgentFieldClient.ts:33]() |
| `caller_did` | `X-Caller-DID` | Caller's Decentralized Identifier [sdk/typescript/src/client/AgentFieldClient.ts:37]() |

### Context Capture and Forwarding
In TypeScript, the `AgentFieldClient.buildExecuteHeaders` method prepares these headers [sdk/typescript/src/client/AgentFieldClient.ts:218-228](). In Python, `Agent.call` extracts these from the `get_current_context()` utility [sdk/python/agentfield/agent.py:1150-1200]().

**Sources:** [sdk/typescript/src/client/AgentFieldClient.ts:29-44](), [sdk/python/agentfield/agent.py:1150-1200]()

---

## Advanced Execution Patterns

### Async Fallback Logic
The Python SDK supports a two-tier execution pattern:
1.  **Async First**: Attempt to dispatch the call asynchronously via `execute_async` [sdk/python/agentfield/agent.py:1180-1195]().
2.  **Sync Fallback**: If async execution is disabled or fails due to specific transport issues, it falls back to a synchronous call [sdk/python/agentfield/agent.py:1197-1205]().

> **Note**: The SDK intentionally skips sync fallback if the error is `ExecutionFailedError` or `ExecutionTimeoutError` to prevent doubling costs for deterministic failures [sdk/python/tests/test_agent_call.py:136-184]().

### Pause and Resume
Cross-agent calls can be interrupted by human-in-the-loop approvals using `ctx.pause()`. This transitions the execution to a `waiting` state on the control plane [sdk/typescript/src/context/ReasonerContext.ts:151-158]().

**Sources:** [sdk/python/agentfield/agent.py:1180-1205](), [sdk/python/tests/test_agent_call.py:136-184](), [sdk/typescript/src/context/ReasonerContext.ts:151-158]()

---

## SDK Implementation Reference

### Python SDK (`Agent.call`)
The Python implementation manages the lifecycle of the call, including argument mapping and context switching.

[sdk/python/agentfield/agent.py:1024-1200]()

### TypeScript SDK (`Agent.call`)
The TypeScript implementation uses `ExecutionContext.run` to wrap local calls and `AgentFieldClient` for remote dispatch.

[sdk/typescript/src/agent/Agent.ts:260-351]()

### Control Plane Client (`AgentFieldClient`)
The client handles the low-level HTTP communication, DID signing, and header sanitization.

[sdk/python/agentfield/client.py:142-230]()
[sdk/typescript/src/client/AgentFieldClient.ts:146-230]()

**Sources:** [sdk/python/agentfield/agent.py:1024-1200](), [sdk/typescript/src/agent/Agent.ts:260-351](), [sdk/python/agentfield/client.py:142-230](), [sdk/typescript/src/client/AgentFieldClient.ts:146-230]()

---

# Page: Workflow Tracking

# Workflow Tracking

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [control-plane/internal/handlers/did_handlers.go](control-plane/internal/handlers/did_handlers.go)
- [control-plane/internal/handlers/execute.go](control-plane/internal/handlers/execute.go)
- [control-plane/internal/handlers/execute_async_test.go](control-plane/internal/handlers/execute_async_test.go)
- [control-plane/internal/handlers/execute_status_update_test.go](control-plane/internal/handlers/execute_status_update_test.go)
- [control-plane/internal/handlers/execution_status_handler_test.go](control-plane/internal/handlers/execution_status_handler_test.go)
- [control-plane/internal/handlers/workflow_dag.go](control-plane/internal/handlers/workflow_dag.go)
- [control-plane/internal/handlers/workflow_execution_events.go](control-plane/internal/handlers/workflow_execution_events.go)
- [control-plane/internal/handlers/workflow_execution_events_test.go](control-plane/internal/handlers/workflow_execution_events_test.go)
- [control-plane/internal/storage/retry_test.go](control-plane/internal/storage/retry_test.go)
- [control-plane/web/client/src/components/WorkflowDAG/DeckGLView.tsx](control-plane/web/client/src/components/WorkflowDAG/DeckGLView.tsx)
- [control-plane/web/client/src/components/WorkflowDAG/hooks/useNodeDetails.ts](control-plane/web/client/src/components/WorkflowDAG/hooks/useNodeDetails.ts)
- [control-plane/web/client/src/components/WorkflowDAG/index.tsx](control-plane/web/client/src/components/WorkflowDAG/index.tsx)
- [control-plane/web/client/src/components/WorkflowDAG/layouts/LayoutManager.ts](control-plane/web/client/src/components/WorkflowDAG/layouts/LayoutManager.ts)
- [control-plane/web/client/src/components/WorkflowDAG/layouts/layoutWorker.ts](control-plane/web/client/src/components/WorkflowDAG/layouts/layoutWorker.ts)
- [control-plane/web/client/src/components/execution/EnhancedModal.tsx](control-plane/web/client/src/components/execution/EnhancedModal.tsx)
- [control-plane/web/client/src/components/execution/ExecutionHeader.tsx](control-plane/web/client/src/components/execution/ExecutionHeader.tsx)
- [control-plane/web/client/src/components/execution/ExecutionIdentityPanel.tsx](control-plane/web/client/src/components/execution/ExecutionIdentityPanel.tsx)
- [control-plane/web/client/src/components/layout/ResponsiveGrid.tsx](control-plane/web/client/src/components/layout/ResponsiveGrid.tsx)
- [control-plane/web/client/src/components/reasoners/ExecutionForm.tsx](control-plane/web/client/src/components/reasoners/ExecutionForm.tsx)
- [control-plane/web/client/src/components/ui/auto-expanding-textarea.tsx](control-plane/web/client/src/components/ui/auto-expanding-textarea.tsx)
- [sdk/python/agentfield/agent_workflow.py](sdk/python/agentfield/agent_workflow.py)

</details>



AgentField automatically tracks all agent executions as a directed acyclic graph (DAG), capturing parent-child relationships, execution hierarchies, and the complete call chain without requiring developers to manually instrument their code. Every agent invocation is assigned unique identifiers and tracked in the control plane's storage layer.

For information about how agents discover and call each other, see [9.1 Agent Discovery]() and [9.2 Cross-Agent Calls](). For long-running asynchronous tasks, see [9.4 Asynchronous Execution]().

---

## Core Tracking Identifiers

AgentField uses several identifiers to track workflow execution:

| Identifier | Purpose | Scope | Generation |
|------------|---------|-------|------------|
| `workflow_id` | Unique identifier for a workflow instance | Global | Generated by control plane on first execution |
| `execution_id` | Unique identifier for a single execution | Per-execution | Generated for each agent/reasoner invocation |
| `parent_execution_id` | Reference to parent execution | Per-execution | Inherited from caller context |
| `root_workflow_id` | Reference to the root workflow | Per-execution | Propagated through entire call chain |
| `workflow_depth` | Depth in the execution tree | Per-execution | Incremented with each nested call |
| `run_id` | Optional identifier for a logical run | Per-run | User-provided or generated |

**Sources:**
- [control-plane/pkg/types/executions.go:42-105]()
- [control-plane/internal/handlers/workflow_dag.go:27-44]()

---

## Automatic DAG Generation

AgentField builds execution DAGs automatically. Each time an agent node reports an execution event (start, success, or failure), the control plane updates the execution graph.

### Execution Event Ingestion
The `WorkflowExecutionEventHandler` in [control-plane/internal/handlers/workflow_execution_events.go:35-84]() processes events from agents. If a step starts and no record exists, it calls `buildExecutionRecordFromEvent` [control-plane/internal/handlers/workflow_execution_events.go:86-128]() to initialize the tracking metadata, including `parent_execution_id` and `run_id`.

```mermaid
graph TD
    subgraph "Code Entity Space"
        H["WorkflowExecutionEventHandler<br/>(handlers/workflow_execution_events.go)"]
        S["ExecutionStore<br/>(handlers/execute.go)"]
        R["buildExecutionRecordFromEvent<br/>(handlers/workflow_execution_events.go)"]
    end

    subgraph "Natural Language Space"
        Event["Agent Execution Event<br/>(Status: running/succeeded)"]
        DB["Workflow Executions Table"]
    end

    Event --> H
    H --> R
    R -->|"execution_id, parent_id"| S
    S -->|"StoreWorkflowExecution"| DB
```
**Diagram: Workflow Event Processing Pipeline**

**Sources:**
- [control-plane/internal/handlers/workflow_execution_events.go:35-84]()
- [control-plane/internal/handlers/execute.go:41-43]()

---

## Execution Status Management

Executions transition through various states. The control plane enforces terminal state immutability to prevent late-arriving "running" events from overwriting "succeeded" or "failed" results—a common race condition in distributed agent systems.

### Terminal Regression Guard
In `applyEventToExecution` [control-plane/internal/handlers/workflow_execution_events.go:130-190](), the system checks `types.IsTerminalExecutionStatus(current.Status)`. If the execution is already in a terminal state, the update is ignored except for the `updated_at` timestamp [control-plane/internal/handlers/workflow_execution_events.go:141-144]().

| Status | Terminal | Description |
|--------|----------|-------------|
| `pending` | No | Execution is enqueued |
| `running` | No | Agent is currently processing |
| `succeeded`| Yes | Execution completed successfully |
| `failed` | Yes | Execution encountered an error |

**Sources:**
- [control-plane/internal/handlers/workflow_execution_events.go:130-190]()
- [control-plane/internal/handlers/execute_status_update_test.go:20-76]()

---

## DAG Query and Reconstruction

The control plane provides endpoints to reconstruct the execution graph for visualization.

### Execution Graph Service
The `executionGraphService` [control-plane/internal/handlers/workflow_dag.go:18-24]() handles the retrieval of DAG nodes. It builds a `WorkflowDAGResponse` [control-plane/internal/handlers/workflow_dag.go:52-68]() which contains:
- `dag`: A hierarchical tree of `WorkflowDAGNode` objects.
- `timeline`: A flat list of nodes ordered by start time.
- `max_depth`: The deepest level of nested calls found.

```mermaid
sequenceDiagram
    participant UI as Dashboard UI
    participant API as handlers.WorkflowDAGHandler
    participant DB as StorageProvider
    
    UI->>API: GET /api/ui/v1/workflows/:id
    API->>DB: QueryWorkflowExecutions(root_workflow_id)
    DB-->>API: List of WorkflowExecution records
    Note over API: Reconstruct tree using<br/>parent_execution_id
    API-->>UI: WorkflowDAGResponse (JSON)
```
**Diagram: DAG Retrieval Flow**

**Sources:**
- [control-plane/internal/handlers/workflow_dag.go:52-68]()
- [control-plane/internal/handlers/execute.go:44]()

---

## Dashboard Visualization

The frontend uses `@xyflow/react` and `deck.gl` to render the tracked workflows.

### Visualization Components
- **WorkflowDAGViewer**: The primary container for graph rendering [control-plane/web/client/src/components/WorkflowDAG/index.tsx:176-217]().
- **WorkflowDeckGLView**: A high-performance renderer used for large graphs (exceeding performance thresholds) [control-plane/web/client/src/components/WorkflowDAG/DeckGLView.tsx:73-79]().
- **useNodeDetails**: A custom hook that fetches detailed execution metadata (input/output payloads) when a node is selected [control-plane/web/client/src/components/WorkflowDAG/hooks/useNodeDetails.ts:31-115]().

```mermaid
graph LR
    subgraph "Frontend Entities"
        WDV["WorkflowDAGViewer<br/>(WorkflowDAG/index.tsx)"]
        DGL["WorkflowDeckGLView<br/>(WorkflowDAG/DeckGLView.tsx)"]
        UND["useNodeDetails<br/>(hooks/useNodeDetails.ts)"]
    end

    subgraph "Backend Entities"
        DAGH["WorkflowDAGHandler<br/>(handlers/workflow_dag.go)"]
        EXDH["ExecutionDetailsHandler<br/>(handlers/execute.go)"]
    end

    WDV -->|"fetches graph"| DAGH
    WDV --> DGL
    DGL -->|"onNodeClick"| UND
    UND -->|"fetches payloads"| EXDH
```
**Diagram: Frontend-Backend Tracking Integration**

**Sources:**
- [control-plane/web/client/src/components/WorkflowDAG/index.tsx:176-217]()
- [control-plane/web/client/src/components/WorkflowDAG/DeckGLView.tsx:73-79]()
- [control-plane/web/client/src/components/WorkflowDAG/hooks/useNodeDetails.ts:31-115]()

---

## Real-Time Tracking Updates

The control plane maintains an `ExecutionEventBus` [control-plane/internal/handlers/execute.go:46]() to broadcast updates as they happen.

### Event Propagation
When `UpdateExecutionStatusHandler` is called [control-plane/internal/handlers/execute_status_update_test.go:46](), it updates the database and can trigger webhooks if `WebhookRegistered` is true [control-plane/internal/handlers/execute_status_update_test.go:131-187](). This ensures that the UI and external systems stay synchronized with the agent's progress.

**Sources:**
- [control-plane/internal/handlers/execute.go:46]()
- [control-plane/internal/handlers/execute_status_update_test.go:131-187]()
- [control-plane/internal/handlers/workflow_execution_events.go:82]()

---

# Page: Asynchronous Execution

# Asynchronous Execution

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [control-plane/internal/handlers/execute_awaiter_status.go](control-plane/internal/handlers/execute_awaiter_status.go)
- [control-plane/internal/handlers/execute_awaiter_status_test.go](control-plane/internal/handlers/execute_awaiter_status_test.go)
- [examples/ts-node-examples/waiting-state/main.ts](examples/ts-node-examples/waiting-state/main.ts)
- [sdk/python/agentfield/agent.py](sdk/python/agentfield/agent.py)
- [sdk/python/agentfield/async_execution_manager.py](sdk/python/agentfield/async_execution_manager.py)
- [sdk/python/agentfield/client.py](sdk/python/agentfield/client.py)
- [sdk/python/agentfield/exceptions.py](sdk/python/agentfield/exceptions.py)
- [sdk/python/agentfield/execution_state.py](sdk/python/agentfield/execution_state.py)
- [sdk/python/tests/test_agent_call.py](sdk/python/tests/test_agent_call.py)
- [sdk/python/tests/test_agent_coverage_additions.py](sdk/python/tests/test_agent_coverage_additions.py)
- [sdk/python/tests/test_async_config.py](sdk/python/tests/test_async_config.py)
- [sdk/python/tests/test_async_execution.py](sdk/python/tests/test_async_execution.py)
- [sdk/python/tests/test_client_laser_push.py](sdk/python/tests/test_client_laser_push.py)
- [sdk/python/tests/test_execution_state.py](sdk/python/tests/test_execution_state.py)
- [sdk/typescript/src/agent/cancel.ts](sdk/typescript/src/agent/cancel.ts)
- [sdk/typescript/src/agent/pause.ts](sdk/typescript/src/agent/pause.ts)
- [sdk/typescript/tests/agent_async_execution.test.ts](sdk/typescript/tests/agent_async_execution.test.ts)
- [sdk/typescript/tests/agent_pause.test.ts](sdk/typescript/tests/agent_pause.test.ts)
- [sdk/typescript/tests/agent_runtime_paths.test.ts](sdk/typescript/tests/agent_runtime_paths.test.ts)

</details>



## Purpose and Scope

This page describes AgentField's asynchronous execution system, which enables fire-and-forget operations, long-running tasks, and human-in-the-loop approvals. The system supports tasks that may run for minutes, hours, or days with durable state management, automatic retry logic, and cooperative cancellation.

For calling other agents synchronously, see [Cross-Agent Calls](9.2). For tracking execution workflows, see [Workflow Tracking](9.3). For the underlying REST API, see [API Endpoints](6.5).

---

## Execution Architecture

AgentField uses a **submit-and-poll** architecture where execution requests are submitted to the control plane's durable execution gateway, assigned an `execution_id`, and tracked through completion. The SDK polls for status updates with adaptive backoff, while optionally supporting webhook notifications or blocking until a human approval is received via `ctx.pause()`.

**Diagram: Asynchronous Execution Flow**

```mermaid
sequenceDiagram
    participant C as "Agent SDK (Caller)"
    participant CP as "Control Plane<br/>/api/v1/execute/async"
    participant A as "Agent Node (Worker)"
    participant W as "Webhook Endpoint"

    C->>CP: "POST /api/v1/execute/async/{target}"
    Note over C,CP: "input: {...}<br/>headers: X-Run-ID, X-Execution-ID"
    
    CP-->>C: "{ execution_id, status: pending }"
    
    Note over C: "SDK starts AsyncExecutionManager<br/>polling loop with jitter"
    
    CP->>A: "Dispatch to Agent Node"
    A->>A: "run_reasoner_async() task starts"
    
    loop "Polling Loop"
        C->>CP: "GET /api/v1/executions/{execution_id}"
        CP-->>C: "{ status: running }"
        Note over C: "Adaptive backoff based on execution age"
    end
    
    A->>CP: "_post_execution_status(status='succeeded')"
    
    alt "Webhook Configured"
        CP->>W: "POST webhook_url<br/>{ execution_id, result }"
    end
    
    C->>CP: "GET /api/v1/executions/{execution_id}"
    CP-->>C: "{ status: succeeded, result }"
```

**Sources:**
- [sdk/python/agentfield/client.py:574-600]()
- [sdk/python/agentfield/client.py:713-798]()
- [sdk/python/agentfield/async_execution_manager.py:185-197]()
- [sdk/python/agentfield/agent.py:1131-1150]()

---

## AsyncConfig Configuration

Asynchronous behavior is controlled via `AsyncConfig`, which configures polling intervals, connection pooling, and timeout thresholds.

**AsyncConfig Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `initial_poll_interval` | `float` | `0.25` | Starting interval between status checks (seconds) |
| `max_poll_interval` | `float` | `10.0` | Maximum interval between polls after exponential backoff |
| `max_execution_timeout` | `float` | `3600.0` | Total wall-clock time to wait for completion |
| `default_execution_timeout`| `float` | `300.0` | Default timeout for the agent-side reasoner watchdog |
| `enable_result_caching` | `bool` | `True` | Whether to cache terminal results locally |
| `webhook_url` | `str` | `None` | URL for completion notifications |

**Sources:**
- [sdk/python/agentfield/async_config.py:12-45]()
- [sdk/python/agentfield/client.py:163-167]()

---

## Human-in-the-Loop: Pausing and Resuming

A unique feature of AgentField's async execution is the ability to **pause** a reasoner mid-flight to wait for human approval without burning the execution's active timeout budget.

### The Pause Mechanism
When a reasoner calls `ctx.pause()` (TS) or `app.pause()` (Python), the following occurs:
1. The execution status is updated to `waiting` on the control plane.
2. A `PauseClock` is started on the agent node to track time spent waiting [sdk/typescript/src/agent/pause.ts:68-98]().
3. The reasoner logic blocks on a local promise/future in the `PauseManager` [sdk/typescript/src/agent/pause.ts:113-137]().
4. When a human approves via the Control Plane UI, the CP sends a webhook to the agent's `/_internal/webhooks/approval` route, resolving the pause [sdk/typescript/src/agent/pause.ts:106-112]().

**Diagram: Pause and Watchdog Logic**

```mermaid
graph TD
    subgraph "AgentNode"
        R["Reasoner Task"] --> P["ctx.pause()"]
        P --> PC["Start PauseClock"]
        PC --> PM["Register in PauseManager"]
        PM --> Block["Block Reasoner"]
        
        W["Watchdog Loop"] --> Check["Check Active Budget"]
        Check --> Calc["(WallTime - TotalPaused) > Timeout?"]
        Calc -->|"Yes"| Abort["Abort Reasoner"]
        Calc -->|"No"| W
    end

    subgraph "Control Plane"
        H["Human Action"] --> Webhook["POST /_internal/webhooks/approval"]
    end

    Webhook --> PM
    PM --> Resolve["Resolve Reasoner"]
    Resolve --> StopPC["End PauseClock"]
    StopPC --> Resume["Continue Reasoner Logic"]
```

**Sources:**
- [sdk/python/agentfield/agent.py:2260-2300]()
- [sdk/typescript/src/agent/pause.ts:68-98]()
- [sdk/python/tests/test_async_execution.py:96-104]()

---

## Adaptive Polling and Metrics

The `AsyncExecutionManager` (Python) and `AgentFieldClient` manage high-concurrency polling for hundreds of active tasks.

### Polling Strategy
The system uses an age-based adaptive polling interval:
- **New Tasks**: Polled frequently (`fast_poll_interval`) to ensure low latency for quick tasks [sdk/python/agentfield/async_config.py:32-34]().
- **Aging Tasks**: Interval increases as the task stays active, reducing load on the control plane.
- **Jitter**: Every poll interval is multiplied by a random factor (0.8x - 1.2x) to prevent "thundering herd" synchronization [sdk/python/agentfield/client.py:880-882]().

### Metrics Tracking
The `AsyncExecutionManager` tracks performance through `PollingMetrics` and `ExecutionManagerMetrics`, including success rates and average poll durations [sdk/python/agentfield/async_execution_manager.py:99-184]().

**Sources:**
- [sdk/python/agentfield/async_execution_manager.py:185-220]()
- [sdk/python/agentfield/async_config.py:24-35]()

---

## Cooperative Cancellation

Executions can be cancelled from the control plane (e.g., via the dashboard). The Agent Node implements cooperative cancellation using `AbortController` (TS) or `asyncio.Task.cancel` (Python).

1. **Registration**: When an async reasoner starts, its `execution_id` is registered in the `CancelRegistry` [sdk/typescript/src/agent/cancel.ts:33-65]().
2. **Signal Propagation**: The `ctx.signal` (TS) or context is passed to downstream skills or AI calls.
3. **Internal Route**: The control plane notifies the agent via `POST /_internal/executions/:execution_id/cancel` [sdk/typescript/src/agent/cancel.ts:99-134]().
4. **Abort**: The registry triggers `.abort()`, causing any bound `fetch` or SDK calls to reject immediately.

**Sources:**
- [sdk/typescript/src/agent/cancel.ts:9-32]()
- [sdk/typescript/src/agent/cancel.ts:99-134]()

---

## Implementation Details: Python vs TypeScript

### Python SDK
Uses a dedicated `AsyncExecutionManager` class that handles background polling tasks and integrates with a `ResultCache` [sdk/python/agentfield/async_execution_manager.py:185-210](). It provides `execute_async` and `wait_for_execution_result` methods on the `AgentFieldClient` [sdk/python/agentfield/client.py:574-610]().

### TypeScript SDK
Uses a similar pattern but exposes a lower-level `ApprovalClient` for manual polling control in addition to the high-level `ctx.pause()` primitive [examples/ts-node-examples/waiting-state/main.ts:38-42](). It uses Express-based internal routes for webhooks [sdk/typescript/src/agent/pause.ts:1-5]().

**Sources:**
- [sdk/python/agentfield/client.py:574-610]()
- [examples/ts-node-examples/waiting-state/main.ts:149-185]()
- [sdk/typescript/src/agent/cancel.ts:99-134]()

---

## Error Handling and Retries

The system distinguishes between different failure types to prevent infinite retry loops that burn budget:
- **ExecutionFailedError**: The reasoner ran and returned an error. The SDK **skips** sync fallback because re-running will yield the same failure [sdk/python/agentfield/exceptions.py:17-33]().
- **ExecutionTimeoutError**: The wait deadline was hit. Sync fallback is skipped to prevent double-billing for a task that might still be running [sdk/python/agentfield/exceptions.py:74-77]().
- **Transient Errors**: Network failures during polling are retried with exponential backoff [sdk/python/agentfield/async_execution_manager.py:117-131]().

**Sources:**
- [sdk/python/tests/test_agent_call.py:136-178]()
- [sdk/python/agentfield/exceptions.py:80-96]()

---

# Page: AI Integration

# AI Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [control-plane/web/client/package-lock.json](control-plane/web/client/package-lock.json)
- [control-plane/web/client/package.json](control-plane/web/client/package.json)
- [control-plane/web/client/pnpm-lock.yaml](control-plane/web/client/pnpm-lock.yaml)
- [control-plane/web/client/src/components/ui/icon-bridge.tsx](control-plane/web/client/src/components/ui/icon-bridge.tsx)
- [control-plane/web/client/src/components/ui/icon.tsx](control-plane/web/client/src/components/ui/icon.tsx)
- [examples/benchmarks/100k-scale/mastra-bench/package-lock.json](examples/benchmarks/100k-scale/mastra-bench/package-lock.json)
- [examples/benchmarks/100k-scale/mastra-bench/package.json](examples/benchmarks/100k-scale/mastra-bench/package.json)
- [examples/python_agent_nodes/rag_evaluation/ui/package-lock.json](examples/python_agent_nodes/rag_evaluation/ui/package-lock.json)
- [examples/python_agent_nodes/rag_evaluation/ui/package.json](examples/python_agent_nodes/rag_evaluation/ui/package.json)
- [sdk/python/agentfield/agent_ai.py](sdk/python/agentfield/agent_ai.py)
- [sdk/python/agentfield/media_router.py](sdk/python/agentfield/media_router.py)
- [sdk/python/agentfield/vision.py](sdk/python/agentfield/vision.py)
- [sdk/python/tests/test_agent_ai.py](sdk/python/tests/test_agent_ai.py)
- [sdk/python/tests/test_image_config.py](sdk/python/tests/test_image_config.py)
- [sdk/python/tests/test_media_router.py](sdk/python/tests/test_media_router.py)
- [sdk/python/tests/test_strict_openai_schema.py](sdk/python/tests/test_strict_openai_schema.py)
- [sdk/python/tests/test_types.py](sdk/python/tests/test_types.py)
- [sdk/python/uv.lock](sdk/python/uv.lock)
- [sdk/typescript/package-lock.json](sdk/typescript/package-lock.json)

</details>



This page describes how agents connect to Large Language Model (LLM) providers and configure AI-powered operations. AI integration in AgentField enables reasoners to perform text generation, streaming responses, structured output, and embedding generation across multiple providers.

For information about defining reasoners that use AI capabilities, see [Defining Reasoners](#3.2) (Python) and [Reasoners and Skills](#4.2) (TypeScript). For memory-based vector operations that use embeddings, see [Vector Storage](#7.3).

---

## Overview

AgentField provides unified AI integration through two SDK implementations:

- **Python SDK**: Uses `litellm` as the underlying provider abstraction [sdk/python/agentfield/agent_ai.py:30-45]().
- **TypeScript SDK**: Uses Vercel AI SDK (`ai` package) with provider-specific adapters [sdk/typescript/package-lock.json:12-20]().

Both SDKs expose a consistent interface for AI operations while supporting 10+ LLM providers. Configuration is handled through the `AIConfig` type, and AI clients are automatically injected into reasoner execution contexts.

**Architecture Flow:**

```mermaid
graph TB
    Reasoner["Reasoner Function<br/>@app.reasoner()"]
    Context["ReasonerContext<br/>ctx.ai()"]
    AIClient["AIClient<br/>(Python: AgentAI)<br/>(TypeScript: AIClient)"]
    
    subgraph "Provider Layer (via litellm/Vercel AI)"
        OpenAI["OpenAI<br/>gpt-4o"]
        Anthropic["Anthropic<br/>claude-3.5-sonnet"]
        Google["Google<br/>gemini-2.0"]
        Mistral["Mistral<br/>mistral-large"]
        Groq["Groq<br/>llama-3.1"]
        XAI["xAI<br/>grok-2"]
        DeepSeek["DeepSeek<br/>deepseek-reasoner"]
        OpenRouter["OpenRouter<br/>gateway"]
    end
    
    Reasoner -->|"accesses"| Context
    Context -->|"delegates to"| AIClient
    AIClient -->|"routes to"| OpenAI
    AIClient -->|"routes to"| Anthropic
    AIClient -->|"routes to"| Google
    AIClient -->|"routes to"| Mistral
    AIClient -->|"routes to"| Groq
    AIClient -->|"routes to"| XAI
    AIClient -->|"routes to"| DeepSeek
    AIClient -->|"routes to"| OpenRouter
```

**Sources:** [sdk/python/agentfield/agent_ai.py:10-16](), [sdk/typescript/package-lock.json:12-20]()

---

## Supported Providers

AgentField supports a wide range of AI providers. Provider support varies slightly between Python (via `litellm`) and TypeScript (via Vercel AI SDK).

### Provider Comparison Table

| Provider | TypeScript SDK | Python SDK | Text Generation | Embeddings | Notes |
|----------|----------------|------------|-----------------|------------|-------|
| **OpenAI** | ✓ | ✓ | ✓ | ✓ | Default provider [sdk/python/tests/test_agent_ai.py:16]() |
| **Anthropic** | ✓ | ✓ | ✓ | ✗ | Claude models [sdk/typescript/package-lock.json:54]() |
| **Google** | ✓ | ✓ | ✓ | ✓ | Gemini models [sdk/typescript/package-lock.json:148]() |
| **Mistral** | ✓ | ✓ | ✓ | ✓ | [sdk/typescript/package-lock.json:180]() |
| **Groq** | ✓ | ✓ | ✓ | ✗ | [sdk/typescript/package-lock.json:164]() |
| **xAI** | ✓ | ✓ | ✓ | ✗ | Grok models [sdk/typescript/package-lock.json:19]() |
| **DeepSeek** | ✓ | ✓ | ✓ | ✗ | [sdk/typescript/package-lock.json:86]() |
| **Cohere** | ✓ | ✓ | ✓ | ✓ | [sdk/typescript/package-lock.json:70]() |
| **OpenRouter** | ✓ | ✓ | ✓ | ✓ | Gateway [sdk/python/agentfield/vision.py:99]() |
| **Ollama** | ✓ | ✓ | ✓ | ✓ | Local models |

### Provider Logic Mapping

The Python SDK utilizes `AgentAI` to wrap `litellm` calls, providing a safety net for transient errors and timeouts [sdk/python/agentfield/agent_ai.py:169-212]().

```mermaid
graph LR
    AgentAI["AgentAI.ai()"]
    Limiter["StatelessRateLimiter"]
    LiteLLM["litellm.acompletion"]
    
    subgraph "Error Handling"
        Transient["_is_transient_llm_error"]
        Permanent["_PERMANENT_LLM_ERROR_MARKERS"]
    end
    
    AgentAI --> Limiter
    Limiter --> LiteLLM
    LiteLLM --"Error"--> Transient
    Transient --"Retry"--> Limiter
    Transient --"Fail"--> Permanent
```

**Sources:** [sdk/python/agentfield/agent_ai.py:185-212](), [sdk/python/agentfield/agent_ai.py:16-18]()

---

## AI Configuration

AI integration is configured through the `AIConfig` object, which controls model selection, authentication, and generation parameters.

### AIConfig Parameters

| Field | Description | Default (Python) |
|-------|-------------|-----------------|
| `model` | The LLM model string (e.g., `openai/gpt-4o`) | `openai/gpt-4` [sdk/python/tests/test_agent_ai.py:16]() |
| `temperature` | Controls randomness (0.0 to 1.0) | `0.1` [sdk/python/tests/test_agent_ai.py:17]() |
| `max_tokens` | Maximum output tokens | `100` [sdk/python/tests/test_agent_ai.py:18]() |
| `fallback_models` | List of models to try if the primary fails | `[]` [sdk/python/tests/test_agent_ai.py:22]() |
| `enable_rate_limit_retry` | Whether to auto-retry on 429 errors | `True` [sdk/python/tests/test_agent_ai.py:24]() |

### Media Models
Configuration also includes specific models for non-text modalities:
- **Audio**: `audio_model` (e.g., `tts-1`) [sdk/python/tests/test_agent_ai.py:33]()
- **Vision**: `vision_model` (e.g., `dall-e-3`) [sdk/python/tests/test_agent_ai.py:34]()
- **Video**: `video_model` (e.g., `fal-ai/minimax-video`) [sdk/python/tests/test_agent_ai.py:35]()

**Sources:** [sdk/python/tests/test_agent_ai.py:14-36]()

---

## Text Generation

Text generation is the core AI capability, supporting both unstructured text and structured data.

### Text vs. Structured Output
AgentField handles structured output by validating against schemas. In Python, this often uses Pydantic models. The SDK detects if a response is empty even after reasoning content is provided [sdk/python/agentfield/agent_ai.py:92-100]().

### Vision and Image Generation
The `vision.py` module handles image generation via `generate_image_litellm` and `generate_image_openrouter` [sdk/python/agentfield/vision.py:29-108](). OpenRouter integration specifically handles "modalities" to enable image generation through standard chat endpoints [sdk/python/agentfield/vision.py:162-172]().

**Sources:** [sdk/python/agentfield/agent_ai.py:48-64](), [sdk/python/agentfield/vision.py:139-177]()

---

## Embeddings

Embeddings are used for semantic search and memory retrieval.

### Generation
The SDK provides methods to generate embeddings for single strings or batches of text. These are used internally by the memory system to populate vector databases.

### Provider Support
Embedding support is generally limited to providers like OpenAI, Google, and Cohere. The SDK will throw errors if embedding generation is attempted on a text-only provider like Anthropic.

**Sources:** [sdk/python/uv.lock:15](), [sdk/typescript/package-lock.json:13]()

---

## Rate Limiting & Retries

AgentField implements a robust retry mechanism to handle the inherent instability of LLM APIs.

### StatelessRateLimiter
The `StatelessRateLimiter` handles exponential backoff and jitter [sdk/python/agentfield/agent_ai.py:16](). It is used by `AgentAI` to wrap all LLM calls [sdk/python/tests/test_agent_ai.py:106-111]().

### Safety Features
- **Timeout Safety Net**: Retries LLM calls that hit wall-clock timeouts, as these are often stalled connections [sdk/python/agentfield/agent_ai.py:169-182]().
- **HTTP Client Reset**: After a timeout, the SDK resets `litellm` HTTP clients to clear deadlocked connection pools [sdk/python/agentfield/agent_ai.py:103-164]().
- **Error Classification**: Distinguishes between transient errors (retriable) and permanent errors (fail fast) [sdk/python/agentfield/agent_ai.py:185-212]().

**Sources:** [sdk/python/agentfield/agent_ai.py:103-164](), [sdk/python/agentfield/agent_ai.py:185-212](), [sdk/python/tests/test_agent_ai.py:134-139]()

---

# Page: Supported Providers

# Supported Providers

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [control-plane/web/client/package-lock.json](control-plane/web/client/package-lock.json)
- [control-plane/web/client/package.json](control-plane/web/client/package.json)
- [control-plane/web/client/pnpm-lock.yaml](control-plane/web/client/pnpm-lock.yaml)
- [control-plane/web/client/src/components/ui/icon-bridge.tsx](control-plane/web/client/src/components/ui/icon-bridge.tsx)
- [control-plane/web/client/src/components/ui/icon.tsx](control-plane/web/client/src/components/ui/icon.tsx)
- [examples/benchmarks/100k-scale/mastra-bench/package-lock.json](examples/benchmarks/100k-scale/mastra-bench/package-lock.json)
- [examples/benchmarks/100k-scale/mastra-bench/package.json](examples/benchmarks/100k-scale/mastra-bench/package.json)
- [examples/python_agent_nodes/rag_evaluation/ui/package-lock.json](examples/python_agent_nodes/rag_evaluation/ui/package-lock.json)
- [examples/python_agent_nodes/rag_evaluation/ui/package.json](examples/python_agent_nodes/rag_evaluation/ui/package.json)
- [sdk/python/agentfield/agent_ai.py](sdk/python/agentfield/agent_ai.py)
- [sdk/python/agentfield/media_router.py](sdk/python/agentfield/media_router.py)
- [sdk/python/agentfield/vision.py](sdk/python/agentfield/vision.py)
- [sdk/python/tests/test_agent_ai.py](sdk/python/tests/test_agent_ai.py)
- [sdk/python/tests/test_image_config.py](sdk/python/tests/test_image_config.py)
- [sdk/python/tests/test_media_router.py](sdk/python/tests/test_media_router.py)
- [sdk/python/tests/test_strict_openai_schema.py](sdk/python/tests/test_strict_openai_schema.py)
- [sdk/python/tests/test_types.py](sdk/python/tests/test_types.py)
- [sdk/python/uv.lock](sdk/python/uv.lock)
- [sdk/typescript/package-lock.json](sdk/typescript/package-lock.json)

</details>



This page documents the AI/LLM providers that AgentField SDKs support for text generation, embeddings, and multimodal outputs. AgentField provides a unified interface for interacting with multiple providers across its Python and TypeScript SDKs, enabling agents to switch between providers without code changes.

For information about configuring AI models and API keys, see [AI Configuration](#10.2). For text generation patterns, see [Text Generation](#10.3). For embedding generation, see [Embeddings](#10.4).

---

## Provider Support Matrix

AgentField supports 10+ AI providers through a unified interface. The TypeScript SDK uses the Vercel AI SDK ecosystem, while the Python SDK leverages LiteLLM for broad coverage and specialized image generation logic.

| Provider | TypeScript SDK | Python SDK | Text Generation | Embeddings | Image Generation |
|----------|----------------|------------|-----------------|------------|------------------|
| **OpenAI** | ✅ | ✅ | ✅ | ✅ | ✅ (DALL-E) |
| **Anthropic** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Google (Gemini)** | ✅ | ✅ | ✅ | ✅ | ✅ (via OpenRouter) |
| **Mistral** | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Groq** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **xAI (Grok)** | ✅ | ✅ | ✅ | ❌ | ✅ (Grok-Imagine) |
| **DeepSeek** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Cohere** | ✅ | ✅ | ✅ | ✅ | ❌ |
| **OpenRouter** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Ollama** | ✅ | ✅ | ✅ | ✅ | ❌ |

✅ = Fully supported  
❌ = Not supported by provider

**Sources:** [sdk/typescript/package-lock.json:12-20](), [sdk/python/uv.lock:15](), [sdk/python/agentfield/vision.py:7-10]()

---

## TypeScript SDK Provider Architecture

The TypeScript SDK uses the Vercel AI SDK (`ai` package) and provider-specific adapters from the `@ai-sdk/*` ecosystem. Each provider is instantiated through factory functions that return model objects.

### Provider Factory Pattern

```mermaid
graph TB
    subgraph "TypeScript AIClient"
        AIClient["AIClient<br/>(src/ai/AIClient.ts)"]
        buildModel["buildModel()"]
        buildEmbeddingModel["buildEmbeddingModel()"]
    end
    
    subgraph "Vercel AI SDK"
        generateText["generateText()"]
        generateObject["generateObject()"]
        streamText["streamText()"]
        embed["embed()"]
    end
    
    subgraph "Provider Factories"
        createOpenAI["createOpenAI()<br/>@ai-sdk/openai"]
        createAnthropic["createAnthropic()<br/>@ai-sdk/anthropic"]
        createGoogle["createGoogleGenerativeAI()<br/>@ai-sdk/google"]
        createMistral["createMistral()<br/>@ai-sdk/mistral"]
        createGroq["createGroq()<br/>@ai-sdk/groq"]
        createXai["createXai()<br/>@ai-sdk/xai"]
        createDeepSeek["createDeepSeek()<br/>@ai-sdk/deepseek"]
        createCohere["createCohere()<br/>@ai-sdk/cohere"]
    end
    
    AIClient --> buildModel
    AIClient --> buildEmbeddingModel
    
    buildModel --> createOpenAI
    buildModel --> createAnthropic
    buildModel --> createGoogle
    buildModel --> createMistral
    buildModel --> createGroq
    buildModel --> createXai
    buildModel --> createDeepSeek
    buildModel --> createCohere
    
    createOpenAI --> generateText
    createOpenAI --> generateObject
    
    buildEmbeddingModel --> embed
```

**Sources:** [sdk/typescript/package-lock.json:12-20](), [sdk/typescript/package-lock.json:54-211]()

---

## Python SDK Provider Architecture

The Python SDK uses `litellm` as its primary abstraction layer. It includes a sophisticated retry mechanism and lazy loading to keep the memory footprint small.

### LiteLLM Integration & Retries

The Python SDK implements a `StatelessRateLimiter` that wraps `litellm` calls. It specifically handles transient provider glitches (5xx, timeouts) vs permanent client errors (auth, model-not-found).

```mermaid
graph TB
    subgraph "Python AgentAI"
        AgentAI["AgentAI<br/>(agent_ai.py)"]
        get_litellm["_get_litellm()<br/>Lazy Loader"]
        ai_call["ai()"]
    end
    
    subgraph "Error Handling"
        Transient["_is_transient_llm_error()"]
        Permanent["_PERMANENT_LLM_ERROR_MARKERS"]
        Reset["_reset_litellm_http_clients()"]
    end
    
    subgraph "LiteLLM"
        acompletion["litellm.acompletion()"]
        aimage["litellm.aimage_generation()"]
    end

    AgentAI --> ai_call
    ai_call --> get_litellm
    ai_call --> acompletion
    acompletion -- "Timeout/Hang" --> Reset
    acompletion -- "Exception" --> Transient
    Transient -- "True" --> ai_call
```

**Sources:** [sdk/python/agentfield/agent_ai.py:30-45](), [sdk/python/agentfield/agent_ai.py:103-165](), [sdk/python/agentfield/agent_ai.py:185-212]()

---

## Image Generation Providers

AgentField supports specialized image generation through `generate_image_litellm` and `generate_image_openrouter`.

### Supported Vision Providers
- **LiteLLM Path**: Supports OpenAI DALL-E (2/3), Azure DALL-E, and AWS Bedrock Stable Diffusion [sdk/python/agentfield/vision.py:29-54]().
- **OpenRouter Path**: Supports models like `google/gemini-3.1-flash-image-preview` and `x-ai/grok-imagine` by using the chat completions endpoint with `modalities: ["image"]` [sdk/python/agentfield/vision.py:99-172]().

### Implementation Details
The OpenRouter implementation includes a specific retry loop for the `No endpoints found` marker, which is a transient error under high load [sdk/python/agentfield/vision.py:18-25]().

**Sources:** [sdk/python/agentfield/vision.py:29-172](), [sdk/python/agentfield/agent_ai.py:218-220]()

---

## Provider Configuration Details

### OpenAI (Default)
The default provider for both SDKs. In Python, it defaults to `openai/gpt-4` in test stubs [sdk/python/tests/test_agent_ai.py:16](). In production, it supports structured output via Pydantic models [sdk/python/agentfield/agent_ai.py:92-101]().

### Anthropic
Supported for text generation. The Python SDK handles reasoning content metadata specifically for Claude-style models [sdk/python/agentfield/agent_ai.py:48-64]().

### OpenRouter & Ollama
Both are treated as OpenAI-compatible providers.
- **OpenRouter**: Used extensively for multimodal tasks. It requires a specific message format for image+text inputs [sdk/python/agentfield/vision.py:148-159]().
- **Ollama**: Supported via the standard OpenAI-compatible local endpoint (`http://localhost:11434/v1`).

---

## Fallback & Scale Handling

The Python SDK implements a robust fallback system where secondary models can be attempted if the primary model fails.

```mermaid
sequenceDiagram
    participant A as AgentAI
    participant L as LiteLLM
    participant C as Config
    
    A->>C: get_litellm_params()
    C-->>A: Primary Model (e.g. GPT-4)
    A->>L: acompletion(Primary)
    L-->>A: Runtime Error / Failure
    A->>C: fallback_models
    C-->>A: ["gpt-3.5-turbo"]
    A->>L: acompletion(Fallback)
    L-->>A: Success Response
```

**Sources:** [sdk/python/tests/test_agent_ai.py:153-192](), [sdk/python/agentfield/agent_ai.py:83-90]()

---

## Provider Selection Summary

| Feature | Logic Location | Code Entity |
|----------|----------------|-------------|
| **Lazy Loading** | Python SDK | `agentfield.agent_ai._get_litellm` |
| **Image Generation** | Python SDK | `agentfield.vision.generate_image_litellm` |
| **Reasoning Metadata** | Python SDK | `agentfield.agent_ai._get_message_reasoning_content` |
| **Provider Adapters** | TypeScript SDK | `@ai-sdk/*` dependencies in `package-lock.json` |

**Sources:** [sdk/python/agentfield/agent_ai.py:30-35](), [sdk/python/agentfield/vision.py:29-37](), [sdk/typescript/package-lock.json:12-20]()

---

# Page: AI Configuration

# AI Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [sdk/python/agentfield/agent_ai.py](sdk/python/agentfield/agent_ai.py)
- [sdk/python/agentfield/media_router.py](sdk/python/agentfield/media_router.py)
- [sdk/python/agentfield/rate_limiter.py](sdk/python/agentfield/rate_limiter.py)
- [sdk/python/agentfield/vision.py](sdk/python/agentfield/vision.py)
- [sdk/python/tests/test_agent_ai.py](sdk/python/tests/test_agent_ai.py)
- [sdk/python/tests/test_ai_config.py](sdk/python/tests/test_ai_config.py)
- [sdk/python/tests/test_image_config.py](sdk/python/tests/test_image_config.py)
- [sdk/python/tests/test_media_router.py](sdk/python/tests/test_media_router.py)
- [sdk/python/tests/test_strict_openai_schema.py](sdk/python/tests/test_strict_openai_schema.py)
- [sdk/python/tests/test_types.py](sdk/python/tests/test_types.py)
- [sdk/python/uv.lock](sdk/python/uv.lock)
- [sdk/typescript/src/ai/RateLimiter.ts](sdk/typescript/src/ai/RateLimiter.ts)
- [sdk/typescript/src/ai/ToolCalling.ts](sdk/typescript/src/ai/ToolCalling.ts)

</details>



This page documents how to configure AI/LLM provider access in AgentField agents. AI configuration controls which language models your reasoners can access, authentication credentials, and provider-specific options.

For information about the full list of supported providers and their capabilities, see [Supported Providers](10.1). For details on using the configured AI to generate text, see [Text Generation](10.3). For embedding generation, see [Embeddings](10.4).

---

## Overview

AgentField agents use the `AIConfig` class to specify LLM provider credentials and settings. Configuration can be provided through:

- Constructor parameters when creating an `Agent` instance [sdk/python/agentfield/agent.py:356-442]()
- Environment variables (automatic fallback) [sdk/python/agentfield/agent.py:494-502]()
- Runtime updates to the agent's `ai_config` attribute [sdk/python/agentfield/agent_ai.py:106-111]()

The Python SDK uses **litellm** for unified multi-provider access [sdk/python/agentfield/agent_ai.py:30-45](), while the TypeScript SDK uses the **Vercel AI SDK** with provider-specific packages.

**Sources:** [sdk/python/agentfield/agent.py:356-442](), [sdk/python/agentfield/agent_ai.py:1-45](), [sdk/python/uv.lock:5-22]()

---

## Configuration Architecture

### Data Flow and Entity Mapping
The following diagram bridges the high-level configuration concepts to the specific code entities responsible for handling them.

```mermaid
graph TB
    subgraph "Natural Language Space"
        UserConfig["User Configuration"]
        LLMProvider["LLM Provider (OpenAI, Anthropic, etc.)"]
    end

    subgraph "Code Entity Space (Python)"
        direction TB
        PyAgent["Agent Class [agent.py]"]
        PyAIConfig["AIConfig Class [types.py]"]
        PyAgentAI["AgentAI Class [agent_ai.py]"]
        PyRateLimiter["StatelessRateLimiter [rate_limiter.py]"]
        PyLiteLLM["litellm.acompletion"]
        
        PyAgent -->|"has a"| PyAIConfig
        PyAgent -->|"instantiates"| PyAgentAI
        PyAgentAI -->|"uses"| PyAIConfig
        PyAgentAI -->|"calls"| PyRateLimiter
        PyAgentAI -->|"executes"| PyLiteLLM
    end

    subgraph "Code Entity Space (TypeScript)"
        direction TB
        TsAgent["Agent Class [Agent.ts]"]
        TsAIClient["AIClient Class [AIClient.ts]"]
        TsRateLimiter["StatelessRateLimiter [RateLimiter.ts]"]
        TsAISDK["ai.generateText"]
        
        TsAgent -->|"instantiates"| TsAIClient
        TsAIClient -->|"uses"| TsRateLimiter
        TsAIClient -->|"calls"| TsAISDK
    end

    UserConfig --> PyAIConfig
    PyLiteLLM --> LLMProvider
    TsAISDK --> LLMProvider
```

**Sources:** [sdk/python/agentfield/agent.py:356-442](), [sdk/python/agentfield/agent_ai.py:106-161](), [sdk/python/agentfield/rate_limiter.py:18-48](), [sdk/typescript/src/ai/RateLimiter.ts:51-72]()

---

## AIConfig Class Structure

### Python SDK

The Python SDK's `AIConfig` is a Pydantic model defined in `agentfield/types.py`. It includes extensive support for fallback models and rate limiting parameters.

| Field | Type | Description |
|-------|------|-------------|
| `model` | `str` | Primary model identifier (default: `"gpt-4o"`) [sdk/python/tests/test_ai_config.py:37]() |
| `fallback_models` | `List[str]` | Models to try if the primary fails [sdk/python/agentfield/agent_ai.py:382-388]() |
| `temperature` | `float` | Sampling temperature (default: `0.7`) |
| `max_tokens` | `Optional[int]` | Maximum tokens to generate |
| `rate_limit_max_retries` | `int` | Max retries for 429 errors (default: `5`) [sdk/python/tests/test_ai_config.py:19]() |
| `circuit_breaker_threshold` | `int` | Consecutive failures before opening circuit (default: `5`) [sdk/python/tests/test_ai_config.py:23]() |

The `AIConfig` class provides a `get_litellm_params()` method to prepare arguments for the underlying provider call [sdk/python/tests/test_ai_config.py:50-57]().

**Sources:** [sdk/python/agentfield/types.py:11-32](), [sdk/python/agentfield/agent_ai.py:106-161](), [sdk/python/tests/test_ai_config.py:1-40]()

---

## Resilience and Rate Limiting

AgentField implements a `StatelessRateLimiter` designed for distributed environments.

```mermaid
sequenceDiagram
    participant AI as AgentAI/AIClient
    participant RL as StatelessRateLimiter
    participant LLM as Provider API

    AI->>RL: execute_with_retry(func)
    RL->>RL: check_circuit_breaker()
    Note over RL: If circuit open, throw RateLimitError
    loop retry_loop (max_retries)
        RL->>LLM: call provider
        alt Success
            LLM-->>RL: result
            RL->>RL: update_circuit_breaker(success=True)
            RL-->>AI: result
        else Rate Limit Error (429/503)
            LLM-->>RL: error + retry_after
            RL->>RL: calculate_backoff_delay()
            Note over RL: uses container_seed + jitter
            RL->>RL: sleep(delay)
        else Permanent Error
            LLM-->>RL: error
            RL->>RL: update_circuit_breaker(success=False)
            RL-->>AI: throw Exception
        end
    end
```

**Sources:** [sdk/python/agentfield/rate_limiter.py:18-210](), [sdk/typescript/src/ai/RateLimiter.ts:51-230]()

### Key Resilience Features
1.  **Adaptive Backoff**: Uses exponential backoff with jitter based on a `_container_seed` (derived from hostname and PID) to prevent "thundering herd" problems [sdk/python/agentfield/rate_limiter.py:49-53]().
2.  **Circuit Breaker**: Automatically stops requests to a provider if the failure threshold is reached, protecting both the agent and the provider [sdk/python/agentfield/rate_limiter.py:163-206]().
3.  **Fallback Chains**: The Python SDK automatically cycles through `fallback_models` if the primary model returns a transient error [sdk/python/agentfield/agent_ai.py:382-388]().
4.  **LiteLLM Reset**: Defensive cleanup of cached HTTP clients after timeouts to prevent deadlocks [sdk/python/agentfield/agent_ai.py:103-161]().

---

## Multi-Modal Configuration

### Vision and Image Generation
Image generation is routed through `MediaRouter` which dispatches to specific providers based on model prefixes [sdk/python/agentfield/media_router.py:1-20]().

- **LiteLLM Path**: Supports DALL-E, Azure, and Bedrock via `generate_image_litellm` [sdk/python/agentfield/vision.py:29-62]().
- **OpenRouter Path**: Uses chat completions with `modalities=["image"]` to support models like Gemini 3.1 Flash Image [sdk/python/agentfield/vision.py:99-172]().
- **Special Handling**: Includes retries for OpenRouter's "No endpoints found" 404 error [sdk/python/agentfield/vision.py:181-200]().

**Sources:** [sdk/python/agentfield/vision.py:1-172](), [sdk/python/agentfield/media_router.py:1-20]()

### Tool Calling Configuration
The TypeScript SDK provides a `ToolCallConfig` for fine-grained control over how capabilities are presented to the LLM.

| Field | Default | Description |
|-------|---------|-------------|
| `maxTurns` | `10` | Max LLM turns in a tool-call loop [sdk/typescript/src/ai/ToolCalling.ts:45]() |
| `maxToolCalls` | `25` | Max total tool calls allowed [sdk/typescript/src/ai/ToolCalling.ts:46]() |
| `schemaHydration` | `"eager"` | `"eager"` (full schemas) or `"lazy"` (metadata first) [sdk/typescript/src/ai/ToolCalling.ts:34]() |

**Sources:** [sdk/typescript/src/ai/ToolCalling.ts:24-48]()

---

## Configuration Patterns

### OpenRouter Attribution
When using OpenRouter models, the SDK automatically injects attribution headers to identify the application.

```python
# Automatic attribution for OpenRouter
params = AIConfig(model="openrouter/openai/gpt-4o").get_litellm_params()
# Results in headers:
# "HTTP-Referer": "https://agentfield.ai"
# "X-OpenRouter-Title": "AgentField AI"
```

**Sources:** [sdk/python/tests/test_ai_config.py:59-72]()

### Strict Schema Enforcement
For OpenAI models, the SDK provides `_strictify_openai_schema` to ensure Pydantic models are converted to OpenAI's "Strict Mode" requirements (e.g., `additionalProperties: false` and all fields in `required`) [sdk/python/tests/test_strict_openai_schema.py:1-10]().

**Sources:** [sdk/python/agentfield/agent_ai.py:15-18](), [sdk/python/tests/test_strict_openai_schema.py:1-60]()

---

# Page: Text Generation

# Text Generation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [sdk/go/ai/README.md](sdk/go/ai/README.md)
- [sdk/go/ai/client.go](sdk/go/ai/client.go)
- [sdk/go/ai/client_test.go](sdk/go/ai/client_test.go)
- [sdk/go/ai/config.go](sdk/go/ai/config.go)
- [sdk/go/ai/model_params.go](sdk/go/ai/model_params.go)
- [sdk/go/ai/model_params_test.go](sdk/go/ai/model_params_test.go)
- [sdk/go/ai/multimodal.go](sdk/go/ai/multimodal.go)
- [sdk/go/ai/multimodal_test.go](sdk/go/ai/multimodal_test.go)
- [sdk/go/ai/request.go](sdk/go/ai/request.go)
- [sdk/go/ai/request_test.go](sdk/go/ai/request_test.go)
- [sdk/go/ai/response.go](sdk/go/ai/response.go)
- [sdk/go/ai/response_test.go](sdk/go/ai/response_test.go)
- [sdk/python/agentfield/agent_ai.py](sdk/python/agentfield/agent_ai.py)
- [sdk/python/agentfield/agent_utils.py](sdk/python/agentfield/agent_utils.py)
- [sdk/python/agentfield/media_router.py](sdk/python/agentfield/media_router.py)
- [sdk/python/agentfield/multimodal.py](sdk/python/agentfield/multimodal.py)
- [sdk/python/agentfield/vision.py](sdk/python/agentfield/vision.py)
- [sdk/python/tests/test_agent_ai.py](sdk/python/tests/test_agent_ai.py)
- [sdk/python/tests/test_image_config.py](sdk/python/tests/test_image_config.py)
- [sdk/python/tests/test_media_router.py](sdk/python/tests/test_media_router.py)
- [sdk/python/tests/test_strict_openai_schema.py](sdk/python/tests/test_strict_openai_schema.py)
- [sdk/python/tests/test_types.py](sdk/python/tests/test_types.py)
- [sdk/python/uv.lock](sdk/python/uv.lock)

</details>



## Purpose and Scope

This document covers text generation capabilities in AgentField agents using Large Language Models (LLMs). Text generation enables reasoners to produce natural language responses, structured data, and multimodal outputs (audio/video/image) by interfacing with various AI providers.

For configuration of AI providers and API keys, see [AI Configuration](10.2). For generating embeddings instead of text, see [Embeddings](10.4). For the full list of supported providers, see [Supported Providers](10.1).

**Sources:** [sdk/python/agentfield/agent_ai.py:1-25](), [sdk/go/ai/client.go:1-13]()

---

## Architecture Overview

```mermaid
graph TB
    subgraph "Agent Runtime"
        Reasoner["@app.reasoner() or agent.reasoner()"]
        Context["ReasonerContext (TS) / ExecutionContext (Python)"]
    end
    
    subgraph "AI Layer"
        AIClient_TS["AIClient (TypeScript)"]
        AgentAI_Py["AgentAI Handler (Python)"]
        AIClient_Go["ai.Client (Go)"]
    end
    
    subgraph "Provider Abstraction"
        AI_SDK["ai-sdk (TypeScript)"]
        LiteLLM["litellm (Python)"]
        Internal_Go["Internal SSE/HTTP (Go)"]
    end
    
    subgraph "AI Providers"
        OpenAI["OpenAI"]
        Anthropic["Anthropic"]
        OpenRouter["OpenRouter"]
        Others["Google, Mistral, Groq, xAI, etc."]
    end
    
    Reasoner -->|ctx.ai() or app.ai()| Context
    Context -->|TypeScript| AIClient_TS
    Context -->|Python| AgentAI_Py
    Context -->|Go| AIClient_Go
    
    AIClient_TS --> AI_SDK
    AgentAI_Py --> LiteLLM
    AIClient_Go --> Internal_Go
    
    AI_SDK --> OpenAI
    LiteLLM --> OpenAI
    Internal_Go --> OpenAI
```

**Title:** Text Generation Architecture in AgentField

AgentField provides unified text generation across Python, TypeScript, and Go SDKs. The Python SDK uses `litellm` [sdk/python/agentfield/agent_ai.py:30-45](), while the Go SDK implements a native HTTP client with Server-Sent Events (SSE) support for streaming [sdk/go/ai/client.go:14-17]().

**Sources:** [sdk/python/agentfield/agent_ai.py:30-45](), [sdk/go/ai/client.go:14-35](), [sdk/go/ai/client.go:248-261]()

---

## Basic Text Generation

### Python Implementation
Python reasoners access AI through the `AgentAI` class, which handles model selection, retries, and multimodal detection.

```python
# Simple text generation
@app.reasoner()
async def summarize(text: str) -> dict:
    result = await app.ai(
        prompt=f"Summarize this: {text}",
        system="You are a helpful assistant"
    )
    return {"summary": result.text}
```

The `AgentAI.ai()` method wraps the underlying provider calls with a `StatelessRateLimiter` [sdk/python/agentfield/agent_ai.py:100-111]().

**Sources:** [sdk/python/agentfield/agent_ai.py:131-150](), [sdk/python/agentfield/agent_ai.py:97-111]()

### Go Implementation
The Go SDK provides a `Client` that supports both standard and streaming completions.

```go
// Go completion example
client, _ := ai.NewClient(nil)
resp, err := client.Complete(ctx, "Summarize this document", ai.WithModel("gpt-4o"))
fmt.Println(resp.Text())
```

The Go `Client.Complete` method builds a `Request` and executes it via `doRequest` [sdk/go/ai/client.go:38-63]().

**Sources:** [sdk/go/ai/client.go:38-63](), [sdk/go/ai/request.go:15-43]()

---

## Structured Output and Schemas

### Pydantic (Python)
Python uses Pydantic models for structured output. The SDK includes a `_strictify_openai_schema` utility to ensure compatibility with OpenAI's strict mode by setting `additionalProperties: false` and requiring all fields [sdk/python/agentfield/agent_ai.py:26-27]().

```python
from pydantic import BaseModel

class Analysis(BaseModel):
    sentiment: str
    score: float

result = await app.ai("Analyze this", response_model=Analysis)
```

**Sources:** [sdk/python/tests/test_strict_openai_schema.py:1-9](), [sdk/python/agentfield/agent_ai.py:92-101]()

### Go Request Rewriting
The Go SDK automatically rewrites `max_tokens` to `max_completion_tokens` for newer OpenAI models (gpt-4o, o1 series) when targeting "vouched" endpoints like `api.openai.com` or `openrouter.ai` [sdk/go/ai/model_params.go:9-17]().

**Sources:** [sdk/go/ai/model_params.go:49-56](), [sdk/go/ai/model_params.go:88-102]()

---

## Multimodal Generation

AgentField supports images, audio, and video as part of the text generation flow.

### Image Generation (Python)
The `vision.py` module handles image generation via `litellm` (DALL-E) or `OpenRouter` (Gemini/Grok) [sdk/python/agentfield/vision.py:1-10]().

| Provider | Method | Supported Modalities |
|----------|--------|----------------------|
| LiteLLM | `aimage_generation` | Image (DALL-E 3, etc.) |
| OpenRouter | `acompletion` | Image via chat modalities |

**Sources:** [sdk/python/agentfield/vision.py:29-37](), [sdk/python/agentfield/vision.py:99-108]()

### Multimodal Inputs (Go)
The Go SDK uses functional options to attach media to requests:

```go
// Attaching audio in Go
req, _ := ai.Complete(ctx, "What is in this audio?", 
    ai.WithAudioFile("path/to/audio.mp3", "mp3"))
```

**Sources:** [sdk/go/ai/multimodal.go:39-65](), [sdk/go/ai/multimodal.go:125-151]()

---

## Streaming Responses

### Go SSE Decoder
The Go SDK implements a custom `SSEDecoder` to handle `text/event-stream` responses [sdk/go/ai/client.go:249-261](). It splits the stream on double-newlines and parses the `data:` chunks into `StreamChunk` objects.

```mermaid
sequenceDiagram
    participant App
    participant Client as ai.Client
    participant Decoder as SSEDecoder
    participant API as AI Provider
    
    App->>Client: StreamComplete(prompt)
    Client->>API: POST /chat/completions (stream:true)
    API-->>Client: HTTP Response (Body Stream)
    Client->>Decoder: NewSSEDecoder(Body)
    loop until EOF
        Decoder->>Decoder: Read buffer
        Decoder->>Decoder: Decode "data:" prefix
        Decoder-->>App: Send StreamChunk to channel
    end
```

**Title:** Go SDK Streaming Flow

**Sources:** [sdk/go/ai/client.go:146-184](), [sdk/go/ai/client.go:264-280]()

---

## Rate Limiting and Safety

### Python Rate Limiter
The Python SDK utilizes a `StatelessRateLimiter` to handle `429 Too Many Requests` errors with exponential backoff and jitter [sdk/python/agentfield/agent_ai.py:16-18]().

**Sources:** [sdk/python/agentfield/agent_ai.py:16-18](), [sdk/python/tests/test_agent_ai.py:97-111]()

### Go Timeout and Retries
The Go `Client` is initialized with a configurable `http.Client` timeout [sdk/go/ai/client.go:31-34](). It checks for transient errors and returns them via an error channel in streaming mode or a standard error in blocking mode [sdk/go/ai/client.go:127-133]().

**Sources:** [sdk/go/ai/client.go:31-34](), [sdk/go/ai/client.go:127-133]()

---

## Model Selection Logic

AgentField uses a "deny-list" approach for model parameters to avoid going stale. For example, in Go, `needsMaxCompletionTokens` returns true for any model that is NOT in the legacy `gpt-3.5` or `gpt-4` (original) families [sdk/go/ai/model_params.go:20-32]().

**Sources:** [sdk/go/ai/model_params.go:20-47](), [sdk/go/ai/model_params_test.go:13-74]()

---

# Page: Embeddings

# Embeddings

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [sdk/go/ai/README.md](sdk/go/ai/README.md)
- [sdk/go/ai/client.go](sdk/go/ai/client.go)
- [sdk/go/ai/client_test.go](sdk/go/ai/client_test.go)
- [sdk/go/ai/config.go](sdk/go/ai/config.go)
- [sdk/go/ai/model_params.go](sdk/go/ai/model_params.go)
- [sdk/go/ai/model_params_test.go](sdk/go/ai/model_params_test.go)
- [sdk/go/ai/multimodal.go](sdk/go/ai/multimodal.go)
- [sdk/go/ai/multimodal_test.go](sdk/go/ai/multimodal_test.go)
- [sdk/go/ai/request.go](sdk/go/ai/request.go)
- [sdk/go/ai/request_test.go](sdk/go/ai/request_test.go)
- [sdk/go/ai/response.go](sdk/go/ai/response.go)
- [sdk/go/ai/response_test.go](sdk/go/ai/response_test.go)
- [sdk/python/agentfield/agent_ai.py](sdk/python/agentfield/agent_ai.py)
- [sdk/python/agentfield/agent_utils.py](sdk/python/agentfield/agent_utils.py)
- [sdk/python/agentfield/media_router.py](sdk/python/agentfield/media_router.py)
- [sdk/python/agentfield/multimodal.py](sdk/python/agentfield/multimodal.py)
- [sdk/python/agentfield/vision.py](sdk/python/agentfield/vision.py)
- [sdk/python/tests/test_agent_ai.py](sdk/python/tests/test_agent_ai.py)
- [sdk/python/tests/test_image_config.py](sdk/python/tests/test_image_config.py)
- [sdk/python/tests/test_media_router.py](sdk/python/tests/test_media_router.py)
- [sdk/python/tests/test_strict_openai_schema.py](sdk/python/tests/test_strict_openai_schema.py)
- [sdk/python/tests/test_types.py](sdk/python/tests/test_types.py)
- [sdk/python/uv.lock](sdk/python/uv.lock)

</details>



## Purpose and Scope

This document describes how to generate text embeddings in AgentField and integrate them with the vector storage system for semantic search and retrieval-augmented generation (RAG) applications. Embeddings are numerical vector representations of text that enable similarity-based operations in memory scopes.

The AgentField system abstracts embedding generation through the `AIClient` (TypeScript) and `AgentAI` (Python) components, providing a unified interface across multiple providers like OpenAI, Google, and Mistral.

---

## Embedding Generation Architecture

Embedding generation flows from the high-level Agent SDKs through provider-specific drivers. In the Python SDK, `AgentAI` handles the coordination of AI tasks, while in TypeScript, `AIClient` manages the direct interaction with LLM providers.

### AI Space to Code Entity Space: Embedding Flow

The following diagram maps the conceptual "Natural Language Space" (where text resides) to the "Code Entity Space" (where vectors are computed and stored).

```mermaid
graph TD
    subgraph "Natural Language Space"
        UserText["User Text / Document Chunk"]
        SearchQuery["Search Query"]
    end

    subgraph "Code Entity Space (SDK)"
        direction TB
        AgentAI_Py["Python: AgentAI.ai() / embed()"]
        AIClient_TS["TypeScript: AIClient.embed()"]
        MemoryInterface["MemoryInterface.embedAndSet()"]
    end

    subgraph "Infrastructure & Providers"
        LiteLLM["LiteLLM (Python Driver)"]
        VercelAI["Vercel AI SDK (TS Driver)"]
        ControlPlane["Control Plane (Vector Store)"]
    end

    UserText --> MemoryInterface
    MemoryInterface --> AgentAI_Py
    MemoryInterface --> AIClient_TS
    
    AgentAI_Py --> LiteLLM
    AIClient_TS --> VercelAI
    
    LiteLLM --> OpenAI["OpenAI / Google / Mistral"]
    VercelAI --> OpenAI
    
    MemoryInterface --> ControlPlane
    OpenAI -- "Vector [0.12, -0.05, ...]" --> MemoryInterface
```

**Sources:** [sdk/python/agentfield/agent_ai.py:10-18](), [sdk/python/agentfield/agent_ai.py:131-150](), [sdk/python/uv.lock:15-22]()

---

## TypeScript SDK Embedding Methods

The TypeScript SDK's `AIClient` class provides two primary methods for generating embeddings, abstracting the underlying provider logic.

### AIClient Embedding Methods

```mermaid
graph LR
    AIClient["AIClient"]
    embed["embed(value, options)"]
    embedMany["embedMany(values, options)"]
    
    OpenAI["OpenAI Provider"]
    Google["Google Provider"]
    Mistral["Mistral Provider"]
    Cohere["Cohere Provider"]
    
    AIClient --> embed
    AIClient --> embedMany
    
    embed --> OpenAI
    embed --> Google
    embed --> Mistral
    embed --> Cohere
    
    embedMany --> OpenAI
    embedMany --> Google
    embedMany --> Mistral
    embedMany --> Cohere
```

#### Single Text Embedding
The `embed()` method generates an embedding vector for a single text string. It returns a numeric array representing the embedding vector.

#### Batch Embeddings
The `embedMany()` method generates embeddings for multiple texts in a single request. Batch processing is significantly more efficient for large document collections or ingestion pipelines.

---

## Provider Support and Detection

AgentField supports a wide range of embedding providers. Support is validated at runtime to ensure the selected model and provider are capable of embedding tasks.

### Supported Providers Table

| Provider | Embedding Support | Method Used |
|----------|------------------|-------------|
| OpenAI | ✅ Yes | `embedding()` |
| Google | ✅ Yes | `textEmbeddingModel()` |
| Mistral | ✅ Yes | `textEmbeddingModel()` |
| Cohere | ✅ Yes | `textEmbeddingModel()` |
| OpenRouter | ✅ Yes | OpenAI-compatible `embedding()` |
| Ollama | ✅ Yes | OpenAI-compatible `embedding()` |
| Anthropic | ❌ No | N/A (Text Generation Only) |
| DeepSeek | ❌ No | N/A (Text Generation Only) |

### Provider Error Handling

The system performs defensive checks before calling provider APIs. For example, in the Python SDK, `_is_transient_llm_error` is used to distinguish between temporary network glitches and permanent configuration errors (like using a non-embedding model for embedding tasks).

```mermaid
graph TD
    Call["Request: embed()"]
    CheckSupport{"Provider supports<br/>Embeddings?"}
    ThrowError["Throw Error:<br/>'Provider not supported'"]
    Exec["Execute via LiteLLM / AI SDK"]
    
    Call --> CheckSupport
    CheckSupport -->|No| ThrowError
    CheckSupport -->|Yes| Exec
    
    Exec --> Success["Return Vector"]
    Exec --> Error{"Error Type?"}
    Error -->|Transient| Retry["Retry with backoff"]
    Error -->|Permanent| Fail["Raise Exception"]
```

**Sources:** [sdk/python/agentfield/agent_ai.py:185-212](), [sdk/python/agentfield/agent_ai.py:214-230]()

---

## Vector Storage Integration

Embeddings are rarely used in isolation; they are typically stored in the system's memory for later retrieval. The `MemoryInterface` provides high-level methods that combine embedding generation with vector storage operations.

### MemoryInterface Operations

1.  **`embedText(text, options)`**: Generates an embedding for a single text string using the configured `AIClient`.
2.  **`embedTexts(texts, options)`**: Generates embeddings for multiple texts.
3.  **`embedAndSet(key, text, metadata, scope, scopeId)`**: A convenience method that generates an embedding and immediately persists it to the Control Plane's vector store.

### Storing and Searching Embeddings

The following sequence diagram illustrates the interaction between the Agent, the AI Provider, and the Control Plane during a RAG ingestion and retrieval flow.

```mermaid
sequenceDiagram
    participant Agent as "Agent Reasoner"
    participant MemInterface as "MemoryInterface"
    participant AgentAI as "AgentAI / AIClient"
    participant ControlPlane as "Control Plane"
    
    Note over Agent,ControlPlane: Storage Phase (Ingestion)
    Agent->>MemInterface: embedAndSet(key, text, meta)
    MemInterface->>AgentAI: embed(text)
    AgentAI->>AIProvider: Request Embedding
    AIProvider-->>AgentAI: Vector [0.1, 0.5, ...]
    AgentAI-->>MemInterface: Vector
    MemInterface->>ControlPlane: POST /api/v1/memory/vector/set
    
    Note over Agent,ControlPlane: Retrieval Phase (Query)
    Agent->>MemInterface: embedText(query)
    MemInterface->>AgentAI: embed(query)
    AgentAI-->>MemInterface: QueryVector
    Agent->>MemInterface: searchVector(QueryVector)
    MemInterface->>ControlPlane: POST /api/v1/memory/vector/search
    ControlPlane-->>MemInterface: [{key, score, metadata}]
    MemInterface-->>Agent: Relevant Context
```

**Sources:** [sdk/python/agentfield/agent_ai.py:131-150](), [sdk/python/agentfield/agent_ai.py:106-111]()

---

## Configuration and Reliability

### Model Selection
Embedding models are configured via the `AIConfig` object. While text generation might use `gpt-4o`, embeddings typically use specialized models like `text-embedding-3-small` or `text-embedding-3-large`.

### Rate Limiting and Retries
Embedding generation is subject to provider rate limits. AgentField uses a `StatelessRateLimiter` to handle `429 Too Many Requests` errors with exponential backoff and jitter.

*   **`rate_limit_max_retries`**: Number of times to retry a failed embedding call.
*   **`rate_limit_base_delay`**: Initial delay between retries.
*   **`rate_limit_circuit_breaker_threshold`**: Number of consecutive failures before tripping the circuit breaker to prevent cascading failures.

**Sources:** [sdk/python/agentfield/agent_ai.py:16-17](), [sdk/python/agentfield/agent_ai.py:97-111](), [sdk/python/agentfield/agent_ai.py:169-182]()

### Timeout Management
To prevent hanging execution, embedding calls have a safety-net timeout. If a call stalls, the `_reset_litellm_http_clients` function is triggered to clear cached connection pools and force a fresh connection on the next attempt.

**Sources:** [sdk/python/agentfield/agent_ai.py:103-164]()

---

# Page: Rate Limiting & Retries

# Rate Limiting & Retries

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [sdk/python/agentfield/agent_ai.py](sdk/python/agentfield/agent_ai.py)
- [sdk/python/agentfield/media_router.py](sdk/python/agentfield/media_router.py)
- [sdk/python/agentfield/rate_limiter.py](sdk/python/agentfield/rate_limiter.py)
- [sdk/python/agentfield/vision.py](sdk/python/agentfield/vision.py)
- [sdk/python/tests/test_agent_ai.py](sdk/python/tests/test_agent_ai.py)
- [sdk/python/tests/test_ai_config.py](sdk/python/tests/test_ai_config.py)
- [sdk/python/tests/test_image_config.py](sdk/python/tests/test_image_config.py)
- [sdk/python/tests/test_media_router.py](sdk/python/tests/test_media_router.py)
- [sdk/python/tests/test_strict_openai_schema.py](sdk/python/tests/test_strict_openai_schema.py)
- [sdk/python/tests/test_types.py](sdk/python/tests/test_types.py)
- [sdk/python/uv.lock](sdk/python/uv.lock)
- [sdk/typescript/src/ai/RateLimiter.ts](sdk/typescript/src/ai/RateLimiter.ts)
- [sdk/typescript/src/ai/ToolCalling.ts](sdk/typescript/src/ai/ToolCalling.ts)

</details>



## Purpose & Scope

This document covers the automatic rate limiting and retry mechanisms built into AgentField's AI integration layer. When AI provider APIs return rate limit errors (typically HTTP 429 status codes), the SDK automatically retries requests using exponential backoff with jitter and circuit breaker patterns. This functionality is implemented via the `StatelessRateLimiter` class and applies to text generation, structured outputs, and embeddings across both Python and TypeScript SDKs.

For information about configuring AI providers and models, see [AI Configuration](#10.2). For details on text generation and embedding operations, see [Text Generation](#10.3) and [Embeddings](#10.4).

---

## Architecture Overview

### Rate Limiting Flow

```mermaid
graph TB
    subgraph "Agent Logic"
        Reasoner["Reasoner/Skill Code"]
    end

    subgraph "SDK Core (agentfield)"
        AgentAI["AgentAI (Python) / AIClient (TS)"]
        RateLimiter["StatelessRateLimiter"]
    end

    subgraph "External"
        LiteLLM["LiteLLM / Provider Client"]
        Provider["AI Provider API<br/>(OpenAI, Anthropic, etc)"]
    end
    
    Reasoner -->|"ai() / generate()"| AgentAI
    AgentAI -->|"execute_with_retry()"| RateLimiter
    RateLimiter -->|"acompletion()"| LiteLLM
    LiteLLM -->|"HTTP Request"| Provider
    Provider -->|"429 Rate Limit"| LiteLLM
    LiteLLM --X|"Exception"| RateLimiter
    RateLimiter -->|"Exponential Backoff<br/>+ Jitter"| LiteLLM
    LiteLLM -->|"200 Success"| RateLimiter
    RateLimiter -->|"Response"| AgentAI
    AgentAI -->|"Result"| Reasoner
```

**Sources:** [sdk/python/agentfield/agent_ai.py:330-360](), [sdk/python/agentfield/rate_limiter.py:18-48](), [sdk/typescript/src/ai/RateLimiter.ts:51-72]()

### Code Entity Mapping

| System Name | Python Entity | TypeScript Entity | Role |
| :--- | :--- | :--- | :--- |
| **Rate Limiter** | `StatelessRateLimiter` | `StatelessRateLimiter` | Handles backoff, jitter, and circuit breaking. |
| **Retry Wrapper** | `execute_with_retry` | `executeWithRetry` | Orchestrates the try/catch loop for API calls. |
| **Error Detection** | `_is_rate_limit_error` | `_isRateLimitError` | Identifies 429/503 status codes and specific error strings. |
| **Delay Logic** | `_calculate_backoff_delay` | `_calculateBackoffDelay` | Implements exponential growth with container-seeded jitter. |

**Sources:** [sdk/python/agentfield/rate_limiter.py:18-212](), [sdk/typescript/src/ai/RateLimiter.ts:51-231]()

---

## Configuration Options

Rate limiting behavior is configured through the `AIConfig` object. In Python, these defaults are established in `AIConfig` and used to initialize the `StatelessRateLimiter` within `AgentAI`.

### Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable_rate_limit_retry` | `bool` | `True` | Master switch to enable/disable automatic retries. |
| `rate_limit_max_retries` | `int` | `5` | Maximum number of retry attempts before failing. |
| `rate_limit_base_delay` | `float` | `0.5` | Initial delay in seconds for first retry. |
| `rate_limit_max_delay` | `float` | `30.0` | Maximum delay in seconds (capped). |
| `rate_limit_jitter_factor` | `float` | `0.25` | Random variance factor (±25%) to prevent thundering herd. |
| `rate_limit_circuit_breaker_threshold` | `int` | `5` | Failures before opening circuit. |
| `rate_limit_circuit_breaker_timeout` | `int` | `30` | Seconds to keep circuit open. |

**Sources:** [sdk/python/agentfield/types.py:30-45](), [sdk/python/tests/test_ai_config.py:18-24]()

---

## Exponential Backoff & Jitter

### Delay Calculation

The delay increases exponentially but is modified by a **container-specific seed**. This ensures that while a single container retries consistently, different containers (even on the same host) will naturally distribute their load over time.

```python
# Delay logic in Python
base_delay = min(self.base_delay * (2**attempt), self.max_delay)
random.seed(self._container_seed + attempt)
jitter = random.uniform(-jitter_range, jitter_range)
delay = max(0.1, base_delay + jitter)
```

**Sources:** [sdk/python/agentfield/rate_limiter.py:142-161](), [sdk/typescript/src/ai/RateLimiter.ts:180-194]()

### Container-Specific Jitter

To prevent the "thundering herd" problem where multiple agents retry at the exact same millisecond, AgentField generates a seed based on the environment:
- **Python**: Uses `HOSTNAME` and `os.getpid()`. [sdk/python/agentfield/rate_limiter.py:49-53]()
- **TypeScript**: Uses `os.hostname()` and `process.pid`. [sdk/typescript/src/ai/RateLimiter.ts:74-78]()

---

## Circuit Breaker Pattern

The circuit breaker prevents cascading failures. If an AI provider is consistently returning 429s, the SDK "opens" the circuit to fail fast, saving compute resources and avoiding further provider penalties.

```mermaid
stateDiagram-v2
    [*] --> Closed
    Closed --> Open: failures >= threshold
    Open --> HalfOpen: timeout expires
    HalfOpen --> Closed: success
    HalfOpen --> Open: failure
    
    note right of Open
        Returns RateLimitError immediately
        without calling the provider API.
    end note
```

**Sources:** [sdk/python/agentfield/rate_limiter.py:163-212](), [sdk/typescript/src/ai/RateLimiter.ts:196-221]()

---

## Specialized Retry Logic

### LLM Timeout & Client Resets
In `agent_ai.py`, AgentField implements a defensive reset for `litellm`'s HTTP clients. If a call hangs and hits a wall-clock timeout, the SDK cancels the task and clears `litellm`'s internal connection pool to prevent deadlocks on half-closed sockets.

- **Timeout Retries**: Defaults to 2 retries for wall-clock timeouts. [sdk/python/agentfield/agent_ai.py:169-182]()
- **Client Purge**: The function `_reset_litellm_http_clients` clears module-level caches in `litellm`. [sdk/python/agentfield/agent_ai.py:103-165]()

### Transient vs. Permanent Errors
The SDK distinguishes between errors that should be retried and those that should fail immediately:

| Error Type | Logic | Markers |
| :--- | :--- | :--- |
| **Transient** | Retry via RateLimiter | `overloaded`, `service unavailable`, `bad gateway`, `connection`, `econnreset` |
| **Permanent** | Fail Immediately | `invalid_request_error`, `authentication`, `no such model`, `context_length` |

**Sources:** [sdk/python/agentfield/agent_ai.py:185-212]()

### OpenRouter "No Endpoints" Retry
Specific logic exists for OpenRouter's transient "No endpoints found" 404 error. The SDK performs up to 3 attempts with inter-sleeps before optionally stripping the `image_config` to maximize compatibility.

**Sources:** [sdk/python/agentfield/vision.py:18-25](), [sdk/python/agentfield/vision.py:187-200]()

---

## Implementation Example (Python)

```python
# The AgentAI class uses the limiter to wrap provider calls
async def _execute_with_retry(self, func, **kwargs):
    if not self.agent.ai_config.enable_rate_limit_retry:
        return await func()
    
    limiter = self._get_rate_limiter()
    return await limiter.execute_with_retry(func)
```

**Sources:** [sdk/python/agentfield/agent_ai.py:330-340](), [sdk/python/tests/test_agent_ai.py:194-212]()

---

## Best Practices

1. **Keep Defaults for Production**: The default theoretical max wait is under 3 minutes, which is optimal for balancing resilience and responsiveness. [sdk/python/tests/test_ai_config.py:27-31]()
2. **Use Structured Outputs with Caution**: If a model provides `reasoning_content` but an empty structured result, the SDK raises `_EmptyReasoningStructuredOutput` to trigger a retry, as this is often a model glitch. [sdk/python/agentfield/agent_ai.py:92-101]()
3. **Monitor Circuit States**: If your agent logs "Circuit breaker opened", it indicates your provider tier is insufficient for the current load. [sdk/python/agentfield/rate_limiter.py:200-207]()

**Sources:** [sdk/python/agentfield/agent_ai.py:1-400](), [sdk/python/agentfield/rate_limiter.py:1-212](), [sdk/typescript/src/ai/RateLimiter.ts:1-250]()

---

# Page: Harness Orchestration

# Harness Orchestration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [sdk/go/agent/agent.go](sdk/go/agent/agent.go)
- [sdk/go/agent/agent_lifecycle.go](sdk/go/agent/agent_lifecycle.go)
- [sdk/go/agent/pause.go](sdk/go/agent/pause.go)
- [sdk/go/agent/pause_test.go](sdk/go/agent/pause_test.go)
- [sdk/go/harness/claudecode.go](sdk/go/harness/claudecode.go)
- [sdk/go/harness/coverage_branches_test.go](sdk/go/harness/coverage_branches_test.go)
- [sdk/go/harness/coverage_helpers_test.go](sdk/go/harness/coverage_helpers_test.go)
- [sdk/go/harness/parity_test.go](sdk/go/harness/parity_test.go)
- [sdk/go/harness/provider.go](sdk/go/harness/provider.go)
- [sdk/go/harness/result.go](sdk/go/harness/result.go)
- [sdk/go/harness/runner.go](sdk/go/harness/runner.go)
- [sdk/go/harness/runner_test.go](sdk/go/harness/runner_test.go)
- [sdk/go/harness/schema.go](sdk/go/harness/schema.go)
- [sdk/python/agentfield/harness/_runner.py](sdk/python/agentfield/harness/_runner.py)
- [sdk/python/agentfield/harness/_schema.py](sdk/python/agentfield/harness/_schema.py)
- [sdk/python/agentfield/harness/providers/claude.py](sdk/python/agentfield/harness/providers/claude.py)
- [sdk/python/agentfield/harness/providers/codex.py](sdk/python/agentfield/harness/providers/codex.py)
- [sdk/python/agentfield/harness/providers/gemini.py](sdk/python/agentfield/harness/providers/gemini.py)
- [sdk/python/agentfield/harness/providers/opencode.py](sdk/python/agentfield/harness/providers/opencode.py)
- [sdk/python/agentfield/types.py](sdk/python/agentfield/types.py)
- [sdk/python/tests/test_harness_ai_schema_repair.py](sdk/python/tests/test_harness_ai_schema_repair.py)
- [sdk/python/tests/test_harness_provider_claude.py](sdk/python/tests/test_harness_provider_claude.py)
- [sdk/python/tests/test_harness_provider_codex.py](sdk/python/tests/test_harness_provider_codex.py)
- [sdk/python/tests/test_harness_provider_gemini.py](sdk/python/tests/test_harness_provider_gemini.py)
- [sdk/python/tests/test_harness_provider_opencode.py](sdk/python/tests/test_harness_provider_opencode.py)
- [sdk/python/tests/test_harness_runner.py](sdk/python/tests/test_harness_runner.py)
- [sdk/python/tests/test_harness_schema.py](sdk/python/tests/test_harness_schema.py)

</details>



The **Harness** system provides a standardized interface for delegating complex, autonomous tasks to specialized coding agents. Unlike standard LLM interactions (e.g., `app.ai()`), the Harness orchestrates "agentic" workflows where the model has access to a file system, shell, and multi-turn reasoning loops to solve engineering problems.

The primary entry point for this system is the `HarnessRunner` (Python) or `Runner` (Go), which manages the lifecycle of these external agents, handles environment preparation, and ensures structured output via schema enforcement.

### Key Capabilities
*   **Provider Abstraction**: A unified API for interacting with `Claude Code`, `Codex`, `Gemini`, and `OpenCode`.
*   **Autonomous Execution**: Agents can read/write files and execute shell commands within a sandboxed or local environment.
*   **Structured Delegation**: Request complex objects (e.g., security audits, code refactors) and receive validated JSON via automated retry loops.
*   **State Management**: Support for resuming sessions and tracking multi-turn execution metrics.

---

## Harness Concepts & Architecture
The Harness operates as a wrapper around specialized CLI tools and SDKs. It translates a high-level `prompt` and `schema` into the specific command-line arguments and file-system protocols required by each provider.

### The Harness Lifecycle
1.  **Preparation**: The `Runner` merges global defaults with per-call `Options`.
2.  **Schema Injection**: If a schema is provided, the `Runner` appends a "Critical Output Requirement" suffix to the prompt, instructing the agent to write its final answer to a deterministic file path (typically `.agentfield_output.json`).
3.  **Execution**: The `Runner` invokes the provider (e.g., via `subprocess` or native SDK).
4.  **Extraction & Validation**: Once the agent finishes, the `Runner` attempts to read the output file, validate it against the schema, and perform repairs if necessary.

For details on the architecture and when to use the Harness vs. standard AI calls, see [Harness Concepts & Architecture](#11.1).

**Sources:**
*   `HarnessRunner` definition: [sdk/python/agentfield/harness/_runner.py:209-211]()
*   Go `Runner` and `Run` logic: [sdk/go/harness/runner.go:21-53]()
*   Prompt suffix injection: [sdk/go/harness/runner.go:121-131]()

---

## Harness Providers
Providers are the bridge between AgentField and the underlying coding agents. Each provider implements a standard `Execute` interface to handle the nuances of different platforms.

| Provider | Backend Entity | Description |
| :--- | :--- | :--- |
| `ClaudeCodeProvider` | `claude_agent_sdk` | Native Python SDK integration for Anthropic's Claude Code. |
| `CodexProvider` | `codex` CLI | High-performance engineering agent with native schema support. |
| `GeminiProvider` | `gemini` CLI | Google's autonomous agent, often used for large-context tasks. |
| `OpenCodeProvider` | `opencode` CLI | Open-source compatible engineering agent. |

### Provider Orchestration Diagram
```mermaid
graph TD
    subgraph "AgentField SDK Space"
        Runner["HarnessRunner / Runner"]
        Opts["Harness Options"]
    end

    subgraph "Provider Implementations"
        CP["ClaudeCodeProvider"]
        CXP["CodexProvider"]
        GNP["GeminiProvider"]
        OCP["OpenCodeProvider"]
    end

    subgraph "External Agent Space"
        CSDK["claude_agent_sdk"]
        CCLI["codex exec"]
        GCLI["gemini run"]
        OCLI["opencode run"]
    end

    Runner -->|dispatch| CP
    Runner -->|dispatch| CXP
    Runner -->|dispatch| GNP
    Runner -->|dispatch| OCP

    CP -->|native call| CSDK
    CXP -->|subprocess| CCLI
    GNP -->|subprocess| GCLI
    OCP -->|subprocess| OCLI
```

For detailed configuration and platform differences, see [Harness Providers](#11.2).

**Sources:**
*   `OpenCodeProvider` implementation: [sdk/python/agentfield/harness/providers/opencode.py:125-147]()
*   `ClaudeCodeProvider` implementation: [sdk/python/agentfield/harness/providers/claude.py:35-47]()
*   Go `Provider` interface: [sdk/go/harness/runner.go:160-166]()

---

## Schema Extraction & Repair
A core strength of the Harness is ensuring that autonomous agents return structured data. Because agents may fail to format JSON correctly during long-running tasks, the system employs several layers of recovery.

### Extraction Strategies
*   **File Protocol**: Most providers are instructed to use their `Write` tool to save JSON to `.agentfield_output.json`.
*   **Native Schema**: `Codex` supports native structured output via `--output-schema`, which AgentField leverages for higher reliability.
*   **Incremental Mode**: For large schemas, the Harness can instruct the agent to build the object field-by-field.

### Repair Loop
If validation fails, the `HarnessRunner` executes a tiered repair strategy:
1.  **Cosmetic Repair**: Regex-based cleaning of markdown fences and trailing commas.
2.  **AI-Based Repair**: A fast, tool-less LLM call (via `litellm`) to reformat the malformed text into the target schema.
3.  **Retry Loop**: Re-running the agent with a "follow-up" prompt highlighting the specific validation errors.

### Schema Entity Mapping
```mermaid
graph LR
    subgraph "Code Entity Space"
        SR["HarnessRunner.handle_schema_with_retry"]
        ASR["_ai_schema_repair"]
        CR["cosmetic_repair"]
        BPS["BuildPromptSuffix"]
    end

    subgraph "Natural Language / File Space"
        Schema[".agentfield_schema.json"]
        Output[".agentfield_output.json"]
        Inst["'CRITICAL OUTPUT REQUIREMENTS'"]
    end

    BPS -->|generates| Inst
    Inst -->|references| Schema
    Inst -->|directs to| Output
    SR -->|calls| CR
    SR -->|calls| ASR
    ASR -->|repairs| Output
```

For details on the repair logic and incremental builds, see [Schema Extraction & Repair](#11.3).

**Sources:**
*   AI Schema Repair logic: [sdk/python/agentfield/harness/_runner.py:66-88]()
*   Cosmetic Repair function: [sdk/go/harness/schema.go:207-212]()
*   Go Retry/Validation loop: [sdk/go/harness/runner.go:140-144]()
*   Output file constants: [sdk/go/harness/schema.go:17-21]()

---

# Page: Harness Concepts & Architecture

# Harness Concepts & Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [sdk/go/harness/cli.go](sdk/go/harness/cli.go)
- [sdk/go/harness/cli_unix.go](sdk/go/harness/cli_unix.go)
- [sdk/go/harness/cli_windows.go](sdk/go/harness/cli_windows.go)
- [sdk/go/harness/opencode.go](sdk/go/harness/opencode.go)
- [sdk/go/harness/opencode_json_test.go](sdk/go/harness/opencode_json_test.go)
- [sdk/go/harness/opencode_test.go](sdk/go/harness/opencode_test.go)
- [sdk/python/agentfield/harness/_cli.py](sdk/python/agentfield/harness/_cli.py)
- [sdk/python/agentfield/harness/_runner.py](sdk/python/agentfield/harness/_runner.py)
- [sdk/python/agentfield/harness/_schema.py](sdk/python/agentfield/harness/_schema.py)
- [sdk/python/agentfield/harness/providers/claude.py](sdk/python/agentfield/harness/providers/claude.py)
- [sdk/python/agentfield/harness/providers/codex.py](sdk/python/agentfield/harness/providers/codex.py)
- [sdk/python/agentfield/harness/providers/gemini.py](sdk/python/agentfield/harness/providers/gemini.py)
- [sdk/python/agentfield/harness/providers/opencode.py](sdk/python/agentfield/harness/providers/opencode.py)
- [sdk/python/agentfield/types.py](sdk/python/agentfield/types.py)
- [sdk/python/tests/test_agent_ai_deadlock_recovery.py](sdk/python/tests/test_agent_ai_deadlock_recovery.py)
- [sdk/python/tests/test_agent_server.py](sdk/python/tests/test_agent_server.py)
- [sdk/python/tests/test_harness_ai_schema_repair.py](sdk/python/tests/test_harness_ai_schema_repair.py)
- [sdk/python/tests/test_harness_cli.py](sdk/python/tests/test_harness_cli.py)
- [sdk/python/tests/test_harness_provider_claude.py](sdk/python/tests/test_harness_provider_claude.py)
- [sdk/python/tests/test_harness_provider_codex.py](sdk/python/tests/test_harness_provider_codex.py)
- [sdk/python/tests/test_harness_provider_gemini.py](sdk/python/tests/test_harness_provider_gemini.py)
- [sdk/python/tests/test_harness_provider_opencode.py](sdk/python/tests/test_harness_provider_opencode.py)
- [sdk/python/tests/test_harness_runner.py](sdk/python/tests/test_harness_runner.py)
- [sdk/python/tests/test_harness_schema.py](sdk/python/tests/test_harness_schema.py)
- [sdk/python/tests/test_run_cli_env.py](sdk/python/tests/test_run_cli_env.py)
- [sdk/typescript/src/harness/cli.ts](sdk/typescript/src/harness/cli.ts)
- [sdk/typescript/tests/harness_cli.test.ts](sdk/typescript/tests/harness_cli.test.ts)

</details>



The **Harness** is a specialized orchestration layer within AgentField designed to delegate complex, autonomous tasks to external coding agents and specialized LLM runtimes (e.g., Claude Code, OpenCode, Codex). Unlike the standard `app.ai()` interface, which performs single-turn or simple tool-calling completions, the Harness manages long-running, multi-turn "trajectories" where an external agent may browse a repository, run tests, and perform multi-step reasoning before returning a final structured result.

## Core Architecture

The Harness architecture follows a "Provider" pattern, abstracting the differences between various autonomous agent CLIs and SDKs.

### The HarnessRunner Lifecycle
The `HarnessRunner` is the central orchestrator responsible for managing the execution lifecycle of a harness task [sdk/python/agentfield/harness/_runner.py:209-211]().

1.  **Option Resolution**: Merges global configuration with call-specific overrides for providers, models, and budgets [sdk/python/agentfield/harness/_runner.py:154-187]().
2.  **Provider Selection**: Instantiates the requested `HarnessProvider` (e.g., `OpenCodeProvider`, `ClaudeCodeProvider`) [sdk/python/agentfield/harness/providers/_factory.py]().
3.  **Execution Loop**: Invokes the provider's `execute` method. This often involves spawning a subprocess or calling a native SDK [sdk/python/agentfield/harness/providers/opencode.py:155-164]().
4.  **Watchdog Monitoring**: A no-progress watchdog monitors `stdout`/`stderr`. If the subprocess remains silent for a defined window (default 300s), it is terminated to prevent silent hangs [sdk/python/agentfield/harness/_cli.py:24-25](), [sdk/go/harness/cli.go:26-27]().
5.  **Schema Extraction & Repair**: If a structured output (Pydantic model) is expected, the runner attempts to extract JSON from the agent's prose and applies AI-based repair if the JSON is malformed [sdk/python/agentfield/harness/_runner.py:66-152]().

### Data Flow Diagram
The following diagram illustrates the flow from a high-level `app.harness()` call down to the OS-level subprocess.

**Harness Execution Flow**
```mermaid
graph TD
    subgraph "Natural Language Space"
        UserPrompt["User Prompt + Pydantic Schema"]
    end

    subgraph "Code Entity Space"
        HR["HarnessRunner (_runner.py)"]
        Prov["HarnessProvider (e.g. OpenCodeProvider)"]
        CLI["run_cli (_cli.py)"]
        SubP["OS Subprocess (e.g. 'opencode run')"]
    end

    UserPrompt --> HR
    HR --> Prov
    Prov --> CLI
    CLI --> SubP
    SubP -- "JSONL Stream / Stdout" --> CLI
    CLI -- "RawResult" --> HR
    HR -- "Validated Object" --> UserPrompt
```
Sources: [sdk/python/agentfield/harness/_runner.py:209-211](), [sdk/python/agentfield/harness/_cli.py:147-155](), [sdk/python/agentfield/harness/providers/opencode.py:125-126]()

## Provider Abstraction

The Harness supports multiple providers through a unified interface. Providers are responsible for translating AgentField options into the specific CLI flags or SDK calls required by the target agent.

### CLI-Based Providers
Providers like `OpenCode`, `Codex`, and `Gemini` typically wrap a CLI binary.
*   **OpenCode**: Uses `opencode run --format json`. It supports project directory isolation via `--dir` and handles model selection via `-m` [sdk/python/agentfield/harness/providers/opencode.py:168-183]().
*   **Codex**: Invokes `codex exec --json` with sandbox permissions [sdk/python/tests/test_harness_provider_codex.py:166-176]().
*   **Concurrency Control**: CLI providers often use a global semaphore to limit the number of simultaneous subprocesses, preventing local resource exhaustion or LLM rate-limiting [sdk/python/agentfield/harness/providers/opencode.py:136-139](), [sdk/go/harness/opencode.go:42-53]().

### Native SDK Providers
*   **Claude Code**: Uses the `claude_agent_sdk` directly rather than a CLI subprocess. It maps AgentField's `permission_mode` to Claude's `bypassPermissions` or `plan` modes [sdk/python/agentfield/harness/providers/claude.py:35-69]().

**Provider Mapping**
| Feature | OpenCode | Claude Code | Codex |
| :--- | :--- | :--- | :--- |
| **Communication** | Subprocess (JSONL) | Native Python SDK | Subprocess (JSON) |
| **Project Root** | `--dir` | `cwd` | `-C` |
| **Binary Name** | `opencode` | `claude_agent_sdk` | `codex` |

Sources: [sdk/python/agentfield/harness/providers/opencode.py:125-183](), [sdk/python/agentfield/harness/providers/claude.py:35-72](), [sdk/python/agentfield/harness/providers/codex.py]()

## Implementation Details

### Subprocess Management (`run_cli`)
The `run_cli` function provides a robust wrapper for `asyncio.create_subprocess_exec`. Key features include:
*   **Environment Inheritance**: Propagates parent process environment variables so that tools like `EXA_API_KEY` reach the agent [sdk/python/agentfield/harness/_cli.py:169-172]().
*   **Idle Watchdog**: Uses a `StreamReader` to record the timestamp of the last activity on `stdout` or `stderr`. If `stalledFor >= idleSeconds`, the process group is killed [sdk/python/agentfield/harness/_cli.py:68-81](), [sdk/go/harness/cli.go:193-217]().
*   **Windows Compatibility**: Resolves `.cmd` shims on Windows using `shutil.which` and handles prompt delivery via `stdin` to bypass the ~8k character command-line limit [sdk/python/agentfield/harness/_cli.py:31-46](), [sdk/go/harness/opencode.go:16-26]().

### Silent Deadlock Recovery
To prevent `litellm` from wedging the system due to half-closed sockets, the AI integration includes a safety net. If an AI call times out, the system forcefully clears the internal `litellm` HTTP client caches to ensure the next call starts with a fresh connection pool [sdk/python/tests/test_agent_ai_deadlock_recovery.py:1-27](), [sdk/python/agentfield/agent_ai.py:41]().

**Subprocess Architecture**
```mermaid
graph LR
    subgraph "Python Process"
        AF["AgentField App"]
        RC["run_cli (_cli.py)"]
        WD["Watchdog Loop"]
    end

    subgraph "OS Level"
        Proc["Child Subprocess (PGID)"]
        Pipes["stdout / stderr Pipes"]
    end

    AF --> RC
    RC -- "create_subprocess_exec" --> Proc
    Proc -- "Output" --> Pipes
    Pipes -- "Read" --> RC
    RC -- "Update Activity" --> WD
    WD -- "Kill PGID on Idle" --> Proc
```
Sources: [sdk/python/agentfield/harness/_cli.py:147-187](), [sdk/go/harness/cli.go:124-136]()

## When to use Harness vs app.ai()

| Criteria | `app.ai()` | `app.harness()` |
| :--- | :--- | :--- |
| **Interaction** | Single-turn / Tool-calling | Multi-turn Autonomous Trajectory |
| **Scope** | Stateless or Session Memory | Full Repository / Local Filesystem |
| **Duration** | Seconds | Minutes |
| **Cost** | Low (Single completion) | High (Multiple turns + tool runs) |
| **Output** | Text or Structured Data | Validated Schema + Trajectory Logs |

Use **Harness** when you need an agent to perform "work" (coding, searching, debugging) that requires multiple steps and autonomous decision-making. Use **app.ai()** for immediate reasoning, classification, or simple data extraction within a larger workflow.

Sources: [sdk/python/agentfield/harness/_runner.py:209-211](), [sdk/python/agentfield/agent_ai.py]()

---

# Page: Harness Providers

# Harness Providers

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [sdk/python/agentfield/harness/_result.py](sdk/python/agentfield/harness/_result.py)
- [sdk/python/agentfield/harness/_runner.py](sdk/python/agentfield/harness/_runner.py)
- [sdk/python/agentfield/harness/_schema.py](sdk/python/agentfield/harness/_schema.py)
- [sdk/python/agentfield/harness/providers/_factory.py](sdk/python/agentfield/harness/providers/_factory.py)
- [sdk/python/agentfield/harness/providers/claude.py](sdk/python/agentfield/harness/providers/claude.py)
- [sdk/python/agentfield/harness/providers/codex.py](sdk/python/agentfield/harness/providers/codex.py)
- [sdk/python/agentfield/harness/providers/gemini.py](sdk/python/agentfield/harness/providers/gemini.py)
- [sdk/python/agentfield/harness/providers/opencode.py](sdk/python/agentfield/harness/providers/opencode.py)
- [sdk/python/agentfield/types.py](sdk/python/agentfield/types.py)
- [sdk/python/tests/test_harness_ai_schema_repair.py](sdk/python/tests/test_harness_ai_schema_repair.py)
- [sdk/python/tests/test_harness_provider_claude.py](sdk/python/tests/test_harness_provider_claude.py)
- [sdk/python/tests/test_harness_provider_codex.py](sdk/python/tests/test_harness_provider_codex.py)
- [sdk/python/tests/test_harness_provider_gemini.py](sdk/python/tests/test_harness_provider_gemini.py)
- [sdk/python/tests/test_harness_provider_opencode.py](sdk/python/tests/test_harness_provider_opencode.py)
- [sdk/python/tests/test_harness_runner.py](sdk/python/tests/test_harness_runner.py)
- [sdk/python/tests/test_harness_schema.py](sdk/python/tests/test_harness_schema.py)
- [sdk/typescript/src/harness/providers/opencode.ts](sdk/typescript/src/harness/providers/opencode.ts)
- [sdk/typescript/tests/harness_provider_opencode.test.ts](sdk/typescript/tests/harness_provider_opencode.test.ts)

</details>



Harness Providers are specialized execution drivers that interface between the `HarnessRunner` [sdk/python/agentfield/harness/_runner.py:209-211]() and various autonomous coding agent platforms. Unlike standard LLM interactions via `app.ai()`, Harness Providers manage full-lifecycle agent execution, including tool use, file system operations, and multi-turn reasoning loops within a repository context.

## Provider Architecture

All providers implement a common interface (or pattern) centered around the `execute` method. This method accepts a natural language prompt and an `options` dictionary, returning a `RawResult` containing the execution output, metrics, and session identifiers.

### Data Flow: Natural Language to Code Entity Space

The following diagram illustrates how a natural language request is transformed into a specific CLI or SDK command targeting a provider's code entity.

**Provider Execution Mapping**
```mermaid
graph TD
    subgraph "Natural Language Space"
        REQ["'Fix the bug in the login route'"]
        CONFIG["HarnessConfig (provider, model, permission_mode)"]
    end

    subgraph "Harness Code Entity Space"
        RUNNER["HarnessRunner.run()"]
        FACTORY["build_provider()"]
        
        subgraph "Providers"
            OP["OpenCodeProvider.execute()"]
            CL["ClaudeCodeProvider.execute()"]
            CX["CodexProvider.execute()"]
            GE["GeminiProvider.execute()"]
        end
    end

    subgraph "External Tool Space"
        OC_CLI["'opencode run'"]
        CL_SDK["claude_agent_sdk.query()"]
        CX_CLI["'codex exec'"]
        GE_CLI["'gemini -p'"]
    end

    REQ --> RUNNER
    CONFIG --> FACTORY
    FACTORY --> RUNNER
    RUNNER --> OP
    RUNNER --> CL
    RUNNER --> CX
    RUNNER --> GE
    
    OP -- "Subprocess" --> OC_CLI
    CL -- "Python SDK" --> CL_SDK
    CX -- "Subprocess" --> CX_CLI
    GE -- "Subprocess" --> GE_CLI
```
**Sources:** [sdk/python/agentfield/harness/_runner.py:209-211](), [sdk/python/agentfield/harness/providers/_factory.py](), [sdk/python/agentfield/harness/providers/opencode.py:125-126](), [sdk/python/agentfield/harness/providers/claude.py:35-36]()

---

## Supported Providers

### 1. OpenCodeProvider
The `OpenCodeProvider` invokes the `opencode` CLI (v1.4+). It is designed for high-concurrency environments and includes specialized logic for parsing JSONL event streams from the CLI's stdout.

*   **Implementation:** Uses `asyncio.create_subprocess_exec` via the internal `run_cli` helper [sdk/python/agentfield/harness/providers/opencode.py:168-170]().
*   **Concurrency Control:** Implements a global `asyncio.Semaphore` (defaulting to 10) to prevent overwhelming the underlying LLM provider during parallel tasks [sdk/python/agentfield/harness/providers/opencode.py:136-139]().
*   **Data Handling:**
    *   **Project Root:** Uses the `--dir` flag to set the agent's workspace. `project_dir` takes precedence over `cwd` [sdk/python/agentfield/harness/providers/opencode.py:177-179]().
    *   **Platform Differences:** On Windows, the prompt is passed via `stdin` to avoid the 8k character limit of `cmd.exe` [sdk/python/agentfield/harness/providers/opencode.py:39-48]().
    *   **Error Detection:** Scans `stderr` for specific patterns like "Model not found" or "AuthenticationError" even if the process exits with code 0 [sdk/python/agentfield/harness/providers/opencode.py:30-36]().

**Sources:** [sdk/python/agentfield/harness/providers/opencode.py:1-180](), [sdk/python/tests/test_harness_provider_opencode.py:62-70]()

### 2. ClaudeCodeProvider
The `ClaudeCodeProvider` utilizes the native `claude_agent_sdk` Python library. Unlike other providers, it does not rely on a CLI subprocess.

*   **Lazy Loading:** The SDK is an optional dependency, loaded only when the provider is instantiated via `_get_claude_sdk()` [sdk/python/agentfield/harness/providers/claude.py:16-26]().
*   **Permission Modes:** Maps Harness permission modes to SDK-specific strings: `auto` becomes `bypassPermissions` and `plan` remains `plan` [sdk/python/agentfield/harness/providers/claude.py:29-32]().
*   **Execution:** Iterates over an async generator returned by `sdk.query()`, accumulating messages and extracting `total_cost_usd` and `num_turns` from the final `result` or `success` events [sdk/python/agentfield/harness/providers/claude.py:102-130]().

**Sources:** [sdk/python/agentfield/harness/providers/claude.py:35-159](), [sdk/python/tests/test_harness_provider_claude.py:22-87]()

### 3. CodexProvider
The `CodexProvider` interfaces with the `codex` CLI using the `exec --json` command.

*   **Sandbox Configuration:** Maps `permission_mode` to Codex sandbox policies. `auto` enables `workspace-write`, while `plan` restricts the agent to `read-only` [sdk/python/agentfield/harness/providers/codex.py:41-45]().
*   **Resilience:** Automatically includes the `--skip-git-repo-check` flag to allow execution in temporary directories or non-git projects [sdk/python/agentfield/harness/providers/codex.py:30]().
*   **Working Directory:** Uses the `-C` flag to specify the agent root [sdk/python/agentfield/harness/providers/codex.py:36]().

**Sources:** [sdk/python/agentfield/harness/providers/codex.py:19-48](), [sdk/python/tests/test_harness_provider_codex.py:166-176]()

### 4. GeminiProvider
The `GeminiProvider` wraps the `gemini` CLI. It features unique argument handling compared to other providers.

*   **Permission Modes:** Uses the `--yolo` flag for `auto` mode (auto-approving actions) and `--approval-mode plan` for `plan` mode [sdk/python/agentfield/harness/providers/gemini.py:27-31]().
*   **Platform Constraints:** Gemini rejects unknown arguments; notably, it does not support a `-C` or `--cd` flag. The provider instead sets the process working directory directly via the `cwd` parameter in `run_cli` [sdk/python/agentfield/harness/providers/gemini.py:46-53]().

**Sources:** [sdk/python/agentfield/harness/providers/gemini.py:13-54](), [sdk/python/tests/test_harness_provider_gemini.py:47-57]()

---

## Configuration and Permission Modes

The behavior of providers is governed by the `HarnessConfig` [sdk/python/agentfield/types.py:328-348]() and the options passed during execution.

### Permission Matrix

| Mode | OpenCode | Claude Code | Codex | Gemini |
| :--- | :--- | :--- | :--- | :--- |
| `auto` | `--dangerously-skip-permissions` | `bypassPermissions` | `--sandbox workspace-write` | `--yolo` |
| `plan` | (Default behavior) | `plan` | `--sandbox read-only` | `--approval-mode plan` |

### Platform and Root Directory Handling

A critical aspect of Harness Providers is managing where the agent is allowed to read and write files.

**Root Directory Resolution Logic**
```mermaid
graph LR
    subgraph "Input Options"
        PD["project_dir"]
        CWD["cwd"]
    end

    subgraph "Provider Logic"
        PREC["Precedence: project_dir > cwd"]
        STRAT["Universal File-Write Strategy"]
    end

    subgraph "Output Entities"
        OUT_PATH[".agentfield_output.json"]
        SCHEMA_PATH[".agentfield_schema.json"]
    end

    PD --> PREC
    CWD --> PREC
    PREC --> STRAT
    STRAT --> OUT_PATH
    STRAT --> SCHEMA_PATH
```

1.  **Precedence:** For all providers, `project_dir` is the canonical agent root. If unset, the system falls back to `cwd` [sdk/python/agentfield/harness/providers/opencode.py:177-179](), [sdk/python/agentfield/harness/providers/claude.py:56-58]().
2.  **Schema Output:** The `HarnessRunner` calculates the output path relative to this resolved root using `get_output_path(cwd)` [sdk/python/agentfield/harness/_schema.py:29-31](). This ensures that even if an agent is executing a task in a nested subdirectory, it writes its structured result to a location within its permitted "project" boundary [sdk/python/tests/test_harness_runner.py:75-108]().

**Sources:** [sdk/python/agentfield/harness/_runner.py:154-187](), [sdk/python/agentfield/harness/_schema.py:1-12](), [sdk/python/agentfield/types.py:328-348]()

---

# Page: Schema Extraction & Repair

# Schema Extraction & Repair

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [sdk/go/agent/agent.go](sdk/go/agent/agent.go)
- [sdk/go/agent/agent_lifecycle.go](sdk/go/agent/agent_lifecycle.go)
- [sdk/go/agent/pause.go](sdk/go/agent/pause.go)
- [sdk/go/agent/pause_test.go](sdk/go/agent/pause_test.go)
- [sdk/go/harness/claudecode.go](sdk/go/harness/claudecode.go)
- [sdk/go/harness/coverage_branches_test.go](sdk/go/harness/coverage_branches_test.go)
- [sdk/go/harness/coverage_helpers_test.go](sdk/go/harness/coverage_helpers_test.go)
- [sdk/go/harness/parity_test.go](sdk/go/harness/parity_test.go)
- [sdk/go/harness/provider.go](sdk/go/harness/provider.go)
- [sdk/go/harness/result.go](sdk/go/harness/result.go)
- [sdk/go/harness/runner.go](sdk/go/harness/runner.go)
- [sdk/go/harness/runner_test.go](sdk/go/harness/runner_test.go)
- [sdk/go/harness/schema.go](sdk/go/harness/schema.go)
- [sdk/python/agentfield/harness/_runner.py](sdk/python/agentfield/harness/_runner.py)
- [sdk/python/agentfield/harness/_schema.py](sdk/python/agentfield/harness/_schema.py)
- [sdk/python/agentfield/harness/providers/claude.py](sdk/python/agentfield/harness/providers/claude.py)
- [sdk/python/agentfield/harness/providers/codex.py](sdk/python/agentfield/harness/providers/codex.py)
- [sdk/python/agentfield/harness/providers/gemini.py](sdk/python/agentfield/harness/providers/gemini.py)
- [sdk/python/agentfield/harness/providers/opencode.py](sdk/python/agentfield/harness/providers/opencode.py)
- [sdk/python/agentfield/types.py](sdk/python/agentfield/types.py)
- [sdk/python/tests/test_harness_ai_schema_repair.py](sdk/python/tests/test_harness_ai_schema_repair.py)
- [sdk/python/tests/test_harness_provider_claude.py](sdk/python/tests/test_harness_provider_claude.py)
- [sdk/python/tests/test_harness_provider_codex.py](sdk/python/tests/test_harness_provider_codex.py)
- [sdk/python/tests/test_harness_provider_gemini.py](sdk/python/tests/test_harness_provider_gemini.py)
- [sdk/python/tests/test_harness_provider_opencode.py](sdk/python/tests/test_harness_provider_opencode.py)
- [sdk/python/tests/test_harness_runner.py](sdk/python/tests/test_harness_runner.py)
- [sdk/python/tests/test_harness_schema.py](sdk/python/tests/test_harness_schema.py)

</details>



The `HarnessRunner` orchestrates the execution of autonomous coding agents and ensures that their natural language reasoning results in structured, machine-readable JSON data. This process involves a sophisticated pipeline of schema-driven prompting, multi-modal extraction (file-based vs. native), and a multi-tiered repair strategy that handles everything from minor syntax errors to complete structural failures.

## Overview of Extraction Strategies

The `HarnessRunner` supports two primary modes for requesting structured output from an agent: **Single-Shot** and **Incremental**.

| Mode | Implementation | Best Use Case |
| :--- | :--- | :--- |
| **Single-Shot** | Asks the agent to write the entire JSON object to a file in one operation [sdk/go/harness/runner.go:83-83](). | Small to medium schemas; lowest token cost. |
| **Incremental** | Asks the agent to build the object top-level field by top-level field [sdk/go/harness/runner.go:84-85](). | Large or deep schemas where agents often "lose the thread" mid-generation. |
| **Auto** | Switches to incremental mode if the schema exceeds a token threshold (default: 4000) [sdk/go/harness/schema.go:20-20](). | General purpose balanced performance. |

### Data Flow: Natural Language to Structured Entity

The following diagram illustrates how the `HarnessRunner` bridges the gap between the LLM's text space and the SDK's typed objects.

**Extraction Pipeline Flow**
```mermaid
graph TD
    subgraph "Natural Language Space"
        A["User Prompt"] --> B["BuildPromptSuffix() / BuildIncrementalPromptSuffix()"]
        B --> C["Agent Execution (LLM)"]
        C --> D["Agent Output (Markdown/Prose/Files)"]
    end

    subgraph "Code Entity Space"
        D --> E["HarnessRunner.handleSchemaWithRetry()"]
        E --> F{"Extraction Method"}
        F -- "File Protocol" --> G["ReadAndParse(.agentfield_output.json)"]
        F -- "Native Protocol" --> H["schemaAware.SetSchema() / --output-schema"]
        G --> I["Cosmetic & AI Repair"]
        H --> I
        I --> J["json.Unmarshal() / pydantic.parse_obj()"]
    end
```
**Sources:** [sdk/go/harness/runner.go:53-158](), [sdk/go/harness/schema.go:137-175](), [sdk/python/agentfield/harness/_runner.py:210-250]()

## The Extraction Protocols

The system employs different protocols based on the provider's capabilities.

### 1. The File-Write Protocol (Claude/OpenCode)
For providers like `ClaudeCodeProvider` or `OpenCodeProvider`, the runner appends a `CRITICAL OUTPUT REQUIREMENTS` suffix to the prompt [sdk/go/harness/schema.go:166-174](). This instructs the agent to use its `Write` tool to create a deterministic file named `.agentfield_output.json` [sdk/go/harness/schema.go:18-18]().

### 2. The Native Schema Protocol (Codex)
Providers implementing the `schemaAware` interface [sdk/go/harness/runner.go:43-45]() (like `CodexProvider`) bypass the file-write instructions. Instead:
- The runner generates a "Strict" JSON schema (stripping defaults, making all fields required) [sdk/go/harness/schema.go:46-50]().
- The schema is passed via CLI flags (e.g., `--output-schema`) [sdk/go/harness/schema.go:126-133]().
- The provider captures the agent's final message and persists it directly [sdk/go/harness/runner.go:125-130]().

## Repair & Retry Loops

When extraction fails (e.g., the file is missing, contains invalid JSON, or fails schema validation), the `HarnessRunner` enters a repair loop.

### Multi-Tiered Repair Logic

1.  **Cosmetic Repair**: A deterministic pass that strips markdown fences (```json ... ```) and attempts to balance trailing braces/brackets [sdk/go/harness/schema.go:207-215]().
2.  **AI-Based Repair**: If cosmetic repair fails, the Python SDK attempts `_ai_schema_repair`. This makes a single, cheap LLM call (no tools) specifically to reformat the existing malformed text into valid JSON matching the schema [sdk/python/agentfield/harness/_runner.py:66-88]().
3.  **Follow-up Retry**: If the output is still invalid, the runner performs a full retry by sending a follow-up prompt to the same agent session, describing the specific validation errors (via `diagnose_output_failure`) [sdk/python/agentfield/harness/_schema.py:21-21]().

**Repair Sequence Diagram**
```mermaid
sequenceDiagram
    participant R as HarnessRunner
    participant P as Provider (e.g., OpenCodeProvider)
    participant AI as Repair LLM (litellm)

    R->>P: Execute(Prompt + Suffix)
    P-->>R: RawResult (Malformed JSON)
    
    rect rgb(240, 240, 240)
    Note over R: Tier 1: Cosmetic
    R->>R: cosmeticRepair()
    end

    alt Still Invalid
        rect rgb(240, 240, 240)
        Note over R: Tier 2: AI Repair
        R->>AI: _ai_schema_repair(text, schema)
        AI-->>R: Validated JSON
        end
    end

    alt Still Invalid
        rect rgb(240, 240, 240)
        Note over R: Tier 3: Follow-up
        R->>P: Execute(BuildFollowupPrompt(errors))
        P-->>R: New RawResult
        end
    end
```
**Sources:** [sdk/python/agentfield/harness/_runner.py:66-152](), [sdk/go/harness/runner.go:141-143](), [sdk/go/harness/schema.go:207-220]()

## Key Implementation Details

### Incremental Build Mode
For complex schemas, the runner uses `BuildIncrementalPromptSuffix` [sdk/go/harness/runner.go:127-127](). This instructs the agent to:
1. Initialize the JSON file with an empty object.
2. For each top-level field in the schema, perform the necessary reasoning and use a `Patch` or `Write` operation to update that specific field [sdk/go/harness/runner.go:84-85]().

### Error Diagnosis
The `diagnose_field_failures` and `diagnose_output_failure` functions [sdk/python/agentfield/harness/_schema.py:20-21]() are used to generate human-readable (and agent-readable) descriptions of why the JSON failed validation. This is critical for the "Follow-up" tier of repair, as it allows the agent to see exactly which field was missing or had the wrong type.

### Token Estimation
The runner uses a simple heuristic of 4 characters per token to decide when a schema is "large" [sdk/go/harness/schema.go:33-36](). If the schema exceeds `largeSchemaTokenThreshold` (4000 tokens), the runner writes the schema to a temporary file `.agentfield_schema.json` and tells the agent to read it from disk rather than including the full text in the prompt [sdk/go/harness/schema.go:151-163]().

**Sources:**
- `sdk/go/harness/runner.go`: Core orchestration logic.
- `sdk/go/harness/schema.go`: Suffix building and cosmetic repair.
- `sdk/python/agentfield/harness/_runner.py`: AI-based repair implementation.
- `sdk/python/agentfield/harness/_schema.py`: Validation and diagnosis utilities.

---

# Page: Examples

# Examples

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/python_agent_nodes/deep_research/README.md](examples/python_agent_nodes/deep_research/README.md)
- [examples/python_agent_nodes/deep_research/__init__.py](examples/python_agent_nodes/deep_research/__init__.py)
- [examples/python_agent_nodes/deep_research/main.py](examples/python_agent_nodes/deep_research/main.py)
- [examples/python_agent_nodes/deep_research/requirements.txt](examples/python_agent_nodes/deep_research/requirements.txt)
- [examples/python_agent_nodes/deep_research/routers/__init__.py](examples/python_agent_nodes/deep_research/routers/__init__.py)
- [examples/python_agent_nodes/deep_research/routers/planning.py](examples/python_agent_nodes/deep_research/routers/planning.py)
- [examples/python_agent_nodes/deep_research/routers/research.py](examples/python_agent_nodes/deep_research/routers/research.py)
- [examples/python_agent_nodes/deep_research/schemas.py](examples/python_agent_nodes/deep_research/schemas.py)
- [examples/python_agent_nodes/documentation_chatbot/README.md](examples/python_agent_nodes/documentation_chatbot/README.md)
- [examples/python_agent_nodes/documentation_chatbot/__init__.py](examples/python_agent_nodes/documentation_chatbot/__init__.py)
- [examples/python_agent_nodes/documentation_chatbot/chunking.py](examples/python_agent_nodes/documentation_chatbot/chunking.py)
- [examples/python_agent_nodes/documentation_chatbot/embedding.py](examples/python_agent_nodes/documentation_chatbot/embedding.py)
- [examples/python_agent_nodes/documentation_chatbot/main.py](examples/python_agent_nodes/documentation_chatbot/main.py)
- [examples/python_agent_nodes/documentation_chatbot/schemas.py](examples/python_agent_nodes/documentation_chatbot/schemas.py)
- [sdk/python/tests/test_skill_pydantic_models.py](sdk/python/tests/test_skill_pydantic_models.py)

</details>



This section provides real-world example applications demonstrating AgentField patterns and architectures. Examples showcase practical implementations of multi-agent systems, RAG (Retrieval-Augmented Generation) pipelines, and distributed agent coordination.

For general concepts about agents, reasoners, and skills, see [Core Concepts](#1.1). For SDK-specific implementation details, see [Python SDK](#3), [TypeScript SDK](#4), or [Go SDK](#5).

## Available Examples

### Documentation Chatbot (RAG System)

The primary example is a production-ready RAG system implementing a three-agent parallel architecture for answering questions about private documentation. This example demonstrates:

- **Parallel execution patterns** — Multiple reasoners coordinating via the control plane.
- **Vector storage integration** — Using AgentField's memory system for embeddings.
- **Self-aware synthesis** — Confidence assessment and automatic refinement.
- **Two-tier storage strategy** — Document-level and chunk-level storage optimization.
- **Pydantic model validation** — Type-safe inputs and outputs across agent boundaries.

**Example Location**: [examples/python_agent_nodes/documentation_chatbot/]()

**Key Components**:
- Agent node with 4 routers organizing 7 capabilities [examples/python_agent_nodes/documentation_chatbot/main.py:34-40]().
- Skills for document ingestion [examples/python_agent_nodes/documentation_chatbot/README.md:144-146]().
- Reasoners for query planning, parallel retrieval, and answer synthesis [examples/python_agent_nodes/documentation_chatbot/README.md:148-168]().
- FastEmbed integration for local embedding generation [examples/python_agent_nodes/documentation_chatbot/embedding.py:1-30]().

For detailed documentation of this example, see:
- [Documentation Chatbot](#12.1) — Overview and architecture
- [Chatbot: Ingestion Pipeline](#12.2) — Document chunking and embedding
- [Chatbot: Query Planning](#12.3) — Multi-query generation
- [Chatbot: Parallel Retrieval](#12.4) — Concurrent search and deduplication
- [Chatbot: Self-Aware Synthesis](#12.5) — Answer generation with confidence assessment

Sources: [examples/python_agent_nodes/documentation_chatbot/README.md:1-229](), [examples/python_agent_nodes/documentation_chatbot/main.py:1-73]()

### Deep Research Agent (Recursive Planning)

The Deep Research Agent demonstrates complex task decomposition and topological execution. It uses recursive planning to break down broad research questions into a graph of atomic subtasks.

- **Recursive Planning** — Decomposes questions into hierarchical task graphs [examples/python_agent_nodes/deep_research/routers/planning.py:101-112]().
- **Topological Execution** — Executes leaf tasks in parallel and synthesizes parent tasks [examples/python_agent_nodes/deep_research/routers/planning.py:25-32]().
- **Web Search Integration** — Uses Tavily for real-time information retrieval [examples/python_agent_nodes/deep_research/routers/research.py:62-64]().

**Example Location**: [examples/python_agent_nodes/deep_research/]()

Sources: [examples/python_agent_nodes/deep_research/README.md:1-11]()

## Example Architecture Overview

The documentation chatbot demonstrates a three-stage RAG pipeline with parallel execution:

```mermaid
graph TB
    User["User Question"]
    
    subgraph "Stage 1: Query Planning"
        PlanReasoner["plan_queries reasoner"]
        QueryPlan["QueryPlan schema<br/>3-5 diverse queries"]
    end
    
    subgraph "Stage 2: Parallel Retrieval"
        ParallelReasoner["parallel_retrieve reasoner"]
        VectorSearch["AgentField Memory<br/>searchVector()"]
        DocStore["Document Store<br/>global scope"]
        Results["RetrievalResult[]<br/>deduplicated chunks"]
    end
    
    subgraph "Stage 3: Self-Aware Synthesis"
        SynthReasoner["synthesize_answer reasoner"]
        DocAnswer["DocAnswer schema<br/>answer + citations + confidence"]
        Refinement["needs_more = true?"]
    end
    
    subgraph "Skills"
        IngestSkill["ingest_folder skill"]
        ChunkUtil["chunk_markdown_text()"]
        EmbedUtil["embed_texts()"]
    end
    
    User --> PlanReasoner
    PlanReasoner --> QueryPlan
    QueryPlan --> ParallelReasoner
    
    ParallelReasoner --> VectorSearch
    VectorSearch --> Results
    ParallelReasoner --> DocStore
    
    Results --> SynthReasoner
    DocStore --> SynthReasoner
    SynthReasoner --> DocAnswer
    DocAnswer --> Refinement
    Refinement -->|"yes, max 1 iter"| PlanReasoner
    Refinement -->|no| User
    
    IngestSkill --> ChunkUtil
    ChunkUtil --> EmbedUtil
    EmbedUtil --> VectorSearch
    IngestSkill --> DocStore
```

**Architecture Pattern**: Three independent reasoners orchestrated by the control plane. Each reasoner can be called directly or as part of the orchestrated `qa_answer` or `qa_answer_with_documents` flows.

Sources: [examples/python_agent_nodes/documentation_chatbot/README.md:15-46](), [examples/python_agent_nodes/documentation_chatbot/main.py:25-73]()

## Code Entity Mapping

### Agent Registration and Routers

This diagram maps high-level concepts to the specific code entities in the Documentation Chatbot.

```mermaid
graph TB
    MainPy["examples/python_agent_nodes/documentation_chatbot/main.py"]
    AgentClass["Agent class<br/>node_id='documentation-chatbot'"]
    
    MainPy --> AgentClass
    
    subgraph "Router Organization"
        QueryRouter["query_router<br/>AgentRouter(prefix='query')"]
        IngestionRouter["ingestion_router<br/>AgentRouter(prefix='ingestion')"]
        RetrievalRouter["retrieval_router<br/>AgentRouter(prefix='retrieval')"]
        QARouter["qa_router<br/>AgentRouter(prefix='qa')"]
    end
    
    AgentClass -->|"app.include_router()"| QueryRouter
    AgentClass -->|"app.include_router()"| IngestionRouter
    AgentClass -->|"app.include_router()"| RetrievalRouter
    AgentClass -->|"app.include_router()"| QARouter
    
    subgraph "Capabilities"
        PlanQuery["@query_router.reasoner()<br/>plan_queries"]
        Ingest["@ingestion_router.skill()<br/>ingest_folder"]
        ParallelRetr["@retrieval_router.reasoner()<br/>parallel_retrieve"]
        Synth["@qa_router.reasoner()<br/>synthesize_answer"]
        QAAnswer["@qa_router.reasoner()<br/>qa_answer"]
        QADoc["@qa_router.reasoner()<br/>qa_answer_with_documents"]
    end
    
    QueryRouter --> PlanQuery
    IngestionRouter --> Ingest
    RetrievalRouter --> ParallelRetr
    QARouter --> Synth
    QARouter --> QAAnswer
    QARouter --> QADoc
```

Sources: [examples/python_agent_nodes/documentation_chatbot/main.py:25-41](), [examples/python_agent_nodes/documentation_chatbot/routers.py:1-40]()

### Data Flow Through Pydantic Schemas

```mermaid
graph LR
    subgraph "Input Schemas"
        Question["user question string"]
    end
    
    subgraph "Planning Stage"
        QueryPlanSchema["QueryPlan<br/>queries: List[str]<br/>strategy: str"]
    end
    
    subgraph "Retrieval Stage"
        RetrievalResultSchema["RetrievalResult<br/>text: str<br/>source: str<br/>score: float<br/>metadata: Dict"]
        DocumentContextSchema["DocumentContext<br/>document_key: str<br/>full_text: str<br/>matching_chunks: int<br/>relevance_score: float"]
    end
    
    subgraph "Synthesis Stage"
        CitationSchema["Citation<br/>key: str<br/>relative_path: str<br/>start_line: int<br/>end_line: int<br/>score: float"]
        DocAnswerSchema["DocAnswer<br/>answer: str<br/>citations: List[Citation]<br/>confidence: str<br/>needs_more: bool<br/>missing_topics: List[str]"]
    end
    
    subgraph "Ingestion Stage"
        DocumentChunkSchema["DocumentChunk<br/>chunk_id: str<br/>namespace: str<br/>relative_path: str<br/>text: str<br/>start_line: int<br/>end_line: int"]
        IngestReportSchema["IngestReport<br/>namespace: str<br/>file_count: int<br/>chunk_count: int"]
    end
    
    Question --> QueryPlanSchema
    QueryPlanSchema --> RetrievalResultSchema
    RetrievalResultSchema --> DocumentContextSchema
    DocumentContextSchema --> DocAnswerSchema
    RetrievalResultSchema --> CitationSchema
    CitationSchema --> DocAnswerSchema
    
    DocumentChunkSchema --> IngestReportSchema
```

Sources: [examples/python_agent_nodes/documentation_chatbot/schemas.py:1-115]()

## Storage Architecture

The documentation chatbot demonstrates AgentField's memory system capabilities with a two-tier storage pattern:

| Storage Tier | Scope | Purpose | Key Pattern | Data Format |
|--------------|-------|---------|-------------|-------------|
| Document Store | `global` | Store full document text once | `{namespace}:doc:{relative_path}` | Plain text |
| Vector Store | `global` | Store chunk embeddings and metadata | Managed by `setVector()` | Embedding + metadata JSON |

**Storage Optimization**: Full document text is stored once in regular memory. Each chunk's metadata contains a `document_key` reference pointing to the document store, avoiding 70% text duplication [examples/python_agent_nodes/documentation_chatbot/README.md:171-175]().

Sources: [examples/python_agent_nodes/documentation_chatbot/README.md:171-175]()

## Key Implementation Patterns

### Reasoner Chaining via Control Plane

The example demonstrates orchestrated reasoner execution where one reasoner's output becomes another's input. The control plane handles routing and context propagation:

1. User calls `qa_answer` or `qa_answer_with_documents` reasoner.
2. Reasoner internally calls `app.call("documentation-chatbot.plan_queries", ...)` [examples/python_agent_nodes/documentation_chatbot/README.md:17-33]().
3. Control plane routes request to `plan_queries` reasoner.
4. Result flows back to calling reasoner.

Sources: [examples/python_agent_nodes/documentation_chatbot/README.md:17-33]()

### Pydantic Model Validation

All reasoners and skills use Pydantic models for input/output validation, demonstrating type-safe agent boundaries:

- **Skills Support Pydantic Models**: Both reasoners and skills can accept Pydantic models as parameters [sdk/python/tests/test_skill_pydantic_models.py:34-40](). The SDK automatically converts JSON dictionaries to model instances [sdk/python/tests/test_skill_pydantic_models.py:50-68]().
- **Validation Points**: Input validation occurs before function execution; output validation occurs on return values.

Sources: [examples/python_agent_nodes/documentation_chatbot/schemas.py:1-115](), [sdk/python/tests/test_skill_pydantic_models.py:87-103]()

### Namespace Isolation

The example uses namespaces to isolate different documentation sets [examples/python_agent_nodes/documentation_chatbot/README.md:176-181](). All vector storage operations include namespace in metadata filtering. Memory keys use namespace prefix: `{namespace}:doc:{path}`.

Sources: [examples/python_agent_nodes/documentation_chatbot/README.md:176-181]()

### Embedding Generation with FastEmbed

The example uses FastEmbed for local, dependency-light embedding generation:

- **Key Functions**: `embed_texts()` for batch embedding and `embed_query()` for single-query embedding [examples/python_agent_nodes/documentation_chatbot/embedding.py:1-30]().
- **Warmup Pattern**: `_warmup_embeddings()` is called on agent startup to avoid cold-start latency [examples/python_agent_nodes/documentation_chatbot/main.py:43-49]().

Sources: [examples/python_agent_nodes/documentation_chatbot/embedding.py:1-30](), [examples/python_agent_nodes/documentation_chatbot/main.py:43-49]()

## Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| Parallel speedup | 3x | 3 concurrent queries vs sequential [examples/python_agent_nodes/documentation_chatbot/README.md:63]() |
| Storage reduction | 70% | Two-tier storage vs full text duplication [examples/python_agent_nodes/documentation_chatbot/README.md:174]() |
| Max refinement iterations | 1 | Prevents infinite loops [examples/python_agent_nodes/documentation_chatbot/README.md:65]() |
| Default chunk size | 1200 chars | Markdown-aware [examples/python_agent_nodes/documentation_chatbot/chunking.py:92]() |

Sources: [examples/python_agent_nodes/documentation_chatbot/README.md:63-174](), [examples/python_agent_nodes/documentation_chatbot/chunking.py:92]()

---

# Page: Documentation Chatbot

# Documentation Chatbot

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/python_agent_nodes/agentic_rag/main.py](examples/python_agent_nodes/agentic_rag/main.py)
- [examples/python_agent_nodes/agentic_rag/skills.py](examples/python_agent_nodes/agentic_rag/skills.py)
- [examples/python_agent_nodes/documentation_chatbot/README.md](examples/python_agent_nodes/documentation_chatbot/README.md)
- [examples/python_agent_nodes/documentation_chatbot/__init__.py](examples/python_agent_nodes/documentation_chatbot/__init__.py)
- [examples/python_agent_nodes/documentation_chatbot/chunking.py](examples/python_agent_nodes/documentation_chatbot/chunking.py)
- [examples/python_agent_nodes/documentation_chatbot/embedding.py](examples/python_agent_nodes/documentation_chatbot/embedding.py)
- [examples/python_agent_nodes/documentation_chatbot/main.py](examples/python_agent_nodes/documentation_chatbot/main.py)
- [examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py](examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py)
- [examples/python_agent_nodes/documentation_chatbot/product_context.py](examples/python_agent_nodes/documentation_chatbot/product_context.py)
- [examples/python_agent_nodes/documentation_chatbot/routers/__init__.py](examples/python_agent_nodes/documentation_chatbot/routers/__init__.py)
- [examples/python_agent_nodes/documentation_chatbot/routers/ingestion.py](examples/python_agent_nodes/documentation_chatbot/routers/ingestion.py)
- [examples/python_agent_nodes/documentation_chatbot/routers/qa.py](examples/python_agent_nodes/documentation_chatbot/routers/qa.py)
- [examples/python_agent_nodes/documentation_chatbot/routers/query_planning.py](examples/python_agent_nodes/documentation_chatbot/routers/query_planning.py)
- [examples/python_agent_nodes/documentation_chatbot/routers/retrieval.py](examples/python_agent_nodes/documentation_chatbot/routers/retrieval.py)
- [examples/python_agent_nodes/documentation_chatbot/schemas.py](examples/python_agent_nodes/documentation_chatbot/schemas.py)
- [examples/python_agent_nodes/hello_world_rag/main.py](examples/python_agent_nodes/hello_world_rag/main.py)
- [examples/python_agent_nodes/hello_world_rag/test_pydantic_skill.py](examples/python_agent_nodes/hello_world_rag/test_pydantic_skill.py)
- [sdk/python/tests/test_skill_pydantic_models.py](sdk/python/tests/test_skill_pydantic_models.py)

</details>



## Purpose and Scope

The Documentation Chatbot is a production-ready Retrieval-Augmented Generation (RAG) system implemented as an AgentField node. It answers complex questions about documentation folders without hallucinations by utilizing a 3-agent parallel architecture. The system ingests local documentation, creates high-quality embeddings with precise line-level metadata, and produces answers with inline citations (e.g., `[A]`).

Key features include:
- **3-Reasoner Parallel Architecture**: Decoupled query planning, retrieval, and synthesis.
- **Self-Aware Synthesis**: Automatic confidence assessment and single-iteration refinement.
- **Two-Tier Storage**: Efficient memory management storing full documents once and referencing them via chunk vectors.
- **Document-Level Retrieval**: Aggregates chunks into full document context for superior comprehension.

**Sources:** [examples/python_agent_nodes/documentation_chatbot/README.md:1-14](), [examples/python_agent_nodes/documentation_chatbot/main.py:58-67]()

## System Architecture

The chatbot implements a multi-stage pipeline where reasoners and skills coordinate through the AgentField control plane.

### 3-Reasoner Parallel Design

```mermaid
graph TB
    User["User Question"]
    
    subgraph "Query Planning Stage"
        QueryPlanner["plan_queries reasoner<br/>routers/query_planning.py"]
        QueryPlan["QueryPlan<br/>{queries: List[str], strategy: str}"]
    end
    
    subgraph "Parallel Retrieval Stage"
        ParallelRetriever["parallel_retrieve reasoner<br/>routers/retrieval.py"]
        VectorSearch["Memory.similarity_search()"]
        ChunkResults["List[RetrievalResult]"]
    end
    
    subgraph "Synthesis Stage"
        Synthesizer["synthesize_answer reasoner<br/>routers/qa.py"]
        ConfidenceCheck["Self-Assessment<br/>{confidence, needs_more, missing_topics}"]
        FinalAnswer["DocAnswer<br/>{answer, citations, confidence}"]
    end
    
    subgraph "Orchestration Layer"
        QAOrch["qa_answer reasoner<br/>routers/qa.py"]
    end
    
    User --> QAOrch
    QAOrch --> QueryPlanner
    QueryPlanner --> QueryPlan
    QueryPlan --> ParallelRetriever
    ParallelRetriever --> VectorSearch
    VectorSearch --> ChunkResults
    ChunkResults --> Synthesizer
    Synthesizer --> ConfidenceCheck
    
    ConfidenceCheck -->|"needs_more=True"| QueryPlanner
    ConfidenceCheck -->|"confidence=high"| FinalAnswer
    FinalAnswer --> User
```

**Sources:** [examples/python_agent_nodes/documentation_chatbot/README.md:17-34](), [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:164-210]()

### Component Interaction Flow

```mermaid
sequenceDiagram
    participant User
    participant Agent as "documentation-chatbot"
    participant Memory as "MemoryInterface"
    
    Note over Agent: Startup
    Agent->>Agent: _warmup_embeddings()
    
    User->>Agent: qa_answer(question)
    Agent->>Agent: plan_queries(question)
    Note right of Agent: Generates 3-5 queries
    
    Agent->>Agent: parallel_retrieve(queries)
    par For each query
        Agent->>Memory: global_scope.similarity_search()
    end
    Memory-->>Agent: Raw Hits
    Agent->>Agent: deduplicate_results()
    
    Agent->>Agent: synthesize_answer(results)
    Note right of Agent: Self-assesses confidence
    
    alt needs_more is True
        Agent->>Agent: plan_queries(missing_topics)
        Note over Agent: One refinement iteration
    end
    
    Agent-->>User: DocAnswer
```

**Sources:** [examples/python_agent_nodes/documentation_chatbot/main.py:43-50](), [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:176-200](), [examples/python_agent_nodes/documentation_chatbot/routers/retrieval.py:60-89]()

## Storage Architecture

### Two-Tier Storage Strategy

To optimize storage, the agent avoids duplicating text within vector metadata by using a cross-reference pattern.

1.  **Tier 1 (Full Documents)**: Stored in regular key-value memory using the key `{namespace}:doc:{relative_path}`.
2.  **Tier 2 (Chunk Vectors)**: Stored in vector memory with metadata containing a `document_key` pointer to Tier 1.

```mermaid
graph LR
    subgraph "Tier 1: Document Storage"
        DocStore["Memory.set()<br/>key: {namespace}:doc:{path}"]
        DocData["{full_text, relative_path, file_size}"]
    end
    
    subgraph "Tier 2: Vector Storage"
        VecStore["Memory.set_vector()"]
        VecMeta["{text_chunk, document_key, start_line, end_line}"]
    end
    
    DocStore --- DocData
    VecStore --- VecMeta
    VecMeta -.->|"references"| DocData
```

**Sources:** [examples/python_agent_nodes/documentation_chatbot/routers/ingestion.py:94-134](), [examples/python_agent_nodes/documentation_chatbot/README.md:171-175]()

## Ingestion Pipeline

The ingestion pipeline handles document discovery, sanitization, chunking, and indexing.

### Document Processing Logic

| Function | File:Lines | Purpose |
| :--- | :--- | :--- |
| `ingest_folder` | [routers/ingestion.py:54-146]() | Main orchestration of the ingestion process. |
| `chunk_markdown_text` | [chunking.py:87-133]() | Chunks text while tracking headings and line numbers. |
| `_collect_headings` | [chunking.py:54-63]() | Extracts markdown headers for section-aware metadata. |
| `_sanitize_text` | [chunking.py:26-34]() | Strips null bytes (`\x00`) for database compatibility. |
| `embed_texts` | [embedding.py:18-23]() | Batch generates embeddings using `fastembed`. |
| `clear_namespace` | [routers/ingestion.py:45-51]() | Skill to wipe a namespace via control plane API. |

### Chunking and Metadata

The `chunk_markdown_text` function uses a sliding window with overlap. It utilizes `bisect` to efficiently map character offsets to line numbers and section headers.

```mermaid
graph TB
    Raw["Raw Markdown Text"]
    Sanitize["_sanitize_text()"]
    Index["_newline_positions() & _collect_headings()"]
    Window["Sliding Window Chunker"]
    
    subgraph "Metadata Mapping"
        Line["_char_to_line()"]
        Sect["_find_section()"]
    end
    
    Raw --> Sanitize
    Sanitize --> Index
    Index --> Window
    Window --> Line
    Window --> Sect
    Line --> Chunk["DocumentChunk Object"]
    Sect --> Chunk
```

**Sources:** [examples/python_agent_nodes/documentation_chatbot/chunking.py:87-133](), [examples/python_agent_nodes/documentation_chatbot/chunking.py:70-84]()

## Query Planning and Retrieval

### Query Planning (`plan_queries`)
This reasoner uses `PRODUCT_CONTEXT` to understand domain-specific terms (e.g., mapping "identity" to "DIDs/VCs") and generates 3-5 diverse queries using strategies like `broad`, `specific`, or `mixed`.

**Sources:** [examples/python_agent_nodes/documentation_chatbot/routers/query_planning.py:14-48](), [examples/python_agent_nodes/documentation_chatbot/product_context.py:3-146]()

### Parallel Retrieval (`parallel_retrieve`)
Executes `MemoryInterface.similarity_search` concurrently for all planned queries using `asyncio.gather`. Results are then deduplicated based on their source (file path and line range).

**Sources:** [examples/python_agent_nodes/documentation_chatbot/routers/retrieval.py:60-89](), [examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py:47-57]()

## Synthesis and Self-Assessment

### Synthesis Reasoner (`synthesize_answer`)
The synthesizer generates a markdown response. It is strictly instructed to use inline citations like `[A]` and leave the `citations` array empty for automatic injection by the system.

**Sources:** [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:26-160]()

### Self-Assessment Logic
The `DocAnswer` schema requires the LLM to evaluate its own output:
- **Confidence**: `high`, `partial`, or `insufficient`.
- **needs_more**: Boolean flag triggering refinement.
- **missing_topics**: Specific information gaps to target in the next retrieval step.

**Sources:** [examples/python_agent_nodes/documentation_chatbot/schemas.py:96-115](), [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:114-128]()

## Document-Aware Retrieval

The system supports an advanced mode, `qa_answer_with_documents`, which aggregates individual chunks back into full document contexts before synthesis.

| Component | File:Lines | Purpose |
| :--- | :--- | :--- |
| `aggregate_chunks_to_documents` | [pipeline_utils.py:113-176]() | Groups chunks by `document_key` and fetches full text. |
| `calculate_document_score` | [pipeline_utils.py:102-110]() | Scores documents based on average chunk score + coverage boost. |
| `format_documents_for_synthesis` | [pipeline_utils.py:179-190]() | Prepares full document text for the LLM prompt. |

**Sources:** [examples/python_agent_nodes/documentation_chatbot/README.md:42-47](), [examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py:102-176]()

## Data Models

### Key Schemas

| Schema | Purpose | Key Fields |
| :--- | :--- | :--- |
| `DocumentChunk` | Ingestion unit | `chunk_id`, `text`, `start_line`, `end_line`, `section` |
| `QueryPlan` | Retrieval plan | `queries`, `strategy` |
| `RetrievalResult` | Search hit | `text`, `source`, `score`, `metadata` |
| `DocAnswer` | Final response | `answer`, `citations`, `confidence`, `needs_more` |
| `Citation` | Source metadata | `key`, `relative_path`, `preview`, `score` |

**Sources:** [examples/python_agent_nodes/documentation_chatbot/schemas.py:13-115]()

## Agent Configuration

The agent is composed using `AgentRouter` modules for clean separation of concerns.

```python
app = Agent(
    node_id="documentation-chatbot",
    agentfield_server=f"{os.getenv('AGENTFIELD_SERVER')}",
    api_key=os.getenv("AGENTFIELD_API_KEY"),
    ai_config=AIConfig(
        model=os.getenv("AI_MODEL", "openrouter/openai/gpt-4o-mini"),
    ),
)

app.include_router(query_router)
app.include_router(ingestion_router)
app.include_router(retrieval_router)
app.include_router(qa_router)
```

**Sources:** [examples/python_agent_nodes/documentation_chatbot/main.py:25-40]()

---

# Page: Chatbot: Ingestion Pipeline

# Chatbot: Ingestion Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/python_agent_nodes/agentic_rag/main.py](examples/python_agent_nodes/agentic_rag/main.py)
- [examples/python_agent_nodes/agentic_rag/skills.py](examples/python_agent_nodes/agentic_rag/skills.py)
- [examples/python_agent_nodes/documentation_chatbot/README.md](examples/python_agent_nodes/documentation_chatbot/README.md)
- [examples/python_agent_nodes/documentation_chatbot/__init__.py](examples/python_agent_nodes/documentation_chatbot/__init__.py)
- [examples/python_agent_nodes/documentation_chatbot/chunking.py](examples/python_agent_nodes/documentation_chatbot/chunking.py)
- [examples/python_agent_nodes/documentation_chatbot/embedding.py](examples/python_agent_nodes/documentation_chatbot/embedding.py)
- [examples/python_agent_nodes/documentation_chatbot/main.py](examples/python_agent_nodes/documentation_chatbot/main.py)
- [examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py](examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py)
- [examples/python_agent_nodes/documentation_chatbot/product_context.py](examples/python_agent_nodes/documentation_chatbot/product_context.py)
- [examples/python_agent_nodes/documentation_chatbot/routers/__init__.py](examples/python_agent_nodes/documentation_chatbot/routers/__init__.py)
- [examples/python_agent_nodes/documentation_chatbot/routers/ingestion.py](examples/python_agent_nodes/documentation_chatbot/routers/ingestion.py)
- [examples/python_agent_nodes/documentation_chatbot/routers/qa.py](examples/python_agent_nodes/documentation_chatbot/routers/qa.py)
- [examples/python_agent_nodes/documentation_chatbot/routers/query_planning.py](examples/python_agent_nodes/documentation_chatbot/routers/query_planning.py)
- [examples/python_agent_nodes/documentation_chatbot/routers/retrieval.py](examples/python_agent_nodes/documentation_chatbot/routers/retrieval.py)
- [examples/python_agent_nodes/documentation_chatbot/schemas.py](examples/python_agent_nodes/documentation_chatbot/schemas.py)
- [examples/python_agent_nodes/hello_world_rag/main.py](examples/python_agent_nodes/hello_world_rag/main.py)
- [examples/python_agent_nodes/hello_world_rag/test_pydantic_skill.py](examples/python_agent_nodes/hello_world_rag/test_pydantic_skill.py)
- [sdk/python/tests/test_skill_pydantic_models.py](sdk/python/tests/test_skill_pydantic_models.py)

</details>



## Purpose and Scope

This document describes the ingestion pipeline for the Documentation Chatbot example, which transforms raw documentation files into searchable, citation-ready chunks stored in AgentField's memory system. The pipeline implements a two-tier storage strategy that eliminates text duplication while preserving precise source attribution through line numbers and section headings.

The ingestion process is handled primarily by the `ingestion_router` [examples/python_agent_nodes/documentation_chatbot/routers/ingestion.py:20](), which coordinates file discovery, chunking, embedding, and storage.

---

## Architecture Overview

The ingestion pipeline consists of five sequential stages that transform documentation files into vector-searchable chunks with full provenance metadata:

```mermaid
graph LR
    Discovery["File Discovery<br/>(is_supported_file)"]
    Reading["Text Reading<br/>(read_text)"]
    Chunking["Markdown-Aware<br/>Chunking<br/>(chunk_markdown_text)"]
    Embedding["Embedding Generation<br/>(embed_texts)"]
    Storage["Two-Tier Storage<br/>(memory.set + setVector)"]
    
    Discovery --> Reading
    Reading --> Chunking
    Chunking --> Embedding
    Embedding --> Storage
    
    Storage --> Tier1["Tier 1: Document Storage<br/>namespace:doc:path → full_text"]
    Storage --> Tier2["Tier 2: Vector Storage<br/>chunk vectors + metadata"]
    
    Tier2 -.->|"references via document_key"| Tier1
```

**Sources:** [examples/python_agent_nodes/documentation_chatbot/README.md:169-174](), [examples/python_agent_nodes/documentation_chatbot/routers/ingestion.py:54-146]()

The pipeline is exposed as a reasoner `ingest_folder` [examples/python_agent_nodes/documentation_chatbot/routers/ingestion.py:55]() on the documentation chatbot agent and is invoked via the control plane's execute API.

---

## Two-Tier Storage Strategy

The ingestion pipeline implements a storage architecture that stores full documents once in regular memory while chunk vectors reference them via keys. This achieves approximately 70% storage savings compared to duplicating full text in every chunk's metadata [examples/python_agent_nodes/documentation_chatbot/README.md:171-174]().

### Storage Tiers

| Tier | Storage Type | Key Format | Content | Purpose |
|------|--------------|------------|---------|---------|
| **Tier 1** | Regular Memory | `{namespace}:doc:{relative_path}` | Complete document text | Single source of truth for document content |
| **Tier 2** | Vector Memory | Embedding vectors | Chunk metadata + `document_key` reference | Semantic search with provenance |

### Storage Operations

```mermaid
graph TB
    subgraph "Tier 1: Document Storage (app.memory.set)"
        DocKey["Key: 'docs:doc:api/auth.md'"]
        DocContent["Value: Full document text<br/>(multi-kilobyte string)"]
        DocKey --> DocContent
    end
    
    subgraph "Tier 2: Chunk Vector Storage (app.memory.set_vector)"
        ChunkVector["Embedding Vector<br/>(384 dimensions)"]
        ChunkMeta["Metadata JSON"]
        
        ChunkMeta --> RelPath["relative_path: 'api/auth.md'"]
        ChunkMeta --> Section["section: 'OAuth Flow'"]
        ChunkMeta --> Lines["start_line: 42<br/>end_line: 58"]
        ChunkMeta --> DocRef["document_key: 'docs:doc:api/auth.md'"]
        
        ChunkVector -.->|"similarity search"| ChunkMeta
    end
    
    ChunkMeta -.->|"references"| DocKey
```

**Sources:** [examples/python_agent_nodes/documentation_chatbot/README.md:171-174](), [examples/python_agent_nodes/documentation_chatbot/routers/ingestion.py:94-134]()

When a query matches chunks, the system:
1. Retrieves chunk metadata via vector search.
2. Uses `document_key` to fetch the full document from Tier 1 [examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py:137-142]().
3. Aggregates chunks to provide complete document context for synthesis [examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py:113-117]().

---

## File Discovery and Filtering

The pipeline discovers documentation files by recursively scanning a folder and filtering based on file extensions.

### Supported File Types

The `is_supported_file()` function filters files based on extension:

```python
SUPPORTED_EXTENSIONS = {".md", ".mdx", ".rst", ".txt"}
```

**Sources:** [examples/python_agent_nodes/documentation_chatbot/chunking.py:16-23]()

### Discovery Process

```mermaid
graph TD
    Start["Input: folder_path"]
    Glob["glob_pattern<br/>(default: '**/*')"]
    Filter["is_supported_file()<br/>check extension"]
    Collect["Collect Path objects"]
    
    Start --> Glob
    Glob --> Filter
    Filter -->|"extension in SUPPORTED_EXTENSIONS"| Collect
    Filter -->|"unsupported"| Skip["Skip file"]
```

**Sources:** [examples/python_agent_nodes/documentation_chatbot/chunking.py:20-23](), [examples/python_agent_nodes/documentation_chatbot/routers/ingestion.py:70-76]()

The discovery logic skips directories, symlinks, and unsupported file types. Skipped files are tracked in the `IngestReport.skipped_files` list [examples/python_agent_nodes/documentation_chatbot/routers/ingestion.py:76]().

---

## Text Processing and Sanitization

### UTF-8 Reading with Fallback

The `read_text()` function implements a two-stage encoding strategy to handle edge cases:

1. **Primary:** Attempt UTF-8 decoding.
2. **Fallback:** Use `latin-1` encoding if UTF-8 fails [examples/python_agent_nodes/documentation_chatbot/chunking.py:40-43]().

**Sources:** [examples/python_agent_nodes/documentation_chatbot/chunking.py:37-45]()

### Null Byte Sanitization

The `_sanitize_text()` function removes null bytes (`\x00`) that PostgreSQL's JSONB columns cannot store:

```python
def _sanitize_text(text: str) -> str:
    return text.replace("\x00", "")
```

**Sources:** [examples/python_agent_nodes/documentation_chatbot/chunking.py:26-34]()

---

## Markdown-Aware Chunking

The `chunk_markdown_text()` function implements a sliding window chunker that preserves document structure and tracks precise source locations.

### Chunking Algorithm

```mermaid
graph TB
    Input["Input: full document text"]
    
    Headings["_collect_headings()<br/>Parse markdown headers<br/>(# ## ### etc)"]
    Newlines["_newline_positions()<br/>Build line index"]
    
    Window["Sliding window<br/>size: chunk_size<br/>stride: chunk_size - overlap"]
    
    Metadata["For each chunk:<br/>- _char_to_line() → start/end lines<br/>- _find_section() → heading context"]
    
    Output["DocumentChunk objects<br/>with full metadata"]
    
    Input --> Headings
    Input --> Newlines
    Input --> Window
    
    Headings --> Metadata
    Newlines --> Metadata
    Window --> Metadata
    
    Metadata --> Output
```

**Sources:** [examples/python_agent_nodes/documentation_chatbot/chunking.py:87-133]()

### Metadata Extraction

The chunking process extracts metadata used for citation and ranking:

| Metadata Type | Extraction Function | Purpose |
|--------------|-------------------|---------|
| **Line numbers** | `_char_to_line()` | Precise source attribution for citations [examples/python_agent_nodes/documentation_chatbot/chunking.py:70-74]() |
| **Section headings** | `_find_section()` | Contextual information for relevance [examples/python_agent_nodes/documentation_chatbot/chunking.py:77-84]() |
| **Character positions** | `_newline_positions()` | Internal mapping for line calculation [examples/python_agent_nodes/documentation_chatbot/chunking.py:66-67]() |

#### Line Number Calculation

The `_char_to_line()` function uses binary search (`bisect.bisect_right()`) on a pre-computed newline index for O(log n) line lookup [examples/python_agent_nodes/documentation_chatbot/chunking.py:73-74]().

#### Section Detection

The `_find_section()` function finds the most recent heading before a chunk's start position using the `_HEADING_PATTERN` regex [examples/python_agent_nodes/documentation_chatbot/chunking.py:17-18]().

### Chunk ID Generation

Each chunk receives a stable identifier combining the file path and sequential index:

```python
chunk_id = f"{relative_path}#chunk-{index}"
```

**Sources:** [examples/python_agent_nodes/documentation_chatbot/chunking.py:118]()

---

## Embedding Generation

The pipeline uses `fastembed` for local embedding generation without external API dependencies [examples/python_agent_nodes/documentation_chatbot/README.md:13]().

### Model Configuration

The embedding model is typically configured via environment variables and loaded through `embedding.py` [examples/python_agent_nodes/documentation_chatbot/embedding.py:12-29]().

### Warmup Strategy

The agent warms up the embedding model on startup to avoid cold-start latency:

```python
def _warmup_embeddings() -> None:
    """Warm up the embedding model on startup."""
    try:
        embed_texts(["doc-chatbot warmup"])
        log_info("FastEmbed model warmed up for documentation chatbot")
```

**Sources:** [examples/python_agent_nodes/documentation_chatbot/main.py:43-49]()

---

## Storage Operations and Memory Scopes

### Memory Scope Selection

The pipeline stores all data in the **global memory scope** to ensure chunks are accessible across all workflows and agents [examples/python_agent_nodes/documentation_chatbot/routers/ingestion.py:83]().

### Storage Flow

```mermaid
sequenceDiagram
    participant Reasoner as "ingest_folder reasoner"
    participant Memory as "app.memory.global_scope"
    participant Storage as "Control Plane Storage"
    
    Note over Reasoner: For each document
    
    Reasoner->>Memory: set(document_key, doc_data)
    Memory->>Storage: Tier 1: Key-Value storage
    
    Note over Reasoner: For each chunk
    
    Reasoner->>Memory: set_vector(vector_key, embedding, metadata)
    Memory->>Storage: Tier 2: Vector storage
    
    Note over Storage: Metadata includes document_key<br/>referencing Tier 1 document
```

**Sources:** [examples/python_agent_nodes/documentation_chatbot/routers/ingestion.py:94-134]()

### DocumentChunk Schema

The `DocumentChunk` Pydantic model defines the metadata structure:

| Field | Type | Description |
|-------|------|-------------|
| `chunk_id` | `str` | Unique identifier [examples/python_agent_nodes/documentation_chatbot/schemas.py:16]() |
| `namespace` | `str` | Logical corpus for isolation [examples/python_agent_nodes/documentation_chatbot/schemas.py:17]() |
| `relative_path` | `str` | File path relative to ingestion root [examples/python_agent_nodes/documentation_chatbot/schemas.py:18]() |
| `section` | `Optional[str]` | Markdown heading context [examples/python_agent_nodes/documentation_chatbot/schemas.py:19]() |
| `text` | `str` | Chunk content [examples/python_agent_nodes/documentation_chatbot/schemas.py:20]() |
| `start_line` | `int` | Starting line number [examples/python_agent_nodes/documentation_chatbot/schemas.py:21]() |
| `end_line` | `int` | Ending line number [examples/python_agent_nodes/documentation_chatbot/schemas.py:22]() |

---

## Ingestion Reasoner Interface

The `ingest_folder` reasoner coordinates the entire pipeline.

### Request Parameters

| Parameter | Type | Default | Purpose |
|-----------|------|---------|---------|
| `folder_path` | `str` | - | Path to documentation folder |
| `namespace` | `str` | `"website-docs"` | Logical corpus identifier |
| `glob_pattern`| `str` | `"**/*"` | File discovery pattern |
| `chunk_size`  | `int` | `1200` | Max characters per chunk |
| `chunk_overlap`| `int` | `250` | Overlap between chunks |

**Sources:** [examples/python_agent_nodes/documentation_chatbot/routers/ingestion.py:55-61]()

### Response Schema

The `IngestReport` model summarizes the operation:

| Field | Type | Description |
|-------|------|-------------|
| `namespace` | `str` | Corpus identifier |
| `file_count` | `int` | Number of files processed |
| `chunk_count` | `int` | Total chunks created |
| `skipped_files`| `List[str]` | Files skipped (unsupported types) |

**Sources:** [examples/python_agent_nodes/documentation_chatbot/schemas.py:25-31]()

### Namespace Management

Before re-indexing, the `clear_namespace` skill can be used to wipe existing vectors via the control plane's `/api/v1/memory/vector/namespace` endpoint [examples/python_agent_nodes/documentation_chatbot/routers/ingestion.py:38-51]().

---

# Page: Chatbot: Query Planning

# Chatbot: Query Planning

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/python_agent_nodes/agentic_rag/main.py](examples/python_agent_nodes/agentic_rag/main.py)
- [examples/python_agent_nodes/agentic_rag/skills.py](examples/python_agent_nodes/agentic_rag/skills.py)
- [examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py](examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py)
- [examples/python_agent_nodes/documentation_chatbot/product_context.py](examples/python_agent_nodes/documentation_chatbot/product_context.py)
- [examples/python_agent_nodes/documentation_chatbot/routers/__init__.py](examples/python_agent_nodes/documentation_chatbot/routers/__init__.py)
- [examples/python_agent_nodes/documentation_chatbot/routers/ingestion.py](examples/python_agent_nodes/documentation_chatbot/routers/ingestion.py)
- [examples/python_agent_nodes/documentation_chatbot/routers/qa.py](examples/python_agent_nodes/documentation_chatbot/routers/qa.py)
- [examples/python_agent_nodes/documentation_chatbot/routers/query_planning.py](examples/python_agent_nodes/documentation_chatbot/routers/query_planning.py)
- [examples/python_agent_nodes/documentation_chatbot/routers/retrieval.py](examples/python_agent_nodes/documentation_chatbot/routers/retrieval.py)
- [examples/python_agent_nodes/hello_world_rag/main.py](examples/python_agent_nodes/hello_world_rag/main.py)
- [examples/python_agent_nodes/hello_world_rag/test_pydantic_skill.py](examples/python_agent_nodes/hello_world_rag/test_pydantic_skill.py)

</details>



## Purpose and Scope

This page documents the **query planning** component of the documentation chatbot example. This component transforms a single user question into multiple diverse search queries to maximize retrieval coverage across the documentation corpus. It is the first stage in the 3-reasoner parallel RAG architecture used by the AgentField documentation assistant.

For the complete system architecture, see [Documentation Chatbot](). For subsequent pipeline stages, see [Parallel Retrieval]() and [Self-Aware Synthesis]().

**Sources:** [examples/python_agent_nodes/documentation_chatbot/routers/query_planning.py:1-49](), [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:174-179]()

---

## Overview

Query planning solves a fundamental problem in retrieval-augmented generation: **a single user question often requires multiple search perspectives to find all relevant documentation**. Instead of executing one vector search, the query planner generates 3-5 semantically diverse queries that explore different terminology, aspects, and angles of the user's intent.

### Why Query Planning Matters

Consider the user question: *"How does identity work?"*

A naive single-query approach might miss documents that:
- Use alternative terminology ("DIDs", "Verifiable Credentials", "authentication") [examples/python_agent_nodes/documentation_chatbot/product_context.py:135-135]()
- Cover specific implementation details ("W3C standards", "cryptographic signatures") [examples/python_agent_nodes/documentation_chatbot/product_context.py:45-51]()
- Discuss related concepts ("audit trails", "trust models") [examples/python_agent_nodes/documentation_chatbot/product_context.py:50-51]()

The query planner systematically generates these variations using product-specific context.

**Sources:** [examples/python_agent_nodes/documentation_chatbot/routers/query_planning.py:19-38](), [examples/python_agent_nodes/documentation_chatbot/product_context.py:132-146]()

---

## Architecture Position

The query planner is implemented as a **reasoner** (not a skill) because it requires LLM intelligence to analyze the question and generate diverse reformulations. It is organized within an `AgentRouter` with the prefix `"query"`.

### Query Planning in the RAG Flow

```mermaid
graph LR
    User["User Question:<br/>String"]
    PlanQ["plan_queries<br/>reasoner"]
    Plan["QueryPlan<br/>schema"]
    Retrieve["parallel_retrieve<br/>reasoner"]
    
    User -->|"question"| PlanQ
    PlanQ -->|"generates"| Plan
    Plan -->|"queries: List[str]"| Retrieve
    
    style PlanQ stroke-dasharray: 5 5
```

**Query Planning Position**
The `plan_queries` reasoner receives the raw user question and outputs a structured `QueryPlan` containing 3-5 diverse search queries. In the main QA orchestrator, this result is then passed to `parallel_retrieve`.

**Sources:** [examples/python_agent_nodes/documentation_chatbot/routers/query_planning.py:10-15](), [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:176-186]()

---

## The QueryPlan Schema

The query planner outputs a structured Pydantic model that encapsulates both the generated queries and the diversity strategy used.

### Schema Definition

```mermaid
classDiagram
    class QueryPlan {
        +List~str~ queries
        +str strategy
    }
    
    note for QueryPlan "Pydantic model used in<br/>routers/query_planning.py:14"
```

**QueryPlan Data Model**

| Field | Type | Description |
|-------|------|-------------|
| `queries` | `List[str]` | 3-5 semantically diverse search queries covering different angles. |
| `strategy` | `str` | Query diversity approach used: `'broad'`, `'specific'`, or `'mixed'`. |

**Sources:** [examples/python_agent_nodes/documentation_chatbot/schemas.py:1-21](), [examples/python_agent_nodes/documentation_chatbot/routers/query_planning.py:6-15]()

---

## Query Generation Strategies

The `strategy` field documents the approach used to generate diverse queries, enabling the system to track how the search space was explored.

### Strategy Types

**1. Broad Strategy**
- **Purpose:** General exploration to maximize coverage across the documentation corpus. [examples/python_agent_nodes/documentation_chatbot/routers/query_planning.py:44-45]()
- **Characteristics:** Wide semantic variation, different terminology domains.

**2. Specific Strategy**
- **Purpose:** Targeted search for precise technical details. [examples/python_agent_nodes/documentation_chatbot/routers/query_planning.py:44-45]()
- **Characteristics:** Narrow semantic range, implementation-focused (e.g., specific API methods or configuration keys).

**3. Mixed Strategy**
- **Purpose:** Balance between broad coverage and specific details. [examples/python_agent_nodes/documentation_chatbot/routers/query_planning.py:45-46]()
- **Characteristics:** Combination of high-level architectural queries and low-level implementation queries.

**Sources:** [examples/python_agent_nodes/documentation_chatbot/routers/query_planning.py:43-46]()

---

## Reasoner Implementation

The `plan_queries` reasoner is registered on the `query_router`. It uses the `app.ai()` method (via the router) to perform a structured LLM call.

### Prompt Engineering and Context

The reasoner is provided with the `PRODUCT_CONTEXT`, which includes a "Search Term Relationships" section. This allows the AI to map colloquial terms to technical system names:
- "Identity" → DIDs, Verifiable Credentials. [examples/python_agent_nodes/documentation_chatbot/product_context.py:135-135]()
- "Functions" → Reasoners, Skills. [examples/python_agent_nodes/documentation_chatbot/product_context.py:141-141]()
- "State" → Memory, Scopes. [examples/python_agent_nodes/documentation_chatbot/product_context.py:136-136]()

### Diversity Guidelines

The system prompt enforces five core diversity strategies:
1. **Terminology:** Use different synonyms and product-specific terms. [examples/python_agent_nodes/documentation_chatbot/routers/query_planning.py:27-27]()
2. **Aspects:** Cover setup, usage, troubleshooting, and configuration. [examples/python_agent_nodes/documentation_chatbot/routers/query_planning.py:28-28]()
3. **Range:** Move from broad concepts to specific terms. [examples/python_agent_nodes/documentation_chatbot/routers/query_planning.py:29-29]()
4. **Relationships:** Include related concepts using the search term mapping. [examples/python_agent_nodes/documentation_chatbot/routers/query_planning.py:30-30]()
5. **Non-redundancy:** Each query must target a unique angle. [examples/python_agent_nodes/documentation_chatbot/routers/query_planning.py:31-31]()

**Sources:** [examples/python_agent_nodes/documentation_chatbot/routers/query_planning.py:14-48](), [examples/python_agent_nodes/documentation_chatbot/product_context.py:132-146]()

---

## Code Entity Mapping

The following diagram maps the logical Query Planning process to the specific code entities in the `documentation_chatbot` example.

```mermaid
graph TD
    subgraph "Natural Language Space"
        UserQ["User Question"]
    end

    subgraph "Code Entity Space"
        Router["AgentRouter(prefix='query')<br/>routers/query_planning.py:10"]
        Func["plan_queries()<br/>routers/query_planning.py:14"]
        Schema["QueryPlan<br/>schemas.py"]
        AI["router.ai()<br/>routers/query_planning.py:17"]
    end

    UserQ --> Func
    Func --> AI
    AI --> Schema
    Schema -->|"List[str]"| ParallelRetrieve["parallel_retrieve()<br/>routers/retrieval.py:60"]
```

**Sources:** [examples/python_agent_nodes/documentation_chatbot/routers/query_planning.py:10-17](), [examples/python_agent_nodes/documentation_chatbot/routers/retrieval.py:60-65]()

---

## Integration with Agent Router

The query planner is exposed as part of the agent's API via the `query_router`. Because the router uses `prefix="query"`, the internal function `plan_queries` is exposed to the Control Plane as `query_plan_queries`.

### Execution Flow

```mermaid
sequenceDiagram
    participant CP as "Control Plane"
    participant Agent as "Agent Node"
    participant LLM as "AI Provider"
    
    CP->>Agent: POST /execute (query_plan_queries)
    Agent->>Agent: plan_queries(question)
    Agent->>LLM: generate(system_prompt, user_prompt, schema=QueryPlan)
    LLM-->>Agent: JSON (QueryPlan)
    Agent-->>CP: 200 OK (QueryPlan)
```

**Sources:** [examples/python_agent_nodes/documentation_chatbot/routers/query_planning.py:10-14](), [examples/python_agent_nodes/documentation_chatbot/product_context.py:59-62]()

---

## Query Diversity Techniques

The reasoner is instructed to generate queries across multiple "Query Types" to ensure a multi-faceted search:

| Query Type | Purpose | Example |
|-----------|---------|---------|
| **How-to** | Procedural steps | "how to install AgentField" |
| **Concept** | Architectural understanding | "AgentField architecture" |
| **Troubleshooting** | Error resolution | "DID registration error" |
| **Configuration** | Settings and environment | "configure PostgreSQL storage" |
| **API/Reference** | Technical specifications | "app.ai method parameters" |
| **Comparison** | Trade-offs | "reasoners vs skills" |

**Sources:** [examples/python_agent_nodes/documentation_chatbot/routers/query_planning.py:33-38]()

---

## Summary

The query planning reasoner acts as the "intelligence gate" for the RAG pipeline. By expanding a single user question into a `QueryPlan` of 3-5 diverse queries, it mitigates the risk of retrieval failure due to terminology mismatch or narrow semantic focus. It leverages the `PRODUCT_CONTEXT` to ensure that generated queries use the precise technical language expected by the vector database.

**Sources:** [examples/python_agent_nodes/documentation_chatbot/routers/query_planning.py:1-49](), [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:174-180]()

---

# Page: Chatbot: Parallel Retrieval

# Chatbot: Parallel Retrieval

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/python_agent_nodes/agentic_rag/main.py](examples/python_agent_nodes/agentic_rag/main.py)
- [examples/python_agent_nodes/agentic_rag/skills.py](examples/python_agent_nodes/agentic_rag/skills.py)
- [examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py](examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py)
- [examples/python_agent_nodes/documentation_chatbot/product_context.py](examples/python_agent_nodes/documentation_chatbot/product_context.py)
- [examples/python_agent_nodes/documentation_chatbot/routers/__init__.py](examples/python_agent_nodes/documentation_chatbot/routers/__init__.py)
- [examples/python_agent_nodes/documentation_chatbot/routers/ingestion.py](examples/python_agent_nodes/documentation_chatbot/routers/ingestion.py)
- [examples/python_agent_nodes/documentation_chatbot/routers/qa.py](examples/python_agent_nodes/documentation_chatbot/routers/qa.py)
- [examples/python_agent_nodes/documentation_chatbot/routers/query_planning.py](examples/python_agent_nodes/documentation_chatbot/routers/query_planning.py)
- [examples/python_agent_nodes/documentation_chatbot/routers/retrieval.py](examples/python_agent_nodes/documentation_chatbot/routers/retrieval.py)
- [examples/python_agent_nodes/hello_world_rag/main.py](examples/python_agent_nodes/hello_world_rag/main.py)
- [examples/python_agent_nodes/hello_world_rag/test_pydantic_skill.py](examples/python_agent_nodes/hello_world_rag/test_pydantic_skill.py)

</details>



## Purpose and Scope

This page documents the parallel retrieval component of the documentation chatbot example, specifically the `parallel_retrieve` reasoner and its implementation within the multi-agent RAG pipeline. This component is responsible for executing multiple search queries concurrently against the vector store, deduplicating results, and optionally aggregating chunks into full document contexts.

By utilizing `asyncio.gather`, the system achieves significant latency reduction compared to sequential retrieval, enabling the use of diverse query sets to improve recall without a linear increase in response time.

**Sources:** [examples/python_agent_nodes/documentation_chatbot/routers/retrieval.py:1-15](), [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:163-186]()

## System Architecture

The parallel retrieval system operates as the second stage in the 3-reasoner pipeline, accepting diverse queries from the query planner and returning ranked results to the synthesizer.

### Retrieval Flow Diagram

```mermaid
graph TB
    QueryPlanner["plan_queries (Reasoner)"]
    ParallelRetriever["parallel_retrieve (Reasoner)"]
    VectorStore["global_memory (MemoryInterface)"]
    Deduplication["deduplicate_results (Utility)"]
    DocumentAggregator["aggregate_chunks_to_documents (Utility)"]
    Synthesizer["synthesize_answer (Reasoner)"]
    
    QueryPlanner -->|"QueryPlan (3-5 queries)"| ParallelRetriever
    ParallelRetriever -->|"asyncio.gather"| VectorStore
    VectorStore -->|"raw_hits + scores"| Deduplication
    Deduplication -->|"List[RetrievalResult]"| DocumentAggregator
    Deduplication -->|"Chunk mode"| Synthesizer
    DocumentAggregator -->|"Document mode"| Synthesizer
    
    subgraph "Execution Context"
        qa_answer["qa_answer orchestrator"]
    end
    
    qa_answer -.->|"calls"| ParallelRetriever
```

**Sources:** [examples/python_agent_nodes/documentation_chatbot/routers/retrieval.py:59-89](), [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:163-188](), [examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py:113-117]()

## Retrieval Data Structures

The parallel retrieval system uses two primary schemas defined in `schemas.py` to represent retrieved information.

### RetrievalResult Schema

The `RetrievalResult` class represents a single retrieved chunk with minimal metadata for efficient processing.

| Field | Type | Description |
|-------|------|-------------|
| `text` | `str` | Chunk content extracted from documentation [examples/python_agent_nodes/documentation_chatbot/routers/retrieval.py:38-38]() |
| `source` | `str` | Formatted string `path:start-end` [examples/python_agent_nodes/documentation_chatbot/routers/retrieval.py:45-45]() |
| `score` | `float` | Similarity score from vector search [examples/python_agent_nodes/documentation_chatbot/routers/retrieval.py:51-51]() |
| `metadata` | `Dict[str, Any]` | Raw metadata from the vector store [examples/python_agent_nodes/documentation_chatbot/routers/retrieval.py:37-37]() |

### DocumentContext Schema

The `DocumentContext` class represents a full documentation page aggregated from matching chunks, used in document-aware retrieval mode.

| Field | Type | Description |
|-------|------|-------------|
| `document_key` | `str` | Key referencing the Tier-1 full document [examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py:158-158]() |
| `full_text` | `str` | Complete document text retrieved from global memory [examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py:159-159]() |
| `relevance_score` | `float` | Calculated score based on chunk frequency and coverage [examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py:162-162]() |

**Sources:** [examples/python_agent_nodes/documentation_chatbot/routers/retrieval.py:35-56](), [examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py:135-165]()

## Implementation Detail: `parallel_retrieve`

The core logic resides in `parallel_retrieve`, which wraps the `_retrieve_for_query` helper.

### Chunk Retrieval Process

```mermaid
sequenceDiagram
    participant PR as "parallel_retrieve"
    participant RQ as "_retrieve_for_query"
    participant MM as "MemoryInterface.similarity_search"
    participant UT as "pipeline_utils"
    
    PR->>RQ: Spawn N tasks (one per query)
    activate RQ
    RQ->>MM: global_memory.similarity_search(embedding, top_k*2)
    MM-->>RQ: raw_hits
    RQ->>UT: filter_hits(raw_hits, namespace, min_score)
    UT-->>RQ: filtered_hits
    RQ-->>PR: List[RetrievalResult]
    deactivate RQ
    
    PR->>UT: deduplicate_results(all_results)
    UT-->>PR: unique_results
```

**Key Implementation Points:**
1. **Concurrency:** Uses `asyncio.gather(*tasks)` to execute embedding and search operations for all queries in parallel [examples/python_agent_nodes/documentation_chatbot/routers/retrieval.py:71-75]().
2. **Filtering:** Hits are filtered by `namespace` and a `min_score` threshold (default `0.35`) using `filter_hits` [examples/python_agent_nodes/documentation_chatbot/routers/retrieval.py:33-33]().
3. **Deduplication:** The `deduplicate_results` utility ensures that if multiple queries find the same chunk, only the version with the highest score is retained [examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py:47-57]().

**Sources:** [examples/python_agent_nodes/documentation_chatbot/routers/retrieval.py:18-89](), [examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py:29-57]()

## Document Aggregation Strategy

The system supports a "Tiered Retrieval" strategy where small chunks are used for initial search, but full documents are retrieved for synthesis if necessary.

### Document Aggregation Logic
The function `aggregate_chunks_to_documents` performs the following steps:
1. **Grouping:** Groups deduplicated chunks by their `document_key` metadata [examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py:121-125]().
2. **Fetching:** For each unique key, it performs a `global_memory.get(key=doc_key)` to retrieve the full Tier-1 document text [examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py:137-137]().
3. **Scoring:** Calculates a `relevance_score` using `calculate_document_score`, which applies a "coverage boost" (0.05 per chunk, up to 5 chunks) to documents that matched multiple queries [examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py:102-110]().

**Sources:** [examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py:102-176]()

## Two-Tier Storage Integration

Parallel retrieval relies on the ingestion pattern established in `ingestion.py`.

### Storage Tier Architecture

```mermaid
graph LR
    subgraph "Tier-2: Vector Storage"
        Vector["set_vector(key, embedding, metadata)"]
    end
    
    subgraph "Tier-1: Document Storage"
        KV["set(key, data)"]
    end
    
    Vector -->|"metadata.document_key"| KV
    
    subgraph "Code Entities"
        Ingest["ingest_folder (Reasoner)"]
        Ret["parallel_retrieve (Reasoner)"]
        Agg["aggregate_chunks_to_documents (Utility)"]
    end
    
    Ingest -->|"writes"| KV
    Ingest -->|"writes"| Vector
    Ret -->|"reads"| Vector
    Agg -->|"reads"| KV
```

**Implementation Details:**
- **Tier 1:** Full document text is stored at `{namespace}:doc:{relative_path}` [examples/python_agent_nodes/documentation_chatbot/routers/ingestion.py:95-104]().
- **Tier 2:** Chunks are stored with an embedding and metadata containing the `document_key` [examples/python_agent_nodes/documentation_chatbot/routers/ingestion.py:121-134]().

**Sources:** [examples/python_agent_nodes/documentation_chatbot/routers/ingestion.py:94-135](), [examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py:121-140]()

## Retrieval Parameters

The `parallel_retrieve` function exposes several knobs for tuning retrieval behavior:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `queries` | `List[str]` | Required | The list of generated search strings [examples/python_agent_nodes/documentation_chatbot/routers/retrieval.py:61-61]() |
| `namespace` | `str` | `"website-docs"` | The logical partition in the vector store [examples/python_agent_nodes/documentation_chatbot/routers/retrieval.py:62-62]() |
| `top_k` | `int` | `6` | Number of chunks to retrieve *per query* [examples/python_agent_nodes/documentation_chatbot/routers/retrieval.py:63-63]() |
| `min_score` | `float` | `0.35` | Minimum similarity threshold [examples/python_agent_nodes/documentation_chatbot/routers/retrieval.py:64-64]() |

**Sources:** [examples/python_agent_nodes/documentation_chatbot/routers/retrieval.py:59-65]()

## Error Handling and Edge Cases

1. **Empty Results:** If no chunks match the `min_score` or `namespace`, `parallel_retrieve` returns an empty list [examples/python_agent_nodes/documentation_chatbot/routers/retrieval.py:89-89](). The `synthesize_answer` reasoner checks for this and returns a "No documentation found" response [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:34-41]().
2. **Missing Documents:** In document aggregation mode, if a `document_key` is found in a chunk but the corresponding Tier-1 document is missing from KV memory, the system logs the issue and skips that document [examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py:138-140]().
3. **Empty Chunks:** Metadata-only hits with no text are discarded during the retrieval loop [examples/python_agent_nodes/documentation_chatbot/routers/retrieval.py:38-40]().

**Sources:** [examples/python_agent_nodes/documentation_chatbot/routers/retrieval.py:38-40](), [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:34-41](), [examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py:138-140]()

---

# Page: Chatbot: Self-Aware Synthesis

# Chatbot: Self-Aware Synthesis

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/python_agent_nodes/agentic_rag/main.py](examples/python_agent_nodes/agentic_rag/main.py)
- [examples/python_agent_nodes/agentic_rag/skills.py](examples/python_agent_nodes/agentic_rag/skills.py)
- [examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py](examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py)
- [examples/python_agent_nodes/documentation_chatbot/product_context.py](examples/python_agent_nodes/documentation_chatbot/product_context.py)
- [examples/python_agent_nodes/documentation_chatbot/routers/__init__.py](examples/python_agent_nodes/documentation_chatbot/routers/__init__.py)
- [examples/python_agent_nodes/documentation_chatbot/routers/ingestion.py](examples/python_agent_nodes/documentation_chatbot/routers/ingestion.py)
- [examples/python_agent_nodes/documentation_chatbot/routers/qa.py](examples/python_agent_nodes/documentation_chatbot/routers/qa.py)
- [examples/python_agent_nodes/documentation_chatbot/routers/query_planning.py](examples/python_agent_nodes/documentation_chatbot/routers/query_planning.py)
- [examples/python_agent_nodes/documentation_chatbot/routers/retrieval.py](examples/python_agent_nodes/documentation_chatbot/routers/retrieval.py)
- [examples/python_agent_nodes/hello_world_rag/main.py](examples/python_agent_nodes/hello_world_rag/main.py)
- [examples/python_agent_nodes/hello_world_rag/test_pydantic_skill.py](examples/python_agent_nodes/hello_world_rag/test_pydantic_skill.py)

</details>



This document describes the self-aware synthesis component of the Documentation Chatbot example, which generates natural language answers with inline citations and automatically assesses answer completeness. This component represents the final stage in the 3-reasoner RAG pipeline.

For information about the overall chatbot architecture, see [Documentation Chatbot](#12.1). For query planning, see [Chatbot: Query Planning](#12.3). For parallel retrieval, see [Chatbot: Parallel Retrieval](#12.4).

---

## Overview

The self-aware synthesis system is a reasoner-based component that performs three critical functions:

1. **Answer Generation**: Produces markdown-formatted answers with inline citations referencing retrieved documentation chunks [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:52-109]().
2. **Confidence Assessment**: Evaluates its own response completeness without requiring a separate review agent [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:110-128]().
3. **Automatic Refinement**: Triggers targeted re-retrieval for missing information (limited to 1 iteration to prevent loops) [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:194-210]().

This architecture eliminates the need for a separate "critic" or "reviewer" agent by embedding self-assessment directly into the synthesis reasoner, reducing latency and system complexity.

**Sources**: [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:26-129](), [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:164-216]()

---

## Synthesis Architecture

The synthesizer operates as the third stage in a three-reasoner pipeline:

```mermaid
graph TD
    UserQ["User Question"]
    PlanR["plan_queries reasoner"]
    RetrieveR["parallel_retrieve reasoner"]
    SynthR["synthesize_answer reasoner"]
    DocAnswer["DocAnswer"]
    
    UserQ --> PlanR
    PlanR -->|"QueryPlan (3-5 queries)"| RetrieveR
    RetrieveR -->|"RetrievalResult[]"| SynthR
    SynthR -->|"answer + confidence"| DocAnswer
    
    DocAnswer -->|"needs_more=true"| Refine["Automatic Refinement"]
    Refine -->|"targeted queries"| RetrieveR
    RetrieveR -->|"additional chunks"| SynthR
    SynthR -->|"final answer"| DocAnswer
    
    Note["Max 1 refinement iteration"]
```

**Diagram: Three-Reasoner Pipeline with Self-Aware Synthesis**

The synthesizer receives `RetrievalResult[]` from the parallel retriever and produces a `DocAnswer` containing the generated text, citations, and self-assessment metadata [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:27-31]().

**Sources**: [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:164-216](), [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:26-41]()

---

## The `DocAnswer` Schema

The `DocAnswer` Pydantic model defines the output contract for the synthesis reasoner. It combines the natural language response with meta-cognitive evaluation fields.

```mermaid
classDiagram
    class DocAnswer {
        +string answer
        +List~Citation~ citations
        +string confidence
        +bool needs_more
        +List~string~ missing_topics
    }
    
    class Citation {
        +string key
        +string relative_path
        +int start_line
        +int end_line
        +string section
        +string preview
        +float score
    }
    
    DocAnswer "1" --> "*" Citation
    
    note for DocAnswer "confidence: 'high' | 'partial' | 'insufficient'"
    note for Citation "key: single letter without brackets (e.g., 'A', 'B', 'AA')"
```

**Diagram: Answer and Citation Schema Structure**

| Field | Type | Description |
|-------|------|-------------|
| `answer` | `str` | Markdown-formatted answer with inline citation keys like `[A][B]` [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:143-145](). |
| `citations` | `List[Citation]` | Array of citation objects mapping keys to source locations [examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py:60-81](). |
| `confidence` | `str` | Answer quality: `"high"`, `"partial"`, or `"insufficient"` [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:114-128](). |
| `needs_more` | `bool` | `True` if additional retrieval is required for completeness [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:114-128](). |
| `missing_topics` | `List[str]` | Specific information gaps if `needs_more=True` [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:119-128](). |

**Sources**: [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:31-41](), [examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py:60-81]()

---

## Citation System

The citation system uses a key-based reference mechanism that ensures all factual claims are traceable to source documents.

### Citation Key Generation

The synthesizer uses short alphabetic keys (`A`, `B`, `C`, ..., `AA`, `AB`, ...) to reference chunks in the answer text [examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py:13-26](). The LLM receives a simplified mapping structure in the prompt:

```text
## Available Sources (use these keys for citations)
  A: syncing/architecture.md:42-58
  B: syncing/implementation.md:15-30
```

The LLM is instructed to generate answer text like:
> "Agentfield uses DIDs for identity [A]. The control plane manages orchestration [B]." [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:69-70]().

### The `Citation` Object

Each citation contains full provenance metadata generated by `build_citations` [examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py:60-81]():

| Field | Type | Description |
|-------|------|-------------|
| `key` | `str` | Single-letter reference (without brackets) |
| `relative_path` | `str` | File path relative to ingestion root |
| `start_line` | `int` | Starting line number in source file |
| `end_line` | `int` | Ending line number in source file |
| `section` | `str` | Markdown heading under which chunk appears |
| `preview` | `str` | Short text excerpt from the chunk |
| `score` | `float` | Similarity score from vector search |

**Sources**: [examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py:60-81](), [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:44-50]()

---

## Self-Assessment Logic

The synthesizer performs internal confidence assessment. This meta-cognitive step allows the agent to recognize when the retrieved context is insufficient to satisfy the user's request.

### Confidence Levels

```mermaid
graph LR
    Chunks["Retrieved Chunks"]
    Synth["synthesize_answer"]
    
    Synth --> High["confidence='high'"]
    Synth --> Partial["confidence='partial'"]
    Synth --> Insufficient["confidence='insufficient'"]
    
    High -->|"needs_more=false"| Complete["Complete Answer"]
    Partial -->|"needs_more=true"| Refine["Trigger Refinement"]
    Insufficient -->|"needs_more=true"| Refine
    
    Refine --> MissingTopics["missing_topics: ['topic1', 'topic2']"]
```

**Diagram: Confidence Assessment Flow**

| Confidence | Criteria | Action |
|------------|----------|--------|
| `high` | Specific, detailed information found that fully answers the question [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:114-117](). | No refinement needed |
| `partial` | Relevant information found but key details are missing [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:119-122](). | Trigger refinement with `missing_topics` |
| `insufficient` | Requested information is not present in documentation [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:124-127](). | Trigger refinement or return failure |

**Sources**: [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:110-129]()

---

## Automatic Refinement

When `needs_more=True`, the orchestrator `qa_answer` triggers one refinement iteration [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:194-210]().

### Refinement Strategy

1. **Targeted Query Generation**: The `plan_queries` reasoner is called again using the `missing_topics` as input [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:196]().
2. **Result Combination**: New chunks from `parallel_retrieve` are merged with original results and deduplicated [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:198-204]().
3. **Refinement Flag**: The `is_refinement=True` parameter is passed to `synthesize_answer` to signal it should provide the best possible answer even if incomplete [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:129]().
4. **Single Iteration Limit**: The orchestrator only performs this loop once to prevent infinite execution [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:194]().

**Sources**: [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:188-216]()

---

## Two QA Modes

The chatbot supports two synthesis modes with different context strategies:

### Chunk-Based QA (`qa_answer`)

The `qa_answer` reasoner orchestrates synthesis using isolated text chunks retrieved via vector search [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:164-216]().

### Document-Aware QA (`qa_answer_with_documents`)

This mode aggregates chunks into full document contexts using `aggregate_chunks_to_documents` [examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py:113-177]().

**Document Aggregation Logic**:
1. Groups retrieved chunks by their `document_key` [examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py:121-125]().
2. Fetches the full document text from the `global_scope` memory [examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py:137]().
3. Calculates a `relevance_score` based on chunk scores and coverage [examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py:142]().
4. Ranks and returns the top `N` full documents for synthesis [examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py:167-176]().

**Sources**: [examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py:113-177](), [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:181-186]()

---

## Integration with Memory System

The synthesis component leverages the two-tier storage strategy implemented during ingestion.

```mermaid
graph TB
    subgraph "Memory Storage (app.memory.global_scope)"
        DocStore["Document Store<br/>Key: namespace:doc:path"]
        ChunkVectors["Chunk Vectors<br/>set_vector()"]
    end
    
    subgraph "Retrieval"
        Search["similarity_search()"]
        ChunkMeta["Metadata: document_key reference"]
    end
    
    subgraph "Synthesis"
        Lookup["memory.get(document_key)"]
        Synth["synthesize_answer()"]
    end
    
    ChunkVectors --> Search
    Search --> ChunkMeta
    ChunkMeta -->|"document_key"| Lookup
    Lookup --> DocStore
    DocStore -->|"full text"| Synth
```

**Diagram: Two-Tier Storage Integration in Synthesis**

### Storage Keys
- **Full Documents**: Stored under `{namespace}:doc:{relative_path}` [examples/python_agent_nodes/documentation_chatbot/routers/ingestion.py:95-96]().
- **Chunk Vectors**: Stored with metadata including a `document_key` pointer back to the full text [examples/python_agent_nodes/documentation_chatbot/routers/ingestion.py:120-132]().

**Sources**: [examples/python_agent_nodes/documentation_chatbot/routers/ingestion.py:94-135](), [examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py:136-140]()

---

## Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| Max refinement iterations | 1 | Hardcoded in `qa_answer` [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:194](). |
| Default `top_k` | 6 | Number of chunks retrieved per query [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:167](). |
| Min Similarity Score | 0.35 | Threshold for relevance filtering [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:168](). |
| Token Usage | High | Refinement and full-document context increase prompt size. |

**Sources**: [examples/python_agent_nodes/documentation_chatbot/routers/qa.py:164-168](), [examples/python_agent_nodes/documentation_chatbot/pipeline_utils.py:179-190]()

---

# Page: Deployment

# Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [.github/workflows/release.yml](.github/workflows/release.yml)
- [.goreleaser.yml](.goreleaser.yml)
- [control-plane/go.mod](control-plane/go.mod)
- [control-plane/go.sum](control-plane/go.sum)
- [control-plane/internal/templates/docker/docker-compose.yml.tmpl](control-plane/internal/templates/docker/docker-compose.yml.tmpl)
- [deployments/docker/Dockerfile.control-plane](deployments/docker/Dockerfile.control-plane)
- [deployments/docker/Dockerfile.demo-go-agent](deployments/docker/Dockerfile.demo-go-agent)
- [deployments/docker/Dockerfile.go-agent](deployments/docker/Dockerfile.go-agent)
- [deployments/helm/agentfield/values.yaml](deployments/helm/agentfield/values.yaml)
- [deployments/kubernetes/base/control-plane-deployment.yaml](deployments/kubernetes/base/control-plane-deployment.yaml)
- [docs/RELEASE.md](docs/RELEASE.md)
- [examples/python_agent_nodes/rag_evaluation/docker-compose.yml](examples/python_agent_nodes/rag_evaluation/docker-compose.yml)
- [examples/triggers-demo/docker-compose.yml](examples/triggers-demo/docker-compose.yml)
- [scripts/bump_version.py](scripts/bump_version.py)
- [scripts/install.ps1](scripts/install.ps1)
- [scripts/install.sh](scripts/install.sh)
- [scripts/tests/__init__.py](scripts/tests/__init__.py)
- [scripts/tests/test_bump_version.py](scripts/tests/test_bump_version.py)
- [sdk/go/ai/openrouter_attribution.go](sdk/go/ai/openrouter_attribution.go)

</details>



This document covers deploying AgentField agents and the control plane to production environments. It includes Docker containerization, platform-specific deployment guides (Railway, serverless providers), environment configuration, and production readiness considerations.

For information about building and releasing AgentField itself, see the [Release Process documentation](docs/RELEASE.md). For local development setup, see [Getting Started](#2). For testing infrastructure, see [Testing & Development](#16).

---

## Overview

AgentField supports multiple deployment patterns:

| Deployment Type | Control Plane | Agent Nodes | Use Case |
|----------------|---------------|-------------|----------|
| **Local** | `af server` | Same machine | Development, testing |
| **Docker** | Container | Container(s) | Self-hosted production |
| **Railway** | Managed service | Managed service | Quick cloud deployment |
| **Serverless** | Separate deployment | AWS Lambda, Azure Functions, Google Cloud Functions | Scalable, event-driven |
| **Kubernetes** | Pod | Pod(s) | Enterprise orchestration |

### Architecture Patterns

```mermaid
graph TB
    subgraph "Pattern 1: Monolithic (Development)"
        CP1["af server<br/>:8080"]
        Agent1["Agent Process<br/>Python/TS/Go"]
        CP1 <--> Agent1
    end
    
    subgraph "Pattern 2: Containerized (Production)"
        CP2["control-plane<br/>Docker Container"]
        Agent2A["agent-1<br/>Docker Container"]
        Agent2B["agent-2<br/>Docker Container"]
        PG2[("PostgreSQL<br/>Container")]
        
        CP2 <--> Agent2A
        CP2 <--> Agent2B
        CP2 --> PG2
    end
    
    subgraph "Pattern 3: Serverless (Scale to Zero)"
        CP3["control-plane<br/>Railway/Cloud Run"]
        Lambda1["agent-1<br/>AWS Lambda"]
        Lambda2["agent-2<br/>Azure Function"]
        PG3[("Managed PostgreSQL")]
        
        CP3 -.->|"HTTP execute"| Lambda1
        CP3 -.->|"HTTP execute"| Lambda2
        CP3 --> PG3
    end
```

**Sources:** [.github/workflows/release.yml:1-51]()

---

## Binary Installation

### Install Script Architecture

The AgentField CLI is distributed as pre-compiled binaries via install scripts for Unix/Linux/macOS (`install.sh`) and Windows (`install.ps1`).

```mermaid
graph TB
    User["User Terminal"]
    
    subgraph "Install Script Flow [scripts/install.sh]"
        Script["install.sh"]
        GitHubAPI["GitHub Releases API"]
        
        Script --> GetVersion["get_latest_version()"]
        GetVersion --> GitHubAPI
        
        GitHubAPI --> DownloadBinary["download_file()<br/>agentfield-{os}-{arch}"]
        GitHubAPI --> DownloadChecksums["download_file()<br/>checksums.txt"]
        
        DownloadBinary --> Verify["verify_checksum()"]
        DownloadChecksums --> Verify
        
        Verify --> Install["install_binary()<br/>AGENTFIELD_INSTALL_DIR"]
    end
    
    User --> Script
```

**Supported Platforms:**

| OS | Architecture | Binary Name |
|----|--------------|-------------|
| macOS | Intel (amd64) | `agentfield-darwin-amd64` |
| macOS | Apple Silicon (arm64) | `agentfield-darwin-arm64` |
| Linux | x86_64 (amd64) | `agentfield-linux-amd64` |
| Linux | ARM64 | `agentfield-linux-arm64` |
| Windows | x86_64 (amd64) | `agentfield-windows-amd64.exe` |

**Sources:** [scripts/install.sh:11-53](), [scripts/install.ps1:67-83](), [.goreleaser.yml:198-203]()

---

## Docker Deployment

### Control Plane Docker Image

The control plane is published as a multi-architecture Docker image. The build process uses a multi-stage `Dockerfile.control-plane` to compile the Go binary and build the Vite-based Web UI.

**Dockerfile Architecture:**

```mermaid
graph LR
    subgraph "ui-builder [node:20-alpine]"
        Vite["vite build"]
    end
    
    subgraph "go-builder [golang:1.25-bookworm]"
        GoBuild["go build -tags 'embedded sqlite_fts5'"]
    end
    
    Vite -->|"dist/"| GoBuild
    GoBuild -->|"agentfield-server"| Runtime["distroless/base-debian12"]
```

**Sources:** [deployments/docker/Dockerfile.control-plane:1-48](), [.github/workflows/release.yml:48-51]()

---

## Railway Deployment

Railway deployment is optimized for Python agents using `nixpacks.toml` and a custom `install.sh` script to manage dependency synchronization with PyPI.

### Configuration

For details, see [Railway Deployment](#13.2).

- **nixpacks.toml**: Defines the build phases. [examples/python_agent_nodes/documentation_chatbot/nixpacks.toml:1-5]()
- **install.sh**: Implements a retry loop to wait for `agentfield` SDK availability on PyPI during a release. [examples/python_agent_nodes/documentation_chatbot/install.sh:25-47]()

**Sources:** [examples/python_agent_nodes/documentation_chatbot/railway.json:1-10]()

---

## Serverless Deployment

Agents can be deployed to AWS Lambda, Azure Functions, or Google Cloud Functions.

### Entry Points
- **Python**: Use `handle_serverless()` to wrap the agent application.
- **TypeScript**: Use `agent.handler()` to create a serverless-compatible entry point.

For details, see [Serverless Deployment](#13.3).

---

## Environment Configuration

Both the control plane and agent nodes are configured via environment variables.

### Key Variables
| Variable | Scope | Purpose |
|----------|-------|---------|
| `AGENTFIELD_STORAGE_MODE` | Server | `local` (SQLite) or `postgres` |
| `AGENTFIELD_SERVER` | Agent | URL of the control plane |
| `AGENT_CALLBACK_URL` | Agent | Public URL where the control plane can reach the agent |
| `OPENROUTER_API_KEY` | Both | API key for LLM access |

For details, see [Environment Configuration](#13.4).

**Sources:** [examples/python_agent_nodes/rag_evaluation/docker-compose.yml:2-32]()

---

## Production Considerations

When moving to production, the following components should be tuned:
- **PostgreSQL**: Use `pgvector` for vector storage and configure connection pooling.
- **DIDs & VCs**: Ensure `AGENTFIELD_NO_VC_EXECUTION` is `false` to maintain a cryptographic audit trail.
- **Storage**: Migrate from `LocalStorage` to `PostgresProvider` for durability.

For details, see [Production Considerations](#13.5).

**Sources:** [control-plane/go.mod:35-37](), [docs/RELEASE.md:9-12]()

---

## Release Pipeline

AgentField uses a **two-tier release system** managed by GitHub Actions and `scripts/bump_version.py`.

```mermaid
graph TD
    Push["Push to main"] --> Staging["Staging Release<br/>(0.1.19-rc.1)"]
    Staging --> Test["Testing/QA"]
    Test --> Dispatch["Manual Workflow Dispatch"]
    Dispatch --> Production["Production Release<br/>(0.1.19)"]
```

- **Staging**: Automatic on push to `main`. [docs/RELEASE.md:63-80]()
- **Production**: Manual trigger via `release.yml`. [docs/RELEASE.md:116-141]()
- **Version Bumping**: Handled by `SemVer` class in Python. [scripts/bump_version.py:36-86]()

**Sources:** [.github/workflows/release.yml:3-23](), [docs/RELEASE.md:1-37]()

---

# Page: Docker Deployment

# Docker Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [control-plane/go.mod](control-plane/go.mod)
- [control-plane/go.sum](control-plane/go.sum)
- [control-plane/internal/handlers/nodes_register.go](control-plane/internal/handlers/nodes_register.go)
- [control-plane/internal/handlers/nodes_serverless_ssrf_test.go](control-plane/internal/handlers/nodes_serverless_ssrf_test.go)
- [control-plane/internal/observability/telemetry.go](control-plane/internal/observability/telemetry.go)
- [control-plane/internal/observability/telemetry_test.go](control-plane/internal/observability/telemetry_test.go)
- [deployments/docker/Dockerfile.control-plane](deployments/docker/Dockerfile.control-plane)
- [deployments/docker/Dockerfile.demo-go-agent](deployments/docker/Dockerfile.demo-go-agent)
- [deployments/docker/Dockerfile.go-agent](deployments/docker/Dockerfile.go-agent)
- [deployments/docker/README.md](deployments/docker/README.md)
- [deployments/docker/docker-compose.yml](deployments/docker/docker-compose.yml)

</details>



## Purpose and Scope

This document covers deploying AgentField components using Docker and Docker Compose. It explains how to run the control plane in containers, containerize agent nodes, and orchestrate multi-container deployments.

---

## Control Plane Deployment

### Official Dockerfile Analysis
The control plane image is built using a multi-stage Dockerfile that compiles the Web UI and the Go backend into a single distroless container.

1.  **UI Builder**: Uses `node:20-alpine` to build the React frontend located in `control-plane/web/client/` [deployments/docker/Dockerfile.control-plane:1-13]().
2.  **Go Builder**: Uses `golang:1.25-bookworm` with `CGO_ENABLED=1` to compile the `agentfield-server` binary [deployments/docker/Dockerfile.control-plane:15-37](). It includes `embedded` and `sqlite_fts5` tags to bundle the UI and enable full-text search [deployments/docker/Dockerfile.control-plane:37]().
3.  **Final Image**: A minimal `gcr.io/distroless/base-debian12` image running as a `nonroot` user [deployments/docker/Dockerfile.control-plane:43-48]().

### Environment Variables
Key environment variables for the control plane container:

| Variable | Description | Default |
|----------|-------------|---------|
| `AGENTFIELD_STORAGE_MODE` | Storage backend (`sqlite` or `postgres`) | `sqlite` |
| `AGENTFIELD_HTTP_ADDR` | HTTP server address and port | `0.0.0.0:8080` |
| `AGENTFIELD_HOME` | Data directory for SQLite and keys | `/data` |
| `AGENTFIELD_POSTGRES_URL` | PostgreSQL connection string | - |
| `AGENTFIELD_TELEMETRY_ENABLED` | Enable anonymous usage telemetry | `true` |

**Sources:** [deployments/docker/docker-compose.yml:21-30](), [deployments/docker/Dockerfile.control-plane:41-46]()

---

## Docker Compose Orchestration

AgentField provides a standard `docker-compose.yml` for local evaluation and production-like setups.

### System Architecture (Docker Space)

```mermaid
graph TD
    subgraph "Docker Network"
        CP["control-plane<br/>(Go Server + UI)"]
        PG["postgres<br/>(pgvector:pg16)"]
        GA["demo-go-agent<br/>(Go SDK)"]
        PA["demo-python-agent<br/>(Python SDK)"]
    end

    U["User Browser"] -->|":8080/ui/"| CP
    CP -->|":5432"| PG
    GA -->|"/api/v1/nodes/register"| CP
    PA -->|"/api/v1/nodes/register"| CP
    CP -->|"/execute (Callback)"| GA
    CP -->|"/execute (Callback)"| PA

    subgraph "Volumes"
        V1[("agentfield-data")]
        V2[("pgdata")]
    end

    CP --- V1
    PG --- V2
```
**Sources:** [deployments/docker/docker-compose.yml:1-71](), [deployments/docker/README.md:1-18]()

### PostgreSQL with pgvector
The stack uses `pgvector/pgvector:pg16` to support vector storage for agent memory [deployments/docker/docker-compose.yml:3](). The control plane waits for the database to be healthy via a `pg_isready` check before starting [deployments/docker/docker-compose.yml:11-15,34-36]().

---

## Agent Containerization

### Go Agent Node
Go agents are compiled into static binaries and placed in a `distroless` container for a minimal footprint.
*   **Source**: `sdk/go` and agent logic [deployments/docker/Dockerfile.demo-go-agent:4-5]().
*   **Build**: Uses `CGO_ENABLED=0` for portability [deployments/docker/Dockerfile.demo-go-agent:9]().

### Python Agent Node
Python agents use a `python:3.11-slim` or similar base.
*   **Registration**: Agents must be configured with `AGENTFIELD_URL` to find the control plane and an `AGENT_CALLBACK_URL` so the control plane can route execution requests back to the container [deployments/docker/docker-compose.yml:62-65]().

### Networking and Discovery
In a Docker network, containers resolve each other by service name.
*   **Agent to Control Plane**: `AGENTFIELD_URL=http://control-plane:8080` [deployments/docker/docker-compose.yml:46]().
*   **Control Plane to Agent**: The agent registers its internal Docker DNS name, e.g., `http://demo-python-agent:8001` [deployments/docker/docker-compose.yml:65]().

The control plane contains logic in `gatherCallbackCandidates` and `resolveCallbackCandidates` to handle cases where agents are running on the host vs. inside Docker [control-plane/internal/handlers/nodes_register.go:91-214]().

---

## Security and SSRF Hardening

When deploying in Docker or Serverless environments, the control plane implements SSRF (Server-Side Request Forgery) protections when discovering or calling agents.

### Discovery Normalization
The `normalizeServerlessDiscoveryURL` function ensures that invocation URLs:
1.  Use only `http` or `https` schemes [control-plane/internal/handlers/nodes_register.go:248-256]().
2.  Do not include user-info, queries, or fragments [control-plane/internal/handlers/nodes_register.go:258-268]().
3.  Have paths cleaned of traversal segments (e.g., `/../`) [control-plane/internal/handlers/nodes_register.go:224-229]().

```mermaid
graph LR
    A["Raw Input URL"] --> B["parseServerlessDiscoveryURL"]
    B --> C{"Allowed Host?"}
    C -->|Yes| D["Reconstruct Safe URL"]
    C -->|No| E["Reject Request"]
    D --> F["Outbound Discovery Request"]
```
**Sources:** [control-plane/internal/handlers/nodes_register.go:223-270](), [control-plane/internal/handlers/nodes_serverless_ssrf_test.go:24-37]()

---

## Anonymous Telemetry

By default, the Docker deployment enables anonymous usage telemetry [deployments/docker/docker-compose.yml:29]().
*   **Implementation**: `TelemetryService` [control-plane/internal/observability/telemetry.go:47-60]().
*   **Data Collected**: Startup events, agent registration (SDK language/version), and execution success/failure buckets [control-plane/internal/observability/telemetry_test.go:61-132]().
*   **Anonymization**: Uses a hashed `install_id` stored in the data volume to identify unique installations without tracking users [control-plane/internal/observability/telemetry.go:100-143]().

To disable, set `AGENTFIELD_TELEMETRY_ENABLED=false` in the environment [deployments/docker/README.md:57-62]().

**Sources:** [control-plane/internal/observability/telemetry.go:1-190](), [deployments/docker/README.md:53-62]()

---

# Page: Railway Deployment

# Railway Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/release.yml](.github/workflows/release.yml)
- [.goreleaser.yml](.goreleaser.yml)
- [control-plane/internal/templates/docker/docker-compose.yml.tmpl](control-plane/internal/templates/docker/docker-compose.yml.tmpl)
- [deployments/helm/agentfield/values.yaml](deployments/helm/agentfield/values.yaml)
- [deployments/kubernetes/base/control-plane-deployment.yaml](deployments/kubernetes/base/control-plane-deployment.yaml)
- [docs/RELEASE.md](docs/RELEASE.md)
- [examples/python_agent_nodes/documentation_chatbot/install.sh](examples/python_agent_nodes/documentation_chatbot/install.sh)
- [examples/python_agent_nodes/documentation_chatbot/nixpacks.toml](examples/python_agent_nodes/documentation_chatbot/nixpacks.toml)
- [examples/python_agent_nodes/documentation_chatbot/railway.json](examples/python_agent_nodes/documentation_chatbot/railway.json)
- [examples/python_agent_nodes/rag_evaluation/docker-compose.yml](examples/python_agent_nodes/rag_evaluation/docker-compose.yml)
- [examples/triggers-demo/docker-compose.yml](examples/triggers-demo/docker-compose.yml)
- [scripts/bump_version.py](scripts/bump_version.py)
- [scripts/install.ps1](scripts/install.ps1)
- [scripts/install.sh](scripts/install.sh)
- [scripts/tests/__init__.py](scripts/tests/__init__.py)
- [scripts/tests/test_bump_version.py](scripts/tests/test_bump_version.py)
- [sdk/go/ai/openrouter_attribution.go](sdk/go/ai/openrouter_attribution.go)

</details>



## Purpose and Scope

This document describes how to deploy AgentField agents to [Railway](https://railway.app), a platform-as-a-service (PaaS) that simplifies containerized deployments. Railway uses Nixpacks as its default builder, which automatically detects Python projects and configures them appropriately.

This page covers:
- Configuration files required for Railway deployment (`nixpacks.toml`, `railway.json`, `install.sh`)
- The PyPI synchronization mechanism that handles version availability
- Environment variable configuration for connecting to a control plane
- Deployment workflow and runtime architecture

For containerized deployments using Docker directly, see [Docker Deployment](#13.1). For serverless platforms like AWS Lambda, see [Serverless Deployment](#13.3). For general environment configuration, see [Environment Configuration](#13.4).

---

## Railway Platform Overview

Railway provides automated deployments triggered by git pushes. When deploying AgentField agents to Railway:

1. Railway detects a Python project via `requirements.txt`.
2. Nixpacks builder creates a containerized environment.
3. Custom configuration in `nixpacks.toml` and `railway.json` controls build and start behavior.
4. The agent process starts and registers with a remote control plane.

Railway handles:
- Automatic HTTPS endpoints for each service.
- Environment variable management.
- Log aggregation.
- Automatic restarts on crashes.

**Key Constraint**: Railway deployments typically occur immediately after a release (often triggered by the same CI/CD pipeline), which can create a race condition where Railway tries to install a PyPI package version before it has fully propagated to all PyPI mirrors.

---

## Configuration Files

### nixpacks.toml Structure

The `nixpacks.toml` file customizes the Nixpacks build process. AgentField agents use a minimal configuration that delegates installation to a custom script to handle dependency timing issues.

```toml
[phases.install]
cmds = ["./install.sh"]

[start]
cmd = "python main.py"
```

**Key Elements**:

| Configuration | Purpose |
|--------------|---------|
| `phases.install.cmds` | Replaces default pip installation with custom `install.sh` script |
| `start.cmd` | Specifies the command to run when the container starts |

Sources: [examples/python_agent_nodes/documentation_chatbot/nixpacks.toml:1-6]()

---

### railway.json Structure

The `railway.json` file provides Railway-specific service configuration, ensuring the correct builder and configuration paths are utilized.

```json
{
  "$schema": "https://railway.com/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "nixpacksConfigPath": "nixpacks.toml"
  },
  "deploy": {
    "startCommand": "python main.py"
  }
}
```

**Configuration Parameters**:

| Field | Value | Purpose |
|-------|-------|---------|
| `build.builder` | `"NIXPACKS"` | Explicitly specifies Nixpacks as the build system |
| `build.nixpacksConfigPath` | `"nixpacks.toml"` | Points to custom Nixpacks configuration |
| `deploy.startCommand` | `"python main.py"` | Start command for the deployed service |

Sources: [examples/python_agent_nodes/documentation_chatbot/railway.json:1-11]()

---

## PyPI Synchronization Mechanism

### The Race Condition Problem

When AgentField releases a new version (triggered by `scripts/bump_version.py` and the GitHub Release workflow):

1. CI/CD pipeline builds and publishes to PyPI.
2. Railway webhook triggers deployment simultaneously.
3. Railway may start deployment before PyPI mirrors propagate the new version.
4. `pip install` fails with "version not found".

### install.sh Retry Logic

The `install.sh` script implements a polling mechanism to wait for PyPI availability.

#### Diagram: PyPI Polling Flow (install.sh)

```mermaid
flowchart TD
    Start["Start install.sh"]
    SetupVenv["Create venv at /opt/venv"]
    ParseReq["Extract agentfield version<br/>from requirements.txt"]
    
    CheckReq{"agentfield<br/>requirement<br/>found?"}
    NormalInstall["pip install -r requirements.txt"]
    
    ParseVersion["Parse MIN_VERSION<br/>from requirement"]
    InitRetry["Initialize retry counter<br/>i = 1, MAX_RETRIES = 30"]
    
    TryDryRun["pip install --dry-run<br/>'agentfield>=MIN_VERSION'"]
    
    CheckSuccess{"Dry run<br/>successful?"}
    CheckMaxRetries{"i == MAX_RETRIES?"}
    
    WaitAndRetry["Wait 10 seconds<br/>Increment i"]
    Timeout["Log timeout warning"]
    
    ActualInstall["pip install -r requirements.txt"]
    Complete["Installation complete"]
    
    Start --> SetupVenv
    SetupVenv --> ParseReq
    ParseReq --> CheckReq
    
    CheckReq -->|No| NormalInstall
    CheckReq -->|Yes| ParseVersion
    
    ParseVersion --> InitRetry
    InitRetry --> TryDryRun
    
    TryDryRun --> CheckSuccess
    CheckSuccess -->|Yes| ActualInstall
    CheckSuccess -->|No| CheckMaxRetries
    
    CheckMaxRetries -->|Yes| Timeout
    CheckMaxRetries -->|No| WaitAndRetry
    
    Timeout --> ActualInstall
    WaitAndRetry --> TryDryRun
    
    NormalInstall --> Complete
    ActualInstall --> Complete
```

Sources: [examples/python_agent_nodes/documentation_chatbot/install.sh:1-47]()

#### Key Implementation Details

**Virtual Environment Setup**:
The script creates a clean virtual environment at `/opt/venv` to isolate agent dependencies from the Nixpacks base environment [examples/python_agent_nodes/documentation_chatbot/install.sh:8-9]().

**Version Extraction**:
The script uses `grep` and `sed` to identify the required `agentfield` version from `requirements.txt` [examples/python_agent_nodes/documentation_chatbot/install.sh:12-21]().

**Retry Configuration**:
- `MAX_RETRIES`: 30 [examples/python_agent_nodes/documentation_chatbot/install.sh:25]()
- `RETRY_INTERVAL`: 10 seconds [examples/python_agent_nodes/documentation_chatbot/install.sh:26]()
- Total timeout: 5 minutes.

**Dry Run Check**:
The script uses `pip install --dry-run` to verify package existence on the registry without performing a full installation until availability is confirmed [examples/python_agent_nodes/documentation_chatbot/install.sh:30-33]().

Sources: [examples/python_agent_nodes/documentation_chatbot/install.sh:1-47]()

---

## Environment Variables Configuration

### Required Variables

Railway services require environment variables to connect agents to a control plane. Configure these in the Railway dashboard under the service's Variables tab:

| Variable | Example Value | Purpose |
|----------|--------------|---------|
| `AGENTFIELD_SERVER` | `https://control-plane.up.railway.app` | URL of the control plane to register with |
| `AGENTFIELD_API_KEY` | `af_prod_abc123...` | Authentication key for control plane communication |
| `PORT` | `8001` | Port the agent listens on (Railway auto-assigns) |

### AI Provider Variables

To enable LLM capabilities in reasoners, provide keys for the supported providers (OpenAI, Anthropic, Google, Mistral, Groq, xAI, DeepSeek, Cohere, OpenRouter, Ollama).

Sources: [examples/python_agent_nodes/rag_evaluation/docker-compose.yml:4-11]()

---

## Deployment Workflow

### Diagram: Railway Deployment Pipeline

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant Git as "Git Repository"
    participant GHA as "GitHub Actions (release.yml)"
    participant PyPI as "PyPI Registry"
    participant Railway as "Railway Platform"
    participant Agent as "Agent Process"
    
    Note over Dev,PyPI: Release Phase
    Dev->>Git: git push (triggers release)
    Git->>GHA: Start Release Workflow
    GHA->>GHA: bump_version.py
    GHA->>PyPI: Publish agentfield package
    
    Note over Railway,Agent: Railway Deployment
    Git->>Railway: Webhook: new commit
    Railway->>Railway: Nixpacks Builder
    Railway->>Agent: Run install.sh
    
    loop Retry up to 30 times
        Agent->>PyPI: pip install --dry-run agentfield>=X.Y.Z
        alt Package available
            PyPI-->>Agent: Success
        else Package not ready
            PyPI-->>Agent: 404/Not Found
            Agent->>Agent: sleep 10s
        end
    end
    
    Agent->>PyPI: pip install -r requirements.txt
    Railway->>Agent: python main.py
    Note over Agent: Agent registers with Control Plane
```

Sources: [.github/workflows/release.yml:1-52](), [examples/python_agent_nodes/documentation_chatbot/install.sh:1-47](), [examples/python_agent_nodes/documentation_chatbot/nixpacks.toml:1-6]()

---

## Multi-Agent Deployment

In a Railway environment, you typically deploy the Control Plane and Agent Nodes as separate services within the same project.

### Diagram: System Entities to Code Mapping

This diagram bridges the conceptual deployment entities to their implementation files.

```mermaid
graph LR
    subgraph "Natural Language Concepts"
        Release["Release Process"]
        Install["CLI Installer"]
        RailwayCfg["Railway Config"]
        BuildScript["Build Script"]
    end

    subgraph "Code Entity Space"
        ReleaseScript["scripts/bump_version.py"]
        InstallerScript["scripts/install.sh"]
        NixpacksFile["examples/.../nixpacks.toml"]
        RailwayFile["examples/.../railway.json"]
        BuildHandler["examples/.../install.sh"]
    end

    Release --- ReleaseScript
    Install --- InstallerScript
    RailwayCfg --- NixpacksFile
    RailwayCfg --- RailwayFile
    BuildScript --- BuildHandler
```

Sources: [scripts/bump_version.py:1-20](), [scripts/install.sh:1-40](), [examples/python_agent_nodes/documentation_chatbot/nixpacks.toml:1-6](), [examples/python_agent_nodes/documentation_chatbot/railway.json:1-11](), [examples/python_agent_nodes/documentation_chatbot/install.sh:1-47]()

### Service Topology

| Service | Type | Code Base | Config |
|---------|------|-----------|--------|
| **Control Plane** | Go Binary | `control-plane/cmd/af` | `AGENTFIELD_STORAGE_MODE=local` |
| **Agent Node** | Python/TS | `sdk/python` | `AGENTFIELD_SERVER=...` |

Sources: [.goreleaser.yml:11-30](), [examples/python_agent_nodes/rag_evaluation/docker-compose.yml:1-15]()

---

## Troubleshooting

### Installation Failures
If `install.sh` fails despite retries, verify that the `VERSION` file in the root matches the requirement in `requirements.txt`. The release workflow [release.yml]() uses `scripts/bump_version.py` to keep these in sync, but manual changes to `requirements.txt` may bypass this.

### Architecture Mismatches
Railway typically uses `linux-amd64`. Ensure your deployment is not accidentally targeting `linux-arm64` if using binary-specific skills or the `af` CLI directly. The `af` CLI installer [scripts/install.sh]() automatically detects architecture but requires `curl` and `bash` to be present in the Nixpacks environment.

Sources: [.github/workflows/release.yml:58-62](), [scripts/install.sh:137-145](), [scripts/bump_version.py:16-27]()

---

# Page: Serverless Deployment

# Serverless Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [control-plane/internal/handlers/nodes_serverless_revocation_test.go](control-plane/internal/handlers/nodes_serverless_revocation_test.go)
- [control-plane/internal/services/health_monitor_additional_test.go](control-plane/internal/services/health_monitor_additional_test.go)
- [control-plane/internal/services/ui_service_additional_test.go](control-plane/internal/services/ui_service_additional_test.go)
- [control-plane/web/client/src/types.ts](control-plane/web/client/src/types.ts)
- [control-plane/web/client/src/types/agentfield.ts](control-plane/web/client/src/types/agentfield.ts)
- [examples/go_agent_nodes/cmd/lambda/main.go](examples/go_agent_nodes/cmd/lambda/main.go)
- [sdk/python/agentfield/agent_discovery.py](sdk/python/agentfield/agent_discovery.py)
- [sdk/python/agentfield/agent_pause.py](sdk/python/agentfield/agent_pause.py)
- [sdk/python/agentfield/agent_schema.py](sdk/python/agentfield/agent_schema.py)
- [sdk/python/agentfield/agent_serverless.py](sdk/python/agentfield/agent_serverless.py)
- [sdk/python/agentfield/agent_vc.py](sdk/python/agentfield/agent_vc.py)

</details>



This page covers deploying AgentField agents to serverless platforms such as AWS Lambda, Azure Functions, Google Cloud Functions, Cloud Run, and Kubernetes Jobs. Serverless agents execute on-demand without maintaining long-running server processes, enabling cost-effective scaling and reduced operational overhead.

For deploying agents as long-running services with the control plane, see [Docker Deployment](#13.1) and [Railway Deployment](#13.2). For production configuration of the control plane itself, see [Production Considerations](#13.5).

---

## Serverless Execution Model

Serverless agents in AgentField differ from long-running agents in several key aspects:

| Aspect | Long-Running Agent | Serverless Agent |
|--------|-------------------|------------------|
| **Lifecycle** | Starts on boot, runs continuously | Created per invocation, destroyed after completion |
| **Registration** | Registers on startup | Auto-registers on first invocation or via `/discover` |
| **Heartbeat** | Periodic heartbeats every 30s | No heartbeat (ephemeral) |
| **Connection** | Maintains WebSocket for events | Uses HTTP for stateless operations |
| **Deployment Type** | `long_running` | `serverless` |
| **Health Monitoring** | Tracked by active health registry | Excluded from active health recovery |

Sources: [sdk/python/agentfield/agent_discovery.py:19-19](), [control-plane/web/client/src/types/agentfield.ts:10-10](), [control-plane/internal/services/health_monitor_additional_test.go:71-105]()

### Execution Flow

```mermaid
sequenceDiagram
    participant Platform as "Serverless Platform<br/>(Lambda/Cloud Functions)"
    participant Agent as "Agent Handler<br/>handle_serverless() / handler()"
    participant CP as "Control Plane<br/>/serverless/register"
    participant Storage as "Storage Layer"

    Note over Platform: Cold start or warm instance
    
    Platform->>Agent: Invoke with event<br/>(HTTP trigger, direct invoke, etc)
    
    alt First Invocation (Auto-Register)
        Agent->>CP: POST /serverless/register<br/>{invocation_url: discovery_url}
        CP->>Agent: GET /discover
        Agent-->>CP: Discovery Metadata
        CP->>Storage: Store agent metadata
        CP-->>Agent: 201 Created
    end
    
    Agent->>Agent: Parse event to extract<br/>target, input, execution_context
    
    alt Discovery Request
        Agent->>Agent: Check path == "/discover"
        Agent-->>Platform: Return agent metadata<br/>{node_id, reasoners, skills}
    end
    
    alt Execution Request
        Agent->>Agent: Find reasoner/skill by name
        Agent->>Agent: Create ExecutionContext<br/>with execution_id, workflow_id
        Agent->>Agent: Execute reasoner/skill handler
        Agent-->>Platform: Return result<br/>{statusCode: 200, body: result}
    end
    
    Note over Platform: Instance destroyed or recycled
```

**Sources:** [sdk/python/agentfield/agent_serverless.py:7-47](), [control-plane/internal/handlers/nodes_serverless_revocation_test.go:41-43](), [sdk/python/agentfield/agent_discovery.py:6-38]()

---

## Python SDK: `handle_serverless()`

The Python SDK provides the `handle_serverless()` method as the universal entry point for serverless platforms.

### Basic Setup

```python
from agentfield import Agent

# Create agent with auto_register=False to defer registration
app = Agent(
    node_id="serverless_agent",
    agentfield_server="https://agentfield.company.com",
    auto_register=True  # Enables auto-registration on first invocation
)

@app.reasoner()
async def analyze(text: str) -> dict:
    return {"analysis": text.upper()}

# AWS Lambda handler
def lambda_handler(event, context):
    return app.handle_serverless(event)
```

**Sources:** [sdk/python/agentfield/agent_serverless.py:32-46]()

### Method Signature

The `handle_serverless()` method accepts:
- **event** (`dict`): Serverless event containing request metadata.
- **adapter** (`Optional[Callable]`): Optional function to normalize platform-specific events.

Returns a `dict` with `statusCode` and `body` fields compatible with API Gateway and similar services.

**Sources:** [sdk/python/agentfield/agent_serverless.py:7-9]()

### Event Format Mapping

The handler extracts execution metadata from the event dictionary to populate the `ExecutionContext`.

```mermaid
graph TB
    subgraph "Input Event Structure"
        Event["event: dict"]
        
        Event --> Path["path: str<br/>'/discover' or '/execute'"]
        Event --> Action["action: str<br/>'discover' or 'execute'"]
        Event --> Target["reasoner/target/skill: str<br/>Function name to invoke"]
        Event --> Input["input: dict<br/>Function parameters"]
        Event --> ExecCtx["execution_context: dict<br/>execution_id, workflow_id, etc"]
    end
    
    subgraph "Code Entities: ExecutionContext"
        ExecCtx --> RunID["run_id"]
        ExecCtx --> ExecID["execution_id"]
        ExecCtx --> WFID["workflow_id"]
        ExecCtx --> CDID["caller_did"]
        ExecCtx --> TDID["target_did"]
    end
```

**Sources:** [sdk/python/agentfield/agent_serverless.py:85-139](), [sdk/python/agentfield/execution_context.py:3-3]()

---

## Go SDK: Serverless Deployment

Go agents can be deployed to AWS Lambda using the standard SDK combined with the `aws-lambda-go` adapter.

### Lambda Implementation

```go
func main() {
    cfg := agent.Config{
        NodeID:               "go-lambda-hello",
        DeploymentType:       "serverless",
        DisableLeaseLoop:     true,
    }

    srv, _ := agent.New(cfg)
    
    srv.RegisterReasoner("hello", func(ctx context.Context, input map[string]any) (any, error) {
        exec := agent.ExecutionContextFrom(ctx)
        return map[string]any{"greeting": "Hello", "exec_id": exec.ExecutionID}, nil
    })

    adapter := httpadapter.NewV2(srv.Handler())
    lambda.Start(adapter.ProxyWithContext)
}
```

**Sources:** [examples/go_agent_nodes/cmd/lambda/main.go:20-90]()

---

## Control Plane: Serverless Management

The control plane includes specialized logic for managing the lifecycle of serverless nodes, including registration and security.

### Serverless Registration and Approval

Serverless agents are registered via the `RegisterServerlessAgentHandler`. This handler performs several critical checks:
1. **Revocation Check**: Blocks re-registration if an agent is in `AgentStatusPendingApproval`.
2. **Tag Preservation**: When a serverless agent re-registers, the control plane preserves only the `ApprovedTags` for its reasoners and skills.
3. **Auth Requirement**: Captures whether the serverless origin requires authentication (`origin_auth_required`).

**Sources:** [control-plane/internal/handlers/nodes_serverless_revocation_test.go:16-61](), [control-plane/internal/handlers/nodes_serverless_revocation_test.go:63-119](), [control-plane/web/client/src/types/agentfield.ts:12-12]()

### Health Monitoring

Serverless nodes are handled differently by the `HealthMonitor`. They are explicitly skipped during database recovery to prevent unnecessary polling of ephemeral instances.

**Sources:** [control-plane/internal/services/health_monitor_additional_test.go:71-105]()

---

## Implementation Details

### Runtime Schema Validation

To optimize serverless cold starts, the Python SDK uses a lightweight `_validate_handler_input` method instead of heavy Pydantic models for every invocation. This saves approximately 1.5-2 KB per handler.

**Sources:** [sdk/python/agentfield/agent_schema.py:67-85]()

### Identity and VCs

Serverless agents still participate in the cryptographic identity system. The `_AgentVCMixin` handles asynchronous VC generation to ensure that signing execution proofs does not block the serverless response.

```mermaid
graph LR
    Execute["Execute Function"] --> Success["Status: success"]
    Success --> GenVC["_generate_vc_async"]
    GenVC --> VCGen["VCGenerator.generate_execution_vc"]
    VCGen --> Log["log_info(Generated VC)"]
```

**Sources:** [sdk/python/agentfield/agent_vc.py:118-155]()

### Pause and Approval Flow

If a serverless reasoner calls `Agent.pause()` to wait for external approval, the `_PauseManager` registers an `asyncio.Future`. When the control plane sends a webhook callback to the agent's endpoint, the manager resolves the future to resume execution.

**Sources:** [sdk/python/agentfield/agent_pause.py:49-76](), [sdk/python/agentfield/agent_pause.py:78-94]()

---

## Platform Considerations

### Deployment Limitations

- **Async Execution**: Serverless handlers automatically disable async execution polling (`enable_async_execution = False`) because the process terminates after the response.
- **Lease Loop**: Go and Python agents should disable the lease loop (`DisableLeaseLoop: true`) as there is no long-running process to maintain the lease.
- **Authentication**: It is highly recommended to set `AGENTFIELD_AUTHORIZATION_INTERNAL_TOKEN` to ensure the `/execute` endpoint on the serverless function is protected from unauthorized direct calls.

**Sources:** [sdk/python/agentfield/agent_serverless.py:81-82](), [examples/go_agent_nodes/cmd/lambda/main.go:33-33](), [examples/go_agent_nodes/cmd/lambda/main.go:36-41]()

---

# Page: Environment Configuration

# Environment Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [control-plane/cmd/af/main.go](control-plane/cmd/af/main.go)
- [control-plane/cmd/agentfield-server/main.go](control-plane/cmd/agentfield-server/main.go)
- [control-plane/config/agentfield.yaml](control-plane/config/agentfield.yaml)
- [control-plane/internal/config/config.go](control-plane/internal/config/config.go)
- [control-plane/internal/config/config_additional_test.go](control-plane/internal/config/config_additional_test.go)
- [control-plane/internal/core/services/coverage_additional_test.go](control-plane/internal/core/services/coverage_additional_test.go)
- [control-plane/internal/packages/env_resolver.go](control-plane/internal/packages/env_resolver.go)
- [control-plane/internal/packages/env_resolver_additional_test.go](control-plane/internal/packages/env_resolver_additional_test.go)
- [control-plane/internal/packages/env_resolver_group_test.go](control-plane/internal/packages/env_resolver_group_test.go)
- [control-plane/internal/packages/env_resolver_test.go](control-plane/internal/packages/env_resolver_test.go)
- [control-plane/internal/server/middleware/auth.go](control-plane/internal/server/middleware/auth.go)
- [control-plane/internal/server/middleware/auth_admin_additional_test.go](control-plane/internal/server/middleware/auth_admin_additional_test.go)
- [control-plane/internal/server/middleware/auth_test.go](control-plane/internal/server/middleware/auth_test.go)
- [control-plane/internal/server/routes_admin.go](control-plane/internal/server/routes_admin.go)
- [control-plane/internal/server/routes_middleware.go](control-plane/internal/server/routes_middleware.go)
- [control-plane/internal/server/server.go](control-plane/internal/server/server.go)
- [control-plane/internal/server/server_additional_test.go](control-plane/internal/server/server_additional_test.go)
- [control-plane/internal/server/server_coverage_additional_test.go](control-plane/internal/server/server_coverage_additional_test.go)
- [deployments/helm/agentfield/templates/control-plane-deployment.yaml](deployments/helm/agentfield/templates/control-plane-deployment.yaml)
- [docs/ENVIRONMENT_VARIABLES.md](docs/ENVIRONMENT_VARIABLES.md)
- [tests/functional/docker/agentfield-test.yaml](tests/functional/docker/agentfield-test.yaml)

</details>



This page documents environment variables and configuration options for AgentField agents and the control plane. It covers how to configure storage backends, agent registration, API keys, and deployment-specific settings.

For information about deploying to specific platforms, see [Docker Deployment](#13.1), [Railway Deployment](#13.2), or [Serverless Deployment](#13.3). For production setup and optimization, see [Production Considerations](#13.5).

---

## Configuration Overview

AgentField uses a layered configuration system where settings can be specified through:
- Environment variables (prefixed with `AGENTFIELD_`)
- Configuration files (YAML, typically `agentfield.yaml`)
- Command-line flags (via `af` or `agentfield-server` CLI)
- SDK constructor parameters
- Runtime defaults

The control plane uses [Viper](https://github.com/spf13/viper) to map nested YAML keys to environment variables using underscores (e.g., `storage.mode` becomes `AGENTFIELD_STORAGE_MODE`) [docs/ENVIRONMENT_VARIABLES.md:5-6]().

**Sources:** [control-plane/internal/config/config.go:16-25](), [docs/ENVIRONMENT_VARIABLES.md:1-6]()

---

## Configuration Precedence

```mermaid
graph TB
    CLI["CLI Flags<br/>(e.g. --port, --storage-mode)"]
    ENV["Environment Variables<br/>(AGENTFIELD_*, AGENT_*)"]
    FILE["Configuration File<br/>(agentfield.yaml)"]
    SDK["SDK Parameters<br/>(Agent constructor)"]
    DEFAULT["Runtime Defaults"]
    
    CLI -->|"Highest Priority"| ENV
    ENV --> FILE
    FILE --> SDK
    SDK -->|"Lowest Priority"| DEFAULT
    
    RESULT["Final Config Object<br/>config.Config"]
    
    DEFAULT --> RESULT
    SDK --> RESULT
    FILE --> RESULT
    ENV --> RESULT
    CLI --> RESULT
```

**Configuration Resolution Order:**
1. **CLI flags** override all other settings [control-plane/cmd/af/main.go:64-67]().
2. **Environment variables** override file and defaults [control-plane/cmd/af/main.go:70-74]().
3. **Configuration file** values override defaults [control-plane/cmd/af/main.go:57-61]().
4. **SDK parameters** (for agents) override defaults.
5. **Runtime defaults** are used if nothing else is specified.

**Sources:** [control-plane/cmd/af/main.go:53-154](), [control-plane/cmd/agentfield-server/main.go:67-154]()

---

## Agent Environment Variables

### Core Agent Configuration

| Variable | Purpose | Example | Default |
|----------|---------|---------|---------|
| `AGENTFIELD_URL` | Control plane URL for agent registration | `http://localhost:8080` | `http://localhost:8080` |
| `AGENT_CALLBACK_URL` | Public URL where control plane can reach agent | `http://agent.example.com` | Auto-detected |
| `AGENTFIELD_TOKEN` | API key for agent authentication | `ak_...` | None |
| `AGENT_NODE_ID` | Unique identifier for the agent node | `my-agent-01` | Random UUID |

**Sources:** [docs/ENVIRONMENT_VARIABLES.md:109-122]()

#### AGENT_CALLBACK_URL Behavior

The agent must be reachable by the control plane to receive execution requests. In containerized environments like Docker or Kubernetes, this usually requires setting the internal DNS name of the agent service [docs/ENVIRONMENT_VARIABLES.md:99-108]().

---

## Control Plane Environment Variables

### Server Configuration

| Variable | Purpose | Example | Default |
|----------|---------|---------|---------|
| `AGENTFIELD_PORT` | HTTP server port | `8080` | `8080` |
| `AGENTFIELD_HOME` | Base directory for local state (DBs, keys) | `/data` | `~/.agentfield` |
| `AGENTFIELD_CONFIG_FILE` | Path to `agentfield.yaml` | `/etc/agentfield/config.yaml` | None |
| `AGENTFIELD_API_KEY` | Global API key for endpoint protection | `secret-key` | None (Unauthenticated) |

**Sources:** [control-plane/internal/server/server.go:109-116](), [docs/ENVIRONMENT_VARIABLES.md:11-13]()

### Authentication & Authorization

AgentField supports two primary auth mechanisms:
1. **API Key Auth**: Enforced via `X-API-Key` or `Bearer` token [control-plane/internal/server/middleware/auth.go:103-112]().
2. **DID Auth**: Cryptographic identity verification for agent-to-agent calls [control-plane/internal/server/routes_middleware.go:90-102]().

| Variable | Purpose | Default |
|----------|---------|---------|
| `AGENTFIELD_AUTHORIZATION_ENABLED` | Enable VC-based authorization | `false` |
| `AGENTFIELD_AUTHORIZATION_MASTER_SEED` | Seed for deriving Ed25519 DID keys | Required if enabled |
| `AGENTFIELD_API_AUTH_API_KEY` | Alias for `AGENTFIELD_API_KEY` | None |

**Sources:** [control-plane/internal/server/middleware/auth.go:19-40](), [docs/ENVIRONMENT_VARIABLES.md:75-83]()

---

## Storage Configuration

### Storage Mode Selection

The `StorageFactory` initializes the persistence layer based on the `AGENTFIELD_STORAGE_MODE` variable [control-plane/internal/server/server.go:123-127]().

```mermaid
graph TB
    subgraph "Storage Selection Logic"
        START["Server Init"]
        MODE{"AGENTFIELD_STORAGE_MODE"}
        LOCAL["Local Mode<br/>(SQLite + BoltDB)"]
        PG["Postgres Mode<br/>(PostgreSQL + pgvector)"]
    end
    
    START --> MODE
    MODE -->|"'local' or empty"| LOCAL
    MODE -->|"'postgres'"| PG
    
    subgraph "Code Entities"
        Factory["storage.StorageFactory"]
        LocalStorage["infrastorage.LocalStorage"]
        PostgresStorage["infrastorage.PostgresStorage"]
    end
    
    LOCAL --> Factory
    PG --> Factory
    Factory --> LocalStorage
    Factory --> PostgresStorage
```

**Sources:** [control-plane/internal/server/server.go:123-134](), [docs/ENVIRONMENT_VARIABLES.md:21-22]()

---

### Local Storage (SQLite + BoltDB)

When `AGENTFIELD_STORAGE_MODE=local`, AgentField stores data in the `AGENTFIELD_HOME` directory [control-plane/internal/server/server.go:109-116]().

| Variable | Purpose | Default |
|----------|---------|---------|
| `AGENTFIELD_STORAGE_LOCAL_DATABASE_PATH` | Path to SQLite DB | `$AGENTFIELD_HOME/agentfield.db` |
| `AGENTFIELD_STORAGE_LOCAL_KV_STORE_PATH` | Path to BoltDB (Memory) | `$AGENTFIELD_HOME/agentfield.bolt` |

**Sources:** [control-plane/config/agentfield.yaml:69-72](), [docs/ENVIRONMENT_VARIABLES.md:24-26]()

---

### PostgreSQL Configuration

When `AGENTFIELD_STORAGE_MODE=postgres`, the control plane requires connection details.

| Variable | Purpose | Example |
|----------|---------|---------|
| `AGENTFIELD_POSTGRES_URL` | Full DSN (Preferred) | `postgres://user:pass@host:5432/db` |
| `AGENTFIELD_STORAGE_POSTGRES_HOST` | Database host | `localhost` |
| `AGENTFIELD_STORAGE_POSTGRES_PORT` | Database port | `5432` |
| `AGENTFIELD_STORAGE_POSTGRES_USER` | Database user | `agentfield` |
| `AGENTFIELD_STORAGE_POSTGRES_PASSWORD`| Database password | `agentfield` |

**Sources:** [control-plane/cmd/af/main.go:90-129](), [docs/ENVIRONMENT_VARIABLES.md:28-40]()

---

## AI Provider Configuration

While agents typically configure AI providers via code, the SDKs often look for these standard environment variables for zero-config initialization.

| Provider | Variable |
|----------|----------|
| **OpenAI** | `OPENAI_API_KEY` |
| **Anthropic** | `ANTHROPIC_API_KEY` |
| **Google** | `GOOGLE_API_KEY` |
| **Mistral** | `MISTRAL_API_KEY` |
| **Groq** | `GROQ_API_KEY` |
| **OpenRouter** | `OPENROUTER_API_KEY` |

**Sources:** [docs/ENVIRONMENT_VARIABLES.md:123-130]()

---

## Telemetry & Logging

### Telemetry
AgentField collects anonymous usage telemetry by default to improve the product. No prompts, secrets, or PII are collected [docs/ENVIRONMENT_VARIABLES.md:53-58]().

| Variable | Purpose | Default |
|----------|---------|---------|
| `AGENTFIELD_TELEMETRY_ENABLED` | Toggle telemetry | `true` |
| `AGENTFIELD_TELEMETRY_ENDPOINT` | Telemetry sink | `https://agentfield.ai/api/oss/telemetry` |

**Sources:** [control-plane/internal/config/config.go:46-58](), [docs/ENVIRONMENT_VARIABLES.md:59-64]()

### Logging
| Variable | Purpose | Values | Default |
|----------|---------|--------|---------|
| `AGENTFIELD_LOGGING_LEVEL` | Minimum log level | `debug`, `info`, `warn`, `error` | `info` |
| `AGENTFIELD_LOGGING_REDACT_PAYLOADS` | Redact I/O from logs | `true`, `false` | `true` |

**Sources:** [control-plane/internal/config/config.go:28-41](), [control-plane/config/agentfield.yaml:64-66]()

---

## Configuration Data Flow

The following diagram illustrates how configuration flows from the environment into the `AgentFieldServer` instance.

```mermaid
sequenceDiagram
    participant OS as OS Environment
    participant CLI as af CLI (Cobra)
    participant Viper as Viper Config Loader
    participant Cfg as config.Config Object
    participant Srv as AgentFieldServer
    
    OS->>CLI: Read Env Vars
    CLI->>Viper: Load YAML + Overrides
    Viper->>Cfg: Unmarshal into Struct
    Cfg->>Srv: Pass to NewAgentFieldServer(cfg)
    Srv->>Srv: applyGlobalMiddleware() (Auth Setup)
```

**Sources:** [control-plane/cmd/af/main.go:53-171](), [control-plane/internal/server/server.go:107-134](), [control-plane/internal/server/routes_middleware.go:18-110]()

---

# Page: Production Considerations

# Production Considerations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [control-plane/internal/encryption/encryption.go](control-plane/internal/encryption/encryption.go)
- [control-plane/internal/encryption/encryption_test.go](control-plane/internal/encryption/encryption_test.go)
- [control-plane/internal/events/node_events.go](control-plane/internal/events/node_events.go)
- [control-plane/internal/handlers/memory.go](control-plane/internal/handlers/memory.go)
- [control-plane/internal/handlers/memory_handler_test.go](control-plane/internal/handlers/memory_handler_test.go)
- [control-plane/internal/handlers/nodes_discovery_test.go](control-plane/internal/handlers/nodes_discovery_test.go)
- [control-plane/internal/handlers/nodes_test.go](control-plane/internal/handlers/nodes_test.go)
- [control-plane/internal/handlers/vector_memory.go](control-plane/internal/handlers/vector_memory.go)
- [control-plane/internal/handlers/vector_memory_test.go](control-plane/internal/handlers/vector_memory_test.go)
- [control-plane/internal/server/server_routes_test.go](control-plane/internal/server/server_routes_test.go)
- [control-plane/internal/services/health_monitor.go](control-plane/internal/services/health_monitor.go)
- [control-plane/internal/services/health_monitor_test.go](control-plane/internal/services/health_monitor_test.go)
- [control-plane/internal/services/status_manager.go](control-plane/internal/services/status_manager.go)
- [control-plane/internal/services/status_manager_test.go](control-plane/internal/services/status_manager_test.go)
- [control-plane/internal/services/webhook_dispatcher_test.go](control-plane/internal/services/webhook_dispatcher_test.go)
- [control-plane/internal/storage/local.go](control-plane/internal/storage/local.go)
- [control-plane/internal/storage/local_query_test.go](control-plane/internal/storage/local_query_test.go)
- [control-plane/internal/storage/storage.go](control-plane/internal/storage/storage.go)
- [control-plane/internal/storage/vector_store.go](control-plane/internal/storage/vector_store.go)
- [control-plane/internal/storage/vector_store_postgres.go](control-plane/internal/storage/vector_store_postgres.go)
- [control-plane/internal/storage/vector_store_sqlite.go](control-plane/internal/storage/vector_store_sqlite.go)
- [control-plane/pkg/types/execution_payload.go](control-plane/pkg/types/execution_payload.go)
- [control-plane/pkg/types/execution_payload_test.go](control-plane/pkg/types/execution_payload_test.go)
- [control-plane/pkg/types/webhook.go](control-plane/pkg/types/webhook.go)

</details>



This page covers production deployment considerations for AgentField, focusing on database configuration, connection pooling, vector storage, and system monitoring. AgentField's control plane is designed to transition from local development to high-availability production environments by switching from SQLite to PostgreSQL.

## Storage Backend Selection

AgentField supports two primary storage modes: `local` (SQLite + BoltDB) for development and `postgres` for production workloads. The `StorageProvider` interface abstracts these backends, allowing the system to scale without code changes [control-plane/internal/storage/storage.go:44-142]().

### Mode Comparison

| Aspect | Local Mode (SQLite) | Postgres Mode |
|--------|-------------------|---------------|
| **Best For** | Development, single-instance | Production, distributed scaling |
| **Concurrency** | WAL mode: concurrent reads, single writer | Full concurrent read/write support |
| **Vector Search** | `sqlite-vss` or in-memory | `pgvector` extension |
| **Scalability** | Single server | Horizontal scaling via read replicas |
| **Data Flow** | Direct file I/O | Networked TCP connections |

**Sources:** [control-plane/internal/storage/local.go:478-502](), [control-plane/internal/storage/storage.go:44-142]()

### Configuration Architecture

The `StorageConfig` struct manages the initialization parameters for the selected backend. When `AGENTFIELD_STORAGE_MODE` is set to `postgres`, the system initializes a `postgresVectorStore` and a SQL-based primary store [control-plane/internal/storage/storage.go:207-255]().

```mermaid
graph TB
    subgraph "Storage Configuration Flow"
        Env["Environment Variables"]
        Config["StorageConfig Struct"]
        Factory["StorageFactory"]
        
        Env -->|AGENTFIELD_STORAGE_MODE| Config
        Config --> Factory
        
        Factory -->|mode=local| LocalStorage["LocalStorage (SQLite)"]
        Factory -->|mode=postgres| PgStorage["PostgreSQL Instance"]
        
        PgStorage --> PostgresDB["PostgreSQL DB"]
        PgStorage --> VectorStore["postgresVectorStore"]
    end
    
    subgraph "Code Entities"
        LocalStorageEntity["storage.LocalStorage"]
        PgVectorEntity["storage.postgresVectorStore"]
        InitFunc["Initialize(ctx, config)"]
        
        PgStorage --- LocalStorageEntity
        VectorStore --- PgVectorEntity
        Factory --- InitFunc
    end
```

**Sources:** [control-plane/internal/storage/storage.go:207-255](), [control-plane/internal/storage/local.go:1-30](), [control-plane/internal/storage/vector_store_postgres.go:15-25]()

## PostgreSQL Configuration

### Connection Pooling

In production, managing database connections is critical for performance. AgentField uses `sql.DB` connection pooling, configured via `PostgresStorageConfig` [control-plane/internal/storage/local.go:706-728]().

| Setting | Default | Purpose |
|---------|---------|---------|
| `MaxOpenConns` | 25 | Maximum concurrent connections to PostgreSQL |
| `MaxIdleConns` | 5 | Idle connections kept in the pool |
| `ConnMaxLifetime` | 30m | Maximum time a connection can be reused |

**Sources:** [control-plane/internal/storage/local.go:706-728]()

### Database Auto-Initialization

AgentField attempts to create the target database if it is missing during startup. It uses an `admin_database` (defaulting to `postgres`) to execute the `CREATE DATABASE` command if a `3D000` (database does not exist) error is caught [control-plane/internal/storage/local.go:668-703]().

```mermaid
sequenceDiagram
    participant S as Storage.Initialize
    participant P as Postgres (Target DB)
    participant A as Postgres (Admin DB)
    
    S->>P: PingContext()
    alt Database Missing (Error 3D000)
        S->>A: Connect to admin_database
        S->>A: Exec("CREATE DATABASE ...")
        S-->>A: Success
        S->>P: Reconnect to Target DB
    end
    S->>P: Run Migrations / createSchema()
```

**Sources:** [control-plane/internal/storage/local.go:668-703](), [control-plane/internal/storage/local.go:730-800]()

## Vector Storage and RAG

For production RAG (Retrieval-Augmented Generation), AgentField utilizes the `pgvector` extension in PostgreSQL. The `postgresVectorStore` handles embedding storage and similarity searches [control-plane/internal/storage/vector_store_postgres.go:1-18]().

### Vector Operations

The `SimilaritySearch` function performs vector lookups using configurable distance metrics (Cosine, L2, or Dot Product) [control-plane/internal/storage/vector_store_postgres.go:153-228]().

| Function | Implementation Detail |
|----------|-----------------------|
| `Set()` | Uses `INSERT ... ON CONFLICT` for upserts [control-plane/internal/storage/vector_store_postgres.go:27-66]() |
| `Search()` | Employs `CROSS JOIN` with a query vector CTE [control-plane/internal/storage/vector_store_postgres.go:153-170]() |
| `DeleteByPrefix()` | Supports hierarchical memory cleanup using `LIKE` [control-plane/internal/storage/vector_store_postgres.go:132-151]() |

**Sources:** [control-plane/internal/storage/vector_store_postgres.go:27-228]()

## Monitoring and Agent Health

Production environments rely on the `StatusManager` and `HealthMonitor` to track the state of distributed agent nodes [control-plane/internal/services/status_manager.go:26-45]().

### Health Monitoring Flow

The `HealthMonitor` performs periodic HTTP probes against agent `/status` endpoints. If an agent fails consecutive checks, its `HealthScore` is reduced to 0 and its state is marked as `Inactive` [control-plane/internal/services/health_monitor.go:16-24]().

```mermaid
graph LR
    subgraph "Monitoring System"
        HM["HealthMonitor.CheckLoop"]
        SM["StatusManager.UpdateAgentStatus"]
        AC["AgentClient.GetAgentStatus"]
    end

    subgraph "State Entities"
        Active["types.AgentStateActive"]
        Inactive["types.AgentStateInactive"]
        Update["types.AgentStatusUpdate"]
    end

    HM --> AC
    AC -->|Failure| SM
    SM -->|Persist| Inactive
    AC -->|Success| SM
    SM -->|Persist| Active
```

**Sources:** [control-plane/internal/services/health_monitor.go:47-90](), [control-plane/internal/services/status_manager.go:124-201](), [control-plane/internal/services/health_monitor_test.go:147-168]()

### Webhook Reliability

In production, workflow completions often trigger external webhooks. The `WebhookDispatcher` handles retries with exponential backoff and manages "in-flight" states to prevent duplicate deliveries in multi-instance control plane setups [control-plane/internal/services/webhook_dispatcher_test.go:113-130]().

- **Worker Count:** Configurable concurrency for webhook processing [control-plane/internal/services/webhook_dispatcher_test.go:113-125]().
- **Retry Logic:** Uses `TryMarkExecutionWebhookInFlight` to ensure atomicity across control plane instances [control-plane/internal/services/webhook_dispatcher_test.go:49-60]().

**Sources:** [control-plane/internal/services/webhook_dispatcher_test.go:49-130]()

## Performance Optimization

### Indexing and FTS

AgentField creates several indexes to maintain query performance as the database grows, including GIN indexes for Full-Text Search (FTS) on workflow names and tags [control-plane/internal/storage/local.go:1031-1089]().

### Memory Scoping

The `MemoryStorage` handlers resolve scopes (workflow, session, actor, global) dynamically from HTTP headers (`X-Workflow-ID`, `X-Session-ID`). In production, these should be populated by the SDK or a gateway to ensure proper data isolation [control-plane/internal/handlers/memory.go:172-192]().

**Sources:** [control-plane/internal/handlers/memory.go:172-218](), [control-plane/internal/handlers/memory_handler_test.go:119-155]()

---

# Page: Desktop Application

# Desktop Application

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [VERSION](VERSION)
- [control-plane/internal/encryption/encryption.go](control-plane/internal/encryption/encryption.go)
- [control-plane/internal/encryption/encryption_test.go](control-plane/internal/encryption/encryption_test.go)
- [control-plane/internal/events/node_events.go](control-plane/internal/events/node_events.go)
- [control-plane/internal/handlers/nodes_discovery_test.go](control-plane/internal/handlers/nodes_discovery_test.go)
- [control-plane/internal/handlers/nodes_test.go](control-plane/internal/handlers/nodes_test.go)
- [control-plane/internal/services/health_monitor.go](control-plane/internal/services/health_monitor.go)
- [control-plane/internal/services/health_monitor_test.go](control-plane/internal/services/health_monitor_test.go)
- [control-plane/internal/services/status_manager.go](control-plane/internal/services/status_manager.go)
- [control-plane/internal/services/status_manager_test.go](control-plane/internal/services/status_manager_test.go)
- [control-plane/internal/services/webhook_dispatcher_test.go](control-plane/internal/services/webhook_dispatcher_test.go)
- [control-plane/internal/storage/local_query_test.go](control-plane/internal/storage/local_query_test.go)
- [control-plane/internal/templates/go/go.mod.tmpl](control-plane/internal/templates/go/go.mod.tmpl)
- [control-plane/pkg/types/execution_payload.go](control-plane/pkg/types/execution_payload.go)
- [control-plane/pkg/types/execution_payload_test.go](control-plane/pkg/types/execution_payload_test.go)
- [control-plane/pkg/types/webhook.go](control-plane/pkg/types/webhook.go)
- [examples/python_agent_nodes/agentic_rag/requirements.txt](examples/python_agent_nodes/agentic_rag/requirements.txt)
- [examples/python_agent_nodes/documentation_chatbot/requirements.txt](examples/python_agent_nodes/documentation_chatbot/requirements.txt)
- [examples/python_agent_nodes/hello_world_rag/requirements.txt](examples/python_agent_nodes/hello_world_rag/requirements.txt)
- [sdk/python/CHANGELOG.md](sdk/python/CHANGELOG.md)
- [sdk/python/agentfield/__init__.py](sdk/python/agentfield/__init__.py)
- [sdk/python/pyproject.toml](sdk/python/pyproject.toml)
- [sdk/python/tests/test_execution_logger.py](sdk/python/tests/test_execution_logger.py)
- [sdk/typescript/package.json](sdk/typescript/package.json)

</details>



The AgentField Desktop application is a cross-platform companion dashboard designed to simplify the management of the local control plane, agent nodes, and installed agents. Modeled after developer tools like Docker Desktop, it provides a graphical interface for non-technical users and developers to monitor system health, manage agent lifecycles, and configure environment secrets without deep CLI knowledge.

## High-Level Architecture

The desktop application is built using **Electron**, **React**, and **TypeScript**. It adheres to a strict security model to protect local system resources while providing deep integration with the AgentField ecosystem.

### Security and Isolation
The app employs a sandboxed renderer with `contextIsolation` enabled and `nodeIntegration` disabled [CHANGELOG.md:24-26](). Communication between the UI and the underlying system occurs through a secure `contextBridge` API, ensuring that the frontend cannot execute arbitrary system commands.

### Core Components
*   **Electron Main Process**: Manages system-level operations, including process management for the local control plane and the `af-tray` companion.
*   **React Renderer**: Provides the "Docker-Desktop-style" dashboard [CHANGELOG.md:18-18]().
*   **AgentField Service Layer**: A dedicated module (`src/main/agentfield.ts`) that handles data fetching, registry parsing, and health mapping [CHANGELOG.md:26-29]().

### Component Interaction Diagram

This diagram illustrates how the Desktop Application (Code Entity Space) interacts with the local environment (Natural Language Space).

```mermaid
graph TD
    subgraph "Desktop Application (Electron)"
        UI["React Dashboard UI"]
        Bridge["contextBridge API"]
        Main["Main Process (src/main/agentfield.ts)"]
    end

    subgraph "Local System"
        CLI["af CLI Binary"]
        Config["~/.agentfield/installed.yaml"]
        CP["Control Plane (localhost:8080)"]
    end

    UI <--> Bridge
    Bridge <--> Main
    Main -- "Reads Registry" --> Config
    Main -- "Invokes Commands" --> CLI
    Main -- "GET /health" --> CP
    Main -- "GET /api/v1/nodes" --> CP
```
Sources: [CHANGELOG.md:16-30]()

## Key Features & Views

The application provides several high-level views to manage the agent lifecycle:

*   **Dashboard**: A unified view showing the global health of the control plane (via `GET /health`) and a summary of active nodes [CHANGELOG.md:18-20]().
*   **Agents View**: Lists locally installed agents from `~/.agentfield/installed.yaml`. It cross-references these against the running control plane to display status badges (Running, Stopped, or Unknown) [CHANGELOG.md:19-21]().
*   **Activity**: Visualizes recent logs and execution events.
*   **Settings**: Configuration for the local control plane, including port management and storage paths.

For details on the UI implementation and IPC security, see [Desktop Overview & Views](#14.1).

## CLI and Provisioning

The desktop app acts as a manager for the `af` CLI. It handles the resolution of the binary across three tiers:
1.  **Managed**: Binaries downloaded and managed by the app.
2.  **PATH**: Existing installations found on the user's system.
3.  **Bundled**: A fallback version included with the desktop installer [CHANGELOG.md:14-14]().

On macOS, the app also manages the `af-tray` companion, which provides quick access to system status from the menu bar.

For details on how the app manages local binaries and environment paths, see [CLI Resolution & Auto-provisioning](#14.2).

## Secret Management

The desktop app provides a secure UI for managing `user_environment` declarations. It allows users to input sensitive API keys (e.g., for OpenAI or Anthropic) which are then stored using **AES-256-GCM** encryption. 

The app integrates with the CLI's secret store by securely piping data to `af secrets set` via `stdin`, ensuring that sensitive values never appear in process logs or shell history.

For details on the encryption model and secret UI, see [Agent Keys & Secrets UI](#14.3).

## Platform Support

The application is designed for multi-platform compatibility, with specific logic to handle the differences between Unix-like systems and Windows.

| Feature | macOS / Linux | Windows |
| :--- | :--- | :--- |
| **Process Control** | SIGINT / Signal-0 [CHANGELOG.md:53-54]() | `taskkill` / `tasklist` [CHANGELOG.md:57-58]() |
| **Log Tailing** | `tail -f` [CHANGELOG.md:68-69]() | `Get-Content -Wait` [CHANGELOG.md:70-71]() |
| **Python Probe** | `python3` [CHANGELOG.md:149-150]() | `py` launcher / Store stubs [CHANGELOG.md:140-144]() |
| **Binary Suffix** | None | `.exe` [CHANGELOG.md:78-80]() |

Sources: [CHANGELOG.md:51-100](), [CHANGELOG.md:131-152]()

---

# Page: Desktop Overview & Views

# Desktop Overview & Views

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [VERSION](VERSION)
- [control-plane/internal/handlers/ui/workflow_runs.go](control-plane/internal/handlers/ui/workflow_runs.go)
- [control-plane/internal/handlers/ui/workflow_runs_helpers_test.go](control-plane/internal/handlers/ui/workflow_runs_helpers_test.go)
- [control-plane/internal/storage/execution_records_test.go](control-plane/internal/storage/execution_records_test.go)
- [control-plane/internal/templates/go/go.mod.tmpl](control-plane/internal/templates/go/go.mod.tmpl)
- [control-plane/web/client/src/App.tsx](control-plane/web/client/src/App.tsx)
- [control-plane/web/client/src/components/StepDetail.tsx](control-plane/web/client/src/components/StepDetail.tsx)
- [control-plane/web/client/src/config/navigation.ts](control-plane/web/client/src/config/navigation.ts)
- [control-plane/web/client/src/pages/NewSettingsPage.tsx](control-plane/web/client/src/pages/NewSettingsPage.tsx)
- [control-plane/web/client/src/pages/RunsPage.tsx](control-plane/web/client/src/pages/RunsPage.tsx)
- [control-plane/web/client/src/services/executionsApi.ts](control-plane/web/client/src/services/executionsApi.ts)
- [control-plane/web/client/src/services/workflowsApi.ts](control-plane/web/client/src/services/workflowsApi.ts)
- [control-plane/web/client/src/test/components/StepDetail.test.tsx](control-plane/web/client/src/test/components/StepDetail.test.tsx)
- [control-plane/web/client/src/test/pages/RunsPage.test.tsx](control-plane/web/client/src/test/pages/RunsPage.test.tsx)
- [control-plane/web/client/src/types/workflows.ts](control-plane/web/client/src/types/workflows.ts)
- [control-plane/web/client/src/utils/executionErrorCategory.test.ts](control-plane/web/client/src/utils/executionErrorCategory.test.ts)
- [control-plane/web/client/src/utils/executionErrorCategory.ts](control-plane/web/client/src/utils/executionErrorCategory.ts)
- [examples/python_agent_nodes/agentic_rag/requirements.txt](examples/python_agent_nodes/agentic_rag/requirements.txt)
- [examples/python_agent_nodes/documentation_chatbot/requirements.txt](examples/python_agent_nodes/documentation_chatbot/requirements.txt)
- [examples/python_agent_nodes/hello_world_rag/requirements.txt](examples/python_agent_nodes/hello_world_rag/requirements.txt)
- [sdk/python/CHANGELOG.md](sdk/python/CHANGELOG.md)
- [sdk/python/agentfield/__init__.py](sdk/python/agentfield/__init__.py)
- [sdk/python/pyproject.toml](sdk/python/pyproject.toml)
- [sdk/python/tests/test_execution_logger.py](sdk/python/tests/test_execution_logger.py)
- [sdk/typescript/package.json](sdk/typescript/package.json)

</details>



The AgentField Desktop application is a "Docker Desktop-style" companion for managing the local control plane and agent nodes. It provides a graphical interface for non-technical users to monitor system health, manage installed agents, and view activity logs across the AgentField ecosystem.

## Core Architecture

The desktop application is built using Electron with a React-based frontend. It follows a strict security model to isolate the renderer process from sensitive system operations.

### Electron Security Model
The application implements the following security constraints:
*   **`contextIsolation`**: Enabled to ensure the renderer and main processes run in separate contexts [CHANGELOG.md:24-25]().
*   **`nodeIntegration`**: Disabled in the renderer to prevent direct access to Node.js APIs [CHANGELOG.md:25]().
*   **`contextBridge`**: A single, unified API bridge is used for all communication between the renderer and the main process [CHANGELOG.md:26]().
*   **Sandboxing**: The renderer process is sandboxed to limit its access to the host operating system [CHANGELOG.md:25]().

### IPC and Data Flow
Data access is centralized in `src/main/agentfield.ts`. This module serves as the primary seam for interacting with the local system, including reading the agent registry and polling the control plane [CHANGELOG.md:26-28]().

| Component | Responsibility |
| :--- | :--- |
| **Main Process** | Manages the lifecycle of the Electron app, handles system-level calls (FS, Process), and manages the tray icon [CHANGELOG.md:14,26-28](). |
| **Renderer Process** | React-based UI that displays the Dashboard, Agents, and Activity views [CHANGELOG.md:24](). |
| **Agent Registry** | Located at `~/.agentfield/installed.yaml`, it tracks locally installed agent nodes [CHANGELOG.md:19-20](). |
| **Control Plane API** | The UI polls `GET /health` and `GET /api/v1/nodes` to synchronize the state of local agents [CHANGELOG.md:18-21](). |

**Sources:** [CHANGELOG.md:14-35]()

## System Views

The application is organized into several primary views, each focused on a specific aspect of the AgentField lifecycle.

### 1. Dashboard View
The Dashboard provides a high-level overview of the Control Plane health. It utilizes the `GET /health` endpoint to display a "Running" or "Stopped" status for the local server [CHANGELOG.md:18-19]().

### 2. Agents View
This view manages the lifecycle of Agent Nodes. It cross-references the local registry (`~/.agentfield/installed.yaml`) with the active nodes reported by the control plane [CHANGELOG.md:19-21]().
*   **Status Badges**: Each agent is assigned a badge: `Running`, `Stopped`, or `Unknown` [CHANGELOG.md:21]().
*   **Polling**: The view polls the control plane every 5 seconds to ensure the UI remains synchronized with the backend [CHANGELOG.md:21-22]().

### 3. Activity View
The Activity view provides visibility into the execution of workflows and reasoners. It visualizes the data returned by the `WorkflowRunHandler` in the control plane [control-plane/internal/handlers/ui/workflow_runs.go:21-27]().

#### Execution Details
When a specific execution is selected, the `StepDetail` component displays:
*   **Provenance**: Displays `caller_did` and `target_did` to show the cryptographic identity chain [control-plane/web/client/src/components/StepDetail.tsx:126-134]().
*   **Input/Output**: Formatted JSON blocks showing the data passed to and from reasoners or skills [control-plane/web/client/src/components/StepDetail.tsx:170-171]().
*   **Status & Errors**: Detailed error categories and messages for failed steps [control-plane/web/client/src/components/StepDetail.tsx:192, control-plane/web/client/src/utils/executionErrorCategory.ts:1-10]().

### 4. Settings View
The Settings view allows users to configure the application and manage environment variables. It handles the resolution of the `af` CLI tool, allowing users to switch between a bundled version or a system-wide PATH version [CHANGELOG.md:14]().

**Sources:** [CHANGELOG.md:14-23](), [control-plane/internal/handlers/ui/workflow_runs.go:21-65](), [control-plane/web/client/src/components/StepDetail.tsx:158-195]()

## Technical Implementation Diagrams

### Desktop Process Architecture
The following diagram illustrates the relationship between the Electron processes and the AgentField Control Plane.

```mermaid
graph TD
    subgraph "Electron Main Process"
        AF_MAIN["src/main/agentfield.ts"]
        REGISTRY_READER["Registry Parser (installed.yaml)"]
        IPC_HANDLER["IPC Handler"]
    end

    subgraph "Electron Renderer Process (React)"
        DASHBOARD["Dashboard View"]
        AGENTS_VIEW["Agents View"]
        STEP_DETAIL["StepDetail.tsx"]
        BRIDGE_API["contextBridge API"]
    end

    subgraph "Local Filesystem"
        INSTALLED_YAML["~/.agentfield/installed.yaml"]
    end

    subgraph "Control Plane (Go)"
        HEALTH_API["GET /health"]
        NODES_API["GET /api/v1/nodes"]
        WF_HANDLER["WorkflowRunHandler"]
    end

    BRIDGE_API <== "IPC" ==> IPC_HANDLER
    IPC_HANDLER --> AF_MAIN
    AF_MAIN --> REGISTRY_READER
    REGISTRY_READER -.-> INSTALLED_YAML
    AF_MAIN -- "HTTP Poll (5s)" --> HEALTH_API
    AF_MAIN -- "HTTP Poll (5s)" --> NODES_API
    DASHBOARD --> BRIDGE_API
    AGENTS_VIEW --> BRIDGE_API
    STEP_DETAIL -- "Fetch Data" --> WF_HANDLER
```
**Sources:** [CHANGELOG.md:16-31](), [control-plane/internal/handlers/ui/workflow_runs.go:146-160]()

### Workflow Run Data Mapping
This diagram maps the UI entities in the Activity view to the Go structs defined in the Control Plane backend.

```mermaid
classDiagram
    class WorkflowRunSummary {
        +String WorkflowID
        +String RunID
        +String Status
        +String RootReasoner
        +Time StartedAt
    }
    class apiWorkflowExecution {
        +String ExecutionID
        +String AgentNodeID
        +String ReasonerID
        +String Status
        +Int WorkflowDepth
    }
    class StepDetail_UI {
        +caller_did
        +target_did
        +input_data
        +output_data
    }

    WorkflowRunSummary "1" -- "*" apiWorkflowExecution : contains
    apiWorkflowExecution -- StepDetail_UI : populates
```
**Sources:** [control-plane/internal/handlers/ui/workflow_runs.go:29-65](), [control-plane/internal/handlers/ui/workflow_runs.go:125-144](), [control-plane/web/client/src/components/StepDetail.tsx:158-195]()

## UI Components and Interaction

### StepDetail Component
The `StepDetail` component is the primary interface for inspecting individual execution units. It is highly interactive and provides the following features:

*   **cURL Generation**: Users can copy a cURL snippet to reproduce the execution locally [control-plane/web/client/src/components/StepDetail.tsx:45-53]().
*   **Workflow Lineage**: Displays the relationship between parent and child executions using `WorkflowID` and `ExecutionID` [control-plane/web/client/src/components/StepDetail.tsx:102-136]().
*   **Webhook Retries**: Provides a UI to trigger retries for failed webhooks associated with an execution [control-plane/web/client/src/components/StepDetail.tsx:36,201-202]().

### Status Mapping
The UI maps internal Go status strings to visual badges. The `WorkflowRunSummary` aggregates statuses from child executions to provide a top-level run state [control-plane/internal/handlers/ui/workflow_runs.go:38-41]().

| Backend Status | UI Badge |
| :--- | :--- |
| `running` | Active/Spinning |
| `completed` | Success (Green) |
| `failed` | Error (Red) |
| `pending` | Waiting |

**Sources:** [control-plane/web/client/src/components/StepDetail.tsx:1-180](), [control-plane/internal/handlers/ui/workflow_runs.go:29-65]()

---

# Page: CLI Resolution & Auto-provisioning

# CLI Resolution & Auto-provisioning

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/release.yml](.github/workflows/release.yml)
- [.goreleaser.yml](.goreleaser.yml)
- [CHANGELOG.md](CHANGELOG.md)
- [VERSION](VERSION)
- [control-plane/internal/templates/docker/docker-compose.yml.tmpl](control-plane/internal/templates/docker/docker-compose.yml.tmpl)
- [control-plane/internal/templates/go/go.mod.tmpl](control-plane/internal/templates/go/go.mod.tmpl)
- [deployments/helm/agentfield/values.yaml](deployments/helm/agentfield/values.yaml)
- [deployments/kubernetes/base/control-plane-deployment.yaml](deployments/kubernetes/base/control-plane-deployment.yaml)
- [docs/RELEASE.md](docs/RELEASE.md)
- [examples/python_agent_nodes/agentic_rag/requirements.txt](examples/python_agent_nodes/agentic_rag/requirements.txt)
- [examples/python_agent_nodes/documentation_chatbot/requirements.txt](examples/python_agent_nodes/documentation_chatbot/requirements.txt)
- [examples/python_agent_nodes/hello_world_rag/requirements.txt](examples/python_agent_nodes/hello_world_rag/requirements.txt)
- [examples/python_agent_nodes/rag_evaluation/docker-compose.yml](examples/python_agent_nodes/rag_evaluation/docker-compose.yml)
- [examples/triggers-demo/docker-compose.yml](examples/triggers-demo/docker-compose.yml)
- [scripts/bump_version.py](scripts/bump_version.py)
- [scripts/install.ps1](scripts/install.ps1)
- [scripts/install.sh](scripts/install.sh)
- [scripts/tests/__init__.py](scripts/tests/__init__.py)
- [scripts/tests/test_bump_version.py](scripts/tests/test_bump_version.py)
- [sdk/go/ai/openrouter_attribution.go](sdk/go/ai/openrouter_attribution.go)
- [sdk/python/CHANGELOG.md](sdk/python/CHANGELOG.md)
- [sdk/python/agentfield/__init__.py](sdk/python/agentfield/__init__.py)
- [sdk/python/pyproject.toml](sdk/python/pyproject.toml)
- [sdk/python/tests/test_execution_logger.py](sdk/python/tests/test_execution_logger.py)
- [sdk/typescript/package.json](sdk/typescript/package.json)

</details>



The AgentField Desktop application acts as a management layer for the `af` CLI, ensuring that users have a consistent experience regardless of whether they are technical developers or non-technical users. It handles the resolution of the binary across multiple possible locations and manages the lifecycle of companion tools like the macOS tray.

## CLI Resolution Strategy

The desktop application and the `install.sh` script prioritize different binary locations to ensure stability and compatibility. The system resolves the `af` binary using a tiered approach:

1.  **Managed Path**: The standard location for binaries installed via the official installer, typically `~/.agentfield/bin/af` [scripts/install.sh:142-143]().
2.  **System PATH**: Any `af` binary currently available in the user's environment `$PATH`.
3.  **Bundled/Staging**: For pre-release testing, binaries may be located in `~/.agentfield-staging/bin/af-staging` [scripts/install.sh:138-140]().

### Platform-Specific Binary Naming
On Windows, the system is aware of `.exe` extensions. The build process for Windows appends `.exe` automatically [CHANGELOG.md:37-41](). When the desktop app or control plane attempts to resolve binaries (such as Go agent nodes), it uses logic to fallback to `.exe` suffixes if the base name is not found [CHANGELOG.md:76-85]().

### CLI Resolution Logic
Title: CLI Path Resolution Flow
```mermaid
graph TD
    "Start" --> "CheckManagedPath[Check ~/.agentfield/bin/af]"
    "CheckManagedPath" -- "Exists" --> "UseManaged[Use Managed CLI]"
    "CheckManagedPath" -- "Not Found" --> "CheckPath[Check System PATH]"
    "CheckPath" -- "Exists" --> "UsePath[Use PATH CLI]"
    "CheckPath" -- "Not Found" --> "Provision[Trigger Auto-provisioning]"
    "Provision" --> "Download[Fetch from GitHub Releases]"
    "Download" --> "Install[Write to ~/.agentfield/bin/af]"
    "Install" --> "UseManaged"
```
Sources: [scripts/install.sh:137-145](), [CHANGELOG.md:76-85]()

## Auto-provisioning & ~/.agentfield/bin

The `install.sh` script (and its Windows counterpart `install.ps1`) is responsible for the initial provisioning of the AgentField environment.

### Provisioning Steps
1.  **Directory Creation**: The installer creates the base directory at `~/.agentfield/bin` [scripts/install.sh:142]().
2.  **Architecture Detection**: The script detects the host OS and architecture (e.g., `darwin-arm64`, `linux-amd64`) to fetch the correct binary from GitHub Releases [scripts/install.sh:11-12](), [.goreleaser.yml:198-204]().
3.  **Binary Deployment**: The `af` binary is downloaded and made executable in the bin directory.
4.  **PATH Configuration**: Unless skipped via `SKIP_PATH_CONFIG=1`, the script attempts to append the bin directory to the user's shell profile (`.zshrc`, `.bashrc`) [scripts/install.sh:122]().

### Implementation Entities
| Entity | Role | File |
| :--- | :--- | :--- |
| `INSTALL_DIR` | Defines the target path for auto-provisioning (`~/.agentfield/bin`). | [scripts/install.sh:142]() |
| `SYMLINK_NAME` | The command name used in the shell (`af`). | [scripts/install.sh:143]() |
| `agentfield-windows-amd64` | The build target for Windows CLI provisioning. | [.goreleaser.yml:130-148]() |
| `agentfield-darwin-arm64` | The build target for Apple Silicon provisioning. | [.goreleaser.yml:70-87]() |

Sources: [scripts/install.sh:137-145](), [.goreleaser.yml:12-148]()

## macOS Companion: af-tray

On macOS, the desktop experience is augmented by `af-tray`, a menu-bar companion that provides quick access to control plane status and logs.

### Tray Management
The `af-tray` is a separate, lightweight binary from the main `af` CLI. It is specifically designed to handle Cocoa/systray dependencies via CGO, which keeps the main `af` binary free of UI-related library requirements [.goreleaser.yml:89-91]().

*   **Installation**: The installer fetches `af-tray` only on macOS platforms [scripts/install.sh:38-42]().
*   **Auto-start**: The tray and the control plane are registered to start automatically via `launchd` on macOS [scripts/install.sh:38-40]().
*   **Opt-out**: Users can skip tray installation by passing `--no-tray` or setting `TRAY_MODE=none` [scripts/install.sh:89-92]().

### Tray vs. Control Plane Architecture
Title: macOS Companion Process Relationship
```mermaid
graph BT
    subgraph "User Space"
        "af-tray[af-tray binary]" -- "Monitors" --> "ControlPlane[af server process]"
        "DesktopApp[Electron App]" -- "IPC / CLI" --> "ControlPlane"
    end
    subgraph "System Services"
        "Launchd[launchd]" -- "Auto-starts" --> "af-tray"
        "Launchd" -- "Auto-starts" --> "ControlPlane"
    end
    "af-tray" -- "UI Interaction" --> "User[Menu Bar]"
```
Sources: [scripts/install.sh:36-43](), [.goreleaser.yml:89-123]()

## Platform Compatibility Layer

To support cross-platform CLI resolution, the codebase utilizes build-tagged helpers to handle differences in process management and shell commands.

### Key Compatibility Helpers
*   **Process Management**: Unix platforms use `SIGINT` and signal-0 probes, while Windows uses `taskkill` and `tasklist` PID queries [CHANGELOG.md:51-64]().
*   **Log Tailing**: The `af logs` command resolves to `tail -f` on Unix and `Get-Content -Tail -Wait` via PowerShell on Windows [CHANGELOG.md:67-74]().
*   **Python Discovery**: The system probes for working interpreters (checking `python3`, `python`, and the Windows `py` launcher) by executing a version query to avoid "app execution alias" stubs that exit with code 9009 [CHANGELOG.md:130-147]().

Sources: [CHANGELOG.md:51-147]()

---

# Page: Agent Keys & Secrets UI

# Agent Keys & Secrets UI

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [VERSION](VERSION)
- [control-plane/internal/cli/list.go](control-plane/internal/cli/list.go)
- [control-plane/internal/cli/secrets.go](control-plane/internal/cli/secrets.go)
- [control-plane/internal/packages/git.go](control-plane/internal/packages/git.go)
- [control-plane/internal/packages/git_summary_test.go](control-plane/internal/packages/git_summary_test.go)
- [control-plane/internal/packages/pyinterp.go](control-plane/internal/packages/pyinterp.go)
- [control-plane/internal/packages/pyinterp_test.go](control-plane/internal/packages/pyinterp_test.go)
- [control-plane/internal/packages/spinner_test.go](control-plane/internal/packages/spinner_test.go)
- [control-plane/internal/templates/go/go.mod.tmpl](control-plane/internal/templates/go/go.mod.tmpl)
- [control-plane/internal/ui/ui.go](control-plane/internal/ui/ui.go)
- [control-plane/internal/ui/ui_test.go](control-plane/internal/ui/ui_test.go)
- [examples/python_agent_nodes/agentic_rag/requirements.txt](examples/python_agent_nodes/agentic_rag/requirements.txt)
- [examples/python_agent_nodes/documentation_chatbot/requirements.txt](examples/python_agent_nodes/documentation_chatbot/requirements.txt)
- [examples/python_agent_nodes/hello_world_rag/requirements.txt](examples/python_agent_nodes/hello_world_rag/requirements.txt)
- [sdk/python/CHANGELOG.md](sdk/python/CHANGELOG.md)
- [sdk/python/agentfield/__init__.py](sdk/python/agentfield/__init__.py)
- [sdk/python/pyproject.toml](sdk/python/pyproject.toml)
- [sdk/python/tests/test_execution_logger.py](sdk/python/tests/test_execution_logger.py)
- [sdk/typescript/package.json](sdk/typescript/package.json)

</details>



The AgentField Desktop application provides a graphical interface for managing sensitive configuration and environment variables required by AI agents. It serves as a visual frontend for the underlying `af secrets` CLI infrastructure, allowing users to securely store API keys and environment-specific credentials using AES-256-GCM encryption.

## Secret Management Architecture

The Desktop app integrates with the `af` CLI's secret store, which is located in the user's home directory. Secrets are managed at two levels: **Global** (shared across all agents) and **Node-scoped** (specific to a single agent node).

### Encryption and Storage
Secrets are stored at rest in `~/.agentfield/secrets.json` (or a similar path derived from the home directory) [control-plane/internal/cli/secrets.go:21-26](). The implementation uses **AES-256-GCM** to ensure confidentiality and integrity. Secrets are only decrypted into an agent's process environment at the moment of execution (`af run`) [control-plane/internal/cli/secrets.go:73-74]().

### Data Flow: Desktop to CLI
The Desktop UI interacts with secrets by invoking the `af secrets` command tree through a secure IPC bridge. This ensures that the Desktop app does not need to reimplement the cryptographic logic.

| Command | Desktop Action | CLI Implementation |
| :--- | :--- | :--- |
| `af secrets set` | User saves a new key/value pair in the Keys Editor. | `newSecretsSetCommand` [control-plane/internal/cli/secrets.go:39-83]() |
| `af secrets ls` | Desktop populates the "Keys" view list. | `newSecretsListCommand` [control-plane/internal/cli/secrets.go:85-118]() |
| `af secrets rm` | User clicks the "Delete" icon on a secret row. | `newSecretsRemoveCommand` [control-plane/internal/cli/secrets.go:120-145]() |

**Sources:**
- `control-plane/internal/cli/secrets.go`
- `CHANGELOG.md`

## User Environment Declarations

Agents can declare required environment variables in their manifest files. The Desktop app surfaces these declarations to guide the user in providing necessary keys (e.g., `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`).

### Environment Injection Logic
When a node is started via the Desktop app (which triggers `af run`), the control plane performs a hierarchical lookup to populate the process environment:
1. **Node-scoped Secrets**: Overrides any global values for that specific agent [control-plane/internal/cli/secrets.go:24-26]().
2. **Global Secrets**: Shared keys available to all agents.
3. **Local Shell Environment**: Variables already present in the user's shell.

### Secure Stdin Integration
To prevent sensitive keys from appearing in shell history, the Desktop app utilizes the `af secrets set` stdin-based input. When the value is omitted from the command arguments, the CLI uses `readHiddenValue` to capture the secret via a secure pipe [control-plane/internal/cli/secrets.go:51-56]().

**Sources:**
- `control-plane/internal/cli/secrets.go`
- `CHANGELOG.md`

## Code Entity Map: Secret Lifecycle

The following diagram traces how a secret moves from the UI to the encrypted store and eventually into an Agent's execution environment.

**Secret Persistence and Injection Flow**
```mermaid
graph TD
    subgraph "Desktop UI (Renderer)"
        A["KeysEditorView"] -- "IPC: setSecret" --> B["Main Process"]
    end

    subgraph "CLI Layer (Go)"
        B -- "exec('af secrets set KEY')" --> C["NewSecretsCommand"]
        C --> D["openSecretStore()"]
        D --> E["packages.SecretStore.Set()"]
    end

    subgraph "Storage (Disk)"
        E -- "AES-256-GCM" --> F["~/.agentfield/secrets.json"]
    end

    subgraph "Agent Execution"
        G["af run <node>"] --> H["Load Registry"]
        H --> I["Decrypt Secrets"]
        I --> J["os.Environ() + Secrets"]
        J --> K["Agent Process (Python/TS/Go)"]
    end

    F -.-> I
```
**Sources:**
- `control-plane/internal/cli/secrets.go:17-37]()` (Command definition)
- `control-plane/internal/cli/secrets.go:61-72]()` (Storage logic)
- `CHANGELOG.md:16-34]()` (Desktop IPC architecture)

## The Keys Editor UI

The Desktop application features a dedicated "Keys" view. This view serves as a centralized management console for the `SecretStore`.

### Key Components
1. **Secret List**: Displays keys and their scopes (Global vs Node). Values are masked using `ui.Muted("••••••••")` [control-plane/internal/cli/secrets.go:107]().
2. **Scope Selector**: Allows users to target a specific agent node or the global scope [control-plane/internal/cli/secrets.go:81]().
3. **Status Feedback**: When a node-scoped secret is updated, the UI informs the user that the change applies only on the next restart of the agent [control-plane/internal/cli/secrets.go:75-77]().

### Technical Implementation: `SecretStore` Interaction
The UI relies on the `InstallationRegistry` to identify which nodes are available for scoping [control-plane/internal/cli/list.go:38-40]().

**Entity Relationship: UI to CLI Data**
```mermaid
classDiagram
    class InstallationRegistry {
        +map[string]InstalledPackage Installed
        +Load(path)
    }
    class SecretStore {
        +Set(scope, key, value)
        +ListAll()
        +Delete(scope, key)
    }
    class SecretsUI {
        +renderList()
        +onSaveSecret()
    }
    
    SecretsUI ..> InstallationRegistry : "Fetches node names for --node flag"
    SecretsUI ..> SecretStore : "Wraps af secrets CLI calls"
```
**Sources:**
- `control-plane/internal/cli/list.go:34-50]()`
- `control-plane/internal/cli/secrets.go:35-37]()`
- `control-plane/internal/cli/secrets.go:120-145]()`

---

# Page: Integrations

# Integrations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [control-plane/internal/handlers/execute_approval.go](control-plane/internal/handlers/execute_approval.go)
- [control-plane/internal/handlers/webhook_approval.go](control-plane/internal/handlers/webhook_approval.go)
- [control-plane/internal/handlers/webhook_approval_test.go](control-plane/internal/handlers/webhook_approval_test.go)
- [control-plane/internal/server/apicatalog/catalog.go](control-plane/internal/server/apicatalog/catalog.go)
- [control-plane/internal/server/apicatalog/catalog_entries.go](control-plane/internal/server/apicatalog/catalog_entries.go)
- [control-plane/internal/server/apicatalog/catalog_test.go](control-plane/internal/server/apicatalog/catalog_test.go)
- [control-plane/internal/server/knowledgebase/content.go](control-plane/internal/server/knowledgebase/content.go)
- [control-plane/internal/server/routes_middleware_additional_test.go](control-plane/internal/server/routes_middleware_additional_test.go)
- [control-plane/internal/sources/generichmac/hmac.go](control-plane/internal/sources/generichmac/hmac.go)
- [control-plane/internal/sources/generichmac/hmac_test.go](control-plane/internal/sources/generichmac/hmac_test.go)
- [control-plane/internal/sources/snowflake/snowflake.go](control-plane/internal/sources/snowflake/snowflake.go)
- [control-plane/internal/sources/snowflake/snowflake_test.go](control-plane/internal/sources/snowflake/snowflake_test.go)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)
- [docs/integrations/snowflake.md](docs/integrations/snowflake.md)
- [integrations/snowflake/README.md](integrations/snowflake/README.md)
- [integrations/snowflake/agentfield-package.yaml](integrations/snowflake/agentfield-package.yaml)
- [tests/functional/tests/test_waiting_state.py](tests/functional/tests/test_waiting_state.py)

</details>



Integrations in AgentField provide first-party connectivity between the Control Plane and external platforms. These integration packs extend the system through two primary mechanisms: **Trigger Sources**, which allow external events to initiate agent workflows, and **Capability Nodes**, which provide agents with specialized tools to interact with third-party data and services.

This page provides a high-level overview of the available first-party integrations. For implementation details and configuration schemas, refer to the specific child pages.

## Integration Architecture

Integrations are implemented as `Sources` within the Control Plane. They are categorized into two execution patterns:
1.  **Loop Sources (`KindLoop`)**: Poll external systems (e.g., Snowflake) at a configured interval to detect new events [control-plane/internal/sources/snowflake/snowflake.go:23-46]().
2.  **HTTP Sources (`KindHTTP`)**: Receive inbound webhooks from external platforms (e.g., Databricks, Linear) and normalize them into AgentField events [control-plane/internal/sources/generichmac/hmac.go:31-32]().

### Data Flow & Normalization
The following diagram illustrates how external signals are converted into AgentField `Event` entities and routed to agents.

**External to Internal Event Flow**
```mermaid
graph TD
    subgraph "External Platforms"
        SF["Snowflake Event Table"]
        DB["Databricks Webhook"]
        LN["Linear Webhook"]
    end

    subgraph "Control Plane (Code Entity Space)"
        S_SF["snowflake.source (KindLoop)"]
        S_HMAC["generichmac.source (KindHTTP)"]
        EV_REG["sources.Register()"]
    end

    subgraph "Natural Language Space"
        EV_OBJ["Normalized Event Object"]
        TRIG["Trigger Execution"]
    end

    SF -- "Polls" --> S_SF
    DB -- "POST /api/v1/sources/:id" --> S_HMAC
    LN -- "POST /api/v1/sources/:id" --> S_HMAC
    
    S_SF -- "Register()" --> EV_REG
    S_HMAC -- "Register()" --> EV_REG
    
    EV_REG -- "Normalize" --> EV_OBJ
    EV_OBJ -- "Matches Pattern" --> TRIG
```
Sources: [control-plane/internal/sources/snowflake/snowflake.go:22-46](), [control-plane/internal/sources/generichmac/hmac.go:27-33](), [control-plane/internal/handlers/webhook_approval.go:39-43]()

## Available Integrations

### Snowflake Integration
The Snowflake integration enables bidirectional communication with the Snowflake Data Cloud. It supports polling Snowflake Event Tables or executing custom SQL queries to trigger agent workflows [control-plane/internal/sources/snowflake/snowflake.go:49-72](). Agents can also utilize Snowflake capability nodes to perform SQL operations, Cortex Search, and Cortex Analyst queries.

For details, see [Snowflake Integration](#15.1).

### Databricks Integration
The Databricks integration connects AgentField to the Databricks Lakehouse. It utilizes notification destination webhooks as a trigger source and provides capability nodes for executing SQL, interacting with AI Functions, and Model Serving endpoints.

For details, see [Databricks Integration](#15.2).

### Linear & Sentry Integrations
These integrations focus on operational and engineering workflows:
*   **Linear**: Supports webhook triggers for issue updates and a capability node for Issue CRUD operations and comment management.
*   **Sentry**: Handles error event triggers, allowing agents to automatically triage or investigate software exceptions reported by Sentry.

For details, see [Linear & Sentry Integrations](#15.3).

## Common Integration Patterns

### Webhook Security
Most HTTP-based integrations utilize the `generic_hmac` source, which enforces HMAC-SHA256 signature verification. This ensures that inbound events are authentic and haven't been tampered with [control-plane/internal/sources/generichmac/hmac.go:102-119](). It also supports replay protection via timestamp tolerance windows [control-plane/internal/sources/generichmac/hmac.go:122-137]().

### Approval Webhooks
A specialized integration exists for human-in-the-loop workflows. The `ApprovalWebhookHandler` processes responses from external approval services (like the `hax-sdk`). It maps various external decision formats (e.g., "approve", "confirm", "reject") into canonical AgentField execution statuses like `approved` or `rejected` [control-plane/internal/handlers/webhook_approval.go:103-116]().

**Approval State Machine**
```mermaid
stateDiagram-v2
    direction LR
    [*] --> Running: Agent Starts
    Running --> Waiting: RequestApprovalHandler()
    Waiting --> Running: Webhook (approved)
    Waiting --> Cancelled: Webhook (rejected)
    Waiting --> Running: Webhook (request_changes)
```
Sources: [control-plane/internal/handlers/execute_approval.go:125-133](), [control-plane/internal/handlers/webhook_approval.go:185-193](), [control-plane/internal/handlers/webhook_approval_test.go:156-195]()

| Component | Role | Code Entity |
| :--- | :--- | :--- |
| **Trigger Source** | Ingests external events | `sources.Source` [control-plane/internal/sources/snowflake/snowflake.go:37]() |
| **HMAC Verifier** | Validates webhook signatures | `generichmac.source` [control-plane/internal/sources/generichmac/hmac.go:23]() |
| **Approval Controller** | Manages human-in-the-loop state | `approvalController` [control-plane/internal/handlers/execute_approval.go:19]() |
| **API Catalog** | Discovers available capabilities | `apicatalog.Catalog` [control-plane/internal/server/apicatalog/catalog.go:44]() |

Sources: [control-plane/internal/sources/snowflake/snowflake.go:37-46](), [control-plane/internal/sources/generichmac/hmac.go:23-33](), [control-plane/internal/handlers/execute_approval.go:19-21](), [control-plane/internal/server/apicatalog/catalog.go:44-49]()

---

# Page: Snowflake Integration

# Snowflake Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [control-plane/internal/sources/snowflake/snowflake.go](control-plane/internal/sources/snowflake/snowflake.go)
- [control-plane/internal/sources/snowflake/snowflake_test.go](control-plane/internal/sources/snowflake/snowflake_test.go)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)
- [docs/integrations/snowflake.md](docs/integrations/snowflake.md)
- [integrations/snowflake/README.md](integrations/snowflake/README.md)
- [integrations/snowflake/agentfield-package.yaml](integrations/snowflake/agentfield-package.yaml)

</details>



The Snowflake integration provides a dual-surface connection between AgentField and the Snowflake Data Cloud. It enables agents to both react to data changes within Snowflake and actively query or analyze Snowflake data using SQL and Cortex AI services.

The integration is architected into two distinct components:
1.  **Snowflake Trigger Source**: A built-in control plane service that polls Snowflake for events and dispatches them to agents [integrations/snowflake/README.md:6-7]().
2.  **Snowflake Capability Node**: An optional, standalone agent node that exposes SQL, metadata, and Cortex AI capabilities to the entire agent mesh [integrations/snowflake/README.md:8-10]().

## System Architecture

The following diagram illustrates the data flow between Snowflake, the AgentField Control Plane, and the Agent Mesh.

### Snowflake Integration Data Flow
```mermaid
graph TD
    subgraph "Snowflake Perimeter"
        "SF_TABLE[Event Table / Alerts]"
        "SF_CORTEX[Cortex AI / Search]"
        "SF_SQL[SQL Engine]"
    end

    subgraph "AgentField Control Plane"
        "SF_SOURCE[snowflake.go:source]"
        "SQL_API_CLIENT[snowflake.go:sqlAPIClient]"
    end

    subgraph "Agent Mesh"
        "SF_NODE[Snowflake Capability Node]"
        "USER_AGENT[User Agent]"
    end

    "SF_TABLE" -- "Poll (SQL API)" --> "SQL_API_CLIENT"
    "SQL_API_CLIENT" -- "Normalize" --> "SF_SOURCE"
    "SF_SOURCE" -- "Dispatch Event" --> "USER_AGENT"
    "USER_AGENT" -- "app.call()" --> "SF_NODE"
    "SF_NODE" -- "SQL / Cortex" --> "SF_SQL"
    "SF_NODE" -- "Inference" --> "SF_CORTEX"
```
Sources: [integrations/snowflake/README.md:18-26](), [control-plane/internal/sources/snowflake/snowflake.go:1-33]()

## Snowflake Trigger Source

The Snowflake trigger source is implemented as a `KindLoop` source within the control plane [control-plane/internal/sources/snowflake/snowflake.go:46](). It periodically polls Snowflake using the Snowflake SQL API to ingest events.

### Configuration Modes
The source supports two operational modes defined in `control-plane/internal/sources/snowflake/snowflake.go`:
*   **`event_table_poll`**: Monitors a specific table for new rows based on a watermark column (e.g., `OCCURRED_AT`) [control-plane/internal/sources/snowflake/snowflake.go:23, 32]().
*   **`custom_query_poll`**: Executes a user-defined read-only SQL statement (starting with `SELECT` or `WITH`) to fetch event data [control-plane/internal/sources/snowflake/snowflake.go:24, 186-191]().

### Configuration Schema
The source requires an `account_url` and a secret (typically a Programmatic Access Token/PAT) [control-plane/internal/sources/snowflake/snowflake.go:47, 69]().

| Property | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `mode` | string | `event_table_poll` | Polling strategy |
| `account_url` | string | - | e.g., `https://abc123.snowflakecomputing.com` |
| `database` | string | - | Target Snowflake database |
| `schema` | string | - | Target Snowflake schema |
| `table` | string | - | Target table (for `event_table_poll`) |
| `interval_seconds`| integer| 30 | Polling frequency (min 5s) |
| `max_batch_size` | integer| 100 | Max events per poll (max 500) |

Sources: [control-plane/internal/sources/snowflake/snowflake.go:50-72](), [control-plane/internal/sources/snowflake/snowflake.go:139-147]()

### Implementation Details
The polling logic is handled by the `source` struct which utilizes a `sqlAPIClient` [control-plane/internal/sources/snowflake/snowflake.go:37-39](). This client manages the HTTP communication with the Snowflake SQL API, including host rewriting and path validation [control-plane/internal/sources/snowflake/snowflake.go:201-215]().

## Snowflake Capability Node

The capability node is a Go-based agent node that registers with the control plane to provide specialized skills and reasoners to other agents [integrations/snowflake/agentfield-package.yaml:1-5]().

### Registered Capabilities
The node exposes the following capabilities under a specific `node_id` (default: `snowflake-prod`) [integrations/snowflake/agentfield-package.yaml:9, 16]():

| Category | Name | Description |
| :--- | :--- | :--- |
| **Reasoner** | `semantic_ask` | NL questions via Cortex Analyst [integrations/snowflake/agentfield-package.yaml:18-19]() |
| **Reasoner** | `explain_result` | Explains query results with citations [integrations/snowflake/agentfield-package.yaml:20-21]() |
| **Skill** | `query_readonly` | Executes read-only SQL with guardrails [integrations/snowflake/agentfield-package.yaml:25-26]() |
| **Skill** | `describe_table` | Returns table/column metadata [integrations/snowflake/agentfield-package.yaml:27-28]() |
| **Skill** | `cortex_search_query`| Queries Cortex Search services [integrations/snowflake/agentfield-package.yaml:33-34]() |

### Prompt Management
For `.ai` based reasoners like `investigate_metric_change`, the node avoids hardcoded prompts. Instead, it loads templates from a YAML file specified by the `SNOWFLAKE_PROMPTS_FILE` environment variable, falling back to packaged defaults [integrations/snowflake/agentfield-package.yaml:70-73](), [docs/integrations/snowflake.md:33-42]().

## Cross-Agent Execution

Agents interact with Snowflake by calling the capability node via the `app.call()` (Python) or `a.Call()` (Go) interface. This maintains a clean separation between the agent logic and the Snowflake connection parameters.

### Code-to-Entity Mapping
The following diagram maps SDK call patterns to the internal integration components.

```mermaid
sequenceDiagram
    participant SDK as "Agent SDK (Python/Go/TS)"
    participant CP as "Control Plane (/api/v1/execute)"
    participant Node as "snowflake-node (Go)"
    participant SF as "Snowflake SQL API"

    Note over SDK: app.call("snowflake-prod.query_readonly", ... )
    SDK->>CP: POST Execution Request
    CP->>Node: Forward to Capability [snowflake-prod]
    Note over Node: snowflake-node:node/snowflake-node
    Node->>SF: POST /api/v2/statements
    SF-->>Node: Rowset Data
    Node-->>CP: Normalized JSON Result
    CP-->>SDK: Final Execution Result
```
Sources: [integrations/snowflake/README.md:92-102](), [docs/ARCHITECTURE.md:47-52](), [integrations/snowflake/agentfield-package.yaml:5-9]()

### Environment Configuration
The Snowflake node requires specific environment variables for its identity and connection:
*   `AGENTFIELD_NODE_ID`: Identity in the mesh (e.g., `snowflake-prod`) [integrations/snowflake/agentfield-package.yaml:44]().
*   `SNOWFLAKE_ACCOUNT_URL`: Validated HTTPS Snowflake URL [integrations/snowflake/agentfield-package.yaml:50-53]().
*   `SNOWFLAKE_PAT`: Secret token for authentication [integrations/snowflake/agentfield-package.yaml:54-56]().
*   `SNOWFLAKE_ROLE`: The Snowflake role used for execution [integrations/snowflake/agentfield-package.yaml:57-59]().

Sources: [integrations/snowflake/agentfield-package.yaml:43-77]()

---

# Page: Databricks Integration

# Databricks Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [control-plane/internal/handlers/execute_approval.go](control-plane/internal/handlers/execute_approval.go)
- [control-plane/internal/handlers/webhook_approval.go](control-plane/internal/handlers/webhook_approval.go)
- [control-plane/internal/handlers/webhook_approval_test.go](control-plane/internal/handlers/webhook_approval_test.go)
- [control-plane/internal/server/apicatalog/catalog.go](control-plane/internal/server/apicatalog/catalog.go)
- [control-plane/internal/server/apicatalog/catalog_entries.go](control-plane/internal/server/apicatalog/catalog_entries.go)
- [control-plane/internal/server/apicatalog/catalog_test.go](control-plane/internal/server/apicatalog/catalog_test.go)
- [control-plane/internal/server/knowledgebase/content.go](control-plane/internal/server/knowledgebase/content.go)
- [control-plane/internal/server/routes_middleware_additional_test.go](control-plane/internal/server/routes_middleware_additional_test.go)
- [control-plane/internal/sources/generichmac/hmac.go](control-plane/internal/sources/generichmac/hmac.go)
- [control-plane/internal/sources/generichmac/hmac_test.go](control-plane/internal/sources/generichmac/hmac_test.go)
- [control-plane/internal/sources/snowflake/snowflake.go](control-plane/internal/sources/snowflake/snowflake.go)
- [control-plane/internal/sources/snowflake/snowflake_test.go](control-plane/internal/sources/snowflake/snowflake_test.go)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)
- [docs/integrations/snowflake.md](docs/integrations/snowflake.md)
- [integrations/snowflake/README.md](integrations/snowflake/README.md)
- [integrations/snowflake/agentfield-package.yaml](integrations/snowflake/agentfield-package.yaml)
- [tests/functional/tests/test_waiting_state.py](tests/functional/tests/test_waiting_state.py)

</details>



The Databricks integration enables AgentField agents to interact with Databricks Lakehouse data and AI assets. It provides a **Trigger Source** for receiving event-driven notifications via webhooks and a **Capability Node** for executing SQL queries, calling Databricks AI Functions, and interacting with Model Serving endpoints.

## Trigger Source: Webhook Notifications

AgentField supports receiving events from Databricks using the `generic_hmac` source pattern. This is primarily used to handle notifications from Databricks SQL Alerts, Job failures, or Model Serving events that support webhook destinations.

### Implementation and Security
The integration utilizes the `generichmac` package to verify inbound webhook signatures using HMAC-SHA256 [control-plane/internal/sources/generichmac/hmac.go:1-6](). This ensures that only authorized events from Databricks are processed by the control plane.

*   **Signature Verification**: The `HandleRequest` function validates the `X-Signature` (or a configured custom header) against a shared secret [control-plane/internal/sources/generichmac/hmac.go:85-119]().
*   **Replay Protection**: It supports an optional `TimestampHeader` to enforce a tolerance window (default 300s), preventing replay attacks [control-plane/internal/sources/generichmac/hmac.go:122-137]().

### Data Flow: Databricks to Agent
1.  **Event Generation**: Databricks triggers a webhook (e.g., a SQL Alert).
2.  **Ingestion**: The AgentField Control Plane receives the POST request at `/api/v1/sources/{source_id}`.
3.  **Validation**: `generichmac.source.HandleRequest` verifies the HMAC signature [control-plane/internal/sources/generichmac/hmac.go:116-119]().
4.  **Normalization**: The raw payload is converted into a standard `sources.Event` [control-plane/internal/sources/generichmac/hmac.go:148-153]().
5.  **Trigger**: The event is routed to the target agent based on the trigger configuration.

**Sources:**
- `control-plane/internal/sources/generichmac/hmac.go`
- `control-plane/internal/sources/generichmac/hmac_test.go`

---

## Capability Node: SQL and AI Functions

The Databricks capability node allows agents to perform cross-agent data access and utilize Databricks-native AI capabilities. This is modeled similarly to the Snowflake integration, providing high-level abstractions over the Databricks SQL API.

### Key Capabilities
*   **SQL Execution**: Run read-only or analytical queries against Unity Catalog tables.
*   **AI Functions**: Call `ai_analyze()`, `ai_summarize()`, or custom registered AI functions directly via SQL.
*   **Model Serving**: Interface with models deployed on Databricks Model Serving.

### System Architecture Diagram

This diagram shows the relationship between the AgentField Control Plane entities and the Databricks infrastructure.

Title: Databricks Capability Architecture
```mermaid
graph TD
    subgraph "AgentField Control Plane"
        A["AgentNode (Registered)"] -- "Registers" --> CP["Control Plane Server"]
        CP -- "Routes Execute" --> B["Capability Node: Databricks"]
    end

    subgraph "Databricks Workspace"
        B -- "SQL API (HTTPS)" --> SQL["SQL Warehouse"]
        SQL -- "Query" --> UC["Unity Catalog"]
        SQL -- "Invoke" --> AIF["AI Functions"]
        B -- "REST API" --> MS["Model Serving"]
    end

    subgraph "Code Entities"
        B_Code["sources.Register()"]
        SQL_Code["sqlAPIClient"]
        Val_Code["validateReadOnlySQL()"]
    end

    B --- B_Code
    SQL --- SQL_Code
    B --- Val_Code
```

**Sources:**
- `control-plane/internal/sources/snowflake/snowflake.go:41-43` (Pattern for registration)
- `control-plane/internal/sources/snowflake/snowflake.go:176-191` (SQL validation pattern)

---

## Approval Workflows with Databricks

For sensitive operations (e.g., modifying a production table or scaling a warehouse), the Databricks integration can leverage AgentField's **Waiting State** and **Approval Webhooks**.

### Approval Flow
When an agent requires human intervention before proceeding with a Databricks operation, it transitions the execution to a `waiting` status [control-plane/internal/handlers/execute_approval.go:50-55]().

1.  **Request**: The agent calls `handleRequestApproval` with a unique `approval_request_id` [control-plane/internal/handlers/execute_approval.go:63-75]().
2.  **Transition**: The Control Plane updates the `WorkflowExecution` status to `waiting_for_approval` [control-plane/internal/handlers/execute_approval.go:114-123]().
3.  **Webhook Callback**: An external system (or a Databricks-based dashboard) posts the decision to `ApprovalWebhookHandler` [control-plane/internal/handlers/webhook_approval.go:127-133]().
4.  **Resumption**: If approved, the execution transitions back to `running` [control-plane/internal/handlers/webhook_approval.go:186-193]().

### Approval Webhook Normalization
The `parseWebhookPayload` function handles multiple formats, including the `hax-sdk` envelope used by common AgentField UI components [control-plane/internal/handlers/webhook_approval.go:43-93]().

| Raw Decision | Normalized Decision | Resulting Status |
| :--- | :--- | :--- |
| `approve`, `confirm` | `approved` | `ExecutionStatusRunning` |
| `reject`, `abort` | `rejected` | `ExecutionStatusCancelled` |
| `request_changes` | `request_changes` | `ExecutionStatusRunning` (Reset) |

**Sources:**
- `control-plane/internal/handlers/execute_approval.go`
- `control-plane/internal/handlers/webhook_approval.go`
- `control-plane/internal/handlers/webhook_approval_test.go`

---

## Configuration and Validation

The Databricks integration requires specific configuration schemas to ensure secure connectivity.

### Configuration Schema (Conceptual)
The configuration typically includes the workspace URL, SQL Warehouse ID, and authentication tokens. Validation logic ensures that SQL queries are restricted to safe operations.

```go
// Example validation logic for SQL safety
func validateReadOnlySQL(sql string) error {
    sql = strings.TrimSpace(sql)
    if strings.Contains(sql, ";") {
        return errors.New("exactly one statement allowed")
    }
    first := strings.ToUpper(strings.Fields(sql)[0])
    if first != "SELECT" && first != "WITH" {
        return fmt.Errorf("read-only query required, got %s", first)
    }
    return nil
}
```

### Integration Sequence Diagram

Title: Cross-Agent Data Access Flow
```mermaid
sequenceDiagram
    participant A as Requesting Agent
    participant CP as Control Plane (apicatalog)
    participant D as Databricks Capability Node
    participant DBX as Databricks SQL API

    A->>CP: POST /api/v1/execute/databricks.query { "sql": "..." }
    CP->>CP: Resolve Capability (catalog_entries.go)
    CP->>D: Invoke handleRequest()
    D->>D: validateReadOnlySQL()
    D->>DBX: POST /api/v2/statements
    DBX-->>D: 200 OK (Result Set)
    D-->>CP: Normalized JSON Response
    CP-->>A: Execution Result
```

**Sources:**
- `control-plane/internal/server/apicatalog/catalog_entries.go:61-65`
- `control-plane/internal/sources/snowflake/snowflake.go:176-191` (Reference for SQL validation)
- `control-plane/internal/server/apicatalog/catalog.go:60-67` (Endpoint registration)

---

# Page: Linear & Sentry Integrations

# Linear & Sentry Integrations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [control-plane/internal/handlers/execute_approval.go](control-plane/internal/handlers/execute_approval.go)
- [control-plane/internal/handlers/webhook_approval.go](control-plane/internal/handlers/webhook_approval.go)
- [control-plane/internal/handlers/webhook_approval_test.go](control-plane/internal/handlers/webhook_approval_test.go)
- [control-plane/internal/server/apicatalog/catalog.go](control-plane/internal/server/apicatalog/catalog.go)
- [control-plane/internal/server/apicatalog/catalog_entries.go](control-plane/internal/server/apicatalog/catalog_entries.go)
- [control-plane/internal/server/apicatalog/catalog_test.go](control-plane/internal/server/apicatalog/catalog_test.go)
- [control-plane/internal/server/knowledgebase/content.go](control-plane/internal/server/knowledgebase/content.go)
- [control-plane/internal/server/routes_middleware_additional_test.go](control-plane/internal/server/routes_middleware_additional_test.go)
- [control-plane/internal/sources/generichmac/hmac.go](control-plane/internal/sources/generichmac/hmac.go)
- [control-plane/internal/sources/generichmac/hmac_test.go](control-plane/internal/sources/generichmac/hmac_test.go)
- [control-plane/internal/sources/snowflake/snowflake.go](control-plane/internal/sources/snowflake/snowflake.go)
- [control-plane/internal/sources/snowflake/snowflake_test.go](control-plane/internal/sources/snowflake/snowflake_test.go)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)
- [docs/integrations/snowflake.md](docs/integrations/snowflake.md)
- [integrations/snowflake/README.md](integrations/snowflake/README.md)
- [integrations/snowflake/agentfield-package.yaml](integrations/snowflake/agentfield-package.yaml)
- [tests/functional/tests/test_waiting_state.py](tests/functional/tests/test_waiting_state.py)

</details>



AgentField provides first-party support for **Linear** and **Sentry** through specialized trigger sources and capability nodes. These integrations allow agents to respond to external events (like a new issue or a production error) and perform actions (like commenting on a ticket or retrieving error context) within a unified execution framework.

## Architecture Overview

Integrations in AgentField follow a standardized pattern where a **Source** (Trigger) ingests external data into the Control Plane, and a **Capability Node** (Skill) allows agents to interact back with the external service.

### Data Flow: Trigger to Action

The following diagram illustrates how an external event from Linear or Sentry flows through the system to trigger an agent, and how that agent uses capability nodes to respond.

**Integration Data Flow Diagram**
```mermaid
graph TD
    subgraph "External Platforms"
        Linear["Linear App"]
        Sentry["Sentry.io"]
    end

    subgraph "AgentField Control Plane"
        LSource["Linear Webhook Source"]
        SSource["Sentry Webhook Source"]
        Dispatcher["Event Dispatcher"]
        Storage["StorageProvider"]
    end

    subgraph "Agent Node Space"
        Agent["Agent Instance"]
        LSkill["Linear Capability Node"]
        SSkill["Sentry Capability Node"]
    end

    Linear -- "HTTP POST (Webhook)" --> LSource
    Sentry -- "HTTP POST (Webhook)" --> SSource
    
    LSource -- "Normalize Event" --> Dispatcher
    SSource -- "Normalize Event" --> Dispatcher
    
    Dispatcher -- "Trigger Reasoner" --> Agent
    Agent -- "app.call('linear.create_comment')" --> LSkill
    Agent -- "app.call('sentry.get_event')" --> SSkill
    
    LSkill -- "GraphQL API" --> Linear
    SSkill -- "REST API" --> Sentry
```

Sources: [control-plane/internal/sources/generichmac/hmac.go:1-21](), [docs/ARCHITECTURE.md]()

---

## Linear Integration

The Linear integration consists of a webhook trigger for issue updates and a capability node for Issue CRUD (Create, Read, Update, Delete) and commenting.

### Linear Webhook Source
The Linear Source uses the `generic_hmac` implementation to verify incoming webhooks from Linear. Linear signs its payloads using an HMAC-SHA256 signature passed in the `X-Linear-Signature` header.

*   **Implementation**: The `generic_hmac` source validates the payload against a configured secret.
*   **Verification**: Uses `hmac.Equal` to prevent timing attacks [control-plane/internal/sources/generichmac/hmac.go:117-119]().
*   **Normalization**: Raw JSON from Linear is passed into the `Normalized` field of the `sources.Event` struct [control-plane/internal/sources/generichmac/hmac.go:148-153]().

### Capability Node (Skills)
Agents can interact with Linear via a registered Linear Skill node. This node abstracts the Linear GraphQL API into simple JSON-based skills:
*   `linear.get_issue`: Retrieves details of a specific issue.
*   `linear.create_comment`: Adds a comment to an issue thread.
*   `linear.update_issue`: Modifies status, priority, or assignees.

Sources: [control-plane/internal/sources/generichmac/hmac.go:31-48](), [control-plane/internal/server/apicatalog/catalog_entries.go:61-68]()

---

## Sentry Integration

The Sentry integration enables "Error-to-Resolution" workflows by triggering agents when new issues are created in Sentry.

### Sentry Webhook Source
Sentry webhooks are ingested via the Control Plane's webhook handler. Like Linear, Sentry uses HMAC signatures for security.

| Configuration Key | Description |
| :--- | :--- |
| `signature_header` | `X-Sentry-Hook-Signature` |
| `event_type_header` | `X-Sentry-Hook-Resource` (e.g., `issue`, `error`) |
| `secret` | The Sentry Webhook Secret provided in the Sentry Developer Settings |

### Error Handling Workflow
When a Sentry event hits the source:
1.  **Validation**: `HandleRequest` verifies the HMAC signature [control-plane/internal/sources/generichmac/hmac.go:85-120]().
2.  **Mapping**: The resource type (e.g., `issue.created`) is mapped to the AgentField event type [control-plane/internal/sources/generichmac/hmac.go:139-142]().
3.  **Execution**: An agent reasoner subscribed to `sentry.issue.created` is invoked.

Sources: [control-plane/internal/sources/generichmac/hmac.go:50-57](), [control-plane/internal/sources/generichmac/hmac.go:148-154]()

---

## Webhook Security & Signatures

Both integrations rely on the `generichmac` package for secure ingestion. This package ensures that only authentic requests from the respective platforms can trigger agent executions.

**Code Entity Map: Webhook Verification**
```mermaid
classDiagram
    class WebhookSource {
        <<interface>>
        +HandleRequest(ctx, req, cfg, secret)
    }
    class GenericHMACSource {
        +Name() "generic_hmac"
        +HandleRequest()
    }
    class HMACValidator {
        +hmac.New(sha256.New, secret)
        +mac.Write(payload)
        +hmac.Equal(provided, expected)
    }

    WebhookSource <|-- GenericHMACSource : implements
    GenericHMACSource ..> HMACValidator : uses to verify
```

### Replay Protection
The `generic_hmac` source supports optional timestamp-based replay protection. If a `timestamp_header` is configured (common in Sentry-style webhooks), the system enforces a `tolerance_seconds` window (defaulting to 300s) to prevent old captured payloads from being re-sent [control-plane/internal/sources/generichmac/hmac.go:122-137]().

Sources: [control-plane/internal/sources/generichmac/hmac.go:25-33](), [control-plane/internal/sources/generichmac/hmac.go:107-120](), [control-plane/internal/sources/generichmac/hmac_test.go:184-210]()

---

## Human-in-the-Loop (Approval)

For sensitive actions (e.g., closing a Linear ticket or resolving a Sentry issue), agents often use the **Approval Webhook** system.

1.  **Request**: An agent calls `RequestApprovalHandler` to transition an execution to the `waiting` state [control-plane/internal/handlers/execute_approval.go:50-55]().
2.  **External Link**: The agent provides an `approval_request_url` (often pointing to a UI for a human to review) [control-plane/internal/handlers/execute_approval.go:26-31]().
3.  **Callback**: Once a human approves, a webhook is sent to `/api/v1/webhooks/approval-response` [control-plane/internal/handlers/webhook_approval.go:127-133]().
4.  **Resume**: The `webhookApprovalController` verifies the signature, normalizes the decision (e.g., `approved`, `rejected`), and resumes the workflow [control-plane/internal/handlers/webhook_approval.go:185-194]().

Sources: [control-plane/internal/handlers/webhook_approval.go:119-133](), [control-plane/internal/handlers/execute_approval.go:141-163](), [control-plane/internal/handlers/webhook_approval_test.go:74-100]()

---

# Page: Testing & Development

# Testing & Development

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/control-plane.yml](.github/workflows/control-plane.yml)
- [.github/workflows/docker.yml](.github/workflows/docker.yml)
- [.github/workflows/functional-tests.yml](.github/workflows/functional-tests.yml)
- [.github/workflows/sdk-go.yml](.github/workflows/sdk-go.yml)
- [.github/workflows/sdk-python.yml](.github/workflows/sdk-python.yml)
- [Makefile](Makefile)
- [scripts/coverage-aggregate.py](scripts/coverage-aggregate.py)
- [scripts/coverage-summary.sh](scripts/coverage-summary.sh)
- [scripts/coverage-surface.sh](scripts/coverage-surface.sh)
- [sdk/python/tests/test_memory_events.py](sdk/python/tests/test_memory_events.py)
- [tests/functional/README.md](tests/functional/README.md)
- [tests/functional/conftest.py](tests/functional/conftest.py)
- [tests/functional/docker/Dockerfile.test-runner](tests/functional/docker/Dockerfile.test-runner)
- [tests/functional/docker/docker-compose.local.yml](tests/functional/docker/docker-compose.local.yml)
- [tests/functional/docker/docker-compose.postgres.yml](tests/functional/docker/docker-compose.postgres.yml)
- [tests/functional/docker/wait-for-services.sh](tests/functional/docker/wait-for-services.sh)
- [tests/functional/requirements.txt](tests/functional/requirements.txt)

</details>



This page documents the testing infrastructure, build system, release process, and contribution guidelines for AgentField. It covers how to run tests locally, understand the CI/CD pipeline, and contribute to the project.

For information about deploying AgentField to production environments, see [Deployment](#13).

---

## Overview

AgentField uses a multi-layer testing strategy including unit tests, integration tests, and functional tests. The build system is orchestrated through a `Makefile`, and releases follow a two-tier model separating staging (prerelease) from production releases. All of this is automated through GitHub Actions workflows.

**Testing Layers:**
- **Unit Tests**: Fast, isolated tests for individual components (Python, TypeScript, Go).
- **Functional Tests**: Docker-based integration tests against real control plane instances and real LLM providers.
- **CI/CD**: Automated testing and release workflows triggered by Git events.

**Release Model:**
- **Staging**: Automatic prerelease on every push to `main` (`X.Y.Z-rc.N`).
- **Production**: Manual stable release via workflow dispatch (`X.Y.Z`).

---

## Functional Test Architecture

AgentField's functional tests run inside Docker containers to ensure consistency across local development and CI environments. Tests verify the system works correctly with both SQLite (`local` mode) and PostgreSQL (`postgres` mode) storage backends.

### System-to-Code Mapping: Functional Infrastructure

```mermaid
graph TB
    subgraph "Natural Language Space"
        Tests["Functional Test Suite"]
        Runner["Test Runner Environment"]
        CP["Control Plane Instance"]
    end

    subgraph "Code Entity Space"
        PytestSuite["pytest tests<br/>tests/functional/"]
        DockerfileRunner["Dockerfile.test-runner<br/>tests/functional/docker/Dockerfile.test-runner"]
        ComposeLocal["docker-compose.local.yml<br/>tests/functional/docker/docker-compose.local.yml"]
        ComposePG["docker-compose.postgres.yml<br/>tests/functional/docker/docker-compose.postgres.yml"]
        WaitScript["wait-for-services.sh<br/>tests/functional/docker/wait-for-services.sh"]
    end

    Tests --- PytestSuite
    Runner --- DockerfileRunner
    CP --- ComposeLocal
    CP --- ComposePG
    WaitScript --- CP
```
**Sources:** [tests/functional/docker/docker-compose.local.yml:1-57](), [tests/functional/docker/docker-compose.postgres.yml:1-84](), [tests/functional/docker/Dockerfile.test-runner:1-110](), [tests/functional/docker/wait-for-services.sh:1-30]()

### Running Functional Tests Locally

Functional tests require an `OPENROUTER_API_KEY` for LLM-dependent tests, though 92% of tests (24/26) can run without it.

```bash
# Run all functional tests (both local and postgres modes)
export OPENROUTER_API_KEY="your-key-here"
make test-functional

# Run only SQLite mode tests
make test-functional-local

# Run only PostgreSQL mode tests  
make test-functional-postgres
```

**Sources:** [Makefile:61-109](), [tests/functional/README.md:39-55]()

### Test Environment Components

| Component | Purpose | Configuration |
|-----------|---------|---------------|
| `control-plane` | AgentField server under test | [tests/functional/docker/agentfield-test.yaml:1-108]() |
| `test-runner` | Pytest execution environment | [tests/functional/docker/Dockerfile.test-runner:1-110]() |
| `postgres` | PostgreSQL database with vector support | `pgvector/pgvector:pg16` |
| `wait-for-services.sh` | Health check script for orchestration | [tests/functional/docker/wait-for-services.sh:1-30]() |

**Sources:** [tests/functional/docker/docker-compose.postgres.yml:2-20](), [tests/functional/docker/docker-compose.local.yml:24-59]()

---

## Unit Tests

Each SDK and the control plane has its own unit test suite using language-appropriate testing frameworks.

| Component | Framework | Location | Command |
|-----------|-----------|----------|---------|
| **Python SDK** | `pytest` | `sdk/python/tests/` | `pytest` |
| **TypeScript SDK** | `vitest` | `sdk/typescript/tests/` | `npm test` |
| **Go SDK** | `go test` | `sdk/go/` | `go test ./...` |
| **Control Plane** | `go test` | `control-plane/` | `go test ./...` |

**Sources:** [.github/workflows/sdk-python.yml:51-53](), [.github/workflows/sdk-go.yml:48-50](), [.github/workflows/control-plane.yml:57-61]()

---

## Build System

The build system is orchestrated through a `Makefile` with targets for building, testing, and maintaining the codebase.

### Makefile Targets

| Target | Description | Key Operations |
|--------|-------------|----------------|
| `make build` | Build all components | Builds `control-plane`, `sdk-go`, `sdk-python` |
| `make test` | Run unit tests | Executes `./scripts/test-all.sh` |
| `make lint` | Run linters | `golangci-lint` (Go), `ruff` (Python) |
| `make fmt` | Format code | `gofmt` (Go), `ruff format` (Python) |
| `make clean` | Remove artifacts | Deletes `bin/`, `dist/`, `__pycache__` |

**Sources:** [Makefile:20-56]()

---

## Release Process

AgentField uses a **two-tier release system** that separates staging (prerelease) from production releases.

```mermaid
graph LR
    subgraph "Code Entity Space"
        BumpScript["bump_version.py<br/>scripts/bump_version.py"]
        ReleaseWorkflow["release.yml<br/>.github/workflows/release.yml"]
        GoReleaser[".goreleaser.yml"]
    end

    subgraph "Natural Language Space"
        Staging["Staging Release<br/>(vX.Y.Z-rc.N)"]
        Production["Production Release<br/>(vX.Y.Z)"]
    end

    BumpScript --> Staging
    BumpScript --> Production
    ReleaseWorkflow --> GoReleaser
    GoReleaser --> GitHubReleases["GitHub Releases"]
```

**Staging Releases**: Automatic on every push to `main`. Artifacts are published to PyPI (as `--pre`), npm (as `@next`), and GHCR (as `staging-*`).
**Production Releases**: Manually triggered via `workflow_dispatch`. Artifacts are published as stable versions.

**Sources:** [.github/workflows/release.yml:1-512](), [scripts/bump_version.py:1-254]()

---

## CI/CD Pipeline

The CI/CD pipeline is managed via GitHub Actions, ensuring that every pull request and merge to `main` is validated.

### Key Workflows

- **`functional-tests.yml`**: Runs the Docker-based integration suite across SQLite and PostgreSQL modes.
- **`control-plane.yml`**: Validates Go builds and UI compilation across Linux, Darwin, and Windows.
- **`sdk-python.yml`**: Runs unit tests across Python 3.10, 3.11, and 3.12, including websocket compatibility checks.
- **`sdk-go.yml`**: Ensures the Go SDK builds and passes basic tests.

**Sources:** [.github/workflows/functional-tests.yml:1-183](), [.github/workflows/control-plane.yml:1-158](), [.github/workflows/sdk-python.yml:1-102](), [.github/workflows/sdk-go.yml:1-66]()

---

## Contributing

Guidelines for contributing to the AgentField ecosystem.

### Development Workflow
1. **Setup**: Use `make install` to install development dependencies.
2. **Coding**: Follow language-specific style guides enforced by `make lint`.
3. **Testing**: Ensure new features include unit tests and, if applicable, functional tests.
4. **PRs**: Open pull requests against the `main` branch. Conventional commits are preferred.

**Sources:** [Makefile:22-24](), [tests/functional/README.md:162-180]()

---

## Child Pages

- [Functional Tests](#16.1) — Running functional tests with docker-compose: local and PostgreSQL modes, test infrastructure
- [Unit Tests](#16.2) — SDK unit tests with pytest (Python), vitest (TypeScript), and go test
- [Build System](#16.3) — Understanding the Makefile: build, test, lint, fmt, clean targets
- [Release Process](#16.4) — Two-tier release system: staging vs production, version bumping, changelog generation
- [CI/CD Pipeline](#16.5) — GitHub Actions workflows: release.yml, functional-tests.yml, build matrix, artifact publishing
- [Contributing](#16.6) — Guidelines for contributing: code style, testing requirements, pull request process

---

# Page: Functional Tests

# Functional Tests

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/functional-tests.yml](.github/workflows/functional-tests.yml)
- [Makefile](Makefile)
- [tests/functional/README.md](tests/functional/README.md)
- [tests/functional/agents/__init__.py](tests/functional/agents/__init__.py)
- [tests/functional/agents/docs_quick_start_agent.py](tests/functional/agents/docs_quick_start_agent.py)
- [tests/functional/agents/quick_start_agent.py](tests/functional/agents/quick_start_agent.py)
- [tests/functional/conftest.py](tests/functional/conftest.py)
- [tests/functional/docker/Dockerfile.test-runner](tests/functional/docker/Dockerfile.test-runner)
- [tests/functional/docker/docker-compose.local.yml](tests/functional/docker/docker-compose.local.yml)
- [tests/functional/docker/docker-compose.postgres.yml](tests/functional/docker/docker-compose.postgres.yml)
- [tests/functional/docker/wait-for-services.sh](tests/functional/docker/wait-for-services.sh)
- [tests/functional/requirements.txt](tests/functional/requirements.txt)
- [tests/functional/tests/__init__.py](tests/functional/tests/__init__.py)
- [tests/functional/tests/test_hello_world.py](tests/functional/tests/test_hello_world.py)
- [tests/functional/tests/test_quick_start.py](tests/functional/tests/test_quick_start.py)
- [tests/functional/utils/__init__.py](tests/functional/utils/__init__.py)
- [tests/functional/utils/agent_server.py](tests/functional/utils/agent_server.py)
- [tests/functional/utils/logging.py](tests/functional/utils/logging.py)
- [tests/functional/utils/naming.py](tests/functional/utils/naming.py)

</details>



## Purpose and Scope

This page documents AgentField's functional testing infrastructure, which validates the complete system through end-to-end integration tests. Functional tests use Docker Compose to orchestrate a full AgentField environment (control plane, test agents, and storage backends) and execute `pytest`-based test scenarios against it.

The suite ensures that:
*   The AgentField control plane (Go) starts correctly and manages state.
*   Python, Go, and TypeScript agents can register and communicate with the control plane [tests/functional/README.md:28-36]().
*   Reasoners execute successfully with and without real LLM integration [tests/functional/README.md:39-54]().
*   Execution metadata, such as workflow IDs and timing, is properly tracked [tests/functional/README.md:33-33]().
*   Both storage modes (SQLite and PostgreSQL) are verified for compatibility [tests/functional/README.md:35-35]().

## Test Architecture

Functional tests verify the entire AgentField stack by deploying real components in isolated Docker containers.

### System Component Mapping

The following diagram maps natural language test concepts to the specific code entities and containers defined in the test infrastructure.

**Natural Language to Code Entity Space**
```mermaid
graph TB
    subgraph "Test Execution (Code Space)"
        PyTest["pytest [tests/functional/requirements.txt:2-2]()"]
        Conftest["conftest.py [tests/functional/conftest.py:1-21]()"]
        RunAgent["run_agent_server() [tests/functional/utils/agent_server.py:36-43]()"]
        GoRunner["run_go_agent() [tests/functional/utils/go_agent_runner.py]()"]
    end

    subgraph "Infrastructure (Docker Space)"
        CP_Local["agentfield-control-plane-local [tests/functional/docker/docker-compose.local.yml:6-6]()"]
        CP_PG["agentfield-control-plane-postgres [tests/functional/docker/docker-compose.postgres.yml:26-26]()"]
        Runner["agentfield-test-runner-* [tests/functional/docker/Dockerfile.test-runner:1-50]()"]
        PGVector["agentfield-postgres-test [tests/functional/docker/docker-compose.postgres.yml:4-4]()"]
    end

    PyTest -->|"uses fixtures from"| Conftest
    Conftest -->|"spins up"| RunAgent
    RunAgent -->|"registers with"| CP_Local
    Runner -->|"executes"| PyTest
    CP_PG -->|"connects to"| PGVector
```
**Sources:** [tests/functional/docker/docker-compose.local.yml:1-60](), [tests/functional/docker/docker-compose.postgres.yml:1-86](), [tests/functional/conftest.py:1-21](), [tests/functional/utils/agent_server.py:36-43]()

## Docker Compose Infrastructure

Functional tests use two separate Docker Compose configurations to test different storage backends.

### Local Storage Mode
The local mode uses SQLite and BoltDB. The control plane is configured with `AGENTFIELD_STORAGE_MODE: local` [tests/functional/docker/docker-compose.local.yml:8-8]().

| Component | Container Name | Purpose |
|-----------|----------------|---------|
| `control-plane` | `agentfield-control-plane-local` | Control plane using local filesystem storage [tests/functional/docker/docker-compose.local.yml:6-6]() |
| `test-runner` | `agentfield-test-runner-local` | Executes the pytest suite [tests/functional/docker/docker-compose.local.yml:28-28]() |

**Sources:** [tests/functional/docker/docker-compose.local.yml:1-60]()

### PostgreSQL Storage Mode
The PostgreSQL mode tests production-like environments with `pgvector`. It sets `AGENTFIELD_STORAGE_MODE: postgres` [tests/functional/docker/docker-compose.postgres.yml:28-28]().

| Component | Container Name | Purpose |
|-----------|----------------|---------|
| `postgres` | `agentfield-postgres-test` | PostgreSQL 16 with `pgvector` [tests/functional/docker/docker-compose.postgres.yml:3-4]() |
| `control-plane` | `agentfield-control-plane-postgres` | Control plane linked to Postgres [tests/functional/docker/docker-compose.postgres.yml:26-26]() |

**Sources:** [tests/functional/docker/docker-compose.postgres.yml:1-86]()

## Test Runner Implementation

The `test-runner` container is built using a multi-stage `Dockerfile` that compiles the Go control plane, Go test agents, and the TypeScript SDK before installing the Python SDK [tests/functional/docker/Dockerfile.test-runner:1-110]().

**Build Stages to Code Entities**
```mermaid
graph LR
    subgraph "Stage 1: ui-builder"
        UI["web/client [tests/functional/docker/Dockerfile.test-runner:1-7]()"]
    end
    subgraph "Stage 2: ts-sdk-builder"
        TS["sdk/typescript [tests/functional/docker/Dockerfile.test-runner:9-17]()"]
    end
    subgraph "Stage 3: af-cli-builder"
        AF["cmd/af [tests/functional/docker/Dockerfile.test-runner:19-36]()"]
        GoAgents["tests/functional/go_agents [tests/functional/docker/Dockerfile.test-runner:40-48]()"]
    end
    subgraph "Final Stage: python-runner"
        PySDK["sdk/python [tests/functional/docker/Dockerfile.test-runner:79-81]()"]
        PytestBin["pytest [tests/functional/docker/Dockerfile.test-runner:109-109]()"]
    end

    UI --> AF
    TS --> PySDK
    AF --> PytestBin
    GoAgents --> PytestBin
```
**Sources:** [tests/functional/docker/Dockerfile.test-runner:1-110]()

### Service Readiness
The runner uses `wait-for-services.sh` to poll the control plane's `/api/v1/health` endpoint [tests/functional/docker/wait-for-services.sh:7-19](). It attempts up to 30 times (default) before failing the test run [tests/functional/docker/wait-for-services.sh:9-29]().

## Pytest Fixtures and Utilities

The `conftest.py` file defines the lifecycle and environment for the functional tests.

### Key Fixtures
*   **`verify_control_plane`**: An `autouse` session fixture that ensures the control plane is reachable before any tests start [tests/functional/conftest.py:135-156]().
*   **`async_http_client`**: Provides an `InstrumentedAsyncClient` that logs all HTTP traffic between the test and the control plane [tests/functional/conftest.py:186-206]().
*   **`openrouter_config`**: Supplies `AIConfig` objects to tests, ensuring consistent model selection via the `OPENROUTER_MODEL` environment variable [tests/functional/conftest.py:101-110]().

### Agent Runner Utility
The `run_agent_server` async context manager in `utils/agent_server.py` handles the lifecycle of an agent during a test [tests/functional/utils/agent_server.py:36-43]():
1.  Allocates a free port [tests/functional/utils/agent_server.py:47-49]().
2.  Starts the agent using `uvicorn` in a background thread [tests/functional/utils/agent_server.py:53-69]().
3.  Registers the agent with the control plane [tests/functional/utils/agent_server.py:74-74]().
4.  Yields a `RunningAgent` object for the test to interact with [tests/functional/utils/agent_server.py:88-88]().
5.  Shuts down the server upon exit [tests/functional/utils/agent_server.py:90-93]().

**Sources:** [tests/functional/conftest.py:1-206](), [tests/functional/utils/agent_server.py:1-94]()

## Running Functional Tests

Tests are orchestrated via the root `Makefile`.

### Local Execution
To run tests locally, the `OPENROUTER_API_KEY` must be set [Makefile:66-71]().

```bash
# Run SQLite mode tests
make test-functional-local

# Run PostgreSQL mode tests
make test-functional-postgres

# Run both modes
make test-functional
```

### CI Execution
The GitHub Actions workflow `functional-tests.yml` runs these tests on every push to `main` and for pull requests [ .github/workflows/functional-tests.yml:3-10](). It uses a matrix strategy to execute `local` and `postgres` modes in parallel [ .github/workflows/functional-tests.yml:37-42]().

For external pull requests (forks), tests requiring OpenRouter are automatically skipped using the `-m "not openrouter"` marker to protect secrets [ .github/workflows/functional-tests.yml:48-50]().

**Sources:** [Makefile:60-120](), [.github/workflows/functional-tests.yml:1-183]()

---

# Page: Unit Tests

# Unit Tests

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/control-plane.yml](.github/workflows/control-plane.yml)
- [.github/workflows/coverage-badge.yml](.github/workflows/coverage-badge.yml)
- [.github/workflows/coverage-report.yml](.github/workflows/coverage-report.yml)
- [.github/workflows/coverage.yml](.github/workflows/coverage.yml)
- [.github/workflows/docker.yml](.github/workflows/docker.yml)
- [.github/workflows/sdk-go.yml](.github/workflows/sdk-go.yml)
- [.github/workflows/sdk-python.yml](.github/workflows/sdk-python.yml)
- [control-plane/internal/cli/agent_helpers_test.go](control-plane/internal/cli/agent_helpers_test.go)
- [control-plane/internal/cli/command_helpers_additional_test.go](control-plane/internal/cli/command_helpers_additional_test.go)
- [control-plane/internal/packages/runner_test.go](control-plane/internal/packages/runner_test.go)
- [scripts/coverage-aggregate.py](scripts/coverage-aggregate.py)
- [scripts/coverage-summary.sh](scripts/coverage-summary.sh)
- [scripts/coverage-surface.sh](scripts/coverage-surface.sh)
- [sdk/python/tests/test_agent_bigfiles_final90.py](sdk/python/tests/test_agent_bigfiles_final90.py)
- [sdk/python/tests/test_memory_events.py](sdk/python/tests/test_memory_events.py)

</details>



This page documents the unit testing infrastructure for the AgentField SDKs and the Control Plane. Unit tests validate individual modules and classes in isolation using mocked dependencies and fixtures. They are fast, deterministic tests that do not require external services.

For end-to-end testing with live services, see [16.1 Functional Tests](). For the overall build system that orchestrates test execution, see [16.3 Build System]().

---

## Overview

AgentField maintains separate unit test suites for each surface area. The CI/CD pipeline uses a dedicated coverage workflow to aggregate results and enforce quality gates.

| Surface | Test Framework | Test Runner | Primary Command |
| :--- | :--- | :--- | :--- |
| **Control Plane** | Go `testing` | `go test` | `go test ./...` |
| **Python SDK** | `pytest` | `pytest` | `./scripts/run_pytest.sh` |
| **TypeScript SDK** | `vitest` | `vitest` | `npm test` |
| **Go SDK** | Go `testing` | `go test` | `go test ./...` |

### Coverage Pipeline
The system uses a multi-stage coverage pipeline defined in `.github/workflows/coverage.yml` [1-125](). It runs per-surface jobs in parallel, uploads artifacts, and then aggregates them to produce a final report [60-125]().

Sources: [.github/workflows/coverage.yml:60-74](), [.github/workflows/sdk-python.yml:51-54](), [.github/workflows/sdk-go.yml:44-47]()

---

## Python SDK Unit Tests

The Python SDK uses `pytest` with extensive configuration for async operations and network mocking.

### Environment & Compatibility
A critical part of the Python test suite is verifying compatibility with different `websockets` versions, as version 14 introduced breaking changes (renaming `extra_headers` to `additional_headers`) [.github/workflows/sdk-python.yml:55-60](). The SDK dynamically detects the version and uses the appropriate keyword argument [sdk/python/tests/test_memory_events.py:137-148]().

### Key Test Entities (Python)

```mermaid
graph TD
    subgraph "Natural Language Space"
        EventHandling["Memory Event Logic"]
        AgentLifecycle["Agent Registration & IP Detection"]
        Execution["Async Task Management"]
    end

    subgraph "Code Entity Space"
        PatternMatcher["PatternMatcher (agentfield.memory_events)"]
        MemoryEventClient["MemoryEventClient (agentfield.memory_events)"]
        AgentClass["Agent (agentfield.agent)"]
        PauseManager["_PauseManager (agentfield.agent)"]
        DetectIP["_detect_container_ip (agentfield.agent)"]
    end

    EventHandling --> PatternMatcher
    EventHandling --> MemoryEventClient
    AgentLifecycle --> AgentClass
    AgentLifecycle --> DetectIP
    Execution --> PauseManager
```

**Implementation Details**:
- **IP Detection**: Tests mock the `requests` module and `socket` to simulate container environments (AWS metadata, ipify) and local network configurations [sdk/python/tests/test_agent_bigfiles_final90.py:64-107]().
- **Memory Events**: `MemoryEventClient` tests use `monkeypatch` to simulate WebSocket connections and verify that subscriptions correctly filter events based on scope and keys [sdk/python/tests/test_memory_events.py:40-57]().
- **Pause Management**: `_PauseManager` is tested for its ability to register, resolve, and cancel pending agent executions (e.g., waiting for human approval) [sdk/python/tests/test_agent_bigfiles_final90.py:134-152]().

Sources: [sdk/python/tests/test_memory_events.py:17-39](), [sdk/python/tests/test_agent_bigfiles_final90.py:12-22](), [.github/workflows/sdk-python.yml:77-82]()

---

## Control Plane & CLI Unit Tests

The Control Plane and CLI are tested using Go's standard library `testing` package and the `testify` library for assertions.

### CLI Helper Testing
The `af` CLI helpers are tested for robust handling of HTTP communication, JSON formatting (pretty vs. compact), and path escaping [control-plane/internal/cli/agent_helpers_test.go:22-45]().

### Registry & Runner Testing
The `AgentNodeRunner` tests validate the lifecycle of managed agent processes:
- **Port Management**: Ensuring the runner can find free ports and detect collisions [control-plane/internal/packages/runner_test.go:31-51]().
- **Process Spawning**: Verifying that environment variables (like `PYTHONUTF8=1`) are correctly injected into child processes [control-plane/internal/packages/runner_test.go:82-97]().
- **Health Checks**: Testing the `waitForAgentNode` logic which polls the agent's `/health` endpoint until it is ready [control-plane/internal/packages/runner_test.go:129-134]().

### Code-to-System Mapping (CLI/CP)

```mermaid
graph LR
    subgraph "System Logic"
        APIClient["Control Plane API Client"]
        ProcMgmt["Process Management"]
        Registry["Installation Registry"]
    end

    subgraph "Code Entities"
        agentHTTP["agentHTTP() (cli/agent_helpers.go)"]
        AgentNodeRunner["AgentNodeRunner (packages/runner.go)"]
        UpdateRuntime["updateRuntimeInfo() (packages/runner.go)"]
        LoadRegistry["loadRegistry() (packages/runner.go)"]
    end

    APIClient --- agentHTTP
    ProcMgmt --- AgentNodeRunner
    Registry --- UpdateRuntime
    Registry --- LoadRegistry
```

Sources: [control-plane/internal/cli/agent_helpers_test.go:47-70](), [control-plane/internal/packages/runner_test.go:31-33](), [control-plane/internal/cli/command_helpers_additional_test.go:18-30]()

---

## TypeScript SDK Unit Tests

The TypeScript SDK utilizes `vitest` for modern, fast unit testing with native ESM support.

### Test Execution
Tests are run via `npm test` [sdk/typescript/package.json:15](). The suite focuses on:
- **AIClient**: Validating provider-specific logic (OpenAI, Anthropic, etc.).
- **MemoryInterface**: Testing scoped key-value operations and vector search mocking.
- **Agent Lifecycle**: Ensuring handlers for different platforms (AWS Lambda, Express) correctly normalize events.

Sources: [sdk/typescript/package.json:12-16](), [.github/workflows/coverage.yml:73]()

---

## CI/CD and Coverage Reporting

AgentField implements a strict coverage gate to prevent regressions.

### Coverage Workflow
1. **Path Detection**: The `changes` job determines if relevant code was modified [.github/workflows/coverage.yml:22-47]().
2. **Parallel Execution**: Each surface (sdk-python, control-plane, etc.) runs its tests and generates LCOV or Cobertura reports [.github/workflows/coverage.yml:60-104]().
3. **Aggregation**: The `coverage-summary` job downloads all artifacts and runs `scripts/coverage-aggregate.py` [.github/workflows/coverage.yml:165-180]().
4. **Sticky Comments**: A separate `Coverage Report` workflow posts the results directly to the Pull Request using `sticky-pull-request-comment` [.github/workflows/coverage-report.yml:34-49]().

### Badge Automation
After merging to `main`, the `Coverage Badge` workflow extracts the final coverage percentage and updates a GitHub Gist to refresh the badge in the project README [.github/workflows/coverage-badge.yml:120-144]().

Sources: [.github/workflows/coverage.yml:125-132](), [.github/workflows/coverage-report.yml:1-12](), [.github/workflows/coverage-badge.yml:1-12]()

---

# Page: Build System

# Build System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/functional-tests.yml](.github/workflows/functional-tests.yml)
- [Makefile](Makefile)
- [tests/functional/README.md](tests/functional/README.md)
- [tests/functional/conftest.py](tests/functional/conftest.py)
- [tests/functional/docker/Dockerfile.test-runner](tests/functional/docker/Dockerfile.test-runner)
- [tests/functional/docker/docker-compose.local.yml](tests/functional/docker/docker-compose.local.yml)
- [tests/functional/docker/docker-compose.postgres.yml](tests/functional/docker/docker-compose.postgres.yml)
- [tests/functional/docker/wait-for-services.sh](tests/functional/docker/wait-for-services.sh)
- [tests/functional/requirements.txt](tests/functional/requirements.txt)

</details>



## Purpose and Scope

This document describes the build system infrastructure for the AgentField codebase, including the Makefile-based build targets, multi-language SDK compilation, functional test orchestration with Docker Compose, and CI/CD integration. The build system provides a unified interface for building all components (control plane, Go SDK, Python SDK), running tests across multiple storage backends, and ensuring code quality through linting and formatting tools.

For information about the release process and version management, see [Release Process](#16.4). For details about specific test implementations, see [Functional Tests](#16.1) and [Unit Tests](#16.2). For CI/CD workflows and GitHub Actions, see [CI/CD Pipeline](#16.5).

---

## Build Target Overview

The root-level `Makefile` provides the primary interface for building, testing, and maintaining the codebase. All build operations are orchestrated through Make targets that coordinate builds across the control plane and multiple SDK implementations.

### Core Build Targets

| Target | Purpose | Components |
|--------|---------|------------|
| `install` | Install development dependencies | Executes `scripts/install-dev-deps.sh` |
| `build` | Build all components | `control-plane`, `sdk-go`, `sdk-python` |
| `control-plane` | Build Go control plane | `cd control-plane && go build ./...` |
| `sdk-go` | Build Go SDK | `cd sdk/go && go build ./...` |
| `sdk-python` | Install Python SDK in editable mode | `cd sdk/python && pip install -e .` |
| `test` | Run all tests | Executes `scripts/test-all.sh` |
| `lint` | Run linters on all components | `golangci-lint`, `ruff check` |
| `fmt` | Format source code | `gofmt`, `ruff format` |
| `tidy` | Clean up Go module dependencies | `go mod tidy` |
| `clean` | Remove build artifacts | Removes `bin/`, `dist/`, `__pycache__/` |

**Sources:** [Makefile:22-56]()

---

## Makefile Target Dependency Graph

```mermaid
graph TB
    all["all"]
    install["install"]
    build["build"]
    control_plane["control-plane"]
    sdk_go["sdk-go"]
    sdk_python["sdk-python"]
    test["test"]
    lint["lint"]
    fmt["fmt"]
    tidy["tidy"]
    clean["clean"]
    
    install_script["scripts/install-dev-deps.sh"]
    test_script["scripts/test-all.sh"]
    
    all --> build
    
    build --> control_plane
    build --> sdk_go
    build --> sdk_python
    
    install --> install_script
    test --> test_script
    
    control_plane --> go_build_cp["go build ./...<br/>(control-plane/)"]
    sdk_go --> go_build_sdk["go build ./...<br/>(sdk/go/)"]
    sdk_python --> pip_install["pip install -e .<br/>(sdk/python/)"]
    
    lint --> golangci_cp["golangci-lint run<br/>(control-plane/)"]
    lint --> golangci_sdk["golangci-lint run<br/>(sdk/go/)"]
    lint --> ruff_check["ruff check<br/>(sdk/python/)"]
    
    fmt --> gofmt_cp["gofmt -w<br/>(control-plane/)"]
    fmt --> gofmt_sdk["gofmt -w<br/>(sdk/go/)"]
    fmt --> ruff_fmt["ruff format<br/>(sdk/python/)"]
    
    tidy --> go_mod_tidy_cp["go mod tidy<br/>(control-plane/)"]
    tidy --> go_mod_tidy_sdk["go mod tidy<br/>(sdk/go/)"]
    
    clean --> rm_artifacts["rm -rf bin/ dist/ __pycache__/"]
```

**Sources:** [Makefile:20-56]()

---

## Multi-Component Build Process

### Control Plane Build

The control plane is built as a Go binary. The build process compiles all packages in the `control-plane/` directory.

```
make control-plane
  └─> cd control-plane && go build ./...
```

**Sources:** [Makefile:27-28]()

### Go SDK Build

The Go SDK provides agent implementation templates and client libraries. The build verifies compilation.

```
make sdk-go
  └─> cd sdk/go && go build ./...
```

**Sources:** [Makefile:30-31]()

### Python SDK Build

The Python SDK is installed in editable (development) mode, allowing local changes to be immediately reflected.

```
make sdk-python
  └─> cd sdk/python && pip install -e . >/dev/null
```

**Sources:** [Makefile:33-34]()

---

## Functional Test Infrastructure

The functional test system uses Docker Compose to orchestrate multi-container test environments that validate end-to-end agent behavior against both SQLite and PostgreSQL storage backends.

### Test Environment Architecture

```mermaid
graph TB
    subgraph "Local Mode"
        cp_local["control-plane<br/>container<br/>agentfield-control-plane-local"]
        test_runner_local["test-runner<br/>container<br/>agentfield-test-runner-local"]
        volume_local["control-plane-data<br/>volume"]
        
        test_runner_local -->|"HTTP 8080"| cp_local
        cp_local --> volume_local
    end
    
    subgraph "Postgres Mode"
        postgres["postgres<br/>container<br/>agentfield-postgres-test<br/>pgvector/pgvector:pg16"]
        cp_postgres["control-plane<br/>container<br/>agentfield-control-plane-postgres"]
        test_runner_postgres["test-runner<br/>container<br/>agentfield-test-runner-postgres"]
        volume_pg["postgres-data<br/>volume"]
        volume_cp_pg["control-plane-data<br/>volume"]
        
        test_runner_postgres -->|"HTTP 8080"| cp_postgres
        cp_postgres -->|"postgres://agentfield:***<br/>@postgres:5432/agentfield_test"| postgres
        postgres --> volume_pg
        cp_postgres --> volume_cp_pg
    end
    
    makefile["Makefile"]
    compose_local["docker-compose.local.yml"]
    compose_postgres["docker-compose.postgres.yml"]
    dockerfile_cp["Dockerfile.control-plane"]
    dockerfile_test["Dockerfile.test-runner"]
    
    makefile -->|"test-functional-local"| compose_local
    makefile -->|"test-functional-postgres"| compose_postgres
    
    compose_local --> cp_local
    compose_local --> test_runner_local
    compose_postgres --> postgres
    compose_postgres --> cp_postgres
    compose_postgres --> test_runner_postgres
    
    dockerfile_cp -.->|"builds"| cp_local
    dockerfile_cp -.->|"builds"| cp_postgres
    dockerfile_test -.->|"builds"| test_runner_local
    dockerfile_test -.->|"builds"| test_runner_postgres
```

**Sources:** [tests/functional/docker/docker-compose.local.yml:1-67](), [tests/functional/docker/docker-compose.postgres.yml:1-94]()

### Functional Test Make Targets

| Target | Storage Mode | Compose File | Container Names |
|--------|--------------|--------------|-----------------|
| `test-functional` | Both (sequential) | Both files | All containers |
| `test-functional-local` | SQLite | `docker-compose.local.yml` | `agentfield-control-plane-local`, `agentfield-test-runner-local` |
| `test-functional-postgres` | PostgreSQL | `docker-compose.postgres.yml` | `agentfield-postgres-test`, `agentfield-control-plane-postgres`, `agentfield-test-runner-postgres` |
| `test-functional-cleanup` | N/A | Both files | Cleanup for both modes |
| `test-functional-ci` | Both (CI mode) | Both files | CI-optimized execution |

**Sources:** [Makefile:61-120]()

### Test Runner Configuration

The `test-runner` container executes pytest with the following environment:

```bash
# Environment variables from docker-compose files
AGENTFIELD_SERVER=http://control-plane:8080
OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
OPENROUTER_MODEL=${OPENROUTER_MODEL:-openrouter/google/gemini-2.5-flash-lite}
STORAGE_MODE=local|postgres
PYTEST_ARGS=${PYTEST_ARGS:--v}
TEST_TIMEOUT=${TEST_TIMEOUT:-300}
TEST_AGENT_BIND_HOST=${TEST_AGENT_BIND_HOST:-0.0.0.0}
TEST_AGENT_CALLBACK_HOST=${TEST_AGENT_CALLBACK_HOST:-test-runner}
FUNCTIONAL_LOG_FILE=/tests/functional/logs/functional-tests.log
AGENTFIELD_HOME=/tmp/agentfield-cli
```

The test runner waits for the control plane to be healthy before executing tests using the `wait-for-services.sh` script:

```bash
sh -c "
echo 'Waiting for control plane to be fully ready...' &&
wait-for-services.sh &&
pytest -n auto $$PYTEST_ARGS --junit-xml=/reports/junit-local.xml --tb=short;
"
```

**Sources:** [tests/functional/docker/docker-compose.local.yml:24-60](), [tests/functional/docker/docker-compose.postgres.yml:50-85]()

---

## Functional Test Execution Flow

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant Make as "Makefile"
    participant Docker as "Docker Compose"
    participant CP as "control-plane<br/>container"
    participant TestRunner as "test-runner<br/>container"
    participant Pytest as "pytest"
    
    Dev->>Make: "make test-functional-local"
    Make->>Make: "Check OPENROUTER_API_KEY"
    Make->>Make: "mkdir -p test-reports logs"
    Make->>Docker: "docker compose -f docker-compose.local.yml up"
    
    Docker->>CP: "Start control-plane"
    CP->>CP: "Initialize storage at /data/agentfield"
    CP->>CP: "Start HTTP server on port 8080"
    
    Docker->>TestRunner: "Start test-runner"
    TestRunner->>TestRunner: "Execute wait-for-services.sh"
    
    loop "Health Check (max 30 attempts)"
        TestRunner->>CP: "curl /api/v1/health"
        CP-->>TestRunner: "200 OK or failure"
    end
    
    TestRunner->>Pytest: "pytest -v --junit-xml=/reports/junit-local.xml"
    
    loop "For each test"
        Pytest->>TestRunner: "Register and execute agents"
        TestRunner->>CP: "POST /api/v1/nodes/register"
        CP-->>TestRunner: "Registration response"
    end
    
    Pytest->>TestRunner: "Generate JUnit XML"
    TestRunner->>Docker: "Exit status code"
    
    Docker->>Make: "Container exit code"
    Make->>Make: "Copy logs to test-reports/"
    Make->>Make: "docker compose down -v"
    Make-->>Dev: "Test results"
```

**Sources:** [Makefile:64-81](), [tests/functional/docker/wait-for-services.sh:1-30](), [tests/functional/conftest.py:134-156]()

---

## CI/CD Integration

### GitHub Actions Functional Test Workflow

The `.github/workflows/functional-tests.yml` workflow automates functional testing. It uses a matrix strategy to test both storage modes in parallel.

#### Workflow Triggers

```yaml
on:
  push:
    branches: [testing, main]
  pull_request:
    branches: [main]
  workflow_dispatch:
    inputs:
      storage_mode:
        default: 'both'
        type: choice
        options: [both, local, postgres]
```

**Sources:** [.github/workflows/functional-tests.yml:3-26]()

#### Matrix Strategy

The workflow runs two parallel jobs:

```yaml
strategy:
  fail-fast: false
  matrix:
    storage_mode: [local, postgres]
```

**Sources:** [.github/workflows/functional-tests.yml:37-43]()

---

## Environment Variable Requirements

### Functional Test Environment

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `OPENROUTER_API_KEY` | Yes | None | OpenRouter API authentication |
| `OPENROUTER_MODEL` | No | `openrouter/google/gemini-2.5-flash-lite` | AI model for tests |
| `AGENTFIELD_SERVER` | No | `http://control-plane:8080` | Control plane URL |
| `STORAGE_MODE` | No | `local` | Storage backend being tested |
| `TEST_TIMEOUT` | No | `300` | Test timeout in seconds |
| `FUNCTIONAL_LOG_FILE` | No | `/tests/functional/logs/functional-tests.log` | Log file path |

**Sources:** [tests/functional/docker/docker-compose.local.yml:29-41](), [tests/functional/conftest.py:23-42]()

### Control Plane Container Configuration

The control plane container uses environment variables to configure storage and behavior:

```yaml
environment:
  AGENTFIELD_STORAGE_MODE: local|postgres
  AGENTFIELD_PORT: 8080
  AGENTFIELD_CONFIG_FILE: /etc/agentfield/agentfield-test.yaml
  AGENTFIELD_HOME: /data/agentfield
```

**Sources:** [tests/functional/docker/docker-compose.local.yml:7-14](), [tests/functional/docker/docker-compose.postgres.yml:27-37]()

---

## Summary

The AgentField build system provides:

1. **Unified Build Interface:** Single `Makefile` orchestrates builds across Go and Python components.
2. **Multi-Storage Testing:** Docker Compose environments test both SQLite and PostgreSQL backends.
3. **CI/CD Integration:** GitHub Actions workflows with matrix strategy and artifact collection.
4. **Developer Tools:** Linting, formatting, and testing targets for rapid development.
5. **Isolated Test Environments:** Containerized functional tests with health checking and automatic cleanup via `wait-for-services.sh`.

**Sources:** [Makefile:1-120](), [.github/workflows/functional-tests.yml:1-183](), [tests/functional/docker/docker-compose.local.yml:1-67](), [tests/functional/docker/docker-compose.postgres.yml:1-94]()

---

# Page: Release Process

# Release Process

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/release.yml](.github/workflows/release.yml)
- [.goreleaser.yml](.goreleaser.yml)
- [control-plane/internal/templates/docker/docker-compose.yml.tmpl](control-plane/internal/templates/docker/docker-compose.yml.tmpl)
- [deployments/helm/agentfield/values.yaml](deployments/helm/agentfield/values.yaml)
- [deployments/kubernetes/base/control-plane-deployment.yaml](deployments/kubernetes/base/control-plane-deployment.yaml)
- [docs/RELEASE.md](docs/RELEASE.md)
- [examples/python_agent_nodes/rag_evaluation/docker-compose.yml](examples/python_agent_nodes/rag_evaluation/docker-compose.yml)
- [examples/triggers-demo/docker-compose.yml](examples/triggers-demo/docker-compose.yml)
- [scripts/bump_version.py](scripts/bump_version.py)
- [scripts/install.ps1](scripts/install.ps1)
- [scripts/install.sh](scripts/install.sh)
- [scripts/tests/__init__.py](scripts/tests/__init__.py)
- [scripts/tests/test_bump_version.py](scripts/tests/test_bump_version.py)
- [sdk/go/ai/openrouter_attribution.go](sdk/go/ai/openrouter_attribution.go)

</details>



## Purpose

This document describes the technical implementation of AgentField's two-tier release system. It covers the automated build pipeline, version management utilities, artifact distribution mechanisms, and the GitHub Actions workflows that orchestrate the release process.

---

## Release System Architecture

AgentField implements a **two-tier release model** that separates staging (pre-release) from production releases. This system uses a single `VERSION` file as the source of truth and orchestrates releases through GitHub Actions.

**Two-Tier Release System Architecture**

```mermaid
graph TB
    subgraph "Version Management"
        VERSION["VERSION file<br/>(Single Source of Truth)"]
        BumpScript["bump_version.py<br/>SemVer parser/bumper"]
        UpdateChangelog["update_changelog.py<br/>Markdown generator"]
    end
    
    subgraph "Trigger Mechanisms"
        Push["git push main<br/>Automatic Trigger"]
        Manual["workflow_dispatch<br/>Manual Trigger"]
    end
    
    subgraph "Release Workflow Jobs"
        PrepareJob["prepare job<br/>Determines version<br/>and publish flags"]
        BuildJob["build-binaries job<br/>Matrix: linux/darwin<br/>amd64/arm64"]
        PublishJob["publish job<br/>Creates releases<br/>and publishes artifacts"]
    end
    
    subgraph "Build Tools"
        GoReleaser["GoReleaser v2<br/>.goreleaser.yml"]
        NPMBuild["npm build<br/>web/client"]
        PyBuild["python -m build<br/>sdk/python"]
        TsBuild["npm run build<br/>sdk/typescript"]
    end
    
    subgraph "Distribution Targets"
        GHRelease["GitHub Releases<br/>Binaries + Checksums"]
        PyPI["PyPI<br/>--pre flag for staging"]
        NPM["npm registry<br/>@next or @latest tag"]
        Docker["GHCR/DockerHub<br/>staging-* or v* + latest"]
    end
    
    Push -->|"paths: control-plane/**<br/>sdk/**, VERSION"| PrepareJob
    Manual -->|"inputs: release_environment<br/>release_component"| PrepareJob
    
    VERSION --> PrepareJob
    PrepareJob --> BumpScript
    BumpScript --> UpdateChangelog
    
    PrepareJob --> BuildJob
    BuildJob --> GoReleaser
    BuildJob --> NPMBuild
    
    PrepareJob --> PublishJob
    PublishJob --> PyBuild
    PublishJob --> TsBuild
    
    PublishJob --> GHRelease
    PublishJob --> PyPI
    PublishJob --> NPM
    PublishJob --> Docker
    
    GoReleaser --> GHRelease
```

**Sources:** [.github/workflows/release.yml:1-51]() | [.goreleaser.yml:1-180]() | [docs/RELEASE.md:7-13]()

---

## Version Management

### VERSION File and SemVer Class

The `VERSION` file at the repository root is the single source of truth for the current version. All components synchronize to this value through `scripts/bump_version.py`.

```mermaid
graph LR
    subgraph "Version Sources Updated"
        VF["VERSION"]
        PyProject["sdk/python/pyproject.toml"]
        PyInit["sdk/python/agentfield/__init__.py"]
        TsPkg["sdk/typescript/package.json"]
        GoMod["control-plane/internal/templates/go/go.mod.tmpl"]
        Reqs["examples/*/requirements.txt"]
    end
    
    subgraph "bump_version.py"
        Parser["SemVer.parse()"]
        Bumper["SemVer.bump()"]
        Prerelease["SemVer.with_prerelease()"]
        Determiner["determine_next_version()"]
    end
    
    VF --> Parser
    Parser --> Determiner
    Determiner --> Bumper
    Determiner --> Prerelease
    
    Bumper --> VF
    Prerelease --> VF
    VF --> PyProject
    VF --> PyInit
    VF --> TsPkg
    VF --> GoMod
    VF --> Reqs
```

**Sources:** [scripts/bump_version.py:16-27]() | [scripts/bump_version.py:37-86]()

### Version Bumping Logic

The `determine_next_version()` function implements the core logic for the two-tier system:

| Input State | Channel | Component | Output |
|------------|---------|-----------|--------|
| `0.1.18` | `stable` | `patch` | `0.1.19` |
| `0.1.18` | `prerelease` | `patch` | `0.1.19-rc.1` |
| `0.1.19-rc.1` | `prerelease` | `patch` | `0.1.19-rc.2` |
| `0.1.19-rc.2` | `stable` | `patch` | `0.1.19` (Finalizes from prerelease) |

The `SemVer` dataclass provides methods to parse, bump, and handle prerelease labels (e.g., `rc`, `beta`). It uses a strict regex pattern to ensure compliance with Semantic Versioning.

**Sources:** [scripts/bump_version.py:30-33]() | [scripts/bump_version.py:89-118]() | [scripts/tests/test_bump_version.py:24-59]()

---

## Build Pipeline Components

### GoReleaser Configuration

The `.goreleaser.yml` defines build targets for the `af` CLI and the `af-tray` macOS companion.

| Build ID | OS | Arch | Features |
|----------|----|------|----------|
| `agentfield-linux-amd64` | Linux | amd64 | CGO, SQLite FTS5, Embedded UI |
| `agentfield-linux-arm64` | Linux | arm64 | Cross-compiled via `aarch64-linux-gnu-gcc` |
| `agentfield-darwin-arm64` | Darwin | arm64 | Native macOS Apple Silicon |
| `agentfield-tray-darwin-arm64` | Darwin | arm64 | Separate binary for macOS menu-bar |

Each build injects version metadata using `ldflags`:
- `main.version`: `{{ .Version }}`
- `main.commit`: `{{ .ShortCommit }}`
- `main.date`: `{{ .Date }}`

**Sources:** [.goreleaser.yml:11-30]() | [.goreleaser.yml:108-123]() | [.goreleaser.yml:130-148]()

### Build Matrix and UI Integration

The release workflow runs a build matrix across `ubuntu-latest` and `macos-14`. A critical step is building the web client before compiling the Go binary, as the Go binary uses build tags to embed the frontend assets.

```mermaid
sequenceDiagram
    participant GHA as GitHub Actions
    participant NPM as Web Client (npm)
    participant Go as Go Compiler
    
    GHA->>NPM: npm run build (control-plane/web/client)
    NPM-->>GHA: static files generated
    GHA->>Go: goreleaser build --clean
    Note over Go: Uses -tags embedded,sqlite_fts5
    Go-->>GHA: Binary with embedded UI
```

**Sources:** [.github/workflows/release.yml:191-280]() | [.goreleaser.yml:6-9]()

---

## Release Workflow Execution

### Prepare Job

The `prepare` job determines the release version and sets publish flags based on the trigger type (automatic `push` to main vs. manual `workflow_dispatch`).

**Logic Flow:**
1. **Determine Environment:** `staging` for push events; user-selected for manual events.
2. **Version Bump:** Calls `scripts/bump_version.py` with the appropriate `--channel` (stable or prerelease).
3. **Changelog:** Calls `scripts/update_changelog.py` to generate the release notes.
4. **Git Operations:** Commits version changes, tags the commit, and pushes to origin.

**Sources:** [.github/workflows/release.yml:64-190]() | [docs/RELEASE.md:63-87]()

### Publish Job

The `publish` job distributes artifacts to various registries:

- **PyPI:** Publishes the Python SDK. Prereleases are automatically handled by PEP 440 logic.
- **npm:** Publishes the TypeScript SDK. Staging versions use the `@next` tag, while production uses `@latest`.
- **Docker:** Pushes the `control-plane` image to GHCR and Docker Hub.
- **GitHub Release:** Uploads binaries and generates a `checksums.txt` file for integrity verification.

**Sources:** [.github/workflows/release.yml:281-512]() | [docs/RELEASE.md:168-188]()

---

## Installation and Consumption

The release process feeds the installation scripts, which allow users to select between the stable and staging channels.

| Channel | Install Command | Binary Name | Install Path |
|---------|-----------------|-------------|--------------|
| **Production** | `curl ... | bash` | `af` | `~/.agentfield/bin` |
| **Staging** | `curl ... | bash -s -- --staging` | `af-staging` | `~/.agentfield-staging/bin` |

The `install.sh` script performs the following:
1. Detects OS and Architecture.
2. Queries the GitHub API for the latest version in the selected channel.
3. Downloads the platform-specific binary and `checksums.txt`.
4. Verifies the SHA256 hash before installation.

**Sources:** [scripts/install.sh:137-145]() | [scripts/install.sh:220-259]() | [scripts/install.ps1:136-186]() | [docs/RELEASE.md:191-213]()

---

# Page: CI/CD Pipeline

# CI/CD Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/control-plane.yml](.github/workflows/control-plane.yml)
- [.github/workflows/docker.yml](.github/workflows/docker.yml)
- [.github/workflows/release.yml](.github/workflows/release.yml)
- [.github/workflows/sdk-go.yml](.github/workflows/sdk-go.yml)
- [.github/workflows/sdk-python.yml](.github/workflows/sdk-python.yml)
- [.goreleaser.yml](.goreleaser.yml)
- [control-plane/internal/templates/docker/docker-compose.yml.tmpl](control-plane/internal/templates/docker/docker-compose.yml.tmpl)
- [deployments/helm/agentfield/values.yaml](deployments/helm/agentfield/values.yaml)
- [deployments/kubernetes/base/control-plane-deployment.yaml](deployments/kubernetes/base/control-plane-deployment.yaml)
- [docs/RELEASE.md](docs/RELEASE.md)
- [examples/python_agent_nodes/rag_evaluation/docker-compose.yml](examples/python_agent_nodes/rag_evaluation/docker-compose.yml)
- [examples/triggers-demo/docker-compose.yml](examples/triggers-demo/docker-compose.yml)
- [scripts/bump_version.py](scripts/bump_version.py)
- [scripts/coverage-aggregate.py](scripts/coverage-aggregate.py)
- [scripts/coverage-summary.sh](scripts/coverage-summary.sh)
- [scripts/coverage-surface.sh](scripts/coverage-surface.sh)
- [scripts/install.ps1](scripts/install.ps1)
- [scripts/install.sh](scripts/install.sh)
- [scripts/tests/__init__.py](scripts/tests/__init__.py)
- [scripts/tests/test_bump_version.py](scripts/tests/test_bump_version.py)
- [sdk/go/ai/openrouter_attribution.go](sdk/go/ai/openrouter_attribution.go)
- [sdk/python/tests/test_memory_events.py](sdk/python/tests/test_memory_events.py)

</details>



## Purpose and Scope

This document describes the continuous integration and continuous deployment (CI/CD) infrastructure for AgentField, including GitHub Actions workflows, build matrices, artifact publishing, and testing infrastructure. For information about the release process and two-tier release system, see [Release Process](#16.4).

The CI/CD pipeline handles:
- Automated staging releases on every push to `main` [docs/RELEASE.md:11-11]()
- Manual production releases via workflow dispatch [.github/workflows/release.yml:14-23]()
- Multi-platform binary builds (Linux/macOS/Windows, amd64/arm64) [.goreleaser.yml:11-149]()
- SDK distribution to PyPI and npm [.github/workflows/release.yml:40-47]()
- Docker image publishing to GitHub Container Registry [.github/workflows/release.yml:48-51]()
- Per-SDK linting and unit testing [.github/workflows/sdk-python.yml:19-53]() [.github/workflows/sdk-go.yml:19-46]()

---

## Workflow Architecture

AgentField uses a set of specialized GitHub Actions workflows to manage the lifecycle of the Control Plane and various SDKs.

### Core Workflows

| Workflow | File | Purpose |
|----------|------|---------|
| **Release** | `.github/workflows/release.yml` | Versioning, multi-platform builds, and publishing. |
| **Control Plane CI** | `.github/workflows/control-plane.yml` | Builds the Go server, builds the React UI, and runs cross-platform compile checks. |
| **Python SDK CI** | `.github/workflows/sdk-python.yml` | Lints with `ruff`, runs `pytest` across Python 3.10-3.12, and verifies `websockets` version compatibility. |
| **Go SDK CI** | `.github/workflows/sdk-go.yml` | Verifies Go SDK builds and tidies modules. |
| **Docker Build** | `.github/workflows/docker.yml` | Smoke tests the Control Plane Docker image. |

### System Data Flow

The following diagram bridges the high-level workflow triggers to the specific scripts and tools used in the pipeline.

```mermaid
graph TB
    subgraph "Triggers"
        PushMain["git push main<br/>(paths: control-plane/**, sdk/**, VERSION)"]
        Manual["workflow_dispatch<br/>(Manual Trigger)"]
    end
    
    subgraph "release.yml (GitHub Actions)"
        PrepareJob["Job: prepare"]
        BuildBinaries["Job: build-binaries (matrix)"]
        PublishJob["Job: publish"]
        
        PrepareJob --> BuildBinaries
        BuildBinaries --> PublishJob
    end

    subgraph "Code Entity Space"
        BumpScript["scripts/bump_version.py"]
        GoReleaser[".goreleaser.yml"]
        PyBuild["python -m build"]
        DockerFile["deployments/docker/Dockerfile.control-plane"]
    end
    
    PrepareJob -->|"calls"| BumpScript
    BuildBinaries -->|"executes"| GoReleaser
    PublishJob -->|"executes"| PyBuild
    PublishJob -->|"builds"| DockerFile
    
    PushMain --> PrepareJob
    Manual --> PrepareJob
```

Sources: [.github/workflows/release.yml:1-52](), [.github/workflows/control-plane.yml:1-13](), [.github/workflows/sdk-python.yml:1-14]()

---

## Release Workflow Deep Dive

### Job: Prepare (Versioning Logic)

The `prepare` job determines the version to release using `scripts/bump_version.py`. It distinguishes between "staging" (prerelease) and "production" (stable) channels.

- **Automatic Staging**: Triggered by push to `main`. It forces a `patch` bump with an `rc` label [.github/workflows/release.yml:142-148]().
- **Collision Check**: The `_remote_tag_names()` function in `bump_version.py` queries `origin` to ensure the next `-rc.N` counter doesn't conflict with existing tags [scripts/bump_version.py:121-158]().
- **Artifact Sync**: The script updates `VERSION`, `pyproject.toml`, `package.json`, and `go.mod.tmpl` simultaneously to ensure all SDKs match the Control Plane version [scripts/bump_version.py:191-228]().

### Job: Build Binaries (Matrix)

AgentField uses a build matrix to handle CGO dependencies required for SQLite (FTS5 support).

```mermaid
graph TD
    subgraph "Build Matrix (release.yml)"
        Linux["ubuntu-latest"]
        MacOS["macos-14"]
    end

    subgraph "GoReleaser Targets (.goreleaser.yml)"
        AL64["agentfield-linux-amd64"]
        ALARM["agentfield-linux-arm64"]
        AD64["agentfield-darwin-amd64"]
        ADARM["agentfield-darwin-arm64"]
        Tray["agentfield-tray-darwin-*"]
    end

    Linux --> AL64
    Linux --> ALARM
    MacOS --> AD64
    MacOS --> ADARM
    MacOS --> Tray
```

- **Linux ARM64**: Built on `ubuntu-latest` using the `aarch64-linux-gnu-gcc` cross-compiler [.goreleaser.yml:37-37]().
- **macOS Tray**: A separate binary (`af-tray`) is built specifically for Darwin to handle the menu-bar companion, keeping the main `af` binary lean [.goreleaser.yml:92-123]().
- **UI Embedding**: Before Go compilation, the React client is built via `npm run build` and embedded into the binary using Go `embed` (triggered by the `embedded` build tag) [.goreleaser.yml:8-29]().

Sources: [.github/workflows/release.yml:191-280](), [.goreleaser.yml:1-166](), [scripts/bump_version.py:89-118]()

---

## SDK-Specific CI

### Python SDK Verification

The Python CI (`sdk-python.yml`) includes a specialized check for `websockets` compatibility.

- **Websockets Versioning**: The SDK detects the installed `websockets` version. In version 14.0, the library renamed `extra_headers` to `additional_headers` [sdk/python/tests/test_memory_events.py:137-148]().
- **Matrix Testing**: The CI runs a matrix against `websockets==12.0` and `websockets==15.0.1` to ensure the `MemoryEventClient` correctly selects the `_HEADERS_KWARG` [.github/workflows/sdk-python.yml:56-83]().

### Control Plane Cross-Compilation

The `control-plane.yml` workflow validates that the server can compile for `linux`, `darwin`, and `windows` even when CGO is disabled for simple status checks [.github/workflows/control-plane.yml:70-81](). However, official releases always use `CGO_ENABLED=1` to support `sqlite_fts5` [.goreleaser.yml:17-148]().

Sources: [.github/workflows/sdk-python.yml:56-83](), [sdk/python/tests/test_memory_events.py:137-148](), [.github/workflows/control-plane.yml:70-120]()

---

## Artifact Publishing

Once builds are successful, the `publish` job distributes the artifacts:

1. **GitHub Release**: Uploads all platform binaries and `checksums.txt` [.github/workflows/release.yml:335-345]().
2. **PyPI**: Publishes the Python SDK. Staging releases are uploaded as prereleases (e.g., `0.1.19rc1`), which `pip` ignores unless `--pre` is specified [.github/workflows/release.yml:350-367]().
3. **npm**: Publishes the TypeScript SDK. Staging uses the `@next` tag; production uses `@latest` [.github/workflows/release.yml:369-395]().
4. **Docker**: Builds a multi-platform image (`linux/amd64`, `linux/arm64`) using `Dockerfile.control-plane` and pushes to GHCR [.github/workflows/release.yml:410-445]().

Sources: [.github/workflows/release.yml:335-445](), [docs/RELEASE.md:11-12]()

---

## Installation Scripts

The CI/CD pipeline supports two primary installation scripts that consume the published artifacts.

### Shell Installer (`install.sh`)
- **Channel Support**: Supports a `--staging` flag to install the latest release candidate [scripts/install.sh:63-66]().
- **Auto-Provisioning**: On macOS, it can automatically install the `af-tray` and configure `launchd` for auto-start [scripts/install.sh:36-43]().
- **Binary Resolution**: It identifies the system architecture (e.g., `x86_64` vs `arm64`) to fetch the correct binary from GitHub [scripts/install.sh:238-270]().

### PowerShell Installer (`install.ps1`)
- **Windows Support**: Provides equivalent functionality for Windows users, installing `agentfield.exe` and creating an `af.exe` alias [scripts/install.ps1:203-218]().
- **Checksum Verification**: Calculates the SHA256 hash of the downloaded `.exe` and compares it against `checksums.txt` from the release [scripts/install.ps1:136-186]().

Sources: [scripts/install.sh:1-126](), [scripts/install.ps1:1-220]()

---

# Page: Contributing

# Contributing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.cliff.toml](.cliff.toml)
- [.github/BRANCH_PROTECTION.md](.github/BRANCH_PROTECTION.md)
- [.github/ISSUE_TEMPLATE/task.md](.github/ISSUE_TEMPLATE/task.md)
- [.github/workflows/ai-label.yml](.github/workflows/ai-label.yml)
- [AGENTS.md](AGENTS.md)
- [CLAUDE.md](CLAUDE.md)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [SECURITY.md](SECURITY.md)
- [SUPPORT.md](SUPPORT.md)
- [control-plane/internal/packages/config_version_test.go](control-plane/internal/packages/config_version_test.go)
- [control-plane/internal/skillkit/skill_data/agentfield/references/cli-toolkit.md](control-plane/internal/skillkit/skill_data/agentfield/references/cli-toolkit.md)
- [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)
- [scripts/update_changelog.py](scripts/update_changelog.py)
- [skills/agentfield/references/cli-toolkit.md](skills/agentfield/references/cli-toolkit.md)

</details>



This page provides guidelines for contributing code, documentation, or bug reports to AgentField. It covers environment setup, coding standards, testing requirements, and the pull request process.

---

## Prerequisites

Development requires the following tools:

| Tool | Version | Purpose |
|------|---------|---------|
| Go | 1.23+ | Control plane and Go SDK [CLAUDE.md:17-17]() |
| Python | 3.8+ | Python SDK and tooling [CLAUDE.md:18-18]() |
| Node.js | 20+ | TypeScript SDK and web UI [CLAUDE.md:19-19]() |
| PostgreSQL | 15+ | Required for cloud mode storage [CLAUDE.md:20-20]() |

---

## Development Environment Setup

### Initial Setup

The repository uses a `Makefile` to orchestrate multi-language dependencies and builds.

```bash
# Clone the repository
git clone https://github.com/Agent-Field/agentfield.git
cd agentfield

# Install all dependencies (Go, Python, Node)
make install

# Build all components
make build
```

The `make install` target executes `scripts/install.sh` to set up the environment [CLAUDE.md:25-28]().

### Build Targets

```mermaid
graph TB
    all["make all"]
    build["make build"]
    test["make test"]
    lint["make lint"]
    fmt["make fmt"]
    
    all -->|default target| build
    
    build --> controlplane["control-plane<br/>(Go build)"]
    build --> sdkgo["sdk-go<br/>(Go build)"]
    build --> sdkpython["sdk-python<br/>(pip install -e)"]
    
    test --> testscript["scripts/test-all.sh<br/>(unit tests)"]
    
    lint --> golint["golangci-lint<br/>(Go code)"]
    lint --> rufflint["ruff check<br/>(Python code)"]
    
    fmt --> gofmt["gofmt<br/>(Go formatting)"]
    fmt --> rufffmt["ruff format<br/>(Python formatting)"]
```

**Sources:** [CLAUDE.md:68-73](), [docs/CONTRIBUTING.md:16-19]()

---

## Code Style Guidelines

### Go (Control Plane & SDK)

**Formatting:**
- Use `gofmt` for automatic formatting.
- Run `make fmt` before committing [CLAUDE.md:94-94]().

**Linting:**
- Use `golangci-lint` for static analysis.
- Run `golangci-lint run` within the `control-plane` directory [CLAUDE.md:98-98]().

**Sources:** [CLAUDE.md:91-98](), [.github/BRANCH_PROTECTION.md:9-13]()

### Python (SDK)

**Formatting & Linting:**
- The project uses `ruff` for both linting and formatting.
- Run `ruff check` and `ruff format .` in `sdk/python` [CLAUDE.md:99-100]().

**Conventions:**
- Follow PEP 8 naming.
- Use type annotations for all function signatures [CLAUDE.md:169-174]().

**Sources:** [CLAUDE.md:99-101](), [.github/BRANCH_PROTECTION.md:20-23]()

---

## Testing Requirements

### Test Hierarchy

```mermaid
graph TB
    subgraph "Test Levels"
        unit["Unit Tests<br/>Fast, isolated"]
        functional["Functional Tests<br/>Full stack integration"]
    end
    
    subgraph "Unit Test Execution"
        pytest["pytest<br/>(Python SDK)"]
        gotest["go test<br/>(Go SDK + Control Plane)"]
        npmtest["npm test<br/>(Web UI)"]
    end
    
    subgraph "Functional Test Execution"
        scripts["scripts/test-all.sh"]
    end
    
    unit --> pytest
    unit --> gotest
    unit --> npmtest
    
    functional --> scripts
```

### Unit Tests

All code changes must include unit tests.

- **Go:** `go test ./...` in the relevant package directory [CLAUDE.md:80-81]().
- **Python:** `pytest` in `sdk/python`. Use `--cov=agentfield` for coverage reports [CLAUDE.md:82-85]().
- **Web UI:** `npm run lint` and `npm test` (Vitest) [CLAUDE.md:88-88]().

### AI-Assisted Testing

If using AI (Claude, Copilot, etc.) to generate code, you are responsible for the quality. AI-generated code must meet the same coverage standards as human code [docs/CONTRIBUTING.md:119-121]().

**Test Quality Checklist:**
- [ ] Tests actually fail when code is broken [docs/CONTRIBUTING.md:159-159]().
- [ ] Edge cases (null, empty, boundary) are covered [docs/CONTRIBUTING.md:161-161]().
- [ ] Assertions verify behavior, not just "no error" [docs/CONTRIBUTING.md:160-160]().

**Sources:** [CLAUDE.md:76-89](), [docs/CONTRIBUTING.md:119-165]()

---

## Pull Request Process

### Workflow Overview

```mermaid
graph LR
    fork["1. Fork & Branch"]
    changes["2. Make Changes"]
    testlocal["3. Test Locally"]
    submit["4. Submit PR"]
    cla["5. Sign CLA"]
    review["6. Code Review"]
    merge["7. Merge"]
    
    fork --> changes
    changes --> testlocal
    testlocal --> submit
    submit --> cla
    cla --> review
    review -->|"changes requested"| changes
    review -->|"approved"| merge
```

### 1. Fork and Branch
Fork the repository and create a feature branch with a descriptive name (e.g., `feat/my-feature` or `fix/issue-id`) [docs/CONTRIBUTING.md:15-23]().

### 2. Commit Guidelines
- Use **Conventional Commits** (`feat:`, `fix:`, `chore:`, `docs:`) [docs/CONTRIBUTING.md:27-27]().
- Reference related issues using `Fixes #<id>` [docs/CONTRIBUTING.md:29-29]().
- If using AI assistance, optionally include `Co-Authored-By: Claude <noreply@anthropic.com>` in the commit footer [docs/CONTRIBUTING.md:107-111]().

### 3. CLA Requirements
AgentField uses `cla-assistant.io`. Human contributors must sign the CLA via the link in the PR [docs/CONTRIBUTING.md:49-53](). Bot accounts (e.g., Dependabot) must be allowlisted by maintainers [docs/CONTRIBUTING.md:54-60]().

### 4. AI Detection
Pull requests are automatically scanned for AI assistance signatures (e.g., "Generated by Claude", "Co-authored-by: Copilot"). Detected PRs are labeled `ai-assisted` for transparency [.github/workflows/ai-label.yml:52-135]().

**Sources:** [docs/CONTRIBUTING.md:1-60](), [.github/workflows/ai-label.yml:1-135]()

---

## CI/CD and Branch Protection

All PRs must pass a suite of automated checks before they can be merged to `main`.

### Required Checks
- **Control Plane:** Go build, Go tests, `golangci-lint`, and cross-compilation (Linux/macOS/Windows) [.github/BRANCH_PROTECTION.md:9-13]().
- **SDKs:** Build verification, unit tests, and `ruff` linting for Python [.github/BRANCH_PROTECTION.md:15-23]().
- **Docker:** Successful build of `Dockerfile.control-plane` and a smoke test (`--help`) [.github/BRANCH_PROTECTION.md:24-26]().

### Troubleshooting Failures
If CI fails, reproduce the issue locally using the following:
- **Go:** `go test ./...` and `golangci-lint run` [.github/BRANCH_PROTECTION.md:39-40]().
- **Python:** `ruff check .` and `pytest` [.github/BRANCH_PROTECTION.md:43-45]().
- **Docker:** `docker build -f deployments/docker/Dockerfile.control-plane ...` [.github/BRANCH_PROTECTION.md:76-77]().

**Sources:** [.github/BRANCH_PROTECTION.md:1-80]()

---

## Introspection Toolkit for Contributors

The `af` CLI provides tools to help contributors debug and inspect the system during development.

| Command | Purpose |
|---------|---------|
| `af doctor --json` | Returns environment truth (AI providers, toolchain availability) [skills/agentfield/references/cli-toolkit.md:11-24]() |
| `af agent status` | One-shot health snapshot of the system [skills/agentfield/references/cli-toolkit.md:27-29]() |
| `af agent query` | Unified JSON resource query for `runs`, `executions`, `agents`, etc. [skills/agentfield/references/cli-toolkit.md:37-41]() |
| `af execution cancel` | Stop a stuck test execution [skills/agentfield/references/cli-toolkit.md:135-135]() |
| `af secrets ls/set` | Manage the local encrypted secret store for agent nodes [skills/agentfield/references/cli-toolkit.md:109-111]() |

**Sources:** [skills/agentfield/references/cli-toolkit.md:1-140]()

---

## Security Contributions
Do **not** open public issues for security vulnerabilities. Report them directly to `contact@agentfield.ai`. Maintainers aim to respond within 48 hours [SECURITY.md:3-9]().

**Sources:** [SECURITY.md:1-28]()

---

# Page: Glossary

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/update-download-stats.yml](.github/workflows/update-download-stats.yml)
- [CHANGELOG.md](CHANGELOG.md)
- [README.md](README.md)
- [VERSION](VERSION)
- [assets/UI.png](assets/UI.png)
- [assets/arch.png](assets/arch.png)
- [assets/examples/ai-security-auditor.png](assets/examples/ai-security-auditor.png)
- [assets/examples/autonomous-engineering-team.png](assets/examples/autonomous-engineering-team.png)
- [assets/examples/deep-research-engine.png](assets/examples/deep-research-engine.png)
- [assets/examples/reactive-database-layer.png](assets/examples/reactive-database-layer.png)
- [assets/features-strip.png](assets/features-strip.png)
- [assets/github hero.png](assets/github hero.png)
- [control-plane/cmd/af/main.go](control-plane/cmd/af/main.go)
- [control-plane/cmd/agentfield-server/main.go](control-plane/cmd/agentfield-server/main.go)
- [control-plane/config/agentfield.yaml](control-plane/config/agentfield.yaml)
- [control-plane/internal/config/config.go](control-plane/internal/config/config.go)
- [control-plane/internal/config/config_additional_test.go](control-plane/internal/config/config_additional_test.go)
- [control-plane/internal/handlers/execute_awaiter_status.go](control-plane/internal/handlers/execute_awaiter_status.go)
- [control-plane/internal/handlers/execute_awaiter_status_test.go](control-plane/internal/handlers/execute_awaiter_status_test.go)
- [control-plane/internal/server/middleware/auth.go](control-plane/internal/server/middleware/auth.go)
- [control-plane/internal/server/middleware/auth_admin_additional_test.go](control-plane/internal/server/middleware/auth_admin_additional_test.go)
- [control-plane/internal/server/middleware/auth_test.go](control-plane/internal/server/middleware/auth_test.go)
- [control-plane/internal/server/routes_admin.go](control-plane/internal/server/routes_admin.go)
- [control-plane/internal/server/routes_middleware.go](control-plane/internal/server/routes_middleware.go)
- [control-plane/internal/server/server.go](control-plane/internal/server/server.go)
- [control-plane/internal/server/server_additional_test.go](control-plane/internal/server/server_additional_test.go)
- [control-plane/internal/server/server_coverage_additional_test.go](control-plane/internal/server/server_coverage_additional_test.go)
- [control-plane/internal/templates/go/go.mod.tmpl](control-plane/internal/templates/go/go.mod.tmpl)
- [deployments/helm/agentfield/templates/control-plane-deployment.yaml](deployments/helm/agentfield/templates/control-plane-deployment.yaml)
- [docs/ENVIRONMENT_VARIABLES.md](docs/ENVIRONMENT_VARIABLES.md)
- [examples/python_agent_nodes/agentic_rag/requirements.txt](examples/python_agent_nodes/agentic_rag/requirements.txt)
- [examples/python_agent_nodes/documentation_chatbot/requirements.txt](examples/python_agent_nodes/documentation_chatbot/requirements.txt)
- [examples/python_agent_nodes/hello_world_rag/requirements.txt](examples/python_agent_nodes/hello_world_rag/requirements.txt)
- [sdk/python/CHANGELOG.md](sdk/python/CHANGELOG.md)
- [sdk/python/agentfield/__init__.py](sdk/python/agentfield/__init__.py)
- [sdk/python/agentfield/agent.py](sdk/python/agentfield/agent.py)
- [sdk/python/agentfield/async_execution_manager.py](sdk/python/agentfield/async_execution_manager.py)
- [sdk/python/agentfield/client.py](sdk/python/agentfield/client.py)
- [sdk/python/agentfield/exceptions.py](sdk/python/agentfield/exceptions.py)
- [sdk/python/agentfield/execution_state.py](sdk/python/agentfield/execution_state.py)
- [sdk/python/agentfield/harness/_runner.py](sdk/python/agentfield/harness/_runner.py)
- [sdk/python/agentfield/harness/_schema.py](sdk/python/agentfield/harness/_schema.py)
- [sdk/python/agentfield/harness/providers/claude.py](sdk/python/agentfield/harness/providers/claude.py)
- [sdk/python/agentfield/harness/providers/codex.py](sdk/python/agentfield/harness/providers/codex.py)
- [sdk/python/agentfield/harness/providers/gemini.py](sdk/python/agentfield/harness/providers/gemini.py)
- [sdk/python/agentfield/harness/providers/opencode.py](sdk/python/agentfield/harness/providers/opencode.py)
- [sdk/python/agentfield/types.py](sdk/python/agentfield/types.py)
- [sdk/python/pyproject.toml](sdk/python/pyproject.toml)
- [sdk/python/tests/test_agent_call.py](sdk/python/tests/test_agent_call.py)
- [sdk/python/tests/test_agent_coverage_additions.py](sdk/python/tests/test_agent_coverage_additions.py)
- [sdk/python/tests/test_async_config.py](sdk/python/tests/test_async_config.py)
- [sdk/python/tests/test_async_execution.py](sdk/python/tests/test_async_execution.py)
- [sdk/python/tests/test_client_laser_push.py](sdk/python/tests/test_client_laser_push.py)
- [sdk/python/tests/test_execution_logger.py](sdk/python/tests/test_execution_logger.py)
- [sdk/python/tests/test_execution_state.py](sdk/python/tests/test_execution_state.py)
- [sdk/python/tests/test_harness_ai_schema_repair.py](sdk/python/tests/test_harness_ai_schema_repair.py)
- [sdk/python/tests/test_harness_provider_claude.py](sdk/python/tests/test_harness_provider_claude.py)
- [sdk/python/tests/test_harness_provider_codex.py](sdk/python/tests/test_harness_provider_codex.py)
- [sdk/python/tests/test_harness_provider_gemini.py](sdk/python/tests/test_harness_provider_gemini.py)
- [sdk/python/tests/test_harness_provider_opencode.py](sdk/python/tests/test_harness_provider_opencode.py)
- [sdk/python/tests/test_harness_runner.py](sdk/python/tests/test_harness_runner.py)
- [sdk/python/tests/test_harness_schema.py](sdk/python/tests/test_harness_schema.py)
- [sdk/typescript/package.json](sdk/typescript/package.json)
- [tests/functional/docker/agentfield-test.yaml](tests/functional/docker/agentfield-test.yaml)

</details>



This page provides definitions for codebase-specific terminology, jargon, and domain concepts used throughout the AgentField project. It serves as a technical reference for onboarding engineers to understand the implementation details and data flow associated with these terms.

## Core System Entities

### Control Plane
The central orchestration service (written in Go) that manages agent registration, routing, memory, and verifiable credentials. It acts as the "Kubernetes for AI Agents," handling the lifecycle and communication of distributed agent nodes.
*   **Implementation**: Defined as `AgentFieldServer` in [control-plane/internal/server/server.go:47-104]().
*   **Key Responsibilities**:
    *   Routing execution requests via `AgentClient` [control-plane/internal/server/server.go:145]().
    *   Managing node health via `StatusManager` [control-plane/internal/server/server.go:168]().
    *   Providing a storage-backed KV and Vector memory system [control-plane/internal/server/server.go:49-50]().

### Agent Node
A running instance of an agent, typically using the Python, TypeScript, or Go SDK. Nodes register themselves with the Control Plane to expose their capabilities (Reasoners and Skills) as REST endpoints.
*   **Implementation**: Managed by `AgentService` in the control plane [control-plane/internal/server/server.go:155](). In Python, the `Agent` class handles the node logic [sdk/python/agentfield/agent.py:92]().

### Reasoner
An agent capability that involves non-deterministic logic, typically involving LLM calls. Reasoners can be nested and call other reasoners or skills.
*   **Implementation**: Registered via the `@app.reasoner()` decorator in Python [sdk/python/agentfield/agent.py:72](). Internally represented as a `ReasonerEntry` [sdk/python/agentfield/agent.py:113-132]().

### Skill
A deterministic function or tool that an agent can execute. Skills are intended to be side-effect heavy or computational, often serving as the "hands" of a reasoner.
*   **Implementation**: Represented as a `SkillEntry` in the SDK [sdk/python/agentfield/agent.py:135-144]().

### Diagram: Request Flow from SDK to Control Plane
This diagram bridges the Natural Language concept of "Calling an Agent" to the specific code entities involved in the execution flow.

```mermaid
graph TD
    subgraph "Agent Node (Python SDK)"
        A["Agent.call() [sdk/python/agentfield/agent.py]"] --> B["AgentFieldClient.execute() [sdk/python/agentfield/client.py]"]
    end

    subgraph "Control Plane (Go)"
        B --> C["/api/v1/execute [control-plane/internal/server/server.go]"]
        C --> D["AgentClient.Call() [control-plane/internal/core/interfaces/interfaces.go]"]
        D --> E["HTTPAgentClient [control-plane/internal/infrastructure/communication/agent_client.go]"]
    end

    subgraph "Target Agent Node"
        E --> F["AgentFieldHandler.handle_request() [sdk/python/agentfield/agent_field_handler.py]"]
    end
```
**Sources**: [sdk/python/agentfield/agent.py:433](), [control-plane/internal/server/server.go:145](), [sdk/python/agentfield/agent_field_handler.py:32]()

---

## Identity & Security Terms

### DID (Decentralized Identifier)
A W3C-standard identifier used to uniquely identify agents and users without a central authority. AgentField uses DIDs for authentication and payload encryption.
*   **Implementation**: Managed by `DIDManager` [sdk/python/agentfield/agent.py:44]() and authenticated via `DIDAuthenticator` [sdk/python/agentfield/did_auth.py:46]().

### VC (Verifiable Credential)
Cryptographically signed statements that prove an execution happened, who triggered it, and what the inputs/outputs were.
*   **Implementation**: Generated by `VCGenerator` [sdk/python/agentfield/agent.py:45]() and verified by the control plane's `vcService` [control-plane/internal/server/server.go:65]().

### Memory Scope
The visibility and persistence level of data stored in the memory system.
*   **Global**: Accessible by all agents.
*   **Actor**: Isolated to a specific DID.
*   **Session**: Isolated to a specific conversation/session ID.
*   **Workflow**: Isolated to a specific execution tree (DAG).
*   **Implementation**: Configured via `MemoryConfig` [sdk/python/agentfield/types.py:61]().

---

## Harness & AI Orchestration

### Harness
A specialized system for delegating tasks to "Coding Agents" (like Claude Code or Codex). It abstracts the complexity of environment setup and multi-turn interaction.
*   **Implementation**: Managed by `HarnessRunner` [sdk/python/agentfield/harness/_runner.py]().
*   **Providers**: Includes `ClaudeCodeProvider`, `CodexProvider`, and `OpenCodeProvider` [sdk/python/agentfield/harness/providers/]() .

### Diagram: Harness Execution Architecture
This diagram shows how the `HarnessRunner` interacts with specific provider implementations to execute coding tasks.

```mermaid
graph TD
    subgraph "Harness System"
        HR["HarnessRunner [sdk/python/agentfield/harness/_runner.py]"]
        HC["HarnessConfig [sdk/python/agentfield/types.py]"]
    end

    subgraph "Providers"
        HR --> CP["ClaudeCodeProvider [sdk/python/agentfield/harness/providers/claude.py]"]
        HR --> OP["OpenCodeProvider [sdk/python/agentfield/harness/providers/opencode.py]"]
        HR --> CX["CodexProvider [sdk/python/agentfield/harness/providers/codex.py]"]
    end

    subgraph "Output Processing"
        CP --> SE["SchemaExtractor [sdk/python/agentfield/harness/_schema.py]"]
        SE --> RES["HarnessResult [sdk/python/agentfield/harness/_result.py]"]
    end
```
**Sources**: [sdk/python/agentfield/harness/_runner.py](), [sdk/python/agentfield/types.py:60](), [sdk/python/agentfield/harness/providers/claude.py]()

---

## Infrastructure Jargon

### AF CLI
The primary command-line tool for managing AgentField. It handles starting the server, installing agents, and viewing logs.
*   **Implementation**: Main entry point in [control-plane/cmd/af/main.go]().

### AgentField Home (`~/.agentfield`)
The default directory where the control plane stores its configuration, local database (SQLite), and registry of installed agents.
*   **Implementation**: Resolved in [control-plane/internal/server/server.go:109-116]().

### Registry (`installed.json` / `installed.yaml`)
A file-based database that tracks which agent nodes are installed on the local machine and how to start them.
*   **Implementation**: Managed by `LocalRegistryStorage` [control-plane/internal/server/server.go:150]().

### Table of Abbreviations

| Abbreviation | Full Term | Context |
| :--- | :--- | :--- |
| **CP** | Control Plane | The central Go server. |
| **DID** | Decentralized Identifier | Identity management [sdk/python/agentfield/did_auth.py](). |
| **VC** | Verifiable Credential | Audit trails and security [sdk/python/agentfield/vc_generator.py](). |
| **KV** | Key-Value | The basic memory storage pattern. |
| **RAG** | Retrieval-Augmented Generation | Vector memory and search capabilities. |
| **DAG** | Directed Acyclic Graph | The structure of a multi-agent workflow. |

**Sources**: [control-plane/internal/server/server.go:1-104](), [sdk/python/agentfield/agent.py:1-150](), [sdk/python/agentfield/did_auth.py:45-52](), [README.md:1-100]()