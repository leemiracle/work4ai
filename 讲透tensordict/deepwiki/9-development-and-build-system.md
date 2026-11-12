<!-- source: DeepWiki mcp.deepwiki.com · repo pytorch/tensordict · page 9 Development and Build System · fetched 2026-10-21 -->

# Development and Build System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/benchmarks.yml](.github/workflows/benchmarks.yml)
- [.github/workflows/benchmarks_pr.yml](.github/workflows/benchmarks_pr.yml)
- [.github/workflows/nightly_build.yml](.github/workflows/nightly_build.yml)
- [.gitignore](.gitignore)
- [README.md](README.md)
- [setup.py](setup.py)
- [version.txt](version.txt)

</details>



This document describes the development, build, and continuous integration (CI) infrastructure for the TensorDict codebase. It covers the build system, C++ extension compilation, versioning, and the CI/CD pipeline, including nightly builds, wheel packaging, and performance benchmarking.

**Scope:**  
- How the codebase is built and packaged (Python and C++ components)
- How versioning is managed for releases and nightly builds
- How CI/CD workflows are structured for testing, building, and publishing
- How continuous benchmarking is integrated

For details on the C++ extension build process, see [Build System and C++ Extensions](#9.1).  
For information about the test and benchmark strategy, see [Testing Strategy and Benchmarks](#9.3).  
For the release and CI/CD process, see [CI/CD Pipeline and Release Process](#9.2).

---

## 1. Overview of the Build and Development Infrastructure

TensorDict uses a hybrid build system combining Python (setuptools) and C++ (CMake) components. The repository is designed for cross-platform compatibility (Linux, macOS, Windows) and supports multiple Python versions (3.9–3.14). The build system is tightly integrated with GitHub Actions for automated testing, packaging, and publishing.

### Diagram: "Build and Development System Overview"

```mermaid
graph LR
    "tensordict/csrc"["tensordict/csrc [C++ sources]"]
    "tensordict/*.py"["tensordict/*.py [Python sources]"]
    "tensordict/*.pyi"["tensordict/*.pyi [Type stubs]"]
    "setup.py"["setup.py"]
    "pyproject.toml"["pyproject.toml"]
    "CMake"["CMake"]
    "setuptools"["setuptools"]
    "Wheel"["dist/*.whl"]
    "GitHubActions"["GitHub Actions"]
    "test/*.py"["test/*.py [Unit tests]"]
    "benchmarks/"["benchmarks/ [Benchmarks]"]
    "PyPI"["PyPI"]
    "gh-pages"["gh-pages [Benchmark results]"]

    "tensordict/csrc" --> "CMake"
    "CMake" --> "setup.py"
    "tensordict/*.py" --> "setup.py"
    "tensordict/*.pyi" --> "setup.py"
    "setup.py" --> "setuptools"
    "pyproject.toml" --> "setuptools"
    "setuptools" --> "Wheel"
    "Wheel" --> "PyPI"
    "GitHubActions" --> "setup.py"
    "GitHubActions" --> "test/*.py"
    "GitHubActions" --> "benchmarks/"
    "benchmarks/" --> "gh-pages"
```
Sources: [setup.py](), [pyproject.toml](), [.github/workflows/nightly_build.yml](), [.github/workflows/benchmarks.yml]()

---

## 2. Build System Components

### 2.1 Python Packaging and Metadata

- **`pyproject.toml`** defines the build system requirements, project metadata, dependencies, and optional dependencies for testing, HDF5 support, development, and type checking.
- **`setup.py`** orchestrates the build, integrating CMake for C++ extension compilation and setuptools for Python packaging.
- **Type stubs** (`*.pyi`) are included for IDE and type checker support.

#### Table: Key Build Files

| File                  | Purpose                                                      |
|-----------------------|--------------------------------------------------------------|
| `pyproject.toml`      | Build system, dependencies, project metadata                 |
| `setup.py`            | Build script, C++ extension integration, version management  |
| `tensordict/csrc/`    | C++ source code for extensions                              |
| `tensordict/*.py`     | Python source code                                           |
| `tensordict/*.pyi`    | Type stubs for static analysis                              |

Sources: [pyproject.toml](), [setup.py]()

### 2.2 C++ Extension Build Process

- C++ extensions are located in `tensordict/csrc/`.
- The build process uses a custom `CMakeExtension` and `CMakeBuild` class in `setup.py` to invoke CMake and build the shared library.
- The extension is named `tensordict._C` and is built as part of the Python package.

#### Diagram: "C++ Extension Build Flow"

```mermaid
flowchart TD
    "setup.py"["setup.py"]
    "CMakeExtension"["CMakeExtension (setup.py)"]
    "CMakeBuild"["CMakeBuild (setup.py)"]
    "tensordict/csrc"["tensordict/csrc [C++ sources]"]
    "cmake"["cmake"]
    "build_ext"["build_ext"]
    "tensordict/_C.so"["tensordict/_C.so"]

    "setup.py" --> "CMakeExtension"
    "CMakeExtension" --> "CMakeBuild"
    "CMakeBuild" --> "cmake"
    "cmake" --> "tensordict/csrc"
    "cmake" --> "tensordict/_C.so"
    "CMakeBuild" --> "build_ext"
    "build_ext" --> "tensordict/_C.so"
```
Sources: [setup.py:49-89](), [tensordict/csrc/]()

---

## 3. Versioning Strategy

TensorDict uses a dynamic versioning scheme to distinguish between stable releases and nightly/development builds.

- **Stable releases**: Use a static version from `version.txt` or a base version variable.
- **Nightly/development builds**: Use a version string that encodes the base version, commit count, commit hash, and date (e.g., `0.10.0.dev123+gabcdef123.d20240601`).

Versioning is managed by:
- Environment variable `SETUPTOOLS_SCM_PRETEND_VERSION`
- Scripts: `.github/scripts/version_script.sh` (Linux/macOS), `.github/scripts/version_script.bat` (Windows)
- Integration with setuptools_scm for version propagation

#### Table: Versioning Artifacts

| File/Script                              | Role in Versioning                                      |
|-------------------------------------------|---------------------------------------------------------|
| `.github/scripts/version_script.sh`       | Sets version for CI builds (Linux/macOS)                |
| `.github/scripts/version_script.bat`      | Sets version for CI builds (Windows)                    |
| `version.txt`                            | Stores base version for releases                        |
| `SETUPTOOLS_SCM_PRETEND_VERSION`         | Environment variable for version override               |
| `pyproject.toml` `[tool.setuptools_scm]` | Configures versioning scheme for setuptools_scm         |

Sources: [.github/scripts/version_script.sh](), [.github/scripts/version_script.bat](), [pyproject.toml:74-79](), [setup.py:95-108]()

---

## 4. Continuous Integration and Delivery (CI/CD)

TensorDict uses GitHub Actions workflows for automated testing, building, packaging, and publishing. The CI/CD system is designed for cross-platform and multi-version support.

### 4.1 Nightly Build and Release Workflow

- **Nightly builds** are triggered on the `nightly` branch, on a schedule, or manually.
- Wheels are built for Linux, macOS, and Windows, across Python 3.9–3.14.
- Wheels are tested, and if successful, uploaded to PyPI as `tensordict-nightly`.

#### Diagram: "Nightly Build and Release Workflow"

```mermaid
flowchart TD
    "GitHubActions"["GitHub Actions"]
    "nightly_build.yml"[".github/workflows/nightly_build.yml"]
    "build-wheel-unix"["build-wheel-unix"]
    "test-wheel-unix"["test-wheel-unix"]
    "upload-wheel-unix"["upload-wheel-unix"]
    "build-wheel-windows"["build-wheel-windows"]
    "test-wheel-windows"["test-wheel-windows"]
    "upload-wheel-windows"["upload-wheel-windows"]
    "PyPI"["PyPI (tensordict-nightly)"]

    "GitHubActions" --> "nightly_build.yml"
    "nightly_build.yml" --> "build-wheel-unix"
    "nightly_build.yml" --> "build-wheel-windows"
    "build-wheel-unix" --> "test-wheel-unix"
    "test-wheel-unix" --> "upload-wheel-unix"
    "build-wheel-windows" --> "test-wheel-windows"
    "test-wheel-windows" --> "upload-wheel-windows"
    "upload-wheel-unix" --> "PyPI"
    "upload-wheel-windows" --> "PyPI"
```
Sources: [.github/workflows/nightly_build.yml]()

### 4.2 Benchmarking and Performance Regression

- Benchmarks are run continuously on both CPU and GPU using dedicated workflows.
- Results are uploaded as artifacts and published to the `gh-pages` branch for tracking.
- Pull requests can trigger benchmarks and receive performance comparisons as comments.

#### Diagram: "Benchmarking Workflow"

```mermaid
flowchart TD
    "GitHubActions"["GitHub Actions"]
    "benchmarks.yml"[".github/workflows/benchmarks.yml"]
    "benchmarks_pr.yml"[".github/workflows/benchmarks_pr.yml"]
    "benchmarks/"["benchmarks/"]
    "pytest-benchmark"["pytest-benchmark"]
    "output.json"["output.json"]
    "gh-pages"["gh-pages"]

    "GitHubActions" --> "benchmarks.yml"
    "GitHubActions" --> "benchmarks_pr.yml"
    "benchmarks.yml" --> "benchmarks/"
    "benchmarks_pr.yml" --> "benchmarks/"
    "benchmarks/" --> "pytest-benchmark"
    "pytest-benchmark" --> "output.json"
    "output.json" --> "gh-pages"
```
Sources: [.github/workflows/benchmarks.yml](), [.github/workflows/benchmarks_pr.yml]()

---

## 5. Build and Test Matrix

TensorDict is built and tested across the following axes:

| OS            | Python Versions         | CUDA Support | Wheels Built | Wheels Tested | Published |
|---------------|------------------------|--------------|--------------|--------------|-----------|
| Ubuntu 22.04  | 3.9, 3.10, 3.11, 3.12, 3.13, 3.14 | CPU          | Yes          | Yes          | Yes (nightly) |
| macOS         | 3.9, 3.10, 3.11, 3.12, 3.13, 3.14 | CPU          | Yes          | Yes          | Yes (nightly) |
| Windows       | 3.9, 3.10, 3.11, 3.12, 3.13, 3.14 | CPU          | Yes          | Yes          | Yes (nightly) |

Sources: [.github/workflows/nightly_build.yml]()

---

## 6. Clean and Editable Builds

- The `clean` command in `setup.py` removes build artifacts and compiled extensions.
- Editable installs (`pip install -e .`) are supported and place the extension in the source directory.

Sources: [setup.py:32-47]()

---

## 7. Build System and CI/CD Code Entities

### Diagram: "Mapping Build System Entities to Code"

```mermaid
flowchart TD
    "setup.py"["setup.py"]
    "CMakeExtension"["CMakeExtension (setup.py)"]
    "CMakeBuild"["CMakeBuild (setup.py)"]
    "clean"["clean (setup.py)"]
    "pyproject.toml"["pyproject.toml"]
    "version_script.sh"[".github/scripts/version_script.sh"]
    "version_script.bat"[".github/scripts/version_script.bat"]
    "nightly_build.yml"[".github/workflows/nightly_build.yml"]
    "benchmarks.yml"[".github/workflows/benchmarks.yml"]
    "benchmarks_pr.yml"[".github/workflows/benchmarks_pr.yml"]

    "setup.py" --> "CMakeExtension"
    "setup.py" --> "CMakeBuild"
    "setup.py" --> "clean"
    "pyproject.toml" --> "setup.py"
    "version_script.sh" --> "nightly_build.yml"
    "version_script.bat" --> "nightly_build.yml"
    "nightly_build.yml" --> "benchmarks.yml"
    "nightly_build.yml" --> "benchmarks_pr.yml"
```
Sources: [setup.py](), [pyproject.toml](), [.github/scripts/version_script.sh](), [.github/scripts/version_script.bat](), [.github/workflows/nightly_build.yml](), [.github/workflows/benchmarks.yml](), [.github/workflows/benchmarks_pr.yml]()

---

## 8. Summary

The TensorDict development and build system is designed for robust, cross-platform, and automated packaging and testing. It leverages a combination of Python and C++ build tools, dynamic versioning, and a comprehensive CI/CD pipeline to ensure code quality and performance.

For more details on specific subsystems:
- [Build System and C++ Extensions](#9.1)
- [CI/CD Pipeline and Release Process](#9.2)
- [Testing Strategy and Benchmarks](#9.3)

---

**Sources:**  
[setup.py](), [pyproject.toml](), [.github/scripts/version_script.sh](), [.github/scripts/version_script.bat](), [.github/workflows/nightly_build.yml](), [.github/workflows/benchmarks.yml](), [.github/workflows/benchmarks_pr.yml]()

---

