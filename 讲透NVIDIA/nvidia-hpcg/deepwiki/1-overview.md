<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvidia-hpcg · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [src/main.cpp](src/main.cpp)

</details>



## Purpose and Scope

This document provides a comprehensive overview of the NVIDIA High Performance Conjugate Gradient (HPCG) benchmark system. NVIDIA HPCG is a high-performance computing benchmark that evaluates sparse linear algebra performance on heterogeneous systems combining NVIDIA GPUs and Grace CPUs. The system performs multigrid preconditioned conjugate gradient iterations using double precision floating point arithmetic to solve large sparse linear systems.

The benchmark is designed to exploit NVIDIA's high-performance math libraries including cuSPARSE, cuBLAS, and NVPL Sparse to achieve optimal performance for sparse matrix-vector multiplication (SpMV) and sparse triangular solvers (SpSV). For detailed information about building and compiling the system, see [Building HPCG](#2.1). For execution instructions and parameter configuration, see [Running HPCG](#2.2).

Sources: [README.md:1-25](), [src/main.cpp:15-40]()

## System Architecture Overview

The NVIDIA HPCG benchmark implements a sophisticated multi-layered architecture that orchestrates heterogeneous computing resources through a centralized controller and dual execution engines.

### Main System Components

```mermaid
graph TB
    subgraph "Orchestration Layer"
        MAIN["main() - Primary Controller<br/>[src/main.cpp:135]"]
        INIT["HPCG_Init() - Parameter Setup<br/>[hpcg.hpp]"]
        PARAMS["HPCG_Params - Configuration<br/>[src/main.cpp:142]"]
    end
    
    subgraph "Execution Engines"
        GPU_ENGINE["GPU Execution Engine<br/>CudaKernels"]
        CPU_ENGINE["CPU Execution Engine<br/>CpuKernels"] 
        
        GPU_ENGINE --> CUSPARSE["cusparsehandle<br/>[src/main.cpp:93]"]
        GPU_ENGINE --> CUBLAS["cublashandle<br/>[src/main.cpp:94]"]
        CPU_ENGINE --> NVPL["nvpl_sparse_handle<br/>[src/main.cpp:102]"]
    end
    
    subgraph "Core Data Structures"
        SPARSE_A["SparseMatrix A<br/>[src/main.cpp:352]"]
        VECTORS["Vector b, x, xexact<br/>[src/main.cpp:354]"]
        CG_DATA["CGData data<br/>[src/main.cpp:356]"]
    end
    
    subgraph "Communication Layer"
        MPI_COMM["MPI Communication"]
        P2P["P2P_Mode<br/>[src/main.cpp:107]"]
        HALO["ExchangeHalo System"]
    end
    
    MAIN --> INIT
    MAIN --> PARAMS
    MAIN --> GPU_ENGINE
    MAIN --> CPU_ENGINE
    MAIN --> SPARSE_A
    
    PARAMS --> GPU_ENGINE
    PARAMS --> CPU_ENGINE
    
    SPARSE_A --> VECTORS
    SPARSE_A --> CG_DATA
    
    GPU_ENGINE --> MPI_COMM
    CPU_ENGINE --> MPI_COMM
    MPI_COMM --> P2P
    MPI_COMM --> HALO
```

The system centers around the `main()` function in [src/main.cpp:135]() which serves as the primary orchestrator. It manages the entire benchmark lifecycle from initialization through problem generation, optimization, validation, and final benchmarking phases.

Sources: [src/main.cpp:135-872](), [src/main.cpp:92-122]()

### Execution Mode Architecture

NVIDIA HPCG supports three distinct execution modes that determine how computational work is distributed across available hardware resources:

```mermaid
graph TD
    PARAMS_EXEC["params.exec_mode<br/>[src/main.cpp:167]"] --> MODE_DECISION{Execution Mode}
    
    MODE_DECISION -->|"GPUONLY"| GPU_ONLY["GPU-Only Execution<br/>[src/main.cpp:174]"]
    MODE_DECISION -->|"CPUONLY"| CPU_ONLY["Grace-Only Execution<br/>[src/main.cpp:168]"] 
    MODE_DECISION -->|"GPUCPU"| HETEROGENEOUS["Heterogeneous GPU+Grace<br/>[src/main.cpp:169]"]
    
    GPU_ONLY --> GPU_LIBS["cuSPARSE + cuBLAS<br/>CUDA Runtime"]
    CPU_ONLY --> CPU_LIBS["NVPL Sparse<br/>CPU Optimization"]
    HETEROGENEOUS --> GPU_LIBS
    HETEROGENEOUS --> CPU_LIBS
    
    GPU_ONLY --> GPU_RANK_SETUP["params.rank_type = GPU<br/>[src/main.cpp:361]"]
    CPU_ONLY --> CPU_RANK_SETUP["params.rank_type = CPU<br/>[src/main.cpp:403]"]
    HETEROGENEOUS --> GPU_RANK_SETUP
    HETEROGENEOUS --> CPU_RANK_SETUP
    
    GPU_RANK_SETUP --> GPU_KERNELS["CudaKernels.cu<br/>GPU Compute Path"]
    CPU_RANK_SETUP --> CPU_KERNELS["CpuKernels.cpp<br/>CPU Compute Path"]
    
    GPU_KERNELS --> COMMUNICATION["MPI/NCCL Communication<br/>P2P_Mode"]
    CPU_KERNELS --> COMMUNICATION
```

The execution mode is determined during initialization and affects library selection, memory allocation strategies, and computational kernel dispatch throughout the benchmark execution.

Sources: [src/main.cpp:167-169](), [src/main.cpp:361-424](), [src/main.cpp:174-235]()

## Benchmark Execution Pipeline

The NVIDIA HPCG benchmark follows a structured multi-phase execution pipeline that ensures reproducible and validated performance measurements:

### Primary Execution Phases

```mermaid
flowchart TD
    START["main() Entry Point<br/>[src/main.cpp:135]"] --> MPI_INIT["MPI_Init<br/>[src/main.cpp:138]"]
    MPI_INIT --> HPCG_INIT["HPCG_Init - Parameter Parsing<br/>[src/main.cpp:143]"]
    
    HPCG_INIT --> VALIDATION["Platform Validation<br/>[src/main.cpp:224-261]"]
    VALIDATION --> RANK_INIT["InitializeRanks<br/>[src/main.cpp:265]"]
    
    RANK_INIT --> PROBLEM_SETUP["Problem Setup Phase<br/>[src/main.cpp:284-425]"]
    PROBLEM_SETUP --> GEOM_GEN["GenerateGeometry<br/>[src/main.cpp:293]"]
    GEOM_GEN --> MATRIX_GEN["GenerateProblem - A,b,x,xexact<br/>[src/main.cpp:380,407]"]
    MATRIX_GEN --> HALO_SETUP["SetupHalo<br/>[src/main.cpp:381,408]"]
    HALO_SETUP --> MG_SETUP["Multigrid Hierarchy<br/>[src/main.cpp:382-386,409-413]"]
    
    MG_SETUP --> REF_TIMING["Reference Timing Phase<br/>[src/main.cpp:448-495]"]
    REF_TIMING --> SPMV_REF["ComputeSPMV_ref<br/>[src/main.cpp:469]"]
    REF_TIMING --> MG_REF["ComputeMG_ref<br/>[src/main.cpp:479]"]
    REF_TIMING --> CG_REF["CG_ref<br/>[src/main.cpp:523]"]
    
    CG_REF --> OPTIMIZATION["OptimizeProblem<br/>[src/main.cpp:562]"]
    OPTIMIZATION --> VALIDATION_TESTS["Validation Testing<br/>[src/main.cpp:622-640]"]
    VALIDATION_TESTS --> TEST_CG["TestCG<br/>[src/main.cpp:630]"]
    VALIDATION_TESTS --> TEST_SYM["TestSymmetry<br/>[src/main.cpp:633]"]
    
    TEST_SYM --> OPT_CG_SETUP["Optimized CG Setup<br/>[src/main.cpp:641-657]"]
    OPT_CG_SETUP --> BENCHMARK_LOOP["Benchmark Timing Loop<br/>[src/main.cpp:758-781]"]
    BENCHMARK_LOOP --> CG_OPTIMIZED["CG - Optimized Kernels<br/>[src/main.cpp:761]"]
    
    CG_OPTIMIZED --> RESULTS["ReportResults<br/>[src/main.cpp:821]"]
    RESULTS --> CLEANUP["Resource Cleanup<br/>[src/main.cpp:824-863]"]
    CLEANUP --> MPI_FINALIZE["MPI_Finalize<br/>[src/main.cpp:869]"]
```

Each phase serves a specific purpose in ensuring benchmark validity and performance measurement accuracy. The reference timing phase establishes baseline performance metrics, while the optimization phase applies platform-specific optimizations before the final timed benchmark execution.

Sources: [src/main.cpp:135-872](), [src/main.cpp:284-425](), [src/main.cpp:758-781]()

## Core Computational Framework

The benchmark implements a sophisticated computational framework centered around sparse matrix operations and conjugate gradient solving:

### Data Structure Relationships

```mermaid
graph TB
    subgraph "Matrix Infrastructure"
        SPARSE_MATRIX["SparseMatrix A<br/>[src/main.cpp:352]"]
        GEOMETRY["Geometry* geom<br/>[src/main.cpp:292]"]
        MG_HIERARCHY["Multigrid Hierarchy<br/>A.Ac (coarse levels)"]
    end
    
    subgraph "Vector System"
        VECTOR_B["Vector b - RHS<br/>[src/main.cpp:354]"]
        VECTOR_X["Vector x - Solution<br/>[src/main.cpp:354]"] 
        VECTOR_XEXACT["Vector xexact - Exact<br/>[src/main.cpp:354]"]
        VECTOR_OVERLAP["x_overlap - Halo<br/>[src/main.cpp:353]"]
    end
    
    subgraph "CG Algorithm Data"
        CG_DATA["CGData data<br/>[src/main.cpp:356]"]
        TIMES_ARRAY["times[10] - Performance<br/>[src/main.cpp:355]"]
        TEST_DATA["TestCGData, TestSymmetryData<br/>[src/main.cpp:628,632]"]
    end
    
    subgraph "Optimization Infrastructure"
        OPT2REF["A.opt2ref - Permutation<br/>[src/main.cpp:649]"]
        REF2OPT["A.ref2opt - Reverse Perm<br/>[src/main.cpp:797]"]
        SLICE_SIZE["A.slice_size - SELL Format<br/>[src/main.cpp:365,404]"]
    end
    
    GEOMETRY --> SPARSE_MATRIX
    SPARSE_MATRIX --> MG_HIERARCHY
    SPARSE_MATRIX --> VECTOR_B
    SPARSE_MATRIX --> VECTOR_X
    SPARSE_MATRIX --> CG_DATA
    
    VECTOR_X --> VECTOR_OVERLAP
    CG_DATA --> TIMES_ARRAY
    CG_DATA --> TEST_DATA
    
    SPARSE_MATRIX --> OPT2REF
    OPT2REF --> REF2OPT
    SPARSE_MATRIX --> SLICE_SIZE
```

The `SparseMatrix` structure serves as the central data container, containing geometry information, numerical data, and optimization metadata. The system maintains multiple vector instances for different algorithmic phases and supports sophisticated permutation schemes for performance optimization.

Sources: [src/main.cpp:352-356](), [src/main.cpp:292-293](), [src/main.cpp:649-657]()

## Communication and Distribution Architecture

NVIDIA HPCG implements a flexible communication system that supports various point-to-point communication modes and distributed memory execution:

### Communication Infrastructure

```mermaid
graph TB
    subgraph "Communication Configuration"
        P2P_MODE["P2P_Mode - Global Variable<br/>[src/main.cpp:107]"]
        COMM_PARAMS["params.p2_mode<br/>[src/main.cpp:150]"]
    end
    
    subgraph "MPI Infrastructure"
        MPI_RANK["rank - Process ID<br/>[src/main.cpp:145]"]
        MPI_SIZE["size - Process Count<br/>[src/main.cpp:145]"]
        RANK_GRID["npx*npy*npz Grid<br/>[src/main.cpp:238]"]
    end
    
    subgraph "Halo Exchange System"
        SETUP_HALO["SetupHalo Function<br/>[src/main.cpp:381,408]"]
        EXCHANGE_HALO["ExchangeHalo Operations"]
        NEIGHBOR_COMM["Neighbor Communication"]
    end
    
    subgraph "GPU-Specific Communication"
        NCCL_MODE["NCCL Communication"]
        CUDA_AWARE["MPI_CUDA_AWARE Mode"]
        GPU_DIRECT["GPU-Direct MPI"]
    end
    
    subgraph "CPU-Specific Communication"
        MPI_CPU["MPI_CPU Mode"]
        HOST_BUFFERS["Host Memory Buffers"]
    end
    
    COMM_PARAMS --> P2P_MODE
    P2P_MODE --> NCCL_MODE
    P2P_MODE --> CUDA_AWARE
    P2P_MODE --> MPI_CPU
    
    MPI_RANK --> RANK_GRID
    MPI_SIZE --> RANK_GRID
    RANK_GRID --> SETUP_HALO
    
    SETUP_HALO --> EXCHANGE_HALO
    EXCHANGE_HALO --> NEIGHBOR_COMM
    
    NCCL_MODE --> GPU_DIRECT
    CUDA_AWARE --> GPU_DIRECT
    MPI_CPU --> HOST_BUFFERS
```

The communication system validates mode compatibility with execution targets and configures appropriate data transfer mechanisms. GPU execution modes leverage CUDA-aware MPI and NCCL for optimal GPU-to-GPU communication, while CPU modes use standard MPI host-based communication.

Sources: [src/main.cpp:105-108](), [src/main.cpp:182-221](), [src/main.cpp:381](), [src/main.cpp:408]()

## Build and Platform Support

The NVIDIA HPCG benchmark supports multiple hardware architectures and provides flexible build configuration options:

### Build System Architecture

| Component | Description | Configuration Variables |
|-----------|-------------|------------------------|
| **GPU Support** | NVIDIA GPU execution with CUDA | `USE_CUDA=1` |
| **Grace Support** | NVIDIA Grace CPU execution | `USE_GRACE=1` |  
| **NCCL Support** | Advanced GPU communication | `USE_NCCL=1` |
| **Architecture** | Target processor architecture | ARM64 vs x86 |
| **Libraries** | Required external dependencies | MPI, CUDA, NVPL |

The build system generates different binary targets based on configuration:
- `xhpcg` - GPU-enabled binary when `USE_CUDA=1`
- `xhpcg-cpu` - CPU-only binary when `USE_CUDA=0` and `USE_GRACE=1`

The system performs extensive runtime validation to ensure library compatibility, including version checks for cuSPARSE (minimum 12.2) and NVPL Sparse (minimum 0.2).

Sources: [README.md:51-66](), [src/main.cpp:310-350](), [src/main.cpp:224-261]()

---

