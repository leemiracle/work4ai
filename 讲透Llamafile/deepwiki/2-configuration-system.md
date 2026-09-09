> 来源: [https://deepwiki.com/mozilla-ai/llamafile/2-configuration-system](https://deepwiki.com/mozilla-ai/llamafile/2-configuration-system)
> DeepWiki mozilla-ai/llamafile | Last indexed: 29 August 2026 (435512

# Configuration System

  Relevant source files 
 - [llama.cpp.patches/llamafile-files/BUILD.mk](https://github.com/mozilla-ai/llamafile/blob/43551265/llama.cpp.patches/llamafile-files/BUILD.mk)
 - [llamafile/BUILD.mk](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/BUILD.mk)
 - [llamafile/cuda.c](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/cuda.c)
 - [llamafile/llamafile.c](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.c)
 - [llamafile/llamafile.h](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.h)
 - [llamafile/metal.c](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/metal.c)
 
  
## Purpose and Scope

 The Configuration System in llamafile provides a comprehensive command-line interface for controlling model loading, inference behavior, HTTP server settings, GPU acceleration, and security policies. The system exposes configuration variables through a unified `FLAG_` namespace that is parsed at startup and used throughout the runtime.

 This document covers flag declaration, parsing, and integration with runtime components. For detailed information about specific flag categories, see the following child page:

 
 - **[Model and Runtime Flags](https://deepwiki.com/mozilla-ai/llamafile/2.1-model-and-runtime-flags)**: Controls model loading, context size, GPU layers, batch sizes, and runtime behavior. Documents `FLAG_gpu`, `FLAG_verbose`, `FLAG_precise`, `FLAG_nothink`, `FLAG_nocompile`, `FLAG_recompile`, `FLAG_unsecure`, and related globals.
 
 
---

 
## Configuration Architecture

 The configuration system utilizes global variables declared as externs in the `llamafile` header. These flags are defined in [llamafile/llamafile.h31-40](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.h#L31-L40) and implemented in [llamafile/llamafile.c](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.c) The `llamafile_get_flags()` function is declared to handle the population of these variables from `argc` and `argv` [llamafile/llamafile.h75](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.h#L75-L75)

 
### Configuration Data Flow

 
```

```

 **Sources:** [llamafile/llamafile.h31-40](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.h#L31-L40) [llamafile/llamafile.h75](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.h#L75-L75)

 
---

 
## Global Flag Definitions

 The following core flags are defined in the global namespace to control the fundamental behavior of the llamafile executable.

 
### Behavior and UI Flags

 
| Flag Name | Type | Purpose | Source |
|---|---|---|---|
| FLAG_log_disable | bool | Disables logging in chatbot_comm.cpp | llamafile/llamafile.h31 |
| FLAG_ascii | bool | Uses ASCII art for logo in chatbot_logo.cpp | llamafile/llamafile.h33 |
| FLAG_nologo | bool | Suppresses logo display in chatbot_main.cpp | llamafile/llamafile.h34 |
| FLAG_nothink | bool | Filters thinking/reasoning content in chatbot_cli.cpp | llamafile/llamafile.h35 |
| FLAG_verbose | int | Controls diagnostic output in main and GPU loaders | llamafile/llamafile.h40 |

 
### Performance and Security Flags

 
| Flag Name | Type | Purpose | Source |
|---|---|---|---|
| FLAG_precise | bool | Forces precise math in tinyblas_cpu.h | llamafile/llamafile.h36 |
| FLAG_unsecure | bool | Disables pledge() sandboxing in sandbox.c | llamafile/llamafile.h38 |

 
### GPU and Compilation Flags

 
| Flag Name | Type | Purpose | Source |
|---|---|---|---|
| FLAG_nocompile | bool | Disables GPU library compilation in metal.c | llamafile/llamafile.h32 |
| FLAG_recompile | bool | Forces GPU library recompilation in metal.c | llamafile/llamafile.h37 |
| FLAG_gpu | int | GPU backend selection (AMD/Apple/NVIDIA/Vulkan) | llamafile/llamafile.h39 |

 
---

 
## GPU Backend Configuration

 The `FLAG_gpu` variable accepts specific integer constants to determine how llamafile interacts with hardware accelerators. The logic in `cuda.c` and `metal.c` branches based on these values to decide whether to load specific DSOs [llamafile/cuda.c91-98](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/cuda.c#L91-L98)

 
### GPU Selection Constants

 
```

```

 **Sources:** [llamafile/llamafile.h101-107](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.h#L101-L107)

 
### GPU Utility Functions

 The configuration system relies on several utility functions to validate and describe the GPU environment:

 
 - `llamafile_gpu_parse(const char *)`: Converts a string argument (e.g., "nvidia") into the corresponding integer flag [llamafile/llamafile.h114](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.h#L114-L114)
 - `llamafile_describe_gpu()`: Returns a human-readable string describing the detected or selected GPU [llamafile/llamafile.h115](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.h#L115-L115)
 - `llamafile_early_gpu_init(char **)`: Performs early-stage initialization of GPU drivers [llamafile/llamafile.h116](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.h#L116-L116)
 
 
---

 
## Sandboxing and Security Configuration

 The security posture is configured via `FLAG_unsecure` and specific sandbox definitions. By default, llamafile applies `pledge()` and `unveil()` (or their platform equivalents like SECCOMP/Landlock) [llamafile/llamafile.h122-125](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.h#L122-L125)

 
### Sandbox Status Codes

 
| Constant | Value | Description | Source |
|---|---|---|---|
| LLAMAFILE_SANDBOX_ACTIVE | 0 | pledge() is active | llamafile/llamafile.h128 |
| LLAMAFILE_SANDBOX_UNSECURE | 1 | Skipped due to --unsecure flag | llamafile/llamafile.h129 |
| LLAMAFILE_SANDBOX_GPU | 2 | Skipped because a GPU backend is loaded | llamafile/llamafile.h130 |
| LLAMAFILE_SANDBOX_UNSUPPORTED | 3 | OS cannot enforce the sandbox | llamafile/llamafile.h131 |

 
---

 
## Flag Subcategories

 Detailed documentation for specific flags is partitioned into the following child section:

 
### [Model and Runtime Flags](https://deepwiki.com/mozilla-ai/llamafile/2.1-model-and-runtime-flags)

 Covers flags that define the execution environment for the LLM, including:

 
 - **GPU Management**: `FLAG_gpu`, `FLAG_nocompile`, and `FLAG_recompile`.
 - **Numerical Precision**: `FLAG_precise` for tinyBLAS kernels.
 - **Diagnostics**: `FLAG_verbose` levels.
 - **Security**: `FLAG_unsecure` for sandbox bypass.
 - **Content Filtering**: `FLAG_nothink` for reasoning models.
 
 **Sources:** [llamafile/llamafile.h27-41](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.h#L27-L41) [llamafile/llamafile.h121-134](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.h#L121-L134)
