# Code Generation and Operator Authoring

- aten/src/ATen/core/boxing/BoxedKernel.h
- aten/src/ATen/core/boxing/BoxedKernel_impl.h
- aten/src/ATen/core/boxing/KernelFunction.h
- aten/src/ATen/core/boxing/KernelFunction_impl.h
- aten/src/ATen/core/dispatch/DispatchKeyExtractor.h
- aten/src/ATen/core/dispatch/Dispatcher.h
- aten/src/ATen/cpu/StatelessPhilox4x32.h
- aten/src/ATen/cuda/StatelessPhilox4x32.cuh
- aten/src/ATen/native/DistributionTemplates.h
- aten/src/ATen/native/Itertools.cpp
- aten/src/ATen/native/PhiloxStatelessRNG.cpp
- aten/src/ATen/native/PhiloxStatelessRNG.h
- aten/src/ATen/native/cuda/PhiloxDistribution.cu
- aten/src/ATen/native/cuda/PhiloxKeySplit.cu
- aten/src/ATen/native/tags.yaml
- c10/core/impl/LocalDispatchKeySet.cpp
- c10/core/impl/LocalDispatchKeySet.h
- test/custom_operator/test_inplace_tag.py
- test/expect/HasDecompTest.test_aten_core_operators.expect
- test/expect/HasDecompTest.test_has_decomposition.expect
- test/test_custom_ops.py
- test/test_decomp.py
- test/test_meta.py
- test/test_python_dispatch.py
- test/test_stateless_rng.py
- torch/_decomp/decompositions.py
- torch/_inductor/runtime/debug_utils.py
- torch/_library/autograd.py
- torch/_library/custom_ops.py
- torch/_library/fake_impl.py
- torch/_meta_registrations.py
- torch/_ops.py
- torch/_strobelight/cli_function_profiler.py
- torch/csrc/utils/python_dispatch.cpp
- torch/func/_random.py
- torch/library.py
- torchgen/model.py
- torchgen/native_function_generation.py

`torchgen`
`torch.library`

## torchgen: ATen Code Generator

`torchgen`
`native_functions.yaml`

- C++ Dispatcher Boilerplate : Code that routes calls from the at:: namespace to specific backend implementations like CPU, CUDA, or XPU via the c10::Dispatcher aten/src/ATen/core/dispatch/Dispatcher.h 1-50
- Functionalization and Decompositions : Generation of functional versions of in-place and view operations to support AOTAutograd, and the registration of Python-based decompositions torch/_decomp/decompositions.py 125-150 torch/_meta_registrations.py 66-76
- NativeFunction Model : A rich Python object model used during generation to represent operator properties like aliasing, mutability, and dispatch keys torchgen/model.py 1-100 torchgen/native_function_generation.py 1-30
- C Shims : Automatic generation of stable C interfaces for ATen ops, used by AOTInductor to bridge the gap between compiled artifacts and C++ execution.

`NativeFunction`
torchgen: ATen Code Generator

torchgen/model.py 1-100
torchgen/native_function_generation.py 1-30
torch/_decomp/decompositions.py 1-50
torch/_meta_registrations.py 1-80
aten/src/ATen/core/dispatch/Dispatcher.h 1-50

## Custom Operators and Library Extension

`torch.library`
`FakeTensor`

- @custom_op : A high-level decorator for defining new operators in Python with support for schema inference and mutation tracking torch/_library/custom_ops.py 67-130 torch/library.py 40
- register_fake / register_meta : Essential for providing meta-functions that allow torch.compile and FakeTensorMode to reason about output shapes and dtypes without executing the kernel torch/library.py 35 torch/_meta_registrations.py 66-76
- Schema Inference : Tools to automatically derive operator schemas from Python function signatures and type hints torch/library.py 22 torch/_library/custom_ops.py 132-138
- Autograd Integration : Mechanics for registering backward formulas that hook into PyTorch's autograd.Function logic torch/_library/autograd.py 24-50 torch/_library/autograd.py 132-150
- Validation : Utilities to ensure custom operators correctly implement aliasing and mutation rules as defined in their schema torch/library.py 67-149 test/test_custom_ops.py 214-219

Custom Operators and Library Extension

torch/library.py 1-176
torch/_library/custom_ops.py 67-173
torch/_library/autograd.py 24-150
torch/_meta_registrations.py 116-173
test/test_custom_ops.py 1-219

## AOTI C Shim and Stable ABI

LibTorch Stable ABI
AOTInductor C Shim

### The Shim Architecture

```

```

torch/csrc/utils/python_dispatch.cpp 87-104
torch/csrc/utils/python_dispatch.cpp 173-184
torch/_library/custom_ops.py 77-113

### Key Components

- Python Kernel Dispatch : The PythonKernelHolder class manages the transition from the C++ dispatcher back into Python-defined kernels or through to C shims torch/csrc/utils/python_dispatch.cpp 87-117
- Stable Representation : Using SafePyObject and IValue stacks to maintain state across different interpreter boundaries torch/csrc/utils/python_dispatch.cpp 15-20 torch/csrc/utils/python_dispatch.cpp 173-177
- Stateless RNG : Specialized handling for random number generation to ensure consistency across different backends and compilation modes torch/func/_random.py 1-20 test/test_stateless_rng.py 40-60

| Component | Responsibility | Code Entity |
|---|---|---|
| Schema | Defines Op Signature | torch.library.define torch/library.py 31 |
| Meta/Fake | Shape/Dtype Prop | torch.library.register_fake torch/library.py 35 |
| Autograd | Backward Formula | make_autograd_impl torch/_library/autograd.py 24 |
| Dispatch | Backend Routing | c10::Dispatcher aten/src/ATen/core/dispatch/Dispatcher.h 10 |

torch/csrc/utils/python_dispatch.cpp 1-184
torch/library.py 1-44
torch/_library/autograd.py 1-150
torch/func/_random.py 1-50

AOTI C Shim and Stable ABI

Child Pages:

- torchgen: ATen Code Generator
- Custom Operators and Library Extension
- AOTI C Shim and Stable ABI

###
