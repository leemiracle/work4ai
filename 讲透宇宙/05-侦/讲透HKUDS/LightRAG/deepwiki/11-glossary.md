<!-- source: DeepWiki mcp.deepwiki.com · repo HKUDS/LightRAG · page 11 Glossary · fetched 2026-11-09 -->

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README-id.md](README-id.md)
- [README-ja.md](README-ja.md)
- [README-zh.md](README-zh.md)
- [README.md](README.md)
- [docs/FileProcessingPipeline-zh.md](docs/FileProcessingPipeline-zh.md)
- [docs/FileProcessingPipeline.md](docs/FileProcessingPipeline.md)
- [docs/design/LatexEscapeRepairContract.md](docs/design/LatexEscapeRepairContract.md)
- [docs/design/PipelineConcurrencyContract.md](docs/design/PipelineConcurrencyContract.md)
- [lightrag/base.py](lightrag/base.py)
- [lightrag/exceptions.py](lightrag/exceptions.py)
- [lightrag/kg/memgraph_impl.py](lightrag/kg/memgraph_impl.py)
- [lightrag/kg/mongo_impl.py](lightrag/kg/mongo_impl.py)
- [lightrag/kg/neo4j_impl.py](lightrag/kg/neo4j_impl.py)
- [lightrag/kg/postgres_impl.py](lightrag/kg/postgres_impl.py)
- [lightrag/kg/qdrant_impl.py](lightrag/kg/qdrant_impl.py)
- [lightrag/kg/redis_impl.py](lightrag/kg/redis_impl.py)
- [lightrag/lightrag.py](lightrag/lightrag.py)
- [lightrag/operate.py](lightrag/operate.py)
- [lightrag/parser/param_schema.py](lightrag/parser/param_schema.py)
- [lightrag/parser/routing.py](lightrag/parser/routing.py)
- [lightrag/prompt.py](lightrag/prompt.py)
- [lightrag/utils.py](lightrag/utils.py)
- [tests/chunker/test_chunk_options_persistence.py](tests/chunker/test_chunk_options_persistence.py)
- [tests/kg/memgraph_impl/test_memgraph_all_edges_dedup.py](tests/kg/memgraph_impl/test_memgraph_all_edges_dedup.py)
- [tests/llm/test_vlm_json_escape_repair.py](tests/llm/test_vlm_json_escape_repair.py)
- [tests/parser/test_engine_params.py](tests/parser/test_engine_params.py)
- [tests/parser/test_hint_params.py](tests/parser/test_hint_params.py)
- [tests/utils/test_embedding_func_shape_validation.py](tests/utils/test_embedding_func_shape_validation.py)

</details>



This page provides technical definitions and implementation details for core concepts, terms, and architectural components within the LightRAG codebase. It connects natural language concepts, domain terminology, and code entities, enabling developers to navigate the internals effectively.

---

## Core Architectural Concepts

### Dual-Level Retrieval
LightRAG implements retrieval-augmented generation using a **dual-level retrieval** strategy combining:

- **Knowledge Graph (KG) Retrieval**: Retrieves entities and relationships from a structured knowledge graph representation.
- **Vector Similarity Retrieval**: Retrieves relevant text chunks or embeddings from large documents.

This is orchestrated by functions in `lightrag/operate.py`, balancing token budgets among entities, relations, and chunks. It supports multiple retrieval modes such as `"local"`, `"global"`, `"hybrid"`, `"naive"`, and `"mix"` to tailor retrieval scope and strategy [lightrag/base.py:90-101]().

The retrieval logic integrates keyword extraction, reranking of chunks, and LLM prompt generation, ensuring high-quality context assembly for final answer generation.

Sources: [lightrag/base.py:90-101](), [lightrag/operate.py:1-63]()

---

### Workspace
A **workspace** is a logical isolation layer for data within the same physical storage backend. It enables multiple independent RAG datasets to coexist on the same database instance, separated by attributes or namespaces.

- In **Neo4j**, workspaces correspond to node labels or relationship types sanitized and quoted suitably to avoid Cypher injection [lightrag/kg/neo4j_impl.py:117-142]().
- In **MongoDB** and **PostgreSQL**, workspace strings are used to generate collection/table prefixes ensuring separation [lightrag/kg/mongo_impl.py:85-100](), [lightrag/kg/postgres_impl.py:89-101]().
- At runtime, the workspace context is managed via environment variables or explicit parameters in classes like `LightRAG` [lightrag/lightrag.py:1-231]().

Workspaces also govern resource locking, reservation, and concurrency controls ensuring multi-tenant operations remain isolated without collision [lightrag/lightrag.py:108-121]().

Sources: [lightrag/lightrag.py:108-121](), [lightrag/kg/mongo_impl.py:85-100](), [lightrag/kg/postgres_impl.py:89-101](), [lightrag/kg/neo4j_impl.py:117-142]()

---

### Namespace
A **namespace** controls types of stored data partitions under a workspace, categorizing information by function:

| Namespace       | Description                                       |
|-----------------|-------------------------------------------------|
| `full_docs`     | Raw documents and document metadata              |
| `text_chunks`   | Chunked text segments for embedding & retrieval  |
| `entities`      | Nodes of the knowledge graph, representing entities |
| `relationships` | Edges of the knowledge graph, representing relations |

These namespaces are formalized as constants within `StorageNameSpace` and used in storage backends to route data operations appropriately [lightrag/base.py:1-184]().

Sources: [lightrag/base.py:1-184]()

---

## Data Entities and Schemas

### TextChunkSchema
A dictionary schema representing a text chunk extracted from documents during ingestion. It supports retrieval, reranking, and KG extraction.

- `tokens`: Number of tokens in the chunk.
- `content`: Text content of the chunk.
- `full_doc_id`: ID of the parent full document.
- `chunk_order_index`: Position of the chunk within the parent document.

Defined as a `TypedDict` in `lightrag/base.py` [lightrag/base.py:79-84]().

Sources: [lightrag/base.py:79-84]()

---

### DocStatus
An enumeration of document ingestion pipeline states reflecting lifecycle progress:

- `PENDING`
- `PROCESSING`
- `PARSING`
- `ANALYZING`
- `PROCESSED`
- `FAILED`
- `UNLINKED`

This state machine facilitates automated resumption, failure handling, and consistency guarantees during document ingestion [lightrag/base.py:129-132]().

Sources: [lightrag/base.py:129-132]()

---

### QueryParam
A core dataclass representing query configuration parameters for LightRAG's query pipeline.

Key fields:

- `mode`: Retrieval mode (`local`, `global`, `hybrid`, `naive`, `mix`, `bypass`) [lightrag/base.py:90-101]().
- Token budgets: `max_entity_tokens`, `max_relation_tokens`, `max_total_tokens` [lightrag/base.py:122-136]().
- `top_k`, `chunk_top_k`: Controls quantity of retrieved results [lightrag/base.py:114-121]().
- `enable_rerank`: Whether to use reranker model for chunk sorting [lightrag/base.py:166-170]().
- `include_references`: Include citation sources in the response [lightrag/base.py:171-176]().
- `user_prompt`, `disable_user_prompt_prefix`: Prompt customization options [lightrag/base.py:149-183]().

This class centralizes query behavior and LLM prompt customization [lightrag/base.py:90-183]().

Sources: [lightrag/base.py:90-183]()

---

## Pipeline and Processing

### Chunker
Breaks documents into manageable text segments ("chunks") for embeddings and KG extraction. LightRAG supports four strategies configurable via `process_options` flags:

- **Fixed (`F`)**: Splits by fixed token window size (`chunking_by_token_size`) [lightrag/lightrag.py:141-142]().
- **Recursive (`R`)**: Hierarchical splitting using semantic and character delimiters.
- **Vector (`V`)**: Uses semantic vector similarity to define chunk boundaries.
- **Paragraph (`P`)**: Considers paragraph boundaries, tables, and semantic cues for chunking [docs/FileProcessingPipeline-zh.md:131-135]().

Chunkers are registered and called dynamically during ingestion by the pipeline to optimize chunk quality for downstream retrieval and KG construction.

Sources: [lightrag/lightrag.py:141-142](), [docs/FileProcessingPipeline-zh.md:131-135]()

---

### Extraction (Entity & Relation)
LLM-driven process extracting semantic nodes and edges as:

- **Entities**: Extracted from chunk text describing concepts, people, places, etc.
- **Relationships**: Binary relations linking two entities describing interactions or attributes [lightrag/prompt.py:56-102]().

Extraction uses prompt templates with strict delimiter syntax to parse tuples output by LLMs consistent with LightRAG's KG schema [lightrag/prompt.py:56-102]().

Sources: [lightrag/prompt.py:56-102]()

---

### Gleaning
An iterative LLM extraction refinement process which continues probing chunks for additional entities and relations beyond initial pass, controlled by constants like `DEFAULT_MAX_GLEANING` [lightrag/lightrag.py:47-52]().

Sources: [lightrag/lightrag.py:47-52]()

---

### Role-Specific LLM Configuration
To support distinct tasks, LightRAG defines multiple LLM roles with tailored settings:

- `EXTRACT`: Entity and relation extraction role.
- `QUERY`: Query answering role.
- `KEYWORDS`: Keyword extraction role.
- `VLM`: Vision-Language Model role (for multimodal inputs).

Each role has specific LLM configurations managed via `RoleLLMConfig` and exposed via the `ROLES` registry to select runtime behavior [lightrag/lightrag.py:215-223]().

Sources: [lightrag/lightrag.py:215-223]()

---

## Storage Backends

| Term                | Description                                                                            | Code Pointer                             |
|---------------------|----------------------------------------------------------------------------------------|----------------------------------------|
| **KV Storage**       | Key-Value store for document metadata, LLM cache, admission control                   | `BaseKVStorage` [lightrag/base.py:126-128]()       |
| **Graph Storage**    | Storage for the structured knowledge graph: entities and relations                    | `BaseGraphStorage` [lightrag/base.py:126-128]()    |
| **Vector Storage**   | Stores embeddings for text chunks, entities, and relations, enabling semantic search  | `BaseVectorStorage` [lightrag/base.py:126-128]()   |
| **DocStatus Storage**| Manages status and lifecycle states of document ingestion                              | `DocStatusStorage` [lightrag/base.py:130-132]()  |

Implementations exist for various backends like **MongoDB**, **Neo4j**, **PostgreSQL AGE**, **Milvus**, **NanoVectorDB**, **Qdrant**, and **FAISS** [lightrag/kg/mongo_impl.py:1-167](), [lightrag/kg/neo4j_impl.py:1-176](), [lightrag/kg/postgres_impl.py:1-166](), [lightrag/kg/qdrant_impl.py:1-198]().

Sources: [lightrag/base.py:126-132](), [lightrag/kg/mongo_impl.py:1-167](), [lightrag/kg/neo4j_impl.py:1-176](), [lightrag/kg/postgres_impl.py:1-166](), [lightrag/kg/qdrant_impl.py:1-198]()

---

## Technical Component Mapping

### Diagram: Natural Language Space to Code Entity Space: Querying
```mermaid
graph TD
    "UserQuery"["User Query (Natural Language)"] --> "QueryParam"["QueryParam Class (base.py)"]
    "QueryParam" --> "kg_query"["kg_query() Function (operate.py)"]

    subgraph "Retrieval Logic (Code Space)"
        "kg_query" --> "LocalRetriever"["Local Retrieval (Entity KG)"]
        "kg_query" --> "GlobalRetriever"["Global Retrieval (Relation KG)"]
        "kg_query" --> "NaiveRetriever"["naive_query() Function (operate.py)"]
    end

    "LocalRetriever" --> "EntitiesVDB"["entities_vdb (BaseVectorStorage)"]
    "GlobalRetriever" --> "RelationsVDB"["relationships_vdb (BaseVectorStorage)"]
    "NaiveRetriever" --> "ChunksVDB"["chunks_vdb (BaseVectorStorage)"]

    "EntitiesVDB" --> "LLM_Call"["use_llm_func_with_cache()"]
    "RelationsVDB" --> "LLM_Call"
    "ChunksVDB" --> "LLM_Call"

    "LLM_Call" --> "FinalResponse"["Final Natural Language Response"]
```
Sources: [lightrag/base.py:90-101](), [lightrag/operate.py:1-63]()

---

### Diagram: Natural Language Space to Code Entity Space: Ingestion Pipeline
```mermaid
graph TD
    "RawDoc"["Raw Document (PDF, DOCX)"] --> "DocumentRoutes"["document_routes.py Endpoint"]
    "DocumentRoutes" --> "PipelineEnqueue"["_PipelineMixin.apipeline_enqueue_documents() (lightrag.py)"]
    
    "PipelineEnqueue" --> "Chunker"["chunking_by_token_size() (chunker.py)"]

    subgraph "Extraction Phase"
        "Chunker" --> "ExtractEntities"["extract_entities() (operate.py)"]
        "ExtractEntities" --> "PromptTemplate"["PROMPTS['entity_extraction_system_prompt'] (prompt.py)"]
    end

    "ExtractEntities" --> "GraphStorage"["BaseGraphStorage: upsert_node/edge()"]
    "ExtractEntities" --> "VectorStorage"["BaseVectorStorage: upsert embeddings"]

    subgraph "Persisted Storage Backends"
        "GraphStorage" --> "MongoGraph"["MongoGraphStorage (mongo_impl.py)"]
        "GraphStorage" --> "PGGraph"["PGGraphStorage (postgres_impl.py)"]
        "VectorStorage" --> "QdrantVector"["QdrantVectorDBStorage (qdrant_impl.py)"]
    end
```
Sources: [lightrag/lightrag.py:1-231](), [lightrag/operate.py:1-196](), [lightrag/prompt.py:56-102](), [lightrag/kg/mongo_impl.py:1-167](), [lightrag/kg/postgres_impl.py:1-166](), [lightrag/kg/qdrant_impl.py:1-198]()

---

## Internal Abbreviations & Constants

| Term                       | Description                                                                                   | Code Location                              |
|----------------------------|-----------------------------------------------------------------------------------------------|--------------------------------------------|
| `VDB`                      | Vector Database: storage backend for embeddings                                              | [lightrag/base.py:126-128]()               |
| `KG`                       | Knowledge Graph: structured graph storage of entities and relations                          | [lightrag/base.py:126-128]()               |
| `MM`                       | Multimodal: Refers to images, tables, equations processed alongside text                      | [docs/FileProcessingPipeline-zh.md:1-152]() |
| `tuple_delimiter`           | The special delimiter separating LLM extraction fields, default: `<|#|>`                     | [lightrag/prompt.py:14-14]()               |
| `completion_delimiter`      | Marker indicating end of LLM generation, default: `<|COMPLETE|>`                             | [lightrag/prompt.py:15-15]()               |
| `GRAPH_FIELD_SEP`           | Internal separator string for complex graph fields, typically `"::&::"`                      | [lightrag/constants.py:1-100]()            |
| `PARSED_DIR_NAME`           | Directory name for parsed document artifacts, default `"__parsed__"`                          | [lightrag/utils.py:60-67]()                |
| `DocStatus`                 | Document ingestion lifecycle status flags                                                    | [lightrag/base.py:129-132]()               |

Sources: [lightrag/base.py:126-132](), [lightrag/prompt.py:14-15](), [lightrag/utils.py:60-67](), [docs/FileProcessingPipeline-zh.md:1-152]()