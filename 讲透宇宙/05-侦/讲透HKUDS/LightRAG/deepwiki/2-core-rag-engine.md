<!-- source: DeepWiki mcp.deepwiki.com · repo HKUDS/LightRAG · page 2 Core RAG Engine · fetched 2026-11-09 -->

# Core RAG Engine

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/design/LatexEscapeRepairContract.md](docs/design/LatexEscapeRepairContract.md)
- [lightrag/lightrag.py](lightrag/lightrag.py)
- [lightrag/operate.py](lightrag/operate.py)
- [lightrag/prompt.py](lightrag/prompt.py)
- [lightrag/utils.py](lightrag/utils.py)
- [tests/llm/test_vlm_json_escape_repair.py](tests/llm/test_vlm_json_escape_repair.py)

</details>



The Core RAG Engine forms the computational backbone of the LightRAG Python library. It manages the conversion of raw text documents into a structured Knowledge Graph (KG) representation and executes flexible multi-level retrieval queries that combine symbolic graph search with vector semantic search.

This engine bridges natural language data and structured code entities through layered components handling text chunking, LLM-driven extraction of entities and relationships, vector indexing, graph storage, and query execution. It balances fully automated KG construction with efficient retrieval modes suitable for diverse user scenarios.

---

### High-Level Architecture and Code Mapping

To situate the core engine within the codebase, the diagram below visualizes the main logical components and the primary modules and classes that implement them:

Title: Core RAG Engine Components to Code Entities
```mermaid
graph TD
    subgraph "Public API [lightrag/lightrag.py]"
        LightRAG["LightRAG Class"]
        AInsert["ainsert async API"]
        AQuery["aquery async API"]
        AQueryData["aquery_data async API"]
    end

    subgraph "Pipeline and Operations [lightrag/pipeline.py & operate.py]"
        PipelineMixin["_PipelineMixin mixin"]
        ExtractEntities["extract_entities function"]
        KGQuery["kg_query function"]
        RebuildKG["rebuild_knowledge_from_chunks function"]
    end

    subgraph "Storage Backends [lightrag/base.py]"
        GraphStorage["BaseGraphStorage interface"]
        VectorStorage["BaseVectorStorage interface"]
        KVStorage["BaseKVStorage interface"]
        DocStatus["DocStatusStorage interface"]
    end

    subgraph "Supporting Modules"
        Chunker["lightrag/chunker.py"]
        Prompt["lightrag/prompt.py"]
        Utils["lightrag/utils.py"]
        UtilsPipeline["lightrag/utils_pipeline.py"]
    end

    LightRAG -->|Inherits and orchestrates| PipelineMixin
    LightRAG -->|Calls| AInsert
    LightRAG -->|Calls| AQuery
    LightRAG -->|Calls| AQueryData

    AInsert -->|Calls| ExtractEntities
    ExtractEntities -->|Uses| Prompt
    ExtractEntities -->|Writes| GraphStorage
    ExtractEntities -->|Writes| KVStorage

    AQuery -->|Calls| KGQuery
    AQueryData -->|Calls| KGQuery
    
    KGQuery -->|Reads| GraphStorage
    KGQuery -->|Reads| VectorStorage
    KGQuery -->|Reads| KVStorage

    PipelineMixin -->|Uses| UtilsPipeline
    ExtractEntities -->|Utilizes| Chunker
    KGQuery -->|Uses| Utils
```
Sources: [lightrag/lightrag.py:162-231](), [lightrag/operate.py:114-196](), [lightrag/base.py:83-139]()

---

### Core Subsystems Overview

The Core RAG Engine is organized into five major subsystems. Each handles a distinct responsibility:

#### 1. LightRAG Class and Pipeline Orchestration
The `LightRAG` class serves as the primary orchestrator for the KG ingestion and query lifecycle [lightrag/lightrag.py:1-231](). It coordinates asynchronous insertion (`ainsert`) and query (`aquery`) APIs, document lifecycle management via `_PipelineMixin`, and safe concurrency controls [lightrag/lightrag.py:162-208]().

For details, see [LightRAG Class and Pipeline Orchestration](#2.1).
Sources: [lightrag/lightrag.py:162-231](), [lightrag/pipeline.py:1-100]()

#### 2. Entity and Relation Extraction
Transforming document text chunks into graph elements is accomplished via `extract_entities` [lightrag/operate.py:147](), driven by LLM prompts governed by templates defined in `lightrag/prompt.py` [lightrag/prompt.py:56-102](). It extracts structured entities and binary relationships with support for gleaning and deduplication.

For details, see [Entity and Relation Extraction](#2.2).
Sources: [lightrag/operate.py:114-196](), [lightrag/prompt.py:56-102]()

#### 3. Retrieval and Query Modes
Querying the KG supports local, global, hybrid, mix, and naive modes encapsulated by `QueryParam` [lightrag/base.py:133](). The core retrieval logic executes in `kg_query` [lightrag/operate.py:148](), managing token budgets, keyword extraction, vector search, and reranking.

For details, see [Retrieval and Query Modes](#2.3).
Sources: [lightrag/operate.py:114-196](), [lightrag/base.py:133-139]()

#### 4. Text Chunking Strategies
Input text is split into segments compatible with model token limits using strategies such as fixed-size token chunks, recursive semantic chunking, and vector semantic chunking via `chunking_by_token_size` [lightrag/lightrag.py:142]().

For details, see [Text Chunking Strategies](#2.4).
Sources: [lightrag/lightrag.py:142](), [lightrag/chunker.py:1-50]()

#### 5. Concurrency, Caching, and Utilities
Robust concurrent execution is managed via `priority_limit_async_func_call` [lightrag/utils.py:188](), storage locks, LLM response caches, vector DB operation wrappers (`safe_vdb_operation_with_exception`) [lightrag/utils.py:156](), and text sanitization utilities including LaTeX escape repair [lightrag/utils.py:27]().

For details, see [Concurrency, Caching, and Utilities](#2.5).
Sources: [lightrag/utils.py:156-209](), [lightrag/operate.py:15-63]()

---

### Data Flow: From Natural Language Input to Knowledge Graph

Title: Data Flow from Raw Text to KG Storage
```mermaid
graph LR
    RawDocument["Raw Document Text"] -->|PipelineMixin| TextChunkSchema["Text Chunk Schema"]

    TextChunkSchema -->|extract_entities| LLMExtraction["LLM Entity and Relation Extraction"]

    LLMExtraction -->|merge_nodes_and_edges| MergedGraph["Merged Entities and Relations"]

    subgraph "Storage Persistence Layer [lightrag/base.py]"
        MergedGraph -->|upsert_node| GraphStorage["BaseGraphStorage"]
        MergedGraph -->|upsert_edge| GraphStorage
        MergedGraph -->|insert| VectorStorage["BaseVectorStorage"]
        TextChunkSchema -->|insert/update| KVStorage["BaseKVStorage"]
    end

    style RawDocument stroke-dasharray: 5 5
    style LLMExtraction stroke-dasharray: 5 5
```
Sources: [lightrag/operate.py:146-152](), [lightrag/base.py:64-72]()

---

### Key Classes and Interfaces in the Core RAG Engine

| Class / Function | File Path | Role and Responsibility |
| --- | --- | --- |
| `LightRAG` | `lightrag/lightrag.py` | Entry point class managing pipeline, LLM roles, and storage backends [lightrag/lightrag.py:1-231](). |
| `_PipelineMixin` | `lightrag/pipeline.py` | Mixin implementing document ingestion lifecycle and chunk processing [lightrag/lightrag.py:209](). |
| `extract_entities` | `lightrag/operate.py` | Performs entity and relation extraction from text chunks [lightrag/operate.py:147](). |
| `kg_query` | `lightrag/operate.py` | Core query executor supporting multi-mode retrieval [lightrag/operate.py:148](). |
| `QueryParam` | `lightrag/base.py` | Typed dataclass specifying query modes and token budgets [lightrag/base.py:133](). |
| `BaseGraphStorage` | `lightrag/base.py` | Abstract interface for knowledge graph storage backends [lightrag/base.py:126](). |
| `BaseVectorStorage` | `lightrag/base.py` | Abstract interface for vector embedding storage backends [lightrag/base.py:128](). |
| `BaseKVStorage` | `lightrag/base.py` | Abstract interface for key-value storage backends [lightrag/base.py:127](). |

Sources: [lightrag/lightrag.py:1-231](), [lightrag/base.py:126-139]()

---

### Bridging Natural Language to Code Entities

Title: Natural Language Input to Extraction Code Path
```mermaid
graph TD
    NLInput["Natural Language Text Document"]

    LightRAG["LightRAG.ainsert API"]
    PipelineMixin["_PipelineMixin"]
    Chunker["chunking_by_token_size"]
    ExtractEntities["extract_entities"]
    Prompts["prompt templates entity_extraction_system_prompt"]
    KVStorage["BaseKVStorage.insert"]
    GraphStore["BaseGraphStorage upsert_node/upsert_edge"]
    VectorStore["BaseVectorStorage.insert"]

    NLInput -->|Ingestion| LightRAG
    LightRAG --> PipelineMixin
    PipelineMixin --> Chunker
    Chunker --> ExtractEntities
    ExtractEntities --> Prompts
    ExtractEntities -->|Writes| KVStorage
    ExtractEntities -->|Writes| GraphStore
    ExtractEntities -->|Writes| VectorStore
```
Sources: [lightrag/lightrag.py:162-231](), [lightrag/operate.py:147](), [lightrag/prompt.py:56-102]()

Title: Query Request to Retrieval Components
```mermaid
graph TD
    UserQuery["User Query Natural Language"]

    LightRAG["LightRAG.aquery API"]
    KGQuery["kg_query"]
    QueryParam["QueryParam settings mode token budgets"]
    GraphStore["BaseGraphStorage"]
    VectorStore["BaseVectorStorage"]
    KVStorage["BaseKVStorage"]
    LLM["LLM Context Assembly"]

    UserQuery --> LightRAG
    LightRAG --> KGQuery
    KGQuery --> QueryParam
    KGQuery --> GraphStore
    KGQuery --> VectorStore
    KGQuery --> KVStorage
    KGQuery --> LLM
```
Sources: [lightrag/lightrag.py:162-231](), [lightrag/operate.py:148](), [lightrag/base.py:133-139]()

---

For a deeper technical dive, each subsystem is expanded in dedicated child pages:
- [LightRAG Class and Pipeline Orchestration](#2.1)
- [Entity and Relation Extraction](#2.2)
- [Retrieval and Query Modes](#2.3)
- [Text Chunking Strategies](#2.4)
- [Concurrency, Caching, and Utilities](#2.5)

---

# Summary

The Core RAG Engine is the central coordinator converting raw text into structured knowledge and enabling sophisticated querying powered by a hybrid KG + vector approach. Its architecture balances modular storage abstractions, LLM-driven extraction intelligence, and multi-mode retrieval to deliver scalable, extensible RAG capabilities in LightRAG.

Sources: [lightrag/lightrag.py:1-231](), [lightrag/operate.py:1-196](), [lightrag/base.py:64-139](), [lightrag/prompt.py:56-102](), [lightrag/utils.py:156-209]()

---

