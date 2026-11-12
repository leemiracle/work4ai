<!-- source: DeepWiki mcp.deepwiki.com · repo browser-use/bubus · page 6 Project Information · fetched 2026-10-30 -->

# Project Information

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [bubus/__init__.py](bubus/__init__.py)

</details>



This document provides essential project metadata, licensing information, and organizational structure for the bubus event bus system. It covers the legal framework, copyright details, and how the project is structured and distributed.

For detailed license terms and copyright information, see [License and Legal Information](6.2). For comprehensive package structure and public API exports, see [Package Structure and Exports](6.1).

## Project Overview

The bubus project is an event bus system designed for the browser-use agent, developed by Browser Use. It provides asynchronous event-driven architecture capabilities with Pydantic-powered type safety, concurrency control, and observability features.

### Project Identity

| Property | Value |
|----------|-------|
| Project Name | bubus |
| Repository | https://github.com/browser-use/bubus |
| Copyright Holder | Browser Use |
| Copyright Year | 2025 |
| License | MIT License |

Sources: [LICENSE:3]()

## License Summary

The bubus project is released under the MIT License, providing broad permissions for use, modification, and distribution. The license grants rights to use, copy, modify, merge, publish, distribute, sublicense, and sell the software without restriction, subject to inclusion of the original copyright notice and license terms.

```mermaid
graph TB
    subgraph "MIT License Permissions"
        USE["Commercial Use"]
        MOD["Modification"]
        DIST["Distribution"]
        SUB["Sublicensing"]
        SELL["Private Use"]
    end
    
    subgraph "Requirements"
        COPY["Include Copyright Notice"]
        LIC["Include License Text"]
    end
    
    subgraph "Limitations"
        WARR["No Warranty"]
        LIAB["No Liability"]
    end
    
    USE --- COPY
    MOD --- COPY
    DIST --- COPY
    SUB --- LIC
    SELL --- LIC
    
    COPY --- WARR
    LIC --- LIAB
```

**MIT License Structure for bubus Project**

Sources: [LICENSE:1-21]()

## Public API Structure

The bubus package provides a clean public API through its `__init__.py` module, exporting core classes and type definitions for event-driven systems.

**Core Public API Export Structure**

```mermaid
graph TB
    subgraph "bubus Package"
        BUBUS_INIT["bubus/__init__.py"]
        BUBUS_MODELS["bubus/models.py"]
        BUBUS_SERVICE["bubus/service.py"]
    end
    
    subgraph "Exported Classes"
        EVENT_BUS["EventBus"]
        BASE_EVENT["BaseEvent"]
        EVENT_RESULT["EventResult"]
        EVENT_HANDLER["EventHandler"]
    end
    
    subgraph "Exported Type Definitions"
        UUID_STR["UUIDStr"]
        PYTHON_ID_STR["PythonIdStr"]
        PYTHON_IDENTIFIER_STR["PythonIdentifierStr"]
    end
    
    BUBUS_SERVICE --> EVENT_BUS
    BUBUS_MODELS --> BASE_EVENT
    BUBUS_MODELS --> EVENT_RESULT
    BUBUS_MODELS --> EVENT_HANDLER
    BUBUS_MODELS --> UUID_STR
    BUBUS_MODELS --> PYTHON_ID_STR
    BUBUS_MODELS --> PYTHON_IDENTIFIER_STR
    
    BUBUS_INIT --> EVENT_BUS
    BUBUS_INIT --> BASE_EVENT
    BUBUS_INIT --> EVENT_RESULT
    BUBUS_INIT --> EVENT_HANDLER
    BUBUS_INIT --> UUID_STR
    BUBUS_INIT --> PYTHON_ID_STR
    BUBUS_INIT --> PYTHON_IDENTIFIER_STR
```

### Package Module Organization

| Module | Exported Classes | Purpose |
|--------|------------------|---------|
| `bubus.service` | `EventBus` | Core event dispatching and management |
| `bubus.models` | `BaseEvent`, `EventResult`, `EventHandler` | Event modeling and result handling |
| `bubus.models` | `UUIDStr`, `PythonIdStr`, `PythonIdentifierStr` | Type validation utilities |

**Public API Import Pattern**

```mermaid
graph LR
    subgraph "User Code"
        IMPORT["from bubus import EventBus, BaseEvent, EventResult"]
    end
    
    subgraph "bubus.__init__.py"
        INIT_IMPORTS["from bubus.models import BaseEvent, EventHandler, EventResult, PythonIdentifierStr, PythonIdStr, UUIDStr"]
        SERVICE_IMPORTS["from bubus.service import EventBus"]
        ALL_EXPORT["__all__ = ['EventBus', 'BaseEvent', 'EventResult', 'EventHandler', 'UUIDStr', 'PythonIdStr', 'PythonIdentifierStr']"]
    end
    
    IMPORT --> INIT_IMPORTS
    IMPORT --> SERVICE_IMPORTS
    INIT_IMPORTS --> ALL_EXPORT
    SERVICE_IMPORTS --> ALL_EXPORT
```

Sources: [bubus/__init__.py:1-14]()

## Project Organization

The bubus project follows standard Python package organization patterns with development tooling exclusions defined in `.gitignore`.

### Development Environment Structure

| Category | Files/Directories | Purpose |
|----------|------------------|---------|
| Source Code | `bubus/` package directory | Core event bus implementation |
| Python Cache | `__pycache__/`, `*.py[cod]`, `*.pyo` | Compiled bytecode files |
| Development Tools | `.ruff_cache/`, `.mypy_cache/`, `.pytest_cache/` | Tool-generated cache directories |
| Virtual Environment | `.venv*`, `venv/`, `env/`, `ENV/` | Python environment isolation |
| IDE Support | `.vscode/`, `.idea/`, `*.swp`, `*.swo` | Editor and IDE configurations |
| Build Artifacts | `dist/`, `build/`, `*.egg-info/` | Package distribution files |
| Testing | `.coverage`, `htmlcov/`, `coverage.xml` | Test coverage reports |
| Documentation | `site/` | Generated documentation |

Sources: [bubus/__init__.py:1](), [LICENSE:1]()

## Copyright and Attribution

The bubus project is copyrighted by Browser Use as of 2025. All source code, documentation, and associated materials are subject to this copyright unless otherwise specified.

### Copyright Notice

```
Copyright (c) 2025 Browser Use
```

This copyright notice must be included in all copies or substantial portions of the software when redistributing or modifying the code, as required by the MIT License terms.

Sources: [LICENSE:3]()

## Distribution and Publishing

The bubus package uses modern Python tooling for development, testing, and distribution with comprehensive quality assurance processes.

```mermaid
flowchart TB
    subgraph "Development Toolchain"
        UV_TOOL["uv"]
        RUFF_TOOL["ruff"]
        PYRIGHT_TOOL["pyright"]
        PYTEST_TOOL["pytest"]
    end
    
    subgraph "Cache Management"
        RUFF_CACHE_DIR[".ruff_cache/"]
        MYPY_CACHE_DIR[".mypy_cache/"] 
        PYTEST_CACHE_DIR[".pytest_cache/"]
        PYCACHE_DIR["__pycache__/"]
    end
    
    subgraph "Build Process"
        UV_LOCK_FILE["uv.lock"]
        DIST_BUILD["dist/"]
        PYPROJECT_CONFIG["pyproject.toml"]
    end
    
    subgraph "Quality Assurance"
        COVERAGE_DATA[".coverage"]
        COVERAGE_HTML["htmlcov/"]
        COVERAGE_XML_REPORT["coverage.xml"]
    end
    
    subgraph "CI/CD Pipeline"
        GITHUB_ACTIONS[".github/workflows/"]
        AUTOMATED_TESTS["Automated Testing"]
        PACKAGE_PUBLISH["PyPI Publishing"]
    end
    
    UV_TOOL --> UV_LOCK_FILE
    RUFF_TOOL --> RUFF_CACHE_DIR
    PYRIGHT_TOOL --> MYPY_CACHE_DIR
    PYTEST_TOOL --> PYTEST_CACHE_DIR
    PYTEST_TOOL --> COVERAGE_DATA
    
    UV_LOCK_FILE --> PYPROJECT_CONFIG
    PYPROJECT_CONFIG --> DIST_BUILD
    
    COVERAGE_DATA --> COVERAGE_HTML
    COVERAGE_DATA --> COVERAGE_XML_REPORT
    
    RUFF_CACHE_DIR -.-> AUTOMATED_TESTS
    COVERAGE_XML_REPORT --> AUTOMATED_TESTS
    AUTOMATED_TESTS --> PACKAGE_PUBLISH
    DIST_BUILD --> PACKAGE_PUBLISH
```

**Modern Python Development and Distribution Pipeline**

### Development Environment Files

The project excludes various development and build artifacts from version control:

| File Pattern | Tool/Purpose | Description |
|-------------|-------------|-------------|
| `__pycache__/`, `*.py[cod]` | Python Runtime | Compiled bytecode cache |
| `.ruff_cache/` | `ruff` | Linter/formatter cache |
| `.mypy_cache/` | `mypy`/`pyright` | Type checker cache |
| `.pytest_cache/` | `pytest` | Test execution cache |
| `uv.lock` | `uv` | Dependency lock file |
| `dist/` | Build Tools | Distribution packages |
| `.coverage`, `htmlcov/` | `pytest-cov` | Test coverage reports |

Sources: [LICENSE:1]()

## Project Scope and Boundaries

The bubus project encompasses:

- **Core Event Bus System**: Asynchronous event dispatching and handling
- **Type Safety**: Pydantic-based validation and generic type support  
- **Concurrency Control**: Advanced semaphore management and retry mechanisms
- **Observability**: Event history tracking and visualization capabilities
- **Development Tooling**: Comprehensive testing and CI/CD infrastructure

The project maintains clear boundaries around event-driven architecture patterns while providing extensibility through handler registration and event forwarding mechanisms.

Sources: [LICENSE:1-21]()

---

