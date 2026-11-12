> 来源: [https://deepwiki.com/apache/tvm/2-core-irs-and-languages](https://deepwiki.com/apache/tvm/2-core-irs-and-languages)
> DeepWiki apache/tvm | Last indexed: 31 August 2026 (b16cde

# Core IRs and Languages

  Relevant source files 
 - [cmake/utils/Library.cmake](https://github.com/apache/tvm/blob/b16cdecb/cmake/utils/Library.cmake)
 - [include/tvm/ir/attrs.h](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/ir/attrs.h)
 - [include/tvm/ir/expr.h](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/ir/expr.h)
 - [include/tvm/ir/function.h](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/ir/function.h)
 - [include/tvm/ir/module.h](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/ir/module.h)
 - [include/tvm/relax/expr.h](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/relax/expr.h)
 - [python/tvm/ir/__init__.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/ir/__init__.py)
 - [python/tvm/ir/expr.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/ir/expr.py)
 - [python/tvm/ir/function.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/ir/function.py)
 - [python/tvm/ir/module.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/ir/module.py)
 - [python/tvm/ir/type.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/ir/type.py)
 - [python/tvm/relax/expr.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/expr.py)
 - [python/tvm/runtime/_tensor.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/runtime/_tensor.py)
 - [python/tvm/script/highlight.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/script/highlight.py)
 - [src/ir/attrs.cc](https://github.com/apache/tvm/blob/b16cdecb/src/ir/attrs.cc)
 - [src/ir/expr.cc](https://github.com/apache/tvm/blob/b16cdecb/src/ir/expr.cc)
 - [src/ir/function.cc](https://github.com/apache/tvm/blob/b16cdecb/src/ir/function.cc)
 - [src/ir/module.cc](https://github.com/apache/tvm/blob/b16cdecb/src/ir/module.cc)
 - [src/relax/ir/expr.cc](https://github.com/apache/tvm/blob/b16cdecb/src/relax/ir/expr.cc)
 - [src/relax/transform/attach_global_symbol.cc](https://github.com/apache/tvm/blob/b16cdecb/src/relax/transform/attach_global_symbol.cc)
 - [src/s_tir/meta_schedule/task_scheduler/task_scheduler.cc](https://github.com/apache/tvm/blob/b16cdecb/src/s_tir/meta_schedule/task_scheduler/task_scheduler.cc)
 - [tests/python/ir/test_ir_type.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/ir/test_ir_type.py)
 - [tests/python/relax/test_expr.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_expr.py)
 - [tests/python/relax/test_transform_attach_global_symbol.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_transform_attach_global_symbol.py)
 - [tests/python/relax/test_utils.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_utils.py)
 - [tests/python/s_tir/meta_schedule/test_meta_schedule_task_scheduler.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/s_tir/meta_schedule/test_meta_schedule_task_scheduler.py)
 
  
## Purpose and Scope

 TVM implements a multi-level IR architecture designed for deep learning compilation that gradually lowers high-level neural network constructs to low-level hardware-specific code. This page provides a high-level overview of TVM's core Intermediate Representations (IRs) and domain-specific languages (DSLs) used to represent, transform, and generate code for ML workloads.

 The key IRs covered here are:

 
 - **TensorIR (TIR)**: A low-level, loop-oriented tensor intermediate representation for explicit buffer and memory management. [include/tvm/tirx/expr.h](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/tirx/expr.h) [include/tvm/tirx/op.h](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/tirx/op.h)
 - **Relax IR**: A high-level functional dataflow IR designed for modern machine learning workloads, supporting shape and type inference. [include/tvm/relax/expr.h19-30](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/relax/expr.h#L19-L30)
 - **TVMScript**: A Python-embedded DSL enabling writing TVM IR using Python syntax with decorators, context managers, and Python-native constructs. [python/tvm/script/highlight.py29-63](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/script/highlight.py#L29-L63)
 
 This page links to dedicated child pages for technical details on each IR and language:

 
 - TensorIR: [TensorIR (TIR)](https://deepwiki.com/apache/tvm/2.1-tensorir-(tir))
 - Relax IR: [Relax IR](https://deepwiki.com/apache/tvm/2.2-relax-ir)
 - TVMScript: [TVMScript](https://deepwiki.com/apache/tvm/2.3-tvmscript)
 - TIRx: [TIRx — Next-Generation Kernel DSL](https://deepwiki.com/apache/tvm/2.4-tirx-next-generation-kernel-dsl)
 
 
---

 
## IR Hierarchy and Relationships

 TVM employs a layered IR system, enabling systematic lowering from high-level, user-friendly neural network descriptions to optimized low-level tensor operators that can be compiled across diverse hardware backends.

 
### Multi-Level IR Overview

 
```

```

 This diagram shows how:

 
 - **Relax IR** models high-level dataflow graphs with first-class functions. [include/tvm/relax/expr.h425-440](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/relax/expr.h#L425-L440)
 - **TensorIR (TIR)** implements explicit loop nests for kernel definitions and exposes buffer-level memory access. [include/tvm/tirx/expr.h](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/tirx/expr.h)
 - Both IRs are authored and manipulated through dedicated IRBuilders driven by the common TVMScript parser infrastructure. [python/tvm/script/highlight.py29-63](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/script/highlight.py#L29-L63)
 - `relax::Call` nodes may invoke TIR functions via `call_tir` for explicit kernel implementations. [python/tvm/relax/expr.py71-97](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/expr.py#L71-L97)
 
 **Sources:**

 
 - [include/tvm/relax/expr.h19-45](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/relax/expr.h#L19-L45)
 - [src/relax/ir/expr.cc30-45](https://github.com/apache/tvm/blob/b16cdecb/src/relax/ir/expr.cc#L30-L45)
 - [python/tvm/relax/expr.py41-43](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/expr.py#L41-L43)
 - [include/tvm/ir/expr.h21-35](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/ir/expr.h#L21-L35)
 
 
---

 
## Relax IR: High-Level Functional IR

 Relax IR serves as TVM's modern high-level IR designed for machine learning workloads. It blends functional programming with explicit dataflow constructs and structural typing. [include/tvm/relax/expr.h19-30](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/relax/expr.h#L19-L30)

 
### Relax IR Core Components

 
```

```

 Relax IR highlights:

 
 - **Functional programs with first-class functions** (`relax::Function`) support explicit parameters and return types. [include/tvm/relax/expr.h425-440](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/relax/expr.h#L425-L440) [src/relax/ir/expr.cc43](https://github.com/apache/tvm/blob/b16cdecb/src/relax/ir/expr.cc#L43-L43)
 - **Dataflow blocks** mark pure regions suitable for compiler optimizations. Variables defined inside are `relax::DataflowVar` forming single assignment nodes. [include/tvm/relax/expr.h69-78](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/relax/expr.h#L69-L78) [src/relax/ir/expr.cc33](https://github.com/apache/tvm/blob/b16cdecb/src/relax/ir/expr.cc#L33-L33)
 - **Calls** invoke operators or other functions, including TIR primfuncs via `call_tir`. [python/tvm/relax/expr.py71-97](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/expr.py#L71-L97)
 - **Tuple and constants** support structured and literal data. [include/tvm/relax/expr.h40-44](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/relax/expr.h#L40-L44) [include/tvm/relax/expr.h93-109](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/relax/expr.h#L93-L109)
 
 **Sources:**

 
 - [include/tvm/relax/expr.h40-109](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/relax/expr.h#L40-L109)
 - [src/relax/ir/expr.cc30-45](https://github.com/apache/tvm/blob/b16cdecb/src/relax/ir/expr.cc#L30-L45)
 - [python/tvm/relax/expr.py107-130](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/expr.py#L107-L130)
 
 
---

 
## TensorIR (TIR): Low-Level Loop IR

 TensorIR (TIR) is the core low-level IR that expresses tensor computations as explicit nested loops with buffer accesses, forming the basis for code generation and hardware mapping. [include/tvm/tirx/expr.h](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/tirx/expr.h)

 
### TIR Buffer Abstraction

 Buffers model multi-dimensional memory with explicit declaration of shape, strides, and type. The Python API `T.Buffer()` maps to the underlying TIR buffer structures.

 Common memory scopes include `"global"`, `"shared"` for GPU shared memory, `"local"` for registers, and platform-specific scopes. [include/tvm/relax/expr.h118](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/relax/expr.h#L118-L118)

 **Sources:**

 
 - [include/tvm/tirx/expr.h](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/tirx/expr.h)
 - [include/tvm/tirx/op.h](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/tirx/op.h)
 - [src/ir/expr.cc31](https://github.com/apache/tvm/blob/b16cdecb/src/ir/expr.cc#L31-L31)
 
 
---

 
## TVMScript: Python-Embedded DSL

 TVMScript is a Python-embedded DSL providing a familiar syntax for writing TVM IR, covering both TIR and Relax IR. [python/tvm/script/highlight.py29-63](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/script/highlight.py#L29-L63)

 
### TVMScript Architecture

 
```

```

 TVMScript enables:

 
 - Authoring TIR kernels with loop and buffer constructs in Python syntax (`@T.prim_func`). [python/tvm/ir/expr.py94](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/ir/expr.py#L94-L94)
 - Writing Relax functional programs with dataflow blocks and operator calls (`@R.function`). [python/tvm/relax/expr.py107](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/expr.py#L107-L107)
 - Defining multi-function modules (`@I.ir_module`) combining Relax and TIR definitions. [python/tvm/ir/module.py31-32](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/ir/module.py#L31-L32)
 
 **Sources:**

 
 - [python/tvm/script/highlight.py29-63](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/script/highlight.py#L29-L63)
 - [python/tvm/ir/module.py31-41](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/ir/module.py#L31-L41)
 - [python/tvm/relax/expr.py107-130](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/expr.py#L107-L130)
 
 
---

 
## Summary

 TVM's core IR and language infrastructure enables a flexible compilation pipeline:

 
| IR / Language | Purpose | C++ Core Classes | Python API / Decorator | Details Page Link |
|---|---|---|---|---|
| Relax IR | High-level functional IR with dataflow | relax::Function, relax::Call | @R.function, R.call_tir | Relax IR |
| TensorIR (TIR) | Low-level explicit tensor loop IR | tir::PrimFunc, tir::For, tir::Buffer | @T.prim_func, T.Buffer | TensorIR (TIR) |
| TVMScript | Python-embedded DSL for IRs | Internal parser and IRBuilders | @T.prim_func, @R.function, @I.ir_module | TVMScript |
| TIRx | Next-gen hardware kernel DSL | tvm.tirx modules | tvm.tirx | TIRx — Next-Generation Kernel DSL |

 **Sources:**

 
 - [include/tvm/ir/module.h58-72](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/ir/module.h#L58-L72)
 - [include/tvm/relax/expr.h425-440](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/relax/expr.h#L425-L440)
 - [src/ir/module.cc44-61](https://github.com/apache/tvm/blob/b16cdecb/src/ir/module.cc#L44-L61)
 - [python/tvm/ir/__init__.py36-52](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/ir/__init__.py#L36-L52)
