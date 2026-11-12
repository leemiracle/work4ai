<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/local-deep-researcher · page 2 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [src/ollama_deep_researcher/graph.py](src/ollama_deep_researcher/graph.py)

</details>



This document describes the overall system architecture of the Local Deep Researcher, focusing on the LangGraph-orchestrated research workflow, component interactions, and integration patterns. For specific implementation details of individual components, see [Core Components](#3). For configuration details, see [Configuration](#4). For deployment architecture, see [Deployment](#5).

The Local Deep Researcher implements an iterative web research system built on LangGraph's state machine framework. The architecture coordinates between local LLM providers, multiple search APIs, and a configurable workflow engine to produce comprehensive research summaries with proper citations.

## LangGraph State Machine Architecture

The core system is implemented as a LangGraph StateGraph that orchestrates the research workflow through a series of connected nodes. Each node represents a distinct phase in the research process.

### Research Workflow State Machine

```mermaid
stateDiagram-v2
    [*] --> generate_query
    generate_query --> web_research
    web_research --> summarize_sources
    summarize_sources --> reflect_on_summary
    reflect_on_summary --> web_research: "research_loop_count <= max_web_research_loops"
    reflect_on_summary --> finalize_summary: "research_loop_count > max_web_research_loops"
    finalize_summary --> [*]
```

**LangGraph Node Implementation**

The StateGraph is defined in [src/ollama_deep_researcher/graph.py:445-465]() with the following node structure:

| Node | Function | Purpose |
|------|----------|---------|
| `generate_query` | [graph.py:138-189]() | Generates initial search query using LLM |
| `web_research` | [graph.py:192-262]() | Executes web search using configured API |
| `summarize_sources` | [graph.py:265-328]() | Creates/updates running summary with LLM |
| `reflect_on_summary` | [graph.py:331-384]() | Identifies knowledge gaps and generates follow-up queries |
| `finalize_summary` | [graph.py:387-418]() | Formats final output with deduplicated sources |

Sources: [src/ollama_deep_researcher/graph.py:445-465](), [src/ollama_deep_researcher/graph.py:138-418]()

### State Management Schema

```mermaid
classDiagram
    class SummaryState {
        +str research_topic
        +str search_query
        +str running_summary
        +list~str~ sources_gathered
        +list~str~ web_research_results
        +int research_loop_count
    }
    
    class SummaryStateInput {
        +str research_topic
    }
    
    class SummaryStateOutput {
        +str running_summary
        +list~str~ sources_gathered
    }
    
    SummaryState --> SummaryStateInput : "input_schema"
    SummaryState --> SummaryStateOutput : "output_schema"
```

The state management system tracks research progress and accumulated data across the iterative workflow. The `SummaryState` class maintains all necessary context between node executions.

Sources: [src/ollama_deep_researcher/state.py]()

## Component Integration Architecture

The system integrates multiple external services through a configuration-driven abstraction layer that allows runtime selection of LLM providers and search APIs.

### LLM Provider Integration

```mermaid
graph TD
    Configuration["Configuration"] --> get_llm["get_llm()"]
    get_llm --> llm_provider_check{"llm_provider == 'lmstudio'?"}
    
    llm_provider_check -->|Yes| lmstudio_branch["ChatLMStudio"]
    llm_provider_check -->|No| ollama_branch["ChatOllama"]
    
    lmstudio_branch --> tool_calling_check1{"use_tool_calling?"}
    ollama_branch --> tool_calling_check2{"use_tool_calling?"}
    
    tool_calling_check1 -->|Yes| ChatLMStudio_tool["ChatLMStudio(temperature=0)"]
    tool_calling_check1 -->|No| ChatLMStudio_json["ChatLMStudio(format='json')"]
    
    tool_calling_check2 -->|Yes| ChatOllama_tool["ChatOllama(temperature=0)"]
    tool_calling_check2 -->|No| ChatOllama_json["ChatOllama(format='json')"]
```

The `get_llm()` function [graph.py:97-135]() provides a unified interface for LLM instantiation, supporting both structured output modes (JSON format and tool calling) across different providers.

Sources: [src/ollama_deep_researcher/graph.py:97-135](), [src/ollama_deep_researcher/lmstudio.py]()

### Search API Integration

```mermaid
graph TD
    web_research["web_research()"] --> get_config_value["get_config_value(search_api)"]
    get_config_value --> search_api_router{"search_api value"}
    
    search_api_router -->|"tavily"| tavily_search["tavily_search()"]
    search_api_router -->|"perplexity"| perplexity_search["perplexity_search()"]
    search_api_router -->|"duckduckgo"| duckduckgo_search["duckduckgo_search()"]
    search_api_router -->|"searxng"| searxng_search["searxng_search()"]
    
    tavily_search --> deduplicate_and_format_sources["deduplicate_and_format_sources()"]
    perplexity_search --> deduplicate_and_format_sources
    duckduckgo_search --> deduplicate_and_format_sources
    searxng_search --> deduplicate_and_format_sources
    
    deduplicate_and_format_sources --> format_sources["format_sources()"]
```

The search integration layer [graph.py:192-262]() provides a unified interface for multiple search APIs, with consistent result formatting and deduplication across all providers.

Sources: [src/ollama_deep_researcher/graph.py:192-262](), [src/ollama_deep_researcher/utils.py]()

## Structured Output Architecture

The system supports two modes for extracting structured data from LLMs: tool calling and JSON mode. This dual approach ensures compatibility across different model capabilities.

### Structured Output Flow

```mermaid
graph TD
    generate_search_query_with_structured_output["generate_search_query_with_structured_output()"] --> use_tool_calling_check{"configurable.use_tool_calling?"}
    
    use_tool_calling_check -->|True| tool_calling_branch["Tool Calling Mode"]
    use_tool_calling_check -->|False| json_mode_branch["JSON Mode"]
    
    tool_calling_branch --> bind_tools["llm.bind_tools([tool_class])"]
    bind_tools --> invoke_tool["llm.invoke(messages)"]
    invoke_tool --> extract_tool_args["result.tool_calls[0]['args']"]
    
    json_mode_branch --> json_format["llm with format='json'"]
    json_format --> invoke_json["llm.invoke(messages)"]
    invoke_json --> parse_json["json.loads(content)"]
    
    extract_tool_args --> return_query["return {'search_query': query}"]
    parse_json --> return_query
```

The `generate_search_query_with_structured_output()` function [graph.py:44-95]() handles both output modes with fallback mechanisms for failed extractions.

Sources: [src/ollama_deep_researcher/graph.py:44-95]()

## Configuration Integration Architecture

The system implements a three-tier configuration hierarchy that allows flexible deployment while maintaining reasonable defaults.

### Configuration Resolution Flow

```mermaid
graph TD
    Configuration_from_runnable_config["Configuration.from_runnable_config(config)"] --> env_vars["Environment Variables"]
    Configuration_from_runnable_config --> langgraph_ui["LangGraph UI Configuration"]
    Configuration_from_runnable_config --> defaults["Configuration Class Defaults"]
    
    env_vars -->|"Highest Priority"| final_config["Final Configuration"]
    langgraph_ui -->|"Medium Priority"| final_config
    defaults -->|"Lowest Priority"| final_config
    
    final_config --> llm_provider["llm_provider"]
    final_config --> search_api["search_api"]
    final_config --> max_web_research_loops["max_web_research_loops"]
    final_config --> use_tool_calling["use_tool_calling"]
```

The configuration system allows runtime customization through multiple channels while ensuring the system remains functional with minimal setup.

Sources: [src/ollama_deep_researcher/configuration.py](), [README.md:135-141]()

## System Boundaries and External Dependencies

The Local Deep Researcher maintains clear boundaries between internal orchestration logic and external service dependencies.

### External Service Integration

```mermaid
graph LR
    subgraph "Local Deep Researcher"
        StateGraph["StateGraph"]
        Configuration["Configuration"]
        Utils["Search Utils"]
    end
    
    subgraph "LLM Providers"
        Ollama["Ollama Service<br/>localhost:11434"]
        LMStudio["LMStudio Service<br/>localhost:1234"]
    end
    
    subgraph "Search APIs"
        DuckDuckGo["DuckDuckGo"]
        Tavily["Tavily API"]
        Perplexity["Perplexity API"]
        SearXNG["SearXNG"]
    end
    
    subgraph "LangGraph Framework"
        LangGraphStudio["LangGraph Studio<br/>Port 2024"]
        LangSmith["LangSmith Tracing"]
    end
    
    Configuration --> Ollama
    Configuration --> LMStudio
    Utils --> DuckDuckGo
    Utils --> Tavily
    Utils --> Perplexity
    Utils --> SearXNG
    StateGraph --> LangGraphStudio
    StateGraph --> LangSmith
```

The architecture maintains loose coupling with external services through configuration-driven service selection and standardized interfaces.

Sources: [src/ollama_deep_researcher/graph.py](), [src/ollama_deep_researcher/utils.py](), [src/ollama_deep_researcher/configuration.py]()

---

