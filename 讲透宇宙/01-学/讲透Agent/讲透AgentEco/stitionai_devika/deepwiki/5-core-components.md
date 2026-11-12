<!-- source: DeepWiki mcp.deepwiki.com · repo stitionai/devika · page 5 Core Components · fetched 2026-10-27 -->

# Core Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [README.md](README.md)
- [devika.py](devika.py)
- [src/state.py](src/state.py)

</details>



This document provides a technical overview of the core components that make up the Devika system, including their purpose, structure, and interactions. It focuses on the fundamental building blocks that enable Devika to function as an agentic AI software engineer.

For detailed information on specific subsystems, see the following related wiki pages:
- For detailed agent system information, see [Agent System](#5.1)
- For code generation specifics, see [Code Generation](#5.2)
- For LLM integration details, see [LLM Interface](#5.3)
- For search capabilities, see [Search and Research](#5.4)

## Core Components Overview

Devika is built on a modular architecture with several key components working together to provide an AI software engineering assistant.

```mermaid
graph TD
    User["User"] <--> Backend["Backend System"]
    Backend <--> AgentSystem["Agent System"]
    Backend <--> StateSystem["State Management System"]
    Backend <--> ConfigSystem["Configuration System"]
    Backend <--> LoggingSystem["Logging System"]
    
    AgentSystem <--> LLMSystem["LLM Integration System"]
    AgentSystem <--> SearchSystem["Search System"]
    
    ProjectManager["ProjectManager"] <--> Backend
    ProjectManager <--> FileSystem["File System"]
    
    AgentSystem -- "stores state" --> StateSystem
    ConfigSystem -- "configures" --> LLMSystem
    Backend -- "logs events" --> LoggingSystem
```

Sources: [devika.py:11-26](), [README.md:51-53]()

## Backend System

The backend system serves as the central nervous system of Devika, handling communication with the frontend, managing API endpoints, and orchestrating the other components.

### Flask Application

The backend is built on Flask, providing HTTP endpoints and Socket.IO for real-time communication.

```mermaid
graph LR
    subgraph "Backend API Endpoints"
        API["/api/data"] --> ProjectList["Project List"]
        API --> ModelList["LLM Models List"]
        API --> SearchEngines["Search Engines List"]
        Socket["user-message Socket"] --> AgentExecution["Agent Execution"]
        States["/api/get-agent-state"] --> StateRetrieval["State Retrieval"]
        BrowserAPI["/api/get-browser-session"] --> BrowserStateRetrieval["Browser State"]
        TerminalAPI["/api/get-terminal-session"] --> TerminalStateRetrieval["Terminal State"]
        TokenAPI["/api/token-usage"] --> TokenRetrieval["Token Usage"]
        SettingsAPI["/api/settings"] --> ConfigRetrieval["Configuration"]
    end
```

Sources: [devika.py:59-205]()

The backend initializes several core components during startup:

```mermaid
graph TD
    DevikaInit["init_devika()"] --> AppInit["Flask App Initialization"]
    AppInit --> ManagerInit["ProjectManager Initialization"]
    AppInit --> StateInit["AgentState Initialization"]
    AppInit --> ConfigInit["Config Initialization"]
    AppInit --> LoggerInit["Logger Initialization"]
    AppInit --> SocketIOInit["SocketIO Initialization"]
```

Sources: [devika.py:7-8](), [devika.py:28-49]()

## Agent System

The Agent System is responsible for processing user requests, breaking them down into tasks, and executing those tasks through specialized agents.

```mermaid
graph TD
    Agent["Agent Class"] --> AgentState["AgentState"]
    Agent --> LLM["LLM"]
    Agent -- "execute()" --> ExecuteMethod["Initial Execution"]
    Agent -- "subsequent_execute()" --> SubsequentMethod["Follow-up Execution"]
    
    ExecuteMethod --> AgentOrchestrator["Agent Orchestration"]
    SubsequentMethod --> AgentOrchestrator
    
    AgentOrchestrator --> Planner["Planner Agent"]
    AgentOrchestrator --> Researcher["Researcher Agent"]
    AgentOrchestrator --> Coder["Coder Agent"]
    AgentOrchestrator --> Action["Action Agent"]
    AgentOrchestrator --> Patcher["Patcher Agent"]
    AgentOrchestrator --> Feature["Feature Agent"]
```

Sources: [devika.py:85-103]()

## State Management System

The State Management System tracks and persists the state of agents and their interactions with the system.

```mermaid
graph TD
    AgentStateClass["AgentState Class"] --> SQLiteDB["SQLite Database (AgentStateModel)"]
    AgentStateClass -- "create_state()" --> NewState["New Agent State"]
    AgentStateClass -- "update_latest_state()" --> StateUpdate["State Updates"]
    AgentStateClass -- "get_latest_state()" --> StateRetrieval["State Retrieval"]
    
    StateStructure["State Structure"] --> InternalMonologue["internal_monologue"]
    StateStructure --> BrowserSession["browser_session"]
    StateStructure --> TerminalSession["terminal_session"]
    StateStructure --> StepCount["step"]
    StateStructure --> CompletionStatus["completed"]
    StateStructure --> AgentStatus["agent_is_active"]
    StateStructure --> TokenUsage["token_usage"]
    
    AgentStateClass -- "emit_agent()" --> SocketIO["Socket.IO Events"]
```

Sources: [src/state.py:1-177]()

### State Persistence

Agent state is persisted in a SQLite database using SQLModel:

```mermaid
graph LR
    AgentStateModel["AgentStateModel"] --> id["id (PK)"]
    AgentStateModel --> project["project"]
    AgentStateModel --> state_stack_json["state_stack_json"]
    
    state_stack_json -- "JSON serialization" --> StateStack["Array of State Objects"]
```

Sources: [src/state.py:10-16](), [src/state.py:25-45]()

## Configuration System

The Configuration System manages application settings, including API keys, endpoints, and other configuration parameters.

```mermaid
graph TD
    ConfigClass["Config Class"] --> ConfigFile["config.toml"]
    ConfigClass -- "get_config()" --> ConfigRetrieval["Configuration Retrieval"]
    ConfigClass -- "update_config()" --> ConfigUpdate["Configuration Updates"]
    
    ConfigStructure["Configuration Structure"] --> APIKeys["API Keys (OpenAI, Claude, etc.)"]
    ConfigStructure --> APIEndpoints["API Endpoints"]
    ConfigStructure --> StoragePaths["Storage Paths"]
    ConfigStructure --> LoggingConfig["Logging Configuration"]
    
    APIKeys --> OpenAI["OPENAI"]
    APIKeys --> Claude["CLAUDE"]
    APIKeys --> Gemini["GEMINI"]
    APIKeys --> Mistral["MISTRAL"]
    APIKeys --> Groq["GROQ"]
    APIKeys --> SearchEngines["BING, GOOGLE_SEARCH"]
```

Sources: [devika.py:190-198](), [README.md:130-151]()

## LLM Integration System

The LLM Integration System provides a unified interface to various language models, allowing Devika to leverage different AI capabilities.

```mermaid
graph TD
    LLMClass["LLM Class"] --> ModelList["list_models()"]
    LLMClass --> LLMAbstraction["LLM Abstraction Layer"]
    
    LLMAbstraction --> OpenAI["OpenAI Client"]
    LLMAbstraction --> Claude["Claude Client"]
    LLMAbstraction --> Gemini["Gemini Client"]
    LLMAbstraction --> Mistral["Mistral Client"]
    LLMAbstraction --> Groq["Groq Client"]
    LLMAbstraction --> Ollama["Ollama Client (Local LLMs)"]
```

Sources: [devika.py:63-64](), [README.md:41]()

## Project Management

The Project Management system handles the organization and management of user projects.

```mermaid
graph TD
    ProjectManagerClass["ProjectManager Class"] -- "get_project_list()" --> ProjectList["Project List"]
    ProjectManagerClass -- "get_messages()" --> ProjectMessages["Project Messages"]
    
    ProjectManagerClass --> FileSystem["Project Files"]
    Agent["Agent System"] --> ProjectManagerClass
```

Sources: [devika.py:46](), [devika.py:59-73]()

## Logging System

The Logging System captures events and diagnostics throughout the application.

```mermaid
graph LR
    LoggerClass["Logger Class"] -- "info()" --> LogInfo["Information Logs"]
    LoggerClass -- "warning()" --> LogWarning["Warning Logs"]
    LoggerClass -- "error()" --> LogError["Error Logs"]
    LoggerClass -- "read_log_file()" --> LogRetrieval["Log File Retrieval"]
    
    RouteLogger["route_logger Decorator"] --> LoggerClass
    
    LoggerClass --> LogFile["Log Files"]
```

Sources: [devika.py:49](), [devika.py:181-184]()

## Communication Between Components

Components in Devika communicate through several mechanisms:

```mermaid
graph TD
    Flask["Flask Routes"] --> API["API Endpoints"]
    SocketIO["Socket.IO Events"] --> RealTime["Real-time Updates"]
    
    API --> ConfigSystem["Configuration System"]
    API --> ProjectManager["Project Manager"]
    API --> AgentState["Agent State"]
    
    RealTime --> AgentState
    RealTime --> AgentSystem["Agent System"]
    
    AgentSystem -- "uses" --> LLM["LLM Integration"]
    AgentSystem -- "updates" --> AgentState
    AgentSystem -- "uses" --> ProjectManager
    
    ConfigSystem -- "configures" --> LLM
    ConfigSystem -- "configures" --> AgentSystem
```

Sources: [devika.py:53-56](), [devika.py:77-103]()

## System Initialization Flow

When Devika starts, the following initialization sequence occurs:

```mermaid
sequenceDiagram
    participant main as "devika.py:main"
    participant init as "init_devika()"
    participant flask as "Flask App"
    participant managers as "Component Managers"
    participant socket as "SocketIO"
    
    main->>init: Call init_devika()
    init->>flask: Initialize Flask application
    flask->>managers: Initialize ProjectManager
    flask->>managers: Initialize AgentState
    flask->>managers: Initialize Config
    flask->>managers: Initialize Logger
    flask->>socket: Initialize SocketIO
    main->>flask: Register routes and blueprints
    main->>socket: Register socket events
    main->>flask: Start server (socketio.run)
```

Sources: [devika.py:7-8](), [devika.py:207-209]()

The core components of Devika work together to provide a comprehensive AI software engineering assistant capable of understanding user requirements, researching solutions, and generating code to meet those requirements.

---

