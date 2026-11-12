> 来源: [https://deepwiki.com/mozilla-ai/llamafile/4-compute-backends](https://deepwiki.com/mozilla-ai/llamafile/4-compute-backends)
> DeepWiki mozilla-ai/llamafile | Last indexed: 29 August 2026 (435512

# Compute Backends

  Relevant source files 
 - [llamafile/cuda.c](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/cuda.c)
 - [llamafile/gpu_backend.c](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/gpu_backend.c)
 - [llamafile/gpu_backend.h](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/gpu_backend.h)
 - [llamafile/llamafile.c](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.c)
 - [llamafile/llamafile.h](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.h)
 - [llamafile/metal.c](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/metal.c)
 - [llamafile/vulkan.c](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/vulkan.c)
 - [tests/gpu_backend_test.cpp](https://github.com/mozilla-ai/llamafile/blob/43551265/tests/gpu_backend_test.cpp)
 
  
## Purpose and Scope

 This document describes llamafile's compute backend system, which provides CPU and GPU acceleration for matrix multiplication and tensor operations. The system uses runtime detection to select optimal implementations based on available hardware capabilities, supporting x86_64 (AVX, AVX2, AVX512, Zen4) and ARM (NEON, DOTPROD, FP16) architectures on CPU, and CUDA, ROCm, Vulkan, and Metal on GPU.

 The system is designed for high portability and performance, utilizing a dynamic dispatch mechanism that allows a single "Actually Portable Executable" (APE) to run with hardware acceleration across diverse operating systems and processor generations.

 For detailed technical specifications, see the following child pages:

 
 - [Backend Architecture](https://deepwiki.com/mozilla-ai/llamafile/4.1-backend-architecture) — Function pointers, dynamic loading, crash guards, and the `GpuBackend` abstraction layer.
 - [CPU Backend](https://deepwiki.com/mozilla-ai/llamafile/4.2-cpu-backend) — SIMD feature discovery, the `GemmFuncs` dispatcher, and the TinyBLAS kernel implementation.
 - [GPU Backends](https://deepwiki.com/mozilla-ai/llamafile/4.3-gpu-backends) — CUDA, ROCm, Vulkan, and Metal integration with runtime DSO loading and out-of-process probing.
 
 
---

 
## Backend Selection Architecture

 The compute backend system uses a multi-tier selection hierarchy: GPU backend selection (governed by `FLAG_gpu` [llamafile/llamafile.h39](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.h#L39-L39)), safety probing (including out-of-process checks), and runtime CPU kernel dispatch based on SIMD features.

 
### Backend Selection Flow

 
```

```

 **Sources:** [llamafile/vulkan.c56-94](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/vulkan.c#L56-L94) [llamafile/gpu_backend.c176-213](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/gpu_backend.c#L176-L213) [llamafile/cuda.c84-129](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/cuda.c#L84-L129)

 
---

 
## Runtime Detection and Safety

 
### GPU Abstraction Layer

 llamafile uses a standardized `GpuBackend` structure to manage dynamically loaded GPU drivers. This ensures that CUDA, ROCm, and Vulkan follow the same safety protocols.

 
| Entity | File | Purpose |
|---|---|---|
| GpuBackend | llamafile/gpu_backend.h74-87 | Runtime state for a loaded backend DSO (handles, symbols, path). |
| GpuBackendDesc | llamafile/gpu_backend.h56-63 | Static identity and symbol names for a backend (e.g., VULKAN_DESC). |
| gpu_backend_probe | llamafile/gpu_backend.c176-213 | In-process crash guard using siglongjmp to handle driver faults. |
| gpu_backend_probe_oop | llamafile/gpu_backend.c215-258 | Out-of-process probe (Windows) to prevent driver init from corrupting the parent. |

 
### ABI-Correct Call Helpers

 On Windows, DSOs export functions using the `ms_abi` calling convention, while the host executable uses System V. llamafile provides wrappers to bridge this gap safely.

 
| Helper | Purpose |
|---|---|
| gpu_call_reg | Invokes ggml_backend_reg_t export llamafile/gpu_backend.c46-52 |
| gpu_call_device_count | Invokes device count probe llamafile/gpu_backend.c54-60 |
| gpu_call_log_set | Sets backend-specific logging llamafile/gpu_backend.c71-78 |

 **Sources:** [llamafile/gpu_backend.c38-78](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/gpu_backend.c#L38-L78)

 
---

 
## CPU Backend Implementation

 
### Architecture-Specific Compilation

 The build system compiles specialized kernels for various microarchitectures. These are linked into the final executable and selected by the `GemmFuncs` dispatcher.

 
| Implementation | Target Architecture | Description |
|---|---|---|
| amd_zen4 | Zen 4 | AVX-512 VNNI/BF16 optimizations. |
| amd_avx512f | Skylake+ | Standard AVX-512 foundation. |
| amd_avxvnni | Alderlake+ | AVX2 with VNNI instructions. |
| arm82 | ARMv8.2-A | DotProd and FP16 hardware support. |

 **Sources:** [llamafile/llamafile.h36](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.h#L36-L36) [llamafile/gpu_backend.h29-36](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/gpu_backend.h#L29-L36)

 
---

 
## GPU Backend Implementation

 
### Vulkan, CUDA, and ROCm

 These backends share a common lifecycle: loading a bundled DSO (e.g., `ggml-vulkan.so`), resolving symbols, and performing a safety probe to ensure usable hardware is present.

 
 - **Vulkan:** Implemented in `vulkan.c`, it uses `gpu_backend_link` to bind to the Vulkan GGML backend [llamafile/vulkan.c52-54](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/vulkan.c#L52-L54) It handles Windows driver faults via `gpu_backend_probe_oop` [llamafile/vulkan.c89](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/vulkan.c#L89-L89)
 - **CUDA/ROCm:** Managed in `cuda.c`. It defines two descriptors (`CUDA_DESC` and `ROCM_DESC`) that share the same underlying `GpuBackend` structure but target different library tags [llamafile/cuda.c42-62](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/cuda.c#L42-L62)
 
 
### Metal (Apple Silicon)

 The Metal backend is specialized for macOS. It utilizes a dynamic compilation pipeline where Metal source files are extracted from the ZIP archive and compiled into a self-contained dylib at runtime [llamafile/metal.c22-31](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/metal.c#L22-L31)

 For details, see [GPU Backends](https://deepwiki.com/mozilla-ai/llamafile/4.3-gpu-backends).

 
---

 
## Source Code Organization

 
| File | Purpose |
|---|---|
| llamafile/gpu_backend.c | Core logic for DSO loading, crash guards, and out-of-process probing. |
| llamafile/gpu_backend.h | Definitions for GpuBackend, GpuBackendDesc, and ABI-correct call helpers. |
| llamafile/vulkan.c | Vulkan-specific backend registration and DSO linking. |
| llamafile/cuda.c | CUDA and ROCm dynamic loading and device detection. |
| llamafile/metal.c | Metal JIT compilation and dylib loading for macOS. |
| llamafile/llamafile.h | Global GPU flags (FLAG_gpu) and detection API. |

 **Sources:** [llamafile/gpu_backend.c1-31](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/gpu_backend.c#L1-L31) [llamafile/cuda.c19-32](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/cuda.c#L19-L32) [llamafile/metal.c19-32](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/metal.c#L19-L32)
