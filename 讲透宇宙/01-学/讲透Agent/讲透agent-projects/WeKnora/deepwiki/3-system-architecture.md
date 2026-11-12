<!-- source: DeepWiki mcp.deepwiki.com · repo Tencent/WeKnora · page 3 System Architecture · fetched 2026-10-29 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [config/config.yaml](config/config.yaml)
- [docker-compose.dev.yml](docker-compose.dev.yml)
- [docker-compose.yml](docker-compose.yml)
- [docreader/README.md](docreader/README.md)
- [docreader/config.py](docreader/config.py)
- [docreader/parser/docx_parser.py](docreader/parser/docx_parser.py)
- [docreader/parser/image_preprocess.py](docreader/parser/image_preprocess.py)
- [docreader/preprocess.py](docreader/preprocess.py)
- [docreader/preprocess_worker.py](docreader/preprocess_worker.py)
- [docreader/tests/test_config.py](docreader/tests/test_config.py)
- [docreader/tests/test_docx_tables.py](docreader/tests/test_docx_tables.py)
- [docreader/tests/test_preprocess_runner.py](docreader/tests/test_preprocess_runner.py)
- [go.mod](go.mod)
- [go.sum](go.sum)
- [internal/config/auth_legacy_env_test.go](internal/config/auth_legacy_env_test.go)
- [internal/config/config.go](internal/config/config.go)
- [internal/container/container.go](internal/container/container.go)
- [scripts/dev.sh](scripts/dev.sh)

</details>



## Purpose and Scope

This document provides a comprehensive overview of WeKnora's technical architecture, design patterns, and component interactions. It focuses on the high-level system structure, architectural decisions, and how major subsystems work together to process documents into interactive knowledge.

As a parent page, this section introduces the core architectural foundations and links to dedicated child pages for deep technical dives into specific layers:

- **Service Architecture and Container Orchestration** ([Service Architecture and Container Orchestration](#3.1)) — Microservices architecture, Docker Compose setup, service dependencies, and container communication.
- **RAG Pipeline Architecture** ([RAG Pipeline Architecture](#3.2)) — Document ingestion, chunking, embedding, indexing, retrieval, and generation pipeline.
- **Agent System and ReAct Engine** ([Agent System and ReAct Engine](#3.3)) — Agent execution model, ReAct pattern, tool registry, and iterative reasoning.
- **Storage and Database Layer** ([Storage and Database Layer](#3.4)) — Multi-database architecture including PostgreSQL, Redis, vector stores, graph databases, and file storage.
- **Security and Multi-Tenancy** ([Security and Multi-Tenancy](#3.5)) — Tenant isolation, RBAC access control, organization sharing, SSRF protection, and best practices.
- **Dependency Injection and Service Layer** ([Dependency Injection and Service Layer](#3.6)) — Dependency injection container, service registration, and layered architecture.
- **Event-Driven Architecture and Chat Pipeline** ([Event-Driven Architecture and Chat Pipeline](#3.7)) — Event bus system, chat pipeline plugins, streaming architecture, and event types.

Sources: [internal/container/container.go:113-145]()

---

## Architectural Overview

WeKnora follows a **layered microservices-inspired architecture**, deployed via Docker Compose (`docker-compose.yml`). This enables easy startup and management of core services and optional components configured via profiles.

The backend is implemented in Go using a clean architecture approach with separation into HTTP handlers, application services, and repositories [internal/container/container.go:113-137](). Persistent storage uses multiple database backends, including relational (PostgreSQL), Redis, vector stores, and graph databases [internal/container/container.go:23-53](). 

### Application Layering and Code Entity Mapping

The following diagram bridges natural language architectural layers to specific code entities and packages in the codebase, enabling precise navigation:

```mermaid
graph TB
    subgraph PresentationLayer["Presentation Layer"]
        Frontend["Vue SPA frontend/src"]
        GinRouter["NewRouter internal/router/router.go"]
    end
    
    subgraph HandlerLayer["Handler Layer"]
        SessionHandler["session.Handler internal/handler/session/handler.go"]
        KBHandler["handler.KnowledgeBaseHandler internal/handler/"]
        SkillHandler["handler.SkillHandler internal/handler/"]
        AuthHandler["handler.AuthHandler internal/handler/"]
    end
    
    subgraph ServiceLayer["Service Layer"]
        SessionService["interfaces.SessionService internal/application/service/"]
        KBService["interfaces.KnowledgeBaseService internal/application/service/"]
        ChatPipeline["chatpipeline.EventManager internal/application/service/chat_pipeline/"]
        FileService["interfaces.FileService internal/application/service/file/"]
    end
    
    subgraph RepositoryLayer["Repository Layer"]
        SessionRepo["repository.sessionRepository internal/application/repository/"]
        KBRepo["repository.knowledgeBaseRepository internal/application/repository/"]
        ChunkRepo["repository.chunkRepository internal/application/repository/"]
    end
    
    subgraph DataLayer["Data Layer"]
        PostgreSQL["gorm.DB postgres internal/container/container.go"]
        Redis["redis.Client go-redis/v9 internal/container/container.go"]
        VectorDB["milvusclient / qdrant internal/container/container.go"]
        Neo4j["neo4j.Driver neo4j-go-driver/v6 internal/container/container.go"]
    end
    
    Frontend --> GinRouter
    GinRouter --> SessionHandler
    GinRouter --> SkillHandler
    GinRouter --> AuthHandler
    
    SessionHandler --> SessionService
    SkillHandler --> KBHandler
    
    SessionService --> ChatPipeline
    KBHandler --> KBService
    KBService --> FileService
    
    SessionService --> SessionRepo
    KBService --> KBRepo
    
    SessionRepo --> PostgreSQL
    KBRepo --> PostgreSQL
    ChunkRepo --> PostgreSQL
    
    SessionService --> Redis
```

For detailed information on DI and service layers, see [Dependency Injection and Service Layer](#3.6).

Sources: [internal/container/container.go:23-137]()

### Deployment Architecture

WeKnora is deployed as containerized microservices orchestrated by Docker Compose (`docker-compose.yml`). Profiles enable optional services and infrastructure components such as vector databases, document parsers, and observability tools.

The high-level deployment topology is structured as follows:

```mermaid
graph TB
    subgraph CoreServices["Core Services"]
        Frontend["frontend WeKnora-frontend docker-compose.yml:2"]
        App["app WeKnora-app docker-compose.yml:36"]
        Postgres["postgres paradedb/paradedb docker-compose.dev.yml:4"]
        Redis["redis redis:7.0-alpine docker-compose.dev.yml:26"]
    end
    
    subgraph ExternalIntegrationProfiles["External Integration Profiles"]
        Docreader["docreader docreader:50051 docreader/README.md:10"]
        MinIO["minio pgsty/minio docker-compose.dev.yml:84"]
        Qdrant["qdrant qdrant/qdrant docker-compose.dev.yml:107"]
        Milvus["milvus milvusdb/milvus docker-compose.dev.yml:177"]
        Neo4j["neo4j neo4j:latest docker-compose.dev.yml:206"]
        OpenSearch["opensearch opensearchproject/opensearch docker-compose.dev.yml:126"]
    end
    
    Frontend --> App
    App --> Postgres
    App --> Redis
    App -.->|"DOCREADER_ADDR"| Docreader
    App -.->|"RETRIEVE_DRIVER=qdrant"| Qdrant
    App -.->|"RETRIEVE_DRIVER=milvus"| Milvus
    App -.->|"STORAGE_TYPE=minio"| MinIO
    App -.->|"NEO4J_ENABLE"| Neo4j
    App -.->|"RETRIEVE_DRIVER=opensearch"| OpenSearch
```

For details on service orchestration, profiles, and inter-container communication, see [Service Architecture and Container Orchestration](#3.1).

Sources: [docker-compose.yml:1-67](), [docker-compose.dev.yml:1-212](), [docreader/README.md:1-15]()

---

## Core Architectural Patterns

### Dependency Injection with uber-go/dig

WeKnora leverages the `uber-go/dig` library for dependency injection and inversion of control [internal/container/container.go:33](). The container setup and service wiring are centralized in `internal/container/container.go` via `BuildContainer` [internal/container/container.go:113-137](). This modularizes application construction and supports lifecycle management of components such as database clients, repositories, services, and handlers.

For in-depth coverage, see [Dependency Injection and Service Layer](#3.6).

Sources: [internal/container/container.go:33-137]()

### Multi-Tenant Role-Based Access Control (RBAC)

WeKnora implements security by enforcing tenant isolation and role-based access control at the middleware and domain handler layers. Tenant-aware service interfaces and handlers verify permissions on every request, configured via environment defaults and database state.

For security details, see [Security and Multi-Tenancy](#3.5).

Sources: [internal/config/config.go:19-43]()

### Asynchronous Task and Event-Driven Pipeline

Background processing for document parsing, enrichment, vector embedding, and chunk indexing utilizes an asynchronous task queue backed by Redis and the `hibiken/asynq` Go library [go.mod:32](). An event bus propagates domain events and supports extensible chat pipeline plugins and streaming response mechanisms.

For further elaboration, see [Event-Driven Architecture and Chat Pipeline](#3.7) and [Async Task Processing with Asynq](#11.2).

Sources: [.env.example:147-182](), [go.mod:32-32]()

---

## Component Layers Detailed Overview

- **HTTP Handler Layer**  
  WeKnora uses the Gin web framework (`github.com/gin-gonic/gin`) to implement HTTP routing, request validation, authentication enforcement, and response formatting [go.mod:23](). Handlers are defined under `internal/handler/` and include domain-specific subpackages [internal/container/container.go:77-88]().

- **Service Layer**  
  Application business logic resides here, handling session orchestration, RAG workflows, chat pipelines, agent execution, and skill management. These services coordinate with repositories and infrastructure components [internal/container/container.go:54-60]().

- **Repository Layer & Storage**  
  Data persistence abstracts over multiple backends:  
  - Relational: PostgreSQL accessed through GORM [internal/container/container.go:35-37]()  
  - Key-Value and caching: Redis [internal/container/container.go:32-32]()  
  - Vector Stores: Qdrant, Milvus, Weaviate, Tencent VectorDB, SQLite-Vec [internal/container/container.go:23-53]()  
  - Graph DB: Neo4j [internal/container/container.go:29-29]()  
  - Object Storage: MinIO, S3, COS, OSS  
  Retrieval engines are abstracted behind a common repository interface, allowing pluggable drivers [internal/container/container.go:43-53]().  
  For details, see [Storage and Database Layer](#3.4).

Sources: [internal/container/container.go:23-88](), [go.mod:23-23]()

---

## Bridging Natural Language Concepts to Code Entities

The following diagrams map abstract domain concepts to concrete code artifacts in the repository.

### From Natural Language System to Code Entities (High-Level)

```mermaid
graph TB
    NL_NaturalLanguageSpace["Natural Language Space"]
    KB_KnowledgeBase["Knowledge Base"]
    Chat_ChatSystem["Chat and Query System"]
    Agent_AgentSystem["Agent System"]
    Storage_StorageLayer["Storage and Database Layer"]
    Sec_Security["Security and Multi-Tenancy"]

    KB_KnowledgeBase -->|API routes & handlers| KBHandler["KnowledgeBaseHandler internal/handler/"]
    Chat_ChatSystem -->|Chat pipeline service| ChatPipeline["chatpipeline.EventManager internal/application/service/chat_pipeline/"]
    Agent_AgentSystem -->|Agent execution services| AgentService["Agent Services internal/agent/"]
    Storage_StorageLayer -->|Repo interfaces| KBRepo["knowledgeBaseRepository internal/application/repository/"]
    Storage_StorageLayer -->|Vector Store clients| VectorDB["Milvus / Qdrant Clients internal/container/container.go"]
    Sec_Security -->|Config and middleware| AuthConfig["TenantConfig internal/config/config.go"]
    
    NL_NaturalLanguageSpace --> KB_KnowledgeBase
    NL_NaturalLanguageSpace --> Chat_ChatSystem
    NL_NaturalLanguageSpace --> Agent_AgentSystem
    KB_KnowledgeBase --> Storage_StorageLayer
    Chat_ChatSystem --> Storage_StorageLayer
    Agent_AgentSystem --> Storage_StorageLayer
    Sec_Security --> Storage_StorageLayer
```

Sources: [internal/container/container.go:28-53](), [internal/config/config.go:19-25]()

### Mapping Service Names to Concrete Code Entities

```mermaid
graph LR
    App["WeKnora Application"]
    Router["Gin Router internal/router/"]
    Containers["Dependency Injection Container internal/container/container.go"]
    Handlers["HTTP Handlers internal/handler/"]
    Services["Application Services internal/application/service/"]
    Repository["Repositories internal/application/repository/"]
    Databases["Databases and Vector Stores internal/database/"]

    App --> Router
    Router --> Handlers
    Handlers --> Services
    Services --> Repository
    Repository --> Databases
    Containers -->|Provide wiring and config| Services
    Containers -->|Provide wiring and config| Repository
```

Sources: [internal/container/container.go:113-137](), [internal/database/databasemigration.go:1-1]()

---

## Further Reading

Explore detailed architecture and design in the related child pages:

- [Service Architecture and Container Orchestration](#3.1)
- [RAG Pipeline Architecture](#3.2)
- [Agent System and ReAct Engine](#3.3)
- [Storage and Database Layer](#3.4)
- [Security and Multi-Tenancy](#3.5)
- [Dependency Injection and Service Layer](#3.6)
- [Event-Driven Architecture and Chat Pipeline](#3.7)

---

## Summary

WeKnora's architecture bridges modern LLM-powered RAG concepts with well-established backend engineering practices:

- Modular layers spanning from frontend single-page applications to backend handlers, services, repositories, and multi-database persistence [internal/container/container.go:23-53]().
- Containerized microservices with profile configurations for optional auxiliary components [docker-compose.yml:1-67]().
- Robust multi-tenancy controls and asynchronous task processing pipelines.
- Dependency injection via `uber-go/dig` ensuring clean service separation and lifecycle management [internal/container/container.go:33-33]().

Sources: [internal/container/container.go:23-137](), [docker-compose.yml:1-67]()

---

