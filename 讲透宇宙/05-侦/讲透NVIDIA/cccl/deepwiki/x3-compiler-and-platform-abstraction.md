<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cccl · extra page Compiler and Platform Abstraction · fetched 2026-10-26 -->

# Compiler and Platform Abstraction

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/libcudacxx/extended_api/type_traits/is_floating_point.rst](docs/libcudacxx/extended_api/type_traits/is_floating_point.rst)
- [lib/cmake/thrust/FindTBB.cmake](lib/cmake/thrust/FindTBB.cmake)
- [libcudacxx/include/cuda/__type_traits/is_floating_point.h](libcudacxx/include/cuda/__type_traits/is_floating_point.h)
- [libcudacxx/include/cuda/std/__atomic/functions/cuda_ptx_generated_helper.h](libcudacxx/include/cuda/std/__atomic/functions/cuda_ptx_generated_helper.h)
- [libcudacxx/include/cuda/std/__cccl/builtin.h](libcudacxx/include/cuda/std/__cccl/builtin.h)
- [libcudacxx/include/cuda/std/__cccl/compiler.h](libcudacxx/include/cuda/std/__cccl/compiler.h)
- [libcudacxx/include/cuda/std/__cccl/cuda_toolkit.h](libcudacxx/include/cuda/std/__cccl/cuda_toolkit.h)
- [libcudacxx/include/cuda/std/__cccl/diagnostic.h](libcudacxx/include/cuda/std/__cccl/diagnostic.h)
- [libcudacxx/include/cuda/std/__cccl/dialect.h](libcudacxx/include/cuda/std/__cccl/dialect.h)
- [libcudacxx/include/cuda/std/__cccl/extended_data_types.h](libcudacxx/include/cuda/std/__cccl/extended_data_types.h)
- [libcudacxx/include/cuda/std/__cccl/system_header.h](libcudacxx/include/cuda/std/__cccl/system_header.h)
- [libcudacxx/include/cuda/std/__cmath/min_max.h](libcudacxx/include/cuda/std/__cmath/min_max.h)
- [libcudacxx/include/cuda/std/__cmath/nan.h](libcudacxx/include/cuda/std/__cmath/nan.h)
- [libcudacxx/include/cuda/std/__complex/complex.h](libcudacxx/include/cuda/std/__complex/complex.h)
- [libcudacxx/include/cuda/std/__complex/logarithms.h](libcudacxx/include/cuda/std/__complex/logarithms.h)
- [libcudacxx/include/cuda/std/__complex/nvbf16.h](libcudacxx/include/cuda/std/__complex/nvbf16.h)
- [libcudacxx/include/cuda/std/__complex/nvfp16.h](libcudacxx/include/cuda/std/__complex/nvfp16.h)
- [libcudacxx/include/cuda/std/__complex/vector_support.h](libcudacxx/include/cuda/std/__complex/vector_support.h)
- [libcudacxx/include/cuda/std/__cstdlib/abs.h](libcudacxx/include/cuda/std/__cstdlib/abs.h)
- [libcudacxx/include/cuda/std/__cstdlib/div.h](libcudacxx/include/cuda/std/__cstdlib/div.h)
- [libcudacxx/include/cuda/std/__functional/bind_front.h](libcudacxx/include/cuda/std/__functional/bind_front.h)
- [libcudacxx/include/cuda/std/__functional/not_fn.h](libcudacxx/include/cuda/std/__functional/not_fn.h)
- [libcudacxx/include/cuda/std/__internal/atomic.h](libcudacxx/include/cuda/std/__internal/atomic.h)
- [libcudacxx/include/cuda/std/__internal/features.h](libcudacxx/include/cuda/std/__internal/features.h)
- [libcudacxx/include/cuda/std/__type_traits/is_extended_floating_point.h](libcudacxx/include/cuda/std/__type_traits/is_extended_floating_point.h)
- [libcudacxx/include/cuda/std/__type_traits/is_trivially_copyable.h](libcudacxx/include/cuda/std/__type_traits/is_trivially_copyable.h)
- [libcudacxx/include/cuda/std/__type_traits/promote.h](libcudacxx/include/cuda/std/__type_traits/promote.h)
- [libcudacxx/include/cuda/std/__type_traits/type_list.h](libcudacxx/include/cuda/std/__type_traits/type_list.h)
- [libcudacxx/include/cuda/std/__utility/declval.h](libcudacxx/include/cuda/std/__utility/declval.h)
- [libcudacxx/include/cuda/std/cmath](libcudacxx/include/cuda/std/cmath)
- [libcudacxx/test/libcudacxx/cuda/iterators/transform_input_output_iterator/types.h](libcudacxx/test/libcudacxx/cuda/iterators/transform_input_output_iterator/types.h)
- [libcudacxx/test/libcudacxx/cuda/iterators/transform_output_iterator/types.h](libcudacxx/test/libcudacxx/cuda/iterators/transform_output_iterator/types.h)
- [libcudacxx/test/libcudacxx/cuda/test_platform.pass.cpp](libcudacxx/test/libcudacxx/cuda/test_platform.pass.cpp)
- [libcudacxx/test/libcudacxx/cuda/type_list.pass.cpp](libcudacxx/test/libcudacxx/cuda/type_list.pass.cpp)
- [libcudacxx/test/libcudacxx/libcxx/utilities/meta/meta.unary/meta.unary.cat/is_floating_point.pass.cpp](libcudacxx/test/libcudacxx/libcxx/utilities/meta/meta.unary/meta.unary.cat/is_floating_point.pass.cpp)
- [libcudacxx/test/libcudacxx/std/language.support/cstdlib/abs.pass.cpp](libcudacxx/test/libcudacxx/std/language.support/cstdlib/abs.pass.cpp)
- [libcudacxx/test/libcudacxx/std/language.support/cstdlib/div.pass.cpp](libcudacxx/test/libcudacxx/std/language.support/cstdlib/div.pass.cpp)
- [libcudacxx/test/libcudacxx/std/numerics/c.math/comparison.h](libcudacxx/test/libcudacxx/std/numerics/c.math/comparison.h)
- [libcudacxx/test/libcudacxx/std/numerics/c.math/error_functions.pass.cpp](libcudacxx/test/libcudacxx/std/numerics/c.math/error_functions.pass.cpp)
- [libcudacxx/test/libcudacxx/std/numerics/c.math/fp_abs.pass.cpp](libcudacxx/test/libcudacxx/std/numerics/c.math/fp_abs.pass.cpp)
- [libcudacxx/test/libcudacxx/std/numerics/c.math/fp_min_max.pass.cpp](libcudacxx/test/libcudacxx/std/numerics/c.math/fp_min_max.pass.cpp)
- [libcudacxx/test/libcudacxx/std/numerics/c.math/fp_traits.pass.cpp](libcudacxx/test/libcudacxx/std/numerics/c.math/fp_traits.pass.cpp)
- [libcudacxx/test/libcudacxx/std/utilities/memory/ptr.align/align.pass.cpp](libcudacxx/test/libcudacxx/std/utilities/memory/ptr.align/align.pass.cpp)
- [libcudacxx/test/libcudacxx/std/utilities/meta/meta.unary/meta.unary.cat/is_floating_point.pass.cpp](libcudacxx/test/libcudacxx/std/utilities/meta/meta.unary/meta.unary.cat/is_floating_point.pass.cpp)
- [libcudacxx/test/support/test_macros.h](libcudacxx/test/support/test_macros.h)

</details>



## Purpose and Scope

The `__cccl/` abstraction layer provides a unified interface for compiler detection, feature detection, and platform-specific workarounds across the diverse ecosystem of CUDA and C++ compilers. This system enables libcudacxx to function as a portable standard library by abstracting away compiler differences through systematic macro-based detection and conditional compilation.

This page covers the compiler and dialect detection mechanisms, builtin wrapping, and diagnostic control. For higher-level type system abstractions, see [Standard Library Components](#2.3.1). For hardware-specific abstractions, see [Hardware Abstractions](#2.3.2).

## Architecture Overview

The compiler abstraction system consists of four primary layers:

```mermaid
graph TB
    subgraph "User Code"
        UserCode["Application Code"]
    end
    
    subgraph "Abstraction Macros"
        CompilerMacros["_CCCL_COMPILER(NVCC, >=, 12, 0)<br/>_CCCL_STD_VER<br/>_CCCL_BUILTIN_ADDRESSOF"]
    end
    
    subgraph "Detection Layer"
        CompilerH["compiler.h<br/>Compiler Version Detection"]
        DialectH["dialect.h<br/>C++ Standard Detection"]
        BuiltinH["builtin.h<br/>Builtin Detection"]
        DiagnosticH["diagnostic.h<br/>Warning Suppression"]
    end
    
    subgraph "Platform Layer"
        NVCC["NVCC<br/>__NVCC__<br/>__CUDACC_VER_*"]
        Clang["Clang<br/>__clang__<br/>__clang_major__"]
        GCC["GCC<br/>__GNUC__<br/>__GNUC_MINOR__"]
        MSVC["MSVC<br/>_MSC_VER"]
        NVRTC["NVRTC<br/>__CUDACC_RTC__"]
    end
    
    UserCode --> CompilerMacros
    CompilerMacros --> CompilerH
    CompilerMacros --> DialectH
    CompilerMacros --> BuiltinH
    CompilerMacros --> DiagnosticH
    
    CompilerH --> NVCC
    CompilerH --> Clang
    CompilerH --> GCC
    CompilerH --> MSVC
    CompilerH --> NVRTC
    
    DialectH --> NVCC
    DialectH --> Clang
    DialectH --> GCC
    DialectH --> MSVC
    
    BuiltinH --> NVCC
    BuiltinH --> Clang
    BuiltinH --> GCC
    BuiltinH --> MSVC
```

**Sources:** [libcudacxx/include/cuda/std/__cccl/compiler.h:1-219](), [libcudacxx/include/cuda/std/__cccl/dialect.h:1-197](), [libcudacxx/include/cuda/std/__cccl/builtin.h:1-494]()

## Compiler Detection System

### Version Comparison Infrastructure

The `_CCCL_VERSION_COMPARE` macro system provides a flexible framework for compiler version queries. The implementation uses preprocessor metaprogramming to support multiple comparison signatures:

```mermaid
graph LR
    subgraph "Version Comparison API"
        OneArg["_CCCL_COMPILER(GCC)<br/>Check if GCC is active"]
        ThreeArg["_CCCL_COMPILER(GCC, >=, 9)<br/>Check major version"]
        FourArg["_CCCL_COMPILER(GCC, >=, 9, 3)<br/>Check major.minor"]
    end
    
    subgraph "Internal Machinery"
        SelectCount["_CCCL_VERSION_SELECT<br/>Count arguments"]
        Compare1["_CCCL_VERSION_COMPARE_1<br/>Non-zero check"]
        Compare3["_CCCL_VERSION_COMPARE_3<br/>Major version"]
        Compare4["_CCCL_VERSION_COMPARE_4<br/>Major.minor version"]
    end
    
    subgraph "Version Storage"
        MakeVersion["_CCCL_COMPILER_MAKE_VERSION<br/>(MAJOR * 100 + MINOR)"]
        VersionPair["_CCCL_COMPILER_GCC()<br/>(9, 3)"]
        Invalid["_CCCL_VERSION_INVALID()<br/>(-1, -1)"]
    end
    
    OneArg --> SelectCount
    ThreeArg --> SelectCount
    FourArg --> SelectCount
    
    SelectCount --> Compare1
    SelectCount --> Compare3
    SelectCount --> Compare4
    
    Compare1 --> VersionPair
    Compare3 --> VersionPair
    Compare4 --> MakeVersion
    
    VersionPair -.->|if not set| Invalid
```

**Sources:** [libcudacxx/include/cuda/std/__cccl/compiler.h:16-52]()

### Host Compiler Detection

The system detects the host compiler through predefined macros and provides normalized version information:

| Compiler | Detection Macro | Version Macro | Version Format |
|----------|----------------|---------------|----------------|
| NVHPC | `__NVCOMPILER` | `_CCCL_COMPILER_NVHPC()` | `(__NVCOMPILER_MAJOR__, __NVCOMPILER_MINOR__)` |
| Clang | `__clang__` | `_CCCL_COMPILER_CLANG()` | `(__clang_major__, __clang_minor__)` |
| GCC | `__GNUC__` | `_CCCL_COMPILER_GCC()` | `(__GNUC__, __GNUC_MINOR__)` |
| MSVC | `_MSC_VER` | `_CCCL_COMPILER_MSVC()` | `(_MSC_VER / 100, _MSC_VER % 100)` |
| NVRTC | `__CUDACC_RTC__` | `_CCCL_COMPILER_NVRTC()` | `(__CUDACC_VER_MAJOR__, __CUDACC_VER_MINOR__)` |

**Sources:** [libcudacxx/include/cuda/std/__cccl/compiler.h:54-106]()

MSVC versions are further categorized into release generations:

```mermaid
graph TB
    MSCVer["_MSC_VER<br/>Raw version number"]
    
    MSVC["_CCCL_COMPILER_MSVC()<br/>Normalized version"]
    
    MSVC2019["_CCCL_COMPILER_MSVC2019()<br/>19.20 - 19.29"]
    MSVC2022["_CCCL_COMPILER_MSVC2022()<br/>19.30 - 19.49"]
    MSVC2026["_CCCL_COMPILER_MSVC2026()<br/>19.50+"]
    
    MSCVer --> MSVC
    MSVC --> MSVC2019
    MSVC --> MSVC2022
    MSVC --> MSVC2026
```

**Sources:** [libcudacxx/include/cuda/std/__cccl/compiler.h:81-102]()

### CUDA Compiler Detection

The system distinguishes between CUDA compilation contexts and identifies the CUDA compiler:

```mermaid
graph TB
    subgraph "Compilation Context"
        CUDAComp["_CCCL_CUDA_COMPILATION()<br/>Compiling .cu file"]
        HostComp["_CCCL_HOST_COMPILATION()<br/>!defined(__CUDA_ARCH__)"]
        DeviceComp["_CCCL_DEVICE_COMPILATION()<br/>defined(__CUDA_ARCH__)"]
    end
    
    subgraph "CUDA Compiler Type"
        NVCC["_CCCL_CUDA_COMPILER_NVCC()<br/>__NVCC__"]
        NVHPC["_CCCL_CUDA_COMPILER_NVHPC()<br/>_NVHPC_CUDA"]
        ClangCUDA["_CCCL_CUDA_COMPILER_CLANG()<br/>__CUDA__ && clang"]
        NVRTCCC["_CCCL_CUDA_COMPILER_NVRTC()<br/>__CUDACC_RTC__"]
    end
    
    subgraph "CUDA Toolkit Version"
        CUDACC["_CCCL_CUDACC()<br/>(__CUDACC_VER_MAJOR__, __CUDACC_VER_MINOR__)"]
        CUDAVersion["CUDA_VERSION / 1000<br/>For clang-cuda"]
    end
    
    CUDAComp --> NVCC
    CUDAComp --> NVHPC
    CUDAComp --> ClangCUDA
    CUDAComp --> NVRTCCC
    
    NVCC --> CUDACC
    NVHPC --> CUDACC
    ClangCUDA --> CUDAVersion
    NVRTCCC --> CUDACC
    
    CUDAComp --> HostComp
    CUDAComp --> DeviceComp
```

**Sources:** [libcudacxx/include/cuda/std/__cccl/compiler.h:108-172]()

## C++ Dialect Detection

### Standard Version Detection

The `_CCCL_STD_VER` macro normalizes C++ standard detection across compilers that use different mechanisms:

```mermaid
graph TB
    subgraph "MSVC Detection"
        MSVC_LANG["_MSVC_LANG<br/>MSVC-specific macro"]
        MSVCVer["201103L → 2011<br/>201402L → 2014<br/>201703L → 2017<br/>202002L → 2020<br/>else → 2023"]
    end
    
    subgraph "Standard Compilers"
        CPlusPlus["__cplusplus<br/>Standard macro"]
        StdVer["199711L → 2003<br/>201103L → 2011<br/>201402L → 2014<br/>201703L → 2017<br/>202002L → 2020<br/>202302L → 2023<br/>else → 2024"]
    end
    
    subgraph "Result"
        CCCLStdVer["_CCCL_STD_VER<br/>Unified version"]
    end
    
    MSVC_LANG --> MSVCVer
    CPlusPlus --> StdVer
    MSVCVer --> CCCLStdVer
    StdVer --> CCCLStdVer
```

**Sources:** [libcudacxx/include/cuda/std/__cccl/dialect.h:28-59]()

### Conditional Language Features

Based on `_CCCL_STD_VER`, the system defines macros for conditionally enabling C++ features:

| Macro | Condition | Usage |
|-------|-----------|-------|
| `_CCCL_CONSTEXPR_CXX20` | `_CCCL_STD_VER >= 2020` | C++20 constexpr extensions |
| `_CCCL_CONSTEXPR_CXX23` | `_CCCL_STD_VER >= 2023` | C++23 constexpr extensions |
| `_CCCL_HAS_CONCEPTS()` | `_CCCL_STD_VER > 2017 && __cpp_concepts >= 201907L` | Concepts support |
| `_CCCL_NO_THREE_WAY_COMPARISON` | `_CCCL_STD_VER <= 2017` | Spaceship operator |
| `_CCCL_HAS_PACK_INDEXING()` | `defined(__cpp_pack_indexing)` | C++26 pack indexing |

**Sources:** [libcudacxx/include/cuda/std/__cccl/dialect.h:61-99]()

### Runtime Constant Evaluation Detection

The system provides a unified interface for detecting constant evaluation context:

```mermaid
graph TB
    subgraph "C++23+ Native Support"
        IfConsteval["if consteval<br/>__cpp_if_consteval >= 202106L"]
    end
    
    subgraph "C++20 Backport"
        CXX20Support["GCC >= 12<br/>Clang (any)<br/>NVHPC with libstdc++ >= 12"]
        CXX20NVCC["NVCC >= 13.0<br/>Host code only<br/>NVCC >= 13.1 device"]
    end
    
    subgraph "Builtin Fallback"
        BuiltinCE["_CCCL_BUILTIN_IS_CONSTANT_EVALUATED"]
        Wrapper["if (_CCCL_BUILTIN_IS_CONSTANT_EVALUATED())"]
    end
    
    subgraph "No Support"
        CompileTime["if constexpr (false/true)"]
    end
    
    subgraph "Unified Interface"
        IfConstevalMacro["_CCCL_IF_CONSTEVAL"]
        IfNotConsteval["_CCCL_IF_NOT_CONSTEVAL"]
    end
    
    IfConsteval --> IfConstevalMacro
    CXX20Support --> CXX20NVCC
    CXX20NVCC --> IfConstevalMacro
    BuiltinCE --> Wrapper
    Wrapper --> IfConstevalMacro
    CompileTime --> IfConstevalMacro
    
    IfConstevalMacro --> IfNotConsteval
```

**Sources:** [libcudacxx/include/cuda/std/__cccl/dialect.h:136-178]()

## Builtin Detection and Wrapping

### Detection Strategy

The builtin detection system handles compilers with varying levels of `__has_builtin` support through a multi-layered strategy:

```mermaid
graph TB
    subgraph "Modern Compilers"
        HasBuiltin["__has_builtin(__builtin_name)<br/>Direct detection"]
        Define["#define _CCCL_HAS_BUILTIN(__x) __has_builtin(__x)"]
    end
    
    subgraph "Legacy Compilers"
        HasFeature["__has_feature(feature)<br/>Clang < 10"]
        IsIdentifier["__is_identifier(__x)<br/>Returns 0 for reserved"]
        CheckBuiltin["_CCCL_CHECK_BUILTIN<br/>Combined check"]
    end
    
    subgraph "Manual Detection"
        GCCVersion["GCC version checks<br/>e.g., _CCCL_COMPILER(GCC, >=, 7)"]
        MSVCVersion["MSVC version checks<br/>e.g., _CCCL_COMPILER(MSVC)"]
    end
    
    subgraph "Result Macros"
        Wrapper["_CCCL_BUILTIN_ADDRESSOF(...)<br/>__builtin_addressof(__VA_ARGS__)"]
        Undefined["#undef _CCCL_BUILTIN_*<br/>For broken implementations"]
    end
    
    HasBuiltin --> Define
    HasFeature --> CheckBuiltin
    IsIdentifier --> CheckBuiltin
    
    CheckBuiltin --> Wrapper
    GCCVersion --> Wrapper
    MSVCVersion --> Wrapper
    
    Wrapper -.->|if broken| Undefined
```

**Sources:** [libcudacxx/include/cuda/std/__cccl/builtin.h:29-67]()

### Builtin Categories

The system wraps compiler builtins in several categories:

**Type Traits Builtins:**

```mermaid
graph LR
    subgraph "Builtin Type Traits"
        AddressOf["_CCCL_BUILTIN_ADDRESSOF<br/>__builtin_addressof"]
        IsArray["_CCCL_BUILTIN_IS_ARRAY<br/>__is_array"]
        IsConstructible["_CCCL_BUILTIN_IS_CONSTRUCTIBLE<br/>__is_constructible"]
        IsAssignable["_CCCL_BUILTIN_IS_ASSIGNABLE<br/>__is_assignable"]
    end
    
    subgraph "Type Transformations"
        RemoveCV["_CCCL_BUILTIN_REMOVE_CV<br/>__remove_cv"]
        RemoveRef["_CCCL_BUILTIN_REMOVE_REFERENCE_T<br/>__remove_reference"]
        Decay["_CCCL_BUILTIN_DECAY<br/>__decay"]
    end
    
    subgraph "Pack Utilities"
        TypePackElement["_CCCL_BUILTIN_TYPE_PACK_ELEMENT<br/>__type_pack_element"]
        IntegerPack["_CCCL_BUILTIN_INTEGER_PACK<br/>__integer_pack"]
    end
```

**Sources:** [libcudacxx/include/cuda/std/__cccl/builtin.h:70-475]()

**Math and Utility Builtins:**

| Builtin Macro | Compiler Support | Workarounds |
|---------------|------------------|-------------|
| `_CCCL_BUILTIN_ASSUME` | Clang, NVHPC, GCC ≥ 13 | MSVC uses `__assume` |
| `_CCCL_BUILTIN_EXPECT` | Most compilers | Manual fallback possible |
| `_CCCL_BUILTIN_CONSTANT_P` | GCC, Clang | Not available on MSVC |
| `_CCCL_BUILTIN_MEMCMP` | GCC, MSVC ≥ 19.28 | Disabled for NVCC/Clang CUDA |
| `_CCCL_BUILTIN_HUGE_VALF` | Most compilers | Special handling for float128 |

**Sources:** [libcudacxx/include/cuda/std/__cccl/builtin.h:99-134]()

### Compiler-Specific Workarounds

The system includes explicit workarounds for known compiler bugs:

```mermaid
graph TB
    subgraph "Detection"
        DetectBuiltin["Builtin detected<br/>via __has_builtin"]
    end
    
    subgraph "Validation"
        TestUsage["Test actual behavior"]
        KnownBug["Check against known bugs"]
    end
    
    subgraph "Workarounds"
        UndefMacro["#undef _CCCL_BUILTIN_*"]
        AlternativeImpl["Use fallback implementation"]
        VersionGuard["#if _CCCL_COMPILER(*, <, version)"]
    end
    
    DetectBuiltin --> TestUsage
    TestUsage --> KnownBug
    KnownBug --> UndefMacro
    KnownBug --> AlternativeImpl
    KnownBug --> VersionGuard
    
    note1["Examples:<br/>- NVCC __remove_cvref < 12.4<br/>- Clang __is_array < 19<br/>- NVCC __is_function (all versions)"]
    
    KnownBug -.-> note1
```

**Example workarounds:**
- [libcudacxx/include/cuda/std/__cccl/builtin.h:442-444]() - NVRTC `__remove_cvref` disabled below 12.4
- [libcudacxx/include/cuda/std/__cccl/builtin.h:275-278]() - Clang `__is_array` disabled below version 19
- [libcudacxx/include/cuda/std/__cccl/builtin.h:304-307]() - NVCC `__is_function` always disabled

**Sources:** [libcudacxx/include/cuda/std/__cccl/builtin.h:70-494]()

## Diagnostic Control

### Warning Suppression System

The diagnostic system provides unified macros for suppressing warnings across different compilers:

```mermaid
graph TB
    subgraph "Public Interface"
        DiagPush["_CCCL_DIAG_PUSH<br/>Push diagnostic state"]
        DiagPop["_CCCL_DIAG_POP<br/>Pop diagnostic state"]
        SuppressClang["_CCCL_DIAG_SUPPRESS_CLANG(warning)"]
        SuppressGCC["_CCCL_DIAG_SUPPRESS_GCC(warning)"]
        SuppressNVHPC["_CCCL_DIAG_SUPPRESS_NVHPC(warning)"]
        SuppressMSVC["_CCCL_DIAG_SUPPRESS_MSVC(warning)"]
    end
    
    subgraph "Clang Implementation"
        ClangPush["#pragma clang diagnostic push"]
        ClangPop["#pragma clang diagnostic pop"]
        ClangSuppress["#pragma clang diagnostic ignored warning"]
    end
    
    subgraph "GCC Implementation"
        GCCPush["#pragma GCC diagnostic push"]
        GCCPop["#pragma GCC diagnostic pop"]
        GCCSuppress["#pragma GCC diagnostic ignored warning"]
    end
    
    subgraph "MSVC Implementation"
        MSVCPush["#pragma warning(push)"]
        MSVCPop["#pragma warning(pop)"]
        MSVCSuppress["#pragma warning(disable : warning)"]
    end
    
    DiagPush --> ClangPush
    DiagPush --> GCCPush
    DiagPush --> MSVCPush
    
    DiagPop --> ClangPop
    DiagPop --> GCCPop
    DiagPop --> MSVCPop
    
    SuppressClang --> ClangSuppress
    SuppressGCC --> GCCSuppress
    SuppressMSVC --> MSVCSuppress
```

**Sources:** [libcudacxx/include/cuda/std/__cccl/diagnostic.h:26-61]()

### NVCC-Specific Diagnostics

CUDA compilers require separate diagnostic control:

| Macro | NVCC ≥ 11.3 | NVCC < 11.3 | Purpose |
|-------|-------------|-------------|---------|
| `_CCCL_NV_DIAG_PUSH()` | `#pragma nv_diagnostic push` | `#pragma diagnostic push` | Save state |
| `_CCCL_NV_DIAG_POP()` | `#pragma nv_diagnostic pop` | `#pragma diagnostic pop` | Restore state |
| `_CCCL_DIAG_SUPPRESS_NVCC(n)` | `#pragma nv_diag_suppress n` | `#pragma diag_suppress n` | Suppress warning |
| `_CCCL_BEGIN_NV_DIAG_SUPPRESS(...)` | Push + suppress all | Push + suppress all | Convenience macro |
| `_CCCL_END_NV_DIAG_SUPPRESS()` | Pop | Pop | Convenience macro |

**Sources:** [libcudacxx/include/cuda/std/__cccl/diagnostic.h:64-86]()

### Convenience Macros

Common warning suppression patterns are wrapped in high-level macros:

```mermaid
graph TB
    subgraph "Deprecation Warnings"
        DeprecatedPush["_CCCL_SUPPRESS_DEPRECATED_PUSH"]
        DeprecatedPop["_CCCL_SUPPRESS_DEPRECATED_POP"]
    end
    
    subgraph "Clang Deprecation"
        ClangDep1["-Wdeprecated"]
        ClangDep2["-Wdeprecated-declarations"]
        ClangNV["NVCC 1444, 20199"]
    end
    
    subgraph "GCC Deprecation"
        GCCDep1["-Wdeprecated"]
        GCCDep2["-Wdeprecated-declarations"]
        GCCNV["NVCC 1444, 20199"]
    end
    
    subgraph "MSVC Deprecation"
        MSVCDep["C4996"]
        MSVCNV["NVCC 1444"]
    end
    
    DeprecatedPush --> ClangDep1
    DeprecatedPush --> ClangDep2
    DeprecatedPush --> ClangNV
    
    DeprecatedPush --> GCCDep1
    DeprecatedPush --> GCCDep2
    DeprecatedPush --> GCCNV
    
    DeprecatedPush --> MSVCDep
    DeprecatedPush --> MSVCNV
```

**Sources:** [libcudacxx/include/cuda/std/__cccl/diagnostic.h:88-122]()

## Extended Data Type Detection

### Floating Point Type Detection

The system detects availability of NVIDIA extended floating-point types:

```mermaid
graph TB
    subgraph "Type Detection Conditions"
        HasInclude["__has_include(<cuda_fpN.h>)"]
        HasCTK["_CCCL_HAS_CTK()<br/>CUDA Toolkit available"]
        CTKVersion["_CCCL_CTK_AT_LEAST(major, minor)"]
        NoDisable["!defined(CCCL_DISABLE_*_SUPPORT)"]
    end
    
    subgraph "FP16 Types"
        NVFP16["_CCCL_HAS_NVFP16()<br/>__half, __half2"]
        FP16Header["<cuda_fp16.h>"]
    end
    
    subgraph "BF16 Types"
        NVBF16["_CCCL_HAS_NVBF16()<br/>__nv_bfloat16, __nv_bfloat162"]
        BF16Header["<cuda_bf16.h>"]
        RequiresFP16["Requires _CCCL_HAS_NVFP16()"]
    end
    
    subgraph "FP8 Types"
        NVFP8["_CCCL_HAS_NVFP8()<br/>__nv_fp8_e5m2, __nv_fp8_e4m3"]
        FP8Header["<cuda_fp8.h>"]
        RequiresBoth["Requires FP16 and BF16"]
    end
    
    subgraph "Lower Precision"
        NVFP6["_CCCL_HAS_NVFP6()<br/>__nv_fp6_e3m2, __nv_fp6_e2m3"]
        NVFP4["_CCCL_HAS_NVFP4()<br/>__nv_fp4_e2m1"]
        RequiresFP8["Requires FP8"]
        NoNVHPC["!_CCCL_CUDA_COMPILER(NVHPC)"]
    end
    
    HasInclude --> FP16Header
    HasCTK --> FP16Header
    NoDisable --> FP16Header
    FP16Header --> NVFP16
    
    NVFP16 --> RequiresFP16
    RequiresFP16 --> BF16Header
    BF16Header --> NVBF16
    
    NVFP16 --> RequiresBoth
    NVBF16 --> RequiresBoth
    RequiresBoth --> FP8Header
    FP8Header --> NVFP8
    
    NVFP8 --> RequiresFP8
    RequiresFP8 --> NoNVHPC
    NoNVHPC --> NVFP6
    NVFP6 --> NVFP4
```

**Sources:** [libcudacxx/include/cuda/std/__cccl/extended_data_types.h:32-98]()

### Integer and Float128 Detection

Additional extended types are detected based on platform and compiler support:

| Type Macro | Requirements | Additional Notes |
|------------|--------------|------------------|
| `_CCCL_HAS_INT128()` | Linux && (`__SIZEOF_INT128__` \|\| NVRTC) | Disabled on non-Linux |
| `_CCCL_HAS_FLOAT128()` | Linux && !ARM64 && int128 support | Host: most compilers; Device: SM_100+ only |
| | | NVCC/NVRTC ≥ 12.8 required for device |
| | | GCC requires extended literals or disable |

**Sources:** [libcudacxx/include/cuda/std/__cccl/extended_data_types.h:40-137]()

The float128 device support requires specific conditions:

```mermaid
graph TB
    subgraph "Host Support"
        HostCompiler["__SIZEOF_FLOAT128__<br/>or __FLOAT128__"]
        HostOS["Linux && !ARM64"]
        HostInt128["_CCCL_HAS_INT128()"]
    end
    
    subgraph "Device Support"
        DeviceCompiler["NVCC or NVRTC >= 12.8"]
        DeviceArch["_CCCL_PTX_ARCH() >= 1000"]
    end
    
    subgraph "Result"
        Float128Host["_CCCL_HAS_FLOAT128() on host"]
        Float128Device["_CCCL_HAS_FLOAT128() on device"]
    end
    
    HostCompiler --> Float128Host
    HostOS --> Float128Host
    HostInt128 --> Float128Host
    
    DeviceCompiler --> Float128Device
    DeviceArch --> Float128Device
```

**Sources:** [libcudacxx/include/cuda/std/__cccl/extended_data_types.h:107-137]()

## Usage Patterns

### Conditional Compilation Example

The abstraction macros enable portable conditional compilation:

```cpp
// From libcudacxx/include/cuda/std/__cccl/dialect.h

#if _CCCL_STD_VER >= 2020
#  define _CCCL_CONSTEXPR_CXX20 constexpr
#else
#  define _CCCL_CONSTEXPR_CXX20
#endif

// From libcudacxx/include/cuda/std/__utility/declval.h

#if !_CCCL_CUDA_COMPILER(NVCC, <, 12, 4) && !_CCCL_COMPILER(MSVC, <, 19, 39)
template <class _Tp, class = void>
extern __declfn_t<void> declval;  // Fast implementation
#else
template <class _Tp>
_CCCL_API inline _Tp&& __declval(int);  // Fallback
#endif
```

**Sources:** [libcudacxx/include/cuda/std/__cccl/dialect.h:65-69](), [libcudacxx/include/cuda/std/__utility/declval.h:48-69]()

### Builtin Detection Pattern

```cpp
// From libcudacxx/include/cuda/std/__cccl/builtin.h

#if _CCCL_CHECK_BUILTIN(builtin_addressof) || _CCCL_COMPILER(GCC, >=, 7) \
  || _CCCL_COMPILER(MSVC) || _CCCL_COMPILER(NVHPC) || _CCCL_COMPILER(NVRTC, >=, 12, 3)
#  define _CCCL_BUILTIN_ADDRESSOF(...) __builtin_addressof(__VA_ARGS__)
#endif

// Usage in type_traits
#ifdef _CCCL_BUILTIN_ADDRESSOF
  return _CCCL_BUILTIN_ADDRESSOF(__x);
#else
  return fallback_implementation(__x);
#endif
```

**Sources:** [libcudacxx/include/cuda/std/__cccl/builtin.h:93-97]()

### Diagnostic Suppression Pattern

```cpp
// From libcudacxx/include/cuda/std/__functional/not_fn.h

_CCCL_SUPPRESS_DEPRECATED_PUSH
template <class _Fn>
class _CCCL_TYPE_VISIBILITY_DEFAULT __not_fn_t
{
  // Implementation using potentially deprecated features
};
_CCCL_SUPPRESS_DEPRECATED_POP
```

**Sources:** [libcudacxx/include/cuda/std/__functional/not_fn.h:1-100]()

## Integration with Type System

The compiler abstraction layer directly enables advanced type trait optimizations:

```mermaid
graph TB
    subgraph "Builtin Detection"
        CheckBuiltin["_CCCL_CHECK_BUILTIN(is_constructible)"]
    end
    
    subgraph "Type Trait Implementation"
        UseBuiltin["#ifdef _CCCL_BUILTIN_IS_CONSTRUCTIBLE<br/>use __is_constructible"]
        Fallback["#else<br/>use template metaprogramming"]
    end
    
    subgraph "Extended Types"
        ExtendedFP["_CCCL_HAS_NVFP16()<br/>_CCCL_HAS_NVBF16()"]
        Specializations["template<> is_floating_point<__half>"]
    end
    
    CheckBuiltin --> UseBuiltin
    CheckBuiltin --> Fallback
    ExtendedFP --> Specializations
```

**Sources:** [libcudacxx/include/cuda/std/__type_traits/is_constructible.h](), [libcudacxx/include/cuda/std/__type_traits/is_extended_floating_point.h:1-79]()

---

