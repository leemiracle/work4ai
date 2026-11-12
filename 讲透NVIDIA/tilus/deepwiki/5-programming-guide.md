<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/tilus · page 5 Programming Guide · fetched 2026-10-26 -->

# Programming Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/matmul/matmul_v0.py](examples/matmul/matmul_v0.py)
- [examples/matmul/matmul_v1.py](examples/matmul/matmul_v1.py)
- [examples/matmul/matmul_v2.py](examples/matmul/matmul_v2.py)
- [examples/matmul/matmul_v3.py](examples/matmul/matmul_v3.py)
- [examples/matmul/matmul_v4.py](examples/matmul/matmul_v4.py)
- [examples/matmul/matmul_v5.py](examples/matmul/matmul_v5.py)

</details>



This document provides practical guidance for implementing high-performance GPU kernels using the Tilus programming framework. It covers the core programming patterns, memory management strategies, optimization techniques, and auto-tuning approaches needed to write efficient GPU code.

For step-by-step tutorials on specific kernel implementations, see [Basic Matrix Multiplication](#5.1), [FlashAttention Implementation](#5.2), [Quantized Computing](#5.3), and [Advanced Kernel Examples](#5.4). For detailed documentation of the underlying systems, see [Script System](#3.1), [Memory Model and Tensor Types](#3.3), and [JIT Compilation and Autotuning](#3.2).

## Core Programming Model

Tilus kernels are implemented by subclassing the `tilus.Script` class and defining two key methods: `__init__` for compile-time hyperparameters and `__call__` for the kernel computation logic. The programming model follows a block-level approach where operations are executed by all threads in a thread block.

**Kernel Structure Pattern**

```mermaid
flowchart TD
    subgraph "tilus.Script Subclass"
        A["__init__()"]
        B["__call__()"]
    end
    
    subgraph "Compilation-time"
        C["Hyperparameters"]
        D["block_m, block_n, block_k"]
        E["num_warps, num_stages"]
    end
    
    subgraph "Runtime Parameters"
        F["Tensor Pointers"]
        G["Dimension Sizes"]
        H["Runtime Scalars"]
    end
    
    subgraph "Kernel Body"
        I["attrs.blocks = [...]"]
        J["attrs.warps = ..."]
        K["Memory Allocation"]
        L["Computation Loop"]
        M["Result Storage"]
    end
    
    A --> C
    C --> D
    C --> E
    B --> F
    B --> G
    B --> H
    B --> I
    I --> J
    J --> K
    K --> L
    L --> M
    
    style A fill:#f9f9f9
    style B fill:#f9f9f9
    style I fill:#e8f5e8
    style J fill:#e8f5e8
```

The `__init__` method processes compile-time known hyperparameters like tile sizes and thread configurations, while `__call__` defines the actual computation using runtime parameters. The kernel execution configuration is set via `attrs.blocks` and `attrs.warps` attributes.

Sources: [examples/matmul/matmul_v0.py:24-36](), [examples/matmul/matmul_v0.py:48-70]()

## Memory Hierarchy and Tensor Management

Tilus provides explicit control over the GPU memory hierarchy through distinct tensor types. The memory model mirrors the hardware architecture with three main memory domains: global memory (large, high latency), shared memory (fast, block-scoped), and register memory (fastest, thread-local).

**Memory Operations and Data Flow**

```mermaid
flowchart LR
    subgraph "Global Memory"
        A["global_view()"]
        B["load_global()"]
        C["store_global()"]
    end
    
    subgraph "Shared Memory"
        D["shared_tensor()"]
        E["load_shared()"]
        F["store_shared()"]
        G["free_shared()"]
    end
    
    subgraph "Register Memory"
        H["register_tensor()"]
        I["Computation"]
        J["cast()"]
    end
    
    subgraph "Async Operations"
        K["copy_async()"]
        L["copy_async_wait_all()"]
        M["copy_async_commit_group()"]
    end
    
    A --> B
    B --> H
    D --> E
    E --> H
    H --> I
    I --> J
    J --> F
    F --> D
    H --> C
    A --> K
    K --> D
    K --> L
    L --> M
    
    style H fill:#e8f5e8
    style I fill:#f3e5f5
    style K fill:#fff3e0
```

The typical data flow involves loading data from global memory into shared memory buffers, then loading into registers for computation. Results are stored back through the hierarchy. Asynchronous copy operations enable overlapping memory transfers with computation for better performance.

Sources: [examples/matmul/matmul_v0.py:77-104](), [examples/matmul/matmul_v1.py:45-89](), [examples/matmul/matmul_v3.py:80-105]()

## Progressive Optimization Patterns

The matrix multiplication examples demonstrate a systematic approach to GPU kernel optimization, with each version introducing new techniques that build upon previous optimizations.

| Version | Optimization Technique | Key Instructions | Performance Impact |
|---------|----------------------|------------------|-------------------|
| v0 | Naive Implementation | `load_global`, `dot`, `store_global` | Baseline |
| v1 | Shared Memory Tiling | `shared_tensor`, `store_shared`, `sync` | Reduced global memory traffic |
| v2 | Auto-tuning | `@tilus.autotune` decorator | Optimal hyperparameter search |
| v3 | Async Copy | `copy_async`, `copy_async_wait_all` | Overlapped memory operations |
| v4 | Software Pipelining | Multi-stage buffers, `copy_async_commit_group` | Computation-memory overlap |
| v5 | Split-K Reduction | `global_tensor`, `lock_semaphore`, `release_semaphore` | Better parallelization |

**Optimization Progression Flow**

```mermaid
flowchart TD
    subgraph "v0: Naive"
        A["Direct global memory access"]
        B["Sequential load-compute-store"]
    end
    
    subgraph "v1: Shared Memory"
        C["shared_tensor allocation"]
        D["Tile-based computation"]
        E["Thread synchronization"]
    end
    
    subgraph "v2: Auto-tuning"
        F["@tilus.autotune decorators"]
        G["Hyperparameter search space"]
        H["Automatic configuration selection"]
    end
    
    subgraph "v3: Async Copy"
        I["copy_async operations"]
        J["Hardware async units"]
        K["Reduced register pressure"]
    end
    
    subgraph "v4: Software Pipelining"
        L["Multi-stage shared buffers"]
        M["Overlapped load-compute"]
        N["Pipeline unrolling"]
    end
    
    subgraph "v5: Split-K"
        O["3D thread block grid"]
        P["Semaphore synchronization"]
        Q["Partial result aggregation"]
    end
    
    A --> C
    B --> D
    D --> F
    E --> G
    G --> I
    H --> J
    J --> L
    K --> M
    M --> O
    N --> P
    
    style F fill:#e8f5e8
    style I fill:#fff3e0
    style L fill:#f3e5f5
    style O fill:#e1f5fe
```

Each optimization targets specific performance bottlenecks: memory bandwidth, latency hiding, parameter tuning, and parallelization efficiency.

Sources: [examples/matmul/matmul_v0.py:48-104](), [examples/matmul/matmul_v1.py:45-89](), [examples/matmul/matmul_v2.py:54-122](), [examples/matmul/matmul_v3.py:84-105](), [examples/matmul/matmul_v4.py:89-131](), [examples/matmul/matmul_v5.py:84-187]()

## Auto-tuning and Performance Optimization

The `@tilus.autotune` decorator enables automatic hyperparameter optimization by defining search spaces for kernel configurations. The system compiles and benchmarks all configurations to select the optimal parameters for given input sizes and hardware targets.

**Auto-tuning Configuration**

```mermaid
flowchart TD
    subgraph "Search Space Definition"
        A["@tilus.autotune('num_warps', [4, 8])"]
        B["@tilus.autotune('block_m, block_n', [(128,128), (64,128)])"]
        C["@tilus.autotune('block_k', [16, 32])"]
    end
    
    subgraph "Compilation Process"
        D["Generate all combinations"]
        E["Compile each configuration"]
        F["Create cached variants"]
    end
    
    subgraph "Runtime Selection"
        G["Benchmark all variants"]
        H["Measure performance"]
        I["Cache best configuration"]
        J["Use optimal kernel"]
    end
    
    A --> D
    B --> D
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    I --> J
    
    style D fill:#e8f5e8
    style G fill:#f3e5f5
    style I fill:#fff3e0
```

The auto-tuning process occurs transparently during the first kernel invocation. Subsequent calls use the cached optimal configuration, eliminating tuning overhead in production workloads.

**Common Auto-tuning Parameters**

| Parameter | Purpose | Typical Values | Impact |
|-----------|---------|----------------|---------|
| `num_warps` | Thread block size | 1, 2, 4, 8, 16 | Resource utilization |
| `block_m`, `block_n` | Output tile dimensions | 32-256 | Memory coalescing |
| `block_k` | Reduction dimension tile | 8-64 | Register pressure |
| `num_stages` | Pipeline depth | 2-8 | Latency hiding |
| `split_k_factor` | K-dimension splitting | 1, 4, 8, 16 | Parallelism |

Sources: [examples/matmul/matmul_v2.py:54-56](), [examples/matmul/matmul_v4.py:51-54](), [examples/matmul/matmul_v5.py:53-57]()

## Advanced Synchronization and Communication

Complex kernels require sophisticated synchronization patterns for coordinating thread blocks and managing shared resources. Tilus provides hardware-accelerated primitives for efficient inter-block communication.

**Synchronization Primitives**

| Instruction | Scope | Purpose | Usage Pattern |
|-------------|-------|---------|---------------|
| `sync()` | Thread block | Barrier synchronization | Memory consistency |
| `lock_semaphore()` | Global | Acquire exclusive access | Inter-block coordination |
| `release_semaphore()` | Global | Release exclusive access | Resource management |
| `copy_async_wait_group()` | Thread block | Wait for async operations | Pipeline synchronization |

**Split-K Synchronization Pattern**

The split-K optimization in `MatmulV5` demonstrates advanced inter-block coordination using semaphores. Multiple thread blocks compute partial results for the same output tile, then use semaphores to serialize the aggregation process.

```mermaid
sequenceDiagram
    participant TB0 as "Thread Block 0"
    participant TB1 as "Thread Block 1"
    participant TB2 as "Thread Block 2"
    participant SEM as "Semaphore"
    participant GM as "Global Memory"
    
    TB0->>GM: Store partial result
    TB0->>SEM: Release (value=1)
    
    TB1->>SEM: Lock (value=1)
    TB1->>GM: Load + accumulate
    TB1->>GM: Store accumulated result
    TB1->>SEM: Release (value=2)
    
    TB2->>SEM: Lock (value=2)
    TB2->>GM: Load + accumulate
    TB2->>GM: Store final result
    TB2->>SEM: Release (value=0)
```

This pattern ensures correct aggregation order while maintaining high parallelism for the compute-intensive portion of the kernel.

Sources: [examples/matmul/matmul_v5.py:163-186](), [examples/matmul/matmul_v4.py:95-124]()

## Type System and Kernel Interfaces

Tilus uses a specialized type system to distinguish between compile-time and runtime parameters, enabling efficient code generation and optimization.

**Parameter Type Annotations**

| Type | Description | JIT Behavior | Usage |
|------|-------------|--------------|-------|
| `int` | Compile-time integer | Triggers recompilation | Tile sizes, constants |
| `int32` | Runtime 32-bit integer | Runtime parameter | Dynamic dimensions |
| `~float16` | Pointer to float16 data | Runtime parameter | Tensor pointers |
| `float16`, `float32` | Scalar data types | Type inference | Tensor element types |

The type system enables the JIT compiler to specialize kernels for specific parameter combinations while maintaining flexibility for runtime inputs. Compile-time parameters become constants in the generated code, enabling aggressive optimization.

Sources: [examples/matmul/matmul_v0.py:59-64](), [examples/matmul/matmul_v0.py:108-114]()

---

