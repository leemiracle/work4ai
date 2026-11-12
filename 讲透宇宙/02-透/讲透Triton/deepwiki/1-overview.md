> 来源: [https://deepwiki.com/triton-lang/triton/1-overview](https://deepwiki.com/triton-lang/triton/1-overview)
> DeepWiki triton-lang/triton | Last indexed: 20 August 2026 (f89384

# Overview

  Relevant source files 
 - [.github/workflows/llvm-build.yml](https://github.com/triton-lang/triton/blob/f893845b/.github/workflows/llvm-build.yml)
 - [.github/workflows/wheels.yml](https://github.com/triton-lang/triton/blob/f893845b/.github/workflows/wheels.yml)
 - [.gitignore](https://github.com/triton-lang/triton/blob/f893845b/.gitignore)
 - [README.md](https://github.com/triton-lang/triton/blob/f893845b/README.md?plain=1)
 - [cmake/llvm-build-info.json](https://github.com/triton-lang/triton/blob/f893845b/cmake/llvm-build-info.json)
 - [docs/getting-started/installation.rst](https://github.com/triton-lang/triton/blob/f893845b/docs/getting-started/installation.rst)
 - [docs/python-api/triton-semantics.rst](https://github.com/triton-lang/triton/blob/f893845b/docs/python-api/triton-semantics.rst)
 - [docs/python-api/triton.language.rst](https://github.com/triton-lang/triton/blob/f893845b/docs/python-api/triton.language.rst)
 - [lib/Conversion/TritonToTritonGPU/TritonToTritonGPUPass.cpp](https://github.com/triton-lang/triton/blob/f893845b/lib/Conversion/TritonToTritonGPU/TritonToTritonGPUPass.cpp)
 - [python/src/ir.cc](https://github.com/triton-lang/triton/blob/f893845b/python/src/ir.cc)
 - [python/test/unit/language/test_core.py](https://github.com/triton-lang/triton/blob/f893845b/python/test/unit/language/test_core.py)
 - [python/test/unit/language/test_frontend.py](https://github.com/triton-lang/triton/blob/f893845b/python/test/unit/language/test_frontend.py)
 - [python/test/unit/runtime/test_cache.py](https://github.com/triton-lang/triton/blob/f893845b/python/test/unit/runtime/test_cache.py)
 - [python/triton/compiler/code_generator.py](https://github.com/triton-lang/triton/blob/f893845b/python/triton/compiler/code_generator.py)
 - [python/triton/compiler/compiler.py](https://github.com/triton-lang/triton/blob/f893845b/python/triton/compiler/compiler.py)
 - [python/triton/language/__init__.py](https://github.com/triton-lang/triton/blob/f893845b/python/triton/language/__init__.py)
 - [python/triton/language/core.py](https://github.com/triton-lang/triton/blob/f893845b/python/triton/language/core.py)
 - [python/triton/language/semantic.py](https://github.com/triton-lang/triton/blob/f893845b/python/triton/language/semantic.py)
 - [python/triton/runtime/interpreter.py](https://github.com/triton-lang/triton/blob/f893845b/python/triton/runtime/interpreter.py)
 - [python/triton/runtime/jit.py](https://github.com/triton-lang/triton/blob/f893845b/python/triton/runtime/jit.py)
 - [scripts/build-llvm-project.sh](https://github.com/triton-lang/triton/blob/f893845b/scripts/build-llvm-project.sh)
 
  
## Purpose and Scope

 This document introduces the Triton compiler system, explaining its purpose as a domain-specific language (DSL) and compiler infrastructure for GPU programming. It provides a high-level summary of Triton's architecture, compilation flow, and key components to help developers understand how Python kernel code transforms into optimized GPU binaries.

 For detailed information about specific subsystems:

 
 - System architecture and compilation stages: see [System Architecture and Compilation Flow](https://deepwiki.com/triton-lang/triton/1.1-system-architecture-and-compilation-flow)
 - Repository organization: see [Repository Structure](https://deepwiki.com/triton-lang/triton/1.2-repository-structure)
 - Python language API: see [Triton Language Core (triton.language)](https://deepwiki.com/triton-lang/triton/2.1-triton-language-core-(triton.language))
 - MLIR dialects: see [MLIR Dialects and IR System](https://deepwiki.com/triton-lang/triton/3-mlir-dialects-and-ir-system)
 - Backend compilation: see [Backend Compilation and Code Generation](https://deepwiki.com/triton-lang/triton/5-backend-compilation-and-code-generation)
 
 **Sources:** [README.md23-29](https://github.com/triton-lang/triton/blob/f893845b/README.md?plain=1#L23-L29) [python/triton/language/core.py1-20](https://github.com/triton-lang/triton/blob/f893845b/python/triton/language/core.py#L1-L20)

 
---

 
## What is Triton?

 Triton is an open-source language and compiler for writing custom deep-learning primitives that execute on GPUs. It provides:

 
 - **A Python-embedded DSL**: Users write GPU kernels in Python using the `triton.language` API [python/triton/language/core.py122-136](https://github.com/triton-lang/triton/blob/f893845b/python/triton/language/core.py#L122-L136)
 - **High-level abstractions**: Block-based tensor operations instead of low-level thread management [python/triton/language/core.py17-18](https://github.com/triton-lang/triton/blob/f893845b/python/triton/language/core.py#L17-L18)
 - **Multi-backend support**: Targets NVIDIA GPUs (CUDA) and AMD GPUs (ROCm/HIP) [python/triton/compiler/compiler.py5-7](https://github.com/triton-lang/triton/blob/f893845b/python/triton/compiler/compiler.py#L5-L7)
 - **Automatic optimization**: Layout optimization, memory coalescing, and operation fusion.
 - **JIT compilation**: Kernels are compiled at runtime with specialization and caching [python/triton/runtime/jit.py136-154](https://github.com/triton-lang/triton/blob/f893845b/python/triton/runtime/jit.py#L136-L154)
 
 The primary goal is to enable higher productivity than CUDA while maintaining performance and flexibility compared to other DSLs [README.md23-29](https://github.com/triton-lang/triton/blob/f893845b/README.md?plain=1#L23-L29)

 **Key Design Principle**: Users write kernels at the tensor-block level (e.g., processing blocks defined by `tl.arange`), and the compiler handles mapping to GPU hardware threads, memory hierarchies, and specialized instructions [python/triton/language/core.py98-114](https://github.com/triton-lang/triton/blob/f893845b/python/triton/language/core.py#L98-L114)

 **Sources:** [README.md23-29](https://github.com/triton-lang/triton/blob/f893845b/README.md?plain=1#L23-L29) [python/triton/language/core.py122-136](https://github.com/triton-lang/triton/blob/f893845b/python/triton/language/core.py#L122-L136) [python/triton/runtime/jit.py136-154](https://github.com/triton-lang/triton/blob/f893845b/python/triton/runtime/jit.py#L136-L154)

 
---

 
## High-Level Architecture

 
### System Layers

 
```

```

 **Triton Architecture: From Python to GPU Execution**

 The architecture consists of five major layers:

 
| Layer | Key Components | Purpose |
|---|---|---|
| User Space | Python source with @triton.jit | Kernel definition python/triton/runtime/jit.py136-142 |
| Frontend | triton.language, JITFunction, CodeGenerator | Parse, validate, generate IR python/triton/compiler/code_generator.py131-149 |
| IR Transformations | TTIR → TTGIR → LLIR | Progressive lowering with optimizations python/triton/compiler/compiler.py78-82 |
| Backend | PTX/AMDGCN generation, assembly | Hardware-specific code generation python/triton/compiler/compiler.py143-146 |
| Runtime | Driver, cache system | Execution and management python/triton/runtime/cache.py18-19 |

 **Sources:** [python/triton/runtime/jit.py136-154](https://github.com/triton-lang/triton/blob/f893845b/python/triton/runtime/jit.py#L136-L154) [python/triton/compiler/compiler.py78-82](https://github.com/triton-lang/triton/blob/f893845b/python/triton/compiler/compiler.py#L78-L82) [python/triton/compiler/code_generator.py131-149](https://github.com/triton-lang/triton/blob/f893845b/python/triton/compiler/code_generator.py#L131-L149)

 
---

 
## Compilation Pipeline

 
### End-to-End Flow with Code Entities

 
```

```

 **Compilation Pipeline: IR Transformation Stages**

 
### Pipeline Stages

 **1. Frontend Parsing** (`CodeGenerator`)

 
 - Visits Python AST nodes using `ast.NodeVisitor` [python/triton/compiler/code_generator.py1-7](https://github.com/triton-lang/triton/blob/f893845b/python/triton/compiler/code_generator.py#L1-L7)
 - Builds MLIR operations via `ir.builder` [python/triton/compiler/code_generator.py131-149](https://github.com/triton-lang/triton/blob/f893845b/python/triton/compiler/code_generator.py#L131-L149)
 - Performs semantic analysis through `TritonSemantic` class [python/triton/language/semantic.py26-34](https://github.com/triton-lang/triton/blob/f893845b/python/triton/language/semantic.py#L26-L34)
 
 **2. TTIR Generation** (`ASTSource.make_ir`)

 
 - Converts Python AST to Triton dialect operations [python/triton/compiler/compiler.py78-82](https://github.com/triton-lang/triton/blob/f893845b/python/triton/compiler/compiler.py#L78-L82)
 - Operations: `tt.load`, `tt.store`, `tt.dot`, `tt.reduce` [python/triton/language/__init__.py31-126](https://github.com/triton-lang/triton/blob/f893845b/python/triton/language/__init__.py#L31-L126)
 
 **3. TTGIR Lowering**

 
 - Adds layout encoding attributes to tensors.
 - Converts `tt.*` ops to `ttg.*` ops.
 
 **4. Optimization Passes**

 
 - Layout propagation, memory optimization, pipelining.
 - Backend-specific transformations configured in backend implementations.
 
 **5. LLVM Lowering**

 
 - Converts TTGIR to LLVM IR.
 - Maps layouts to thread/warp operations.
 
 **6. Binary Generation**

 
 - NVIDIA: LLVM IR → PTX → `ptxas` → cubin [python/triton/compiler/compiler.py143-146](https://github.com/triton-lang/triton/blob/f893845b/python/triton/compiler/compiler.py#L143-L146)
 - AMD: LLVM IR → AMDGCN → `llvm-mc` → hsaco [python/triton/compiler/compiler.py143-146](https://github.com/triton-lang/triton/blob/f893845b/python/triton/compiler/compiler.py#L143-L146)
 
 **Sources:** [python/triton/compiler/compiler.py78-82](https://github.com/triton-lang/triton/blob/f893845b/python/triton/compiler/compiler.py#L78-L82) [python/triton/compiler/code_generator.py131-149](https://github.com/triton-lang/triton/blob/f893845b/python/triton/compiler/code_generator.py#L131-L149) [python/triton/language/semantic.py26-34](https://github.com/triton-lang/triton/blob/f893845b/python/triton/language/semantic.py#L26-L34)

 
---

 
## Key Components

 
### Core Classes and Modules

 
| Component | Location | Purpose |
|---|---|---|
| JITFunction | python/triton/runtime/jit.py108-113 | Wraps kernel function, manages compilation and caching |
| CodeGenerator | python/triton/compiler/code_generator.py129-150 | Converts Python AST to Triton MLIR |
| TritonSemantic | python/triton/language/semantic.py26-34 | Type checking and semantic analysis |
| ASTSource | python/triton/compiler/compiler.py52-82 | Container for Python source and metadata during compilation |
| tensor | python/triton/language/core.py50-91 | Fundamental tensor type in language |

 
### Language API Surface

 The `triton.language` module provides the user-facing API [python/triton/language/__init__.py1-288](https://github.com/triton-lang/triton/blob/f893845b/python/triton/language/__init__.py#L1-L288):

 
```

```

 **Sources:** [python/triton/language/__init__.py1-288](https://github.com/triton-lang/triton/blob/f893845b/python/triton/language/__init__.py#L1-L288) [python/triton/language/core.py122-136](https://github.com/triton-lang/triton/blob/f893845b/python/triton/language/core.py#L122-L136)

 
---

 
## Programming Model

 
### Kernel Definition and Execution

 **Kernel Structure:** Kernels are defined using the `@triton.jit` decorator [python/triton/runtime/jit.py108-113](https://github.com/triton-lang/triton/blob/f893845b/python/triton/runtime/jit.py#L108-L113) They operate on blocks of data using the `tl.tensor` type.

 **Execution Model:**

 
 - Kernels are launched with a grid specification (e.g., `(1, )`) [python/test/unit/language/test_core.py160](https://github.com/triton-lang/triton/blob/f893845b/python/test/unit/language/test_core.py#L160-L160)
 - Each program instance processes a block of data.
 - The `program_id` identifies which block this instance handles [python/triton/language/semantic.py39-42](https://github.com/triton-lang/triton/blob/f893845b/python/triton/language/semantic.py#L39-L42)
 - Compilation happens on first invocation, results are cached in the `FileCacheManager` or `RemoteCacheManager` [python/test/unit/runtime/test_cache.py18-19](https://github.com/triton-lang/triton/blob/f893845b/python/test/unit/runtime/test_cache.py#L18-L19)
 
 **Type System:**

 
 - `tensor`: Block of values, shape known at compile time [python/triton/language/core.py50-91](https://github.com/triton-lang/triton/blob/f893845b/python/triton/language/core.py#L50-L91)
 - `tl.constexpr`: Compile-time constant values used for shapes or specialized logic [python/triton/language/core.py192-208](https://github.com/triton-lang/triton/blob/f893845b/python/triton/language/core.py#L192-L208)
 - `dtype`: Scalar types (int32, float16, etc.) [python/triton/language/semantic.py124-153](https://github.com/triton-lang/triton/blob/f893845b/python/triton/language/semantic.py#L124-L153)
 
 **Sources:** [python/triton/runtime/jit.py108-113](https://github.com/triton-lang/triton/blob/f893845b/python/triton/runtime/jit.py#L108-L113) [python/triton/language/semantic.py39-42](https://github.com/triton-lang/triton/blob/f893845b/python/triton/language/semantic.py#L39-L42) [python/test/unit/runtime/test_cache.py18-19](https://github.com/triton-lang/triton/blob/f893845b/python/test/unit/runtime/test_cache.py#L18-L19)

 
---

 
## Build System Integration

 
### Dependencies and Configuration

 **Core Dependencies:**

 
 - **LLVM/MLIR**: Specific version tracked in `cmake/llvm-build-info.json` [.github/workflows/llvm-build.yml62-65](https://github.com/triton-lang/triton/blob/f893845b/.github/workflows/llvm-build.yml#L62-L65)
 - **Python**: 3.10-3.14 [README.md39](https://github.com/triton-lang/triton/blob/f893845b/README.md?plain=1#L39-L39)
 - **CMake**: Build system orchestration [README.md99-100](https://github.com/triton-lang/triton/blob/f893845b/README.md?plain=1#L99-L100)
 
 **Build Process:**

 
 - Clone LLVM at pinned commit [.github/workflows/llvm-build.yml91-96](https://github.com/triton-lang/triton/blob/f893845b/.github/workflows/llvm-build.yml#L91-L96)
 - Build LLVM with required projects (MLIR, lld, clang) [.github/workflows/llvm-build.yml148](https://github.com/triton-lang/triton/blob/f893845b/.github/workflows/llvm-build.yml#L148-L148)
 - Build Triton C++ libraries against LLVM [README.md110-113](https://github.com/triton-lang/triton/blob/f893845b/README.md?plain=1#L110-L113)
 
 **Key Configuration Knobs:**

 
 - `TRITON_BUILD_WITH_CLANG_LLD`: Use clang and lld for faster builds [README.md119-121](https://github.com/triton-lang/triton/blob/f893845b/README.md?plain=1#L119-L121)
 - `TRITON_HOME`: Location for cache and downloads [README.md124-127](https://github.com/triton-lang/triton/blob/f893845b/README.md?plain=1#L124-L127)
 - `MAX_JOBS`: Limit build concurrency to manage memory [README.md129-132](https://github.com/triton-lang/triton/blob/f893845b/README.md?plain=1#L129-L132)
 
 **Sources:** [README.md64-114](https://github.com/triton-lang/triton/blob/f893845b/README.md?plain=1#L64-L114) [.github/workflows/llvm-build.yml137-155](https://github.com/triton-lang/triton/blob/f893845b/.github/workflows/llvm-build.yml#L137-L155)
