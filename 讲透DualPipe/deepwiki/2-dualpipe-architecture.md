> 来源: [https://deepwiki.com/deepseek-ai/DualPipe/2-dualpipe-architecture](https://deepwiki.com/deepseek-ai/DualPipe/2-dualpipe-architecture)
> DeepWiki deepseek-ai/DualPipe

# DualPipe Architecture

  Relevant source files 
 - [dualpipe/dualpipe.py](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipe.py)
 - [images/dualpipe.png](https://github.com/deepseek-ai/DualPipe/blob/030ce432/images/dualpipe.png)
 
  This document provides a detailed technical overview of the DualPipe pipeline parallelism architecture. DualPipe is a bidirectional pipeline parallelism algorithm introduced in the DeepSeek-V3 Technical Report that achieves full overlap of forward and backward computation-communication phases, significantly reducing pipeline bubbles. For information about the DualPipeV variant, which uses a "cut-in-half" approach with fewer devices, see [DualPipeV Architecture](https://deepwiki.com/deepseek-ai/DualPipe/3-dualpipev-architecture).

 
## Core Concepts and Design Principles

 DualPipe is designed to maximize hardware utilization in distributed training by implementing an innovative bidirectional schedule that reduces pipeline bubbles - the idle periods in traditional pipeline parallelism methods.

 The key design principles of DualPipe are:

 
 - **Bidirectional Execution**: Uses both forward and reverse pipeline directions simultaneously.
 - **Full Computation-Communication Overlap**: Overlaps forward and backward passes with communication.
 - **Zero-Bubble Optimization**: Strategically uses zero-bubble techniques to further reduce idle time.
 - **Balanced Pipeline Stages**: Works with an even number of pipeline stages/ranks arranged in two halves.
 
 
```

```

 Sources: [dualpipe/dualpipe.py11-45](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipe.py#L11-L45)

 
## System Architecture

 DualPipe is implemented as a PyTorch module that encapsulates distributed pipeline parallelism logic. The system requires an even number of pipeline stages distributed across multiple devices.

 
```

```

 Sources: [dualpipe/dualpipe.py11-45](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipe.py#L11-L45) [dualpipe/utils.py11-13](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/utils.py#L11-L13)

 
## Pipeline Stage Configuration

 DualPipe divides the model into two halves across an even number of ranks (pipeline stages). The directionality and behavior of each rank depends on its position in the pipeline. The `rank_mapping` allows for flexible physical-to-logical rank assignment [dualpipe/dualpipe.py30-36](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipe.py#L30-L36)

 
| Position | Description | Behavior |
|---|---|---|
| First Rank (0) | Start of forward direction | Receives initial input tensors dualpipe/dualpipe.py42 |
| Last Rank (num_ranks-1) | Start of reverse direction | Receives reverse direction input tensors dualpipe/dualpipe.py43 |
| Middle Ranks | Transition between halves | Special handling for phase transitions dualpipe/dualpipe.py45 |
| First Half Ranks | Ranks 0 to (num_ranks/2-1) | Phase 0 = forward, Phase 1 = reverse dualpipe/dualpipe.py44 |
| Second Half Ranks | Ranks (num_ranks/2) to (num_ranks-1) | Phase 0 = reverse, Phase 1 = forward dualpipe/dualpipe.py44 |

 
```

```

 Sources: [dualpipe/dualpipe.py42-45](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipe.py#L42-L45) [dualpipe/dualpipe.py334-338](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipe.py#L334-L338)

 
## Execution Phases

 The DualPipe algorithm executes in 8 distinct steps to orchestrate the bidirectional flow. Each step has a specific purpose in the overall pipeline execution, managed within the `step()` method [dualpipe/dualpipe.py294-425](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipe.py#L294-L425)

 
```

```

 Sources: [dualpipe/dualpipe.py358-425](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipe.py#L358-L425)

 
### Step 1: Initial Forward (Phase 0)

 Performs initial forward passes in one direction to fill the pipeline. The number of iterations is determined by the rank's position relative to the pipeline center [dualpipe/dualpipe.py358-361](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipe.py#L358-L361)

 
### Step 4: Main Step - Overlapped Bidirectional Execution

 This is the core of DualPipe where forward and backward passes are fully overlapped in both directions. It utilizes `_forward_backward_compute_chunk` to execute concurrent computation [dualpipe/dualpipe.py382-396](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipe.py#L382-L396)

 
```

```

 Sources: [dualpipe/dualpipe.py382-396](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipe.py#L382-L396)

 
## Technical Implementation Details

 
### Input/Output Management

 DualPipe divides the input batch into micro-batches that are processed through the pipeline. Each stage maintains several data structures to track these micro-batches, which are reset at the start of every iteration via `_reset_states()` [dualpipe/dualpipe.py47-65](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipe.py#L47-L65)

 
```

```

 Sources: [dualpipe/dualpipe.py50-65](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipe.py#L50-L65)

 
### Forward and Backward Computation

 DualPipe implements several key methods for computation:

 
 - `_forward_compute_chunk`: Executes a forward pass for a specific phase [dualpipe/dualpipe.py67-86](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipe.py#L67-L86)
 - `_backward_compute_chunk`: Executes a backward pass with optional zero-bubble optimization via `WeightGradStore` [dualpipe/dualpipe.py87-120](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipe.py#L87-L120)
 - `_forward_backward_compute_chunk`: Overlaps forward and backward computation for maximum efficiency [dualpipe/dualpipe.py121-183](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipe.py#L121-L183)
 
 When the model supports it, DualPipe can use custom `overlapped_forward_backward` methods to further optimize the overlapped execution [dualpipe/dualpipe.py168-171](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipe.py#L168-L171)

 For details, see [DualPipe Implementation](https://deepwiki.com/deepseek-ai/DualPipe/2.1-dualpipe-implementation).

 
### Communication System

 DualPipe uses non-blocking point-to-point communication operations to exchange tensors between pipeline stages. These are orchestrated by methods like `_recv_forward`, `_send_forward`, and `_commit_and_wait_comm` [dualpipe/dualpipe.py231-292](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipe.py#L231-L292)

 For details, see [DualPipe Implementation](https://deepwiki.com/deepseek-ai/DualPipe/2.1-dualpipe-implementation).

 
### Zero-Bubble Optimization

 DualPipe strategically uses zero-bubble techniques to further reduce pipeline bubbles. This is implemented through the `WeightGradStore` system that manages gradient accumulation and deferred weight gradient computation [dualpipe/utils.py11-53](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/utils.py#L11-L53)

 
```

```

 Sources: [dualpipe/dualpipe.py97-115](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipe.py#L97-L115) [dualpipe/dualpipe.py216-224](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipe.py#L216-L224)

 
## Step Method API

 The main interface to DualPipe is the `step` method, which executes a full forward and backward pass through the pipeline. It handles the splitting of inputs using `scatter` and gathering of results using `gather` [dualpipe/dualpipe.py294-440](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipe.py#L294-L440)

 
### Key Parameters:

 
| Parameter | Type | Description |
|---|---|---|
| inputs | torch.Tensor | Input tensors for the model (required only on first/last ranks) |
| num_chunks | int | Number of micro-batches to use (must be even and >= num_ranks*2) |
| criterion | Callable | Loss function used on first/last ranks |
| labels | List[torch.Tensor] | Labels for the loss function |
| return_outputs | bool | Whether to return model outputs |

 Sources: [dualpipe/dualpipe.py294-304](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipe.py#L294-L304)

 For details on usage, see [DualPipe Example Usage](https://deepwiki.com/deepseek-ai/DualPipe/2.2-dualpipe-example-usage).

 
## Memory and Performance Characteristics

 DualPipe makes specific tradeoffs to achieve better pipeline efficiency:

 
| Characteristic | DualPipe | Traditional Methods (1F1B) |
|---|---|---|
| Pipeline Bubbles | (PP/2-1)(F&B+B-3W) | (PP-1)(F+B) |
| Parameter Memory | 2× | 1× |
| Activation Memory | PP+1 | PP |
| Number of Devices | PP | PP |

 Sources: [dualpipe/dualpipe.py11-45](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipe.py#L11-L45)
