<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/multi-gpu-programming-models · extra page NCCL with Overlap · fetched 2026-10-26 -->

# NCCL with Overlap

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [nccl/jacobi.cpp](nccl/jacobi.cpp)
- [nccl_overlap/jacobi.cpp](nccl_overlap/jacobi.cpp)

</details>



## Purpose and Scope

This page documents the NCCL with Overlap implementation of the Jacobi solver, which enhances performance by overlapping computation and communication operations. This approach allows the solver to perform interior grid computations while simultaneously handling boundary exchanges with neighboring GPUs. For the basic NCCL implementation without overlap, see [NCCL Implementation](#3.4.1).

The NCCL with Overlap implementation leverages CUDA stream priorities and careful event synchronization to optimize the performance of multi-GPU Jacobi solvers by minimizing the time GPUs spend waiting for data.

Sources: [nccl_overlap/jacobi.cpp:1-460]()

## Key Concepts and Implementation Approach

The key innovation in this implementation is separating computation into boundary and interior regions and using separate CUDA streams with different priorities to enable effective overlap.

### Stream Prioritization

The implementation creates two CUDA streams with different priorities:
1. A high-priority stream for boundary computations and communication
2. A low-priority stream for interior computations

This prioritization ensures that operations critical for inter-GPU communication receive execution preference on the GPU.

```mermaid
flowchart TB
    subgraph "Stream Creation and Priority Assignment"
        GetPriority["Get stream priority range"]
        CreateCompute["Create compute_stream with lowest priority"]
        CreatePush["Create push_stream with highest priority"]
        CreateEvents["Create synchronization events"]
    end
    
    GetPriority --> CreateCompute
    GetPriority --> CreatePush
    CreateCompute --> CreateEvents
    CreatePush --> CreateEvents
```

Sources: [nccl_overlap/jacobi.cpp:290-304]()

### Domain Decomposition Strategy

The NCCL with Overlap implementation splits the grid domain into distinct regions for effective overlapping:

```mermaid
flowchart TD
    subgraph "Domain Decomposition"
        direction LR
        subgraph "Rank n-1"
            Top["Top Boundary (Received)"]
            Interior1["Interior Region"]
            BottomHalo1["Bottom Halo (Sent)"]
        end
        
        subgraph "Rank n"
            TopHalo["Top Halo (Sent)"]
            Interior["Interior Region"]
            Bottom["Bottom Boundary (Received)"]
        end
        
        subgraph "Rank n+1"
            TopHalo1["Top Halo (Sent)"]
            Interior2["Interior Region"]
            Bottom1["Bottom Boundary (Received)"]
        end
    end
    
    BottomHalo1 --"NCCL Send/Recv"--> Top
    TopHalo --"NCCL Send/Recv"--> Bottom1
    Bottom --"NCCL Send/Recv"--> TopHalo1
```

Sources: [nccl_overlap/jacobi.cpp:273-284]()

## Computation-Communication Overlap Technique

The implementation achieves overlap through a three-step process:

1. Compute boundary regions first (high-priority stream)
2. Start communication of boundary data (high-priority stream)
3. Compute interior region in parallel (low-priority stream)

This technique minimizes GPU idle time by allowing interior computation to proceed while boundary exchanges occur.

### Execution Pattern

```mermaid
sequenceDiagram
    participant Comp as "Compute Stream (low priority)"
    participant Push as "Push Stream (high priority)"
    participant Device as "GPU Device"
    participant Neighbor as "Neighboring GPUs"
    
    Comp->>Device: Reset L2 norm
    Comp->>Push: Signal reset_l2norm_done
    Push->>Device: Compute top boundary
    Push->>Device: Compute bottom boundary
    Push->>Comp: Signal push_prep_done
    Comp->>Device: Compute interior region
    Push->>Neighbor: Send/Receive boundaries (NCCL)
    Push->>Comp: Signal push_done
    Comp->>Device: Continue to next iteration
```

Sources: [nccl_overlap/jacobi.cpp:342-387]()

## Implementation Details

### Key Code Components

| Component | Purpose | Location |
|-----------|---------|----------|
| Stream Creation | Creates prioritized streams for computation and communication | [nccl_overlap/jacobi.cpp:290-298]() |
| Event Creation | Creates events for synchronization between streams | [nccl_overlap/jacobi.cpp:299-304]() |
| Boundary Computation | Computes outer rows that will be exchanged | [nccl_overlap/jacobi.cpp:348-353]() |
| Interior Computation | Computes inner rows of the domain | [nccl_overlap/jacobi.cpp:355-356]() |
| NCCL Communication | Performs boundary exchanges between GPUs | [nccl_overlap/jacobi.cpp:369-376]() |
| Synchronization | Coordinates between computation and communication | [nccl_overlap/jacobi.cpp:359-362](), [nccl_overlap/jacobi.cpp:387]() |

### Split Kernel Execution

The core computational work is split into three parts:

```mermaid
flowchart LR
    subgraph "Kernel Execution Pattern"
        direction TB
        subgraph "High Priority (push_stream)"
            TopRow["Process Row iy_start"]
            BottomRow["Process Row (iy_end-1)"]
        end
        
        subgraph "Low Priority (compute_stream)"
            Interior["Process Interior Rows
            (iy_start+1) to (iy_end-2)"]
        end
    end
    
    TopRow --> Comm
    BottomRow --> Comm
    
    subgraph "Communication (push_stream)"
        Comm["NCCL GroupStart
        Send/Recv Boundaries
        NCCL GroupEnd"]
    end
```

Sources: [nccl_overlap/jacobi.cpp:348-356](), [nccl_overlap/jacobi.cpp:369-375]()

## Communication Pattern

The implementation uses NCCL for boundary exchanges with a specific communication pattern:

1. Receive from top neighbor into top boundary
2. Send bottom boundary to bottom neighbor
3. Receive from bottom neighbor into bottom boundary
4. Send top boundary to top neighbor

This pattern is executed in the high-priority push stream to ensure it completes as quickly as possible.

```mermaid
flowchart TB
    subgraph "NCCL Communication Pattern"
        Group["ncclGroupStart()"]
        RecvTop["ncclRecv(a_new, nx, NCCL_REAL_TYPE, top, nccl_comm, push_stream)"]
        SendBottom["ncclSend(a_new + (iy_end-1)*nx, nx, NCCL_REAL_TYPE, bottom, nccl_comm, push_stream)"]
        RecvBottom["ncclRecv(a_new + (iy_end*nx), nx, NCCL_REAL_TYPE, bottom, nccl_comm, push_stream)"]
        SendTop["ncclSend(a_new + iy_start*nx, nx, NCCL_REAL_TYPE, top, nccl_comm, push_stream)"]
        GroupEnd["ncclGroupEnd()"]
    end
    
    Group --> RecvTop
    RecvTop --> SendBottom
    SendBottom --> RecvBottom
    RecvBottom --> SendTop
    SendTop --> GroupEnd
```

Sources: [nccl_overlap/jacobi.cpp:369-375]()

## Synchronization Mechanism

Proper synchronization between streams is crucial for the overlap strategy to work correctly. The implementation uses CUDA events for this purpose:

1. `reset_l2norm_done`: Signals when L2 norm reset is complete
2. `push_prep_done`: Signals when boundary computation is complete
3. `push_done`: Signals when communication is complete

These events control the dependencies between operations in different streams.

```mermaid
flowchart TD
    subgraph "Stream Synchronization Pattern"
        ResetL2["Reset L2 norm (compute_stream)"]
        RecordReset["Record reset_l2norm_done"]
        WaitForReset["push_stream waits for reset_l2norm_done"]
        BoundaryComp["Compute boundaries (push_stream)"]
        RecordPrep["Record push_prep_done"]
        InteriorComp["Compute interior (compute_stream)"]
        CommOps["NCCL communication (push_stream)"]
        RecordPush["Record push_done"]
        WaitForPush["compute_stream waits for push_done"]
    end
    
    ResetL2 --> RecordReset
    RecordReset --> WaitForReset
    WaitForReset --> BoundaryComp
    BoundaryComp --> RecordPrep
    RecordPrep --> InteriorComp
    BoundaryComp --> CommOps
    CommOps --> RecordPush
    RecordPush --> WaitForPush
    WaitForPush --> ResetL2
```

Sources: [nccl_overlap/jacobi.cpp:343-387]()

## Optional User Buffer Registration

The implementation optionally supports NCCL's user buffer registration API for potentially improved communication performance:

```mermaid
flowchart LR
    subgraph "User Buffer Registration"
        CheckVersion["Check NCCL version support"]
        Allocate["ncclMemAlloc()"]
        Register["ncclCommRegister()"]
        Use["Use registered buffers for communication"]
        Deregister["ncclCommDeregister()"]
        Free["ncclMemFree()"]
    end
    
    CheckVersion -->|"Supported"| Allocate
    Allocate --> Register
    Register --> Use
    Use --> Deregister
    Deregister --> Free
```

Sources: [nccl_overlap/jacobi.cpp:251-262](), [nccl_overlap/jacobi.cpp:440-452]()

## Performance Considerations

The NCCL with Overlap implementation offers several performance advantages:

1. **Reduced Idle Time**: By overlapping computation and communication, the GPU spends less time idle
2. **Stream Prioritization**: Ensures critical communication tasks are executed first
3. **Boundary Optimization**: Processes boundary data early to minimize communication latency

It is particularly effective for large problem sizes where the interior computation takes significant time compared to boundary exchanges.

The main trade-off is increased code complexity due to the need for careful stream and event management.

Sources: [nccl_overlap/jacobi.cpp:418-430]()

---

