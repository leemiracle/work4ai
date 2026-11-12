<!-- source: DeepWiki mcp.deepwiki.com · repo deepspeedai/DeepSpeed · extra page ZeRO Stages 1 and 2 · fetched 2026-10-21 -->

# ZeRO Stages 1 and 2

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [deepspeed/runtime/activation_checkpointing/checkpointing.py](deepspeed/runtime/activation_checkpointing/checkpointing.py)
- [deepspeed/runtime/base_optimizer.py](deepspeed/runtime/base_optimizer.py)
- [deepspeed/runtime/bf16_optimizer.py](deepspeed/runtime/bf16_optimizer.py)
- [deepspeed/runtime/config.py](deepspeed/runtime/config.py)
- [deepspeed/runtime/constants.py](deepspeed/runtime/constants.py)
- [deepspeed/runtime/engine.py](deepspeed/runtime/engine.py)
- [deepspeed/runtime/utils.py](deepspeed/runtime/utils.py)
- [deepspeed/runtime/zero/config.py](deepspeed/runtime/zero/config.py)
- [deepspeed/runtime/zero/mics.py](deepspeed/runtime/zero/mics.py)
- [deepspeed/runtime/zero/parameter_offload.py](deepspeed/runtime/zero/parameter_offload.py)
- [deepspeed/runtime/zero/partition_parameters.py](deepspeed/runtime/zero/partition_parameters.py)
- [deepspeed/runtime/zero/partitioned_param_coordinator.py](deepspeed/runtime/zero/partitioned_param_coordinator.py)
- [deepspeed/runtime/zero/stage3.py](deepspeed/runtime/zero/stage3.py)
- [deepspeed/runtime/zero/stage_1_and_2.py](deepspeed/runtime/zero/stage_1_and_2.py)
- [deepspeed/runtime/zero/utils.py](deepspeed/runtime/zero/utils.py)
- [docs/_pages/config-json.md](docs/_pages/config-json.md)
- [docs/_posts/2020-09-09-sparse-attention.md](docs/_posts/2020-09-09-sparse-attention.md)
- [docs/_tutorials/megatron.md](docs/_tutorials/megatron.md)
- [docs/_tutorials/one-cycle.md](docs/_tutorials/one-cycle.md)
- [docs/_tutorials/pipeline.md](docs/_tutorials/pipeline.md)
- [docs/_tutorials/pytorch-profiler.md](docs/_tutorials/pytorch-profiler.md)
- [docs/_tutorials/sparse-attention.md](docs/_tutorials/sparse-attention.md)
- [docs/_tutorials/zero-offload.md](docs/_tutorials/zero-offload.md)
- [docs/_tutorials/zero.md](docs/_tutorials/zero.md)
- [requirements/requirements-sparse_attn.txt](requirements/requirements-sparse_attn.txt)

</details>



## Purpose and Scope

This page documents the implementation of ZeRO (Zero Redundancy Optimizer) Stages 1 and 2 in DeepSpeed. These stages reduce memory consumption during training by partitioning optimizer states and gradients across data parallel processes.

**Scope:**
- **ZeRO Stage 1**: Optimizer state partitioning only.
- **ZeRO Stage 2**: Optimizer state and gradient partitioning.

**Related Pages:**
- For ZeRO Stage 3 (parameter partitioning), see [ZeRO Stage 3](3.2.2).
- For parameter offloading and lifecycle management, see [Parameter Lifecycle and Offloading](3.2.3).
- For ZeRO configuration options, see [Configuration System](2.3).

## Overview

ZeRO Stages 1 and 2 are implemented in the `DeepSpeedZeroOptimizer` class, which wraps a base optimizer and manages memory-efficient distributed training through state and gradient partitioning.

### ZeRO Stage Definitions

| Stage | What is Partitioned | Memory Savings | Class Flag |
|-------|-------------------|----------------|------------|
| Stage 0 | Nothing (disabled) | None | N/A |
| Stage 1 | Optimizer states | 4x with Adam | `partition_grads=False` |
| Stage 2 | Optimizer states + Gradients | 8x with Adam | `partition_grads=True` |

**Key Insight:** Each data parallel rank only stores and updates a partition of the optimizer states and (optionally) gradients, rather than maintaining full copies. Parameters remain replicated across all ranks.

Sources: [deepspeed/runtime/zero/stage_1_and_2.py:126-173](), [deepspeed/runtime/zero/config.py:81-87]()

## Architecture and Key Components

### Component Diagram

```mermaid
graph TB
    subgraph "DeepSpeedEngine"
        Engine["DeepSpeedEngine<br/>(runtime/engine.py:255)"]
    end
    
    subgraph "ZeRO Optimizer"
        ZeroOpt["DeepSpeedZeroOptimizer<br/>(zero/stage_1_and_2.py:126)"]
        BaseOpt["self.optimizer<br/>(torch.optim.Adam, etc.)"]
        
        ZeroOpt -->|wraps| BaseOpt
    end
    
    subgraph "Memory Structures"
        BF16Groups["self.bit16_groups<br/>List[List[Parameter]]<br/>Original model params"]
        BF16Flat["self.bit16_groups_flat<br/>List[Tensor]<br/>Flattened params"]
        ParallelPart["self.parallel_partitioned_bit16_groups<br/>List[List[Tensor]]<br/>Partitioned across ranks"]
        FP32Single["self.single_partition_of_fp32_groups<br/>List[Tensor]<br/>FP32 master weights (this rank)"]
        FP32Grads["self.fp32_groups_gradients<br/>List[List[Tensor]]<br/>FP32 gradients buffer"]
    end
    
    subgraph "Communication Methods"
        AllReduce["allreduce_bucket()<br/>Stage 1 gradient sync"]
        ReduceScatter["reduce_scatter_bucket()<br/>Stage 2 gradient sync"]
        AllGather["allgather_and_copy()<br/>Parameter gathering"]
    end
    
    Engine -->|"_configure_zero_optimizer()"| ZeroOpt
    ZeroOpt -->|manages| BF16Groups
    BF16Groups -->|"flatten_dense_tensors_aligned()"| BF16Flat
    BF16Flat -->|"get_data_parallel_partitions()"| ParallelPart
    ParallelPart -->|"clone().float()"| FP32Single
    BaseOpt -->|"step()"| FP32Single
    
    ZeroOpt -->|"partition_grads=False"| AllReduce
    ZeroOpt -->|"partition_grads=True"| ReduceScatter
    ZeroOpt -->|"after step()"| AllGather
    FP32Grads -.->|bucketed| AllReduce
    FP32Grads -.->|bucketed| ReduceScatter
```

Sources: [deepspeed/runtime/zero/stage_1_and_2.py:126-586](), [deepspeed/runtime/engine.py:363-368]()

### Core Class Structure

```mermaid
classDiagram
    class DeepSpeedZeroOptimizer {
        +optimizer: Optimizer
        +partition_gradients: bool
        +bit16_groups: List~List~Parameter~~
        +bit16_groups_flat: List~Tensor~
        +parallel_partitioned_bit16_groups: List~List~Tensor~~
        +single_partition_of_fp32_groups: List~Tensor~
        +fp32_groups_gradients: List~List~Tensor~~
        +fp32_groups_gradients_flat: List~Tensor~
        +reduce_bucket_size: int
        +allgather_bucket_size: int
        +ipg_buckets: Dict~dtype, IPGBucket~
        
        +step() LossScaleOptimizer
        +backward(loss) None
        +allreduce_bucket(bucket_index, rank, dtype) None
        +reduce_scatter_bucket(bucket_index, rank, dtype) None
        +allgather_and_copy(data_parallel_partitions, data_parallel_world_size) None
        +_partition_gradients() None
        +initialize_gradient_partitioning_data_structures() None
        +get_data_parallel_partitions(tensor, i) List~Tensor~
        +flatten_dense_tensors_aligned(tensor_list, alignment) Tensor
        +reduce_ipg_grads_callback(param_group_id, param) Function
    }
    
    class ZeROOptimizer {
        <<abstract>>
        +_global_grad_norm: float
    }
    
    class IPGBucket {
        +buffer: List~Tensor~
        +params: List~Tensor~
        +grads: List~Tensor~
        +elements: int
        +has_moe_params: bool
        +clear() None
    }
    
    ZeROOptimizer <|-- DeepSpeedZeroOptimizer
    DeepSpeedZeroOptimizer --> IPGBucket: "self.ipg_buckets[dtype]"
```

Sources: [deepspeed/runtime/zero/stage_1_and_2.py:126-173](), [deepspeed/runtime/zero/stage_1_and_2.py:111-124](), [deepspeed/runtime/base_optimizer.py:18-30]()

## Stage 1: Optimizer State Partitioning

### Memory Layout

In ZeRO Stage 1, model parameters and gradients are replicated across all data parallel ranks, but optimizer states are partitioned.

```mermaid
graph LR
    subgraph "Rank 0"
        R0P["Parameters (FP16)<br/>Full Copy"]
        R0G["Gradients (FP32)<br/>Full Copy"]
        R0O["Optimizer States<br/>Partition 0/N"]
        R0M["Master Weights (FP32)<br/>Partition 0/N"]
    end
    
    subgraph "Rank 1"
        R1P["Parameters (FP16)<br/>Full Copy"]
        R1G["Gradients (FP32)<br/>Full Copy"]
        R1O["Optimizer States<br/>Partition 1/N"]
        R1M["Master Weights (FP32)<br/>Partition 1/N"]
    end
    
    subgraph "Rank N-1"
        RNP["Parameters (FP16)<br/>Full Copy"]
        RNG["Gradients (FP32)<br/>Full Copy"]
        RNO["Optimizer States<br/>Partition N-1/N"]
        RNM["Master Weights (FP32)<br/>Partition N-1/N"]
    end
```

**Key Characteristics:**
- **Replicated**: Model parameters (`bit16_groups`), gradients (`fp32_groups_gradients`).
- **Partitioned**: Optimizer states, FP32 master weights (`single_partition_of_fp32_groups`).
- **Communication**: `allreduce` for gradients, `allgather` for updated parameters.

Sources: [deepspeed/runtime/zero/stage_1_and_2.py:354-483]()

### Training Step Flow (Stage 1)

```mermaid
sequenceDiagram
    participant User
    participant Engine as DeepSpeedEngine
    participant ZeroOpt as DeepSpeedZeroOptimizer
    participant AllReduce as AllReduce Collective
    participant AllGather as AllGather Collective
    participant BaseOpt as Base Optimizer
    
    User->>Engine: loss.backward()
    Engine->>ZeroOpt: backward(loss)
    
    Note over ZeroOpt: Gradients accumulated in<br/>fp32_groups_gradients
    
    ZeroOpt->>ZeroOpt: _create_reduce_and_remove_grad_hooks()
    Note over ZeroOpt: Hooks trigger gradient reduction
    
    ZeroOpt->>AllReduce: allreduce_bucket(gradients)
    Note over AllReduce: Synchronize gradients<br/>across all ranks
    AllReduce-->>ZeroOpt: Averaged gradients
    
    User->>Engine: engine.step()
    Engine->>ZeroOpt: step()
    
    ZeroOpt->>ZeroOpt: Check overflow
    ZeroOpt->>BaseOpt: step() on partition
    Note over BaseOpt: Updates only this rank's<br/>partition of master weights
    
    ZeroOpt->>AllGather: allgather_and_copy(updated_partitions)
    Note over AllGather: Gather all partitions to<br/>reconstruct full parameters
    AllGather-->>ZeroOpt: Full FP32 weights
    
    ZeroOpt->>ZeroOpt: Copy FP32 to FP16 params
    ZeroOpt-->>User: Training step complete
```

Sources: [deepspeed/runtime/zero/stage_1_and_2.py:773-900](), [deepspeed/runtime/zero/stage_1_and_2.py:1078-1228]()

### Implementation Details

The optimizer partitions parameters during initialization:

1. **Parameter Flattening**: Parameters are flattened into a single contiguous buffer per parameter group [deepspeed/runtime/zero/stage_1_and_2.py:404-417]().
2. **Partitioning**: The flat buffer is divided into equal-sized partitions (one per rank) [deepspeed/runtime/zero/stage_1_and_2.py:427-428]().
3. **FP32 Partition Creation**: Each rank creates an FP32 copy of its partition for optimizer updates [deepspeed/runtime/zero/stage_1_and_2.py:449-450]().

Sources: [deepspeed/runtime/zero/stage_1_and_2.py:354-483]()

## Stage 2: Optimizer State + Gradient Partitioning

### Memory Layout

In ZeRO Stage 2, both optimizer states and gradients are partitioned.

```mermaid
graph LR
    subgraph "Rank 0"
        R0P["Parameters (FP16)<br/>Full Copy"]
        R0G["Gradients (FP32)<br/>Partition 0/N"]
        R0O["Optimizer States<br/>Partition 0/N"]
        R0M["Master Weights (FP32)<br/>Partition 0/N"]
    end
    
    subgraph "Rank 1"
        R1P["Parameters (FP16)<br/>Full Copy"]
        R1G["Gradients (FP32)<br/>Partition 1/N"]
        R1O["Optimizer States<br/>Partition 1/N"]
        R1M["Master Weights (FP32)<br/>Partition 1/N"]
    end
    
    subgraph "Rank N-1"
        RNP["Parameters (FP16)<br/>Full Copy"]
        RNG["Gradients (FP32)<br/>Partition N-1/N"]
        RNO["Optimizer States<br/>Partition N-1/N"]
        RNM["Master Weights (FP32)<br/>Partition N-1/N"]
    end
```

**Key Difference from Stage 1:**
- Gradients are now partitioned rather than replicated.
- Uses `reduce_scatter` instead of `allreduce` for gradient synchronization.
- Each rank only needs to store gradients for its assigned partition.

Sources: [deepspeed/runtime/zero/stage_1_and_2.py:212-214]()

### Gradient Partitioning Logic

ZeRO Stage 2 introduces gradient partitioning logic to determine which gradients belong to which rank. This is implemented through several data structures initialized in `initialize_gradient_partitioning_data_structures()` [deepspeed/runtime/zero/stage_1_and_2.py:912-1076]().

**Partition Mapping Data Structures:**

```mermaid
graph TB
    subgraph "Initialization (initialize_gradient_partitioning_data_structures)"
        GetPartInfo["get_partition_info(params, partition_size, partition_id)"]
        
        ParamsIn["self.params_in_partition[i]<br/>Parameters owned by this rank"]
        ParamsNotIn["self.params_not_in_partition[i]<br/>Parameters owned by other ranks"]
        FirstOff["self.first_offset[i]<br/>Offset of first param in partition"]
        
        GetPartInfo --> ParamsIn
        GetPartInfo --> ParamsNotIn
        GetPartInfo --> FirstOff
    end
    
    subgraph "Per-Parameter Tracking"
        ParamToPartition["self.param_to_partition_ids[param_id]<br/>Which partition(s) param belongs to"]
        GradInsertOffset["self.grad_partition_insertion_offset[param_id]<br/>Where to insert grad in partition"]
        GradStartOffset["self.grad_start_offset[param_id]<br/>Offset in gradient for insertion"]
        IsGradComputed["self.is_grad_computed[partition_id][param_id]<br/>Has this gradient been computed?"]
        
        AvgGrads["self.averaged_gradients[param_id]<br/>Stores reduced gradient partition"]
    end
    
    ParamsIn -.->|"for each param"| ParamToPartition
```

**Key Mapping Structures:**

| Structure | Type | Purpose |
|-----------|------|---------|
| `params_in_partition[i]` | List[Parameter] | Parameters whose gradients this rank updates. |
| `param_to_partition_ids` | List[int] | Partition IDs containing this parameter. |
| `grad_partition_insertion_offset` | Dict[partition_id, int] | Where to insert gradient in partition buffer. |
| `averaged_gradients` | Tensor | Stores partition of averaged gradient. |

Sources: [deepspeed/runtime/zero/stage_1_and_2.py:912-1076](), [deepspeed/runtime/zero/stage_1_and_2.py:1230-1580]()

## Communication Patterns

### Bucketing Strategy

Both stages use bucketing to batch small communication operations into larger, more efficient ones through the `IPGBucket` (Independent Parameter Gradients Bucket) mechanism.

```mermaid
graph TB
    subgraph "Gradient Flow and Bucketing"
        GradHook["reduce_ipg_grads_callback()"]
        CheckSize["bucket.elements + grad.numel()<br/><= reduce_bucket_size?"]
        AddToBucket["Add to bucket:<br/>bucket.grads.append(grad)<br/>bucket.params.append(param)<br/>bucket.elements += numel"]
        
        FlushStage1["Stage 1:<br/>allreduce_bucket()"]
        FlushStage2["Stage 2:<br/>reduce_scatter_bucket()"]
        
        Flatten["_flatten_dense_tensors(bucket.grads)"]
        ClearBucket["bucket.clear()"]
        
        GradHook --> CheckSize
        CheckSize -->|No, bucket full| FlushStage1
        CheckSize -->|No, bucket full| FlushStage2
        CheckSize -->|Yes| AddToBucket
        
        FlushStage1 --> Flatten
        FlushStage2 --> Flatten
        Flatten --> ClearBucket
    end
    
    subgraph "IPGBucket Structure (stage_1_and_2.py:111-124)"
        IPG["@dataclass IPGBucket"]
        IPG_params["params: List[Tensor]"]
        IPG_grads["grads: List[Tensor]"]
        IPG_elements["elements: int"]
        
        IPG --> IPG_params
        IPG --> IPG_grads
        IPG --> IPG_elements
    end
```

**Implementation Flow:**
1. Backward pass computes gradient → triggers `reduce_ipg_grads_callback(i, param)` [deepspeed/runtime/zero/stage_1_and_2.py:681-770]().
2. Gradient added to appropriate dtype bucket: `self.ipg_buckets[grad.dtype]`.
3. When bucket reaches `reduce_bucket_size`, flush via `allreduce_bucket()` or `reduce_scatter_bucket()`.
4. Gradients are flattened using `_flatten_dense_tensors()` before communication.
5. Bucket is cleared with `bucket.clear()` after successful communication.

Sources: [deepspeed/runtime/zero/stage_1_and_2.py:111-124](), [deepspeed/runtime/zero/stage_1_and_2.py:681-770]()

### Communication Collectives

#### Stage 1: AllReduce Pattern
**Method: `allreduce_bucket(bucket_index, rank, dtype)`** [deepspeed/runtime/zero/stage_1_and_2.py:1394-1470]()
- Each rank has full gradients in its local bucket.
- Result scaled by `1/world_size` to compute average.
- For MoE models, uses appropriate expert data parallel group.

#### Stage 2: ReduceScatter Pattern
**Method: `reduce_scatter_bucket(bucket_index, rank, dtype)`** [deepspeed/runtime/zero/stage_1_and_2.py:1582-1732]()
- Maps gradients to correct partition owners using `self.grad_partition_insertion_offset`.
- Calls `reduce_scatter_coalesced()` to average and partition gradients.
- Each rank receives and stores only its partition in `self.averaged_gradients[param_id]`.

Sources: [deepspeed/runtime/zero/stage_1_and_2.py:1394-1470](), [deepspeed/runtime/zero/stage_1_and_2.py:1582-1732]()

## Lifecycle and Training Loop

### Gradient Reduction Hooks

Gradient reduction is triggered automatically via hooks registered on parameters during optimizer initialization [deepspeed/runtime/zero/stage_1_and_2.py:587-680]().

**Hook Registration Flow:**
1. **Hook Creation**: `reduce_ipg_grads_callback(i, param)` returns a closure that extracts the gradient and adds it to the appropriate `IPGBucket`.
2. **Registration**: Uses `register_grad_hook(param, hook)` [deepspeed/utils/torch.py:20-21]() to attach the reduction logic to the PyTorch autograd engine.
3. **Async Execution**: If `overlap_comm=True`, the reduction is issued asynchronously on `self.reduction_stream` [deepspeed/runtime/zero/stage_1_and_2.py:488]().

Sources: [deepspeed/runtime/zero/stage_1_and_2.py:587-680](), [deepspeed/runtime/zero/stage_1_and_2.py:681-770]()

### CPU Offloading

ZeRO Stages 1 and 2 support offloading optimizer states to CPU memory to free up GPU memory.

- **Configuration**: Set `offload_optimizer` with `device: "cpu"` in the config [deepspeed/runtime/zero/config.py:164-170]().
- **Optimizer Selection**: Typically uses `DeepSpeedCPUAdam` for efficient CPU-side updates [deepspeed/runtime/zero/stage_1_and_2.py:28]().
- **Data Flow**: Gradients are accumulated on CPU, optimizer updates CPU-side master weights, and updated partitions are gathered back to GPU.

Sources: [deepspeed/runtime/zero/stage_1_and_2.py:176-181](), [deepspeed/runtime/zero/config.py:164-170]()

## Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `stage` | int | 0 | ZeRO stage: 1 (optimizer), 2 (optimizer+gradients) [deepspeed/runtime/zero/config.py:95](). |
| `reduce_bucket_size` | int | 500M | Max elements per gradient reduction bucket [deepspeed/runtime/zero/config.py:113](). |
| `allgather_bucket_size` | int | 5B | Max elements per parameter gathering bucket [deepspeed/runtime/zero/config.py:132](). |
| `overlap_comm` | bool | True | Overlap communication with computation [deepspeed/runtime/zero/config.py:138](). |
| `contiguous_gradients` | bool | True | Copy gradients to contiguous buffer to avoid fragmentation [deepspeed/runtime/zero/config.py:102](). |
| `round_robin_gradients` | bool | False | Reorder parameters to balance communication load [deepspeed/runtime/zero/stage_1_and_2.py:387-401](). |

Sources: [deepspeed/runtime/zero/config.py:90-260](), [docs/_pages/config-json.md:1-300]()

---

