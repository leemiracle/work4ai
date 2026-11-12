<!-- source: DeepWiki mcp.deepwiki.com · repo reworkd/AgentGPT · page 3 Backend · fetched 2026-10-26 -->

# Backend

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [next/src/utils/interfaces.ts](next/src/utils/interfaces.ts)
- [platform/poetry.lock](platform/poetry.lock)
- [platform/pyproject.toml](platform/pyproject.toml)
- [platform/reworkd_platform/settings.py](platform/reworkd_platform/settings.py)
- [platform/reworkd_platform/web/api/agent/agent_service/agent_service.py](platform/reworkd_platform/web/api/agent/agent_service/agent_service.py)
- [platform/reworkd_platform/web/api/agent/agent_service/agent_service_provider.py](platform/reworkd_platform/web/api/agent/agent_service/agent_service_provider.py)
- [platform/reworkd_platform/web/api/agent/agent_service/mock_agent_service.py](platform/reworkd_platform/web/api/agent/agent_service/mock_agent_service.py)
- [platform/reworkd_platform/web/api/agent/agent_service/open_ai_agent_service.py](platform/reworkd_platform/web/api/agent/agent_service/open_ai_agent_service.py)
- [platform/reworkd_platform/web/api/agent/dependancies.py](platform/reworkd_platform/web/api/agent/dependancies.py)
- [platform/reworkd_platform/web/api/agent/views.py](platform/reworkd_platform/web/api/agent/views.py)

</details>



This document provides an overview of the Python/FastAPI backend platform that powers AgentGPT's autonomous agent execution system. The backend handles agent lifecycle management, task processing, tool integration, and external service communication.

For information about the frontend Next.js application, see [Frontend](#2). For details about the agent execution algorithms and lifecycle, see [Agent System](#4).

## Architecture Overview

The AgentGPT backend is built using FastAPI and follows a service-oriented architecture with clear separation between API routing, business logic, and external integrations. The system is designed to handle autonomous agent execution through a series of coordinated services.

```mermaid
graph TB
    subgraph "FastAPI Application"
        ROUTER["/api/agent router<br/>views.py"]
        DEPS["Dependencies<br/>dependancies.py"]
        VALIDATOR["Request Validators"]
    end
    
    subgraph "Agent Service Layer"
        PROVIDER["AgentServiceProvider<br/>agent_service_provider.py"]
        OPENAI_SVC["OpenAIAgentService<br/>open_ai_agent_service.py"]
        MOCK_SVC["MockAgentService<br/>mock_agent_service.py"]
        INTERFACE["AgentService Protocol<br/>agent_service.py"]
    end
    
    subgraph "Core Services"
        TOKEN_SVC["TokenService"]
        MODEL_FACTORY["WrappedChatOpenAI<br/>model_factory.py"]
        SETTINGS["Settings<br/>settings.py"]
    end
    
    subgraph "External APIs"
        OPENAI_API["OpenAI API"]
        TOOLS_API["Tool APIs<br/>(SERP, Replicate, etc.)"]
    end
    
    subgraph "Database"
        MYSQL_DB["MySQL Database<br/>SQLAlchemy + aiomysql"]
    end
    
    ROUTER --> DEPS
    DEPS --> VALIDATOR
    VALIDATOR --> PROVIDER
    PROVIDER --> OPENAI_SVC
    PROVIDER --> MOCK_SVC
    OPENAI_SVC --> INTERFACE
    MOCK_SVC --> INTERFACE
    
    OPENAI_SVC --> TOKEN_SVC
    OPENAI_SVC --> MODEL_FACTORY
    PROVIDER --> SETTINGS
    
    MODEL_FACTORY --> OPENAI_API
    OPENAI_SVC --> TOOLS_API
    
    DEPS --> MYSQL_DB
```

**Backend System Architecture**

Sources: [platform/reworkd_platform/web/api/agent/views.py:1-146](), [platform/reworkd_platform/web/api/agent/agent_service/agent_service_provider.py:1-54](), [platform/reworkd_platform/web/api/agent/agent_service/open_ai_agent_service.py:1-228](), [platform/reworkd_platform/settings.py:1-179]()

## Technology Stack

The backend leverages a modern Python stack optimized for asynchronous processing and AI workloads:

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Web Framework** | FastAPI | High-performance async API server |
| **Database ORM** | SQLAlchemy 2.0 | Async database operations |
| **Database Driver** | aiomysql | Async MySQL connectivity |
| **AI/LLM** | LangChain + OpenAI | Language model orchestration |
| **HTTP Client** | httpx | Async HTTP requests |
| **Streaming** | Lanarky | FastAPI streaming response utilities |
| **Configuration** | Pydantic BaseSettings | Environment-based configuration |
| **Logging** | Loguru | Structured logging |
| **Message Queue** | aiokafka (optional) | Event streaming |

Sources: [platform/pyproject.toml:16-44]()

## Core Agent Service Architecture

The agent service layer implements the core business logic for autonomous agent execution through a clean protocol-based design:

```mermaid
graph TD
    subgraph "Service Protocol Layer"
        PROTOCOL["AgentService Protocol"]
        METHODS["• start_goal_agent()<br/>• analyze_task_agent()<br/>• execute_task_agent()<br/>• create_tasks_agent()<br/>• summarize_task_agent()<br/>• chat()"]
    end
    
    subgraph "Implementation Layer"
        OPENAI_IMPL["OpenAIAgentService"]
        MOCK_IMPL["MockAgentService"]
    end
    
    subgraph "Factory Layer"
        PROVIDER_FUNC["get_agent_service()"]
        FEATURE_FLAG["ff_mock_mode_enabled"]
    end
    
    subgraph "Core Dependencies"
        MODEL["WrappedChatOpenAI"]
        TOKEN_SERVICE["TokenService"]
        SETTINGS_OBJ["ModelSettings"]
        USER["UserBase"]
        OAUTH["OAuthCrud"]
    end
    
    PROTOCOL --> METHODS
    PROTOCOL <|-- OPENAI_IMPL
    PROTOCOL <|-- MOCK_IMPL
    
    PROVIDER_FUNC --> FEATURE_FLAG
    FEATURE_FLAG -->|"enabled"| MOCK_IMPL
    FEATURE_FLAG -->|"disabled"| OPENAI_IMPL
    
    OPENAI_IMPL --> MODEL
    OPENAI_IMPL --> TOKEN_SERVICE
    OPENAI_IMPL --> SETTINGS_OBJ
    OPENAI_IMPL --> USER
    OPENAI_IMPL --> OAUTH
```

**Agent Service Class Hierarchy**

Sources: [platform/reworkd_platform/web/api/agent/agent_service/agent_service.py:1-52](), [platform/reworkd_platform/web/api/agent/agent_service/open_ai_agent_service.py:43-58](), [platform/reworkd_platform/web/api/agent/agent_service/agent_service_provider.py:22-54]()

## FastAPI Router and Endpoints

The API layer exposes agent functionality through RESTful endpoints that handle the complete agent execution workflow:

```mermaid
graph LR
    subgraph "API Endpoints"
        START["/start<br/>POST"]
        ANALYZE["/analyze<br/>POST"] 
        EXECUTE["/execute<br/>POST"]
        CREATE["/create<br/>POST"]
        SUMMARIZE["/summarize<br/>POST"]
        CHAT["/chat<br/>POST"]
        TOOLS["/tools<br/>GET"]
    end
    
    subgraph "Request Bodies"
        AGENT_RUN["AgentRun"]
        TASK_ANALYZE["AgentTaskAnalyze"]
        TASK_EXECUTE["AgentTaskExecute"]
        TASK_CREATE["AgentTaskCreate"]
        AGENT_SUMMARIZE["AgentSummarize"]
        AGENT_CHAT["AgentChat"]
    end
    
    subgraph "Response Types"
        NEW_TASKS["NewTasksResponse"]
        ANALYSIS_RESP["Analysis"]
        STREAMING["StreamingResponse"]
        TOOLS_RESP["ToolsResponse"]
    end
    
    START --> AGENT_RUN
    ANALYZE --> TASK_ANALYZE
    EXECUTE --> TASK_EXECUTE
    CREATE --> TASK_CREATE
    SUMMARIZE --> AGENT_SUMMARIZE
    CHAT --> AGENT_CHAT
    
    START --> NEW_TASKS
    ANALYZE --> ANALYSIS_RESP
    EXECUTE --> STREAMING
    CREATE --> NEW_TASKS
    SUMMARIZE --> STREAMING
    CHAT --> STREAMING
    TOOLS --> TOOLS_RESP
```

**API Endpoint Structure**

The core agent workflow endpoints are:

- **`/agent/start`** - Initializes agent with goal and returns initial task list
- **`/agent/analyze`** - Analyzes a task to determine appropriate tool and arguments  
- **`/agent/execute`** - Executes a task using the selected tool (streaming response)
- **`/agent/create`** - Generates new tasks based on execution results
- **`/agent/summarize`** - Creates summary of agent run results (streaming response)
- **`/agent/chat`** - Enables chat interaction with agent results (streaming response)
- **`/agent/tools`** - Returns available tools and their metadata

Sources: [platform/reworkd_platform/web/api/agent/views.py:34-146](), [next/src/utils/interfaces.ts:25-38]()

## Dependency Injection and Validation

The backend uses FastAPI's dependency injection system to handle request validation, database sessions, and service instantiation:

```mermaid
graph TB
    subgraph "Validation Pipeline"
        REQUEST["HTTP Request"]
        VALIDATOR["Request Validator Functions"]
        AGENT_CRUD["AgentCRUD"]
        DB_SESSION["AsyncSession"]
        USER_AUTH["UserBase"]
    end
    
    subgraph "Service Resolution"
        SERVICE_PROVIDER["get_agent_service()"]
        AGENT_SERVICE["AgentService"]
        TOKEN_SERVICE["TokenService"]
        OAUTH_CRUD["OAuthCrud"]
    end
    
    subgraph "Validator Functions"
        START_VALIDATOR["agent_start_validator"]
        ANALYZE_VALIDATOR["agent_analyze_validator"] 
        EXECUTE_VALIDATOR["agent_execute_validator"]
        CREATE_VALIDATOR["agent_create_validator"]
        SUMMARIZE_VALIDATOR["agent_summarize_validator"]
        CHAT_VALIDATOR["agent_chat_validator"]
    end
    
    REQUEST --> VALIDATOR
    VALIDATOR --> AGENT_CRUD
    AGENT_CRUD --> DB_SESSION
    VALIDATOR --> USER_AUTH
    
    VALIDATOR --> START_VALIDATOR
    VALIDATOR --> ANALYZE_VALIDATOR
    VALIDATOR --> EXECUTE_VALIDATOR
    VALIDATOR --> CREATE_VALIDATOR
    VALIDATOR --> SUMMARIZE_VALIDATOR
    VALIDATOR --> CHAT_VALIDATOR
    
    SERVICE_PROVIDER --> AGENT_SERVICE
    SERVICE_PROVIDER --> TOKEN_SERVICE
    SERVICE_PROVIDER --> OAUTH_CRUD
```

**Dependency Injection Flow**

Each endpoint validator creates database records to track agent runs and tasks, ensuring proper audit trails and state management throughout the agent execution process.

Sources: [platform/reworkd_platform/web/api/agent/dependancies.py:26-96]()

## Configuration System

The backend uses Pydantic `BaseSettings` for environment-based configuration management with comprehensive service integrations:

| Configuration Category | Key Settings | Purpose |
|------------------------|--------------|---------|
| **Application** | `host`, `port`, `environment`, `log_level` | Basic server configuration |
| **OpenAI Integration** | `openai_api_key`, `openai_api_base`, `azure_openai_deployment_name` | LLM service configuration |  
| **Database** | `db_host`, `db_port`, `db_user`, `db_pass`, `db_base` | MySQL connection settings |
| **External APIs** | `replicate_api_key`, `serp_api_key`, `helicone_api_key` | Tool service API keys |
| **Feature Flags** | `ff_mock_mode_enabled`, `max_loops` | Development and safety controls |
| **Security** | `secret_signing_key`, `frontend_url` | Authentication and CORS |

The `Settings` class includes computed properties like `db_url`, `pusher_enabled`, `kafka_enabled` that derive connection URLs and feature availability from the base configuration.

Sources: [platform/reworkd_platform/settings.py:34-179]()

## Database Integration

The backend uses SQLAlchemy 2.0 with async support for database operations, connecting to MySQL via the `aiomysql` driver. The database URL is constructed as `mysql+aiomysql://user:pass@host:port/database`.

Key database integration components:
- **`AgentCRUD`** - Handles agent run and task persistence  
- **`OAuthCrud`** - Manages user authentication tokens
- **`AsyncSession`** - Provides async database session management

Sources: [platform/reworkd_platform/settings.py:122-131](), [platform/pyproject.toml:23-25]()

## External Service Integration

The backend integrates with multiple external services through dedicated API clients and abstractions:

- **OpenAI/Azure OpenAI** - Primary LLM provider via LangChain integration
- **Helicone** - Optional LLM observability and caching layer  
- **Replicate** - Image generation capabilities
- **SERP API** - Web search functionality
- **Pinecone** - Vector database for semantic search (optional)
- **AWS Services** - S3 storage and Secrets Manager via boto3
- **Kafka** - Event streaming for distributed processing (optional)

The service availability is controlled through feature flags and API key presence checks in the settings configuration.

Sources: [platform/reworkd_platform/settings.py:54-171](), [platform/pyproject.toml:19-44]()

---

