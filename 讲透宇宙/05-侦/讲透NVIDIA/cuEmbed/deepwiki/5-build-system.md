<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cuEmbed · page 5 Build System · fetched 2026-10-26 -->

# Build System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CMakeLists.txt](CMakeLists.txt)

</details>



The cuEmbed build system uses CMake to manage compilation, dependency resolution, and target generation across the core library, tests, benchmarks, and PyTorch integration. This system orchestrates the build process for CUDA C++ code and handles integration with third-party libraries.

For detailed CMake configuration options and target definitions, see [CMake Configuration](#5.1). For information about third-party dependency management, see [Dependencies](#5.2).

## Build System Architecture

The build system is structured around a root CMake configuration that conditionally includes subsystems based on build options. The system supports multiple CUDA architectures and integrates with both native C++ testing frameworks and PyTorch extension building.

```mermaid
graph TD
    CMakeLists["CMakeLists.txt<br/>Root Configuration"]
    
    subgraph "Core Targets"
        cuembed_hdrs["cuembed_hdrs<br/>Header-only Interface Library"]
    end
    
    subgraph "Conditional Subsystems"
        utils_cmake["utils/CMakeLists.txt<br/>Testing Utilities"]
        tests_cmake["tests/CMakeLists.txt<br/>Test Executables"] 
        benchmarks_cmake["benchmarks/CMakeLists.txt<br/>Benchmark Tools"]
        pytorch_cmake["examples/pytorch/CMakeLists.txt<br/>PyTorch Extension"]
    end
    
    subgraph "Third-party Dependencies"
        abseil["third_party/abseil-cpp<br/>Abseil C++ Library"]
        gtest["third_party/gtest<br/>Google Test Framework"]
    end
    
    subgraph "Build Options"
        BUILD_TESTS["BUILD_TESTS"]
        BUILD_BENCHMARKS["BUILD_BENCHMARKS"] 
        BUILD_EXAMPLES["BUILD_EXAMPLES"]
    end
    
    CMakeLists --> cuembed_hdrs
    CMakeLists --> BUILD_TESTS
    CMakeLists --> BUILD_BENCHMARKS
    CMakeLists --> BUILD_EXAMPLES
    
    BUILD_TESTS --> tests_cmake
    BUILD_TESTS --> utils_cmake
    BUILD_TESTS --> gtest
    BUILD_TESTS --> abseil
    
    BUILD_BENCHMARKS --> benchmarks_cmake
    BUILD_BENCHMARKS --> utils_cmake
    BUILD_BENCHMARKS --> abseil
    
    BUILD_EXAMPLES --> pytorch_cmake
```

Sources: [CMakeLists.txt:1-60]()

## Build Configuration Structure

The root CMake configuration establishes the project foundation with CUDA support and defines the primary interface library. The system uses C++17 standard and targets multiple CUDA compute capabilities.

| Configuration | Value | Purpose |
|---------------|-------|---------|
| `CMAKE_CXX_STANDARD` | 17 | C++ language standard |
| `CMAKE_CUDA_ARCHITECTURES` | 70 75 80 90 | Supported GPU architectures |
| `CMAKE_CUDA_FLAGS` | `--ptxas-options=-v` | Enable verbose PTX assembly |
| `ABSL_PROPAGATE_CXX_STD` | ON | Ensure Abseil uses same C++ standard |

The core `cuembed_hdrs` interface library provides header-only access to the cuEmbed functionality:

```mermaid
graph LR
    subgraph "Interface Library Structure"
        cuembed_hdrs["cuembed_hdrs<br/>INTERFACE Library"]
        source_dir["CUEMBED_PROJECT_SOURCE_DIR<br/>Include Directory"]
        alias["cuembed::hdrs<br/>Alias Target"]
    end
    
    subgraph "Consuming Targets"
        tests["Test Executables"]
        benchmarks["Benchmark Tools"]  
        pytorch_ext["PyTorch Extension"]
    end
    
    cuembed_hdrs --> source_dir
    cuembed_hdrs --> alias
    alias --> tests
    alias --> benchmarks
    alias --> pytorch_ext
```

Sources: [CMakeLists.txt:16-22](), [CMakeLists.txt:34-36]()

## Build Options and Targets

The build system provides three main configuration options that control which subsystems are included in the build:

| Option | Default | Controls | Dependencies |
|--------|---------|----------|-------------|
| `BUILD_TESTS` | ON | Test executables and validation | `gtest`, `abseil-cpp`, `utils` |
| `BUILD_BENCHMARKS` | ON | Performance measurement tools | `abseil-cpp`, `utils` |  
| `BUILD_EXAMPLES` | OFF | PyTorch integration examples | PyTorch libraries |

The conditional inclusion logic ensures dependencies are only built when needed:

```mermaid
graph TD
    subgraph "Dependency Resolution Logic"
        condition1{"BUILD_TESTS OR<br/>BUILD_BENCHMARKS"}
        condition2{"BUILD_TESTS"}
        condition3{"BUILD_BENCHMARKS"}
        condition4{"BUILD_EXAMPLES"}
        
        abseil_add["add_subdirectory<br/>third_party/abseil-cpp"]
        utils_add["add_subdirectory<br/>utils"]
        gtest_add["add_subdirectory<br/>third_party/gtest"]
        tests_add["add_subdirectory<br/>tests"]
        benchmarks_add["add_subdirectory<br/>benchmarks"]
        examples_add["add_subdirectory<br/>examples/pytorch"]
    end
    
    condition1 -->|true| abseil_add
    condition1 -->|true| utils_add
    condition2 -->|true| gtest_add
    condition2 -->|true| tests_add
    condition3 -->|true| benchmarks_add  
    condition4 -->|true| examples_add
```

Sources: [CMakeLists.txt:26-28](), [CMakeLists.txt:38-60]()

## CUDA Integration

The build system configures CUDA compilation with specific architecture targeting and compiler flags. The `enable_language(CUDA)` directive allows CMake to handle CUDA source files alongside C++ files.

Key CUDA configuration elements:
- **Architecture Support**: Targets compute capabilities 7.0, 7.5, 8.0, and 9.0 for broad GPU compatibility
- **PTX Verbosity**: Enables verbose PTX assembly output for debugging and optimization analysis
- **CUDAToolkit Integration**: Uses `find_package(CUDAToolkit)` for accessing CUDA runtime and driver APIs

Sources: [CMakeLists.txt:19-22](), [CMakeLists.txt:30]()

## Subsystem Integration

The build system serves as the integration point for all major cuEmbed components. Each subsystem maintains its own CMake configuration while relying on the root configuration for common settings and dependencies.

The modular design allows selective building of components based on development needs, whether focusing on core library development, performance analysis, or PyTorch integration work.

Sources: [CMakeLists.txt:1-60]()

---

