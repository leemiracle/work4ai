# Inference Runtime: NativeRT and AOTInductor

- test/dynamo/test_aot_autograd_cache.py
- test/inductor/test_codecache.py
- test/inductor/test_codegen_triton.py
- test/inductor/test_cudagraph_trees.py
- test/inductor/test_custom_op_out_lowering.py
- test/inductor/test_torchbind.py
- test/inductor/test_torchinductor_dynamic_shapes.py
- test/inductor/test_torchinductor_strided_blocks.py
- torch/_functorch/_aot_autograd/autograd_cache.py
- torch/_functorch/_aot_autograd/codegen.py
- torch/_functorch/_aot_autograd/standalone_runtime.py
- torch/_functorch/_aot_autograd/to_standalone_python.py
- torch/_functorch/aot_autograd.py
- torch/_inductor/codecache.py
- torch/_inductor/codegen/aoti_runtime/interface.cpp
- torch/_inductor/codegen/triton_utils.py
- torch/_inductor/codegen/xpu/compile_utils.py
- torch/_inductor/codegen/xpu/xpu_env.py
- torch/_inductor/compile_fx.py
- torch/_inductor/cudagraph_trees.py
- torch/_inductor/cudagraph_utils.py
- torch/_inductor/output_code.py
- torch/_inductor/runtime/static_triton_launcher.py
- torch/_inductor/test_case.py
- torch/csrc/inductor/aoti_runner/model_container_observer.h
- torch/csrc/inductor/aoti_runner/model_container_runner.cpp
- torch/csrc/inductor/aoti_runner/model_container_runner.h
- torch/csrc/inductor/aoti_runner/model_container_runner_cpu.cpp
- torch/csrc/inductor/aoti_runner/model_container_runner_cpu.h
- torch/csrc/inductor/aoti_runner/model_container_runner_cuda.cpp
- torch/csrc/inductor/aoti_runner/model_container_runner_cuda.h
- torch/csrc/inductor/aoti_runner/model_container_runner_xpu.cpp
- torch/csrc/inductor/aoti_runner/model_container_runner_xpu.h
- torch/csrc/inductor/aoti_runner/pybind.cpp
- torch/csrc/inductor/aoti_runtime/arrayref_tensor.h
- torch/csrc/inductor/aoti_runtime/arrayref_tensor_conversion.h
- torch/csrc/inductor/aoti_runtime/device_utils.h
- torch/csrc/inductor/aoti_runtime/interface.h
- torch/csrc/inductor/aoti_runtime/model_base.h
- torch/csrc/inductor/aoti_runtime/model_container.h
- torch/csrc/inductor/aoti_runtime/scalar_to_tensor.h
- torch/csrc/inductor/aoti_runtime/sycl_runtime_wrappers.h
- torch/csrc/inductor/aoti_runtime/thread_local.h
- torch/csrc/inductor/aoti_torch/shim_common.cpp
- torch/csrc/inductor/aoti_torch/utils.h
- torch/csrc/inductor/array_ref_impl.h
- torch/csrc/inductor/static_launcher/common.h
- torch/csrc/inductor/static_launcher/cuda.cpp
- torch/csrc/inductor/static_launcher/xpu.cpp
- torch/testing/_internal/logging_utils.py
- torch/utils/_indented_buffer.py

`torch.compile`
NativeRT
AOTInductor

## Overview of Runtimes

| Feature | NativeRT | AOTInductor (AOTI) |
|---|---|---|
| Primary Goal | Flexible C++ execution of ExportedProgram | Ahead-of-time compiled deployment |
| Artifact | .pt2 archive (Thrift-based serialization) | Shared Library ( .so / .dll ) |
| Execution Model | Graph-centric Interpreter (Native C++ IR) | Direct machine code / Kernel calls |
| Customization | High (supports dynamic graph manipulation) | Low (optimized for a fixed graph) |
| Dependency | libtorch , NativeRT runtime | Minimal C runtime shim (AOTI Runtime) |

### NativeRT and AOTInductor in the Deployment Flow

`ExportedProgram`
`AOTIModelContainerRunner`

```

```

torch/csrc/inductor/aoti_runner/model_container_runner.h 20-40
torch/_inductor/output_code.py 81-85

## NativeRT: Graph-Centric C++ Inference

`torch.export`
`ExportedProgram`

- Graph IR : A C++ representation of the graph including Node , Value , and Graph entities.
- GraphSignature : Encapsulates the input/output specifications and state requirements of the graph.
- OpKernel Dispatch : A mechanism to route graph nodes to high-performance implementations.
- Serialization : NativeRT leverages the Thrift-based schema for deserializing ExportedProgram artifacts into the runtime's internal structures.

NativeRT Architecture

## AOTInductor: Ahead-of-Time Compiled Deployment

### Compilation and Packaging

`interface.h`
torch/csrc/inductor/aoti_runtime/interface.h 1-50
`AOTInductorModelContainerHandle`
torch/csrc/inductor/aoti_runtime/interface.h 24-25

### Runtime and Model Management

`AOTInductorModelContainer`
`AOTInductorModel`
torch/csrc/inductor/aoti_runtime/model_container.h 93-108
torch/csrc/inductor/aoti_runtime/model_container.h 25-40

```

```

torch/csrc/inductor/aoti_runner/model_container_runner.h 15-30
torch/csrc/inductor/aoti_runtime/model_container.h 93-108
torch/csrc/inductor/aoti_runtime/interface.h 109-121

### C++ Wrappers and Kernel Launching

- CPU/GPU Wrapper : Manages the loading and launching of optimized kernels. AOTI can bundle Triton kernels into the FX graph cache torch/_inductor/codecache.py 141-145
- AOTI Runtime Headers : Includes utilities for tensor conversion and device management, such as arrayref_tensor.h and device_utils.h .

## ExportedProgram Serialization

`ExportedProgram`

- PT2 Archive : The deployment artifact is a ZIP-based archive containing weights and graph metadata torch/_inductor/codecache.py 125-126
- Weights Packaging : AOTI specifically packages weights using Weights and TensorProperties classes torch/_inductor/codecache.py 125
- Caching : AOTI leverages FxGraphCache to avoid redundant compilations of exported graphs torch/_inductor/compile_fx.py 65

ExportedProgram Serialization

torch/_inductor/codecache.py 125-126
torch/_inductor/compile_fx.py 65
torch/_inductor/output_code.py 101-112

###
