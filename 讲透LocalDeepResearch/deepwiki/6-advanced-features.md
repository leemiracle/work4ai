> 来源: [https://deepwiki.com/LearningCircuit/local-deep-research/6-advanced-features](https://deepwiki.com/LearningCircuit/local-deep-research/6-advanced-features)
> DeepWiki LearningCircuit/local-deep-research | Last indexed: 6 May 2026 (4a6a90

# Advanced Features

  Relevant source files 
 - [docs/BENCHMARKING.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/BENCHMARKING.md?plain=1)
 - [src/local_deep_research/advanced_search_system/questions/browsecomp_question.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/advanced_search_system/questions/browsecomp_question.py)
 - [src/local_deep_research/advanced_search_system/questions/flexible_browsecomp_question.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/advanced_search_system/questions/flexible_browsecomp_question.py)
 - [src/local_deep_research/advanced_search_system/strategies/langgraph_agent_strategy.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/advanced_search_system/strategies/langgraph_agent_strategy.py)
 - [src/local_deep_research/advanced_search_system/strategies/topic_organization_strategy.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/advanced_search_system/strategies/topic_organization_strategy.py)
 - [src/local_deep_research/advanced_search_system/tools/fetch/__init__.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/advanced_search_system/tools/fetch/__init__.py)
 - [src/local_deep_research/advanced_search_system/tools/fetch/prompts.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/advanced_search_system/tools/fetch/prompts.py)
 - [src/local_deep_research/benchmarks/models/__init__.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/benchmarks/models/__init__.py)
 - [src/local_deep_research/database/migrations/versions/0009_default_fetch_mode_summary.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/database/migrations/versions/0009_default_fetch_mode_summary.py)
 - [src/local_deep_research/database/models/library.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/database/models/library.py)
 - [src/local_deep_research/database/session_context.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/database/session_context.py)
 - [src/local_deep_research/defaults/default_settings.json](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/defaults/default_settings.json)
 - [src/local_deep_research/defaults/research_library/library_settings.json](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/defaults/research_library/library_settings.json)
 - [src/local_deep_research/news/api.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/news/api.py)
 - [src/local_deep_research/news/core/storage_manager.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/news/core/storage_manager.py)
 - [src/local_deep_research/news/flask_api.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/news/flask_api.py)
 - [src/local_deep_research/news/web.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/news/web.py)
 - [src/local_deep_research/research_library/routes/library_routes.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/research_library/routes/library_routes.py)
 - [src/local_deep_research/research_library/routes/rag_routes.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/research_library/routes/rag_routes.py)
 - [src/local_deep_research/research_library/services/download_service.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/research_library/services/download_service.py)
 - [src/local_deep_research/research_library/services/library_rag_service.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/research_library/services/library_rag_service.py)
 - [src/local_deep_research/research_library/services/library_service.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/research_library/services/library_service.py)
 - [src/local_deep_research/research_library/services/pdf_storage_manager.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/research_library/services/pdf_storage_manager.py)
 - [src/local_deep_research/research_library/utils/__init__.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/research_library/utils/__init__.py)
 - [src/local_deep_research/search_system_factory.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/search_system_factory.py)
 - [src/local_deep_research/web/static/js/components/library_search_ui.js](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/static/js/components/library_search_ui.js)
 - [src/local_deep_research/web/static/js/components/save_to_collection.js](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/static/js/components/save_to_collection.js)
 - [src/local_deep_research/web/templates/components/storage_mode_modal.html](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/templates/components/storage_mode_modal.html)
 - [src/local_deep_research/web/templates/pages/collection_create.html](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/templates/pages/collection_create.html)
 - [src/local_deep_research/web/templates/pages/collection_upload.html](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/templates/pages/collection_upload.html)
 - [src/local_deep_research/web/templates/pages/download_manager.html](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/templates/pages/download_manager.html)
 - [src/local_deep_research/web/templates/pages/library.html](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/templates/pages/library.html)
 - [src/local_deep_research/web_search_engines/engines/search_engine_collection.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web_search_engines/engines/search_engine_collection.py)
 - [src/local_deep_research/web_search_engines/engines/search_engine_library.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web_search_engines/engines/search_engine_library.py)
 - [tests/advanced_search_system/tools/test_fetch_modes.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/advanced_search_system/tools/test_fetch_modes.py)
 - [tests/database/test_migration_0009_default_fetch_mode.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/database/test_migration_0009_default_fetch_mode.py)
 - [tests/news/test_api_functions_extended.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/news/test_api_functions_extended.py)
 - [tests/news/test_api_module_extended.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/news/test_api_module_extended.py)
 - [tests/news/test_news_api.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/news/test_news_api.py)
 - [tests/news/test_news_api_coverage.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/news/test_news_api_coverage.py)
 - [tests/news/test_news_api_extended.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/news/test_news_api_extended.py)
 - [tests/news/test_storage_manager.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/news/test_storage_manager.py)
 - [tests/news/test_storage_manager_extended.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/news/test_storage_manager_extended.py)
 - [tests/settings/golden_master_settings.json](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/settings/golden_master_settings.json)
 - [tests/settings/test_settings_defaults_integrity.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/settings/test_settings_defaults_integrity.py)
 - [tests/strategies/test_langgraph_agent_strategy.py](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/tests/strategies/test_langgraph_agent_strategy.py)
 
  This page documents advanced capabilities of Local Deep Research beyond basic research execution. These features include RAG-based document indexing for semantic search, multi-strategy research modes, automated news subscriptions, comprehensive document management, and systematic benchmarking. For basic research operations, see [Research Service and Execution Lifecycle](https://deepwiki.com/LearningCircuit/local-deep-research/3.3-research-service-and-execution-lifecycle). For configuration of these features, see [Configuration System](https://deepwiki.com/LearningCircuit/local-deep-research/4-configuration-system).

 
---

 
## RAG and Document Indexing

 Local Deep Research includes a comprehensive RAG (Retrieval-Augmented Generation) system for indexing and semantically searching documents in the research library. The system uses FAISS vector indices with configurable embedding models and chunking strategies.

 
### Architecture Overview

 Title: RAG Indexing and Search Pipeline

 
```

```

 **Per-Collection Configuration System**

 The RAG system maintains separate indices per collection, each with its own embedding model and chunking configuration. The `LibraryRAGService` handles the lifecycle of these indices, including creation, loading, and searching [src/local_deep_research/research_library/services/library_rag_service.py43-164](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/research_library/services/library_rag_service.py#L43-L164) The `LibraryRAGSearchEngine` allows the research system to treat these collections as searchable engines by merging results across indexed collections [src/local_deep_research/web_search_engines/engines/search_engine_library.py23-185](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web_search_engines/engines/search_engine_library.py#L23-L185)

 Sources: [src/local_deep_research/research_library/services/library_rag_service.py43-164](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/research_library/services/library_rag_service.py#L43-L164) [src/local_deep_research/database/models/library.py79-168](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/database/models/library.py#L79-L168) [src/local_deep_research/research_library/routes/rag_routes.py94-127](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/research_library/routes/rag_routes.py#L94-L127) [src/local_deep_research/web_search_engines/engines/search_engine_library.py23-55](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web_search_engines/engines/search_engine_library.py#L23-L55)

 
### Key Components

 
| Component | Class/Function | Purpose |
|---|---|---|
| RAG Service | LibraryRAGService | Orchestrates indexing pipeline and provides semantic search src/local_deep_research/research_library/services/library_rag_service.py43 |
| Text Splitting | get_text_splitter() | Chunks documents (recursive, token, sentence, semantic) src/local_deep_research/embeddings/splitters.py31 |
| Embeddings | LocalEmbeddingManager | Generates vector embeddings using local or API providers src/local_deep_research/web_search_engines/engines/local_embedding_manager.py33-35 |
| Index Storage | RAGIndex model | Tracks index metadata, file paths, and configuration hashes src/local_deep_research/database/models/library.py126 |
| Chunk Storage | DocumentChunk model | Stores individual text chunks with metadata for retrieval src/local_deep_research/database/models/library.py150 |

 For details, see [RAG and Document Indexing](https://deepwiki.com/LearningCircuit/local-deep-research/6.1-rag-and-document-indexing).

 
---

 
## Multi-Strategy Research

 Local Deep Research supports 30+ research strategies, ranging from simple single-pass summaries to complex iterative exploration.

 
### Strategy Architecture

 Title: Research Strategy Selection and Components

 
```

```

 **Key Strategies:**

 
 - **Focused Iteration**: A high-performance strategy (96.51% SimpleQA accuracy) using iterative question generation. It allows configuring `adaptive_questions` and specific `question_generator` types like `flexible` [src/local_deep_research/search_system_factory.py83-177](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/search_system_factory.py#L83-L177)
 - **Source-Based**: The default comprehensive strategy using iterative question generation followed by a `CrossEngineFilter` to reorder results by relevance [src/local_deep_research/search_system_factory.py62-80](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/search_system_factory.py#L62-L80)
 - **IterDRAG**: Iterative Dense Retrieval Augmented Generation strategy [src/local_deep_research/search_system_factory.py13-16](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/search_system_factory.py#L13-L16)
 
 For details, see [Multi-Strategy Research](https://deepwiki.com/LearningCircuit/local-deep-research/6.2-multi-strategy-research).

 Sources: [src/local_deep_research/search_system_factory.py32-200](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/search_system_factory.py#L32-L200) [src/local_deep_research/advanced_search_system/strategies/focused_iteration_strategy.py1-60](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/advanced_search_system/strategies/focused_iteration_strategy.py#L1-L60) [src/local_deep_research/advanced_search_system/strategies/source_based_strategy.py22-57](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/advanced_search_system/strategies/source_based_strategy.py#L22-L57)

 
---

 
## News and Subscription Management

 The news system provides automated monitoring and document processing.

 **Implementation Details:**

 
 - **Auto-Indexing**: A global `ThreadPoolExecutor` (`_auto_index_executor`) manages background RAG tasks for news and library updates to prevent thread proliferation [src/local_deep_research/research_library/routes/rag_routes.py67-89](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/research_library/routes/rag_routes.py#L67-L89)
 - **Personalized Feed**: The `get_news_feed` API allows users to request news based on specific `focus` areas or `subscription_id` [src/local_deep_research/news/flask_api.py122-182](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/news/flask_api.py#L122-L182)
 - **Scheduler Control**: Global scheduler operations are gated by `scheduler_control_required` decorators to prevent unauthorized server-wide changes [src/local_deep_research/news/flask_api.py23-59](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/news/flask_api.py#L23-L59)
 
 For details, see [News and Subscription Management](https://deepwiki.com/LearningCircuit/local-deep-research/6.3-news-and-subscription-management).

 Sources: [src/local_deep_research/research_library/routes/rag_routes.py67-91](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/research_library/routes/rag_routes.py#L67-L91) [src/local_deep_research/news/flask_api.py23-191](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/news/flask_api.py#L23-L191)

 
---

 
## Document Download and Management

 The `DownloadService` handles the acquisition of PDFs from various academic and web sources using a modular downloader architecture [src/local_deep_research/research_library/services/download_service.py68-140](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/research_library/services/download_service.py#L68-L140)

 
### Downloader Pipeline

 The system uses a chain of specialized downloaders to resolve URLs into documents.

 
| Downloader | Purpose |
|---|---|
| DirectPDFDownloader | Efficiently handles direct .pdf links src/local_deep_research/research_library/services/download_service.py124 |
| ArxivDownloader | Resolves arXiv IDs and handles specific PDF paths src/local_deep_research/research_library/services/download_service.py134 |
| PubMedDownloader | Interfaces with NCBI/PubMed with built-in rate limiting src/local_deep_research/research_library/services/download_service.py135 |
| SemanticScholarDownloader | Uses API keys for high-quality academic PDF discovery src/local_deep_research/research_library/services/download_service.py125 |
| OpenAlexDownloader | Performs API lookups for open access document discovery src/local_deep_research/research_library/services/download_service.py131-133 |

 
### PDF Storage Modes

 The `PDFStorageManager` abstracts physical storage, supporting:

 
 - **Database Mode**: PDFs are stored as encrypted blobs in `DocumentBlob` [src/local_deep_research/database/models/library.py171-185](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/database/models/library.py#L171-L185)
 - **Filesystem Mode**: PDFs are stored unencrypted in the library directory [src/local_deep_research/research_library/services/library_service.py56-70](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/research_library/services/library_service.py#L56-L70)
 - **Text Only**: Only extracted text is stored to save space [src/local_deep_research/web/templates/pages/library.html81-84](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/templates/pages/library.html#L81-L84)
 
 For details, see [Document Download and Management](https://deepwiki.com/LearningCircuit/local-deep-research/6.4-document-download-and-management).

 Sources: [src/local_deep_research/research_library/services/download_service.py115-140](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/research_library/services/download_service.py#L115-L140) [src/local_deep_research/research_library/services/library_service.py139-200](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/research_library/services/library_service.py#L139-L200) [src/local_deep_research/web/templates/pages/library.html71-85](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/web/templates/pages/library.html#L71-L85)

 
---

 
## Benchmarking System

 Local Deep Research includes a benchmarking infrastructure to measure performance across different strategies and LLM configurations.

 
### Benchmarking Flow

 
 - **Dataset Loading**: Loads questions from `SimpleQA` or `BrowseComp` datasets.
 - **Execution**: Runs research queries using specialized research functions or specific strategies.
 - **Grading**: Uses a separate "Evaluator LLM" to grade responses against ground truth.
 - **Optimization**: Supports Optuna-based parameter optimization to find ideal iterations and question counts.
 
 For details, see [Benchmarking System](https://deepwiki.com/LearningCircuit/local-deep-research/6.5-benchmarking-system).

 Sources: [docs/BENCHMARKING.md](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/docs/BENCHMARKING.md?plain=1) [src/local_deep_research/advanced_search_system/strategies/focused_iteration_strategy.py1-20](https://github.com/LearningCircuit/local-deep-research/blob/4a6a9088/src/local_deep_research/advanced_search_system/strategies/focused_iteration_strategy.py#L1-L20)

 
---

 
### Child Pages

 
 - [RAG and Document Indexing](https://deepwiki.com/LearningCircuit/local-deep-research/6.1-rag-and-document-indexing)
 - [Multi-Strategy Research](https://deepwiki.com/LearningCircuit/local-deep-research/6.2-multi-strategy-research)
 - [News and Subscription Management](https://deepwiki.com/LearningCircuit/local-deep-research/6.3-news-and-subscription-management)
 - [Document Download and Management](https://deepwiki.com/LearningCircuit/local-deep-research/6.4-document-download-and-management)
 - [Benchmarking System](https://deepwiki.com/LearningCircuit/local-deep-research/6.5-benchmarking-system)
