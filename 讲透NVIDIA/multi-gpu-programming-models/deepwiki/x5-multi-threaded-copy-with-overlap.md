<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/multi-gpu-programming-models · extra page Multi-Threaded Copy with Overlap · fetched 2026-10-26 -->

# Multi-Threaded Copy with Overlap

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [multi_threaded_copy_overlap/jacobi.cu](multi_threaded_copy_overlap/jacobi.cu)

</details>



## Purpose and Scope

This document describes the Multi-Threaded Copy with Overlap implementation of the Jacobi solver. This implementation extends the [Multi-Threaded Copy](#3.1.2) approach by adding computation-communication overlap to improve performance. While the basic multi-threaded copy implementation uses sequential communication and computation, this version uses multiple CUDA streams to overlap these operations, hiding communication latency behind useful computation.

Sources: [multi_threaded_copy_overlap/jacobi.cu:1-5]()

## Overview

The Multi-Threaded Copy with Overlap implementation uses a combination of:

1. OpenMP for thread-level parallelism (one thread per GPU)
2. CUDA streams for managing overlapped operations
3. CUDA events for fine-grained synchronization
4. Asynchronous memory transfers between GPUs
5. Stream priorities to ensure proper ordering of operations

This approach allows halo exchanges to occur simultaneously with computation, reducing the overall execution time by hiding data transfer latency.

Sources: [multi_threaded_copy_overlap/jacobi.cu:173-186](), [multi_threaded_copy_overlap/jacobi.cu:237-254]()

## Execution Model

### Domain Decomposition and Thread Assignment

The implementation divides the computational domain among available GPUs, with each OpenMP thread managing one GPU. The domain is split along the y-dimension, with each GPU responsible for a chunk of rows.

```mermaid
flowchart TD
    subgraph "Domain Decomposition"
        direction TB
        
        subgraph "GPU0"
            direction TB
            g0_top["Top Halo (from GPU N-1)"]
            g0_interior["Interior Points"]
            g0_bottom["Bottom Halo (from GPU1)"]
        end
        
        subgraph "GPU1"
            direction TB
            g1_top["Top Halo (from GPU0)"]
            g1_interior["Interior Points"]
            g1_bottom["Bottom Halo (from GPU2)"]
        end
        
        subgraph "GPU N-1"
            direction TB
            gn_top["Top Halo (from GPU N-2)"]
            gn_interior["Interior Points"]
            gn_bottom["Bottom Halo (from GPU0)"]
        end
    end
    
    g0_bottom --- g1_top
    g1_bottom --- gn_top
    gn_bottom --- g0_top
```

Sources: [multi_threaded_copy_overlap/jacobi.cu:194-229]()

### Stream and Event Organization

The implementation uses three CUDA streams per GPU to manage different operations with appropriate priorities:

```mermaid
flowchart LR
    subgraph "GPU Streams and Events"
        direction TB
        
        subgraph "CUDA Streams"
            compute["compute_stream
            (lower priority)"]
            push_top["push_top_stream
            (higher priority)"]
            push_bottom["push_bottom_stream
            (higher priority)"]
        end
        
        subgraph "CUDA Events"
            reset_event["reset_l2norm_done"]
            top_events["push_top_done[2][N]
            (double buffered)"]
            bottom_events["push_bottom_done[2][N]
            (double buffered)"]
        end
    end
    
    compute --> reset_event
    push_top --> top_events
    push_bottom --> bottom_events
```

Sources: [multi_threaded_copy_overlap/jacobi.cu:237-254](), [multi_threaded_copy_overlap/jacobi.cu:167-169]()

## Implementation Details

### Stream Priority Management

The implementation uses CUDA stream priorities to ensure that communication operations (halo exchanges) have higher priority than computation operations. This helps minimize the latency of data transfers between GPUs.

```mermaid
flowchart TD
    subgraph "Stream Priority Assignment"
        getPriority["cudaDeviceGetStreamPriorityRange()"]
        computeStream["compute_stream
        (lowest priority)"]
        commStreams["push_top_stream & push_bottom_stream
        (highest priority)"]
        
        getPriority --> |"priorityRange"| computeStream
        getPriority --> |"priorityRange"| commStreams
    end
```

Sources: [multi_threaded_copy_overlap/jacobi.cu:237-246]()

### Peer Access Configuration

To allow direct memory transfers between GPUs, the implementation enables peer access between adjacent GPUs:

```mermaid
flowchart TD
    subgraph "GPU Peer Access Configuration"
        checkPeer["cudaDeviceCanAccessPeer()"]
        enablePeer["cudaDeviceEnablePeerAccess()"]
        
        checkPeer --> |"canAccessPeer == 1"| enablePeer
    end
```

Sources: [multi_threaded_copy_overlap/jacobi.cu:259-272]()

### Main Iteration Loop

The main iteration loop implements the overlapped computation and communication pattern:

```mermaid
flowchart TD
    subgraph "Iteration Loop with Overlap"
        reset["Reset Norm Counter"]
        
        subgraph "Computation"
            bulkComp["Compute Interior Points
            (on compute_stream)"]
            topComp["Compute Top Boundary
            (on push_top_stream)"]
            bottomComp["Compute Bottom Boundary
            (on push_bottom_stream)"]
        end
        
        subgraph "Communication"
            topExchange["Send Top Boundary to Top Neighbor
            (on push_top_stream)"]
            bottomExchange["Send Bottom Boundary to Bottom Neighbor
            (on push_bottom_stream)"]
        end
        
        normCalc["Calculate Global Norm (if needed)"]
        swap["Swap Buffers (a and a_new)"]
    end
    
    reset --> bulkComp & topComp & bottomComp
    topComp --> topExchange
    bottomComp --> bottomExchange
    bulkComp & topExchange & bottomExchange --> normCalc
    normCalc --> swap
```

Sources: [multi_threaded_copy_overlap/jacobi.cu:312-386]()

## Key Algorithm Components

### Synchronization Pattern

A key aspect of this implementation is the careful synchronization between computation and communication operations to ensure correctness while maximizing overlap:

1. Each iteration waits for halo exchanges from the previous iteration to complete
2. Boundary computations wait for the relevant neighboring halo transfers
3. Communication operations are started as soon as the relevant data is ready

This is implemented using CUDA events and stream wait operations:

```mermaid
flowchart TD
    subgraph "Synchronization Pattern"
        direction TB
        
        subgraph "Current Iteration N"
            waitEvents["Wait for push_top_done[N%2] and
            push_bottom_done[N%2]"]
            compBulk["Compute Interior Points"]
            compBoundaries["Compute Boundaries"]
            pushHalos["Push Halos to Neighbors"]
            recordEvents["Record push_top_done[(N+1)%2] and
            push_bottom_done[(N+1)%2]"]
        end
        
        subgraph "Next Iteration N+1"
            nextWait["Wait for push_top_done[(N+1)%2] and
            push_bottom_done[(N+1)%2]"]
        end
    end
    
    waitEvents --> compBulk
    compBulk --> compBoundaries
    compBoundaries --> pushHalos
    pushHalos --> recordEvents
    recordEvents --> nextWait
```

Sources: [multi_threaded_copy_overlap/jacobi.cu:321-323](), [multi_threaded_copy_overlap/jacobi.cu:332-343](), [multi_threaded_copy_overlap/jacobi.cu:347-356]()

### Double-Buffered Event Management

The implementation uses a double-buffering technique for CUDA events to allow overlapping iterations:

```
push_top_done[0][dev_id]    // Events for even iterations
push_bottom_done[0][dev_id] // Events for even iterations
push_top_done[1][dev_id]    // Events for odd iterations
push_bottom_done[1][dev_id] // Events for odd iterations
```

This allows the current iteration to record events that will be waited on in the next iteration without conflicts.

Sources: [multi_threaded_copy_overlap/jacobi.cu:167-168](), [multi_threaded_copy_overlap/jacobi.cu:248-253]()

## Norm Calculation

The implementation calculates the L2 norm periodically (either every `nccheck` iterations or every 100 iterations when printing progress):

1. Each GPU computes a partial L2 norm for its portion of the domain
2. These partial norms are gathered using OpenMP atomic operations
3. The global L2 norm is computed as the square root of the sum

```mermaid
flowchart TD
    subgraph "Norm Calculation Process"
        direction TB
        
        partial["Calculate Partial Norm
        on each GPU"]
        memcpy["cudaMemcpyAsync l2_norm from
        device to host"]
        barrier["OpenMP Barrier"]
        atomic["#pragma omp atomic
        l2_norm += *(l2_norm_h)"]
        sqrt["l2_norm = sqrt(l2_norm)"]
    end
    
    partial --> memcpy
    memcpy --> barrier
    barrier --> atomic
    atomic --> sqrt
```

Sources: [multi_threaded_copy_overlap/jacobi.cu:358-380]()

## Performance Considerations

### Communication-Computation Overlap Benefits

The primary advantage of this implementation over the basic multi-threaded copy approach is the overlap of computation and communication. This reduces the effective time spent on communication by hiding it behind computation, particularly beneficial when:

1. The communication time is significant but less than computation time
2. GPUs have sufficient resources to perform computation and communication simultaneously
3. The problem size is large enough to benefit from parallelism

### Stream Priority Optimization

Using different priorities for computation and communication streams helps ensure that communication operations are scheduled promptly, minimizing the latency between when data is ready to be transferred and when the transfer actually begins.

Sources: [multi_threaded_copy_overlap/jacobi.cu:237-246]()

## Differences from Multi-Threaded Copy (without Overlap)

The key differences from the basic [Multi-Threaded Copy](#3.1.2) implementation are:

1. **Multiple CUDA Streams**: Uses separate streams for computation and communication
2. **CUDA Events**: Uses events for fine-grained synchronization between operations
3. **Stream Priorities**: Assigns higher priority to communication streams
4. **Asynchronous Memory Operations**: Uses `cudaMemcpyAsync` for all data transfers
5. **Double-buffered Events**: Uses alternating sets of events for odd and even iterations

These differences enable the overlapping of computation and communication, which can significantly improve performance for large problem sizes.

Sources: [multi_threaded_copy_overlap/jacobi.cu:167-169](), [multi_threaded_copy_overlap/jacobi.cu:237-254](), [multi_threaded_copy_overlap/jacobi.cu:347-356]()

---

