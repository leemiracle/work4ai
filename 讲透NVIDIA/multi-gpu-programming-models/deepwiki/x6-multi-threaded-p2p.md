<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/multi-gpu-programming-models · extra page Multi-Threaded P2P · fetched 2026-10-26 -->

# Multi-Threaded P2P

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [multi_threaded_p2p/Makefile](multi_threaded_p2p/Makefile)
- [multi_threaded_p2p/jacobi.cu](multi_threaded_p2p/jacobi.cu)

</details>



## Purpose and Scope

This page documents the Multi-Threaded P2P implementation of the Jacobi solver in the multi-GPU programming models repository. This implementation uses CUDA's peer-to-peer (P2P) memory access capabilities to allow direct GPU-to-GPU data transfers without going through host memory. This approach eliminates the host memory bottleneck seen in previous implementations.

For information about the basic multi-threaded implementation using host memory, see [Multi-Threaded Copy](#3.1.2). For the optimized P2P version with deferred norm calculation, see [Multi-Threaded P2P Optimized](#3.2.2).

Sources: [multi_threaded_p2p/jacobi.cu:1-551]()

## Technical Overview

The Multi-Threaded P2P implementation divides the 2D Jacobi domain across multiple GPUs using OpenMP to manage one CPU thread per GPU device. The key optimization is the use of CUDA's GPUDirect P2P technology, which enables direct memory transfers between GPUs over the PCIe bus (or NVLink if available).

### Key Features

- Peer-to-peer direct memory access between GPUs
- OpenMP for multi-threading (one thread per GPU)
- Domain decomposition with direct halo exchange
- Multiple CUDA streams for managing computation and communication
- CUDA events for synchronization between devices

Sources: [multi_threaded_p2p/jacobi.cu:185-427]()

## Domain Decomposition

The 2D domain is partitioned horizontally into slices, with each GPU processing a chunk of rows. The chunking algorithm ensures optimal load balancing by distributing rows as evenly as possible.

```mermaid
flowchart TD
    subgraph "Domain Decomposition"
        direction TB
        domain["Full 2D Domain (nx × ny)"]
        
        subgraph "GPU 0"
            direction LR
            chunk0["Chunk 0 + Halos"]
        end
        
        subgraph "GPU 1"
            direction LR
            chunk1["Chunk 1 + Halos"]
        end
        
        subgraph "GPU n-1"
            direction LR
            chunkn["Chunk n-1 + Halos"]
        end
        
        domain --> chunk0
        domain --> chunk1
        domain --> chunkn
        
        chunk0 -- "P2P Transfer" --> chunk1
        chunk1 -- "P2P Transfer" --> chunk0
        chunk1 -- "P2P Transfer" --> chunkn
        chunkn -- "P2P Transfer" --> chunk1
    end
```

Domain calculation is performed using a load-balancing algorithm:
- Calculate base chunk size: `chunk_size_low = (ny - 2) / num_devices`
- Some GPUs may get one additional row: `chunk_size_high = chunk_size_low + 1`
- Determine how many GPUs get the smaller chunk: `num_ranks_low`
- Assign appropriate chunk size to each GPU based on its ID

Sources: [multi_threaded_p2p/jacobi.cu:209-224](), [multi_threaded_p2p/jacobi.cu:264-276]()

## P2P Memory Access Setup

Before computation begins, the implementation checks and enables P2P access between GPUs. This is a critical step that determines whether direct GPU-to-GPU communication is possible.

```mermaid
sequenceDiagram
    participant "Main Thread" as main
    participant "OpenMP Thread 0" as omp0
    participant "OpenMP Thread 1" as omp1
    participant "OpenMP Thread n-1" as ompn
    participant "GPU 0" as gpu0
    participant "GPU 1" as gpu1
    participant "GPU n-1" as gpun
    
    main->>omp0: Create thread
    main->>omp1: Create thread
    main->>ompn: Create thread
    
    omp0->>gpu0: Set device
    omp1->>gpu1: Set device
    ompn->>gpun: Set device
    
    omp0->>gpu0: Check P2P access to neighbors
    omp1->>gpu1: Check P2P access to neighbors
    ompn->>gpun: Check P2P access to neighbors
    
    omp0->>gpu0: Enable P2P access to neighbors
    omp1->>gpu1: Enable P2P access to neighbors
    ompn->>gpun: Enable P2P access to neighbors
    
    Note over omp0,gpun: Barrier synchronization
    
    omp0->>gpu0: Allocate memory
    omp1->>gpu1: Allocate memory
    ompn->>gpun: Allocate memory
    
    omp0->>gpu0: Initialize boundaries
    omp1->>gpu1: Initialize boundaries
    ompn->>gpun: Initialize boundaries
```

The code checks for P2P support between each GPU and its neighbors:
- Each GPU needs access to its top and bottom neighbors
- If P2P access is not available, the implementation reports an error
- P2P access is enabled using `cudaDeviceEnablePeerAccess()`

Sources: [multi_threaded_p2p/jacobi.cu:225-253]()

## Memory Management and Data Structures

The implementation uses several key data structures for computation and communication:

1. `a` - Current iteration data array on each GPU
2. `a_new` - Next iteration data array (shared via P2P)
3. `l2_norm_d` - Device memory for norm calculation
4. `compute_done` - CUDA events for signaling completion

The arrays are allocated with space for the actual computational domain plus halo regions for boundary exchange:

```mermaid
graph TD
    subgraph "Memory Layout Per GPU"
        a["a[dev_id]<br>nx × (chunk_size+2)"]
        a_new["a_new[dev_id]<br>nx × (chunk_size+2)"]
        
        subgraph "Memory Regions"
            top_halo["Top Halo<br>(from previous GPU)"]
            computation["Computation Region<br>(chunk_size rows)"]
            bottom_halo["Bottom Halo<br>(from next GPU)"]
        end
        
        a_new --> top_halo
        a_new --> computation
        a_new --> bottom_halo
    end
```

Sources: [multi_threaded_p2p/jacobi.cu:258-262](), [multi_threaded_p2p/jacobi.cu:170-171]()

## Computation and Communication Pattern

The implementation uses a specific pattern for computation and communication:

1. Each GPU waits for compute completion from neighboring GPUs
2. The Jacobi kernel updates the interior points and writes to halo regions via P2P
3. CUDA events signal completion of computation to other GPUs
4. Norm calculation is performed when needed
5. Arrays are swapped for the next iteration

```mermaid
flowchart LR
    subgraph "Computation Flow"
        direction TB
        wait["Wait for neighbors<br>cudaStreamWaitEvent()"]
        compute["Compute Jacobi iteration<br>jacobi_kernel"]
        signal["Signal completion<br>cudaEventRecord()"]
        norm["Calculate norm<br>(if needed)"]
        swap["Swap arrays<br>std::swap(a_new, a)"]
        
        wait --> compute
        compute --> signal
        signal --> norm
        norm --> swap
        swap --> wait
    end
    
    subgraph "GPU 0"
        direction LR
        top0["Top Halo"]
        data0["Data"]
        bottom0["Bottom Halo"]
    end
    
    subgraph "GPU 1"
        direction LR
        top1["Top Halo"]
        data1["Data"]
        bottom1["Bottom Halo"]
    end
    
    bottom0 <-- "P2P Write" --> top1
    top0 <-- "P2P Write" --> bottom1
```

The key innovation in this implementation is that GPUs directly write to the halo regions of their neighbors through P2P memory access, eliminating the need for explicit copy operations through host memory.

Sources: [multi_threaded_p2p/jacobi.cu:323-363](), [multi_threaded_p2p/jacobi.cu:98-139]()

## Jacobi Kernel Implementation

The Jacobi kernel performs the main computation and handles the direct P2P memory updates:

```mermaid
graph TD
    subgraph "jacobi_kernel"
        direction TB
        init["Initialize local variables"]
        bounds["Check boundary conditions"]
        compute["Compute new value<br>(5-point stencil)"]
        write_local["Write to local array"]
        write_top["Write to top neighbor<br>(if at top boundary)"]
        write_bottom["Write to bottom neighbor<br>(if at bottom boundary)"]
        norm["Calculate norm contribution<br>(if needed)"]
        
        init --> bounds
        bounds --> compute
        compute --> write_local
        write_local --> write_top
        write_top --> write_bottom
        write_bottom --> norm
    end
```

Key aspects of the kernel:
- Calculates new values using the 5-point stencil pattern
- Directly writes to neighboring GPU memory for halo regions
- Optionally calculates the norm contribution
- Uses CUB library for efficient block reduction (if available)

Sources: [multi_threaded_p2p/jacobi.cu:98-139]()

## Synchronization Mechanisms

The implementation uses several synchronization mechanisms to coordinate work:

1. **CUDA Events**: Used to signal completion of computation to neighboring GPUs
   - `compute_done` events are recorded after kernel execution
   - Neighboring GPUs wait on these events before starting computation

2. **OpenMP Barriers**: Used to synchronize CPU threads at critical points
   - Before checking global convergence
   - Before accessing shared data structures

3. **Stream Synchronization**: Used to ensure memory operations are complete
   - `cudaStreamSynchronize()` called when waiting for norm calculation

Sources: [multi_threaded_p2p/jacobi.cu:328-341](), [multi_threaded_p2p/jacobi.cu:344-354]()

## Full Execution Flow

The complete execution flow combines all these elements:

```mermaid
flowchart TD
    start["Start"]
    init["Initialize OpenMP threads<br>One thread per GPU"]
    check_p2p["Check P2P access between GPUs"]
    alloc["Allocate memory on each GPU"]
    boundary["Initialize boundary conditions"]
    streams["Create CUDA streams and events"]
    
    iter_start["Start iterations"]
    
    memset["Reset norm counter<br>cudaMemsetAsync"]
    wait["Wait for neighbor events<br>cudaStreamWaitEvent"]
    kernel["Execute Jacobi kernel<br>Direct P2P updates"]
    record["Record completion event<br>cudaEventRecord"]
    
    calc_norm{"Calculate norm?"}
    copy_norm["Copy norm to host<br>cudaMemcpyAsync"]
    sync["Synchronize and reduce norm"]
    check_conv{"Converged?"}
    
    swap["Swap arrays<br>std::swap(a_new, a)"]
    cleanup["Clean up resources"]
    end_flow["End"]
    
    start --> init
    init --> check_p2p
    check_p2p --> alloc
    alloc --> boundary
    boundary --> streams
    streams --> iter_start
    
    iter_start --> memset
    memset --> wait
    wait --> kernel
    kernel --> record
    record --> calc_norm
    
    calc_norm -- "Yes" --> copy_norm
    calc_norm -- "No" --> swap
    
    copy_norm --> sync
    sync --> check_conv
    
    check_conv -- "Yes" --> cleanup
    check_conv -- "No" --> swap
    
    swap --> memset
    cleanup --> end_flow
```

Sources: [multi_threaded_p2p/jacobi.cu:185-427]()

## Build and Execution

The implementation is built using NVCC with OpenMP support and can be compiled with optional CUB library support for optimized reductions.

Relevant build flags:
- `-fopenmp`: Enable OpenMP support
- `-DHAVE_CUB`: Enable CUB library optimizations
- `-DUSE_NVTX`: Enable NVIDIA Tools Extension for profiling

Sources: [multi_threaded_p2p/Makefile:1-34]()

## Performance Considerations

The Multi-Threaded P2P implementation offers several performance advantages:

1. **Eliminates Host Memory Bottleneck**: By enabling direct GPU-to-GPU transfers, it avoids the costly round-trip through host memory seen in host-based implementations.

2. **Reduces PCIe Traffic**: Data transfers occur directly between GPUs over the PCIe bus (or NVLink if available).

3. **Overlap Potential**: The use of separate CUDA streams provides potential for overlapping computation and communication.

The implementation reports performance metrics including:
- Single-GPU baseline runtime
- Multi-GPU runtime
- Speedup relative to single-GPU
- Parallel efficiency

Sources: [multi_threaded_p2p/jacobi.cu:376-406]()

## Limitations

There are a few limitations to be aware of:

1. **P2P Compatibility**: Not all GPU combinations support P2P access. The code checks this but will fail if P2P is not supported.

2. **NUMA Considerations**: On multi-socket systems, GPUs on different CPU sockets may have reduced P2P performance.

3. **No Computation-Communication Overlap**: Unlike the [Multi-Threaded P2P Optimized](#3.2.2) version, this implementation doesn't actively overlap computation and communication.

Sources: [multi_threaded_p2p/jacobi.cu:227-250]()

## Summary

The Multi-Threaded P2P implementation represents a significant performance improvement over host-based communication methods by enabling direct GPU-to-GPU memory transfers. It uses OpenMP for CPU thread management and CUDA's peer-to-peer memory access capabilities to efficiently distribute and solve the Jacobi problem across multiple GPUs.

This approach eliminates the host memory bottleneck and reduces PCIe traffic, resulting in better scalability as the number of GPUs increases. However, it requires hardware support for P2P access between the GPUs used in the computation.

---

