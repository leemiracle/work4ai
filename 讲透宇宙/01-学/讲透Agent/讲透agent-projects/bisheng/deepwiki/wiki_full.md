# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docker/bisheng-ft/config.yaml](docker/bisheng-ft/config.yaml)
- [docker/bisheng-uns/config.yaml](docker/bisheng-uns/config.yaml)
- [docker/bisheng/config/config.yaml](docker/bisheng/config/config.yaml)
- [docker/docker-compose-ft.yml](docker/docker-compose-ft.yml)
- [docker/docker-compose-office.yml](docker/docker-compose-office.yml)
- [docker/docker-compose-uns.yml](docker/docker-compose-uns.yml)
- [docker/docker-compose.yml](docker/docker-compose.yml)
- [docker/mysql/conf/my.cnf](docker/mysql/conf/my.cnf)
- [docker/nginx/nginx.conf](docker/nginx/nginx.conf)
- [src/backend/bisheng/__init__.py](src/backend/bisheng/__init__.py)
- [src/backend/bisheng/api/services/assistant.py](src/backend/bisheng/api/services/assistant.py)
- [src/backend/bisheng/api/services/flow.py](src/backend/bisheng/api/services/flow.py)
- [src/backend/bisheng/api/services/workflow.py](src/backend/bisheng/api/services/workflow.py)
- [src/backend/bisheng/api/utils.py](src/backend/bisheng/api/utils.py)
- [src/backend/bisheng/api/v1/assistant.py](src/backend/bisheng/api/v1/assistant.py)
- [src/backend/bisheng/api/v1/endpoints.py](src/backend/bisheng/api/v1/endpoints.py)
- [src/backend/bisheng/api/v1/flows.py](src/backend/bisheng/api/v1/flows.py)
- [src/backend/bisheng/api/v1/schemas.py](src/backend/bisheng/api/v1/schemas.py)
- [src/backend/bisheng/api/v1/skillcenter.py](src/backend/bisheng/api/v1/skillcenter.py)
- [src/backend/bisheng/api/v1/workflow.py](src/backend/bisheng/api/v1/workflow.py)
- [src/backend/bisheng/database/base.py](src/backend/bisheng/database/base.py)
- [src/backend/bisheng/database/models/assistant.py](src/backend/bisheng/database/models/assistant.py)
- [src/backend/bisheng/database/models/flow.py](src/backend/bisheng/database/models/flow.py)
- [src/backend/bisheng/database/models/flow_version.py](src/backend/bisheng/database/models/flow_version.py)
- [src/backend/bisheng/database/models/template.py](src/backend/bisheng/database/models/template.py)
- [src/backend/bisheng/database/models/user_link.py](src/backend/bisheng/database/models/user_link.py)
- [src/backend/bisheng/graph/vertex/base.py](src/backend/bisheng/graph/vertex/base.py)
- [src/backend/bisheng/initdb_config.yaml](src/backend/bisheng/initdb_config.yaml)
- [src/backend/bisheng/interface/chains/base.py](src/backend/bisheng/interface/chains/base.py)
- [src/backend/bisheng/interface/chains/custom.py](src/backend/bisheng/interface/chains/custom.py)
- [src/backend/bisheng/interface/initialize/loading.py](src/backend/bisheng/interface/initialize/loading.py)
- [src/backend/bisheng/main.py](src/backend/bisheng/main.py)
- [src/backend/bisheng/template/frontend_node/chains.py](src/backend/bisheng/template/frontend_node/chains.py)
- [src/backend/bisheng/template/frontend_node/wrappers.py](src/backend/bisheng/template/frontend_node/wrappers.py)
- [src/backend/pyproject.toml](src/backend/pyproject.toml)
- [update.sh](update.sh)

</details>



## Purpose and Scope

Bisheng is a comprehensive AI application development platform that enables users to build, deploy, and manage AI-powered applications. The platform provides integrated subsystems for knowledge base management, conversational AI assistants, visual workflow orchestration, and document-centric task automation. This document provides a high-level overview of the entire Bisheng system architecture, core components, and deployment model.

For detailed information about specific subsystems, see:
- Knowledge base processing: [Knowledge Base Management](#3.1)
- Chat and assistant execution: [Chat and Messaging System](#3.2), [Assistant System](#3.3)
- Workflow automation: [Workflow Engine](#3.5), [Linsight AI Workbench](#3.4)
- Access control and permissions: [User and Access Control](#4)
- Deployment configurations: [Development and Deployment](#5)

## System Architecture

Bisheng implements a three-tier architecture consisting of a React/TypeScript frontend, FastAPI backend services, and a multi-database storage layer. The system supports multiple AI application paradigms including skills (flows), assistants, and workflows.

### High-Level Component Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        WEB["React Frontend<br/>Port 3001"]
    end
    
    subgraph "API Layer - bisheng.main:app"
        FASTAPI["FastAPI Application<br/>Port 7860<br/>bisheng/main.py"]
        ROUTER["API Router<br/>bisheng/api/router.py"]
        V1["v1 Endpoints"]
        V2["v2 Endpoints"]
    end
    
    subgraph "Service Layer"
        ASSISTANT_SVC["AssistantService<br/>bisheng/api/services/assistant.py"]
        FLOW_SVC["FlowService<br/>bisheng/api/services/flow.py"]
        WORKFLOW_SVC["WorkFlowService<br/>bisheng/api/services/workflow.py"]
        KNOWLEDGE_SVC["KnowledgeService"]
    end
    
    subgraph "Execution Layer"
        CHAT_MGR["ChatManager<br/>bisheng/chat/manager.py"]
        ASSISTANT_AGENT["AssistantAgent<br/>bisheng/api/services/assistant_agent.py"]
        WORKFLOW_ENGINE["Workflow<br/>bisheng/workflow/graph/workflow.py"]
        GRAPH["Graph<br/>bisheng/graph/graph/base.py"]
    end
    
    subgraph "Data Access Layer - DAOs"
        FLOW_DAO["FlowDao<br/>bisheng/database/models/flow.py"]
        ASSISTANT_DAO["AssistantDao<br/>bisheng/database/models/assistant.py"]
        KNOWLEDGE_DAO["KnowledgeDao"]
        MESSAGE_DAO["ChatMessageDao"]
    end
    
    subgraph "Storage Layer"
        MYSQL["MySQL<br/>Port 3306"]
        REDIS["Redis<br/>Port 6379"]
        MILVUS["Milvus<br/>Port 19530"]
        ES["Elasticsearch<br/>Port 9200"]
        MINIO["MinIO<br/>Port 9000"]
    end
    
    WEB --> FASTAPI
    FASTAPI --> ROUTER
    ROUTER --> V1
    ROUTER --> V2
    
    V1 --> ASSISTANT_SVC
    V1 --> FLOW_SVC
    V1 --> WORKFLOW_SVC
    V1 --> KNOWLEDGE_SVC
    
    ASSISTANT_SVC --> ASSISTANT_AGENT
    FLOW_SVC --> GRAPH
    WORKFLOW_SVC --> WORKFLOW_ENGINE
    
    ASSISTANT_AGENT --> CHAT_MGR
    WORKFLOW_ENGINE --> CHAT_MGR
    
    ASSISTANT_SVC --> ASSISTANT_DAO
    FLOW_SVC --> FLOW_DAO
    KNOWLEDGE_SVC --> KNOWLEDGE_DAO
    CHAT_MGR --> MESSAGE_DAO
    
    FLOW_DAO --> MYSQL
    ASSISTANT_DAO --> MYSQL
    KNOWLEDGE_DAO --> MYSQL
    MESSAGE_DAO --> MYSQL
    
    CHAT_MGR --> REDIS
    KNOWLEDGE_DAO --> MILVUS
    KNOWLEDGE_DAO --> ES
    KNOWLEDGE_DAO --> MINIO
```

**Sources:** [src/backend/bisheng/main.py:64-102](), [src/backend/bisheng/api/services/assistant.py:1-516](), [src/backend/bisheng/api/services/flow.py:1-445](), [src/backend/bisheng/api/services/workflow.py:1-451](), [src/backend/bisheng/database/models/flow.py:1-550](), [src/backend/bisheng/database/models/assistant.py:1-300]()

## Core Application Types

Bisheng supports three primary application types, each with distinct execution models and use cases. The `FlowType` enum defines these types in the data model.

### Application Type Definitions

```mermaid
graph LR
    subgraph "FlowType Enum"
        FLOW_TYPE["FlowType<br/>bisheng/database/models/flow.py:31-36"]
    end
    
    subgraph "Application Types"
        FLOW["FLOW = 1<br/>Skills/Chains<br/>LangChain-based"]
        ASSISTANT["ASSISTANT = 5<br/>AI Assistants<br/>Agent-based"]
        WORKFLOW["WORKFLOW = 10<br/>Visual Workflows<br/>Node-graph based"]
        LINSIGHT["LINSIGHT = 20<br/>Document Automation<br/>Task-based"]
    end
    
    FLOW_TYPE --> FLOW
    FLOW_TYPE --> ASSISTANT
    FLOW_TYPE --> WORKFLOW
    FLOW_TYPE --> LINSIGHT
    
    FLOW --> GRAPH_BUILD["Graph.from_payload()<br/>bisheng/graph/graph/base.py"]
    ASSISTANT --> AGENT_INIT["AssistantAgent<br/>bisheng/api/services/assistant_agent.py"]
    WORKFLOW --> WORKFLOW_CLASS["Workflow()<br/>bisheng/workflow/graph/workflow.py"]
    LINSIGHT --> LINSIGHT_TASK["LinsightWorkflowTask<br/>bisheng/linsight/workflow/task.py"]
```

**Sources:** [src/backend/bisheng/database/models/flow.py:31-36](), [src/backend/bisheng/api/services/assistant.py:39-516](), [src/backend/bisheng/api/services/workflow.py:35-451]()

## Request Flow Architecture

The following diagram illustrates how user requests flow through the system, from API endpoints to execution engines and data persistence.

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI as "FastAPI App<br/>bisheng/main.py"
    participant Router as "API Router<br/>bisheng/api/v1/"
    participant Service as "Service Layer<br/>*Service classes"
    participant DAO as "DAO Layer<br/>*Dao classes"
    participant Executor as "Execution Engine<br/>AssistantAgent/Workflow/Graph"
    participant DB as "MySQL"
    participant Cache as "Redis"
    
    Client->>FastAPI: HTTP/WebSocket Request
    FastAPI->>Router: Route to endpoint
    
    alt Assistant Request
        Router->>Service: AssistantService method
        Service->>DAO: AssistantDao query
        DAO->>DB: SELECT from assistant
        DB-->>DAO: Assistant record
        DAO-->>Service: Assistant object
        Service->>Executor: AssistantAgent.init_assistant()
        Executor->>Cache: Session state
        Executor-->>Service: Agent ready
        Service-->>Client: Response/Stream
    else Workflow Request
        Router->>Service: WorkFlowService method
        Service->>DAO: FlowDao query
        DAO->>DB: SELECT from flow
        DB-->>DAO: Flow record
        DAO-->>Service: Flow object
        Service->>Executor: Workflow(flow_id, data)
        Executor->>Cache: Graph state
        Executor-->>Service: Workflow ready
        Service-->>Client: Response/Stream
    else Flow/Skill Request
        Router->>Service: FlowService method
        Service->>DAO: FlowDao query
        DAO->>DB: SELECT from flow
        DB-->>DAO: Flow record
        DAO-->>Service: Flow object
        Service->>Executor: Graph.from_payload()
        Executor->>Cache: Build cache
        Executor-->>Service: Graph built
        Service-->>Client: Response/Stream
    end
```

**Sources:** [src/backend/bisheng/main.py:64-102](), [src/backend/bisheng/api/v1/assistant.py:1-177](), [src/backend/bisheng/api/v1/workflow.py:1-312](), [src/backend/bisheng/api/v1/flows.py:1-226](), [src/backend/bisheng/api/services/assistant.py:39-516](), [src/backend/bisheng/api/services/workflow.py:35-451](), [src/backend/bisheng/api/services/flow.py:38-445]()

## Technology Stack

| Layer | Technology | Configuration |
|-------|-----------|---------------|
| **Frontend** | React 18, TypeScript, Vite | Port 3001 |
| **Backend API** | FastAPI 0.120.4+, Python 3.10+ | Port 7860 |
| **Relational DB** | MySQL 8.0 | Port 3306, database: `bisheng` |
| **Cache/Queue** | Redis 7.0.4 | Port 6379, databases: 0, 1, 2 |
| **Vector Store** | Milvus 2.5.10, pymilvus 2.5.10 | Port 19530 |
| **Full-text Search** | Elasticsearch 8.12.0 | Port 9200 |
| **Object Storage** | MinIO | Port 9000 (API), 9001 (Console) |
| **Coordination** | ETCD 3.5.5 | For Milvus metadata |
| **LLM Framework** | LangChain 0.3.23+, LangGraph 0.3.27+ | |
| **Async Workers** | Celery 5.5.3+ | Redis broker at db 2 |

**Sources:** [src/backend/pyproject.toml:1-87](), [docker/docker-compose.yml:1-201](), [docker/bisheng/config/config.yaml:1-88]()

## Database Configuration

The system uses environment-based configuration with encrypted credentials. The `database_url` and `redis_url` settings support password encryption using the platform's encryption utilities.

```mermaid
graph TB
    subgraph "Configuration Files"
        CONFIG_YAML["config.yaml<br/>docker/bisheng/config/config.yaml"]
        INITDB_YAML["initdb_config.yaml<br/>src/backend/bisheng/initdb_config.yaml"]
    end
    
    subgraph "Database URLs"
        MYSQL_URL["database_url<br/>mysql+pymysql://root:****@mysql:3306/bisheng"]
        REDIS_URL["redis_url<br/>redis://redis:6379/1"]
        CELERY_REDIS["celery_redis_url<br/>redis://redis:6379/2"]
    end
    
    subgraph "Environment Variables"
        BS_MILVUS["BS_MILVUS_CONNECTION_ARGS"]
        BS_ES["BS_ELASTICSEARCH_URL"]
        BS_MINIO["BS_MINIO_*"]
    end
    
    CONFIG_YAML --> MYSQL_URL
    CONFIG_YAML --> REDIS_URL
    CONFIG_YAML --> CELERY_REDIS
    CONFIG_YAML --> BS_MILVUS
    CONFIG_YAML --> BS_ES
    CONFIG_YAML --> BS_MINIO
    
    INITDB_YAML --> SYSTEM_SETTINGS["System Settings<br/>Stored in config table"]
```

**Sources:** [docker/bisheng/config/config.yaml:1-88](), [src/backend/bisheng/initdb_config.yaml:1-81]()

## API Routing Structure

The FastAPI application organizes endpoints into versioned routers with specific functional domains.

### API Endpoint Organization

```mermaid
graph TB
    subgraph "bisheng/api/router.py"
        MAIN_ROUTER["Main API Router"]
    end
    
    subgraph "v1 Endpoints"
        ENDPOINTS["/api/v1/endpoints.py<br/>/all, /env, /process"]
        FLOWS["/api/v1/flows.py<br/>/flows/*"]
        ASSISTANT["/api/v1/assistant.py<br/>/assistant/*"]
        WORKFLOW["/api/v1/workflow.py<br/>/workflow/*"]
        CHAT["/api/v1/chat.py<br/>/chat/*"]
        KNOWLEDGE["/api/v1/knowledge.py<br/>/knowledge/*"]
        SKILL["/api/v1/skillcenter.py<br/>/skill/*"]
    end
    
    subgraph "Key Routes"
        ASSISTANT_CHAT["WS: /assistant/chat/{assistant_id}"]
        WORKFLOW_CHAT["WS: /workflow/chat/{workflow_id}"]
        PROCESS_FLOW["POST: /process<br/>Legacy flow execution"]
        FLOW_CRUD["GET/POST/PATCH/DELETE: /flows/{flow_id}"]
    end
    
    MAIN_ROUTER --> ENDPOINTS
    MAIN_ROUTER --> FLOWS
    MAIN_ROUTER --> ASSISTANT
    MAIN_ROUTER --> WORKFLOW
    MAIN_ROUTER --> CHAT
    MAIN_ROUTER --> KNOWLEDGE
    MAIN_ROUTER --> SKILL
    
    ASSISTANT --> ASSISTANT_CHAT
    WORKFLOW --> WORKFLOW_CHAT
    ENDPOINTS --> PROCESS_FLOW
    FLOWS --> FLOW_CRUD
```

**Sources:** [src/backend/bisheng/api/v1/endpoints.py:1-428](), [src/backend/bisheng/api/v1/flows.py:1-226](), [src/backend/bisheng/api/v1/assistant.py:1-177](), [src/backend/bisheng/api/v1/workflow.py:1-312]()

## Version Information

The platform version is defined in multiple locations and kept synchronized via build scripts:

- Current version: `2.4.0-beta1`
- Version files: [src/backend/bisheng/__init__.py:10](), [src/backend/pyproject.toml:3](), [update.sh:3-7]()
- Docker images: `dataelement/bisheng-backend:v2.4.0-beta1`, `dataelement/bisheng-frontend:v2.4.0-beta1`

**Sources:** [src/backend/bisheng/__init__.py:1-17](), [src/backend/pyproject.toml:1-87](), [update.sh:1-8]()

## Deployment Model

Bisheng uses Docker Compose for orchestration with a modular service architecture. The base deployment includes 8 required services plus 3 optional services.

### Docker Compose Service Architecture

```mermaid
graph TB
    subgraph "Core Services - docker-compose.yml"
        BACKEND["bisheng-backend<br/>FastAPI + API"]
        WORKER["bisheng-backend-worker<br/>Celery Workers"]
        FRONTEND["bisheng-frontend<br/>Nginx + React"]
        MYSQL_C["bisheng-mysql<br/>MySQL 8.0"]
        REDIS_C["bisheng-redis<br/>Redis 7.0.4"]
        MILVUS_C["bisheng-milvus-standalone<br/>Milvus 2.5.10"]
        ES_C["bisheng-es<br/>Elasticsearch 8.12.0"]
        MINIO_C["bisheng-milvus-minio<br/>MinIO"]
        ETCD_C["bisheng-milvus-etcd<br/>ETCD 3.5.5"]
    end
    
    subgraph "Optional Services"
        UNS["bisheng-unstructured<br/>docker-compose-uns.yml<br/>Document Processing"]
        FT["bisheng-ft-server<br/>docker-compose-ft.yml<br/>Fine-tuning"]
        OFFICE["bisheng-office<br/>docker-compose-office.yml<br/>OnlyOffice 7.1.1"]
    end
    
    BACKEND --> MYSQL_C
    BACKEND --> REDIS_C
    BACKEND --> MILVUS_C
    BACKEND --> ES_C
    BACKEND --> MINIO_C
    
    WORKER --> MYSQL_C
    WORKER --> REDIS_C
    
    FRONTEND --> BACKEND
    
    MILVUS_C --> ETCD_C
    MILVUS_C --> MINIO_C
    
    BACKEND -.optional.-> UNS
    BACKEND -.optional.-> FT
    BACKEND -.optional.-> OFFICE
```

**Sources:** [docker/docker-compose.yml:1-201](), [docker/docker-compose-uns.yml:1-22](), [docker/docker-compose-ft.yml:1-31](), [docker/docker-compose-office.yml:1-15]()

## Initialization and Lifecycle

The FastAPI application uses an async lifespan context manager to handle startup and shutdown tasks. Key initialization steps include database setup, service initialization, and default data population.

### Application Lifecycle

```mermaid
sequenceDiagram
    participant Main as "main.py"
    participant App as "FastAPI App"
    participant Context as "initialize_app_context()"
    participant Services as "initialize_services()"
    participant InitData as "init_default_data()"
    participant DB as "Database"
    
    Main->>App: create_app()
    App->>App: lifespan() context
    activate App
    
    App->>Context: Initialize context
    Context->>DB: Setup connections
    DB-->>Context: Ready
    
    App->>Services: Initialize services
    Services->>Services: Setup task service
    Services->>Services: Setup session service
    
    App->>InitData: Create defaults
    InitData->>DB: Insert default users/groups
    InitData->>DB: Insert system configs
    DB-->>InitData: Complete
    
    Note over App: Application running...
    
    App->>Services: teardown_services()
    App->>Context: close_app_context()
    deactivate App
```

**Sources:** [src/backend/bisheng/main.py:52-62](), [src/backend/bisheng/main.py:64-102]()

## Summary

Bisheng is a production-ready AI application platform built with modern Python web frameworks and supporting multiple AI application paradigms. The architecture emphasizes modularity through service-oriented design, type safety through SQLModel and Pydantic, and scalability through distributed task processing with Celery. The platform's multi-database approach leverages specialized storage systems (MySQL for relational data, Milvus for vectors, Elasticsearch for search, Redis for caching) to optimize different access patterns.

For implementation details of specific subsystems, refer to the dedicated pages in sections 2 through 6 of this wiki.

**Sources:** [src/backend/bisheng/main.py:1-113](), [src/backend/pyproject.toml:1-87](), [docker/docker-compose.yml:1-201](), [src/backend/bisheng/database/models/flow.py:1-550](), [src/backend/bisheng/database/models/assistant.py:1-300](), [src/backend/bisheng/api/services/assistant.py:1-516](), [src/backend/bisheng/api/services/workflow.py:1-451]()

---

# Page: System Architecture

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docker/bisheng-ft/config.yaml](docker/bisheng-ft/config.yaml)
- [docker/bisheng-uns/config.yaml](docker/bisheng-uns/config.yaml)
- [docker/docker-compose-ft.yml](docker/docker-compose-ft.yml)
- [docker/docker-compose-office.yml](docker/docker-compose-office.yml)
- [docker/docker-compose-uns.yml](docker/docker-compose-uns.yml)
- [docker/docker-compose.yml](docker/docker-compose.yml)
- [docker/mysql/conf/my.cnf](docker/mysql/conf/my.cnf)
- [docker/nginx/nginx.conf](docker/nginx/nginx.conf)
- [src/backend/bisheng/__init__.py](src/backend/bisheng/__init__.py)
- [src/backend/bisheng/api/services/assistant.py](src/backend/bisheng/api/services/assistant.py)
- [src/backend/bisheng/api/services/flow.py](src/backend/bisheng/api/services/flow.py)
- [src/backend/bisheng/api/services/knowledge.py](src/backend/bisheng/api/services/knowledge.py)
- [src/backend/bisheng/api/services/knowledge_imp.py](src/backend/bisheng/api/services/knowledge_imp.py)
- [src/backend/bisheng/api/services/workflow.py](src/backend/bisheng/api/services/workflow.py)
- [src/backend/bisheng/api/v1/assistant.py](src/backend/bisheng/api/v1/assistant.py)
- [src/backend/bisheng/api/v1/flows.py](src/backend/bisheng/api/v1/flows.py)
- [src/backend/bisheng/api/v1/schemas.py](src/backend/bisheng/api/v1/schemas.py)
- [src/backend/bisheng/api/v1/skillcenter.py](src/backend/bisheng/api/v1/skillcenter.py)
- [src/backend/bisheng/api/v1/workflow.py](src/backend/bisheng/api/v1/workflow.py)
- [src/backend/bisheng/database/models/assistant.py](src/backend/bisheng/database/models/assistant.py)
- [src/backend/bisheng/database/models/flow.py](src/backend/bisheng/database/models/flow.py)
- [src/backend/bisheng/database/models/flow_version.py](src/backend/bisheng/database/models/flow_version.py)
- [src/backend/bisheng/database/models/template.py](src/backend/bisheng/database/models/template.py)
- [src/backend/bisheng/database/models/user_link.py](src/backend/bisheng/database/models/user_link.py)
- [src/backend/bisheng/template/frontend_node/wrappers.py](src/backend/bisheng/template/frontend_node/wrappers.py)
- [src/backend/bisheng/worker/knowledge/file_worker.py](src/backend/bisheng/worker/knowledge/file_worker.py)
- [src/backend/bisheng/worker/knowledge/qa.py](src/backend/bisheng/worker/knowledge/qa.py)
- [src/backend/bisheng/worker/knowledge/rebuild_knowledge_worker.py](src/backend/bisheng/worker/knowledge/rebuild_knowledge_worker.py)
- [src/backend/pyproject.toml](src/backend/pyproject.toml)
- [update.sh](update.sh)

</details>



## Purpose and Scope

This document provides a high-level overview of the Bisheng platform's system architecture, describing the three-tier structure, major components, and how they interact. Bisheng is a comprehensive AI application development platform supporting knowledge management, assistants, workflows, and chat capabilities.

For detailed information about specific subsystems:
- Frontend application structure: see [Frontend Architecture](#2.1)
- Backend service patterns: see [Backend Services](#2.2)  
- Storage layer details: see [Data Storage Layer](#2.3)
- Individual service implementations: see [Core Services](#3)

---

## Three-Tier Architecture Overview

Bisheng follows a classic three-tier architecture separating presentation, business logic, and data persistence layers. The system is containerized using Docker Compose and designed for scalability and modularity.

### High-Level System Diagram

```mermaid
graph TB
    subgraph "Presentation Tier"
        WEB["Web UI (React/TypeScript)<br/>Port 3001<br/>bisheng-frontend container"]
    end
    
    subgraph "Application Tier"
        FASTAPI["FastAPI Backend<br/>Port 7860<br/>bisheng-backend container"]
        WORKER["Celery Workers<br/>bisheng-backend-worker container"]
        LINSIGHT_WORKER["Linsight Workers<br/>Multi-process Execution"]
    end
    
    subgraph "Business Logic Layer"
        KNOWLEDGE["KnowledgeService<br/>bisheng/api/services/knowledge.py"]
        ASSISTANT["AssistantService<br/>bisheng/api/services/assistant.py"]
        WORKFLOW["WorkFlowService<br/>bisheng/api/services/workflow.py"]
        CHAT["ChatManager<br/>bisheng/chat/manager.py"]
        FLOW["FlowService<br/>bisheng/api/services/flow.py"]
    end
    
    subgraph "Data Tier"
        MYSQL["MySQL<br/>Port 3306<br/>bisheng-mysql container"]
        REDIS["Redis<br/>Port 6379<br/>bisheng-redis container"]
        MILVUS["Milvus<br/>Port 19530<br/>bisheng-milvus-standalone"]
        ES["Elasticsearch<br/>Port 9200<br/>bisheng-es container"]
        MINIO["MinIO<br/>Port 9100/9101<br/>bisheng-milvus-minio"]
        ETCD["ETCD<br/>bisheng-milvus-etcd"]
    end
    
    WEB --> FASTAPI
    FASTAPI --> KNOWLEDGE
    FASTAPI --> ASSISTANT
    FASTAPI --> WORKFLOW
    FASTAPI --> CHAT
    FASTAPI --> FLOW
    
    KNOWLEDGE --> WORKER
    KNOWLEDGE --> MYSQL
    KNOWLEDGE --> MILVUS
    KNOWLEDGE --> ES
    KNOWLEDGE --> MINIO
    
    ASSISTANT --> MYSQL
    WORKFLOW --> MYSQL
    FLOW --> MYSQL
    CHAT --> MYSQL
    
    WORKER --> REDIS
    LINSIGHT_WORKER --> REDIS
    
    MILVUS --> ETCD
    MILVUS --> MINIO
```

**Sources:** [docker/docker-compose.yml:1-201](), [src/backend/bisheng/api/services/knowledge.py:1-1000](), [src/backend/bisheng/api/services/assistant.py:1-500](), [src/backend/bisheng/api/services/workflow.py:1-430]()

---

## Component Responsibilities

### Frontend Layer

The frontend is a single-page application built with React and TypeScript, served via Nginx on port 3001. It communicates with the backend exclusively through REST APIs and WebSocket connections.

| Component | Technology | Responsibility |
|-----------|-----------|----------------|
| Web UI | React 18, TypeScript | User interface for all platform features |
| State Management | React Context/Hooks | Application state and data flow |
| API Client | Axios, WebSocket | Backend communication layer |
| Routing | React Router | Client-side navigation |

**Sources:** [docker/docker-compose.yml:110-123]()

---

### Backend Services Layer

The backend is built on FastAPI and provides both REST and WebSocket endpoints. The main application runs on port 7860 inside the `bisheng-backend` container.

### API Router Structure

```mermaid
graph LR
    FASTAPI["FastAPI App<br/>bisheng/main.py"]
    
    FASTAPI --> FLOWS["flows router<br/>/api/v1/flows"]
    FASTAPI --> ASSISTANT["assistant router<br/>/api/v1/assistant"]
    FASTAPI --> WORKFLOW["workflow router<br/>/api/v1/workflow"]
    FASTAPI --> KNOWLEDGE["knowledge router<br/>/api/v1/knowledge"]
    FASTAPI --> CHAT["chat endpoint<br/>WebSocket /chat"]
    
    FLOWS --> FlowService["FlowService<br/>bisheng/api/services/flow.py"]
    ASSISTANT --> AssistantService["AssistantService<br/>bisheng/api/services/assistant.py"]
    WORKFLOW --> WorkFlowService["WorkFlowService<br/>bisheng/api/services/workflow.py"]
    KNOWLEDGE --> KnowledgeService["KnowledgeService<br/>bisheng/api/services/knowledge.py"]
    CHAT --> ChatManager["ChatManager<br/>bisheng/chat/manager.py"]
```

**Sources:** [src/backend/bisheng/api/v1/flows.py:1-205](), [src/backend/bisheng/api/v1/assistant.py:1-177](), [src/backend/bisheng/api/v1/workflow.py:1-290]()

### Core Service Classes

| Service Class | File Path | Primary Responsibility |
|--------------|-----------|----------------------|
| `KnowledgeService` | [bisheng/api/services/knowledge.py]() | Knowledge base CRUD, file processing orchestration |
| `AssistantService` | [bisheng/api/services/assistant.py]() | AI assistant lifecycle management |
| `WorkFlowService` | [bisheng/api/services/workflow.py]() | Workflow execution and node management |
| `FlowService` | [bisheng/api/services/flow.py]() | Flow/skill version control and comparison |
| `ChatManager` | [bisheng/chat/manager.py]() | WebSocket connection pool management |

**Sources:** [src/backend/bisheng/api/services/knowledge.py:72-377](), [src/backend/bisheng/api/services/assistant.py:39-453](), [src/backend/bisheng/api/services/workflow.py:35-425](), [src/backend/bisheng/api/services/flow.py:38-425]()

---

## Data Storage Layer

Bisheng employs a polyglot persistence strategy with six different storage systems, each optimized for specific data types and access patterns.

### Storage Systems Architecture

```mermaid
graph TB
    subgraph "Relational Data"
        MYSQL["MySQL 8.0<br/>Container: bisheng-mysql<br/>Port: 3306"]
    end
    
    subgraph "Key-Value Cache"
        REDIS["Redis 7.0.4<br/>Container: bisheng-redis<br/>Port: 6379"]
    end
    
    subgraph "Vector Search"
        MILVUS["Milvus 2.5.10<br/>Container: bisheng-milvus-standalone<br/>Port: 19530"]
    end
    
    subgraph "Full-Text Search"
        ES["Elasticsearch 8.12.0<br/>Container: bisheng-es<br/>Port: 9200"]
    end
    
    subgraph "Object Storage"
        MINIO["MinIO RELEASE.2023-03-20T20-16-18Z<br/>Container: bisheng-milvus-minio<br/>Ports: 9100, 9101"]
    end
    
    subgraph "Coordination"
        ETCD["ETCD v3.5.5<br/>Container: bisheng-milvus-etcd"]
    end
    
    MYSQL --> |"User, Flow, Assistant,<br/>KnowledgeFile, Message"| APP["Application Services"]
    REDIS --> |"Session cache,<br/>Celery queue,<br/>Preview cache"| APP
    MILVUS --> |"Vector embeddings,<br/>Semantic search"| APP
    ES --> |"Keyword search,<br/>Hybrid retrieval"| APP
    MINIO --> |"Documents, images,<br/>Model files"| APP
    
    MILVUS --> ETCD
    MILVUS --> MINIO
```

**Sources:** [docker/docker-compose.yml:2-201]()

### Data Model Layer

The system uses SQLModel for ORM, providing both synchronous and asynchronous database access patterns:

```mermaid
graph LR
    subgraph "Domain Models"
        Flow["Flow<br/>bisheng/database/models/flow.py"]
        Assistant["Assistant<br/>bisheng/database/models/assistant.py"]
        Knowledge["Knowledge<br/>bisheng/knowledge/domain/models/knowledge.py"]
        KnowledgeFile["KnowledgeFile<br/>bisheng/knowledge/domain/models/knowledge_file.py"]
        Message["Message<br/>bisheng/database/models/message.py"]
    end
    
    subgraph "DAO Layer"
        FlowDao["FlowDao<br/>flow.py:109-425"]
        AssistantDao["AssistantDao<br/>assistant.py:65-270"]
        KnowledgeDao["KnowledgeDao"]
        KnowledgeFileDao["KnowledgeFileDao"]
    end
    
    subgraph "Database Session"
        SyncSession["get_sync_db_session()"]
        AsyncSession["get_async_db_session()"]
    end
    
    Flow --> FlowDao
    Assistant --> AssistantDao
    Knowledge --> KnowledgeDao
    KnowledgeFile --> KnowledgeFileDao
    
    FlowDao --> SyncSession
    FlowDao --> AsyncSession
    AssistantDao --> SyncSession
    AssistantDao --> AsyncSession
```

**Sources:** [src/backend/bisheng/database/models/flow.py:1-425](), [src/backend/bisheng/database/models/assistant.py:1-270]()

### Storage Responsibilities

| Storage System | Data Types | Access Pattern | Primary Use Cases |
|---------------|------------|----------------|------------------|
| MySQL | Structured relational data | ACID transactions | Users, flows, assistants, knowledge metadata, chat messages |
| Redis | Key-value ephemeral data | Fast in-memory access | Session caching, Celery task queue, file preview cache |
| Milvus | Vector embeddings | Approximate nearest neighbor | Semantic search on knowledge chunks |
| Elasticsearch | Text documents with metadata | Full-text search + filters | Keyword search, hybrid retrieval with Milvus |
| MinIO | Binary objects | S3-compatible API | Original files, generated PDFs, images, model artifacts |
| ETCD | Distributed configuration | Consensus-based KV store | Milvus cluster coordination |

**Sources:** [docker/docker-compose.yml:2-201](), [src/backend/bisheng/api/services/knowledge_imp.py:369-400]()

---

## Worker Process Architecture

Bisheng uses asynchronous task processing for long-running operations to avoid blocking the API server.

### Worker System Diagram

```mermaid
graph TB
    subgraph "Task Sources"
        API["FastAPI API<br/>bisheng-backend container"]
    end
    
    subgraph "Task Queue"
        REDIS_QUEUE["Redis Broker<br/>Port 6379<br/>Celery backend"]
    end
    
    subgraph "Worker Processes"
        CELERY["Celery Workers<br/>bisheng-backend-worker<br/>bisheng/worker/"]
        FILE_WORKER["file_worker.py<br/>parse_knowledge_file_celery"]
        REBUILD["rebuild_knowledge_worker.py<br/>rebuild_knowledge_celery"]
        QA["qa.py<br/>insert_qa_celery"]
    end
    
    subgraph "Task Execution"
        PROCESS["process_file_task()<br/>knowledge_imp.py:252-299"]
        ADD_EMBEDDING["addEmbedding()<br/>knowledge_imp.py:438-541"]
        READ_CHUNK["read_chunk_text()<br/>knowledge_imp.py:789-1000"]
    end
    
    API -->|"delay()"| REDIS_QUEUE
    REDIS_QUEUE --> CELERY
    CELERY --> FILE_WORKER
    CELERY --> REBUILD
    CELERY --> QA
    
    FILE_WORKER --> PROCESS
    PROCESS --> ADD_EMBEDDING
    ADD_EMBEDDING --> READ_CHUNK
```

**Sources:** [docker/docker-compose.yml:79-108](), [src/backend/bisheng/worker/knowledge/file_worker.py:1-330](), [src/backend/bisheng/api/services/knowledge_imp.py:252-661]()

### Worker Task Types

| Worker Module | Task Function | Trigger | Purpose |
|--------------|---------------|---------|---------|
| `file_worker.py` | `parse_knowledge_file_celery` | File upload | Parse document, extract text, generate embeddings, store in Milvus/ES |
| `file_worker.py` | `retry_knowledge_file_celery` | Manual retry | Retry failed file processing |
| `file_worker.py` | `file_copy_celery` | Knowledge base copy | Copy files and vectors between knowledge bases |
| `rebuild_knowledge_worker.py` | `rebuild_knowledge_celery` | Embedding model change | Re-embed all chunks with new model |
| `qa.py` | `insert_qa_celery` | QA pair creation | Insert Q&A pair into vector stores |

**Sources:** [src/backend/bisheng/worker/knowledge/file_worker.py:25-330](), [src/backend/bisheng/worker/knowledge/rebuild_knowledge_worker.py:22-220](), [src/backend/bisheng/worker/knowledge/qa.py:20-180]()

---

## Configuration Management

The system uses a layered configuration approach with environment variables, YAML files, and database-stored settings.

### Configuration Sources

```mermaid
graph TB
    ENV["Environment Variables<br/>docker-compose.yml"]
    CONFIG_YAML["config.yaml<br/>Deployment configuration"]
    INITDB["initdb_config.yaml<br/>Database-stored settings"]
    
    ENV --> |"Override"| APP["Application Runtime<br/>bisheng/common/services/config_service.py"]
    CONFIG_YAML --> APP
    INITDB --> |"Loaded at startup"| DB["MySQL config_system table"]
    DB --> APP
    
    APP --> COMPONENTS["Service Components"]
```

**Sources:** [docker/docker-compose.yml:46-58]()

### Key Configuration Categories

| Configuration Type | Storage Location | Scope | Examples |
|-------------------|------------------|-------|----------|
| Infrastructure | `docker-compose.yml` env vars | Container orchestration | Database URLs, ports, service endpoints |
| Deployment | `config.yaml` | Application runtime | Vector store connections, logging, storage paths |
| Feature flags | `initdb_config.yaml` → MySQL | Dynamic application settings | LLM models, knowledge base settings, UI configurations |

**Sources:** [docker/docker-compose.yml:1-201]()

---

## Version Information

The system maintains version consistency across multiple components:

| Component | Version | Location |
|-----------|---------|----------|
| Backend | 2.4.0-beta1 | [src/backend/bisheng/__init__.py:10]() |
| Python Package | 2.4.0-beta1 | [src/backend/pyproject.toml:3]() |
| Docker Images | v2.4.0-beta1 | [docker/docker-compose.yml:43](), [docker/docker-compose.yml:81](), [docker/docker-compose.yml:112]() |

Version updates are automated via the `update.sh` script which modifies all version references consistently.

**Sources:** [src/backend/bisheng/__init__.py:1-16](), [src/backend/pyproject.toml:1-87](), [update.sh:1-8]()

---

## Deployment Architecture

### Container Orchestration

The system uses Docker Compose to manage six core services and three optional services:

**Core Services:**
1. `bisheng-mysql` - Relational database
2. `bisheng-redis` - Cache and queue
3. `bisheng-backend` - FastAPI application server
4. `bisheng-backend-worker` - Celery async workers
5. `bisheng-frontend` - Nginx + React SPA
6. `bisheng-es` - Elasticsearch search engine
7. `bisheng-milvus-standalone` - Vector database
8. `bisheng-milvus-minio` - Object storage
9. `bisheng-milvus-etcd` - Coordination service

**Optional Services (separate compose files):**
- `bisheng-unstructured` - Advanced document processing ([docker/docker-compose-uns.yml:2-22]())
- `bisheng-ft-server` - Fine-tuning service ([docker/docker-compose-ft.yml:2-31]())
- `bisheng-office` - OnlyOffice document editing ([docker/docker-compose-office.yml:2-15]())

### Health Checks and Dependencies

All services implement health checks to ensure proper startup order:

```mermaid
graph TD
    MYSQL["MySQL<br/>Health: mysql client test"]
    REDIS["Redis<br/>Health: redis-cli ping"]
    ETCD["ETCD<br/>Health: etcdctl endpoint health"]
    MINIO["MinIO<br/>Health: curl /minio/health/live"]
    
    MILVUS["Milvus<br/>Health: curl /healthz<br/>Depends on: ETCD, MinIO"]
    BACKEND["Backend<br/>Health: curl /health<br/>Depends on: MySQL, Redis"]
    WORKER["Worker<br/>Depends on: MySQL, Redis"]
    FRONTEND["Frontend<br/>Depends on: Backend"]
    
    ETCD --> MILVUS
    MINIO --> MILVUS
    MYSQL --> BACKEND
    REDIS --> BACKEND
    MYSQL --> WORKER
    REDIS --> WORKER
    BACKEND --> FRONTEND
```

**Sources:** [docker/docker-compose.yml:15-20](), [docker/docker-compose.yml:34-38](), [docker/docker-compose.yml:67-77](), [docker/docker-compose.yml:150-154](), [docker/docker-compose.yml:170-174](), [docker/docker-compose.yml:189-194]()

---

## Inter-Service Communication Patterns

### Synchronous Communication

REST API calls between frontend and backend use standard HTTP/HTTPS on port 7860. All API routes are versioned under `/api/v1/` or `/api/v2/`.

### Asynchronous Communication  

1. **WebSocket** - Real-time bidirectional communication for chat and workflow execution
2. **Celery Tasks** - Async job execution via Redis broker
3. **Event Streaming** - Server-sent events (SSE) for streaming responses

### Internal Service URLs

Within the Docker network, services reference each other by container names:
- Backend to MySQL: `mysql:3306`
- Backend to Redis: `redis:6379`  
- Backend to Milvus: `milvus:19530`
- Backend to Elasticsearch: `elasticsearch:9200`
- Backend to MinIO: `minio:9000`

**Sources:** [docker/docker-compose.yml:48-58](), [docker/docker-compose.yml:84-94]()

---

# Page: Frontend Architecture

# Frontend Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/frontend/package-lock.json](src/frontend/package-lock.json)
- [src/frontend/platform/public/assets/dashboard/setting.svg](src/frontend/platform/public/assets/dashboard/setting.svg)
- [src/frontend/platform/public/locales/en-US/dashboard.json](src/frontend/platform/public/locales/en-US/dashboard.json)
- [src/frontend/platform/public/locales/ja/dashboard.json](src/frontend/platform/public/locales/ja/dashboard.json)
- [src/frontend/platform/public/locales/zh-Hans/dashboard.json](src/frontend/platform/public/locales/zh-Hans/dashboard.json)
- [src/frontend/platform/src/components/bs-ui/select/hover.tsx](src/frontend/platform/src/components/bs-ui/select/hover.tsx)
- [src/frontend/platform/src/layout/MainLayout.tsx](src/frontend/platform/src/layout/MainLayout.tsx)
- [src/frontend/platform/src/pages/BuildPage/flow/FlowNode/component/KnowledgeSelectItem.tsx](src/frontend/platform/src/pages/BuildPage/flow/FlowNode/component/KnowledgeSelectItem.tsx)
- [src/frontend/platform/src/pages/Dashboard/components/config/ChartSelector.tsx](src/frontend/platform/src/pages/Dashboard/components/config/ChartSelector.tsx)
- [src/frontend/platform/src/pages/Dashboard/components/config/ComponentConfigDrawer.tsx](src/frontend/platform/src/pages/Dashboard/components/config/ComponentConfigDrawer.tsx)
- [src/frontend/platform/src/pages/Dashboard/components/config/DashboardConfigPanel.tsx](src/frontend/platform/src/pages/Dashboard/components/config/DashboardConfigPanel.tsx)
- [src/frontend/platform/src/pages/Dashboard/components/config/DatasetSelector.tsx](src/frontend/platform/src/pages/Dashboard/components/config/DatasetSelector.tsx)
- [src/frontend/platform/src/pages/Dashboard/components/config/DimensionBlock.tsx](src/frontend/platform/src/pages/Dashboard/components/config/DimensionBlock.tsx)
- [src/frontend/platform/src/pages/Dashboard/components/config/FilterConditionDialog.tsx](src/frontend/platform/src/pages/Dashboard/components/config/FilterConditionDialog.tsx)
- [src/frontend/platform/src/pages/Dashboard/components/config/StyleConfigPanel.tsx](src/frontend/platform/src/pages/Dashboard/components/config/StyleConfigPanel.tsx)
- [src/frontend/platform/src/pages/Dashboard/components/config/useChartState.tsx](src/frontend/platform/src/pages/Dashboard/components/config/useChartState.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/AdjustFilesUpload.tsx](src/frontend/platform/src/pages/KnowledgePage/AdjustFilesUpload.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/KnowledgeFile.tsx](src/frontend/platform/src/pages/KnowledgePage/KnowledgeFile.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/KnowledgeQa.tsx](src/frontend/platform/src/pages/KnowledgePage/KnowledgeQa.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/components/FileUploadStep2.tsx](src/frontend/platform/src/pages/KnowledgePage/components/FileUploadStep2.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/components/FileUploadStep4.tsx](src/frontend/platform/src/pages/KnowledgePage/components/FileUploadStep4.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/components/Files.tsx](src/frontend/platform/src/pages/KnowledgePage/components/Files.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/components/Header.tsx](src/frontend/platform/src/pages/KnowledgePage/components/Header.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/components/Paragraphs.tsx](src/frontend/platform/src/pages/KnowledgePage/components/Paragraphs.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/components/PreviewFile.tsx](src/frontend/platform/src/pages/KnowledgePage/components/PreviewFile.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/components/PreviewParagraph.tsx](src/frontend/platform/src/pages/KnowledgePage/components/PreviewParagraph.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/components/PreviewResult.tsx](src/frontend/platform/src/pages/KnowledgePage/components/PreviewResult.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/components/RuleFile.tsx](src/frontend/platform/src/pages/KnowledgePage/components/RuleFile.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/components/RuleTable.tsx](src/frontend/platform/src/pages/KnowledgePage/components/RuleTable.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/detail.tsx](src/frontend/platform/src/pages/KnowledgePage/detail.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/filesUpload.tsx](src/frontend/platform/src/pages/KnowledgePage/filesUpload.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/qas.tsx](src/frontend/platform/src/pages/KnowledgePage/qas.tsx)

</details>



## Purpose and Scope

This document describes the React/TypeScript frontend architecture of the Bisheng platform. The frontend is a comprehensive single-page application (SPA) serving Port 3001, organized into distinct feature domains: Knowledge Management, Chat/Assistants, Dashboard/Analytics, and System Administration. This page covers the application structure, routing hierarchy, major page components, shared UI libraries, API integration patterns, and state management approaches.

For backend API services that this frontend communicates with, see [Backend Services](#2.2). For specific feature implementations, see [Knowledge Base Management](#3.1), [Chat and Messaging System](#3.2), [Assistant System](#3.3), and [Dashboard and Analytics](#3.6).

---

## Application Structure and Entry Points

The frontend application follows a standard React SPA architecture with centralized routing, layout management, and feature-based page organization.

### Application Root and Router Configuration

```mermaid
graph TB
    AppTsx["App.tsx<br/>Root Component"]
    RouterConfig["routes.tsx<br/>Route Definitions"]
    MainLayout["MainLayout.tsx<br/>Navigation Shell"]
    
    AppTsx --> RouterConfig
    RouterConfig --> MainLayout
    
    MainLayout --> NavBar["Left Navigation Bar<br/>ApplicationIcon, KnowledgeIcon,<br/>BookOpenIcon, DashboardIcon, etc."]
    MainLayout --> Header["Top Header<br/>User Menu, Settings"]
    MainLayout --> Content["Main Content Area<br/><Outlet/>"]
    
    Content --> KnowledgePages["Knowledge Pages<br/>/filelib/*"]
    Content --> ChatPages["Chat Pages<br/>/chat/*"]
    Content --> SkillPages["Skill/Flow Pages<br/>/build/*"]
    Content --> DashboardPages["Dashboard Pages<br/>/dashboard/*"]
    Content --> SystemPages["System Pages<br/>/sys/*"]
```

The `MainLayout` component provides the primary navigation structure with route-specific active state highlighting, user context integration, and responsive layout management.

**Sources:**
- [src/frontend/platform/src/layout/MainLayout.tsx:1-50]()
- [src/frontend/platform/src/layout/MainLayout.tsx:100-250]()

---

## Major Application Domains

The frontend is organized into five primary feature domains, each with dedicated page components and routing structures.

### Frontend Domain Architecture

```mermaid
graph TB
    Frontend["Frontend Application<br/>Port 3001"]
    
    subgraph "Knowledge Domain"
        KbList["KnowledgeFile.tsx<br/>/filelib"]
        QaList["KnowledgeQa.tsx<br/>/filelib/qalib"]
        KbDetail["detail.tsx + Files.tsx<br/>/filelib/:id"]
        KbUpload["filesUpload.tsx<br/>/filelib/upload/:id"]
        Paragraphs["Paragraphs.tsx<br/>Chunk Editor"]
    end
    
    subgraph "Chat/Assistant Domain"
        ChatUI["SkillChatPage<br/>Chat Interface"]
        AssistantMgmt["Assistant Management<br/>Configure Agents"]
        SkillList["SkillPage<br/>/build"]
        SkillEdit["Skill Editor<br/>Graph Builder"]
    end
    
    subgraph "Dashboard Domain"
        DashList["Dashboard List<br/>/dashboard"]
        DashEdit["Dashboard Editor<br/>Component Config"]
        ComponentDrawer["ComponentConfigDrawer<br/>Chart Configuration"]
        ChartRender["Chart Rendering<br/>ECharts Integration"]
    end
    
    subgraph "System Domain"
        UserMgmt["User Management<br/>/sys/user"]
        GroupMgmt["Group Management<br/>/sys/usergroup"]
        ModelMgmt["Model Page<br/>/sys/model"]
        AuditPage["Audit Log Viewer<br/>/sys/audit"]
    end
    
    subgraph "Shared Infrastructure"
        APICtrl["controllers/API/<br/>Centralized API Layer"]
        BsUI["components/bs-ui/<br/>UI Component Library"]
        Stores["Zustand Stores<br/>dashboardStore, etc."]
    end
    
    Frontend --> KbList
    Frontend --> ChatUI
    Frontend --> DashList
    Frontend --> UserMgmt
    
    KbList --> APICtrl
    ChatUI --> APICtrl
    DashEdit --> APICtrl
    
    ComponentDrawer --> BsUI
    KbUpload --> BsUI
    
    DashEdit --> Stores
```

**Sources:**
- [src/frontend/platform/src/pages/KnowledgePage/KnowledgeFile.tsx:314-640]()
- [src/frontend/platform/src/pages/Dashboard/components/config/ComponentConfigDrawer.tsx:91-700]()
- [src/frontend/platform/src/layout/MainLayout.tsx:1-400]()

### Knowledge Management Pages

The knowledge management system provides document ingestion, segmentation, preview, and chunk-level editing capabilities.

| Route Pattern | Component | Primary Functions |
|--------------|-----------|-------------------|
| `/filelib` | `KnowledgeFile.tsx` | Knowledge base list, create, copy, delete |
| `/filelib/qalib` | `KnowledgeQa.tsx` | QA knowledge base list and management |
| `/filelib/upload/:id` | `filesUpload.tsx` | 4-step file upload wizard |
| `/filelib/adjust/:id` | `AdjustFilesUpload.tsx` | 3-step segmentation adjustment |
| `/filelib/:id` | `detail.tsx` + `Files.tsx` | File list with status indicators |
| `/filelib/:id` (tab 2) | `Paragraphs.tsx` | Chunk preview and inline editing |

**Key Workflows**:
- **File Upload**: `FileUploadStep1` → `FileUploadStep2` → `PreviewResult` → `FileUploadStep4`
- **Segmentation Adjustment**: `FileUploadStep2` → `PreviewResult` → `FileUploadStep4`
- **Chunk Editing**: `Files.tsx` → `Paragraphs.tsx` → `PreviewFile` + `PreviewParagraph`

**Sources:**
- [src/frontend/platform/src/pages/KnowledgePage/KnowledgeFile.tsx:1-640]()
- [src/frontend/platform/src/pages/KnowledgePage/filesUpload.tsx:37-417]()
- [src/frontend/platform/src/pages/KnowledgePage/components/Paragraphs.tsx:26-796]()

### Dashboard and Analytics Pages

The dashboard system provides business intelligence capabilities with visual chart builders, dataset integration, and query components.

| Route | Component | Features |
|-------|-----------|----------|
| `/dashboard` | Dashboard List | Published/unpublished dashboards, search |
| `/dashboard/:id` | Dashboard Viewer | Component rendering, query parameter handling |
| `/dashboard/:id/edit` | Dashboard Editor | Drag-drop layout, component configuration |

**Core Dashboard Components**:
- **ComponentConfigDrawer**: Chart type selection, dimension/metric configuration, filter conditions, style customization
- **DatasetSelector**: Dataset picker with field browser (dimensions/metrics)
- **ChartSelector**: Query component configuration with linked charts and time ranges
- **StyleConfigPanel**: Theme colors, axis titles, legend positioning, font formatting

**Sources:**
- [src/frontend/platform/src/pages/Dashboard/components/config/ComponentConfigDrawer.tsx:91-700]()
- [src/frontend/platform/src/pages/Dashboard/components/config/DatasetSelector.tsx:22-300]()
- [src/frontend/platform/src/pages/Dashboard/components/config/ChartSelector.tsx:40-300]()
</old_str>

<new_str>
# Frontend Architecture

## Purpose and Scope

This document describes the React/TypeScript frontend architecture of the Bisheng platform. The frontend is a comprehensive single-page application (SPA) serving Port 3001, organized into distinct feature domains: Knowledge Management, Chat/Assistants, Dashboard/Analytics, and System Administration. This page covers the application structure, routing hierarchy, major page components, shared UI libraries, API integration patterns, and state management approaches.

For backend API services that this frontend communicates with, see [Backend Services](#2.2). For specific feature implementations, see [Knowledge Base Management](#3.1), [Chat and Messaging System](#3.2), [Assistant System](#3.3), and [Dashboard and Analytics](#3.6).

---

## Application Structure and Entry Points

The frontend application follows a standard React SPA architecture with centralized routing, layout management, and feature-based page organization.

### Application Root and Router Configuration

**Diagram: Application Bootstrap and Layout Structure**

```mermaid
graph TB
    AppTsx["App.tsx<br/>Root Component"]
    RouterConfig["routes.tsx<br/>Route Definitions"]
    MainLayout["MainLayout.tsx<br/>Navigation Shell"]
    
    AppTsx --> RouterConfig
    RouterConfig --> MainLayout
    
    MainLayout --> NavBar["Left Navigation Bar<br/>ApplicationIcon, KnowledgeIcon,<br/>BookOpenIcon, DashboardIcon"]
    MainLayout --> Header["Top Header<br/>User Menu, Settings"]
    MainLayout --> Content["Main Content Area<br/>React Router Outlet"]
    
    Content --> KnowledgePages["/filelib/*<br/>Knowledge Pages"]
    Content --> ChatPages["/chat/*<br/>Chat Pages"]
    Content --> SkillPages["/build/*<br/>Skill/Flow Pages"]
    Content --> DashboardPages["/dashboard/*<br/>Dashboard Pages"]
    Content --> SystemPages["/sys/*<br/>System Pages"]
```

The `MainLayout` component [src/frontend/platform/src/layout/MainLayout.tsx:1-400]() provides the primary navigation structure with route-specific active state highlighting, user context integration via `userContext`, and responsive layout management. Navigation icons are imported from `@/components/bs-icons` [src/frontend/platform/src/layout/MainLayout.tsx:1-12]().

**Sources:**
- [src/frontend/platform/src/layout/MainLayout.tsx:1-50]()
- [src/frontend/platform/src/layout/MainLayout.tsx:100-400]()

---

## Major Application Domains

The frontend is organized into five primary feature domains, each with dedicated page components and routing structures.

### Frontend Domain Architecture

**Diagram: Feature Domain Organization with Code Entities**

```mermaid
graph TB
    Frontend["Frontend Application<br/>Port 3001 - Vite + React"]
    
    subgraph "Knowledge Domain /filelib"
        KbList["KnowledgeFile.tsx<br/>readFileLibDatabase API"]
        QaList["KnowledgeQa.tsx<br/>QA KB Management"]
        KbDetail["detail.tsx + Files.tsx<br/>readFileByLibDatabase"]
        KbUpload["filesUpload.tsx<br/>subUploadLibFile API"]
        Paragraphs["Paragraphs.tsx<br/>getKnowledgeChunkApi"]
    end
    
    subgraph "Chat/Assistant Domain /build"
        ChatUI["SkillChatPage<br/>WebSocket Chat"]
        AssistantMgmt["Assistant Management<br/>Assistant Config"]
        SkillList["SkillPage<br/>Flow/Skill List"]
        SkillEdit["Skill Editor<br/>Graph Builder Canvas"]
    end
    
    subgraph "Dashboard Domain /dashboard"
        DashList["Dashboard List<br/>getDashboards API"]
        DashEdit["Dashboard Editor<br/>useEditorDashboardStore"]
        ComponentDrawer["ComponentConfigDrawer<br/>Chart Configuration"]
        DatasetSelector["DatasetSelector<br/>getDatasets API"]
    end
    
    subgraph "System Domain /sys"
        UserMgmt["User Management<br/>UserDao backend"]
        GroupMgmt["Group Management<br/>GroupDao backend"]
        ModelMgmt["Model Page<br/>LLM Configuration"]
        AuditPage["Audit Log Viewer<br/>AuditLogDao"]
    end
    
    subgraph "Shared Infrastructure"
        APICtrl["controllers/API/index.ts<br/>captureAndAlertRequestErrorHoc"]
        BsUI["components/bs-ui/<br/>Button, Input, Dialog, etc."]
        Stores["Zustand Stores<br/>dashboardStore, knowledgeStore"]
    end
    
    Frontend --> KbList
    Frontend --> ChatUI
    Frontend --> DashList
    Frontend --> UserMgmt
    
    KbList --> APICtrl
    ChatUI --> APICtrl
    DashEdit --> APICtrl
    
    ComponentDrawer --> BsUI
    KbUpload --> BsUI
    
    DashEdit --> Stores
```

**Sources:**
- [src/frontend/platform/src/pages/KnowledgePage/KnowledgeFile.tsx:314-640]()
- [src/frontend/platform/src/pages/Dashboard/components/config/ComponentConfigDrawer.tsx:91-700]()
- [src/frontend/platform/src/layout/MainLayout.tsx:1-400]()

### Knowledge Management Pages

The knowledge management system provides document ingestion, segmentation, preview, and chunk-level editing capabilities.

| Route Pattern | Component | Primary Functions |
|--------------|-----------|-------------------|
| `/filelib` | `KnowledgeFile.tsx` | Knowledge base list, create via `createFileLib`, copy via `copyLibDatabase`, delete via `deleteFileLib` |
| `/filelib/qalib` | `KnowledgeQa.tsx` | QA knowledge base list, create via `createFileLib(type=1)` |
| `/filelib/upload/:id` | `filesUpload.tsx` | 4-step wizard: `FileUploadStep1` → `FileUploadStep2` → `PreviewResult` → `FileUploadStep4` |
| `/filelib/adjust/:id` | `AdjustFilesUpload.tsx` | 3-step re-segmentation: `FileUploadStep2` → `PreviewResult` → `FileUploadStep4` |
| `/filelib/:id` | `detail.tsx` + `Files.tsx` | File list table with `StatusIndicator`, uses `readFileByLibDatabase` |
| `/filelib/:id` (paragraphs) | `Paragraphs.tsx` | Chunk editor with `PreviewFile` + `PreviewParagraph`, calls `updateChunkApi` |

**Key Workflows**:
- **File Upload**: `FileUploadStep1` (file selection) → `FileUploadStep2` (segmentation rules) → `PreviewResult` (text comparison with `previewFileSplitApi`) → `FileUploadStep4` (polling status via `readFileByLibDatabase`)
- **Chunk Editing**: Click file in `Files.tsx` → Navigate to `Paragraphs.tsx` → Select chunk → `PreviewFile` highlights bbox → Edit in `PreviewParagraph` → Save via `updateChunkApi`

**Sources:**
- [src/frontend/platform/src/pages/KnowledgePage/KnowledgeFile.tsx:1-640]()
- [src/frontend/platform/src/pages/KnowledgePage/filesUpload.tsx:37-417]()
- [src/frontend/platform/src/pages/KnowledgePage/components/Paragraphs.tsx:26-796]()
- [src/frontend/platform/src/pages/KnowledgePage/components/Files.tsx:1-300]()

### Dashboard and Analytics Pages

The dashboard system provides business intelligence capabilities with visual chart builders, dataset integration via `getDatasets` API, and query component linking.

| Route | Component | Features |
|-------|-----------|----------|
| `/dashboard` | Dashboard List | Published/unpublished dashboards, search, default dashboard selection |
| `/dashboard/:id` | Dashboard Viewer | Component rendering with ECharts, query parameter handling |
| `/dashboard/:id/edit` | Dashboard Editor | Drag-drop layout using `react-grid-layout`, component configuration via `useEditorDashboardStore` |

**Core Dashboard Components**:
- **ComponentConfigDrawer** [src/frontend/platform/src/pages/Dashboard/components/config/ComponentConfigDrawer.tsx:91-700](): Chart type selection with `ComponentPicker`, dimension/metric drag-drop via `DimensionBlock`, filter conditions via `FilterConditionDialog`, style customization via `StyleConfigPanel`
- **DatasetSelector** [src/frontend/platform/src/pages/Dashboard/components/config/DatasetSelector.tsx:22-300](): Dataset picker with field browser, calls `getDatasets` and displays dimensions/metrics with time granularity support
- **ChartSelector** [src/frontend/platform/src/pages/Dashboard/components/config/ChartSelector.tsx:40-200](): Query component configuration with linked chart selection, time range picker via `AdvancedDatePicker`
- **useChartState** [src/frontend/platform/src/pages/Dashboard/components/config/useChartState.tsx:12-400](): Custom hook managing chart state including `categoryDimensions`, `stackDimensions`, `valueDimensions`, and sort priority

**Sources:**
- [src/frontend/platform/src/pages/Dashboard/components/config/ComponentConfigDrawer.tsx:91-700]()
- [src/frontend/platform/src/pages/Dashboard/components/config/DatasetSelector.tsx:22-300]()
- [src/frontend/platform/src/pages/Dashboard/components/config/ChartSelector.tsx:40-200]()
- [src/frontend/platform/src/pages/Dashboard/components/config/useChartState.tsx:12-300]()

### Chat and Assistant Pages

The chat system provides real-time conversational interfaces with AI assistants, supporting both pre-configured assistants and custom skill/flow execution.

**Chat Components**:
- **SkillChatPage**: Main chat interface with WebSocket connection (`ChatManager`), message streaming, and session management
- **Assistant Management**: Configure assistant parameters including model selection, tool integration, knowledge base linking, and system prompts
- **SkillPage** (`/build`): Visual flow editor with node-based programming interface for custom assistant logic

**Key Features**:
- Real-time message streaming via WebSocket endpoints
- Chat history persistence with session tracking
- Message marking and review workflows for quality control
- Multi-turn conversation with context management

**Sources:**
- Referenced in high-level architecture diagrams (components not in provided file excerpts)

### System Administration Pages

System pages provide platform administration capabilities including user management, group permissions, model configuration, and audit logging.

| Route | Component | Functions |
|-------|-----------|-----------|
| `/sys/user` | User Management | User creation, role assignment, group membership |
| `/sys/usergroup` | Group Management | Group creation, resource permissions, RBAC configuration |
| `/sys/model` | Model Page | LLM model registration, embedding model selection, API key management |
| `/sys/audit` | Audit Log Viewer | Search and filter audit events via `AuditLogService` backend |

**Permission Model**: The system implements group-based resource ownership combined with role-based access control (RBAC), where resources (flows, knowledge bases, assistants) belong to user groups and roles define fine-grained permissions within groups.

**Sources:**
- [src/frontend/platform/src/layout/MainLayout.tsx:1-12]() (navigation icons)
- Referenced in high-level architecture Diagram 4 (Data Access & Permission Architecture)

---

## Shared Component Library and UI Patterns

The frontend uses a custom component library (`components/bs-ui/`) providing consistent UI patterns across all feature domains.

### Core UI Components

**Diagram: Shared Component Architecture**

```mermaid
graph TB
    BsUI["components/bs-ui/<br/>Shared Component Library"]
    
    BsUI --> Forms["Form Components"]
    BsUI --> Layout["Layout Components"]
    BsUI --> Feedback["Feedback Components"]
    BsUI --> DataDisplay["Data Display"]
    BsUI --> Icons["Icon Library"]
    
    Forms --> Button["Button.tsx<br/>variant: outline, ghost, etc."]
    Forms --> Input["Input.tsx + SearchInput"]
    Forms --> Select["Select.tsx + SelectHover"]
    Forms --> Checkbox["checkBox.tsx"]
    Forms --> Radio["radio.tsx"]
    Forms --> Textarea["textarea in Input"]
    
    Layout --> Dialog["dialog.tsx<br/>Modal dialogs"]
    Layout --> Tabs["tabs.tsx<br/>Tab navigation"]
    Layout --> Accordion["accordion.tsx<br/>Collapsible sections"]
    Layout --> Tooltip["tooltip.tsx + Tip.tsx"]
    
    Feedback --> Toast["toast/use-toast.ts<br/>useToast hook"]
    Feedback --> Alert["alertDialog/useConfirm<br/>bsConfirm()"]
    Feedback --> Loading["LoadingIcon"]
    
    DataDisplay --> Table["table.tsx<br/>TableHeader, TableBody, etc."]
    DataDisplay --> Pagination["pagination/autoPagination"]
    DataDisplay --> Badge["badge.tsx"]
    
    Icons --> BsIcons["bs-icons/<br/>ApplicationIcon, KnowledgeIcon,<br/>BookOpenIcon, etc."]
    Icons --> Lucide["lucide-react<br/>Settings, Trash2, etc."]
```

**Common Patterns**:
- **Form Validation**: Input components with error states and validation messages
- **Confirmation Dialogs**: `bsConfirm()` for destructive actions [src/frontend/platform/src/components/bs-ui/alertDialog/useConfirm.ts]()
- **Toast Notifications**: `useToast()` hook for success/error/warning messages [src/frontend/platform/src/components/bs-ui/toast/use-toast.ts]()
- **Loading States**: `LoadingIcon` component with consistent spinner styling [src/frontend/platform/src/components/bs-icons/loading.tsx]()

**Sources:**
- [src/frontend/platform/src/pages/KnowledgePage/KnowledgeFile.tsx:1-30]() (component imports)
- [src/frontend/platform/src/pages/Dashboard/components/config/ComponentConfigDrawer.tsx:1-27]() (component imports)
- [src/frontend/platform/src/components/bs-ui/button.tsx]() (referenced)
- [src/frontend/platform/src/components/bs-ui/toast/use-toast.ts]() (referenced)

### Specialized Components

**File Preview Components**:
- **FileView**: Multi-format document viewer supporting PDF (with bbox highlighting), images, and structured data
- **DocxPreview**: DOCX file renderer [src/frontend/platform/src/pages/KnowledgePage/components/PreviewFile.tsx:8]()
- **ExcelPreview**: Spreadsheet viewer for XLSX/XLS/CSV [src/frontend/platform/src/pages/KnowledgePage/components/PreviewFile.tsx:12]()
- **TxtFileViewer**: Text and Markdown renderer [src/frontend/platform/src/pages/KnowledgePage/components/PreviewFile.tsx:11]()

**Editor Components**:
- **AceEditor**: Code editor with syntax highlighting, used for raw chunk editing [src/frontend/platform/src/pages/KnowledgePage/components/PreviewParagraph.tsx:11]()
- **Vditor**: WYSIWYG Markdown editor with instant rendering [src/frontend/platform/src/pages/KnowledgePage/components/PreviewParagraph.tsx:12-13]()

**Sources:**
- [src/frontend/platform/src/pages/KnowledgePage/components/PreviewFile.tsx:1-15]()
- [src/frontend/platform/src/pages/KnowledgePage/components/PreviewParagraph.tsx:11-13]()

---

## API Integration Layer

The frontend communicates with backend services through a centralized API module (`controllers/API/index.ts`) that provides typed API functions, error handling, and request/response transformations.

### API Controller Organization

**Diagram: API Layer Architecture with Backend Endpoints**

```mermaid
graph TB
    Frontend["Frontend Pages<br/>React Components"]
    
    subgraph "controllers/API/"
        APIIndex["index.ts<br/>Knowledge & File APIs"]
        DashboardAPI["dashboard.ts<br/>getDatasets, getDashboards"]
        FinetuneAPI["finetune.ts<br/>getKnowledgeModelConfig"]
    end
    
    ErrorHandler["captureAndAlertRequestErrorHoc<br/>Global Error Handler"]
    
    subgraph "Backend Endpoints"
        KnowledgeEndpoints["/api/v1/knowledge<br/>POST /create, GET /, PUT /, DELETE /"]
        FileEndpoints["/api/v1/knowledge/upload<br/>POST /process, POST /retry"]
        ChunkEndpoints["/api/v1/knowledge/chunk<br/>GET /, PUT /, DELETE /"]
        PreviewEndpoints["/api/v1/knowledge/preview<br/>POST /, GET /status"]
        DashboardEndpoints["/api/v2/dashboard<br/>GET /datasets, GET /dashboards"]
    end
    
    Frontend --> APIIndex
    Frontend --> DashboardAPI
    Frontend --> FinetuneAPI
    
    APIIndex --> ErrorHandler
    DashboardAPI --> ErrorHandler
    
    ErrorHandler --> KnowledgeEndpoints
    ErrorHandler --> FileEndpoints
    ErrorHandler --> ChunkEndpoints
    ErrorHandler --> PreviewEndpoints
    ErrorHandler --> DashboardEndpoints
```

**Sources:**
- [src/frontend/platform/src/controllers/API/index.ts:139-531]()
- [src/frontend/platform/src/controllers/API/dashboard.ts]() (referenced)
- [src/frontend/platform/src/controllers/API/finetune.ts]() (referenced)

### Key API Function Categories

| Category | Functions | Backend Routes |
|----------|-----------|----------------|
| **Knowledge CRUD** | `createFileLib`, `readFileLibDatabase`, `updateKnowledge`, `deleteFileLib`, `copyLibDatabase` | `/api/v1/knowledge/*` |
| **File Operations** | `uploadLibFile`, `subUploadLibFile`, `retryKnowledgeFileApi`, `rebUploadFile`, `deleteFile` | `/api/v1/knowledge/upload`, `/api/v1/knowledge/process` |
| **Chunk Management** | `getKnowledgeChunkApi`, `updateChunkApi`, `delChunkApi` | `/api/v1/knowledge/chunk` |
| **Preview System** | `previewFileSplitApi`, `updatePreviewChunkApi`, `delChunkInPreviewApi` | `/api/v1/knowledge/preview` |
| **Metadata** | `addMetadata`, `updateMetadataFields`, `deleteMetadataFields`, `saveUserMetadataApi` | `/api/v1/knowledge/metadata` |
| **Dashboard** | `getDatasets`, `getDashboards`, `getFieldEnums` | `/api/v2/dashboard/*` |

**Error Handling Pattern**:
All API calls are wrapped with `captureAndAlertRequestErrorHoc()` [src/frontend/platform/src/controllers/request.ts](), which:
1. Catches async errors and rejected promises
2. Displays toast notifications with localized messages
3. Returns `null` on error for graceful degradation
4. Supports custom error handlers as optional second parameter

**Usage Example**:
```typescript
await captureAndAlertRequestErrorHoc(
  deleteFile(id).then(res => {
    reload();
  })
);
```

**Sources:**
- [src/frontend/platform/src/controllers/API/index.ts:139-531]()
- [src/frontend/platform/src/pages/KnowledgePage/components/Files.tsx:157-161]()
- [src/frontend/platform/src/controllers/request.ts]() (referenced)

### Polling-Based API Pattern

The `previewFileSplitApi()` function implements a polling mechanism for long-running preview tasks, simulating server-sent events (SSE).

**Polling State Machine**:

```mermaid
stateDiagram-v2
    [*] --> CreateTask: "POST /api/v1/knowledge/preview"
    CreateTask --> Polling: "Receive preview_file_id"
    
    Polling --> Processing: "status='processing'"
    Processing --> Polling: "Wait 2s, poll again"
    
    Polling --> Completed: "status='completed'"
    Completed --> [*]: "onEvent('completed', data)"
    
    Polling --> Error: "status='error'"
    Error --> [*]: "onEvent('error', {code, message})"
    
    Polling --> Canceled: "User cancels"
    Canceled --> [*]: "onEvent('canceled')"
```

**Implementation Details** [src/frontend/platform/src/controllers/API/index.ts:313-461]():
- Uses dual `AbortController` instances for task creation and polling
- Default poll interval: 2000ms (configurable via `options.pollInterval`)
- Returns cancel function to abort requests and clear timers
- Emits events: `'processing'`, `'completed'`, `'error'`, `'canceled'`, `'closed'`
- Validates response format and emits structured errors

**Sources:**
- [src/frontend/platform/src/controllers/API/index.ts:313-461]()

---

## State Management Patterns

The frontend uses a combination of Zustand stores for global state, React Context for dependency injection, and local useState/useRef for component-specific state.

### Zustand Store Architecture

**Diagram: Store Structure with State Slices**

```mermaid
graph TB
    StoreLayer["Zustand Stores"]
    
    StoreLayer --> KnowledgeStore["useKnowledgeStore<br/>Knowledge-specific state"]
    StoreLayer --> DashboardStore["useDashboardStore<br/>Dashboard state"]
    
    KnowledgeStore --> ChunkIndex["selectedChunkIndex: number<br/>Currently selected chunk"]
    KnowledgeStore --> DistanceFactor["selectedChunkDistanceFactor: number<br/>Scroll offset adjustment"]
    KnowledgeStore --> Bbox["selectedBbox: array<br/>Active bbox coordinates"]
    KnowledgeStore --> NeedCover["needCoverData: {index, txt}<br/>Chunk overwrite data"]
    KnowledgeStore --> Editable["isEditable: boolean<br/>User write permission"]
    
    DashboardStore --> EditorStore["useEditorDashboardStore<br/>Editor-specific state"]
    DashboardStore --> ComponentStore["useComponentEditorStore<br/>Component config"]
    
    EditorStore --> CurrentDash["currentDashboard: Dashboard<br/>Active dashboard"]
    EditorStore --> Components["components: Component[]<br/>Layout components"]
    EditorStore --> IsDirty["isDirty: boolean<br/>Unsaved changes flag"]
    
    ComponentStore --> EditingComp["editingComponent: Component<br/>Currently editing"]
    ComponentStore --> CollapsedSections["collapsedSections: object<br/>Panel collapse state"]
    
    PreviewFile["PreviewFile.tsx"] -.->|"read/write"| ChunkIndex
    PreviewParagraph["PreviewParagraph.tsx"] -.->|"read/write"| ChunkIndex
    ComponentDrawer["ComponentConfigDrawer.tsx"] -.->|"read/write"| EditingComp
    DashboardEditor["Dashboard Editor"] -.->|"read/write"| IsDirty
```

**Store Usage Patterns**:
- **Selective Subscriptions**: Components subscribe only to needed state slices using Zustand selectors
- **Action Methods**: Store exposes setter methods like `setSelectedChunkIndex()`, `updateEditingComponent()`
- **Derived State**: Computed values stored in components via `useMemo` rather than in stores

**Sources:**
- [src/frontend/platform/src/pages/KnowledgePage/components/PreviewParagraph.tsx:14-38]() (useKnowledgeStore usage)
- [src/frontend/platform/src/pages/Dashboard/components/config/ComponentConfigDrawer.tsx:14-34]() (dashboard stores)
- [src/frontend/platform/src/pages/Dashboard/components/config/useChartState.tsx:8-30]() (store integration)

### React Context Providers

| Context | Provider | Purpose | Accessed Via |
|---------|----------|---------|--------------|
| `userContext` | Root level | Current user info, permissions | `useContext(userContext)` |
| `locationContext` | Root level | Navigation state, route params | `useContext(locationContext)` |

**Sources:**
- [src/frontend/platform/src/pages/KnowledgePage/KnowledgeFile.tsx:316]() (userContext usage)
- [src/frontend/platform/src/pages/KnowledgePage/components/PreviewParagraph.tsx:5]() (locationContext usage)

### Local State and Ref Patterns

Complex components use `useRef` for values that shouldn't trigger re-renders and `useState` for UI state.

**Common Patterns**:
- **Debounced Updates**: `prevPreviewCountMapRef` prevents duplicate API calls [src/frontend/platform/src/pages/KnowledgePage/components/PreviewResult.tsx:67]()
- **Mutable Flags**: `submittingRef.current` prevents double-submit [src/frontend/platform/src/pages/KnowledgePage/filesUpload.tsx:59]()
- **Cached Data**: `labelsMapTempRef` stores bbox selections per chunk [src/frontend/platform/src/pages/KnowledgePage/components/PreviewFile.tsx:72]()
- **Latest Values**: `latestFileUrlRef` tracks most recent URL without re-renders [src/frontend/platform/src/pages/KnowledgePage/components/Paragraphs.tsx:79]()
- **Component Instances**: `fileUploadStep2Ref` enables parent-to-child method calls [src/frontend/platform/src/pages/KnowledgePage/filesUpload.tsx:57]()

**Sources:**
- [src/frontend/platform/src/pages/KnowledgePage/components/PreviewResult.tsx:67]()
- [src/frontend/platform/src/pages/KnowledgePage/filesUpload.tsx:56-59]()
- [src/frontend/platform/src/pages/KnowledgePage/components/PreviewFile.tsx:71-73]()

---

## File Upload Workflow Architecture

The file upload system implements two distinct multi-step wizards: a 4-step **normal upload flow** (`filesUpload.tsx`) and a 3-step **adjustment flow** (`AdjustFilesUpload.tsx`) for re-segmenting existing files.

### Upload Flow State Machines

**Diagram: Upload Workflow State Transitions**

```mermaid
stateDiagram-v2
    [*] --> NormalUpload: "/filelib/upload/:id"
    [*] --> AdjustMode: "/filelib/adjust/:id"
    
    state NormalUpload {
        Step1: "Step 1: FileUploadStep1<br/>uploadLibFile()"
        Step2: "Step 2: FileUploadStep2<br/>RuleFile + RuleTable"
        Step3: "Step 3: PreviewResult<br/>previewFileSplitApi()"
        Step4: "Step 4: FileUploadStep4<br/>readFileByLibDatabase()"
        
        Step1 --> Step2: "handleStep1Next()"
        Step2 --> Step3: "handleStep2Next()"
        Step3 --> Step4: "subUploadLibFile()"
        Step4 --> [*]: "navigate(-1)"
    }
    
    state AdjustMode {
        Adj1: "Step 1: FileUploadStep2<br/>Pre-filled with split_rule"
        Adj2: "Step 2: PreviewResult<br/>previewFileSplitApi()"
        Adj3: "Step 3: FileUploadStep4<br/>rebUploadFile()"
        
        Adj1 --> Adj2: "handleStep2Next()"
        Adj2 --> Adj3: "rebUploadFile()"
        Adj3 --> [*]: "navigate(-1)"
    }
```

**Key Differences**:
- **Normal Upload**: Starts with file selection (`FileUploadStep1`), uploads files via `uploadLibFile`, processes via `subUploadLibFile`
- **Adjustment Mode**: Skips file selection, pre-fills `FileUploadStep2` with existing `split_rule` from `location.state`, re-processes via `rebUploadFile`

**Sources:**
- [src/frontend/platform/src/pages/KnowledgePage/filesUpload.tsx:17-138]()
- [src/frontend/platform/src/pages/KnowledgePage/AdjustFilesUpload.tsx:16-193]()

### Step 2: Segmentation Strategy Component

`FileUploadStep2.tsx` [src/frontend/platform/src/pages/KnowledgePage/components/FileUploadStep2.tsx:58-323]() handles both document and table file types with different rule configurations. It maintains persistent state across step navigation to preserve user inputs.

#### State Persistence Pattern

**Diagram: Step2 State Management with Persistence**

```mermaid
graph LR
    Parent["filesUpload.tsx<br/>Parent Component"]
    Step2["FileUploadStep2.tsx<br/>Strategy Editor"]
    
    Parent -->|"persistState: Step2PersistState"| Step2
    Step2 -->|"onPersistStateChange(state)"| Parent
    
    Step2 --> RuleFile["RuleFile.tsx<br/>separator, separatorRule"]
    Step2 --> RuleTable["RuleTable.tsx<br/>excel_rule config"]
    
    Step2 --> Preview["PreviewResult.tsx<br/>previewFileSplitApi()"]
    
    subgraph "Step2PersistState"
        rules["rules: {separator, chunkSize,<br/>chunkOverlap, fileList}"]
        strategies["strategies: [{id, regex,<br/>position, rule}]"]
        applyEachCell["applyEachCell: boolean"]
        cellConfig["cellGeneralConfig: {slice_length,<br/>append_header, header_*_row}"]
    end
    
    Step2 -.->|"useEffect sync<br/>lines 111-120"| rules
    Step2 -.->|"useEffect sync"| strategies
```

The parent component stores state via `step2PersistState` [src/frontend/platform/src/pages/KnowledgePage/filesUpload.tsx:54]() and passes it back to Step2 on re-mount via the `persistState` prop [src/frontend/platform/src/pages/KnowledgePage/filesUpload.tsx:345](), preventing data loss when navigating between steps.

**Key Implementation Details**:
- **Dual Rule Systems**: Documents use `separator`/`separator_rule` arrays [src/frontend/platform/src/pages/KnowledgePage/components/FileUploadStep2.tsx:413-425](); tables use `excel_rule` objects with `slice_length`, `append_header`, `header_start_row`, `header_end_row` [src/frontend/platform/src/pages/KnowledgePage/components/FileUploadStep2.tsx:376-383]()
- **Preview Toggle**: `showPreview` state controls side-by-side preview rendering [src/frontend/platform/src/pages/KnowledgePage/components/FileUploadStep2.tsx:65]()
- **Validation**: `vildateCell()` checks for empty separators, chunk overlap > chunk size, invalid header row ranges [src/frontend/platform/src/pages/KnowledgePage/components/FileUploadStep2.tsx:135-151]()
- **Tab Switching**: `displayMode` determines whether to show document tab, table tab, or both [src/frontend/platform/src/pages/KnowledgePage/components/FileUploadStep2.tsx:81-88]()

**Sources:**
- [src/frontend/platform/src/pages/KnowledgePage/components/FileUploadStep2.tsx:28-323]()
- [src/frontend/platform/src/pages/KnowledgePage/filesUpload.tsx:54-65]()
- [src/frontend/platform/src/pages/KnowledgePage/components/FileUploadStep2.tsx:111-120]()

### Step 3: Text Comparison and Preview

`PreviewResult.tsx` [src/frontend/platform/src/pages/KnowledgePage/components/PreviewResult.tsx:18-242]() orchestrates the preview system with four key responsibilities:
1. Calling `previewFileSplitApi()` (polling-based API) with segmentation rules
2. Displaying file selector `<Select>` dropdown for multi-file uploads
3. Rendering `PreviewFile.tsx` (left pane) and `PreviewParagraph.tsx` (right pane)
4. Synchronizing chunk edits with `updatePreviewChunkApi()`

**Preview API Flow**:

**Diagram: Preview Polling Sequence with Backend Interaction**

```mermaid
sequenceDiagram
    participant PR as "PreviewResult.tsx"
    participant API as "previewFileSplitApi()"
    participant Backend as "/api/v1/knowledge/preview"
    participant Poll as "/api/v1/knowledge/preview/status"
    
    PR->>API: "Call with rules, file_list"
    API->>Backend: "POST create preview task"
    Backend-->>API: "{preview_file_id: 'abc123'}"
    
    loop "Every 2s until completed"
        API->>Poll: "GET ?preview_file_id=abc123"
        Poll-->>API: "{status: 'processing'}"
        API->>PR: "onEvent('processing', {})"
    end
    
    Poll-->>API: "{status: 'completed',<br/>data: {chunks, file_url, partitions}}"
    API->>PR: "onEvent('completed', data)"
    PR->>PR: "setChunks(data.chunks)<br/>setFileViewUrl(data.file_url)<br/>setPartitions(data.partitions)"
```

**State Management** [src/frontend/platform/src/pages/KnowledgePage/components/PreviewResult.tsx:38-80]():
- `chunks`: Array of chunk objects with `text`, `chunkIndex`, `bbox` metadata
- `partitions`: Partition data for bbox highlighting (UNS/OCR files)
- `syncChunksSelectId`: Tracks selected file to prevent stale chunk data
- `prevPreviewCountMapRef`: Prevents duplicate API calls via ref caching [src/frontend/platform/src/pages/KnowledgePage/components/PreviewResult.tsx:67]()

**Sources:**
- [src/frontend/platform/src/pages/KnowledgePage/components/PreviewResult.tsx:33-242]()
- [src/frontend/platform/src/controllers/API/index.ts:313-461]()

### Step 4: Processing Status Display

`FileUploadStep4.tsx` [src/frontend/platform/src/pages/KnowledgePage/components/FileUploadStep4.tsx:14-200]() implements a polling mechanism to track file processing status, displaying `ProgressItem` components for each file.

**File Status Transitions**:
- `await` (status=5): Queued, waiting for worker
- `parsing` (status=1 or 4): Being processed by Celery worker
- `end` (status=2): Successfully completed
- `error` (status=3 or 6): Failed or timed out

**Polling Logic** [src/frontend/platform/src/pages/KnowledgePage/components/FileUploadStep4.tsx:50-120]():
1. Maintains `processingRef` Set with file IDs being processed
2. Polls `readFileByLibDatabase()` every 5 seconds with `file_ids` filter
3. Matches results by `file_name.toLowerCase().trim()` for case-insensitive comparison
4. Removes completed/failed files from `processingRef` on status 2, 3, or 6
5. Stops polling when `processingRef.current.size === 0`
6. Displays success dialog when all files complete

**Sources:**
- [src/frontend/platform/src/pages/KnowledgePage/components/FileUploadStep4.tsx:14-200]()

---

## Document Preview and Editing System

The preview system supports multiple file formats (PDF, DOCX, Excel, Markdown, images) with unified bbox-based highlighting for OCR-parsed documents.

### Preview File Type Routing

**Diagram: File Format Routing with Component Mapping**

```mermaid
graph TB
    PreviewFile["PreviewFile.tsx<br/>Format Router + Bbox Manager"]
    
    PreviewFile -->|"suffix='pdf'"| FileView["FileView Component<br/>PDF Canvas Renderer"]
    PreviewFile -->|"suffix='docx'"| DocxPreview["DocxPreview.tsx<br/>DOCX HTML Renderer"]
    PreviewFile -->|"suffix='xlsx/xls/csv'"| ExcelPreview["ExcelPreview.tsx<br/>Spreadsheet Grid"]
    PreviewFile -->|"suffix='txt/md/html'"| TxtViewer["TxtFileViewer.tsx<br/>Text/Markdown Display"]
    PreviewFile -->|"suffix='jpg/png/bmp'"| ImgTag["HTML img element"]
    
    FileView --> Labels["pageLabels: Map<page, Label[]><br/>Bbox coordinate arrays"]
    FileView --> Scroll["calculatedPostion: [page, y]<br/>Auto-scroll to active chunk"]
    FileView --> Select["onSelectLabel(labels)<br/>Click/drag handler"]
    
    Select --> UpdateBbox["setSelectedBbox(bbox)<br/>useKnowledgeStore"]
    UpdateBbox --> CoverButton["Show 'Overwrite Segment'<br/>if labelChange=true"]
```

**File Type Detection Logic** [src/frontend/platform/src/pages/KnowledgePage/components/PreviewFile.tsx:43-66]():
1. Matches `rawFiles` array by `file.id` to get complete metadata
2. Determines `fileParseType`: if `step === 2` use `resultFiles[0].isEtl4lm`, else if `step === 3 && etl` use `etl`, else use `targetFile.fileType`
3. Computes `suffix` from URL extension: `url.split('?')[0].split('/').pop().split('.')[1].toLowerCase()`
4. Identifies `isUnsType`: `fileParseType === 'uns' || targetFile.fileType.includes('uns')`

**Sources:**
- [src/frontend/platform/src/pages/KnowledgePage/components/PreviewFile.tsx:14-210]()
- [src/frontend/platform/src/pages/KnowledgePage/components/PreviewFile.tsx:43-66]()

### Bbox Label Management and Chunk Synchronization

For PDF and UNS-type documents, `PreviewFile.tsx` maintains a `labelsMap` state (Map structure) that synchronizes with chunk selections via the `selectedChunkIndex` Zustand store value.

#### Label Synchronization Flow

**Diagram: Bbox Selection and Chunk Overwrite Flow**

```mermaid
graph TB
    ChunkClick["User clicks chunk N<br/>in PreviewParagraph.tsx"]
    ChunkClick --> SetIndex["setSelectedChunkIndex(N)<br/>useKnowledgeStore"]
    
    SetIndex --> InitLabels["PreviewFile useEffect<br/>line 79-133, depends on<br/>selectedChunkIndex"]
    
    InitLabels --> ParseBbox["Parse chunk.bbox JSON<br/>chunk_bboxes: [{page, bbox: [x, y, w, h]}]"]
    ParseBbox --> MarkActive["Mark matching labels active=true<br/>by id: page-x-y-w-h"]
    
    MarkActive --> RenderLabels["Pass pageLabels prop to FileView<br/>pageLabels: {page: [Label]}"]
    RenderLabels --> Highlight["FileView renders bbox<br/>rectangles on PDF canvas"]
    
    UserSelect["User drags/clicks bbox<br/>on PDF"] --> OnSelectLabel["handleSelectLabels(labels)"]
    OnSelectLabel --> SyncPartID["Sync all labels with same part_id<br/>from labelTextRef.current"]
    OnSelectLabel --> UpdateStore["setSelectedBbox(bbox)<br/>Store in Zustand"]
    
    UpdateStore --> ShowButton["Show 'Overwrite Segment' button<br/>if labelChange=true"]
    ShowButton --> Overwrite["User clicks → handleOvergap()"]
    Overwrite --> Concatenate["Concatenate active label text<br/>with \\n or \\n\\n spacing"]
    Concatenate --> SetNeedCover["setNeedCoverData({index, txt})<br/>Zustand store"]
    SetNeedCover --> ApplyInParagraph["PreviewParagraph reads<br/>needCoverData, calls onChange()"]
```

**Key Functions**:
- **`convertJsonData(partitions)`** [src/frontend/platform/src/pages/KnowledgePage/components/ParagraphEdit.tsx:1-50](): Converts partition object `{id: {text, type, part_id}}` to array `[{id, page, label: [x,y,w,h], active}]`
- **`handleSelectLabels(labels)`** [src/frontend/platform/src/pages/KnowledgePage/components/PreviewFile.tsx:170-206](): Groups selections by `part_id`, updates `labelsMap` state, calls `setSelectedBbox()`
- **`handleOvergap()`** [src/frontend/platform/src/pages/KnowledgePage/components/PreviewFile.tsx:287-320](): Merges active label text with intelligent spacing: uses `\n\n` if label type is `title`, else `\n`

**Sources:**
- [src/frontend/platform/src/pages/KnowledgePage/components/PreviewFile.tsx:79-206]()
- [src/frontend/platform/src/pages/KnowledgePage/components/PreviewFile.tsx:287-320]()
- [src/frontend/platform/src/pages/KnowledgePage/components/ParagraphEdit.tsx:1-50]()

### Chunk Editing Interface

`PreviewParagraph.tsx` [src/frontend/platform/src/pages/KnowledgePage/components/PreviewParagraph.tsx:1-250]() renders the right-side chunk list with inline editing capabilities. Each chunk is an `EditMarkdown` component supporting two editor modes.

#### Editor Mode Toggle

| Mode | Component | Features | Implementation |
|------|-----------|----------|----------------|
| **WYSIWYG** (default) | `VditorEditor` | Instant rendering, Markdown shortcuts, math support (`katex`), toolbar hidden | Uses `Vditor` library [line 12-13]() |
| **Raw Markdown** | `AceEditorCom` | Syntax highlighting, GitHub theme, no gutter, live validation | Uses `react-ace` with `markdown` mode [line 11]() |

**Editor Lifecycle** [src/frontend/platform/src/pages/KnowledgePage/components/PreviewParagraph.tsx:115-230]():
1. User clicks chunk → `setSelectedChunkIndex(index)` → highlights in `PreviewFile`
2. User toggles mode icon → `setEdit(!edit)` → switches between Vditor and Ace components
3. User edits text → `debounced setValue()` (via `useMiniDebounce` hook) → local state update
4. User blurs field → `handleBlur()` → validates non-empty → calls `onChange(chunkIndex, newValue)`
5. Parent (`Paragraphs.tsx` or `PreviewResult.tsx`) calls API → `updateChunkApi()` or `updatePreviewChunkApi()`

**Validation Rules** [src/frontend/platform/src/pages/KnowledgePage/components/PreviewParagraph.tsx:195-210]():
- Empty chunks rejected with error toast: `t('chunkContentCannotBeEmpty')`
- Unchanged chunks skip API call (text comparison after `.trim()`)
- Deleted chunks removed from array, triggering `reload()` in parent

**Sources:**
- [src/frontend/platform/src/pages/KnowledgePage/components/PreviewParagraph.tsx:34-249]()
- [src/frontend/platform/src/pages/KnowledgePage/components/Paragraphs.tsx:209-231]()

---

## State Management Architecture

The knowledge base UI uses a hybrid state management approach: Zustand for cross-component shared state, React hooks for local state, and URL parameters for navigation persistence.

### Zustand Store: `useKnowledgeStore`

```mermaid
graph LR
    Store["useKnowledgeStore<br/>(Zustand)"]
    
    Store --> ChunkIndex["selectedChunkIndex: number<br/>Currently selected chunk"]
    Store --> DistanceFactor["selectedChunkDistanceFactor: number<br/>Scroll adjustment offset"]
    Store --> Bbox["selectedBbox: array<br/>Active bbox coordinates"]
    Store --> NeedCover["needCoverData: {index, txt}<br/>Force chunk overwrite data"]
    Store --> Editable["isEditable: boolean<br/>User write permission"]
    
    PreviewParagraph["PreviewParagraph.tsx"] -.->|"get/set"| ChunkIndex
    PreviewFile["PreviewFile.tsx"] -.->|"get"| ChunkIndex
    PreviewFile -.->|"get"| DistanceFactor
    PreviewFile -.->|"set"| Bbox
    PreviewFile -.->|"set"| NeedCover
    
    Paragraphs["Paragraphs.tsx"] -.->|"get"| Editable
    Files["Files.tsx"] -.->|"set via setEditable()"| Editable
```

**Store Definition** (inferred pattern from usage):
```typescript
interface KnowledgeStore {
  selectedChunkIndex: number;
  setSelectedChunkIndex: (index: number) => void;
  selectedChunkDistanceFactor: number;
  setSelectedChunkDistanceFactor: (factor: number) => void;
  selectedBbox: Array<{page: number, bbox: number[]}>;
  setSelectedBbox: (bbox: Array) => void;
  needCoverData: {index: number, txt: string};
  setNeedCoverData: (data: {index: number, txt: string}) => void;
  isEditable: boolean;
  setEditable: (editable: boolean) => void;
}
```

**Sources:**
- [src/frontend/platform/src/pages/KnowledgePage/components/PreviewParagraph.tsx:259]()
- [src/frontend/platform/src/pages/KnowledgePage/components/PreviewFile.tsx:37-40]()
- [src/frontend/platform/src/pages/KnowledgePage/components/Paragraphs.tsx:32-96]()

### Local State Patterns

Complex components use `useRef` for values that shouldn't trigger re-renders and `useState` for UI state:

**Common Patterns**:
- **Debounced Updates**: `prevPreviewCountMapRef` prevents duplicate API calls [src/frontend/platform/src/pages/KnowledgePage/components/PreviewResult.tsx:67]()
- **Mutable Flags**: `submittingRef.current` prevents double-submit [src/frontend/platform/src/pages/KnowledgePage/filesUpload.tsx:59]()
- **Cached Data**: `labelsMapTempRef` stores bbox selections per chunk [src/frontend/platform/src/pages/KnowledgePage/components/PreviewFile.tsx:72]()
- **Latest Values**: `latestFileUrlRef` tracks most recent URL without causing re-renders [src/frontend/platform/src/pages/KnowledgePage/components/Paragraphs.tsx:79]()

**Sources:**
- [src/frontend/platform/src/pages/KnowledgePage/components/PreviewResult.tsx:67]()
- [src/frontend/platform/src/pages/KnowledgePage/filesUpload.tsx:56-59]()
- [src/frontend/platform/src/pages/KnowledgePage/components/PreviewFile.tsx:71-73]()

---

## API Integration Patterns

The frontend communicates with the backend via a centralized API module that implements polling, SSE-style interfaces, and CRUD operations.

### API Function Categories

```mermaid
graph TB
    API["controllers/API/index.ts"]
    
    subgraph "Knowledge Base CRUD"
        createFileLib["createFileLib(data)<br/>POST /api/v1/knowledge/create"]
        readFileLibDatabase["readFileLibDatabase(params)<br/>GET /api/v1/knowledge"]
        updateKnowledgeApi["updateKnowledgeApi(data)<br/>PUT /api/v1/knowledge"]
        deleteFileLib["deleteFileLib(id)<br/>DELETE /api/v1/knowledge"]
    end
    
    subgraph "File Operations"
        uploadLibFile["uploadLibFile(data, config)<br/>POST /api/v1/knowledge/upload"]
        subUploadLibFile["subUploadLibFile(data)<br/>POST /api/v1/knowledge/process"]
        rebUploadFile["rebUploadFile(data)<br/>POST /rebuild"]
        retryKnowledgeFileApi["retryKnowledgeFileApi(data)<br/>POST /retry"]
        deleteFile["deleteFile(id)<br/>DELETE /file/:id"]
    end
    
    subgraph "Chunk Management"
        getKnowledgeChunkApi["getKnowledgeChunkApi(params)<br/>GET /chunk?file_ids=..."]
        updateChunkApi["updateChunkApi(data)<br/>PUT /chunk"]
        delChunkApi["delChunkApi(data)<br/>DELETE /chunk"]
    end
    
    subgraph "Preview System"
        previewFileSplitApi["previewFileSplitApi(data, onEvent)<br/>POST /preview + Polling"]
        updatePreviewChunkApi["updatePreviewChunkApi(data)<br/>PUT /preview"]
        delChunkInPreviewApi["delChunkInPreviewApi(data)<br/>DELETE /preview"]
    end
    
    subgraph "Metadata"
        addMetadata["addMetadata(kb_id, fields)<br/>POST /add_metadata_fields"]
        updateMetadataFields["updateMetadataFields(kb_id, updates)<br/>PUT /update_metadata_fields"]
        deleteMetadataFields["deleteMetadataFields(kb_id, names)<br/>DELETE /delete_metadata_fields"]
        saveUserMetadataApi["saveUserMetadataApi(file_id, list)<br/>PUT /file/user_metadata"]
    end
    
    API --> createFileLib
    API --> readFileLibDatabase
    API --> uploadLibFile
    API --> previewFileSplitApi
    API --> getKnowledgeChunkApi
    API --> addMetadata
```

**Sources:**
- [src/frontend/platform/src/controllers/API/index.ts:139-531]()

### Preview API Polling Implementation

The `previewFileSplitApi()` function implements a polling-based SSE-like interface that creates a task and polls for status updates.

**Polling State Machine**:

```mermaid
stateDiagram-v2
    [*] --> CreateTask: POST /api/v1/knowledge/preview
    CreateTask --> Polling: Receive preview_file_id
    
    Polling --> Processing: status="processing"
    Processing --> Polling: Continue after 2s
    
    Polling --> Completed: status="completed"
    Completed --> [*]: onEvent('completed', data)
    
    Polling --> Error: status="error"
    Error --> [*]: onEvent('error', {code, message})
    
    Polling --> Canceled: status="canceled"
    Canceled --> [*]: onEvent('canceled')
```

**Implementation Details**:
- Uses two `AbortController` instances: one for task creation, one for polling
- Default poll interval: 2000ms (configurable via `options.pollInterval`)
- Returns cancel function that aborts both controllers and clears timers
- Emits events: `'processing'`, `'completed'`, `'error'`, `'canceled'`, `'closed'`

**Error Handling**:
- Catches `ERR_CANCELED` / `CanceledError` and silently returns
- Falls back to generic error event for network failures
- Validates response format and emits structured error on invalid status

**Sources:**
- [src/frontend/platform/src/controllers/API/index.ts:313-461]()

### Request Error Handling

All API calls are wrapped with `captureAndAlertRequestErrorHoc()`, which:
1. Catches errors from async functions
2. Displays toast notifications with localized error messages
3. Returns `null` on error to allow graceful fallback
4. Supports optional custom error handler as second parameter

**Usage Pattern**:
```typescript
await captureAndAlertRequestErrorHoc(
  deleteFile(id).then(res => {
    reload();
  })
);
```

**Sources:**
- [src/frontend/platform/src/controllers/request.ts]() (referenced but not in provided files)
- [src/frontend/platform/src/pages/KnowledgePage/components/Files.tsx:157-161]()

---

## Metadata Management System

The metadata system allows users to define custom fields for knowledge base files with type validation and built-in field protection.

### Metadata Dialog Architecture

```mermaid
graph TB
    Main["MainMetadataDialog<br/>File-level metadata editor"]
    Side["MetadataSideDialog<br/>Field selector/creator"]
    Manage["MetadataManagementDialog<br/>KB-level field manager"]
    
    Main -->|"Search Fields"| Side
    Main -->|"Add Field"| Side
    
    Side -->|"Create Mode"| AddAPI["addMetadata()<br/>POST /add_metadata_fields"]
    Side -->|"Search Mode"| Select["Select existing field"]
    
    Main -->|"Save Button"| SaveAPI["saveUserMetadataApi()<br/>PUT /file/user_metadata"]
    
    Manage -->|"Create Field"| AddAPI
    Manage -->|"Rename Field"| UpdateAPI["updateMetadataFields()<br/>PUT /update_metadata_fields"]
    Manage -->|"Delete Field"| DeleteAPI["deleteMetadataFields()<br/>DELETE /delete_metadata_fields"]
    
    FileTable["Files.tsx"] -->|"Metadata Button"| Manage
    Paragraphs["Paragraphs.tsx"] -->|"Metadata Button"| Main
```

**Built-in Metadata Fields** (read-only, reserved names):
- `document_id`, `document_name` (String)
- `upload_time`, `update_time` (Time)
- `uploader`, `updater` (String)
- `chunk_index`, `page`, `knowledge_id` (Number)
- `bbox`, `abstract`, `user_metadata` (String)

**Field Naming Rules**:
- Must start with lowercase letter
- Only lowercase letters, digits, underscores allowed: `/^[a-z][a-z0-9_]*$/`
- Maximum length: 255 characters
- Cannot overlap with built-in field names

**Sources:**
- [src/frontend/platform/src/pages/KnowledgePage/components/Paragraphs.tsx:475-509]()
- [src/frontend/platform/src/pages/KnowledgePage/components/MetadataManagementDialog.tsx:31-44]()
- [src/frontend/platform/src/pages/KnowledgePage/components/MetadataManagementDialog.tsx:188-231]()

---

## Internationalization (i18n)

All user-facing text uses `react-i18next` with the `knowledge` namespace. The system supports dynamic language switching and provides context-aware translations.

**Common Translation Keys**:
- File operations: `uploadFile`, `deleteFile`, `retry`, `parseFailed`
- Segmentation: `splitStrategy`, `chunkSize`, `chunkOverlap`, `previewResults`
- Status: `parsing`, `completed`, `failed`, `copying`
- Validation: `nameRequired`, `nameExceedsLimit`, `chunkContentCannotBeEmpty`

**Usage Pattern**:
```typescript
const { t } = useTranslation('knowledge');
<span>{t('chunk')}{data.chunkIndex + 1}</span>
```

**Sources:**
- [src/frontend/platform/src/pages/KnowledgePage/components/PreviewParagraph.tsx:16-28]()
- [src/frontend/platform/src/pages/KnowledgePage/KnowledgeFile.tsx:416-419]()

---

# Page: Backend Services

# Backend Services

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docker/bisheng/config/config.yaml](docker/bisheng/config/config.yaml)
- [src/backend/bisheng/api/services/assistant.py](src/backend/bisheng/api/services/assistant.py)
- [src/backend/bisheng/api/services/flow.py](src/backend/bisheng/api/services/flow.py)
- [src/backend/bisheng/api/services/workflow.py](src/backend/bisheng/api/services/workflow.py)
- [src/backend/bisheng/api/utils.py](src/backend/bisheng/api/utils.py)
- [src/backend/bisheng/api/v1/assistant.py](src/backend/bisheng/api/v1/assistant.py)
- [src/backend/bisheng/api/v1/chat.py](src/backend/bisheng/api/v1/chat.py)
- [src/backend/bisheng/api/v1/endpoints.py](src/backend/bisheng/api/v1/endpoints.py)
- [src/backend/bisheng/api/v1/flows.py](src/backend/bisheng/api/v1/flows.py)
- [src/backend/bisheng/api/v1/mark_task.py](src/backend/bisheng/api/v1/mark_task.py)
- [src/backend/bisheng/api/v1/schema/chat_schema.py](src/backend/bisheng/api/v1/schema/chat_schema.py)
- [src/backend/bisheng/api/v1/schema/mark_schema.py](src/backend/bisheng/api/v1/schema/mark_schema.py)
- [src/backend/bisheng/api/v1/schemas.py](src/backend/bisheng/api/v1/schemas.py)
- [src/backend/bisheng/api/v1/skillcenter.py](src/backend/bisheng/api/v1/skillcenter.py)
- [src/backend/bisheng/api/v1/workflow.py](src/backend/bisheng/api/v1/workflow.py)
- [src/backend/bisheng/database/base.py](src/backend/bisheng/database/base.py)
- [src/backend/bisheng/database/models/assistant.py](src/backend/bisheng/database/models/assistant.py)
- [src/backend/bisheng/database/models/flow.py](src/backend/bisheng/database/models/flow.py)
- [src/backend/bisheng/database/models/flow_version.py](src/backend/bisheng/database/models/flow_version.py)
- [src/backend/bisheng/database/models/mark_app_user.py](src/backend/bisheng/database/models/mark_app_user.py)
- [src/backend/bisheng/database/models/mark_record.py](src/backend/bisheng/database/models/mark_record.py)
- [src/backend/bisheng/database/models/mark_task.py](src/backend/bisheng/database/models/mark_task.py)
- [src/backend/bisheng/database/models/message.py](src/backend/bisheng/database/models/message.py)
- [src/backend/bisheng/database/models/template.py](src/backend/bisheng/database/models/template.py)
- [src/backend/bisheng/database/models/user_link.py](src/backend/bisheng/database/models/user_link.py)
- [src/backend/bisheng/graph/vertex/base.py](src/backend/bisheng/graph/vertex/base.py)
- [src/backend/bisheng/initdb_config.yaml](src/backend/bisheng/initdb_config.yaml)
- [src/backend/bisheng/interface/chains/base.py](src/backend/bisheng/interface/chains/base.py)
- [src/backend/bisheng/interface/chains/custom.py](src/backend/bisheng/interface/chains/custom.py)
- [src/backend/bisheng/interface/initialize/loading.py](src/backend/bisheng/interface/initialize/loading.py)
- [src/backend/bisheng/main.py](src/backend/bisheng/main.py)
- [src/backend/bisheng/template/frontend_node/chains.py](src/backend/bisheng/template/frontend_node/chains.py)
- [src/backend/bisheng/utils/linked_list.py](src/backend/bisheng/utils/linked_list.py)

</details>



This document describes the backend services architecture of the Bisheng platform, including the FastAPI-based synchronous API server and the Celery-based asynchronous worker system. It covers the organization of API endpoints, service layer components, and the separation of synchronous versus asynchronous operations.

For information about data storage systems used by the backend, see [Data Storage Layer](#2.3). For details on specific functional services like Knowledge Base Management or Workflow Engine, see [Core Services](#3).

---

## Architecture Overview

The backend services consist of two primary components running on the same codebase but deployed as separate containers:

1. **FastAPI Backend** - Synchronous HTTP API server on port 7860
2. **Celery Workers** - Asynchronous task processors

Both components share the same Python application code and dependencies but are started with different entry points.

### Backend Services Deployment

```mermaid
graph TB
    subgraph "Backend Container"
        API["FastAPI Server<br/>Port 7860<br/>Entry: entrypoint.sh api"]
        UVICORN["uvicorn<br/>ASGI Server"]
        FASTAPI["FastAPI Application<br/>bisheng.api.*"]
    end
    
    subgraph "Worker Container"
        WORKER["Celery Worker<br/>Entry: entrypoint.sh worker"]
        CELERY["Celery Application<br/>bisheng.worker.main"]
        TASKS["Task Modules<br/>file_worker.py<br/>rebuild_knowledge_worker.py<br/>qa.py"]
    end
    
    subgraph "Shared Infrastructure"
        REDIS["Redis<br/>Port 6379<br/>Task Queue & Cache"]
        MYSQL["MySQL<br/>Port 3306<br/>Application Data"]
    end
    
    API --> UVICORN
    UVICORN --> FASTAPI
    FASTAPI --> REDIS
    FASTAPI --> MYSQL
    
    WORKER --> CELERY
    CELERY --> TASKS
    TASKS --> REDIS
    TASKS --> MYSQL
    
    FASTAPI -.->|"Enqueue Tasks"| REDIS
    REDIS -.->|"Consume Tasks"| CELERY
```

**Sources:** [docker/docker-compose.yml:41-108](), [src/backend/pyproject.toml:1-84]()

The deployment uses a shared Docker image (`dataelement/bisheng-backend`) with different command arguments to start either the API server or worker processes. Both containers mount the same configuration file and data volumes.

---

## API Layer Organization

The API layer is structured as a set of FastAPI routers organized by functional domain. The application supports both v1 and v2 API endpoints, with routers mounted under the `/api` prefix.

### FastAPI Application Structure

The main application is initialized in [src/backend/bisheng/main.py:64-73]() with middleware, exception handlers, and a lifespan context manager for startup/shutdown tasks:

```python
def create_app():
    app = FastAPI(
        default_response_class=ORJSONResponse,
        exception_handlers=_EXCEPTION_HANDLERS,
        lifespan=lifespan,
    )
```

The API routers are registered in [src/backend/bisheng/api/__init__.py]() and include both v1 and v2 versions. The routers are organized as:

```mermaid
graph TB
    subgraph "FastAPI Application"
        MAIN["create_app()<br/>bisheng.main"]
        ROUTER["APIRouter<br/>bisheng.api.router<br/>Prefix: /api"]
    end
    
    subgraph "V1 API Endpoints - bisheng.api.v1.*"
        CHAT_V1["chat.py<br/>Tags: Chat<br/>chat_manager"]
        FLOWS_V1["flows.py<br/>Prefix: /flows<br/>Tags: Flows"]
        WORKFLOW_V1["workflow.py<br/>Prefix: /workflow<br/>Tags: Workflow"]
        ASSISTANT_V1["assistant.py<br/>Prefix: /assistant<br/>Tags: Assistant"]
        ENDPOINTS_V1["endpoints.py<br/>Tags: Base<br/>General utilities"]
        MARK_TASK["mark_task.py<br/>Prefix: /mark<br/>Tags: Mark"]
        SKILLCENTER["skillcenter.py<br/>Prefix: /skill<br/>Tags: Skills"]
    end
    
    subgraph "Service Layer - bisheng.api.services.*"
        ASSISTANT_SVC["AssistantService<br/>assistant.py"]
        WORKFLOW_SVC["WorkFlowService<br/>workflow.py"]
        FLOW_SVC["FlowService<br/>flow.py"]
        BASE_SVC["BaseService<br/>base.py"]
    end
    
    MAIN --> ROUTER
    ROUTER --> CHAT_V1
    ROUTER --> FLOWS_V1
    ROUTER --> WORKFLOW_V1
    ROUTER --> ASSISTANT_V1
    ROUTER --> ENDPOINTS_V1
    ROUTER --> MARK_TASK
    ROUTER --> SKILLCENTER
    
    ASSISTANT_V1 --> ASSISTANT_SVC
    WORKFLOW_V1 --> WORKFLOW_SVC
    FLOWS_V1 --> FLOW_SVC
    ASSISTANT_SVC --> BASE_SVC
    WORKFLOW_SVC --> BASE_SVC
    FLOW_SVC --> BASE_SVC
```

**Sources:** [src/backend/bisheng/main.py:64-73](), [src/backend/bisheng/api/v1/chat.py:49-50](), [src/backend/bisheng/api/v1/flows.py:26](), [src/backend/bisheng/api/v1/workflow.py:32](), [src/backend/bisheng/api/v1/assistant.py:23]()

### Key API Modules and Endpoints

| Module | Prefix/Tags | Key Endpoints | Purpose |
|--------|-------------|---------------|---------|
| `chat.py` | Tags: Chat | `/chat/history`, `/chat/{flow_id}` (WebSocket), `/chat/list` | Session management, message history, WebSocket chat |
| `flows.py` | `/flows` | `POST /`, `GET /{flow_id}`, `PATCH /{flow_id}`, `/versions/*` | Flow/Skill CRUD, version management |
| `workflow.py` | `/workflow` | `POST /create`, `/chat/{workflow_id}` (WebSocket), `/run_once` | Workflow CRUD, execution, status updates |
| `assistant.py` | `/assistant` | `GET /`, `POST /`, `PUT /`, `/chat/{assistant_id}` (WebSocket) | Assistant CRUD, auto-optimization |
| `endpoints.py` | Tags: Base | `/all`, `/env`, `/config`, `/process` | Environment info, configuration, skill execution |
| `mark_task.py` | `/mark` | `/list`, `/create_task`, `/mark` | Annotation task management |
| `skillcenter.py` | `/skill` | `/template/*` | Template management |

**Sources:** [src/backend/bisheng/api/v1/chat.py:49-719](), [src/backend/bisheng/api/v1/flows.py:26-270](), [src/backend/bisheng/api/v1/workflow.py:32-291](), [src/backend/bisheng/api/v1/assistant.py:23-177](), [src/backend/bisheng/api/v1/endpoints.py:46-619](), [src/backend/bisheng/api/v1/mark_task.py:19-261]()

### Response Format Standardization

All API endpoints use a unified response format defined in [src/backend/bisheng/api/v1/schemas.py:69-88]():

```python
class UnifiedResponseModel(BaseModel, Generic[DataT]):
    status_code: int
    status_message: str
    data: DataT = None

def resp_200(data: Union[list, dict, str, Any] = None,
             message: str = 'SUCCESS') -> UnifiedResponseModel:
    return UnifiedResponseModel(status_code=200, status_message=message, data=data)
```

This ensures consistent API responses across all endpoints with a standard structure containing `status_code`, `status_message`, and `data` fields.

**Sources:** [src/backend/bisheng/api/v1/schemas.py:69-88]()

---

## Service Layer Architecture

The service layer provides business logic implementation, separating concerns from API endpoint handlers. Services interact with database models, external systems (Milvus, Elasticsearch, MinIO), and enqueue asynchronous tasks.

### Service Layer Components

The service layer implements business logic and coordinates between API endpoints, database operations, and external systems. Services follow a class-based pattern with `@classmethod` decorators for stateless operations.

```mermaid
graph TB
    subgraph "Core Service Classes"
        BASE_SVC["BaseService<br/>base.py<br/>get_logo_share_link()<br/>get_user_name()"]
        ASSISTANT_SVC["AssistantService<br/>assistant.py<br/>get_assistant()<br/>create_assistant()<br/>update_assistant()<br/>auto_update_stream()"]
        WORKFLOW_SVC["WorkFlowService<br/>workflow.py<br/>get_all_flows()<br/>run_once()<br/>update_flow_status()"]
        FLOW_SVC["FlowService<br/>flow.py<br/>get_version_list_by_flow()<br/>create_new_version()<br/>change_current_version()"]
        AUDIT_SVC["AuditLogService<br/>audit_log.py<br/>create_build_assistant()<br/>delete_chat_flow()"]
    end
    
    subgraph "Assistant Support"
        ASSISTANT_AGENT["AssistantAgent<br/>assistant_agent.py<br/>init_assistant()<br/>optimize_assistant_prompt()"]
        ASSISTANT_BASE["AssistantUtils<br/>assistant_base.py<br/>get_auto_info()<br/>get_auto_tool_info()"]
    end
    
    subgraph "Database Access Objects"
        FLOW_DAO["FlowDao<br/>flow.py<br/>create_flow()<br/>get_flow_by_id()<br/>get_flows()"]
        ASSISTANT_DAO["AssistantDao<br/>assistant.py<br/>get_all_assistants()<br/>create_assistant()"]
        FLOW_VERSION_DAO["FlowVersionDao<br/>flow_version.py<br/>get_version_by_id()<br/>change_current_version()"]
        MESSAGE_DAO["ChatMessageDao<br/>message.py<br/>get_messages_by_chat_id()<br/>insert_one()"]
        SESSION_DAO["MessageSessionDao<br/>session.py<br/>get_one()<br/>filter_session()"]
    end
    
    ASSISTANT_SVC --> BASE_SVC
    WORKFLOW_SVC --> BASE_SVC
    FLOW_SVC --> BASE_SVC
    
    ASSISTANT_SVC --> ASSISTANT_AGENT
    ASSISTANT_SVC --> ASSISTANT_BASE
    ASSISTANT_SVC --> ASSISTANT_DAO
    
    FLOW_SVC --> FLOW_DAO
    FLOW_SVC --> FLOW_VERSION_DAO
    WORKFLOW_SVC --> FLOW_DAO
    
    ASSISTANT_SVC --> AUDIT_SVC
    FLOW_SVC --> AUDIT_SVC
```

**Sources:** [src/backend/bisheng/api/services/assistant.py:39-516](), [src/backend/bisheng/api/services/workflow.py:35-451](), [src/backend/bisheng/api/services/flow.py:38-520](), [src/backend/bisheng/database/models/flow.py:109-685](), [src/backend/bisheng/database/models/assistant.py:65-275]()

### Key Service Methods

The service layer implements core business operations with permission checks, audit logging, and telemetry tracking:

#### AssistantService

The `AssistantService` class in [src/backend/bisheng/api/services/assistant.py:39-516]() manages AI assistant lifecycle:

- `get_assistant()` - Retrieves assistants with role-based access control and tag filtering
- `create_assistant()` - Creates new assistant, auto-generates description, records telemetry
- `update_assistant()` - Updates assistant configuration with permission checks
- `update_status()` - Validates assistant initialization before going online
- `auto_update_stream()` - Generates optimized prompts and auto-selects tools using LLM
- `create_assistant_hook()` - Post-creation logic: group resource binding, audit logging

The service integrates with `AssistantAgent` for LLM-powered features like prompt optimization and tool selection.

**Sources:** [src/backend/bisheng/api/services/assistant.py:39-516]()

#### WorkFlowService

The `WorkFlowService` class in [src/backend/bisheng/api/services/workflow.py:35-451]() handles workflow operations:

- `get_all_flows()` - Returns flows/workflows/assistants with user access filtering
- `run_once()` - Executes single node for testing with `NodeFactory.instance_node()`
- `update_flow_status()` - Changes workflow status, validates initialization on online
- `convert_chat_response_to_workflow_event()` - Transforms chat responses to workflow events
- `get_frequently_used_flows()` - Retrieves user's commonly used applications
- `add_extra_field()` - Enriches flow data with user names, versions, groups, tags

**Sources:** [src/backend/bisheng/api/services/workflow.py:35-451]()

#### FlowService

The `FlowService` class in [src/backend/bisheng/api/services/flow.py:38-520]() manages flow/skill versioning:

- `get_version_list_by_flow()` - Returns all versions for a flow
- `create_new_version()` - Creates new version from current or another version
- `change_current_version()` - Switches active version with permission checks
- `delete_version()` - Removes version (cannot delete current version)
- `update_flow_hook()` - Post-update logic: updates sessions, triggers audit logs

Version management enables A/B testing and rollback capabilities for skills.

**Sources:** [src/backend/bisheng/api/services/flow.py:38-520]()

---

## Synchronous vs Asynchronous Operations

The backend architecture separates operations into synchronous (immediate response) and asynchronous (background processing) patterns.

### Task Dispatch Flow

Asynchronous operations follow a consistent pattern where the API handler enqueues a task and returns immediately, while background workers process the task:

```mermaid
sequenceDiagram
    participant Client
    participant Router as "API Router<br/>chat.py"
    participant Manager as "ChatManager<br/>chat_manager"
    participant Redis as "Redis<br/>flow_data_*"
    participant Worker as "Celery Worker<br/>file_worker.py"
    participant MySQL
    participant Milvus
    
    Client->>Router: POST /build/init/&#123;flow_id&#125;
    Router->>Redis: ahset(flow_data_&#123;flow_id&#125;, graph_data, status=STARTED)
    Router-->>Client: &#123;flowId&#125;
    
    Client->>Router: GET /build/stream/&#123;flow_id&#125;
    Router->>Redis: ahget(flow_data_&#123;flow_id&#125;)
    Router->>Router: build_flow(graph_data)
    Router->>Redis: ahsetkey(status=IN_PROGRESS)
    Router->>Manager: Validate graph nodes
    Router->>Redis: ahsetkey(status=SUCCESS)
    Router-->>Client: SSE stream with input_keys
    
    Client->>Router: WebSocket /chat/&#123;flow_id&#125;
    Router->>Manager: handle_websocket()
    Manager->>Manager: Create ChatClient
    Manager->>MySQL: Load chat history
    Manager-->>Client: WebSocket connected
    
    Note over Worker,Milvus: Background File Processing
    Worker->>MySQL: Get file records
    Worker->>Worker: Parse & chunk document
    Worker->>Milvus: Insert vectors
    Worker->>MySQL: Update status=SUCCESS
```

**Sources:** [src/backend/bisheng/api/v1/chat.py:510-718](), [src/backend/bisheng/api/v1/chat.py:50]()

### Synchronous Operations

Handled directly by FastAPI handlers with immediate responses:

- **CRUD Operations**: Create/Read/Update/Delete for entities (Knowledge, Flow, Assistant)
- **Query Operations**: Listing, filtering, pagination
- **Lightweight Processing**: Preview generation, validation
- **Authentication & Authorization**: User login, permission checks

### Asynchronous Operations

Delegated to Celery workers for background processing:

- **File Processing**: Document parsing, chunking, embedding
- **Vector Operations**: Batch inserts, rebuilding embeddings
- **Heavy Computation**: Knowledge base copying, QA pair processing
- **External API Calls**: ETL4LM document parsing, fine-tuning jobs

---

## Celery Worker System

The worker system uses Celery with Redis as the message broker to handle long-running tasks asynchronously.

### Worker Task Organization

```mermaid
graph TB
    subgraph "Celery Application"
        CELERY_APP["bisheng_celery<br/>bisheng.worker.main"]
    end
    
    subgraph "Task Modules - bisheng.worker.knowledge.*"
        FILE_WORKER["file_worker.py<br/>Tasks:<br/>- parse_knowledge_file_celery<br/>- retry_knowledge_file_celery<br/>- file_copy_celery"]
        REBUILD_WORKER["rebuild_knowledge_worker.py<br/>Tasks:<br/>- rebuild_knowledge_celery"]
        QA_WORKER["qa.py<br/>Tasks:<br/>- insert_qa_celery<br/>- copy_qa_knowledge_celery<br/>- rebuild_qa_knowledge_celery"]
    end
    
    subgraph "Implementation Functions"
        PROCESS_TASK["process_file_task()<br/>knowledge_imp.py"]
        ADD_EMBEDDING["addEmbedding()<br/>knowledge_imp.py"]
        READ_CHUNK["read_chunk_text()<br/>knowledge_imp.py"]
    end
    
    subgraph "External Services"
        ETL4LM["ETL4LM Service<br/>Document Parsing"]
        MILVUS["Milvus<br/>Vector Storage"]
        ES["Elasticsearch<br/>Text Storage"]
    end
    
    CELERY_APP --> FILE_WORKER
    CELERY_APP --> REBUILD_WORKER
    CELERY_APP --> QA_WORKER
    
    FILE_WORKER --> PROCESS_TASK
    PROCESS_TASK --> ADD_EMBEDDING
    ADD_EMBEDDING --> READ_CHUNK
    
    READ_CHUNK --> ETL4LM
    ADD_EMBEDDING --> MILVUS
    ADD_EMBEDDING --> ES
```

**Sources:** [src/backend/bisheng/worker/knowledge/file_worker.py:1-340](), [src/backend/bisheng/worker/knowledge/rebuild_knowledge_worker.py:1-244](), [src/backend/bisheng/worker/knowledge/qa.py:1-150]()

### Key Celery Tasks

| Task Function | Module | Purpose |
|--------------|---------|---------|
| `parse_knowledge_file_celery` | `file_worker.py` | Parse uploaded file, split into chunks, index in Milvus/ES |
| `retry_knowledge_file_celery` | `file_worker.py` | Retry failed file processing with updated parameters |
| `file_copy_celery` | `file_worker.py` | Copy all files from one knowledge base to another |
| `rebuild_knowledge_celery` | `rebuild_knowledge_worker.py` | Rebuild vector embeddings with new model |
| `insert_qa_celery` | `qa.py` | Insert Q&A pair into knowledge base |
| `copy_qa_knowledge_celery` | `qa.py` | Copy Q&A knowledge between knowledge bases |
| `rebuild_qa_knowledge_celery` | `qa.py` | Rebuild Q&A embeddings with new model |

**Sources:** [src/backend/bisheng/worker/knowledge/file_worker.py:244-340](), [src/backend/bisheng/worker/knowledge/rebuild_knowledge_worker.py:22-106](), [src/backend/bisheng/worker/knowledge/qa.py:20-150]()

### Task Execution Pattern

```python
# Example: Knowledge file processing task
@bisheng_celery.task(acks_late=True)
def parse_knowledge_file_celery(file_id: int, preview_cache_key: str, callback_url: str):
    db_file = KnowledgeFileDao.query_by_id(file_id)
    knowledge = KnowledgeDao.query_by_id(db_file.knowledge_id)
    
    process_file_task(
        knowledge=knowledge,
        db_files=[db_file],
        separator=...,
        chunk_size=...,
        preview_cache_keys=[preview_cache_key],
        callback_url=callback_url
    )
```

Tasks are idempotent and handle their own error recovery, updating database status accordingly.

**Sources:** [src/backend/bisheng/worker/knowledge/file_worker.py:244-289]()

---

## Dependency Management

The backend uses Python's `pyproject.toml` for dependency management with a comprehensive set of libraries.

### Core Dependencies

| Category | Key Dependencies | Purpose |
|----------|-----------------|---------|
| **Web Framework** | `fastapi>=0.120.4`, `uvicorn>=0.38.0` | ASGI web server and framework |
| **Async Tasks** | `celery>=5.5.3`, `redis>=7.0.1` | Task queue and message broker |
| **Database** | `sqlmodel>=0.0.27`, `alembic>=1.17.1` | ORM and migrations |
| **Database Drivers** | `pymysql>=1.1.2`, `asyncpg>=0.30.0`, `aiomysql>=0.3.2` | MySQL/PostgreSQL connectivity |
| **Vector Storage** | `pymilvus>=2.5.10`, `langchain-milvus==0.2.1` | Milvus vector database |
| **Search** | `langchain-elasticsearch>=0.4.0` | Elasticsearch integration |
| **Object Storage** | `minio==7.2.18`, `miniopy-async>=1.23.4` | MinIO S3-compatible storage |
| **LangChain** | `langchain>=0.3.23`, `langgraph>=0.3.27` | LLM orchestration framework |
| **LLM Providers** | `langchain-openai>=0.3.16`, `langchain-anthropic>=0.3.10` | LLM integrations |
| **Document Processing** | `pypandoc>=1.15`, `python-docx>=1.2.0`, `pymupdf>=1.26.5` | Document parsing |
| **Authentication** | `pyjwt>=2.10.1` | JWT token handling |

**Sources:** [src/backend/pyproject.toml:8-84]()

### Version Management

The backend version is centrally managed and updated across multiple files:

- **Backend Package**: [src/backend/pyproject.toml:3]() - `version = "2.3.0-beta2"`
- **Python Module**: [src/backend/bisheng/__init__.py:10]() - `__version__ = '2.3.0-beta2'`
- **Docker Images**: [docker/docker-compose.yml:43]() - `image: dataelement/bisheng-backend:v2.3.0-beta2`

Version updates are automated via [update.sh]() script.

**Sources:** [update.sh:1-8](), [src/backend/pyproject.toml:1-4](), [src/backend/bisheng/__init__.py:1-16]()

---

## Deployment Configuration

The backend services are deployed as Docker containers with environment-based configuration.

### Container Configuration

Both backend API and worker containers use the same Docker image with different entry point commands.

#### Backend API Container Configuration

The API server runs uvicorn to serve the FastAPI application:

```yaml
# docker/docker-compose.yml (simplified)
backend:
  container_name: bisheng-backend
  image: dataelement/bisheng-backend:v2.3.0-beta2
  ports:
    - "7860:7860"
  environment:
    BS_MILVUS_CONNECTION_ARGS: '{"host":"milvus","port":"19530",...}'
    BS_ELASTICSEARCH_URL: 'http://elasticsearch:9200'
    BS_MINIO_ENDPOINT: 'minio:9000'
  volumes:
    - ./bisheng/config/config.yaml:/app/bisheng/config.yaml
    - ./data/bisheng:/app/data
  command: sh entrypoint.sh api
```

The `entrypoint.sh api` command starts uvicorn with the FastAPI application defined in [src/backend/bisheng/main.py:64-73]().

**Sources:** [docker/docker-compose.yml:41-77]()

#### Worker Container Configuration

The worker processes Celery tasks using the same codebase:

```yaml
# docker/docker-compose.yml (simplified)
backend_worker:
  container_name: bisheng-backend-worker
  image: dataelement/bisheng-backend:v2.3.0-beta2
  environment:
    # Same environment variables as backend API
  volumes:
    - ./bisheng/config/config.yaml:/app/bisheng/config.yaml
    - ./data/bisheng:/app/data
  command: sh entrypoint.sh worker
```

The `entrypoint.sh worker` command starts Celery workers defined in `bisheng.worker.main`.

**Sources:** [docker/docker-compose.yml:79-108]()

### Configuration File Structure

The backend uses a YAML configuration file with environment variable interpolation. The file is structured as:

```yaml
# docker/bisheng/config/config.yaml
database_url: "mysql+pymysql://root:encrypted_password@mysql:3306/bisheng"
redis_url: "redis://redis:6379/1"
celery_redis_url: "redis://redis:6379/2"

vector_stores:
  milvus:
    connection_args: !env ${BS_MILVUS_CONNECTION_ARGS}
    is_partition: !env ${BS_MILVUS_IS_PARTITION}
  elasticsearch:
    url: !env ${BS_ELASTICSEARCH_URL}

object_storage:
  type: minio
  minio:
    endpoint: !env ${BS_MINIO_ENDPOINT}
    access_key: !env ${BS_MINIO_ACCESS_KEY}
    secret_key: !env ${BS_MINIO_SECRET_KEY}
    public_bucket: 'bisheng'
    tmp_bucket: 'tmp-dir'
```

The `!env ${VAR}` syntax allows environment variables to override configuration values at runtime. This enables different configurations for development, staging, and production environments without modifying the config file.

**Sources:** [docker/bisheng/config/config.yaml:1-88]()

---

## Request Processing Flow

This diagram shows how a typical API request flows through the backend system, including authentication, service layer processing, and database access:

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI as "FastAPI Router<br/>flows.py"
    participant Auth as "UserPayload.get_login_user<br/>user_deps.py"
    participant Service as "FlowService<br/>flow.py"
    participant DAO as "FlowDao<br/>models/flow.py"
    participant MySQL
    participant Redis
    participant Audit as "AuditLogService<br/>audit_log.py"
    
    Client->>FastAPI: PATCH /flows/&#123;flow_id&#125;
    FastAPI->>Auth: Depends(UserPayload.get_login_user)
    Auth->>Redis: Validate JWT from Authorization header
    Redis-->>Auth: Token metadata
    Auth-->>FastAPI: UserPayload(user_id, user_name, ...)
    
    FastAPI->>Service: FlowService.get_one_flow(login_user, flow_id)
    Service->>DAO: FlowDao.aget_flow_by_id(flow_id)
    DAO->>MySQL: SELECT * FROM flow WHERE id=?
    MySQL-->>DAO: Flow record
    DAO-->>Service: Flow model
    
    Service->>Service: login_user.async_access_check(owner_id, flow_id, FLOW_WRITE)
    Service->>Service: Validate status != ONLINE
    Service->>DAO: FlowDao.aupdate_flow(db_flow)
    DAO->>MySQL: UPDATE flow SET ... WHERE id=?
    MySQL-->>DAO: Success
    
    Service->>Audit: AuditLogService.update_build_flow()
    Audit->>MySQL: INSERT INTO auditlog
    
    Service-->>FastAPI: Updated Flow
    FastAPI-->>Client: resp_200(data=flow)
```

**Sources:** [src/backend/bisheng/api/v1/flows.py:126-170](), [src/backend/bisheng/api/services/flow.py:38-520](), [src/backend/bisheng/database/models/flow.py:109-685](), [src/backend/bisheng/common/dependencies/user_deps.py:1-150]()

---

## WebSocket Connections

For real-time interactive features (chat, workflow execution), the backend provides WebSocket endpoints:

```python
# src/backend/bisheng/api/v1/assistant.py:158-177
@router.websocket('/chat/{assistant_id}')
async def chat(
    *,
    assistant_id: str,
    websocket: WebSocket,
    chat_id: Optional[str] = None,
    login_user: UserPayload = Depends(UserPayload.get_login_user_from_ws)
):
    await chat_manager.dispatch_client(
        websocket, assistant_id, chat_id, 
        login_user, WorkType.GPTS, websocket
    )
```

WebSocket connections are managed by `ChatManager` which dispatches to appropriate client handlers based on work type (GPTS, Workflow, etc.).

**Sources:** [src/backend/bisheng/api/v1/assistant.py:158-177](), [src/backend/bisheng/api/v1/workflow.py:136-147]()

---

# Page: Data Storage Layer

# Data Storage Layer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docker/bisheng-ft/config.yaml](docker/bisheng-ft/config.yaml)
- [docker/bisheng-uns/config.yaml](docker/bisheng-uns/config.yaml)
- [docker/docker-compose-ft.yml](docker/docker-compose-ft.yml)
- [docker/docker-compose-office.yml](docker/docker-compose-office.yml)
- [docker/docker-compose-uns.yml](docker/docker-compose-uns.yml)
- [docker/docker-compose.yml](docker/docker-compose.yml)
- [docker/mysql/conf/my.cnf](docker/mysql/conf/my.cnf)
- [docker/nginx/nginx.conf](docker/nginx/nginx.conf)
- [src/backend/bisheng/__init__.py](src/backend/bisheng/__init__.py)
- [src/backend/bisheng/api/services/knowledge.py](src/backend/bisheng/api/services/knowledge.py)
- [src/backend/bisheng/api/services/knowledge_imp.py](src/backend/bisheng/api/services/knowledge_imp.py)
- [src/backend/bisheng/core/cache/redis_conn.py](src/backend/bisheng/core/cache/redis_conn.py)
- [src/backend/bisheng/linsight/domain/task_exec.py](src/backend/bisheng/linsight/domain/task_exec.py)
- [src/backend/bisheng/linsight/domain/utils.py](src/backend/bisheng/linsight/domain/utils.py)
- [src/backend/bisheng/linsight/worker.py](src/backend/bisheng/linsight/worker.py)
- [src/backend/bisheng/template/frontend_node/wrappers.py](src/backend/bisheng/template/frontend_node/wrappers.py)
- [src/backend/bisheng/worker/knowledge/file_worker.py](src/backend/bisheng/worker/knowledge/file_worker.py)
- [src/backend/bisheng/worker/knowledge/qa.py](src/backend/bisheng/worker/knowledge/qa.py)
- [src/backend/bisheng/worker/knowledge/rebuild_knowledge_worker.py](src/backend/bisheng/worker/knowledge/rebuild_knowledge_worker.py)
- [src/backend/pyproject.toml](src/backend/pyproject.toml)
- [update.sh](update.sh)

</details>



## Overview

The Data Storage Layer implements a multi-database architecture where different storage technologies are used for their specialized capabilities. This layer consists of six primary storage systems: MySQL for relational data, Redis for caching and message queuing, Milvus for vector embeddings, Elasticsearch for full-text search, MinIO for object storage, and ETCD for coordination services. Each system is independently scalable and has specific configuration requirements detailed in deployment manifests.

For information about how services interact with these storage systems, see [Backend Services](#2.2). For deployment configuration details, see [Docker Deployment](#5.2).

---

## Storage Services Architecture

```mermaid
graph TB
    subgraph "Application Layer"
        BACKEND["bisheng-backend<br/>FastAPI Server"]
        WORKER["bisheng-backend-worker<br/>Celery Worker"]
        LINSIGHT["Linsight Workers<br/>Multi-process"]
    end
    
    subgraph "Relational Storage"
        MYSQL["mysql:8.0<br/>Container: bisheng-mysql<br/>Port: 3306"]
    end
    
    subgraph "Cache & Queue"
        REDIS["redis:7.0.4<br/>Container: bisheng-redis<br/>Port: 6379"]
    end
    
    subgraph "Vector & Search"
        MILVUS["milvus:v2.5.10<br/>Container: bisheng-milvus-standalone<br/>Port: 19530"]
        ES["elasticsearch:8.12.0<br/>Container: bisheng-es<br/>Port: 9200"]
    end
    
    subgraph "Object Storage"
        MINIO["minio:RELEASE.2023-03-20T20-16-18Z<br/>Container: bisheng-milvus-minio<br/>Port: 9100"]
    end
    
    subgraph "Coordination"
        ETCD["etcd:v3.5.5<br/>Container: bisheng-milvus-etcd<br/>Port: 2379"]
    end
    
    BACKEND --> MYSQL
    BACKEND --> REDIS
    BACKEND --> MILVUS
    BACKEND --> ES
    BACKEND --> MINIO
    
    WORKER --> MYSQL
    WORKER --> REDIS
    WORKER --> MILVUS
    WORKER --> ES
    WORKER --> MINIO
    
    LINSIGHT --> REDIS
    LINSIGHT --> MINIO
    
    MILVUS --> ETCD
    MILVUS --> MINIO
```

**Sources:** [docker/docker-compose.yml:1-201]()

---

## MySQL: Relational Database

### Configuration

MySQL 8.0 is deployed as the primary relational database for structured data storage. The database uses UTF-8MB4 character encoding and strict SQL mode.

| Configuration | Value | Source |
|--------------|-------|--------|
| Container Name | `bisheng-mysql` | docker-compose.yml |
| Image | `mysql:8.0` | docker-compose.yml |
| Port | `3306` | docker-compose.yml |
| Database Name | `bisheng` | docker-compose.yml |
| Character Set | `utf8mb4` | my.cnf |
| Collation | `utf8mb4_unicode_ci` | my.cnf |
| SQL Mode | `STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION` | my.cnf |

**Connection Configuration:**

```python
# Database connection established via SQLModel with async MySQL driver
# Configured in config.yaml: database_url parameter
```

### Data Models

MySQL stores all structured application data through SQLModel ORM:

| Domain | Tables | Examples |
|--------|--------|----------|
| **Knowledge Management** | `Knowledge`, `KnowledgeFile`, `QAKnowledge` | Knowledge base metadata, file tracking, QA pairs |
| **User & Access Control** | `User`, `UserGroup`, `GroupResource`, `Role`, `RoleAccess` | User accounts, group memberships, resource permissions |
| **Workflow & Assistant** | `Flow`, `Assistant`, `AssistantConfig` | Flow definitions, assistant configurations |
| **Chat & Session** | `ChatMessage`, `ChatHistory`, `SessionService` | Message history, chat sessions |
| **Linsight Tasks** | `LinsightSessionVersion`, `LinsightExecuteTask` | Workflow sessions, task execution tracking |
| **Audit & Telemetry** | `AuditLog`, `TelemetryEvent` | System audit trails, usage analytics |

### Connection Management

```mermaid
graph LR
    APP["Application Code"]
    SQLMODEL["SQLModel ORM"]
    AIOMYSQL["aiomysql Driver"]
    MYSQL_DB["MySQL Server"]
    
    APP --> SQLMODEL
    SQLMODEL --> AIOMYSQL
    AIOMYSQL --> MYSQL_DB
    
    SYNC["get_sync_db_session"]
    ASYNC["async database operations"]
    
    SYNC --> SQLMODEL
    ASYNC --> SQLMODEL
```

**Sources:** [docker/docker-compose.yml:2-21](), [docker/mysql/conf/my.cnf:1-13](), [src/backend/pyproject.toml:10]()

---

## Redis: Cache and Queue System

### Redis Client Architecture

Redis provides both caching and message queuing capabilities through a unified `RedisClient` class that supports multiple deployment modes:

```mermaid
graph TB
    subgraph "Client Initialization"
        CONFIG["redis_url Configuration"]
        MODES["Deployment Modes"]
        CONFIG --> MODES
    end
    
    subgraph "Supported Modes"
        SINGLE["Standalone Mode<br/>redis://host:port"]
        CLUSTER["Cluster Mode<br/>startup_nodes list"]
        SENTINEL["Sentinel Mode<br/>sentinel_hosts list"]
    end
    
    MODES --> SINGLE
    MODES --> CLUSTER
    MODES --> SENTINEL
    
    subgraph "Client Implementation"
        REDIS_CLIENT["RedisClient<br/>src/backend/bisheng/core/cache/redis_conn.py"]
        SYNC_CONN["connection<br/>Redis StrictRedis"]
        ASYNC_CONN["async_connection<br/>AsyncRedis"]
    end
    
    SINGLE --> REDIS_CLIENT
    CLUSTER --> REDIS_CLIENT
    SENTINEL --> REDIS_CLIENT
    
    REDIS_CLIENT --> SYNC_CONN
    REDIS_CLIENT --> ASYNC_CONN
    
    subgraph "Access Patterns"
        MANAGER["get_redis_client_sync<br/>get_redis_client"]
        CACHE["Cache Operations<br/>set/get/mset/mget"]
        HASH["Hash Operations<br/>hset/hget/hgetall"]
        LIST["List/Queue Operations<br/>rpush/blpop/lrange"]
    end
    
    MANAGER --> REDIS_CLIENT
    REDIS_CLIENT --> CACHE
    REDIS_CLIENT --> HASH
    REDIS_CLIENT --> LIST
```

### Key Namespaces and Usage

Redis keys follow structured naming conventions for different functional areas:

| Key Pattern | Purpose | Expiration | Code Reference |
|-------------|---------|------------|----------------|
| `preview_file_chunk:{knowledge_id}:{md5}` | File preview cache | Default 3600s | KnowledgeUtils.get_preview_cache_key |
| `file_name:{uuid}` | Uploaded file name mapping | 86400s (1 day) | KnowledgeService.save_upload_file_original_name |
| `linsight:queue` | Linsight task queue | None | LinsightQueue |
| `linsight:node:heartbeat:{node_id}` | Worker node liveness | 15s | NodeManager.start_heartbeat |
| `linsight:task:owner:{session_version_id}` | Task ownership tracking | 86400s | NodeManager.register_task_ownership |
| Session graph cache | Flow execution state | Configurable | SessionService |

### Cache Operations

The `RedisClient` class provides both synchronous and asynchronous methods for all operations:

```mermaid
graph LR
    subgraph "Simple Key-Value"
        SET["set/aset"]
        GET["get/aget"]
        SETEX["setex/asetex"]
        SETNX["setNx/asetNx"]
    end
    
    subgraph "Batch Operations"
        MSET["mset/amset"]
        MGET["mget/amget"]
    end
    
    subgraph "Hash Operations"
        HSET["hset/ahset"]
        HGET["hget/ahget"]
        HGETALL["hgetall/ahgetall"]
        HDEL["hdel/ahdel"]
    end
    
    subgraph "List Operations"
        RPUSH["rpush/arpush"]
        BLPOP["ablpop"]
        LRANGE["alrange"]
        LREM["alrem"]
    end
    
    subgraph "Utilities"
        INCR["incr/aincr"]
        EXPIRE["expire_key/aexpire_key"]
        DELETE["delete/adelete"]
        EXISTS["exists"]
    end
```

All values are automatically pickled/unpickled for Python object storage.

**Sources:** [src/backend/bisheng/core/cache/redis_conn.py:1-433](), [src/backend/bisheng/linsight/worker.py:72-115](), [src/backend/bisheng/api/services/knowledge_imp.py:90-173]()

### Queue Pattern: Linsight Task Processing

The Linsight system uses Redis lists as a distributed task queue:

```mermaid
sequenceDiagram
    participant API as API Endpoint
    participant Queue as LinsightQueue
    participant Redis as Redis List
    participant Worker as ScheduleCenterProcess
    participant Semaphore as asyncio.Semaphore
    
    API->>Queue: put(session_version_id)
    Queue->>Redis: arpush("linsight:queue", data)
    
    loop Worker Poll Loop
        Worker->>Semaphore: acquire()
        Worker->>Queue: get_wait()
        Queue->>Redis: blpop("linsight:queue")
        Redis-->>Queue: session_version_id
        Queue-->>Worker: session_version_id
        Worker->>Worker: create_task(LinsightWorkflowTask)
        Note over Worker: Semaphore released on task completion
    end
```

**Key Implementation Details:**

- **Queue Key:** `linsight:queue` (namespace: "linsight", name: "queue")
- **Operations:** `put()` uses `arpush`, `get_wait()` uses `ablpop` with timeout
- **Concurrency:** Each `ScheduleCenterProcess` has an `asyncio.Semaphore` limiting concurrent tasks
- **Task Ownership:** Workers register ownership with key `linsight:task:owner:{session_version_id}`
- **Heartbeat:** Workers maintain liveness with `linsight:node:heartbeat:{node_id}` (TTL 15s, refresh every 5s)

**Sources:** [src/backend/bisheng/linsight/worker.py:72-215](), [docker/docker-compose.yml:23-39]()

---

## Milvus: Vector Storage

### Architecture and Configuration

Milvus 2.5.10 provides high-performance vector similarity search for embeddings generated from knowledge base documents.

| Configuration | Value | Environment Variable |
|---------------|-------|---------------------|
| Container | `bisheng-milvus-standalone` | - |
| Port | `19530` | - |
| Connection Args | `{"host":"milvus","port":"19530"}` | `BS_MILVUS_CONNECTION_ARGS` |
| Partition Mode | Enabled | `BS_MILVUS_IS_PARTITION=true` |
| Partition Suffix | `1` | `BS_MILVUS_PARTITION_SUFFIX=1` |
| Storage Backend | MinIO | `MINIO_ADDRESS=minio:9000` |
| Metadata Service | ETCD | `ETCD_ENDPOINTS=etcd:2379` |

### Collection Structure

Milvus stores vector embeddings with rich metadata following the `KNOWLEDGE_RAG_METADATA_SCHEMA`:

```mermaid
graph TB
    subgraph "Collection Naming"
        COL_NAME["Collection Name Patterns"]
        SINGLE["col_{uuid}<br/>Single Collection Mode"]
        PARTITION["partition_{suffix}<br/>Partition Key Mode"]
        COL_NAME --> SINGLE
        COL_NAME --> PARTITION
    end
    
    subgraph "Vector Fields"
        VECTOR["vector<br/>Embedding Data<br/>Dimension varies by model"]
        TEXT["text<br/>Chunk Content<br/>with metadata"]
    end
    
    subgraph "Metadata Schema"
        DOC_ID["document_id<br/>File ID"]
        KB_ID["knowledge_id<br/>Knowledge Base ID"]
        SOURCE["source<br/>Document Name"]
        BBOX["bbox<br/>OCR Coordinates"]
        UPLOAD["upload_time<br/>create_time"]
        UPDATE["update_time<br/>update timestamp"]
        UPLOADER["uploader/updater<br/>User Names"]
        USER_META["user_metadata<br/>Custom Fields"]
    end
    
    VECTOR --> DOC_ID
    VECTOR --> KB_ID
    TEXT --> DOC_ID
    TEXT --> KB_ID
    
    DOC_ID --> SOURCE
    KB_ID --> BBOX
    SOURCE --> UPLOAD
    BBOX --> UPDATE
    UPLOAD --> UPLOADER
    UPDATE --> USER_META
```

### Vector Operations

Key Milvus operations in the codebase:

| Operation | Code Location | Purpose |
|-----------|--------------|---------|
| **Collection Creation** | `KnowledgeRag.init_knowledge_milvus_vectorstore_sync` | Initialize vector store with embedding model |
| **Insert Vectors** | `vector_client.add_texts(texts, metadatas)` | Add document chunks with embeddings |
| **Query by Metadata** | `col.query(expr="document_id==X")` | Retrieve vectors by file ID |
| **Delete by Expression** | `col.delete(expr="document_id in [...]")` | Remove file vectors |
| **Partition Key Access** | `param["partition_key"] = knowledge_id` | Route queries to specific partition |

**Initialization Pattern:**

```python
# From knowledge_imp.py:307-308
vector_client = KnowledgeRag.init_knowledge_milvus_vectorstore_sync(
    user_id=0,
    knowledge=knowledge,
    metadata_schemas=KNOWLEDGE_RAG_METADATA_SCHEMA
)
```

### Data Flow: File to Vector

```mermaid
sequenceDiagram
    participant User
    participant API as KnowledgeService
    participant Worker as Celery Worker
    participant Parser as read_chunk_text
    participant Embedding as Embedding Model
    participant Milvus as Milvus Collection
    participant MinIO as MinIO Storage
    
    User->>API: Upload file
    API->>MinIO: put_object_sync(file)
    API->>MySQL: INSERT KnowledgeFile
    API->>Worker: parse_knowledge_file_celery.delay(file_id)
    
    Worker->>MinIO: Download file
    Worker->>Parser: read_chunk_text()
    Parser-->>Worker: texts[], metadatas[]
    
    Worker->>Worker: Aggregate metadata into chunks
    Note over Worker: KnowledgeUtils.aggregate_chunk_metadata
    
    Worker->>Embedding: embed_texts(texts)
    Embedding-->>Worker: vectors[]
    
    Worker->>Milvus: add_texts(texts, metadatas)
    Note over Milvus: Embeddings computed automatically<br/>by langchain-milvus integration
    Milvus->>MinIO: Store vectors
    Milvus->>ETCD: Update metadata
    
    Worker->>MySQL: UPDATE status=SUCCESS
```

**Sources:** [src/backend/bisheng/api/services/knowledge_imp.py:301-324, 438-661](), [src/backend/bisheng/worker/knowledge/file_worker.py:167-248](), [docker/docker-compose.yml:176-200]()

---

## Elasticsearch: Full-Text Search

### Configuration

Elasticsearch 8.12.0 provides keyword-based search capabilities complementing Milvus vector search for hybrid retrieval strategies.

| Configuration | Value | Environment Variable |
|---------------|-------|---------------------|
| Container | `bisheng-es` | - |
| Port | `9200` (HTTP), `9300` (Transport) | - |
| Connection URL | `http://elasticsearch:9200` | `BS_ELASTICSEARCH_URL` |
| SSL Verification | Configurable | `BS_ELASTICSEARCH_SSL_VERIFY` |
| Index Naming | Matches Milvus collection names | `knowledge.index_name` |

### Index Structure

Elasticsearch indices mirror the metadata structure of Milvus collections:

```mermaid
graph TB
    subgraph "Index Document"
        TEXT["text<br/>Full Document Text"]
        METADATA["metadata Object"]
    end
    
    subgraph "Metadata Fields"
        DOC_ID["document_id"]
        KB_ID["knowledge_id"]
        SOURCE["source"]
        BBOX["bbox"]
        TIMES["upload_time<br/>update_time"]
        USERS["uploader<br/>updater"]
    end
    
    TEXT --> METADATA
    METADATA --> DOC_ID
    METADATA --> KB_ID
    METADATA --> SOURCE
    METADATA --> BBOX
    METADATA --> TIMES
    METADATA --> USERS
```

### Key Operations

| Operation | Code Pattern | Purpose |
|-----------|-------------|---------|
| **Create Index** | `es_client._store._create_index_if_not_exists()` | Initialize index with mapping |
| **Add Documents** | `es_client.add_texts(texts, metadatas)` | Index text chunks |
| **Search by Metadata** | `es_client.client.search(query={"term": {...}})` | Filter documents |
| **Delete by Query** | `es_client.client.delete_by_query(query={"terms": {...}})` | Remove documents |
| **Refresh Index** | `es_client.client.indices.refresh(index=...)` | Make changes visible |

**Deletion Pattern (from knowledge_imp.py):**

```python
# Delete vectors by file IDs
res = es_client.client.delete_by_query(
    index=knowledge.index_name,
    query={"terms": {"metadata.document_id": file_ids}},
)
```

### Hybrid Search Strategy

The system uses both Milvus and Elasticsearch for complementary search capabilities:

- **Milvus:** Semantic similarity via vector embeddings
- **Elasticsearch:** Keyword matching, exact phrase search
- **Combined:** Results merged based on relevance scores

**Sources:** [src/backend/bisheng/api/services/knowledge_imp.py:311-323, 375-399](), [src/backend/bisheng/worker/knowledge/rebuild_knowledge_worker.py:108-133](), [docker/docker-compose.yml:124-136]()

---

## MinIO: Object Storage

### Configuration and Bucket Structure

MinIO provides S3-compatible object storage for files, images, and documents.

| Configuration | Value | Environment Variable |
|---------------|-------|---------------------|
| Container | `bisheng-milvus-minio` | - |
| API Port | `9100` (mapped from 9000) | - |
| Console Port | `9101` (mapped from 9001) | - |
| Access Key | `minioadmin` | `BS_MINIO_ACCESS_KEY` |
| Secret Key | `minioadmin` | `BS_MINIO_SECRET_KEY` |
| Schema | HTTP (development) | `BS_MINIO_SCHEMA=false` |
| Endpoint | `minio:9000` | `BS_MINIO_ENDPOINT` |
| Share Point | `minio:9000` | `BS_MINIO_SHAREPOINT` |

### Bucket Organization

MinIO uses a single primary bucket with structured object naming:

```mermaid
graph TB
    BUCKET["Main Bucket<br/>bisheng"]
    TMP_BUCKET["Temporary Bucket<br/>bisheng-tmp"]
    
    subgraph "Object Name Patterns"
        ORIGINAL["original/{file_id}.{ext}<br/>Source Files"]
        PARTITIONS["partitions/{file_id}.json<br/>OCR Bounding Boxes"]
        PREVIEW["preview/{file_id}.{ext}<br/>Converted Preview Files"]
        IMAGES["knowledge/images/{kb_id}/{doc_id}/*<br/>Extracted Images"]
        LINSIGHT_SESSION["linsight/session_files/{session_id}/*<br/>Workflow Files"]
        LINSIGHT_RESULT["linsight/final_result/{session_id}/*<br/>Output Files"]
        LINSIGHT_STEP["linsight/step_event/{session_id}/*<br/>Intermediate Files"]
    end
    
    BUCKET --> ORIGINAL
    BUCKET --> PARTITIONS
    BUCKET --> PREVIEW
    BUCKET --> IMAGES
    BUCKET --> LINSIGHT_SESSION
    BUCKET --> LINSIGHT_RESULT
    BUCKET --> LINSIGHT_STEP
    
    TMP_BUCKET --> TMP_PREVIEW["preview/*<br/>Temporary Conversions"]
```

### Storage Manager Implementation

The `MinioStorageManager` provides both sync and async operations:

| Method | Purpose | Example Usage |
|--------|---------|---------------|
| `put_object_sync/put_object` | Upload file | Store uploaded knowledge base files |
| `get_share_link_sync/get_share_link` | Generate presigned URL | Provide download links |
| `copy_object_sync/copy_object` | Copy between objects | Move tmp to permanent storage |
| `remove_object_sync/remove_object` | Delete object | Clean up deleted files |
| `object_exists_sync/object_exists` | Check existence | Verify file before operations |

**Path Helper Functions (from KnowledgeUtils):**

```python
# Get object name for source file
KnowledgeUtils.get_knowledge_file_object_name(file_id, file_name)
# Returns: "original/{file_id}.{ext}"

# Get bbox partition file
KnowledgeUtils.get_knowledge_bbox_file_object_name(file_id)
# Returns: "partitions/{file_id}.json"

# Get preview file path
KnowledgeUtils.get_knowledge_preview_file_object_name(file_id, file_name)
# Returns: "preview/{file_id}.docx" or "preview/{file_id}.pdf"

# Get image directory
KnowledgeUtils.get_knowledge_file_image_dir(doc_id, knowledge_id)
# Returns: "knowledge/images/{knowledge_id}/{doc_id}"
```

### Integration with Milvus

MinIO serves as the persistent storage backend for Milvus vector data:

```mermaid
graph LR
    MILVUS["Milvus Standalone"]
    MINIO["MinIO Storage"]
    ETCD["ETCD Metadata"]
    
    MILVUS -->|"Write Vectors"| MINIO
    MILVUS -->|"Update Metadata"| ETCD
    MILVUS -->|"Read Vectors"| MINIO
    
    MINIO_DATA["MinIO Data:<br/>/milvus_data/files/<br/>Segment Files"]
    MINIO --> MINIO_DATA
```

**Sources:** [src/backend/bisheng/api/services/knowledge_imp.py:184-217, 220-250, 327-349](), [src/backend/bisheng/linsight/domain/utils.py:58-98](), [docker/docker-compose.yml:156-174]()

---

## ETCD: Coordination Service

### Configuration

ETCD v3.5.5 provides distributed coordination for Milvus cluster management.

| Configuration | Value | Purpose |
|---------------|-------|---------|
| Container | `bisheng-milvus-etcd` | - |
| Port | `2379` (client) | - |
| Endpoint | `etcd:2379` | Milvus connection |
| Auto Compaction | Revision mode, retain 1000 | Prevent database growth |
| Backend Quota | 4GB | Storage limit |
| Snapshot Count | 50000 | Checkpoint frequency |

### Role in Milvus

ETCD stores Milvus cluster metadata:

- Collection schemas and configurations
- Index definitions and build status
- Segment metadata and locations
- Cluster node registration
- Coordination for distributed operations

```mermaid
graph TB
    MILVUS["Milvus Standalone"]
    ETCD["ETCD Service"]
    
    subgraph "Metadata Types"
        COLLECTIONS["Collection Definitions"]
        SEGMENTS["Segment Information"]
        INDEXES["Index Configurations"]
        NODES["Node Registry"]
    end
    
    MILVUS -->|"Register/Update"| ETCD
    ETCD -->|"Store"| COLLECTIONS
    ETCD -->|"Store"| SEGMENTS
    ETCD -->|"Store"| INDEXES
    ETCD -->|"Store"| NODES
    
    MILVUS -->|"Query Metadata"| ETCD
```

**Health Check:** `etcdctl endpoint health`

**Sources:** [docker/docker-compose.yml:137-154]()

---

## Data Flow Patterns

### Knowledge Base File Processing

Complete data flow from upload to searchable vectors:

```mermaid
graph TB
    START["User Uploads File"]
    
    subgraph "Storage Phase"
        MINIO_UPLOAD["MinIO: Store original file<br/>original/{file_id}.{ext}"]
        MYSQL_RECORD["MySQL: INSERT KnowledgeFile<br/>status=WAITING"]
    end
    
    subgraph "Processing Phase"
        CELERY["Celery: parse_knowledge_file_celery"]
        DOWNLOAD["MinIO: Download file"]
        PARSE["Parser: Extract text + metadata"]
        CHUNK["Split into chunks"]
        TITLE["LLM: Extract titles (optional)"]
        AGGREGATE["Aggregate chunk metadata"]
    end
    
    subgraph "Vector Storage Phase"
        EMBED["Embedding Model: Generate vectors"]
        MILVUS_INSERT["Milvus: add_texts()<br/>Store vectors + metadata"]
        ES_INSERT["Elasticsearch: add_texts()<br/>Index text + metadata"]
        BBOX_UPLOAD["MinIO: Upload bbox JSON<br/>partitions/{file_id}.json"]
    end
    
    subgraph "Completion Phase"
        UPDATE_STATUS["MySQL: UPDATE status=SUCCESS"]
        CACHE_CLEAR["Redis: Delete preview cache"]
    end
    
    START --> MINIO_UPLOAD
    MINIO_UPLOAD --> MYSQL_RECORD
    MYSQL_RECORD --> CELERY
    
    CELERY --> DOWNLOAD
    DOWNLOAD --> PARSE
    PARSE --> CHUNK
    CHUNK --> TITLE
    TITLE --> AGGREGATE
    
    AGGREGATE --> EMBED
    EMBED --> MILVUS_INSERT
    EMBED --> ES_INSERT
    EMBED --> BBOX_UPLOAD
    
    MILVUS_INSERT --> UPDATE_STATUS
    ES_INSERT --> UPDATE_STATUS
    BBOX_UPLOAD --> UPDATE_STATUS
    UPDATE_STATUS --> CACHE_CLEAR
    
    MILVUS_INSERT -.->|"Backend Storage"| MINIO_VECTORS["MinIO: Vector data"]
    MILVUS_INSERT -.->|"Metadata"| ETCD_META["ETCD: Collection info"]
```

### Linsight Task Execution

Distributed workflow task processing with Redis queue coordination:

```mermaid
graph TB
    USER["User Submits Task"]
    
    subgraph "Task Queue"
        ENQUEUE["Redis: rpush linsight:queue"]
        OWNERSHIP["Redis: set task:owner:{session_id}"]
    end
    
    subgraph "Worker Lifecycle"
        HEARTBEAT["Redis: Node heartbeat<br/>TTL 15s, refresh 5s"]
        DEQUEUE["Redis: blpop linsight:queue"]
        ACQUIRE["Semaphore: acquire()"]
    end
    
    subgraph "File Management"
        DOWNLOAD["MinIO: Download input files"]
        WORKSPACE["Local: Create workspace"]
        EXECUTE["Execute workflow tasks"]
        UPLOAD_STEP["MinIO: Upload step files<br/>linsight/step_event/*"]
        UPLOAD_FINAL["MinIO: Upload results<br/>linsight/final_result/*"]
    end
    
    subgraph "State Tracking"
        MYSQL_SESSION["MySQL: LinsightSessionVersion<br/>status=IN_PROGRESS"]
        MYSQL_TASKS["MySQL: LinsightExecuteTask<br/>status per task"]
        REDIS_STATE["Redis: Session state cache"]
    end
    
    subgraph "Completion"
        RELEASE["Semaphore: release()"]
        CLEANUP["Delete workspace"]
        UPDATE_STATUS["MySQL: Update status"]
    end
    
    USER --> ENQUEUE
    ENQUEUE --> OWNERSHIP
    
    HEARTBEAT --> DEQUEUE
    DEQUEUE --> ACQUIRE
    ACQUIRE --> DOWNLOAD
    
    DOWNLOAD --> WORKSPACE
    WORKSPACE --> EXECUTE
    
    EXECUTE --> UPLOAD_STEP
    EXECUTE --> UPLOAD_FINAL
    UPLOAD_FINAL --> UPDATE_STATUS
    
    MYSQL_SESSION -.-> EXECUTE
    MYSQL_TASKS -.-> EXECUTE
    REDIS_STATE -.-> EXECUTE
    
    UPDATE_STATUS --> RELEASE
    RELEASE --> CLEANUP
```

**Sources:** [src/backend/bisheng/api/services/knowledge_imp.py:252-661](), [src/backend/bisheng/linsight/domain/task_exec.py:105-163](), [src/backend/bisheng/linsight/domain/utils.py:34-98]()

---

## Connection Configuration Summary

All storage connections are configured through environment variables in `docker-compose.yml` and backend configuration files:

| Storage | Connection String | Configuration Location |
|---------|------------------|------------------------|
| **MySQL** | `mysql+aiomysql://root:1234@mysql:3306/bisheng` | `config.yaml`: `database_url` |
| **Redis** | `redis://redis:6379/0` (or cluster/sentinel config) | `config.yaml`: `redis` |
| **Milvus** | `{"host":"milvus","port":"19530"}` | ENV: `BS_MILVUS_CONNECTION_ARGS` |
| **Elasticsearch** | `http://elasticsearch:9200` | ENV: `BS_ELASTICSEARCH_URL` |
| **MinIO** | `http://minio:9000` | ENV: `BS_MINIO_ENDPOINT` |
| **ETCD** | `etcd:2379` | Milvus internal |

All storage systems support health checks for orchestrated startup:

- MySQL: `mysql -u root -p$MYSQL_ROOT_PASSWORD`
- Redis: `redis-cli ping`
- Milvus: `curl http://localhost:9091/healthz`
- Elasticsearch: Bitnami health endpoint
- MinIO: `curl http://localhost:9000/minio/health/live`
- ETCD: `etcdctl endpoint health`

**Sources:** [docker/docker-compose.yml:1-201](), [src/backend/pyproject.toml:8-86]()

---

# Page: Core Services

# Core Services

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/backend/bisheng/api/services/assistant.py](src/backend/bisheng/api/services/assistant.py)
- [src/backend/bisheng/api/services/flow.py](src/backend/bisheng/api/services/flow.py)
- [src/backend/bisheng/api/services/knowledge.py](src/backend/bisheng/api/services/knowledge.py)
- [src/backend/bisheng/api/services/knowledge_imp.py](src/backend/bisheng/api/services/knowledge_imp.py)
- [src/backend/bisheng/api/services/workflow.py](src/backend/bisheng/api/services/workflow.py)
- [src/backend/bisheng/api/v1/assistant.py](src/backend/bisheng/api/v1/assistant.py)
- [src/backend/bisheng/api/v1/chat.py](src/backend/bisheng/api/v1/chat.py)
- [src/backend/bisheng/api/v1/flows.py](src/backend/bisheng/api/v1/flows.py)
- [src/backend/bisheng/api/v1/mark_task.py](src/backend/bisheng/api/v1/mark_task.py)
- [src/backend/bisheng/api/v1/schema/chat_schema.py](src/backend/bisheng/api/v1/schema/chat_schema.py)
- [src/backend/bisheng/api/v1/schema/mark_schema.py](src/backend/bisheng/api/v1/schema/mark_schema.py)
- [src/backend/bisheng/api/v1/schemas.py](src/backend/bisheng/api/v1/schemas.py)
- [src/backend/bisheng/api/v1/skillcenter.py](src/backend/bisheng/api/v1/skillcenter.py)
- [src/backend/bisheng/api/v1/workflow.py](src/backend/bisheng/api/v1/workflow.py)
- [src/backend/bisheng/database/models/assistant.py](src/backend/bisheng/database/models/assistant.py)
- [src/backend/bisheng/database/models/flow.py](src/backend/bisheng/database/models/flow.py)
- [src/backend/bisheng/database/models/flow_version.py](src/backend/bisheng/database/models/flow_version.py)
- [src/backend/bisheng/database/models/mark_app_user.py](src/backend/bisheng/database/models/mark_app_user.py)
- [src/backend/bisheng/database/models/mark_record.py](src/backend/bisheng/database/models/mark_record.py)
- [src/backend/bisheng/database/models/mark_task.py](src/backend/bisheng/database/models/mark_task.py)
- [src/backend/bisheng/database/models/message.py](src/backend/bisheng/database/models/message.py)
- [src/backend/bisheng/database/models/template.py](src/backend/bisheng/database/models/template.py)
- [src/backend/bisheng/database/models/user_link.py](src/backend/bisheng/database/models/user_link.py)
- [src/backend/bisheng/utils/linked_list.py](src/backend/bisheng/utils/linked_list.py)
- [src/backend/bisheng/worker/knowledge/file_worker.py](src/backend/bisheng/worker/knowledge/file_worker.py)
- [src/backend/bisheng/worker/knowledge/qa.py](src/backend/bisheng/worker/knowledge/qa.py)
- [src/backend/bisheng/worker/knowledge/rebuild_knowledge_worker.py](src/backend/bisheng/worker/knowledge/rebuild_knowledge_worker.py)

</details>



## Purpose and Scope

This document provides an overview of the major functional services that comprise Bisheng's core capabilities. These services are implemented as distinct service classes and DAO (Data Access Object) layers that orchestrate business logic, data persistence, and system integrations.

The services covered here include:
- **Knowledge Base Management** - file upload, processing, chunking, embedding, and vector storage
- **Chat and Messaging System** - real-time WebSocket communication, message persistence, and session management
- **Assistant System** - AI assistant configuration, tool/knowledge/skill integration, and agent orchestration
- **Workflow Engine** - node-based visual programming with typed inputs/outputs
- **Marking and Annotation** - session review workflows and quality assurance tasks
- **Flow and Skill Management** - application lifecycle, versioning, and permission management

For implementation details of specific execution engines (AssistantAgent, Workflow, Linsight), see [Assistant System](#3.3), [Linsight AI Workbench](#3.4), and [Workflow Engine](#3.5). For data storage architecture, see [Data Storage Layer](#2.3). For frontend UI patterns, see [Frontend Architecture](#2.1).

---

## Service Architecture Overview

The following diagram shows how the core services relate to each other and the data layer:

```mermaid
graph TB
    subgraph "API Layer"
        ChatAPI["/chat endpoints<br/>chat.py"]
        KnowledgeAPI["/knowledge endpoints<br/>knowledge.py"]
        AssistantAPI["/assistant endpoints<br/>assistant.py"]
        WorkflowAPI["/workflow endpoints<br/>workflow.py"]
        FlowAPI["/flows endpoints<br/>flows.py"]
        MarkAPI["/mark endpoints<br/>mark_task.py"]
    end
    
    subgraph "Service Layer"
        KnowledgeService["KnowledgeService<br/>knowledge.py"]
        ChatManager["ChatManager<br/>chat_manager.py"]
        AssistantService["AssistantService<br/>assistant.py"]
        WorkFlowService["WorkFlowService<br/>workflow.py"]
        FlowService["FlowService<br/>flow.py"]
    end
    
    subgraph "DAO Layer"
        KnowledgeDao["KnowledgeDao<br/>KnowledgeFileDao"]
        MessageSessionDao["MessageSessionDao<br/>ChatMessageDao"]
        AssistantDao["AssistantDao<br/>AssistantLinkDao"]
        FlowDao["FlowDao<br/>FlowVersionDao"]
        MarkTaskDao["MarkTaskDao<br/>MarkRecordDao"]
    end
    
    subgraph "Processing Layer"
        KnowledgeWorker["Celery Workers<br/>file_worker.py"]
        KnowledgeImp["process_file_task<br/>knowledge_imp.py"]
    end
    
    subgraph "Data Storage"
        MySQL[(MySQL)]
        Milvus[(Milvus)]
        ES[(Elasticsearch)]
        Redis[(Redis)]
        MinIO[(MinIO)]
    end
    
    ChatAPI --> ChatManager
    KnowledgeAPI --> KnowledgeService
    AssistantAPI --> AssistantService
    WorkflowAPI --> WorkFlowService
    FlowAPI --> FlowService
    MarkAPI --> MarkTaskDao
    
    KnowledgeService --> KnowledgeDao
    KnowledgeService --> KnowledgeWorker
    ChatManager --> MessageSessionDao
    AssistantService --> AssistantDao
    WorkFlowService --> FlowDao
    FlowService --> FlowDao
    
    KnowledgeWorker --> KnowledgeImp
    
    KnowledgeDao --> MySQL
    KnowledgeImp --> Milvus
    KnowledgeImp --> ES
    KnowledgeImp --> MinIO
    MessageSessionDao --> MySQL
    MessageSessionDao --> Redis
    AssistantDao --> MySQL
    FlowDao --> MySQL
    MarkTaskDao --> MySQL
```

**Sources:** 
- [src/backend/bisheng/api/v1/chat.py:1-565]()
- [src/backend/bisheng/api/services/knowledge.py:1-1000]()
- [src/backend/bisheng/api/services/assistant.py:1-450]()
- [src/backend/bisheng/api/services/workflow.py:1-363]()
- [src/backend/bisheng/api/services/flow.py:1-350]()

---

## Knowledge Base Management

The Knowledge Base Management service handles the complete lifecycle of document ingestion, processing, chunking, embedding, and retrieval.

### Service Architecture

| Component | File | Key Classes | Responsibility |
|-----------|------|-------------|----------------|
| **Service Layer** | `knowledge.py` | `KnowledgeService` | Orchestrates knowledge base operations, authorization checks |
| **Implementation Layer** | `knowledge_imp.py` | `KnowledgeUtils`, `addEmbedding()`, `process_file_task()` | File parsing, chunking, embedding logic |
| **Worker Layer** | `file_worker.py` | `parse_knowledge_file_celery()` | Asynchronous Celery tasks for file processing |
| **DAO Layer** | `knowledge.py` (domain) | `KnowledgeDao`, `KnowledgeFileDao` | Database CRUD operations |

### Key Operations

#### Creating a Knowledge Base

The `KnowledgeService.create_knowledge()` method handles knowledge base creation:

```mermaid
sequenceDiagram
    participant User
    participant KnowledgeService
    participant KnowledgeDao
    participant Milvus
    participant ES
    
    User->>KnowledgeService: create_knowledge(name, model, ...)
    KnowledgeService->>KnowledgeService: Validate embedding model
    KnowledgeService->>KnowledgeService: generate_knowledge_index_name()
    KnowledgeService->>KnowledgeDao: insert_one(knowledge)
    KnowledgeDao-->>KnowledgeService: db_knowledge
    KnowledgeService->>Milvus: init_knowledge_milvus_vectorstore_sync()
    KnowledgeService->>ES: init_knowledge_es_vectorstore_sync()
    KnowledgeService->>KnowledgeService: create_knowledge_hook()
    KnowledgeService-->>User: Knowledge created
```

**Sources:** [src/backend/bisheng/api/services/knowledge.py:156-199]()

#### File Upload and Processing

File processing follows an asynchronous pipeline:

1. **Upload Phase** - `save_knowledge_file()` uploads files to MinIO and creates database records with `WAITING` status
2. **Async Processing** - Celery task `parse_knowledge_file_celery()` downloads file, parses content, chunks text, embeds to Milvus/ES
3. **Preview/Edit** - Users can preview chunks via `get_preview_file_chunk()` and edit via `update_preview_file_chunk()`
4. **Finalization** - Status updates to `SUCCESS` or `FAILED`

The main processing function is `process_file_task()` in [src/backend/bisheng/api/services/knowledge_imp.py:252-298]():

```python
def process_file_task(
    knowledge: Knowledge,
    db_files: List[KnowledgeFile],
    separator: List[str],
    separator_rule: List[str],
    chunk_size: int,
    chunk_overlap: int,
    callback_url: str = None,
    extra_metadata: Dict = None,
    preview_cache_keys: List[str] = None,
    ...
)
```

**Sources:** 
- [src/backend/bisheng/api/services/knowledge.py:511-591]()
- [src/backend/bisheng/api/services/knowledge_imp.py:252-541]()
- [src/backend/bisheng/worker/knowledge/file_worker.py:25-145]()

#### Text Chunking and Embedding

The `read_chunk_text()` function orchestrates document parsing and chunking:

```mermaid
graph LR
    File["Input File"] --> Loader["Document Loader<br/>filetype_load_map"]
    Loader --> Splitter["ElemCharacterTextSplitter"]
    Splitter --> LLM["extract_title()<br/>LLM-based title extraction"]
    LLM --> Metadata["Metadata enrichment"]
    Metadata --> Vectors["Vector Embedding"]
    Vectors --> Milvus["Milvus Storage"]
    Vectors --> ES["ES Storage"]
```

The system supports multiple file types via specialized loaders defined in [src/backend/bisheng/api/services/knowledge_imp.py:75-82]():

```python
filetype_load_map = {
    "txt": TextLoader,
    "pdf": PyPDFLoader,
    "html": BSHTMLLoader,
    "md": TextLoader,
    "docx": UnstructuredWordDocumentLoader,
    "pptx": UnstructuredPowerPointLoader,
}
```

**Sources:** [src/backend/bisheng/api/services/knowledge_imp.py:789-962]()

#### Preview Cache Management

The `KnowledgeUtils` class provides Redis-based caching for preview operations:

- `get_preview_cache_key()` - generates cache key: `preview_file_chunk:{knowledge_id}:{md5}`
- `async_save_preview_cache()` - stores chunked text and metadata as JSON in Redis hash
- `async_get_preview_cache()` - retrieves cached chunks for editing
- `delete_preview_cache()` - clears cache after final processing

**Sources:** [src/backend/bisheng/api/services/knowledge_imp.py:85-174]()

### Vector Storage Integration

Knowledge bases use dual storage for hybrid retrieval:

| Storage | Purpose | Initialization |
|---------|---------|----------------|
| **Milvus** | Semantic vector similarity search | `KnowledgeRag.init_knowledge_milvus_vectorstore_sync()` |
| **Elasticsearch** | Keyword/BM25 full-text search | `KnowledgeRag.init_knowledge_es_vectorstore_sync()` |

Both are initialized with `KNOWLEDGE_RAG_METADATA_SCHEMA` for consistent metadata fields.

**Sources:** [src/backend/bisheng/api/services/knowledge_imp.py:369-399](), [src/backend/bisheng/api/services/knowledge_imp.py:458-464]()

---

## Chat and Messaging System

The Chat and Messaging System provides real-time WebSocket communication, message persistence, session tracking, and conversation history management.

### Core Components

```mermaid
graph TB
    subgraph "WebSocket Layer"
        WSEndpoint["/chat/{flow_id}<br/>WebSocket endpoint"]
        ChatManager["ChatManager<br/>Connection pool"]
    end
    
    subgraph "Client Handling"
        ChatClient["ChatClient<br/>Per-session handler"]
        WorkType["WorkType enum<br/>FLOW/GPTS/WORKFLOW"]
    end
    
    subgraph "Execution Dispatch"
        AssistantAgent["AssistantAgent"]
        Workflow["Workflow"]
        FlowRunner["Flow execution"]
    end
    
    subgraph "Persistence Layer"
        MessageSessionDao["MessageSessionDao<br/>Session metadata"]
        ChatMessageDao["ChatMessageDao<br/>Message CRUD"]
    end
    
    subgraph "Storage"
        MySQL[(MySQL<br/>messages, sessions)]
        Redis[(Redis<br/>session cache)]
    end
    
    WSEndpoint --> ChatManager
    ChatManager --> ChatClient
    ChatClient --> WorkType
    WorkType --> AssistantAgent
    WorkType --> Workflow
    WorkType --> FlowRunner
    ChatClient --> MessageSessionDao
    ChatClient --> ChatMessageDao
    MessageSessionDao --> MySQL
    MessageSessionDao --> Redis
    ChatMessageDao --> MySQL
```

**Sources:** [src/backend/bisheng/api/v1/chat.py:510-565]()

### WebSocket Chat Endpoint

The main chat endpoint is defined at [src/backend/bisheng/api/v1/chat.py:510-565]():

```python
@router.websocket('/chat/{flow_id}')
async def chat(
    *,
    flow_id: UUID,
    websocket: WebSocket,
    chat_id: Optional[str] = None,
    version_id: Optional[int] = None,
    login_user: UserPayload = Depends(UserPayload.get_login_user_from_ws),
):
    """Websocket endpoint for chat."""
```

The endpoint:
1. Validates flow existence and online status
2. Retrieves graph data from Redis cache or database
3. Delegates to `ChatManager.handle_websocket()` for connection management
4. Handles exceptions and sends error messages via WebSocket

**Sources:** [src/backend/bisheng/api/v1/chat.py:510-565]()

### Message Persistence

Messages are persisted using the `ChatMessage` model and `ChatMessageDao`:

| Field | Type | Description |
|-------|------|-------------|
| `is_bot` | bool | Whether message is from bot (True) or user (False) |
| `message` | str | Message content (LONGTEXT) |
| `type` | str | Message type: 'start', 'stream', 'end', 'error', 'info', 'file' |
| `category` | str | Message category: 'question', 'answer', 'processing', 'tool' |
| `flow_id` | str | Associated flow/assistant/workflow ID |
| `chat_id` | str | Session identifier |
| `user_id` | int | User who created the message |
| `liked` | int | User rating: 0=unrated, 1=liked, 2=disliked |
| `intermediate_steps` | str | Process log for debugging |

**Sources:** [src/backend/bisheng/database/models/message.py:20-47]()

### Session Management

The `MessageSession` model tracks conversation sessions:

```python
class MessageSessionDao:
    @classmethod
    def get_one(cls, chat_id: str) -> MessageSession
    
    @classmethod
    def filter_session(
        cls,
        flow_ids: List[str] = None,
        user_ids: List[int] = None,
        flow_type: List[int] = None,
        page: int = 1,
        limit: int = 10,
        include_delete: bool = False
    ) -> List[MessageSession]
    
    @classmethod
    def delete_session(cls, chat_id: str)
    
    @classmethod
    def update_sensitive_status(cls, chat_id: str, status: SensitiveStatus)
```

**Sources:** [src/backend/bisheng/database/models/session.py:1-200]() (inferred from usage patterns)

### REST API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/chat/history` | GET | Retrieve chat message history with pagination |
| `/chat/list` | GET | Get user's session list filtered by flow type |
| `/chat/app/list` | GET | Get sessions for marking/review tasks |
| `/chat/{chat_id}` | DELETE | Delete a chat session and associated data |
| `/chat/message` | POST | Add a full Q&A record (for security checks) |
| `/chat/message/{message_id}` | PUT | Update message content (for security review) |
| `/liked` | POST | Record user's like/dislike feedback |
| `/chat/copied` | POST | Track when user copies message content |

**Sources:** [src/backend/bisheng/api/v1/chat.py:54-461]()

### Message Feedback System

The system tracks three types of user feedback:

```python
class LikedType(Enum):
    UNRATED = 0
    LIKED = 1
    DISLIKED = 2

# Counters maintained at session level:
# - like_count: Number of liked messages
# - dislike_count: Number of disliked messages  
# - copied_count: Number of copied messages
```

When feedback changes, both the message record and session counters are updated atomically.

**Sources:** [src/backend/bisheng/api/v1/chat.py:408-442](), [src/backend/bisheng/database/models/message.py:14-17]()

---

## Assistant System

The Assistant System provides a configuration-driven AI agent framework that integrates tools, knowledge bases, skills, and LLMs into coherent conversational assistants.

### Service Architecture

```mermaid
graph TB
    subgraph "Service Layer"
        AssistantService["AssistantService<br/>assistant.py"]
    end
    
    subgraph "Agent Execution"
        AssistantAgent["AssistantAgent<br/>assistant_agent.py"]
        InitAssistant["init_assistant()<br/>Build agent with tools/knowledge"]
    end
    
    subgraph "Configuration"
        Assistant["Assistant model<br/>name, prompt, model_name, etc"]
        AssistantLink["AssistantLink<br/>tool/flow/knowledge associations"]
    end
    
    subgraph "DAO Layer"
        AssistantDao["AssistantDao<br/>CRUD operations"]
        AssistantLinkDao["AssistantLinkDao<br/>Manage associations"]
    end
    
    subgraph "Resources"
        GptsTools["GptsTools<br/>Tool definitions"]
        Flow["Flow/Skill<br/>graph definitions"]
        Knowledge["Knowledge<br/>vector stores"]
    end
    
    AssistantService --> AssistantAgent
    AssistantService --> AssistantDao
    AssistantService --> AssistantLinkDao
    AssistantAgent --> InitAssistant
    AssistantDao --> Assistant
    AssistantLinkDao --> AssistantLink
    AssistantLink --> GptsTools
    AssistantLink --> Flow
    AssistantLink --> Knowledge
```

**Sources:** [src/backend/bisheng/api/services/assistant.py:1-450]()

### Assistant Configuration Model

The `Assistant` model stores assistant metadata:

| Field | Type | Description |
|-------|------|-------------|
| `id` | str | UUID primary key |
| `name` | str | Assistant display name |
| `desc` | str | Description shown to users |
| `logo` | str | Logo image URL/path |
| `system_prompt` | str | Internal system-level prompt |
| `prompt` | str | User-visible prompt/instructions |
| `guide_word` | str | Opening message/ice breaker |
| `guide_question` | List | Suggested questions |
| `model_name` | str | LLM model ID from model management |
| `temperature` | float | Model temperature (0.0-1.0) |
| `max_token` | int | Maximum token limit |
| `status` | int | 1=offline, 2=online |
| `user_id` | int | Creator user ID |

**Sources:** [src/backend/bisheng/database/models/assistant.py:22-43]()

### Assistant-Resource Linking

The `AssistantLink` table maintains many-to-many relationships:

```python
class AssistantLinkBase:
    assistant_id: str  # Foreign key to Assistant
    tool_id: int       # Foreign key to GptsTools (nullable)
    flow_id: str       # Foreign key to Flow (nullable)
    knowledge_id: int  # Foreign key to Knowledge (nullable)
```

Helper methods manage these associations:

```python
class AssistantLinkDao:
    @classmethod
    def update_assistant_tool(cls, assistant_id: str, tool_list: List[int])
    
    @classmethod
    def update_assistant_flow(cls, assistant_id: str, flow_list: List[str])
    
    @classmethod
    def update_assistant_knowledge(cls, assistant_id: str, knowledge_list: List[int])
```

**Sources:** [src/backend/bisheng/database/models/assistant.py:45-140]()

### Key Service Methods

#### Creating an Assistant

```python
class AssistantService:
    @classmethod
    async def create_assistant(
        cls, 
        request: Request, 
        login_user: UserPayload, 
        assistant: Assistant
    ) -> AssistantInfo:
        # 1. Check for name conflicts
        # 2. Auto-populate default LLM model
        # 3. Generate auto info (description, guide word/questions)
        # 4. Create database record
        # 5. Execute create_assistant_hook() for group resources
```

**Sources:** [src/backend/bisheng/api/services/assistant.py:149-186]()

#### Updating an Assistant

The update flow validates permissions and atomically updates configuration:

```python
@classmethod
async def update_assistant(
    cls,
    request: Request,
    login_user: UserPayload, 
    req: AssistantUpdateReq
) -> AssistantInfo:
    # 1. Check write permission via access_check()
    # 2. Validate name uniqueness if changed
    # 3. Update assistant fields
    # 4. Update tool/flow/knowledge associations if provided
    # 5. Execute update_assistant_hook()
```

**Sources:** [src/backend/bisheng/api/services/assistant.py:282-327]()

#### Status Management

Assistants can be online (2) or offline (1). Going online requires validation:

```python
@classmethod
async def update_status(
    cls,
    request: Request,
    login_user: UserPayload,
    assistant_id: str,
    status: int
) -> bool:
    if status == AssistantStatus.ONLINE.value:
        # Try to initialize agent to validate configuration
        tmp_agent = AssistantAgent(assistant, '', login_user.user_id)
        await tmp_agent.init_assistant()  # Raises if invalid config
```

**Sources:** [src/backend/bisheng/api/services/assistant.py:342-368]()

### REST API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/assistant` | GET | List assistants with filtering and pagination |
| `/assistant/info/{assistant_id}` | GET | Get detailed assistant configuration |
| `/assistant` | POST | Create new assistant |
| `/assistant` | PUT | Update assistant configuration |
| `/assistant/delete` | POST | Delete assistant and cleanup resources |
| `/assistant/status` | POST | Change online/offline status |
| `/assistant/prompt` | POST | Update prompt only |
| `/assistant/flow` | POST | Update skill list |
| `/assistant/tool` | POST | Update tool list |
| `/assistant/auto/task` | POST | Create auto-optimization task |
| `/assistant/auto` | GET | Stream auto-generated prompt/tools (SSE) |
| `/assistant/chat/{assistant_id}` | WebSocket | Chat with assistant |

**Sources:** [src/backend/bisheng/api/v1/assistant.py:1-177]()

---

## Workflow Engine

The Workflow Engine enables node-based visual programming with typed inputs/outputs, supporting complex branching, loops, and conditional logic.

### Service Architecture

```mermaid
graph TB
    subgraph "API Layer"
        WorkflowAPI["/workflow endpoints<br/>workflow.py"]
    end
    
    subgraph "Service Layer"
        WorkFlowService["WorkFlowService<br/>workflow.py"]
    end
    
    subgraph "Execution Engine"
        Workflow["Workflow class<br/>workflow/graph/workflow.py"]
        GraphState["GraphState<br/>Variable management"]
        NodeFactory["NodeFactory<br/>Node instantiation"]
    end
    
    subgraph "Node Types"
        InputNode["InputNode"]
        LLMNode["LLMNode"]
        AgentNode["AgentNode"]
        RAGNode["RAGNode"]
        CodeNode["CodeNode"]
        ConditionNode["ConditionNode"]
        OutputNode["OutputNode"]
    end
    
    subgraph "Data Layer"
        FlowDao["FlowDao<br/>Workflow metadata"]
        FlowVersionDao["FlowVersionDao<br/>Version management"]
    end
    
    WorkflowAPI --> WorkFlowService
    WorkFlowService --> Workflow
    WorkFlowService --> FlowDao
    Workflow --> GraphState
    Workflow --> NodeFactory
    NodeFactory --> InputNode
    NodeFactory --> LLMNode
    NodeFactory --> AgentNode
    NodeFactory --> RAGNode
    NodeFactory --> CodeNode
    NodeFactory --> ConditionNode
    NodeFactory --> OutputNode
    FlowDao --> FlowVersionDao
```

**Sources:** [src/backend/bisheng/api/services/workflow.py:1-363]()

### Workflow Data Model

Workflows reuse the `Flow` model with `flow_type = FlowType.WORKFLOW.value` (10):

```python
class Flow:
    id: str                  # UUID
    name: str                # Workflow name
    description: str         # Description
    data: Dict              # Node graph: {"nodes": [...], "edges": [...]}
    status: int             # 1=offline, 2=online
    flow_type: int          # 10 for workflows
    user_id: int            # Creator
```

**Sources:** [src/backend/bisheng/database/models/flow.py:80-83]()

### Key Service Methods

#### Running Single Node

The `run_once()` method executes a single node for testing:

```python
@classmethod
def run_once(
    cls,
    login_user: UserPayload,
    node_input: Dict[str, any],
    node_data: Dict[any, any],
    workflow_id: str
):
    # 1. Get workflow info
    # 2. Create BaseNodeData from node_data
    # 3. Instantiate node via NodeFactory
    # 4. Handle input based on node type
    # 5. Execute node._run()
    # 6. Parse and return log data
```

**Sources:** [src/backend/bisheng/api/services/workflow.py:115-178]()

#### Status Management

Workflows must be online to execute. The `update_flow_status()` method validates before going online:

```python
@classmethod
async def update_flow_status(
    cls,
    login_user: UserPayload,
    flow_id: str,
    version_id: int,
    status: int
):
    if status == FlowStatus.ONLINE.value:
        # Initialize workflow to validate configuration
        _ = Workflow(flow_id, db_flow.name, login_user.user_id, 
                    version_info.data, False, 10, 10, None)
        # If successful, change current version
        await FlowVersionDao.change_current_version(flow_id, version_info)
```

**Sources:** [src/backend/bisheng/api/services/workflow.py:181-212]()

### Event Conversion

Workflows use a specialized event schema for WebSocket communication. The `convert_chat_response_to_workflow_event()` method transforms `ChatResponse` objects into `WorkflowEvent` objects:

| Event Type | Conversion Logic |
|------------|------------------|
| `UserInput` | Extract input schema, convert form definitions |
| `GuideWord` | Extract guide word message |
| `GuideQuestion` | Extract guide question list |
| `OutputMsg` | Extract message, files, handle source traceability |
| `OutputWithChoose` | Include inline option selection |
| `OutputWithInput` | Include inline text input |
| `StreamMsg` | Stream status, reasoning content, output key |
| `Error` | Convert to Close event with error message |

**Sources:** [src/backend/bisheng/api/services/workflow.py:215-334]()

### REST API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/workflow/write/auth` | GET | Check user write permissions |
| `/workflow/report/file` | GET | Get report template file URL |
| `/workflow/report/copy` | POST | Copy report template file |
| `/workflow/report/callback` | POST | OnlyOffice callback for saving templates |
| `/workflow/run_once` | POST | Execute single node for testing |
| `/workflow/chat/{workflow_id}` | WebSocket | Execute workflow via WebSocket |
| `/workflow/create` | POST | Create new workflow |
| `/workflow/versions` | GET | Get workflow version list |
| `/workflow/versions` | POST | Create new workflow version |

**Sources:** [src/backend/bisheng/api/v1/workflow.py:1-300]()

---

## Marking and Annotation

The Marking and Annotation system enables quality assurance workflows where designated reviewers evaluate and annotate chat sessions for training data creation, quality monitoring, and compliance review.

### System Architecture

```mermaid
graph TB
    subgraph "Task Management"
        MarkTask["MarkTask<br/>Task configuration"]
        MarkAppUser["MarkAppUser<br/>App-User assignments"]
    end
    
    subgraph "Record Management"
        MarkRecord["MarkRecord<br/>Session review records"]
    end
    
    subgraph "Navigation"
        NextPrev["next/prev navigation<br/>Linked list traversal"]
    end
    
    subgraph "DAO Layer"
        MarkTaskDao["MarkTaskDao"]
        MarkRecordDao["MarkRecordDao"]
        MarkAppUserDao["MarkAppUserDao"]
    end
    
    subgraph "Data Storage"
        MySQL[(MySQL)]
    end
    
    MarkTask --> MarkTaskDao
    MarkAppUser --> MarkAppUserDao
    MarkRecord --> MarkRecordDao
    NextPrev --> MarkRecordDao
    MarkTaskDao --> MySQL
    MarkRecordDao --> MySQL
    MarkAppUserDao --> MySQL
```

**Sources:** [src/backend/bisheng/api/v1/mark_task.py:1-261]()

### Data Models

#### MarkTask

Defines a review task with assigned apps and reviewers:

```python
class MarkTask:
    id: int                    # Primary key
    create_user: str           # Creator name
    create_id: int             # Creator user ID
    app_id: str                # Comma-separated app IDs: "flow1,flow2,flow3"
    process_users: str         # Comma-separated reviewer IDs: "1,2,3"
    mark_user: str             # Current reviewer (optional)
    status: int                # 1=default, 2=done, 3=in-progress
```

**Sources:** [src/backend/bisheng/database/models/mark_task.py:19-30]()

#### MarkRecord

Tracks individual session review status:

```python
class MarkRecord:
    id: int                    # Primary key
    create_user: str           # Reviewer name
    create_id: int             # Reviewer user ID
    app_id: int                # Associated app ID
    task_id: int               # Parent task ID
    session_id: str            # Chat session ID being reviewed
    flow_type: int             # Flow/assistant/workflow type
    status: int                # 1=default, 2=done, 3=rejected
```

**Sources:** [src/backend/bisheng/database/models/mark_record.py:19-31]()

#### MarkAppUser

Junction table for many-to-many task-app-user relationships:

```python
class MarkAppUser:
    app_id: str                # Application ID
    user_id: int               # Reviewer user ID  
    task_id: int               # Task ID
    create_id: int             # Task creator ID
    status: int                # Status flag
```

**Sources:** [src/backend/bisheng/database/models/mark_app_user.py:12-17]()

### Task Lifecycle

#### Creating a Task

```python
@router.post('/mark/create_task')
async def create(task_create: MarkTaskCreate, login_user: UserPayload):
    # 1. Create MarkTask with comma-separated IDs
    task = MarkTask(
        create_id=login_user.user_id,
        create_user=login_user.user_name,
        app_id=",".join(task_create.app_list),
        process_users=",".join(task_create.user_list)
    )
    MarkTaskDao.create_task(task)
    
    # 2. Create MarkAppUser records for all combinations
    user_app = [
        MarkAppUser(task_id=task.id, create_id=login_user.user_id, 
                   app_id=app, user_id=user)
        for app in task_create.app_list 
        for user in task_create.user_list
    ]
    MarkAppUserDao.create_task(user_app)
```

**Sources:** [src/backend/bisheng/api/v1/mark_task.py:79-96]()

#### Marking Sessions

The `mark()` endpoint handles session review status updates:

```python
@router.post('/mark/mark')
async def mark(data: MarkData, login_user: UserPayload):
    # 1. Get or create MarkRecord
    db_r = MarkRecordDao.get_record(data.task_id, data.session_id)
    
    if db_r:
        db_r.status = data.status
        MarkRecordDao.update_record(db_r)
    else:
        record_info = MarkRecord(
            create_user=login_user.user_name,
            create_id=login_user.user_id,
            session_id=data.session_id,
            task_id=data.task_id,
            status=data.status,
            flow_type=data.flow_type
        )
        MarkRecordDao.create_record(record_info)
    
    # 2. Check if task is complete
    msg_list = ChatMessageDao.get_msg_by_flows(task.app_id.split(","))
    r_list = MarkRecordDao.get_list_by_taskid(data.task_id)
    if all_sessions_reviewed:
        MarkTaskDao.update_task(data.task_id, MarkTaskStatus.DONE.value)
```

**Sources:** [src/backend/bisheng/api/v1/mark_task.py:117-169]()

### Session Navigation

The system provides prev/next navigation through unmarked sessions using a double-linked list structure:

```python
@router.get("/mark/next")
async def pre_or_next(chat_id: str, action: str, task_id: int):
    if action == "next":
        # Get all messages not yet marked
        msg = MessageSessionDao.filter_session(
            flow_ids=task.app_id.split(","), 
            exclude_chats=marked_chat_ids
        )
        
        # Build linked list
        linked = DoubleLinkList()
        for m in msg:
            linked.append(m.chat_id)
        
        # Find current position and navigate
        cur = linked.find(chat_id)
        if cur.next:
            return cur.next.data
        else:
            return linked.head().data  # Wrap around
```

**Sources:** [src/backend/bisheng/api/v1/mark_task.py:178-246]()

### REST API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/mark/list` | GET | List tasks (filtered by user role) |
| `/mark/get_status` | GET | Get review status for a session |
| `/mark/create_task` | POST | Create new review task |
| `/mark/get_user` | GET | Get reviewers assigned to task |
| `/mark/mark` | POST | Mark session with status |
| `/mark/get_record` | GET | Get individual mark record |
| `/mark/next` | GET | Navigate to next/previous session |
| `/mark/del` | DELETE | Delete task and all records |

**Sources:** [src/backend/bisheng/api/v1/mark_task.py:22-261]()

---

## Flow and Skill Management

Flow and Skill Management provides lifecycle operations for Flow-type applications (flow_type=1), including creation, versioning, comparison, and permission management.

### Service Architecture

```mermaid
graph TB
    subgraph "Service Layer"
        FlowService["FlowService<br/>flow.py"]
        WorkFlowService["WorkFlowService<br/>workflow.py"]
    end
    
    subgraph "Version Management"
        FlowVersionDao["FlowVersionDao<br/>CRUD versions"]
        CurrentVersion["is_current flag<br/>One active version per flow"]
    end
    
    subgraph "Lifecycle Operations"
        Create["create_flow()<br/>Initialize v0"]
        Update["update_version_info()"]
        Delete["delete_version()"]
        Switch["change_current_version()"]
        Compare["compare_version()"]
    end
    
    subgraph "Resource Management"
        GroupResource["GroupResourceDao<br/>Share with groups"]
        RoleAccess["RoleAccessDao<br/>Fine-grained permissions"]
    end
    
    subgraph "Data Storage"
        FlowDao["FlowDao<br/>Flow metadata"]
        MySQL[(MySQL)]
    end
    
    FlowService --> FlowVersionDao
    FlowService --> Create
    FlowService --> Update
    FlowService --> Delete
    FlowService --> Switch
    FlowService --> Compare
    FlowService --> GroupResource
    FlowService --> RoleAccess
    FlowService --> FlowDao
    FlowVersionDao --> MySQL
    FlowDao --> MySQL
    GroupResource --> MySQL
    RoleAccess --> MySQL
```

**Sources:** [src/backend/bisheng/api/services/flow.py:1-350]()

### Version Management

#### Version Data Model

```python
class FlowVersion:
    id: int                    # Primary key
    flow_id: str               # Parent flow UUID
    name: str                  # Version name (e.g., "v1", "production")
    data: Dict                 # Node graph definition
    description: str           # Version description
    is_current: int            # 1 if active version, 0 otherwise
    is_delete: int             # Soft delete flag
    user_id: int               # Creator user ID
    flow_type: int             # Flow type (1=flow, 10=workflow)
```

Only one version can have `is_current=1` at a time per flow.

**Sources:** [src/backend/bisheng/database/models/flow_version.py:16-50]()

#### Creating Versions

```python
@classmethod
async def create_new_version(
    cls,
    user: UserPayload,
    flow_id: str,
    flow_version: FlowVersionCreate
) -> FlowVersion:
    # 1. Validate flow existence and permissions
    flow_info = await FlowDao.aget_flow_by_id(flow_id)
    await cls.judge_flow_write_permission(user, flow_id)
    
    # 2. Check version name uniqueness
    versions = FlowVersionDao.get_list_by_flow(flow_id)
    if any(v.name == flow_version.name for v in versions):
        raise VersionNameExistsError()
    
    # 3. Create version record
    db_version = FlowVersion(
        flow_id=flow_id,
        name=flow_version.name,
        data=flow_version.data or flow_info.data,
        is_current=0,  # New versions start inactive
        ...
    )
    return FlowVersionDao.insert_one(db_version)
```

**Sources:** [src/backend/bisheng/api/services/flow.py:121-179]()

#### Switching Active Version

```python
@classmethod
async def change_current_version(
    cls,
    request: Request,
    user: UserPayload,
    flow_id: str,
    version_id: int
):
    # 1. Validate permissions and status
    if flow_info.status == FlowStatus.ONLINE.value:
        raise FlowOnlineEditError()
    
    # 2. Change active version
    await FlowVersionDao.change_current_version(flow_id, version_info)
    
    # 3. Sync flow.data with version.data
    flow_info.data = version_info.data
    await FlowDao.aupdate_flow(flow_info)
```

**Sources:** [src/backend/bisheng/api/services/flow.py:186-226]()

### Version Comparison

The system supports automated A/B testing across versions:

```python
class FlowCompareReq:
    inputs: Any                      # Shared inputs for all versions
    question_list: List[str]         # Test cases
    version_list: List[int]          # Version IDs to compare
    node_id: str                     # Target node for output comparison
    thread_num: int = 1              # Parallel execution threads

@classmethod
async def compare_version(
    cls,
    user: UserPayload,
    flow_id: str,
    req: FlowCompareReq
) -> AsyncGenerator:
    # For each version:
    #   1. Build graph from version data
    #   2. Execute with each test question
    #   3. Collect outputs from specified node
    #   4. Yield comparison results
```

**Sources:** [src/backend/bisheng/api/services/flow.py:286-478]()

### Flow Hooks

The service layer uses hooks for cross-cutting concerns:

```python
@classmethod
def create_flow_hook(
    cls,
    request: Request,
    login_user: UserPayload,
    db_flow: Flow,
    version_id: int,
    flow_type: int = FlowType.FLOW.value
):
    # 1. Add flow to user's groups
    user_groups = UserGroupDao.get_user_group(login_user.user_id)
    GroupResourceDao.insert_group_batch([
        GroupResource(group_id=g.group_id, third_id=db_flow.id, 
                     type=ResourceTypeEnum.FLOW)
        for g in user_groups
    ])
    
    # 2. Write audit log
    AuditLogService.create_build_flow(login_user, get_request_ip(request), 
                                      db_flow.id)
    
    # 3. Initialize variable values
    VariableDao.init_variables(version_id, db_flow.data)
```

**Sources:** [src/backend/bisheng/api/services/flow.py:231-275]()

### REST API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/flows/` | POST | Create new flow |
| `/flows/` | GET | List flows with filtering |
| `/flows/{flow_id}` | GET | Get flow details |
| `/flows/{flow_id}` | PATCH | Update flow metadata |
| `/flows/{flow_id}` | DELETE | Delete flow |
| `/flows/versions` | GET | List versions for a flow |
| `/flows/versions` | POST | Create new version |
| `/flows/versions/{version_id}` | PUT | Update version |
| `/flows/versions/{version_id}` | DELETE | Delete version |
| `/flows/versions/{version_id}` | GET | Get version details |
| `/flows/change_version` | POST | Switch active version |
| `/flows/status` | POST | Update online/offline status |
| `/flows/copy/{flow_id}` | POST | Copy flow to new flow |
| `/flows/check_valid` | POST | Validate flow configuration |
| `/flows/compare` | POST | Compare version outputs (SSE) |

**Sources:** [src/backend/bisheng/api/v1/flows.py:1-300]()

---

## Summary Table

The following table summarizes the core services:

| Service | Primary Files | Key Classes | Main Responsibilities |
|---------|---------------|-------------|----------------------|
| **Knowledge Base** | `knowledge.py`, `knowledge_imp.py`, `file_worker.py` | `KnowledgeService`, `KnowledgeDao`, `process_file_task()` | File upload, parsing, chunking, embedding to Milvus/ES, preview/edit |
| **Chat & Messaging** | `chat.py`, `message.py`, `session.py` | `ChatManager`, `MessageSessionDao`, `ChatMessageDao` | WebSocket handling, message persistence, session tracking, feedback |
| **Assistant** | `assistant.py`, `assistant.py` (model) | `AssistantService`, `AssistantDao`, `AssistantLinkDao` | Assistant configuration, tool/knowledge/skill linking, status management |
| **Workflow** | `workflow.py`, `workflow.py` (engine) | `WorkFlowService`, `Workflow`, `NodeFactory` | Node-based execution, graph state, single node testing, event conversion |
| **Marking** | `mark_task.py`, `mark_record.py`, `mark_app_user.py` | `MarkTaskDao`, `MarkRecordDao` | Review task creation, session marking, navigation, completion tracking |
| **Flow/Skill** | `flow.py`, `flows.py`, `flow_version.py` | `FlowService`, `FlowDao`, `FlowVersionDao` | Version management, lifecycle hooks, comparison, permission enforcement |

**Sources:** All files cited throughout this document.

---

# Page: Knowledge Base Management

# Knowledge Base Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/backend/bisheng/api/services/knowledge.py](src/backend/bisheng/api/services/knowledge.py)
- [src/backend/bisheng/api/services/knowledge_imp.py](src/backend/bisheng/api/services/knowledge_imp.py)
- [src/backend/bisheng/worker/knowledge/file_worker.py](src/backend/bisheng/worker/knowledge/file_worker.py)
- [src/backend/bisheng/worker/knowledge/qa.py](src/backend/bisheng/worker/knowledge/qa.py)
- [src/backend/bisheng/worker/knowledge/rebuild_knowledge_worker.py](src/backend/bisheng/worker/knowledge/rebuild_knowledge_worker.py)
- [src/frontend/platform/src/components/bs-ui/select/hover.tsx](src/frontend/platform/src/components/bs-ui/select/hover.tsx)
- [src/frontend/platform/src/layout/MainLayout.tsx](src/frontend/platform/src/layout/MainLayout.tsx)
- [src/frontend/platform/src/pages/BuildPage/flow/FlowNode/component/KnowledgeSelectItem.tsx](src/frontend/platform/src/pages/BuildPage/flow/FlowNode/component/KnowledgeSelectItem.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/AdjustFilesUpload.tsx](src/frontend/platform/src/pages/KnowledgePage/AdjustFilesUpload.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/KnowledgeFile.tsx](src/frontend/platform/src/pages/KnowledgePage/KnowledgeFile.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/KnowledgeQa.tsx](src/frontend/platform/src/pages/KnowledgePage/KnowledgeQa.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/components/FileUploadStep2.tsx](src/frontend/platform/src/pages/KnowledgePage/components/FileUploadStep2.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/components/FileUploadStep4.tsx](src/frontend/platform/src/pages/KnowledgePage/components/FileUploadStep4.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/components/Files.tsx](src/frontend/platform/src/pages/KnowledgePage/components/Files.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/components/Header.tsx](src/frontend/platform/src/pages/KnowledgePage/components/Header.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/components/Paragraphs.tsx](src/frontend/platform/src/pages/KnowledgePage/components/Paragraphs.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/components/PreviewFile.tsx](src/frontend/platform/src/pages/KnowledgePage/components/PreviewFile.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/components/PreviewParagraph.tsx](src/frontend/platform/src/pages/KnowledgePage/components/PreviewParagraph.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/components/PreviewResult.tsx](src/frontend/platform/src/pages/KnowledgePage/components/PreviewResult.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/components/RuleFile.tsx](src/frontend/platform/src/pages/KnowledgePage/components/RuleFile.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/components/RuleTable.tsx](src/frontend/platform/src/pages/KnowledgePage/components/RuleTable.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/detail.tsx](src/frontend/platform/src/pages/KnowledgePage/detail.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/filesUpload.tsx](src/frontend/platform/src/pages/KnowledgePage/filesUpload.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/qas.tsx](src/frontend/platform/src/pages/KnowledgePage/qas.tsx)

</details>



## Purpose and Scope

The Knowledge Base Management system provides a complete document lifecycle management solution including file upload, parsing, chunking, embedding generation, dual indexing (vector and text), retrieval, and interactive chunk editing with bounding box support. This system transforms raw documents into searchable, AI-ready knowledge bases.

The system features a 4-step upload wizard on the frontend and sophisticated backend processing pipelines that support multiple document formats with intelligent text segmentation and preview generation.

For information about chat systems that consume knowledge bases, see page 3.2. For details about retrieval strategies and RAG implementation, see page 6.3.

## System Architecture

The Knowledge Base Management system integrates frontend components, backend services, and multiple storage systems:

**System Architecture: Frontend to Backend**

```mermaid
graph TB
    subgraph "Frontend UI"
        Upload["filesUpload.tsx<br/>4-Step Wizard"]
        FileList["Files.tsx<br/>File Management"]
        Paragraphs["Paragraphs.tsx<br/>Chunk Editor"]
        Preview["PreviewResult.tsx<br/>Preview System"]
    end
    
    subgraph "Backend API"
        KnowledgeAPI["/api/v1/knowledge"]
        ProcessAPI["/api/v1/knowledge/process"]
        PreviewAPI["/api/v1/knowledge/preview"]
        ChunkAPI["/api/v1/knowledge/chunk"]
    end
    
    subgraph "Service Layer"
        KnowledgeService["KnowledgeService<br/>knowledge.py"]
        KnowledgeImp["knowledge_imp.py<br/>Core Processing"]
    end
    
    subgraph "Async Processing"
        Celery["Celery Worker"]
        FileWorker["file_worker.py<br/>parse_knowledge_file_celery"]
        RebuildWorker["rebuild_knowledge_worker.py"]
    end
    
    subgraph "Storage Systems"
        MySQL["MySQL<br/>Knowledge, KnowledgeFile"]
        Milvus["Milvus<br/>Vector Embeddings"]
        ES["Elasticsearch<br/>Text Index"]
        MinIO["MinIO<br/>Files & Partitions"]
        Redis["Redis<br/>Preview Cache"]
    end
    
    Upload --> ProcessAPI
    FileList --> KnowledgeAPI
    Paragraphs --> ChunkAPI
    Preview --> PreviewAPI
    
    ProcessAPI --> KnowledgeService
    PreviewAPI --> KnowledgeService
    ChunkAPI --> KnowledgeService
    
    KnowledgeService --> KnowledgeImp
    KnowledgeService --> Celery
    Celery --> FileWorker
    
    KnowledgeImp --> MySQL
    KnowledgeImp --> MinIO
    FileWorker --> Milvus
    FileWorker --> ES
    KnowledgeService --> Redis
```

**Sources:** [src/backend/bisheng/api/services/knowledge.py:72-263](), [src/backend/bisheng/api/services/knowledge_imp.py:250-297](), [src/frontend/platform/src/pages/KnowledgePage/filesUpload.tsx:37-416](), [src/backend/bisheng/worker/knowledge/file_worker.py:247-337]()

## Knowledge Base Types

The system supports three distinct knowledge base types defined in `KnowledgeTypeEnum`:

| Type | Value | Description | Storage Model |
|------|-------|-------------|---------------|
| `NORMAL` | 0 | Document-based knowledge bases | `KnowledgeFile` with chunking |
| `QA` | 1 | Question-Answer pair knowledge bases | `QAKnowledge` with Q&A pairs |
| `PRIVATE` | 2 | Personal workstation knowledge bases | Per-user file storage |

**Sources:** [src/backend/bisheng/knowledge/domain/models/knowledge.py:17-21](), [src/backend/bisheng/knowledge/domain/models/knowledge_file.py:15-64]()

## File Upload Workflow

The frontend implements a 4-step upload wizard that guides users through the complete file processing workflow:

**4-Step Upload Wizard Flow**

```mermaid
graph LR
    Step1["Step 1<br/>Upload Files<br/>FileUploadStep1"]
    Step2["Step 2<br/>Segmentation Strategy<br/>FileUploadStep2"]
    Step3["Step 3<br/>Text Comparison<br/>PreviewResult"]
    Step4["Step 4<br/>Data Processing<br/>FileUploadStep4"]
    
    Step1 -->|"onNext(files)"| Step2
    Step2 -->|"onNext(config)"| Step3
    Step3 -->|"handleSave(config)"| Step4
    
    subgraph "Step1 Actions"
        Upload["Upload to MinIO tmp/"]
        Validate["Validate duplicates"]
        SaveUUID["Save filename mapping"]
    end
    
    subgraph "Step2 Configuration"
        Separator["Configure separators"]
        ChunkSize["Set chunk size/overlap"]
        ExcelRule["Excel-specific rules"]
        OCR["OCR & formula options"]
    end
    
    subgraph "Step3 Preview"
        SSE["SSE preview API call"]
        Display["Display chunks"]
        Edit["Allow chunk editing"]
    end
    
    subgraph "Step4 Processing"
        Queue["Queue Celery task"]
        Poll["Poll file status"]
        Complete["Navigate on completion"]
    end
    
    Step1 --> Upload
    Step2 --> Separator
    Step3 --> SSE
    Step4 --> Queue
```

### Step 1: File Upload

The `FileUploadStep1` component handles initial file selection and upload:

- **File upload**: Uploads to MinIO temporary storage (`tmp/` prefix)
- **UUID mapping**: Stores original filename in Redis with UUID key for 24 hours
- **Duplicate detection**: Checks MD5 hash against existing files
- **Format validation**: Supports PDF, DOCX, DOC, PPTX, PPT, XLS, XLSX, CSV, TXT, MD, HTML

**Sources:** [src/frontend/platform/src/pages/KnowledgePage/filesUpload.tsx:68-83](), [src/backend/bisheng/api/services/knowledge.py:376-389]()

### Step 2: Segmentation Strategy

The `FileUploadStep2` component provides configuration for text chunking:

**Segmentation Configuration Options:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `separator` | `string[]` | Regex patterns for splitting | `['\\n\\n', '\\n']` |
| `separator_rule` | `string[]` | Split position ('before'/'after') | `['after', 'after']` |
| `chunk_size` | `number` | Maximum chunk size in characters | 1000 |
| `chunk_overlap` | `number` | Overlap between chunks | 200 |
| `retain_images` | `boolean` | Keep extracted images | true |
| `enable_formula` | `boolean` | Enable formula recognition | true |
| `force_ocr` | `boolean` | Force OCR processing | false |
| `filter_page_header_footer` | `boolean` | Remove headers/footers | false |

**Excel-specific rules** (via `ExcelRule`):
- `slice_length`: Number of rows per chunk
- `append_header`: Include header in each chunk
- `header_start_row`: First header row (1-based)
- `header_end_row`: Last header row (1-based)

**Sources:** [src/frontend/platform/src/pages/KnowledgePage/components/FileUploadStep2.tsx:75-108](), [src/backend/bisheng/api/v1/schemas.py:1-50]()

### Step 3: Text Comparison (Preview)

The preview system uses Server-Sent Events (SSE) to stream processing results:

```mermaid
sequenceDiagram
    participant UI as PreviewResult.tsx
    participant API as /api/v1/knowledge/preview
    participant Worker as Background Processing
    participant Redis as Redis Cache
    participant MinIO as MinIO Storage
    
    UI->>API: POST with config + file_path
    API->>Worker: Spawn processing task
    Worker->>Worker: Parse document
    Worker->>Worker: Apply chunking rules
    Worker->>Redis: Cache chunks
    Worker->>MinIO: Store partitions/bbox
    Worker-->>API: Stream 'processing' events
    API-->>UI: SSE: eventType='processing'
    Worker->>API: Processing complete
    API-->>UI: SSE: eventType='completed'<br/>data: {chunks, file_url, partitions}
    UI->>UI: Display chunks with preview
```

Users can edit chunks before final submission. Changes are stored in Redis cache with key format: `preview_file_chunk:{knowledge_id}:{md5}`.

**Sources:** [src/frontend/platform/src/pages/KnowledgePage/components/PreviewResult.tsx:67-162](), [src/backend/bisheng/api/services/knowledge.py:391-473]()

### Step 4: Data Processing

The final step submits files for asynchronous processing:

1. **API call**: `POST /api/v1/knowledge/process` with all configuration
2. **File creation**: Creates `KnowledgeFile` records with status `PROCESSING` (1)
3. **Celery task**: Queues `parse_knowledge_file_celery` for each file
4. **Status polling**: Frontend polls file status every 5 seconds
5. **Completion**: Updates status to `SUCCESS` (2) or `FAILED` (3)

**Sources:** [src/frontend/platform/src/pages/KnowledgePage/components/FileUploadStep4.tsx:60-110](), [src/backend/bisheng/api/services/knowledge.py:543-589]()

## Document Processing Pipeline

The core processing pipeline is implemented in `addEmbedding` and handles the transformation from raw files to searchable chunks:

**Processing Pipeline: File to Vectors**

```mermaid
graph TD
    Download["Download from MinIO<br/>file_download()"]
    Parse["Parse Document<br/>read_chunk_text()"]
    Convert["Format Conversion<br/>convert_file_to_md()"]
    ETL["ETL4LM Processing<br/>Etl4lmLoader"]
    Split["Text Splitting<br/>ElemCharacterTextSplitter"]
    Title["Extract Titles<br/>extract_title()"]
    Aggregate["Aggregate Metadata<br/>aggregate_chunk_metadata()"]
    Embed["Generate Embeddings<br/>Model inference"]
    Store["Store Vectors & Text<br/>Milvus + Elasticsearch"]
    
    Download --> Parse
    Parse --> Convert
    Parse --> ETL
    Convert --> Split
    ETL --> Split
    Split --> Title
    Title --> Aggregate
    Aggregate --> Embed
    Embed --> Store
    
    subgraph "File Type Routing"
        PDF["PDF → ETL4LM"]
        DOCX["DOCX → Markdown"]
        Excel["XLS/XLSX → Markdown"]
        Text["TXT/MD → Direct"]
    end
    
    subgraph "Output Storage"
        Milvus["Milvus: vectors + text"]
        ES["Elasticsearch: text + metadata"]
        MinIOBbox["MinIO: partitions/{id}.json"]
        MySQLStatus["MySQL: status = SUCCESS"]
    end
    
    Store --> Milvus
    Store --> ES
    Parse --> MinIOBbox
    Store --> MySQLStatus
```

### Document Parsing

The `read_chunk_text` function orchestrates document parsing with format-specific handlers:

**Format-Specific Processing:**

| Format | Handler | Special Processing |
|--------|---------|-------------------|
| PDF | `Etl4lmLoader` or local `PyPDFLoader` | ETL4LM for OCR, bbox extraction |
| DOCX/DOC | `convert_file_to_md()` + `TextLoader` | Convert to Markdown via OnlyOffice |
| PPTX/PPT | `convert_file_to_md()` + `convert_ppt_to_pdf()` | Markdown + PDF preview |
| XLS/XLSX/CSV | `convert_file_to_md()` | Table to Markdown with header handling |
| TXT/MD | `TextLoader` | Direct loading with encoding detection |
| HTML | `BSHTMLLoader` | HTML parsing with structure preservation |

**ETL4LM Processing** (for complex documents):
- OCR with bounding box extraction
- Table detection and structure preservation
- Formula recognition (when enabled)
- Page header/footer filtering
- Image extraction to MinIO

**Sources:** [src/backend/bisheng/api/services/knowledge_imp.py:773-936](), [src/backend/bisheng/api/services/etl4lm_loader.py:1-200]()

### Text Chunking

The `ElemCharacterTextSplitter` implements intelligent text segmentation:

```python
# Example configuration
text_splitter = ElemCharacterTextSplitter(
    separators=['\\n\\n', '\\n'],        # Regex patterns
    separator_rule=['after', 'after'],   # Split position
    chunk_size=1000,                     # Max characters
    chunk_overlap=200,                   # Overlap size
    is_separator_regex=True              # Enable regex
)
texts = text_splitter.split_documents(documents)
```

**Chunking Strategy:**
1. Apply separators in order (longest match first)
2. Respect `separator_rule` (split before/after separator)
3. Ensure chunks don't exceed `chunk_size` (with overflow handling)
4. Add `chunk_overlap` from previous chunk
5. Preserve metadata including bounding boxes

**Sources:** [src/backend/bisheng/api/services/knowledge_imp.py:805-811](), [src/backend/bisheng_langchain/text_splitter.py:1-300]()

### Metadata Enrichment

Each chunk is enriched with metadata via `aggregate_chunk_metadata`:

```python
# Metadata structure
metadata = {
    'document_id': file.id,
    'document_name': file.file_name,
    'knowledge_id': knowledge.id,
    'upload_time': int(file.create_time.timestamp()),
    'update_time': int(file.update_time.timestamp()),
    'uploader': user.user_name,
    'updater': user.user_name,
    'abstract': extracted_title,  # LLM-generated summary
    'chunk_index': index,
    'page': page_number,
    'bbox': json.dumps({'chunk_bboxes': [...]}),  # Bounding boxes
    'user_metadata': {}  # Custom metadata fields
}
```

The `aggregate_chunk_metadata` function wraps chunk text with metadata:
```
{<file_title>document_name</file_title>
<file_abstract>abstract</file_abstract>
<paragraph_content>chunk_text</paragraph_content>}
```

**Sources:** [src/backend/bisheng/api/services/knowledge_imp.py:94-100](), [src/backend/bisheng/api/services/knowledge_imp.py:637-646]()

## Storage Systems Integration

### Vector Storage with Milvus

The system uses Milvus for storing document embeddings, initialized via `KnowledgeRag.init_knowledge_milvus_vectorstore_sync`:

**Milvus Collection Schema:**

| Field | Type | Description |
|-------|------|-------------|
| `pk` | `int64` | Auto-generated primary key |
| `vector` | `float[]` | Embedding vector (dimension based on model) |
| `text` | `varchar` | Full chunk text with metadata wrapper |
| `document_id` | `int64` | Reference to `KnowledgeFile.id` |
| `knowledge_id` | `int64` | Reference to `Knowledge.id` |
| `document_name` | `varchar` | Original filename |
| `source` | `varchar` | File path reference |
| `page` | `int64` | Page number (for PDFs) |
| `bbox` | `varchar` | JSON with bounding box coordinates |
| `chunk_index` | `int64` | Index within document |
| `upload_time` | `int64` | Unix timestamp |
| `update_time` | `int64` | Unix timestamp |
| `uploader` | `varchar` | Username |
| `updater` | `varchar` | Username |
| `abstract` | `varchar` | LLM-generated summary |
| `user_metadata` | `varchar` | JSON with custom fields |

**Collection Naming Strategies:**
- **Single collection**: `col_{timestamp}_{uuid}` - Dedicated collection per knowledge base
- **Partition mode**: `partition_embedding_knowledge_{suffix}` - Shared collection with partition keys

**Sources:** [src/backend/bisheng/knowledge/domain/knowledge_rag.py:40-120](), [src/backend/bisheng/api/services/knowledge_imp.py:456-460]()

### Elasticsearch Integration

Elasticsearch provides full-text search initialized via `KnowledgeRag.init_knowledge_es_vectorstore_sync`:

**Index Naming:** `index_{timestamp}_{uuid}` or reuses `collection_name`

**Document Structure:**
```json
{
  "_id": "uuid",
  "text": "chunk content with metadata",
  "metadata": {
    "document_id": 123,
    "knowledge_id": 456,
    "document_name": "file.pdf",
    "chunk_index": 0,
    "page": 1,
    "bbox": "{\"chunk_bboxes\": [...]}",
    "upload_time": 1234567890,
    "user_metadata": {}
  }
}
```

The system performs parallel writes to Milvus and Elasticsearch via `add_texts()`.

**Sources:** [src/backend/bisheng/api/services/knowledge_imp.py:461-462](), [src/backend/bisheng/api/services/knowledge_imp.py:650-655]()

### MinIO Object Storage

MinIO organizes files using standardized object naming via `KnowledgeUtils` methods:

**Storage Organization:**

| Object Type | Path Pattern | Purpose |
|-------------|--------------|---------|
| Original files | `original/{file_id}.{ext}` | Source documents |
| Preview files | `preview/{file_id}.{converted_ext}` | Converted for viewing (DOC→DOCX, PPT→PDF) |
| Bbox data | `partitions/{file_id}.json` | OCR bounding boxes and partition info |
| Images | `knowledge/images/{knowledge_id}/{doc_id}/{filename}` | Extracted images from documents |
| Temporary | `tmp/{uuid}.{ext}` | Files during upload (24h TTL) |

**File Conversion:**
- `.doc` → `.docx` (stored in `preview/`)
- `.ppt`, `.pptx` → `.pdf` (stored in `preview/`)
- Excel files → Markdown (temporary processing)

**Sources:** [src/backend/bisheng/api/services/knowledge_imp.py:182-216](), [src/backend/bisheng/api/services/knowledge_imp.py:218-248]()

### Redis Cache

Redis provides temporary storage for preview data and file metadata:

**Cache Keys:**
- **Preview chunks**: `preview_file_chunk:{knowledge_id}:{md5_hash}` - Hash map of chunk index to chunk data
- **Parse type**: `preview_file_chunk:{knowledge_id}:{md5_hash}_parse_type` - "etl4lm" or "un_etl4lm"
- **File path**: `preview_file_chunk:{knowledge_id}:{md5_hash}_file_path` - Temporary file URL
- **Partitions**: `preview_file_chunk:{knowledge_id}:{md5_hash}_partitions` - Bbox data
- **File names**: `file_name:{uuid}` - Original filename mapping (24h expiration)

**Sources:** [src/backend/bisheng/api/services/knowledge_imp.py:88-172](), [src/backend/bisheng/api/services/knowledge.py:376-389]()

## Chunk Management and Editing

The system provides interactive chunk editing through the `Paragraphs` component, allowing users to modify chunks after processing:

**Chunk Management Flow**

```mermaid
graph TD
    FileList["File List View<br/>Files.tsx"]
    ChunkView["Chunk Editor<br/>Paragraphs.tsx"]
    Preview["Preview File<br/>PreviewFile.tsx"]
    Editor["Paragraph Editor<br/>PreviewParagraph.tsx"]
    
    FileList -->|"Click file"| ChunkView
    ChunkView --> Preview
    ChunkView --> Editor
    
    subgraph "Chunk Operations"
        Load["Load chunks via<br/>getKnowledgeChunkApi"]
        Edit["Edit text content"]
        BboxSelect["Select bbox regions"]
        Update["Update via<br/>updateChunkApi"]
        Delete["Delete via<br/>delChunkApi"]
    end
    
    subgraph "Preview Features"
        PDFView["PDF with bbox highlights"]
        TxtView["Text/Markdown viewer"]
        DocxView["DOCX preview"]
        ExcelView["Excel preview"]
    end
    
    ChunkView --> Load
    Editor --> Edit
    Preview --> BboxSelect
    Edit --> Update
    Editor --> Delete
    
    Preview --> PDFView
    Preview --> TxtView
    Preview --> DocxView
    Preview --> ExcelView
```

### Bounding Box Support

For documents processed with ETL4LM, chunks include bounding box coordinates that map text to specific regions in the document:

**Bbox Data Structure:**
```typescript
interface ChunkBbox {
  page: number;           // Page number (1-based)
  bbox: [x0, y0, x1, y1]; // Coordinates in PDF points
}

interface BboxMetadata {
  chunk_bboxes: ChunkBbox[];
}
```

**Interactive Selection:**
1. User clicks on highlighted regions in PDF preview
2. Frontend tracks selected bboxes via `useKnowledgeStore.selectedBbox`
3. Selected regions are synchronized across chunks
4. Updates sent to backend via `updateChunkApi`

**Partition Data** (stored in MinIO `partitions/{file_id}.json`):
```json
{
  "page-x0-y0-x1-y1": {
    "text": "extracted text",
    "type": "Title|Text|Table",
    "part_id": 0
  }
}
```

The frontend uses this data to enable region-based chunk editing where users can select/deselect text blocks to rebuild chunks.

**Sources:** [src/frontend/platform/src/pages/KnowledgePage/components/Paragraphs.tsx:166-188](), [src/backend/bisheng/api/services/knowledge_imp.py:698-716](), [src/frontend/platform/src/pages/KnowledgePage/components/PreviewFile.tsx:79-134]()

### Chunk Editing API

**Get Chunks:**
```
GET /api/v1/knowledge/chunks?knowledge_id={id}&file_ids[]={file_id}&page={page}&page_size={size}
```
Returns paginated chunks with metadata.

**Update Chunk:**
```
PUT /api/v1/knowledge/chunk
{
  "knowledge_id": 123,
  "file_id": 456,
  "chunk_index": 0,
  "text": "updated text",
  "bbox": "{\"chunk_bboxes\": [...]}"
}
```
Updates both Milvus and Elasticsearch in real-time.

**Delete Chunk:**
```
DELETE /api/v1/knowledge/chunk
{
  "knowledge_id": 123,
  "file_id": 456,
  "chunk_index": 0
}
```
Removes chunk from both vector and text indexes.

**Sources:** [src/backend/bisheng/api/v1/knowledge.py:1-100](), [src/frontend/platform/src/controllers/API/index.ts:1-300]()

## Metadata Management

The system supports custom metadata fields for knowledge bases, allowing users to add structured information to chunks:

**Metadata System Architecture**

```mermaid
graph LR
    subgraph "Built-in Metadata"
        DocID["document_id"]
        DocName["document_name"]
        UploadTime["upload_time"]
        UpdateTime["update_time"]
        Uploader["uploader"]
        Page["page"]
        ChunkIdx["chunk_index"]
    end
    
    subgraph "Custom Metadata"
        UserDef["user_metadata<br/>(JSON field)"]
        CustomFields["field_name: field_value"]
    end
    
    subgraph "Field Types"
        StringType["String"]
        NumberType["Number"]
        TimeType["Time"]
    end
    
    UserDef --> CustomFields
    CustomFields --> StringType
    CustomFields --> NumberType
    CustomFields --> TimeType
```

**Metadata Operations:**

**Add Metadata Fields:**
```
POST /api/v1/knowledge/add_metadata_fields
{
  "knowledge_id": 123,
  "metadata_fields": [
    {"field_name": "department", "field_type": "string"},
    {"field_name": "priority", "field_type": "number"}
  ]
}
```

**Update File User Metadata:**
```
PUT /api/v1/knowledge/file/user_metadata
{
  "knowledge_file_id": 456,
  "user_metadata_list": [
    {"field_name": "department", "field_value": "Engineering"},
    {"field_name": "priority", "field_value": 1}
  ]
}
```

**Field Validation:**
- Field names must match `^[a-z][a-z0-9_]*$` (lowercase, alphanumeric, underscore)
- Field names cannot conflict with built-in fields
- Maximum field name length: 255 characters

**Sources:** [src/frontend/platform/src/pages/KnowledgePage/components/MetadataManagementDialog.tsx:1-400](), [src/backend/bisheng/api/v1/knowledge.py:200-250]()

## Adjustment and Re-segmentation

The system allows users to adjust segmentation strategies for already-processed files through the `AdjustFilesUpload` component:

**Re-segmentation Workflow**

```mermaid
sequenceDiagram
    participant User
    participant Paragraphs as Paragraphs.tsx
    participant Adjust as AdjustFilesUpload.tsx
    participant API as /api/v1/knowledge/process/rebuild
    participant Worker as retry_knowledge_file_celery
    
    User->>Paragraphs: Click "Adjust Segmentation"
    Paragraphs->>Adjust: Navigate with file data
    Note over Adjust: Displays Step 1: Segmentation Strategy<br/>Pre-filled with existing rules
    User->>Adjust: Modify chunk_size, separators, etc.
    User->>Adjust: Preview results (Step 2)
    User->>Adjust: Confirm changes
    Adjust->>API: POST rebuild request
    API->>Worker: Delete existing vectors
    Worker->>Worker: Re-parse with new rules
    Worker->>Worker: Generate new embeddings
    Worker-->>Adjust: Processing status updates
    Adjust->>User: Show completion
```

**Adjustment Process:**

1. **Entry Point**: User clicks "Adjust Segmentation" button in `Paragraphs.tsx`
2. **Navigation**: Navigate to `/filelib/adjust/{knowledge_id}` with `fileData` in state
3. **Configuration**: `AdjustFilesUpload` displays `FileUploadStep2` with pre-filled split rules
4. **Preview**: Same preview system as initial upload (Step 2 → Step 3)
5. **Submission**: Calls `POST /api/v1/knowledge/process/rebuild`
6. **Processing**: 
   - Deletes existing vectors via `delete_knowledge_file_vectors`
   - Queues `retry_knowledge_file_celery` task
   - Re-parses file with new configuration
   - Updates status to `PROCESSING` → `SUCCESS`/`FAILED`

**API Endpoint:**
```
POST /api/v1/knowledge/process/rebuild
{
  "knowledge_id": 123,
  "kb_file_id": 456,
  "separator": ["\\n\\n"],
  "separator_rule": ["after"],
  "chunk_size": 1500,
  "chunk_overlap": 150,
  "excel_rule": {...}
}
```

**Sources:** [src/frontend/platform/src/pages/KnowledgePage/components/Paragraphs.tsx:512-533](), [src/frontend/platform/src/pages/KnowledgePage/AdjustFilesUpload.tsx:1-200](), [src/backend/bisheng/api/services/knowledge.py:592-631]()

## API Endpoints

### Knowledge Base Operations

| Endpoint | Method | Purpose | Key Parameters |
|----------|--------|---------|----------------|
| `POST /api/v1/knowledge` | POST | Create knowledge base | `name`, `description`, `model` (embedding model ID) |
| `GET /api/v1/knowledge` | GET | List knowledge bases | `page`, `page_size`, `name`, `type` (0/1/2) |
| `PUT /api/v1/knowledge` | PUT | Update knowledge base | `knowledge_id`, `name`, `description` |
| `DELETE /api/v1/knowledge` | DELETE | Delete knowledge base | `knowledge_id` |
| `POST /api/v1/knowledge/copy` | POST | Copy knowledge base | `knowledge_id`, `knowledge_name` |

**Sources:** [src/backend/bisheng/api/v1/knowledge.py:1-100]()

### File Processing Endpoints

| Endpoint | Method | Purpose | Key Parameters |
|----------|--------|---------|----------------|
| `POST /api/v1/knowledge/upload` | POST | Upload files to MinIO tmp | `file` (multipart) |
| `POST /api/v1/knowledge/process` | POST | Process uploaded files | `knowledge_id`, `file_list`, `separator`, `chunk_size`, `chunk_overlap` |
| `POST /api/v1/knowledge/process/rebuild` | POST | Re-process with new config | `knowledge_id`, `kb_file_id`, segmentation params |
| `POST /api/v1/knowledge/preview` | POST | Preview chunks (SSE) | Same as `/process` but returns preview |
| `GET /api/v1/knowledge/file_list/{knowledge_id}` | GET | List files | `page`, `page_size`, `file_name`, `status` |
| `DELETE /api/v1/knowledge/file/{file_id}` | DELETE | Delete file | `file_id` |
| `POST /api/v1/knowledge/retry` | POST | Retry failed files | `file_objs` (list of files) |

**Sources:** [src/backend/bisheng/api/v1/knowledge.py:100-350]()

### Chunk Management Endpoints

| Endpoint | Method | Purpose | Key Parameters |
|----------|--------|---------|----------------|
| `GET /api/v1/knowledge/chunks` | GET | Get paginated chunks | `knowledge_id`, `file_ids`, `page`, `page_size` |
| `PUT /api/v1/knowledge/chunk` | PUT | Update chunk | `knowledge_id`, `file_id`, `chunk_index`, `text`, `bbox` |
| `DELETE /api/v1/knowledge/chunk` | DELETE | Delete chunk | `knowledge_id`, `file_id`, `chunk_index` |
| `PUT /api/v1/knowledge/chunk/preview` | PUT | Update preview chunk | Same as update but targets Redis cache |
| `DELETE /api/v1/knowledge/chunk/preview` | DELETE | Delete preview chunk | Same as delete but targets Redis cache |

**Sources:** [src/backend/bisheng/api/v1/knowledge.py:1-200]()

### Metadata Management Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `POST /api/v1/knowledge/add_metadata_fields` | POST | Add custom metadata fields to knowledge base |
| `PUT /api/v1/knowledge/update_metadata_fields` | PUT | Rename metadata fields |
| `DELETE /api/v1/knowledge/delete_metadata_fields` | DELETE | Remove metadata fields |
| `GET /api/v1/knowledge/file/info/{file_id}` | GET | Get file info with user metadata |
| `PUT /api/v1/knowledge/file/user_metadata` | PUT | Set user metadata for specific file |

**Sources:** [src/backend/bisheng/api/v1/knowledge.py:200-300]()

### QA Knowledge Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `POST /api/v1/knowledge/qa/add` | POST | Add Q&A pairs |
| `GET /api/v1/knowledge/qa/list/{qa_knowledge_id}` | GET | List Q&A pairs |
| `PUT /api/v1/knowledge/qa` | PUT | Update Q&A pair |
| `DELETE /api/v1/knowledge/qa` | DELETE | Delete Q&A pair |
| `GET /api/v1/knowledge/qa/export/{qa_knowledge_id}` | GET | Export Q&A to Excel |
| `POST /api/v1/knowledge/qa/import/{qa_knowledge_id}` | POST | Import Q&A from Excel |

**Sources:** [src/backend/bisheng/api/v1/knowledge.py:400-617]()

## Background Processing

### Celery Worker Tasks

The system uses Celery for asynchronous file processing with multiple specialized worker tasks:

**Async Processing Flow**

```mermaid
graph TD
    API["KnowledgeService<br/>process_knowledge_file"]
    SaveDB["Save KnowledgeFile<br/>status=PROCESSING"]
    Queue["Celery Queue"]
    
    Worker1["parse_knowledge_file_celery<br/>Initial processing"]
    Worker2["retry_knowledge_file_celery<br/>Re-processing"]
    Worker3["file_copy_celery<br/>Knowledge base copy"]
    Worker4["rebuild_knowledge_celery<br/>Rebuild embeddings"]
    
    Process["process_file_task<br/>addEmbedding"]
    Delete["delete_knowledge_file_vectors"]
    Success["Update status=SUCCESS"]
    Failed["Update status=FAILED"]
    
    API --> SaveDB
    SaveDB --> Queue
    Queue --> Worker1
    Queue --> Worker2
    Queue --> Worker3
    Queue --> Worker4
    
    Worker1 --> Process
    Worker2 --> Delete
    Worker2 --> Process
    Worker3 --> Process
    Worker4 --> Delete
    Worker4 --> Process
    
    Process --> Success
    Process --> Failed
```

### Key Worker Tasks

**`parse_knowledge_file_celery(file_id, preview_cache_key, callback_url)`**

Main processing task queued after file upload:

1. Loads `KnowledgeFile` record by ID
2. Validates status is `PROCESSING`
3. Extracts split rules from `split_rule` JSON field
4. Calls `process_file_task` with configuration
5. Updates status to `SUCCESS` or `FAILED`
6. Optionally calls `callback_url` with result

**Sources:** [src/backend/bisheng/worker/knowledge/file_worker.py:247-302]()

**`retry_knowledge_file_celery(file_id, preview_cache_key, callback_url)`**

Retry task for failed or duplicate files:

1. Deletes existing vectors via `delete_knowledge_file_vectors`
2. Calls `_parse_knowledge_file` to re-process
3. Preserves original file in MinIO (no re-upload)
4. Used for both failed files and duplicate resolution

**Sources:** [src/backend/bisheng/worker/knowledge/file_worker.py:304-322]()

**`file_copy_celery(params)`**

Copies all files from source to target knowledge base:

1. Queries files from source knowledge base (paginated)
2. For each file:
   - Copies MySQL record with new knowledge_id
   - Copies MinIO objects (original, bbox, preview)
   - Copies vectors from source Milvus collection
   - Copies ES documents with updated IDs
3. Updates knowledge base state when complete

**Parameters:**
```python
{
  "source_knowledge_id": 123,
  "target_id": 456,
  "login_user_id": 789
}
```

**Sources:** [src/backend/bisheng/worker/knowledge/file_worker.py:26-79]()

**`rebuild_knowledge_celery(knowledge_id, new_model_id, invoke_user_id)`**

Rebuilds entire knowledge base with new embedding model:

1. Updates all successful files to status `REBUILDING` (4)
2. Deletes all vectors from Milvus (keeps ES for text)
3. For each file:
   - Fetches chunks from Elasticsearch
   - Generates new embeddings with new model
   - Inserts into Milvus
4. Updates files to `SUCCESS` or `FAILED`
5. Updates knowledge base state

**Sources:** [src/backend/bisheng/worker/knowledge/rebuild_knowledge_worker.py:22-106]()

### File Status Transitions

```mermaid
stateDiagram-v2
    [*] --> PROCESSING: File uploaded
    PROCESSING --> SUCCESS: Processing complete
    PROCESSING --> FAILED: Processing error
    FAILED --> PROCESSING: Retry triggered
    SUCCESS --> REBUILDING: Rebuild triggered
    REBUILDING --> SUCCESS: Rebuild complete
    REBUILDING --> FAILED: Rebuild error
    
    note right of PROCESSING
        status = 1
        Parsing document
    end note
    
    note right of SUCCESS
        status = 2
        Vectors stored
    end note
    
    note right of FAILED
        status = 3
        Error in remark field
    end note
    
    note right of REBUILDING
        status = 4
        Re-generating embeddings
    end note
```

**Status Values:**

| Status | Value | Description | Displayed As |
|--------|-------|-------------|--------------|
| `PROCESSING` | 1 | File being parsed/embedded | "Parsing" (blue) |
| `SUCCESS` | 2 | Successfully processed | "Completed" (green) |
| `FAILED` | 3 | Processing failed | "Parse Failed" (red) |
| `REBUILDING` | 4 | Re-embedding with new model | "Parsing" (blue, merged with 1) |

**Error Tracking:**

Failed files store error details in the `remark` field as JSON:
```json
{
  "status_code": "KNOWLEDGE_FILE_FAILED",
  "data": {
    "exception": "error message"
  }
}
```

Common error codes:
- `KNOWLEDGE_FILE_EMPTY`: File parsed but no text extracted
- `KNOWLEDGE_FILE_CHUNK_MAX`: Chunk exceeds 10,000 characters
- `KNOWLEDGE_FILE_DAMAGED`: PDF file corrupted
- `KNOWLEDGE_ETL4LM_TIMEOUT`: ETL4LM service timeout
- `KNOWLEDGE_FILE_NOT_SUPPORTED`: Unsupported file format

**Sources:** [src/backend/bisheng/knowledge/domain/models/knowledge_file.py:15-19](), [src/frontend/platform/src/pages/KnowledgePage/components/Files.tsx:36-91]()

## QA Management System

### QA Knowledge Structure

QA knowledge bases store question-answer pairs with the following structure:

```mermaid
graph LR
    subgraph "QA Knowledge"
        Questions["questions: List[str]"]
        Answer["answers: str (JSON)"]
        Source["source: int"]
        Status["status: int"]
        Knowledge["knowledge_id: int"]
    end
    
    subgraph "Source Types"
        Manual["1: Manual Entry"]
        Audit["2: Audit Creation"]
        API["3: API Import"]
        Batch["4: Batch Import"]
    end
    
    subgraph "Status Types"
        Disabled["0: Disabled"]
        Enabled["1: Enabled"]
        Processing["2: Processing"]
        Failed["3: Failed"]
    end
    
    Source --> Manual
    Source --> Audit
    Source --> API
    Source --> Batch
    
    Status --> Disabled
    Status --> Enabled
    Status --> Processing
    Status --> Failed
```

**Sources:** [src/backend/bisheng/database/models/knowledge_file.py:59-95](), [src/backend/bisheng/database/models/knowledge_file.py:243-340]()

### QA Import/Export

The system supports Excel-based batch import/export of QA data:

- **Template Generation**: Creates Excel templates with proper column structure
- **Batch Import**: Processes Excel files with question/answer pairs
- **Similar Question Support**: Handles multiple similar questions per answer
- **Export Functionality**: Generates Excel files with current QA data

**Sources:** [src/backend/bisheng/api/v1/knowledge.py:422-617]()

## Cache and Preview System

### Preview Caching

The system implements Redis-based caching for file preview data:

- **Cache Key Format**: `preview_file_chunk:{knowledge_id}:{md5_hash}`
- **Chunk Editing**: Allows real-time editing of document chunks before processing
- **Cache Management**: Automatic cleanup after processing completion

**Sources:** [src/backend/bisheng/api/services/knowledge_imp.py:83-149](), [src/backend/bisheng/api/services/knowledge.py:389-465]()

---

# Page: Chat and Messaging System

# Chat and Messaging System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/backend/bisheng/api/services/assistant_agent.py](src/backend/bisheng/api/services/assistant_agent.py)
- [src/backend/bisheng/api/services/base.py](src/backend/bisheng/api/services/base.py)
- [src/backend/bisheng/api/v1/callback.py](src/backend/bisheng/api/v1/callback.py)
- [src/backend/bisheng/api/v1/chat.py](src/backend/bisheng/api/v1/chat.py)
- [src/backend/bisheng/api/v1/mark_task.py](src/backend/bisheng/api/v1/mark_task.py)
- [src/backend/bisheng/api/v1/schema/chat_schema.py](src/backend/bisheng/api/v1/schema/chat_schema.py)
- [src/backend/bisheng/api/v1/schema/mark_schema.py](src/backend/bisheng/api/v1/schema/mark_schema.py)
- [src/backend/bisheng/chat/client.py](src/backend/bisheng/chat/client.py)
- [src/backend/bisheng/chat/handlers.py](src/backend/bisheng/chat/handlers.py)
- [src/backend/bisheng/chat/manager.py](src/backend/bisheng/chat/manager.py)
- [src/backend/bisheng/database/models/mark_app_user.py](src/backend/bisheng/database/models/mark_app_user.py)
- [src/backend/bisheng/database/models/mark_record.py](src/backend/bisheng/database/models/mark_record.py)
- [src/backend/bisheng/database/models/mark_task.py](src/backend/bisheng/database/models/mark_task.py)
- [src/backend/bisheng/database/models/message.py](src/backend/bisheng/database/models/message.py)
- [src/backend/bisheng/utils/linked_list.py](src/backend/bisheng/utils/linked_list.py)
- [src/backend/bisheng/utils/threadpool.py](src/backend/bisheng/utils/threadpool.py)

</details>



## Purpose and Scope

The Chat and Messaging System manages real-time chat sessions, message persistence, and user feedback collection within the Bisheng platform. It provides WebSocket-based communication for interactive conversations with AI assistants and workflows, tracks user interactions through like/dislike/copy mechanisms, and implements a comprehensive marking/annotation task system for quality assurance workflows.

The system consists of three primary subsystems:
1. **Real-time Chat**: WebSocket-based communication with message streaming and session management
2. **Message Management**: Persistent storage of chat history with categorization and metadata tracking
3. **Marking System**: Task assignment and session annotation for QA workflows with navigation support

For information about the knowledge retrieval aspects of chat interactions, see [Knowledge Management](#3.1). For details about assistant and agent orchestration during chat, see [Assistant System](#3.3). For workflow execution triggered through chat, see [Workflow Engine](#3.5).

## System Architecture

### Chat System Architecture

```mermaid
graph TB
    subgraph "API Layer"
        ChatRouter["APIRouter(tags=['Chat'])<br/>src/backend/bisheng/api/v1/chat.py"]
        ChatCompletions["@router.post('/chat/completions')<br/>chat_completions()"]
        WebSocketEndpoint["@router.websocket('/chat/{flow_id}')<br/>chat()"]
        AppListEndpoint["@router.get('/chat/app/list')<br/>get_app_chat_list()"]
        MarkRouter["APIRouter(prefix='/mark')<br/>src/backend/bisheng/api/v1/mark_task.py"]
    end
    
    subgraph "Connection Management"
        ChatManager["ChatManager<br/>manager.py:78"]
        ActiveConnections["active_connections<br/>Dict[str, WebSocket]"]
        ActiveClients["active_clients<br/>Dict[str, ChatClient]"]
        DispatchClient["dispatch_client()<br/>manager.py:196"]
    end
    
    subgraph "Client Processing"
        ChatClient["ChatClient<br/>client.py:26"]
        WorkflowClient["WorkflowClient<br/>clients/workflow_client.py"]
        HandleMessage["handle_message()<br/>client.py:61"]
        HandleGptsMessage["handle_gpts_message()<br/>client.py:257"]
    end
    
    subgraph "Message Processing" 
        Handler["Handler<br/>handlers.py:28"]
        DispatchTask["dispatch_task()<br/>handlers.py:41"]
        AsyncCallbackHandler["AsyncStreamingLLMCallbackHandler<br/>callback.py:22"]
        AsyncGptsCallback["AsyncGptsDebugCallbackHandler<br/>callback.py:412"]
        StreamQueue["stream_queue<br/>Queue"]
    end
    
    subgraph "Business Logic"
        AssistantAgent["AssistantAgent<br/>assistant_agent.py:43"]
        InitAssistant["init_assistant()<br/>assistant_agent.py:80"]
        RunAgent["run()<br/>assistant_agent.py:527"]
        ThreadPoolManager["ThreadPoolManager<br/>threadpool.py:10"]
    end
    
    subgraph "Data Access"
        ChatMessageDao["ChatMessageDao<br/>message.py:138"]
        MessageSessionDao["MessageSessionDao<br/>session.py"]
        MarkTaskDao["MarkTaskDao<br/>mark_task.py:41"]
        MarkRecordDao["MarkRecordDao<br/>mark_record.py:37"]
    end
    
    subgraph "Storage"
        MySQL[("MySQL<br/>ChatMessage, MessageSession")]
        RedisFlowDataStore["redis_client<br/>flow_data_store"]
    end
    
    ChatRouter --> ChatCompletions
    ChatRouter --> WebSocketEndpoint
    ChatRouter --> AppListEndpoint
    ChatRouter --> MarkRouter
    
    WebSocketEndpoint --> ChatManager
    ChatManager --> ActiveConnections
    ChatManager --> ActiveClients
    ChatManager --> DispatchClient
    
    DispatchClient --> ChatClient
    DispatchClient --> WorkflowClient
    ChatClient --> HandleMessage
    HandleMessage --> HandleGptsMessage
    
    ChatClient --> Handler
    Handler --> DispatchTask
    Handler --> AsyncCallbackHandler
    Handler --> AsyncGptsCallback
    Handler --> StreamQueue
    
    HandleGptsMessage --> AssistantAgent
    AssistantAgent --> InitAssistant
    AssistantAgent --> RunAgent
    Handler --> ThreadPoolManager
    
    ChatClient --> ChatMessageDao
    ChatManager --> MessageSessionDao
    MarkRouter --> MarkTaskDao
    MarkRouter --> MarkRecordDao
    
    ChatMessageDao --> MySQL
    MessageSessionDao --> MySQL
    MarkTaskDao --> MySQL
    MarkRecordDao --> MySQL
    WebSocketEndpoint --> RedisFlowDataStore
```

**Sources:** [src/backend/bisheng/api/v1/chat.py:48-715](), [src/backend/bisheng/api/v1/mark_task.py:19-261]()

### WebSocket Communication Flow

```mermaid
sequenceDiagram
    participant Client
    participant ChatEndpoint as "chat() function<br/>chat.py:487"
    participant ChatManager as "ChatManager<br/>manager.py"
    participant ChatClient as "ChatClient<br/>client.py"
    participant AssistantAgent as "AssistantAgent<br/>assistant_agent.py"
    participant AsyncCallback as "AsyncGptsDebugCallbackHandler<br/>callback.py:412"
    participant ChatMessageDao as "ChatMessageDao<br/>message.py"
    participant RedisFlowData as "flow_data_store<br/>redis_client"
    
    Client->>ChatEndpoint: "WebSocket Connect + JWT token"
    ChatEndpoint->>ChatEndpoint: "Authorize.jwt_required(auth_from='websocket')"
    ChatEndpoint->>RedisFlowData: "flow_data_store.hget(flow_data_key, 'status')"
    RedisFlowData-->>ChatEndpoint: "BuildStatus.SUCCESS.value"
    ChatEndpoint->>ChatManager: "dispatch_client(WorkType.GPTS)"
    ChatManager->>ChatClient: "ChatClient(client_key, client_id, chat_id)"
    ChatManager->>ChatManager: "accept_client(client_key, chat_client)"
    
    loop "Message Processing Loop"
        Client->>ChatClient: "websocket.receive_json()"
        ChatClient->>ChatClient: "handle_message(message)" 
        ChatClient->>ChatClient: "init_gpts_agent()"
        ChatClient->>AssistantAgent: "AssistantAgent(assistant, chat_id)"
        ChatClient->>AssistantAgent: "init_assistant(callbacks)"
        ChatClient->>AssistantAgent: "run(input_msg, chat_history, callbacks)"
        AssistantAgent->>AsyncCallback: "on_llm_new_token(), on_tool_start()"
        AsyncCallback-->>Client: "websocket.send_json(ChatResponse)"
        AssistantAgent->>ChatMessageDao: "insert_one(ChatMessage)"
        ChatClient-->>Client: "send_response('answer', 'end')"
    end
    
    Client->>ChatEndpoint: "WebSocket Disconnect"
    ChatManager->>ChatManager: "close_client(client_key)"
```

**Sources:** [src/backend/bisheng/api/v1/chat.py:506-561]()

## Core Components

### ChatManager and Client Architecture

The chat system uses a dual-architecture approach with `ChatManager` coordinating multiple `ChatClient` instances:

```mermaid
graph TB
    subgraph "ChatManager State<br/>manager.py:78"
        ActiveConnections["active_connections<br/>Dict[str, WebSocket]"]
        ActiveClients["active_clients<br/>Dict[str, ChatClient]"]
        ChatHistory["chat_history<br/>ChatHistory():Subject"]
        TaskManager["task_manager<br/>List[asyncio.Task]"]
        StreamQueue["stream_queue<br/>Dict[str, Queue]"]
    end
    
    subgraph "Client Types"
        ChatClientType["ChatClient<br/>WorkType.GPTS<br/>client.py:26"]
        WorkflowClientType["WorkflowClient<br/>WorkType.WORKFLOW<br/>clients/workflow_client.py"]
    end
    
    subgraph "Message Processing Methods"
        HandleMessage["handle_message()<br/>client.py:61"]
        HandleGptsMessage["handle_gpts_message()<br/>client.py:257"]
        WrapperTask["wrapper_task()<br/>client.py:75"]
        ThreadPoolSubmit["thread_pool.submit()<br/>threadpool.py:25"]
    end
    
    subgraph "Key Manager Methods"
        DispatchClient["dispatch_client()<br/>manager.py:196"]
        AcceptClient["accept_client()<br/>manager.py:173"]
        CloseClient["close_client()<br/>manager.py:184"]
        HandleWebsocket["handle_websocket()<br/>manager.py:262"]
    end
    
    ActiveConnections --> DispatchClient
    ActiveClients --> AcceptClient
    ChatHistory --> HandleWebsocket
    
    DispatchClient --> ChatClientType
    DispatchClient --> WorkflowClientType
    
    ChatClientType --> HandleMessage
    WorkflowClientType --> HandleMessage
    
    HandleMessage --> HandleGptsMessage
    HandleMessage --> WrapperTask
    WrapperTask --> ThreadPoolSubmit
    
    AcceptClient --> ChatClientType
    CloseClient --> ActiveClients
```

**Sources:** [src/backend/bisheng/api/v1/chat.py:49-50]()

### WebSocket Chat Handler

The main chat endpoint at `/chat/{flow_id}` provides real-time communication through WebSocket connections:

```mermaid
graph LR
    subgraph "chat_function_flow"["chat() Function Flow<br/>chat.py:487"]
        JWTValidation["Authorize.jwt_required()<br/>auth_from='websocket'"]
        FlowValidation["session.get(Flow, flow_id)<br/>db_flow.status == 2"]
        BuildStatusCheck["flow_data_store.hget()<br/>BuildStatus.SUCCESS.value"]
        ManagerDispatch["chat_manager.dispatch_client()"]
    end
    
    subgraph "work_type_routing"["WorkType Routing"]
        GPTSType["WorkType.GPTS<br/>Assistant interactions"]
        WorkflowType["WorkType.WORKFLOW<br/>Flow execution"]
    end
    
    subgraph "function_parameters"["Function Parameters"]
        FlowIDParam["flow_id: UUID<br/>@router.websocket('/chat/{flow_id}')"]
        ChatIDParam["chat_id: Optional[str]<br/>Query parameter"]
        VersionIDParam["version_id: Optional[int]<br/>Query parameter"]
        TokenParam["t: Optional[str]<br/>JWT Token"]
        AuthorizeParam["Authorize: AuthJWT<br/>Depends()"]
    end
    
    subgraph "error_handling"["Error Handling"]
        PolicyViolation["status.WS_1008_POLICY_VIOLATION<br/>'该技能已被删除'"]
        InternalError["status.WS_1011_INTERNAL_ERROR<br/>'Error in chat websocket'"]
        TryAgainLater["status.WS_1013_TRY_AGAIN_LATER<br/>'当前编译没通过'"]
    end
    
    FlowIDParam --> JWTValidation
    ChatIDParam --> FlowValidation
    VersionIDParam --> BuildStatusCheck
    TokenParam --> JWTValidation
    AuthorizeParam --> JWTValidation
    
    JWTValidation --> FlowValidation
    FlowValidation --> BuildStatusCheck
    BuildStatusCheck --> ManagerDispatch
    
    ManagerDispatch --> GPTSType
    ManagerDispatch --> WorkflowType
    
    FlowValidation --> PolicyViolation
    BuildStatusCheck --> TryAgainLater
    ManagerDispatch --> InternalError
```

**Sources:** [src/backend/bisheng/api/v1/chat.py:506-561]()

### Message Data Model and Streaming

The `ChatMessage` model represents individual chat messages with comprehensive metadata:

| Field | Type | Purpose |
|-------|------|---------|
| `id` | int | Primary key |
| `flow_id` | str | Associated skill/assistant ID |
| `chat_id` | str | Session identifier |
| `user_id` | int | User who sent message |
| `is_bot` | bool | Distinguishes human vs AI messages |
| `message` | str | Message content |
| `type` | str | Message type (human/bot/stream) |
| `category` | str | Message category (question/answer/tool_call/tool_result) |
| `liked` | int | User rating (LikedType: UNRATED=0, LIKED=1, DISLIKED=2) |
| `copied` | int | Copy tracking |
| `sensitive_status` | int | Content moderation status |
| `intermediate_steps` | str | Process logs |
| `files` | str | Attached files JSON |
| `sender` | str | AutoGen sender identification |
| `receiver` | dict | AutoGen receiver data |
| `remark` | str | Special flags (e.g., 'break_answer') |

**Sources:** [src/backend/bisheng/database/models/message.py:14-58]()

### Streaming and Callback System

The chat system implements comprehensive streaming through callback handlers:

```mermaid
graph TB
    subgraph "Callback Handlers"
        AsyncCallback["AsyncStreamingLLMCallbackHandler<br/>WebSocket streaming"]
        AsyncGPTSCallback["AsyncGptsDebugCallbackHandler<br/>GPTS-specific callbacks"]
        StreamCallback["StreamingLLMCallbackHandler<br/>Sync streaming"]
    end
    
    subgraph "Stream Events"
        LLMToken["on_llm_new_token()<br/>Token-by-token streaming"]
        ToolStart["on_tool_start()<br/>Tool execution start"]
        ToolEnd["on_tool_end()<br/>Tool execution complete"]
        AgentAction["on_agent_action()<br/>Agent reasoning"]
        ChainEvents["on_chain_start/end()<br/>Chain execution"]
    end
    
    subgraph "Stream Management"
        StreamQueue["stream_queue: Queue<br/>Buffered content"]
        WebSocketSend["websocket.send_json()<br/>Real-time delivery"]
        MessagePersist["ChatMessageDao.insert_one()<br/>Database storage"]
    end
    
    AsyncCallback --> LLMToken
    AsyncCallback --> ToolStart
    AsyncCallback --> ToolEnd
    AsyncCallback --> AgentAction
    AsyncCallback --> ChainEvents
    
    LLMToken --> StreamQueue
    ToolStart --> WebSocketSend
    ToolEnd --> WebSocketSend
    AgentAction --> WebSocketSend
    
    StreamQueue --> MessagePersist
```

**Sources:** [src/backend/bisheng/api/v1/chat.py:506-561]()

### Chat Session Management

The system manages chat sessions through the `MessageSession` model and `MessageSessionDao` data access operations:

#### MessageSession Data Model

The `MessageSession` table stores chat session metadata with the following key fields:

| Field | Type | Purpose |
|-------|------|---------|
| `chat_id` | str | Unique session identifier (primary key) |
| `flow_id` | str | Associated application/skill ID |
| `flow_type` | int | Application type (FlowType enum) |
| `flow_name` | str | Display name of application |
| `user_id` | int | Session owner |
| `like` | int | Count of liked messages |
| `dislike` | int | Count of disliked messages |
| `copied` | int | Count of copied messages |
| `sensitive_status` | int | Content moderation status |
| `is_delete` | int | Soft delete flag (0=active, 1=deleted) |

#### Session Operations

```mermaid
graph TD
    subgraph "MessageSessionDao Operations"
        CreateSession["insert_one()<br/>Create new session"]
        GetSession["get_one(chat_id)<br/>Retrieve session"]
        FilterSessions["filter_session()<br/>Query with filters"]
        UpdateStatus["update_sensitive_status()<br/>Content moderation"]
        UpdateCounters["add_like_count()<br/>add_dislike_count()<br/>add_copied_count()"]
        DeleteSession["delete_session(chat_id)<br/>Soft delete (is_delete=1)"]
    end
    
    subgraph "Session Lifecycle"
        NewChat["User initiates chat<br/>POST /chat/message"]
        OngoingChat["Messages exchanged<br/>WebSocket /chat/{flow_id}"]
        UserFeedback["User likes/dislikes<br/>POST /liked"]
        SessionEnd["Session deleted<br/>DELETE /chat/{chat_id}"]
    end
    
    NewChat --> CreateSession
    OngoingChat --> GetSession
    UserFeedback --> UpdateCounters
    SessionEnd --> DeleteSession
    
    CreateSession --> UpdateStatus
    UpdateCounters --> FilterSessions
```

**Sources:** [src/backend/bisheng/database/models/session.py](), [src/backend/bisheng/api/v1/chat.py:266-365](), [src/backend/bisheng/api/v1/chat.py:404-450]()

## Chat Message Operations

### Message Lifecycle Management

The `ChatMessageDao` class provides comprehensive message operations:

```mermaid
graph LR
    subgraph "Create Operations"
        InsertOne["insert_one()<br/>Single message"]
        InsertBatch["insert_batch()<br/>Multiple messages"]
    end
    
    subgraph "Read Operations" 
        GetByID["get_message_by_id()"]
        GetByChatID["get_messages_by_chat_id()"]
        GetLatest["get_latest_message_by_chat_ids()"]
        FilterMessages["Message filtering & pagination"]
    end
    
    subgraph "Update Operations"
        UpdateMessage["update_message_model()"]
        UpdateLiked["Like/dislike updates"]
        UpdateCopied["update_message_copied()"]
        UpdateMark["update_message_mark()"]
    end
    
    subgraph "Delete Operations"
        DeleteByChat["delete_by_user_chat_id()"]
        DeleteByMessage["delete_by_message_id()"]
    end
```

**Sources:** [src/backend/bisheng/database/models/message.py:143-369]()

### Message Interaction Tracking

The system tracks user interactions with messages:

```mermaid
stateDiagram-v2
    [*] --> Unrated: New Message
    Unrated --> Liked: User likes (liked=1)
    Unrated --> Disliked: User dislikes (liked=2)
    Liked --> Disliked: Change rating
    Disliked --> Liked: Change rating
    Liked --> Unrated: Remove rating
    Disliked --> Unrated: Remove rating
    
    Unrated --> Copied: User copies
    Liked --> Copied: User copies
    Disliked --> Copied: User copies
```

**Sources:** [src/backend/bisheng/api/v1/chat.py:404-456]()

## Chat Annotation and Quality Control System

### Marking Tasks and Records

The chat system includes a sophisticated annotation system for quality control through `MarkTask` and `MarkRecord` models:

```mermaid
graph TB
    subgraph "Task Management"
        CreateTask["MarkTaskDao.create_task()<br/>MarkTaskCreate schema"]
        TaskList["get_task_list()<br/>Filtering by status, user"]
        TaskStatus["MarkTaskStatus<br/>DEFAULT=1, ING=3, DONE=2"]
        UserAssignment["MarkAppUser<br/>Many-to-many app-user relations"]
    end
    
    subgraph "Record Management"
        MarkRecord["MarkRecordDao.create_record()<br/>Individual session marking"]
        RecordStatus["MarkRecordStatus<br/>DEFAULT=1, DONE=2, NO=3"]
        StatusTracking["get_status()<br/>User-specific status"]
        ProgressCount["get_count()<br/>Aggregated progress"]
    end
    
    subgraph "Navigation System"
        PrevNext["/next endpoint<br/>prev/next actions"]
        DoubleLinkList["DoubleLinkList<br/>utils/linked_list.py"]
        ChatNavigation["Sequential chat review<br/>find(), append(), head()"]
        TaskCompletion["Auto-completion check<br/>m_list == app_record"]
    end
    
    subgraph "API Endpoints"
        ListAPI["/mark/list<br/>Task listing"]
        CreateAPI["/mark/create_task<br/>Task creation"]
        MarkAPI["/mark/mark<br/>Session marking"]
        NavigateAPI["/mark/next<br/>Navigation"]
        StatusAPI["/mark/get_status<br/>Status check"]
    end
    
    CreateTask --> UserAssignment
    CreateTask --> TaskStatus
    
    MarkRecord --> RecordStatus
    MarkRecord --> StatusTracking
    StatusTracking --> ProgressCount
    
    PrevNext --> DoubleLinkList
    DoubleLinkList --> ChatNavigation
    MarkRecord --> TaskCompletion
    
    ListAPI --> TaskList
    CreateAPI --> CreateTask
    MarkAPI --> MarkRecord
    NavigateAPI --> PrevNext
    StatusAPI --> StatusTracking
```

**Sources:** [src/backend/bisheng/api/v1/mark_task.py:22-261](), [src/backend/bisheng/database/models/mark_task.py:13-134](), [src/backend/bisheng/database/models/mark_record.py:13-112](), [src/backend/bisheng/utils/linked_list.py:17-150]()

### Chat Application List with Marking Integration

The system provides filtered chat lists for annotation workflows:

```mermaid
graph LR
    subgraph "Filter Parameters"
        Keyword["keyword: Optional[str]<br/>Search flows/users"]
        MarkUser["mark_user: Optional[str]<br/>Filter by marker"]
        MarkStatus["mark_status: Optional[int]<br/>Filter by status"]
        TaskID["task_id: Optional[int]<br/>Specific task"]
        FlowType["flow_type: Optional[int]<br/>Assistant vs Flow"]
    end
    
    subgraph "Permission System"
        AdminCheck["login_user.is_admin()<br/>Full access"]
        GroupAdmin["UserGroupDao.get_user_admin_group()<br/>Group permissions"]
        TaskAuth["task.process_users<br/>Task-specific access"]
    end
    
    subgraph "Data Assembly"
        SessionFilter["MessageSessionDao.filter_session()<br/>Core chat data"]
        StatusLookup["MarkRecordDao.filter_records()<br/>Marking status"]
        AppChatList["AppChatList schema<br/>Combined result"]
    end
    
    Keyword --> SessionFilter
    MarkUser --> StatusLookup
    MarkStatus --> StatusLookup
    TaskID --> TaskAuth
    
    AdminCheck --> SessionFilter
    GroupAdmin --> TaskAuth
    TaskAuth --> SessionFilter
    
    SessionFilter --> AppChatList
    StatusLookup --> AppChatList
```

**Sources:** [src/backend/bisheng/api/v1/chat.py:53-152]()

## API Endpoints

### REST API Routes

The chat system exposes multiple REST endpoints for different functionalities:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/chat/completions` | POST | OpenAI-compatible chat completions |
| `/chat/app/list` | GET | Application chat list with marking filters |
| `/chat/history` | GET | Chat message history pagination |
| `/chat/conversation/rename` | POST | Rename chat sessions |
| `/chat/conversation/copy` | POST | Copy chat sessions |
| `/chat/{chat_id}` | DELETE | Delete chat sessions + cleanup |
| `/chat/message` | POST | Add complete Q&A records |
| `/chat/message/{message_id}` | PUT/DELETE | Update/delete messages |
| `/liked` | POST | Rate messages (LikedType values) |
| `/chat/copied` | POST | Track message copying |
| `/chat/comment` | POST | Add message comments |
| `/chat/list` | GET | User chat session list |
| `/chat/online` | GET | Available online skills/assistants |
| `/chat/{flow_id}` | WebSocket | Real-time chat communication |

**Sources:** [src/backend/bisheng/api/v1/chat.py:48-715]()

### Marking System API Routes

The annotation system provides dedicated endpoints for quality control workflows:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/mark/list` | GET | List marking tasks with progress |
| `/mark/create_task` | POST | Create new annotation task |
| `/mark/mark` | POST | Mark individual chat session |
| `/mark/get_status` | GET | Get marking status for session |
| `/mark/get_user` | GET | Get users assigned to task |
| `/mark/next` | GET | Navigate to next/prev session |
| `/mark/get_record` | GET | Get marking record details |
| `/mark/del` | DELETE | Delete marking task |

**Sources:** [src/backend/bisheng/api/v1/mark_task.py:22-261]()

### Build System Integration

The chat system integrates with a build system for flow compilation and graph execution:

```mermaid
graph TB
    subgraph "Build API Endpoints"
        InitBuildEndpoint["@router.post('/build/init/{flow_id}')<br/>init_build()<br/>chat.py:554"]
        StreamBuildEndpoint["@router.get('/build/stream/{flow_id}')<br/>stream_build()<br/>chat.py:607"]
        StatusEndpoint["@router.get('/build/{flow_id}/status')<br/>build_status()<br/>chat.py:590"]
    end
    
    subgraph "BuildStatus Enum Values"
        BuildStatusStarted["BuildStatus.STARTED.value<br/>'started'"]
        BuildStatusInProgress["BuildStatus.IN_PROGRESS.value<br/>'in_progress'"]
        BuildStatusSuccess["BuildStatus.SUCCESS.value<br/>'success'"]
        BuildStatusFailure["BuildStatus.FAILURE.value<br/>'failure'"]
    end
    
    subgraph "Redis Flow Data Store"
        FlowDataKeyBase["flow_data_key = 'flow_data_' + flow_id"]
        FlowDataKeyVersion["flow_data_key + '_' + str(version_id)"]
        GraphDataField["flow_data_store.hget(key, 'graph_data')"]
        StatusField["flow_data_store.hget(key, 'status')"]
        ExpireTime["expire = 600  # Redis 60s expiration"]
    end
    
    subgraph "Build Process Flow"
        BuildFlowGenerator["build_flow(graph_data, artifacts)<br/>async generator"]
        GraphAbuild["await graph.abuild()<br/>Node compilation"]
        InputKeysResponse["build_input_keys_response()<br/>Interface extraction"]
        ChatHistoryEmpty["chat_manager.chat_history.empty_history()"]
        SetCacheNone["chat_manager.set_cache(key, None)"]
    end
    
    subgraph "Response Types"
        InitResponse["InitResponse(flowId=flow_id)"]
        BuiltResponse["BuiltResponse(built=bool)"]
        StreamData["StreamData(event, data)"]
        StreamingResponse["StreamingResponse(event_stream)"]
    end
    
    InitBuildEndpoint --> BuildStatusStarted
    StreamBuildEndpoint --> BuildStatusInProgress
    BuildStatusInProgress --> BuildFlowGenerator
    BuildFlowGenerator --> GraphAbuild
    GraphAbuild --> InputKeysResponse
    InputKeysResponse --> BuildStatusSuccess
    BuildFlowGenerator --> BuildStatusFailure
    
    InitBuildEndpoint --> FlowDataKeyBase
    InitBuildEndpoint --> FlowDataKeyVersion
    FlowDataKeyBase --> GraphDataField
    FlowDataKeyBase --> StatusField
    FlowDataKeyBase --> ExpireTime
    
    BuildStatusSuccess --> ChatHistoryEmpty
    BuildStatusSuccess --> SetCacheNone
    
    InitBuildEndpoint --> InitResponse
    StatusEndpoint --> BuiltResponse
    StreamBuildEndpoint --> StreamingResponse
```

**Sources:** [src/backend/bisheng/api/v1/chat.py:563-715]()

## Integration Points

### External System Connections

The chat system connects to other platform components:

```mermaid
graph TB
    subgraph "Chat System Core"
        ChatAPI["Chat API Router"]
        ChatManager["ChatManager"]
        MessageDB["Message Storage"]
    end
    
    subgraph "Connected Systems"
        KnowledgeService["Knowledge Service<br/>RAG Integration"]
        AssistantService["Assistant Service<br/>Agent Tools"]
        WorkflowEngine["Workflow Engine<br/>Graph Execution"]
        AuditService["AuditLogService<br/>Activity Logging"]
    end
    
    subgraph "External Services"
        Redis["Redis Cache<br/>Session State"]
        Milvus["Vector Storage<br/>Temporary Collections"]
        Elasticsearch["Text Search<br/>Cleanup Operations"]
    end
    
    ChatAPI --> ChatManager
    ChatManager --> WorkflowEngine
    ChatAPI --> AuditService
    
    ChatManager --> KnowledgeService
    ChatManager --> AssistantService
    
    MessageDB --> Redis
    ChatAPI --> Milvus
    ChatAPI --> Elasticsearch
```

**Sources:** [src/backend/bisheng/api/v1/chat.py:13-42](), [src/backend/bisheng/api/v1/chat.py:246-261]()

---

# Page: Assistant System

# Assistant System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/backend/bisheng/api/services/assistant.py](src/backend/bisheng/api/services/assistant.py)
- [src/backend/bisheng/api/services/assistant_agent.py](src/backend/bisheng/api/services/assistant_agent.py)
- [src/backend/bisheng/api/services/base.py](src/backend/bisheng/api/services/base.py)
- [src/backend/bisheng/api/services/flow.py](src/backend/bisheng/api/services/flow.py)
- [src/backend/bisheng/api/services/knowledge.py](src/backend/bisheng/api/services/knowledge.py)
- [src/backend/bisheng/api/services/knowledge_imp.py](src/backend/bisheng/api/services/knowledge_imp.py)
- [src/backend/bisheng/api/services/workflow.py](src/backend/bisheng/api/services/workflow.py)
- [src/backend/bisheng/api/v1/assistant.py](src/backend/bisheng/api/v1/assistant.py)
- [src/backend/bisheng/api/v1/callback.py](src/backend/bisheng/api/v1/callback.py)
- [src/backend/bisheng/api/v1/flows.py](src/backend/bisheng/api/v1/flows.py)
- [src/backend/bisheng/api/v1/schemas.py](src/backend/bisheng/api/v1/schemas.py)
- [src/backend/bisheng/api/v1/skillcenter.py](src/backend/bisheng/api/v1/skillcenter.py)
- [src/backend/bisheng/api/v1/workflow.py](src/backend/bisheng/api/v1/workflow.py)
- [src/backend/bisheng/chat/client.py](src/backend/bisheng/chat/client.py)
- [src/backend/bisheng/chat/handlers.py](src/backend/bisheng/chat/handlers.py)
- [src/backend/bisheng/chat/manager.py](src/backend/bisheng/chat/manager.py)
- [src/backend/bisheng/database/models/assistant.py](src/backend/bisheng/database/models/assistant.py)
- [src/backend/bisheng/database/models/flow.py](src/backend/bisheng/database/models/flow.py)
- [src/backend/bisheng/database/models/flow_version.py](src/backend/bisheng/database/models/flow_version.py)
- [src/backend/bisheng/database/models/template.py](src/backend/bisheng/database/models/template.py)
- [src/backend/bisheng/database/models/user_link.py](src/backend/bisheng/database/models/user_link.py)
- [src/backend/bisheng/utils/threadpool.py](src/backend/bisheng/utils/threadpool.py)
- [src/backend/bisheng/worker/knowledge/file_worker.py](src/backend/bisheng/worker/knowledge/file_worker.py)
- [src/backend/bisheng/worker/knowledge/qa.py](src/backend/bisheng/worker/knowledge/qa.py)
- [src/backend/bisheng/worker/knowledge/rebuild_knowledge_worker.py](src/backend/bisheng/worker/knowledge/rebuild_knowledge_worker.py)

</details>



## Purpose and Scope

The Assistant System provides the core infrastructure for creating, managing, and executing conversational AI assistants (also called GPTS) within the Bisheng platform. This system handles the complete lifecycle of assistants, from creation and configuration through real-time conversation execution with support for tools, skills (flows), and knowledge bases.

For workflow-based applications, see [Workflow Engine](#3.5). For knowledge base integration details, see [Knowledge Base Management](#3.1). For general application lifecycle management across all application types, see [Application Lifecycle Management](#3.6).

---

## System Architecture

The Assistant System is built on a layered architecture consisting of API endpoints, service layer, agent orchestration, and real-time chat handling:

```mermaid
graph TB
    subgraph "API Layer"
        API["/assistant<br/>FastAPI Router"]
        CREATE["/assistant POST"]
        UPDATE["/assistant PUT"]
        STATUS["/assistant/status POST"]
        WS["/assistant/chat/{id}<br/>WebSocket"]
        AUTO["/assistant/auto GET<br/>SSE Stream"]
    end
    
    subgraph "Service Layer"
        AS["AssistantService<br/>CRUD Operations"]
        AS_CREATE["create_assistant()"]
        AS_UPDATE["update_assistant()"]
        AS_STATUS["update_status()"]
        AS_AUTO["auto_update_stream()"]
    end
    
    subgraph "Agent Orchestration"
        AA["AssistantAgent<br/>Agent Management"]
        AA_INIT["init_assistant()"]
        AA_LLM["init_llm()"]
        AA_TOOLS["init_tools()"]
        AA_AGENT["init_agent()"]
        AA_RUN["run() / astream()"]
    end
    
    subgraph "Chat Management"
        CM["ChatManager<br/>WebSocket Manager"]
        CC["ChatClient<br/>GPTS Handler"]
        CC_INIT["init_gpts_agent()"]
        CC_HANDLE["handle_gpts_message()"]
    end
    
    subgraph "Data Layer"
        ASSISTANT_DB[("Assistant<br/>Main Table")]
        LINK_DB[("AssistantLink<br/>Tool/Flow/KB")]
        SESSION_DB[("MessageSession<br/>Chat Sessions")]
        MESSAGE_DB[("ChatMessage<br/>History")]
    end
    
    API --> AS
    CREATE --> AS_CREATE
    UPDATE --> AS_UPDATE
    STATUS --> AS_STATUS
    AUTO --> AS_AUTO
    WS --> CM
    
    AS_CREATE --> ASSISTANT_DB
    AS_UPDATE --> ASSISTANT_DB
    AS_STATUS --> AA_INIT
    
    CM --> CC
    CC --> CC_INIT
    CC_INIT --> AA
    CC_HANDLE --> AA_RUN
    
    AA_INIT --> AA_LLM
    AA_INIT --> AA_TOOLS
    AA_INIT --> AA_AGENT
    
    AA --> ASSISTANT_DB
    AA --> LINK_DB
    CC --> SESSION_DB
    CC --> MESSAGE_DB
```

**Sources**: [src/backend/bisheng/api/v1/assistant.py:1-177](), [src/backend/bisheng/api/services/assistant.py:1-517](), [src/backend/bisheng/api/services/assistant_agent.py:1-421](), [src/backend/bisheng/chat/client.py:1-372](), [src/backend/bisheng/chat/manager.py:1-447]()

---

## Data Model

### Assistant Entity

The `Assistant` model represents an AI assistant configuration stored in the database:

| Field | Type | Description |
|-------|------|-------------|
| `id` | str | Unique identifier (UUID) |
| `name` | str | Assistant display name |
| `logo` | str | Path to logo image in MinIO |
| `desc` | str | User-visible description |
| `system_prompt` | str | Internal system prompt (not user-visible) |
| `prompt` | str | User-visible prompt/instructions |
| `guide_word` | str | Opening greeting message |
| `guide_question` | List | Suggested starter questions |
| `model_name` | str | LLM model ID from model management |
| `temperature` | float | Model temperature (default: 0.5) |
| `max_token` | int | Maximum context window (default: 32000) |
| `status` | int | Online (2) or Offline (1) status |
| `user_id` | int | Creator user ID |
| `is_delete` | int | Soft delete flag |

The `AssistantStatus` enum defines valid status values at [src/backend/bisheng/database/models/assistant.py:17-19]().

### Assistant Link Entity

The `AssistantLink` model creates many-to-many relationships between assistants and their capabilities:

| Field | Type | Description |
|-------|------|-------------|
| `assistant_id` | str | Assistant ID reference |
| `tool_id` | int | Tool ID (if linking a tool) |
| `flow_id` | str | Flow/skill ID (if linking a flow) |
| `knowledge_id` | int | Knowledge base ID (if linking KB) |

Each assistant can have multiple links to tools, flows, and knowledge bases. The system validates that each link has exactly one non-zero foreign key field.

**Sources**: [src/backend/bisheng/database/models/assistant.py:22-61](), [src/backend/bisheng/api/v1/schemas.py:244-293]()

---

## Assistant Lifecycle Management

### Creation Flow

```mermaid
sequenceDiagram
    participant UI as "Frontend UI"
    participant API as "POST /assistant"
    participant AS as "AssistantService"
    participant LLM as "LLMService"
    participant DB as "Database"
    participant GR as "GroupResourceDao"
    participant AL as "AuditLogService"
    
    UI->>API: Create assistant request
    API->>AS: create_assistant()
    AS->>AS: judge_name_repeat()
    AS->>LLM: get_assistant_llm()
    LLM-->>AS: Default model config
    AS->>AS: get_auto_info()
    AS->>DB: Insert Assistant
    AS->>GR: Link to user groups
    AS->>AL: Log audit event
    AS-->>API: AssistantInfo
    API-->>UI: Success response
```

The creation process implements several automatic features:

1. **Name Validation**: Checks for duplicate names within user scope via `judge_name_repeat()` at [src/backend/bisheng/api/services/assistant.py:448-453]()
2. **Default Model Selection**: Automatically assigns default LLM from configuration at [src/backend/bisheng/api/services/assistant.py:162-167]()
3. **Auto Description**: Generates description from prompt using `get_auto_info()` at [src/backend/bisheng/api/services/assistant.py:456-468]()
4. **Group Association**: Links assistant to creator's user groups via `create_assistant_hook()` at [src/backend/bisheng/api/services/assistant.py:189-211]()

**Sources**: [src/backend/bisheng/api/services/assistant.py:151-187](), [src/backend/bisheng/api/v1/assistant.py:58-66]()

### Update and Status Management

Assistant updates are handled by `update_assistant()` which validates several constraints:

```mermaid
graph TD
    START["update_assistant()"]
    CHECK_PERM["Check write permission"]
    CHECK_STATUS{"Assistant<br/>online?"}
    CHECK_NAME{"Name<br/>changed?"}
    VALIDATE_NAME["Validate unique name"]
    UPDATE_BASIC["Update basic fields"]
    UPDATE_TOOLS{"tool_list<br/>not None?"}
    UPDATE_FLOWS{"flow_list<br/>not None?"}
    UPDATE_KB{"knowledge_list<br/>not None?"}
    HOOK["update_assistant_hook()"]
    END["Return AssistantInfo"]
    
    START --> CHECK_PERM
    CHECK_PERM --> CHECK_STATUS
    CHECK_STATUS -->|Offline| CHECK_NAME
    CHECK_STATUS -->|Online| REJECT["Raise AssistantNotEditError"]
    CHECK_NAME -->|Yes| VALIDATE_NAME
    CHECK_NAME -->|No| UPDATE_BASIC
    VALIDATE_NAME --> UPDATE_BASIC
    UPDATE_BASIC --> UPDATE_TOOLS
    UPDATE_TOOLS -->|Yes| UPDATE_FLOWS
    UPDATE_TOOLS -->|No| UPDATE_FLOWS
    UPDATE_FLOWS -->|Yes| UPDATE_KB
    UPDATE_FLOWS -->|No| UPDATE_KB
    UPDATE_KB --> HOOK
    HOOK --> END
```

Key update rules:
- **Online assistants cannot be edited** except for status changes (offline → online or vice versa)
- Name changes require uniqueness validation via `judge_name_repeat()`
- Tool, flow, and knowledge lists use `None` to indicate no change, empty list `[]` to clear associations
- All updates trigger `update_assistant_hook()` for audit logging and cache updates

Status changes are special-cased in `update_status()` at [src/backend/bisheng/api/services/assistant.py:343-369](), which validates the assistant can be initialized before setting status to online.

**Sources**: [src/backend/bisheng/api/services/assistant.py:284-341](), [src/backend/bisheng/api/services/assistant.py:343-369](), [src/backend/bisheng/api/v1/assistant.py:79-86]()

---

## Agent Orchestration and Execution

### AssistantAgent Architecture

The `AssistantAgent` class at [src/backend/bisheng/api/services/assistant_agent.py:34-421]() serves as the core orchestrator for assistant execution:

```mermaid
graph TB
    subgraph "Initialization Phase"
        AGENT["AssistantAgent<br/>Constructor"]
        INIT_LLM["init_llm()<br/>Model Setup"]
        INIT_TOOLS["init_tools()<br/>Tool Loading"]
        INIT_AGENT["init_agent()<br/>Executor Creation"]
    end
    
    subgraph "LLM Configuration"
        GET_LLM["LLMService.get_assistant_llm()"]
        SELECT_MODEL["Select model by model_name"]
        CREATE_LLM["LLMService.get_bisheng_llm()"]
        CONFIG["temperature, streaming<br/>app_id, user_id"]
    end
    
    subgraph "Tool Integration"
        LOAD_LINKS["AssistantLinkDao.get_assistant_link()"]
        TOOL_EXEC["ToolExecutor.init_by_tool_ids()"]
        KB_TOOL["ToolExecutor.init_knowledge_tool()"]
        FLOW_BUILD["build_flow_no_yield()"]
        TOOLS["List[BaseTool]"]
    end
    
    subgraph "Agent Executor Types"
        REACT["ReAct Agent<br/>ConfigurableAssistant"]
        FUNC_CALL["Function Calling<br/>create_react_agent()"]
    end
    
    AGENT --> INIT_LLM
    AGENT --> INIT_TOOLS
    AGENT --> INIT_AGENT
    
    INIT_LLM --> GET_LLM
    GET_LLM --> SELECT_MODEL
    SELECT_MODEL --> CREATE_LLM
    CREATE_LLM --> CONFIG
    
    INIT_TOOLS --> LOAD_LINKS
    LOAD_LINKS --> TOOL_EXEC
    LOAD_LINKS --> KB_TOOL
    LOAD_LINKS --> FLOW_BUILD
    TOOL_EXEC --> TOOLS
    KB_TOOL --> TOOLS
    FLOW_BUILD --> TOOLS
    
    INIT_AGENT --> REACT
    INIT_AGENT --> FUNC_CALL
```

**Sources**: [src/backend/bisheng/api/services/assistant_agent.py:53-76](), [src/backend/bisheng/api/services/assistant_agent.py:78-107](), [src/backend/bisheng/api/services/assistant_agent.py:122-190](), [src/backend/bisheng/api/services/assistant_agent.py:192-223]()

### LLM Initialization

The `init_llm()` method at [src/backend/bisheng/api/services/assistant_agent.py:78-107]() performs model configuration:

1. Retrieves assistant LLM configuration via `LLMService.get_assistant_llm()`
2. Matches `assistant.model_name` to configured models
3. Falls back to default model if specified model not found
4. Creates LLM instance with telemetry tracking (app_id, app_name, app_type, user_id)
5. Stores agent executor type and knowledge retriever parameters

The system supports two agent executor types stored in `llm_agent_executor`:
- `"ReAct"` - Traditional ReAct agent pattern
- `"function call"` - OpenAI-style function calling

**Sources**: [src/backend/bisheng/api/services/assistant_agent.py:78-107]()

### Tool Initialization

The `init_tools()` method at [src/backend/bisheng/api/services/assistant_agent.py:122-190]() loads three types of tools:

1. **Direct Tools**: Loaded via `ToolExecutor.init_by_tool_ids()` for tool IDs from `AssistantLink`
2. **Knowledge Tools**: Each linked knowledge base becomes a retrieval tool via `ToolExecutor.init_knowledge_tool()`
3. **Flow Tools**: Linked flows are built into callable tools via `build_flow_no_yield()`, wrapped in LangChain `Tool` objects

Flow tools handle offline flows specially by tracking them in `self.offline_flows` and later sending fake callbacks to notify the UI via `fake_callback()` at [src/backend/bisheng/api/services/assistant_agent.py:261-272]().

**Sources**: [src/backend/bisheng/api/services/assistant_agent.py:122-190]()

### Agent Executor Creation

The `init_agent()` method at [src/backend/bisheng/api/services/assistant_agent.py:192-223]() creates the appropriate agent executor:

**ReAct Mode**:
```python
self.agent = ConfigurableAssistant(
    agent_executor_type='get_react_agent_executor',
    tools=self.tools,
    llm=self.llm,
    assistant_message=prompt
)
```

**Function Calling Mode**:
```python
self.agent = create_react_agent(
    self.llm, 
    self.tools, 
    prompt=prompt, 
    checkpointer=False
)
self.agent = self.agent.with_config({'recursion_limit': 100})
```

Special handling for Cohere models uses `ASSISTANT_PROMPT_COHERE` template at [src/backend/bisheng/api/services/assistant_agent.py:36-51]().

**Sources**: [src/backend/bisheng/api/services/assistant_agent.py:192-223]()

### Execution Methods

The agent provides two execution interfaces:

**Synchronous Execution** via `run()` at [src/backend/bisheng/api/services/assistant_agent.py:320-344]():
- Appends user query to chat history
- Trims history to fit within `max_token` via `trim_messages()`
- Executes appropriate agent executor (ReAct or function calling)
- Records full conversation history to file if `BISHENG_RECORD_HISTORY` is set

**Streaming Execution** via `astream()` at [src/backend/bisheng/api/services/assistant_agent.py:346-406]():
- Uses same history management as `run()`
- For function calling mode, uses `agent.astream()` with `stream_mode="messages"` for token-level streaming
- ReAct mode falls back to non-streaming execution
- Yields individual message chunks as they're generated

**Sources**: [src/backend/bisheng/api/services/assistant_agent.py:320-406]()

---

## Real-time Chat Interface

### WebSocket Connection Flow

```mermaid
sequenceDiagram
    participant UI as "Frontend"
    participant WS as "/assistant/chat/{id}<br/>WebSocket"
    participant CM as "ChatManager"
    participant CC as "ChatClient"
    participant AA as "AssistantAgent"
    participant DB as "Database"
    
    UI->>WS: Connect to WebSocket
    WS->>CM: dispatch_client()
    CM->>CC: Create ChatClient
    CM->>CC: accept_client()
    
    loop Message Loop
        UI->>WS: Send message
        WS->>CC: handle_message()
        CC->>CC: Submit to thread pool
        CC->>CC: init_gpts_agent()
        CC->>AA: init_assistant()
        CC->>DB: Load chat history
        CC->>AA: run() or astream()
        AA-->>CC: Response messages
        CC->>DB: Save messages
        CC->>UI: Stream responses
    end
    
    UI->>WS: Disconnect
    WS->>CM: close_client()
```

**Sources**: [src/backend/bisheng/api/v1/assistant.py:158-176](), [src/backend/bisheng/chat/manager.py:204-288](), [src/backend/bisheng/chat/client.py:68-153]()

### ChatClient Implementation

The `ChatClient` class at [src/backend/bisheng/chat/client.py:33-372]() manages individual assistant chat sessions:

**Key Properties**:
- `client_id`: Assistant ID
- `chat_id`: Session ID (empty for debug mode)
- `gpts_agent`: Cached `AssistantAgent` instance
- `chat_history`: In-memory chat history buffer
- `stream_queue`: Queue for collecting streaming output during interruptions

**Message Handling** via `handle_gpts_message()` at [src/backend/bisheng/chat/client.py:294-371]():

1. Checks for stop action to handle interruptions
2. Initializes agent via `init_gpts_agent()` if needed
3. Loads latest chat history (configured rounds via `latest_history_num`)
4. Submits to thread pool with `wrapper_task()` for async execution
5. Invokes `AssistantAgent.run()` with chat history
6. Saves conversation including tool calls to database
7. Streams responses to WebSocket

**History Management** via `get_latest_history()` at [src/backend/bisheng/chat/client.py:227-250]():
- Loads up to `latest_history_num` (default 10) complete Q&A pairs
- Reconstructs message objects: `HumanMessage`, `AIMessage`, `ToolMessage`
- Filters out incomplete conversations (e.g., interrupted answers)
- Includes tool call/result pairs in history

**Sources**: [src/backend/bisheng/chat/client.py:33-372](), [src/backend/bisheng/chat/client.py:171-209](), [src/backend/bisheng/chat/client.py:294-371]()

### Message Categories

The system uses a category-based message tracking scheme:

| Category | Description | `is_bot` | Example |
|----------|-------------|----------|---------|
| `question` | User input | 0 | `{"input": "What is AI?"}` |
| `answer` | Final LLM response | 1 | Plain text answer |
| `reasoning_answer` | Chain-of-thought reasoning | 1 | Internal reasoning steps |
| `tool_call` | Tool invocation | 1 | AIMessage with tool_calls |
| `tool_result` | Tool output | 1 | ToolMessage with result |

Messages are saved via `add_message()` at [src/backend/bisheng/chat/client.py:108-153](), which creates both in-memory entries and database records.

**Sources**: [src/backend/bisheng/chat/client.py:108-153](), [src/backend/bisheng/database/models/message.py]()

---

## Tool and Knowledge Integration

### Tool Integration Architecture

```mermaid
graph TB
    subgraph "Assistant Configuration"
        ASSISTANT["Assistant Entity"]
        LINKS["AssistantLink<br/>tool_id, flow_id, knowledge_id"]
    end
    
    subgraph "Tool Types"
        DIRECT["Direct Tools<br/>GptsTools"]
        KB["Knowledge Tools<br/>Retriever Wrapper"]
        FLOW["Flow Tools<br/>Executable Skills"]
    end
    
    subgraph "Tool Execution"
        TOOL_EXEC["ToolExecutor"]
        INIT_TOOLS["init_by_tool_ids()"]
        INIT_KB["init_knowledge_tool()"]
        BUILD_FLOW["build_flow_no_yield()"]
    end
    
    subgraph "Runtime Tools"
        TOOLS_LIST["List[BaseTool]"]
        TOOL_NAME["name: tool_name"]
        KB_NAME["name: kb_{id}"]
        FLOW_NAME["name: flow_{id}"]
    end
    
    ASSISTANT --> LINKS
    LINKS -->|tool_id| DIRECT
    LINKS -->|knowledge_id| KB
    LINKS -->|flow_id| FLOW
    
    DIRECT --> INIT_TOOLS
    KB --> INIT_KB
    FLOW --> BUILD_FLOW
    
    INIT_TOOLS --> TOOL_EXEC
    INIT_KB --> TOOL_EXEC
    BUILD_FLOW --> TOOL_EXEC
    
    TOOL_EXEC --> TOOLS_LIST
    TOOLS_LIST --> TOOL_NAME
    TOOLS_LIST --> KB_NAME
    TOOLS_LIST --> FLOW_NAME
```

**Sources**: [src/backend/bisheng/api/services/assistant_agent.py:122-190](), [src/backend/bisheng/tool/domain/services/executor.py]()

### Knowledge Base Tool Integration

Knowledge bases are integrated as retrieval tools at [src/backend/bisheng/api/services/assistant_agent.py:152-156]():

```python
knowledge_tool = await ToolExecutor.init_knowledge_tool(
    self.invoke_user_id, 
    knowledge_id, 
    llm=self.llm,
    callbacks=callbacks,
    **self.knowledge_retriever
)
```

The `knowledge_retriever` dict contains:
- `max_content`: Maximum characters to return (from LLM config)
- `sort_by_source_and_index`: Whether to sort results by source document

Knowledge tools use the system's hybrid retrieval (Milvus vector + Elasticsearch keyword) under the hood. See [Vector Search and Retrieval](#6.3) for details.

**Sources**: [src/backend/bisheng/api/services/assistant_agent.py:94-97](), [src/backend/bisheng/api/services/assistant_agent.py:152-156]()

### Flow Tool Integration

Flows (skills) are converted to tools at [src/backend/bisheng/api/services/assistant_agent.py:157-189]():

1. Retrieves flow data from `FlowDao.get_flow_by_ids()`
2. Checks flow online status, tracking offline flows separately
3. Builds flow graph via `build_flow_no_yield()`
4. Wraps built object in LangChain `Tool` with:
   - Name: `flow_{flow_id}`
   - Description: `{flow.name}:{flow.description}`
   - Args schema: `InputRequest` (simple string input)
   - Coroutine: Flow's `ainvoke` method

Offline flows are tracked in `self.offline_flows` and trigger fake callbacks during execution at [src/backend/bisheng/api/services/assistant_agent.py:261-272]().

**Sources**: [src/backend/bisheng/api/services/assistant_agent.py:157-189]()

---

## Auto-optimization Features

### Auto-generation System

```mermaid
graph TB
    START["User provides<br/>initial prompt"]
    GEN_DESC["generate_description()<br/>Brief summary"]
    OPT_PROMPT["optimize_assistant_prompt()<br/>Improve prompt"]
    GEN_GUIDE["generate_opening_dialog()<br/>Opening + questions"]
    SELECT_TOOLS["choose_tools()<br/>Auto-select tools"]
    SELECT_FLOWS["choose_tools()<br/>Auto-select flows"]
    COMPLETE["Complete assistant<br/>configuration"]
    
    START --> GEN_DESC
    GEN_DESC --> OPT_PROMPT
    OPT_PROMPT --> GEN_GUIDE
    GEN_GUIDE --> SELECT_TOOLS
    SELECT_TOOLS --> SELECT_FLOWS
    SELECT_FLOWS --> COMPLETE
```

**Sources**: [src/backend/bisheng/api/services/assistant.py:456-468](), [src/backend/bisheng/api/services/assistant.py:247-277](), [src/backend/bisheng/api/services/assistant_agent.py:224-259]()

### Auto-update Stream API

The `POST /assistant/auto/task` and `GET /assistant/auto` endpoints at [src/backend/bisheng/api/v1/assistant.py:89-125]() provide streaming auto-optimization:

**Process Flow**:
1. Client submits task with `assistant_id` and new `prompt`
2. System generates `task_id` and caches request in Redis
3. Client opens SSE connection with `task_id`
4. Server streams updates for each optimization step:
   - `type: 'prompt'` - Optimized prompt text chunks
   - `type: 'guide_word'` - Generated opening message
   - `type: 'guide_question'` - Suggested questions
   - `type: 'tool_list'` - Auto-selected tools
   - `type: 'flow_list'` - Auto-selected flows

**Streaming Implementation** via `auto_update_stream()` at [src/backend/bisheng/api/services/assistant.py:247-282]():
- Uses `optimize_assistant_prompt()` for streaming prompt generation via LLM
- Calls `generate_guide()` for opening dialog/questions
- Iterates through tools and flows in batches (50 at a time)
- Invokes `choose_tools()` on each batch with original prompt as context

**Sources**: [src/backend/bisheng/api/v1/assistant.py:89-125](), [src/backend/bisheng/api/services/assistant.py:247-282]()

### Tool Selection Algorithm

The `choose_tools()` method at [src/backend/bisheng/api/services/assistant_agent.py:249-259]() uses LLM-based selection:

```python
tool_selector = ToolSelector(llm=self.llm, tools=tool_list)
return tool_selector.select(self.assistant.name, prompt)
```

The `ToolSelector` from `bisheng_langchain.gpts.auto_tool_selected` evaluates each tool's relevance to the assistant's purpose based on tool descriptions and the user's prompt.

**Auto Tool Selection** at [src/backend/bisheng/api/services/assistant.py:471-496]():
- Loads all user tools in batches of 50
- Converts to `{name, description}` format
- Invokes `choose_tools()` for each batch
- Aggregates selected tools across batches

**Auto Flow Selection** at [src/backend/bisheng/api/services/assistant.py:499-516]():
- Loads top 50 online flows user can access
- Uses same selection algorithm as tools
- Returns flows matching assistant purpose

**Sources**: [src/backend/bisheng/api/services/assistant_agent.py:249-259](), [src/backend/bisheng/api/services/assistant.py:471-516]()

### Prompt Optimization Functions

The system uses functions from `bisheng_langchain.gpts.auto_optimization`:

- **`generate_breif_description(llm, prompt)`** - Creates concise description from prompt
- **`optimize_assistant_prompt(llm, name, description)`** - Improves prompt clarity and effectiveness
- **`generate_opening_dialog(llm, prompt)`** - Generates opening message and 3-5 suggested questions

These are invoked via `AssistantAgent` methods at [src/backend/bisheng/api/services/assistant_agent.py:224-247]():
- `optimize_assistant_prompt()` - Async streaming version
- `generate_description()` - Synchronous brief description
- `generate_guide()` - Opening dialog and questions

**Sources**: [src/backend/bisheng/api/services/assistant_agent.py:224-247](), [src/backend/bisheng_langchain/gpts/auto_optimization.py]()

---

## Database Schema

### Assistant Table Structure

The `assistant` table stores core assistant configurations:

```sql
CREATE TABLE assistant (
    id VARCHAR(32) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    logo VARCHAR(255),
    desc TEXT,
    system_prompt TEXT,
    prompt TEXT,
    guide_word TEXT,
    guide_question JSON,
    model_name VARCHAR(255),
    temperature FLOAT DEFAULT 0.5,
    max_token INT DEFAULT 32000,
    status INT DEFAULT 1,
    user_id INT,
    is_delete INT DEFAULT 0,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_create_time (create_time)
)
```

**Sources**: [src/backend/bisheng/database/models/assistant.py:22-41]()

### AssistantLink Table Structure

The `assistant_link` table creates associations between assistants and capabilities:

```sql
CREATE TABLE assistant_link (
    id INT PRIMARY KEY AUTO_INCREMENT,
    assistant_id VARCHAR(32),
    tool_id INT,
    flow_id VARCHAR(32),
    knowledge_id INT,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_assistant_id (assistant_id),
    INDEX idx_tool_id (tool_id),
    INDEX idx_flow_id (flow_id),
    INDEX idx_knowledge_id (knowledge_id)
)
```

Each row represents one capability link with exactly one of `tool_id`, `flow_id`, or `knowledge_id` set.

**Link Update Methods**:
- `update_assistant_tool()` at [src/backend/bisheng/database/models/assistant.py:220-239]() - Replace tool associations
- `update_assistant_flow()` at [src/backend/bisheng/database/models/assistant.py:241-262]() - Replace flow associations  
- `update_assistant_knowledge()` at [src/backend/bisheng/database/models/assistant.py:264-285]() - Replace KB associations

**Sources**: [src/backend/bisheng/database/models/assistant.py:43-61](), [src/backend/bisheng/database/models/assistant.py:220-285]()

---

## Access Control and Permissions

Assistant access control integrates with the platform's role-based access control system:

**Permission Types**:
- `AccessType.ASSISTANT_READ` - View assistant details, use in chat
- `AccessType.ASSISTANT_WRITE` - Edit assistant configuration, manage status

**Access Check Flow**:
1. Check if user is assistant owner via `assistant.user_id == login_user.user_id`
2. Check if user is system admin via `login_user.is_admin()`
3. Check role-based permissions via `RoleAccessDao.get_role_access()` with user's role IDs
4. Check group-based access via `GroupResourceDao` for shared assistants

The `check_update_permission()` helper at [src/backend/bisheng/api/services/assistant.py:414-422]() enforces:
- User must have write access
- Assistant must be offline for configuration changes
- Online assistants can only have status changed

**Sources**: [src/backend/bisheng/api/services/assistant.py:414-422](), [src/backend/bisheng/api/services/assistant.py:44-96](), [src/backend/bisheng/api/services/assistant.py:110-123]()

---

## Telemetry and Monitoring

The Assistant System integrates comprehensive telemetry tracking:

**Event Types**:
- `NEW_APPLICATION` - Assistant creation at [src/backend/bisheng/api/services/assistant.py:174-181]()
- `EDIT_APPLICATION` - Assistant updates at [src/backend/bisheng/api/services/assistant.py:309-310]()
- `DELETE_APPLICATION` - Assistant deletion at [src/backend/bisheng/api/services/assistant.py:225-227]()
- `NEW_MESSAGE_SESSION` - New chat session at [src/backend/bisheng/chat/client.py:141-151]()
- `APPLICATION_PROCESS` - Message processing time at [src/backend/bisheng/chat/client.py:84-106]()
- `APPLICATION_ALIVE` - Session duration at [src/backend/bisheng/chat/manager.py:277-287]()

**Tracked Metadata**:
- `app_id`: Assistant ID
- `app_name`: Assistant name
- `app_type`: `ApplicationTypeEnum.ASSISTANT`
- `user_id`: Operating user
- `session_id` / `chat_id`: Chat session identifier
- `start_time` / `end_time`: Timestamps for duration events
- `process_time`: Milliseconds for processing events

**Sources**: [src/backend/bisheng/api/services/assistant.py:174-181](), [src/backend/bisheng/chat/client.py:81-106](), [src/backend/bisheng/chat/manager.py:277-287]()

---

## Error Handling

The Assistant System defines specialized error types in `bisheng.common.errcode.assistant`:

| Error | HTTP Status | Scenario |
|-------|-------------|----------|
| `AssistantNotExistsError` | 404 | Assistant ID not found or deleted |
| `AssistantNameRepeatError` | 400 | Name already exists for user |
| `AssistantNotEditError` | 400 | Attempted edit on online assistant |
| `AssistantDeletedError` | 404 | Assistant was deleted |
| `AssistantNotOnlineError` | 400 | Chat attempted with offline assistant |
| `AssistantInitError` | 500 | Failed to initialize agent executor |
| `AssistantModelEmptyError` | 500 | No LLM models configured |
| `AssistantModelNotConfigError` | 500 | Specified model not found |
| `AssistantAutoLLMError` | 500 | Auto-optimization LLM not configured |
| `AssistantOtherError` | 500 | Generic unexpected error |

Errors are raised at appropriate points:
- CRUD operations in `AssistantService`
- Agent initialization in `AssistantAgent.init_assistant()`
- Chat handling in `ChatClient.handle_gpts_message()`

All errors inherit from `BaseErrorCode` and provide structured JSON responses via `websocket_close_message()` for WebSocket contexts.

**Sources**: [src/backend/bisheng/common/errcode/assistant.py](), [src/backend/bisheng/api/services/assistant.py:218-223](), [src/backend/bisheng/chat/client.py:204-209]()

---

# Page: Linsight AI Workbench

# Linsight AI Workbench

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/backend/bisheng/core/cache/redis_conn.py](src/backend/bisheng/core/cache/redis_conn.py)
- [src/backend/bisheng/linsight/domain/task_exec.py](src/backend/bisheng/linsight/domain/task_exec.py)
- [src/backend/bisheng/linsight/domain/utils.py](src/backend/bisheng/linsight/domain/utils.py)
- [src/backend/bisheng/linsight/worker.py](src/backend/bisheng/linsight/worker.py)

</details>



## Purpose and Scope

The Linsight AI Workbench is an AI-driven system for generating and executing Standard Operating Procedures (SOPs). It enables users to submit questions or tasks, automatically generates structured SOPs using LLM agents, and executes those SOPs through an asynchronous workflow engine with support for interactive user input, file processing, and tool invocation.

This page covers the complete Linsight subsystem including question submission, SOP generation, task execution, and the supporting infrastructure. For general chat interactions, see [Chat and Messaging System](#3.2). For knowledge base integration, see [Knowledge Base Management](#3.1). For workflow concepts beyond Linsight, see [Workflow Engine](#3.5).

## System Overview

The Linsight AI Workbench follows a multi-stage pipeline architecture:

```mermaid
graph TB
    subgraph "Frontend Interaction"
        USER[User]
        UI_SUBMIT["Submit Question<br/>+ Files + Tools"]
        UI_GENERATE["Generate SOP<br/>View & Edit"]
        UI_EXECUTE["Execute SOP<br/>Monitor Progress"]
        UI_FEEDBACK["Provide Feedback<br/>& Rating"]
    end
    
    subgraph "API Layer - /api/v1/linsight.py"
        API_SUBMIT["/workbench/submit<br/>POST EventSourceResponse"]
        API_GEN["/workbench/generate-sop<br/>POST EventSourceResponse"]
        API_START["/workbench/start-execute<br/>POST"]
        API_WS["/workbench/task-message-stream<br/>WebSocket"]
        API_INPUT["/workbench/user-input<br/>POST"]
        API_TERMINATE["/workbench/terminate-execute<br/>POST"]
    end
    
    subgraph "Service Layer"
        IMPL["LinsightWorkbenchImpl<br/>workbench_impl.py"]
        SOP_MGR["SOPManageService<br/>sop_manage.py"]
    end
    
    subgraph "Execution Infrastructure"
        QUEUE["LinsightQueue<br/>Redis-based"]
        WORKER["ScheduleCenterProcess<br/>worker.py"]
        TASK_EXEC["LinsightWorkflowTask<br/>task_exec.py"]
        STATE_MGR["LinsightStateMessageManager<br/>state_message_manager.py"]
    end
    
    subgraph "AI Components"
        AGENT["LinsightAgent<br/>bisheng_langchain"]
        LLM["BishengLLM<br/>Task Model"]
        TOOLS["Tool Executor<br/>Code Interpreter, etc"]
    end
    
    subgraph "Storage"
        MYSQL[(MySQL<br/>linsight_session_version<br/>linsight_execute_task<br/>linsight_sop)]
        REDIS[(Redis<br/>Task Queue<br/>State Cache)]
        MILVUS[(Milvus<br/>SOP Vector Store)]
        ES[(Elasticsearch<br/>SOP Keyword Search)]
        MINIO[(MinIO<br/>Files & Results)]
    end
    
    USER --> UI_SUBMIT --> API_SUBMIT
    API_SUBMIT --> IMPL
    
    UI_GENERATE --> API_GEN
    API_GEN --> IMPL
    IMPL --> SOP_MGR
    IMPL --> AGENT
    
    UI_EXECUTE --> API_START
    API_START --> QUEUE
    QUEUE --> WORKER
    WORKER --> TASK_EXEC
    
    TASK_EXEC --> AGENT
    TASK_EXEC --> TOOLS
    TASK_EXEC --> STATE_MGR
    
    UI_EXECUTE -.Monitor.- API_WS
    API_WS -.Stream.- STATE_MGR
    
    UI_FEEDBACK -.User Input.- API_INPUT
    API_INPUT --> STATE_MGR
    
    IMPL --> MYSQL
    IMPL --> MINIO
    SOP_MGR --> MILVUS
    SOP_MGR --> ES
    SOP_MGR --> MYSQL
    
    STATE_MGR --> REDIS
    STATE_MGR --> MYSQL
    TASK_EXEC --> MINIO
```

Sources: [src/backend/bisheng/api/v1/linsight.py:48-707](), [src/backend/bisheng/api/services/linsight/workbench_impl.py:68-1313](), [src/backend/bisheng/linsight/worker.py:1-195](), [src/backend/bisheng/linsight/task_exec.py:1-680]()

## Core Components

### Workbench Implementation Layer

The `LinsightWorkbenchImpl` class serves as the main service layer orchestrating Linsight operations:

```mermaid
graph TB
    subgraph "LinsightWorkbenchImpl Class"
        SUBMIT["submit_user_question()<br/>Creates MessageSession<br/>+ LinsightSessionVersion"]
        TITLE["task_title_generate()<br/>Generates title using LLM"]
        GEN_SOP["generate_sop()<br/>Async generator<br/>Streams SOP content"]
        MODIFY["modify_sop()<br/>Updates SOP content"]
        UPLOAD["upload_file()<br/>Returns file_id"]
        PARSE["parse_file()<br/>Background task<br/>Parses & indexes to Milvus"]
        INIT_TOOLS["init_linsight_config_tools()<br/>Initializes selected tools"]
    end
    
    subgraph "Key Methods"
        PREP_FILES["_process_submitted_files()<br/>Validates & copies files"]
        PREP_TOOLS["_prepare_tools()<br/>Initializes tools + linsight tools"]
        CREATE_AGENT["_create_linsight_agent()<br/>Creates LinsightAgent<br/>with file_dir, tools, llm"]
        GEN_CONTENT["_generate_sop_content()<br/>Calls agent.generate_sop()<br/>or agent.feedback_sop()"]
    end
    
    subgraph "Helper Methods"
        GET_LLM["_get_llm()<br/>Gets BishengLLM from<br/>workbench_conf.task_model"]
        PREP_HIST["_prepare_history_summary()<br/>Extracts answers from<br/>previous tasks"]
        PREP_FILE_LIST["prepare_file_list()<br/>Formats file info<br/>for agent"]
        PREP_KB_LIST["prepare_knowledge_list()<br/>Formats KB info<br/>for agent"]
    end
    
    SUBMIT --> PREP_FILES
    GEN_SOP --> GET_LLM
    GEN_SOP --> PREP_TOOLS
    GEN_SOP --> CREATE_AGENT
    GEN_SOP --> PREP_HIST
    GEN_SOP --> GEN_CONTENT
    
    PREP_TOOLS --> INIT_TOOLS
    CREATE_AGENT --> PREP_FILE_LIST
    CREATE_AGENT --> PREP_KB_LIST
    
    UPLOAD --> PARSE
```

**Key Constants and Configuration:**

| Constant | Value | Purpose |
|----------|-------|---------|
| `COLLECTION_NAME_PREFIX` | `"col_linsight_file_"` | Milvus collection naming |
| `FILE_INFO_REDIS_KEY_PREFIX` | `"linsight_file:"` | Redis key for file metadata |
| `CACHE_EXPIRATION_HOURS` | `24` | File cache expiration |

Sources: [src/backend/bisheng/api/services/linsight/workbench_impl.py:68-1313]()

### API Layer

The FastAPI router exposes Linsight functionality through RESTful endpoints and WebSocket:

```mermaid
graph LR
    subgraph "File Management"
        EP_UPLOAD["/workbench/upload-file<br/>POST<br/>UploadFile → file_id"]
        EP_STATUS["/workbench/file-parsing-status<br/>POST<br/>file_ids[] → parsing status"]
    end
    
    subgraph "Question & SOP Lifecycle"
        EP_SUBMIT["/workbench/submit<br/>POST EventSourceResponse<br/>LinsightQuestionSubmitSchema"]
        EP_GEN["/workbench/generate-sop<br/>POST EventSourceResponse<br/>session_version_id"]
        EP_MODIFY["/workbench/sop-modify<br/>POST<br/>sop_content, version_id"]
    end
    
    subgraph "Task Execution"
        EP_START["/workbench/start-execute<br/>POST<br/>Adds to LinsightQueue"]
        EP_WS["/workbench/task-message-stream<br/>WebSocket<br/>Streams MessageData events"]
        EP_INPUT["/workbench/user-input<br/>POST<br/>Sets user input in Redis"]
        EP_TERMINATE["/workbench/terminate-execute<br/>POST<br/>Removes from queue"]
    end
    
    subgraph "Monitoring & Downloads"
        EP_VERSIONS["/workbench/session-version-list<br/>GET<br/>Returns version history"]
        EP_TASKS["/workbench/execute-task-detail<br/>GET<br/>Returns task tree"]
        EP_QUEUE["/workbench/queue-status<br/>GET<br/>Returns queue position"]
        EP_DOWNLOAD["/workbench/batch-download-files<br/>POST<br/>Returns ZIP stream"]
    end
```

**Request/Response Schemas:**

| Schema | Fields | Purpose |
|--------|--------|---------|
| `LinsightQuestionSubmitSchema` | question, tools[], files[], org_knowledge_enabled, personal_knowledge_enabled | Submit user question |
| `SubmitFileSchema` | file_id, file_name, parsing_status | File reference |
| `DownloadFilesSchema` | file_name, file_url | Download specification |
| `UserInputEventSchema` | user_input, files[], is_completed | User interaction data |

Sources: [src/backend/bisheng/api/v1/linsight.py:48-885](), [src/backend/bisheng/api/v1/schema/linsight_schema.py:1-62]()

### Task Execution Engine

The `LinsightWorkflowTask` class manages the execution lifecycle of SOP tasks:

```mermaid
graph TB
    subgraph "LinsightWorkflowTask Lifecycle"
        ENTRY["async_run(session_version_id)<br/>Entry point"]
        MGD_EXEC["_managed_execution()<br/>Context manager<br/>Resource management"]
        EXEC_WF["_execute_workflow()<br/>Core execution logic"]
        CLEANUP["_cleanup_resources()<br/>Stop monitor, delete files"]
    end
    
    subgraph "Initialization Phase"
        GET_SESSION["_get_session_model()<br/>Load from DB"]
        CHECK_STATUS["_is_session_in_progress()<br/>Prevent duplicate runs"]
        INIT_DIR["_init_file_directory()<br/>Download files from MinIO"]
        START_MONITOR["_start_termination_monitor()<br/>Check for user termination"]
    end
    
    subgraph "Execution Phase"
        UPDATE_STATUS["_update_session_status()<br/>Set IN_PROGRESS"]
        GET_LLM_E["_get_llm()<br/>Initialize LLM"]
        GEN_TOOLS["_generate_tools()<br/>Initialize configured tools"]
        CREATE_AGENT_E["_create_agent()<br/>LinsightAgent instance"]
        GEN_TASK["agent.generate_task(sop)<br/>Generate task tree"]
        SAVE_TASK["_save_task_info()<br/>Save to DB & Redis"]
        EXEC_AGENT["_execute_agent_tasks()<br/>Execute with monitoring"]
    end
    
    subgraph "Event Handling"
        HANDLE_EVENT["_handle_event()<br/>Dispatch based on type"]
        H_GEN_SUB["_handle_generate_subtask()<br/>Save new subtasks"]
        H_START["_handle_task_start()<br/>Update status, push message"]
        H_END["_handle_task_end()<br/>Save result, push message"]
        H_INPUT["_handle_need_user_input()<br/>Wait for input"]
        H_STEP["_handle_exec_step()<br/>Log step, upload files"]
    end
    
    subgraph "Completion Phase"
        HANDLE_COMPLETE["_handle_task_completion()"]
        H_SUCCESS["_handle_task_success()<br/>Upload files to MinIO<br/>Set COMPLETED"]
        H_FAILURE["_handle_task_failure()<br/>Set FAILED<br/>Revoke invite code"]
        H_TERMINATE["_handle_user_termination()<br/>Set TERMINATED<br/>Mark tasks failed"]
    end
    
    ENTRY --> MGD_EXEC
    MGD_EXEC --> GET_SESSION
    MGD_EXEC --> CHECK_STATUS
    MGD_EXEC --> INIT_DIR
    MGD_EXEC --> START_MONITOR
    MGD_EXEC --> EXEC_WF
    MGD_EXEC --> CLEANUP
    
    EXEC_WF --> UPDATE_STATUS
    EXEC_WF --> GET_LLM_E
    EXEC_WF --> GEN_TOOLS
    EXEC_WF --> CREATE_AGENT_E
    EXEC_WF --> GEN_TASK
    EXEC_WF --> SAVE_TASK
    EXEC_WF --> EXEC_AGENT
    
    EXEC_AGENT --> HANDLE_EVENT
    HANDLE_EVENT --> H_GEN_SUB
    HANDLE_EVENT --> H_START
    HANDLE_EVENT --> H_END
    HANDLE_EVENT --> H_INPUT
    HANDLE_EVENT --> H_STEP
    
    EXEC_AGENT --> HANDLE_COMPLETE
    HANDLE_COMPLETE --> H_SUCCESS
    HANDLE_COMPLETE --> H_FAILURE
    HANDLE_COMPLETE --> H_TERMINATE
```

**Task Status Enumeration:**

| Status | Description |
|--------|-------------|
| `NOT_STARTED` | Initial state |
| `IN_PROGRESS` | Currently executing |
| `SUCCESS` | Completed successfully |
| `WAITING_FOR_USER_INPUT` | Paused for user interaction |
| `USER_INPUT_COMPLETED` | User provided input |
| `FAILED` | Execution failed |
| `TERMINATED` | User stopped execution |

Sources: [src/backend/bisheng/linsight/task_exec.py:50-680](), [src/backend/bisheng/database/models/linsight_execute_task.py:23-41]()

### SOP Management System

The `SOPManageService` manages a library of reusable SOPs with vector-based search:

```mermaid
graph TB
    subgraph "SOP Library Management"
        ADD["add_sop()<br/>Add to DB, Milvus, ES<br/>Generate vector_store_id"]
        UPDATE["update_sop()<br/>Update content in DB<br/>Refresh vectors"]
        DELETE["remove_sop()<br/>Delete from DB, Milvus, ES"]
        GET["get_sop_by_id()<br/>Retrieve single SOP"]
        LIST["get_sop_list()<br/>Paginated listing"]
    end
    
    subgraph "SOP Search & Retrieval"
        SEARCH["search_sop(query, k=3)<br/>Hybrid search"]
        V_SEARCH["BaselineVectorRetriever<br/>Milvus similarity"]
        K_SEARCH["KeywordRetriever<br/>Elasticsearch BM25"]
        ENSEMBLE["EnsembleRetriever<br/>Combines results"]
        RERANK["Optional reranking"]
    end
    
    subgraph "SOP Record Management"
        ADD_RECORD["add_sop_record()<br/>Save execution record"]
        GET_RECORD["get_sop_record()<br/>Query by keyword, user"]
        SYNC["sync_sop_record()<br/>Promote records to library"]
        UPDATE_SCORE["update_sop_record_score()<br/>Save user rating"]
        UPDATE_FB["update_sop_record_feedback()<br/>Save feedback"]
    end
    
    subgraph "Bulk Operations"
        PARSE["parse_sop_file()<br/>Parse Excel file"]
        UPLOAD["upload_sop_file()<br/>Batch import SOPs"]
        GEN_SUMMARY["generate_sop_summary()<br/>LLM-generated title<br/>& description"]
    end
    
    SEARCH --> V_SEARCH
    SEARCH --> K_SEARCH
    V_SEARCH --> ENSEMBLE
    K_SEARCH --> ENSEMBLE
    ENSEMBLE --> RERANK
    
    ADD --> GEN_SUMMARY
    SYNC --> ADD
    ADD_RECORD --> GEN_SUMMARY
    
    PARSE --> UPLOAD
    UPLOAD --> SYNC
```

**Storage Configuration:**

| Store | Collection/Index | Purpose |
|-------|-----------------|---------|
| Milvus | `col_linsight_sop` | Vector embeddings (first 10k chars) |
| Elasticsearch | `col_linsight_sop` | Full-text keyword search |
| MySQL | `linsight_sop` | SOP metadata & content |
| MySQL | `linsight_sop_record` | Execution history records |

Sources: [src/backend/bisheng/api/services/linsight/sop_manage.py:42-547](), [src/backend/bisheng/database/models/linsight_sop.py:1-311]()

### Worker Infrastructure

The worker system uses Redis-based queuing with multi-process execution:

```mermaid
graph TB
    subgraph "Queue Layer"
        QUEUE_CLASS["LinsightQueue<br/>Redis-backed queue"]
        PUT["put(data)<br/>arpush to Redis"]
        GET_WAIT["get_wait(timeout)<br/>ablpop blocking"]
        GET_NOWAIT["get_nowait()<br/>alpop non-blocking"]
        INDEX["index(data)<br/>Find position in queue"]
        REMOVE["remove(data)<br/>alrem from queue"]
    end
    
    subgraph "Worker Process"
        WORKER["ScheduleCenterProcess<br/>Daemon process"]
        INIT["__init__(max_concurrency)<br/>Set up semaphore"]
        RUN["run()<br/>Process entry point"]
        ASYNC_RUN["async_run()<br/>Main event loop"]
        HANDLE["handle_task_result()<br/>Callback on completion"]
    end
    
    subgraph "Task Execution"
        ACQUIRE["semaphore.acquire()<br/>Limit concurrency"]
        DEQUEUE["queue.get_wait()<br/>Blocking wait"]
        CREATE_TASK["LinsightWorkflowTask()<br/>Create executor"]
        EXEC_ASYNC["exec_task.async_run()<br/>Execute in background"]
        RELEASE["semaphore.release()<br/>Free slot"]
    end
    
    subgraph "Process Management"
        START["start_schedule_center_process()<br/>Start N workers"]
        SPAWN["Process.start()<br/>Fork worker"]
        JOIN["Process.join()<br/>Wait for completion"]
    end
    
    PUT --> QUEUE_CLASS
    GET_WAIT --> QUEUE_CLASS
    
    WORKER --> INIT
    INIT --> RUN
    RUN --> ASYNC_RUN
    
    ASYNC_RUN --> ACQUIRE
    ACQUIRE --> DEQUEUE
    DEQUEUE --> CREATE_TASK
    CREATE_TASK --> EXEC_ASYNC
    EXEC_ASYNC --> HANDLE
    HANDLE --> RELEASE
    
    START --> SPAWN
    SPAWN --> WORKER
```

**Configuration Parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `worker_num` | 4 | Number of worker processes |
| `max_concurrency` | 32 | Tasks per worker process |
| `queue_key` | `linsight:queue` | Redis queue key |

Sources: [src/backend/bisheng/linsight/worker.py:19-195]()

### State and Message Management

The `LinsightStateMessageManager` handles real-time state synchronization:

```mermaid
graph TB
    subgraph "LinsightStateMessageManager"
        INIT["__init__(session_version_id)<br/>Initialize keys"]
        KEYS["Redis Key Structure:<br/>linsight_tasks:{id}:session_version_info<br/>linsight_tasks:{id}:messages<br/>linsight_tasks:{id}:execution_tasks:{task_id}"]
    end
    
    subgraph "Session Management"
        SET_SESSION["set_session_version_info()<br/>Write to DB + Redis<br/>Atomic transaction"]
        GET_SESSION["get_session_version_info()<br/>Read from Redis<br/>Fallback to DB"]
    end
    
    subgraph "Task Management"
        SET_TASKS["set_execution_tasks()<br/>Batch write to Redis<br/>mset operation"]
        GET_TASK["get_execution_task(task_id)<br/>Read single task<br/>Fallback to DB"]
        GET_ALL["get_execution_tasks()<br/>Pattern match keys<br/>Batch read"]
        UPDATE_STATUS["update_execution_task_status()<br/>Update DB then Redis"]
        ADD_STEP["add_execution_task_step()<br/>Append to history<br/>Sync to DB"]
    end
    
    subgraph "Message Streaming"
        PUSH["push_message(MessageData)<br/>arpush to list"]
        POP["pop_message()<br/>ablpop from list"]
        EVENT_TYPES["MessageEventType enum:<br/>TASK_START, TASK_GENERATE<br/>TASK_EXECUTE_STEP, TASK_END<br/>USER_INPUT, ERROR_MESSAGE<br/>FINAL_RESULT, TASK_TERMINATED"]
    end
    
    subgraph "User Input Handling"
        SET_INPUT["set_user_input()<br/>Update task history<br/>Set USER_INPUT_COMPLETED"]
        WAIT_INPUT["Task waits for<br/>status == USER_INPUT_COMPLETED"]
    end
    
    subgraph "Cleanup"
        CLEANUP["cleanup_session_data()<br/>Delete pattern keys"]
        CLEANUP_ALL["cleanup_all_sessions()<br/>Class method"]
        STATS["get_session_stats()<br/>Count messages & tasks"]
    end
    
    INIT --> KEYS
    
    SET_SESSION -.Atomic transaction.- GET_SESSION
    
    SET_TASKS --> GET_TASK
    SET_TASKS --> GET_ALL
    GET_TASK --> UPDATE_STATUS
    UPDATE_STATUS --> ADD_STEP
    
    PUSH --> EVENT_TYPES
    POP --> EVENT_TYPES
    
    SET_INPUT --> WAIT_INPUT
    
    CLEANUP --> CLEANUP_ALL
```

**Retry Configuration:**

| Setting | Value | Purpose |
|---------|-------|---------|
| `DEFAULT_RETRY_ATTEMPTS` | 3 | Number of retry attempts |
| `DEFAULT_RETRY_DELAY` | 1 | Seconds between retries |
| `DEFAULT_EXPIRATION` | 3600 | Redis key TTL in seconds |

Sources: [src/backend/bisheng/linsight/state_message_manager.py:52-481]()

## Data Flow

### Question Submission Flow

```mermaid
sequenceDiagram
    participant User
    participant API as /workbench/submit
    participant Impl as LinsightWorkbenchImpl
    participant Redis
    participant MySQL
    participant MinIO
    
    User->>API: POST question + files + tools
    API->>Impl: submit_user_question()
    
    Impl->>Redis: Check file parsing status
    Redis-->>Impl: File metadata
    
    Impl->>MinIO: Copy files to session storage
    MinIO-->>Impl: New object paths
    
    Impl->>MySQL: Insert MessageSession
    MySQL-->>Impl: chat_id
    
    Impl->>MySQL: Insert LinsightSessionVersion
    MySQL-->>Impl: session_version_id
    
    Impl-->>API: SSE: linsight_workbench_submit event
    API-->>User: session data
    
    Impl->>Impl: task_title_generate()
    Impl->>LLM: Generate title from question
    LLM-->>Impl: Generated title
    
    Impl->>MySQL: Update session title
    
    Impl-->>API: SSE: linsight_workbench_title_generate event
    API-->>User: title data
```

Sources: [src/backend/bisheng/api/v1/linsight.py:109-169](), [src/backend/bisheng/api/services/linsight/workbench_impl.py:129-191](), [src/backend/bisheng/api/services/linsight/workbench_impl.py:250-290]()

### SOP Generation Flow

```mermaid
sequenceDiagram
    participant User
    participant API as /workbench/generate-sop
    participant Impl as LinsightWorkbenchImpl
    participant SOPService as SOPManageService
    participant Agent as LinsightAgent
    participant LLM
    participant Vector as Milvus/ES
    
    User->>API: POST session_version_id
    API->>Impl: generate_sop()
    
    alt No Feedback (Initial Generation)
        Impl->>SOPService: search_sop(query, k=3)
        SOPService->>Vector: Hybrid search
        Vector-->>SOPService: Similar SOPs
        SOPService-->>Impl: SOP templates
    end
    
    Impl->>Impl: _get_llm()
    Impl->>Impl: _prepare_tools()
    Impl->>Impl: _create_linsight_agent()
    
    Impl->>Impl: prepare_file_list()
    Impl->>Impl: prepare_knowledge_list()
    
    alt Initial Generation
        Impl->>Agent: agent.generate_sop(sop_template, file_list, kb_list)
    else With Feedback
        Impl->>Agent: agent.feedback_sop(current_sop, feedback, history)
    end
    
    loop Stream SOP Content
        Agent->>LLM: Generate SOP chunk
        LLM-->>Agent: Content chunk
        Agent-->>Impl: Yield content
        Impl-->>API: SSE: generate_sop_content event
        API-->>User: Stream chunk
    end
    
    Impl->>MySQL: Update session_version.sop
    
    Impl-->>API: SSE: sop_generate_complete event
    API-->>User: Completion notification
```

Sources: [src/backend/bisheng/api/v1/linsight.py:173-273](), [src/backend/bisheng/api/services/linsight/workbench_impl.py:357-449](), [src/backend/bisheng/api/services/linsight/sop_manage.py:475-547]()

### Task Execution Flow

```mermaid
sequenceDiagram
    participant User
    participant API_Start as /workbench/start-execute
    participant Queue as LinsightQueue
    participant Worker as ScheduleCenterProcess
    participant TaskExec as LinsightWorkflowTask
    participant StateMgr as LinsightStateMessageManager
    participant API_WS as WebSocket
    participant Agent as LinsightAgent
    participant MySQL
    participant Redis
    
    User->>API_Start: POST session_version_id
    API_Start->>Queue: queue.put(session_version_id)
    Queue->>Redis: RPUSH to queue
    API_Start-->>User: Task queued
    
    Worker->>Queue: queue.get_wait() [blocking]
    Queue->>Redis: BLPOP from queue
    Redis-->>Queue: session_version_id
    Queue-->>Worker: session_version_id
    
    Worker->>TaskExec: async_run(session_version_id)
    
    TaskExec->>MySQL: Load LinsightSessionVersion
    TaskExec->>StateMgr: Initialize manager
    TaskExec->>StateMgr: Update status=IN_PROGRESS
    StateMgr->>MySQL: Update status
    StateMgr->>Redis: Cache session data
    
    TaskExec->>TaskExec: _init_file_directory()
    TaskExec->>MinIO: Download session files
    
    TaskExec->>TaskExec: _generate_tools()
    TaskExec->>TaskExec: _create_agent()
    
    TaskExec->>Agent: agent.generate_task(sop)
    Agent-->>TaskExec: Task tree structure
    
    TaskExec->>MySQL: Batch insert LinsightExecuteTask
    TaskExec->>StateMgr: set_execution_tasks()
    StateMgr->>Redis: Batch set task data
    StateMgr->>StateMgr: push_message(TASK_GENERATE)
    
    loop Monitor WebSocket Connection
        API_WS->>StateMgr: pop_message()
        StateMgr->>Redis: BLPOP messages
        Redis-->>StateMgr: MessageData
        StateMgr-->>API_WS: Event
        API_WS-->>User: Stream event
    end
    
    TaskExec->>Agent: agent.ainvoke(task_info, sop)
    
    loop For Each Task
        Agent->>Agent: Execute task steps
        
        alt Task Start
            Agent-->>TaskExec: TaskStart event
            TaskExec->>StateMgr: update_execution_task_status(IN_PROGRESS)
            StateMgr->>StateMgr: push_message(TASK_START)
        end
        
        loop Execute Steps
            Agent-->>TaskExec: ExecStep event
            TaskExec->>TaskExec: handle_step_event_extra()
            TaskExec->>MinIO: Upload step files if needed
            TaskExec->>StateMgr: add_execution_task_step()
            StateMgr->>StateMgr: push_message(TASK_EXECUTE_STEP)
        end
        
        alt Need User Input
            Agent-->>TaskExec: NeedUserInput event
            TaskExec->>StateMgr: update_status(WAITING_FOR_USER_INPUT)
            StateMgr->>StateMgr: push_message(USER_INPUT)
            StateMgr-->>API_WS: Stream to user
            API_WS-->>User: Request input
            
            User->>API_Input: POST user input + files
            API_Input->>StateMgr: set_user_input()
            StateMgr->>Redis: Update task with input
            StateMgr->>MySQL: Update task history
            StateMgr->>StateMgr: push_message(USER_INPUT_COMPLETED)
            
            TaskExec->>TaskExec: Wait for status=USER_INPUT_COMPLETED
            TaskExec->>Agent: agent.continue_task(task_id, user_input)
        end
        
        alt Task End
            Agent-->>TaskExec: TaskEnd event
            TaskExec->>StateMgr: update_execution_task_status(SUCCESS/FAILED)
            StateMgr->>StateMgr: push_message(TASK_END)
        end
    end
    
    TaskExec->>TaskExec: _handle_task_success()
    TaskExec->>TaskExec: Read file directory
    TaskExec->>MinIO: Upload final result files
    TaskExec->>MySQL: Update session status=COMPLETED
    TaskExec->>StateMgr: push_message(FINAL_RESULT)
    StateMgr-->>API_WS: Final event
    API_WS-->>User: Completion notification
```

Sources: [src/backend/bisheng/api/v1/linsight.py:307-353](), [src/backend/bisheng/linsight/worker.py:88-118](), [src/backend/bisheng/linsight/task_exec.py:106-680](), [src/backend/bisheng/api/v1/linsight.py:602-651]()

## Key Features

### File Processing Pipeline

Linsight supports file upload, parsing, and indexing for use in SOP execution:

```mermaid
graph LR
    subgraph "Upload Phase"
        UPLOAD["upload_file(UploadFile)"]
        GEN_ID["Generate file_id<br/>8-char hex"]
        SAVE["save_file_to_folder()<br/>CACHE_DIR/linsight/"]
        CACHE_UPLOAD["Cache to Redis<br/>status=running"]
    end
    
    subgraph "Parse Phase - Background"
        PARSE["parse_file()<br/>Background task"]
        READ["async_read_chunk_text()<br/>Split into chunks"]
        MD["Generate markdown<br/>content"]
        MINIO_SAVE["Save .md to MinIO tmp"]
        EMBED["Get embedding model<br/>from workbench_conf"]
        INDEX_V["Add to Milvus<br/>col_linsight_file_{model_id}"]
        INDEX_K["Add to Elasticsearch<br/>col_linsight_file_{model_id}"]
        CACHE_COMPLETE["Update Redis<br/>status=completed<br/>+ file paths"]
    end
    
    subgraph "Submit Phase"
        SUBMIT["submit_user_question()"]
        VALIDATE["Validate parsing_status=completed"]
        COPY["Copy .md from tmp<br/>to linsight/{chat_id}/"]
        ADD_SESSION["Add to session files[]"]
    end
    
    UPLOAD --> GEN_ID --> SAVE --> CACHE_UPLOAD
    CACHE_UPLOAD -.Async.- PARSE
    PARSE --> READ --> MD --> MINIO_SAVE
    PARSE --> EMBED --> INDEX_V
    PARSE --> EMBED --> INDEX_K
    PARSE --> CACHE_COMPLETE
    
    SUBMIT --> VALIDATE --> COPY --> ADD_SESSION
```

**File Metadata Schema:**

```typescript
{
  file_id: string;              // 8-char unique ID
  original_filename: string;    // User's filename
  filename: string;             // Stored filename with file_id
  file_path: string;            // Local cache path
  parsing_status: string;       // "running" | "completed" | "failed"
  markdown_filename?: string;   // Generated .md filename
  markdown_file_path?: string;  // MinIO object path
  markdown_file_md5?: string;   // MD5 hash
  embedding_model_id?: number;  // Used embedding model
  collection_name?: string;     // Milvus collection
}
```

Sources: [src/backend/bisheng/api/services/linsight/workbench_impl.py:699-863](), [src/backend/bisheng/api/v1/linsight.py:52-106]()

### Tool Integration

Linsight initializes and manages tools for agent execution:

```mermaid
graph TB
    subgraph "Tool Selection - Frontend"
        USER_SELECT["User selects tools<br/>in UI"]
        TOOL_SCHEMA["LinsightToolSchema<br/>id, name, children[]"]
    end
    
    subgraph "Workbench Configuration"
        WS_CONFIG["WorkStationService.aget_config()"]
        LINSIGHT_CONFIG["linsightConfig.tools[]<br/>Admin-configured tools"]
    end
    
    subgraph "Tool Initialization"
        INIT["init_linsight_config_tools()"]
        EXTRACT["Extract tool IDs<br/>from nested children"]
        FILTER["Filter against<br/>workbench config"]
        SPECIAL["Special handling:<br/>bisheng_code_interpreter"]
        EXEC_INIT["ToolExecutor.init_by_tool_ids()"]
        LINSIGHT_TOOLS["ToolServices.init_linsight_tools()<br/>Built-in tools"]
    end
    
    subgraph "Code Interpreter Special Case"
        CODE_TOOL["Bisheng Code Interpreter"]
        LOCAL_SYNC["Set local_sync_path<br/>= session file_dir"]
        E2B_SYNC["Set e2b.local_sync_path<br/>+ file_list[]"]
        TIMEOUT["Set e2b.timeout = 3600s<br/>keep_sandbox = True"]
    end
    
    USER_SELECT --> TOOL_SCHEMA
    TOOL_SCHEMA --> INIT
    
    WS_CONFIG --> LINSIGHT_CONFIG
    LINSIGHT_CONFIG --> FILTER
    
    INIT --> EXTRACT --> FILTER
    FILTER --> SPECIAL
    FILTER --> EXEC_INIT
    INIT --> LINSIGHT_TOOLS
    
    SPECIAL --> CODE_TOOL
    CODE_TOOL --> LOCAL_SYNC
    CODE_TOOL --> E2B_SYNC
    CODE_TOOL --> TIMEOUT
```

**Built-in Linsight Tools:**

The system automatically adds these tools from `ToolServices.init_linsight_tools()`:
- File manipulation tools (read, write, replace)
- Directory operations
- Text processing utilities

**Tool Configuration Structure:**

```json
{
  "id": 1,
  "name": "Code & Analysis",
  "children": [
    {
      "id": 42,
      "tool_key": "bisheng_code_interpreter",
      "name": "Code Interpreter",
      "desc": "Execute Python code"
    }
  ]
}
```

Sources: [src/backend/bisheng/api/services/linsight/workbench_impl.py:902-963](), [src/backend/bisheng/api/services/linsight/workbench_impl.py:459-474]()

### Interactive User Input

Tasks can request user input during execution through the `NeedUserInput` event:

```mermaid
sequenceDiagram
    participant Agent
    participant TaskExec as LinsightWorkflowTask
    participant StateMgr as LinsightStateMessageManager
    participant Redis
    participant MySQL
    participant WS as WebSocket
    participant User
    
    Agent->>TaskExec: Emit NeedUserInput event
    TaskExec->>StateMgr: add_execution_task_step(event)
    StateMgr->>MySQL: Append to task.history
    
    TaskExec->>StateMgr: update_execution_task_status<br/>(WAITING_FOR_USER_INPUT)
    StateMgr->>MySQL: Update task status
    StateMgr->>Redis: Update cached task
    
    TaskExec->>StateMgr: push_message(USER_INPUT)
    StateMgr->>Redis: RPUSH message
    
    WS->>StateMgr: pop_message()
    StateMgr-->>WS: USER_INPUT event
    WS-->>User: Display input prompt
    
    loop Polling for Input
        TaskExec->>TaskExec: _wait_for_input_completion()
        TaskExec->>StateMgr: get_execution_task(task_id)
        StateMgr->>Redis: Read task
        StateMgr-->>TaskExec: Task with status
        TaskExec->>TaskExec: Check if USER_INPUT_COMPLETED
        alt Not Completed
            TaskExec->>TaskExec: sleep(1)
        end
    end
    
    User->>API: POST /workbench/user-input
    API->>StateMgr: set_user_input(task_id, content, files)
    
    alt Files Provided
        StateMgr->>MinIO: Download files to file_dir
    end
    
    StateMgr->>Redis: Update task.history[-1]<br/>Set user_input, is_completed=True
    StateMgr->>MySQL: Update task.history, status
    
    StateMgr->>StateMgr: push_message(USER_INPUT_COMPLETED)
    
    TaskExec->>TaskExec: Loop detects USER_INPUT_COMPLETED
    TaskExec->>Agent: agent.continue_task(task_id, user_input)
    
    Agent->>Agent: Resume execution with input
```

**User Input Event Schema:**

```python
class UserInputEventSchema(NeedUserInput):
    files: Optional[List[Dict[str, str]]]  # Uploaded files
    user_input: Optional[str]               # Text input
    is_completed: bool                      # Completion flag
```

Sources: [src/backend/bisheng/linsight/task_exec.py:427-512](), [src/backend/bisheng/api/v1/linsight.py:357-390](), [src/backend/bisheng/linsight/state_message_manager.py:262-309]()

## Storage and Persistence

### Database Schema

The Linsight system uses three primary MySQL tables:

**`linsight_session_version` Table:**

| Column | Type | Description |
|--------|------|-------------|
| `id` | CHAR(36) | Primary key, UUID hex |
| `session_id` | CHAR(36) | FK to message_session.chat_id |
| `user_id` | INT | FK to user.user_id |
| `question` | TEXT | User's original question |
| `title` | TEXT | Generated session title |
| `tools` | JSON | Selected tools configuration |
| `personal_knowledge_enabled` | BOOLEAN | Personal KB flag |
| `org_knowledge_enabled` | BOOLEAN | Organization KB flag |
| `files` | JSON | Array of file metadata |
| `sop` | TEXT | Generated SOP content |
| `output_result` | JSON | Execution results |
| `status` | ENUM | Session status |
| `score` | INT | User rating (1-5) |
| `execute_feedback` | TEXT | User feedback |
| `has_reexecute` | BOOLEAN | Re-execution flag |
| `version` | DATETIME | Version timestamp |

**`linsight_execute_task` Table:**

| Column | Type | Description |
|--------|------|-------------|
| `id` | CHAR(36) | Primary key, UUID hex |
| `session_version_id` | CHAR(36) | FK to session version |
| `parent_task_id` | CHAR(36) | FK to parent task (nullable) |
| `previous_task_id` | CHAR(36) | Previous sibling task |
| `next_task_id` | CHAR(36) | Next sibling task |
| `task_type` | ENUM | SINGLE or COMPOSITE |
| `task_data` | JSON | Task definition |
| `history` | JSON | Array of execution steps |
| `status` | ENUM | Task execution status |
| `result` | JSON | Task output |

**`linsight_sop` & `linsight_sop_record` Tables:**

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT | Primary key (auto-increment) |
| `name` | TEXT | SOP name |
| `description` | TEXT | SOP description |
| `user_id` | INT | Creator user ID |
| `content` | LONGTEXT | Full SOP content |
| `rating` | INT | Quality rating (0-5) |
| `vector_store_id` | CHAR(36) | Link to vector store |
| `linsight_version_id` | CHAR(36) | Source session version |
| `showcase` | BOOLEAN | Featured SOP flag (sop only) |
| `execute_feedback` | TEXT | Execution feedback (record only) |

Sources: [src/backend/bisheng/database/models/linsight_session_version.py:34-77](), [src/backend/bisheng/database/models/linsight_execute_task.py:43-84](), [src/backend/bisheng/database/models/linsight_sop.py:15-66]()

### Redis Data Structures

Linsight uses Redis for caching and message streaming:

**Key Patterns:**

| Key Pattern | Type | TTL | Purpose |
|-------------|------|-----|---------|
| `linsight_file:{file_id}` | Hash | 24h | File parsing metadata |
| `linsight:queue` | List | - | Task execution queue |
| `linsight_tasks:{version_id}:session_version_info` | String | 1h | Cached session data |
| `linsight_tasks:{version_id}:messages` | List | 1h | Event message queue |
| `linsight_tasks:{version_id}:execution_tasks:{task_id}` | Hash | 1h | Cached task data |

**Queue Operations:**

```python
# Adding task to queue
await queue.put(session_version_id)  # RPUSH
await queue.get_wait()                # BLPOP (blocking)

# Queue monitoring
await queue.qsize()                   # LLEN
await queue.index(data)               # LRANGE + search
await queue.remove(data)              # LREM
```

Sources: [src/backend/bisheng/linsight/worker.py:19-62](), [src/backend/bisheng/linsight/state_message_manager.py:52-79](), [src/backend/bisheng/api/services/linsight/workbench_impl.py:72-74]()

### Vector Storage

SOP content is indexed in both Milvus and Elasticsearch for hybrid retrieval:

**Indexing Strategy:**

```mermaid
graph LR
    subgraph "SOP Content Processing"
        CONTENT["SOP Content<br/>(up to 50,000 chars)"]
        TRUNCATE["Truncate to 10,000 chars<br/>for Milvus"]
        FULL["Full text for ES"]
    end
    
    subgraph "Vector Store"
        MILVUS["Milvus Collection<br/>col_linsight_sop"]
        EMB["Embedding Model<br/>from workbench_conf"]
        META_V["Metadata:<br/>vector_store_id"]
    end
    
    subgraph "Keyword Store"
        ES["Elasticsearch Index<br/>col_linsight_sop"]
        META_K["Metadata:<br/>vector_store_id"]
    end
    
    CONTENT --> TRUNCATE --> EMB
    EMB --> MILVUS
    TRUNCATE --> META_V
    
    CONTENT --> FULL --> ES
    FULL --> META_K
```

**Search Process:**

```python
# Hybrid search with ensemble retriever
keyword_retriever = KeywordRetriever(
    keyword_store=es_client,
    search_kwargs={"k": 100},
    text_splitter=text_splitter
)

baseline_vector_retriever = BaselineVectorRetriever(
    vector_store=vector_client,
    search_kwargs={"k": 100},
    text_splitter=text_splitter
)

ensemble = EnsembleRetriever(
    retrievers=[keyword_retriever, baseline_vector_retriever],
    weights=[0.3, 0.7]  # 30% keyword, 70% vector
)

results = await ensemble.ainvoke(query, k=3)
```

Sources: [src/backend/bisheng/api/services/linsight/sop_manage.py:323-372](), [src/backend/bisheng/api/services/linsight/sop_manage.py:475-547]()

---

# Page: Workflow Engine

# Workflow Engine

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/backend/bisheng/api/services/assistant.py](src/backend/bisheng/api/services/assistant.py)
- [src/backend/bisheng/api/services/flow.py](src/backend/bisheng/api/services/flow.py)
- [src/backend/bisheng/api/services/workflow.py](src/backend/bisheng/api/services/workflow.py)
- [src/backend/bisheng/api/v1/assistant.py](src/backend/bisheng/api/v1/assistant.py)
- [src/backend/bisheng/api/v1/flows.py](src/backend/bisheng/api/v1/flows.py)
- [src/backend/bisheng/api/v1/schemas.py](src/backend/bisheng/api/v1/schemas.py)
- [src/backend/bisheng/api/v1/skillcenter.py](src/backend/bisheng/api/v1/skillcenter.py)
- [src/backend/bisheng/api/v1/workflow.py](src/backend/bisheng/api/v1/workflow.py)
- [src/backend/bisheng/database/models/assistant.py](src/backend/bisheng/database/models/assistant.py)
- [src/backend/bisheng/database/models/flow.py](src/backend/bisheng/database/models/flow.py)
- [src/backend/bisheng/database/models/flow_version.py](src/backend/bisheng/database/models/flow_version.py)
- [src/backend/bisheng/database/models/template.py](src/backend/bisheng/database/models/template.py)
- [src/backend/bisheng/database/models/user_link.py](src/backend/bisheng/database/models/user_link.py)
- [src/backend/bisheng/workflow/callback/event.py](src/backend/bisheng/workflow/callback/event.py)
- [src/backend/bisheng/workflow/common/node.py](src/backend/bisheng/workflow/common/node.py)
- [src/backend/bisheng/workflow/edges/edges.py](src/backend/bisheng/workflow/edges/edges.py)
- [src/backend/bisheng/workflow/graph/graph_engine.py](src/backend/bisheng/workflow/graph/graph_engine.py)
- [src/backend/bisheng/workflow/graph/graph_state.py](src/backend/bisheng/workflow/graph/graph_state.py)
- [src/backend/bisheng/workflow/graph/workflow.py](src/backend/bisheng/workflow/graph/workflow.py)
- [src/backend/bisheng/workflow/nodes/agent/agent.py](src/backend/bisheng/workflow/nodes/agent/agent.py)
- [src/backend/bisheng/workflow/nodes/base.py](src/backend/bisheng/workflow/nodes/base.py)
- [src/backend/bisheng/workflow/nodes/code/code.py](src/backend/bisheng/workflow/nodes/code/code.py)
- [src/backend/bisheng/workflow/nodes/condition/condition.py](src/backend/bisheng/workflow/nodes/condition/condition.py)
- [src/backend/bisheng/workflow/nodes/input/input.py](src/backend/bisheng/workflow/nodes/input/input.py)
- [src/backend/bisheng/workflow/nodes/llm/llm.py](src/backend/bisheng/workflow/nodes/llm/llm.py)
- [src/backend/bisheng/workflow/nodes/output/output.py](src/backend/bisheng/workflow/nodes/output/output.py)
- [src/backend/bisheng/workflow/nodes/qa_retriever/qa_retriever.py](src/backend/bisheng/workflow/nodes/qa_retriever/qa_retriever.py)
- [src/backend/bisheng/workflow/nodes/rag/rag.py](src/backend/bisheng/workflow/nodes/rag/rag.py)
- [src/backend/bisheng/workflow/nodes/start/start.py](src/backend/bisheng/workflow/nodes/start/start.py)
- [src/backend/bisheng/workflow/nodes/tool/tool.py](src/backend/bisheng/workflow/nodes/tool/tool.py)

</details>



The Workflow Engine is Bisheng's node-based visual programming system that enables complex AI workflows with typed inputs/outputs, conditional branching, and multi-step orchestration. It provides a graph-based execution model where nodes represent processing units (LLM calls, RAG retrieval, code execution, etc.) connected by edges that define data flow and execution order.

**Scope**: This document covers the workflow execution engine, graph state management, and node-based processing. For general skill/flow management (type 1), see [Flow and Skill Management](#3.7). For assistant-based execution (type 5), see [Assistant System](#3.3). For advanced document workflows, see [Linsight AI Workbench](#3.4).

## Architecture Overview

The workflow engine is built on top of LangGraph and provides a graph-based execution framework where nodes execute in a defined order based on edge connections and conditional logic.

```mermaid
graph TB
    subgraph "Workflow Layer"
        Workflow["Workflow<br/>(workflow.py)"]
        GraphEngine["GraphEngine<br/>(graph_engine.py)"]
        GraphState["GraphState<br/>(graph_state.py)"]
    end
    
    subgraph "Node Layer"
        NodeFactory["NodeFactory<br/>(node_manage.py)"]
        BaseNode["BaseNode<br/>(base.py)"]
        StartNode["StartNode"]
        InputNode["InputNode"]
        LLMNode["LLMNode"]
        AgentNode["AgentNode"]
        RAGNode["RagNode"]
        CodeNode["CodeNode"]
        ConditionNode["ConditionNode"]
        OutputNode["OutputNode"]
        ToolNode["ToolNode"]
    end
    
    subgraph "Edge & Routing"
        EdgeManage["EdgeManage<br/>(edges.py)"]
        EdgeBase["EdgeBase"]
    end
    
    subgraph "LangGraph Integration"
        StateGraph["LangGraph StateGraph"]
        MemorySaver["MemorySaver"]
    end
    
    subgraph "Callbacks"
        BaseCallback["BaseCallback"]
        NodeStartData["NodeStartData"]
        NodeEndData["NodeEndData"]
        OutputMsgData["OutputMsgData"]
    end
    
    Workflow --> GraphEngine
    GraphEngine --> GraphState
    GraphEngine --> EdgeManage
    GraphEngine --> NodeFactory
    GraphEngine --> StateGraph
    
    NodeFactory --> BaseNode
    BaseNode --> StartNode
    BaseNode --> InputNode
    BaseNode --> LLMNode
    BaseNode --> AgentNode
    BaseNode --> RAGNode
    BaseNode --> CodeNode
    BaseNode --> ConditionNode
    BaseNode --> OutputNode
    BaseNode --> ToolNode
    
    EdgeManage --> EdgeBase
    
    GraphEngine --> BaseCallback
    BaseCallback --> NodeStartData
    BaseCallback --> NodeEndData
    BaseCallback --> OutputMsgData
```

**Sources**: [src/backend/bisheng/workflow/graph/workflow.py:1-62](), [src/backend/bisheng/workflow/graph/graph_engine.py:1-71](), [src/backend/bisheng/workflow/nodes/base.py:1-67]()

## Core Components

### Workflow Class

The `Workflow` class is the top-level orchestrator that manages workflow execution lifecycle, timeout handling, and user input continuations.

**Key responsibilities**:
- Initialize `GraphEngine` with workflow configuration
- Manage execution state and timeout
- Handle user input for interactive nodes
- Save conversation history

**Main methods**:
- `run(input_data)` - Execute workflow or continue from interruption
- `save_user_input_history(input_data)` - Persist user input to conversation memory

```mermaid
graph LR
    User["User Request"] --> WorkflowRun["Workflow.run()"]
    WorkflowRun --> CheckInput{"input_data<br/>provided?"}
    CheckInput -->|"Yes"| ContinueRun["graph_engine.continue_run()"]
    CheckInput -->|"No"| FirstRun["graph_engine.run()"]
    ContinueRun --> SaveHistory["save_user_input_history()"]
    FirstRun --> UpdateTime["Update current_time"]
    SaveHistory --> Result["Return status, reason"]
    UpdateTime --> Result
```

**Sources**: [src/backend/bisheng/workflow/graph/workflow.py:10-62]()

### GraphEngine

The `GraphEngine` is the core execution engine that builds and executes the node graph using LangGraph's `StateGraph`.

**Key responsibilities**:
- Parse workflow data into nodes and edges
- Build LangGraph state graph with proper routing
- Handle node fan-in/fan-out scenarios
- Manage node execution order based on hierarchy
- Support both sync and async execution modes

**Initialization flow**:
1. `build_edges()` - Parse edges into `EdgeManage`
2. `build_nodes()` - Instantiate all nodes via `NodeFactory`
3. Calculate node hierarchy levels for execution ordering
4. Add nodes and edges to LangGraph `StateGraph`
5. Handle complex routing (conditional edges, fan-in nodes)

```mermaid
graph TB
    Init["GraphEngine.__init__()"] --> BuildEdges["build_edges()"]
    BuildEdges --> BuildNodes["build_nodes()"]
    BuildNodes --> InitNodes["init_nodes()"]
    InitNodes --> BuildLevel["build_node_level()"]
    BuildLevel --> AddNodeEdge["add_node_edge()"]
    AddNodeEdge --> BuildFanIn["build_more_fan_in_node()"]
    BuildFanIn --> CompileGraph["graph_builder.compile()"]
    
    InitNodes --> StartNode["Find start node"]
    InitNodes --> EndNodes["Find end nodes"]
    InitNodes --> InterruptNodes["Find interrupt nodes"]
    
    AddNodeEdge --> CheckType{"Node type?"}
    CheckType -->|"OUTPUT"| AddFake["Add fake node"]
    CheckType -->|"CONDITION"| AddConditional["Add conditional edge"]
    CheckType -->|"Other"| AddNormal["Add normal edge"]
```

**Sources**: [src/backend/bisheng/workflow/graph/graph_engine.py:27-71](), [src/backend/bisheng/workflow/graph/graph_engine.py:72-131]()

### GraphState

The `GraphState` manages global state across all nodes during workflow execution, including variable storage and conversation history.

**Data structures**:
- `history_memory` - `ConversationBufferWindowMemory` for chat context
- `variables_pool` - `Dict[node_id, Dict[key, value]]` for node outputs

**Key methods**:

| Method | Purpose | Example |
|--------|---------|---------|
| `set_variable(node_id, key, value)` | Store node output | `set_variable("llm_1", "output", "response")` |
| `get_variable(node_id, key)` | Retrieve node output | `get_variable("input_1", "user_input")` |
| `get_variable_by_str(contact_key)` | Parse and retrieve | `get_variable_by_str("input_1.user_input#0")` |
| `save_context(content, msg_sender)` | Store chat message | `save_context("Hello", "human")` |
| `get_history_memory(count)` | Get chat history | `get_history_memory(5)` |
| `get_all_variables()` | Get all stored data | Returns `{"node_id.key": value}` dict |

**Variable reference syntax**:
- Simple: `node_id.key` - Get node's output variable
- Array index: `node_id.key#0` - Get first element of array
- Dict key: `node_id.key#field` - Get dict field value
- Special: `node_id.chat_history` - Get conversation history

**Sources**: [src/backend/bisheng/workflow/graph/graph_state.py:1-109]()

## Node Types

Nodes are the fundamental building blocks of workflows. Each node type implements specific functionality and can reference variables from other nodes.

| Node Type | Description | Input Example | Output Example | File |
|-----------|-------------|---------------|----------------|------|
| `start` | Workflow entry point, initializes context | - | `current_time`, user info | [nodes/start/start.py]() |
| `input` | User input collection (dialog or form) | - | `user_input`, uploaded files | [nodes/input/input.py]() |
| `llm` | LLM completion with prompt templates | `system_prompt`, `user_prompt` | `output` | [nodes/llm/llm.py]() |
| `agent` | ReAct/function-call agent with tools | `system_prompt`, `user_prompt`, tools | `output` | [nodes/agent/agent.py]() |
| `rag` | RAG retrieval + LLM answer | `user_question`, knowledge sources | Retrieved docs + answer | [nodes/rag/rag.py]() |
| `qa_retriever` | QA knowledge retrieval | `user_question` | `retrieved_result` | [nodes/qa_retriever/qa_retriever.py]() |
| `code` | Python code execution | `code_input` variables | `code_output` variables | [nodes/code/code.py]() |
| `tool` | External tool invocation | Tool-specific params | `output` | [nodes/tool/tool.py]() |
| `condition` | Conditional branching | Variables to evaluate | Routes to next node | [nodes/condition/condition.py]() |
| `output` | User-facing output (message/choice/input) | `message`, files | Interaction result | [nodes/output/output.py]() |
| `end` | Workflow termination | - | - | - |

**Sources**: [src/backend/bisheng/workflow/common/node.py:8-26](), [src/backend/bisheng/workflow/nodes/base.py:20-67]()

### BaseNode Interface

All nodes inherit from `BaseNode` and implement:

**Required methods**:
- `_run(unique_id)` - Execute node logic, return dict of outputs
- `parse_log(unique_id, result)` - Format execution log for display

**Optional methods**:
- `get_input_schema()` - Return form schema for user input (INPUT/OUTPUT nodes)
- `handle_input(user_input)` - Process user input for interactive nodes
- `is_condition_node()` - Return True for CONDITION/OUTPUT nodes
- `route_node(state)` - Determine next node(s) for conditional routing

**Common utilities**:
- `get_other_node_variable(variable_key)` - Retrieve other node's output
- `parse_msg_with_variables(msg)` - Replace `{node_id.key}` in strings
- `contact_file_into_prompt(human_message, image_prompt)` - Add files to LLM input

**Sources**: [src/backend/bisheng/workflow/nodes/base.py:20-159]()

## Execution Flow

### Workflow Execution Sequence

```mermaid
sequenceDiagram
    participant User
    participant API as workflow.py API
    participant WF as Workflow
    participant GE as GraphEngine
    participant Node as Node Instance
    participant GS as GraphState
    participant CB as BaseCallback
    
    User->>API: POST /workflow/chat (WebSocket)
    API->>WF: Workflow.__init__(workflow_data)
    WF->>GE: GraphEngine.__init__()
    GE->>GE: build_edges()
    GE->>GE: build_nodes()
    GE->>GE: Calculate node hierarchy
    GE->>GE: Build LangGraph StateGraph
    
    API->>WF: run(input_data=None)
    WF->>GE: graph_engine.run()
    GE->>Node: start_node.run()
    Node->>GS: set_variable("start", "current_time", value)
    Node->>CB: on_node_start(NodeStartData)
    Node->>Node: _run(unique_id)
    Node->>CB: on_node_end(NodeEndData)
    
    GE->>Node: input_node.run()
    Node->>CB: on_user_input(UserInputData)
    Node-->>User: Request user input
    
    User->>API: Send input via WebSocket
    API->>WF: run(input_data={"user_input": "..."})
    WF->>GE: continue_run(input_data)
    GE->>Node: input_node.handle_input()
    Node->>GS: set_variable("input_1", "user_input", value)
    
    GE->>Node: llm_node.run()
    Node->>GS: get_variable("input_1", "user_input")
    Node->>Node: _run(unique_id) - Call LLM
    Node->>GS: set_variable("llm_1", "output", response)
    Node->>CB: on_stream_msg() / on_stream_over()
    
    GE->>Node: output_node.run()
    Node->>GS: get_variable("llm_1", "output")
    Node->>CB: on_output_msg(OutputMsgData)
    Node-->>User: Send final message
    
    GE-->>WF: Return (status, reason)
    WF-->>API: Return execution result
```

**Sources**: [src/backend/bisheng/workflow/graph/workflow.py:50-62](), [src/backend/bisheng/workflow/graph/graph_engine.py:219-313]()

### Node Execution Lifecycle

Each node follows this execution pattern:

1. **Pre-execution**:
   - `on_node_start()` callback fired
   - Retrieve referenced variables from `GraphState`
   - Parse prompt templates with variable substitution

2. **Execution**:
   - `_run(unique_id)` performs core logic
   - Stream callbacks for real-time updates (LLM/Agent nodes)
   - Store results in `GraphState`

3. **Post-execution**:
   - `parse_log()` formats execution details
   - `on_node_end()` callback with log data
   - Determine next node(s) based on edges/conditions

4. **Routing**:
   - Normal nodes: Follow outgoing edges
   - Condition nodes: Evaluate conditions, call `route_node()`
   - Output nodes (choice): Wait for user selection, then route

**Sources**: [src/backend/bisheng/workflow/graph/graph_engine.py:219-272]()

### Fan-In Node Handling

The GraphEngine implements special logic for nodes with multiple incoming edges (fan-in):

```mermaid
graph TB
    NodeA["Node A"] --> FanIn["Fan-in Node"]
    NodeB["Node B"] --> FanIn
    NodeC["Node C"] --> FanIn
    
    CheckLevel{"All source<br/>levels <=<br/>target level?"}
    
    FanIn --> CheckLevel
    CheckLevel -->|"Yes"| Wait["Wait for all sources"]
    CheckLevel -->|"No"| NoWait["Don't wait - mutual exclusion"]
    
    Wait --> CheckBranches{"Mutually<br/>exclusive<br/>branches?"}
    CheckBranches -->|"Yes"| NoWait
    CheckBranches -->|"No"| WaitAll["Add edge from all sources"]
```

The algorithm in `parse_fan_in_node()`:
1. Check if all source nodes have level ≤ target node level
2. If no, sources are downstream - no waiting needed
3. If yes, check for mutually exclusive branches (from CONDITION/OUTPUT nodes)
4. If mutually exclusive, no waiting needed
5. Otherwise, wait for all fan-in sources

**Sources**: [src/backend/bisheng/workflow/graph/graph_engine.py:119-177]()

## State Management Details

### Variable Storage and Retrieval

The `GraphState` stores all intermediate results using a nested dictionary structure:

```
variables_pool = {
    "input_1": {
        "user_input": "What is AI?",
        "dialog_files": []
    },
    "llm_1": {
        "output": "AI is artificial intelligence..."
    },
    "rag_1": {
        "retrieved_result": [Document(...)],
        "output": "Based on the context..."
    }
}
```

**Variable reference patterns**:

| Pattern | Example | Resolves To |
|---------|---------|-------------|
| Simple | `input_1.user_input` | `"What is AI?"` |
| Array index | `rag_1.retrieved_result#0` | First document |
| Dict key | `start.custom_variables#user_name` | Custom variable value |
| Special | `start.chat_history` | Formatted conversation history |

**Sources**: [src/backend/bisheng/workflow/graph/graph_state.py:43-109]()

### Conversation Memory

Chat history is managed through LangChain's `ConversationBufferWindowMemory`:

- Initialized in `StartNode` with configurable window size (default 10)
- Messages added via `save_context(content, msg_sender)`
- Retrieved as string via `get_history_memory(count)` or as message list via `get_history_list(count)`
- Used by LLM/Agent nodes to maintain conversation context

**Sources**: [src/backend/bisheng/workflow/graph/graph_state.py:17-42](), [src/backend/bisheng/workflow/nodes/start/start.py:25-26]()

## Key Node Implementations

### Input Node

The Input Node handles user input in two modes: dialog input and form input.

**Dialog mode** (`tab='dialog_input'`):
- Collects `user_input` text
- Handles file uploads (parse mode: keep_raw, extract_text, ingest_to_temp_kb)
- Stores files in temporary Milvus/ES collections for retrieval
- Outputs: `user_input`, `dialog_files_content`, `dialog_file_paths`, `dialog_image_files`

**Form mode** (`tab='form_input'`):
- Defines custom form fields with types (text, number, file, etc.)
- Each field becomes a separate output variable
- Supports file upload with same parsing modes as dialog

**File processing modes**:
1. `KEEP_RAW` - Store file paths only
2. `EXTRACT_TEXT` - Extract text content into variable
3. `INGEST_TO_KNOWLEDGE_BASE` - Chunk, embed, store in vector DB for later retrieval

**Sources**: [src/backend/bisheng/workflow/nodes/input/input.py:33-347]()

### LLM Node

Executes LLM completions with configurable prompts and supports batch processing.

**Configuration**:
- `model_id` - LLM model selection from configured models
- `temperature` - Model temperature parameter
- `system_prompt` - System message template
- `user_prompt` - User message template
- `tab` - Single or batch mode
- `output_user` - Whether to stream to user

**Batch mode**:
- `batch_variable` - List of variables to iterate over
- `output` - List of output keys, one per batch item
- Each batch item gets separate system/user prompts with variable substitution

**Execution**:
1. Parse prompt templates, substitute variables
2. Invoke LLM via `LLMService.get_bisheng_llm_sync()`
3. Stream tokens if `output_user=True`
4. Return completion(s) in dict

**Sources**: [src/backend/bisheng/workflow/nodes/llm/llm.py:14-135]()

### Agent Node

Implements ReAct or function-calling agents with tools, knowledge, and SQL capabilities.

**Configuration**:
- `system_prompt`, `user_prompt` - Agent prompts
- `model_id` - LLM for agent reasoning
- `tool_list` - Selected tools from tool management
- `knowledge_id` - Knowledge bases or temporary files for retrieval
- `sql_agent` - Optional NL2SQL configuration
- `chat_history_flag` - Whether to include conversation history

**Agent types**:
- **ReAct** - Uses `ConfigurableAssistant` with tool reasoning
- **Function Call** - Uses `create_react_agent` with native function calling

**Tool initialization**:
1. Load configured tools via `ToolExecutor.init_by_tool_ids_sync()`
2. Initialize knowledge retrieval tools for each knowledge base
3. Initialize SQL agent tool if configured
4. Combine all tools for agent

**Execution**:
1. Build agent with tools and system prompt
2. Format user prompt with variables
3. Invoke agent with chat history
4. Track tool invocations via callback
5. Return agent output and reasoning content

**Sources**: [src/backend/bisheng/workflow/nodes/agent/agent.py:50-405]()

### RAG Node

Performs retrieval-augmented generation by combining knowledge retrieval with LLM synthesis.

**Configuration**:
- `user_question` - Question(s) to retrieve for
- `knowledge_id` - Knowledge sources (type: knowledge | file_metadata)
- `rerank_model` - Optional reranking model
- `retrieval_mode` - Vector, keyword, or hybrid search
- `model_id` - LLM for answer generation
- `system_prompt`, `user_prompt` - QA prompts

**Execution flow**:
1. Initialize multi-retriever (Milvus + Elasticsearch)
2. Retrieve relevant documents for question
3. Optional reranking to improve relevance
4. Format QA prompt with retrieved context
5. Invoke LLM to generate answer
6. Return answer and source documents

**Prompt variables**:
- `{question}` - User question
- `{context}` - Retrieved document content
- Custom variables from other nodes

**Sources**: [src/backend/bisheng/workflow/nodes/rag/rag.py:22-197]()

### Condition Node

Routes execution based on conditional logic evaluation.

**Configuration**:
- `condition` - List of condition cases with:
  - `id` - Condition identifier for routing
  - `conditions` - List of comparison expressions
  - `logical_operator` - AND/OR for multiple conditions

**Condition evaluation**:
1. Iterate through condition cases in order
2. Evaluate each case's conditions against variables
3. First matching case determines next node(s)
4. Fall back to default route if no match

**Supported operators**:
- Comparison: `==`, `!=`, `>`, `<`, `>=`, `<=`
- String: `contains`, `not contains`, `is empty`, `is not empty`
- Logical: `AND`, `OR`

**Sources**: [src/backend/bisheng/workflow/nodes/condition/condition.py:8-48]()

### Output Node

Sends messages to users with optional interaction (input/choice).

**Output types**:
- `message` - Simple text output
- `input` - Output with inline text input request
- `choose` - Output with option selection

**Configuration**:
- `output_msg` - Message template with variable substitution
- `output_files` - File attachments (converted to share links)
- `output_result` - User input schema or choice options
- `output_type` - Message, input, or choose

**Execution**:
1. Parse output message template
2. Substitute variables from graph state
3. Get file share links from MinIO
4. Send via callback (`on_output_msg`, `on_output_input`, `on_output_choose`)
5. For interactive types, workflow pauses until user responds

**Sources**: [src/backend/bisheng/workflow/nodes/output/output.py:10-137]()

## Service Layer Integration

### WorkFlowService

The `WorkFlowService` provides business logic for workflow management and execution.

**Key methods**:

| Method | Purpose | HTTP Endpoint |
|--------|---------|---------------|
| `get_all_flows()` | List workflows with filters | GET `/workflow/list` |
| `run_once()` | Execute single node for testing | POST `/workflow/run_once` |
| `update_flow_status()` | Online/offline workflow | PATCH `/workflow/status` |
| `get_one_workflow_simple_info()` | Get workflow metadata | - |

**Workflow status management**:
- `OFFLINE (1)` - Draft mode, can be edited
- `ONLINE (2)` - Published, requires initialization check

When changing to ONLINE:
1. Validate workflow structure via `Workflow.__init__()`
2. Check all nodes can be instantiated
3. If valid, update status and current version
4. If invalid, raise `WorkFlowInitError`

**Sources**: [src/backend/bisheng/api/services/workflow.py:35-451]()

### API Endpoints

```mermaid
graph LR
    subgraph "Workflow API Routes"
        Create["POST /workflow/create"]
        Update["PATCH /workflow/update/{flow_id}"]
        Status["PATCH /workflow/status"]
        GetOne["GET /workflow/get_one_flow/{flow_id}"]
        RunOnce["POST /workflow/run_once"]
        Chat["WS /workflow/chat/{workflow_id}"]
    end
    
    subgraph "Version Management"
        GetVersions["GET /workflow/versions"]
        CreateVersion["POST /workflow/versions"]
        UpdateVersion["PUT /workflow/versions/{version_id}"]
        DeleteVersion["DELETE /workflow/versions/{version_id}"]
        ChangeVersion["POST /workflow/change_version"]
    end
    
    subgraph "Report Template"
        GetReport["GET /workflow/report/file"]
        CopyReport["POST /workflow/report/copy"]
        CallbackReport["POST /workflow/report/callback"]
    end
```

**WebSocket chat flow** (`/workflow/chat/{workflow_id}`):
1. Client connects with workflow_id and optional chat_id
2. Server dispatches to `ChatManager.dispatch_client()`
3. `ChatClient` initializes `Workflow` instance
4. User messages trigger `workflow.run(input_data)`
5. Callbacks stream events back to client (node start/end, outputs, errors)
6. Workflow execution continues until completion or user input needed

**Sources**: [src/backend/bisheng/api/v1/workflow.py:1-312]()

## Callback System

The workflow engine uses callbacks to provide real-time execution feedback via WebSocket.

**Event types**:

| Event | Data Class | When Fired | Purpose |
|-------|-----------|------------|---------|
| `node_start` | `NodeStartData` | Node begins execution | Show node in "running" state |
| `node_end` | `NodeEndData` | Node completes | Show results/logs, mark complete |
| `user_input` | `UserInputData` | INPUT/OUTPUT needs input | Display input form to user |
| `guide_word` | `GuideWordData` | START node greeting | Show welcome message |
| `guide_question` | `GuideQuestionData` | Recommended questions | Show quick reply options |
| `output_msg` | `OutputMsgData` | OUTPUT node message | Display final message |
| `output_input` | `OutputMsgInputData` | OUTPUT with input | Display message + input field |
| `output_choose` | `OutputMsgChooseData` | OUTPUT with choice | Display message + options |
| `stream_msg` | `StreamMsgData` | LLM/Agent streaming | Stream token-by-token |
| `stream_over` | `StreamMsgOverData` | LLM/Agent complete | End stream, show sources |

**Callback flow**:
```
BaseNode.run()
  -> callback_manager.on_node_start(NodeStartData)
  -> node._run(unique_id)
     -> (LLM nodes) callback_manager.on_stream_msg(StreamMsgData)
     -> (LLM nodes) callback_manager.on_stream_over(StreamMsgOverData)
     -> (Output nodes) callback_manager.on_output_msg(OutputMsgData)
  -> callback_manager.on_node_end(NodeEndData)
```

**Sources**: [src/backend/bisheng/workflow/callback/event.py:1-72](), [src/backend/bisheng/workflow/graph/graph_engine.py:219-272]()

## Integration with Other Systems

### LLM Service Integration

Nodes that use LLMs (LLM, Agent, RAG) obtain model instances via `LLMService`:

```python
llm = LLMService.get_bisheng_llm_sync(
    model_id=node_params['model_id'],
    temperature=node_params.get('temperature', 0.3),
    app_id=workflow_id,
    app_name=workflow_name,
    app_type=ApplicationTypeEnum.WORKFLOW,
    user_id=user_id
)
```

This integrates with the LLM management system to:
- Validate model availability
- Track usage for telemetry
- Apply user-specific configurations
- Support various providers (OpenAI, Azure, xinference, etc.)

**Sources**: [src/backend/bisheng/workflow/nodes/llm/llm.py:39-44](), [src/backend/bisheng/workflow/nodes/agent/agent.py:75-80]()

### Knowledge Base Integration

RAG and Agent nodes retrieve from knowledge bases via:

1. **Knowledge-based retrieval** - From persisted knowledge bases:
   - `ToolExecutor.init_knowledge_tool_sync()` creates retrieval tool
   - Uses Milvus for vector search + Elasticsearch for keyword
   - Applies user permissions via `MilvusWithPermissionCheck`

2. **File-based retrieval** - From INPUT node uploaded files:
   - Files ingested to temporary Milvus/ES collections
   - Collection name includes embedding model ID
   - Filtered by `document_id` from file metadata

**Sources**: [src/backend/bisheng/workflow/nodes/agent/agent.py:160-204](), [src/backend/bisheng/workflow/common/knowledge.py]()

### Tool System Integration

Agent and Tool nodes execute external tools via `ToolExecutor`:

```python
tools = ToolExecutor.init_by_tool_ids_sync(
    tool_ids=[1, 2, 3],
    app_id=workflow_id,
    app_name=workflow_name,
    app_type=ApplicationTypeEnum.WORKFLOW,
    user_id=user_id
)
```

This supports:
- API tools (HTTP requests with auth)
- Knowledge retrieval tools
- SQL query tools (NL2SQL)
- Custom tool implementations

**Sources**: [src/backend/bisheng/workflow/nodes/agent/agent.py:140-147](), [src/backend/bisheng/workflow/nodes/tool/tool.py:10-58]()

### Session and Version Management

Workflows integrate with:

1. **Flow versions** - Multiple versions per workflow:
   - Current version used for execution
   - Version data stored in `FlowVersion` table
   - Status change requires validation of current version

2. **Chat sessions** - Persistent conversation tracking:
   - Session ID maps to conversation history
   - Stored in `MessageSession` table
   - Linked to user and workflow

3. **Audit logging** - All workflow operations logged:
   - Create, update, delete, status change
   - Tracks user, timestamp, affected resources

**Sources**: [src/backend/bisheng/api/services/workflow.py:181-212](), [src/backend/bisheng/database/models/flow_version.py:1-50]()

---

# Page: Dashboard and Analytics

# Dashboard and Analytics

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/frontend/platform/public/assets/dashboard/setting.svg](src/frontend/platform/public/assets/dashboard/setting.svg)
- [src/frontend/platform/public/locales/en-US/dashboard.json](src/frontend/platform/public/locales/en-US/dashboard.json)
- [src/frontend/platform/public/locales/ja/dashboard.json](src/frontend/platform/public/locales/ja/dashboard.json)
- [src/frontend/platform/public/locales/zh-Hans/dashboard.json](src/frontend/platform/public/locales/zh-Hans/dashboard.json)
- [src/frontend/platform/src/pages/Dashboard/components/config/ChartSelector.tsx](src/frontend/platform/src/pages/Dashboard/components/config/ChartSelector.tsx)
- [src/frontend/platform/src/pages/Dashboard/components/config/ComponentConfigDrawer.tsx](src/frontend/platform/src/pages/Dashboard/components/config/ComponentConfigDrawer.tsx)
- [src/frontend/platform/src/pages/Dashboard/components/config/DashboardConfigPanel.tsx](src/frontend/platform/src/pages/Dashboard/components/config/DashboardConfigPanel.tsx)
- [src/frontend/platform/src/pages/Dashboard/components/config/DatasetSelector.tsx](src/frontend/platform/src/pages/Dashboard/components/config/DatasetSelector.tsx)
- [src/frontend/platform/src/pages/Dashboard/components/config/DimensionBlock.tsx](src/frontend/platform/src/pages/Dashboard/components/config/DimensionBlock.tsx)
- [src/frontend/platform/src/pages/Dashboard/components/config/FilterConditionDialog.tsx](src/frontend/platform/src/pages/Dashboard/components/config/FilterConditionDialog.tsx)
- [src/frontend/platform/src/pages/Dashboard/components/config/StyleConfigPanel.tsx](src/frontend/platform/src/pages/Dashboard/components/config/StyleConfigPanel.tsx)
- [src/frontend/platform/src/pages/Dashboard/components/config/useChartState.tsx](src/frontend/platform/src/pages/Dashboard/components/config/useChartState.tsx)

</details>



## Purpose and Scope

The Dashboard and Analytics system provides business intelligence capabilities for visualizing and analyzing data within Bisheng. It enables users to create interactive dashboards with multiple chart types, configure data queries with dimensions and metrics, apply filters, and customize visual styling. This system is primarily a frontend feature that integrates with backend dataset APIs to provide a complete data visualization solution.

For information about other analytics features such as audit logging, see [User and Access Control](#4).

---

## System Architecture

The dashboard system follows a component-based architecture with three main layers: dataset management, chart configuration, and rendering.

```mermaid
graph TB
    subgraph "User Interface Layer"
        Editor["Dashboard Editor<br/>DashboardPage"]
        ConfigDrawer["ComponentConfigDrawer<br/>Configuration Panel"]
        StylePanel["StyleConfigPanel<br/>Style Customization"]
        FilterDialog["FilterConditionDialog<br/>Filter Configuration"]
    end
    
    subgraph "State Management"
        EditorStore["useEditorDashboardStore<br/>Dashboard State"]
        ComponentStore["useComponentEditorStore<br/>Component State"]
        ChartState["useChartState<br/>Chart Configuration Hook"]
    end
    
    subgraph "Data Configuration"
        DatasetSelector["DatasetSelector<br/>Dataset Selection"]
        DimensionBlock["DimensionBlock<br/>Dimension/Metric Management"]
        ChartSelector["ChartSelector<br/>Query Component Config"]
    end
    
    subgraph "Backend APIs"
        DatasetAPI["GET /api/v1/datasets<br/>Dataset Metadata"]
        EnumAPI["GET /api/v1/field_enums<br/>Enum Values"]
        DashboardAPI["Dashboard CRUD APIs<br/>Save/Load Dashboards"]
    end
    
    Editor --> ConfigDrawer
    ConfigDrawer --> DatasetSelector
    ConfigDrawer --> DimensionBlock
    ConfigDrawer --> FilterDialog
    ConfigDrawer --> StylePanel
    ConfigDrawer --> ChartSelector
    
    ConfigDrawer --> ChartState
    ChartState --> ComponentStore
    Editor --> EditorStore
    
    DatasetSelector --> DatasetAPI
    FilterDialog --> EnumAPI
    EditorStore --> DashboardAPI
    
    style ChartState fill:#e1f5ff
    style EditorStore fill:#fff4e1
    style DatasetAPI fill:#ffe1f5
```

**Sources:** 
- [src/frontend/platform/src/pages/Dashboard/components/config/ComponentConfigDrawer.tsx:1-100]()
- [src/frontend/platform/src/pages/Dashboard/components/config/useChartState.tsx:1-50]()
- [src/frontend/platform/src/pages/Dashboard/components/config/DatasetSelector.tsx:1-30]()

### Core Components

| Component | File | Purpose |
|-----------|------|---------|
| `ComponentConfigDrawer` | `ComponentConfigDrawer.tsx` | Main configuration interface for charts |
| `StyleConfigPanel` | `StyleConfigPanel.tsx` | Visual style customization |
| `DatasetSelector` | `DatasetSelector.tsx` | Dataset and field selection |
| `DimensionBlock` | `DimensionBlock.tsx` | Dimension/metric drag-drop area |
| `FilterConditionDialog` | `FilterConditionDialog.tsx` | Filter configuration dialog |
| `ChartSelector` | `ChartSelector.tsx` | Query component linking |
| `DashboardConfigPanel` | `DashboardConfigPanel.tsx` | Dashboard-level settings |
| `useChartState` | `useChartState.tsx` | Chart state management hook |

**Sources:** 
- [src/frontend/platform/src/pages/Dashboard/components/config/ComponentConfigDrawer.tsx:91-100]()

---

## Dataset Management

### Dataset Structure

Datasets are the foundation of the dashboard system, providing structured data with dimensions and metrics.

```mermaid
graph LR
    Dataset["Dataset<br/>dataset_code, dataset_name"]
    Schema["schema_config"]
    Dimensions["Dimensions<br/>Category Fields"]
    Metrics["Metrics<br/>Value Fields"]
    
    Dataset --> Schema
    Schema --> Dimensions
    Schema --> Metrics
    
    Dimensions --> TimeDim["Time Dimensions<br/>timestamp.year<br/>timestamp.month<br/>timestamp.day"]
    Dimensions --> RegularDim["Regular Dimensions<br/>user_group_name<br/>app_type<br/>model_type"]
    
    Metrics --> Regular["Regular Metrics<br/>total_user_count<br/>session_count<br/>total_token"]
    Metrics --> Virtual["Virtual Metrics<br/>is_virtual=true<br/>Calculated Fields"]
```

**Sources:** 
- [src/frontend/platform/src/pages/Dashboard/components/config/DatasetSelector.tsx:108-130]()
- [src/frontend/platform/public/locales/zh-Hans/dashboard.json:391-466]()

### DatasetField Type Definition

The `DatasetField` interface represents individual fields within a dataset:

```typescript
interface DatasetField {
    fieldCode: string          // SQL field name (e.g., "timestamp", "total_user_count")
    displayName: string        // UI display name (localized)
    fieldType: "string" | "number" | "date"
    role: "dimension" | "metric"
    enumValues?: string[]      // For enum filtering
    isVirtual?: boolean        // Calculated metrics
    timeGranularity?: string   // For time dimensions: "year", "month", "day", "hour"
}
```

**Sources:** 
- [src/frontend/platform/src/pages/Dashboard/components/config/DatasetSelector.tsx:12-20]()

### Dataset Selector Component

The `DatasetSelector` component handles dataset selection and field exploration:

```mermaid
sequenceDiagram
    participant User
    participant DatasetSelector
    participant API as getDatasets()
    participant FieldList
    participant Drag as Drag Handler
    
    User->>DatasetSelector: Select dataset
    DatasetSelector->>API: Fetch all datasets
    API-->>DatasetSelector: Return dataset list
    DatasetSelector->>FieldList: Display dimensions & metrics
    
    User->>FieldList: Drag field
    FieldList->>Drag: onDragStart(field)
    Drag->>Drag: Set effectAllowed='copy'
    Drag->>Drag: JSON.stringify(dragData)
    User->>Drag: Drop on target
```

**Sources:** 
- [src/frontend/platform/src/pages/Dashboard/components/config/DatasetSelector.tsx:56-102]()
- [src/frontend/platform/src/pages/Dashboard/components/config/DatasetSelector.tsx:143-185]()

### Time Dimension Handling

Time dimensions support multiple granularities:

| Granularity | Icon | Display Key | Example |
|-------------|------|-------------|---------|
| Year | Clock3 | `timestamp.year` | `timestamp: {year: "2024"}` |
| Quarter | Clock3 | `timestamp.quarter` | `timestamp: {quarter: "2024-Q1"}` |
| Month | Clock3 | `timestamp.month` | `timestamp: {month: "2024-01"}` |
| Week | Clock3 | `timestamp.week` | `timestamp: {week: "2024-W01"}` |
| Day | Clock3 | `timestamp.day` | `timestamp: {day: "2024-01-15"}` |
| Hour | Clock3 | `timestamp.hour` | `timestamp: {hour: "2024-01-15-14"}` |

**Sources:** 
- [src/frontend/platform/src/pages/Dashboard/components/config/DatasetSelector.tsx:30-37]()
- [src/frontend/platform/src/pages/Dashboard/components/config/DatasetSelector.tsx:206-232]()

---

## Chart Configuration System

### Configuration Workflow

```mermaid
graph TB
    Start["User Opens Config"]
    SelectType["Select Chart Type<br/>ComponentPicker"]
    SelectDataset["Select Dataset<br/>DatasetSelector"]
    
    ConfigDims["Configure Dimensions<br/>Category Axis"]
    ConfigStack["Configure Stack<br/>(Optional)"]
    ConfigMetrics["Configure Metrics<br/>Value Axis"]
    
    ApplyFilters["Apply Filters<br/>FilterConditionDialog"]
    SetTimeRange["Set Time Range<br/>AdvancedDatePicker"]
    SetLimit["Set Result Limit<br/>limitType, limitValue"]
    
    StyleConfig["Style Configuration<br/>StyleConfigPanel"]
    
    Validate["Validate Configuration<br/>validateChartConfig()"]
    Update["Update Chart<br/>handleUpdateChart()"]
    Refresh["Refresh Rendering<br/>refreshChart()"]
    
    Start --> SelectType
    SelectType --> SelectDataset
    SelectDataset --> ConfigDims
    ConfigDims --> ConfigStack
    ConfigStack --> ConfigMetrics
    ConfigMetrics --> ApplyFilters
    ApplyFilters --> SetTimeRange
    SetTimeRange --> SetLimit
    SetLimit --> StyleConfig
    StyleConfig --> Validate
    Validate --> Update
    Update --> Refresh
```

**Sources:** 
- [src/frontend/platform/src/pages/Dashboard/components/config/ComponentConfigDrawer.tsx:489-607]()
- [src/frontend/platform/src/pages/Dashboard/components/config/useChartState.tsx:42-193]()

### Chart Types

The system supports multiple chart types organized in groups:

```typescript
enum ChartType {
    // Bar Charts
    Bar = 'bar',
    StackedBar = 'stacked-bar',
    GroupedBar = 'grouped-bar',
    
    // Horizontal Bar Charts
    HorizontalBar = 'horizontal-bar',
    StackedHorizontalBar = 'stacked-horizontal-bar',
    GroupedHorizontalBar = 'grouped-horizontal-bar',
    
    // Line Charts
    Line = 'line',
    StackedLine = 'stacked-line',
    MultipleLine = 'multiple-line',
    
    // Area Charts
    Area = 'area',
    StackedArea = 'stacked-area',
    
    // Pie Charts
    Pie = 'pie',
    Donut = 'donut',
    
    // Special
    Metric = 'metric',  // Single metric card
    Query = 'query'     // Query component
}
```

**Sources:** 
- [src/frontend/platform/public/locales/en-US/dashboard.json:393-412]()
- [src/frontend/platform/src/pages/Dashboard/components/config/ComponentConfigDrawer.tsx:152-159]()

### Dimension and Metric Configuration

#### Three Configuration Sections

1. **Category Dimensions** (类别轴): X-axis, max 2 dimensions
2. **Stack Dimensions** (堆叠项): For stacked charts, max 1 dimension
3. **Value Dimensions** (指标): Y-axis metrics

```mermaid
graph LR
    subgraph "Dimension Configuration"
        Cat1["Category Dimension 1<br/>e.g., timestamp.day"]
        Cat2["Category Dimension 2<br/>e.g., user_group_name"]
        Stack["Stack Dimension<br/>e.g., app_type"]
    end
    
    subgraph "Metric Configuration"
        Metric1["Metric 1<br/>total_user_count<br/>aggregation: sum"]
        Metric2["Metric 2<br/>session_count<br/>aggregation: avg"]
        Metric3["Metric 3<br/>(Stacked charts only)"]
    end
    
    Cat1 --> XAxis["X-Axis"]
    Cat2 --> XAxis
    Stack --> Series["Series/Legend"]
    
    Metric1 --> YAxis["Y-Axis"]
    Metric2 --> YAxis
    Metric3 --> YAxis
```

**Sources:** 
- [src/frontend/platform/src/pages/Dashboard/components/config/ComponentConfigDrawer.tsx:924-974]()
- [src/frontend/platform/src/pages/Dashboard/components/config/useChartState.tsx:22-28]()

#### Drag-and-Drop System

Fields can be dragged from the `DatasetSelector` to dimension blocks:

```mermaid
sequenceDiagram
    participant User
    participant Field as DatasetField
    participant Drag as handleDragStart
    participant Drop as handleDrop
    participant State as useChartState
    
    User->>Field: Start drag
    Field->>Drag: onDragStart(field)
    Drag->>Drag: Set dragData JSON
    
    User->>Drop: Drop on section
    Drop->>Drop: Parse dragData
    Drop->>Drop: Validate field type
    
    alt Valid dimension → category
        Drop->>State: setCategoryDimensions
    else Valid metric → value
        Drop->>State: setValueDimensions
    else Invalid drop
        Drop->>User: Show toast warning
    end
    
    State->>State: Update sortPriorityOrder
```

**Sources:** 
- [src/frontend/platform/src/pages/Dashboard/components/config/DatasetSelector.tsx:85-102]()
- [src/frontend/platform/src/pages/Dashboard/components/config/useChartState.tsx:299-445]()

### Dimension Block Component

The `DimensionBlock` component displays configured dimensions with controls:

| Control | Purpose | Available For |
|---------|---------|---------------|
| Sort | Ascending/Descending/None | Dimensions |
| Aggregation | Sum/Avg/Count/Max/Min/Distinct Count | Metrics |
| Number Format | Type/Decimals/Units/Separator | Metrics |
| Edit Name | Change display name | All |
| Delete | Remove from configuration | All |

**Sources:** 
- [src/frontend/platform/src/pages/Dashboard/components/config/DimensionBlock.tsx:66-82]()
- [src/frontend/platform/src/pages/Dashboard/components/config/DimensionBlock.tsx:160-173]()

### Aggregation Functions

For metrics, the following aggregations are supported:

```typescript
type AggregationType = 
    | 'sum'            // 求和
    | 'average'        // 平均
    | 'count'          // 计数
    | 'max'            // 最大值
    | 'min'            // 最小值
    | 'distinct_count' // 去重计数
```

**Sources:** 
- [src/frontend/platform/src/pages/Dashboard/components/config/DimensionBlock.tsx:160-167]()
- [src/frontend/platform/public/locales/en-US/dashboard.json:157-163]()

### Virtual Metrics

Virtual metrics are calculated fields that cannot use aggregation:

```typescript
const isVirtualMetric = (field: DatasetField) => {
    return field.isVirtual === true
}

// Virtual metrics skip aggregation menu
if (!isVirtualMetric(dimension)) {
    // Show aggregation options
}
```

**Sources:** 
- [src/frontend/platform/src/pages/Dashboard/components/config/ComponentConfigDrawer.tsx:160-162]()
- [src/frontend/platform/src/pages/Dashboard/components/config/DimensionBlock.tsx:156-158]()

### Number Formatting

Metrics support comprehensive number formatting:

```typescript
type MetricFormat = {
    type: 'number' | 'percent' | 'duration' | 'storage'
    decimalPlaces: number
    unit?: string           // e.g., '', '万', '亿'
    suffix?: string         // Custom suffix
    thousandSeparator: boolean
}
```

**Format Examples:**

| Type | Input | Output |
|------|-------|--------|
| Number (2 decimals) | 1234567.89 | 1,234,567.89 |
| Percent | 0.8543 | 85.43% |
| Duration | 3661 | 1h 1m 1s |
| Storage | 1234567890 | 1.15 GB |

**Sources:** 
- [src/frontend/platform/src/pages/Dashboard/components/config/DimensionBlock.tsx:58-64]()
- [src/frontend/platform/public/locales/en-US/dashboard.json:178-193]()

---

## Filtering System

### Filter Architecture

```mermaid
graph TB
    FilterDialog["FilterConditionDialog"]
    FilterGroup["FilterGroup<br/>logic: and|or"]
    Conditions["FilterCondition[]"]
    
    FilterDialog --> FilterGroup
    FilterGroup --> Conditions
    
    Conditions --> Conditional["Conditional Filter<br/>operator-based"]
    Conditions --> Enum["Enum Filter<br/>multi-select"]
    
    Conditional --> Operators["Operators:<br/>equals, not_equals<br/>contains, not_contains<br/>greater_than, less_than<br/>is_empty, is_not_empty"]
    
    Enum --> EnumAPI["getFieldEnums()<br/>Paginated API"]
```

**Sources:** 
- [src/frontend/platform/src/pages/Dashboard/components/config/FilterConditionDialog.tsx:28-70]()
- [src/frontend/platform/src/pages/Dashboard/components/config/FilterConditionDialog.tsx:364-487]()

### Filter Data Structure

```typescript
interface FilterGroup {
    logic: "and" | "or"
    conditions: FilterCondition[]
}

interface FilterCondition {
    id: string
    fieldCode?: string
    fieldId?: string
    fieldName?: string
    fieldType?: "string" | "number"
    operator?: FilterOperator
    value?: string | number | string[]
    filterType?: "conditional" | "enum"
}

type FilterOperator =
    | "equals" | "not_equals"
    | "contains" | "not_contains"
    | "greater_than" | "greater_than_or_equal"
    | "less_than" | "less_than_or_equal"
    | "is_empty" | "is_not_empty"
    | "enum_in" | "enum_not_in"
```

**Sources:** 
- [src/frontend/platform/src/pages/Dashboard/components/config/FilterConditionDialog.tsx:28-70]()

### Enum Filter with Pagination

For fields with many distinct values, the enum filter uses paginated loading:

```mermaid
sequenceDiagram
    participant User
    participant EnumSelect
    participant API as getFieldEnums()
    participant State
    
    User->>EnumSelect: Open dropdown
    EnumSelect->>API: Fetch page 1 (pageSize=20)
    API-->>EnumSelect: Return first 20 values
    EnumSelect->>State: setValues(result)
    EnumSelect->>State: setHasMore(result.length === 20)
    
    User->>EnumSelect: Scroll to bottom
    EnumSelect->>API: Fetch page 2
    API-->>EnumSelect: Return next 20 values
    EnumSelect->>State: setValues([...prev, ...result])
    
    User->>EnumSelect: Type search term
    EnumSelect->>API: Fetch with keyword
    API-->>EnumSelect: Return filtered results
    EnumSelect->>State: Replace values with search results
```

**Sources:** 
- [src/frontend/platform/src/pages/Dashboard/components/config/FilterConditionDialog.tsx:92-164]()
- [src/frontend/platform/src/pages/Dashboard/components/config/FilterConditionDialog.tsx:188-197]()

### Time Range Filtering

Time filtering is handled separately through the `AdvancedDatePicker`:

```typescript
interface TimeFilter {
    recentDays?: number        // e.g., 7, 30, 90, 180
    type: "recent_days" | "custom" | "all"
    startDate?: string
    endDate?: string
    mode: "dynamic" | "fixed"
}
```

**Shortcut Options:**
- Last 7 days
- Last 30 days
- Last 90 days
- Last 180 days
- Custom range (with dynamic update option)

**Sources:** 
- [src/frontend/platform/src/pages/Dashboard/components/config/ComponentConfigDrawer.tsx:609-634]()
- [src/frontend/platform/public/locales/en-US/dashboard.json:333-338]()

---

## Style Customization

### Style Configuration Structure

```typescript
interface ComponentStyleConfig {
    // Color Theme
    themeColor: string
    bgColor: string
    
    // Title
    title: string
    titleFontSize: number
    titleBold: boolean
    titleItalic: boolean
    titleUnderline: boolean
    titleStrikethrough: boolean
    titleAlign: "left" | "center" | "right"
    titleColor: string
    
    // X-Axis
    xAxisTitle: string
    xAxisFontSize: number
    xAxisBold: boolean
    xAxisItalic: boolean
    xAxisAlign: "left" | "center" | "right"
    xAxisColor: string
    
    // Y-Axis
    yAxisTitle: string
    yAxisFontSize: number
    yAxisBold: boolean
    yAxisItalic: boolean
    yAxisAlign: "left" | "center" | "right"
    yAxisColor: string
    
    // Legend
    legendPosition: "top" | "bottom" | "left" | "right"
    legendFontSize: number
    legendBold: boolean
    legendItalic: boolean
    legendAlign: "left" | "center" | "right"
    legendColor: string
    
    // Metric Card (for type='metric')
    metricFontSize: number
    metricBold: boolean
    metricItalic: boolean
    metricAlign: "left" | "center" | "right"
    metricColor: string
    
    showSubtitle: boolean
    subtitle: string
    subtitleFontSize: number
    
    // Chart Options
    showLegend: boolean
    showAxis: boolean
    showDataLabel: boolean
    showGrid: boolean
}
```

**Sources:** 
- [src/frontend/platform/src/pages/Dashboard/components/config/ComponentConfigDrawer.tsx:27-89]()
- [src/frontend/platform/src/pages/Dashboard/components/config/StyleConfigPanel.tsx:269-365]()

### Color Schemes

The system provides predefined color schemes defined in `colorSchemes`:

```mermaid
graph LR
    Scheme["Color Scheme"]
    ID["scheme.id<br/>e.g., professional-blue"]
    Colors["colors.light[]<br/>5-color palette"]
    
    Scheme --> ID
    Scheme --> Colors
    
    Colors --> Apply["Applied to:<br/>- Bar colors<br/>- Line colors<br/>- Pie slices<br/>- Series colors"]
```

**Sources:** 
- [src/frontend/platform/src/pages/Dashboard/components/config/StyleConfigPanel.tsx:290-300]()
- [src/frontend/platform/src/pages/Dashboard/components/config/StyleConfigPanel.tsx:376-421]()

### TextFormat Component

The reusable `TextFormat` component provides font customization:

| Control | Options | Default |
|---------|---------|---------|
| Font Size | 10, 12, 14, 16, 18, 20, 24, 28 | 14 |
| Color | Color picker | #000000 |
| Alignment | Left, Center, Right | Left |
| Bold | Toggle | false |
| Italic | Toggle | false |

**Sources:** 
- [src/frontend/platform/src/pages/Dashboard/components/config/StyleConfigPanel.tsx:30-180]()

### Dashboard Theme

At the dashboard level, users can choose between light and dark themes:

```typescript
interface DashboardStyleConfig {
    theme: 'light' | 'dark'
}

// Dashboard-level theme affects all components
const handleThemeChange = (theme: 'light' | 'dark') => {
    updateCurrentDashboard({
        ...currentDashboard,
        style_config: { theme }
    })
}
```

**Sources:** 
- [src/frontend/platform/src/pages/Dashboard/components/config/DashboardConfigPanel.tsx:15-44]()

---

## Query Components

Query components provide date range selectors that can link to multiple charts.

### Query Component Architecture

```mermaid
graph TB
    QueryComp["Query Component<br/>type='query'"]
    Config["QueryConfig"]
    Links["linkedComponentIds[]"]
    Conditions["queryConditions"]
    
    QueryComp --> Config
    Config --> Links
    Config --> Conditions
    
    Links --> Chart1["Chart 1"]
    Links --> Chart2["Chart 2"]
    Links --> ChartN["Chart N"]
    
    Conditions --> Display["displayType:<br/>single | range"]
    Conditions --> Granularity["timeGranularity:<br/>year_month<br/>year_month_day<br/>year_month_day_hour"]
    Conditions --> Default["hasDefaultValue"]
    
    Default --> DefaultVal["defaultValue:<br/>shortcutKey<br/>startDate<br/>endDate<br/>mode"]
```

**Sources:** 
- [src/frontend/platform/src/pages/Dashboard/components/config/ComponentConfigDrawer.tsx:702-748]()
- [src/frontend/platform/src/pages/Dashboard/components/config/ChartSelector.tsx:21-33]()

### ChartSelector Configuration

The `ChartSelector` component allows users to:

1. Select which charts to link
2. Choose display type (single time vs. time range)
3. Set time granularity
4. Configure default values

```typescript
interface QueryConfig {
    linkedComponentIds: string[]
    queryConditions: {
        id: string
        displayType: "single" | "range"
        timeGranularity: "year_month" | "year_month_day" | "year_month_day_hour"
        hasDefaultValue: boolean
        defaultValue: {
            shortcutKey?: number
            type: "recent_days" | "custom" | "all"
            mode: TimeRangeMode.Dynamic | TimeRangeMode.Fixed
            recentDays?: number
            startDate?: string
            endDate?: string
        }
    }
}
```

**Sources:** 
- [src/frontend/platform/src/pages/Dashboard/components/config/ChartSelector.tsx:41-267]()
- [src/frontend/platform/src/pages/Dashboard/components/config/ComponentConfigDrawer.tsx:708-732]()

---

## Data Flow and State Management

### State Management Architecture

```mermaid
graph TB
    subgraph "Global State"
        EditorStore["useEditorDashboardStore"]
        ComponentStore["useComponentEditorStore"]
    end
    
    subgraph "Local State"
        ChartState["useChartState Hook"]
        LocalState["Component Local State"]
    end
    
    subgraph "State Data"
        Dashboard["currentDashboard<br/>components[]<br/>style_config"]
        Editing["editingComponent<br/>data_config<br/>style_config"]
        Chart["chartType<br/>dimensions<br/>metrics<br/>filters"]
    end
    
    EditorStore --> Dashboard
    ComponentStore --> Editing
    ChartState --> Chart
    
    Dashboard --> Persist["updateCurrentDashboard()<br/>Save to backend"]
    Editing --> Apply["updateEditingComponent()<br/>Apply changes"]
    Chart --> Render["refreshChart()<br/>Trigger re-render"]
```

**Sources:** 
- [src/frontend/platform/src/pages/Dashboard/components/config/ComponentConfigDrawer.tsx:93-94]()
- [src/frontend/platform/src/pages/Dashboard/components/config/useChartState.tsx:8-36]()

### Chart Update Flow

```mermaid
sequenceDiagram
    participant User
    participant ConfigDrawer
    participant Validate as validateChartConfig()
    participant GetData as getDataConfig()
    participant Update as updateEditingComponent()
    participant Refresh as refreshChart()
    
    User->>ConfigDrawer: Click "Update Chart"
    ConfigDrawer->>Validate: Check configuration
    
    alt Invalid
        Validate-->>User: Show error toast
    else Valid
        Validate->>GetData: Build DataConfig
        GetData->>GetData: Map dimensions to config
        GetData->>GetData: Map metrics to config
        GetData->>GetData: Map filters to config
        GetData->>GetData: Apply time range
        GetData->>GetData: Apply result limit
        
        GetData-->>Update: Return DataConfig
        Update->>Update: Merge with style_config
        Update->>Update: Update component in store
        
        Update->>Refresh: Trigger chart refresh
        Refresh-->>User: Display updated chart
    end
```

**Sources:** 
- [src/frontend/platform/src/pages/Dashboard/components/config/ComponentConfigDrawer.tsx:489-606]()
- [src/frontend/platform/src/pages/Dashboard/components/config/useChartState.tsx:520-639]()

### Data Configuration Generation

The `getDataConfig` method in `useChartState` builds the final configuration:

```typescript
const getDataConfig = (
    limitType: "all" | "limit",
    limitValue: string,
    timeFilter?: TimeFilter
): DataConfig => {
    return {
        dimensions: categoryDimensions.map(d => ({
            fieldId: d.fieldId,
            fieldCode: d.name,
            fieldName: d.originalName,
            displayName: d.displayName,
            sort: d.sort,
            timeGranularity: d.timeGranularity
        })),
        
        stackDimension: stackDimensions.length > 0 ? {
            fieldId: stackDimensions[0].fieldId,
            fieldCode: stackDimensions[0].name,
            fieldName: stackDimensions[0].originalName,
            displayName: stackDimensions[0].displayName,
            sort: stackDimensions[0].sort
        } : undefined,
        
        metrics: valueDimensions.map(d => ({
            fieldId: d.fieldId,
            fieldCode: d.name,
            fieldName: d.originalName,
            displayName: d.displayName,
            aggregation: d.aggregation,
            sort: d.sort,
            numberFormat: d.numberFormat,
            isVirtual: d.isVirtual,
            formula: d.isDivide
        })),
        
        filters: filterGroup?.conditions || [],
        filtersLogic: filterGroup?.logic || "and",
        
        timeFilter: timeFilter,
        
        resultLimit: limitType === "limit" ? {
            limit: limitValue
        } : undefined,
        
        fieldOrder: sortPriorityOrder.map(componentId => {
            const field = [...categoryDimensions, ...stackDimensions, ...valueDimensions]
                .find(d => d.id === componentId)
            return {
                fieldId: field?.fieldId,
                sortPriority: 0
            }
        }).filter(f => f.fieldId)
    }
}
```

**Sources:** 
- [src/frontend/platform/src/pages/Dashboard/components/config/useChartState.tsx:520-639]()

### Validation Rules

The `validateChartConfig` function enforces:

1. **Chart Type Required** (except for query/metric types)
2. **Category Required** (for non-metric cards, at least 1)
3. **Metric Required** (at least 1 value dimension)
4. **Dataset Required** (must select a dataset)
5. **No Invalid Fields** (all fields must exist in dataset)

**Sources:** 
- [src/frontend/platform/src/pages/Dashboard/components/config/ComponentConfigDrawer.tsx:489-528]()

---

## Localization

The dashboard system supports multiple languages (Chinese, English, Japanese) with comprehensive translation keys:

| Category | Key Prefix | Examples |
|----------|-----------|----------|
| Charts | `chart.*` | `chart.barChart`, `chart.lineChart` |
| Datasets | Dataset codes | `mid_user_increment`, `timestamp.day` |
| Filters | `filterConditionDialog.*` | `operators.equals`, `filterTypes.conditional` |
| Config | `componentConfigDrawer.*` | `chartType`, `categoryAxis` |
| Style | `styleConfigPanel.*` | `sections.color`, `labels.themeColor` |
| Validation | `validation.*` | `chartTypeRequired`, `metricRequired` |

**Sources:** 
- [src/frontend/platform/public/locales/en-US/dashboard.json:1-489]()
- [src/frontend/platform/public/locales/zh-Hans/dashboard.json:1-467]()
- [src/frontend/platform/public/locales/ja/dashboard.json:1-490]()

---

# Page: Flow and Skill Management

# Flow and Skill Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docker/bisheng/config/config.yaml](docker/bisheng/config/config.yaml)
- [src/backend/bisheng/api/services/assistant.py](src/backend/bisheng/api/services/assistant.py)
- [src/backend/bisheng/api/services/flow.py](src/backend/bisheng/api/services/flow.py)
- [src/backend/bisheng/api/services/workflow.py](src/backend/bisheng/api/services/workflow.py)
- [src/backend/bisheng/api/utils.py](src/backend/bisheng/api/utils.py)
- [src/backend/bisheng/api/v1/assistant.py](src/backend/bisheng/api/v1/assistant.py)
- [src/backend/bisheng/api/v1/endpoints.py](src/backend/bisheng/api/v1/endpoints.py)
- [src/backend/bisheng/api/v1/flows.py](src/backend/bisheng/api/v1/flows.py)
- [src/backend/bisheng/api/v1/schemas.py](src/backend/bisheng/api/v1/schemas.py)
- [src/backend/bisheng/api/v1/skillcenter.py](src/backend/bisheng/api/v1/skillcenter.py)
- [src/backend/bisheng/api/v1/workflow.py](src/backend/bisheng/api/v1/workflow.py)
- [src/backend/bisheng/database/base.py](src/backend/bisheng/database/base.py)
- [src/backend/bisheng/database/models/assistant.py](src/backend/bisheng/database/models/assistant.py)
- [src/backend/bisheng/database/models/flow.py](src/backend/bisheng/database/models/flow.py)
- [src/backend/bisheng/database/models/flow_version.py](src/backend/bisheng/database/models/flow_version.py)
- [src/backend/bisheng/database/models/template.py](src/backend/bisheng/database/models/template.py)
- [src/backend/bisheng/database/models/user_link.py](src/backend/bisheng/database/models/user_link.py)
- [src/backend/bisheng/graph/vertex/base.py](src/backend/bisheng/graph/vertex/base.py)
- [src/backend/bisheng/initdb_config.yaml](src/backend/bisheng/initdb_config.yaml)
- [src/backend/bisheng/interface/chains/base.py](src/backend/bisheng/interface/chains/base.py)
- [src/backend/bisheng/interface/chains/custom.py](src/backend/bisheng/interface/chains/custom.py)
- [src/backend/bisheng/interface/initialize/loading.py](src/backend/bisheng/interface/initialize/loading.py)
- [src/backend/bisheng/main.py](src/backend/bisheng/main.py)
- [src/backend/bisheng/template/frontend_node/chains.py](src/backend/bisheng/template/frontend_node/chains.py)

</details>



## Purpose and Scope

This document describes the Flow and Skill management system in Bisheng, which handles the complete lifecycle of node-based AI skill compositions. It covers flow creation, multi-version management, graph building and caching, status transitions, updates, and deletion.

Flows (also called "Skills") are the primary building blocks for creating AI capabilities in Bisheng. Each flow is a directed graph of nodes representing LLMs, chains, tools, retrievers, and other components connected by edges that define data flow.

For workflow execution (different from flows), see [Workflow Engine](#3.5). For assistant configuration using flows, see [Assistant System](#3.3). For user access control mechanisms, see [User and Access Control](#4).

---

## Core Data Models

### Flow and FlowVersion Tables

Flows use a two-table structure to support version management:

```mermaid
erDiagram
    Flow ||--o{ FlowVersion : "has versions"
    Flow {
        string id PK "UUID"
        string name "Flow name"
        int user_id FK "Creator"
        string description "Flow description"
        json data "Current graph data"
        string logo "Logo path"
        int status "1=OFFLINE, 2=ONLINE"
        int flow_type "1=FLOW, 10=WORKFLOW"
        string guide_word "Opening message"
        datetime create_time
        datetime update_time
    }
    FlowVersion {
        int id PK "Auto-increment"
        string flow_id FK "References Flow.id"
        string name "Version name (e.g., v1.0)"
        json data "Version graph data"
        string description "Version description"
        int user_id FK "Creator"
        int flow_type "Mirrors Flow.flow_type"
        int is_current "1 if active version"
        int is_delete "Soft delete flag"
        int original_version_id FK "Source version"
        datetime create_time
        datetime update_time
    }
```

**Key Relationships:**
- One `Flow` has many `FlowVersion` records
- Only one version per flow has `is_current=1` at a time
- The `Flow.data` field always mirrors the current version's data
- Version creation copies from an `original_version_id`

**Sources:** [src/backend/bisheng/database/models/flow.py:49-83](), [src/backend/bisheng/database/models/flow_version.py:16-51]()

### Flow Graph Data Structure

The `data` field in both `Flow` and `FlowVersion` tables stores the complete node graph as JSON:

```json
{
  "nodes": [
    {
      "id": "node_uuid",
      "type": "LLMNode",
      "data": {
        "node": {
          "template": {
            "param_name": {
              "value": "param_value",
              "type": "str",
              "required": true
            }
          },
          "base_classes": ["BaseLanguageModel"],
          "description": "Node description"
        }
      },
      "position": {"x": 100, "y": 200}
    }
  ],
  "edges": [
    {
      "id": "edge_uuid",
      "source": "source_node_id",
      "target": "target_node_id",
      "sourceHandle": "output_handle",
      "targetHandle": "input_handle"
    }
  ]
}
```

**Sources:** [src/backend/bisheng/database/models/flow.py:63-77](), [src/backend/bisheng/database/models/flow_version.py:32-46]()

---

## Flow Lifecycle States

Flows transition through two primary states:

```mermaid
stateDiagram-v2
    [*] --> OFFLINE: FlowDao.create_flow()
    OFFLINE --> ValidationPending: PATCH /flows/{id}<br/>status=ONLINE
    ValidationPending --> ONLINE: build_flow_no_yield()<br/>success
    ValidationPending --> OFFLINE: build_flow_no_yield()<br/>failure
    ONLINE --> OFFLINE: PATCH /flows/{id}<br/>status=OFFLINE
    OFFLINE --> Editing: User updates
    Editing --> OFFLINE: Save changes
    ONLINE --> [*]: DELETE /flows/{id}
    OFFLINE --> [*]: DELETE /flows/{id}
    
    note right of ONLINE
        Read-only state
        Cannot edit data
        Can chat/execute
        Version switching blocked
    end note
    
    note right of OFFLINE
        Editable state
        Can update all fields
        Can switch versions
        Cannot chat/execute
    end note
```

**Status Enum (`FlowStatus`):**
- `OFFLINE = 1`: Draft mode, editable, not accessible for execution
- `ONLINE = 2`: Published mode, read-only, available for chat and execution

**Sources:** [src/backend/bisheng/database/models/flow.py:26-28](), [src/backend/bisheng/api/v1/flows.py:126-168]()

---

## Flow Creation

### Creation Flow

Creating a flow involves initializing both the `Flow` record and a default version (`v0`):

**API Endpoint:** `POST /flows/`

**Request Schema (`FlowCreate`):**
```python
{
  "name": "My Skill",
  "description": "Skill description",
  "data": {
    "nodes": [...],
    "edges": [...]
  },
  "logo": "path/to/logo.png",
  "guide_word": "How can I help you?"
}
```

**Creation Sequence:**

```mermaid
sequenceDiagram
    participant Client
    participant POST_flows as "POST /flows"
    participant FlowDao
    participant FlowVersionDao
    participant GroupResourceDao
    participant AuditLog
    participant MySQL
    
    Client->>POST_flows: FlowCreate payload
    POST_flows->>FlowDao: get_flow_by_name(user_id, name)
    alt Name exists
        FlowDao-->>POST_flows: Existing flow
        POST_flows-->>Client: FlowNameExistsError
    else Name unique
        POST_flows->>POST_flows: Flow.model_validate(flow)
        POST_flows->>FlowDao: create_flow(flow, FlowType.FLOW)
        FlowDao->>MySQL: INSERT INTO flow
        FlowDao->>FlowVersionDao: Create FlowVersion(name='v0', is_current=1)
        FlowVersionDao->>MySQL: INSERT INTO flow_version
        FlowDao->>FlowDao: log_event(NEW_APPLICATION)
        FlowDao-->>POST_flows: Flow object
        POST_flows->>FlowVersionDao: get_version_by_flow(flow.id)
        FlowVersionDao-->>POST_flows: version_id
        POST_flows->>GroupResourceDao: Associate with user groups
        POST_flows->>AuditLog: create_build_flow()
        POST_flows-->>Client: FlowRead + version_id
    end
```

**Key Steps:**
1. **Name validation**: Check uniqueness within user's flows via `FlowDao.get_flow_by_name()`
2. **Flow creation**: Insert into `flow` table with `status=1` (OFFLINE)
3. **Default version**: Automatically create version "v0" with `is_current=1`
4. **Group association**: Link flow to user's groups via `GroupResourceDao`
5. **Audit logging**: Record creation event with operator IP and timestamp
6. **Telemetry**: Log `NEW_APPLICATION` event with app metadata

**Sources:** [src/backend/bisheng/api/v1/flows.py:29-45](), [src/backend/bisheng/database/models/flow.py:112-149](), [src/backend/bisheng/api/services/flow.py:1-36]()

---

## Version Management System

### Version Lifecycle and Operations

Flows support comprehensive version control allowing users to maintain multiple snapshots:

```mermaid
stateDiagram-v2
    [*] --> v0: Flow creation<br/>create_flow()
    v0 --> v1_draft: POST /flows/versions<br/>create_new_version()
    v1_draft --> v1_active: POST /flows/change_version<br/>change_current_version()
    v1_active --> v2_draft: Create new version
    v1_active --> v1_draft: Switch to v2
    v1_draft --> v1_deleted: DELETE /flows/versions/{id}<br/>delete_version()
    
    note right of v0
        name='v0'
        is_current=1
        is_delete=0
    end note
    
    note right of v1_active
        is_current=1
        Cannot delete
        Flow.data synced
    end note
    
    note right of v1_draft
        is_current=0
        Can edit/delete
    end note
```

**Version Constraints:**
- Version names must be unique per `flow_id`
- Cannot delete version where `is_current=1`
- Cannot switch version when flow `status=ONLINE`
- Only one version has `is_current=1` at a time
- Deleted versions have `is_delete=1` (soft delete)

**Sources:** [src/backend/bisheng/database/models/flow_version.py:16-51]()

### Creating New Versions

**API Endpoint:** `POST /flows/versions?flow_id={flow_id}`

**Request Schema (`FlowVersionCreate`):**
```python
{
  "name": "v1.1.0",                    # Version name (unique per flow)
  "description": "Added RAG node",     # Version description
  "data": {...},                       # Complete graph data (nodes + edges)
  "original_version_id": 5,            # Source version to copy from
  "flow_type": 1                       # FlowType.FLOW
}
```

**Creation Sequence:**

```mermaid
sequenceDiagram
    participant Client
    participant POST_versions as "POST /flows/versions"
    participant FlowService
    participant FlowDao
    participant FlowVersionDao
    participant VariableDao
    participant MySQL
    
    Client->>POST_versions: flow_id, FlowVersionCreate
    POST_versions->>FlowService: create_new_version()
    FlowService->>FlowDao: aget_flow_by_id(flow_id)
    FlowDao-->>FlowService: Flow object
    FlowService->>FlowService: judge_flow_write_permission()
    FlowService->>FlowVersionDao: get_version_by_name(flow_id, name)
    alt Name exists
        FlowVersionDao-->>Client: VersionNameExistsError
    else Name unique
        FlowService->>FlowVersionDao: create_version(new FlowVersion)
        FlowVersionDao->>MySQL: INSERT INTO flow_version<br/>(is_current=0)
        FlowService->>VariableDao: copy_variables(flow_id, original_id, new_id)
        VariableDao->>MySQL: Copy variable records
        FlowService->>FlowService: get_L2_param_from_flow(data)
        FlowService-->>Client: FlowVersion
    end
```

**Post-Creation Processing:**
1. **Variable copying**: For flows with form inputs, copies variable definitions from `original_version_id`
2. **L2 parameter extraction**: Parses graph to extract file nodes and form parameters via `get_L2_param_from_flow()`
3. **Version is inactive**: New version has `is_current=0`, must be explicitly activated

**Sources:** [src/backend/bisheng/api/services/flow.py:138-172](), [src/backend/bisheng/api/v1/flows.py:56-64](), [src/backend/bisheng/database/models/flow_version.py:60-68]()

### Switching Active Version

**API Endpoint:** `POST /flows/change_version?flow_id={flow_id}&version_id={version_id}`

Only offline flows can switch versions:

```mermaid
sequenceDiagram
    participant Client
    participant POST_change as "POST /flows/change_version"
    participant FlowService
    participant FlowDao
    participant FlowVersionDao
    participant SessionService
    participant MySQL
    
    Client->>POST_change: flow_id, version_id
    POST_change->>FlowService: change_current_version()
    FlowService->>FlowDao: aget_flow_by_id(flow_id)
    FlowDao-->>FlowService: Flow object
    alt Flow status=ONLINE
        FlowService-->>Client: FlowOnlineEditError
    else Flow status=OFFLINE
        FlowService->>FlowVersionDao: aget_version_by_id(version_id)
        FlowVersionDao-->>FlowService: FlowVersion
        alt Version already current
            FlowService-->>Client: Success (no-op)
        else Version switch needed
            FlowService->>FlowVersionDao: change_current_version(flow_id, version)
            FlowVersionDao->>MySQL: UPDATE flow_version<br/>SET is_current=0<br/>WHERE flow_id=X
            FlowVersionDao->>MySQL: UPDATE flow_version<br/>SET is_current=1<br/>WHERE id=Y
            FlowVersionDao->>MySQL: UPDATE flow<br/>SET data=version.data<br/>WHERE id=X
            FlowService->>SessionService: Clear cached graphs
            FlowService-->>Client: Success
        end
    end
```

**Critical Steps:**
1. **Status check**: Flow must have `status=OFFLINE` (enforced before switch)
2. **Atomic update**: Three-step database update:
   - Clear all `is_current` flags for flow: `UPDATE flow_version SET is_current=0 WHERE flow_id=X`
   - Set new current: `UPDATE flow_version SET is_current=1 WHERE id=version_id`
   - Sync Flow.data: `UPDATE flow SET data=version.data WHERE id=flow_id`
3. **Cache invalidation**: Clears any cached graphs in `SessionService`

**Sources:** [src/backend/bisheng/api/services/flow.py:108-136](), [src/backend/bisheng/database/models/flow_version.py:127-154]()

### Updating Version Data

**API Endpoint:** `PUT /flows/versions/{version_id}`

Allows editing version name, description, and graph data:

```mermaid
sequenceDiagram
    participant Client
    participant PUT_version as "PUT /flows/versions/{id}"
    participant FlowService
    participant FlowVersionDao
    participant MySQL
    
    Client->>PUT_version: version_id, FlowVersionCreate
    PUT_version->>FlowService: update_version_info()
    FlowService->>FlowVersionDao: aget_version_by_id(version_id, include_delete=True)
    FlowVersionDao-->>FlowService: FlowVersion
    FlowService->>FlowService: judge_flow_write_permission()
    
    alt Version is_current=1 AND Flow ONLINE AND data update
        FlowService-->>Client: FlowOnlineEditError
    else Update allowed
        FlowService->>FlowVersionDao: Update name, description, data
        FlowVersionDao->>MySQL: UPDATE flow_version
        alt Version is_current=1
            FlowVersionDao->>MySQL: UPDATE flow SET data=version.data
        end
        FlowService->>FlowService: get_L2_param_from_flow(data)
        FlowService-->>Client: Updated FlowVersion
    end
```

**Update Rules:**
- Can always update `name` and `description`
- Can update `data` if version is not current, or flow is offline
- Cannot update current version's `data` when flow is `ONLINE`
- Sets `is_delete=0` (restores deleted versions)

**Sources:** [src/backend/bisheng/api/services/flow.py:175-215](), [src/backend/bisheng/database/models/flow_version.py:87-102]()

### Deleting Versions

**API Endpoint:** `DELETE /flows/versions/{version_id}`

Versions are soft-deleted:

```python
# Deletion rules enforced by FlowService.delete_version()
if version_info.is_current == 1:
    raise CurVersionDelError
    
FlowVersionDao.delete_flow_version(version_id)
# Sets is_delete=1 in database
```

**Constraints:**
- Cannot delete version where `is_current=1`
- Must have `FLOW_WRITE` permission
- Deleted versions remain in database with `is_delete=1`
- Can be restored via update operation

**Sources:** [src/backend/bisheng/api/services/flow.py:62-91](), [src/backend/bisheng/database/models/flow_version.py:181-191]()

---

## Graph Building and Caching

### Building Flows into Executable Graphs

Flows are converted from JSON `data` into executable `Graph` objects via the build process:

**Title:** Flow Build Process

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant process_graph_cached
    participant SessionService
    participant Graph
    participant Vertex
    participant loading
    
    Client->>API: Execute flow (chat/process)
    API->>SessionService: generate_key(session_id, data_graph)
    SessionService-->>API: session_key
    API->>process_graph_cached: process_graph_cached(graph_data, inputs, session_id)
    process_graph_cached->>SessionService: get_cache(session_key)
    
    alt Cache hit
        SessionService-->>process_graph_cached: Cached Graph
    else Cache miss
        process_graph_cached->>Graph: Graph.from_payload(graph_data)
        Graph->>Graph: Build vertices and edges
        loop For each vertex
            Graph->>Vertex: vertex.build(user_id)
            Vertex->>loading: instantiate_class(node_type, params)
            loading-->>Vertex: Built object
        end
        Graph-->>process_graph_cached: Built Graph
        process_graph_cached->>SessionService: set_cache(session_key, graph)
    end
    
    process_graph_cached->>Graph: Execute with inputs
    Graph-->>API: Result
    API-->>Client: Response
```

**Sources:** [src/backend/bisheng/processing/process.py](), [src/backend/bisheng/services/deps.py](), [src/backend/bisheng/graph/graph/base.py]()

### Session Service Integration

The `SessionService` manages caching of built graphs:

**Title:** SessionService Caching Mechanism

```mermaid
graph TB
    subgraph "SessionService"
        gen_key["generate_key(session_id, data_graph)<br/>Returns: MD5 hash"]
        get_cache["get_cache(key)<br/>Returns: Graph or None"]
        set_cache["set_cache(key, graph, langchain_obj)<br/>Stores in Redis"]
        clear["clear_session_id(session_id)<br/>Removes all keys"]
    end
    
    subgraph "Redis Cache"
        redis_key["Key: MD5(session_id + graph_data)"]
        redis_value["Value: Pickled Graph object"]
        redis_ttl["TTL: Configurable"]
    end
    
    subgraph "Cache Key Calculation"
        session_id["session_id (chat_id)"]
        graph_data["flow.data (JSON)"]
        combined["session_id + json.dumps(graph_data)"]
        hash["MD5 hash"]
    end
    
    gen_key --> hash
    session_id --> combined
    graph_data --> combined
    combined --> hash
    hash --> redis_key
    
    get_cache --> redis_key
    set_cache --> redis_value
    clear --> redis_key
```

**Cache Key Generation:**
```python
def generate_key(session_id: str, data_graph: dict) -> str:
    json_str = json.dumps(data_graph, sort_keys=True)
    return hashlib.md5(f"{session_id}{json_str}".encode()).hexdigest()
```

**Cache Behavior:**
- **Key uniqueness**: Each `(session_id, graph_data)` pair gets unique cache key
- **Invalidation**: Changing flow data or session creates new key
- **Clear operations**: `clear_session_id()` removes all cached graphs for a session
- **Storage**: Uses Redis with pickle serialization

**Sources:** [src/backend/bisheng/services/deps.py](), [src/backend/bisheng/core/cache/utils.py]()

### Build Process Details

The `build_flow()` generator streams build progress:

```mermaid
sequenceDiagram
    participant build_flow
    participant Graph
    participant Vertex
    participant instantiate_class
    participant Client
    
    build_flow->>Graph: Graph.from_payload(graph_data)
    Graph-->>build_flow: Graph with vertices
    
    loop For each vertex in generator_build()
        build_flow->>Client: StreamData(event='log', 'Building node X')
        build_flow->>Vertex: vertex.build(user_id)
        Vertex->>Vertex: _build_params()
        Vertex->>instantiate_class: instantiate_class(base_type, node_type, params, user_id)
        instantiate_class-->>Vertex: Built langchain object
        Vertex-->>build_flow: Built
        build_flow->>Client: StreamData(event='message', {valid, params, id, progress})
    end
    
    build_flow-->>build_flow: Return completed Graph
```

**Special Build Logic:**
- **Document loaders**: Skip file processing if `process_file=False`
- **Vector stores**: Auto-generate `collection_name` if not provided: `f'tmp_{flow_id}_{chat_id}'`
- **Error handling**: Streams error events to client if build fails

**Sources:** [src/backend/bisheng/api/utils.py:71-155](), [src/backend/bisheng/graph/vertex/base.py]()

---

## Flow Status Management

### Online/Offline Transitions

Status changes control flow availability and require validation:

**API Endpoint:** `PATCH /flows/{flow_id}`

**Title:** Flow Status Transition with Validation

```mermaid
sequenceDiagram
    participant Client
    participant PATCH_flow as "PATCH /flows/{id}"
    participant FlowDao
    participant build_flow_no_yield
    participant Graph
    participant MySQL
    
    Client->>PATCH_flow: FlowUpdate{status: 2}
    PATCH_flow->>FlowDao: aget_flow_by_id(flow_id)
    FlowDao-->>PATCH_flow: Flow (current status=1)
    
    alt Transition to ONLINE
        PATCH_flow->>build_flow_no_yield: build_flow_no_yield(flow.data, flow_id)
        build_flow_no_yield->>Graph: Graph.from_payload(graph_data)
        loop For each vertex
            build_flow_no_yield->>Graph: vertex.build()
        end
        
        alt Build success
            Graph-->>PATCH_flow: Validated graph
            PATCH_flow->>MySQL: UPDATE flow SET status=2
            PATCH_flow-->>Client: Success
        else Build failure
            Graph-->>PATCH_flow: Exception
            PATCH_flow-->>Client: ServerError
        end
    
    else Edit while ONLINE
        alt Request contains status=OFFLINE
            PATCH_flow->>MySQL: UPDATE flow SET status=1, ...
            PATCH_flow-->>Client: Success
        else Request edits other fields
            PATCH_flow-->>Client: FlowOnlineEditError
        end
    end
```

**Validation Steps:**
1. **Graph construction**: Calls `Graph.from_payload()` to parse nodes and edges
2. **Node building**: Each vertex calls `vertex.build()` to instantiate components
3. **Parameter validation**: All required node parameters must be provided
4. **Connection validation**: All edges must connect valid nodes and ports
5. **Component instantiation**: LLMs, chains, tools must be instantiable

**Status Constraints:**
- **OFFLINE → ONLINE**: Requires successful `build_flow_no_yield()`
- **ONLINE → OFFLINE**: Allowed without validation
- **Edit while ONLINE**: Only `status` field can change (to OFFLINE)
- **Version switch**: Blocked when ONLINE

**Sources:** [src/backend/bisheng/api/v1/flows.py:126-168](), [src/backend/bisheng/api/utils.py:158-220]()

---

## Flow Updates

### Updating Flow Metadata

**API Endpoint:** `PATCH /flows/{flow_id}`

Flow updates follow strict rules based on online status:

**Request Schema (`FlowUpdate`):**
```python
{
  "name": "Updated name",          # Optional
  "description": "New description", # Optional
  "logo": "new/logo/path.png",     # Optional
  "guide_word": "New greeting",    # Optional
  "data": {...},                   # Optional (graph changes)
  "status": 1 or 2                 # Optional
}
```

**Update Constraints:**

| Flow Status | Allowed Updates | Forbidden Updates |
|-------------|----------------|-------------------|
| **OFFLINE** | All fields | None |
| **ONLINE** | `status` (only to OFFLINE) | `data`, `name`, `description`, `logo`, `guide_word` |

**Title:** Flow Update Logic

```mermaid
graph TD
    Request["PATCH /flows/{id}<br/>FlowUpdate"]
    GetFlow["FlowDao.aget_flow_by_id()"]
    CheckPerm{"Has FLOW_WRITE?"}
    CheckStatus{"Flow status?"}
    CheckData{"Update includes<br/>data or metadata?"}
    ApplyUpdate["Apply updates:<br/>setattr(flow, key, value)"]
    Reject["FlowOnlineEditError"]
    Save["FlowDao.aupdate_flow()"]
    Success["Return updated Flow"]
    
    Request --> GetFlow
    GetFlow --> CheckPerm
    CheckPerm -->|No| Unauthorized
    CheckPerm -->|Yes| CheckStatus
    CheckStatus -->|OFFLINE| ApplyUpdate
    CheckStatus -->|ONLINE| CheckData
    CheckData -->|Only status→OFFLINE| ApplyUpdate
    CheckData -->|Other fields| Reject
    ApplyUpdate --> Save
    Save --> Success
```

**Special Handling:**
- **Empty logo**: If `logo=""`, field is not updated (preserves existing)
- **Ignored fields**: `create_time`, `update_time`, `data` are never updated directly via PATCH
- **Graph data updates**: Must be done through version operations

**Sources:** [src/backend/bisheng/api/v1/flows.py:126-168](), [src/backend/bisheng/database/models/flow.py:374-387]()

---

## Flow Deletion

### Deletion Process

**API Endpoint:** `DELETE /flows/{flow_id}`

Deletion permanently removes the flow and cascades to related resources:

**Title:** Flow Deletion Sequence

```mermaid
sequenceDiagram
    participant Client
    participant DELETE_flow as "DELETE /flows/{id}"
    participant FlowDao
    participant FlowVersionDao
    participant GroupResourceDao
    participant TagDao
    participant AuditLog
    participant Telemetry
    participant MySQL
    
    Client->>DELETE_flow: flow_id
    DELETE_flow->>FlowDao: get_flow_by_id(flow_id)
    FlowDao-->>DELETE_flow: Flow object
    DELETE_flow->>DELETE_flow: access_check(FLOW_WRITE)
    
    alt Has permission
        DELETE_flow->>FlowDao: delete_flow(flow)
        FlowDao->>MySQL: DELETE FROM flow WHERE id=X
        FlowDao->>FlowVersionDao: UPDATE flow_version<br/>SET is_delete=1<br/>WHERE flow_id=X
        DELETE_flow->>GroupResourceDao: delete_group_resource_by_third_id(flow_id)
        GroupResourceDao->>MySQL: DELETE FROM group_resource<br/>WHERE third_id=X
        DELETE_flow->>TagDao: Delete tag associations
        DELETE_flow->>AuditLog: delete_build_flow()
        DELETE_flow->>Telemetry: log_event(DELETE_APPLICATION)
        DELETE_flow-->>Client: Success
    else No permission
        DELETE_flow-->>Client: UnAuthorizedError
    end
```

**Cascading Cleanup:**

| Resource | Action | Table | Effect |
|----------|--------|-------|--------|
| **Flow record** | Hard delete | `flow` | `DELETE FROM flow WHERE id=X` |
| **All versions** | Soft delete | `flow_version` | `UPDATE flow_version SET is_delete=1 WHERE flow_id=X` |
| **Group links** | Hard delete | `group_resource` | `DELETE FROM group_resource WHERE third_id=X AND type='flow'` |
| **Tag links** | Hard delete | `resource_tag` | Delete tag associations |
| **Chat sessions** | Update | `message_session` | Update `flow_name`, `desc`, `logo` (preserves history) |
| **Variables** | Orphaned | `variable_value` | Remain in database (unused) |

**Permission Requirements:**
- Must have `FLOW_WRITE` access type
- Owner always has permission
- Admin users have permission
- Role-based access checked via `RoleAccessDao`

**Sources:** [src/backend/bisheng/api/v1/flows.py:171-195](), [src/backend/bisheng/database/models/flow.py:152-161](), [src/backend/bisheng/api/services/flow.py]()

---

## Access Control

### Permission Types for Flows

| Access Type | Enum Value | Description | Required For |
|------------|------------|-------------|--------------|
| `FLOW` | `AccessType.FLOW` | Read access | View flow, list flows, execute |
| `FLOW_WRITE` | `AccessType.FLOW_WRITE` | Write access | Edit, delete, change status, manage versions |

**Title:** Flow Permission Check Logic

```mermaid
graph TB
    Request["API Request"]
    CheckAdmin{"User is admin?"}
    CheckOwner{"User is owner?"}
    GetRoles["UserRoleDao.get_user_roles()"]
    GetAccess["RoleAccessDao.get_role_access()"]
    CheckResource{"flow_id in<br/>accessible IDs?"}
    Allow["Grant access"]
    Deny["UnAuthorizedError"]
    
    Request --> CheckAdmin
    CheckAdmin -->|Yes| Allow
    CheckAdmin -->|No| CheckOwner
    CheckOwner -->|user_id == flow.user_id| Allow
    CheckOwner -->|No| GetRoles
    GetRoles --> GetAccess
    GetAccess --> CheckResource
    CheckResource -->|Yes| Allow
    CheckResource -->|No| Deny
```

**Access Hierarchy:**
1. **System admin** (`user.is_admin()`): Full access to all flows
2. **Flow owner** (`user_id == flow.user_id`): Full read/write access
3. **Role-based access**: Granted via `role_access` table entries
4. **Group membership**: Flows linked to user's groups via `group_resource`

**Checking Permissions in Code:**
```python
# Read permission check
if not await login_user.async_access_check(flow.user_id, flow_id, AccessType.FLOW):
    raise UnAuthorizedError()

# Write permission check  
if not await login_user.async_access_check(flow.user_id, flow_id, AccessType.FLOW_WRITE):
    raise UnAuthorizedError()
```

**Sources:** [src/backend/bisheng/common/dependencies/user_deps.py](), [src/backend/bisheng/database/models/role_access.py]()


---

## API Routes

### Flow Management Endpoints

**Base Path:** `/api/v1/flows`

| Method | Endpoint | Function | Purpose | Permission |
|--------|----------|----------|---------|------------|
| POST | `/flows/` | `create_flow()` | Create new flow | Authenticated user |
| GET | `/flows/` | `read_flows()` | List flows (paginated, filtered) | User's accessible flows |
| GET | `/flows/{flow_id}` | `read_flow()` | Get flow details | `FLOW` read |
| PATCH | `/flows/{flow_id}` | `update_flow()` | Update flow metadata/status | `FLOW_WRITE` |
| DELETE | `/flows/{flow_id}` | `delete_flow()` | Delete flow | `FLOW_WRITE` |

**Sources:** [src/backend/bisheng/api/v1/flows.py:29-195]()

### Version Management Endpoints

| Method | Endpoint | Function | Purpose | Permission |
|--------|----------|----------|---------|------------|
| GET | `/flows/versions?flow_id=X` | `get_versions()` | List all versions | `FLOW` read |
| POST | `/flows/versions?flow_id=X` | `create_versions()` | Create new version | `FLOW_WRITE` |
| GET | `/flows/versions/{version_id}` | `get_version_info()` | Get version details | `FLOW` read |
| PUT | `/flows/versions/{version_id}` | `update_versions()` | Update version | `FLOW_WRITE` |
| DELETE | `/flows/versions/{version_id}` | `delete_versions()` | Delete version | `FLOW_WRITE` |
| POST | `/flows/change_version` | `change_version()` | Switch active version | `FLOW_WRITE` |

**Query Parameters:**
- `flow_id`: Required for list/create operations
- `version_id`: Version identifier for get/update/delete

**Sources:** [src/backend/bisheng/api/v1/flows.py:48-104]()

### Flow Execution Endpoint

| Method | Endpoint | Function | Purpose |
|--------|----------|----------|---------|
| POST | `/process` | `process_flow()` | Execute flow synchronously with inputs |

**Request Body:**
```json
{
  "flow_id": "uuid",
  "inputs": {"input_key": "value"},
  "session_id": "optional_session",
  "clear_cache": false,
  "history_count": 10
}
```

**Sources:** [src/backend/bisheng/api/v1/endpoints.py:174-349]()

---

## Audit Logging

All lifecycle operations are logged via `AuditLogService`:

**Logged Events:**
- `create_build_flow()`: Flow/Workflow creation
- `create_build_assistant()`: Assistant creation
- `update_build_flow()`: Flow/Workflow updates
- `update_build_assistant()`: Assistant updates
- `delete_build_flow()`: Flow/Workflow deletion
- `delete_build_assistant()`: Assistant deletion
- `create_chat_flow()`: New flow chat session
- `create_chat_assistant()`: New assistant chat session

**Audit Log Fields:**
- `user_id`: Operator
- `group_ids`: Associated groups
- `ip`: Request IP address
- `event_type`: Operation type
- `object_id`: Target application ID
- `timestamp`: Operation time

**Sources:** [src/backend/bisheng/api/services/audit_log.py]()

---

## Telemetry Events

Application lifecycle events trigger telemetry logging:

| Event Type | Trigger | Event Data |
|------------|---------|------------|
| `NEW_APPLICATION` | Creation | `app_id`, `app_name`, `app_type` |
| `EDIT_APPLICATION` | Update/Version change | None |
| `DELETE_APPLICATION` | Deletion | None |
| `APPLICATION_ALIVE` | WebSocket session | `app_id`, `chat_id`, `start_time`, `end_time` |
| `APPLICATION_PROCESS` | Message processing | `app_id`, `chat_id`, `process_time` |

**Sources:** [src/backend/bisheng/database/models/flow.py:139-147](), [src/backend/bisheng/api/services/assistant.py:174-181]()

---

# Page: LLM and Component Integration

# LLM and Component Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [.github/workflows/release.yml](.github/workflows/release.yml)
- [.pre-commit-config.yaml](.pre-commit-config.yaml)
- [docker/bisheng/config/config.yaml](docker/bisheng/config/config.yaml)
- [src/backend/bisheng/api/services/chat_imp.py](src/backend/bisheng/api/services/chat_imp.py)
- [src/backend/bisheng/api/utils.py](src/backend/bisheng/api/utils.py)
- [src/backend/bisheng/api/v1/endpoints.py](src/backend/bisheng/api/v1/endpoints.py)
- [src/backend/bisheng/database/base.py](src/backend/bisheng/database/base.py)
- [src/backend/bisheng/graph/vertex/base.py](src/backend/bisheng/graph/vertex/base.py)
- [src/backend/bisheng/initdb_config.yaml](src/backend/bisheng/initdb_config.yaml)
- [src/backend/bisheng/interface/chains/base.py](src/backend/bisheng/interface/chains/base.py)
- [src/backend/bisheng/interface/chains/custom.py](src/backend/bisheng/interface/chains/custom.py)
- [src/backend/bisheng/interface/initialize/loading.py](src/backend/bisheng/interface/initialize/loading.py)
- [src/backend/bisheng/interface/initialize/vector_store.py](src/backend/bisheng/interface/initialize/vector_store.py)
- [src/backend/bisheng/main.py](src/backend/bisheng/main.py)
- [src/backend/bisheng/processing/base.py](src/backend/bisheng/processing/base.py)
- [src/backend/bisheng/processing/process.py](src/backend/bisheng/processing/process.py)
- [src/backend/bisheng/services/session/service.py](src/backend/bisheng/services/session/service.py)
- [src/backend/bisheng/template/frontend_node/chains.py](src/backend/bisheng/template/frontend_node/chains.py)
- [src/backend/bisheng/template/frontend_node/embeddings.py](src/backend/bisheng/template/frontend_node/embeddings.py)
- [src/backend/bisheng/template/frontend_node/llms.py](src/backend/bisheng/template/frontend_node/llms.py)
- [src/backend/bisheng/template/frontend_node/vectorstores.py](src/backend/bisheng/template/frontend_node/vectorstores.py)
- [src/backend/test/test_filelib.py](src/backend/test/test_filelib.py)

</details>



## Purpose and Scope

This document explains how Bisheng integrates Large Language Models (LLMs) and other AI components into the workflow system. It covers:

1. **LLM Service Integration**: How the `LLMService` manages model lifecycle and configuration
2. **Model Selection**: Mechanisms for choosing and configuring LLM and embedding models
3. **Component Initialization Framework**: The `instantiate_class()` routing system that creates component instances
4. **Frontend Node Configuration**: How component parameters are exposed and validated in the UI
5. **Xinference Client Integration**: Using xinference as a model serving backend

For workflow execution details, see [Workflow Engine](#3.5). For custom component development, see [Custom Component System](#6.4).

---

## Component Type System

Bisheng supports multiple component types, each with its own registry and loader. The type system is defined in [src/backend/bisheng/interface/importing/utils.py:36-59]() within the `import_by_type()` function.

### Supported Component Types

| Type | Description | Registry Location | Example Classes |
|------|-------------|-------------------|-----------------|
| `llms` | Language models (LLM and Chat) | `llm_type_to_cls_dict` | `ChatOpenAI`, `ChatAnthropic`, `BishengLLM` |
| `embeddings` | Text embedding models | `embedding_type_to_cls_dict` | `OpenAIEmbeddings`, `OpenAIProxyEmbedding` |
| `agents` | Agent implementations | Dynamic import | `JsonAgent`, `VectorStoreAgent` |
| `chains` | Chain components | `chain_creator` | `SeriesCharacterChain`, `load_qa_chain` |
| `tools` | Tool implementations | `tool_creator` | `PythonFunctionTool`, custom tools |
| `memory` | Memory/history stores | `memory_type_to_cls_dict` | `PostgresChatMessageHistory` |
| `vectorstores` | Vector database clients | `vectorstore_creator` | Milvus, Elasticsearch wrappers |
| `documentloaders` | Document loaders | `documentloaders_type_to_cls_dict` | PDF loaders, text loaders |
| `textsplitters` | Text chunking strategies | `textsplitter_type_to_cls_dict` | Character splitters, recursive splitters |
| `output_parsers` | Output format parsers | `output_parser_creator` | `StructuredOutputParser` |
| `custom_components` | User-defined components | Dynamic evaluation | Custom classes |

**Sources:** [src/backend/bisheng/interface/importing/utils.py:36-59]()

---

## Component Registry Architecture

### Registry Structure

The component registry system uses dictionaries to map component names (strings) to their corresponding Python classes. The primary registry is defined in [src/backend/bisheng/interface/custom_lists.py]().

```mermaid
graph TB
    subgraph "Registry Initialization"
        LANGCHAIN["LangChain Base<br/>llms.__all__<br/>embeddings.__all__<br/>etc."]
        CONTRIB["bisheng_langchain<br/>chat_models.__all__<br/>document_loaders.__all__"]
        CUSTOM["Custom Components<br/>CUSTOM_AGENTS<br/>CUSTOM_CHAINS<br/>CUSTOM_EMBEDDING"]
    end
    
    subgraph "Registry Dictionaries"
        LLM_REG["llm_type_to_cls_dict"]
        EMB_REG["embedding_type_to_cls_dict"]
        LOADER_REG["documentloaders_type_to_cls_dict"]
        SPLITTER_REG["textsplitter_type_to_cls_dict"]
        CUSTOM_NODES["CUSTOM_NODES"]
    end
    
    LANGCHAIN -->|"Base components"| LLM_REG
    LANGCHAIN -->|"Base embeddings"| EMB_REG
    LANGCHAIN -->|"Base loaders"| LOADER_REG
    
    CONTRIB -->|"update()"| LLM_REG
    CONTRIB -->|"update()"| EMB_REG
    CONTRIB -->|"update()"| LOADER_REG
    
    CUSTOM -->|"merge"| CUSTOM_NODES
    
    LLM_REG -->|"ChatOpenAI: ChatOpenAI"| LLM_REG
    LLM_REG -->|"BishengLLM: BishengLLM"| LLM_REG
    
    EMB_REG -->|"OpenAIEmbeddings: OpenAIEmbeddings"| EMB_REG
    CUSTOM -->|"OpenAIProxyEmbedding"| EMB_REG
```

**Sources:** [src/backend/bisheng/interface/custom_lists.py:21-121]()

### LLM Registry

The LLM registry aggregates models from multiple sources:

```python
# Base LangChain LLMs
llm_type_to_cls_dict = llms.get_type_to_cls_dict()

# Major chat models
llm_type_to_cls_dict['ChatOpenAI'] = ChatOpenAI
llm_type_to_cls_dict['ChatAnthropic'] = ChatAnthropic
llm_type_to_cls_dict['ChatVertexAI'] = ChatVertexAI
llm_type_to_cls_dict['MiniMaxChat'] = MiniMaxChat
llm_type_to_cls_dict['ChatTongyi'] = ChatTongyi
llm_type_to_cls_dict['ChatZhipuAI'] = ChatZhipuAI
llm_type_to_cls_dict['ChatDeepSeek'] = ChatDeepSeek

# Contribute models from bisheng_langchain
llm_type_to_cls_dict.update({
    llm_name: import_class(f'bisheng_langchain.chat_models.{llm_name}')
    for llm_name in chat_models.__all__
})
```

**Sources:** [src/backend/bisheng/interface/custom_lists.py:22-45]()

### Embedding Registry

The embedding registry similarly combines multiple sources:

```python
# LangChain community embeddings
embedding_type_to_cls_dict = {
    embedding_name: import_class(f'langchain_community.embeddings.{embedding_name}')
    for embedding_name in embeddings.__all__
}

# Bisheng contribute embeddings
embedding_type_to_cls_dict.update({
    embedding_name: import_class(f'bisheng_langchain.embeddings.{embedding_name}')
    for embedding_name in contribute_embeddings.__all__
})

# OpenAI embeddings
embedding_type_to_cls_dict.update({
    "OpenAIEmbeddings": OpenAIEmbeddings,
    "AzureOpenAIEmbeddings": AzureOpenAIEmbeddings,
})
```

**Sources:** [src/backend/bisheng/interface/custom_lists.py:82-95]()

### Custom Nodes Merge

Custom implementations are merged into a unified registry:

```python
CUSTOM_NODES = {
    **CUSTOM_AGENTS,      # From bisheng.interface.agents.custom
    **CUSTOM_CHAINS,      # From bisheng.interface.chains.custom
    **CUSTOM_EMBEDDING,   # From bisheng.interface.embeddings.custom
}
```

**Sources:** [src/backend/bisheng/interface/custom_lists.py:116-120]()

---

## Dynamic Import Mechanism

The dynamic import system provides a unified interface for loading components by type and name. The core function is `import_by_type()` which dispatches to type-specific import functions.

### Import Dispatcher Flow

```mermaid
graph TB
    REQUEST["import_by_type(type, name)"]
    
    subgraph "Type Routing"
        FUNC_DICT["func_dict lookup"]
        LLM_ROUTE{"type == 'llms'?"}
        LLM_KEY{"name in chat_models.__all__?"}
        OTHER_ROUTE["Direct function<br/>lookup"]
    end
    
    subgraph "LLM Importers"
        CONTRIB["import_chain_contribute_llm()"]
        CHAT["import_chat_llm()"]
        BASE["import_llm()"]
    end
    
    subgraph "Other Importers"
        EMB["import_embedding()"]
        AGENT["import_agent()"]
        TOOL["import_tool()"]
        CHAIN["import_chain()"]
        PARSER["import_output_parser()"]
    end
    
    REQUEST --> FUNC_DICT
    FUNC_DICT --> LLM_ROUTE
    
    LLM_ROUTE -->|"Yes"| LLM_KEY
    LLM_KEY -->|"Yes"| CONTRIB
    LLM_KEY -->|"No, 'chat' in name"| CHAT
    LLM_KEY -->|"No"| BASE
    
    LLM_ROUTE -->|"No"| OTHER_ROUTE
    
    OTHER_ROUTE --> EMB
    OTHER_ROUTE --> AGENT
    OTHER_ROUTE --> TOOL
    OTHER_ROUTE --> CHAIN
    OTHER_ROUTE --> PARSER
```

**Sources:** [src/backend/bisheng/interface/importing/utils.py:31-67]()

### Import Function Hierarchy

Each component type has a dedicated import function that knows where to find the component:

**LLM Import** [src/backend/bisheng/interface/importing/utils.py:89-94]():
```python
def import_chat_llm(llm: str) -> BaseChatModel:
    from bisheng.interface.llms.base import llm_creator
    if llm in llm_creator.type_to_loader_dict:
        return llm_creator.type_to_loader_dict[llm]
    return import_class(f'bisheng_langchain.chat_models.{llm}')
```

**Embedding Import** [src/backend/bisheng/interface/importing/utils.py:186-190]():
```python
def import_embedding(embedding: str) -> Any:
    from bisheng.interface.embeddings.base import embedding_creator
    return next(x for x in embedding_creator.type_to_loader_dict.values()
                if x.__name__ == embedding)
```

**Agent Import** [src/backend/bisheng/interface/importing/utils.py:155-161]():
```python
def import_agent(agent: str) -> Agent:
    from bisheng_langchain import agents
    if agent in agents.__all__:
        return import_class(f'bisheng_langchain.agents.{agent}')
    return import_class(f'langchain.agents.{agent}')
```

**Tool Import** [src/backend/bisheng/interface/importing/utils.py:170-177]():
```python
def import_tool(tool: str) -> BaseTool:
    from bisheng.interface.tools.base import tool_creator
    if tool in tool_creator.type_to_loader_dict:
        return tool_creator.type_to_loader_dict[tool]['fcn']
    return import_class(f'langchain_community.tools.{tool}')
```

**Sources:** [src/backend/bisheng/interface/importing/utils.py:89-177]()

### Module Import Utilities

The `import_class()` and `import_module()` functions provide low-level import capabilities:

**import_class()** [src/backend/bisheng/interface/importing/utils.py:126-130]():
```python
def import_class(class_path: str) -> Any:
    """Import class from class path"""
    module_path, class_name = class_path.rsplit('.', 1)
    module = import_module(module_path)
    return getattr(module, class_name)
```

**import_module()** [src/backend/bisheng/interface/importing/utils.py:17-28]():
```python
def import_module(module_path: str) -> Any:
    """Import module from module path"""
    if 'from' not in module_path:
        return importlib.import_module(module_path)
    
    # Parse "from X import Y" syntax
    _, module_path, _, object_name = module_path.split()
    module = importlib.import_module(module_path)
    return getattr(module, object_name)
```

**Sources:** [src/backend/bisheng/interface/importing/utils.py:17-130]()

---

## Proxy and Custom Component Implementations

### OpenAIProxyEmbedding

The `OpenAIProxyEmbedding` class provides a proxy pattern for dynamically loading the default knowledge base embedding model:

```python
class OpenAIProxyEmbedding(Embeddings):
    embeddings: Optional[Embeddings] = Field(default=None)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        from bisheng.llm.domain.services import LLMService
        # Dynamically load default embedding
        self.embeddings = LLMService.get_knowledge_default_embedding(0)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        return self.embeddings.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        return self.embeddings.embed_query(text)
```

This pattern allows:
1. **Runtime Configuration**: The actual embedding model is determined at runtime from system configuration
2. **Transparent Delegation**: All embedding calls are delegated to the configured model
3. **Centralized Management**: Embedding model selection is managed by `LLMService`

**Sources:** [src/backend/bisheng/interface/embeddings/custom.py:12-31]()

### FakeEmbedding

The `FakeEmbedding` class provides a placeholder implementation for cases where a model has been decommissioned but vector stores still reference it:

```python
class FakeEmbedding(Embeddings):
    """为了保证milvus等，在模型下线还能继续用"""
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return []
    
    def embed_query(self, text: str) -> List[float]:
        return []
```

This ensures that:
- Vector stores using retired models can still be loaded
- System remains stable when models are removed
- Graceful degradation instead of crashes

**Sources:** [src/backend/bisheng/interface/embeddings/custom.py:33-42]()

### Custom Embedding Registry

Custom embedding implementations are registered in a dictionary:

```python
CUSTOM_EMBEDDING = {
    'OpenAIProxyEmbedding': OpenAIProxyEmbedding,
    'BishengEmbedding': BishengEmbedding,  # From bisheng.llm.domain.llm.embedding
}
```

**Sources:** [src/backend/bisheng/interface/embeddings/custom.py:45-48]()

### BishengLLM Integration

The `BishengLLM` class is registered in the LLM creator as a special custom LLM implementation:

```python
class LLMCreator(LangChainTypeCreator):
    @property
    def type_to_loader_dict(self) -> Dict:
        if self.type_dict is None:
            self.type_dict = llm_type_to_cls_dict
            self.type_dict.update({
                'BishengLLM': BishengLLM,
            })
        return self.type_dict
```

**Sources:** [src/backend/bisheng/interface/llms/base.py:20-26]()

---

## Creator Pattern and Frontend Integration

The system uses a "Creator" pattern to manage component types and generate frontend templates. Each component type has a dedicated creator class that extends `LangChainTypeCreator`.

### Creator Class Architecture

```mermaid
graph TB
    subgraph "Base Creator"
        BASE["LangChainTypeCreator<br/>(abstract base)"]
    end
    
    subgraph "Creator Implementations"
        LLM_C["LLMCreator<br/>type_name='llms'"]
        EMB_C["embedding_creator"]
        PARSER_C["OutputParserCreator<br/>type_name='output_parsers'"]
        CHAIN_C["chain_creator"]
        TOOL_C["tool_creator"]
        MEMORY_C["memory_creator"]
    end
    
    subgraph "Frontend Nodes"
        LLM_FN["LLMFrontendNode"]
        PARSER_FN["OutputParserFrontendNode"]
        OTHER_FN["Other FrontendNode classes"]
    end
    
    subgraph "Methods"
        LOADER["type_to_loader_dict<br/>Component registry"]
        SIG["get_signature(name)<br/>Generate template"]
        LIST["to_list()<br/>Available components"]
        FRONTEND["frontend_node_class<br/>UI template class"]
    end
    
    BASE --> LLM_C
    BASE --> EMB_C
    BASE --> PARSER_C
    BASE --> CHAIN_C
    BASE --> TOOL_C
    BASE --> MEMORY_C
    
    LLM_C --> LOADER
    LLM_C --> SIG
    LLM_C --> LIST
    LLM_C --> FRONTEND
    
    LLM_C -.->|"returns"| LLM_FN
    PARSER_C -.->|"returns"| PARSER_FN
    
    LOADER -.->|"llm_type_to_cls_dict"| LLM_C
    FRONTEND -.->|"template generation"| LLM_FN
```

**Sources:** [src/backend/bisheng/interface/llms/base.py:12-48](), [src/backend/bisheng/interface/output_parsers/base.py:12-61]()

### LLMCreator Implementation

The `LLMCreator` class manages LLM component registration and frontend template generation:

```python
class LLMCreator(LangChainTypeCreator):
    type_name: str = 'llms'

    @property
    def frontend_node_class(self) -> Type[LLMFrontendNode]:
        return LLMFrontendNode

    @property
    def type_to_loader_dict(self) -> Dict:
        if self.type_dict is None:
            self.type_dict = llm_type_to_cls_dict
            self.type_dict.update({'BishengLLM': BishengLLM})
        return self.type_dict

    def get_signature(self, name: str) -> Optional[Dict]:
        """Get the signature of an llm."""
        try:
            return build_template_from_class(name, llm_type_to_cls_dict)
        except ValueError as exc:
            raise ValueError('LLM not found') from exc
        except AttributeError as exc:
            logger.error(f'LLM {name} not loaded: {exc}')
            return None

    def to_list(self) -> List[str]:
        return [
            llm.__name__
            for llm in self.type_to_loader_dict.values()
            if llm.__name__ in settings.llms or settings.dev
        ]
```

**Key Methods:**
- `type_to_loader_dict`: Returns the registry of LLM classes
- `get_signature()`: Generates UI template from class introspection
- `to_list()`: Returns filtered list of available LLMs based on settings
- `frontend_node_class`: Returns the frontend template class

**Sources:** [src/backend/bisheng/interface/llms/base.py:12-47]()

### OutputParserCreator Implementation

The `OutputParserCreator` demonstrates support for alternative constructor patterns:

```python
class OutputParserCreator(LangChainTypeCreator):
    type_name: str = 'output_parsers'
    from_method_nodes: ClassVar[Dict] = {
        'StructuredOutputParser': 'from_response_schemas',
    }

    @property
    def type_to_loader_dict(self) -> Dict:
        if self.type_dict is None:
            self.type_dict = {}
            for output_parser_name in output_parsers.__all__:
                if not settings.dev and output_parser_name not in settings.output_parsers:
                    continue
                if output_parser_name == "GuardrailsOutputParser":
                    self.type_dict[output_parser_name] = import_class(
                        f'langchain_community.output_parsers.rail_parser.{output_parser_name}'
                    )
                else:
                    self.type_dict[output_parser_name] = import_class(
                        f'langchain.output_parsers.{output_parser_name}'
                    )
        return self.type_dict

    def get_signature(self, name: str) -> Optional[Dict]:
        try:
            if name in self.from_method_nodes:
                # Use factory method instead of constructor
                return build_template_from_method(
                    name,
                    type_to_cls_dict=self.type_to_loader_dict,
                    method_name=self.from_method_nodes[name],
                )
            else:
                return build_template_from_class(
                    name,
                    type_to_cls_dict=self.type_to_loader_dict,
                )
        except (ValueError, AttributeError) as exc:
            logger.error(f'OutputParser {name} not loaded: {exc}')
        return None
```

**Special Features:**
- `from_method_nodes`: Maps component names to factory methods (e.g., `from_response_schemas`)
- Conditional template generation based on constructor pattern
- Settings-based filtering of available components

**Sources:** [src/backend/bisheng/interface/output_parsers/base.py:12-61]()

---

## Frontend Node Definitions

Frontend nodes define the UI templates for components in the visual editor. These are stored in [src/backend/bisheng/custom/customs.py]().

### Custom Nodes Structure

```python
CUSTOM_NODES = {
    'tools': {
        'PythonFunctionTool': frontend_node.tools.PythonFunctionToolNode(),
        'PythonFunction': frontend_node.tools.PythonFunctionNode(),
        'Tool': frontend_node.tools.ToolNode(),
    },
    'agents': {
        'JsonAgent': frontend_node.agents.JsonAgentNode(),
        'AgentInitializer': frontend_node.agents.InitializeAgentNode(),
        'VectorStoreAgent': frontend_node.agents.VectorStoreAgentNode(),
        'VectorStoreRouterAgent': frontend_node.agents.VectorStoreRouterAgentNode(),
    },
    'utilities': {
        'SQLDatabase': frontend_node.agents.SQLDatabaseNode(),
    },
    'memories': {
        'PostgresChatMessageHistory': 
            frontend_node.memories.PostgresChatMessageHistoryFrontendNode(),
        'MongoDBChatMessageHistory': 
            frontend_node.memories.MongoDBChatMessageHistoryFrontendNode(),
    },
    'chains': {
        'SeriesCharacterChain': frontend_node.chains.SeriesCharacterChainNode(),
        'TimeTravelGuideChain': frontend_node.chains.TimeTravelGuideChainNode(),
        'MidJourneyPromptChain': frontend_node.chains.MidJourneyPromptChainNode(),
        'load_qa_chain': frontend_node.chains.CombineDocsChainNode(),
        'load_summarize_chain': frontend_node.chains.SummarizeDocsChain(),
    },
    'embeddings': {
        'OpenAIProxyEmbedding': frontend_node.embeddings.OpenAIProxyEmbedding(),
    },
    'input_output': {
        'InputNode': frontend_node.input_output.InputNode(),
        'OutputNode': frontend_node.input_output.OutputNode(),
        'InputFileNode': frontend_node.input_output.InputFileNode(),
    },
}
```

The `get_custom_nodes()` function provides access to type-specific custom nodes:

```python
def get_custom_nodes(node_type: str):
    """Get custom nodes."""
    return CUSTOM_NODES.get(node_type, {})
```

**Sources:** [src/backend/bisheng/custom/customs.py:4-53]()

---

## Component Loading Flow

The following diagram illustrates the complete flow from a component request to instantiation:

```mermaid
graph TB
    subgraph "1. Request"
        REQ["API Request<br/>or Workflow Builder"]
        TYPE_NAME["type: 'embeddings'<br/>name: 'OpenAIProxyEmbedding'"]
    end
    
    subgraph "2. Import Dispatcher"
        IMPORT_BY_TYPE["import_by_type(type, name)"]
        FUNC_LOOKUP["func_dict lookup"]
        TYPE_FUNC["import_embedding()"]
    end
    
    subgraph "3. Creator Lookup"
        CREATOR["embedding_creator"]
        LOADER_DICT["type_to_loader_dict"]
        CLASS_REF["OpenAIProxyEmbedding class"]
    end
    
    subgraph "4. Component Instantiation"
        INIT["__init__(**kwargs)"]
        LLM_SVC["LLMService.get_knowledge_default_embedding()"]
        DELEGATE["Delegate to actual embedding"]
    end
    
    subgraph "5. Usage"
        EMBED_DOCS["embed_documents(texts)"]
        EMBED_QUERY["embed_query(text)"]
        VECTOR_STORE["Store in Milvus"]
    end
    
    REQ --> TYPE_NAME
    TYPE_NAME --> IMPORT_BY_TYPE
    IMPORT_BY_TYPE --> FUNC_LOOKUP
    FUNC_LOOKUP -->|"'embeddings'"| TYPE_FUNC
    
    TYPE_FUNC --> CREATOR
    CREATOR --> LOADER_DICT
    LOADER_DICT --> CLASS_REF
    
    CLASS_REF --> INIT
    INIT -->|"OpenAIProxyEmbedding"| LLM_SVC
    LLM_SVC --> DELEGATE
    
    DELEGATE --> EMBED_DOCS
    DELEGATE --> EMBED_QUERY
    EMBED_DOCS --> VECTOR_STORE
    EMBED_QUERY --> VECTOR_STORE
```

**Sources:** [src/backend/bisheng/interface/importing/utils.py:31-67](), [src/backend/bisheng/interface/embeddings/custom.py:12-31]()

---

## Configuration and Streaming Options

The system provides utilities for managing component behavior at runtime.

### Streaming Configuration

The `try_setting_streaming_options()` function configures streaming behavior for LLM components:

```python
def try_setting_streaming_options(langchain_object, websocket):
    # Find the LLM instance in the langchain object
    llm = None
    if hasattr(langchain_object, 'llm'):
        llm = langchain_object.llm
    elif hasattr(langchain_object, 'llm_chain') and hasattr(langchain_object.llm_chain, 'llm'):
        llm = langchain_object.llm_chain.llm

    if isinstance(llm, BaseLanguageModel):
        if hasattr(llm, 'streaming') and isinstance(llm.streaming, bool):
            llm.streaming = settings.get_from_db('llm_request').get('stream') \
                if 'stream' in settings.get_from_db('llm_request') \
                else ChatConfig.streaming
        elif hasattr(llm, 'stream') and isinstance(llm.stream, bool):
            llm.stream = settings.get_from_db('llm_request').get('stream') \
                if 'stream' in settings.get_from_db('llm_request') \
                else ChatConfig.streaming
    return langchain_object
```

This function:
1. Locates the LLM instance within composite objects (chains, agents)
2. Checks for streaming attributes (`streaming` or `stream`)
3. Applies streaming configuration from database settings or defaults

**Sources:** [src/backend/bisheng/interface/utils.py:38-57]()

### File Loading Utilities

The `load_file_into_dict()` function provides flexible configuration file loading:

```python
def load_file_into_dict(file_path: str) -> dict:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f'File not found: {file_path}')

    with open(file_path, 'r') as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            file.seek(0)
            data = yaml.safe_load(file)
        except ValueError as exc:
            raise ValueError('Invalid file type. Expected .json or .yaml.') from exc
    return data
```

This supports loading component configurations from both JSON and YAML formats.

**Sources:** [src/backend/bisheng/interface/utils.py:15-28]()

---

## Component Type Summary Table

| Component Type | Primary Registry | Creator Class | Import Function | Example Usage |
|----------------|------------------|---------------|-----------------|---------------|
| **LLMs** | `llm_type_to_cls_dict` | `LLMCreator` | `import_chat_llm()` | Chat models, completion models |
| **Embeddings** | `embedding_type_to_cls_dict` | `embedding_creator` | `import_embedding()` | Text vectorization, semantic search |
| **Agents** | Dynamic import | `agent_creator` | `import_agent()` | ReAct agents, function calling |
| **Chains** | `chain_creator` | `ChainCreator` | `import_chain()` | Sequential processing, QA chains |
| **Tools** | `tool_creator` | `ToolCreator` | `import_tool()` | API calls, Python functions |
| **Memories** | `memory_type_to_cls_dict` | `memory_creator` | `import_memory()` | Chat history, context management |
| **Vector Stores** | `vectorstore_creator` | `VectorstoreCreator` | `import_vectorstore()` | Milvus, Elasticsearch clients |
| **Document Loaders** | `documentloaders_type_to_cls_dict` | `documentloader_creator` | `import_documentloader()` | PDF, text, web loaders |
| **Text Splitters** | `textsplitter_type_to_cls_dict` | `textsplitter_creator` | `import_textsplitter()` | Character, recursive splitters |
| **Output Parsers** | `output_parser_creator` | `OutputParserCreator` | `import_output_parser()` | JSON, structured output |

**Sources:** [src/backend/bisheng/interface/custom_lists.py](), [src/backend/bisheng/interface/importing/utils.py]()

---

## Integration Points

### With Workflow Engine

The workflow engine uses `import_by_type()` to instantiate nodes dynamically based on node configurations. See [Workflow Engine](#3.5) for details on how components are used in graph execution.

### With LLMService

The `LLMService` manages LLM and embedding model lifecycle, using the component registry to instantiate models based on system configuration. The `OpenAIProxyEmbedding` class demonstrates tight integration with `LLMService`.

### With Frontend

Frontend nodes are generated using the creator pattern's `get_signature()` method, which introspects component classes to generate UI templates with appropriate input fields, validation rules, and default values.

**Sources:** [src/backend/bisheng/interface/llms/base.py:28-37](), [src/backend/bisheng/interface/embeddings/custom.py:15-18]()

---

# Page: User and Access Control

# User and Access Control

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/backend/bisheng/api/services/audit_log.py](src/backend/bisheng/api/services/audit_log.py)
- [src/backend/bisheng/api/services/role_group_service.py](src/backend/bisheng/api/services/role_group_service.py)
- [src/backend/bisheng/api/v1/audit.py](src/backend/bisheng/api/v1/audit.py)
- [src/backend/bisheng/api/v1/usergroup.py](src/backend/bisheng/api/v1/usergroup.py)
- [src/backend/bisheng/database/models/audit_log.py](src/backend/bisheng/database/models/audit_log.py)
- [src/backend/bisheng/database/models/group.py](src/backend/bisheng/database/models/group.py)
- [src/backend/bisheng/database/models/group_resource.py](src/backend/bisheng/database/models/group_resource.py)
- [src/backend/bisheng/database/models/role.py](src/backend/bisheng/database/models/role.py)
- [src/backend/bisheng/database/models/role_access.py](src/backend/bisheng/database/models/role_access.py)
- [src/backend/bisheng/database/models/session.py](src/backend/bisheng/database/models/session.py)
- [src/backend/bisheng/database/models/user_group.py](src/backend/bisheng/database/models/user_group.py)
- [src/backend/bisheng/user/domain/models/user_role.py](src/backend/bisheng/user/domain/models/user_role.py)

</details>



This document describes Bisheng's multi-tenant authorization system, including user groups, role-based access control (RBAC), resource permissions, group administration, and comprehensive audit logging. For system configuration settings, see [Configuration Management](#5.1). For deployment considerations, see [Docker Deployment](#5.2).

## Overview

Bisheng implements a sophisticated two-layer permission model:
1. **Group-based access**: Users belong to Groups, and resources (flows, knowledge bases, assistants, tools, workflows, dashboards) are owned by groups
2. **Role-based access control (RBAC)**: Fine-grained permissions via group-specific roles

Every operation is logged via `AuditLogService` with comprehensive metadata including operator, timestamp, affected resources, and associated groups.

Sources: [src/backend/bisheng/api/services/role_group_service.py:1-396](), [src/backend/bisheng/api/services/audit_log.py:1-161]()

## System Architecture

```mermaid
graph TB
    subgraph "User Layer"
        USER["User"]
        ADMIN["System Administrator<br/>(AdminRole=1)"]
        GROUP_ADMIN["Group Administrator<br/>(is_group_admin=True)"]
    end
    
    subgraph "Group Layer"
        DEFAULT_GROUP["DefaultGroup<br/>(ID=2)"]
        CUSTOM_GROUP["Custom Groups"]
        USER_GROUP["UserGroup Table<br/>user_id + group_id"]
    end
    
    subgraph "Role Layer"
        ROLE["Role Table<br/>group-specific roles"]
        USER_ROLE["UserRole Table<br/>user_id + role_id"]
        ROLE_ACCESS["RoleAccess Table<br/>role_id + third_id + type"]
    end
    
    subgraph "Resource Layer"
        RESOURCES["Resources:<br/>Flow, Knowledge, Assistant,<br/>Tool, Workflow, Dashboard"]
        GROUP_RESOURCE["GroupResource Table<br/>group_id + third_id + type"]
    end
    
    subgraph "Audit Layer"
        AUDIT_LOG["AuditLog Table<br/>operator, group_ids, event_type,<br/>object_type, ip_address"]
    end
    
    USER --> USER_GROUP
    GROUP_ADMIN --> USER_GROUP
    ADMIN -.system-wide access.-> RESOURCES
    
    USER_GROUP --> DEFAULT_GROUP
    USER_GROUP --> CUSTOM_GROUP
    
    USER --> USER_ROLE
    USER_ROLE --> ROLE
    ROLE --> ROLE_ACCESS
    
    CUSTOM_GROUP --> GROUP_RESOURCE
    DEFAULT_GROUP --> GROUP_RESOURCE
    GROUP_RESOURCE --> RESOURCES
    
    ROLE_ACCESS -.grants access to.-> RESOURCES
    
    USER --> AUDIT_LOG
    GROUP_ADMIN --> AUDIT_LOG
    ADMIN --> AUDIT_LOG
```

**Authorization Architecture**

The system provides three levels of access control:
- **System Administrators** (`AdminRole=1`): Full system access, can manage all groups and resources
- **Group Administrators** (`is_group_admin=True`): Manage users, roles, and resources within their groups
- **Regular Users**: Access resources based on group membership and assigned roles

Sources: [src/backend/bisheng/database/models/user_group.py:12-36](), [src/backend/bisheng/database/models/role.py:14-41](), [src/backend/bisheng/database/models/group_resource.py:12-47](), [src/backend/bisheng/database/constants.py:1-10]()

## User Groups

### Group Model

The `Group` table defines user groups with the following structure:

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Primary key (ID=2 is DefaultGroup) |
| `group_name` | str | Unique display name |
| `remark` | str | Optional description |
| `create_user` | int | User ID who created the group |
| `update_user` | int | User ID who last updated the group |
| `create_time` | datetime | Creation timestamp |
| `update_time` | datetime | Last update timestamp |

Sources: [src/backend/bisheng/database/models/group.py:14-28]()

### DefaultGroup Concept

`DefaultGroup` (ID=2) serves as a fallback for orphaned resources. When a group is deleted, resources that belong only to that group are automatically moved to `DefaultGroup` to prevent data loss.

```python
# src/backend/bisheng/database/models/group.py:11
DefaultGroup = 2
```

Sources: [src/backend/bisheng/database/models/group.py:10-11](), [src/backend/bisheng/api/services/role_group_service.py:116-130]()

### UserGroup Relationship

The `UserGroup` table manages user-group membership:

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | int | Foreign key to user.user_id |
| `group_id` | int | Foreign key to group.id |
| `is_group_admin` | bool | Whether user is group administrator |
| `remark` | str | Optional notes |
| `create_time` | datetime | When user joined group |
| `update_time` | datetime | Last update timestamp |

Key methods in `UserGroupDao`:
- `get_user_group(user_id)`: Get groups where user is a member (not admin)
- `get_user_admin_group(user_id)`: Get groups where user is administrator
- `insert_user_group_admin(user_id, group_id)`: Set user as group admin
- `add_default_user_group(user_id)`: Add user to DefaultGroup

Sources: [src/backend/bisheng/database/models/user_group.py:12-115]()

### Group Management Service

`RoleGroupService` provides high-level operations:

```mermaid
graph LR
    API["API Endpoints<br/>/group/*"]
    SERVICE["RoleGroupService"]
    GROUP_DAO["GroupDao"]
    USER_GROUP_DAO["UserGroupDao"]
    AUDIT["AuditLogService"]
    
    API --> SERVICE
    SERVICE --> GROUP_DAO
    SERVICE --> USER_GROUP_DAO
    SERVICE --> AUDIT
    
    SERVICE --> |"create_group_hook()"| AUDIT
    SERVICE --> |"update_group_hook()"| AUDIT
    SERVICE --> |"delete_group_hook()"| AUDIT
```

**Group Management Flow**

Key operations:
- `create_group(request, login_user, group)`: Create new group with optional admins
- `update_group(request, login_user, group)`: Update group name/description
- `delete_group(request, login_user, group_id)`: Delete group after validation
- `set_group_admin(request, login_user, user_ids, group_id)`: Set group administrators
- `replace_user_groups(request, login_user, user_id, group_ids)`: Update user's group memberships

When a group is deleted, the system:
1. Checks if any users remain in the group (prevents deletion if users exist)
2. Moves orphaned resources to `DefaultGroup`
3. Deletes all roles associated with the group
4. Removes all group administrators
5. Publishes a Redis event for cache invalidation

Sources: [src/backend/bisheng/api/services/role_group_service.py:32-243](), [src/backend/bisheng/api/v1/usergroup.py:16-186]()

## Resource Ownership

### GroupResource Model

The `GroupResource` table links resources to groups:

| Field | Type | Description |
|-------|------|-------------|
| `group_id` | str | Foreign key to group.id |
| `third_id` | str | Resource identifier (flow_id, knowledge_id, etc.) |
| `type` | int | ResourceTypeEnum value |
| `create_time` | datetime | Creation timestamp |
| `update_time` | datetime | Last update timestamp |

### ResourceTypeEnum

```python
class ResourceTypeEnum(Enum):
    KNOWLEDGE = 1        # Knowledge bases
    FLOW = 2            # Skills/Flows
    ASSISTANT = 3       # Assistants
    GPTS_TOOL = 4       # Tools
    WORK_FLOW = 5       # Workflows
    DASHBOARD = 6       # Dashboards
    WORKSTATION = 7     # Workstation sessions
```

Sources: [src/backend/bisheng/database/models/group_resource.py:12-20]()

### Resource Access Methods

`GroupResourceDao` provides:
- `get_group_resource(group_id, resource_type)`: Get resources in a group
- `get_resource_group(resource_type, third_id)`: Get groups owning a resource
- `insert_group_batch(group_resources)`: Add multiple resource-group associations
- `delete_group_resource_by_third_id(third_id, resource_type)`: Remove resource associations

Resources can belong to multiple groups simultaneously. The `group_ids` field in session tracking and audit logs stores all associated groups.

Sources: [src/backend/bisheng/database/models/group_resource.py:49-181]()

## Role-Based Access Control

### Role Model

Roles are group-specific and provide fine-grained permissions:

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Primary key (ID=1 is AdminRole) |
| `role_name` | str | Display name (unique within group) |
| `group_id` | int | Foreign key to group.id |
| `remark` | str | Optional description |
| `create_time` | datetime | Creation timestamp |
| `update_time` | datetime | Last update timestamp |

The `AdminRole` (ID=1) is a special system-wide role for super administrators.

Sources: [src/backend/bisheng/database/models/role.py:14-41](), [src/backend/bisheng/database/constants.py:1-10]()

### UserRole Relationship

The `UserRole` table assigns roles to users:

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | int | Foreign key to user.user_id |
| `role_id` | int | Foreign key to role.id |
| `create_time` | datetime | Assignment timestamp |
| `update_time` | datetime | Last update timestamp |

Key methods:
- `get_user_roles(user_id)`: Get all roles assigned to user
- `set_admin_user(user_id)`: Assign AdminRole to user
- `add_user_roles(user_id, role_ids)`: Bulk assign roles
- `delete_user_roles(user_id, role_ids)`: Remove role assignments

Sources: [src/backend/bisheng/user/domain/models/user_role.py:13-110]()

### RoleAccess Model

The `RoleAccess` table defines what resources a role can access:

| Field | Type | Description |
|-------|------|-------------|
| `role_id` | int | Foreign key to role.id |
| `third_id` | str | Resource identifier or menu name |
| `type` | int | AccessType value |
| `create_time` | datetime | Creation timestamp |
| `update_time` | datetime | Last update timestamp |

### AccessType Enumeration

```python
class AccessType(Enum):
    KNOWLEDGE = 1              # Knowledge base read
    FLOW = 2                   # Skill read
    KNOWLEDGE_WRITE = 3        # Knowledge base write
    FLOW_WRITE = 4             # Skill write
    ASSISTANT_READ = 5         # Assistant read
    ASSISTANT_WRITE = 6        # Assistant write
    GPTS_TOOL_READ = 7         # Tool read
    GPTS_TOOL_WRITE = 8        # Tool write
    WORKFLOW = 9               # Workflow read
    WORKFLOW_WRITE = 10        # Workflow write
    DASHBOARD = 11             # Dashboard read
    DASHBOARD_WRITE = 12       # Dashboard write
    WEB_MENU = 99              # Frontend menu restrictions
```

### WebMenuResource

Frontend menu permissions are controlled via:

```python
class WebMenuResource(Enum):
    BUILD = 'build'                    # Build menu
    KNOWLEDGE = 'knowledge'            # Knowledge menu
    MODEL = 'model'                    # Model menu
    EVALUATION = 'evaluation'          # Evaluation menu
    FRONTEND = 'frontend'              # Frontend permissions
    BACKEND = 'backend'                # Backend access
    CREATE_DASHBOARD = 'create_dashboard'  # Dashboard creation
```

Sources: [src/backend/bisheng/database/models/role_access.py:13-67]()

### Permission Checking

```mermaid
sequenceDiagram
    participant User
    participant UserPayload
    participant UserRoleDao
    participant RoleAccessDao
    participant GroupResourceDao
    
    User->>UserPayload: get_login_user()
    UserPayload->>UserPayload: check if is_admin()
    
    alt System Admin
        UserPayload-->>User: Full access granted
    else Regular User
        UserPayload->>UserRoleDao: get_user_roles(user_id)
        UserRoleDao-->>UserPayload: role_ids
        
        UserPayload->>RoleAccessDao: judge_role_access(role_ids, resource_id, access_type)
        RoleAccessDao-->>UserPayload: access_granted?
        
        alt No role access
            UserPayload->>GroupResourceDao: get_resource_group(resource_type, resource_id)
            GroupResourceDao-->>UserPayload: group_ids
            
            UserPayload->>UserPayload: check_group_admin(group_ids)
            UserPayload-->>User: Access based on group admin status
        else Has role access
            UserPayload-->>User: Access granted
        end
    end
```

**Permission Verification Flow**

The permission check follows this hierarchy:
1. **System Admin Check**: If user has `AdminRole`, grant full access
2. **Role-Based Check**: Query `RoleAccess` for specific resource permissions
3. **Group Admin Check**: If no role access, check if user is group administrator
4. **Group Membership Check**: Verify user belongs to resource's groups

Sources: [src/backend/bisheng/database/models/role_access.py:74-169](), [src/backend/bisheng/api/services/role_group_service.py:161-208]()

## Group Administration

### Admin Permissions

Group administrators (`is_group_admin=True`) can:
- View and manage users within their groups
- Create and manage roles within their groups
- View and manage resources (flows, knowledge bases, assistants, etc.) within their groups
- View audit logs for their groups
- Modify user group memberships (limited to their managed groups)

System administrators (`AdminRole`) can:
- Perform all group administrator operations across all groups
- Create and delete groups
- Set group administrators
- Access system-wide audit logs

Sources: [src/backend/bisheng/api/services/role_group_service.py:161-180](), [src/backend/bisheng/api/v1/usergroup.py:19-38]()

### Admin Restrictions

Certain operations are restricted to protect system integrity:

1. **DefaultGroup Protection**: The default group (ID=2) cannot be deleted
2. **Admin User Protection**: Users with `AdminRole` cannot have their group memberships modified by group administrators
3. **Group Deletion Restriction**: Groups cannot be deleted if they contain users

```python
# Prevent admin user modification
if any(one.role_id == AdminRole for one in user_role_list):
    raise AdminUserUpdateForbiddenError()
```

Sources: [src/backend/bisheng/api/services/role_group_service.py:96-99](), [src/backend/bisheng/api/services/role_group_service.py:163-166]()

### Resource Management API

The `/group/get_group_resources` endpoint retrieves resources for a group:

```mermaid
graph LR
    API["/group/get_group_resources"]
    CHECK["UserPayload.check_group_admin()"]
    SERVICE["RoleGroupService.get_group_resources()"]
    
    FLOW["get_group_flow()"]
    KNOWLEDGE["get_group_knowledge()"]
    ASSISTANT["get_group_assistant()"]
    TOOL["get_group_tool()"]
    DASHBOARD["get_group_dashboards()"]
    
    API --> CHECK
    CHECK --> |authorized| SERVICE
    CHECK --> |unauthorized| ERROR["UnAuthorizedError"]
    
    SERVICE --> FLOW
    SERVICE --> KNOWLEDGE
    SERVICE --> ASSISTANT
    SERVICE --> TOOL
    SERVICE --> DASHBOARD
```

**Group Resource Retrieval**

Each resource type has a dedicated retrieval method:
- `get_group_flow()`: Skills and workflows with pagination
- `get_group_knowledge()`: Knowledge bases with user info
- `get_group_assistant()`: Assistants with simplified info
- `get_group_tool()`: Tools with user mapping
- `get_group_dashboards()`: Dashboards with layout excluded

Sources: [src/backend/bisheng/api/v1/usergroup.py:126-150](), [src/backend/bisheng/api/services/role_group_service.py:249-375]()

## Audit Logging

### AuditLog Model

The `AuditLog` table tracks all system operations:

| Field | Type | Description |
|-------|------|-------------|
| `id` | str | UUID primary key |
| `operator_id` | int | User who performed action |
| `operator_name` | str | Username |
| `group_ids` | List[int] | Associated groups |
| `system_id` | str | SystemId enum value |
| `event_type` | str | EventType enum value |
| `object_type` | str | ObjectType enum value |
| `object_id` | str | Resource identifier |
| `object_name` | str | Resource name |
| `note` | str | Optional notes |
| `ip_address` | str | Client IP address |
| `create_time` | datetime | Action timestamp |

Sources: [src/backend/bisheng/database/models/audit_log.py:72-92]()

### System Modules (SystemId)

```python
class SystemId(Enum):
    CHAT = "chat"            # Chat sessions
    BUILD = "build"          # Build/development
    KNOWLEDGE = "knowledge"  # Knowledge bases
    SYSTEM = "system"        # System administration
    DASHBOARD = "dashboard"  # Dashboards
```

Sources: [src/backend/bisheng/database/models/audit_log.py:13-19]()

### Event Types (EventType)

| Event | Description |
|-------|-------------|
| `CREATE_CHAT` | New chat session |
| `DELETE_CHAT` | Delete chat session |
| `CREATE_BUILD` | New application (flow/assistant/workflow) |
| `UPDATE_BUILD` | Edit application |
| `DELETE_BUILD` | Delete application |
| `CREATE_KNOWLEDGE` | New knowledge base |
| `DELETE_KNOWLEDGE` | Delete knowledge base |
| `UPLOAD_FILE` | Upload file to knowledge base |
| `DELETE_FILE` | Delete file from knowledge base |
| `UPDATE_USER` | Edit user account/groups/roles |
| `FORBID_USER` | Disable user account |
| `RECOVER_USER` | Enable user account |
| `CREATE_USER_GROUP` | Create user group |
| `UPDATE_USER_GROUP` | Edit user group |
| `DELETE_USER_GROUP` | Delete user group |
| `CREATE_ROLE` | Create role |
| `UPDATE_ROLE` | Edit role |
| `DELETE_ROLE` | Delete role |
| `ADD_TOOL` | Add tool |
| `UPDATE_TOOL` | Edit tool |
| `DELETE_TOOL` | Delete tool |
| `USER_LOGIN` | User login |
| `CREATE_DASHBOARD` | Create dashboard |
| `UPDATE_DASHBOARD` | Edit dashboard |
| `DELETE_DASHBOARD` | Delete dashboard |

Sources: [src/backend/bisheng/database/models/audit_log.py:22-54]()

### Object Types (ObjectType)

```python
class ObjectType(Enum):
    NONE = "none"                    # No specific object
    FLOW = "flow"                    # Skill
    WORK_FLOW = "work_flow"          # Workflow
    ASSISTANT = "assistant"          # Assistant
    WORKSTATION = "workstation"      # Workstation session
    KNOWLEDGE = "knowledge"          # Knowledge base
    FILE = "file"                    # Document
    USER_CONF = "user_conf"          # User configuration
    USER_GROUP_CONF = "user_group_conf"  # User group config
    ROLE_CONF = "role_conf"          # Role configuration
    TOOL = "tool"                    # Tool
    DASHBOARD = "dashboard"          # Dashboard
```

Sources: [src/backend/bisheng/database/models/audit_log.py:57-70]()

### Audit Service Methods

```mermaid
graph TB
    subgraph "Chat Events"
        CREATE_CHAT_ASSISTANT["create_chat_assistant()"]
        CREATE_CHAT_FLOW["create_chat_flow()"]
        DELETE_CHAT_FLOW["delete_chat_flow()"]
    end
    
    subgraph "Build Events"
        CREATE_BUILD_FLOW["create_build_flow()"]
        UPDATE_BUILD_FLOW["update_build_flow()"]
        DELETE_BUILD_FLOW["delete_build_flow()"]
        CREATE_BUILD_ASSISTANT["create_build_assistant()"]
    end
    
    subgraph "Knowledge Events"
        CREATE_KNOWLEDGE["create_knowledge()"]
        DELETE_KNOWLEDGE["delete_knowledge()"]
        UPLOAD_FILE["upload_knowledge_file()"]
        DELETE_FILE["delete_knowledge_file()"]
    end
    
    subgraph "System Events"
        UPDATE_USER["update_user()"]
        FORBID_USER["forbid_user()"]
        CREATE_GROUP["create_user_group()"]
        CREATE_ROLE["create_role()"]
        USER_LOGIN["user_login()"]
    end
    
    subgraph "Dashboard Events"
        CREATE_DASHBOARD["create_dashboard()"]
        UPDATE_DASHBOARD["update_dashboard()"]
        DELETE_DASHBOARD["delete_dashboard()"]
    end
    
    ALL["AuditLogDao.insert_audit_logs()"]
    
    CREATE_CHAT_ASSISTANT --> ALL
    CREATE_BUILD_FLOW --> ALL
    CREATE_KNOWLEDGE --> ALL
    UPDATE_USER --> ALL
    CREATE_DASHBOARD --> ALL
```

**Audit Logging Methods**

Each audit method follows a pattern:
1. Retrieve resource details (name, ID)
2. Determine associated groups via `GroupResourceDao` or user groups
3. Create `AuditLog` object with metadata
4. Insert via `AuditLogDao.insert_audit_logs()` or `ainsert_audit_logs()`

Sources: [src/backend/bisheng/api/services/audit_log.py:34-552]()

### Group-Scoped Audit Queries

Audit logs can be filtered by group membership:

```python
# Filter logs by user-managed groups
if not login_user.is_admin():
    groups = [one.group_id for one in UserGroupDao.get_user_admin_group(user_id)]
    # Only show logs for managed groups
    
# Query with group filter
data, total = await AuditLogDao.get_audit_logs(
    groups, operator_ids, start_time, end_time,
    system_id, event_type, page, limit
)
```

The `group_ids` field in audit logs uses JSON storage and supports `json_contains()` queries to find logs associated with specific groups.

Sources: [src/backend/bisheng/api/services/audit_log.py:36-56](), [src/backend/bisheng/database/models/audit_log.py:102-136]()

## Session Group Tracking

### MessageSession Model

Chat sessions track group associations via the `group_ids` field:

```python
class MessageSessionBase(SQLModelSerializable):
    chat_id: str              # Session unique ID
    flow_id: str              # Application ID
    flow_type: int            # App type (skill/assistant/workflow)
    user_id: int              # Session creator
    group_ids: List[int]      # Associated groups (JSON column)
    sensitive_status: int     # Review status
    create_time: datetime
```

When creating a session, the system automatically populates `group_ids` from the user's group memberships:

```python
if not data.group_ids:
    user_groups = UserGroupDao.get_user_group(data.user_id)
    data.group_ids = [ug.group_id for ug in user_groups]
```

This enables group administrators to view sessions from users in their groups.

Sources: [src/backend/bisheng/database/models/session.py:18-43](), [src/backend/bisheng/database/models/session.py:47-72]()

### Session List Filtering

The `/audit/session` endpoint filters sessions by group:

```python
# For regular users, limit to managed groups
if not user.is_admin():
    user_managed_groups = await UserGroupDao.aget_user_admin_group(user.user_id)
    managed_group_ids = {one.group_id for one in user_managed_groups}
    
    # Intersect with requested groups
    if group_ids:
        valid_group_ids = list(set(group_ids) & managed_group_ids)
    else:
        valid_group_ids = list(managed_group_ids)

# Query sessions using JSON contains
group_filters = [
    func.json_contains(MessageSession.group_ids, str(gid))
    for gid in search_group_ids
]
```

Sources: [src/backend/bisheng/api/services/audit_log.py:600-675]()

## API Endpoints

### User Group Endpoints

| Method | Path | Description | Permission |
|--------|------|-------------|------------|
| GET | `/group/list` | List all groups | Group admin or system admin |
| POST | `/group/create` | Create new group | System admin |
| PUT | `/group/create` | Update group | System admin |
| DELETE | `/group/create` | Delete group | System admin |
| POST | `/group/set_user_group` | Set user's groups | Group admin or system admin |
| GET | `/group/get_user_group` | Get user's groups | Authenticated user |
| GET | `/group/get_group_user` | Get group members | Authenticated user |
| POST | `/group/set_group_admin` | Set group admins | System admin |
| GET | `/group/get_group_resources` | Get group resources | Group admin |
| GET | `/group/roles` | Get group roles | Group admin |
| GET | `/group/manage/resources` | Get managed resources | Group admin |

Sources: [src/backend/bisheng/api/v1/usergroup.py:16-186]()

### Audit Log Endpoints

| Method | Path | Description | Permission |
|--------|------|-------------|------------|
| GET | `/audit` | Query audit logs | Group admin or system admin |
| GET | `/audit/operators` | Get all operators | Group admin or system admin |
| GET | `/audit/session` | Get session list | Group admin or system admin |
| GET | `/audit/session/export` | Export sessions to CSV | Group admin or system admin |
| GET | `/audit/session/export/data` | Export session data | Group admin or system admin |

Sources: [src/backend/bisheng/api/v1/audit.py:10-99]()

## Data Model Relationships

```mermaid
erDiagram
    User ||--o{ UserGroup : belongs_to
    User ||--o{ UserRole : has
    Group ||--o{ UserGroup : contains
    Group ||--o{ Role : defines
    Group ||--o{ GroupResource : owns
    Role ||--o{ UserRole : assigned_to
    Role ||--o{ RoleAccess : grants
    Resource ||--o{ GroupResource : belongs_to
    Resource ||--o{ RoleAccess : accessible_via
    User ||--o{ AuditLog : creates
    Group ||--o{ AuditLog : scopes
    
    User {
        int user_id PK
        string user_name
        string password
        datetime create_time
    }
    
    Group {
        int id PK
        string group_name
        int create_user FK
        datetime create_time
    }
    
    UserGroup {
        int user_id PK,FK
        int group_id PK,FK
        bool is_group_admin
        datetime create_time
    }
    
    Role {
        int id PK
        string role_name
        int group_id FK
        datetime create_time
    }
    
    UserRole {
        int id PK
        int user_id FK
        int role_id FK
        datetime create_time
    }
    
    GroupResource {
        int id PK
        string group_id FK
        string third_id
        int type
        datetime create_time
    }
    
    RoleAccess {
        int id PK
        int role_id FK
        string third_id
        int type
        datetime create_time
    }
    
    Resource {
        string id PK
        string name
        int type
    }
    
    AuditLog {
        string id PK
        int operator_id FK
        json group_ids
        string system_id
        string event_type
        string object_type
        string object_id
        datetime create_time
    }
```

**Entity Relationship Diagram**

Key relationships:
- Users belong to multiple Groups via `UserGroup`
- Users have multiple Roles via `UserRole`
- Groups own Resources via `GroupResource`
- Roles grant access to Resources via `RoleAccess`
- All operations logged in `AuditLog` with group associations

Sources: [src/backend/bisheng/database/models/user_group.py:12-36](), [src/backend/bisheng/database/models/group.py:14-28](), [src/backend/bisheng/database/models/role.py:14-27](), [src/backend/bisheng/database/models/user_role.py:13-33](), [src/backend/bisheng/database/models/group_resource.py:21-33](), [src/backend/bisheng/database/models/role_access.py:13-24](), [src/backend/bisheng/database/models/audit_log.py:72-92]()

## Permission Verification Examples

### Checking Group Admin Status

```python
# UserPayload method
def check_group_admin(self, group_id: int) -> bool:
    """Check if user is admin of specific group"""
    if self.is_admin():
        return True
    
    admin_groups = UserGroupDao.get_user_admin_group(self.user_id)
    return group_id in [ug.group_id for ug in admin_groups]
```

### Checking Resource Access

```python
# Example: Verify user can access a flow
user_roles = UserRoleDao.get_user_roles(user_id)
role_ids = [ur.role_id for ur in user_roles]

# Check if user has read permission for this flow
access = RoleAccessDao.judge_role_access(
    role_ids, 
    flow_id, 
    AccessType.FLOW
)

if not access:
    # Check group membership as fallback
    resource_groups = GroupResourceDao.get_resource_group(
        ResourceTypeEnum.FLOW, 
        flow_id
    )
    user_groups = UserGroupDao.get_user_group(user_id)
    
    # User must belong to at least one resource group
    has_access = any(
        rg.group_id in [ug.group_id for ug in user_groups]
        for rg in resource_groups
    )
```

Sources: [src/backend/bisheng/database/models/role_access.py:112-130](), [src/backend/bisheng/database/models/group_resource.py:119-127]()

### Filtering Resources by Permission

```python
# Get resources user can manage
async def get_manage_resources(login_user, keyword, page, page_size):
    """Get resources in user's managed groups"""
    groups = []
    
    if not login_user.is_admin():
        # Get groups where user is admin
        user_groups = await UserGroupDao.aget_user_admin_group(login_user.user_id)
        groups = [str(one.group_id) for one in user_groups]
        
        if not groups:
            return [], 0
    
    # Get resources in those groups
    if groups:
        group_resources = await GroupResourceDao.get_groups_resource(
            groups,
            resource_types=[
                ResourceTypeEnum.FLOW,
                ResourceTypeEnum.ASSISTANT,
                ResourceTypeEnum.WORK_FLOW
            ]
        )
        resource_ids = [one.third_id for one in group_resources]
    
    return await FlowDao.aget_all_apps(keyword, id_list=resource_ids, page=page, limit=page_size)
```

Sources: [src/backend/bisheng/api/services/role_group_service.py:377-396]()

## Security Considerations

### Admin User Protection

The system prevents modification of super administrator accounts:

```python
# Check if operating on admin user
user_role_list = UserRoleDao.get_user_roles(user_id)
if any(one.role_id == AdminRole for one in user_role_list):
    raise AdminUserUpdateForbiddenError()
```

Sources: [src/backend/bisheng/api/services/role_group_service.py:163-166](), [src/backend/bisheng/common/errcode/user.py:1-50]()

### Group Deletion Safety

Before deleting a group:
1. Verify no users remain in the group
2. Move orphaned resources to `DefaultGroup`
3. Clean up associated roles and permissions
4. Publish Redis event for distributed cache invalidation

Sources: [src/backend/bisheng/api/services/role_group_service.py:96-140]()

### IP Address Logging

All audit logs capture the client's IP address via `get_request_ip(request)`:

```python
def get_request_ip(request: Request) -> str:
    """Extract client IP from request headers or connection"""
    # Check X-Forwarded-For header first
    # Fall back to X-Real-IP
    # Finally use client connection info
```

This enables security auditing and forensic analysis.

Sources: [src/backend/bisheng/api/services/audit_log.py:73-115](), [src/backend/bisheng/utils.py:1-500]()

---

# Page: Development and Deployment

# Development and Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.drone.yml](.drone.yml)
- [.github/workflows/base_ci.yml](.github/workflows/base_ci.yml)
- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [.github/workflows/release.yml](.github/workflows/release.yml)
- [.pre-commit-config.yaml](.pre-commit-config.yaml)
- [docker/bisheng-ft/config.yaml](docker/bisheng-ft/config.yaml)
- [docker/bisheng-uns/config.yaml](docker/bisheng-uns/config.yaml)
- [docker/docker-compose-ft.yml](docker/docker-compose-ft.yml)
- [docker/docker-compose-office.yml](docker/docker-compose-office.yml)
- [docker/docker-compose-uns.yml](docker/docker-compose-uns.yml)
- [docker/docker-compose.yml](docker/docker-compose.yml)
- [docker/mysql/conf/my.cnf](docker/mysql/conf/my.cnf)
- [docker/nginx/nginx.conf](docker/nginx/nginx.conf)
- [src/backend/Dockerfile](src/backend/Dockerfile)
- [src/backend/base.Dockerfile](src/backend/base.Dockerfile)
- [src/backend/bisheng/.gitignore](src/backend/bisheng/.gitignore)
- [src/backend/bisheng/__init__.py](src/backend/bisheng/__init__.py)
- [src/backend/bisheng/api/services/chat_imp.py](src/backend/bisheng/api/services/chat_imp.py)
- [src/backend/bisheng/core/ai/rerank/xinference/__init__.py](src/backend/bisheng/core/ai/rerank/xinference/__init__.py)
- [src/backend/bisheng/core/ai/rerank/xinference/_compat.py](src/backend/bisheng/core/ai/rerank/xinference/_compat.py)
- [src/backend/bisheng/core/ai/rerank/xinference/client/__init__.py](src/backend/bisheng/core/ai/rerank/xinference/client/__init__.py)
- [src/backend/bisheng/core/ai/rerank/xinference/client/common.py](src/backend/bisheng/core/ai/rerank/xinference/client/common.py)
- [src/backend/bisheng/core/ai/rerank/xinference/client/handlers.py](src/backend/bisheng/core/ai/rerank/xinference/client/handlers.py)
- [src/backend/bisheng/core/ai/rerank/xinference/client/restful/__init__.py](src/backend/bisheng/core/ai/rerank/xinference/client/restful/__init__.py)
- [src/backend/bisheng/core/ai/rerank/xinference/client/restful/async_restful_client.py](src/backend/bisheng/core/ai/rerank/xinference/client/restful/async_restful_client.py)
- [src/backend/bisheng/core/ai/rerank/xinference/client/restful/restful_client.py](src/backend/bisheng/core/ai/rerank/xinference/client/restful/restful_client.py)
- [src/backend/bisheng/core/ai/rerank/xinference/fields.py](src/backend/bisheng/core/ai/rerank/xinference/fields.py)
- [src/backend/bisheng/interface/initialize/vector_store.py](src/backend/bisheng/interface/initialize/vector_store.py)
- [src/backend/bisheng/processing/base.py](src/backend/bisheng/processing/base.py)
- [src/backend/bisheng/processing/process.py](src/backend/bisheng/processing/process.py)
- [src/backend/bisheng/services/session/service.py](src/backend/bisheng/services/session/service.py)
- [src/backend/bisheng/template/frontend_node/embeddings.py](src/backend/bisheng/template/frontend_node/embeddings.py)
- [src/backend/bisheng/template/frontend_node/llms.py](src/backend/bisheng/template/frontend_node/llms.py)
- [src/backend/bisheng/template/frontend_node/vectorstores.py](src/backend/bisheng/template/frontend_node/vectorstores.py)
- [src/backend/bisheng/template/frontend_node/wrappers.py](src/backend/bisheng/template/frontend_node/wrappers.py)
- [src/backend/pyproject.toml](src/backend/pyproject.toml)
- [src/backend/test/test_filelib.py](src/backend/test/test_filelib.py)
- [update.sh](update.sh)

</details>



This page provides an overview of the development, deployment, and release management processes for the Bisheng platform. The system uses a containerized architecture with multi-stage CI/CD pipelines supporting both AMD64 and ARM64 architectures.

**Key Topics**:
- **Configuration Management** (page 5.1): Two-tier configuration system with `initdb_config.yaml` for business logic and `config.yaml` for infrastructure
- **Docker Deployment** (page 5.2): Docker Compose orchestration with 10+ microservices including MySQL, Redis, Milvus, Elasticsearch, and MinIO
- **CI/CD Pipeline** (page 5.3): GitHub Actions workflows for automated multi-architecture builds, manifest creation, and registry synchronization

## System Overview

The Bisheng platform follows a modern cloud-native architecture with clear separation between development, deployment, and operations concerns. The system is packaged as Docker containers and deployed via Docker Compose, with automated CI/CD pipelines handling multi-architecture builds.

### Technology Stack

The backend is built using Python 3.10+ with dependency management via `pyproject.toml`. Key technology categories:

| Category | Key Dependencies | Version |
|----------|------------------|---------|
| Web Framework | `fastapi`, `uvicorn` | >=0.120.4, >=0.38.0 |
| AI/ML Libraries | `langchain`, `langgraph`, `openai`, `transformers` | 0.3.x, 0.3.x, 1.68.2, 4.57.1 |
| Database | `sqlmodel`, `pymysql`, `aiomysql`, `alembic` | >=0.0.27, >=1.1.2, >=0.3.2, >=1.17.1 |
| Vector Storage | `pymilvus`, `langchain-milvus` | 2.5.10, 0.2.1 |
| Search | `langchain-elasticsearch` | >=0.4.0 |
| Task Queue | `celery`, `redis` | >=5.5.3, >=7.0.1 |
| Object Storage | `minio`, `miniopy-async` | 7.2.18, >=1.23.4 |

The project version is defined as `2.3.0-beta2` in [src/backend/pyproject.toml:3]() and synchronized across [src/backend/bisheng/__init__.py:10]() and [docker/docker-compose.yml:43]().

### Deployment Architecture Layers

```mermaid
graph TB
    subgraph "Layer 1: External Access"
        Users["External Users"]
        GH["GitHub Actions<br/>CI/CD"]
    end
    
    subgraph "Layer 2: Frontend"
        Frontend["bisheng-frontend:3001<br/>nginx + React SPA"]
    end
    
    subgraph "Layer 3: API Gateway"
        Nginx["Nginx Reverse Proxy"]
    end
    
    subgraph "Layer 4: Backend Services"
        Backend["bisheng-backend:7860<br/>FastAPI uvicorn"]
        Worker["bisheng-backend-worker<br/>Celery Workers"]
    end
    
    subgraph "Layer 5: Data Persistence"
        MySQL["MySQL 8.0<br/>bisheng DB"]
        Redis["Redis 7.0.4<br/>Cache & Queue"]
        ES["Elasticsearch 8.12.0<br/>Full-text Index"]
        Milvus["Milvus 2.5.10<br/>Vector Store"]
        MinIO["MinIO<br/>Object Storage"]
    end
    
    subgraph "Layer 6: Support Services"
        Etcd["etcd 3.5.5<br/>Milvus Metadata"]
        Office["OnlyOffice 7.1.1<br/>Document Server"]
        UNS["bisheng-unstructured:10001<br/>Parser Service"]
        FT["bisheng-ft:8000<br/>Fine-tuning"]
    end
    
    Users --> Frontend
    GH --> Frontend
    GH --> Backend
    Frontend --> Nginx
    Nginx --> Backend
    Backend --> MySQL
    Backend --> Redis
    Backend --> ES
    Backend --> Milvus
    Backend --> MinIO
    Backend --> Office
    Backend --> UNS
    Worker --> MySQL
    Worker --> Redis
    Worker --> Milvus
    Worker --> MinIO
    Worker --> FT
    Milvus --> Etcd
    Milvus --> MinIO
```

**Sources**: [src/backend/pyproject.toml:1-85](), [docker/docker-compose.yml:1-201](), [src/backend/bisheng/__init__.py:10]()

## Configuration System

Bisheng uses a two-tier configuration system separating business logic from infrastructure configuration. See page 5.1 for complete details.

### Configuration Files

| File | Purpose | Key Settings |
|------|---------|--------------|
| `initdb_config.yaml` | Business logic configuration | Knowledge base ETL, LLM timeouts, password policies, workflow settings, Linsight parameters |
| `config.yaml` | Infrastructure configuration | Database URLs, Redis connections, Celery queues, vector stores, object storage, logging |

### Configuration Loading Flow

```mermaid
graph LR
    subgraph "Initialization"
        Init["Application Startup<br/>bisheng.main"]
        LoadConfig["load_config()"]
    end
    
    subgraph "Configuration Sources"
        EnvVars["Environment Variables<br/>BS_* prefix"]
        ConfigYAML["config.yaml<br/>Infrastructure"]
        InitDBYAML["initdb_config.yaml<br/>Business Logic"]
        Database["Config Table<br/>MySQL"]
    end
    
    subgraph "Processing"
        EnvInterpolation["Environment Variable<br/>Interpolation<br/>!env ${VAR}"]
        Encryption["Password Decryption<br/>encrypt() function"]
        RedisCache["Redis Cache<br/>config:initdb_config"]
    end
    
    subgraph "Runtime Access"
        Settings["bisheng_settings<br/>Singleton"]
        ConfigDao["ConfigDao<br/>Database Access"]
        APIs["API Endpoints<br/>/config, /env"]
    end
    
    Init --> LoadConfig
    LoadConfig --> ConfigYAML
    LoadConfig --> InitDBYAML
    LoadConfig --> Database
    EnvVars --> EnvInterpolation
    ConfigYAML --> EnvInterpolation
    EnvInterpolation --> Encryption
    Encryption --> RedisCache
    InitDBYAML --> Database
    Database --> RedisCache
    RedisCache --> Settings
    Settings --> APIs
    Database --> ConfigDao
    ConfigDao --> APIs
```

Key configuration endpoints in [src/backend/bisheng/api/v1/endpoints.py:102-156]():
- `GET /config`: Retrieves `initdb_config.yaml` content (admin only)
- `POST /config/save`: Updates and validates configuration (admin only)
- `GET /env`: Returns frontend environment settings
- `GET /web/config`: Retrieves web-specific configuration
- `POST /web/config`: Updates web configuration (admin only)

**Sources**: [src/backend/bisheng/initdb_config.yaml:1-81](), [docker/bisheng/config/config.yaml:1-87](), [src/backend/bisheng/api/v1/endpoints.py:102-156]()

## Docker Deployment

The platform is deployed using Docker Compose with separate service definitions for core components and optional services. See page 5.2 for complete deployment details.

### Core Services (docker-compose.yml)

The main compose file [docker/docker-compose.yml:1-201]() defines:

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| `mysql` | `mysql:8.0` | 3306 | Primary database with `bisheng` schema |
| `redis` | `redis:7.0.4` | 6379 | Cache and Celery broker |
| `backend` | `dataelement/bisheng-backend:v2.3.0-beta2` | 7860 | FastAPI application server |
| `backend_worker` | `dataelement/bisheng-backend:v2.3.0-beta2` | - | Celery async workers |
| `frontend` | `dataelement/bisheng-frontend:v2.3.0-beta2` | 3001 | Nginx + React SPA |
| `elasticsearch` | `bitnamilegacy/elasticsearch:8.12.0` | 9200, 9300 | Full-text search engine |
| `etcd` | `quay.io/coreos/etcd:v3.5.5` | 2379 | Milvus metadata store |
| `minio` | `minio/minio:RELEASE.2023-03-20T20-16-18Z` | 9100, 9101 | Object storage for files and vectors |
| `milvus` | `milvusdb/milvus:v2.5.10` | 19530, 9091 | Vector database |

### Optional Services

Additional compose files for specialized features:
- **Document Processing**: `docker-compose-uns.yml` - Unstructured service with OCR capabilities
- **Model Fine-tuning**: `docker-compose-ft.yml` - GPU-enabled fine-tuning server
- **Document Editing**: `docker-compose-office.yml` - OnlyOffice document server

### Service Startup Modes

The backend container supports two startup modes via `entrypoint.sh`:

```bash
# API mode - FastAPI server
command: sh entrypoint.sh api

# Worker mode - Celery + Linsight workers  
command: sh entrypoint.sh worker
```

The worker mode starts three types of workers:
1. **Knowledge Celery Worker**: Queue `knowledge_celery`, 20 threads for file processing
2. **Workflow Celery Worker**: Queue `workflow_celery`, 100 threads for workflow execution
3. **Linsight Worker**: 4 processes with 5 max concurrency for SOP tasks

**Sources**: [docker/docker-compose.yml:1-201](), [docker/docker-compose-uns.yml:1-22](), [docker/docker-compose-ft.yml:1-31](), [docker/docker-compose-office.yml:1-15]()

## CI/CD Pipeline

Bisheng uses GitHub Actions for automated build, test, and deployment. The CI/CD system supports multi-architecture builds (AMD64/ARM64) with separate workflows for pre-release and production releases. See page 5.3 for complete pipeline details.

### Build Pipeline Architecture

```mermaid
graph TB
    subgraph "Trigger: Git Tag Push"
        TagPush["git push --tags v*"]
    end
    
    subgraph "CI Workflow (.github/workflows/ci.yml)"
        BuildBackendAMD["build_bisheng_backend<br/>ubuntu-latest<br/>linux/amd64"]
        BuildBackendARM["build_backend_arm<br/>ubuntu-22.04-arm<br/>linux/arm64<br/>Remove ibm-db"]
        BuildFrontendAMD["build_bisheng_frontend<br/>ubuntu-latest<br/>linux/amd64"]
        BuildFrontendARM["build_frontend_arm<br/>ubuntu-22.04-arm<br/>linux/arm64"]
        NotifyFeishu1["notify_feishu<br/>Pre-release notification"]
    end
    
    subgraph "Docker Hub"
        BackendAMD["bisheng-backend:VERSION-amd64"]
        BackendARM["bisheng-backend:VERSION-arm64"]
        FrontendAMD["bisheng-frontend:VERSION-amd64"]
        FrontendARM["bisheng-frontend:VERSION-arm64"]
    end
    
    subgraph "Release Workflow (.github/workflows/release.yml)"
        Trigger["Trigger: GitHub Release Published"]
        CombineImages["combine_publish_images<br/>Create multi-arch manifests"]
        SyncRegistry["sync_dataelem_repos<br/>Sync to cr.dataelem.com"]
        TestPull["test_pull_images<br/>Verify availability"]
        NotifyFeishu2["notify_feishu<br/>Release notification"]
    end
    
    TagPush --> BuildBackendAMD
    TagPush --> BuildBackendARM
    TagPush --> BuildFrontendAMD
    TagPush --> BuildFrontendARM
    
    BuildBackendAMD --> BackendAMD
    BuildBackendARM --> BackendARM
    BuildFrontendAMD --> FrontendAMD
    BuildFrontendARM --> FrontendARM
    
    BackendAMD --> NotifyFeishu1
    BackendARM --> NotifyFeishu1
    FrontendAMD --> NotifyFeishu1
    FrontendARM --> NotifyFeishu1
    
    Trigger --> CombineImages
    CombineImages --> SyncRegistry
    SyncRegistry --> TestPull
    TestPull --> NotifyFeishu2
```

### CI Workflow (Pre-release)

Triggered on git tag push matching pattern `v*` [.github/workflows/ci.yml:4-7]():

1. **Build AMD64 Images**: Uses `ubuntu-latest` runners with Docker Buildx [.github/workflows/ci.yml:18-55]()
2. **Build ARM64 Images**: Uses `ubuntu-22.04-arm` runners, removes `ibm-db` dependency for ARM compatibility [.github/workflows/ci.yml:56-96]()
3. **Push to Docker Hub**: Tags images with `-amd64` or `-arm64` suffix
4. **Notification**: Sends build status to Feishu webhook [.github/workflows/ci.yml:161-188]()

### Release Workflow (Production)

Triggered when a GitHub Release is published [.github/workflows/release.yml:4-6]():

1. **Combine Images**: Creates multi-arch manifests combining AMD64 and ARM64 images [.github/workflows/release.yml:38-51]()
2. **Sync to Private Registry**: Pulls from Docker Hub and pushes to `cr.dataelem.com` [.github/workflows/release.yml:53-101]()
3. **Test Availability**: Validates images can be pulled from both registries [.github/workflows/release.yml:103-140]()
4. **Release Notification**: Sends completion status to Feishu [.github/workflows/release.yml:142-166]()

### Version Management

Version updates are synchronized across the codebase using [update.sh:1-8]():
- `docker/docker-compose.yml`: Service image tags
- `src/backend/pyproject.toml`: Package version
- `src/backend/bisheng/__init__.py`: Module version constant

**Sources**: [.github/workflows/ci.yml:1-188](), [.github/workflows/release.yml:1-166](), [update.sh:1-8]()

## Environment Variable Interpolation

The configuration system supports environment variable substitution using the `!env` YAML tag, enabling dynamic configuration without hardcoding sensitive values.

### Environment Variable Pattern

Configuration in [docker/bisheng/config/config.yaml:33-56]() uses environment variables for infrastructure settings:

```yaml
vector_stores:
  milvus:
    connection_args: !env ${BS_MILVUS_CONNECTION_ARGS}
    is_partition: !env ${BS_MILVUS_IS_PARTITION}
    partition_suffix: !env ${BS_MILVUS_PARTITION_SUFFIX}
  elasticsearch:
    url: !env ${BS_ELASTICSEARCH_URL}
    ssl_verify: !env ${BS_ELASTICSEARCH_SSL_VERIFY}

object_storage:
  minio:
    schema: !env ${BS_MINIO_SCHEMA}
    endpoint: !env ${BS_MINIO_ENDPOINT}
    access_key: !env ${BS_MINIO_ACCESS_KEY}
    secret_key: !env ${BS_MINIO_SECRET_KEY}
```

These environment variables are set in [docker/docker-compose.yml:46-58]() for the backend service:

```yaml
environment:
  BS_MILVUS_CONNECTION_ARGS: '{"host":"milvus","port":"19530",...}'
  BS_ELASTICSEARCH_URL: 'http://elasticsearch:9200'
  BS_MINIO_ENDPOINT: 'minio:9000'
  BS_MINIO_ACCESS_KEY: 'minioadmin'
  BS_MINIO_SECRET_KEY: 'minioadmin'
```

This pattern allows the same configuration file to work across different deployment environments by changing only environment variables.

**Sources**: [docker/bisheng/config/config.yaml:33-56](), [docker/docker-compose.yml:46-58]()

## Service Dependencies and Health Checks

The Docker Compose deployment enforces startup order through dependency declarations and health checks to ensure services are ready before dependent services start.

### Dependency Chain

```mermaid
graph TB
    subgraph "Foundation Layer"
        MySQL["mysql<br/>Health: mysql connection"]
        Redis["redis<br/>Health: redis-cli ping"]
        Etcd["etcd<br/>Health: etcdctl endpoint health"]
        MinIO["minio<br/>Health: curl minio/health/live"]
    end
    
    subgraph "Storage Layer"
        Milvus["milvus<br/>Depends: etcd, minio<br/>Health: curl :9091/healthz"]
        ES["elasticsearch<br/>No health check"]
    end
    
    subgraph "Application Layer"
        Backend["backend<br/>Depends: mysql, redis<br/>Health: curl :7860/health"]
        Worker["backend_worker<br/>Depends: mysql, redis<br/>No health check"]
    end
    
    subgraph "Presentation Layer"
        Frontend["frontend<br/>Depends: backend<br/>No health check"]
    end
    
    MySQL --> Backend
    MySQL --> Worker
    Redis --> Backend
    Redis --> Worker
    Etcd --> Milvus
    MinIO --> Milvus
    Backend --> Frontend
```

### Health Check Configuration

Health checks are defined in [docker/docker-compose.yml:15-72]():

| Service | Test Command | Interval | Timeout | Retries |
|---------|--------------|----------|---------|---------|
| `mysql` | `mysql -u root -p$MYSQL_ROOT_PASSWORD` | 20s | 10s | 4 |
| `redis` | `redis-cli ping \| grep -e "PONG\|NOAUTH"` | 10s | 5s | 3 |
| `backend` | `curl -f http://localhost:7860/health` | 90s | 30s | 3 |
| `milvus` | `curl -f http://localhost:9091/healthz` | 30s | 20s | 3 |
| `etcd` | `etcdctl endpoint health` | 30s | 20s | 3 |
| `minio` | `curl -f http://localhost:9000/minio/health/live` | 30s | 20s | 3 |

The backend health check endpoint is implemented in the FastAPI application and verifies basic service availability.

**Sources**: [docker/docker-compose.yml:15-72](), [docker/docker-compose.yml:73-107]()

## Version Management and Updates

The platform uses a centralized version management system to ensure consistency across all components.

### Version Update Process

The version update script [update.sh:1-8]() synchronizes version numbers across:
- Docker Compose configuration: `./docker/docker-compose.yml`
- Python package configuration: `./src/backend/pyproject.toml`
- Python package module: `./src/backend/bisheng/__init__.py`

Current platform version is defined as `2.0.3` in [src/backend/bisheng/__init__.py:9]().

### Container Image Versioning

All Docker images follow the same versioning scheme:
- Backend: `dataelement/bisheng-backend:v2.0.3`
- Frontend: `dataelement/bisheng-frontend:v2.0.3`
- Unstructured: `dataelement/bisheng-unstructured:v0.0.3.14`
- Fine-tuning: `dataelement/bisheng-ft:v0.2.0`

**Sources**: [update.sh:1-8](), [src/backend/bisheng/__init__.py:9](), [docker/docker-compose.yml:56-128]()

---

# Page: Configuration Management

# Configuration Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docker/bisheng-ft/config.yaml](docker/bisheng-ft/config.yaml)
- [docker/bisheng-uns/config.yaml](docker/bisheng-uns/config.yaml)
- [docker/bisheng/config/config.yaml](docker/bisheng/config/config.yaml)
- [docker/docker-compose-ft.yml](docker/docker-compose-ft.yml)
- [docker/docker-compose-office.yml](docker/docker-compose-office.yml)
- [docker/docker-compose-uns.yml](docker/docker-compose-uns.yml)
- [docker/docker-compose.yml](docker/docker-compose.yml)
- [docker/mysql/conf/my.cnf](docker/mysql/conf/my.cnf)
- [docker/nginx/nginx.conf](docker/nginx/nginx.conf)
- [src/backend/bisheng/__init__.py](src/backend/bisheng/__init__.py)
- [src/backend/bisheng/api/utils.py](src/backend/bisheng/api/utils.py)
- [src/backend/bisheng/api/v1/endpoints.py](src/backend/bisheng/api/v1/endpoints.py)
- [src/backend/bisheng/database/base.py](src/backend/bisheng/database/base.py)
- [src/backend/bisheng/graph/vertex/base.py](src/backend/bisheng/graph/vertex/base.py)
- [src/backend/bisheng/initdb_config.yaml](src/backend/bisheng/initdb_config.yaml)
- [src/backend/bisheng/interface/chains/base.py](src/backend/bisheng/interface/chains/base.py)
- [src/backend/bisheng/interface/chains/custom.py](src/backend/bisheng/interface/chains/custom.py)
- [src/backend/bisheng/interface/initialize/loading.py](src/backend/bisheng/interface/initialize/loading.py)
- [src/backend/bisheng/main.py](src/backend/bisheng/main.py)
- [src/backend/bisheng/template/frontend_node/chains.py](src/backend/bisheng/template/frontend_node/chains.py)
- [src/backend/bisheng/template/frontend_node/wrappers.py](src/backend/bisheng/template/frontend_node/wrappers.py)
- [src/backend/pyproject.toml](src/backend/pyproject.toml)
- [update.sh](update.sh)

</details>



## Purpose and Scope

This document explains Bisheng's configuration system, which manages settings across deployment environments and runtime operations. The platform uses a multi-layered configuration architecture consisting of database-stored settings (`initdb_config.yaml`), deployment configurations (`config.yaml`), and environment variables. 

For information about Docker deployment orchestration, see [Docker Deployment](#5.2). For CI/CD configuration management, see [CI/CD Pipeline](#5.3).

## Configuration Architecture

Bisheng's configuration system operates in three distinct layers that work together to provide flexible deployment and runtime parameter management:

```mermaid
graph TB
    subgraph "Configuration Sources"
        INITDB["initdb_config.yaml<br/>(Database-Stored Settings)"]
        CONFIG["config.yaml<br/>(Deployment Config)"]
        ENV["Environment Variables<br/>(BS_* prefixed)"]
    end
    
    subgraph "Loading & Parsing"
        YAML_PARSE["YAML Parser<br/>yaml.safe_load()"]
        ENV_RESOLVER["Environment Resolver<br/>!env ${VAR} syntax"]
        ENCRYPT["Encryption Handler<br/>gAAAAAB... decryption"]
    end
    
    subgraph "Storage Layer"
        MYSQL_CONFIG[("MySQL<br/>config table<br/>ConfigDao")]
        REDIS_CACHE[("Redis Cache<br/>config:initdb_config")]
    end
    
    subgraph "Runtime Access"
        SETTINGS["config_service.settings<br/>Global Settings Object"]
        DAO["ConfigDao<br/>Database Operations"]
        API["Config API Endpoints<br/>/config, /web/config"]
    end
    
    subgraph "Application Components"
        KNOWLEDGE["Knowledge Service<br/>ETL4LM settings"]
        LLM["LLM Service<br/>request_timeout, max_retries"]
        AUTH["Auth System<br/>password_conf, login_method"]
        WORKFLOW["Workflow Engine<br/>max_steps, timeout"]
        LINSIGHT["Linsight Workers<br/>tool_buffer, max_steps"]
    end
    
    INITDB --> YAML_PARSE
    CONFIG --> YAML_PARSE
    CONFIG --> ENV_RESOLVER
    ENV --> ENV_RESOLVER
    
    YAML_PARSE --> ENCRYPT
    ENV_RESOLVER --> ENCRYPT
    ENCRYPT --> MYSQL_CONFIG
    
    MYSQL_CONFIG --> DAO
    DAO --> REDIS_CACHE
    
    REDIS_CACHE --> SETTINGS
    DAO --> SETTINGS
    SETTINGS --> API
    
    SETTINGS --> KNOWLEDGE
    SETTINGS --> LLM
    SETTINGS --> AUTH
    SETTINGS --> WORKFLOW
    SETTINGS --> LINSIGHT
    
    API --> MYSQL_CONFIG
```

**Configuration Flow:**

1. **Source Loading**: Configuration files are parsed during application startup
2. **Environment Resolution**: Variables marked with `!env ${VAR}` are replaced with environment values
3. **Encryption Handling**: Encrypted strings (e.g., database passwords) are decrypted using Fernet
4. **Database Storage**: `initdb_config.yaml` contents are stored in the `config` table via `ConfigDao`
5. **Redis Caching**: Frequently accessed settings are cached with key `config:initdb_config`
6. **Runtime Access**: Components access settings through the global `settings` object or `ConfigDao`

Sources: [src/backend/bisheng/initdb_config.yaml:1-81](), [docker/bisheng/config/config.yaml:1-88](), [src/backend/bisheng/api/v1/endpoints.py:101-129]()

---

## Database-Stored Configuration (initdb_config.yaml)

The `initdb_config.yaml` file contains business logic settings that can be modified at runtime through the admin API. These settings are stored in the database and cached in Redis for performance.

### Configuration Structure

```mermaid
graph LR
    subgraph "initdb_config.yaml Sections"
        KNOWLEDGE["knowledges<br/>etl4lm.url<br/>etl4lm.timeout<br/>etl4lm.ocr_sdk_url"]
        LLM_REQ["llm_request<br/>request_timeout: 600<br/>max_retries: 1"]
        OPERATOR["default_operator<br/>user: 1<br/>enable_guest_access"]
        PASSWORD["password_conf<br/>password_valid_period<br/>login_error_time_window<br/>max_error_times"]
        LOGIN["system_login_method<br/>allow_multi_login<br/>gateway_login<br/>admin_username"]
        ENV["env<br/>office_url<br/>show_github_and_help<br/>enable_registration<br/>uploaded_files_maximum_size"]
        WORKFLOW["workflow<br/>max_steps: 50<br/>timeout: 5"]
        LINSIGHT["linsight<br/>tool_buffer: 100000<br/>max_steps: 200<br/>retry_num: 3<br/>retry_sleep: 5"]
        CAPTCHA["use_captcha: True"]
        TIPS["dialog_tips<br/>Chat window prompt"]
    end
```

### Knowledge Base Configuration

| Key | Type | Description | Default |
|-----|------|-------------|---------|
| `knowledges.etl4lm.url` | string | ETL4LM document parsing service endpoint | `""` |
| `knowledges.etl4lm.timeout` | int | Request timeout in seconds | `600` |
| `knowledges.etl4lm.ocr_sdk_url` | string | High-precision OCR SDK URL (optional) | `""` |

When `etl4lm.url` is configured, the system enables image format support (png, jpg, jpeg, bmp) for document processing.

Sources: [src/backend/bisheng/initdb_config.yaml:1-8](), [src/backend/bisheng/api/v1/endpoints.py:77-80]()

### LLM Request Configuration

The `llm_request` section controls timeout behavior for LLM component invocations:

```yaml
llm_request:
  request_timeout: 600  # seconds
  max_retries: 1
```

These settings are applied at runtime when instantiating LLM components:

- **Applied in**: `instantiate_llm()` function
- **Code path**: [src/backend/bisheng/interface/initialize/loading.py:253-291]()
- **Runtime access**: `settings.get_from_db('llm_request')`

The system checks if the LLM instance has `request_timeout` and `max_retries` attributes and sets them accordingly.

Sources: [src/backend/bisheng/initdb_config.yaml:9-12](), [src/backend/bisheng/interface/initialize/loading.py:281-289]()

### Default Operator Configuration

| Key | Type | Description |
|-----|------|-------------|
| `default_operator.user` | int | User ID for guest/anonymous operations |
| `default_operator.enable_guest_access` | bool | Enable guest link access |

Guest access links allow unauthenticated users to access flows and assistants. Operations are logged under the configured user ID.

Sources: [src/backend/bisheng/initdb_config.yaml:14-17]()

### Password Security Configuration

```yaml
password_conf:
  password_valid_period: 200       # Days until password expires
  login_error_time_window: 5       # Minutes
  max_error_times: 0               # 0 = disabled
```

**Password Expiration Logic:**
- If `password_valid_period > 0`: Users must change passwords after N days
- On login, system checks `last_password_change` against validity period
- User is prompted to reset if expired

**Account Lockout Logic:**
- Requires both `password_valid_period > 0` and `login_error_time_window > 0`
- If failed login attempts exceed `max_error_times` within the time window, account is locked
- `max_error_times = 0` disables lockout

Sources: [src/backend/bisheng/initdb_config.yaml:19-26]()

### System Login Method

| Key | Type | Description |
|-----|------|-------------|
| `system_login_method.allow_multi_login` | bool | Allow concurrent sessions per user |
| `system_login_method.gateway_login` | bool | Enable SSO/gateway authentication |
| `system_login_method.admin_username` | string | Default admin username for SSO/LDAP |

Sources: [src/backend/bisheng/initdb_config.yaml:28-33]()

### Environment Settings

The `env` section contains frontend-facing configuration:

```yaml
env:
  office_url: http://IP:8701              # OnlyOffice integration endpoint
  show_github_and_help: true              # Display help links in UI
  enable_registration: true               # Allow new user registration
  uploaded_files_maximum_size: 50        # MB limit for file uploads
```

These settings are exposed via the `/env` API endpoint and consumed by the frontend.

Sources: [src/backend/bisheng/initdb_config.yaml:42-53](), [src/backend/bisheng/api/v1/endpoints.py:71-98]()

### Workflow Configuration

```yaml
workflow:
  max_steps: 50        # Maximum node execution steps per workflow
  timeout: 5           # Minutes to wait for user input
```

The `max_steps` setting prevents infinite loops in workflow graphs. The `timeout` applies to nodes that require user interaction.

Sources: [src/backend/bisheng/initdb_config.yaml:55-59]()

### Linsight Configuration

The `linsight` section controls advanced workflow execution parameters:

| Key | Type | Description | Default |
|-----|------|-------------|---------|
| `tool_buffer` | int | Max tokens for tool messages before summarization | 100000 |
| `max_steps` | int | Maximum task execution steps | 200 |
| `retry_num` | int | Model call retry attempts | 3 |
| `retry_sleep` | int | Seconds between retries | 5 |
| `max_file_num` | int | User files in SOP prompt | 5 |
| `max_knowledge_num` | int | Knowledge bases in SOP prompt | 20 |
| `file_content_length` | int | Characters to read from files | 5000 |
| `default_temperature` | float | Model temperature | 0 |
| `retry_temperature` | float | Temperature for JSON retry | 1 |

Sources: [src/backend/bisheng/initdb_config.yaml:61-81]()

---

## Deployment Configuration (config.yaml)

The `config.yaml` file contains infrastructure and deployment settings. It is mounted into containers at `/app/bisheng/config.yaml` and should not be modified at runtime.

### Configuration Entity Mapping

```mermaid
graph TB
    subgraph "config.yaml Structure"
        DB["database_url<br/>MySQL connection"]
        REDIS_MAIN["redis_url<br/>Main cache"]
        REDIS_CELERY["celery_redis_url<br/>Task broker"]
        CELERY_TASK["celery_task<br/>task_routers"]
        VECTOR["vector_stores<br/>milvus, elasticsearch"]
        STORAGE["object_storage<br/>minio settings"]
        ENV_CONF["environment<br/>env, uns_support"]
        LOGGER["logger_conf<br/>handlers, level, format"]
    end
    
    subgraph "Code Entities"
        SETTINGS["config_service.settings"]
        DB_SESSION["database.py<br/>get_db_session()"]
        REDIS_MGR["redis_manager.py<br/>get_redis_client_sync()"]
        CELERY_APP["worker/__init__.py<br/>Celery app"]
        MILVUS_INIT["vecstore_initializer"]
        MINIO_CLIENT["MinioClient"]
        LOGURU["loguru.logger"]
    end
    
    DB --> DB_SESSION
    REDIS_MAIN --> REDIS_MGR
    REDIS_CELERY --> CELERY_APP
    CELERY_TASK --> CELERY_APP
    VECTOR --> MILVUS_INIT
    STORAGE --> MINIO_CLIENT
    LOGGER --> LOGURU
    
    SETTINGS --> DB_SESSION
    SETTINGS --> REDIS_MGR
    SETTINGS --> CELERY_APP
    SETTINGS --> MILVUS_INIT
    SETTINGS --> MINIO_CLIENT
    SETTINGS --> LOGURU
```

### Database Configuration

The `database_url` specifies the MySQL connection string with encrypted password support:

```yaml
database_url: "mysql+pymysql://root:gAAAAABlp4b4c59...@mysql:3306/bisheng?charset=utf8mb4"
```

**Encryption Format:**
- Password is encrypted using Fernet encryption
- Format: `gAAAAAB<encrypted_base64_string>`
- Decryption is handled automatically by the settings loader
- To encrypt a password, use the Bisheng encryption utility (see documentation link in config file)

**Connection String Components:**
- **Driver**: `mysql+pymysql` (SQLModel/SQLAlchemy driver)
- **Host**: `mysql` (Docker service name)
- **Port**: `3306`
- **Database**: `bisheng`
- **Charset**: `utf8mb4` (full Unicode support)

Sources: [docker/bisheng/config/config.yaml:1-4]()

### Redis Configuration

Bisheng supports three Redis deployment modes:

**1. Standalone Mode (Default):**
```yaml
redis_url: "redis://redis:6379/1"
celery_redis_url: "redis://redis:6379/2"
```

**2. Cluster Mode:**
```yaml
redis_url:
  mode: "cluster"
  startup_nodes:
    - {"host": "192.168.106.115", "port": 6002}
  password: encrypt(gAAAAAB...)
```

**3. Sentinel Mode:**
```yaml
redis_url:
  mode: "sentinel"
  sentinel_hosts: [("redis", 6379)]
  sentinel_master: "mymaster"
  sentinel_password: encrypt(gAAAAAB...)
  db: 1
```

**Redis Database Allocation:**
- **DB 1**: Main cache (sessions, temporary data)
- **DB 2**: Celery broker (task queue)
- **DB 5**: Fine-tuning service (optional)

Sources: [docker/bisheng/config/config.yaml:6-23]()

### Celery Task Configuration

The `celery_task` section defines task routing for different worker types:

```yaml
celery_task:
  task_routers:
    bisheng.worker.knowledge.*:      # Knowledge file processing
      queue: knowledge_celery
    bisheng.worker.workflow.*:       # Workflow execution
      queue: workflow_celery
```

**Important:** Workflow tasks must execute in a single process to maintain state consistency. Do not distribute workflow tasks across multiple worker instances.

Sources: [docker/bisheng/config/config.yaml:24-32]()

### Vector Store Configuration

Vector store settings use environment variable resolution with the `!env` directive:

```yaml
vector_stores:
  milvus:
    connection_args: !env ${BS_MILVUS_CONNECTION_ARGS}
    is_partition: !env ${BS_MILVUS_IS_PARTITION}
    partition_suffix: !env ${BS_MILVUS_PARTITION_SUFFIX}
  elasticsearch:
    url: !env ${BS_ELASTICSEARCH_URL}
    ssl_verify: !env ${BS_ELASTICSEARCH_SSL_VERIFY}
```

**Environment Variable Format (Docker Compose):**
```yaml
BS_MILVUS_CONNECTION_ARGS: '{"host":"milvus","port":"19530","user":"","password":"","secure":false}'
BS_MILVUS_IS_PARTITION: 'true'
BS_MILVUS_PARTITION_SUFFIX: '1'
BS_ELASTICSEARCH_URL: 'http://elasticsearch:9200'
BS_ELASTICSEARCH_SSL_VERIFY: '{}'  # or '{"basic_auth": ("elastic", "elastic")}'
```

**Runtime Access:**
- Code path: [src/backend/bisheng/interface/initialize/loading.py:485-549]()
- Function: `instantiate_vectorstore()`
- Settings access: `settings.vector_stores.milvus`, `settings.vector_stores.elasticsearch`

Sources: [docker/bisheng/config/config.yaml:34-42](), [docker/docker-compose.yml:48-52]()

### Object Storage Configuration

MinIO configuration for file persistence:

```yaml
object_storage:
  type: minio
  minio:
    schema: !env ${BS_MINIO_SCHEMA}          # http or https
    cert_check: !env ${BS_MINIO_CERT_CHECK}  # SSL verification
    endpoint: !env ${BS_MINIO_ENDPOINT}      # Service endpoint
    sharepoint: !env ${BS_MINIO_SHAREPOINT}  # Public URL
    access_key: !env ${BS_MINIO_ACCESS_KEY}
    secret_key: !env ${BS_MINIO_SECRET_KEY}
    public_bucket: 'bisheng'                 # Persistent files
    tmp_bucket: 'tmp-dir'                    # Temporary files with TTL
```

**Bucket Usage:**
- **bisheng**: Public bucket for platform assets (icons, workflow files, dashboards)
- **tmp-dir**: Temporary storage with lifecycle policies

Sources: [docker/bisheng/config/config.yaml:45-56]()

### Logger Configuration

Loguru-based logging with multiple handlers:

```yaml
logger_conf:
  level: DEBUG  # Console output level
  format: '<level>[{time:YYYY-MM-DD HH:mm:ss.SSSSSS}] [{level.name} process-{process.id}-{thread.id} {name}:{line}]</level> - <level>trace={extra[trace_id]} {message}</level>'
  handlers:
    - sink: "/app/data/bisheng.log"
      level: INFO
      rotation: "00:00"
      retention: "3 Days"
      enqueue: true
    - sink: "/app/data/statistic.log"
      level: INFO
      filter: "lambda record: record['level'].name == 'INFO' and record['message'].startswith('k=s')"
      rotation: "00:00"
      retention: "3 Days"
```

**Handler Types:**
1. **General log**: All INFO+ messages
2. **Statistic log**: Filtered messages matching specific patterns

**Filter Syntax:**
- Filters are Python lambda expressions evaluated at runtime
- Support `record['level']`, `record['message']`, etc.

Sources: [docker/bisheng/config/config.yaml:62-88]()

---

## Environment Variables

Environment variables provide Docker-specific overrides and are resolved at container startup using the `!env ${VAR}` syntax in `config.yaml`.

### Standard Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `BS_MILVUS_CONNECTION_ARGS` | Milvus connection JSON | `{"host":"milvus","port":"19530"}` |
| `BS_MILVUS_IS_PARTITION` | Enable Milvus partitioning | `"true"` |
| `BS_MILVUS_PARTITION_SUFFIX` | Partition suffix for multi-tenancy | `"1"` |
| `BS_ELASTICSEARCH_URL` | Elasticsearch endpoint | `http://elasticsearch:9200` |
| `BS_ELASTICSEARCH_SSL_VERIFY` | ES authentication | `{}` or `{"basic_auth":(...)}` |
| `BS_MINIO_SCHEMA` | HTTP scheme | `"false"` (http) / `"true"` (https) |
| `BS_MINIO_CERT_CHECK` | SSL certificate verification | `"false"` / `"true"` |
| `BS_MINIO_ENDPOINT` | MinIO internal endpoint | `minio:9000` |
| `BS_MINIO_SHAREPOINT` | MinIO public URL | `minio:9000` |
| `BS_MINIO_ACCESS_KEY` | MinIO access key | `minioadmin` |
| `BS_MINIO_SECRET_KEY` | MinIO secret key | `minioadmin` |

### Docker Compose Integration

Environment variables are defined in the `backend` and `backend_worker` services:

```yaml
services:
  backend:
    environment:
      TZ: Asia/Shanghai
      BS_MILVUS_CONNECTION_ARGS: '{"host":"milvus","port":"19530",...}'
      BS_ELASTICSEARCH_URL: 'http://elasticsearch:9200'
      BS_MINIO_ENDPOINT: 'minio:9000'
      # ... other variables
```

The same variables must be set for both the API and worker containers to ensure consistent configuration.

Sources: [docker/docker-compose.yml:46-59](), [docker/docker-compose.yml:82-94]()

---

## Configuration Management APIs

Bisheng provides REST APIs for runtime configuration management, accessible only to administrators.

### Configuration API Endpoints

```mermaid
sequenceDiagram
    participant Admin
    participant API as "/config endpoints"
    participant DAO as ConfigDao
    participant DB as MySQL config table
    participant Redis as Redis Cache
    
    Admin->>API: GET /config
    API->>DAO: ConfigDao.get_config(INIT_DB)
    DAO->>DB: SELECT * FROM config WHERE key='initdb_config'
    DB-->>DAO: Config record
    DAO-->>API: config.value (YAML string)
    API-->>Admin: resp_200(config_str)
    
    Admin->>API: POST /config/save {data: "...yaml..."}
    API->>API: yaml.safe_load(data)
    API->>API: Validate linsight_invitation_code
    API->>DAO: ConfigDao.insert_config(config)
    DAO->>DB: INSERT/UPDATE config
    DAO->>Redis: DELETE config:initdb_config
    Redis-->>DAO: OK
    DAO-->>API: Success
    API-->>Admin: resp_200()
```

### GET /config

Retrieves the current `initdb_config.yaml` contents from the database.

**Implementation:**
- File: [src/backend/bisheng/api/v1/endpoints.py:101-105]()
- Function: `get_config()`
- Authorization: Admin user only (`UserPayload.get_admin_user`)

**Response:**
```json
{
  "status_code": 200,
  "status_message": "success",
  "data": "knowledges:\n  etl4lm:\n    url: \"\"..."
}
```

Sources: [src/backend/bisheng/api/v1/endpoints.py:101-105]()

### POST /config/save

Updates the database-stored configuration and invalidates the Redis cache.

**Implementation:**
- File: [src/backend/bisheng/api/v1/endpoints.py:108-129]()
- Function: `save_config()`
- Authorization: Admin user only

**Request Body:**
```json
{
  "data": "knowledges:\n  etl4lm:\n    url: http://..."
}
```

**Validation Steps:**
1. Check YAML syntax with `yaml.safe_load()`
2. Validate `linsight_invitation_code` is boolean (if present)
3. Update `config` table via `ConfigDao.insert_config()`
4. Delete Redis cache key `config:initdb_config`

**Error Handling:**
- Empty data: `SystemConfigEmptyError`
- Invalid YAML: `SystemConfigInvalidError`
- Invalid boolean: `SystemConfigInvalidError`

Sources: [src/backend/bisheng/api/v1/endpoints.py:108-129]()

### GET /web/config

Retrieves frontend-specific configuration settings.

**Implementation:**
- File: [src/backend/bisheng/api/v1/endpoints.py:132-138]()
- Function: `get_web_config()`
- Authorization: None (public endpoint)

**Config Key:** `ConfigKeyEnum.WEB_CONFIG`

Sources: [src/backend/bisheng/api/v1/endpoints.py:132-138]()

### POST /web/config

Updates frontend configuration settings.

**Implementation:**
- File: [src/backend/bisheng/api/v1/endpoints.py:141-154]()
- Function: `update_web_config()`
- Authorization: Admin user only

**Request:**
```json
{
  "value": "{\"theme\": \"dark\", ...}"
}
```

Sources: [src/backend/bisheng/api/v1/endpoints.py:141-154]()

---

## Runtime Configuration Access

Configuration values are accessed at runtime through the `config_service.settings` singleton and `ConfigDao` for database-stored settings.

### Settings Service Architecture

```mermaid
graph TB
    subgraph "Configuration Loading"
        YAML_FILE["config.yaml file"]
        ENV_VARS["Environment Variables"]
        PARSER["YAML Parser + Env Resolver"]
    end
    
    subgraph "Settings Object"
        SETTINGS["config_service.settings"]
        DB_URL["settings.database_url"]
        REDIS_URL["settings.redis_url"]
        VECTOR["settings.vector_stores"]
        STORAGE["settings.object_storage"]
        LOGGER["settings.logger_conf"]
        DEBUG["settings.debug"]
        ENV_OBJ["settings.environment"]
    end
    
    subgraph "Database Config"
        CONFIGDAO["ConfigDao"]
        GET_CONFIG["get_config(ConfigKeyEnum)"]
        GET_FROM_DB["settings.get_from_db(key)"]
        REDIS_CACHE["Redis Cache"]
    end
    
    YAML_FILE --> PARSER
    ENV_VARS --> PARSER
    PARSER --> SETTINGS
    
    SETTINGS --> DB_URL
    SETTINGS --> REDIS_URL
    SETTINGS --> VECTOR
    SETTINGS --> STORAGE
    SETTINGS --> LOGGER
    
    GET_FROM_DB --> CONFIGDAO
    CONFIGDAO --> GET_CONFIG
    GET_CONFIG --> REDIS_CACHE
```

### Accessing Deployment Configuration

Deployment settings from `config.yaml` are accessed directly via the `settings` object:

```python
from bisheng.common.services.config_service import settings

# Database URL
db_url = settings.database_url

# Redis URLs
redis_url = settings.redis_url
celery_url = settings.celery_redis_url

# Vector stores
milvus_args = settings.vector_stores.milvus.connection_args
es_url = settings.vector_stores.elasticsearch.url

# Object storage
minio_endpoint = settings.object_storage.minio.endpoint
minio_bucket = settings.object_storage.minio.public_bucket

# Environment
env_name = settings.environment.env
uns_support = settings.environment.uns_support
```

Sources: [src/backend/bisheng/main.py:13](), [src/backend/bisheng/api/v1/endpoints.py:23]()

### Accessing Database-Stored Configuration

Settings from `initdb_config.yaml` are accessed through `settings.get_from_db()`:

```python
from bisheng.common.services.config_service import settings

# Knowledge base ETL settings
knowledge_config = settings.get_knowledge()
etl_url = knowledge_config.etl4lm.url
etl_timeout = knowledge_config.etl4lm.timeout

# LLM request configuration
llm_config = settings.get_from_db('llm_request')
request_timeout = llm_config.get('request_timeout', 600)
max_retries = llm_config.get('max_retries', 1)

# Environment settings
office_url = settings.get_from_db('office_url')
dialog_tips = settings.get_from_db('dialog_tips')
env_dict = settings.get_from_db('env') or {}

# System login method
login_method = settings.get_system_login_method()
allow_multi_login = login_method.allow_multi_login
```

**Caching Behavior:**
- Database config is cached in Redis with key `config:initdb_config`
- Cache is invalidated on config updates via `POST /config/save`
- First access after cache miss loads from MySQL

Sources: [src/backend/bisheng/api/v1/endpoints.py:77-96](), [src/backend/bisheng/interface/initialize/loading.py:281-289]()

### ConfigDao Operations

Direct database access for configuration management:

```python
from bisheng.common.models.config import ConfigDao, ConfigKeyEnum

# Get configuration by key
config = ConfigDao.get_config(ConfigKeyEnum.INIT_DB)
config_value = config.value if config else ''

# Save configuration
config.value = new_yaml_content
ConfigDao.insert_config(config)

# Clear Redis cache
from bisheng.core.cache.redis_manager import get_redis_client_sync
get_redis_client_sync().delete('config:initdb_config')
```

Sources: [src/backend/bisheng/api/v1/endpoints.py:103-125]()

---

## Configuration Security

Bisheng implements several security mechanisms for sensitive configuration data.

### Password Encryption

Database passwords and Redis passwords support Fernet encryption:

**Encryption Format:**
```
gAAAAABlp4b4c59FeVGF_OQRVf6NOUIGdxq8246EBD-b0hdK_jVKRs1x4PoAn0A6C5S6IiFKmWn0Nm5eBUWu-7jxcqw6TiVjQA==
```

**Usage in Configuration:**
```yaml
database_url: "mysql+pymysql://root:gAAAAAB...@mysql:3306/bisheng"

redis_url:
  mode: "cluster"
  password: encrypt(gAAAAAB...)
```

**Decryption:**
- Automatically handled by the configuration loader
- Decryption key must be available in the environment
- See internal documentation for encryption utility usage

Sources: [docker/bisheng/config/config.yaml:1-4](), [docker/bisheng/config/config.yaml:16]()

### Configuration Access Control

| API Endpoint | Authorization | Purpose |
|-------------|---------------|---------|
| `GET /config` | Admin only | View database config |
| `POST /config/save` | Admin only | Update database config |
| `GET /web/config` | Public | View frontend config |
| `POST /web/config` | Admin only | Update frontend config |
| `GET /env` | Public | View environment settings |

Admin authorization is enforced via `UserPayload.get_admin_user` dependency injection.

Sources: [src/backend/bisheng/api/v1/endpoints.py:102](), [src/backend/bisheng/api/v1/endpoints.py:109]()

### Sensitive Data Handling

The system prevents sensitive data exposure in logs and API responses:

1. **API Key Removal**: Flow data has API keys stripped before transmission
   - Function: `remove_api_keys()` in [src/backend/bisheng/api/utils.py:22-33]()
   - Detects fields with "api", "key", "token" in names
   - Sets `value: null` for password-type fields

2. **Environment Variable Masking**: Sensitive environment variables are not logged

3. **Config Validation**: YAML parsing errors are caught to prevent injection attacks

Sources: [src/backend/bisheng/api/utils.py:15-33]()

---

## Configuration Deployment Patterns

### Local Development

For local development without Docker:

1. Copy `config.yaml` to a local directory
2. Set environment variables or modify `!env` directives to direct values
3. Update `database_url`, `redis_url`, `celery_redis_url` to localhost
4. Point to local Milvus, Elasticsearch, MinIO instances

**Example:**
```yaml
database_url: "mysql+pymysql://root:password@localhost:3306/bisheng"
redis_url: "redis://localhost:6379/1"
vector_stores:
  milvus:
    connection_args: {"host":"localhost","port":"19530"}
```

### Docker Compose Deployment

Standard deployment pattern using Docker Compose:

1. Environment variables defined in `docker-compose.yml`
2. `config.yaml` mounted as volume at `/app/bisheng/config.yaml`
3. `initdb_config.yaml` content stored in database on first run
4. Configuration changes via API persist to database

**Volume Mounts:**
```yaml
volumes:
  - ./bisheng/config/config.yaml:/app/bisheng/config.yaml
  - ./data/bisheng:/app/data
```

Sources: [docker/docker-compose.yml:60-62]()

### Multi-Environment Strategy

For managing multiple environments (dev, staging, prod):

**Approach 1: Environment-Specific config.yaml**
```
config/
  ├── config.dev.yaml
  ├── config.staging.yaml
  └── config.prod.yaml
```

**Approach 2: Environment Variables Override**
```yaml
# config.yaml uses env vars for all environment-specific values
database_url: !env ${DATABASE_URL}
redis_url: !env ${REDIS_URL}
```

**Approach 3: Config Server Integration**
- Store configs in external config server (e.g., Consul, etcd)
- Load at startup via initialization script
- Not currently implemented in base system

### Configuration Versioning

The `initdb_config.yaml` contents are versioned in the database:

1. **Version Tracking**: Each config update creates a new record
2. **Rollback Support**: Previous versions can be restored by updating the `config` table
3. **Audit Trail**: Use database audit logs to track configuration changes

**Best Practices:**
- Commit `initdb_config.yaml` changes to Git for version control
- Document configuration changes in commit messages
- Test configuration changes in staging before production
- Use the API to update runtime config rather than direct database edits

Sources: [src/backend/bisheng/api/v1/endpoints.py:108-129]()

---

## Version Management

Application version is managed across multiple files using a centralized update script:

**Version Files:**
- [src/backend/pyproject.toml:3]() - Python package version
- [src/backend/bisheng/__init__.py:10]() - Runtime version constant
- [docker/docker-compose.yml:43]() - Backend image tag
- [docker/docker-compose.yml:81]() - Worker image tag
- [docker/docker-compose.yml:112]() - Frontend image tag

**Update Script:**
```bash
# update.sh
old_version="2.3.0"
new_version="2.4.0-beta1"
sed -i.bak "s/$old_version/$new_version/g" ./docker/docker-compose.yml
sed -i.bak "s/$old_version/$new_version/g" ./src/backend/pyproject.toml
sed -i.bak "s/$old_version/$new_version/g" ./src/backend/bisheng/__init__.py
```

The version is exposed via the API:
- Endpoint: `GET /version`
- Implementation: [src/backend/bisheng/api/v1/endpoints.py:424-427]()
- Included in: `GET /env` response as `env['version']`

Sources: [update.sh:1-8](), [src/backend/bisheng/__init__.py:10](), [src/backend/bisheng/api/v1/endpoints.py:95]()

---

# Page: Docker Deployment

# Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.drone.yml](.drone.yml)
- [.github/workflows/base_ci.yml](.github/workflows/base_ci.yml)
- [docker/bisheng-ft/config.yaml](docker/bisheng-ft/config.yaml)
- [docker/bisheng-uns/config.yaml](docker/bisheng-uns/config.yaml)
- [docker/docker-compose-ft.yml](docker/docker-compose-ft.yml)
- [docker/docker-compose-office.yml](docker/docker-compose-office.yml)
- [docker/docker-compose-uns.yml](docker/docker-compose-uns.yml)
- [docker/docker-compose.yml](docker/docker-compose.yml)
- [docker/mysql/conf/my.cnf](docker/mysql/conf/my.cnf)
- [docker/nginx/nginx.conf](docker/nginx/nginx.conf)
- [src/backend/Dockerfile](src/backend/Dockerfile)
- [src/backend/base.Dockerfile](src/backend/base.Dockerfile)
- [src/backend/bisheng/.gitignore](src/backend/bisheng/.gitignore)
- [src/backend/bisheng/__init__.py](src/backend/bisheng/__init__.py)
- [src/backend/bisheng/core/ai/rerank/xinference/__init__.py](src/backend/bisheng/core/ai/rerank/xinference/__init__.py)
- [src/backend/bisheng/core/ai/rerank/xinference/_compat.py](src/backend/bisheng/core/ai/rerank/xinference/_compat.py)
- [src/backend/bisheng/core/ai/rerank/xinference/client/__init__.py](src/backend/bisheng/core/ai/rerank/xinference/client/__init__.py)
- [src/backend/bisheng/core/ai/rerank/xinference/client/common.py](src/backend/bisheng/core/ai/rerank/xinference/client/common.py)
- [src/backend/bisheng/core/ai/rerank/xinference/client/handlers.py](src/backend/bisheng/core/ai/rerank/xinference/client/handlers.py)
- [src/backend/bisheng/core/ai/rerank/xinference/client/restful/__init__.py](src/backend/bisheng/core/ai/rerank/xinference/client/restful/__init__.py)
- [src/backend/bisheng/core/ai/rerank/xinference/client/restful/async_restful_client.py](src/backend/bisheng/core/ai/rerank/xinference/client/restful/async_restful_client.py)
- [src/backend/bisheng/core/ai/rerank/xinference/client/restful/restful_client.py](src/backend/bisheng/core/ai/rerank/xinference/client/restful/restful_client.py)
- [src/backend/bisheng/core/ai/rerank/xinference/fields.py](src/backend/bisheng/core/ai/rerank/xinference/fields.py)
- [src/backend/bisheng/template/frontend_node/wrappers.py](src/backend/bisheng/template/frontend_node/wrappers.py)
- [src/backend/pyproject.toml](src/backend/pyproject.toml)
- [update.sh](update.sh)

</details>



This document covers BISHENG's deployment architecture, containerization strategy, and production deployment workflows. It details the Docker-based service orchestration, CI/CD pipeline configuration, and infrastructure requirements for running BISHENG in production environments.

For system configuration details, see [Configuration](#5.1). For CI/CD pipeline specifics, see [CI/CD Pipeline](#5.3).

## Container Architecture

BISHENG uses a microservices architecture deployed through Docker containers with service orchestration managed by Docker Compose. The system consists of core application services, data storage services, and supporting services.

```mermaid
graph TB
    subgraph "Application Services"
        Backend["bisheng-backend<br/>FastAPI Application<br/>Port: 7860"]
        Frontend["bisheng-frontend<br/>React Application<br/>Port: 3001"]
        Worker["Celery Workers<br/>Background Processing"]
    end
    
    subgraph "Data Services"
        MySQL["bisheng-mysql<br/>MySQL 8.0<br/>Port: 3306"]
        Redis["bisheng-redis<br/>Redis Cache<br/>Port: 6379"]
        ES["bisheng-es<br/>Elasticsearch 8.12<br/>Ports: 9200,9300"]
        Milvus["milvus-standalone<br/>Vector Database<br/>Port: 19530"]
    end
    
    subgraph "Supporting Services"
        OnlyOffice["bisheng-office<br/>OnlyOffice DocumentServer<br/>Port: 8701"]
        Unstructured["bisheng-unstructured<br/>Document Processing<br/>Port: 10001"]
        FTServer["bisheng-ft-server<br/>Fine-tuning Service<br/>Port: 8000"]
    end
    
    subgraph "Storage Dependencies"
        MinIO["milvus-minio<br/>Object Storage<br/>Ports: 9100,9101"]
        Etcd["milvus-etcd<br/>Metadata Store<br/>Port: 2379"]
    end
    
    Backend --> MySQL
    Backend --> Redis
    Backend --> ES
    Backend --> Milvus
    Backend --> OnlyOffice
    Backend --> Unstructured
    
    Milvus --> MinIO
    Milvus --> Etcd
    
    Frontend --> Backend
    Worker --> Redis
    Worker --> MySQL
```

**Core Service Dependencies**

The deployment architecture ensures proper service dependencies and health checks. The backend service depends on healthy MySQL, Redis, and OnlyOffice services before starting.

Sources: [docker/docker-compose.yml:86-92](), [docker/docker-compose.yml:54-93]()

## Service Configuration

### Backend Service Configuration

The backend service runs on port 7860 using image `dataelement/bisheng-backend:v1.3.1` with comprehensive environment variables for service integration:

| Environment Variable | Purpose | Default Value |
|----------------------|---------|---------------|
| `BS_MILVUS_CONNECTION_ARGS` | Milvus connection parameters | `{"host":"milvus","port":"19530","user":"","password":"","secure":false}` |
| `BS_MILVUS_IS_PARTITION` | Enable Milvus partitioning | `true` |
| `BS_MILVUS_PARTITION_SUFFIX` | Partition identifier | `1` |
| `BS_ELASTICSEARCH_URL` | Elasticsearch endpoint | `http://elasticsearch:9200` |
| `BS_ELASTICSEARCH_SSL_VERIFY` | ES authentication config | `{}` |
| `BS_MINIO_ENDPOINT` | MinIO storage endpoint | `minio:9000` |
| `BS_MINIO_SHAREPOINT` | MinIO share endpoint | `minio:9000` |
| `BS_MINIO_ACCESS_KEY` | MinIO access credentials | `minioadmin` |
| `BS_MINIO_SECRET_KEY` | MinIO secret credentials | `minioadmin` |
| `BS_MINIO_SCHEMA` | Use HTTPS for MinIO | `false` |
| `BS_MINIO_CERT_CHECK` | SSL certificate verification | `false` |

**Container Volume Mapping:**
```mermaid
graph LR
    subgraph "Host Volumes"
        ConfigYAML["${DOCKER_VOLUME_DIRECTORY}/bisheng/config/config.yaml"]
        EntryScript["${DOCKER_VOLUME_DIRECTORY}/bisheng/entrypoint.sh"] 
        DataDir["${DOCKER_VOLUME_DIRECTORY}/data/bisheng"]
    end
    
    subgraph "Container Paths"
        AppConfig["/app/bisheng/config.yaml"]
        AppEntry["/app/entrypoint.sh"]
        AppData["/app/data"]
    end
    
    ConfigYAML --> AppConfig
    EntryScript --> AppEntry
    DataDir --> AppData
```

**Backend Worker Service:**
The `backend_worker` service uses the same image and configuration but runs Celery workers for background task processing using command `sh entrypoint.sh worker`.

Sources: [docker/docker-compose.yml:54-93](), [docker/docker-compose.yml:94-125](), [docker/docker-compose.yml:60-71]()

### Frontend Service Configuration

The frontend service runs on port 3001 using image `dataelement/bisheng-frontend:v1.3.1` with Nginx reverse proxy configuration. The service depends on the backend service and mounts custom Nginx configuration files:

| Volume Mount | Purpose | Container Path |
|--------------|---------|----------------|
| `nginx/nginx.conf` | Main Nginx configuration | `/etc/nginx/nginx.conf` |
| `nginx/conf.d` | Virtual host configurations | `/etc/nginx/conf.d` |

**Service Dependencies:**
```mermaid
graph TD
    Frontend["bisheng-frontend<br/>dataelement/bisheng-frontend:v1.3.1<br/>Port: 3001"]
    Backend["bisheng-backend<br/>Port: 7860"]
    
    Frontend --> Backend
```

The frontend container serves the React application and proxies API requests to the backend service.

Sources: [docker/docker-compose.yml:126-139](), [docker/docker-compose.yml:134-135]()

### Database Services

**MySQL Configuration (`bisheng-mysql`):**
- Image: `mysql:8.0`
- Port: 3306
- Database: `bisheng`
- Root password: `1234` (configurable via `MYSQL_ROOT_PASSWORD`)
- Volume mounts:
  - Configuration: `mysql/conf/my.cnf` → `/etc/mysql/my.cnf`
  - Data persistence: `mysql/data` → `/var/lib/mysql`
- Health check: `mysql -u root -p$$MYSQL_ROOT_PASSWORD`

**Redis Configuration (`bisheng-redis`):**
- Image: `redis:7.0.4`
- Port: 6379
- Volume mounts:
  - Data: `data/redis` → `/data`
  - Config: `redis/redis.conf` → `/etc/redis.conf`
- Command: `redis-server /etc/redis.conf`
- Health check: `redis-cli ping|grep -e "PONG\|NOAUTH"`

**Elasticsearch Configuration (`bisheng-es`):**
- Image: `docker.io/bitnami/elasticsearch:8.12.0`
- Ports: 9200, 9300
- Data volume: `data/es` → `/bitnami/elasticsearch/data`
- User: `root`

**Milvus Vector Database (`bisheng-milvus-standalone`):**
- Image: `milvusdb/milvus:v2.5.10`
- Port: 19530 (gRPC), 9091 (HTTP)
- Dependencies: `etcd:2379`, `minio:9000`
- Data volume: `data/milvus` → `/var/lib/milvus`
- Health check: `curl -f http://localhost:9091/healthz`

Sources: [docker/docker-compose.yml:2-21](), [docker/docker-compose.yml:23-39](), [docker/docker-compose.yml:140-151](), [docker/docker-compose.yml:192-217]()

## Docker Image Building

### Multi-Architecture Build Process

BISHENG supports both AMD64 and ARM64 architectures through GitHub Actions CI/CD pipeline. The build process creates separate images for each architecture and combines them into multi-platform manifests.

**Build Architecture:**
```mermaid
graph TD
    subgraph "GitHub Actions Pipeline"
        TagPush["Git Tag Push<br/>refs/tags/v*"]
        BuildLangchain["build_bisheng_langchain<br/>Python Package Build"]
        BuildBackendAMD["build_bisheng_backend<br/>AMD64 Runner"]
        BuildBackendARM["build_backend_arm<br/>ARM64 Runner"]
        BuildFrontendAMD["build_bisheng_frontend<br/>AMD64 Runner"] 
        BuildFrontendARM["build_frontend_arm<br/>ARM64 Runner"]
    end
    
    subgraph "Docker Registry"
        BackendAMD["dataelement/bisheng-backend:v1.3.1-amd64"]
        BackendARM["dataelement/bisheng-backend:v1.3.1-arm64"]
        FrontendAMD["dataelement/bisheng-frontend:v1.3.1-amd64"]
        FrontendARM["dataelement/bisheng-frontend:v1.3.1-arm64"]
    end
    
    TagPush --> BuildLangchain
    BuildLangchain --> BuildBackendAMD
    BuildLangchain --> BuildBackendARM
    TagPush --> BuildFrontendAMD
    TagPush --> BuildFrontendARM
    
    BuildBackendAMD --> BackendAMD
    BuildBackendARM --> BackendARM
    BuildFrontendAMD --> FrontendAMD
    BuildFrontendARM --> FrontendARM
```

**Backend Build Process:**
The backend build uses `src/backend/Dockerfile` with platform-specific tags:
- AMD64: `bisheng-backend:$VERSION-amd64`
- ARM64: `bisheng-backend:$VERSION-arm64`

**Frontend Build Process:**
The frontend build uses `src/frontend/Dockerfile` with corresponding architecture tags.

Sources: [.github/workflows/ci.yml:84-87](), [.github/workflows/ci.yml:120-123](), [.github/workflows/ci.yml:149-152]()

### Version Management

Version synchronization is handled through the `update.sh` script and maintained consistently across:

| File | Version Location | Current Version |
|------|------------------|-----------------|
| Docker Compose | `image: dataelement/bisheng-backend:v1.3.1` | 1.3.1 |
| Python Package | `version = "1.3.1"` | 1.3.1 |
| Backend Module | `__version__ = '1.3.1'` | 1.3.1 |
| CI Environment | `RELEASE_VERSION=1.3.1` | 1.3.1 |

```bash
old_version="1.3.0"
new_version="1.3.1"
```

Sources: [update.sh:3-7](), [src/backend/pyproject.toml:3](), [src/backend/bisheng/__init__.py:9](), [docker/docker-compose.yml:56]()

## CI/CD Pipeline Architecture

BISHENG uses GitHub Actions for automated building, testing, and deployment with two main workflows: CI pipeline for tag builds and release pipeline for production deployments.

**GitHub Actions Workflow:**
```mermaid
graph TD
    subgraph "Trigger Events"
        TagPush["Git Tag Push<br/>refs/tags/v*"]
        ReleasePub["GitHub Release<br/>Published"]
    end
    
    subgraph "CI Pipeline (.github/workflows/ci.yml)"
        BuildLang["build_bisheng_langchain<br/>PyPI Package Build"]
        BuildBE["build_bisheng_backend<br/>docker buildx AMD64"]
        BuildBEARM["build_backend_arm<br/>docker buildx ARM64"]  
        BuildFE["build_bisheng_frontend<br/>docker buildx AMD64"]
        BuildFEARM["build_frontend_arm<br/>docker buildx ARM64"]
        NotifyFS["notify_feishu<br/>Feishu Webhook"]
    end
    
    subgraph "Release Pipeline (.github/workflows/release.yml)"
        CombineImages["combine_publish_images<br/>docker manifest"]
        SyncPrivate["sync_dataelem_repos<br/>cr.dataelem.com"]
        TestPull["test_pull_images<br/>Validation"]
        NotifyRelease["notify_feishu<br/>Release Notification"]
    end
    
    subgraph "Registries"
        DockerHub["DockerHub<br/>dataelement/bisheng-*"]
        PrivateReg["Private Registry<br/>cr.dataelem.com"]
    end
    
    TagPush --> BuildLang
    BuildLang --> BuildBE
    BuildLang --> BuildBEARM
    TagPush --> BuildFE
    TagPush --> BuildFEARM
    
    BuildBE --> DockerHub
    BuildBEARM --> DockerHub
    BuildFE --> DockerHub
    BuildFEARM --> DockerHub
    
    BuildBE --> NotifyFS
    BuildBEARM --> NotifyFS
    BuildFE --> NotifyFS
    BuildFEARM --> NotifyFS
    
    ReleasePub --> CombineImages
    CombineImages --> SyncPrivate
    SyncPrivate --> TestPull
    TestPull --> NotifyRelease
    
    CombineImages --> DockerHub
    SyncPrivate --> PrivateReg
```

### Build Stages

**Package Stage (`build_bisheng_langchain`):**
- Builds `bisheng-langchain` wheel using `python setup.py bdist_wheel`
- Publishes to PyPI using `twine upload`
- Required dependency for backend builds

**Multi-Architecture Docker Builds:**
- Uses `docker buildx` for cross-platform builds
- Separate runners for AMD64 and ARM64 architectures
- Platform-specific tags: `${VERSION}-amd64`, `${VERSION}-arm64`

**Release Manifest Creation:**
- Combines architecture-specific images into multi-platform manifests
- Creates both versioned and `latest` tags
- Synchronizes to private registry `cr.dataelem.com`

### Environment Configuration

**DockerHub Integration:**
- Uses `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` secrets
- Repository prefix: `dataelement/`
- Automatic image tagging based on Git tag version

**Private Registry Sync:**
- Secondary deployment to `cr.dataelem.com`
- Uses separate credentials: `CR_DOCKERHUB_USERNAME`, `CR_DOCKERHUB_TOKEN`
- Validation through pull testing

Sources: [.github/workflows/ci.yml:16-216](), [.github/workflows/release.yml:15-156](), [.github/workflows/ci.yml:38-48]()

## Service Orchestration Files

### Main Services Compose

The primary `docker-compose.yml` defines the core BISHENG services with proper dependency management and health checks:

```yaml
services:
  backend:
    depends_on:
      mysql:
        condition: service_healthy
      redis:
        condition: service_healthy
      office:
        condition: service_started
```

Sources: [docker/docker-compose.yml:1-185]()

### Additional Services

**Document Processing Service (`docker-compose-uns.yml`):**
- Service name: `bisheng-unstructured`
- Image: `dataelement/bisheng-unstructured:v0.0.3.14`
- Port: 10001
- Configuration: `bisheng-uns/config.yaml` with PDF model endpoints
- Health check: `curl -f http://localhost:10001/health`

**Fine-tuning Service (`docker-compose-ft.yml`):**
- Service name: `bisheng-ft-server` 
- Image: `dataelement/bisheng-ft:v0.2.0`
- Port: 8000
- GPU requirements: `driver: nvidia, count: all, capabilities: [gpu]`
- Volume mounts:
  - Model repository: `/opt/bisheng-ft/models/model_repository`
  - Training output: `/opt/bisheng-ft/finetune_output`
- Redis connection: `redis://bisheng-redis:6379/5`

Sources: [docker/docker-compose-uns.yml:1-22](), [docker/docker-compose-ft.yml:1-30](), [docker/bisheng-ft/config.yaml:3]()

## Production Deployment Considerations

### Resource Requirements

The deployment requires adequate resources for all services:

| Service | CPU | Memory | Storage | Special Requirements |
|---------|-----|--------|---------|---------------------|
| Backend | 2+ cores | 4GB+ | - | - |
| Frontend | 1 core | 1GB | - | - |
| MySQL | 2+ cores | 2GB+ | 50GB+ | Persistent storage |
| Milvus | 4+ cores | 8GB+ | 100GB+ | Vector storage |
| Elasticsearch | 2+ cores | 4GB+ | 50GB+ | Search indices |

### Security Configuration

Production deployments should implement:
- SSL/TLS termination at the load balancer
- Database credential encryption
- JWT secret key rotation
- Network isolation between services

### Monitoring and Health Checks

Each service includes comprehensive health check configuration:
- HTTP endpoint checks for web services
- Database connection validation
- Custom health check intervals and retry policies

Sources: [docker/docker-compose.yml:15-20](), [docker/docker-compose.yml:80-85](), [docker/docker-compose.yml:173-178]()

---

# Page: CI/CD Pipeline

# CI/CD Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.drone.yml](.drone.yml)
- [.github/workflows/base_ci.yml](.github/workflows/base_ci.yml)
- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [.github/workflows/release.yml](.github/workflows/release.yml)
- [.pre-commit-config.yaml](.pre-commit-config.yaml)
- [src/backend/Dockerfile](src/backend/Dockerfile)
- [src/backend/base.Dockerfile](src/backend/base.Dockerfile)
- [src/backend/bisheng/.gitignore](src/backend/bisheng/.gitignore)
- [src/backend/bisheng/api/services/chat_imp.py](src/backend/bisheng/api/services/chat_imp.py)
- [src/backend/bisheng/core/ai/rerank/xinference/__init__.py](src/backend/bisheng/core/ai/rerank/xinference/__init__.py)
- [src/backend/bisheng/core/ai/rerank/xinference/_compat.py](src/backend/bisheng/core/ai/rerank/xinference/_compat.py)
- [src/backend/bisheng/core/ai/rerank/xinference/client/__init__.py](src/backend/bisheng/core/ai/rerank/xinference/client/__init__.py)
- [src/backend/bisheng/core/ai/rerank/xinference/client/common.py](src/backend/bisheng/core/ai/rerank/xinference/client/common.py)
- [src/backend/bisheng/core/ai/rerank/xinference/client/handlers.py](src/backend/bisheng/core/ai/rerank/xinference/client/handlers.py)
- [src/backend/bisheng/core/ai/rerank/xinference/client/restful/__init__.py](src/backend/bisheng/core/ai/rerank/xinference/client/restful/__init__.py)
- [src/backend/bisheng/core/ai/rerank/xinference/client/restful/async_restful_client.py](src/backend/bisheng/core/ai/rerank/xinference/client/restful/async_restful_client.py)
- [src/backend/bisheng/core/ai/rerank/xinference/client/restful/restful_client.py](src/backend/bisheng/core/ai/rerank/xinference/client/restful/restful_client.py)
- [src/backend/bisheng/core/ai/rerank/xinference/fields.py](src/backend/bisheng/core/ai/rerank/xinference/fields.py)
- [src/backend/bisheng/interface/initialize/vector_store.py](src/backend/bisheng/interface/initialize/vector_store.py)
- [src/backend/bisheng/processing/base.py](src/backend/bisheng/processing/base.py)
- [src/backend/bisheng/processing/process.py](src/backend/bisheng/processing/process.py)
- [src/backend/bisheng/services/session/service.py](src/backend/bisheng/services/session/service.py)
- [src/backend/bisheng/template/frontend_node/embeddings.py](src/backend/bisheng/template/frontend_node/embeddings.py)
- [src/backend/bisheng/template/frontend_node/llms.py](src/backend/bisheng/template/frontend_node/llms.py)
- [src/backend/bisheng/template/frontend_node/vectorstores.py](src/backend/bisheng/template/frontend_node/vectorstores.py)
- [src/backend/test/test_filelib.py](src/backend/test/test_filelib.py)

</details>



## Purpose and Scope

This document describes the Continuous Integration and Continuous Deployment (CI/CD) pipeline for the Bisheng platform. The pipeline automates the building, testing, and publishing of Docker images for both backend and frontend components across multiple architectures (amd64 and arm64).

For information about Docker deployment configuration, see [Docker Deployment](#5.2). For general configuration management, see [Configuration Management](#5.1).

---

## Overview

The Bisheng CI/CD pipeline consists of three distinct automation systems that work together to build, test, and deploy the platform:

1. **Base Image Workflow** (`.github/workflows/base_ci.yml`) - Triggered on tags matching `base.v*`, builds foundational Docker images with system dependencies and Python packages for both amd64 and arm64 architectures
2. **Application CI Workflow** (`.github/workflows/ci.yml`) - Triggered on Git tag pushes matching `v*`, builds application-specific Docker images that extend the base images with Bisheng code
3. **Release Workflow** (`.github/workflows/release.yml`) - Triggered on GitHub release publication, creates unified multi-architecture manifests and synchronizes images to the private registry at `cr.dataelem.com`
4. **Drone CI Workflow** (`.drone.yml`) - Provides continuous deployment for the `release` branch and feature branches to private infrastructure, with automatic Docker builds and SSH-based deployment to test servers

The GitHub Actions workflows handle public releases to Docker Hub, while Drone CI manages internal deployments to private infrastructure with Chinese mirror repositories for faster builds. Base images are versioned separately (e.g., `base.v8`) to allow dependency updates independent of application releases.

**Sources:** [.github/workflows/base_ci.yml:1-129](), [.github/workflows/ci.yml:1-188](), [.github/workflows/release.yml:1-166](), [.drone.yml:1-338]()

---

## Pipeline Architecture

### Complete Pipeline Overview

```mermaid
graph TB
    subgraph "Base Image Pipeline"
        BASE_TAG["Git Tag Push<br/>base.v*"]
        BASE_TAG --> BASE_AMD["build_bisheng_amd<br/>ubuntu-latest"]
        BASE_TAG --> BASE_ARM["build_bisheng_arm<br/>ubuntu-22.04-arm"]
        
        BASE_AMD --> BASE_IMG_AMD["bisheng-backend:base.vX-amd64"]
        BASE_ARM --> BASE_IMG_ARM["bisheng-backend:base.vX-arm64"]
        
        BASE_IMG_AMD --> COMBINE_BASE["combine_two_images"]
        BASE_IMG_ARM --> COMBINE_BASE
        COMBINE_BASE --> BASE_MANIFEST["bisheng-backend:base.vX"]
        BASE_MANIFEST --> DH_BASE["Docker Hub"]
    end
    
    subgraph "Application CI Pipeline"
        APP_TAG["Git Tag Push<br/>v*"]
        APP_TAG --> BUILD_BE_AMD["build_bisheng_backend<br/>ubuntu-latest"]
        APP_TAG --> BUILD_BE_ARM["build_backend_arm<br/>ubuntu-22.04-arm"]
        APP_TAG --> BUILD_FE_AMD["build_bisheng_frontend<br/>ubuntu-latest"]
        APP_TAG --> BUILD_FE_ARM["build_frontend_arm<br/>ubuntu-22.04-arm"]
        
        DH_BASE -.->|"FROM base.vX"| BUILD_BE_AMD
        DH_BASE -.->|"FROM base.vX"| BUILD_BE_ARM
        
        BUILD_BE_AMD --> IMG_BE_AMD["bisheng-backend:VERSION-amd64"]
        BUILD_BE_ARM --> IMG_BE_ARM["bisheng-backend:VERSION-arm64"]
        BUILD_FE_AMD --> IMG_FE_AMD["bisheng-frontend:VERSION-amd64"]
        BUILD_FE_ARM --> IMG_FE_ARM["bisheng-frontend:VERSION-arm64"]
        
        IMG_BE_AMD --> DH_APP["Docker Hub"]
        IMG_BE_ARM --> DH_APP
        IMG_FE_AMD --> DH_APP
        IMG_FE_ARM --> DH_APP
    end
    
    subgraph "Release Pipeline"
        RELEASE["GitHub Release"]
        RELEASE --> COMBINE["combine_publish_images"]
        RELEASE --> SYNC["sync_dataelem_repos"]
        
        DH_APP -.-> COMBINE
        DH_APP -.-> SYNC
        
        COMBINE --> MANIFEST["Multi-arch Manifests"]
        SYNC --> CR["cr.dataelem.com"]
        
        MANIFEST --> TEST["test_pull_images"]
        CR --> TEST
        TEST --> NOTIFY_REL["notify_feishu"]
    end
    
    subgraph "Drone CI Pipeline"
        DRONE_PUSH["Push to release branch"]
        DRONE_PUSH --> CLONE["clone step"]
        CLONE --> SET_POETRY["set poetry<br/>Modify Dockerfile"]
        SET_POETRY --> DOCKER_BE["build_docker<br/>Backend"]
        SET_POETRY --> DOCKER_FE["build_docker_frontend"]
        
        DOCKER_BE --> PRIVATE_REG["192.168.106.8:6082"]
        DOCKER_FE --> PRIVATE_REG
        
        PRIVATE_REG --> SSH_DEPLOY["ssh deploy<br/>192.168.106.116"]
        SSH_DEPLOY --> DOCKER_COMPOSE["docker compose pull<br/>docker compose up -d"]
        DOCKER_COMPOSE --> NOTIFY_DRONE["notify-start<br/>Feishu webhook"]
    end
```

**Sources:** [.github/workflows/base_ci.yml:3-7](), [.github/workflows/ci.yml:3-7](), [.github/workflows/release.yml:4-6](), [.drone.yml:1-6,156-160]()

### Pipeline Comparison

| Pipeline | Trigger | Registry | Purpose | Architecture |
|----------|---------|----------|---------|--------------|
| Base Image | Tag `base.v*` | Docker Hub | Build foundation images with dependencies | amd64, arm64 |
| Application CI | Tag `v*` | Docker Hub | Build app images on top of base | amd64, arm64 |
| Release | GitHub Release | Docker Hub + cr.dataelem.com | Publish multi-arch manifests | Multi-arch |
| Drone CI | Push to `release` branch | 192.168.106.8:6082 | Deploy to test environment | Single-arch |

**Sources:** [.github/workflows/base_ci.yml:3-7](), [.github/workflows/ci.yml:3-7](), [.github/workflows/release.yml:4-6](), [.drone.yml:156-160]()

---

## CI Workflow Details

The CI workflow is triggered when a tag matching the pattern `v*` is pushed to the repository. It builds four separate Docker images in parallel jobs.

### Trigger Configuration

```yaml
on:
  push:
    tags:
      - "v*"
```

**Sources:** [.github/workflows/ci.yml:3-7]()

### Build Jobs

| Job Name | Runner | Platform | Image | Notes |
|----------|--------|----------|-------|-------|
| `build_bisheng_backend` | `ubuntu-latest` | `linux/amd64` | `bisheng-backend:VERSION-amd64` | Standard backend build |
| `build_backend_arm` | `ubuntu-22.04-arm` | `linux/arm64` | `bisheng-backend:VERSION-arm64` | Removes `ibm-db` dependency |
| `build_bisheng_frontend` | `ubuntu-latest` | `linux/amd64` | `bisheng-frontend:VERSION-amd64` | Standard frontend build |
| `build_frontend_arm` | `ubuntu-22.04-arm` | `linux/arm64` | `bisheng-frontend:VERSION-arm64` | Standard frontend build |

**Sources:** [.github/workflows/ci.yml:18-96](), [.github/workflows/ci.yml:97-159]()

### Backend Build Process (amd64)

```mermaid
graph LR
    CHECKOUT["Checkout Code"] --> VERSION["Extract Version<br/>from Tag"]
    VERSION --> LOGIN["Login to<br/>Docker Hub"]
    LOGIN --> QEMU["Setup QEMU"]
    QEMU --> BUILDX["Setup Docker<br/>Buildx"]
    BUILDX --> BUILD["docker buildx build<br/>--platform linux/amd64<br/>--tag VERSION-amd64"]
    BUILD --> PUSH["Push to<br/>Docker Hub"]
```

**Sources:** [.github/workflows/ci.yml:22-54]()

### ARM64-Specific Handling

The ARM64 backend build includes a critical preprocessing step to remove the `ibm-db` dependency, which is not compatible with ARM64 architecture:

```bash
# Remove ibm-db lib
sed -i '/ibm-db*/d' ./src/backend/pyproject.toml
```

This step modifies the `pyproject.toml` file before building to exclude the `ibm-db` package.

**Sources:** [.github/workflows/ci.yml:86-90]()

### Version Extraction

Each job extracts the version from the Git tag using GitHub Actions expressions:

```bash
echo ::set-output name=VERSION::${GITHUB_REF/refs\/tags\//}
```

This removes the `refs/tags/` prefix, converting `refs/tags/v1.0.0` to `v1.0.0`.

**Sources:** [.github/workflows/ci.yml:25-28](), [.github/workflows/ci.yml:62-65]()

### Docker Build Command

The actual build command uses Docker Buildx for multi-platform support:

```bash
docker buildx build \
  --file ./src/backend/Dockerfile \
  --platform linux/amd64 \
  --provenance false \
  --tag dataelement/bisheng-backend:VERSION-amd64 \
  --push \
  ./src/backend/
```

The `--provenance false` flag disables provenance attestation to avoid compatibility issues with some registries.

**Sources:** [.github/workflows/ci.yml:51-54](), [.github/workflows/ci.yml:92-95]()

---

## Release Workflow Details

The Release workflow is triggered when a GitHub release is published (not just created as a draft).

### Workflow Structure

```mermaid
graph TB
    TRIGGER["GitHub Release<br/>Published"] --> JOB1["combine_publish_images"]
    TRIGGER --> JOB2["sync_dataelem_repos"]
    
    JOB1 --> MANIFEST1["Create Backend Manifest<br/>VERSION + latest"]
    JOB1 --> MANIFEST2["Create Frontend Manifest<br/>VERSION + latest"]
    
    JOB2 --> PULL1["Pull amd64 Images"]
    JOB2 --> PULL2["Pull arm64 Images"]
    PULL1 --> TAG1["Tag for cr.dataelem.com"]
    PULL2 --> TAG1
    TAG1 --> PUSH1["Push to Private Registry"]
    
    JOB1 --> TEST["test_pull_images"]
    JOB2 --> TEST
    TEST --> VERIFY1["docker pull from Docker Hub"]
    TEST --> VERIFY2["docker pull from cr.dataelem.com"]
    VERIFY1 --> NOTIFY["notify_feishu"]
    VERIFY2 --> NOTIFY
```

**Sources:** [.github/workflows/release.yml:15-166]()

### Manifest Creation

The `combine_publish_images` job creates multi-architecture manifests that reference both amd64 and arm64 images:

```bash
# Create VERSION manifest
docker manifest create \
  dataelement/bisheng-backend:VERSION \
  dataelement/bisheng-backend:VERSION-arm64 \
  dataelement/bisheng-backend:VERSION-amd64

docker manifest push dataelement/bisheng-backend:VERSION

# Create latest manifest
docker manifest create \
  dataelement/bisheng-backend:latest \
  dataelement/bisheng-backend:VERSION-arm64 \
  dataelement/bisheng-backend:VERSION-amd64

docker manifest push dataelement/bisheng-backend:latest
```

This process is repeated for both backend and frontend images.

**Sources:** [.github/workflows/release.yml:38-51]()

### Private Registry Synchronization

The `sync_dataelem_repos` job synchronizes images to the private registry at `cr.dataelem.com`:

```mermaid
graph LR
    PULL["Pull from Docker Hub<br/>dataelement/bisheng-backend:VERSION-amd64"] --> TAG1["Tag as<br/>cr.dataelem.com/.../VERSION"]
    PULL --> TAG2["Tag as<br/>cr.dataelem.com/.../latest"]
    TAG1 --> PUSH1["Push VERSION"]
    TAG2 --> PUSH2["Push latest"]
    
    PULL_ARM["Pull ARM64<br/>VERSION-arm64"] --> TAG_ARM["Tag as<br/>cr.dataelem.com/.../VERSION-arm64"]
    TAG_ARM --> PUSH_ARM["Push ARM64"]
```

**Sources:** [.github/workflows/release.yml:72-101]()

### Image Validation

The `test_pull_images` job validates that all images can be successfully pulled from both registries:

```bash
# Test Docker Hub
docker pull dataelement/bisheng-backend:VERSION
docker pull dataelement/bisheng-frontend:VERSION

# Test Private Registry
docker pull cr.dataelem.com/dataelement/bisheng-backend:VERSION
docker pull cr.dataelem.com/dataelement/bisheng-frontend:VERSION
```

This ensures the release process completed successfully before sending notifications.

**Sources:** [.github/workflows/release.yml:133-139]()

---

## Image Naming Convention

The pipeline uses a systematic naming convention for Docker images:

### Architecture-Specific Tags (CI Stage)

| Component | Architecture | Tag Format | Example |
|-----------|-------------|------------|---------|
| Backend | amd64 | `bisheng-backend:VERSION-amd64` | `bisheng-backend:v1.0.0-amd64` |
| Backend | arm64 | `bisheng-backend:VERSION-arm64` | `bisheng-backend:v1.0.0-arm64` |
| Frontend | amd64 | `bisheng-frontend:VERSION-amd64` | `bisheng-frontend:v1.0.0-amd64` |
| Frontend | arm64 | `bisheng-frontend:VERSION-arm64` | `bisheng-frontend:v1.0.0-arm64` |

### Multi-Architecture Tags (Release Stage)

| Component | Tag Type | Tag Format | Points To |
|-----------|----------|------------|-----------|
| Backend | Version | `bisheng-backend:VERSION` | Manifest referencing both architectures |
| Backend | Latest | `bisheng-backend:latest` | Manifest referencing both architectures |
| Frontend | Version | `bisheng-frontend:VERSION` | Manifest referencing both architectures |
| Frontend | Latest | `bisheng-frontend:latest` | Manifest referencing both architectures |

**Sources:** [.github/workflows/ci.yml:54](), [.github/workflows/release.yml:41-51]()

---

## Registry Configuration

### Docker Hub (Public)

- **Registry:** `docker.io`
- **Repository Prefix:** `dataelement/`
- **Authentication:** Uses GitHub Secrets `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN`
- **Purpose:** Primary public distribution channel

**Sources:** [.github/workflows/ci.yml:10](), [.github/workflows/ci.yml:35-42]()

### Private Registry

- **Registry:** `cr.dataelem.com`
- **Repository Prefix:** `dataelement/`
- **Authentication:** Uses GitHub Secrets `CR_DOCKERHUB_USERNAME` and `CR_DOCKERHUB_TOKEN`
- **Purpose:** Private distribution for enterprise deployments

**Sources:** [.github/workflows/release.yml:68-70]()

### Authentication Configuration

Both workflows authenticate to Docker registries using the `docker/login-action@v1` action:

```yaml
- name: Login to DockerHub
  uses: docker/login-action@v1
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}
```

For the private registry, the `registry` parameter is specified:

```yaml
- name: Login to DockerHub
  uses: docker/login-action@v1
  with:
    registry: https://cr.dataelem.com/
    username: ${{ secrets.CR_DOCKERHUB_USERNAME }}
    password: ${{ secrets.CR_DOCKERHUB_TOKEN }}
```

**Sources:** [.github/workflows/ci.yml:35-42](), [.github/workflows/release.yml:65-70]()

---

## Multi-Architecture Support

The pipeline implements comprehensive multi-architecture support using Docker Buildx and manifest lists.

### Platform-Specific Build Matrix

| Architecture | Runner | Special Handling |
|-------------|--------|------------------|
| `linux/amd64` | `ubuntu-latest` | Standard build process |
| `linux/arm64` | `ubuntu-22.04-arm` | - Native ARM runner<br/>- Removes `ibm-db` dependency for backend |

**Sources:** [.github/workflows/ci.yml:19](), [.github/workflows/ci.yml:57]()

### Docker Buildx Setup

Each build job sets up Docker Buildx for cross-platform builds:

```yaml
- name: Set up QEMU
  uses: docker/setup-qemu-action@v1

- name: set up Docker Buildx
  uses: docker/setup-buildx-action@v3
```

QEMU enables emulation of different CPU architectures, while Buildx provides the multi-platform build capability.

**Sources:** [.github/workflows/ci.yml:45-49]()

### Manifest List Creation

The release workflow combines architecture-specific images into multi-architecture manifest lists:

```mermaid
graph TB
    subgraph "Input Images"
        AMD64["bisheng-backend:VERSION-amd64<br/>Platform: linux/amd64"]
        ARM64["bisheng-backend:VERSION-arm64<br/>Platform: linux/arm64"]
    end
    
    subgraph "Manifest Creation"
        CMD["docker manifest create<br/>bisheng-backend:VERSION"]
    end
    
    subgraph "Output Manifest"
        MANIFEST["bisheng-backend:VERSION<br/>Multi-arch manifest list"]
        MANIFEST_AMD["Reference to amd64 image"]
        MANIFEST_ARM["Reference to arm64 image"]
    end
    
    AMD64 --> CMD
    ARM64 --> CMD
    CMD --> MANIFEST
    MANIFEST --> MANIFEST_AMD
    MANIFEST --> MANIFEST_ARM
```

When a client pulls `bisheng-backend:VERSION`, Docker automatically selects the appropriate architecture-specific image based on the client's platform.

**Sources:** [.github/workflows/release.yml:40-42]()

---

## Notification System

Both workflows integrate with Feishu (a collaboration platform) to send build and release notifications.

### Notification Jobs

| Workflow | Job Name | Trigger | Content |
|----------|----------|---------|---------|
| CI | `notify_feishu` | After all builds complete | Pre-release success with version and commit message |
| Release | `notify_feishu` | After image validation | Release success with version and commit message |

**Sources:** [.github/workflows/ci.yml:161-188](), [.github/workflows/release.yml:142-166]()

### Message Format

Notifications are sent via HTTP POST to a Feishu webhook URL:

```json
{
  "msg_type": "post",
  "content": {
    "post": {
      "zh_cn": {
        "title": "VERSION-amd64镜像预发布成功",
        "content": [
          [
            {"tag": "text", "text": "发布功能："},
            {"tag": "text", "text": "COMMIT_MESSAGE"}
          ]
        ]
      }
    }
  }
}
```

**Sources:** [.github/workflows/ci.yml:187]()

### Commit Message Processing

The workflows process commit messages to handle newlines for JSON formatting:

```bash
value=$(echo "${{ github.event.head_commit.message }}" | sed -e ':a' -e 'N' -e '$!ba' -e 's/\n/%0A/g')
value=$(echo "${value}" | sed -e ':a' -e 'N' -e '$!ba' -e 's/\r/%0A/g')
echo "message=${value}" >> $GITHUB_ENV
```

**Sources:** [.github/workflows/ci.yml:174-180]()

---

## Base Image Pipeline

The base image pipeline builds foundational Docker images containing system dependencies, Python environment, and common packages. These images are versioned independently from application releases to allow dependency updates without triggering full application rebuilds.

### Base Image Workflow Structure

```mermaid
graph LR
    TAG["Tag: base.v8"] --> BUILD_ARM["build_bisheng_arm<br/>ubuntu-22.04-arm"]
    TAG --> BUILD_AMD["build_bisheng_amd<br/>ubuntu-latest"]
    
    BUILD_ARM --> IMG_ARM["bisheng-backend:base.v8-arm64"]
    BUILD_AMD --> IMG_AMD["bisheng-backend:base.v8-amd64"]
    
    IMG_ARM --> COMBINE["combine_two_images"]
    IMG_AMD --> COMBINE
    
    COMBINE --> MANIFEST["bisheng-backend:base.v8"]
    MANIFEST --> NOTIFY["notify feishu"]
```

**Sources:** [.github/workflows/base_ci.yml:16-129]()

### Base Dockerfile Contents

The base image ([src/backend/base.Dockerfile:1-60]()) includes:

1. **System Dependencies** - libreoffice, FFmpeg, fonts, OpenCV libraries
2. **Document Processing Tools** - Pandoc 3.6.4 for document conversion
3. **Python Package Manager** - UV for fast dependency installation
4. **Python Dependencies** - Compiled from `pyproject.toml` and installed system-wide
5. **NLTK Data** - punkt, averaged_perceptron_tagger
6. **Playwright** - Chromium browser with system dependencies

The base image build process:

```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ curl build-essential libreoffice \
    wget procps vim fonts-wqy-zenhei \
    libglib2.0-0 libsm6 libxrender1 libxext6 libgl1

# Install uv package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Compile and install Python dependencies
RUN uv pip compile pyproject.toml --output-file requirements.txt && \
    uv pip install -r requirements.txt --system --no-cache-dir && \
    uv cache clean
```

**Sources:** [src/backend/base.Dockerfile:1-60]()

### ARM64 Base Image Handling

The ARM64 base image build removes the `ibm-db` dependency before compiling requirements:

```yaml
- name: fix ibm-db lib error
  run: |
    # remove ibm-db lib
    sed -i '/ibm-db*/d' ./src/backend/pyproject.toml
```

This step is critical because the IBM DB2 driver does not support ARM64 architecture.

**Sources:** [.github/workflows/base_ci.yml:45-49]()

### Base Image Build Arguments

The base Dockerfile accepts a `PANDOC_ARCH` build argument to download the correct Pandoc binary:

```dockerfile
ARG PANDOC_ARCH=amd64
ENV PANDOC_ARCH=$PANDOC_ARCH

RUN wget https://github.com/jgm/pandoc/releases/download/3.6.4/pandoc-3.6.4-linux-${PANDOC_ARCH}.tar.gz
```

The GitHub Actions workflow passes this argument during build:

```yaml
docker buildx build \
  --build-arg PANDOC_ARCH=arm64 \
  --file ./src/backend/base.Dockerfile \
  --platform linux/arm64 \
  --tag dataelement/bisheng-backend:base.v8-arm64 \
  --push ./src/backend/
```

**Sources:** [src/backend/base.Dockerfile:3-4,22-27](), [.github/workflows/base_ci.yml:51-54]()

---

## Drone CI Pipeline

Drone CI provides continuous deployment to private infrastructure for development and testing. Unlike GitHub Actions which publishes to Docker Hub, Drone builds images with Chinese mirror repositories and deploys them directly to test servers.

### Drone Pipeline Architecture

```mermaid
graph TB
    subgraph "Clone Step"
        CLONE_START["clone step<br/>alpine/git"] --> GIT_CONFIG["git config compression 0"]
        GIT_CONFIG --> GIT_CLONE["git clone + checkout"]
    end
    
    subgraph "Build Preparation"
        GIT_CLONE --> SET_POETRY["set poetry step<br/>golang image"]
        SET_POETRY --> MODIFY_DF["Modify Dockerfile:<br/>- Add Tsinghua mirrors<br/>- Remove uv cache clean"]
    end
    
    subgraph "Backend Build"
        MODIFY_DF --> BUILD_BE["build_docker step<br/>docker:24.0.6"]
        BUILD_BE --> LOGIN_BE["docker login<br/>192.168.106.8:6082"]
        LOGIN_BE --> DOCKER_BUILD_BE["docker build backend"]
        DOCKER_BUILD_BE --> PUSH_BE["docker push<br/>bisheng-backend:release"]
    end
    
    subgraph "Frontend Build"
        MODIFY_DF --> BUILD_FE["build_docker_frontend<br/>docker:24.0.6"]
        BUILD_FE --> LOGIN_FE["docker login"]
        LOGIN_FE --> DOCKER_BUILD_FE["docker build frontend"]
        DOCKER_BUILD_FE --> PUSH_FE["docker push<br/>bisheng-frontend:release"]
    end
    
    subgraph "Deployment"
        PUSH_BE --> SSH["ssh deploy step<br/>appleboy/drone-ssh"]
        PUSH_FE --> SSH
        SSH --> SSH_CMD["SSH to 192.168.106.116"]
        SSH_CMD --> COMPOSE_PULL["docker compose pull"]
        COMPOSE_PULL --> COMPOSE_UP["docker compose up -d"]
    end
    
    subgraph "Notification"
        COMPOSE_UP --> NOTIFY["notify-start<br/>plugins/webhook"]
        NOTIFY --> FEISHU["POST to Feishu"]
    end
```

**Sources:** [.drone.yml:8-124]()

### Drone Pipeline Configuration

The Drone pipeline is defined in [.drone.yml:1-338]() with two separate pipelines:

1. **cicd Pipeline** - Triggers on pushes to `release` branch
2. **feat_cicd Pipeline** - Triggers on pushes to feature branches (currently disabled via `add_some_branch_you_need`)

**Sources:** [.drone.yml:1-6,156-160,319-323]()

### Dockerfile Modification for Chinese Mirrors

A critical step in the Drone pipeline modifies the backend Dockerfile to use Chinese mirror repositories for faster builds:

```yaml
- name: set poetry
  image: golang
  commands:
    - cd ./src/backend
    - sed -i '6i\RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple' Dockerfile
    - sed -i '7i\ENV UV_PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple' Dockerfile
    - sed -i '8i\ENV UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple' Dockerfile
    - sed -i '9i\ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple' Dockerfile
    - sed -i.bak 's/uv cache clean.*$/ /' Dockerfile
```

These modifications:
- Configure pip and uv to use Tsinghua University's PyPI mirror
- Remove the `uv cache clean` command to preserve cached packages across builds

**Sources:** [.drone.yml:22-48]()

### Drone Volume Mounts

Drone uses host volume mounts to cache dependencies and share data:

```yaml
volumes:
  - name: bisheng-cache
    host:
      path: /opt/drone/data/bisheng/
  - name: pro-cache
    host:
      path: /opt/drone/data/pro/
  - name: apt-cache
    host:
      path: /opt/drone/data/bisheng/apt/
  - name: socket
    host:
      path: /var/run/docker.sock
```

These volumes persist between builds to speed up subsequent runs by caching:
- Python packages (`pro-cache`)
- APT packages (`apt-cache`)
- General build artifacts (`bisheng-cache`)

The `socket` volume mount provides access to the Docker daemon for building images.

**Sources:** [.drone.yml:162-175]()

### SSH-Based Deployment

The deployment step uses the `appleboy/drone-ssh` plugin to execute commands on the target server:

```yaml
- name: ssh deploy
  image: appleboy/drone-ssh
  settings:
    host: 192.168.106.116
    username: root
    password:
      from_secret: sshpwd
    script:
      - echo =======找到目录=======
      - cd /opt/server/bisheng-test
      - echo =======直接启动=======
      - docker compose pull
      - docker compose up -d
```

This assumes the target server has a pre-configured Docker Compose environment at `/opt/server/bisheng-test`.

**Sources:** [.drone.yml:110-123]()

### Drone Image Tagging Strategy

The Drone pipeline uses different tagging strategies based on the branch:

**Release Branch:**
- Backend: `192.168.106.8:6082/dataelement/bisheng-backend:release`
- Frontend: `192.168.106.8:6082/dataelement/bisheng-frontend:release`

**Feature Branches:**
- Backend: `192.168.106.8:6082/dataelement/bisheng-backend:${DRONE_BRANCH}` (with `/` replaced by `_`)
- Frontend: `192.168.106.8:6082/dataelement/bisheng-frontend:${DRONE_BRANCH}` (with `/` replaced by `_`)

The branch name transformation:
```bash
version=$(echo $version | sed 's/\\//_/g')
```

**Sources:** [.drone.yml:69-80,241-255,272-286]()

---

## Required Secrets

The CI/CD pipeline requires the following secrets to be configured:

### GitHub Actions Secrets

| Secret Name | Purpose | Used In |
|-------------|---------|---------|
| `DOCKERHUB_USERNAME` | Docker Hub account username | Base CI, Application CI, Release |
| `DOCKERHUB_TOKEN` | Docker Hub access token | Base CI, Application CI, Release |
| `CR_DOCKERHUB_USERNAME` | Private registry username (cr.dataelem.com) | Release |
| `CR_DOCKERHUB_TOKEN` | Private registry access token | Release |
| `FEISHU_WEBHOOK` | Feishu webhook URL for notifications | Base CI, Application CI, Release |

**Sources:** [.github/workflows/ci.yml:38-42](), [.github/workflows/release.yml:69-70](), [.github/workflows/ci.yml:185](), [.github/workflows/base_ci.yml:39-40]()

### Drone Secrets

| Secret Name | Purpose | Used In |
|-------------|---------|---------|
| `PROXY` | HTTP proxy for git and package downloads | Clone, Build |
| `NEXUS_USER` | Username for private Docker registry | Build |
| `NEXUS_PASSWORD` | Password for private Docker registry | Build |
| `PY_NEXUS` | Python package repository URL (unused in current config) | Build preparation |
| `APT-GET` | APT mirror configuration | Build preparation |
| `sshpwd` | SSH password for deployment server | Deployment |
| `FEISHU_URL` | Feishu webhook URL for notifications | Notification |

**Sources:** [.drone.yml:13-16,27-34,64-75,116-117,130-131]()

---

## Concurrency Control

Both workflows implement concurrency control to prevent multiple simultaneous runs:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

This configuration ensures that:
- Only one instance of each workflow runs per Git reference (branch/tag)
- New triggers cancel in-progress runs for the same reference
- Resources are not wasted on outdated builds

**Sources:** [.github/workflows/ci.yml:12-14](), [.github/workflows/release.yml:11-13]()

---

## Workflow Dependencies

```mermaid
graph TB
    subgraph "CI Workflow Dependencies"
        CI_START["Git Tag Push"] --> CI_BUILD["Parallel Builds<br/>4 jobs"]
        CI_BUILD --> CI_NOTIFY["notify_feishu<br/>needs: all build jobs"]
    end
    
    subgraph "Release Workflow Dependencies"
        REL_START["GitHub Release"] --> REL_COMBINE["combine_publish_images"]
        REL_START --> REL_SYNC["sync_dataelem_repos"]
        REL_COMBINE --> REL_TEST["test_pull_images<br/>needs: combine, sync"]
        REL_SYNC --> REL_TEST
        REL_TEST --> REL_NOTIFY["notify_feishu<br/>needs: test_pull_images"]
    end
    
    CI_NOTIFY -.->|"Pre-built<br/>Images Available"| REL_START
```

### CI Workflow Dependencies

The `notify_feishu` job requires all build jobs to complete successfully:

```yaml
notify_feishu:
  needs:
    - build_bisheng_backend
    - build_backend_arm
    - build_bisheng_frontend
    - build_frontend_arm
```

**Sources:** [.github/workflows/ci.yml:162-166]()

### Release Workflow Dependencies

The release workflow has a chain of dependencies:

```yaml
test_pull_images:
  needs:
    - combine_publish_images
    - sync_dataelem_repos

notify_feishu:
  needs:
    - test_pull_images
```

**Sources:** [.github/workflows/release.yml:104-106](), [.github/workflows/release.yml:143-144]()

---

## Build Context and Dockerfiles

The pipeline builds Docker images from specific contexts with corresponding Dockerfiles:

| Component | Dockerfile Path | Build Context | Notes |
|-----------|----------------|---------------|-------|
| Backend | `./src/backend/Dockerfile` | `./src/backend/` | Contains Python application and dependencies |
| Frontend | `./src/frontend/Dockerfile` | `./src/frontend/` | Contains React application build |

The build commands specify both the Dockerfile location and the build context:

```bash
docker buildx build \
  --file ./src/backend/Dockerfile \
  --platform linux/amd64 \
  --provenance false \
  --tag dataelement/bisheng-backend:VERSION-amd64 \
  --push \
  ./src/backend/
```

The final argument (`./src/backend/`) is the build context directory that Docker uses to locate files referenced in the Dockerfile.

**Sources:** [.github/workflows/ci.yml:54](), [.github/workflows/ci.yml:124]()

---

# Page: Advanced Topics

# Advanced Topics

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/backend/bisheng/api/services/knowledge.py](src/backend/bisheng/api/services/knowledge.py)
- [src/backend/bisheng/api/services/knowledge_imp.py](src/backend/bisheng/api/services/knowledge_imp.py)
- [src/backend/bisheng/core/cache/redis_conn.py](src/backend/bisheng/core/cache/redis_conn.py)
- [src/backend/bisheng/linsight/domain/task_exec.py](src/backend/bisheng/linsight/domain/task_exec.py)
- [src/backend/bisheng/linsight/domain/utils.py](src/backend/bisheng/linsight/domain/utils.py)
- [src/backend/bisheng/linsight/worker.py](src/backend/bisheng/linsight/worker.py)
- [src/backend/bisheng/worker/knowledge/file_worker.py](src/backend/bisheng/worker/knowledge/file_worker.py)
- [src/backend/bisheng/worker/knowledge/qa.py](src/backend/bisheng/worker/knowledge/qa.py)
- [src/backend/bisheng/worker/knowledge/rebuild_knowledge_worker.py](src/backend/bisheng/worker/knowledge/rebuild_knowledge_worker.py)

</details>



This page provides deep technical dives into specialized subsystems of the Bisheng platform. It covers implementation details of document processing, asynchronous task execution, vector storage strategies, component initialization patterns, and caching mechanisms. For general system architecture, see [System Architecture](#2). For development setup and deployment, see [Development and Deployment](#5).

## Document Processing Pipeline

The document processing pipeline transforms uploaded files into searchable vector embeddings stored in both Milvus and Elasticsearch. The pipeline supports multiple file formats with specialized parsing strategies.

### Pipeline Architecture

```mermaid
flowchart TD
    Upload["User uploads file<br/>(KnowledgeService)"]
    Store["save_knowledge_file()<br/>Store in MinIO + MySQL"]
    Queue["Celery task queued<br/>parse_knowledge_file_celery"]
    Status["Update status:<br/>WAITING → PROCESSING"]
    Download["Download from MinIO<br/>file_download()"]
    Parse["read_chunk_text()<br/>Parse and chunk"]
    Loader{File Type}
    ETL["Etl4lmLoader<br/>(PDF, images, OCR)"]
    MD["convert_file_to_md()<br/>(DOCX, XLSX, PPT)"]
    Direct["Direct Loaders<br/>(TXT, HTML, MD)"]
    Split["ElemCharacterTextSplitter<br/>Chunk generation"]
    Title["extract_title()<br/>LLM-based title extraction"]
    Metadata["Metadata enrichment<br/>(uploader, timestamps)"]
    Milvus["vector_client.add_texts()<br/>Milvus storage"]
    ES["es_client.add_texts()<br/>Elasticsearch storage"]
    Complete["Update status:<br/>SUCCESS or FAILED"]
    
    Upload --> Store
    Store --> Queue
    Queue --> Status
    Status --> Download
    Download --> Parse
    Parse --> Loader
    Loader -->|PDF, images| ETL
    Loader -->|DOCX, XLSX, PPT, HTML| MD
    Loader -->|TXT, MD| Direct
    ETL --> Split
    MD --> Split
    Direct --> Split
    Split --> Title
    Title --> Metadata
    Metadata --> Milvus
    Metadata --> ES
    Milvus --> Complete
    ES --> Complete
```

**Sources:** [src/backend/bisheng/api/services/knowledge_imp.py:789-960](), [src/backend/bisheng/api/services/knowledge.py:510-591](), [src/backend/bisheng/worker/knowledge/file_worker.py:274-333]()

### File Type Processing Matrix

| File Extension | Preprocessing | Parser | Special Handling |
|----------------|---------------|--------|------------------|
| `.pdf` | Damage check via `is_pdf_damaged()` | `Etl4lmLoader` with OCR | Force OCR option, formula extraction, header/footer filtering |
| `.docx` | Convert `.doc` → `.docx` via LibreOffice | `convert_file_to_md()` | Extract images to MinIO, replace original with fixed version |
| `.doc` | Convert to `.docx` | `convert_doc_to_docx()` | Upload `.docx` as preview file |
| `.xlsx`, `.xls`, `.csv` | N/A | `convert_file_to_md()` with `ExcelRule` | Header row config, slice length, append header option |
| `.ppt`, `.pptx` | Convert to PDF for preview | `convert_file_to_md()` | Upload PDF preview to MinIO |
| `.txt`, `.md` | N/A | `TextLoader` with autodetect encoding | Direct loading |
| `.html`, `.mhtml` | Convert to Markdown | `convert_file_to_md()` | Same as DOCX processing |

**Sources:** [src/backend/bisheng/api/services/knowledge_imp.py:789-960]()

### Text Chunking Strategy

The `ElemCharacterTextSplitter` class implements configurable text segmentation:

```mermaid
graph LR
    Input["Document text"]
    Separator["Apply separators<br/>(regex patterns)"]
    Rules["Apply separator_rule<br/>(conditional logic)"]
    Size["Enforce chunk_size<br/>(default: configurable)"]
    Overlap["Apply chunk_overlap<br/>(default: configurable)"]
    Chunks["Text chunks"]
    
    Input --> Separator
    Separator --> Rules
    Rules --> Size
    Size --> Overlap
    Overlap --> Chunks
```

Configuration parameters are stored in the `KnowledgeFile.split_rule` field as JSON:
- `separator`: List of regex patterns (e.g., `["\n\n", "\n", "。", "！", "？"]`)
- `separator_rule`: List of conditional rules
- `chunk_size`: Maximum characters per chunk
- `chunk_overlap`: Overlapping characters between chunks
- `retain_images`: Whether to preserve images (0/1)
- `enable_formula`: Whether to extract formulas (0/1)
- `force_ocr`: Force OCR on all content (0/1)
- `filter_page_header_footer`: Remove headers/footers (0/1)

**Sources:** [src/backend/bisheng/api/services/knowledge_imp.py:821-827]()

### LLM-Based Title Extraction

For each chunk, the system optionally extracts a descriptive title using an LLM:

1. **LLM Selection**: `decide_knowledge_llm()` retrieves the configured model via `LLMService.get_knowledge_llm().extract_title_model_id`
2. **Title Generation**: `extract_title()` or `async_extract_title()` sends the chunk text to the LLM
3. **Post-processing**: `parse_document_title()` removes thinking model artifacts (``) and extracts code blocks if present
4. **Metadata Storage**: Title stored in `Metadata.bbox` field as structured data

**Sources:** [src/backend/bisheng/api/services/knowledge_imp.py:402-436](), [src/backend/bisheng/api/services/knowledge_imp.py:774-786]()

### Preview and Edit Workflow

Before final processing, users can preview and edit chunks:

1. **Preview Generation**: `get_preview_file_chunk()` parses file and caches chunks in Redis
   - Cache key format: `preview_file_chunk:{knowledge_id}:{md5_hash}`
   - Each chunk stored as hash field with text and metadata
   - Associated keys store parse type, file path, and OCR partitions
2. **Chunk Editing**: `update_preview_file_chunk()` modifies cached chunks
   - Updates text content
   - Updates bbox coordinates for OCR-processed files
3. **Deletion**: `delete_preview_file_chunk()` removes specific chunks from cache
4. **Final Processing**: If preview cache exists, `add_file_embedding()` uses cached data instead of re-parsing

**Sources:** [src/backend/bisheng/api/services/knowledge.py:393-475](), [src/backend/bisheng/api/services/knowledge.py:477-508](), [src/backend/bisheng/api/services/knowledge_imp.py:603-665]()

### Metadata Schema

Each chunk is enriched with metadata conforming to `KNOWLEDGE_RAG_METADATA_SCHEMA`:

| Field | Type | Description |
|-------|------|-------------|
| `document_id` | int | Knowledge file ID |
| `knowledge_id` | int | Knowledge base ID |
| `document_name` | str | Original filename |
| `abstract` | str | LLM-generated title/summary |
| `bbox` | str | OCR bounding box coordinates (JSON) |
| `page` | int | Page number (for PDFs) |
| `upload_time` | int | Unix timestamp |
| `update_time` | int | Unix timestamp |
| `uploader` | str | Username who uploaded |
| `updater` | str | Username who last modified |
| `user_metadata` | dict | Custom key-value pairs |

Text and metadata are concatenated before vector storage using `aggregate_chunk_metadata()`:
```
{<file_title>filename</file_title>
<file_abstract>summary</file_abstract>
<paragraph_content>chunk text</paragraph_content>}
```

**Sources:** [src/backend/bisheng/api/services/knowledge_imp.py:96-102](), [src/backend/bisheng/api/services/knowledge_imp.py:637-660]()

## Asynchronous Task Processing

Bisheng uses two asynchronous execution systems: Celery for knowledge processing and a custom multi-process worker for Linsight workflows.

### Celery Worker Architecture

```mermaid
graph TB
    subgraph "Task Submission"
        API["FastAPI endpoint"]
        Delay["task.delay() call"]
    end
    
    subgraph "Redis Queue"
        Queue["Celery queue:<br/>default broker"]
    end
    
    subgraph "Worker Processes"
        W1["Worker 1<br/>bisheng-backend-worker"]
        W2["Worker 2"]
        WN["Worker N"]
    end
    
    subgraph "Task Handlers"
        Parse["parse_knowledge_file_celery<br/>(file_id, cache_key)"]
        Retry["retry_knowledge_file_celery<br/>(file_id, cache_key)"]
        Copy["file_copy_celery<br/>(source_id, target_id)"]
        Rebuild["rebuild_knowledge_celery<br/>(knowledge_id, model_id)"]
        QA["insert_qa_celery<br/>(qa_id)"]
    end
    
    subgraph "Resource Access"
        MySQL["MySQL:<br/>file status updates"]
        Milvus["Milvus:<br/>vector insertion"]
        ES["Elasticsearch:<br/>text indexing"]
        MinIO["MinIO:<br/>file download"]
    end
    
    API --> Delay
    Delay --> Queue
    Queue --> W1
    Queue --> W2
    Queue --> WN
    W1 --> Parse
    W1 --> Retry
    W2 --> Copy
    WN --> Rebuild
    WN --> QA
    Parse --> MySQL
    Parse --> Milvus
    Parse --> ES
    Parse --> MinIO
    Retry --> MySQL
    Copy --> Milvus
    Rebuild --> Milvus
    QA --> Milvus
```

**Sources:** [src/backend/bisheng/worker/knowledge/file_worker.py:1-374](), [src/backend/bisheng/worker/knowledge/rebuild_knowledge_worker.py:1-278]()

### Celery Task Definitions

#### parse_knowledge_file_celery

Processes a single uploaded file:

1. Retrieves file record from `KnowledgeFileDao.get_file_by_ids()`
2. Updates status to `PROCESSING` if currently `WAITING`
3. Extracts split rules from `KnowledgeFile.split_rule` JSON field
4. Calls `process_file_task()` to execute pipeline
5. Updates final status to `SUCCESS` or `FAILED`
6. Sends callback to `callback_url` if provided
7. Logs telemetry event via `telemetry_service.log_event_sync()`

**Task signature:** `parse_knowledge_file_celery(file_id: int, preview_cache_key: str, callback_url: str)`

**Sources:** [src/backend/bisheng/worker/knowledge/file_worker.py:274-292]()

#### retry_knowledge_file_celery

Retries failed file processing:

1. Calls `delete_knowledge_file_vectors()` to remove existing vectors (keeps MinIO files)
2. Re-executes `_parse_knowledge_file()` with same parameters
3. Handles preview cache if available

**Task signature:** `retry_knowledge_file_celery(file_id: int, preview_cache_key: str, callback_url: str)`

**Sources:** [src/backend/bisheng/worker/knowledge/file_worker.py:335-359]()

#### rebuild_knowledge_celery

Rebuilds entire knowledge base with new embedding model:

1. Queries all files with status `SUCCESS` or `REBUILDING`
2. Deletes Milvus collection via `delete_knowledge_file_in_vector()`
3. Updates file statuses to `REBUILDING`
4. Queries Elasticsearch for all chunks
5. Re-embeds each chunk with new model via `LLMService.get_bisheng_knowledge_embedding_sync()`
6. Inserts into Milvus via `vector_client.add_texts()`
7. Updates knowledge state to `PUBLISHED` or `FAILED`

**Task signature:** `rebuild_knowledge_celery(knowledge_id: int, new_model_id: int, invoke_user_id: int)`

**Sources:** [src/backend/bisheng/worker/knowledge/rebuild_knowledge_worker.py:22-106]()

#### file_copy_celery

Copies knowledge base files and vectors:

1. Iterates through source files in batches of 20
2. Creates new `KnowledgeFile` records with new IDs
3. Copies MinIO objects: source file, PDF conversion, bbox JSON, preview file
4. Queries source Milvus vectors by `document_id` and `knowledge_id`
5. Updates vector metadata with new IDs
6. Inserts into target Milvus collection and Elasticsearch index
7. Creates target collection/index if not exists

**Task signature:** `file_copy_celery(param: dict)` where `param` contains `source_knowledge_id`, `target_id`, `login_user_id`

**Sources:** [src/backend/bisheng/worker/knowledge/file_worker.py:25-165]()

### Linsight Worker Architecture

The Linsight system uses a custom multi-process worker pool with Redis-based task queue and node heartbeat mechanism.

```mermaid
graph TB
    subgraph "Task Submission"
        API["Linsight API"]
        QueuePush["LinsightQueue.put()<br/>session_version_id"]
    end
    
    subgraph "Redis Queue"
        Queue["linsight:queue<br/>(Redis list)"]
        Ownership["linsight:task:owner:{id}<br/>(task → node mapping)"]
        Heartbeat["linsight:node:heartbeat:{node_id}<br/>(TTL: 15s)"]
    end
    
    subgraph "Worker Processes"
        P1["ScheduleCenterProcess 1<br/>(max_concurrency: 32)"]
        P2["ScheduleCenterProcess 2"]
        PN["ScheduleCenterProcess N"]
    end
    
    subgraph "Process Components"
        Semaphore["asyncio.Semaphore<br/>(limits concurrency)"]
        HeartbeatTask["Heartbeat task<br/>(every 5s)"]
        NodeMgr["NodeManager<br/>(ownership tracking)"]
    end
    
    subgraph "Task Execution"
        TaskExec["LinsightWorkflowTask"]
        Agent["LinsightAgent<br/>(task generation & execution)"]
        StateManager["LinsightStateMessageManager<br/>(Redis state tracking)"]
    end
    
    API --> QueuePush
    QueuePush --> Queue
    Queue --> P1
    Queue --> P2
    Queue --> PN
    P1 --> Semaphore
    P1 --> HeartbeatTask
    P1 --> NodeMgr
    Semaphore --> TaskExec
    HeartbeatTask --> Heartbeat
    NodeMgr --> Ownership
    TaskExec --> Agent
    TaskExec --> StateManager
    StateManager --> Ownership
```

**Sources:** [src/backend/bisheng/linsight/worker.py:1-276](), [src/backend/bisheng/linsight/domain/task_exec.py:1-676]()

### NodeManager and Heartbeat System

The `NodeManager` class provides distributed node coordination:

**Initialization:**
- `node_id`: Generated as `{hostname}-{uuid[:8]}`
- `heartbeat_key`: `linsight:node:heartbeat:{node_id}`
- `interval`: 5 seconds between heartbeats
- `ttl`: 15 seconds Redis key expiration

**Key Methods:**

| Method | Purpose | Redis Operation |
|--------|---------|-----------------|
| `start_heartbeat()` | Maintains node liveness | `SETEX heartbeat_key "1" 15` every 5s |
| `register_task_ownership()` | Claims task ownership | `SETEX linsight:task:owner:{session_version_id} {node_id} 86400` |
| `release_task_ownership()` | Releases ownership | `DEL linsight:task:owner:{session_version_id}` |
| `is_node_alive()` | Checks target node health | `EXISTS linsight:node:heartbeat:{target_node_id}` |

**Sources:** [src/backend/bisheng/linsight/worker.py:20-69]()

### LinsightQueue Implementation

Custom Redis-backed queue using `RedisClient`:

```python
# Queue operations
await queue.put(session_version_id)           # RPUSH linsight:queue {id}
session_id = await queue.get_wait(timeout)    # BLPOP linsight:queue {timeout}
session_id = await queue.get_nowait()         # LPOP linsight:queue
size = await queue.qsize()                    # LLEN linsight:queue
position = await queue.index(session_id)      # LRANGE + search
await queue.remove(session_id)                # LREM linsight:queue 0 {id}
```

**Sources:** [src/backend/bisheng/linsight/worker.py:71-115]()

### ScheduleCenterProcess Execution Flow

Each worker process follows this lifecycle:

1. **Initialization:**
   - Create `asyncio.Semaphore(max_concurrency)` to limit concurrent tasks
   - Initialize `LinsightQueue` from Redis
   - Start `NodeManager.start_heartbeat()` background task

2. **Task Loop:**
   ```python
   while True:
       await semaphore.acquire()               # Block if at max concurrency
       session_version_id = await queue.get_wait()
       await node_manager.register_task_ownership(session_version_id)
       exec_task = LinsightWorkflowTask()
       task = asyncio.create_task(exec_task.async_run(session_version_id))
       task.add_done_callback(handle_task_result)  # Release semaphore when done
   ```

3. **Concurrency Control:**
   - Semaphore acquired before task start
   - Released in callback after task completion or error
   - Prevents process from accepting more tasks than configured limit

**Sources:** [src/backend/bisheng/linsight/worker.py:117-215]()

### Task Ownership and Failure Recovery

On worker startup, `check_and_terminate_incomplete_tasks()` recovers orphaned tasks:

1. Query all sessions with status `IN_PROGRESS` from database
2. For each session:
   - Check `linsight:task:owner:{session_id}` for owner node
   - If no owner or owner node heartbeat expired: mark as `FAILED`
3. Batch update session status and execution task status
4. Rollback invitation codes if enabled

This ensures tasks are cleaned up when worker processes crash.

**Sources:** [src/backend/bisheng/linsight/domain/utils.py:262-353]()

### LinsightWorkflowTask Lifecycle

The `LinsightWorkflowTask` class orchestrates document generation workflows:

```mermaid
stateDiagram-v2
    [*] --> Initialization
    Initialization --> StatusCheck: Check session status
    StatusCheck --> TerminationMonitor: Start monitor
    TerminationMonitor --> FileInit: Initialize file directory
    FileInit --> DownloadFiles: Download from MinIO
    DownloadFiles --> LLMInit: Get LLM instance
    LLMInit --> ToolInit: Initialize tools
    ToolInit --> AgentCreate: Create LinsightAgent
    AgentCreate --> TaskGen: Generate subtasks
    TaskGen --> TaskExec: Execute tasks
    TaskExec --> EventLoop: Process events
    EventLoop --> EventLoop: TaskStart, TaskEnd, ExecStep
    EventLoop --> UserInput: NeedUserInput
    UserInput --> WaitInput: Wait for user
    WaitInput --> EventLoop: Continue execution
    EventLoop --> FileUpload: Upload results to MinIO
    FileUpload --> Complete: Update session status
    Complete --> Cleanup: Delete local files
    Cleanup --> [*]
    
    StatusCheck --> AlreadyRunning: Already IN_PROGRESS
    AlreadyRunning --> [*]
    
    EventLoop --> Terminated: User terminates
    Terminated --> Cleanup
```

**Sources:** [src/backend/bisheng/linsight/domain/task_exec.py:49-676]()

Key implementation details:

**Resource Management:**
- Context manager `_managed_execution()` ensures cleanup
- File directory: `{CACHE_DIR}/linsight/{session_id[:8]}/`
- Termination monitor runs every 2 seconds checking session status
- Cleanup deletes local directory via `shutil.rmtree()`

**Task Execution:**
- Creates `LinsightAgent` with LLM, tools, and file directory
- Calls `agent.generate_task()` to get task list
- Saves tasks via `LinsightExecuteTaskDao.batch_create_tasks()`
- Executes via `agent.ainvoke()` async generator
- Concurrent execution of agent task and termination monitor

**Event Handling:**
- `GenerateSubTask`: Save additional subtasks to database
- `TaskStart`: Update status to `IN_PROGRESS`, push message
- `TaskEnd`: Update status to `SUCCESS`/`FAILED`, store result
- `NeedUserInput`: Wait for user input completion
- `ExecStep`: Add to task history, upload files to MinIO if needed

**Sources:** [src/backend/bisheng/linsight/domain/task_exec.py:105-371]()

## Vector Search and Retrieval

Bisheng implements hybrid search combining Milvus (vector similarity) and Elasticsearch (keyword matching).

### VectorStore Initialization

The `decide_vectorstores()` function initializes vector stores with environment-specific configuration:

```mermaid
graph TD
    Init["decide_vectorstores()<br/>(collection_name, vector_store, embedding)"]
    Type{vector_store type}
    
    Milvus["Milvus"]
    MilvusConf["settings.get_vectors_conf().milvus"]
    MilvusParams["collection_name<br/>embedding<br/>partition_key (if partition mode)"]
    MilvusClient["instantiate_vectorstore()<br/>Milvus class"]
    
    ES["ElasticKeywordsSearch"]
    ESConf["settings.get_vectors_conf().elasticsearch"]
    ESParams["index_name<br/>embedding<br/>ssl_verify"]
    ESClient["instantiate_vectorstore()<br/>ElasticKeywordsSearch class"]
    
    Init --> Type
    Type -->|"Milvus"| Milvus
    Type -->|"ElasticKeywordsSearch"| ES
    
    Milvus --> MilvusConf
    MilvusConf --> MilvusParams
    MilvusParams --> MilvusClient
    
    ES --> ESConf
    ESConf --> ESParams
    ESParams --> ESClient
```

**Milvus Configuration:**
```python
{
    "collection_name": str,           # or partition_{suffix} for partition mode
    "embedding": Embeddings,
    "partition_key": int,             # knowledge_id if partition mode
    "connection_args": {
        "host": str,
        "port": int,
        "user": str,
        "password": str
    }
}
```

**Elasticsearch Configuration:**
```python
{
    "index_name": str,
    "embedding": Embeddings,
    "es_url": str,
    "es_user": str,
    "es_password": str,
    "ssl_verify": bool                # eval() if string
}
```

**Sources:** [src/backend/bisheng/api/services/knowledge_imp.py:369-399]()

### KnowledgeRag Helper Class

The `KnowledgeRag` class provides factory methods for knowledge-specific vector stores:

| Method | Purpose | Key Parameters |
|--------|---------|----------------|
| `init_knowledge_milvus_vectorstore_sync()` | Initialize Milvus with metadata schemas | `knowledge_id`, `knowledge`, `metadata_schemas` |
| `init_knowledge_es_vectorstore_sync()` | Initialize Elasticsearch with metadata schemas | `knowledge_id`, `knowledge`, `metadata_schemas` |

Both methods:
1. Determine collection/index name from `Knowledge` model
2. Get embedding model via `LLMService.get_bisheng_knowledge_embedding_sync()`
3. Pass `metadata_schemas` to configure field types and indexing

**Sources:** References to `KnowledgeRag.init_knowledge_milvus_vectorstore_sync()` in [src/backend/bisheng/api/services/knowledge_imp.py:307-311](), [src/backend/bisheng/api/services/knowledge_imp.py:459-464]()

### Partition vs. Collection Mode

Milvus supports two collection strategies:

**Collection Mode** (prefix: `col`):
- One collection per knowledge base
- Collection name: `col{uuid}`
- Dropped entirely on delete: `col.drop()`

**Partition Mode** (prefix: `partition`):
- Shared collection across knowledge bases
- Partition key: `knowledge_id`
- Deletion by partition key: `col.delete(f"pk in {[...]}")`

Detection logic:
```python
if collection_name.startswith("col"):
    # Collection mode
    vector_client.col.drop()
else:
    # Partition mode - query by knowledge_id, then delete by pk
    pk = vector_client.col.query(expr=f'knowledge_id=="{knowledge_id}"', output_fields=["pk"])
    vector_client.col.delete(f"pk in {[p['pk'] for p in pk]}")
```

**Sources:** [src/backend/bisheng/api/services/knowledge.py:301-329]()

### Metadata Schema Configuration

The `KNOWLEDGE_RAG_METADATA_SCHEMA` constant defines field types and indexing:

```python
KNOWLEDGE_RAG_METADATA_SCHEMA = [
    {"name": "document_id", "type": "int", "index": True},
    {"name": "knowledge_id", "type": "int", "index": True},
    {"name": "document_name", "type": "str", "index": False},
    {"name": "abstract", "type": "str", "index": False},
    {"name": "bbox", "type": "str", "index": False},
    {"name": "page", "type": "int", "index": False},
    {"name": "upload_time", "type": "int", "index": True},
    {"name": "update_time", "type": "int", "index": True},
    {"name": "uploader", "type": "str", "index": False},
    {"name": "updater", "type": "str", "index": False},
]
```

Indexed fields support efficient filtering in vector queries.

**Sources:** [bisheng/common/constants/vectorstore_metadata.py]() (referenced in imports)

### Hybrid Search Strategy

Knowledge retrieval combines both vector stores:

1. **Milvus (Semantic Search):**
   - Vector similarity search via `col.query()` or `search()`
   - Filters by `knowledge_id` and `document_id` if needed
   - Returns top-k results by cosine similarity

2. **Elasticsearch (Keyword Search):**
   - Full-text search via `client.search()`
   - Supports term queries, match queries, filters
   - Query structure: `{"query": {"terms": {"metadata.document_id": [...]}}}`

Both stores maintain identical text content and metadata, enabling flexible retrieval strategies.

**Sources:** [src/backend/bisheng/api/services/knowledge_imp.py:301-324]()

### Vector Store Operations

**Insertion:**
```python
# Both stores accept same signature
texts = ["chunk1", "chunk2", ...]
metadatas = [{"document_id": 1, ...}, {"document_id": 1, ...}, ...]

vector_client.add_texts(texts=texts, metadatas=metadatas)  # Milvus
es_client.add_texts(texts=texts, metadatas=metadatas)      # Elasticsearch
```

**Deletion:**
```python
# Milvus: by document_id
vector_client.col.delete(expr=f"document_id in {file_ids}", timeout=10)

# Elasticsearch: by metadata field
es_client.client.delete_by_query(
    index=index_name,
    query={"terms": {"metadata.document_id": file_ids}}
)
```

**Sources:** [src/backend/bisheng/api/services/knowledge_imp.py:655-660](), [src/backend/bisheng/api/services/knowledge_imp.py:301-324]()

## Custom Component System

The component system provides a flexible framework for instantiating LangChain-compatible classes with frontend configuration.

### Component Initialization Flow

```mermaid
graph TD
    Frontend["Frontend node configuration"]
    API["API receives component config"]
    Route["instantiate_class() router"]
    Type{Component Type}
    
    LLM["LLM Components"]
    LLMService["LLMService.get_bisheng_llm()"]
    LLMModel["BaseChatModel instance"]
    
    Embed["Embedding Components"]
    EmbedService["LLMService.get_bisheng_knowledge_embedding_sync()"]
    EmbedModel["Embeddings instance"]
    
    Vector["VectorStore Components"]
    VectorInit["decide_vectorstores()"]
    VectorStore["Milvus or ElasticKeywordsSearch"]
    
    Generic["Other Components"]
    Import["import_by_type() or import_vectorstore()"]
    Instantiate["instantiate_llm() or instantiate_vectorstore()"]
    Instance["Component instance"]
    
    Frontend --> API
    API --> Route
    Route --> Type
    
    Type -->|LLM| LLM
    LLM --> LLMService
    LLMService --> LLMModel
    
    Type -->|Embeddings| Embed
    Embed --> EmbedService
    EmbedService --> EmbedModel
    
    Type -->|VectorStore| Vector
    Vector --> VectorInit
    VectorInit --> VectorStore
    
    Type -->|Other| Generic
    Generic --> Import
    Import --> Instantiate
    Instantiate --> Instance
```

**Sources:** [src/backend/bisheng/interface/initialize/loading.py]() (referenced in imports), [src/backend/bisheng/llm/domain/services.py]() (referenced in imports)

### LLM Service Integration

The `LLMService` class provides unified access to language models:

**Synchronous Methods:**
```python
# Get LLM for general use
llm = LLMService.get_bisheng_llm_sync(
    model_id=int,
    app_id=str,
    app_name=str,
    app_type=ApplicationTypeEnum,
    user_id=int
)

# Get LLM for knowledge processing (title extraction)
llm = LLMService.get_bisheng_llm_sync(
    model_id=knowledge_llm.extract_title_model_id,
    app_id=ApplicationTypeEnum.KNOWLEDGE_BASE.value,
    app_name=ApplicationTypeEnum.KNOWLEDGE_BASE.value,
    app_type=ApplicationTypeEnum.KNOWLEDGE_BASE,
    user_id=invoke_user_id
)
```

**Asynchronous Methods:**
```python
# Async LLM retrieval
llm = await LLMService.get_bisheng_llm(...)

# Async Linsight LLM
llm = await LLMService.get_bisheng_linsight_llm(
    invoke_user_id=int,
    model_id=int,
    temperature=float
)
```

Configuration retrieved via `LLMService.get_knowledge_llm()` returns model with `extract_title_model_id` field.

**Sources:** [src/backend/bisheng/api/services/knowledge_imp.py:402-436](), [src/backend/bisheng/linsight/domain/task_exec.py:188-197]()

### Embedding Service Integration

Embeddings are retrieved similarly to LLMs:

```python
# Synchronous embedding retrieval for knowledge base
embeddings = LLMService.get_bisheng_knowledge_embedding_sync(
    model_id=int,
    invoke_user_id=int
)

# Async embedding retrieval
embeddings = await LLMService.get_bisheng_knowledge_embedding()
```

The embedding model is used for:
- Initial file processing: converting chunks to vectors
- Knowledge base rebuilding: re-embedding with new model
- Query-time retrieval: embedding user questions

**Sources:** [src/backend/bisheng/worker/knowledge/rebuild_knowledge_worker.py:155-168]()

### FakeEmbedding Utility

The `FakeEmbedding` class provides a no-op embedding implementation for operations that don't require actual embeddings:

```python
from bisheng.interface.embeddings.custom import FakeEmbedding

# Used when only accessing vector store metadata, not embedding
embeddings = FakeEmbedding()
vector_client = decide_vectorstores(collection_name, "Milvus", embeddings)

# Can query/delete but not insert new vectors
vector_client.col.delete(expr=f"document_id in {file_ids}")
```

This pattern is used in:
- File deletion operations
- Knowledge base copying (vectors already embedded)
- Vector store inspection

**Sources:** [src/backend/bisheng/api/services/knowledge.py:303-306](), [src/backend/bisheng/worker/knowledge/file_worker.py:174-177]()

### instantiate_vectorstore Pattern

Generic vector store instantiation:

```python
from bisheng.interface.importing.utils import import_vectorstore
from bisheng.interface.initialize.loading import instantiate_vectorstore

# Import class
class_obj = import_vectorstore("Milvus")  # or "ElasticKeywordsSearch"

# Prepare parameters
param = {
    "embedding": embeddings,
    "collection_name": "partition_xxx",
    "partition_key": knowledge_id,
    **vector_config  # From settings.get_vectors_conf()
}

# Instantiate
vectorstore = instantiate_vectorstore("Milvus", class_object=class_obj, params=param)
```

The `instantiate_vectorstore()` function:
1. Validates parameters against class signature
2. Handles special cases (e.g., `ssl_verify` string → bool)
3. Returns initialized instance

**Sources:** [src/backend/bisheng/api/services/knowledge_imp.py:369-399]()

## Session Management and Caching

Bisheng uses Redis extensively for session state, graph caching, and distributed coordination.

### RedisClient Architecture

The `RedisClient` class abstracts Redis operations with support for multiple deployment modes:

```mermaid
graph TB
    Config["Redis Configuration"]
    Mode{Mode}
    
    Single["Single Instance"]
    SinglePool["ConnectionPool<br/>redis.StrictRedis"]
    
    Sentinel["Sentinel Mode"]
    SentinelHosts["sentinel_hosts list"]
    SentinelMaster["Sentinel.master_for()"]
    
    Cluster["Cluster Mode"]
    ClusterNodes["startup_nodes list"]
    ClusterClient["RedisCluster.from_url()"]
    
    Sync["Sync Methods:<br/>set, get, hset, hget, etc."]
    Async["Async Methods:<br/>aset, aget, ahset, ahget, etc."]
    
    Config --> Mode
    Mode --> Single
    Mode --> Sentinel
    Mode --> Cluster
    
    Single --> SinglePool
    Sentinel --> SentinelHosts
    SentinelHosts --> SentinelMaster
    Cluster --> ClusterNodes
    ClusterNodes --> ClusterClient
    
    SinglePool --> Sync
    SinglePool --> Async
    SentinelMaster --> Sync
    SentinelMaster --> Async
    ClusterClient --> Sync
    ClusterClient --> Async
```

**Configuration Examples:**

```python
# Single instance
redis_url = "redis://localhost:6379/0"

# Sentinel mode
redis_conf = {
    "mode": "sentinel",
    "sentinel_hosts": ["('host1', 26379)", "('host2', 26379)"],
    "sentinel_master": "mymaster",
    "sentinel_password": "pass",
    "password": "redis_pass"
}

# Cluster mode
redis_conf = {
    "mode": "cluster",
    "startup_nodes": [
        {"host": "node1", "port": 6379},
        {"host": "node2", "port": 6379}
    ]
}
```

**Sources:** [src/backend/bisheng/core/cache/redis_conn.py:18-56]()

### Core Redis Operations

The `RedisClient` provides unified sync/async methods:

| Operation | Sync Method | Async Method | Redis Command | Use Case |
|-----------|-------------|--------------|---------------|----------|
| Set value | `set(key, value, expiration)` | `aset(key, value, expiration)` | `SETEX` | Cache data with TTL |
| Get value | `get(key)` | `aget(key)` | `GET` | Retrieve cached data |
| Set if not exists | `setNx(key, value, expiration)` | `asetNx(key, value, expiration)` | `SETNX` + `EXPIRE` | Distributed locks |
| Hash set | `hset(name, key, value, mapping)` | `ahset(name, key, value, mapping)` | `HSET` | Store structured data |
| Hash get | `hget(name, key)` | `ahget(name, key)` | `HGET` | Retrieve hash field |
| Hash get all | `hgetall(name)` | `ahgetall(name)` | `HGETALL` | Get entire hash |
| Hash delete | `hdel(name, *keys)` | `ahdel(name, *keys)` | `HDEL` | Remove hash fields |
| Increment | `incr(key, expiration)` | `aincr(key, expiration)` | `INCR` | Counters |
| Delete | `delete(key)` | `adelete(key)` | `DEL` | Remove key |
| List push | `rpush(key, value, expiration)` | `arpush(key, value, expiration)` | `RPUSH` | Queue operations |
| Blocking pop | N/A | `ablpop(key, timeout)` | `BLPOP` | Queue consumption |
| List range | N/A | `alrange(key, start, end)` | `LRANGE` | Get list items |
| List remove | N/A | `alrem(key, value)` | `LREM` | Remove from queue |

All methods automatically pickle/unpickle Python objects.

**Sources:** [src/backend/bisheng/core/cache/redis_conn.py:57-430]()

### Preview Cache Implementation

Knowledge file preview uses Redis hash for chunk storage:

**Cache Structure:**
```
Key: preview_file_chunk:{knowledge_id}:{md5_hash}
Type: Hash
Fields:
  0: {"text": "chunk 0 text", "metadata": {...}}
  1: {"text": "chunk 1 text", "metadata": {...}}
  ...
  
Associated Keys:
  preview_file_chunk:{knowledge_id}:{md5_hash}_parse_type: "etl4lm" or "un_etl4lm"
  preview_file_chunk:{knowledge_id}:{md5_hash}_file_path: "share_url"
  preview_file_chunk:{knowledge_id}:{md5_hash}_partitions: {...}
```

**Operations:**

```python
# Save all chunks
cache_map = {index: {"text": text, "metadata": metadata}}
await KnowledgeUtils.async_save_preview_cache(cache_key, mapping=cache_map)

# Update single chunk
chunk_info = await KnowledgeUtils.async_get_preview_cache(cache_key, chunk_index)
chunk_info["text"] = new_text
await KnowledgeUtils.async_save_preview_cache(cache_key, chunk_index=chunk_index, value=chunk_info)

# Delete cache
KnowledgeUtils.delete_preview_cache(cache_key)  # Deletes all associated keys
```

**Sources:** [src/backend/bisheng/api/services/knowledge_imp.py:123-173](), [src/backend/bisheng/api/services/knowledge.py:414-475]()

### Linsight State Management

The `LinsightStateMessageManager` tracks workflow execution state in Redis:

**State Keys:**
```
linsight:session_version:{session_version_id}         # LinsightSessionVersion model
linsight:execution_tasks:{session_version_id}          # List of LinsightExecuteTask models
linsight:execution_task:{task_id}                      # Individual task details
linsight:message_queue:{session_version_id}            # Message queue for real-time updates
```

**State Operations:**

```python
state_mgr = LinsightStateMessageManager(session_version_id)

# Session version
await state_mgr.set_session_version_info(session_model)
session = await state_mgr.get_session_version_info()

# Execution tasks
await state_mgr.set_execution_tasks(tasks)
tasks = await state_mgr.get_execution_tasks()
task = await state_mgr.get_execution_task(task_id)

# Update task status
task_data = await state_mgr.update_execution_task_status(
    task_id=task_id,
    status=ExecuteTaskStatusEnum.IN_PROGRESS,
    result={"answer": "..."}
)

# Add execution step
await state_mgr.add_execution_task_step(task_id, step=exec_step_event)

# Push messages for real-time updates
await state_mgr.push_message(MessageData(
    event_type=MessageEventType.TASK_START,
    data=task_data
))
```

**Sources:** References to `LinsightStateMessageManager` in [src/backend/bisheng/linsight/domain/task_exec.py:70-675]()

### Graph Caching Pattern

Session service caches flow graphs to avoid rebuilding:

**Cache Key Pattern:**
```python
cache_key = f"session:{session_id}:graph"
```

**Usage:**
```python
# Check cache
cached_graph = await redis_client.aget(cache_key)
if cached_graph:
    return pickle.loads(cached_graph)

# Build and cache
graph = build_graph_from_flow()
await redis_client.aset(cache_key, graph, expiration=3600)
```

The graph includes:
- Compiled LangChain runnable
- Component instances (LLMs, embeddings, retrievers)
- Tool definitions
- Memory/state management

**Cache Invalidation:**
- On flow/skill update
- When configuration changes
- Manual deletion via API

**Sources:** Pattern inferred from Redis operations and SessionService references

### Batch Operations

Redis supports efficient batch operations via pipelining:

```python
# Sync pipeline
pipe = redis_client.pipeline(transaction=True)
for key, value in items:
    pipe.set(key, value)
    pipe.expire(key, 3600)
pipe.execute()

# Async pipeline
pipe = redis_client.async_pipeline(transaction=True)
for key, value in items:
    await pipe.set(key, value)
    await pipe.expire(key, 3600)
await pipe.execute()

# Bulk set with expiration
await redis_client.amset(mapping={"key1": val1, "key2": val2}, expiration=3600)

# Bulk get
values = await redis_client.amget(keys=["key1", "key2", "key3"])
```

**Sources:** [src/backend/bisheng/core/cache/redis_conn.py:135-194](), [src/backend/bisheng/core/cache/redis_conn.py:469-477]()

### Distributed Coordination Patterns

**Distributed Lock (Set if Not Exists):**
```python
lock_acquired = await redis_client.asetNx(f"lock:{resource_id}", "owner_id", expiration=30)
if lock_acquired:
    try:
        # Critical section
        pass
    finally:
        await redis_client.adelete(f"lock:{resource_id}")
```

**Task Ownership (with TTL):**
```python
# Register ownership
await redis_client.aset(f"task:owner:{task_id}", node_id, expiration=86400)

# Check owner
owner = await redis_client.aget(f"task:owner:{task_id}")

# Release ownership
await redis_client.adelete(f"task:owner:{task_id}")
```

**Heartbeat (node liveness):**
```python
# Send heartbeat
await redis_client.aset(f"node:heartbeat:{node_id}", "1", expiration=15)

# Check liveness
is_alive = await redis_client.aexists(f"node:heartbeat:{node_id}") > 0
```

**Sources:** [src/backend/bisheng/linsight/worker.py:40-68]()

---

# Page: Document Processing Pipeline

# Document Processing Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/backend/bisheng/api/services/knowledge.py](src/backend/bisheng/api/services/knowledge.py)
- [src/backend/bisheng/api/services/knowledge_imp.py](src/backend/bisheng/api/services/knowledge_imp.py)
- [src/backend/bisheng/worker/knowledge/file_worker.py](src/backend/bisheng/worker/knowledge/file_worker.py)
- [src/backend/bisheng/worker/knowledge/qa.py](src/backend/bisheng/worker/knowledge/qa.py)
- [src/backend/bisheng/worker/knowledge/rebuild_knowledge_worker.py](src/backend/bisheng/worker/knowledge/rebuild_knowledge_worker.py)
- [src/frontend/platform/src/components/bs-ui/select/hover.tsx](src/frontend/platform/src/components/bs-ui/select/hover.tsx)
- [src/frontend/platform/src/layout/MainLayout.tsx](src/frontend/platform/src/layout/MainLayout.tsx)
- [src/frontend/platform/src/pages/BuildPage/flow/FlowNode/component/KnowledgeSelectItem.tsx](src/frontend/platform/src/pages/BuildPage/flow/FlowNode/component/KnowledgeSelectItem.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/AdjustFilesUpload.tsx](src/frontend/platform/src/pages/KnowledgePage/AdjustFilesUpload.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/KnowledgeFile.tsx](src/frontend/platform/src/pages/KnowledgePage/KnowledgeFile.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/KnowledgeQa.tsx](src/frontend/platform/src/pages/KnowledgePage/KnowledgeQa.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/components/FileUploadStep2.tsx](src/frontend/platform/src/pages/KnowledgePage/components/FileUploadStep2.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/components/FileUploadStep4.tsx](src/frontend/platform/src/pages/KnowledgePage/components/FileUploadStep4.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/components/Files.tsx](src/frontend/platform/src/pages/KnowledgePage/components/Files.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/components/Header.tsx](src/frontend/platform/src/pages/KnowledgePage/components/Header.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/components/Paragraphs.tsx](src/frontend/platform/src/pages/KnowledgePage/components/Paragraphs.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/components/PreviewFile.tsx](src/frontend/platform/src/pages/KnowledgePage/components/PreviewFile.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/components/PreviewParagraph.tsx](src/frontend/platform/src/pages/KnowledgePage/components/PreviewParagraph.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/components/PreviewResult.tsx](src/frontend/platform/src/pages/KnowledgePage/components/PreviewResult.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/components/RuleFile.tsx](src/frontend/platform/src/pages/KnowledgePage/components/RuleFile.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/components/RuleTable.tsx](src/frontend/platform/src/pages/KnowledgePage/components/RuleTable.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/detail.tsx](src/frontend/platform/src/pages/KnowledgePage/detail.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/filesUpload.tsx](src/frontend/platform/src/pages/KnowledgePage/filesUpload.tsx)
- [src/frontend/platform/src/pages/KnowledgePage/qas.tsx](src/frontend/platform/src/pages/KnowledgePage/qas.tsx)

</details>



## Purpose and Scope

This document details the document processing pipeline in Bisheng, which handles the complete lifecycle of file ingestion into knowledge bases. The pipeline encompasses file upload, parsing, text extraction, chunking, embedding generation, and storage in both vector (Milvus) and full-text (Elasticsearch) search engines.

For information about knowledge base creation and management, see [Knowledge Base Management](#3.1). For details on vector search and retrieval strategies, see [Vector Search and Retrieval](#6.3). For asynchronous task processing patterns, see [Asynchronous Task Processing](#6.2).

---

## Pipeline Architecture Overview

The document processing pipeline follows a multi-stage architecture with clear separation between synchronous user interactions and asynchronous background processing.

```mermaid
graph TB
    subgraph "Frontend Upload Flow"
        UI["FileUploadStep1<br/>File Selection"]
        STEP2["FileUploadStep2<br/>Segmentation Config"]
        PREVIEW["PreviewResult<br/>Chunk Preview"]
        SUBMIT["API Submission"]
    end
    
    subgraph "API Layer"
        SAVE["KnowledgeService.save_knowledge_file()"]
        PROCESS["KnowledgeService.process_knowledge_file()"]
    end
    
    subgraph "Storage Initialization"
        MINIO_UPLOAD["Upload to MinIO<br/>get_knowledge_file_object_name()"]
        DB_CREATE["Create KnowledgeFile Record<br/>Status: WAITING"]
    end
    
    subgraph "Async Processing"
        CELERY_QUEUE["Celery Task Queue"]
        WORKER["parse_knowledge_file_celery()"]
        PROCESS_TASK["process_file_task()"]
    end
    
    subgraph "Document Processing"
        READ_CHUNK["read_chunk_text()"]
        PARSE["Document Parsers<br/>Etl4lmLoader, PyPDFLoader, etc."]
        CHUNK["ElemCharacterTextSplitter"]
        TITLE["extract_title()<br/>LLM-based"]
    end
    
    subgraph "Vector Storage"
        ADD_EMBED["add_file_embedding()"]
        MILVUS["Milvus.add_texts()"]
        ES["ElasticKeywordsSearch.add_texts()"]
    end
    
    UI --> STEP2
    STEP2 --> PREVIEW
    PREVIEW --> SUBMIT
    SUBMIT --> SAVE
    SAVE --> MINIO_UPLOAD
    SAVE --> DB_CREATE
    SAVE --> PROCESS
    PROCESS --> CELERY_QUEUE
    CELERY_QUEUE --> WORKER
    WORKER --> PROCESS_TASK
    PROCESS_TASK --> READ_CHUNK
    READ_CHUNK --> PARSE
    PARSE --> CHUNK
    CHUNK --> TITLE
    TITLE --> ADD_EMBED
    ADD_EMBED --> MILVUS
    ADD_EMBED --> ES
```

**Sources:** [src/backend/bisheng/api/services/knowledge.py:511-565](), [src/backend/bisheng/api/services/knowledge_imp.py:252-298](), [src/backend/bisheng/worker/knowledge/file_worker.py:274-332]()

---

## File Upload and MinIO Storage

### Upload Flow and Storage Structure

The frontend manages a 4-step upload wizard that guides users through file selection, segmentation configuration, preview, and final submission. Files are temporarily stored with UUID-based names to avoid conflicts before being moved to permanent locations.

```mermaid
graph LR
    subgraph "Frontend Step 1"
        SELECT["File Selection<br/>filesUpload.tsx"]
        UUID_GEN["save_upload_file_original_name()<br/>Generate UUID filename"]
        TEMP_UPLOAD["Upload to MinIO tmp bucket"]
    end
    
    subgraph "API Processing"
        SAVE_FILE["process_one_file()"]
        CHECK_DUP["Check MD5 + filename<br/>KnowledgeFileDao.get_file_by_condition()"]
        COPY_TO_PERM["Copy to permanent bucket<br/>get_knowledge_file_object_name()"]
    end
    
    subgraph "MinIO Structure"
        TMP["tmp/{uuid}.{ext}"]
        ORIG["original/{file_id}.{ext}"]
        BBOX["partitions/{file_id}.json"]
        PREVIEW["preview/{file_id}.pdf/docx"]
    end
    
    SELECT --> UUID_GEN
    UUID_GEN --> TEMP_UPLOAD
    TEMP_UPLOAD --> SAVE_FILE
    SAVE_FILE --> CHECK_DUP
    CHECK_DUP --> COPY_TO_PERM
    COPY_TO_PERM --> ORIG
    COPY_TO_PERM --> BBOX
    COPY_TO_PERM --> PREVIEW
```

The system uses three storage path patterns defined in `KnowledgeUtils`:

| Path Type | Method | Format | Purpose |
|-----------|--------|--------|---------|
| **Original File** | `get_knowledge_file_object_name()` | `original/{file_id}.{ext}` | Source document storage |
| **BBox Data** | `get_knowledge_bbox_file_object_name()` | `partitions/{file_id}.json` | OCR bounding box metadata |
| **Preview File** | `get_knowledge_preview_file_object_name()` | `preview/{file_id}.pdf/docx` | Converted files for preview |
| **Images** | `get_knowledge_file_image_dir()` | `knowledge/images/{kb_id}/{doc_id}` | Extracted document images |

**Sources:** [src/backend/bisheng/api/services/knowledge.py:718-765](), [src/backend/bisheng/api/services/knowledge_imp.py:184-217](), [src/frontend/platform/src/pages/KnowledgePage/filesUpload.tsx:68-98]()

### Duplicate Detection Strategy

The system implements a two-level duplicate detection mechanism:

1. **Content-based**: MD5 hash comparison of file contents
2. **Name-based**: Filename matching within the same knowledge base

When a duplicate is detected, the file is uploaded to a temporary location with status `FAILED` and a remark indicating the conflict. Users can then choose to overwrite the existing file via the retry interface.

**Sources:** [src/backend/bisheng/api/services/knowledge.py:736-765]()

---

## Document Parsing Strategies

### Parser Selection Matrix

The system routes files to different parsers based on file type, with fallback strategies for unsupported formats:

```mermaid
graph TB
    FILE["Input File"]
    EXT_CHECK{{"File Extension"}}
    
    subgraph "Table Files"
        EXCEL["Excel/CSV<br/>xlsx, xls, csv"]
        MD_CONV["convert_file_to_md()<br/>pandas processing"]
        COMBINE["combine_multiple_md_files_to_raw_texts()"]
    end
    
    subgraph "Office Documents"
        OFFICE["Office Files<br/>doc, docx, ppt, pptx"]
        CONVERT["LibreOffice Conversion<br/>convert_doc_to_docx()<br/>convert_ppt_to_pptx()"]
        ETL_CONV["convert_file_to_md()<br/>via etl4lm"]
    end
    
    subgraph "Text Documents"
        TEXT["Text Files<br/>txt, md"]
        TEXT_LOADER["TextLoader<br/>autodetect_encoding"]
    end
    
    subgraph "Complex Documents"
        PDF["PDF/Images"]
        ETL4LM["Etl4lmLoader<br/>unstructured API"]
        OCR["OCR Processing<br/>force_ocr flag"]
        BBOX["Extract bboxes<br/>parse_partitions()"]
    end
    
    FILE --> EXT_CHECK
    EXT_CHECK -->|"xlsx,xls,csv"| EXCEL
    EXT_CHECK -->|"doc,docx,ppt,pptx"| OFFICE
    EXT_CHECK -->|"txt,md,html"| TEXT
    EXT_CHECK -->|"pdf,jpg,png"| PDF
    
    EXCEL --> MD_CONV --> COMBINE
    OFFICE --> CONVERT --> ETL_CONV
    TEXT --> TEXT_LOADER
    PDF --> ETL4LM --> OCR --> BBOX
```

**Sources:** [src/backend/bisheng/api/services/knowledge_imp.py:789-931]()

### Etl4lm Loader Configuration

For complex document types (PDF, images, unsupported formats), the system uses the `Etl4lmLoader` which connects to an external unstructured service:

```python
# Configuration from settings
etl4lm_settings = settings.get_knowledge().etl4lm
loader = Etl4lmLoader(
    file_name,
    input_file,
    unstructured_api_url=etl4lm_settings.url,
    ocr_sdk_url=etl4lm_settings.ocr_sdk_url,
    force_ocr=bool(force_ocr),
    enable_formular=bool(enable_formula),
    timeout=etl4lm_settings.timeout,
    filter_page_header_footer=bool(filter_page_header_footer),
    knowledge_id=knowledge_id,
)
```

The loader returns structured partitions with bounding box data for each text element, enabling precise location tracking and re-segmentation later.

**Sources:** [src/backend/bisheng/api/services/knowledge_imp.py:907-930]()

### Excel-Specific Processing

Excel files require special handling due to their tabular structure. The system converts them to Markdown format with configurable row slicing:

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `header_start_row` | 1 | First row of header |
| `header_end_row` | 1 | Last row of header |
| `slice_length` | 10 | Rows per chunk |
| `append_header` | true | Include header in each chunk |

**Sources:** [src/backend/bisheng/api/services/knowledge_imp.py:837-856](), [src/frontend/platform/src/pages/KnowledgePage/components/RuleTable.tsx:17-95]()

---

## Text Chunking and Segmentation

### ElemCharacterTextSplitter Architecture

The chunking system uses `ElemCharacterTextSplitter` which implements a sophisticated regex-based splitting strategy with position-aware rules:

```mermaid
graph TB
    INPUT["Document Text"]
    SPLITTER["ElemCharacterTextSplitter"]
    
    subgraph "Configuration"
        SEPS["separators: List[str]<br/>['\\n\\n', '\\n', ' ']"]
        RULES["separator_rule: List[str]<br/>['before', 'after', 'both']"]
        SIZE["chunk_size: int<br/>default: 1000"]
        OVERLAP["chunk_overlap: int<br/>default: 0"]
    end
    
    subgraph "Processing"
        REGEX["Compile regex patterns<br/>is_separator_regex=True"]
        SPLIT["Split by separators<br/>with position rules"]
        MERGE["Merge small chunks<br/>respect chunk_size"]
        META["Generate metadata<br/>chunk_index, page, bbox"]
    end
    
    INPUT --> SPLITTER
    SEPS --> SPLITTER
    RULES --> SPLITTER
    SIZE --> SPLITTER
    OVERLAP --> SPLITTER
    
    SPLITTER --> REGEX
    REGEX --> SPLIT
    SPLIT --> MERGE
    MERGE --> META
```

**Sources:** [src/backend/bisheng/api/services/knowledge_imp.py:821-827]()

### Separator Position Rules

The system supports three position rules for each separator:

- **`before`**: Split occurs before the separator (separator included in next chunk)
- **`after`**: Split occurs after the separator (separator included in current chunk)
- **`both`**: Split occurs around the separator (separator forms its own chunk)

This is visualized in the frontend with scissors emoji (✂️) to show cut positions:

```
before: ✂️\n\n  → cut before newlines
after: \n\n✂️   → cut after newlines
```

**Sources:** [src/frontend/platform/src/pages/KnowledgePage/components/Paragraphs.tsx:576-590]()

### Chunk Metadata Schema

Each chunk receives comprehensive metadata defined in `KNOWLEDGE_RAG_METADATA_SCHEMA`:

| Field | Type | Description |
|-------|------|-------------|
| `document_id` | int | File ID in database |
| `knowledge_id` | int | Knowledge base ID |
| `chunk_index` | int | Sequential chunk number |
| `document_name` | str | Original filename |
| `page` | int | Source page number |
| `bbox` | JSON | Bounding box coordinates |
| `upload_time` | int | Unix timestamp |
| `uploader` | str | Username |
| `user_metadata` | dict | Custom metadata fields |

**Sources:** [src/backend/bisheng/api/services/knowledge_imp.py:637-651]()

---

## LLM-Based Title Extraction

### Title Extraction Workflow

The system optionally enhances chunks with LLM-generated titles/summaries before storage. This is controlled by the `extract_title_model_id` configuration:

```mermaid
sequenceDiagram
    participant Chunk as Text Chunk
    participant Config as LLMService.get_knowledge_llm()
    participant LLM as decide_knowledge_llm()
    participant Extract as extract_title()
    participant Storage as Vector Storage
    
    Chunk->>Config: Check extract_title_model_id
    alt Title extraction enabled
        Config->>LLM: Get LLM instance<br/>model_id, user_id
        LLM->>Extract: invoke with chunk text
        Extract->>Extract: Parse title from response<br/>remove ` patterns
2. Extract code blocks if present (removes markdown code fences)
3. Strip extra whitespace

This ensures clean, usable titles even from verbose model outputs.

**Sources:** [src/backend/bisheng/api/services/knowledge_imp.py:774-786]()

---

## Vector Storage Architecture

### Dual Storage Strategy

The system implements a dual-storage approach for optimal retrieval performance:

```mermaid
graph TB
    subgraph "Input Processing"
        CHUNKS["Chunked Text + Metadata"]
        AGG["KnowledgeUtils.aggregate_chunk_metadata()<br/>Format: <file_title>...<paragraph_content>"]
    end
    
    subgraph "Milvus (Vector Similarity)"
        MILVUS_EMBED["Generate embeddings<br/>via configured embedding model"]
        MILVUS_STORE["Milvus.add_texts()<br/>Collection: partition_{kb_id} or col_{kb_id}"]
        MILVUS_INDEX["Vector Index<br/>IVF_FLAT / HNSW"]
    end
    
    subgraph "Elasticsearch (Keyword Search)"
        ES_STORE["ElasticKeywordsSearch.add_texts()<br/>Index: kb_{kb_id}"]
        ES_INDEX["Full-text Index<br/>BM25 scoring"]
    end
    
    subgraph "Metadata Storage"
        META_SCHEMA["KNOWLEDGE_RAG_METADATA_SCHEMA<br/>Document ID, Chunk Index, BBox, User Metadata"]
    end
    
    CHUNKS --> AGG
    AGG --> MILVUS_EMBED
    AGG --> ES_STORE
    MILVUS_EMBED --> MILVUS_STORE
    MILVUS_STORE --> MILVUS_INDEX
    ES_STORE --> ES_INDEX
    META_SCHEMA --> MILVUS_STORE
    META_SCHEMA --> ES_STORE
```

**Sources:** [src/backend/bisheng/api/services/knowledge_imp.py:654-660](), [src/backend/bisheng/api/services/knowledge_imp.py:96-102]()

### Collection Naming Conventions

The system supports two collection strategies:

1. **Partition Mode**: Single collection `partition_knowledge` with partition key = `knowledge_id`
2. **Individual Collections**: Separate collections `col_{uuid}` per knowledge base

The naming is determined by `settings.get_vectors_conf().milvus.is_partition` configuration.

**Sources:** [src/backend/bisheng/api/services/knowledge_imp.py:369-399]()

### Metadata Aggregation Format

Before storage, chunks are enriched with a structured format:

```
{<file_title>document_name</file_title>
<file_abstract>abstract_text</file_abstract>
<paragraph_content>chunk_text</paragraph_content>}
```

This format enables the retrieval system to provide rich context when returning search results.

**Sources:** [src/backend/bisheng/api/services/knowledge_imp.py:96-102]()

---

## Preview and Editing Workflow

### Real-Time Preview Architecture

The frontend provides real-time preview of segmentation results using Server-Sent Events (SSE) for streaming updates:

```mermaid
graph LR
    subgraph "Frontend Preview Request"
        BTN["Preview Button<br/>FileUploadStep2"]
        REQ["previewFileSplitApi()<br/>SSE endpoint"]
    end
    
    subgraph "Backend Processing"
        SSE["SSE Stream<br/>Event Types:<br/>processing, completed, error"]
        ASYNC["async_read_chunk_text()"]
        CACHE["Redis Cache<br/>preview_file_chunk:{kb_id}:{md5}"]
    end
    
    subgraph "Preview Display"
        PREVIEW["PreviewResult<br/>Shows chunks"]
        FILE_VIEW["PreviewFile<br/>PDF with bboxes"]
        PARA_VIEW["PreviewParagraph<br/>Editable chunks"]
    end
    
    BTN --> REQ
    REQ --> SSE
    SSE --> ASYNC
    ASYNC --> CACHE
    CACHE --> PREVIEW
    PREVIEW --> FILE_VIEW
    PREVIEW --> PARA_VIEW
```

**Sources:** [src/frontend/platform/src/pages/KnowledgePage/components/PreviewResult.tsx:94-152](), [src/frontend/platform/src/pages/KnowledgePage/components/FileUploadStep2.tsx:199-219]()

### BBox-Based Chunk Editing

For documents parsed with OCR (via Etl4lm), users can visually select text regions in the PDF preview to modify chunk boundaries:

1. **Label Selection**: Click bounding boxes in PDF viewer (`FileView` component)
2. **Label Activation**: Selected boxes become "active" labels
3. **Text Aggregation**: Active labels' text is concatenated respecting partition types (Title, Table, etc.)
4. **Chunk Update**: Modified text overwrites the chunk via `updatePreviewChunkApi()`

The label structure:

```typescript
{
  id: string,           // "{page}-{x1}-{y1}-{x2}-{y2}"
  page: number,         // PDF page number
  label: [x1,y1,x2,y2], // Bounding box coordinates
  active: boolean,      // Selected for current chunk
  text: string,         // OCR-extracted text
  type: string,         // "Title" | "Text" | "Table"
  part_id: number       // Partition group ID
}
```

**Sources:** [src/frontend/platform/src/pages/KnowledgePage/components/PreviewFile.tsx:169-205](), [src/frontend/platform/src/pages/KnowledgePage/components/ParagraphEdit.tsx:1-339]()

### Cache-Based Editing Flow

Preview data is cached in Redis using `KnowledgeUtils.get_preview_cache_key()` with format:

```
preview_file_chunk:{knowledge_id}:{file_md5}
```

When users submit the final file for processing, if cache data exists, it is used instead of re-parsing, preserving user edits.

**Sources:** [src/backend/bisheng/api/services/knowledge_imp.py:90-93](), [src/backend/bisheng/api/services/knowledge_imp.py:603-608]()

---

## Asynchronous Processing Architecture

### Celery Worker Task Flow

The system uses Celery for background file processing to avoid blocking the API:

```mermaid
sequenceDiagram
    participant API as FastAPI Endpoint
    participant KS as KnowledgeService
    participant DB as MySQL
    participant Queue as Redis Queue
    participant Worker as Celery Worker
    participant Storage as Milvus + ES
    
    API->>KS: process_knowledge_file()
    KS->>DB: Create KnowledgeFile<br/>status=WAITING
    KS->>Queue: parse_knowledge_file_celery.delay(file_id)
    KS-->>API: Return file list
    
    Queue->>Worker: Task picked up
    Worker->>DB: Update status=PROCESSING
    Worker->>Worker: read_chunk_text()<br/>Parse document
    Worker->>Worker: extract_title()<br/>Optional LLM call
    Worker->>Storage: add_texts() to Milvus
    Worker->>Storage: add_texts() to ES
    Worker->>DB: Update status=SUCCESS/FAILED
    
    Note over API,Storage: Frontend polls status via GET /api/v1/knowledge/file/{id}
```

**Sources:** [src/backend/bisheng/worker/knowledge/file_worker.py:274-332](), [src/backend/bisheng/api/services/knowledge.py:545-564]()

### Task Retry Logic

Failed files can be retried via `retry_knowledge_file_celery()` which:

1. Deletes existing vector data via `delete_knowledge_file_vectors()`
2. Re-processes the file with updated parameters
3. Preserves the original file in MinIO (no re-upload needed)

The retry API accepts file objects with updated `split_rule` configuration:

```python
{
    "file_objs": [
        {
            "id": file_id,
            "file_path": "tmp/uuid.pdf",
            "split_rule": {
                "separator": ["\\n\\n", "\\n"],
                "chunk_size": 1500,
                "chunk_overlap": 100
            }
        }
    ]
}
```

**Sources:** [src/backend/bisheng/worker/knowledge/file_worker.py:335-359](), [src/backend/bisheng/api/services/knowledge.py:634-694]()

### Status Tracking and Polling

File processing status follows this state machine:

```mermaid
stateDiagram-v2
    [*] --> WAITING: File uploaded
    WAITING --> PROCESSING: Worker picks up
    PROCESSING --> SUCCESS: Parsing complete
    PROCESSING --> FAILED: Parse error
    PROCESSING --> TIMEOUT: etl4lm timeout
    FAILED --> WAITING: User retries
    SUCCESS --> REBUILDING: Model change rebuild
    REBUILDING --> SUCCESS: Rebuild complete
    REBUILDING --> FAILED: Rebuild error
```

The frontend polls file status every 5 seconds when files are in `PROCESSING` or `WAITING` states.

**Sources:** [src/frontend/platform/src/pages/KnowledgePage/components/Files.tsx:127-135](), [src/backend/bisheng/knowledge/domain/models/knowledge_file.py:1-200]()

---

## Error Handling and Recovery

### Structured Error Codes

The system uses structured error codes defined in `bisheng.common.errcode.knowledge`:

| Error Code | Class | Trigger Condition |
|------------|-------|-------------------|
| `100301` | `KnowledgeFileEmptyError` | No text extracted from file |
| `100302` | `KnowledgeFileChunkMaxError` | Chunk exceeds 10,000 characters |
| `100303` | `KnowledgeFileDamagedError` | PDF corruption detected |
| `100304` | `KnowledgeEtl4lmTimeoutError` | Unstructured API timeout |
| `100305` | `KnowledgeExcelChunkMaxError` | Excel cell exceeds size limit |

Errors are serialized to JSON and stored in `KnowledgeFile.remark` field for display to users.

**Sources:** [src/backend/bisheng/api/services/knowledge_imp.py:498-518](), [src/backend/bisheng/common/errcode/knowledge.py:1-300]()

### Duplicate File Handling

When duplicate files are detected (by MD5 or filename), the system:

1. Uploads to temporary location: `tmp/{file_id}.{ext}`
2. Sets status to `FAILED` with remark: `{"new_name": "...", "old_name": "..."}`
3. Displays dialog with options: **Overwrite** or **Skip**
4. On overwrite: Calls `retryKnowledgeFileApi()` to move temp file to permanent location and re-process

**Sources:** [src/backend/bisheng/api/services/knowledge.py:749-765](), [src/frontend/platform/src/pages/KnowledgePage/filesUpload.tsx:217-275]()

### Cleanup on Deletion

When files are deleted during processing, the Celery worker detects missing records and cleans up orphaned vector data:

```python
db_file = KnowledgeFileDao.get_file_by_ids([file_id])
if not db_file:
    # File deleted during processing - cleanup vectors
    delete_vector_files([file_id], knowledge)
```

This ensures no orphaned data remains in Milvus or Elasticsearch.

**Sources:** [src/backend/bisheng/worker/knowledge/file_worker.py:286-292]()

---

## Configuration and Extensibility

### File Type Extension Points

To add support for new file types, implement the following:

1. **Add loader mapping** in `filetype_load_map` dictionary
2. **Add conversion logic** in `read_chunk_text()` for preprocessing
3. **Update frontend validation** in upload components

Example for new type:

```python
filetype_load_map = {
    "txt": TextLoader,
    "pdf": PyPDFLoader,
    "newtype": CustomNewTypeLoader,  # Add here
}
```

**Sources:** [src/backend/bisheng/api/services/knowledge_imp.py:75-82]()

### Segmentation Strategy Customization

The frontend provides a visual strategy builder (`FileUploadStep2`) with:

- **Predefined strategies**: Double newline, single newline
- **Custom strategies**: Regex-based with position rules
- **Per-file overrides**: Different strategies for different files in batch
- **Excel-specific**: Row-based slicing with header handling

All strategies are serialized to `KnowledgeFile.split_rule` as JSON for persistence.

**Sources:** [src/frontend/platform/src/pages/KnowledgePage/components/FileUploadStep2.tsx:75-109](), [src/frontend/platform/src/pages/KnowledgePage/components/RuleFile.tsx:1-450]()

### Embedding Model Configuration

The system retrieves embedding configuration from `LLMService.get_knowledge_llm()` which reads from database-stored settings. To change models:

1. Update via knowledge base settings dialog (frontend)
2. Triggers rebuild workflow via `rebuild_knowledge_celery()` task
3. Re-embeds all successful chunks with new model

**Sources:** [src/backend/bisheng/worker/knowledge/rebuild_knowledge_worker.py:22-106]()

---

# Page: Asynchronous Task Processing

# Asynchronous Task Processing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/backend/bisheng/api/services/knowledge.py](src/backend/bisheng/api/services/knowledge.py)
- [src/backend/bisheng/api/services/knowledge_imp.py](src/backend/bisheng/api/services/knowledge_imp.py)
- [src/backend/bisheng/core/cache/redis_conn.py](src/backend/bisheng/core/cache/redis_conn.py)
- [src/backend/bisheng/linsight/domain/task_exec.py](src/backend/bisheng/linsight/domain/task_exec.py)
- [src/backend/bisheng/linsight/domain/utils.py](src/backend/bisheng/linsight/domain/utils.py)
- [src/backend/bisheng/linsight/worker.py](src/backend/bisheng/linsight/worker.py)
- [src/backend/bisheng/worker/knowledge/file_worker.py](src/backend/bisheng/worker/knowledge/file_worker.py)
- [src/backend/bisheng/worker/knowledge/qa.py](src/backend/bisheng/worker/knowledge/qa.py)
- [src/backend/bisheng/worker/knowledge/rebuild_knowledge_worker.py](src/backend/bisheng/worker/knowledge/rebuild_knowledge_worker.py)

</details>



This document describes the asynchronous task processing architecture in Bisheng. The system employs two distinct patterns: a general-purpose Celery worker system for background tasks like file processing, and a specialized Redis-based queue system (`LinsightQueue`) for managing AI-driven workflow execution. Both systems coordinate through Redis for message brokering and state management.

For information about the Linsight AI Workbench feature that heavily utilizes async processing, see [Linsight AI Workbench](#3.4). For workflow execution details, see [Workflow Engine](#3.5).

## System Architecture Overview

Bisheng implements a dual-pattern asynchronous processing architecture to handle different types of workloads with varying requirements for concurrency, state management, and real-time feedback.

### Deployment Architecture

```mermaid
graph TB
    subgraph "Backend Services"
        API["FastAPI Backend<br/>bisheng-backend<br/>Port 7860"]
        WORKER["Celery Worker<br/>bisheng-backend-worker<br/>command: worker"]
        LINSIGHT_WORKER["Linsight Worker<br/>ScheduleCenterProcess<br/>worker.py"]
    end
    
    subgraph "Message Broker"
        REDIS["Redis<br/>Port 6379"]
        CELERY_QUEUE["Celery Queue<br/>Default"]
        LINSIGHT_QUEUE["Linsight Queue<br/>namespace:linsight"]
    end
    
    subgraph "State Storage"
        REDIS_STATE["Redis State<br/>linsight_tasks:*"]
        MYSQL_STATE["MySQL<br/>linsight_session_version<br/>linsight_execute_task"]
    end
    
    API -->|"enqueue_task()"| CELERY_QUEUE
    API -->|"queue.put()"| LINSIGHT_QUEUE
    
    WORKER -->|"poll"| CELERY_QUEUE
    LINSIGHT_WORKER -->|"get_wait()"| LINSIGHT_QUEUE
    
    CELERY_QUEUE -.->|"stored in"| REDIS
    LINSIGHT_QUEUE -.->|"stored in"| REDIS
    
    LINSIGHT_WORKER -->|"LinsightStateMessageManager"| REDIS_STATE
    LINSIGHT_WORKER -->|"sync"| MYSQL_STATE
    
    REDIS_STATE -.->|"cached from"| MYSQL_STATE
```

**Diagram: Asynchronous Task Processing Deployment**

Sources: [docker/docker-compose.yml:79-107](), [src/backend/bisheng/linsight/worker.py:18-62]()

The system runs three key processes:
- **API Backend**: Synchronous FastAPI server that enqueues tasks
- **Celery Worker**: General-purpose task worker for file processing and knowledge base operations
- **Linsight Worker**: Specialized worker pool for AI workflow execution with custom concurrency control

## Celery Worker System

The general-purpose Celery worker handles file processing, knowledge base operations, and other background tasks that don't require real-time streaming feedback.

### Configuration and Deployment

The Celery worker is deployed as a separate container (`bisheng-backend-worker`) using the same image as the backend but with a different entrypoint command.

| Configuration | Value | Description |
|--------------|-------|-------------|
| Container Name | `bisheng-backend-worker` | Separate container for worker processes |
| Image | `dataelement/bisheng-backend:v2.3.0-beta2` | Same image as backend API |
| Command | `sh entrypoint.sh worker` | Starts Celery worker mode |
| Broker | Redis (port 6379) | Message queue backend |
| Result Backend | Redis | Task result storage |

Sources: [docker/docker-compose.yml:79-107](), [src/backend/pyproject.toml:18]()

### Task Types

The Celery system handles knowledge base processing operations:

1. **File Parsing** (`parse_knowledge_file_celery`): Asynchronous document parsing and vectorization
2. **File Retry** (`retry_knowledge_file_celery`): Reprocessing failed or updated files
3. **Knowledge Base Rebuild** (`rebuild_knowledge_celery`): Batch re-embedding with new models
4. **File Deletion** (`delete_knowledge_file_celery`): Asynchronous vector cleanup
5. **Knowledge Copy** (`file_copy_celery`): Cross-knowledge-base file replication
6. **QA Operations** (`insert_qa_celery`, `copy_qa_knowledge_celery`, `rebuild_qa_knowledge_celery`): QA knowledge base management

**Knowledge File Processing Flow**

```mermaid
sequenceDiagram
    participant Client
    participant API as "KnowledgeService<br/>knowledge.py"
    participant DB as "MySQL"
    participant MinIO
    participant Celery as "file_worker.py"
    participant Worker as "parse_knowledge_file_celery"
    participant Milvus
    participant ES as "Elasticsearch"
    
    Client->>API: process_knowledge_file()
    API->>API: save_knowledge_file()
    API->>MinIO: Upload original file
    API->>DB: INSERT KnowledgeFile<br/>status=WAITING
    API->>Celery: parse_knowledge_file_celery.delay(file_id)
    API-->>Client: Return file list
    
    Worker->>DB: UPDATE status=PROCESSING
    Worker->>MinIO: Download file
    Worker->>Worker: read_chunk_text()
    Worker->>Worker: text splitting & chunking
    Worker->>Worker: extract_title() via LLM
    Worker->>MinIO: Upload bbox partitions
    Worker->>Milvus: add_texts()
    Worker->>ES: add_texts()
    Worker->>DB: UPDATE status=SUCCESS
```

**Diagram: Knowledge File Processing via Celery**

Sources: [src/backend/bisheng/api/services/knowledge.py:545-564](), [src/backend/bisheng/worker/knowledge/file_worker.py:275-292](), [src/backend/bisheng/api/services/knowledge_imp.py:252-298]()

### Celery Task Implementations

**File Parsing Task**

The `parse_knowledge_file_celery` task coordinates the complete file processing pipeline:

| Step | Function | Purpose |
|------|----------|---------|
| 1. Status Update | `KnowledgeFileDao.update_file_status()` | Set `PROCESSING` |
| 2. Download File | `file_download()` via MinIO | Retrieve uploaded file |
| 3. Parse Content | `read_chunk_text()` | Extract text, split chunks |
| 4. Title Extraction | `extract_title()` | LLM-based chunk summarization |
| 5. Vector Storage | `add_file_embedding()` | Insert to Milvus + ES |
| 6. Update Status | `KnowledgeFileDao.update()` | Set `SUCCESS` or `FAILED` |

Sources: [src/backend/bisheng/worker/knowledge/file_worker.py:275-332]()

**File Retry Task**

The `retry_knowledge_file_celery` task handles reprocessing:

```python
@bisheng_celery.task(acks_late=True)
def retry_knowledge_file_celery(file_id: int, preview_cache_key: str = None, callback_url: str = None):
    # Delete existing vectors without removing MinIO files
    delete_knowledge_file_vectors(file_ids=[file_id], clear_minio=False)
    
    # Reparse using cached preview data if available
    _parse_knowledge_file(file_id, preview_cache_key, callback_url)
```

This enables updating files without re-uploading when segmentation parameters change.

Sources: [src/backend/bisheng/worker/knowledge/file_worker.py:336-359]()

**Knowledge Base Rebuild Task**

The `rebuild_knowledge_celery` task re-embeds all files with a new embedding model:

| Phase | Operation | Details |
|-------|-----------|---------|
| 1. Vector Deletion | `delete_knowledge_file_in_vector()` | Clear Milvus collection |
| 2. File Retrieval | `get_files_by_multiple_status()` | Get `SUCCESS` files |
| 3. Status Update | `update_status_bulk()` | Mark as `REBUILDING` |
| 4. Re-embedding | `_rebuild_embeddings()` | Fetch from ES, re-embed to Milvus |
| 5. Status Finalization | `update_status_bulk()` | Set `SUCCESS` or `FAILED` |

The task preserves ES data (text chunks) while regenerating Milvus vectors with the new model.

Sources: [src/backend/bisheng/worker/knowledge/rebuild_knowledge_worker.py:23-106]()

**Copy Task**

The `file_copy_celery` task replicates knowledge bases:

```python
@bisheng_celery.task(acks_late=True)
def file_copy_celery(param: json) -> str:
    # Copy MySQL records
    # Copy MinIO files (original, bbox, preview)
    # Copy Milvus vectors
    # Copy ES documents
```

This supports knowledge base templates and version management.

Sources: [src/backend/bisheng/worker/knowledge/file_worker.py:26-84]()

## Linsight Queue System

The Linsight system implements a custom Redis-based queue for managing AI workflow execution. This specialized queue provides fine-grained control over concurrency and enables real-time task progress streaming.

### LinsightQueue Implementation

```mermaid
graph LR
    subgraph "Queue Operations"
        PUT["put(data)"]
        GET_WAIT["get_wait(timeout)"]
        INDEX["index(data)"]
        REMOVE["remove(data)"]
    end
    
    subgraph "Redis List"
        KEY["linsight:queue"]
        RPUSH["arpush()"]
        BLPOP["ablpop()"]
        LRANGE["alrange()"]
        LREM["alrem()"]
    end
    
    PUT -->|"enqueue"| RPUSH
    GET_WAIT -->|"dequeue blocking"| BLPOP
    INDEX -->|"find position"| LRANGE
    REMOVE -->|"delete item"| LREM
    
    RPUSH -.-> KEY
    BLPOP -.-> KEY
    LRANGE -.-> KEY
    LREM -.-> KEY
```

**Diagram: LinsightQueue Operations on Redis**

Sources: [src/backend/bisheng/linsight/worker.py:18-62]()

The `LinsightQueue` class wraps Redis list operations:

| Method | Redis Command | Purpose |
|--------|--------------|---------|
| `put(data)` | `RPUSH` | Add task to queue end |
| `get_wait(timeout)` | `BLPOP` | Blocking pop from queue head |
| `get_nowait()` | `LPOP` | Non-blocking pop |
| `index(data)` | `LRANGE` + search | Find task position for status API |
| `remove(data)` | `LREM` | Remove task (for cancellation) |

Sources: [src/backend/bisheng/linsight/worker.py:24-61]()

### Worker Process Architecture

The Linsight worker uses a multi-process architecture with per-process concurrency control and node heartbeat management:

```mermaid
graph TB
    MAIN["Main Process<br/>worker.py __main__"]
    NODE_MGR["NodeManager<br/>node_id={hostname}-{uuid}"]
    
    subgraph "Worker Pool"
        P1["ScheduleCenterProcess #1<br/>semaphore: max_concurrency"]
        P2["ScheduleCenterProcess #2<br/>semaphore: max_concurrency"]
        PN["ScheduleCenterProcess #N<br/>semaphore: max_concurrency"]
    end
    
    subgraph "Task Execution"
        T1["LinsightWorkflowTask<br/>session_version_id"]
        T2["LinsightWorkflowTask<br/>session_version_id"]
        TN["LinsightWorkflowTask<br/>session_version_id"]
    end
    
    subgraph "Redis Keys"
        HB1["linsight:node:heartbeat:{node_id}<br/>TTL=15s"]
        OWNER["linsight:task:owner:{session_id}<br/>node_id value"]
    end
    
    MAIN -->|"check_and_terminate_incomplete_tasks()"| NODE_MGR
    MAIN -->|"spawn"| P1
    MAIN -->|"spawn"| P2
    MAIN -->|"spawn"| PN
    
    P1 -->|"start_heartbeat()"| HB1
    P1 -->|"register_task_ownership()"| OWNER
    P1 -->|"asyncio.create_task()"| T1
    P2 -->|"asyncio.create_task()"| T2
    PN -->|"asyncio.create_task()"| TN
    
    T1 -.->|"semaphore.release()"| P1
    T2 -.->|"semaphore.release()"| P2
    TN -.->|"semaphore.release()"| PN
```

**Diagram: Worker Process and Concurrency Model with Node Management**

Sources: [src/backend/bisheng/linsight/worker.py:117-214](), [src/backend/bisheng/linsight/worker.py:20-69]()

**Key Components:**

1. **NodeManager**: Manages node heartbeat and task ownership
   - Heartbeat interval: 5 seconds
   - Heartbeat TTL: 15 seconds
   - Registers task ownership in Redis key `linsight:task:owner:{session_version_id}`

2. **ScheduleCenterProcess** (Process): Each worker process maintains its own event loop
   - Acquires semaphore before dequeuing tasks
   - Registers task ownership via `NodeManager.register_task_ownership()`
   - Releases semaphore on task completion via callback

3. **LinsightWorkflowTask**: Individual task executor with lifecycle management

Command-line configuration:
```bash
python -m bisheng.linsight.worker --worker_num 4 --max_concurrency 32
```

Sources: [src/backend/bisheng/linsight/worker.py:243-276]()

### Task Enqueueing

Tasks are enqueued via API endpoint:

```mermaid
sequenceDiagram
    participant Client
    participant API as "/workbench/start-execute"
    participant Queue as "LinsightQueue"
    participant Redis
    participant Worker as "ScheduleCenterProcess"
    
    Client->>API: POST start-execute
    API->>Queue: put(session_version_id)
    Queue->>Redis: RPUSH linsight:queue
    Redis-->>Queue: OK
    Queue-->>API: enqueued
    API-->>Client: 200 {message: "task started"}
    
    Worker->>Queue: get_wait()
    Queue->>Redis: BLPOP linsight:queue
    Redis-->>Queue: session_version_id
    Queue-->>Worker: session_version_id
    Worker->>Worker: LinsightWorkflowTask.async_run()
```

**Diagram: Task Enqueue and Dequeue Flow**

Sources: [src/backend/bisheng/api/v1/linsight.py:307-353](), [src/backend/bisheng/linsight/worker.py:88-118]()

The enqueue process at `start_execute_sop` endpoint:
1. Validates session version exists and permissions
2. Checks session is not already running
3. Adds `session_version_id` to queue via `queue.put()`
4. Creates SOP record in background task
5. Returns immediately to client

Sources: [src/backend/bisheng/api/v1/linsight.py:307-353]()

## Task State Management

The system implements dual-layer state management using Redis for real-time operations and MySQL for persistence.

### LinsightStateMessageManager

The `LinsightStateMessageManager` class provides a unified interface for state operations:

```mermaid
graph TB
    subgraph "State Manager Operations"
        SESSION["set_session_version_info()"]
        TASKS["set_execution_tasks()"]
        UPDATE["update_execution_task_status()"]
        INPUT["set_user_input()"]
        PUSH["push_message()"]
    end
    
    subgraph "Redis Keys"
        SESSION_KEY["linsight_tasks:{id}:<br/>session_version_info"]
        TASKS_KEY["linsight_tasks:{id}:<br/>execution_tasks:{task_id}"]
        MSG_KEY["linsight_tasks:{id}:<br/>messages"]
    end
    
    subgraph "MySQL Tables"
        SESSION_TBL["linsight_session_version"]
        TASKS_TBL["linsight_execute_task"]
    end
    
    SESSION -->|"pickle.dumps()"| SESSION_KEY
    SESSION -->|"LinsightSessionVersionDao"| SESSION_TBL
    
    TASKS -->|"batch write"| TASKS_KEY
    UPDATE -->|"sync write"| TASKS_KEY
    UPDATE -->|"LinsightExecuteTaskDao"| TASKS_TBL
    
    INPUT -->|"update history"| TASKS_KEY
    INPUT -->|"update_by_id()"| TASKS_TBL
    
    PUSH -->|"RPUSH"| MSG_KEY
```

**Diagram: State Management Dual-Layer Architecture**

Sources: [src/backend/bisheng/linsight/state_message_manager.py:52-419]()

**Key Methods and Their Storage Patterns:**

| Method | Redis Operation | MySQL Operation | Purpose |
|--------|----------------|-----------------|---------|
| `set_session_version_info()` | `SET` with pickle | `LinsightSessionVersionDao.insert_one()` | Update session status |
| `set_execution_tasks()` | `MSET` batch write | N/A (already in DB) | Cache task list |
| `update_execution_task_status()` | `SET` single task | `LinsightExecuteTaskDao.update_by_id()` | Update task progress |
| `set_user_input()` | `SET` with pipeline | `update_by_id()` history field | Handle user interaction |
| `push_message()` | `RPUSH` to messages list | N/A (ephemeral) | Stream events to client |

Sources: [src/backend/bisheng/linsight/state_message_manager.py:139-310]()

### Message Event Types

The system defines typed events for streaming task progress:

```python
class MessageEventType(str, Enum):
    TASK_START = "task_start"
    TASK_GENERATE = "task_generate"
    TASK_STATUS_UPDATE = "task_status_update"
    USER_INPUT = "user_input"
    USER_INPUT_COMPLETED = "user_input_completed"
    TASK_EXECUTE_STEP = "task_execute_step"
    TASK_END = "task_end"
    ERROR_MESSAGE = "error_message"
    FINAL_RESULT = "final_result"
    TASK_TERMINATED = "task_terminated"
```

Sources: [src/backend/bisheng/linsight/state_message_manager.py:19-42]()

### State Synchronization Strategy

The dual-layer approach balances performance and durability:

1. **Redis Layer**:
   - Fast access for active tasks
   - Message queue for real-time streaming
   - TTL-based expiration (1 hour default)
   - Automatic fallback to DB on cache miss

2. **MySQL Layer**:
   - Persistent storage for task history
   - Session and task status records
   - User input and results
   - Query support for task list APIs

**Synchronization Points:**

```python
# Write to both layers atomically
async with self._redis_client.async_pipeline() as pipe:
    await LinsightSessionVersionDao.insert_one(session_version_model)
    await pipe.set(key, pickle.dumps(data), ex=expiration)
    await pipe.execute()
```

Sources: [src/backend/bisheng/linsight/state_message_manager.py:146-164]()

## Task Execution Lifecycle

The `LinsightWorkflowTask` class orchestrates the complete lifecycle of AI workflow execution.

### Execution Flow

```mermaid
stateDiagram-v2
    [*] --> Managed_Execution: async_run()
    
    Managed_Execution --> Check_Status: _managed_execution()
    Check_Status --> Initialize: Status OK
    Check_Status --> [*]: Already in progress
    
    Initialize --> Start_Monitor: _start_termination_monitor()
    Start_Monitor --> Init_Files: _init_file_directory()
    Init_Files --> Execute_Workflow: _execute_workflow()
    
    Execute_Workflow --> Update_Status: Set IN_PROGRESS
    Update_Status --> Init_LLM: _get_llm()
    Init_LLM --> Init_Tools: _generate_tools()
    Init_Tools --> Create_Agent: _create_agent()
    Create_Agent --> Generate_Tasks: agent.generate_task()
    Generate_Tasks --> Save_Tasks: _save_task_info()
    Save_Tasks --> Execute_Tasks: _execute_agent_tasks()
    
    Execute_Tasks --> Success: Task complete
    Execute_Tasks --> Terminated: User termination
    Execute_Tasks --> Failed: Exception
    
    Success --> Handle_Success: _handle_task_success()
    Terminated --> Handle_Termination: _handle_user_termination()
    Failed --> Handle_Error: _handle_execution_error()
    
    Handle_Success --> Cleanup: Upload files to MinIO
    Handle_Termination --> Cleanup: Set status TERMINATED
    Handle_Error --> Cleanup: Set status FAILED
    
    Cleanup --> [*]: _cleanup_resources()
```

**Diagram: LinsightWorkflowTask Execution State Machine**

Sources: [src/backend/bisheng/linsight/task_exec.py:106-164]()

### Resource Management

The task uses context managers for safe resource handling:

```python
async with self._managed_execution() as session_model:
    await self._execute_workflow(session_model)
```

**Managed Resources:**
1. **File Directory**: Downloaded files cached in `/cache/linsight/{session_id[:8]}`
2. **Termination Monitor**: Background task checking for user cancellation
3. **Code Interpreter Sandbox**: E2B sandbox for code execution (if configured)

Sources: [src/backend/bisheng/linsight/task_exec.py:67-102]()

### Event Handling During Execution

The task processes streaming events from the agent:

| Event Type | Handler Method | State Change |
|-----------|---------------|--------------|
| `GenerateSubTask` | `_handle_generate_subtask()` | Create child tasks in DB |
| `TaskStart` | `_handle_task_start()` | Update status to `IN_PROGRESS` |
| `TaskEnd` | `_handle_task_end()` | Update status to `SUCCESS`/`FAILED` |
| `NeedUserInput` | `_handle_need_user_input()` | Set status `WAITING_FOR_USER_INPUT` |
| `ExecStep` | `_handle_exec_step()` | Append step to history |

Sources: [src/backend/bisheng/linsight/task_exec.py:375-441]()

**Event Processing Loop:**

```python
async for event in agent.ainvoke(task_info, sop, file_list):
    await self._handle_event(agent, event, session_model)
```

The loop runs concurrently with a termination monitor that checks for user cancellation every 0.5 seconds.

Sources: [src/backend/bisheng/linsight/task_exec.py:319-327]()

### User Input Handling

Tasks can request user input mid-execution:

```mermaid
sequenceDiagram
    participant Agent as "LinsightAgent"
    participant Task as "LinsightWorkflowTask"
    participant State as "StateMessageManager"
    participant Redis
    participant WS as "WebSocket Client"
    participant User
    
    Agent->>Task: emit NeedUserInput
    Task->>State: add_execution_task_step()
    Task->>State: update_task_status(WAITING)
    State->>Redis: SET task status
    State->>Redis: RPUSH message
    State-->>WS: pop_message()
    WS->>User: Display input request
    
    User->>WS: Submit input + files
    WS->>API: POST /workbench/user-input
    API->>State: set_user_input()
    State->>Redis: UPDATE task history
    State->>Redis: SET status=COMPLETED
    
    loop Polling
        Task->>State: get_execution_task()
        State->>Redis: GET task
        alt Status == USER_INPUT_COMPLETED
            Task->>Task: Download files
            Task->>Agent: continue_task(user_input)
            Agent-->>Task: Resume execution
        else Still waiting
            Task->>Task: sleep(1)
        end
    end
```

**Diagram: User Input Request and Completion Flow**

Sources: [src/backend/bisheng/linsight/task_exec.py:427-495](), [src/backend/bisheng/api/v1/linsight.py:357-390]()

**Implementation Details:**

1. Agent emits `NeedUserInput` event with prompt
2. Task sets status to `WAITING_FOR_USER_INPUT`
3. Event streams to client via WebSocket
4. Client submits input via API endpoint
5. API updates Redis state
6. Task polls for completion (1-second intervals)
7. On completion, downloads any uploaded files
8. Agent resumes with user input

Sources: [src/backend/bisheng/linsight/task_exec.py:443-512]()

## Message Streaming

Real-time task progress is streamed to clients via WebSocket connections.

### WebSocket Connection Lifecycle

```mermaid
sequenceDiagram
    participant Client
    participant WS as "WebSocket Endpoint<br/>/task-message-stream"
    participant Handler as "MessageStreamHandle"
    participant State as "StateMessageManager"
    participant Redis
    
    Client->>WS: Connect with session_version_id
    WS->>Handler: MessageStreamHandle(ws, id)
    Handler->>State: initialize manager
    Handler->>Handler: await connect()
    
    loop Message Streaming
        Handler->>State: pop_message()
        State->>Redis: BLPOP messages
        Redis-->>State: MessageData
        State-->>Handler: MessageData
        Handler->>Handler: serialize to JSON
        Handler->>Client: ws.send_json()
    end
    
    alt Connection closed
        Client->>Handler: disconnect
        Handler->>Handler: cleanup
    end
    
    alt Timeout or error
        Handler->>Client: ws.close()
    end
```

**Diagram: WebSocket Message Streaming Architecture**

Sources: [src/backend/bisheng/api/v1/linsight.py:603-651]()

### Message Stream Handle Implementation

The `MessageStreamHandle` class (not shown in provided files but referenced) manages WebSocket connections:

**Key Operations:**
1. Establish WebSocket connection with authentication
2. Block on Redis list pop operations (`BLPOP`)
3. Deserialize `MessageData` objects
4. Stream JSON events to client
5. Handle connection errors and timeouts

**Message Format:**

```python
{
    "event_type": "task_execute_step",
    "data": {
        "task_id": "abc123",
        "name": "search_tool",
        "status": "end",
        "result": {...}
    },
    "timestamp": 1234567890.123
}
```

Sources: [src/backend/bisheng/api/v1/linsight.py:617-620](), [src/backend/bisheng/linsight/state_message_manager.py:45-49]()

### Event Streaming in API Layer

Some operations use Server-Sent Events (SSE) instead of WebSocket:

```python
async def event_generator():
    async for event in LinsightWorkbenchImpl.generate_sop(...):
        yield {
            "event": "generate_sop_content",
            "data": event.model_dump_json()
        }
    yield {
        "event": "sop_generate_complete",
        "data": json.dumps({"message": "Complete"})
    }

return EventSourceResponse(event_generator())
```

Sources: [src/backend/bisheng/api/v1/linsight.py:221-246]()

**Use Cases:**
- SOP generation streaming (SSE)
- Task execution progress (WebSocket)
- Question submission response (SSE)

## Task Termination and Cleanup

The system supports graceful task termination and automatic cleanup on restart.

### User-Initiated Termination

```python
# Remove from queue if not yet started
await queue.remove(session_version_id)

# Update session status
session_version_model.status = SessionVersionStatusEnum.TERMINATED

# Push termination message
await state_manager.push_message(MessageData(
    event_type=MessageEventType.TASK_TERMINATED,
    data={"message": "Task stopped by user"}
))
```

Sources: [src/backend/bisheng/api/v1/linsight.py:476-533]()

**Termination Detection:**

During execution, the task continuously monitors for user termination:

```python
async def _check_user_termination(self) -> bool:
    current_session = await self._state_manager.get_session_version_info()
    return current_session.status == SessionVersionStatusEnum.TERMINATED
```

This check runs every 2 seconds in a background coroutine.

Sources: [src/backend/bisheng/linsight/task_exec.py:547-558]()

### Startup Recovery

On worker startup, the system checks for incomplete tasks and validates node ownership:

```python
async def check_and_terminate_incomplete_tasks(node_id: str):
    # Get all IN_PROGRESS sessions
    incomplete_tasks = await LinsightSessionVersionDao.get_session_versions_by_status(
        status=SessionVersionStatusEnum.IN_PROGRESS
    )
    
    for session in incomplete_tasks:
        # Check task ownership in Redis
        owner_node_id = await redis_client.get(f"linsight:task:owner:{session.id}")
        
        if not owner_node_id:
            # No owner - mark as failed
            should_terminate = True
        else:
            # Check if owner node is alive via heartbeat
            is_alive = await node_manager.is_node_alive(owner_node_id)
            should_terminate = not is_alive
        
        if should_terminate:
            # Update session and tasks to FAILED
            # Revoke invitation codes if enabled
```

**Recovery Logic:**

| Scenario | Action | Reason |
|----------|--------|--------|
| No owner in Redis | Mark FAILED | Task was never claimed or Redis cleared |
| Owner node dead (no heartbeat) | Mark FAILED | Worker crashed or killed |
| Owner node alive | Skip | Task is actively processing |

Sources: [src/backend/bisheng/linsight/domain/utils.py:262-352](), [src/backend/bisheng/linsight/worker.py:264]()

This ensures orphaned tasks are cleaned up while preserving active work.

### Resource Cleanup

**Per-Task Cleanup:**
1. Stop termination monitor task
2. Close code interpreter sandbox
3. Delete temporary file directory
4. Release semaphore slot

**Global Cleanup:**
```python
async def cleanup_all_sessions():
    """Remove all linsight_tasks:* keys from Redis"""
    pattern = f"{KEY_PREFIX}*"
    keys = await redis.akeys(pattern)
    if keys:
        await redis.adelete(*keys)
```

Sources: [src/backend/bisheng/linsight/task_exec.py:91-102](), [src/backend/bisheng/linsight/state_message_manager.py:409-419]()

## Performance Considerations

### Concurrency Control

| Component | Concurrency Model | Default Limit | Configuration |
|-----------|------------------|---------------|---------------|
| Celery Worker | Process pool | Varies | Docker Compose deployment |
| Celery Task | `acks_late=True` | N/A | Prevents message loss |
| Linsight Worker Process | Asyncio Semaphore | 32 concurrent tasks | `--max_concurrency` flag |
| Linsight Worker Pool | Multi-process | 4 processes | `--worker_num` flag |
| Total Linsight Capacity | Workers × Semaphore | 128 concurrent tasks | Calculated |

**Celery Task Configuration:**

All knowledge processing tasks use `acks_late=True` to ensure tasks are requeued if the worker crashes before completion:

```python
@bisheng_celery.task(acks_late=True)
def parse_knowledge_file_celery(file_id: int, ...):
    # Task implementation
```

This prevents data loss at the cost of potential duplicate processing.

Sources: [src/backend/bisheng/worker/knowledge/file_worker.py:25](), [src/backend/bisheng/linsight/worker.py:189-196](), [src/backend/bisheng/linsight/worker.py:243-252]()

### Redis Key Expiration

**Cache TTLs:**
- Session version info: 3600 seconds (1 hour)
- Execution tasks: 3600 seconds (1 hour)
- Node heartbeat: 15 seconds (refreshed every 5 seconds)
- Task ownership: 86400 seconds (24 hours)
- Messages: No expiration (consumed via `BLPOP`)

**Heartbeat Mechanism:**

The `NodeManager` maintains node liveness through periodic heartbeat updates:

```python
async def start_heartbeat(self):
    while True:
        await self.redis.aset(self.heartbeat_key, "1", expiration=15)
        await asyncio.sleep(5)
```

If a worker crashes, its heartbeat expires after 15 seconds, allowing cleanup of orphaned tasks.

Sources: [src/backend/bisheng/linsight/worker.py:20-49](), [src/backend/bisheng/linsight/worker.py:51-60]()

### File Processing Optimization

File downloads use concurrent coroutines:

```python
download_tasks = [
    self._download_file(file_info, file_dir)
    for file_info in session_model.files
]
results = await asyncio.gather(*download_tasks, return_exceptions=True)
```

This parallelizes I/O operations across multiple files.

Sources: [src/backend/bisheng/linsight/task_exec.py:211-222]()

## Error Handling and Retry Patterns

### State Manager Retry Decorator

Critical Redis operations use automatic retry:

```python
@retry_async(num_retries=3, delay=1)
async def push_message(self, message: MessageData) -> None:
    await self._redis_client.arpush(self._keys['messages'], message.model_dump())
```

Sources: [src/backend/bisheng/linsight/state_message_manager.py:101-116]()

### Task Execution Error Handling

The task executor catches and categorizes exceptions:

| Exception Type | Handler | Result Status |
|---------------|---------|---------------|
| `UserTerminationError` | `_handle_user_termination()` | `TERMINATED` |
| `TaskAlreadyInProgressError` | Log warning | No change |
| `TaskExecutionError` | `_handle_execution_error()` | `FAILED` |
| `Exception` (any) | `_handle_execution_error()` | `FAILED` |

Sources: [src/backend/bisheng/linsight/task_exec.py:117-126]()

**Error Propagation:**

Errors are persisted and streamed:
```python
session_model.status = SessionVersionStatusEnum.FAILED
session_model.output_result = {"error_message": str(e)}
await state_manager.push_message(MessageData(
    event_type=MessageEventType.ERROR_MESSAGE,
    data={"error": str(e)}
))
```

Sources: [src/backend/bisheng/linsight/task_exec.py:636-652]()

---

# Page: Vector Search and Retrieval

# Vector Search and Retrieval

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [.github/workflows/release.yml](.github/workflows/release.yml)
- [.pre-commit-config.yaml](.pre-commit-config.yaml)
- [docker/bisheng/config/config.yaml](docker/bisheng/config/config.yaml)
- [src/backend/bisheng/api/services/chat_imp.py](src/backend/bisheng/api/services/chat_imp.py)
- [src/backend/bisheng/api/services/knowledge.py](src/backend/bisheng/api/services/knowledge.py)
- [src/backend/bisheng/api/services/knowledge_imp.py](src/backend/bisheng/api/services/knowledge_imp.py)
- [src/backend/bisheng/api/utils.py](src/backend/bisheng/api/utils.py)
- [src/backend/bisheng/api/v1/endpoints.py](src/backend/bisheng/api/v1/endpoints.py)
- [src/backend/bisheng/database/base.py](src/backend/bisheng/database/base.py)
- [src/backend/bisheng/graph/vertex/base.py](src/backend/bisheng/graph/vertex/base.py)
- [src/backend/bisheng/initdb_config.yaml](src/backend/bisheng/initdb_config.yaml)
- [src/backend/bisheng/interface/chains/base.py](src/backend/bisheng/interface/chains/base.py)
- [src/backend/bisheng/interface/chains/custom.py](src/backend/bisheng/interface/chains/custom.py)
- [src/backend/bisheng/interface/initialize/loading.py](src/backend/bisheng/interface/initialize/loading.py)
- [src/backend/bisheng/interface/initialize/vector_store.py](src/backend/bisheng/interface/initialize/vector_store.py)
- [src/backend/bisheng/main.py](src/backend/bisheng/main.py)
- [src/backend/bisheng/processing/base.py](src/backend/bisheng/processing/base.py)
- [src/backend/bisheng/processing/process.py](src/backend/bisheng/processing/process.py)
- [src/backend/bisheng/services/session/service.py](src/backend/bisheng/services/session/service.py)
- [src/backend/bisheng/template/frontend_node/chains.py](src/backend/bisheng/template/frontend_node/chains.py)
- [src/backend/bisheng/template/frontend_node/embeddings.py](src/backend/bisheng/template/frontend_node/embeddings.py)
- [src/backend/bisheng/template/frontend_node/llms.py](src/backend/bisheng/template/frontend_node/llms.py)
- [src/backend/bisheng/template/frontend_node/vectorstores.py](src/backend/bisheng/template/frontend_node/vectorstores.py)
- [src/backend/bisheng/worker/knowledge/file_worker.py](src/backend/bisheng/worker/knowledge/file_worker.py)
- [src/backend/bisheng/worker/knowledge/qa.py](src/backend/bisheng/worker/knowledge/qa.py)
- [src/backend/bisheng/worker/knowledge/rebuild_knowledge_worker.py](src/backend/bisheng/worker/knowledge/rebuild_knowledge_worker.py)
- [src/backend/test/test_filelib.py](src/backend/test/test_filelib.py)

</details>



## Purpose and Scope

This document describes the vector search and retrieval mechanisms in the Bisheng platform, focusing on the hybrid search architecture that combines Milvus vector similarity search with Elasticsearch keyword search. It covers document indexing, retrieval strategies, reranking, and integration patterns with RAG (Retrieval-Augmented Generation) and agent systems.

For information about document processing and chunking before indexing, see [Document Processing Pipeline](#6.1). For knowledge base management and file upload, see [Knowledge Base Management](#3.1). For asynchronous task processing of indexing operations, see [Asynchronous Task Processing](#6.2).

## Hybrid Search Architecture

The Bisheng platform implements a dual-index architecture where documents are simultaneously indexed in both Milvus (for semantic vector search) and Elasticsearch (for keyword-based full-text search). This enables hybrid retrieval strategies that leverage both semantic similarity and exact keyword matching.

**Hybrid Retrieval Architecture**

```mermaid
graph TB
    Query[User Query]
    
    subgraph "Retrieval Layer"
        VectorSearch["Vector Search<br/>(Milvus)"]
        KeywordSearch["Keyword Search<br/>(Elasticsearch)"]
        Rerank["Optional Reranking<br/>(Rerank Model)"]
    end
    
    subgraph "Storage Layer"
        MilvusDB[(Milvus Collection<br/>Vector Embeddings)]
        ESDB[(ES Index<br/>Text + Metadata)]
    end
    
    subgraph "Consumption"
        RAGNode["RagNode<br/>_run()"]
        AgentNode["AgentNode<br/>_init_knowledge_tools()"]
        QANode["QARetrieverNode<br/>_init_retriever()"]
    end
    
    Query --> VectorSearch
    Query --> KeywordSearch
    
    VectorSearch --> MilvusDB
    KeywordSearch --> ESDB
    
    VectorSearch --> Rerank
    KeywordSearch --> Rerank
    
    Rerank --> RAGNode
    Rerank --> AgentNode
    Rerank --> QANode
```

Sources: [src/backend/bisheng/workflow/nodes/rag/rag.py:22-197](), [src/backend/bisheng/workflow/nodes/agent/agent.py:160-188](), [src/backend/bisheng/workflow/nodes/qa_retriever/qa_retriever.py:11-72]()

## Vector Store Factory and Configuration

The `decide_vectorstores()` function serves as a factory for creating vector store instances, supporting both Milvus and Elasticsearch backends with configuration from the system settings.

**Vector Store Initialization Flow**

```mermaid
graph TB
    Factory["decide_vectorstores()<br/>knowledge_imp.py:367-397"]
    
    Config["settings.get_vectors_conf()"]
    
    Milvus["Milvus<br/>collection_name<br/>partition_key support"]
    ES["ElasticKeywordsSearch<br/>index_name<br/>ssl_verify"]
    
    Import["import_vectorstore()<br/>Dynamic Class Import"]
    Instantiate["instantiate_vectorstore()<br/>Create Instance"]
    
    Factory --> Config
    Factory --> Import
    Factory --> Instantiate
    
    Instantiate --> Milvus
    Instantiate --> ES
    
    style Factory fill:#f9f9f9
    style Milvus fill:#e1f5e1
    style ES fill:#e1e5f5
```

The factory function handles:
- **Milvus**: Collection naming, partition key configuration for multi-tenancy, embedding model compatibility
- **Elasticsearch**: Index naming, SSL verification, metadata schema validation

Sources: [src/backend/bisheng/api/services/knowledge_imp.py:367-397]()

| Parameter | Milvus Configuration | Elasticsearch Configuration |
|-----------|---------------------|----------------------------|
| Primary Identifier | `collection_name` | `index_name` |
| Multi-tenancy | `partition_key` (knowledge_id) | Not applicable |
| Connection | From `settings.get_vectors_conf().milvus` | From `settings.get_vectors_conf().elasticsearch` |
| Metadata | Vector embeddings + metadata | Text + metadata (no vectors) |

## Document Indexing Pipeline

When documents are processed and chunked, they are simultaneously indexed in both Milvus and Elasticsearch. The `add_file_embedding()` function orchestrates this dual-indexing process.

**Dual-Index Document Flow**

```mermaid
graph TB
    Process["add_file_embedding()<br/>knowledge_imp.py:541-680"]
    
    Parse["read_chunk_text()<br/>Parse & Chunk Document"]
    
    Metadata["Enrich Metadata<br/>document_id, knowledge_id<br/>upload_time, uploader"]
    
    AddMilvus["vector_client.add_texts()<br/>texts + metadatas"]
    AddES["es_client.add_texts()<br/>texts + metadatas"]
    
    MilvusCol[(Milvus Collection)]
    ESIndex[(ES Index)]
    
    Cache["Preview Cache<br/>KnowledgeUtils.get_preview_cache()"]
    
    Process --> Parse
    Parse --> Metadata
    
    Cache -.->|"If exists"| Metadata
    
    Metadata --> AddMilvus
    Metadata --> AddES
    
    AddMilvus --> MilvusCol
    AddES --> ESIndex
```

Sources: [src/backend/bisheng/api/services/knowledge_imp.py:541-680]()

Key aspects of the indexing process:

1. **Text Extraction**: Documents are parsed and split into chunks using `read_chunk_text()` [src/backend/bisheng/api/services/knowledge_imp.py:773-957]()

2. **Metadata Enrichment**: Each chunk receives metadata including:
   - `document_id`: File identifier
   - `knowledge_id`: Knowledge base identifier
   - `upload_time` and `update_time`: Timestamps
   - `uploader` and `updater`: User information
   - `bbox`: Optional OCR bounding box data for preview

3. **Dual Insertion**: Chunks are inserted into both stores:
   - **Milvus**: Stores text + vector embedding + metadata [src/backend/bisheng/api/services/knowledge_imp.py:650]()
   - **Elasticsearch**: Stores text + metadata (no embedding) [src/backend/bisheng/api/services/knowledge_imp.py:654]()

4. **Cache Integration**: If preview cache exists (user-edited chunks), those are used instead of freshly parsed chunks [src/backend/bisheng/api/services/knowledge_imp.py:600-609]()

## Milvus Vector Storage

Milvus stores high-dimensional vector embeddings generated from document chunks. The system supports both dedicated collections and partitioned collections for multi-tenancy.

**Milvus Collection Management**

```mermaid
graph TB
    Init["KnowledgeRag.init_knowledge_milvus_vectorstore_sync()<br/>knowledge_rag.py"]
    
    CollectionName["Collection Naming<br/>col_* or partition_*"]
    
    Partition["Partition Key Support<br/>knowledge_id as partition"]
    
    Schema["Metadata Schema<br/>KNOWLEDGE_RAG_METADATA_SCHEMA"]
    
    Operations["Collection Operations"]
    
    Insert["col.insert()<br/>Batch Insert Vectors"]
    Query["col.query()<br/>expr filter"]
    Delete["col.delete()<br/>expr filter"]
    Search["similarity_search()<br/>Vector Similarity"]
    
    Init --> CollectionName
    Init --> Partition
    Init --> Schema
    
    Schema --> Operations
    
    Operations --> Insert
    Operations --> Query
    Operations --> Delete
    Operations --> Search
```

Sources: [src/backend/bisheng/api/services/knowledge_imp.py:383-391](), [src/backend/bisheng/worker/knowledge/file_worker.py:161-221]()

### Collection Naming Strategies

The system uses two collection naming strategies:

1. **Dedicated Collections** (prefix `col_`): Each knowledge base gets its own collection
2. **Partitioned Collections** (prefix `partition_`): Multiple knowledge bases share a collection, differentiated by partition keys

This is determined during knowledge base creation [src/backend/bisheng/api/services/knowledge.py:177-179]():

```python
db_knowledge.index_name = generate_knowledge_index_name()
db_knowledge.collection_name = db_knowledge.index_name
```

### Vector Operations

Key Milvus operations used throughout the system:

| Operation | Usage | Example Location |
|-----------|-------|-----------------|
| `add_texts()` | Insert document chunks | [knowledge_imp.py:650]() |
| `query()` | Filtered retrieval by metadata | [file_worker.py:174-176]() |
| `delete()` | Remove documents by ID | [knowledge_imp.py:312]() |
| `similarity_search()` | Vector similarity retrieval | Through retriever interface |

### Partition Key Support

For partitioned collections, the `partition_key` is set to `knowledge_id` during initialization:

```python
if knowledge_id and collection_name.startswith("partition"):
    param["partition_key"] = knowledge_id
```

This enables efficient multi-tenant isolation within a shared collection [src/backend/bisheng/api/services/knowledge_imp.py:383-384]().

## Elasticsearch Full-Text Search

Elasticsearch provides keyword-based search capabilities, complementing Milvus vector search with exact term matching and filtering.

**Elasticsearch Index Structure**

```mermaid
graph TB
    ESClient["ElasticKeywordsSearch<br/>Vector Store"]
    
    Index["Index Structure<br/>index_name = collection_name"]
    
    Document["Document Schema<br/>text: chunk content<br/>metadata: document metadata"]
    
    Operations["ES Operations"]
    
    AddTexts["add_texts()<br/>Bulk Insert"]
    Search["search()<br/>Query DSL"]
    Delete["delete_by_query()<br/>Term/Match Queries"]
    Filter["as_retriever()<br/>search_kwargs filters"]
    
    ESClient --> Index
    Index --> Document
    Document --> Operations
    
    Operations --> AddTexts
    Operations --> Search
    Operations --> Delete
    Operations --> Filter
```

Sources: [src/backend/bisheng/api/services/knowledge_imp.py:315-320](), [src/backend/bisheng/worker/knowledge/file_worker.py:223-244]()

### Index Management

Elasticsearch indices are created with the same name as the knowledge base's `index_name` [src/backend/bisheng/api/services/knowledge.py:189-191]():

```python
es_client = KnowledgeRag.init_knowledge_es_vectorstore_sync(
    knowledge=db_knowledge, 
    metadata_schemas=KNOWLEDGE_RAG_METADATA_SCHEMA
)
es_client._store._create_index_if_not_exists()
```

### Search Capabilities

Elasticsearch provides:
- **Full-text search**: Tokenized search across document content
- **Metadata filtering**: Filter by `document_id`, `knowledge_id`, etc.
- **Scoring**: BM25 relevance scoring for keyword matches

Example deletion by query [src/backend/bisheng/api/services/knowledge_imp.py:315-320]():

```python
res = es_client.client.delete_by_query(
    index=knowledge.index_name,
    query={"terms": {"metadata.document_id": file_ids}},
)
```

## Hybrid Retrieval in RAG Nodes

The `RagNode` class implements hybrid retrieval by combining results from both Milvus vector search and Elasticsearch keyword search, with optional reranking.

**RAG Node Retrieval Flow**

```mermaid
graph TB
    RagNode["RagNode._run()<br/>workflow/nodes/rag/rag.py:56-73"]
    
    Init["init_multi_retriever()<br/>Initialize Milvus + ES"]
    
    Retrieve["retrieve_question()<br/>Hybrid Retrieval"]
    
    Milvus["Milvus Retriever<br/>Vector Similarity"]
    ES["ES Retriever<br/>Keyword Match"]
    
    Rerank["init_rerank_model()<br/>Optional Reranking"]
    
    Results["source_documents<br/>List[Document]"]
    
    Chain["create_stuff_documents_chain()<br/>LLM + Prompt + Context"]
    
    Answer["Final Answer"]
    
    RagNode --> Init
    Init --> Milvus
    Init --> ES
    
    RagNode --> Retrieve
    Retrieve --> Milvus
    Retrieve --> ES
    Retrieve --> Rerank
    
    Rerank --> Results
    Results --> Chain
    Chain --> Answer
```

Sources: [src/backend/bisheng/workflow/nodes/rag/rag.py:56-126]()

### Multi-Retriever Initialization

The RAG node extends `RagUtils` base class, which provides retriever initialization methods. The key retrievers are:

1. **Vector Retriever** (`self._milvus`): Initialized from Milvus collection
2. **Keyword Retriever** (`self._es`): Initialized from ES index  
3. **Rerank Model** (optional): Applied to combined results

Retriever configuration is based on:
- Knowledge base IDs or temporary file metadata
- Search parameters (top-k, score threshold)
- Metadata filtering expressions

### Question Retrieval Process

The `retrieve_question()` method (inherited from `RagUtils`) performs:

1. **Parallel Search**: Query both Milvus and ES simultaneously
2. **Result Merging**: Combine documents from both sources
3. **Deduplication**: Remove duplicate chunks if present
4. **Reranking**: Apply rerank model if configured
5. **Top-K Selection**: Return top results based on score

Retrieved documents include:
- `page_content`: The text chunk
- `metadata`: Document metadata (file name, page number, etc.)

### Integration with LLM Chain

Retrieved documents are passed to `create_stuff_documents_chain()` which constructs the final LLM prompt:

```python
qa_chain = create_stuff_documents_chain(llm=self._llm, prompt=self._qa_prompt)
inputs = {
    "context": source_documents,
    "question": question
}
result = qa_chain.invoke(inputs, config=RunnableConfig(callbacks=[llm_callback]))
```

Sources: [src/backend/bisheng/workflow/nodes/rag/rag.py:84-99]()

The prompt template allows referencing `{context}` for retrieved documents and `{question}` for the user query.

## Knowledge Tools in Agent Nodes

Agent nodes can access knowledge bases through specialized knowledge tools that wrap the retrieval functionality.

**Agent Knowledge Tool Initialization**

```mermaid
graph TB
    Agent["AgentNode._init_knowledge_tools()<br/>workflow/nodes/agent/agent.py:160-188"]
    
    KnowledgeType{"Knowledge Type"}
    
    KnowledgeDB["Knowledge Base<br/>ToolExecutor.init_knowledge_tool_sync()"]
    
    TempFile["Temporary File<br/>ToolExecutor.init_tmp_knowledge_tool_sync()"]
    
    VectorRet["init_file_milvus()<br/>Milvus Retriever"]
    ESRet["init_file_es()<br/>ES Retriever"]
    
    Tool["LangChain Tool<br/>name, description, retriever"]
    
    Agent --> KnowledgeType
    
    KnowledgeType -->|"type='knowledge'"| KnowledgeDB
    KnowledgeType -->|"type='temp_file'"| TempFile
    
    TempFile --> VectorRet
    TempFile --> ESRet
    
    VectorRet --> Tool
    ESRet --> Tool
    KnowledgeDB --> Tool
```

Sources: [src/backend/bisheng/workflow/nodes/agent/agent.py:160-188]()

### Knowledge Tool Types

Agents can use two types of knowledge tools:

1. **Persistent Knowledge Bases**: Standard knowledge bases from the system
   - Initialized via `ToolExecutor.init_knowledge_tool_sync()` [src/backend/bisheng/workflow/nodes/agent/agent.py:166-169]()
   - Includes pre-configured retrieval parameters

2. **Temporary File Knowledge**: Files uploaded within the workflow session
   - Requires separate Milvus and ES retriever initialization
   - Uses temporary collection with workflow-scoped partition key
   - File metadata provides document IDs for filtering

### Temporary File Retrieval

For temporary files, the agent node initializes retrievers with filtering expressions:

**Milvus Retriever** [src/backend/bisheng/workflow/nodes/agent/agent.py:190-199]():
```python
vector_client = KnowledgeRag.init_milvus_vectorstore(
    collection_name=collection_name, 
    embeddings=embeddings
)
return vector_client.as_retriever(
    search_kwargs={"expr": f'document_id in {file_ids}'}
)
```

**ES Retriever** [src/backend/bisheng/workflow/nodes/agent/agent.py:201-204]():
```python
es_client = KnowledgeRag.init_es_vectorstore_sync(index_name=self.tmp_collection_name)
return es_client.as_retriever(
    search_kwargs={"filter": [{"term": {"metadata.document_id": file_metadata['document_id']}}]}
)
```

This allows agents to access both persistent and session-specific knowledge within the same conversation.

## Temporary File Vector Storage

The `InputNode` handles file uploads within workflows and indexes them in temporary vector stores for downstream retrieval.

**Input Node File Processing**

```mermaid
graph TB
    Input["InputNode.parse_upload_file()<br/>workflow/nodes/input/input.py:174-259"]
    
    Parse["get_upload_file_path_content()<br/>Parse file chunks"]
    
    Embed["Default Embedding Model<br/>get_knowledge_default_embedding()"]
    
    Collection["Temporary Collection<br/>tmp_workflow_data_new_{model_id}"]
    
    InitMilvus["KnowledgeRag.init_milvus_vectorstore()<br/>collection_name + embeddings"]
    
    InitES["KnowledgeRag.init_es_vectorstore_sync()<br/>tmp_collection_name"]
    
    Metadata["Build Metadata<br/>document_id=file_id<br/>knowledge_id=workflow_id"]
    
    InsertMilvus["vector_client.add_texts()<br/>texts + metadatas"]
    InsertES["es_client.add_texts()<br/>texts + metadatas"]
    
    Input --> Parse
    Input --> Embed
    Input --> Collection
    
    Collection --> InitMilvus
    Collection --> InitES
    
    Parse --> Metadata
    Metadata --> InsertMilvus
    Metadata --> InsertES
```

Sources: [src/backend/bisheng/workflow/nodes/input/input.py:174-259]()

### Temporary Collection Naming

Temporary files use a special collection naming scheme that includes the embedding model ID:

```python
self.tmp_collection_name = 'tmp_workflow_data_new'
milvus_collection_name = self.get_milvus_collection_name(getattr(self._embedding, 'model_id'))
# Results in: tmp_workflow_data_new_{model_id}
```

This ensures that files embedded with different models are stored in separate collections, maintaining vector compatibility [src/backend/bisheng/workflow/nodes/input/input.py:188-189]().

### File Metadata Structure

Each uploaded file chunk receives metadata with workflow-scoped identifiers:

| Metadata Field | Value | Purpose |
|----------------|-------|---------|
| `document_id` | Generated UUID (shared per variable) | Group chunks from same upload variable |
| `document_name` | Original file name | Display and reference |
| `knowledge_id` | `workflow_id` | Partition key for multi-workflow isolation |
| `upload_time` | Current timestamp | Temporal tracking |
| `bbox` | Empty string | No OCR data for temp files |

Sources: [src/backend/bisheng/workflow/nodes/input/input.py:233-240]()

The `document_id` is shared across all files uploaded to the same input variable, allowing retrieval of all related documents with a single filter expression.

## QA Knowledge Retrieval

QA knowledge bases use a specialized retrieval mechanism for question-answer pairs, with dedicated Milvus collections and permission-aware retrievers.

**QA Retrieval Architecture**

```mermaid
graph TB
    QANode["QARetrieverNode._run()<br/>workflow/nodes/qa_retriever/qa_retriever.py:42-57"]
    
    Init["_init_retriever()<br/>Initialize QA Retriever"]
    
    Permission["MilvusWithPermissionCheck<br/>User-based Access Control"]
    
    Chain["RetrievalChain<br/>retriever wrapper"]
    
    Query["Question Input"]
    
    Search["similarity_search_with_score<br/>score_threshold"]
    
    Result["QA Document<br/>metadata.extra.answer"]
    
    Extract["Extract Answer<br/>from metadata"]
    
    QANode --> Init
    Init --> Permission
    Permission --> Chain
    
    QANode --> Query
    Query --> Chain
    Chain --> Search
    Search --> Result
    Result --> Extract
```

Sources: [src/backend/bisheng/workflow/nodes/qa_retriever/qa_retriever.py:11-72]()

### QA Collection Structure

QA knowledge bases store question-answer pairs as special documents where:
- The `text` field contains the question (for embedding/search)
- The `metadata.extra.answer` field contains the answer
- Access is controlled by user permissions via `MilvusWithPermissionCheck`

### QA Retriever Configuration

The QA retriever uses:
- **Collection Name**: Directly specified QA knowledge ID
- **Search Type**: `similarity_score_threshold`
- **Search Parameters**: `{'k': 1, 'score_threshold': user_configured_score}`
- **Permission Check**: Enabled via `_is_check_auth` parameter

Sources: [src/backend/bisheng/workflow/nodes/qa_retriever/qa_retriever.py:24-40]()

When a question is retrieved, the system:
1. Performs vector similarity search on questions
2. Filters by score threshold
3. Extracts answer from top result's metadata
4. Returns answer text or empty string if no match

The result document is also stored for source tracing: `self.graph_state.set_variable(self.id, '$retrieved_result$', result['result'][0])` [src/backend/bisheng/workflow/nodes/qa_retriever/qa_retriever.py:49]()

## Vector Store Rebuilding

When the embedding model changes, the system must rebuild vector stores by re-embedding all chunks while preserving the original text in Elasticsearch.

**Rebuild Process Flow**

```mermaid
graph TB
    Trigger["rebuild_knowledge_celery()<br/>rebuild_knowledge_worker.py:23-105"]
    
    GetFiles["Get SUCCESS Files<br/>KnowledgeFileDao.get_files_by_multiple_status()"]
    
    DeleteVectors["Delete Milvus Collection<br/>KnowledgeService.delete_knowledge_file_in_vector()"]
    
    UpdateStatus["Update Files to REBUILDING<br/>KnowledgeFileDao.update_status_bulk()"]
    
    ESQuery["Query ES for Chunks<br/>es_client.search()"]
    
    NewEmbed["New Embedding Model<br/>LLMService.get_bisheng_knowledge_embedding_sync()"]
    
    ReEmbed["_rebuild_embeddings()<br/>Process each file"]
    
    InsertMilvus["Insert New Vectors<br/>vector_client.add_texts()"]
    
    UpdateFiles["Update File Status<br/>SUCCESS or FAILED"]
    
    Trigger --> GetFiles
    GetFiles --> DeleteVectors
    DeleteVectors --> UpdateStatus
    UpdateStatus --> ESQuery
    UpdateStatus --> NewEmbed
    ESQuery --> ReEmbed
    NewEmbed --> ReEmbed
    ReEmbed --> InsertMilvus
    InsertMilvus --> UpdateFiles
```

Sources: [src/backend/bisheng/worker/knowledge/rebuild_knowledge_worker.py:22-257]()

### Rebuild Strategy

The rebuild process follows these steps:

1. **Preserve Text Data**: ES retains original text and metadata
2. **Delete Vectors Only**: Only Milvus collection is dropped [src/backend/bisheng/worker/knowledge/rebuild_knowledge_worker.py:50]()
3. **Batch Processing**: Files are processed in batches to prevent memory issues
4. **Re-embedding**: Each chunk is re-embedded with the new model
5. **Status Tracking**: Files track rebuild status (REBUILDING, SUCCESS, FAILED)

### Per-File Processing

For each file, the rebuild worker [src/backend/bisheng/worker/knowledge/rebuild_knowledge_worker.py:207-257]():

1. **Queries ES** for all chunks belonging to the file:
   ```python
   search_query = {
       "query": {"match": {"metadata.file_id": file.id}},
       "size": 10000
   }
   response = es_client.client.search(index=index_name, body=search_query)
   ```

2. **Extracts text and metadata** from ES results

3. **Removes pk field** from metadata to avoid conflicts

4. **Calls add_texts()** with new embedding model:
   ```python
   vector_client.add_texts(texts=texts, metadatas=metadatas)
   ```

This preserves all original metadata while updating only the vector embeddings.

## Metadata Schemas and Filtering

Both Milvus and Elasticsearch use structured metadata schemas defined by `KNOWLEDGE_RAG_METADATA_SCHEMA` for consistent filtering and retrieval.

### Standard Metadata Fields

| Field | Type | Purpose | Used In |
|-------|------|---------|---------|
| `document_id` | int | File identifier | Filtering specific files |
| `knowledge_id` | int/str | Knowledge base identifier | Multi-tenancy isolation |
| `document_name` | string | File name | Display and reference |
| `page` | int | Page number | Source tracking |
| `bbox` | JSON string | OCR bounding boxes | Preview highlighting |
| `upload_time` | int | Upload timestamp | Temporal filtering |
| `update_time` | int | Last update timestamp | Change tracking |
| `uploader` | string | Upload user | Audit trail |
| `updater` | string | Update user | Audit trail |
| `user_metadata` | dict | Custom metadata | Extensibility |

### Filter Expression Examples

**Milvus expr syntax** [src/backend/bisheng/worker/knowledge/file_worker.py:174-176]():
```python
expr = f"document_id=={source_file_id} && knowledge_id=={source_knowledge.id}"
source_data = source_milvus.col.query(expr=expr, output_fields=fields)
```

**Elasticsearch filter DSL** [src/backend/bisheng/workflow/nodes/agent/agent.py:203-204]():
```python
search_kwargs = {
    "filter": [{"term": {"metadata.document_id": file_metadata['document_id']}}]
}
```

These consistent metadata schemas enable precise filtering across both vector stores, supporting use cases like:
- Single file retrieval
- Knowledge base isolation
- User-scoped access control
- Temporal queries
- Cross-reference resolution

Sources: [src/backend/bisheng/api/services/knowledge_imp.py:637-645](), [src/backend/bisheng/workflow/nodes/input/input.py:233-240]()

---

# Page: Custom Component System

# Custom Component System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [.github/workflows/release.yml](.github/workflows/release.yml)
- [.pre-commit-config.yaml](.pre-commit-config.yaml)
- [docker/bisheng/config/config.yaml](docker/bisheng/config/config.yaml)
- [src/backend/bisheng/api/services/chat_imp.py](src/backend/bisheng/api/services/chat_imp.py)
- [src/backend/bisheng/api/utils.py](src/backend/bisheng/api/utils.py)
- [src/backend/bisheng/api/v1/endpoints.py](src/backend/bisheng/api/v1/endpoints.py)
- [src/backend/bisheng/database/base.py](src/backend/bisheng/database/base.py)
- [src/backend/bisheng/graph/vertex/base.py](src/backend/bisheng/graph/vertex/base.py)
- [src/backend/bisheng/initdb_config.yaml](src/backend/bisheng/initdb_config.yaml)
- [src/backend/bisheng/interface/chains/base.py](src/backend/bisheng/interface/chains/base.py)
- [src/backend/bisheng/interface/chains/custom.py](src/backend/bisheng/interface/chains/custom.py)
- [src/backend/bisheng/interface/initialize/loading.py](src/backend/bisheng/interface/initialize/loading.py)
- [src/backend/bisheng/interface/initialize/vector_store.py](src/backend/bisheng/interface/initialize/vector_store.py)
- [src/backend/bisheng/main.py](src/backend/bisheng/main.py)
- [src/backend/bisheng/processing/base.py](src/backend/bisheng/processing/base.py)
- [src/backend/bisheng/processing/process.py](src/backend/bisheng/processing/process.py)
- [src/backend/bisheng/services/session/service.py](src/backend/bisheng/services/session/service.py)
- [src/backend/bisheng/template/frontend_node/chains.py](src/backend/bisheng/template/frontend_node/chains.py)
- [src/backend/bisheng/template/frontend_node/embeddings.py](src/backend/bisheng/template/frontend_node/embeddings.py)
- [src/backend/bisheng/template/frontend_node/llms.py](src/backend/bisheng/template/frontend_node/llms.py)
- [src/backend/bisheng/template/frontend_node/vectorstores.py](src/backend/bisheng/template/frontend_node/vectorstores.py)
- [src/backend/test/test_filelib.py](src/backend/test/test_filelib.py)

</details>



The Custom Component System provides a unified framework for instantiating, configuring, and extending AI components in Bisheng. It enables dynamic creation of LLMs, vector stores, embeddings, chains, agents, and other LangChain primitives from frontend configuration, while supporting custom implementations and permission-based filtering.

For information about how components are executed within workflows, see [Workflow Engine](#3.5). For details on session-level caching of instantiated components, see [Session Management and Caching](#6.5).

---

## System Architecture

The Custom Component System consists of three primary subsystems: the instantiation router (`instantiate_class`), frontend node configurators, and specialized initializers for each component type.

### Component Instantiation Flow

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI["Frontend Node Configuration"]
        PARAMS["Component Parameters"]
    end
    
    subgraph "Vertex Layer"
        VERTEX["Vertex._build()"]
        BUILD_PARAMS["_build_params()"]
    end
    
    subgraph "Instantiation Router"
        INST_CLASS["instantiate_class()"]
        CUSTOM_CHECK{"node_type in CUSTOM_NODES?"}
        IMPORT["import_by_type()"]
        INST_BASED["instantiate_based_on_type()"]
    end
    
    subgraph "Type-Specific Handlers"
        INST_LLM["instantiate_llm()"]
        INST_VECTOR["instantiate_vectorstore()"]
        INST_EMB["instantiate_embedding()"]
        INST_CHAIN["instantiate_chains()"]
        INST_CUSTOM["instantiate_custom_component()"]
        INST_OTHERS["Other handlers..."]
    end
    
    subgraph "Specialized Initializers"
        VEC_INIT["vecstore_initializer"]
        MILVUS["initial_milvus()"]
        ELASTIC["initial_elastic()"]
        PERMISSION["Permission filtering"]
    end
    
    subgraph "Component Output"
        BUILT_OBJ["Built Component Object"]
        ARTIFACTS["Artifacts/Metadata"]
    end
    
    UI --> VERTEX
    PARAMS --> BUILD_PARAMS
    BUILD_PARAMS --> INST_CLASS
    
    INST_CLASS --> CUSTOM_CHECK
    CUSTOM_CHECK -->|"Yes"| BUILT_OBJ
    CUSTOM_CHECK -->|"No"| IMPORT
    IMPORT --> INST_BASED
    
    INST_BASED -->|"base_type='llms'"| INST_LLM
    INST_BASED -->|"base_type='vectorstores'"| INST_VECTOR
    INST_BASED -->|"base_type='embeddings'"| INST_EMB
    INST_BASED -->|"base_type='chains'"| INST_CHAIN
    INST_BASED -->|"base_type='custom_components'"| INST_CUSTOM
    INST_BASED -->|"Others"| INST_OTHERS
    
    INST_VECTOR --> VEC_INIT
    VEC_INIT --> MILVUS
    VEC_INIT --> ELASTIC
    MILVUS --> PERMISSION
    ELASTIC --> PERMISSION
    
    INST_LLM --> BUILT_OBJ
    INST_VECTOR --> BUILT_OBJ
    INST_EMB --> BUILT_OBJ
    INST_CHAIN --> BUILT_OBJ
    INST_CUSTOM --> BUILT_OBJ
    INST_OTHERS --> BUILT_OBJ
    PERMISSION --> BUILT_OBJ
    
    BUILT_OBJ --> ARTIFACTS
```

**Diagram: Component Instantiation Routing Architecture**

Sources: [src/backend/bisheng/interface/initialize/loading.py:58-147](), [src/backend/bisheng/graph/vertex/base.py:254-413]()

---

## Core Instantiation Framework

### Main Entry Point: instantiate_class

The `instantiate_class` function serves as the universal entry point for creating any component in Bisheng. It accepts a `node_type` (e.g., "ChatOpenAI", "Milvus"), a `base_type` (e.g., "llms", "vectorstores"), and parameters dict.

```mermaid
graph LR
    CALL["instantiate_class(node_type, base_type, params)"]
    CONVERT["convert_params_to_sets()"]
    KWARGS["convert_kwargs()"]
    EXTRACT["Extract NODE_ID_DICT"]
    CHECK{"node_type in CUSTOM_NODES?"}
    CUSTOM_INIT["custom_node.initialize()"]
    IMPORT["import_by_type()"]
    ROUTE["instantiate_based_on_type()"]
    
    CALL --> CONVERT
    CONVERT --> KWARGS
    KWARGS --> EXTRACT
    EXTRACT --> CHECK
    CHECK -->|"Yes"| CUSTOM_INIT
    CHECK -->|"No"| IMPORT
    IMPORT --> ROUTE
```

**Diagram: instantiate_class Function Flow**

Key operations:

| Step | Function | Purpose |
|------|----------|---------|
| 1 | `convert_params_to_sets()` | Converts string lists to Python sets for parameters like `allowed_special` |
| 2 | `convert_kwargs()` | Parses JSON strings in kwargs/config parameters |
| 3 | Extract `NODE_ID_DICT` | Maintains mapping of parameter keys to source node IDs |
| 4 | Check `CUSTOM_NODES` | Determines if component is a pre-registered custom node |
| 5 | `import_by_type()` | Dynamically imports the class from LangChain or bisheng_langchain |
| 6 | `instantiate_based_on_type()` | Routes to specialized instantiation handler |

Sources: [src/backend/bisheng/interface/initialize/loading.py:58-86]()

### Type-Based Routing

The `instantiate_based_on_type` function routes to specialized handlers based on `base_type`:

| Base Type | Handler Function | Purpose |
|-----------|------------------|---------|
| `agents` | `instantiate_agent()` | Creates AgentExecutor with tools |
| `prompts` | `instantiate_prompt()` | Builds prompt templates with partial variables |
| `tools` | `instantiate_tool()` | Creates tools with dynamic args_schema |
| `embeddings` | `instantiate_embedding()` | Initializes embedding models |
| `vectorstores` | `instantiate_vectorstore()` | Creates vector stores with permission filtering |
| `chains` | `instantiate_chains()` | Builds chains with retriever integration |
| `llms` | `instantiate_llm()` | Initializes LLMs with timeout/retry config |
| `custom_components` | `instantiate_custom_component()` | Evaluates and builds user-defined components |
| `memory` | `instantiate_memory()` | Creates memory objects with retriever support |

Sources: [src/backend/bisheng/interface/initialize/loading.py:99-147]()

---

## Frontend Node Configuration System

Frontend nodes define how components are configured in the UI. Each component type has a corresponding `FrontendNode` subclass that specifies fields, validation rules, and display properties.

### TemplateField Structure

Components are configured through `TemplateField` objects that define:

```
TemplateField(
    name='temperature',           # Parameter name
    field_type='float',           # Type (str, int, float, dict, code, etc.)
    required=True,                # Whether field is mandatory
    show=True,                    # Whether to display in UI
    advanced=False,               # Whether field is in advanced section
    value=0.7,                    # Default value
    display_name='Temperature',   # UI label
    password=False,               # Whether to mask input
    is_list=False,                # Whether accepts multiple values
    options=['a', 'b']            # Dropdown options (if applicable)
)
```

### LLM Frontend Node

The `LLMFrontendNode` class handles configuration for language models:

```mermaid
graph TB
    subgraph "LLMFrontendNode Processing"
        BASE["Base LLM Class"]
        FORMAT["format_field()"]
        OPENAI["format_openai_field()"]
        AZURE["format_azure_field()"]
        VERTEX["format_vertex_field()"]
        CONTRIB["format_contribute_field()"]
    end
    
    subgraph "Field Modifications"
        PROXY["openai_proxy: show=True"]
        TEMP["temperature: advanced=False"]
        KEY["api_key: password=True"]
        STREAM["streaming: show=True"]
        MODEL["model_name: show=True"]
    end
    
    subgraph "Special Cases"
        BISHENG["BishengLLM: model_id → bisheng_model"]
        TIMEOUT["Apply llm_request timeout config"]
        CACHE["Add cache field"]
    end
    
    BASE --> FORMAT
    FORMAT --> OPENAI
    FORMAT --> AZURE
    FORMAT --> VERTEX
    FORMAT --> CONTRIB
    
    OPENAI --> PROXY
    OPENAI --> KEY
    CONTRIB --> TEMP
    CONTRIB --> MODEL
    
    FORMAT --> STREAM
    FORMAT --> BISHENG
    FORMAT --> TIMEOUT
    FORMAT --> CACHE
```

**Diagram: LLM Frontend Node Field Processing**

Key features:

- **API Key Handling**: Automatically marks fields containing "api", "key", or "token" as password fields
- **BishengLLM Integration**: Converts `model_id` field type to `"bisheng_model"` for custom model selector [src/backend/bisheng/template/frontend_node/llms.py:223-231]()
- **Timeout Configuration**: Applies global `llm_request.request_timeout` and `max_retries` from `initdb_config.yaml` [src/backend/bisheng/interface/initialize/loading.py:281-290]()
- **Proxy Support**: Enables proxy configuration for OpenAI-compatible endpoints

Sources: [src/backend/bisheng/template/frontend_node/llms.py:10-231]()

### VectorStore Frontend Node

The `VectorStoreFrontendNode` handles configuration for vector databases with special handling for multi-knowledge-base scenarios:

```mermaid
graph TB
    subgraph "VectorStore Configuration"
        TYPE{"Vector Store Type"}
        MILVUS["MilvusWithPermissionCheck"]
        ELASTIC["ElasticsearchWithPermissionCheck"]
        STANDARD["Standard Vector Stores"]
    end
    
    subgraph "Permission Check Types"
        COL_TYPE["collection_name field_type"]
        SINGLE["'knowledge_one' (radio)"]
        MULTI["'knowledge_list' (multi-select)"]
    end
    
    subgraph "Extra Fields Added"
        SEARCH["search_kwargs (code)"]
        SEARCH_TYPE["search_type (str)"]
        PERSIST["persist (bool) - Chroma only"]
        FOLDER["folder_path (str) - FAISS only"]
    end
    
    TYPE --> MILVUS
    TYPE --> ELASTIC
    TYPE --> STANDARD
    
    MILVUS --> COL_TYPE
    ELASTIC --> COL_TYPE
    COL_TYPE --> MULTI
    
    STANDARD --> COL_TYPE
    COL_TYPE --> SINGLE
    
    MILVUS --> SEARCH
    ELASTIC --> SEARCH
    STANDARD --> SEARCH
    SEARCH --> SEARCH_TYPE
    
    STANDARD --> PERSIST
    STANDARD --> FOLDER
```

**Diagram: VectorStore Frontend Node Configuration**

**Special Handling for Permission-Checked Vector Stores**:

1. **MilvusWithPermissionCheck**: Changes `collection_name` field type to `"knowledge_list"` (multi-select) with `is_list=True` [src/backend/bisheng/template/frontend_node/vectorstores.py:347-350]()
2. **ElasticsearchWithPermissionCheck**: Uses `"knowledge_list"` for `index_name` field [src/backend/bisheng/template/frontend_node/vectorstores.py:352-362]()
3. Both hide embedding and documents fields from UI (handled during instantiation)

Sources: [src/backend/bisheng/template/frontend_node/vectorstores.py:7-400]()

### Chain Frontend Node

The `ChainFrontendNode` customizes fields for different chain types:

| Chain Type | Special Fields Added |
|------------|---------------------|
| `ConversationalRetrievalChain` | `memory` (BaseChatMemory), `return_source_documents` (bool), `chain_type` (dropdown), `document_prompt` (BasePromptTemplate) |
| `SequentialChain` | `chain_order` (str, array format) |
| `MultiPromptChain`, `MultiRuleChain` | `LLMChains` (list), `destination_chain_name` (dict mapping) |

Sources: [src/backend/bisheng/template/frontend_node/chains.py:9-176]()

---

## Component Initialization Patterns

### Direct Instantiation

Most components use direct class instantiation after parameter preparation:

```
# Example: Standard LLM instantiation
class_object = ChatOpenAI  # Imported via import_by_type
params = {'temperature': 0.7, 'model_name': 'gpt-3.5-turbo', ...}
llm = class_object(**params)
```

Sources: [src/backend/bisheng/interface/initialize/loading.py:253-291]()

### From-Method Initialization

Some components require initialization through class methods rather than constructors:

```mermaid
graph LR
    CHECK{"node_type in from_method_nodes?"}
    METHOD["Get method name from mapping"]
    CALL["class_object.method(**params)"]
    DIRECT["class_object(**params)"]
    
    CHECK -->|"Yes"| METHOD
    METHOD --> CALL
    CHECK -->|"No"| DIRECT
```

**Diagram: From-Method Initialization Pattern**

**Examples**:

| Component | Method Name | Source |
|-----------|-------------|--------|
| `APIChain` | `from_llm_and_api_docs` | [src/backend/bisheng/interface/chains/base.py:28]() |
| `ConversationalRetrievalChain` | `from_llm` | [src/backend/bisheng/interface/chains/base.py:29]() |
| `BishengRetrievalQA` | `from_llm` | [src/backend/bisheng/interface/chains/base.py:33]() |
| `CombineDocsChain` | `load_qa_chain` | [src/backend/bisheng/interface/chains/custom.py:105-128]() |

Sources: [src/backend/bisheng/interface/chains/base.py:27-36](), [src/backend/bisheng/interface/initialize/loading.py:380-385]()

### Custom Component Evaluation

User-defined custom components are instantiated through code evaluation:

```mermaid
sequenceDiagram
    participant Caller
    participant Handler as instantiate_custom_component()
    participant Eval as eval_custom_component_code()
    participant Custom as CustomComponent
    participant Build as component.build()
    
    Caller->>Handler: params with 'code' field
    Handler->>Eval: params['code']
    Eval->>Custom: Evaluated class
    Handler->>Custom: Instantiate with user_id
    Handler->>Custom: Check if build() is async
    alt Async build
        Handler->>Build: await build(**params)
    else Sync build
        Handler->>Build: build(**params)
    end
    Build-->>Handler: built_object
    Handler->>Custom: custom_repr()
    Handler-->>Caller: (built_object, {'repr': repr_str})
```

**Diagram: Custom Component Instantiation Sequence**

Key steps:
1. Extract `code` parameter from params
2. Evaluate code to get `CustomComponent` class
3. Instantiate with `user_id`
4. Detect if `build()` method is async using `inspect.iscoroutinefunction()`
5. Call `build()` appropriately (await if async)
6. Return built object with custom representation

Sources: [src/backend/bisheng/interface/initialize/loading.py:149-168]()

---

## Vector Store Initialization with Permission Checks

Vector stores have complex initialization logic that includes permission filtering and multi-collection support.

### Permission-Based Filtering Flow

```mermaid
graph TB
    subgraph "Input Parameters"
        COL_LIST["collection_name: [{key: kb_id}]"]
        USER["user_name"]
        CHECK_FLAG["_is_check_auth: bool"]
    end
    
    subgraph "Permission Filtering"
        EXTRACT["Extract knowledge_ids from collection_name"]
        PERM_CHECK{"_is_check_auth?"}
        WITH_PERM["KnowledgeDao.judge_knowledge_permission()"]
        NO_PERM["KnowledgeDao.get_list_by_ids()"]
        FILTER["Filtered knowledge_list"]
    end
    
    subgraph "Embedding Assignment"
        LOOP["For each knowledge in list"]
        GET_EMB["LLMService.get_bisheng_knowledge_embedding_sync()"]
        APPEND["Append to collection_embeddings"]
    end
    
    subgraph "Milvus-Specific"
        PART_CHECK{"collection_name starts with 'partition'?"}
        SET_PART["Set partition_keys[i] = knowledge.id"]
        SET_NONE["Set partition_keys[i] = None"]
    end
    
    COL_LIST --> EXTRACT
    USER --> EXTRACT
    CHECK_FLAG --> PERM_CHECK
    EXTRACT --> PERM_CHECK
    PERM_CHECK -->|"True"| WITH_PERM
    PERM_CHECK -->|"False"| NO_PERM
    WITH_PERM --> FILTER
    NO_PERM --> FILTER
    
    FILTER --> LOOP
    LOOP --> GET_EMB
    GET_EMB --> APPEND
    APPEND --> PART_CHECK
    PART_CHECK -->|"Yes"| SET_PART
    PART_CHECK -->|"No"| SET_NONE
```

**Diagram: Vector Store Permission Filtering Flow**

**MilvusWithPermissionCheck Initialization** [src/backend/bisheng/interface/initialize/loading.py:494-525]():

1. **Input**: `collection_name` parameter contains list of `{key: knowledge_id}` dicts
2. **Permission Check**: If `_is_check_auth=True`, calls `KnowledgeDao.judge_knowledge_permission(user_name, knowledge_ids)` to filter based on user permissions
3. **Embedding Assignment**: For each authorized knowledge base, fetches corresponding embedding model via `LLMService.get_bisheng_knowledge_embedding_sync(0, model_id=knowledge.model)`
4. **Partition Handling**: If collection name starts with "partition", sets `partition_keys[i] = knowledge.id` for partition-based filtering
5. **Fallback**: If no knowledge bases remain after filtering, uses `FakeEmbedding()` to prevent initialization errors

**ElasticsearchWithPermissionCheck**: Similar logic but uses `index_name` parameter instead of `collection_name` and doesn't require partition handling [src/backend/bisheng/interface/initialize/loading.py:526-529]()

Sources: [src/backend/bisheng/interface/initialize/loading.py:485-549]()

### Vector Store Initializer Registry

The `vecstore_initializer` dict maps vector store class names to custom initialization functions:

| Class Name | Initializer Function | Key Features |
|------------|---------------------|--------------|
| `Milvus` | `initial_milvus()` | Auto-loads connection_args from config, fetches embedding from knowledge base |
| `MilvusWithPermissionCheck` | `initial_milvus()` | Same as Milvus + permission filtering |
| `ElasticsearchStore` | `initial_elastic_vector()` | Supports connect_kwargs for credentials |
| `ElasticKeywordsSearch` | `initial_elastic()` | Keyword-based search, no embedding required |
| `ElasticsearchWithPermissionCheck` | `initial_elastic()` | Same as ElasticKeywordsSearch + permission filtering |
| `Pinecone` | `initialize_pinecone()` | Auto-retrieves API key from environment |
| `Chroma` | `initialize_chroma()` | Supports persistence flag |
| `FAISS` | `initialize_faiss()` | Supports local save/load |

Sources: [src/backend/bisheng/interface/initialize/vector_store.py:275-288]()

---

## LLM Configuration and Telemetry

### LLM Instantiation with Global Settings

```mermaid
graph TB
    subgraph "LLM Initialization"
        PARAMS["Input params"]
        PROXY_CHECK{"openai_proxy in params?"}
        HTTP_CLIENT["Create httpx Client with proxy"]
        VERTEX{"node_type == 'VertexAI'?"}
        VERTEX_INIT["initialize_vertexai()"]
        BISHENG{"node_type == 'BishengLLM'?"}
        INJECT["Inject app_id, app_name, app_type, user_id"]
        INSTANTIATE["class_object(**params)"]
    end
    
    subgraph "Global Config Application"
        LLM_OBJ["LLM Object"]
        GET_CONFIG["settings.get_from_db('llm_request')"]
        TIMEOUT{"'request_timeout' in config?"}
        SET_TIMEOUT["llm.request_timeout = config['request_timeout']"]
        RETRIES{"'max_retries' in config?"}
        SET_RETRIES["llm.max_retries = config['max_retries']"]
    end
    
    PARAMS --> PROXY_CHECK
    PROXY_CHECK -->|"Yes"| HTTP_CLIENT
    HTTP_CLIENT --> VERTEX
    PROXY_CHECK -->|"No"| VERTEX
    VERTEX -->|"Yes"| VERTEX_INIT
    VERTEX -->|"No"| BISHENG
    BISHENG -->|"Yes"| INJECT
    INJECT --> INSTANTIATE
    BISHENG -->|"No"| INSTANTIATE
    VERTEX_INIT --> INSTANTIATE
    
    INSTANTIATE --> LLM_OBJ
    LLM_OBJ --> GET_CONFIG
    GET_CONFIG --> TIMEOUT
    TIMEOUT -->|"Yes"| SET_TIMEOUT
    TIMEOUT -->|"No"| RETRIES
    SET_TIMEOUT --> RETRIES
    RETRIES -->|"Yes"| SET_RETRIES
```

**Diagram: LLM Configuration Pipeline**

**Configuration Sources**:

1. **Proxy Configuration**: If `openai_proxy` is provided, creates `httpx.Client` and `httpx.AsyncClient` with proxy settings [src/backend/bisheng/interface/initialize/loading.py:258-261]()

2. **Global Timeout/Retry Settings**: Applies settings from `initdb_config.yaml` under `llm_request` section:
   ```yaml
   llm_request:
     request_timeout: 600
     max_retries: 1
   ```
   Applied to LLM instances that have these attributes [src/backend/bisheng/interface/initialize/loading.py:281-290]()

3. **BishengLLM Telemetry**: Injects metadata for telemetry tracking:
   - `app_id`: "flow(will be deprecated)"
   - `app_name`: "flow(will be deprecated)"
   - `app_type`: `ApplicationTypeEnum.SKILL`
   - `user_id`: From params or default 0

Sources: [src/backend/bisheng/interface/initialize/loading.py:253-291](), [src/backend/bisheng/initdb_config.yaml:9-12]()

---

## Retriever and Chain Integration

### Retriever Wrapping with File Access Control

When `file_access` setting is configured, retrievers are wrapped with `VectorStoreFilterRetriever` to enforce document-level permissions:

```mermaid
graph TB
    subgraph "Chain with Retriever"
        PARAMS["params with 'retriever' key"]
        HAS_RETRIEVER{"'retriever' in params?"}
        HAS_METHOD{"retriever.as_retriever exists?"}
        FILE_ACCESS{"settings.get_from_db('file_access')?"}
        BUILD_URL["access_url = file_access + '?username=' + user_name"]
        WRAP["VectorStoreFilterRetriever(vectorstore, access_url)"]
        STANDARD["retriever.as_retriever()"]
        USE_DIRECT["Use retriever as-is"]
    end
    
    PARAMS --> HAS_RETRIEVER
    HAS_RETRIEVER -->|"Yes"| HAS_METHOD
    HAS_RETRIEVER -->|"No"| USE_DIRECT
    HAS_METHOD -->|"Yes"| FILE_ACCESS
    HAS_METHOD -->|"No"| USE_DIRECT
    FILE_ACCESS -->|"Configured"| BUILD_URL
    BUILD_URL --> WRAP
    FILE_ACCESS -->|"Not configured"| STANDARD
```

**Diagram: Retriever Wrapping for Access Control**

This pattern applies to:
- **Chain instantiation**: When chain has a retriever parameter [src/backend/bisheng/interface/initialize/loading.py:332-343]()
- **VectorStore as_retriever**: When converting vector store to retriever [src/backend/bisheng/interface/initialize/loading.py:538-548]()

The `VectorStoreFilterRetriever` makes HTTP requests to the configured `file_access` endpoint to verify user permissions for each retrieved document before returning results.

Sources: [src/backend/bisheng/interface/initialize/loading.py:332-343, 538-548]()

---

## Extension Points

### Adding Custom Nodes

Custom nodes can be registered in `CUSTOM_NODES` dict [src/backend/bisheng/interface/initialize/loading.py:63-68](). They must either:
1. Implement an `initialize()` classmethod
2. Be instantiable via `__init__()`

### Creating New Initializers

To add a new vector store initializer:

1. Define initialization function in [src/backend/bisheng/interface/initialize/vector_store.py]()
2. Add mapping to `vecstore_initializer` dict [src/backend/bisheng/interface/initialize/vector_store.py:275-288]()
3. Handle special cases (connection args, embedding selection, permission checks)

### Extending Frontend Nodes

To customize UI configuration for a component type:

1. Create or extend a `FrontendNode` subclass in [src/backend/bisheng/template/frontend_node/]()
2. Override `format_field()` to customize field properties
3. Override `add_extra_fields()` to inject additional configuration fields

Example field type mappings:

| Field Type | Frontend Rendering |
|------------|-------------------|
| `"bisheng_model"` | Model selector dropdown from LLM service |
| `"bisheng_embedding"` | Embedding model selector dropdown |
| `"knowledge_one"` | Single knowledge base selector (radio) |
| `"knowledge_list"` | Multiple knowledge base selector (checkboxes) |
| `"code"` | Code editor with syntax highlighting |
| `"file"` | File upload widget |

Sources: [src/backend/bisheng/template/frontend_node/base.py](), [src/backend/bisheng/template/frontend_node/llms.py:223-231](), [src/backend/bisheng/template/frontend_node/vectorstores.py:346-362]()

---

## Integration with Vertex Build System

The Custom Component System is invoked during vertex building in the workflow graph:

```mermaid
sequenceDiagram
    participant Graph
    participant Vertex
    participant Build as Vertex._build()
    participant Params as _build_each_node_in_params_dict()
    participant Inst as instantiate_class()
    participant Handler as Type-specific handler
    
    Graph->>Vertex: generator_build()
    Vertex->>Build: Called for each vertex
    Build->>Params: Build dependent vertices first
    loop For each param
        Params->>Params: Check if param is Vertex
        alt Is Vertex
            Params->>Vertex: await node.get_result()
        end
    end
    Params-->>Build: All params resolved
    Build->>Inst: await instantiate_class(vertex_type, base_type, params)
    Inst->>Handler: Route to handler
    Handler-->>Inst: Built object
    Inst-->>Build: (object, artifacts) or object
    Build->>Vertex: Set _built_object and artifacts
```

**Diagram: Component Instantiation within Vertex Build**

Key points:
- Vertices are built in topological order
- Dependent vertices are built recursively before a vertex instantiates its component
- The `NODE_ID_DICT` tracks which vertex IDs provided which parameter values
- Built objects and artifacts are cached on the vertex for reuse

Sources: [src/backend/bisheng/graph/vertex/base.py:254-413](), [src/backend/bisheng/api/utils.py:158-228]()

---

**Summary**: The Custom Component System provides a flexible, extensible framework for instantiating AI components with frontend-configurable parameters, permission-based filtering, and support for both standard LangChain components and custom user-defined implementations. It bridges the gap between UI configuration and runtime execution through a type-based routing system with specialized handlers for each component category.

---

# Page: Session Management and Caching

# Session Management and Caching

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docker/bisheng/config/config.yaml](docker/bisheng/config/config.yaml)
- [src/backend/bisheng/api/services/assistant_agent.py](src/backend/bisheng/api/services/assistant_agent.py)
- [src/backend/bisheng/api/services/base.py](src/backend/bisheng/api/services/base.py)
- [src/backend/bisheng/api/utils.py](src/backend/bisheng/api/utils.py)
- [src/backend/bisheng/api/v1/callback.py](src/backend/bisheng/api/v1/callback.py)
- [src/backend/bisheng/api/v1/endpoints.py](src/backend/bisheng/api/v1/endpoints.py)
- [src/backend/bisheng/chat/client.py](src/backend/bisheng/chat/client.py)
- [src/backend/bisheng/chat/handlers.py](src/backend/bisheng/chat/handlers.py)
- [src/backend/bisheng/chat/manager.py](src/backend/bisheng/chat/manager.py)
- [src/backend/bisheng/database/base.py](src/backend/bisheng/database/base.py)
- [src/backend/bisheng/graph/vertex/base.py](src/backend/bisheng/graph/vertex/base.py)
- [src/backend/bisheng/initdb_config.yaml](src/backend/bisheng/initdb_config.yaml)
- [src/backend/bisheng/interface/chains/base.py](src/backend/bisheng/interface/chains/base.py)
- [src/backend/bisheng/interface/chains/custom.py](src/backend/bisheng/interface/chains/custom.py)
- [src/backend/bisheng/interface/initialize/loading.py](src/backend/bisheng/interface/initialize/loading.py)
- [src/backend/bisheng/main.py](src/backend/bisheng/main.py)
- [src/backend/bisheng/template/frontend_node/chains.py](src/backend/bisheng/template/frontend_node/chains.py)
- [src/backend/bisheng/utils/threadpool.py](src/backend/bisheng/utils/threadpool.py)

</details>



## Purpose and Scope

This document describes Bisheng's session management and caching mechanisms, which enable efficient stateful conversations and prevent redundant graph rebuilding. Session management tracks user interactions across WebSocket connections and REST API calls, while the caching layer stores expensive-to-build objects like LangChain graphs, LLM instances, and vector stores.

For information about flow/skill execution workflow, see [Flow and Skill Management](#3.7). For chat message persistence, see [Chat and Messaging System](#3.2).

---

## Session Management Architecture

### Session Identification and Key Generation

Sessions in Bisheng are identified by composite keys combining `flow_id` (or `client_id`) and `chat_id`. The system uses a consistent key generation function to maintain identity across different subsystems.

```mermaid
graph TB
    subgraph "Session Key Generation"
        FK["Flow/Client ID"]
        CK["Chat ID"]
        GCK["get_cache_key()"]
        SK["Session Key<br/>'{flow_id}_{chat_id}'"]
        
        FK --> GCK
        CK --> GCK
        GCK --> SK
    end
    
    subgraph "Session Usage"
        SK --> WS["WebSocket Connection<br/>active_connections[key]"]
        SK --> CACHE["In-Memory Cache<br/>in_memory_cache.get(key)"]
        SK --> QUEUE["Stream Queue<br/>stream_queue[key]"]
        SK --> THREAD["Thread Pool Tasks<br/>thread_pool.submit(key, ...)"]
    end
    
    subgraph "Session Data"
        HIST["Chat History<br/>MySQL ChatMessage"]
        SESS["MessageSession<br/>MySQL session record"]
        STATE["Context State<br/>context_dict[key]"]
    end
    
    SK --> HIST
    SK --> SESS
    SK --> STATE
```

**Session Key Format**: The key follows the pattern `{flow_id}_{chat_id}`, generated by the `get_cache_key()` utility function. This key serves as the primary identifier across all session-related operations.

**Sources**: [src/backend/bisheng/chat/manager.py:115-122](), [src/backend/bisheng/utils/util.py]() (referenced)

### Session Lifecycle Management

The session lifecycle begins when a WebSocket connection is established or a REST API call is made, and continues until the connection is closed or the session expires.

```mermaid
sequenceDiagram
    participant Client
    participant Manager as ChatManager
    participant DB as MySQL Database
    participant Cache as InMemoryCache
    participant Thread as ThreadPool
    
    Client->>Manager: WebSocket connect(flow_id, chat_id)
    Manager->>Manager: generate key = get_cache_key(flow_id, chat_id)
    Manager->>Manager: active_connections[key] = websocket
    Manager->>Manager: stream_queue[key] = Queue()
    
    alt First message in session
        Manager->>DB: Check MessageSession exists
        alt Session does not exist
            Manager->>DB: INSERT MessageSession(chat_id, flow_id, user_id)
            Manager->>Manager: Log telemetry event (NEW_MESSAGE_SESSION)
        end
    end
    
    Client->>Manager: Send message payload
    Manager->>Manager: context_dict[key] = {status: 'init', ...}
    
    alt Graph not cached
        Manager->>Thread: submit(key, init_langchain_object_task)
        Thread->>Thread: Build graph from graph_data
        Thread->>Cache: set(key, built_object)
        Thread->>Cache: set(key + '_artifacts', artifacts)
        Thread->>Cache: set(key + '_question', questions)
    end
    
    Manager->>Cache: get(key) to retrieve graph
    Manager->>Thread: submit(key, dispatch_task)
    Thread->>Thread: Execute graph with inputs
    Thread-->>Manager: Return results
    Manager->>Client: Send response via WebSocket
    
    Client->>Manager: WebSocket disconnect
    Manager->>Manager: active_connections.pop(key)
    Manager->>Manager: stream_queue.pop(key)
    Manager->>Manager: Log telemetry event (APPLICATION_ALIVE)
```

**Connection Establishment**: When a WebSocket connection is established via `ChatManager.connect()`, the manager creates entries in `active_connections` and `stream_queue` dictionaries using the session key.

**Context Tracking**: The `context_dict` maintains per-session state including:
- `status`: Current processing stage ('init', 'init_object', 'waiting_object')
- `has_file`: Whether file processing is involved
- `flow_id` and `chat_id`: Session identifiers

**Sources**: [src/backend/bisheng/chat/manager.py:115-122](), [src/backend/bisheng/chat/manager.py:289-446](), [src/backend/bisheng/chat/manager.py:680-712]()

### Chat History Management

Chat history is managed through two layers: database persistence (MySQL) and runtime memory for the current session.

| Storage Layer | Component | Purpose | Scope |
|---------------|-----------|---------|-------|
| **Database** | `ChatMessage` table | Persistent storage of all messages | All sessions, all time |
| **Database** | `MessageSession` table | Session metadata (flow_id, flow_name, user_id) | Session-level records |
| **Memory** | `ChatClient.chat_history` | Runtime conversation context | Current session only |
| **Memory** | `AssistantAgent` message trimming | Token-limited history for LLM | Current conversation |

**Chat History for Assistants**: The `ChatClient` maintains a runtime `chat_history` list that is loaded from the database on initialization and used to provide conversational context to AI agents.

```mermaid
graph LR
    subgraph "History Loading"
        INIT["ChatClient<br/>init_chat_history()"]
        DB[(MySQL<br/>ChatMessage)]
        MEM["chat_history[]<br/>In-Memory List"]
        
        INIT --> |"Query latest N*4 messages"| DB
        DB --> |"category: question,<br/>answer, tool_call,<br/>tool_result"| MEM
    end
    
    subgraph "History Usage"
        MEM --> CONV["get_latest_history()"]
        CONV --> TRIM["Filter invalid<br/>Q&A pairs"]
        TRIM --> MSGS["List[BaseMessage]<br/>HumanMessage,<br/>AIMessage,<br/>ToolMessage"]
        MSGS --> AGENT["AssistantAgent.run()<br/>Pass as chat_history"]
    end
    
    subgraph "History Persistence"
        NEW["New message"]
        NEW --> ADD["add_message()"]
        ADD --> |"Insert"| DB
        ADD --> MEM
    end
```

**Message Categories**: Messages are categorized as `question`, `answer`, `tool_call`, `tool_result`, or `reasoning_answer` to support different conversation patterns and enable proper history reconstruction.

**Token Management**: The `AssistantAgent.trim_messages()` method ensures chat history stays within the configured `max_token` limit by removing oldest messages while maintaining conversation coherence.

**Sources**: [src/backend/bisheng/chat/client.py:211-250](), [src/backend/bisheng/api/services/assistant_agent.py:294-318](), [src/backend/bisheng/chat/manager.py:45-84]()

---

## Caching Architecture

### In-Memory Cache Implementation

The `InMemoryCache` class provides a simple key-value store with LRU eviction and expiration support. It is the primary cache for expensive-to-build graph objects.

```mermaid
graph TB
    subgraph "InMemoryCache Structure"
        IMC["InMemoryCache"]
        CACHE["_cache: Dict[str, Any]"]
        TIMES["_timestamps: Dict[str, float]"]
        MAX["max_size: int"]
        EXP["expiration_time: int"]
        
        IMC --> CACHE
        IMC --> TIMES
        IMC --> MAX
        IMC --> EXP
    end
    
    subgraph "Cache Operations"
        GET["get(key)"]
        SET["set(key, value)"]
        DEL["delete(key)"]
        CLEAR["clear()"]
        
        GET --> CHECK_EXP["Check expiration"]
        CHECK_EXP --> |"Expired"| RET_NONE["Return None"]
        CHECK_EXP --> |"Valid"| RET_VAL["Return value"]
        
        SET --> CHECK_SIZE["Check max_size"]
        CHECK_SIZE --> |"Full"| EVICT["Evict oldest"]
        CHECK_SIZE --> |"Space available"| STORE["Store value"]
        EVICT --> STORE
    end
    
    subgraph "Cached Objects"
        GRAPH["Built Graph Object<br/>key: {flow_id}_{chat_id}"]
        ARTIFACTS["Artifacts Dictionary<br/>key: {flow_id}_{chat_id}_artifacts"]
        QUESTIONS["Input Questions List<br/>key: {flow_id}_{chat_id}_question"]
    end
    
    CACHE --> GRAPH
    CACHE --> ARTIFACTS
    CACHE --> QUESTIONS
```

**Cache Key Patterns**:
- Base key: `{flow_id}_{chat_id}` - Stores the built graph/chain object
- Artifacts key: `{flow_id}_{chat_id}_artifacts` - Stores template variables and metadata
- Questions key: `{flow_id}_{chat_id}_question` - Stores pre-generated questions for batch processing

**Cache Invalidation**: The cache can be explicitly cleared by calling `set_cache(key, None)`, which triggers a rebuild on the next access. This occurs when file uploads are detected that require document loader re-initialization.

**Sources**: [src/backend/bisheng/core/cache/flow.py]() (referenced), [src/backend/bisheng/chat/manager.py:91-93](), [src/backend/bisheng/chat/manager.py:173-179]()

### Redis-Based Distributed Caching

Redis serves as a distributed cache layer for shared data that needs to be accessible across multiple backend instances or worker processes.

| Cache Type | Key Pattern | TTL | Purpose |
|------------|-------------|-----|---------|
| **Logo URLs** | `logo_cache_new:{logo_path}` | 5 days (432,000s) | MinIO temporary URLs for asset access |
| **Config** | `config:initdb_config` | Manual invalidation | System configuration from database |
| **Session State** | Various | Session lifetime | Linsight workflow state and node heartbeats |

**Two-Tier Logo Caching**: The `BaseService.get_logo_share_link()` implements a two-tier cache strategy:
1. First check `LogoMemoryCache` (in-memory, per-process)
2. Then check Redis (shared across processes)
3. Finally fetch from MinIO and populate both caches

```mermaid
graph TB
    REQUEST["get_logo_share_link<br/>(logo_path)"]
    
    subgraph "Memory Cache Layer"
        MEMCACHE["LogoMemoryCache<br/>InMemoryCache<br/>max_size=200<br/>ttl=24h"]
        MEMHIT{"Hit?"}
    end
    
    subgraph "Redis Cache Layer"
        REDIS[(Redis)]
        REDISHIT{"Hit?"}
    end
    
    subgraph "Storage Layer"
        MINIO[(MinIO<br/>Object Storage)]
        GENERATE["Generate 7-day<br/>share link"]
    end
    
    REQUEST --> MEMHIT
    MEMHIT --> |"Yes"| RETURN1["Return URL"]
    MEMHIT --> |"No"| REDISHIT
    
    REDISHIT --> |"Check<br/>redis.get()"| REDIS
    REDIS --> |"Hit"| STORE1["Store in<br/>memory cache"]
    STORE1 --> RETURN2["Return URL"]
    
    REDIS --> |"Miss"| GENERATE
    GENERATE --> MINIO
    MINIO --> STORE2["Store in Redis<br/>ttl=5 days"]
    STORE2 --> STORE3["Store in<br/>memory cache"]
    STORE3 --> RETURN3["Return URL"]
```

**Config Caching**: System configuration loaded from the database (`initdb_config.yaml` values) is cached in Redis with key `config:initdb_config` and manually invalidated when configuration is updated via the admin API.

**Sources**: [src/backend/bisheng/api/services/base.py:6-59](), [src/backend/bisheng/api/v1/endpoints.py:122-126]()

### Graph Object Caching Strategy

The most expensive operation in Bisheng is building graph objects from flow definitions. The caching strategy minimizes this cost through intelligent reuse.

```mermaid
sequenceDiagram
    participant Client
    participant Manager as ChatManager
    participant Cache as InMemoryCache
    participant Builder as build_flow_no_yield
    participant Graph as Graph Object
    
    Client->>Manager: Send message with inputs
    Manager->>Manager: key = get_cache_key(flow_id, chat_id)
    Manager->>Cache: get(key)
    
    alt Graph cached
        Cache-->>Manager: Return cached graph
        Manager->>Graph: Execute with new inputs
    else Graph not cached
        Manager->>Manager: context['status'] = 'init_object'
        Manager->>Manager: Submit build task to thread pool
        
        Note over Manager,Builder: Task runs in background thread
        
        Manager->>Builder: init_langchain_object_task(flow_id, chat_id, user_id, graph_data)
        Builder->>Builder: Build graph from JSON
        Builder->>Builder: await vertex.build() for each node
        Builder->>Builder: Extract input_node questions
        
        Builder->>Cache: set(key, built_object)
        Builder->>Cache: set(key + '_artifacts', artifacts)
        Builder->>Cache: set(key + '_question', questions)
        
        Manager->>Manager: context['status'] = 'waiting_object'
        Manager->>Cache: Poll for key existence
        Cache-->>Manager: Graph now available
        Manager->>Manager: context['status'] = 'init'
        Manager->>Graph: Execute with inputs
    end
    
    Note over Client,Graph: Subsequent messages reuse cached graph
```

**Build Process**: The `init_langchain_object_task()` method performs expensive operations:
1. Parse graph JSON structure
2. Topologically sort vertices (nodes)
3. Build each vertex (instantiate LLM, embeddings, vector stores, etc.)
4. Extract artifacts (template variables, input questions)
5. Cache all results

**Cache Invalidation Triggers**:
- File upload: When `InputFileNode` or document loaders receive new files, cache is cleared to ensure fresh parsing
- Explicit cache clearing: REST API parameter `clear_cache=true`
- Session expiration: Cache entries without activity may be evicted by LRU policy

**Sources**: [src/backend/bisheng/chat/manager.py:680-712](), [src/backend/bisheng/api/utils.py:158-227](), [src/backend/bisheng/chat/manager.py:520-565]()

---

## Session Service Integration

The `SessionService` provides a higher-level abstraction for session management, particularly for REST API endpoints that don't use WebSocket connections.

```mermaid
graph TB
    subgraph "SessionService"
        SS["SessionService"]
        GENKEY["generate_key()<br/>Hash graph_data"]
        LOAD["load_session()<br/>Build or retrieve graph"]
    end
    
    subgraph "Session Storage"
        SESSMAP["sessions: Dict[str, tuple]<br/>{session_id: (Graph, artifacts)}"]
    end
    
    subgraph "REST API Flow"
        API["/api/v1/process"]
        REQ["Request with<br/>flow_id, inputs, session_id"]
        
        API --> REQ
        REQ --> |"session_id=None"| GENKEY
        REQ --> |"session_id provided"| LOAD
        
        GENKEY --> |"Create session_id from hash"| SESSMAP
        LOAD --> |"Check sessions dict"| SESSMAP
        SESSMAP --> |"Not found"| BUILD["Build new graph"]
        SESSMAP --> |"Found"| REUSE["Reuse cached graph"]
        BUILD --> STORE["Store in sessions"]
        STORE --> EXEC["Execute graph"]
        REUSE --> EXEC
    end
```

**Session ID Generation**: When no `session_id` is provided in REST API calls, `generate_key()` creates one by hashing the graph structure. This ensures identical flows share the same cache key for better reuse.

**Session Persistence**: Unlike the WebSocket-based `ChatManager` which ties sessions to active connections, `SessionService` maintains sessions in a dictionary that persists across requests within the same backend process.

**Sources**: [src/backend/bisheng/api/v1/endpoints.py:200-204](), [src/backend/bisheng/services/deps.py]() (referenced)

---

## Cache Performance Optimization

### Cache Hit Optimization Strategies

The system employs several strategies to maximize cache hit rates and minimize redundant computation:

| Strategy | Implementation | Benefit |
|----------|----------------|---------|
| **Stable key generation** | Hash-based session IDs for REST API | Identical flows reuse cache |
| **Multi-level caching** | Memory → Redis → Storage | Fast access with fallback |
| **Lazy loading** | Build graphs only when needed | Reduces memory footprint |
| **Selective invalidation** | Only clear cache when structure changes | Preserves valid entries |
| **Artifact caching** | Cache template variables separately | Faster input validation |

**Graph Reuse Conditions**: A cached graph can be reused when:
1. The flow structure (nodes and edges) hasn't changed
2. No file uploads or document loader changes occurred
3. Node parameters haven't been modified via tweaks
4. The session hasn't expired from the cache

**Performance Impact**: Caching reduces typical request processing time from 2-5 seconds (graph building) to 50-200ms (cached execution), representing a ~10-20x speedup for subsequent requests.

**Sources**: [src/backend/bisheng/chat/manager.py:520-565](), [src/backend/bisheng/processing/process.py]() (referenced)

### Memory Management

The caching system implements memory management strategies to prevent unbounded growth:

```mermaid
graph TB
    subgraph "Memory Management"
        SIZE["InMemoryCache<br/>max_size limit"]
        LRU["LRU Eviction<br/>Remove oldest entries"]
        EXP["Expiration Check<br/>Time-based invalidation"]
        
        SIZE --> LRU
        EXP --> CLEANUP["Remove expired entries"]
    end
    
    subgraph "Connection Management"
        CLOSE["WebSocket close"]
        DISC["disconnect()"]
        POP["active_connections.pop(key)"]
        QUEUE_CLEAN["stream_queue.pop(key)"]
        
        CLOSE --> DISC
        DISC --> POP
        DISC --> QUEUE_CLEAN
    end
    
    subgraph "Thread Management"
        CANCEL["cancel_task()"]
        TASKS["future_dict and async_task"]
        CANCEL_FUTURES["Cancel pending futures"]
        
        CLOSE --> CANCEL
        CANCEL --> TASKS
        TASKS --> CANCEL_FUTURES
    end
    
    LRU -.->|"Prevents"| MEM_EXHAUST["Memory Exhaustion"]
    CLEANUP -.->|"Prevents"| STALE["Stale Data"]
    CANCEL_FUTURES -.->|"Prevents"| LEAK["Resource Leaks"]
```

**Automatic Cleanup**: When a WebSocket connection closes, the `ChatManager` performs comprehensive cleanup:
- Removes connection from `active_connections`
- Clears associated `stream_queue`
- Cancels pending thread pool tasks
- Logs telemetry for session duration

**Manual Cache Management**: Administrators can force cache clearing by setting cache entries to `None`, triggering a rebuild on next access.

**Sources**: [src/backend/bisheng/chat/manager.py:124-164](), [src/backend/bisheng/utils/threadpool.py:90-103]()

---

## Streaming Output Queue Management

For real-time streaming responses, Bisheng maintains per-session queues to buffer LLM token outputs.

```mermaid
graph LR
    subgraph "Stream Queue Setup"
        CONN["WebSocket connect"]
        KEY["Session key"]
        QUEUE["Queue()<br/>FIFO buffer"]
        
        CONN --> KEY
        KEY --> |"stream_queue[key] = Queue()"| QUEUE
    end
    
    subgraph "Stream Production"
        LLM["LLM generates tokens"]
        CALLBACK["AsyncStreamingLLMCallbackHandler"]
        PUT["queue.put(token)"]
        
        LLM --> CALLBACK
        CALLBACK --> |"on_llm_new_token()"| PUT
        PUT --> QUEUE
    end
    
    subgraph "Stream Consumption"
        HANDLER["Message handler"]
        GET["queue.get()"]
        AGGREGATE["Accumulate full response"]
        DB[(MySQL<br/>Save complete message)]
        
        QUEUE --> GET
        GET --> HANDLER
        HANDLER --> AGGREGATE
        AGGREGATE --> DB
    end
    
    subgraph "Stop Handling"
        STOP["User sends 'stop' action"]
        DRAIN["while not queue.empty()"]
        PARTIAL["Save partial response<br/>remark='break_answer'"]
        
        STOP --> DRAIN
        DRAIN --> QUEUE
        DRAIN --> PARTIAL
        PARTIAL --> DB
    end
```

**Queue Purpose**: The stream queue serves two purposes:
1. **Stop handling**: When users interrupt streaming output, the queue contents are drained and saved as a partial response
2. **Message tracking**: Accumulates streamed tokens for complete message persistence

**Thread Safety**: Each session has its own `Queue()` instance, providing thread-safe communication between the LLM callback thread and the message handling thread.

**Cleanup**: Stream queues are cleared when sessions end or when new messages begin to prevent cross-contamination.

**Sources**: [src/backend/bisheng/chat/manager.py:99-122](), [src/backend/bisheng/chat/handlers.py:79-134](), [src/backend/bisheng/chat/client.py:264-289]()

---

## Cache Key Utilities and Conventions

The system uses consistent naming conventions for cache keys to ensure proper organization and collision avoidance.

| Key Pattern | Example | Purpose |
|-------------|---------|---------|
| `{flow_id}_{chat_id}` | `abc123_def456` | Primary session identifier |
| `{flow_id}_{chat_id}_artifacts` | `abc123_def456_artifacts` | Template variables and metadata |
| `{flow_id}_{chat_id}_question` | `abc123_def456_question` | Pre-generated questions for batch processing |
| `tmp_{flow_id}_{chat_id}` | `tmp_abc123_def456` | Temporary vector store collections |
| `logo_cache_new:{path}` | `logo_cache_new:icon/xyz.png` | MinIO share links |
| `config:initdb_config` | `config:initdb_config` | System configuration |

**Temporary Collections**: When flows dynamically create vector stores without explicit collection names, the system generates temporary collection names using the pattern `tmp_{flow_id}_{chat_id}` to ensure isolation between sessions.

**Key Generation Function**: The `get_cache_key(client_id, chat_id)` utility ensures consistent key generation across all components.

**Sources**: [src/backend/bisheng/api/utils.py:230-270]() (temporary collection naming), [src/backend/bisheng/chat/manager.py:115-122]()