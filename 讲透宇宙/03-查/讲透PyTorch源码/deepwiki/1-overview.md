# Overview

- CLAUDE.md
- aten/src/ATen/ExpandUtils.h
- aten/src/ATen/TensorIndexing.cpp
- aten/src/ATen/TensorIndexing.h
- aten/src/ATen/core/CachingHostAllocator.h
- aten/src/ATen/native/Repeat.cpp
- aten/src/ATen/native/Repeat.h
- aten/src/ATen/native/cuda/Repeat.cu
- c10/core/RingBuffer.h
- docs/source/nn.init.md
- docs/source/torch_cuda_memory.md
- pyrefly.toml
- test/distributed/test_c10d_nccl4py.py
- test/distributed/test_watchdog.py
- test/inductor/test_mmdecomp.py
- test/nn/attention/test_fa3.py
- test/nn/attention/test_open_registry.py
- test/nn/test_dropout.py
- test/nn/test_init.py
- test/nn/test_lazy_modules.py
- test/nn/test_load_state_dict.py
- test/nn/test_module_hooks.py
- test/nn/test_parametrization.py
- test/nn/test_pruning.py
- test/profiler/test_cpp_thread.cpp
- test/test_bmm_outer_product.py
- test/test_prims.py
- test/test_proxy_tensor.py
- test/test_public_bindings.py
- test/test_tensor_creation_ops.py
- test/test_testing.py
- test/test_torch.py
- torch/_inductor/decomposition.py
- torch/_native/__init__.py
- torch/_native/ops/__init__.py
- torch/_native/ops/bmm_outer_product/__init__.py
- torch/_native/ops/bmm_outer_product/triton_impl.py
- torch/_native/ops/bmm_outer_product/triton_kernels.py
- torch/_numpy/testing/__init__.py
- torch/_numpy/testing/utils.py
- torch/ao/pruning/_experimental/data_sparsifier/data_norm_sparsifier.py
- torch/ao/pruning/_experimental/data_sparsifier/quantization_utils.py
- torch/ao/pruning/_experimental/pruner/prune_functions.py
- torch/csrc/autograd/python_torch_functions_manual.cpp
- torch/csrc/autograd/python_variable_indexing.cpp
- torch/csrc/autograd/python_variable_indexing.h
- torch/csrc/cuda/memory_snapshot.cpp
- torch/distributed/_watchdog.py
- torch/distributed/nccl4py_backend.py
- torch/nn/init.py
- torch/testing/_internal/common_utils.py
- torch/testing/_utils.py
- torch/utils/__init__.py
- torch/utils/hooks.py
- torch/utils/weak.py

## Purpose and Scope

- Compilation system : Encompasses torch.compile API, TorchDynamo bytecode analysis, AOTAutograd for joint forward-backward graph tracing and functionalization, and the TorchInductor lowering and code generation backend.
- Distributed training : Covers collective communication infrastructure (c10d), the DTensor distributed tensor abstraction with placement and sharding semantics, and sharding-based distributed training via Fully Sharded Data Parallel (FSDP).
- Device backends : Includes implementations for CUDA, Apple MPS, Intel XPU, and the ATen native operation dispatch framework for routing operators to backends.
- Build/Test infrastructure : Describes the repository’s build system (CMake, Python setups), code generation for ATen ops ( torchgen ), testing frameworks including OpInfo for operator coverage, and CI workflows.

Sources:
torch/__init__.py 5-28
torch/testing/_internal/common_utils.py 127-171
CLAUDE.md 44-67

## High-Level Architecture

### Compilation Pipeline: From Python User Code to Optimized Execution

```

```

`torch.compile()`
`TorchDynamo`
`AOTAutograd`
`torch/_inductor/decomposition.py`
torch/_inductor/decomposition.py 65-114

Sources:
torch/_inductor/decomposition.py 114-152
test/test_proxy_tensor.py 31-37
torch/testing/_internal/common_utils.py 122-126

## Core Subsystems

### 1. Compilation and Export Stack

- TorchDynamo : The frontend bytecode interpreter captures Python execution frames. It uses VariableTracker and symbolic execution to build an OutputGraph with runtime guards.
- torch.export : Produces ExportedProgram artifacts with strict symbolic shape constraints using ShapeEnv and SymInt torch/csrc/autograd/python_variable_indexing.cpp 155-160
- AOTAutograd : Ahead-of-time joint tracing of forward and backward passes. It leverages FakeTensorMode for shape/dtype propagation without actual data test/test_proxy_tensor.py 19-25
- TorchInductor : The default backend compiler that lowers FX graphs into tensor IR and applies scheduling for fusion. It manages a large set of decompositions to simplify complex ATen ops torch/_inductor/decomposition.py 114-150

Compilation System

### 2. Device Backends and Native Operations

- ATen native functions : PyTorch’s core operations are routed through the ATen dispatcher. Operations like torch.bmm may have specialized Triton-based overrides for specific shapes like outer products test/test_bmm_outer_product.py 4-9
- CUDA backend : Manages GPU memory via the CUDACachingAllocator . It supports advanced features like CUDA graphs and memory snapshots torch/csrc/cuda/memory_snapshot.cpp
- MPS backend : Supports Apple Silicon GPU devices, implementing native operations and Metal kernels.
- XPU backend : Intel’s GPU backend, including specific allocator pools and launcher logic pyrefly.toml 52-57

Device Backends and Native Operations

### 3. Distributed Training Systems

- c10d : The fundamental collective communication library supporting backends like NCCL and Gloo.
- DTensor : Enables SPMD-style distributed tensors with Shard and Replicate placements torch/testing/_comparison.py 86-93
- FSDP (Fully Sharded Data Parallel) : Implements parameter and optimizer state sharding for large-scale training.
- Pipeline Parallelism : Supports staged model parallelism (e.g., 1F1B , GPipe ).

Distributed Training Systems

## Build and Infrastructure

### Build System and Code Generation

- Build Entrypoints : Build is primarily performed via pip install -e . which triggers CMake and Python-based codegen CLAUDE.md 47-49
- torchgen : Translates native_functions.yaml into C++ dispatch boilerplate.

### Testing Infrastructure

- OpInfo : Drives systematic operator coverage testing across devices and dtypes test/test_testing.py 31-38
- Common Utils : Provides TestCase and run_tests orchestration for the repository torch/testing/_internal/common_utils.py 55-61
- Hardware Classification : Tests are categorized (e.g., GENERIC , ACCELERATOR , CUDA ) to target specific CI shards torch/testing/_internal/common_utils.py 166-172

### Repository Layout and Navigation

| System | Primary Entry Point | Code Areas |
|---|---|---|
| Compilation | torch.compile | torch/_dynamo/ , torch/_inductor/ |
| Testing | run_tests() | test/ , torch/testing/_internal/ |
| Core Ops | torch.ops.aten | aten/src/ATen/native/ |
| Distributed | init_process_group | torch/distributed/ |

- Getting Started: Building, Testing, and Navigating the Repo
- Repository Map and Subprojects (benchmarks, android, caffe2, scripts, third_party)

Sources:
torch/testing/_internal/common_utils.py 1-48
test/test_torch.py 36-57
CLAUDE.md 52-62

###
