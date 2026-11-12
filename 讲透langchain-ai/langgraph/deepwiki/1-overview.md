<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/langgraph · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [AGENTS.md](AGENTS.md)
- [CLAUDE.md](CLAUDE.md)
- [README.md](README.md)
- [libs/checkpoint-conformance/uv.lock](libs/checkpoint-conformance/uv.lock)
- [libs/checkpoint-postgres/pyproject.toml](libs/checkpoint-postgres/pyproject.toml)
- [libs/checkpoint-postgres/uv.lock](libs/checkpoint-postgres/uv.lock)
- [libs/checkpoint-sqlite/pyproject.toml](libs/checkpoint-sqlite/pyproject.toml)
- [libs/checkpoint-sqlite/uv.lock](libs/checkpoint-sqlite/uv.lock)
- [libs/checkpoint/pyproject.toml](libs/checkpoint/pyproject.toml)
- [libs/checkpoint/uv.lock](libs/checkpoint/uv.lock)
- [libs/langgraph/README.md](libs/langgraph/README.md)
- [libs/langgraph/pyproject.toml](libs/langgraph/pyproject.toml)
- [libs/langgraph/uv.lock](libs/langgraph/uv.lock)
- [libs/prebuilt/pyproject.toml](libs/prebuilt/pyproject.toml)
- [libs/prebuilt/uv.lock](libs/prebuilt/uv.lock)
- [libs/sdk-js/README.md](libs/sdk-js/README.md)
- [libs/sdk-py/MIGRATION.md](libs/sdk-py/MIGRATION.md)
- [libs/sdk-py/README.md](libs/sdk-py/README.md)
- [libs/sdk-py/uv.lock](libs/sdk-py/uv.lock)

</details>



## Purpose and Scope

LangGraph is a low-level orchestration framework for building stateful, multi-actor applications with Large Language Models (LLMs). Unlike high-level abstractions, LangGraph provides infrastructure without abstracting prompts or architecture, giving developers full control over their application logic [libs/langgraph/pyproject.toml:5-8](). It is specifically designed to handle the unique challenges of long-running agentic workflows, such as persistence, cycle management, and human intervention [README.md:22-24]().

### Core Capabilities

LangGraph provides foundational infrastructure for production-grade agents:

| Capability | Description | Implementation |
|------------|-------------|----------------|
| **Durable Execution** | Agents persist through failures and resume from exact state | Build agents that persist through failures and resume from exactly where they left off [README.md:39](). |
| **Human-in-the-Loop** | Inspect and modify agent state at any execution point | Incorporate human oversight by inspecting and modifying agent state during execution [README.md:40](). |
| **Comprehensive Memory** | Short-term working memory and long-term persistent storage | Short-term working memory for ongoing reasoning and long-term persistent memory across sessions [README.md:41](). |

The framework is built on a Bulk Synchronous Parallel (BSP) execution model inspired by Google's Pregel paper [README.md:82](), [libs/langgraph/README.md:46]().

Sources: [README.md:12-43](), [libs/langgraph/pyproject.toml:5-8](), [README.md:80-82](), [libs/langgraph/README.md:20-28]()

## Core Concepts

LangGraph centers on a stateful graph abstraction where execution is managed through discrete supersteps.

### Core Abstractions

| Concept | Description | Primary Implementation |
|---------|-------------|----------------------|
| **Graph** | Computational structure with nodes (functions) and edges (control flow) | `StateGraph` class [libs/langgraph/README.md:24-28]() |
| **State** | Shared data structure managed through typed channels | `TypedDict` schemas [libs/langgraph/README.md:24-26]() |
| **Checkpoint** | Serialized snapshot containing state and execution metadata | `BaseCheckpointSaver` interface [libs/checkpoint/pyproject.toml:8]() |

### Graph Definition Approaches

**Declarative API** (`StateGraph`):
Developers define nodes as Python functions and use the `StateGraph` builder to specify the workflow and state schema [libs/langgraph/README.md:24-28]().

```python
from langgraph.graph import START, StateGraph
from typing_extensions import TypedDict

class State(TypedDict):
    text: str

def node_a(state: State) -> dict:
    return {"text": state["text"] + "a"}

graph = StateGraph(State)
graph.add_node("node_a", node_a)
graph.add_edge(START, "node_a")
```
[libs/langgraph/README.md:24-28]()

### Execution Model

At runtime, the execution engine orchestrates execution:
1. **Durable Execution**: Automatically resumes from the last successful step [README.md:39]().
2. **State Management**: Uses reducers to apply updates to the shared state [libs/langgraph/README.md:22-24]().
3. **Persistence**: Saves state snapshots via a `BaseCheckpointSaver` [libs/checkpoint/pyproject.toml:8]().

Sources: [libs/langgraph/README.md:20-46](), [README.md:80-82](), [libs/checkpoint/pyproject.toml:5-17]()

## Architectural Components

The LangGraph system comprises major subsystems organized as a monorepo, managed with the `uv` build tool [libs/langgraph/pyproject.toml:83-90]().

### High-Level System Architecture

```mermaid
graph TB
    subgraph "CoreExecution [libs/langgraph]"
        "StateGraph[StateGraph]"
        "Pregel[Pregel Engine]"
    end
    
    subgraph "Persistence [libs/checkpoint-*]"
        "BaseCheckpointSaver[BaseCheckpointSaver Interface]"
        "SqliteSaver[SqliteSaver (libs/checkpoint-sqlite)]"
        "PostgresSaver[PostgresSaver (libs/checkpoint-postgres)]"
    end
    
    subgraph "ClientSDKs [libs/sdk-py]"
        "LangGraphClient[LangGraphClient]"
    end
    
    subgraph "Prebuilt [libs/prebuilt]"
        "create_react_agent[create_react_agent()]"
        "ToolNode[ToolNode]"
    end
    
    "StateGraph" -->|"compile()"| "Pregel"
    "Pregel" -->|"save()"| "BaseCheckpointSaver"
    
    "LangGraphClient" -->|"HTTP API"| "Pregel"
    
    "create_react_agent" -->|"returns"| "StateGraph"
    "ToolNode" -->|"used in"| "StateGraph"
```

**Code Entity Mapping:**

1. **Core Execution Engine**: 
   - `StateGraph` at [libs/langgraph/README.md:24-28](): The primary builder for defining application logic.
   - `Pregel`: The underlying internal execution engine inspired by Google Pregel [README.md:82]().

2. **Persistence Layer**: 
   - `BaseCheckpointSaver` at [libs/checkpoint/pyproject.toml:8](): Base interface for persisting graph state.
   - `PostgresSaver` at [libs/checkpoint-postgres/pyproject.toml:8](): Production-grade PostgreSQL persistence.
   - `SqliteSaver` at [libs/checkpoint-sqlite/pyproject.toml:13-17](): Local SQLite persistence via `aiosqlite`.

3. **Client SDKs**: 
   - `LangGraphClient` at [libs/sdk-py/README.md:30](): Python SDK for interacting with deployed LangGraph servers.

4. **Prebuilt Components**: 
   - `create_react_agent()` at [libs/langgraph/pyproject.toml:30](): Pre-configured ReAct agent factory.
   - `ToolNode` at [libs/prebuilt/pyproject.toml:8](): Standardized node for executing tool calls.

Sources: [libs/langgraph/pyproject.toml:26-33](), [libs/langgraph/README.md:20-46](), [README.md:80-82](), [libs/checkpoint/pyproject.toml:5-17](), [libs/checkpoint-postgres/pyproject.toml:5-19]()

## Package Ecosystem

LangGraph uses a modular architecture where the `langgraph` core package coordinates several specialized libraries [libs/langgraph/pyproject.toml:26-33]().

```mermaid
graph LR
    "langgraph[langgraph]"
    "checkpoint[langgraph-checkpoint]"
    "cp_postgres[langgraph-checkpoint-postgres]"
    "cp_sqlite[langgraph-checkpoint-sqlite]"
    "prebuilt[langgraph-prebuilt]"
    "sdk[langgraph-sdk]"
    
    "langgraph" --> "checkpoint"
    "langgraph" --> "prebuilt"
    "langgraph" --> "sdk"
    
    "prebuilt" --> "checkpoint"
    
    "cp_postgres" --> "checkpoint"
    "cp_sqlite" --> "checkpoint"
```

**Package Descriptions:**

| Package | Purpose | Key Dependencies |
|---------|---------|------------------|
| `langgraph` | Core framework for stateful graph execution | `langgraph-checkpoint`, `langgraph-sdk`, `langgraph-prebuilt` [libs/langgraph/pyproject.toml:26-30]() |
| `langgraph-checkpoint` | Base interfaces for durable execution and serialization | `langchain-core`, `ormsgpack` [libs/checkpoint/pyproject.toml:14-17]() |
| `langgraph-prebuilt` | High-level APIs for agents and tool execution | `langgraph-checkpoint`, `langchain-core` [libs/prebuilt/pyproject.toml:26-29]() |
| `langgraph-sdk` | Python client for remote execution and management | `pydantic`, `httpx` [libs/langgraph/pyproject.toml:29-33]() |

Sources: [libs/langgraph/pyproject.toml:26-33](), [libs/prebuilt/pyproject.toml:26-29](), [libs/checkpoint/pyproject.toml:5-17](), [libs/checkpoint-postgres/pyproject.toml:14-19]()

## Integration with LangChain Ecosystem

LangGraph is built by the LangChain team and integrates deeply with its products while remaining usable as a standalone framework [README.md:82]().

- **LangChain**: Provides composable components (models, tools, prompts) used within graph nodes [README.md:55]().
- **LangSmith**: Used for tracing, observability, and debugging complex agent trajectories [README.md:42](), [README.md:56]().
- **LangSmith Deployment**: Purpose-built infrastructure for hosting and scaling LangGraph applications [README.md:57]().

Sources: [README.md:42-57](), [libs/langgraph/README.md:20-28]()

## System Requirements

**Python Version**: `>=3.10` [libs/langgraph/pyproject.toml:10]()

**Build System**: `hatchling` is used as the build backend across all packages [libs/langgraph/pyproject.toml:1-3](), [libs/checkpoint/pyproject.toml:1-3]().

**Core Dependencies**:
- `langchain-core>=1.4.7,<2` [libs/langgraph/pyproject.toml:27]()
- `langgraph-checkpoint>=4.1.0,<5.0.0` [libs/langgraph/pyproject.toml:28]()
- `pydantic>=2.7.4` [libs/langgraph/pyproject.toml:32]()
- `xxhash>=3.5.0` [libs/langgraph/pyproject.toml:31]()

Sources: [libs/langgraph/pyproject.toml:1-33](), [libs/checkpoint/pyproject.toml:1-17]()

---

