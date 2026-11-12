<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cnmem · page 2 Getting Started · fetched 2026-10-26 -->

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CMakeLists.txt](CMakeLists.txt)
- [README.md](README.md)

</details>



This document provides an overview of how to set up and begin using the cnmem CUDA memory management library. It covers the prerequisites, basic setup workflow, and points you to detailed information for building and using the system.

For detailed build instructions including dependencies and platform-specific considerations, see [Building the Library](#2.1). For simple usage examples and common patterns, see [Quick Start Guide](#2.2). For complete function documentation, see [API Reference](#3).

## Prerequisites and Dependencies

Before building cnmem, you need the following components installed on your system:

| Component | Requirement | Purpose |
|-----------|-------------|---------|
| CUDA Toolkit | >= 7.0 recommended | Core CUDA runtime and development libraries |
| CMake | >= 2.8.8 | Build system configuration |
| C++ Compiler | C++11 support | Source compilation |
| Google Test | Optional | Unit test framework (only if building tests) |
| Threading Library | pthread (Linux) / Win32 (Windows) | Thread synchronization |

The cnmem library integrates directly with CUDA's memory management functions and requires proper CUDA environment setup including `CUDA_HOME` and library path configuration.

**Sources:** [README.md:11-25](), [CMakeLists.txt:5-6]()

## System Overview

CNMeM Overview: Core Components and Dependencies

```mermaid
graph TB
    subgraph "User Application"
        APP["Deep Learning Framework"]
    end
    
    subgraph "CNMeM Library"
        API["cnmem.h<br/>Public API Interface"]
        IMPL["cnmem.cpp<br/>Core Implementation"]
    end
    
    subgraph "Build System"
        CMAKE["CMakeLists.txt<br/>Build Configuration"]
        SHARED["libcnmem.so/dll/dylib<br/>Shared Library"]
    end
    
    subgraph "Testing Framework"
        UNIT_TEST["cnmem_tests<br/>Unit Test Executable"]
        KERNEL_TEST["cnmem_kernel_tests<br/>CUDA Kernel Tests"]
    end
    
    subgraph "External Dependencies"
        CUDA["CUDA Toolkit<br/>cudaMalloc/cudaFree"]
        GTEST["Google Test<br/>Testing Framework"]
    end
    
    APP --> API
    API --> IMPL
    CMAKE --> SHARED
    IMPL --> SHARED
    API --> SHARED
    
    CMAKE --> UNIT_TEST
    CMAKE --> KERNEL_TEST
    UNIT_TEST --> GTEST
    KERNEL_TEST --> GTEST
    
    IMPL --> CUDA
    UNIT_TEST --> SHARED
    KERNEL_TEST --> SHARED
```

**Sources:** [CMakeLists.txt:10-16](), [README.md:1-6]()

## Basic Setup Workflow

The process of setting up cnmem follows these key phases:

CNMeM Setup and Integration Workflow

```mermaid
sequenceDiagram
    participant DEV as "Developer"
    participant BUILD as "Build System"  
    participant LIB as "cnmem Library"
    participant APP as "Application"
    participant CUDA as "CUDA Runtime"
    
    Note over DEV,CUDA: Setup Phase
    DEV->>BUILD: "cmake .."
    BUILD->>BUILD: "find_package(CUDA REQUIRED)"
    BUILD->>BUILD: "include_directories(include)"
    BUILD->>LIB: "add_library(cnmem SHARED src/cnmem.cpp)"
    BUILD-->>DEV: "libcnmem.so created"
    
    Note over DEV,CUDA: Integration Phase
    DEV->>APP: "Include cnmem.h"
    DEV->>APP: "Link with libcnmem"
    APP->>LIB: "cnmemInit()"
    LIB->>CUDA: "Initialize device managers"
    CUDA-->>LIB: "Memory pools allocated"
    LIB-->>APP: "CNMEM_STATUS_SUCCESS"
    
    Note over DEV,CUDA: Usage Phase
    APP->>LIB: "cnmemMalloc(&ptr, size, stream)"
    LIB->>LIB: "Route to appropriate manager"
    LIB-->>APP: "Memory pointer returned"
    
    Note over DEV,CUDA: Cleanup Phase
    APP->>LIB: "cnmemFree(ptr, stream)"
    APP->>LIB: "cnmemFinalize()"
    LIB->>CUDA: "Release all pools"
```

**Sources:** [CMakeLists.txt:9-16](), [README.md:33-49]()

## Build Configuration Options

The cnmem build system provides several configuration options controlled through CMake flags:

| CMake Option | Effect | Files Generated |
|--------------|--------|-----------------|
| Default build | Library only | `libcnmem.so/dll/dylib` |
| `-DWITH_TESTS=True` | Library + tests | Library + `cnmem_tests` + `cnmem_kernel_tests` |
| `-DCMAKE_BUILD_TYPE=Debug` | Debug symbols | Debug builds with symbols |
| `-DCMAKE_INSTALL_PREFIX=path` | Install location | Custom installation directory |

The build system automatically detects:
- CUDA installation via `find_package(CUDA QUIET REQUIRED)` 
- Google Test framework via `find_package(GTest QUIET REQUIRED)` (when tests enabled)
- C++11 compiler support for modern standard library features

**Sources:** [CMakeLists.txt:19-49](), [CMakeLists.txt:27-34]()

## Library Integration Points

Applications integrate with cnmem through several key interfaces:

CNMeM Integration Architecture

```mermaid
graph TD
    subgraph "Application Layer"
        DL_FW["Deep Learning Framework<br/>(TensorFlow, PyTorch)"]
        CUSTOM["Custom CUDA Application"]
    end
    
    subgraph "CNMeM Public Interface"
        INIT_API["cnmemInit()<br/>cnmemFinalize()"]
        MEM_API["cnmemMalloc()<br/>cnmemFree()"]
        INFO_API["cnmemMemGetInfo()<br/>cnmemPrintMemoryState()"]
        STREAM_API["cnmemRegisterStream()"]
    end
    
    subgraph "CNMeM Implementation"
        MANAGER["Manager Classes<br/>Device & Stream Managers"]
        CONTEXT["Context Class<br/>Global State Management"]
        BLOCK["Block Class<br/>Memory Block Tracking"]
    end
    
    subgraph "CUDA Runtime Layer"
        CUDA_MEM["cudaMalloc()<br/>cudaFree()"]
        CUDA_STREAM["cudaStream_t"]
        CUDA_CTX["CUDA Context Management"]
    end
    
    DL_FW --> INIT_API
    DL_FW --> MEM_API
    DL_FW --> STREAM_API
    CUSTOM --> MEM_API
    CUSTOM --> INFO_API
    
    INIT_API --> MANAGER
    MEM_API --> MANAGER
    INFO_API --> CONTEXT
    STREAM_API --> MANAGER
    
    MANAGER --> BLOCK
    MANAGER --> CONTEXT
    
    MANAGER --> CUDA_MEM
    MANAGER --> CUDA_STREAM
    CONTEXT --> CUDA_CTX
```

**Sources:** [CMakeLists.txt:10-16](), [README.md:51-56]()

## Next Steps

After understanding this overview, proceed with:

1. **Building the Library**: Follow the detailed build instructions in [Building the Library](#2.1) to compile cnmem for your platform
2. **Basic Usage**: Review the [Quick Start Guide](#2.2) for simple examples of initialization, allocation, and cleanup
3. **API Details**: Consult the [API Reference](#3) for complete function documentation and parameter details
4. **Advanced Features**: Explore [Architecture and Implementation](#4) to understand the hierarchical memory management system

The cnmem library is designed specifically for applications that work with large memory buffers and predictable allocation patterns, making it particularly suitable for deep learning frameworks and GPU computing applications.

**Sources:** [README.md:3-9](), [CMakeLists.txt:1-16]()

---

