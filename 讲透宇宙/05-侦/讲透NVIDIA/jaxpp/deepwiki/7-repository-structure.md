<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/jaxpp · page 7 Repository Structure · fetched 2026-10-26 -->

# Repository Structure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [.gitignore](.gitignore)
- [README.md](README.md)

</details>



## Purpose

This document provides a detailed overview of the JaxPP repository organization, file structure, and key components. It serves as a map to help developers navigate the codebase and understand how different parts of the system are organized. For information about the core functionality and API, see [Core Functionality](#2).

## Repository Layout

JaxPP follows a standard Python package layout with some specialized directories for examples, documentation, and development tools.

```mermaid
graph TD
    subgraph "Repository Root"
        A["jaxpp/"] --> B["jaxpp/ (Core Package)"]
        A --> C["examples/"]
        A --> D["scripts/"]
        A --> E["docs/"]
        A --> F["tests/"]
        A --> G["setup.py"]
        A --> H["Makefile"]
        A --> I["README.md"]
    end

    subgraph "Core Package Structure"
        B --> B1["__init__.py"]
        B --> B2["pipeline.py"]
        B --> B3["grad_accumulation.py"]
        B --> B4["mpmd_mesh.py"]
        B --> B5["schedules.py"]
        B --> B6["ray_runtime/"]
    end

    subgraph "Docker Configuration"
        D --> D1["docker/"]
        D1 --> D2["Dockerfile.base"]
        D1 --> D3["Dockerfile"]
    end

    subgraph "Examples"
        C --> C1["basic.py"]
        C --> C2["other examples..."]
    end
```

Sources: [README.md](), [.gitignore]()

## Core Package Structure

The main functionality of JaxPP is organized in a Python package that implements pipeline parallelism primitives and utilities. The core modules implement the key components of the system architecture.

```mermaid
graph LR
    subgraph "Core JaxPP Package"
        A["jaxpp/__init__.py"] --> B["Export Public API"]
        
        C["jaxpp/pipeline.py"] --> C1["pipeline_enter_stage()"]
        C --> C2["@pipelined Decorator"]
        
        D["jaxpp/grad_accumulation.py"] --> D1["accumulate_grads()"]
        
        E["jaxpp/mpmd_mesh.py"] --> E1["MpmdMesh Class"]
        
        F["jaxpp/schedules.py"] --> F1["Pipeline Schedules"]
        F1 --> F2["Eager1F1B"]
        
        G["jaxpp/ray_runtime/"] --> G1["Ray Single-controller Runtime"]
    end
    
    A --> C
    A --> D
    A --> E
    A --> F
    A --> G
```

Sources: [README.md]()

### Key Files and Their Purposes

| File | Description |
|------|-------------|
| `jaxpp/pipeline.py` | Implements the pipeline parallelism core functionality, including `pipeline_enter_stage()` and the `@pipelined` decorator |
| `jaxpp/grad_accumulation.py` | Contains the `accumulate_grads()` function for handling gradient accumulation in pipelined training |
| `jaxpp/mpmd_mesh.py` | Defines the `MpmdMesh` class for configuring device meshes for pipeline parallelism |
| `jaxpp/schedules.py` | Implements different pipeline scheduling strategies like `Eager1F1B` |
| `jaxpp/ray_runtime/` | Contains the experimental Ray-based single-controller runtime implementation |

Sources: [README.md]()

## Example Directory

The examples directory contains sample code demonstrating how to use JaxPP for different use cases. These examples serve as practical guides for implementing pipeline parallelism in various scenarios.

```mermaid
graph TD
    subgraph "examples/"
        A["basic.py"] --> A1["Basic pipeline parallelism example"]
        B["other examples..."] --> B1["Additional use cases"]
    end
```

The `basic.py` example demonstrates:
- Creating a simple model with pipeline stages
- Defining a pipelined training function
- Setting up the MpmdMesh
- Running training with pipeline parallelism

Sources: [README.md:114]()

## Development and Testing Infrastructure

The repository includes various files and directories related to development, testing, and quality assurance.

```mermaid
graph TD
    subgraph "Development Tools"
        A["Makefile"] --> A1["Build commands"]
        A --> A2["Test commands"]
        A --> A3["Lint commands"]
        
        B["tests/"] --> B1["Test suites"]
        
        C[".gitignore"] --> C1["Git ignore patterns"]
        
        D["setup.py"] --> D1["Package installation"]
        
        E[".ruff.toml"] --> E1["Ruff linter configuration"]
    end
```

### Testing Framework

The project uses pytest for unit and integration testing. Test files are organized in the `tests/` directory, matching the structure of the main package.

### Build System

The Makefile provides commands for:
- Building the package
- Running tests
- Linting and formatting code
- Building documentation

Sources: [.gitignore](), [README.md:157-162]()

## Docker Configuration

JaxPP provides Docker containers for development and testing, configured in two stages:

```mermaid
flowchart TD
    subgraph "Docker Build Process"
        A["scripts/docker/Dockerfile.base"] --> B["jaxpp-base image"]
        B --> C["scripts/docker/Dockerfile"]
        C --> D["jaxpp image"]
    end
    
    subgraph "Base Image Contents"
        B --> E["CUDA 12.6"]
        B --> F["Ubuntu 22.04"]
        B --> G["Core Dependencies"]
    end
    
    subgraph "Main Image Contents"
        D --> H["JaxPP Code"]
        D --> I["Development Tools"]
        D --> J["Test Suites"]
    end
```

The Docker configuration is designed to provide a consistent environment for development and testing, with all necessary dependencies pre-installed.

Sources: [README.md:115-143]()

## Documentation System

The documentation for JaxPP is organized in the `docs/` directory and uses Sphinx for generation.

```mermaid
graph TD
    subgraph "Documentation Structure"
        A["docs/"] --> B["_build/"]
        A --> C["conf.py"]
        A --> D["index.rst"]
        A --> E["api/"]
        A --> F["_static/"]
    end
```

The documentation system likely includes:
- API reference documentation
- Usage guides
- Performance optimization recommendations
- Development guidelines

Sources: [.gitignore:73-75]()

## Installation and Dependencies

JaxPP has specific dependencies and installation requirements:

```mermaid
graph TD
    subgraph "Dependencies"
        A["JAX 0.5.1"] --> B["JaxPP"]
        C["CUDA 12"] --> B
        D["cuDNN 9"] --> B
        E["Ray (Optional)"] --> B
    end
    
    subgraph "Installation Process"
        F["Clone Repository"] --> G["Run pip install -e ."]
        G --> H["Verify with examples/basic.py"]
    end
```

The installation process is straightforward and follows standard Python package installation practices. For multi-node setups, JaxPP needs to be installed on all participating nodes.

Sources: [README.md:24-38](), [README.md:167-173]()

## Additional Resources

The repository includes several other important files:

| File | Description |
|------|-------------|
| `README.md` | Overview, installation instructions, examples, and citations |
| `CONTRIBUTING.md` | Guidelines for contributors |
| `LICENSE` | Apache 2.0 license information |

Sources: [README.md]()

## File Organization for Different Parallelism Techniques

JaxPP's codebase organization reflects its support for various parallelism techniques:

```mermaid
graph TD
    subgraph "Parallelism Implementation"
        A["JaxPP Core"] --> B["Pipeline Parallelism"]
        A --> C["Data Parallelism"]
        A --> D["Tensor Parallelism"]
        
        B --> B1["pipeline.py: pipeline_enter_stage()"]
        B --> B2["pipeline.py: @pipelined"]
        B --> B3["schedules.py: Pipeline Schedules"]
        
        C --> C1["grad_accumulation.py: accumulate_grads()"]
        
        D --> D1["Integration with JAX Sharding"]
    end
```

Sources: [README.md:42-72]()