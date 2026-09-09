> 来源: [https://deepwiki.com/mozilla-ai/llamafile/7-distribution-system](https://deepwiki.com/mozilla-ai/llamafile/7-distribution-system)
> DeepWiki mozilla-ai/llamafile | Last indexed: 29 August 2026 (435512

# Distribution System

  Relevant source files 
 - [README.md](https://github.com/mozilla-ai/llamafile/blob/43551265/README.md?plain=1)
 - [llamafile/cuda.c](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/cuda.c)
 - [llamafile/llamafile.c](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.c)
 - [llamafile/llamafile.h](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.h)
 - [llamafile/metal.c](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/metal.c)
 - [llamafile/version.h](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/version.h)
 
  
## Purpose and Scope

 The Distribution System enables llamafile's core value proposition: **distributing and running Large Language Models as single-file executables**. This system combines three key technologies:

 
 - **Cosmopolitan Libc** to create Actually Portable Executables (APE) that run on Linux, macOS, Windows, and FreeBSD without modification [README.md14-23](https://github.com/mozilla-ai/llamafile/blob/43551265/README.md?plain=1#L14-L23)
 - **ZIP-based model embedding** to package GGUF model weights inside the executable with proper memory alignment [llamafile/llamafile.c70-182](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.c#L70-L182)
 - **Multi-Architecture Fat Binaries** containing optimized code paths for both x86_64 and aarch64 in a single file [llamafile/version.h21-29](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/version.h#L21-L29)
 
 The result is a truly portable LLM distribution: users download one file, make it executable, and run it—no installation, no dependencies, no platform-specific builds [README.md44-66](https://github.com/mozilla-ai/llamafile/blob/43551265/README.md?plain=1#L44-L66)

 For details on the specific mechanisms, see the child pages:

 
 - For details on cross-platform portability, see [Cosmopolitan Libc Integration](https://deepwiki.com/mozilla-ai/llamafile/7.1-cosmopolitan-libc-integration).
 - For details on GGUF embedding and memory mapping, see [Embedded Model Format](https://deepwiki.com/mozilla-ai/llamafile/7.2-embedded-model-format).
 - For details on fat binary creation, see [Multi-Architecture Support](https://deepwiki.com/mozilla-ai/llamafile/7.3-multi-architecture-support).
 
 **Sources:** [README.md13-24](https://github.com/mozilla-ai/llamafile/blob/43551265/README.md?plain=1#L13-L24) [llamafile/version.h21-29](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/version.h#L21-L29)

 
---

 
## Actually Portable Executable (APE) Format

 
### Cosmopolitan Libc Integration

 Llamafile uses [Cosmopolitan Libc](https://github.com/mozilla-ai/llamafile/blob/43551265/Cosmopolitan Libc) a C library that enables the creation of **Actually Portable Executables (APE)**. An APE is a single binary file that executes natively on multiple operating systems and architectures without requiring recompilation or separate builds [README.md17-22](https://github.com/mozilla-ai/llamafile/blob/43551265/README.md?plain=1#L17-L22)

 The APE format works by structuring the executable to be valid in multiple formats simultaneously (PE, ELF, Mach-O). At runtime, a small bootstrap shim detects the host platform and jumps to the appropriate platform-specific code path. Llamafile leverages `cosmo_once` and `cosmo_dlopen` to manage platform-specific initialization and dynamic library loading [llamafile/cuda.c146-153](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/cuda.c#L146-L153)

 
```

```

 **Diagram: APE Bootstrap and Platform Detection**

 For details, see [Cosmopolitan Libc Integration](https://deepwiki.com/mozilla-ai/llamafile/7.1-cosmopolitan-libc-integration).

 **Sources:** [README.md19-22](https://github.com/mozilla-ai/llamafile/blob/43551265/README.md?plain=1#L19-L22) [llamafile/llamafile.c19-24](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.c#L19-L24) [llamafile/cuda.c36-40](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/cuda.c#L36-L40)

 
---

 
## ZIP-based Model Embedding

 
### GGUF in ZIP Archives

 Llamafile embeds GGUF model weights inside the executable using the PKZIP format [llamafile/llamafile.c70-82](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.c#L70-L82) This allows the weights to be memory-mapped directly from the archive without extraction, provided they are stored uncompressed and properly aligned [llamafile/llamafile.c170-182](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.c#L170-L182) The system searches for the PKZIP End of Central Directory (EOCD) record at the end of the file to locate embedded models [llamafile/llamafile.c110-136](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.c#L110-L136)

 The structure of a llamafile with an embedded model:

 
```

```

 **Diagram: Llamafile Internal File Layout**

 
### Memory Alignment Requirements

 GPU backends require model weights to be aligned on specific boundaries for efficient memory mapping [llamafile/llamafile.c170-182](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.c#L170-L182) The internal `struct llamafile` manages the file mapping and references to the embedded content [llamafile/llamafile.c59-68](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.c#L59-L68)

 For details, see [Embedded Model Format](https://deepwiki.com/mozilla-ai/llamafile/7.2-embedded-model-format).

 **Sources:** [llamafile/llamafile.c59-182](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.c#L59-L182) [llamafile/zip.h1-100](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/zip.h#L1-L100) [llamafile/llamafile.h48-61](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.h#L48-L61)

 
---

 
## Multi-Architecture Fat Binaries

 
### Dual x86_64 and aarch64 Support

 Llamafile executables are "fat binaries" containing machine code for both x86_64 and aarch64 architectures. The distribution system ensures that the correct optimized kernels are selected at runtime. For example, on macOS ARM64, the system detects Apple Silicon (`IsXnuSilicon()`) and prioritizes the Metal backend [llamafile/cuda.c85-88](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/cuda.c#L85-L88)

 
| Feature | x86_64 Path | aarch64 Path |
|---|---|---|
| Detection | !IsXnuSilicon() | IsXnuSilicon() |
| Backends | CUDA, ROCm, Vulkan | Metal, Vulkan |
| Library Extension | llamafile_get_dso_extension() | llamafile_get_dso_extension() |

 
### Build Pipeline for Fat Binaries

 The build system facilitates multi-architecture support by embedding source files and headers that can be compiled on the fly if a pre-built binary is not available [llamafile/metal.c54-91](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/metal.c#L54-L91)

 
```

```

 **Diagram: Fat Binary Concept**

 For details, see [Multi-Architecture Support](https://deepwiki.com/mozilla-ai/llamafile/7.3-multi-architecture-support).

 **Sources:** [llamafile/cuda.c85-117](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/cuda.c#L85-L117) [llamafile/metal.c54-91](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/metal.c#L54-L91) [llamafile/llamafile.h101-117](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.h#L101-L117)

 
---

 
## Dynamic GPU Backend Loading

 Llamafile supports dynamic loading of GPU acceleration backends (CUDA, ROCm, and Metal) at runtime [llamafile/cuda.c22-31](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/cuda.c#L22-L31) These backends are often provided as shared libraries (`.so` or `.dll`) that can be bundled within the llamafile's ZIP store and loaded using `cosmo_dlopen()` [llamafile/cuda.c26-31](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/cuda.c#L26-L31)

 
 - **CUDA/ROCm Backend:** Uses a shared `GpuBackend` structure and `GpuBackendDesc` to identify whether NVIDIA or AMD hardware is present [llamafile/cuda.c44-62](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/cuda.c#L44-L62)
 - **Metal Backend:** On macOS, the system can extract Metal source files (such as `ggml-metal.metal`) from the internal ZIP and compile a self-contained dylib at runtime using `posix_spawn` and the system compiler [llamafile/metal.c23-48](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/metal.c#L23-L48)
 - **DSO Resolution:** The function `llamafile_try_load_prebuilt_dso` handles searching for platform-appropriate binaries in `/zip/`, the application directory, or the user's home directory [llamafile/llamafile.h94-96](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.h#L94-L96)
 
 **Sources:** [llamafile/cuda.c44-82](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/cuda.c#L44-L82) [llamafile/metal.c20-48](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/metal.c#L20-L48) [llamafile/llamafile.h85-96](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/llamafile.h#L85-L96)
