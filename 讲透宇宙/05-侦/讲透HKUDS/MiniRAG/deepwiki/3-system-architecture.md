<!-- source: DeepWiki mcp.deepwiki.com · repo HKUDS/MiniRAG · page 3 System Architecture · fetched 2026-11-09 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [minirag/kg/weaviate_impl.py](minirag/kg/weaviate_impl.py)
- [minirag/minirag.py](minirag/minirag.py)
- [tests/test_weaviate.py](tests/test_weaviate.py)

</details>



This document provides an overview of the MiniRAG system architecture. It explains the high-level design, key components, and how they interact to provide retrieval-augmented generation capabilities optimized for small language models (SLMs). For details about specific components, see [Core Components](#2.1), [Data Flow](#2.2), and [Storage Layer](#2.3).

## High-Level Architecture Overview

The MiniRAG system is built with a modular architecture that separates concerns across several logical layers while providing flexibility through pluggable components.

### System Architecture Diagram

```mermaid
graph TD
    subgraph "Core Components"
        MiniRAGClass["MiniRAG Class"]
        IndexingPipeline["Indexing Pipeline"]
        QueryPipeline["Query Pipeline"]
    end
    
    subgraph "Storage Layer"
        KVStorage["BaseKVStorage"]
        VectorStorage["BaseVectorStorage"]
        GraphStorage["BaseGraphStorage"]
        DocStatusStorage["DocStatusStorage"]
    end
    
    subgraph "External Components"
        LLM["Language Models"]
        EmbeddingModels["Embedding Models"]
    end
    
    InputDocs["Input Documents"] --> IndexingPipeline
    UserQuery["User Query"] --> QueryPipeline
    
    IndexingPipeline --> KVStorage
    IndexingPipeline --> VectorStorage
    IndexingPipeline --> GraphStorage
    IndexingPipeline --> DocStatusStorage
    
    QueryPipeline --> KVStorage
    QueryPipeline --> VectorStorage
    QueryPipeline --> GraphStorage
    
    IndexingPipeline --> EmbeddingModels
    QueryPipeline --> EmbeddingModels
    QueryPipeline --> LLM
    
    MiniRAGClass --> IndexingPipeline
    MiniRAGClass --> QueryPipeline
```

Sources: [minirag/minirag.py:119-607](), [minirag/base.py:49-149]()

## Architecture Design Principles

MiniRAG is built on several key architectural principles:

1. **Modular Design**: The system is composed of interchangeable components that can be swapped without affecting the overall functionality.

2. **Storage Abstraction**: All storage operations are performed through abstract interfaces that allow multiple backend implementations.

3. **Workflow Separation**: Document processing and query processing follow separate, well-defined workflows.

4. **Extensibility**: The system can be extended with new storage backends, embedding models, and language models.

5. **Heterogeneous Graph Indexing**: Documents are processed into a graph structure that connects text chunks with entities and their relationships.

6. **Multi-Mode Querying**: Support for different retrieval strategies (light, naive, mini) to optimize for different use cases.

### Storage System Design

```mermaid
classDiagram
    class StorageNameSpace {
        +namespace: str
        +global_config: dict
        +index_done_callback()
        +query_done_callback()
    }
    
    class BaseVectorStorage {
        +embedding_func: EmbeddingFunc
        +query(query, top_k)
        +upsert(data)
    }
    
    class BaseKVStorage {
        +get_by_id(id)
        +get_by_ids(ids)
        +filter_keys(data)
        +upsert(data)
    }
    
    class BaseGraphStorage {
        +get_node(node_id)
        +get_edge(source_id, target_id)
        +upsert_node(node_id, data)
        +upsert_edge(source_id, target_id, data)
    }
    
    class DocStatusStorage {
        +get_status_counts()
        +get_failed_docs()
        +get_pending_docs()
    }
    
    StorageNameSpace <|-- BaseVectorStorage
    StorageNameSpace <|-- BaseKVStorage
    StorageNameSpace <|-- BaseGraphStorage
    BaseKVStorage <|-- DocStatusStorage
```

Sources: [minirag/base.py:49-197]()

## Component Interaction in Key Workflows

### Document Indexing Workflow

The document indexing workflow processes input documents into a queryable knowledge base:

```mermaid
sequenceDiagram
    participant Client
    participant MiniRAG
    participant Chunking
    participant EntityExtraction
    participant Storage
    
    Client->>MiniRAG: insert(documents)
    MiniRAG->>MiniRAG: apipeline_enqueue_documents()
    MiniRAG->>Storage: Store document status as PENDING
    MiniRAG->>MiniRAG: apipeline_process_enqueue_documents()
    
    loop For each document
        MiniRAG->>Chunking: chunking_func(document)
        Chunking-->>MiniRAG: document chunks
        MiniRAG->>Storage: Store chunks in chunks_vdb and text_chunks
        MiniRAG->>Storage: Update document status to PROCESSED
    end
    
    MiniRAG->>EntityExtraction: extract_entities(chunks)
    EntityExtraction->>Storage: Store entities in entities_vdb
    EntityExtraction->>Storage: Store relationships in relationships_vdb
    EntityExtraction->>Storage: Build graph in chunk_entity_relation_graph
    
    MiniRAG->>MiniRAG: _insert_done()
    MiniRAG->>Storage: Finalize storage operations
    MiniRAG-->>Client: Done
```

Sources: [minirag/minirag.py:336-385](), [minirag/minirag.py:387-446](), [minirag/minirag.py:447-511]()

### Query Processing Workflow

The query processing workflow retrieves relevant information and generates responses:

```mermaid
sequenceDiagram
    participant Client
    participant MiniRAG
    participant QueryProcessor
    participant Storage
    participant LLM
    
    Client->>MiniRAG: query(query, param)
    
    alt param.mode == "light"
        MiniRAG->>QueryProcessor: hybrid_query()
    else param.mode == "mini"
        MiniRAG->>QueryProcessor: minirag_query()
    else param.mode == "naive"
        MiniRAG->>QueryProcessor: naive_query()
    end
    
    QueryProcessor->>Storage: Retrieve relevant information
    Storage-->>QueryProcessor: Retrieved context
    
    QueryProcessor->>LLM: Generate response with context
    LLM-->>QueryProcessor: Generated response
    
    QueryProcessor-->>MiniRAG: Response
    MiniRAG->>MiniRAG: _query_done()
    MiniRAG-->>Client: Response
```

Sources: [minirag/minirag.py:529-576]()

## Key Classes and Their Roles

### MiniRAG Class

The `MiniRAG` class serves as the main entry point and orchestrator for the entire system:

```mermaid
classDiagram
    class MiniRAG {
        +working_dir: str
        +kv_storage: str
        +vector_storage: str
        +graph_storage: str
        +doc_status_storage: str
        +embedding_func: EmbeddingFunc
        +llm_model_func: callable
        +insert(string_or_strings): None
        +query(query, param): str
        +ainsert(input, split_by_character, split_by_character_only, ids): None
        +aquery(query, param): str
        -_get_storage_class(storage_name): dict
        -apipeline_enqueue_documents(input, ids): None
        -apipeline_process_enqueue_documents(split_by_character, split_by_character_only): None
    }
```

The `MiniRAG` class is responsible for:

1. **System Initialization**: Setting up storage instances and processing pipelines
2. **Document Processing**: Managing the document indexing workflow
3. **Query Processing**: Handling user queries and generating responses
4. **Storage Management**: Coordinating operations across multiple storage backends

Sources: [minirag/minirag.py:119-607]()

### Storage Component Initialization

During initialization, `MiniRAG` creates multiple storage instances:

```mermaid
flowchart TD
    MiniRAG["MiniRAG.__post_init__()"] --> KV["Create KV Storage"]
    MiniRAG --> Vector["Create Vector Storage"]
    MiniRAG --> Graph["Create Graph Storage"]
    MiniRAG --> DocStatus["Create DocStatus Storage"]
    
    KV --> full_docs["full_docs: key_string_value_json_storage_cls"]
    KV --> text_chunks["text_chunks: key_string_value_json_storage_cls"]
    KV --> llm_response_cache["llm_response_cache: key_string_value_json_storage_cls"]
    
    Vector --> entities_vdb["entities_vdb: vector_db_storage_cls"]
    Vector --> entity_name_vdb["entity_name_vdb: vector_db_storage_cls"]
    Vector --> relationships_vdb["relationships_vdb: vector_db_storage_cls"]
    Vector --> chunks_vdb["chunks_vdb: vector_db_storage_cls"]
    
    Graph --> chunk_entity_relation_graph["chunk_entity_relation_graph: graph_storage_cls"]
    
    DocStatus --> doc_status["doc_status: doc_status_storage_cls"]
```

Sources: [minirag/minirag.py:186-308]()

### Query Parameter Configuration

The `QueryParam` class configures how queries are processed:

```mermaid
classDiagram
    class QueryParam {
        +mode: Literal["light", "naive", "mini"]
        +only_need_context: bool
        +only_need_prompt: bool
        +response_type: str
        +stream: bool
        +top_k: int
        +max_token_for_text_unit: int
        +max_token_for_global_context: int
        +max_token_for_local_context: int
        +max_token_for_node_context: int
        +hl_keywords: list[str]
        +ll_keywords: list[str]
        +conversation_history: list[dict]
        +history_turns: int
    }
```

The `QueryParam` class controls:

1. **Query Mode**: Determines which retrieval strategy to use
2. **Response Format**: Configures the response format and token limits
3. **Retrieval Parameters**: Sets parameters for retrieval, such as number of items to retrieve
4. **Context Control**: Controls how much context to include in the prompt

Sources: [minirag/base.py:18-46]()

### Storage System Implementation

The storage system is based on abstract base classes with multiple concrete implementations:

| Storage Type | Base Class | Available Implementations |
|--------------|------------|---------------------------|
| Vector Storage | `BaseVectorStorage` | NanoVectorDBStorage, ChromaVectorDBStorage, OracleVectorDBStorage, TiDBVectorDBStorage, MilvusVectorDBStorage, PGVectorStorage |
| Key-Value Storage | `BaseKVStorage` | JsonKVStorage, OracleKVStorage, MongoKVStorage, RedisKVStorage, TiDBKVStorage, PGKVStorage |
| Graph Storage | `BaseGraphStorage` | NetworkXStorage, Neo4JStorage, OracleGraphStorage, MongoGraphStorage, TiDBGraphStorage, PGGraphStorage, AGEStorage, GremlinStorage |
| Document Status Storage | `DocStatusStorage` | JsonDocStatusStorage, PGDocStatusStorage |

The storage implementations are dynamically loaded using a lazy import mechanism:

```python
def _get_storage_class(self, storage_name: str) -> dict:
    import_path = STORAGES[storage_name]
    storage_class = lazy_external_import(import_path, storage_name)
    return storage_class
```

Sources: [minirag/minirag.py:39-62](), [minirag/minirag.py:311-314]()

## Summary

The MiniRAG system architecture is built on a modular design with clear separation of concerns. The system is centered around the `MiniRAG` class, which orchestrates the interaction between various components. The storage layer provides a flexible foundation with pluggable backends, while the document processing and query processing pipelines implement the core functionality.

Key architectural features include:

1. **Modular Storage System**: Abstract base classes with multiple implementations
2. **Heterogeneous Graph Indexing**: Building a graph that connects document chunks with entities
3. **Multiple Query Modes**: Different retrieval strategies for different use cases
4. **Extensible Design**: Support for custom storage backends, embedding models, and language models

For more details about specific aspects of the architecture, refer to:
- [Core Components](#2.1) for information about each component's responsibilities
- [Data Flow](#2.2) for a detailed explanation of data flow during indexing and querying
- [Storage Layer](#2.3) for information about storage implementations

Sources: [minirag/minirag.py](), [minirag/base.py](), [main.py]()

---

