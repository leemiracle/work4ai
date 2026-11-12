<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/envlogger · page 5 Build System and Development Setup · fetched 2026-10-26 -->

# Build System and Development Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [WORKSPACE.bazel](WORKSPACE.bazel)
- [docker/Dockerfile](docker/Dockerfile)
- [envlogger/setup.py](envlogger/setup.py)

</details>



This document covers the build system architecture and development setup for EnvLogger, including both Python and C++ components. EnvLogger uses a hybrid build system combining Bazel for C++ compilation and native Python packaging with setuptools for distribution.

For detailed information about the Python package build process specifically, see [Python Package Build](#5.1). For Bazel workspace configuration details, see [Bazel Build Configuration](#5.2).

## Build System Architecture

EnvLogger employs a multi-layered build system that coordinates between Bazel (for C++ components) and Python setuptools (for package distribution). The system must handle cross-language compilation, protocol buffer generation, and complex dependency management.

### Build System Components

```mermaid
graph TB
    subgraph "Python Package Layer"
        setup_py["setup.py<br/>Python package definition"]
        build_py["_BuildPy<br/>Custom build command"]
        build_ext["_BuildExt<br/>Bazel integration"]
        generate_protos["_GenerateProtoFiles<br/>Protocol buffer compilation"]
    end
    
    subgraph "Bazel Build Layer"
        workspace["WORKSPACE.bazel<br/>Dependency definitions"]
        bazel_targets["Bazel BUILD targets<br/>C++ compilation"]
        bazel_extensions["BazelExtension<br/>C++ Python bindings"]
    end
    
    subgraph "External Dependencies"
        protobuf["com_google_protobuf"]
        riegeli["com_google_riegeli"]
        pybind11["pybind11"]
        abseil["com_google_absl"]
        xtensor["xtensor"]
    end
    
    subgraph "Generated Artifacts"
        proto_bindings["storage_pb2.py<br/>Python protocol buffers"]
        so_files["*.so files<br/>C++ extension modules"]
        python_package["envlogger Python package"]
    end
    
    setup_py --> build_py
    setup_py --> build_ext
    setup_py --> generate_protos
    
    build_ext --> bazel_targets
    build_ext --> bazel_extensions
    
    bazel_targets --> workspace
    workspace --> protobuf
    workspace --> riegeli
    workspace --> pybind11
    workspace --> abseil
    workspace --> xtensor
    
    generate_protos --> proto_bindings
    build_ext --> so_files
    
    proto_bindings --> python_package
    so_files --> python_package
```

Sources: [envlogger/setup.py:1-175](), [WORKSPACE.bazel:1-215]()

### Build Process Flow

The build process follows a specific sequence that ensures proper dependency resolution and artifact generation:

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant Setup as "setup.py"
    participant Bazel as "Bazel Build"
    participant Proto as "Protocol Buffers"
    participant Ext as "C++ Extensions"
    
    Dev->>Setup: "python setup.py build"
    Setup->>Proto: "run generate_protos command"
    Proto-->>Setup: "storage_pb2.py generated"
    
    Setup->>Bazel: "bazel build ..."
    Bazel->>Ext: "Compile C++ extensions"
    Note over Ext: "riegeli_dataset_reader.so<br/>riegeli_dataset_writer.so<br/>episode_info.so"
    Ext-->>Bazel: "Extension modules built"
    Bazel-->>Setup: "Shared libraries ready"
    
    Setup->>Setup: "Copy .so files to package"
    Setup-->>Dev: "Python package built"
```

Sources: [envlogger/setup.py:94-137]()

## Bazel Workspace Configuration

The `WORKSPACE.bazel` file defines the complete dependency graph for the project, including external libraries and build rules.

### Key External Dependencies

| Dependency | Purpose | Version/Commit |
|------------|---------|----------------|
| `com_google_protobuf` | Protocol buffer support | 3.21.9 |
| `com_google_riegeli` | High-performance data storage | b2210b97... |
| `com_google_absl` | Abseil C++ libraries | 20220623.1 |
| `pybind11` | Python-C++ bindings | 2.10.4 |
| `xtensor` | C++ tensor library | 54dbb822... |
| `com_google_googletest` | C++ testing framework | 1.12.1 |

Sources: [WORKSPACE.bazel:18-214]()

### Dependency Resolution Strategy

```mermaid
graph TD
    subgraph "Core Dependencies"
        protobuf["com_google_protobuf<br/>Protocol buffer compiler"]
        absl["com_google_absl<br/>Abseil C++ libraries"]
        gtest["com_google_googletest<br/>Testing framework"]
    end
    
    subgraph "Data Processing Dependencies"
        riegeli["com_google_riegeli<br/>Storage engine"]
        xtensor["xtensor<br/>Tensor operations"]
        xtl["xtl<br/>Tensor library support"]
    end
    
    subgraph "Compression Dependencies"
        zstd["net_zstd<br/>Zstandard compression"]
        brotli["org_brotli<br/>Brotli compression"]
        snappy["snappy<br/>Snappy compression"]
        zlib["zlib<br/>Zlib compression"]
    end
    
    subgraph "Python Integration"
        pybind11_rules["pybind11_bazel<br/>Build rules"]
        pybind11_lib["pybind11<br/>Binding library"]
        pybind11_proto["pybind11_protobuf<br/>Protocol buffer bindings"]
    end
    
    riegeli --> zstd
    riegeli --> brotli
    riegeli --> snappy
    riegeli --> zlib
    
    xtensor --> xtl
    
    pybind11_rules --> pybind11_lib
    pybind11_proto --> pybind11_lib
    pybind11_proto --> protobuf
    
    riegeli --> absl
    riegeli --> protobuf
```

Sources: [WORKSPACE.bazel:83-207]()

## Python Package Build System

The `setup.py` script implements a custom build system that integrates Bazel compilation with Python packaging.

### Custom Build Commands

The setup system defines several custom commands that extend the standard setuptools build process:

```mermaid
graph LR
    subgraph "setuptools Commands"
        build_py_cmd["build_py<br/>Python module compilation"]
        build_ext_cmd["build_ext<br/>C++ extension compilation"]
        generate_protos_cmd["generate_protos<br/>Protocol buffer generation"]
    end
    
    subgraph "Custom Command Classes"
        BuildPy["_BuildPy<br/>Extends build_py.build_py"]
        BuildExt["_BuildExt<br/>Extends build_ext.build_ext"]
        GenerateProtoFiles["_GenerateProtoFiles<br/>Custom command"]
    end
    
    subgraph "Bazel Integration"
        BazelExtension["BazelExtension<br/>Custom extension class"]
        bazel_build["bazel_build()<br/>Bazel execution"]
    end
    
    build_py_cmd --> BuildPy
    build_ext_cmd --> BuildExt
    generate_protos_cmd --> GenerateProtoFiles
    
    BuildPy --> GenerateProtoFiles
    BuildExt --> GenerateProtoFiles
    BuildExt --> BazelExtension
    BuildExt --> bazel_build
```

Sources: [envlogger/setup.py:38-137]()

### Bazel Extension Compilation

The system compiles three main C++ extensions as Bazel targets:

```mermaid
graph TB
    subgraph "Bazel Extension Targets"
        episode_info["//envlogger/backends/python:episode_info<br/>Episode metadata handling"]
        riegeli_reader["//envlogger/backends/python:riegeli_dataset_reader<br/>C++ data reading"]
        riegeli_writer["//envlogger/backends/python:riegeli_dataset_writer<br/>C++ data writing"]
    end
    
    subgraph "Build Process"
        bazel_bin["bazel-bin/<br/>Compiled artifacts"]
        so_files["*.so files<br/>Shared libraries"]
        python_modules["Python extension modules"]
    end
    
    subgraph "Package Structure"
        envlogger_pkg["envlogger/<br/>Python package"]
        backends_pkg["backends/<br/>Subpackage"]
        python_pkg["python/<br/>Extension modules"]
    end
    
    episode_info --> bazel_bin
    riegeli_reader --> bazel_bin
    riegeli_writer --> bazel_bin
    
    bazel_bin --> so_files
    so_files --> python_modules
    
    python_modules --> python_pkg
    python_pkg --> backends_pkg
    backends_pkg --> envlogger_pkg
```

Sources: [envlogger/setup.py:145-149](), [envlogger/setup.py:115-136]()

## Docker Development Environment

The project provides a containerized development environment for consistent builds across different platforms.

### Docker Build Configuration

```mermaid
graph TD
    subgraph "Base Environment"
        ubuntu["ubuntu:20.04<br/>Base OS"]
        timezone["TZ=America/Montreal<br/>Timezone setup"]
        packages["System packages<br/>git, curl, wget, gcc-9, g++-9"]
    end
    
    subgraph "Python Environment"
        python_version["Python 3.x<br/>Configurable via PY3_VERSION"]
        pip_install["pip installation<br/>Latest pip + setuptools"]
        python_packages["Python dependencies<br/>requirements.txt"]
    end
    
    subgraph "Build Tools"
        bazel_install["Bazel 6.2.1<br/>Build system"]
        compiler_setup["GCC/G++ 9<br/>C++ compiler"]
        alternatives["update-alternatives<br/>Tool version management"]
    end
    
    subgraph "EnvLogger Setup"
        source_copy["Copy source code<br/>ADD . /envlogger/"]
        workdir["WORKDIR /envlogger"]
        grpc_tools["grpcio-tools<br/>Protocol buffer compilation"]
    end
    
    ubuntu --> timezone
    ubuntu --> packages
    packages --> python_version
    python_version --> pip_install
    pip_install --> python_packages
    
    packages --> bazel_install
    packages --> compiler_setup
    compiler_setup --> alternatives
    
    python_packages --> grpc_tools
    grpc_tools --> source_copy
    source_copy --> workdir
```

Sources: [docker/Dockerfile:1-54]()

### Development Workflow

The Docker environment supports the complete development workflow:

1. **Environment Setup**: Creates a consistent Ubuntu 20.04 environment with all required dependencies
2. **Python Configuration**: Supports multiple Python versions (3.x) with configurable `PY3_VERSION`
3. **Build Tool Installation**: Installs Bazel 6.2.1 and configures GCC/G++ 9 as the default compilers
4. **Dependency Management**: Installs Python requirements and gRPC tools for protocol buffer compilation

## Development Setup Instructions

### Prerequisites

- **Operating System**: Ubuntu 20.04+ (or use Docker)
- **Python**: 3.8+ (3.10+ recommended)
- **Bazel**: 6.2.1+
- **Compiler**: GCC/G++ 9+
- **Dependencies**: `libgmp-dev` for mathematical operations

### Local Development Setup

1. **Install System Dependencies**:
   ```bash
   sudo apt install -y gcc-9 g++-9 libgmp-dev python3.10-dev
   ```

2. **Install Bazel**:
   ```bash
   wget https://github.com/bazelbuild/bazel/releases/download/6.2.1/bazel-6.2.1-linux-x86_64
   chmod +x bazel-6.2.1-linux-x86_64
   sudo mv bazel-6.2.1-linux-x86_64 /usr/bin/bazel
   ```

3. **Build the Package**:
   ```bash
   cd envlogger
   python setup.py build
   ```

### Docker Development Setup

1. **Build Docker Image**:
   ```bash
   docker build -t envlogger-dev -f docker/Dockerfile .
   ```

2. **Run Development Container**:
   ```bash
   docker run -it -v $(pwd):/envlogger envlogger-dev
   ```

Sources: [docker/Dockerfile:19-53](), [envlogger/setup.py:104-113]()

---

