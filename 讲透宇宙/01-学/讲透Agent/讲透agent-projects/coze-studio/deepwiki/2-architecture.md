<!-- source: DeepWiki mcp.deepwiki.com · repo coze-dev/coze-studio · page 2 Architecture · fetched 2026-10-29 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/CODEOWNERS](.github/CODEOWNERS)
- [README.md](README.md)
- [backend/api/model/base/base.go](backend/api/model/base/base.go)

</details>



This document provides a high-level architectural overview of the Coze Studio monorepo, describing the major subsystems, their responsibilities, and how they interact. It covers the frontend's layered package architecture, the DDD-based backend microservices, the Thrift-based Interface Definition Layer (IDL), and the containerized infrastructure.

For specific implementation details about individual subsystems, see [Frontend Architecture](#2.1), [Backend Architecture](#2.2), [Infrastructure Stack](#2.3), [Interface Definition Layer](#2.4), and [Plugin and Extension System](#2.5).

## System Overview

Coze Studio is structured as a monorepo with distinct architectural layers. The backend is developed using **Golang** (utilizing the **Hertz** HTTP framework and **Eino** AI orchestration framework), while the frontend employs **React 18** with **TypeScript** managed by **Rush.js** for monorepo dependency control. The overall architecture follows **Domain-Driven Design (DDD)** principles to handle complex business domains such as AI agents, workflows, plugins, knowledge bases, and databases.

**High-Level System Topology**

```mermaid
graph TB
    subgraph "Frontend Layer (React/TypeScript)"
        FE_App["frontend/apps/coze-studio/"]
        FE_IDE["Agent IDE & Project IDE<br/>(packages/agent-ide, packages/project-ide)"]
        FE_Core["Core Systems<br/>(workflow, studio, data)"]
        FE_Arch["Architecture/Foundation<br/>(bot-api, bot-http, arch packages)"]
    end

    subgraph "IDL Layer (Thrift)"
        ThriftIDL["idl/*.thrift files<br/>(API Contracts & Data Types)"]
    end

    subgraph "Backend Layer (Go/DDD Architecture)"
        BE_API["backend/api/<br/>(HTTP handlers, middleware, models)"]
        BE_App["backend/application/<br/>(Use Cases)"]
        BE_Domain["backend/domain/<br/>(Business Logic, Entities, Eino AI Framework)"]
        BE_Infra["backend/infra/<br/>(Adapters: DB, Cache, VectorStore, etc.)"]
        BE_Pkg["backend/pkg/<br/>(Utilities)"]
        BE_Types["backend/types/"]
    end

    subgraph "Infrastructure Layer"
        DB["MySQL / Relational DB"]
        Cache["Redis / Cache Layer"]
        VectorStore["Milvus / OceanBase / Vector Search"]
        Storage["MinIO / S3 Object Storage"]
        MQ["NSQ / RocketMQ / NATS / Pulsar Messaging Queues"]
        Proxy["Nginx / Reverse Proxy"]
    end

    FE_App --> FE_IDE
    FE_IDE --> FE_Core
    FE_Core --> FE_Arch

    FE_Arch -.->| "idl2ts-generated API Types" | ThriftIDL
    ThriftIDL -.->| "kitex Go Stubs" | BE_API

    FE_Arch -.->| "HTTP/SSE calls" | BE_API
    BE_API --> BE_App
    BE_App --> BE_Domain
    BE_Domain --> BE_Infra

    BE_Infra --> DB
    BE_Infra --> Cache
    BE_Infra --> VectorStore
    BE_Infra --> Storage
    BE_Infra --> MQ

    BE_API --> Proxy
    FE_App --> Proxy
```

This diagram connects the natural language "system parts" (like "Agent IDE" or "MySQL") with their concrete code entities and directories, showing how each layer depends on or interacts with others.

**Sources:** [README.md:27-28](), [.github/CODEOWNERS:1-280]()

---

## Frontend Architecture

The frontend is organized into multiple layers to promote code reuse and maintainability:

- **Layer 1 (Apps):** The top-level application entrypoint(s) live in `frontend/apps/coze-studio/`.
- **Layer 2 (IDEs & Feature Packages):** Packages like `agent-ide` and `project-ide` provide integrated development environments for building and managing AI agents and projects.
- **Layer 3 (Core Systems):** Packages responsible for core business logic such as `workflow`, `studio`, and `data`.
- **Layer 4 (Foundation & Common Utilities):** Provides shared foundational services (e.g., state stores, account management).
- **Layer 5 (Architecture Layer):** Contains low-level utilities and API client layers (`bot-api`, `bot-http`, `idl`, `i18n`, etc.).

The frontend heavily employs the **Adapter Pattern** with packages named `*-adapter`, `*-base`, and `*-interface` to provide flexibility and pluggable implementations.

This layered dependency structure is managed by **Rush.js** enforcing trust boundaries and a strict "dependency tier" system from level-1 (apps) down to level-4 (core arch libraries). Teams maintain ownership of package sets grouped by these tiers.

For full details, see [Frontend Architecture](#2.1).

**Sources:** [.github/CODEOWNERS:3-150](), [README.md:27-28]()

---

## Backend Architecture

The backend is a Go-based microservice system structured following **Domain-Driven Design (DDD)** principles, enabling separation of concerns and clean layering.

- **API Layer (`backend/api/`):** Contains HTTP request handlers, middlewares, router definitions, and Thrift-generated models. Uses the **Hertz** HTTP framework for high-performance networking and provides uniform error handling utilities (e.g., `BadRequest`, `InternalError`).

- **Application Layer (`backend/application/`):** Implements use cases spanning multiple domain services such as agent running, workflow execution, knowledge querying, memory management, and plugin support.

- **Domain Layer (`backend/domain/`):** Pure business logic entities and domain services. Includes modules like `agent` (single agent execution), `conversation`, `knowledge`, `memory`, `plugin`, `workflow`, and cross-domain concerns. The **Eino** AI orchestration framework is integrated here to manage AI model chains and workflows.

- **Infrastructure Layer (`backend/infra/`):** Implements external adapter services such as GORM relational database access, Redis caching, vector stores (Milvus/OceanBase), event buses (NSQ/RocketMQ/NATS/Pulsar), object storage (MinIO/S3), document parsing, and embedding services (OpenAI, Volcengine, Ollama).

- **Utility Packages (`backend/pkg/`, `backend/types/`):** Provide reusable components and type definitions.

For full details, see [Backend Architecture](#2.2).

**Sources:** [backend/api/model/base/base.go:10-60](), [README.md:27-28]()

---

## Interface Definition Layer (IDL)

To enforce consistent API contracts between frontend and backend, Coze Studio uses **Apache Thrift** as an Interface Definition Language (IDL).

- Contract definitions reside in the `idl/` directory, including base types (`base.thrift`), API interfaces (`api.thrift`), and domain-specific thrift files.

- Backend Go code is generated using the **kitex** toolchain, producing tightly coupled service stubs and data models used in the `backend/api/` layer.

- Frontend TypeScript interfaces are generated via `idl2ts`, enabling type-safe API consumption within packages like `bot-api` and `bot-http`.

This shared IDL ensures synchronized data structures and RPC contracts across the system.

For full details, see [Interface Definition Layer](#2.4).

**Sources:** [backend/api/model/base/base.go:1-191](), [.github/CODEOWNERS:26]()

---

## Infrastructure Stack

Coze Studio is designed for cloud-native deployment using containerization and orchestration:

- **Docker Compose** provides a ready-to-run local development topology including services for `coze-server` (backend), `coze-web` (frontend with Nginx), MySQL, Redis, Elasticsearch, MinIO, Milvus, etcd, and messaging brokers (NSQ, RocketMQ, NATS, or Pulsar).

- **Kubernetes** deployment is orchestrated via Helm charts located in `helm/charts/opencoze/`, enabling scalable production environments with configurable storage classes, service types, and external integrations like OceanBase.

- Essential infrastructure services:
  - **MySQL:** Main relational database with migrations managed via Atlas.
  - **Redis:** Distributed cache layer.
  - **Elasticsearch:** Full-text search engine supporting the knowledge base.
  - **MinIO:** S3-compatible object storage.
  - **Milvus/OceanBase:** Vector search stores for AI embeddings.
  - **NSQ/RocketMQ/NATS/Pulsar:** Event bus messaging frameworks handling asynchronous processing.
  - **Nginx:** Reverse proxy to route frontend and backend HTTP traffic.

For full details, see [Infrastructure Stack](#2.3).

**Sources:** [README.md:41-68](), [.github/CODEOWNERS:275-277]()

---

## Plugin and Extension System

Coze Studio supports a modular plugin architecture enabling flexible extension of agent capabilities and workflows:

- **Backend Plugins:** Managed as a domain inside `backend/domain/plugin`, supporting OAuth authentication with AES-encrypted tokens and runtime execution integration.

- **Frontend Plugins:** Implemented within the `agent-ide` and `studio` packages using the adapter pattern (`bot-plugin`, `plugin-modal-adapter`), enabling dynamic loading, configuration, and store management of plugins.

- **Workflow Integration:** Plugins can define custom nodes or actions invocable within visual workflows.

This plugin system supports community-driven extensions and customization of AI agent logic.

For full details, see [Plugin and Extension System](#2.5).

**Sources:** [.github/CODEOWNERS:161-183](), [README.md:35]()

---

This architecture page summarizes how the multiple layers and subsystems work together to provide a cohesive platform for building, running, and extending conversational AI applications using Coze Studio.

For deeper dives into each subsystem, consult the linked child pages:
- [Frontend Architecture](#2.1)
- [Backend Architecture](#2.2)
- [Infrastructure Stack](#2.3)
- [Interface Definition Layer](#2.4)
- [Plugin and Extension System](#2.5)

---

