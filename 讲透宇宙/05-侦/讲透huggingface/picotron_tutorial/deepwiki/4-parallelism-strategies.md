<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/picotron_tutorial · page 4 Parallelism Strategies · fetched 2026-10-26 -->

# Parallelism Strategies

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.demo/step4_tensor_parallel.json](.demo/step4_tensor_parallel.json)
- [.demo/step5_data_parallel_naive.json](.demo/step5_data_parallel_naive.json)
- [.demo/step6_data_parallel_bucket.json](.demo/step6_data_parallel_bucket.json)
- [step6_data_parallel_bucket/data_parallel.py](step6_data_parallel_bucket/data_parallel.py)

</details>



This document covers the three fundamental parallelism strategies implemented in the Picotron tutorial system for distributed deep learning: Tensor Parallelism, Data Parallelism, and Pipeline Parallelism. These strategies enable training large language models by distributing computation and memory across multiple GPUs and processes.

For details on the process group coordination that enables these strategies, see [Process Group Management](#3.3). For information about how these strategies integrate in complete training scripts, see [Training Integration](#5).

## Overview of Parallelism Dimensions

The tutorial implements a 3D parallelism approach where each dimension addresses different scaling challenges:

```mermaid
graph TB
    subgraph "3D Parallelism Architecture"
        subgraph "Tensor Parallel"
            TP1["ColumnParallelLinear<br/>Split output features"]
            TP2["RowParallelLinear<br/>Split input features"] 
            TP3["VocabParallelEmbedding<br/>Split vocabulary"]
        end
        
        subgraph "Data Parallel"
            DP1["DataParallelNaive<br/>Simple all-reduce"]
            DP2["DataParallelBucket<br/>Gradient bucketing"]
        end
        
        subgraph "Pipeline Parallel"
            PP1["AFAB Engine<br/>Forward-then-backward"]
            PP2["1F1B Engine<br/>Overlapped execution"]
        end
    end
    
    subgraph "Communication Patterns"
        COMM1["All-Reduce<br/>TP + DP gradients"]
        COMM2["Point-to-Point<br/>PP activations"]
        COMM3["Broadcast<br/>Parameter sync"]
    end
    
    TP1 --> COMM1
    TP2 --> COMM1
    DP1 --> COMM1
    DP2 --> COMM1
    PP1 --> COMM2
    PP2 --> COMM2
    
    style TP1 fill:#f9f9f9
    style DP1 fill:#f9f9f9
    style PP1 fill:#f9f9f9
```

**Sources:** [step4_tensor_parallel/tensor_parallel.py](), [step6_data_parallel_bucket/data_parallel.py](), [.demo/step4_tensor_parallel.json](), [.demo/step5_data_parallel_naive.json](), [.demo/step6_data_parallel_bucket.json]()

## Tensor Parallelism Implementation

Tensor Parallelism distributes model weights across multiple GPUs within each transformer layer. The implementation uses three core classes that handle different aspects of weight sharding.

### Core Tensor Parallel Classes

```mermaid
graph LR
    subgraph "Linear Layer Sharding"
        COL["ColumnParallelLinear<br/>output_size // tp_size"]
        ROW["RowParallelLinear<br/>input_size // tp_size"]
    end
    
    subgraph "Embedding Sharding"
        VOCAB["VocabParallelEmbedding<br/>vocab_size // tp_size"]
    end
    
    subgraph "Communication Functions"
        ALL_REDUCE["all_reduce_fn<br/>Sum across TP group"]
        ALL_GATHER["all_gather_fn<br/>Gather from TP group"]
    end
    
    COL --> ALL_GATHER
    ROW --> ALL_REDUCE
    VOCAB --> ALL_REDUCE
    
    subgraph "Model Application"
        APPLY["apply_tensor_parallel<br/>Replace Linear layers"]
    end
    
    APPLY --> COL
    APPLY --> ROW
    APPLY --> VOCAB
```

**Sources:** [step4_tensor_parallel/tensor_parallel.py:68-111](), [step4_tensor_parallel/tensor_parallel.py:128-165](), [step4_tensor_parallel/tensor_parallel.py:175-216]()

### Weight Initialization and Communication

The tensor parallel implementation handles weight initialization carefully to ensure consistent model behavior across different tensor parallel configurations:

| Class | Weight Initialization | Forward Communication | Backward Communication |
|-------|----------------------|----------------------|----------------------|
| `ColumnParallelLinear` | Local partition only | No communication | `all_gather_fn` |
| `RowParallelLinear` | Full weight, then slice | `all_reduce_fn` | No communication |
| `VocabParallelEmbedding` | Local vocabulary partition | `all_reduce_fn` | No communication |

**Sources:** [step4_tensor_parallel/tensor_parallel.py:139-157](), [step4_tensor_parallel/tensor_parallel.py:191-209](), [step4_tensor_parallel/tensor_parallel.py:242-245]()

### Tensor Parallel Application Process

The `apply_tensor_parallel` function transforms a standard model into a tensor-parallel version by replacing specific layer types:

```mermaid
flowchart TD
    MODEL["Base LLaMA Model"] --> SCAN["Scan model modules"]
    SCAN --> CHECK_EMBED["Check for Embedding layers"]
    SCAN --> CHECK_LINEAR["Check for Linear layers"]
    
    CHECK_EMBED --> VOCAB_REPLACE["Replace with VocabParallelEmbedding"]
    CHECK_LINEAR --> LAYER_TYPE["Determine layer type"]
    
    LAYER_TYPE --> Q_PROJ["q_proj → ColumnParallelLinear"]
    LAYER_TYPE --> K_PROJ["k_proj → ColumnParallelLinear"] 
    LAYER_TYPE --> V_PROJ["v_proj → ColumnParallelLinear"]
    LAYER_TYPE --> GATE_PROJ["gate_proj → ColumnParallelLinear"]
    LAYER_TYPE --> UP_PROJ["up_proj → ColumnParallelLinear"]
    
    LAYER_TYPE --> O_PROJ["o_proj → RowParallelLinear"]
    LAYER_TYPE --> DOWN_PROJ["down_proj → RowParallelLinear"]
    
    Q_PROJ --> FINAL["Tensor Parallel Model"]
    K_PROJ --> FINAL
    V_PROJ --> FINAL
    GATE_PROJ --> FINAL
    UP_PROJ --> FINAL
    O_PROJ --> FINAL
    DOWN_PROJ --> FINAL
    VOCAB_REPLACE --> FINAL
```

**Sources:** [step4_tensor_parallel/tensor_parallel.py:68-111]()

## Data Parallelism Strategies

Data Parallelism replicates the model across multiple processes and synchronizes gradients after backward passes. The tutorial implements two approaches with different optimization strategies.

### Naive Data Parallelism

The `DataParallelNaive` class provides a straightforward implementation using parameter hooks:

```mermaid
graph TB
    MODULE["Wrapped Module"] --> FORWARD["Forward Pass"]
    FORWARD --> BACKWARD["Backward Pass"]
    BACKWARD --> HOOK["Parameter Hook Triggered"]
    HOOK --> SYNC_CHECK["Check require_backward_grad_sync"]
    SYNC_CHECK --> ALL_REDUCE["dist.all_reduce on gradient"]
    ALL_REDUCE --> SCALE["gradient /= dp_world_size"]
    SCALE --> OPTIMIZER["Optimizer Step"]
    
    subgraph "Hook Registration"
        REG_HOOK["register_backward_hook<br/>for each parameter"]
        ALLREDUCE_GRADS["_allreduce_grads<br/>hook function"]
    end
    
    REG_HOOK --> ALLREDUCE_GRADS
    ALLREDUCE_GRADS --> HOOK
```

**Sources:** [step6_data_parallel_bucket/data_parallel.py:10-36]()

### Bucketed Data Parallelism

The `DataParallelBucket` class optimizes gradient synchronization using gradient bucketing and asynchronous communication:

```mermaid
graph TB
    subgraph "Bucket Management System"
        MGR["BucketManager<br/>Organizes parameters"]
        BUCKET1["Bucket 1<br/>params + grad_data"]
        BUCKET2["Bucket 2<br/>params + grad_data"]
        BUCKETN["Bucket N<br/>params + grad_data"]
        
        MGR --> BUCKET1
        MGR --> BUCKET2
        MGR --> BUCKETN
    end
    
    subgraph "Gradient Flow"
        PARAM["Parameter.grad"] --> MAIN_GRAD["Parameter.main_grad<br/>Accumulate"]
        MAIN_GRAD --> MARK_READY["mark_param_as_ready"]
        MARK_READY --> CHECK_BUCKET["All params ready?"]
        CHECK_BUCKET -->|Yes| ASYNC_REDUCE["async all_reduce"]
        CHECK_BUCKET -->|No| WAIT["Wait for more params"]
        WAIT --> MARK_READY
    end
    
    subgraph "Post-Backward Callback"
        CALLBACK["_post_backward<br/>queue_callback"]
        WAIT_ALL["bucket_manager.wait()"]
        COPY_BACK["Copy to param.grad"]
        
        CALLBACK --> WAIT_ALL
        WAIT_ALL --> COPY_BACK
    end
    
    ASYNC_REDUCE --> CALLBACK
```

**Sources:** [step6_data_parallel_bucket/data_parallel.py:83-163](), [step6_data_parallel_bucket/data_parallel.py:165-258]()

### Gradient Bucketing Strategy

The bucketing system optimizes communication by grouping parameters and overlapping computation with communication:

| Component | Responsibility | Key Methods |
|-----------|---------------|-------------|
| `BucketManager` | Parameter organization, bucket allocation | `_initialize_buckets`, `mark_param_as_ready` |
| `Bucket` | Gradient storage, async communication | `sync_gradient`, `wait`, `mark_param_as_ready` |
| `DataParallelBucket` | Hook registration, gradient accumulation | `register_backward_hook`, `_make_param_hook` |

**Sources:** [step6_data_parallel_bucket/data_parallel.py:39-82](), [step6_data_parallel_bucket/data_parallel.py:102-148]()

## Pipeline Parallelism Engines

Pipeline Parallelism splits the model across multiple stages, with each stage executing on different processes. The tutorial implements two execution engines with different scheduling strategies.

### Pipeline Execution Patterns

```mermaid
sequenceDiagram
    participant S0 as "Stage 0"
    participant S1 as "Stage 1" 
    participant S2 as "Stage 2"
    
    Note over S0,S2: AFAB Pattern (All Forward, All Backward)
    S0->>S1: Forward batch 1
    S1->>S2: Forward batch 1
    S0->>S1: Forward batch 2
    S1->>S2: Forward batch 2
    S2->>S1: Backward batch 1
    S1->>S0: Backward batch 1
    S2->>S1: Backward batch 2
    S1->>S0: Backward batch 2
    
    Note over S0,S2: 1F1B Pattern (Overlapped)
    S0->>S1: Forward batch 1
    S1->>S2: Forward batch 1
    S0->>S1: Forward batch 2
    S2->>S1: Backward batch 1
    S1->>S2: Forward batch 2
    S1->>S0: Backward batch 1
```

**Sources:** [.demo/step4_tensor_parallel.json](), [.demo/step5_data_parallel_naive.json]()

## Integration and Communication Coordination

The parallelism strategies integrate through the `ProcessGroupManager` which coordinates different communication groups:

```mermaid
graph TB
    subgraph "Process Group Coordination"
        PGM["ProcessGroupManager"] --> TP_GROUP["tp_group<br/>Tensor parallel ranks"]
        PGM --> DP_GROUP["dp_group<br/>Data parallel ranks"]
        PGM --> PP_GROUP["pp_group<br/>Pipeline parallel ranks"]
    end
    
    subgraph "Strategy Integration"
        TP_WRAP["apply_tensor_parallel<br/>Uses tp_group"]
        DP_WRAP["DataParallelBucket<br/>Uses dp_group"]
        PP_WRAP["PipelineParallel<br/>Uses pp_group"]
    end
    
    TP_GROUP --> TP_WRAP
    DP_GROUP --> DP_WRAP
    PP_GROUP --> PP_WRAP
    
    subgraph "Model Transformation Pipeline"
        BASE_MODEL["Base LLaMA Model"]
        BASE_MODEL --> TP_WRAP
        TP_WRAP --> PP_WRAP
        PP_WRAP --> DP_WRAP
        DP_WRAP --> FINAL_MODEL["3D Parallel Model"]
    end
```

**Sources:** [step6_data_parallel_bucket/data_parallel.py:175](), [step4_tensor_parallel/tensor_parallel.py:68-111]()

The three parallelism dimensions work together to enable training of large models by:
- **Tensor Parallelism**: Reducing memory per GPU by splitting weights
- **Data Parallelism**: Increasing throughput by processing multiple batches
- **Pipeline Parallelism**: Enabling models larger than single GPU memory by splitting layers

Each strategy addresses different scaling bottlenecks and can be combined to achieve optimal performance for specific model sizes and hardware configurations.

---

