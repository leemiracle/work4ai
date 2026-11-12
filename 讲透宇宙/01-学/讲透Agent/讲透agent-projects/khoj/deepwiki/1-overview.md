<!-- source: DeepWiki mcp.deepwiki.com · repo khoj-ai/khoj · page 1 Overview · fetched 2026-10-29 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [documentation/docs/advanced/gcp-vertex.md](documentation/docs/advanced/gcp-vertex.md)
- [documentation/package.json](documentation/package.json)
- [documentation/yarn.lock](documentation/yarn.lock)
- [pyproject.toml](pyproject.toml)
- [src/interface/desktop/yarn.lock](src/interface/desktop/yarn.lock)
- [src/interface/obsidian/README.md](src/interface/obsidian/README.md)
- [src/interface/obsidian/yarn.lock](src/interface/obsidian/yarn.lock)
- [src/interface/web/bun.lock](src/interface/web/bun.lock)
- [src/interface/web/tsconfig.json](src/interface/web/tsconfig.json)
- [src/khoj/app/settings.py](src/khoj/app/settings.py)
- [src/khoj/main.py](src/khoj/main.py)
- [src/khoj/utils/cli.py](src/khoj/utils/cli.py)
- [src/khoj/utils/state.py](src/khoj/utils/state.py)
- [uv.lock](uv.lock)

</details>



Khoj is an open-source personal AI assistant system designed as a "second brain" that combines semantic search over personal documents with conversational AI capabilities. The system enables users to chat with their notes, search their knowledge base, generate images and diagrams, execute code, browse the web, and automate tasks through multiple client interfaces (web, desktop, Emacs, Obsidian).

For detailed information about specific subsystems, see:
- Backend infrastructure and API design: [System Architecture](#1.1)
- Chat and AI capabilities: [Feature Overview](#1.2)
- Document indexing and search: [Content Processing and Search](#4)
- Client applications: [User Interfaces](#5)
- Deployment and operations: [Deployment and Operations](#6)

## System Architecture

Khoj implements a client-server architecture with a FastAPI/Django backend, PostgreSQL database with vector search capabilities, and multiple frontend clients. The system integrates with various LLM providers (OpenAI, Anthropic, Google Gemini) and supports extensible tooling through MCP (Model Context Protocol).

### High-Level Component Structure

```mermaid
graph TB
    subgraph "Client Layer"
        WebApp["Next.js Web App<br/>src/interface/web"]
        EmacsClient["Emacs Client<br/>src/interface/emacs/khoj.el"]
        ObsidianPlugin["Obsidian Plugin<br/>src/interface/obsidian"]
        DesktopApp["Electron Desktop<br/>src/interface/desktop"]
    end
    
    subgraph "API Gateway"
        FastAPIApp["FastAPI Application<br/>src/khoj/main.py"]
        APIRouter["api.py<br/>Search, Settings, Transcribe"]
        ChatRouter["api_chat.py<br/>Chat, History, Sessions"]
        AuthMiddleware["UserAuthenticationBackend<br/>src/khoj/configure.py"]
    end
    
    subgraph "Core Services"
        ConversationProcessor["Conversation Processor<br/>src/khoj/routers/helpers.py<br/>agenerate_chat_response()"]
        SearchEngine["Text Search<br/>src/khoj/search_type/text_search.py"]
        ContentIndexer["Content Indexer<br/>src/khoj/configure.py<br/>initialize_content()"]
        ResearchOrchestrator["Research Mode<br/>src/khoj/routers/research.py"]
    end
    
    subgraph "AI Integration"
        LLMRouter["Multi-Provider Router<br/>send_message_to_model_wrapper()"]
        OpenAIChat["openai_send_message_to_model<br/>src/khoj/processor/conversation/openai/gpt.py"]
        AnthropicChat["anthropic_send_message_to_model<br/>src/khoj/processor/conversation/anthropic/"]
        GeminiChat["gemini_send_message_to_model<br/>src/khoj/processor/conversation/google/"]
    end
    
    subgraph "Tool Ecosystem"
        OnlineSearch["search_online()<br/>src/khoj/processor/tools/online_search.py"]
        CodeExecution["run_code()<br/>src/khoj/processor/tools/run_code.py"]
        MCPTools["MCPClient<br/>src/khoj/processor/tools/mcp.py"]
        ImageGen["text_to_image()<br/>src/khoj/processor/image/generate.py"]
    end
    
    subgraph "Data Layer"
        DjangoORM["Django Models<br/>src/khoj/database/models/__init__.py"]
        Adapters["Database Adapters<br/>src/khoj/database/adapters/__init__.py"]
        PostgreSQL[("PostgreSQL + pgvector<br/>KhojUser, Entry, Conversation<br/>Agent, Subscription")]
    end
    
    WebApp --> FastAPIApp
    EmacsClient --> FastAPIApp
    ObsidianPlugin --> FastAPIApp
    DesktopApp --> FastAPIApp
    
    FastAPIApp --> AuthMiddleware
    AuthMiddleware --> APIRouter
    AuthMiddleware --> ChatRouter
    
    APIRouter --> SearchEngine
    APIRouter --> ContentIndexer
    ChatRouter --> ConversationProcessor
    
    ConversationProcessor --> LLMRouter
    ConversationProcessor --> ResearchOrchestrator
    
    LLMRouter --> OpenAIChat
    LLMRouter --> AnthropicChat
    LLMRouter --> GeminiChat
    
    ConversationProcessor --> OnlineSearch
    ConversationProcessor --> CodeExecution
    ConversationProcessor --> MCPTools
    ConversationProcessor --> ImageGen
    
    SearchEngine --> Adapters
    ContentIndexer --> Adapters
    ConversationProcessor --> Adapters
    Adapters --> DjangoORM
    DjangoORM --> PostgreSQL
```

**Sources**: [src/khoj/main.py:61-198](), [src/khoj/app/settings.py:72-83](), [src/khoj/app/settings.py:178-189](), [pyproject.toml:38-98]()

### Request Processing Flow

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI as "FastAPI<br/>main.py"
    participant Auth as "UserAuthenticationBackend"
    participant Router as "api_chat.py"
    participant Helper as "helpers.py<br/>agenerate_chat_response()"
    participant LLM as "LLM Provider<br/>OpenAI/Anthropic/Gemini"
    participant DB as "PostgreSQL"
    
    Client->>FastAPI: POST /api/chat
    FastAPI->>Auth: authenticate()
    Auth->>DB: Query KhojUser
    DB-->>Auth: User object
    Auth-->>FastAPI: AuthenticatedKhojUser
    
    FastAPI->>Router: event_generator()
    Router->>Helper: agenerate_chat_response()
    
    alt Tool Required
        Helper->>Helper: Execute tool (search/code/web)
        Helper-->>Router: yield {ChatEvent.STATUS}
    end
    
    Helper->>LLM: send_message_to_model_wrapper()
    LLM-->>Helper: Stream response chunks
    Helper-->>Router: yield {ChatEvent.MESSAGE}
    
    Router-->>Client: Server-Sent Events
```

**Sources**: [src/khoj/main.py:61-67](), [src/khoj/main.py:185-195](), [src/khoj/app/settings.py:192-192]()

## Core Components

### Backend Application

The backend is built on **FastAPI** with **Django ORM** for database management. The main application entry point is `src/khoj/main.py`, which initializes the server, configures middleware, and registers API routers. It also handles the initialization of the database via Django management commands [src/khoj/main.py:51-54]().

| Component | File Path | Purpose |
|-----------|-----------|---------|
| Application Bootstrap | `src/khoj/main.py` | FastAPI app initialization, middleware setup, and DB migration |
| Settings | `src/khoj/app/settings.py` | Django configuration, database settings, and app definitions |
| State Management | `src/khoj/utils/state.py` | Global application state (models, clients, schedulers) |
| CLI Interface | `src/khoj/utils/cli.py` | Command-line argument parsing and server configuration |

**Sources**: [src/khoj/main.py:26-67](), [src/khoj/app/settings.py:1-210](), [src/khoj/utils/state.py:1-41](), [src/khoj/utils/cli.py:9-53]()

### Feature Overview

Khoj provides a comprehensive suite of AI-powered features designed to augment human intelligence. For details, see [Feature Overview](#1.2).

*   **Chat & Agents**: Interact with multiple LLMs (OpenAI, Anthropic, Gemini) [pyproject.toml:45-90](). Create custom agents with specific personas and tools [README.md:49-49]().
*   **Semantic Search**: Advanced search over local documents including PDF, Markdown, Org-mode, and Word [README.md:47-47]().
*   **Tool Integrations**: Built-in capabilities for web search, code execution via E2B, and image generation [pyproject.toml:95-96]().
*   **Automations**: Scheduled research tasks and personal newsletters delivered to inbox [README.md:50-50]().
*   **Computer Operator**: Experimental agents capable of browser and computer automation [README.md:37-37]().

**Sources**: [README.md:42-55](), [pyproject.toml:38-98]()

### User Interfaces

Khoj is accessible through a variety of interfaces to fit into any workflow. For details, see [User Interfaces](#5).

*   **Web Interface**: A modern Next.js application [src/interface/web/bun.lock:51-51]().
*   **Desktop App**: Electron-based application for local use [src/interface/desktop/yarn.lock:5-19]().
*   **Obsidian Plugin**: Integrates Khoj directly into your vault [src/interface/obsidian/README.md:1-4]().
*   **Emacs**: Native integration via `khoj.el`.

**Sources**: [README.md:48-48](), [src/interface/obsidian/README.md:1-4](), [src/interface/web/bun.lock:1-61]()

## Deployment and Operations

Khoj is designed to be flexible, supporting both cloud-scale enterprise deployments and private, on-device usage. It utilizes Docker for containerization and includes a comprehensive CI/CD pipeline for testing and benchmarking. For details, see [Deployment and Operations](#6).

**Sources**: [README.md:67-73](), [pyproject.toml:109-133](), [src/khoj/main.py:153-182]()

---

