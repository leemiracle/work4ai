<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/ParrotServe · page 4 ServeCore Layer · fetched 2026-10-26 -->

# ServeCore Layer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [parrot/serve/backend_repr/engine.py](parrot/serve/backend_repr/engine.py)
- [parrot/serve/context_manager.py](parrot/serve/context_manager.py)
- [parrot/serve/core.py](parrot/serve/core.py)
- [parrot/serve/engine_manager.py](parrot/serve/engine_manager.py)
- [parrot/serve/scheduler/__init__.py](parrot/serve/scheduler/__init__.py)
- [parrot/serve/scheduler/completion_task.py](parrot/serve/scheduler/completion_task.py)
- [parrot/serve/scheduler/global_scheduler.py](parrot/serve/scheduler/global_scheduler.py)
- [parrot/serve/session/graph_executor.py](parrot/serve/session/graph_executor.py)
- [parrot/serve/session/session.py](parrot/serve/session/session.py)
- [parrot/serve/session_manager.py](parrot/serve/session_manager.py)
- [parrot/serve/variable_manager.py](parrot/serve/variable_manager.py)
- [tests/serve/test_context.py](tests/serve/test_context.py)
- [tests/serve/test_graph.py](tests/serve/test_graph.py)
- [tests/serve/test_prefix_matcher.py](tests/serve/test_prefix_matcher.py)
- [tests/serve/test_session.py](tests/serve/test_session.py)
- [tests/serve/test_sv.py](tests/serve/test_sv.py)
- [tests/serve/test_tokenizer.py](tests/serve/test_tokenizer.py)

</details>



The ServeCore layer is the central orchestration component of ParrotServe, responsible for coordinating all distributed LLM serving operations. It acts as the intermediary between client applications and the engine layer, managing sessions, scheduling computation graphs, and optimizing resource utilization through sophisticated context management.

For information about the client-facing programming interfaces, see [Client Programming Interface](#3). For details about the backend LLM engines, see [Engine Layer](#5).

## Overview

The ServeCore layer implements a distributed orchestration architecture centered around the `ParrotServeCore` class. It manages multiple concurrent user sessions, each containing computation graphs that represent LLM request dependencies. The core innovation is its ability to automatically parallelize and optimize LLM requests through semantic variable abstraction and shared context management.

**Core Components Architecture**
```mermaid
graph TB
    subgraph "ParrotServeCore"
        A[ParrotServeCore] -->|manages| B[SessionManager]
        A -->|manages| C[EngineManager] 
        A -->|manages| D[GlobalScheduler]
        A -->|manages| E[ServeCoreContextManager]
        A -->|manages| F[SemanticVariableManager]
        A -->|manages| G[TokenizersWrapper]
    end
    
    subgraph "Per-Session Components"
        H[Session] -->|contains| I[GraphExecutor]
        H -->|contains| J[PyNativeExecutor]
        I -->|uses| K[ComputeGraph]
    end
    
    B -->|creates| H
    D -->|schedules| L[CompletionTask]
    I -->|submits| L
    
    L -->|executed by| M[ExecutionEngine]
    E -->|provides contexts to| L
    F -->|manages variables for| K
```

Sources: [parrot/serve/core.py:34-89](), [parrot/serve/session/session.py:43-84](), [parrot/serve/session/graph_executor.py:32-60]()

## Request Processing Pipeline

The ServeCore processes requests through a multi-stage pipeline that transforms client semantic function calls into schedulable engine tasks. This pipeline enables automatic parallelization and optimization of LLM requests.

**Request Flow Through ServeCore**
```mermaid
graph TD
    A["submit_semantic_call()"] --> B[ChunkedSemanticCallRequest]
    B --> C[RequestChain]
    C --> D[CompletionChain]
    D --> E[CompletionTask]
    
    F[SessionManager] --> G["check_session_status()"]
    G --> H["session_access_update()"]
    H --> I["session.add_request()"]
    
    I --> J[SemanticVariableManager]
    J --> K["create_vars_for_semantic_request_chain()"]
    K --> L[GraphExecutor]
    L --> M["add_request()"]
    
    M --> N["_execute_coroutine()"]
    N --> O[TaskCreator]
    O --> P["create_task()"]
    P --> Q[GlobalScheduler]
    Q --> R["submit_task()"]
    
    subgraph "Task Execution"
        S["wait_scheduled()"] --> T["tokenize_chain()"]
        T --> U[ServeCoreContextManager]
        U --> V["set_task_contexts()"]
        V --> W["execute()"]
    end
    
    R --> S
```

Sources: [parrot/serve/core.py:198-225](), [parrot/serve/session/session.py:103-134](), [parrot/serve/session/graph_executor.py:103-116]()

The pipeline handles both semantic function calls and Python native function calls through separate but parallel processing paths. Each request is converted into a computation graph where nodes represent either constant text fills or placeholder generations.

| Stage | Component | Responsibility |
|-------|-----------|----------------|
| Request Parsing | `ChunkedSemanticCallRequest` | Parse template and parameters |
| Graph Construction | `RequestChain` | Convert to node sequence |
| Variable Assignment | `SemanticVariableManager` | Create/assign semantic variables |
| Task Creation | `TaskCreator` | Create schedulable tasks |
| Scheduling | `GlobalScheduler` | Assign tasks to engines |
| Context Assignment | `ServeCoreContextManager` | Optimize memory usage |
| Execution | `GraphExecutor` | Execute Fill/Generate primitives |

## Session Management

The `SessionManager` maintains isolated execution environments for each connected client application. Sessions provide namespace isolation for semantic variables while enabling global optimizations across sessions through shared constant prefixes.

**Session Lifecycle Management**
```mermaid
graph LR
    A["register_session()"] --> B[Session]
    B --> C[SessionStatus.RUNNING]
    
    D["session_access_update()"] --> E["_session_last_access_time"]
    
    F["check_running_sessions()"] --> G{Session Expired?}
    G -->|Yes| H[SessionStatus.DEAD]
    G -->|No| I{Executor Exception?}
    I -->|Yes| J[SessionStatus.BAD]
    
    K["sweep_not_running_sessions()"] --> L["_remove_session()"]
    L --> M["free_session_resources()"]
    
    subgraph "Session Resources"
        N[GraphExecutor]
        O[PyNativeExecutor] 
        P[Session Contexts]
        Q[Local Variable Space]
    end
    
    B --> N
    B --> O
    M --> P
    M --> Q
```

Sources: [parrot/serve/session_manager.py:22-156](), [parrot/serve/session/session.py:192-208]()

Each session contains its own `GraphExecutor` for managing computation graphs and `PyNativeExecutor` for Python function execution. Sessions automatically expire after a configurable timeout period, triggering cleanup of all associated resources including contexts and semantic variables.

## Global Task Scheduling 

The `GlobalScheduler` implements sophisticated algorithms to distribute completion tasks across available engines while considering model compatibility, capacity constraints, and context optimization opportunities.

**Scheduling Algorithm Flow**
```mermaid
graph TD
    A["submit_task()"] --> B[task_queue]
    
    C["schedule()"] --> D{app_fifo enabled?}
    D -->|Yes| E["Sort by SV depth"]
    D -->|No| F[FIFO order]
    
    E --> G[Task Grouping]
    F --> G
    
    G --> H{graph_group enabled?}
    H -->|Yes| I["Group by chain_groups"]
    
    G --> J{ctx_group enabled?} 
    J -->|Yes| K["Group by first_node.sv"]
    
    I --> L["_find_engine()"]
    K --> L
    G -->|No grouping| L
    
    L --> M["_get_engine_list()"]
    M --> N[Engine Compatibility Check]
    
    subgraph "Engine Selection Criteria"
        O[Model Type Match]
        P[Model Name Match] 
        Q[Task Capacity Check]
        R[Token Capacity Check]
        S[Context Awareness]
    end
    
    N --> O
    N --> P  
    N --> Q
    N --> R
    
    S --> T["query_prefixes_in_engines()"]
    T --> U[Best Engine Selection]
    U --> V["task.schedule_to()"]
```

Sources: [parrot/serve/scheduler/global_scheduler.py:32-254](), [parrot/serve/scheduler/completion_task.py:66-76]()

The scheduler supports multiple optimization strategies:

- **Application FIFO**: Prioritizes tasks by semantic variable depth to minimize end-to-end latency
- **Graph Grouping**: Batches tasks sharing common chain groups for improved throughput  
- **Context Grouping**: Batches tasks with shared prefixes to leverage cached contexts
- **Context Awareness**: Prefers engines already containing relevant cached prefixes

## Context Management and Optimization

The `ServeCoreContextManager` implements advanced memory management through prefix caching and reference counting. It enables significant performance improvements by sharing cached KV contexts across requests and sessions.

**Context Sharing and Caching Strategy**
```mermaid
graph TB
    subgraph "Context Types"
        A[Intra-session Context]
        B[Inter-session Context] 
        C[Constant Prefix Context]
    end
    
    subgraph "PrefixCache per Engine"
        D["prefix_hash -> context_id"]
        E["{{sv0}} -> ctx0"]
        F["{{sv0}}{{sv1}} -> ctx1"] 
        G["{{sv0}}{{sv1}}{{sv2}} -> ctx2"]
    end
    
    H["set_task_contexts()"] --> I{Prefix cached?}
    I -->|Yes| J["get_cached_prefix_context()"]
    I -->|No| K["_new_context()"]
    
    J --> L["_add_ref_counter()"]
    K --> M["cache_prefix_context()"]
    M --> L
    
    N["free_task_contexts()"] --> O["_free_context()"]
    O --> P{ref_counter > 0?}
    P -->|Yes| Q[Keep Context]
    P -->|No| R["free_context() API call"]
    
    subgraph "Constant Prefix Optimization"
        S[SemanticVariableManager]
        T["constant_prefix_contexts"]
        U["Extra ref_counter"]
    end
    
    S --> T
    T --> U
    U --> L
```

Sources: [parrot/serve/context_manager.py:77-379](), [parrot/serve/variable_manager.py:154-164]()

The context manager implements several key optimizations:

- **Prefix Hashing**: Maps content-based hashes to cached contexts using format `{{var_id}}{{var_id2}}`
- **Reference Counting**: Tracks context usage across multiple tasks and sessions  
- **Constant Prefix Variables**: Maintains global cache for frequently used text prefixes
- **Hierarchical Context Forking**: Creates parent-child context relationships for efficient memory usage

## Integration Points

The ServeCore coordinates with other system layers through well-defined interfaces:

**Layer Communication Protocols**
```mermaid
graph TB
    subgraph "Client Layer APIs"
        A["POST /session/register"]
        B["POST /semantic_call"] 
        C["GET /semantic_variable/{var_id}"]
        D["PUT /semantic_variable/{var_id}"]
    end
    
    subgraph "ServeCore Processing"  
        E[ParrotServeCore]
        F["register_session()"]
        G["submit_semantic_call()"]
        H["get_semantic_variable()"]
        I["set_semantic_variable()"]
    end
    
    subgraph "Engine Layer APIs"
        J["POST /register"]
        K["POST /heartbeat"]
        L["POST /fill"]
        M["POST /generate"]
    end
    
    A --> F
    B --> G  
    C --> H
    D --> I
    
    E --> F
    E --> G
    E --> H  
    E --> I
    
    N[EngineManager] --> J
    N --> K
    O[GraphExecutor] --> L
    O --> M
```

Sources: [parrot/serve/core.py:99-133](), [parrot/serve/core.py:198-331](), [parrot/serve/session/graph_executor.py:158-241]()

The ServeCore maintains engine connectivity through heartbeat monitoring and automatic failure detection. When engines become unresponsive, the `EngineManager` marks them as dead and removes them from the scheduling pool, ensuring system resilience.

| Interface | Direction | Purpose |
|-----------|-----------|---------|
| HTTP REST APIs | Client → ServeCore | Session and variable management |
| Primitive APIs | ServeCore → Engine | Fill/Generate/Free operations |
| Registration | Engine → ServeCore | Engine discovery and capabilities |
| Heartbeat | Engine → ServeCore | Health monitoring and runtime info |

---

