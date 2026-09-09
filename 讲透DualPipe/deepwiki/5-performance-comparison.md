> 来源: [https://deepwiki.com/deepseek-ai/DualPipe/5-performance-comparison](https://deepwiki.com/deepseek-ai/DualPipe/5-performance-comparison)
> DeepWiki deepseek-ai/DualPipe

# Performance Comparison

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/DualPipe/blob/030ce432/README.md?plain=1)
 - [images/dualpipe.png](https://github.com/deepseek-ai/DualPipe/blob/030ce432/images/dualpipe.png)
 - [images/dualpipev.png](https://github.com/deepseek-ai/DualPipe/blob/030ce432/images/dualpipev.png)
 
  This document provides a technical comparison of DualPipe and DualPipeV pipeline parallelism methods against traditional approaches like 1F1B (One-Forward-One-Backward) and ZB1P (Zero-Bubble 1-Phase). We analyze performance characteristics, memory requirements, device utilization, and pipeline bubble optimization.

 
## Pipeline Bubbles and Memory Footprint

 The primary motivation for DualPipe is the reduction of the "pipeline bubble"—the idle time ranks spend waiting for data from other stages. DualPipe achieves a significantly smaller bubble compared to 1F1B and ZB1P by overlapping forward (F) and backward (B) chunks across two symmetric directions.

 
### Comparison Table

 
| Method | Bubble Size Formula | Parameter Memory | Activation Memory | Devices |
|---|---|---|---|---|
| 1F1B | $(PP-1)(F+B)$ | $1\times$ | $PP$ | $PP$ |
| ZB1P | $(PP-1)(F+B-2W)$ | $1\times$ | $PP$ | $PP$ |
| DualPipe | $(PP/2-1)(F&B+B-3W)$ | $2\times$ | $PP+1$ | $PP$ |
| DualPipeV | $(PP/2-1)(F&B+B-3W)$ | $2\times$ | $PP+1$ | $PP/2$ |

 **Definitions:**

 
 - **$PP$**: Total number of pipeline stages.
 - **$F$**: Execution time of a forward chunk.
 - **$B$**: Execution time of a full backward chunk (Activation grad + Weight grad).
 - **$W$**: Execution time of a "backward for weights" chunk.
 - **$F&B$**: Execution time of mutually overlapped forward and backward chunks.
 
 Sources: [README.md24-36](https://github.com/deepseek-ai/DualPipe/blob/030ce432/README.md?plain=1#L24-L36)

 
## Scheduling Logic and Data Flow

 The performance gains in DualPipe are realized through an 8-step schedule that manages bidirectional micro-batches. DualPipeV achieves the same bubble efficiency by folding the pipeline into a V-shape, allowing two logical stages to reside on one physical device.

 
### Code-to-Entity Mapping: Scheduling Components

 The following diagram maps the logical scheduling phases described in the performance formulas to the internal methods within the `DualPipe` and `DualPipeV` classes.

 
```

```

 Sources: [dualpipe/main.py151-240](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/main.py#L151-L240) [dualpipev/main.py176-281](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipev/main.py#L176-L281)

 
## Computation-Communication Overlap

 A key differentiator for DualPipe is the full overlap of computation and communication. While traditional methods often stall for P2P transfers, DualPipe utilizes asynchronous communication dispatched via `dualpipe.comm` to hide latency behind the `overlapped_forward_backward` computation.

 
### Data Flow for Overlapped Execution

 This diagram illustrates how the system transitions from the "Natural Language" concept of overlap to the "Code Space" implementation using `WeightGradStore` and `batch_isend_irecv`.

 
```

```

 Sources: [dualpipe/main.py276-302](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/main.py#L276-L302) [dualpipe/comm.py38](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/comm.py#L38-L38) [dualpipe/utils.py46-56](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/utils.py#L46-L56)

 
## Trade-off Analysis

 
### 1. Memory vs. Throughput

 DualPipe requires **2× Parameter Memory** because each device must store parameters for two different stages (or two directions) to facilitate the bidirectional flow. This is the primary cost for reducing the bubble from $(PP-1)$ to approximately $(PP/2-1)$.

 
### 2. Activation Memory

 Activation memory increases slightly ($PP+1$ vs $PP$) due to the additional micro-batches held in flight to maintain the bidirectional pipeline pressure.

 
### 3. Device Utilization (DualPipe vs DualPipeV)

 
 - **DualPipe**: Utilizes $PP$ physical devices. Each device handles two logical stages (one for each direction).
 - **DualPipeV**: Utilizes $PP/2$ physical devices. Each device handles two logical stages from the *same* direction but at different depths of the V-shape.
 - **Result**: DualPipeV provides the same throughput and bubble reduction as DualPipe but consumes half the physical hardware resources.
 
 Sources: [README.md24-36](https://github.com/deepseek-ai/DualPipe/blob/030ce432/README.md?plain=1#L24-L36) [dualpipev/main.py15-30](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipev/main.py#L15-L30)

 
## Implementation Requirements for Peak Performance

 To achieve the theoretical performance limits:

 
 - **Custom Autograd**: Users must use custom autograd functions that separate input gradient computation from weight gradient computation. This is demonstrated in the `LinearFunc` implementation in the examples. [examples/example_dualpipe.py13-34](https://github.com/deepseek-ai/DualPipe/blob/030ce432/examples/example_dualpipe.py#L13-L34)
 - **WeightGradStore**: The `WeightGradStore` must be used to defer weight gradient updates, allowing the "Backward for Weights" ($W$) phase to be shifted out of the critical path. [dualpipe/utils.py46-68](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/utils.py#L46-L68)
 - **P2P Buffers**: Proper tensor shape and dtype configuration via `set_p2p_tensor_shapes` is mandatory to avoid dynamic allocation overhead during the `step()` loop. [dualpipe/comm.py32-38](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/comm.py#L32-L38)
 
 Sources: [examples/example_dualpipe.py54-83](https://github.com/deepseek-ai/DualPipe/blob/030ce432/examples/example_dualpipe.py#L54-L83) [dualpipe/main.py261-274](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/main.py#L261-L274)
