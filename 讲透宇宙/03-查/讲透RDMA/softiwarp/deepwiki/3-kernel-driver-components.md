<!-- source: DeepWiki mcp.deepwiki.com · repo zrlio/softiwarp · page 3 Kernel Driver Components · fetched 2026-11-11 -->

# Kernel Driver Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [kernel/siw.h](kernel/siw.h)
- [kernel/siw_cq.c](kernel/siw_cq.c)
- [kernel/siw_main.c](kernel/siw_main.c)

</details>



## Purpose and Scope

This page provides an overview of the kernel-space components of the SoftiWARP (siw) driver, explaining how the kernel module implements iWARP functionality and integrates with the Linux networking stack and RDMA subsystem. It covers the core architectural components, data structures, and their interactions within the kernel driver.

For detailed implementation of specific components, see: Queue Pair Transmission ([3.1](#3.1)), Connection Management ([3.2](#3.2)), Queue Pair Reception ([3.3](#3.3)), Memory Management ([3.4](#3.4)), Object Management ([3.5](#3.5)), and Device and Module Management ([3.6](#3.6)). For user-space components, see User Space Library ([4](#4)).

## Core Architecture

The SoftiWARP kernel driver implements a software-based iWARP RDMA provider that operates over standard TCP sockets. The driver integrates with the Linux InfiniBand/RDMA subsystem to provide RDMA services to applications through the standard verbs interface.

```mermaid
graph TB
    subgraph "Linux Kernel Space"
        subgraph "RDMA Subsystem"
            IBCORE["ib_core"]
            IWCM["iw_cm"]
        end
        
        subgraph "SoftiWARP Driver (siw)"
            SIWDEV["siw_dev<br/>Device Management"]
            SIWVERBS["siw_verbs<br/>Verbs Implementation"]
            SIWOBJ["Object Management<br/>IDR Trees"]
            SIWQP["siw_qp<br/>Queue Pairs"]
            SIWCQ["siw_cq<br/>Completion Queues"]
            SIWMEM["siw_mem<br/>Memory Regions"]
            SIWCM["Connection Management<br/>CEP State Machine"]
        end
        
        subgraph "Network Stack"
            TCP["TCP Sockets"]
            NETDEV["Network Devices"]
        end
    end
    
    IBCORE --> SIWVERBS
    IWCM --> SIWCM
    SIWDEV --> SIWOBJ
    SIWDEV --> SIWQP
    SIWDEV --> SIWCQ
    SIWDEV --> SIWMEM
    SIWQP --> TCP
    SIWCM --> TCP
    TCP --> NETDEV
```

Sources: [kernel/siw.h:122-151](), [kernel/siw_main.c:341-513]()

## Device and Registration Model

The siw driver follows a one-to-one mapping between network devices and RDMA devices. Each qualified network interface gets its own `siw_dev` instance that registers with the RDMA subsystem.

```mermaid
graph LR
    subgraph "Network Interfaces"
        ETH0["eth0"]
        ETH1["eth1"] 
        LO["lo (loopback)"]
    end
    
    subgraph "SoftiWARP Devices"
        SIWETH0["siw_eth0<br/>siw_dev instance"]
        SIWETH1["siw_eth1<br/>siw_dev instance"]
        SIWLO["siw_lo<br/>siw_dev instance"]
    end
    
    subgraph "RDMA Device Registration"
        IBDEV0["ib_device<br/>registered with ib_core"]
        IBDEV1["ib_device<br/>registered with ib_core"] 
        IBDEV2["ib_device<br/>registered with ib_core"]
    end
    
    ETH0 --> SIWETH0
    ETH1 --> SIWETH1
    LO --> SIWLO
    
    SIWETH0 --> IBDEV0
    SIWETH1 --> IBDEV1
    SIWLO --> IBDEV2
```

Sources: [kernel/siw_main.c:141-183](), [kernel/siw_main.c:517-620]()

## Core Data Structures

The kernel driver is built around several key data structures that represent RDMA objects and their relationships:

| Structure | Purpose | Key Fields |
|-----------|---------|------------|
| `siw_dev` | Main device representation | `netdev`, `attrs`, IDR trees, object counters |
| `siw_qp` | Queue Pair implementation | `tx_ctx`, `rx_ctx`, `sendq`, `recvq`, `attrs` |
| `siw_cq` | Completion Queue | `queue`, `cq_put`, `cq_get`, `num_cqe` |
| `siw_mem` | Memory region/window | `va`, `len`, `perms`, `stag_state` |
| `siw_pd` | Protection Domain | `hdr` (object header) |
| `siw_objhdr` | Common object header | `id`, `ref` (kref), `sdev` |

Sources: [kernel/siw.h:122-178](), [kernel/siw.h:222-258](), [kernel/siw.h:293-303](), [kernel/siw.h:544-587]()

## Object Management System

The driver uses Linux IDR (ID Radix) trees to manage RDMA objects, providing efficient lookup and allocation of object IDs. Each device maintains separate IDR trees for different object types.

```mermaid
graph TB
    subgraph "siw_dev Device Instance"
        IDRLOCK["idr_lock<br/>spinlock"]
        
        subgraph "IDR Trees"
            QPIDR["qp_idr<br/>Queue Pairs"]
            CQIDR["cq_idr<br/>Completion Queues"] 
            PDIDR["pd_idr<br/>Protection Domains"]
            MEMIDR["mem_idr<br/>Memory Regions/Windows"]
        end
        
        subgraph "Object Counters"
            NUMQP["num_qp<br/>atomic_t"]
            NUMCQ["num_cq<br/>atomic_t"]
            NUMPD["num_pd<br/>atomic_t"]
            NUMMEM["num_mem<br/>atomic_t"]
        end
    end
    
    subgraph "Object Lifecycle"
        ALLOC["Object Allocation<br/>idr_alloc()"]
        LOOKUP["Object Lookup<br/>idr_find()"]
        REFCOUNT["Reference Counting<br/>kref_get/put"]
        FREE["Object Cleanup<br/>idr_remove()"]
    end
    
    IDRLOCK --> QPIDR
    IDRLOCK --> CQIDR
    IDRLOCK --> PDIDR  
    IDRLOCK --> MEMIDR
    
    ALLOC --> LOOKUP
    LOOKUP --> REFCOUNT
    REFCOUNT --> FREE
```

Sources: [kernel/siw.h:135-149](), [kernel/siw.h:153-157]()

## Queue Pair Processing Architecture

Queue Pairs are the core data transfer mechanism, with separate TX and RX processing contexts that handle iWARP protocol operations over TCP connections.

```mermaid
graph TB
    subgraph "siw_qp Queue Pair"
        subgraph "Send Side"
            SENDQ["sendq[]<br/>siw_sqe array"]
            SQPUT["sq_put<br/>producer index"]
            SQGET["sq_get<br/>consumer index"] 
            TXCTX["tx_ctx<br/>siw_iwarp_tx"]
        end
        
        subgraph "Receive Side"  
            RECVQ["recvq[]<br/>siw_rqe array"]
            RQPUT["rq_put<br/>producer index"]
            RQGET["rq_get<br/>consumer index"]
            RXCTX["rx_ctx<br/>siw_iwarp_rx"]
        end
        
        subgraph "Read Operations"
            IRQ["irq[]<br/>inbound read queue"]
            ORQ["orq[]<br/>outbound read queue"]
        end
    end
    
    subgraph "Network Processing"
        TCPSOCK["TCP Socket"]
        SKBUFF["Socket Buffers"]
    end
    
    TXCTX --> TCPSOCK
    RXCTX --> SKBUFF
    SENDQ --> TXCTX
    RECVQ --> RXCTX
```

Sources: [kernel/siw.h:544-587](), [kernel/siw.h:409-454](), [kernel/siw.h:483-540]()

## Connection and State Management  

The driver implements iWARP connection establishment through Connection Endpoints (CEPs) that manage the MPA handshake protocol and coordinate with Queue Pair state transitions.

```mermaid
stateDiagram-v2
    [*] --> SIW_EPSTATE_IDLE
    SIW_EPSTATE_IDLE --> SIW_EPSTATE_LISTENING: siw_create_listen()
    SIW_EPSTATE_IDLE --> SIW_EPSTATE_CONNECTING: siw_connect()
    
    SIW_EPSTATE_LISTENING --> SIW_EPSTATE_AWAIT_MPAREQ: TCP_ESTABLISHED
    SIW_EPSTATE_CONNECTING --> SIW_EPSTATE_AWAIT_MPAREP: TCP_ESTABLISHED
    
    SIW_EPSTATE_AWAIT_MPAREQ --> SIW_EPSTATE_RECVD_MPAREQ: MPA_Request
    SIW_EPSTATE_AWAIT_MPAREP --> SIW_EPSTATE_RDMA_MODE: MPA_Reply
    
    SIW_EPSTATE_RECVD_MPAREQ --> SIW_EPSTATE_RDMA_MODE: siw_accept()
    SIW_EPSTATE_RECVD_MPAREQ --> SIW_EPSTATE_CLOSED: siw_reject()
    
    SIW_EPSTATE_RDMA_MODE --> SIW_EPSTATE_CLOSED: Error/Close
```

Sources: [kernel/siw.h:305-315]() (QP states), connection management implementation in sub-components

## Memory Management Integration

The driver provides RDMA memory management through integration with Linux memory management, supporting both kernel and user memory registration with DMA operations.

```mermaid
graph TB
    subgraph "Memory Registration"
        UMEM["siw_umem<br/>User Memory Descriptor"]
        PAGECHUNK["siw_page_chunk<br/>Page Arrays"]
        PAGES["Physical Pages<br/>get_user_pages()"]
    end
    
    subgraph "RDMA Memory Objects"
        MR["siw_mr<br/>Memory Region"]
        MW["siw_mw<br/>Memory Window"] 
        STAG["STAG<br/>Steering Tag"]
    end
    
    subgraph "Access Control"
        PD["siw_pd<br/>Protection Domain"]
        PERMS["Access Permissions<br/>Local/Remote R/W"]
        VALIDATION["STAG Validation<br/>VALID/INVALID"]
    end
    
    PAGES --> PAGECHUNK
    PAGECHUNK --> UMEM
    UMEM --> MR
    MR --> MW
    PD --> MR
    PERMS --> VALIDATION
    STAG --> VALIDATION
```

Sources: [kernel/siw.h:203-258](), [kernel/siw.h:696-723]()

## Integration Points

The kernel driver integrates with several Linux subsystems:

- **RDMA Subsystem**: Registers as an `ib_device` with verbs operations
- **Network Stack**: Uses TCP sockets for iWARP transport  
- **Memory Management**: Integrates with page allocation and DMA mapping
- **Module Framework**: Standard Linux kernel module with parameter support
- **Debug Framework**: DebugFS integration for runtime diagnostics

The driver supports both kernel clients (direct verbs calls) and user-space applications (through uverbs), with different optimizations for each path.

Sources: [kernel/siw_main.c:39-770](), [kernel/siw.h:60-63]()

---

