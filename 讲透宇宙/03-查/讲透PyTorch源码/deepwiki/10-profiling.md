# Profiling and Observability

> 来源: DeepWiki pytorch/pytorch (Last indexed: 2 September 2026, commit 580b06)

Relevant source files: torch/autograd/{proffiler,profiler_util}.py, torch/csrc/autograd/profiler_kineto.{cpp,h}, torch/csrc/profiler/{collection,kineto_shim}.{cpp,h}, torch/profiler/profiler.py, torch/profiler/_cupti/**, torch/profiler/_chrome_trace_export.py, torch/cuda/{graphs,green_contexts,_graph_annotations}.py 等。

The PyTorch profiling and observability infrastructure provides a multi-layered suite of tools for performance analysis, resource monitoring, and distributed system debugging. This subsystem bridges high-level Python execution with low-level hardware activities across CPUs, GPUs, and other accelerators.

## System Overview

The observability stack is centered around the **Kineto-based profiler**, which integrates with the PyTorch Autograd engine to correlate high-level operators with device-level kernels. This is complemented by specialized observers for execution traces, memory allocation snapshots, and distributed communication debugging.

**Sources:** torch/autograd/profiler.py:113-160, torch/csrc/autograd/profiler_kineto.cpp:109-136, torch/csrc/profiler/kineto_shim.h:1-40, torch/profiler/profiler.py:42-44

---

## Kineto and Autograd Profiling

The primary entry point for performance analysis is the `torch.profiler` API. It leverages the **Kineto** library to capture hardware-level events and the **Autograd Profiler** to track CPU-side operator execution.

- **ProfilerActivity**: Defines the scope of profiling, such as `CPU`, `CUDA`, or `XPU` (torch/autograd/profiler.py:28-32)
- **Kineto Shim**: A translation layer that facilitates communication between PyTorch and the Kineto library, mapping PyTorch's internal `ProfilerState` to Kineto activities (torch/csrc/autograd/profiler_kineto.cpp:79-84)
- **record_function**: A context manager used to annotate blocks of code. It triggers callbacks that the profiler uses to mark start/end timestamps and collect metadata like input shapes and dtypes (torch/csrc/autograd/profiler_kineto.cpp:152-162)
- **Trace Export**: Results are aggregated into an `EventList` (torch/autograd/profiler_util.py:29-50). These can be exported to the Chrome Trace format for visualization (torch/autograd/profiler_util.py:81-83)
- **CUPTI Activity Monitor**: A specialized monitor for low-level NVIDIA GPU activity, supporting advanced record layouts and background flushing via `CuptiMonitor` (torch/profiler/_cupti/monitor.py:136-170)

## Memory Visualization

PyTorch provides deep visibility into memory usage through the `CUDACachingAllocator` and dedicated snapshot tools.

- **Memory Snapshots**: Utilities capture the state of the allocator, including active blocks and segments, serialized for offline analysis using `MemoryProfile`
- **Memory Timeline**: `MemoryProfileTimeline` provides a structured view of memory events over time, including allocations and deallocations
- **Allocation Events**: `KinetoThreadLocalState` implements `reportMemoryUsage` and `reportOutOfMemory` to pipe allocator events into the profiling trace (torch/csrc/autograd/profiler_kineto.cpp:143-175)
- **Private Pools**: Support for visualizing user-created memory pools by tracking pool identifiers in the profiler result (torch/csrc/profiler/collection.cpp:37-71)

## Distributed Debugging and Observability

- **Execution Trace Observer**: Captures the relationship between high-level Python code and low-level kernel launches via `_add_execution_trace_observer` (torch/profiler/profiler.py:19-25)
- **CUDA Graph Annotations**: During CUDA graph capture, `mark_kernels` records the capture frontier and annotates kernel nodes with `toolsId` to match them to profiler trace events (torch/cuda/_graph_annotations.py:1-8)
- **KinetoStepTracker**: Manages the synchronization of profiling steps across distributed ranks, ensuring traces are captured for the same execution window (torch/autograd/profiler.py:54)
- **Pattern Detection**: The profiler allows identifying performance issues such as memory leaks through periodic garbage collection and cache clearing during profiling (test/profiler/test_profiler.py:149-160)

**Sources:** torch/cuda/_graph_annotations.py:1-42, torch/profiler/profiler.py:42-44, torch/autograd/profiler.py:113-190, torch/csrc/profiler/collection.cpp:54-59
