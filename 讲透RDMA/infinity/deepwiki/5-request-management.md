<!-- source: DeepWiki mcp.deepwiki.com · repo claudebarthels/infinity · page 5 Request Management · fetched 2026-11-11 -->

# Request Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/infinity/requests/RequestToken.cpp](src/infinity/requests/RequestToken.cpp)
- [src/infinity/requests/RequestToken.h](src/infinity/requests/RequestToken.h)

</details>



## Purpose and Scope

The Request Management subsystem provides asynchronous operation tracking for RDMA operations in the Infinity library. It centers around the `RequestToken` class, which serves as a handle for tracking the completion status and results of non-blocking RDMA operations such as read, write, send, and atomic operations.

For information about the RDMA operations that generate these tokens, see [QueuePair Operations](#3.2). For details on the memory regions associated with requests, see [Memory Management](#4).

## RequestToken Class Overview

The `RequestToken` class provides a unified interface for tracking asynchronous RDMA operations. Each token represents a single pending operation and maintains state information about its completion status, success/failure, and associated data.

### Core Components

```mermaid
graph TB
    subgraph "RequestToken Structure"
        RT[RequestToken]
        Context["context*<br/>infinity::core::Context"]
        Region["region*<br/>infinity::memory::Region"]
        
        subgraph "Completion State"
            Completed["completed<br/>std::atomic<bool>"]
            Success["success<br/>std::atomic<bool>"]
        end
        
        subgraph "User Data"
            UserData["userData*<br/>void*"]
            UserDataSize["userDataSize<br/>uint32_t"]
            UserDataValid["userDataValid<br/>bool"]
        end
        
        subgraph "Immediate Value"
            ImmediateValue["immediateValue<br/>uint32_t"]
            ImmediateValueValid["immediateValueValid<br/>bool"]
        end
    end
    
    RT --> Context
    RT --> Region
    RT --> Completed
    RT --> Success
    RT --> UserData
    RT --> UserDataSize
    RT --> UserDataValid
    RT --> ImmediateValue
    RT --> ImmediateValueValid
```

**Sources:** [src/infinity/requests/RequestToken.h:21-62]()

### Key Methods

| Method | Purpose | Blocking |
|--------|---------|----------|
| `setCompleted(bool success)` | Mark operation as completed | No |
| `checkIfCompleted()` | Check completion status | No |
| `waitUntilCompleted()` | Block until operation completes | Yes |
| `wasSuccessful()` | Get operation result | No |
| `reset()` | Reset token for reuse | No |

**Sources:** [src/infinity/requests/RequestToken.h:32-36](), [src/infinity/requests/RequestToken.cpp:26-59]()

## Asynchronous Operation Tracking

The `RequestToken` uses atomic variables to provide thread-safe tracking of operation completion. The completion polling mechanism integrates with the InfiniBand completion queue system through the `Context` class.

### Completion Flow

```mermaid
sequenceDiagram
    participant App as "Application"
    participant QP as "QueuePair"
    participant RT as "RequestToken"
    participant Ctx as "Context"
    participant CQ as "Completion Queue"
    
    App->>QP: "read/write/send operation"
    QP->>RT: "new RequestToken(context)"
    QP->>RT: "setRegion(region)"
    QP->>Ctx: "Post operation to IBV"
    Ctx-->>CQ: "Operation queued"
    QP-->>App: "Return RequestToken"
    
    Note over App,CQ: "Asynchronous completion"
    CQ-->>Ctx: "Completion event"
    Ctx->>RT: "setCompleted(success)"
    
    Note over App,CQ: "Application polling"
    App->>RT: "checkIfCompleted()"
    RT->>Ctx: "pollSendCompletionQueue()"
    Ctx-->>RT: "Process completions"
    RT-->>App: "Completion status"
```

**Sources:** [src/infinity/requests/RequestToken.cpp:31-44]()

### Completion Checking Methods

The `RequestToken` provides two approaches for checking completion:

1. **Non-blocking Check**: `checkIfCompleted()` polls the completion queue once and returns the current status
2. **Blocking Wait**: `waitUntilCompleted()` continuously polls until the operation completes

```mermaid
graph TD
    subgraph "checkIfCompleted() Flow"
        Check["checkIfCompleted()"]
        LoadCompleted["completed.load()"]
        PollCQ["context->pollSendCompletionQueue()"]
        LoadAgain["completed.load()"]
        ReturnStatus["return status"]
    end
    
    Check --> LoadCompleted
    LoadCompleted -->|"false"| PollCQ
    LoadCompleted -->|"true"| ReturnStatus
    PollCQ --> LoadAgain
    LoadAgain --> ReturnStatus
    
    subgraph "waitUntilCompleted() Flow"
        Wait["waitUntilCompleted()"]
        Loop["while (!completed.load())"]
        PollCQ2["context->pollSendCompletionQueue()"]
        Complete["return"]
    end
    
    Wait --> Loop
    Loop -->|"not completed"| PollCQ2
    PollCQ2 --> Loop
    Loop -->|"completed"| Complete
```

**Sources:** [src/infinity/requests/RequestToken.cpp:31-44]()

## Data Management Features

The `RequestToken` supports additional data management features for enhanced operation tracking and result handling.

### User Data Association

Applications can associate arbitrary data with requests using the user data mechanism:

| Method | Purpose |
|--------|---------|
| `setUserData(void* userData, uint32_t userDataSize)` | Attach user data to request |
| `getUserData()` | Retrieve user data pointer |
| `hasUserData()` | Check if user data is present |
| `getUserDataSize()` | Get size of user data |

**Sources:** [src/infinity/requests/RequestToken.cpp:69-85]()

### Immediate Value Support

For operations that support immediate values (such as RDMA send with immediate), the token can store and retrieve these values:

| Method | Purpose |
|--------|---------|
| `setImmediateValue(uint32_t immediateValue)` | Store immediate value |
| `getImmediateValue()` | Retrieve immediate value |
| `hasImmediateValue()` | Check if immediate value is present |

**Sources:** [src/infinity/requests/RequestToken.cpp:87-98]()

### Memory Region Association

Each token can be associated with a specific memory region involved in the operation:

```mermaid
graph LR
    subgraph "Region Association"
        RT["RequestToken"]
        Region["infinity::memory::Region*"]
        SetRegion["setRegion(region)"]
        GetRegion["getRegion()"]
    end
    
    RT --> Region
    SetRegion --> Region
    Region --> GetRegion
```

**Sources:** [src/infinity/requests/RequestToken.cpp:61-67]()

## Integration with Core Components

The `RequestToken` integrates closely with other Infinity components to provide comprehensive request management.

### Component Integration

```mermaid
graph TB
    subgraph "Request Management Integration"
        QP["QueuePair<br/>RDMA Operations"]
        RT["RequestToken<br/>Async Tracking"]
        Ctx["Context<br/>Completion Polling"]
        Region["Region<br/>Memory Management"]
        
        subgraph "InfiniBand Layer"
            IBV["ibv_post_send<br/>ibv_post_recv"]
            CQ["ibv_cq<br/>Completion Queue"]
        end
    end
    
    QP --> RT
    RT --> Ctx
    RT --> Region
    Ctx --> CQ
    QP --> IBV
    IBV --> CQ
```

**Sources:** [src/infinity/requests/RequestToken.h:15-16](), [src/infinity/requests/RequestToken.cpp:14-24]()

### Token Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Created: "new RequestToken(context)"
    Created --> Configured: "setRegion(), setUserData()"
    Configured --> Posted: "QueuePair operation"
    Posted --> Polling: "checkIfCompleted()"
    Polling --> Completed: "setCompleted(success)"
    Polling --> Polling: "continue polling"
    Completed --> Reset: "reset()"
    Reset --> Created: "token reuse"
    Completed --> [*]: "token destruction"
```

**Sources:** [src/infinity/requests/RequestToken.cpp:50-59]()

## Thread Safety

The `RequestToken` implementation uses atomic operations for thread-safe completion status tracking. The `completed` and `success` flags are implemented as `std::atomic<bool>` to ensure safe concurrent access between the completion processing thread and application threads.

**Sources:** [src/infinity/requests/RequestToken.h:52-53]()

---

