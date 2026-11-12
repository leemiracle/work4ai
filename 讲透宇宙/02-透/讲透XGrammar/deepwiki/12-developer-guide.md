> 来源: [https://deepwiki.com/mlc-ai/xgrammar/12-developer-guide](https://deepwiki.com/mlc-ai/xgrammar/12-developer-guide)
> DeepWiki mlc-ai/xgrammar | Last indexed: 7 March 2026 (c30554

# Developer Guide

  Relevant source files 
 - [.pre-commit-config.yaml](https://github.com/mlc-ai/xgrammar/blob/c30554f7/.pre-commit-config.yaml)
 - [CMakeLists.txt](https://github.com/mlc-ai/xgrammar/blob/c30554f7/CMakeLists.txt)
 - [pyproject.toml](https://github.com/mlc-ai/xgrammar/blob/c30554f7/pyproject.toml)
 - [scripts/release_new_version.sh](https://github.com/mlc-ai/xgrammar/blob/c30554f7/scripts/release_new_version.sh)
 
  This guide provides essential information for developers contributing to or extending xgrammar. It covers the development environment setup, build system configuration, testing practices, code quality standards, and contribution workflows. The focus is on the practical aspects of working with the codebase, including both C++ and Python components.

 For detailed API documentation, see [Python API Reference](https://deepwiki.com/mlc-ai/xgrammar/3-python-api-reference). For C++ implementation details, see [C++ Implementation Details](https://deepwiki.com/mlc-ai/xgrammar/11-c++-implementation-details). For system architecture overview, see [System Architecture](https://deepwiki.com/mlc-ai/xgrammar/10-system-architecture).

 
## Development Environment Overview

 The xgrammar project uses a hybrid Python-C++ architecture with a sophisticated build system that orchestrates both ecosystems. The development workflow involves editing source code, building the project, running tests, and ensuring code quality through automated checks.

 
### Development Workflow Diagram

 
```

```

 Sources: [pyproject.toml1-161](https://github.com/mlc-ai/xgrammar/blob/c30554f7/pyproject.toml#L1-L161) [CMakeLists.txt1-145](https://github.com/mlc-ai/xgrammar/blob/c30554f7/CMakeLists.txt#L1-L145) [.pre-commit-config.yaml1-76](https://github.com/mlc-ai/xgrammar/blob/c30554f7/.pre-commit-config.yaml#L1-L76)

 
## Quick Setup for Developers

 
### Prerequisites

 The following tools and dependencies are required:

 
| Component | Requirement | Purpose |
|---|---|---|
| Python | >=3.8, <4 | Runtime and bindings |
| CMake | >=3.18 | C++ build system |
| C++ Compiler | C++17 support | Compile core library |
| scikit-build-core | >=0.10.0 | Python build backend |
| nanobind | ==2.5.0 | Python-C++ bindings |

 Sources: [pyproject.toml16](https://github.com/mlc-ai/xgrammar/blob/c30554f7/pyproject.toml#L16-L16) [pyproject.toml44-45](https://github.com/mlc-ai/xgrammar/blob/c30554f7/pyproject.toml#L44-L45) [CMakeLists.txt1-2](https://github.com/mlc-ai/xgrammar/blob/c30554f7/CMakeLists.txt#L1-L2) [CMakeLists.txt30-31](https://github.com/mlc-ai/xgrammar/blob/c30554f7/CMakeLists.txt#L30-L31)

 
### Development Installation

 For local development with editable installation:

 
```

```

 The editable install rebuilds the C++ extension automatically when source files change, as configured in [pyproject.toml98-99](https://github.com/mlc-ai/xgrammar/blob/c30554f7/pyproject.toml#L98-L99)

 Sources: [pyproject.toml30-40](https://github.com/mlc-ai/xgrammar/blob/c30554f7/pyproject.toml#L30-L40) [pyproject.toml97-99](https://github.com/mlc-ai/xgrammar/blob/c30554f7/pyproject.toml#L97-L99)

 
### Directory Structure

 
```
xgrammar/
├── cpp/                    # C++ source code
│   ├── *.cc               # Implementation files
│   └── nanobind/          # Python binding code
├── include/xgrammar/      # C++ headers (public API)
├── python/xgrammar/       # Python package
│   └── *.py               # Python modules
├── tests/                 # Test suites
│   ├── *.py               # Python tests
│   └── cpp/               # C++ tests
├── cmake/                 # CMake modules
├── 3rdparty/             # Third-party dependencies
├── CMakeLists.txt        # Main CMake configuration
├── pyproject.toml        # Python project configuration
└── .pre-commit-config.yaml  # Code quality hooks
```

 Sources: [CMakeLists.txt77-78](https://github.com/mlc-ai/xgrammar/blob/c30554f7/CMakeLists.txt#L77-L78) [pyproject.toml63-93](https://github.com/mlc-ai/xgrammar/blob/c30554f7/pyproject.toml#L63-L93)

 
## Build System Architecture

 The build system uses `scikit-build-core` as the Python build backend, which orchestrates CMake to compile C++ code and create Python wheels. This enables seamless integration between Python packaging and native code compilation.

 
### Build Pipeline

 
```

```

 Sources: [CMakeLists.txt1-111](https://github.com/mlc-ai/xgrammar/blob/c30554f7/CMakeLists.txt#L1-L111) [pyproject.toml43-65](https://github.com/mlc-ai/xgrammar/blob/c30554f7/pyproject.toml#L43-L65)

 
### CMake Build Options

 The following CMake options control build behavior, defined in [CMakeLists.txt17-28](https://github.com/mlc-ai/xgrammar/blob/c30554f7/CMakeLists.txt#L17-L28):

 
| Option | Default | Description |
|---|---|---|
| XGRAMMAR_BUILD_PYTHON_BINDINGS | ON | Build Python bindings with nanobind |
| XGRAMMAR_BUILD_CXX_TESTS | OFF | Build C++ unit tests with GoogleTest |
| XGRAMMAR_ENABLE_CPPTRACE | OFF | Enable C++ stack traces (Linux only) |
| XGRAMMAR_ENABLE_COVERAGE | OFF | Enable code coverage with gcov |
| XGRAMMAR_ENABLE_INTERNAL_CHECK | OFF | Enable internal assertion checks |
| XGRAMMAR_CUDA_ARCHITECTURES | native | CUDA architecture targets |

 These options can be set via a `config.cmake` file in the build directory, project root, or `cmake/` directory, as detected in [CMakeLists.txt4-15](https://github.com/mlc-ai/xgrammar/blob/c30554f7/CMakeLists.txt#L4-L15)

 
### Compilation Flags

 The project uses strict compilation flags configured in [CMakeLists.txt48-71](https://github.com/mlc-ai/xgrammar/blob/c30554f7/CMakeLists.txt#L48-L71):

 **For non-MSVC compilers:**

 
 - `-Wall -Wextra -Werror`: Enable all warnings and treat them as errors
 - `-Wno-pedantic -Wno-unused-parameter`: Suppress specific warnings
 - `-Woverloaded-virtual`: Warn about virtual function hiding
 - `-flto=auto`: Link-time optimization (except RISC-V)
 - `-O3`: Aggressive optimization for non-Debug builds
 
 **Build type defaults:**

 
 - Default: `RelWithDebInfo` (optimized with debug info)
 - Configurable via `CMAKE_BUILD_TYPE`
 
 Sources: [CMakeLists.txt34-71](https://github.com/mlc-ai/xgrammar/blob/c30554f7/CMakeLists.txt#L34-L71)

 
### Source File Organization

 The C++ library is compiled from sources gathered via glob pattern in [CMakeLists.txt77-78](https://github.com/mlc-ai/xgrammar/blob/c30554f7/CMakeLists.txt#L77-L78):

 
```

```

 This collects all `.cc` files in `cpp/` except those in `cpp/nanobind/`, which are compiled separately for the Python bindings.

 The static library includes third-party dependencies:

 
 - **picojson**: JSON parsing ([CMakeLists.txt73-75](https://github.com/mlc-ai/xgrammar/blob/c30554f7/CMakeLists.txt#L73-L75))
 - **dlpack**: Tensor interchange format ([CMakeLists.txt74-75](https://github.com/mlc-ai/xgrammar/blob/c30554f7/CMakeLists.txt#L74-L75))
 - **cpptrace** (optional): Stack trace support ([CMakeLists.txt85-91](https://github.com/mlc-ai/xgrammar/blob/c30554f7/CMakeLists.txt#L85-L91))
 
 Sources: [CMakeLists.txt73-91](https://github.com/mlc-ai/xgrammar/blob/c30554f7/CMakeLists.txt#L73-L91)

 
## Testing Infrastructure

 
### Python Testing with pytest

 The project uses `pytest` for Python tests, configured in [pyproject.toml101-104](https://github.com/mlc-ai/xgrammar/blob/c30554f7/pyproject.toml#L101-L104):

 
```

```

 **Test execution:**

 
```

```

 The `hf_token_required` marker is used for tests that require HuggingFace API access, allowing them to be skipped in CI environments without tokens.

 Sources: [pyproject.toml101-104](https://github.com/mlc-ai/xgrammar/blob/c30554f7/pyproject.toml#L101-L104)

 
### C++ Testing with GoogleTest

 C++ unit tests are optional and disabled by default. Enable them with:

 
```

```

 The test infrastructure is configured in [CMakeLists.txt113-125](https://github.com/mlc-ai/xgrammar/blob/c30554f7/CMakeLists.txt#L113-L125):

 
```

```

 C++ tests are automatically discovered and can be run with `ctest`.

 Sources: [CMakeLists.txt113-125](https://github.com/mlc-ai/xgrammar/blob/c30554f7/CMakeLists.txt#L113-L125)

 
### Code Coverage

 Code coverage can be enabled via [CMakeLists.txt127-138](https://github.com/mlc-ai/xgrammar/blob/c30554f7/CMakeLists.txt#L127-L138):

 
```

```

 This adds gcov instrumentation flags and links against the coverage library. Coverage reports can be generated using standard gcov/lcov tools.

 Sources: [CMakeLists.txt127-138](https://github.com/mlc-ai/xgrammar/blob/c30554f7/CMakeLists.txt#L127-L138)

 
## Code Quality and Formatting

 
### Pre-commit Hook System

 The project uses `pre-commit` for automated code formatting and quality checks. The configuration in [.pre-commit-config.yaml1-76](https://github.com/mlc-ai/xgrammar/blob/c30554f7/.pre-commit-config.yaml#L1-L76) includes:

 
| Tool | Purpose | Files |
|---|---|---|
| black | Python code formatter | *.py |
| isort | Python import sorter | *.py |
| clang-format | C++ code formatter | *.cc, *.h, *.cu |
| cmake-format | CMake formatter | CMakeLists.txt |
| yamlfmt | YAML formatter | *.yaml, *.yml |
| taplo-format | TOML formatter | *.toml |

 **Standard hooks** from `pre-commit-hooks` check for:

 
 - Large files
 - Merge conflicts
 - Trailing whitespace
 - End-of-file fixers
 - Mixed line endings
 
 Sources: [.pre-commit-config.yaml21-76](https://github.com/mlc-ai/xgrammar/blob/c30554f7/.pre-commit-config.yaml#L21-L76)

 
### Installing Pre-commit Hooks

 
```

```

 After installation, hooks run automatically on `git commit`, formatting code before it's committed.

 Sources: [.pre-commit-config.yaml1-19](https://github.com/mlc-ai/xgrammar/blob/c30554f7/.pre-commit-config.yaml#L1-L19)

 
### Python Code Style Configuration

 Python formatting is configured via `pyproject.toml`:

 **Black formatter** ([pyproject.toml124-127](https://github.com/mlc-ai/xgrammar/blob/c30554f7/pyproject.toml#L124-L127)):

 
```

```

 **isort configuration** ([pyproject.toml129-134](https://github.com/mlc-ai/xgrammar/blob/c30554f7/pyproject.toml#L129-L134)):

 
```

```

 **Ruff linter** ([pyproject.toml109-122](https://github.com/mlc-ai/xgrammar/blob/c30554f7/pyproject.toml#L109-L122)):

 
 - Selects rules: `C` (complexity), `E` (errors), `F` (pyflakes), `W` (warnings)
 - Ignores: `C901` (complexity), `E501` (line length), `E741` (ambiguous names)
 - Special per-file ignores for `__init__.py` and test files
 
 Sources: [pyproject.toml109-134](https://github.com/mlc-ai/xgrammar/blob/c30554f7/pyproject.toml#L109-L134)

 
### C++ Code Style

 C++ code is formatted with `clang-format` version 19.1.7, configured in [.pre-commit-config.yaml52-58](https://github.com/mlc-ai/xgrammar/blob/c30554f7/.pre-commit-config.yaml#L52-L58):

 
```

```

 The format excludes third-party code and generated files.

 Sources: [.pre-commit-config.yaml52-58](https://github.com/mlc-ai/xgrammar/blob/c30554f7/.pre-commit-config.yaml#L52-L58)

 
## Cross-Platform Wheel Building

 
### cibuildwheel Configuration

 The project uses `cibuildwheel` to build wheels for multiple platforms, configured in [pyproject.toml136-161](https://github.com/mlc-ai/xgrammar/blob/c30554f7/pyproject.toml#L136-L161):

 
```

```

 Sources: [pyproject.toml136-161](https://github.com/mlc-ai/xgrammar/blob/c30554f7/pyproject.toml#L136-L161)

 
### Platform-Specific Configuration

 **Linux** ([pyproject.toml152-153](https://github.com/mlc-ai/xgrammar/blob/c30554f7/pyproject.toml#L152-L153)):

 
 - Architectures: x86_64, aarch64
 - manylinux compatibility
 
 **macOS** ([pyproject.toml155-157](https://github.com/mlc-ai/xgrammar/blob/c30554f7/pyproject.toml#L155-L157)):

 
 - Architectures: x86_64, arm64
 - Deployment target: macOS 10.14
 - Note: Python 3.13 on x86_64 is skipped due to PyTorch compatibility
 
 **Windows** ([pyproject.toml159-160](https://github.com/mlc-ai/xgrammar/blob/c30554f7/pyproject.toml#L159-L160)):

 
 - Architecture: AMD64 only
 
 
### Skipped Builds

 The following builds are skipped ([pyproject.toml141-147](https://github.com/mlc-ai/xgrammar/blob/c30554f7/pyproject.toml#L141-L147)):

 
 - Python 3.6, 3.7, 3.8 (too old)
 - musllinux (not supported)
 - cp313-macosx_x86_64 (PyTorch wheels unavailable)
 
 
### Test Command

 Each wheel is tested after building with:

 
```

```

 This ensures wheels are functional before distribution.

 Sources: [pyproject.toml149-150](https://github.com/mlc-ai/xgrammar/blob/c30554f7/pyproject.toml#L149-L150)

 
## Release Process

 
### Versioning

 The project version is defined in [pyproject.toml3](https://github.com/mlc-ai/xgrammar/blob/c30554f7/pyproject.toml#L3-L3):

 
```

```

 Version numbers follow semantic versioning principles.

 
### Release Workflow

 The release process is handled by [scripts/release_new_version.sh1-18](https://github.com/mlc-ai/xgrammar/blob/c30554f7/scripts/release_new_version.sh#L1-L18):

 
```

```

 **Release steps:**

 
 - Update version in `pyproject.toml`
 - Run `./scripts/release_new_version.sh v0.1.X`
 - Script creates and pushes git tag
 - CI builds wheels automatically for the tag
 - Wheels are uploaded to PyPI
 
 Sources: [scripts/release_new_version.sh1-18](https://github.com/mlc-ai/xgrammar/blob/c30554f7/scripts/release_new_version.sh#L1-L18) [pyproject.toml3](https://github.com/mlc-ai/xgrammar/blob/c30554f7/pyproject.toml#L3-L3)

 
### Distribution Configuration

 Source distributions (sdist) include specific files defined in [pyproject.toml67-93](https://github.com/mlc-ai/xgrammar/blob/c30554f7/pyproject.toml#L67-L93):

 **Included:**

 
 - Build files: CMakeLists.txt, cmake/, pyproject.toml
 - Source code: cpp/, include/, python/xgrammar/
 - Third-party: 3rdparty/
 - Documentation: docs/, LICENSE, README.md
 - Tests: tests/
 
 **Excluded:**

 
 - Version control: .git, .github
 - Build artifacts: **pycache**, *.pyc, build, dist
 
 Sources: [pyproject.toml67-95](https://github.com/mlc-ai/xgrammar/blob/c30554f7/pyproject.toml#L67-L95)

 
## Development Best Practices

 
### Compilation Checks

 The project enforces strict compilation standards:

 
 - **Warning-free compilation**: All warnings are treated as errors via `-Werror`
 - **Platform-specific handling**: Special cases for RISC-V and PowerPC architectures
 - **Link-time optimization**: Enabled via `-flto=auto` for most platforms
 
 Enable internal checks during development:

 
```

```

 This activates additional assertion checks in the C++ code ([CMakeLists.txt140-144](https://github.com/mlc-ai/xgrammar/blob/c30554f7/CMakeLists.txt#L140-L144)).

 Sources: [CMakeLists.txt48-71](https://github.com/mlc-ai/xgrammar/blob/c30554f7/CMakeLists.txt#L48-L71) [CMakeLists.txt140-144](https://github.com/mlc-ai/xgrammar/blob/c30554f7/CMakeLists.txt#L140-L144)

 
### Debugging Support

 For debugging with stack traces on Linux:

 
```

```

 This links against the cpptrace library and enables debug symbols ([CMakeLists.txt85-91](https://github.com/mlc-ai/xgrammar/blob/c30554f7/CMakeLists.txt#L85-L91)).

 Sources: [CMakeLists.txt85-91](https://github.com/mlc-ai/xgrammar/blob/c30554f7/CMakeLists.txt#L85-L91)

 
### Editable Installation

 For active development, use editable installation ([pyproject.toml97-99](https://github.com/mlc-ai/xgrammar/blob/c30554f7/pyproject.toml#L97-L99)):

 
```

```

 With configuration:

 
```

```

 This automatically rebuilds C++ extensions when source files change.

 Sources: [pyproject.toml97-99](https://github.com/mlc-ai/xgrammar/blob/c30554f7/pyproject.toml#L97-L99)

 
### Dependency Management

 **Runtime dependencies** ([pyproject.toml17-24](https://github.com/mlc-ai/xgrammar/blob/c30554f7/pyproject.toml#L17-L24)):

 
 - `pydantic`: Schema validation
 - `torch>=1.10.0`: Tensor operations and DLPack support
 - `transformers>=4.38.0`: Tokenizer integration
 - `triton`: GPU kernels (Linux x86_64 only)
 - `numpy`: Array operations
 - `typing-extensions>=4.9.0`: Type hints
 
 **Test dependencies** ([pyproject.toml31-40](https://github.com/mlc-ai/xgrammar/blob/c30554f7/pyproject.toml#L31-L40)):

 
 - `huggingface-hub[cli]`: Model downloads
 - `protobuf`: Serialization
 - `pytest`: Test framework
 - `sentencepiece`, `tiktoken`: Tokenizer libraries
 - Platform-specific: `transformers<4.50.0` on macOS
 
 Sources: [pyproject.toml17-40](https://github.com/mlc-ai/xgrammar/blob/c30554f7/pyproject.toml#L17-L40)

 
## Contributing Workflow

 
### Standard Workflow

 
 - **Fork and clone** the repository
 - **Create feature branch**: `git checkout -b feature-name`
 - **Make changes** to Python or C++ code
 - **Run pre-commit checks**: `pre-commit run -a`
 - **Run tests**: `pytest tests`
 - **Commit changes**: Pre-commit hooks run automatically
 - **Push and create pull request**
 
 
### Code Organization Principles

 
 - **Python code**: High-level API, user-facing interfaces
 - **C++ code**: Performance-critical algorithms, core data structures
 - **Bindings**: Minimal glue code in `cpp/nanobind/`
 - **Tests**: Co-located with implementation (`tests/` mirrors `python/`)
 
 
### Pull Request Checklist

 
 - Code follows style guidelines (enforced by pre-commit)
 - Tests pass locally
 - New functionality includes tests
 - Documentation updated if needed
 - Commit messages are descriptive
 - No merge conflicts with main branch
 
 For more detailed information on specific subsystems, see:

 
 - Build system details: [Build System and Configuration](https://deepwiki.com/mlc-ai/xgrammar/12.1-build-system-and-configuration)
 - Testing practices: [Testing Framework and Practices](https://deepwiki.com/mlc-ai/xgrammar/12.3-testing-framework-and-practices)
 - Code quality tools: [Code Quality and Pre-commit Hooks](https://deepwiki.com/mlc-ai/xgrammar/12.4-code-quality-and-pre-commit-hooks)
 - Packaging: [Cross-Platform Wheel Building](https://deepwiki.com/mlc-ai/xgrammar/12.5-cross-platform-wheel-building)
 
 Sources: [pyproject.toml1-161](https://github.com/mlc-ai/xgrammar/blob/c30554f7/pyproject.toml#L1-L161) [CMakeLists.txt1-145](https://github.com/mlc-ai/xgrammar/blob/c30554f7/CMakeLists.txt#L1-L145) [.pre-commit-config.yaml1-76](https://github.com/mlc-ai/xgrammar/blob/c30554f7/.pre-commit-config.yaml#L1-L76) [scripts/release_new_version.sh1-18](https://github.com/mlc-ai/xgrammar/blob/c30554f7/scripts/release_new_version.sh#L1-L18)
