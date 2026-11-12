<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvmath-python · page 3 Architecture Overview · fetched 2026-10-26 -->

# Architecture Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [builder/__init__.py](builder/__init__.py)
- [builder/utils.py](builder/utils.py)

</details>



## Purpose and Scope

This document provides a high-level overview of nvmath-python's internal architecture, explaining how the library bridges Python code to NVIDIA's native CUDA math libraries through a carefully designed layered system. It covers the overall design philosophy, the three-tier API architecture, the Python bindings layer, framework integration patterns, and the build system.

For detailed information about specific topics:
- API category usage patterns and selection criteria: see [API Categories](#3.1)
- Python bindings implementation details: see [Python Bindings Layer](#3.2)
- Host API usage: see [Host APIs](#4)
- Device API usage: see [Device APIs](#5)
- Distributed API usage: see [Distributed APIs](#6)

---

## High-Level Layered Architecture

nvmath-python is structured as a multi-layered architecture that separates concerns between Python API presentation, bindings management, and native library access.

### Overall System Layers

```mermaid
graph TB
    subgraph "User Layer"
        NUMPY["NumPy Arrays"]
        CUPY["CuPy Arrays"]
        TORCH["PyTorch Tensors"]
        NUMBA["Numba CUDA Kernels"]
    end
    
    subgraph "Python API Layer - nvmath.*"
        HOST_API["Host APIs<br/>nvmath.linalg.advanced<br/>nvmath.fft"]
        DEVICE_API["Device APIs<br/>nvmath.device.fft"]
        DIST_API["Distributed APIs<br/>nvmath.distributed"]
    end
    
    subgraph "Python Bindings Layer - nvmath.bindings.*"
        BIND_CUBLAS["nvmath.bindings.cublas<br/>nvmath.bindings.cublasLt<br/>nvmath.bindings.cublasMp"]
        BIND_CUFFT["nvmath.bindings.cufft<br/>nvmath.bindings.cufftMp"]
        BIND_OTHER["nvmath.bindings.cudss<br/>nvmath.bindings.cusparse<br/>etc."]
    end
    
    subgraph "Cython Compilation Layer"
        PYX["*.pyx files<br/>Cython implementations"]
        PXD["*.pxd files<br/>Cython headers"]
        BUILDER["builder/utils.py<br/>detect_cuda_paths()"]
    end
    
    subgraph "NVIDIA CUDA Libraries"
        CUBLAS_LIB["libcublas.so<br/>libcublasLt.so<br/>libcublasMp.so"]
        CUFFT_LIB["libcufft.so<br/>libcufftMp.so"]
        OTHER_LIB["libcudss.so<br/>libcusparse.so<br/>libnvshmem.so"]
    end
    
    NUMPY --> HOST_API
    CUPY --> HOST_API
    TORCH --> HOST_API
    NUMBA --> DEVICE_API
    
    HOST_API --> BIND_CUBLAS
    HOST_API --> BIND_CUFFT
    DEVICE_API --> BIND_CUFFT
    DIST_API --> BIND_CUFFT
    DIST_API --> BIND_CUBLAS
    
    BIND_CUBLAS --> PYX
    BIND_CUFFT --> PYX
    BIND_OTHER --> PYX
    
    PYX --> BUILDER
    PXD --> BUILDER
    
    BUILDER --> CUBLAS_LIB
    BUILDER --> CUFFT_LIB
    BUILDER --> OTHER_LIB
```

**Sources:** [README.md:1-208](), [builder/utils.py:12-52](), [builder/utils.py:55-75]()

The architecture consists of five distinct layers:

| Layer | Purpose | Key Components |
|-------|---------|----------------|
| **User Layer** | Framework integration | NumPy, CuPy, PyTorch tensors/arrays; Numba kernels |
| **Python API Layer** | High-level Pythonic APIs | `nvmath.linalg.advanced`, `nvmath.fft`, `nvmath.device`, `nvmath.distributed` |
| **Python Bindings Layer** | Low-level library wrapping | `nvmath.bindings.cublas`, `nvmath.bindings.cufft`, etc. |
| **Cython Compilation Layer** | C/Python bridge | `.pyx` implementation files, `.pxd` header files, build utilities |
| **NVIDIA CUDA Libraries** | Native GPU acceleration | `libcublas.so`, `libcufft.so`, `libcudss.so`, etc. |

---

## Three-Tier API Architecture

nvmath-python organizes its functionality into three distinct API categories, each targeting different execution models and use cases.

### API Category Relationships

```mermaid
graph TB
    subgraph "Host APIs - nvmath.linalg.advanced, nvmath.fft"
        MATMUL["nvmath.linalg.advanced.Matmul<br/>Stateful matrix operations"]
        FFT_HOST["nvmath.fft.fft/ifft<br/>FFT with custom epilogs"]
        COMPILE["nvmath.fft.compile_epilog<br/>LTO-IR compilation"]
    end
    
    subgraph "Device APIs - nvmath.device"
        FFT_DEVICE["nvmath.device.fft<br/>Returns callable descriptor"]
        DEVICE_DESC["FFT descriptor attributes:<br/>storage_size, block_dim,<br/>shared_memory_size, stride"]
    end
    
    subgraph "Distributed APIs - nvmath.distributed"
        DIST_INIT["nvmath.distributed.initialize<br/>MPI + NVSHMEM setup"]
        DIST_FFT["nvmath.distributed.fft.fft/ifft<br/>Multi-node operations"]
        DIST_MEM["nvmath.distributed.allocate_symmetric_memory<br/>NVSHMEM heap allocation"]
    end
    
    subgraph "Common Binding Infrastructure"
        CUBLAS_BIND["nvmath.bindings.cublas<br/>nvmath.bindings.cublasLt"]
        CUFFT_BIND["nvmath.bindings.cufft"]
        CUFFTMP_BIND["nvmath.bindings.cufftMp"]
    end
    
    MATMUL --> CUBLAS_BIND
    FFT_HOST --> CUFFT_BIND
    COMPILE --> CUFFT_BIND
    
    FFT_DEVICE --> CUFFT_BIND
    DEVICE_DESC --> FFT_DEVICE
    
    DIST_INIT --> CUFFTMP_BIND
    DIST_FFT --> CUFFTMP_BIND
    DIST_MEM --> CUFFTMP_BIND
```

**Sources:** [README.md:20-215]()

### API Category Characteristics

| API Category | Execution Context | Memory Model | Primary Use Case | Example |
|--------------|------------------|--------------|------------------|---------|
| **Host APIs** | Called from Python, executes on CPU/GPU | Standard array/tensor memory | High-level operations with full control | `nvmath.linalg.advanced.Matmul` |
| **Device APIs** | Called from CUDA kernels, executes on GPU | Thread-local and shared memory | Custom kernel integration | `nvmath.device.fft` in `@cuda.jit` |
| **Distributed APIs** | Called from Python, executes across nodes | NVSHMEM symmetric heap | Multi-node, multi-GPU computing | `nvmath.distributed.fft.fft` |

Each API category builds on the same Python bindings layer but exposes different programming models to address specific execution requirements. See [API Categories](#3.1) for detailed usage guidance.

**Sources:** [README.md:20-215]()

---

## Python Bindings Layer Structure

The Python bindings layer uses Cython to wrap NVIDIA's native CUDA libraries, exposing their functionality to Python with minimal overhead.

### Binding Module Organization

```mermaid
graph LR
    subgraph "nvmath.bindings Package Structure"
        CUBLAS["cublas<br/>~400 functions<br/>Basic BLAS operations"]
        CUBLASLT["cublasLt<br/>Advanced GEMM<br/>Algorithm selection"]
        CUBLASMP["cublasMp<br/>Distributed GEMM<br/>Multi-GPU operations"]
        CUFFT["cufft<br/>FFT planning & execution<br/>Multiple precisions"]
        CUDSS["cudss<br/>Direct sparse solvers<br/>Factorization methods"]
        CUSPARSE["cusparse<br/>Sparse matrix operations"]
        CURAND["curand<br/>Random number generation"]
    end
    
    subgraph "Cython Source Files"
        PYX_FILES["*.pyx files<br/>Implementation"]
        PXD_FILES["*.pxd files<br/>Type declarations"]
    end
    
    subgraph "Native Libraries"
        SO_FILES["*.so files<br/>CUDA libraries"]
    end
    
    CUBLAS --> PYX_FILES
    CUBLASLT --> PYX_FILES
    CUBLASMP --> PYX_FILES
    CUFFT --> PYX_FILES
    CUDSS --> PYX_FILES
    CUSPARSE --> PYX_FILES
    CURAND --> PYX_FILES
    
    PYX_FILES --> PXD_FILES
    PYX_FILES --> SO_FILES
```

**Sources:** [builder/utils.py:55-75]()

Each binding module follows a consistent pattern:

1. **Cython Implementation (`.pyx`)**: Contains the actual wrapping code that bridges Python and C.
2. **Cython Header (`.pxd`)**: Declares C types, functions, and constants for Cython compilation.
3. **Python Module**: Exposes enumerations, constants, and wrapper functions to Python.

The bindings provide direct function mappings, enumeration classes representing CUDA library enums, and automatic error checking via status code validation.

**Sources:** [builder/utils.py:55-75]()

---

## Build System and CUDA Path Detection

The build system manages the complex task of detecting CUDA installations, configuring compilation flags, and linking against CUDA libraries across different deployment scenarios.

### Build Process Flow

```mermaid
graph TD
    START["Build initiated:<br/>pip install nvmath-python"]
    
    DETECT["builder/utils.py:detect_cuda_paths<br/>Search for CUDA headers"]
    
    subgraph "CUDA Path Search Order"
        WHEEL["sys.path entries:<br/>nvidia/cu13<br/>nvidia/cuda_profiler_api"]
        ENV["Environment variables:<br/>CUDA_PATH<br/>CUDA_HOME"]
        DEFAULT["/usr/local/cuda"]
    end
    
    CHECK["Verify cuda.h,<br/>crt/host_defines.h,<br/>cudaProfiler.h exist"]
    
    PREP["builder/utils.py:_prep_includes_libs_rpaths<br/>Configure includes and rpaths"]
    
    DECIDE["builder/utils.py:decide_lib_name<br/>Determine target library"]
    
    subgraph "Per-Extension Configuration"
        INCLUDES["Set include_dirs:<br/>CUDA header paths"]
        LINKER["Set extra_link_args:<br/>-Wl,--disable-new-dtags<br/>-rpath settings"]
        STRIP["Add -Wl,--strip-all<br/>for wheel builds"]
    end
    
    CYTHON["Cython compilation:<br/>*.pyx -> *.c -> *.so"]
    
    PARALLEL["Parallel build:<br/>os.cpu_count() threads"]
    
    START --> DETECT
    DETECT --> WHEEL
    DETECT --> ENV
    DETECT --> DEFAULT
    WHEEL --> CHECK
    ENV --> CHECK
    DEFAULT --> CHECK
    CHECK --> PREP
    PREP --> DECIDE
    DECIDE --> INCLUDES
    DECIDE --> LINKER
    DECIDE --> STRIP
    INCLUDES --> CYTHON
    LINKER --> CYTHON
    STRIP --> CYTHON
    CYTHON --> PARALLEL
```

**Sources:** [builder/utils.py:12-52](), [builder/utils.py:55-75](), [builder/utils.py:78-146]()

### CUDA Path Detection Logic

The `detect_cuda_paths()` function [builder/utils.py:12-52]() implements a multi-strategy search:

```python
# Searches in order:
# 1. sys.path entries (for pip wheel installations like nvidia/cu13)
# 2. CUDA_PATH or CUDA_HOME environment variables
# 3. Default /usr/local/cuda location
```

The function verifies headers like `cuda.h`, `crt/host_defines.h`, and `cudaProfiler.h` are accessible to ensure a valid build environment [builder/utils.py:47-51]().

### Library-Specific Configuration

The `decide_lib_name()` function [builder/utils.py:55-75]() maps extension names to library names, including `cublas`, `cufft`, `cudss`, `cusparse`, and others.

The `build_ext` class [builder/utils.py:78-146]() coordinates compilation:
- Parallel compilation using `os.cpu_count()` threads [builder/utils.py:144-145]().
- Automatic binary stripping for wheel size reduction [builder/utils.py:100-102]().
- Proper rpath configuration for runtime library discovery [builder/utils.py:108-128]().

**Sources:** [builder/utils.py:12-146]()

---

## Framework Integration Patterns

nvmath-python integrates with popular Python array frameworks through a unified abstraction layer that detects array types and manages memory across different frameworks.

### Array Framework Support

The framework integration follows these principles:

1. **Type Detection**: Host APIs detect input array types (NumPy, CuPy, PyTorch) automatically [README.md:32-37]().
2. **Zero-Copy Access**: Extract data pointers or interfaces (like `__cuda_array_interface__`) to avoid unnecessary host-device copies.
3. **Stream Management**: Respect framework-specific CUDA streams for asynchronous execution [README.md:64-66]().
4. **Result Consistency**: Return results in the same framework as the inputs [README.md:68-69]().

### Example: Framework-Agnostic Matrix Multiplication

From [README.md:28-69](), the `Matmul` class accepts inputs from any supported framework:

```python
import cupy as cp
import nvmath

# Prepare sample input data (CuPy example)
a = cp.random.rand(m, k).astype(cp.float32)
b = cp.random.rand(k, n).astype(cp.float32)

# nvmath-python handles the underlying library selection (cuBLASLt)
mm = nvmath.linalg.advanced.Matmul(a, b, options={...})
result = mm.execute()
```

**Sources:** [README.md:28-69]()

---

## Summary

nvmath-python's architecture achieves several key design goals:

1. **Layered Abstraction**: Clean separation between high-level Python APIs, binding layer, and native libraries.
2. **Multi-Framework Support**: Seamless integration with NumPy, CuPy, and PyTorch through unified array handling.
3. **Three Execution Models**: Host, Device, and Distributed APIs address different computational paradigms.
4. **Flexible Build System**: Supports pip wheels, custom CUDA paths, and system installations.
5. **Minimal Overhead**: Cython bindings provide near-zero-cost abstractions over native libraries.

For deeper exploration:
- Implementation details of each API category: [API Categories](#3.1)
- Binding layer internals and Cython usage: [Python Bindings Layer](#3.2)
- Practical usage of Host APIs: [Host APIs](#4)
- Device kernel integration: [Device APIs](#5)
- Multi-node computing patterns: [Distributed APIs](#6)

---

