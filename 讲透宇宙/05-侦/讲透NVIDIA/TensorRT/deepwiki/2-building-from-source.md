<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/TensorRT · page 2 Building From Source · fetched 2026-10-26 -->

# Building From Source

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CMakeLists.txt](CMakeLists.txt)
- [README.md](README.md)
- [VERSION](VERSION)
- [cmake/toolchains/cmake_qnx_safe.toolchain](cmake/toolchains/cmake_qnx_safe.toolchain)
- [docker/build.sh](docker/build.sh)
- [docker/launch.sh](docker/launch.sh)
- [docker/ubuntu-cross-aarch64.Dockerfile](docker/ubuntu-cross-aarch64.Dockerfile)
- [include/NvInferVersion.h](include/NvInferVersion.h)
- [samples/common/sampleEngines.cpp](samples/common/sampleEngines.cpp)
- [samples/common/sampleInference.cpp](samples/common/sampleInference.cpp)
- [samples/common/sampleInference.h](samples/common/sampleInference.h)
- [samples/common/sampleOptions.cpp](samples/common/sampleOptions.cpp)
- [samples/common/sampleOptions.h](samples/common/sampleOptions.h)
- [samples/common/sampleReporting.cpp](samples/common/sampleReporting.cpp)
- [samples/trtexec/trtexec.cpp](samples/trtexec/trtexec.cpp)

</details>



This document provides comprehensive guidance for building TensorRT Open Source Software (OSS) components from source code. It covers the CMake-based build system, Docker containerization for reproducible builds, dependency management, and cross-compilation support for multiple platforms and architectures.

For information about the overall repository structure and components, see [TensorRT Overview](#1). For details about the plugin system that gets built as part of this process, see [Plugin System](#4).

## Build System Overview

TensorRT OSS uses a CMake-based build system that supports multiple platforms, architectures, and build configurations. The system is designed to build plugins, parsers, and sample applications while linking against the TensorRT GA (General Availability) libraries.

### Build System Architecture

```mermaid
graph TB
    subgraph "Version Management"
        VERSION_FILE["VERSION file"]
        NVINFER_VERSION_H["NvInferVersion.h"]
    end
    
    subgraph "CMake Configuration"
        ROOT_CMAKE["CMakeLists.txt"]
        CMAKE_MODULES["cmake/modules/"]
        TOOLCHAINS["cmake/toolchains/"]
    end
    
    subgraph "Build Targets"
        PLUGINS["plugin/ (BUILD_PLUGINS)"]
        PARSERS["parsers/ (BUILD_PARSERS)"] 
        SAMPLES["samples/ (BUILD_SAMPLES)"]
    end
    
    subgraph "Dependencies"
        TRT_GA["TensorRT GA Libraries"]
        CUDA_DEPS["CUDA/cuDNN"]
        PROTOBUF["Protobuf (third_party)"]
    end
    
    subgraph "Output Artifacts"
        PLUGIN_LIB["libnvinfer_plugin.so"]
        PARSER_LIB["libnvonnxparser.so"] 
        SAMPLE_BINS["Sample Executables"]
    end
    
    VERSION_FILE --> NVINFER_VERSION_H
    NVINFER_VERSION_H --> ROOT_CMAKE
    ROOT_CMAKE --> CMAKE_MODULES
    ROOT_CMAKE --> TOOLCHAINS
    
    ROOT_CMAKE --> PLUGINS
    ROOT_CMAKE --> PARSERS
    ROOT_CMAKE --> SAMPLES
    
    TRT_GA --> ROOT_CMAKE
    CUDA_DEPS --> ROOT_CMAKE
    PROTOBUF --> ROOT_CMAKE
    
    PLUGINS --> PLUGIN_LIB
    PARSERS --> PARSER_LIB
    SAMPLES --> SAMPLE_BINS
```

Sources: [CMakeLists.txt:1-239](), [include/NvInferVersion.h:1-45](), [VERSION:1-2]()

## Prerequisites and Dependencies

The build system requires several categories of dependencies that must be satisfied before compilation can begin.

### Required Dependencies

| Component | Version | Purpose |
|-----------|---------|---------|
| TensorRT GA | 10.13.3.9 | Core runtime libraries |
| CUDA | 13.0.0 or 12.9.0 | GPU computation framework |
| CMake | >= 3.31 | Build system generator |
| Python | 3.10-3.13.x | Build scripting and samples |
| GCC/Clang | Compatible | C++ compilation |

### CMake Build Variables

The build system uses several key CMake variables for configuration:

| Variable | Default | Description |
|----------|---------|-------------|
| `TRT_LIB_DIR` | `CMAKE_BINARY_DIR` | Path to TensorRT GA libraries |
| `TRT_OUT_DIR` | `CMAKE_BINARY_DIR` | Output directory for build artifacts |
| `BUILD_PLUGINS` | `ON` | Build TensorRT plugin library |
| `BUILD_PARSERS` | `ON` | Build ONNX parser library |
| `BUILD_SAMPLES` | `ON` | Build sample applications |
| `GPU_ARCHS` | Auto-detected | Target GPU architectures |

Sources: [README.md:29-72](), [CMakeLists.txt:205-219]()

## Docker Build Environments

TensorRT OSS provides Docker-based build environments for reproducible cross-platform builds. The Docker system supports multiple Linux distributions and cross-compilation targets.

### Docker Build System Architecture

```mermaid
graph TB
    subgraph "Build Scripts"
        BUILD_SH["docker/build.sh"]
        LAUNCH_SH["docker/launch.sh"]
    end
    
    subgraph "Dockerfile Variants"
        UBUNTU_22["ubuntu-22.04.Dockerfile"]
        UBUNTU_24["ubuntu-24.04-aarch64.Dockerfile"]
        UBUNTU_CROSS["ubuntu-cross-aarch64.Dockerfile"]
        ROCKY_8["rockylinux8.Dockerfile"]
    end
    
    subgraph "Container Features"
        CUDA_TOOLKIT["CUDA Toolkit Installation"]
        TENSORRT_PREINSTALL["Pre-installed TensorRT Libraries"]
        CROSS_TOOLS["Cross-compilation Toolchains"]
        BUILD_DEPS["Build Dependencies"]
    end
    
    subgraph "Build Targets"
        X86_64_NATIVE["x86_64 Native Build"]
        AARCH64_CROSS["aarch64 Cross-compile"]
        JETSON_TARGET["Jetson Platform Build"]
    end
    
    BUILD_SH --> UBUNTU_22
    BUILD_SH --> UBUNTU_CROSS
    BUILD_SH --> ROCKY_8
    
    LAUNCH_SH --> X86_64_NATIVE
    LAUNCH_SH --> AARCH64_CROSS
    
    UBUNTU_CROSS --> CROSS_TOOLS
    UBUNTU_22 --> CUDA_TOOLKIT
    UBUNTU_CROSS --> TENSORRT_PREINSTALL
    
    CROSS_TOOLS --> JETSON_TARGET
    CUDA_TOOLKIT --> X86_64_NATIVE
```

### Container Build Process

The Docker build system uses two main scripts:

1. **`docker/build.sh`** - Builds Docker images with specified configurations
2. **`docker/launch.sh`** - Launches containers with proper GPU access and volume mounts

Example container generation:
```bash
./docker/build.sh --file docker/ubuntu-22.04.Dockerfile --tag tensorrt-ubuntu22.04-cuda13.0
./docker/launch.sh --tag tensorrt-ubuntu22.04-cuda13.0 --gpus all
```

Sources: [docker/build.sh:1-51](), [docker/launch.sh:1-59](), [docker/ubuntu-cross-aarch64.Dockerfile:1-101]()

## CMake Configuration and Build Options

The root `CMakeLists.txt` implements a sophisticated build configuration system that handles version management, dependency resolution, and target architecture selection.

### Version Management System

The build system extracts version information from header files and integrates it into CMake variables:

```mermaid
graph LR
    VERSION_FILE["VERSION file<br/>10.13.3.9"] --> NVINFER_VERSION["NvInferVersion.h<br/>TRT_MAJOR_ENTERPRISE<br/>TRT_MINOR_ENTERPRISE<br/>TRT_PATCH_ENTERPRISE<br/>TRT_BUILD_ENTERPRISE"]
    
    NVINFER_VERSION --> CMAKE_PARSING["CMake String Parsing<br/>file(STRINGS)<br/>foreach(TYPE MAJOR MINOR...)"]
    
    CMAKE_PARSING --> CMAKE_VARS["CMake Variables<br/>TRT_VERSION<br/>TRT_SOVERSION<br/>ONNX2TRT_VERSION"]
```

The version extraction is implemented in [CMakeLists.txt:51-61]():
- Reads `#define TRT_.*_ENTERPRISE` patterns from `NvInferVersion.h`
- Extracts numeric values using regex matching
- Sets `TRT_VERSION` and `TRT_SOVERSION` variables

### GPU Architecture Selection

The build system supports flexible GPU architecture targeting through the `GPU_ARCHS` variable:

```mermaid
graph TB
    GPU_ARCHS_CHECK{"GPU_ARCHS<br/>defined?"}
    
    GPU_ARCHS_CHECK -->|Yes| USER_DEFINED["User-specified Architectures<br/>separate_arguments(GPU_ARCHS)<br/>foreach(SM IN LISTS GPU_ARCHS)"]
    
    GPU_ARCHS_CHECK -->|No| AUTO_DETECT["Auto-detect Architectures<br/>75 80 86 87 89 90<br/>+100 120 if CUDA >= 12.8"]
    
    USER_DEFINED --> GENCODE_GEN["Generate CUDA Gencodes<br/>-gencode arch=compute_XX,code=sm_XX"]
    AUTO_DETECT --> GENCODE_GEN
    
    GENCODE_GEN --> BERT_FILTER["BERT-specific Filter<br/>if arch >= 75<br/>BERT_GENCODES"]
```

Sources: [CMakeLists.txt:71-100]()

## Build Process

### Standard Build Workflow

The typical build process follows these steps:

1. **Environment Setup**
```bash
export TRT_LIBPATH=/path/to/tensorrt/lib
cd TensorRT
mkdir -p build && cd build
```

2. **CMake Configuration**
```bash
cmake .. -DTRT_LIB_DIR=$TRT_LIBPATH -DTRT_OUT_DIR=`pwd`/out
```

3. **Compilation**
```bash
make -j$(nproc)
```

### Build Targets and Dependencies

```mermaid
graph TB
    subgraph "External Dependencies"
        TRT_GA["TensorRT GA<br/>nvinfer<br/>find_library_create_target"]
        CUDART["CUDA Runtime<br/>cudart_static<br/>cugfx_dll"]
        PROTOBUF_EXT["Protobuf<br/>third_party/protobuf.cmake<br/>configure_protobuf"]
    end
    
    subgraph "Build Conditionals"
        BUILD_PLUGINS_OPT["BUILD_PLUGINS"]
        BUILD_PARSERS_OPT["BUILD_PARSERS"] 
        BUILD_SAMPLES_OPT["BUILD_SAMPLES"]
    end
    
    subgraph "Subdirectory Targets"
        PLUGIN_SUBDIR["add_subdirectory(plugin)"]
        PARSER_SUBDIR["add_subdirectory(parsers)"]
        SAMPLE_SUBDIR["add_subdirectory(samples)"]
    end
    
    BUILD_PLUGINS_OPT -->|ON| PLUGIN_SUBDIR
    BUILD_PARSERS_OPT -->|ON| PARSER_SUBDIR
    BUILD_SAMPLES_OPT -->|ON| SAMPLE_SUBDIR
    
    BUILD_PARSERS_OPT --> PROTOBUF_EXT
    TRT_GA --> PLUGIN_SUBDIR
    TRT_GA --> SAMPLE_SUBDIR
    CUDART --> PLUGIN_SUBDIR
```

Sources: [CMakeLists.txt:224-238](), [CMakeLists.txt:159-178]()

## Cross-Compilation Support

### Jetson and aarch64 Builds

The build system supports cross-compilation for ARM-based platforms through CMake toolchain files:

| Platform | Toolchain File | Build Command |
|----------|---------------|---------------|
| aarch64 native | `cmake_aarch64-native.toolchain` | Standard cmake with toolchain |
| aarch64 cross-compile | `cmake_aarch64_cross.toolchain` | Cross-compilation from x86_64 |
| Jetson Thor | Native build | `TRT_PLATFORM_ID=aarch64 GPU_ARCHS=110` |

### Cross-compilation Docker Environment

The `ubuntu-cross-aarch64.Dockerfile` provides a complete cross-compilation environment:

- **Base Image**: `nvidia/cuda:13.0.0-devel-ubuntu24.04`
- **Cross-compile Toolchain**: `g++-aarch64-linux-gnu`
- **CUDA Cross Tools**: `cuda-cross-sbsa-13-0`
- **Pre-installed TensorRT**: aarch64 libraries in `/usr/lib/aarch64-linux-gnu`

Example cross-compilation build:
```bash
cmake .. -DTRT_LIB_DIR=$TRT_LIBPATH \
         -DCMAKE_TOOLCHAIN_FILE=$TRT_OSSPATH/cmake/toolchains/cmake_aarch64_cross.toolchain \
         -DGPU_ARCHS=110
```

Sources: [docker/ubuntu-cross-aarch64.Dockerfile:78-100](), [README.md:184-191]()

## Build System Integration

### Library Name Resolution

The build system handles platform-specific library naming conventions through conditional logic:

```mermaid
graph TB
    PLATFORM_CHECK{"Platform<br/>MSVC?"}
    
    PLATFORM_CHECK -->|Windows| WIN_NAMES["Windows Library Names<br/>nvinfer_${TRT_SOVERSION}<br/>nvinfer_plugin_${TRT_SOVERSION}<br/>nvonnxparser_${TRT_SOVERSION}"]
    
    PLATFORM_CHECK -->|Linux| LINUX_NAMES["Linux Library Names<br/>nvinfer<br/>nvinfer_plugin<br/>nvonnxparser"]
    
    WIN_NAMES --> FIND_LIB["find_library_create_target<br/>Creates CMake targets"]
    LINUX_NAMES --> FIND_LIB
```

The `find_library_create_target` function from [cmake/modules/find_library_create_target.cmake]() creates CMake targets for TensorRT libraries, searching in `TRT_LIB_DIR` and system paths.

Sources: [CMakeLists.txt:180-198](), [CMakeLists.txt:22-33]()

---

