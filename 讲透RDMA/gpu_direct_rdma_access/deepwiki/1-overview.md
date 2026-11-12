<!-- source: DeepWiki mcp.deepwiki.com · repo Mellanox/gpu_direct_rdma_access · page 1 Overview · fetched 2026-11-11 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Makefile](Makefile)
- [README.md](README.md)
- [gpu_direct_rdma_access.c](gpu_direct_rdma_access.c)

</details>



## Purpose and Scope

This document provides an overview of the GPU Direct RDMA Access system, a high-performance data transfer solution that enables direct memory access between distributed systems using Mellanox Dynamic Connect (DC) Queue Pairs. The system supports both GPU and CPU memory allocation with transparent RDMA operations, eliminating traditional CPU-mediated data transfers for optimal performance.

The system consists of client-server applications that demonstrate GPU Direct RDMA capabilities, along with supporting libraries for memory management, network configuration, and hardware topology discovery. For detailed information about specific subsystems, see the [Build System](#2), [Core RDMA Engine](#3), [Memory Management Subsystem](#4), and [Client-Server Applications](#5).

Sources: [README.md:1-4](), [gpu_direct_rdma_access.c:1-31]()

## High-Level Architecture

The GPU Direct RDMA Access system implements a distributed architecture where clients can perform high-performance data transfers to remote servers using RDMA operations directly to GPU or CPU memory buffers.

### System Architecture Overview

```mermaid
graph TB
    subgraph "Client Node"
        CLIENT["client.c<br/>Main Application"]
        CLIENT_MEM["Memory Buffers<br/>(GPU/CPU)"]
        CLIENT_RDMA["RDMA Engine<br/>DCT Queue Pair"]
    end
    
    subgraph "Server Node"
        SERVER["server.c<br/>Main Application"]
        SERVER_MEM["CPU Memory<br/>Buffers"]
        SERVER_RDMA["RDMA Engine<br/>DCI Queue Pair"]
    end
    
    subgraph "Core RDMA System"
        RDMA_LIB["gpu_direct_rdma_access.c<br/>DC QP Management"]
        MEM_MGR["gpu_mem_util.c<br/>Memory Abstraction"]
        UTILS["utils.c<br/>Network Utilities"]
        AH_CACHE["khash.h<br/>Address Handle Cache"]
    end
    
    subgraph "Infrastructure"
        CONFIG_SCRIPTS["Configuration Scripts<br/>arp_announce_conf.sh<br/>map_pci_nic_gpu.sh"]
        BUILD_SYS["Makefile<br/>Conditional Compilation"]
    end
    
    CLIENT --> CLIENT_MEM
    CLIENT --> RDMA_LIB
    SERVER --> SERVER_MEM
    SERVER --> RDMA_LIB
    RDMA_LIB --> MEM_MGR
    RDMA_LIB --> UTILS
    RDMA_LIB --> AH_CACHE
    CLIENT_RDMA -.->|"RDMA Operations"| SERVER_RDMA
    CLIENT -.->|"TCP Control Channel"| SERVER
    
    CONFIG_SCRIPTS --> CLIENT
    CONFIG_SCRIPTS --> SERVER
    BUILD_SYS --> CLIENT
    BUILD_SYS --> SERVER
```

Sources: [Makefile:1-55](), [gpu_direct_rdma_access.c:97-154](), [README.md:10-16]()

## Key Features

### Dynamic Connect Queue Pairs
The system uses Mellanox-specific Dynamic Connect (DC) Queue Pairs to achieve high performance RDMA operations. The client creates a DCT (Dynamic Connect Target) while the server uses DCI (Dynamic Connect Initiator) for scalable one-to-many connections.

### Unified Memory Management
The memory subsystem provides a transparent abstraction layer supporting both CUDA GPU memory and traditional CPU memory allocation through a single API, enabling deployment flexibility across different hardware configurations.

### Address Handle Caching
Performance optimization through cached address resolution using hash tables to store `ibv_ah` structures, reducing overhead for repeated RDMA operations to the same destinations.

### Conditional Compilation
Sophisticated build system supporting multiple variants: GPU-enabled vs CPU-only builds, with optional latency measurement capabilities through preprocessor flags.

Sources: [gpu_direct_rdma_access.c:618-621](), [gpu_direct_rdma_access.c:796-798](), [gpu_direct_rdma_access.c:76](), [Makefile:5-19]()

## Core System Components

### RDMA Device Management

```mermaid
graph TB
    subgraph "Client Side (DCT)"
        CLIENT_INIT["rdma_open_device_client()"]
        DCT_QP["DCT Queue Pair<br/>mlx5dv_create_qp()"]
        SRQ["Shared Receive Queue<br/>ibv_create_srq()"]
    end
    
    subgraph "Server Side (DCI)"
        SERVER_INIT["rdma_open_device_server()"]
        DCI_QP["DCI Queue Pair<br/>mlx5dv_create_qp()"]
        QPEX["Extended QP Interface<br/>ibv_qp_to_qp_ex()"]
    end
    
    subgraph "Common Infrastructure"
        CONTEXT["IBV Context<br/>open_ib_device_by_addr()"]
        PD["Protection Domain<br/>ibv_alloc_pd()"]
        CQ["Completion Queue<br/>ibv_create_cq()"]
        AH_HASH["Address Handle Cache<br/>kh_ib_ah"]
    end
    
    CLIENT_INIT --> DCT_QP
    CLIENT_INIT --> SRQ
    SERVER_INIT --> DCI_QP
    SERVER_INIT --> QPEX
    
    DCT_QP --> CONTEXT
    DCI_QP --> CONTEXT
    DCT_QP --> PD
    DCI_QP --> PD
    DCT_QP --> CQ
    DCI_QP --> CQ
    
    CLIENT_INIT --> AH_HASH
    SERVER_INIT --> AH_HASH
```

Sources: [gpu_direct_rdma_access.c:526-711](), [gpu_direct_rdma_access.c:714-886](), [gpu_direct_rdma_access.c:97-143]()

### Memory Management Architecture

```mermaid
graph TB
    subgraph "Unified Memory API"
        ALLOC_API["work_buffer_alloc()"]
        FREE_API["work_buffer_free()"]
    end
    
    subgraph "Compilation Paths"
        CUDA_FLAG{{"HAVE_CUDA<br/>Preprocessor Flag"}}
    end
    
    subgraph "Runtime Selection"
        USE_CUDA_FLAG{{"use_cuda<br/>Runtime Parameter"}}
        BDF_PARAM["bdf Parameter<br/>GPU Device Selection"]
    end
    
    subgraph "GPU Memory Path"
        CUDA_CONTEXT["CUDA Context<br/>cuCtxCreate()"]
        GPU_ALLOC["GPU Memory<br/>cuMemAlloc()"]
    end
    
    subgraph "CPU Memory Path"
        CPU_ALLOC["Aligned Memory<br/>memalign()"]
    end
    
    subgraph "RDMA Registration"
        MR_REG["Memory Region<br/>ibv_reg_mr()"]
        RDMA_BUFFER["rdma_buffer<br/>Structure"]
    end
    
    ALLOC_API --> CUDA_FLAG
    ALLOC_API --> USE_CUDA_FLAG
    CUDA_FLAG -->|"Defined"| BDF_PARAM
    CUDA_FLAG -->|"Not Defined"| CPU_ALLOC
    USE_CUDA_FLAG -->|"True"| CUDA_CONTEXT
    USE_CUDA_FLAG -->|"False"| CPU_ALLOC
    BDF_PARAM --> GPU_ALLOC
    CUDA_CONTEXT --> GPU_ALLOC
    
    GPU_ALLOC --> MR_REG
    CPU_ALLOC --> MR_REG
    MR_REG --> RDMA_BUFFER
    
    FREE_API --> RDMA_BUFFER
```

Sources: [gpu_mem_util.c:1-200](), [gpu_direct_rdma_access.c:1155-1212]()

## Build System Architecture

The build system uses conditional compilation to create different variants from the same codebase:

| Build Flag | Purpose | Libraries | Target Use Case |
|------------|---------|-----------|-----------------|
| `USE_CUDA=1` | Enable GPU support | `-lcuda` + RDMA libs | Client machines with GPU |
| `USE_CUDA=0` | CPU-only build | RDMA libs only | Server machines |
| `PRINT_LAT=1` | Enable latency measurement | Extended CQ support | Performance analysis |
| `PRINT_LAT=0` | Standard build | Standard CQ | Production deployment |

### Core Dependencies
- **RDMA Libraries**: `libverbs`, `lrdmacm`, `lmlx5` for InfiniBand/RoCE operations
- **CUDA Libraries**: `libcuda` for GPU memory management (conditional)
- **Source Components**: `gpu_direct_rdma_access.c`, `gpu_mem_util.c`, `utils.c`
- **Header Dependencies**: All `.h` files defining API interfaces

Sources: [Makefile:5-32](), [Makefile:37-45]()

## Task Execution Flow

```mermaid
sequenceDiagram
    participant Client as "Client Application"
    participant Server as "Server Application" 
    participant RDMA as "RDMA Engine"
    participant GPU as "GPU Memory"
    
    Client->>GPU: work_buffer_alloc()
    Client->>RDMA: rdma_buffer_reg()
    Client->>Server: TCP connection + buffer descriptor
    Server->>RDMA: rdma_submit_task()
    RDMA->>RDMA: rdma_create_ah_cached()
    RDMA->>RDMA: rdma_exec_task()
    RDMA-->>GPU: Direct RDMA Write/Read
    Server->>RDMA: rdma_poll_completions()
    Server->>Client: TCP completion notification
    Client->>RDMA: rdma_buffer_dereg()
    Client->>GPU: work_buffer_free()
```

Sources: [gpu_direct_rdma_access.c:1342-1419](), [gpu_direct_rdma_access.c:890-1006](), [gpu_direct_rdma_access.c:1422-1548]()

## Hardware Requirements and Configuration

### Required Hardware
- **NICs**: Mellanox ConnectX-5 or newer for DC QP support
- **GPUs**: NVIDIA GPUs with CUDA support (client-side optional)
- **Network**: InfiniBand or RoCE-capable Ethernet infrastructure

### Configuration Scripts
- **`arp_announce_conf.sh`**: Configures ARP handling for multi-homed RoCE networks
- **`map_pci_nic_gpu.sh`**: Discovers optimal GPU-NIC pairings on same PCI bridge for performance

Sources: [README.md:23-42](), [README.md:75-84]()

## Performance Characteristics

The system is optimized for high-performance data transfer with several key optimizations:

- **Zero-copy transfers**: Direct GPU-to-GPU memory access bypassing CPU
- **Address handle caching**: Reduces connection setup overhead using `khash` implementation
- **Polling-based completion**: Eliminates interrupt overhead for low latency
- **Scatter-gather support**: Efficient handling of non-contiguous memory regions through `iovec` arrays

Optional latency measurement capabilities provide detailed timing analysis across the entire RDMA operation pipeline when compiled with `PRINT_LAT=1`.

Sources: [gpu_direct_rdma_access.c:128](), [gpu_direct_rdma_access.c:1422-1548](), [gpu_direct_rdma_access.c:88-142]()

---

