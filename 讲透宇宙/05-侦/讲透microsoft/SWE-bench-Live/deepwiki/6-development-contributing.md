<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/SWE-bench-Live · page 6 Development & Contributing · fetched 2026-10-26 -->

# Development & Contributing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [SECURITY.md](SECURITY.md)
- [SUPPORT.md](SUPPORT.md)
- [pyproject.toml](pyproject.toml)

</details>



This document provides information for developers working on the SWE-bench-Live project, including project structure, development workflow, and contribution guidelines. It covers the technical aspects of setting up a development environment and understanding how the codebase is organized.

For detailed information about project dependencies and structure, see [Project Structure & Dependencies](#6.1). For support and security information, see [Support & Security](#6.2). For licensing and community guidelines, see [License & Code of Conduct](#6.3).

## Overview

SWE-bench-Live is a Python-based system that combines multiple components: an evaluation harness (`swebench` package), a dataset curation pipeline, and the RepoLaunch tool for automated environment setup. The project uses modern Python tooling and supports multiple deployment scenarios.

## Development Environment Architecture

```mermaid
graph TB
    subgraph "Development Setup"
        A["Python 3.10+"]
        B["uv workspace"]
        C["setuptools build system"]
        D["Docker runtime"]
    end
    
    subgraph "Main Packages"
        E["swebench package"]
        F["launch workspace member"]
        G["curation scripts"]
        H["agent modules"]
    end
    
    subgraph "Optional Dependencies"
        I["datasets extras"]
        J["inference extras"] 
        K["test extras"]
        L["docs extras"]
    end
    
    A --> B
    B --> C
    B --> F
    C --> E
    E --> G
    E --> H
    
    I --> E
    J --> E
    K --> E
    L --> E
    
    D --> E
    D --> F
```

**Development Environment Structure**
Sources: [pyproject.toml:1-99]()

## Code Organization

The codebase follows a modular architecture with clear separation between evaluation, curation, and tooling components:

```mermaid
graph LR
    subgraph "swebench Package"
        A["swebench.__version__"]
        B["evaluation harness"]
        C["run_evaluation entrypoint"]
    end
    
    subgraph "launch Workspace"
        D["RepoLaunch tool"]
        E["agent system"]
        F["LLM integration"]
    end
    
    subgraph "curation Scripts"
        G["curation/crawl_repo.py"]
        H["curation/filter_repo.py"]
        I["repository discovery"]
    end
    
    subgraph "Supporting Modules"
        J["Docker utilities"]
        K["GitHub API integration"]
        L["logging system"]
    end
    
    A --> B
    B --> C
    D --> E
    E --> F
    G --> I
    H --> I
    
    C --> J
    D --> J
    I --> K
    B --> L
```

**Primary Code Modules and Their Relationships**
Sources: [pyproject.toml:79-92](), [pyproject.toml:6-11]()

## Development Workflow

### Build System Configuration

The project uses `setuptools` as the build backend with dynamic versioning from the `swebench.__version__` attribute. The build system is configured to include package data and supports namespace packages.

```mermaid
flowchart TD
    A["Developer Changes"] --> B["Pre-commit Hooks"]
    B --> C["setuptools Build"]
    C --> D["Package Distribution"]
    
    E["uv workspace"] --> F["launch member"]
    E --> G["swebench package"]
    
    H["Dynamic Version"] --> C
    I["Package Data"] --> C
    
    C --> J["PyPI Distribution"]
    C --> K["Local Development"]
```

**Build and Distribution Workflow**
Sources: [pyproject.toml:1-4](), [pyproject.toml:79-88]()

## Dependency Management

### Core Dependencies

The project has several categories of dependencies managed through `pyproject.toml`:

| Category | Key Dependencies | Purpose |
|----------|------------------|---------|
| Core | `docker`, `requests`, `rich` | Container management, HTTP, UI |
| Data | `datasets`, `GitPython`, `ghapi` | Dataset handling, Git operations |
| LLM | `openai`, `anthropic` | AI model integration |
| Utils | `tenacity`, `tqdm`, `unidiff` | Retry logic, progress, diff parsing |

### Optional Dependency Groups

```mermaid
graph TB
    subgraph "Optional Dependencies"
        A["datasets extras"]
        B["inference extras"]
        C["test extras"] 
        D["docs extras"]
    end
    
    subgraph "datasets Group"
        E["transformers"]
        F["tiktoken"]
        G["openai"]
        H["anthropic"]
    end
    
    subgraph "inference Group"
        I["torch"]
        J["flash_attn"]
        K["triton"]
        L["peft"]
    end
    
    subgraph "test Group"
        M["pytest"]
        N["pytest-cov"]
    end
    
    subgraph "docs Group"
        O["mkdocs"]
        P["mkdocs-material"]
        Q["mkdocstrings"]
    end
    
    A --> E
    A --> F
    A --> G
    A --> H
    
    B --> I
    B --> J
    B --> K
    B --> L
    
    C --> M
    C --> N
    
    D --> O
    D --> P
    D --> Q
```

**Optional Dependency Structure for Different Use Cases**
Sources: [pyproject.toml:40-77]()

## Development Environment Setup

### Python Version Requirements

The project requires Python 3.10 or higher, supporting both 3.10 and 3.11. This requirement ensures compatibility with modern Python features used throughout the codebase.

### Workspace Configuration

The project uses `uv.workspace` configuration with the `launch` directory as a workspace member, enabling coordinated development across the main package and the RepoLaunch tool.

### Ignored Files and Directories

The development environment excludes numerous file types and directories through `.gitignore`, including:

- Python bytecode (`__pycache__/`, `*.pyc`)
- Build artifacts (`build/`, `dist/`, `*.egg-info/`)
- IDE files (`.vscode/`, except specific configurations)
- Log files and temporary data
- Playground directories for experimentation

Sources: [.gitignore:329-430](), [pyproject.toml:89-92](), [pyproject.toml:17-22]()

## Project Metadata and Links

The project maintains several important URLs for community engagement:

- **Documentation**: GitHub repository link
- **Bug Reports**: GitHub issues
- **Source Code**: GitHub repository
- **Website**: swebench.com

The project is licensed under the MIT License and classified as supporting Python 3.10+ on any operating system.

Sources: [pyproject.toml:94-98](), [pyproject.toml:15-22]()

---

