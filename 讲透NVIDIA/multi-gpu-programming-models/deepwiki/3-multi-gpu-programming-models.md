<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/multi-gpu-programming-models · page 3 Multi-GPU Programming Models · fetched 2026-10-26 -->

# Multi-GPU Programming Models

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [bench.sh](bench.sh)
- [nccl/Makefile](nccl/Makefile)
- [nccl/jacobi_kernels.cu](nccl/jacobi_kernels.cu)
- [nccl_overlap/Makefile](nccl_overlap/Makefile)

</details>



This document provides an overview of the multi-GPU programming models implemented in the repository. These models demonstrate different approaches for distributing the Jacobi solver algorithm across multiple GPUs, each with distinct characteristics, performance trade-offs, and implementation complexity. For information about the mathematical background, see [Jacobi Method Theory](#2).

## Purpose and Scope

The repository contains multiple implementations of a Jacobi solver using different multi-GPU programming paradigms. Each implementation solves the same problem but uses a different approach to:

1. Distribute data across multiple GPUs
2. Manage communication between GPUs
3. Synchronize computations
4. Optimize performance through various techniques

This page provides a high-level overview of the programming models, while subsequent pages explore each model in detail.

Sources: [README.md:1-15]()

## Multi-GPU Programming Model Categories

The implementations in the repository are organized into five major categories:

```mermaid
graph TD
    A["Multi-GPU Programming Models"] --> B["Host-Based Communication"]
    A --> C["Direct GPU-to-GPU Communication"]
    A --> D["MPI-Based Communication"]
    A --> E["NCCL-Based Communication"]
    A --> F["NVSHMEM-Based Communication"]
    
    B --> B1["single_threaded_copy"]
    B --> B2["multi_threaded_copy"]
    B --> B3["multi_threaded_copy_overlap"]
    
    C --> C1["multi_threaded_p2p"]
    C --> C2["multi_threaded_p2p_opt"]
    C --> C3["multi_threaded_um"]
    C --> C4["multi_node_p2p"]
    
    D --> D1["mpi"]
    D --> D2["mpi_overlap"]
    
    E --> E1["nccl"]
    E --> E2["nccl_overlap"]
    E --> E3["nccl_graphs"]
    
    F --> F1["nvshmem"]
```

Sources: [README.md:1-15]()

### Communication Abstraction Levels

The implementations demonstrate progressively more sophisticated communication mechanisms, from basic memory transfers to advanced distributed memory models:

```mermaid
flowchart TD
    A["Communication Abstraction Levels"]
    
    A --> B["Level 1: Direct Memory Transfers"]
    A --> C["Level 2: Messaging Protocols"]
    A --> D["Level 3: Distributed Memory Models"]
    
    B --> B1["cudaMemcpy"]
    B --> B2["GPUDirect P2P"]
    
    C --> C1["MPI"]
    C --> C2["NCCL Collectives"]
    
    D --> D1["Unified Memory"]
    D --> D2["NVSHMEM PGAS"]
    
    style A stroke-width:2px
```

Sources: [README.md:2-15]()

## Host-Based Communication Models

The host-based communication models use the CPU as an intermediary for transferring data between GPUs. Data must be copied from one GPU to the host memory and then to another GPU.

### Single-Threaded Copy

The simplest approach uses sequential `cudaMemcpy` operations managed by a single CPU thread to transfer halo regions between GPUs.

Key characteristics:
- Uses a single thread for managing all data transfers
- Simple implementation but limited scaling
- Becomes a bottleneck as GPU count increases

For more details, see [Single-Threaded Copy](#3.1.1).

### Multi-Threaded Copy

Improves upon the single-threaded approach by using OpenMP to parallelize the data transfers.

Key characteristics:
- One CPU thread per GPU for managing transfers
- Better scaling than single-threaded version
- Still requires host memory as intermediary

For more details, see [Multi-Threaded Copy](#3.1.2).

### Multi-Threaded Copy with Overlap

Further improves performance by overlapping computation and communication.

Key characteristics:
- Uses CUDA streams to execute communication and computation concurrently
- Interior points computed while boundary data transfers occur
- Reduces the effective communication overhead

For more details, see [Multi-Threaded Copy with Overlap](#3.1.3).

Sources: [README.md:3-5](), [bench.sh:95-155]()

## Direct GPU-to-GPU Communication Models

These models leverage hardware capabilities to enable direct communication between GPUs without host involvement, significantly reducing communication overhead.

```mermaid
graph TD
    A["GPU 0"] --> |"Direct Memory Access"| B["GPU 1"]
    B --> |"Direct Memory Access"| A
    
    C["Host Memory"] -.-> |"Not Used for\nGPU-GPU Transfer"| A
    C -.-> |"Not Used for\nGPU-GPU Transfer"| B
    
    subgraph "GPUDirect P2P Transfer"
        A
        B
    end
    
    subgraph "Host Memory"
        C
    end
```

Sources: [README.md:6-8]()

### Multi-Threaded P2P

Uses NVIDIA's GPUDirect Peer-to-Peer (P2P) technology to enable direct memory access between GPUs.

Key characteristics:
- Direct access to remote GPU memory
- Eliminates host memory copies
- Requires peer mapping capability between GPUs
- Significantly lower latency than host-based transfers

For more details, see [Multi-Threaded P2P](#3.2.1).

### Multi-Threaded P2P Optimized

Extends the P2P model with optimized norm calculation.

Key characteristics:
- Delayed norm calculation to reduce synchronization points
- Improved performance through fewer global synchronizations
- Same direct memory access benefits as basic P2P

For more details, see [Multi-Threaded P2P Optimized](#3.2.2).

### Unified Memory

Uses CUDA Unified Memory to automatically manage data transfers between GPUs.

Key characteristics:
- Simplified programming model
- Hardware-managed page migration
- Transparent peer mappings
- Can be less performant than explicit P2P in some cases

For more details, see [Unified Memory](#3.2.3).

### Multi-Node P2P

Advanced implementation for cross-node P2P communication.

Key characteristics:
- Uses low-level CUDA Driver APIs
- Virtual Memory Management and Multicast Object Management
- Enables P2P communication across compute nodes
- Demonstrates techniques used internally by libraries like NCCL and NVSHMEM

For more details, see [Multi-Node P2P](#3.2.4).

Sources: [README.md:6-8](), [README.md:15]()

## MPI-Based Communication Models

These models use Message Passing Interface (MPI) for inter-GPU communication, particularly beneficial in distributed memory environments.

```mermaid
graph TD
    A["MPI Process 0\nwith GPU 0"] --> |"MPI_Send/MPI_Recv"| B["MPI Process 1\nwith GPU 1"]
    B --> |"MPI_Send/MPI_Recv"| A
    
    A --> |"cudaMemcpy"| A1["GPU 0 Memory"]
    B --> |"cudaMemcpy"| B1["GPU 1 Memory"]
    
    subgraph "Node 0"
        A
        A1
    end
    
    subgraph "Node 1"
        B
        B1
    end
```

Sources: [README.md:9-10]()

### Basic MPI Implementation

Uses CUDA-aware MPI to facilitate GPU-to-GPU communication.

Key characteristics:
- One MPI process per GPU
- CUDA-aware MPI for direct GPU buffer operations
- Works across compute nodes in a cluster
- Synchronous communication pattern

For more details, see [MPI Implementation](#3.3.1).

### MPI with Computation-Communication Overlap

Enhances the basic MPI implementation with overlapped communication and computation.

Key characteristics:
- Uses non-blocking MPI operations
- Dedicated CUDA streams for boundary exchanges
- Interior computation proceeds while boundaries are being exchanged
- Optional high-priority streams for boundary operations

For more details, see [MPI with Computation-Communication Overlap](#3.3.2).

Sources: [README.md:9-10](), [bench.sh:193-209]()

## NCCL-Based Communication Models

These models leverage NVIDIA's Collective Communications Library (NCCL) for optimized GPU-to-GPU communication, particularly efficient for collective operations.

```mermaid
graph TB
    A["MPI for Process Initialization"]
    B["NCCL for GPU-to-GPU Communication"]
    
    A --> B
    
    B --> C["Point-to-Point\nOperations"]
    B --> D["Collective\nOperations"]
    
    C --> C1["ncclSend/ncclRecv"]
    D --> D1["ncclAllReduce"]
    
    E["GPU 0"] <-->|"ncclSend/ncclRecv"| F["GPU 1"]
    E <-->|"ncclSend/ncclRecv"| G["GPU 2"]
    F <-->|"ncclSend/ncclRecv"| G
    
    E -->|"Contributes"| H["ncclAllReduce"]
    F -->|"Contributes"| H
    G -->|"Contributes"| H
    
    H -->|"Result"| E
    H -->|"Result"| F
    H -->|"Result"| G
```

Sources: [README.md:11-13](), [nccl/Makefile:1-44]()

### Basic NCCL Implementation

Uses NCCL for efficient GPU-to-GPU data exchange.

Key characteristics:
- Optimized communication paths based on hardware topology
- Uses MPI for process initialization
- Efficient handling of both point-to-point and collective operations
- Advanced support for NVLINK interconnect

For more details, see [NCCL Implementation](#3.4.1).

### NCCL with Overlap

Combines NCCL with computation-communication overlap.

Key characteristics:
- Uses NCCL's asynchronous operations
- Boundary exchanges occur concurrently with interior computation
- Reduced overall execution time
- Optional user buffer registration for reduced memory copies

For more details, see [NCCL with Overlap](#3.4.2).

### NCCL with CUDA Graphs

Integrates CUDA Graphs with NCCL for reduced kernel launch overhead.

Key characteristics:
- Captures sequence of CUDA operations in a graph
- Reduces CPU overhead for kernel launches
- Allows the driver to optimize execution
- Requires CUDA 11.7+ and newer NCCL versions

For more details, see [NCCL with CUDA Graphs](#3.4.3).

Sources: [README.md:11-13](), [nccl/Makefile:1-44](), [nccl_overlap/Makefile:1-44](), [nccl/jacobi_kernels.cu:1-116]()

## NVSHMEM-Based Communication

NVSHMEM implements a Partitioned Global Address Space (PGAS) programming model specifically for GPUs.

```mermaid
graph TD
    A["GPU 0 Memory"] --- B["GPU 1 Memory"]
    B --- C["GPU 2 Memory"]
    C --- D["GPU 3 Memory"]
    D --- A
    
    subgraph "Virtual Unified Memory Space (Symmetric Memory)"
        A
        B
        C
        D
    end
    
    E["GPU 0"] -->|"nvshmem_put"| B
    F["GPU 1"] -->|"nvshmem_put"| C
    G["GPU 2"] -->|"nvshmem_put"| D
    H["GPU 3"] -->|"nvshmem_put"| A
    
    I["GPU Threads"] -->|"nvshmemx_barrier_all_on_stream"| I
    I -->|"neighborhood_sync"| I
```

Sources: [README.md:14](), [bench.sh:238-258]()

Key characteristics:
- One-sided communication operations
- Remote memory access without remote process involvement
- GPU-initiated communication
- Global synchronization primitives
- Optional neighborhood synchronization for better performance
- Optional computation-communication overlap
- Block cooperative communication option

Advanced features:
- Neighborhood synchronization for reduced synchronization scope
- Delayed norm execution similar to P2P optimized version
- Configurable symmetric memory size

For more details, see [NVSHMEM-Based Communication](#3.5).

## Implementation and Performance Considerations

When choosing between multi-GPU programming models, consider:

| Programming Model | Advantages | Disadvantages | Best Use Cases |
|-------------------|------------|---------------|----------------|
| Host-Based Communication | Simple implementation<br>Works with any GPU configuration | Host memory bottleneck<br>Higher latency | Small scale (2-4 GPUs)<br>When P2P not available |
| Direct P2P | Low latency<br>High bandwidth | Requires P2P capability between GPUs<br>Limited to single node | Single node with NVLink<br>High performance requirements |
| MPI-Based | Works across multiple nodes<br>Portable standard | Complex programming model<br>May require CUDA-aware MPI | Multi-node clusters<br>HPC environments |
| NCCL-Based | Optimized for NVIDIA GPUs<br>Collective operations support | NVIDIA-specific<br>Requires recent drivers | Deep learning<br>Applications with collectives |
| NVSHMEM-Based | One-sided communication<br>Low synchronization overhead | Requires symmetric memory allocation<br>Newer technology | Irregular communication patterns<br>Fine-grained communication |

Sources: [README.md:1-15](), [bench.sh:1-258]()

## Programming Model Evolution Path

The implementations in this repository demonstrate a natural evolution of multi-GPU programming techniques, from simple to more sophisticated approaches:

```mermaid
graph LR
    A["Single-threaded\ncudaMemcpy"] --> B["Multi-threaded\ncudaMemcpy"]
    B --> C["Multi-threaded\nwith overlap"]
    C --> D["GPUDirect P2P"]
    D --> E["Optimized P2P"]
    
    F["Basic MPI"] --> G["MPI with overlap"]
    G --> H["NCCL"]
    H --> I["NCCL with overlap"]
    I --> J["NCCL with\nCUDA Graphs"]
    
    K["Unified Memory"] --> L["NVSHMEM"]
    
    style A stroke-width:1px
    style L stroke-width:2px
    style J stroke-width:2px
```

Sources: [README.md:1-15](), [bench.sh:1-258]()

## Summary of Required Technologies

The multi-GPU programming models in this repository rely on several key technologies:

- **CUDA**: Foundation for all implementations (version 11.0+ recommended)
- **OpenMP**: Required for multi-threaded implementations
- **MPI**: Required for distributed implementations (CUDA-aware MPI recommended)
- **NCCL**: Required for NCCL-based implementations (version 2.8+)
- **NVSHMEM**: Required for NVSHMEM implementation (version 0.4.1+)
- **CUDA Graphs**: Required for NCCL with CUDA Graphs (CUDA 11.7+)
- **CUDA Driver APIs**: Required for multi-node P2P (CUDA 12.4+)

For specific version requirements and compatibility information, see [Building and Running](#5).

Sources: [README.md:24-31]()

## Benchmarking

The repository includes a benchmarking script (`bench.sh`) that can evaluate the performance of all implementations with various GPU configurations. The script:

- Controls GPU visibility for different test configurations
- Manages thread and process pinning for consistent results
- Collects performance results in CSV format
- Automatically finds the best result from multiple runs

For detailed benchmarking results and comparative analysis, see [Performance Comparison and Benchmarking](#4).

Sources: [bench.sh:1-258]()

---

