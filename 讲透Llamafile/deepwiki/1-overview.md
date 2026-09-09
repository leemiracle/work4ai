> 来源: [https://deepwiki.com/mozilla-ai/llamafile/1-overview](https://deepwiki.com/mozilla-ai/llamafile/1-overview)
> DeepWiki mozilla-ai/llamafile | Last indexed: 29 August 2026 (435512

# Overview

  Relevant source files 
 - [README.md](https://github.com/mozilla-ai/llamafile/blob/43551265/README.md?plain=1)
 - [docs/images/llamafile-640x640.png](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/images/llamafile-640x640.png)
 - [docs/images/mozilla-logo-bw-rgb.png](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/images/mozilla-logo-bw-rgb.png)
 - [docs/index.md](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/index.md?plain=1)
 - [docs/quickstart.md](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/quickstart.md?plain=1)
 - [docs/security.md](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/security.md?plain=1)
 - [docs/support.md](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/support.md?plain=1)
 - [llamafile/version.h](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/version.h)
 
  
## Purpose

 This page provides an architectural overview of the llamafile project, explaining its design principles, core components, and how they work together to enable single-file distribution and execution of Large Language Models (LLMs). For detailed information about specific subsystems, see the specialized pages: [Project Architecture](https://deepwiki.com/mozilla-ai/llamafile/1.1-project-architecture) and [Quick Start](https://deepwiki.com/mozilla-ai/llamafile/1.2-quick-start).

 
## What is llamafile

 llamafile is a system that distributes and runs Large Language Models (LLMs) as single-file executables that work across multiple operating systems and CPU architectures without installation [README.md13-22](https://github.com/mozilla-ai/llamafile/blob/43551265/README.md?plain=1#L13-L22) It combines [llama.cpp](https://github.com/mozilla-ai/llamafile/blob/43551265/llama.cpp) (the inference engine), [Cosmopolitan Libc](https://github.com/mozilla-ai/llamafile/blob/43551265/Cosmopolitan Libc) (cross-platform runtime), and GGML (tensor operations) into a unified framework [docs/index.md13-22](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/index.md?plain=1#L13-L22) Model weights in GGUF format can be embedded directly into the executable using ZIP archives with 64KB page alignment for memory-mapped access [docs/index.md72-78](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/index.md?plain=1#L72-L78)

 Starting with version 0.10.0 [llamafile/version.h21-29](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/version.h#L21-L29) llamafile has transitioned to a new build system designed to maintain closer alignment with the latest upstream llama.cpp releases [README.md27-36](https://github.com/mozilla-ai/llamafile/blob/43551265/README.md?plain=1#L27-L36) The project also bundles `whisperfile` for speech-to-text, `transcribefile` for multi-model transcription, and `diffusionfile` for image generation [README.md24](https://github.com/mozilla-ai/llamafile/blob/43551265/README.md?plain=1#L24-L24)

 **Sources:** [README.md13-22](https://github.com/mozilla-ai/llamafile/blob/43551265/README.md?plain=1#L13-L22) [README.md27-36](https://github.com/mozilla-ai/llamafile/blob/43551265/README.md?plain=1#L27-L36) [docs/index.md13-22](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/index.md?plain=1#L13-L22) [docs/index.md72-78](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/index.md?plain=1#L72-L78) [llamafile/version.h21-29](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/version.h#L21-L29) [README.md24](https://github.com/mozilla-ai/llamafile/blob/43551265/README.md?plain=1#L24-L24)

 
## Key Features

 
| Feature | Description | Implementation |
|---|---|---|
| Cross-platform | Single binary runs on Windows, macOS, Linux, FreeBSD, NetBSD, OpenBSD | Cosmopolitan Libc APE format docs/support.md7-12 |
| Multi-architecture | x86_64 and aarch64 support in one file | Runtime dispatching and fat binary support docs/index.md55-63 |
| Embedded weights | Model weights inside executable | ZIP + 64KB alignment for mmap docs/index.md72-78 |
| GPU acceleration | NVIDIA (CUDA), AMD (ROCm), Apple (Metal), Vulkan | Dynamic DSO compilation/loading docs/support.md37-44 |
| HTTP Server | OpenAI and Anthropic compatible REST API | Embedded server with Web UI docs/quickstart.md50-59 |
| Execution Modes | AUTO, CHAT, SERVER, and CLI modes | ProgramMode enum in chatbot_repl.cpp README_0.10.0.md33 |
| Security | System call and filesystem sandboxing | pledge() and unveil() via Cosmopolitan docs/security.md3-13 |

 **Sources:** [README.md13-24](https://github.com/mozilla-ai/llamafile/blob/43551265/README.md?plain=1#L13-L24) [docs/index.md52-78](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/index.md?plain=1#L52-L78) [docs/support.md7-12](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/support.md?plain=1#L7-L12) [docs/quickstart.md50-59](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/quickstart.md?plain=1#L50-L59) [docs/security.md3-13](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/security.md?plain=1#L3-L13) [README_0.10.0.md33](https://github.com/mozilla-ai/llamafile/blob/43551265/README_0.10.0.md?plain=1#L33-L33)

 
## Core Architecture

 The llamafile system bridges high-level model distribution with low-level hardware acceleration:

 
```

```

 **System Architecture: Bridging Code Entities to System Components**

 The system integrates Cosmopolitan Libc for portability, llama.cpp for inference, and specialized shell scripts to handle GPU backend compilation. For example, `rocm.sh` and `cuda.sh` manage the dynamic generation of shared libraries (`.so`/`.dll`) for specific hardware architectures [docs/support.md44-51](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/support.md?plain=1#L44-L51)

 **Sources:** [README.md17-24](https://github.com/mozilla-ai/llamafile/blob/43551265/README.md?plain=1#L17-L24) [docs/index.md52-78](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/index.md?plain=1#L52-L78) [docs/support.md44-51](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/support.md?plain=1#L44-L51) [docs/security.md3-13](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/security.md?plain=1#L3-L13)

 
## Execution Modes

 llamafile v0.10.0+ introduces unified execution modes that allow a single binary to behave as a chat interface, a server, or a command-line tool [README_0.10.0.md33](https://github.com/mozilla-ai/llamafile/blob/43551265/README_0.10.0.md?plain=1#L33-L33)

 
 - **CHAT**: Launches an interactive terminal REPL using `bestline` for line editing and `chatbot_repl.cpp` for state management [docs/quickstart.md31-39](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/quickstart.md?plain=1#L31-L39)
 - **SERVER**: Starts the HTTP server (typically on port 8080) providing an OpenAI-compatible API and a web-based chat UI [docs/quickstart.md50-59](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/quickstart.md?plain=1#L50-L59)
 - **CLI**: Runs a one-shot completion based on a provided prompt [docs/security.md41](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/security.md?plain=1#L41-L41)
 - **Combined Mode (Default)**: When run without flags, it starts both the server and the terminal chat simultaneously [docs/security.md83-85](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/security.md?plain=1#L83-L85)
 
 For details, see [Project Architecture](https://deepwiki.com/mozilla-ai/llamafile/1.1-project-architecture).

 **Sources:** [README_0.10.0.md33](https://github.com/mozilla-ai/llamafile/blob/43551265/README_0.10.0.md?plain=1#L33-L33) [docs/quickstart.md31-59](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/quickstart.md?plain=1#L31-L59) [docs/security.md41-85](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/security.md?plain=1#L41-L85)

 
## Hardware Support and Backends

 llamafile dynamically detects hardware capabilities at runtime to select the most efficient compute path.

 
```

```

 **Backend Dispatch: Mapping Hardware to Code Logic**

 The system supports AVX, AVX2, AVX512, FMA, F16C, and VNNI on AMD64, and ARMv8a+ on ARM64 [docs/support.md25-36](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/support.md?plain=1#L25-L36) For GPUs, it detects tools like `nvcc` or `hipcc` on the `PATH` to compile optimized shared libraries on the fly [docs/support.md106-115](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/support.md?plain=1#L106-L115) If no specific vendor backend is available, it defaults to Vulkan or CPU fallback [docs/support.md40-42](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/support.md?plain=1#L40-L42)

 **Sources:** [docs/support.md21-51](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/support.md?plain=1#L21-L51) [docs/support.md106-115](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/support.md?plain=1#L106-L115) [docs/support.md40-42](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/support.md?plain=1#L40-L42)

 
## Getting Started

 To run a llamafile, you generally follow a three-step process:

 
 - Download a pre-built `.llamafile` (e.g., Qwen3.5-0.8B) [README.md49-50](https://github.com/mozilla-ai/llamafile/blob/43551265/README.md?plain=1#L49-L50)
 - Grant execution permissions (`chmod +x` on Unix) or add `.exe` on Windows [README.md52-65](https://github.com/mozilla-ai/llamafile/blob/43551265/README.md?plain=1#L52-L65)
 - Execute the file directly [README.md56](https://github.com/mozilla-ai/llamafile/blob/43551265/README.md?plain=1#L56-L56)
 
 For a step-by-step guide, see [Quick Start](https://deepwiki.com/mozilla-ai/llamafile/1.2-quick-start).

 **Sources:** [README.md44-65](https://github.com/mozilla-ai/llamafile/blob/43551265/README.md?plain=1#L44-L65) [docs/quickstart.md1-35](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/quickstart.md?plain=1#L1-L35)

 
## Project Structure

 
 - **`llama.cpp/`**: The upstream inference engine and core GGML library.
 - **`llamafile/`**: Core project logic, including GPU scripts (`rocm.sh`, `cuda.sh`), TinyBLAS kernels (`tinyblas.cu`), and versioning [llamafile/version.h21-29](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/version.h#L21-L29)
 - **`docs/`**: Technical documentation and user guides.
 - **`whisperfile/`**, **`transcribefile/`**, **`diffusionfile/`**: Specialized single-file tools for audio and image tasks [README.md24](https://github.com/mozilla-ai/llamafile/blob/43551265/README.md?plain=1#L24-L24)
 - **`tests/`**: Unit and integration tests, including `sandbox_test` for security verification [docs/security.md98-106](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/security.md?plain=1#L98-L106)
 
 **Sources:** [README.md24](https://github.com/mozilla-ai/llamafile/blob/43551265/README.md?plain=1#L24-L24) [README.md69-81](https://github.com/mozilla-ai/llamafile/blob/43551265/README.md?plain=1#L69-L81) [llamafile/version.h21-29](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/version.h#L21-L29) [docs/security.md98-106](https://github.com/mozilla-ai/llamafile/blob/43551265/docs/security.md?plain=1#L98-L106)
