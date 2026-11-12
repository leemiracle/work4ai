<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cuDecomp · page 2 Getting Started · fetched 2026-10-26 -->

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CMakeLists.txt](CMakeLists.txt)
- [README.md](README.md)
- [docs/env_vars.rst](docs/env_vars.rst)
- [docs/overview.rst](docs/overview.rst)
- [include/cudecomp.h](include/cudecomp.h)

</details>



This page provides an introduction to building and running your first cuDecomp program. It covers the essential prerequisites, basic build instructions, and the fundamental workflow for initializing and using the library. For detailed build configuration options, see [Building and Installation](#2.1). For a complete working example with code, see [Quick Start Tutorial](#2.2).

## Purpose and Scope

This Getting Started guide will help you:
- Understand the required dependencies and toolchain
- Build the cuDecomp library from source
- Learn the basic initialization sequence
- Understand the minimal set of API calls needed for decomposition operations

This page does not cover advanced topics like performance autotuning or detailed API usage. For core concepts like pencil decomposition and communication backends, see [Core Concepts](#3).

## Prerequisites

cuDecomp requires specific toolchain components and libraries. The library is designed to work with the NVIDIA HPC SDK, which bundles all required dependencies.

### Required Dependencies

| Dependency | Purpose | Minimum Version |
|------------|---------|-----------------|
| NVHPC SDK | C++/CUDA/Fortran compilers, CUDA runtime, cuTENSOR, NCCL | Recommended (latest) |
| MPI | Inter-process communication | CUDA-aware MPI required |
| CMake | Build system | 3.16+ |

### Optional Dependencies

| Dependency | Purpose | Enable Via |
|------------|---------|------------|
| NVSHMEM | Symmetric memory communication backend | `CUDECOMP_ENABLE_NVSHMEM=ON` |

**Important**: cuDecomp requires CUDA-aware MPI. Verify your MPI library supports this feature. On Cray systems, the Cray MPI with GPU Transport Layer (GTL) is automatically detected and linked [CMakeLists.txt:68-94]().

Sources: [CMakeLists.txt:1-147](), [README.md:30-39]()

## Building the Library

### Basic Build Process

```mermaid
graph LR
    subgraph "Prerequisites"
        NVHPC["NVHPC SDK<br/>(nvc++, nvfortran)"]
        MPI["CUDA-aware MPI"]
        CMAKE["CMake 3.16+"]
    end
    
    subgraph "Build Configuration"
        CONFIG["cmake ..<br/>Configure build options"]
        DETECT["Detect NVHPC compilers<br/>nvc++, nvfortran"]
        FIND["Find dependencies<br/>MPI, NCCL, cuTENSOR"]
    end
    
    subgraph "Compilation"
        LIBCPP["Build libcudecomp.so<br/>C++ library"]
        LIBFORT["Build libcudecomp_fort.so<br/>Fortran bindings"]
        EXTRAS["Build examples/tests<br/>(optional)"]
    end
    
    subgraph "Installation"
        INSTALL["Install to prefix<br/>lib/, include/"]
    end
    
    NVHPC --> DETECT
    MPI --> FIND
    CMAKE --> CONFIG
    
    CONFIG --> DETECT
    DETECT --> FIND
    FIND --> LIBCPP
    LIBCPP --> LIBFORT
    LIBCPP --> EXTRAS
    LIBFORT --> INSTALL
    EXTRAS --> INSTALL
```

**Basic Build**

The minimal build requires only the core library without examples:

```bash
mkdir build
cd build
cmake ..
make -j
```

This creates `libcudecomp.so` in `build/lib/` and installs `cudecomp.h` to `build/include/` [CMakeLists.txt:149-254]().

**Build with Examples and NVSHMEM**

To build additional examples, tests, and enable NVSHMEM backends:

```bash
cmake -DCUDECOMP_BUILD_EXTRAS=ON -DCUDECOMP_ENABLE_NVSHMEM=ON ..
make -j
```

Sources: [README.md:15-27](), [CMakeLists.txt:15-22]()

### Build Options

The following CMake options control the build configuration:

| Option | Default | Description |
|--------|---------|-------------|
| `CUDECOMP_BUILD_FORTRAN` | `ON` | Build Fortran bindings (`libcudecomp_fort.so`) |
| `CUDECOMP_ENABLE_NVTX` | `ON` | Enable NVTX profiling ranges |
| `CUDECOMP_ENABLE_NVSHMEM` | `OFF` | Enable NVSHMEM communication backends |
| `CUDECOMP_BUILD_EXTRAS` | `OFF` | Build benchmarks, examples, and tests |
| `CUDECOMP_NCCL_HOME` | (empty) | Override NCCL installation path |
| `CUDECOMP_NVSHMEM_HOME` | (empty) | Override NVSHMEM installation path |
| `CUDECOMP_CUDA_CC_LIST` | (auto-detected) | CUDA compute capabilities to build for |

The build system automatically detects CUDA compute capabilities based on the CUDA toolkit version [CMakeLists.txt:52-64]().

Sources: [CMakeLists.txt:15-64]()

### Compiler Detection

```mermaid
graph TD
    START["CMake Configuration"]
    
    FIND_NVHPC["find_program(nvc++)"]
    SET_CXX["Set CMAKE_CXX_COMPILER"]
    
    CHECK_FORT{"CUDECOMP_BUILD_FORTRAN?"}
    FIND_FORT["find_program(nvfortran)"]
    SET_FORT["Set CMAKE_Fortran_COMPILER"]
    
    LOCATE_SDK["Locate NVHPC SDK path"]
    SET_PREFIX["Set CMAKE_PREFIX_PATH"]
    
    FIND_DEPS["find_package(NVHPC)<br/>CUDA, MATH, NCCL"]
    
    START --> FIND_NVHPC
    FIND_NVHPC --> SET_CXX
    SET_CXX --> CHECK_FORT
    
    CHECK_FORT -->|Yes| FIND_FORT
    CHECK_FORT -->|No| LOCATE_SDK
    FIND_FORT --> SET_FORT
    SET_FORT --> LOCATE_SDK
    
    LOCATE_SDK --> SET_PREFIX
    SET_PREFIX --> FIND_DEPS
```

The build system locates the NVHPC SDK compilers and automatically configures paths to find CUDA, cuTENSOR, and NCCL libraries bundled with the SDK [CMakeLists.txt:23-122]().

Sources: [CMakeLists.txt:23-146]()

## Library Initialization Workflow

### Basic API Call Sequence

```mermaid
graph TD
    START["Application Start"]
    
    MPI_INIT["MPI_Init()"]
    
    CUDECOMP_INIT["cudecompInit(handle, mpi_comm)"]
    
    CONFIG_INIT["cudecompGridDescConfigSetDefaults(config)"]
    CONFIG_SET["Set config.gdims, config.pdims"]
    
    GRID_CREATE["cudecompGridDescCreate(handle, grid_desc, config, NULL)"]
    
    GET_PENCIL["cudecompGetPencilInfo(handle, grid_desc, pencil_info, axis, ...)"]
    
    ALLOC_DATA["Allocate data buffers"]
    ALLOC_WORK["cudecompMalloc(handle, grid_desc, workspace, size)"]
    
    OPERATIONS["Perform operations:<br/>cudecompTransposeXToY()<br/>cudecompUpdateHalosX()"]
    
    FREE_WORK["cudecompFree(handle, grid_desc, workspace)"]
    FREE_DATA["Free data buffers"]
    
    GRID_DESTROY["cudecompGridDescDestroy(handle, grid_desc)"]
    
    CUDECOMP_FINAL["cudecompFinalize(handle)"]
    
    MPI_FINAL["MPI_Finalize()"]
    
    END["Application End"]
    
    START --> MPI_INIT
    MPI_INIT --> CUDECOMP_INIT
    CUDECOMP_INIT --> CONFIG_INIT
    CONFIG_INIT --> CONFIG_SET
    CONFIG_SET --> GRID_CREATE
    GRID_CREATE --> GET_PENCIL
    GET_PENCIL --> ALLOC_DATA
    ALLOC_DATA --> ALLOC_WORK
    ALLOC_WORK --> OPERATIONS
    OPERATIONS --> FREE_WORK
    FREE_WORK --> FREE_DATA
    FREE_DATA --> GRID_DESTROY
    GRID_DESTROY --> CUDECOMP_FINAL
    CUDECOMP_FINAL --> MPI_FINAL
    MPI_FINAL --> END
```

This diagram shows the complete lifecycle of a cuDecomp application, from initialization through operation and cleanup.

Sources: [include/cudecomp.h:204-261]()

### Minimal Code Structure

A minimal cuDecomp program follows this pattern:

1. **Initialize the library** with `cudecompInit()`, passing an MPI communicator [include/cudecomp.h:213]()
2. **Configure decomposition** using `cudecompGridDescConfig_t` structure [include/cudecomp.h:113-132]()
3. **Create grid descriptor** with `cudecompGridDescCreate()` [include/cudecomp.h:251]()
4. **Query pencil geometry** using `cudecompGetPencilInfo()` [include/cudecomp.h:305]()
5. **Allocate workspaces** with `cudecompMalloc()` [include/cudecomp.h:366]()
6. **Perform operations** like transposes or halo updates
7. **Clean up** in reverse order: free workspaces, destroy grid descriptor, finalize library

### Key Data Structures

```mermaid
graph TD
    subgraph "Opaque Handles"
        HANDLE["cudecompHandle_t<br/>(library instance)"]
        GRIDDESC["cudecompGridDesc_t<br/>(decomposition config)"]
    end
    
    subgraph "Configuration Structures"
        CONFIG["cudecompGridDescConfig_t<br/>gdims[3]: global dimensions<br/>pdims[2]: process grid<br/>transpose_comm_backend<br/>halo_comm_backend"]
        
        AUTOTUNE["cudecompGridDescAutotuneOptions_t<br/>n_warmup_trials<br/>n_trials<br/>autotune_transpose_backend<br/>autotune_halo_backend"]
    end
    
    subgraph "Information Structures"
        PENCIL["cudecompPencilInfo_t<br/>shape[3]: pencil dimensions<br/>lo[3], hi[3]: bounds<br/>order[3]: memory layout<br/>halo_extents[3]<br/>size: total elements"]
    end
    
    subgraph "Enumerations"
        TBACKEND["cudecompTransposeCommBackend_t<br/>CUDECOMP_TRANSPOSE_COMM_MPI_P2P<br/>CUDECOMP_TRANSPOSE_COMM_NCCL<br/>CUDECOMP_TRANSPOSE_COMM_NVSHMEM"]
        
        HBACKEND["cudecompHaloCommBackend_t<br/>CUDECOMP_HALO_COMM_MPI<br/>CUDECOMP_HALO_COMM_NCCL<br/>CUDECOMP_HALO_COMM_NVSHMEM"]
        
        DTYPE["cudecompDataType_t<br/>CUDECOMP_FLOAT<br/>CUDECOMP_DOUBLE<br/>CUDECOMP_FLOAT_COMPLEX<br/>CUDECOMP_DOUBLE_COMPLEX"]
    end
    
    HANDLE --> CONFIG
    CONFIG --> GRIDDESC
    AUTOTUNE -.optional.-> GRIDDESC
    GRIDDESC --> PENCIL
    
    CONFIG --> TBACKEND
    CONFIG --> HBACKEND
    PENCIL --> DTYPE
```

- `cudecompHandle_t`: Opaque pointer representing a library instance, initialized by `cudecompInit()` [include/cudecomp.h:103]()
- `cudecompGridDesc_t`: Opaque pointer representing a decomposition configuration, created by `cudecompGridDescCreate()` [include/cudecomp.h:108]()
- `cudecompGridDescConfig_t`: User-visible structure defining the global grid dimensions, process grid, and communication backends [include/cudecomp.h:113-132]()
- `cudecompPencilInfo_t`: Structure containing geometry information about a pencil, returned by `cudecompGetPencilInfo()` [include/cudecomp.h:194-202]()

Sources: [include/cudecomp.h:42-202]()

### API Function Categories

```mermaid
graph LR
    subgraph "Initialization"
        INIT["cudecompInit()"]
        FINALIZE["cudecompFinalize()"]
    end
    
    subgraph "Grid Configuration"
        CONFIG_DEF["cudecompGridDescConfigSetDefaults()"]
        AUTOTUNE_DEF["cudecompGridDescAutotuneOptionsSetDefaults()"]
        GRID_CREATE["cudecompGridDescCreate()"]
        GRID_DESTROY["cudecompGridDescDestroy()"]
    end
    
    subgraph "Information Queries"
        GET_PENCIL["cudecompGetPencilInfo()"]
        GET_TWORK["cudecompGetTransposeWorkspaceSize()"]
        GET_HWORK["cudecompGetHaloWorkspaceSize()"]
        GET_CONFIG["cudecompGetGridDescConfig()"]
        GET_RANK["cudecompGetShiftedRank()"]
    end
    
    subgraph "Memory Management"
        MALLOC["cudecompMalloc()"]
        FREE["cudecompFree()"]
    end
    
    subgraph "Transpose Operations"
        TXY["cudecompTransposeXToY()"]
        TYZ["cudecompTransposeYToZ()"]
        TZY["cudecompTransposeZToY()"]
        TYX["cudecompTransposeYToX()"]
    end
    
    subgraph "Halo Operations"
        HX["cudecompUpdateHalosX()"]
        HY["cudecompUpdateHalosY()"]
        HZ["cudecompUpdateHalosZ()"]
    end
    
    INIT --> GRID_CREATE
    GRID_CREATE --> GET_PENCIL
    GET_PENCIL --> MALLOC
    MALLOC --> TXY
    MALLOC --> HX
    TXY --> FREE
    HX --> FREE
    FREE --> GRID_DESTROY
    GRID_DESTROY --> FINALIZE
```

The cuDecomp API is organized into six functional categories, each serving a specific purpose in the decomposition workflow.

Sources: [include/cudecomp.h:204-625]()

## Process Grid and Pencils

The decomposition is controlled by two key configuration parameters:

- **`gdims[3]`**: Global grid dimensions `[X, Y, Z]` in column-major order
- **`pdims[2]`**: Process grid dimensions `[P_row, P_col]`

The library creates three pencil orientations:
- **X-pencils**: Shape `[X, Y/P_row, Z/P_col]`, contiguous in X direction
- **Y-pencils**: Shape `[X/P_row, Y, Z/P_col]`, contiguous in Y direction
- **Z-pencils**: Shape `[X/P_row, Y/P_col, Z]`, contiguous in Z direction

Transpose operations redistribute data between these orientations using either row or column communicators [docs/overview.rst:31-65]().

## Communication Backends

cuDecomp supports multiple communication backends, selectable via the `transpose_comm_backend` and `halo_comm_backend` fields in `cudecompGridDescConfig_t`:

| Backend | Enum Value | Requirements |
|---------|------------|--------------|
| MPI P2P | `CUDECOMP_TRANSPOSE_COMM_MPI_P2P` | CUDA-aware MPI |
| MPI P2P Pipelined | `CUDECOMP_TRANSPOSE_COMM_MPI_P2P_PL` | CUDA-aware MPI |
| MPI Alltoallv | `CUDECOMP_TRANSPOSE_COMM_MPI_A2A` | CUDA-aware MPI |
| NCCL | `CUDECOMP_TRANSPOSE_COMM_NCCL` | NCCL library |
| NCCL Pipelined | `CUDECOMP_TRANSPOSE_COMM_NCCL_PL` | NCCL library |
| NVSHMEM | `CUDECOMP_TRANSPOSE_COMM_NVSHMEM` | NVSHMEM library, `CUDECOMP_ENABLE_NVSHMEM=ON` |
| NVSHMEM Pipelined | `CUDECOMP_TRANSPOSE_COMM_NVSHMEM_PL` | NVSHMEM library, `CUDECOMP_ENABLE_NVSHMEM=ON` |

Pipelined backends overlap communication with computation for better performance. The optimal backend depends on system topology, scale, and problem size. Use autotuning to select automatically (see [Performance Autotuning](#7)).

Sources: [include/cudecomp.h:42-63]()

## Next Steps

After successfully building the library, proceed to:

- **[Quick Start Tutorial](#2.2)**: Complete working example with code
- **[Core Concepts](#3)**: Understanding decomposition, pencils, and communication patterns
- **[API Reference](#4)**: Detailed documentation of all functions
- **[Examples and Use Cases](#11)**: Real-world applications including FFT solvers

For runtime configuration, see the environment variables documented in [docs/env_vars.rst:1-100]().

Sources: [README.md:1-43](), [docs/overview.rst:1-66]()

---

