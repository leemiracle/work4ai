<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/langgraph · page 7 Server API · fetched 2026-10-26 -->

# Server API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [libs/sdk-py/langgraph_sdk/__init__.py](libs/sdk-py/langgraph_sdk/__init__.py)
- [libs/sdk-py/langgraph_sdk/auth/__init__.py](libs/sdk-py/langgraph_sdk/auth/__init__.py)
- [libs/sdk-py/langgraph_sdk/auth/exceptions.py](libs/sdk-py/langgraph_sdk/auth/exceptions.py)
- [libs/sdk-py/langgraph_sdk/auth/types.py](libs/sdk-py/langgraph_sdk/auth/types.py)
- [libs/sdk-py/langgraph_sdk/client.py](libs/sdk-py/langgraph_sdk/client.py)
- [libs/sdk-py/langgraph_sdk/schema.py](libs/sdk-py/langgraph_sdk/schema.py)
- [libs/sdk-py/pyproject.toml](libs/sdk-py/pyproject.toml)

</details>



The LangGraph Server API provides a structured interface for deploying, managing, and executing stateful multi-actor applications. It abstracts the underlying graph execution engine into a set of RESTful resources: **Assistants**, **Threads**, **Runs**, **Cron Jobs**, and a persistent **Store**.

This API is designed to handle the complexities of long-running agentic workflows, including state persistence, human-in-the-loop interactions, and background scheduling.

## API Resource Overview

The Server API is organized around five primary resource types, each managed by dedicated clients in the `langgraph-sdk` package [libs/sdk-py/langgraph_sdk/client.py:1-8]().

| Resource | Purpose | Code Entity |
| :--- | :--- | :--- |
| **Assistant** | Versioned configurations of a graph, including specific parameters and metadata. | `AssistantsClient` [libs/sdk-py/langgraph_sdk/client.py:12-12]() |
| **Thread** | Stateful sessions that persist the progress of a conversation or task across multiple runs. | `ThreadsClient` [libs/sdk-py/langgraph_sdk/client.py:21-21]() |
| **Run** | An individual execution of an Assistant on a Thread, supporting various streaming modes. | `RunsClient` [libs/sdk-py/langgraph_sdk/client.py:19-19]() |
| **Cron** | Scheduled triggers that initiate Runs based on a defined frequency. | `CronClient` [libs/sdk-py/langgraph_sdk/client.py:17-17]() |
| **Store** | A cross-thread persistent document store for long-term memory and shared state. | `StoreClient` [libs/sdk-py/langgraph_sdk/client.py:20-20]() |

**Sources:**
- [libs/sdk-py/langgraph_sdk/client.py:1-55]()
- [libs/sdk-py/langgraph_sdk/schema.py:1-109]()

## Lifecycle and Execution Flow

The following diagram illustrates how natural language interactions map to the underlying code entities and API resources during a typical execution lifecycle.

### From Interaction to Execution
```mermaid
graph TD
    "UserInteraction" -- "POST /threads/{id}/runs" --> "RunsClient.stream()/.create()"
    subgraph "Code Entity Space"
        "RunsClient" -- "loads" --> "Assistant[GraphSchema]"
        "RunsClient" -- "binds to" --> "Thread[thread_id]"
        "Assistant[GraphSchema]" -- "references" --> "PregelGraph"
    end
    "PregelGraph" -- "executes step" --> "BaseCheckpointSaver"
    "BaseCheckpointSaver" -- "persists" --> "DB[(State Storage)]"
```
**Sources:**
- [libs/sdk-py/langgraph_sdk/client.py:12-31]()
- [libs/sdk-py/langgraph_sdk/schema.py:208-220]()
- [libs/sdk-py/langgraph_sdk/schema.py:221-245]()
- [libs/sdk-py/langgraph_sdk/schema.py:246-261]()

## Core Resources

### Assistants and Threads
**Assistants** act as templates or deployments. They wrap a specific `graph_id` with a set of `config` parameters and `metadata` [libs/sdk-py/langgraph_sdk/schema.py:246-261](). This allows developers to deploy multiple "personalities" or configurations of the same underlying graph.

**Threads** provide the context for stateful execution. A thread maintains a history of checkpoints, allowing an agent to "remember" previous interactions. The status of a thread can be `idle`, `busy`, `interrupted`, or `error` [libs/sdk-py/langgraph_sdk/schema.py:34-41]().

For details, see [Assistants and Threads](#7.1).

### Runs
A **Run** is the active execution of an assistant. The API supports both stateful runs (associated with a thread) and stateless runs. Execution can be monitored via streaming using various `StreamMode` options such as `values`, `updates`, `messages`, or `debug` [libs/sdk-py/langgraph_sdk/schema.py:51-72]().

Runs follow a status lifecycle: `pending` -> `running` -> `success`/`error`/`timeout`/`interrupted` [libs/sdk-py/langgraph_sdk/schema.py:23-32]().

For details, see [Runs](#7.2).

### Cron Jobs
**Cron Jobs** automate graph execution. They allow users to schedule runs on a specific thread or for a specific assistant using standard cron syntax. The `CronSortBy` enum defines how these resources can be organized, including `next_run_date` and `end_time` [libs/sdk-py/langgraph_sdk/schema.py:166-177]().

For details, see [Cron Jobs](#7.3).

### Store API
The **Store** is a specialized resource for persistent, cross-thread memory. Unlike Thread state, which is local to a specific conversation, the Store allows agents to persist information (like user preferences or global knowledge) that can be accessed across different threads and assistants via `StoreClient` [libs/sdk-py/langgraph_sdk/client.py:20-20]().

For details, see [Store API](#7.4).

## Authentication and Security
The Server API includes a robust authentication and authorization system via the `Auth` class [libs/sdk-py/langgraph_sdk/auth/__init__.py:13-107](). Developers can register custom `@auth.authenticate` handlers [libs/sdk-py/langgraph_sdk/auth/__init__.py:49-60]() and fine-grained `@auth.on` authorization rules [libs/sdk-py/langgraph_sdk/auth/__init__.py:62-94]() to control access to resources based on user identity and permissions [libs/sdk-py/langgraph_sdk/auth/types.py:164-179](). The system supports `MinimalUser` protocols and `AuthContext` for request-level security [libs/sdk-py/langgraph_sdk/auth/types.py:151-162]().

## System Architecture Mapping

The following diagram bridges high-level API concepts to the internal client components used to communicate with the server.

### API to System Mapping
```mermaid
graph LR
    subgraph "Natural Language Space"
        "Schedule['Every Monday at 9AM']"
        "Memory['Remember my name is Alice']"
        "Task['Process this document']"
    end

    subgraph "Code Entity Space"
        "Schedule['Every Monday at 9AM']" -- "maps to" --> "SyncCronClient.create(schedule='0 9 * * 1')"
        "Memory['Remember my name is Alice']" -- "maps to" --> "SyncStoreClient.put(namespace, key, value)"
        "Task['Process this document']" -- "maps to" --> "SyncRunsClient.create(input={...})"
        
        "SyncCronClient.create(schedule='0 9 * * 1')" -- "triggers" --> "SyncRunsClient.create(input={...})"
        "SyncRunsClient.create(input={...})" -- "executes on" --> "Thread[thread_id]"
    end
```
**Sources:**
- [libs/sdk-py/langgraph_sdk/client.py:25-31]()
- [libs/sdk-py/langgraph_sdk/schema.py:166-178]()
- [libs/sdk-py/langgraph_sdk/schema.py:81-88]()
- [libs/sdk-py/langgraph_sdk/auth/types.py:111-120]()

---

