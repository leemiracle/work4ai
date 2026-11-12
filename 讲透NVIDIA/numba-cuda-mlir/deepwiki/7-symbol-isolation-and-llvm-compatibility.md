<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/numba-cuda-mlir · page 7 Symbol Isolation and LLVM Compatibility · fetched 2026-10-26 -->

# Symbol Isolation and LLVM Compatibility

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cext/launcher/llvm_downgrade.cpp](cext/launcher/llvm_downgrade.cpp)
- [cext/mlir-llvm70/include/llvm70/LLVM70Target.h](cext/mlir-llvm70/include/llvm70/LLVM70Target.h)
- [cext/mlir-llvm70/lib/LLVM70Target.cpp](cext/mlir-llvm70/lib/LLVM70Target.cpp)
- [ci/tools/run-expensive-tests](ci/tools/run-expensive-tests)
- [ci/tools/run-tests](ci/tools/run-tests)
- [src/numba_cuda_mlir/__init__.py](src/numba_cuda_mlir/__init__.py)
- [tests/data/Makefile](tests/data/Makefile)
- [tests/data/fake_mlir_shim.c](tests/data/fake_mlir_shim.c)
- [tests/test_dynamic_shared_memory.py](tests/test_dynamic_shared_memory.py)
- [tests/test_jit_compat.py](tests/test_jit_compat.py)
- [tests/test_symbol_isolation.py](tests/test_symbol_isolation.py)

</details>



The `numba-cuda-mlir` project operates in a complex environment where multiple versions of LLVM and MLIR may coexist within the same process (e.g., when used alongside other MLIR-based libraries or different versions of Numba). To ensure stability and compatibility with legacy NVIDIA toolchains, the project implements two primary C++ subsystems: one for symbol isolation and another for LLVM IR version bridging.

### System Interaction Overview

The following diagram illustrates how the C++ extensions bridge the gap between the modern MLIR-based frontend and the target-specific backends.

**C++ Extension Bridging Logic**
```mermaid
graph TD
    subgraph "Python Space"
        [numba_cuda_mlir/__init__.py] --> |"RTLD_DEEPBIND"| [CDLL_Handles]
        [MLIRDispatcher] --> |"Target Options"| [LLVM70Options]
    end

    subgraph "Symbol Isolation (C++ Layer)"
        [CDLL_Handles] --> |"Isolate"| [libMLIRPythonCAPI.so]
        [CDLL_Handles] --> |"Isolate"| [libMLIRToLLVM70.so]
    end

    subgraph "LLVM Compatibility (C++ Layer)"
        [MLIRToLLVM70] --> |"Translate"| [LLVM70IRBuilder]
        [LLVM70IRBuilder] --> |"C-API"| [libLLVM-7.so]
        [LLVM70IRBuilder] --> |"Bitcode"| [LibNVVMCompiler]
        [LibNVVMCompiler] --> |"Compile"| [libnvvm.so]
    end

    [libnvvm.so] --> |"Output"| [PTX_LTOIR]
```
Sources: [src/numba_cuda_mlir/__init__.py:7-35](), [cext/mlir-llvm70/include/llvm70/LLVM70Target.h:37-53](), [cext/mlir-llvm70/lib/LLVM70Target.cpp:30-46]()

---

## Symbol Isolation (RTLD_DEEPBIND)

To prevent symbol preemption—where symbols from one version of LLVM/MLIR are mistakenly used by another—`numba-cuda-mlir` uses `RTLD_DEEPBIND` when loading its bundled libraries on Linux. This ensures that the libraries look within their own dependencies first before searching the global scope.

### Key Mechanisms
*   **Preloading**: The `_preload_mlir_libs_with_deepbind` function in `__init__.py` explicitly loads `libMLIRPythonCAPI.so` and related modules using `os.RTLD_DEEPBIND` [src/numba_cuda_mlir/__init__.py:10-35]().
*   **Verification**: The system includes a "poisoning" test using `fake_mlir_shim.c`. This shim defines symbols that would cause an abort if the isolation failed and the global scope was searched instead of the local library scope [tests/data/fake_mlir_shim.c:16-21]().
*   **Leak Prevention**: Tests verify that internal LLVM symbols do not leak into the `RTLD_DEFAULT` scope, ensuring they remain invisible to other parts of the Python process [tests/test_symbol_isolation.py:35-66]().

For details, see [Symbol Isolation (RTLD_DEEPBIND)](#7.1).

---

## LLVM IR Downgrade for libnvvm

NVIDIA's `libnvvm` (the compiler component of the CUDA Toolkit) often requires older LLVM IR versions (specifically LLVM 7.0 compatible IR for many versions). Since the project uses a modern MLIR/LLVM stack, it must "downgrade" the IR to a format `libnvvm` can ingest.

### Compatibility Pipeline

The `MLIRToLLVM70` translator and `LLVM70IRBuilder` handle the conversion of modern MLIR LLVM Dialect operations into legacy LLVM 7.0 C-API calls.

**Entity Mapping for IR Downgrade**
```mermaid
graph LR
    subgraph "MLIR Entities"
        [gpu.GPUModuleOp]
        [LLVM::LLVMFuncOp]
        [LLVM::AtomicRMWOp]
    end

    subgraph "Downgrade Logic (llvm_downgrade.cpp / LLVM70Target.cpp)"
        [MLIRToLLVM70::translate]
        [MLIRToLLVM70::convertType]
        [adapt_for_libnvvm]
    end

    subgraph "Legacy LLVM 7.0 C-API"
        [LLVMAddFunction]
        [LLVMBuildCall2]
        [LLVMSetAtomicRMWBinOp]
    end

    [gpu.GPUModuleOp] --> [MLIRToLLVM70::translate]
    [LLVM::LLVMFuncOp] --> [LLVMAddFunction]
    [LLVM::AtomicRMWOp] --> [LLVMSetAtomicRMWBinOp]
    [adapt_for_libnvvm] --> |"Semantic Patch"| [LLVMBuildCall2]
```
Sources: [cext/mlir-llvm70/lib/LLVM70Target.cpp:157-185](), [cext/launcher/llvm_downgrade.cpp:73-162](), [cext/mlir-llvm70/include/llvm70/LLVM70Target.h:66-74]()

### Core Components
*   **Semantic Patching**: The `adapt_for_libnvvm` logic applies patches for features not directly supported in legacy IR, such as modern barrier synchronizations or specific atomic floating-point additions [cext/launcher/llvm_downgrade.cpp:122-124]().
*   **Type Conversion**: The `convertType` method maps modern MLIR types (including `BFloat16Type`) to their legacy LLVM equivalents, often using `i16` bitcasting for newer types like `bf16` [cext/mlir-llvm70/lib/LLVM70Target.cpp:121-151]().
*   **Target Translation**: The `translateToPTX` entry point orchestrates the full flow: building the legacy IR, linking with `libdevice` bitcode, and finally invoking `libnvvm` to produce PTX or LTOIR [cext/mlir-llvm70/lib/LLVM70Target.cpp:48-108]().

For details, see [LLVM IR Downgrade for libnvvm](#7.2).

---

