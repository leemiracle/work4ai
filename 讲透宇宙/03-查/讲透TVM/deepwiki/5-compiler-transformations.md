> 来源: [https://deepwiki.com/apache/tvm/5-compiler-transformations](https://deepwiki.com/apache/tvm/5-compiler-transformations)
> DeepWiki apache/tvm | Last indexed: 31 August 2026 (b16cde

# Compiler Transformations

  Relevant source files 
 - [include/tvm/ir/transform.h](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/ir/transform.h)
 - [include/tvm/relax/transform.h](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/relax/transform.h)
 - [python/tvm/ir/instrument.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/ir/instrument.py)
 - [python/tvm/ir/transform.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/ir/transform.py)
 - [python/tvm/relax/transform/__init__.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/__init__.py)
 - [python/tvm/relax/transform/fuse_transpose_matmul.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/fuse_transpose_matmul.py)
 - [python/tvm/relax/transform/lazy_transform_params.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/lazy_transform_params.py)
 - [python/tvm/relax/transform/transform.py](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/transform.py)
 - [src/ir/transform.cc](https://github.com/apache/tvm/blob/b16cdecb/src/ir/transform.cc)
 - [src/relax/transform/alter_op_impl.cc](https://github.com/apache/tvm/blob/b16cdecb/src/relax/transform/alter_op_impl.cc)
 - [src/relax/transform/decompose_ops.cc](https://github.com/apache/tvm/blob/b16cdecb/src/relax/transform/decompose_ops.cc)
 - [src/relax/transform/eliminate_common_subexpr.cc](https://github.com/apache/tvm/blob/b16cdecb/src/relax/transform/eliminate_common_subexpr.cc)
 - [src/relax/transform/lazy_transform_params.cc](https://github.com/apache/tvm/blob/b16cdecb/src/relax/transform/lazy_transform_params.cc)
 - [src/relax/transform/meta_schedule.cc](https://github.com/apache/tvm/blob/b16cdecb/src/relax/transform/meta_schedule.cc)
 - [tests/python/ir/test_pass_instrument.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/ir/test_pass_instrument.py)
 - [tests/python/relax/test_transform_alter_op_impl.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_transform_alter_op_impl.py)
 - [tests/python/relax/test_transform_cse.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_transform_cse.py)
 - [tests/python/relax/test_transform_decompose_ops.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_transform_decompose_ops.py)
 - [tests/python/relax/test_transform_fuse_transpose_matmul.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_transform_fuse_transpose_matmul.py)
 - [tests/python/relax/test_transform_lazy_transform_params.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_transform_lazy_transform_params.py)
 - [tests/python/relax/test_transform_meta_schedule_apply_database.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_transform_meta_schedule_apply_database.py)
 - [tests/python/relax/test_transform_meta_schedule_tuning.py](https://github.com/apache/tvm/blob/b16cdecb/tests/python/relax/test_transform_meta_schedule_tuning.py)
 
  This page provides an overview of TVM's optimization and transformation infrastructure across different intermediate representation (IR) levels. For detailed information about specific transformation passes, see the child pages:

 
 - [Relax Transformations](https://deepwiki.com/apache/tvm/5.1-relax-transformations) — High-level functional IR optimizations including fusion and memory planning.
 - [TIR Transformations](https://deepwiki.com/apache/tvm/5.2-tir-transformations) — Low-level tensor program optimizations like vectorization and loop unrolling.
 - [Arithmetic Analysis and Simplification](https://deepwiki.com/apache/tvm/5.3-arithmetic-analysis-and-simplification) — Expression simplification and bound analysis subsystems.
 - [MetaSchedule and Auto-Tuning](https://deepwiki.com/apache/tvm/5.4-metaschedule-and-auto-tuning) — Automated search framework for optimizing TIR kernels.
 - [Dataflow Pattern Language](https://deepwiki.com/apache/tvm/5.5-dataflow-pattern-language) — Pattern matching for graph rewriting and BYOC backends.
 
 
## Purpose and Scope

 Compiler transformations in TVM are organized as modular passes that operate on `IRModule` instances. The system is designed to progressively lower high-level functional models into optimized, hardware-specific tensor programs.

 
 - **Unified Pass Infrastructure**: Uses `tvm.transform.Pass` as the base class for all IR variants [python/tvm/ir/transform.py144-148](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/ir/transform.py#L144-L148)
 - **Pass Context**: Managed by `PassContext`, which controls optimization levels, instrumentation, and pass-specific configurations [include/tvm/ir/transform.h80-136](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/ir/transform.h#L80-L136)
 - **Composability**: Passes can be grouped into a `Sequential` pass, resolving dependencies and execution order automatically [python/tvm/ir/transform.py185-203](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/ir/transform.py#L185-L203)
 
 Sources: [include/tvm/ir/transform.h20-55](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/ir/transform.h#L20-L55) [python/tvm/ir/transform.py18-47](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/ir/transform.py#L18-L47) [src/ir/transform.cc20-40](https://github.com/apache/tvm/blob/b16cdecb/src/ir/transform.cc#L20-L40)

 
---

 
## Transformation Layers

 TVM's compilation pipeline involves transformations at multiple IR levels, each corresponding to a distinct abstraction domain:

 
```

```

 Sources: [python/tvm/relax/transform/transform.py19-55](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/transform.py#L19-L55) [include/tvm/relax/transform.h20-100](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/relax/transform.h#L20-L100) [python/tvm/ir/transform.py185-200](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/ir/transform.py#L185-L200)

 
---

 
## Pass Infrastructure Overview

 
### Pass Types and Scope

 
| Pass Type | Target Entity | Base Class | Example |
|---|---|---|---|
| ModulePass | IRModule | transform.ModulePass | DeadCodeElimination |
| FunctionPass | relax.Function | relax.FunctionPass | FuseOps |
| DataflowBlockPass | relax.DataflowBlock | relax.DataflowBlockPass | Local optimizations |

 Sources: [python/tvm/relax/transform/transform.py43-52](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/transform.py#L43-L52) [python/tvm/ir/transform.py174-183](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/ir/transform.py#L174-L183) [include/tvm/relax/transform.h57-74](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/relax/transform.h#L57-L74)

 
### Pass Context and Configuration

 The `PassContext` provides a scoped environment for passes. It maintains an `opt_level` (defaulting to 2) and a `config` map for pass-specific parameters [include/tvm/ir/transform.h80-90](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/ir/transform.h#L80-L90) Users can register custom config options using `RegisterConfigOption` [src/ir/transform.cc177-180](https://github.com/apache/tvm/blob/b16cdecb/src/ir/transform.cc#L177-L180)

 Sources: [src/ir/transform.cc47-88](https://github.com/apache/tvm/blob/b16cdecb/src/ir/transform.cc#L47-L88) [python/tvm/ir/transform.py55-76](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/ir/transform.py#L55-L76)

 
---

 
## Relax Transformations Overview

 Relax transformations focus on graph-level optimizations and the transition to TIR. For details, see [Relax Transformations](https://deepwiki.com/apache/tvm/5.1-relax-transformations).

 
 - **Operator Fusion**: `FuseOps` groups operators, while `FuseOpsByPattern` uses the Dataflow Pattern Language for targeted fusion [python/tvm/relax/transform/transform.py46-47](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/transform.py#L46-L47)
 - **Automatic Differentiation**: The `Gradient` pass performs reverse-mode AD, generating adjoint functions for training [python/tvm/relax/transform/transform.py55-106](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/transform.py#L55-L106)
 - **Memory Planning**: `StaticPlanBlockMemory` reuses buffers based on lifetime analysis to reduce memory footprint [include/tvm/relax/transform.h124-145](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/relax/transform.h#L124-L145)
 - **Structural Simplification**: `CanonicalizeBindings` and `EliminateCommonSubexpr` remove redundant computations and variables [src/relax/transform/eliminate_common_subexpr.cc22-34](https://github.com/apache/tvm/blob/b16cdecb/src/relax/transform/eliminate_common_subexpr.cc#L22-L34)
 - **Lazy Transformation**: `LazyTransformParams` optimizes model weight loading by transforming parameter functions into lazy versions [python/tvm/relax/transform/lazy_transform_params.py112-140](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/lazy_transform_params.py#L112-L140)
 
 Sources: [include/tvm/relax/transform.h76-191](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/relax/transform.h#L76-L191) [python/tvm/relax/transform/__init__.py20-89](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/__init__.py#L20-L89)

 
---

 
## TIR Transformations Overview

 TIR transformations optimize the generated tensor programs for specific hardware targets. For details, see [TIR Transformations](https://deepwiki.com/apache/tvm/5.2-tir-transformations).

 
 - **Loop Optimizations**: Includes `VectorizeLoop`, `UnrollLoop`, and `PeelLoop`.
 - **Memory Management**: `StorageRewrite` optimizes buffer allocation and reuse within a `PrimFunc`.
 - **Layout Transformation**: `AlterOpImpl` replaces `PrimFunc` implementations and inserts necessary layout transformations for i/o buffers [src/relax/transform/alter_op_impl.cc21-25](https://github.com/apache/tvm/blob/b16cdecb/src/relax/transform/alter_op_impl.cc#L21-L25)
 - **Tuning Integration**: `MetaScheduleApplyDatabase` applies tuned schedules from the MetaSchedule database to `PrimFunc` nodes [src/relax/transform/meta_schedule.cc79-100](https://github.com/apache/tvm/blob/b16cdecb/src/relax/transform/meta_schedule.cc#L79-L100)
 
 Sources: [src/relax/transform/alter_op_impl.cc82-100](https://github.com/apache/tvm/blob/b16cdecb/src/relax/transform/alter_op_impl.cc#L82-L100) [src/relax/transform/meta_schedule.cc20-33](https://github.com/apache/tvm/blob/b16cdecb/src/relax/transform/meta_schedule.cc#L20-L33)

 
---

 
## Arithmetic Analysis and Simplification

 The arithmetic subsystem provides the mathematical foundation for most transformations. For details, see [Arithmetic Analysis and Simplification](https://deepwiki.com/apache/tvm/5.3-arithmetic-analysis-and-simplification).

 
 - **Analyzer**: The central interface for simplification and bound inference [include/tvm/arith/analyzer.h30-80](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/arith/analyzer.h#L30-L80)
 - **RewriteSimplifier**: Uses pattern matching to simplify PrimExprs (e.g., `x + 0 -> x`) [src/arith/rewrite_simplify.cc40-60](https://github.com/apache/tvm/blob/b16cdecb/src/arith/rewrite_simplify.cc#L40-L60)
 - **ConstIntBound**: Analyzes the possible range of integer expressions.
 
 Sources: [src/relax/transform/alter_op_impl.cc26-30](https://github.com/apache/tvm/blob/b16cdecb/src/relax/transform/alter_op_impl.cc#L26-L30) [include/tvm/relax/transform.h32-33](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/relax/transform.h#L32-L33)

 
---

 
## Code Mapping: System to Entities

 
```

```

 Sources: [src/ir/transform.cc47-57](https://github.com/apache/tvm/blob/b16cdecb/src/ir/transform.cc#L47-L57) [src/relax/transform/eliminate_common_subexpr.cc93-96](https://github.com/apache/tvm/blob/b16cdecb/src/relax/transform/eliminate_common_subexpr.cc#L93-L96) [python/tvm/relax/transform/lazy_transform_params.py112-120](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/lazy_transform_params.py#L112-L120) [src/relax/transform/meta_schedule.cc38-49](https://github.com/apache/tvm/blob/b16cdecb/src/relax/transform/meta_schedule.cc#L38-L49)

 
---

 
## References

 
 - `Pass` and `PassContext`: [include/tvm/ir/transform.h56-151](https://github.com/apache/tvm/blob/b16cdecb/include/tvm/ir/transform.h#L56-L151)
 - Relax Pass Registry: [python/tvm/relax/transform/transform.py43-52](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/transform.py#L43-L52)
 - CSE Implementation: [src/relax/transform/eliminate_common_subexpr.cc93-194](https://github.com/apache/tvm/blob/b16cdecb/src/relax/transform/eliminate_common_subexpr.cc#L93-L194)
 - Lazy Param Transformation: [python/tvm/relax/transform/lazy_transform_params.py1-200](https://github.com/apache/tvm/blob/b16cdecb/python/tvm/relax/transform/lazy_transform_params.py#L1-L200)
 - MetaSchedule Relax Pass: [src/relax/transform/meta_schedule.cc1-160](https://github.com/apache/tvm/blob/b16cdecb/src/relax/transform/meta_schedule.cc#L1-L160)
 - Layout Alteration: [src/relax/transform/alter_op_impl.cc82-151](https://github.com/apache/tvm/blob/b16cdecb/src/relax/transform/alter_op_impl.cc#L82-L151)
