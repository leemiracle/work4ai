<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/ACCV-Lab · page 3 Build System · fetched 2026-10-26 -->

# Build System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [build_config/__init__.py](build_config/__init__.py)
- [build_config/accvlab_build_config/__init__.py](build_config/accvlab_build_config/__init__.py)
- [build_config/accvlab_build_config/helpers/__init__.py](build_config/accvlab_build_config/helpers/__init__.py)

</details>



## Purpose and Scope

The Build System provides centralized build configuration and utilities for all ACCV-Lab packages. This document covers the `build_config/` directory structure, the `accvlab_build_config` package, and how it supports building C++/CUDA extensions across the repository. For information about installing packages using these build utilities, see [Local Installation](#2.2). For details about configuring the development environment, see [Docker Environment](#2.1).

## Overview

The build system serves as a shared foundation that standardizes compilation across all ACCV-Lab packages. It handles CUDA architecture detection, compiler flag generation, and provides utilities for both setuptools-based extension builds and external CMake projects.

```mermaid
graph TB
    subgraph "Repository Structure"
        ROOT["Repository Root"]
        BUILD_CONFIG["build_config/"]
        PACKAGES["packages/"]
    end
    
    subgraph "Build Configuration Package"
        PKG["accvlab_build_config"]
        HELPERS["helpers/"]
        BUILD_UTILS["build_utils.py"]
        CMAKE_ARGS["cmake_args.py"]
    end
    
    subgraph "Consumer Packages"
        OVDEC["on_demand_video_decoder"]
        BATCH["batching_helpers"]
        DALI["dali_pipeline_framework"]
        HEATMAP["draw_heatmap"]
        OPTIM["optim_test_tools"]
    end
    
    ROOT --> BUILD_CONFIG
    ROOT --> PACKAGES
    
    BUILD_CONFIG --> PKG
    PKG --> HELPERS
    HELPERS --> BUILD_UTILS
    HELPERS --> CMAKE_ARGS
    
    PACKAGES --> OVDEC
    PACKAGES --> BATCH
    PACKAGES --> DALI
    PACKAGES --> HEATMAP
    PACKAGES --> OPTIM
    
    OVDEC -.->|imports| PKG
    BATCH -.->|imports| PKG
    DALI -.->|imports| PKG
    HEATMAP -.->|imports| PKG
    OPTIM -.->|imports| PKG
```

**Sources:** [build_config/__init__.py](), [build_config/accvlab_build_config/__init__.py](), [README.md:105-110]()

## Package Structure

The `build_config/` directory contains the `accvlab_build_config` package, which is structured as a standard Python package with helper modules.

| Directory/File | Purpose |
|----------------|---------|
| `build_config/` | Top-level directory for build configuration |
| `build_config/accvlab_build_config/` | Main package directory |
| `build_config/accvlab_build_config/helpers/` | Helper modules containing core functionality |
| `build_config/accvlab_build_config/helpers/build_utils.py` | Build utilities for configuration and compilation |
| `build_config/accvlab_build_config/helpers/cmake_args.py` | CMake argument generation from environment variables |

```mermaid
graph LR
    subgraph "accvlab_build_config Package"
        INIT["__init__.py"]
        HELPERS_INIT["helpers/__init__.py"]
        BUILD_UTILS["helpers/build_utils.py"]
        CMAKE_ARGS["helpers/cmake_args.py"]
    end
    
    subgraph "Exported Functions"
        LOAD["load_config()"]
        DETECT["detect_cuda_info()"]
        FLAGS["get_compile_flags()"]
        EXTERNAL["run_external_build()"]
        ABS_DIR["get_abs_setup_dir()"]
        CMAKE["build_cmake_args_from_env()"]
    end
    
    BUILD_UTILS --> LOAD
    BUILD_UTILS --> DETECT
    BUILD_UTILS --> FLAGS
    BUILD_UTILS --> EXTERNAL
    BUILD_UTILS --> ABS_DIR
    CMAKE_ARGS --> CMAKE
    
    HELPERS_INIT --> LOAD
    HELPERS_INIT --> DETECT
    HELPERS_INIT --> FLAGS
    HELPERS_INIT --> EXTERNAL
    HELPERS_INIT --> ABS_DIR
    HELPERS_INIT --> CMAKE
    
    INIT -.->|exports all| HELPERS_INIT
```

The package exports all helper functions through its top-level `__init__.py`, allowing consumers to import directly from `accvlab_build_config`.

**Sources:** [build_config/accvlab_build_config/__init__.py:15](), [build_config/accvlab_build_config/helpers/__init__.py:19-37]()

## Build Utilities

The `build_utils` module provides five core functions that support package compilation:

### Function Overview

| Function | Purpose | Returns |
|----------|---------|---------|
| `load_config()` | Loads build configuration from environment variables | Configuration dictionary |
| `detect_cuda_info()` | Detects CUDA architecture and version information from PyTorch | CUDA information dictionary |
| `get_compile_flags()` | Generates compiler flags for C++/CUDA compilation | List of compiler flags |
| `run_external_build()` | Executes external build processes (e.g., CMake builds) | None (side effect: builds artifacts) |
| `get_abs_setup_dir()` | Returns absolute path to the setup.py directory | Absolute path string |

### Build Workflow Using Utilities

```mermaid
graph TD
    START["Package setup.py Execution"]
    
    subgraph "Configuration Phase"
        GET_DIR["get_abs_setup_dir()"]
        LOAD["load_config()"]
        ENV["Environment Variables"]
    end
    
    subgraph "CUDA Detection Phase"
        DETECT["detect_cuda_info()"]
        TORCH["PyTorch CUDA Info"]
        CUDA_ARCH["CUDA Architectures"]
    end
    
    subgraph "Compilation Phase"
        FLAGS["get_compile_flags()"]
        COMPILER["C++ Compiler"]
        EXTENSION["Extension Modules"]
    end
    
    subgraph "External Build Phase"
        CMAKE["build_cmake_args_from_env()"]
        EXTERNAL["run_external_build()"]
        CMAKE_PROJECT["CMake Projects"]
    end
    
    START --> GET_DIR
    START --> LOAD
    ENV --> LOAD
    
    LOAD --> DETECT
    DETECT --> TORCH
    TORCH --> CUDA_ARCH
    
    LOAD --> FLAGS
    CUDA_ARCH --> FLAGS
    FLAGS --> COMPILER
    COMPILER --> EXTENSION
    
    ENV --> CMAKE
    CMAKE --> EXTERNAL
    EXTERNAL --> CMAKE_PROJECT
```

**Sources:** [build_config/accvlab_build_config/helpers/__init__.py:19-37]()

## Configuration Loading

The `load_config()` function reads environment variables to determine build settings. It serves as the entry point for all build configuration, parsing environment variables into a structured format that other build utilities can consume.

### Key Configuration Parameters

Based on the repository's build system design, the following environment variables are recognized:

| Environment Variable | Purpose | Default Behavior |
|---------------------|---------|------------------|
| `DEBUG_BUILD` | Enable debug symbols and disable optimizations | Release build |
| `CPP_STANDARD` | Set C++ standard version (e.g., 11, 14, 17, 20) | Compiler default |
| `CUSTOM_CUDA_ARCHS` | Override CUDA architecture targets | Auto-detected from PyTorch |

**Sources:** [build_config/accvlab_build_config/helpers/__init__.py:20](), README references to environment variables

## CUDA Detection

The `detect_cuda_info()` function queries CUDA-related information from the installed PyTorch version. This ensures that compiled extensions are compatible with the PyTorch CUDA environment.

### Detection Process

```mermaid
graph LR
    DETECT["detect_cuda_info()"]
    TORCH_CHECK["Check PyTorch Installation"]
    CUDA_VERSION["Extract CUDA Version"]
    CUDA_ARCHS["Extract CUDA Architectures"]
    INFO["Return CUDA Info Dict"]
    
    DETECT --> TORCH_CHECK
    TORCH_CHECK --> CUDA_VERSION
    TORCH_CHECK --> CUDA_ARCHS
    CUDA_VERSION --> INFO
    CUDA_ARCHS --> INFO
```

The function retrieves:
- CUDA version installed with PyTorch
- CUDA architectures that PyTorch was compiled for
- Whether CUDA is available in the current environment

This information is critical for ensuring that compiled extensions can interoperate with PyTorch tensors on CUDA devices.

**Sources:** [build_config/accvlab_build_config/helpers/__init__.py:21]()

## Compilation Flag Generation

The `get_compile_flags()` function generates appropriate compiler flags based on the loaded configuration and detected CUDA information.

### Flag Categories

```mermaid
graph TB
    GET_FLAGS["get_compile_flags()"]
    
    subgraph "Input Sources"
        CONFIG["load_config() Result"]
        CUDA_INFO["detect_cuda_info() Result"]
    end
    
    subgraph "Generated Flags"
        STD_FLAGS["C++ Standard Flags"]
        DEBUG_FLAGS["Debug/Optimization Flags"]
        CUDA_FLAGS["CUDA Architecture Flags"]
        INCLUDE_FLAGS["Include Path Flags"]
    end
    
    subgraph "Output"
        COMPILER_FLAGS["Compiler Flag List"]
    end
    
    CONFIG --> GET_FLAGS
    CUDA_INFO --> GET_FLAGS
    
    GET_FLAGS --> STD_FLAGS
    GET_FLAGS --> DEBUG_FLAGS
    GET_FLAGS --> CUDA_FLAGS
    GET_FLAGS --> INCLUDE_FLAGS
    
    STD_FLAGS --> COMPILER_FLAGS
    DEBUG_FLAGS --> COMPILER_FLAGS
    CUDA_FLAGS --> COMPILER_FLAGS
    INCLUDE_FLAGS --> COMPILER_FLAGS
```

The function ensures that:
- CUDA architecture flags match PyTorch's CUDA compilation targets
- Debug builds include appropriate symbols and disable optimizations
- C++ standard is set consistently across all extensions

**Sources:** [build_config/accvlab_build_config/helpers/__init__.py:22]()

## CMake Integration

The `cmake_args` module provides the `build_cmake_args_from_env()` function, which generates CMake command-line arguments from environment variables.

### CMake Argument Generation

```mermaid
graph TD
    ENV_VARS["Environment Variables"]
    BUILD_CMAKE["build_cmake_args_from_env()"]
    
    subgraph "Processed Variables"
        DEBUG["DEBUG_BUILD"]
        STD["CPP_STANDARD"]
        CUDA["CUSTOM_CUDA_ARCHS"]
        CUSTOM["Other CMake Variables"]
    end
    
    subgraph "Generated Arguments"
        BUILD_TYPE["-DCMAKE_BUILD_TYPE"]
        CXX_STD["-DCMAKE_CXX_STANDARD"]
        CUDA_ARCH["-DCMAKE_CUDA_ARCHITECTURES"]
        OTHERS["-D&lt;VAR&gt;=&lt;VALUE&gt;"]
    end
    
    CMAKE_ARGS["CMake Argument List"]
    
    ENV_VARS --> DEBUG
    ENV_VARS --> STD
    ENV_VARS --> CUDA
    ENV_VARS --> CUSTOM
    
    DEBUG --> BUILD_CMAKE
    STD --> BUILD_CMAKE
    CUDA --> BUILD_CMAKE
    CUSTOM --> BUILD_CMAKE
    
    BUILD_CMAKE --> BUILD_TYPE
    BUILD_CMAKE --> CXX_STD
    BUILD_CMAKE --> CUDA_ARCH
    BUILD_CMAKE --> OTHERS
    
    BUILD_TYPE --> CMAKE_ARGS
    CXX_STD --> CMAKE_ARGS
    CUDA_ARCH --> CMAKE_ARGS
    OTHERS --> CMAKE_ARGS
```

### Usage Pattern

Packages that use CMake for building external components call `build_cmake_args_from_env()` to obtain a list of CMake arguments, then pass these arguments to `run_external_build()` or directly invoke CMake:

```python
from accvlab_build_config import build_cmake_args_from_env, run_external_build

cmake_args = build_cmake_args_from_env()
run_external_build(cmake_args)
```

**Sources:** [build_config/accvlab_build_config/helpers/__init__.py:26-28]()

## External Build Execution

The `run_external_build()` function executes external build systems, typically CMake-based projects. This is used by packages that have native code organized as CMake projects rather than setuptools extensions.

### Build Execution Flow

```mermaid
graph TD
    SETUP["Package setup.py"]
    CMAKE_ARGS["build_cmake_args_from_env()"]
    RUN_BUILD["run_external_build()"]
    
    subgraph "External Build Process"
        CONFIG["CMake Configuration"]
        COMPILE["CMake Compilation"]
        INSTALL["CMake Installation"]
    end
    
    OUTPUT["Built Artifacts"]
    PACKAGE["Package Installation"]
    
    SETUP --> CMAKE_ARGS
    CMAKE_ARGS --> RUN_BUILD
    RUN_BUILD --> CONFIG
    CONFIG --> COMPILE
    COMPILE --> INSTALL
    INSTALL --> OUTPUT
    OUTPUT --> PACKAGE
```

The function handles:
- Setting up the build directory
- Running CMake configuration with generated arguments
- Executing the build process
- Ensuring artifacts are placed in the correct package directories

**Sources:** [build_config/accvlab_build_config/helpers/__init__.py:23]()

## Integration with Package Builds

Individual packages integrate with the build system by importing functions from `accvlab_build_config` in their `setup.py` files.

### Setuptools Extension Build Pattern

```mermaid
graph TB
    SETUP["Package setup.py"]
    
    subgraph "Build Configuration Import"
        IMPORT["from accvlab_build_config import *"]
    end
    
    subgraph "Configuration Steps"
        LOAD["config = load_config()"]
        DETECT["cuda_info = detect_cuda_info()"]
        FLAGS["flags = get_compile_flags(config, cuda_info)"]
    end
    
    subgraph "Extension Definition"
        EXT_DEF["Extension() with flags"]
        PYBIND["Pybind11Extension()"]
    end
    
    SETUPTOOLS["setuptools.setup()"]
    INSTALL["Installed Package"]
    
    SETUP --> IMPORT
    IMPORT --> LOAD
    LOAD --> DETECT
    DETECT --> FLAGS
    FLAGS --> EXT_DEF
    EXT_DEF --> PYBIND
    PYBIND --> SETUPTOOLS
    SETUPTOOLS --> INSTALL
```

### Scikit-build Pattern

Some packages use scikit-build for building with CMake:

```mermaid
graph TB
    SETUP["Package setup.py"]
    
    subgraph "Build Configuration Import"
        IMPORT["from accvlab_build_config import build_cmake_args_from_env"]
    end
    
    subgraph "CMake Integration"
        CMAKE_ARGS["args = build_cmake_args_from_env()"]
        SKBUILD["skbuild.setup(cmake_args=args)"]
    end
    
    CMAKE_BUILD["CMake Build Process"]
    INSTALL["Installed Package"]
    
    SETUP --> IMPORT
    IMPORT --> CMAKE_ARGS
    CMAKE_ARGS --> SKBUILD
    SKBUILD --> CMAKE_BUILD
    CMAKE_BUILD --> INSTALL
```

**Sources:** [build_config/accvlab_build_config/helpers/__init__.py:19-37](), [README.md:90-93]()

## Complete Build System Architecture

```mermaid
graph TB
    subgraph "User Input"
        ENV["Environment Variables<br/>DEBUG_BUILD, CPP_STANDARD,<br/>CUSTOM_CUDA_ARCHS"]
        NS_CONFIG["namespace_packages_config.py"]
    end
    
    subgraph "Build Configuration Package"
        BUILD_CONFIG["accvlab_build_config"]
        LOAD_CONFIG["load_config()"]
        DETECT_CUDA["detect_cuda_info()"]
        GET_FLAGS["get_compile_flags()"]
        CMAKE_BUILD["build_cmake_args_from_env()"]
        EXTERNAL_BUILD["run_external_build()"]
    end
    
    subgraph "External Dependencies"
        PYTORCH["PyTorch<br/>CUDA Info Source"]
        PYBIND["Pybind11<br/>Git Submodule"]
        DLPACK["DLPack<br/>Git Submodule"]
        NVTX["NVTX<br/>Git Submodule"]
    end
    
    subgraph "Package Builds"
        PKG_SETUP["Package setup.py"]
        CPP_CODE["C++/CUDA Source Code"]
        EXTENSIONS["Compiled Extensions"]
    end
    
    subgraph "Installation"
        INSTALLED["Installed Packages"]
        PYTHON_ENV["Python Environment"]
    end
    
    ENV --> LOAD_CONFIG
    NS_CONFIG --> PKG_SETUP
    
    BUILD_CONFIG --> LOAD_CONFIG
    BUILD_CONFIG --> DETECT_CUDA
    BUILD_CONFIG --> GET_FLAGS
    BUILD_CONFIG --> CMAKE_BUILD
    BUILD_CONFIG --> EXTERNAL_BUILD
    
    PYTORCH --> DETECT_CUDA
    
    PKG_SETUP --> LOAD_CONFIG
    PKG_SETUP --> DETECT_CUDA
    LOAD_CONFIG --> GET_FLAGS
    DETECT_CUDA --> GET_FLAGS
    
    GET_FLAGS --> CPP_CODE
    CMAKE_BUILD --> EXTERNAL_BUILD
    EXTERNAL_BUILD --> CPP_CODE
    
    PYBIND --> CPP_CODE
    DLPACK --> CPP_CODE
    NVTX --> CPP_CODE
    
    CPP_CODE --> EXTENSIONS
    EXTENSIONS --> INSTALLED
    INSTALLED --> PYTHON_ENV
```

This diagram shows the complete flow from user configuration through the build system to installed packages. The `accvlab_build_config` package serves as the central coordination point, consuming environment variables and PyTorch information to generate appropriate build configurations for all package builds.

**Sources:** [build_config/accvlab_build_config/__init__.py:15](), [build_config/accvlab_build_config/helpers/__init__.py](), [README.md:69-93]()

## Build System Benefits

The centralized build system provides several key advantages:

| Benefit | Description |
|---------|-------------|
| **Consistency** | All packages use the same CUDA architectures and compilation flags |
| **Maintainability** | Build logic is defined once and shared across all packages |
| **PyTorch Compatibility** | CUDA detection ensures extensions match PyTorch's CUDA configuration |
| **Flexibility** | Environment variables allow customization without code changes |
| **Dual Build Support** | Supports both setuptools extensions and external CMake builds |

The system handles the complexity of coordinating C++/CUDA compilation across multiple packages while exposing a simple interface for package developers.

**Sources:** [build_config/accvlab_build_config/__init__.py:15-18](), [README.md:105-110]()

---

