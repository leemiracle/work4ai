<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvidia-hpcg · page 4 Computational Engines · fetched 2026-10-26 -->

# Computational Engines

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/CpuKernels.cpp](src/CpuKernels.cpp)
- [src/CudaKernels.cu](src/CudaKernels.cu)

</details>



This document describes the dual computational engines that provide high-performance sparse linear algebra operations for the NVIDIA HPCG benchmark. The computational engines consist of specialized GPU (CUDA) and CPU (Grace) execution paths that handle matrix operations, vector computations, and distributed communication primitives.

For information about the overall architecture coordination, see [Core Architecture](#3). For details about specific matrix data structures used by these engines, see [Core Data Structures](#3.3). For distributed computing coordination that uses these engines, see [Distributed Computing](#5.2).

## Engine Architecture Overview

The computational engines implement a dual-path architecture supporting both GPU acceleration and CPU optimization targeting NVIDIA Grace processors:

```mermaid
graph TB
    subgraph "Computational Engine Interface"
        MATRIX_OPS["Matrix Operations"]
        VECTOR_OPS["Vector Operations"] 
        MG_OPS["Multigrid Operations"]
        COMM_OPS["Communication Primitives"]
    end
    
    subgraph "GPU Engine (CUDA)"
        GPU_MEM["AllocateMemCuda()<br/>DeleteMatrixGpu()"]
        GPU_KERN["CUDA Kernels<br/>CudaKernels.cu"]
        GPU_LIBS["cuSPARSE/cuBLAS<br/>Integration"]
        GPU_P2P["GPU-Direct MPI<br/>NCCL Support"]
    end
    
    subgraph "CPU Engine (Grace)"
        CPU_MEM["AllocateMemCpu()<br/>DeleteMatrixCpu()"]
        CPU_KERN["CPU Kernels<br/>CpuKernels.cpp"]
        CPU_LIBS["NVPL Sparse<br/>SVE Optimization"]
        CPU_P2P["Standard MPI<br/>CPU Communication"]
    end
    
    MATRIX_OPS --> GPU_KERN
    MATRIX_OPS --> CPU_KERN
    VECTOR_OPS --> GPU_KERN
    VECTOR_OPS --> CPU_KERN
    MG_OPS --> GPU_KERN
    MG_OPS --> CPU_KERN
    COMM_OPS --> GPU_P2P
    COMM_OPS --> CPU_P2P
    
    GPU_KERN --> GPU_MEM
    GPU_KERN --> GPU_LIBS
    CPU_KERN --> CPU_MEM
    CPU_KERN --> CPU_LIBS
```

**Sources:** [src/CudaKernels.cu:1-2427](), [src/CpuKernels.cpp:1-1351]()

## Memory Management Subsystem

Both engines implement sophisticated memory management with optimization features:

```mermaid
graph LR
    subgraph "GPU Memory Management"
        GPU_ALLOC["AllocateMemCuda()"]
        GPU_COMPRESS["L2 Compression<br/>cudaMallocCompressible()"]
        GPU_ESTIMATE["EstimateLUmem()"]
        GPU_DELETE["DeleteMatrixGpu()"]
    end
    
    subgraph "CPU Memory Management"
        CPU_ALLOC["AllocateMemCpu()"]
        CPU_ESTIMATE["Memory Estimation"]
        CPU_DELETE["DeleteMatrixCpu()"]
    end
    
    subgraph "Memory Optimization Features"
        REDUCTION["Use_Hpcg_Mem_Reduction"]
        COMPRESSION["Use_Compression"]
        ESTIMATE["Size Estimation<br/>288x512x512<br/>296x512x512"]
    end
    
    GPU_ALLOC --> GPU_COMPRESS
    GPU_ALLOC --> GPU_ESTIMATE
    CPU_ALLOC --> CPU_ESTIMATE
    REDUCTION --> GPU_ALLOC
    REDUCTION --> CPU_ALLOC
    COMPRESSION --> GPU_COMPRESS
    ESTIMATE --> GPU_ESTIMATE
    ESTIMATE --> CPU_ESTIMATE
```

The memory management implements several key optimizations:

| Feature | GPU Implementation | CPU Implementation |
|---------|-------------------|-------------------|
| L2 Compression | `cudaMallocCompressible()` | Not available |
| Memory Reduction | Shared L/U matrices | Shared L/U matrices |
| Size Estimation | `EstimateLUmem()` with hardcoded sizes | Same estimation logic |
| Buffer Optimization | cuSPARSE SpSV buffers | NVPL SpSV buffers |

**Sources:** [src/CudaKernels.cu:173-243](), [src/CudaKernels.cu:252-343](), [src/CpuKernels.cpp:24-132]()

## Matrix Operations Engine

### Graph Coloring and Optimization

Both engines implement the Jones-Plassmann Luby graph coloring algorithm for matrix optimization:

```mermaid
graph TD
    subgraph "GPU Coloring Pipeline"
        GPU_INIT["setVectorAsc_kernel()"]
        GPU_HASH["minmaxHashStep_kernel()"]
        GPU_TEST["testHashStep3_kernel()"]
        GPU_PERM["thrust::sort_by_key()"]
        GPU_INV["inversePerm_kernel()"]
    end
    
    subgraph "CPU Coloring Pipeline"
        CPU_INIT["Initialize colors to -1"]
        CPU_HASH["minmaxHashStep()"]
        CPU_TEST["testHashStep3()"]
        CPU_COUNT["Parallel counting"]
        CPU_PERM["Prefixsum8ColCpu()"]
    end
    
    subgraph "Matrix Format Creation"
        SELL_GPU["GPU SELL Creation<br/>createSellLUColumnsValues_kernel()"]
        SELL_CPU["CPU SELL Creation<br/>CreateSellPermCpu()"]
        TRANSPOSE["GPU Transpose<br/>transposeBlock_kernel()"]
    end
    
    GPU_INIT --> GPU_HASH
    GPU_HASH --> GPU_TEST
    GPU_TEST --> GPU_PERM
    GPU_PERM --> GPU_INV
    
    CPU_INIT --> CPU_HASH
    CPU_HASH --> CPU_TEST
    CPU_TEST --> CPU_COUNT
    CPU_COUNT --> CPU_PERM
    
    GPU_INV --> SELL_GPU
    CPU_PERM --> SELL_CPU
    SELL_GPU --> TRANSPOSE
```

**Sources:** [src/CudaKernels.cu:1782-1875](), [src/CpuKernels.cpp:572-703](), [src/CudaKernels.cu:1977-1993](), [src/CpuKernels.cpp:708-887]()

### Sparse Matrix Vector Multiplication (SpMV)

The engines provide optimized SpMV implementations for different matrix formats:

```mermaid
graph LR
    subgraph "GPU SpMV Operations"
        GPU_INTERNAL["Internal Matrix SpMV<br/>SELL Format"]
        GPU_EXTERNAL["extMv_kernel()<br/>CSR External Matrix"]
        GPU_SCATTER["Scatter & Permute<br/>ref2opt mapping"]
    end
    
    subgraph "CPU SpMV Operations"
        CPU_INTERNAL["CPU Internal SpMV<br/>SELL Format"]
        CPU_EXTERNAL["ExtSpMVCpu()<br/>CSR External Matrix"]
        CPU_SVE["SVE Vectorization"]
    end
    
    subgraph "Vector Operations"
        WAXPBY_GPU["computeWAXPBY_kernel()"]
        WAXPBY_CPU["ComputeWAXPBYCpu()<br/>SVE Optimized"]
        DOT_CPU["ComputeDotProductCpu()<br/>SVE Optimized"]
    end
    
    GPU_EXTERNAL --> GPU_SCATTER
    CPU_EXTERNAL --> CPU_SVE
    WAXPBY_CPU --> CPU_SVE
    DOT_CPU --> CPU_SVE
```

**Sources:** [src/CudaKernels.cu:2222-2281](), [src/CpuKernels.cpp:1334-1350](), [src/CudaKernels.cu:2126-2147](), [src/CpuKernels.cpp:1076-1258]()

## Multigrid Operations

Both engines implement multigrid restriction and prolongation operations:

```mermaid
graph TB
    subgraph "GPU Multigrid Kernels"
        GPU_RESTRICT["computeRestriction_kernel()"]
        GPU_PROLONG["computeProlongation_kernel()"]
    end
    
    subgraph "CPU Multigrid Operations"
        CPU_RESTRICT["CPU Restriction<br/>OpenMP Parallel"]
        CPU_PROLONG["CPU Prolongation<br/>OpenMP Parallel"]
    end
    
    subgraph "Multigrid Data Flow"
        F2C["f2c Mapping"]
        F2C_PERM["f2cPerm Permutation"]
        COARSE["Coarse Grid"]
        FINE["Fine Grid"]
    end
    
    F2C --> GPU_RESTRICT
    F2C --> CPU_RESTRICT
    F2C --> GPU_PROLONG
    F2C --> CPU_PROLONG
    
    F2C_PERM --> GPU_RESTRICT
    F2C_PERM --> GPU_PROLONG
    
    FINE --> GPU_RESTRICT
    GPU_RESTRICT --> COARSE
    COARSE --> GPU_PROLONG
    GPU_PROLONG --> FINE
```

**Sources:** [src/CudaKernels.cu:2098-2120](), [src/CudaKernels.cu:2071-2093]()

## Communication Integration

The engines integrate with multiple communication backends for distributed execution:

| Communication Mode | GPU Support | CPU Support | Implementation |
|-------------------|-------------|-------------|----------------|
| `MPI_CPU` | Host staging | Direct | `ExchangeHaloCuda()` with staging |
| `MPI_CUDA_AWARE` | GPU-Direct | N/A | Direct GPU memory MPI |
| `MPI_GPU_All2allv` | GPU-Direct | N/A | `MPI_Alltoallv` on GPU memory |
| `MPI_CPU_All2allv` | Host staging | Direct | `MPI_Alltoallv` with staging |
| `NCCL` | Native | N/A | `ncclSend`/`ncclRecv` operations |

The halo exchange implementation supports different P2P communication modes:

```mermaid
graph LR
    subgraph "Communication Preparation"
        PACK["PackSendBufferCuda()<br/>sendbuf_kernel()"]
        GATHER["Gather x values"]
        STAGE["Host Staging<br/>(if required)"]
    end
    
    subgraph "Communication Execution"
        MPI_CPU["Standard MPI<br/>Host Memory"]
        MPI_GPU["CUDA-Aware MPI<br/>Device Memory"]
        NCCL["NCCL Collectives<br/>Device Memory"]
        ALL2ALL["MPI_Alltoallv<br/>Bulk Transfer"]
    end
    
    subgraph "Communication Completion"
        SCATTER["Scatter to x_external"]
        SYNC["Stream Synchronization"]
    end
    
    GATHER --> PACK
    PACK --> STAGE
    STAGE --> MPI_CPU
    PACK --> MPI_GPU
    PACK --> NCCL
    PACK --> ALL2ALL
    
    MPI_CPU --> SCATTER
    MPI_GPU --> SCATTER
    NCCL --> SCATTER
    ALL2ALL --> SCATTER
    
    SCATTER --> SYNC
```

**Sources:** [src/CudaKernels.cu:1200-1348](), [src/CudaKernels.cu:1081-1156]()

## Engine Performance Features

### GPU-Specific Optimizations

- **L2 Memory Compression**: Reduces memory bandwidth requirements for large matrices
- **Cooperative Groups**: Efficient warp-level primitives for reduction operations  
- **Thrust Integration**: GPU-accelerated sorting and algorithms for matrix optimization
- **cuSPARSE Integration**: Hardware-accelerated sparse operations

### CPU-Specific Optimizations  

- **SVE Vectorization**: ARM Scalable Vector Extensions for vectorized operations
- **OpenMP Parallelization**: Multi-threaded execution across CPU cores
- **NVPL Sparse Integration**: Optimized sparse linear algebra library
- **Memory Prefetching**: Optimized memory access patterns

**Sources:** [src/CudaKernels.cu:60-139](), [src/CpuKernels.cpp:948-1070](), [src/CpuKernels.cpp:1076-1258]()

---

