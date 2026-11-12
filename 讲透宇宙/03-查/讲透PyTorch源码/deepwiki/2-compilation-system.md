# Compilation System

- test/dynamo/test_aot_autograd.py
- test/dynamo/test_cudagraphs.py
- test/dynamo/test_decorators.py
- test/dynamo/test_dynamic_spec.py
- test/dynamo/test_guard_manager.py
- test/dynamo/test_hooks.py
- test/dynamo/test_structured_trace.py
- test/dynamo/test_utils.py
- test/export/test_torchbind.py
- test/functorch/common_utils.py
- test/functorch/test_ac_logging.py
- test/functorch/test_aotdispatch.py
- test/functorch/test_codegen_backward_epilogue.py
- test/functorch/test_codegen_backward_prologue.py
- test/functorch/test_codegen_dedup.py
- test/functorch/test_codegen_mutation_epilogue.py
- test/functorch/test_codegen_runtime_wrapper.py
- test/functorch/test_leaf_function.py
- test/functorch/test_subclass_codegen.py
- test/fx/test_opaque_infrastructure.py
- test/inductor/test_aot_inductor.py
- test/inductor/test_aot_inductor_arrayref.py
- test/inductor/test_aot_inductor_custom_ops.py
- test/inductor/test_combo_kernels.py
- test/inductor/test_coordinate_descent_tuner.py
- test/inductor/test_inductor_scheduler.py
- test/inductor/test_loop_ordering.py
- test/inductor/test_mix_order_reduction.py
- test/inductor/test_mkldnn_pattern_matcher.py
- test/inductor/test_nested_reduction.py
- test/inductor/test_static_triton_launcher.py
- test/inductor/test_strict_numerics.py
- test/inductor/test_torchinductor.py
- test/inductor/test_torchinductor_codegen_dynamic_shapes.py
- test/inductor/test_torchinductor_opinfo_properties.py
- test/inductor/test_triton_heuristics.py
- test/inductor/test_wrapper_codegen.py
- test/test_dynamic_shapes.py
- torch/_C/_dynamo/guards.pyi
- torch/__init__.py
- torch/_dynamo/__init__.py
- torch/_dynamo/compiled_autograd.py
- torch/_dynamo/config.py
- torch/_dynamo/convert_frame.py
- torch/_dynamo/decorators.py
- torch/_dynamo/eval_frame.py
- torch/_dynamo/external_utils.py
- torch/_dynamo/guards.py
- torch/_dynamo/output_graph.py
- torch/_functorch/_activation_checkpointing/ac_logging_utils.py
- torch/_functorch/_aot_autograd/aot_autograd_result.py
- torch/_functorch/_aot_autograd/collect_metadata_analysis.py
- torch/_functorch/_aot_autograd/frontend_utils.py
- torch/_functorch/_aot_autograd/graph_capture_wrappers.py
- torch/_functorch/_aot_autograd/graph_compile.py
- torch/_functorch/_aot_autograd/input_output_analysis.py
- torch/_functorch/_aot_autograd/runtime_wrappers.py
- torch/_functorch/_aot_autograd/schemas.py
- torch/_functorch/_aot_autograd/subclass_codegen.py
- torch/_functorch/_aot_autograd/subclass_parametrization.py
- torch/_functorch/_aot_autograd/subclass_utils.py
- torch/_functorch/partitioners.py
- torch/_higher_order_ops/invoke_leaf_function.py
- torch/_higher_order_ops/register_hook.py
- torch/_higher_order_ops/schema.py
- torch/_inductor/codegen/common.py
- torch/_inductor/codegen/cpp_wrapper_cpu.py
- torch/_inductor/codegen/cpp_wrapper_cpu_array_ref.py
- torch/_inductor/codegen/cuda/device_op_overrides.py
- torch/_inductor/codegen/simd.py
- torch/_inductor/codegen/triton.py
- torch/_inductor/codegen/triton_combo_kernel.py
- torch/_inductor/codegen/wrapper.py
- torch/_inductor/config.py
- torch/_inductor/graph.py
- torch/_inductor/invert_expr_analysis.py
- torch/_inductor/ir.py
- torch/_inductor/lowering.py
- torch/_inductor/ops_handler.py
- torch/_inductor/runtime/coordinate_descent_tuner.py
- torch/_inductor/runtime/hints.py
- torch/_inductor/runtime/triton_heuristics.py
- torch/_inductor/scheduler.py
- torch/_inductor/tiling_utils.py
- torch/csrc/dynamo/guards.cpp
- torch/csrc/inductor/aoti_runtime/utils.h
- torch/fx/experimental/dynamic_spec.py
- torch/fx/experimental/sym_node.py
- torch/fx/experimental/symbolic_shapes.py
- torch/nested/_internal/nested_tensor.py
- torch/nn/utils/parametrize.py

- TorchDynamo ( TorchDynamo Frontend ) — A Python bytecode analysis and symbolic execution frontend that captures user code into FX graphs.
- torch.export ( torch.export: Static Graph Export ) — A static export mechanism producing portable, fully-traced ExportedProgram artifacts with strict shape/dtype constraints suitable for ahead-of-time deployment.
- AOT Autograd ( AOT Autograd and Functionalization ) — Performs ahead-of-time tracing and functionalization of the joint forward-backward graph enabling optimizations like in-place mutation handling and graph partitioning.
- TorchInductor ( TorchInductor Backend ) — The default compiler backend that lowers FX graphs to an intermediate representation (IR), performs scheduling and fusion, and emits optimized code for GPUs and CPUs (e.g., via Triton, CUTLASS, or C++).

## Compilation Pipeline Flow

```

```

- User code runs under torch.compile or torch.export .
- TorchDynamo intercepts the Python bytecode evaluation ( eval_frame ), using symbolic execution ( InstructionTranslator ) and VariableTracker hierarchy to build an OutputGraph (an FX Graph with side effect tracking).
- torch.export produces a static ExportedProgram using shape environment and fake tensor modes.
- The AOT Autograd layer compiles the joint forward/backward graphs, handling mutable and functionalization transformations torch/_functorch/_aot_autograd/runtime_wrappers.py 1-7
- TorchInductor lowers ATen operators from the FX graph to its IR, schedules and fuses kernels, then generates backend-specific code torch/_inductor/ir.py 189-220

torch/_dynamo/output_graph.py 5-20
torch/_inductor/compile_fx.py 152
torch/_inductor/scheduler.py 104-120
torch/_inductor/ir.py 189-220
torch/_dynamo/guards.py 1-50
torch/_functorch/_aot_autograd/runtime_wrappers.py 1-7

## Entry Points and Decorators

| Entry Point | Purpose | Strictness | Typical Use Cases |
|---|---|---|---|
| @torch.compile | Just-in-time eager-mode compilation | Non-strict, supports graph breaks | Training and inference requiring flexible dynamism |
| torch.export.export() | Static graph export | Strict, no graph breaks allowed | Model serialization and deployment with strict guarantees |

`@torch.compile`
`eval_frame`
`InstructionTranslator`
torch/_dynamo/convert_frame.py 1-20

```

```

test/inductor/test_torchinductor.py 33-40
torch/_dynamo/convert_frame.py 1-20
torch/_dynamo/eval_frame.py 1-20

## Key Data Structures and Concepts

### VariableTracker Hierarchy

`VariableTracker`

| Class | Role | Location |
|---|---|---|
| TensorVariable | Tracks tensor values with metadata like shape and dtype | torch/_dynamo/variables/ |
| NNModuleVariable | Represents torch.nn.Module objects | torch/_dynamo/variables/ |
| SymNodeVariable | Represents symbolic integers for shape tracking | torch/_dynamo/variables/ |

### OutputGraph Structure

`OutputGraph`
`torch.fx.Graph`
torch/_dynamo/output_graph.py 5-20

torch/_dynamo/output_graph.py 5-20
torch/_dynamo/variables/builder.py 55

## Lowering and Scheduling (TorchInductor)

### ATen to Inductor IR

torch/_inductor/ir.py 1-220

- The lowerings registry maps ATen operators to functions producing IR nodes torch/_inductor/lowering.py 127
- Key IR node kinds include TensorBox , View , StorageBox , and Buffer torch/_inductor/ir.py 201-220
- Inductor IR distinguishes between tensors that own storage and those that are views of other storage torch/_inductor/ir.py 210-220

### Scheduling and Fusion

`Scheduler`
torch/_inductor/scheduler.py 104-120

```

```

torch/_inductor/ir.py 189-220
torch/_inductor/lowering.py 127-132
torch/_inductor/scheduler.py 104-120

## Code Generation and Autotuning

- Triton backend : The primary GPU backend, using TritonKernel to emit Python code that is compiled by the Triton compiler torch/_inductor/codegen/triton.py 1-100
- C++ backend : For CPU execution, often using cpp_wrapper to generate C++ code torch/_inductor/config.py 196
- Autotuning : Benchmarks different kernel configurations (e.g., block sizes) to find the most efficient one for the current hardware torch/_inductor/runtime/triton_heuristics.py 178-192

torch/_inductor/codegen/triton.py 1-100
torch/_inductor/runtime/triton_heuristics.py 178-192
torch/_inductor/config.py 196

## Compilation Caching

- FxGraphCache : Caches the result of FX graph compilation torch/_inductor/config.py 109-114
- AutotuneCache : Caches the results of kernel autotuning to avoid re-running benchmarks torch/_inductor/runtime/triton_heuristics.py 55
- PyCodeCache : Stores generated Python wrapper code torch/_inductor/scheduler.py 46

torch/_inductor/config.py 109-114
torch/_inductor/runtime/triton_heuristics.py 55
torch/_inductor/scheduler.py 46

###
