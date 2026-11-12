<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cutlass · page 14 Contributing and Development Guidelines · fetched 2026-10-26 -->

# Contributing and Development Guidelines

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/ISSUE_TEMPLATE/documentation_request.md](.github/ISSUE_TEMPLATE/documentation_request.md)
- [.github/ISSUE_TEMPLATE/submit_question.md](.github/ISSUE_TEMPLATE/submit_question.md)
- [.github/workflows/labeler.yml](.github/workflows/labeler.yml)
- [.github/workflows/new-issues-to-triage-projects.yml](.github/workflows/new-issues-to-triage-projects.yml)
- [.github/workflows/stale.yml](.github/workflows/stale.yml)
- [.gitignore](.gitignore)
- [CONTRIBUTORS.md](CONTRIBUTORS.md)
- [include/cutlass/gemm/collective/sm90_mma_array_tma_gmma_ss_warpspecialized_fp8.hpp](include/cutlass/gemm/collective/sm90_mma_array_tma_gmma_ss_warpspecialized_fp8.hpp)
- [python/cutlass_library/sm90_utils.py](python/cutlass_library/sm90_utils.py)

</details>



## Purpose and Scope

This page provides guidelines for developing, building, testing, and contributing to the CUTLASS project. It covers environment setup, build system configuration, coding standards, testing procedures, and submission process. For information about using CUTLASS as a library, see [Overview](#1). For details on specific components like GEMM operations or CuTe abstractions, see [GEMM Operations](#4) and [CuTe Core Abstractions](#2).

---

## Development Environment Requirements

### System Prerequisites

CUTLASS development requires specific compiler, operating system, and CUDA toolkit versions to ensure compatibility across the supported GPU architectures.

**Minimum Requirements:**

| Component | Requirement |
|-----------|-------------|
| Architecture | Volta (compute capability 7.0) or newer |
| Compiler | C++17 support required |
| CUDA Toolkit | 11.4 minimum, 12.8+ recommended |
| CMake | 3.18+ |

**Supported Operating Systems:**

| Operating System | Tested Compiler |
|-----------------|-----------------|
| Ubuntu 18.04 | GCC 7.5.0 |
| Ubuntu 20.04 | GCC 10.3.0 |
| Ubuntu 22.04 | GCC 11.2.0 |

**Important Compiler Notes:**
- GCC 8.5.0 has known regressions with fold expressions and overloaded operators.
- GCC 7.5.0 or GCC >= 9 recommended.
- Windows builds currently have known issues across all CUDA toolkits.

### CUDA Toolkit Configuration

The `CUDACXX` environment variable must point to the NVCC compiler in your CUDA toolkit installation. The build system uses utilities like `CudaToolkitVersionSatisfies` to ensure the environment meets feature requirements (e.g., SM90/SM100 features require specific CUDA versions).

Sources: [python/cutlass_library/sm90_utils.py:57-70]()

---

## Build System Architecture

### CMake Configuration Overview

CUTLASS uses a CMake-based build system with custom functions for managing CUDA compilation, unity builds, and architecture-specific code generation.

```mermaid
graph TB
    subgraph "CMake_Entry_Point"
        ["CMakeLists.txt"]
    end
    
    subgraph "CUDA_Detection"
        ["CUDA.cmake"]
        ["NVCC_version_validation"]
    end
    
    subgraph "Build_Configuration"
        ["CUTLASS_NVCC_ARCHS"]
        ["CUTLASS_UNITY_BUILD_ENABLED"]
    end
    
    subgraph "Target_Creation"
        ["cutlass_add_library"]
        ["cutlass_add_executable"]
        ["cutlass_unify_source_files"]
    end
    
    subgraph "Output_Artifacts"
        ["cutlass_lib.a"]
        ["test_unit_binaries"]
        ["example_binaries"]
    end
    
    "CMakeLists.txt" --> "CUDA.cmake"
    "CUDA.cmake" --> "NVCC_version_validation"
    
    "CMakeLists.txt" --> "CUTLASS_NVCC_ARCHS"
    "CMakeLists.txt" --> "CUTLASS_UNITY_BUILD_ENABLED"
    
    "CUTLASS_NVCC_ARCHS" --> "cutlass_add_library"
    "CUTLASS_UNITY_BUILD_ENABLED" --> "cutlass_unify_source_files"
    
    "cutlass_add_library" --> "cutlass_lib.a"
    "cutlass_add_executable" --> "test_unit_binaries"
    "cutlass_add_executable" --> "example_binaries"
```

**Figure: CMake Build System Architecture**

### Architecture Target Specification

CUTLASS uses the `CUTLASS_NVCC_ARCHS` CMake variable to specify target GPU architectures. This is critical for architecture-accelerated features.

**Architecture Flag Syntax:**

| Architecture | Flag | Notes |
|--------------|------|-------|
| Hopper GH100 | `90a` | Architecture-accelerated features |
| Blackwell SM100 | `100a` | Datacenter products |
| Blackwell SM103 | `103a` | B300 GPUs |
| Ampere | `80` | Standard PTX |

The `a` suffix (e.g., `90a`, `100a`) enables architecture-accelerated PTX instructions that do not have forward compatibility guarantees.

---

## Project Structure and Organization

### Header-Only Library Design

CUTLASS is a header-only template library. All core logic resides in the `include/` directory.

```
include/                     # Client applications target this directory
  cutlass/                   # CUDA Templates for Linear Algebra Subroutines
    arch/                    # Architecture-specific features
    gemm/                    # GEMM operations and kernels
    numeric_types.h          # Numeric type definitions
    trace.h                  # Debugging and tracing
    version.h                # Version macros
    
  cute/                      # CuTe abstractions (CUTLASS 3.x+)
    arch/                    # PTX wrapper structs
    atom/                    # MMA and Copy atoms
      mma_atom.hpp           # Mma_Atom and TiledMMA
      copy_atom.hpp          # Copy_Atom and TiledCopy
    tensor.hpp               # CuTe Tensor abstraction
```

Sources: [include/cutlass/gemm/collective/sm90_mma_array_tma_gmma_ss_warpspecialized_fp8.hpp:34-46]()

### Python Package Organization

CUTLASS includes several Python packages. Version information is centrally managed, and packages are organized to support both the C++ generator and the CuTe DSL.

| Package | Purpose |
|---------|---------|
| `cutlass_library` | Kernel enumeration and library generation |
| `pycute` | Python CuTe implementation |
| `cutlass_cppgen` | C++ code generation utilities |

Sources: [python/cutlass_library/sm90_utils.py:33-54](), [.gitignore:1-4]()

---

## Submission and Issue Management

### Issue Triage and Labeling

The repository uses GitHub Actions for automated triage and labeling. Issues and Pull Requests are automatically categorized based on content and activity.

```mermaid
graph LR
    subgraph "Issue_Ingestion"
        ["Issue_Opened"]
        ["Parse_Issue_Body"]
    end

    subgraph "Automated_Labeling"
        ["labeler.yml"]
        ["Map_Component_Labels"]
    end

    subgraph "Project_Assignment"
        ["new-issues-to-triage-projects.yml"]
        ["Assign_to_Needs_prioritizing"]
    end

    "Issue_Opened" --> "Parse_Issue_Body"
    "Parse_Issue_Body" --> "labeler.yml"
    "labeler.yml" --> "Map_Component_Labels"
    "Map_Component_Labels" --> "new-issues-to-triage-projects.yml"
    "new-issues-to-triage-projects.yml" --> "Assign_to_Needs_prioritizing"
```

**Figure: Issue Triage Workflow**

**Labeling Rules:**
- **Components:** Issues are automatically labeled by the `labeler.yml` workflow which triages pull requests. [.github/workflows/labeler.yml:1-12]()
- **Triage Status:** New issues are processed and tagged with `? - Needs Triage`. [.github/workflows/new-issues-to-triage-projects.yml:17-31]()
- **Stale Policy:** Issues with no activity for 30 days are labeled `inactive-30d`. After 90 days, they are labeled `inactive-90d`. [.github/workflows/stale.yml:11-32]()

Sources: [.github/workflows/labeler.yml:1-12](), [.github/workflows/stale.yml:11-32](), [.github/workflows/new-issues-to-triage-projects.yml:15-35]()

### Issue Templates

Contributors should use the appropriate template for their submission:
- **Documentation Request:** For reporting incorrect or missing documentation. [.github/ISSUE_TEMPLATE/documentation_request.md:10-36]()
- **Submit Question:** For general queries using the `[QST]` prefix. [.github/ISSUE_TEMPLATE/submit_question.md:1-11]()

---

## Coding Standards and Conventions

### License Headers

All files must include the BSD-3-Clause license header. The copyright year should be updated to include the current year (e.g., `2017 - 2026`).

Sources: [CONTRIBUTORS.md:175-176](), [python/cutlass_library/sm90_utils.py:3-4](), [include/cutlass/gemm/collective/sm90_mma_array_tma_gmma_ss_warpspecialized_fp8.hpp:2-3]()

### SM90/SM100 Kernel Enumeration

When contributing new kernels, especially for SM90+, developers should follow the "Global Level" generation pattern. This system uses a single integer to control multiple generator parameters (WGMMA shapes, cluster sizes, etc.).

**Global Level Mapping:**
- **WGMMA Level:** `global_level % 10` [python/cutlass_library/sm90_utils.py:90-91]()
- **MMA Multiplier Level:** `(global_level // 10) % 10` [python/cutlass_library/sm90_utils.py:94-95]()
- **Cluster Level:** `(global_level // 100) % 10` [python/cutlass_library/sm90_utils.py:98-99]()

Sources: [python/cutlass_library/sm90_utils.py:71-103]()

---

## Testing Requirements

### Unit Testing Strategy

New features must include unit tests. Tests should be added to the `test/unit/` directory. For SM90+ kernels, testing often involves verifying complex collective mainloops.

**Example: Collective MMA FP8 Test Configuration**
Collective components like `CollectiveMma` for SM90 FP8 require validation of:
- `MainloopPipeline` stages (e.g., `PipelineTmaAsync`). [include/cutlass/gemm/collective/sm90_mma_array_tma_gmma_ss_warpspecialized_fp8.hpp:115]()
- `SmemLayout` atom compatibility. [include/cutlass/gemm/collective/sm90_mma_array_tma_gmma_ss_warpspecialized_fp8.hpp:123-130]()
- `TMA_A` and `TMA_B` copy atom specifications using `make_tma_copy`. [include/cutlass/gemm/collective/sm90_mma_array_tma_gmma_ss_warpspecialized_fp8.hpp:151-163]()

Sources: [include/cutlass/gemm/collective/sm90_mma_array_tma_gmma_ss_warpspecialized_fp8.hpp:115-150]()

### Python Development and Testing

Python code should follow standard `__pycache__` exclusion rules. Package setup is handled via scripts in the `python/` directory.

Sources: [.gitignore:1-4]()

---

## Contributors

The project maintains a list of contributors in [CONTRIBUTORS.md](), categorized by their primary area of impact:
- **CUTLASS C++ Developers:** Core library and template developers. [CONTRIBUTORS.md:5-69]()
- **CUTLASS DSL Developers:** Python DSL and JIT infrastructure. [CONTRIBUTORS.md:73-110]()
- **CuTe Developers:** Core algebraic abstraction developers. [CONTRIBUTORS.md:115-118]()
- **Product Management:** Matthew Nicely. [CONTRIBUTORS.md:121-123]()

Sources: [CONTRIBUTORS.md:5-124]()

---

