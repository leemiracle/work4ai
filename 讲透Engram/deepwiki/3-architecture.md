> 来源: [https://deepwiki.com/deepseek-ai/Engram/3-architecture](https://deepwiki.com/deepseek-ai/Engram/3-architecture)
> DeepWiki deepseek-ai/Engram

# Architecture

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/README.md?plain=1)
 - [csrc/jit/compiler.hpp](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit/compiler.hpp)
 - [csrc/jit/device_runtime.hpp](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit/device_runtime.hpp)
 - [csrc/jit/handle.hpp](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit/handle.hpp)
 - [csrc/utils/system.hpp](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/utils/system.hpp)
 - [setup.py](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/setup.py)
 
  This document provides a technical overview of DeepGEMM's system architecture, focusing on the JIT compilation pipeline, device runtime management, kernel implementations, and data flow patterns. The architecture is designed to generate optimal CUDA kernels at runtime based on input parameters and GPU architecture.

 
## System Overview

 DeepGEMM employs a multi-layered architecture with clear separation between Python API, C++ compilation infrastructure, and CUDA kernel execution. The system's core design principle is JIT (Just-In-Time) compilation: kernels are generated and compiled on-demand based on runtime parameters, then cached for reuse.

 **System Architecture Diagram**

 
```

```

 Sources: [README.md3-7](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/README.md?plain=1#L3-L7) [csrc/python_api.cpp1-28](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/python_api.cpp#L1-L28) [csrc/jit/compiler.hpp23-62](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit/compiler.hpp#L23-L62) [csrc/jit/device_runtime.hpp14-29](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit/device_runtime.hpp#L14-L29)

 
## Core Architectural Components

 
### System Architecture Overview

 The system provides a unified interface for various deep learning primitives. It integrates external dependencies like `CUTLASS`, `CuTe`, and `{fmt}` while maintaining a lightweight core. The flow starts from Python calls, passes through `pybind11` bindings in `csrc/python_api.cpp`, and triggers the JIT compilation or execution of specialized CUDA kernels. For details, see [System Architecture Overview](https://deepwiki.com/deepseek-ai/DeepGEMM/3.1-system-architecture-overview).

 Sources: [README.md33-39](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/README.md?plain=1#L33-L39) [csrc/python_api.cpp17-28](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/python_api.cpp#L17-L28) [setup.py33-49](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/setup.py#L33-L49)

 
### JIT Compilation Pipeline

 The compilation infrastructure manages kernel generation and caching. It supports multiple backends including `NVCC` and `NVRTC`. The system is designed for low CPU overhead, utilizing a C++ JIT module initialized during package import. It handles atomic directory renames for thread-safe caching on distributed filesystems. For details, see [JIT Compilation Pipeline](https://deepwiki.com/deepseek-ai/DeepGEMM/3.2-jit-compilation-pipeline).

 **Compiler Logic Bridge**

 
```

```

 Sources: [csrc/jit/compiler.hpp100-149](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit/compiler.hpp#L100-L149) [csrc/jit/handle.hpp13-47](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit/handle.hpp#L13-L47) [csrc/jit/compiler.hpp70-98](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit/compiler.hpp#L70-L98)

 
### Mega MoE Architecture

 Mega MoE fuses and overlaps EP dispatch, dual linear layers (Linear1 and Linear2), SwiGLU activation, and EP combine into a single execution flow. It utilizes a symmetric memory layout to optimize multi-GPU communication and computation overlap. For details, see [Mega MoE Architecture](https://deepwiki.com/deepseek-ai/DeepGEMM/3.3-mega-moe-architecture).

 Sources: [README.md114-116](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/README.md?plain=1#L114-L116) [csrc/python_api.cpp27](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/python_api.cpp#L27-L27)

 
### Hardware Architecture Support

 DeepGEMM provides specialized support for NVIDIA SM90 (Hopper) and SM100 (Blackwell) architectures. The `DeviceRuntime` class detects architecture at runtime to dispatch appropriate kernels and configurations. It handles architecture-specific features like `TMA` and `TMEM`. For details, see [Hardware Architecture Support](https://deepwiki.com/deepseek-ai/DeepGEMM/3.4-hardware-architecture-support).

 Sources: [README.md29-35](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/README.md?plain=1#L29-L35) [csrc/jit/device_runtime.hpp83-97](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit/device_runtime.hpp#L83-L97) [csrc/jit/device_runtime.hpp72-81](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit/device_runtime.hpp#L72-L81)

 
### Memory and Data Layout

 The library handles complex memory hierarchies and alignment requirements. Key features include:

 
 - **TMA Alignment**: Ensuring tensors meet hardware-specific alignment for asynchronous copies.
 - **Scaling Factors**: SM90 requires FP32 SFs, while SM100 requires packed **UE8M0** format.
 - **Symmetric Memory**: A specialized layout for MoE to facilitate NVLink communication overlap. For details, see [Memory and Data Layout](https://deepwiki.com/deepseek-ai/DeepGEMM/3.5-memory-and-data-layout).
 
 Sources: [README.md67-72](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/README.md?plain=1#L67-L72) [csrc/jit/handle.hpp46](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit/handle.hpp#L46-L46)

 
### Heuristics and Auto-tuning

 A heuristic system selects optimal kernel configurations, such as block sizes and thread counts, based on the input matrix shapes and hardware specifications. This system can be influenced by environment variables like `DG_PRINT_CONFIGS` for debugging. For details, see [Heuristics and Auto-tuning](https://deepwiki.com/deepseek-ai/DeepGEMM/3.6-heuristics-and-auto-tuning).

 Sources: [csrc/jit/device_runtime.hpp103-123](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit/device_runtime.hpp#L103-L123) [csrc/jit/compiler.hpp58-62](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit/compiler.hpp#L58-L62)

 
### Work Scheduling and Distribution

 DeepGEMM employs advanced scheduling techniques, including persistent thread blocks and specialized schedulers, to maximize SM utilization and overlap communication with computation in MoE workloads. It supports features like Programmatic Stream Serialization (PDL). For details, see [Work Scheduling and Distribution](https://deepwiki.com/deepseek-ai/DeepGEMM/3.7-work-scheduling-and-distribution).

 Sources: [csrc/jit/device_runtime.hpp127-133](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit/device_runtime.hpp#L127-L133) [csrc/jit/handle.hpp101-106](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/jit/handle.hpp#L101-L106)
