<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/context-aware-rag · page 2 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



This document describes the high-level architecture of the NVIDIA Context-Aware RAG system, presenting the core components and their interactions. For detailed information about specific components, please refer to the dedicated pages for [Data Ingestion Service](#2.1), [Data Retrieval Service](#2.2), [Storage Backend Systems](#2.3), [GraphRAG Capabilities](#2.4), and [Observability Features](#2.5).

## Core Architecture Overview

The Context-Aware RAG system follows a microservices architecture designed for scalability, flexibility, and maintainability. The system consists of two primary services that interact with a multi-modal storage layer and are monitored through a comprehensive observability stack.

### System Components Diagram

```mermaid
graph TD
    Client["Client Applications"] --> DIS["Data Ingestion Service\n(vss_ctx_rag.rest.ingestion)"]
    Client --> DRS["Data Retrieval Service\n(vss_ctx_rag.rest.retrieval)"]
    
    subgraph "Storage Backend"
        Neo4j["Neo4j\n(Knowledge Graphs)"]
        Milvus["Milvus\n(Vector Database)"]
        Cassandra["Cassandra\n(Document Store)"]
    end
    
    DIS --> Neo4j
    DIS --> Milvus
    DIS --> Cassandra
    DRS --> Neo4j
    DRS --> Milvus
    DRS --> Cassandra
    
    subgraph "Observability"
        OTel["OpenTelemetry Collector"]
        Jaeger["Jaeger\n(Tracing)"]
        Prometheus["Prometheus\n(Metrics)"]
    end
    
    DIS --> OTel
    DRS --> OTel
    OTel --> Jaeger
    OTel --> Prometheus
```

Sources: [README.md:115-142]()

## Key Components

The system architecture consists of these principal components:

1. **Data Ingestion Service**: Processes and stores documents in the appropriate storage systems.
2. **Data Retrieval Service**: Retrieves relevant information based on user queries.
3. **Storage Backend**:
   - Neo4j: Stores knowledge graphs for semantic connections
   - Milvus: Manages vector embeddings for semantic search
   - Cassandra: Stores document content and metadata
4. **Observability Stack**:
   - OpenTelemetry: Collects telemetry data
   - Jaeger: Provides distributed tracing capabilities
   - Prometheus: Monitors system metrics

Sources: [README.md:27-31](), [README.md:118-142]()

## Data Processing Workflow

The system operates through two main workflows: ingestion and retrieval. Both services coordinate to provide an efficient RAG (Retrieval Augmented Generation) pipeline.

### Data Flow Diagram

```mermaid
flowchart LR
    subgraph "Ingestion Flow"
        direction LR
        Doc["Document"] --> Preprocess["Preprocessing\n(vss_ctx_rag.ingestion.processing)"]
        Preprocess --> Chunk["Chunking"]
        Chunk --> TwoWays
        
        subgraph TwoWays ["Parallel Processing"]
            direction TB
            Embed["Generate Embeddings\n(vss_ctx_rag.ingestion.embedding)"] --> VecStore["Vector Storage\n(Milvus)"]
            KGExtract["Knowledge Graph Extraction\n(vss_ctx_rag.ingestion.kg)"] --> GraphStore["Graph Storage\n(Neo4j)"]
        end
        
        Doc --> MetaProcess["Metadata Processing"]
        MetaProcess --> MetaStore["Metadata Storage\n(Cassandra)"]
    end
    
    subgraph "Retrieval Flow"
        direction LR
        Query["User Query"] --> QPreprocess["Query Processing\n(vss_ctx_rag.retrieval)"]
        QPreprocess --> QTwoWays
        
        subgraph QTwoWays ["Hybrid Search"]
            direction TB
            QEmbed["Embedding\n(vss_ctx_rag.retrieval.embedding)"] --> VecSearch["Vector Search\n(Milvus)"]
            GraphQuery["Graph Query\n(vss_ctx_rag.retrieval.kg)"] --> GraphSearch["Graph Search\n(Neo4j)"]
        end
        
        VecSearch --> ResultsRank["Result Ranking\n(vss_ctx_rag.retrieval.ranking)"]
        GraphSearch --> ResultsRank
        ResultsRank --> ContextBuild["Context Building"]
        MetaStore --> ContextBuild
        ContextBuild --> LLMResponse["LLM Response Generation"]
    end
```

Sources: [README.md:27-31]()

## Service Communication

The services in Context-Aware RAG communicate through REST APIs, with both the Data Ingestion and Data Retrieval services exposing endpoints for client applications to interact with.

### Service Interaction Diagram

```mermaid
sequenceDiagram
    participant Client as "Client Application"
    participant DIS as "Data Ingestion Service\n(/init, /add_doc)"
    participant DRS as "Data Retrieval Service\n(/init, /call)"
    participant Storage as "Storage Backend"
    
    Client->>DIS: POST /init {uuid: "1", config_path: "..."}
    DIS-->>Client: 200 OK
    
    loop Document Processing
        Client->>DIS: POST /add_doc {document, doc_index, doc_metadata}
        DIS->>Storage: Store processed document
        DIS-->>Client: 200 OK
    end
    
    Client->>DRS: POST /init {uuid: "1", config_path: "..."}
    DRS-->>Client: 200 OK
    
    Client->>DRS: POST /call {state: {chat: {question: "..."}}}
    DRS->>Storage: Retrieve relevant information
    Storage-->>DRS: Return data
    DRS-->>Client: 200 OK with response
```

Sources: [README.md:147-219]()

## API Structure

Both services expose REST APIs with similar initialization patterns but different operational endpoints:

| Service | Endpoint | Purpose | Parameters |
|---------|----------|---------|------------|
| Data Ingestion | `/init` | Initialize service with configuration | `uuid`, `config_path` or `context_config` |
| Data Ingestion | `/add_doc` | Add document to the system | `document`, `doc_index`, `doc_metadata` (optional) |
| Data Retrieval | `/init` | Initialize service with configuration | `uuid`, `config_path` or `context_config` |
| Data Retrieval | `/call` | Process query and retrieve relevant information | `state` containing query information |

Sources: [README.md:154-191](), [README.md:204-218]()

## Deployment Architecture

The system is designed for containerized deployment using Docker and Docker Compose, with each component running in its own container.

### Deployment Diagram

```mermaid
graph TD
    subgraph "Docker Compose Environment"
        DIS["ctx-rag-data-ingestion\nPort: VSS_CTX_PORT_IN"]
        DRS["ctx-rag-data-retrieval\nPort: VSS_CTX_PORT_RET"]
        Neo4j["neo4j\nPort: 7474"]
        Milvus["milvus"]
        OTel["otel-collector"]
        Jaeger["jaeger\nPort: 16686"]
        Prometheus["prometheus\nPort: 9090"]
        Cassandra["cassandra"]
    end
    
    Client["External Client Applications"] --> DIS
    Client --> DRS
    
    subgraph "Volumes"
        Neo4jData["Neo4j Data Volume"]
        MilvusData["Milvus Data Volume"]
        CassandraData["Cassandra Data Volume"]
        LogData["Log Data Volume"]
    end
    
    Neo4j --> Neo4jData
    Milvus --> MilvusData
    Cassandra --> CassandraData
    DIS --> LogData
    DRS --> LogData
```

Sources: [README.md:103-144]()

## Configuration Management

The system uses a configuration file approach that allows customizing both services. Configuration can be provided in two ways:

1. **File-based configuration**: Using the `config_path` parameter
2. **Inline configuration**: Using the `context_config` parameter

Both services must be initialized with the same UUID to ensure they operate on the same data context.

### Configuration Flow

```mermaid
graph TD
    ConfigFile["Configuration File\n(YAML)"] --> ConfigRead["Configuration Loading"]
    Inline["Inline Configuration\n(JSON/Dict)"] --> ConfigRead
    
    ConfigRead --> DIS["Data Ingestion Service"]
    ConfigRead --> DRS["Data Retrieval Service"]
    
    UUID["UUID\n(Unique Identifier)"] --> DIS
    UUID --> DRS
    
    subgraph "Configuration Parameters"
        Embeddings["Embedding Model Settings"]
        ChunkSize["Document Chunking Parameters"]
        KGSettings["Knowledge Graph Extraction Settings"]
        LLMSettings["LLM Configuration"]
        StorageConfig["Storage Backend Settings"]
    end
    
    ConfigRead --> Embeddings
    ConfigRead --> ChunkSize
    ConfigRead --> KGSettings
    ConfigRead --> LLMSettings
    ConfigRead --> StorageConfig
```

Sources: [README.md:156-162](), [README.md:205]()

## Integration Points

The Context-Aware RAG system is designed to integrate with existing workflows through these key integration points:

1. **Client Applications**: Connect via REST APIs
2. **Storage Systems**: Leverage standard clients for Neo4j, Milvus, and Cassandra
3. **LLM Providers**: Support for multiple LLM providers (NVIDIA, OpenAI)
4. **Observability**: Integration with OpenTelemetry-compatible monitoring tools

### Environment Configuration

The system requires setting environment variables for proper operation:

```
NVIDIA_API_KEY         # If using NVIDIA LLMs
NVIDIA_VISIBLE_DEVICES # GPU device ID
OPENAI_API_KEY         # If using OpenAI LLMs
VSS_CTX_PORT_RET       # Data Retrieval Service port
VSS_CTX_PORT_IN        # Data Ingestion Service port
```

Sources: [README.md:93-101]()

## Summary

The NVIDIA Context-Aware RAG architecture provides a comprehensive framework for building customized data ingestion and retrieval pipelines. The microservices-based design, coupled with a multi-modal storage approach and robust observability features, enables flexible and powerful RAG implementations for various use cases.

Each component in the architecture plays a specific role, from processing and storing documents to retrieving relevant information based on user queries. The system's modular design allows for easy customization and extension to meet specific requirements.

---

