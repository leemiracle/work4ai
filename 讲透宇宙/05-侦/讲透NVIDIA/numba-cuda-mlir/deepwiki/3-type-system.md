<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/numba-cuda-mlir · page 3 Type System · fetched 2026-10-26 -->

# Type System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/numba_cuda_mlir/numba_cuda/np/numpy_support.py](src/numba_cuda_mlir/numba_cuda/np/numpy_support.py)
- [src/numba_cuda_mlir/numba_cuda/typeconv/rules.py](src/numba_cuda_mlir/numba_cuda/typeconv/rules.py)
- [src/numba_cuda_mlir/numba_cuda/types/__init__.py](src/numba_cuda_mlir/numba_cuda/types/__init__.py)
- [src/numba_cuda_mlir/numba_cuda/types/abstract.py](src/numba_cuda_mlir/numba_cuda/types/abstract.py)
- [src/numba_cuda_mlir/numba_cuda/typing/npydecl.py](src/numba_cuda_mlir/numba_cuda/typing/npydecl.py)
- [src/numba_cuda_mlir/types.py](src/numba_cuda_mlir/types.py)

</details>



The `numba-cuda-mlir` type system provides a bridge between high-level Python/NumPy types and the low-level MLIR representation required for CUDA kernel generation. It extends the standard Numba type hierarchy to support CUDA-specific hardware features, such as reduced-precision floats and specialized memory layouts.

The system is centered around the `Type` base class [src/numba_cuda_mlir/numba_cuda/types/abstract.py:87-93](), which uses a metaclass-based interning mechanism to ensure type stability and fast matching during dispatch.

### Type Representation and Interning

All types in the system inherit from `Type`. To optimize performance and ensure that type comparisons are efficient, the system employs the `_TypeMetaclass` [src/numba_cuda_mlir/numba_cuda/types/abstract.py:38-44](). This metaclass interns every type instance into a global `_typecache` [src/numba_cuda_mlir/numba_cuda/types/abstract.py:31](), assigning a unique integer `_code` to each distinct type [src/numba_cuda_mlir/numba_cuda/types/abstract.py:63-65]().

#### Type System Entity Mapping
The following diagram illustrates how Python-level types are mapped to internal Numba/MLIR type representations.

```mermaid
graph TD
    subgraph "Python/NumPy Space"
        NP_DTYPE["np.dtype('float32')"]
        PY_FLOAT["float"]
        NP_ARRAY["np.ndarray"]
    end

    subgraph "Code Entity Space (numba_cuda_mlir)"
        NB_TYPE["Type (abstract.py)"]
        NB_FLOAT["Float (scalars.py)"]
        NB_ARRAY["Array (npytypes.py)"]
        METACLASS["_TypeMetaclass"]
        CACHE["_typecache (weakref)"]
    end

    NP_DTYPE -->|from_dtype| NB_FLOAT
    PY_FLOAT -->|inference| NB_FLOAT
    NP_ARRAY -->|inference| NB_ARRAY
    NB_FLOAT --|> NB_TYPE
    NB_ARRAY --|> NB_TYPE
    NB_TYPE -->|managed by| METACLASS
    METACLASS -->|interns into| CACHE
```
**Sources:** [src/numba_cuda_mlir/numba_cuda/types/abstract.py:31-76](), [src/numba_cuda_mlir/numba_cuda/np/numpy_support.py:53-69]()

---

### Core Types and NumPy Support
The compiler supports a wide range of standard Numba types including `Integer`, `Float`, `Complex`, `Array`, and `Record` [src/numba_cuda_mlir/types.py:31-93](). 

Key capabilities include:
*   **DType Mapping:** Conversion between NumPy `dtype` objects and Numba types via `from_dtype` [src/numba_cuda_mlir/numba_cuda/np/numpy_support.py:178-179]().
*   **Type Promotion:** Automatic promotion rules (e.g., `int32` to `int64` or `float32` to `float64`) managed by the `TypeCastingRules` [src/numba_cuda_mlir/numba_cuda/typeconv/rules.py:18-62]().
*   **Ufunc Support:** Logic for matching NumPy ufunc loops to specific type signatures [src/numba_cuda_mlir/numba_cuda/typing/npydecl.py:93-121]().

For details, see [Core Types and NumPy Support](#3.1).

---

### CUDA-Specific Types
To leverage NVIDIA hardware, the type system introduces types that do not exist in standard Python or NumPy:
*   **Reduced Precision:** Support for `bfloat16`, `tf32`, and various `fp8` formats (e.g., `E4M3`, `E5M2`) [src/numba_cuda_mlir/types.py:152-166]().
*   **Opaque CUDA Types:** Types like `CUTensorMap` for Hopper TMA support [src/numba_cuda_mlir/types.py:172-176]().
*   **Type Attributes:** Decorators like `grid_constant` and `alignas` that attach metadata to types for use during MLIR lowering [src/numba_cuda_mlir/types.py:125-136]().

For details, see [CUDA-Specific Types](#3.2).

---

### Typing Infrastructure
The typing infrastructure handles the resolution of function calls and operators. It uses a registry-based system where `FunctionTemplate` and `AbstractTemplate` define how Python functions should be typed based on their arguments [src/numba_cuda_mlir/numba_cuda/typing/npydecl.py:30-41]().

#### Dispatch and Resolution Flow
This diagram shows how the `MLIRTypingContext` interacts with templates to resolve a function signature.

```mermaid
graph LR
    subgraph "Typing Registry"
        REG["Registry (templates.py)"]
        TMPL["AbstractTemplate"]
    end

    subgraph "Resolution Logic"
        CTX["MLIRTypingContext"]
        SIG["Signature"]
    end

    REG -->|stores| TMPL
    CTX -->|looks up| REG
    TMPL -->|generic()| SIG
    SIG -->|returns to| CTX
```
**Sources:** [src/numba_cuda_mlir/numba_cuda/typing/npydecl.py:24-30](), [src/numba_cuda_mlir/numba_cuda/typing/templates.py:7-12]()

For details, see [Typing Infrastructure](#3.3).

---

### Summary of Type Aliases
The system provides numerous aliases to match both C-style and NumPy-style naming conventions:

| Category | Aliases | Source |
| :--- | :--- | :--- |
| **Fixed-width Ints** | `i1`, `i4`, `i8`, `u1`, `u4`, `u8` | [src/numba_cuda_mlir/numba_cuda/types/__init__.py:132-140]() |
| **Floats** | `f2` (f16), `f4` (f32), `f8` (f64) | [src/numba_cuda_mlir/numba_cuda/types/__init__.py:142-144]() |
| **CUDA Specials** | `bf16`, `tf32`, `nvfp4` | [src/numba_cuda_mlir/types.py:152-166]() |
| **Pointers** | `voidptr`, `ptr`, `byval_ptr` | [src/numba_cuda_mlir/types.py:167-169]() |

**Sources:**
* `src/numba_cuda_mlir/types.py`
* `src/numba_cuda_mlir/numba_cuda/types/abstract.py`
* `src/numba_cuda_mlir/numba_cuda/types/__init__.py`
* `src/numba_cuda_mlir/numba_cuda/np/numpy_support.py`
* `src/numba_cuda_mlir/numba_cuda/typeconv/rules.py`

---

