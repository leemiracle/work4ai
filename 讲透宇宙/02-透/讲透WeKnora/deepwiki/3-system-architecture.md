> 来源: [https://deepwiki.com/Tencent/WeKnora/3-system-architecture](https://deepwiki.com/Tencent/WeKnora/3-system-architecture)
> DeepWiki Tencent/WeKnora

# System Architecture

  Relevant source files 
 - [.env.example](https://github.com/Tencent/WeKnora/blob/10973ed3/.env.example)
 - [config/config.yaml](https://github.com/Tencent/WeKnora/blob/10973ed3/config/config.yaml)
 - [docker-compose.dev.yml](https://github.com/Tencent/WeKnora/blob/10973ed3/docker-compose.dev.yml)
 - [docker-compose.yml](https://github.com/Tencent/WeKnora/blob/10973ed3/docker-compose.yml)
 - [frontend/src/api/skill/index.ts](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/api/skill/index.ts)
 - [frontend/vite.config.ts](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/vite.config.ts)
 - [go.mod](https://github.com/Tencent/WeKnora/blob/10973ed3/go.mod)
 - [go.sum](https://github.com/Tencent/WeKnora/blob/10973ed3/go.sum)
 - [internal/config/config.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/config/config.go)
 - [internal/container/container.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/container/container.go)
 - [internal/handler/skill_handler.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/skill_handler.go)
 - [internal/types/retriever.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/retriever.go)
 - [scripts/dev.sh](https://github.com/Tencent/WeKnora/blob/10973ed3/scripts/dev.sh)
 
  
## Purpose and Scope

 This document provides a comprehensive overview of WeKnora's technical architecture, design patterns, and component interactions. It focuses on the high-level system structure, architectural decisions, and how major subsystems work together to turn documents into living knowledge.

 For detailed information about specific architectural layers and subsystems, see:

 
 - [Service Architecture and Container Orchestration](https://deepwiki.com/Tencent/WeKnora/3.1-service-architecture-and-container-orchestration) — Explain the microservices architecture, Docker Compose setup, service dependencies, and container communication.
 - [RAG Pipeline Architecture](https://deepwiki.com/Tencent/WeKnora/3.2-rag-pipeline-architecture) — Detail the RAG pipeline from document ingestion through chunking, embedding, indexing, to retrieval and generation.
 - [Agent System and ReAct Engine](https://deepwiki.com/Tencent/WeKnora/3.3-agent-system-and-react-engine) — Explain the agent execution model, ReAct pattern implementation, tool registry, and iterative reasoning.
 - [Storage and Database Layer](https://deepwiki.com/Tencent/WeKnora/3.4-storage-and-database-layer) — Document the multi-database architecture including PostgreSQL, Redis, vector stores, graph databases, and file storage options.
 - [Security and Multi-Tenancy](https://deepwiki.com/Tencent/WeKnora/3.5-security-and-multi-tenancy) — Explain tenant isolation, RBAC access control, organization sharing, SSRF protection, and security best practices.
 - [Dependency Injection and Service Layer](https://deepwiki.com/Tencent/WeKnora/3.6-dependency-injection-and-service-layer) — Document the dependency injection container, service registration, and layered architecture pattern.
 - [Event-Driven Architecture and Chat Pipeline](https://deepwiki.com/Tencent/WeKnora/3.7-event-driven-architecture-and-chat-pipeline) — Explain the event bus system, chat pipeline plugins, streaming architecture, and event types.
 
 Sources: [internal/container/container.go100-145](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/container/container.go#L100-L145) [docker-compose.yml1-35](https://github.com/Tencent/WeKnora/blob/10973ed3/docker-compose.yml#L1-L35)

 
---

 
## Architectural Overview

 WeKnora follows a **layered microservices-inspired architecture** deployed via Docker Compose (`docker-compose.yml`), enabling easy startup of various services and optional components with profile-based activation. The backend is written in Go, utilizing a clean architecture approach with clear separation between HTTP handlers (`handler`), application services (`service`), and repositories (`repository`) that interface with various databases. The frontend is a Vue.js Single Page Application (`frontend/src`).

 
### Application Layering and Code Entity Mapping

 The diagram below bridges the logical system layers to concrete code entities, helping engineers directly locate functionality in the source.

 **Code Entity Mapping Diagram**

 
```

```

 For details on the service layer and DI container, see [Dependency Injection and Service Layer](https://deepwiki.com/Tencent/WeKnora/3.6-dependency-injection-and-service-layer).

 Sources: [internal/container/container.go100-145](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/container/container.go#L100-L145) [internal/handler/skill_handler.go19-42](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/skill_handler.go#L19-L42)

 
---

 
### Deployment Architecture

 WeKnora adopts a containerized deployment model orchestrated by Docker Compose (`docker-compose.yml`), supporting flexible service topologies and optional infrastructure profiles.

 **Container Orchestration Diagram**

 
```

```

 For container orchestration details, profile selection, and communication topologies, see [Service Architecture and Container Orchestration](https://deepwiki.com/Tencent/WeKnora/3.1-service-architecture-and-container-orchestration).

 Sources: [docker-compose.yml1-150](https://github.com/Tencent/WeKnora/blob/10973ed3/docker-compose.yml#L1-L150) [docker-compose.dev.yml1-213](https://github.com/Tencent/WeKnora/blob/10973ed3/docker-compose.dev.yml#L1-L213)

 
---

 
## Core Architectural Patterns

 
### 1. Dependency Injection with uber-go/dig

 WeKnora uses `uber-go/dig` within `internal/container/container.go` to wire application components cleanly [internal/container/container.go100-145](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/container/container.go#L100-L145) For comprehensive documentation on the DI container, service registration, and lifecycle management, see [Dependency Injection and Service Layer](https://deepwiki.com/Tencent/WeKnora/3.6-dependency-injection-and-service-layer).

 Sources: [internal/container/container.go100-145](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/container/container.go#L100-L145)

 
### 2. Multi-Tenant Role-Based Access Control (RBAC)

 The security subsystem enforces tenant isolation and role-based permissions (`owner`, `admin`, `contributor`, `viewer`) via middleware and domain handlers [internal/config/config.go110-114](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/config/config.go#L110-L114) For details on tenant isolation and security practices, see [Security and Multi-Tenancy](https://deepwiki.com/Tencent/WeKnora/3.5-security-and-multi-tenancy).

 Sources: [internal/config/config.go110-114](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/config/config.go#L110-L114)

 
### 3. Asynchronous Tasks and Event-Driven Pipelines

 Task processing leverages `hibiken/asynq` backed by Redis for document ingestion, background chunking, and enrichment tasks [go.mod32](https://github.com/Tencent/WeKnora/blob/10973ed3/go.mod#L32-L32) [.env.example145-185](https://github.com/Tencent/WeKnora/blob/10973ed3/.env.example#L145-L185) For details on the event bus, chat pipeline plugins, and streaming architecture, see [Event-Driven Architecture and Chat Pipeline](https://deepwiki.com/Tencent/WeKnora/3.7-event-driven-architecture-and-chat-pipeline) and [Async Task Processing with Asynq](https://deepwiki.com/Tencent/WeKnora/11.2-async-task-processing-with-asynq).

 Sources: [go.mod32](https://github.com/Tencent/WeKnora/blob/10973ed3/go.mod#L32-L32) [.env.example145-185](https://github.com/Tencent/WeKnora/blob/10973ed3/.env.example#L145-L185)

 
---

 
## Component Layers Detailed Overview

 
 - **HTTP Handler Layer**: Implemented using Gin (`github.com/gin-gonic/gin`) [go.mod23](https://github.com/Tencent/WeKnora/blob/10973ed3/go.mod#L23-L23) handling routing, request validation, authentication extraction, and response formatting [internal/container/container.go100-145](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/container/container.go#L100-L145)
 - **Service Layer**: Houses core application business logic, session orchestration, RAG processing flows, agent reasoning loops, and skill management [internal/container/container.go49-53](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/container/container.go#L49-L53) [internal/handler/skill_handler.go19-33](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/skill_handler.go#L19-L33)
 - **Repository Layer & Storage**: Abstracts data persistence across relational stores (`gorm.io/gorm`), vector retrieval engines (`types.RetrieverEngineType`), graph stores, and object storage providers [internal/container/container.go32-48](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/container/container.go#L32-L48) [internal/types/retriever.go3-27](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/retriever.go#L3-L27) For deep storage details, see [Storage and Database Layer](https://deepwiki.com/Tencent/WeKnora/3.4-storage-and-database-layer).
 
 Sources: [internal/container/container.go32-53](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/container/container.go#L32-L53) [internal/types/retriever.go3-27](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/retriever.go#L3-L27) [internal/handler/skill_handler.go19-33](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/skill_handler.go#L19-L33)
