<!-- source: DeepWiki mcp.deepwiki.com · repo zrlio/softiwarp · page 1 Overview · fetched 2026-11-11 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [kernel/siw.h](kernel/siw.h)
- [kernel/siw_cq.c](kernel/siw_cq.c)

</details>



## Purpose and Scope

SoftiWARP (siw) is a software implementation of the iWARP protocol suite that provides RDMA (Remote Direct Memory Access) functionality over standard TCP/IP networks without requiring dedicated RDMA hardware. This documentation covers the complete SoftiWARP system, including both the kernel driver components and the user-space library that together implement the iWARP protocols (MPA/DDP/RDMAP, IETF-RFC 5044/5041/5040) entirely in software.

For detailed information about building and installing the system, see [Build System and Installation](#6). For specifics about the kernel-userspace interface, see [User-Kernel Interface](#5).

**Note**: This repository is maintained for reference only. The SoftiWARP driver became part of upstream Linux with kernel 5.2 and is now maintained there.

## System Components

SoftiWARP consists of two primary components that work together to provide RDMA functionality:

| Component | Location | Purpose |
|-----------|----------|---------|
| Kernel Module (`siw`) | `kernel/` | Implements iWARP protocol processing, connection management, and data transfer |
| User Library (`libsiw`) | `userlib/` | Provides user-space RDMA verbs API and integrates with OpenFabrics framework |
| Common Headers | `common/` | Shared data structures and definitions between kernel and user space |

## Overall System Architecture

The following diagram shows how SoftiWARP integrates with the Linux networking stack and OpenFabrics ecosystem:

### SoftiWARP System Architecture
```mermaid
graph TB
    subgraph "User Space Applications"
        APP["RDMA Applications"]
        LIBIBVERBS["libibverbs Framework"]
        LIBRDMACM["librdmacm Connection Mgmt"]
    end
    
    subgraph "SoftiWARP User Library"  
        LIBSIW["libsiw User Library"]
        SIW_VERBS["siw_verbs.c"]
        SIW_UVERBS["siw_uverbs.c"]
    end
    
    subgraph "Linux Kernel"
        IBCORE["InfiniBand Core"]
        IWCM["iWARP Connection Manager"]
        
        subgraph "SoftiWARP Kernel Driver"
            SIW_MAIN["siw_main.c"]
            SIW_VERBS_K["siw_verbs.c"]
            SIW_QP_TX["siw_qp_tx.c"]
            SIW_QP_RX["siw_qp_rx.c"] 
            SIW_CM["siw_cm.c"]
            SIW_OBJ["siw_obj.c"]
        end
        
        TCP["TCP Socket Layer"]
    end
    
    subgraph "Network Hardware"
        NET["Network Interfaces"]
    end
    
    APP --> LIBIBVERBS
    APP --> LIBRDMACM
    LIBIBVERBS --> LIBSIW
    LIBRDMACM --> IWCM
    
    LIBSIW --> SIW_VERBS
    LIBSIW --> SIW_UVERBS
    
    LIBSIW -.->|"System Calls"| IBCORE
    IWCM --> SIW_CM
    IBCORE --> SIW_VERBS_K
    
    SIW_MAIN --> SIW_VERBS_K
    SIW_MAIN --> SIW_QP_TX
    SIW_MAIN --> SIW_QP_RX
    SIW_MAIN --> SIW_CM
    SIW_MAIN --> SIW_OBJ
    
    SIW_QP_TX --> TCP
    SIW_QP_RX --> TCP
    SIW_CM --> TCP
    TCP --> NET
```

Sources: [README.md:11-34](), [kernel/siw.h:122-151]()

## Core Data Structures and Objects

SoftiWARP manages several key RDMA objects that are fundamental to its operation:

### SoftiWARP Object Hierarchy
```mermaid
graph TB
    subgraph "siw_dev Device Instance"
        DEV["siw_dev<br/>Main Device Structure"]
        NETDEV["net_device<br/>Associated Network Interface"]
        IDR_TREES["IDR Trees<br/>Object Management"]
    end
    
    subgraph "RDMA Objects"
        QP["siw_qp<br/>Queue Pairs"]
        CQ["siw_cq<br/>Completion Queues"] 
        PD["siw_pd<br/>Protection Domains"]
        MR["siw_mr<br/>Memory Regions"]
        MW["siw_mw<br/>Memory Windows"]
        SRQ["siw_srq<br/>Shared Receive Queues"]
    end
    
    subgraph "Object Lifecycle"
        OBJHDR["siw_objhdr<br/>Common Object Header"]
        KREF["kref<br/>Reference Counting"]
        CLEANUP["Object Cleanup"]
    end
    
    DEV --> NETDEV
    DEV --> IDR_TREES
    
    IDR_TREES --> QP
    IDR_TREES --> CQ  
    IDR_TREES --> PD
    IDR_TREES --> MR
    IDR_TREES --> MW
    IDR_TREES --> SRQ
    
    QP --> OBJHDR
    CQ --> OBJHDR
    PD --> OBJHDR
    MR --> OBJHDR
    MW --> OBJHDR
    SRQ --> OBJHDR
    
    OBJHDR --> KREF
    KREF --> CLEANUP
```

Sources: [kernel/siw.h:122-151](), [kernel/siw.h:153-157](), [kernel/siw.h:175-178]()

## iWARP Protocol Stack Implementation

SoftiWARP implements the complete iWARP protocol stack as defined by IETF RFCs:

### iWARP Protocol Layers
```mermaid
graph TB
    subgraph "Application Layer"
        RDMA_OPS["RDMA Operations<br/>Send, Receive, Read, Write"]
    end
    
    subgraph "RDMAP Layer"
        RDMAP["RDMAP (RFC 5040)<br/>Remote Direct Memory Access Protocol"]
        RDMAP_HDR["RDMAP Headers"]
    end
    
    subgraph "DDP Layer" 
        DDP["DDP (RFC 5041)<br/>Direct Data Placement"]
        DDP_SEGMENTS["DDP Segments"]
        TAGGED["Tagged Buffers"]
        UNTAGGED["Untagged Buffers"]
    end
    
    subgraph "MPA Layer"
        MPA["MPA (RFC 5044)<br/>Marker PDU Aligned"]
        MPA_MARKERS["MPA Markers"]
        MPA_CRC["MPA CRC"]
    end
    
    subgraph "Transport Layer"
        TCP["TCP Reliable Stream"]
        SOCKETS["Linux Socket API"]
    end
    
    subgraph "Network Layer"
        IP["IP Layer"]
        ETHERNET["Ethernet"]
    end
    
    RDMA_OPS --> RDMAP
    RDMAP --> RDMAP_HDR
    RDMAP_HDR --> DDP
    
    DDP --> DDP_SEGMENTS
    DDP_SEGMENTS --> TAGGED
    DDP_SEGMENTS --> UNTAGGED
    
    TAGGED --> MPA
    UNTAGGED --> MPA
    MPA --> MPA_MARKERS
    MPA --> MPA_CRC
    
    MPA_MARKERS --> TCP
    MPA_CRC --> TCP
    TCP --> SOCKETS
    SOCKETS --> IP
    IP --> ETHERNET
```

Sources: [README.md:13-17](), [kernel/siw.h:409-454](), [kernel/siw.h:483-540]()

## Data Flow Architecture

The following diagram illustrates how data flows through the SoftiWARP system from application to network:

### SoftiWARP Data Flow
```mermaid
graph LR
    subgraph "User Application"
        WR["Work Requests<br/>siw_sqe/siw_rqe"]
    end
    
    subgraph "Kernel Processing"
        TX_PATH["TX Path<br/>siw_qp_tx.c"]
        RX_PATH["RX Path<br/>siw_qp_rx.c"]
        
        subgraph "Queue Management"
            SQ["Send Queue<br/>sendq[]"]
            RQ["Receive Queue<br/>recvq[]"]
            CQ_TX["Completion Queue<br/>TX Side"]
            CQ_RX["Completion Queue<br/>RX Side"]
        end
        
        subgraph "Protocol Processing"
            IWARP_TX["iwarp_tx Context"]
            IWARP_RX["iwarp_rx Context"]
            MPA_CRC_TX["MPA CRC TX"]
            MPA_CRC_RX["MPA CRC RX"]
        end
    end
    
    subgraph "Network"
        SKB["Socket Buffers<br/>sk_buff"]
        TCP_SOCK["TCP Socket"]
    end
    
    WR --> SQ
    WR --> RQ
    
    SQ --> TX_PATH
    TX_PATH --> IWARP_TX
    IWARP_TX --> MPA_CRC_TX
    MPA_CRC_TX --> SKB
    SKB --> TCP_SOCK
    
    TCP_SOCK --> SKB
    SKB --> MPA_CRC_RX
    MPA_CRC_RX --> IWARP_RX
    IWARP_RX --> RX_PATH
    RX_PATH --> RQ
    
    TX_PATH --> CQ_TX
    RX_PATH --> CQ_RX
```

Sources: [kernel/siw.h:544-587](), [kernel/siw.h:409-454](), [kernel/siw.h:483-540]()

## Key System Characteristics

SoftiWARP provides the following key characteristics and capabilities:

- **Software-only Implementation**: No dedicated RDMA hardware required - runs over standard Ethernet
- **OpenFabrics Integration**: Compatible with standard RDMA applications through libibverbs
- **Kernel and User Space Support**: Supports both kernel-level and user-level RDMA applications  
- **TCP-based Transport**: Uses reliable TCP connections for data transport
- **Memory Management**: Efficient user memory registration and DMA operations
- **Connection Management**: Full iWARP connection establishment and teardown
- **Performance Optimization**: Multiple data paths including direct memory mapping for performance

The system limits are defined in [kernel/siw.h:68-82]() and include support for up to 102,400 Queue Pairs, 3.2M work requests, and 128 outstanding read operations per QP.

Sources: [README.md:11-28](), [kernel/siw.h:60-82](), [kernel/siw.h:90-119]()

---

