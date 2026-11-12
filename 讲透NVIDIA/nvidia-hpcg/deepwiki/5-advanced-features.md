<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvidia-hpcg · page 5 Advanced Features · fetched 2026-10-26 -->

# Advanced Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/ExchangeHalo.cpp](src/ExchangeHalo.cpp)
- [src/GenerateCoarseProblem.cpp](src/GenerateCoarseProblem.cpp)
- [src/OptimizeProblem.cpp](src/OptimizeProblem.cpp)

</details>



## Purpose and Scope

This document covers the specialized functionality that enables high-performance execution in NVIDIA HPCG, including multigrid preconditioning methods, distributed memory support, and performance optimization techniques. These advanced features work together to achieve optimal performance on heterogeneous HPC systems with GPU and Grace CPU configurations.

For information about the basic computational engines that execute these optimized algorithms, see [Computational Engines](#4). For details about the core data structures these features operate on, see [Core Data Structures](#3.3).

## Advanced Features Architecture

The advanced features system consists of three interconnected subsystems that transform and optimize the benchmark execution:

### High-Level System Integration

```mermaid
graph TB
    subgraph "Benchmark Execution Flow"
        INIT["Problem Initialization"]
        OPT["OptimizeProblem()"]
        MG["GenerateCoarseProblem()"]
        SOLVE["CG Solver Execution"]
    end
    
    subgraph "Performance Optimization Layer"
        GRAPH_COLOR["Graph Coloring<br/>ColorMatrixCuda/Cpu"]
        MATRIX_PERM["Matrix Permutation<br/>ref2opt/opt2ref"]
        SELL_CONV["SELL Format Conversion<br/>EllPermColumnsValuesCuda"]
        CUSPARSE_SETUP["cuSPARSE/NVPL Setup<br/>cusparseCreateSlicedEll"]
    end
    
    subgraph "Multigrid Hierarchy"
        COARSE_GEN["Coarse Problem Generation<br/>GenerateCoarseProblem"]
        F2C_OP["Fine-to-Coarse Mapping<br/>f2cOperator"]
        MG_DATA["MGData Structure<br/>InitializeMGData"]
        GEOMETRY["Coarse Geometry<br/>GenerateGeometry"]
    end
    
    subgraph "Distributed Communication"
        HALO_EX["Halo Exchange<br/>ExchangeHalo"]
        P2P_MODE["Communication Mode<br/>P2P_Mode"]
        MPI_OPS["MPI Operations<br/>MPI_Irecv/Send/Alltoallv"]
        NEIGHBOR_COMM["Neighbor Communication<br/>neighborsPhysical"]
    end
    
    INIT --> OPT
    OPT --> GRAPH_COLOR
    OPT --> MATRIX_PERM
    OPT --> SELL_CONV
    OPT --> CUSPARSE_SETUP
    
    OPT --> MG
    MG --> COARSE_GEN
    MG --> F2C_OP
    MG --> MG_DATA
    MG --> GEOMETRY
    
    SOLVE --> HALO_EX
    HALO_EX --> P2P_MODE
    HALO_EX --> MPI_OPS
    HALO_EX --> NEIGHBOR_COMM
    
    OPT --> SOLVE
    MG --> SOLVE
    
    style OPT fill:#f9f9f9,stroke:#333,stroke-width:2px
    style MG fill:#f9f9f9,stroke:#333,stroke-width:2px
    style HALO_EX fill:#f9f9f9,stroke:#333,stroke-width:2px
```

Sources: [src/OptimizeProblem.cpp:410-427](), [src/GenerateCoarseProblem.cpp:65-157](), [src/ExchangeHalo.cpp:54-119]()

### Data Structure Transformation Pipeline

```mermaid
flowchart TD
    subgraph "Input Data Structures"
        SPARSE_IN["SparseMatrix A<br/>Original CSR Format"]
        VECTOR_IN["Vector x, b<br/>Original Layout"]
        GEOM_IN["Geometry<br/>Fine Grid"]
    end
    
    subgraph "Optimization Transformations"
        COLOR["Graph Coloring<br/>gpuAux.color<br/>cpuAux.nRowsWithColor"]
        PERM["Permutation Arrays<br/>ref2opt[]<br/>opt2ref[]"]
        SELL["SELL Conversion<br/>sellAPermColumns<br/>sellAPermValues"]
        SLICE["Sliced Format<br/>sellLSliceMrl<br/>sellUSliceMrl"]
    end
    
    subgraph "Multigrid Hierarchy"
        COARSE_MAT["Coarse SparseMatrix Ac<br/>Reduced Dimensions"]
        F2C["f2cOperator[]<br/>Fine-to-Coarse Mapping"]
        MG_STRUCT["MGData Structure<br/>rc, xc, Axf vectors"]
        COARSE_GEOM["Coarse Geometry<br/>nxc, nyc, nzc"]
    end
    
    subgraph "Communication Structures"
        SEND_BUF["sendBuffer[]<br/>elementsToSend[]"]
        RECV_BUF["receiveLength[]<br/>sendLength[]"]
        NEIGHBORS["neighborsPhysical[]<br/>numberOfSendNeighbors"]
        P2P_CONFIG["P2P_Mode Configuration<br/>MPI_CPU/MPI_CPU_All2allv"]
    end
    
    subgraph "Optimized Output"
        GPU_MAT["cuSPARSE Matrices<br/>matL, matU, matA"]
        CPU_MAT["NVPL Sparse Matrices<br/>nvplSparseOpt"]
        OPT_VECTORS["Optimized Vectors<br/>Permuted Layout"]
    end
    
    SPARSE_IN --> COLOR
    COLOR --> PERM
    PERM --> SELL
    SELL --> SLICE
    
    SPARSE_IN --> COARSE_MAT
    GEOM_IN --> COARSE_GEOM
    COARSE_MAT --> F2C
    F2C --> MG_STRUCT
    
    SPARSE_IN --> SEND_BUF
    SEND_BUF --> RECV_BUF
    RECV_BUF --> NEIGHBORS
    NEIGHBORS --> P2P_CONFIG
    
    SLICE --> GPU_MAT
    SLICE --> CPU_MAT
    VECTOR_IN --> OPT_VECTORS
    
    style COLOR fill:#f9f9f9,stroke:#333,stroke-width:2px
    style COARSE_MAT fill:#f9f9f9,stroke:#333,stroke-width:2px
    style P2P_CONFIG fill:#f9f9f9,stroke:#333,stroke-width:2px
```

Sources: [src/OptimizeProblem.cpp:77-123](), [src/GenerateCoarseProblem.cpp:69-152](), [src/ExchangeHalo.cpp:57-66]()

## Feature Subsystems

### Multigrid Methods

Multigrid preconditioning is implemented through hierarchical coarse problem generation that reduces computational complexity. The `GenerateCoarseProblem` function creates a four-level multigrid hierarchy where each coarse level has dimensions that are half of the fine level in each direction.

Key components include:
- **Coarse grid generation**: Dimensions `nxc = nxf/2`, `nyc = nyf/2`, `nzc = nzf/2`
- **Fine-to-coarse mapping**: `f2cOperator` array maps fine grid points to coarse grid points
- **Multigrid data structure**: `MGData` contains restriction/prolongation operators and auxiliary vectors

For detailed implementation, see [Multigrid Methods](#5.1).

### Distributed Computing

MPI-based distributed memory support enables multi-node scaling through efficient boundary data exchange. The `ExchangeHalo` function implements neighbor communication with multiple communication modes optimized for different network configurations.

Key components include:
- **Communication modes**: `P2P_Mode` supports `MPI_CPU` and `MPI_CPU_All2allv`
- **Neighbor topology**: `neighborsPhysical` array defines communication partners
- **Buffer management**: `sendBuffer` and receive buffers handle boundary data

For detailed implementation, see [Distributed Computing](#5.2).

### Performance Optimization

Matrix optimization transforms the sparse matrix data structures to achieve optimal memory access patterns and leverage hardware-specific libraries. The `OptimizeProblem` function applies graph coloring, permutation, and format conversion techniques.

Key components include:
- **Graph coloring**: Eliminates data dependencies for parallel execution
- **Matrix permutation**: `ref2opt` and `opt2ref` arrays reorder matrix elements
- **SELL format**: Sliced ELLPACK format optimizes memory bandwidth utilization
- **Hardware libraries**: Integration with cuSPARSE (GPU) and NVPL Sparse (CPU)

For detailed implementation, see [Performance Optimization](#5.3).

## Integration Points

These advanced features are tightly integrated within the benchmark execution flow:

| Feature | Integration Point | Primary Function | Data Structures |
|---------|------------------|------------------|-----------------|
| Performance Optimization | After problem generation | `OptimizeProblem()` | `SparseMatrix`, permutation arrays |
| Multigrid Methods | During optimization phase | `GenerateCoarseProblem()` | `MGData`, coarse matrices |
| Distributed Computing | During solver execution | `ExchangeHalo()` | Communication buffers, neighbor lists |

The optimization phase transforms all data structures before solver execution, multigrid hierarchy is established during problem setup, and halo exchange occurs during iterative solving to maintain data consistency across distributed memory boundaries.

Sources: [src/OptimizeProblem.cpp:410-434](), [src/GenerateCoarseProblem.cpp:65-157](), [src/ExchangeHalo.cpp:38-121]()

---

