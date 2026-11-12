<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/picotron_tutorial · extra page Naive Data Parallelism · fetched 2026-10-26 -->

# Naive Data Parallelism

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [step5_data_parallel_naive/data_parallel.py](step5_data_parallel_naive/data_parallel.py)
- [step5_data_parallel_naive/patch_step_5.diff](step5_data_parallel_naive/patch_step_5.diff)

</details>



This document covers the naive data parallelism implementation in the Picotron tutorial, which provides the simplest approach to synchronizing gradients across multiple processes in distributed training. This implementation uses straightforward all-reduce operations to average gradients after backward passes.

The naive approach forms the foundation for understanding data parallelism concepts before moving to more optimized implementations. For the advanced bucketed approach that improves communication efficiency, see [Bucketed Data Parallelism](#4.2.2). For tensor parallelism strategies, see [Tensor Parallelism](#4.1).

## System Architecture

The naive data parallelism implementation operates as a wrapper around the base model, intercepting gradient computations to perform synchronization across data parallel process groups.

### High-Level Integration

```mermaid
graph TB
    subgraph "Training Process Flow"
        MODEL["Base LLaMA Model"]
        TP_WRAP["apply_tensor_parallel"]
        DP_WRAP["DataParallelNaive"]
        DEVICE["model.to(device)"]
    end
    
    subgraph "Data Pipeline"
        DATASET["Dataset"]
        SAMPLER["DistributedSampler"]
        DATALOADER["MicroBatchDataLoader"]
    end
    
    subgraph "Process Groups"
        PGM["ProcessGroupManager"]
        DP_GROUP["dp_group"]
        TP_GROUP["tp_group"]
    end
    
    subgraph "Training Loop"
        FORWARD["Forward Pass"]
        BACKWARD["Backward Pass"]
        SYNC["Gradient All-Reduce"]
        OPTIMIZER["Optimizer Step"]
    end
    
    MODEL --> TP_WRAP
    TP_WRAP --> DEVICE
    DEVICE --> DP_WRAP
    
    PGM --> DP_GROUP
    PGM --> TP_GROUP
    
    DATASET --> SAMPLER
    SAMPLER --> DATALOADER
    
    DP_WRAP --> FORWARD
    FORWARD --> BACKWARD
    BACKWARD --> SYNC
    SYNC --> OPTIMIZER
    
    DP_GROUP -.->|"coordinates"| SAMPLER
    DP_GROUP -.->|"synchronizes"| SYNC
```

Sources: [step5_data_parallel_naive/patch_step_5.diff:88-132](), [step5_data_parallel_naive/data_parallel.py:9-34]()

## DataParallelNaive Implementation

The core implementation wraps the base model and manages gradient synchronization through PyTorch's backward hook mechanism.

### Class Structure

```mermaid
graph LR
    subgraph "DataParallelNaive Class"
        INIT["__init__"]
        FORWARD["forward"]
        HOOK_REG["register_backward_hook"]
        ALLREDUCE["_allreduce_grads"]
    end
    
    subgraph "State Management"
        MODULE["self.module"]
        SYNC_FLAG["require_backward_grad_sync"]
    end
    
    subgraph "PyTorch Integration"
        PARAM["parameter.register_hook"]
        DIST_ALL_REDUCE["dist.all_reduce"]
        DP_GROUP["pgm.dp_group"]
    end
    
    INIT --> MODULE
    INIT --> SYNC_FLAG
    INIT --> HOOK_REG
    
    HOOK_REG --> PARAM
    PARAM --> ALLREDUCE
    
    ALLREDUCE --> DIST_ALL_REDUCE
    DIST_ALL_REDUCE --> DP_GROUP
    
    FORWARD --> MODULE
```

Sources: [step5_data_parallel_naive/data_parallel.py:10-34]()

### Key Components

| Component | Purpose | Implementation |
|-----------|---------|----------------|
| `module` | Wrapped base model | Stores reference to original model |
| `require_backward_grad_sync` | Controls synchronization timing | Boolean flag for gradient accumulation |
| `register_backward_hook` | Hook registration | Attaches `_allreduce_grads` to all parameters |
| `_allreduce_grads` | Gradient synchronization | Performs all-reduce and averaging |

## Gradient Synchronization Mechanism

The naive approach uses PyTorch's parameter hooks to intercept gradients during backward passes and synchronize them across the data parallel group.

### Synchronization Flow

```mermaid
graph TD
    subgraph "Backward Pass Flow"
        LOSS["Loss Computation"]
        BACKWARD["loss.backward()"]
        PARAM_GRADS["Parameter Gradients"]
    end
    
    subgraph "Hook Execution"
        HOOK_TRIGGER["Hook Triggered"]
        CHECK_SYNC["Check require_backward_grad_sync"]
        ALLREDUCE_CALL["dist.all_reduce()"]
        AVERAGE["grad /= dp_world_size"]
    end
    
    subgraph "Distributed Communication"
        DP_RANKS["DP Rank 0, 1, 2, 3"]
        SUM_OP["ReduceOp.SUM"]
        RESULT["Averaged Gradients"]
    end
    
    LOSS --> BACKWARD
    BACKWARD --> PARAM_GRADS
    PARAM_GRADS --> HOOK_TRIGGER
    
    HOOK_TRIGGER --> CHECK_SYNC
    CHECK_SYNC -->|"True"| ALLREDUCE_CALL
    CHECK_SYNC -->|"False"| PARAM_GRADS
    
    ALLREDUCE_CALL --> DP_RANKS
    DP_RANKS --> SUM_OP
    SUM_OP --> AVERAGE
    AVERAGE --> RESULT
```

Sources: [step5_data_parallel_naive/data_parallel.py:27-33]()

### Gradient Accumulation Integration

The implementation coordinates with gradient accumulation by only synchronizing gradients on the final accumulation step:

```mermaid
graph LR
    subgraph "Micro-batch Loop"
        MB1["Micro-batch 1"]
        MB2["Micro-batch 2"] 
        MB3["Micro-batch N"]
    end
    
    subgraph "Sync Control"
        SYNC_OFF["require_backward_grad_sync = False"]
        SYNC_ON["require_backward_grad_sync = True"]
    end
    
    subgraph "Operations"
        LOCAL_GRAD["Local Gradient Accumulation"]
        ALLREDUCE["All-Reduce Synchronization"]
        OPT_STEP["Optimizer Step"]
    end
    
    MB1 --> SYNC_OFF
    MB2 --> SYNC_OFF
    MB3 --> SYNC_ON
    
    SYNC_OFF --> LOCAL_GRAD
    SYNC_ON --> ALLREDUCE
    ALLREDUCE --> OPT_STEP
```

Sources: [step5_data_parallel_naive/patch_step_5.diff:108-118]()

## Training Integration

The naive data parallelism is integrated into the training pipeline with specific coordination between the model wrapper, data loading, and gradient accumulation.

### Model Initialization Sequence

The model undergoes a specific initialization sequence to ensure proper device placement and wrapper ordering:

| Step | Operation | Code Location |
|------|-----------|---------------|
| 1 | Create base model | [step5_data_parallel_naive/patch_step_5.diff:123]() |
| 2 | Apply tensor parallelism | [step5_data_parallel_naive/patch_step_5.diff:124]() |
| 3 | Move to device | [step5_data_parallel_naive/patch_step_5.diff:128]() |
| 4 | Wrap with DataParallelNaive | [step5_data_parallel_naive/patch_step_5.diff:130-131]() |

### Data Loading Coordination

The data loading pipeline integrates with data parallelism through `DistributedSampler`:

```mermaid
graph LR
    subgraph "Data Distribution"
        DATASET["Full Dataset"]
        SAMPLER["DistributedSampler"]
        DP_SHARD_0["DP Rank 0 Data"]
        DP_SHARD_1["DP Rank 1 Data"]
        DP_SHARD_N["DP Rank N Data"]
    end
    
    subgraph "Sampler Configuration"
        NUM_REPLICAS["num_replicas = dp_world_size"]
        RANK["rank = dp_rank"]
        SEED["seed = args.seed"]
    end
    
    DATASET --> SAMPLER
    NUM_REPLICAS --> SAMPLER
    RANK --> SAMPLER  
    SEED --> SAMPLER
    
    SAMPLER --> DP_SHARD_0
    SAMPLER --> DP_SHARD_1
    SAMPLER --> DP_SHARD_N
```

Sources: [step5_data_parallel_naive/patch_step_5.diff:70-85]()

### Training Step Coordination

Each training step coordinates gradient synchronization with gradient accumulation:

```mermaid
graph TD
    subgraph "Training Step Loop"
        START["Start Training Step"]
        CHECK_DP["dp_world_size > 1?"]
        MICRO_LOOP["For each micro-batch"]
        SET_SYNC["Set require_backward_grad_sync"]
        FORWARD["Forward Pass"]
        BACKWARD["Backward Pass"]
        CHECK_LAST["Last micro-batch?"]
        OPTIMIZER["Optimizer Step"]
    end
    
    START --> CHECK_DP
    CHECK_DP -->|"Yes"| MICRO_LOOP
    CHECK_DP -->|"No"| MICRO_LOOP
    
    MICRO_LOOP --> SET_SYNC
    SET_SYNC --> FORWARD
    FORWARD --> BACKWARD
    BACKWARD --> CHECK_LAST
    
    CHECK_LAST -->|"No"| MICRO_LOOP
    CHECK_LAST -->|"Yes"| OPTIMIZER
```

Sources: [step5_data_parallel_naive/patch_step_5.diff:104-118]()

## Communication Patterns

The naive implementation uses simple all-reduce operations without optimization, resulting in straightforward but potentially inefficient communication patterns.

### All-Reduce Operation Details

| Aspect | Implementation | Code Reference |
|--------|----------------|----------------|
| Operation | `dist.all_reduce()` | [step5_data_parallel_naive/data_parallel.py:31]() |
| Reduce Operation | `ReduceOp.SUM` | [step5_data_parallel_naive/data_parallel.py:31]() |
| Process Group | `pgm.process_group_manager.dp_group` | [step5_data_parallel_naive/data_parallel.py:31]() |
| Averaging | `grad /= dp_world_size` | [step5_data_parallel_naive/data_parallel.py:32]() |

### Performance Characteristics

The naive approach has the following performance characteristics:

- **Simplicity**: Straightforward implementation with minimal complexity
- **Synchronous**: All processes must wait for gradient synchronization to complete
- **Per-parameter**: Each parameter gradient triggers a separate all-reduce operation
- **Memory Overhead**: Minimal additional memory usage beyond the base model

Sources: [step5_data_parallel_naive/data_parallel.py:27-33]()

---

