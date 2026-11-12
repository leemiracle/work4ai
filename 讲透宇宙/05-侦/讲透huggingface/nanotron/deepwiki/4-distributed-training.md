<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/nanotron · page 4 Distributed Training · fetched 2026-10-26 -->

# Distributed Training

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/nanotron/distributed.py](src/nanotron/distributed.py)
- [src/nanotron/parallel/context.py](src/nanotron/parallel/context.py)
- [tests/helpers/utils.py](tests/helpers/utils.py)
- [tests/test_distributed.py](tests/test_distributed.py)

</details>



This document covers Nanotron's distributed training architecture, which enables efficient large-scale model training across multiple GPUs and nodes using 3D parallelism (tensor, pipeline, and data parallelism). The distributed training system manages process groups, communication patterns, and coordination between different parallelism strategies.

For specific parallelism implementation details, see [Tensor Parallelism](#4.3), [Pipeline Parallelism](#4.4), and [3D Parallelism](#4.2). For cluster deployment, see [Multi-Node Training](#4.5). For process group management, see [Parallel Context](#4.1).

## Architecture Overview

Nanotron's distributed training system is built around the `ParallelContext` class, which acts as the central coordinator for all distributed operations. The system supports multiple forms of parallelism simultaneously and manages the complex process group topology required for efficient communication.

### Distributed Training System Architecture

```mermaid
graph TB
    subgraph "Initialization Layer"
        ENV["Environment Variables<br/>WORLD_SIZE, RANK, LOCAL_RANK"]
        InitTorch["initialize_torch_distributed()"]
        SetupDist["setup_dist_env()"]
    end
    
    subgraph "Core Coordination"
        PC["ParallelContext<br/>Central Coordinator"]
        WorldPG["world_pg<br/>Global Process Group"]
        RankMatrix["world_rank_matrix<br/>5D Rank Mapping"]
    end
    
    subgraph "Process Groups"
        TPPG["tp_pg<br/>Tensor Parallel"]
        PPPG["pp_pg<br/>Pipeline Parallel"]
        DPPG["dp_pg<br/>Data Parallel"]
        CPPG["cp_pg<br/>Context Parallel"]
        EPPG["ep_pg<br/>Expert Parallel"]
    end
    
    subgraph "Communication Primitives"
        ReduceScatter["reduce_scatter_tensor()"]
        AllGather["all_gather_into_tensor()"]
        AllReduce["all_reduce_coalesced()"]
        NewGroup["new_group()"]
    end
    
    ENV --> InitTorch
    InitTorch --> PC
    SetupDist --> PC
    PC --> WorldPG
    PC --> RankMatrix
    RankMatrix --> TPPG
    RankMatrix --> PPPG
    RankMatrix --> DPPG
    RankMatrix --> CPPG
    RankMatrix --> EPPG
    
    PC --> ReduceScatter
    PC --> AllGather
    PC --> AllReduce
    PC --> NewGroup
```

Sources: [src/nanotron/parallel/context.py:12-183](), [src/nanotron/distributed.py:249-279](), [tests/helpers/utils.py:246-276]()

## ParallelContext Core Components

The `ParallelContext` class manages the initialization and coordination of all distributed training components. It creates and maintains process groups for different parallelism strategies and provides utilities for rank mapping and communication.

### ParallelContext Initialization Flow

```mermaid
sequenceDiagram
    participant Init as "Initialization"
    participant PC as "ParallelContext.__init__()"
    participant Env as "Environment Setup"
    participant PG as "Process Group Creation"
    participant Matrix as "Rank Matrix Setup"
    
    Init->>PC: "tensor_parallel_size=tp<br/>pipeline_parallel_size=pp<br/>data_parallel_size=dp"
    PC->>Env: "Read WORLD_SIZE, RANK<br/>Assert tp*pp*dp == world_size"
    PC->>PC: "set_device()<br/>Set CUDA device"
    PC->>PG: "initialize_torch_distributed()<br/>Init base process group"
    PC->>Matrix: "_init_parallel_groups()<br/>Create 5D rank matrix"
    Matrix->>PG: "create_new_group()<br/>tp_pg, pp_pg, dp_pg, etc."
    PG->>PC: "Return initialized context"
```

Sources: [src/nanotron/parallel/context.py:13-58](), [src/nanotron/parallel/context.py:59-122]()

## Process Group Management

The distributed training system uses a 5-dimensional rank matrix to organize processes across different parallelism dimensions. This matrix enables efficient creation of process groups for various communication patterns.

### Process Group Topology

```mermaid
graph TB
    subgraph "5D Rank Matrix Organization"
        Matrix["world_rank_matrix[ep, pp, dp, cp, tp]<br/>Shape: (expert_parallel_size,<br/>pipeline_parallel_size,<br/>data_parallel_size,<br/>context_parallel_size,<br/>tensor_parallel_size)"]
    end
    
    subgraph "Primary Process Groups"
        TP["tp_pg<br/>Tensor Parallel Group<br/>ranks.transpose((0,1,2,3,4))"]
        CP["cp_pg<br/>Context Parallel Group<br/>ranks.transpose((4,0,1,2,3))"]
        DP["dp_pg<br/>Data Parallel Group<br/>ranks.transpose((3,4,0,1,2))"]
        PP["pp_pg<br/>Pipeline Parallel Group<br/>ranks.transpose((2,3,4,0,1))"]
        EP["ep_pg<br/>Expert Parallel Group<br/>ranks.transpose((1,2,3,4,0))"]
    end
    
    subgraph "Composite Process Groups"
        MP["mp_pg<br/>Model Parallel<br/>(TP + PP + EP)"]
        DPCP["dp_cp_pg<br/>Data + Context Parallel"]
        TPEP["tp_and_ep_pg<br/>Tensor + Expert Parallel"]
    end
    
    Matrix --> TP
    Matrix --> CP
    Matrix --> DP  
    Matrix --> PP
    Matrix --> EP
    
    TP --> MP
    PP --> MP
    EP --> MP
    
    DP --> DPCP
    CP --> DPCP
    
    TP --> TPEP
    EP --> TPEP
```

Sources: [src/nanotron/parallel/context.py:62-122](), [src/nanotron/parallel/context.py:123-141]()

## Communication Primitives

Nanotron provides optimized communication primitives that wrap PyTorch's distributed operations with additional functionality for version compatibility and error handling.

| Function | Purpose | Key Features |
|----------|---------|--------------|
| `reduce_scatter_tensor()` | Reduce and scatter tensors | PyTorch 1.12+ compatibility |
| `all_gather_into_tensor()` | Gather tensors from all ranks | Memory-efficient gathering |
| `reduce_scatter_coalesced()` | Batch reduce-scatter operations | Coalesced for efficiency |
| `all_gather_coalesced()` | Batch all-gather operations | NCCL-compatible implementation |
| `all_reduce_coalesced()` | Batch all-reduce operations | Single-rank optimization |
| `new_group()` | Create process groups | Timeout and validation |

Sources: [src/nanotron/distributed.py:21-153](), [src/nanotron/distributed.py:225-247]()

## Rank Management and Utilities

The system provides utilities for converting between local ranks in different parallelism dimensions and global ranks, enabling flexible communication patterns.

### Rank Conversion System

```mermaid
graph LR
    subgraph "Rank Conversion"
        LocalRanks["Local Ranks<br/>{ep: 0, pp: 1, dp: 0, cp: 0, tp: 1}"]
        GlobalRank["Global Rank<br/>get_global_rank()"]
        WorldMatrix["world_rank_matrix<br/>5D Array Lookup"]
    end
    
    subgraph "Process Group Utilities"
        GetRank["get_rank(group)<br/>Safe rank retrieval"]
        GetGlobalRanks["get_global_ranks(group)<br/>All ranks in group"]
        CreateGroup["create_new_group()<br/>Distributed group creation"]
    end
    
    LocalRanks --> WorldMatrix
    WorldMatrix --> GlobalRank
    GlobalRank --> GetRank
    GetRank --> GetGlobalRanks
    GetGlobalRanks --> CreateGroup
```

Sources: [src/nanotron/parallel/context.py:151-182](), [src/nanotron/distributed.py:225-247]()

## Testing and Development Support

The distributed training system includes comprehensive testing utilities that support various GPU configurations and automatically handle common distributed training issues.

### Testing Infrastructure

```mermaid
graph TB
    subgraph "Test Configuration"
        AllConfigs["get_all_3d_configurations()<br/>Generate all valid (tp,pp,dp) combinations"]
        AvailableGPUs["available_gpus()<br/>Detect usable GPU devices"]
        RerunDecorator["@rerun_if_address_is_in_use<br/>Handle port conflicts"]
    end
    
    subgraph "Test Execution"
        InitDist["@init_distributed(tp,dp,pp)<br/>Setup distributed environment"]
        GlobalWrapper["global_wrapper()<br/>Per-process setup"]
        MPSpawn["mp.spawn()<br/>Multi-process execution"]
    end
    
    subgraph "Test Validation"
        ValidatePC["_test_init_parallel_context()<br/>Verify ParallelContext setup"]
        ValidatePG["isinstance(pg, ProcessGroup)<br/>Check process group types"]
        ValidateRanks["Assert global_rank == dist.get_rank()<br/>Verify rank consistency"]
    end
    
    AllConfigs --> InitDist
    AvailableGPUs --> InitDist
    RerunDecorator --> InitDist
    
    InitDist --> GlobalWrapper
    GlobalWrapper --> MPSpawn
    MPSpawn --> ValidatePC
    ValidatePC --> ValidatePG
    ValidatePG --> ValidateRanks
```

Sources: [tests/helpers/utils.py:110-276](), [tests/test_distributed.py:14-46]()

## Environment Setup Requirements

Distributed training requires specific environment variables to be set for proper initialization:

| Environment Variable | Purpose | Example |
|---------------------|---------|---------|
| `WORLD_SIZE` | Total number of processes | `8` |
| `RANK` | Global rank of current process | `0-7` |
| `LOCAL_RANK` | Local rank on current node | `0-7` |
| `LOCAL_WORLD_SIZE` | Processes per node | `8` |
| `MASTER_ADDR` | Master node address | `"localhost"` |
| `MASTER_PORT` | Master node port | `29500` |

The system automatically validates that the parallelism configuration matches the available world size: `tensor_parallel_size * pipeline_parallel_size * data_parallel_size * context_parallel_size * expert_parallel_size == WORLD_SIZE`.

Sources: [src/nanotron/parallel/context.py:23-28](), [src/nanotron/distributed.py:249-279](), [tests/helpers/utils.py:247-258]()

---

