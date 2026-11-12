<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/multi-gpu-programming-models · extra page Multi-Node P2P · fetched 2026-10-26 -->

# Multi-Node P2P

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [multi_node_p2p/Makefile](multi_node_p2p/Makefile)
- [multi_node_p2p/jacobi.cpp](multi_node_p2p/jacobi.cpp)
- [multi_node_p2p/jacobi_kernels.cu](multi_node_p2p/jacobi_kernels.cu)

</details>



This page documents the Multi-Node P2P (Peer-to-Peer) implementation of the Jacobi solver, which enables direct GPU-to-GPU communication across multiple compute nodes. Unlike single-node multi-GPU implementations which use GPUDirect P2P within a node (see [Multi-Threaded P2P](#3.2.1)), this implementation leverages CUDA Driver APIs with fabric memory handles to establish direct memory access between GPUs across different physical machines.

## Architecture Overview

The Multi-Node P2P implementation combines MPI for process coordination with CUDA Driver APIs for direct GPU memory access across physical nodes. This approach eliminates the need for staging data through host memory when communicating across node boundaries.

```mermaid
flowchart TD
    subgraph "Node 1"
        mpi1["MPI Process"]
        gpu1["GPU Memory"]
        mpi1 -- "CUDA Driver API" --> gpu1
    end

    subgraph "Node 2"
        mpi2["MPI Process"]
        gpu2["GPU Memory"]
        mpi2 -- "CUDA Driver API" --> gpu2
    end

    mpi1 <--> mpi2
    gpu1 <-- "Direct P2P via Fabric Handles" --> gpu2
```

Sources: [multi_node_p2p/jacobi.cpp:290-325]()

## Fabric Memory System

The key innovation in this implementation is the use of CUDA fabric memory handles to enable direct GPU memory access across nodes.

```mermaid
sequenceDiagram
    participant GPU1 as "GPU on Node 1"
    participant Process1 as "MPI Process on Node 1"
    participant Process2 as "MPI Process on Node 2"
    participant GPU2 as "GPU on Node 2"

    Note over Process1: Allocate GPU Memory
    Process1->>GPU1: 1. Create memory allocation (cuMemCreate)
    Process1->>Process1: 2. Export to fabric handle (cuMemExportToShareableHandle)
    Process1->>Process1: 3. Reserve address space (cuMemAddressReserve)
    Process1->>GPU1: 4. Map allocation (cuMemMap)
    Process1->>GPU1: 5. Set memory access (cuMemSetAccess)
    
    Process1->>Process2: Exchange fabric handles via MPI
    
    Note over Process2: Import remote memory
    Process2->>Process2: 1. Import from fabric handle (cuMemImportFromShareableHandle)
    Process2->>Process2: 2. Reserve address space (cuMemAddressReserve)
    Process2->>GPU2: 3. Map allocation (cuMemMap)
    Process2->>GPU2: 4. Set memory access (cuMemSetAccess)
    
    Note over GPU1,GPU2: Direct memory access established
    GPU1-->>GPU2: Direct memory access via mapped addresses
    GPU2-->>GPU1: Direct memory access via mapped addresses
```

Sources: [multi_node_p2p/jacobi.cpp:182-287](), [multi_node_p2p/jacobi.cpp:382-453]()

## Key Components

### 1. Fabric Memory Allocation and Sharing

The implementation uses a `fabric_mem` struct to encapsulate the details of allocatable and shareable GPU memory:

```mermaid
classDiagram
    class fabric_mem {
        CUdeviceptr ptr
        size_t size
        size_t aligned_size
        size_t granularity
        int device_id
        CUmemGenericAllocationHandle generic_handle
        CUmemFabricHandle fabric_handle
        CUdeviceptr ptr_top
        CUmemGenericAllocationHandle generic_handle_top
        CUdeviceptr ptr_bottom
        CUmemGenericAllocationHandle generic_handle_bottom
    }
```

The memory allocation process follows these steps:
1. Create a CUDA memory allocation (cuMemCreate)
2. Export the allocation to a shareable fabric handle (cuMemExportToShareableHandle)
3. Reserve an address range (cuMemAddressReserve)
4. Map the allocation into the address range (cuMemMap)
5. Set access permissions (cuMemSetAccess)

Sources: [multi_node_p2p/jacobi.cpp:182-194](), [multi_node_p2p/jacobi.cpp:213-252]()

### 2. Peer Memory Mapping

To enable direct access to peer GPUs' memory, the implementation:
1. Reserves local address ranges for the remote memory
2. Maps the remote memory into those address ranges
3. Sets appropriate access permissions

This process allows the local GPU to directly read from and write to the remote GPU's memory.

Sources: [multi_node_p2p/jacobi.cpp:260-287]()

### 3. MPI Process Coordination

MPI serves several crucial roles in this implementation:
- Identifying process ranks and distributing work
- Exchanging fabric memory handles between nodes
- Coordinating algorithm phases across nodes
- Optionally reducing norm values for convergence checks

Sources: [multi_node_p2p/jacobi.cpp:290-332](), [multi_node_p2p/jacobi.cpp:416-425]()

### 4. Optimized P2P Jacobi Kernel

The Jacobi kernel is specifically designed to directly write halo data to peer GPU memory:

```mermaid
flowchart LR
    subgraph "GPU on Node 1"
        a1["Array a"]
        a_new1["Array a_new"]
    end
    
    subgraph "GPU on Node 2"
        a2["Array a"]
        a_new2["Array a_new"]
    end
    
    a1 --> compute1["Jacobi Kernel"]
    compute1 --> a_new1
    compute1 --> a_new2_halo["Array a_new_top on Node 2"]
    
    a2 --> compute2["Jacobi Kernel"]
    compute2 --> a_new2
    compute2 --> a_new1_halo["Array a_new_bottom on Node 1"]
```

The `jacobi_p2p_kernel` performs three key operations:
1. Computes new values for the local domain
2. Directly writes boundary data to the mapped memory of neighboring GPUs
3. Calculates partial L2 norm for convergence checks when needed

Sources: [multi_node_p2p/jacobi_kernels.cu:126-183]()

## Multicast Reduction Optimization

An optional optimization uses CUDA Multicast Objects for efficient cross-node reductions of the L2 norm:

```mermaid
flowchart TD
    subgraph "Node 1"
        uc1["UC Pointer"]
        mc1["MC Pointer"]
        uc1 -->|"Write"| mc1
        mc1 -->|"Read"| uc1
    end
    
    subgraph "Node 2"
        uc2["UC Pointer"]
        mc2["MC Pointer"]
        uc2 -->|"Write"| mc2
        mc2 -->|"Read"| uc2
    end
    
    subgraph "Node 3"
        uc3["UC Pointer"]
        mc3["MC Pointer"]
        uc3 -->|"Write"| mc3
        mc3 -->|"Read"| uc3
    end
    
    mc1 <-->|"Multicast"| mc2
    mc2 <-->|"Multicast"| mc3
    mc3 <-->|"Multicast"| mc1
```

This optimization uses:
1. A paired unicast (UC) and multicast (MC) pointer structure
2. A specialized kernel for all-reduce operations using multicast
3. Atomic operations on the GPU to coordinate barrier synchronization

When enabled, this eliminates the need for MPI_Allreduce operations for convergence checking.

Sources: [multi_node_p2p/jacobi.cpp:467-543](), [multi_node_p2p/jacobi_kernels.cu:185-233]()

## Halo Exchange Implementation

The Multi-Node P2P implementation uses a direct halo exchange pattern where each GPU kernel writes its boundary data directly to the memory of its neighbors:

```mermaid
flowchart LR
    subgraph "Node 0"
        a0("a[chunk 0]")
        a_new0("a_new[chunk 0]")
    end
    
    subgraph "Node 1"
        a1("a[chunk 1]")
        a_new1("a_new[chunk 1]")
    end
    
    subgraph "Node 2"
        a2("a[chunk 2]")
        a_new2("a_new[chunk 2]")
    end
    
    kernel0["jacobi_p2p_kernel"] -- "Write top boundary" --> a_new2
    kernel0["jacobi_p2p_kernel"] -- "Write bottom boundary" --> a_new1
    
    kernel1["jacobi_p2p_kernel"] -- "Write top boundary" --> a_new0
    kernel1["jacobi_p2p_kernel"] -- "Write bottom boundary" --> a_new2
    
    kernel2["jacobi_p2p_kernel"] -- "Write top boundary" --> a_new1
    kernel2["jacobi_p2p_kernel"] -- "Write bottom boundary" --> a_new0
    
    a0 --> kernel0
    a1 --> kernel1
    a2 --> kernel2
    
    kernel0 --> a_new0
    kernel1 --> a_new1
    kernel2 --> a_new2
```

Key aspects:
1. Each process sets up peer memory mappings to its top and bottom neighbors
2. The kernel directly writes boundary data to these mapped regions
3. A cyclic boundary pattern ensures all processes have neighbors

Sources: [multi_node_p2p/jacobi_kernels.cu:142-153](), [multi_node_p2p/jacobi.cpp:416-453]()

## Implementation Details

### Data Distribution

The implementation divides the computational domain into roughly equal chunks across all available MPI ranks:

```mermaid
flowchart TD
    domain["Full Domain nx × ny"]
    chunk0["Chunk 0 (Rank 0): nx × chunk_size"]
    chunk1["Chunk 1 (Rank 1): nx × chunk_size"]
    chunkN["Chunk N (Rank N): nx × chunk_size"]
    
    domain --> |"Divide"| chunk0
    domain --> |"Divide"| chunk1
    domain --> |"Divide"| chunkN
    
    classDef boundary fill:#f9f9f9,stroke:#333
    class boundary boundary
```

Each chunk includes additional halo regions for the boundary data, which are updated through direct memory access to neighboring GPUs.

Sources: [multi_node_p2p/jacobi.cpp:364-401]()

### Algorithm Flow

The main iteration loop follows this pattern:

1. Optionally reset the L2 norm accumulator
2. Launch the `jacobi_p2p_kernel` to compute new values and directly update neighbor halos
3. If norm checking is enabled, either:
   - Use the multicast reduction to compute the global norm, or
   - Use MPI_Allreduce to compute the global norm
4. Swap pointers for the next iteration
5. Check for convergence or maximum iterations

Sources: [multi_node_p2p/jacobi.cpp:561-601]()

### Hardware Requirements

The implementation requires specific GPU capabilities:

1. Support for fabric handle export/import (CU_DEVICE_ATTRIBUTE_HANDLE_TYPE_FABRIC_SUPPORTED)
2. For the multicast optimization, support for multicast objects (CU_DEVICE_ATTRIBUTE_MULTICAST_SUPPORTED)

These features are available on NVIDIA GPUs supporting the necessary driver extensions.

Sources: [multi_node_p2p/jacobi.cpp:322-356]()

## Key Advantages

The Multi-Node P2P implementation offers several advantages compared to traditional MPI-based approaches:

1. **Reduced Communication Overhead**: Direct GPU-to-GPU communication eliminates host memory staging
2. **Simplified Programming Model**: The application can treat remote GPU memory similar to local GPU memory
3. **Overlap of Computation and Communication**: Direct memory writes can be overlapped with computation
4. **Optional Multicast Optimization**: Efficient cross-node reductions without MPI involvement

These advantages make this implementation particularly well-suited for large-scale multi-node GPU clusters with high-speed interconnects.

Sources: [multi_node_p2p/jacobi.cpp:561-601](), [multi_node_p2p/jacobi_kernels.cu:126-168]()

---

