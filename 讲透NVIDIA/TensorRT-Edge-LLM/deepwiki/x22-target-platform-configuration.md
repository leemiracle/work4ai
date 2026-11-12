<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/TensorRT-Edge-LLM · extra page Target Platform Configuration · fetched 2026-10-26 -->

# Target Platform Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cmake/XQACubins.cmake](cmake/XQACubins.cmake)
- [cmake/aarch64_linux_toolchain.cmake](cmake/aarch64_linux_toolchain.cmake)

</details>



This page documents the `EMBEDDED_TARGET` CMake variable and its supported values for cross-compiling TensorRT-Edge-LLM to NVIDIA edge platforms. Each target option configures platform-specific settings including CUDA architecture, toolkit directories, and compiler flags.

For general cross-compilation setup instructions, see [Cross-Compilation for ARM64](#5.2). For CMake build variables and overall build configuration, see [CMake Configuration](#5.1).

---

## Overview

The `EMBEDDED_TARGET` variable controls platform-specific build configuration when using the aarch64 cross-compilation toolchain. It is specified when invoking CMake with the toolchain file:

```bash
cmake .. \
  -DCMAKE_TOOLCHAIN_FILE=cmake/aarch64_linux_toolchain.cmake \
  -DEMBEDDED_TARGET=jetson-thor \
  -DTRT_PACKAGE_DIR=/path/to/TensorRT
```

The toolchain file [cmake/aarch64_linux_toolchain.cmake:51-93]() reads this variable and configures:
- `CMAKE_CUDA_ARCHITECTURES`: GPU compute capability for code generation.
- `CUDA_CTK_VERSION`: Expected CUDA toolkit version (replaces `CUDA_VERSION` to avoid macro ambiguity).
- `CUDA_DIR`: Path to CUDA toolkit libraries and headers.
- `CUDA_TARGET_DIR`: Optional secondary CUDA directory for specific platform paths.

**Sources**: [cmake/aarch64_linux_toolchain.cmake:44-93]()

---

## Supported Target Platforms

The following table summarizes all supported `EMBEDDED_TARGET` values:

| Target Value | Platform | CUDA Arch (SM) | Default CUDA Version | CUDA Toolkit Path (`CUDA_DIR`) |
|--------------|----------|----------------|----------------------|-------------------|
| `auto-thor` | NVIDIA DRIVE Auto-Thor | 101a or 110a* | 13.3 | `/usr/local/cuda/targets/aarch64-linux` |
| `jetson-thor` | NVIDIA Jetson Thor | 110a | 13.0 | `/usr/local/cuda/targets/sbsa-linux` |
| `jetson-orin` | NVIDIA Jetson Orin | 87 | 12.6 | `/usr/local/cuda/targets/aarch64-linux` or `sbsa-linux`* |
| `gb10` | NVIDIA DRIVE GB10 | 121a | 13.0 | `/usr/local/cuda/targets/sbsa-linux` |

\* `auto-thor` selects architecture based on `CUDA_CTK_VERSION` [cmake/aarch64_linux_toolchain.cmake:53-57]().
\* `jetson-orin` switches to `sbsa-linux` if `CUDA_CTK_VERSION >= 13.0` [cmake/aarch64_linux_toolchain.cmake:74-82]().

**Sources**: [cmake/aarch64_linux_toolchain.cmake:51-93]()

---

## Target Selection Flow

The following diagram illustrates how the `EMBEDDED_TARGET` variable propagates through the CMake toolchain to define architecture and paths.

### Platform Configuration Logic
```mermaid
graph TD
    ["START"] --> ["CHECK_TARGET"]
    
    ["CHECK_TARGET"] -- "auto-thor" --> ["AUTO_THOR"]
    ["CHECK_TARGET"] -- "jetson-thor" --> ["JETSON_THOR"]
    ["CHECK_TARGET"] -- "jetson-orin" --> ["JETSON_ORIN"]
    ["CHECK_TARGET"] -- "gb10" --> ["GB10"]
    
    ["AUTO_THOR"] --> ["CHECK_CUDA_THOR"]
    ["CHECK_CUDA_THOR"] -- "Yes" --> ["SM101"]
    ["CHECK_CUDA_THOR"] -- "No" --> ["SM110_AUTO"]
    
    ["JETSON_THOR"] --> ["SM110_JETSON"]
    
    ["JETSON_ORIN"] --> ["CHECK_CUDA_ORIN"]
    ["CHECK_CUDA_ORIN"] -- "Yes" --> ["ORIN_SBSA"]
    ["CHECK_CUDA_ORIN"] -- "No" --> ["ORIN_AARCH64"]
    
    ["GB10"] --> ["SM121"]
    
    ["SM101"] --> ["DONE"]
    ["SM110_AUTO"] --> ["DONE"]
    ["SM110_JETSON"] --> ["DONE"]
    ["ORIN_SBSA"] --> ["DONE"]
    ["ORIN_AARCH64"] --> ["DONE"]
    ["SM121"] --> ["DONE"]

    style START stroke-dasharray: 5 5
    style DONE stroke-width:4px
```

**Sources**: [cmake/aarch64_linux_toolchain.cmake:51-93]()

---

## Platform-Specific Configuration

### auto-thor (NVIDIA DRIVE Auto-Thor)

The `auto-thor` target is designed for NVIDIA DRIVE automotive platforms and includes version-adaptive logic:

**Configuration Logic** [cmake/aarch64_linux_toolchain.cmake:51-64]():
- **CUDA Version**: Defaults to 13.3.
- **Architecture**: 
  - If `CUDA_CTK_VERSION < 13.0`: Sets `CMAKE_CUDA_ARCHITECTURES` to `101a`.
  - If `CUDA_CTK_VERSION >= 13.0`: Sets `CMAKE_CUDA_ARCHITECTURES` to `110a`.
- **Paths**: 
  - `CUDA_DIR`: `/usr/local/cuda/targets/aarch64-linux`
  - `CUDA_TARGET_DIR`: `/usr/local/cuda/thor/targets/aarch64-linux`

**Sources**: [cmake/aarch64_linux_toolchain.cmake:51-64]()

### jetson-thor (NVIDIA Jetson Thor)

The `jetson-thor` target configures for next-generation Jetson platforms with Thor GPU architecture:

**Configuration** [cmake/aarch64_linux_toolchain.cmake:65-70]():
- **Architecture**: Fixed `110a`.
- **CUDA Version**: Defaults to 13.0.
- **Paths**: Uses SBSA (Server Base System Architecture) path: `/usr/local/cuda/targets/sbsa-linux`.

**Sources**: [cmake/aarch64_linux_toolchain.cmake:65-70]()

### jetson-orin (NVIDIA Jetson Orin)

The `jetson-orin` target supports current-generation Jetson AGX Orin, Orin NX, and Orin Nano platforms:

**Configuration** [cmake/aarch64_linux_toolchain.cmake:71-82]():
- **Architecture**: `87` (Ampere).
- **CUDA Version**: Defaults to 12.6.
- **Paths**: 
  - If `CUDA_CTK_VERSION >= 13.0`: `/usr/local/cuda/targets/sbsa-linux`.
  - Otherwise: `/usr/local/cuda/targets/aarch64-linux`.

**Sources**: [cmake/aarch64_linux_toolchain.cmake:71-82]()

### gb10 (NVIDIA DRIVE GB10)

The `gb10` target configures for NVIDIA DRIVE GB10 automotive compute platform:

**Configuration** [cmake/aarch64_linux_toolchain.cmake:83-93]():
- **Architecture**: `121a`.
- **CUDA Version**: Defaults to 13.0.
- **Paths**: 
  - `CUDA_DIR`: `/usr/local/cuda/targets/sbsa-linux`
  - `CUDA_TARGET_DIR`: `/usr/local/cuda/n1/targets/sbsa-linux`

**Sources**: [cmake/aarch64_linux_toolchain.cmake:83-93]()

---

## Kernel Specialization: XQA Cubins

The `CMAKE_CUDA_ARCHITECTURES` variable defined by the `EMBEDDED_TARGET` directly influences the generation of XQA (eXpert Query Attention) cubins. The function `edgellm_xqa_cubins_setup` parses these architectures to determine which kernels to compile.

### XQA Cubin Data Flow
```mermaid
graph LR
    subgraph "Build Configuration"
        ["EMBEDDED_TARGET"] --> ["CMAKE_CUDA_ARCHITECTURES"]
    end
    
    subgraph "XQA Cubin Generation"
        ["CMAKE_CUDA_ARCHITECTURES"] --> ["_edgellm_xqa_get_required_sms"]
        ["_edgellm_xqa_get_required_sms"] --> ["gen_cubins.py"]
        ["gen_cubins.py"] --> ["*.cubin.cpp"]
    end
    
    subgraph "Final Artifacts"
        ["*.cubin.cpp"] --> ["generateXQACubins"]
    end
```

**Implementation Details**:
- `_edgellm_xqa_get_required_sms` maps CMake architecture strings (e.g., `110a`) to integer SM versions (e.g., `101` or `110`) for the generator script [cmake/XQACubins.cmake:22-60](). It handles special cases like mapping SM `110` to `101` when necessary [cmake/XQACubins.cmake:47-49]().
- The `edgellm_xqa_cubins_setup` function uses `Python3` to execute the generator script [cmake/XQACubins.cmake:62-89]().
- The `generateXQACubins` custom target invokes `kernelSrcs/xqa/gen_cubins.py` to produce specialized kernels for the target platform [cmake/XQACubins.cmake:102-113]().

**Sources**: [cmake/XQACubins.cmake:22-113](), [cmake/aarch64_linux_toolchain.cmake:51-93]()

---

## CUDA Architecture Mapping

The mapping between platform targets and CUDA compute capabilities is managed via `CMAKE_CUDA_ARCHITECTURES`.

### Target to SM Architecture Mapping
```mermaid
graph LR
    subgraph "Jetson Platforms"
        ["jetson-orin"]
        ["jetson-thor"]
    end
    
    subgraph "DRIVE Platforms"
        ["auto-thor"]
        ["gb10"]
    end
    
    subgraph "SM Architectures"
        ["87"]
        ["101a"]
        ["110a"]
        ["121a"]
    end
    
    ["jetson-orin"] --> ["87"]
    ["auto-thor"] -- "CUDA < 13.0" --> ["101a"]
    ["auto-thor"] -- "CUDA >= 13.0" --> ["110a"]
    ["jetson-thor"] --> ["110a"]
    ["gb10"] --> ["121a"]
```

**Sources**: [cmake/aarch64_linux_toolchain.cmake:51-93]()

---

## Implementation Details

### Variable Initialization
The build system uses a `set_ifndef` macro to provide default values while allowing user overrides via the command line.

```cmake
macro(set_ifndef var val)
  if(NOT DEFINED ${var})
    set(${var} ${val})
  endif()
  message(STATUS "Configurable variable ${var} set to ${${var}}")
endmacro()
```
[cmake/aarch64_linux_toolchain.cmake:37-42]()

### CUDA Version Safety
To prevent ambiguity with internal CUDA macros, the build system mandates the use of `CUDA_CTK_VERSION` instead of `CUDA_VERSION`.

```cmake
if(DEFINED CUDA_VERSION)
  message(FATAL_ERROR "CUDA_VERSION can cause ambiguity... Please use -DCUDA_CTK_VERSION")
endif()
```
[cmake/aarch64_linux_toolchain.cmake:44-49]()

### Cross-Compiler Configuration
The toolchain explicitly sets the `aarch64-linux-gnu` compilers and the CUDA host compiler:

- **C/C++ Compiler**: `/usr/bin/aarch64-linux-gnu-gcc` and `g++` [cmake/aarch64_linux_toolchain.cmake:21-22]().
- **CUDA Host Compiler**: Forced to match the CXX compiler [cmake/aarch64_linux_toolchain.cmake:28-31]().
- **Search Paths**: The toolchain restricts CMake search paths to the target environment (`ONLY`) for libraries and includes, but allows `NEVER` for programs to ensure host build tools are used [cmake/aarch64_linux_toolchain.cmake:96-98]().

**Sources**: [cmake/aarch64_linux_toolchain.cmake:17-34](), [cmake/aarch64_linux_toolchain.cmake:96-101]()

---

