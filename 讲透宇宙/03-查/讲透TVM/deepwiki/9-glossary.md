> 来源: [https://deepwiki.com/apache/tvm/9-glossary](https://deepwiki.com/apache/tvm/9-glossary)
> DeepWiki apache/tvm | Last indexed: 31 August 2026 (b16cde

# Glossary

  Relevant source files 
 - [CONTRIBUTORS.md](https://github.com/apache/tvm/blob/b16cdecb/CONTRIBUTORS.md?plain=1)
 - [cmake/utils/Library.cmake](https://github.com/apache/tvm/blob/b16cdecb/cmake/utils/Library.cmake)
 - [docs/arch/device_target_interactions.rst](https://github.com/apache/tvm/blob/b16cdecb/docs/arch/device_target_interactions.rst)
 - [docs/arch/introduction_to_module_serialization.rst](https://github.com/apache/tvm/blob/b16cdecb/docs/arch/introduction_to_module_serialization.rst)
 - [docs/conf.py](https://github.com/apache/tvm/blob/b16cdecb/docs/conf.py)
 - [docs/deep_dive/relax/tutorials/relax_transformation.py](https://github.com/apache/tvm/blob/b16cdecb/docs/deep_dive/relax/tutorials/relax_transformation.py)
 - [docs/errors.rst](https://github.com/apache/tvm/blob/b16cdecb/docs/errors.rst)
 - [docs/index.rst](https://github.com/apache/tvm/blob/b16cdecb/docs/index.rst)
 - [docs/reference/api/links.rst](https://github.com/apache/tvm/blob/b16cdecb/docs/reference/api/links.rst)
 - [include/tvm/ir/expr.h](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/ir/expr.h)
 - [include/tvm/relax/attrs/nn.h](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/relax/attrs/nn.h)
 - [include/tvm/relax/expr.h](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/relax/expr.h)
 - [include/tvm/relax/transform.h](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/relax/transform.h)
 - [include/tvm/tirx/function.h](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/tirx/function.h)
 - [python/tvm/ir/__init__.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/ir/__init__.py)
 - [python/tvm/ir/expr.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/ir/expr.py)
 - [python/tvm/ir/function.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/ir/function.py)
 - [python/tvm/ir/type.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/ir/type.py)
 - [python/tvm/relax/expr.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/expr.py)
 - [python/tvm/relax/frontend/torch/base_fx_graph_translator.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/frontend/torch/base_fx_graph_translator.py)
 - [python/tvm/relax/frontend/torch/exported_program_translator.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/frontend/torch/exported_program_translator.py)
 - [python/tvm/relax/frontend/torch/fx_translator.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/frontend/torch/fx_translator.py)
 - [python/tvm/relax/op/nn/__init__.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/op/nn/__init__.py)
 - [python/tvm/relax/op/nn/nn.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/op/nn/nn.py)
 - [python/tvm/relax/transform/__init__.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/__init__.py)
 - [python/tvm/relax/transform/fuse_transpose_matmul.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/fuse_transpose_matmul.py)
 - [python/tvm/relax/transform/lazy_transform_params.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/lazy_transform_params.py)
 - [python/tvm/relax/transform/legalize_ops/nn.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/legalize_ops/nn.py)
 - [python/tvm/relax/transform/transform.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/transform.py)
 - [python/tvm/runtime/_tensor.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/runtime/_tensor.py)
 - [src/backend/cuda/codegen/codegen_cuda.cc](https://github.com/apache/tvm/blob/b16cdecb/src/backend/cuda/codegen/codegen_cuda.cc)
 - [src/backend/cuda/runtime/cuda_module.cc](https://github.com/apache/tvm/blob/b16cdecb/src/backend/cuda/runtime/cuda_module.cc)
 - [src/ir/expr.cc](https://github.com/apache/tvm/blob/b16cdecb/src/ir/expr.cc)
 - [src/ir/function.cc](https://github.com/apache/tvm/blob/b16cdecb/src/ir/function.cc)
 - [src/relax/ir/expr.cc](https://github.com/apache/tvm/blob/b16cdecb/src/relax/ir/expr.cc)
 - [src/relax/op/nn/nn.cc](https://github.com/apache/tvm/blob/b16cdecb/src/relax/op/nn/nn.cc)
 - [src/relax/op/nn/nn.h](https://github.com/apache/tvm/blob/b16cdecb/src/relax/op/nn/nn.h)
 - [src/relax/transform/alter_op_impl.cc](https://github.com/apache/tvm/blob/b16cdecb/src/relax/transform/alter_op_impl.cc)
 - [src/relax/transform/eliminate_common_subexpr.cc](https://github.com/apache/tvm/blob/b16cdecb/src/relax/transform/eliminate_common_subexpr.cc)
 - [src/relax/transform/lazy_transform_params.cc](https://github.com/apache/tvm/blob/b16cdecb/src/relax/transform/lazy_transform_params.cc)
 - [src/relax/transform/meta_schedule.cc](https://github.com/apache/tvm/blob/b16cdecb/src/relax/transform/meta_schedule.cc)
 - [src/runtime/metadata.h](https://github.com/apache/tvm/blob/b16cdecb/src/runtime/metadata.h)
 - [src/runtime/thread_storage_scope.h](https://github.com/apache/tvm/blob/b16cdecb/src/runtime/thread_storage_scope.h)
 - [src/s_tir/meta_schedule/task_scheduler/task_scheduler.cc](https://github.com/apache/tvm/blob/b16cdecb/src/s_tir/meta_schedule/task_scheduler/task_scheduler.cc)
 - [src/tirx/ir/exec_scope.cc](https://github.com/apache/tvm/blob/b16cdecb/src/tirx/ir/exec_scope.cc)
 - [src/tirx/transform/split_host_device.cc](https://github.com/apache/tvm/blob/b16cdecb/src/tirx/transform/split_host_device.cc)
 - [tests/cpp/runtime/thread_storage_scope_test.cc](https://github.com/apache/tvm/blob/b16cdecb/tests/cpp/runtime/thread_storage_scope_test.cc)
 - [tests/python/ir/test_ir_type.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/ir/test_ir_type.py)
 - [tests/python/relax/test_expr.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_expr.py)
 - [tests/python/relax/test_frontend_from_exported_program.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_frontend_from_exported_program.py)
 - [tests/python/relax/test_frontend_from_fx.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_frontend_from_fx.py)
 - [tests/python/relax/test_op_nn.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_op_nn.py)
 - [tests/python/relax/test_transform_alter_op_impl.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_transform_alter_op_impl.py)
 - [tests/python/relax/test_transform_cse.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_transform_cse.py)
 - [tests/python/relax/test_transform_fuse_transpose_matmul.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_transform_fuse_transpose_matmul.py)
 - [tests/python/relax/test_transform_lazy_transform_params.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_transform_lazy_transform_params.py)
 - [tests/python/relax/test_transform_legalize_ops_nn.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_transform_legalize_ops_nn.py)
 - [tests/python/relax/test_transform_meta_schedule_apply_database.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_transform_meta_schedule_apply_database.py)
 - [tests/python/relax/test_transform_meta_schedule_tuning.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_transform_meta_schedule_tuning.py)
 - [tests/python/relax/test_utils.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_utils.py)
 - [tests/python/s_tir/meta_schedule/test_meta_schedule_task_scheduler.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/s_tir/meta_schedule/test_meta_schedule_task_scheduler.py)
 - [tests/python/tirx-transform/test_tir_transform_split_host_device.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/tirx-transform/test_tir_transform_split_host_device.py)
 - [tests/python/tirx/codegen/test_codegen_cuda.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/tirx/codegen/test_codegen_cuda.py)
 - [tests/python/tirx/transform/test_transform_lower_tirx.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/tirx/transform/test_transform_lower_tirx.py)
 - [tests/scripts/setup-pytest-env.sh](https://github.com/apache/tvm/blob/b16cdecb/tests/scripts/setup-pytest-env.sh)
 - [tests/scripts/task_python_docs.sh](https://github.com/apache/tvm/blob/b16cdecb/tests/scripts/task_python_docs.sh)
 - [tests/scripts/task_python_unittest.sh](https://github.com/apache/tvm/blob/b16cdecb/tests/scripts/task_python_unittest.sh)
 - [tests/scripts/task_python_unittest_gpuonly.sh](https://github.com/apache/tvm/blob/b16cdecb/tests/scripts/task_python_unittest_gpuonly.sh)
 
  This page provides definitions and technical context for codebase-specific terms, jargon, and domain concepts used throughout the Apache TVM project.

 
## Core Compilation Concepts

 
### IRModule

 The primary container for all intermediate representation (IR) entities in TVM. An `IRModule` can contain multiple functions, including both high-level `Relax` functions and low-level `TIR` `PrimFuncs` [include/tvm/relax/transform.h31-32](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/relax/transform.h#L31-L32) Transformations typically take an `IRModule` as input and return a modified `IRModule` [python/tvm/relax/transform/transform.py62-63](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/transform.py#L62-L63)

 
### Pass / Transformation

 A discrete optimization or analysis step that operates on an `IRModule`. TVM organizes passes into a hierarchy:

 
 - **FunctionPass**: Operates on individual functions within a module [python/tvm/relax/transform/transform.py43-48](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/transform.py#L43-L48)
 - **DataflowBlockPass**: Specialized for `DataflowBlock` structures in Relax [python/tvm/relax/transform/transform.py50-52](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/transform.py#L50-L52)
 - **ModulePass**: Operates on the entire `IRModule` [include/tvm/relax/transform.h43](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/relax/transform.h#L43-L43)
 
 
### Legalization

 The process of converting high-level operators (like `R.nn.conv1d`) into lower-level implementations, typically by expanding them into a series of `TIR` calls or `topi` implementations [python/tvm/relax/transform/legalize_ops/nn.py31-57](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/legalize_ops/nn.py#L31-L57) This is registered via the `register_legalize` decorator [python/tvm/relax/transform/legalize_ops/nn.py31](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/legalize_ops/nn.py#L31-L31)

 **Sources:** [python/tvm/relax/transform/transform.py43-63](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/transform.py#L43-L63) [include/tvm/relax/transform.h31-43](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/relax/transform.h#L31-L43) [python/tvm/relax/transform/legalize_ops/nn.py31-57](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/legalize_ops/nn.py#L31-L57)

 
## Relax (High-level IR)

 
### Dataflow Block

 A specific region within a Relax function where all operations are side-effect-free and can be analyzed using a Directed Acyclic Graph (DAG) [python/tvm/relax/transform/transform.py120-125](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/transform.py#L120-L125) These blocks allow for advanced optimizations like `RewriteDataflowReshape` [include/tvm/relax/transform.h110-122](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/relax/transform.h#L110-L122)

 
### Normalized Form

 A canonical state of Relax IR where expressions are in A-Normal Form (ANF). Normalization ensures that every intermediate result is bound to a variable, simplifying subsequent analysis and transformation passes [include/tvm/relax/transform.h154-160](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/relax/transform.h#L154-L160)

 
### Lambda Lifting

 A transformation that extracts nested functions into the global scope of the `IRModule`, assigning them unique names [include/tvm/relax/transform.h76-81](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/relax/transform.h#L76-L81)

 **Sources:** [python/tvm/relax/transform/transform.py120-125](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/transform.py#L120-L125) [include/tvm/relax/transform.h76-160](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/relax/transform.h#L76-L160)

 
## Code Generation & Backends

 
### Codegen

 The backend process that converts TVM's internal IR into executable code for a specific target (e.g., CUDA, C). The CUDA backend, for example, handles the generation of native GPU kernels [src/backend/cuda/codegen/codegen_cuda.cc1-50](https://github.com/apache/tvm/blob/b16cdecb/src/backend/cuda/codegen/codegen_cuda.cc#L1-L50)

 
### BYOC (Bring Your Own Codegen)

 A framework allowing external libraries or hardware-specific compilers to handle parts of the computation graph. This often involves partitioning the graph into subgraphs that the external backend can execute [python/tvm/relax/transform/transform.py32-34](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/transform.py#L32-L34)

 
### Target

 A description of the hardware and software environment for which code is being compiled. It includes the `TargetKind` (e.g., "llvm", "cuda") and specific attributes like architecture or features [tests/python/relax/test_frontend_from_exported_program.py72](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_frontend_from_exported_program.py#L72-L72)

 **Sources:** [src/backend/cuda/codegen/codegen_cuda.cc1-50](https://github.com/apache/tvm/blob/b16cdecb/src/backend/cuda/codegen/codegen_cuda.cc#L1-L50) [python/tvm/relax/transform/transform.py32-34](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/transform.py#L32-L34) [tests/python/relax/test_frontend_from_exported_program.py72](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_frontend_from_exported_program.py#L72-L72)

 
## Runtime & Infrastructure

 
### Virtual Machine (VM)

 The execution engine for Relax programs. It manages memory, executes instructions, and handles the dispatching of kernels to hardware [tests/python/relax/test_frontend_from_exported_program.py73-74](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_frontend_from_exported_program.py#L73-L74)

 
### Disco

 TVM's distributed runtime framework for multi-GPU and multi-node execution. It handles collective communications and session management for large-scale models [python/tvm/relax/transform/transform.py1-20](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/transform.py#L1-L20)

 
### TVMScript

 A Python-embedded DSL used to represent TVM IR (Relax, TIR, and TIRx) in a human-readable format.

 
 - `R` namespace: Relax [tests/python/relax/test_frontend_from_exported_program.py32](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_frontend_from_exported_program.py#L32-L32)
 - `T` namespace: TIR/TIRx [tests/python/relax/test_frontend_from_exported_program.py33](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_frontend_from_exported_program.py#L33-L33)
 - `I` namespace: IR core [tests/python/relax/test_frontend_from_exported_program.py31](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_frontend_from_exported_program.py#L31-L31)
 
 **Sources:** [tests/python/relax/test_frontend_from_exported_program.py31-74](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_frontend_from_exported_program.py#L31-L74) [python/tvm/relax/transform/transform.py1-20](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/transform.py#L1-L20)

 
---

 
## Technical Mapping: Frontend to IR

 The following diagram illustrates how high-level frontend entities (like PyTorch modules) are mapped to TVM's internal representations through the translation layer.

 **Entity Mapping: PyTorch to Relax**

 
```

```

 **Sources:** [python/tvm/relax/frontend/torch/exported_program_translator.py42-45](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/frontend/torch/exported_program_translator.py#L42-L45) [python/tvm/relax/frontend/torch/fx_translator.py31-37](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/frontend/torch/fx_translator.py#L31-L37) [python/tvm/relax/frontend/torch/base_fx_graph_translator.py37-52](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/frontend/torch/base_fx_graph_translator.py#L37-L52)

 
---

 
## Technical Mapping: Operator Legalization Flow

 This diagram tracks the flow from a high-level Relax operator to a low-level TIR implementation during the legalization pass.

 **Data Flow: Operator Legalization**

 
```

```

 **Sources:** [python/tvm/relax/transform/legalize_ops/nn.py31-57](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/legalize_ops/nn.py#L31-L57) [python/tvm/relax/transform/legalize_ops/common.py28-29](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/legalize_ops/common.py#L28-L29) [include/tvm/relax/transform.h108-109](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/relax/transform.h#L108-L109)

 
---

 
## Common Abbreviations

 
| Abbreviation | Full Term | Context |
|---|---|---|
| TIR | Tensor Intermediate Representation | Low-level loop-based IR include/tvm/relax/transform.h31 |
| TIRx | Next-Gen Kernel DSL | Hardware-native DSL for ML kernels tests/python/relax/test_frontend_from_exported_program.py33 |
| TOPI | TVM Operator Inventory | Library of pre-defined compute patterns python/tvm/relax/transform/legalize_ops/nn.py23 |
| FFI | Foreign Function Interface | Mechanism for cross-language (C++/Python) calls python/tvm/relax/transform/transform.py29-30 |
| ANF | A-Normal Form | Canonical representation for functional IR include/tvm/relax/transform.h155 |
| CSE | Common Subexpression Elimination | Optimization pass to remove redundant computations include/tvm/relax/transform.h185-191 |
| BYOC | Bring Your Own Codegen | External backend integration framework python/tvm/relax/transform/transform.py32-34 |

 **Sources:** [python/tvm/relax/transform/transform.py29-34](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/transform.py#L29-L34) [include/tvm/relax/transform.h31-191](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/relax/transform.h#L31-L191) [python/tvm/relax/transform/legalize_ops/nn.py23-57](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/legalize_ops/nn.py#L23-L57)
