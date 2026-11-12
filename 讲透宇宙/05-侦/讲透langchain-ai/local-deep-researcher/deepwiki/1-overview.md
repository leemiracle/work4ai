<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/local-deep-researcher · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

Local Deep Researcher is a LangGraph-orchestrated web research assistant that uses local LLMs to conduct iterative, autonomous research on user-provided topics. The system integrates with local LLM providers (Ollama, LMStudio) and multiple search APIs to generate comprehensive research summaries with citations.

This document provides a high-level technical overview of the system architecture, core components, and capabilities. For detailed project structure and dependencies, see [Project Structure](#1.1). For comprehensive deployment information, see [Deployment](#5). For step-by-step usage instructions, see [Usage Guide](#6).

## System Architecture

The Local Deep Researcher implements a state machine-driven research workflow using LangGraph to orchestrate interactions between LLM providers, search APIs, and content processing components.

### Core Architecture Components

```mermaid
graph TB
    subgraph "Entry Points"
        langgraph_dev["langgraph dev command"]
        langgraph_studio["LangGraph Studio UI<br/>Port 2024"]
    end
    
    subgraph "Core Orchestration"
        graph_py["graph.py<br/>StateGraph Definition"]
        state_py["state.py<br/>SummaryState Class"]
        configuration_py["configuration.py<br/>Configuration Class"]
    end
    
    subgraph "LLM Integration Layer"
        ollama_integration["Ollama Integration<br/>langchain-ollama"]
        lmstudio_wrapper["LMStudio Wrapper<br/>Custom OpenAI Client"]
    end
    
    subgraph "Search Integration Layer" 
        utils_py["utils.py<br/>search_web() function"]
        duckduckgo["DuckDuckGo<br/>duckduckgo-search"]
        tavily["Tavily API<br/>tavily-python"]
        perplexity["Perplexity API<br/>httpx client"]
        searxng["SearXNG<br/>httpx client"]
    end
    
    subgraph "Processing Layer"
        prompts_py["prompts.py<br/>Prompt Templates"]
        markdownify_lib["markdownify<br/>Content Processing"]
    end
    
    langgraph_dev --> graph_py
    langgraph_studio --> graph_py
    graph_py --> state_py
    graph_py --> configuration_py
    graph_py --> prompts_py
    
    configuration_py --> ollama_integration
    configuration_py --> lmstudio_wrapper
    
    prompts_py --> ollama_integration
    prompts_py --> lmstudio_wrapper
    
    graph_py --> utils_py
    utils_py --> duckduckgo
    utils_py --> tavily
    utils_py --> perplexity
    utils_py --> searxng
    
    utils_py --> markdownify_lib
```

**Sources:** [README.md:1-221](), [langgraph.json](), [pyproject.toml]()

### Research Workflow State Machine

```mermaid
stateDiagram-v2
    [*] --> generate_query
    
    state generate_query {
        [*] --> prompts_generate_query_template
        prompts_generate_query_template --> LLM_invoke
        LLM_invoke --> SummaryState_search_query
        SummaryState_search_query --> [*]
    }
    
    generate_query --> search_web
    
    state search_web {
        [*] --> utils_search_web_function
        utils_search_web_function --> search_api_call
        search_api_call --> content_processing
        content_processing --> SummaryState_sources_gathered
        SummaryState_sources_gathered --> [*]
    }
    
    search_web --> summarize_findings
    
    state summarize_findings {
        [*] --> prompts_summarize_template
        prompts_summarize_template --> LLM_invoke
        LLM_invoke --> SummaryState_running_summary
        SummaryState_running_summary --> [*]
    }
    
    summarize_findings --> reflect_on_summary
    
    state reflect_on_summary {
        [*] --> prompts_reflect_template
        prompts_reflect_template --> LLM_invoke
        LLM_invoke --> loop_decision
        loop_decision --> SummaryState_research_loop_count
        SummaryState_research_loop_count --> [*]
    }
    
    reflect_on_summary --> conditional_continue
    conditional_continue --> generate_query : Continue Research
    conditional_continue --> finalize_summary : Complete Research
    
    finalize_summary --> [*]
```

**Sources:** [README.md:165-172](), [graph.py](), [state.py](), [prompts.py](), [utils.py]()

## Core Workflow Process

The system implements an iterative research methodology inspired by IterDRAG, using a configurable loop to progressively build comprehensive research summaries.

### Research Loop Components

| Component | Code Location | Purpose |
|-----------|---------------|---------|
| Query Generation | `prompts.py` templates | Convert research topic into targeted search queries |
| Web Search | `utils.py:search_web()` | Execute searches across configured APIs |
| Content Summarization | `prompts.py` templates | Extract relevant information from search results |
| Gap Analysis | `prompts.py` reflection templates | Identify knowledge gaps for follow-up research |
| State Management | `state.py:SummaryState` | Track progress and accumulate findings |

### Configuration-Driven Behavior

The system uses a three-tier configuration hierarchy:

1. **Environment Variables** (highest priority) - [.env file]()
2. **LangGraph Studio Configuration** - Runtime UI settings  
3. **Default Values** - [`configuration.py:Configuration`]() class defaults

Key configuration parameters include:

- `LLM_PROVIDER`: Selection between `ollama` and `lmstudio`
- `SEARCH_API`: Choice of `duckduckgo`, `tavily`, `perplexity`, or `searxng`
- `MAX_WEB_RESEARCH_LOOPS`: Iteration limit (default: 3)
- `FETCH_FULL_PAGE`: Content depth control for DuckDuckGo searches

**Sources:** [README.md:30-82](), [README.md:135-141](), [configuration.py]()

## Technology Stack

### Core Framework Dependencies

```mermaid
graph LR
    subgraph "Orchestration Framework"
        langgraph["langgraph<br/>State Machine"]
        langchain_core["langchain-core<br/>Base Classes"]
    end
    
    subgraph "LLM Integration"
        langchain_ollama["langchain-ollama<br/>Ollama Provider"]
        langchain_openai["langchain-openai<br/>OpenAI Compatible"]
        openai_client["openai<br/>LMStudio Client"]
    end
    
    subgraph "Search Libraries"
        duckduckgo_search["duckduckgo-search<br/>DDG API"]
        tavily_python["tavily-python<br/>Tavily SDK"]
        httpx["httpx<br/>HTTP Client"]
    end
    
    subgraph "Development Tools"
        uv_package_manager["uv<br/>Package Manager"] 
        python_dotenv["python-dotenv<br/>Environment Loading"]
        pydantic["pydantic<br/>Data Validation"]
    end
    
    langgraph --> langchain_core
    langchain_ollama --> langchain_core
    langchain_openai --> langchain_core
    openai_client --> langchain_openai
    
    httpx --> tavily_python
    httpx --> perplexity_api["Perplexity API"]
    httpx --> searxng_api["SearXNG API"]
```

**Sources:** [pyproject.toml](), [README.md:96-98](), [README.md:116-119]()

## Key Capabilities

### Multi-Provider LLM Support

The system supports both local and cloud-based LLM providers through standardized interfaces:

- **Ollama Integration**: Direct connection to local Ollama service at `http://localhost:11434`
- **LMStudio Integration**: OpenAI-compatible API wrapper for LMStudio at `http://localhost:1234/v1`
- **Fallback Mechanisms**: Automatic handling of models with limited JSON support

### Search API Abstraction

Unified search interface supporting multiple providers:

- **DuckDuckGo**: No API key required, optional full-page content fetching
- **Tavily**: Commercial search API with structured results
- **Perplexity**: AI-powered search with Sonar API integration  
- **SearXNG**: Self-hosted metasearch engine support

### Deployment Flexibility

- **Development Mode**: `langgraph dev` command with hot reload
- **Production Deployment**: Multi-architecture Docker containers
- **CI/CD Pipeline**: Automated GitHub Actions workflows for container builds

**Sources:** [README.md:35-82](), [README.md:193-221](), [Dockerfile](), [.github/workflows/docker-image.yml]()

---

