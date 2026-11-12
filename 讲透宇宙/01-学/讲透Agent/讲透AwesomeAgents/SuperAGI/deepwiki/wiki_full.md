# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile-gpu](Dockerfile-gpu)
- [README.MD](README.MD)
- [config_template.yaml](config_template.yaml)
- [docker-compose-gpu.yml](docker-compose-gpu.yml)
- [gui/app/favicon.ico](gui/app/favicon.ico)
- [gui/pages/Content/Agents/TaskQueue.js](gui/pages/Content/Agents/TaskQueue.js)
- [gui/pages/Dashboard/Dashboard.module.css](gui/pages/Dashboard/Dashboard.module.css)
- [gui/pages/Dashboard/Settings/Settings.js](gui/pages/Dashboard/Settings/Settings.js)
- [gui/pages/Dashboard/TopBar.js](gui/pages/Dashboard/TopBar.js)
- [gui/pages/_app.js](gui/pages/_app.js)
- [gui/pages/api/apiConfig.js](gui/pages/api/apiConfig.js)
- [main.py](main.py)
- [requirements.txt](requirements.txt)
- [superagi/agent/agent_prompt_builder.py](superagi/agent/agent_prompt_builder.py)
- [superagi/agent/output_parser.py](superagi/agent/output_parser.py)
- [superagi/helper/json_cleaner.py](superagi/helper/json_cleaner.py)
- [superagi/helper/llm_loader.py](superagi/helper/llm_loader.py)
- [superagi/helper/token_counter.py](superagi/helper/token_counter.py)
- [superagi/jobs/agent_executor.py](superagi/jobs/agent_executor.py)
- [superagi/llms/llm_model_factory.py](superagi/llms/llm_model_factory.py)
- [superagi/llms/local_llm.py](superagi/llms/local_llm.py)
- [superagi/types/model_source_types.py](superagi/types/model_source_types.py)
- [tests/unit_tests/tools/duck_duck_go/test_duckduckgo_results.py](tests/unit_tests/tools/duck_duck_go/test_duckduckgo_results.py)

</details>



SuperAGI is an open-source framework for building, managing, and running autonomous AI agents. This system enables developers to create, configure, and deploy AI agents that can perform a variety of tasks using different tools and language models.

For detailed information about specific components, please refer to the [System Architecture](#1.1) page and the [Agent System](#2) page.

## What is SuperAGI?

SuperAGI provides a comprehensive platform for creating autonomous agents that can:

- Perform complex tasks through iterative reasoning
- Use various tools to interact with external systems
- Leverage different language models (LLMs) as their cognitive engine
- Maintain persistent memory during execution
- Follow customizable workflows to achieve goals

The framework is designed to be extensible, allowing developers to add new capabilities through tools and to customize agent behavior through templates and workflows.

```mermaid
graph TD
    subgraph "SuperAGI System"
        User["User"] -- "Interacts with" --> GUI["Web Interface"]
        GUI -- "Makes requests to" --> API["FastAPI Backend"]
        API -- "Creates & manages" --> Agent["Agents"]
        
        Agent -- "Executes" --> Workflow["Agent Workflows"]
        Agent -- "Utilizes" --> Tools["Tools"]
        Agent -- "Communicates with" --> LLM["Language Models"]
        Agent -- "Stores/Retrieves" --> Memory["Memory Systems"]
        
        Tools -- "Interact with" --> External["External Systems"]
        LLM -- "Provides" --> Reasoning["Reasoning Capabilities"]
        Memory -- "Enables" --> Persistence["Persistent Knowledge"]
    end
```

Sources: [README.MD:78-94](), [main.py:10-45]()

## Core Components

The SuperAGI system consists of the following core components:

| Component | Description | Key Functionality |
|-----------|-------------|-------------------|
| Agent System | The core execution engine | Creates, configures, and executes agents |
| Workflow System | Controls agent execution flow | Defines steps and logic for agent operation |
| Tools System | Expands agent capabilities | Allows agents to perform specific tasks |
| Resource Management | Handles files and data | Manages agent inputs and outputs |
| LLM Integration | Powers agent reasoning | Connects to various language model providers |
| Vector Store | Enables knowledge retrieval | Stores embeddings for semantic search |
| Web Interface | User interaction layer | Provides controls and monitoring for agents |

```mermaid
graph TD
    subgraph "System Architecture"
        API["FastAPI Backend"] --> AgentController["Agent Controller"]
        API --> ExecutionController["Agent Execution Controller"]
        API --> ResourceController["Resource Controller"]
        API --> ToolController["Tool Controller"]
        API --> ModelController["Models Controller"]
        API --> VectorDBController["Vector DB Controller"]
        
        AgentController --> AgentExecutor["AgentExecutor"]
        ExecutionController --> AgentExecutor
        
        AgentExecutor --> IterationHandler["AgentIterationStepHandler"]
        AgentExecutor --> ToolHandler["AgentToolStepHandler"]
        AgentExecutor --> WaitHandler["AgentWaitStepHandler"]
        
        AgentExecutor --> LLMIntegration["LLM Integration"]
        AgentExecutor --> ToolManager["Tool Manager"]
        AgentExecutor --> Memory["Vector Store Memory"]
    end
```

Sources: [superagi/jobs/agent_executor.py:37-157](), [main.py:109-137]()

## Agent Execution Flow

When an agent runs, it follows this general execution flow:

```mermaid
sequenceDiagram
    participant User
    participant UI as "Web Interface"
    participant API
    participant Executor as "AgentExecutor"
    participant LLM as "Language Model"
    participant Tools
    participant Memory
    
    User->>UI: Configure agent (goals, tools, model)
    UI->>API: Create agent
    API->>Executor: Start execution
    
    loop Until completion or max iterations
        Executor->>LLM: Send context, goals, and prompts
        LLM->>Executor: Return reasoning and next action
        
        alt Tool action
            Executor->>Tools: Execute tool with parameters
            Tools->>Executor: Return tool results
        else Iteration step
            Executor->>Executor: Process agent reasoning
        else Wait step
            Executor->>Executor: Pause execution
        end
        
        Executor->>Memory: Store execution results
        Executor->>UI: Update execution status
    end
    
    Executor->>API: Complete execution
    API->>UI: Display final results
    UI->>User: Show execution summary
```

Sources: [superagi/jobs/agent_executor.py:39-104](), [superagi/agent/agent_iteration_step_handler.py]()

## Configuration and Setup

SuperAGI can be deployed in multiple ways:

1. **SuperAGI Cloud**: Hosted service at app.superagi.com
2. **Local Installation**: Using Docker and docker-compose
3. **DigitalOcean Deployment**: One-click deployment option

The system configuration is managed through a `config.yaml` file which defines:

- LLM provider credentials
- Database connections
- Storage settings
- Tool configurations
- Authentication settings

```mermaid
graph TD
    subgraph "Deployment Options"
        Cloud["SuperAGI Cloud"] -- "Easiest option" --> Hosted["Managed Service"]
        Docker["Local Docker"] -- "Development" --> Self["Self-hosted"]
        Cloud_Provider["DigitalOcean"] -- "Production" --> Self
    end
    
    subgraph "Docker Components"
        Backend["Backend Container"]
        Celery["Celery Worker"]
        Frontend["GUI Container"]
        DB["PostgreSQL Database"]
        Cache["Redis"]
        NGINX["NGINX Proxy"]
    end
    
    Self -- "Uses" --> Docker_Compose["docker-compose.yaml"]
    Docker_Compose -- "Orchestrates" --> Backend
    Docker_Compose -- "Orchestrates" --> Celery
    Docker_Compose -- "Orchestrates" --> Frontend
    Docker_Compose -- "Orchestrates" --> DB
    Docker_Compose -- "Orchestrates" --> Cache
    Docker_Compose -- "Orchestrates" --> NGINX
```

Sources: [README.MD:100-115](), [config_template.yaml:1-126](), [docker-compose-gpu.yml:1-96]()

## LLM Integration

SuperAGI supports multiple language model providers:

| Provider | Models | Integration |
|----------|--------|------------|
| OpenAI | GPT-3.5, GPT-4 | API-based |
| Google | PaLM | API-based |
| Hugging Face | Various models | API-based |
| Replicate | Various models | API-based |
| Local LLM | Custom, open models | Local deployment |

The system uses a factory pattern to instantiate appropriate LLM client classes:

```mermaid
graph TD
    subgraph "LLM Integration"
        Factory["LLM Model Factory"]
        
        Factory --> OpenAI["OpenAI Class"]
        Factory --> GooglePalm["GooglePalm Class"]
        Factory --> HuggingFace["HuggingFace Class"]
        Factory --> Replicate["Replicate Class"]
        Factory --> LocalLLM["LocalLLM Class"]
        
        LocalLLM --> LLamaLoader["LLM Loader"]
        
        LLamaLoader --> GrammarHandler["LLama Grammar"]
        LLamaLoader --> ModelHandler["LLama Model"]
    end
    
    subgraph "Common LLM Operations"
        ApiKey["API Key Validation"]
        ChatCompletion["Chat Completion"]
        TokenCount["Token Counting"]
    end
    
    OpenAI -- "Implements" --> ApiKey
    OpenAI -- "Implements" --> ChatCompletion
    
    TokenCounter["TokenCounter Class"] -- "Manages" --> TokenCount
```

Sources: [superagi/llms/llm_model_factory.py:1-55](), [superagi/helper/llm_loader.py:1-38](), [superagi/types/model_source_types.py:1-33](), [superagi/helper/token_counter.py:1-99]()

## Tools System

The tools system extends agent capabilities by providing interfaces to external services and functionalities:

```mermaid
graph TD
    subgraph "Tools System"
        BaseTool["BaseTool Abstract Class"]
        ToolManager["Tool Manager"]
        
        BaseTool --> FileTool["File Tools"]
        BaseTool --> CodeTool["Code Generation Tools"]
        BaseTool --> EmailTool["Email Tools"]
        BaseTool --> SearchTool["Search Tools"]
        BaseTool --> ImageGenTool["Image Generation Tools"]
        BaseTool --> SocialTool["Social Media Tools"]
        
        ToolManager -- "Registers & manages" --> BaseTool
        ToolManager -- "Organizes tools into" --> Toolkit["Toolkits"]
        
        AgentExecutor["Agent Executor"] -- "Uses" --> ToolManager
        
        OutputParser["Output Parser"] -- "Parses tool selection" --> ToolExecution["Tool Execution"]
    end
```

Tools are dynamically loaded and made available to agents based on configuration. Each tool provides:

- Name and description for agent understanding
- JSON schema for required arguments
- Execution logic to perform actions
- Result formatting for agent consumption

Sources: [superagi/agent/output_parser.py:1-70](), [superagi/agent/agent_prompt_builder.py:1-137]()

## User Interface

The SuperAGI user interface provides a comprehensive dashboard for managing agents and monitoring their execution:

```mermaid
graph TD
    subgraph "User Interface Components"
        App["Main App (_app.js)"]
        
        App --> TopBar["Top Bar"]
        App --> SideBar["Side Bar"]
        App --> Content["Content Area"]
        
        Content --> AgentManagement["Agent Management"]
        Content --> Settings["Settings Panel"]
        Content --> Marketplace["Marketplace"]
        
        AgentManagement --> AgentWorkspace["Agent Workspace"]
        AgentWorkspace --> ActivityFeed["Activity Feed"]
        AgentWorkspace --> TaskQueue["Task Queue"]
        AgentWorkspace --> ResourceViewer["Resource Viewer"]
        
        Settings --> ModelSettings["Model Settings"]
        Settings --> DatabaseSettings["Database Settings"]
        Settings --> ApiKeySettings["API Key Management"]
    end
```

The interface provides functionality for:

- Creating and configuring agents
- Monitoring agent execution in real-time
- Managing resources and tools
- Configuring system settings
- Installing templates from marketplace

Sources: [gui/pages/_app.js:31-314](), [gui/pages/Dashboard/TopBar.js:1-116](), [gui/pages/Dashboard/Settings/Settings.js:1-57](), [gui/pages/Dashboard/Dashboard.module.css:1-126](), [gui/pages/Content/Agents/TaskQueue.js:1-69]()

## Security and Authentication

SuperAGI implements security through:

- JWT-based authentication
- API key management
- GitHub OAuth integration
- Role-based permissions
- Environment configuration options

The system supports different permission modes for agent execution, allowing for controlled autonomous operation.

Sources: [main.py:141-386](), [gui/pages/api/apiConfig.js:1-51]()

## System Requirements and Dependencies

SuperAGI requires:

- Python 3.10+
- PostgreSQL
- Redis
- Node.js (for frontend)
- Docker (recommended)
- Optional: NVIDIA GPU for local LLM support

The system has many Python dependencies including:

- FastAPI for API server
- SQLAlchemy for database ORM
- Celery for task queue
- Various LLM client libraries
- Vector database clients

Sources: [requirements.txt:1-161]()

---

# Page: System Architecture

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [.gitignore](.gitignore)
- [Dockerfile](Dockerfile)
- [Dockerfile-gpu](Dockerfile-gpu)
- [README.MD](README.MD)
- [config_template.yaml](config_template.yaml)
- [docker-compose-gpu.yml](docker-compose-gpu.yml)
- [docker-compose.yaml](docker-compose.yaml)
- [entrypoint.sh](entrypoint.sh)
- [entrypoint_celery.sh](entrypoint_celery.sh)
- [gui/.dockerignore](gui/.dockerignore)
- [gui/Dockerfile](gui/Dockerfile)
- [gui/DockerfileProd](gui/DockerfileProd)
- [gui/next.config.js](gui/next.config.js)
- [gui/pages/Content/Agents/ActionConsole.js](gui/pages/Content/Agents/ActionConsole.js)
- [gui/pages/Content/Agents/RunHistory.js](gui/pages/Content/Agents/RunHistory.js)
- [main.py](main.py)
- [nginx/default.conf](nginx/default.conf)
- [requirements.txt](requirements.txt)
- [superagi/agent/agent_prompt_builder.py](superagi/agent/agent_prompt_builder.py)
- [superagi/agent/output_parser.py](superagi/agent/output_parser.py)
- [superagi/helper/json_cleaner.py](superagi/helper/json_cleaner.py)
- [superagi/helper/llm_loader.py](superagi/helper/llm_loader.py)
- [superagi/helper/token_counter.py](superagi/helper/token_counter.py)
- [superagi/jobs/agent_executor.py](superagi/jobs/agent_executor.py)
- [superagi/llms/llm_model_factory.py](superagi/llms/llm_model_factory.py)
- [superagi/llms/local_llm.py](superagi/llms/local_llm.py)
- [superagi/types/model_source_types.py](superagi/types/model_source_types.py)
- [tests/unit_tests/tools/duck_duck_go/test_duckduckgo_results.py](tests/unit_tests/tools/duck_duck_go/test_duckduckgo_results.py)
- [wait-for-it.sh](wait-for-it.sh)

</details>



This document provides a detailed explanation of SuperAGI's system architecture, component interactions, and data flow. It covers the core components, their responsibilities, and how they interact to create a cohesive system for autonomous AI agents.

For information about specific agent systems and their implementation, see [Agent System](#2).

## High-Level Architecture Overview

SuperAGI is built with a modular, service-oriented architecture designed to run autonomous AI agents. The system is composed of several key components that work together to create, manage, and execute intelligent agents.

### System Components Diagram

```mermaid
graph TD
    User["User"] --> GUI["GUI/Frontend"]
    GUI --> |"HTTP/API Requests"| Proxy["Nginx Proxy"]
    Proxy --> |"Routes /api/"| Backend["FastAPI Backend"]
    Proxy --> |"Routes /"| GUI
    
    Backend --> |"Spawns tasks"| Celery["Celery Worker"]
    Backend --> |"Query/Store"| Database["PostgreSQL"]
    Celery --> |"Query/Store"| Database
    Celery --> |"Message broker"| Redis["Redis"]
    Backend --> |"Cache/Vector storage"| Redis
    
    subgraph "Core Components"
        Backend --> Controllers["API Controllers"]
        Celery --> AgentExecutor["Agent Executor"]
        
        Controllers --> |"Create/Configure"| AgentController["Agent Controller"]
        Controllers --> |"Manage execution"| AgentExecutionController["Agent Execution Controller"]
        Controllers --> |"Manage resources"| ResourceController["Resource Controller"]
        Controllers --> |"Configure system"| ConfigController["Config Controller"]
        Controllers --> |"Manage tools"| ToolController["Tool Controller"]
        Controllers --> |"Manage models"| ModelController["Models Controller"]
        
        AgentExecutor --> AgentToolStepHandler["Agent Tool Step Handler"]
        AgentExecutor --> AgentIterationStepHandler["Agent Iteration Step Handler"]
        AgentExecutor --> AgentWaitStepHandler["Agent Wait Step Handler"]
    end
    
    subgraph "External Systems"
        Backend --> LLMIntegration["LLM Integration"]
        LLMIntegration --> OpenAI["OpenAI"]
        LLMIntegration --> GooglePalm["Google Palm"]
        LLMIntegration --> HuggingFace["Hugging Face"]
        LLMIntegration --> LocalLLM["Local LLM"]
        
        Backend --> VectorStores["Vector Stores"]
        VectorStores --> Pinecone["Pinecone"]
        VectorStores --> Weaviate["Weaviate"]
        VectorStores --> RedisVS["Redis Vector Store"]
        VectorStores --> Qdrant["Qdrant"]
        
        Backend --> ResourceManagement["Resource Management"]
        ResourceManagement --> FileSystem["File System"]
        ResourceManagement --> S3["Amazon S3"]
    end
    
    classDef core fill:#f9f9f9,stroke:#333,stroke-width:1px
    classDef external fill:#f9f9f9,stroke:#333,stroke-width:1px,stroke-dasharray: 5 5
    
    class CoreComponents core
    class ExternalSystems external
```

Sources:
- [main.py:61-137]()
- [docker-compose.yaml:1-76]()
- [superagi/jobs/agent_executor.py:1-186]()
- [README.MD:150-175]()

## Core Components

The SuperAGI system is composed of several core components:

1. **FastAPI Backend**: The main server handling API requests, agent management, and system coordination
2. **GUI/Frontend**: Next.js-based user interface for interacting with the system
3. **Nginx Proxy**: Routes requests between frontend and backend
4. **PostgreSQL Database**: Stores system data, agent configurations, and execution history
5. **Redis**: Used for caching, message brokering, and vector storage
6. **Celery Worker**: Handles background tasks, particularly agent execution

### API Backend Components Diagram

```mermaid
graph LR
    subgraph "FastAPI Backend"
        API["FastAPI App"] --> Routers["API Routers"]
        
        Routers --> AgentRouter["Agent Router"]
        Routers --> AgentExecutionRouter["Agent Execution Router"]
        Routers --> ProjectRouter["Project Router"]
        Routers --> ToolRouter["Tool Router"]
        Routers --> ResourceRouter["Resource Router"]
        Routers --> ConfigRouter["Config Router"]
        Routers --> VectorDBRouter["Vector DB Router"]
        Routers --> ModelRouter["Model Router"]
        
        AgentRouter --> AgentController["Agent Controller"]
        AgentExecutionRouter --> AgentExecutionController["Agent Execution Controller"]
        ToolRouter --> ToolController["Tool Controller"]
        ResourceRouter --> ResourceController["Resource Controller"]
        VectorDBRouter --> VectorDBController["Vector DB Controller"]
        ModelRouter --> ModelController["Model Controller"]
        
        AgentController --> AgentService["Agent Service"]
        ToolController --> ToolService["Tool Service"]
        ResourceController --> ResourceService["Resource Service"]
    end
    
    DB[(PostgreSQL)]
    
    AgentService --> DB
    ToolService --> DB
    ResourceService --> DB
    
    classDef component fill:#f9f9f9,stroke:#333,stroke-width:1px
    classDef db fill:#f9f9f9,stroke:#333,stroke-width:1px,stroke-dasharray: 5 5
    
    class FastAPIBackend component
    class DB db
```

Sources:
- [main.py:61-137]()
- [main.py:17-41]()

## Agent Execution System

The Agent Execution System is responsible for running agents and handling their workflow steps. This is the core engine of SuperAGI that manages the agent's life cycle, from initialization to completion.

### Agent Execution Diagram

```mermaid
graph TD
    AgentExecution["Agent Execution"] --> AgentExecutor["Agent Executor"]
    
    AgentExecutor --> |"If action_type=TOOL"| AgentToolStepHandler["Agent Tool Step Handler"]
    AgentExecutor --> |"If action_type=ITERATION_WORKFLOW"| AgentIterationStepHandler["Agent Iteration Step Handler"]
    AgentExecutor --> |"If action_type=WAIT_STEP"| AgentWaitStepHandler["Agent Wait Step Handler"]
    
    AgentToolStepHandler --> |"Execute tool"| ToolManager["Tool Manager"]
    AgentIterationStepHandler --> |"Build prompt"| AgentPromptBuilder["Agent Prompt Builder"]
    AgentIterationStepHandler --> |"Call LLM"| LLMIntegration["LLM Integration"]
    AgentIterationStepHandler --> |"Parse response"| OutputParser["Output Parser"]
    
    LLMIntegration --> |"Model factory"| LLMModelFactory["LLM Model Factory"]
    LLMModelFactory --> |"Create model"| ModelInstance["Model Instance"]
    
    AgentExecutor --> |"Check permissions"| AgentPermissions["Agent Permissions"]
    AgentExecutor --> |"Check max iterations"| AgentLimits["Agent Limits"]
    
    AgentExecutor --> AgentMemory["Agent Memory"]
    AgentMemory --> VectorStoreFactory["Vector Store Factory"]
    VectorStoreFactory --> VectorStore["Vector Store"]
    
    class AgentExecution,AgentExecutor,AgentToolStepHandler,AgentIterationStepHandler,AgentWaitStepHandler,ToolManager,AgentPromptBuilder,OutputParser,LLMIntegration,LLMModelFactory,ModelInstance,AgentPermissions,AgentLimits,AgentMemory,VectorStoreFactory,VectorStore component
```

Sources:
- [superagi/jobs/agent_executor.py:37-157]()
- [superagi/agent/agent_prompt_builder.py:12-136]()
- [superagi/agent/output_parser.py:1-70]()
- [superagi/llms/llm_model_factory.py:1-55]()

## Workflow System

The Workflow System defines how agents operate through a series of steps. SuperAGI supports different workflow types for various agent behaviors.

### Agent Workflow Diagram

```mermaid
graph TD
    Agent["Agent"] --> |"has"| AgentWorkflow["Agent Workflow"]
    AgentWorkflow --> |"consists of"| WorkflowSteps["Workflow Steps"]
    
    WorkflowSteps --> ToolStep["Tool Step"]
    WorkflowSteps --> IterationStep["Iteration Step"]
    WorkflowSteps --> WaitStep["Wait Step"]
    
    ToolStep --> |"executes"| Tool["Tool"]
    IterationStep --> |"generates next steps via"| LLM["LLM"]
    WaitStep --> |"pauses for"| Delay["Time Delay"]
    
    AgentWorkflow --> |"examples"| GoalBasedWorkflow["Goal Based Workflow"]
    AgentWorkflow --> |"examples"| TaskBasedWorkflow["Task Based Workflow"]
    AgentWorkflow --> |"examples"| FixedTaskWorkflow["Fixed Task Workflow"]
    
    Agent --> |"has"| AgentConfig["Agent Configuration"]
    AgentConfig --> Goals["Goals"]
    AgentConfig --> Instructions["Instructions"]
    AgentConfig --> Constraints["Constraints"]
    AgentConfig --> Tools["Tool Selection"]
    AgentConfig --> ModelSelection["Model Selection"]
    
    Agent --> |"creates"| AgentExecution["Agent Execution"]
    AgentExecution --> |"tracks"| ExecutionFeeds["Execution Feeds"]
    AgentExecution --> |"manages"| Resources["Resources"]
    
    class Agent,AgentWorkflow,WorkflowSteps,ToolStep,IterationStep,WaitStep,Tool,LLM,Delay,GoalBasedWorkflow,TaskBasedWorkflow,FixedTaskWorkflow,AgentConfig,Goals,Instructions,Constraints,Tools,ModelSelection,AgentExecution,ExecutionFeeds,Resources component
```

Sources:
- [superagi/jobs/agent_executor.py:105-127]()
- [main.py:224-232]()

## LLM Integration System

The LLM Integration System connects SuperAGI to various large language model providers, allowing agents to use different models for their thinking and decision-making.

### LLM Integration Diagram

```mermaid
graph TD
    LLMIntegration["LLM Integration"] --> LLMModelFactory["LLM Model Factory"]
    
    LLMModelFactory --> |"creates"| BaseLLM["Base LLM"]
    
    BaseLLM --> OpenAI["OpenAI"]
    BaseLLM --> GooglePalm["Google Palm"]
    BaseLLM --> HuggingFace["Hugging Face"]
    BaseLLM --> Replicate["Replicate"]
    BaseLLM --> LocalLLM["Local LLM"]
    
    OpenAI --> |"models"| GPT35["GPT-3.5-Turbo"]
    OpenAI --> |"models"| GPT4["GPT-4"]
    
    LLMModelFactory --> |"uses"| ModelConfig["Models Config"]
    ModelConfig --> |"stored in"| Database[(Database)]
    
    LocalLLM --> |"loads"| LLMLoader["LLM Loader"]
    LLMLoader --> |"loads from"| LocalModelPath["Local Model Path"]
    
    class LLMIntegration,LLMModelFactory,BaseLLM,OpenAI,GooglePalm,HuggingFace,Replicate,LocalLLM,GPT35,GPT4,ModelConfig,Database,LLMLoader,LocalModelPath component
```

Sources:
- [superagi/llms/llm_model_factory.py:1-55]()
- [superagi/helper/llm_loader.py:1-39]()
- [superagi/llms/local_llm.py:1-96]()
- [superagi/types/model_source_types.py:1-33]()

## Tool System

The Tool System allows agents to interact with external systems and perform specific tasks. SuperAGI provides a framework for creating, managing, and using tools.

### Tool System Diagram

```mermaid
graph TD
    ToolManager["Tool Manager"] --> |"manages"| Tools["Tools"]
    ToolManager --> |"manages"| Toolkits["Toolkits"]
    
    Tools --> |"inherits from"| BaseTool["Base Tool"]
    Toolkits --> |"inherits from"| BaseToolkit["Base Toolkit"]
    
    BaseTool --> |"examples"| FileTools["File Tools"]
    BaseTool --> |"examples"| CodeTools["Code Tools"]
    BaseTool --> |"examples"| EmailTools["Email Tools"]
    BaseTool --> |"examples"| SearchTools["Search Tools"]
    BaseTool --> |"examples"| ImageGenTools["Image Generation Tools"]
    
    ToolManager --> |"registers"| ToolRegistry["Tool Registry"]
    ToolRegistry --> |"stored in"| Database[(Database)]
    
    Tools --> |"configured via"| ToolConfigs["Tool Configs"]
    ToolConfigs --> |"stored in"| Database
    
    AgentToolStepHandler["Agent Tool Step Handler"] --> |"uses"| ToolManager
    
    class ToolManager,Tools,Toolkits,BaseTool,BaseToolkit,FileTools,CodeTools,EmailTools,SearchTools,ImageGenTools,ToolRegistry,Database,ToolConfigs,AgentToolStepHandler component
```

Sources:
- [main.py:45]()
- [superagi/jobs/agent_executor.py:108-114]()

## Resource Management System

The Resource Management System handles files and data that agents work with, providing storage and retrieval capabilities.

### Resource Management Diagram

```mermaid
graph TD
    ResourceController["Resource Controller"] --> ResourceHelper["Resource Helper"]
    ResourceHelper --> |"if storage=FILE"| FileManager["File Manager"]
    ResourceHelper --> |"if storage=S3"| S3Helper["S3 Helper"]
    
    ResourceController --> ResourceSummarizer["Resource Summarizer"]
    ResourceSummarizer --> VectorStoreFactory["Vector Store Factory"]
    
    VectorStoreFactory --> |"creates"| VectorStore["Vector Store"]
    VectorStore --> |"types"| Pinecone["Pinecone"]
    VectorStore --> |"types"| Weaviate["Weaviate"]
    VectorStore --> |"types"| RedisVS["Redis Vector Store"]
    VectorStore --> |"types"| Qdrant["Qdrant"]
    VectorStore --> |"types"| ChromaDB["Chroma DB"]
    
    ResourceController --> |"operations"| Upload["Upload"]
    ResourceController --> |"operations"| Download["Download"]
    ResourceController --> |"operations"| List["List"]
    ResourceController --> |"operations"| Query["Query"]
    
    class ResourceController,ResourceHelper,FileManager,S3Helper,ResourceSummarizer,VectorStoreFactory,VectorStore,Pinecone,Weaviate,RedisVS,Qdrant,ChromaDB,Upload,Download,List,Query component
```

Sources:
- [config_template.yaml:31-43]()
- [superagi/jobs/agent_executor.py:73-78]()

## Deployment Architecture

SuperAGI can be deployed using Docker Compose, which sets up all the necessary services.

### Deployment Diagram

```mermaid
graph TD
    User["User"] --> |"HTTP requests"| Port3000["Port 3000"]
    Port3000 --> Proxy["Nginx Proxy"]
    
    Proxy --> |"/ requests"| GUI["GUI Container"]
    Proxy --> |"/api requests"| Backend["Backend Container"]
    
    Backend --> Celery["Celery Worker Container"]
    Backend --> Database["PostgreSQL Container"]
    Backend --> Redis["Redis Container"]
    Celery --> Database
    Celery --> Redis
    
    Backend --> |"mounts"| Workspace["Workspace Volume"]
    Celery --> |"mounts"| Workspace
    
    Database --> |"stores in"| PGData["PostgreSQL Data Volume"]
    Redis --> |"stores in"| RedisData["Redis Data Volume"]
    
    class User,Port3000,Proxy,GUI,Backend,Celery,Database,Redis,Workspace,PGData,RedisData component
```

Sources:
- [docker-compose.yaml:1-76]()
- [docker-compose-gpu.yml:1-96]()
- [nginx/default.conf:1-27]()
- [Dockerfile:1-39]()
- [gui/Dockerfile:1-22]()

## Key Classes and Their Relationships

This section outlines the key classes in SuperAGI and their relationships.

### Core Classes Diagram

```mermaid
classDiagram
    class Agent {
        +id
        +name
        +description
        +organisation_id
        +project_id
        +get_agent_config()
        +update_agent_config()
    }
    
    class AgentExecution {
        +id
        +agent_id
        +name
        +status
        +last_execution_time
        +num_of_calls
        +current_agent_step_id
    }
    
    class AgentConfiguration {
        +id
        +key
        +value
        +agent_id
    }
    
    class AgentWorkflow {
        +id
        +name
        +description
    }
    
    class AgentWorkflowStep {
        +id
        +unique_id
        +agent_workflow_id
        +prompt_id
        +action_type
        +output_type
    }
    
    class Tool {
        +name
        +description
        +args
        +execute()
    }
    
    class Resource {
        +id
        +name
        +path
        +type
        +storage_type
    }
    
    class Organisation {
        +id
        +name
    }
    
    class Project {
        +id
        +name
        +organisation_id
    }
    
    Agent "1" --> "many" AgentConfiguration : has
    Agent "1" --> "many" AgentExecution : has
    Agent "many" --> "1" Project : belongs to
    Project "many" --> "1" Organisation : belongs to
    Agent "many" --> "1" AgentWorkflow : uses
    AgentWorkflow "1" --> "many" AgentWorkflowStep : contains
    AgentExecution "1" --> "1" AgentWorkflowStep : current step
    Agent "many" --> "many" Tool : uses
    AgentExecution "1" --> "many" Resource : creates
```

Sources:
- [superagi/jobs/agent_executor.py:37-157]()
- [main.py:52-55]()

## Data Flow

The data flow in SuperAGI follows this general pattern:

1. User interacts with the GUI to create and manage agents
2. GUI sends requests to the backend via the Nginx proxy
3. Backend processes requests and interacts with the database
4. When an agent is executed:
   - Backend creates an agent execution record
   - Celery worker picks up the execution task
   - Agent Executor processes workflow steps
   - LLM integration provides reasoning capabilities
   - Tool system allows interaction with external systems
   - Resource management handles file operations
   - Results are stored and returned to the GUI

### Request Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant GUI
    participant Proxy
    participant Backend
    participant Celery
    participant LLM
    participant Database
    
    User->>GUI: Create agent request
    GUI->>Proxy: POST /api/agents
    Proxy->>Backend: Forward request
    Backend->>Database: Store agent config
    Database-->>Backend: Success
    Backend-->>Proxy: Response
    Proxy-->>GUI: Forward response
    GUI-->>User: Display confirmation
    
    User->>GUI: Run agent request
    GUI->>Proxy: POST /api/agentexecutions
    Proxy->>Backend: Forward request
    Backend->>Database: Create execution record
    Backend->>Celery: Queue execution task
    Celery->>Database: Read agent configuration
    Celery->>LLM: Process iteration
    LLM-->>Celery: Response
    Celery->>Database: Update execution status
    
    loop Until completion
        Celery->>Celery: Process next step
        Celery->>LLM: Make API call
        LLM-->>Celery: Process response
        Celery->>Database: Update status
    end
    
    Database-->>Backend: Status updates
    Backend-->>Proxy: Send updates
    Proxy-->>GUI: Forward updates
    GUI-->>User: Display agent progress
```

Sources:
- [superagi/jobs/agent_executor.py:39-103]()
- [main.py:61-137]()

## Configuration System

SuperAGI uses a YAML-based configuration system that allows setting up various components:

| Category | Configuration Options | Example |
|----------|----------------------|---------|
| System Keys | API keys for models and services | `OPENAI_API_KEY: "your-key-here"` |
| Database | PostgreSQL connection details | `DB_URL: postgresql://user:pass@host/db` |
| Storage | File system or S3 storage | `STORAGE_TYPE: "FILE"` |
| LLM | Model selection and parameters | `MODEL_NAME: "gpt-3.5-turbo"` |
| Vector Store | Vector database options | `RESOURCE_VECTOR_STORE: "REDIS"` |
| Tools | Tool-specific settings | `GOOGLE_API_KEY: "your-key-here"` |

Sources:
- [config_template.yaml:1-126]()

## Security Model

SuperAGI implements several security mechanisms:

1. **JWT-based Authentication**: Used for securing API endpoints
2. **Permission System**: Controls what actions agents can perform
3. **API Key Encryption**: Secures external service credentials
4. **Resource Isolation**: Docker containers provide service isolation
5. **Action Console**: Allows users to approve or deny agent actions

### Permission Flow Diagram

```mermaid
graph TD
    Agent["Agent"] --> |"requests action"| PermissionType["Permission Type"]
    PermissionType --> |"if restricted"| PermissionRequest["Permission Request"]
    PermissionType --> |"if god mode"| DirectExecution["Direct Execution"]
    
    PermissionRequest --> ActionConsole["Action Console"]
    ActionConsole --> |"user approves"| ApprovedAction["Approved Action"]
    ActionConsole --> |"user denies"| DeniedAction["Denied Action"]
    
    ApprovedAction --> ToolExecution["Tool Execution"]
    DirectExecution --> ToolExecution
    
    class Agent,PermissionType,PermissionRequest,DirectExecution,ActionConsole,ApprovedAction,DeniedAction,ToolExecution component
```

Sources:
- [gui/pages/Content/Agents/ActionConsole.js:1-162]()
- [superagi/jobs/agent_executor.py:54]()

## Conclusion

SuperAGI's architecture is designed for flexibility, scalability, and extensibility. The modular approach allows for easy addition of new components, tools, and LLM integrations. The system uses industry-standard technologies and follows a service-oriented architecture pattern, making it suitable for both development and production environments.

The key strengths of the architecture include:

1. **Modularity**: Components are loosely coupled, allowing for easy replacement or enhancement
2. **Extensibility**: The tool and LLM integration systems can be extended with new capabilities
3. **Scalability**: Separation of concerns allows for horizontal scaling of different components
4. **Container-based Deployment**: Docker-based deployment simplifies setup and ensures consistency

For more detailed information about specific components, please refer to the linked wiki pages.

---

# Page: Agent System

# Agent System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [main.py](main.py)
- [superagi/agent/agent_prompt_builder.py](superagi/agent/agent_prompt_builder.py)
- [superagi/agent/output_parser.py](superagi/agent/output_parser.py)
- [superagi/controllers/agent.py](superagi/controllers/agent.py)
- [superagi/controllers/agent_execution.py](superagi/controllers/agent_execution.py)
- [superagi/controllers/agent_execution_feed.py](superagi/controllers/agent_execution_feed.py)
- [superagi/controllers/agent_execution_permission.py](superagi/controllers/agent_execution_permission.py)
- [superagi/controllers/agent_template.py](superagi/controllers/agent_template.py)
- [superagi/controllers/budget.py](superagi/controllers/budget.py)
- [superagi/controllers/config.py](superagi/controllers/config.py)
- [superagi/controllers/organisation.py](superagi/controllers/organisation.py)
- [superagi/controllers/project.py](superagi/controllers/project.py)
- [superagi/controllers/user.py](superagi/controllers/user.py)
- [superagi/helper/json_cleaner.py](superagi/helper/json_cleaner.py)
- [superagi/helper/token_counter.py](superagi/helper/token_counter.py)
- [superagi/jobs/agent_executor.py](superagi/jobs/agent_executor.py)
- [superagi/models/agent.py](superagi/models/agent.py)
- [superagi/models/agent_execution.py](superagi/models/agent_execution.py)
- [superagi/models/agent_execution_feed.py](superagi/models/agent_execution_feed.py)
- [superagi/models/agent_template.py](superagi/models/agent_template.py)
- [tests/unit_tests/controllers/test_agent_template.py](tests/unit_tests/controllers/test_agent_template.py)

</details>



The Agent System is the core component of SuperAGI that manages the creation, execution, and monitoring of AI agents. This document explains the architecture and components of the Agent System, how agents are defined, configured, executed, and how they interact with other parts of the platform.

## System Purpose and Scope

The Agent System enables users to create and run autonomous AI agents with specific goals, instructions, and constraints. It handles the agent lifecycle from creation through execution to completion, providing mechanisms for monitoring and controlling agent behavior. This document covers:

- The architecture of the Agent System
- Agent creation and configuration 
- Agent execution workflow
- Agent templates
- Agent scheduling and monitoring

For information about specific agent workflows, see [Agent Execution](#2.2). For details about tools that agents can use, see [Tools System](#4).

## Agent System Architecture

```mermaid
graph TD
    subgraph "Agent System Architecture"
        User(["User"]) --> UI["Web Interface"]
        UI --> |"Creates/Configures"| AgentController["Agent Controller"]
        UI --> |"Executes/Monitors"| AgentExecutionController["Agent Execution Controller"]
        UI --> |"Uses/Creates"| AgentTemplateController["Agent Template Controller"]
        
        AgentController --> Agent["Agent"]
        AgentExecutionController --> AgentExecution["Agent Execution"]
        AgentTemplateController --> AgentTemplate["Agent Template"]
        
        Agent --> |"References"| AgentConfig["Agent Configuration"]
        Agent --> |"Follows"| AgentWorkflow["Agent Workflow"]
        
        AgentExecution --> |"Creates"| AgentExecutionFeed["Execution Feed"]
        AgentExecution --> |"Runs in"| AgentExecutor["Agent Executor"]
        
        AgentExecutor --> |"Manages"| StepHandlers["Step Handlers"]
        StepHandlers --> |"Iteration Step"| IterationStepHandler["Iteration Step Handler"]
        StepHandlers --> |"Tool Step"| ToolStepHandler["Tool Step Handler"]
        StepHandlers --> |"Wait Step"| WaitStepHandler["Wait Step Handler"]
        
        IterationStepHandler --> |"Uses"| PromptBuilder["Prompt Builder"]
        IterationStepHandler --> |"Uses"| OutputParser["Output Parser"]
        IterationStepHandler --> |"Calls"| LLM["LLM Integration"]
        
        AgentTemplate --> |"Creates"| Agent
    end
```

Sources:
- [superagi/jobs/agent_executor.py:37-157](superagi/jobs/agent_executor.py)
- [superagi/models/agent.py:20-302](superagi/models/agent.py)
- [superagi/controllers/agent.py:39-419](superagi/controllers/agent.py)
- [superagi/controllers/agent_execution.py:32-229](superagi/controllers/agent_execution.py)
- [superagi/controllers/agent_template.py:27-542](superagi/controllers/agent_template.py)

## Core Components

### Agent

The `Agent` entity is the central component of the Agent System. It represents an autonomous AI agent configured with specific goals, instructions, constraints, and tools.

Key properties of an Agent:
- **name**: The name of the agent
- **description**: A description of the agent's purpose
- **project_id**: The project the agent belongs to
- **agent_workflow_id**: The workflow the agent follows during execution
- **configurations**: Goals, instructions, constraints, tools, etc.

```mermaid
classDiagram
    class Agent {
        +id: Integer
        +name: String
        +project_id: Integer
        +description: String
        +agent_workflow_id: Integer
        +is_deleted: Boolean
        +fetch_configuration(session, agent_id)
        +create_agent_with_config(db, agent_config)
        +create_agent_with_template_id(db, project_id, template_id)
        +get_agent_organisation(session)
    }
    
    class AgentConfiguration {
        +id: Integer
        +agent_id: Integer
        +key: String
        +value: String
    }
    
    Agent "1" --> "*" AgentConfiguration: has
```

Sources:
- [superagi/models/agent.py:20-302](superagi/models/agent.py)

### Agent Execution

The `AgentExecution` entity represents a single run of an agent. It tracks the execution state, progress, and generates feeds that record the agent's activities.

Key properties of an AgentExecution:
- **status**: The current status (CREATED, RUNNING, PAUSED, COMPLETED, TERMINATED, etc.)
- **agent_id**: The agent being executed
- **current_agent_step_id**: The current workflow step being executed
- **last_execution_time**: The timestamp of the last execution step
- **num_of_calls**: Number of LLM calls made
- **num_of_tokens**: Number of tokens consumed

```mermaid
classDiagram
    class AgentExecution {
        +id: Integer
        +status: String
        +name: String
        +agent_id: Integer
        +last_execution_time: DateTime
        +num_of_calls: Integer
        +num_of_tokens: Integer
        +current_agent_step_id: Integer
        +permission_id: Integer
        +iteration_workflow_step_id: Integer
        +current_feed_group_id: String
        +update_tokens(session, execution_id, tokens, calls)
        +assign_next_step_id(session, execution_id, step_id)
    }
    
    class AgentExecutionFeed {
        +id: Integer
        +agent_execution_id: Integer
        +agent_id: Integer
        +feed: Text
        +role: String
        +extra_info: String
        +feed_group_id: String
        +error_message: String
    }
    
    class AgentExecutionPermission {
        +id: Integer
        +agent_execution_id: Integer
        +status: String
        +tool_name: String
        +question: String
        +user_feedback: String
    }
    
    AgentExecution "1" --> "*" AgentExecutionFeed: generates
    AgentExecution "1" --> "*" AgentExecutionPermission: requires
```

Sources:
- [superagi/models/agent_execution.py:11-214](superagi/models/agent_execution.py)
- [superagi/models/agent_execution_feed.py:8-70](superagi/models/agent_execution_feed.py)
- [superagi/controllers/agent_execution_feed.py:32-244](superagi/controllers/agent_execution_feed.py)
- [superagi/controllers/agent_execution_permission.py:20-159](superagi/controllers/agent_execution_permission.py)

### Agent Executor

The `AgentExecutor` class is responsible for executing agent workflow steps. It manages the execution flow, handles step transitions, and processes different types of steps (iteration, tool, wait).

Key functionalities:
- Executing the next step in an agent's workflow
- Managing agent's maximum iteration limits
- Handling paused executions and waiting workflows

```mermaid
sequenceDiagram
    participant User
    participant AgentExecutionController
    participant AgentExecutor
    participant StepHandlers
    participant LLM
    
    User->>AgentExecutionController: Start agent execution
    AgentExecutionController->>AgentExecutor: execute_agent(execution_id)
    
    loop Until completion
        AgentExecutor->>AgentExecutor: execute_next_step()
        AgentExecutor->>StepHandlers: Execute current workflow step
        alt Iteration Step
            StepHandlers->>LLM: Make LLM API call
            LLM-->>StepHandlers: Response
            StepHandlers->>AgentExecutor: Update execution state
        else Tool Step
            StepHandlers->>StepHandlers: Execute tool action
            StepHandlers->>AgentExecutor: Update execution state
        else Wait Step
            StepHandlers->>AgentExecutor: Pause execution
        end
    end
    
    AgentExecutor-->>AgentExecutionController: Execution completed
    AgentExecutionController-->>User: Notify completion
```

Sources:
- [superagi/jobs/agent_executor.py:37-157](superagi/jobs/agent_executor.py)
- [main.py:194-247](main.py)

### Agent Templates

The `AgentTemplate` entity provides pre-configured agent settings that can be used to create new agents quickly. Templates can be local or from the marketplace.

Key functionalities:
- Creating templates from existing agents
- Importing templates from the marketplace
- Using templates to create new agents with predefined configurations

```mermaid
classDiagram
    class AgentTemplate {
        +id: Integer
        +organisation_id: Integer
        +agent_workflow_id: Integer
        +name: String
        +description: Text
        +marketplace_template_id: Integer
        +main_keys()
        +fetch_marketplace_list(search_str, page)
        +fetch_marketplace_detail(template_id)
        +clone_agent_template_from_marketplace(db, org_id, template_id)
    }
    
    class AgentTemplateConfig {
        +id: Integer
        +agent_template_id: Integer
        +key: String
        +value: String
    }
    
    AgentTemplate "1" --> "*" AgentTemplateConfig: has
```

Sources:
- [superagi/models/agent_template.py:16-226](superagi/models/agent_template.py)
- [superagi/controllers/agent_template.py:27-542](superagi/controllers/agent_template.py)

## Agent Lifecycle

The agent lifecycle in SuperAGI consists of three main phases: creation, execution, and monitoring.

```mermaid
graph LR
    subgraph "Agent Lifecycle"
        Creation["Agent Creation"] -->|"Configure"| Configuration["Agent Configuration"]
        Configuration -->|"Initialize"| Execution["Agent Execution"]
        Execution -->|"Generate"| Feed["Execution Feed"]
        Execution -->|"Monitor"| Monitoring["Agent Monitoring"]
        Monitoring -->|"Control"| Control["User Control"]
        Control -->|"Update"| Execution
    end
```

Sources:
- [superagi/controllers/agent.py:60-164](superagi/controllers/agent.py)
- [superagi/controllers/agent_execution.py:65-151](superagi/controllers/agent_execution.py)
- [superagi/controllers/agent_execution_feed.py:152-218](superagi/controllers/agent_execution_feed.py)

### Agent Creation and Configuration

Agents are created with specific configurations that define their behavior and capabilities. These include:

1. **Basic Information**:
   - Name and description
   - Project assignment

2. **Agent Behavior Configuration**:
   - Goals (what the agent aims to achieve)
   - Instructions (guidance for the agent)
   - Constraints (limitations on agent actions)
   - Maximum iterations limit
   - Permission type (God Mode/Restricted Mode)

3. **Technical Configuration**:
   - Agent workflow (execution pattern)
   - Tools and toolkits (capabilities)
   - LLM model configuration
   - Vector database configuration

Agents can be created:
- From scratch with complete configuration
- Using agent templates (predefined configurations)
- By cloning existing agents

```mermaid
flowchart TD
    subgraph "Agent Creation Process"
        Start([Start]) --> InputConfig["Input Configuration"]
        InputConfig --> ValidateConfig["Validate Configuration"]
        ValidateConfig --> CreateAgent["Create Agent Record"]
        CreateAgent --> StoreConfig["Store Agent Configuration"]
        StoreConfig --> CreateExecution["Create Initial Execution"]
        CreateExecution --> End([End])
    end
```

Sources:
- [superagi/controllers/agent.py:60-164](superagi/controllers/agent.py)
- [superagi/models/agent.py:120-182](superagi/models/agent.py)

### Agent Execution

Agent execution follows a defined workflow that consists of steps and transitions. The main step types are:

1. **Iteration Steps**: The core reasoning steps where the agent:
   - Receives input (goals, context, memory)
   - Processes it through an LLM
   - Decides on the next action

2. **Tool Steps**: Steps where the agent:
   - Executes a specific tool
   - Processes the tool's output
   - Updates its understanding

3. **Wait Steps**: Steps where the agent:
   - Pauses execution for a specified time
   - Waits for user input or permission
   - Schedules future actions

The execution process is managed by the `AgentExecutor` which:
- Initializes the execution with the starting workflow step
- Processes each step based on its type
- Manages transitions between steps
- Tracks execution state and progress
- Handles completion, termination, and errors

```mermaid
stateDiagram-v2
    [*] --> CREATED
    CREATED --> RUNNING: Start Execution
    RUNNING --> RUNNING: Execute Step
    RUNNING --> PAUSED: User Pause
    RUNNING --> WAIT_STEP: Wait Step
    RUNNING --> WAITING_FOR_PERMISSION: Requires Permission
    RUNNING --> COMPLETED: Completion
    RUNNING --> TERMINATED: Termination
    RUNNING --> ERROR_PAUSED: Error Occurs
    PAUSED --> RUNNING: Resume
    WAIT_STEP --> RUNNING: Wait Complete
    WAITING_FOR_PERMISSION --> RUNNING: Permission Granted
    WAITING_FOR_PERMISSION --> TERMINATED: Permission Denied
    ERROR_PAUSED --> RUNNING: Error Resolved
    COMPLETED --> [*]
    TERMINATED --> [*]
```

Sources:
- [superagi/jobs/agent_executor.py:37-157](superagi/jobs/agent_executor.py)
- [superagi/controllers/agent_execution.py:65-151](superagi/controllers/agent_execution.py)

### Agent Monitoring and Control

Agents provide multiple monitoring and control mechanisms:

1. **Execution Feed**: A detailed record of the agent's thoughts, actions, and results
2. **Status Tracking**: Real-time execution status (RUNNING, PAUSED, etc.)
3. **Performance Metrics**: Token usage, number of API calls, execution time
4. **Permission System**: User approval workflow for restricted operations
5. **Control Actions**: Pause, resume, terminate execution

The user interface provides a dashboard for:
- Viewing the agent's execution feed in real-time
- Responding to permission requests
- Tracking execution metrics
- Controlling the agent's execution

```mermaid
flowchart TD
    subgraph "Agent Monitoring and Control"
        Agent["Agent Execution"] -->|"Generates"| Feed["Execution Feed"]
        Agent -->|"Updates"| Status["Execution Status"]
        Agent -->|"Records"| Metrics["Performance Metrics"]
        Agent -->|"Requests"| Permissions["User Permissions"]
        
        User["User"] -->|"Views"| Feed
        User -->|"Monitors"| Status
        User -->|"Analyzes"| Metrics
        User -->|"Responds to"| Permissions
        User -->|"Controls"| Agent
    end
```

Sources:
- [superagi/controllers/agent_execution_feed.py:152-218](superagi/controllers/agent_execution_feed.py)
- [superagi/controllers/agent_execution_permission.py:125-159](superagi/controllers/agent_execution_permission.py)

## Agent Prompt Building and Output Parsing

### Prompt Building

The `AgentPromptBuilder` constructs prompts for the LLM based on the agent's configuration and current context. Key components include:

1. **Goal Integration**: Incorporating the agent's goals
2. **Instruction Integration**: Adding user instructions
3. **Constraint Integration**: Adding constraints on the agent's behavior
4. **Tool Description**: Describing available tools and their parameters
5. **Context Management**: Including relevant context from memory and previous steps
6. **Task Management**: Managing task-based workflows

The prompt builder uses templating to inject these components into a base prompt structure.

```mermaid
flowchart TD
    subgraph "Prompt Building Process"
        Config["Agent Configuration"] --> |"Extract"| Components["Prompt Components"]
        Components --> |"Build"| BasePrompt["Base Prompt Structure"]
        Context["Execution Context"] --> |"Inject"| BasePrompt
        Memory["Agent Memory"] --> |"Enhance"| BasePrompt
        BasePrompt --> |"Finalize"| FinalPrompt["Final LLM Prompt"]
    end
```

Sources:
- [superagi/agent/agent_prompt_builder.py:12-136](superagi/agent/agent_prompt_builder.py)

### Output Parsing

The `OutputParser` processes the LLM's response to extract structured actions. Key functionalities:

1. **JSON Extraction**: Extracting JSON data from the LLM response
2. **Action Parsing**: Identifying the tool name and arguments
3. **Error Handling**: Managing malformed outputs
4. **Response Cleaning**: Removing extraneous formatting

The parsed output is then used to determine the next action the agent should take.

```mermaid
flowchart LR
    subgraph "Output Parsing Process"
        LLMResponse["LLM Response"] --> |"Extract"| JSONSection["JSON Section"]
        JSONSection --> |"Clean"| CleanedJSON["Cleaned JSON"]
        CleanedJSON --> |"Parse"| ActionData["Action Data"]
        ActionData --> |"Create"| AgentAction["Agent Action Object"]
    end
```

Sources:
- [superagi/agent/output_parser.py:11-70](superagi/agent/output_parser.py)
- [superagi/helper/json_cleaner.py:8-107](superagi/helper/json_cleaner.py)

## Agent Scheduling

SuperAGI supports scheduling agents to run at specified times and intervals. Key scheduling features include:

1. **One-time Scheduling**: Running an agent at a specific date and time
2. **Recurring Execution**: Scheduling periodic runs with a defined interval
3. **Expiration Conditions**: Setting conditions for ending scheduling (date or number of runs)
4. **Schedule Management**: Viewing, editing, and stopping schedules

```mermaid
classDiagram
    class AgentSchedule {
        +id: Integer
        +agent_id: Integer
        +start_time: DateTime
        +next_scheduled_time: DateTime
        +recurrence_interval: String
        +expiry_date: DateTime
        +expiry_runs: Integer
        +current_runs: Integer
        +status: String
    }
    
    Agent "1" --> "*" AgentSchedule: has
```

Sources:
- [superagi/controllers/agent.py:167-234](superagi/controllers/agent.py)
- [superagi/controllers/agent_execution.py:234-293](superagi/controllers/agent_execution.py)

## Integration with Other Systems

The Agent System integrates with various other components of SuperAGI:

1. **Tools System**: Agents use tools to interact with external systems and perform actions
2. **Resource Management**: Agents can access and manipulate resources (files, data)
3. **Vector Database**: Agents use vector databases for knowledge storage and retrieval
4. **LLM Integration**: Agents leverage various LLM providers for reasoning

```mermaid
flowchart TD
    subgraph "System Integration"
        Agent["Agent System"] <-->|"Utilizes"| ToolSystem["Tools System"]
        Agent <-->|"Manages"| Resources["Resource Management"]
        Agent <-->|"Queries"| VectorDB["Vector Databases"]
        Agent <-->|"Leverages"| LLM["LLM Integration"]
        Agent <-->|"Follows"| Workflows["Agent Workflows"]
    end
```

Sources:
- [superagi/jobs/agent_executor.py:37-157](superagi/jobs/agent_executor.py)
- [main.py:108-138](main.py)

## Agent API Endpoints

The Agent System exposes several API endpoints for agent management:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/agents/create` | POST | Create a new agent with configuration |
| `/agents/schedule` | POST | Create and schedule an agent |
| `/agents/stop/schedule` | POST | Stop a scheduled agent |
| `/agents/edit/schedule` | PUT | Edit a scheduled agent |
| `/agents/get/project/{project_id}` | GET | Get all agents for a project |
| `/agents/delete/{agent_id}` | PUT | Delete (soft) an agent |
| `/agentexecutions/add` | POST | Create a new agent execution |
| `/agentexecutions/add_run` | POST | Create a new agent run with configuration |
| `/agentexecutions/get/{agent_execution_id}` | GET | Get an agent execution by ID |
| `/agentexecutions/get/agent/{agent_id}` | GET | Get executions for an agent |
| `/agentexecutionfeeds/get/execution/{agent_execution_id}` | GET | Get execution feeds |
| `/agent_templates/list` | GET | List available agent templates |
| `/agent_templates/get/{agent_template_id}` | GET | Get a specific agent template |

Sources:
- [superagi/controllers/agent.py:39-419](superagi/controllers/agent.py)
- [superagi/controllers/agent_execution.py:32-229](superagi/controllers/agent_execution.py)
- [superagi/controllers/agent_execution_feed.py:32-244](superagi/controllers/agent_execution_feed.py)
- [superagi/controllers/agent_template.py:27-542](superagi/controllers/agent_template.py)

## Conclusion

The Agent System is the core of SuperAGI, providing a flexible framework for creating, configuring, and running autonomous AI agents. It integrates with other system components to provide a comprehensive agent platform with powerful capabilities for reasoning, tool usage, and autonomous operation.

---

# Page: Agent Creation and Configuration

# Agent Creation and Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [gui/pages/Content/Agents/ActivityFeed.js](gui/pages/Content/Agents/ActivityFeed.js)
- [gui/pages/Content/Agents/AgentCreate.js](gui/pages/Content/Agents/AgentCreate.js)
- [gui/pages/Content/Agents/AgentSchedule.js](gui/pages/Content/Agents/AgentSchedule.js)
- [gui/pages/Content/Agents/AgentWorkspace.js](gui/pages/Content/Agents/AgentWorkspace.js)
- [gui/pages/Content/Agents/Agents.js](gui/pages/Content/Agents/Agents.js)
- [gui/pages/Content/Agents/Agents.module.css](gui/pages/Content/Agents/Agents.module.css)
- [gui/pages/Content/Agents/Details.js](gui/pages/Content/Agents/Details.js)
- [gui/pages/Content/Agents/ResourceList.js](gui/pages/Content/Agents/ResourceList.js)
- [gui/pages/Content/Agents/ResourceManager.js](gui/pages/Content/Agents/ResourceManager.js)
- [gui/pages/Dashboard/Content.js](gui/pages/Dashboard/Content.js)
- [gui/pages/_app.css](gui/pages/_app.css)
- [gui/pages/api/DashboardService.js](gui/pages/api/DashboardService.js)
- [gui/utils/utils.js](gui/utils/utils.js)
- [superagi/controllers/agent.py](superagi/controllers/agent.py)
- [superagi/controllers/agent_template.py](superagi/controllers/agent_template.py)
- [superagi/models/agent.py](superagi/models/agent.py)
- [superagi/models/agent_execution.py](superagi/models/agent_execution.py)
- [superagi/models/agent_execution_feed.py](superagi/models/agent_execution_feed.py)
- [superagi/models/agent_template.py](superagi/models/agent_template.py)
- [tests/unit_tests/controllers/test_agent_template.py](tests/unit_tests/controllers/test_agent_template.py)

</details>



This document provides a technical overview of how agents are created and configured in SuperAGI. It covers the UI components, API endpoints, data models, and configuration options available when creating agents. For information about running agents after they've been created, see [Agent Execution](#2.2).

## Overview of Agent Creation Architecture

The agent creation process in SuperAGI involves both frontend and backend components that work together to create, configure, and store agent definitions.

```mermaid
flowchart TD
    User(["User"]) --> AgentCreateUI["AgentCreate.js Component"]
    AgentCreateUI -->|"handleAddAgent()"| API["POST /agents/create"]
    API -->|"create_agent_with_config()"| AgentModel["Agent Model"]
    API -->|"stores config"| AgentConfig["AgentConfiguration"]
    API -->|"creates"| AgentExec["AgentExecution"]
    AgentExec -->|"configures"| ExecConfig["AgentExecutionConfiguration"]
    AgentTemplate["AgentTemplate"] -.->|"optional template"| AgentCreateUI
```

Sources:
- [gui/pages/Content/Agents/AgentCreate.js:497-541](gui/pages/Content/Agents/AgentCreate.js:497-541)
- [superagi/controllers/agent.py:60-163](superagi/controllers/agent.py:60-163)

## Data Models

Agent configurations are stored using several related database models that maintain different aspects of the agent's definition:

```mermaid
classDiagram
    class Agent {
        id: int
        name: string
        project_id: int
        description: string
        agent_workflow_id: int
        is_deleted: bool
    }
    
    class AgentConfiguration {
        id: int
        agent_id: int
        key: string
        value: string
    }
    
    class AgentExecution {
        id: int
        agent_id: int
        status: string
        name: string
        current_agent_step_id: int
        iteration_workflow_step_id: int
    }
    
    class AgentExecutionConfiguration {
        id: int
        agent_execution_id: int
        key: string
        value: string
    }
    
    Agent "1" -- "*" AgentConfiguration: has
    Agent "1" -- "*" AgentExecution: has
    AgentExecution "1" -- "*" AgentExecutionConfiguration: has
```

Sources:
- [superagi/models/agent.py:20-41](superagi/models/agent.py:20-41)
- [superagi/models/agent_execution.py:11-41](superagi/models/agent_execution.py:11-41)

## Agent Configuration Parameters

Agents in SuperAGI can be configured with the following parameters:

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| name | string | Name of the agent | *Required* |
| description | string | Description of the agent | *Required* |
| project_id | int | Project the agent belongs to | *Required* |
| goal | string[] | List of goals for the agent | *Required* |
| instruction | string[] | Additional instructions | `[]` |
| agent_workflow | string | Workflow type (e.g., "Goal Based Workflow") | *Required* |
| constraints | string[] | Limitations on agent behavior | System defaults |
| tools | int[] | Tool IDs the agent can use | *Required* |
| exit | string | Exit criterion | "No exit criterion" |
| iteration_interval | int | Time between iterations (ms) | 500 |
| model | string | LLM model (e.g., "gpt-4") | *Required* |
| permission_type | string | "God Mode" or "RESTRICTED" | "God Mode" |
| LTM_DB | string | Long-term memory database | "Pinecone" |
| max_iterations | int | Maximum iterations allowed | 25 |
| knowledge | int | Knowledge base ID (optional) | null |

Sources:
- [gui/pages/Content/Agents/AgentCreate.js:549-569](gui/pages/Content/Agents/AgentCreate.js:549-569)
- [superagi/controllers/agent.py:60-96](superagi/controllers/agent.py:60-96)

## Frontend Implementation

The agent creation UI is implemented in the `AgentCreate.js` React component. This component provides an interface for configuring all agent parameters and submitting them to the backend.

```mermaid
flowchart TD
    AgentCreate["AgentCreate Component"]
    AgentCreate --> BasicInfo["Basic Information\n- Name\n- Description"]
    AgentCreate --> Goals["Goals Editor"]
    AgentCreate --> Instructions["Instructions Editor"]
    AgentCreate --> ToolSelect["Tool Selection"]
    AgentCreate --> AdvancedOptions["Advanced Options"]
    AdvancedOptions --> ModelSelect["Model Selection"]
    AdvancedOptions --> Constraints["Constraints Editor"]
    AdvancedOptions --> Permissions["Permission Type"]
    AdvancedOptions --> Memory["Memory Settings"]
    AdvancedOptions --> MaxIterations["Max Iterations"]
    
    AgentCreate -->|"validateAgentData()"| Validation
    AgentCreate -->|"handleAddAgent()"| SubmitAgent["Submit to API"]
    SubmitAgent --> CreateAgent["createAgent() API call"]
```

Key features of the agent creation UI:

1. Form fields for all configurable parameters
2. Validation of required fields
3. Pre-filled values for optional parameters 
4. Support for creating agents from templates
5. File upload for agent resources

Sources:
- [gui/pages/Content/Agents/AgentCreate.js:38-96](gui/pages/Content/Agents/AgentCreate.js:38-96)
- [gui/pages/Content/Agents/AgentCreate.js:454-493](gui/pages/Content/Agents/AgentCreate.js:454-493)

### Agent Creation Flow in UI

When creating an agent through the UI, the following steps occur:

1. User fills out the agent configuration form
2. User clicks "Create" button, triggering `handleAddAgent()`
3. Form data is validated with `validateAgentData()`
4. If valid, agent data is prepared with `setAgentData()`
5. API call is made to `createAgent()` endpoint
6. On success, any resources are uploaded and the agent is executed

Sources:
- [gui/pages/Content/Agents/AgentCreate.js:495-606](gui/pages/Content/Agents/AgentCreate.js:495-606)

## Backend Implementation

### Agent Creation API Endpoint

The primary endpoint for agent creation is:

```
POST /agents/create
```

Implemented in `create_agent_with_config()` in `superagi/controllers/agent.py`, this endpoint:

1. Validates the agent configuration
2. Creates an `Agent` record in the database
3. Sets up the agent workflow
4. Creates an initial `AgentExecution` with "CREATED" status
5. Stores all configuration parameters
6. Returns the agent ID, execution ID, and other metadata

Sources:
- [superagi/controllers/agent.py:60-163](superagi/controllers/agent.py:60-163)

### Agent Creation Process Flow

The backend process for creating an agent involves:

```mermaid
flowchart TD
    APIRequest["API Request\n/agents/create"] --> ValidateProject["Validate Project Exists"]
    ValidateProject --> ValidateTools["Validate Tools Exist"]
    ValidateTools --> CreateAgent["Create Agent Record"]
    CreateAgent --> SetupWorkflow["Set Up Agent Workflow"]
    SetupWorkflow --> CreateExecution["Create Agent Execution"]
    CreateExecution --> StoreConfig["Store Agent Configuration"]
    StoreConfig --> TrackEvents["Track Events"]
    TrackEvents --> ReturnResponse["Return Response"]
```

Sources:
- [superagi/controllers/agent.py:60-163](superagi/controllers/agent.py:60-163)

### Data Storage Process

When an agent is created, the configuration is stored across multiple models:

1. Basic information (name, description) in the `Agent` model
2. Configuration parameters as key-value pairs in `AgentConfiguration`
3. Execution information in `AgentExecution`
4. Execution-specific configuration in `AgentExecutionConfiguration`

This flexible approach allows for storing diverse configuration types and supports both agent templates and direct agent creation.

Sources:
- [superagi/models/agent.py:54-155](superagi/models/agent.py:54-155)

## Agent Templates

Agent templates provide reusable configurations for creating new agents. Templates can be:

1. Local - Created by users within their organization
2. Marketplace - Downloaded from the SuperAGI marketplace

```mermaid
classDiagram
    class AgentTemplate {
        id: int
        organisation_id: int
        name: string
        description: string
        agent_workflow_id: int
        marketplace_template_id: int
    }
    
    class AgentTemplateConfig {
        id: int
        agent_template_id: int
        key: string
        value: string
    }
    
    class Agent {
        id: int
        name: string
        description: string
        project_id: int
        agent_workflow_id: int
    }
    
    AgentTemplate "1" -- "*" AgentTemplateConfig: has
    AgentTemplate ..> Agent: creates
```

Working with templates involves:

1. Selecting a template when creating a new agent
2. The template's configuration is loaded into the agent creation form
3. Users can modify the configuration if needed
4. When submitted, a new agent is created with the template's configuration

Users can also save existing agents as templates using the "Save as Template" feature in the agent workspace.

Sources:
- [superagi/models/agent_template.py:16-37](superagi/models/agent_template.py:16-37)
- [gui/pages/Content/Agents/AgentCreate.js:187-201](gui/pages/Content/Agents/AgentCreate.js:187-201)
- [gui/pages/Content/Agents/AgentWorkspace.js:315-323](gui/pages/Content/Agents/AgentWorkspace.js:315-323)

## Agent Scheduling

Agents can be scheduled to run at specified times with optional recurrence. The scheduling feature enables:

1. Running agents at a future time
2. Setting up recurring agent runs at defined intervals
3. Configuring expiry conditions (date or number of runs)

```mermaid
classDiagram
    class Agent {
        id: int
        name: string
    }
    
    class AgentSchedule {
        id: int
        agent_id: int
        start_time: datetime
        next_scheduled_time: datetime
        recurrence_interval: string
        expiry_date: date
        expiry_runs: int
        current_runs: int
        status: string
    }
    
    Agent "1" -- "0..1" AgentSchedule: has
```

Sources:
- [gui/pages/Content/Agents/AgentSchedule.js:12-73](gui/pages/Content/Agents/AgentSchedule.js:12-73)
- [superagi/controllers/agent.py:167-234](superagi/controllers/agent.py:167-234)

## Agent Permissions

SuperAGI supports two permission types for agents:

1. **God Mode**: The agent operates autonomously without requiring permission for tool execution
2. **RESTRICTED**: The agent must request permission before using any tool

The permission type is configured during agent creation and affects the agent's behavior during execution.

Sources:
- [gui/pages/Content/Agents/AgentCreate.js:97-101](gui/pages/Content/Agents/AgentCreate.js:97-101)
- [gui/pages/Content/Agents/AgentWorkspace.js:480-486](gui/pages/Content/Agents/AgentWorkspace.js:480-486)

## Agent Resources

Agents can have resources (files) associated with them. These are managed in two categories:

1. **Input resources**: Files uploaded by users that the agent can access
2. **Output resources**: Files generated by the agent during execution

Resources are managed through the ResourceManager component in the agent workspace, which allows:
- Uploading new files
- Viewing existing resources
- Downloading resources

Sources:
- [gui/pages/Content/Agents/ResourceManager.js:10-117](gui/pages/Content/Agents/ResourceManager.js:10-117)
- [gui/pages/Content/Agents/ResourceList.js:6-82](gui/pages/Content/Agents/ResourceList.js:6-82)

## Creating Agents Programmatically

For developers wanting to create agents programmatically, the process involves:

1. Prepare the agent configuration as a JSON object
2. Send a POST request to the `/agents/create` endpoint
3. Include all required parameters (name, description, goals, tools, model, etc.)
4. Process the response to get the agent ID and execution ID

Example agent configuration structure:

```json
{
  "name": "My Agent",
  "project_id": 1,
  "description": "Agent description",
  "goal": ["Achieve goal 1", "Achieve goal 2"],
  "instruction": ["Optional instruction"],
  "agent_workflow": "Goal Based Workflow",
  "constraints": ["System defined constraint", "Custom constraint"],
  "tools": [1, 2, 3],
  "model": "gpt-4",
  "permission_type": "God Mode",
  "LTM_DB": "Pinecone",
  "max_iterations": 25
}
```

Sources:
- [superagi/controllers/agent.py:60-163](superagi/controllers/agent.py:60-163)

## Conclusion

The agent creation and configuration system in SuperAGI provides a flexible, robust framework for defining autonomous agents with specific capabilities and constraints. Through the UI or API, users can configure agents with precise goals, tools, and execution parameters to accomplish a wide variety of tasks.

---

# Page: Agent Execution

# Agent Execution

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [main.py](main.py)
- [superagi/agent/agent_prompt_builder.py](superagi/agent/agent_prompt_builder.py)
- [superagi/agent/output_parser.py](superagi/agent/output_parser.py)
- [superagi/controllers/agent_execution.py](superagi/controllers/agent_execution.py)
- [superagi/controllers/agent_execution_feed.py](superagi/controllers/agent_execution_feed.py)
- [superagi/controllers/agent_execution_permission.py](superagi/controllers/agent_execution_permission.py)
- [superagi/controllers/budget.py](superagi/controllers/budget.py)
- [superagi/controllers/config.py](superagi/controllers/config.py)
- [superagi/controllers/organisation.py](superagi/controllers/organisation.py)
- [superagi/controllers/project.py](superagi/controllers/project.py)
- [superagi/controllers/user.py](superagi/controllers/user.py)
- [superagi/helper/json_cleaner.py](superagi/helper/json_cleaner.py)
- [superagi/helper/token_counter.py](superagi/helper/token_counter.py)
- [superagi/jobs/agent_executor.py](superagi/jobs/agent_executor.py)

</details>



This document explains the agent execution process in SuperAGI - how agents run, process tasks, use tools, and generate outputs. The execution system is responsible for running agents after they've been created and configured (for info about agent creation and configuration, see [Agent Creation and Configuration](#2.1)).

## Agent Execution Overview

The agent execution system is the core engine that powers the autonomous operation of agents in SuperAGI. It handles the entire lifecycle of an agent's runtime, from initialization to completion, managing the agent's thinking process, tool usage, and interaction with users.

```mermaid
flowchart TD
    subgraph "Agent Execution Process"
        direction TB
        Start["Start Execution"] --> Initialize["Initialize Agent Environment"]
        Initialize --> IterationStep["Process Iteration Step"]
        IterationStep --> ToolStep["Execute Tool Actions"]
        ToolStep --> CheckCompletion{"Completed or\nMax Iterations?"}
        CheckCompletion -- "Yes" --> End["End Execution"]
        CheckCompletion -- "No" --> IterationStep
        
        IterationStep -. "May require\npermission" .-> Permission["Request User Permission"]
        Permission --> IterationStep
        
        IterationStep -. "May need\nto wait" .-> Wait["Wait Step"]
        Wait --> IterationStep
    end
```

Sources:
- [superagi/jobs/agent_executor.py:37-157]()
- [superagi/controllers/agent_execution.py:65-149]()

## Key Components of Agent Execution

```mermaid
classDiagram
    class AgentExecutor {
        +execute_next_step(agent_execution_id)
        +_check_for_max_iterations()
        +execute_waiting_workflows()
        -__execute_workflow_step()
    }
    
    class AgentIterationStepHandler {
        +execute_step()
    }
    
    class AgentToolStepHandler {
        +execute_step()
    }
    
    class AgentWaitStepHandler {
        +execute_step()
        +handle_next_step()
    }
    
    class AgentPromptBuilder {
        +replace_main_variables()
        +replace_task_based_variables()
        +add_tools_to_prompt()
    }
    
    class OutputParser {
        +parse()
    }
    
    AgentExecutor --> AgentIterationStepHandler : uses
    AgentExecutor --> AgentToolStepHandler : uses
    AgentExecutor --> AgentWaitStepHandler : uses
    AgentIterationStepHandler --> AgentPromptBuilder : uses
    AgentIterationStepHandler --> OutputParser : uses
```

Sources:
- [superagi/jobs/agent_executor.py:37-157]()
- [superagi/agent/agent_prompt_builder.py:12-136]()
- [superagi/agent/output_parser.py:21-70]()

## Agent Execution Lifecycle

The execution lifecycle begins when an agent is created and configured in the SuperAGI system.

### 1. Initializing Agent Execution

When a new agent execution is requested, the system:

1. Creates an `AgentExecution` record
2. Sets initial status to "CREATED" then "RUNNING"
3. Configures the execution with the agent's parameters
4. Schedules the execution with the worker system

```mermaid
sequenceDiagram
    actor User
    participant API as "FastAPI Backend"
    participant AEC as "AgentExecutionController"
    participant DB as "Database"
    participant Worker as "Worker System"
    participant AE as "AgentExecutor"
    
    User->>API: Request agent execution
    API->>AEC: create_agent_execution() or create_agent_run()
    AEC->>DB: Create AgentExecution record
    AEC->>DB: Set status to "RUNNING"
    AEC->>DB: Store execution configurations
    AEC->>Worker: execute_agent.delay(execution_id)
    Worker->>AE: execute_next_step(execution_id)
    AE-->>User: Execution started
```

Sources:
- [superagi/controllers/agent_execution.py:65-149]()
- [superagi/controllers/agent_execution.py:152-231]()
- [main.py:148-149]()

### 2. Workflow Step Execution

The `AgentExecutor` processes execution in distinct workflow steps:

- **Iteration Step**: Handles the agent's reasoning and task planning
- **Tool Step**: Executes specific tools based on the agent's decisions
- **Wait Step**: Manages waiting periods for user approval or scheduled delays

```mermaid
flowchart TD
    subgraph "Workflow Step Execution"
        direction TB
        ExecuteStep["execute_next_step()"] --> CheckAgent["Load agent & configuration"]
        CheckAgent --> CheckStatus{"Check execution\nstatus"}
        CheckStatus -- "Running or\nWaiting" --> ExecuteWorkflow["__execute_workflow_step()"]
        CheckStatus -- "Completed or\nTerminated" --> End["End"]
        
        ExecuteWorkflow --> CheckStepType{"Check step type"}
        CheckStepType -- "Iteration" --> IterationHandler["AgentIterationStepHandler"]
        CheckStepType -- "Tool" --> ToolHandler["AgentToolStepHandler"]
        CheckStepType -- "Wait" --> WaitHandler["AgentWaitStepHandler"]
        
        IterationHandler --> NextStep["Schedule next step"]
        ToolHandler --> NextStep
        WaitHandler --> NextStep
        NextStep --> End
    end
```

Sources:
- [superagi/jobs/agent_executor.py:39-102]()
- [superagi/jobs/agent_executor.py:105-127]()

### 3. Iteration Step Processing

During an iteration step, the agent:

1. Builds a prompt based on goals, instructions, constraints, and tools
2. Sends the prompt to the configured LLM
3. Parses the LLM response to determine the next action
4. Updates the agent's state and execution feed

Sources:
- [superagi/agent/agent_prompt_builder.py:66-94]()
- [superagi/agent/output_parser.py:21-70]()

### 4. Tool Execution

When executing a tool, the system:

1. Validates the tool action
2. Checks permissions if restricted mode is enabled
3. Executes the selected tool with provided arguments
4. Captures and stores the tool's output
5. Updates the agent's execution feed with results

Sources:
- [superagi/jobs/agent_executor.py:108-114]()

## Agent Execution Status Management

Agent executions progress through various statuses throughout their lifecycle:

| Status | Description |
|--------|-------------|
| CREATED | Initial status when execution is first created |
| RUNNING | Actively processing tasks and executing steps |
| PAUSED | Execution manually paused by user |
| COMPLETED | All tasks successfully completed |
| TERMINATED | Execution prematurely ended |
| WAITING_FOR_PERMISSION | Waiting for user approval to proceed |
| WAIT_STEP | In a scheduled waiting period |
| ERROR_PAUSED | Paused due to an error |
| ITERATION_LIMIT_EXCEEDED | Stopped after reaching maximum iterations |

Sources:
- [superagi/controllers/agent_execution.py:340-347]()
- [superagi/jobs/agent_executor.py:47-56]()
- [superagi/jobs/agent_executor.py:143-157]()

## Permission System

The permission system allows agents to request user approval before executing certain actions:

```mermaid
sequenceDiagram
    participant Agent as "Agent Execution"
    participant DB as "Database"
    participant UI as "User Interface"
    participant User
    
    Agent->>DB: Create permission request
    Agent->>DB: Set status to "WAITING_FOR_PERMISSION"
    UI->>DB: Poll for pending permissions
    UI-->>User: Display permission request
    User->>UI: Approve/Reject with feedback
    UI->>DB: Update permission status
    DB->>Agent: Resume execution with decision
```

Sources:
- [superagi/controllers/agent_execution_permission.py:124-158]()
- [superagi/controllers/agent_execution_feed.py:188-204]()

## Execution Feed System

The execution feed system captures and stores the agent's thinking process, actions, and results:

```mermaid
flowchart TD
    subgraph "Execution Feed System"
        direction TB
        AgentAction["Agent Action"] --> CreateFeed["Create Feed Entry"]
        CreateFeed --> StoreFeed["Store in Database"]
        StoreFeed --> UpdateUI["Update UI Feed"]
        
        subgraph "Feed Types"
            Thinking["Thinking Process"]
            ToolExecution["Tool Execution"]
            ToolResult["Tool Result"]
            Error["Error Message"]
        end
        
        CreateFeed --> Thinking
        CreateFeed --> ToolExecution
        CreateFeed --> ToolResult
        CreateFeed --> Error
    end
```

Sources:
- [superagi/controllers/agent_execution_feed.py:58-85]()
- [superagi/controllers/agent_execution_feed.py:151-218]()

## Token Usage Tracking

The system tracks token usage to monitor LLM consumption and enforce iteration limits:

1. Each agent interaction with the LLM increments the token count
2. The `TokenCounter` utility measures token usage accurately
3. When max iterations are reached, the agent execution is stopped

Sources:
- [superagi/helper/token_counter.py:37-98]()
- [superagi/jobs/agent_executor.py:143-157]()

## Scheduled and Recurring Executions

SuperAGI supports scheduling agents to run at specific times or on recurring intervals:

```mermaid
flowchart TD
    subgraph "Agent Scheduling System"
        direction TB
        Schedule["Schedule Agent"] --> ConfigureSchedule["Configure Schedule Parameters"]
        ConfigureSchedule --> StoreSchedule["Store Schedule in Database"]
        StoreSchedule --> WaitForTime["Wait for Scheduled Time"]
        WaitForTime --> StartExecution["Start Agent Execution"]
        StartExecution --> CheckRecurring{"Is Recurring?"}
        CheckRecurring -- "Yes" --> ScheduleNext["Schedule Next Run"]
        CheckRecurring -- "No" --> End["End Schedule"]
        
        subgraph "Schedule Parameters"
            StartTime["Start Time"]
            RecurrenceInterval["Recurrence Interval"]
            ExpiryDate["Expiry Date"]
            ExpiryRuns["Maximum Runs"]
        end
    end
```

Sources:
- [superagi/controllers/agent_execution.py:234-293]()

## Execution Wait Steps

The agent can enter wait periods either by design or when waiting for external input:

1. **Scheduled Waits**: Time-based pauses configured in the workflow
2. **Permission Waits**: Waiting for user approval to continue
3. **Resuming from Waits**: Automatic or manual resumption of execution

The system periodically checks waiting executions to resume them when appropriate.

Sources:
- [superagi/jobs/agent_executor.py:159-186]()

## Integration with External Systems

Agent execution integrates with several other system components:

1. **LLM Integration**: Connects to various language models for agent reasoning
2. **Vector Stores**: Accesses knowledge stored in vector databases for context
3. **Event Tracking**: Records execution events for monitoring and analytics
4. **Resource Management**: Manages files and resources used during execution

Sources:
- [superagi/jobs/agent_executor.py:62-81]()
- [superagi/controllers/agent_execution.py:130-146]()

## Conclusion

The agent execution system is the heart of SuperAGI, orchestrating the complex process of agent operation from start to finish. It manages the interaction between the agent's reasoning process, tool usage, and user feedback, enabling autonomous operation while maintaining safety and control through various monitoring and permission mechanisms.

---

# Page: Agent Templates

# Agent Templates

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [gui/pages/Content/Agents/ActivityFeed.js](gui/pages/Content/Agents/ActivityFeed.js)
- [gui/pages/Content/Agents/AgentCreate.js](gui/pages/Content/Agents/AgentCreate.js)
- [gui/pages/Content/Agents/AgentSchedule.js](gui/pages/Content/Agents/AgentSchedule.js)
- [gui/pages/Content/Agents/AgentTemplatesList.js](gui/pages/Content/Agents/AgentTemplatesList.js)
- [gui/pages/Content/Agents/AgentWorkspace.js](gui/pages/Content/Agents/AgentWorkspace.js)
- [gui/pages/Content/Agents/Agents.js](gui/pages/Content/Agents/Agents.js)
- [gui/pages/Content/Agents/Agents.module.css](gui/pages/Content/Agents/Agents.module.css)
- [gui/pages/Content/Agents/Details.js](gui/pages/Content/Agents/Details.js)
- [gui/pages/Content/Agents/ResourceList.js](gui/pages/Content/Agents/ResourceList.js)
- [gui/pages/Content/Agents/ResourceManager.js](gui/pages/Content/Agents/ResourceManager.js)
- [gui/pages/Content/Marketplace/AgentTemplate.js](gui/pages/Content/Marketplace/AgentTemplate.js)
- [gui/pages/Content/Marketplace/Market.js](gui/pages/Content/Marketplace/Market.js)
- [gui/pages/Content/Marketplace/Market.module.css](gui/pages/Content/Marketplace/Market.module.css)
- [gui/pages/Content/Marketplace/MarketAgent.js](gui/pages/Content/Marketplace/MarketAgent.js)
- [gui/pages/Content/Marketplace/MarketTools.js](gui/pages/Content/Marketplace/MarketTools.js)
- [gui/pages/Content/Marketplace/MarketplacePublic.js](gui/pages/Content/Marketplace/MarketplacePublic.js)
- [gui/pages/Dashboard/Content.js](gui/pages/Dashboard/Content.js)
- [gui/pages/_app.css](gui/pages/_app.css)
- [gui/pages/api/DashboardService.js](gui/pages/api/DashboardService.js)
- [gui/public/images/tick.svg](gui/public/images/tick.svg)
- [gui/utils/utils.js](gui/utils/utils.js)
- [superagi/controllers/agent.py](superagi/controllers/agent.py)
- [superagi/controllers/agent_template.py](superagi/controllers/agent_template.py)
- [superagi/models/agent.py](superagi/models/agent.py)
- [superagi/models/agent_execution.py](superagi/models/agent_execution.py)
- [superagi/models/agent_execution_feed.py](superagi/models/agent_execution_feed.py)
- [superagi/models/agent_template.py](superagi/models/agent_template.py)
- [tests/unit_tests/controllers/test_agent_template.py](tests/unit_tests/controllers/test_agent_template.py)

</details>



Agent Templates in SuperAGI provide a mechanism to save, reuse, and share agent configurations. They allow users to quickly create new agents based on predefined configurations, reducing repetitive setup work and enabling the sharing of effective agent designs across the platform.

For information about creating agents from scratch, see [Agent Creation and Configuration](#2.1). For details about how agents execute after creation, see [Agent Execution](#2.2).

## Purpose and Function

Agent Templates serve as blueprints for creating new agents with predefined configurations. These templates store all essential configuration parameters including:

- Goals and instructions
- Constraints
- Selected tools
- Model settings
- Workflow type
- Maximum iterations
- Permission types
- Memory settings

Templates can be created by saving existing agent configurations, installed from the marketplace, or built from scratch. Once a template is available, users can select it when creating a new agent to automatically populate configuration fields, which can then be customized as needed.

Sources:
- [superagi/models/agent_template.py:16-35]()
- [gui/pages/Content/Agents/AgentCreate.js:187-195]()

## Template Data Structure

An Agent Template consists of two main components: the template metadata and the template configuration data.

```mermaid
classDiagram
    class AgentTemplate {
        id: Integer
        organisation_id: Integer
        agent_workflow_id: Integer
        name: String
        description: String
        marketplace_template_id: Integer
    }
    
    class AgentTemplateConfig {
        id: Integer
        agent_template_id: Integer
        key: String
        value: Text
    }
    
    class AgentWorkflow {
        id: Integer
        name: String
        description: String
    }
    
    AgentTemplate "1" -- "many" AgentTemplateConfig: has
    AgentTemplate "many" -- "1" AgentWorkflow: uses
```

**Template Metadata** (AgentTemplate):
- Basic information including name, description
- Organizational ownership
- Associated agent workflow type
- Marketplace reference (if installed from marketplace)

**Template Configuration** (AgentTemplateConfig):
- Stored as key-value pairs
- Contains all agent settings and parameters
- Includes goals, constraints, tools, model settings, etc.

Sources:
- [superagi/models/agent_template.py:16-35]()
- [superagi/models/agent_template_config.py]()
- [superagi/controllers/agent_template.py:27-50]()

## Creating and Managing Templates

### Saving an Agent as a Template

Users can save an existing agent's configuration as a template for future use:

```mermaid
sequenceDiagram
    participant User
    participant AgentWorkspace as "Agent Workspace UI"
    participant API as "Backend API"
    participant DB as "Database"
    
    User->>AgentWorkspace: Click "Save as Template" in dropdown
    AgentWorkspace->>API: saveAgentAsTemplate(agentId, executionId)
    API->>DB: Fetch agent configuration
    API->>DB: Create new AgentTemplate
    API->>DB: Save configurations as AgentTemplateConfig
    API-->>AgentWorkspace: Success response
    AgentWorkspace-->>User: Success toast notification
```

An agent's current configuration can be saved as a template from the agent workspace by clicking on the dropdown menu and selecting "Save as Template". This creates a new template that captures all the agent's current settings.

Sources:
- [gui/pages/Content/Agents/AgentWorkspace.js:314-323]()
- [superagi/controllers/agent_template.py:262-293]()

### Editing Templates

Templates can be modified after creation. When a user creates an agent from a template and has the "Edit Template" option available, they can make changes to the template settings and update the stored template.

Sources:
- [gui/pages/Content/Agents/AgentCreate.js:686-724]()
- [superagi/controllers/agent_template.py:347-400]()

## Template Selection and Usage

### Template Selection Interface

When creating a new agent, users are presented with a template selection interface that displays available templates:

```mermaid
flowchart TD
    A["User accesses 'Create Agent'"] --> B["View Template Selection"]
    B --> C{"Choose option"}
    C -->|"Select Template"| D["Template loads configuration"]
    C -->|"Build from Scratch"| E["Start with empty configuration"]
    C -->|"Browse Marketplace"| F["View Marketplace Templates"]
    D --> G["Modify configuration as needed"]
    E --> G
    F --> H["Install Template"]
    H --> D
    G --> I["Create Agent"]
```

The template selection interface shows local templates that the user has created or installed. Each template displays its name and description to help users make an appropriate selection.

Sources:
- [gui/pages/Content/Agents/AgentTemplatesList.js:18-58]()
- [gui/pages/Dashboard/Content.js:463-466]()

### Creating an Agent from a Template

When a template is selected, its configuration is loaded into the agent creation form:

1. Template data is fetched from the backend API
2. Form fields are automatically populated with template values
3. Users can modify any settings as needed
4. Upon submission, a new agent is created with the current configuration

The template itself remains unchanged unless explicitly edited and updated.

Sources:
- [gui/pages/Content/Agents/AgentCreate.js:187-206]()
- [gui/pages/Content/Agents/AgentCreate.js:274-291]()

## Marketplace Integration

SuperAGI includes a marketplace where users can discover, install, and publish agent templates.

```mermaid
flowchart TB
    subgraph "Local System"
        A["Local Templates"] 
        B["Agent Creation"]
        C["Agent Workspace"]
    end
    
    subgraph "Marketplace"
        D["Public Templates"]
        E["Template Details"]
    end
    
    A -->|"Used in"| B
    C -->|"Save as Template"| A
    D -->|"View Details"| E
    E -->|"Install"| A
    A -->|"Publish"| D
    
    style A fill:#f5f5f5,stroke:#333
    style B fill:#f5f5f5,stroke:#333
    style C fill:#f5f5f5,stroke:#333
    style D fill:#f5f5f5,stroke:#333
    style E fill:#f5f5f5,stroke:#333
```

### Installing Templates from Marketplace

Users can browse the marketplace to discover templates created by others:

1. Access the marketplace tab
2. Browse agent templates
3. View template details 
4. Install templates of interest
5. Installed templates appear in the local templates list

Sources:
- [gui/pages/Content/Marketplace/Market.js:15-92]()
- [gui/pages/Content/Marketplace/MarketAgent.js:8-53]()
- [gui/pages/Content/Marketplace/AgentTemplate.js:62-87]()

### Publishing Templates to Marketplace

Users can share their agent templates with the community by publishing them to the marketplace:

1. Save an agent as a template or edit an existing template
2. Click "Publish to marketplace" option
3. The template is submitted for review
4. Once approved, it becomes available in the marketplace for others to install

Sources:
- [gui/pages/Content/Agents/AgentWorkspace.js:67-83]()
- [gui/pages/Content/Agents/AgentCreate.js:886-894]()

## Implementation Details

### Database Models

Agent Templates are primarily implemented through two database models:

1. **AgentTemplate** - Stores the template metadata
   ```python
   class AgentTemplate(DBBaseModel):
       id = Column(Integer, primary_key=True)
       organisation_id = Column(Integer)
       agent_workflow_id = Column(Integer)
       name = Column(String)
       description = Column(String)
       marketplace_template_id = Column(Integer)
   ```

2. **AgentTemplateConfig** - Stores the template configuration settings as key-value pairs
   ```python
   class AgentTemplateConfig(DBBaseModel):
       id = Column(Integer, primary_key=True)
       agent_template_id = Column(Integer)
       key = Column(String)
       value = Column(Text)
   ```

Sources:
- [superagi/models/agent_template.py:16-35]()
- [superagi/models/agent_template_config.py]()

### Frontend Components

The user interface for agent templates is implemented through several key components:

1. **AgentTemplatesList** - Displays available templates for selection
2. **AgentCreate** - Handles template loading and agent creation
3. **MarketAgent** - Shows marketplace templates
4. **AgentTemplate** - Displays template details

Sources:
- [gui/pages/Content/Agents/AgentTemplatesList.js]()
- [gui/pages/Content/Agents/AgentCreate.js]()
- [gui/pages/Content/Marketplace/MarketAgent.js]()
- [gui/pages/Content/Marketplace/AgentTemplate.js]()

### API Endpoints

The backend API provides several endpoints for managing agent templates:

1. **/agent_templates/list** - Lists available templates
2. **/agent_templates/get/{id}** - Gets template details
3. **/agent_templates/agent_config** - Gets template configuration
4. **/agent_templates/save_agent_as_template** - Saves an agent as a template
5. **/agent_templates/update_agent_template/{id}** - Updates a template
6. **/agent_templates/download** - Installs a template from marketplace
7. **/agent_templates/publish_template** - Publishes a template to marketplace

Sources:
- [superagi/controllers/agent_template.py]()
- [gui/pages/api/DashboardService.js:103-137]()

## Template Usage Flow

The complete flow from template selection to agent creation is visualized below:

```mermaid
sequenceDiagram
    actor User
    participant TemplatesList as "AgentTemplatesList"
    participant AgentCreate as "AgentCreate"
    participant API as "API Service"
    participant DB as "Database"
    
    User->>TemplatesList: Select template
    TemplatesList->>AgentCreate: Pass template ID
    AgentCreate->>API: fetchAgentTemplateConfigLocal(templateId)
    API->>DB: Query template configuration
    DB-->>API: Return template data
    API-->>AgentCreate: Template configuration
    AgentCreate->>AgentCreate: Fill form fields with template data
    User->>AgentCreate: Modify configuration (optional)
    User->>AgentCreate: Click "Create"
    AgentCreate->>API: createAgent(agentData)
    API->>DB: Save new agent with configuration
    API-->>AgentCreate: Success response
    AgentCreate-->>User: Show success notification
```

This sequence represents how a user interacts with the system to select a template and create a new agent based on that template.

Sources:
- [gui/pages/Content/Agents/AgentTemplatesList.js:53-58]()
- [gui/pages/Content/Agents/AgentCreate.js:187-206]()
- [gui/pages/Content/Agents/AgentCreate.js:495-543]()
- [superagi/controllers/agent.py:60-163]()

---

# Page: User Interface

# User Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [gui/app/favicon.ico](gui/app/favicon.ico)
- [gui/pages/Content/Agents/ActivityFeed.js](gui/pages/Content/Agents/ActivityFeed.js)
- [gui/pages/Content/Agents/AgentCreate.js](gui/pages/Content/Agents/AgentCreate.js)
- [gui/pages/Content/Agents/AgentSchedule.js](gui/pages/Content/Agents/AgentSchedule.js)
- [gui/pages/Content/Agents/AgentWorkspace.js](gui/pages/Content/Agents/AgentWorkspace.js)
- [gui/pages/Content/Agents/Agents.js](gui/pages/Content/Agents/Agents.js)
- [gui/pages/Content/Agents/Agents.module.css](gui/pages/Content/Agents/Agents.module.css)
- [gui/pages/Content/Agents/Details.js](gui/pages/Content/Agents/Details.js)
- [gui/pages/Content/Agents/ResourceList.js](gui/pages/Content/Agents/ResourceList.js)
- [gui/pages/Content/Agents/ResourceManager.js](gui/pages/Content/Agents/ResourceManager.js)
- [gui/pages/Content/Agents/TaskQueue.js](gui/pages/Content/Agents/TaskQueue.js)
- [gui/pages/Dashboard/Content.js](gui/pages/Dashboard/Content.js)
- [gui/pages/Dashboard/Dashboard.module.css](gui/pages/Dashboard/Dashboard.module.css)
- [gui/pages/Dashboard/Settings/Settings.js](gui/pages/Dashboard/Settings/Settings.js)
- [gui/pages/Dashboard/TopBar.js](gui/pages/Dashboard/TopBar.js)
- [gui/pages/_app.css](gui/pages/_app.css)
- [gui/pages/_app.js](gui/pages/_app.js)
- [gui/pages/api/DashboardService.js](gui/pages/api/DashboardService.js)
- [gui/pages/api/apiConfig.js](gui/pages/api/apiConfig.js)
- [gui/utils/utils.js](gui/utils/utils.js)

</details>



This document provides a comprehensive overview of the SuperAGI user interface architecture, components, and user interaction patterns. The UI enables users to create, manage, and monitor autonomous agents, handle resources, and configure system settings.

For information about specific agent functionality, refer to the [Agent System](#2) documentation, and for tool integrations, see the [Tools System](#4).

## User Interface Architecture

The SuperAGI UI is built as a Next.js web application with a modular component structure organized in a dashboard layout:

```mermaid
graph TD
    User(["User"]) --> Browser["Web Browser"]
    Browser --> NextApp["Next.js Application (_app.js)"]
    
    NextApp --> AuthLayer["Authentication Layer"]
    AuthLayer --> DashboardLayout["Dashboard Layout"]
    
    DashboardLayout --> SideBar["SideBar (Navigation)"]
    DashboardLayout --> TopBar["TopBar (Header)"]
    DashboardLayout --> Content["Content (Main Area)"]
    
    Content --> Tabs["Tab Management System"]
    Tabs --> AgentViews["Agent Views"]
    Tabs --> ToolkitViews["Toolkit Views"]
    Tabs --> KnowledgeViews["Knowledge Views"]
    Tabs --> SettingsViews["Settings Views"]
    Tabs --> MarketplaceView["Marketplace"]
    
    AgentViews --> AgentCreate["Agent Create Form"]
    AgentViews --> AgentWorkspace["Agent Workspace"]
    AgentWorkspace --> LeftPanel["Activity Feed/Task Queue"]
    AgentWorkspace --> RightPanel["Details/Resource Manager/Action Console"]
    
    style NextApp fill:#f9f9f9,stroke:#333,stroke-width:1px
    style Content fill:#f9f9f9,stroke:#333,stroke-width:1px
    style Tabs fill:#f9f9f9,stroke:#333,stroke-width:1px
    style AgentWorkspace fill:#f9f9f9,stroke:#333,stroke-width:1px
```

Sources:
- `gui/pages/_app.js`
- `gui/pages/Dashboard/Content.js`
- `gui/pages/Dashboard/TopBar.js`
- `gui/pages/Content/Agents/AgentWorkspace.js`

## Layout Components

### Application Entry Point

The application entry point (`_app.js`) handles:
- Authentication status management
- Environment detection (DEV/PROD)
- Application layout rendering
- Global event listeners

It renders either the sign-in screen or the main dashboard layout depending on authentication status:

```javascript
// Simplified structure from _app.js
{applicationState === 'AUTHENTICATED' ? (
  <div className="projectStyle">
    <div className="sideBarStyle">
      <SideBar onSelectEvent={handleSelectionEvent} env={env}/>
    </div>
    <div className="workSpaceStyle">
      <div className="topBarStyle">
        <TopBar selectedProject={selectedProject} organisationId={organisationId} userName={userName} env={env}/>
      </div>
      <div className="contentStyle">
        <Content env={env} organisationId={organisationId} selectedView={selectedView}
                 selectedProjectId={selectedProject?.id || ''}/>
      </div>
    </div>
  </div>
) : (
  <div className="signInStyle">
    {/* Sign-in screen */}
  </div>
)}
```

Sources:
- `gui/pages/_app.js:270-314`

### Top Bar Component

The TopBar provides:
- Project selection display
- Marketplace access
- Documentation links
- Settings access
- User profile menu

```mermaid
graph LR
    TopBar["TopBar Component"]
    TopBar --> ProjectSection["Project Display"]
    TopBar --> MarketplaceLink["Marketplace Link"]
    TopBar --> DocLinks["Documentation Links"]
    TopBar --> SettingsIcon["Settings Icon"]
    TopBar --> UserProfile["User Profile Dropdown"]
    
    UserProfile --> Logout["Logout"]
    DocLinks --> DocsLink["Docs Link"]
    DocLinks --> HelpLink["Get Help Link"]
    DocLinks --> GithubLink["Github Link"]
```

Sources:
- `gui/pages/Dashboard/TopBar.js:10-115`

### Content Management

The Content component is the core UI renderer that:
- Manages the tab system
- Renders the appropriate view based on selected navigation item
- Handles tab creation, selection, and closure

```mermaid
graph TD
    Content["Content Component"]
    Content --> TabSystem["Tab System"]
    Content --> SidebarItems["Sidebar Items"]
    
    TabSystem --> TabBar["Tab Navigation Bar"]
    TabSystem --> TabContent["Tab Content Area"]
    
    SidebarItems -- "Agents View" --> AgentsList["Agents List"]
    SidebarItems -- "Toolkits View" --> ToolkitsList["Toolkits List"]
    SidebarItems -- "Knowledge View" --> KnowledgeList["Knowledge List"]
    SidebarItems -- "Models View" --> ModelsList["Models List"]
    
    TabBar --> TabItem["Tab Item"]
    TabItem -- "Click" --> SelectTab["Select Tab"]
    TabItem -- "Close" --> CancelTab["Cancel Tab"]
    
    TabContent --> AgentWorkspace["Agent Workspace"]
    TabContent --> AgentCreate["Agent Create"]
    TabContent --> ToolkitWorkspace["Toolkit Workspace"]
    TabContent --> KnowledgeDetails["Knowledge Details"]
    TabContent --> Settings["Settings"]
```

Sources:
- `gui/pages/Dashboard/Content.js:37-503`

## Agent Interface

### Agent Creation

The Agent Create form allows users to define new agents with various configurations:

```mermaid
graph TD
    AgentCreate["AgentCreate Component"]
    AgentCreate --> BasicSettings["Basic Settings"]
    AgentCreate --> GoalsSection["Goals Configuration"]
    AgentCreate --> InstructionsSection["Instructions Configuration"]
    AgentCreate --> ModelSelection["Model Selection"]
    AgentCreate --> ToolsSection["Tools Selection"]
    AgentCreate --> AdvancedOptions["Advanced Options"]
    
    BasicSettings --> AgentName["Agent Name Input"]
    BasicSettings --> AgentDescription["Agent Description Input"]
    
    GoalsSection --> GoalsList["Goals List"]
    GoalsSection --> AddGoalButton["Add Goal Button"]
    
    InstructionsSection --> InstructionsList["Instructions List"]
    InstructionsSection --> AddInstructionButton["Add Instruction Button"]
    
    ModelSelection --> ModelDropdown["Model Dropdown"]
    ModelSelection --> BrowseModelsLink["Browse Models Link"]
    
    ToolsSection --> ToolkitsList["Toolkits List"]
    ToolsSection --> SelectedTools["Selected Tools"]
    
    AdvancedOptions --> ConstraintsSection["Constraints"]
    AdvancedOptions --> MemorySettings["Memory Settings"]
    AdvancedOptions --> PermissionSettings["Permission Settings"]
    AdvancedOptions --> IterationSettings["Iteration Settings"]
    AdvancedOptions --> ResourcesSection["Resources Upload"]
    
    AgentCreate -- "Submit" --> ValidateForm["Validate Form"]
    ValidateForm -- "Valid" --> CreateAgent["Create Agent API Call"]
    ValidateForm -- "Invalid" --> ShowErrors["Show Error Messages"]
    
    CreateAgent --> UploadResources["Upload Resources"]
    CreateAgent --> RunExecution["Run Execution"]
```

The form has extensive validation logic ensuring all required fields are completed and compatible settings are selected before an agent can be created:

```javascript
const validateAgentData = (isNewAgent) => {
  if (isNewAgent && !hasAPIkey) {
    toast.error("Your API key is empty!", {autoClose: 1800});
    openNewTab(-3, "Settings", "Settings", false);
    return false;
  }

  if (agentName?.replace(/\s/g, '') === '') {
    toast.error("Agent name can't be blank", {autoClose: 1800});
    return false;
  }

  // Additional validation checks...
  
  return true;
}
```

Sources:
- `gui/pages/Content/Agents/AgentCreate.js:23-896`
- `gui/pages/Content/Agents/AgentCreate.js:454-493`

### Agent Workspace

The Agent Workspace is the primary interface for interacting with created agents, divided into three main sections:

1. Run History (collapsible sidebar)
2. Left Panel (Activity Feed or Task Queue)
3. Right Panel (Details, Action Console, or Resource Manager)

```mermaid
graph TD
    AgentWorkspace["AgentWorkspace Component"]
    AgentWorkspace --> RunHistory["Run History"]
    AgentWorkspace --> LeftPanel["Left Panel"]
    AgentWorkspace --> RightPanel["Right Panel"]
    
    RunHistory --> RunList["Runs List"]
    RunHistory --> SelectRun["Run Selection"]
    
    LeftPanel --> Tabs1["Panel Tabs"]
    Tabs1 --> ActivityFeed["Activity Feed"]
    Tabs1 --> TaskQueue["Task Queue"]
    
    RightPanel --> Tabs2["Panel Tabs"]
    Tabs2 --> ActionConsole["Action Console"]
    Tabs2 --> Details["Agent Details"]
    Tabs2 --> ResourceManager["Resource Manager"]
    
    ActionConsole --> PermissionRequests["Permission Requests"]
    
    ActivityFeed --> FeedItems["Feed Messages"]
    ActivityFeed --> AgentStatus["Agent Status Indicator"]
    
    TaskQueue --> PendingTasks["Pending Tasks"]
    TaskQueue --> CompletedTasks["Completed Tasks"]
    
    Details --> AgentInfo["Agent Information"]
    Details --> AgentStats["Agent Statistics"]
    Details --> AgentGoals["Agent Goals"]
    Details --> AgentTools["Agent Tools"]
    Details --> AgentConfig["Agent Configuration"]
    
    ResourceManager --> InputResources["Input Resources"]
    ResourceManager --> OutputResources["Output Resources"]
```

The workspace has a consistent top navigation with controls for:
- Viewing run history
- Switching between Activity Feed and Task Queue
- Creating new runs
- Performing actions like pause/resume, saving as template, and deleting

Sources:
- `gui/pages/Content/Agents/AgentWorkspace.js:28-637`

#### Activity Feed

The Activity Feed displays the agent's actions, thoughts, and status in real-time:

```javascript
// ActivityFeed displays agent messages and status updates
{feeds && feeds.map((f, index) => (
  <div key={index} className={styles.history_box} style={{background: '#272335', padding: '20px', cursor: 'default'}}>
    <div style={{display: 'flex'}}>
      {f.role === 'user' && <div className={styles.feed_icon}>💁</div>}
      {f.role === 'system' && <div className={styles.feed_icon}>🛠️ </div>}
      {f.role === 'assistant' && <div className={styles.feed_icon}>💡</div>}
      <div className={styles.feed_title}>{f?.feed || ''}</div>
    </div>
    <div className={styles.more_details_wrapper}>
      {f.time_difference && <div className={styles.more_details}>
        <div style={{display: 'flex', alignItems: 'center'}}>
          <div>
            <Image width={12} height={12} src="/images/schedule.svg" alt="schedule-icon"/>
          </div>
          <div className={styles.history_info}>
            {formatTimeDifference(f.time_difference)}
          </div>
        </div>
      </div>}
    </div>
  </div>
))}
```

Sources:
- `gui/pages/Content/Agents/ActivityFeed.js:9-207`

#### Task Queue

For task-based agent workflows, the Task Queue displays pending and completed tasks:

```javascript
{tasks.pending.map((task, index) => (
  <div key={index} className={styles.history_box}
       style={{background: '#272335', padding: '20px', cursor: 'default'}}>
    <div style={{display: 'flex'}}>
      <div>
        <Image width={14} height={14} style={{mixBlendMode: 'exclusion'}} src="/images/loading.gif"
               alt="loading-icon"/>
      </div>
      <div className={styles.feed_title}>
        {task.name}
      </div>
    </div>
  </div>
))}
```

Sources:
- `gui/pages/Content/Agents/TaskQueue.js:7-70`

#### Action Console

The Action Console appears when an agent requires permission to perform certain actions. It allows users to approve or deny agent requests.

Sources:
- `gui/pages/Content/Agents/AgentWorkspace.js:519-523`

#### Agent Details

The Agent Details panel displays comprehensive information about the agent:

- Name and description
- Statistics (runs, calls, tokens)
- Goals list
- Instructions list
- Assigned tools
- Constraints
- Schedule information (if applicable)

```javascript
<div className={styles.agent_info_box}>
  <div><Image width={15} height={15} src="/images/flag.svg" alt="goals-icon"/></div>
  <div style={info_text}>{agentDetails?.goal?.length || 0} Goals</div>
</div>
{agentDetails?.goal && agentDetails?.goal?.length > 0 && <div>
  <div ref={goalBoxRef} className={styles.large_text_box} style={!showGoals ? {overflow: 'hidden', display: '-webkit-box'} : {}}>
    {agentDetails?.goal?.map((goal, index) => (<div key={index} style={{marginTop: '0'}}>
      <div>{index + 1}. {goal || ''}</div>
      {index !== agentDetails?.goal?.length - 1 && <br/>}
    </div>))}
  </div>
  {isOverflowing[0] && <div className={styles.show_more_button} onClick={() => setShowGoals(!showGoals)}>
    {showGoals ? 'Show Less' : 'Show More'}
  </div>}
</div>}
```

Sources:
- `gui/pages/Content/Agents/Details.js:7-260`

## Resource Management

The Resource Manager provides an interface for handling files used by agents:

```mermaid
graph TD
    ResourceManager["ResourceManager Component"]
    ResourceManager --> ChannelTabs["Channel Tabs"]
    ChannelTabs --> InputTab["Input Tab"]
    ChannelTabs --> OutputTab["Output Tab"]
    
    InputTab --> DropZone["File Drop Zone"]
    InputTab --> InputFiles["Input Files List"]
    
    OutputTab --> RunGroups["Run Groups"]
    RunGroups --> OutputFiles["Output Files"]
    
    DropZone -- "Drop/Click" --> FileUpload["File Upload"]
    FileUpload --> ValidateFile["Validate File"]
    ValidateFile -- "Valid" --> UploadFile["Upload to Server"]
    ValidateFile -- "Invalid" --> ShowError["Show Error"]
    
    InputFiles -- "Click" --> DownloadFile["Download File"]
    OutputFiles -- "Click" --> DownloadFile
    RunGroups -- "Download All" --> DownloadAllFiles["Download All Files"]
```

The Resource Manager allows:
- Uploading input files via drag-and-drop or file picker
- File size validation (max 5MB)
- Viewing files organized by agent runs
- Downloading individual files or all files from a run

```javascript
// Resource manager with file upload functionality
<div className={`file-drop-area ${isDragging ? 'dragging' : ''}`} onDragEnter={handleDragEnter}
     onDragLeave={handleDragLeave} onDragOver={handleDragOver} onDrop={handleDrop}
     onClick={handleDropAreaClick}>
  <p className="text_14 text_align_center">+ Choose or drop a file here</p>
  <p className="text_12 text_align_center">Supported file formats are txt, pdf,
    docx, epub, csv, pptx only</p>
  <input type="file" ref={fileInputRef} style={{display: 'none'}} onChange={handleFileInputChange}/>
</div>
```

Sources:
- `gui/pages/Content/Agents/ResourceManager.js:10-116`
- `gui/pages/Content/Agents/ResourceList.js:6-75`

## Settings Interface

The Settings interface is organized into tabs for different configuration areas:

```mermaid
graph TD
    Settings["Settings Component"]
    Settings --> Tabs["Settings Tabs"]
    
    Tabs --> ModelTab["Model Providers"]
    Tabs --> DatabaseTab["Database"]
    Tabs --> ApiKeysTab["API Keys"]
    Tabs --> WebhooksTab["Webhooks"]
    
    ModelTab --> ModelSettings["Model Configuration"]
    DatabaseTab --> DatabaseSettings["Database Configuration"]
    ApiKeysTab --> ApiKeyManagement["API Key Management"]
    WebhooksTab --> WebhookSettings["Webhook Settings"]
    
    ModelSettings --> ModelApiKeys["LLM API Keys"]
    ModelSettings --> ModelConfig["LLM Configuration"]
    
    DatabaseSettings --> VectorDBs["Vector Databases"]
    DatabaseSettings --> DatabaseConfig["Database Configuration"]
```

The settings interface provides a centralized location for configuring:
- Model providers and API keys
- Vector databases
- API keys for external access
- Webhook configurations

```javascript
<button onClick={() => switchTab('model')} className={activeTab === 'model' ? 'tab_button_selected' : 'tab_button'}>
  <Image width={14} height={14} src="/images/model_light.svg" alt="model-icon"/>
  <span>Model Providers</span>
</button>
<button onClick={() => switchTab('database')} className={activeTab === 'database' ? 'tab_button_selected' : 'tab_button'}>
  <Image width={14} height={14} src="/images/database.svg" alt="database-icon"/>
  <span>Database</span>
</button>
<button onClick={() => switchTab('apikeys')} className={activeTab === 'apikeys' ? 'tab_button_selected' : 'tab_button'}>
  <Image width={14} height={14} src="/images/key_white.svg" alt="api-key-icon"/>
  <span>API Keys</span>
</button>
<button onClick={() => switchTab('webhooks')} className={activeTab === 'webhooks' ? 'tab_button_selected' : 'tab_button'}>
  <Image className={styles.settings_tab_img} width={14} height={14} src="/images/webhook_icon.svg"
         alt="database-icon"/>&nbsp;Webhooks
</button>
```

Sources:
- `gui/pages/Dashboard/Settings/Settings.js:10-57`

## Tab Management System

The tab management system is a core component of the UI that allows users to work with multiple views simultaneously:

```mermaid
graph TD
    TabSystem["Tab Management System"]
    TabSystem --> TabBar["Tab Navigation Bar"]
    TabSystem --> TabContainer["Tab Content Container"]
    
    TabBar --> TabItem["Tab Item"]
    TabItem --> TabIcon["Tab Icon"]
    TabItem --> TabName["Tab Name"]
    TabItem --> CloseButton["Close Button"]
    
    TabItem -- "Click" --> SelectTab["Select Tab"]
    CloseButton -- "Click" --> CloseTab["Close Tab"]
    
    TabContainer --> TabContent["Active Tab Content"]
    
    User(["User"]) -- "Open View" --> AddTab["Add New Tab"]
    User -- "EventBus Event" --> OpenNewTab["Open New Tab Event"]
    
    AddTab --> TabBar
    OpenNewTab --> AddTab
```

The tab system is implemented in `Content.js` and allows:
- Opening multiple views simultaneously
- Selecting between open tabs
- Closing tabs when no longer needed
- Persisting tab state during navigation

```javascript
// Tab selection and rendering code
{tabs.map((tab, index) => (
  <div data-tab-id={index} key={index}
       className={`${styles.tab_box} ${selectedTab === index ? styles.tab_box_selected : ''}`}
       onClick={() => {
         selectTab(tab, index)
       }}>
    <div style={{display: 'flex', order: '0', overflowX: 'hidden'}}>
      {/* Tab icon based on contentType */}
      <div style={{marginLeft: '8px'}}><span className={styles.tab_text}>{tab.name}</span></div>
    </div>
    <div onClick={(e) => {
      e.stopPropagation();
      cancelTab(index, tab.contentType, tab.internalId || 0)
    }} className={styles.tab_active} style={{order: '1'}}><Image width={13} height={13}
                                                               src="/images/close.svg"
                                                               alt="close-icon"/></div>
  </div>
))}
```

Sources:
- `gui/pages/Dashboard/Content.js:192-429`

## UI State Management

The UI uses multiple state management approaches:

1. **Local Component State**: React's `useState` and `useEffect` hooks for component-specific state
2. **EventBus**: A custom pub/sub system for cross-component communication
3. **LocalStorage**: For persisting state between page reloads
4. **Prop Drilling**: For parent-child component communication

The EventBus allows components to communicate without direct parent-child relationships:

```javascript
// EventBus usage example
useEffect(() => {
  const openNewTab = (eventData) => {
    addTab(eventData.element);
  };

  const removeTab = (eventData) => {
    const element = eventData.element;
    const tabIndex = tabs.findIndex(
      (tab) => tab.id === element.id &&
        tab.name === element.name &&
        tab.contentType === element.contentType &&
        tab.internalId === element.internalId
    );
    cancelTab(tabIndex, element.contentType, element.internalId);
  };

  EventBus.on('openNewTab', openNewTab);
  EventBus.on('removeTab', removeTab);

  return () => {
    EventBus.off('openNewTab', openNewTab);
    EventBus.off('removeTab', removeTab);
  };
});
```

The utility functions in `utils.js` provide helper methods for UI components, including:
- Local storage management
- Date and time formatting
- File handling
- Event tracking

Sources:
- `gui/utils/utils.js:10-565`
- `gui/pages/Dashboard/Content.js:254-290`

## API Communication

The UI communicates with the backend using a centralized API service in `DashboardService.js`:

```mermaid
graph TD
    UI["UI Components"]
    UI --> APIServices["API Services"]
    APIServices --> APIConfig["API Configuration"]
    APIConfig --> BaseURL["Base URL"]
    APIConfig --> AuthHeaders["Auth Headers"]
    
    APIServices --> AgentAPI["Agent API"]
    APIServices --> ToolkitAPI["Toolkit API"]
    APIServices --> ResourceAPI["Resource API"]
    APIServices --> ConfigAPI["Config API"]
    APIServices --> AuthAPI["Auth API"]
    
    UI -- "HTTP Requests" --> APIServices
    APIServices -- "HTTP Responses" --> UI
```

The API service includes functions for:
- Agent management (creation, execution, configuration)
- Tool management
- Resource handling
- Settings and configuration
- Authentication

Each API call returns a Promise that components can handle with `.then()` and `.catch()` for success and error cases.

Sources:
- `gui/pages/api/DashboardService.js:1-406`
- `gui/pages/api/apiConfig.js:1-51`

## UI Styling System

The UI uses a combination of:
- Module-scoped CSS (e.g., `Agents.module.css`)
- Global CSS (e.g., `_app.css`)
- Inline styles for component-specific styling

The styling system defines:
- Layout structure
- Component styling
- Form elements
- Common UI patterns (modals, dropdowns, etc.)
- Animation effects

The CSS includes carefully designed components like:
- Buttons (primary, secondary)
- Form inputs
- Dropdowns
- Modals
- Tabs
- Cards

Sources:
- `gui/pages/_app.css:1-791`
- `gui/pages/Content/Agents/Agents.module.css:1-387`
- `gui/pages/Dashboard/Dashboard.module.css:1-126`

## Conclusion

The SuperAGI User Interface provides a comprehensive set of components for interacting with autonomous agents. The modular architecture allows for extensibility while maintaining a consistent user experience. The tab-based interface enables users to work with multiple views simultaneously, and the comprehensive agent workspace provides tools for monitoring and interacting with agents during execution.

Sources:
- All files reviewed in this document

---

# Page: Agent Workspace

# Agent Workspace

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [Dockerfile](Dockerfile)
- [entrypoint.sh](entrypoint.sh)
- [gui/pages/Content/Agents/ActionConsole.js](gui/pages/Content/Agents/ActionConsole.js)
- [gui/pages/Content/Agents/ActivityFeed.js](gui/pages/Content/Agents/ActivityFeed.js)
- [gui/pages/Content/Agents/AgentCreate.js](gui/pages/Content/Agents/AgentCreate.js)
- [gui/pages/Content/Agents/AgentSchedule.js](gui/pages/Content/Agents/AgentSchedule.js)
- [gui/pages/Content/Agents/AgentWorkspace.js](gui/pages/Content/Agents/AgentWorkspace.js)
- [gui/pages/Content/Agents/Agents.js](gui/pages/Content/Agents/Agents.js)
- [gui/pages/Content/Agents/Agents.module.css](gui/pages/Content/Agents/Agents.module.css)
- [gui/pages/Content/Agents/Details.js](gui/pages/Content/Agents/Details.js)
- [gui/pages/Content/Agents/ResourceList.js](gui/pages/Content/Agents/ResourceList.js)
- [gui/pages/Content/Agents/ResourceManager.js](gui/pages/Content/Agents/ResourceManager.js)
- [gui/pages/Content/Agents/RunHistory.js](gui/pages/Content/Agents/RunHistory.js)
- [gui/pages/Dashboard/Content.js](gui/pages/Dashboard/Content.js)
- [gui/pages/_app.css](gui/pages/_app.css)
- [gui/pages/api/DashboardService.js](gui/pages/api/DashboardService.js)
- [gui/utils/utils.js](gui/utils/utils.js)
- [wait-for-it.sh](wait-for-it.sh)

</details>



The Agent Workspace is the primary interface in SuperAGI for monitoring and managing agent executions after they've been created. It provides a comprehensive dashboard where users can track agent activities, control executions, manage resources, and handle permission requests in real-time.

For information about creating new agents, see [Agent Creation and Configuration](#2.1).

## Overview

The Agent Workspace serves as the central monitoring and control panel for each agent in SuperAGI. It displays real-time execution data, allows control over agent runs, provides access to agent resources, and presents detailed information about the agent's configuration and performance.

```mermaid
graph TD
    subgraph "Agent Workspace Layout"
        MainPanel["Main Area"]
        LeftPanel["Left Panel"]
        RightPanel["Right Panel"]
        RunHistory["Run History Panel (Optional)"]
        
        MainPanel --- LeftPanel
        MainPanel --- RightPanel
        MainPanel --- RunHistory
        
        subgraph "Left Panel Views"
            ActivityFeed["Activity Feed"]
            TaskQueue["Task Queue"]
            LeftPanel --> ActivityFeed
            LeftPanel --> TaskQueue
        end
        
        subgraph "Right Panel Views"
            ActionConsole["Action Console"]
            Details["Agent Details"]
            ResourceManager["Resource Manager"]
            RightPanel --> ActionConsole
            RightPanel --> Details
            RightPanel --> ResourceManager
        end
    end
```

Sources: [gui/pages/Content/Agents/AgentWorkspace.js:28-637]()

## Key Components

### Layout and Navigation

The workspace is divided into three main panels:

1. **Left Panel**: Displays either Activity Feed or Task Queue
2. **Right Panel**: Shows either Action Console, Details, or Resource Manager
3. **Run History Panel**: Optional side panel showing execution history

Each panel has tab controls allowing users to switch between different views. The workspace also includes a top toolbar with run controls and a dropdown menu for additional actions.

```mermaid
graph LR
    subgraph "AgentWorkspace Component Hierarchy"
        AW["AgentWorkspace.js"]
        AF["ActivityFeed.js"]
        RH["RunHistory.js"]
        AC["ActionConsole.js"]
        RM["ResourceManager.js"]
        D["Details.js"]
        TQ["TaskQueue.js"]
        
        AW --> AF["ActivityFeed\n(Feed of agent actions)"]
        AW --> RH["RunHistory\n(Past execution runs)"]
        AW --> AC["ActionConsole\n(Permission management)"]
        AW --> RM["ResourceManager\n(File management)"]
        AW --> D["Details\n(Agent configuration)"]
        AW --> TQ["TaskQueue\n(Workflow tasks)"]
    end
```

Sources: [gui/pages/Content/Agents/AgentWorkspace.js:348-533](), [gui/pages/Dashboard/Content.js:434-467]()

### Top Controls

The top section of the workspace contains:

- Run history toggle
- Current run name and status
- Panel navigation tabs
- "New Run" button 
- Actions dropdown menu (pause/resume run, save as template, publish to marketplace, edit/delete agent, schedule management)

Sources: [gui/pages/Content/Agents/AgentWorkspace.js:348-466]()

### Left Panel Components

#### Activity Feed

The Activity Feed displays a chronological log of agent activities, including:

- System messages
- Agent thoughts and reasoning
- Tool usage and results
- Wait states
- Completion or error messages

```mermaid
sequenceDiagram
    participant UI as ActivityFeed
    participant API as DashboardService
    participant BE as Backend
    
    Note over UI,BE: Polling cycle (every 5 seconds)
    UI->>API: getExecutionFeeds(selectedRunId)
    API->>BE: GET /agentexecutionfeeds/get/execution/{id}
    BE-->>API: Return feeds data
    API-->>UI: Update activity feed
    
    Note over UI: Display message types
    UI->>UI: Display user messages (💁)
    UI->>UI: Display system messages (🛠️)
    UI->>UI: Display assistant messages (💡)
    
    Note over UI: Display status indicators
    UI->>UI: Show "Thinking..." for RUNNING status
    UI->>UI: Show completion message for COMPLETED status
    UI->>UI: Show limit message for ITERATION_LIMIT_EXCEEDED
    UI->>UI: Show error message for ERROR_PAUSED
```

Sources: [gui/pages/Content/Agents/ActivityFeed.js:1-207](), [gui/pages/Content/Agents/AgentWorkspace.js:469-474]()

#### Task Queue

For agents using task-based workflows (Dynamic Task Workflow or Fixed Task Workflow), the Task Queue displays:

- Pending tasks
- Completed tasks
- Failed tasks
- Current task status

Sources: [gui/pages/Content/Agents/AgentWorkspace.js:379-385](), [gui/pages/Content/Agents/AgentWorkspace.js:474]()

### Right Panel Components

#### Action Console

The Action Console manages permission requests from the agent:

- Shows pending tool permission requests
- Allows approving or denying requests
- Provides feedback options when denying permissions
- Displays history of previous permission decisions

Sources: [gui/pages/Content/Agents/ActionConsole.js:1-169](), [gui/pages/Content/Agents/AgentWorkspace.js:520-523]()

#### Details

The Details panel shows comprehensive information about the agent:

- Name and description
- Execution statistics (runs, calls, tokens consumed)
- Goals and instructions
- Tools assigned to the agent
- Constraints
- Workflow type
- Model information
- Permission type
- Max iterations
- Scheduling information (if applicable)

Sources: [gui/pages/Content/Agents/Details.js:1-224](), [gui/pages/Content/Agents/AgentWorkspace.js:526-529]()

#### Resource Manager

The Resource Manager provides access to files associated with the agent:

- Input files (uploaded by users)
- Output files (generated by the agent)
- File uploading through drag-and-drop
- File downloading capabilities
- Batch download options organized by run

```mermaid
graph TD
    subgraph "Resource Manager"
        RM["ResourceManager Component"]
        InputTab["Input Tab"]
        OutputTab["Output Tab"]
        
        RM --> InputTab
        RM --> OutputTab
        
        InputTab --> UploadZone["Upload Zone\n(Drag & Drop)"]
        InputTab --> InputFiles["Input File List"]
        
        OutputTab --> RunSelector["Run Selector"]
        OutputTab --> OutputFiles["Output Files\nGrouped by Run"]
        
        UploadZone --> FileUpload["uploadFile API"]
        OutputFiles --> FileDownload["downloadFile API"]
        OutputFiles --> BatchDownload["downloadAllFiles Utility"]
    end
```

Sources: [gui/pages/Content/Agents/ResourceManager.js:1-117](), [gui/pages/Content/Agents/ResourceList.js:1-75](), [gui/pages/Content/Agents/AgentWorkspace.js:531]()

### Run History Panel

The Run History panel displays all executions of the current agent:

- Run names
- Status indicators (running, paused, completed, etc.)
- Statistics for each run (number of calls)
- Timestamp information
- Selection interface to switch between runs

Sources: [gui/pages/Content/Agents/RunHistory.js:1-60](), [gui/pages/Content/Agents/AgentWorkspace.js:351-352]()

## User Interactions

### Creating New Runs

Users can create new runs of an agent by:
1. Clicking the "New Run" button
2. Providing a name for the run
3. Optionally modifying goals and instructions
4. Confirming to start the execution

Sources: [gui/pages/Content/Agents/AgentWorkspace.js:389-390](), [gui/pages/Content/Agents/AgentWorkspace.js:535-595]()

### Managing Run Status

The workspace provides controls to manage execution status:

| Action | UI Location | Description |
|--------|-------------|-------------|
| Pause | Dropdown menu | Pauses a running execution |
| Resume | Dropdown menu | Resumes a paused execution |
| Delete | Dropdown menu | Removes a run from history |
| View Run History | Button or panel | Shows/hides run history panel |
| Create New Run | Button | Creates a new execution |

Sources: [gui/pages/Content/Agents/AgentWorkspace.js:393-437](), [gui/pages/Content/Agents/AgentWorkspace.js:216-234]()

### Handling Permissions

For agents running in restricted mode, the Action Console:
1. Displays tool permission requests in real-time
2. Allows users to approve or deny requests
3. Provides a feedback field when denying permissions
4. Updates pending permission notification count

Sources: [gui/pages/Content/Agents/ActionConsole.js:101-168](), [gui/pages/Content/Agents/AgentWorkspace.js:480-486]()

### Resource Management

Users can manage agent resources through the Resource Manager:
- Upload new input files via drag-and-drop
- Download individual files by clicking on them
- Download all files from a run with the download button
- Switch between input and output resources

Sources: [gui/pages/Content/Agents/ResourceManager.js:10-116](), [gui/pages/Content/Agents/ResourceList.js:6-74]()

### Agent Scheduling

The workspace provides scheduling capabilities:

1. Schedule Run - Configure a specific start time for the agent
2. Edit Schedule - Modify existing schedule parameters
3. Stop Schedule - Cancel a scheduled agent run

Scheduling options include:
- Setting a specific start time
- Configuring recurring runs with intervals
- Setting expiration conditions (by date or number of runs)

Sources: [gui/pages/Content/Agents/AgentWorkspace.js:424-443](), [gui/pages/Content/Agents/AgentSchedule.js:12-368]()

## Technical Implementation

The Agent Workspace is implemented as a React component in [gui/pages/Content/Agents/AgentWorkspace.js]() that manages state and coordinates several sub-components.

### Data Flow

```mermaid
sequenceDiagram
    participant UI as AgentWorkspace
    participant API as DashboardService
    participant Backend as Backend API
    
    Note over UI,Backend: Initial Loading
    UI->>API: getAgentDetails(agentId, selectedRun?.id)
    API->>Backend: GET /agent_executions_configs/details/agent_id/{id}/agent_execution_id/{id}
    Backend-->>API: Return agent configuration
    API-->>UI: Update agentDetails state
    
    UI->>API: getAgentExecutions(agentId)
    API->>Backend: GET /agentexecutions/get/agent/{id}
    Backend-->>API: Return execution history
    API-->>UI: Update agentExecutions state
    
    Note over UI,Backend: Polling Cycle
    loop Every 5 seconds (if run is active)
        UI->>API: getExecutionFeeds(selectedRunId)
        API->>Backend: GET /agentexecutionfeeds/get/execution/{id}
        Backend-->>API: Return feeds and permissions
        API-->>UI: Update ActivityFeed and ActionConsole
    end
    
    Note over UI,Backend: User Interactions
    UI->>API: addExecution(executionData)
    API->>Backend: POST /agentexecutions/add
    Backend-->>API: Return new execution data
    API-->>UI: Update UI with new run
    
    UI->>API: updateExecution(executionId, status)
    API->>Backend: PUT /agentexecutions/update/{id}
    Backend-->>API: Confirm status update
    API-->>UI: Refresh UI components
    
    UI->>API: updatePermissions(permissionId, data)
    API->>Backend: PUT /agentexecutionpermissions/update/status/{id}
    Backend-->>API: Confirm permission update
    API-->>UI: Update ActionConsole
```

Sources: [gui/pages/Content/Agents/AgentWorkspace.js:265-275](), [gui/pages/Content/Agents/AgentWorkspace.js:288-299](), [gui/pages/api/DashboardService.js:31-41]()

### State Management

The AgentWorkspace component manages several pieces of state:

- **Panel selection**: `leftPanel` and `rightPanel` states control which views are displayed
- **Run selection**: `selectedRun` state tracks the current execution being viewed
- **Agent data**: `agentDetails` and `agentExecutions` store agent configuration and history
- **UI toggles**: States for modals, dropdowns, and panel visibility

Sources: [gui/pages/Content/Agents/AgentWorkspace.js:29-54](), [gui/pages/Content/Agents/AgentWorkspace.js:237-246]()

### Event Communication

The component uses the EventBus pattern to communicate between components:

- `reFetchAgents` - Triggers agent list refresh
- `updateRunStatus` - Updates run status across components
- `resetRunStatus` - Resets run status display
- `refreshDate` - Updates scheduling information 
- `removeTab` - Closes workspace tabs

Sources: [gui/pages/Content/Agents/AgentWorkspace.js:326-345](), [gui/utils/utils.js:227-238]()

## Use Cases

### Monitoring Agent Progress

1. Open the Agent Workspace
2. View the Activity Feed to see real-time agent actions
3. Check the Details panel for execution statistics
4. For workflow-based agents, use the Task Queue to monitor task status

### Managing Permissions

1. When a permission request appears, check the Action Console
2. Review the tool permission request
3. Approve or deny the request
4. Optionally provide feedback for denied requests

### Working with Resources

1. Navigate to the Resource Manager
2. Upload input files using drag-and-drop
3. Switch to the Output tab to view files generated by the agent
4. Download individual files or entire run artifacts

### Scheduling Agent Runs

1. Open the dropdown menu and select "Schedule Run"
2. Set the start time for the agent
3. Configure recurring parameters if needed
4. Set expiration conditions
5. Confirm to create the schedule

Sources: [gui/pages/Content/Agents/AgentWorkspace.js:393-437](), [gui/pages/Content/Agents/AgentSchedule.js:140-184]()

## Conclusion

The Agent Workspace is the primary interface for monitoring and controlling agents after they've been created. It provides a comprehensive set of tools for tracking agent progress, managing resources, handling permissions, and scheduling runs. The interface is designed to support both real-time monitoring and historical analysis of agent executions.

---

# Page: Marketplace

# Marketplace

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [gui/app/favicon.ico](gui/app/favicon.ico)
- [gui/pages/Content/Agents/AgentTemplatesList.js](gui/pages/Content/Agents/AgentTemplatesList.js)
- [gui/pages/Content/Agents/TaskQueue.js](gui/pages/Content/Agents/TaskQueue.js)
- [gui/pages/Content/Marketplace/AgentTemplate.js](gui/pages/Content/Marketplace/AgentTemplate.js)
- [gui/pages/Content/Marketplace/Market.js](gui/pages/Content/Marketplace/Market.js)
- [gui/pages/Content/Marketplace/Market.module.css](gui/pages/Content/Marketplace/Market.module.css)
- [gui/pages/Content/Marketplace/MarketAgent.js](gui/pages/Content/Marketplace/MarketAgent.js)
- [gui/pages/Content/Marketplace/MarketTools.js](gui/pages/Content/Marketplace/MarketTools.js)
- [gui/pages/Content/Marketplace/MarketplacePublic.js](gui/pages/Content/Marketplace/MarketplacePublic.js)
- [gui/pages/Dashboard/Dashboard.module.css](gui/pages/Dashboard/Dashboard.module.css)
- [gui/pages/Dashboard/Settings/Settings.js](gui/pages/Dashboard/Settings/Settings.js)
- [gui/pages/Dashboard/TopBar.js](gui/pages/Dashboard/TopBar.js)
- [gui/pages/_app.js](gui/pages/_app.js)
- [gui/pages/api/apiConfig.js](gui/pages/api/apiConfig.js)
- [gui/public/images/tick.svg](gui/public/images/tick.svg)

</details>



The Marketplace is a central hub within SuperAGI where users can discover, browse, and install various components that extend the system's capabilities. This includes agent templates, toolkits, and knowledge templates. The Marketplace serves as both a distribution platform for pre-built components and a community resource for sharing configurations.

For information about creating agent templates, see [Agent Templates](#2.3).

## 1. Marketplace Overview

The SuperAGI Marketplace provides a collection of ready-to-use components that can be directly installed into your SuperAGI instance. It's accessible both within the application for authenticated users and through a public interface for unauthenticated users.

```mermaid
graph TD
    User(["User"]) --> AuthenticatedAccess["Authenticated Access"]
    User --> PublicAccess["Public Access (Unauthenticated)"]
    
    AuthenticatedAccess --> MarketplaceUI["Marketplace UI"]
    PublicAccess --> PublicMarketplaceUI["Public Marketplace UI"]
    
    MarketplaceUI --> TemplateCategories["Template Categories"]
    PublicMarketplaceUI --> TemplateCategories
    
    TemplateCategories --> Tools["Tools"]
    TemplateCategories --> Knowledge["Knowledge"]
    TemplateCategories --> AgentTemplates["Agent Templates"]
    TemplateCategories --> Models["Models (Public Only)"]
    
    Tools --> ToolDetails["Tool Template Details"]
    Knowledge --> KnowledgeDetails["Knowledge Template Details"]
    AgentTemplates --> AgentDetails["Agent Template Details"]
    Models --> ModelDetails["Model Template Details"]
    
    ToolDetails --> Installation["Template Installation"]
    KnowledgeDetails --> Installation
    AgentDetails --> Installation
    ModelDetails --> Installation
```

Sources:
- [gui/pages/Content/Marketplace/Market.js:1-119]()
- [gui/pages/Content/Marketplace/MarketplacePublic.js:1-39]()

## 2. Accessing the Marketplace

The Marketplace can be accessed in two ways:

1. **From the Dashboard**: Authenticated users can access the Marketplace directly from the top navigation bar in the SuperAGI interface.
2. **Public URL**: Unauthenticated users can access a public version of the Marketplace that allows browsing but requires sign-in for installation.

### 2.1 Dashboard Access

In the top navigation bar of the SuperAGI dashboard, there's a "Marketplace" link that opens the Marketplace interface. This is implemented in the TopBar component.

Sources:
- [gui/pages/Dashboard/TopBar.js:75-78]()

### 2.2 Public Marketplace

The public Marketplace is a standalone interface that can be accessed without authentication. It includes a sign-up/sign-in button, allowing users to authenticate if they want to install templates.

Sources:
- [gui/pages/Content/Marketplace/MarketplacePublic.js:1-39]()
- [gui/pages/_app.js:25-40]()

## 3. Marketplace Components

The Marketplace is organized into different categories of templates that users can browse and install.

### 3.1 Template Categories

The Marketplace offers the following template categories:

| Category | Description | Component |
|----------|-------------|-----------|
| Tools | Toolkits that extend agent capabilities | MarketTools |
| Knowledge | Knowledge templates for information retrieval | MarketKnowledge |
| Agent Templates | Pre-configured agent templates | MarketAgent |
| Models (Public only) | Model configurations | MarketModels |

Sources:
- [gui/pages/Content/Marketplace/Market.js:53-58]()
- [gui/pages/Content/Marketplace/MarketTools.js:1-73]()
- [gui/pages/Content/Marketplace/MarketAgent.js:1-72]()

### 3.2 Template Display and Management

The Marketplace UI is managed by the Market component, which handles tab switching, template selection, and detail views.

```mermaid
classDiagram
    class Market {
        activeTab: string
        itemClicked: boolean
        templateData: object
        detailType: string
        switchTab()
        handleOpenTemplateDetails()
        handleBackClick()
    }
    
    class MarketAgent {
        agentTemplates: array
        showMarketplace: boolean
        isLoading: boolean
        loadingText: string
        handleTemplateClick()
    }
    
    class MarketTools {
        toolTemplates: array
        showMarketplace: boolean
        isLoading: boolean
        loadingText: string
        handleTemplateClick()
    }
    
    class AgentTemplate {
        template: object
        tools: array
        agentWorkflow: string
        templateModel: string
        goals: array
        instructions: array
        constraints: array
        handleInstallClick()
    }
    
    Market --> MarketAgent: renders if activeTab="market_agents"
    Market --> MarketTools: renders if activeTab="market_tools"
    Market --> AgentTemplate: renders if detailType="agent_template"
```

Sources:
- [gui/pages/Content/Marketplace/Market.js:1-119]()
- [gui/pages/Content/Marketplace/AgentTemplate.js:1-219]()

## 4. Template Details and Installation

When a user selects a template from any category, they can view its details and choose to install it.

### 4.1 Agent Template Details

For agent templates, the details view includes:
- Template name and description
- Required tools
- Agent workflow
- Model used
- Goals
- Instructions (if any)
- Constraints

Sources:
- [gui/pages/Content/Marketplace/AgentTemplate.js:94-214]()

### 4.2 Installation Process

The installation process differs based on whether the user is authenticated:

```mermaid
sequenceDiagram
    participant User as "User"
    participant UI as "Marketplace UI"
    participant App as "_app.js"
    participant API as "Backend API"
    
    User->>UI: Select template to install
    
    alt Authenticated User
        UI->>API: Direct installation request
        API-->>UI: Installation confirmation
        UI->>User: Show success message
    else Unauthenticated User
        UI->>UI: Store template ID in localStorage
        Note right of UI: localStorage.setItem('agent_to_install', template.id)
        UI->>User: Redirect to login page
        User->>App: Completes authentication
        App->>App: Detects stored template ID
        App->>API: Installs template
        API-->>App: Installation confirmation
        App->>User: Show success message
    end
```

The installation process is handled by different components depending on the context:

1. **Direct Installation**: For authenticated users, installation is handled directly by the template detail components.
2. **Deferred Installation**: For unauthenticated users, the template ID is stored in localStorage and installation occurs after authentication.

Sources:
- [gui/pages/Content/Marketplace/AgentTemplate.js:61-87]()
- [gui/pages/_app.js:65-104]()

## 5. Technical Implementation

### 5.1 Data Flow and State Management

The Marketplace uses a combination of React state and localStorage to manage user interactions:

- **Active Tab**: The selected tab is stored in localStorage as `marketplace_tab`
- **Template Selection**: When a template is selected, its data and the detail type are stored in state and localStorage
- **Installation State**: For deferred installations, template IDs are stored in localStorage (e.g., `agent_to_install`, `toolkit_to_install`)

Sources:
- [gui/pages/Content/Marketplace/Market.js:21-46]()
- [gui/pages/_app.js:65-104]()

### 5.2 Event-Based Communication

The Marketplace components use an event-driven approach for communication:

- **EventBus**: A custom event bus facilitates communication between components
- **Events**: Key events include `openTemplateDetails` and `goToMarketplace`

Sources:
- [gui/pages/Content/Marketplace/Market.js:39-46]()
- [gui/pages/Content/Marketplace/MarketAgent.js:41-45]()

### 5.3 API Integration

The Marketplace fetches data from different endpoints based on whether it's being accessed publicly or within the authenticated application:

- **Authenticated**: Uses API endpoints like `/api/agent_templates/list`
- **Public**: Uses public endpoints like `https://app.superagi.com/api/agent_templates/marketplace/list`

Sources:
- [gui/pages/Content/Marketplace/MarketAgent.js:15-38]()
- [gui/pages/Content/Marketplace/MarketTools.js:15-40]()

## 6. Integration with Other SuperAGI Components

The Marketplace is integrated with other parts of the SuperAGI system, particularly:

### 6.1 Agent Creation Flow

When creating a new agent, users can choose to use a template from the local templates or go to the Marketplace to find more templates.

Sources:
- [gui/pages/Content/Agents/AgentTemplatesList.js:90-106]()

### 6.2 Dashboard Navigation

The Marketplace can be accessed from the top navigation bar of the SuperAGI dashboard.

Sources:
- [gui/pages/Dashboard/TopBar.js:75-78]()

## 7. Marketplace Styling and UI

The Marketplace has a consistent styling defined in CSS modules, with specific styles for different elements like template cards, detail views, and tabs.

Sources:
- [gui/pages/Content/Marketplace/Market.module.css:1-552]()

## 8. Cross-Platform Integration

When a user attempts to install a template from the public Marketplace, the system handles redirects and authentication appropriately based on the environment:

- **Production**: Redirects to app.superagi.com
- **Development**: Redirects to the local instance

Sources:
- [gui/pages/Content/Marketplace/AgentTemplate.js:61-70]()
- [gui/pages/Content/Marketplace/MarketplacePublic.js:7-14]()

---

# Page: Settings and Configuration UI

# Settings and Configuration UI

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [gui/app/favicon.ico](gui/app/favicon.ico)
- [gui/pages/Content/APM/ApmDashboard.js](gui/pages/Content/APM/ApmDashboard.js)
- [gui/pages/Content/Agents/TaskQueue.js](gui/pages/Content/Agents/TaskQueue.js)
- [gui/pages/Content/Marketplace/MarketKnowledge.js](gui/pages/Content/Marketplace/MarketKnowledge.js)
- [gui/pages/Content/Toolkits/ToolkitWorkspace.js](gui/pages/Content/Toolkits/ToolkitWorkspace.js)
- [gui/pages/Content/Toolkits/Toolkits.js](gui/pages/Content/Toolkits/Toolkits.js)
- [gui/pages/Dashboard/Dashboard.module.css](gui/pages/Dashboard/Dashboard.module.css)
- [gui/pages/Dashboard/Settings/Settings.js](gui/pages/Dashboard/Settings/Settings.js)
- [gui/pages/Dashboard/TopBar.js](gui/pages/Dashboard/TopBar.js)
- [gui/pages/_app.js](gui/pages/_app.js)
- [gui/pages/api/apiConfig.js](gui/pages/api/apiConfig.js)
- [superagi/controllers/google_oauth.py](superagi/controllers/google_oauth.py)

</details>



The Settings and Configuration UI in SuperAGI provides a centralized interface for managing various system configurations, including model providers, databases, API keys, and webhooks. This page documents the structure and functionality of the settings interface, how to access it, and how to configure different components of the system.

For information about tool-specific settings, see [Tools System](#4). For deployment configuration options, see [Configuration Options](#7.2).

## Accessing the Settings UI

Users can access the Settings UI by clicking the settings icon in the top right corner of the SuperAGI interface. This icon is rendered as a gear/cog and is displayed in the TopBar component of the application.

```mermaid
flowchart LR
    A["User"] -->|"Click Settings Icon"| B["Settings UI"]
    
    subgraph "TopBar Navigation"
        C["TopBar.js - Settings Icon"] -->|"openNewTab(-3, 'Settings', 'Settings', false)"| D["Settings Page"]
    end
```

Sources: [gui/pages/Dashboard/TopBar.js:98-98]()

## Settings UI Structure

The Settings UI is organized into four main tabs that provide access to different configuration areas of SuperAGI. The active tab is persisted in localStorage, allowing users to return to their last-used tab when revisiting the Settings page.

```mermaid
flowchart TD
    A["Settings Page"] --> B["Tab Navigation"]
    B --> C["Model Providers"]
    B --> D["Database"]
    B --> E["API Keys"]
    B --> F["Webhooks"]
    
    subgraph "Tab Management"
        G["localStorage - settings_tab"] --- H["activeTab State"]
        H -->|"Controls"| I["Tab Visibility"]
    end
```

Each tab offers specific configuration options:

| Tab | Purpose | Component |
|-----|---------|-----------|
| Model Providers | Configure LLM providers | Model.js |
| Database | Configure vector databases | Database.js |
| API Keys | Manage API keys for external services | ApiKeys.js |
| Webhooks | Set up event notifications | Webhooks.js |

Sources: [gui/pages/Dashboard/Settings/Settings.js:11-56]()

## Model Providers Configuration

The Model Providers tab allows users to configure various language model providers that SuperAGI can use for agent operations. This includes OpenAI models, Google Palm, and other supported LLM providers.

```mermaid
flowchart LR
    A["Model Providers Tab"] --> B["Model Configuration Form"]
    B -->|"Save"| C["API Request"]
    C -->|"Store"| D["Database"]
    
    subgraph "Model Config Components"
        E["Provider Selection"]
        F["API Key Input"]
        G["Model Parameters"]
    end
```

In this tab, users can:
- Select which model provider to use as default
- Enter API keys for different providers
- Configure model-specific parameters
- Test the connection to the model provider

Sources: [gui/pages/Dashboard/Settings/Settings.js:49-49]()

## Database Configuration

The Database tab provides interfaces for configuring the vector databases used by SuperAGI for storing embeddings and knowledge. This is important for tools that require semantic search capabilities.

```mermaid
flowchart TD
    A["Database Tab"] --> B["Vector Database Selection"]
    B --> C["Connection Parameters"]
    C -->|"Save"| D["Update Database Config"]
    
    subgraph "Database Options"
        E["Pinecone"]
        F["Weaviate"]
        G["Qdrant"]
        H["Redis"]
        I["ChromaDB"]
        J["LanceDB"]
    end
    
    D -->|"sendDatabaseData"| K["Apply Configuration"]
```

Users can configure:
- Which vector database to use
- Connection parameters (API keys, endpoints)
- Database-specific settings

Sources: [gui/pages/Dashboard/Settings/Settings.js:50-50]()

## API Keys Management

The API Keys tab allows users to manage API keys for various external services integrated with SuperAGI. These keys are stored securely and used by the system to authenticate with third-party services.

```mermaid
flowchart LR
    A["API Keys Tab"] --> B["API Key Form"]
    B -->|"Add/Update"| C["Save API Key"]
    C -->|"Store"| D["Secure Storage"]
    
    subgraph "Key Management"
        E["Add New Key"]
        F["Update Existing Key"]
        G["Remove Key"]
    end
```

The system manages API keys for various services, including:
- OpenAI
- Google services
- Other third-party integrations

Sources: [gui/pages/Dashboard/Settings/Settings.js:51-51](), [gui/pages/api/apiConfig.js:1-51]()

## Webhooks Configuration

The Webhooks tab allows users to configure webhook notifications for various events that occur within the SuperAGI system, enabling integration with external systems.

```mermaid
flowchart TD
    A["Webhooks Tab"] --> B["Webhook Configuration Form"]
    B -->|"Save"| C["Register Webhook"]
    
    subgraph "Webhook Settings"
        D["Event Selection"]
        E["Endpoint URL"]
        F["Authentication Headers"]
    end
    
    C -->|"Trigger"| G["Event System"]
    G -->|"When Event Occurs"| H["Send HTTP Request"]
    H -->|"Notify"| I["External System"]
```

Users can:
- Configure webhook endpoints for different event types
- Set authentication headers for secure webhook delivery
- Enable/disable specific webhooks

Sources: [gui/pages/Dashboard/Settings/Settings.js:52-52]()

## Tool-specific Configuration

While the main Settings UI handles system-wide configurations, individual tools and toolkits have their own configuration interfaces. These tool-specific settings are managed through the Toolkit Workspace UI.

### Toolkit Configuration Flow

```mermaid
flowchart TD
    A["Toolkit Workspace"] --> B["Configuration Tab"]
    B --> C["Tool Config Form"]
    C -->|"updateToolConfig"| D["Save Configuration"]
    
    subgraph "Authentication Flows"
        E["Regular Tools"] -->|"Update Configuration"| D
        F["OAuth Tools"] -->|"Authenticate"| G["OAuth Flow"]
        G -->|"Get Tokens"| H["Store Tokens"]
        H -->|"Update Configuration"| D
    end
    
    subgraph "Tool Config Storage"
        D -->|"Store"| I["Tool Configuration Database"]
        I -->|"getToolConfig"| J["Load Tool Configuration"]
        J -->|"Display"| C
    end
```

The system supports different types of tool configurations:
1. Simple configuration with API keys and parameters
2. OAuth-based authentication for services like Google Calendar and Twitter

Sources: [gui/pages/Content/Toolkits/ToolkitWorkspace.js:14-232](), [superagi/controllers/google_oauth.py:1-93]()

### OAuth Authentication Process

For tools requiring OAuth authentication (such as Google Calendar or Twitter), SuperAGI provides a specialized authentication flow:

```mermaid
sequenceDiagram
    participant User
    participant SuperAGI
    participant OAuth as "OAuth Provider"
    
    User->>SuperAGI: Click "Authenticate Tool"
    SuperAGI->>OAuth: Redirect to OAuth Authorization URL
    OAuth->>User: Display Permission Screen
    User->>OAuth: Grant Permissions
    OAuth->>SuperAGI: Redirect with Auth Code
    SuperAGI->>OAuth: Exchange Code for Tokens
    SuperAGI->>SuperAGI: Store OAuth Tokens
    SuperAGI->>User: Display Success Message
```

For example, with Google Calendar:
1. User enters client ID and client secret
2. User clicks "Authenticate Tool"
3. System redirects to Google OAuth page
4. After authorization, tokens are stored for future API calls

Sources: [gui/pages/Content/Toolkits/ToolkitWorkspace.js:32-46](), [superagi/controllers/google_oauth.py:24-65]()

## Environment Configuration

SuperAGI supports different environment configurations (Development/Production), which affect various aspects of the system's behavior. The environment is determined via the `checkEnvironment` API call.

```mermaid
flowchart LR
    A["Application Startup"] -->|"checkEnvironment()"| B["Environment Detection"]
    B -->|"DEV"| C["Development Mode"]
    B -->|"PROD"| D["Production Mode"]
    
    subgraph "Environment-specific Behavior"
        C -->|"Simplified Auth"| E["Auto-login"]
        D -->|"OAuth Authentication"| F["GitHub Login"]
    end
    
    subgraph "apiConfig.js"
        G["API_BASE_URL"]
        H["GITHUB_CLIENT_ID"]
        I["MIXPANEL_AUTH_ID"]
    end
```

Key environment-dependent behaviors include:
- Authentication flow (GitHub OAuth for Production)
- API endpoints (local vs. remote)
- Analytics tracking

Sources: [gui/pages/_app.js:110-171](), [gui/pages/api/apiConfig.js:1-51]()

## Settings Persistence

SuperAGI stores settings in several different ways, depending on the type of setting:

1. **System Settings**: Stored in the backend database (accessed via API calls)
2. **UI State**: Stored in localStorage for persistence between sessions
3. **Authentication Tokens**: Stored in cookies for secure access

| Setting Type | Storage Method | Scope | Example |
|--------------|----------------|-------|---------|
| System Config | Database | Global | Model providers, Vector DB config |
| Tool Config | Database | Per toolkit | API keys, OAuth tokens |
| UI Preferences | localStorage | Per user/browser | Active tab, layout preferences |
| Auth Tokens | Cookies | Per user | Access tokens |

The following localStorage keys are actively used by the settings components:

- `settings_tab` - Stores the active tab in Settings UI
- `toolkit_tab_[id]` - Stores the active tab for a specific toolkit
- `api_configs_[id]` - Temporarily stores toolkit API configurations

Sources: [gui/pages/Dashboard/Settings/Settings.js:14-22](), [gui/pages/Content/Toolkits/ToolkitWorkspace.js:57-59](), [gui/pages/_app.js:234-268]()

## APM Dashboard Configuration

The Agent Performance Monitoring (APM) dashboard has its own configuration UI that allows users to customize the layout of metrics and visualizations. This layout configuration is stored in localStorage.

```mermaid
flowchart TD
    A["APM Dashboard"] --> B["Responsive Grid Layout"]
    B -->|"onLayoutChange"| C["Update Layout"]
    C -->|"Save"| D["localStorage - myLayoutKey"]
    
    subgraph "Layout Management"
        E["Initial Layout"] -->|"First Load"| F["Check Stored Layout"]
        F -->|"Exists"| G["Load Custom Layout"]
        F -->|"Not Found"| H["Use Default Layout"]
    end
    
    subgraph "Dashboard Components"
        I["Total Agents"]
        J["Total Tokens"]
        K["Active Runs"]
        L["Model Usage Graphs"]
        M["Tool Usage Stats"]
    end
```

Users can:
- Resize and rearrange dashboard components
- Reset to the default layout
- Persist custom layouts between sessions

Sources: [gui/pages/Content/APM/ApmDashboard.js:31-46](), [gui/pages/Content/APM/ApmDashboard.js:54-64]()

## Conclusion

The Settings and Configuration UI in SuperAGI provides a comprehensive set of interfaces for configuring all aspects of the system. From model providers to databases, API keys, and webhooks, users can customize the system to meet their specific requirements. Tool-specific configurations, especially those requiring OAuth authentication, are handled through dedicated interfaces in the Toolkit Workspace.

Understanding these configuration options is essential for effectively deploying and using SuperAGI in various environments and use cases.

---

# Page: Tools System

# Tools System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [superagi/helper/tool_helper.py](superagi/helper/tool_helper.py)
- [superagi/lib/logger.py](superagi/lib/logger.py)
- [superagi/models/tool_config.py](superagi/models/tool_config.py)
- [superagi/tools/code/prompts/generate_logic.txt](superagi/tools/code/prompts/generate_logic.txt)
- [superagi/tools/code/write_code.py](superagi/tools/code/write_code.py)
- [superagi/tools/code/write_spec.py](superagi/tools/code/write_spec.py)
- [superagi/tools/code/write_test.py](superagi/tools/code/write_test.py)
- [superagi/tools/file/append_file.py](superagi/tools/file/append_file.py)
- [superagi/tools/file/delete_file.py](superagi/tools/file/delete_file.py)
- [superagi/tools/file/list_files.py](superagi/tools/file/list_files.py)
- [superagi/tools/file/read_file.py](superagi/tools/file/read_file.py)
- [superagi/tools/file/write_file.py](superagi/tools/file/write_file.py)
- [test.py](test.py)
- [tests/unit_tests/helper/test_tool_helper.py](tests/unit_tests/helper/test_tool_helper.py)
- [tests/unit_tests/test_tool_manager.py](tests/unit_tests/test_tool_manager.py)
- [tools.json](tools.json)

</details>



The Tools System in SuperAGI provides agents with capabilities to interact with external systems and perform specific tasks. This system is a foundational component that enables agents to manipulate files, generate code, send emails, create images, and interact with various external services.

For information about specific tool implementations, please see the related pages on [File Tools](#4.1), [Code Generation Tools](#4.2), and other tool categories.

## Architecture Overview

The Tools System organizes functionality into individual tools and toolkits (collections of related tools). The system handles tool registration, configuration, discovery, and execution.

![Tools System Architecture](https://placeholder)
```mermaid
graph TD
    subgraph "Tool Management"
        ToolManager["ToolManager"] --> ToolHelper["ToolHelper"]
        ToolHelper --> ToolInstallation["Tool Installation"]
        ToolHelper --> ToolRegistration["Tool Registration"]
        
        ToolManager --> ToolConfigs["Tool Configurations"]
        ToolManager --> ToolkitRegistry["Toolkit Registry"]
    end
    
    subgraph "Tool Categories"
        BaseTool["BaseTool"] --> FileTool["File Tools"]
        BaseTool --> CodeTool["Code Generation Tools"]
        BaseTool --> EmailTool["Email Tools"]
        BaseTool --> ImageGenTool["Image Generation Tools"]
        BaseTool --> KnowledgeSearchTool["Knowledge Search Tools"]
        BaseTool --> SocialTool["Social Media Tools"]
        BaseTool --> QueryResourceTool["Resource Query Tool"]
        
        BaseToolkit["BaseToolkit"] --> FileToolkit["File Toolkit"]
        BaseToolkit --> CodeToolkit["Code Toolkit"]
        BaseToolkit --> EmailToolkit["Email Toolkit"]
        BaseToolkit --> ImageGenToolkit["Image Generation Toolkit"]
        BaseToolkit --> InstagramToolkit["Instagram Toolkit"]
    end
    
    subgraph "Tool Authentication"
        ToolConfigs --> OAuth["OAuth Integration"]
        OAuth --> GoogleOAuth["Google OAuth"]
        OAuth --> TwitterOAuth["Twitter OAuth"]
    end
    
    subgraph "Tool Execution"
        AgentExecutor["AgentExecutor"] --> ToolExecution["Tool Execution"]
        ToolExecution --> ToolPermission["Tool Permission"]
        ToolExecution --> ToolOutput["Tool Output"]
        ToolOutput --> AgentMemory["Agent Memory"]
    end
    
    ToolManager --> BaseTool
    ToolManager --> BaseToolkit
```

Sources:
- [superagi/helper/tool_helper.py]()
- [superagi/tools/file/read_file.py]()
- [superagi/tools/file/write_file.py]()

## Core Components

### BaseTool

All tools in SuperAGI inherit from the `BaseTool` abstract class, which provides the common structure and functionality:

- **name**: A string identifier for the tool
- **description**: A description of what the tool does
- **args_schema**: A Pydantic model that defines the input arguments
- **_execute method**: The implementation of the tool's functionality

Example tool structures:

![Tool Class Hierarchy](https://placeholder)
```mermaid
classDiagram
    BaseTool <|-- ReadFileTool
    BaseTool <|-- WriteFileTool
    BaseTool <|-- CodingTool
    BaseTool <|-- WriteTestTool
    BaseTool <|-- WriteSpecTool
    
    class BaseTool {
        +name: str
        +description: str
        +args_schema: Type[BaseModel]
        +agent_id: int
        +agent_execution_id: int
        +resource_manager: Optional[FileManager]
        +_execute(*args): str
    }
    
    class ReadFileTool {
        +name: "Read File"
        +description: "Reads the file content in a specified location"
        +_execute(file_name: str): str
    }
    
    class WriteFileTool {
        +name: "Write File"
        +description: "Writes text to a file"
        +_execute(file_name: str, content: str): str
    }
    
    class CodingTool {
        +name: "CodingTool"
        +description: "Generates code based on description"
        +llm: BaseLlm
        +_execute(code_description: str): str
    }
```

Sources:
- [superagi/tools/file/read_file.py:27-42]()
- [superagi/tools/file/write_file.py:19-34]()
- [superagi/tools/code/write_code.py:26-52]()

### BaseToolkit

Toolkits are collections of related tools. Each toolkit:

- Has a name and description
- Provides a list of tools it contains
- Defines required environment keys or configuration parameters

### Tool Configuration

Tools can require configuration parameters, which are stored in the database using the `ToolConfig` model:

```
id              - Primary key
key             - Configuration parameter name
value           - Parameter value
toolkit_id      - Associated toolkit ID
key_type        - Data type (STRING, INT, BOOLEAN, etc.)
is_secret       - Whether the value should be treated as sensitive
is_required     - Whether the parameter is mandatory
```

Sources:
- [superagi/models/tool_config.py:10-46]()

## Tool Registration Process

The tool registration process discovers and loads tools during system startup:

![Tool Registration Process](https://placeholder)
```mermaid
sequenceDiagram
    participant App as System
    participant TH as ToolHelper
    participant FS as FileSystem
    participant DB as Database
    
    App->>TH: register_toolkits(session, organisation)
    TH->>TH: process_files(tool_paths, session, organisation)
    TH->>TH: init_toolkits(...)
    TH->>FS: Scan directories for Python files
    FS-->>TH: Return Python files
    TH->>TH: get_classes_in_file(file_path, BaseToolkit)
    
    loop For each toolkit class
        TH->>DB: Toolkit.add_or_update(...)
        TH->>DB: Tool.add_or_update(...) for each tool
        TH->>DB: ToolConfig.add_or_update(...) for each config
    end
    
    TH->>TH: init_tools(folder_paths, session, tool_name_to_toolkit)
    TH->>FS: Scan directories for Python files
    FS-->>TH: Return Python files
    TH->>TH: get_classes_in_file(file_path, BaseTool)
    
    loop For each tool class
        TH->>DB: Tool.add_or_update(...)
    end
    
    TH-->>App: Registration complete
```

The registration process involves:

1. Scanning tool directories (`superagi/tools`, `superagi/tools/external_tools`, etc.)
2. Loading Python modules and finding classes that inherit from `BaseTool` and `BaseToolkit`
3. Registering toolkits, tools, and their configurations in the database

Sources:
- [superagi/helper/tool_helper.py:121-237]()
- [superagi/helper/tool_helper.py:259-271]()

## Tool Execution Flow

When an agent uses a tool, the following sequence occurs:

![Tool Execution Flow](https://placeholder)
```mermaid
sequenceDiagram
    participant Agent
    participant AgentExecutor
    participant Tool
    participant ResourceManager
    
    Agent->>AgentExecutor: Request to use tool
    AgentExecutor->>Tool: execute(tool_inputs)
    Tool->>Tool: Validate inputs using args_schema
    Tool->>Tool: _execute(validated_inputs)
    
    alt File Tool
        Tool->>ResourceManager: File operation (read/write/etc.)
        ResourceManager-->>Tool: Operation result
    else Code Tool
        Tool->>LLM: Generate code/tests/specs
        LLM-->>Tool: Generated content
        Tool->>ResourceManager: Save generated content
        ResourceManager-->>Tool: Save result
    end
    
    Tool-->>AgentExecutor: Return execution result
    AgentExecutor-->>Agent: Return formatted result
```

For example, the `WriteFileTool._execute` method:

```python
def _execute(self, file_name: str, content: str):
    """
    Execute the write file tool.
    
    Args:
        file_name : The name of the file to write.
        content : The text to write to the file.
        
    Returns:
        success message if message is file written successfully 
        or failure message if writing file fails.
    """
    return self.resource_manager.write_file(file_name, content)
```

Sources:
- [superagi/tools/file/write_file.py:39-50]()
- [superagi/tools/file/read_file.py:43-101]()
- [superagi/tools/code/write_code.py:57-119]()

## File Tools

File tools handle basic file operations. The core file tools include:

| Tool | Description | Key Methods |
|------|-------------|------------|
| ReadFileTool | Reads content from a file | `_execute(file_name)` |
| WriteFileTool | Writes content to a file | `_execute(file_name, content)` |
| AppendFileTool | Appends content to an existing file | `_execute(file_name, content)` |
| DeleteFileTool | Deletes a file | `_execute(file_name)` |
| ListFileTool | Lists files in a directory | `_execute()` |

Sources:
- [superagi/tools/file/read_file.py]()
- [superagi/tools/file/write_file.py]()
- [superagi/tools/file/append_file.py]()
- [superagi/tools/file/delete_file.py]()
- [superagi/tools/file/list_files.py]()

## Code Generation Tools

Code generation tools help agents create code, specifications, and tests:

| Tool | Description | Key Methods |
|------|-------------|------------|
| CodingTool | Generates code based on a description | `_execute(code_description)` |
| WriteSpecTool | Generates software specifications | `_execute(task_description, spec_file_name)` |
| WriteTestTool | Generates unit tests | `_execute(test_description, test_file_name)` |

Sources:
- [superagi/tools/code/write_code.py]()
- [superagi/tools/code/write_spec.py]()
- [superagi/tools/code/write_test.py]()

## External Tools Integration

SuperAGI supports loading tools from external GitHub repositories:

1. External tool repositories are tracked in `tools.json`:
   ```json
   {
     "tools": {
       "repo-name": "https://github.com/owner/repo"
     }
   }
   ```

2. Tools are downloaded and extracted during system startup:
   ```python
   def download_tool(tool_url, target_folder):
       parsed_url = parse_github_url(tool_url)
       parts = parsed_url.split("/")
       owner, repo, branch = parts[0], parts[1], parts[2]
       archive_url = f"https://api.github.com/repos/{owner}/{repo}/zipball/{branch}"
       # Download and extract repository...
   ```

3. New tools can be added programmatically:
   ```python
   def add_tool_to_json(repo_link):
       # Read tools.json
       # Add new repository link
       # Write updated JSON back
   ```

Sources:
- [tools.json]()
- [superagi/helper/tool_helper.py:20-68]()
- [superagi/helper/tool_helper.py:280-294]()

## Creating Custom Tools

To create a new tool:

1. Create a new Python file in an appropriate directory
2. Define a Pydantic model for the tool's input arguments
3. Create a class that inherits from `BaseTool`
4. Implement the `_execute` method

Example template:

```python
from typing import Type
from pydantic import BaseModel, Field
from superagi.tools.base_tool import BaseTool

class YourToolInput(BaseModel):
    param1: str = Field(..., description="Parameter description")
    param2: int = Field(..., description="Parameter description")

class YourTool(BaseTool):
    name: str = "Your Tool Name"
    description: str = "Description of what your tool does"
    args_schema: Type[BaseModel] = YourToolInput
    
    def _execute(self, param1: str, param2: int):
        # Implement tool functionality
        return "Result of tool execution"
```

## Tool Authentication

For tools that need to access external services, SuperAGI provides an authentication system through tool configurations:

1. Define required configuration keys in the toolkit:
   ```python
   def get_env_keys(self):
       return [
           ToolConfiguration(key="API_KEY", key_type=ToolConfigKeyType.STRING, is_required=True, is_secret=True),
           ToolConfiguration(key="API_BASE", key_type=ToolConfigKeyType.STRING, is_required=False)
       ]
   ```

2. Access these configurations in tool execution:
   ```python
   api_key = self.get_tool_config("API_KEY")
   api_base = self.get_tool_config("API_BASE")
   ```

Sources:
- [superagi/helper/tool_helper.py:217-228]()
- [superagi/models/tool_config.py:65-102]()

## Conclusion

The Tools System is a crucial component of SuperAGI that enables agents to interact with external systems and perform a wide range of tasks. By understanding this architecture and following the patterns established, you can extend agent capabilities by creating new tools or integrating external tool repositories.

---

# Page: File Tools

# File Tools

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [superagi/helper/resource_helper.py](superagi/helper/resource_helper.py)
- [superagi/resource_manager/file_manager.py](superagi/resource_manager/file_manager.py)
- [superagi/tools/file/append_file.py](superagi/tools/file/append_file.py)
- [superagi/tools/file/delete_file.py](superagi/tools/file/delete_file.py)
- [superagi/tools/file/list_files.py](superagi/tools/file/list_files.py)
- [superagi/tools/file/read_file.py](superagi/tools/file/read_file.py)
- [superagi/tools/file/write_file.py](superagi/tools/file/write_file.py)
- [superagi/types/storage_types.py](superagi/types/storage_types.py)
- [test.py](test.py)
- [tests/unit_tests/helper/test_resource_helper.py](tests/unit_tests/helper/test_resource_helper.py)

</details>



This page documents the file manipulation tools in SuperAGI that allow agents to read, write, append to, delete, and list files. These tools enable agents to interact with the file system, making it possible for them to persist information, process data, and utilize external files as part of their operations.

For information about how these tools are used with the overall tool system, see [Tools System](#4).

## File Tools Architecture

The File Tools in SuperAGI are built on a layered architecture that provides flexibility in file storage locations and consistent interfaces for file operations.

### Architecture Overview

```mermaid
graph TD
    subgraph "Agent Execution"
        AgentExecutor["AgentExecutor"]
        ToolManager["ToolManager"]
    end
    
    subgraph "File Tools"
        BaseTool["BaseTool"] --> ReadFileTool["ReadFileTool"]
        BaseTool --> WriteFileTool["WriteFileTool"]
        BaseTool --> AppendFileTool["AppendFileTool"]
        BaseTool --> DeleteFileTool["DeleteFileTool"]
        BaseTool --> ListFileTool["ListFileTool"]
    end
    
    subgraph "Resource Management"
        ResourceHelper["ResourceHelper"]
        FileManager["FileManager"]
        StorageType["StorageType\n(FILE/S3)"]
    end
    
    subgraph "Storage Systems"
        FileSystem["File System"]
        S3Storage["Amazon S3"]
    end
    
    AgentExecutor --> ToolManager
    ToolManager --> BaseTool
    
    ReadFileTool --> ResourceHelper
    WriteFileTool --> FileManager
    AppendFileTool --> ResourceHelper
    DeleteFileTool --> ResourceHelper
    ListFileTool --> ResourceHelper
    
    FileManager --> ResourceHelper
    ResourceHelper --> StorageType
    
    StorageType --> FileSystem
    StorageType --> S3Storage
```

Sources:
- [superagi/tools/file/read_file.py:11-37]()
- [superagi/tools/file/write_file.py:9-34]()
- [superagi/tools/file/append_file.py:14-36]()
- [superagi/tools/file/delete_file.py:14-34]()
- [superagi/tools/file/list_files.py:16-31]()
- [superagi/resource_manager/file_manager.py:11-17]()
- [superagi/types/storage_types.py:4-15]()

### File Path Resolution

A key component of the file tools is the path resolution system. The `ResourceHelper` class provides methods to determine appropriate file paths based on agent context, ensuring proper organization of files and resources.

```mermaid
flowchart TD
    Start["File Operation Request"] --> RequestType{"Operation Type"}
    
    RequestType -->|"Read"| ReadPath["get_agent_read_resource_path()"]
    RequestType -->|"Write"| WritePath["get_agent_write_resource_path()"]
    
    ReadPath --> CheckInputDir["Check in INPUT_ROOT_DIR first"]
    CheckInputDir --> CheckOutputDir["If not found, check in OUTPUT_ROOT_DIR"]
    
    WritePath --> ResolveAgent["Resolve agent-specific path"]
    ResolveAgent --> ResolveExecution["Resolve execution-specific path"]
    
    CheckOutputDir --> DetermineFinalPath["Final Path"]
    ResolveExecution --> DetermineFinalPath
    
    DetermineFinalPath --> StorageType{"Storage Type"}
    
    StorageType -->|"FILE"| FileSystemOp["Local File System Operation"]
    StorageType -->|"S3"| S3Op["S3 Operation"]
```

Sources:
- [superagi/helper/resource_helper.py:84-182]()
- [superagi/resource_manager/file_manager.py:88-93]()

## Available File Tools

SuperAGI provides five primary file manipulation tools:

### 1. ReadFileTool

The ReadFileTool allows agents to read the contents of a file. It supports various file types including text files, CSV files, and even more complex formats like EPUB.

**Key Features:**
- Reads text files and returns content as string
- Supports EPUB parsing using ebooklib and BeautifulSoup
- Handles CSV file encoding corrections automatically
- Compatible with both local file system and S3 storage

Sources:
- [superagi/tools/file/read_file.py:27-101]()

### 2. WriteFileTool

The WriteFileTool enables agents to create new files or overwrite existing ones with specified content.

**Key Features:**
- Creates text files with specified content
- Creates parent directories if they don't exist
- Works with both local file system and S3 storage
- Updates resource metadata in the database

Sources:
- [superagi/tools/file/write_file.py:19-50]()
- [superagi/resource_manager/file_manager.py:48-66]()

### 3. AppendFileTool

The AppendFileTool allows agents to add content to existing files without overwriting their current contents.

**Key Features:**
- Appends text to existing files
- Creates the file if it doesn't exist
- Special handling for S3 storage (read-modify-write)
- Compatible with both storage types

Sources:
- [superagi/tools/file/append_file.py:21-81]()

### 4. DeleteFileTool

The DeleteFileTool provides functionality to remove files.

**Key Features:**
- Deletes specified files
- Works with both local file system and S3 storage
- Returns success/error messages

Sources:
- [superagi/tools/file/delete_file.py:20-64]()

### 5. ListFileTool

The ListFileTool allows agents to discover files in the resource directories.

**Key Features:**
- Lists files in input directories
- Recursively searches directories
- Filters out hidden files and system directories
- Supports both local and S3 storage types

Sources:
- [superagi/tools/file/list_files.py:18-69]()

## Resource Management

The resource management system is a critical component that supports file tools. It consists of two main classes: `ResourceHelper` and `FileManager`.

### ResourceHelper

The `ResourceHelper` class provides utility methods for managing file paths and resources. It handles the complexity of determining file paths based on agent context and storage configuration.

**Key Methods:**
- `make_written_file_resource`: Creates Resource objects for written files
- `get_agent_write_resource_path`: Gets the path for writing files
- `get_agent_read_resource_path`: Gets the path for reading files
- `get_formatted_agent_level_path`: Formats path with agent information
- `get_formatted_agent_execution_level_path`: Formats path with execution information

### FileManager

The `FileManager` class provides a higher-level interface for file operations, with methods for reading, writing, and managing files.

**Key Methods:**
- `write_file`: Writes text content to a file
- `write_binary_file`: Writes binary data to a file
- `write_csv_file`: Writes CSV data to a file
- `read_file`: Reads content from a file
- `get_files`: Lists all files in agent's resource directory

### Storage Types

SuperAGI supports two storage types for files:

| Storage Type | Configuration Value | Description |
|--------------|---------------------|-------------|
| FILE         | "FILE"              | Local file system storage |
| S3           | "S3"                | Amazon S3 cloud storage   |

Storage type is configured using the `STORAGE_TYPE` environment variable. The system automatically routes file operations to the appropriate storage backend based on this setting.

Sources:
- [superagi/helper/resource_helper.py:12-182]()
- [superagi/resource_manager/file_manager.py:11-124]()
- [superagi/types/storage_types.py:4-15]()

## File Resource Path Management

The file path resolution system in SuperAGI is designed to organize resources by agent and execution context.

```mermaid
graph TD
    subgraph "Path Resolution Process"
        FileOperation["File Operation\n(read/write/append/delete)"] --> GetPath["Get Resource Path"]
        GetPath --> StorageCheck{"Storage Type?"}
        
        StorageCheck -->|"FILE"| LocalPath["Local File Path"]
        StorageCheck -->|"S3"| S3Path["S3 File Path\n(prefixed with 'resources')"]
        
        LocalPath --> DirectoryCheck["Create Directory\nif needed"]
        S3Path --> S3Operation["S3 Operation"]
        
        DirectoryCheck --> FileOperation2["Perform File Operation"]
        
        FileOperation2 --> ResourceTracking["Create/Update Resource\nin Database"]
    end
    
    subgraph "Path Template Variables"
        PathVars["Path Variables"] --> AgentVar["{agent_id}"]
        PathVars --> ExecVar["{agent_execution_id}"]
        
        AgentVar --> FormatAgent["Replace with\nAgentName_AgentId"]
        ExecVar --> FormatExec["Replace with\nExecutionName_ExecutionId"]
    end
```

Sources:
- [superagi/helper/resource_helper.py:82-182]()
- [superagi/resource_manager/file_manager.py:16-35]()

## File Tools Integration with Agents

File tools are integrated into the agent system, allowing agents to interact with files during their execution cycle.

```mermaid
sequenceDiagram
    participant Agent as "Agent"
    participant ToolManager as "ToolManager"
    participant FileTool as "File Tool"
    participant ResourceHelper as "ResourceHelper"
    participant Storage as "Storage System"
    
    Agent->>ToolManager: Execute tool (e.g., WriteFileTool)
    ToolManager->>FileTool: _execute(file_name, content)
    
    alt WriteFileTool
        FileTool->>ResourceHelper: get_agent_write_resource_path()
        ResourceHelper->>FileTool: final_path
        FileTool->>Storage: Write content to path
    else ReadFileTool
        FileTool->>ResourceHelper: get_agent_read_resource_path()
        ResourceHelper->>FileTool: final_path
        FileTool->>Storage: Read content from path
        Storage->>FileTool: file content
    end
    
    FileTool->>ToolManager: Operation result
    ToolManager->>Agent: Tool execution result
```

Sources:
- [superagi/tools/file/read_file.py:42-100]()
- [superagi/tools/file/write_file.py:39-50]()
- [superagi/tools/file/append_file.py:38-81]()
- [superagi/resource_manager/file_manager.py:48-66]()

## Example Usage

Below is a table showing how agents typically use the file tools:

| Operation | Tool | Example Usage |
|-----------|------|---------------|
| Store information | WriteFileTool | Store research findings, save code, record observations |
| Retrieve information | ReadFileTool | Access previous data, read inputs, analyze code files |
| Update logs | AppendFileTool | Add to logs, update records, append new findings |
| Clean up resources | DeleteFileTool | Remove temporary files, delete outdated information |
| Discover resources | ListFileTool | Find available resources, check existing files |

The file tools provide persistent storage capabilities to SuperAGI agents, allowing them to maintain state, share information between iterations, and work with external data sources.

---

# Page: Code Generation Tools

# Code Generation Tools

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [superagi/lib/logger.py](superagi/lib/logger.py)
- [superagi/tools/code/prompts/generate_logic.txt](superagi/tools/code/prompts/generate_logic.txt)
- [superagi/tools/code/write_code.py](superagi/tools/code/write_code.py)
- [superagi/tools/code/write_spec.py](superagi/tools/code/write_spec.py)
- [superagi/tools/code/write_test.py](superagi/tools/code/write_test.py)

</details>



This document details the Code Generation Tools in SuperAGI, which provide agents with the capability to create specifications, write code, and generate tests. These tools leverage large language models (LLMs) to transform natural language descriptions into functioning software components.

For information about other tool types available in SuperAGI, see [Tools System](#4).

## Overview

The Code Generation Tools consist of three core components that work together to support a complete software development workflow:

1. **Write Specification Tool**: Creates detailed specifications based on task descriptions
2. **Coding Tool**: Generates code that fulfills the specifications
3. **Write Test Tool**: Creates unit tests for the generated code

These tools are designed to be used sequentially, mirroring a test-driven development approach, but can also be used independently.

Sources:
- [superagi/tools/code/write_spec.py:29-41](superagi/tools/code/write_spec.py:29-41)
- [superagi/tools/code/write_code.py:26-38](superagi/tools/code/write_code.py:26-38)
- [superagi/tools/code/write_test.py:30-42](superagi/tools/code/write_test.py:30-42)

## Code Generation Workflow

The Code Generation Tools follow a structured workflow that enables agents to progressively refine their output from specification to implementation to testing.

```mermaid
flowchart LR
    subgraph "Natural Language Space"
        task["Task Description"]
    end
    
    subgraph "Code Generation Pipeline"
        spec["WriteSpecTool"]
        code["CodingTool"]
        test["WriteTestTool"]
    end
    
    subgraph "Code Entity Space"
        spec_file["Specification File"]
        code_files["Source Code Files"]
        test_files["Test Files"]
    end
    
    task --> spec
    spec --> spec_file
    spec_file -.-> code
    code --> code_files
    code_files -.-> test
    spec_file -.-> test
    test --> test_files
```

The dashed lines represent optional but recommended data flows that enhance the quality of the generated code and tests.

Sources:
- [superagi/tools/code/write_spec.py:55-85](superagi/tools/code/write_spec.py:55-85)
- [superagi/tools/code/write_code.py:57-119](superagi/tools/code/write_code.py:57-119)
- [superagi/tools/code/write_test.py:60-120](superagi/tools/code/write_test.py:60-120)

## Tool Architecture

All code generation tools share a common architecture pattern, integrating with the LLM system and resource management components of SuperAGI.

```mermaid
classDiagram
    class BaseTool {
        <<abstract>>
        +name: str
        +description: str
        +args_schema: Type[BaseModel]
        +_execute()
    }
    
    class WriteSpecTool {
        +llm: BaseLlm
        +resource_manager: FileManager
        +goals: List[str]
        +_execute(task_description, spec_file_name)
    }
    
    class CodingTool {
        +llm: BaseLlm
        +resource_manager: FileManager
        +tool_response_manager: ToolResponseQueryManager
        +goals: List[str]
        +_execute(code_description)
    }
    
    class WriteTestTool {
        +llm: BaseLlm
        +resource_manager: FileManager
        +tool_response_manager: ToolResponseQueryManager
        +goals: List[str]
        +_execute(test_description, test_file_name)
    }
    
    BaseTool <|-- WriteSpecTool
    BaseTool <|-- CodingTool
    BaseTool <|-- WriteTestTool
```

All Code Generation Tools inherit from the `BaseTool` class and utilize:
- An LLM for generating content
- A `FileManager` for managing file resources
- A `ToolResponseQueryManager` (for `CodingTool` and `WriteTestTool`) to access outputs from previous tools

Sources:
- [superagi/tools/code/write_spec.py:29-53](superagi/tools/code/write_spec.py:29-53)
- [superagi/tools/code/write_code.py:26-55](superagi/tools/code/write_code.py:26-55)
- [superagi/tools/code/write_test.py:30-58](superagi/tools/code/write_test.py:30-58)

## Write Specification Tool

The Write Specification Tool (`WriteSpecTool`) generates detailed specifications for software components based on a high-level task description.

### Input Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `task_description` | string | Description of the task to be implemented |
| `spec_file_name` | string | Name of the file where the specification will be saved |

### Execution Flow

```mermaid
sequenceDiagram
    participant Agent
    participant WriteSpecTool
    participant LLM
    participant FileManager
    
    Agent->>WriteSpecTool: _execute(task_description, spec_file_name)
    WriteSpecTool->>WriteSpecTool: Load prompt template
    WriteSpecTool->>WriteSpecTool: Replace placeholders with goals and task
    WriteSpecTool->>LLM: chat_completion(messages)
    LLM-->>WriteSpecTool: Return specification content
    WriteSpecTool->>FileManager: write_file(spec_file_name, content)
    FileManager-->>WriteSpecTool: Return file write result
    WriteSpecTool-->>Agent: Return specification content and status
```

The tool loads a prompt template, replaces placeholders with the agent's goals and task description, sends the prompt to the LLM, and saves the resulting specification to a file.

Sources:
- [superagi/tools/code/write_spec.py:55-85](superagi/tools/code/write_spec.py:55-85)

## Coding Tool

The Coding Tool (`CodingTool`) generates code based on a description and any previously created specification.

### Input Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `code_description` | string | Description of the coding task |

### Execution Flow

```mermaid
flowchart TD
    A["Execute CodingTool"] --> B["Load prompt template"]
    B --> C["Replace placeholders with goals and description"]
    C --> D["Get spec from previous WriteSpecTool call if available"]
    D --> E["Send prompt to LLM"]
    E --> F["Parse response for code blocks"]
    F --> G["Extract filename and code from each block"]
    G --> H["Write each code file"]
    H --> I["Extract README content"]
    I --> J["Write README.md"]
    J --> K["Return success message with filenames"]
```

The Coding Tool:
1. Constructs a prompt using the task description and agent goals
2. Retrieves and incorporates previous specification output if available
3. Sends the prompt to the LLM
4. Parses the response to extract code blocks with filenames
5. Saves each code block as a separate file
6. Extracts and saves README content
7. Returns a success message with the list of generated files

Sources:
- [superagi/tools/code/write_code.py:57-119](superagi/tools/code/write_code.py:57-119)

### Code Parsing

The tool uses regular expressions to extract code blocks and filenames from the LLM's output:

```
regex = r"(\S+?)\n```\S*\n(.+?)```"
```

This pattern captures:
1. A filename (any non-whitespace characters)
2. A code block delimited by triple backticks

Sources:
- [superagi/tools/code/write_code.py:87-96](superagi/tools/code/write_code.py:87-96)

## Write Test Tool

The Write Test Tool (`WriteTestTool`) generates unit tests based on a test description and previous specifications or code.

### Input Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `test_description` | string | Description of the testing task |
| `test_file_name` | string | Name of the file where tests will be saved |

### Execution Flow

```mermaid
sequenceDiagram
    participant Agent
    participant WriteTestTool
    participant ToolResponseManager
    participant LLM
    participant FileManager
    
    Agent->>WriteTestTool: _execute(test_description, test_file_name)
    WriteTestTool->>WriteTestTool: Load prompt template
    WriteTestTool->>WriteTestTool: Replace placeholders with goals and description
    WriteTestTool->>ToolResponseManager: get_last_response("WriteSpecTool")
    alt Specification Found
        ToolResponseManager-->>WriteTestTool: Return specification content
    else No Specification
        WriteTestTool->>ToolResponseManager: get_last_response()
        ToolResponseManager-->>WriteTestTool: Return any previous response
    end
    WriteTestTool->>LLM: chat_completion(messages)
    LLM-->>WriteTestTool: Return test code content
    WriteTestTool->>WriteTestTool: Parse response to extract code blocks
    loop For each code block
        WriteTestTool->>FileManager: write_file(file_name, code)
    end
    WriteTestTool-->>Agent: Return test content and status
```

The Write Test Tool:
1. Constructs a prompt using the test description and agent goals
2. Attempts to retrieve previous specification or any other relevant output
3. Sends the prompt to the LLM
4. Parses the response to extract test code and filenames
5. Saves each test file
6. Returns a success message with the generated test content

Sources:
- [superagi/tools/code/write_test.py:60-120](superagi/tools/code/write_test.py:60-120)

## Integration with Agent System

The Code Generation Tools integrate with the SuperAGI agent system through the tool manager and can be used in agent workflows.

### Tool Installation and Registration

Each tool is registered with SuperAGI's tool system, making it available for agents to use. The tools can be included individually or as part of a Code Toolkit.

### Token Management

All Code Generation Tools implement token management to ensure that LLM requests stay within token limits:

```
organisation = Agent.find_org_by_agent_id(self.toolkit_config.session, agent_id=self.agent_id)
total_tokens = TokenCounter.count_message_tokens(messages, self.llm.get_model())
token_limit = TokenCounter(session=self.toolkit_config.session, organisation_id=organisation.id).token_limit(self.llm.get_model())

result = self.llm.chat_completion(messages, max_tokens=(token_limit - total_tokens - 100))
```

This ensures that prompts don't exceed the LLM's token limits, allowing for complex code generation within constraints.

Sources:
- [superagi/tools/code/write_spec.py:71-75](superagi/tools/code/write_spec.py:71-75)
- [superagi/tools/code/write_code.py:77-81](superagi/tools/code/write_code.py:77-81)
- [superagi/tools/code/write_test.py:89-92](superagi/tools/code/write_test.py:89-92)

### Error Handling

The tools implement error handling for LLM API errors:

```
if 'error' in result and result['message'] is not None:
    ErrorHandler.handle_openai_errors(self.toolkit_config.session, self.agent_id, self.agent_execution_id, result['message'])
```

This ensures that errors from the LLM provider are properly logged and handled.

Sources:
- [superagi/tools/code/write_spec.py:77-78](superagi/tools/code/write_spec.py:77-78)
- [superagi/tools/code/write_code.py:83-84](superagi/tools/code/write_code.py:83-84)
- [superagi/tools/code/write_test.py:94-95](superagi/tools/code/write_test.py:94-95)

## Best Practices for Code Generation

The Code Generation Tools include built-in best practices for generated code, especially in the Coding Tool. These include:

- Placing distinct classes in separate files
- Creating appropriate run scripts as entry points
- Generating suitable dependency files (requirements.txt for Python, package.json for Node.js)
- Including function purpose comments
- Commenting complex logic
- Adhering to language-specific best practices

For Python projects, the preferred testing framework is pytest, and the tools encourage the use of dataclasses.

Sources:
- [superagi/tools/code/prompts/generate_logic.txt:1-11](superagi/tools/code/prompts/generate_logic.txt:1-11)

## Summary

The Code Generation Tools in SuperAGI provide a comprehensive solution for automated software development, enabling agents to:

1. Generate detailed specifications from task descriptions
2. Create code implementations based on those specifications
3. Develop unit tests to verify code functionality

These tools can be used independently or in sequence, supporting a complete development workflow that mirrors best practices in software engineering.

---

# Page: Email and Communication Tools

# Email and Communication Tools

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [superagi/helper/imap_email.py](superagi/helper/imap_email.py)
- [superagi/helper/read_email.py](superagi/helper/read_email.py)
- [superagi/tools/email/read_email.py](superagi/tools/email/read_email.py)
- [superagi/tools/email/send_email.py](superagi/tools/email/send_email.py)
- [superagi/tools/email/send_email_attachment.py](superagi/tools/email/send_email_attachment.py)
- [tests/__init__.py](tests/__init__.py)

</details>



This document describes the email and communication tools in SuperAGI that enable agents to send and receive emails. These tools allow AI agents to communicate with external systems and humans through email channels, providing capabilities for sending basic emails, emails with attachments, and reading emails from IMAP mailboxes.

## Overview of Email Tools

SuperAGI includes three main email tools, all implemented as extensions of the `BaseTool` class:

1. **SendEmailTool**: For sending plain text emails
2. **SendEmailAttachmentTool**: For sending emails with file attachments
3. **ReadEmailTool**: For reading and processing emails from IMAP mailboxes

These tools are supported by helper classes that handle IMAP connections, email processing, and parsing.

### Email Tools Architecture

```mermaid
graph TD
    subgraph "Agent System"
        Agent["Agent"]
        AgentExecution["AgentExecution"]
    end

    subgraph "Email Tools"
        BaseTool["BaseTool"] --> SendEmailTool["SendEmailTool"]
        BaseTool --> SendEmailAttachmentTool["SendEmailAttachmentTool"]
        BaseTool --> ReadEmailTool["ReadEmailTool"]
    end

    subgraph "Helper Classes"
        ImapEmail["ImapEmail"]
        ReadEmail["ReadEmail"]
        ResourceHelper["ResourceHelper"]
    end

    Agent --> AgentExecution
    AgentExecution --> SendEmailTool
    AgentExecution --> SendEmailAttachmentTool
    AgentExecution --> ReadEmailTool

    SendEmailTool --> ImapEmail
    SendEmailAttachmentTool --> ImapEmail
    SendEmailAttachmentTool --> ResourceHelper
    ReadEmailTool --> ImapEmail
    ReadEmailTool --> ReadEmail
```

Sources: [superagi/tools/email/send_email.py](), [superagi/tools/email/send_email_attachment.py](), [superagi/tools/email/read_email.py](), [superagi/helper/imap_email.py](), [superagi/helper/read_email.py]()

## Email Sending Capabilities

### SendEmailTool

The `SendEmailTool` provides functionality to send plain text emails with the following input parameters:

- `to`: Recipient email address
- `subject`: Email subject line
- `body`: Email body text

This tool is defined in [superagi/tools/email/send_email.py:12-87]() and follows the standard BaseTool implementation pattern.

```python
class SendEmailInput(BaseModel):
    to: str = Field(..., description="Email Address of the Receiver, default email address is 'example@example.com'")
    subject: str = Field(..., description="Subject of the Email to be sent")
    body: str = Field(..., description="Email Body to be sent. Escape special characters in the body. Do not add senders details and end it with Warm Regards without entering any name.")
```

Sources: [superagi/tools/email/send_email.py:12-16]()

### SendEmailAttachmentTool

The `SendEmailAttachmentTool` extends the email functionality to include file attachments with an additional parameter:

- `filename`: Name of the file to attach

This tool integrates with the agent's resource management system, supporting both local file system and S3 storage backends.

```python
class SendEmailAttachmentInput(BaseModel):
    to: str = Field(..., description="Email Address of the Receiver, default email address is 'example@example.com'")
    subject: str = Field(..., description="Subject of the Email to be sent")
    body: str = Field(..., description="Email Body to be sent, Do not add senders details in the email body and end it with Warm Regards without entering any name.")
    filename: str = Field(..., description="Name of the file to be sent as an Attachment with Email")
```

Sources: [superagi/tools/email/send_email_attachment.py:25-29]()

### Email Sending Flow

```mermaid
sequenceDiagram
    participant Agent as "Agent"
    participant Tool as "EmailTool"
    participant SMTP as "SMTP Server"
    participant IMAP as "IMAP Server (Draft Mode)"
    
    Agent->>Tool: Execute(to, subject, body, [filename])
    Tool->>Tool: Get email configuration
    
    alt With Attachment
        Tool->>Tool: Retrieve file from resources
    end
    
    alt Draft Mode Enabled
        Tool->>IMAP: Connect and authenticate
        Tool->>IMAP: Save to drafts folder
        IMAP-->>Tool: Confirm saved
    else Draft Mode Disabled
        Tool->>SMTP: Connect and authenticate
        Tool->>SMTP: Send email
        SMTP-->>Tool: Confirm sent
    end
    
    Tool-->>Agent: Return success/failure message
```

Sources: [superagi/tools/email/send_email.py:31-87](), [superagi/tools/email/send_email_attachment.py:47-143]()

### Draft Mode

Both email sending tools support a "draft mode" feature, which saves emails to the drafts folder instead of sending them immediately. This is controlled by the `EMAIL_DRAFT_MODE` configuration parameter. When set to "TRUE", emails are saved to the drafts folder specified by `EMAIL_DRAFT_FOLDER` instead of being sent.

```python
send_to_draft = self.get_tool_config('EMAIL_DRAFT_MODE') or "FALSE"
if send_to_draft.upper() == "TRUE":
    send_to_draft = True
else:
    send_to_draft = False

if send_to_draft:
    draft_folder = self.get_tool_config('EMAIL_DRAFT_FOLDER')
    imap_server = self.get_tool_config('EMAIL_IMAP_SERVER')
    conn = ImapEmail().imap_open(draft_folder, email_sender, email_password, imap_server)
    conn.append(
        draft_folder,
        "",
        imaplib.Time2Internaldate(time.time()),
        str(message).encode("UTF-8")
    )
    return f"Email went to {draft_folder}"
```

Sources: [superagi/tools/email/send_email.py:57-73](), [superagi/tools/email/send_email_attachment.py:114-129]()

## Email Reading Capabilities

### ReadEmailTool

The `ReadEmailTool` allows agents to retrieve and process emails from an IMAP mailbox with the following parameters:

- `imap_folder`: The folder to read from (defaults to "INBOX")
- `page`: Page number for pagination (defaults to 0)
- `limit`: Maximum number of emails to retrieve (defaults to 5)

This tool connects to an IMAP server, fetches emails, extracts headers and body content, and returns a structured representation of the emails.

```python
class ReadEmailInput(BaseModel):
    imap_folder: str = Field(..., description="Email folder to read from. default value is \"INBOX\"")
    page: int = Field(...,
                      description="The index of the page result the function should resturn. Defaults to 0, the first page.")
    limit: int = Field(..., description="Number of emails to fetch in one cycle. Defaults to 5.")
```

Sources: [superagi/tools/email/read_email.py:13-17]()

### Email Reading Process

```mermaid
flowchart TD
    A["ReadEmailTool._execute()"] --> B["Connect to IMAP server"]
    B --> C["Select mail folder"]
    C --> D["Get total message count"]
    D --> E["Loop through messages"]
    E --> F["Fetch message by index"]
    F --> G["Process message structure"]
    G --> H["Extract headers: From, To, Date, Subject"]
    G --> I["Extract message body"]
    G --> J["Detect and process attachments"]
    H --> K["Create structured email data"]
    I --> K
    J --> K
    K --> L["Add to results array"]
    L --> M["Check token limit"]
    M --> N["Return processed emails"]
```

Sources: [superagi/tools/email/read_email.py:33-69](), [superagi/helper/read_email.py:9-87]()

## Helper Classes

### ImapEmail

The `ImapEmail` helper class manages IMAP connections and folder handling:

- `imap_open()`: Establishes connections to IMAP servers
- `adjust_imap_folder()`: Adjusts folder names based on the email provider (e.g., Gmail has special folder naming)

```python
def imap_open(self, imap_folder, email_sender, email_password, imap_server) -> imaplib.IMAP4_SSL:
    """
    Function to open an IMAP connection to the email server.
    """
    conn = imaplib.IMAP4_SSL(imap_server)
    conn.login(email_sender, email_password)
    conn.select(imap_folder)
    return conn
```

Sources: [superagi/helper/imap_email.py:6-21]()

### ReadEmail

The `ReadEmail` helper provides utilities for email processing:

- `clean_email_body()`: Sanitizes and formats email body text
- `obtain_header()`: Extracts and processes email headers
- `download_attachment()`: Handles attachment downloading

Sources: [superagi/helper/read_email.py:8-87]()

## Configuration Requirements

### Required Configuration Parameters

For email tools to function properly, the following configuration parameters must be set:

| Parameter | Description | Required For |
|-----------|-------------|-------------|
| `EMAIL_ADDRESS` | Sender's email address | All email tools |
| `EMAIL_PASSWORD` | Sender's email password | All email tools |
| `EMAIL_SMTP_HOST` | SMTP server hostname | Send Email tools |
| `EMAIL_SMTP_PORT` | SMTP server port | Send Email tools |
| `EMAIL_IMAP_SERVER` | IMAP server hostname | Read Email tool, Draft mode |
| `EMAIL_SIGNATURE` | Optional signature to append to emails | Send Email tools |
| `EMAIL_DRAFT_MODE` | "TRUE" to save to drafts instead of sending | Send Email tools |
| `EMAIL_DRAFT_FOLDER` | Name of the drafts folder | Send Email tools (when draft mode enabled) |

### Configuration Flow

```mermaid
classDiagram
    class EmailToolConfig {
        EMAIL_ADDRESS: string
        EMAIL_PASSWORD: string
        EMAIL_SMTP_HOST: string
        EMAIL_SMTP_PORT: string
        EMAIL_IMAP_SERVER: string
        EMAIL_SIGNATURE: string (optional)
        EMAIL_DRAFT_MODE: string (optional)
        EMAIL_DRAFT_FOLDER: string (optional)
    }
    
    class SendEmailTool {
        get_tool_config()
        _execute()
    }
    
    class SendEmailAttachmentTool {
        get_tool_config()
        _execute()
    }
    
    class ReadEmailTool {
        get_tool_config()
        _execute()
    }
    
    EmailToolConfig -- SendEmailTool: Configures
    EmailToolConfig -- SendEmailAttachmentTool: Configures
    EmailToolConfig -- ReadEmailTool: Configures
```

Sources: [superagi/tools/email/send_email.py:43-48](), [superagi/tools/email/send_email_attachment.py:97-102](), [superagi/tools/email/read_email.py:45-50]()

## Integration with Agent System

The email tools integrate with the broader agent system through the tool execution framework. Agents can access these tools if they are included in the agent's toolkit configuration.

```mermaid
sequenceDiagram
    participant Agent
    participant AgentExecutor
    participant ToolManager
    participant EmailTool
    
    Agent->>AgentExecutor: Execute iteration
    AgentExecutor->>ToolManager: Get available tools
    ToolManager-->>AgentExecutor: Return tools (including email tools)
    AgentExecutor->>EmailTool: Execute tool with parameters
    EmailTool->>EmailTool: Process email operation
    EmailTool-->>AgentExecutor: Return result
    AgentExecutor-->>Agent: Include result in context
```

Sources: [superagi/tools/email/send_email.py](), [superagi/tools/email/send_email_attachment.py](), [superagi/tools/email/read_email.py]()

## Error Handling

The email tools include several error handling mechanisms:

1. **Configuration Validation**:
   - Check if email address and password are provided
   - Return appropriate error messages if missing

2. **File Access Checks** (for `SendEmailAttachmentTool`):
   - Verify if the file exists
   - Handle S3 and local file system appropriately

3. **Email Processing Safeguards** (for `ReadEmailTool`):
   - Safe handling of email content types
   - Character encoding and decoding safeguards
   - Empty results handling

Sources: [superagi/tools/email/send_email.py:45-48](), [superagi/tools/email/send_email_attachment.py:74-78](), [superagi/tools/email/read_email.py:66-67]()

## Summary

The Email and Communication Tools in SuperAGI provide agents with robust capabilities for email communication, including sending plain emails, emails with attachments, and reading emails from IMAP servers. These tools are configurable through the tool configuration system and integrate with the agent execution framework. They provide a foundation for building agents that can communicate via email channels, potentially allowing for scheduling, reporting, notifications, and other email-based workflows.

---

# Page: Image Generation Tools

# Image Generation Tools

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [superagi/tools/image_generation/dalle_image_gen.py](superagi/tools/image_generation/dalle_image_gen.py)
- [superagi/tools/image_generation/stable_diffusion_image_gen.py](superagi/tools/image_generation/stable_diffusion_image_gen.py)
- [superagi/tools/instagram_tool/README.MD](superagi/tools/instagram_tool/README.MD)
- [superagi/tools/instagram_tool/instagram.py](superagi/tools/instagram_tool/instagram.py)
- [superagi/tools/instagram_tool/instagram_toolkit.py](superagi/tools/instagram_tool/instagram_toolkit.py)
- [tests/unit_tests/tools/image_generation/test_dalle_image_gen.py](tests/unit_tests/tools/image_generation/test_dalle_image_gen.py)
- [tests/unit_tests/tools/image_generation/test_stable_diffusion_image_gen.py](tests/unit_tests/tools/image_generation/test_stable_diffusion_image_gen.py)
- [tests/unit_tests/tools/instagram_tool/__init__.py](tests/unit_tests/tools/instagram_tool/__init__.py)
- [tests/unit_tests/tools/instagram_tool/test_instagram_tool.py](tests/unit_tests/tools/instagram_tool/test_instagram_tool.py)
- [tests/unit_tests/tools/instagram_tool/test_instagram_toolkit.py](tests/unit_tests/tools/instagram_tool/test_instagram_toolkit.py)

</details>



This document explains the image generation capabilities in SuperAGI, which enable agents to create images based on text prompts. SuperAGI provides integration with two popular image generation models: OpenAI's DALL-E and Stability AI's Stable Diffusion. These tools allow agents to generate custom images that can be stored in the resource system and used in various tasks, including social media posting.

## Overview

Image generation tools in SuperAGI extend the BaseTool class and implement specific functionality to interact with external image generation APIs. The system currently includes two primary image generation tools:

1. DALL-E Image Generation Tool - Uses OpenAI's DALL-E model
2. Stable Diffusion Image Generation Tool - Uses Stability AI's Stable Diffusion model

These tools can be used independently or in combination with other tools, such as the Instagram Tool, which allows posting generated images to social media.

## Architecture

### Image Generation Tools System Architecture

```mermaid
graph TD
    subgraph "Agent System"
        Agent["Agent"] --> AgentExecutor["AgentExecutor"]
        AgentExecutor --> ToolManager["ToolManager"]
    end

    subgraph "Image Generation Tools"
        ToolManager --> BaseTool["BaseTool"]
        BaseTool --> DalleImageGenTool["DalleImageGenTool"]
        BaseTool --> StableDiffusionImageGenTool["StableDiffusionImageGenTool"]
        
        DalleImageGenTool --> DalleImageGenInput["DalleImageGenInput"]
        StableDiffusionImageGenTool --> StableDiffusionImageGenInput["StableDiffusionImageGenInput"]
    end
    
    subgraph "External APIs"
        DalleImageGenTool --> OpenAIAPI["OpenAI API"]
        StableDiffusionImageGenTool --> StabilityAPI["Stability AI API"]
    end
    
    subgraph "Resource Management"
        DalleImageGenTool --> ResourceManager["ResourceManager"]
        StableDiffusionImageGenTool --> ResourceManager
        ResourceManager --> FileStorage["File Storage/S3"]
    end
    
    subgraph "Integration"
        ImageGenTools["Image Generation Tools"] --> InstagramTool["Instagram Tool"]
        InstagramTool --> MetaGraphAPI["Meta Graph API"]
    end
```

Sources: [superagi/tools/image_generation/dalle_image_gen.py](), [superagi/tools/image_generation/stable_diffusion_image_gen.py](), [superagi/tools/instagram_tool/instagram.py]()

## DALL-E Image Generation Tool

The DALL-E Image Generation Tool leverages OpenAI's DALL-E model to generate images based on text prompts. It is implemented in the `DalleImageGenTool` class.

### Input Schema

The `DalleImageGenInput` class defines the input parameters for the DALL-E tool:

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| prompt | string | Text description for image generation | Required |
| size | integer | Size of the image to be generated | 512 |
| num | integer | Number of images to generate | 2 |
| image_names | list | Names for the generated image files | Required |

### Implementation Details

The DALL-E tool operates through the following workflow:

1. Validates input parameters (including checking for a valid API key)
2. Adjusts the size parameter to one of the accepted values (256, 512, or 1024)
3. Calls the OpenAI DALL-E API through the `OpenAiDalle` class
4. Downloads the generated images from the URLs provided in the response
5. Saves the images using the resource manager with the specified file names

```mermaid
sequenceDiagram
    participant Agent as "Agent"
    participant DalleTool as "DalleImageGenTool"
    participant OpenAI as "OpenAiDalle"
    participant ResManager as "ResourceManager"
    
    Agent->>DalleTool: _execute(prompt, image_names, size, num)
    DalleTool->>DalleTool: Validate parameters
    DalleTool->>DalleTool: Get API key from config
    DalleTool->>OpenAI: generate_image(prompt, size)
    OpenAI-->>DalleTool: Return image URLs
    loop For each image (i=0 to num-1)
        DalleTool->>OpenAI: Download image data
        DalleTool->>ResManager: write_binary_file(image_names[i], data)
    end
    DalleTool-->>Agent: "Images downloaded successfully"
```

Sources: [superagi/tools/image_generation/dalle_image_gen.py:19-71]()

## Stable Diffusion Image Generation Tool

The Stable Diffusion Image Generation Tool uses Stability AI's Stable Diffusion model to create images from text prompts. It provides more customization options than the DALL-E tool.

### Input Schema

The `StableDiffusionImageGenInput` class defines the input parameters:

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| prompt | string | Text description for image generation | Required |
| height | integer | Height of the image in pixels | 512 |
| width | integer | Width of the image in pixels | 512 |
| num | integer | Number of images to generate | 2 |
| steps | integer | Number of diffusion steps to run | 50 |
| image_names | list | Names for the generated image files | Required |

### Implementation Details

The Stable Diffusion tool follows this workflow:

1. Retrieves the Stability API key from tool configuration
2. Calls the Stability AI API via the `call_stable_diffusion` method
3. Processes the base64-encoded images from the response
4. Decodes the images and saves them using the resource manager

```mermaid
sequenceDiagram
    participant Agent as "Agent"
    participant SDTool as "StableDiffusionImageGenTool"
    participant StabilityAPI as "Stability AI API"
    participant ResManager as "ResourceManager"
    
    Agent->>SDTool: _execute(prompt, image_names, width, height, num, steps)
    SDTool->>SDTool: Get API key from config
    SDTool->>SDTool: call_stable_diffusion(api_key, width, height, num, prompt, steps)
    SDTool->>StabilityAPI: POST request to API
    StabilityAPI-->>SDTool: JSON response with base64 images
    SDTool->>SDTool: Extract base64 strings from response
    loop For each image (i=0 to num-1)
        SDTool->>SDTool: Decode base64 to image data
        SDTool->>ResManager: write_binary_file(image_names[i], data)
    end
    SDTool-->>Agent: "Images downloaded and saved successfully!!"
```

Sources: [superagi/tools/image_generation/stable_diffusion_image_gen.py:15-98]()

## Integration with Instagram

SuperAGI includes an Instagram Tool that can work with the image generation tools to automate social media posting. This tool takes generated images and posts them to an Instagram business account.

### Instagram Tool Workflow

```mermaid
graph TD
    subgraph "Instagram Tool Flow"
        Start["Execute Instagram Tool"] --> GetConfig["Get META_USER_ACCESS_TOKEN and FACEBOOK_PAGE_ID"]
        GetConfig --> CreateCaption["Create caption using LLM"]
        CreateCaption --> GetFilePath["Get file path for image"]
        GetFilePath --> GetInstaID["Get Instagram business account ID"]
        GetInstaID --> UploadToS3["Upload image to S3 bucket"]
        UploadToS3 --> GetMediaContainer["Create media container in Instagram"]
        GetMediaContainer --> PublishMedia["Publish media to Instagram"]
        PublishMedia --> End["Return success message"]
    end
```

The Instagram Tool:
1. Creates an engaging caption for the post using an LLM
2. Retrieves the Instagram business account ID associated with the Facebook page
3. Uploads the image to an S3 bucket to make it publicly accessible
4. Creates a media container in Instagram with the image URL and caption
5. Publishes the media container to the Instagram account

Sources: [superagi/tools/instagram_tool/instagram.py:31-205]()

## Configuration Requirements

### DALL-E Image Generation Tool

Required configuration in the toolkit settings:

| Key | Description |
|-----|-------------|
| OPENAI_API_KEY | Your OpenAI API key with DALL-E access |

### Stable Diffusion Image Generation Tool

Required configuration in the toolkit settings:

| Key | Description |
|-----|-------------|
| STABILITY_API_KEY | Your Stability AI API key |
| ENGINE_ID | The engine ID to use (e.g., "stable-diffusion-v1-5") |

### Instagram Tool

Required configuration in the toolkit settings:

| Key | Description |
|-----|-------------|
| META_USER_ACCESS_TOKEN | User access token for the Meta Graph API |
| FACEBOOK_PAGE_ID | ID of the Facebook page connected to your Instagram business account |
| INSTAGRAM_TOOL_BUCKET_NAME | S3 bucket name for temporary image storage (environment variable) |

Sources: [superagi/tools/instagram_tool/instagram_toolkit.py:7-18](), [superagi/tools/instagram_tool/README.MD:16-31]()

## Usage Examples

### Generating Images with DALL-E

```
{
  "prompt": "A futuristic city with flying cars and tall glass buildings",
  "size": 1024,
  "num": 2,
  "image_names": ["future_city_1.png", "future_city_2.png"]
}
```

### Generating Images with Stable Diffusion

```
{
  "prompt": "A detailed oil painting of a mountain landscape with a lake",
  "height": 768,
  "width": 768,
  "num": 1,
  "steps": 50,
  "image_names": ["landscape.png"]
}
```

### Posting to Instagram

```
{
  "photo_description": "A beautiful AI-generated landscape painting",
  "filename": "landscape.png"
}
```

## Error Handling

Both image generation tools implement error handling for:

1. Missing API keys - Returns a message indicating the need to add the API key in configuration
2. Invalid API responses - Returns the error message from the API response
3. Size parameter validation - The DALL-E tool automatically adjusts sizes to valid values (256, 512, or 1024)
4. Engine constraints - The Stable Diffusion tool enforces minimum image dimensions based on the selected engine

Sources: [superagi/tools/image_generation/dalle_image_gen.py:57-62](), [superagi/tools/image_generation/stable_diffusion_image_gen.py:48-55](), [superagi/tools/image_generation/stable_diffusion_image_gen.py:77-82]()

## Testing

SuperAGI includes unit tests for both image generation tools to ensure they function correctly. These tests mock the external API calls to simulate responses and verify that the tools process the results correctly.

Test files:
- [tests/unit_tests/tools/image_generation/test_dalle_image_gen.py]()
- [tests/unit_tests/tools/image_generation/test_stable_diffusion_image_gen.py]()

## Limitations and Considerations

1. DALL-E only supports specific image sizes (256×256, 512×512, or 1024×1024)
2. Stable Diffusion may have minimum size requirements depending on the engine selected
3. Instagram Tool requires an Instagram Business Account and Facebook Page connection
4. Image generation can be computationally expensive and may have usage costs associated with the external APIs

---

# Page: Tool Authentication

# Tool Authentication

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [gui/pages/Content/APM/ApmDashboard.js](gui/pages/Content/APM/ApmDashboard.js)
- [gui/pages/Content/Marketplace/MarketKnowledge.js](gui/pages/Content/Marketplace/MarketKnowledge.js)
- [gui/pages/Content/Toolkits/ToolkitWorkspace.js](gui/pages/Content/Toolkits/ToolkitWorkspace.js)
- [gui/pages/Content/Toolkits/Toolkits.js](gui/pages/Content/Toolkits/Toolkits.js)
- [superagi/controllers/google_oauth.py](superagi/controllers/google_oauth.py)
- [superagi/tools/image_generation/dalle_image_gen.py](superagi/tools/image_generation/dalle_image_gen.py)
- [superagi/tools/image_generation/stable_diffusion_image_gen.py](superagi/tools/image_generation/stable_diffusion_image_gen.py)
- [superagi/tools/instagram_tool/README.MD](superagi/tools/instagram_tool/README.MD)
- [superagi/tools/instagram_tool/instagram.py](superagi/tools/instagram_tool/instagram.py)
- [superagi/tools/instagram_tool/instagram_toolkit.py](superagi/tools/instagram_tool/instagram_toolkit.py)
- [tests/unit_tests/tools/image_generation/test_dalle_image_gen.py](tests/unit_tests/tools/image_generation/test_dalle_image_gen.py)
- [tests/unit_tests/tools/image_generation/test_stable_diffusion_image_gen.py](tests/unit_tests/tools/image_generation/test_stable_diffusion_image_gen.py)
- [tests/unit_tests/tools/instagram_tool/__init__.py](tests/unit_tests/tools/instagram_tool/__init__.py)
- [tests/unit_tests/tools/instagram_tool/test_instagram_tool.py](tests/unit_tests/tools/instagram_tool/test_instagram_tool.py)
- [tests/unit_tests/tools/instagram_tool/test_instagram_toolkit.py](tests/unit_tests/tools/instagram_tool/test_instagram_toolkit.py)

</details>



This page documents the authentication mechanisms used by SuperAGI tools to securely connect with external services and APIs. It covers how different tools authenticate with their respective services, the supported authentication methods, and how to configure authentication credentials in the system.

For information about the general tools system, see [Tools System](#4), and for details about specific tools, see their respective pages such as [Email and Communication Tools](#4.3) or [Image Generation Tools](#4.4).

## Overview of Authentication Methods

SuperAGI supports three primary authentication methods for external service integration:

1. **API Key Authentication**: Simple string tokens used for services like DALL-E and Stable Diffusion
2. **OAuth Authentication**: Interactive authentication flow for services like Google Calendar and Twitter
3. **Token-based Authentication**: Pre-obtained tokens for services like Instagram/Meta

The diagram below shows the relationship between these authentication methods and the tools that use them:

```mermaid
graph TD
    User(["User"]) --> ToolkitWorkspace["Toolkit Workspace UI"]
    ToolkitWorkspace --> ToolConfig["Tool Configuration Storage"]
    ToolkitWorkspace --> OAuthFlow["OAuth Flow Initiation"]
    
    OAuthFlow --> GoogleOAuth["Google OAuth"]
    OAuthFlow --> TwitterOAuth["Twitter OAuth"]
    
    ToolConfig --> ApiKeyAuth["API Key Authentication"]
    ToolConfig --> TokenAuth["Token-based Authentication"]
    OAuthFlow --> OAuthTokens["OAuth Tokens Storage"]
    
    ApiKeyAuth --> DALLE["DALL-E Tool"]
    ApiKeyAuth --> StableDiffusion["Stable Diffusion Tool"]
    TokenAuth --> Instagram["Instagram Tool"]
    OAuthTokens --> GoogleCalendar["Google Calendar Tool"]
    OAuthTokens --> Twitter["Twitter Tool"]
    
    DALLE --> OpenAIAPI["OpenAI API"]
    StableDiffusion --> StabilityAPI["Stability AI API"]
    Instagram --> MetaAPI["Meta Graph API"]
    GoogleCalendar --> GoogleAPI["Google Calendar API"]
    Twitter --> TwitterAPI["Twitter API"]
```

Sources: 
- [superagi/tools/image_generation/dalle_image_gen.py:54-62]()
- [superagi/tools/image_generation/stable_diffusion_image_gen.py:46-51]()
- [superagi/tools/instagram_tool/instagram.py:63-69]()
- [gui/pages/Content/Toolkits/ToolkitWorkspace.js:90-113]()

## Authentication Methods

### API Key Authentication

Many tools in SuperAGI use API keys for authentication. These are simple string tokens that are passed with API requests to verify the identity of the requester.

#### Implementation

In the code, API keys are retrieved using the `get_tool_config` method and validated before making API requests:

```python
# Example from DALL-E Image Generation Tool
api_key = self.get_tool_config("OPENAI_API_KEY")
if api_key is None:
    return "Enter your OpenAi api key in the configuration"
```

The sequence diagram below illustrates the API key authentication flow:

```mermaid
sequenceDiagram
    participant "User" as User
    participant "SuperAGI Frontend" as Frontend
    participant "SuperAGI Backend" as Backend
    participant "External API" as API
    
    User->>Frontend: "Configure toolkit with API key"
    Frontend->>Backend: "updateToolConfig(toolkit_name, config_data)"
    Backend->>Backend: "Store API key in ToolConfig table"
    User->>Frontend: "Run agent with tool"
    Frontend->>Backend: "Execute agent"
    Backend->>Backend: "Tool retrieves API key"
    Backend->>API: "Make API request with key"
    API->>Backend: "Return API response"
    Backend->>Frontend: "Update agent execution status"
    Frontend->>User: "Show tool execution result"
```

Sources:
- [superagi/tools/image_generation/dalle_image_gen.py:60-62]()
- [superagi/tools/image_generation/stable_diffusion_image_gen.py:48-51]()

### OAuth Authentication

OAuth is used for more complex authentication scenarios where users need to grant permission for SuperAGI to access their accounts on external services.

#### Google OAuth Flow

The Google OAuth flow in SuperAGI follows the standard OAuth 2.0 authorization code flow:

```mermaid
sequenceDiagram
    participant "User" as User
    participant "SuperAGI Frontend" as Frontend
    participant "SuperAGI Backend" as Backend
    participant "Google OAuth" as Google
    
    User->>Frontend: "Click Authenticate Tool"
    Frontend->>Backend: "authenticateGoogleCred(toolkit_id)"
    Backend->>Frontend: "Return client_id"
    Frontend->>Google: "Redirect to Google OAuth page"
    Google->>User: "Present authentication form"
    User->>Google: "Authorize access"
    Google->>Backend: "Redirect with authorization code"
    Backend->>Google: "Exchange code for tokens"
    Google->>Backend: "Return access and refresh tokens"
    Backend->>Backend: "Store tokens in OauthTokens table"
    Backend->>Frontend: "Redirect to success page"
    Frontend->>User: "Show authentication success"
```

The frontend initiates the authentication by redirecting to Google's OAuth page:

```javascript
function getGoogleToken(client_data) {
  var redirect_uri = "";
  if (env == "PROD") {
    redirect_uri = 'https://app.superagi.com/api/google/oauth-tokens';
  } else {
    redirect_uri = "http://localhost:3000/api/google/oauth-tokens";
  }
  const client_id = client_data.client_id
  const scope = 'https://www.googleapis.com/auth/calendar';
  window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${client_id}&redirect_uri=${redirect_uri}&access_type=offline&approval_prompt=force&response_type=code&scope=${scope}&state=${toolkitDetails.id}`;
}
```

The backend handles the OAuth callback and token exchange:

```python
@router.get('/oauth-tokens')
async def google_auth_calendar(code: str = Query(...), state: str = Query(...)):
    toolkit_id = int(state)
    # Get client_id and client_secret from the database
    # Exchange code for tokens
    # Store tokens in the database
```

Sources:
- [gui/pages/Content/Toolkits/ToolkitWorkspace.js:32-42]()
- [gui/pages/Content/Toolkits/ToolkitWorkspace.js:90-101]()
- [superagi/controllers/google_oauth.py:24-64]()

#### Twitter OAuth Flow

Twitter uses a similar OAuth process with its own endpoints:

```javascript
function getTwitterToken(oauth_data) {
  window.location.href = `https://api.twitter.com/oauth/authenticate?oauth_token=${oauth_data.oauth_token}`
}
```

Sources:
- [gui/pages/Content/Toolkits/ToolkitWorkspace.js:44-46]()
- [gui/pages/Content/Toolkits/ToolkitWorkspace.js:102-112]()

### Token-based Authentication

Some services like Instagram/Meta require pre-obtained tokens. Users must obtain these tokens separately and configure them in the toolkit.

For example, the Instagram Tool requires a Meta user access token and Facebook page ID:

```python
meta_user_access_token = self.get_tool_config("META_USER_ACCESS_TOKEN")
facebook_page_id = self.get_tool_config("FACEBOOK_PAGE_ID")

if meta_user_access_token is None:
    return "Error: Missing meta user access token."

if facebook_page_id is None:
    return "Error: Missing facebook page id."
```

Sources:
- [superagi/tools/instagram_tool/instagram.py:63-69]()
- [superagi/tools/instagram_tool/instagram_toolkit.py:14-18]()

## Configuration and Storage

### Configuring Authentication in the UI

Authentication credentials are configured in the Toolkit Workspace UI. The interface provides input fields for credentials and buttons to initiate OAuth flows when needed.

The configuration UI allows users to:
1. Enter API keys and other credentials
2. Initiate OAuth authentication for supported services
3. Update stored credentials

```javascript
{apiConfigs.length > 0 ? (apiConfigs.map((config, index) => (
  <div key={index}>
    <div className="vertical_containers w_100 color_gray mb_20 text_align_left">
      <label className="mb_6">{convertToTitleCase(config.key)}</label>
      <div className={styles.search_box}>
        <input className="color_white" type={config?.is_secret ? 'password' : 'text'} 
               value={config.value || ''} onChange={(event) => handleKeyChange(event, index)}/>
      </div>
    </div>
  </div>
))) : (<div>No configurations found</div>)}

{apiConfigs.length > 0 && (
  <div className="horizontal_space_between">
    {authenticateToolkits.includes(toolkitDetails.name) &&
      <button className="primary_button w_fit_content" onClick={() => handleAuthenticateClick(toolkitDetails.name)}>
        Authenticate Tool
      </button>}
      <button className="primary_button" onClick={handleUpdateChanges}>
        Update Changes
      </button>
  </div>)}
```

Sources:
- [gui/pages/Content/Toolkits/ToolkitWorkspace.js:188-209]()

### Credential Storage and Security

Authentication credentials are stored securely in the database:

1. **ToolConfig table**: Stores API keys, client IDs, and other simple credentials
2. **OauthTokens table**: Stores OAuth tokens obtained from authentication flows

Sensitive credentials are encrypted before storage and decrypted when needed:

```python
if(is_encrypted(client_id.value)):
    client_id = decrypt_data(client_id.value)
else:
    client_id = client_id.value
```

Sources:
- [superagi/controllers/google_oauth.py:28-36]()
- [superagi/controllers/google_oauth.py:74-81]()

## Supported Tools and Authentication Methods

The following table summarizes the tools in SuperAGI and their authentication methods:

| Tool/Toolkit | Authentication Method | Required Credentials |
|--------------|------------------------|----------------------|
| DALL-E Image Generation | API Key | OPENAI_API_KEY |
| Stable Diffusion Image Generation | API Key | STABILITY_API_KEY, ENGINE_ID |
| Google Calendar | OAuth | GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET |
| Twitter | OAuth | (OAuth token handled by the system) |
| Instagram | Token-based | META_USER_ACCESS_TOKEN, FACEBOOK_PAGE_ID |

Sources:
- [superagi/tools/image_generation/dalle_image_gen.py:20-71]()
- [superagi/tools/image_generation/stable_diffusion_image_gen.py:25-98]()
- [superagi/tools/instagram_tool/instagram_toolkit.py:7-18]()
- [gui/pages/Content/Toolkits/ToolkitWorkspace.js:20]()

## Authentication Flow in Code

The diagram below illustrates the code paths involved in tool authentication:

```mermaid
graph TD
    ToolkitWorkspace["ToolkitWorkspace.js\nUI Component"] -->|"authenticateGoogleCred()\nauthenticateTwitterCred()"| DashboardService["DashboardService.js\nAPI Client"]
    DashboardService -->|"HTTP Request"| GoogleOAuth["google_oauth.py\nBackend Controller"]
    
    GoogleOAuth -->|"Query"| ToolConfig["ToolConfig\nDatabase Model"]
    GoogleOAuth -->|"Store"| OauthTokens["OauthTokens\nDatabase Model"]
    
    Tool["BaseTool\nTool Implementation"] -->|"get_tool_config()"| ToolkitConfig["ToolkitConfig\nConfiguration Access"]
    ToolkitConfig -->|"Query"| ToolConfig
    ToolkitConfig -->|"Query"| OauthTokens
    
    Tool -->|"API Request with Auth"| ExternalService["External Service\n(Google, OpenAI, etc.)"]
```

Sources:
- [gui/pages/Content/Toolkits/ToolkitWorkspace.js:90-113]()
- [superagi/controllers/google_oauth.py:24-64]()
- [superagi/tools/image_generation/dalle_image_gen.py:60-71]()
- [superagi/tools/instagram_tool/instagram.py:63-69]()

## Summary

Tool Authentication in SuperAGI provides a flexible and secure way for tools to authenticate with external services. The system supports API keys, OAuth, and token-based authentication methods, accommodating a wide range of external service requirements. The toolkit workspace UI provides an intuitive interface for configuring authentication credentials, and the backend handles the secure storage and retrieval of these credentials.

By understanding how tool authentication works in SuperAGI, developers can integrate new external services and users can securely configure their tools to work with third-party APIs.

---

# Page: Resource Management

# Resource Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [migrations/versions/c02f3d759bf3_add_summary_to_resource.py](migrations/versions/c02f3d759bf3_add_summary_to_resource.py)
- [superagi/controllers/resources.py](superagi/controllers/resources.py)
- [superagi/helper/resource_helper.py](superagi/helper/resource_helper.py)
- [superagi/models/resource.py](superagi/models/resource.py)
- [superagi/resource_manager/file_manager.py](superagi/resource_manager/file_manager.py)
- [superagi/resource_manager/resource_summary.py](superagi/resource_manager/resource_summary.py)
- [superagi/tools/resource/__init__.py](superagi/tools/resource/__init__.py)
- [superagi/tools/resource/query_resource.py](superagi/tools/resource/query_resource.py)
- [superagi/tools/resource/resource_toolkit.py](superagi/tools/resource/resource_toolkit.py)
- [superagi/types/storage_types.py](superagi/types/storage_types.py)
- [superagi/types/vector_store_types.py](superagi/types/vector_store_types.py)
- [superagi/worker.py](superagi/worker.py)
- [tests/unit_tests/helper/test_resource_helper.py](tests/unit_tests/helper/test_resource_helper.py)

</details>



## Purpose and Scope

Resource Management in SuperAGI provides a system for handling files, data, and artifacts that agents work with. It enables the storage, retrieval, processing, and querying of resources within the agent ecosystem. This system supports both local file storage and S3 cloud storage, along with vectorization capabilities for efficient resource querying.

For information on how Language Models are integrated with resources, see [LLM Integration](#6).

## System Architecture

```mermaid
graph TD
    subgraph "API Layer"
        ResourceController["ResourceController"]
    end

    subgraph "Core Components"
        ResourceHelper["ResourceHelper"]
        FileManager["FileManager"]
        S3Helper["S3Helper"]
        ResourceSummarizer["ResourceSummarizer"]
    end

    subgraph "Storage Systems"
        LocalFileSystem["Local File System"]
        S3Storage["Amazon S3"]
    end

    subgraph "Vector Storage"
        VectorStoreFactory["VectorStoreFactory"]
        Redis["Redis"]
        Pinecone["Pinecone"]
        Chroma["ChromaDB"]
        Weaviate["Weaviate"]
        Qdrant["Qdrant"]
        LanceDB["LanceDB"]
    end

    subgraph "Agent Integration"
        Agent["Agent"]
        AgentExecution["AgentExecution"]
        QueryResourceTool["QueryResourceTool"]
    end

    ResourceController --> ResourceHelper
    ResourceHelper --> FileManager
    ResourceHelper --> S3Helper
    
    FileManager --> LocalFileSystem
    S3Helper --> S3Storage
    
    ResourceController --> ResourceSummarizer
    ResourceSummarizer --> VectorStoreFactory
    
    VectorStoreFactory --> Redis
    VectorStoreFactory --> Pinecone
    VectorStoreFactory --> Chroma
    VectorStoreFactory --> Weaviate
    VectorStoreFactory --> Qdrant
    VectorStoreFactory --> LanceDB
    
    Agent --> ResourceController
    Agent --> QueryResourceTool
    QueryResourceTool --> VectorStoreFactory
```

Sources: [superagi/controllers/resources.py](), [superagi/helper/resource_helper.py](), [superagi/resource_manager/file_manager.py](), [superagi/resource_manager/resource_summary.py](), [superagi/types/vector_store_types.py]()

## Resource Model

The Resource model is the core entity that represents files and data in the system.

```mermaid
classDiagram
    class Resource {
        +id: Integer
        +name: String
        +storage_type: String
        +path: String
        +size: Integer
        +type: String
        +channel: String
        +agent_id: Integer
        +agent_execution_id: Integer
        +summary: Text
        +validate_resource_type()
        +find_by_run_ids()
    }
```

### Resource Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | Integer | Primary key identifier for the resource |
| `name` | String | Name of the resource (e.g., file name) |
| `storage_type` | String | Storage system used (FILE or S3) |
| `path` | String | Path where the resource is stored |
| `size` | Integer | Size of the resource in bytes |
| `type` | String | MIME type of the resource (e.g., application/pdf) |
| `channel` | String | Whether the resource is an input (INPUT) or output (OUTPUT) |
| `agent_id` | Integer | ID of the agent associated with the resource |
| `agent_execution_id` | Integer | ID of the agent execution that created/used the resource |
| `summary` | Text | Summary of the resource content (for efficient querying) |

Sources: [superagi/models/resource.py](), [migrations/versions/c02f3d759bf3_add_summary_to_resource.py]()

## Storage Systems

SuperAGI supports two primary storage types for resources:

```mermaid
graph TD
    subgraph "StorageType Enum"
        StorageType["StorageType"] --> FILE["FILE"]
        StorageType --> S3["S3"]
    end

    subgraph "Storage Selection Flow"
        Config["Configuration"] --> |STORAGE_TYPE| StorageTypeSelection["Storage Type Selection"]
        StorageTypeSelection --> |FILE| LocalFileSystem["Local File System"]
        StorageTypeSelection --> |S3| S3Storage["Amazon S3"]
    end
    
    subgraph "S3 Configuration"
        S3Storage --> S3Config["S3 Configuration"]
        S3Config --> AWS_ACCESS_KEY_ID["AWS_ACCESS_KEY_ID"]
        S3Config --> AWS_SECRET_ACCESS_KEY["AWS_SECRET_ACCESS_KEY"]
        S3Config --> BUCKET_NAME["BUCKET_NAME"]
    end
```

### Local File Storage

Local file storage stores resources on the filesystem where SuperAGI is running. File paths are determined based on the agent and agent execution IDs, creating a hierarchical structure.

Key configuration:
- `RESOURCES_INPUT_ROOT_DIR`: Root directory for input resources
- `RESOURCES_OUTPUT_ROOT_DIR`: Root directory for output resources

### S3 Storage

Amazon S3 storage enables storing resources in the cloud. This requires proper AWS credentials configuration.

Key configuration:
- `AWS_ACCESS_KEY_ID`: AWS access key ID for S3 authentication
- `AWS_SECRET_ACCESS_KEY`: AWS secret access key for S3 authentication
- `BUCKET_NAME`: Name of the S3 bucket to store resources in

Sources: [superagi/types/storage_types.py](), [superagi/helper/resource_helper.py:27-29](), [superagi/controllers/resources.py:25-29]()

## Resource Operations

### Resource Upload Flow

```mermaid
sequenceDiagram
    participant Client
    participant ResourceController
    participant ResourceHelper
    participant StorageSystem
    participant Database
    participant ResourceSummarizer

    Client->>ResourceController: POST /add/{agent_id}
    ResourceController->>ResourceHelper: get_root_input_dir()
    ResourceHelper-->>ResourceController: input_directory
    
    alt storage_type = FILE
        ResourceController->>StorageSystem: Write file to filesystem
    else storage_type = S3
        ResourceController->>StorageSystem: Upload to S3 bucket
    end
    
    ResourceController->>Database: Create Resource record
    Database-->>ResourceController: resource_id
    
    ResourceController->>ResourceSummarizer: summarize_resource(agent_id, resource_id)
    ResourceController-->>Client: Return Resource object
```

### Resource Download Flow

```mermaid
sequenceDiagram
    participant Client
    participant ResourceController
    participant Database
    participant StorageSystem
    
    Client->>ResourceController: GET /get/{resource_id}
    ResourceController->>Database: Query Resource by ID
    Database-->>ResourceController: Resource object
    
    alt storage_type = FILE
        ResourceController->>StorageSystem: Read file from filesystem
    else storage_type = S3
        ResourceController->>StorageSystem: Get object from S3 bucket
    end
    
    StorageSystem-->>ResourceController: File content
    ResourceController-->>Client: StreamingResponse with file
```

### Resource Operations API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/add/{agent_id}` | POST | Upload a file as a resource for an agent |
| `/get/all/{agent_id}` | GET | Get all resources for an agent |
| `/get/{resource_id}` | GET | Download a specific resource by ID |

Sources: [superagi/controllers/resources.py:32-174]()

## Resource Helper

The ResourceHelper class provides utility functions for managing resource paths and creating resource objects.

```mermaid
classDiagram
    class ResourceHelper {
        +make_written_file_resource()
        +get_formatted_agent_level_path()
        +get_formatted_agent_execution_level_path()
        +get_resource_path()
        +get_root_output_dir()
        +get_root_input_dir()
        +get_agent_write_resource_path()
        +get_agent_read_resource_path()
    }
```

### Path Management

ResourceHelper provides methods to generate appropriate paths for resources based on the configuration, agent, and execution context:

1. **Root Directories**:
   - `get_root_input_dir()`: Returns the configured root directory for input resources
   - `get_root_output_dir()`: Returns the configured root directory for output resources

2. **Agent-Specific Paths**:
   - `get_formatted_agent_level_path()`: Formats a path with the agent ID/name
   - `get_formatted_agent_execution_level_path()`: Formats a path with the agent execution ID/name
   - `get_agent_write_resource_path()`: Gets the path to write agent-specific resources
   - `get_agent_read_resource_path()`: Gets the path to read agent-specific resources

3. **Resource Creation**:
   - `make_written_file_resource()`: Creates a Resource object for files written by agents

Sources: [superagi/helper/resource_helper.py](), [tests/unit_tests/helper/test_resource_helper.py]()

## File Manager

The FileManager class provides high-level methods for file operations:

```mermaid
classDiagram
    class FileManager {
        -session: Session
        -agent_id: Integer
        -agent_execution_id: Integer
        +write_binary_file()
        +write_to_s3()
        +write_file()
        +write_csv_file()
        +get_agent_resource_path()
        +read_file()
        +get_files()
    }
```

### Key Operations

1. **File Writing**:
   - `write_file()`: Writes text content to a file
   - `write_binary_file()`: Writes binary data to a file
   - `write_csv_file()`: Writes CSV data to a file

2. **File Reading**:
   - `read_file()`: Reads content from a file
   - `get_files()`: Lists all files in the agent's resource directory

3. **S3 Integration**:
   - `write_to_s3()`: Uploads files to S3 when S3 storage is configured

Sources: [superagi/resource_manager/file_manager.py]()

## Resource Summarization and Vectorization

Resources can be summarized and vectorized for efficient querying by agents:

```mermaid
graph TD
    subgraph "Resource Summarization Process"
        Upload["Resource Upload"] --> |"summarize_resource(agent_id, resource_id)"| SummarizeTask["Summarize Resource Task"]
        SummarizeTask --> ResourceSummarizer["ResourceSummarizer"]
        ResourceSummarizer --> CreateDocuments["Create LlamaIndex Documents"]
        CreateDocuments --> VectorStoreFactory["VectorStoreFactory"]
        VectorStoreFactory --> VectorStore["Selected Vector Store"]
    end
    
    subgraph "Vector Store Types"
        VectorStoreFactory --> Redis["Redis"]
        VectorStoreFactory --> Pinecone["Pinecone"]
        VectorStoreFactory --> Chroma["ChromaDB"]
        VectorStoreFactory --> Weaviate["Weaviate"]
        VectorStoreFactory --> Qdrant["Qdrant"]
        VectorStoreFactory --> LanceDB["LanceDB"]
    end
    
    subgraph "Resource Querying"
        Agent["Agent"] --> QueryResourceTool["QueryResourceTool"]
        QueryResourceTool --> VectorStoreFactory
        VectorStoreFactory --> |"Search Vectors"| VectorStore
        VectorStore --> |"Return Relevant Content"| QueryResourceTool
        QueryResourceTool --> |"Results"| Agent
    end
```

### Summarization Process

1. When a resource is uploaded, a background task `summarize_resource` is triggered
2. The task creates documents from the resource using LlamaIndex
3. The documents are added to a vector store for semantic searching
4. A summary of the resource content is generated and stored

### Querying Resources

Agents can query resources using the QueryResourceTool, which:
1. Takes a natural language query from the agent
2. Converts the query to a vector using the same model as summarization
3. Searches the vector store for semantically similar content
4. Returns the relevant information to the agent

### Supported Vector Stores

| Vector Store | Description |
|--------------|-------------|
| Redis | In-memory database with vector search capabilities |
| Pinecone | Managed vector database optimized for similarity search |
| Chroma | Open-source embedding database |
| Weaviate | Vector search engine and knowledge graph |
| Qdrant | Vector similarity search engine |
| LanceDB | Serverless vector database |

Sources: [superagi/worker.py:75-104](), [superagi/resource_manager/resource_summary.py](), [superagi/tools/resource/query_resource.py](), [superagi/types/vector_store_types.py]()

## Integration with Agents

Resources are tightly integrated with agents and agent executions:

```mermaid
graph TD
    subgraph "Agent Resource Lifecycle"
        AgentCreation["Agent Creation"] --> |"Upload Input Resources"| ResourceUpload["Resource Upload"]
        ResourceUpload --> |"Summarize Resources"| ResourceSummarization["Resource Summarization"]
        ResourceSummarization --> |"Store Vectors"| VectorStorage["Vector Storage"]
        
        AgentExecution["Agent Execution"] --> |"Query Resources"| ResourceQuery["Resource Query"]
        ResourceQuery --> VectorStorage
        
        AgentExecution --> |"Generate Output"| ResourceCreation["Resource Creation"]
    end
    
    subgraph "Resource Types"
        ResourceUpload --> InputResources["Input Resources (channel=INPUT)"]
        ResourceCreation --> OutputResources["Output Resources (channel=OUTPUT)"]
    end
    
    subgraph "Resource Metadata"
        Resource["Resource"] --> agent_id["agent_id"]
        Resource --> agent_execution_id["agent_execution_id"]
        Resource --> channel["channel (INPUT/OUTPUT)"]
    end
```

### Agent Resource Relationships

1. **Input Resources**:
   - Uploaded by users for agents to use
   - Processed and vectorized for semantic search
   - Associated with agents through the `agent_id` field

2. **Output Resources**:
   - Generated by agents during execution
   - Stored with references to both agent and execution
   - Associated with both agent and execution through `agent_id` and `agent_execution_id` fields

3. **Resource Summary**:
   - Agents maintain a summary of all their input resources
   - This summary is stored in the agent configuration as `resource_summary`
   - Used to provide context to the agent about available resources

Sources: [superagi/helper/resource_helper.py:14-80](), [superagi/resource_manager/resource_summary.py:50-89]()

## Query Resource Tool

Agents can use the QueryResourceTool to search and retrieve information from resources:

```mermaid
classDiagram
    class BaseTool {
        +name: str
        +description: str
        +args_schema: Type[BaseModel]
        +_execute()
    }
    
    class QueryResourceTool {
        +name: str = "QueryResource"
        +description: str
        +args_schema: Type[BaseModel] = QueryResource
        +agent_id: int
        +llm: Optional[BaseLlm]
        +_execute(query: str)
    }
    
    class QueryResource {
        +query: str
    }
    
    BaseTool <|-- QueryResourceTool
    QueryResourceTool --> QueryResource
```

### Usage Flow

1. Agent constructs a query about information it needs from resources
2. Query is passed to the QueryResourceTool
3. The tool:
   - Connects to the configured vector store
   - Applies filters to limit results to the agent's resources
   - Executes the semantic search
   - Returns relevant information to the agent

### Configuration

The QueryResourceTool is configured with:
- `RESOURCE_VECTOR_STORE`: Type of vector store to use (Redis, Pinecone, etc.)
- `RESOURCE_VECTOR_STORE_INDEX_NAME`: Name of the index in the vector store

Sources: [superagi/tools/resource/query_resource.py](), [superagi/tools/resource/resource_toolkit.py]()

## Summary

The Resource Management system in SuperAGI provides a comprehensive framework for handling files and data within the agent ecosystem. It supports:

1. Multiple storage backends (local filesystem and Amazon S3)
2. Resource uploading, downloading, and listing
3. Automatic resource summarization and vectorization
4. Vector-based semantic search for intelligent resource querying
5. Integration with agents and agent executions
6. Tool-based querying for agents to access resource information

This system enables agents to efficiently work with various resources and retrieve relevant information when needed for their tasks.

---

# Page: File Storage

# File Storage

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [migrations/versions/c02f3d759bf3_add_summary_to_resource.py](migrations/versions/c02f3d759bf3_add_summary_to_resource.py)
- [superagi/controllers/resources.py](superagi/controllers/resources.py)
- [superagi/helper/resource_helper.py](superagi/helper/resource_helper.py)
- [superagi/models/resource.py](superagi/models/resource.py)
- [superagi/resource_manager/file_manager.py](superagi/resource_manager/file_manager.py)
- [superagi/resource_manager/resource_summary.py](superagi/resource_manager/resource_summary.py)
- [superagi/tools/resource/__init__.py](superagi/tools/resource/__init__.py)
- [superagi/tools/resource/query_resource.py](superagi/tools/resource/query_resource.py)
- [superagi/tools/resource/resource_toolkit.py](superagi/tools/resource/resource_toolkit.py)
- [superagi/types/storage_types.py](superagi/types/storage_types.py)
- [superagi/types/vector_store_types.py](superagi/types/vector_store_types.py)
- [superagi/worker.py](superagi/worker.py)
- [tests/unit_tests/helper/test_resource_helper.py](tests/unit_tests/helper/test_resource_helper.py)

</details>



The File Storage system in SuperAGI provides mechanisms for storing, retrieving, and managing files used by agents. SuperAGI supports both local file system storage and Amazon S3 cloud storage, allowing flexibility in deployment configurations. This document details how files are stored, accessed, and managed throughout the system.

For information about vector database integration used for storing and retrieving knowledge from these files, see [Vector Databases](#5.2).

## Storage Types

SuperAGI supports two primary storage types for managing resources:

```mermaid
graph TD
    A["Storage Types"] --> B["File System Storage"]
    A --> C["S3 Storage"]
    
    B --> D["Local disk storage"]
    B --> E["Path-based organization"]
    
    C --> F["Amazon S3 bucket storage"]
    C --> G["Cloud-based organization"]
    
    style A stroke-width:2px
    style B stroke-width:2px
    style C stroke-width:2px
```

Sources: [superagi/types/storage_types.py]()

### File System Storage

The default storage method is local file system storage, which stores files on the server's disk. This is suitable for local deployments or when all files should be kept on the server where SuperAGI is running.

Key characteristics:
- Files are organized in directories based on agent and execution IDs
- Root directories can be configured via environment variables
- Simple to set up with no additional dependencies

### Amazon S3 Storage

For cloud deployments or cases where more scalable storage is needed, SuperAGI supports storing files in Amazon S3 buckets.

Key characteristics:
- Requires AWS credentials configuration
- Scales well for larger deployments
- Provides redundancy and availability guarantees
- Suitable for distributed deployments

### Configuration

Storage type is configured through the `STORAGE_TYPE` environment variable, which accepts either `FILE` or `S3`:

```
STORAGE_TYPE=FILE  # For local file system storage
STORAGE_TYPE=S3    # For Amazon S3 storage
```

When using S3 storage, additional configuration is required:
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `BUCKET_NAME`: S3 bucket name to store files

Sources: [superagi/types/storage_types.py](), [superagi/controllers/resources.py:64-65]()

## Resource Model

Files in SuperAGI are represented by the `Resource` model, which contains metadata about each stored file:

```mermaid
classDiagram
    class Resource {
        +Integer id
        +String name
        +String storage_type
        +String path
        +Integer size
        +String type
        +String channel
        +Integer agent_id
        +Integer agent_execution_id
        +Text summary
        +validate_resource_type()
        +find_by_run_ids()
    }
```

Key attributes:
- `name`: The file name 
- `storage_type`: Storage type (`FILE` or `S3`)
- `path`: Path to the file within the storage system
- `size`: File size in bytes
- `type`: MIME type of the file (e.g., "application/pdf")
- `channel`: Whether the file is an input (`INPUT`) or output (`OUTPUT`)
- `agent_id`: ID of the agent associated with the resource
- `agent_execution_id`: ID of the specific agent execution that created or used the resource
- `summary`: Optional text summary of the file content (generated through LLM processing)

Sources: [superagi/models/resource.py]()

## File Path Management

SuperAGI uses a structured approach to managing file paths, with separate directories for input and output files:

```mermaid
graph TD
    A["File Path Management"] --> B["Input Directory"]
    A --> C["Output Directory"]
    
    B --> D["Resources uploaded by users"]
    C --> E["Resources generated by agents"]
    
    B --> F["RESOURCES_INPUT_ROOT_DIR"]
    C --> G["RESOURCES_OUTPUT_ROOT_DIR"]
    
    F --> H["Default: current working directory"]
    G --> I["Default: current working directory"]
    
    F --> J["Can include {agent_id} placeholder"]
    G --> K["Can include {agent_id} and {agent_execution_id} placeholders"]
    
    style A stroke-width:2px
```

### Directory Configuration

The root directories for file storage are configured through environment variables:
- `RESOURCES_INPUT_ROOT_DIR`: Root directory for files uploaded by users
- `RESOURCES_OUTPUT_ROOT_DIR`: Root directory for files generated by agents

If these are not specified, the current working directory is used.

### Path Templates

Path templates can include placeholders to organize files by agent and execution:
- `{agent_id}`: Replaced with `AgentName_ID` (e.g., "TestAgent_1")
- `{agent_execution_id}`: Replaced with `ExecutionName_ID` (e.g., "TestExecution_1")

For example, with `RESOURCES_OUTPUT_ROOT_DIR=/data/{agent_id}/{agent_execution_id}/` and an agent named "ResearchBot" with ID 42 and execution ID 123, a file path might resolve to `/data/ResearchBot_42/Execution_123/output.txt`.

Sources: [superagi/helper/resource_helper.py:82-91](), [superagi/helper/resource_helper.py:114-125]()

## Resource Operations

SuperAGI provides several operations for managing resources:

```mermaid
graph TD
    A["Resource Operations"] --> B["Upload Resources"]
    A --> C["Download Resources"]
    A --> D["List Resources"]
    A --> E["Write Resources"]
    A --> F["Read Resources"]
    
    B --> B1["API: POST /add/{agent_id}"]
    C --> C1["API: GET /get/{resource_id}"]
    D --> D1["API: GET /get/all/{agent_id}"]
    
    E --> E1["FileManager.write_file()"]
    E --> E2["FileManager.write_binary_file()"]
    E --> E3["FileManager.write_csv_file()"]
    
    F --> F1["FileManager.read_file()"]
    
    style A stroke-width:2px
```

### Uploading Resources

Files can be uploaded via the REST API endpoint `/add/{agent_id}`. The process includes:
1. Validating the agent exists
2. Checking if the file type is supported (PDF, DOCX, PPTX, CSV, TXT, EPUB)
3. Determining storage location based on storage type
4. Storing the file and creating a Resource record
5. Triggering background summarization

```python
POST /add/{agent_id}
Parameters:
  - agent_id (path): ID of the agent
  - file (form): Uploaded file
  - name (form): Name of the resource
  - size (form): Size of the resource
  - type (form): Type of the resource
```

Sources: [superagi/controllers/resources.py:32-97]()

### Downloading Resources

Files can be downloaded via the REST API endpoint `/get/{resource_id}`:
1. Validates the resource exists
2. Checks if the user has permission to access the resource
3. Retrieves the file from the storage system
4. Streams the file content as a download response

```python
GET /get/{resource_id}
Parameters:
  - resource_id (path): ID of the resource to download
```

Sources: [superagi/controllers/resources.py:118-174]()

### Listing Resources

All resources for an agent can be listed via the REST API endpoint `/get/all/{agent_id}`:

```python
GET /get/all/{agent_id}
Parameters:
  - agent_id (path): ID of the agent
```

Sources: [superagi/controllers/resources.py:100-115]()

### File Operations

The `FileManager` class provides methods for agents to read and write files:

| Method | Description |
|--------|-------------|
| `write_file` | Writes text content to a file |
| `write_binary_file` | Writes binary data (e.g., images) to a file |
| `write_csv_file` | Writes CSV data to a file |
| `read_file` | Reads content from a file |
| `get_files` | Lists all files in the agent's directory |

For each operation, the system:
1. Resolves the appropriate file path
2. Performs the file operation on the local file system
3. If using S3 storage, also synchronizes the file to the S3 bucket
4. For write operations, creates or updates the Resource record

Sources: [superagi/resource_manager/file_manager.py]()

## Resource Summarization and Vectorization

When resources are uploaded, SuperAGI processes them in the background to enable semantic search and retrieval:

```mermaid
sequenceDiagram
    participant RC as "ResourceController"
    participant W as "Worker"
    participant RS as "ResourceSummarizer"
    participant RM as "ResourceManager"
    participant VS as "VectorStore"
    participant DB as "Database"
    
    RC->>W: summarize_resource.delay(agent_id, resource_id)
    W->>RM: create_llama_document(file_path)
    W->>RS: add_to_vector_store_and_create_summary(resource_id, documents)
    RS->>RM: save_document_to_vector_store(documents)
    RM->>VS: Store document vectors
    RS->>DB: Store resource summary
```

The process involves:
1. Extracting text content from the uploaded file
2. Processing the content into chunks for vectorization
3. Creating vector embeddings of the content chunks
4. Storing the embeddings in the configured vector store
5. Generating a summary of the resource content
6. Storing the summary in the Resource record

This enables agents to:
- Search through document content semantically
- Retrieve relevant information from stored files
- Use the QueryResourceTool to access information in documents

Sources: [superagi/worker.py:75-104](), [superagi/resource_manager/resource_summary.py]()

## Integration with Agents

Agents can interact with stored resources in several ways:

```mermaid
graph TD
    A["Agent Resource Access"] --> B["Reading Files"]
    A --> C["Writing Files"]
    A --> D["Querying Content"]
    
    B --> B1["FileManager.read_file()"]
    C --> C1["FileManager.write_file()"]
    D --> D1["QueryResourceTool"]
    
    D1 --> E["Vector Search"]
    E --> F["Retrieves relevant content"]
    
    B1 --> G["ResourceHelper.get_agent_read_resource_path()"]
    C1 --> H["ResourceHelper.get_agent_write_resource_path()"]
    
    style A stroke-width:2px
```

### File Access

Agents can read existing files and write new files using the `FileManager`:
- Input files are searched first in the input directory, then in the output directory
- Output files are always written to the output directory
- Path resolution considers agent and execution context

### Resource Querying

The `QueryResourceTool` lets agents semantically search through resources:
1. Agent submits a natural language query
2. System searches the vector store for relevant content
3. Relevant passages are retrieved and returned to the agent

This tool is particularly useful for tasks that require extracting information from large documents or multiple files.

Sources: [superagi/tools/resource/query_resource.py]()

## Storage Implementation Details

### File System Implementation

When using file system storage:
1. Files are stored at the computed path on disk
2. Directory structure is created if it doesn't exist
3. File operations use standard Python file I/O

### S3 Implementation

When using S3 storage:
1. Files are temporarily stored on the local file system
2. Files are then uploaded to the configured S3 bucket
3. File paths in S3 include a "resources" prefix
4. Downloads retrieve content from S3 and stream it to the client

For S3 storage, the system also maintains a local copy of files for processing purposes, such as vectorization.

Sources: [superagi/controllers/resources.py:78-85](), [superagi/resource_manager/file_manager.py:35-47]()

## Summary

The SuperAGI File Storage system provides a flexible framework for managing resources across different storage backends. It handles file operations, path resolution, and integrates with the agent system to enable both input/output file handling and semantic search capabilities.

Key benefits:
- Support for both local and cloud storage
- Structured organization of files by agent and execution
- Integration with vector stores for semantic search
- Background processing for extracting and summarizing content
- Comprehensive API for resource management

This system forms the foundation for agent-based document processing and information extraction capabilities in SuperAGI.

---

# Page: Vector Databases

# Vector Databases

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/ISSUE_TEMPLATE/1.BUG_REPORT.yml](.github/ISSUE_TEMPLATE/1.BUG_REPORT.yml)
- [.github/workflows/codeql.yml](.github/workflows/codeql.yml)
- [superagi/controllers/vector_db_indices.py](superagi/controllers/vector_db_indices.py)
- [superagi/controllers/vector_dbs.py](superagi/controllers/vector_dbs.py)
- [superagi/models/vector_db_indices.py](superagi/models/vector_db_indices.py)
- [superagi/tools/knowledge_search/knowledge_search.py](superagi/tools/knowledge_search/knowledge_search.py)
- [superagi/vector_embeddings/vector_embedding_factory.py](superagi/vector_embeddings/vector_embedding_factory.py)
- [superagi/vector_embeddings/weaviate.py](superagi/vector_embeddings/weaviate.py)
- [superagi/vector_store/qdrant.py](superagi/vector_store/qdrant.py)
- [superagi/vector_store/vector_factory.py](superagi/vector_store/vector_factory.py)
- [superagi/vector_store/weaviate.py](superagi/vector_store/weaviate.py)
- [tests/integration_tests/vector_embeddings/test_weaviate.py](tests/integration_tests/vector_embeddings/test_weaviate.py)
- [tests/integration_tests/vector_store/test_qdrant.py](tests/integration_tests/vector_store/test_qdrant.py)
- [tests/integration_tests/vector_store/test_weaviate.py](tests/integration_tests/vector_store/test_weaviate.py)
- [tests/unit_tests/vector_store/__init__.py](tests/unit_tests/vector_store/__init__.py)
- [tests/unit_tests/vector_store/test_vector_factory.py](tests/unit_tests/vector_store/test_vector_factory.py)

</details>



## Purpose and Scope

This document covers the vector database integration within SuperAGI, explaining how vector databases are configured, connected, and utilized within the system. Vector databases are essential for efficient storage and retrieval of embeddings, which enable semantic search capabilities in agents. This page focuses on the core architecture, supported vector database providers, and integration with the wider SuperAGI ecosystem.

For information about general resource management, see [Resource Management](#5). For specific details about file storage options, see [File Storage](#5.1).

## Vector Database Architecture

SuperAGI implements an abstraction layer for vector databases that allows the system to work with multiple vector database providers while maintaining a consistent interface. The architecture consists of several core components:

```mermaid
graph TD
    subgraph "Application Layer"
        KnowledgeSearch["Knowledge Search Tool"]
        VectorDBsController["Vector DBs Controller"]
        VectorDBIndicesController["Vector DB Indices Controller"]
    end

    subgraph "Core Vector DB System"
        VectorFactory["VectorFactory"]
        VectorStore["VectorStore (Base Class)"]
        
        VectorFactory --> VectorStore
        VectorStore --> Pinecone["Pinecone Implementation"]
        VectorStore --> Weaviate["Weaviate Implementation"]
        VectorStore --> Qdrant["Qdrant Implementation"]
        VectorStore --> Redis["Redis Implementation"]
    end

    subgraph "Data Layer"
        VectordbsModel["Vectordbs Model"]
        VectordbIndicesModel["VectordbIndices Model"]
        VectordbConfigsModel["VectordbConfigs Model"]
    end

    subgraph "External Services"
        PineconeDB[("Pinecone DB")]
        WeaviateDB[("Weaviate DB")]
        QdrantDB[("Qdrant DB")]
        RedisDB[("Redis DB")]
    end

    KnowledgeSearch --> VectorFactory
    VectorDBsController --> VectorFactory
    VectorDBIndicesController --> VectordbIndicesModel
    
    VectorFactory --> VectordbsModel
    VectorFactory --> VectordbConfigsModel
    
    Pinecone --> PineconeDB
    Weaviate --> WeaviateDB
    Qdrant --> QdrantDB
    Redis --> RedisDB
```

Vector Database System Architecture Diagram

Sources:
- [superagi/vector_store/vector_factory.py:15-111]()
- [superagi/controllers/vector_dbs.py:1-149]()
- [superagi/controllers/vector_db_indices.py:1-52]()

## Vector Store Base Class and Implementations

SuperAGI uses a common interface defined by the `VectorStore` base class that all specific vector database implementations must inherit from. This ensures consistent behavior regardless of the underlying vector database provider.

```mermaid
classDiagram
    class VectorStore {
        <<abstract>>
        +add_texts(texts, metadatas) List[str]
        +get_matching_text(query, top_k, metadata) Dict
        +get_index_stats() Dict
        +add_embeddings_to_vector_db(embeddings) None
        +delete_embeddings_from_vector_db(ids) None
    }
    
    VectorStore <|-- Weaviate
    VectorStore <|-- Qdrant
    VectorStore <|-- Pinecone
    VectorStore <|-- Redis
    
    class Weaviate {
        -client
        -embedding_model
        -class_name
        -text_field
        +add_texts(texts, metadatas)
        +get_matching_text(query, top_k, metadata)
        +get_index_stats()
        +add_embeddings_to_vector_db(embeddings)
        +delete_embeddings_from_vector_db(ids)
        -_get_metadata_fields()
        -_build_documents()
        -_get_search_res()
    }
    
    class Qdrant {
        -client
        -embedding_model
        -collection_name
        -text_field_payload_key
        -metadata_payload_key
        +add_texts(texts, metadatas)
        +get_matching_text(query, top_k, metadata)
        +get_index_stats()
        +add_embeddings_to_vector_db(embeddings)
        +delete_embeddings_from_vector_db(ids)
        -__get_embeddings(texts)
        -__build_payloads(texts, metadatas)
        -__build_documents(results)
        +create_collection(client, collection_name, size)
    }
```

Vector Store Class Hierarchy Diagram

Sources:
- [superagi/vector_store/weaviate.py:43-147]()
- [superagi/vector_store/qdrant.py:31-288]()

### Common Vector Store Operations

All vector database implementations support these key operations:

1. **Adding Texts**: Converting text to embeddings and storing them in the vector database
2. **Querying Similar Texts**: Finding texts that are semantically similar to a query
3. **Getting Index Statistics**: Retrieving metadata about the vector database index
4. **Direct Embedding Management**: Adding or deleting embeddings directly

### Weaviate Implementation

The Weaviate implementation allows SuperAGI to connect to a Weaviate vector database. It handles:

- Client creation and management
- Text to embedding conversion
- Querying for similar texts
- Metadata filtering

```python
# Key operations in the Weaviate class
def add_texts(self, texts, metadatas=None, **kwargs):
    # Convert texts to embeddings and add them to the vector database
    
def get_matching_text(self, query, top_k=5, metadata=None, **kwargs):
    # Search for texts similar to the query
    
def get_index_stats(self):
    # Get statistics about the vector database index
    
def add_embeddings_to_vector_db(self, embeddings):
    # Add pre-computed embeddings to the vector database
    
def delete_embeddings_from_vector_db(self, ids):
    # Delete embeddings from the vector database
```

Sources:
- [superagi/vector_store/weaviate.py:53-126]()

### Qdrant Implementation

The Qdrant implementation provides similar functionality but for Qdrant vector database:

- Client creation and management
- Batch processing for efficiency
- Collection creation and management
- Payload management for metadata

```python
# Key operations in the Qdrant class
def add_texts(self, input_texts, metadata_list=None, id_list=None, batch_limit=64):
    # Add texts to the vector database with batching support
    
def get_matching_text(self, text=None, embedding=None, k=4, metadata=None):
    # Search for similar texts with optional filter criteria
    
def get_index_stats(self):
    # Get collection statistics
    
@classmethod
def create_collection(cls, client, collection_name, size):
    # Create a new collection in Qdrant
```

Sources:
- [superagi/vector_store/qdrant.py:59-280]()

## Vector Factory

The `VectorFactory` class serves as a factory for creating vector database instances based on configuration or explicit parameters. It abstracts away the complexity of creating specific vector database implementations.

```mermaid
sequenceDiagram
    participant App as "Application"
    participant Factory as "VectorFactory"
    participant Config as "Configuration"
    participant Store as "VectorStore Implementation"
    participant DB as "External Vector Database"
    
    App->>Factory: get_vector_storage(vector_store, index_name, embedding_model)
    Factory->>Config: get_config(DB_CREDENTIALS)
    Config-->>Factory: credentials
    
    alt vector_store is PINECONE
        Factory->>Store: Create Pinecone instance
    else vector_store is WEAVIATE
        Factory->>Store: Create Weaviate instance
    else vector_store is QDRANT
        Factory->>Store: Create Qdrant instance
    else vector_store is REDIS
        Factory->>Store: Create Redis instance
    end
    
    Store->>DB: Connect and verify
    DB-->>Store: Connection established
    Store-->>Factory: VectorStore instance
    Factory-->>App: VectorStore instance
```

Vector Store Initialization Sequence Diagram

Sources:
- [superagi/vector_store/vector_factory.py:15-111]()

The `VectorFactory` provides two main methods:

1. **get_vector_storage**: Creates a vector store based on configuration from environment variables
2. **build_vector_storage**: Creates a vector store using explicitly provided credentials

This factory pattern allows other components to create vector stores without needing to know the specific implementation details of each type.

## Data Models

SuperAGI uses several database models to manage vector database configurations and indices:

### Vectordbs

This model represents a connection to a vector database service:

- **id**: Unique identifier for the vector database connection
- **name**: User-friendly name for the vector database
- **db_type**: Type of vector database (Pinecone, Weaviate, Qdrant, etc.)
- **organisation_id**: Organization that owns this vector database connection

### VectordbIndices

This model represents an index or collection within a vector database:

- **id**: Unique identifier for the index
- **name**: Name of the index/collection
- **vector_db_id**: Reference to the parent vector database
- **dimensions**: Number of dimensions in the vector embeddings
- **state**: State of the index (None, Custom, Marketplace)

```mermaid
erDiagram
    Vectordbs ||--o{ VectordbIndices : "has many"
    Vectordbs ||--|| VectordbConfigs : "has one"
    Knowledges }o--|| VectordbIndices : "uses"
    
    Vectordbs {
        int id
        string name
        string db_type
        int organisation_id
    }
    
    VectordbIndices {
        int id
        string name
        int vector_db_id
        int dimensions
        string state
    }
    
    VectordbConfigs {
        int vector_db_id
        string api_key
        string environment
        string url
        int port
    }
    
    Knowledges {
        int id
        string name
        int vector_db_index_id
    }
```

Vector Database Data Model Diagram

Sources:
- [superagi/models/vector_db_indices.py:1-59]()
- [superagi/controllers/vector_dbs.py:1-149]()

## API Endpoints

SuperAGI provides API endpoints for managing vector databases and their indices.

### Vector Database Controller

Endpoints for managing vector databases:

| Endpoint | Method | Description |
|----------|--------|-------------|
| /get/list | GET | Get list of vector databases |
| /marketplace/list | GET | Get list of marketplace vector databases |
| /user/list | GET | Get user's connected vector databases |
| /db/details/{vector_db_id} | GET | Get details of a specific vector database |
| /delete/{vector_db_id} | POST | Delete a vector database |
| /connect/pinecone | POST | Connect to a Pinecone vector database |
| /connect/qdrant | POST | Connect to a Qdrant vector database |
| /connect/weaviate | POST | Connect to a Weaviate vector database |
| /update/vector_db/{vector_db_id} | PUT | Update a vector database |

### Vector Database Indices Controller

Endpoints for managing vector database indices:

| Endpoint | Method | Description |
|----------|--------|-------------|
| /marketplace/valid_indices/{knowledge_name} | GET | Get valid indices for a marketplace knowledge |
| /user/valid_indices | GET | Get valid indices for a user |

Sources:
- [superagi/controllers/vector_dbs.py:14-147]()
- [superagi/controllers/vector_db_indices.py:10-52]()

## Integration with Knowledge Search

Vector databases are a critical component of the Knowledge Search functionality in SuperAGI. The Knowledge Search tool uses vector databases to find semantically similar content.

```mermaid
sequenceDiagram
    participant Agent
    participant KnowledgeSearchTool
    participant Session
    participant VectorFactory
    participant VectorStore
    participant ExternalDB

    Agent->>KnowledgeSearchTool: execute(query)
    KnowledgeSearchTool->>Session: Get knowledge configuration
    Session-->>KnowledgeSearchTool: Knowledge config with vector DB info
    
    KnowledgeSearchTool->>VectorFactory: build_vector_storage(db_type, index_name, embedding_model, credentials)
    VectorFactory->>VectorStore: Create appropriate VectorStore
    VectorStore->>ExternalDB: Connect to external DB
    ExternalDB-->>VectorStore: Connection established
    VectorStore-->>VectorFactory: Vector store instance
    VectorFactory-->>KnowledgeSearchTool: Vector store instance
    
    KnowledgeSearchTool->>VectorStore: get_matching_text(query, metadata=filters)
    VectorStore->>ExternalDB: Perform semantic search
    ExternalDB-->>VectorStore: Search results
    VectorStore-->>KnowledgeSearchTool: Formatted results
    KnowledgeSearchTool-->>Agent: "Result: {search_results}"
```

Knowledge Search Flow Using Vector Databases

Sources:
- [superagi/tools/knowledge_search/knowledge_search.py:24-59]()

## Vector Embeddings

SuperAGI includes a system for managing vector embeddings for different database types. The `VectorEmbeddingFactory` creates the appropriate embedding representation for each vector database.

```mermaid
graph TD
    subgraph "Vector Embeddings System"
        VectorEmbeddingFactory["VectorEmbeddingFactory"]
        VectorEmbeddingFactory --> PineconeEmbed["Pinecone Embeddings"]
        VectorEmbeddingFactory --> WeaviateEmbed["Weaviate Embeddings"]
        VectorEmbeddingFactory --> QdrantEmbed["Qdrant Embeddings"]
    end
    
    subgraph "Text Processing"
        TextChunking["Text Chunking"]
        TextChunking --> EmbeddingModel["Embedding Model (e.g., OpenAI)"]
        EmbeddingModel --> Embeddings["Raw Embeddings"]
    end
    
    Embeddings --> VectorEmbeddingFactory
```

Vector Embeddings System Diagram

Sources:
- [superagi/vector_embeddings/vector_embedding_factory.py:1-47]()
- [superagi/vector_embeddings/weaviate.py:1-15]()

## Vector Database Connection Process

The process for connecting to a vector database in SuperAGI involves several steps:

1. **User submits connection details** via API endpoints
2. **System validates the connection** by attempting to connect to the database
3. **Connection information is stored** in the database
4. **Indices are created or connected** to complete the setup

```mermaid
sequenceDiagram
    participant User
    participant API as "Vector DBs Controller"
    participant VectorFactory
    participant Database as "SuperAGI Database"
    participant ExternalDB as "External Vector DB"
    
    User->>API: POST /connect/{provider} with credentials
    API->>VectorFactory: build_vector_storage(provider, collection, credentials)
    VectorFactory->>ExternalDB: Attempt connection
    ExternalDB-->>VectorFactory: Connection response
    VectorFactory->>ExternalDB: get_index_stats()
    ExternalDB-->>VectorFactory: Index statistics
    VectorFactory-->>API: Connection status and stats
    
    alt Connection successful
        API->>Database: Store DB connection (Vectordbs)
        API->>Database: Store credentials (VectordbConfigs)
        API->>Database: Store indices (VectordbIndices)
        Database-->>API: Success
        API-->>User: Connection successful
    else Connection failed
        API-->>User: Connection failed
    end
```

Vector Database Connection Process Diagram

Sources:
- [superagi/controllers/vector_dbs.py:64-122]()

## Conclusion

Vector databases are a critical component of SuperAGI's knowledge management system, providing efficient storage and retrieval of semantic embeddings. The system's modular architecture allows for easy integration of different vector database providers while maintaining a consistent interface for the rest of the application.

The abstraction layers provided by the `VectorStore` base class and `VectorFactory` make it possible to swap vector database implementations without affecting other parts of the system, providing flexibility and future-proofing as new vector database technologies emerge.

---

# Page: LLM Integration

# LLM Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile-gpu](Dockerfile-gpu)
- [README.MD](README.MD)
- [config_template.yaml](config_template.yaml)
- [docker-compose-gpu.yml](docker-compose-gpu.yml)
- [gui/pages/Content/Models/AddModel.js](gui/pages/Content/Models/AddModel.js)
- [gui/pages/Content/Models/MarketModels.js](gui/pages/Content/Models/MarketModels.js)
- [gui/pages/Content/Models/ModelForm.js](gui/pages/Content/Models/ModelForm.js)
- [gui/pages/Content/Models/ModelTemplate.js](gui/pages/Content/Models/ModelTemplate.js)
- [gui/pages/Content/Models/Models.js](gui/pages/Content/Models/Models.js)
- [requirements.txt](requirements.txt)
- [superagi/controllers/models_controller.py](superagi/controllers/models_controller.py)
- [superagi/controllers/types/models_types.py](superagi/controllers/types/models_types.py)
- [superagi/helper/llm_loader.py](superagi/helper/llm_loader.py)
- [superagi/llms/llm_model_factory.py](superagi/llms/llm_model_factory.py)
- [superagi/llms/local_llm.py](superagi/llms/local_llm.py)
- [superagi/models/models.py](superagi/models/models.py)
- [superagi/models/models_config.py](superagi/models/models_config.py)
- [superagi/types/model_source_types.py](superagi/types/model_source_types.py)
- [tests/unit_tests/controllers/test_models_controller.py](tests/unit_tests/controllers/test_models_controller.py)
- [tests/unit_tests/tools/duck_duck_go/test_duckduckgo_results.py](tests/unit_tests/tools/duck_duck_go/test_duckduckgo_results.py)

</details>



This page documents the Language Model integration system in SuperAGI. It details how various LLM providers are integrated into the platform, how models are configured, and how the system interacts with them. For information about model management through the user interface, see [Model Management](#6.2).

## Overview

SuperAGI provides a flexible interface to work with various Language Model providers. The system supports integration with multiple LLM providers including OpenAI, Google Palm, Replicate, Hugging Face, and local LLMs. This modular design allows users to switch between different providers seamlessly while maintaining a consistent interface for agents to interact with language models.

```mermaid
flowchart TB
    subgraph "SuperAGI"
        Agent["Agent Executor"]
        ModelFactory["LLM Model Factory"]
        ModelConfig["Models Config"]
        
        Agent -->|"uses"| ModelFactory
        ModelFactory -->|"reads config"| ModelConfig
        
        subgraph "LLM Providers"
            OpenAI["OpenAI Provider"]
            GooglePalm["Google Palm Provider"]
            Replicate["Replicate Provider"]
            HuggingFace["Hugging Face Provider"]
            LocalLLM["Local LLM Provider"]
        end
        
        ModelFactory -->|"instantiates"| OpenAI
        ModelFactory -->|"instantiates"| GooglePalm
        ModelFactory -->|"instantiates"| Replicate
        ModelFactory -->|"instantiates"| HuggingFace
        ModelFactory -->|"instantiates"| LocalLLM
    end
    
    subgraph "External Services"
        OpenAIAPI["OpenAI API"]
        GooglePalmAPI["Google Palm API"]
        ReplicateAPI["Replicate API"]
        HuggingFaceAPI["Hugging Face API"]
        GPU["Local GPU"]
    end
    
    OpenAI -->|"calls"| OpenAIAPI
    GooglePalm -->|"calls"| GooglePalmAPI
    Replicate -->|"calls"| ReplicateAPI
    HuggingFace -->|"calls"| HuggingFaceAPI
    LocalLLM -->|"uses"| GPU
```

Sources: [superagi/llms/llm_model_factory.py:1-55](), [superagi/types/model_source_types.py:1-33]()

## System Architecture

The LLM integration architecture in SuperAGI consists of several key components:

```mermaid
classDiagram
    class BaseLlm {
        <<interface>>
        +chat_completion(messages, max_tokens)
        +get_source()
        +get_api_key()
        +get_model()
    }
    
    class ModelsConfig {
        +id: Integer
        +provider: String
        +api_key: String
        +org_id: Integer
        +store_api_key()
        +fetch_api_key()
        +fetch_api_keys()
    }
    
    class Models {
        +id: Integer
        +model_name: String
        +description: String
        +end_point: String
        +model_provider_id: Integer
        +token_limit: Integer
        +type: String
        +version: String
        +org_id: Integer
        +context_length: Integer
        +store_model_details()
        +fetch_models()
    }
    
    class LLMModelFactory {
        +get_model()
        +build_model_with_api_key()
    }
    
    class OpenAi {
        +chat_completion()
        +get_models()
    }
    
    class GooglePalm {
        +chat_completion()
    }
    
    class Replicate {
        +chat_completion()
    }
    
    class HuggingFace {
        +chat_completion()
    }
    
    class LocalLLM {
        +chat_completion()
        +llm_model
        +llm_grammar
    }
    
    class LLMLoader {
        +model
        +grammar
    }
    
    BaseLlm <|-- OpenAi
    BaseLlm <|-- GooglePalm
    BaseLlm <|-- Replicate
    BaseLlm <|-- HuggingFace
    BaseLlm <|-- LocalLLM
    
    LLMModelFactory ..> BaseLlm: creates
    LLMModelFactory --> ModelsConfig: reads
    LLMModelFactory --> Models: reads
    
    LocalLLM --> LLMLoader: uses
```

Sources: [superagi/llms/llm_model_factory.py:1-55](), [superagi/models/models.py:1-238](), [superagi/models/models_config.py:1-164](), [superagi/llms/local_llm.py:1-96]()

### Core Components

1. **BaseLlm**: An interface that defines the contract for all LLM providers
2. **ModelsConfig**: Database model for storing provider configurations and API keys
3. **Models**: Database model for storing specific model details
4. **LLMModelFactory**: Factory class for instantiating appropriate LLM provider classes
5. **Provider Implementations**: Concrete implementations for each supported LLM provider (OpenAI, Google Palm, etc.)

## Model Configuration Management

SuperAGI stores model configurations and API keys in the database, allowing users to manage multiple providers and models.

### Database Schema

#### ModelsConfig Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| provider | String | Name of the LLM provider (e.g., "OpenAI", "Google Palm") |
| api_key | String | Encrypted API key for the provider |
| org_id | Integer | Organization ID that owns this configuration |

#### Models Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| model_name | String | Name of the model (e.g., "gpt-3.5-turbo") |
| description | String | Description of the model |
| end_point | String | Custom endpoint URL (for Hugging Face) |
| model_provider_id | Integer | Foreign key to ModelsConfig |
| token_limit | Integer | Maximum token limit for the model |
| type | String | Type of model (Custom/Marketplace) |
| version | String | Version information (for Replicate) |
| org_id | Integer | Organization ID that owns this model |
| context_length | Integer | Context length for Local LLM models |

Sources: [superagi/models/models_config.py:12-34](), [superagi/models/models.py:15-57]()

## API Key Management

SuperAGI securely stores API keys for different LLM providers. The keys are encrypted before storage and decrypted when needed for API calls.

```mermaid
sequenceDiagram
    participant User
    participant ModelsController
    participant ModelsConfig
    participant Database
    
    User->>ModelsController: Store API key (provider, key)
    ModelsController->>ModelsConfig: store_api_key(org_id, provider, key)
    ModelsConfig->>ModelsConfig: encrypt_data(key)
    ModelsConfig->>Database: Store encrypted key
    
    User->>ModelsController: Fetch API key (provider)
    ModelsController->>ModelsConfig: fetch_api_key(org_id, provider)
    ModelsConfig->>Database: Query API key
    Database->>ModelsConfig: Return encrypted key
    alt Not Local LLM
        ModelsConfig->>ModelsConfig: decrypt_data(key)
    end
    ModelsConfig->>ModelsController: Return key
    ModelsController->>User: API key information
```

Sources: [superagi/models/models_config.py:78-139](), [superagi/controllers/models_controller.py:37-61]()

## Adding and Managing Models

SuperAGI provides APIs to add new models, verify endpoints, and fetch existing models. These APIs are used by the frontend to provide a user-friendly interface for model management.

### Model Addition Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant ModelsController
    participant Models
    participant ModelsConfig
    
    User->>Frontend: Fill model details
    Frontend->>ModelsController: Verify endpoint
    ModelsController->>Frontend: Endpoint validation result
    
    User->>Frontend: Submit model
    Frontend->>ModelsController: Store model
    ModelsController->>Models: store_model_details()
    Models->>ModelsConfig: Get provider info
    Models->>Models: Validate model data
    Models->>Database: Store model
    Database->>Models: Return model ID
    Models->>ModelsController: Success response
    ModelsController->>Frontend: Model addition result
    Frontend->>User: Display success/error
```

Sources: [superagi/controllers/models_controller.py:73-82](), [superagi/models/models.py:108-162](), [gui/pages/Content/Models/ModelForm.js:1-217]()

## Supported LLM Providers

SuperAGI supports the following LLM providers:

### 1. OpenAI

Integration with OpenAI API for models like GPT-3.5 and GPT-4. Supported with customizable parameters like temperature, max tokens, etc.

### 2. Google Palm

Integration with Google's PaLM models through the Google API.

### 3. Replicate

Support for deploying models through Replicate, which provides a variety of open-source models.

### 4. Hugging Face

Integration with Hugging Face's model serving endpoints, allowing access to thousands of open-source models.

### 5. Local LLM

Support for running LLMs locally using GPU acceleration. This is particularly useful for self-hosting models or working with models that require privacy.

The system automatically detects which provider to use based on the model name and configuration.

Sources: [superagi/llms/llm_model_factory.py:12-42](), [config_template.yaml:1-126]()

## Local LLM Support

SuperAGI includes support for running language models locally using the llama-cpp-python library. This allows users to run LLMs on their own hardware, which can be useful for privacy or when working with custom models.

```mermaid
flowchart TB
    subgraph "Local LLM Integration"
        LLMLoader["LLMLoader"]
        LocalLLM["LocalLLM Class"]
        LlamaModel["Llama Model"]
        LlamaGrammar["Llama Grammar"]
        
        LocalLLM -->|"initializes"| LLMLoader
        LLMLoader -->|"loads"| LlamaModel
        LLMLoader -->|"loads"| LlamaGrammar
        LocalLLM -->|"uses"| LlamaModel
        LocalLLM -->|"uses"| LlamaGrammar
    end
    
    subgraph "GPU Acceleration"
        CUDA["CUDA Libraries"]
        Docker["Docker with GPU Support"]
        
        LlamaModel -->|"uses"| CUDA
        Docker -->|"provides"| CUDA
    end
```

### Local LLM Configuration

To use local LLMs, SuperAGI provides a Docker configuration with GPU support. The key components include:

1. **LLMLoader**: Singleton class that loads the model and grammar
2. **LocalLLM**: Implementation of the BaseLlm interface for local models
3. **Docker GPU Configuration**: Setup for CUDA and GPU acceleration

Sources: [superagi/helper/llm_loader.py:1-39](), [superagi/llms/local_llm.py:1-96](), [docker-compose-gpu.yml:1-96](), [Dockerfile-gpu:1-45]()

### Using GPU Acceleration

For GPU-accelerated local LLMs, SuperAGI provides a specific Docker configuration:

```
docker compose -f docker-compose-gpu.yml up --build
```

This setup requires NVIDIA drivers and Docker with GPU support.

Sources: [README.MD:136-139](), [docker-compose-gpu.yml:16-22](), [docker-compose-gpu.yml:36-42]()

## Web Interface for Model Management

SuperAGI provides a web interface for managing LLM integrations. The interface allows users to:

1. Add API keys for different LLM providers
2. Add and configure models
3. Test models for compatibility
4. View model details

```mermaid
flowchart TB
    subgraph "Model Management UI"
        ModelsList["Models List"]
        AddModel["Add Model Form"]
        ModelTemplate["Model Template View"]
        MarketModels["Marketplace Models"]
        
        ModelsList -->|"Add New Model"| AddModel
        ModelsList -->|"View Model"| ModelTemplate
        ModelsList -->|"Browse Marketplace"| MarketModels
        MarketModels -->|"Install Model"| ModelTemplate
    end
    
    subgraph "Backend API"
        ModelsController["Models Controller"]
        APIHandlers["API Handlers"]
        
        AddModel -->|"Store Model"| ModelsController
        AddModel -->|"Verify Endpoint"| ModelsController
        ModelTemplate -->|"Fetch Model Details"| ModelsController
        MarketModels -->|"Fetch Marketplace Models"| ModelsController
        
        ModelsController -->|"Handle Requests"| APIHandlers
    end
```

Sources: [gui/pages/Content/Models/Models.js:1-37](), [gui/pages/Content/Models/ModelForm.js:1-217](), [gui/pages/Content/Models/MarketModels.js:1-93](), [gui/pages/Content/Models/ModelTemplate.js:1-61]()

## Environment Configuration

SuperAGI uses a configuration file to set up default LLM parameters. An example configuration for LLM integration from the config template:

```yaml
# OpenAI API Configuration
OPENAI_API_KEY: YOUR_OPEN_API_KEY
OPENAI_API_BASE: https://api.openai.com/v1

# For locally hosted LLMs
# OPENAI_API_BASE: "http://super__tgwui:5001/v1"

# Google Palm Configuration
PALM_API_KEY: YOUR_PALM_API_KEY

# Replicate Configuration
REPLICATE_API_TOKEN: YOUR_REPLICATE_API_TOKEN

# Hugging Face Configuration
HUGGING_API_TOKEN: YOUR_HUGGING_FACE_API_TOKEN

# Model Configuration
MODEL_NAME: "gpt-3.5-turbo-0301"
RESOURCES_SUMMARY_MODEL_NAME: "gpt-3.5-turbo"
MAX_TOOL_TOKEN_LIMIT: 800
MAX_MODEL_TOKEN_LIMIT: 4032

# GPU Layers for Local LLM
GPU_LAYERS: GPU_LAYERS_THAT_YOU_WANT_TO_OFFLOAD
```

Sources: [config_template.yaml:2-125]()

## Integration with Agent System

Language models are a core component of SuperAGI's agent system. The agents use LLMs to:

1. Process and understand tasks
2. Generate responses
3. Make decisions
4. Use tools

The LLM integration provides a consistent interface for agents to interact with different language model providers, allowing for flexibility and customization.

```mermaid
flowchart TB
    subgraph "Agent System"
        AgentExecutor["Agent Executor"]
        PromptBuilder["Prompt Builder"]
        OutputParser["Output Parser"]
        
        AgentExecutor -->|"builds prompts"| PromptBuilder
        PromptBuilder -->|"sends to LLM"| LLMModelFactory
        LLMModelFactory -->|"returns response"| OutputParser
        OutputParser -->|"extracts actions"| AgentExecutor
    end
    
    subgraph "LLM Integration"
        LLMModelFactory["LLM Model Factory"]
        BaseLLM["Base LLM Interface"]
        
        LLMModelFactory -->|"creates"| BaseLLM
        BaseLLM -->|"implements"| ProviderImpls["Provider Implementations"]
    end
    
    subgraph "External Services"
        ProviderImpls -->|"calls"| LLMAPIs["LLM Provider APIs"]
    end
```

Sources: [superagi/llms/llm_model_factory.py:1-55]()

## Testing and Verification

SuperAGI includes testing capabilities for LLM integrations, particularly for local LLMs. The `test_local_llm` endpoint allows users to verify that their local LLM configuration is working correctly.

```mermaid
sequenceDiagram
    participant User
    participant ModelsController
    participant LLMLoader
    participant Llama
    
    User->>ModelsController: Test local LLM
    ModelsController->>LLMLoader: Initialize loader
    LLMLoader->>Llama: Load model and grammar
    
    alt Success
        Llama->>LLMLoader: Model loaded
        LLMLoader->>ModelsController: Return success
        ModelsController->>User: Model loaded successfully
    else Error
        Llama->>LLMLoader: Error loading model
        LLMLoader->>ModelsController: Return error
        ModelsController->>User: Error loading model
    end
```

Sources: [superagi/controllers/models_controller.py:178-204](), [tests/unit_tests/controllers/test_models_controller.py:110-118]()

## Summary

The LLM integration in SuperAGI provides a flexible and extensible system for working with different language model providers. The system includes:

1. Support for multiple LLM providers (OpenAI, Google Palm, Replicate, Hugging Face, Local LLM)
2. Secure API key management
3. Model configuration and management
4. Local LLM support with GPU acceleration
5. Integration with the agent system
6. Web interface for model management

This design allows users to easily switch between different LLM providers based on their requirements, while maintaining a consistent interface for agents to interact with language models.

---

# Page: Supported LLM Providers

# Supported LLM Providers

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile-gpu](Dockerfile-gpu)
- [README.MD](README.MD)
- [config_template.yaml](config_template.yaml)
- [docker-compose-gpu.yml](docker-compose-gpu.yml)
- [gui/pages/Content/Models/AddModel.js](gui/pages/Content/Models/AddModel.js)
- [gui/pages/Content/Models/MarketModels.js](gui/pages/Content/Models/MarketModels.js)
- [gui/pages/Content/Models/ModelForm.js](gui/pages/Content/Models/ModelForm.js)
- [gui/pages/Content/Models/ModelTemplate.js](gui/pages/Content/Models/ModelTemplate.js)
- [gui/pages/Content/Models/Models.js](gui/pages/Content/Models/Models.js)
- [requirements.txt](requirements.txt)
- [superagi/controllers/models_controller.py](superagi/controllers/models_controller.py)
- [superagi/controllers/types/models_types.py](superagi/controllers/types/models_types.py)
- [superagi/helper/llm_loader.py](superagi/helper/llm_loader.py)
- [superagi/llms/llm_model_factory.py](superagi/llms/llm_model_factory.py)
- [superagi/llms/local_llm.py](superagi/llms/local_llm.py)
- [superagi/models/models.py](superagi/models/models.py)
- [superagi/models/models_config.py](superagi/models/models_config.py)
- [superagi/types/model_source_types.py](superagi/types/model_source_types.py)
- [tests/unit_tests/controllers/test_models_controller.py](tests/unit_tests/controllers/test_models_controller.py)
- [tests/unit_tests/tools/duck_duck_go/test_duckduckgo_results.py](tests/unit_tests/tools/duck_duck_go/test_duckduckgo_results.py)

</details>



## Purpose and Scope

This document details the Language Learning Model (LLM) providers supported by SuperAGI, including configuration options, integration methods, and management features. It serves as a technical reference for developers who want to understand how to configure, customize, and use different LLM providers within the SuperAGI framework.

For information about general model management in the system, see [Model Management](#6.2).

## Overview of Supported Providers

SuperAGI integrates with multiple LLM providers, giving users flexibility in choosing models based on their specific requirements, performance needs, and budget constraints.

Currently, SuperAGI supports the following LLM providers:

| Provider | Description | Configuration Key | Model Examples |
|----------|-------------|-------------------|----------------|
| OpenAI | GPT models with strong general capabilities | OPENAI_API_KEY | gpt-3.5-turbo, gpt-4 |
| Google Palm | Google's PaLM-based language models | PALM_API_KEY | models/chat-bison-001 |
| Hugging Face | Open-source models with custom endpoints | HUGGING_API_TOKEN | Custom endpoints |
| Replicate | Hosted models with versioning | REPLICATE_API_TOKEN | Requires version ID |
| Local LLM | Self-hosted models using llama-cpp | N/A | Custom local models |

Sources: [superagi/types/model_source_types.py](), [config_template.yaml](), [superagi/llms/llm_model_factory.py]()

## LLM Integration Architecture

SuperAGI uses a factory pattern to abstract away the specific details of each LLM provider while maintaining a consistent interface for the rest of the system.

### LLM Provider Integration Diagram

```mermaid
graph TD
    subgraph "Agent System"
        Agent["Agent"]
        AgentExecution["Agent Execution"]
    end

    subgraph "Model Management"
        ModelController["ModelsController"]
        ModelHelper["ModelsHelper"]
        ModelConfig["ModelsConfig"]
        ModelTable["Models Table"]
    end

    subgraph "LLM Integration"
        LLMFactory["LLMModelFactory"]
        BaseLLM["BaseLlm Abstract Class"]
    end

    subgraph "Provider Implementations"
        OpenAI["OpenAi Class"]
        GooglePalm["GooglePalm Class"]
        Replicate["Replicate Class"]
        HuggingFace["HuggingFace Class"]
        LocalLLM["LocalLLM Class"]
    end

    subgraph "Local Model Support"
        LLMLoader["LLMLoader"]
        LlamaGrammar["LlamaGrammar"]
        LlamaModel["Llama Model (llama-cpp)"]
    end

    Agent --> AgentExecution
    AgentExecution --> LLMFactory

    ModelController --> ModelHelper
    ModelController --> ModelConfig
    ModelController --> ModelTable

    LLMFactory --> BaseLLM
    LLMFactory --> ModelConfig
    LLMFactory --> ModelTable

    BaseLLM --> OpenAI
    BaseLLM --> GooglePalm
    BaseLLM --> Replicate
    BaseLLM --> HuggingFace
    BaseLLM --> LocalLLM

    LocalLLM --> LLMLoader
    LLMLoader --> LlamaGrammar
    LLMLoader --> LlamaModel
```

Sources: [superagi/llms/llm_model_factory.py](), [superagi/llms/local_llm.py](), [superagi/helper/llm_loader.py]()

## Model Configuration and Database Storage

The system stores model configurations and API keys in the database to ensure secure and persistent access.

### Model Data Flow Diagram

```mermaid
graph TD
    subgraph "User Interface"
        UI["Web UI"]
        ModelForm["ModelForm Component"]
    end

    subgraph "API Layer"
        APIEndpoints["Models Controller Endpoints"]
        StoreModel["POST /store_model"]
        StoreAPIKey["POST /store_api_keys"]
        VerifyEndpoint["GET /verify_end_point"]
        FetchModels["GET /fetch_models"]
    end

    subgraph "Database"
        ModelsConfigTable["ModelsConfig Table"]
        ModelsTable["Models Table"]
    end

    UI --> ModelForm
    ModelForm --> StoreAPIKey
    ModelForm --> VerifyEndpoint
    ModelForm --> StoreModel
    ModelForm --> FetchModels

    StoreAPIKey --> ModelsConfigTable
    StoreModel --> ModelsTable
    VerifyEndpoint --> ModelsHelper["ModelsHelper"]
    FetchModels --> ModelsTable
    FetchModels --> ModelsConfigTable

    ModelsConfigTable --> |"provides API key"| ModelsTable
    ModelsTable --> |"references"| ModelsConfigTable
```

Sources: [superagi/controllers/models_controller.py](), [superagi/models/models_config.py](), [superagi/models/models.py](), [gui/pages/Content/Models/ModelForm.js]()

## Configuration Options

### Basic Configuration in config.yaml

Key settings in your `config.yaml` file:

```yaml
# API Keys for different providers
OPENAI_API_KEY: YOUR_OPEN_API_KEY
PALM_API_KEY: YOUR_PALM_API_KEY
REPLICATE_API_TOKEN: YOUR_REPLICATE_API_TOKEN
HUGGING_API_TOKEN: YOUR_HUGGING_FACE_API_TOKEN

# OpenAI endpoint (default or custom)
OPENAI_API_BASE: https://api.openai.com/v1
# For local LLM, use:
# OPENAI_API_BASE: "http://super__tgwui:5001/v1"

# Default model settings
MODEL_NAME: "gpt-3.5-turbo-0301"
RESOURCES_SUMMARY_MODEL_NAME: "gpt-3.5-turbo"
MAX_TOOL_TOKEN_LIMIT: 800
MAX_MODEL_TOKEN_LIMIT: 4032

# GPU settings for local LLM
GPU_LAYERS: 40  # GPU layers to offload
```

Sources: [config_template.yaml]()

### Database Schema

The system uses two main tables for model configuration:

1. **ModelsConfig** - Stores provider information and API keys:
   - `id`: Primary key
   - `provider`: Provider name (e.g., "OpenAI", "Google Palm")
   - `api_key`: Encrypted API key
   - `org_id`: Organization ID

2. **Models** - Stores specific model details:
   - `id`: Primary key
   - `model_name`: Name of the model
   - `description`: Description of the model
   - `end_point`: API endpoint (for Hugging Face)
   - `model_provider_id`: Reference to ModelsConfig table
   - `token_limit`: Maximum token limit
   - `type`: Model type (Custom/Marketplace)
   - `version`: Model version (for Replicate)
   - `org_id`: Organization ID
   - `context_length`: Context length (for local models)

Sources: [superagi/models/models_config.py](), [superagi/models/models.py]()

## Provider-Specific Details

### OpenAI

OpenAI is the default provider in SuperAGI, supporting models like GPT-3.5-Turbo and GPT-4.

**Configuration Requirements:**
- `OPENAI_API_KEY` in config.yaml or environment
- Optional custom `OPENAI_API_BASE` for proxies or custom endpoints

**Default Models:**
```python
default_models = {
    "gpt-3.5-turbo": 4032,
    "gpt-4": 8092,
    "gpt-3.5-turbo-16k": 16184
}
```

When an OpenAI API key is added, the system automatically adds these default models to the database.

Sources: [superagi/models/models_config.py:102-109]()

### Google Palm

Google Palm provides an alternative to OpenAI models through Google's PaLM API.

**Configuration Requirements:**
- `PALM_API_KEY` in config.yaml or environment
- Typically uses "models/chat-bison-001" as the model

Sources: [superagi/llms/llm_model_factory.py:31-33]()

### Hugging Face

Hugging Face integration allows the use of open-source models through custom endpoints.

**Configuration Requirements:**
- `HUGGING_API_TOKEN` in config.yaml or environment
- Model endpoint URL when adding a new model
- Endpoint must support the expected API format

Sources: [superagi/llms/llm_model_factory.py:34-36]()

### Replicate

Replicate hosts a variety of AI models that can be accessed through their API.

**Configuration Requirements:**
- `REPLICATE_API_TOKEN` in config.yaml or environment
- Model version ID when adding a new model

Sources: [superagi/llms/llm_model_factory.py:28-30]()

### Local LLM

SuperAGI supports running local models through the llama-cpp-python library.

**Configuration Requirements:**
- Docker with GPU support
- Model file in the specified path
- Context length specification
- Optional GPU acceleration settings

The system uses a singleton `LLMLoader` class to manage the loading of the model and grammar:

```python
# Simplified version of LLMLoader initialization
llm_model = Llama(
    model_path="/app/local_model_path", 
    n_ctx=context_length,
    n_gpu_layers=int(get_config('GPU_LAYERS', '-1'))
)
llm_grammar = LlamaGrammar.from_file("superagi/llms/grammar/json.gbnf")
```

For GPU acceleration, ensure you're using the GPU-enabled docker-compose file:
```shell
docker compose -f docker-compose-gpu.yml up --build
```

Sources: [superagi/llms/local_llm.py](), [superagi/helper/llm_loader.py](), [docker-compose-gpu.yml]()

## Adding and Managing Models

### Through the Web UI

The web UI provides a user-friendly interface for adding and managing models:

1. Navigate to the Models section
2. Click "Add Model"
3. Fill in the model details:
   - Name
   - Description
   - Provider selection
   - Provider-specific settings:
     - Endpoint URL for Hugging Face
     - Model version for Replicate
     - Context length for Local LLM
   - Token limit

The UI also provides options to test local models before adding them.

Sources: [gui/pages/Content/Models/ModelForm.js](), [gui/pages/Content/Models/AddModel.js]()

### Through the API

The Models Controller provides these endpoints for programmatic model management:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/models_controller/store_api_keys` | POST | Store provider API keys |
| `/models_controller/get_api_keys` | GET | Get all stored API keys |
| `/models_controller/get_api_key` | GET | Get specific provider API key |
| `/models_controller/verify_end_point` | GET | Verify model endpoint |
| `/models_controller/store_model` | POST | Add a new model |
| `/models_controller/fetch_models` | GET | Get all available models |
| `/models_controller/fetch_model/{model_id}` | GET | Get specific model details |
| `/models_controller/test_local_llm` | GET | Test local LLM functionality |

Example request for adding a model:
```json
{
  "model_name": "my-gpt-4",
  "description": "OpenAI GPT-4 model",
  "end_point": "",
  "model_provider_id": 1,
  "token_limit": 8092,
  "type": "Custom",
  "version": "",
  "context_length": 0
}
```

Sources: [superagi/controllers/models_controller.py]()

## Using Models in Agents

Once configured, models can be selected when creating or configuring agents. The system loads the appropriate model implementation through the `LLMModelFactory`:

```python
# Simplified version of model loading
def get_model(organisation_id, api_key, model="gpt-3.5-turbo", **kwargs):
    # Get model details from database
    model_instance = session.query(Models).filter(
        Models.org_id == organisation_id, 
        Models.model_name == model
    ).first()
    
    # Get provider information
    provider_name = session.query(ModelsConfig.provider).filter(
        ModelsConfig.org_id == organisation_id,
        ModelsConfig.id == model_instance.model_provider_id
    ).first().provider
    
    # Return appropriate implementation
    if provider_name == 'OpenAI':
        return OpenAi(model=model_instance.model_name, api_key=api_key)
    elif provider_name == 'Replicate':
        return Replicate(model=model_instance.model_name, version=model_instance.version, api_key=api_key)
    # Other providers...
    elif provider_name == 'Local LLM':
        return LocalLLM(model=model_instance.model_name, context_length=model_instance.context_length)
```

Sources: [superagi/llms/llm_model_factory.py:12-41]()

## Model Marketplace

SuperAGI includes a model marketplace that allows discovery and installation of pre-configured models:

1. Models can be browsed in the marketplace UI
2. Models can be installed with a single click
3. Installed models are added to the organization's available models

Sources: [gui/pages/Content/Models/MarketModels.js](), [gui/pages/Content/Models/ModelTemplate.js]()

## Best Practices

1. **Security:**
   - API keys are stored encrypted in the database
   - Consider using environment variables instead of config files
   - Regularly rotate API keys

2. **Performance:**
   - Match model token limits to your requirements
   - For performance-critical applications, consider local LLMs with GPU acceleration
   - Be mindful of token usage and costs with paid providers

3. **Model Selection:**
   - For general tasks, "gpt-3.5-turbo" provides a good balance of capability and cost
   - For complex reasoning, consider "gpt-4" or equivalent
   - For cost-sensitive applications, consider open-source models through Hugging Face or local LLMs

4. **Testing:**
   - Use the test functionality for local LLMs before deploying
   - Start with smaller models when experimenting
   - Consider fine-tuning open-source models for specific domains

Sources: [README.MD](), [superagi/controllers/models_controller.py:178-201]()

---

# Page: Model Management

# Model Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [gui/pages/Content/Models/AddModel.js](gui/pages/Content/Models/AddModel.js)
- [gui/pages/Content/Models/MarketModels.js](gui/pages/Content/Models/MarketModels.js)
- [gui/pages/Content/Models/ModelForm.js](gui/pages/Content/Models/ModelForm.js)
- [gui/pages/Content/Models/ModelTemplate.js](gui/pages/Content/Models/ModelTemplate.js)
- [gui/pages/Content/Models/Models.js](gui/pages/Content/Models/Models.js)
- [superagi/controllers/models_controller.py](superagi/controllers/models_controller.py)
- [superagi/controllers/types/models_types.py](superagi/controllers/types/models_types.py)
- [superagi/models/models.py](superagi/models/models.py)
- [superagi/models/models_config.py](superagi/models/models_config.py)
- [tests/unit_tests/controllers/test_models_controller.py](tests/unit_tests/controllers/test_models_controller.py)

</details>



This document explains how to manage and configure language models in SuperAGI. It covers the model registration process, API key management, and the model marketplace. For information about supported LLM providers, see [Supported LLM Providers](#6.1).

## Model Management Architecture

SuperAGI's model management system allows users to configure, store, and use various language models across different providers. The system comprises several core components that work together to provide a flexible model management experience.

```mermaid
graph TD
    subgraph "Frontend"
        ModelUI["Model UI Components"]
        ModelForm["Model Form"]
        MarketModels["Marketplace Models"]
    end
    
    subgraph "API Layer"
        MC["ModelsController"]
    end
    
    subgraph "Data Layer"
        Models["Models Table"]
        ModelsConfig["ModelsConfig Table"]
    end
    
    subgraph "External Systems"
        OpenAI["OpenAI API"]
        GooglePalm["Google Palm API"]
        HuggingFace["Hugging Face API"]
        Replicate["Replicate API"]
        LocalLLM["Local LLM"]
    end
    
    ModelUI --> |"Displays"| Models
    ModelUI --> |"Uses"| ModelForm
    ModelForm --> |"API Calls"| MC
    MarketModels --> |"API Calls"| MC
    
    MC --> |"CRUD Operations"| Models
    MC --> |"CRUD Operations"| ModelsConfig
    
    ModelsConfig --> |"API Keys"| OpenAI
    ModelsConfig --> |"API Keys"| GooglePalm
    ModelsConfig --> |"API Keys"| HuggingFace
    ModelsConfig --> |"API Keys"| Replicate
    ModelsConfig --> |"Configuration"| LocalLLM
    
    Models --> |"References"| ModelsConfig
```

The model management system allows users to:
1. Register and configure language models from various providers
2. Store and manage API keys for different model providers
3. Set model parameters like token limits and context length
4. Browse and install models from the marketplace

Sources:
- [superagi/controllers/models_controller.py]()
- [superagi/models/models.py]()
- [superagi/models/models_config.py]()

## Core Data Models

The model management system is built around two primary database entities:

### ModelsConfig

The `ModelsConfig` table stores API keys and configuration for model providers:

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| provider | String | Model provider name (e.g., OpenAI, Google Palm) |
| api_key | String | Encrypted API key for the provider |
| org_id | Integer | Organization ID that owns this configuration |

### Models 

The `Models` table stores details about individual models:

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| model_name | String | Name of the model (e.g., gpt-3.5-turbo) |
| description | String | Description of the model |
| end_point | String | Custom endpoint for the model (if applicable) |
| model_provider_id | Integer | References ModelsConfig.id |
| token_limit | Integer | Maximum tokens the model can process |
| type | String | Type of model (Custom or Marketplace) |
| version | String | Version of the model (for Replicate models) |
| org_id | Integer | Organization ID that owns this model |
| model_features | String | Features of the model |
| context_length | Integer | Context window size for the model |

Sources:
- [superagi/models/models.py:15-56]()
- [superagi/models/models_config.py:12-35]()

## Model Registration Flow

The process of adding a new model to SuperAGI involves several steps:

```mermaid
sequenceDiagram
    participant User
    participant ModelForm as "Model Form UI"
    participant ModelsController
    participant ModelsConfig
    participant Models
    participant ExternalAPI as "External Provider API"

    User->>ModelForm: Fills model details
    ModelForm->>ModelsController: Verify API key exists
    ModelsController->>ModelsConfig: Fetch API key
    ModelsConfig-->>ModelsController: Return API key
    
    ModelForm->>ModelsController: Verify endpoint
    ModelsController->>ExternalAPI: Test endpoint with API key
    ExternalAPI-->>ModelsController: Endpoint validation result
    
    ModelForm->>ModelsController: Store model
    ModelsController->>Models: Save model details
    Models-->>ModelsController: Confirmation
    ModelsController-->>ModelForm: Success/Error response
    ModelForm-->>User: Display confirmation
```

When adding a new model, the system:
1. Verifies that an API key exists for the selected model provider
2. Validates the endpoint (if applicable)
3. Stores the model details in the database

Sources:
- [superagi/controllers/models_controller.py:73-84]()
- [superagi/models/models.py:108-162]()
- [gui/pages/Content/Models/ModelForm.js:65-123]()

## API Key Management

API keys are securely stored and managed in the `ModelsConfig` table. The system encrypts API keys before storing them in the database.

```mermaid
graph TD
    subgraph "API Key Management"
        StoreAPIKey["Store API Key"]
        FetchAPIKey["Fetch API Key"]
        VerifyEndpoint["Verify Endpoint"]
    end
    
    subgraph "Security Layer"
        Encrypt["Encrypt Data"]
        Decrypt["Decrypt Data"]
    end
    
    subgraph "Database"
        ModelsConfigTable["ModelsConfig Table"]
    end
    
    StoreAPIKey --> |"Input"| Encrypt
    Encrypt --> |"Store Encrypted"| ModelsConfigTable
    FetchAPIKey --> |"Query"| ModelsConfigTable
    ModelsConfigTable --> |"Retrieve Encrypted"| Decrypt
    Decrypt --> |"Return Decrypted"| FetchAPIKey
    
    VerifyEndpoint --> |"Uses"| FetchAPIKey
    VerifyEndpoint --> |"Validates with"| ExternalAPI["External API"]
```

Key API operations include:
- Storing API keys: Encrypts and saves API keys for model providers
- Fetching API keys: Retrieves and decrypts API keys for use
- Verifying endpoints: Tests if an endpoint is valid using the stored API key

Sources:
- [superagi/controllers/models_controller.py:37-70]()
- [superagi/models/models_config.py:78-139]()

## Supported Model Providers

SuperAGI supports the following model providers:

| Provider | Description | API Key Required |
|----------|-------------|-----------------|
| OpenAI | Models like GPT-3.5, GPT-4 | Yes |
| Google Palm | Google's PaLM models | Yes |
| Hugging Face | Hosted Hugging Face models | Yes |
| Replicate | Replicate-hosted models | Yes |
| Local LLM | Locally hosted models | No* |

*Local LLM requires local model files but no external API key

When an OpenAI API key is added, the system automatically detects and adds common models:

```mermaid
graph TB
    subgraph "OpenAI API Key Addition"
        AddAPIKey["Add OpenAI API Key"]
        StoreAPIKey["Store API Key"]
        FetchModels["Fetch Available Models"]
        StoreModels["Store Default Models"]
    end
    
    AddAPIKey --> StoreAPIKey
    StoreAPIKey --> FetchModels
    FetchModels --> StoreModels
    
    subgraph "Default Models"
        GPT35["gpt-3.5-turbo (4032 tokens)"]
        GPT4["gpt-4 (8092 tokens)"]
        GPT35_16k["gpt-3.5-turbo-16k (16184 tokens)"]
    end
    
    StoreModels --> GPT35
    StoreModels --> GPT4
    StoreModels --> GPT35_16k
```

Sources:
- [superagi/models/models_config.py:101-110]()
- [gui/pages/Content/Models/ModelForm.js:9-10]()

## Local LLM Support

SuperAGI provides support for locally hosted language models. The system includes a mechanism to test if a local model is properly configured:

```mermaid
sequenceDiagram
    participant User
    participant ModelForm as "Model Form UI"
    participant ModelsController
    participant LLMLoader
    participant LocalLLM

    User->>ModelForm: Enter Local LLM details
    User->>ModelForm: Click "Test Model"
    ModelForm->>ModelsController: Test Local LLM
    ModelsController->>LLMLoader: Load model
    LLMLoader->>LocalLLM: Initialize model
    LocalLLM-->>LLMLoader: Model loaded
    LLMLoader->>LocalLLM: Create test chat completion
    LocalLLM-->>LLMLoader: Response
    LLMLoader-->>ModelsController: Success/Error
    ModelsController-->>ModelForm: Test result
    ModelForm-->>User: Display success/error
```

Local LLM configuration requires setting:
- Model context length
- Token limit
- No external API key is needed

Sources:
- [superagi/controllers/models_controller.py:178-204]()
- [superagi/models/models_config.py:158-164]()
- [gui/pages/Content/Models/ModelForm.js:177-201]()

## Model Marketplace

SuperAGI includes a marketplace where users can discover and install pre-configured models:

```mermaid
graph TD
    subgraph "Model Marketplace"
        BrowseModels["Browse Models"]
        ModelDetails["View Model Details"]
        InstallModel["Install Model"]
    end
    
    subgraph "API Layer"
        FetchMarketplace["Fetch Marketplace Models"]
        GetModelDetails["Get Model Details"]
        StoreModelAPI["Store Model API"]
    end
    
    subgraph "Database"
        ModelsTable["Models Table"]
    end
    
    BrowseModels --> FetchMarketplace
    FetchMarketplace --> |"Display"| BrowseModels
    
    BrowseModels --> |"Select"| ModelDetails
    ModelDetails --> GetModelDetails
    
    ModelDetails --> |"Install"| InstallModel
    InstallModel --> StoreModelAPI
    StoreModelAPI --> ModelsTable
```

The marketplace functionality includes:
- Browsing available models from the SuperAGI marketplace
- Viewing detailed information about models
- Installing models to your organization
- Tracking model installation statistics

Sources:
- [superagi/controllers/models_controller.py:114-176]()
- [superagi/models/models.py:59-88]()
- [gui/pages/Content/Models/MarketModels.js]()

## User Interface for Model Management

The SuperAGI web interface provides several components for managing models:

### Model List View
Displays all models configured in the system with options to add new models.

### Add Model Form
Provides a form to add new models with fields for:
- Model name
- Description
- Model provider selection
- Token limit
- Context length (for Local LLM)
- Model endpoint (for Hugging Face)
- Model version (for Replicate)

### Model Marketplace
Embeds an iframe to the models.superagi.com marketplace where users can browse and install pre-configured models.

Sources:
- [gui/pages/Content/Models/Models.js]()
- [gui/pages/Content/Models/ModelForm.js]()
- [gui/pages/Content/Models/MarketModels.js]()
- [gui/pages/Content/Models/AddModel.js]()

## API Endpoints

The Models Controller provides several REST endpoints for model management:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/store_api_keys` | POST | Store API keys for model providers |
| `/get_api_keys` | GET | Retrieve all API keys |
| `/get_api_key` | GET | Retrieve a specific API key by provider |
| `/verify_end_point` | GET | Verify if an endpoint is valid |
| `/store_model` | POST | Store a new model |
| `/fetch_models` | GET | Fetch all models for the organization |
| `/fetch_model/{model_id}` | GET | Fetch details for a specific model |
| `/get/list` | GET | Get marketplace model list |
| `/test_local_llm` | GET | Test if a local LLM is properly configured |

Sources:
- [superagi/controllers/models_controller.py:37-204]()

---

# Page: Deployment

# Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [.gitignore](.gitignore)
- [Dockerfile](Dockerfile)
- [Dockerfile-gpu](Dockerfile-gpu)
- [README.MD](README.MD)
- [config_template.yaml](config_template.yaml)
- [docker-compose-gpu.yml](docker-compose-gpu.yml)
- [docker-compose.yaml](docker-compose.yaml)
- [entrypoint.sh](entrypoint.sh)
- [entrypoint_celery.sh](entrypoint_celery.sh)
- [gui/.dockerignore](gui/.dockerignore)
- [gui/Dockerfile](gui/Dockerfile)
- [gui/DockerfileProd](gui/DockerfileProd)
- [gui/next.config.js](gui/next.config.js)
- [gui/pages/Content/Agents/ActionConsole.js](gui/pages/Content/Agents/ActionConsole.js)
- [gui/pages/Content/Agents/RunHistory.js](gui/pages/Content/Agents/RunHistory.js)
- [nginx/default.conf](nginx/default.conf)
- [requirements.txt](requirements.txt)
- [superagi/helper/llm_loader.py](superagi/helper/llm_loader.py)
- [superagi/llms/llm_model_factory.py](superagi/llms/llm_model_factory.py)
- [superagi/llms/local_llm.py](superagi/llms/local_llm.py)
- [superagi/types/model_source_types.py](superagi/types/model_source_types.py)
- [tests/unit_tests/tools/duck_duck_go/test_duckduckgo_results.py](tests/unit_tests/tools/duck_duck_go/test_duckduckgo_results.py)
- [wait-for-it.sh](wait-for-it.sh)

</details>



This page provides a comprehensive guide to deploying SuperAGI in various environments. It covers the requirements, configuration options, and step-by-step procedures for setting up and running the system. For specific information about configuring models, please see [LLM Integration](#6) and for detailed configuration settings, refer to [Configuration Options](#7.2).

## Deployment Options Overview

SuperAGI offers multiple deployment options to accommodate different user needs:

```mermaid
flowchart TD
    Start["Deployment Choice"] --> Cloud["SuperAGI Cloud"]
    Start --> LocalDocker["Local Docker Deployment"]
    Start --> DigitalOcean["DigitalOcean Deployment"]
    
    LocalDocker --> Standard["Standard Docker Deployment"]
    LocalDocker --> GPU["GPU-Accelerated Docker Deployment"]
    
    Cloud --> |"Managed Service"| NoSetup["No Setup Required\nVisit app.superagi.com"]
    Standard --> |"Basic Setup"| CPUBased["CPU-Based\nFor General Use"]
    GPU --> |"Advanced Setup"| GPUAccel["GPU-Accelerated\nFor Local LLM Integration"]
    DigitalOcean --> |"One-Click Deploy"| DODeploy["DigitalOcean App Platform"]
```

Sources: [README.MD:100-147]()

## Prerequisites

Before deploying SuperAGI, ensure you have the following prerequisites:

| Requirement | Standard Deployment | GPU Deployment | Notes |
|-------------|---------------------|----------------|-------|
| Docker | Required | Required | Docker Desktop or Docker Engine |
| Docker Compose | Required | Required | Usually included with Docker Desktop |
| Git | Required | Required | To clone the repository |
| NVIDIA GPU | Not required | Required | With CUDA support |
| NVIDIA Drivers | Not required | Required | Compatible with CUDA 12.1.1 |
| Storage Space | ~2GB minimum | ~10GB minimum | For Docker images and data |

Sources: [README.MD:114-128](), [Dockerfile:1-39](), [Dockerfile-gpu:1-45]()

## Standard Docker Deployment

The standard deployment uses Docker Compose to run SuperAGI on CPU:

1. Clone the repository:
```bash
git clone https://github.com/TransformerOptimus/SuperAGI.git
```

2. Navigate to the cloned directory:
```bash
cd SuperAGI
```

3. Create a configuration file:
```bash
cp config_template.yaml config.yaml
```

4. Edit the `config.yaml` file to add your API keys and customize settings

5. Start the application:
```bash
docker compose -f docker-compose.yaml up --build
```

6. Access the application at http://localhost:3000

```mermaid
graph TD
    subgraph "SuperAGI Deployment"
        User["User Browser"] -->|"HTTP/Port 3000"| Proxy["Nginx Proxy"]
        
        Proxy -->|"Frontend Requests"| GUI["GUI Container"]
        Proxy -->|"API Requests /api/*"| Backend["Backend Container"]
        
        Backend -->|"Database Operations"| Postgres["super__postgres\nPostgreSQL Database"]
        Backend -->|"Queue Jobs"| Redis["super__redis\nRedis Server"]
        
        Celery["Celery Worker"] -->|"Process Jobs"| Redis
        Celery -->|"Database Operations"| Postgres
        Celery -->|"File Operations"| Storage["File Storage\n(workspace/ directory)"]
    end
```

Sources: [docker-compose.yaml:1-76](), [README.MD:114-146](), [nginx/default.conf:1-27]()

## GPU-Accelerated Deployment

For users who want to run local LLMs with GPU acceleration:

1. Follow steps 1-4 from the standard deployment

2. Start the application with the GPU-enabled compose file:
```bash
docker compose -f docker-compose-gpu.yml up --build
```

3. Access the application at http://localhost:3000

4. Update your `config.yaml` file to use local LLMs by uncommenting:
```yaml
#OPENAI_API_BASE: "http://super__tgwui:5001/v1"
```

The GPU deployment includes additional CUDA libraries and configurations to leverage NVIDIA GPUs for accelerated performance when running local language models.

```mermaid
graph TD
    subgraph "GPU Deployment Architecture"
        User["User Browser"] -->|"HTTP/Port 3000"| Proxy["Nginx Proxy"]
        
        Proxy -->|"Frontend Requests"| GUI["GUI Container"]
        Proxy -->|"API Requests /api/*"| Backend["Backend Container\nwith CUDA support"]
        
        Backend -->|"Database Operations"| Postgres["super__postgres\nPostgreSQL Database"]
        Backend -->|"Queue Jobs"| Redis["super__redis\nRedis Server"]
        Backend -->|"GPU Operations"| GPU["NVIDIA GPU\nvia CUDA Libraries"]
        
        Celery["Celery Worker\nwith CUDA support"] -->|"Process Jobs"| Redis
        Celery -->|"Database Operations"| Postgres
        Celery -->|"GPU Operations"| GPU
        Celery -->|"File Operations"| Storage["File Storage\n(workspace/ directory)"]
        
        LLMHelper["LLMLoader Class"] -->|"Load Local Models"| GPU
    end
```

Sources: [docker-compose-gpu.yml:1-96](), [Dockerfile-gpu:1-45](), [superagi/helper/llm_loader.py:1-38](), [superagi/llms/local_llm.py:1-92]()

## Container Architecture

The SuperAGI deployment consists of the following containers:

| Container | Purpose | Source |
|-----------|---------|--------|
| backend | FastAPI server that handles API requests | [Dockerfile:1-39]() |
| celery | Background task processing | [entrypoint_celery.sh:1-9]() |
| gui | Next.js frontend application | [gui/Dockerfile:1-20]() |
| super__redis | Redis for task queuing and caching | [docker-compose.yaml:35-43]() |
| super__postgres | PostgreSQL database for data storage | [docker-compose.yaml:45-57]() |
| proxy | Nginx proxy for routing requests | [nginx/default.conf:1-27]() |

The containers communicate over a Docker network and use volumes for persistent storage:

```mermaid
graph TB
    subgraph "Volume Management"
        PGVol["superagi_postgres_data\nPersistent Volume"] <-->|"Store Database Data"| PG["super__postgres"]
        RedisVol["redis_data\nPersistent Volume"] <-->|"Store Redis Data"| Redis["super__redis"]
        WorkspaceVol["./workspace\nHost-Mounted Volume"] <-->|"Store Agent Resources"| Celery["celery"]
    end
    
    subgraph "Network Communication"
        Backend["backend"] <-->|"API Requests"| Proxy["proxy"]
        GUI["gui"] <-->|"Web Requests"| Proxy
        Backend <-->|"Database Queries"| PG
        Backend <-->|"Queue Management"| Redis
        Celery <-->|"Task Processing"| Redis
        Celery <-->|"Data Storage"| PG
    end
    
    subgraph "External Access"
        User["External User"] -->|"HTTP Port 3000"| Proxy
    end
```

Sources: [docker-compose.yaml:1-76](), [docker-compose-gpu.yml:1-96]()

## Configuration

SuperAGI is configured through the `config.yaml` file, which contains settings for:

1. API keys for external services (OpenAI, Pinecone, etc.)
2. Database connection details
3. Storage configuration (local or S3)
4. LLM provider settings
5. Tool-specific configurations

The configuration file is loaded at startup and used throughout the application. Any changes require a restart of the containers.

```mermaid
graph LR
    subgraph "Configuration Flow"
        ConfigFile["config.yaml"] -->|"Read at Startup"| Backend["Backend Container"]
        ConfigFile -->|"Read at Startup"| Celery["Celery Container"]
        
        subgraph "Key Configuration Sections"
            APIKeys["API Keys\n(OpenAI, Pinecone, etc.)"]
            DBConfig["Database Configuration"]
            StorageConfig["Storage Configuration\n(File or S3)"]
            ToolConfig["Tool Configuration"]
            ModelConfig["LLM Model Configuration"]
        end
        
        ConfigFile ---|"Contains"| APIKeys
        ConfigFile ---|"Contains"| DBConfig
        ConfigFile ---|"Contains"| StorageConfig
        ConfigFile ---|"Contains"| ToolConfig
        ConfigFile ---|"Contains"| ModelConfig
    end
```

Sources: [config_template.yaml:1-126]()

## Cloud Deployment

### SuperAGI Cloud

For users who prefer a managed solution without setup complexity:

1. Visit [SuperAGI Cloud](https://app.superagi.com)
2. Log in using your GitHub account
3. Configure your API keys in account settings
4. Start creating and running agents

### DigitalOcean One-Click Deployment

SuperAGI provides a one-click deployment option for DigitalOcean:

1. Click the "Deploy to DigitalOcean" button in the README
2. Log in to your DigitalOcean account
3. Configure the deployment options
4. Deploy the application

This option automates the deployment process on DigitalOcean's App Platform.

Sources: [README.MD:144-147]()

## Environment Variables

SuperAGI uses several environment variables that can be set in the `config.yaml` file or in your environment:

| Variable | Purpose | Default | Notes |
|----------|---------|---------|-------|
| OPENAI_API_KEY | API key for OpenAI | None | Required for OpenAI models |
| PINECONE_API_KEY | API key for Pinecone | None | For vector database integration |
| STORAGE_TYPE | Storage backend type | "FILE" | "FILE" or "S3" |
| DB_URL | Database connection string | postgresql://superagi:password@super__postgres:5432/super_agi_main | For PostgreSQL connection |
| REDIS_URL | Redis connection string | "super__redis:6379" | For Redis connection |
| GPU_LAYERS | GPU layers for local LLMs | None | Used in GPU deployment |

Sources: [config_template.yaml:1-126](), [docker-compose.yaml:1-76](), [docker-compose-gpu.yml:1-96]()

## External Resource Directory

By default, SuperAGI stores resources in the `workspace` directory. For custom locations, you can set the `EXTERNAL_RESOURCE_DIR` environment variable:

```bash
EXTERNAL_RESOURCE_DIR=/custom/path docker compose -f docker-compose.yaml up
```

This is especially useful when you need to persist agent inputs/outputs across container restarts or when sharing resources between multiple SuperAGI instances.

Sources: [docker-compose.yaml:15-16](), [docker-compose-gpu.yml:15-16]()

## LLM Integration Architecture

SuperAGI supports multiple LLM providers, including local LLMs that can leverage GPU acceleration:

```mermaid
graph TD
    subgraph "LLM Provider Integration"
        LLMFactory["LLM Model Factory\nllm_model_factory.py"] --> OpenAI["OpenAI Provider"]
        LLMFactory --> GooglePalm["Google Palm Provider"]
        LLMFactory --> Replicate["Replicate Provider"]
        LLMFactory --> HuggingFace["Hugging Face Provider"]
        LLMFactory --> LocalLLM["Local LLM Provider"]
        
        LocalLLM -->|"GPU Acceleration"| LLMLoader["LLMLoader\nllm_loader.py"]
        LLMLoader -->|"Load Models"| Llama["Llama CPP\nPython Binding"]
    end
    
    Agent["Agent Executor"] -->|"Get Model"| LLMFactory
    Config["config.yaml"] -->|"Configure"| LLMFactory
```

Sources: [superagi/llms/llm_model_factory.py:1-55](), [superagi/helper/llm_loader.py:1-38](), [superagi/llms/local_llm.py:1-92](), [superagi/types/model_source_types.py:1-33]()

## Troubleshooting Deployment

Common issues and their solutions:

1. **Container startup failures**:
   - Check Docker logs: `docker compose logs`
   - Ensure correct configuration in `config.yaml`
   - Verify port 3000 is not in use by another application

2. **Database connection issues**:
   - Ensure PostgreSQL container is running: `docker compose ps`
   - Check database connection string in `config.yaml`

3. **GPU not detected in GPU deployment**:
   - Verify NVIDIA drivers are installed and working
   - Check NVIDIA Docker runtime is installed
   - Run `nvidia-smi` to confirm GPU is accessible

4. **API key errors**:
   - Ensure all required API keys are correctly set in `config.yaml`
   - Check for spaces or special characters in API keys

5. **File permission issues**:
   - Ensure the `workspace` directory has appropriate permissions
   - For custom external resource directories, check permissions

Sources: [README.MD:190-196](), [entrypoint.sh:1-14](), [wait-for-it.sh:1-183]()

## Deployment Security Considerations

When deploying SuperAGI, consider these security best practices:

1. **API Keys Protection**:
   - Do not commit `config.yaml` with API keys to version control
   - Use environment variables for sensitive information in production

2. **Network Security**:
   - By default, SuperAGI exposes port 3000
   - Use a reverse proxy with HTTPS for production deployments
   - Consider network isolation for production environments

3. **Database Security**:
   - Change the default PostgreSQL password in production
   - Consider using a managed database service for production

4. **Resource Limits**:
   - Set appropriate container resource limits for CPU and memory
   - Monitor resource usage in production environments

Sources: [docker-compose.yaml:1-76](), [config_template.yaml:1-126](), [.gitignore:1-23]()

## System Requirements

Minimum hardware requirements for running SuperAGI:

| Deployment Type | CPU | RAM | Storage | GPU |
|-----------------|-----|-----|---------|-----|
| Standard | 2 cores | 4GB | 10GB | Not required |
| With Local LLMs | 4 cores | 8GB | 20GB | NVIDIA GPU with 8GB+ VRAM |
| Production | 4+ cores | 16GB+ | 40GB+ | Optional |

Sources: [requirements.txt:1-161](), [Dockerfile:1-39](), [Dockerfile-gpu:1-45]()

---

# Page: Docker Deployment

# Docker Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [.gitignore](.gitignore)
- [Dockerfile](Dockerfile)
- [docker-compose.yaml](docker-compose.yaml)
- [entrypoint.sh](entrypoint.sh)
- [entrypoint_celery.sh](entrypoint_celery.sh)
- [gui/.dockerignore](gui/.dockerignore)
- [gui/Dockerfile](gui/Dockerfile)
- [gui/DockerfileProd](gui/DockerfileProd)
- [gui/next.config.js](gui/next.config.js)
- [gui/pages/Content/Agents/ActionConsole.js](gui/pages/Content/Agents/ActionConsole.js)
- [gui/pages/Content/Agents/RunHistory.js](gui/pages/Content/Agents/RunHistory.js)
- [nginx/default.conf](nginx/default.conf)
- [wait-for-it.sh](wait-for-it.sh)

</details>



This document provides a comprehensive guide for deploying SuperAGI using Docker. Docker containerization offers a simplified setup that packages all required dependencies and services, making deployment consistent across different environments. For information about non-Docker configuration options, see [Configuration Options](#7.2).

## 1. Deployment Architecture Overview

SuperAGI's Docker deployment architecture consists of multiple containerized services that work together to provide a complete system. The following diagram illustrates the architecture:

```mermaid
graph TD
    User["User Browser"] --> Proxy["Nginx Proxy (port:3000)"]
    
    subgraph "Docker Containers"
        Proxy --> |"/api/*"| Backend["Backend (FastAPI)"]
        Proxy --> |"/"| GUI["GUI (Next.js)"]
        
        Backend --> Super__Postgres["PostgreSQL (super_agi_main)"]
        Backend --> Super__Redis["Redis Stack Server"]
        Backend --> Celery["Celery Worker"]
        
        Celery --> Super__Redis
        Celery --> Super__Postgres
    end
    
    subgraph "Persistent Volumes"
        Super__Postgres --> PostgresVolume["superagi_postgres_data"]
        Super__Redis --> RedisVolume["redis_data"]
    end
    
    subgraph "External Resources"
        Celery --> ExtResources["External Resources Directory"]
    end
```

Sources: [docker-compose.yaml:1-76]()

## 2. Docker Services Explained

SuperAGI's Docker deployment consists of six main services defined in the `docker-compose.yaml` file:

### 2.1 Backend Service
- **Purpose**: Serves the FastAPI backend application
- **Build**: Uses the repository's root Dockerfile
- **Dependencies**: Requires Redis and PostgreSQL
- **Entrypoint**: Uses `wait-for-it.sh` to wait for PostgreSQL before starting via `entrypoint.sh`

### 2.2 Celery Service
- **Purpose**: Processes background tasks and asynchronous operations
- **Volume Mapping**: Maps the external resource directory for file storage
- **Entrypoint**: Uses `entrypoint_celery.sh` to start the Celery worker

### 2.3 GUI Service
- **Purpose**: Serves the Next.js frontend application
- **Build**: Uses the Dockerfile in the `gui` directory
- **Environment Configuration**: Configures API base URL during build

### 2.4 Redis Service
- **Purpose**: Provides caching, message broker, and vector database functionality
- **Image**: Uses `redis/redis-stack-server:latest`
- **Persistent Storage**: Uses a volume for data persistence

### 2.5 PostgreSQL Service
- **Purpose**: Primary database for storing system data
- **Image**: Uses `postgres:15`
- **Configuration**: Pre-configured with database name, username, and password
- **Persistent Storage**: Uses a volume for data persistence

### 2.6 Nginx Proxy
- **Purpose**: Routes requests to appropriate backend or frontend services
- **Port Mapping**: Maps container port 80 to host port 3000
- **Configuration**: Uses custom configuration from `nginx/default.conf`

Sources: [docker-compose.yaml:3-69](), [nginx/default.conf:1-27]()

## 3. Docker Deployment Process

The following diagram shows the build and startup sequence for the Docker deployment:

```mermaid
flowchart TD
    Start["Start Deployment"] --> DockerCompose["docker-compose up"]
    
    subgraph "Build Phase"
        DockerCompose --> BuildBackend["Build Backend Image"]
        DockerCompose --> BuildGUI["Build GUI Image"]
        
        BuildBackend --> BackendDeps["Install Python Dependencies"]
        BuildGUI --> GUIDeps["Install Node Dependencies"]
    end
    
    subgraph "Startup Phase"
        BuildBackend --> StartServices["Start Services"]
        StartServices --> StartPostgres["Start PostgreSQL"]
        StartServices --> StartRedis["Start Redis"]
        
        StartPostgres --> WaitForPostgres["Wait for PostgreSQL (wait-for-it.sh)"]
        
        WaitForPostgres --> StartBackend["Start Backend (entrypoint.sh)"]
        StartBackend --> ToolManager["Run Tool Manager"]
        StartBackend --> InstallTools["Install Tool Dependencies"]
        StartBackend --> MigrateDB["Run Alembic Migrations"]
        StartBackend --> LaunchAPI["Launch FastAPI Server"]
        
        StartRedis --> StartCelery["Start Celery Worker"]
        
        StartBackend --> StartGUI["Start GUI"]
        StartGUI --> StartNginx["Start Nginx Proxy"]
    end
    
    StartNginx --> Ready["Deployment Ready (http://localhost:3000)"]
```

Sources: [docker-compose.yaml:12-23](), [entrypoint.sh:1-14](), [entrypoint_celery.sh:1-9]()

## 4. Container Build Details

### 4.1 Backend Container

The backend container uses a multi-stage build process to optimize the final image size:

```mermaid
graph TD
    subgraph "Backend Dockerfile"
        Stage1["Stage 1: compile-image"] --> InstallDeps["Install system dependencies"]
        InstallDeps --> SetupVenv["Create Python virtual environment"]
        SetupVenv --> InstallPythonDeps["Install Python dependencies"]
        InstallPythonDeps --> InstallNLTK["Download NLTK data"]
        InstallNLTK --> SetupPerms["Set script permissions"]
        
        Stage1 --> Stage2["Stage 2: build-image"]
        Stage2 --> CopyVenv["Copy virtual environment"]
        CopyVenv --> CopyApp["Copy application code"]
        CopyApp --> CopyNLTK["Copy NLTK data"]
        CopyNLTK --> ExposePort["Expose port 8001"]
    end
```

Sources: [Dockerfile:1-39]()

### 4.2 GUI Container

The GUI container build process:

```mermaid
graph TD
    subgraph "GUI Dockerfile"
        Stage1["deps: Install dependencies"] --> InstallDeps["Install Node dependencies"]
        
        InstallDeps --> Stage2["builder: Build application"]
        Stage2 --> CopyDeps["Copy node_modules"]
        CopyDeps --> CopyApp["Copy application code"]
        CopyApp --> SetEnv["Set environment variables"]
        SetEnv --> ExposePort["Expose port 3000"]
        ExposePort --> RunDev["Run npm run dev"]
    end
```

Sources: [gui/Dockerfile:1-20]()

## 5. Configuration Files

### 5.1 Docker Compose Configuration

The `docker-compose.yaml` file defines all services, their relationships, networking, and volume configurations. Key configuration aspects include:

| Service | Configuration Highlights |
|---------|--------------------------|
| backend | Mounts application code, depends on PostgreSQL and Redis |
| celery | Mounts external resource directory, processes background tasks |
| gui | Builds with API base URL configuration |
| super__redis | Redis Stack Server with persistent volume |
| super__postgres | PostgreSQL with environment variables and persistent volume |
| proxy | Nginx proxy with port mapping (3000:80) |

Sources: [docker-compose.yaml:1-76]()

### 5.2 Nginx Configuration

The Nginx proxy routes requests between the GUI and backend services:

| Path | Target | Purpose |
|------|--------|---------|
| `/` | `gui:3000` | Frontend application |
| `/api` | `backend:8001` | API routes (with path rewriting) |
| `/_next/webpack-hmr` | `gui:3000` | WebSocket for hot module replacement |

Sources: [nginx/default.conf:1-27]()

## 6. Deployment Instructions

### 6.1 Prerequisites

- Docker Engine (version 19.03.0+)
- Docker Compose (version 1.27.0+)
- Git (to clone the repository)

### 6.2 Deployment Steps

1. Clone the SuperAGI repository:
   ```
   git clone https://github.com/TransformerOptimus/SuperAGI.git
   cd SuperAGI
   ```

2. Start the Docker deployment:
   ```
   docker-compose up -d
   ```

3. Access the application at `http://localhost:3000`

### 6.3 Environment Configuration

SuperAGI can be configured through environment variables. The primary configuration for Docker deployments is:

| Variable | Purpose | Default |
|----------|---------|---------|
| EXTERNAL_RESOURCE_DIR | Directory for external resources | ./workspace |

Sources: [docker-compose.yaml:16]()

## 7. Customization Options

### 7.1 Exposing Database Ports

By default, the database ports are not exposed to the host. To expose them for external access, uncomment the relevant port mapping lines in `docker-compose.yaml`:

For PostgreSQL:
```yaml
# ports:
#   - "5432:5432"
```

For Redis:
```yaml
# ports:
#   - "6379:6379"
```

Sources: [docker-compose.yaml:40-41](), [docker-compose.yaml:56-57]()

### 7.2 External Resource Directory

You can customize the external resource directory by setting the `EXTERNAL_RESOURCE_DIR` environment variable when starting the deployment:

```
EXTERNAL_RESOURCE_DIR=/path/to/resources docker-compose up -d
```

Sources: [docker-compose.yaml:16]()

### 7.3 GUI Development Mode

The GUI container is configured to run in development mode by default. For production deployments, you would use the production Dockerfile (`DockerfileProd`).

Sources: [gui/Dockerfile:20](), [gui/DockerfileProd:1-43]()

## 8. Container Scripts and Entry Points

### 8.1 Backend Entry Point

The `entrypoint.sh` script is the main entry point for the backend container:

1. Downloads tools from marketplace and external repositories
2. Installs tool dependencies
3. Runs database migrations
4. Starts the FastAPI server

Sources: [entrypoint.sh:1-14]()

### 8.2 Celery Entry Point

The `entrypoint_celery.sh` script initializes the Celery worker:

1. Downloads tools
2. Installs tool dependencies
3. Starts the Celery worker with beat scheduler

Sources: [entrypoint_celery.sh:1-9]()

### 8.3 Wait For It Script

The `wait-for-it.sh` script is used to ensure PostgreSQL is ready before starting the backend:

- Checks if the PostgreSQL service is accepting connections
- Times out after a configurable period (60 seconds by default)
- Executes the backend entrypoint script once the database is ready

Sources: [wait-for-it.sh:1-183](), [docker-compose.yaml:12]()

## 9. Troubleshooting

### 9.1 Common Issues

- **Container startup failures**: Check logs with `docker-compose logs [service_name]`
- **Database connection issues**: Ensure PostgreSQL container is running and healthy
- **Missing volume data**: Verify that Docker volumes are properly created

### 9.2 Docker Volume Management

SuperAGI uses two persistent volumes:
- `superagi_postgres_data`: Stores PostgreSQL data
- `redis_data`: Stores Redis data

To list volumes:
```
docker volume ls
```

To inspect a volume:
```
docker volume inspect [volume_name]
```

Sources: [docker-compose.yaml:74-76]()

---

# Page: Configuration Options

# Configuration Options

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile-gpu](Dockerfile-gpu)
- [README.MD](README.MD)
- [config_template.yaml](config_template.yaml)
- [docker-compose-gpu.yml](docker-compose-gpu.yml)
- [requirements.txt](requirements.txt)
- [superagi/helper/llm_loader.py](superagi/helper/llm_loader.py)
- [superagi/llms/llm_model_factory.py](superagi/llms/llm_model_factory.py)
- [superagi/llms/local_llm.py](superagi/llms/local_llm.py)
- [superagi/types/model_source_types.py](superagi/types/model_source_types.py)
- [tests/unit_tests/tools/duck_duck_go/test_duckduckgo_results.py](tests/unit_tests/tools/duck_duck_go/test_duckduckgo_results.py)

</details>



This document provides a comprehensive guide to the configuration options available in SuperAGI. It covers environment variables, configuration files, and various settings that control the behavior of the system. For information about deployment instructions, see [Docker Deployment](#7.1).

## Overview of Configuration System

SuperAGI uses a YAML-based configuration system that allows users to customize various aspects of the platform. The primary configuration file is `config.yaml`, which users create based on the provided template file `config_template.yaml`.

```mermaid
flowchart TD
    subgraph "Configuration Flow"
        A["config_template.yaml"] -->|Copy and modify| B["config.yaml"]
        B -->|Used by| C["SuperAGI System"]
        D["Environment Variables"] -->|Override| B
    end
```

Sources: [config_template.yaml:1-126]()

## Core Configuration Categories

The configuration options in SuperAGI are organized into several categories:

```mermaid
flowchart LR
    root["SuperAGI Configuration"] --> sys["System Keys"]
    root --> db["Database Configuration"]
    root --> storage["Storage Configuration"] 
    root --> auth["Authentication"]
    root --> llm["LLM Integration"]
    root --> vector["Vector Databases"]
    root --> tools["Tool-specific Configuration"]
    
    sys --> api_keys["API Keys"]
    sys --> model_settings["Model Settings"]
    
    storage --> type["Storage Type"]
    storage --> paths["Resource Paths"]
    storage --> s3["S3 Configuration"]
    
    auth --> jwt["JWT Settings"]
    auth --> oauth["GitHub OAuth"]
    
    tools --> search["Search Tools"]
    tools --> email["Email Tool"]
    tools --> github["GitHub Tool"]
    tools --> jira["Jira Tool"]
    tools --> slack["Slack Tool"]
    tools --> image["Image Generation"]
```

Sources: [config_template.yaml:1-126]()

## System Keys and API Integration

### Language Model API Keys

SuperAGI supports multiple LLM providers, each requiring specific API keys:

| Provider | Configuration Key | Description |
|----------|------------------|-------------|
| OpenAI | `OPENAI_API_KEY` | API key for OpenAI models (GPT-3.5, GPT-4) |
| Google Palm | `PALM_API_KEY` | API key for Google PaLM models |
| Replicate | `REPLICATE_API_TOKEN` | Token for Replicate-hosted models |
| Hugging Face | `HUGGING_API_TOKEN` | Token for Hugging Face models |

### Vector Database API Keys

For vector database integration:

| Vector DB | Configuration Keys |
|-----------|-------------------|
| Pinecone | `PINECONE_API_KEY`, `PINECONE_ENVIRONMENT` |
| Weaviate | `WEAVIATE_URL`, `WEAVIATE_API_KEY`, `WEAVIATE_USE_EMBEDDED` |
| Qdrant | `QDRANT_HOST_NAME`, `QDRANT_PORT` |
| Chroma | `CHROMA_HOST_NAME`, `CHROMA_PORT` |

Sources: [config_template.yaml:1-9](), [config_template.yaml:61-67](), [config_template.yaml:107-124]()

## Model Configuration Options

SuperAGI provides extensive configuration for language model settings:

```mermaid
flowchart TD
    subgraph "LLM Configuration System"
        config["get_config()"] -->|Loads| model_settings["Model Settings"]
        model_settings -->|Controls| model_factory["LLM Model Factory"]
        
        model_factory -->|Creates| openai["OpenAI Model"]
        model_factory -->|Creates| palm["Google Palm Model"]
        model_factory -->|Creates| replicate["Replicate Model"]
        model_factory -->|Creates| huggingface["Hugging Face Model"]
        model_factory -->|Creates| local_llm["Local LLM Model"]
        
        local_llm -->|Uses| llm_loader["LLM Loader"]
        
        llm_loader -->|Loads| llama_model["Llama Model"]
        llm_loader -->|Uses| gpu_config["GPU Configuration"]
    end
```

### Key Model Settings

| Configuration | Description | Default Value |
|---------------|-------------|--------------|
| `MODEL_NAME` | Default model name | "gpt-3.5-turbo-0301" |
| `RESOURCES_SUMMARY_MODEL_NAME` | Model for summarizing resources | "gpt-3.5-turbo" |
| `MAX_TOOL_TOKEN_LIMIT` | Maximum token limit for tools | 800 |
| `MAX_MODEL_TOKEN_LIMIT` | Maximum token limit for the model | 4032 |
| `OPENAI_API_BASE` | Base URL for OpenAI API | https://api.openai.com/v1 |
| `GPU_LAYERS` | GPU layers for local LLM acceleration | - |

For local LLM support using GPU acceleration, you need to configure:
- `GPU_LAYERS`: Number of GPU layers to offload to the GPU
- Set `OPENAI_API_BASE` to your local model endpoint

Sources: [config_template.yaml:10-20](), [superagi/llms/llm_model_factory.py:1-55](), [superagi/helper/llm_loader.py:1-38](), [superagi/llms/local_llm.py:1-92](), [superagi/types/model_source_types.py:1-33]()

## Database Configuration

SuperAGI uses PostgreSQL for its primary database and Redis for various caching and vector storage purposes:

| Configuration | Description | Default Value |
|---------------|-------------|--------------|
| `DB_NAME` | Database name | super_agi_main |
| `DB_HOST` | Database host | super__postgres |
| `DB_USERNAME` | Database username | superagi |
| `DB_PASSWORD` | Database password | password |
| `DB_URL` | Full database connection URL | postgresql://superagi:password@super__postgres:5432/super_agi_main |
| `REDIS_URL` | Redis connection URL | "super__redis:6379" |

Sources: [config_template.yaml:22-29]()

## Storage Configuration

SuperAGI supports multiple storage options for resources:

| Configuration | Description | Default Value |
|---------------|-------------|--------------|
| `STORAGE_TYPE` | Storage type ("FILE" or "S3") | "FILE" |
| `RESOURCES_INPUT_ROOT_DIR` | Directory for input resources | workspace/input/{agent_id} |
| `RESOURCES_OUTPUT_ROOT_DIR` | Directory for output resources | workspace/output/{agent_id}/{agent_execution_id} |

### S3 Storage Configuration (when `STORAGE_TYPE` is "S3")

| Configuration | Description |
|---------------|-------------|
| `BUCKET_NAME` | S3 bucket name |
| `INSTAGRAM_TOOL_BUCKET_NAME` | Public bucket for Instagram tool images |
| `AWS_ACCESS_KEY_ID` | AWS access key |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key |

Sources: [config_template.yaml:31-46]()

## Authentication Configuration

SuperAGI provides authentication options:

| Configuration | Description | Default Value |
|---------------|-------------|--------------|
| `ENV` | Environment (DEV/PROD) | 'DEV' |
| `JWT_SECRET_KEY` | Secret key for JWT | 'secret' |
| `expiry_time_hours` | JWT token expiry time | 1 |

### GitHub OAuth (when `ENV` is 'PROD')

| Configuration | Description |
|---------------|-------------|
| `GITHUB_CLIENT_ID` | GitHub OAuth client ID |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth client secret |
| `FRONTEND_URL` | Frontend URL | "http://localhost:3000" |

### Encryption

| Configuration | Description | Default Value |
|---------------|-------------|--------------|
| `ENCRYPTION_KEY` | Key for encrypting sensitive data | abcdefghijklmnopqrstuvwxyz123456 |

Sources: [config_template.yaml:48-59]()

## Vector Database Configuration

SuperAGI supports multiple vector databases for knowledge storage:

```mermaid
flowchart TD
    subgraph "Vector Database Configuration"
        config["Configuration"] -->|Sets| vector_store["RESOURCE_VECTOR_STORE"]
        config -->|Sets| index_name["RESOURCE_VECTOR_STORE_INDEX_NAME"]
        
        vector_store -->|Can be| redis["REDIS"]
        vector_store -->|Can be| pinecone["PINECONE"]
        vector_store -->|Can be| chroma["CHROMA"]
        vector_store -->|Can be| qdrant["QDRANT"]
        
        redis -->|Requires| redis_url["REDIS_VECTOR_STORE_URL"]
        pinecone -->|Requires| pinecone_config["PINECONE_API_KEY, PINECONE_ENVIRONMENT"]
        chroma -->|Requires| chroma_config["CHROMA_HOST_NAME, CHROMA_PORT"]
        qdrant -->|Requires| qdrant_config["QDRANT_HOST_NAME, QDRANT_PORT"]
    end
```

Sources: [config_template.yaml:107-124]()

## Tool Configuration Options

SuperAGI includes various tools that require specific configuration:

### Search Tools

| Configuration | Description |
|---------------|-------------|
| `GOOGLE_API_KEY` | Google API key |
| `SEARCH_ENGINE_ID` | Google Search Engine ID |
| `SERP_API_KEY` | Serper.dev API key (alternative to Google) |

### Email Tool

| Configuration | Description | Default Value |
|---------------|-------------|--------------|
| `EMAIL_ADDRESS` | Email address | - |
| `EMAIL_PASSWORD` | App password for email | - |
| `EMAIL_SMTP_HOST` | SMTP host | smtp.gmail.com |
| `EMAIL_SMTP_PORT` | SMTP port | 587 |
| `EMAIL_IMAP_SERVER` | IMAP server | imap.gmail.com |
| `EMAIL_SIGNATURE` | Signature for emails | Email sent by SuperAGI |
| `EMAIL_DRAFT_MODE_WITH_FOLDER` | Draft folder | - |
| `EMAIL_ATTACHMENT_BASE_PATH` | Directory for email attachments | - |

### GitHub Tool

| Configuration | Description |
|---------------|-------------|
| `GITHUB_USERNAME` | GitHub username |
| `GITHUB_ACCESS_TOKEN` | GitHub access token |

### Jira Tool

| Configuration | Description |
|---------------|-------------|
| `JIRA_INSTANCE_URL` | Jira instance URL |
| `JIRA_USERNAME` | Jira email |
| `JIRA_API_TOKEN` | Jira API token |

### Slack Tool

| Configuration | Description |
|---------------|-------------|
| `SLACK_BOT_TOKEN` | Slack bot token |

### Image Generation Tools

| Configuration | Description | Default Value |
|---------------|-------------|--------------|
| `STABILITY_API_KEY` | Stability API key | - |
| `ENGINE_ID` | Image generation engine ID | "stable-diffusion-xl-beta-v2-2-2" |

Sources: [config_template.yaml:69-102]()

## Docker Deployment Configuration

SuperAGI provides specialized Docker configurations for different deployment scenarios:

### Regular Deployment

```bash
docker compose -f docker-compose.yaml up --build
```

### GPU-Accelerated Deployment

```bash
docker compose -f docker-compose-gpu.yml up --build
```

The GPU configuration in `docker-compose-gpu.yml` includes:

- NVIDIA CUDA container configuration
- GPU resource allocation for backend and celery services
- OpenCL and CUDA libraries for LLM acceleration

Sources: [README.MD:131-139](), [docker-compose-gpu.yml:1-96](), [Dockerfile-gpu:1-45]()

## Environment Variable Overrides

All configuration options in `config.yaml` can be overridden using environment variables with the same name. This is particularly useful for:

- Docker deployments
- CI/CD pipelines
- Cloud hosting environments
- Keeping sensitive information out of configuration files

For example, to override the OpenAI API key:

```bash
OPENAI_API_KEY=your_actual_key docker compose up
```

## Configuration Best Practices

1. **Never commit `config.yaml` with sensitive information** to version control
2. Use environment variables for sensitive information in production
3. Replace the default `ENCRYPTION_KEY` with a secure value in production
4. In production, set `ENV` to 'PROD' to enable GitHub OAuth
5. For local development, the defaults in `config_template.yaml` provide a good starting point
6. When using GPU acceleration, adjust `GPU_LAYERS` based on your hardware capabilities

Sources: [README.MD:100-148](), [config_template.yaml:1-126]()