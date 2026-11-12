<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/dl-cuda-graph-doc · page 5 Troubleshooting · fetched 2026-10-26 -->

# Troubleshooting

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/troubleshooting/debugging-strategies.md](docs/troubleshooting/debugging-strategies.md)
- [docs/troubleshooting/introduction.md](docs/troubleshooting/introduction.md)

</details>



The use of CUDA Graphs in PyTorch introduces a fundamentally different execution model: operations are captured once and replayed as a fixed unit. This shift from eager execution to a capture-replay model means that issues which would be obvious in standard code—such as synchronization errors or dynamic shape changes—can manifest as silent numerical failures, memory corruption, or complex process hangs [docs/troubleshooting/introduction.md:13-15]().

This section provides a systematic taxonomy of failure modes and detailed strategies for diagnosing and resolving them.

## Failure Mode Taxonomy

Troubleshooting is categorized by the phase of execution and the nature of the symptom.

| Failure Mode | Symptoms | Phase | Difficulty |
|--------------|----------|----------------|------------|
| 🛠️ **[Debugging Strategies](#5.1)** | Any issue | All phases | N/A |
| 🚫 **[Capture Failures](#5.2)** | `RuntimeError` during capture | Capture phase | ⭐ Easy |
| 🔢 **[Numerical Errors](#5.3)** | Wrong results, NaN/Inf | Replay phase | ⭐⭐⭐ Hard |
| 💾 **[Memory Issues](#5.4)** | OOM, allocation errors | Capture/Replay | ⭐⭐ Medium |
| ⏳ **[Process Hang](#5.5)** | Freezes, no progress | Any phase | ⭐⭐⭐⭐ Very Hard |
| 📉 **[Performance Issues](#5.6)** | Slower than expected | Replay phase | ⭐⭐ Medium |

Sources: [docs/troubleshooting/introduction.md:68-75]()

## From Symptoms to Code Entities

The following diagram maps common symptoms to the specific PyTorch and CUDA entities involved in the troubleshooting process.

### Symptom-to-Entity Mapping
```mermaid
graph TD
    "Symptom" --> "Failure_Category"
    
    subgraph "Failure_Category"
        "RuntimeError_during_capture"["RuntimeError during capture"]
        "Silent_Numerical_Divergence"["Silent Numerical Divergence"]
        "Process_Freeze"["Process Freeze"]
    end

    "RuntimeError_during_capture" --> "torch_cuda_graph_context"["torch.cuda.graph() context"]
    "RuntimeError_during_capture" --> "Illegal_Sync_Ops"["Illegal Sync: .item(), .cpu()"]
    
    "Silent_Numerical_Divergence" --> "Tensor_Reassignment"["Tensor Reassignment: x = y"]
    "Silent_Numerical_Divergence" --> "RNG_State"["torch.Generator state"]
    
    "Process_Freeze" --> "NCCL_Watchdog"["NCCL Watchdog / Work"]
    "Process_Freeze" --> "CUDA_Stream_Wait"["cudaStreamWaitEvent"]

    style "torch_cuda_graph_context" stroke-dasharray: 5 5
```
Sources: [docs/troubleshooting/debugging-strategies.md:70-85](), [docs/troubleshooting/introduction.md:36-55]()

## Troubleshooting Sub-sections

### 5.1 Debugging Strategies
Before diving into specific errors, it is essential to establish a baseline in eager mode. This section covers systematic isolation techniques, such as binary searching through captured regions and progressive simplification of model features (e.g., disabling dropout or pipeline parallelism) [docs/troubleshooting/debugging-strategies.md:17-40](). It also details how to use `g.enable_debug_mode()` and `g.debug_dump()` to visualize the captured DAG [docs/troubleshooting/debugging-strategies.md:90-106]().

For details, see **[Debugging Strategies](debugging-strategies.md)**.

### 5.2 Capture Failures
Capture failures typically occur when the code violates CUDA Graph constraints during the recording phase. Common causes include illegal synchronizations (e.g., calling `.item()` on a tensor), memory allocations within the capture stream, or using the default stream which may conflict with background tasks like the NCCL watchdog [docs/troubleshooting/debugging-strategies.md:70-75]().

For details, see **[Capture Failures](capture-failures.md)**.

### 5.3 Numerical Errors
Numerical errors are "silent" failures where the graph executes without error but produces incorrect outputs or NaNs. These often stem from reassigning input tensors (which breaks the static memory address requirement) instead of using in-place operations like `.copy_()`, or failing to manage RNG states across graph replays [docs/troubleshooting/debugging-strategies.md:109-135]().

For details, see **[Numerical Errors](numerical-errors.md)**.

### 5.4 Memory Issues
CUDA Graphs require a private memory pool to ensure addresses remain static. This can lead to Out-of-Memory (OOM) errors during capture if the pool overhead is too high, or memory leaks if graph objects are not managed correctly. This section explores interactions between the PyTorch caching allocator and graph memory management [docs/troubleshooting/introduction.md:43-48]().

For details, see **[Memory Issues](memory-issues.md)**.

### 5.5 Process Hang
Hangs are the most difficult to debug and often involve distributed training. They can be caused by deadlocks between the CPU and GPU, such as when a graph replay waits for a NCCL operation that was never properly synchronized, or when a data-dependent infinite loop is captured into the graph topology [docs/troubleshooting/introduction.md:50-55]().

For details, see **[Process Hang](process-hang.md)**.

### 5.6 Performance Issues
If a CUDA Graph does not provide a speedup, the application may not be CPU-bound, or the overhead of managing many small graphs may outweigh the launch savings. This section covers profiling with Nsight Systems to identify bottlenecks and optimize graph granularity [docs/troubleshooting/introduction.md:57-62]().

For details, see **[Performance Issues](performance-issues.md)**.

### Debugging Workflow
```mermaid
flowchart TD
    "Start"["Start Troubleshooting"] --> "EagerCheck"{"Does Eager Mode work?"}
    "EagerCheck" -- "No" --> "FixEager"["Fix standard PyTorch bugs"]
    "EagerCheck" -- "Yes" --> "CapturePhase"{"Does Capture succeed?"}
    
    "CapturePhase" -- "No" --> "CaptureFailures"["See: Capture Failures"]
    "CapturePhase" -- "Yes" --> "ReplayPhase"{"Does Replay produce correct results?"}
    
    "ReplayPhase" -- "No" --> "NumericalErrors"["See: Numerical Errors"]
    "ReplayPhase" -- "Yes" --> "PerfCheck"{"Is performance improved?"}
    
    "PerfCheck" -- "No" --> "PerfIssues"["See: Performance Issues"]
    "PerfCheck" -- "Yes" --> "Success"["Success!"]

    style "FixEager" stroke-width:2px
```
Sources: [docs/troubleshooting/debugging-strategies.md:17-64]()

---

