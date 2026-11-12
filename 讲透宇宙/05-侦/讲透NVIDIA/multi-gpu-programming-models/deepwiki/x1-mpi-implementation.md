<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/multi-gpu-programming-models · extra page MPI Implementation · fetched 2026-10-26 -->

# MPI Implementation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [mpi/Makefile](mpi/Makefile)
- [mpi/jacobi.cpp](mpi/jacobi.cpp)

</details>



This page documents the basic MPI-based implementation of the Jacobi solver using CUDA-aware MPI. This implementation distributes the computation across multiple GPUs by dividing the domain among separate MPI processes, with each process managing its own GPU. For the implementation that overlaps computation and communication, see [MPI with Computation-Communication Overlap](#3.3.2).

## Overview

The MPI implementation leverages the Message Passing Interface (MPI) framework with CUDA-aware MPI to enable direct GPU memory communication between processes. This approach uses a domain decomposition strategy where the 2D grid is divided into horizontal strips, with each MPI process handling a portion of the domain on its assigned GPU.

Key characteristics of this implementation:
- Uses CUDA-aware MPI to eliminate host-device transfer overhead
- Employs a row-wise domain decomposition with ghost cells
- Implements periodic boundary conditions
- Uses point-to-point communication for boundary exchanges
- Utilizes collective operations for convergence checking

## Architecture and Domain Decomposition

### Domain Decomposition Strategy

The implementation divides the 2D grid horizontally among MPI processes, with each process handling approximately the same number of rows:

Domain Decomposition Diagram
```mermaid
flowchart TB
    FullGrid["Full 2D Grid (nx × ny)"]
    
    subgraph "Process Distribution"
        direction TB
        P0["Process 0\nchunk_size rows"]
        P1["Process 1\nchunk_size rows"]
        Pdots["..."]
        PN["Process N-1\nchunk_size rows"]
    end
    
    FullGrid --> P0
    FullGrid --> P1
    FullGrid --> Pdots
    FullGrid --> PN
    
    subgraph "Memory Layout for Process 1"
        direction TB
        TopGhost["Top Ghost Row (from Process 0)"]
        LocalRows["Local Data Rows\n(chunk_size rows)"]
        BottomGhost["Bottom Ghost Row (from Process 2)"]
    end
    
    P1 -.-> TopGhost
    P1 -.-> LocalRows
    P1 -.-> BottomGhost
```

Sources: [mpi/jacobi.cpp:193-222]()

The load balancing algorithm ensures optimal distribution when the domain size is not perfectly divisible by the number of processes:

```mermaid
flowchart TD
    Start["Calculate Domain Distribution"]
    CalcLow["chunk_size_low = (ny - 2) / size"]
    CalcHigh["chunk_size_high = chunk_size_low + 1"]
    CalcRanksLow["num_ranks_low = size * chunk_size_low + size - (ny - 2)"]
    CheckRank["rank < num_ranks_low?"]
    AssignLow["chunk_size = chunk_size_low"]
    AssignHigh["chunk_size = chunk_size_high"]
    
    Start --> CalcLow
    CalcLow --> CalcHigh
    CalcHigh --> CalcRanksLow
    CalcRanksLow --> CheckRank
    CheckRank -- "Yes" --> AssignLow
    CheckRank -- "No" --> AssignHigh
```

Sources: [mpi/jacobi.cpp:193-205]()

### Process and Communication Architecture

The MPI implementation establishes a communication pattern between neighboring processes:

Process Communication Diagram
```mermaid
flowchart LR
    subgraph "Process 0"
        P0["GPU 0"]
        Data0["Local Data\n(a, a_new arrays)"]
        P0 --- Data0
    end
    
    subgraph "Process 1"
        P1["GPU 1"]
        Data1["Local Data\n(a, a_new arrays)"]
        P1 --- Data1
    end
    
    subgraph "Process N-1"
        PN["GPU N-1"]
        DataN["Local Data\n(a, a_new arrays)"]
        PN --- DataN
    end
    
    Data0 -- "MPI_Sendrecv\n(Boundary Exchange)" --> Data1
    Data1 -- "MPI_Sendrecv\n(Boundary Exchange)" --> Data0
    
    Data1 -- "..." --> DataN
    DataN -- "..." --> Data1
    
    Data0 -- "MPI_Sendrecv\n(Periodic Boundary)" --> DataN
    DataN -- "MPI_Sendrecv\n(Periodic Boundary)" --> Data0
    
    AllData["All Processes"] -- "MPI_Allreduce\n(l2_norm convergence)" --> AllData
```

Sources: [mpi/jacobi.cpp:286-302]()

## Implementation Details

### Initialization Process

The initialization phase consists of several critical steps:

1. **MPI Initialization**: Initialize the MPI environment and verify CUDA-aware MPI support
2. **Process Identification**: Determine process rank and size
3. **Device Selection**: Based on local rank within a node
4. **Domain Calculation**: Compute local domain boundaries
5. **Memory Allocation**: Allocate GPU memory for computation and communication
6. **Boundary Initialization**: Set initial conditions for boundaries

```mermaid
flowchart TD
    Init["MPI_Init"]
    CudaCheck["Check CUDA-aware MPI support"]
    CommRank["MPI_Comm_rank - Get process ID"]
    CommSize["MPI_Comm_size - Get total processes"]
    LocalRank["Calculate local_rank for device selection"]
    SetDevice["cudaSetDevice(local_rank % num_devices)"]
    AllocMem["Allocate GPU memory:\na, a_new, l2_norm_d"]
    CalcBounds["Calculate domain boundaries:\nchunk_size, iy_start, iy_end"]
    InitBounds["Initialize boundary conditions"]
    
    Init --> CudaCheck
    CudaCheck --> CommRank
    CommRank --> CommSize
    CommSize --> LocalRank
    LocalRank --> SetDevice
    SetDevice --> AllocMem
    AllocMem --> CalcBounds
    CalcBounds --> InitBounds
```

Sources: [mpi/jacobi.cpp:149-230]()

### Main Computation Loop

The main iteration loop follows this sequence:

1. Reset norm calculation buffer
2. Launch Jacobi kernel for the local domain
3. Synchronize and exchange boundary data with neighbors
4. Check convergence (if necessary) using a global reduction
5. Swap buffers and proceed to next iteration

```mermaid
flowchart TD
    LoopCheck["while l2_norm > tol && iter < iter_max"]
    ResetNorm["cudaMemsetAsync(l2_norm_d)"]
    CalcNorm["calculate_norm = (iter % nccheck == 0)"]
    Jacobi["launch_jacobi_kernel\n(Process local domain)"]
    RecordEvent["cudaEventRecord(compute_done)"]
    CopyNorm["cudaMemcpyAsync(l2_norm_h)\n(if calculating norm)"]
    SyncEvent["cudaEventSynchronize(compute_done)"]
    ExchangeTop["MPI_Sendrecv - Exchange with top neighbor"]
    ExchangeBottom["MPI_Sendrecv - Exchange with bottom neighbor"]
    SyncStream["cudaStreamSynchronize(compute_stream)\n(if calculating norm)"]
    GlobalReduce["MPI_Allreduce(l2_norm_h)\n(if calculating norm)"]
    CalcFinalNorm["l2_norm = sqrt(l2_norm)\n(if calculating norm)"]
    PrintStatus["Print status\n(if rank 0 and iter % 100 == 0)"]
    SwapBuffers["std::swap(a_new, a)"]
    Increment["iter++"]
    
    LoopCheck --> ResetNorm
    ResetNorm --> CalcNorm
    CalcNorm --> Jacobi
    Jacobi --> RecordEvent
    RecordEvent --> CopyNorm
    CopyNorm --> SyncEvent
    SyncEvent --> ExchangeTop
    ExchangeTop --> ExchangeBottom
    ExchangeBottom --> SyncStream
    SyncStream --> GlobalReduce
    GlobalReduce --> CalcFinalNorm
    CalcFinalNorm --> PrintStatus
    PrintStatus --> SwapBuffers
    SwapBuffers --> Increment
    Increment --> LoopCheck
```

Sources: [mpi/jacobi.cpp:272-311]()

### Boundary Exchange Mechanism

The implementation uses `MPI_Sendrecv` to perform boundary exchanges between neighboring processes:

```mermaid
flowchart LR
    subgraph "Process i"
        TopRow["Top Row - iy_start"]
        BottomRow["Bottom Row - (iy_end-1)"]
        TopGhost["Top Ghost Row - 0"]
        BottomGhost["Bottom Ghost Row - iy_end"]
    end
    
    subgraph "Process i-1"
        PrevBottom["Bottom Row"]
    end
    
    subgraph "Process i+1"
        NextTop["Top Row"]
    end
    
    TopRow -- "MPI_Sendrecv" --> PrevBottom
    PrevBottom -- "MPI_Sendrecv" --> TopGhost
    
    BottomRow -- "MPI_Sendrecv" --> NextTop
    NextTop -- "MPI_Sendrecv" --> BottomGhost
```

The code implements periodic boundary conditions by defining appropriate neighbor ranks:

```
const int top = rank > 0 ? rank - 1 : (size - 1);
const int bottom = (rank + 1) % size;
```

Sources: [mpi/jacobi.cpp:286-296]()

## Critical Code Sections

### MPI Communication Calls

The core communication is performed through two `MPI_Sendrecv` calls:

1. Send top row to top neighbor, receive bottom ghost from bottom neighbor:
```
MPI_CALL(MPI_Sendrecv(a_new + iy_start * nx, nx, MPI_REAL_TYPE, top, 0,
                      a_new + (iy_end * nx), nx, MPI_REAL_TYPE, bottom, 0, MPI_COMM_WORLD,
                      MPI_STATUS_IGNORE));
```

2. Send bottom row to bottom neighbor, receive top ghost from top neighbor:
```
MPI_CALL(MPI_Sendrecv(a_new + (iy_end - 1) * nx, nx, MPI_REAL_TYPE, bottom, 0, a_new, nx,
                      MPI_REAL_TYPE, top, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE));
```

Sources: [mpi/jacobi.cpp:292-296]()

### Convergence Checking

The convergence check is performed using a global reduction operation:

```
MPI_CALL(MPI_Allreduce(l2_norm_h, &l2_norm, 1, MPI_REAL_TYPE, MPI_SUM, MPI_COMM_WORLD));
l2_norm = std::sqrt(l2_norm);
```

Sources: [mpi/jacobi.cpp:301-302]()

## Building and Running

The implementation can be built using the provided Makefile:

```
make -C mpi
```

To run with a specific number of MPI processes:

```
mpirun -np <number_of_processes> ./mpi/jacobi [options]
```

Available command-line options:
- `-niter <N>`: Maximum number of iterations (default: 1000)
- `-nx <N>`, `-ny <N>`: Grid dimensions (default: 16384×16384)
- `-nccheck <N>`: Check convergence every N iterations (default: 1)
- `-csv`: Output results in CSV format

Sources: [mpi/Makefile:41-42]()

## Performance Considerations

Several factors impact the performance of the MPI implementation:

1. **Synchronization Barriers**:
   - The implementation synchronizes after computation before boundary exchange
   - Global synchronization during convergence checking

2. **Communication Overhead**:
   - Each iteration requires two `MPI_Sendrecv` operations per process
   - Convergence checking requires an `MPI_Allreduce` across all processes

3. **CUDA-aware MPI Requirements**:
   - Implementation requires CUDA-aware MPI for direct GPU-to-GPU communication
   - A compatibility check is performed at initialization [mpi/jacobi.cpp:36-42]()

4. **Load Balancing**:
   - The implementation distributes rows optimally when ny-2 is not divisible by the number of processes
   - Some processes may receive one additional row for better load balancing

## Comparison with Other Implementations

| Feature | MPI Implementation | MPI with Overlap | NCCL Implementation |
|---------|-------------------|------------------|---------------------|
| Communication Mechanism | CUDA-aware MPI | CUDA-aware MPI | NCCL Collectives |
| Computation-Communication Overlap | No | Yes | Varies by implementation |
| Boundary Exchange | Synchronous after computation | Asynchronous during computation | NCCL SendRecv |
| Memory Requirements | 2 arrays + ghost cells | 3 arrays + ghost cells | 2 arrays + communication buffers |
| Programming Complexity | Moderate | Higher | Moderate |

The main limitation of this basic MPI implementation is the lack of computation-communication overlap, which is addressed in the [MPI with Computation-Communication Overlap](#3.3.2) implementation.

Sources: [mpi/jacobi.cpp]()

---

