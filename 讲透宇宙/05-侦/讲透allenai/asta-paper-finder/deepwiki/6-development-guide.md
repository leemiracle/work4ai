<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/asta-paper-finder · page 6 Development Guide · fetched 2026-10-26 -->

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Makefile](Makefile)
- [agents/mabool/api/.python-version](agents/mabool/api/.python-version)
- [agents/mabool/api/Makefile](agents/mabool/api/Makefile)

</details>



This document provides a comprehensive guide for developers working on the ASTA Paper Finder system. It covers environment setup, build system usage, code quality tools, and development workflows specific to this multi-project Python repository.

For information about the overall system architecture, see [System Architecture](#2). For details about configuring the system, see [Configuration System](#4). For API usage and testing, see [API Reference](#5).

## Development Workflow Overview

The ASTA Paper Finder uses a multi-project structure with a centralized build system that orchestrates development tasks across all subprojects.

```mermaid
graph TB
    subgraph "Development Environment"
        DEV["Developer Workstation"]
        UV["uv Package Manager<br/>Python 3.12.8"]
        VENV[".venv<br/>Virtual Environment"]
    end
    
    subgraph "Root Build System"
        ROOT_MAKE["Makefile<br/>Root Orchestrator"]
        FOREACH["dev/make/make_foreach.sh<br/>Multi-project Executor"]
        COMMON_MK["dev/make/common.mk<br/>Shared Targets"]
    end
    
    subgraph "Subprojects"
        MABOOL_API["agents/mabool/api/<br/>FastAPI Application"]
        LIBS_COMMON["libs/common/"]
        LIBS_DI["libs/di/"]
        LIBS_DCOLLECTION["libs/dcollection/"]
        LIBS_CHAIN["libs/chain/"]
        LIBS_CONFIG["libs/config/"]
    end
    
    subgraph "Generated Artifacts"
        TYPE_CFG["mabool/data_model/<br/>Config Types"]
        TYPE_UFS["mabool/data_model/ufs.py<br/>User-Facing Strings"]
        LOCK_FILE["uv.lock<br/>Dependency Lock"]
    end
    
    DEV --> UV
    UV --> VENV
    DEV --> ROOT_MAKE
    ROOT_MAKE --> FOREACH
    
    FOREACH --> MABOOL_API
    FOREACH --> LIBS_COMMON
    FOREACH --> LIBS_DI
    FOREACH --> LIBS_DCOLLECTION
    FOREACH --> LIBS_CHAIN
    FOREACH --> LIBS_CONFIG
    
    MABOOL_API --> TYPE_CFG
    MABOOL_API --> TYPE_UFS
    ROOT_MAKE --> LOCK_FILE
    
    COMMON_MK --> MABOOL_API
    COMMON_MK --> LIBS_COMMON
    COMMON_MK --> LIBS_DI
    COMMON_MK --> LIBS_DCOLLECTION
    COMMON_MK --> LIBS_CHAIN
    COMMON_MK --> LIBS_CONFIG
```

**Sources**: [Makefile:1-89](), [agents/mabool/api/Makefile:1-32]()

## Environment Setup

### Python Version and Package Management

The system requires Python 3.12.8 and uses `uv` as the package manager for dependency resolution and virtual environment management.

| Component | Version/Tool | Purpose |
|-----------|-------------|---------|
| Python | 3.12.8 | Runtime environment |
| Package Manager | `uv` | Dependency management and virtual environments |
| Lock File | `uv.lock` | Reproducible dependency resolution |
| Constraints | `constraints.txt` | Version constraints (e.g., setuptools<72) |

### Initial Setup Commands

```bash
# Create virtual environment
make venv

# Install dependencies (production only)
make sync

# Install dependencies including development tools
make sync-dev

# Lock dependencies after changes
make lock
```

**Sources**: [Makefile:12-34](), [agents/mabool/api/.python-version:1-2]()

## Build System Architecture

The build system uses a hierarchical Makefile structure that enables both project-wide and individual subproject operations.

```mermaid
graph TB
    subgraph "Root Level Commands"
        MAKE_SYNC["make sync"]
        MAKE_SYNC_DEV["make sync-dev"]
        MAKE_STYLE["make style"]
        MAKE_FIX["make fix"]
        MAKE_LINT["make lint"]
        MAKE_FORMAT["make format"]
        MAKE_TYPE_CHECK["make type-check"]
    end
    
    subgraph "Execution Strategy"
        MODE_PAR["MODE=par<br/>(default)<br/>Parallel execution"]
        MODE_SEQ["MODE=seq<br/>Sequential execution"]
        FOREACH_SCRIPT["make_foreach.sh<br/>Orchestration Script"]
    end
    
    subgraph "Subproject Targets"
        API_MAKE["agents/mabool/api/Makefile"]
        COMMON_MAKE["libs/common/Makefile"]
        DI_MAKE["libs/di/Makefile"]
        DCOLL_MAKE["libs/dcollection/Makefile"]
        CHAIN_MAKE["libs/chain/Makefile"]
        CONFIG_MAKE["libs/config/Makefile"]
    end
    
    subgraph "Special API Targets"
        TYPE_CFG_GEN["type-cfg-gen<br/>Config Type Generation"]
        TYPE_UFS_GEN["type-ufs-gen<br/>User-Facing String Types"]
        START_DEV["start-dev<br/>Development Server"]
    end
    
    MAKE_STYLE --> FOREACH_SCRIPT
    MAKE_FIX --> FOREACH_SCRIPT
    MAKE_LINT --> FOREACH_SCRIPT
    MAKE_FORMAT --> FOREACH_SCRIPT
    MAKE_TYPE_CHECK --> FOREACH_SCRIPT
    
    MODE_PAR --> FOREACH_SCRIPT
    MODE_SEQ --> FOREACH_SCRIPT
    
    FOREACH_SCRIPT --> API_MAKE
    FOREACH_SCRIPT --> COMMON_MAKE
    FOREACH_SCRIPT --> DI_MAKE
    FOREACH_SCRIPT --> DCOLL_MAKE
    FOREACH_SCRIPT --> CHAIN_MAKE
    FOREACH_SCRIPT --> CONFIG_MAKE
    
    API_MAKE --> TYPE_CFG_GEN
    API_MAKE --> TYPE_UFS_GEN
    API_MAKE --> START_DEV
```

### Common Development Commands

| Command | Purpose | Execution Mode |
|---------|---------|----------------|
| `make style` | Run format check, lint, and type-check | Parallel by default |
| `make fix` | Auto-fix formatting and linting issues | Parallel by default |
| `make lint` | Run Ruff linter across all projects | Parallel by default |
| `make format` | Format code with auto-formatting tools | Parallel by default |
| `make type-check` | Run pyright type checker | Parallel by default |

### Execution Modes

The build system supports two execution modes controlled by the `MODE` variable:

- **Parallel Mode** (`MODE=par`, default): Runs tasks across all subprojects simultaneously, capturing output and reporting only failures
- **Sequential Mode** (`MODE=seq`): Runs tasks one subproject at a time with full output visibility

Example usage:
```bash
# Run format check in sequential mode to see detailed output
make format-check MODE=seq
```

**Sources**: [Makefile:35-89](), [agents/mabool/api/Makefile:1-32]()

## Code Quality and Tooling

The system enforces code quality through multiple automated tools integrated into the build system.

### Linting and Formatting

| Tool | Configuration | Purpose |
|------|--------------|---------|
| Ruff | Project-specific config | Code linting and formatting |
| Flake8 | `.flake8` | Additional linting rules |
| pyright | Project-specific config | Type checking |

### Custom Quality Tools

The system includes custom development tools:

- **stable_sort_checker**: Custom Flake8 plugin for enforcing consistent sorting
- **Coverage reporting**: Configured via `.coveragerc`

### Quality Check Workflow

```bash
# Check all quality metrics
make style

# Auto-fix issues where possible
make fix

# Run individual checks
make lint-check
make format-check
make type-check
```

**Sources**: [Makefile:37-63]()

## Type Generation System

The mabool API subproject includes an automated type generation system that creates Python type definitions from TOML configuration files.

### Type Generation Targets

| Target | Input | Output | Purpose |
|--------|-------|--------|---------|
| `type-cfg-gen` | Configuration TOML files | `mabool/data_model/` | Generate config data classes |
| `type-ufs-gen` | `conf/user_facing/*.toml` | `mabool/data_model/ufs.py` | Generate user-facing string types |

### Type Generation Workflow

```mermaid
graph LR
    subgraph "Input Files"
        CONFIG_TOML["config.toml<br/>conf/user_facing/*.toml"]
    end
    
    subgraph "Generation Process"
        GEN_SCRIPT["ai2i.config.gen_config_types<br/>Python Module"]
        TYPE_CFG_TARGET["make type-cfg-gen"]
        TYPE_UFS_TARGET["make type-ufs-gen"]
    end
    
    subgraph "Generated Output"
        DATA_MODEL_DIR["mabool/data_model/<br/>Type Definitions"]
        UFS_PY["mabool/data_model/ufs.py<br/>User-Facing Strings"]
    end
    
    CONFIG_TOML --> GEN_SCRIPT
    GEN_SCRIPT --> TYPE_CFG_TARGET
    GEN_SCRIPT --> TYPE_UFS_TARGET
    
    TYPE_CFG_TARGET --> DATA_MODEL_DIR
    TYPE_UFS_TARGET --> UFS_PY
```

### Usage

```bash
# Generate configuration types
make type-cfg-gen

# Generate user-facing string types
make type-ufs-gen

# Both are included in the fix target
make fix
```

The type generation system ensures type safety between the TOML configuration files and the Python code that consumes them, automatically creating dataclasses and type annotations.

**Sources**: [agents/mabool/api/Makefile:8-18]()

## Development Server

### Starting the Development Server

The mabool API includes a development server for local testing and development:

```bash
# Start development server
cd agents/mabool/api
make start-dev
```

This runs the `dev.sh` script which sets up the development environment and starts the FastAPI application with development-specific settings.

### Development Server Features

- Hot reloading for code changes
- Development-specific logging and debugging
- Local API endpoint access for testing

**Sources**: [agents/mabool/api/Makefile:20-22]()

## Multi-Project Structure

The repository is organized as multiple independent Python projects that share common development tooling:

| Project Path | Purpose |
|-------------|---------|
| `agents/mabool/api/` | FastAPI application and agent system |
| `libs/common/` | Shared common utilities |
| `libs/di/` | Dependency injection framework |
| `libs/dcollection/` | Data collection utilities |
| `libs/chain/` | Chain processing utilities |
| `libs/config/` | Configuration management |

Each subproject maintains its own `Makefile` that inherits from the common build system while defining project-specific targets and dependencies.

**Sources**: [Makefile:6]()

---

