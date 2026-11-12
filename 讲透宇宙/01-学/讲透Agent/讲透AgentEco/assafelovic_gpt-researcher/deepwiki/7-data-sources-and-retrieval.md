<!-- source: DeepWiki mcp.deepwiki.com · repo assafelovic/gpt-researcher · page 7 Data Sources and Retrieval · fetched 2026-10-27 -->

# Data Sources and Retrieval

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [gpt_researcher/actions/retriever.py](gpt_researcher/actions/retriever.py)
- [gpt_researcher/retrievers/__init__.py](gpt_researcher/retrievers/__init__.py)
- [gpt_researcher/retrievers/bing/__init__.py](gpt_researcher/retrievers/bing/__init__.py)
- [gpt_researcher/retrievers/bing/bing.py](gpt_researcher/retrievers/bing/bing.py)
- [gpt_researcher/retrievers/google/google.py](gpt_researcher/retrievers/google/google.py)
- [gpt_researcher/retrievers/openalex/__init__.py](gpt_researcher/retrievers/openalex/__init__.py)
- [gpt_researcher/retrievers/openalex/openalex.py](gpt_researcher/retrievers/openalex/openalex.py)
- [gpt_researcher/retrievers/searchapi/searchapi.py](gpt_researcher/retrievers/searchapi/searchapi.py)
- [gpt_researcher/retrievers/searx/searx.py](gpt_researcher/retrievers/searx/searx.py)
- [gpt_researcher/retrievers/serpapi/serpapi.py](gpt_researcher/retrievers/serpapi/serpapi.py)
- [gpt_researcher/retrievers/serper/serper.py](gpt_researcher/retrievers/serper/serper.py)
- [gpt_researcher/retrievers/tavily/tavily_search.py](gpt_researcher/retrievers/tavily/tavily_search.py)
- [gpt_researcher/retrievers/utils.py](gpt_researcher/retrievers/utils.py)
- [gpt_researcher/retrievers/xquik/__init__.py](gpt_researcher/retrievers/xquik/__init__.py)
- [gpt_researcher/retrievers/xquik/xquik.py](gpt_researcher/retrievers/xquik/xquik.py)

</details>



## Purpose and Scope

This document provides an overview of GPT Researcher's data source and retrieval architecture. It covers how the system acquires information from multiple sources including web search engines, local documents, cloud storage, and specialized data providers. The document explains the orchestration layer that routes research queries to appropriate data sources and consolidates results into usable research context.

For detailed implementation specifics of each subsystem, see:
- Web search retriever implementations: [Retriever System](#7.1)
- Parallel web scraping mechanics: [Web Scraping System](#7.2)
- File format parsers and document loaders: [Document Loading System](#7.3)
- Azure Blob Storage integration: [Cloud Storage Integration](#7.4)
- Model Context Protocol for specialized data: [Model Context Protocol (MCP)](#7.5)
- Semantic search and embeddings: [Vector Store Integration](#7.6)
- Source mode configuration reference: [Report Source Modes](#7.7)
- Filtering results by specific domains: [Domain Filtering](#7.8)

## Data Source Architecture

GPT Researcher implements a flexible multi-source data acquisition architecture orchestrated by the `ResearchConductor` class. Data flows from various sources through a unified pipeline that handles scraping, compression, and context assembly.

### Source Type Enumeration

The system defines several distinct source modes via the `ReportSource` enum, allowing the agent to target specific data environments:

| Source Mode | Description | Primary Use Case |
|------------|-------------|------------------|
| `ReportSource.Web` | Web search + scraping | Internet research with search engines |
| `ReportSource.Local` | Local file system documents | Research on proprietary documents (PDF, DOCX, etc.) |
| `ReportSource.Azure` | Azure Blob Storage documents | Cloud-hosted document research |
| `ReportSource.Hybrid` | Local + Web combined | Complement local docs with web data |
| `ReportSource.LangChainDocuments` | Pre-loaded LangChain Document objects | Integration with existing LangChain pipelines |
| `ReportSource.LangChainVectorStore` | Vector store similarity search | Research on pre-embedded document collections |

**Sources:** [gpt_researcher/utils/enum.py:30-51](), [gpt_researcher/agent.py:141]()

### Research Conductor Overview

The `ResearchConductor` class serves as the orchestration layer for all data acquisition, managing the transition from planning to context gathering.

**ResearchConductor Data Flow Diagram**
```mermaid
graph TB
    subgraph "ResearchConductor Orchestration"
        [ResearchConductor] --> [conduct_research]
        [ResearchConductor] --> [plan_research]
    end
    
    subgraph "Source Routing Methods"
        [conduct_research] --> [_get_context_by_urls]
        [conduct_research] --> [_get_context_by_web_search]
        [conduct_research] --> [_get_context_by_vectorstore]
    end
    
    subgraph "Data Sources"
        [_get_context_by_urls] --> [Source_URLs]
        [_get_context_by_web_search] --> [Web_Search_Retrievers]
        [_get_context_by_web_search] --> [Local_Documents]
        [_get_context_by_web_search] --> [Azure_Blob_Storage]
        [_get_context_by_web_search] --> [MCP_Tools]
        [_get_context_by_vectorstore] --> [VectorStoreWrapper]
    end
    
    subgraph "Processing Pipeline"
        [Source_URLs] --> [BrowserManager.browse_urls]
        [Web_Search_Retrievers] --> [BrowserManager.browse_urls]
        [BrowserManager.browse_urls] --> [ContextManager.get_similar_content_by_query]
        [ContextManager.get_similar_content_by_query] --> [SourceCurator.curate_sources]
    end
    
    [SourceCurator.curate_sources] --> FinalContext["Final Research Context"]
```

**Sources:** [gpt_researcher/skills/researcher.py:21-211]()

## Source Selection and Routing

The research workflow begins with source selection based on the `report_source` parameter passed to `GPTResearcher.__init__()`.

**Source Routing Logic**
```mermaid
graph LR
    [GPTResearcher.__init__] --> CheckSource{"report_source value?"}
    
    CheckSource -->|"source_urls provided"| [_get_context_by_urls]
    CheckSource -->|"Web"| [_get_context_by_web_search]
    CheckSource -->|"Local"| [DocumentLoader]
    CheckSource -->|"Azure"| [AzureDocumentLoader]
    CheckSource -->|"Hybrid"| HybridPath["Local + Web Combined"]
    CheckSource -->|"LangChainDocuments"| [LangChainDocumentLoader]
    CheckSource -->|"LangChainVectorStore"| [_get_context_by_vectorstore]
    
    [_get_context_by_urls] --> Context["Research Context"]
    [_get_context_by_web_search] --> Context
    [DocumentLoader] --> Context
    [AzureDocumentLoader] --> Context
    HybridPath --> Context
    [LangChainDocumentLoader] --> Context
    [_get_context_by_vectorstore] --> Context
```

**Sources:** [gpt_researcher/agent.py:51-82](), [gpt_researcher/skills/researcher.py:134-211]()

## Web Search and Retriever System

GPT Researcher supports 17+ search providers through a unified retriever interface. The `get_retrievers()` factory function instantiates retriever classes based on configuration.

### Retriever Factory Pattern

The system determines which search providers to use by checking headers, the `Config` object, or falling back to `TavilySearch` as the default.

**Retriever Resolution Diagram**
```mermaid
graph TB
    subgraph "Configuration Inputs"
        [Headers_retrievers]
        [Config_retrievers]
        [Default_Fallback]
    end
    
    [get_retrievers] --> [get_retriever]
    
    [Headers_retrievers] --> [get_retrievers]
    [Config_retrievers] --> [get_retrievers]
    [Default_Fallback] --> [get_retrievers]
    
    subgraph "Retriever Implementations"
        [get_retriever] --> [TavilySearch]
        [get_retriever] --> [GoogleSearch]
        [get_retriever] --> [BingSearch]
        [get_retriever] --> [Duckduckgo]
        [get_retriever] --> [ArxivSearch]
        [get_retriever] --> [XquikSearch]
        [get_retriever] --> [OpenAlexSearch]
        [get_retriever] --> [MCPRetriever]
    end
```

**Sources:** [gpt_researcher/actions/retriever.py:8-156](), [gpt_researcher/retrievers/__init__.py:1-37]()

### Supported Retrievers

The system currently supports the following retrievers, mapping names to classes in `gpt_researcher/actions/retriever.py`:

*   **General Search:** `tavily`, `google`, `duckduckgo`, `bing`, `searx`, `bocha`, `xquik` (X/Twitter)
*   **Academic/Medical:** `arxiv`, `semantic_scholar`, `pubmed_central`, `openalex`
*   **AI/Neural Search:** `exa`
*   **API Aggregators:** `serper`, `serpapi`, `searchapi`
*   **Protocol Based:** `mcp` (Model Context Protocol)

**Sources:** [gpt_researcher/actions/retriever.py:33-103](), [gpt_researcher/retrievers/utils.py:62-80]()

### Domain Filtering

Users can restrict web search results to specific domains (e.g., `wikipedia.org`). This is primarily implemented by modifying the search query with `site:` operators or using provider-specific parameters.

*   **Google:** Constructs queries like `(site:example.com) query` [gpt_researcher/retrievers/google/google.py:61-63]().
*   **Tavily:** Passes `include_domains` directly to the API [gpt_researcher/retrievers/tavily/tavily_search.py:113]().
*   **Serper:** Appends `-site:excluded.com` or `site:included.com` to the query string [gpt_researcher/retrievers/serper/serper.py:78-86]().

**Sources:** [gpt_researcher/retrievers/google/google.py:59-67](), [gpt_researcher/retrievers/tavily/tavily_search.py:100-115](), [gpt_researcher/retrievers/serper/serper.py:74-91]()

## Web Scraping Pipeline

Once search results are obtained, the `BrowserManager` orchestrates parallel web scraping to extract full page content. Performance is controlled by environment variables like `MAX_SCRAPER_WORKERS` and `SCRAPER_RATE_LIMIT_DELAY`.

**Sources:** [.env.example:12-30](), [gpt_researcher/skills/browser.py:14-116]()

## Document Loading System

GPT Researcher can ingest local files and remote documents using the `DocumentLoader` class.

*   **Local Docs:** Set the `DOC_PATH` environment variable and use `report_source="local"` [.env.example:4]().
*   **Hybrid Mode:** Combines these local documents with real-time web search results.
*   **Cloud Integration:** Integration with Azure Blob Storage allows fetching blobs from containers using the `AZURE_CONNECTION_STRING`.

**Sources:** [gpt_researcher/skills/researcher.py:154-189]()

## Model Context Protocol (MCP) Integration

MCP allows GPT Researcher to interact with external tools and data servers during the research process.

*   **Strategies:** Supports `fast` (single execution) and `deep` (per sub-query) strategies.
*   **Retriever:** The `MCPRetriever` handles communication with MCP servers to fetch context [gpt_researcher/retrievers/mcp.py]().

**Sources:** [gpt_researcher/retrievers/mcp.py](), [gpt_researcher/skills/researcher.py:279-327]()

## Vector Store Integration

The `VectorStoreWrapper` enables semantic similarity search over pre-embedded document collections. This is used when `report_source` is set to `langchain_vectorstore`.

**Sources:** [gpt_researcher/agent.py:63-64](), [gpt_researcher/skills/researcher.py:233-264]()

---

