<!-- source: DeepWiki mcp.deepwiki.com · repo Significant-Gravitas/AutoGPT · extra page Execution System · fetched 2026-10-26 -->

# Execution System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [autogpt_platform/backend/backend/blocks/agent.py](autogpt_platform/backend/backend/blocks/agent.py)
- [autogpt_platform/backend/backend/data/block.py](autogpt_platform/backend/backend/data/block.py)
- [autogpt_platform/backend/backend/data/credit_ceiling_test.py](autogpt_platform/backend/backend/data/credit_ceiling_test.py)
- [autogpt_platform/backend/backend/data/credit_concurrency_test.py](autogpt_platform/backend/backend/data/credit_concurrency_test.py)
- [autogpt_platform/backend/backend/data/credit_integration_test.py](autogpt_platform/backend/backend/data/credit_integration_test.py)
- [autogpt_platform/backend/backend/data/credit_metadata_test.py](autogpt_platform/backend/backend/data/credit_metadata_test.py)
- [autogpt_platform/backend/backend/data/credit_refund_test.py](autogpt_platform/backend/backend/data/credit_refund_test.py)
- [autogpt_platform/backend/backend/data/credit_test.py](autogpt_platform/backend/backend/data/credit_test.py)
- [autogpt_platform/backend/backend/data/credit_underflow_test.py](autogpt_platform/backend/backend/data/credit_underflow_test.py)
- [autogpt_platform/backend/backend/data/credit_user_balance_migration_test.py](autogpt_platform/backend/backend/data/credit_user_balance_migration_test.py)
- [autogpt_platform/backend/backend/data/execution.py](autogpt_platform/backend/backend/data/execution.py)
- [autogpt_platform/backend/backend/data/execution_io_cap_test.py](autogpt_platform/backend/backend/data/execution_io_cap_test.py)
- [autogpt_platform/backend/backend/data/generate_data.py](autogpt_platform/backend/backend/data/generate_data.py)
- [autogpt_platform/backend/backend/data/graph.py](autogpt_platform/backend/backend/data/graph.py)
- [autogpt_platform/backend/backend/data/graph_test.py](autogpt_platform/backend/backend/data/graph_test.py)
- [autogpt_platform/backend/backend/data/includes.py](autogpt_platform/backend/backend/data/includes.py)
- [autogpt_platform/backend/backend/data/model.py](autogpt_platform/backend/backend/data/model.py)
- [autogpt_platform/backend/backend/executor/manager.py](autogpt_platform/backend/backend/executor/manager.py)
- [autogpt_platform/backend/backend/executor/utils.py](autogpt_platform/backend/backend/executor/utils.py)
- [autogpt_platform/backend/backend/executor/utils_test.py](autogpt_platform/backend/backend/executor/utils_test.py)
- [autogpt_platform/backend/backend/util/exceptions.py](autogpt_platform/backend/backend/util/exceptions.py)
- [autogpt_platform/backend/backend/util/settings.py](autogpt_platform/backend/backend/util/settings.py)
- [autogpt_platform/backend/schema.prisma](autogpt_platform/backend/schema.prisma)
- [autogpt_platform/frontend/src/lib/autogpt-server-api/types.ts](autogpt_platform/frontend/src/lib/autogpt-server-api/types.ts)

</details>



## Purpose and Scope

The Execution System is responsible for orchestrating and managing the execution of agent graphs (workflows) in the AutoGPT Platform. It handles the scheduling, queuing, execution, and monitoring of individual nodes within agent graphs, ensuring proper dependency management, resource allocation, and status tracking throughout the execution lifecycle.

This document covers the core execution engine and orchestration components. For information about the graph structure and node definitions, see [Block System](). For API endpoints that trigger executions, see [API System]().

## Architecture Overview

The Execution System follows a distributed, event-driven architecture with multiple cooperating services:

### High-Level Component Architecture

```mermaid
graph TB
    subgraph "Execution Control Layer"
        EM["ExecutionManager<br/>(manager.py)"]
        SCHED["Scheduler<br/>(scheduler.py)"]
    end
    
    subgraph "Data Services"
        DB["DatabaseManager<br/>(database.py)"]
        CREDS["IntegrationCredentialsManager<br/>(credentials_store.py)"]
    end
    
    subgraph "Message Infrastructure"
        RMQ["RabbitMQ<br/>Graph & Node Queues"]
        REDIS["Redis<br/>Event Bus & Cache"]
    end
    
    subgraph "Execution Workers"
        GE["Graph Executor<br/>Process Pool"]
        NE["Node Executor<br/>Async Workers"]
    end
    
    subgraph "External Systems"
        BLOCKS["Block Implementations<br/>(blocks/)"]
        APIS["External APIs<br/>(LLM, OAuth, etc.)"]
    end
    
    %% Control flow
    EM --> DB
    EM --> RMQ
    EM --> REDIS
    EM --> CREDS
    
    %% Execution flow
    RMQ --> GE
    GE --> NE
    NE --> BLOCKS
    BLOCKS --> APIS
    
    %% Data persistence
    GE --> DB
    NE --> DB
    
    %% Event broadcasting
    GE --> REDIS
    NE --> REDIS
```

Sources: [autogpt_platform/backend/backend/executor/manager.py:1-887](), [autogpt_platform/backend/backend/executor/database.py:1-124](), [autogpt_platform/backend/backend/executor/utils.py:1-773]()

## Core Components

### ExecutionManager

The `ExecutionManager` is the central orchestrator that manages the lifecycle of graph executions. It operates as a multi-process system with separate worker pools for graph and node execution.

```mermaid
graph TB
    subgraph "ExecutionManager Process"
        MM["Main Manager<br/>ProcessPoolExecutor"]
        GW["Graph Workers<br/>(NUM_GRAPH_WORKERS)"]
        MM --> GW
    end
    
    subgraph "Graph Worker Process"
        GE["Graph Executor<br/>(Executor.on_graph_execution)"]
        NEL["Node Execution Loop<br/>(asyncio event loop)"]
        NEVAL["Node Evaluation Loop<br/>(asyncio event loop)"]
        
        GE --> NEL
        GE --> NEVAL
    end
    
    subgraph "Execution Queues"
        GRAPHQ["graph_execution_queue<br/>(GraphExecutionEntry)"]
        NODEQ["Node Execution Queue<br/>(In-Memory)"]
        CANCELQ["graph_execution_cancel_queue<br/>(CancelExecutionEvent)"]
    end
    
    GRAPHQ --> GE
    GE --> NODEQ
    CANCELQ --> GE
    
    NEL --> BLOCKS["Block.execute()"]
    NEVAL --> NEXT["Next Node Enqueueing"]
```

Sources: [autogpt_platform/backend/backend/executor/manager.py:400-887](), [autogpt_platform/backend/backend/executor/manager.py:513-529]()

### Database Manager

The `DatabaseManager` provides a service-oriented interface to all database operations required during execution, including execution tracking, node status updates, and user metadata management.

Key database operations:
- `get_graph_execution()` / `create_graph_execution()` - Graph execution lifecycle
- `get_node_execution()` / `update_node_execution_status()` - Node status tracking  
- `upsert_execution_input()` / `upsert_execution_output()` - Node I/O persistence
- `spend_credits()` / `get_credits()` - Usage billing

Sources: [autogpt_platform/backend/backend/executor/database.py:65-124]()

### Message Queuing System

The system uses RabbitMQ for reliable message delivery between execution components:

```mermaid
graph LR
    subgraph "RabbitMQ Exchanges & Queues"
        GEQ["graph_execution_queue<br/>(GraphExecutionEntry)"]
        GCQ["graph_execution_cancel_queue<br/>(CancelExecutionEvent)"]
        NEQ["Node Execution Queue<br/>(In-Memory)"]
    end
    
    subgraph "Event Bus (Redis)"
        EXEC_EVENTS["execution_event<br/>AsyncRedisExecutionEventBus"]
        WS_EVENTS["WebSocket Events<br/>Real-time Updates"]
    end
    
    API["REST API"] --> GEQ
    API --> GCQ
    
    GEQ --> GE["Graph Executor"]
    GCQ --> GE
    
    GE --> NEQ
    NEQ --> NE["Node Executor"]
    
    NE --> EXEC_EVENTS
    EXEC_EVENTS --> WS_EVENTS
```

Sources: [autogpt_platform/backend/backend/executor/utils.py:69-86](), [autogpt_platform/backend/backend/data/execution.py:58-59]()

## Execution Flow

### Graph Execution Lifecycle

The execution of an agent graph follows this sequence:

```mermaid
sequenceDiagram
    participant API as "REST API"
    participant DB as "DatabaseManager"
    participant RMQ as "RabbitMQ"
    participant GE as "Graph Executor"
    participant NE as "Node Executor"
    participant REDIS as "Redis EventBus"
    
    API->>DB: create_graph_execution()
    API->>RMQ: enqueue GraphExecutionEntry
    RMQ->>GE: pick up execution request
    
    GE->>DB: get_graph_execution_meta()
    GE->>DB: update_graph_execution_start_time()
    GE->>REDIS: broadcast RUNNING status
    
    loop For each starting node
        GE->>NE: enqueue NodeExecutionEntry
        NE->>DB: update_node_execution_status(RUNNING)
        NE->>NE: execute_node()
        NE->>DB: upsert_execution_output()
        NE->>DB: update_node_execution_status(COMPLETED)
        NE->>GE: notify completion
        GE->>GE: enqueue next nodes
    end
    
    GE->>DB: update_graph_execution_stats()
    GE->>REDIS: broadcast COMPLETED status
```

Sources: [autogpt_platform/backend/backend/executor/manager.py:532-887](), [autogpt_platform/backend/backend/executor/manager.py:424-511]()

### Node Execution Process

Individual node execution involves block instantiation, input validation, credential acquisition, and output processing:

```mermaid
graph TD
    START["NodeExecutionEntry received"]
    
    VALIDATE["validate_exec()<br/>Input validation"]
    PREPARE["Prepare execution context<br/>- Block instance<br/>- Credentials<br/>- Extra kwargs"]
    
    ACQUIRE["Acquire credentials lock<br/>creds_manager.acquire()"]
    EXECUTE["Block.execute()<br/>async generator"]
    PROCESS["Process outputs<br/>- Store to DB<br/>- Enqueue next nodes"]
    RELEASE["Release credentials lock"]
    
    ERROR["Handle execution error<br/>- Log error<br/>- Update status"]
    COMPLETE["Update execution stats<br/>- Timing info<br/>- Cost tracking"]
    
    START --> VALIDATE
    VALIDATE --> PREPARE
    PREPARE --> ACQUIRE
    ACQUIRE --> EXECUTE
    EXECUTE --> PROCESS
    PROCESS --> RELEASE
    RELEASE --> COMPLETE
    
    VALIDATE -->|"Validation fails"| ERROR
    EXECUTE -->|"Exception thrown"| ERROR
    ERROR --> RELEASE
```

Sources: [autogpt_platform/backend/backend/executor/manager.py:133-243](), [autogpt_platform/backend/backend/executor/manager.py:463-511]()

### Node Dependency Resolution

The system handles complex node dependencies and ensures proper execution ordering:

```mermaid
graph TB
    subgraph "Input Resolution"
        STATIC["Static Links<br/>(is_static=true)"]
        DYNAMIC["Dynamic Links<br/>(is_static=false)"]
        DEFAULTS["Node Default Values<br/>(input_default)"]
        OVERRIDES["Input Masks<br/>(nodes_input_masks)"]
    end
    
    subgraph "Execution Coordination"
        VALIDATE["validate_exec()<br/>Check required inputs"]
        INCOMPLETE["INCOMPLETE status<br/>Wait for inputs"]
        QUEUED["QUEUED status<br/>Ready for execution"]
    end
    
    subgraph "Next Node Processing"
        OUTPUT["Node Output Generated"]
        PARSE["parse_execution_output()"]
        ENQUEUE["_enqueue_next_nodes()"]
        REGISTER["_register_next_executions()"]
    end
    
    STATIC --> VALIDATE
    DYNAMIC --> VALIDATE
    DEFAULTS --> VALIDATE
    OVERRIDES --> VALIDATE
    
    VALIDATE -->|"Missing inputs"| INCOMPLETE
    VALIDATE -->|"All inputs ready"| QUEUED
    
    OUTPUT --> PARSE
    PARSE --> ENQUEUE
    ENQUEUE --> REGISTER
    REGISTER --> INCOMPLETE
    REGISTER --> QUEUED
```

Sources: [autogpt_platform/backend/backend/executor/manager.py:245-397](), [autogpt_platform/backend/backend/executor/utils.py:254-290]()

## Data Models

### Execution Status Management

The system tracks execution progress through well-defined status transitions:

| Status | Description | Transitions To |
|--------|-------------|----------------|
| `INCOMPLETE` | Node waiting for input data | `QUEUED` |
| `QUEUED` | Ready for execution, in queue | `RUNNING` |
| `RUNNING` | Currently executing | `COMPLETED`, `FAILED` |
| `COMPLETED` | Successfully finished | N/A |
| `FAILED` | Execution failed with error | N/A |
| `TERMINATED` | Cancelled by user/system | N/A |
| `REVIEW` | Execution paused for human review | `QUEUED`, `RUNNING`, `TERMINATED`, `FAILED` |

Sources: [autogpt_platform/backend/backend/data/execution.py:69-70](), [autogpt_platform/frontend/src/lib/autogpt-server-api/types.ts:375-381](), [autogpt_platform/backend/backend/data/execution.py:134-165]()

### Core Data Structures

```mermaid
classDiagram
    class GraphExecutionEntry {
        +user_id: str
        +graph_id: str
        +graph_version: int
        +graph_exec_id: str
        +nodes_input_masks: dict
    }
    
    class NodeExecutionEntry {
        +user_id: str
        +graph_exec_id: str
        +node_exec_id: str
        +node_id: str
        +block_id: str
        +inputs: BlockInput
    }
    
    class ExecutionOutputEntry {
        +node: Node
        +node_exec_id: str
        +data: BlockData
    }
    
    class NodeExecutionStats {
        +walltime: float
        +cputime: float
        +input_size: int
        +output_size: int
        +error: str | None
    }
    
    GraphExecutionEntry --> NodeExecutionEntry
    NodeExecutionEntry --> ExecutionOutputEntry
    NodeExecutionEntry --> NodeExecutionStats
```

Sources: [autogpt_platform/backend/backend/executor/utils.py:129-178](), [autogpt_platform/backend/backend/data/execution.py:278-333](), [autogpt_platform/backend/backend/data/model.py:454-478]()

## Resource Management

### Cost Tracking and Credits

The execution system integrates with the credit system to track and bill for resource usage:

```mermaid
graph TB
    subgraph "Usage Tracking"
        BLOCK_COST["Block Usage Cost<br/>block_usage_cost()"]
        EXEC_COST["Execution Cost<br/>execution_usage_cost()"]
        METADATA["UsageTransactionMetadata<br/>- graph_exec_id<br/>- node_exec_id<br/>- block details"]
    end
    
    subgraph "Credit Operations"
        CHECK["Check Credits<br/>get_credits()"]
        SPEND["Spend Credits<br/>spend_credits()"]
        INSUFFICIENT["InsufficientBalanceError"]
    end
    
    subgraph "Execution Flow"
        CHARGE["_charge_usage()"]
        EXECUTE["Execute Node"]
        UPDATE["Update Stats"]
    end
    
    CHARGE --> CHECK
    CHECK -->|"Balance > 0"| SPEND
    CHECK -->|"Balance <= 0"| INSUFFICIENT
    
    SPEND --> BLOCK_COST
    SPEND --> EXEC_COST
    SPEND --> METADATA
    
    SPEND --> EXECUTE
    EXECUTE --> UPDATE
```

Sources: [autogpt_platform/backend/backend/executor/manager.py:594-642](), [autogpt_platform/backend/backend/executor/utils.py:502-526](), [autogpt_platform/backend/backend/data/credit.py:49-58]()

### Credentials Management

The system provides secure credential management for external service integrations:

```mermaid
graph LR
    subgraph "Credential Acquisition"
        NODE["Node Execution"]
        FIELDS["Credential Fields<br/>input_schema.get_credentials_fields()"]
        ACQUIRE["creds_manager.acquire()<br/>(with lock)"]
        LOCK["Redis Lock<br/>Prevents concurrent use"]
    end
    
    subgraph "Execution Context"
        KWARGS["Extra Execution Kwargs<br/>field_name: credentials"]
        EXECUTE["block.execute(**kwargs)"]
        APIS["External API Calls"]
    end
    
    subgraph "Cleanup"
        RELEASE["creds_lock.release()"]
        FINALLY["Finally block<br/>Ensures cleanup"]
    end
    
    NODE --> FIELDS
    FIELDS --> ACQUIRE
    ACQUIRE --> LOCK
    LOCK --> KWARGS
    KWARGS --> EXECUTE
    EXECUTE --> APIS
    APIS --> RELEASE
    EXECUTE --> FINALLY
    FINALLY --> RELEASE
```

Sources: [autogpt_platform/backend/backend/executor/manager.py:200-235](), [autogpt_platform/backend/backend/integrations/creds_manager.py:1-492]()

## Error Handling and Monitoring

### Error Recovery and Status Updates

The system provides comprehensive error handling with proper state management:

- **Validation Errors**: Input validation failures are logged and marked as errors
- **Execution Errors**: Block execution exceptions are caught and recorded
- **Credit Errors**: Insufficient balance errors halt execution gracefully  
- **Infrastructure Errors**: Network/service failures are retried with exponential backoff

Sources: [autogpt_platform/backend/backend/executor/manager.py:186-193](), [autogpt_platform/backend/backend/executor/manager.py:609-612](), [autogpt_platform/backend/backend/util/exceptions.py:77-94]()

### Real-time Monitoring

Execution progress is broadcast in real-time through Redis event bus:

```mermaid
graph LR
    subgraph "Event Generation"
        NODE_UPDATE["Node Status Update"]
        GRAPH_UPDATE["Graph Status Update"]
        STATS_UPDATE["Execution Stats Update"]
    end
    
    subgraph "Event Broadcasting"
        REDIS_BUS["AsyncRedisEventBus"]
        WS_SERVER["WebSocket Server"]
        CLIENT["Frontend Client"]
    end
    
    NODE_UPDATE --> REDIS_BUS
    GRAPH_UPDATE --> REDIS_BUS
    STATS_UPDATE --> REDIS_BUS
    
    REDIS_BUS --> WS_SERVER
    WS_SERVER --> CLIENT
```

The system also exposes Prometheus metrics for operational monitoring:
- `execution_manager_active_runs` - Number of active graph executions
- `execution_manager_pool_size` - Maximum number of graph workers
- `execution_manager_utilization_ratio` - Worker utilization percentage

Sources: [autogpt_platform/backend/backend/executor/manager.py:89-98](), [autogpt_platform/backend/backend/data/execution.py:58-59](), [autogpt_platform/backend/backend/executor/utils.py:186-225]()

---

