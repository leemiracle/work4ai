<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/numbast · page 3 Numbast: Binding Generation Core · fetched 2026-10-26 -->

# Numbast: Binding Generation Core

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yaml](.github/workflows/ci.yaml)
- [.github/workflows/pr.yaml](.github/workflows/pr.yaml)
- [README.md](README.md)
- [ast_canopy/README.md](ast_canopy/README.md)
- [ci/detect_test_paths.py](ci/detect_test_paths.py)
- [ci/run_tests.py](ci/run_tests.py)
- [docs/source/quickstart.rst](docs/source/quickstart.rst)
- [numbast/README.md](numbast/README.md)
- [numbast/src/numbast/__init__.py](numbast/src/numbast/__init__.py)
- [numbast/src/numbast/experimental/mlir/tests/conftest.py](numbast/src/numbast/experimental/mlir/tests/conftest.py)
- [numbast/src/numbast/experimental/mlir/tools/tests/test_symbol_exposure.py](numbast/src/numbast/experimental/mlir/tools/tests/test_symbol_exposure.py)
- [numbast/src/numbast/function.py](numbast/src/numbast/function.py)
- [numbast/src/numbast/struct.py](numbast/src/numbast/struct.py)

</details>



The `numbast` package provides the core logic for translating C++ declarations (parsed by `ast_canopy`) into Numba-compatible Python bindings. It automates the generation of Numba typing templates, lowering implementations, and C++ shim code required to bridge the Python/C++ boundary in CUDA kernels [numbast/README.md:1-7]().

### Binding Pipeline Overview

The system operates by consuming `ast_canopy` declaration objects and registering them within Numba's internal registries. The pipeline follows a structured sequence to ensure C++ types and functions are correctly represented in Numba's IR and data models.

#### Natural Language to Code Entity Space: Core Pipeline
| Concept | Code Entity | File Reference |
|:---|:---|:---|
| **Binding Entrypoint** | `bind_cxx_struct`, `bind_cxx_function` | [numbast/src/numbast/__init__.py:17-28]() |
| **Type Mapping** | `to_numba_type`, `to_numba_arg_type` | [numbast/src/numbast/types.py]() |
| **Call Bridge** | `FunctionCallConv` | [numbast/src/numbast/callconv.py:23-23]() |
| **Shim Generation** | `MemoryShimWriter`, `FileShimWriter` | [numbast/src/numbast/shim_writer.py:45-46]() |
| **Intent Analysis** | `compute_intent_plan`, `ArgIntent` | [numbast/src/numbast/intent.py:26-26]() |

#### Binding System Architecture
```mermaid
graph TD
    subgraph "Input Layer"
        A["ast_canopy.decl.Struct"] --> D
        B["ast_canopy.decl.Function"] --> D
        C["ast_canopy.decl.ClassTemplate"] --> D
    end

    subgraph "Numbast Core Engine"
        D["Binding Dispatcher"] --> E["Type Registry (types.py)"]
        D --> F["Shim Generator (shim_writer.py)"]
        D --> G["Call Convention (callconv.py)"]
        G --> H["Intent Planner (intent.py)"]
    end

    subgraph "Numba Integration"
        E --> I["register_model"]
        G --> J["@lower"]
        F --> K["shim_writer.links()"]
    end

    Sources: ["numbast/src/numbast/struct.py:25-34", "numbast/src/numbast/function.py:16-23"]
```

---

### Operational Modes

Numbast supports two primary workflows depending on whether the C++ environment is available at runtime [numbast/README.md:31-34]().

#### 1. Dynamic Binding Generation
Used for development and experimentation. It parses headers and registers bindings at runtime. This mode requires `ast_canopy`, `Clang`, and CUDA headers to be present on the system executing the Python code [numbast/README.md:35-40]().
*   **Key Functions:** `bind_cxx_struct`, `bind_cxx_function`.
*   **Shim Management:** Uses `MemoryShimWriter` to store generated C++ shims in memory for just-in-time linking [numbast/src/numbast/struct.py:34]().

#### 2. Static Binding Generation
Used for production packaging. A CLI tool generates a standalone Python module containing all Numba registration logic and a static C++ shim file [numbast/README.md:60-65]().
*   **CLI:** `python -m numbast --cfg-path config.yml` [numbast/README.md:66-68]().
*   **Benefit:** End users do not need `ast_canopy` or `Clang` at runtime.

---

### Major Subsystems

#### [Dynamic Binding: bind_cxx_struct and bind_cxx_function](#3.1)
Details the lifecycle of a binding, including how C++ constructors are mapped to Numba `lower` calls [numbast/src/numbast/struct.py:63-148]() and how operator overloads (e.g., `+`, `*`) are mapped to Python operators [numbast/src/numbast/function.py:78-81]().

#### [Template Binding: Class and Function Templates](#3.2)
Explains the management of C++ templates. Numbast handles on-the-fly specialization by materializing concrete types when Numba encounters specific template arguments at runtime [numbast/src/numbast/__init__.py:33-40]().

#### [Type System: C++ to Numba Type Mapping](#3.3)
Covers the translation layer between C++ types and Numba types. It utilizes `CTYPE_MAPS` to resolve fundamental types and handles complex scenarios like pointers, references, and CUDA-specific vector types [numbast/src/numbast/struct.py:25]().

#### [Shim Writer and Call Convention](#3.4)
The `ShimWriter` abstraction (e.g., `MemoryShimWriter`) manages the accumulation of C++ source code needed to bridge Python calls to C++ device functions [numbast/src/numbast/shim_writer.py:45-46](). `FunctionCallConv` manages the LLVM IR generation to invoke these shims [numbast/src/numbast/callconv.py:23-23]().

#### [Argument Intents](#3.5)
The `ArgIntent` system allows users to define how C++ reference parameters should behave in Python (e.g., as input, output, or returned values) via `compute_intent_plan` [numbast/src/numbast/intent.py:26-26]().

---

### Code Entity Space: Class Roles
```mermaid
classDiagram
    class bind_cxx_struct {
        +registers_model()
        +bind_ctors()
        +bind_methods()
    }
    class bind_cxx_function {
        +resolves_overloads()
        +creates_shim()
        +registers_lowering()
    }
    class FunctionCallConv {
        +builder
        +context
        +__call__(sig, args)
    }
    class ShimWriter {
        +add_shim(code)
        +links()
    }

    bind_cxx_struct --> ShimWriter : uses
    bind_cxx_function --> FunctionCallConv : creates
    FunctionCallConv --> ShimWriter : references code

    Sources: ["numbast/src/numbast/struct.py:63-86", "numbast/src/numbast/function.py:125-155", "numbast/src/numbast/callconv.py:23-23"]
```

**Sources:**
- [numbast/src/numbast/struct.py:1-190]()
- [numbast/src/numbast/function.py:1-205]()
- [numbast/src/numbast/__init__.py:1-80]()
- [numbast/README.md:1-95]()

---

