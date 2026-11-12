<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/context-aware-rag · page 1 Context-Aware RAG Overview · fetched 2026-10-26 -->

# Context-Aware RAG Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

Context-Aware RAG is a flexible library designed by NVIDIA to build customized data ingestion and retrieval pipelines for Retrieval Augmented Generation (RAG). This document provides a high-level overview of the system's architecture, components, and data flow. For detailed information about specific components, please refer to their respective documentation pages:

- For system architecture details, see [System Architecture](#2)
- For data ingestion specifics, see [Data Ingestion Service](#2.1)
- For data retrieval specifics, see [Data Retrieval Service](#2.2)
- For GraphRAG capabilities, see [GraphRAG Capabilities](#2.4)

Sources: [README.md:19-34]()

## Key Components

Context-Aware RAG consists of several core components that work together to provide a complete RAG solution:

| Component | Description | Wiki Reference |
|-----------|-------------|---------------|
| Data Ingestion Service | Processes and stores documents from various sources | [#2.1](#2.1) |
| Data Retrieval Service | Handles queries and generates context-aware responses | [#2.2](#2.2) |
| Storage Backend Systems | Includes Neo4j, Milvus, and Cassandra for different data storage needs | [#2.3](#2.3) |
| GraphRAG Capabilities | Extracts knowledge graphs from documents to enhance retrieval | [#2.4](#2.4) |
| Observability Features | Provides monitoring via OpenTelemetry, Jaeger, and Prometheus | [#2.5](#2.5) |

Sources: [README.md:25-31]()

## System Architecture

The system follows a microservices architecture pattern with dedicated services for data ingestion and retrieval, supported by specialized storage backends and comprehensive observability.

```mermaid
graph TD
    Client["Client Applications"] --> DIS["Data Ingestion Service
    /init, /add_doc endpoints"]
    Client --> DRS["Data Retrieval Service
    /init, /call endpoints"]
    
    subgraph "Storage Layer"
        Neo4j["Neo4j 
        (Knowledge Graphs)"]
        Milvus["Milvus
        (Vector Embeddings)"]
        Cassandra["Cassandra
        (Document Metadata)"]
    end
    
    DIS --> Neo4j
    DIS --> Milvus
    DIS --> Cassandra
    DRS --> Neo4j
    DRS --> Milvus
    DRS --> Cassandra
    
    subgraph "Observability Stack"
        OTel["OpenTelemetry Collector"]
        Jaeger["Jaeger - Tracing"]
        Prometheus["Prometheus - Metrics"]
    end
    
    DIS --> OTel
    DRS --> OTel
    OTel --> Jaeger
    OTel --> Prometheus
```

Sources: [README.md:113-142]()

## Data Processing Workflow

The following diagram illustrates the data flow through the Context-Aware RAG system, from document ingestion to query response generation:

```mermaid
flowchart LR
    subgraph "Data Ingestion Pipeline"
        Document["Document Input
        via /add_doc endpoint"] --> Chunking["Document Chunking"]
        Chunking --> Embedding["Generate Embeddings"]
        Embedding --> VectorStorage["Store in Milvus
        vector database"]
        Document --> KGExtraction["Knowledge Graph Extraction"]
        KGExtraction --> GraphStorage["Store in Neo4j
        graph database"]
        Document --> MetadataProcessing["Process Metadata"]
        MetadataProcessing --> MetadataStorage["Store in Cassandra
        metadata storage"]
    end
    
    subgraph "Data Retrieval Pipeline"
        Query["User Query
        via /call endpoint"] --> QueryEmbedding["Generate Query Embedding"]
        QueryEmbedding --> VectorSearch["Vector Search in Milvus"]
        Query --> GraphSearch["Graph Search in Neo4j"]
        VectorSearch --> Ranking["Result Ranking"]
        GraphSearch --> Ranking
        Ranking --> ContextAssembly["Assemble Context"]
        MetadataStorage --> ContextAssembly
        ContextAssembly --> ResponseGeneration["Generate Response"]
    end
```

Sources: [README.md:146-219]()

## API Communication Pattern

The Context-Aware RAG services follow a consistent API pattern for initialization and data processing:

```mermaid
sequenceDiagram
    participant Client as "Client Application"
    participant DIS as "Data Ingestion Service"
    participant DRS as "Data Retrieval Service"
    participant Storage as "Storage Backends"
    
    Client->>DIS: POST /init {uuid: "1", config_path: "/path/to/config.yaml"}
    Note right of DIS: Initialize service with unique UUID
    DIS-->>Client: 200 OK
    
    loop Document Processing
        Client->>DIS: POST /add_doc {document: "text", doc_index: n, doc_metadata: {...}}
        DIS->>Storage: Process and store document
        DIS-->>Client: 200 OK
    end
    
    Client->>DRS: POST /init {uuid: "1", config_path: "/path/to/config.yaml"}
    Note right of DRS: Use same UUID as ingestion service
    DRS-->>Client: 200 OK
    
    Client->>DRS: POST /call {state: {chat: {question: "What happens?"}}}
    DRS->>Storage: Retrieve relevant information
    Storage-->>DRS: Return data
    DRS-->>Client: 200 OK with generated response
```

Sources: [README.md:156-218]()

## Codebase Organization to System Component Mapping

The following diagram maps the conceptual components of the Context-Aware RAG system to their actual implementation in the codebase:

```mermaid
graph TD
    subgraph "System Components"
        DIS["Data Ingestion Service"]
        DRS["Data Retrieval Service"]
        Storage["Storage Backends"]
        Obs["Observability"]
    end
    
    subgraph "Implementation"
        IngestEndpoints["/init and /add_doc endpoints"]
        RetrieveEndpoints["/init and /call endpoints"]
        Neo4jImpl["Neo4j Knowledge Graph"]
        MilvusImpl["Milvus Vector Database"]
        CassandraImpl["Cassandra Metadata Store"]
        OTelImpl["OpenTelemetry Integration"]
    end
    
    DIS --> IngestEndpoints
    DRS --> RetrieveEndpoints
    Storage --> Neo4jImpl
    Storage --> MilvusImpl
    Storage --> CassandraImpl
    Obs --> OTelImpl
    
    subgraph "Docker Components"
        IngestContainer["ctx-rag-data-ingestion container"]
        RetContainer["ctx-rag-data-retrieval container"]
        Neo4jContainer["neo4j container"]
        MilvusContainer["milvus container"]
        CassandraContainer["cassandra container"]
        JaegerContainer["jaeger container"]
        PrometheusContainer["prometheus container"]
    end
    
    IngestEndpoints --> IngestContainer
    RetrieveEndpoints --> RetContainer
    Neo4jImpl --> Neo4jContainer
    MilvusImpl --> MilvusContainer
    CassandraImpl --> CassandraContainer
    OTelImpl --> JaegerContainer
    OTelImpl --> PrometheusContainer
```

Sources: [README.md:113-142]()

## System Deployment Overview

Context-Aware RAG is designed to be deployed as a set of Docker containers, managed via Docker Compose:

```mermaid
graph TD
    subgraph "Docker Compose Environment"
        DIS["ctx-rag-data-ingestion
        Port: VSS_CTX_PORT_IN"]
        DRS["ctx-rag-data-retrieval
        Port: VSS_CTX_PORT_RET"]
        Neo4j["neo4j
        UI Port: 7474"]
        Milvus["milvus"]
        OTel["otel-collector"]
        Jaeger["jaeger
        UI Port: 16686"]
        Prometheus["prometheus
        UI Port: 9090"]
        Cassandra["cassandra"]
    end
    
    Client["External Client"] --> DIS
    Client --> DRS
```

Sources: [README.md:85-144]()

## Getting Started

To begin using Context-Aware RAG, you'll need to:

1. Install prerequisites (Git, uv)
2. Clone the repository
3. Set up a virtual environment
4. Install the package
5. Configure environment variables
6. Deploy using Docker Compose

For detailed deployment instructions, see the [Deployment Guide](#4) and [Docker Deployment](#4.1) pages.

Examples for using the Data Ingestion and Data Retrieval services are provided in the README:

- Data Ingestion: Initialize the service and add documents
- Data Retrieval: Initialize the service with the same UUID and send queries

Sources: [README.md:45-219]()

## Key Features and Benefits

Context-Aware RAG provides several advantages for building RAG pipelines:

1. **Flexible Integration**: Seamlessly integrates with existing data processing workflows
2. **Customizable Pipelines**: Build tailored data ingestion and retrieval pipelines
3. **Knowledge Graph Enhanced Retrieval**: Leverages graph relationships for better context understanding
4. **Comprehensive Observability**: Monitor and troubleshoot with OpenTelemetry-compatible tools
5. **Containerized Deployment**: Easy deployment using Docker Compose

Sources: [README.md:25-34]()

---

