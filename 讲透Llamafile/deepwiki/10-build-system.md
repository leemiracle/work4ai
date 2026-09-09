> 来源: [https://deepwiki.com/mozilla-ai/llamafile/10-build-system](https://deepwiki.com/mozilla-ai/llamafile/10-build-system)
> DeepWiki mozilla-ai/llamafile | Last indexed: 29 August 2026 (435512

# Build System

  Relevant source files 
 - [Makefile](https://github.com/mozilla-ai/llamafile/blob/43551265/Makefile)
 - [build/config.mk](https://github.com/mozilla-ai/llamafile/blob/43551265/build/config.mk)
 - [build/deps.mk](https://github.com/mozilla-ai/llamafile/blob/43551265/build/deps.mk)
 - [build/rules.mk](https://github.com/mozilla-ai/llamafile/blob/43551265/build/rules.mk)
 - [build/tags.mk](https://github.com/mozilla-ai/llamafile/blob/43551265/build/tags.mk)
 - [llama.cpp.patches/llamafile-files/BUILD.mk](https://github.com/mozilla-ai/llamafile/blob/43551265/llama.cpp.patches/llamafile-files/BUILD.mk)
 - [llamafile/BUILD.mk](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/BUILD.mk)
 
  The Build System orchestrates the compilation of llamafile from source code into cross-platform executables. It manages multi-architecture compilation, architecture-specific optimizations, asset embedding, and the creation of "Actually Portable Executables" (APE) that run natively on Linux, macOS, Windows, and BSD systems across both x86_64 and AARCH64 architectures without modification.

 For information about the distribution format produced by the build system, see [Distribution System](https://deepwiki.com/mozilla-ai/llamafile/7-distribution-system). For details on how the runtime selects optimal code paths, see [CPU Backend](https://deepwiki.com/mozilla-ai/llamafile/4.2-cpu-backend) and [Architecture-Specific Builds](https://deepwiki.com/mozilla-ai/llamafile/10.3-architecture-specific-builds).

 
## Build Configuration

 The build system is configured through `build/config.mk`, which defines essential variables and environment settings for the compilation process.

 
### Toolchain Variables

 The build system uses the Cosmopolitan Libc toolchain, referenced through several key variables [build/config.mk18-27](https://github.com/mozilla-ai/llamafile/blob/43551265/build/config.mk#L18-L27):

 
| Variable | Default Value | Purpose |
|---|---|---|
| PREFIX | /usr/local | Installation directory for binaries and man pages |
| COSMOCC | .cosmocc/4.0.2 | Directory containing the Cosmopolitan compiler toolchain |
| TOOLCHAIN | $(COSMOCC)/bin/cosmo | Path prefix for compiler executables |
| CC | $(TOOLCHAIN)cc | C compiler |
| CXX | $(TOOLCHAIN)c++ | C++ compiler |
| AR | $(COSMOCC)/bin/ar.ape | Static library archiver |
| ZIPOBJ | $(COSMOCC)/bin/zipobj | Tool for embedding assets as ZIP objects |

 The Cosmopolitan toolchain is automatically downloaded if not present [build/config.mk75-76](https://github.com/mozilla-ai/llamafile/blob/43551265/build/config.mk#L75-L76):

 
```

```

 
### Compiler Flags

 Default compilation flags are defined in [build/config.mk29-34](https://github.com/mozilla-ai/llamafile/blob/43551265/build/config.mk#L29-L34):

 
 - `ARFLAGS = rcsD` - Archive flags for creating static libraries.
 - `CXXFLAGS = -frtti -std=gnu++23` - C++ standard with RTTI enabled.
 - `CCFLAGS = -O2 -g -fexceptions -ffunction-sections -fdata-sections -mclang` - Common C/C++ flags with optimization and section separation.
 - `CPPFLAGS_ = -iquote. -mcosmo -DGGML_MULTIPLATFORM -Wno-attributes -DLLAMAFILE_DEBUG` - Preprocessor flags including Cosmopolitan mode and platform defines.
 - `TARGET_ARCH = -Xx86_64-mtune=znver4` - Default target architecture (AMD Zen 4).
 
 
### Build Modes and Environment

 The build system supports different build modes through the `MODE` variable [build/config.mk47-52](https://github.com/mozilla-ai/llamafile/blob/43551265/build/config.mk#L47-L52) All build artifacts are placed in `o/$(MODE)/` directories. Deterministic builds are enforced by setting `SOURCE_DATE_EPOCH = 0` [build/config.mk56](https://github.com/mozilla-ai/llamafile/blob/43551265/build/config.mk#L56-L56)

 For details, see [Build Configuration](https://deepwiki.com/mozilla-ai/llamafile/10.1-build-configuration).

 **Sources:** [build/config.mk1-76](https://github.com/mozilla-ai/llamafile/blob/43551265/build/config.mk#L1-L76)

 
## Makefile Structure

 The main `Makefile` orchestrates the build by including specialized build files for different components [Makefile12-26](https://github.com/mozilla-ai/llamafile/blob/43551265/Makefile#L12-L26)

 
### Component Inclusion Map

 
```

```

 Each `BUILD.mk` file defines package-specific sources (`SRCS`), headers (`HDRS`), and compiler flags (e.g., `LLAMAFILE_CPPFLAGS`) [llamafile/BUILD.mk32-64](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/BUILD.mk#L32-L64)

 **Sources:** [Makefile1-26](https://github.com/mozilla-ai/llamafile/blob/43551265/Makefile#L1-L26) [llamafile/BUILD.mk1-64](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/BUILD.mk#L1-L64)

 
## Compilation Pipeline

 The `build/rules.mk` file defines pattern rules for compiling different source file types into object files.

 
### Core Compilation Rules

 The pipeline uses standard and extension-preserving rules to handle filename collisions (e.g., when `ggml.c` and `ggml.cpp` exist in the same directory) [build/rules.mk8-54](https://github.com/mozilla-ai/llamafile/blob/43551265/build/rules.mk#L8-L54)

 
| Rule | Input | Output | Tool |
|---|---|---|---|
| COMPILE.c | .c | .o | $(CC) |
| COMPILE.cc | .cc, .cpp | .o | $(CXX) |
| o/$(MODE)/%.c | .gperf | .c | build/gperf |
| o/$(MODE)/%.zip.o | Any asset | .zip.o | $(ZIPOBJ) |

 
### Dual-Architecture Archives

 Static libraries are created with special handling for dual-architecture support [build/rules.mk68-71](https://github.com/mozilla-ai/llamafile/blob/43551265/build/rules.mk#L68-L71):

 
```

```

 This creates both x86_64 and AARCH64 versions of each library, with the ARM version stored in a `.aarch64` subdirectory.

 For details, see [Compilation Pipeline](https://deepwiki.com/mozilla-ai/llamafile/10.2-compilation-pipeline).

 **Sources:** [build/rules.mk1-115](https://github.com/mozilla-ai/llamafile/blob/43551265/build/rules.mk#L1-L115)

 
## Multi-Architecture Optimized Kernels

 The build system compiles source code into multiple architecture-specific variants within a single build. This is most prominent in the `llamafile` package, which provides runtime CPU dispatch to SIMD implementations [llamafile/BUILD.mk175-200](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/BUILD.mk#L175-L200)

 
### CPU Kernel Dispatch Logic

 The `llamafile/sgemm.cpp` file acts as a runtime dispatcher, selecting the best kernel based on CPU features detected via `X86_HAVE` or `getauxval(AT_HWCAP)`.

 
```

```

 
### Specialized Source Groups

 
| Group | Files | Optimizations |
|---|---|---|
| SGEMM | tinyblas_cpu_sgemm_*.cpp | AVX, AVX2, AVX512, Zen4, ARM80, ARM82 llamafile/BUILD.mk175-184 |
| MIXMUL | tinyblas_cpu_mixmul_*.cpp | Mixture-of-Experts kernels for SIMD llamafile/BUILD.mk186-194 |
| IQK | iqk_mul_mat_*.cpp | Integer Quantized Kernels (Q4_K, Q8_K) llamafile/BUILD.mk198-201 |

 For details, see [Architecture-Specific Builds](https://deepwiki.com/mozilla-ai/llamafile/10.3-architecture-specific-builds).

 **Sources:** [llamafile/BUILD.mk175-201](https://github.com/mozilla-ai/llamafile/blob/43551265/llamafile/BUILD.mk#L175-L201)

 
## GPU Backend Targets

 The build system includes standalone targets for building GPU shared libraries (`.so`/`.dll`) that can be loaded at runtime [Makefile65-80](https://github.com/mozilla-ai/llamafile/blob/43551265/Makefile#L65-L80)

 
```

```

 
 - `make cuda`: Builds CUDA backend with TinyBLAS [Makefile65-67](https://github.com/mozilla-ai/llamafile/blob/43551265/Makefile#L65-L67)
 - `make cublas`: Builds CUDA backend using NVIDIA's cuBLAS library [Makefile69-71](https://github.com/mozilla-ai/llamafile/blob/43551265/Makefile#L69-L71)
 - `make rocm`: Builds ROCm backend for AMD GPUs [Makefile73-75](https://github.com/mozilla-ai/llamafile/blob/43551265/Makefile#L73-L75)
 - `make vulkan`: Builds Vulkan backend [Makefile77-79](https://github.com/mozilla-ai/llamafile/blob/43551265/Makefile#L77-L79)
 
 These targets invoke specialized scripts, passing the `GGML_VERSION` and `GGML_COMMIT` extracted from the submodules [build/config.mk8-12](https://github.com/mozilla-ai/llamafile/blob/43551265/build/config.mk#L8-L12)

 **Sources:** [Makefile65-80](https://github.com/mozilla-ai/llamafile/blob/43551265/Makefile#L65-L80) [build/config.mk8-12](https://github.com/mozilla-ai/llamafile/blob/43551265/build/config.mk#L8-L12)

 
## Setup and Patch Management

 Before building, the system requires initialization via `make setup` [Makefile87-128](https://github.com/mozilla-ai/llamafile/blob/43551265/Makefile#L87-L128)

 
 - **Submodule Initialization**: Fetches `llama.cpp`, `whisper.cpp`, `stable-diffusion.cpp`, `transcribe.cpp`, and `zipalign` [Makefile92-125](https://github.com/mozilla-ai/llamafile/blob/43551265/Makefile#L92-L125)
 - **Patch Application**: Applies custom llamafile patches to submodules to enable Cosmopolitan support and TUI integration [Makefile97-120](https://github.com/mozilla-ai/llamafile/blob/43551265/Makefile#L97-L120)
 - **Toolchain Setup**: Downloads the required `cosmocc` version [Makefile127](https://github.com/mozilla-ai/llamafile/blob/43551265/Makefile#L127-L127)
 
 If the submodules need to be restored to their original state, `make reset-repo` can be used [Makefile129-141](https://github.com/mozilla-ai/llamafile/blob/43551265/Makefile#L129-L141)

 **Sources:** [Makefile87-141](https://github.com/mozilla-ai/llamafile/blob/43551265/Makefile#L87-L141)
