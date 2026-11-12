<!-- source: DeepWiki mcp.deepwiki.com · repo deepseek-ai/DualPipe · page 4 Core Components · fetched 2026-10-30 -->

# Core Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [dualpipe/__init__.py](dualpipe/__init__.py)
- [dualpipe/comm.py](dualpipe/comm.py)
- [dualpipe/utils.py](dualpipe/utils.py)

</details>



This page documents the foundational components shared by both `DualPipe` and `DualPipeV` implementations. These components provide essential functionality for weight gradient management, communication between pipeline stages, and tensor manipulation.

## Overview of Core Components

The DualPipe codebase is built on several key components that work together to enable efficient pipeline parallelism:

```mermaid
graph TD
    subgraph "Core Components"
        WGS["WeightGradStore Class (dualpipe/utils.py)"]
        COM["Communication Utilities (dualpipe/comm.py)"]
        UTIL["Tensor Utilities (dualpipe/utils.py)"]
    end
    
    subgraph "Main Implementations"
        DP["DualPipe (dualpipe/dualpipe.py)"]
        DPV["DualPipeV (dualpipe/dualpipev.py)"]
    end
    
    WGS -->|"Gradient management"| DP
    WGS -->|"Gradient management"| DPV
    
    COM -->|"P2P communication"| DP
    COM -->|"P2P communication"| DPV
    
    UTIL -->|"Tensor operations"| DP
    UTIL -->|"Tensor operations"| DPV
```

Sources: [dualpipe/__init__.py:1-17](), [dualpipe/utils.py:1-80](), [dualpipe/comm.py:1-38]()

## Weight Gradient Management

The `WeightGradStore` is a critical component that manages the collection, storage, and application of weight gradients during pipeline parallelism. It enables efficient gradient accumulation across micro-batches and supports deferred weight gradient computation (the "W" phase) to maximize overlap.

For details, see [Weight Gradient Management](#4.1).

### WeightGradStore Implementation

```mermaid
classDiagram
    class WeightGradStore {
        +bool enabled
        +List[Callable] cache
        +Queue funcs_queue
        +put(func: Callable)
        +flush()
        +pop()
        +clear()
    }
    
    note for WeightGradStore "Static class in dualpipe/utils.py\nmanaging gradient accumulation"
```

The `WeightGradStore` manages a lifecycle of `put`, `flush`, and `pop` [dualpipe/utils.py:15-29](). It works alongside the `run_backward` utility [dualpipe/utils.py:36-43](), which uses `accumulate_grad=True` to allow multiple backward passes to contribute to the same gradient tensors without immediate optimizer steps.

Sources: [dualpipe/utils.py:8-43]()

## Communication System

The communication system provides utilities for point-to-point (P2P) tensor exchange between pipeline stages using PyTorch's distributed communication primitives (`dist.P2POp`). It abstracts global rank translation and buffer management.

For details, see [Communication System](#4.2).

### Communication Flow

```mermaid
sequenceDiagram
    participant Stage1 as "Pipeline Stage 1"
    participant Stage2 as "Pipeline Stage 2"
    
    Note over Stage1,Stage2: Global State: TENSOR_SHAPES, TENSOR_DTYPE
    
    Stage1->>Stage1: build_from_tensor_shapes()
    Stage1-->>Stage2: append_isend(ops, tensors, dst, group)
    Stage2->>Stage2: append_irecv(ops, src, group)
    
    Note over Stage1,Stage2: batch_isend_irecv() executes P2POps
```

The system relies on global configuration via `set_p2p_tensor_shapes` [dualpipe/comm.py:11-13]() and `set_p2p_tensor_dtype` [dualpipe/comm.py:16-18](). It uses `dist.distributed_c10d.get_global_rank` to ensure P2P operations target the correct ranks across the distributed group [dualpipe/comm.py:27-35]().

Sources: [dualpipe/comm.py:1-38]()

## Tensor Utilities

The tensor utilities provide functions for manipulating tensors during pipeline execution, particularly for handling micro-batches and gradient computation.

### Tensor Operations

| Function | Purpose | Description |
|----------|---------|-------------|
| `run_backward` | Gradient computation | Executes backward pass with `accumulate_grad=True` [dualpipe/utils.py:36-43]() |
| `chunk_tensor` | Tensor splitting | Divides tensors into chunks using `tensor_split` [dualpipe/utils.py:46-49]() |
| `cat_tensor` | Tensor concatenation | Combines tensors from multiple micro-batches using `torch.cat` [dualpipe/utils.py:52-59]() |
| `scatter` | Input distribution | Distributes inputs into micro-batches for the pipeline [dualpipe/utils.py:62-71]() |
| `gather` | Output collection | Collects and concatenates outputs from micro-batches [dualpipe/utils.py:74-80]() |

```mermaid
graph TD
    subgraph "Tensor Flow in Pipeline"
        Input["Input Tensor(s)"]
        Microbatches["Micro-batches"]
        ProcessedMicro["Processed Micro-batches"]
        Output["Output Tensor(s)"]
        
        Input -->|"scatter()"| Microbatches
        Microbatches -->|"Process through pipeline"| ProcessedMicro
        ProcessedMicro -->|"gather()"| Output
    end
    
    subgraph "Internal Logic (dualpipe/utils.py)"
        chunk["chunk_tensor()"]
        cat["cat_tensor()"]
        backward["run_backward()"]
    end
    
    scatter -->|"uses"| chunk
    gather -->|"uses"| cat
    ProcessedMicro -->|"Gradient computation"| backward
```

Sources: [dualpipe/utils.py:36-80]()

## Integration in Pipeline Parallelism

The core components are integrated into the pipeline parallelism framework to facilitate the bidirectional 8-step schedule used by `DualPipe` and `DualPipeV`.

During execution:
1. **Forward Pass**: `scatter` divides inputs [dualpipe/utils.py:62](), and `append_isend`/`append_irecv` handle activation exchange [dualpipe/comm.py:25-38]().
2. **Backward Pass**: `run_backward` computes gradients [dualpipe/utils.py:36](), while `WeightGradStore.put` captures weight gradient functions [dualpipe/utils.py:15]().
3. **Overlap Phase**: While new micro-batches are computed, `WeightGradStore.pop` executes deferred weight gradient computations to fill pipeline bubbles [dualpipe/utils.py:24]().

Sources: [dualpipe/utils.py:1-80](), [dualpipe/comm.py:1-38]()

---

