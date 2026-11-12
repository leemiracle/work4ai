<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/skala · extra page Compiler Pragma System · fetched 2026-10-26 -->

# Compiler Pragma System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [third_party/gauxc/external/gau2grid/generated_source/gau2grid/gau2grid_pragma.h](third_party/gauxc/external/gau2grid/generated_source/gau2grid/gau2grid_pragma.h)
- [third_party/gauxc/external/gau2grid/generated_source/gau2grid_deriv1.c](third_party/gauxc/external/gau2grid/generated_source/gau2grid_deriv1.c)
- [third_party/gauxc/external/gau2grid/generated_source/gau2grid_deriv2.c](third_party/gauxc/external/gau2grid/generated_source/gau2grid_deriv2.c)
- [third_party/gauxc/external/gau2grid/generated_source/gau2grid_deriv3.c](third_party/gauxc/external/gau2grid/generated_source/gau2grid_deriv3.c)
- [third_party/gauxc/external/gau2grid/generated_source/gau2grid_phi.c](third_party/gauxc/external/gau2grid/generated_source/gau2grid_phi.c)
- [third_party/gauxc/external/gau2grid/src/gau2grid/c_generator.py](third_party/gauxc/external/gau2grid/src/gau2grid/c_generator.py)
- [third_party/gauxc/external/gau2grid/src/gau2grid/c_pragma.py](third_party/gauxc/external/gau2grid/src/gau2grid/c_pragma.py)

</details>



## Purpose and Scope

The compiler pragma system provides a platform-independent abstraction layer for compiler-specific directives used throughout the Gau2Grid collocation kernels. This system enables the generated C code to leverage advanced compiler features such as vectorization hints, aligned memory allocation, and pointer aliasing restrictions across multiple compiler toolchains without requiring separate code generation paths.

For information about the code generation pipeline that produces the pragma header, see [Code Generation Pipeline](#6.1.1). For details on how these pragmas are used within the generated kernels, see [Generated Kernel Structure](#6.1.2).

**Sources:** [third_party/gauxc/external/gau2grid/src/gau2grid/c_pragma.py:1-106](), [third_party/gauxc/external/gau2grid/generated_source/gau2grid/gau2grid_pragma.h:1-99]()

## Macro Abstraction Layer

The pragma system defines five primary abstraction macros that encapsulate compiler-specific functionality:

| Macro | Purpose | Return Type |
|-------|---------|-------------|
| `ALIGNED_MALLOC(alignment, size)` | Allocates memory aligned to specified byte boundary | `void*` |
| `ALIGNED_FREE(ptr)` | Frees memory allocated by ALIGNED_MALLOC | `void` |
| `ASSUME_ALIGNED(ptr, width)` | Hints to compiler that pointer is aligned | Statement |
| `PRAGMA_VECTORIZE` | Enables automatic vectorization of following loop | Statement |
| `PRAGMA_RESTRICT` | Declares pointer with no aliasing (restrict keyword) | Type qualifier |

These macros are defined differently for each supported compiler toolchain, providing uniform semantics while utilizing platform-specific intrinsics and directives.

**Sources:** [third_party/gauxc/external/gau2grid/generated_source/gau2grid/gau2grid_pragma.h:16-99]()

## Compiler Detection and Specialization

```mermaid
flowchart TD
    START["Pragma Header Inclusion"] --> NO_PRAGMA{__GG_NO_PRAGMA<br/>defined?}
    NO_PRAGMA -->|Yes| DISABLE["Disable all optimizations<br/>Use standard malloc/free<br/>No vectorization hints"]
    NO_PRAGMA -->|No| INTEL{__ICC or<br/>__INTEL_COMPILER?}
    
    INTEL -->|Yes| INTEL_IMPL["Intel Compiler<br/>_mm_malloc/_mm_free<br/>__assume_aligned<br/>_Pragma(vector)<br/>__restrict__"]
    
    INTEL -->|No| CLANG_MSVC{__clang__ and<br/>_MSC_VER?}
    CLANG_MSVC -->|Yes| CLANG_MSVC_IMPL["Clang-CL<br/>_aligned_malloc/_aligned_free<br/>__pragma(loop ivdep)<br/>__restrict"]
    
    CLANG_MSVC -->|No| CLANG{__clang__?}
    CLANG -->|Yes| CLANG_IMPL["Clang<br/>_mm_malloc/_mm_free<br/>_Pragma(clang loop vectorize)<br/>__restrict__"]
    
    CLANG -->|No| GCC_APPLE{__GNUC__ and<br/>__APPLE__?}
    GCC_APPLE -->|Yes| GCC_APPLE_IMPL["GCC on Darwin<br/>malloc/free (no aligned_alloc)<br/>_Pragma(GCC ivdep)<br/>__restrict__"]
    
    GCC_APPLE -->|No| GCC{__GNUC__ or<br/>__GNUG__?}
    GCC -->|Yes| GCC_IMPL["GCC<br/>aligned_alloc/free<br/>_Pragma(GCC ivdep)<br/>__restrict__"]
    
    GCC -->|No| MSVC{_MSC_VER?}
    MSVC -->|Yes| MSVC_IMPL["MSVC<br/>_aligned_malloc/_aligned_free<br/>__pragma(loop ivdep)<br/>__restrict"]
    
    MSVC -->|No| PGI{__PGI?}
    PGI -->|Yes| PGI_IMPL["PGI Compiler<br/>aligned_alloc/free<br/>_Pragma(ivdep)<br/>__restrict__"]
    
    PGI -->|No| FALLBACK["No compiler detected<br/>undefined behavior"]
```

**Diagram: Compiler Detection Flow**

The detection sequence is carefully ordered to handle compilers that define multiple preprocessor symbols. For example, Clang defines `__GNUC__`, so Clang detection must precede GCC detection to prevent misidentification.

**Sources:** [third_party/gauxc/external/gau2grid/generated_source/gau2grid/gau2grid_pragma.h:16-99]()

## Memory Allocation Abstractions

### ALIGNED_MALLOC and ALIGNED_FREE

Aligned memory allocation is critical for SIMD vectorization performance. The abstraction handles platform-specific allocation functions:

```mermaid
graph LR
    subgraph "Intel Compiler"
        IM["_mm_malloc(size, alignment)"]
        IF["_mm_free(ptr)"]
    end
    
    subgraph "Clang/GCC Linux"
        CM["aligned_alloc(alignment, size)"]
        CF["free(ptr)"]
    end
    
    subgraph "MSVC/Clang-CL"
        MM["_aligned_malloc(size, alignment)"]
        MF["_aligned_free(ptr)"]
    end
    
    subgraph "GCC Darwin"
        DM["malloc(size)<br/>(unaligned)"]
        DF["free(ptr)"]
    end
    
    subgraph "Disabled"
        NM["malloc(size)"]
        NF["free(ptr)"]
    end
    
    MALLOC["ALIGNED_MALLOC"] --> IM
    MALLOC --> CM
    MALLOC --> MM
    MALLOC --> DM
    MALLOC --> NM
    
    FREE["ALIGNED_FREE"] --> IF
    FREE --> CF
    FREE --> MF
    FREE --> DF
    FREE --> NF
```

**Diagram: Memory Allocation Macro Expansion by Compiler**

**Parameter Order Variation:** Note that `_mm_malloc` and `_aligned_malloc` reverse the order of `size` and `alignment` parameters. The macro interface normalizes this to `(alignment, size)` order, with implementation-specific reordering.

**Sources:** [third_party/gauxc/external/gau2grid/generated_source/gau2grid/gau2grid_pragma.h:19-20,29-30,39-40,50-51,60-61,70-71,80-81,91-92]()

### ASSUME_ALIGNED

The `ASSUME_ALIGNED` macro provides compiler hints that a pointer is aligned to a specific boundary:

| Compiler | Implementation | Effect |
|----------|---------------|--------|
| Intel | `__assume_aligned(ptr, width)` | Enables aligned load/store instructions |
| Clang | Empty (no-op) | Relies on allocation alignment |
| GCC | Empty (no-op) | Relies on allocation alignment |
| MSVC | Empty (no-op) | Relies on allocation alignment |
| PGI | Empty (no-op) | Relies on allocation alignment |
| Disabled | Empty (no-op) | No optimization |

Only Intel compilers provide explicit alignment assumption intrinsics. Other compilers infer alignment from allocation or generate conservative code.

**Sources:** [third_party/gauxc/external/gau2grid/generated_source/gau2grid/gau2grid_pragma.h:21,31,38,49,59,69,79,90]()

## Vectorization and Optimization Pragmas

### PRAGMA_VECTORIZE

The vectorization macro instructs compilers to auto-vectorize loops using SIMD instructions:

```mermaid
graph TB
    PV["PRAGMA_VECTORIZE"] --> INTEL["_Pragma(&quot;vector&quot;)<br/>Intel: Aggressive vectorization"]
    PV --> CLANG["_Pragma(&quot;clang loop vectorize(enable)&quot;)<br/>Clang: Force vectorization"]
    PV --> GCC["_Pragma(&quot;GCC ivdep&quot;)<br/>GCC: Ignore vector dependencies"]
    PV --> MSVC["__pragma(loop(ivdep))<br/>MSVC: Independent loop iterations"]
    PV --> PGI["_Pragma(&quot;ivdep&quot;)<br/>PGI: Independent vector dependencies"]
    PV --> DISABLED["Empty<br/>No vectorization hint"]
```

**Diagram: Vectorization Pragma Expansion**

**Semantic Differences:**
- **Intel `vector`**: Most aggressive, may reorder operations
- **Clang `vectorize(enable)`**: Enables vectorization even if cost model suggests against it
- **GCC/PGI `ivdep`**: Asserts no loop-carried dependencies
- **MSVC `loop(ivdep)`**: Asserts iterations are independent

**Sources:** [third_party/gauxc/external/gau2grid/generated_source/gau2grid/gau2grid_pragma.h:23,33,43,54,64,74,84,95]()

### PRAGMA_RESTRICT

The `PRAGMA_RESTRICT` macro provides the C99 `restrict` keyword equivalent for each compiler:

| Compiler | Keyword | Standard |
|----------|---------|----------|
| Intel | `__restrict__` | GNU extension |
| Clang | `__restrict__` | GNU extension |
| GCC | `__restrict__` | GNU extension |
| MSVC/Clang-CL | `__restrict` | MSVC extension |
| PGI | `__restrict__` | GNU extension |
| Disabled | Empty | No aliasing hints |

This qualifier enables compilers to assume pointer arguments do not alias, permitting more aggressive optimizations such as reordering memory operations.

**Sources:** [third_party/gauxc/external/gau2grid/generated_source/gau2grid/gau2grid_pragma.h:24,34,44,55,65,75,85,96]()

## Pragma Header Generation

The pragma header is generated by Python code during the build process:

```mermaid
sequenceDiagram
    participant CG as c_generator.py
    participant CP as c_pragma.py
    participant File as gau2grid_pragma.h
    
    CG->>CG: generate_c_gau2grid()
    CG->>CP: build_pragma_header(gg_pragma)
    CP->>CP: Process _pragma_data template
    loop Each line in template
        CP->>File: Write preprocessor directive
    end
    CP-->>CG: Return
    CG->>File: Write complete header
```

**Diagram: Pragma Header Generation Sequence**

The generation occurs in the `generate_c_gau2grid` function:

1. Creates a `CodeGen` object for the pragma header ([c_generator.py:68]())
2. Calls `c_pragma.build_pragma_header(gg_pragma)` ([c_generator.py:95]())
3. Writes the header to `gau2grid/gau2grid_pragma.h` ([c_generator.py:314]())

**Sources:** [third_party/gauxc/external/gau2grid/src/gau2grid/c_generator.py:68,95,314](), [third_party/gauxc/external/gau2grid/src/gau2grid/c_pragma.py:100-106]()

## Usage in Generated Code

The generated collocation kernels use these macros extensively to enable platform-optimized execution:

### Memory Allocation Pattern

```mermaid
graph LR
    subgraph "Initialization"
        A1["ALIGNED_MALLOC<br/>cache_data<br/>64-byte aligned"]
        A2["ALIGNED_MALLOC<br/>expn1, expn2<br/>Primitive exponents"]
        A3["ALIGNED_MALLOC<br/>phi_tmp arrays<br/>Output temporaries"]
    end
    
    subgraph "Alignment Hints"
        B1["ASSUME_ALIGNED<br/>xc, yc, zc<br/>Coordinate arrays"]
        B2["ASSUME_ALIGNED<br/>R2, S0, S1<br/>Radial arrays"]
        B3["ASSUME_ALIGNED<br/>phi_tmp<br/>Output arrays"]
    end
    
    subgraph "Cleanup"
        C1["ALIGNED_FREE<br/>cache_data"]
        C2["ALIGNED_FREE<br/>expn1, expn2"]
        C3["ALIGNED_FREE<br/>phi_tmp arrays"]
    end
    
    A1 --> B1
    A2 --> B2
    A3 --> B3
    B1 --> C1
    B2 --> C2
    B3 --> C3
```

**Diagram: Memory Management Pattern in Generated Kernels**

Example from `gg_collocation_L0`:
- Allocate cache block: `ALIGNED_MALLOC(64, 192 * sizeof(double))` ([gau2grid_phi.c:41]())
- Assign aligned pointers: `ASSUME_ALIGNED(xc, 64)` ([gau2grid_phi.c:43]())
- Free on exit: `ALIGNED_FREE(cache_data)` ([gau2grid_phi.c:141]())

**Sources:** [third_party/gauxc/external/gau2grid/generated_source/gau2grid_phi.c:41-53,141]()

### Vectorization Annotations

The `PRAGMA_VECTORIZE` macro appears before all performance-critical inner loops:

**Example Usage Pattern:**
```c
// From gau2grid_deriv1.c:97-111
PRAGMA_VECTORIZE
for (unsigned long i = 0; i < remain; i++) {
    xc[i] = x[i] - center_x;
    yc[i] = y[i] - center_y;
    zc[i] = z[i] - center_z;
    
    R2[i] = xc[i] * xc[i];
    R2[i] += yc[i] * yc[i];
    R2[i] += zc[i] * zc[i];
    
    S0[i] = 0.0;
    S1[i] = 0.0;
}
```

The pragma enables compilers to generate SIMD instructions (SSE, AVX, AVX-512) for these loops.

**Sources:** [third_party/gauxc/external/gau2grid/generated_source/gau2grid_deriv1.c:97,115,138,250,268,291,303]()

### Restrict Qualifier Usage

Function signatures use `PRAGMA_RESTRICT` to prevent pointer aliasing:

**Function Signature Example:**
```c
void gg_collocation_L1_deriv1(
    const unsigned long npoints, 
    const double* PRAGMA_RESTRICT xyz,
    const unsigned long xyz_stride, 
    const int nprim, 
    const double* PRAGMA_RESTRICT coeffs,
    const double* PRAGMA_RESTRICT exponents,
    const double* PRAGMA_RESTRICT center,
    const int order, 
    double* PRAGMA_RESTRICT phi_out,
    double* PRAGMA_RESTRICT phi_x_out,
    double* PRAGMA_RESTRICT phi_y_out,
    double* PRAGMA_RESTRICT phi_z_out
)
```

This guarantees to the compiler that `xyz`, `coeffs`, `exponents`, `center`, and output arrays do not overlap in memory, enabling aggressive optimization.

**Sources:** [third_party/gauxc/external/gau2grid/generated_source/gau2grid_deriv1.c:178](), [third_party/gauxc/external/gau2grid/src/gau2grid/c_generator.py:392-403]()

## Integration with Code Generation

The pragma system integrates into the code generation pipeline through standard includes:

```mermaid
flowchart LR
    subgraph "Python Generation"
        GEN["c_generator.py<br/>generate_c_gau2grid()"]
        PRAGMA["c_pragma.py<br/>build_pragma_header()"]
    end
    
    subgraph "Generated Headers"
        PH["gau2grid_pragma.h<br/>Macro definitions"]
        GH["gau2grid.h<br/>Function declarations"]
        UH["gau2grid_utility.h<br/>Helper functions"]
    end
    
    subgraph "Generated Sources"
        PHI["gau2grid_phi.c"]
        D1["gau2grid_deriv1.c"]
        D2["gau2grid_deriv2.c"]
        D3["gau2grid_deriv3.c"]
    end
    
    GEN -->|Generates| PH
    PRAGMA -->|Provides template| PH
    GEN -->|Generates| GH
    GEN -->|Generates| UH
    GEN -->|Generates| PHI
    GEN -->|Generates| D1
    GEN -->|Generates| D2
    GEN -->|Generates| D3
    
    PH -.->|#include| PHI
    PH -.->|#include| D1
    PH -.->|#include| D2
    PH -.->|#include| D3
    
    GH -.->|#include| PHI
    GH -.->|#include| D1
    
    UH -.->|#include| PHI
```

**Diagram: Pragma System Integration in Build Pipeline**

All generated C files include the pragma header:
```c
#include "gau2grid/gau2grid.h"
#include "gau2grid/gau2grid_utility.h"
#include "gau2grid/gau2grid_pragma.h"
```

**Sources:** [third_party/gauxc/external/gau2grid/src/gau2grid/c_generator.py:113-116](), [third_party/gauxc/external/gau2grid/generated_source/gau2grid_phi.c:19-21]()

## Design Rationale

The pragma abstraction layer addresses several critical requirements:

### Cross-Platform Compatibility

Different platforms provide different mechanisms for aligned allocation:
- **POSIX (Linux, Unix)**: `aligned_alloc()` from C11
- **macOS**: Standard `malloc()` only (no `aligned_alloc()`)
- **Windows**: `_aligned_malloc()` from CRT
- **Intel**: `_mm_malloc()` from compiler intrinsics

The abstraction ensures generated code compiles and runs optimally on all platforms without conditional compilation in the generated kernels.

### Performance Portability

Vectorization hints differ semantically across compilers:
- Some compilers (`ivdep`) only assert independence
- Others (`vector`, `vectorize(enable)`) actively force vectorization
- The abstraction allows each compiler to use its most effective directive

### Maintainability

Generated code uses consistent macro names (`PRAGMA_VECTORIZE`, `ALIGNED_MALLOC`) rather than compiler-specific syntax. This:
- Simplifies code generation templates
- Makes generated code more readable
- Localizes platform-specific knowledge to a single header

### Fallback Safety

The `__GG_NO_PRAGMA` path provides a safety valve for platforms with problematic pragma support, allowing compilation to succeed (albeit without optimizations) on any C99-compliant compiler.

**Sources:** [third_party/gauxc/external/gau2grid/src/gau2grid/c_pragma.py:1-106]()

## Compiler Support Matrix

| Compiler | Version Tested | SIMD Support | Aligned Alloc | Restrict | Notes |
|----------|----------------|--------------|---------------|----------|-------|
| Intel ICC | 18.0+ | AVX, AVX-512 | `_mm_malloc` | `__restrict__` | Best vectorization |
| Clang | 8.0+ | SSE, AVX | `_mm_malloc` | `__restrict__` | Requires explicit enable |
| GCC | 7.0+ | SSE, AVX | `aligned_alloc` | `__restrict__` | Strong `ivdep` |
| MSVC | 2017+ | SSE, AVX | `_aligned_malloc` | `__restrict` | Limited vectorization |
| PGI | 19.0+ | SSE, AVX | `aligned_alloc` | `__restrict__` | HPC-focused |
| AppleClang | 10.0+ | SSE, AVX | `malloc` | `__restrict__` | No aligned_alloc |

The system automatically detects and configures for each compiler at compile time through preprocessor macros.

**Sources:** [third_party/gauxc/external/gau2grid/generated_source/gau2grid/gau2grid_pragma.h:26-96]()

---

