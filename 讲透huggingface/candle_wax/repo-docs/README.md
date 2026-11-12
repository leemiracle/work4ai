# Candle Wax

ML playground for experimenting and developing Candle concepts.

The wax that candles are made from.

# Design Philosophy

## The Problem

Model developers and framework maintainers have fundamentally different goals:

**Model Developers** want:
- Flexibility to experiment with new architectures
- Performance that matches existing implementations
- Freedom from worrying about low-level optimization details

**Framework Maintainers** want:
- A small set of heavily optimized kernels
- Ability to quickly develop backends for new hardware
- Maintainable, portable codebases

Currently, these goals are in tension. When a new model architecture emerges, framework maintainers must spend significant engineering hours creating bespoke implementations. You can see this pattern in projects like Transformers or Candle—each new model requires substantial custom work.

## Our Solution

### Basis Operations

All tensor operations can be decomposed into a small set of basis operations that can be composed together to achieve any desired result. We define this basis set as the minimum collection of operations where every other operation can be expressed using O(1) basis operations.

#### Examples

**Matrix Multiplication** decomposes into:
- Broadcast multiply
- Reduce sum

**Softmax** decomposes into:
- Map exponential
- Reduce sum
- Broadcast division

**Attention** decomposes into:
- 2 matrix multiplies (further decomposable)
- Broadcast division
- Softmax (further decomposable)

The basis set includes operations like:
- **Map** - Apply scalar → scalar functions (e.g., ReLU, exponential)
- **Reduce** - Aggregation with an accumulator (e.g., sum, max)
- **Broadcast** - Element-wise binary operations on scalars
- **Structural operations** - Reshape, slice, permute (require no tensor value knowledge, just memory layout)
- **Spectral operations** - Convolutions, FFT, etc.

### Modular Backend Architecture

We're building a flexible system that separates concerns and enables true extensibility:

- **External Backend Development** - Create backends in separate repositories without forking the main project.
- **Separation of Storage and Execution** - Tensors and tensor storage are decoupled from backend implementation. Operations are no longer performed directly on storage, eliminating unnecessary coupling. This means tensors can live in for example NVIDIA VRAM while running different backends. For example, one optimized for computer vision, and another for transformers, without data movement.

## Benefits

### For Model Developers
Write models using familiar high-level operations. The framework automatically transforms them into basis operations under the hood—no performance penalty, no implementation burden.

### For Framework Maintainers
- **Faster backend development** - Only implement basis operations for new hardware, Spend time optimizing critical kernels rather than implementing every conceivable operation.
- **No forking required** - Develop and maintain backends in separate repositories
- **Flexible optimization** - Start with simple implementations, then optimize critical paths using rewrite rules
- **Backend composition** - Use multiple specialized backends simultaneously without moving data

### For Everyone
This approach decouples model innovation from framework implementation speed. Model developers can experiment freely while framework maintainers maintain clean, optimized codebases, and backend developers can contribute without modifying the core framework.