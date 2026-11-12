<!-- source: DeepWiki mcp.deepwiki.com · repo LearningCircuit/local-deep-research · page 6 Advanced Features · fetched 2026-10-29 -->

# Advanced Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/BENCHMARKING.md](docs/BENCHMARKING.md)
- [src/local_deep_research/advanced_search_system/questions/browsecomp_question.py](src/local_deep_research/advanced_search_system/questions/browsecomp_question.py)
- [src/local_deep_research/advanced_search_system/questions/flexible_browsecomp_question.py](src/local_deep_research/advanced_search_system/questions/flexible_browsecomp_question.py)
- [src/local_deep_research/advanced_search_system/strategies/langgraph_agent_strategy.py](src/local_deep_research/advanced_search_system/strategies/langgraph_agent_strategy.py)
- [src/local_deep_research/advanced_search_system/strategies/topic_organization_strategy.py](src/local_deep_research/advanced_search_system/strategies/topic_organization_strategy.py)
- [src/local_deep_research/advanced_search_system/tools/fetch/__init__.py](src/local_deep_research/advanced_search_system/tools/fetch/__init__.py)
- [src/local_deep_research/advanced_search_system/tools/fetch/prompts.py](src/local_deep_research/advanced_search_system/tools/fetch/prompts.py)
- [src/local_deep_research/benchmarks/models/__init__.py](src/local_deep_research/benchmarks/models/__init__.py)
- [src/local_deep_research/database/migrations/versions/0009_default_fetch_mode_summary.py](src/local_deep_research/database/migrations/versions/0009_default_fetch_mode_summary.py)
- [src/local_deep_research/database/models/library.py](src/local_deep_research/database/models/library.py)
- [src/local_deep_research/database/session_context.py](src/local_deep_research/database/session_context.py)
- [src/local_deep_research/defaults/default_settings.json](src/local_deep_research/defaults/default_settings.json)
- [src/local_deep_research/defaults/research_library/library_settings.json](src/local_deep_research/defaults/research_library/library_settings.json)
- [src/local_deep_research/news/api.py](src/local_deep_research/news/api.py)
- [src/local_deep_research/news/core/storage_manager.py](src/local_deep_research/news/core/storage_manager.py)
- [src/local_deep_research/news/flask_api.py](src/local_deep_research/news/flask_api.py)
- [src/local_deep_research/news/web.py](src/local_deep_research/news/web.py)
- [src/local_deep_research/research_library/routes/library_routes.py](src/local_deep_research/research_library/routes/library_routes.py)
- [src/local_deep_research/research_library/routes/rag_routes.py](src/local_deep_research/research_library/routes/rag_routes.py)
- [src/local_deep_research/research_library/services/download_service.py](src/local_deep_research/research_library/services/download_service.py)
- [src/local_deep_research/research_library/services/library_rag_service.py](src/local_deep_research/research_library/services/library_rag_service.py)
- [src/local_deep_research/research_library/services/library_service.py](src/local_deep_research/research_library/services/library_service.py)
- [src/local_deep_research/research_library/services/pdf_storage_manager.py](src/local_deep_research/research_library/services/pdf_storage_manager.py)
- [src/local_deep_research/research_library/utils/__init__.py](src/local_deep_research/research_library/utils/__init__.py)
- [src/local_deep_research/search_system_factory.py](src/local_deep_research/search_system_factory.py)
- [src/local_deep_research/web/static/js/components/library_search_ui.js](src/local_deep_research/web/static/js/components/library_search_ui.js)
- [src/local_deep_research/web/static/js/components/save_to_collection.js](src/local_deep_research/web/static/js/components/save_to_collection.js)
- [src/local_deep_research/web/templates/components/storage_mode_modal.html](src/local_deep_research/web/templates/components/storage_mode_modal.html)
- [src/local_deep_research/web/templates/pages/collection_create.html](src/local_deep_research/web/templates/pages/collection_create.html)
- [src/local_deep_research/web/templates/pages/collection_upload.html](src/local_deep_research/web/templates/pages/collection_upload.html)
- [src/local_deep_research/web/templates/pages/download_manager.html](src/local_deep_research/web/templates/pages/download_manager.html)
- [src/local_deep_research/web/templates/pages/library.html](src/local_deep_research/web/templates/pages/library.html)
- [src/local_deep_research/web_search_engines/engines/search_engine_collection.py](src/local_deep_research/web_search_engines/engines/search_engine_collection.py)
- [src/local_deep_research/web_search_engines/engines/search_engine_library.py](src/local_deep_research/web_search_engines/engines/search_engine_library.py)
- [tests/advanced_search_system/tools/test_fetch_modes.py](tests/advanced_search_system/tools/test_fetch_modes.py)
- [tests/database/test_migration_0009_default_fetch_mode.py](tests/database/test_migration_0009_default_fetch_mode.py)
- [tests/news/test_api_functions_extended.py](tests/news/test_api_functions_extended.py)
- [tests/news/test_api_module_extended.py](tests/news/test_api_module_extended.py)
- [tests/news/test_news_api.py](tests/news/test_news_api.py)
- [tests/news/test_news_api_coverage.py](tests/news/test_news_api_coverage.py)
- [tests/news/test_news_api_extended.py](tests/news/test_news_api_extended.py)
- [tests/news/test_storage_manager.py](tests/news/test_storage_manager.py)
- [tests/news/test_storage_manager_extended.py](tests/news/test_storage_manager_extended.py)
- [tests/settings/golden_master_settings.json](tests/settings/golden_master_settings.json)
- [tests/settings/test_settings_defaults_integrity.py](tests/settings/test_settings_defaults_integrity.py)
- [tests/strategies/test_langgraph_agent_strategy.py](tests/strategies/test_langgraph_agent_strategy.py)

</details>



This page documents advanced capabilities of Local Deep Research beyond basic research execution. These features include RAG-based document indexing for semantic search, multi-strategy research modes, automated news subscriptions, comprehensive document management, and systematic benchmarking. For basic research operations, see [Research Service and Execution Lifecycle](#3.3). For configuration of these features, see [Configuration System](#4).

---

## RAG and Document Indexing

Local Deep Research includes a comprehensive RAG (Retrieval-Augmented Generation) system for indexing and semantically searching documents in the research library. The system uses FAISS vector indices with configurable embedding models and chunking strategies.

### Architecture Overview

Title: RAG Indexing and Search Pipeline
```mermaid
graph TB
    subgraph "Document_Sources"
        [Document_Entity] --> [SourceType_Enum]
        [ResearchResource_Entity] --> [Document_Entity]
    end
    
    subgraph "LibraryRAGService_Logic"
        [LibraryRAGService] --> [get_text_splitter]
        [get_text_splitter] --> [DocumentChunk_Entity]
        [DocumentChunk_Entity] --> [LocalEmbeddingManager]
        [LocalEmbeddingManager] --> [FAISS_Index]
    end
    
    subgraph "Database_Models"
        [Document_Entity]
        [DocumentChunk_Entity]
        [Collection_Entity]
        [RAGIndex_Entity]
        [DocumentBlob_Entity]
    end
    
    subgraph "Verification"
        [FAISS_Index] --> [FAISSIndexVerifier]
        [FAISSIndexVerifier] --> [FileIntegrityManager]
    end
    
    [Collection_Entity] -.->|"configures"| [LibraryRAGService]
    [LocalEmbeddingManager] -.->|"uses"| [EmbeddingProvider_Enum]
```

**Per-Collection Configuration System**

The RAG system maintains separate indices per collection, each with its own embedding model and chunking configuration. The `LibraryRAGService` handles the lifecycle of these indices, including creation, loading, and searching [src/local_deep_research/research_library/services/library_rag_service.py:43-164](). The `LibraryRAGSearchEngine` allows the research system to treat these collections as searchable engines by merging results across indexed collections [src/local_deep_research/web_search_engines/engines/search_engine_library.py:23-185]().

Sources: [src/local_deep_research/research_library/services/library_rag_service.py:43-164](), [src/local_deep_research/database/models/library.py:79-168](), [src/local_deep_research/research_library/routes/rag_routes.py:94-127](), [src/local_deep_research/web_search_engines/engines/search_engine_library.py:23-55]()

### Key Components

| Component | Class/Function | Purpose |
|-----------|---------------|---------|
| RAG Service | `LibraryRAGService` | Orchestrates indexing pipeline and provides semantic search [src/local_deep_research/research_library/services/library_rag_service.py:43-43]() |
| Text Splitting | `get_text_splitter()` | Chunks documents (recursive, token, sentence, semantic) [src/local_deep_research/embeddings/splitters.py:31-31]() |
| Embeddings | `LocalEmbeddingManager` | Generates vector embeddings using local or API providers [src/local_deep_research/web_search_engines/engines/local_embedding_manager.py:33-35]() |
| Index Storage | `RAGIndex` model | Tracks index metadata, file paths, and configuration hashes [src/local_deep_research/database/models/library.py:126-126]() |
| Chunk Storage | `DocumentChunk` model | Stores individual text chunks with metadata for retrieval [src/local_deep_research/database/models/library.py:150-150]() |

For details, see [RAG and Document Indexing](#6.1).

---

## Multi-Strategy Research

Local Deep Research supports 30+ research strategies, ranging from simple single-pass summaries to complex iterative exploration.

### Strategy Architecture

Title: Research Strategy Selection and Components
```mermaid
graph TB
    subgraph "Search_System_Space"
        [AdvancedSearchSystem] --> [SourceBasedSearchStrategy]
        [AdvancedSearchSystem] --> [FocusedIterationStrategy]
        [AdvancedSearchSystem] --> [ParallelSearchStrategy]
        [AdvancedSearchSystem] --> [IterDRAGStrategy]
    end
    
    subgraph "Strategy_Logic"
        [SourceBasedSearchStrategy] --> [StandardQuestionGenerator]
        [FocusedIterationStrategy] --> [BrowseCompQuestionGenerator]
        [FocusedIterationStrategy] --> [ProgressiveExplorer]
        [SourceBasedSearchStrategy] --> [CrossEngineFilter]
    end

    subgraph "Output_Components"
        [BaseSearchStrategy] --> [CitationHandler]
        [AdvancedSearchSystem] --> [FindingsRepository]
    end
```

**Key Strategies:**
- **Focused Iteration**: A high-performance strategy (96.51% SimpleQA accuracy) using iterative question generation. It allows configuring `adaptive_questions` and specific `question_generator` types like `flexible` [src/local_deep_research/search_system_factory.py:83-177]().
- **Source-Based**: The default comprehensive strategy using iterative question generation followed by a `CrossEngineFilter` to reorder results by relevance [src/local_deep_research/search_system_factory.py:62-80]().
- **IterDRAG**: Iterative Dense Retrieval Augmented Generation strategy [src/local_deep_research/search_system_factory.py:13-16]().

For details, see [Multi-Strategy Research](#6.2).

Sources: [src/local_deep_research/search_system_factory.py:32-200](), [src/local_deep_research/advanced_search_system/strategies/focused_iteration_strategy.py:1-60](), [src/local_deep_research/advanced_search_system/strategies/source_based_strategy.py:22-57]()

---

## News and Subscription Management

The news system provides automated monitoring and document processing.

**Implementation Details:**
- **Auto-Indexing**: A global `ThreadPoolExecutor` (`_auto_index_executor`) manages background RAG tasks for news and library updates to prevent thread proliferation [src/local_deep_research/research_library/routes/rag_routes.py:67-89]().
- **Personalized Feed**: The `get_news_feed` API allows users to request news based on specific `focus` areas or `subscription_id` [src/local_deep_research/news/flask_api.py:122-182]().
- **Scheduler Control**: Global scheduler operations are gated by `scheduler_control_required` decorators to prevent unauthorized server-wide changes [src/local_deep_research/news/flask_api.py:23-59]().

For details, see [News and Subscription Management](#6.3).

Sources: [src/local_deep_research/research_library/routes/rag_routes.py:67-91](), [src/local_deep_research/news/flask_api.py:23-191]()

---

## Document Download and Management

The `DownloadService` handles the acquisition of PDFs from various academic and web sources using a modular downloader architecture [src/local_deep_research/research_library/services/download_service.py:68-140]().

### Downloader Pipeline

The system uses a chain of specialized downloaders to resolve URLs into documents.

| Downloader | Purpose |
|------------|---------|
| `DirectPDFDownloader` | Efficiently handles direct `.pdf` links [src/local_deep_research/research_library/services/download_service.py:124-124]() |
| `ArxivDownloader` | Resolves arXiv IDs and handles specific PDF paths [src/local_deep_research/research_library/services/download_service.py:134-134]() |
| `PubMedDownloader` | Interfaces with NCBI/PubMed with built-in rate limiting [src/local_deep_research/research_library/services/download_service.py:135-135]() |
| `SemanticScholarDownloader` | Uses API keys for high-quality academic PDF discovery [src/local_deep_research/research_library/services/download_service.py:125-125]() |
| `OpenAlexDownloader` | Performs API lookups for open access document discovery [src/local_deep_research/research_library/services/download_service.py:131-133]() |

### PDF Storage Modes
The `PDFStorageManager` abstracts physical storage, supporting:
- **Database Mode**: PDFs are stored as encrypted blobs in `DocumentBlob` [src/local_deep_research/database/models/library.py:171-185]().
- **Filesystem Mode**: PDFs are stored unencrypted in the library directory [src/local_deep_research/research_library/services/library_service.py:56-70]().
- **Text Only**: Only extracted text is stored to save space [src/local_deep_research/web/templates/pages/library.html:81-84]().

For details, see [Document Download and Management](#6.4).

Sources: [src/local_deep_research/research_library/services/download_service.py:115-140](), [src/local_deep_research/research_library/services/library_service.py:139-200](), [src/local_deep_research/web/templates/pages/library.html:71-85]()

---

## Benchmarking System

Local Deep Research includes a benchmarking infrastructure to measure performance across different strategies and LLM configurations.

### Benchmarking Flow
1. **Dataset Loading**: Loads questions from `SimpleQA` or `BrowseComp` datasets.
2. **Execution**: Runs research queries using specialized research functions or specific strategies.
3. **Grading**: Uses a separate "Evaluator LLM" to grade responses against ground truth.
4. **Optimization**: Supports Optuna-based parameter optimization to find ideal iterations and question counts.

For details, see [Benchmarking System](#6.5).

Sources: [docs/BENCHMARKING.md](), [src/local_deep_research/advanced_search_system/strategies/focused_iteration_strategy.py:1-20]()

---

### Child Pages
- [RAG and Document Indexing](#6.1)
- [Multi-Strategy Research](#6.2)
- [News and Subscription Management](#6.3)
- [Document Download and Management](#6.4)
- [Benchmarking System](#6.5)

---

