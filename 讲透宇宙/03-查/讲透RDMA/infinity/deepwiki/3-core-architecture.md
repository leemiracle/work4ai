<!-- source: DeepWiki mcp.deepwiki.com · repo claudebarthels/infinity · page 3 Core Architecture · fetched 2026-11-11 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/infinity/core/Configuration.h](src/infinity/core/Configuration.h)
- [src/infinity/core/Context.cpp](src/infinity/core/Context.cpp)
- [src/infinity/queues/QueuePair.cpp](src/infinity/queues/QueuePair.cpp)
- [src/infinity/queues/QueuePair.h](src/infinity/queues/QueuePair.h)

</details>



This document explains the fundamental architecture and design principles of the Infinity RDMA library. It covers the core components that provide the foundation for all RDMA operations, including resource management, communication endpoints, and the abstraction layer over InfiniBand Verbs.

For specific details about memory management, see [Memory Management](#4). For connection establishment procedures, see [Connection Management](#3.3). For detailed API documentation, see [API Reference](#7).

## Architecture Overview

The Infinity library follows a layered architecture that abstracts InfiniBand Verbs complexity while maintaining high performance. The core consists of three primary components working together to provide RDMA functionality.

```mermaid
graph TB
    subgraph "Application Layer"
        App["Application Code"]
    end
    
    subgraph "Infinity Core Architecture"
        Context["Context<br/>Resource Manager"]
        Config["Configuration<br/>System Constants"]
        
        subgraph "Communication Layer"
            QP["QueuePair<br/>RDMA Operations"]
            OpFlags["OperationFlags<br/>Operation Control"]
            QPFactory["QueuePairFactory<br/>Connection Management"]
        end
        
        subgraph "Request Management"
            RequestToken["RequestToken<br/>Async Tracking"]
        end
    end
    
    subgraph "InfiniBand Verbs Layer"
        IBVContext["ibv_context"]
        IBVProtectionDomain["ibv_pd"]
        IBVQueuePair["ibv_qp"]
        IBVCompletionQueue["ibv_cq"]
        IBVSharedReceiveQueue["ibv_srq"]
    end
    
    App --> Context
    App --> QP
    Context --> Config
    Context --> QP
    Context --> QPFactory
    Context --> RequestToken
    QP --> OpFlags
    
    Context --> IBVContext
    Context --> IBVProtectionDomain
    Context --> IBVCompletionQueue
    Context --> IBVSharedReceiveQueue
    QP --> IBVQueuePair
```

Sources: [src/infinity/core/Context.cpp:1-225](), [src/infinity/queues/QueuePair.cpp:1-590](), [src/infinity/core/Configuration.h:1-55]()

## Core Components

The core architecture consists of several key components that work together to provide RDMA functionality:

| Component | Class | Purpose | Key Methods |
|-----------|-------|---------|-------------|
| Resource Manager | `infinity::core::Context` | Manages InfiniBand resources and device context | `postReceiveBuffer()`, `receive()`, `pollSendCompletionQueue()` |
| Communication Endpoint | `infinity::queues::QueuePair` | Handles RDMA operations and queue pair management | `send()`, `write()`, `read()`, `activate()` |
| Configuration | `infinity::core::Configuration` | Defines system constants and limits | Static constants for queue lengths and limits |
| Operation Control | `infinity::queues::OperationFlags` | Controls operation behavior flags | `ibvFlags()` |

Sources: [src/infinity/core/Context.cpp:31-74](), [src/infinity/queues/QueuePair.cpp:38-75](), [src/infinity/core/Configuration.h:17-49]()

## Context Resource Management

The `Context` class serves as the central resource manager, initializing and managing all InfiniBand resources. It abstracts the complexity of InfiniBand device management and provides a unified interface for resource allocation.

```mermaid
graph TB
    subgraph "Context Initialization Flow"
        DeviceList["ibv_get_device_list()"]
        OpenDevice["ibv_open_device()"]
        ProtectionDomain["ibv_alloc_pd()"]
        CompletionQueues["ibv_create_cq()"]
        SharedReceiveQueue["ibv_create_srq()"]
        DefaultObjects["Default RequestToken & Atomic"]
    end
    
    subgraph "Context Resources"
        IBVContext["ibvContext<br/>Device Context"]
        IBVProtectionDomain["ibvProtectionDomain<br/>Memory Protection"]
        IBVSendCQ["ibvSendCompletionQueue<br/>Send Completions"]
        IBVRecvCQ["ibvReceiveCompletionQueue<br/>Receive Completions"]
        IBVSRQ["ibvSharedReceiveQueue<br/>Shared Receives"]
        QPMap["queuePairMap<br/>QP Registry"]
    end
    
    DeviceList --> OpenDevice
    OpenDevice --> ProtectionDomain
    ProtectionDomain --> CompletionQueues
    CompletionQueues --> SharedReceiveQueue
    SharedReceiveQueue --> DefaultObjects
    
    OpenDevice --> IBVContext
    ProtectionDomain --> IBVProtectionDomain
    CompletionQueues --> IBVSendCQ
    CompletionQueues --> IBVRecvCQ
    SharedReceiveQueue --> IBVSRQ
    DefaultObjects --> QPMap
```

The Context constructor initializes InfiniBand resources in a specific order, ensuring proper dependency management between components.

Sources: [src/infinity/core/Context.cpp:31-74](), [src/infinity/core/Context.h:1-100]()

## QueuePair Architecture

The `QueuePair` class implements the primary communication interface, providing methods for all RDMA operations. It maintains state for connection management and operation execution.

```mermaid
graph TB
    subgraph "QueuePair Lifecycle"
        Constructor["QueuePair(context)<br/>Create IBV QP"]
        InitState["IBV_QPS_INIT<br/>Set port and access flags"]
        RTRState["IBV_QPS_RTR<br/>Ready to Receive"]
        RTSState["IBV_QPS_RTS<br/>Ready to Send"]
        ActiveQP["Active QueuePair<br/>Ready for operations"]
    end
    
    subgraph "Operation Categories"
        TwoSided["Two-sided Operations<br/>send(), sendWithImmediate()"]
        OneSided["One-sided Operations<br/>write(), read()"]
        Atomic["Atomic Operations<br/>compareAndSwap(), fetchAndAdd()"]
        Complex["Complex Operations<br/>multiWrite(), multiWriteWithImmediate()"]
    end
    
    subgraph "InfiniBand Integration"
        IBVWorkRequest["ibv_send_wr<br/>Work Request"]
        IBVScatterGather["ibv_sge<br/>Scatter-Gather Element"]
        IBVPostSend["ibv_post_send()<br/>Submit Operation"]
    end
    
    Constructor --> InitState
    InitState --> RTRState
    RTRState --> RTSState
    RTSState --> ActiveQP
    
    ActiveQP --> TwoSided
    ActiveQP --> OneSided
    ActiveQP --> Atomic
    ActiveQP --> Complex
    
    TwoSided --> IBVWorkRequest
    OneSided --> IBVWorkRequest
    Atomic --> IBVWorkRequest
    Complex --> IBVWorkRequest
    
    IBVWorkRequest --> IBVScatterGather
    IBVScatterGather --> IBVPostSend
```

The QueuePair follows the InfiniBand state machine, transitioning through INIT, RTR (Ready to Receive), and RTS (Ready to Send) states before becoming operational.

Sources: [src/infinity/queues/QueuePair.cpp:38-123](), [src/infinity/queues/QueuePair.h:44-153]()

## Operation Flow Architecture

RDMA operations follow a consistent pattern from initiation to completion, involving work request creation, submission, and completion handling.

```mermaid
sequenceDiagram
    participant App as "Application"
    participant QP as "QueuePair"
    participant RT as "RequestToken"
    participant IBV as "InfiniBand Verbs"
    participant CQ as "Completion Queue"
    participant Context as "Context"
    
    App->>QP: "write(buffer, destination, requestToken)"
    QP->>RT: "reset(), setRegion(buffer)"
    
    Note over QP,IBV: Work Request Creation
    QP->>QP: "Create ibv_sge structure"
    QP->>QP: "Create ibv_send_wr structure"
    QP->>QP: "Set operation flags"
    
    QP->>IBV: "ibv_post_send(ibvQueuePair, &workRequest)"
    IBV-->>QP: "Return status"
    
    Note over IBV,Context: Asynchronous Completion
    IBV->>CQ: "Post completion event"
    Context->>CQ: "pollSendCompletionQueue()"
    CQ-->>Context: "ibv_wc completion"
    Context->>RT: "setCompleted(success)"
    
    App->>RT: "waitUntilCompleted()"
    RT-->>App: "Operation result"
```

All operations follow this pattern, with variations in the work request structure based on the operation type (send, write, read, atomic).

Sources: [src/infinity/queues/QueuePair.cpp:241-282](), [src/infinity/core/Context.cpp:169-189]()

## Configuration and Constants

The `Configuration` class defines system-wide constants that control resource allocation and operational limits throughout the library.

```mermaid
graph LR
    subgraph "Queue Configuration"
        SendCQLen["SEND_COMPLETION_QUEUE_LENGTH<br/>16351"]
        RecvCQLen["RECV_COMPLETION_QUEUE_LENGTH<br/>16351"]
        SRQLen["SHARED_RECV_QUEUE_LENGTH<br/>16351"]
        MaxOutstanding["MAX_NUMBER_OF_OUTSTANDING_REQUESTS<br/>16351"]
        MaxSGE["MAX_NUMBER_OF_SGE_ELEMENTS<br/>1"]
    end
    
    subgraph "System Configuration"
        PageSize["PAGE_SIZE<br/>4096"]
        UserDataSize["MAX_CONNECTION_USER_DATA_SIZE<br/>1024"]
        DefaultDevice["DEFAULT_IB_DEVICE<br/>ib0"]
    end
    
    subgraph "Usage in Code"
        ContextInit["Context initialization"]
        QueuePairInit["QueuePair creation"]
        MemoryAlloc["Memory allocation"]
        ConnectionSetup["Connection setup"]
    end
    
    SendCQLen --> ContextInit
    RecvCQLen --> ContextInit
    SRQLen --> ContextInit
    MaxOutstanding --> QueuePairInit
    MaxSGE --> QueuePairInit
    PageSize --> MemoryAlloc
    UserDataSize --> ConnectionSetup
    DefaultDevice --> ContextInit
```

These constants ensure consistent resource allocation and provide tuneable parameters for different deployment scenarios.

Sources: [src/infinity/core/Configuration.h:17-49]()

## Component Interactions

The core components interact through well-defined interfaces, with the Context serving as the central coordinator for all InfiniBand resources.

```mermaid
graph TB
    subgraph "Initialization Phase"
        AppInit["Application creates Context"]
        ContextInit["Context initializes IBV resources"]
        QPCreate["QueuePair creation via Context"]
        QPRegister["Context registers QueuePair"]
    end
    
    subgraph "Operation Phase"
        BufferPost["Context posts receive buffers"]
        OpExecute["QueuePair executes operations"]
        CompletionPoll["Context polls completion queues"]
        TokenUpdate["RequestToken completion updates"]
    end
    
    subgraph "Cleanup Phase"
        QPDestroy["QueuePair destruction"]
        ContextDestroy["Context cleanup"]
        IBVCleanup["IBV resource deallocation"]
    end
    
    AppInit --> ContextInit
    ContextInit --> QPCreate
    QPCreate --> QPRegister
    QPRegister --> BufferPost
    BufferPost --> OpExecute
    OpExecute --> CompletionPoll
    CompletionPoll --> TokenUpdate
    TokenUpdate --> QPDestroy
    QPDestroy --> ContextDestroy
    ContextDestroy --> IBVCleanup
```

This interaction pattern ensures proper resource management and maintains the abstraction layer while providing high-performance RDMA operations.

Sources: [src/infinity/core/Context.cpp:31-100](), [src/infinity/queues/QueuePair.cpp:38-87](), [src/infinity/core/Context.cpp:191-193]()

---

