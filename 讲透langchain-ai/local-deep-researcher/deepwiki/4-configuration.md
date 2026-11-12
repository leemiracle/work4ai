<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/local-deep-researcher · page 4 Configuration · fetched 2026-10-26 -->

# Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [src/ollama_deep_researcher/configuration.py](src/ollama_deep_researcher/configuration.py)

</details>



This document covers the configuration system for the Local Deep Researcher, including all available configuration options, their sources, and how they are processed by the system. This includes LLM provider settings, search API configuration, and operational parameters that control the research workflow behavior.

For deployment-specific configuration, see [Deployment](#5). For LangGraph framework configuration details, see [LangGraph Configuration](#4.2).

## Configuration Sources and Priority

The Local Deep Researcher uses a hierarchical configuration system with three primary sources, processed in order of priority:

```mermaid
graph TB
    subgraph "Configuration Priority Hierarchy"
        P1[Priority1] --> EnvVars["Environment Variables<br/>(.env file)"]
        P2[Priority2] --> UIConfig["LangGraph Studio UI<br/>(Runtime configurable)"]
        P3[Priority3] --> Defaults["Default Values<br/>(Configuration class)"]
    end
    
    subgraph "Configuration Processing"
        ConfigClass["Configuration.from_runnable_config()"] --> Validation["Pydantic Validation"]
        Validation --> ConfigInstance["Configuration Instance"]
    end
    
    subgraph "Configuration Categories"
        LLMConfig["LLM Configuration<br/>• llm_provider<br/>• local_llm<br/>• ollama_base_url<br/>• lmstudio_base_url"]
        SearchConfig["Search Configuration<br/>• search_api<br/>• tavily_api_key<br/>• perplexity_api_key<br/>• searxng_url"]
        OpConfig["Operational Configuration<br/>• max_web_research_loops<br/>• fetch_full_page<br/>• strip_thinking_tokens"]
    end
    
    EnvVars --> ConfigClass
    UIConfig --> ConfigClass
    Defaults --> ConfigClass
    
    ConfigInstance --> LLMConfig
    ConfigInstance --> SearchConfig
    ConfigInstance --> OpConfig
```

The configuration system loads values using the `Configuration.from_runnable_config()` method, which checks environment variables first, then configurable parameters from the LangGraph runtime, and finally falls back to default values defined in the `Configuration` class.

**Sources:** [src/ollama_deep_researcher/configuration.py:58-76](), [.env.example:1-17]()

## LLM Provider Configuration

The system supports two local LLM providers with distinct configuration requirements:

| Configuration Field | Type | Default | Description |
|---------------------|------|---------|-------------|
| `llm_provider` | `"ollama"` \| `"lmstudio"` | `"ollama"` | LLM service provider |
| `local_llm` | `str` | `"llama3.2"` | Model name in the provider |
| `ollama_base_url` | `str` | `"http://localhost:11434/"` | Ollama API endpoint |
| `lmstudio_base_url` | `str` | `"http://localhost:1234/v1"` | LMStudio OpenAI-compatible API |
| `strip_thinking_tokens` | `bool` | `true` | Remove `` tags are removed from model responses, which is particularly useful for reasoning models that output their thought process.

**Sources:** [src/ollama_deep_researcher/configuration.py:22-31](), [src/ollama_deep_researcher/configuration.py:42-56](), [.env.example:10-14]()

## Search API Configuration

The system integrates with multiple web search providers through a unified configuration interface:

```mermaid
graph TB
    subgraph "SearchAPI Enum Values"
        SearchAPIEnum["SearchAPI Enum"] --> DDG["DUCKDUCKGO = 'duckduckgo'"]
        SearchAPIEnum --> Tavily["TAVILY = 'tavily'"]
        SearchAPIEnum --> Perplexity["PERPLEXITY = 'perplexity'"]
        SearchAPIEnum --> SearXNG["SEARXNG = 'searxng'"]
    end
    
    subgraph "Authentication Requirements"
        DDG --> NoAuth["No API key required<br/>(Default option)"]
        Tavily --> TavilyKey["TAVILY_API_KEY<br/>tvly-xxxxx format"]
        Perplexity --> PerplexityKey["PERPLEXITY_API_KEY<br/>pplx-xxxxx format"]
        SearXNG --> SearXNGURL["SEARXNG_URL<br/>Self-hosted endpoint"]
    end
    
    subgraph "Configuration Fields"
        SearchConfig["search_api field<br/>(Configuration class)"] --> ProviderSelection["Selected provider"]
        FetchConfig["fetch_full_page field<br/>(bool, default: True)"] --> ContentDepth["Full page content vs summaries"]
    end
    
    ProviderSelection --> NoAuth
    ProviderSelection --> TavilyKey
    ProviderSelection --> PerplexityKey
    ProviderSelection --> SearXNGURL
```

| Provider | Configuration | Authentication | Default URL |
|----------|---------------|----------------|-------------|
| DuckDuckGo | `search_api="duckduckgo"` | None required | Built-in |
| Tavily | `search_api="tavily"` | `TAVILY_API_KEY` | `https://api.tavily.com` |
| Perplexity | `search_api="perplexity"` | `PERPLEXITY_API_KEY` | `https://api.perplexity.ai` |
| SearXNG | `search_api="searxng"` | `SEARXNG_URL` | `http://localhost:8888` |

The `fetch_full_page` parameter determines whether the system retrieves complete webpage content or just summaries from search results, affecting both research depth and processing time.

**Sources:** [src/ollama_deep_researcher/configuration.py:8-12](), [src/ollama_deep_researcher/configuration.py:32-41](), [.env.example:1-8]()

## Operational Parameters

Core operational settings control the research workflow behavior:

| Parameter | Type | Default | Environment Variable | Description |
|-----------|------|---------|---------------------|-------------|
| `max_web_research_loops` | `int` | `3` | `MAX_WEB_RESEARCH_LOOPS` | Research iteration limit |
| `fetch_full_page` | `bool` | `true` | `FETCH_FULL_PAGE` | Retrieve complete page content |
| `strip_thinking_tokens` | `bool` | `true` | `STRIP_THINKING_TOKENS` | Remove thinking tags from responses |

```mermaid
graph TD
    subgraph "Research Loop Control"
        StartResearch["Begin Research"] --> GenerateQuery["Generate Search Query"]
        GenerateQuery --> ExecuteSearch["Execute Web Search"]
        ExecuteSearch --> ProcessResults["Process Results<br/>(fetch_full_page setting)"]
        ProcessResults --> UpdateState["Update SummaryState"]
        UpdateState --> CheckLoop{"research_loop_count <br/>< max_web_research_loops?"}
        CheckLoop -->|Yes| GenerateQuery
        CheckLoop -->|No| FinishResearch["Finalize Summary"]
    end
    
    subgraph "Response Processing"
        LLMResponse["Raw LLM Response"] --> ThinkingCheck{"strip_thinking_tokens<br/>enabled?"}
        ThinkingCheck -->|Yes| StripTokens["Remove <think> tags"]
        ThinkingCheck -->|No| PassThrough["Use raw response"]
        StripTokens --> CleanResponse["Clean Response"]
        PassThrough --> CleanResponse
    end
```

These parameters directly control the research workflow execution, with `max_web_research_loops` preventing infinite research cycles and `fetch_full_page` balancing research depth against processing speed.

**Sources:** [src/ollama_deep_researcher/configuration.py:17-21](), [src/ollama_deep_researcher/configuration.py:37-41](), [src/ollama_deep_researcher/configuration.py:52-56](), [.env.example:16-17]()

## Configuration Loading Process

The configuration system uses Pydantic for validation and type safety, with a custom loading mechanism that handles environment variables and runtime configuration:

```mermaid
graph TD
    subgraph "Configuration Loading Flow"
        RunnableConfig["RunnableConfig<br/>(from LangGraph)"] --> FromRunnable["Configuration.from_runnable_config()"]
        EnvVars["Environment Variables<br/>(os.environ)"] --> FromRunnable
        
        FromRunnable --> ExtractConfigurable["Extract 'configurable' dict"]
        ExtractConfigurable --> BuildRawValues["Build raw_values dict<br/>(env vars + configurable)"]
        BuildRawValues --> FilterNone["Filter None values"]
        FilterNone --> PydanticConstruct["Configuration(**values)"]
        PydanticConstruct --> ValidatedConfig["Validated Configuration"]
    end
    
    subgraph "Field Resolution Priority"
        FieldName["Configuration field name"] --> EnvLookup["os.environ.get(name.upper())"]
        EnvLookup --> ConfigLookup["configurable.get(name)"]
        ConfigLookup --> DefaultValue["Field default value"]
    end
    
    subgraph "Pydantic Validation"
        ValidatedConfig --> FieldValidation["Per-field type validation"]
        FieldValidation --> EnumValidation["Enum constraint checking"]
        EnumValidation --> ConfigInstance["Final Configuration instance"]
    end
```

The loading process follows this sequence:

1. **Extract values**: For each field in `Configuration.model_fields`, check environment variables using uppercase field names
2. **Runtime override**: Check the `configurable` dictionary from `RunnableConfig` for runtime values
3. **Filter and construct**: Remove `None` values and construct the `Configuration` instance
4. **Validate**: Pydantic validates types, constraints, and enum values

**Sources:** [src/ollama_deep_researcher/configuration.py:58-76](), [src/ollama_deep_researcher/configuration.py:14-56]()

---

