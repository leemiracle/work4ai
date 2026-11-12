<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvidia-hpcg · page 3 Core Architecture · fetched 2026-10-26 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/hpcg.hpp](src/hpcg.hpp)
- [src/init.cpp](src/init.cpp)
- [src/main.cpp](src/main.cpp)

</details>



This document provides an overview of the main architectural components of the NVIDIA HPCG benchmark and how they work together to orchestrate benchmark execution across heterogeneous GPU and CPU systems.

The core architecture encompasses the central program controller, parameter management system, rank assignment mechanisms, and execution mode coordination. For detailed information about specific computational implementations, see [Computational Engines](#4). For distributed computing aspects, see [Distributed Computing](#5.2).

## System Overview

The NVIDIA HPCG benchmark is built around a central orchestration architecture that coordinates execution across multiple hardware targets and communication patterns. The system supports three primary execution modes and manages complex interactions between GPU and CPU resources.

### Main Architectural Components

```mermaid
graph TB
    subgraph "Program Controller"
        MAIN["main()"]
        PHASES["Execution Phases"]
    end
    
    subgraph "Configuration System"
        HPCG_PARAMS["HPCG_Params"]
        INIT_RANKS["InitializeRanks()"]
        HPCG_INIT["HPCG_Init()"]
    end
    
    subgraph "Execution Modes"
        GPUONLY["GPUONLY Mode"]
        CPUONLY["CPUONLY Mode"]
        GPUCPU["GPUCPU Mode"]
    end
    
    subgraph "Communication Layer"
        MPI_LAYER["MPI Layer"]
        NCCL_LAYER["NCCL Layer"]
        P2P_MODES["P2P Communication Modes"]
    end
    
    subgraph "Hardware Integration"
        CUDA_LIBS["CUDA Libraries"]
        GRACE_LIBS["Grace/NVPL Libraries"]
        DEVICE_MGMT["Device Management"]
    end
    
    MAIN --> HPCG_INIT
    HPCG_INIT --> HPCG_PARAMS
    HPCG_INIT --> INIT_RANKS
    
    INIT_RANKS --> GPUONLY
    INIT_RANKS --> CPUONLY
    INIT_RANKS --> GPUCPU
    
    MAIN --> PHASES
    PHASES --> MPI_LAYER
    PHASES --> NCCL_LAYER
    
    GPUONLY --> CUDA_LIBS
    CPUONLY --> GRACE_LIBS
    GPUCPU --> CUDA_LIBS
    GPUCPU --> GRACE_LIBS
    
    P2P_MODES --> MPI_LAYER
    P2P_MODES --> NCCL_LAYER
```

**Sources:** [src/main.cpp:135-872](), [src/hpcg.hpp:109-144](), [src/init.cpp:112-248]()

## Program Controller Architecture

The central program controller in `main()` orchestrates the entire benchmark execution through a well-defined sequence of phases. This controller manages hardware resources, coordinates between execution modes, and ensures proper sequencing of benchmark operations.

### Main Execution Flow

```mermaid
flowchart TD
    START["main() Entry"] --> MPI_INIT["MPI_Init()"]
    MPI_INIT --> PARAM_INIT["HPCG_Init()"]
    PARAM_INIT --> RANK_INIT["InitializeRanks()"]
    
    RANK_INIT --> VALIDATION["Parameter Validation"]
    VALIDATION --> LIB_CHECK["Library Version Checks"]
    
    LIB_CHECK --> PROBLEM_SETUP["Problem Setup Phase"]
    PROBLEM_SETUP --> GEOM_GEN["GenerateGeometry()"]
    GEOM_GEN --> SPARSE_INIT["InitializeSparseMatrix()"]
    SPARSE_INIT --> PROBLEM_GEN["GenerateProblem()"]
    PROBLEM_GEN --> HALO_SETUP["SetupHalo()"]
    HALO_SETUP --> COARSE_GEN["GenerateCoarseProblem()"]
    
    COARSE_GEN --> REF_TIMING["Reference Timing Phase"]
    REF_TIMING --> SPMV_REF["ComputeSPMV_ref()"]
    SPMV_REF --> MG_REF["ComputeMG_ref()"]
    MG_REF --> CG_REF["CG_ref()"]
    
    CG_REF --> OPTIMIZATION["OptimizeProblem()"]
    OPTIMIZATION --> VALIDATION_PHASE["Validation Phase"]
    VALIDATION_PHASE --> TEST_CG["TestCG()"]
    TEST_CG --> TEST_SYM["TestSymmetry()"]
    
    TEST_SYM --> BENCHMARK["Benchmark Phase"]
    BENCHMARK --> CG_LOOP["CG() Loop"]
    CG_LOOP --> RESULTS["ReportResults()"]
    RESULTS --> CLEANUP["Resource Cleanup"]
    CLEANUP --> END["Program Exit"]
```

**Sources:** [src/main.cpp:284-872]()

## Parameter and Configuration System

The configuration system is centered around the `HPCG_Params` structure, which encapsulates all runtime parameters and execution modes. This system supports both command-line and file-based configuration, with comprehensive parameter validation.

### Parameter Structure

| Parameter Category | Key Parameters | Purpose |
|-------------------|----------------|---------|
| **Execution Mode** | `exec_mode`, `rank_type` | Defines GPU/CPU execution strategy |
| **Problem Size** | `nx`, `ny`, `nz` | Local problem dimensions |
| **Process Grid** | `npx`, `npy`, `npz` | MPI process grid layout |
| **Communication** | `p2_mode` | Point-to-point communication method |
| **Optimization** | `use_l2compression`, `gpu_slice_size` | Performance optimization flags |
| **Runtime** | `runningTime`, `benchmark_mode` | Execution time and testing mode |

```mermaid
graph TB
    subgraph "Parameter Sources"
        CMD_LINE["Command Line Args"]
        HPCG_DAT["hpcg.dat File"]
        ENV_VARS["Environment Variables"]
    end
    
    subgraph "Parameter Processing"
        READ_HPCG["ReadHpcgDat()"]
        PARSE_ARGS["Argument Parsing"]
        VALIDATION["Parameter Validation"]
    end
    
    subgraph "Configuration Output"
        HPCG_PARAMS_STRUCT["HPCG_Params Structure"]
        EXEC_MODE["exec_mode_t"]
        RANK_TYPE["rank_type_t"]
        P2P_MODE["p2p_comm_mode_t"]
    end
    
    CMD_LINE --> PARSE_ARGS
    HPCG_DAT --> READ_HPCG
    ENV_VARS --> PARSE_ARGS
    
    PARSE_ARGS --> VALIDATION
    READ_HPCG --> VALIDATION
    
    VALIDATION --> HPCG_PARAMS_STRUCT
    HPCG_PARAMS_STRUCT --> EXEC_MODE
    HPCG_PARAMS_STRUCT --> RANK_TYPE
    HPCG_PARAMS_STRUCT --> P2P_MODE
```

**Sources:** [src/hpcg.hpp:109-144](), [src/init.cpp:250-444]()

## Rank Assignment and Execution Modes

The rank assignment system automatically determines whether each MPI rank operates as a GPU or CPU rank based on the execution mode and available hardware. This system supports three distinct execution modes with different resource allocation strategies.

### Rank Assignment Logic

```mermaid
graph TD
    INIT_RANKS["InitializeRanks()"] --> GET_GLOBAL["Get Global MPI Info"]
    GET_GLOBAL --> SPLIT_COMM["Split MPI Communicators"]
    SPLIT_COMM --> CHECK_MODE{"Check exec_mode"}
    
    CHECK_MODE -->|CPUONLY| CPU_ASSIGN["Set rank_type = CPU"]
    CHECK_MODE -->|GPUONLY| GPU_ASSIGN["Set rank_type = GPU"]
    CHECK_MODE -->|GPUCPU| HYBRID_ASSIGN["Hybrid Assignment"]
    
    HYBRID_ASSIGN --> CALC_RANKS["Calculate ranks_for_numa"]
    CALC_RANKS --> CHECK_LOCAL{"local_rank % ranks_for_numa == 0?"}
    
    CHECK_LOCAL -->|Yes| ASSIGN_GPU["rank_type = GPU"]
    CHECK_LOCAL -->|No| ASSIGN_CPU["rank_type = CPU"]
    
    ASSIGN_GPU --> SET_DEVICE["cudaSetDevice()"]
    ASSIGN_CPU --> SET_PRINT["Set cpu_allowed_to_print"]
    
    GPU_ASSIGN --> SET_DEVICE
    CPU_ASSIGN --> CPU_ONLY_SETUP["CPU-Only Setup"]
    
    SET_DEVICE --> NCCL_CHECK{"P2P_Mode == NCCL?"}
    NCCL_CHECK -->|Yes| NCCL_INIT["ncclCommInitRank()"]
    NCCL_CHECK -->|No| FINISH["Assignment Complete"]
    NCCL_INIT --> FINISH
    CPU_ONLY_SETUP --> FINISH
    SET_PRINT --> FINISH
```

**Sources:** [src/init.cpp:112-248]()

## Hardware Integration Architecture

The system integrates with different hardware accelerators through abstracted interfaces that handle library initialization, device management, and resource allocation. Each execution mode activates specific hardware integration paths.

### Library Integration

```mermaid
graph TB
    subgraph "GPU Integration"
        CUDA_CHECK["CUDA Runtime Check"]
        CUSPARSE_INIT["cusparseCreate()"]
        CUBLAS_INIT["cublasCreate()"]
        STREAM_CREATE["cudaStreamCreate()"]
        DEVICE_SET["cudaSetDevice()"]
    end
    
    subgraph "CPU Integration"
        GRACE_CHECK["Grace Architecture Check"]
        NVPL_INIT["nvpl_sparse_create()"]
        THREAD_SETUP["OpenMP Thread Setup"]
    end
    
    subgraph "Communication Setup"
        MPI_INIT_COMM["MPI Initialization"]
        NCCL_SETUP["NCCL Communicator Setup"]
        P2P_MODE_SELECT["P2P Mode Selection"]
    end
    
    RANK_TYPE{"rank_type"} -->|GPU| CUDA_CHECK
    RANK_TYPE -->|CPU| GRACE_CHECK
    
    CUDA_CHECK --> CUSPARSE_INIT
    CUSPARSE_INIT --> CUBLAS_INIT
    CUBLAS_INIT --> STREAM_CREATE
    STREAM_CREATE --> DEVICE_SET
    
    GRACE_CHECK --> NVPL_INIT
    NVPL_INIT --> THREAD_SETUP
    
    DEVICE_SET --> P2P_MODE_SELECT
    THREAD_SETUP --> P2P_MODE_SELECT
    
    P2P_MODE_SELECT --> MPI_INIT_COMM
    P2P_MODE_SELECT --> NCCL_SETUP
```

**Sources:** [src/main.cpp:310-350](), [src/main.cpp:361-424](), [src/init.cpp:180-246]()

## Communication Architecture

The communication system supports multiple point-to-point communication modes, allowing optimization for different network configurations and hardware capabilities. The system automatically selects appropriate communication patterns based on execution mode and hardware availability.

### Supported Communication Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `MPI_CPU` | Standard MPI with CPU buffers | Basic CPU-only execution |
| `MPI_CPU_All2allv` | MPI All-to-all with CPU buffers | CPU-optimized collective operations |
| `MPI_CUDA_AWARE` | CUDA-aware MPI | GPU memory direct access |
| `MPI_GPU_All2allv` | GPU-optimized All-to-all | GPU collective operations |
| `NCCL` | NVIDIA Collective Communications | Multi-GPU scaling |

```mermaid
graph TB
    P2P_SELECTION["P2P Mode Selection"] --> EXEC_CHECK{"Execution Mode"}
    
    EXEC_CHECK -->|CPUONLY| CPU_MODES["CPU Communication Modes"]
    EXEC_CHECK -->|GPUONLY| GPU_MODES["GPU Communication Modes"]
    EXEC_CHECK -->|GPUCPU| HYBRID_MODES["Hybrid Communication"]
    
    CPU_MODES --> MPI_CPU["MPI_CPU"]
    CPU_MODES --> MPI_CPU_ALL2ALL["MPI_CPU_All2allv"]
    
    GPU_MODES --> MPI_CUDA_AWARE["MPI_CUDA_AWARE"]
    GPU_MODES --> MPI_GPU_ALL2ALL["MPI_GPU_All2allv"]
    GPU_MODES --> NCCL["NCCL"]
    
    HYBRID_MODES --> MIXED_P2P["Mixed P2P Patterns"]
    
    MPI_CPU --> VALIDATION["Mode Validation"]
    MPI_CPU_ALL2ALL --> VALIDATION
    MPI_CUDA_AWARE --> VALIDATION
    MPI_GPU_ALL2ALL --> VALIDATION
    NCCL --> VALIDATION
    MIXED_P2P --> VALIDATION
    
    VALIDATION --> COMM_INIT["Communication Initialization"]
```

**Sources:** [src/main.cpp:106-108](), [src/init.cpp:378-389](), [src/main.cpp:181-221]()

---

