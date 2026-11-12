<!-- source: DeepWiki mcp.deepwiki.com · repo zrlio/softiwarp · page 2 System Architecture · fetched 2026-11-11 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [common/siw_user.h](common/siw_user.h)
- [kernel/siw.h](kernel/siw.h)
- [kernel/siw_cq.c](kernel/siw_cq.c)

</details>



This document provides a detailed explanation of the SoftiWARP (siw) system architecture, focusing on the core data structures, component interactions, and the relationship between kernel and user space components. It covers the overall design patterns that enable software-based iWARP functionality over standard TCP sockets.

For information about specific kernel driver components, see [Kernel Driver Components](#3). For details about the user space library implementation, see [User Space Library](#4). For the user-kernel interface specifications, see [User-Kernel Interface](#5).

## Overall System Architecture

SoftiWARP implements a layered architecture that bridges RDMA applications with the Linux network stack through a software-only iWARP implementation. The system is split between user space and kernel space components that communicate through a well-defined ABI.

### System Components Overview

```mermaid
graph TB
    subgraph "User Space"
        APP["RDMA Applications"]
        LIBIBVERBS["libibverbs Framework"]
        LIBSIW["libsiw User Library"]
        LIBRDMACM["librdmacm Connection Manager"]
    end
    
    subgraph "Kernel Space"
        IBCORE["InfiniBand Core"]
        IWCM["iWARP Connection Manager"]
        SIW_MAIN["siw Module (siw_main.c)"]
        SIW_VERBS["siw_verbs.c"]
        SIW_QP["siw_qp.c"]
        SIW_CM["siw_cm.c"]
        SIW_MEM["siw_mem.c"]
        SIW_OBJ["siw_obj.c"]
    end
    
    subgraph "Linux Network Stack"
        TCP["TCP Sockets"]
        NET["Network Interfaces"]
    end
    
    APP --> LIBIBVERBS
    APP --> LIBRDMACM
    LIBIBVERBS --> LIBSIW
    LIBRDMACM --> IWCM
    
    LIBSIW -.->|"System Calls"| IBCORE
    IWCM --> SIW_CM
    IBCORE --> SIW_VERBS
    
    SIW_MAIN --> SIW_VERBS
    SIW_MAIN --> SIW_QP
    SIW_MAIN --> SIW_CM
    SIW_MAIN --> SIW_MEM
    SIW_MAIN --> SIW_OBJ
    
    SIW_CM --> TCP
    SIW_QP --> TCP
    TCP --> NET
```

Sources: [README.md:11-28](), [kernel/siw.h:122-151]()

## Core Device and Object Management

The `siw_dev` structure serves as the central coordination point for all RDMA objects and device operations. It integrates with the OpenFabrics framework while managing object lifecycles through IDR trees and reference counting.

### Device and Object Hierarchy

```mermaid
graph TB
    subgraph "siw_dev Device Structure"
        DEV["siw_dev"]
        OFADEV["ib_device ofa_dev"]
        NETDEV["net_device *netdev"]
        ATTRS["siw_devinfo attrs"]
        
        DEV --> OFADEV
        DEV --> NETDEV
        DEV --> ATTRS
    end
    
    subgraph "Object Management"
        IDR_LOCK["spinlock_t idr_lock"]
        QP_IDR["idr qp_idr"]
        CQ_IDR["idr cq_idr"]
        PD_IDR["idr pd_idr"]
        MEM_IDR["idr mem_idr"]
        
        IDR_LOCK --> QP_IDR
        IDR_LOCK --> CQ_IDR
        IDR_LOCK --> PD_IDR
        IDR_LOCK --> MEM_IDR
    end
    
    subgraph "RDMA Objects"
        QP_OBJ["siw_qp Objects"]
        CQ_OBJ["siw_cq Objects"]
        PD_OBJ["siw_pd Objects"]
        MR_OBJ["siw_mr Objects"]
        MW_OBJ["siw_mw Objects"]
        
        QP_IDR --> QP_OBJ
        CQ_IDR --> CQ_OBJ
        PD_IDR --> PD_OBJ
        MEM_IDR --> MR_OBJ
        MEM_IDR --> MW_OBJ
    end
    
    subgraph "Object Headers"
        OBJHDR["siw_objhdr"]
        KREF["kref ref"]
        OBJID["u32 id"]
        SDEV["siw_dev *sdev"]
        
        OBJHDR --> KREF
        OBJHDR --> OBJID
        OBJHDR --> SDEV
    end
    
    DEV --> IDR_LOCK
    QP_OBJ --> OBJHDR
    CQ_OBJ --> OBJHDR
    PD_OBJ --> OBJHDR
    MR_OBJ --> OBJHDR
    MW_OBJ --> OBJHDR
```

Sources: [kernel/siw.h:122-151](), [kernel/siw.h:153-157]()

## Queue Pair Architecture

Queue pairs represent the core data transfer mechanism in SoftiWARP. Each `siw_qp` contains separate transmit and receive contexts, multiple work queues, and integrates with the completion queue system.

### Queue Pair Structure and Queues

```mermaid
graph TB
    subgraph "siw_qp Structure"
        QP["siw_qp"]
        OFA_QP["ib_qp ofa_qp"]
        HDR["siw_objhdr hdr"]
        ATTRS["siw_qp_attrs attrs"]
        
        QP --> OFA_QP
        QP --> HDR
        QP --> ATTRS
    end
    
    subgraph "Work Queues"
        SENDQ["siw_sqe *sendq"]
        RECVQ["siw_rqe *recvq"]
        IRQ["siw_sqe *irq"]
        ORQ["siw_sqe *orq"]
        
        SENDQ_GET["sq_get"]
        SENDQ_PUT["sq_put"]
        RECVQ_GET["rq_get"]
        RECVQ_PUT["rq_put"]
        IRQ_GET["irq_get"]
        IRQ_PUT["irq_put"]
        ORQ_GET["orq_get"]
        ORQ_PUT["orq_put"]
        
        SENDQ --> SENDQ_GET
        SENDQ --> SENDQ_PUT
        RECVQ --> RECVQ_GET
        RECVQ --> RECVQ_PUT
        IRQ --> IRQ_GET
        IRQ --> IRQ_PUT
        ORQ --> ORQ_GET
        ORQ --> ORQ_PUT
    end
    
    subgraph "Processing Contexts"
        RX_CTX["siw_iwarp_rx rx_ctx"]
        TX_CTX["siw_iwarp_tx tx_ctx"]
        
        RX_WQE["siw_wqe wqe_active"]
        TX_WQE["siw_wqe wqe_active"]
        
        RX_CTX --> RX_WQE
        TX_CTX --> TX_WQE
    end
    
    subgraph "Associated Objects"
        PD["siw_pd *pd"]
        SCQ["siw_cq *scq"]
        RCQ["siw_cq *rcq"]
        CEP["siw_cep *cep"]
        
        PD --> SCQ
        PD --> RCQ
        PD --> CEP
    end
    
    QP --> SENDQ
    QP --> RECVQ
    QP --> IRQ
    QP --> ORQ
    QP --> RX_CTX
    QP --> TX_CTX
    QP --> PD
```

Sources: [kernel/siw.h:544-587](), [common/siw_user.h:149-164]()

## Memory Management Architecture

SoftiWARP implements a sophisticated memory management system that handles user memory registration, DMA operations, and provides both Memory Regions (MR) and Memory Windows (MW) functionality.

### Memory Object Hierarchy

```mermaid
graph TB
    subgraph "Memory Registration"
        UMEM["siw_umem"]
        PAGE_CHUNK["siw_page_chunk"]
        PAGES["struct page **p"]
        
        UMEM --> PAGE_CHUNK
        PAGE_CHUNK --> PAGES
    end
    
    subgraph "Memory Objects"
        MEM["siw_mem"]
        MR["siw_mr"]
        MW["siw_mw"]
        
        MEM_HDR["siw_objhdr hdr"]
        MEM_MR["siw_mr *mr"]
        MEM_VA["u64 va"]
        MEM_LEN["u64 len"]
        MEM_PERMS["enum siw_access_flags perms"]
        
        MEM --> MEM_HDR
        MEM --> MEM_MR
        MEM --> MEM_VA
        MEM --> MEM_LEN
        MEM --> MEM_PERMS
    end
    
    subgraph "Memory Region"
        MR_OFA["ib_mr ofa_mr"]
        MR_MEM["siw_mem mem"]
        MR_UMEM["siw_umem *umem"]
        MR_PD["siw_pd *pd"]
        
        MR --> MR_OFA
        MR --> MR_MEM
        MR --> MR_UMEM
        MR --> MR_PD
    end
    
    subgraph "Memory Window"
        MW_OFA["ib_mw ofa_mw"]
        MW_MEM["siw_mem mem"]
        
        MW --> MW_OFA
        MW --> MW_MEM
    end
    
    subgraph "Access Control"
        SR_MEM_LREAD["SR_MEM_LREAD"]
        SR_MEM_LWRITE["SR_MEM_LWRITE"]
        SR_MEM_RREAD["SR_MEM_RREAD"]
        SR_MEM_RWRITE["SR_MEM_RWRITE"]
        
        MEM_PERMS --> SR_MEM_LREAD
        MEM_PERMS --> SR_MEM_LWRITE
        MEM_PERMS --> SR_MEM_RREAD
        MEM_PERMS --> SR_MEM_RWRITE
    end
    
    MR_UMEM --> UMEM
    MR_MEM --> MEM
    MW_MEM --> MEM
```

Sources: [kernel/siw.h:207-258](), [kernel/siw.h:180-190]()

## User-Kernel Communication Paths

SoftiWARP provides two distinct communication paths between user space and kernel: the standard OpenFabrics syscall interface and an optimized mapped interface for high-performance operations.

### Dual Interface Architecture

```mermaid
graph TB
    subgraph "User Space Library"
        USER_APP["User Application"]
        VERBS_U["siw_verbs.c (user)"]
        UVERBS["siw_uverbs.c"]
    end
    
    subgraph "Interface Selection"
        OFED_PATH["SIW_IF_OFED"]
        MAPPED_PATH["SIW_IF_MAPPED"]
        
        OFED_OPS["OFED Operations"]
        MAPPED_OPS["Mapped Operations"]
        
        OFED_PATH --> OFED_OPS
        MAPPED_PATH --> MAPPED_OPS
    end
    
    subgraph "Kernel Interface"
        IBCORE_K["InfiniBand Core"]
        VERBS_K["siw_verbs.c (kernel)"]
        UOBJ["siw_uobj"]
        UCONTEXT["siw_ucontext"]
    end
    
    subgraph "Shared Memory Objects"
        SQE_SHARED["siw_sqe (shared)"]
        RQE_SHARED["siw_rqe (shared)"]
        CQE_SHARED["siw_cqe (shared)"]
        CQ_CTRL["siw_cq_ctrl"]
    end
    
    subgraph "ABI Structures"
        URESP_CQ["siw_uresp_create_cq"]
        URESP_QP["siw_uresp_create_qp"]
        UREQ_MR["siw_ureq_reg_mr"]
        URESP_MR["siw_uresp_reg_mr"]
    end
    
    USER_APP --> VERBS_U
    VERBS_U --> UVERBS
    
    UVERBS --> OFED_PATH
    UVERBS --> MAPPED_PATH
    
    OFED_OPS -.->|"System Calls"| IBCORE_K
    MAPPED_OPS -.->|"Direct Memory Access"| SQE_SHARED
    MAPPED_OPS -.->|"Direct Memory Access"| RQE_SHARED
    MAPPED_OPS -.->|"Direct Memory Access"| CQE_SHARED
    
    IBCORE_K --> VERBS_K
    VERBS_K --> UOBJ
    VERBS_K --> UCONTEXT
    
    VERBS_K --> URESP_CQ
    VERBS_K --> URESP_QP
    VERBS_K --> UREQ_MR
    VERBS_K --> URESP_MR
```

Sources: [kernel/siw.h:60-63](), [common/siw_user.h:63-95](), [kernel/siw.h:159-173]()

## Network Integration and Protocol Stack

SoftiWARP integrates with the Linux network stack through TCP sockets, implementing the complete iWARP protocol suite (MPA/DDP/RDMAP) in software while leveraging existing network infrastructure.

### Protocol Stack Integration

```mermaid
graph TB
    subgraph "iWARP Protocol Implementation"
        IWARP_TX["siw_iwarp_tx"]
        IWARP_RX["siw_iwarp_rx"]
        
        IWARP_HDR["union iwarp_hdrs hdr"]
        MPA_TRAILER["mpa_trailer trailer"]
        
        IWARP_TX --> IWARP_HDR
        IWARP_RX --> IWARP_HDR
        IWARP_TX --> MPA_TRAILER
        IWARP_RX --> MPA_TRAILER
    end
    
    subgraph "Protocol Processing"
        SEND_PKT["siw_send_pkt"]
        WRITE_PKT["siw_write_pkt"]
        RREQ_PKT["siw_rreq_pkt"]
        RRESP_PKT["siw_rresp_pkt"]
        
        IWARP_HDR --> SEND_PKT
        IWARP_HDR --> WRITE_PKT
        IWARP_HDR --> RREQ_PKT
        IWARP_HDR --> RRESP_PKT
    end
    
    subgraph "Connection Management"
        CEP["siw_cep"]
        CM_ATTRS["siw_qp_attrs"]
        SOCKET["socket *llp_stream_handle"]
        
        CEP --> CM_ATTRS
        CM_ATTRS --> SOCKET
    end
    
    subgraph "TCP Integration"
        SK_UPCALLS["siw_sk_upcalls"]
        TCP_SOCK["TCP Sockets"]
        SKB["sk_buff"]
        
        SK_DATA_READY["sk_data_ready"]
        SK_WRITE_SPACE["sk_write_space"]
        SK_STATE_CHANGE["sk_state_change"]
        SK_ERROR_REPORT["sk_error_report"]
        
        SK_UPCALLS --> SK_DATA_READY
        SK_UPCALLS --> SK_WRITE_SPACE
        SK_UPCALLS --> SK_STATE_CHANGE
        SK_UPCALLS --> SK_ERROR_REPORT
        
        TCP_SOCK --> SKB
    end
    
    subgraph "Network Devices"
        NETDEV["net_device *netdev"]
        NET_INTERFACES["Network Interfaces"]
        
        NETDEV --> NET_INTERFACES
    end
    
    IWARP_TX --> TCP_SOCK
    IWARP_RX --> SKB
    SOCKET --> TCP_SOCK
    CEP --> SK_UPCALLS
    TCP_SOCK --> NETDEV
```

Sources: [kernel/siw.h:409-454](), [kernel/siw.h:483-540](), [kernel/siw.h:346-351](), [kernel/siw.h:391-392]()

## OpenFabrics Integration

SoftiWARP integrates seamlessly with the OpenFabrics architecture by implementing the required verb interfaces and maintaining compatibility with existing RDMA applications through the InfiniBand core layer.

### OFA Interface Implementation

```mermaid
graph TB
    subgraph "OFA Device Layer"
        IB_DEVICE["ib_device"]
        SIW_DEV_OFA["siw_dev.ofa_dev"]
        DEVICE_ATTRS["siw_devinfo attrs"]
        
        SIW_DEV_OFA --> IB_DEVICE
        SIW_DEV_OFA --> DEVICE_ATTRS
    end
    
    subgraph "OFA Object Wrappers"
        IB_QP["ib_qp ofa_qp"]
        IB_CQ["ib_cq ofa_cq"]
        IB_PD["ib_pd ofa_pd"]
        IB_MR["ib_mr ofa_mr"]
        IB_MW["ib_mw ofa_mw"]
        
        SIW_QP_OFA["siw_qp.ofa_qp"]
        SIW_CQ_OFA["siw_cq.ofa_cq"]
        SIW_PD_OFA["siw_pd.ofa_pd"]
        SIW_MR_OFA["siw_mr.ofa_mr"]
        SIW_MW_OFA["siw_mw.ofa_mw"]
        
        SIW_QP_OFA --> IB_QP
        SIW_CQ_OFA --> IB_CQ
        SIW_PD_OFA --> IB_PD
        SIW_MR_OFA --> IB_MR
        SIW_MW_OFA --> IB_MW
    end
    
    subgraph "Verb Operations"
        QUERY_DEVICE["siw_query_device"]
        CREATE_QP["siw_create_qp"]
        CREATE_CQ["siw_create_cq"]
        REG_MR["siw_reg_mr"]
        POST_SEND["siw_post_send"]
        POST_RECV["siw_post_recv"]
        POLL_CQ["siw_poll_cq"]
    end
    
    subgraph "Completion Translation"
        SIW_CQE["siw_cqe"]
        IB_WC["ib_wc"]
        WC_TRANSLATE["siw_wc_siw2ofa"]
        
        SIW_CQE --> WC_TRANSLATE
        WC_TRANSLATE --> IB_WC
    end
    
    IB_DEVICE --> QUERY_DEVICE
    IB_QP --> CREATE_QP
    IB_QP --> POST_SEND
    IB_QP --> POST_RECV
    IB_CQ --> CREATE_CQ
    IB_CQ --> POLL_CQ
    IB_MR --> REG_MR
    
    POLL_CQ --> SIW_CQE
```

Sources: [kernel/siw.h:90-119](), [kernel/siw_cq.c:52-62](), [kernel/siw_cq.c:67-88]()

---

