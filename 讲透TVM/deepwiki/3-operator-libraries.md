> 来源: [https://deepwiki.com/apache/tvm/3-operator-libraries](https://deepwiki.com/apache/tvm/3-operator-libraries)
> DeepWiki apache/tvm | Last indexed: 31 August 2026 (b16cde

# Operator Libraries

  Relevant source files 
 - [include/tvm/relax/attrs/index.h](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/relax/attrs/index.h)
 - [include/tvm/topi/nn.h](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/topi/nn.h)
 - [include/tvm/topi/nn/rms_norm.h](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/topi/nn/rms_norm.h)
 - [include/tvm/topi/reduction.h](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/topi/reduction.h)
 - [include/tvm/topi/transform.h](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/topi/transform.h)
 - [python/tvm/relax/op/index.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/op/index.py)
 - [python/tvm/relax/transform/legalize_ops/__init__.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/legalize_ops/__init__.py)
 - [python/tvm/relax/transform/legalize_ops/index.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/legalize_ops/index.py)
 - [python/tvm/relax/transform/legalize_ops/linear_algebra.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/legalize_ops/linear_algebra.py)
 - [python/tvm/relax/transform/legalize_ops/statistical.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/legalize_ops/statistical.py)
 - [python/tvm/topi/nn/__init__.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/topi/nn/__init__.py)
 - [python/tvm/topi/nn/rms_norm.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/topi/nn/rms_norm.py)
 - [python/tvm/topi/reduction.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/topi/reduction.py)
 - [python/tvm/topi/testing/__init__.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/topi/testing/__init__.py)
 - [python/tvm/topi/testing/rms_norm_python.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/topi/testing/rms_norm_python.py)
 - [python/tvm/topi/transform.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/topi/transform.py)
 - [src/relax/op/tensor/index.cc](https://github.com/apache/tvm/blob/b16cdecb/src/relax/op/tensor/index.cc)
 - [src/relax/op/tensor/index.h](https://github.com/apache/tvm/blob/b16cdecb/src/relax/op/tensor/index.h)
 - [src/topi/nn.cc](https://github.com/apache/tvm/blob/b16cdecb/src/topi/nn.cc)
 - [src/topi/reduction.cc](https://github.com/apache/tvm/blob/b16cdecb/src/topi/reduction.cc)
 - [src/topi/transform.cc](https://github.com/apache/tvm/blob/b16cdecb/src/topi/transform.cc)
 - [tests/python/relax/test_op_index.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_op_index.py)
 - [tests/python/relax/test_op_take.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_op_take.py)
 - [tests/python/relax/test_transform_legalize_ops_index_linear_algebra.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_transform_legalize_ops_index_linear_algebra.py)
 - [tests/python/relax/test_transform_legalize_ops_search_statistical.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_transform_legalize_ops_search_statistical.py)
 
  
## Purpose and Scope

 Operator libraries in TVM provide reusable implementations of computational operations (operators) used in machine learning models. This document provides an overview of TVM's operator library architecture and the primary operator systems: TOPI (TVM Operator Inventory), Relax Operators, and fundamental Transform Operations.

 
 - For detailed information about Transform Operations and tensor manipulation primitives, see [Transform Operations](https://deepwiki.com/apache/tvm/3.1-transform-operations).
 - For detailed information about TOPI's implementation and hardware-specific schedules, see [TOPI - TVM Operator Inventory](https://deepwiki.com/apache/tvm/3.2-topi-tvm-operator-inventory).
 - For Relax-level operator APIs including registration and type inference, see [Relax Operators](https://deepwiki.com/apache/tvm/3.3-relax-operators).
 
 **Sources:** [python/tvm/topi/__init__.py19-22](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/topi/__init__.py#L19-L22) [src/relax/op/tensor/index.cc21-23](https://github.com/apache/tvm/blob/b16cdecb/src/relax/op/tensor/index.cc#L21-L23)

 
## Operator Library Architecture

 TVM's operator libraries operate at two distinct abstraction levels within the compilation pipeline:

 
 - **Relax Operators**: High-level, framework-facing operators that define semantics and type signatures (e.g., `relax.take`, `relax.matmul`).
 - **TOPI (TVM Operator Inventory)**: Low-level compute declarations and hardware-specific schedule implementations.
 
 
### Code-to-System Mapping: Operator Execution Flow

 The following diagram associates specific code entities with the stages of operator execution, from a high-level Relax call to the generation of a TensorIR (TIR) kernel.

 
```

```

 **Sources:** [src/relax/op/tensor/index.cc49-56](https://github.com/apache/tvm/blob/b16cdecb/src/relax/op/tensor/index.cc#L49-L56) [src/relax/op/tensor/index.cc129-135](https://github.com/apache/tvm/blob/b16cdecb/src/relax/op/tensor/index.cc#L129-L135) [python/tvm/relax/transform/legalize_ops/index.py30-34](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/legalize_ops/index.py#L30-L34) [src/topi/transform.cc112-128](https://github.com/apache/tvm/blob/b16cdecb/src/topi/transform.cc#L112-L128) [include/tvm/topi/transform.h1115-1130](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/topi/transform.h#L1115-L1130)

 
## Transform Operations

 Transform operations are the fundamental building blocks for tensor shape manipulation and data movement. These are used extensively by both Relax and TOPI to implement higher-level neural network layers.

 
### Key Primitives

 
| Operator | Code Location (TOPI) | Description |
|---|---|---|
| expand_dims | include/tvm/topi/transform.h156-192 | Inserts new dimensions of length 1 at a specified axis. |
| transpose | include/tvm/topi/transform.h194-220 | Permutes the dimensions of an array. |
| reshape | include/tvm/topi/transform.h496-515 | Changes the shape of a tensor without changing its data. |
| concatenate | include/tvm/topi/transform.h614-635 | Joins a sequence of tensors along an existing axis. |
| strided_slice | include/tvm/topi/transform.h894-915 | Extracts a slice of an array with optional striding. |
| sliding_window | include/tvm/topi/transform.h76-142 | Creates an operation to slide a window over the input tensor. |

 For details on the implementation of these primitives, see [Transform Operations](https://deepwiki.com/apache/tvm/3.1-transform-operations).

 **Sources:** [include/tvm/topi/transform.h21-23](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/topi/transform.h#L21-L23) [python/tvm/topi/transform.py18-31](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/topi/transform.py#L18-L31)

 
## Relax Operator System

 The Relax operator system provides a high-level API for expressing operations in the Relax IR. These operators serve as the interface between frontend importers (like ONNX or PyTorch) and the lower-level compilation pipeline.

 
### Type and Shape Inference

 Relax operators are characterized by their ability to perform compile-time inference. For example, `relax.take` uses `InferTypeTake` to calculate the resulting `TensorType` based on the input data and indices.

 
```

```

 **Sources:** [src/relax/op/tensor/index.cc63-127](https://github.com/apache/tvm/blob/b16cdecb/src/relax/op/tensor/index.cc#L63-L127) [src/relax/op/tensor/index.cc129-135](https://github.com/apache/tvm/blob/b16cdecb/src/relax/op/tensor/index.cc#L129-L135)

 For more information, see [Relax Operators](https://deepwiki.com/apache/tvm/3.3-relax-operators).

 
## TOPI - TVM Operator Inventory

 TOPI is TVM's library of compute declarations and optimized schedules. It provides generic implementations and hardware-specific optimizations.

 
### Dual-Language Implementation

 TOPI operators are typically defined in C++ headers (e.g., `include/tvm/topi/transform.h`) and then exposed to Python via FFI registrations in `src/topi/transform.cc`.

 
 - **Compute Declaration**: Uses `tvm::te::compute` to define the mathematical operation. [include/tvm/topi/transform.h115-141](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/topi/transform.h#L115-L141)
 - **FFI Registration**: Maps C++ functions to the `topi.*` namespace for Python access using `def_packed`. [src/topi/transform.cc43-47](https://github.com/apache/tvm/blob/b16cdecb/src/topi/transform.cc#L43-L47)
 
 
### Reduction and Statistical Logic

 Beyond simple transforms, TOPI includes complex reduction logic (sum, max, prod) and statistical operations (mean, variance).

 
 - **Reduction Logic**: `CommReduce` and `DoCommReduce` handle axis normalization and target shape calculation for commutative reductions. [include/tvm/topi/reduction.h140-169](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/topi/reduction.h#L140-L169)
 - **Statistical Ops**: Operations like `mean` and `variance` are often legalized to a combination of `topi.sum` and `topi.divide`. [python/tvm/relax/transform/legalize_ops/statistical.py85-98](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/legalize_ops/statistical.py#L85-L98)
 
 For details, see [TOPI - TVM Operator Inventory](https://deepwiki.com/apache/tvm/3.2-topi-tvm-operator-inventory).

 **Sources:** [include/tvm/topi/reduction.h1-25](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/topi/reduction.h#L1-L25) [src/topi/reduction.cc1-25](https://github.com/apache/tvm/blob/b16cdecb/src/topi/reduction.cc#L1-L25) [python/tvm/relax/transform/legalize_ops/statistical.py134-179](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/legalize_ops/statistical.py#L134-L179)

 
## Legalization: Connecting Relax to TOPI

 The `LegalizeOps` pass is the primary mechanism that bridges the gap between high-level Relax operators and low-level TOPI implementations.

 
 - **Registration**: Operators register legalization functions using `@register_legalize`. [python/tvm/relax/transform/legalize_ops/linear_algebra.py28](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/legalize_ops/linear_algebra.py#L28-L28)
 - **Transformation**: The legalization function typically calls a TOPI counterpart or a TE-based compute function via `bb.call_te`. [python/tvm/relax/transform/legalize_ops/linear_algebra.py122](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/legalize_ops/linear_algebra.py#L122-L122)
 - **TIR Generation**: `call_te` generates a `call_tir` to a `PrimFunc` derived from the TOPI compute, effectively lowering the high-level op to schedulable TIR. [tests/python/relax/test_transform_legalize_ops_index_linear_algebra.py42-44](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_transform_legalize_ops_index_linear_algebra.py#L42-L44)
 
 **Sources:** [python/tvm/relax/transform/legalize_ops/linear_algebra.py27-28](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/legalize_ops/linear_algebra.py#L27-L28) [python/tvm/relax/transform/legalize_ops/index.py69-78](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/legalize_ops/index.py#L69-L78)

 
## Summary

 TVM's operator libraries provide a layered architecture:

 
 - **Transform Operations**: Fundamental tensor manipulation primitives.
 - **Relax Operators**: High-level semantic operations with type inference.
 - **TOPI**: Performance-oriented compute declarations and schedules.
 - **Legalization**: The link that converts Relax calls into executable TIR via TOPI.
 
 For more information, visit the sub-pages:

 
 - [Transform Operations](https://deepwiki.com/apache/tvm/3.1-transform-operations)
 - [TOPI - TVM Operator Inventory](https://deepwiki.com/apache/tvm/3.2-topi-tvm-operator-inventory)
 - [Relax Operators](https://deepwiki.com/apache/tvm/3.3-relax-operators)
