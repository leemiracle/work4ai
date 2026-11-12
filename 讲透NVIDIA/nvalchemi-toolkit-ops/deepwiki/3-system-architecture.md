<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvalchemi-toolkit-ops · page 3 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/userguide/about/faq.md](docs/userguide/about/faq.md)
- [docs/userguide/about/intro.md](docs/userguide/about/intro.md)

</details>



This page describes the internal architecture of NVIDIA ALCHEMI Toolkit-Ops, focusing on how the three computational primitives integrate with NVIDIA Warp for GPU acceleration, PyTorch for tensor operations, and the batch processing system. For details on the computational primitives themselves, see [Core Components](#2). For performance characteristics, see [Performance and Benchmarks](#4).

## Architectural Overview

NVIDIA ALCHEMI Toolkit-Ops follows a three-layer architecture: a high-level Python API layer, a GPU acceleration layer built on NVIDIA Warp, and a PyTorch compatibility layer that provides tensor operations and automatic differentiation.

```mermaid
graph TB
    subgraph "Layer 1: User API"
        NL_API["neighbor_list()<br/>(nvalchemiops.neighborlist)"]
        D3_API["dftd3()<br/>(nvalchemiops.interactions.dispersion)"]
        EWALD_API["ewald_summation()<br/>(nvalchemiops.interactions.electrostatics)"]
        PME_API["particle_mesh_ewald()<br/>(nvalchemiops.interactions.electrostatics)"]
    end
    
    subgraph "Layer 2: Algorithm Dispatch"
        NL_CELL["cell_list()"]
        NL_NAIVE["naive_neighbor_list()"]
        NL_BCELL["batch_cell_list()"]
        NL_BNAIVE["batch_naive_neighbor_list()"]
        
        D3_SINGLE["Single-system D3"]
        D3_BATCH["Batched D3"]
        
        EWALD_CORE["Ewald core"]
        PME_CORE["PME core"]
    end
    
    subgraph "Layer 3: Warp Kernel Layer"
        WARP_NL["Neighbor list kernels<br/>(@wp.kernel decorators)"]
        WARP_D3["D3 force kernels<br/>(4-pass computation)"]
        WARP_EWALD["Ewald/PME kernels<br/>(real/reciprocal space)"]
    end
    
    subgraph "Layer 4: PyTorch Integration"
        TENSOR["torch.Tensor interface"]
        AUTOGRAD["torch.autograd integration"]
        COMPILE["torch.compile support"]
    end
    
    subgraph "Hardware Execution"
        GPU["CUDA GPU execution"]
        CPU["CPU fallback"]
    end
    
    NL_API --> NL_CELL
    NL_API --> NL_NAIVE
    NL_API --> NL_BCELL
    NL_API --> NL_BNAIVE
    
    D3_API --> D3_SINGLE
    D3_API --> D3_BATCH
    
    EWALD_API --> EWALD_CORE
    PME_API --> PME_CORE
    
    NL_CELL --> WARP_NL
    NL_NAIVE --> WARP_NL
    NL_BCELL --> WARP_NL
    NL_BNAIVE --> WARP_NL
    
    D3_SINGLE --> WARP_D3
    D3_BATCH --> WARP_D3
    
    EWALD_CORE --> WARP_EWALD
    PME_CORE --> WARP_EWALD
    
    WARP_NL --> GPU
    WARP_NL --> CPU
    WARP_D3 --> GPU
    WARP_D3 --> CPU
    WARP_EWALD --> GPU
    WARP_EWALD --> CPU
    
    TENSOR -.->|"wraps all inputs/outputs"| NL_API
    TENSOR -.->|"wraps all inputs/outputs"| D3_API
    TENSOR -.->|"wraps all inputs/outputs"| EWALD_API
    TENSOR -.->|"wraps all inputs/outputs"| PME_API
    
    AUTOGRAD -.->|"gradient tracking"| D3_API
    AUTOGRAD -.->|"gradient tracking"| EWALD_API
    
    COMPILE -.->|"JIT optimization"| NL_CELL
    COMPILE -.->|"JIT optimization"| D3_SINGLE
```

**Sources:** [README.md:10-44](), [docs/userguide/about/intro.md:44-54]()

The architecture separates concerns into distinct layers:

| Layer | Responsibility | Key Technologies |
|-------|---------------|------------------|
| **User API** | Unified interface with automatic algorithm selection | Python functions |
| **Algorithm Dispatch** | Route to appropriate implementation based on system size and batching | Conditional logic |
| **Warp Kernels** | GPU-accelerated computation primitives | NVIDIA Warp `@wp.kernel` decorators |
| **PyTorch Integration** | Tensor operations, autograd, JIT compilation | PyTorch tensors and operators |
| **Hardware** | Execution on CUDA GPUs or CPU fallback | CUDA runtime |

**Sources:** [README.md:10-14](), [docs/userguide/about/intro.md:44-54]()

## NVIDIA Warp Backend

All computational primitives are implemented as NVIDIA Warp kernels. Warp provides a Python-embedded DSL for writing GPU kernels that compile to optimized CUDA code or CPU SIMD instructions.

```mermaid
graph TB
    subgraph "Python API Layer"
        PY_FUNC["Python function<br/>(e.g., cell_list)"]
    end
    
    subgraph "Warp Kernel Definition"
        KERNEL_DEF["@wp.kernel decorator<br/>Type annotations<br/>Launch configuration"]
        
        KERNEL_IMPL["Kernel implementation<br/>wp.tid() indexing<br/>Atomic operations<br/>Shared memory"]
    end
    
    subgraph "Warp Compilation"
        JIT["JIT compilation<br/>Per-device caching"]
        CUDA["CUDA PTX generation"]
        CPU_CODE["CPU SIMD code"]
    end
    
    subgraph "Execution"
        LAUNCH["wp.launch()<br/>Grid/block dimensions<br/>Stream management"]
        
        GPU_EXEC["GPU execution<br/>Parallel threads"]
        CPU_EXEC["CPU execution<br/>Vectorized"]
    end
    
    subgraph "Memory Management"
        WARP_ARRAY["wp.array allocation<br/>Device memory"]
        TENSOR_WRAP["PyTorch tensor wrapping<br/>Zero-copy interop"]
    end
    
    PY_FUNC --> KERNEL_DEF
    KERNEL_DEF --> KERNEL_IMPL
    
    KERNEL_IMPL --> JIT
    JIT --> CUDA
    JIT --> CPU_CODE
    
    CUDA --> LAUNCH
    CPU_CODE --> LAUNCH
    
    LAUNCH --> GPU_EXEC
    LAUNCH --> CPU_EXEC
    
    PY_FUNC -.->|"allocates"| WARP_ARRAY
    WARP_ARRAY -.->|"wraps"| TENSOR_WRAP
```

**Sources:** [README.md:12-14](), [docs/userguide/about/faq.md:16-23]()

### Kernel Organization

Warp kernels follow a consistent pattern across all computational primitives:

1. **Type-annotated kernel functions** - Each kernel uses Warp's type system (`wp.int32`, `wp.float32`, `wp.vec3`, etc.) for static compilation
2. **Thread indexing** - `wp.tid()` retrieves the global thread index for parallel execution
3. **Atomic operations** - Neighbor counting and force accumulation use `wp.atomic_add()` for thread-safe updates
4. **Launch configuration** - Python wrappers call `wp.launch()` with grid dimensions matching problem size

**Sources:** [README.md:12-14]()

### Memory Layout

Warp kernels operate on `wp.array` objects that map directly to PyTorch tensors:

- **Positions**: Shape `[num_atoms, 3]`, contiguous layout for coalesced memory access
- **Neighbor matrices**: Shape `[num_atoms, max_neighbors]` for dense format
- **Cell lists**: Spatial decomposition with hash-based lookups
- **Batch indices**: Shape `[num_atoms]` for heterogeneous batch processing

**Sources:** [README.md:55-90]()

### Hardware Requirements

The Warp backend supports:

| Platform | Requirements |
|----------|-------------|
| **NVIDIA GPU** | CUDA Compute Capability 8.0+ (A100, H100, etc.) |
| **CPU** | x86_64 or ARM64 (including Apple Silicon) |
| **CUDA Version** | 12.0+ recommended for optimal performance |
| **Driver** | 570.xx or newer |

**Sources:** [docs/userguide/about/faq.md:16-23]()

## PyTorch Compatibility Layer

All inputs and outputs use PyTorch tensors, providing seamless integration with ML workflows and automatic differentiation.

```mermaid
graph TB
    subgraph "Input Processing"
        TORCH_IN["PyTorch tensors<br/>(positions, atomic_numbers, etc.)"]
        DEVICE_CHECK["Device detection<br/>torch.device"]
        DTYPE_CHECK["Dtype validation<br/>torch.float32/float64"]
    end
    
    subgraph "Tensor Conversion"
        TO_WARP["Convert to wp.array<br/>Zero-copy when possible"]
        FROM_WARP["Convert from wp.array<br/>Wrap with torch.Tensor"]
    end
    
    subgraph "Computation"
        WARP_KERNEL["Warp kernel execution<br/>GPU/CPU dispatch"]
    end
    
    subgraph "Autograd Integration"
        FORWARD["Forward pass<br/>Save tensors for backward"]
        BACKWARD["Backward pass<br/>torch.autograd.Function"]
        GRAD["Gradient computation<br/>Chain rule application"]
    end
    
    subgraph "torch.compile Support"
        CUSTOM_OP["torch.library.custom_op<br/>Registration"]
        FAKE_IMPL["Abstract implementation<br/>Shape/dtype inference"]
        JIT_COMPILE["JIT compilation<br/>Graph optimization"]
    end
    
    subgraph "Output"
        TORCH_OUT["PyTorch tensors<br/>(energies, forces, etc.)"]
        GRAD_OUT["Gradient tensors<br/>(if requires_grad=True)"]
    end
    
    TORCH_IN --> DEVICE_CHECK
    TORCH_IN --> DTYPE_CHECK
    DEVICE_CHECK --> TO_WARP
    DTYPE_CHECK --> TO_WARP
    
    TO_WARP --> WARP_KERNEL
    WARP_KERNEL --> FROM_WARP
    
    FROM_WARP --> FORWARD
    FORWARD --> TORCH_OUT
    
    TORCH_OUT -.->|"backward()"| BACKWARD
    BACKWARD --> GRAD
    GRAD --> GRAD_OUT
    
    FORWARD -.->|"registered with"| CUSTOM_OP
    CUSTOM_OP --> FAKE_IMPL
    FAKE_IMPL --> JIT_COMPILE
```

**Sources:** [README.md:55-90](), [docs/userguide/about/intro.md:357-376]()

### Tensor Interface

The PyTorch compatibility layer handles:

- **Automatic device placement**: Kernels execute on the same device as input tensors (CUDA or CPU)
- **Dtype support**: Both `torch.float32` and `torch.float64` supported
- **Zero-copy conversion**: Warp arrays wrap PyTorch tensor memory when layouts match
- **Contiguity handling**: Non-contiguous tensors are copied to contiguous buffers before kernel launch

**Sources:** [docs/userguide/about/intro.md:357-364]()

### Automatic Differentiation

Select operations support automatic differentiation via `torch.autograd.Function`:

- **Forward pass**: Computation proceeds through Warp kernels, saving necessary tensors
- **Backward pass**: Custom gradient implementations compute derivatives with respect to inputs
- **Gradient tracking**: Output tensors maintain `requires_grad=True` when inputs require gradients

The DFT-D3 and electrostatics functions support full gradient computation for forces and energies.

**Sources:** [docs/userguide/about/intro.md:357-364]()

### torch.compile Integration

Selected kernels register with `torch.compile` for JIT optimization:

```mermaid
graph LR
    PYTHON["Python code<br/>with torch.compile"]
    
    TRACE["Trace execution<br/>Build computation graph"]
    
    DETECT["Detect custom ops<br/>torch.library.custom_op"]
    
    ABSTRACT["Run abstract impl<br/>Infer output shapes"]
    
    OPTIMIZE["Graph optimization<br/>Fusion, constant folding"]
    
    EXECUTE["Execute optimized graph<br/>with Warp kernels"]
    
    PYTHON --> TRACE
    TRACE --> DETECT
    DETECT --> ABSTRACT
    ABSTRACT --> OPTIMIZE
    OPTIMIZE --> EXECUTE
```

**Sources:** [docs/userguide/about/faq.md:60-74](), [docs/userguide/about/intro.md:357-364]()

For `torch.compile` compatibility:

- Output tensors must be pre-allocated with known shapes
- Custom operators register abstract implementations for shape inference
- Graph breaks are avoided by using tensor operations instead of Python control flow

**Sources:** [docs/userguide/about/faq.md:60-74]()

## Batch Processing Architecture

The toolkit provides native support for processing multiple systems simultaneously with heterogeneous parameters.

```mermaid
graph TB
    subgraph "Batch Input"
        POS["positions<br/>[total_atoms, 3]"]
        NUMS["atomic_numbers<br/>[total_atoms]"]
        BIDX["batch_idx<br/>[total_atoms]"]
        BPTR["batch_ptr<br/>[num_systems + 1]"]
        CELL["cell<br/>[num_systems, 3, 3]"]
        PBC["pbc<br/>[num_systems, 3]"]
    end
    
    subgraph "Batch Processing Strategy"
        DISPATCH["Dispatch logic"]
        
        DISPATCH --> SINGLE_PASS["Single-pass kernels<br/>(batch-aware indexing)"]
        DISPATCH --> MULTI_PASS["Multi-pass kernels<br/>(per-system iteration)"]
        
        SINGLE_PASS --> KERNEL_BATCH["Parallel processing<br/>across all atoms"]
        
        MULTI_PASS --> KERNEL_LOOP["Sequential per-system<br/>+ parallel per-atom"]
    end
    
    subgraph "Batch Indexing"
        BIDX_USE["batch_idx lookup<br/>Map atom to system"]
        BPTR_USE["batch_ptr slicing<br/>System atom ranges"]
        
        BIDX_USE --> SYS_PARAM["System-specific params<br/>(cell, pbc, etc.)"]
    end
    
    subgraph "Output Aggregation"
        ATOM_OUT["Per-atom outputs<br/>[total_atoms, ...]"]
        SYS_OUT["Per-system outputs<br/>[num_systems, ...]"]
        
        ATOM_OUT -.->|"scatter/gather"| SYS_OUT
    end
    
    POS --> KERNEL_BATCH
    POS --> KERNEL_LOOP
    NUMS --> KERNEL_BATCH
    NUMS --> KERNEL_LOOP
    
    BIDX --> BIDX_USE
    BPTR --> BPTR_USE
    
    CELL --> SYS_PARAM
    PBC --> SYS_PARAM
    
    SYS_PARAM --> KERNEL_BATCH
    SYS_PARAM --> KERNEL_LOOP
    
    KERNEL_BATCH --> ATOM_OUT
    KERNEL_LOOP --> ATOM_OUT
    
    ATOM_OUT --> SYS_OUT
```

**Sources:** [README.md:95-138](), [docs/userguide/about/intro.md:236-253]()

### Batch Indexing Scheme

Batched operations use two indexing tensors:

1. **`batch_idx`**: Shape `[total_atoms]`, maps each atom to its system index
2. **`batch_ptr`**: Shape `[num_systems + 1]`, CSR-style pointers defining atom ranges per system

For example, with 3 systems containing 5, 3, and 4 atoms:
- `batch_idx = [0, 0, 0, 0, 0, 1, 1, 1, 2, 2, 2, 2]`
- `batch_ptr = [0, 5, 8, 12]`
- System 0 atoms: `positions[0:5]`
- System 1 atoms: `positions[5:8]`
- System 2 atoms: `positions[8:12]`

**Sources:** [README.md:111-120]()

### Heterogeneous Parameters

Each system in a batch can have:
- Different cell parameters (`cell` has shape `[num_systems, 3, 3]`)
- Different periodicity (`pbc` has shape `[num_systems, 3]`)
- Different atomic compositions (via concatenated `positions` and `atomic_numbers`)

Kernels index into per-system parameters using the atom's `batch_idx` value:

```python
system_id = batch_idx[atom_idx]
atom_cell = cell[system_id]
atom_pbc = pbc[system_id]
```

**Sources:** [README.md:95-138](), [docs/userguide/about/intro.md:229-253]()

### Batch Algorithm Selection

The unified `neighbor_list()` API automatically selects batched algorithms:

| Condition | Algorithm | Complexity |
|-----------|-----------|------------|
| `batch_idx` provided + system size < 5000 atoms | `batch_naive_neighbor_list()` | O(N²) per system |
| `batch_idx` provided + system size ≥ 5000 atoms | `batch_cell_list()` | O(N) per system |
| No `batch_idx` + system size < 5000 atoms | `naive_neighbor_list()` | O(N²) single system |
| No `batch_idx` + system size ≥ 5000 atoms | `cell_list()` | O(N) single system |

**Sources:** [docs/userguide/about/intro.md:58-149]()

## Data Flow Through the System

The following diagram illustrates how data flows through a typical batched DFT-D3 calculation:

```mermaid
graph TB
    subgraph "1. Input Preparation"
        INPUT["User provides:<br/>positions, atomic_numbers<br/>cell, pbc, batch_idx"]
    end
    
    subgraph "2. Neighbor List Construction"
        NL_DISPATCH["neighbor_list() dispatch<br/>Selects batch_cell_list()"]
        NL_BUILD["Build spatial cells<br/>per system"]
        NL_QUERY["Query neighbors<br/>within cutoff"]
        NL_OUT["Output:<br/>neighbor_list [2, num_edges]<br/>neighbor_ptr [total_atoms + 1]<br/>shifts [num_edges, 3]"]
    end
    
    subgraph "3. DFT-D3 Computation"
        D3_INIT["dftd3() initialization<br/>Load D3Parameters"]
        D3_CN["Pass 1: Coordination numbers<br/>Count weighted neighbors"]
        D3_C6["Pass 2: Interpolate C6<br/>from reference values"]
        D3_ENERGY["Pass 3: Compute energies<br/>C6/r⁶ + C8/r⁸ terms"]
        D3_FORCE["Pass 4: Compute forces<br/>Multi-body chain rule"]
    end
    
    subgraph "4. Output Aggregation"
        AGG["Aggregate by system:<br/>Energy: scatter_add by batch_idx<br/>Forces: per-atom [total_atoms, 3]"]
        RETURN["Return:<br/>energies [num_systems]<br/>forces [total_atoms, 3]<br/>coord_nums [total_atoms]<br/>virials [num_systems, 3, 3]"]
    end
    
    INPUT --> NL_DISPATCH
    NL_DISPATCH --> NL_BUILD
    NL_BUILD --> NL_QUERY
    NL_QUERY --> NL_OUT
    
    NL_OUT --> D3_INIT
    D3_INIT --> D3_CN
    D3_CN --> D3_C6
    D3_C6 --> D3_ENERGY
    D3_ENERGY --> D3_FORCE
    
    D3_FORCE --> AGG
    AGG --> RETURN
```

**Sources:** [README.md:95-138](), [docs/userguide/about/intro.md:177-253]()

Key data transformations:

1. **Neighbor list stage**: Converts 3D positions to graph connectivity (edge list or dense matrix)
2. **Coordination calculation**: Aggregates neighbor information per atom
3. **C6 interpolation**: Maps coordination numbers to dispersion coefficients
4. **Force computation**: Differentiates energy with respect to positions using multi-pass kernel
5. **System aggregation**: Sums per-atom energies to per-system totals using `batch_idx`

**Sources:** [README.md:95-138]()

## Integration Points

### External Libraries

The toolkit integrates with:

| Library | Integration Point | Purpose |
|---------|------------------|---------|
| **NVIDIA Warp** | Kernel implementation | GPU acceleration via `@wp.kernel` decorators |
| **PyTorch** | Tensor interface | All inputs/outputs are `torch.Tensor` objects |
| **CUDA** | Runtime execution | Device management, memory allocation, kernel launch |

**Sources:** [README.md:10-14](), [docs/userguide/about/intro.md:355-376]()

### Profiling and Debugging

The architecture supports standard profiling tools:

- **Nsight Systems**: Profile kernel launches and memory transfers
- **Nsight Compute**: Analyze kernel occupancy and memory bandwidth
- **PyTorch Profiler**: Profile Python-level overhead and data movement
- **Warp debugging**: Set `warp.config.mode = "debug"` for kernel assertions

**Sources:** [docs/userguide/about/intro.md:365-370]()

### Future Extensions

The architecture is designed for extensibility:

- New Warp kernels can be added by following existing kernel patterns
- New PyTorch custom operators register via `torch.library.custom_op`
- Batch processing extends naturally to new primitives via `batch_idx` indexing

**Sources:** [README.md:179-194]()

---

