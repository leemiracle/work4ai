<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/asta-paper-finder · page 5 API Reference · fetched 2026-10-26 -->

# API Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [agents/mabool/api/dev.sh](agents/mabool/api/dev.sh)
- [agents/mabool/api/mabool/__init__.py](agents/mabool/api/mabool/__init__.py)

</details>



This document provides comprehensive documentation for the FastAPI application that serves as the primary interface to the ASTA Paper Finder system. It covers the REST API endpoints, request/response models, and server configuration. For information about the underlying agent system that processes requests, see [Agent System](#3). For details about configuring API behavior and external service integration, see [Configuration System](#4).

## FastAPI Application Overview

The ASTA Paper Finder exposes its functionality through a FastAPI web application located in the `agents/mabool/api` directory. The application provides a single main endpoint for processing paper search queries and returns structured results from the agent pipeline.

```mermaid
graph TB
    subgraph "FastAPI Application Structure"
        APP["create_app()"]
        ENDPOINT["/api/2/rounds"]
        MODELS["Request/Response Models"]
        CONFIG["Configuration Loading"]
    end
    
    subgraph "Agent Pipeline Integration"
        QUERY_ANALYZER["Query Analyzer Agent"]
        SEARCH_AGENTS["Search Agents"]
        RELEVANCE["Relevance Processing"]
        RESULTS["Structured Results"]
    end
    
    subgraph "External Dependencies"
        GUNICORN["gunicorn server"]
        UVICORN["UvicornWorker"]
        ENV_CONFIG["APP_CONFIG_ENV"]
    end
    
    APP --> CONFIG
    APP --> ENDPOINT
    ENDPOINT --> MODELS
    ENDPOINT --> QUERY_ANALYZER
    QUERY_ANALYZER --> SEARCH_AGENTS
    SEARCH_AGENTS --> RELEVANCE
    RELEVANCE --> RESULTS
    RESULTS --> MODELS
    
    GUNICORN --> UVICORN
    UVICORN --> APP
    ENV_CONFIG --> CONFIG
```

**Sources:** [agents/mabool/api/dev.sh:1-11](), [README.md:35-40]()

## Main API Endpoint

### POST /api/2/rounds

The primary endpoint for submitting paper search queries to the ASTA Paper Finder system. This endpoint accepts natural language descriptions of paper search requirements and returns ranked, relevant papers through the agent pipeline.

#### Request Model

The endpoint accepts a JSON payload with the following structure:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `paper_description` | string | Yes | - | Natural language paper search description |
| `operation_mode` | string | No | "infer" | Search mode: "infer", "fast", or "diligent" |
| `inserted_before` | string | No | None | Upper-bound date filter (YYYY-MM-DD format) |
| `read_results_from_cache` | boolean | No | false | Enable file-based cache retrieval |

#### Operation Modes

- **infer/fast**: Executes a fast search (~30 seconds) with optimized agent configuration
- **diligent**: Performs exhaustive search (~3 minutes) with comprehensive agent pipeline

```mermaid
graph LR
    subgraph "Request Processing Flow"
        REQUEST["POST /api/2/rounds"]
        VALIDATION["Request Validation"]
        MODE_CHECK["operation_mode Check"]
        CACHE_CHECK["Cache Check"]
        AGENT_PIPELINE["Agent Pipeline Execution"]
        RESPONSE["JSON Response"]
    end
    
    REQUEST --> VALIDATION
    VALIDATION --> CACHE_CHECK
    CACHE_CHECK --> MODE_CHECK
    MODE_CHECK --> AGENT_PIPELINE
    AGENT_PIPELINE --> RESPONSE
    
    subgraph "Mode Configuration"
        FAST_CONFIG["Fast Mode Config"]
        DILIGENT_CONFIG["Diligent Mode Config"]
    end
    
    MODE_CHECK --> FAST_CONFIG
    MODE_CHECK --> DILIGENT_CONFIG
```

**Sources:** [README.md:44-57]()

## Server Configuration

### Development Server

The development server is configured using gunicorn with uvicorn workers for asynchronous request handling.

#### Server Launch Configuration

The development server uses the following configuration:

- **Server**: gunicorn with UvicornWorker
- **Workers**: 1 (single worker for development)
- **Bind Address**: 0.0.0.0:8000
- **Timeout**: 0 (unlimited for long-running searches)
- **Reload**: Enabled for development
- **Environment**: APP_CONFIG_ENV=dev

#### Application Factory

The FastAPI application is created through the factory pattern using `mabool.api.app:create_app()`. This function loads configuration, initializes the agent system, and sets up the API routes.

```mermaid
graph TB
    subgraph "Server Stack"
        CLI["make start-dev"]
        GUNICORN["gunicorn"]
        UVICORN_WORKER["UvicornWorker"]
        FASTAPI_APP["FastAPI Application"]
        CREATE_APP["create_app()"]
    end
    
    subgraph "Configuration Loading"
        ENV_VAR["APP_CONFIG_ENV=dev"]
        CONFIG_FILES["Configuration TOML Files"]
        SECRETS[".env.secret"]
    end
    
    subgraph "Application Components"
        ROUTES["API Routes"]
        MIDDLEWARE["FastAPI Middleware"]
        AGENT_SYSTEM["Agent System Initialization"]
    end
    
    CLI --> GUNICORN
    GUNICORN --> UVICORN_WORKER
    UVICORN_WORKER --> FASTAPI_APP
    FASTAPI_APP --> CREATE_APP
    
    ENV_VAR --> CREATE_APP
    CONFIG_FILES --> CREATE_APP
    SECRETS --> CREATE_APP
    
    CREATE_APP --> ROUTES
    CREATE_APP --> MIDDLEWARE
    CREATE_APP --> AGENT_SYSTEM
```

**Sources:** [agents/mabool/api/dev.sh:1-11](), [README.md:37-40]()

## API Authentication and Secrets

The API requires several external service API keys configured in the `.env.secret` file:

| Service | Key Variable | Purpose |
|---------|--------------|---------|
| OpenAI | `OPENAI_API_KEY` | LLM operations for query analysis and planning |
| Semantic Scholar | `S2_API_KEY` | Paper metadata and citation retrieval |
| Cohere | `COHERE_API_KEY` | Document reranking and relevance scoring |
| Google AI | `GOOGLE_API_KEY` | Alternative LLM provider |

**Sources:** [README.md:23-24]()

## Integration with Agent System

The FastAPI application serves as the entry point to the comprehensive agent pipeline. When a request is received, it flows through multiple processing stages:

```mermaid
graph TB
    subgraph "API Layer"
        API_ENDPOINT["/api/2/rounds Endpoint"]
        REQUEST_MODEL["Request Validation"]
        RESPONSE_MODEL["Response Serialization"]
    end
    
    subgraph "Agent Orchestration"
        QUERY_ANALYZER["QueryAnalyzerAgent"]
        METADATA_PLANNER["MetadataPlannerAgent"]
        SEARCH_DISPATCH["Search Agent Dispatch"]
    end
    
    subgraph "Search Execution"
        DENSE_AGENT["DenseAgent"]
        KEYWORD_AGENT["BroadSearchByKeywordAgent"]
        CITATION_AGENT["BroadByCitationAgent"]
        TITLE_AGENT["SpecificPaperByTitleAgent"]
        AUTHOR_AGENT["SearchByAuthorAgent"]
    end
    
    subgraph "Result Processing"
        RELEVANCE_JUDGE["RelevanceJudgementAgent"]
        SNOWBALL_AGENT["SnowballAgent"]
        FINAL_RANKING["Result Ranking & Filtering"]
    end
    
    API_ENDPOINT --> REQUEST_MODEL
    REQUEST_MODEL --> QUERY_ANALYZER
    QUERY_ANALYZER --> METADATA_PLANNER
    METADATA_PLANNER --> SEARCH_DISPATCH
    
    SEARCH_DISPATCH --> DENSE_AGENT
    SEARCH_DISPATCH --> KEYWORD_AGENT
    SEARCH_DISPATCH --> CITATION_AGENT
    SEARCH_DISPATCH --> TITLE_AGENT
    SEARCH_DISPATCH --> AUTHOR_AGENT
    
    DENSE_AGENT --> RELEVANCE_JUDGE
    KEYWORD_AGENT --> RELEVANCE_JUDGE
    CITATION_AGENT --> RELEVANCE_JUDGE
    TITLE_AGENT --> RELEVANCE_JUDGE
    AUTHOR_AGENT --> RELEVANCE_JUDGE
    
    RELEVANCE_JUDGE --> SNOWBALL_AGENT
    SNOWBALL_AGENT --> FINAL_RANKING
    FINAL_RANKING --> RESPONSE_MODEL
```

**Sources:** [README.md:11]()

## Development and Testing

### Local Development Setup

To start the development server:

```bash
cd agents/mabool/api
make start-dev
```

### API Interaction

Once the server is running on `http://localhost:8000`, the API can be accessed through:

- **cURL**: Command-line HTTP requests
- **Swagger UI**: Interactive API documentation at `http://localhost:8000/docs`
- **ReDoc**: Alternative API documentation at `http://localhost:8000/redoc`

**Sources:** [README.md:35-40]()

---

