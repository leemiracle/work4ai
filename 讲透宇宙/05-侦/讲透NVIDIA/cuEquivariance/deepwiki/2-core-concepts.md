<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cuEquivariance · page 2 Core Concepts · fetched 2026-10-26 -->

# Core Concepts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cuequivariance/cuequivariance/group_theory/equivariant_polynomial.py](cuequivariance/cuequivariance/group_theory/equivariant_polynomial.py)
- [cuequivariance/cuequivariance/segmented_polynomials/segmented_polynomial.py](cuequivariance/cuequivariance/segmented_polynomials/segmented_polynomial.py)

</details>



This document covers the fundamental mathematical concepts and core data structures that form the foundation of the cuEquivariance library. These concepts enable the construction of equivariant neural networks through polynomial representations of tensor operations that respect group symmetries.

For framework-specific implementations, see [PyTorch Implementation](#3) and [JAX Implementation](#4). For performance optimization details, see [CUDA Kernels and Tuning](#5.2).

## Mathematical Foundations

The cuEquivariance library is built on mathematical concepts from group theory and representation theory that ensure neural network operations maintain equivariance properties under group transformations.

### Group Theory and Equivariance

```mermaid
graph TD
    subgraph "Mathematical Foundation"
        GROUP["Group G<br/>(SO3, O3)"]
        REP["Representation ρ<br/>Group → GL(V)"]
        IRREP["Irreducible Representations<br/>Fundamental building blocks"]
    end
    
    subgraph "Equivariance Constraint"
        INPUT["Input Tensor x"]
        TRANSFORM["Group Element g ∈ G"]
        FUNCTION["Neural Network f"]
        OUTPUT["Output Tensor f(x)"]
    end
    
    subgraph "Implementation"
        CUE_REP["cue.Rep<br/>Abstract representation"]
        IRREPS["cue.Irreps<br/>Direct sum of irreps"]
        LAYOUT["cue.IrrepsAndLayout<br/>Memory layout specification"]
    end
    
    GROUP --> REP
    REP --> IRREP
    
    INPUT --> FUNCTION
    FUNCTION --> OUTPUT
    TRANSFORM --> INPUT
    TRANSFORM --> OUTPUT
    
    IRREP --> CUE_REP
    CUE_REP --> IRREPS
    IRREPS --> LAYOUT
    
    FUNCTION -.->|"f(ρ(g)x) = ρ(g)f(x)"| TRANSFORM
```

The core mathematical principle is that for any group element `g`, the function `f` must satisfy the equivariance constraint: `f(ρ(g)x) = ρ(g)f(x)`, where `ρ` is the group representation.

Sources: [cuequivariance/cuequivariance/group_theory/equivariant_polynomial.py:28-75]()

### Representation Theory Implementation

| Concept | Implementation | Purpose |
|---------|----------------|---------|
| Group | `cue.SO3`, `cue.O3` | Rotation and reflection groups |
| Representation | `cue.Rep` | Abstract group representation |
| Irreducible Representation | `cue.Irrep` | Fundamental representation building blocks |
| Direct Sum | `cue.Irreps` | Combination of multiple irreps |
| Memory Layout | `cue.IrrepsAndLayout` | Tensor layout with representation info |

Sources: [cuequivariance/cuequivariance/group_theory/equivariant_polynomial.py:42-75]()

## Core Data Structures

The library implements several key data structures that work together to represent and compute equivariant operations.

### Segmented Operands and Tensor Products

```mermaid
graph TD
    subgraph "Data Structure Hierarchy"
        SEGOP["SegmentedOperand<br/>• size: int<br/>• segments: tuple[tuple[int, ...]]<br/>• segment_shape management"]
        
        STP["SegmentedTensorProduct<br/>• operands: tuple[SegmentedOperand]<br/>• paths: list[Path]<br/>• coefficient_subscripts: str"]
        
        OPERATION["Operation<br/>• buffers: tuple[int]<br/>• input/output mapping<br/>• permutation operations"]
    end
    
    subgraph "Tensor Product Components"
        PATH["Path<br/>• Coefficient indexing<br/>• Operand indexing<br/>• Computational path"]
        
        SUBSCRIPTS["Subscripts<br/>• Einstein notation<br/>• Mode specifications<br/>• Contraction patterns"]
        
        COEFF["Coefficients<br/>• Learnable parameters<br/>• Clebsch-Gordan coefficients<br/>• Weight matrices"]
    end
    
    SEGOP --> STP
    OPERATION --> STP
    STP --> PATH
    STP --> SUBSCRIPTS
    STP --> COEFF
```

**SegmentedOperand** represents tensors divided into segments, each with potentially different shapes. This segmentation allows efficient handling of irreducible representations where different irreps may have different dimensions.

**SegmentedTensorProduct** defines how multiple operands are combined through tensor product operations. It contains the computational paths and indexing patterns needed to perform the operations.

**Operation** specifies which operands (identified by buffer indices) participate in a tensor product and how they map to inputs and outputs.

Sources: [cuequivariance/cuequivariance/segmented_polynomials/segmented_polynomial.py:49-51](), [cuequivariance/cuequivariance/segmented_polynomials/segmented_polynomial.py:70-85]()

### Polynomial Representations

The library uses polynomial representations to encode complex equivariant operations as sequences of tensor products.

```mermaid
graph LR
    subgraph "Polynomial Architecture"
        INPUTS["inputs: tuple[SegmentedOperand]"]
        OUTPUTS["outputs: tuple[SegmentedOperand]"]
        OPERATIONS["operations: tuple[<br/>(Operation, SegmentedTensorProduct)]"]
    end
    
    subgraph "SegmentedPolynomial"
        SP_CLASS["SegmentedPolynomial<br/>• Pure tensor operations<br/>• No equivariance constraints<br/>• Computational graph"]
    end
    
    subgraph "EquivariantPolynomial" 
        EP_CLASS["EquivariantPolynomial<br/>• inputs: tuple[Rep]<br/>• outputs: tuple[Rep]<br/>• polynomial: SegmentedPolynomial"]
        
        REP_CONSTRAINT["Representation Constraints<br/>• Input/output rep validation<br/>• Equivariance enforcement<br/>• Group theory integration"]
    end
    
    INPUTS --> SP_CLASS
    OUTPUTS --> SP_CLASS  
    OPERATIONS --> SP_CLASS
    
    SP_CLASS --> EP_CLASS
    REP_CONSTRAINT --> EP_CLASS
```

**SegmentedPolynomial** is the foundational computational representation that defines a sequence of tensor product operations without any group theory constraints. It manages the computational graph and provides core functionality for evaluation, transformation, and automatic differentiation.

**EquivariantPolynomial** extends `SegmentedPolynomial` by adding group representation information for inputs and outputs, ensuring that all operations respect equivariance constraints.

Sources: [cuequivariance/cuequivariance/segmented_polynomials/segmented_polynomial.py:34-51](), [cuequivariance/cuequivariance/group_theory/equivariant_polynomial.py:28-75]()

## Data Flow and Computational Graph

The computational flow proceeds from high-level equivariant specifications down to low-level tensor operations:

```mermaid
graph TD
    subgraph "High-Level Interface"
        DESC["Descriptors<br/>• linear<br/>• spherical_harmonics<br/>• channelwise_tensor_product<br/>• symmetric_contraction<br/>• fully_connected_tensor_product"]
    end
    
    subgraph "Polynomial Layer"
        EQUIV_POLY["EquivariantPolynomial<br/>Representation constraints"]
        SEG_POLY["SegmentedPolynomial<br/>Computational graph"]
    end
    
    subgraph "Operation Layer"  
        OP_STP["(Operation, SegmentedTensorProduct)<br/>Individual tensor products"]
        PATHS["Path sequences<br/>Coefficient indexing"]
    end
    
    subgraph "Execution Layer"
        BACKEND["Backend Selection<br/>• naive<br/>• uniform_1d<br/>• fused_tp<br/>• indexed_linear"]
        KERNELS["CUDA Kernels<br/>• Triton implementations<br/>• Custom primitives"]
    end
    
    DESC --> EQUIV_POLY
    EQUIV_POLY --> SEG_POLY
    SEG_POLY --> OP_STP
    OP_STP --> PATHS
    PATHS --> BACKEND
    BACKEND --> KERNELS
```

The flow starts with high-level descriptors that specify the mathematical operation, proceeds through polynomial representations that encode the computational graph, and ends with optimized kernel implementations.

Sources: [cuequivariance/cuequivariance/segmented_polynomials/segmented_polynomial.py:36-47](), [cuequivariance/cuequivariance/group_theory/equivariant_polynomial.py:28-45]()

## Key Methods and Operations

### SegmentedPolynomial Core Methods

| Method Category | Key Methods | Purpose |
|----------------|-------------|---------|
| Construction | `eval_last_operand()`, `stack()`, `concatenate()` | Building polynomial representations |
| Analysis | `flop()`, `memory()`, `used_inputs()` | Performance and dependency analysis |
| Transformation | `consolidate()`, `fuse_stps()`, `apply_fn()` | Optimization and manipulation |
| Filtering | `filter_keep_operands()`, `compute_only()` | Selective computation |
| Autodiff | `jvp()`, `transpose()`, `backward()` | Automatic differentiation support |

Sources: [cuequivariance/cuequivariance/segmented_polynomials/segmented_polynomial.py:149-1113]()

### EquivariantPolynomial Extensions

The `EquivariantPolynomial` class provides the same interface as `SegmentedPolynomial` but with added representation validation and group theory constraints. Key additional methods include:

- `split_operand_by_irrep()`: Splits operands along irreducible representation boundaries
- Representation-aware stacking and filtering operations
- Automatic validation of representation compatibility

Sources: [cuequivariance/cuequivariance/group_theory/equivariant_polynomial.py:422-474]()

## Memory Layout and Segmentation

The segmented approach allows efficient memory management and computation by grouping tensor elements according to their transformation properties:

```mermaid
graph LR
    subgraph "Tensor Structure"
        TENSOR["Input Tensor<br/>Shape: (batch, total_dim)"]
    end
    
    subgraph "Segmented View"
        SEG1["Segment 1<br/>Irrep 0e (scalars)<br/>dim = 1"]
        SEG2["Segment 2<br/>Irrep 1o (vectors)<br/>dim = 3"] 
        SEG3["Segment 3<br/>Irrep 2e (5D tensors)<br/>dim = 5"]
    end
    
    subgraph "Operations"
        TP1["TensorProduct 1<br/>Operates on segments 1,2"]
        TP2["TensorProduct 2<br/>Operates on segments 1,3"]
        TP3["TensorProduct 3<br/>Operates on segments 2,3"]
    end
    
    TENSOR --> SEG1
    TENSOR --> SEG2  
    TENSOR --> SEG3
    
    SEG1 --> TP1
    SEG2 --> TP1
    SEG1 --> TP2
    SEG3 --> TP2
    SEG2 --> TP3
    SEG3 --> TP3
```

This segmentation enables the library to:
- Process only relevant portions of tensors for each operation
- Optimize memory access patterns
- Support heterogeneous irreducible representations efficiently

Sources: [cuequivariance/cuequivariance/segmented_polynomials/segmented_polynomial.py:109-144]()

---

