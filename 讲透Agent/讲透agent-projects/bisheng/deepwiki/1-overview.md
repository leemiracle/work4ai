<!-- source: DeepWiki mcp.deepwiki.com · repo dataelement/bisheng · page 1 Overview · fetched 2026-10-29 -->

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

