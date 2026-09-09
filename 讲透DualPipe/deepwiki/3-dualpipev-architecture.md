> 来源: [https://deepwiki.com/deepseek-ai/DualPipe/3-dualpipev-architecture](https://deepwiki.com/deepseek-ai/DualPipe/3-dualpipev-architecture)
> DeepWiki deepseek-ai/DualPipe

# DualPipeV Architecture

  Relevant source files 
 - [dualpipe/dualpipev.py](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipev.py)
 - [images/dualpipev.png](https://github.com/deepseek-ai/DualPipe/blob/030ce432/images/dualpipev.png)
 
  
## Purpose

 This document explains the DualPipeV architecture, a variant of pipeline parallelism that achieves the same efficiency as DualPipe while requiring only half the number of devices. For information about the original DualPipe architecture, see [DualPipe Architecture](https://deepwiki.com/deepseek-ai/DualPipe/2-dualpipe-architecture).

 
## Overview

 DualPipeV is a concise V-shape schedule derived from DualPipe using a "cut-in-half" procedure. It was introduced by Sea AI Lab and integrated into the DeepSeek-V3 architecture as documented in the DeepSeek-V3 Technical Report.

 
### Key Features

 
 - Implements a V-shape pipeline parallelism schedule [dualpipe/dualpipev.py11-12](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipev.py#L11-L12)
 - Requires only PP/2 devices compared to DualPipe's PP devices [README.md14-16](https://github.com/deepseek-ai/DualPipe/blob/030ce432/README.md?plain=1#L14-L16)
 - Maintains the same pipeline bubble size as DualPipe [README.md24-36](https://github.com/deepseek-ai/DualPipe/blob/030ce432/README.md?plain=1#L24-L36)
 - Achieves full overlap of forward and backward computation-communication phases [dualpipe/dualpipev.py23](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipev.py#L23-L23)
 
 For implementation details, see [DualPipeV Implementation](https://deepwiki.com/deepseek-ai/DualPipe/3.1-dualpipev-implementation).

 Sources: [README.md14-16](https://github.com/deepseek-ai/DualPipe/blob/030ce432/README.md?plain=1#L14-L16) [dualpipe/dualpipev.py11-23](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipev.py#L11-L23)

 
## V-Shape Schedule Concept

 
### Diagram: DualPipeV V-Shape Schedule

 
```

```

 In this diagram, data flows forward through the first half of pipeline stages (Phase 0), then makes a "V-turn" at the midpoint (the physical last rank) before flowing through the second half of the pipeline (Phase 1) on the same devices in reverse order. This differs from traditional pipeline parallelism where data flows linearly through twice as many distinct ranks.

 The V-shape schedule allows DualPipeV to effectively simulate a pipeline with `PP` stages using only `PP/2` devices by having each device process data in both the forward and backward directions of the V-shape [dualpipe/dualpipev.py70-80](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipev.py#L70-L80)

 Sources: [README.md19-22](https://github.com/deepseek-ai/DualPipe/blob/030ce432/README.md?plain=1#L19-L22) [dualpipe/dualpipev.py11-12](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipev.py#L11-L12) [dualpipe/dualpipev.py70-80](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipev.py#L70-L80)

 
## Pipeline Parallelism Comparison

 The following table compares DualPipeV with other pipeline parallelism methods:

 
| Method | Pipeline Bubble Size | Parameter Memory | Activation Memory | Required Devices |
|---|---|---|---|---|
| 1F1B | (PP-1)(𝐹+𝐵) | 1× | PP | PP |
| ZB1P | (PP-1)(𝐹+𝐵-2𝑊) | 1× | PP | PP |
| DualPipe | (PP/2-1)(𝐹&𝐵+𝐵-3𝑊) | 2× | PP+1 | PP |
| DualPipeV | (PP/2-1)(𝐹&𝐵+𝐵-3𝑊) | 2× | PP+1 | PP/2 |

 Where:

 
 - *PP* is the number of pipeline parallelism stages (must be even).
 - 𝐹 is the execution time of a forward pass.
 - 𝐵 is the execution time of a backward pass.
 - 𝑊 is the execution time of a "backward for weights" pass.
 - 𝐹&𝐵 is the execution time of overlapped forward and backward passes.
 
 Sources: [README.md24-36](https://github.com/deepseek-ai/DualPipe/blob/030ce432/README.md?plain=1#L24-L36)

 
## DualPipeV Class Implementation

 The `DualPipeV` class is implemented as a PyTorch module that manages pipeline parallelism using the V-shape schedule.

 
### Class Structure and Code Entities

 
```

```

 The `DualPipeV` class takes two modules that represent different segments of the pipeline (e.g., layers 0-N and layers N+1-2N) but reside on the same physical device [dualpipe/dualpipev.py12-22](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipev.py#L12-L22) It manages a complex scheduling system to ensure efficient overlapping of computation and communication.

 Sources: [dualpipe/dualpipev.py11-42](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipev.py#L11-L42) [dualpipe/dualpipev.py107](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipev.py#L107-L107)

 
## Execution Flow

 The execution of the DualPipeV pipeline is managed by the `step` method [dualpipe/dualpipev.py288](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipev.py#L288-L288)

 
### Diagram: DualPipeV Step Logic

 
```

```

 The `step` method implements the V-shape schedule through a sequence of 8 steps [dualpipe/dualpipev.py288-411](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipev.py#L288-L411) The execution is divided into two phases: `phase 0` (forward path of the V) and `phase 1` (backward path of the V).

 For a detailed walkthrough of this 8-step schedule, see [DualPipeV Implementation](https://deepwiki.com/deepseek-ai/DualPipe/3.1-dualpipev-implementation).

 Sources: [dualpipe/dualpipev.py288-411](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipev.py#L288-L411)

 
## Key Components and Internal Methods

 
### State Management

 DualPipeV maintains several internal state variables during execution to track micro-batch progress across the V-shape [dualpipe/dualpipev.py43-62](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipev.py#L43-L62):

 
 - `input_chunks`, `output_chunks`: Tensors for the forward passes of Phase 0 and 1.
 - `input_grad_chunks`, `output_grad_chunks`: Gradient tensors for the backward passes.
 - `current_f_chunk_id`, `current_b_chunk_id`: Tracking chunk IDs for forward and backward passes.
 - `comm_ops`: Pending communication operations to be executed via `dist.batch_isend_irecv`.
 
 Sources: [dualpipe/dualpipev.py43-62](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipev.py#L43-L62)

 
### Computation Methods

 DualPipeV implements several key computation methods:

 
 - `_forward_compute_chunk(phase)`: Executes forward computation for a specific phase [dualpipe/dualpipev.py63](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipev.py#L63-L63)
 - `_backward_compute_chunk(phase, enable_zb)`: Executes backward computation, optionally enabling `WeightGradStore` for zero-bubble weight updates [dualpipe/dualpipev.py84](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipev.py#L84-L84)
 - `_forward_backward_compute_chunk(phase0, phase1)`: The core overlap method that can call a module's custom `overlapped_forward_backward` hook [dualpipe/dualpipev.py120](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipev.py#L120-L120)
 
 Sources: [dualpipe/dualpipev.py63-126](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipev.py#L63-L126) [dualpipe/dualpipev.py127-186](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipev.py#L127-L186)

 
## Optimizations

 
### Zero Bubble Technique

 DualPipeV employs a "zero bubble" optimization in several steps to further reduce pipeline bubbles by accumulating weight gradients asynchronously [dualpipe/dualpipev.py344-350](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipev.py#L344-L350) This is managed via the `enable_zb` flag passed to `_backward_compute_chunk` [dualpipe/dualpipev.py84](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipev.py#L84-L84)

 
### Overlapped Forward-Backward Computation

 For modules that support it, DualPipeV can use an optimized `overlapped_forward_backward` computation [dualpipe/dualpipev.py165-168](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipev.py#L165-L168) This allows the model to overlap the forward pass of one micro-batch with the backward pass of another at the kernel level.

 For details on how to implement these modules, see [DualPipeV Example Usage](https://deepwiki.com/deepseek-ai/DualPipe/3.2-dualpipev-example-usage).

 Sources: [dualpipe/dualpipev.py84](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipev.py#L84-L84) [dualpipe/dualpipev.py165-168](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipev.py#L165-L168) [dualpipe/dualpipev.py344-350](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipev.py#L344-L350)
