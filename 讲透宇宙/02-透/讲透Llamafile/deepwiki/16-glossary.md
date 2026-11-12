> 来源: [https://deepwiki.com/mozilla-ai/llamafile/16-glossary](https://deepwiki.com/mozilla-ai/llamafile/16-glossary)
> DeepWiki mozilla-ai/llamafile | Last indexed: 29 August 2026 (435512

# Glossary

  Relevant source files 
 - [README.md](https://github.com/mozilla-ai/llamafile/blob/43551265/README.md?plain=1)
 - [docs/images/llamafile-640x640.png](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/images/llamafile-640x640.png)
 - [docs/images/mozilla-logo-bw-rgb.png](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/images/mozilla-logo-bw-rgb.png)
 - [docs/index.md](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/index.md?plain=1)
 - [docs/quickstart.md](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/quickstart.md?plain=1)
 - [docs/security.md](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/security.md?plain=1)
 - [docs/support.md](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/support.md?plain=1)
 - [llamafile/cuda.c](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/cuda.c)
 - [llamafile/llamafile.c](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.c)
 - [llamafile/llamafile.h](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.h)
 - [llamafile/metal.c](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/metal.c)
 - [llamafile/sgemm.cpp](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/sgemm.cpp)
 - [llamafile/sgemm.h](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/sgemm.h)
 - [llamafile/tinyblas-compat.h](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/tinyblas-compat.h)
 - [llamafile/tinyblas.cu](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/tinyblas.cu)
 - [llamafile/tinyblas.h](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/tinyblas.h)
 - [llamafile/tinyblas_cpu_unsupported.cpp](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/tinyblas_cpu_unsupported.cpp)
 - [llamafile/version.h](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/version.h)
 - [tests/strsm/BUILD.mk](https://github.com/mozilla-ai/llamafile/blob/43551265/tests/strsm/BUILD.mk)
 - [tests/strsm/build_and_run.sh](https://github.com/mozilla-ai/llamafile/blob/43551265/tests/strsm/build_and_run.sh)
 - [tests/strsm/strsm_test.cu](https://github.com/mozilla-ai/llamafile/blob/43551265/tests/strsm/strsm_test.cu)
 
  This page provides definitions for codebase-specific terms, jargon, and domain concepts used throughout the llamafile project. It is intended to assist onboarding engineers in navigating the integration of Large Language Models (LLMs) with multi-platform runtime environments.

 
## Core Concepts

 
### Actually Portable Executable (APE)

 A binary format enabled by **Cosmopolitan Libc** that allows a single file to run on multiple operating systems (Linux, macOS, Windows, FreeBSD, OpenBSD, NetBSD) and architectures (x86_64, ARM64) without installation [README.md19-22](https://github.com/mozilla-ai/llamafile/blob/43551265/README.md?plain=1#L19-L22) In llamafile, this is used to package the LLM weights, the inference engine, and the HTTP server into one executable [README.md13-15](https://github.com/mozilla-ai/llamafile/blob/43551265/README.md?plain=1#L13-L15) On UNIX systems, it extracts a small loader program named `ape` to `$TMPDIR/.ape-1.10` to map the model into memory [docs/support.md14-17](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/support.md?plain=1#L14-L17)

 
### GGUF (GPT-Generated Unified Format)

 The standard file format for LLM weights used by llama.cpp and llamafile. llamafile extends this by embedding GGUF files within a ZIP structure inside the APE binary [llamafile/llamafile.c70-76](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.c#L70-L76) Weights are typically memory-mapped directly from the executable for efficiency [llamafile/llamafile.c64-68](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.c#L64-L68)

 
### TinyBLAS

 A lightweight, header-only Basic Linear Algebra Subprograms (BLAS) library implemented in llamafile to provide optimized matrix multiplication kernels for both CPU and GPU backends [llamafile/tinyblas.h1-97](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/tinyblas.h#L1-L97) It supports runtime dispatch based on CPU features like AVX, AVX2, AVX512, and ARM NEON [llamafile/sgemm.cpp64-138](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/sgemm.cpp#L64-L138) The GPU implementation uses warp and block tiling strategies for performance [llamafile/tinyblas.cu140-154](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/tinyblas.cu#L140-L154)

 
---

 
## Technical Terms & Components

 
| Term | Definition | Code Pointer |
|---|---|---|
| DSO | Dynamic Shared Object. Used for runtime loading of GPU backends (CUDA/ROCm/Metal). | llamafile/cuda.c22-27 |
| IQK | Integer Quantized Kernels. Highly optimized matmul for Q4_K, Q5_K, and Q6_K formats. | llamafile/sgemm.h11-22 |
| MoE | Mixture of Experts. llamafile provides specialized routing and multiplication kernels for MoE models. | llamafile/sgemm.cpp50-58 |
| Pledge / Unveil | Security sandboxing mechanisms from OpenBSD, ported via Cosmopolitan to restrict process capabilities. | llamafile/llamafile.h119-125 |
| Schlep | Internal term for memory-mapping or "warming up" model weights into RAM. | llamafile/llamafile.h73 |
| Yoink | A Cosmopolitan Libc macro (__static_yoink) used to force the inclusion of source files or assets into the binary. | llamafile/metal.c54-60 |
| ProgramMode | Enum defining the execution mode (AUTO, CHAT, SERVER, CLI). | llamafile/llamafile.h139-144 |
| tinyblasHandle_t | A pointer to a tinyblasContext, used to manage GPU streams and state. | llamafile/tinyblas.h49-50 |

 
---

 
## Architecture & Data Flow

 
### GPU Backend Discovery and Loading

 llamafile detects GPU hardware at runtime and attempts to load or compile the necessary drivers. It uses `cosmo_dlopen` to load shared libraries (`.so`, `.dylib`, or `.dll`) dynamically [llamafile/cuda.c26-31](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/cuda.c#L26-L31) If a backend is explicitly requested via `FLAG_gpu` but fails, the program exits with a fatal error [llamafile/cuda.c138-142](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/cuda.c#L138-L142)

 Title: GPU Backend Initialization Flow

 
```

```

 Sources: [llamafile/llamafile.h101-116](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.h#L101-L116) [llamafile/cuda.c64-82](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/cuda.c#L64-L82) [llamafile/metal.c22-30](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/metal.c#L22-L30) [llamafile/cuda.c126-130](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/cuda.c#L126-L130)

 
### CPU Kernel Dispatch (SGEMM)

 The `GemmFuncs` struct acts as a traffic controller, selecting the fastest available math kernel based on the host CPU's instruction set discovered via `X86_HAVE` or `getauxval` [llamafile/sgemm.cpp47-139](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/sgemm.cpp#L47-L139)

 Title: Natural Language Space to Code Entity Space: CPU Dispatch

 
```

```

 Sources: [llamafile/sgemm.cpp47-139](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/sgemm.cpp#L47-L139) [llamafile/sgemm.h39-57](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/sgemm.h#L39-L57)

 
---

 
## Global Configuration Flags

 The behavior of the llamafile runtime is controlled by several global `extern` variables defined in `llamafile.h` and implemented in `llamafile.c`.

 
| Flag | Description | Code Pointer |
|---|---|---|
| FLAG_gpu | Integer selecting the GPU backend (0=Auto, -1=Disable, 1=AMD, 2=Apple, 4=NVIDIA, 8=Vulkan). | llamafile/llamafile.h39 |
| FLAG_nocompile | If true, prevents the runtime from attempting to compile GPU DSOs (e.g., Metal). | llamafile/llamafile.h32 |
| FLAG_recompile | Forces recompilation of GPU libraries even if they exist in the cache. | llamafile/llamafile.h37 |
| FLAG_precise | Forces the use of higher-precision math in TinyBLAS kernels. | llamafile/llamafile.h36 |
| FLAG_nothink | Filters out "thinking" or reasoning tokens (e.g., <thought>) from output. | llamafile/llamafile.h35 |
| FLAG_unsecure | Disables pledge() sandboxing. | llamafile/llamafile.h38 |

 Sources: [llamafile/llamafile.h31-40](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.h#L31-L40) [llamafile/llamafile.c1-40](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.c#L1-L40)

 
## Derived Tools and Tooling Terminology

 
 - **`cosmocc`**: The Cosmopolitan C toolchain used to build the "Actually Portable" binaries [docs/support.md29-31](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/support.md?plain=1#L29-L31)
 - **`zipalign`**: A utility used to ensure that model weights within the ZIP archive are aligned to 64KB boundaries, required for direct memory mapping to GPU [llamafile/llamafile.c188-195](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.c#L188-L195)
 - **`whisperfile`**: A single-file speech-to-text tool built on whisper.cpp [README.md24](https://github.com/mozilla-ai/llamafile/blob/43551265/README.md?plain=1#L24-L24)
 - **`transcribefile`**: A CLI tool for multi-model transcription supporting various families like Parakeet and Moonshine.
 - **`diffusionfile`**: A single-file image generation tool built on stable-diffusion.cpp.
 - **`LocalScore`**: A benchmarking tool for measuring LLM performance (TPS, TTFT) and hardware capabilities [README.md61-63](https://github.com/mozilla-ai/llamafile/blob/43551265/README.md?plain=1#L61-L63)
 - **`mnpack`**: Part of the build system for creating multi-architecture fat binaries.
 
 Sources: [llamafile/llamafile.c70-155](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.c#L70-L155) [README.md1-70](https://github.com/mozilla-ai/llamafile/blob/43551265/README.md?plain=1#L1-L70) [docs/support.md1-40](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/support.md?plain=1#L1-L40)
