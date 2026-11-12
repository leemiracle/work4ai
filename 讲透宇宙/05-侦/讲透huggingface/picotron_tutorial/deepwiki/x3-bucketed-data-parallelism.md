<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/picotron_tutorial · extra page Bucketed Data Parallelism · fetched 2026-10-26 -->

# Bucketed Data Parallelism

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [step6_data_parallel_bucket/patch_step_6.diff](step6_data_parallel_bucket/patch_step_6.diff)
- [step6_data_parallel_bucket/train.py](step6_data_parallel_bucket/train.py)

</details>



This document covers the bucketed data parallelism implementation in the Picotron tutorial, which provides an optimized approach to gradient synchronization across data-parallel processes. This implementation groups model parameters into buckets to enable overlapped computation and communication, improving training efficiency compared to the naive all-reduce approach.

For information about the simpler naive data parallelism approach, see [Naive Data Parallelism](#4.2.1). For details on tensor parallelism strategies, see [Tensor Parallelism](#4.1).

## Overview and Benefits

Bucketed data parallelism addresses the communication bottleneck in naive data parallelism by grouping model parameters into buckets and performing asynchronous gradient synchronization. Instead of waiting for all gradients to be computed before starting communication, this approach begins synchronizing gradients as soon as complete buckets are ready.

The key benefits include:
- **Overlapped Communication**: Gradient synchronization begins before all gradients are computed
- **Reduced Memory Pressure**: Gradients are organized into fixed-size buckets
- **Improved Throughput**: Less idle time waiting for synchronization
- **Asynchronous Operations**: Non-blocking all-reduce operations

## System Architecture

The bucketed data parallelism system consists of three main components that work together to manage gradient synchronization:

```mermaid
graph TB
    subgraph "DataParallelBucket Wrapper"
        DPB[DataParallelBucket]
        HOOKS[Backward Hooks]
        CALLBACK[Post-Backward Callback]
    end
    
    subgraph "BucketManager Coordination"
        BM[BucketManager]
        PARAM_MAP[params_to_bucket_location]
        GRAD_DATA[grad_data_list]
    end
    
    subgraph "Bucket Storage and Sync"
        B1[Bucket_0]
        B2[Bucket_1]
        BN[Bucket_N]
        HANDLE1[async_handle_0]
        HANDLE2[async_handle_1]
        HANDLEN[async_handle_N]
    end
    
    subgraph "Model Parameters"
        PARAM1[param.main_grad]
        PARAM2[param.main_grad]
        PARAMN[param.main_grad]
    end
    
    DPB --> BM
    DPB --> HOOKS
    HOOKS --> CALLBACK
    
    BM --> PARAM_MAP
    BM --> GRAD_DATA
    BM --> B1
    BM --> B2
    BM --> BN
    
    B1 --> HANDLE1
    B2 --> HANDLE2
    BN --> HANDLEN
    
    PARAM_MAP -.-> PARAM1
    PARAM_MAP -.-> PARAM2
    PARAM_MAP -.-> PARAMN
    
    GRAD_DATA -.-> PARAM1
    GRAD_DATA -.-> PARAM2
    GRAD_DATA -.-> PARAMN
```

Sources: [step6_data_parallel_bucket/patch_step_6.diff:146-238](), [step6_data_parallel_bucket/patch_step_6.diff:64-144](), [step6_data_parallel_bucket/patch_step_6.diff:20-62]()

## Core Components

### DataParallelBucket Class

The `DataParallelBucket` class serves as the main interface, wrapping the model and coordinating gradient synchronization. It manages the overall process including gradient accumulation and backward hook registration.

| Component | Purpose | Key Methods |
|-----------|---------|-------------|
| `module` | Wrapped model reference | `forward()`, `backward()` |
| `bucket_manager` | Coordinates bucket operations | `mark_param_as_ready()`, `wait()` |
| `require_backward_grad_sync` | Controls sync timing | Set per micro-batch |
| `grad_accs` | Gradient accumulator functions | Registered as hooks |

The class automatically calculates bucket size based on a configurable capacity (default 25MB) and gradient data type size.

Sources: [step6_data_parallel_bucket/patch_step_6.diff:146-156]()

### BucketManager Class  

The `BucketManager` divides model parameters into buckets and manages the mapping between parameters and their storage locations within buckets.

```mermaid
graph LR
    subgraph "Parameter Division Process"
        PARAMS[Model Parameters]
        BUCKET_LOGIC[Bucket Assignment Logic]
        BUCKET_STORAGE[Bucket Storage Tensors]
    end
    
    subgraph "Bucket Organization"
        BUCKET0["Bucket 0<br/>params: [p1, p2]<br/>size: 12MB"]
        BUCKET1["Bucket 1<br/>params: [p3, p4, p5]<br/>size: 18MB"]  
        BUCKET2["Bucket 2<br/>params: [p6]<br/>size: 8MB"]
    end
    
    subgraph "Parameter Mapping"
        MAP["params_to_bucket_location<br/>{param: (start, end, bucket_id)}"]
        VIEWS["Parameter Views<br/>param.main_grad"]
    end
    
    PARAMS --> BUCKET_LOGIC
    BUCKET_LOGIC --> BUCKET0
    BUCKET_LOGIC --> BUCKET1  
    BUCKET_LOGIC --> BUCKET2
    
    BUCKET0 --> MAP
    BUCKET1 --> MAP
    BUCKET2 --> MAP
    
    MAP --> VIEWS
    BUCKET_STORAGE --> VIEWS
```

The bucket assignment algorithm works sequentially through parameters, creating new buckets when the size limit would be exceeded.

Sources: [step6_data_parallel_bucket/patch_step_6.diff:83-127]()

### Bucket Class

Individual `Bucket` instances manage gradient synchronization for their assigned parameters. Each bucket tracks parameter readiness and launches asynchronous all-reduce operations.

| Attribute | Purpose |
|-----------|---------|
| `params` | Set of parameters in this bucket |
| `params_with_grad_ready` | Parameters ready for synchronization |
| `grad_data` | Tensor storing gradients for this bucket |
| `process_group` | Data parallel process group |
| `handle` | Async all-reduce operation handle |

Sources: [step6_data_parallel_bucket/patch_step_6.diff:20-34]()

## Gradient Synchronization Flow

The gradient synchronization process involves multiple stages, from parameter readiness detection to final gradient application:

```mermaid
sequenceDiagram
    participant BP as Backward Pass
    participant PH as Parameter Hook
    participant BM as BucketManager  
    participant B as Bucket
    participant AR as All-Reduce
    participant CB as Post-Backward Callback
    
    BP->>PH: Parameter gradient ready
    PH->>PH: Accumulate to main_grad
    PH->>BM: mark_param_as_ready(param)
    BM->>B: mark_param_as_ready(param)
    
    alt All bucket params ready
        B->>B: Average gradients
        B->>AR: async all_reduce(grad_data)
        AR-->>B: Return handle
    end
    
    BP->>CB: Backward pass complete
    CB->>BM: wait()
    BM->>B: wait()
    B->>AR: handle.wait()
    CB->>CB: Copy main_grad to param.grad
```

The key optimization is that all-reduce operations begin as soon as individual buckets are complete, rather than waiting for all parameters to be ready.

Sources: [step6_data_parallel_bucket/patch_step_6.diff:194-220](), [step6_data_parallel_bucket/patch_step_6.diff:56-62]()

## Integration with Training Loop

The bucketed data parallelism integrates seamlessly with the training process through the `require_backward_grad_sync` flag and gradient accumulation control.

### Training Step Integration

```mermaid
graph TD
    subgraph "Training Step Process"
        START[Start Training Step]
        MICRO1[Micro-batch 1]
        MICRO2[Micro-batch 2]
        MICRON[Micro-batch N]
        OPT[Optimizer Step]
        RESET[Reset Buckets]
    end
    
    subgraph "Gradient Sync Control"
        SYNC_OFF[require_backward_grad_sync = False]
        SYNC_ON[require_backward_grad_sync = True]
        ACCUMULATE[Accumulate Gradients Only]
        SYNCHRONIZE[Synchronize + Accumulate]
    end
    
    START --> MICRO1
    MICRO1 --> MICRO2
    MICRO2 --> MICRON
    MICRON --> OPT
    OPT --> RESET
    
    MICRO1 --> SYNC_OFF
    MICRO2 --> SYNC_OFF
    MICRON --> SYNC_ON
    
    SYNC_OFF --> ACCUMULATE
    SYNC_ON --> SYNCHRONIZE
```

The training script controls synchronization timing by setting `model.require_backward_grad_sync = (i == dataloader.grad_acc_steps - 1)` to enable synchronization only on the final micro-batch.

Sources: [step6_data_parallel_bucket/train.py:29-40]()

### Model Wrapping Process

The model is wrapped with `DataParallelBucket` after tensor parallel application and device placement:

| Step | Code Location | Purpose |
|------|---------------|---------|
| Apply tensor parallel | [step6_data_parallel_bucket/train.py:134-135]() | Shard model weights |
| Move to device | [step6_data_parallel_bucket/train.py:139]() | Place on GPU before hook registration |
| Wrap with DataParallelBucket | [step6_data_parallel_bucket/train.py:141-142]() | Enable gradient bucketing |

The device placement before wrapping is critical because backward hooks must be attached to the GPU model instance.

Sources: [step6_data_parallel_bucket/train.py:134-144]()

## Memory and Communication Optimization

The bucketed approach provides several optimization benefits compared to naive data parallelism:

### Bucket Size Configuration

The default bucket capacity is 25MB, calculated as:
```
bucket_size = bucket_cap_mb * 1024 * 1024 // grad_size
```

Where `grad_size = 2` bytes for bfloat16 gradients, resulting in approximately 13M gradient elements per bucket.

### Gradient Data Type Handling

The system supports mixed precision by storing gradients in a configurable type (default `torch.float32`) while copying them back to parameter dtype during the post-backward callback. This prevents precision loss during accumulation while maintaining compatibility with the optimizer.

Sources: [step6_data_parallel_bucket/patch_step_6.diff:147-155](), [step6_data_parallel_bucket/patch_step_6.diff:234]()

### Asynchronous Communication Pattern

Unlike naive data parallelism which performs blocking all-reduce operations, the bucketed approach uses `async_op=True` to enable computation-communication overlap. The `handle.wait()` call is deferred until the post-backward callback, allowing gradient computation to continue while communication proceeds.

Sources: [step6_data_parallel_bucket/patch_step_6.diff:40](), [step6_data_parallel_bucket/patch_step_6.diff:52-54]()

---

