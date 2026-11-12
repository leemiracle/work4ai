<!-- source: DeepWiki mcp.deepwiki.com · repo openJiuwen-ai/agent-studio · page 1 Overview · fetched 2026-11-02 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [backend/openjiuwen_studio/core/common/logging/__init__.py](backend/openjiuwen_studio/core/common/logging/__init__.py)
- [backend/openjiuwen_studio/core/common/logging/events.py](backend/openjiuwen_studio/core/common/logging/events.py)
- [backend/openjiuwen_studio/core/config.py](backend/openjiuwen_studio/core/config.py)
- [backend/openjiuwen_studio/core/manager/agent.py](backend/openjiuwen_studio/core/manager/agent.py)
- [backend/openjiuwen_studio/core/manager/convertor/agent.py](backend/openjiuwen_studio/core/manager/convertor/agent.py)
- [backend/openjiuwen_studio/core/manager/convertor/components/sub_workflow.py](backend/openjiuwen_studio/core/manager/convertor/components/sub_workflow.py)
- [backend/openjiuwen_studio/core/manager/email_manager/__init__.py](backend/openjiuwen_studio/core/manager/email_manager/__init__.py)
- [backend/openjiuwen_studio/core/manager/email_manager/email_template.py](backend/openjiuwen_studio/core/manager/email_manager/email_template.py)
- [backend/openjiuwen_studio/core/manager/email_manager/email_utils.py](backend/openjiuwen_studio/core/manager/email_manager/email_utils.py)
- [backend/openjiuwen_studio/core/manager/knowledge_base.py](backend/openjiuwen_studio/core/manager/knowledge_base.py)
- [backend/openjiuwen_studio/core/manager/model_manager/managers/embedding_model_test_manager.py](backend/openjiuwen_studio/core/manager/model_manager/managers/embedding_model_test_manager.py)
- [backend/openjiuwen_studio/core/manager/redis_manager/__init__.py](backend/openjiuwen_studio/core/manager/redis_manager/__init__.py)
- [backend/openjiuwen_studio/core/manager/repositories/agent_repository.py](backend/openjiuwen_studio/core/manager/repositories/agent_repository.py)
- [backend/openjiuwen_studio/core/manager/repositories/plugin_repository.py](backend/openjiuwen_studio/core/manager/repositories/plugin_repository.py)
- [backend/openjiuwen_studio/core/manager/repositories/tool_repository.py](backend/openjiuwen_studio/core/manager/repositories/tool_repository.py)
- [backend/openjiuwen_studio/core/manager/utils/utils.py](backend/openjiuwen_studio/core/manager/utils/utils.py)
- [backend/openjiuwen_studio/main.py](backend/openjiuwen_studio/main.py)
- [backend/openjiuwen_studio/routers/agents.py](backend/openjiuwen_studio/routers/agents.py)
- [backend/openjiuwen_studio/routers/embedding_models.py](backend/openjiuwen_studio/routers/embedding_models.py)
- [backend/openjiuwen_studio/schemas/agent.py](backend/openjiuwen_studio/schemas/agent.py)
- [frontend/packages/api-client/src/config.ts](frontend/packages/api-client/src/config.ts)
- [frontend/packages/api-client/src/services/agentService.ts](frontend/packages/api-client/src/services/agentService.ts)
- [frontend/src/locales/en-US.json](frontend/src/locales/en-US.json)
- [frontend/src/locales/zh-CN.json](frontend/src/locales/zh-CN.json)
- [frontend/src/pages/Auth/PrivacyPolicyPage.tsx](frontend/src/pages/Auth/PrivacyPolicyPage.tsx)
- [frontend/src/pages/Auth/UserLoginPage.tsx](frontend/src/pages/Auth/UserLoginPage.tsx)
- [frontend/src/pages/KnowledgeBase/components/AddDocumentDialog.tsx](frontend/src/pages/KnowledgeBase/components/AddDocumentDialog.tsx)
- [frontend/src/pages/KnowledgeBase/components/KnowledgeBaseFormDialog.tsx](frontend/src/pages/KnowledgeBase/components/KnowledgeBaseFormDialog.tsx)
- [frontend/src/pages/Models/ModelsPage.tsx](frontend/src/pages/Models/ModelsPage.tsx)
- [frontend/src/pages/Models/ModelsPageNew.tsx](frontend/src/pages/Models/ModelsPageNew.tsx)
- [frontend/src/pages/Models/components/EmbeddingModelsTable.tsx](frontend/src/pages/Models/components/EmbeddingModelsTable.tsx)
- [frontend/src/pages/Models/components/LLMModelsTable.tsx](frontend/src/pages/Models/components/LLMModelsTable.tsx)

</details>



OpenJiuwen Agent Studio is a comprehensive AI agent development platform that enables users to build, deploy, and manage intelligent agents through visual interfaces and automated workflows. The system provides a complete toolkit for creating both autonomous (ReAct) and orchestrated (Workflow) agents, with integrated support for knowledge bases, model management, prompt optimization, and plugin extensibility.

This page provides a technical overview of the system architecture, major components, and how they interconnect. For detailed guides on specific features, see:
- Agent development and lifecycle: [Agents](#3.1)
- Workflow design and execution: [Workflows](#3.2)
- Database architecture and migrations: [Data Layer](#5.4)
- API endpoint reference: [API Reference](#8)

## System Architecture

The platform follows a modern three-tier architecture with clear separation between presentation (React frontend), business logic (FastAPI backend), and data persistence (multi-database strategy).

### High-Level Component Architecture

```mermaid
graph TB
    subgraph "Client Tier"
        Browser["Web Browser"]
    end
    
    subgraph "Frontend Application"
        Dashboard["Dashboard<br/>/src/pages/Dashboard"]
        AgentPages["Agent Pages<br/>/src/pages/Agents"]
        WorkflowPages["Workflow Pages<br/>/src/pages/Workflows"]
        ModelPages["Model Pages<br/>/src/pages/Models"]
        KBPages["KB Pages<br/>/src/pages/KnowledgeBase"]
        PluginPages["Plugin Pages<br/>/src/pages/Plugins"]
        
        ApiClient["@test-agentstudio/api-client<br/>AgentService, WorkflowService"]
        AuthStore["useAuthStore<br/>Zustand State"]
    end
    
    subgraph "Backend Services"
        MainApp["main.py<br/>FastAPI Application"]
        AgentRouter["routers/agents.py<br/>agents_router"]
        WorkflowRouter["routers/workflows.py"]
        ModelRouter["routers/models.py"]
        
        AgentManager["core/manager/agent.py<br/>agent_react_create, agent_save"]
        WorkflowMgr["core/manager/workflow.py"]
        KBManager["core/manager/knowledge_base.py"]
        
        AgentConverter["core/manager/convertor/agent.py<br/>agent_convert, workflow_convert"]
    end
    
    subgraph "Data Tier"
        AgentRepo["repositories/agent_repository.py<br/>AgentRepository"]
        WorkflowRepo["repositories/workflow_repository.py"]
        
        AgentDB["models/agent.py<br/>AgentBaseDB, AgentPublishDB"]
        WorkflowDB["models/workflow.py<br/>WorkflowBaseDB"]
        
        MySQL["MySQL 8.0+<br/>or SQLite"]
        VectorDB["Milvus/Chroma<br/>Vector Store"]
        Redis["Redis<br/>Cache & Checkpoint"]
    end
    
    Browser --> Dashboard
    Dashboard --> AgentPages & WorkflowPages & ModelPages
    AgentPages --> ApiClient
    WorkflowPages --> ApiClient
    ApiClient --> AuthStore
    
    ApiClient --> AgentRouter
    ApiClient --> WorkflowRouter
    ApiClient --> ModelRouter
    
    AgentRouter --> AgentManager
    WorkflowRouter --> WorkflowMgr
    AgentManager --> AgentConverter
    AgentManager --> AgentRepo
    WorkflowMgr --> WorkflowRepo
    
    AgentRepo --> AgentDB
    WorkflowRepo --> WorkflowDB
    AgentDB --> MySQL
    WorkflowDB --> MySQL
    KBManager --> VectorDB
    AgentManager --> Redis
```

**Sources:** 
- [frontend/src/pages/Models/ModelsPage.tsx:1-114]()
- [backend/openjiuwen_studio/main.py:1-262]()
- [backend/openjiuwen_studio/routers/agents.py:1-70]()
- [backend/openjiuwen_studio/core/manager/agent.py:1-160]()

### Application Initialization and Lifecycle

The application follows a structured startup and shutdown process managed by FastAPI's lifespan context:

```mermaid
graph TD
    Start["Application Start"] --> LoadEnv["Load .env Configuration"]
    LoadEnv --> CreateApp["FastAPI app = FastAPI<br/>lifespan=lifespan_func"]
    
    CreateApp --> Startup["Startup Phase"]
    Startup --> RenameIndexes["Rename SQLite Indexes<br/>if engine.url.drivername == 'sqlite'"]
    RenameIndexes --> CreateTables["Base.metadata.create_all<br/>target_tables, checkfirst=True"]
    CreateTables --> InitMemory["MemoryEngineManager.init"]
    InitMemory --> CheckAlembic["check_alembic_versions"]
    CheckAlembic --> CreateOpsTables["create_database_tables<br/>Ops DB"]
    CreateOpsTables --> InitRunner["Runner.start<br/>if enable_redis_checkpoint"]
    
    InitRunner --> RegisterRouters["register.router_register<br/>agents_router, workflows_router"]
    RegisterRouters --> Running["Application Running"]
    
    Running --> Shutdown["Shutdown Signal"]
    Shutdown --> Cleanup["Runner.stop<br/>Close DB connections"]
    Cleanup --> End["Application Stopped"]
```

**Key initialization classes and functions:**

| Component | Code Entity | Location |
|-----------|-------------|----------|
| Application Factory | `FastAPI(lifespan=lifespan_func)` | [backend/openjiuwen_studio/main.py:149-163]() |
| Database Tables | `Base.metadata.create_all()` | [backend/openjiuwen_studio/main.py:110-114]() |
| Table Models | `AgentBaseDB`, `AgentPublishDB`, `WorkflowBaseDB`, etc. | [backend/openjiuwen_studio/main.py:28-43]() |
| Memory Engine | `MemoryEngineManager.init()` | [backend/openjiuwen_studio/main.py:115]() |
| Version Check | `check_alembic_versions()` | [backend/openjiuwen_studio/main.py:121]() |
| Runner Initialization | `Runner.start()` | [backend/openjiuwen_studio/main.py:140]() |

**Sources:**
- [backend/openjiuwen_studio/main.py:54-146]()
- [backend/openjiuwen_studio/core/config.py:1-80]()

## Technology Stack

### Frontend Stack

| Layer | Technologies | Key Files |
|-------|-------------|-----------|
| **Framework** | React 18, TypeScript, Vite | [frontend/src/main.tsx](), [frontend/vite.config.ts]() |
| **UI Components** | Material-UI (MUI), Lucide Icons | [frontend/src/pages/Models/ModelsPage.tsx:1-50]() |
| **State Management** | Zustand (`useAuthStore`, `useAgentStore`) | [frontend/src/stores/useAuthStore.ts]() |
| **API Client** | React Query, Axios | [frontend/packages/api-client/src/services/agentService.ts:1-50]() |
| **Routing** | React Router v6 | [frontend/src/App.tsx]() |
| **i18n** | react-i18next | [frontend/src/locales/zh-CN.json](), [frontend/src/locales/en-US.json]() |
| **Workflow Canvas** | Custom React Flow implementation | [@workflow-canvas package]() |

**Sources:**
- [frontend/src/pages/Models/ModelsPage.tsx:1-45]()
- [frontend/packages/api-client/src/config.ts:1-70]()
- [frontend/src/locales/zh-CN.json:1-100]()

### Backend Stack

| Layer | Technologies | Key Files |
|-------|-------------|-----------|
| **Framework** | FastAPI, Uvicorn | [backend/openjiuwen_studio/main.py:1-50]() |
| **ORM** | SQLAlchemy 2.x | [backend/openjiuwen_studio/models/agent.py]() |
| **Validation** | Pydantic v2 | [backend/openjiuwen_studio/schemas/agent.py:1-50]() |
| **Migration** | Alembic (multi-head: MySQL + SQLite) | [backend/alembic/]() |
| **Authentication** | JWT (PyJWT) | [backend/openjiuwen_studio/core/manager/login_manager/]() |
| **AI Integration** | `openjiuwen` package (LLM, RAG, Agents) | [backend/openjiuwen_studio/core/manager/convertor/agent.py:1-50]() |
| **Task Queue** | Redis (optional) | [backend/openjiuwen_studio/core/manager/redis_manager/]() |

**Sources:**
- [backend/openjiuwen_studio/main.py:1-262]()
- [backend/openjiuwen_studio/schemas/agent.py:1-100]()
- [backend/openjiuwen_studio/core/config.py:1-80]()

### Database Architecture

The system supports multiple database backends for different data types:

```mermaid
graph TB
    subgraph "Application Layer"
        App["FastAPI Application"]
    end
    
    subgraph "Database Selection"
        DBType{DB_TYPE env var}
        DBType -->|mysql| MySQLEngine["SQLAlchemy Engine<br/>mysql+pymysql://"]
        DBType -->|sqlite| SQLiteEngine["SQLAlchemy Engine<br/>sqlite:///data/databases/"]
    end
    
    subgraph "Relational Databases"
        MySQLDB["MySQL 8.0+<br/>openjiuwen_agent<br/>openjiuwen_ops"]
        SQLiteDB["SQLite<br/>agent.db<br/>ops.db"]
    end
    
    subgraph "Vector Database Selection"
        IndexType{INDEX_MANAGER_TYPE}
        IndexType -->|chroma| ChromaDB["ChromaVectorStore<br/>Embedded Default"]
        IndexType -->|milvus| MilvusDB["MilvusVectorStore<br/>Requires etcd, MinIO"]
    end
    
    subgraph "Supporting Services"
        RedisDB["Redis 7.1.0<br/>Cache & Checkpointer<br/>redis_manager_bytes.client"]
        MinIO["MinIO/OBS<br/>Object Storage<br/>OBSDocumentManager"]
    end
    
    App --> DBType
    DBType --> MySQLEngine & SQLiteEngine
    MySQLEngine --> MySQLDB
    SQLiteEngine --> SQLiteDB
    
    App --> IndexType
    IndexType --> ChromaDB & MilvusDB
    
    App --> RedisDB
    App --> MinIO
```

**Database configuration mapping:**

| Purpose | Environment Variable | Code Entity | Default Value |
|---------|---------------------|-------------|---------------|
| DB Type | `DB_TYPE` | `settings.db_type` | `sqlite` |
| MySQL Host | `DB_HOST` | `settings.db_host` | `localhost` |
| SQLite Path | `SQLITE_DB_PATH` | `settings.sqlite_db_path` | `data/databases` |
| Vector DB Type | `INDEX_MANAGER_TYPE` | `_CURR_INDEX_TYPE` | `chroma` |
| Milvus Host | `MILVUS_HOST` | `settings.milvus_host` | `jiuwen-milvus-standalone` |
| Redis Host | `REDIS_HOST` | `settings.redis_host` | `localhost` |

**Sources:**
- [.env.example:88-149]()
- [backend/openjiuwen_studio/core/config.py:26-80]()
- [backend/openjiuwen_studio/core/manager/knowledge_base.py:83-152]()

## Core Components and Data Flow

### Agent Development Flow

The following diagram maps the natural language user journey to concrete code entities:

```mermaid
sequenceDiagram
    participant User
    participant AgentCreatePage as "AgentCreatePage.tsx"
    participant AgentService as "AgentService.createAgent"
    participant agents_router as "routers/agents.py<br/>agent_create"
    participant agent_react_create as "manager/agent.py<br/>agent_react_create"
    participant AgentRepository as "repositories/<br/>agent_repository.py"
    participant AgentBaseDB as "models/agent.py<br/>AgentBaseDB"
    
    User->>AgentCreatePage: Click "Create Agent"
    AgentCreatePage->>AgentCreatePage: Fill form (name, desc, type)
    AgentCreatePage->>AgentService: createAgent(request)
    AgentService->>agents_router: POST /agents/create
    agents_router->>agents_router: validate_request(AgentCreate)
    agents_router->>agent_react_create: mgr.agent_react_create(req, user)
    agent_react_create->>agent_react_create: create_agent_react_info<br/>generate UUID, set defaults
    agent_react_create->>AgentRepository: agent_repository.create_agent_db
    AgentRepository->>AgentBaseDB: INSERT INTO agent_base
    AgentBaseDB-->>AgentRepository: Success
    AgentRepository-->>agent_react_create: ResponseModel(code=200)
    agent_react_create-->>agents_router: AgentResponseCreate(id=uuid)
    agents_router-->>AgentService: ResponseModel[dict]
    AgentService-->>AgentCreatePage: Response with agent_id
    AgentCreatePage->>User: Navigate to agent editor
```

**Key code entities in agent creation:**

| Stage | Frontend Entity | Backend Entity | Data Model |
|-------|----------------|----------------|------------|
| UI Form | `AgentCreatePage` | - | `CreateAgentRequest` |
| API Call | `AgentService.createAgent()` | `POST /agents/create` | `AgentCreate` schema |
| Validation | - | `validate_request()` | Pydantic validation |
| Business Logic | - | `agent_react_create()` | `AgentBaseDBPd` |
| Persistence | - | `AgentRepository.create_agent_db()` | `AgentBaseDB` model |

**Sources:**
- [frontend/packages/api-client/src/services/agentService.ts:44-54]()
- [backend/openjiuwen_studio/routers/agents.py:157-179]()
- [backend/openjiuwen_studio/core/manager/agent.py:329-376]()
- [backend/openjiuwen_studio/core/manager/repositories/agent_repository.py:1-50]()

### Agent Configuration and Execution

Agents are configured in "display mode" and converted to executable DSL format:

```mermaid
graph LR
    subgraph "Display Mode - Frontend"
        DisplayInfo["AgentDisplayInfo<br/>name, desc, model, plugins,<br/>workflows, knowledge"]
    end
    
    subgraph "Save Process"
        agent_save["agent_save()<br/>Validate & Save"]
        AgentBaseDB["AgentBaseDB<br/>Stored in DB"]
    end
    
    subgraph "Conversion Process"
        agent_convert["agent_convert()<br/>Display → DSL"]
        
        workflow_convert["workflow_convert()<br/>Fetch canvas, params"]
        plugin_convert["agent_plugin_convert()<br/>Tool info to schema"]
        kb_convert["KB retrieval config<br/>Embedding model"]
    end
    
    subgraph "Executable DSL"
        AgentDSL["dsl.AgentDSL<br/>agent_type, model_config,<br/>workflows, plugins, kb_config"]
        WorkflowSchema["dsl.WorkflowSchema<br/>inputs, outputs"]
        PluginSchema["dsl.PluginSchema<br/>inputs, outputs"]
    end
    
    subgraph "Execution"
        Runner["Runner.run()<br/>Execute agent graph"]
    end
    
    DisplayInfo --> agent_save
    agent_save --> AgentBaseDB
    
    AgentBaseDB --> agent_convert
    agent_convert --> workflow_convert
    agent_convert --> plugin_convert
    agent_convert --> kb_convert
    
    workflow_convert --> WorkflowSchema
    plugin_convert --> PluginSchema
    kb_convert --> AgentDSL
    WorkflowSchema --> AgentDSL
    PluginSchema --> AgentDSL
    
    AgentDSL --> Runner
```

**Conversion function mapping:**

| Conversion Task | Function | Input | Output |
|----------------|----------|-------|--------|
| Main conversion | `agent_convert()` | `AgentBaseDBPd` | `dsl.AgentDSL` |
| Workflow list | `workflows_convert()` | `List[dict]` | `List[dsl.WorkflowSchema]` |
| Single workflow | `workflow_convert()` | `AgentWorkflowListNodeBase` | `(inputs, outputs)` |
| Plugin list | `agent_plugins_convert()` | `List[AgentPlugin]` | `List[dsl.PluginSchema]` |
| Single plugin | `agent_plugin_convert()` | `AgentPlugin` | `dsl.PluginSchema` |
| Model config | `model_convert()` | `AgentBaseDBPd.model_id` | `dsl.ModelConfig` |
| Knowledge base | KB retrieval logic | `kb_list` | `dsl.KBRetrievalConfig` |

**Sources:**
- [backend/openjiuwen_studio/core/manager/agent.py:613-695]()
- [backend/openjiuwen_studio/core/manager/convertor/agent.py:1-400]()
- [backend/openjiuwen_studio/schemas/agent.py:1-200]()

### Model Management Architecture

The system supports two types of models with distinct configurations:

```mermaid
graph TB
    subgraph "Frontend UI"
        ModelsPage["ModelsPage.tsx<br/>activeTab: LLM | Embedding"]
        LLMTable["LLMModelsTable.tsx"]
        EmbeddingTable["EmbeddingModelsTable.tsx"]
    end
    
    subgraph "API Hooks"
        useModels["useModels<br/>LLM configs"]
        useEmbedding["useEmbeddingModels<br/>Embedding configs"]
        
        createLLM["useCreateModel"]
        createEmbed["useCreateEmbeddingModel"]
    end
    
    subgraph "Backend Routers"
        models_router["routers/models.py<br/>POST /models/create"]
        embedding_router["routers/embedding_models.py<br/>POST /embedding-models"]
    end
    
    subgraph "Managers"
        ModelConfigManager["ModelConfigManager<br/>get_paginated_configs<br/>create_config"]
        EmbedRepo["EmbeddingModelConfigRepository<br/>create, get_by_id"]
    end
    
    subgraph "Database Models"
        ModelConfig["models/model_config.py<br/>ModelConfig<br/>provider, model_type, api_key,<br/>temperature, max_tokens"]
        
        EmbeddingModelConfig["models/embedding_model_config.py<br/>EmbeddingModelConfig<br/>model_id, api_base, api_key,<br/>max_batch_size"]
    end
    
    ModelsPage --> LLMTable
    ModelsPage --> EmbeddingTable
    
    LLMTable --> useModels
    LLMTable --> createLLM
    EmbeddingTable --> useEmbedding
    EmbeddingTable --> createEmbed
    
    useModels --> models_router
    createLLM --> models_router
    useEmbedding --> embedding_router
    createEmbed --> embedding_router
    
    models_router --> ModelConfigManager
    embedding_router --> EmbedRepo
    
    ModelConfigManager --> ModelConfig
    EmbedRepo --> EmbeddingModelConfig
```

**Model type comparison:**

| Aspect | LLM Models | Embedding Models |
|--------|-----------|------------------|
| **Frontend Component** | `LLMModelsTable.tsx` | `EmbeddingModelsTable.tsx` |
| **API Hook** | `useModels()` | `useEmbeddingModels()` |
| **Backend Router** | `routers/models.py` | `routers/embedding_models.py` |
| **Manager** | `ModelConfigManager` | `EmbeddingModelConfigRepository` |
| **DB Model** | `ModelConfig` | `EmbeddingModelConfig` |
| **Key Parameters** | `temperature`, `max_tokens`, `top_p`, `timeout` | `max_batch_size` |
| **Usage** | Agent reasoning, tool calls | Document embedding, RAG retrieval |

**Sources:**
- [frontend/src/pages/Models/ModelsPage.tsx:1-300]()
- [frontend/src/pages/Models/components/LLMModelsTable.tsx:1-100]()
- [frontend/src/pages/Models/components/EmbeddingModelsTable.tsx:1-100]()
- [backend/openjiuwen_studio/routers/embedding_models.py:1-200]()

### Knowledge Base Document Processing Pipeline

Documents flow through a multi-stage processing pipeline:

```mermaid
graph TB
    subgraph "Upload Phase"
        UploadUI["AddDocumentDialog.tsx<br/>File selection & upload"]
        UploadAPI["POST /knowledge-bases/<br/>{kb_id}/documents/batch"]
        SaveFile["OBSDocumentManager<br/>upload_document()"]
    end
    
    subgraph "Database Recording"
        CreateRecord["KnowledgeBaseDocumentDB<br/>status=UPLOADED<br/>file_path, original_name"]
    end
    
    subgraph "Processing Phase"
        ProcessAPI["POST /knowledge-bases/<br/>{kb_id}/documents/process"]
        
        ParseDoc["AutoFileParser<br/>PDF, DOCX, TXT, MD"]
        ChunkText["TextChunker<br/>Token/Semantic strategy"]
        GraphExtract["TripleExtractor<br/>Optional graph enhancement"]
    end
    
    subgraph "Indexing Phase"
        EmbedText["OpenAIEmbedding<br/>_create_embed_model()"]
        
        IndexManager{INDEX_MANAGER_TYPE}
        IndexManager -->|chroma| ChromaIndexer["ChromaIndexer<br/>index_documents"]
        IndexManager -->|milvus| MilvusIndexer["MilvusIndexer<br/>index_documents"]
    end
    
    subgraph "Status Updates"
        StatusUploaded["UPLOADED"]
        StatusParsing["PARSING"]
        StatusIndexing["INDEXING"]
        StatusIndexed["INDEXED"]
        StatusFailed["FAILED"]
    end
    
    UploadUI --> UploadAPI
    UploadAPI --> SaveFile
    SaveFile --> CreateRecord
    CreateRecord --> StatusUploaded
    
    StatusUploaded --> ProcessAPI
    ProcessAPI --> StatusParsing
    StatusParsing --> ParseDoc
    ParseDoc --> ChunkText
    ChunkText --> GraphExtract
    GraphExtract --> StatusIndexing
    
    StatusIndexing --> EmbedText
    EmbedText --> IndexManager
    ChromaIndexer --> StatusIndexed
    MilvusIndexer --> StatusIndexed
    
    ParseDoc -.->|Error| StatusFailed
    ChunkText -.->|Error| StatusFailed
    IndexManager -.->|Error| StatusFailed
```

**Processing function mapping:**

| Stage | Code Entity | Key Parameters | Location |
|-------|-------------|----------------|----------|
| **Upload** | `document_upload_batch()` | `files: List[UploadFile]` | [knowledge_base.py:700-800]() |
| **Save to storage** | `OBSDocumentManager.upload_document()` | `object_name`, `file_path` | [knowledge_base.py:144-151]() |
| **Parse** | `AutoFileParser.parse()` | `file_path` | Via `openjiuwen` package |
| **Chunk** | `TextChunker.chunk()` | `chunk_size`, `overlap` | Via `openjiuwen` package |
| **Extract triples** | `TripleExtractor.extract()` | `llm_client`, `documents` | Via `openjiuwen` package |
| **Embed** | `OpenAIEmbedding.embed()` | `texts`, `batch_size` | [knowledge_base.py:369-451]() |
| **Index** | `ChromaIndexer.index_documents()` | `documents`, `collection_name` | Via `openjiuwen` package |
| **Status update** | `knowledge_base_repository.update_document_status()` | `doc_id`, `status` | [knowledge_base.py:1000-1100]() |

**Sources:**
- [frontend/src/pages/KnowledgeBase/components/AddDocumentDialog.tsx:1-200]()
- [backend/openjiuwen_studio/core/manager/knowledge_base.py:86-451]()
- [backend/openjiuwen_studio/schemas/knowledge_base.py:1-100]()

## Configuration and Environment

The system is configured through environment variables defined in `.env`:

**Critical configuration mapping:**

| Category | Variable | Code Reference | Default | Purpose |
|----------|----------|----------------|---------|---------|
| **Database** | `DB_TYPE` | `settings.db_type` | `sqlite` | `mysql` or `sqlite` |
| | `DB_HOST` | `settings.db_host` | `localhost` | MySQL host |
| | `SQLITE_DB_PATH` | `settings.sqlite_db_path` | `data/databases` | SQLite file location |
| **Vector DB** | `INDEX_MANAGER_TYPE` | `_CURR_INDEX_TYPE` | `chroma` | `milvus` or `chroma` |
| | `MILVUS_HOST` | `settings.milvus_host` | `jiuwen-milvus-standalone` | Milvus server |
| **Authentication** | `SECRET_KEY` | `settings.secret_key` | (required) | JWT signing key |
| | `ACCESS_TOKEN_EXPIRE_MINUTES` | `settings.access_token_expire_minutes` | `2880` | Token lifetime |
| **Services** | `BACKEND_PORT` | `settings.port` | `8000` | Backend port |
| | `FRONTEND_PORT` | - | `3000` | Frontend dev server |
| | `REDIS_HOST` | `settings.redis_host` | `localhost` | Redis cache |
| | `CODE_SANDBOX_URL` | `settings.code_sandbox_url` | - | Plugin execution sandbox |
| **Object Storage** | `OBS_BUCKET` | `OBSDocumentManager.bucket` | - | MinIO/OBS bucket |
| | `OBS_SERVER` | Used in `AioBotoClient` | - | Object storage endpoint |
| **Email** | `SMTP_HOST` | `settings.smtp_host` | - | Email server |
| | `SMTP_PORT` | `settings.smtp_port` | `465` | Email port |

**Frontend environment variables:**

| Variable | Purpose | Default | Code Usage |
|----------|---------|---------|------------|
| `VITE_API_BASE_URL` | Backend API endpoint | `/api/v1` | `API_CONFIG.BASE_URL` |
| `VITE_API_PROXY_TARGET` | Dev proxy target | `http://localhost:8000/` | `vite.config.ts` |
| `VITE_TOKEN_REFRESH_INTERVAL_SECONDS` | Token refresh frequency | `600` | `useAuthStore` |
| `VITE_ENABLE_NEW_AUTH` | Enable registration system | `False` | Auth routing |
| `VITE_PLUGIN_SERVICE_URL` | External plugin server | - | Plugin execution |

**Sources:**
- [.env.example:1-196]()
- [backend/openjiuwen_studio/core/config.py:1-80]()
- [frontend/packages/api-client/src/config.ts:1-70]()

## Request-Response Flow Example

A complete request flow for saving an agent configuration:

```mermaid
sequenceDiagram
    participant UI as "AgentEditorEditPage"
    participant Store as "useAgentStore"
    participant ApiClient as "AgentService"
    participant Router as "agents_router<br/>/agents/save"
    participant Middleware as "LogMiddleware"
    participant Handler as "agent_save"
    participant Validator as "validate_request"
    participant Manager as "mgr.agent_save"
    participant Converter as "agent_convert"
    participant Repo as "AgentRepository"
    participant DB as "AgentBaseDB Table"
    
    UI->>Store: Get agent data
    Store-->>UI: AgentDisplayInfo
    UI->>ApiClient: saveAgent(displayInfo)
    ApiClient->>Router: POST /api/v1/agents/save
    Router->>Middleware: Request logging start
    Router->>Validator: validate_request(AgentDisplayInfo)
    Validator->>Validator: Pydantic validation
    Validator-->>Router: Validated schema
    Router->>Handler: agent_save(req, current_user, manager)
    Handler->>Handler: check_user_space(space_id, user)
    Handler->>Handler: Get model config from DB
    Handler->>Manager: Save to AgentBaseDBPd
    Manager->>Repo: update_agent_db(agent_info)
    Repo->>DB: UPDATE agent_base SET ...
    DB-->>Repo: Success
    Repo-->>Manager: ResponseModel(code=200)
    Manager->>Manager: extract_agent_references
    Manager->>Converter: agent_convert(agent_info)
    Converter->>Converter: workflow_convert, plugin_convert
    Converter-->>Manager: AgentDSL
    Manager-->>Handler: ResponseModel with DSL
    Handler-->>Router: Success response
    Router->>Middleware: Log execution time
    Router-->>ApiClient: ResponseModel[dict]
    ApiClient-->>UI: Success
    UI->>UI: Show success message
```

**Key validation and error handling points:**

| Stage | Code Location | Error Handling |
|-------|--------------|----------------|
| Schema validation | `validate_request(AgentDisplayInfo)` | `ValidationError` → `handle_validation_error()` → HTTP 400 |
| User permission | `check_user_space()` | Raises exception if unauthorized |
| Model lookup | `manager.get_config_by_id()` | Returns `AGENT_MODEL_NOT_FOUND` if missing |
| Database save | `agent_repository.update_agent_db()` | Returns `ResponseModel` with error code |
| DSL conversion | `agent_convert()` | Catches conversion errors, logs warnings |

**Sources:**
- [backend/openjiuwen_studio/routers/agents.py:200-250]()
- [backend/openjiuwen_studio/core/manager/agent.py:613-800]()
- [backend/openjiuwen_studio/main.py:166-222]()

## Internationalization (i18n)

The platform supports English and Chinese through react-i18next:

**Language resolution strategy (backend):**

```python
def _resolve_language(current_user: Optional[dict]) -> str:
    """Sticky English strategy - prefers 'en' if specified in header or profile"""
    # 1. Check HTTP Header
    language = get_language()  # From Accept-Language or custom header
    if language and language.lower() not in {"cn"}:
        header_lang = _normalize_language(language)
        if header_lang == "en":
            return "en"
    
    # 2. Check user profile
    if current_user:
        locale = (current_user.get("data") or {}).get("locale")
        if locale and _normalize_language(locale) == "en":
            return "en"
    
    # 3. Default to Chinese
    return "zh"
```

**Translation file structure:**

| File | Keys | Usage |
|------|------|-------|
| `frontend/src/locales/zh-CN.json` | ~2500+ keys | Chinese translations |
| `frontend/src/locales/en-US.json` | ~2500+ keys | English translations |

**Key translation domains:**

- `common.*` - Buttons, messages, status
- `agents.*` - Agent-specific UI
- `workflows.*` - Workflow editor
- `models.*` - Model management
- `knowledgeBases.*` - Knowledge base UI
- `auth.*` - Authentication flows

**Sources:**
- [frontend/src/locales/zh-CN.json:1-500]()
- [frontend/src/locales/en-US.json:1-500]()
- [backend/openjiuwen_studio/routers/agents.py:28-68]()

---

This overview provides the foundation for understanding OpenJiuwen Agent Studio's architecture. For detailed information on specific subsystems, refer to the subsequent sections linked at the beginning of this document.

---

