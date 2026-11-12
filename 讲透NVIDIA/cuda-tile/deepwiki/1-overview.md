<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cuda-tile · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



This document provides a high-level introduction to the CUDA Tile IR project, explaining its purpose as an MLIR-based intermediate representation for CUDA kernel optimization, its relationship to LLVM/MLIR and the CUDA Toolkit, and its major architectural components.

For detailed build instructions, see [Building from Source](#2.1). For dialect-specific information, see [Core Dialect](#3). For execution details, see [Execution Pipeline](#9).

## Purpose

CUDA Tile IR is an MLIR-based intermediate representation and compiler infrastructure for expressing and optimizing tile-based computations on NVIDIA GPUs. The project provides a domain-specific dialect within the MLIR framework that simplifies the development of high-performance CUDA kernels through first-class abstractions for tiling patterns, memory hierarchy management, and GPU-specific optimizations targeting tensor core units.

This implementation is aligned with CUDA Toolkit version 13.1 and provides a complete ecosystem including a dialect definition, bytecode serialization format, optimization passes, and language bindings (C++, C, Python).

**Sources:** [README.md:1-12]()

## System Context

CUDA Tile IR occupies a specific position in the compilation pipeline between high-level compiler infrastructure (LLVM/MLIR) and low-level GPU execution (CUDA Toolkit):

**System Context Diagram**

```mermaid
graph LR
    subgraph "Compiler Infrastructure"
        LLVM["LLVM/MLIR Framework<br/>mlir::MLIRContext<br/>mlir::OpBuilder"]
    end
    
    subgraph "CUDA Tile IR Project"
        Dialect["mlir::cuda_tile::CudaTileDialect<br/>lib/Dialect/CudaTile/IR/<br/>ModuleOp, EntryOp"]
        Bytecode["BytecodeWriter/BytecodeReader<br/>lib/Bytecode/<br/>.tilebc files"]
        API["mlirCudaTileRegisterAllDialects()<br/>cuda_tile Python module<br/>C++ mlir::cuda_tile namespace"]
    end
    
    subgraph "NVIDIA Execution"
        Toolkit["tileiras compiler<br/>CUDA Toolkit 13.1+<br/>bytecode to cubin"]
        Driver["cuModuleLoad()<br/>cuLaunchKernel()<br/>CUDA Driver API"]
    end
    
    subgraph "User Code"
        Source["MLIR Text .mlir<br/>cuda_tile.module {...}<br/>Python IR Builder"]
        App["Host Application<br/>cuModuleGetFunction()"]
    end
    
    LLVM -->|"provides MLIR<br/>infrastructure"| Dialect
    Source -->|"constructs"| Dialect
    Dialect -->|"serializes to"| Bytecode
    API -->|"manipulates"| Dialect
    Bytecode -->|"JIT compile"| Driver
    Bytecode -->|"AOT compile"| Toolkit
    Toolkit -->|"produces .cubin"| Driver
    App -->|"launches via<br/>cuLaunchKernel"| Driver
```

**Sources:** [README.md:1-12](), [lib/Dialect/CudaTile/IR/CudaTile.cpp](), [lib/Bytecode/Writer/Writer.cpp](), [lib/Bytecode/Reader/Reader.cpp]()

The project sits at the intersection of three domains:
- **LLVM/MLIR ecosystem**: Provides compiler infrastructure (`mlir::MLIRContext`, `mlir::OpBuilder`) and dialect framework
- **CUDA Toolkit**: Provides GPU compilation (`tileiras` tool) and runtime execution
- **User applications**: Consume the IR through C++ (`mlir::cuda_tile` namespace), C API (`mlirCudaTile*` functions), or Python (`cuda_tile` module)

## Major Components

CUDA Tile IR consists of five major subsystems:

**Component Architecture Diagram**

```mermaid
graph TB
    subgraph "1. Core Dialect Definition"
        DialectDef["mlir::cuda_tile::CudaTileDialect<br/>include/Dialect/CudaTile/IR/Dialect.h<br/>lib/Dialect/CudaTile/IR/CudaTile.cpp"]
        Types["mlir::cuda_tile::TileType<br/>mlir::cuda_tile::PointerType<br/>include/Dialect/CudaTile/IR/Types.td<br/>TokenType, TensorViewType, PartitionViewType"]
        Attrs["mlir::cuda_tile::RoundingModeAttr<br/>mlir::cuda_tile::MemoryScopeAttr<br/>OptimizationHintsAttr<br/>DILocAttr, DISubprogramAttr"]
        Ops["mlir::cuda_tile::AddFOp<br/>mlir::cuda_tile::LoadPtrTkoOp<br/>mlir::cuda_tile::IfOp<br/>include/Dialect/CudaTile/IR/Ops.td"]
    end
    
    subgraph "2. Bytecode Serialization"
        Writer["BytecodeWriter class<br/>lib/Bytecode/Writer/Writer.cpp<br/>StringManager, TypeManager"]
        Reader["BytecodeReader class<br/>lib/Bytecode/Reader/Reader.cpp<br/>parseSections()"]
        Version["bytecode::kCurrentVersion<br/>13.1"]
    end
    
    subgraph "3. API Layers"
        CppAPI["mlir::cuda_tile namespace<br/>include/Dialect/CudaTile/IR/<br/>OpBuilder interface"]
        CAPI["mlirCudaTileRegisterAllDialects()<br/>mlirCudaTileTileTypeGet()<br/>include/Dialect/CudaTile-c/"]
        PyAPI["cuda_tile module<br/>python/Dialect/CudaTile/<br/>_cuda_tile.pyi"]
    end
    
    subgraph "4. Build System"
        CMake["CMakeLists.txt<br/>cmake/IncludeLLVM.cmake<br/>CUDA_TILE_USE_LLVM_SOURCE_DIR"]
        TableGen["cuda-tile-tblgen executable<br/>tools/cuda-tile-tblgen/<br/>MLIR TableGen backend"]
        TDFiles["Ops.td, Types.td, Attrs.td<br/>include/Dialect/CudaTile/IR/"]
    end
    
    subgraph "5. Tools"
        TileOpt["cuda-tile-opt executable<br/>tools/cuda-tile-opt/<br/>applyPasses()"]
        TileTblgen["cuda-tile-tblgen executable<br/>generates .h.inc files"]
        Translate["cuda-tile-translate executable<br/>tools/cuda-tile-translate/<br/>mlir-to-cudatilebc"]
    end
    
    TDFiles -->|"processed by"| TableGen
    TableGen -->|"generates"| DialectDef
    TableGen -->|"generates"| Types
    TableGen -->|"generates"| Attrs
    TableGen -->|"generates"| Ops
    
    DialectDef --> Writer
    DialectDef --> Reader
    DialectDef --> CppAPI
    CppAPI --> CAPI
    CAPI --> PyAPI
    
    CMake -->|"orchestrates"| TableGen
    CMake -->|"builds"| TileOpt
    CMake -->|"builds"| Translate
```

**Sources:** [README.md:14-25](), [lib/Dialect/CudaTile/IR/CudaTile.cpp](), [include/Dialect/CudaTile/IR/Types.td](), [include/Dialect/CudaTile/IR/Ops.td](), [lib/Bytecode/Writer/Writer.cpp](), [lib/Bytecode/Reader/Reader.cpp]()

### Component Descriptions

| Component | Location | Key Classes/Functions | Purpose |
|-----------|----------|----------------------|---------|
| **Core Dialect** | `include/Dialect/CudaTile/IR/`, `lib/Dialect/CudaTile/IR/` | `mlir::cuda_tile::CudaTileDialect`, `TileType`, `PointerType`, `AddFOp`, `LoadPtrTkoOp` | Defines the MLIR dialect with types, attributes, and operations for tile-based computations |
| **Bytecode System** | `lib/Bytecode/` | `BytecodeWriter`, `BytecodeReader`, `StringManager`, `TypeManager`, `bytecode::kCurrentVersion` | Provides binary serialization/deserialization with version 13.1 format and compatibility guarantees |
| **C++ API** | `include/Dialect/CudaTile/IR/` | `mlir::cuda_tile` namespace, `mlir::OpBuilder` interface | Internal implementation API using `mlir::cuda_tile` namespace |
| **C API** | `include/Dialect/CudaTile-c/` | `mlirCudaTileRegisterAllDialects()`, `mlirCudaTileTileTypeGet()`, `mlirCudaTileWriteBytecode()` | Language-agnostic API with `MLIR_CAPI_EXPORTED` functions prefixed with `mlirCudaTile*` |
| **Python Bindings** | `python/` | `cuda_tile` module, `_cuda_tile` extension module | Python wrappers for IR construction and manipulation (optional component) |
| **Build System** | `cmake/`, `CMakeLists.txt` | `CUDA_TILE_USE_LLVM_SOURCE_DIR`, `CUDA_TILE_ENABLE_BINDINGS_PYTHON` | CMake-based configuration supporting three LLVM integration modes |
| **Tools** | `tools/` | `cuda-tile-opt`, `cuda-tile-translate`, `cuda-tile-tblgen` executables | Command-line utilities: `cuda-tile-opt` (optimization), `cuda-tile-translate` (bytecode conversion), `cuda-tile-tblgen` (code generation) |

**Sources:** [README.md:14-25](), [README.md:144-210](), [include/Dialect/CudaTile/IR/Dialect.h](), [lib/Bytecode/Writer/Writer.cpp](), [include/Dialect/CudaTile-c/Dialect.h]()

## Compilation and Execution Flow

The typical workflow from source IR to GPU execution follows this pipeline:

**Compilation and Execution Pipeline Diagram**

```mermaid
graph LR
    subgraph "Source Representation"
        MLIR["MLIR Textual Format<br/>cuda_tile.module @name {...}<br/>entry @kernel(...) {...}"]
        CppCode["C++ Programmatic<br/>mlir::OpBuilder::create()<br/>ModuleOp construction"]
        PyCode["Python IR Builder<br/>cuda_tile module<br/>TileIrGenerator"]
    end
    
    subgraph "In-Memory IR"
        IR["mlir::cuda_tile::ModuleOp<br/>mlir::cuda_tile::EntryOp<br/>Operation tree in memory"]
    end
    
    subgraph "Optimization Optional"
        Opt["mlirCudaTileApplyOptimizations()<br/>or applyTileIROptimizations()<br/>LoopSplitPass, CSE"]
    end
    
    subgraph "Serialization"
        BCWrite["BytecodeWriter::write()<br/>or mlirCudaTileWriteBytecode()<br/>lib/Bytecode/Writer/"]
        TileBC[".tilebc file<br/>bytecode::kCurrentVersion 13.1<br/>Binary bytecode format"]
    end
    
    subgraph "Compilation Options"
        JIT["JIT Path<br/>cuModuleLoad(*.tilebc)<br/>CUDA Driver compiles"]
        AOT["AOT Path<br/>tileiras --gpu-name sm_100<br/>CUDA Toolkit compiler"]
    end
    
    subgraph "Execution"
        Cubin[".cubin file<br/>SM-specific binary<br/>PTX assembled"]
        Launch["cuModuleGetFunction()<br/>cuLaunchKernel()<br/>Grid: 1x1x1, Shared: 0"]
    end
    
    MLIR --> IR
    CppCode --> IR
    PyCode --> IR
    IR --> Opt
    Opt --> BCWrite
    BCWrite --> TileBC
    TileBC --> JIT
    TileBC --> AOT
    AOT --> Cubin
    JIT --> Launch
    Cubin --> Launch
```

**Sources:** [README.md:212-339](), [lib/Bytecode/Writer/Writer.cpp](), [include/Dialect/CudaTile-c/Bytecode.h]()

### Pipeline Stages

1. **Source Construction**: IR can be created from:
   - MLIR textual syntax using `cuda_tile.module` and `entry` operations
   - C++ programmatically via `mlir::OpBuilder::create<mlir::cuda_tile::ModuleOp>()` and related builder methods
   - Python via the `cuda_tile` module using `TileIrGenerator` class

2. **Optimization** (Optional): The `mlirCudaTileApplyOptimizations()` C API function or `applyTileIROptimizations()` Python function applies transformation passes including:
   - `LoopSplitPass` at [lib/Dialect/CudaTile/Transforms/LoopSplit.cpp]()
   - Common subexpression elimination (CSE)
   - Canonicalization patterns

3. **Bytecode Serialization**: 
   - C++ API: `BytecodeWriter::write()` method at [lib/Bytecode/Writer/Writer.cpp]()
   - C API: `mlirCudaTileWriteBytecode()` function at [include/Dialect/CudaTile-c/Bytecode.h]()
   - Both serialize IR to `.tilebc` binary format at version `bytecode::kCurrentVersion` (13.1)

4. **Compilation Paths**:
   - **JIT**: Bytecode is loaded directly via CUDA Driver API `cuModuleLoad("example.tilebc")` for just-in-time compilation
   - **AOT**: The `tileiras` tool (CUDA Toolkit) compiles bytecode to architecture-specific `.cubin` files using `tileiras --gpu-name sm_100 example.tilebc -o example.cubin`

5. **Execution**: Both paths converge at `cuModuleGetFunction()` followed by `cuLaunchKernel()` with specific constraints:
   - Grid dimensions: 1×1×1 (sets Tile Grid dimensions)
   - Block dimensions: 1×1×1 (unused, must be 1×1×1)
   - Shared memory: 0 bytes (unused, must be 0)

**Sources:** [README.md:212-339](), [README.md:296-314](), [lib/Bytecode/Writer/Writer.cpp](), [include/Dialect/CudaTile-c/Bytecode.h](), [lib/Dialect/CudaTile/Transforms/LoopSplit.cpp]()

## LLVM/MLIR Integration

CUDA Tile IR is built on top of the MLIR framework and requires a compatible LLVM/MLIR installation. The project supports three integration modes:

| Mode | CMake Variable | Description |
|------|----------------|-------------|
| **Auto-download** | (default) | CMake downloads LLVM sources from GitHub at the commit specified in `cmake/IncludeLLVM.cmake:29` |
| **Source directory** | `CUDA_TILE_USE_LLVM_SOURCE_DIR` | Links against locally built LLVM at a compatible commit |
| **Install directory** | `CUDA_TILE_USE_LLVM_INSTALL_DIR` | Uses pre-built LLVM libraries from an installation directory |

The exact required LLVM commit is defined at [cmake/IncludeLLVM.cmake:29]() and must match for source/install directory modes.

**Sources:** [README.md:69-102](), Diagram 2

## CUDA Toolkit Integration

CUDA Tile IR requires CUDA Toolkit 13.1 or higher for execution. The integration occurs through:

- **tileiras compiler**: Compiles `.tilebc` bytecode files to SM-specific `.cubin` binaries
- **CUDA Driver API**: Loads bytecode (JIT) or cubin (AOT) and executes kernels via `cuModuleLoad()` and `cuLaunchKernel()`
- **Execution constraints**: CUDA Tile IR kernels must be launched with grid dimensions of 1x1x1 and 0 bytes of shared memory

**Sources:** [README.md:11-12](), [README.md:226-227](), [README.md:296-314]()

## API Architecture

CUDA Tile IR provides a three-layer API architecture for different integration scenarios:

**API Layer Architecture Diagram**

```mermaid
graph TB
    subgraph "Internal Implementation"
        DialectImpl["mlir::cuda_tile::CudaTileDialect<br/>include/Dialect/CudaTile/IR/Dialect.h<br/>lib/Dialect/CudaTile/IR/CudaTile.cpp"]
        OpImpl["Operation implementations<br/>lib/Dialect/CudaTile/IR/Ops.cpp<br/>AddFOp::verify(), IfOp::build()"]
        TypeImpl["Type implementations<br/>lib/Dialect/CudaTile/IR/Types.cpp<br/>TileType::get(), PointerType::get()"]
        BytecodeImpl["BytecodeWriter/BytecodeReader<br/>lib/Bytecode/Writer/Writer.cpp<br/>lib/Bytecode/Reader/Reader.cpp"]
    end
    
    subgraph "C API Layer"
        RegDialect["mlirCudaTileRegisterAllDialects()<br/>include/Dialect/CudaTile-c/Dialect.h<br/>MLIR_CAPI_EXPORTED"]
        TypeAPI["mlirCudaTileTileTypeGet()<br/>mlirCudaTilePointerTypeGet()<br/>include/Dialect/CudaTile-c/Types.h"]
        AttrAPI["mlirCudaTileRoundingModeAttrGet()<br/>mlirCudaTileMemoryScopeAttrGet()<br/>include/Dialect/CudaTile-c/Attributes.h"]
        BCAPI["mlirCudaTileWriteBytecode()<br/>include/Dialect/CudaTile-c/Bytecode.h<br/>MlirBytecodeWriterConfig"]
    end
    
    subgraph "Python Layer"
        PyModule["cuda_tile Python module<br/>python/Dialect/CudaTile/<br/>_cuda_tile extension"]
        PyIR["TileIrGenerator<br/>cuda_tile_ops.py<br/>@cuda_tile_op decorators"]
    end
    
    subgraph "External Integration"
        CppCompiler["C++ projects<br/>mlir::OpBuilder::create<>()<br/>link CudaTileDialect"]
        FFI["Other languages<br/>via C ABI<br/>MLIR_CAPI_EXPORTED"]
        PyTools["Python-based tools<br/>import cuda_tile<br/>TileIrGenerator"]
    end
    
    DialectImpl --> RegDialect
    OpImpl --> TypeAPI
    TypeImpl --> TypeAPI
    BytecodeImpl --> BCAPI
    
    RegDialect --> PyModule
    TypeAPI --> PyModule
    AttrAPI --> PyModule
    BCAPI --> PyModule
    
    PyModule --> PyIR
    
    RegDialect --> CppCompiler
    TypeAPI --> CppCompiler
    BCAPI --> CppCompiler
    
    RegDialect -.->|"extern C"| FFI
    TypeAPI -.->|"extern C"| FFI
    
    PyIR --> PyTools
```

**Sources:** [README.md:144-210](), [include/Dialect/CudaTile/IR/Dialect.h](), [include/Dialect/CudaTile-c/Dialect.h](), [include/Dialect/CudaTile-c/Types.h](), [include/Dialect/CudaTile-c/Bytecode.h](), [python/Dialect/CudaTile/]()

### API Layer Purposes

- **C++ Internal API** (`mlir::cuda_tile` namespace): Used for direct integration in C++ projects, provides full access to dialect implementation including:
  - Type creation: `mlir::cuda_tile::TileType::get()`, `mlir::cuda_tile::PointerType::get()`
  - Operation builders: `mlir::OpBuilder::create<mlir::cuda_tile::AddFOp>()`
  - Bytecode I/O: `BytecodeWriter::write()`, `BytecodeReader::read()`
  
- **C API** (`mlirCudaTile*` functions): Language-agnostic interface with `MLIR_CAPI_EXPORTED` linkage defined at [include/Dialect/CudaTile-c/](), enables FFI from other languages with functions like:
  - `mlirCudaTileRegisterAllDialects(MlirContext)`
  - `mlirCudaTileTileTypeGet(MlirContext, intptr_t numElements, MlirType* elementTypes)`
  - `mlirCudaTileWriteBytecode(MlirModule, MlirStringCallback, void*)`

- **Python Bindings**: High-level interface for programmatic IR construction, manipulation, and testing (optional, controlled by `CUDA_TILE_ENABLE_BINDINGS_PYTHON` CMake variable) including:
  - `cuda_tile` module with `TileIrGenerator` class
  - `@cuda_tile_op` decorators for operation wrappers
  - High-level `Tile` class with operator overloading

**Sources:** [README.md:104-118](), [include/Dialect/CudaTile-c/Dialect.h](), [include/Dialect/CudaTile-c/Types.h](), [include/Dialect/CudaTile-c/Bytecode.h](), [python/Dialect/CudaTile/]()

## Build System Overview

The CMake build system handles complex dependencies and code generation:

**Build System Architecture Diagram**

```mermaid
graph TB
    RootCMake["Root CMakeLists.txt<br/>project(cuda-tile)<br/>CMAKE_BUILD_TYPE"]
    
    subgraph "LLVM Integration"
        IncludeLLVM["cmake/IncludeLLVM.cmake<br/>LLVM_COMMIT_HASH<br/>FetchContent"]
        LLVMMode{{"LLVM Integration Mode"}}
        AutoDL["Auto-download from GitHub<br/>FetchContent_Declare<br/>llvm-project"]
        SourceDir["CUDA_TILE_USE_LLVM_SOURCE_DIR<br/>Local build from source"]
        InstallDir["CUDA_TILE_USE_LLVM_INSTALL_DIR<br/>Pre-built libraries"]
    end
    
    subgraph "Utilities"
        CompCheck["cmake/IncludeCompilerChecks.cmake<br/>CMAKE_CXX_COMPILER_ID<br/>GCC 7.4+, Clang 5.0+, MSVC 19.29+"]
        Utils["cmake/IncludeCudaTileUtils.cmake<br/>set(CMAKE_BUILD_TYPE)<br/>Release/Debug/RelWithDebInfo"]
    end
    
    subgraph "Code Generation"
        TblgenTool["cuda-tile-tblgen executable<br/>tools/cuda-tile-tblgen/<br/>mlir-tblgen backend"]
        TDDefs["Ops.td, Types.td, Attrs.td<br/>include/Dialect/CudaTile/IR/"]
        GenCode["Generated files<br/>Ops.h.inc, Ops.cpp.inc<br/>build/include/Dialect/CudaTile/IR/"]
    end
    
    subgraph "Build Products"
        Libraries["Static libraries<br/>libCudaTileDialect.a<br/>libCudaTileBytecodeReader.a<br/>libCudaTileBytecodeWriter.a"]
        Tools["Executables<br/>cuda-tile-opt<br/>cuda-tile-translate"]
        PyBindings["Python module<br/>_cuda_tile.cpython-*.so<br/>CUDA_TILE_ENABLE_BINDINGS_PYTHON"]
        Tests["Test suite<br/>check-cuda-tile target<br/>CUDA_TILE_ENABLE_TESTING"]
    end
    
    RootCMake --> IncludeLLVM
    RootCMake --> CompCheck
    RootCMake --> Utils
    
    IncludeLLVM --> LLVMMode
    LLVMMode -->|"default"| AutoDL
    LLVMMode -->|"set variable"| SourceDir
    LLVMMode -->|"set variable"| InstallDir
    
    AutoDL --> TblgenTool
    SourceDir --> TblgenTool
    InstallDir --> TblgenTool
    
    TblgenTool --> TDDefs
    TDDefs --> GenCode
    
    GenCode --> Libraries
    GenCode --> Tools
    
    RootCMake --> PyBindings
    RootCMake --> Tests
```

**Sources:** [README.md:36-133](), [CMakeLists.txt](), [cmake/IncludeLLVM.cmake](), [cmake/IncludeCompilerChecks.cmake]()

The build system performs three critical functions:
1. **LLVM/MLIR Integration**: Downloads (via `FetchContent`) or locates LLVM at the commit specified in [cmake/IncludeLLVM.cmake:29]()
2. **Compiler Validation**: Checks `CMAKE_CXX_COMPILER_ID` to ensure GCC 7.4+, Clang 5.0+, or MSVC 19.29+ via [cmake/IncludeCompilerChecks.cmake]()
3. **Code Generation**: Runs `cuda-tile-tblgen` (MLIR TableGen backend) on `.td` definition files at [include/Dialect/CudaTile/IR/]() to generate `.h.inc` and `.cpp.inc` files

**Sources:** [README.md:36-133](), [CMakeLists.txt](), [cmake/IncludeLLVM.cmake](), [cmake/IncludeCompilerChecks.cmake]()

## Key Features

CUDA Tile IR provides several key capabilities:

- **Tile-based type system**: First-class types defined in [include/Dialect/CudaTile/IR/Types.td]():
  - `mlir::cuda_tile::TileType` for fixed-shape tensors with power-of-2 dimensions
  - `mlir::cuda_tile::PointerType` for typed memory pointers
  - `mlir::cuda_tile::TokenType` for memory operation ordering
  - `mlir::cuda_tile::TensorViewType` for dynamic-shape global memory references
  - `mlir::cuda_tile::PartitionViewType` for grid-partitioned views

- **Memory model**: Explicit memory ordering and scope semantics via attributes:
  - `MemoryOrderingSemantics`: `WEAK`, `RELAXED`, `ACQUIRE`, `RELEASE`, `ACQ_REL`
  - `MemoryScope`: `TL_BLK`, `DEVICE`, `SYS`
  - Token-ordered operations (suffix `_tko`): `LoadPtrTkoOp`, `StoreViewTkoOp`, `AtomicCasTkoOp`

- **Optimization passes**: Located in [lib/Dialect/CudaTile/Transforms/]():
  - `LoopSplitPass` at [lib/Dialect/CudaTile/Transforms/LoopSplit.cpp]()
  - Common subexpression elimination (CSE)
  - Canonicalization patterns

- **Debug information**: DWARF-compatible debug info attributes:
  - `mlir::cuda_tile::DILocAttr` for source locations
  - `mlir::cuda_tile::DISubprogramAttr` for function metadata
  - `mlir::cuda_tile::DIFileAttr` for file references

- **Assumption predicates**: Predicates for enabling compiler optimizations:
  - `mlir::cuda_tile::AssumeDivByOp` for divisibility assumptions
  - `mlir::cuda_tile::AssumeSameElementsOp` for element equality
  - `mlir::cuda_tile::AssumeBoundedOp` for value bounds

- **Architecture-specific hints**: `mlir::cuda_tile::OptimizationHintsAttr` for controlling:
  - CTA count and distribution
  - TMA (Tensor Memory Accelerator) usage
  - Latency tolerance
  - Occupancy targets

- **Stable bytecode format**: Version `bytecode::kCurrentVersion` (13.1) with FROZEN opcode policy ensuring backward compatibility in section-based format (Header, String, Type, Constant, Debug, Func)

**Sources:** [README.md:1-12](), [include/Dialect/CudaTile/IR/Types.td](), [include/Dialect/CudaTile/IR/Attrs.td](), [lib/Dialect/CudaTile/Transforms/LoopSplit.cpp](), [lib/Bytecode/Writer/Writer.cpp]()

## License

CUDA Tile IR is licensed under Apache License v2.0 with LLVM Exceptions, matching the LLVM project's licensing model. This allows embedding compiled portions of the software into object form without full Apache 2.0 compliance and enables combination with GPLv2 software.

**Sources:** [LICENSE.txt:1-8](), [README.md:351-354]()

---

