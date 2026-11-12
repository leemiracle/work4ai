<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/otk-pyoptix · page 1 PyOptiX Overview · fetched 2026-10-26 -->

# PyOptiX Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [optix/main.cpp](optix/main.cpp)
- [optix/setup.py](optix/setup.py)

</details>



## Purpose and Scope

This document provides a high-level overview of PyOptiX, explaining its architecture, core components, and relationship to the NVIDIA OptiX ray tracing API. It covers the overall system design and the binding layer that enables Python applications to use OptiX functionality.

For detailed installation instructions, see [Installation and Dependencies](#2.1). For hands-on usage examples, see [Your First Ray Tracing Application](#2.2). For comprehensive API documentation, see [Core API Reference](#3).

## What is PyOptiX

PyOptiX is a Python binding library that provides Python access to NVIDIA's OptiX 7 ray tracing API. It enables Python developers to build high-performance ray tracing applications by wrapping the OptiX C API with Python-friendly interfaces using pybind11.

**Key characteristics:**
- **Python bindings for OptiX 7.6+**: Wraps the complete OptiX C API for Python use
- **pybind11-based implementation**: Uses modern C++ binding techniques for seamless Python integration  
- **Complete API coverage**: Supports device contexts, modules, pipelines, acceleration structures, and denoising
- **Cross-platform support**: Works on Linux and Windows with appropriate OptiX and CUDA installations

**Sources:** [README.md:1-96](), [optix/main.cpp:1-50]()

## System Architecture

PyOptiX follows a layered architecture that bridges Python applications with the OptiX C API through C++ bindings:

```mermaid
graph TB
    subgraph "Python Application Layer"
        UserApp["User Python Applications"]
        Examples["PyOptiX Examples<br/>hello.py, triangle.py, curves.py"]  
        Tests["Test Suite<br/>pytest-based validation"]
    end
    
    subgraph "PyOptiX Python API Layer"
        DeviceContextPy["optix.DeviceContext"]
        ModulePy["optix.Module"]
        PipelinePy["optix.Pipeline"] 
        ProgramGroupPy["optix.ProgramGroup"]
        DenoiserPy["optix.Denoiser"]
        UtilFuncs["optix.launch()<br/>optix.version()<br/>optix.sbtRecordPackHeader()"]
    end
    
    subgraph "C++ Binding Layer (main.cpp)"
        Wrappers["pyoptix::DeviceContext<br/>pyoptix::Module<br/>pyoptix::Pipeline<br/>pyoptix::ProgramGroup<br/>pyoptix::Denoiser"]
        ErrorHandling["PYOPTIX_CHECK Macros<br/>Exception Translation"]
        Helpers["convertBuildInputs()<br/>context_log_cb()"]
    end
    
    subgraph "OptiX C API"
        OptixCore["optixDeviceContextCreate<br/>optixModuleCreate<br/>optixPipelineCreate<br/>optixLaunch<br/>optixAccelBuild"]
    end
    
    subgraph "External Dependencies"
        CUDARuntime["CUDA Runtime API"]
        OptiXSDK["OptiX SDK 7.6+"]
    end
    
    UserApp --> DeviceContextPy
    UserApp --> ModulePy
    UserApp --> PipelinePy
    UserApp --> UtilFuncs
    
    Examples --> DeviceContextPy
    Examples --> ModulePy  
    Examples --> UtilFuncs
    
    Tests --> DeviceContextPy
    Tests --> ModulePy
    
    DeviceContextPy --> Wrappers
    ModulePy --> Wrappers
    PipelinePy --> Wrappers
    ProgramGroupPy --> Wrappers
    DenoiserPy --> Wrappers
    UtilFuncs --> Wrappers
    
    Wrappers --> ErrorHandling
    Wrappers --> Helpers
    ErrorHandling --> OptixCore
    Helpers --> OptixCore
    
    OptixCore --> OptiXSDK
    OptixCore --> CUDARuntime
```

**Sources:** [optix/main.cpp:85-137](), [optix/main.cpp:1070-1096](), [README.md:20-27]()

## Python API to C++ Binding Mapping

The binding layer translates Python calls into OptiX C API calls through C++ wrapper objects:

```mermaid
graph LR
    subgraph "Python Space"
        PyDeviceContext["optix.DeviceContext"]
        PyModule["optix.Module"] 
        PyPipeline["optix.Pipeline"]
        PyLaunch["optix.launch()"]
        PyVersion["optix.version()"]
    end
    
    subgraph "C++ Binding Functions (main.cpp)"
        DeviceContextCreate["deviceContextCreate()"]
        ModuleCreate["moduleCreate()"]
        PipelineCreate["pipelineCreate()"]
        Launch["launch()"]  
        Version["version()"]
    end
    
    subgraph "C++ Wrapper Structs"
        StructDeviceContext["pyoptix::DeviceContext<br/>OptixDeviceContext deviceContext"]
        StructModule["pyoptix::Module<br/>OptixModule module"]
        StructPipeline["pyoptix::Pipeline<br/>OptixPipeline pipeline"]
    end
    
    subgraph "OptiX C API Calls"
        OptixDeviceContextCreate["optixDeviceContextCreate()"]
        OptixModuleCreate["optixModuleCreate()"]
        OptixPipelineCreate["optixPipelineCreate()"] 
        OptixLaunch["optixLaunch()"]
    end
    
    PyDeviceContext --> DeviceContextCreate
    PyModule --> ModuleCreate
    PyPipeline --> PipelineCreate
    PyLaunch --> Launch
    PyVersion --> Version
    
    DeviceContextCreate --> StructDeviceContext
    ModuleCreate --> StructModule
    PipelineCreate --> StructPipeline
    
    StructDeviceContext --> OptixDeviceContextCreate
    StructModule --> OptixModuleCreate  
    StructPipeline --> OptixPipelineCreate
    Launch --> OptixLaunch
```

**Sources:** [optix/main.cpp:1098-1114](), [optix/main.cpp:1348-1391](), [optix/main.cpp:1280-1315](), [optix/main.cpp:1555-1578]()

## Core Components

PyOptiX provides Python wrappers for the primary OptiX objects and operations:

| Python Class/Function | C++ Wrapper Struct | OptiX C API | Purpose |
|----------------------|-------------------|-------------|---------|
| `optix.DeviceContext` | `pyoptix::DeviceContext` | `OptixDeviceContext` | GPU context and configuration management |
| `optix.Module` | `pyoptix::Module` | `OptixModule` | Compiled PTX shader module container |
| `optix.ProgramGroup` | `pyoptix::ProgramGroup` | `OptixProgramGroup` | Collection of related shader programs |
| `optix.Pipeline` | `pyoptix::Pipeline` | `OptixPipeline` | Complete ray tracing pipeline |
| `optix.Denoiser` | `pyoptix::Denoiser` | `OptixDenoiser` | AI-based image denoising |
| `optix.launch()` | `launch()` function | `optixLaunch()` | Ray tracing execution |

**Error handling** is managed through `PYOPTIX_CHECK` macros that translate OptiX errors into Python exceptions, providing consistent error reporting across the binding layer.

**Sources:** [optix/main.cpp:105-136](), [optix/main.cpp:28-45]()

## Ray Tracing Pipeline Flow

PyOptiX applications follow the standard OptiX pipeline pattern:

```mermaid
flowchart TD
    DeviceSetup["Device Context Setup<br/>optix.DeviceContext"] 
    PTXCompile["PTX Compilation<br/>nvrtc or external"]
    ModuleCreate["Module Creation<br/>optix.Module"]
    ProgramGroups["Program Group Creation<br/>optix.ProgramGroup"]
    PipelineLink["Pipeline Linking<br/>optix.Pipeline"]
    AccelBuild["Acceleration Structure<br/>optix.accelBuild()"]
    SBTSetup["Shader Binding Table<br/>optix.sbtRecordPackHeader()"]
    Launch["Ray Tracing Launch<br/>optix.launch()"]
    
    DeviceSetup --> PTXCompile
    PTXCompile --> ModuleCreate
    ModuleCreate --> ProgramGroups
    ProgramGroups --> PipelineLink
    DeviceSetup --> AccelBuild
    PipelineLink --> SBTSetup
    AccelBuild --> SBTSetup
    SBTSetup --> Launch
```

This pipeline enables GPU-accelerated ray tracing with OptiX's dedicated RT cores for optimal performance.

**Sources:** [optix/main.cpp:1348-1391](), [optix/main.cpp:1450-1542](), [optix/main.cpp:1640-1688](), [optix/main.cpp:1555-1578]()

## Build System Integration

PyOptiX uses a CMake-based build system integrated with Python's setuptools:

- **CMake backend**: [optix/setup.py:16-88]() provides `CMakeExtension` and `CMakeBuild` classes
- **Environment configuration**: `PYOPTIX_CMAKE_ARGS` environment variable specifies OptiX SDK location  
- **Cross-platform support**: Handles Windows and Linux build differences
- **Dependency management**: Links against OptiX SDK, CUDA runtime, and pybind11

**Sources:** [optix/setup.py:38-75](), [README.md:57-78]()

## Integration Points

PyOptiX integrates with several related systems and tools:

- **CUDA ecosystem**: Uses CuPy arrays for GPU memory management and NVRTC for runtime PTX compilation
- **OptiX examples**: Demonstrates usage patterns for geometry rendering, motion blur, and denoising  
- **Testing framework**: Pytest-based validation ensures API correctness across OptiX versions

For detailed component documentation, see [Core API Reference](#3). For practical usage examples, see [Examples and Tutorials](#4). For build system details, see [Build System and Development](#6).

**Sources:** [README.md:20-27](), [optix/main.cpp:51-82]()

---

