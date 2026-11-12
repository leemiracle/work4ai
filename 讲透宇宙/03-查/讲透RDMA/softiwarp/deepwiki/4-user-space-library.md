<!-- source: DeepWiki mcp.deepwiki.com · repo zrlio/softiwarp · page 4 User Space Library · fetched 2026-11-11 -->

# User Space Library

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [userlib/src/siw.c](userlib/src/siw.c)
- [userlib/src/siw.h](userlib/src/siw.h)
- [userlib/src/siw_abi.h](userlib/src/siw_abi.h)
- [userlib/src/siw_uverbs.c](userlib/src/siw_uverbs.c)
- [userlib/src/siw_verbs.c](userlib/src/siw_verbs.c)

</details>



## Purpose and Scope

The SoftiWARP user space library (`libsiw`) provides a complete libibverbs-compatible implementation that enables RDMA applications to use the SoftiWARP kernel driver. This library serves as the critical bridge between user applications and the kernel driver, implementing all standard Verbs API operations while providing optimized data paths for high-performance communication.

The library supports two distinct operation modes: standard OFED syscall interface and optimized mapped memory interface. For information about the kernel driver components that this library interfaces with, see [Kernel Driver Components](#3). For details about the user-kernel interface protocols, see [User-Kernel Interface](#5).

## Library Architecture

The libsiw library integrates with the standard libibverbs framework and provides device-specific implementations of all RDMA Verbs operations. The library automatically detects the kernel driver capabilities and selects the optimal operation mode.

### Core Library Structure

```mermaid
graph TB
    subgraph "User Application"
        APP["RDMA Application"]
    end
    
    subgraph "libibverbs Framework"
        IBVERBS["libibverbs Core"]
        DRIVER_API["Driver API"]
    end
    
    subgraph "libsiw Library"
        DEVICE_OPS["siw_device_ops"]
        CONTEXT_OPS["siw_context_ops"]
        VERBS_IMPL["siw_verbs.c"]
        UVERBS_IMPL["siw_uverbs.c"]
        DEVICE_DETECT["siw_driver_init"]
    end
    
    subgraph "Kernel Interface"
        SYSCALLS["System Calls"]
        MMAP["Memory Mapping"]
    end
    
    APP --> IBVERBS
    IBVERBS --> DRIVER_API
    DRIVER_API --> DEVICE_OPS
    DEVICE_OPS --> CONTEXT_OPS
    CONTEXT_OPS --> VERBS_IMPL
    CONTEXT_OPS --> UVERBS_IMPL
    DEVICE_DETECT --> VERBS_IMPL
    
    VERBS_IMPL --> SYSCALLS
    UVERBS_IMPL --> SYSCALLS
    UVERBS_IMPL --> MMAP
```

**Sources:** [userlib/src/siw.c:147-150](), [userlib/src/siw.c:59-81]()

### Device Discovery and Registration

The library registers itself with libibverbs through the `siw_register_driver` constructor function, which enables automatic device discovery when applications initialize libibverbs.

```mermaid
graph LR
    subgraph "Device Discovery Process"
        CONSTRUCTOR["siw_register_driver"]
        INIT["siw_driver_init"]
        SYSFS_CHECK["Sysfs Validation"]
        VERSION_CHECK["Version Check"]
        IF_TYPE_CHECK["Interface Type Check"]
        DEVICE_CREATE["siw_device Creation"]
    end
    
    CONSTRUCTOR --> INIT
    INIT --> SYSFS_CHECK
    SYSFS_CHECK --> VERSION_CHECK
    VERSION_CHECK --> IF_TYPE_CHECK
    IF_TYPE_CHECK --> DEVICE_CREATE
```

**Sources:** [userlib/src/siw.c:211-214](), [userlib/src/siw.c:152-209]()

## Operation Modes

The library supports two distinct operation modes that provide different performance characteristics and kernel interaction patterns.

### OFED Mode vs Mapped Mode

| Aspect | OFED Mode | Mapped Mode |
|--------|-----------|-------------|
| Interface | Standard syscalls via `ibv_cmd_*` | Direct memory mapping + syscalls |
| Performance | Standard latency | Optimized low-latency |
| Work Request Posting | `siw_post_send_ofed` | `siw_post_send_mapped` |
| Completion Polling | `siw_poll_cq_ofed` | `siw_poll_cq_mapped` |
| Memory Access | Kernel copy required | Direct user-kernel shared memory |

```mermaid
graph TB
    subgraph "Operation Mode Selection"
        CONTEXT_ALLOC["siw_alloc_context"]
        IF_TYPE_CHECK{"siw_dev->if_type"}
        OFED_SETUP["OFED Mode Setup"]
        MAPPED_SETUP["Mapped Mode Setup"]
    end
    
    subgraph "OFED Operations"
        OFED_POST_SEND["siw_post_send_ofed"]
        OFED_POST_RECV["siw_post_recv_ofed"]
        OFED_POLL_CQ["siw_poll_cq_ofed"]
    end
    
    subgraph "Mapped Operations"
        MAPPED_POST_SEND["siw_post_send_mapped"]
        MAPPED_POST_RECV["siw_post_recv_mapped"]
        MAPPED_POLL_CQ["siw_poll_cq_mapped"]
    end
    
    CONTEXT_ALLOC --> IF_TYPE_CHECK
    IF_TYPE_CHECK -->|SIW_IF_OFED| OFED_SETUP
    IF_TYPE_CHECK -->|SIW_IF_MAPPED| MAPPED_SETUP
    
    OFED_SETUP --> OFED_POST_SEND
    OFED_SETUP --> OFED_POST_RECV
    OFED_SETUP --> OFED_POLL_CQ
    
    MAPPED_SETUP --> MAPPED_POST_SEND
    MAPPED_SETUP --> MAPPED_POST_RECV
    MAPPED_SETUP --> MAPPED_POLL_CQ
```

**Sources:** [userlib/src/siw.c:111-135](), [userlib/src/siw_uverbs.c:85-134]()

## RDMA Object Management

The library manages all standard RDMA objects through comprehensive lifecycle operations, maintaining both libibverbs compatibility and SoftiWARP-specific optimizations.

### Core Data Structures

```mermaid
graph TB
    subgraph "Device Context"
        SIW_DEVICE["siw_device"]
        SIW_CONTEXT["siw_context"]
    end
    
    subgraph "Protection Domain"
        SIW_PD["siw_pd"]
    end
    
    subgraph "Memory Objects"
        SIW_MR["siw_mr"]
    end
    
    subgraph "Queue Objects"
        SIW_QP["siw_qp"]
        SIW_CQ["siw_cq"]
        SIW_SRQ["siw_srq"]
    end
    
    subgraph "Work Queues"
        SENDQ["sendq (siw_sqe[])"]
        RECVQ["recvq (siw_rqe[])"]
        CQQUEUE["queue (siw_cqe[])"]
    end
    
    SIW_DEVICE --> SIW_CONTEXT
    SIW_CONTEXT --> SIW_PD
    SIW_PD --> SIW_MR
    SIW_PD --> SIW_QP
    SIW_PD --> SIW_CQ
    SIW_PD --> SIW_SRQ
    
    SIW_QP --> SENDQ
    SIW_QP --> RECVQ
    SIW_SRQ --> RECVQ
    SIW_CQ --> CQQUEUE
```

**Sources:** [userlib/src/siw.h:57-123]()

### Queue Pair Operations

Queue pairs represent the core communication endpoints, with the library providing optimized implementations for both operation modes.

```mermaid
graph LR
    subgraph "QP Creation Flow"
        CREATE_QP["siw_create_qp"]
        KERNEL_CMD["ibv_cmd_create_qp"]
        MMAP_SQ["mmap Send Queue"]
        MMAP_RQ["mmap Recv Queue"]
        SPINLOCK_INIT["pthread_spin_init"]
    end
    
    subgraph "QP Work Request Processing"
        POST_SEND["siw_post_send_*"]
        PUSH_SQE["push_send_wqe"]
        DOORBELL["Doorbell Ring"]
        POST_RECV["siw_post_recv_*"]
        PUSH_RQE["push_recv_wqe"]
    end
    
    CREATE_QP --> KERNEL_CMD
    KERNEL_CMD --> MMAP_SQ
    MMAP_SQ --> MMAP_RQ
    MMAP_RQ --> SPINLOCK_INIT
    
    POST_SEND --> PUSH_SQE
    PUSH_SQE --> DOORBELL
    POST_RECV --> PUSH_RQE
```

**Sources:** [userlib/src/siw_verbs.c:321-406](), [userlib/src/siw_uverbs.c:161-221]()

## Performance Optimizations

### Memory Mapping Strategy

In mapped mode, the library establishes direct memory mappings to kernel queue structures, eliminating data copying overhead for work request submission and completion polling.

```mermaid
graph TB
    subgraph "Memory Mapping Process"
        QP_CREATE["Queue Pair Creation"]
        KERNEL_ALLOC["Kernel Queue Allocation"]
        MMAP_CALL["mmap() System Call"]
        USER_ACCESS["Direct User Access"]
    end
    
    subgraph "Mapped Structures"
        SQ_MMAP["Send Queue Mapping<br/>siw_sqe[]"]
        RQ_MMAP["Recv Queue Mapping<br/>siw_rqe[]"]
        CQ_MMAP["Completion Queue Mapping<br/>siw_cqe[]"]
        CQ_CTRL["CQ Control Structure<br/>siw_cq_ctrl"]
    end
    
    QP_CREATE --> KERNEL_ALLOC
    KERNEL_ALLOC --> MMAP_CALL
    MMAP_CALL --> USER_ACCESS
    
    USER_ACCESS --> SQ_MMAP
    USER_ACCESS --> RQ_MMAP
    USER_ACCESS --> CQ_MMAP
    CQ_MMAP --> CQ_CTRL
```

**Sources:** [userlib/src/siw_verbs.c:350-394](), [userlib/src/siw_verbs.c:190-208]()

### Work Request Processing Optimization

The mapped mode implementation uses lock-free algorithms with memory barriers to ensure correct ordering while maximizing performance.

| Operation | OFED Implementation | Mapped Implementation |
|-----------|--------------------|-----------------------|
| Send WR Posting | `ibv_cmd_post_send()` | Direct `siw_sqe` write + doorbell |
| Recv WR Posting | `ibv_cmd_post_recv()` | Direct `siw_rqe` write |
| CQ Polling | `ibv_cmd_poll_cq()` | Direct `siw_cqe` read |
| Synchronization | Kernel locks | User-space spinlocks + memory barriers |

**Sources:** [userlib/src/siw_uverbs.c:247-301](), [userlib/src/siw_uverbs.c:468-492]()

### Completion Queue Notification

The library implements both solicited and unsolicited notification mechanisms, with mapped mode providing direct control structure access for optimal performance.

```mermaid
graph LR
    subgraph "CQ Notification Modes"
        NOTIFY_CALL["siw_notify_cq"]
        CTRL_CHECK{"cq->ctrl available?"}
        MAPPED_NOTIFY["Direct ctrl->notify write"]
        OFED_NOTIFY["ibv_cmd_req_notify_cq"]
    end
    
    subgraph "Notification Types"
        SOLICITED["SIW_NOTIFY_SOLICITED"]
        NEXT_COMP["SIW_NOTIFY_NEXT_COMPLETION"]
    end
    
    NOTIFY_CALL --> CTRL_CHECK
    CTRL_CHECK -->|Yes| MAPPED_NOTIFY
    CTRL_CHECK -->|No| OFED_NOTIFY
    
    MAPPED_NOTIFY --> SOLICITED
    MAPPED_NOTIFY --> NEXT_COMP
```

**Sources:** [userlib/src/siw_uverbs.c:64-82]()

---

