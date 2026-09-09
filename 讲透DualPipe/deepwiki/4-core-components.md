> 来源: [https://deepwiki.com/deepseek-ai/DualPipe/4-core-components](https://deepwiki.com/deepseek-ai/DualPipe/4-core-components)
> DeepWiki deepseek-ai/DualPipe

# Core Components

  Relevant source files 
 - [dualpipe/__init__.py](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/__init__.py)
 - [dualpipe/comm.py](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/comm.py)
 - [dualpipe/utils.py](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/utils.py)
 
  This page documents the foundational components shared by both `DualPipe` and `DualPipeV` implementations. These components provide essential functionality for weight gradient management, communication between pipeline stages, and tensor manipulation.

 
## Overview of Core Components

 The DualPipe codebase is built on several key components that work together to enable efficient pipeline parallelism:

 
```

```

 Sources: [dualpipe/__init__.py1-17](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/__init__.py#L1-L17) [dualpipe/utils.py1-80](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/utils.py#L1-L80) [dualpipe/comm.py1-38](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/comm.py#L1-L38)

 
## Weight Gradient Management

 The `WeightGradStore` is a critical component that manages the collection, storage, and application of weight gradients during pipeline parallelism. It enables efficient gradient accumulation across micro-batches and supports deferred weight gradient computation (the "W" phase) to maximize overlap.

 For details, see [Weight Gradient Management](https://deepwiki.com/deepseek-ai/DualPipe/4.1-weight-gradient-management).

 
### WeightGradStore Implementation

 
```

```

 The `WeightGradStore` manages a lifecycle of `put`, `flush`, and `pop` [dualpipe/utils.py15-29](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/utils.py#L15-L29) It works alongside the `run_backward` utility [dualpipe/utils.py36-43](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/utils.py#L36-L43) which uses `accumulate_grad=True` to allow multiple backward passes to contribute to the same gradient tensors without immediate optimizer steps.

 Sources: [dualpipe/utils.py8-43](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/utils.py#L8-L43)

 
## Communication System

 The communication system provides utilities for point-to-point (P2P) tensor exchange between pipeline stages using PyTorch's distributed communication primitives (`dist.P2POp`). It abstracts global rank translation and buffer management.

 For details, see [Communication System](https://deepwiki.com/deepseek-ai/DualPipe/4.2-communication-system).

 
### Communication Flow

 
```

```

 The system relies on global configuration via `set_p2p_tensor_shapes` [dualpipe/comm.py11-13](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/comm.py#L11-L13) and `set_p2p_tensor_dtype` [dualpipe/comm.py16-18](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/comm.py#L16-L18) It uses `dist.distributed_c10d.get_global_rank` to ensure P2P operations target the correct ranks across the distributed group [dualpipe/comm.py27-35](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/comm.py#L27-L35)

 Sources: [dualpipe/comm.py1-38](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/comm.py#L1-L38)

 
## Tensor Utilities

 The tensor utilities provide functions for manipulating tensors during pipeline execution, particularly for handling micro-batches and gradient computation.

 
### Tensor Operations

 
| Function | Purpose | Description |
|---|---|---|
| run_backward | Gradient computation | Executes backward pass with accumulate_grad=True dualpipe/utils.py36-43 |
| chunk_tensor | Tensor splitting | Divides tensors into chunks using tensor_split dualpipe/utils.py46-49 |
| cat_tensor | Tensor concatenation | Combines tensors from multiple micro-batches using torch.cat dualpipe/utils.py52-59 |
| scatter | Input distribution | Distributes inputs into micro-batches for the pipeline dualpipe/utils.py62-71 |
| gather | Output collection | Collects and concatenates outputs from micro-batches dualpipe/utils.py74-80 |

 
```

```

 Sources: [dualpipe/utils.py36-80](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/utils.py#L36-L80)

 
## Integration in Pipeline Parallelism

 The core components are integrated into the pipeline parallelism framework to facilitate the bidirectional 8-step schedule used by `DualPipe` and `DualPipeV`.

 During execution:

 
 - **Forward Pass**: `scatter` divides inputs [dualpipe/utils.py62](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/utils.py#L62-L62) and `append_isend`/`append_irecv` handle activation exchange [dualpipe/comm.py25-38](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/comm.py#L25-L38)
 - **Backward Pass**: `run_backward` computes gradients [dualpipe/utils.py36](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/utils.py#L36-L36) while `WeightGradStore.put` captures weight gradient functions [dualpipe/utils.py15](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/utils.py#L15-L15)
 - **Overlap Phase**: While new micro-batches are computed, `WeightGradStore.pop` executes deferred weight gradient computations to fill pipeline bubbles [dualpipe/utils.py24](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/utils.py#L24-L24)
 
 Sources: [dualpipe/utils.py1-80](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/utils.py#L1-L80) [dualpipe/comm.py1-38](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/comm.py#L1-L38)
