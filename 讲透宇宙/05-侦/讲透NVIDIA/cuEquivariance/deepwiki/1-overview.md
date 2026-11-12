<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cuEquivariance · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [README.md](README.md)
- [VERSION](VERSION)
- [docs/changelog.md](docs/changelog.md)
- [docs/index.rst](docs/index.rst)

</details>



This document provides an overview of the cuEquivariance library, its architecture, and core concepts. cuEquivariance is an NVIDIA Python library for building high-performance geometric neural networks using segmented polynomials and optimized CUDA kernels.

For specific installation instructions, see [Installation](#1.1). For detailed version history and breaking changes, see [Version History](#1.2). For mathematical foundations, see [Core Concepts](#2).

## What is cuEquivariance

cuEquivariance enables the construction of equivariant neural networks that respect geometric symmetries. Equivariance is the mathematical formalization of "respecting symmetries" - robust physical models exhibit equivariance with respect to rotations and translations in three-dimensional space, making AI models more data-efficient.

The library provides:
- **Segmented Polynomials**: Flexible mathematical framework for describing equivariant operations
- **Triangular Operations**: Specialized operations for AlphaFold2-style architectures  
- **CUDA Optimization**: High-performance GPU kernels with automatic tuning
- **Dual Bindings**: Support for both PyTorch and JAX frameworks

**Sources**: [README.md:1-6](), [docs/index.rst:19-22]()

## Package Architecture

cuEquivariance is organized into three main packages that provide different levels of functionality:

```mermaid
graph TB
    subgraph "Package Ecosystem"
        CORE["cuequivariance<br/>Core Mathematical Library"]
        TORCH["cuequivariance-torch<br/>PyTorch Integration"] 
        JAX["cuequivariance-jax<br/>JAX Integration"]
        
        subgraph "CUDA Acceleration"
            CUDA_TORCH["cuequivariance-ops-torch-cu12<br/>PyTorch CUDA Kernels"]
            CUDA_JAX["cuequivariance-ops-jax-cu12<br/>JAX CUDA Kernels"]
        end
    end
    
    subgraph "Import Aliases"
        CUE["import cuequivariance as cue"]
        CUET["import cuequivariance_torch as cuet"] 
        CUEX["import cuequivariance_jax as cuex"]
    end
    
    CORE --> TORCH
    CORE --> JAX
    CUDA_TORCH --> TORCH
    CUDA_JAX --> JAX
    
    CUE -.-> CORE
    CUET -.-> TORCH
    CUEX -.-> JAX
```

### Core Package (`cuequivariance`)

The core package contains framework-agnostic mathematical components:
- Group theory foundations (`cue.Rep`, `cue.Irreps`)
- Segmented tensor products (`cue.SegmentedTensorProduct`)
- Polynomial representations (`cue.SegmentedPolynomial`, `cue.EquivariantPolynomial`)
- Mathematical descriptors (`cue.descriptors`)

### Framework Bindings

| Package | Purpose | Key Components |
|---------|---------|----------------|
| `cuequivariance-torch` | PyTorch integration | `cuet.SegmentedPolynomial`, `cuet.TensorProduct`, triangle operations |
| `cuequivariance-jax` | JAX integration | `cuex.segmented_polynomial()`, `cuex.equivariant_polynomial()` |

### CUDA Acceleration

Optimized CUDA kernels provide significant performance improvements:
- **Triton Kernels**: Auto-tuned GPU implementations
- **Custom CUDA**: Specialized operations like `sigmoid_gated_dual_gemm`
- **Fallback Support**: Automatic fallback to framework implementations when needed

**Sources**: [docs/index.rst:57-69](), [README.md:13-22](), [CHANGELOG.md:18]()

## Core Mathematical Framework

The library uses a hierarchical structure to describe equivariant operations:

```mermaid
graph TD
    subgraph "Mathematical Hierarchy"
        EQP["cue.EquivariantPolynomial<br/>Representation constraints<br/>Input/output Rep validation"]
        
        SP["cue.SegmentedPolynomial<br/>Operation sequences<br/>Multiple tensor products<br/>Optimization pipeline"]
        
        STP["cue.SegmentedTensorProduct<br/>Individual tensor product<br/>Path definitions<br/>Coefficient handling"]
        
        SO["cue.SegmentedOperand<br/>Tensor segments<br/>Shape management<br/>Memory layout"]
    end
    
    subgraph "Group Theory"
        REP["cue.Rep<br/>Abstract representation"]
        IRREPS["cue.Irreps<br/>SO(3) irreducible representations"]
        LAYOUT["cue.IrrepsLayout<br/>Memory organization"]
    end
    
    EQP --> SP
    SP --> STP
    STP --> SO
    
    EQP --> REP
    REP --> IRREPS
    IRREPS --> LAYOUT
```

### Key Classes

- **`cue.EquivariantPolynomial`**: High-level interface ensuring equivariance constraints
- **`cue.SegmentedPolynomial`**: Manages sequences of tensor product operations  
- **`cue.SegmentedTensorProduct`**: Defines specific tensor product computations
- **`cue.SegmentedOperand`**: Handles tensor segmentation and memory layout

**Sources**: [docs/index.rst:75-80](), [CHANGELOG.md:92-94]()

## Execution Methods and Performance

cuEquivariance provides multiple execution backends optimized for different scenarios:

```mermaid
graph LR
    subgraph "User Operation"
        USER["cuet.SegmentedPolynomial<br/>or<br/>cuex.segmented_polynomial()"]
    end
    
    subgraph "Method Selection"
        METHOD_ARG["method parameter<br/>naive | uniform_1d<br/>fused_tp | indexed_linear"]
    end
    
    subgraph "Execution Backends"
        NAIVE["naive<br/>PyTorch/JAX fallback<br/>Framework operations"]
        UNIFORM["uniform_1d<br/>CUDA optimized<br/>Triton kernels"]
        FUSED["fused_tp<br/>Multi-operand fusion<br/>Memory optimization"]
        INDEXED["indexed_linear<br/>Weighted operations<br/>Scatter/gather"]
    end
    
    USER --> METHOD_ARG
    METHOD_ARG --> NAIVE
    METHOD_ARG --> UNIFORM  
    METHOD_ARG --> FUSED
    METHOD_ARG --> INDEXED
```

### Execution Methods

| Method | Description | Use Case |
|--------|-------------|----------|
| `naive` | Framework fallback implementation | Development, debugging, unsupported shapes |
| `uniform_1d` | CUDA-optimized for uniform operations | Standard tensor products, best general performance |
| `fused_tp` | Multi-operand tensor product fusion | Complex polynomials, memory-bound operations |
| `indexed_linear` | Scatter/gather with linear operations | Sparse operations, graph neural networks |

### Performance Features

- **Auto-tuning**: Kernel parameters optimized per hardware configuration
- **Precision Control**: TF32, IEEE-754, mixed precision support  
- **Memory Optimization**: Fused operations reduce memory bandwidth requirements
- **Fallback Logic**: Automatic selection based on input shapes and platform capabilities

**Sources**: [CHANGELOG.md:7](), [CHANGELOG.md:34-41](), [CHANGELOG.md:43-48]()

## Framework Integration Patterns

### PyTorch Integration

```mermaid
graph LR
    subgraph "PyTorch Workflow"
        DESC["cue.descriptors<br/>linear, spherical_harmonics<br/>channelwise_tensor_product"]
        
        MODULE["cuet.SegmentedPolynomial<br/>PyTorch nn.Module<br/>Trainable parameters"]
        
        EXEC["Execution<br/>CUDA kernels<br/>torch.compile support"]
    end
    
    DESC --> MODULE
    MODULE --> EXEC
```

### JAX Integration  

```mermaid
graph LR
    subgraph "JAX Workflow"
        DESC_JAX["cue.descriptors<br/>Same mathematical definitions"]
        
        FUNC["cuex.equivariant_polynomial()<br/>Functional interface<br/>JAX transformations"]
        
        EXEC_JAX["Execution<br/>JIT compilation<br/>Custom primitives"]
    end
    
    DESC_JAX --> FUNC
    FUNC --> EXEC_JAX
```

Both frameworks share the same mathematical descriptors from the core package but provide different execution interfaces optimized for their respective ecosystems.

**Sources**: [docs/index.rst:81-84](), [CHANGELOG.md:124-127](), [CHANGELOG.md:150-152]()

## Specialized Operations

Beyond general tensor products, cuEquivariance provides operations optimized for specific architectures:

### Triangle Operations
- **`cuet.triangle_attention`**: Attention mechanisms for triangular adjacency matrices
- **`cuet.triangle_multiplicative_update`**: AlphaFold2-style triangle multiplicative updates
- **`cuet.attention_pair_bias`**: Pair bias computation with caching support

### Symmetric Operations  
- **`cuet.SymmetricTensorProduct`**: Symmetric contractions and products
- **`cue.descriptors.symmetric_contraction`**: Mathematical descriptor for symmetric operations

**Sources**: [CHANGELOG.md:64-66](), [CHANGELOG.md:6]()

---

