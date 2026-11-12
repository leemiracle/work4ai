<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cccl · extra page Hardware Abstractions · fetched 2026-10-26 -->

# Hardware Abstractions

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/cccl/development/macro.rst](docs/cccl/development/macro.rst)
- [docs/libcudacxx/extended_api/exceptions.rst](docs/libcudacxx/extended_api/exceptions.rst)
- [docs/libcudacxx/extended_api/memory.rst](docs/libcudacxx/extended_api/memory.rst)
- [docs/libcudacxx/extended_api/memory/is_pointer_accessible.rst](docs/libcudacxx/extended_api/memory/is_pointer_accessible.rst)
- [docs/libcudacxx/extended_api/memory/ranges_overlap.rst](docs/libcudacxx/extended_api/memory/ranges_overlap.rst)
- [docs/libcudacxx/extended_api/tma/make_tma_descriptor.rst](docs/libcudacxx/extended_api/tma/make_tma_descriptor.rst)
- [docs/libcudacxx/ptx/instructions/bmsk.rst](docs/libcudacxx/ptx/instructions/bmsk.rst)
- [docs/libcudacxx/ptx/instructions/prmt.rst](docs/libcudacxx/ptx/instructions/prmt.rst)
- [docs/libcudacxx/ptx/instructions/shl.rst](docs/libcudacxx/ptx/instructions/shl.rst)
- [docs/libcudacxx/ptx/instructions/shr.rst](docs/libcudacxx/ptx/instructions/shr.rst)
- [libcudacxx/codegen/add_ptx_instruction.py](libcudacxx/codegen/add_ptx_instruction.py)
- [libcudacxx/codegen/cccl_paths.py](libcudacxx/codegen/cccl_paths.py)
- [libcudacxx/codegen/generate_prologue_epilogue.py](libcudacxx/codegen/generate_prologue_epilogue.py)
- [libcudacxx/include/cuda/__driver/driver_api.h](libcudacxx/include/cuda/__driver/driver_api.h)
- [libcudacxx/include/cuda/__memory/is_pointer_accessible.h](libcudacxx/include/cuda/__memory/is_pointer_accessible.h)
- [libcudacxx/include/cuda/__memory/ranges_overlap.h](libcudacxx/include/cuda/__memory/ranges_overlap.h)
- [libcudacxx/include/cuda/__ptx/instructions/bmsk.h](libcudacxx/include/cuda/__ptx/instructions/bmsk.h)
- [libcudacxx/include/cuda/__runtime/api_wrapper.h](libcudacxx/include/cuda/__runtime/api_wrapper.h)
- [libcudacxx/include/cuda/__tma/make_tma_descriptor.h](libcudacxx/include/cuda/__tma/make_tma_descriptor.h)
- [libcudacxx/include/cuda/memory](libcudacxx/include/cuda/memory)
- [libcudacxx/include/cuda/std/__cccl/attributes.h](libcudacxx/include/cuda/std/__cccl/attributes.h)
- [libcudacxx/include/cuda/std/__cccl/epilogue.h](libcudacxx/include/cuda/std/__cccl/epilogue.h)
- [libcudacxx/include/cuda/std/__cccl/exceptions.h](libcudacxx/include/cuda/std/__cccl/exceptions.h)
- [libcudacxx/include/cuda/std/__cccl/prologue.h](libcudacxx/include/cuda/std/__cccl/prologue.h)
- [libcudacxx/include/cuda/std/__exception/cuda_error.h](libcudacxx/include/cuda/std/__exception/cuda_error.h)
- [libcudacxx/include/cuda/std/__exception/exception_macros.h](libcudacxx/include/cuda/std/__exception/exception_macros.h)
- [libcudacxx/include/cuda/std/__exception/msg_storage.h](libcudacxx/include/cuda/std/__exception/msg_storage.h)
- [libcudacxx/include/cuda/std/__memory/align.h](libcudacxx/include/cuda/std/__memory/align.h)
- [libcudacxx/test/libcudacxx/cuda/ccclrt/algorithm/common.cuh](libcudacxx/test/libcudacxx/cuda/ccclrt/algorithm/common.cuh)
- [libcudacxx/test/libcudacxx/cuda/memory/is_pointer_accessible.pass.cpp](libcudacxx/test/libcudacxx/cuda/memory/is_pointer_accessible.pass.cpp)
- [libcudacxx/test/libcudacxx/cuda/memory/ranges_overlap.pass.cpp](libcudacxx/test/libcudacxx/cuda/memory/ranges_overlap.pass.cpp)
- [libcudacxx/test/libcudacxx/cuda/tma/make_tma_descriptor.pass.cpp](libcudacxx/test/libcudacxx/cuda/tma/make_tma_descriptor.pass.cpp)
- [libcudacxx/test/libcudacxx/libcxx/exceptions/try_catch.pass.cpp](libcudacxx/test/libcudacxx/libcxx/exceptions/try_catch.pass.cpp)
- [libcudacxx/test/libcudacxx/libcxx/exceptions/try_catch_no_exceptions_device.runfail.cpp](libcudacxx/test/libcudacxx/libcxx/exceptions/try_catch_no_exceptions_device.runfail.cpp)
- [libcudacxx/test/libcudacxx/libcxx/exceptions/try_catch_no_exceptions_host.runfail.cpp](libcudacxx/test/libcudacxx/libcxx/exceptions/try_catch_no_exceptions_host.runfail.cpp)
- [libcudacxx/test/libcudacxx/libcxx/macros/lifetime_bound.compile.fail.cpp](libcudacxx/test/libcudacxx/libcxx/macros/lifetime_bound.compile.fail.cpp)
- [libcudacxx/test/libcudacxx/libcxx/macros/lifetime_bound.compile.pass.cpp](libcudacxx/test/libcudacxx/libcxx/macros/lifetime_bound.compile.pass.cpp)

</details>



This page documents libcudacxx's CUDA-specific hardware abstractions that enable efficient use of GPU features across different compilers, architectures, and platforms. These abstractions provide portable access to atomic operations, synchronization primitives, memory operations, and PTX-level instructions.

For standard C++ library components available in libcudacxx, see [Standard Library Components](#2.3.1). For information about CUB's low-level device primitives, see [CUB](#2.2). For compiler detection and platform abstraction implementation details, see [Platform Abstraction Layer](#5.1).

## Overview

libcudacxx provides hardware abstractions through three layers:

1. **User-Facing APIs**: High-level types like `cuda::atomic_ref`, `cuda::barrier`, memory fences
2. **Platform Abstraction**: Compiler-agnostic macros that detect and adapt to different toolchains
3. **Hardware Intrinsics**: Direct access to PTX instructions and architecture-specific features

These abstractions enable code to work across NVCC, Clang-CUDA, NVHPC, and host-only compilers while maintaining performance.

```mermaid
graph TB
    subgraph "User Code"
        USER["Application using cuda::atomic_ref"]
    end
    
    subgraph "High-Level Hardware Abstractions"
        ATOMIC["cuda::atomic<br/>cuda::atomic_ref<br/>cuda::thread_scope_*"]
        BARRIER["cuda::barrier<br/>cuda::latch<br/>cuda::counting_semaphore"]
        MEMOPS["cuda::memory_order_*<br/>cuda::atomic_thread_fence<br/>cuda::atomic_signal_fence"]
    end
    
    subgraph "Platform Abstraction Layer"
        BUILTIN["_CCCL_BUILTIN_* macros<br/>Compiler builtin detection<br/>Fallback implementations"]
        ATTRS["_CCCL_* attributes<br/>Execution space markers<br/>Optimization hints"]
        COMPILER["_CCCL_COMPILER detection<br/>_CCCL_CUDA_COMPILER detection<br/>Version comparison"]
    end
    
    subgraph "Compiler-Specific Implementations"
        NVCC["NVCC intrinsics<br/>__atomic_*<br/>PTX assembly"]
        CLANG["Clang-CUDA builtins<br/>__builtin_*<br/>LLVM intrinsics"]
        HOST["Host atomics<br/>std::atomic<br/>GCC/MSVC intrinsics"]
    end
    
    USER --> ATOMIC
    USER --> BARRIER
    USER --> MEMOPS
    
    ATOMIC --> BUILTIN
    BARRIER --> BUILTIN
    MEMOPS --> BUILTIN
    
    ATOMIC --> ATTRS
    BARRIER --> ATTRS
    
    BUILTIN --> COMPILER
    ATTRS --> COMPILER
    
    COMPILER --> NVCC
    COMPILER --> CLANG
    COMPILER --> HOST
```

Sources: [README.md:1-106](), [libcudacxx/include/cuda/__cccl_config:1-37]()

## Atomic Operations

libcudacxx provides `cuda::atomic` and `cuda::atomic_ref` as hardware-abstracted atomic types that work in both host and device code. These types use the `_LIBCUDACXX_HAS_CUDA_ATOMIC_IMPL` configuration to dispatch to appropriate implementations.

### Core Atomic Types

| Type | Description | Header |
|------|-------------|--------|
| `cuda::atomic<T>` | Atomic object with storage | `<cuda/atomic>` |
| `cuda::atomic_ref<T, Scope>` | Reference to existing storage | `<cuda/atomic>` |
| `cuda::thread_scope_system` | System-wide atomics | `<cuda/std/atomic>` |
| `cuda::thread_scope_device` | Device-wide atomics | `<cuda/std/atomic>` |
| `cuda::thread_scope_block` | Block-wide atomics | `<cuda/std/atomic>` |
| `cuda::thread_scope_thread` | Thread-local (no sync) | `<cuda/std/atomic>` |

### Memory Orders

```mermaid
graph LR
    subgraph "Memory Order Hierarchy"
        RELAXED["cuda::memory_order_relaxed<br/>No synchronization"]
        ACQUIRE["cuda::memory_order_acquire<br/>Acquire semantics"]
        RELEASE["cuda::memory_order_release<br/>Release semantics"]
        ACQ_REL["cuda::memory_order_acq_rel<br/>Acquire + Release"]
        SEQ_CST["cuda::memory_order_seq_cst<br/>Sequential consistency"]
    end
    
    RELAXED --> ACQUIRE
    RELAXED --> RELEASE
    ACQUIRE --> ACQ_REL
    RELEASE --> ACQ_REL
    ACQ_REL --> SEQ_CST
```

### Implementation Dispatch

```mermaid
graph TB
    API["cuda::atomic_ref::fetch_add"]
    
    subgraph "Compilation Context Detection"
        CUDA_COMP["_CCCL_HAS_CUDA_COMPILER()<br/>_CCCL_DEVICE_COMPILATION()"]
    end
    
    subgraph "Implementation Selection"
        CUDA_IMPL["_LIBCUDACXX_HAS_CUDA_ATOMIC_IMPL<br/>CUDA atomic dispatch layer"]
        HOST_IMPL["_LIBCUDACXX_HAS_GCC_ATOMIC_IMP<br/>or _LIBCUDACXX_HAS_MSVC_ATOMIC_IMPL"]
    end
    
    subgraph "Low-Level Operations"
        PTX["PTX instructions<br/>atom.add, atom.cas<br/>fence.sc.sys"]
        GCC["__atomic_fetch_add<br/>__atomic_compare_exchange"]
        MSVC["_InterlockedExchangeAdd<br/>_InterlockedCompareExchange"]
    end
    
    API --> CUDA_COMP
    
    CUDA_COMP -->|"Device code"| CUDA_IMPL
    CUDA_COMP -->|"Host code"| HOST_IMPL
    
    CUDA_IMPL --> PTX
    HOST_IMPL --> GCC
    HOST_IMPL --> MSVC
```

Sources: [libcudacxx/include/cuda/std/detail/libcxx/include/__config:58-144](), [README.md:46-106]()

## Compiler Builtin Abstractions

The `_CCCL_BUILTIN_*` macro family provides portable access to compiler intrinsics. These are implemented in [libcudacxx/include/cuda/std/__cccl/builtin.h:1-677]() and form the foundation for hardware abstractions.

### Builtin Detection Strategy

```mermaid
graph TB
    subgraph "Detection Methods"
        HAS_BUILTIN["__has_builtin(__builtin_name)<br/>Clang, modern GCC"]
        HAS_FEATURE["__has_feature(feature_name)<br/>Clang features"]
        IS_IDENTIFIER["__is_identifier(__name)<br/>Returns 0 if reserved"]
    end
    
    subgraph "Combined Check"
        CHECK["_CCCL_CHECK_BUILTIN(name)<br/>Tries all three methods"]
    end
    
    subgraph "Result"
        MACRO["_CCCL_BUILTIN_NAME(...)<br/>Defined if available"]
        FALLBACK["Undefined if unavailable<br/>Code uses #ifdef"]
    end
    
    HAS_BUILTIN --> CHECK
    HAS_FEATURE --> CHECK
    IS_IDENTIFIER --> CHECK
    
    CHECK -->|"Available"| MACRO
    CHECK -->|"Not available"| FALLBACK
```

### Key Builtin Categories

**Type Operations**:
- `_CCCL_BUILTIN_ADDRESSOF`: Portable `__builtin_addressof` [libcudacxx/include/cuda/std/__cccl/builtin.h:93-97]()
- `_CCCL_BUILTIN_BIT_CAST`: Type punning via `__builtin_bit_cast` [libcudacxx/include/cuda/std/__cccl/builtin.h:113-116]()
- `_CCCL_BUILTIN_IS_CONSTANT_EVALUATED`: Constexpr context detection [libcudacxx/include/cuda/std/__cccl/builtin.h:252-254]()

**Bit Manipulation**:
- `_CCCL_BUILTIN_POPCOUNT`/`_CCCL_BUILTIN_POPCOUNTLL`: Population count [libcudacxx/include/cuda/std/__cccl/builtin.h:118-122]()
- `_CCCL_BUILTIN_CLZ`/`_CCCL_BUILTIN_CLZLL`: Count leading zeros [libcudacxx/include/cuda/std/__cccl/builtin.h:133-136]()
- `_CCCL_BUILTIN_CTZ`/`_CCCL_BUILTIN_CTZLL`: Count trailing zeros [libcudacxx/include/cuda/std/__cccl/builtin.h:147-150]()
- `_CCCL_BUILTIN_BSWAP16`/`32`/`64`: Byte swap [libcudacxx/include/cuda/std/__cccl/builtin.h:161-171]()

**Optimization Hints**:
- `_CCCL_BUILTIN_ASSUME`: Optimization assumptions [libcudacxx/include/cuda/std/__cccl/builtin.h:99-107]()
- `_CCCL_BUILTIN_EXPECT`: Branch prediction [libcudacxx/include/cuda/std/__cccl/builtin.h:211-213]()
- `_CCCL_BUILTIN_PREFETCH`: Memory prefetch [libcudacxx/include/cuda/std/__cccl/builtin.h:354-358]()

**Compiler Workarounds**:

```mermaid
graph TB
    subgraph "Example: POPCOUNT Abstraction"
        CHECK_PC["_CCCL_CHECK_BUILTIN(builtin_popcount)<br/>or _CCCL_COMPILER(GCC, <, 10)"]
        
        DEFINE_PC["#define _CCCL_BUILTIN_POPCOUNT(...)<br/>__builtin_popcount(__VA_ARGS__)"]
        
        DISABLE_NVCC["#if _CCCL_CUDA_COMPILER(NVCC)<br/>#undef _CCCL_BUILTIN_POPCOUNTG<br/>#endif"]
    end
    
    CHECK_PC -->|"Available"| DEFINE_PC
    DEFINE_PC --> DISABLE_NVCC
```

The NVCC workaround demonstrates how [libcudacxx/include/cuda/std/__cccl/builtin.h:128-131]() disables `_CCCL_BUILTIN_POPCOUNTG` for NVCC because that compiler cannot handle the generic version.

Sources: [libcudacxx/include/cuda/std/__cccl/builtin.h:1-677]()

## Attribute Abstractions

The `_CCCL_*` attribute macros provide portable function and type annotations that work across compilers. These enable optimization hints, debug control, and semantic guarantees.

### Attribute Categories

| Category | Macro | Purpose |
|----------|-------|---------|
| **Optimization** | `_CCCL_PURE` | Function has no side effects [libcudacxx/include/cuda/std/__cccl/attributes.h:114-123]() |
| | `_CCCL_CONST` | Function is purely mathematical [libcudacxx/include/cuda/std/__cccl/attributes.h:88-93]() |
| | `_CCCL_ASSUME(expr)` | Optimization assumption [libcudacxx/include/cuda/std/__cccl/attributes.h:77-85]() |
| **Debug Control** | `_CCCL_NODEBUG` | Suppress debug info [libcudacxx/include/cuda/std/__cccl/attributes.h:55-59]() |
| | `_CCCL_ARTIFICIAL` | Don't step into in debugger [libcudacxx/include/cuda/std/__cccl/attributes.h:64-68]() |
| **Safety** | `_CCCL_NO_SANITIZE(type)` | Disable sanitizer [libcudacxx/include/cuda/std/__cccl/attributes.h:135-139]() |
| | `_CCCL_NO_CFI` | Disable CFI checks [libcudacxx/include/cuda/std/__cccl/attributes.h:126-131]() |
| **ABI** | `_CCCL_NO_UNIQUE_ADDRESS` | Enable empty base optimization [libcudacxx/include/cuda/std/__cccl/attributes.h:158-180]() |

### Multi-Tier Fallback Example: _CCCL_ASSUME

```mermaid
graph TB
    ASSUME_API["_CCCL_ASSUME(condition)"]
    
    subgraph "Tier 1: NVCC Device Code"
        NVCC_CHECK["_CCCL_CUDA_COMPILER(NVCC)<br/>&& _CCCL_DEVICE_COMPILATION()"]
        NVCC_IMPL["__builtin_assume(condition)"]
    end
    
    subgraph "Tier 2: C++23 Standard"
        CPP23_CHECK["_CCCL_HAS_CPP_ATTRIBUTE(assume)"]
        CPP23_IMPL["[[assume(condition)]]"]
    end
    
    subgraph "Tier 3: Builtin Fallback"
        BUILTIN_CHECK["_CCCL_BUILTIN_ASSUME defined"]
        BUILTIN_IMPL["_CCCL_BUILTIN_ASSUME(condition)"]
    end
    
    ASSUME_API --> NVCC_CHECK
    NVCC_CHECK -->|"Yes"| NVCC_IMPL
    NVCC_CHECK -->|"No"| CPP23_CHECK
    
    CPP23_CHECK -->|"Yes"| CPP23_IMPL
    CPP23_CHECK -->|"No"| BUILTIN_CHECK
    
    BUILTIN_CHECK -->|"Yes"| BUILTIN_IMPL
    BUILTIN_CHECK -->|"No"| EMPTY["Empty macro"]
```

This shows the implementation at [libcudacxx/include/cuda/std/__cccl/attributes.h:77-85]() which tries three approaches before falling back to a no-op.

### Attribute Detection Methods

| Method | Macro | Compilers |
|--------|-------|-----------|
| `__has_attribute` | `_CCCL_HAS_ATTRIBUTE(__x)` | Clang, GCC 5+ |
| `__has_cpp_attribute` | `_CCCL_HAS_CPP_ATTRIBUTE(__x)` | All modern |
| `__has_declspec_attribute` | `_CCCL_HAS_DECLSPEC_ATTRIBUTE(__x)` | MSVC, Clang |

Source: [libcudacxx/include/cuda/std/__cccl/attributes.h:30-46]()

### Known Issues and Workarounds

**MSVC `[[no_unique_address]]` Issue**:
```mermaid
graph LR
    CHECK["_CCCL_COMPILER(MSVC)<br/>or _CCCL_HAS_CPP_ATTRIBUTE(no_unique_address) < 201803L"]
    DISABLE["#define _CCCL_HAS_ATTRIBUTE_NO_UNIQUE_ADDRESS() 0<br/>#define _CCCL_NO_UNIQUE_ADDRESS"]
    REASON["MSVC implementation causes<br/>silent runtime corruption<br/>when passing to kernels"]
    
    CHECK --> DISABLE
    DISABLE -.-> REASON
```

**Clang C++17 NVCC Issue**:
The attribute is also disabled when using Clang as host compiler with NVCC in C++17 mode to avoid data corruption from nested `[[no_unique_address]]` objects passed to kernels (nvbug 5265027).

Sources: [libcudacxx/include/cuda/std/__cccl/attributes.h:158-180]()

## Compiler and Platform Detection

libcudacxx's hardware abstractions depend on accurate compiler and platform detection. This system is implemented in [libcudacxx/include/cuda/std/__cccl/compiler.h:1-218]().

### Compiler Detection Architecture

```mermaid
graph TB
    subgraph "Version Comparison Infrastructure"
        VERSION_MACRO["_CCCL_VERSION_COMPARE(_PREFIX, ...)"]
        MAKE_VER["_CCCL_*_MAKE_VERSION(_MAJOR, _MINOR)"]
        VERSION_SEL["_CCCL_VERSION_SELECT(...)<br/>Chooses 1-arg, 3-arg, or 4-arg form"]
    end
    
    subgraph "Host Compiler Detection"
        NVHPC["_CCCL_COMPILER_NVHPC()<br/>(__NVCOMPILER_MAJOR__, __NVCOMPILER_MINOR__)"]
        CLANG["_CCCL_COMPILER_CLANG()<br/>(__clang_major__, __clang_minor__)"]
        GCC["_CCCL_COMPILER_GCC()<br/>(__GNUC__, __GNUC_MINOR__)"]
        MSVC["_CCCL_COMPILER_MSVC()<br/>(_MSC_VER / 100, _MSC_VER % 100)"]
        NVRTC["_CCCL_COMPILER_NVRTC()<br/>(__CUDACC_VER_MAJOR__, __CUDACC_VER_MINOR__)"]
    end
    
    subgraph "CUDA Compiler Detection"
        NVCC["_CCCL_CUDA_COMPILER_NVCC()<br/>__NVCC__ defined"]
        NVHPC_CUDA["_CCCL_CUDA_COMPILER_NVHPC()<br/>_NVHPC_CUDA defined"]
        CLANG_CUDA["_CCCL_CUDA_COMPILER_CLANG()<br/>__CUDA__ && Clang"]
        NVRTC_CUDA["_CCCL_CUDA_COMPILER_NVRTC()<br/>__CUDACC_RTC__ defined"]
    end
    
    VERSION_MACRO --> MAKE_VER
    VERSION_MACRO --> VERSION_SEL
    
    NVHPC --> VERSION_MACRO
    CLANG --> VERSION_MACRO
    GCC --> VERSION_MACRO
    MSVC --> VERSION_MACRO
```

### Compilation Context Macros

| Macro | Meaning | True When |
|-------|---------|-----------|
| `_CCCL_HAS_CUDA_COMPILER()` | CUDA compiler available | Any CUDA compiler detected |
| `_CCCL_CUDA_COMPILATION()` | Compiling CUDA code | `__CUDACC__` or NVHPC CUDA |
| `_CCCL_HOST_COMPILATION()` | Compiling host code | `!__CUDA_ARCH__` (or always for NVHPC) |
| `_CCCL_DEVICE_COMPILATION()` | Compiling device code | `__CUDA_ARCH__` defined |
| `_CCCL_CUDACC_BELOW(12, 7)` | CUDA version check | During CUDA compilation only |
| `_CCCL_CUDACC_AT_LEAST(12, 7)` | CUDA version check | During CUDA compilation only |

**Special Case: NVHPC**:
When compiling with `nvc++`, both `_CCCL_HOST_COMPILATION()` and `_CCCL_DEVICE_COMPILATION()` return true because NVHPC compiles host and device code simultaneously, unlike NVCC's two-pass model.

Sources: [libcudacxx/include/cuda/std/__cccl/compiler.h:56-174]()

### Usage Example

```cpp
#if _CCCL_COMPILER(MSVC, >=, 19, 29)
#  define USE_MSVC_INTRINSIC
#elif _CCCL_CUDA_COMPILER(NVCC) && _CCCL_DEVICE_COMPILATION()
#  define USE_PTX_ASSEMBLY
#elif _CCCL_HAS_CUDA_COMPILER()
#  define USE_CUDA_BUILTIN
#endif
```

This pattern appears throughout libcudacxx to select appropriate implementations.

## Diagnostic Control

Hardware abstractions must suppress warnings across different compilers. The diagnostic system is implemented in [libcudacxx/include/cuda/std/__cccl/diagnostic.h:1-132]().

### Per-Compiler Warning Suppression

```mermaid
graph TB
    subgraph "Warning Suppression API"
        PUSH["_CCCL_DIAG_PUSH<br/>Save warning state"]
        POP["_CCCL_DIAG_POP<br/>Restore warning state"]
        
        SUPP_CLANG["_CCCL_DIAG_SUPPRESS_CLANG('-Wwarning')"]
        SUPP_GCC["_CCCL_DIAG_SUPPRESS_GCC('-Wwarning')"]
        SUPP_NVHPC["_CCCL_DIAG_SUPPRESS_NVHPC(code)"]
        SUPP_MSVC["_CCCL_DIAG_SUPPRESS_MSVC(code)"]
    end
    
    subgraph "NVCC/NVRTC Warnings"
        NV_PUSH["_CCCL_NV_DIAG_PUSH()"]
        NV_POP["_CCCL_NV_DIAG_POP()"]
        SUPP_NVCC["_CCCL_DIAG_SUPPRESS_NVCC(code)"]
    end
    
    subgraph "Convenience Macros"
        DEPR_PUSH["_CCCL_SUPPRESS_DEPRECATED_PUSH"]
        DEPR_POP["_CCCL_SUPPRESS_DEPRECATED_POP"]
    end
    
    PUSH --> SUPP_CLANG
    PUSH --> SUPP_GCC
    PUSH --> SUPP_NVHPC
    PUSH --> SUPP_MSVC
    
    PUSH --> POP
    
    NV_PUSH --> SUPP_NVCC
    NV_PUSH --> NV_POP
    
    DEPR_PUSH --> PUSH
    DEPR_PUSH --> NV_PUSH
```

### Compiler-Specific Implementation

| Compiler | Push | Pop | Suppress |
|----------|------|-----|----------|
| Clang | `#pragma clang diagnostic push` | `#pragma clang diagnostic pop` | `#pragma clang diagnostic ignored "-Wname"` |
| GCC | `#pragma GCC diagnostic push` | `#pragma GCC diagnostic pop` | `#pragma GCC diagnostic ignored "-Wname"` |
| NVHPC | `#pragma diagnostic push` | `#pragma diagnostic pop` | `#pragma diag_suppress code` |
| MSVC | `#pragma warning(push)` | `#pragma warning(pop)` | `#pragma warning(disable: code)` |
| NVCC | `#pragma nv_diagnostic push` | `#pragma nv_diagnostic pop` | `#pragma nv_diag_suppress code` |

Source: [libcudacxx/include/cuda/std/__cccl/diagnostic.h:26-86]()

### Common Warning Pattern

```cpp
_CCCL_SUPPRESS_DEPRECATED_PUSH
// Code using deprecated features
cuda::atomic<int> old_atomic;
_CCCL_SUPPRESS_DEPRECATED_POP
```

This expands to push/suppress/pop for all active compilers at [libcudacxx/include/cuda/std/__cccl/diagnostic.h:88-122]().

## Configuration and Integration

All hardware abstractions are integrated through the main configuration header.

### Integration Hierarchy

```mermaid
graph TB
    USER["User code includes<br/><cuda/atomic><br/><cuda/barrier>"]
    
    CCCL_CONFIG["<cuda/__cccl_config><br/>Central configuration hub"]
    
    ARCH["<cuda/std/__cccl/architecture.h><br/>Architecture detection"]
    COMPILER["<cuda/std/__cccl/compiler.h><br/>Compiler detection"]
    BUILTIN["<cuda/std/__cccl/builtin.h><br/>Builtin abstractions"]
    ATTRS["<cuda/std/__cccl/attributes.h><br/>Attribute abstractions"]
    DIAG["<cuda/std/__cccl/diagnostic.h><br/>Warning control"]
    EXEC["<cuda/std/__cccl/execution_space.h><br/>__host__ __device__ macros"]
    
    LIBCUDACXX_CONFIG["<cuda/std/detail/libcxx/include/__config><br/>libcudacxx configuration"]
    
    USER --> CCCL_CONFIG
    
    CCCL_CONFIG --> ARCH
    CCCL_CONFIG --> COMPILER
    CCCL_CONFIG --> BUILTIN
    CCCL_CONFIG --> ATTRS
    CCCL_CONFIG --> DIAG
    CCCL_CONFIG --> EXEC
    
    LIBCUDACXX_CONFIG --> CCCL_CONFIG
    
    BUILTIN --> COMPILER
    ATTRS --> COMPILER
    DIAG --> COMPILER
```

Sources: [libcudacxx/include/cuda/__cccl_config:1-37](), [libcudacxx/include/cuda/std/detail/libcxx/include/__config:1-208]()

### Atomic Implementation Selection

The atomic implementation is configured at [libcudacxx/include/cuda/std/detail/libcxx/include/__config:109-144]():

```mermaid
graph TB
    START["Determine atomic implementation"]
    
    CHECK_CLANG["_CCCL_COMPILER(CLANG)"]
    CHECK_GCC["_CCCL_COMPILER(GCC)"]
    CHECK_NVHPC["_CCCL_COMPILER(NVHPC)"]
    CHECK_MSVC["_CCCL_COMPILER(MSVC)"]
    
    GCC_IMPL["#define _LIBCUDACXX_HAS_GCC_ATOMIC_IMP"]
    MSVC_IMPL["#define _LIBCUDACXX_HAS_MSVC_ATOMIC_IMPL"]
    
    CHECK_CUDA["_CCCL_HAS_CUDA_COMPILER()<br/>or _CCCL_COMPILER(NVHPC)"]
    CUDA_IMPL["#define _LIBCUDACXX_HAS_CUDA_ATOMIC_IMPL<br/>CUDA atomics supersede host atomics"]
    
    START --> CHECK_CLANG
    CHECK_CLANG -->|"Yes"| GCC_IMPL
    CHECK_CLANG -->|"No"| CHECK_GCC
    CHECK_GCC -->|"Yes"| GCC_IMPL
    CHECK_GCC -->|"No"| CHECK_NVHPC
    CHECK_NVHPC -->|"Yes"| GCC_IMPL
    CHECK_NVHPC -->|"No"| CHECK_MSVC
    CHECK_MSVC -->|"Yes"| MSVC_IMPL
    
    GCC_IMPL --> CHECK_CUDA
    MSVC_IMPL --> CHECK_CUDA
    
    CHECK_CUDA -->|"Yes"| CUDA_IMPL
```

**Key Insight**: `_LIBCUDACXX_HAS_CUDA_ATOMIC_IMPL` supersedes host atomic implementations to insert the host/device dispatch layer, enabling the same atomic types to work in both host and device code.

Sources: [libcudacxx/include/cuda/std/detail/libcxx/include/__config:109-144]()

## Hardware Feature Macros

libcudacxx provides macros to detect hardware feature availability, primarily for extended data types.

### Extended Data Type Support

| Feature Macro | Description | Underlying Check |
|---------------|-------------|------------------|
| `_CCCL_HAS_INT128()` | 128-bit integers | `__int128` and `__uint128_t` |
| `_CCCL_HAS_NVFP8()` | 8-bit float types | `__nv_fp8_e5m2`, `__nv_fp8_e4m3`, `__nv_fp8_e8m0` |
| `_CCCL_HAS_NVFP16()` | 16-bit float types | `__half`, `__half2` |
| `_CCCL_HAS_NVBF16()` | 16-bit bfloat types | `__nv_bfloat16`, `__nv_bfloat162` |
| `_CCCL_HAS_FLOAT128()` | 128-bit float | `__float128` |

These can be disabled via:
- `CCCL_DISABLE_INT128_SUPPORT`
- `CCCL_DISABLE_NVFP8_SUPPORT`
- `CCCL_DISABLE_NVFP16_SUPPORT`
- `CCCL_DISABLE_NVBF16_SUPPORT`
- `CCCL_DISABLE_FLOAT128_SUPPORT`

### Type Trait Builtins

Many type traits use compiler builtins for efficiency. Examples from [libcudacxx/include/cuda/std/__cccl/builtin.h:387-586]():

```mermaid
graph LR
    subgraph "High-Level API"
        IS_ARRAY["cuda::std::is_array<T>"]
        IS_CONST["cuda::std::is_constructible<T, Args...>"]
        REMOVE_CV["cuda::std::remove_cv_t<T>"]
    end
    
    subgraph "Builtin Macros"
        BUILTIN_IS_ARRAY["_CCCL_BUILTIN_IS_ARRAY(T)<br/>__is_array(T)"]
        BUILTIN_IS_CONST["_CCCL_BUILTIN_IS_CONSTRUCTIBLE(T, Args...)<br/>__is_constructible(T, Args...)"]
        BUILTIN_REMOVE_CV["_CCCL_BUILTIN_REMOVE_CV(T)<br/>__remove_cv(T)"]
    end
    
    IS_ARRAY --> BUILTIN_IS_ARRAY
    IS_CONST --> BUILTIN_IS_CONST
    REMOVE_CV --> BUILTIN_REMOVE_CV
```

**Workarounds**: Some builtins are disabled for specific compilers:
- `_CCCL_BUILTIN_IS_ARRAY`: Disabled for Clang < 19 due to incorrect results for `T[0]` [libcudacxx/include/cuda/std/__cccl/builtin.h:391-394]()
- `_CCCL_BUILTIN_IS_FUNDAMENTAL`: Disabled for Clang < 10 [libcudacxx/include/cuda/std/__cccl/builtin.h:429-432]()
- `_CCCL_BUILTIN_REMOVE_CVREF`: Disabled for NVRTC < 12.4 [libcudacxx/include/cuda/std/__cccl/builtin.h:558-560]()

Sources: [libcudacxx/include/cuda/std/__cccl/builtin.h:387-592]()

## Summary

libcudacxx's hardware abstractions provide a comprehensive platform abstraction layer that enables CUDA features to work portably across compilers and architectures:

1. **Compiler Detection**: `_CCCL_COMPILER` and `_CCCL_CUDA_COMPILER` macros identify toolchains
2. **Builtin Abstraction**: `_CCCL_BUILTIN_*` macros provide portable intrinsic access
3. **Attribute Abstraction**: `_CCCL_*` attributes enable optimization and debug control
4. **Diagnostic Control**: Per-compiler warning suppression maintains clean builds
5. **Implementation Dispatch**: Multi-tier selection of optimal implementations
6. **Hardware Features**: Atomic operations, synchronization, and memory operations

This infrastructure allows user-facing types like `cuda::atomic_ref` to work efficiently in both host and device code while maintaining a single, clean API surface.

Sources: [libcudacxx/include/cuda/__cccl_config:1-37](), [libcudacxx/include/cuda/std/__cccl/builtin.h:1-677](), [libcudacxx/include/cuda/std/__cccl/attributes.h:1-207](), [libcudacxx/include/cuda/std/__cccl/compiler.h:1-218](), [libcudacxx/include/cuda/std/__cccl/diagnostic.h:1-132](), [libcudacxx/include/cuda/std/detail/libcxx/include/__config:1-208]()

---

