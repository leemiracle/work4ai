<!-- source: DeepWiki mcp.deepwiki.com · repo zylon-ai/private-gpt · page 4 Services · fetched 2026-10-26 -->

# Services

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [fern/docs/assets/ui.png](fern/docs/assets/ui.png)
- [private_gpt/server/__init__.py](private_gpt/server/__init__.py)

</details>



This page provides an overview of the core services that power PrivateGPT, explaining their purpose, architecture, and interactions. Services in PrivateGPT are the high-level functional components that expose specific capabilities through the API. They implement the business logic for various features such as document ingestion, chat functionality, and text summarization.

## Service Overview

PrivateGPT is structured around a set of services that provide both high-level abstractions for common tasks and low-level primitives for advanced use cases. These services are exposed through a RESTful API that follows and extends the OpenAI API standard.

```mermaid
graph TD
    subgraph "PrivateGPT_Services"
        ["IngestService"]
        ["ChatService"]
        ["ChunksService"]
        ["SummarizeService"]
        ["EmbeddingService"]
    end
    
    User["End User"] -->|Documents| ["IngestService"]
    User -->|Queries| ["ChatService"]
    User -->|Search Queries| ["ChunksService"]
    User -->|Texts to Summarize| ["SummarizeService"]
    User -->|Text for Embeddings| ["EmbeddingService"]
    
    subgraph "Core_Components"
        ["LLMComponent"]
        ["EmbeddingComponent"]
        ["VectorStoreComponent"]
        ["NodeStoreComponent"]
    end
    
    ["IngestService"] -->|Uses| ["EmbeddingComponent"]
    ["IngestService"] -->|Uses| ["VectorStoreComponent"]
    ["IngestService"] -->|Uses| ["NodeStoreComponent"]
    
    ["ChatService"] -->|Uses| ["LLMComponent"]
    ["ChatService"] -->|Uses| ["EmbeddingComponent"]
    ["ChatService"] -->|Uses| ["VectorStoreComponent"]
    ["ChatService"] -->|Uses| ["NodeStoreComponent"]
    
    ["ChunksService"] -->|Uses| ["EmbeddingComponent"]
    ["ChunksService"] -->|Uses| ["VectorStoreComponent"]
    
    ["SummarizeService"] -->|Uses| ["LLMComponent"]
    ["SummarizeService"] -->|Uses| ["EmbeddingComponent"]
    ["SummarizeService"] -->|Uses| ["VectorStoreComponent"]
    
    ["EmbeddingService"] -->|Uses| ["EmbeddingComponent"]
```

*Service Architecture Overview*

Sources: [README.md:95-107]()

## Service Architecture Pattern

PrivateGPT follows a consistent architectural pattern for its services, with a clear separation between the API layer and business logic. The `private_gpt.server` package contains sub-packages for each functional area, typically consisting of a FastAPI router and a corresponding service implementation.

```mermaid
graph TD
    subgraph "Service_Pattern"
        ["*_router.py"]
        ["*_service.py"]
        ["Components"]
        
        ["*_router.py"] -->|"request.state.injector.get()"| ["*_service.py"]
        ["*_service.py"] -->|"Constructor Injection"| ["Components"]
    end
    
    subgraph "Code_Entity_Mapping"
        ["summarize_router.py"]
        ["SummarizeService"]
        ["LLMComponent"]
        ["VectorStoreComponent"]
        
        ["summarize_router.py"] -- "imports" --> ["SummarizeService"]
        ["SummarizeService"] -- "uses" --> ["LLMComponent"]
        ["SummarizeService"] -- "uses" --> ["VectorStoreComponent"]
    end
```

*Service Architecture Pattern and Code Mapping*

Sources: [README.md:98-107](), [private_gpt/server/recipes/summarize/summarize_router.py:1-86]()

Each service consists of:
1. A router file (`*_router.py`) defining the API endpoints using FastAPI.
2. A service file (`*_service.py`) implementing the business logic and interacting with LlamaIndex abstractions.
3. Dependencies on various components that provide implementations of the core abstractions (LLM, Embeddings, Vector Store).

## High-Level Services

These services abstract the complexity of implementing a RAG (Retrieval Augmented Generation) pipeline.

### Ingest Service
The Ingest Service manages the document ingestion pipeline, processing documents for later retrieval. It handles document parsing, text chunking, and embedding generation. For details, see [Ingestion Service](#4.1).

**Key Features**:
- Document parsing and metadata extraction.
- Text chunking with configurable parameters.
- Embedding generation and storage in `VectorStoreComponent`.

Sources: [README.md:29-30](), [README.md:98-101]()

### Chat Service
The Chat Service provides conversational capabilities with optional context retrieval from ingested documents. It abstracts prompt engineering and response generation. For details, see [Chat Service](#4.2).

**Key Features**:
- Context-aware chat using the RAG pipeline.
- Support for streaming and non-streaming responses.
- Source citation for retrieved document chunks.

Sources: [README.md:31-32](), [README.md:98-101]()

### Summarize Service
The Summarize Service generates concise summaries from text or documents using advanced LlamaIndex response modes like `TREE_SUMMARIZE`. For details, see [Summarize Service](#4.3).

**Key Features**:
- Summarization of provided text or existing ingested documents.
- Integration with `SummaryIndex` for hierarchical summarization.

Sources: [private_gpt/server/recipes/summarize/summarize_router.py:28-86](), [README.md:98-101]()

## Low-Level Services

These services provide lower-level primitives for advanced users to implement custom RAG pipelines.

### Chunks Service
The Chunks Service retrieves relevant chunks from ingested documents based on semantic similarity. It allows users to see exactly what context would be provided to an LLM.

**Key Features**:
- Semantic search for relevant document chunks.
- Filtering by document IDs via `ContextFilter`.

Sources: [README.md:36-37]()

### Embedding Service
The Embedding Service generates vector representations of text for semantic operations.

**Key Features**:
- Text-to-vector conversion using the configured `EmbeddingComponent`.
- OpenAI-compatible embeddings API.

Sources: [README.md:35]()

## RAG Pipeline and Service Interactions

The services work together to implement the RAG pipeline, creating a context-aware AI system:

```mermaid
graph TD
    subgraph "Ingestion_Pipeline"
        ["Document"] --> ["IngestService"]
        ["IngestService"] --> ["VectorStoreComponent"]
    end
    
    subgraph "Retrieval_Generation_Pipeline"
        ["UserQuery"] --> ["ChatService"]
        ["ChatService"] --> ["ChunksService"]
        ["ChunksService"] --> ["VectorStoreComponent"]
        ["VectorStoreComponent"] --> ["RelevantChunks"]
        ["RelevantChunks"] --> ["ChatService"]
        ["ChatService"] --> ["LLMComponent"]
        ["LLMComponent"] --> ["AIResponse"]
    end
```

*RAG Pipeline and Service Interactions*

Sources: [README.md:81-87]()

## Service Design Principles

The PrivateGPT services follow several design principles:

1. **Dependency Injection**: Services are retrieved from an injector (see `di.py`) rather than being instantiated manually, facilitating decoupling.
2. **Abstraction Usage**: Services use LlamaIndex base abstractions (like `BaseEmbedding` or `LLM`) rather than specific provider implementations.
3. **OpenAI Compatibility**: Where possible, service request and response models follow the OpenAI API scheme.

Sources: [README.md:88-95]()

---

