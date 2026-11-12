<!-- source: DeepWiki mcp.deepwiki.com · repo browser-use/eval · page 6 Development Environment · fetched 2026-10-30 -->

# Development Environment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [build_repo.sh](build_repo.sh)
- [requirements_old.txt](requirements_old.txt)

</details>



This document covers the development environment setup for the browser-use evaluation system, including the build process, key dependencies, and integration with the browser-use package. This environment enables automated browser task execution and AI-powered evaluation of web interactions.

For step-by-step setup instructions, see [Environment Setup](#6.1). For detailed dependency analysis, see [Dependencies and Packages](#6.2). For development tooling and best practices, see [Development Tools](#6.3).

## Environment Overview

The development environment consists of a Python 3.11 virtual environment with the browser-use package built from source, along with supporting libraries for web automation, AI model integration, and data processing. The system uses `uv` for fast dependency management and virtual environment creation.

### Development Environment Architecture

```mermaid
graph TB
    subgraph "Source Control"
        GH["https://github.com/browser-use/browser-use.git"]
        BRANCH["memory-state-extraction"]
    end
    
    subgraph "Build Environment"
        VENV[".venv (Python 3.11)"]
        UV["uv package manager"]
        BUILD["python -m build"]
    end
    
    subgraph "Core Dependencies"
        BU["browser_use-*.whl"]
        PW["playwright"]
        LC["langchain_google_genai"]
    end
    
    subgraph "Runtime Components"
        BROWSER["Browser Instances"]
        LLM["LLM Providers"]
        EVAL["Evaluation Pipeline"]
    end
    
    GH --> BRANCH
    BRANCH --> UV
    UV --> VENV
    VENV --> BUILD
    BUILD --> BU
    BU --> PW
    BU --> LC
    BU --> BROWSER
    LC --> LLM
    BROWSER --> EVAL
```

Sources: [build_repo.sh:9-32]()

## Build Process Flow

The build process is orchestrated by the `build_repo.sh` script, which handles cloning, environment setup, building, and dependency installation in a specific sequence to ensure compatibility with the evaluation system.

### Build Process Sequence

```mermaid
sequenceDiagram
    participant Script as build_repo.sh
    participant Git as GitHub Repository
    participant UV as uv Package Manager
    participant Build as Python Build System
    participant Playwright as Playwright Browser Engine
    
    Script->>Git: "git clone browser-use.git"
    Script->>Git: "git checkout memory-state-extraction"
    Script->>UV: "uv venv --python=3.11"
    Script->>UV: "source .venv/bin/activate"
    Script->>UV: "uv pip install build"
    Script->>Build: "python -m build"
    Script->>UV: "uv pip install dist/browser_use-*.whl"
    Script->>UV: "uv pip install langchain_google_genai"
    Script->>Playwright: "playwright install"
```

Sources: [build_repo.sh:9-32]()

## Key Dependency Categories

The evaluation system requires several categories of dependencies that work together to enable web automation and AI evaluation capabilities.

| Category | Purpose | Key Packages |
|----------|---------|-------------|
| Browser Automation | Web interaction and control | `browser-use`, `selenium`, `playwright` |
| LLM Integration | AI model communication | `anthropic`, `openai`, `langchain-*` |
| Web Processing | Content extraction and parsing | `beautifulsoup4`, `trafilatura`, `html2text` |
| HTTP Clients | Network communication | `httpx`, `aiohttp`, `requests` |
| Data Processing | JSON/data manipulation | `pydantic`, `numpy`, `jsonpatch` |
| Async Runtime | Concurrent execution | `trio`, `anyio`, `asyncio` |

Sources: [requirements_old.txt:1-82]()

## Browser-Use Package Integration

The system builds and installs the `browser-use` package from a specific Git branch to ensure compatibility with the evaluation framework. This package provides the core browser automation capabilities used by the task execution engine.

### Browser-Use Build Configuration

```mermaid
graph LR
    subgraph "Source Repository"
        REPO["browser-use/browser-use.git"]
        BRANCH["memory-state-extraction"]
    end
    
    subgraph "Build Process"
        CLONE["git clone"]
        CHECKOUT["git checkout"]
        BUILD_CMD["python -m build"]
        WHEEL["dist/browser_use-*.whl"]
    end
    
    subgraph "Installation"
        UV_INSTALL["uv pip install"]
        VENV_PKG["Installed Package"]
    end
    
    REPO --> CLONE
    CLONE --> CHECKOUT
    CHECKOUT --> BRANCH
    CHECKOUT --> BUILD_CMD
    BUILD_CMD --> WHEEL
    WHEEL --> UV_INSTALL
    UV_INSTALL --> VENV_PKG
```

Sources: [build_repo.sh:9-28]()

## Development Environment Components

The development environment provides the foundation for the entire evaluation pipeline, from task execution through result analysis.

### Environment Component Dependencies

```mermaid
graph TB
    subgraph "Core Runtime"
        PYTHON["Python 3.11"]
        VENV[".venv Virtual Environment"]
        UV_MGR["uv Package Manager"]
    end
    
    subgraph "Browser Automation Stack"
        BU_PKG["browser_use package"]
        SELENIUM["selenium==4.26.1"]
        PLAYWRIGHT_PY["playwright (Python)"]
        PLAYWRIGHT_BIN["playwright browsers"]
    end
    
    subgraph "AI Integration Stack"
        ANTHROPIC["anthropic==0.39.0"]
        OPENAI["openai==1.54.4"]
        LANGCHAIN["langchain==0.3.7"]
        LANGCHAIN_ANTHROPIC["langchain-anthropic==0.3.0"]
        LANGCHAIN_OPENAI["langchain-openai==0.2.8"]
        LANGCHAIN_GOOGLE["langchain_google_genai"]
    end
    
    subgraph "Web Processing Stack"
        BS4["beautifulsoup4==4.12.3"]
        TRAFILATURA["trafilatura==1.12.2"]
        HTML2TEXT["html2text==2024.2.26"]
        REQUESTS["requests==2.32.3"]
        HTTPX["httpx==0.27.2"]
    end
    
    PYTHON --> VENV
    VENV --> UV_MGR
    UV_MGR --> BU_PKG
    BU_PKG --> SELENIUM
    BU_PKG --> PLAYWRIGHT_PY
    PLAYWRIGHT_PY --> PLAYWRIGHT_BIN
    UV_MGR --> ANTHROPIC
    UV_MGR --> OPENAI
    UV_MGR --> LANGCHAIN
    LANGCHAIN --> LANGCHAIN_ANTHROPIC
    LANGCHAIN --> LANGCHAIN_OPENAI
    LANGCHAIN --> LANGCHAIN_GOOGLE
    UV_MGR --> BS4
    UV_MGR --> TRAFILATURA
    UV_MGR --> HTML2TEXT
    UV_MGR --> REQUESTS
    UV_MGR --> HTTPX
```

Sources: [build_repo.sh:21-32](), [requirements_old.txt:10-82]()

## Environment Prerequisites

Before running the build script, ensure the following prerequisites are met:

- **Git**: For cloning the browser-use repository
- **Python 3.11**: Required Python version for compatibility
- **uv**: Fast Python package manager for dependency installation
- **Internet Access**: For downloading packages and browser binaries

The build script automatically handles virtual environment creation, dependency installation, and browser binary downloads through Playwright.

Sources: [build_repo.sh:21-32]()

---

