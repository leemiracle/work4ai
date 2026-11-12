<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/alphafold3 · page 9 Development and Build · fetched 2026-10-26 -->

# Development and Build

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [pyproject.toml](pyproject.toml)
- [src/alphafold3/version.py](src/alphafold3/version.py)
- [uv.lock](uv.lock)

</details>



This document provides guidance for developers building, testing, and contributing to AlphaFold 3. It covers the build system architecture, dependency management, native extensions, and contribution workflows.

For installation instructions aimed at end users, see [Installation Guide](#2). For detailed build configuration and dependencies, see [Build System](#9.1). For CI/CD workflows and automated testing, see [CI/CD Pipeline](#9.2). For details on the C++ bindings and native modules, see [Native C++ Extensions](#9.3).

## Overview

AlphaFold 3 uses a hybrid build system that combines modern Python package management with C++ compilation for performance-critical components. The project is structured to support:

- **Local development** using `uv` for fast dependency resolution and environment management [pyproject.toml:38-44]().
- **C++ extensions** built with CMake and `scikit-build-core` for efficient structure parsing and biological data processing.
- **Continuous integration** through GitHub Actions for automated testing and validation.

The build process produces both Python packages and compiled C++ extensions, managed via `pyproject.toml` and `scikit-build-core` [pyproject.toml:1-9]().

**Sources:** [pyproject.toml:1-74](), [src/alphafold3/version.py:1-22]()

## Build System Architecture

```mermaid
graph TB
    subgraph "Source Code Space"
        [Python_Source] --> ["src/alphafold3/"]
        [Cpp_Extensions] --> ["src/alphafold3/*.cc"]
        [Build_Config] --> ["pyproject.toml"]
    end
    
    subgraph "Build Toolchain"
        ["scikit-build-core"] --> ["CMake >=3.28"]
        ["CMake >=3.28"] --> ["Ninja"]
        ["CMake >=3.28"] --> ["pybind11"]
    end
    
    subgraph "Dependency Space"
        ["uv"] --> ["uv.lock"]
        ["uv.lock"] --> ["Python Dependencies"]
    end
    
    subgraph "Build Outputs"
        ["Ninja"] --> ["cpp.so (Python Extension)"]
        ["Python_Source"] --> ["alphafold3 Wheel"]
        ["build_data script"] --> ["alphafold3.build_data:build_data"]
    end

    [Build_Config] -- "defines backend" --> ["scikit-build-core"]
    [uv.lock] -- "locks versions" --> ["Python Dependencies"]
```

**Diagram: Build System Architecture**

For detailed information on the build backend, `pyproject.toml` configuration, CMake integration, and dependency management via `uv`, see [Build System](#9.1).

**Sources:** [pyproject.toml:1-74](), [uv.lock:1-15]()

## CI/CD Pipeline

Continuous integration ensures that all contributions pass automated checks, code style guidelines, and regression tests. The pipeline relies on GitHub Actions to execute test suites across supported platforms.

For details on workflow definitions, test execution, and contribution guidelines, see [CI/CD Pipeline](#9.2).

**Sources:** [CONTRIBUTING.md:1-36]()

## Native C++ Extensions

AlphaFold 3 implements performance-critical routines in C++ and binds them to Python using `pybind11`. These include parsers for mmCIF and FASTA formats, MSA feature extractors, structural utilities, and secondary structure assignment (`mkdssp`).

For a comprehensive breakdown of the extension modules in `parsers/cpp` and `structure/cpp`, and how they are exposed through `cpp.cc`, see [Native C++ Extensions](#9.3).

**Sources:** [pyproject.toml:1-9]()

## Contributing

We welcome small patches related to bug fixes and documentation [CONTRIBUTING.md:3-4]().

### Contribution Rules
- **AI Generated Code**: Must be transparently labeled, manually reviewed, and locally tested before submission [CONTRIBUTING.md:7-18]().
- **CLA**: Contributions require a signed Contributor License Agreement via Google's CLA portal [CONTRIBUTING.md:19-30]().
- **Code Reviews**: All submissions require review via GitHub Pull Requests [CONTRIBUTING.md:31-36]().

**Sources:** [CONTRIBUTING.md:1-36]()

## Version Management

The version is centrally tracked in `src/alphafold3/version.py` [src/alphafold3/version.py:20-22]():

```python
__version__ = '3.0.4'
```

This version is dynamically utilized during packaging and build metadata generation via `setuptools_scm` and `scikit-build-core` [pyproject.toml:13, 64-67]().

**Sources:** [src/alphafold3/version.py:1-22](), [pyproject.toml:11-14, 64-67]()

---

