<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cutlass · page 3 Python Interface and DSL · fetched 2026-10-26 -->

# Python Interface and DSL

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [README.md](README.md)
- [include/cutlass/version.h](include/cutlass/version.h)
- [python/CuTeDSL/cutlass/base_dsl/dsl.py](python/CuTeDSL/cutlass/base_dsl/dsl.py)
- [python/CuTeDSL/cutlass/base_dsl/env_manager.py](python/CuTeDSL/cutlass/base_dsl/env_manager.py)
- [python/CuTeDSL/cutlass/base_dsl/runtime/cuda.py](python/CuTeDSL/cutlass/base_dsl/runtime/cuda.py)
- [python/CuTeDSL/cutlass/base_dsl/tvm_ffi_builder/tvm_ffi_builder.py](python/CuTeDSL/cutlass/base_dsl/tvm_ffi_builder/tvm_ffi_builder.py)
- [python/CuTeDSL/cutlass/cute/__init__.py](python/CuTeDSL/cutlass/cute/__init__.py)
- [python/CuTeDSL/cutlass/cute/_tvm_ffi_args_spec_converter.py](python/CuTeDSL/cutlass/cute/_tvm_ffi_args_spec_converter.py)
- [python/CuTeDSL/cutlass/cute/arch/nvvm_wrappers.py](python/CuTeDSL/cutlass/cute/arch/nvvm_wrappers.py)
- [python/CuTeDSL/cutlass/cute/core.py](python/CuTeDSL/cutlass/cute/core.py)
- [python/CuTeDSL/cutlass/cute/runtime.py](python/CuTeDSL/cutlass/cute/runtime.py)
- [python/CuTeDSL/cutlass/cutlass_dsl/cuda_jit_executor.py](python/CuTeDSL/cutlass/cutlass_dsl/cuda_jit_executor.py)
- [python/CuTeDSL/cutlass/jax/primitive.py](python/CuTeDSL/cutlass/jax/primitive.py)
- [python/CuTeDSL/requirements-cu13.txt](python/CuTeDSL/requirements-cu13.txt)
- [python/CuTeDSL/requirements.txt](python/CuTeDSL/requirements.txt)
- [python/cutlass_cppgen/__init__.py](python/cutlass_cppgen/__init__.py)
- [python/setup_cutlass.py](python/setup_cutlass.py)
- [python/setup_library.py](python/setup_library.py)
- [python/setup_pycute.py](python/setup_pycute.py)

</details>



CUTLASS provides two distinct Python interfaces for accessing high-performance CUDA kernels. The **CuTe DSL** (Domain-Specific Language) enables writing custom CUDA kernels directly in Python with performance comparable to hand-tuned C++. The **cutlass_cppgen** package provides a higher-level API for instantiating and running pre-defined CUTLASS operations like GEMM and convolution.

This page provides an overview of the Python ecosystem. For detailed information on specific components, see:
- [CuTe DSL Kernel Authoring](#3.1) — Tutorial on writing CUDA kernels in Python using `@cute.jit` and `@cute.kernel` decorators
- [TVM FFI Integration](#3.2) — Explain TVM FFI backend for reduced host overhead and zero-copy framework integration
- [JIT Compilation and Caching](#3.3) — Document the JIT compilation pipeline from Python AST to MLIR to PTX/CUBIN
- [Runtime Tensor Representation](#3.4) — Explain `_Tensor`, `_Pointer`, and `_FakeTensor` classes for bridging Python to MLIR
- [cutlass_cppgen API Reference](#3.5) — Document the package for generating C++ CUTLASS kernels programmatically
- [Operation Enumeration and Code Generation](#3.6) — Explain the kernel generation pipeline using `generator.py` and `cutlass_library`
- [AOT Export and Framework Integration](#3.7) — Document ahead-of-time (AOT) compilation and export of CuTe DSL kernels
- [CUTLASS Operator API](#3.8) — Document the high-level Python Operator API for finding and executing kernels

## Python Ecosystem Architecture

CUTLASS 4.x introduced a comprehensive Python ecosystem with two primary paths for different use cases:

**Dual-Path Architecture Diagram**

```mermaid
graph LR
    subgraph "Python Development Paths"
        ["DSL_USER"] -- "Custom Kernels" --> ["DSL_CODE"]
        ["CPPGEN_USER"] -- "Pre-built Ops" --> ["CPPGEN_API"]
    end
    
    subgraph "CuTe DSL Path"
        ["DSL_CODE"] -- "@cute.jit" --> ["MLIR_PIPELINE"]
        ["MLIR_PIPELINE"] -- "cutlass_compiler" --> ["JIT_CUBIN"]
        ["JIT_CUBIN"] --> ["DSL_EXEC"]
    end
    
    subgraph "cutlass_cppgen Path"
        ["CPPGEN_API"] -- "Gemm/Conv2d" --> ["EMIT_CPP"]
        ["EMIT_CPP"] -- "NVCC" --> ["CPP_SO"]
        ["CPP_SO"] --> ["CPPGEN_EXEC"]
    end
    
    subgraph "Shared Infrastructure"
        ["DSL_EXEC"] --> ["CUDA_RT"]
        ["CPPGEN_EXEC"] --> ["CUDA_RT"]
        ["CUDA_RT"] -- "cuda-python" --> ["GPU_HW"]
        ["RMM"] -- "Memory Pool" --> ["GPU_HW"]
    end

    style DSL_CODE stroke-dasharray: 5 5
    style CPPGEN_API stroke-dasharray: 5 5
```

Sources: [README.md:27-40](), [python/cutlass_cppgen/__init__.py:136-162](), [python/CuTeDSL/cutlass/cute/core.py:33-56]()

### Key Differences

| Aspect | CuTe DSL | cutlass_cppgen |
|--------|----------|----------------|
| **Use Case** | Custom kernel authoring | Pre-built operation instantiation |
| **Programming Model** | Python-native with decorators | High-level API with builder pattern |
| **Compilation** | JIT via MLIR Pipeline | Ahead-of-time NVCC + caching |
| **Compile Time** | Fast (seconds) | Slower (minutes for large sets) |
| **Flexibility** | Full control over kernel logic | Fixed operation templates |
| **Integration** | Native Python AST manipulation | C++ template emission |

Sources: [README.md:27-40](), [CHANGELOG.md:7-14](), [python/cutlass_cppgen/__init__.py:84-95]()

### Package Organization

The Python interface is distributed across several interoperating packages.

```mermaid
graph TD
    subgraph "Repository Structure"
        ["python/cutlass_library"] -- "Enumeration" --> ["cutlass_library_pkg"]
        ["python/cutlass_cppgen"] -- "C++ Gen" --> ["cutlass_cppgen_pkg"]
        ["python/pycute"] -- "Layouts" --> ["pycute_pkg"]
        ["python/CuTeDSL"] -- "DSL/JIT" --> ["nvidia-cutlass-dsl_pkg"]
    end
    
    subgraph "Dependencies"
        ["nvidia-cutlass-dsl_pkg"] --> ["cuda-python"]
        ["nvidia-cutlass-dsl_pkg"] --> ["cutlass_compiler"]
        ["cutlass_cppgen_pkg"] --> ["cutlass_library_pkg"]
    end
```

Sources: [python/setup_library.py:38-42](), [python/setup_pycute.py:38-42](), [python/setup_cutlass.py:52-74](), [python/CuTeDSL/requirements.txt:3-4]()

## Runtime and Compilation Infrastructure

Both Python paths share common runtime infrastructure built on `cuda-python` bindings and the `cutlass_library` core.

### CUDA Context and Memory Management

Context initialization and memory pooling are handled on-demand to avoid overhead during import.

- **Context Initialization**: The `initialize_cuda_context` function ensures version compatibility between the `cuda-python` package and the system `nvcc` [python/cutlass_cppgen/__init__.py:183-209]().
- **Memory Pool**: Uses **RMM** (RAPIDS Memory Manager) if available to manage device memory, defaulting to a pool size of 1GB to 4GB [python/cutlass_cppgen/__init__.py:100-108](), [python/cutlass_cppgen/__init__.py:149-156]().
- **Device Detection**: The `OptionRegistry` uses `device_cc()` to match kernel configurations to the current hardware's compute capability [python/cutlass_cppgen/__init__.py:125-134]().

Sources: [python/cutlass_cppgen/__init__.py:100-209](), [python/CuTeDSL/cutlass/cute/runtime.py:75-115]()

### Runtime Tensor Representations

The DSL uses specialized runtime classes to bridge Python objects (like PyTorch/JAX tensors) to the MLIR compilation pipeline.

- **`_Pointer`**: Runtime representation of a device pointer, tracking `dtype`, `address_space`, and `assumed_align` [python/CuTeDSL/cutlass/cute/runtime.py:54-98]().
- **`_Tensor`**: Adapter for **DLPack**-compatible tensors. It lazily loads a `DLTensorWrapper` to avoid overhead in the critical path [python/CuTeDSL/cutlass/cute/runtime.py:163-209]().
- **Fake Tensors**: Placeholder objects (`_FakeTensor`, `_FakeCompactTensor`) hold metadata for compilation without requiring real data allocations.

For details, see [Runtime Tensor Representation](#3.4).

## CuTe DSL and JIT Compilation

CuTe DSL is a Python-native language for authoring kernels using CuTe abstractions. It uses a sophisticated compiler stack to lower Python AST to hardware-optimized binaries.

### AST Preprocessing and Control Flow
The DSL transforms Python control flow into structured MLIR operations.
- **Loop Transformation**: `for i in range(...)` is lowered to `scf.for` in MLIR.
- **Yield Generation**: Variables modified within dynamic loops are automatically tracked and yielded to maintain SSA form.
- **Primitives API**: Introduced in 4.7.0, this provides a thin wrapper over **NVVM** operations for low-level SIMT programming when CuTe abstractions are not required [CHANGELOG.md:8-11](), [python/CuTeDSL/cutlass/cute/arch/nvvm_wrappers.py:66-86]().

### TVM FFI Integration
For latency-sensitive applications, CuTe DSL supports **TVM FFI** (Foreign Function Interface). This reduces host overhead by providing an optimized calling path for PyTorch and JAX tensors [CHANGELOG.md:81-83]().

For details, see [CuTe DSL Kernel Authoring](#3.1) and [TVM FFI Integration](#3.2).

## Code Generation with cutlass_cppgen

The `cutlass_cppgen` package allows users to programmatically instantiate and compile C++ CUTLASS kernels.

### Operation Classes
It exposes high-level classes for standard operations:
- **`Gemm`**: Standard matrix multiplication [python/cutlass_cppgen/__init__.py:140]().
- **`Conv2d`**: Forward (`Conv2dFprop`), Dgrad, and Wgrad convolutions [python/cutlass_cppgen/__init__.py:141]().
- **`GroupedGemm`**: Support for multiple GEMM problems in a single kernel launch [python/cutlass_cppgen/__init__.py:142]().

### Compilation and Caching
`cutlass_cppgen` emits C++ code that instantiates CUTLASS templates. These are compiled using NVCC and cached in `compiled_cache.db` [python/cutlass_cppgen/__init__.py:84]().

For details, see [cutlass_cppgen API Reference](#3.5) and [Operation Enumeration and Code Generation](#3.6).

## Version and Compatibility

| Component | Specification |
|-----------|---------------|
| **CUTLASS Version** | 4.7.0 [include/cutlass/version.h:41-43]() |
| **Python Support** | 3.8+ (3.9+ for RMM) [python/cutlass_cppgen/__init__.py:101]() |
| **CUDA Python** | >= 11.8.0 [python/setup_cutlass.py:68]() |
| **Architectures** | Volta (SM70) to Blackwell (SM100/SM120) [README.md:26]() |

Sources: [include/cutlass/version.h:41-52](), [python/setup_cutlass.py:52-74](), [python/CuTeDSL/requirements.txt:3]()

---

