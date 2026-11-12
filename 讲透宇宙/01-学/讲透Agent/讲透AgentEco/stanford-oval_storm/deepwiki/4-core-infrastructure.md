<!-- source: DeepWiki mcp.deepwiki.com · repo stanford-oval/storm · page 4 Core Infrastructure · fetched 2026-10-27 -->

# Core Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [knowledge_storm/interface.py](knowledge_storm/interface.py)
- [knowledge_storm/lm.py](knowledge_storm/lm.py)

</details>



This document provides an overview of the shared infrastructure components that power both STORM and Co-STORM systems. The core infrastructure consists of three main integration layers (Language Models, Retrieval Modules, and Encoders) and a set of abstract interfaces that define contracts for custom implementations.

For detailed information about specific components:
- Language model integration and caching: see [Language Model Integration](#4.1)
- Retrieval module implementations: see [Retrieval Modules](#4.2)
- Text embedding generation: see [Encoder System](#4.3)
- Utility classes and helpers: see [Utilities and Helpers](#4.4)
- Abstract base classes and interfaces: see [Abstract Interfaces](#4.5)

## Purpose and Scope

The core infrastructure provides a provider-agnostic abstraction layer that allows both STORM and Co-STORM to operate with 100+ different LLM providers (via LiteLLM) and 11+ different search engines without changing application logic. This layer handles:

1. **Language Model Integration**: Universal wrapper for LLM providers with caching and token tracking
2. **Retrieval Module Integration**: Unified interface to web search engines, vector databases, and specialized retrievers
3. **Encoder Integration**: Text embedding generation for semantic similarity operations
4. **Abstract Interfaces**: Base classes that define contracts for custom implementations
5. **Performance Optimization**: Two-tier caching (LRU + disk), thread-safe token tracking, parallel query execution

The infrastructure is designed to be modular and extensible, allowing users to swap providers or implement custom components by adhering to the defined interfaces.

## Infrastructure Architecture

The following diagram shows the layered architecture of the core infrastructure and how it integrates with the two main systems (STORM and Co-STORM):

```mermaid
graph TB
    subgraph "Application Layer"
        STORMRunner["STORMWikiRunner<br/>(storm_wiki/engine.py)"]
        CoSTORMRunner["CoStormRunner<br/>(collaborative_storm/engine.py)"]
    end
    
    subgraph "Configuration Layer"
        STORMLMConfigs["STORMWikiLMConfigs<br/>(storm_wiki/engine.py)"]
        CoSTORMLMConfigs["CollaborativeStormLMConfigs<br/>(collaborative_storm/engine.py)"]
        EngineBase["Engine (interface.py)<br/>- lm_configs<br/>- time tracking<br/>- lm_cost / rm_cost"]
    end
    
    subgraph "Integration Layer - language models"
        LitellmModel["LitellmModel (lm.py)<br/>- Two-tier caching<br/>- Token tracking<br/>- Thread-safe counters"]
        LM["LM base class<br/>(from dspy via litellm)"]
    end
    
    subgraph "Integration Layer - retrieval"
        Retriever["Retriever (interface.py)<br/>- retrieve()<br/>- max_thread"]
        RMImpls["RM Implementations<br/>YouRM, BingSearch<br/>VectorRM, SerperRM<br/>BraveRM, etc. (rm.py)"]
    end
    
    subgraph "Integration Layer - embeddings"
        Encoder["Encoder (encoder.py)<br/>- get_embedding()<br/>- Token tracking"]
    end
    
    subgraph "External Services"
        LLMProviders["100+ LLM Providers<br/>(via litellm routing)"]
        SearchAPIs["Search Engine APIs<br/>Bing, Google, You.com, etc."]
        VectorDBs["Vector Databases<br/>Qdrant, etc."]
    end
    
    STORMRunner --> EngineBase
    CoSTORMRunner --> EngineBase
    EngineBase --> STORMLMConfigs
    EngineBase --> CoSTORMLMConfigs
    
    STORMLMConfigs --> LitellmModel
    CoSTORMLMConfigs --> LitellmModel
    LitellmModel --> LM
    
    STORMRunner --> Retriever
    CoSTORMRunner --> Retriever
    Retriever --> RMImpls
    
    CoSTORMRunner --> Encoder
    
    LM --> LLMProviders
    RMImpls --> SearchAPIs
    RMImpls --> VectorDBs
    Encoder --> LLMProviders
```

**Sources**: [knowledge_storm/interface.py:485-563](), [knowledge_storm/lm.py:192-269]()

The architecture consists of four distinct layers:

1. **Application Layer**: Contains `STORMWikiRunner` and `CoStormRunner` which orchestrate the respective pipelines
2. **Configuration Layer**: Manages LM configurations and tracks execution metrics through the `Engine` base class
3. **Integration Layer**: Provides universal wrappers for LLMs (`LitellmModel`), retrievers (`Retriever`), and embeddings (`Encoder`)
4. **External Services**: The actual LLM providers, search engines, and vector databases

## Language Model Integration Architecture

The language model integration is built around the `LitellmModel` class, which wraps the LiteLLM library to provide access to 100+ LLM providers. The following diagram shows how language model requests flow through the system:

```mermaid
graph TB
    subgraph "Configuration Management"
        LMConfigs["LMConfigs (interface.py:427-483)<br/>Abstract base class<br/>- collect_and_reset_lm_usage()<br/>- collect_and_reset_lm_history()"]
        STORMConfigs["STORMWikiLMConfigs<br/>- conv_simulator_lm<br/>- question_asker_lm<br/>- outline_gen_lm<br/>- article_gen_lm<br/>- article_polish_lm"]
        CoSTORMConfigs["CollaborativeStormLMConfigs<br/>- question_answering_lm<br/>- discourse_manage_lm<br/>- utterance_polishing_lm<br/>- warmstart_outline_gen_lm<br/>- question_asking_lm<br/>- knowledge_base_lm"]
    end
    
    subgraph "LM Wrapper Layer"
        LitellmModelClass["LitellmModel (lm.py:192-269)<br/>Attributes:<br/>- model: str<br/>- model_type: 'chat' or 'text'<br/>- prompt_tokens: int<br/>- completion_tokens: int<br/>- _token_usage_lock: Lock<br/>Methods:<br/>- __call__(prompt, messages, **kwargs)<br/>- log_usage(response)<br/>- get_usage_and_reset()"]
    end
    
    subgraph "Caching Layer"
        LRUCache["LRU Cache (lm.py:115-129)<br/>@functools.lru_cache<br/>maxsize=3000"]
        DiskCache["Disk Cache (lm.py:40-43)<br/>litellm.cache<br/>disk_cache_dir:<br/>~/.storm_local_cache"]
    end
    
    subgraph "LiteLLM Library"
        LitellmCompletion["litellm.completion()<br/>Universal LLM interface"]
    end
    
    LMConfigs --> STORMConfigs
    LMConfigs --> CoSTORMConfigs
    STORMConfigs --> LitellmModelClass
    CoSTORMConfigs --> LitellmModelClass
    
    LitellmModelClass --> LRUCache
    LRUCache --> DiskCache
    DiskCache --> LitellmCompletion
    LitellmCompletion --> LitellmModelClass
```

**Sources**: [knowledge_storm/lm.py:192-269](), [knowledge_storm/interface.py:427-483](), [knowledge_storm/lm.py:40-43](), [knowledge_storm/lm.py:115-129]()

### Key Components

| Component | File Location | Purpose |
|-----------|--------------|---------|
| `LitellmModel` | [knowledge_storm/lm.py:192-269]() | Main wrapper class that provides thread-safe token tracking and integrates with caching layers |
| `LM` base class | [knowledge_storm/lm.py:57-114]() | Parent class from DSPy that defines the interface |
| `cached_litellm_completion` | [knowledge_storm/lm.py:115-117]() | LRU cache decorator with maxsize=3000 |
| `litellm.cache` | [knowledge_storm/lm.py:40-43]() | Disk cache initialized at `~/.storm_local_cache` |
| `LMConfigs` | [knowledge_storm/interface.py:427-483]() | Abstract base for collecting usage statistics |

### Token Tracking

The `LitellmModel` class implements thread-safe token counting using a `threading.Lock`:

```python
# From lm.py:206-216
self._token_usage_lock = threading.Lock()
self.prompt_tokens = 0
self.completion_tokens = 0

def log_usage(self, response):
    usage_data = response.get("usage")
    if usage_data:
        with self._token_usage_lock:
            self.prompt_tokens += usage_data.get("prompt_tokens", 0)
            self.completion_tokens += usage_data.get("completion_tokens", 0)
```

This allows multiple modules to safely track token usage concurrently. The `Engine` base class aggregates usage statistics from all configured LMs via `collect_and_reset_lm_usage()` [knowledge_storm/interface.py:452-473]().

**Sources**: [knowledge_storm/lm.py:206-232](), [knowledge_storm/interface.py:452-473]()

## Retrieval Module Architecture

The retrieval module layer provides a unified interface to 11+ different search engines and retrieval backends. The following diagram shows the retrieval architecture and concrete implementations:

```mermaid
graph TB
    subgraph "Abstract Interface"
        RetrieverBase["Retriever (interface.py:260-319)<br/>Attributes:<br/>- rm: dspy.Retrieve<br/>- max_thread: int<br/>Methods:<br/>- retrieve(query, exclude_urls)<br/>- collect_and_reset_rm_usage()"]
    end
    
    subgraph "Concrete RM Implementations"
        YouRM["YouRM (rm.py)<br/>You.com search"]
        BingSearch["BingSearch (rm.py)<br/>Bing Web Search API"]
        VectorRM["VectorRM (rm.py)<br/>Qdrant vector DB"]
        SerperRM["SerperRM (rm.py)<br/>Serper.dev API"]
        BraveRM["BraveRM (rm.py)<br/>Brave Search API"]
        DuckDuckGo["DuckDuckGoSearchRM (rm.py)<br/>DuckDuckGo search"]
        Tavily["TavilySearchRM (rm.py)<br/>Tavily AI search"]
        GoogleSearch["GoogleSearch (rm.py)<br/>Google Custom Search"]
        AzureAI["AzureAISearch (rm.py)<br/>Azure Cognitive Search"]
        SearXNG["SearXNG (rm.py)<br/>SearXNG metasearch"]
        ArxivRM["StanfordOvalArxivRM (rm.py)<br/>ArXiv papers"]
    end
    
    subgraph "Data Processing"
        WebPageHelper["WebPageHelper (utils.py)<br/>- fetch_webpage()<br/>- limit_word_count_preserve_newline()"]
        Information["Information (interface.py:41-134)<br/>Attributes:<br/>- url: str<br/>- description: str<br/>- snippets: List[str]<br/>- title: str<br/>- meta: dict<br/>- citation_uuid: int"]
    end
    
    RetrieverBase --> YouRM
    RetrieverBase --> BingSearch
    RetrieverBase --> VectorRM
    RetrieverBase --> SerperRM
    RetrieverBase --> BraveRM
    RetrieverBase --> DuckDuckGo
    RetrieverBase --> Tavily
    RetrieverBase --> GoogleSearch
    RetrieverBase --> AzureAI
    RetrieverBase --> SearXNG
    RetrieverBase --> ArxivRM
    
    YouRM --> WebPageHelper
    BingSearch --> WebPageHelper
    SerperRM --> WebPageHelper
    BraveRM --> WebPageHelper
    DuckDuckGo --> WebPageHelper
    Tavily --> WebPageHelper
    
    WebPageHelper --> Information
```

**Sources**: [knowledge_storm/interface.py:260-319](), [knowledge_storm/interface.py:41-134]()

### Retriever Interface

The `Retriever` base class [knowledge_storm/interface.py:260-319]() provides:

1. **Parallel Query Execution**: Uses `ThreadPoolExecutor` with configurable `max_thread` to process multiple queries concurrently [knowledge_storm/interface.py:311-317]()
2. **Citation Processing**: Automatically removes citations from retrieved snippets to avoid confusion [knowledge_storm/interface.py:303-305]()
3. **Information Standardization**: Converts all retrieval results to `Information` objects with consistent schema [knowledge_storm/interface.py:306-308]()
4. **Usage Tracking**: Collects query counts from RM implementations via `collect_and_reset_rm_usage()` [knowledge_storm/interface.py:273-286]()

### Retrieval Module Implementations

Each RM implementation follows the pattern defined by DSPy's `dspy.Retrieve` interface and returns data in a standardized format that includes:

- `url`: Unique identifier for the source
- `snippets`: List of text excerpts
- `title`: Source title
- `description`: Brief source description

The `WebPageHelper` utility class [knowledge_storm/utils.py]() provides common functionality for fetching and processing web content used by multiple RM implementations.

**Sources**: [knowledge_storm/interface.py:260-319](), [knowledge_storm/interface.py:288-319]()

## Abstract Interface System

The codebase defines a comprehensive set of abstract interfaces in [knowledge_storm/interface.py]() that enable modularity and custom implementations. The following diagram shows the key abstract base classes and their relationships:

```mermaid
graph TB
    subgraph "Data Abstractions"
        InformationTable["InformationTable (interface.py:23-38)<br/>Abstract base class<br/>Method:<br/>- retrieve_information(**kwargs)"]
        Article["Article (interface.py:162-258)<br/>Abstract base class<br/>Attributes:<br/>- root: ArticleSectionNode<br/>Methods:<br/>- to_string()<br/>- from_string()<br/>- find_section()<br/>- get_outline_tree()"]
        ArticleSectionNode["ArticleSectionNode (interface.py:136-160)<br/>Concrete class<br/>Attributes:<br/>- section_name: str<br/>- content: Any<br/>- children: List<br/>- preference: Any"]
    end
    
    subgraph "Module Abstractions"
        KnowledgeCuration["KnowledgeCurationModule (interface.py:322-344)<br/>Abstract method:<br/>- research(topic) -> InformationTable"]
        OutlineGeneration["OutlineGenerationModule (interface.py:347-369)<br/>Abstract method:<br/>- generate_outline(topic, information_table, **kwargs) -> Article"]
        ArticleGenerationMod["ArticleGenerationModule (interface.py:372-392)<br/>Abstract method:<br/>- generate_article(topic, information_table, article_with_outline, **kwargs) -> Article"]
        ArticlePolishing["ArticlePolishingModule (interface.py:395-408)<br/>Abstract method:<br/>- polish_article(topic, draft_article, **kwargs) -> Article"]
    end
    
    subgraph "Engine Abstraction"
        Engine["Engine (interface.py:485-563)<br/>Abstract base class<br/>Attributes:<br/>- lm_configs: LMConfigs<br/>- time: dict<br/>- lm_cost: dict<br/>- rm_cost: dict<br/>Abstract methods:<br/>- run_knowledge_curation_module()<br/>- run_outline_generation_module()<br/>- run_article_generation_module()<br/>- run_article_polishing_module()<br/>- run()"]
        LMConfigsAbs["LMConfigs (interface.py:427-483)<br/>Abstract base class<br/>Methods:<br/>- collect_and_reset_lm_history()<br/>- collect_and_reset_lm_usage()<br/>- log()"]
    end
    
    subgraph "Agent Abstraction"
        Agent["Agent (interface.py:565-608)<br/>Abstract base class<br/>Attributes:<br/>- topic: str<br/>- role_name: str<br/>- role_description: str<br/>Abstract method:<br/>- generate_utterance(knowledge_base, conversation_history, logging_wrapper, **kwargs)"]
    end
    
    KnowledgeCuration --> InformationTable
    OutlineGeneration --> InformationTable
    OutlineGeneration --> Article
    ArticleGenerationMod --> InformationTable
    ArticleGenerationMod --> Article
    ArticlePolishing --> Article
    
    Article --> ArticleSectionNode
    
    Engine --> LMConfigsAbs
    Engine --> KnowledgeCuration
    Engine --> OutlineGeneration
    Engine --> ArticleGenerationMod
    Engine --> ArticlePolishing
```

**Sources**: [knowledge_storm/interface.py:23-608]()

### Key Abstract Contracts

| Abstract Class | Purpose | Key Methods | Implementations |
|----------------|---------|-------------|-----------------|
| `InformationTable` | Store collected information | `retrieve_information(**kwargs)` | `StormInformationTable` (STORM) |
| `Article` | Represent article structure | `to_string()`, `from_string()` | `StormArticle` (STORM) |
| `KnowledgeCurationModule` | Collect information | `research(topic)` | `StormKnowledgeCurationModule` |
| `OutlineGenerationModule` | Generate article outline | `generate_outline(topic, information_table)` | `StormOutlineGenerationModule` |
| `ArticleGenerationModule` | Write article sections | `generate_article(topic, information_table, article_with_outline)` | `StormArticleGenerationModule` |
| `ArticlePolishingModule` | Refine final article | `polish_article(topic, draft_article)` | `StormArticlePolishingModule` |
| `Engine` | Orchestrate pipeline | `run_knowledge_curation_module()`, etc. | `STORMWikiRunner`, `CoStormRunner` |
| `LMConfigs` | Manage LM configurations | `collect_and_reset_lm_usage()` | `STORMWikiLMConfigs`, `CollaborativeStormLMConfigs` |
| `Agent` | Generate conversational utterances | `generate_utterance()` | `CoStormExpert`, `Moderator`, `SimulatedUser` |

### Decorator Pattern for Execution Tracking

The `Engine` base class [knowledge_storm/interface.py:485-523]() provides the `log_execution_time_and_lm_rm_usage` decorator that automatically wraps methods starting with `run_` to track:

1. **Execution Time**: Duration of each pipeline stage
2. **LM Cost**: Token usage per stage via `lm_configs.collect_and_reset_lm_usage()`
3. **RM Cost**: Query count per stage via `retriever.collect_and_reset_rm_usage()`

This is applied automatically in the `apply_decorators()` method [knowledge_storm/interface.py:512-522]().

**Sources**: [knowledge_storm/interface.py:492-523]()

## Performance Optimization and Observability

The infrastructure layer implements several performance optimizations and observability features:

### Two-Tier Caching System

```mermaid
graph LR
    Request["LLM Request<br/>(prompt + params)"]
    LRUCheck{"In LRU Cache?<br/>(3000 entries)"}
    DiskCheck{"In Disk Cache?<br/>(~/.storm_local_cache)"}
    APICall["LiteLLM API Call<br/>litellm.completion()"]
    Response["LLM Response"]
    
    Request --> LRUCheck
    LRUCheck -->|"Yes"| Response
    LRUCheck -->|"No"| DiskCheck
    DiskCheck -->|"Yes"| Response
    DiskCheck -->|"No"| APICall
    APICall --> Response
    Response --> LRUCheck
    Response --> DiskCheck
```

**Sources**: [knowledge_storm/lm.py:54](), [knowledge_storm/lm.py:40-43](), [knowledge_storm/lm.py:115-129]()

The caching system has two levels:

1. **LRU Cache** [knowledge_storm/lm.py:115-129](): In-memory cache using `@functools.lru_cache` with `maxsize=3000`. Provides instant response for repeated queries within the same session.

2. **Disk Cache** [knowledge_storm/lm.py:40-43](): Persistent cache managed by LiteLLM at `~/.storm_local_cache`. Survives across sessions and can be shared between runs.

Cache keys are generated by serializing the request (model, messages, and parameters) to JSON using `ujson` [knowledge_storm/lm.py:93]().

### Token Usage Tracking

The infrastructure provides comprehensive token tracking at multiple levels:

| Level | Component | Method | Thread Safety |
|-------|-----------|--------|---------------|
| Individual LM | `LitellmModel` | `log_usage(response)` | Yes (uses `threading.Lock`) |
| LM Config | `LMConfigs` | `collect_and_reset_lm_usage()` | N/A (aggregates from LMs) |
| Engine | `Engine` | Automatic via decorator | N/A (aggregates per stage) |

The thread-safe implementation [knowledge_storm/lm.py:206-216]() allows multiple modules to safely increment token counters concurrently, which is important since both STORM and Co-STORM use parallel processing.

**Sources**: [knowledge_storm/lm.py:206-232](), [knowledge_storm/interface.py:452-473](), [knowledge_storm/interface.py:492-510]()

### Parallel Query Execution

The `Retriever` class [knowledge_storm/interface.py:288-319]() uses `concurrent.futures.ThreadPoolExecutor` to process multiple queries in parallel:

```python
# From interface.py:311-317
with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_thread) as executor:
    results = list(executor.map(process_query, queries))
```

This enables efficient batch retrieval when multiple perspectives or questions need information simultaneously, which is common in both STORM's perspective-guided research and Co-STORM's collaborative discourse.

**Sources**: [knowledge_storm/interface.py:311-317]()

### Execution Time and Cost Summary

The `Engine.summary()` method [knowledge_storm/interface.py:544-557]() provides a comprehensive report of:

- **Execution time** for each pipeline stage
- **Token usage** broken down by model and stage
- **Query count** for retrieval operations

This enables developers to identify bottlenecks and optimize resource usage.

**Sources**: [knowledge_storm/interface.py:544-557]()

## Integration with STORM and Co-STORM

Both STORM and Co-STORM systems inherit from the `Engine` base class and use the same infrastructure components, but configure them differently based on their operational paradigms:

### STORM Configuration

```mermaid
graph TB
    STORMRunner["STORMWikiRunner"]
    STORMLMConfigs["STORMWikiLMConfigs<br/>5 specialized LMs"]
    RetrieverRM["Retriever + YouRM/BingSearch"]
    
    Conv["conv_simulator_lm<br/>(conversation simulation)"]
    QA["question_asker_lm<br/>(question generation)"]
    Outline["outline_gen_lm<br/>(outline creation)"]
    Article["article_gen_lm<br/>(section writing)"]
    Polish["article_polish_lm<br/>(final refinement)"]
    
    STORMRunner --> STORMLMConfigs
    STORMRunner --> RetrieverRM
    STORMLMConfigs --> Conv
    STORMLMConfigs --> QA
    STORMLMConfigs --> Outline
    STORMLMConfigs --> Article
    STORMLMConfigs --> Polish
```

**Sources**: [README.md:114-134]()

### Co-STORM Configuration

```mermaid
graph TB
    CoSTORMRunner["CoStormRunner"]
    CoSTORMLMConfigs["CollaborativeStormLMConfigs<br/>6 specialized LMs"]
    RetrieverRM["Retriever + BingSearch"]
    EncoderComp["Encoder<br/>(embeddings)"]
    
    QAns["question_answering_lm<br/>(expert responses)"]
    Disc["discourse_manage_lm<br/>(turn policy)"]
    Utt["utterance_polishing_lm<br/>(response refinement)"]
    WS["warmstart_outline_gen_lm<br/>(initial KB)"]
    QAsk["question_asking_lm<br/>(question generation)"]
    KB["knowledge_base_lm<br/>(KB operations)"]
    
    CoSTORMRunner --> CoSTORMLMConfigs
    CoSTORMRunner --> RetrieverRM
    CoSTORMRunner --> EncoderComp
    CoSTORMLMConfigs --> QAns
    CoSTORMLMConfigs --> Disc
    CoSTORMLMConfigs --> Utt
    CoSTORMLMConfigs --> WS
    CoSTORMLMConfigs --> QAsk
    CoSTORMLMConfigs --> KB
```

**Sources**: [README.md:165-196]()

The key differences:
- **STORM** uses 5 LMs for its linear pipeline stages, no encoder required
- **Co-STORM** uses 6 LMs for collaborative discourse management, plus an encoder for knowledge base organization
- Both systems can use any LLM provider supported by LiteLLM without code changes

**Sources**: [README.md:104-216]()

---

