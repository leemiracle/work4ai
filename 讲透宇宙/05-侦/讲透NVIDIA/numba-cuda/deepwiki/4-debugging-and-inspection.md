<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/numba-cuda · page 4 Debugging and Inspection · fetched 2026-10-26 -->

# Debugging and Inspection

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [numba_cuda/numba/cuda/debuginfo.py](numba_cuda/numba/cuda/debuginfo.py)
- [numba_cuda/numba/cuda/lowering.py](numba_cuda/numba/cuda/lowering.py)
- [numba_cuda/numba/cuda/testing.py](numba_cuda/numba/cuda/testing.py)
- [numba_cuda/numba/cuda/tests/cudadrv/test_managed_alloc.py](numba_cuda/numba/cuda/tests/cudadrv/test_managed_alloc.py)
- [numba_cuda/numba/cuda/tests/cudapy/test_debuginfo.py](numba_cuda/numba/cuda/tests/cudapy/test_debuginfo.py)
- [numba_cuda/numba/cuda/tests/cudapy/test_debuginfo_types.py](numba_cuda/numba/cuda/tests/cudapy/test_debuginfo_types.py)
- [numba_cuda/numba/cuda/tests/cudapy/test_inspect.py](numba_cuda/numba/cuda/tests/cudapy/test_inspect.py)
- [numba_cuda/numba/cuda/tests/cudapy/test_ipc.py](numba_cuda/numba/cuda/tests/cudapy/test_ipc.py)

</details>



This document covers the debugging and inspection capabilities in numba-cuda, including debug information generation, code inspection methods, and error handling mechanisms. These features enable developers to analyze compiled CUDA kernels, debug runtime issues, and understand the generated code at various compilation stages.

For information about the core compilation pipeline, see [Core Architecture](#2). For testing infrastructure, see [Testing Framework](#6.1).

## Debug Information Generation

The debug information system in numba-cuda generates DWARF debug metadata that can be used by profiling tools and debuggers. The system is built around the `CUDADIBuilder` class and integrates with the compilation pipeline.

```mermaid
graph TD
    A["@cuda.jit(debug=True)"] --> B["CUDADispatcher"]
    B --> C["compile_cuda()"]
    C --> D["CUDACompiler"]
    D --> E["CUDALower"]
    E --> F["CUDADIBuilder"]
    F --> G["LLVM Debug Metadata"]
    G --> H["NVVM Compilation"]
    H --> I["PTX with Debug Sections"]
    
    J["kernel_fixup()"] --> K["Exception Handling"]
    K --> L["Error State Variables"]
    
    C --> J
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style I fill:#9f9,stroke:#333,stroke-width:2px
```

The `CUDADIBuilder` class extends the core Numba debug info builder to handle CUDA-specific types and metadata generation. It creates debug metadata for variables, function parameters, and supports polymorphic types through union representations.

Sources: [numba_cuda/numba/cuda/debuginfo.py:10-15](), [numba_cuda/numba/cuda/compiler.py:271-282](), [numba_cuda/numba/cuda/lowering.py:49-83]()

## Code Inspection System

The inspection system provides methods to examine compiled kernels at different stages of the compilation pipeline. These methods are available on both `_Kernel` and `CUDADispatcher` objects.

```mermaid
graph LR
    A["Compiled Kernel"] --> B["inspect_llvm()"]
    A --> C["inspect_asm()"]
    A --> D["inspect_sass()"]
    A --> E["inspect_sass_cfg()"]
    A --> F["inspect_types()"]
    
    B --> G["LLVM IR Output"]
    C --> H["PTX Assembly"]
    D --> I["SASS Assembly"]
    E --> J["Control Flow Graph"]
    F --> K["Type Annotations"]
    
    L["CUDACodeLibrary"] --> M["get_llvm_str()"]
    L --> N["get_asm_str()"]
    L --> O["get_sass()"]
    L --> P["get_sass_cfg()"]
    
    M --> G
    N --> H
    O --> I
    P --> J
```

The inspection methods delegate to the underlying `CUDACodeLibrary` to retrieve the requested representation:

| Method | Returns | Purpose |
|--------|---------|---------|
| `inspect_llvm()` | LLVM IR string | View intermediate representation |
| `inspect_asm(cc)` | PTX assembly string | View generated PTX code |
| `inspect_sass()` | SASS assembly string | View native GPU assembly |
| `inspect_sass_cfg()` | Control flow graph | Analyze execution flow |
| `inspect_types()` | Type annotations | Debug type inference |

Sources: [numba_cuda/numba/cuda/dispatcher.py:375-418](), [numba_cuda/numba/cuda/dispatcher.py:890-996]()

## Debug Flag Configuration

The debug system is controlled through several compilation flags that affect code generation and runtime behavior.

```mermaid
graph TD
    A["Debug Flags"] --> B["debug=True"]
    A --> C["lineinfo=True"]
    A --> D["opt=False"]
    
    B --> E["Full Debug Info"]
    B --> F["Exception Handling"]
    B --> G["Error Model: Python"]
    
    C --> H["Line Mapping Only"]
    C --> I["Profiling Support"]
    
    D --> J["Disable Optimizations"]
    D --> K["Preserve Variable Names"]
    
    E --> L["DWARF Metadata"]
    F --> M["Exception State Tracking"]
    G --> N["Python-style Errors"]
    
    H --> O["Source Correlation"]
    I --> P["Profiler Integration"]
    
    style B fill:#f99,stroke:#333,stroke-width:2px
    style C fill:#99f,stroke:#333,stroke-width:2px
```

The debug flags have specific interactions:
- `debug=True` enables full debug information but requires `opt=False`
- `lineinfo=True` provides line mapping without affecting optimization
- `debug=True` and `lineinfo=True` are mutually exclusive

Sources: [numba_cuda/numba/cuda/compiler.py:271-282](), [numba_cuda/numba/cuda/decorators.py:126-140]()

## Exception Handling in Debug Mode

When `debug=True`, the compilation system adds comprehensive exception handling to CUDA kernels through the `kernel_fixup()` function and exception helper infrastructure.

```mermaid
graph TD
    A["kernel_fixup()"] --> B["add_exception_store_helper()"]
    B --> C["Global Error Variables"]
    C --> D["gv_exc: Error Code"]
    C --> E["gv_tid: Thread ID"]
    C --> F["gv_ctaid: Block ID"]
    
    G["Kernel Launch"] --> H["Exception Check"]
    H --> I["Status Code != 0?"]
    I -->|Yes| J["Load Error State"]
    I -->|No| K["Normal Execution"]
    
    J --> L["Extract Thread Position"]
    J --> M["Get Exception Details"]
    L --> N["Format Error Message"]
    M --> N
    N --> O["Raise Python Exception"]
    
    P["Exception Helper"] --> Q["Atomic Compare-Exchange"]
    Q --> R["First Error Only"]
    R --> S["Store Thread Context"]
    
    style A fill:#f99,stroke:#333,stroke-width:2px
    style O fill:#f99,stroke:#333,stroke-width:2px
```

The exception handling system creates global variables in the kernel module to track error state and thread context. When an exception occurs, it atomically stores the error code and thread position to provide detailed error information.

Sources: [numba_cuda/numba/cuda/compiler.py:365-457](), [numba_cuda/numba/cuda/compiler.py:459-525](), [numba_cuda/numba/cuda/dispatcher.py:446-512]()

## Debug Metadata Generation

The `CUDADIBuilder` generates LLVM debug metadata that describes variables, types, and execution context for debugging and profiling tools.

```mermaid
graph LR
    A["CUDADIBuilder"] --> B["_var_type()"]
    A --> C["mark_variable()"]
    A --> D["update_variable()"]
    
    B --> E["Boolean Types"]
    B --> F["Integer Types"]
    B --> G["Union Types"]
    B --> H["GridGroup Types"]
    
    C --> I["llvm.dbg.declare"]
    D --> J["llvm.dbg.value"]
    
    E --> K["DW_ATE_boolean"]
    F --> L["DW_ATE_signed"]
    G --> M["DW_TAG_union_type"]
    H --> N["DW_ATE_unsigned"]
    
    O["Polymorphic Variables"] --> P["UnionModel"]
    P --> Q["Member Types"]
    Q --> R["DIDerivedType"]
    R --> S["DICompositeType"]
    
    style A fill:#9f9,stroke:#333,stroke-width:2px
    style M fill:#99f,stroke:#333,stroke-width:2px
```

The debug metadata system handles several CUDA-specific requirements:
- Special encoding for boolean and GridGroup types
- Union types for polymorphic variables
- Scalar variable tracking with `llvm.dbg.value`
- Type deduplication for variables with same name and type

Sources: [numba_cuda/numba/cuda/debuginfo.py:16-111](), [numba_cuda/numba/cuda/debuginfo.py:140-214](), [numba_cuda/numba/cuda/lowering.py:8-47]()

## Testing and Validation

The debug system is thoroughly tested through the `TestCudaDebugInfo` class, which validates debug metadata generation, exception handling, and inspection capabilities.

```mermaid
graph TD
    A["TestCudaDebugInfo"] --> B["Debug Metadata Tests"]
    A --> C["Inspection Tests"]
    A --> D["Exception Tests"]
    
    B --> E["test_debuginfo_in_asm()"]
    B --> F["test_bool_type()"]
    B --> G["test_union_poly_types()"]
    
    C --> H["test_llvm_dbg_value()"]
    C --> I["test_kernel_args_types()"]
    
    D --> J["test_chained_device_function()"]
    D --> K["test_debug_function_calls()"]
    
    E --> L["PTX Debug Sections"]
    F --> M["DW_ATE_boolean"]
    G --> N["DW_TAG_union_type"]
    
    H --> O["llvm.dbg.value calls"]
    I --> P["DISubroutineType"]
    
    style A fill:#9f9,stroke:#333,stroke-width:2px
    style L fill:#99f,stroke:#333,stroke-width:2px
```

The test suite covers:
- Debug section presence in PTX output
- Correct DWARF encoding for different types
- Variable tracking and metadata generation
- Multi-module debug compilation
- Exception handling integration

Sources: [numba_cuda/numba/cuda/tests/cudapy/test_debuginfo.py:12-408]()

---

