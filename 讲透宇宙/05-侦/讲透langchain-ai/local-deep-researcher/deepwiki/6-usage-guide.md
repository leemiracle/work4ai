<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/local-deep-researcher · page 6 Usage Guide · fetched 2026-10-26 -->

# Usage Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



This document provides practical guidance for setting up and using the Local Deep Researcher system. It covers the essential setup steps, configuration options, and deployment methods needed to get the LLM-driven research assistant running in your environment.

For detailed step-by-step installation instructions, see [Quick Start](#6.1). For advanced configuration of specific components, see [Advanced Configuration](#6.2). For architectural details about how the system works internally, see [System Architecture](#2).

## Setup Overview

The Local Deep Researcher requires three main setup categories: LLM provider configuration, search API selection, and runtime environment setup. The system uses a hierarchical configuration approach where environment variables take precedence over UI settings, which take precedence over code defaults.

```mermaid
flowchart TD
    START["User Initiates Setup"] --> ENV["Configure Environment Variables<br/>.env file"]
    ENV --> LLM_CHOICE{"Choose LLM Provider"}
    
    LLM_CHOICE -->|Local| OLLAMA["Setup Ollama<br/>localhost:11434"]
    LLM_CHOICE -->|Local| LMSTUDIO["Setup LMStudio<br/>localhost:1234"]
    LLM_CHOICE -->|Cloud| OPENAI["Setup OpenAI API"]
    
    OLLAMA --> SEARCH_CHOICE{"Choose Search API"}
    LMSTUDIO --> SEARCH_CHOICE
    OPENAI --> SEARCH_CHOICE
    
    SEARCH_CHOICE -->|No API Key| DDG["DuckDuckGo<br/>Default, No Setup"]
    SEARCH_CHOICE -->|API Key Required| TAVILY["Tavily API"]
    SEARCH_CHOICE -->|API Key Required| PERP["Perplexity API"]
    SEARCH_CHOICE -->|Self-Hosted| SEARX["SearXNG Instance"]
    
    DDG --> RUNTIME_CHOICE{"Choose Runtime"}
    TAVILY --> RUNTIME_CHOICE
    PERP --> RUNTIME_CHOICE
    SEARX --> RUNTIME_CHOICE
    
    RUNTIME_CHOICE -->|Development| LANGGRAPH_DEV["langgraph dev<br/>LangGraph Studio"]
    RUNTIME_CHOICE -->|Production| DOCKER["Docker Container<br/>Port 2024"]
    
    LANGGRAPH_DEV --> READY["System Ready<br/>http://127.0.0.1:2024"]
    DOCKER --> READY
```

Sources: [README.md:22-221]()

## Configuration Hierarchy

The system implements a three-tier configuration priority system managed by the `Configuration` class. This hierarchy ensures predictable behavior across different deployment scenarios while maintaining flexibility.

```mermaid
graph TB
    subgraph "Configuration Priority (High to Low)"
        ENV_VARS["Environment Variables<br/>.env file or system env"]
        UI_CONFIG["LangGraph Studio UI<br/>Configuration Tab"]
        DEFAULTS["Configuration Class Defaults<br/>configuration.py"]
    end
    
    subgraph "Configuration Processing"
        CONFIG_CLASS["Configuration Class<br/>configuration.py"]
        DOTENV_LOADER["python-dotenv<br/>Automatic .env loading"]
        LANGGRAPH_JSON["langgraph.json<br/>Points to .env file"]
    end
    
    subgraph "Runtime Application"
        GRAPH_STATE["SummaryState<br/>state.py"]
        LLM_NODES["LLM Integration Nodes<br/>graph.py"]
        SEARCH_NODES["Search API Nodes<br/>utils.py"]
    end
    
    ENV_VARS -->|"Highest Priority"| CONFIG_CLASS
    UI_CONFIG -->|"Medium Priority"| CONFIG_CLASS
    DEFAULTS -->|"Lowest Priority"| CONFIG_CLASS
    
    DOTENV_LOADER --> ENV_VARS
    LANGGRAPH_JSON --> DOTENV_LOADER
    
    CONFIG_CLASS --> GRAPH_STATE
    CONFIG_CLASS --> LLM_NODES
    CONFIG_CLASS --> SEARCH_NODES
```

Sources: [README.md:135-141](), [README.md:30-31]()

## LLM Provider Configuration

The system supports multiple LLM providers through a unified interface. The `LLM_PROVIDER` environment variable controls which provider to use, with provider-specific configuration handled through dedicated environment variables.

| Provider | Configuration Variables | Default Port | Notes |
|----------|------------------------|--------------|-------|
| `ollama` | `OLLAMA_BASE_URL`, `LOCAL_LLM` | 11434 | Requires Ollama service running |
| `lmstudio` | `LMSTUDIO_BASE_URL`, `LOCAL_LLM` | 1234 | Requires LMStudio server active |
| `openai` | `OPENAI_API_KEY`, `OPENAI_MODEL` | N/A | Cloud API, requires API key |

```mermaid
graph LR
    subgraph "LLM Provider Selection"
        ENV_VAR["LLM_PROVIDER<br/>Environment Variable"]
    end
    
    subgraph "Ollama Integration"
        OLLAMA_CONFIG["OLLAMA_BASE_URL<br/>LOCAL_LLM"]
        OLLAMA_SERVICE["Ollama Service<br/>localhost:11434"]
        OLLAMA_WRAPPER["langchain-ollama<br/>Integration"]
    end
    
    subgraph "LMStudio Integration"
        LMS_CONFIG["LMSTUDIO_BASE_URL<br/>LOCAL_LLM"]
        LMS_SERVICE["LMStudio Server<br/>localhost:1234"]
        LMS_WRAPPER["Custom OpenAI Wrapper<br/>configuration.py"]
    end
    
    subgraph "OpenAI Integration"
        OPENAI_CONFIG["OPENAI_API_KEY<br/>OPENAI_MODEL"]
        OPENAI_API["OpenAI API<br/>api.openai.com"]
        OPENAI_WRAPPER["langchain-openai<br/>Integration"]
    end
    
    ENV_VAR -->|"ollama"| OLLAMA_CONFIG
    ENV_VAR -->|"lmstudio"| LMS_CONFIG
    ENV_VAR -->|"openai"| OPENAI_CONFIG
    
    OLLAMA_CONFIG --> OLLAMA_SERVICE
    OLLAMA_SERVICE --> OLLAMA_WRAPPER
    
    LMS_CONFIG --> LMS_SERVICE
    LMS_SERVICE --> LMS_WRAPPER
    
    OPENAI_CONFIG --> OPENAI_API
    OPENAI_API --> OPENAI_WRAPPER
```

Sources: [README.md:35-70]()

## Search API Integration

The system provides a unified search interface that abstracts different search providers. Each provider has specific capabilities and requirements, with DuckDuckGo serving as the default option requiring no API keys.

```mermaid
graph TD
    subgraph "Search API Selection"
        SEARCH_ENV["SEARCH_API<br/>Environment Variable"]
    end
    
    subgraph "No API Key Required"
        DDG_CONFIG["search_api: duckduckgo<br/>FETCH_FULL_PAGE"]
        DDG_LIB["duckduckgo-search<br/>Python Library"]
        DDG_IMPL["DuckDuckGo Search<br/>utils.py functions"]
    end
    
    subgraph "API Key Required"
        TAVILY_CONFIG["TAVILY_API_KEY<br/>tavily.com"]
        PERP_CONFIG["PERPLEXITY_API_KEY<br/>perplexity.ai"]
        TAVILY_LIB["tavily-python<br/>SDK"]
        PERP_HTTP["httpx requests<br/>Direct API calls"]
    end
    
    subgraph "Self-Hosted"
        SEARX_CONFIG["SEARX_BASE_URL<br/>Self-hosted instance"]
        SEARX_HTTP["httpx requests<br/>SearXNG API"]
    end
    
    subgraph "Unified Search Interface"
        SEARCH_UTILS["search_web function<br/>utils.py"]
        CONTENT_PROC["Content Processing<br/>markdownify conversion"]
    end
    
    SEARCH_ENV -->|"duckduckgo"| DDG_CONFIG
    SEARCH_ENV -->|"tavily"| TAVILY_CONFIG
    SEARCH_ENV -->|"perplexity"| PERP_CONFIG
    SEARCH_ENV -->|"searxng"| SEARX_CONFIG
    
    DDG_CONFIG --> DDG_LIB
    DDG_LIB --> DDG_IMPL
    
    TAVILY_CONFIG --> TAVILY_LIB
    PERP_CONFIG --> PERP_HTTP
    SEARX_CONFIG --> SEARX_HTTP
    
    DDG_IMPL --> SEARCH_UTILS
    TAVILY_LIB --> SEARCH_UTILS
    PERP_HTTP --> SEARCH_UTILS
    SEARX_HTTP --> SEARCH_UTILS
    
    SEARCH_UTILS --> CONTENT_PROC
```

Sources: [README.md:72-81]()

## Running the System

The primary method for running Local Deep Researcher is through LangGraph Studio, which provides both a development server and web-based user interface. The system also supports Docker deployment for production environments.

### LangGraph Studio Development

The `langgraph dev` command starts a local development server that hosts both the LangGraph API and serves the web UI. The system uses `uv` package manager for dependency management and supports both Unix and Windows environments.

```bash
# Install and run with uv (recommended)
uvx --refresh --from "langgraph-cli[inmem]" --with-editable . --python 3.11 langgraph dev

# Alternative installation method
pip install -e .
pip install -U "langgraph-cli[inmem]"
langgraph dev
```

### Docker Deployment

The included `Dockerfile` creates a containerized version of the system that runs LangGraph Studio as a service. The container exposes port 2024 and requires external LLM services to be configured via environment variables.

```bash
# Build container image
docker build -t local-deep-researcher .

# Run with environment configuration
docker run --rm -it -p 2024:2024 \
  -e SEARCH_API="tavily" \
  -e TAVILY_API_KEY="tvly-***" \
  -e LLM_PROVIDER=ollama \
  -e OLLAMA_BASE_URL="http://host.docker.internal:11434/" \
  -e LOCAL_LLM="llama3.2" \
  local-deep-researcher
```

Sources: [README.md:84-122](), [README.md:194-221]()

## System Access and Interface

Once running, the system provides multiple access points for interaction and monitoring. The LangGraph Studio UI serves as the primary interface for configuring parameters and visualizing the research process.

| Interface | URL | Purpose |
|-----------|-----|---------|
| LangGraph Studio UI | `https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024` | Main user interface |
| API Endpoint | `http://127.0.0.1:2024` | Direct API access |
| API Documentation | `http://127.0.0.1:2024/docs` | OpenAPI specification |

### Configuration Interface

The LangGraph Studio UI provides a configuration tab where runtime parameters can be adjusted without restarting the service. These settings have medium priority in the configuration hierarchy, below environment variables but above code defaults.

```mermaid
graph TB
    subgraph "User Interaction Flow"
        BROWSER["Web Browser<br/>LangGraph Studio UI"]
        CONFIG_TAB["Configuration Tab<br/>Runtime Settings"]
        RESEARCH_INPUT["Research Topic Input<br/>Main Interface"]
    end
    
    subgraph "Backend Processing"
        LANGGRAPH_API["LangGraph API<br/>Port 2024"]
        STATE_GRAPH["StateGraph Execution<br/>graph.py"]
        SUMMARY_STATE["SummaryState Management<br/>state.py"]
    end
    
    subgraph "Output Visualization"
        GRAPH_VIZ["Graph Execution Visualization<br/>Node-by-node progress"]
        STATE_INSPECTOR["State Inspector<br/>Intermediate results"]
        FINAL_OUTPUT["Final Research Summary<br/>Markdown with citations"]
    end
    
    BROWSER --> CONFIG_TAB
    BROWSER --> RESEARCH_INPUT
    
    CONFIG_TAB --> LANGGRAPH_API
    RESEARCH_INPUT --> LANGGRAPH_API
    
    LANGGRAPH_API --> STATE_GRAPH
    STATE_GRAPH --> SUMMARY_STATE
    
    STATE_GRAPH --> GRAPH_VIZ
    SUMMARY_STATE --> STATE_INSPECTOR
    STATE_GRAPH --> FINAL_OUTPUT
    
    GRAPH_VIZ --> BROWSER
    STATE_INSPECTOR --> BROWSER
    FINAL_OUTPUT --> BROWSER
```

Sources: [README.md:124-148](), [README.md:174-183]()

## Troubleshooting Common Issues

### Model Compatibility

Some LLM models may have difficulty with structured JSON output requirements. The system includes fallback mechanisms for models that struggle with JSON mode formatting, particularly smaller or specialized models.

### Browser Compatibility

The LangGraph Studio UI works best with Firefox. Safari users may encounter security warnings due to mixed HTTPS/HTTP content. Alternative browsers or disabling ad-blocking extensions can resolve compatibility issues.

### Docker Networking

When running in Docker, the `OLLAMA_BASE_URL` must point to `host.docker.internal:11434` instead of `localhost:11434` to properly connect to Ollama running on the host system.

Sources: [README.md:149-162](), [README.md:194-221]()

---

