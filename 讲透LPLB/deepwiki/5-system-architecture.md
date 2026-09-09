> 来源: [https://deepwiki.com/deepseek-ai/LPLB/5-system-architecture](https://deepwiki.com/deepseek-ai/LPLB/5-system-architecture)
> DeepWiki deepseek-ai/LPLB

# System Architecture

  Relevant source files 
 - [csrc/plugin.cpp](https://github.com/deepseek-ai/LPLB/blob/0490f794/csrc/plugin.cpp)
 - [lplb/planner.py](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/planner.py)
 - [lplb/resources/csrc-tmpl/minilp.cu](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/resources/csrc-tmpl/minilp.cu)
 
  
## Purpose and Scope

 This document provides a comprehensive overview of LPLB's internal architecture, explaining how the system's components are organized, how they interact, and how data flows through the pipeline. The architecture is designed as a three-layer system: a Python API layer for user interaction, a C++ compilation layer for dynamic kernel generation, and a CUDA execution layer for GPU-optimized computation.

 For information about using the LPLB API, see [API Reference](https://deepwiki.com/deepseek-ai/LPLB/4-api-reference). For details on building and compiling the system, see [Build System](https://deepwiki.com/deepseek-ai/LPLB/6-build-system). For advanced usage patterns, see [Advanced Topics](https://deepwiki.com/deepseek-ai/LPLB/8-advanced-topics).

 
## Architecture Overview

 LPLB implements a **three-layer architecture** that separates concerns between user-facing APIs, compilation infrastructure, and GPU execution:

 
```

```

 **Sources:** [csrc/plugin.cpp122-661](https://github.com/deepseek-ai/LPLB/blob/0490f794/csrc/plugin.cpp#L122-L661) [lplb/planner.py38-267](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/planner.py#L38-L267) [lplb/resources/csrc-tmpl/minilp.cu1-516](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/resources/csrc-tmpl/minilp.cu#L1-L516)

 
### Layer 1: Python API Layer

 The Python layer provides the user-facing API and implements static load balancing. Key components:

 
 - **`Planner` class** ([lplb/planner.py38-267](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/planner.py#L38-L267)): Main orchestrator that coordinates all load balancing operations
 - **`EPLB` module** ([lplb/eplb.py](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/eplb.py)): Static expert rebalancing based on historical workload
 - **`_get_solver()` function** ([lplb/planner.py17-35](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/planner.py#L17-L35)): Factory function that returns cached `CompiledSolver` instances
 
 The Python layer handles tensor management, distributed communication coordination via `torch.distributed`, and maintains the redundancy topology configuration.

 
### Layer 2: C++ Compilation Layer

 The C++ layer bridges Python and CUDA, implementing runtime kernel compilation and caching. The core component is the **`compiled_solver` struct** ([csrc/plugin.cpp122-661](https://github.com/deepseek-ai/LPLB/blob/0490f794/csrc/plugin.cpp#L122-L661)):

 
 - **Compilation** ([csrc/plugin.cpp149-327](https://github.com/deepseek-ai/LPLB/blob/0490f794/csrc/plugin.cpp#L149-L327)): Uses NVRTC to compile specialized CUDA kernels based on topology parameters (`GROUP_SIZE`, `DUP_PER_RANK`)
 - **Caching** ([csrc/plugin.cpp207-326](https://github.com/deepseek-ai/LPLB/blob/0490f794/csrc/plugin.cpp#L207-L326)): Hash-based disk cache in `~/.lplb/cache/` to avoid recompilation
 - **Module Loading** ([csrc/plugin.cpp329-352](https://github.com/deepseek-ai/LPLB/blob/0490f794/csrc/plugin.cpp#L329-L352)): Loads compiled kernels and extracts function pointers
 - **Communication Setup** ([csrc/plugin.cpp357-457](https://github.com/deepseek-ai/LPLB/blob/0490f794/csrc/plugin.cpp#L357-L457)): Initializes NVSHMEM and CUDA IPC when available
 
 This layer is exposed to Python via **pybind11** ([csrc/plugin.cpp663-679](https://github.com/deepseek-ai/LPLB/blob/0490f794/csrc/plugin.cpp#L663-L679)) as the `lplb._cpp.CompiledSolver` class.

 
### Layer 3: CUDA Execution Layer

 The CUDA layer implements the core algorithms as three specialized kernels:

 
 - **`kernel_solve`** ([lplb/resources/csrc-tmpl/minilp.cu83-402](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/resources/csrc-tmpl/minilp.cu#L83-L402)): Implements the 5-iteration Interior Point Method for LP optimization
 - **`kernel_count_idx`** ([lplb/resources/csrc-tmpl/minilp.cu410-443](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/resources/csrc-tmpl/minilp.cu#L410-L443)): Counts workload per SM using shared memory histograms
 - **`kernel_map_idx`** ([lplb/resources/csrc-tmpl/minilp.cu445-515](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/resources/csrc-tmpl/minilp.cu#L445-L515)): Deterministically maps logical to physical expert indices
 
 These kernels use **cuSolverDx** ([lplb/resources/csrc-tmpl/minilp.cu38](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/resources/csrc-tmpl/minilp.cu#L38-L38)) for Cholesky decomposition and **cuBLASDx** ([lplb/resources/csrc-tmpl/minilp.cu42-59](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/resources/csrc-tmpl/minilp.cu#L42-L59)) for matrix operations.

 
## Component Interactions

 The following diagram shows how key classes and functions interact during a typical load balancing operation:

 
```

```

 **Sources:** [lplb/planner.py245-266](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/planner.py#L245-L266) [csrc/plugin.cpp491-660](https://github.com/deepseek-ai/LPLB/blob/0490f794/csrc/plugin.cpp#L491-L660)

 
## Data Structures and Memory Layout

 
### Redundancy Topology Representation

 LPLB represents expert redundancy using two key tensors maintained by the `Planner` class:

 
| Tensor | Shape | Description | Code Reference |
|---|---|---|---|
| r2o (redundant_to_original) | [group_size, num_redundants] | Maps each redundant expert to its original rank | lplb/planner.py66 |
| o2r (original_to_redundant) | [group_size, num_redundants] | Inverse mapping obtained via argsort | lplb/planner.py67 |
| phy2log | [n_routed_experts] | Maps physical expert IDs to logical IDs | lplb/planner.py90 |

 
```

```

 **Sources:** [lplb/planner.py66-91](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/planner.py#L66-L91) [lplb/resources/csrc-tmpl/minilp.cu21-26](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/resources/csrc-tmpl/minilp.cu#L21-L26)

 
### Shared Memory Layout in `kernel_solve`

 The `kernel_solve` kernel uses a large shared memory structure to perform LP optimization:

 
```

```

 **Sources:** [lplb/resources/csrc-tmpl/minilp.cu64-77](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/resources/csrc-tmpl/minilp.cu#L64-L77) [lplb/resources/csrc-tmpl/minilp.cu323-401](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/resources/csrc-tmpl/minilp.cu#L323-L401)

 
## Communication Architecture

 LPLB implements a **three-tier communication hierarchy** to optimize data movement across different hardware boundaries:

 
```

```

 **Sources:** [csrc/plugin.cpp357-457](https://github.com/deepseek-ai/LPLB/blob/0490f794/csrc/plugin.cpp#L357-L457) [lplb/resources/csrc-tmpl/minilp.cu110-177](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/resources/csrc-tmpl/minilp.cu#L110-L177)

 
### Communication Setup in `compiled_solver::init_comm`

 When NVSHMEM is enabled, the `init_comm` method ([csrc/plugin.cpp357-457](https://github.com/deepseek-ai/LPLB/blob/0490f794/csrc/plugin.cpp#L357-L457)) performs the following initialization:

 
 - **NVSHMEM Initialization** ([csrc/plugin.cpp364-385](https://github.com/deepseek-ai/LPLB/blob/0490f794/csrc/plugin.cpp#L364-L385)): Creates symmetric heap and team configuration
 - **Symbol Synchronization** ([csrc/plugin.cpp372-374](https://github.com/deepseek-ai/LPLB/blob/0490f794/csrc/plugin.cpp#L372-L374)): Copies NVSHMEM device state to loaded module
 - **IPC Handle Exchange** ([csrc/plugin.cpp403-438](https://github.com/deepseek-ai/LPLB/blob/0490f794/csrc/plugin.cpp#L403-L438)): Uses `torch.distributed._allgather_base` to exchange CUDA IPC handles
 - **Peer Mapping** ([csrc/plugin.cpp422-438](https://github.com/deepseek-ai/LPLB/blob/0490f794/csrc/plugin.cpp#L422-L438)): Opens remote memory handles for intra-node communication
 
 This enables the **hybrid communication pattern** where:

 
 - Inter-node: NVSHMEM RDMA for low-latency cross-node data transfer
 - Intra-node: CUDA IPC for fast GPU-to-GPU peer access within a node
 
 
## Runtime Compilation Pipeline

 The `compiled_solver::compile_cubin` method ([csrc/plugin.cpp149-327](https://github.com/deepseek-ai/LPLB/blob/0490f794/csrc/plugin.cpp#L149-L327)) implements a sophisticated compilation pipeline:

 
```

```

 **Sources:** [csrc/plugin.cpp149-327](https://github.com/deepseek-ai/LPLB/blob/0490f794/csrc/plugin.cpp#L149-L327)

 
### Specialization Parameters

 The kernel template is compiled with the following parameters specialized at runtime:

 
| Parameter | Description | Source |
|---|---|---|
| GROUP_SIZE | Number of ranks in each redundancy group | csrc/plugin.cpp184 |
| DUP_PER_RANK | Number of redundant experts per rank | csrc/plugin.cpp185 |
| SM_Ver | GPU compute capability (e.g., 900 for H100) | csrc/plugin.cpp186 |
| BLOCK_DIM | Thread block size (fixed at 256) | csrc/plugin.cpp187 |

 These parameters are used as C preprocessor definitions during NVRTC compilation, allowing the kernel to be fully optimized for the specific topology configuration.

 
## Kernel Execution Model

 Each of the three kernels has a distinct execution model optimized for its workload:

 
### `kernel_count_idx` Execution Model

 
```

```

 **Sources:** [lplb/resources/csrc-tmpl/minilp.cu410-443](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/resources/csrc-tmpl/minilp.cu#L410-L443)

 
### `kernel_solve` Execution Model

 The solve kernel uses **cooperative kernel launch** to enable grid-wide synchronization:

 
 - **Workload Aggregation** ([lplb/resources/csrc-tmpl/minilp.cu110-197](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/resources/csrc-tmpl/minilp.cu#L110-L197)): Optionally uses NVSHMEM to aggregate workload across all nodes
 - **Problem Formulation** ([lplb/resources/csrc-tmpl/minilp.cu203-293](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/resources/csrc-tmpl/minilp.cu#L203-L293)): Constructs LP constraint matrix and objective
 - **Iterative Refinement** ([lplb/resources/csrc-tmpl/minilp.cu335-367](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/resources/csrc-tmpl/minilp.cu#L335-L367)): 5 iterations of Interior Point Method
 - **Validation** ([lplb/resources/csrc-tmpl/minilp.cu379-401](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/resources/csrc-tmpl/minilp.cu#L379-L401)): Checks convergence criteria
 
 Detailed information about the LP solver algorithm is available in [Linear Programming Solver](https://deepwiki.com/deepseek-ai/LPLB/5.5-linear-programming-solver).

 
### `kernel_map_idx` Execution Model

 
```

```

 **Sources:** [lplb/resources/csrc-tmpl/minilp.cu445-515](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/resources/csrc-tmpl/minilp.cu#L445-L515)

 The mapping kernel implements **deterministic load distribution** using a multiplicative hash function `(counter * 499 + 41) % total` ([lplb/resources/csrc-tmpl/minilp.cu505](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/resources/csrc-tmpl/minilp.cu#L505-L505)) to ensure reproducible results across runs.

 
## Key Abstractions and Invariants

 
### Problem Size Invariants

 The system maintains strict relationships between problem sizes:

 
```

```

 **Sources:** [lplb/planner.py82-88](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/planner.py#L82-L88) [lplb/resources/csrc-tmpl/minilp.cu61-62](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/resources/csrc-tmpl/minilp.cu#L61-L62)

 
### Expert ID Translation

 LPLB uses three types of expert IDs that must be carefully translated:

 
| ID Type | Range | Description |
|---|---|---|
| Logical | [0, n_logical_routed_experts) | Expert IDs visible to the model, without redundancy |
| Physical | [0, n_routed_experts) | Actual expert IDs including all replicas |
| Local Physical | [0, n_local_routed_experts) | Per-rank physical expert IDs |

 The `phy2log` tensor ([lplb/planner.py90](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/planner.py#L90-L90)) maps physical IDs to logical IDs, enabling the system to determine which logical expert each physical expert replica represents.

 
## Integration with External Systems

 
### PyTorch Integration

 LPLB integrates tightly with PyTorch through:

 
 - **Tensor management**: All inputs/outputs are `torch.Tensor` objects
 - **CUDA stream coordination**: Uses `c10::cuda::getCurrentCUDAStream()` ([csrc/plugin.cpp555](https://github.com/deepseek-ai/LPLB/blob/0490f794/csrc/plugin.cpp#L555-L555))
 - **Device management**: Respects `torch.cuda.current_device()` ([csrc/plugin.cpp151](https://github.com/deepseek-ai/LPLB/blob/0490f794/csrc/plugin.cpp#L151-L151))
 - **ProcessGroup**: Uses `c10d::ProcessGroup` for collective communication ([csrc/plugin.cpp147](https://github.com/deepseek-ai/LPLB/blob/0490f794/csrc/plugin.cpp#L147-L147))
 
 **Sources:** [csrc/plugin.cpp31-33](https://github.com/deepseek-ai/LPLB/blob/0490f794/csrc/plugin.cpp#L31-L33) [lplb/planner.py7](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/planner.py#L7-L7)

 
### Optional DeepEP Integration

 When DeepEP is available, LPLB can use its optimized communication buffers:

 
```

```

 **Sources:** [lplb/planner.py104-113](https://github.com/deepseek-ai/LPLB/blob/0490f794/lplb/planner.py#L104-L113) [csrc/plugin.cpp92-105](https://github.com/deepseek-ai/LPLB/blob/0490f794/csrc/plugin.cpp#L92-L105)

 For detailed information about DeepEP integration, see [DeepEP Integration](https://deepwiki.com/deepseek-ai/LPLB/8.1-deepep-integration).

 
## Summary

 LPLB's architecture achieves high performance through:

 
 - **Compile-time specialization**: Kernels are compiled for specific topology configurations
 - **Efficient caching**: Compiled kernels are cached to avoid repeated compilation
 - **Hierarchical communication**: Three-tier architecture minimizes communication overhead
 - **Cooperative execution**: Grid-wide synchronization enables efficient all-reduce patterns
 - **GPU-optimized algorithms**: Uses cuSolverDx and cuBLASDx for optimal performance
 
 The following subsections provide detailed information about each layer:

 
 - [Architecture Overview](https://deepwiki.com/deepseek-ai/LPLB/5.1-architecture-overview): High-level component diagram and responsibilities
 - [Python Layer Implementation](https://deepwiki.com/deepseek-ai/LPLB/5.2-python-layer-implementation): Details on `Planner` and `EPLB`
 - [C++ Extension and Runtime Compilation](https://deepwiki.com/deepseek-ai/LPLB/5.3-c++-extension-and-runtime-compilation): Deep dive into `CompiledSolver`
 - [CUDA Kernel Implementation](https://deepwiki.com/deepseek-ai/LPLB/5.4-cuda-kernel-implementation): Kernel algorithms and GPU optimizations
 - [Linear Programming Solver](https://deepwiki.com/deepseek-ai/LPLB/5.5-linear-programming-solver): Interior Point Method details
 - [Distributed Communication Architecture](https://deepwiki.com/deepseek-ai/LPLB/5.6-distributed-communication-architecture): Communication patterns and protocols
