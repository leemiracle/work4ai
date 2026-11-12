# Glossary

- aten/src/ATen/cpu/StatelessPhilox4x32.h
- aten/src/ATen/cuda/StatelessPhilox4x32.cuh
- aten/src/ATen/native/DistributionTemplates.h
- aten/src/ATen/native/Itertools.cpp
- aten/src/ATen/native/PhiloxStatelessRNG.cpp
- aten/src/ATen/native/PhiloxStatelessRNG.h
- aten/src/ATen/native/cuda/PhiloxDistribution.cu
- aten/src/ATen/native/cuda/PhiloxKeySplit.cu
- aten/src/ATen/native/tags.yaml
- docs/source/distributed.md
- test/custom_operator/test_inplace_tag.py
- test/distributed/algorithms/ddp_comm_hooks/test_ddp_hooks.py
- test/distributed/test_c10d_common.py
- test/distributed/test_c10d_nccl.py
- test/dynamo/test_aot_autograd.py
- test/dynamo/test_dicts.py
- test/dynamo/test_error_messages.py
- test/dynamo/test_generator.py
- test/dynamo/test_hooks.py
- test/dynamo/test_misc.py
- test/dynamo/test_reorder_logs.py
- test/dynamo/test_sequence_ops.py
- test/dynamo/test_sets.py
- test/dynamo/test_structured_trace.py
- test/dynamo/test_utils.py
- test/expect/HasDecompTest.test_aten_core_operators.expect
- test/expect/HasDecompTest.test_has_decomposition.expect
- test/export/test_torchbind.py
- test/functorch/common_utils.py
- test/functorch/test_ac_logging.py
- test/functorch/test_aotdispatch.py
- test/functorch/test_codegen_backward_epilogue.py
- test/functorch/test_codegen_backward_prologue.py
- test/functorch/test_codegen_dedup.py
- test/functorch/test_codegen_mutation_epilogue.py
- test/functorch/test_codegen_runtime_wrapper.py
- test/functorch/test_subclass_codegen.py
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
- test/test_decomp.py
- test/test_meta.py
- test/test_stateless_rng.py
- torch/_C/_distributed_c10d.pyi
- torch/_decomp/decompositions.py
- torch/_dynamo/compiled_autograd.py
- torch/_dynamo/exc.py
- torch/_dynamo/external_utils.py
- torch/_dynamo/graph_break_registry.json
- torch/_dynamo/side_effects.py
- torch/_dynamo/symbolic_convert.py
- torch/_dynamo/trace_rules.py
- torch/_dynamo/utils.py
- torch/_dynamo/variables/__init__.py
- torch/_dynamo/variables/base.py
- torch/_dynamo/variables/builder.py
- torch/_dynamo/variables/builtin.py
- torch/_dynamo/variables/constant.py
- torch/_dynamo/variables/dicts.py
- torch/_dynamo/variables/functions.py
- torch/_dynamo/variables/lists.py
- torch/_dynamo/variables/misc.py
- torch/_dynamo/variables/nn_module.py
- torch/_dynamo/variables/object_protocol.py
- torch/_dynamo/variables/sets.py
- torch/_dynamo/variables/tensor.py
- torch/_dynamo/variables/torch.py
- torch/_dynamo/variables/user_defined.py
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
- torch/_higher_order_ops/register_hook.py
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
- torch/_meta_registrations.py
- torch/csrc/distributed/c10d/Backend.hpp
- torch/csrc/distributed/c10d/Ops.cpp
- torch/csrc/distributed/c10d/ProcessGroup.hpp
- torch/csrc/distributed/c10d/ProcessGroupNCCL.cpp
- torch/csrc/distributed/c10d/ProcessGroupNCCL.hpp
- torch/csrc/distributed/c10d/init.cpp
- torch/csrc/inductor/aoti_runtime/utils.h
- torch/distributed/algorithms/ddp_comm_hooks/quantization_hooks.py
- torch/distributed/distributed_c10d.py
- torch/func/_random.py
- torch/nn/utils/parametrize.py
- torch/testing/_internal/common_distributed.py
- torchgen/model.py
- torchgen/native_function_generation.py

## Compilation Pipeline Terms

### TorchDynamo & Tracing

- Frame Evaluation : The process where TorchDynamo intercepts Python's frame execution using the eval_frame / set_eval_frame API to perform symbolic analysis and produce an FX graph torch/_dynamo/eval_frame.py 50
- InstructionTranslator : The symbolic execution engine that iterates through Python bytecode and converts it into symbolic actions to construct the OutputGraph torch/_dynamo/symbolic_convert.py 1-20
- VariableTracker : An abstraction used during symbolic execution to represent Python objects (tensors, lists, dicts) and track their properties and mutations torch/_dynamo/variables/base.py 108-119
- VariableBuilder : A utility class that converts Python values into VariableTracker instances, handling source tracking and guard installation torch/_dynamo/variables/builder.py 8-17
- Guard : A condition that must remain true for a previously compiled graph to be valid. Guards are managed by GuardManager and hierarchical checks torch/_C/_dynamo/guards.pyi 1-15
- Graph Break : A point where TorchDynamo cannot symbolically trace a Python construct, forcing a fallback to the Python interpreter and ending the current FX graph test/dynamo/test_misc.py 228-232

### TorchInductor & Lowering

- Lowering : The process of converting high-level ATen operators into Inductor's Intermediate Representation (IR) via the lowerings registry torch/_inductor/lowering.py 127-129
- TensorBox : The top-level IR construct representing a torch.Tensor . It can wrap a View , StorageBox , or Buffer to model metadata vs. storage torch/_inductor/ir.py 187-207
- StorageBox : An IR layer that introduces the concept of a Layout (size, stride, offset) over a 1D Buffer torch/_inductor/ir.py 210-213
- SchedulerNode : A wrapper around IR nodes (e.g., ComputedBuffer ) used by the scheduler to determine fusion groups and execution order torch/_inductor/scheduler.py 65-72
- Pointwise Fusion : Combining multiple element-wise operations into a single kernel to reduce memory bandwidth overhead torch/_inductor/scheduler.py 26-27
- Triton : The default GPU code generation backend for Inductor, producing high-performance Python-based kernels torch/_inductor/codegen/triton.py 1-20

### Symbolic Execution Data Flow

Dynamo Symbolic Tracing Flow

```

```

torch/_dynamo/eval_frame.py 50
torch/_dynamo/variables/builder.py 8-17
torch/_dynamo/variables/base.py 108-119
torch/_dynamo/symbolic_convert.py 1-20
torch/_dynamo/output_graph.py 116-121

## Distributed Training Concepts

- c10d : The core library providing collective communication primitives (AllReduce, Broadcast, etc.) for distributed training torch/distributed/distributed_c10d.py 1-50
- ProcessGroup : An abstraction for a set of ranks that can perform collective operations. Common backends include NCCL and Gloo torch/csrc/distributed/c10d/ProcessGroupNCCL.cpp 1-50
- DTensor (Distributed Tensor) : A tensor abstraction that describes how data is partitioned across a DeviceMesh using Placement types like Shard or Replicate .
- DeviceMesh : A multi-dimensional grid of devices used to define the topology for sharding and collective communication.
- Symmetric Memory : A high-performance memory access pattern enabling direct GPU-to-GPU memory access torch/_inductor/scheduler.py 67-70
- FSDP (Fully Sharded Data Parallel) : A strategy that shards parameters, gradients, and optimizer states across ranks to save memory.

## ATen and Device Internals

- Native Function : An operator defined in native_functions.yaml that maps to a C++ implementation aten/src/ATen/native/native_functions.yaml 1-50
- Dispatch Key : A mechanism (e.g., CUDA , Autograd , XPU ) used by the PyTorch dispatcher to route an operator call to the correct implementation torch/_inductor/lowering.py 35-47
- CUDACachingAllocator : PyTorch's custom memory allocator for CUDA that reduces the overhead of cudaMalloc by maintaining a pool of reusable blocks.
- FakeTensor : A tensor that carries metadata (shape, dtype, device) but no actual data. Used during compilation to predict shapes without executing computation torch/_inductor/ir.py 75-80
- SymInt : A symbolic integer type used to represent dynamic dimensions in the ShapeEnv torch/_inductor/ir.py 68-79

### ATen Dispatch Flow

Operator Dispatch Logic

```

```

torch/_inductor/lowering.py 127-131
torch/_inductor/ir.py 187-207
aten/src/ATen/native/native_functions.yaml 1-10

## Infrastructure and Build Terms

- OpInfo : A metadata structure used in the testing suite to define operator behavior, valid dtypes, and sample inputs torch/testing/_internal/common_methods_invocations.py 92-94
- AOTInductor (AOTI) : A mode of Inductor that compiles a model into a standalone shared library for deployment in non-Python environments test/inductor/test_aot_inductor.py 1-20
- AOTI C Shim : A stable C ABI wrapper around compiled Inductor artifacts for integration with C++ runtimes torch/_inductor/config.py 196-198

| Term | Definition | Primary File/Location |
|---|---|---|
| Autotune | Benchmarking different kernel configurations (block sizes, etc.) to find the fastest implementation. | torch/_inductor/runtime/triton_heuristics.py 164-165 |
| Functionalization | The process of removing in-place operations and views from a graph, replacing them with functional equivalents. | torch/_inductor/lowering.py 26-29 |
| Decomposition | Breaking down complex ATen ops into simpler primitives (e.g., addmm into mm and add ). | torch/_inductor/lowering.py 69 |
| Inductor IR | The internal representation used by Inductor (TensorBox, StorageBox, Buffer). | torch/_inductor/ir.py 189-207 |
| ShapeEnv | The environment that tracks symbolic shapes and constraints during compilation. | torch/_inductor/ir.py 68-79 |

torch/_inductor/runtime/triton_heuristics.py 164-165
torch/_inductor/lowering.py 69
torch/_inductor/ir.py 189-207
torch/_inductor/config.py 109-114

###
