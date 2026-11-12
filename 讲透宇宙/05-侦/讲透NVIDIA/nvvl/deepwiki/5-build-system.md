<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvvl · page 5 Build System · fetched 2026-10-26 -->

# Build System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CMakeLists.txt](CMakeLists.txt)
- [cmake/BuildType.cmake](cmake/BuildType.cmake)
- [cmake/CudaArchFlags.cmake](cmake/CudaArchFlags.cmake)

</details>



## Purpose and Scope

This document describes NVVL's CMake-based build system architecture, including dependency resolution, target configuration, and package generation. It covers the top-level build organization and how the various CMake modules work together to produce the shared library.

For specific topics:
- Build type configuration and compiler flags: see [CMake Configuration](#5.1)
- CUDA GPU architecture selection: see [CUDA Architecture Detection](#5.2)
- Installation and downstream integration: see [Package Configuration](#5.3)

## Build System Architecture

NVVL uses CMake 3.8+ as its build system, organized into a main configuration file and specialized modules for different aspects of the build.

### CMake Module Organization

```mermaid
graph TB
    Main["CMakeLists.txt<br/>Main Build Configuration"]
    BuildType["cmake/BuildType.cmake<br/>Build Type Defaults"]
    CudaArch["cmake/CudaArchFlags.cmake<br/>CUDA Architecture Flags"]
    ConfigIn["cmake/NVVLConfig.cmake.in<br/>Package Config Template"]
    
    DocDir["doc/CMakeLists.txt<br/>Documentation Build"]
    ExamplesDir["doc/examples/CMakeLists.txt<br/>Examples Build"]
    
    Main -->|"include()"| BuildType
    Main -->|"include()"| CudaArch
    Main -->|"configure_package_config_file()"| ConfigIn
    Main -->|"add_subdirectory(EXCLUDE_FROM_ALL)"| DocDir
    Main -->|"add_subdirectory(EXCLUDE_FROM_ALL)"| ExamplesDir
    
    BuildType -.->|"sets"| BuildTypeVar["CMAKE_BUILD_TYPE<br/>CMAKE_CXX_FLAGS_DEBUG"]
    CudaArch -.->|"appends to"| CudaFlags["CMAKE_CUDA_FLAGS<br/>-gencode arch=compute_XX"]
    ConfigIn -.->|"generates"| ConfigOut["NVVLConfig.cmake<br/>find_package() support"]
```

**Build System Module Structure**

Sources: [CMakeLists.txt:1-14](), [cmake/BuildType.cmake:1-17](), [cmake/CudaArchFlags.cmake:1-51]()

The build system is organized into three primary modules:
- **Main configuration** ([CMakeLists.txt]()) - Project definition, targets, dependencies, installation
- **Build type module** ([cmake/BuildType.cmake]()) - Sets default build configuration to `RelWithDebInfo`
- **CUDA architecture module** ([cmake/CudaArchFlags.cmake]()) - Generates GPU architecture compilation flags

## Build Process Flow

### Initialization and Configuration

```mermaid
graph TD
    Start["cmake .."]
    
    MinVer["Check CMake >= 3.8"]
    CudaFlags["Set CMAKE_CUDA_FLAGS<br/>-cudart shared"]
    Project["project(NVVL VERSION 1.0<br/>LANGUAGES C CXX CUDA)"]
    
    IncludeBT["include(cmake/BuildType.cmake)"]
    SetBuildType["Set CMAKE_BUILD_TYPE<br/>default: RelWithDebInfo"]
    
    IncludeCA["include(cmake/CudaArchFlags.cmake)"]
    ProcessArch["Process CUDA_ARCH list<br/>Generate -gencode flags"]
    
    FindPkg["find_package(PkgConfig REQUIRED)"]
    FindFFmpeg["pkg_check_modules()<br/>avformat avcodec avfilter avutil"]
    CheckFFmpeg["check_struct_has_member()<br/>check_type_size()"]
    
    Start --> MinVer
    MinVer --> CudaFlags
    CudaFlags --> Project
    Project --> IncludeBT
    IncludeBT --> SetBuildType
    SetBuildType --> IncludeCA
    IncludeCA --> ProcessArch
    ProcessArch --> FindPkg
    FindPkg --> FindFFmpeg
    FindFFmpeg --> CheckFFmpeg
    CheckFFmpeg --> DefineTargets["Define Build Targets"]
```

**CMake Configuration Phase**

Sources: [CMakeLists.txt:1-29](), [cmake/BuildType.cmake:4-13](), [cmake/CudaArchFlags.cmake:9-21]()

The configuration phase proceeds through these steps:

1. **Version check** - Ensures CMake 3.8+ for CUDA language support
2. **CUDA runtime setup** - Sets `-cudart shared` flag if not already defined [CMakeLists.txt:3-5]()
3. **Project declaration** - Defines NVVL 1.0 with C, C++, and CUDA languages [CMakeLists.txt:7]()
4. **Build type configuration** - Sets default to `RelWithDebInfo` if not specified [cmake/BuildType.cmake:4-13]()
5. **Architecture detection** - Processes `CUDA_ARCH` variable and generates `-gencode` flags [cmake/CudaArchFlags.cmake:9-51]()
6. **Dependency resolution** - Finds FFmpeg libraries via `pkg-config` and checks API compatibility [CMakeLists.txt:17-28]()

### Target Definition and Compilation

```mermaid
graph LR
    subgraph "Library Target: nvvl"
        Sources["Source Files<br/>VideoLoader.cpp<br/>PictureSequence.cpp<br/>CUVideoDecoder.cpp<br/>imgproc.cu<br/>..."]
        
        Compile["Compilation<br/>C++14 standard<br/>-Wall warnings<br/>CUDA separable compilation"]
        
        Link["Linking<br/>FFmpeg libs<br/>cuda<br/>nvcuvid<br/>nvidia-ml"]
        
        Output["libnvvl.so<br/>Shared Library"]
    end
    
    Sources --> Compile
    Compile --> Link
    Link --> Output
    
    Features["Compile Features<br/>cxx_std_14"] -.-> Compile
    Props["Properties<br/>POSITION_INDEPENDENT_CODE<br/>CUDA_SEPARABLE_COMPILATION"] -.-> Compile
    Defs["Definitions<br/>HAVE_AVSTREAM_CODECPAR<br/>HAVE_AVBSFCONTEXT"] -.-> Compile
```

**Build Target Configuration**

Sources: [CMakeLists.txt:32-74]()

The main build target `nvvl` is a shared library with these characteristics:

| Property | Value | Line Reference |
|----------|-------|----------------|
| Target name | `nvvl` | [CMakeLists.txt:32]() |
| Export name | `NVVL` | [CMakeLists.txt:62]() |
| Namespace | `NVVL::NVVL` | [CMakeLists.txt:44]() |
| Language standard | C++14 | [CMakeLists.txt:46]() |
| Position-independent code | ON | [CMakeLists.txt:60]() |
| CUDA separable compilation | ON | [CMakeLists.txt:61]() |

**Source Files**

The library comprises 10 source files [CMakeLists.txt:33-42]():
- `src/VideoLoader.cpp` - Main API implementation
- `src/PictureSequence.cpp` - Frame sequence management
- `src/detail/CUContext.cpp` - CUDA context wrapper
- `src/detail/CUVideoDecoder.cpp` - Video decoder wrapper
- `src/detail/CUVideoParser.cpp` - Video stream parser
- `src/detail/Decoder.cpp` - Decoder abstraction
- `src/detail/JoiningThread.cpp` - Thread management
- `src/detail/NvDecoder.cpp` - NVIDIA decoder implementation
- `src/detail/cuda/imgproc.cu` - CUDA image processing kernels

## Dependency Management

### FFmpeg Library Detection

```mermaid
graph TB
    PkgConfig["PkgConfig Module<br/>find_package(PkgConfig REQUIRED)"]
    
    Loop["foreach(m avformat avcodec avfilter avutil)"]
    
    Check["pkg_check_modules($m REQUIRED<br/>IMPORTED_TARGET lib$m)"]
    
    Target["Creates PkgConfig::$m<br/>imported target"]
    
    Append["list(APPEND FFmpeg_LIBS<br/>PkgConfig::$m)"]
    
    Link["target_link_libraries(nvvl<br/>PRIVATE ${FFmpeg_LIBS})"]
    
    PkgConfig --> Loop
    Loop --> Check
    Check --> Target
    Target --> Append
    Append --> Link
```

**FFmpeg Component Resolution**

Sources: [CMakeLists.txt:17-22]()

The build system uses `pkg-config` to locate FFmpeg libraries:

1. **Module iteration** - Loops through required FFmpeg components: `avformat`, `avcodec`, `avfilter`, `avutil` [CMakeLists.txt:18]()
2. **Package check** - Calls `pkg_check_modules()` with `IMPORTED_TARGET` to create CMake targets [CMakeLists.txt:20]()
3. **Target accumulation** - Builds `FFmpeg_LIBS` list with `PkgConfig::avformat`, `PkgConfig::avcodec`, etc. [CMakeLists.txt:21]()

### FFmpeg API Compatibility Checks

```mermaid
graph LR
    SetIncludes["CMAKE_REQUIRED_INCLUDES<br/>= avformat_INCLUDE_DIRS"]
    SetLibs["CMAKE_REQUIRED_LIBRARIES<br/>= avformat_LIBRARIES"]
    
    Check1["check_struct_has_member()<br/>AVStream.codecpar"]
    Result1["HAVE_AVSTREAM_CODECPAR"]
    
    Check2["check_type_size()<br/>AVBSFContext"]
    Result2["HAVE_AVBSFCONTEXT"]
    
    SetIncludes --> Check1
    SetLibs --> Check1
    Check1 --> Result1
    
    Check2 --> Result2
    
    Result1 -.->|"if defined"| Def1["target_compile_definitions()<br/>HAVE_AVSTREAM_CODECPAR=1"]
    Result2 -.->|"if defined"| Def2["target_compile_definitions()<br/>HAVE_AVBSFCONTEXT=1"]
```

**API Version Detection**

Sources: [CMakeLists.txt:24-57]()

NVVL adapts to different FFmpeg versions through compile-time checks:

1. **AVStream.codecpar check** [CMakeLists.txt:26]()
   - Tests for `codecpar` member in `struct AVStream`
   - Sets `HAVE_AVSTREAM_CODECPAR` if present
   - Defines preprocessor macro for conditional compilation [CMakeLists.txt:51-53]()

2. **AVBSFContext check** [CMakeLists.txt:28]()
   - Tests for `AVBSFContext` type existence
   - Sets `HAVE_AVBSFCONTEXT` if present
   - Defines preprocessor macro for conditional compilation [CMakeLists.txt:55-57]()

These checks enable backward compatibility with older FFmpeg versions while using newer APIs when available.

### CUDA and NVIDIA Libraries

```mermaid
graph LR
    CudaToolkit["CMAKE_CUDA_TOOLKIT_INCLUDE_DIRECTORIES<br/>CUDA headers from toolkit"]
    
    LibCuda["cuda<br/>CUDA runtime"]
    LibNvcuvid["nvcuvid<br/>Hardware video decoder"]
    LibNvml["nvidia-ml<br/>GPU management"]
    
    TargetInclude["target_include_directories(nvvl<br/>PUBLIC ${CMAKE_CUDA_TOOLKIT_INCLUDE_DIRECTORIES})"]
    
    TargetLink["target_link_libraries(nvvl<br/>PRIVATE cuda nvcuvid nvidia-ml)"]
    
    CudaToolkit --> TargetInclude
    LibCuda --> TargetLink
    LibNvcuvid --> TargetLink
    LibNvml --> TargetLink
```

**NVIDIA Library Dependencies**

Sources: [CMakeLists.txt:69-74]()

The library links against three NVIDIA libraries [CMakeLists.txt:73]():

| Library | Purpose |
|---------|---------|
| `cuda` | CUDA runtime API |
| `nvcuvid` | Hardware video decoding via CUVID API |
| `nvidia-ml` | GPU device management and monitoring |

CUDA toolkit headers are included via `CMAKE_CUDA_TOOLKIT_INCLUDE_DIRECTORIES` [CMakeLists.txt:69](), which CMake populates automatically when CUDA is enabled as a project language.

## Installation and Export

### Installation Targets

```mermaid
graph TD
    LibTarget["install(TARGETS nvvl<br/>EXPORT nvvl-targets)"]
    LibDest["LIBRARY DESTINATION<br/>${CMAKE_INSTALL_LIBDIR}"]
    ArchDest["ARCHIVE DESTINATION<br/>${CMAKE_INSTALL_LIBDIR}"]
    
    Headers["install(DIRECTORY include/<br/>DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})"]
    
    ExportTargets["install(EXPORT nvvl-targets<br/>FILE NVVLTargets.cmake<br/>NAMESPACE NVVL::)"]
    ExportDest["DESTINATION<br/>${CMAKE_INSTALL_LIBDIR}/cmake/NVVL"]
    
    ConfigFiles["install(FILES<br/>NVVLConfig.cmake<br/>NVVLConfigVersion.cmake)"]
    
    LibTarget --> LibDest
    LibTarget --> ArchDest
    LibTarget -.->|"generates"| ExportTargets
    
    Headers --> HeaderDest["${CMAKE_INSTALL_INCLUDEDIR}/"]
    
    ExportTargets --> ExportDest
    ConfigFiles --> ExportDest
```

**Installation Layout**

Sources: [CMakeLists.txt:76-116]()

The installation process creates this directory structure:

```
${CMAKE_INSTALL_PREFIX}/
├── lib/
│   ├── libnvvl.so                    # Shared library
│   └── cmake/NVVL/
│       ├── NVVLTargets.cmake         # Imported target definitions
│       ├── NVVLConfig.cmake          # Package configuration
│       └── NVVLConfigVersion.cmake   # Version compatibility
└── include/
    ├── VideoLoader.h                 # Public headers
    ├── PictureSequence.h
    └── ...
```

**Installation Components:**

1. **Library files** [CMakeLists.txt:80-84]()
   - Shared library (`libnvvl.so`) to `${CMAKE_INSTALL_LIBDIR}`
   - Archive variant to same location for static linking

2. **Header files** [CMakeLists.txt:86]()
   - All files from `include/` directory to `${CMAKE_INSTALL_INCLUDEDIR}`

3. **CMake export files** [CMakeLists.txt:89-96]()
   - `NVVLTargets.cmake` defining the `NVVL::NVVL` imported target
   - Uses namespace `NVVL::` for all exported targets

4. **Package configuration** [CMakeLists.txt:98-116]()
   - `NVVLConfigVersion.cmake` for version compatibility checks
   - `NVVLConfig.cmake` generated from template for `find_package()` support

### Build Tree Export

```mermaid
graph LR
    ExportCmd["export(EXPORT nvvl-targets<br/>FILE NVVLTargets.cmake<br/>NAMESPACE NVVL::)"]
    
    Location["${CMAKE_CURRENT_BINARY_DIR}/<br/>NVVLTargets.cmake"]
    
    Registry["export(PACKAGE NVVL)"]
    UserRegistry["~/.cmake/packages/NVVL/"]
    
    ExportCmd --> Location
    Location -.->|"enables"| BuildTreeUse["Use from build tree<br/>without installation"]
    
    Registry --> UserRegistry
    UserRegistry -.->|"enables"| AutoFind["find_package(NVVL)<br/>finds build tree"]
```

**Build Tree Integration**

Sources: [CMakeLists.txt:118-122]()

NVVL can be used directly from the build tree without installation:

1. **Export to build directory** [CMakeLists.txt:119]()
   - Creates `NVVLTargets.cmake` in build directory
   - Allows downstream projects to use `find_package(NVVL PATHS /path/to/build)`

2. **User package registry** [CMakeLists.txt:122]()
   - Registers build tree location in `~/.cmake/packages/NVVL/`
   - Enables automatic discovery via `find_package(NVVL)` without specifying path
   - Useful for development workflows where library is frequently rebuilt

## Build Targets Summary

### Primary Targets

| Target | Type | Description | Source |
|--------|------|-------------|--------|
| `nvvl` | Shared Library | Main library target | [CMakeLists.txt:32]() |
| `NVVL::NVVL` | Alias | Namespace alias for library | [CMakeLists.txt:44]() |
| `doc` | Subdirectory | Documentation generation (excluded from all) | [CMakeLists.txt:124]() |
| `doc/examples` | Subdirectory | Example programs (excluded from all) | [CMakeLists.txt:125]() |

Sources: [CMakeLists.txt:32-44](), [CMakeLists.txt:124-126]()

Both `doc` and `doc/examples` subdirectories are marked `EXCLUDE_FROM_ALL`, meaning they are not built by default when running `make` or `cmake --build .`. They must be explicitly requested:

```bash
cmake --build . --target doc          # Build documentation
cmake --build . --target extract_frames  # Build specific example
```

### Compiler and Linker Configuration

**Compile Options** [CMakeLists.txt:48-49]():
- `-Wall` enabled for C/C++ code (not CUDA)
- `-Wno-unused-function` suppresses unused function warnings
- Applied only to non-CUDA source files using generator expression

**CUDA Configuration**:
- Shared CUDA runtime (`-cudart shared`) [CMakeLists.txt:4]()
- Separable compilation enabled [CMakeLists.txt:61]()
- Architecture flags generated by [cmake/CudaArchFlags.cmake]()

**Debug Configuration** [cmake/BuildType.cmake:16]():
- Uses `-Og` optimization for faster debugging with modern GCC
- Includes `-g` for debug symbols

Sources: [CMakeLists.txt:3-5](), [CMakeLists.txt:48-49](), [CMakeLists.txt:59-63](), [cmake/BuildType.cmake:16]()

---

