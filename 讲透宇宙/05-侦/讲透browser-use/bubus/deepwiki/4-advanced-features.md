<!-- source: DeepWiki mcp.deepwiki.com · repo browser-use/bubus · page 4 Advanced Features · fetched 2026-10-30 -->

# Advanced Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [tests/test_comprehensive_patterns.py](tests/test_comprehensive_patterns.py)

</details>



This document covers the sophisticated capabilities of bubus that go beyond basic event dispatching and handling. These features enable complex event-driven architectures with reliable concurrency control, event persistence, debugging capabilities, and multi-service communication patterns.

For basic EventBus usage and API reference, see [EventBus API](#3.1). For testing patterns specific to advanced features, see [Testing Framework and Patterns](#5.2).

## Event Hierarchy and Parent-Child Relationships

The bubus event system automatically tracks relationships between events when handlers dispatch child events. This creates a tree structure that enables sophisticated debugging and audit trails.

### Parent-Child Event Tracking Architecture

```mermaid
graph TD
    PE[ParentEvent] --> PH["parent_handler()"]
    PH --> CD1["bus.dispatch(ChildEvent1)"]
    PH --> CD2["await bus.dispatch(ChildEvent2)"]
    
    CD1 --> CE1[ChildEvent1]
    CD2 --> CE2[ChildEvent2]
    
    CE1 --> CH1["child_handler_1()"]
    CE2 --> CH2["child_handler_2()"]
    
    CH2 --> CD3["bus.dispatch(GrandchildEvent)"]
    CD3 --> GCE[GrandchildEvent]
    
    PE -.-> |"event_children"| CE1
    PE -.-> |"event_children"| CE2
    CE2 -.-> |"event_children"| GCE
    
    CE1 -.-> |"event_parent_id"| PE
    CE2 -.-> |"event_parent_id"| PE
    GCE -.-> |"event_parent_id"| CE2
```

**Sources:** [README.md:230-265](), [tests/test_comprehensive_patterns.py:47-102]()

### Sync vs Async Child Event Processing

```mermaid
sequenceDiagram
    participant PH as "parent_handler()"
    participant Bus as "EventBus"
    participant Queue as "FIFO Queue"
    
    PH->>Bus: "bus.dispatch(AsyncChildEvent)"
    Bus->>Queue: "enqueue for later"
    Bus-->>PH: "return pending event"
    
    PH->>Bus: "await bus.dispatch(SyncChildEvent)"
    Bus->>Bus: "process immediately (jump queue)"
    Bus-->>PH: "return completed event"
    
    Note over PH: "parent handler completes"
    
    Queue->>Bus: "process AsyncChildEvent"
    Bus->>Bus: "run child handlers"
```

**Sources:** [README.md:208-226](), [tests/test_comprehensive_patterns.py:55-66]()

Child events dispatched with `await` jump the FIFO queue and process immediately, while non-awaited dispatches are queued for later processing. The `event_parent_id` field automatically links children to their parent, and `event_children` provides reverse lookup.

## Multi-Bus Communication and Event Forwarding

Multiple `EventBus` instances can forward events between each other, enabling microservice-style architecture with automatic loop prevention.

### Event Forwarding Implementation

```mermaid
graph LR
    subgraph "MainBus"
        MB[EventBus] --> MH["main_handlers"]
    end
    
    subgraph "AuthBus" 
        AB[EventBus] --> AH["auth_handlers"]
    end
    
    subgraph "DataBus"
        DB[EventBus] --> DH["data_handlers"]
    end
    
    MB --> |"on('*', auth_bus.dispatch)"| AB
    AB --> |"on('*', data_bus.dispatch)"| DB
    DB --> |"on('*', main_bus.dispatch)"| MB
    
    subgraph "Event Metadata"
        EP["event_path: ['MainBus', 'AuthBus', 'DataBus']"]
        LP["Loop Prevention Logic"]
    end
    
    AB -.-> EP
    EP -.-> LP
```

**Sources:** [README.md:145-165](), [tests/test_comprehensive_patterns.py:29-45]()

### Loop Prevention Mechanism

The `event_path` field tracks which buses have already processed an event, preventing infinite forwarding loops:

```mermaid
flowchart TD
    E[Event] --> Check{"bus.name in event.event_path?"}
    Check -->|Yes| Skip["Skip Processing"]
    Check -->|No| Process["Add bus.name to event_path"]
    Process --> Execute["Execute Handlers"]
    Execute --> Forward["Forward to Other Buses"]
```

**Sources:** [README.md:158-164](), [tests/test_comprehensive_patterns.py:76-87]()

Each bus checks if its name is already in `event.event_path` before processing. If found, the event is skipped to prevent loops.

## Type System and Automatic Result Validation

The bubus type system leverages Pydantic for automatic validation of event data and handler return values.

### Generic Event Result Types

```mermaid
classDiagram
    class BaseEvent~T~ {
        +event_result_type: type[T]
        +event_result() → T
        +event_results_list() → list[T]
    }
    
    class ScreenshotEvent {
        +width: int
        +height: int
    }
    
    class ScreenshotResult {
        +image_bytes: bytes
        +error: str
    }
    
    class EventResult~T~ {
        +result: T
        +__await__() → T
        +validate_result()
    }
    
    BaseEvent~T~ <|-- ScreenshotEvent
    ScreenshotEvent --> ScreenshotResult : "BaseEvent[ScreenshotResult]"
    EventResult~T~ --> BaseEvent~T~ : "contained in event_results"
```

**Sources:** [README.md:356-411](), [README.md:602-635]()

### Result Validation Pipeline

```mermaid
flowchart TD
    Handler["Handler Function"] --> Return["return result"]
    Return --> Validate{"TypeAdapter.validate()"}
    Validate -->|Valid| Store["EventResult.result = value"]
    Validate -->|Invalid| Error["raise ValidationError"]
    Store --> Aggregate["BaseEvent.event_results[handler_id]"]
    
    Aggregate --> Access1["await event.event_result()"]
    Aggregate --> Access2["await event.event_results_list()"]
    Aggregate --> Access3["await event.event_results_flat_dict()"]
```

**Sources:** [README.md:377-390](), [README.md:650-763]()

The `TypeAdapter` from Pydantic validates but does not coerce handler return values, ensuring strict type safety.

## Event Debugging and Tree Visualization

The bubus logging system provides comprehensive debugging capabilities for complex event trees and handler execution analysis.

### Event Tree Structure Visualization

```mermaid
graph TD
    subgraph "EventBus.event_history"
        EH["Dict[event_id, BaseEvent]"]
    end
    
    subgraph "Event Tree Logging"
        LET["log_eventbus_tree()"] --> Parse["Parse event_children relationships"]
        Parse --> Build["Build tree structure"]
        Build --> Render["Render ASCII tree"]
    end
    
    subgraph "Handler Analysis"
        TO["Timeout Detection"] --> Status["Handler Status Analysis"]
        Status --> Tree["Handler Execution Tree"]
    end
    
    EH --> LET
    EH --> TO
```

**Sources:** [README.md:267-268](), [tests/test_comprehensive_patterns.py:167-171]()

### Event Status and Timeout Tracking

The system tracks detailed execution metadata for debugging handler issues:

```mermaid
stateDiagram-v2
    [*] --> pending : "event created"
    pending --> started : "first handler begins"
    started --> completed : "all handlers finish"
    started --> timeout : "event_timeout exceeded"
    started --> error : "handler raises exception"
    
    timeout --> [*] : "cleanup"
    error --> [*] : "cleanup"
    completed --> [*] : "cleanup"
```

**Sources:** [README.md:628-631](), [README.md:804-807]()

The `log_eventbus_tree()` function in `bubus.logging` provides visual debugging output showing the complete event hierarchy and handler execution status.

## Concurrency Control and Retry Mechanisms

The `@retry` decorator provides sophisticated concurrency control with semaphores and automatic retry logic for unreliable operations.

### Retry Decorator Architecture

```mermaid
graph TD
    subgraph "Retry Configuration"
        RC["@retry(timeout=5, retries=3, wait=2)"] --> SM["Semaphore Management"]
        RC --> BF["Backoff Factor Calculation"]
    end
    
    subgraph "Semaphore Scopes"
        SM --> Global["semaphore_scope='global'"]
        SM --> Class["semaphore_scope='class'"]
        SM --> Self["semaphore_scope='self'"]
        SM --> Multi["semaphore_scope='multiprocess'"]
    end
    
    subgraph "Execution Flow"
        Acquire["Acquire Semaphore"] --> Execute["Execute Function"]
        Execute --> Success["Success"]
        Execute --> Retry["Retry on Exception"]
        Retry --> Wait["Backoff Wait"]
        Wait --> Execute
        Success --> Release["Release Semaphore"]
        Retry --> Release
    end
    
    RC --> Acquire
```

**Sources:** [README.md:825-924]()

### Semaphore Scope Implementation

```mermaid
flowchart TD
    Call["Function Call"] --> Scope{"semaphore_scope"}
    
    Scope -->|global| GlobalSem["Global semaphore shared across all calls"]
    Scope -->|class| ClassSem["Per-class semaphore shared across instances"]
    Scope -->|self| SelfSem["Per-instance semaphore"]
    Scope -->|multiprocess| MultiSem["Cross-process semaphore"]
    
    GlobalSem --> Limit["Apply semaphore_limit"]
    ClassSem --> Limit
    SelfSem --> Limit
    MultiSem --> Limit
    
    Limit --> Execute["Execute with concurrency control"]
```

**Sources:** [README.md:868-890]()

The retry system supports different semaphore scopes to control concurrency at various levels, from global limits to per-instance restrictions.

## Write-Ahead Logging and Persistence

The WAL system persists completed events to JSONL files for audit trails, debugging, and event replay capabilities.

### WAL Implementation Architecture

```mermaid
sequenceDiagram
    participant Event as "BaseEvent"
    participant Bus as "EventBus"
    participant WAL as "WAL Writer"
    participant File as "events.jsonl"
    
    Bus->>Event: "process handlers"
    Event->>Bus: "event completed"
    Bus->>WAL: "serialize completed event"
    WAL->>File: "append JSON line"
    
    Note over File: "{"event_type": "MyEvent", "timestamp": "...", ...}"
```

**Sources:** [README.md:475-492]()

### Event Serialization Format

The WAL system serializes events using Pydantic's JSON serialization, creating a structured log of all completed events:

| Field | Description | Source |
|-------|-------------|---------|
| `event_type` | Event class name | `BaseEvent.event_type` |
| `event_id` | Unique identifier | `BaseEvent.event_id` |
| `event_created_at` | Creation timestamp | `BaseEvent.event_created_at` |
| `event_completed_at` | Completion timestamp | `BaseEvent.event_completed_at` |
| Custom fields | Event-specific data | Subclass fields |

**Sources:** [README.md:488-491](), [README.md:607-622]()

The WAL is enabled by setting `wal_path` when creating an `EventBus` instance: `EventBus(wal_path='./events.jsonl')`.

---

