# Device Backends and Native Operations

- aten/src/ATen/native/BatchLinearAlgebra.cpp
- aten/src/ATen/native/cuda/Resize.cpp
- aten/src/ATen/native/cuda/Resize.h
- aten/src/ATen/native/mps/kernels/LinearAlgebra.h
- aten/src/ATen/native/mps/kernels/LinearAlgebra.metal
- aten/src/ATen/native/mps/kernels/ReduceOps.h
- aten/src/ATen/native/mps/kernels/ReduceOps.metal
- aten/src/ATen/native/mps/operations/LinearAlgebra.mm
- aten/src/ATen/native/mps/operations/ReduceOps.mm
- aten/src/ATen/native/native_functions.yaml
- c10/core/CachingDeviceAllocator.h
- c10/cuda/CUDAAllocatorConfig.cpp
- c10/cuda/CUDAAllocatorConfig.h
- c10/cuda/CUDACachingAllocator.cpp
- c10/cuda/CUDACachingAllocator.h
- c10/cuda/CUDAMallocAsyncAllocator.cpp
- c10/metal/common.h
- test/distributed/test_cupy_as_tensor.py
- test/distributions/test_distributions.py
- test/test_cuda.py
- test/test_cuda_expandable_segments.py
- test/test_mps.py
- torch/_C/__init__.pyi.in
- torch/_dynamo/polyfills/__init__.py
- torch/csrc/DeviceAccelerator.cpp
- torch/csrc/cuda/CUDAPluggableAllocator.cpp
- torch/csrc/cuda/CUDAPluggableAllocator.h
- torch/csrc/cuda/Module.cpp
- torch/cuda/__init__.py
- torch/cuda/memory.py
- torch/testing/_internal/common_methods_invocations.py
- torch/testing/_internal/common_mps.py
- torch/testing/_internal/opinfo/definitions/linalg.py

## Purpose and Scope

- The ATen Native Function System for operator registration and dispatch.
- Device Backends (CUDA, MPS, XPU) and their specific implementations.
- Memory Management via caching allocators for various devices.
- High-performance Operations such as BLAS and Attention mechanisms.

- ATen Native Function System — Operator registration, native_functions.yaml , and the dispatcher.
- CUDA Backend — Caching allocator, CUDA graphs, and cuBLAS/cuDNN integration.
- MPS Backend (Metal Performance Shaders) — Metal Performance Shaders and Objective-C++ implementations for Apple hardware.
- XPU Backend (Intel GPU) — Intel GPU support via SYCL and XPUCachingAllocator.
- Attention Mechanisms and Transformers — SDPA, FlexAttention, and FlashAttention integrations.

## ATen Native Function System

`native_functions.yaml`
aten/src/ATen/native/native_functions.yaml 1-50

- Function signatures (e.g., func: _cast_Byte(Tensor self, bool non_blocking=False) -> Tensor ) aten/src/ATen/native/native_functions.yaml 9-10
- Allowed variants (e.g., function , method ) aten/src/ATen/native/native_functions.yaml 43
- Dispatch keys indicating which backend implementations are available or prioritized, such as CompositeExplicitAutograd , CPU , or CUDA aten/src/ATen/native/native_functions.yaml 98-104

`c10::Dispatcher`
`DispatchKey`
`_assert_async`
`_assert_async_cuda`
`_assert_async_mps`
aten/src/ATen/native/native_functions.yaml 150-155

### Operator Routing Architecture

```

```

aten/src/ATen/native/native_functions.yaml 1-160
torch/_C/__init__.pyi.in 31-45

ATen Native Function System

## Device Backends

### CUDA Backend (NVIDIA GPUs)

`CUDACachingAllocator`
`cudaMalloc`
`cudaFree`
c10/cuda/CUDACachingAllocator.cpp 103-127

- Memory management: Block-based pools separate large (>1MB) and small allocations c10/cuda/CUDACachingAllocator.cpp 115-117 It supports expandable_segments to reduce fragmentation via virtual memory APIs c10/cuda/CUDACachingAllocator.cpp 82-88
- Stream safety: The allocator provides a recordStream() function to ensure blocks are not reused before recorded asynchronous work completes c10/cuda/CUDACachingAllocator.cpp 129-133
- CUDA Graph support: The allocator satisfies requests from a graph-private memory pool during capture to ensure baked-in addresses remain valid during replay c10/cuda/CUDACachingAllocator.cpp 136-166
- Python Integration: Functionality is exposed through torch.cuda , including memory monitoring utilities like memory_stats and memory_snapshot torch/cuda/memory.py 33-66

c10/cuda/CUDACachingAllocator.cpp 1-170
torch/cuda/memory.py 103-153
test/test_cuda.py 205-210

### MPS Backend (Apple Silicon Metal Performance Shaders)

- Operation implementations: Native operations like mm and addmm are implemented in Objective-C++ using MPSGraph or custom Metal kernels aten/src/ATen/native/mps/operations/LinearAlgebra.mm 29-51
- Kernel Architecture: Metal kernels are managed via MetalShaderLibrary and launched with specific configurations like GemvConfig aten/src/ATen/native/mps/operations/LinearAlgebra.mm 73-77 aten/src/ATen/native/mps/operations/LinearAlgebra.mm 123-143
- Memory Tracking: The backend includes specialized memory leak detection that compares torch.mps.current_allocated_memory() against driver-level statistics test/test_mps.py 102-127

aten/src/ATen/native/mps/operations/LinearAlgebra.mm 1-184
test/test_mps.py 84-117
torch/testing/_internal/common_mps.py 10-25

### XPU Backend (Intel GPU)

- Infrastructure: Exposed via torch.xpu with specific pool handles for memory management torch/_C/__init__.pyi.in 77
- Integration: Native operations like _assert_async have dedicated XPU dispatch targets ( _assert_async_xpu ) in the operator schema aten/src/ATen/native/native_functions.yaml 155

XPU Backend (Intel GPU)

## Native Operations and BLAS

`Dispatcher`

### Cross-Backend BLAS Dispatch

```

```

aten/src/ATen/native/mps/operations/LinearAlgebra.mm 109-121

aten/src/ATen/native/native_functions.yaml 150-162
aten/src/ATen/native/mps/operations/LinearAlgebra.mm 87-100

## Attention and Transformers

- CUDA: Supports FlashAttention and memory-efficient attention torch/testing/_internal/common_methods_invocations.py 36-38
- MPS: Includes optimized ReduceOps and linear algebra kernels for attention computation aten/src/ATen/native/mps/operations/LinearAlgebra.mm 1-20

Attention Mechanisms and Transformers

## Testing and OpInfo Framework

`OpInfo`
`op_db`
torch/testing/_internal/common_methods_invocations.py 66-102

- Sample Inputs: Operators provide sample_inputs functions (e.g., sample_inputs_svd , sample_inputs_slice ) to generate diverse test cases torch/testing/_internal/opinfo/definitions/linalg.py 83-90 torch/testing/_internal/common_methods_invocations.py 180-185
- Device-Specific Modifiers: Tools like mps_ops_modifier allow the test suite to account for unimplemented or platform-specific failures (e.g., lack of complex number support on certain MPS versions) torch/testing/_internal/common_mps.py 12-25

torch/testing/_internal/common_methods_invocations.py 63-116
torch/testing/_internal/opinfo/definitions/linalg.py 49-61
torch/testing/_internal/common_mps.py 72-85

# Summary Diagram: Device Backends and Dispatcher

```

```

- aten/src/ATen/native/native_functions.yaml 1-104
- c10/cuda/CUDACachingAllocator.cpp 1-141
- torch/cuda/memory.py 103-136
- aten/src/ATen/native/mps/operations/LinearAlgebra.mm 1-190
- test/test_mps.py 178-182
- torch/testing/_internal/common_methods_invocations.py 63-112
- torch/testing/_internal/opinfo/definitions/linalg.py 45-57

###
