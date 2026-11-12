<!-- source: DeepWiki mcp.deepwiki.com · repo browser-use/bubus · page 1 Overview · fetched 2026-10-30 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [bubus/__init__.py](bubus/__init__.py)

</details>



The `bubus` library is a production-ready, Pydantic-powered asynchronous event bus system for Python applications. It provides type-safe event processing with FIFO ordering, automatic parent-child event tracking, multi-bus communication, and advanced concurrency controls.

For detailed implementation specifics, see [Core Architecture](#2). For complete API documentation, see [API Reference](#3). For advanced usage patterns and debugging capabilities, see [Advanced Features](#4).

## Purpose and Core Value Proposition

`bubus` enables event-driven architectures with strong type safety and predictable execution semantics. The system combines Pydantic's validation capabilities with async Python patterns to deliver reliable event processing for both simple pub-sub patterns and complex distributed event workflows.

Key benefits include automatic event metadata management, built-in concurrency controls via the `@retry` decorator, write-ahead logging for durability, and sophisticated debugging tools for event tree visualization.

### Core Architecture Components

```mermaid
graph TB
    subgraph "bubus.service"
        EventBus["EventBus<br/>dispatch(), on(), expect()"]
        EventBusRunLoop["EventBus._run_loop()<br/>Main processing task"]
        EventBusStop["EventBus.stop()<br/>Graceful shutdown"]
    end
    
    subgraph "bubus.models"
        BaseEvent["BaseEvent[T]<br/>Generic event model"]
        BaseEventMethods["event_result()<br/>event_results_list()<br/>event_results_flat_dict()"]
        EventResult["EventResult<br/>Handler execution state"]
        EventHandler["EventHandler<br/>Callable wrapper"]
    end
    
    subgraph "bubus.helpers"
        RetryDecorator["@retry<br/>Concurrency & reliability"]
        SemaphoreSystem["Semaphore scopes<br/>global|class|self|multiprocess"]
    end
    
    subgraph "Internal Infrastructure"
        CleanShutdownQueue["CleanShutdownQueue<br/>FIFO event ordering"]
        ReentrantLock["ReentrantLock<br/>Thread-safe processing"]
        WriteAheadLog["Write-Ahead Log<br/>JSONL persistence"]
    end
    
    EventBus --> BaseEvent
    EventBus --> EventResult
    EventBus --> EventHandler
    EventBus --> CleanShutdownQueue
    EventBus --> ReentrantLock
    EventBus --> WriteAheadLog
    
    BaseEvent --> BaseEventMethods
    BaseEvent --> EventResult
    
    RetryDecorator --> SemaphoreSystem
    RetryDecorator --> EventHandler
    
```

Sources: [bubus/__init__.py:1-14](), [README.md:507-513](), [README.md:592-622]()

## Core Event Processing Model

The system operates on a publish-subscribe pattern where `EventBus` instances manage event dispatch and handler execution. Events are defined as Pydantic models inheriting from `BaseEvent`, providing type safety and validation. Each event dispatch creates `EventResult` objects that track handler execution outcomes.

### Key Components Overview

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| `EventBus` | Central event broker | FIFO processing, parallel handlers, inter-bus forwarding |
| `BaseEvent` | Event data model | Pydantic validation, automatic metadata, parent-child tracking |
| `EventResult` | Handler execution tracker | Async result handling, error tracking, timeout management |
| `CleanShutdownQueue` | Event ordering | FIFO guarantees, graceful shutdown |
| `ReentrantLock` | Concurrency control | Thread-safe processing, context tracking |

Sources: [README.md:499-589](), [README.md:592-779]()

### Event Processing Flow

```mermaid
sequenceDiagram
    participant Client
    participant EventBus
    participant BaseEvent
    participant EventResult
    participant EventHandler
    
    Client->>EventBus: "bus.dispatch(MyEvent())"
    EventBus->>BaseEvent: "Initialize event_id, event_type, event_created_at"
    EventBus-->>Client: "Return pending BaseEvent instance"
    
    EventBus->>EventBus: "Add to FIFO processing queue"
    EventBus->>EventHandler: "Execute registered handlers via bus.on()"
    
    EventHandler->>EventHandler: "Process event logic"
    Note over EventHandler: "Can call event.event_bus.dispatch(child)"
    
    EventHandler-->>EventResult: "Store handler return value"
    EventResult->>BaseEvent: "Update event.event_results dict"
    
    BaseEvent->>BaseEvent: "Set event_status = 'completed'"
    
    Note over Client: "await event returns completed BaseEvent"
    Client->>BaseEvent: "await event.event_result()"
```

Sources: [README.md:21-42](), [README.md:546-553](), [README.md:643-670]()

## Core Capabilities

| Feature | Description | Key Components |
|---------|-------------|----------------|
| **Type-Safe Events** | Pydantic models with `BaseEvent[T]` generic typing | `BaseEvent`, automatic validation |
| **Handler Registration** | Multiple registration patterns with wildcard support | `bus.on(EventClass, handler)`, `bus.on('*', handler)` |
| **FIFO Processing** | Strict event ordering with async handler support | `CleanShutdownQueue`, sequential execution |
| **Event Hierarchies** | Automatic parent-child tracking for nested events | `event_parent_id`, `event_children` |
| **Multi-Bus Forwarding** | Event routing between `EventBus` instances | `event_path`, loop prevention |
| **Result Aggregation** | Multiple handlers per event with result collection | `event_results_list()`, `event_results_flat_dict()` |
| **Concurrency Control** | Built-in retry logic and semaphore management | `@retry` decorator, semaphore scopes |
| **Persistence** | Write-ahead logging to JSONL files | `wal_path` parameter |

### Multi-Bus Event Forwarding

```mermaid
graph LR
    subgraph "Application Architecture"
        MainBus["EventBus(name='MainBus')"]
        AuthBus["EventBus(name='AuthBus')"]
        DataBus["EventBus(name='DataBus')"]
    end
    
    subgraph "Event Flow"
        LoginEvent["LoginEvent<br/>dispatched to MainBus"]
        EventPath["event.event_path<br/>['MainBus', 'AuthBus', 'DataBus']"]
    end
    
    MainBus -->|"main_bus.on('*', auth_bus.dispatch)"| AuthBus
    AuthBus -->|"auth_bus.on('*', data_bus.dispatch)"| DataBus
    DataBus -.->|"Loop prevention via event_path"| MainBus
    
    LoginEvent --> EventPath
    
```

Sources: [README.md:145-165](), [README.md:151-164]()

### Built-in Concurrency and Reliability

The `@retry` decorator provides automatic retry logic with semaphore-based concurrency control:

```python
from bubus.helpers import retry

@retry(
    retries=3,
    wait=2,
    semaphore_limit=5,
    semaphore_scope='global'
)
async def reliable_handler(event: MyEvent):
    # Automatic retry on failures
    # Maximum 5 concurrent executions
    return await external_api_call()
```

Sources: [README.md:822-924](), [README.md:838-853]()

## Integration Architecture

```mermaid
graph LR
    subgraph "Application Layer"
        UserCode["User Application Code"]
        EventModels["Custom BaseEvent subclasses"]
        EventHandlers["Handler Functions"]
    end
    
    subgraph "bubus Framework"
        EventBusAPI["EventBus.dispatch()"]
        EventBusCore["EventBus._run_loop()"]
        EventValidation["BaseEvent validation"]
        ResultTracking["EventResult management"]
    end
    
    subgraph "Python Runtime"
        AsyncIO["asyncio event loop"]
        Threading["threading.Lock"]
        ContextVars["contextvars"]
    end
    
    subgraph "External Dependencies"
        Pydantic["pydantic validation"]
        AnyIO["anyio async framework"]
        AIOFiles["aiofiles persistence"]
        UUID7["uuid7 ID generation"]
    end
    
    UserCode --> EventModels
    UserCode --> EventHandlers
    UserCode --> EventBusAPI
    
    EventModels --> EventValidation
    EventHandlers --> EventBusCore
    EventBusAPI --> EventBusCore
    
    EventValidation --> Pydantic
    EventBusCore --> AsyncIO
    EventBusCore --> Threading
    EventBusCore --> ContextVars
    ResultTracking --> AnyIO
    
    EventBusCore --> AIOFiles
    EventValidation --> UUID7
    
```

Sources: [README.md:17-42](), [README.md:70-87]()

The `bubus` system provides a comprehensive foundation for building reactive applications with strong type safety, flexible concurrency models, and sophisticated event relationship tracking. Its modular architecture allows for both simple pub-sub patterns and complex event-driven workflows with inter-service communication capabilities.

---

