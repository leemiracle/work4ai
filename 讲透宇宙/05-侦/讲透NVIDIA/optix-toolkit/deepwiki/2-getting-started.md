<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/optix-toolkit · page 2 Getting Started · fetched 2026-10-26 -->

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitmodules](.gitmodules)
- [CMakeLists.txt](CMakeLists.txt)
- [DemandLoading/CMakeLists.txt](DemandLoading/CMakeLists.txt)

</details>



This guide covers the essential steps for building and configuring the OptiX Toolkit (OTK). It focuses on the build system setup, dependency management, and basic configuration options needed to compile the toolkit's core libraries and example applications.

For detailed information about individual libraries and their APIs, see [Core Libraries](#1.1). For advanced build system customization and development workflows, see [CMake Development](#6.2).

## Prerequisites and Dependencies

The OptiX Toolkit requires several external dependencies that must be installed before building:

### Required Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| CMake | 3.27+ | Build system orchestration |
| CUDA Toolkit | 11.1+ | GPU computing platform |
| OptiX SDK | 7.3+ | Ray tracing library |
| C++ Compiler | C++11 | Core compilation |

### Dependency Acquisition Methods

The toolkit supports two methods for acquiring third-party dependencies:

```mermaid
graph TB
    subgraph "Build Configuration"
        CMAKE_CONFIG["CMakeLists.txt<br/>cmake_minimum_required(VERSION 3.27)"]
        BUILD_CONFIG["BuildConfig.cmake<br/>OTK_USE_VCPKG option"]
    end
    
    subgraph "Method 1: vcpkg Package Manager"
        VCPKG_SUBMODULE["vcpkg/ submodule<br/>Git submodule"]
        VCPKG_JSON["vcpkg.json<br/>Dependency manifest"]
        VCPKG_CONFIG["vcpkg-configuration.json<br/>Overlay settings"]
    end
    
    subgraph "Method 2: CMake FetchContent"
        FETCH_CONTENT["FetchContent module<br/>Direct download"]
        FIND_PACKAGE["find_package()<br/>System dependencies"]
    end
    
    subgraph "Required External Dependencies"
        CUDA_TOOLKIT["CUDAToolkit<br/>find_package(CUDAToolkit)"]
        OPTIX_SDK["OptiX SDK<br/>OptiX_INSTALL_DIR variable"]
    end

    CMAKE_CONFIG --> BUILD_CONFIG
    BUILD_CONFIG --> |"OTK_USE_VCPKG=ON"| VCPKG_SUBMODULE
    BUILD_CONFIG --> |"OTK_USE_VCPKG=OFF"| FETCH_CONTENT
    
    VCPKG_SUBMODULE --> VCPKG_JSON
    VCPKG_SUBMODULE --> VCPKG_CONFIG
    
    CMAKE_CONFIG --> CUDA_TOOLKIT
    CMAKE_CONFIG --> OPTIX_SDK
```

**vcpkg Method (Recommended)**
- Uses the vcpkg submodule for dependency management
- Configured via `vcpkg.json` manifest file
- Provides consistent, reproducible builds
- Handles complex dependency chains automatically

**FetchContent Method**
- Downloads dependencies at configure time
- Suitable for environments where vcpkg is not available
- Requires manual dependency resolution

Sources: [CMakeLists.txt:14-17](), [CMakeLists.txt:55-59](), [.gitmodules:1-3]()

## Quick Start Build Process

### 1. Clone and Initialize Repository

```bash
git clone https://github.com/NVIDIA/optix-toolkit.git
cd optix-toolkit
git submodule update --init --recursive
```

### 2. Set OptiX SDK Path

The OptiX SDK must be installed separately and its path specified:

```bash
# Set OptiX_INSTALL_DIR to your OptiX SDK installation
export OptiX_INSTALL_DIR=/path/to/optix/sdk
```

### 3. Configure and Build

```bash
# Basic configuration with default options
cmake -B build -S .

# Build the toolkit
cmake --build build --parallel
```

## Core Library Selection and Dependencies

The toolkit uses a modular library system where you can select which components to build:

```mermaid
graph TD
    subgraph "Library Selection System"
        OTK_LIBRARIES["OTK_LIBRARIES variable<br/>Default: ALL"]
        LIBRARY_DEPS["Library Dependencies<br/>Automatic resolution"]
    end
    
    subgraph "Core Libraries"
        DEMAND_LOADING["DemandLoading<br/>Sparse resource loading"]
        MEMORY["Memory<br/>GPU memory management"]
        SHADER_UTIL["ShaderUtil<br/>CUDA/OptiX utilities"]
        OMM_BAKING["OmmBaking<br/>Opacity micromap generation"]
    end
    
    subgraph "Dependency Resolution"
        DEP_DEMAND["DemandLoading_DEPENDENCIES<br/>Memory;ShaderUtil"]
        DEP_MEMORY["Memory_DEPENDENCIES<br/>(none)"]
        DEP_SHADER["ShaderUtil_DEPENDENCIES<br/>Memory"]
        DEP_OMM["OmmBaking_DEPENDENCIES<br/>Memory"]
    end

    OTK_LIBRARIES --> LIBRARY_DEPS
    
    LIBRARY_DEPS --> DEMAND_LOADING
    LIBRARY_DEPS --> MEMORY
    LIBRARY_DEPS --> SHADER_UTIL
    LIBRARY_DEPS --> OMM_BAKING
    
    DEMAND_LOADING --> DEP_DEMAND
    MEMORY --> DEP_MEMORY
    SHADER_UTIL --> DEP_SHADER
    OMM_BAKING --> DEP_OMM
```

The build system automatically resolves dependencies between libraries. For example, selecting `DemandLoading` automatically includes `Memory` and `ShaderUtil`.

Sources: [CMakeLists.txt:76-97]()

## Build Configuration Options

### Primary Build Options

| Option | Default | Description |
|--------|---------|-------------|
| `OTK_LIBRARIES` | `"ALL"` | Semicolon-separated list of libraries to build |
| `OTK_BUILD_EXAMPLES` | `ON` | Build example applications |
| `OTK_BUILD_TESTS` | `ON` | Build unit tests and test framework |
| `OTK_BUILD_PYOPTIX` | `OFF` | Build Python bindings |
| `OTK_BUILD_DOCS` | `OFF` | Build API documentation |
| `OTK_USE_VCPKG` | `ON` | Use vcpkg for dependency management |
| `BUILD_SHARED_LIBS` | `ON` | Build shared libraries instead of static |

### Advanced CUDA Options

For CUDA Toolkit 11.2+, additional memory management options are available:

| Option | Default | Description |
|--------|---------|-------------|
| `OTK_USE_CUDA_MEMORY_POOLS` | `ON` (CUDA 11.2+) | Enable CUDA memory pools and stream-ordered allocators |

Sources: [CMakeLists.txt:33-37](), [DemandLoading/CMakeLists.txt:21-25]()

## Configuration Examples

### Minimal Build (Core Libraries Only)

```bash
cmake -B build -S . \
  -DOTK_BUILD_EXAMPLES=OFF \
  -DOTK_BUILD_TESTS=OFF \
  -DOTK_LIBRARIES="Memory;ShaderUtil"
```

### Full Development Build

```bash
cmake -B build -S . \
  -DOTK_BUILD_EXAMPLES=ON \
  -DOTK_BUILD_TESTS=ON \
  -DOTK_BUILD_DOCS=ON \
  -DOTK_LIBRARIES="ALL"
```

### Custom Library Selection

```bash
cmake -B build -S . \
  -DOTK_LIBRARIES="DemandLoading;OmmBaking"
```

## Build System Architecture

The following diagram shows how the CMake build system processes configuration and manages the modular build:

```mermaid
graph LR
    subgraph "Configuration Phase"
        CMAKE_CONFIGURE["cmake configure<br/>CMakeLists.txt processing"]
        BUILD_CONFIG_MODULE["BuildConfig.cmake<br/>Option processing"]
        POLICIES_MODULE["Policies.cmake<br/>CMake policy settings"]
    end
    
    subgraph "Dependency Resolution"
        FIND_CUDA["find_package(CUDAToolkit)"]
        FIND_OPTIX["find_package(OptiX)"]
        CHECK_OPTIX_DIR["OptiX_INSTALL_DIR validation"]
    end
    
    subgraph "Library Processing"
        LIBRARY_SELECTION["Library selection logic<br/>OTK_LIBRARIES processing"]
        DEP_RESOLUTION["Dependency resolution<br/>buildSubDirs calculation"]
        SUBDIR_CHECK["checkSubDirectory()<br/>Validation and add_subdirectory()"]
    end
    
    subgraph "Build Outputs"
        CORE_LIBS["Core library targets"]
        EXAMPLE_TARGETS["Example executables"]
        TEST_TARGETS["Test executables"]
    end

    CMAKE_CONFIGURE --> BUILD_CONFIG_MODULE
    CMAKE_CONFIGURE --> POLICIES_MODULE
    CMAKE_CONFIGURE --> FIND_CUDA
    CMAKE_CONFIGURE --> FIND_OPTIX
    FIND_OPTIX --> CHECK_OPTIX_DIR
    
    BUILD_CONFIG_MODULE --> LIBRARY_SELECTION
    LIBRARY_SELECTION --> DEP_RESOLUTION
    DEP_RESOLUTION --> SUBDIR_CHECK
    
    SUBDIR_CHECK --> CORE_LIBS
    SUBDIR_CHECK --> EXAMPLE_TARGETS
    SUBDIR_CHECK --> TEST_TARGETS
```

Sources: [CMakeLists.txt:11-29](), [CMakeLists.txt:65-97]()

## Verification and Testing

After building, verify the installation by running the test suite:

```bash
# Run all tests
ctest --test-dir build

# Run tests with verbose output
ctest --test-dir build --verbose
```

The test framework validates core functionality including memory management, demand loading, and OptiX integration. For detailed information about the testing infrastructure, see [Testing Framework](#6.1).

Sources: [CMakeLists.txt:32-37]()

---

