<!-- source: DeepWiki mcp.deepwiki.com · repo pytorch/torchrec · page 4 Distributed Training · fetched 2026-10-21 -->

# Distributed Training

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [torchrec/distributed/batched_embedding_kernel.py](torchrec/distributed/batched_embedding_kernel.py)
- [torchrec/distributed/embedding.py](torchrec/distributed/embedding.py)
- [torchrec/distributed/embedding_kernel.py](torchrec/distributed/embedding_kernel.py)
- [torchrec/distributed/embedding_lookup.py](torchrec/distributed/embedding_lookup.py)
- [torchrec/distributed/embeddingbag.py](torchrec/distributed/embeddingbag.py)
- [torchrec/distributed/model_parallel.py](torchrec/distributed/model_parallel.py)
- [torchrec/distributed/quant_embedding_kernel.py](torchrec/distributed/quant_embedding_kernel.py)
- [torchrec/distributed/tests/test_utils.py](torchrec/distributed/tests/test_utils.py)
- [torchrec/distributed/types.py](torchrec/distributed/types.py)
- [torchrec/distributed/utils.py](torchrec/distributed/utils.py)
- [torchrec/quant/embedding_modules.py](torchrec/quant/embedding_modules.py)
- [torchrec/quant/tests/test_embedding_modules.py](torchrec/quant/tests/test_embedding_modules.py)

</details>



This document covers TorchRec's distributed training capabilities, including model parallelization, embedding sharding strategies, and communication primitives. For information about embedding modules themselves, see [Embedding Modules](#3). For details about data structures used in distributed training, see [Core Data Structures](#2).

## Overview

TorchRec provides distributed training capabilities specifically designed for large-scale recommendation models with massive embedding tables. The system enables model parallelism across multiple GPUs/nodes by sharding embedding tables according to different strategies while maintaining the illusion of a single unified model.

The distributed training system consists of three main components:
- **Model Parallelization Layer**: `DistributedModelParallel` wrapper and sharding planning
- **Distributed Embedding Collections**: Sharded versions of embedding modules
- **Communication Infrastructure**: Primitives for data redistribution across ranks

## System Architecture

```mermaid
graph TB
    subgraph "User Model"
        UserModel["User Model"]
        EBC["EmbeddingBagCollection"]
        EC["EmbeddingCollection"]
    end
    
    subgraph "Model Parallelization"
        DMP["DistributedModelParallel"]
        SP["ShardingPlan"]
        ESP["EmbeddingShardingPlanner"]
    end
    
    subgraph "Sharded Collections"
        SEBC["ShardedEmbeddingBagCollection"]
        SEC["ShardedEmbeddingCollection"]
        SQEBC["ShardedQuantEmbeddingCollection"]
    end
    
    subgraph "Sharding Strategies"
        RW["RwPooledEmbeddingSharding"]
        TW["TwPooledEmbeddingSharding"]
        CW["CwPooledEmbeddingSharding"]
        DP["DpPooledEmbeddingSharding"]
    end
    
    subgraph "Communication"
        KJTA2A["KJTAllToAll"]
        PEA2A["PooledEmbeddingsAllToAll"]
    end
    
    UserModel --> DMP
    EBC --> SEBC
    EC --> SEC
    DMP --> SP
    ESP --> SP
    SP --> SEBC
    SP --> SEC
    SEBC --> RW
    SEBC --> TW
    SEBC --> CW
    SEBC --> DP
    RW --> KJTA2A
    TW --> PEA2A
```

**TorchRec Distributed Training Architecture**

Sources: [torchrec/distributed/model_parallel.py:196-298](), [torchrec/distributed/embeddingbag.py:454-610](), [torchrec/distributed/embedding.py:397-511]()

## DistributedModelParallel

`DistributedModelParallel` is the main entry point for distributed training in TorchRec. It wraps a user model and applies sharding to embedding modules while leaving other modules for data parallelism.

```mermaid
graph TD
    subgraph "DistributedModelParallel Initialization"
        UserModule["User Module"]
        Sharders["ModuleSharder List"]
        Plan["ShardingPlan"]
        Env["ShardingEnv"]
    end
    
    subgraph "Planning Phase"
        ESP["EmbeddingShardingPlanner"]
        Topology["Topology"]
        CollectivePlan["collective_plan()"]
    end
    
    subgraph "Sharding Phase"
        InitDMP["_init_dmp()"]
        ShardedModules["Sharded Modules"]
        UnshardedModules["Unsharded Modules"]
    end
    
    subgraph "Data Parallel Phase"
        DDP["DistributedDataParallel"]
        FSDP["FullyShardedDataParallel"]
    end
    
    UserModule --> ESP
    Sharders --> ESP
    Topology --> ESP
    ESP --> Plan
    Plan --> InitDMP
    InitDMP --> ShardedModules
    InitDMP --> UnshardedModules
    UnshardedModules --> DDP
    UnshardedModules --> FSDP
```

**DistributedModelParallel Processing Flow**

The `DistributedModelParallel` class performs the following steps:

1. **Planning**: Uses `EmbeddingShardingPlanner` to determine optimal sharding strategy
2. **Sharding**: Converts embedding modules to their sharded equivalents
3. **Data Parallel Wrapping**: Applies DDP/FSDP to non-sharded modules

Key methods:
- `__init__()`: Initializes the distributed wrapper with sharding plan
- `init_data_parallel()`: Applies data parallelism to unsharded modules
- `forward()`: Delegates to the wrapped module

Sources: [torchrec/distributed/model_parallel.py:196-300](), [torchrec/distributed/planner.py](), [torchrec/distributed/types.py:601-710]()

## Sharding Strategies

TorchRec supports multiple embedding sharding strategies, each optimized for different scenarios:

```mermaid
graph LR
    subgraph "Sharding Types"
        DP["DATA_PARALLEL<br/>Replicated"]
        TW["TABLE_WISE<br/>Whole tables per rank"]
        RW["ROW_WISE<br/>Split by rows"]
        CW["COLUMN_WISE<br/>Split by columns"]
        TWRW["TABLE_ROW_WISE<br/>Hierarchical"]
        Grid["GRID_SHARD<br/>2D distribution"]
    end
    
    subgraph "Implementation Classes"
        DpSharding["DpPooledEmbeddingSharding"]
        TwSharding["TwPooledEmbeddingSharding"]
        RwSharding["RwPooledEmbeddingSharding"]
        CwSharding["CwPooledEmbeddingSharding"]
        TwRwSharding["TwRwPooledEmbeddingSharding"]
        GridSharding["GridPooledEmbeddingSharding"]
    end
    
    DP --> DpSharding
    TW --> TwSharding
    RW --> RwSharding
    CW --> CwSharding
    TWRW --> TwRwSharding
    Grid --> GridSharding
```

**Embedding Sharding Strategies and Implementations**

### Strategy Details

| Strategy | Description | Use Case |
|----------|-------------|----------|
| `DATA_PARALLEL` | Tables replicated on all ranks | Small tables, minimal communication |
| `TABLE_WISE` | Complete tables on single ranks | Medium tables, balanced load |
| `ROW_WISE` | Tables split by embedding rows | Large tables, memory constraints |
| `COLUMN_WISE` | Tables split by embedding dimensions | Wide embeddings, computation parallelism |
| `TABLE_ROW_WISE` | Table-wise across nodes, row-wise within nodes | Multi-node scenarios |
| `GRID_SHARD` | 2D sharding combining CW and TWRW | Very large tables, complex topologies |

The sharding strategy is determined by `EmbeddingShardingPlanner` based on:
- Table sizes and memory constraints
- Network topology and bandwidth
- Compute requirements

Sources: [torchrec/distributed/types.py:118-139](), [torchrec/distributed/sharding/](), [torchrec/distributed/embeddingbag.py:752-799]()

## Distributed Embedding Collections

Distributed embedding collections are sharded versions of the standard embedding modules. They handle the complexity of distributed execution while maintaining the same interface.

```mermaid
graph TB
    subgraph "Sharded Embedding Collections"
        SEBC["ShardedEmbeddingBagCollection"]
        SEC["ShardedEmbeddingCollection"]
        SQEBC["ShardedQuantEmbeddingCollection"]
    end
    
    subgraph "Internal Components"
        InputDist["Input Distribution"]
        Lookup["Embedding Lookup"]
        OutputDist["Output Distribution"]
    end
    
    subgraph "Sharding Context"
        EmbShardCtx["EmbeddingShardingContext"]
        SeqShardCtx["SequenceShardingContext"]
        EBCCtx["EmbeddingBagCollectionContext"]
    end
    
    SEBC --> InputDist
    SEC --> InputDist
    InputDist --> Lookup
    Lookup --> OutputDist
    OutputDist --> EmbShardCtx
    OutputDist --> SeqShardCtx
    OutputDist --> EBCCtx
```

**Sharded Embedding Collection Architecture**

### ShardedEmbeddingBagCollection

`ShardedEmbeddingBagCollection` is the distributed version of `EmbeddingBagCollection` that handles pooled embeddings.

Key components:
- **Input Distribution**: Redistributes sparse features according to sharding strategy
- **Lookup**: Performs local embedding lookup on sharded tables
- **Output Distribution**: Redistributes and combines results back to original layout

The class maintains three phases:
1. **Input Phase**: `_input_dists` modules handle feature redistribution
2. **Lookup Phase**: `_lookups` modules perform embedding table access
3. **Output Phase**: `_output_dists` modules redistribute results

Sources: [torchrec/distributed/embeddingbag.py:454-610](), [torchrec/distributed/embedding_sharding.py]()

### ShardedEmbeddingCollection

`ShardedEmbeddingCollection` handles sequence embeddings (non-pooled) with similar architecture but different output handling for jagged tensors.

Key differences from bag collections:
- Outputs `Dict[str, JaggedTensor]` instead of `KeyedTensor`
- Handles variable-length sequences per feature
- Supports sequence-level operations

Sources: [torchrec/distributed/embedding.py:397-511]()

## Communication Patterns

Distributed training requires specific communication patterns to redistribute data efficiently across ranks.

```mermaid
graph TB
    subgraph "Communication Flow"
        LocalFeatures["Local Features<br/>KeyedJaggedTensor"]
        InputA2A["AllToAll<br/>Feature Redistribution"]
        LocalLookup["Local Embedding<br/>Lookup"]
        OutputA2A["AllToAll<br/>Result Redistribution"]
        FinalResult["Final Results<br/>KeyedTensor"]
    end
    
    subgraph "Communication Primitives"
        KJTA2A["KJTAllToAll"]
        PEA2A["PooledEmbeddingsAllToAll"]
        SEA2A["SequenceEmbeddingsAllToAll"]
        RS["ReduceScatter"]
    end
    
    LocalFeatures --> InputA2A
    InputA2A --> LocalLookup
    LocalLookup --> OutputA2A
    OutputA2A --> FinalResult
    
    InputA2A -.-> KJTA2A
    OutputA2A -.-> PEA2A
    OutputA2A -.-> SEA2A
    OutputA2A -.-> RS
```

**Distributed Training Communication Flow**

### Communication Primitives

The communication layer provides specialized AllToAll operations:

1. **KJTAllToAll**: Redistributes sparse features (`KeyedJaggedTensor`) based on sharding strategy
2. **PooledEmbeddingsAllToAll**: Redistributes pooled embedding results
3. **SequenceEmbeddingsAllToAll**: Redistributes sequence embedding results
4. **ReduceScatter**: Aggregates gradients for row-wise sharded tables

### Three-Phase Execution

Distributed training follows a consistent three-phase pattern:

1. **Input Distribution**: Convert from data-parallel to model-parallel layout
   - Features are redistributed so each rank gets the features for its sharded tables
   
2. **Local Computation**: Each rank performs embedding lookup on its local shards
   - No communication required during this phase
   
3. **Output Distribution**: Convert from model-parallel back to data-parallel layout
   - Results are redistributed so each rank has complete embeddings for its batch

Sources: [torchrec/distributed/comm_ops.py](), [torchrec/distributed/dist_data.py](), [torchrec/distributed/embedding_sharding.py]()

## Training Flow

The complete distributed training flow integrates all components:

```mermaid
sequenceDiagram
    participant User as "User Code"
    participant DMP as "DistributedModelParallel"
    participant SEBC as "ShardedEmbeddingBagCollection"
    participant InputDist as "Input Distribution"
    participant Lookup as "Embedding Lookup"
    participant OutputDist as "Output Distribution"
    participant DDP as "DistributedDataParallel"
    
    User->>DMP: forward(features)
    DMP->>SEBC: forward(kjt)
    SEBC->>InputDist: distribute features
    InputDist-->>Lookup: local features
    Lookup->>Lookup: embedding lookup
    Lookup-->>OutputDist: local embeddings
    OutputDist->>SEBC: redistributed embeddings
    SEBC->>DMP: pooled embeddings
    DMP->>DDP: dense forward
    DMP->>User: model output
    
    Note over User,DDP: Backward pass follows reverse flow
```

**Distributed Training Execution Sequence**

### Initialization Process

1. **Model Creation**: User creates model with standard embedding modules
2. **DMP Wrapping**: `DistributedModelParallel` wraps the model
3. **Sharding Planning**: `EmbeddingShardingPlanner` determines optimal sharding
4. **Module Replacement**: Embedding modules are replaced with sharded equivalents
5. **Data Parallel Setup**: Remaining modules are wrapped with DDP/FSDP

### Forward Pass

1. **Feature Input**: `KeyedJaggedTensor` with sparse features
2. **Input Distribution**: Features redistributed according to sharding plan
3. **Local Lookup**: Each rank performs embedding lookup on local shards
4. **Output Distribution**: Results redistributed to original batch layout
5. **Dense Computation**: Standard forward pass through dense layers

### Backward Pass

Gradients flow in reverse order:
1. Dense gradients computed with standard autograd
2. Embedding gradients distributed back to parameter owners
3. Local optimizer updates applied to each shard

Sources: [torchrec/distributed/model_parallel.py:321-333](), [torchrec/distributed/embeddingbag.py:1000-1100](), [torchrec/distributed/embedding.py:600-700]()

---

