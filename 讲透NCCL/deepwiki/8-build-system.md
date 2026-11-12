<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nccl · page 8 Build System · fetched 2026-10-28 -->

# Build System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CMakeLists.txt](CMakeLists.txt)
- [Makefile](Makefile)
- [bindings/ir/CMakeLists.txt](bindings/ir/CMakeLists.txt)
- [bindings/ir/Makefile](bindings/ir/Makefile)
- [bindings/ir/clang_compat/texture_fetch_functions.h](bindings/ir/clang_compat/texture_fetch_functions.h)
- [makefiles/common.mk](makefiles/common.mk)
- [src/CMakeLists.txt](src/CMakeLists.txt)
- [src/Makefile](src/Makefile)
- [src/include/nccl_device.h](src/include/nccl_device.h)
- [src/transport/net_efa_gda/CMakeLists.txt](src/transport/net_efa_gda/CMakeLists.txt)
- [src/transport/net_efa_gda/efa-dp-direct/CMakeLists.txt](src/transport/net_efa_gda/efa-dp-direct/CMakeLists.txt)

</details>



The NCCL build system is a hierarchical GNU Make-based system that orchestrates compilation of host and device code, manages library versioning, and produces multiple distribution formats. The build system consists of a top-level `Makefile` that delegates to subsystem makefiles in `src/`, `pkg/`, `bindings/`, and `docs/examples/` directories, with shared configuration defined in `makefiles/`. In addition to the primary Make system, a `CMakeLists.txt` is provided for platform detection and integration with modern C++ build workflows.

For detailed information on specific subsystems, see the following child pages:
*   [Build Orchestration](#8.1) — Detailed target DAG and root directory dispatch.
*   [Source Build System](#8.2) — Compilation of `libnccl.so`, source groups, and device manifest.
*   [Build Configuration](#8.3) — Compiler flags, CUDA architecture targeting, versioning, and LLVM IR generation.
*   [Packaging and Distribution](#8.4) — Generation of `.deb`, `.rpm`, and `.txz` packages.

---

## Build Directory Structure

The build system uses a configurable output directory (default: `./build`) that contains all generated artifacts. The directory layout isolates build products from source files and organizes outputs by type.

| Directory | Content |
|:---|:---|
| `include/` | Public headers (`nccl.h`, `nccl_device.h`) and internal device headers. |
| `lib/` | Shared libraries (`libnccl.so`), static archives (`libnccl_static.a`), and LLVM bitcode (`libnccl_device.bc`). |
| `obj/` | Intermediate object files (`.o`), dependency tracking files (`.d`), and IR aux files. |
| `bin/` | Compiled utility binaries, such as `ncclras`. |
| `lib/pkgconfig/` | Metadata for `pkg-config` integration (`nccl.pc`). |

**Sources:** [Makefile:27-28](), [src/Makefile:73-78](), [bindings/ir/Makefile:13-15](), [bindings/ir/CMakeLists.txt:12-14]()

---

## Top-Level Build Orchestration

The root `Makefile` provides the primary entry point for developers. It defines the `BUILDDIR` and `ABSBUILDDIR` variables and uses pattern rules to dispatch commands to subdirectories. It also handles the generation of LLVM IR bitcode if `EMIT_LLVM_IR` or `NCCL_EMIT_LTO_IR` is enabled.

### Target Dispatch Logic

The root Makefile maps high-level targets to specific directory actions:

```mermaid
graph TD
    "default"["default"] --> "src.build"["src.build"]
    "default" -->|"if IR_GOALS"| "ir-emit"["ir-emit"]
    
    "install"["install"] --> "src.install"["src.install"]
    
    "clean"["clean"] --> "src.clean"["src.clean"]
    "clean" --> "pkg.clean"["pkg.clean"]
    "clean" --> "nccl4py.clean"["nccl4py.clean"]
    "clean" --> "ir.clean"["ir.clean"]
    
    "examples"["examples"] --> "src.build"
    "examples" --> "ExamplesMake"["make -C docs/examples"]
    
    "pkg.txz.prep"["pkg.txz.prep"] --> "lic"["lic (License Copy)"]
```

**Sources:** [Makefile:9-30](), [Makefile:44-64]()

---

## Build Configuration and Versioning

Configuration is centralized in `makefiles/common.mk` and `makefiles/version.mk`. These files define compiler flags, sanitizer options, and the semantic versioning components.

### Version and Architecture Flow

The build system translates version definitions and hardware requirements into compiler definitions:

```mermaid
graph TB
    subgraph "Configuration Space"
        "VMK"["makefiles/version.mk"]
        "CMK"["makefiles/common.mk"]
    end

    subgraph "Code Entity Space"
        "MAJOR"["NCCL_MAJOR"]
        "MINOR"["NCCL_MINOR"]
        "GENCODE"["NVCC_GENCODE"]
        "CSTD"["CXXSTD (-std=c++17)"]
    end

    "VMK" --> "MAJOR"
    "VMK" --> "MINOR"
    "CMK" --> "GENCODE"
    "CMK" --> "CSTD"

    "MAJOR" -->|"add_compile_definitions"| "CMakeLists.txt:14-20"
    "GENCODE" -->|"NVCUFLAGS"| "NVCC_Compiler_Call"["NVCC Compiler Call"]
    "CSTD" -->|"CUDA 13 Logic"| "CMK_STD"["common.mk:93-98"]
```

**Sources:** [makefiles/common.mk:58-91](), [makefiles/common.mk:93-98](), [CMakeLists.txt:5-11](), [CMakeLists.txt:13-20](), [CMakeLists.txt:138-166]()

---

## LLVM IR Generation Pipeline

NCCL supports generating LLVM IR bitcode and LTO IR for device APIs, primarily used by downstream JIT consumers. This pipeline uses `clang`, `opt`, and `llvm-as` for standard bitcode, and `nvcc` for LTO IR.

### IR Build Process

The IR generation process involves several stages of transformation to ensure compatibility with `libNVVM`:

1.  **Clang Compilation:** Compiles `nccl_device_wrapper__impl.h` to unoptimized bitcode using `--cuda-device-only` [bindings/ir/Makefile:77-80]().
2.  **Optimization:** Runs `opt` with `internalize` and `inline` passes, preserving only `*nccl*` symbols [bindings/ir/Makefile:82-84]().
3.  **Cleaning:** Disassembles to human-readable `.ll` to strip `nvvm-reflect-ftz` and alignment attributes that cause rejection by `libNVVM` [bindings/ir/Makefile:89-97]().
4.  **Assembly:** Re-assembles the cleaned IR into the final `libnccl_device.bc` [bindings/ir/Makefile:99-102]().
5.  **LTO IR:** Separately generates LTO bitcode using `nvcc -dlto --ltoir` [bindings/ir/Makefile:115-122]().

**Sources:** [bindings/ir/Makefile:49-63](), [bindings/ir/Makefile:77-102](), [bindings/ir/CMakeLists.txt:97-143]()

---

## Packaging and Distribution

The `pkg/` directory contains logic for wrapping the compiled artifacts into OS-specific formats.

*   **Debian/Ubuntu:** Uses `debuild` to create `.deb` files.
*   **RedHat/CentOS:** Uses `rpmbuild` with a provided `.spec` file to create `.rpm` files.
*   **Generic:** Produces a `.txz` tarball containing the `include`, `lib`, and `bin` directories.
*   **CMake Support:** The `CMakeLists.txt` provides options like `BUILD_DEBIAN_PACKAGE`, `BUILD_REDHAT_PACKAGE`, and `BUILD_TXZ_PACKAGE` to automate these steps within a CMake workflow.

**Sources:** [Makefile:63-64](), [CMakeLists.txt:36-40]()

---

## Key Build Variables

| Variable | Description |
|:---|:---|
| `CUDA_HOME` | Path to the CUDA toolkit installation (default: `/usr/local/cuda`). |
| `NVCC_GENCODE` | Target CUDA architectures (e.g., `-gencode=arch=compute_90,code=sm_90`). |
| `EMIT_LLVM_IR` | If set to `1`, triggers the LLVM IR generation pipeline. |
| `NCCL_EMIT_LTO_IR` | If set to `1`, triggers the LTO IR generation pipeline. |
| `BUILDDIR` | Location for all build artifacts (default: `./build`). |
| `DEBUG` | If set to `1`, enables debug host and device flags. |

**Sources:** [makefiles/common.mk:8-12](), [makefiles/common.mk:58-91](), [Makefile:9-19]()

---

