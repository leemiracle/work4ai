> 来源: [https://deepwiki.com/deepseek-ai/TileKernels/2-core-architecture%3A-tilelang-kernel-framework](https://deepwiki.com/deepseek-ai/TileKernels/2-core-architecture%3A-tilelang-kernel-framework)
> DeepWiki deepseek-ai/TileKernels

# Core Architecture: TileLang Kernel Framework

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/README.md?plain=1)
 - [tile_kernels/config.py](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/config.py)
 - [tile_kernels/engram/engram_gate_kernel.py](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/engram/engram_gate_kernel.py)
 
  This page provides a high-level overview of the architecture and development patterns used in the TileKernels library. TileKernels leverages **TileLang**, a domain-specific language (DSL) that allows developers to write high-performance GPU kernels directly in Python while maintaining fine-grained control over hardware resources like shared memory, asynchronous copies, and warp-level primitives.

 
## Kernel Authoring and JIT Compilation

 Kernels in TileKernels are defined using the `@tilelang.jit` decorator pattern. This decorator transforms a Python function containing TileLang syntax into a Just-In-Time (JIT) compiled GPU kernel. The framework typically separates the kernel definition into two parts: a "generator" function (decorated with `@tilelang.jit`) and the internal hardware-aware logic (decorated with `T.prim_func`).

 
### The @tilelang.jit Decorator

 The decorator often includes `pass_configs` to tune the compilation process, such as disabling specific thread synchronizations or warp specializations to maximize performance [tile_kernels/engram/engram_gate_kernel.py11-16](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/engram/engram_gate_kernel.py#L11-L16)

 
### T.prim_func and T.Kernel

 The core logic resides within a `T.prim_func`. Inside this function, `T.Kernel` defines the launch grid. TileKernels frequently uses a **Persistent-Block Scheduling** pattern where the number of blocks is decoupled from the total workload size to improve cache locality and SM occupancy [tile_kernels/engram/engram_gate_kernel.py58-70](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/engram/engram_gate_kernel.py#L58-L70)

 
### Debugging with TK_PRINT_KERNEL_SOURCE

 For developers needing to inspect the generated CUDA/Triton-like source code, the library supports a debug flag (conceptually referred to as `TK_PRINT_KERNEL_SOURCE` in documentation, though often implemented via TileLang's internal logging) to output the final kernel source during the JIT process.

 
## Architectural Components

 The framework is built on several pillars that ensure kernels reach near-peak hardware performance:

 
### 1. Persistent-Block Scheduling

 Instead of launching one block per data tile, many kernels (like the Engram Gate) calculate a fixed number of `num_persistent_blocks` based on the available Streaming Multiprocessors (SMs) on the device [tile_kernels/engram/engram_gate_kernel.py41-49](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/engram/engram_gate_kernel.py#L41-L49) These blocks then loop over the total workload using `T.Serial` loops [tile_kernels/engram/engram_gate_kernel.py86-90](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/engram/engram_gate_kernel.py#L86-L90)

 
### 2. Manual Memory Hierarchy Management

 Kernels explicitly manage the transition of data between global memory, shared memory (`T.alloc_shared`), and registers (`T.alloc_local`) [tile_kernels/engram/engram_gate_kernel.py72-84](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/engram/engram_gate_kernel.py#L72-L84)

 
### 3. Asynchronous Pipelining

 To hide memory latency, kernels utilize `T.async_copy` (mapping to CUDA `cp.async`) and `T.ptx_wait_group` to overlap data movement with computation [tile_kernels/engram/engram_gate_kernel.py103-105](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/engram/engram_gate_kernel.py#L103-L105)

 
## System Architecture Overview

 The following diagram illustrates how a TileLang kernel is structured and how it interacts with the hardware configuration.

 **TileLang Kernel Composition**

 
```

```

 
## Data Flow: From Host to Device Execution

 This diagram shows the relationship between the configuration utilities and the kernel execution lifecycle.

 **Execution and Dispatch Flow**

 
```

```

 
## Subsystem Guides

 The framework's functionality is detailed in the following child pages:

 
### [Kernel Authoring Patterns](https://deepwiki.com/deepseek-ai/TileKernels/2.1-kernel-authoring-patterns)

 Covers the specific TileLang primitives used across the repository, including `T.async_copy`, `T.ptx_wait_group` for double-buffering, and `T.warp_reduce_sum` for efficient intra-warp reductions. For details, see [Kernel Authoring Patterns](https://deepwiki.com/deepseek-ai/TileKernels/2.1-kernel-authoring-patterns).

 
### [Device Configuration and SM Management](https://deepwiki.com/deepseek-ai/TileKernels/2.2-device-configuration-and-sm-management)

 Documents the `tile_kernels/config.py` module. This sub-system is responsible for querying GPU properties (like SM count and max shared memory) to dynamically size kernel grids and tiles. For details, see [Device Configuration and SM Management](https://deepwiki.com/deepseek-ai/TileKernels/2.2-device-configuration-and-sm-management).

 
### [Utility Helpers](https://deepwiki.com/deepseek-ai/TileKernels/2.3-utility-helpers)

 Details the mathematical and alignment utilities in `tile_kernels/utils.py` (such as `ceil_div` and `align`) that are used to calculate buffer sizes and loop bounds. For details, see [Utility Helpers](https://deepwiki.com/deepseek-ai/TileKernels/2.3-utility-helpers).

 
---

 **Sources:**

 
 - [README.md1-24](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/README.md?plain=1#L1-L24)
 - [tile_kernels/config.py1-30](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/config.py#L1-L30)
 - [tile_kernels/engram/engram_gate_kernel.py11-153](https://github.com/deepseek-ai/TileKernels/blob/36d9e45d/tile_kernels/engram/engram_gate_kernel.py#L11-L153)
