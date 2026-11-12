<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvalchemi-toolkit-ops · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/index.md](docs/index.md)
- [docs/userguide/about/intro.md](docs/userguide/about/intro.md)

</details>



This page provides a high-level introduction to the NVIDIA ALCHEMI Toolkit-Ops codebase, its architectural design, computational primitives, and target use cases. For installation instructions, see [Installation and Setup](#1.1). For hands-on examples, see [Quick Start Guide](#1.2). For detailed documentation of individual components, see [Core Components](#2).

## What is NVIDIA ALCHEMI Toolkit-Ops?

NVIDIA ALCHEMI Toolkit-Ops (`nvalchemiops`) is a GPU-accelerated library providing computational primitives for atomistic simulations, computational chemistry, and machine learning workflows. The toolkit implements high-performance kernels in [NVIDIA Warp](https://github.com/NVIDIA/warp) and exposes them through PyTorch-compatible APIs.

**Key Capabilities:**

| Capability | Description | Scaling |
|-----------|-------------|---------|
| Neighbor list construction | Spatial decomposition with automatic algorithm selection | O(N) cell list or O(N²) naive |
| DFT-D3 dispersion corrections | Becke-Johnson damped dispersion with coordination-dependent C6 | Multi-pass force calculation |
| Electrostatic interactions | Ewald summation and particle mesh Ewald (PME) | O(N²) Ewald or O(N log N) PME |
| Batch processing | Heterogeneous systems with different sizes and parameters | Native batching support |

The toolkit is designed for systems ranging from small molecules (~100 atoms) to large crystalline structures (>100,000 atoms) and supports both single-system and batched operation modes.

**Sources:** [README.md:1-50](), [docs/index.md:1-16](), [docs/userguide/about/intro.md:1-50]()

## System Architecture

The following diagram illustrates the complete system architecture, showing how computational primitives, backend implementations, and hardware platforms relate to each other:

```mermaid
graph TB
    subgraph Core["nvalchemiops (Core Package)"]
        API["High-Level API Layer"]
        
        subgraph Primitives["Computational Primitives"]
            NL["neighborlist module"]
            DISP["interactions.dispersion module"]
            ELEC["interactions.electrostatics module"]
        end
        
        subgraph Implementations["Warp Kernel Implementations"]
            NL_WARP["neighborlist.warp module"]
            DISP_WARP["interactions.dispersion.warp module"]
            ELEC_WARP["interactions.electrostatics.warp module"]
        end
    end
    
    subgraph Backend["Execution Backends"]
        WARP["NVIDIA Warp Runtime"]
        TORCH["PyTorch Tensor Ops"]
    end
    
    subgraph Hardware["Hardware Platforms"]
        GPU["NVIDIA GPUs<br/>(Compute 8.0+)"]
        CPU["CPU Fallback<br/>(x86/ARM)"]
    end
    
    API --> NL
    API --> DISP
    API --> ELEC
    
    NL --> NL_WARP
    DISP --> DISP_WARP
    ELEC --> ELEC_WARP
    
    NL_WARP --> WARP
    DISP_WARP --> WARP
    ELEC_WARP --> WARP
    
    NL -.->|"provides neighbors"| DISP
    NL -.->|"provides neighbors"| ELEC
    
    TORCH -.->|"tensor interface"| API
    
    WARP --> GPU
    WARP --> CPU
```

**Architecture Layers:**

1. **High-Level API Layer**: User-facing functions with automatic algorithm selection ([nvalchemiops/neighborlist/__init__.py](), [nvalchemiops/interactions/dispersion/dftd3.py](), [nvalchemiops/interactions/electrostatics/]())
2. **Computational Primitives**: Three main modules implementing neighbor lists, dispersion corrections, and electrostatics
3. **Warp Kernel Implementations**: GPU-optimized kernels written in NVIDIA Warp ([nvalchemiops/neighborlist/warp/](), [nvalchemiops/interactions/dispersion/warp/](), [nvalchemiops/interactions/electrostatics/warp/]())
4. **Execution Backends**: NVIDIA Warp runtime for GPU/CPU execution with PyTorch tensor compatibility

**Sources:** [README.md:10-25](), [docs/index.md:8-15](), [docs/userguide/about/intro.md:44-53]()

## Computational Primitives

The toolkit provides three core computational primitives that work together to enable atomistic simulations:

```mermaid
graph LR
    subgraph Input["Input Data"]
        POS["positions<br/>(torch.Tensor)"]
        ATNUMS["atomic_numbers<br/>(torch.Tensor)"]
        CELL["cell<br/>(torch.Tensor)"]
        PBC["pbc<br/>(torch.Tensor)"]
    end
    
    subgraph NL["Neighbor List Construction"]
        NL_API["neighbor_list()"]
        
        NL_API --> CL["cell_list()<br/>O(N) spatial"]
        NL_API --> NAIVE["naive_neighbor_list()<br/>O(N²) pairwise"]
        NL_API --> BCL["batch_cell_list()<br/>O(N) batched"]
        NL_API --> BNAIVE["batch_naive_neighbor_list()<br/>O(N²) batched"]
        
        CL --> OUT_DENSE["neighbor_matrix<br/>num_neighbors<br/>shift_matrix"]
        NAIVE --> OUT_DENSE
        BCL --> OUT_DENSE
        BNAIVE --> OUT_DENSE
        
        CL --> OUT_COO["edge_index<br/>neighbor_ptr<br/>shifts"]
        NAIVE --> OUT_COO
        BCL --> OUT_COO
        BNAIVE --> OUT_COO
    end
    
    subgraph DISP["DFT-D3 Dispersion"]
        DFTD3["dftd3()"]
        
        DFTD3 --> D3_OUT["d3_energies<br/>d3_forces<br/>coord_nums<br/>d3_virials"]
    end
    
    subgraph ELEC["Electrostatics"]
        ELEC_API["Electrostatics API"]
        
        ELEC_API --> EWALD["ewald_summation()<br/>O(N²)"]
        ELEC_API --> PME["particle_mesh_ewald()<br/>O(N log N)"]
        
        EWALD --> ELEC_OUT["atom_energies<br/>atom_forces"]
        PME --> ELEC_OUT
    end
    
    POS --> NL_API
    CELL --> NL_API
    PBC --> NL_API
    
    OUT_DENSE -.->|"neighbor data"| DFTD3
    OUT_COO -.->|"neighbor data"| DFTD3
    
    OUT_DENSE -.->|"neighbor data"| ELEC_API
    OUT_COO -.->|"neighbor data"| ELEC_API
    
    POS --> DFTD3
    ATNUMS --> DFTD3
    
    POS --> ELEC_API
```

### Primitive 1: Neighbor List Construction

| Function | Algorithm | Complexity | Use Case |
|----------|-----------|------------|----------|
| `cell_list` | Spatial decomposition | O(N) | Single systems >5K atoms |
| `naive_neighbor_list` | Pairwise distance | O(N²) | Single systems <5K atoms |
| `batch_cell_list` | Batched spatial | O(N) | Multiple large systems |
| `batch_naive_neighbor_list` | Batched pairwise | O(N²) | Multiple small systems |

The unified `neighbor_list()` function automatically selects the appropriate algorithm based on system size and batching configuration. Output formats include dense matrices (for `torch.compile` optimization) and sparse COO format (for GNN integration).

**Key Code Entities:**
- [nvalchemiops/neighborlist/neighbor_list.py]() - Main API function
- [nvalchemiops/neighborlist/cell_list.py]() - Cell list implementation
- [nvalchemiops/neighborlist/naive.py]() - Naive implementation
- [nvalchemiops/neighborlist/warp/]() - GPU kernels

For detailed documentation, see [Neighbor Lists](#2.1).

### Primitive 2: DFT-D3 Dispersion Corrections

The `dftd3()` function computes Grimme's DFT-D3 dispersion energy with Becke-Johnson damping, using environment-dependent C6 coefficients derived from coordination numbers. The implementation uses a multi-pass kernel architecture:

| Pass | Purpose | Computation |
|------|---------|-------------|
| Pass 0 | PBC handling | Apply periodic boundary shifts |
| Pass 1 | Coordination | Calculate coordination numbers |
| Pass 2 | Direct forces | Compute dispersion forces |
| Pass 3 | Chain rule | Apply coordination-dependent derivatives |

**Key Code Entities:**
- [nvalchemiops/interactions/dispersion/dftd3.py]() - Main API
- [nvalchemiops/interactions/dispersion/dftd3_params.py]() - Parameter dataclass
- [nvalchemiops/interactions/dispersion/warp/dftd3_kernel.py]() - Multi-pass kernel

For detailed documentation, see [Dispersion Corrections (DFT-D3)](#2.2).

### Primitive 3: Electrostatics

Two methods are provided for long-range Coulomb interactions in periodic systems:

| Method | Function | Complexity | Recommended Size |
|--------|----------|------------|-----------------|
| Ewald | `ewald_summation()` | O(N²) | <5K atoms |
| PME | `particle_mesh_ewald()` | O(N log N) | >5K atoms |

Both methods split the $1/r$ potential into real-space (short-range) and reciprocal-space (long-range) components, with automatic parameter estimation based on target accuracy.

**Key Code Entities:**
- [nvalchemiops/interactions/electrostatics/ewald.py]() - Ewald summation
- [nvalchemiops/interactions/electrostatics/pme.py]() - Particle mesh Ewald
- [nvalchemiops/interactions/electrostatics/warp/]() - GPU kernels

For detailed documentation, see [Electrostatics](#2.3).

**Sources:** [README.md:16-24](), [docs/userguide/about/intro.md:54-265](), [docs/index.md:8-15]()

## Target Users and Use Cases

The toolkit serves three primary user personas with different interaction patterns:

```mermaid
graph TB
    subgraph Users["User Personas"]
        ML["ML Researchers"]
        METHOD["Method Developers"]
        CHEM["Computational Chemists"]
    end
    
    subgraph APIs["API Entry Points"]
        HIGH["High-Level APIs<br/>neighbor_list()<br/>dftd3()<br/>ewald_summation()"]
        LOW["Low-Level Kernels<br/>warp modules"]
    end
    
    subgraph Workflows["Workflow Patterns"]
        GNN["GNN Training<br/>COO edge_index<br/>batched graphs"]
        CUSTOM["Custom Methods<br/>composable kernels<br/>profiling tools"]
        DFT["DFT+D3<br/>energy/forces<br/>geometry opt"]
    end
    
    subgraph Integration["Integration"]
        TORCH_INT["PyTorch Tensors<br/>torch.compile<br/>autograd"]
        WARP_INT["Warp Kernels<br/>GPU memory<br/>custom workflows"]
    end
    
    ML --> HIGH
    ML --> GNN
    ML --> TORCH_INT
    GNN -.->|"sparse COO output"| HIGH
    
    METHOD --> LOW
    METHOD --> CUSTOM
    METHOD --> WARP_INT
    CUSTOM -.->|"access to"| LOW
    
    CHEM --> HIGH
    CHEM --> DFT
    CHEM --> TORCH_INT
    DFT -.->|"uses"| HIGH
```

### Use Case 1: Graph Neural Networks

ML researchers use `nvalchemiops` to generate graph connectivity for molecular datasets. The sparse COO output format (`return_neighbor_list=True`) provides `edge_index` directly compatible with GNN frameworks. Batching enables high-throughput training on datasets with heterogeneous molecule sizes.

**Example Workflow:**
```python
# From docs/userguide/about/intro.md:82-88
edge_index, neighbor_ptr, shifts = neighbor_list(
    positions, cutoff, cell=cell, pbc=pbc, return_neighbor_list=True
)
# edge_index is sparse COO format compatible with PyTorch Geometric
```

### Use Case 2: Method Development

Method developers access low-level Warp kernels to build custom atomistic algorithms. The modular kernel design allows composition of primitives (e.g., combining neighbor lists with custom interaction potentials).

**Key Code Entities:**
- [nvalchemiops/neighborlist/warp/]() - Neighbor list kernels
- [nvalchemiops/interactions/dispersion/warp/]() - Dispersion kernels
- [nvalchemiops/interactions/electrostatics/warp/]() - Electrostatics kernels

### Use Case 3: Computational Chemistry

Computational chemists integrate DFT-D3 dispersion corrections into density functional theory workflows. The `dftd3()` function provides accurate forces for geometry optimization and coordinates numbers for analysis.

**Example Workflow:**
```python
# From docs/userguide/about/intro.md:186-198
energy, forces, coord_num = dftd3(
    positions, numbers, neighbor_list=neighbors,
    a1=0.4289, a2=4.4407, s8=0.7875,  # PBE functional parameters
    d3_params=d3_params
)
```

**Sources:** [README.md:26-44](), [docs/index.md:17-28](), [docs/userguide/about/intro.md:16-42]()

## Package Structure

The codebase is organized into a three-layer hierarchy:

```mermaid
graph TB
    subgraph Package["nvalchemiops/"]
        subgraph HighLevel["High-Level APIs"]
            NL_INIT["neighborlist/__init__.py<br/>neighbor_list()"]
            DISP_INIT["interactions/dispersion/dftd3.py<br/>dftd3()"]
            ELEC_INIT["interactions/electrostatics/<br/>ewald.py, pme.py"]
        end
        
        subgraph Implementations["Algorithm Implementations"]
            NL_IMPL["neighborlist/<br/>cell_list.py<br/>naive.py<br/>batch_cell_list.py<br/>batch_naive.py"]
            DISP_IMPL["interactions/dispersion/<br/>dftd3_params.py<br/>coordination.py"]
            ELEC_IMPL["interactions/electrostatics/<br/>coulomb.py<br/>utils.py"]
        end
        
        subgraph Kernels["Warp Kernels (GPU)"]
            NL_WARP["neighborlist/warp/<br/>cell_list.py<br/>naive.py<br/>batch_kernels.py"]
            DISP_WARP["interactions/dispersion/warp/<br/>dftd3_kernel.py<br/>coordination_kernel.py"]
            ELEC_WARP["interactions/electrostatics/warp/<br/>ewald_kernel.py<br/>pme_kernel.py"]
        end
    end
    
    subgraph External["External Systems"]
        BENCH["benchmarks/<br/>benchmark scripts<br/>generate_plots.py"]
        DOCS["docs/<br/>userguide/<br/>examples/"]
        TESTS["tests/<br/>unit tests<br/>integration tests"]
    end
    
    NL_INIT --> NL_IMPL
    DISP_INIT --> DISP_IMPL
    ELEC_INIT --> ELEC_IMPL
    
    NL_IMPL --> NL_WARP
    DISP_IMPL --> DISP_WARP
    ELEC_IMPL --> ELEC_WARP
    
    BENCH -.->|"measures"| NL_INIT
    BENCH -.->|"measures"| DISP_INIT
    BENCH -.->|"measures"| ELEC_INIT
    
    DOCS -.->|"documents"| NL_INIT
    DOCS -.->|"documents"| DISP_INIT
    DOCS -.->|"documents"| ELEC_INIT
    
    TESTS -.->|"validates"| NL_IMPL
    TESTS -.->|"validates"| DISP_IMPL
    TESTS -.->|"validates"| ELEC_IMPL
```

### Key Modules

| Module | Purpose | Key Files |
|--------|---------|-----------|
| `nvalchemiops.neighborlist` | Neighbor list construction | `neighbor_list.py`, `cell_list.py`, `naive.py` |
| `nvalchemiops.neighborlist.warp` | Neighbor list GPU kernels | `cell_list.py`, `naive.py`, `batch_kernels.py` |
| `nvalchemiops.interactions.dispersion` | DFT-D3 dispersion corrections | `dftd3.py`, `dftd3_params.py`, `coordination.py` |
| `nvalchemiops.interactions.dispersion.warp` | Dispersion GPU kernels | `dftd3_kernel.py`, `coordination_kernel.py` |
| `nvalchemiops.interactions.electrostatics` | Electrostatic interactions | `ewald.py`, `pme.py`, `coulomb.py` |
| `nvalchemiops.interactions.electrostatics.warp` | Electrostatics GPU kernels | `ewald_kernel.py`, `pme_kernel.py` |
| `benchmarks/` | Performance benchmarking | `benchmark_*.py`, `generate_plots.py` |
| `docs/` | Documentation | `userguide/`, `examples/`, `benchmarks/` |
| `tests/` | Test suite | Unit and integration tests |

**Sources:** [README.md:1-203](), package structure analysis

## Integration with PyTorch and NVIDIA Warp

The toolkit provides seamless integration with the PyTorch ecosystem while leveraging NVIDIA Warp for GPU acceleration:

```mermaid
graph LR
    subgraph User["User Code"]
        INPUT["PyTorch Tensors<br/>positions, charges, etc."]
    end
    
    subgraph NVAO["nvalchemiops"]
        API["Python API Layer<br/>neighbor_list(), dftd3()"]
        BRIDGE["PyTorch-Warp Bridge<br/>tensor conversion"]
        KERNELS["Warp GPU Kernels<br/>@wp.kernel functions"]
    end
    
    subgraph Runtime["Runtime Systems"]
        WARP_RT["NVIDIA Warp Runtime<br/>JIT compilation"]
        TORCH_RT["PyTorch Runtime<br/>autograd, compile"]
    end
    
    subgraph HW["Hardware"]
        GPU_HW["NVIDIA GPU<br/>CUDA execution"]
    end
    
    INPUT --> API
    API --> BRIDGE
    BRIDGE --> KERNELS
    KERNELS --> WARP_RT
    WARP_RT --> GPU_HW
    
    API -.->|"torch.compile support"| TORCH_RT
    TORCH_RT -.->|"JIT optimization"| GPU_HW
    
    GPU_HW --> KERNELS
    KERNELS --> BRIDGE
    BRIDGE --> API
    API --> INPUT
```

### PyTorch Compatibility

All public API functions accept and return PyTorch tensors with the following features:

- **Automatic device handling**: CPU and CUDA tensors are supported transparently
- **`torch.compile` support**: Custom operators registered for JIT compilation
- **Autograd integration**: Gradients maintained where applicable (e.g., DFT-D3 forces)
- **Batch operations**: Native support for batched tensors with `batch_idx` parameter

For details, see [PyTorch Compatibility](#3.2).

### NVIDIA Warp Backend

GPU kernels are implemented in NVIDIA Warp, providing:

- **JIT compilation**: Kernels compiled at runtime for target GPU architecture
- **Memory optimization**: GPU memory layouts optimized for NVIDIA hardware
- **Profiling support**: Compatible with Nsight Systems and other NVIDIA tools
- **CPU fallback**: Automatic CPU execution when GPU unavailable

For details, see [NVIDIA Warp Integration](#3.1).

**Sources:** [docs/index.md:13-15](), [docs/userguide/about/intro.md:355-372](), [README.md:12-14]()

## Performance Characteristics

The toolkit exhibits distinct performance scaling behavior across different system sizes:

| System Size | Recommended Algorithm | Time Range | Memory Usage |
|-------------|----------------------|------------|--------------|
| <1K atoms | `naive` or `batch_naive` | ~0.3-0.5 ms | <100 MB |
| 1K-5K atoms | Algorithm transition region | ~0.5-2 ms | 100 MB - 1 GB |
| 5K-100K atoms | `cell_list` or `batch_cell_list` | ~2-100 ms | 1 GB - 10 GB |
| >100K atoms | `cell_list` (risk of OOM) | >100 ms | >10 GB |

The automatic algorithm selection in `neighbor_list()` switches from naive O(N²) to cell list O(N) at the ~5K atom threshold to optimize performance. For comprehensive performance analysis, see [Performance and Benchmarks](#4).

**Sources:** [README.md:16-24](), performance diagram analysis

## What's Next?

To get started with NVIDIA ALCHEMI Toolkit-Ops:

1. Follow [Installation and Setup](#1.1) to install the package
2. Try the [Quick Start Guide](#1.2) for working examples
3. Read [Core Components](#2) for detailed component documentation
4. Explore [Performance and Benchmarks](#4) to understand scaling behavior
5. Refer to [API Reference](#5) for complete function signatures

For method developers interested in low-level kernel access, see [NVIDIA Warp Integration](#3.1) and [Development and Contributing](#6).

**Sources:** [docs/userguide/about/intro.md:378-388](), [README.md:179-203]()

---

