<!-- source: DeepWiki mcp.deepwiki.com · repo mpaepper/llm_agents · page 4 Dependencies and External Services · fetched 2026-10-26 -->

# Dependencies and External Services

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [poetry.lock](poetry.lock)
- [pyproject.toml](pyproject.toml)
- [requirements.txt](requirements.txt)
- [setup.py](setup.py)

</details>



This page documents all external dependencies and third-party service integrations required by the llm_agents package. It covers both runtime Python package dependencies and external API services that tools connect to.

For detailed instructions on obtaining and configuring API keys, see [Required API Keys](#4.1). For a comprehensive breakdown of Python package dependencies and their purposes, see [Python Dependencies](#4.2).

## Overview

The llm_agents system has two categories of external dependencies:

1. **External API Services**: Third-party web services that tools integrate with to provide capabilities like web search and code execution
2. **Python Package Dependencies**: Libraries required for LLM integration, HTTP communication, data validation, and web scraping

All external API services require authentication via environment variables. The system uses modern Python dependency management through Poetry, with locked versions for reproducible builds.

Sources: [requirements.txt:1-5](), [pyproject.toml:16-23](), [poetry.lock:1-391]()

## External API Services

The system integrates with five external services, each providing specific capabilities to different tools.

### Service Integration Architecture

```mermaid
graph TB
    subgraph "Environment Configuration"
        OPENAI_KEY["OPENAI_API_KEY"]
        SERPAPI_KEY["SERPAPI_API_KEY"]
        GOOGLE_KEY["GOOGLE_API_KEY"]
        GOOGLE_CSE["GOOGLE_CSE_ID"]
        SEARX_URL["SEARX_INSTANCE_URL"]
    end
    
    subgraph "llm_agents Core"
        ChatLLM["ChatLLM class"]
        SerpAPITool["SerpAPITool class"]
        GoogleSearchTool["GoogleSearchTool class"]
        HNSearchTool["HackerNewsSearchTool class"]
        SearxSearchTool["SearxSearchTool class"]
        PythonREPL["PythonREPLTool class"]
    end
    
    subgraph "External Services"
        OpenAI["OpenAI API<br/>api.openai.com"]
        SerpAPI["SerpAPI Service<br/>serpapi.com"]
        GoogleAPI["Google Custom<br/>Search API"]
        HackerNewsAPI["Hacker News<br/>Algolia API"]
        SearxInstance["Self-hosted<br/>Searx Instance"]
        PythonInterp["Local Python<br/>Interpreter"]
    end
    
    OPENAI_KEY -->|authenticates| ChatLLM
    SERPAPI_KEY -->|authenticates| SerpAPITool
    GOOGLE_KEY -->|authenticates| GoogleSearchTool
    GOOGLE_CSE -->|identifies search engine| GoogleSearchTool
    SEARX_URL -->|specifies endpoint| SearxSearchTool
    
    ChatLLM -->|HTTPS POST| OpenAI
    SerpAPITool -->|HTTPS GET| SerpAPI
    GoogleSearchTool -->|HTTPS| GoogleAPI
    HNSearchTool -->|HTTPS GET| HackerNewsAPI
    SearxSearchTool -->|HTTPS POST| SearxInstance
    PythonREPL -->|exec| PythonInterp
```

**External API Services**

| Service | Purpose | Authentication Required | Used By |
|---------|---------|------------------------|---------|
| OpenAI API | LLM text generation for agent reasoning | `OPENAI_API_KEY` | `ChatLLM` class |
| SerpAPI | Google search results via third-party API | `SERPAPI_API_KEY` | `SerpAPITool` |
| Google Custom Search API | Direct Google search integration | `GOOGLE_API_KEY`, `GOOGLE_CSE_ID` | `GoogleSearchTool` |
| Hacker News Algolia API | Search Hacker News stories | None (public API) | `HackerNewsSearchTool` |
| Searx Instance | Privacy-focused meta-search engine | `SEARX_INSTANCE_URL` | `SearxSearchTool` |
| Python Interpreter | Local code execution | None (system Python) | `PythonREPLTool` |

Sources: [requirements.txt:1-5](), [pyproject.toml:16-23]()

### Service Dependencies by Component

```mermaid
graph LR
    subgraph "Core Components"
        Agent["Agent"]
        ChatLLM["ChatLLM"]
    end
    
    subgraph "Search Tool Group"
        SerpAPI["SerpAPITool"]
        Google["GoogleSearchTool"]
        HN["HackerNewsSearchTool"]
        Searx["SearxSearchTool"]
    end
    
    subgraph "Execution Tool"
        Python["PythonREPLTool"]
    end
    
    subgraph "External Dependencies"
        OpenAILib["openai>=0.27.0"]
        Requests["requests>=2.28.2"]
        GoogleClient["google-api-python-client>=2.83.0"]
        GoogleResults["google-search-results>=2.4.2"]
        BS4["beautifulsoup4"]
    end
    
    ChatLLM -->|imports| OpenAILib
    Agent -->|uses| ChatLLM
    
    SerpAPI -->|imports| GoogleResults
    SerpAPI -->|imports| Requests
    
    Google -->|imports| GoogleClient
    
    HN -->|imports| Requests
    HN -->|imports| BS4
    
    Searx -->|imports| Requests
    
    Python -->|uses| PythonInterp["Python exec"]
```

Sources: [requirements.txt:1-5](), [pyproject.toml:16-23]()

## Python Package Dependencies

The project uses **Poetry** for dependency management with pinned versions in `poetry.lock` for reproducible builds. Dependencies are organized into main (runtime) and dev (testing) groups.

### Core Runtime Dependencies

| Package | Minimum Version | Purpose | Primary Consumer |
|---------|----------------|---------|------------------|
| `openai` | 0.27.0 | OpenAI API client for LLM access | `ChatLLM` class |
| `pydantic` | 1.10.5 | Data validation and settings management | Configuration validation |
| `requests` | 2.28.2 | HTTP client for API calls | All search tools |
| `google-api-python-client` | 2.83.0 | Google APIs client library | `GoogleSearchTool` |
| `google-search-results` | 2.4.2 | SerpAPI Python client | `SerpAPITool` |
| `beautifulsoup4` | 4.12.0+ | HTML parsing for web scraping | `HackerNewsSearchTool` |

Sources: [requirements.txt:1-5](), [pyproject.toml:16-23]()

### Transitive Dependencies

The `poetry.lock` file pins all transitive dependencies. Key transitive dependencies include:

| Package | Purpose | Brought in by |
|---------|---------|---------------|
| `httpx` | Async HTTP client | `openai` library |
| `httpcore` | Low-level HTTP implementation | `httpx` |
| `certifi` | SSL certificate bundle | `requests`, `httpcore` |
| `google-auth` | Google API authentication | `google-api-python-client` |
| `protobuf` | Protocol buffer serialization | Google client libraries |
| `soupsieve` | CSS selector library | `beautifulsoup4` |

Sources: [poetry.lock:1-391]()

### Development Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `pytest` | 7.4.0+ | Test framework |
| `pytest-cov` | 4.1.0+ | Code coverage measurement |
| `pytest-mock` | 3.11.1+ | Mocking support for tests |

Sources: [pyproject.toml:25-28]()

## Dependency Management System

### Build System Configuration

```mermaid
graph TB
    subgraph "Dependency Specification Files"
        PyProject["pyproject.toml<br/>Poetry config + metadata"]
        Requirements["requirements.txt<br/>Minimal runtime deps"]
        SetupPy["setup.py<br/>setuptools config"]
    end
    
    subgraph "Lock Files"
        PoetryLock["poetry.lock<br/>Exact pinned versions"]
    end
    
    subgraph "Installation Methods"
        PoetryInstall["poetry install<br/>Development setup"]
        PipInstall["pip install -r requirements.txt<br/>Minimal runtime"]
        SetupInstall["pip install .<br/>Package installation"]
    end
    
    PyProject -->|generates| PoetryLock
    PyProject -->|poetry export| Requirements
    
    PoetryLock -->|poetry install reads| PoetryInstall
    Requirements -->|pip reads| PipInstall
    SetupPy -->|pip reads| SetupInstall
    
    PyProject -.defines same deps as.- SetupPy
    Requirements -.subset of.- PyProject
```

The project maintains three dependency specification files for different use cases:

1. **pyproject.toml**: Primary Poetry configuration with full metadata
2. **requirements.txt**: Minimal runtime dependencies for pip-based installs
3. **setup.py**: Classic setuptools configuration for package distribution

Sources: [pyproject.toml:1-89](), [requirements.txt:1-5](), [setup.py:1-21]()

### Dependency Version Constraints

The project specifies minimum versions (using `>=`) rather than exact versions in the source files, allowing patch and minor version updates. The `poetry.lock` file pins exact versions for all direct and transitive dependencies.

**Version Constraint Philosophy:**
- **Direct dependencies** in [requirements.txt:1-5]() use minimum version constraints (`>=`)
- **Poetry lock file** in [poetry.lock:1-391]() pins exact versions with SHA256 hashes
- **Python version** requires `^3.8` (3.8 or higher, but below 4.0)

Sources: [pyproject.toml:17](), [requirements.txt:1-5](), [poetry.lock:1-391]()

## Dependency Relationship Map

### OpenAI Integration Stack

```mermaid
graph TB
    Agent["Agent.run"]
    ChatLLM["ChatLLM.generate"]
    OpenAIClient["openai.OpenAI"]
    
    subgraph "OpenAI Library Dependencies"
        HTTPX["httpx"]
        HTTPCore["httpcore"]
        H11["h11"]
        AnyIO["anyio"]
        Pydantic["pydantic"]
    end
    
    OpenAIAPI["api.openai.com"]
    
    Agent -->|calls| ChatLLM
    ChatLLM -->|instantiates| OpenAIClient
    OpenAIClient -->|uses| HTTPX
    OpenAIClient -->|validates with| Pydantic
    
    HTTPX -->|built on| HTTPCore
    HTTPCore -->|uses| H11
    HTTPX -->|async support| AnyIO
    
    OpenAIClient -->|HTTPS POST| OpenAIAPI
```

Sources: [poetry.lock:18-63](), [poetry.lock:562-621]()

### Search Tool Dependencies

```mermaid
graph TB
    subgraph "Search Tools"
        SerpAPI["SerpAPITool"]
        Google["GoogleSearchTool"]
        HN["HackerNewsSearchTool"]
        Searx["SearxSearchTool"]
    end
    
    subgraph "HTTP Layer"
        Requests["requests library"]
        GoogleClient["google-api-python-client"]
        SerpAPILib["google-search-results"]
    end
    
    subgraph "Supporting Libraries"
        Certifi["certifi<br/>CA certificates"]
        CharsetNorm["charset-normalizer<br/>Text encoding"]
        IDNA["idna<br/>Domain encoding"]
        GoogleAuth["google-auth<br/>OAuth2"]
        BS4["beautifulsoup4<br/>HTML parser"]
    end
    
    SerpAPI -->|uses| SerpAPILib
    SerpAPILib -->|built on| Requests
    
    Google -->|uses| GoogleClient
    GoogleClient -->|uses| GoogleAuth
    GoogleClient -->|HTTP via| Requests
    
    HN -->|uses| Requests
    HN -->|parses with| BS4
    
    Searx -->|uses| Requests
    
    Requests -->|SSL certs| Certifi
    Requests -->|encoding| CharsetNorm
    Requests -->|domains| IDNA
```

Sources: [poetry.lock:100-211](), [poetry.lock:456-473](), [poetry.lock:518-530](), [poetry.lock:65-85]()

## Environment Variable Configuration

All external service authentication and configuration is managed through environment variables. These must be set before running the agent.

**Required Environment Variables by Feature:**

| Feature | Required Variables | Optional Variables |
|---------|-------------------|-------------------|
| Core agent (ChatLLM) | `OPENAI_API_KEY` | - |
| SerpAPI search | `OPENAI_API_KEY`, `SERPAPI_API_KEY` | - |
| Google Custom Search | `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `GOOGLE_CSE_ID` | - |
| Hacker News search | `OPENAI_API_KEY` | - |
| Searx search | `OPENAI_API_KEY`, `SEARX_INSTANCE_URL` | - |
| Python REPL | `OPENAI_API_KEY` | - |

**Note:** `OPENAI_API_KEY` is required for all operations since the agent's reasoning loop depends on the ChatLLM component.

Sources: Based on tool implementations and architecture diagrams

## Installation Methods

### Poetry Installation (Recommended for Development)

```bash
# Install with locked dependencies
poetry install

# Install without dev dependencies
poetry install --no-dev
```

This installs all dependencies from [poetry.lock:1-391]() with exact versions.

### Pip Installation (Minimal Runtime)

```bash
# Install from requirements.txt
pip install -r requirements.txt

# Or install as package
pip install .
```

This installs minimum required versions from [requirements.txt:1-5]() or [setup.py:11-16]().

Sources: [pyproject.toml:87-89](), [setup.py:1-21](), [requirements.txt:1-5]()

## Dependency Security and Updates

The `poetry.lock` file includes SHA256 hashes for all packages to verify integrity during installation. The project specifies minimum versions to allow security patches while maintaining compatibility.

**Update Strategy:**
- Minimum version constraints allow automatic patch updates
- Poetry lock file ensures reproducible builds
- Manual review required for major/minor version updates

To update dependencies:
```bash
# Update within constraints
poetry update

# Update specific package
poetry update openai
```

Sources: [poetry.lock:1-391](), [pyproject.toml:16-23]()

---

