# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Repository Purpose

This repository contains two independent starter applications that serve as reference implementations for integrating OpenAI's ChatKit service into conversational AI applications. The repository demonstrates two distinct integration patterns, allowing developers to choose the approach that best fits their infrastructure and operational requirements.

**Sources:** [README.md:1-9]()

---

## Two Starter Applications

The repository provides two complete, working examples:

| Application | Directory | Integration Pattern | Operational Model |
|-------------|-----------|---------------------|-------------------|
| **Self-Hosted ChatKit** | `chatkit/` | Full control over all components | Developer manages infrastructure and scaling |
| **Managed ChatKit** | `managed-chatkit/` | Uses OpenAI hosted workflows | Reduced operational complexity |

Both applications share identical technology stacks (FastAPI + Vite/React) but differ in how they handle conversation orchestration. The self-hosted variant provides complete control and customization, while the managed variant offloads workflow execution to OpenAI's hosted infrastructure.

For detailed comparison of these patterns, see [Two Integration Patterns](#1.1).

**Sources:** [README.md:5-8]()

---

## Repository Structure

The repository is organized as two independent projects with parallel structures:

### High-Level Organization

```mermaid
graph TB
    subgraph Repository["openai-chatkit-starter-app"]
        ROOT_README["README.md<br/>Repository documentation"]
        CI["/.github/workflows/ci.yml<br/>CI/CD pipeline"]
        
        subgraph ChatKit["chatkit/<br/>Self-Hosted Integration"]
            CK_README["README.md"]
            CK_BACKEND["backend/<br/>FastAPI application"]
            CK_FRONTEND["frontend/<br/>Vite + React"]
        end
        
        subgraph ManagedChatKit["managed-chatkit/<br/>Managed Integration"]
            MCK_README["README.md"]
            MCK_BACKEND["backend/<br/>FastAPI application"]
            MCK_FRONTEND["frontend/<br/>Vite + React"]
        end
    end
    
    ROOT_README -.->|"documents"| ChatKit
    ROOT_README -.->|"documents"| ManagedChatKit
    CI -.->|"validates"| CK_BACKEND
    CI -.->|"validates"| CK_FRONTEND
    CI -.->|"validates"| MCK_BACKEND
    CI -.->|"validates"| MCK_FRONTEND
```

Each application directory (`chatkit/` and `managed-chatkit/`) contains:
- `backend/` - FastAPI Python backend with AI agent integration
- `frontend/` - Vite + React TypeScript frontend
- `README.md` - Application-specific setup instructions

For detailed directory layout, see [Repository Structure](#1.3).

**Sources:** [README.md:1-9]()

---

## Shared Architecture Pattern

Both starter applications follow an identical architectural pattern with separate backend and frontend components:

### Self-Hosted ChatKit Architecture (chatkit/)

```mermaid
graph TB
    subgraph Frontend["Frontend: Vite + React<br/>Port 3000"]
        UI["React UI Components"]
        CONFIG["config.ts<br/>Connection settings"]
        PANEL["ChatKitPanel.tsx<br/>Main UI layout"]
    end
    
    subgraph Backend["Backend: FastAPI<br/>Port 8000"]
        MAIN["main.py<br/>FastAPI app"]
        ENDPOINT["/chatkit endpoint<br/>HTTP handler"]
        SERVER["StarterChatServer<br/>app/server.py"]
        STORE["MemoryStore<br/>In-memory data"]
        AGENT["assistant_agent<br/>AI integration"]
    end
    
    subgraph External["External Services"]
        OPENAI["OpenAI API<br/>Chat completions"]
        CHATKIT_LIB["openai-chatkit library"]
    end
    
    UI -->|"HTTP proxy /chatkit"| ENDPOINT
    ENDPOINT --> SERVER
    SERVER --> STORE
    SERVER --> AGENT
    AGENT --> CHATKIT_LIB
    CHATKIT_LIB --> OPENAI
    OPENAI -.->|"streaming response"| CHATKIT_LIB
```

The managed variant (`managed-chatkit/`) uses the same structure but delegates workflow execution to hosted infrastructure instead of local agent processing.

For detailed architecture of each variant, see:
- Self-hosted: [Self-Hosted ChatKit Architecture](#3.1)
- Managed: [Managed ChatKit Architecture](#4.2)

**Sources:** High-level system architecture diagrams

---

## Technology Stack Overview

Both starter applications are built on modern, production-ready technologies:

### Backend Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.11+ | Programming language |
| **FastAPI** | 0.114-0.116 | High-performance async web framework |
| **Uvicorn** | Latest | ASGI server for FastAPI |
| **openai** | ≥1.40 | OpenAI Python SDK |
| **openai-chatkit** | 1.4.0-2.0 | ChatKit integration library |

### Frontend Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **Node.js** | 22 | JavaScript runtime |
| **Vite** | Latest | Fast build tool and dev server |
| **React** | Latest | UI component library |
| **TypeScript** | Latest | Type-safe JavaScript |

### Development Tools

Both projects use modern quality assurance tools:
- **ruff** - Fast Python linter and formatter
- **mypy** - Python static type checker
- **ESLint** - JavaScript/TypeScript linter

For comprehensive dependency documentation, see [Key Technologies](#1.2) and [Dependencies & Package Management](#5).

**Sources:** High-level system architecture diagrams

---

## Request Flow Example

The following sequence shows a typical chat interaction in the self-hosted variant:

### Complete Request Lifecycle

```mermaid
sequenceDiagram
    participant User
    participant Frontend as "React Frontend<br/>Port 3000"
    participant Proxy as "/chatkit endpoint<br/>FastAPI"
    participant Server as "StarterChatServer<br/>app/server.py"
    participant Store as "MemoryStore"
    participant Agent as "assistant_agent"
    participant OpenAI as "OpenAI API"
    
    User->>Frontend: "Send message"
    Frontend->>Proxy: "POST /chatkit"
    Proxy->>Server: "process(payload)"
    
    Server->>Store: "load_thread_items()<br/>(last 30 messages)"
    Store-->>Server: "Conversation history"
    
    Server->>Agent: "run_streamed(input)"
    Agent->>OpenAI: "Chat completion request"
    
    loop "Streaming Response"
        OpenAI-->>Agent: "Partial chunk"
        Agent-->>Server: "ThreadStreamEvent"
        Server-->>Proxy: "StreamingResponse"
        Proxy-->>Frontend: "SSE event"
        Frontend-->>User: "Update UI"
    end
    
    Server->>Store: "save_item()<br/>(persist message)"
```

This streaming architecture enables real-time response rendering while maintaining conversation context through the `MemoryStore` component.

For detailed flow analysis, see [Request Flow & Data Model](#3.4).

**Sources:** High-level system architecture diagrams

---

## Getting Started

Each starter application can be run independently with the following setup:

### Quick Start

1. **Install dependencies**:
   - Python 3.11+ and Node.js 22
   - Backend: Python virtual environment with `pip install -r requirements.txt`
   - Frontend: `npm install` in frontend directory

2. **Configure environment**:
   - Set `OPENAI_API_KEY` in backend `.env.local`
   - Configure `VITE_CHATKIT_API_URL` and `VITE_CHATKIT_API_DOMAIN_KEY` in frontend `.env.local`

3. **Run both servers**:
   ```bash
   npm run dev  # Starts both backend (port 8000) and frontend (port 3000)
   ```

For detailed setup instructions, see [Getting Started](#2).

**Sources:** [README.md:1-9]()

---

## Key Customization Points

The starter applications are designed for easy customization:

### Backend Customization

| Component | File Path | Customization |
|-----------|-----------|---------------|
| **Data Storage** | `backend/app/server.py` | Replace `MemoryStore` with persistent database |
| **AI Agent** | `backend/app/server.py` | Modify `assistant_agent` configuration and system prompts |
| **Context Window** | `backend/app/server.py` | Adjust `load_thread_items(limit=30)` for more/less history |

### Frontend Customization

| Component | File Path | Customization |
|-----------|-----------|---------------|
| **UI Layout** | `frontend/src/components/ChatKitPanel.tsx` | Modify chat interface layout and styling |
| **Connection Settings** | `frontend/src/lib/config.ts` | Configure API endpoints and domain keys |

For detailed customization guidance, see [Customization Guide](#3.5).

**Sources:** High-level system architecture diagrams

---

## CI/CD Validation

The repository includes automated quality checks via GitHub Actions:

### Validation Pipeline

```mermaid
graph LR
    subgraph "Python Checks"
        PY_SYNTAX["Syntax check<br/>python -m py_compile"]
        PY_LINT["ruff check"]
        PY_FORMAT["ruff format --check"]
        PY_TYPE["mypy --strict"]
    end
    
    subgraph "Node.js Checks"
        NODE_INSTALL["npm ci"]
        NODE_LINT["npm run lint"]
        NODE_BUILD["npm run build"]
    end
    
    PY_SYNTAX --> PY_LINT --> PY_FORMAT --> PY_TYPE
    NODE_INSTALL --> NODE_LINT --> NODE_BUILD
```

All four projects (`chatkit/backend`, `chatkit/frontend`, `managed-chatkit/backend`, `managed-chatkit/frontend`) are validated in parallel on every push and pull request.

For complete CI/CD documentation, see [CI/CD Pipeline](#6).

**Sources:** High-level system architecture diagrams

---

## Next Steps

After reading this overview, explore the following sections for detailed documentation:

- **Setup Instructions**: [Getting Started](#2) for step-by-step setup
- **Architecture Deep Dive**: [Application Architecture](#5) for component relationships
- **API Documentation**: [Backend API](#7) for session endpoint details
- **Customization Guide**: [Configuration System](#8) for modifying prompts and behavior
- **Deployment**: [Deployment Guide](#12) for production builds

**Sources:** Table of contents structure

---

# Page: Two Integration Patterns

# Two Integration Patterns

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

This document explains the two integration patterns provided in the OpenAI ChatKit Starter repository: **self-hosted ChatKit** and **managed ChatKit**. It clarifies the architectural and operational differences between these patterns to help developers choose the appropriate approach for their use case.

For detailed architecture of the self-hosted implementation, see [Architecture Overview](#3.1). For managed ChatKit specifics, see [Overview & Hosted Workflows](#4.1). For choosing between patterns based on infrastructure requirements, see [Deployment Considerations](#8).

---

## Overview

The repository provides two independent starter applications that demonstrate different operational models for integrating ChatKit:

| Pattern | Directory | Description |
|---------|-----------|-------------|
| Self-Hosted | `chatkit/` | Complete application where developers manage all infrastructure, logic, and state |
| Managed | `managed-chatkit/` | Integration using hosted workflows to reduce operational complexity |

Both patterns share the same technology stack (FastAPI backend + Vite/React frontend) but differ fundamentally in where the conversational logic executes and who manages the infrastructure.

**Sources:** [README.md:1-9]()

---

## Pattern Comparison

### Self-Hosted ChatKit Pattern

```mermaid
graph TB
    subgraph Developer_Infrastructure["Developer-Managed Infrastructure"]
        subgraph Backend["chatkit/backend/"]
            MAIN["main.py<br/>/chatkit endpoint"]
            SERVER["app/server.py<br/>StarterChatServer"]
            STORE["app/server.py<br/>MemoryStore"]
            AGENT["app/server.py<br/>assistant_agent"]
        end
        
        subgraph Frontend["chatkit/frontend/"]
            UI["React UI Components"]
            CONFIG["src/lib/config.ts"]
        end
    end
    
    subgraph External["External Services"]
        OPENAI["OpenAI API"]
    end
    
    UI -->|"Proxied requests"| MAIN
    MAIN -->|"Orchestrates"| SERVER
    SERVER -->|"Loads/saves state"| STORE
    SERVER -->|"Generates responses"| AGENT
    AGENT -->|"Chat completions"| OPENAI
    
    note1["Developer Responsibilities:<br/>- Host backend & frontend<br/>- Manage state persistence<br/>- Handle scaling<br/>- Monitor performance<br/>- Maintain infrastructure"]
    
    Developer_Infrastructure -.-> note1
```

**Characteristics:**

- **Full Control**: Developers implement and manage the entire `StarterChatServer` class, including conversation orchestration, state management via `MemoryStore`, and agent configuration
- **Local State**: Thread history and metadata stored in developer-managed storage (default: in-memory via `MemoryStore`)
- **Direct API Integration**: Backend directly calls OpenAI API through `openai-chatkit` library
- **Infrastructure Ownership**: Requires hosting FastAPI backend and serving React frontend
- **Customization**: Complete access to modify server logic, storage layer, and agent behavior

**Sources:** [README.md:7](), Diagram 2 from system architecture, Diagram 6 from system architecture

---

### Managed ChatKit Pattern

```mermaid
graph TB
    subgraph Developer_Infrastructure["Developer-Managed Components"]
        subgraph Backend["managed-chatkit/backend/"]
            MAIN_M["main.py<br/>/chatkit endpoint"]
            SERVER_M["app/server.py<br/>Configuration"]
        end
        
        subgraph Frontend_M["managed-chatkit/frontend/"]
            UI_M["React UI Components"]
            CONFIG_M["src/lib/config.ts"]
        end
    end
    
    subgraph Hosted_Services["Hosted Workflows (Managed)"]
        WORKFLOW["Conversation Logic"]
        STATE["State Management"]
        SCALING["Auto-scaling"]
    end
    
    subgraph External["External Services"]
        OPENAI_M["OpenAI API"]
    end
    
    UI_M -->|"Proxied requests"| MAIN_M
    MAIN_M -->|"Delegates to"| WORKFLOW
    WORKFLOW -->|"Managed"| STATE
    WORKFLOW -->|"Chat completions"| OPENAI_M
    
    note2["Developer Responsibilities:<br/>- Configure workflows<br/>- Host frontend proxy<br/>- Manage API keys<br/><br/>Hosted Services Handle:<br/>- Conversation orchestration<br/>- State persistence<br/>- Scaling & availability<br/>- Infrastructure maintenance"]
    
    Hosted_Services -.-> note2
```

**Characteristics:**

- **Reduced Operational Burden**: Hosted workflows manage conversation orchestration, eliminating need for custom server implementation
- **Managed State**: Thread history and state handled by hosted infrastructure, not developer-managed storage
- **Simplified Backend**: Backend primarily acts as configuration point and proxy, not full orchestrator
- **Automatic Scaling**: Hosted workflows handle traffic spikes and resource allocation
- **Limited Customization**: Workflow behavior configured rather than directly implemented

**Sources:** [README.md:8](), Diagram 1 from system architecture, Diagram 6 from system architecture

---

## Code Structure Mapping

### Directory Organization

```mermaid
graph TB
    subgraph Repo["openai-chatkit-starter-app/"]
        README["README.md<br/>Pattern documentation"]
        
        subgraph SelfHosted["chatkit/<br/>(Self-Hosted Pattern)"]
            SH_BE["backend/<br/>Full server implementation"]
            SH_FE["frontend/<br/>UI + config"]
            SH_README["README.md"]
        end
        
        subgraph Managed["managed-chatkit/<br/>(Managed Pattern)"]
            M_BE["backend/<br/>Minimal configuration"]
            M_FE["frontend/<br/>UI + config"]
            M_README["README.md"]
        end
    end
    
    README -->|"Links to"| SH_README
    README -->|"Links to"| M_README
    
    note["Both patterns:<br/>- Same tech stack<br/>- Independent applications<br/>- Separate dependencies<br/>- Isolated configurations"]
    
    Repo -.-> note
```

The two patterns exist as completely independent applications within the repository. Each has its own:

- Backend directory with `main.py` entrypoint and `pyproject.toml`
- Frontend directory with `vite.config.ts` and `package.json`
- Environment configuration (`.env.local`)
- README with pattern-specific instructions

**Sources:** [README.md:3-8](), Diagram 1 from system architecture, Diagram 3 from system architecture

---

## Key Architectural Differences

| Aspect | Self-Hosted (`chatkit/`) | Managed (`managed-chatkit/`) |
|--------|--------------------------|------------------------------|
| **Server Logic** | Full `StarterChatServer` implementation in `backend/app/server.py` | Minimal configuration, workflow logic hosted externally |
| **State Storage** | Developer implements storage (default: `MemoryStore` class) | Managed by hosted infrastructure |
| **Conversation Orchestration** | `StarterChatServer.respond()` method orchestrates flow | Hosted workflow orchestrates flow |
| **Agent Definition** | Local `assistant_agent` configuration in `backend/app/server.py` | Workflow-configured agent |
| **Scaling** | Developer manages uvicorn workers and infrastructure | Automatic via hosted services |
| **Deployment Complexity** | Higher - requires hosting both backend and frontend | Lower - primarily frontend hosting |
| **Customization Level** | High - direct code access to all components | Medium - configuration-based customization |

**Sources:** Diagram 2 from system architecture, Diagram 6 from system architecture

---

## Operational Model Comparison

### Self-Hosted Operational Flow

```mermaid
sequenceDiagram
    participant Developer
    participant Infrastructure as "Developer Infrastructure"
    participant Backend as "chatkit/backend/"
    participant OpenAI
    
    Developer->>Infrastructure: "Deploy FastAPI app"
    Developer->>Infrastructure: "Deploy React frontend"
    Developer->>Backend: "Implement StarterChatServer"
    Developer->>Backend: "Implement MemoryStore"
    
    Note over Developer,Backend: "Runtime: Developer manages"
    
    Infrastructure->>Backend: "User request"
    Backend->>Backend: "Load from MemoryStore"
    Backend->>OpenAI: "API call"
    OpenAI-->>Backend: "Response"
    Backend->>Backend: "Save to MemoryStore"
    Backend-->>Infrastructure: "Stream response"
    
    Note over Developer,Infrastructure: "Monitoring, scaling,<br/>maintenance by developer"
```

**Sources:** Diagram 2 from system architecture, Diagram 4 from system architecture

---

### Managed Operational Flow

```mermaid
sequenceDiagram
    participant Developer
    participant Frontend as "managed-chatkit/frontend/"
    participant Backend as "managed-chatkit/backend/"
    participant Hosted as "Hosted Workflows"
    participant OpenAI
    
    Developer->>Backend: "Configure workflow connection"
    Developer->>Frontend: "Deploy React frontend"
    
    Note over Developer,Hosted: "Runtime: Hosted manages orchestration"
    
    Frontend->>Backend: "User request"
    Backend->>Hosted: "Delegate to workflow"
    Hosted->>Hosted: "Load managed state"
    Hosted->>OpenAI: "API call"
    OpenAI-->>Hosted: "Response"
    Hosted->>Hosted: "Save to managed state"
    Hosted-->>Backend: "Stream response"
    Backend-->>Frontend: "Forward stream"
    
    Note over Hosted,OpenAI: "Scaling, state management<br/>handled by hosted infrastructure"
```

**Sources:** [README.md:8](), Diagram 6 from system architecture

---

## Choosing Between Patterns

### Use Self-Hosted When:

- **Full Control Required**: Need to customize conversation logic, state management, or agent behavior beyond configuration
- **On-Premise Deployment**: Security or compliance requires running all infrastructure internally
- **Custom Storage**: Need to integrate with specific database systems or state management approaches
- **Learning Implementation**: Want to understand complete ChatKit integration architecture
- **Complex Workflows**: Building sophisticated multi-agent or multi-step conversation flows

**Key Trade-off**: Higher operational complexity in exchange for maximum flexibility.

---

### Use Managed When:

- **Rapid Deployment**: Need to launch quickly without infrastructure setup
- **Reduced Maintenance**: Want to minimize operational burden and focus on frontend experience
- **Automatic Scaling**: Expect variable traffic patterns and need automatic resource management
- **Standard Use Cases**: Conversation requirements fit within workflow configuration options
- **Team Constraints**: Limited DevOps resources for managing backend infrastructure

**Key Trade-off**: Configuration-based customization in exchange for simplified operations.

**Sources:** Diagram 6 from system architecture

---

## Pattern Selection Decision Tree

```mermaid
graph TD
    START["Integration Pattern Selection"]
    
    Q1{"Need custom<br/>conversation logic?"}
    Q2{"Have DevOps resources<br/>for backend hosting?"}
    Q3{"Need on-premise<br/>deployment?"}
    Q4{"Standard conversation<br/>requirements?"}
    
    SELF["Self-Hosted Pattern<br/>chatkit/"]
    MANAGED["Managed Pattern<br/>managed-chatkit/"]
    
    START --> Q1
    Q1 -->|"Yes"| Q2
    Q1 -->|"No"| Q4
    
    Q2 -->|"Yes"| SELF
    Q2 -->|"No"| Q3
    
    Q3 -->|"Yes"| SELF
    Q3 -->|"No"| MANAGED
    
    Q4 -->|"Yes"| MANAGED
    Q4 -->|"No"| SELF
```

**Sources:** Diagram 6 from system architecture

---

## Common Elements

Despite operational differences, both patterns share:

- **Technology Stack**: FastAPI (backend), Vite + React (frontend), TypeScript
- **Environment Configuration**: Both use `.env.local` for `OPENAI_API_KEY` and `VITE_*` variables
- **Development Workflow**: Both use `npm run dev` to start concurrent backend and frontend servers
- **OpenAI Integration**: Both ultimately interact with OpenAI API for chat completions
- **Frontend Structure**: Nearly identical React UI components and configuration files

The patterns diverge at the **backend orchestration layer**: self-hosted implements full server logic locally, while managed delegates to hosted workflows.

**Sources:** [README.md:3-8](), Diagram 3 from system architecture, Diagram 5 from system architecture

---

## Next Steps

After selecting a pattern:

- **Self-Hosted**: Continue to [Architecture Overview](#3.1) for complete implementation details
- **Managed**: See [Overview & Hosted Workflows](#4.1) for workflow configuration
- **Setup**: Both patterns start with [Installation & Prerequisites](#2.1)
- **Configuration**: See [Environment Configuration](#2.2) for required variables

**Sources:** [README.md:5-8]()

---

# Page: Key Technologies

# Key Technologies

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [chatkit/.env.example](chatkit/.env.example)
- [chatkit/.gitignore](chatkit/.gitignore)
- [chatkit/README.md](chatkit/README.md)
- [chatkit/backend/.gitignore](chatkit/backend/.gitignore)
- [chatkit/backend/app/__init__.py](chatkit/backend/app/__init__.py)
- [chatkit/backend/pyproject.toml](chatkit/backend/pyproject.toml)

</details>



This page documents the technology stack shared by both starter applications in this repository. Both `chatkit/` (self-hosted) and `managed-chatkit/` (managed) use identical technology stacks, differing only in their integration with OpenAI services. The architecture follows a standard separation between backend (Python/FastAPI) and frontend (Node.js/Vite/React).

For information on how these dependencies are managed and installed, see section 5 (Dependencies & Package Management). For CI/CD validation of these technologies, see section 6 (CI/CD Pipeline).

## Technology Stack Overview

Both starter applications consist of two independent technology stacks that communicate via HTTP:

| Layer | Technology | Version Requirement | Purpose |
|-------|-----------|---------------------|---------|
| **Backend Runtime** | Python | ≥3.11 | Server-side execution environment |
| **Backend Framework** | FastAPI | 0.114-0.116 | HTTP API server with async support |
| **Backend Server** | Uvicorn | ≥0.36, <0.37 | ASGI application server |
| **OpenAI SDK** | openai | ≥1.40 | OpenAI API client |
| **ChatKit Library** | openai-chatkit | 1.4.0-2.0 | ChatKit server integration |
| **Frontend Runtime** | Node.js | 22 | JavaScript execution environment |
| **Frontend Build Tool** | Vite | Latest | Fast development server and bundler |
| **Frontend Framework** | React | Latest | UI component library |
| **Frontend Language** | TypeScript | Latest | Type-safe JavaScript development |

**Sources**: [chatkit/backend/pyproject.toml:5-11](), [chatkit/README.md:3-4](), [README.md:1-8]()

## Technology Architecture

### Full Stack Architecture Diagram

```mermaid
graph TB
    subgraph Backend["Backend Stack (Python)"]
        Python["Python 3.11+"]
        FastAPI["FastAPI 0.114-0.116"]
        Uvicorn["Uvicorn ASGI Server"]
        OpenAI_SDK["openai ≥1.40"]
        ChatKit_SDK["openai-chatkit 1.4.0-2.0"]
    end
    
    subgraph Frontend["Frontend Stack (Node.js)"]
        Node["Node.js 22"]
        Vite["Vite Build Tool"]
        React["React"]
        TypeScript["TypeScript"]
    end
    
    subgraph DevTools["Development Tools"]
        Ruff["ruff (Python)"]
        Mypy["mypy (Python)"]
        ESLint["ESLint (JavaScript)"]
    end
    
    subgraph External["External Services"]
        OpenAI_API["OpenAI API"]
        Workflows["Hosted Workflows<br/>(managed-chatkit only)"]
    end
    
    Python --> FastAPI
    FastAPI --> Uvicorn
    Python --> OpenAI_SDK
    Python --> ChatKit_SDK
    ChatKit_SDK --> OpenAI_API
    
    Node --> Vite
    Vite --> React
    Vite --> TypeScript
    
    Frontend -->|"HTTP /chatkit"| Backend
    Backend -.->|"managed variant"| Workflows
    
    Ruff -.->|"validates"| Python
    Mypy -.->|"type checks"| Python
    ESLint -.->|"validates"| Frontend
```

**Sources**: [chatkit/backend/pyproject.toml:5-16](), [chatkit/README.md:3-16]()

### Technology Layer Mapping

```mermaid
graph LR
    subgraph User["User Browser"]
        UI["React UI Components"]
    end
    
    subgraph Dev["Development Layer"]
        ViteServer["vite dev server<br/>Port 3000"]
    end
    
    subgraph Backend["Backend Layer"]
        ASGI["uvicorn server<br/>Port 8000"]
        FastAPIApp["FastAPI app"]
        Server["StarterChatServer"]
    end
    
    subgraph Integration["Integration Layer"]
        ChatKitLib["openai-chatkit library"]
        OpenAISDK["openai SDK"]
    end
    
    subgraph External["External Services"]
        API["OpenAI API"]
    end
    
    UI -->|"HTTP Proxy"| ViteServer
    ViteServer -->|"/chatkit"| ASGI
    ASGI --> FastAPIApp
    FastAPIApp --> Server
    Server --> ChatKitLib
    ChatKitLib --> OpenAISDK
    OpenAISDK --> API
```

**Sources**: [chatkit/backend/app/main.py:1-50](), [chatkit/README.md:13-16]()

## Backend Technologies

### Python 3.11+

Python serves as the backend runtime environment. The minimum required version is 3.11, specified in the project configuration.

**Version Requirement**: `requires-python = ">=3.11"`

Python 3.11 provides:
- Performance improvements over 3.10 (up to 25% faster)
- Enhanced error messages with precise location information
- Type hinting improvements used throughout the codebase
- Async/await syntax used by FastAPI and the ChatKit library

**Sources**: [chatkit/backend/pyproject.toml:5]()

### FastAPI 0.114-0.116

FastAPI is the core web framework providing the HTTP API server. It handles request routing, request/response serialization, and middleware integration.

**Version Requirement**: `fastapi>=0.114,<0.116`

#### FastAPI Application Structure

The FastAPI application in `chatkit/backend/app/main.py` provides:

| Component | Implementation | Purpose |
|-----------|----------------|---------|
| Main app instance | `app = FastAPI()` | Core application object |
| CORS middleware | `CORSMiddleware` | Cross-origin request handling for frontend |
| POST endpoint | `/chatkit` | Receives chat requests from frontend |
| Health check | Root route | Application status verification |

#### Request Processing Model

```mermaid
sequenceDiagram
    participant Client as "Frontend (Port 3000)"
    participant FastAPI as "FastAPI App"
    participant Endpoint as "/chatkit Endpoint"
    participant Server as "StarterChatServer"
    
    Client->>FastAPI: "POST /chatkit"
    FastAPI->>Endpoint: "Route request"
    Endpoint->>Server: "respond(payload)"
    Server-->>Endpoint: "StreamingResponse"
    Endpoint-->>FastAPI: "HTTP 200"
    FastAPI-->>Client: "Stream chat events"
```

**Sources**: [chatkit/backend/app/main.py:1-50](), [chatkit/backend/pyproject.toml:7]()

### Uvicorn ASGI Server

Uvicorn is the production-grade ASGI server that runs the FastAPI application. It provides:

**Version Requirement**: `uvicorn[standard]>=0.36,<0.37`

#### Server Configuration

The `[standard]` extra includes:
- **httptools**: High-performance HTTP parser
- **websockets**: WebSocket protocol support
- **uvloop** (on Unix): Fast asyncio event loop
- **watchfiles**: File change detection for development

#### Development Server Launch

The application starts via: `uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload`

| Flag | Value | Purpose |
|------|-------|---------|
| `--host` | `127.0.0.1` | Bind to localhost only (development) |
| `--port` | `8000` | Listen on port 8000 |
| `--reload` | enabled | Auto-restart on code changes |

**Sources**: [chatkit/backend/pyproject.toml:8](), [chatkit/README.md:15-16]()

### OpenAI Python SDK

The OpenAI SDK provides the client library for interacting with OpenAI's APIs.

**Version Requirement**: `openai>=1.40`

#### SDK Integration Points

The SDK is used by the `openai-chatkit` library to:
- Create chat completions via the Chat Completions API
- Stream response chunks in real-time
- Handle authentication with API keys
- Manage model configuration (e.g., `gpt-4o-mini`)

The SDK version `1.40+` ensures compatibility with:
- Streaming responses (`stream=True`)
- Assistant API features
- Chat completion with tools/functions

**Sources**: [chatkit/backend/pyproject.toml:9]()

### openai-chatkit Library

The `openai-chatkit` library is the core integration package that provides the ChatKit server implementation.

**Version Requirement**: `openai-chatkit>=1.4.0,<2`

#### ChatKit Core Components

```mermaid
graph TB
    subgraph ChatKitLibrary["openai-chatkit Library"]
        Agent["Agent Class"]
        AssistantAgent["assistant_agent()"]
        RunStreamed["run_streamed()"]
        Store["Store Protocol"]
        Events["ThreadStreamEvent"]
    end
    
    subgraph Application["Application Code"]
        Server["StarterChatServer"]
        MemoryStore["MemoryStore"]
        ResponseMethod["respond()"]
    end
    
    Application -->|"implements"| Store
    Server -->|"uses"| AssistantAgent
    Server -->|"calls"| RunStreamed
    RunStreamed -->|"yields"| Events
    ResponseMethod -->|"returns"| Events
```

#### Library Features Used

| Feature | Implementation File | Purpose |
|---------|-------------------|---------|
| `Store` protocol | `backend/app/store.py` | Thread and message persistence interface |
| `assistant_agent()` | `backend/app/server.py` | Pre-configured AI agent factory |
| `run_streamed()` | `backend/app/server.py` | Streaming response generation |
| `ThreadStreamEvent` | `backend/app/server.py` | Event types for streaming |
| `simple_to_agent_input()` | `backend/app/server.py` | Message format conversion |

**Sources**: [chatkit/backend/pyproject.toml:10](), [chatkit/backend/app/server.py:1-100]()

## Frontend Technologies

### Node.js 22

Node.js 22 is the required JavaScript runtime environment for the frontend build toolchain and development server.

**Version Requirement**: Node.js 22

Node.js 22 provides:
- ES modules support used by Vite
- Native fetch API used by frontend code
- Performance improvements for build times
- Compatibility with latest npm packages

**Sources**: [chatkit/README.md:1-11]()

### Vite Build Tool

Vite is the frontend build tool and development server, replacing traditional bundlers like webpack.

#### Vite Features Used

| Feature | Implementation | Purpose |
|---------|----------------|---------|
| Dev Server | `vite dev` | Fast hot module replacement |
| Proxy | `/chatkit` → `http://127.0.0.1:8000` | Route API requests to backend |
| React Plugin | `@vitejs/plugin-react` | JSX transformation and Fast Refresh |
| TypeScript | Native support | Type checking during development |
| Production Build | `vite build` | Optimized production bundle |

#### Development Server Configuration

The Vite dev server runs on port 3000 with proxy configuration:

```typescript
proxy: {
  '/chatkit': {
    target: 'http://127.0.0.1:8000',
    changeOrigin: true
  }
}
```

This allows frontend code to make requests to `/chatkit` which are automatically forwarded to the FastAPI backend.

**Sources**: [chatkit/README.md:13-16](), [chatkit/frontend/vite.config.ts:1-20]()

### React

React provides the UI component library and virtual DOM implementation for the frontend.

#### React Architecture in Application

```mermaid
graph TB
    subgraph ReactApp["React Application"]
        Root["Root Component<br/>(App.tsx)"]
        Panel["ChatKitPanel<br/>Component"]
        Config["config.ts<br/>Configuration"]
    end
    
    subgraph ReactFeatures["React Features Used"]
        JSX["JSX Syntax"]
        Hooks["Hooks (useState, useEffect)"]
        Refs["useRef for DOM access"]
    end
    
    subgraph Rendering["Rendering"]
        ReactDOM["ReactDOM.createRoot()"]
        DOMNode["#root element"]
    end
    
    Root --> Panel
    Panel --> Config
    
    Panel --> JSX
    Panel --> Hooks
    Panel --> Refs
    
    ReactDOM --> Root
    ReactDOM --> DOMNode
```

#### React Components

The application uses React for:
- **ChatKitPanel** component: Main chat interface wrapper
- **Component lifecycle**: `useEffect` for initialization
- **DOM integration**: `useRef` to mount ChatKit library
- **Configuration**: Props-based component configuration

**Sources**: [chatkit/frontend/src/components/ChatKitPanel.tsx:1-50](), [chatkit/frontend/src/App.tsx:1-20]()

### TypeScript

TypeScript provides static type checking for the frontend codebase.

#### TypeScript Configuration

The `tsconfig.json` configures:

| Setting | Value | Purpose |
|---------|-------|---------|
| `target` | `ES2020` | Modern JavaScript features |
| `jsx` | `react-jsx` | React 17+ JSX transform |
| `strict` | `true` | Strict type checking enabled |
| `module` | `ESNext` | ES modules system |
| `moduleResolution` | `bundler` | Vite-compatible resolution |

#### Type Safety Benefits

TypeScript provides:
- Compile-time error detection
- IDE autocomplete and IntelliSense
- Type-safe configuration objects
- Interface definitions for API responses

**Sources**: [chatkit/frontend/tsconfig.json:1-30]()

## Development Tools

### Ruff (Python)

Ruff is the Python linter and code formatter used for backend code quality.

**Version Requirement**: `ruff>=0.6.4,<0.7` (dev dependency)

#### Ruff Capabilities

Ruff combines multiple Python tools into one:
- **Linter**: Replaces Flake8, pylint, pycodestyle
- **Formatter**: Replaces Black
- **Import sorter**: Replaces isort
- **Performance**: 10-100x faster than traditional tools

#### CI Integration

The CI pipeline runs two Ruff checks:

```bash
ruff check .          # Lint for code quality issues
ruff format --check . # Verify code formatting
```

**Sources**: [chatkit/backend/pyproject.toml:14-16](), [.github/workflows/ci.yml:30-40]()

### mypy (Python)

mypy is the static type checker for Python, ensuring type safety in the backend codebase.

#### Type Checking Benefits

mypy validates:
- Function parameter types
- Return value types
- Variable assignments
- Protocol implementations (e.g., `Store` protocol)

#### CI Integration

The CI pipeline runs: `mypy . --strict`

The `--strict` flag enables:
- Disallow untyped function definitions
- Disallow incomplete type definitions
- Require explicit return types
- Strict optional checking

**Sources**: [.github/workflows/ci.yml:40-50]()

### ESLint (JavaScript)

ESLint validates JavaScript and TypeScript code in the frontend.

#### ESLint Configuration

The frontend uses:
- **eslint.config.js**: ESLint 9 flat config format
- **TypeScript ESLint**: Type-aware linting rules
- **React Rules**: React-specific best practices

#### CI Integration

The CI pipeline runs: `npm run lint`

This checks for:
- Unused variables
- Missing dependencies in React hooks
- TypeScript type errors
- Code style violations

**Sources**: [.github/workflows/ci.yml:60-70](), [chatkit/frontend/eslint.config.js:1-20]()

## OpenAI Integration

### OpenAI API

Both starter applications integrate with the OpenAI API for conversational AI capabilities.

#### API Authentication

The backend requires the `OPENAI_API_KEY` environment variable:

```bash
export OPENAI_API_KEY=sk-proj-...
```

This key authenticates all requests to OpenAI's API endpoints.

#### API Usage Pattern

```mermaid
sequenceDiagram
    participant App as "Application"
    participant ChatKit as "openai-chatkit"
    participant SDK as "openai SDK"
    participant API as "OpenAI API"
    
    App->>ChatKit: "assistant_agent(model='gpt-4o-mini')"
    App->>ChatKit: "run_streamed(messages)"
    ChatKit->>SDK: "client.chat.completions.create()"
    SDK->>API: "POST /v1/chat/completions"
    API-->>SDK: "Stream response chunks"
    SDK-->>ChatKit: "Delta events"
    ChatKit-->>App: "ThreadStreamEvent"
```

#### Model Configuration

The default model is `gpt-4o-mini`, configured in the agent:

```python
assistant_agent(
    model="gpt-4o-mini",
    instructions="You are a helpful assistant."
)
```

**Sources**: [chatkit/README.md:20](), [chatkit/backend/app/server.py:1-50](), [chatkit/.env.example:1-3]()

### Domain Keys

Domain keys authenticate frontend requests to the ChatKit API.

**Environment Variables**:
- `VITE_CHATKIT_API_DOMAIN_KEY`: Frontend domain authentication key
- Default: `domain_pk_localhost_dev` (development)
- Production: Register domain key in OpenAI dashboard

Domain keys:
- Restrict which domains can make ChatKit API calls
- Prevent unauthorized usage
- Track usage by domain

**Sources**: [chatkit/README.md:22-26](), [chatkit/.env.example:3]()

## Technology Communication Flow

### Backend-Frontend Integration

The frontend and backend communicate via HTTP:

```mermaid
graph LR
    subgraph Frontend["Frontend (Port 3000)"]
        Browser["Browser"]
        ViteDev["Vite Dev Server"]
        Proxy["Proxy Middleware"]
    end
    
    subgraph Backend["Backend (Port 8000)"]
        Uvicorn["Uvicorn Server"]
        FastAPI["FastAPI App"]
        Endpoint["/chatkit Endpoint"]
    end
    
    Browser -->|"HTTP Request"| ViteDev
    ViteDev -->|"/chatkit/*"| Proxy
    Proxy -->|"Forward to :8000"| Uvicorn
    Uvicorn --> FastAPI
    FastAPI --> Endpoint
```

#### Development Proxy Configuration

In development, the Vite proxy forwards `/chatkit` requests:

| Setting | Value | Purpose |
|---------|-------|---------|
| Proxy path | `/chatkit` | Intercept these requests |
| Target | `http://127.0.0.1:8000` | Forward to FastAPI backend |
| Change origin | `true` | Rewrite host header |

This allows the frontend at `localhost:3000` to call the backend at `localhost:8000` without CORS issues.

**Sources**: [chatkit/README.md:15-16](), [chatkit/frontend/vite.config.ts:1-20]()

## Environment Variables

### Backend Environment Variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API authentication |

The backend reads this from the shell environment or `.env.local` file at the repository root.

**Sources**: [chatkit/README.md:20](), [chatkit/.env.example:1]()

### Frontend Environment Variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `VITE_CHATKIT_API_URL` | No | `/chatkit` | Backend API endpoint URL |
| `VITE_CHATKIT_API_DOMAIN_KEY` | No | `domain_pk_localhost_dev` | Domain authentication key |

Frontend variables must be prefixed with `VITE_` to be exposed to client-side code.

**Sources**: [chatkit/README.md:21-22](), [chatkit/.env.example:2-3]()

### Environment File Structure

The `.env.local` file at the repository root contains:

```bash
OPENAI_API_KEY=sk-proj-...
VITE_CHATKIT_API_URL=/chatkit
VITE_CHATKIT_API_DOMAIN_KEY=domain_pk_localhost_dev
```

This file is:
- Ignored by git (`.gitignore`)
- Loaded by both backend and frontend during development
- Referenced by Vite for `VITE_*` variables
- Read by Python's `os.environ` for backend variables

**Sources**: [chatkit/.env.example:1-3](), [chatkit/.gitignore:1-4]()

## Dependency Version Strategy

### Backend Dependency Versioning

Python dependencies use PEP 440 version specifiers:

| Package | Specifier | Accepts | Rationale |
|---------|-----------|---------|-----------|
| `fastapi` | `>=0.114,<0.116` | 0.114.x - 0.115.x | Pin to known compatible minors |
| `uvicorn` | `>=0.36,<0.37` | 0.36.x only | Server stability critical |
| `openai` | `>=1.40` | 1.40.0+ | Accept new API features |
| `openai-chatkit` | `>=1.4.0,<2` | 1.4.0 - 1.x.x | Major version stability |
| `ruff` | `>=0.6.4,<0.7` | 0.6.4+ | Development tool flexibility |

#### Version Strategy Diagram

```mermaid
graph TB
    subgraph Production["Production Dependencies"]
        FastAPI["fastapi<br/>>=0.114,<0.116"]
        Uvicorn["uvicorn<br/>>=0.36,<0.37"]
        OpenAI["openai<br/>>=1.40"]
        ChatKit["openai-chatkit<br/>>=1.4.0,<2"]
    end
    
    subgraph Development["Dev Dependencies"]
        Ruff["ruff<br/>>=0.6.4,<0.7"]
    end
    
    subgraph Strategy["Version Control Strategy"]
        Tight["Tight Range<br/>Minor version pinning"]
        Loose["Loose Range<br/>Major version only"]
        Open["Open Range<br/>Minimum only"]
    end
    
    FastAPI --> Tight
    Uvicorn --> Tight
    ChatKit --> Loose
    OpenAI --> Open
    Ruff --> Tight
```

**Sources**: [chatkit/backend/pyproject.toml:6-16]()

### Frontend Dependency Versioning

Frontend dependencies use npm semantic versioning:

- **Vite**: Latest stable version (managed by npm)
- **React**: Latest stable version (managed by npm)
- **TypeScript**: Latest stable version (managed by npm)
- **ESLint**: Latest stable version (managed by npm)

The frontend uses `npm install` to fetch latest compatible versions within major version constraints.

**Sources**: [chatkit/frontend/package.json:1-30]()

## Technology Integration Summary

The five core technologies integrate as follows:

1. **Next.js** orchestrates the application, managing routing, server/client boundaries, and build process
2. **React 19** provides the component model and rendering engine
3. **TypeScript** enforces type safety across the entire codebase
4. **ChatKit** supplies the chat interface and OpenAI integration
5. **Tailwind CSS** handles styling through utility classes and CSS variables

Each technology's configuration file serves as the integration point:
- [next.config.ts:1-12]() - Next.js framework configuration
- [tsconfig.json:1-27]() - TypeScript compiler options
- [package.json:1-32]() - Dependency manifest and version locking

---

# Page: Repository Structure

# Repository Structure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [chatkit/.env.example](chatkit/.env.example)
- [chatkit/.gitignore](chatkit/.gitignore)
- [chatkit/README.md](chatkit/README.md)
- [chatkit/backend/.gitignore](chatkit/backend/.gitignore)
- [chatkit/backend/app/__init__.py](chatkit/backend/app/__init__.py)

</details>



This document describes the directory layout and organization of the OpenAI ChatKit Starter repository. The repository contains two independent starter applications demonstrating different ChatKit integration patterns: self-hosted and managed.

For details on specific technologies used, see [Key Technologies (1.2)](#1.2). For information on integration patterns, see [Two Integration Patterns (1.1)](#1.1).

---

## Purpose and Scope

The repository is organized into two top-level application directories, each containing a complete full-stack application with independent backend (FastAPI + Python) and frontend (Vite + React) implementations. Each application demonstrates a different ChatKit integration approach while following identical architectural patterns. Understanding this structure is essential for choosing the right integration pattern and navigating the codebase.

---

## High-Level Repository Structure

```mermaid
graph TB
    ROOT["openai-chatkit-starter-app/"]
    
    README["README.md"]
    GITHUB[".github/"]
    WORKFLOWS[".github/workflows/"]
    CI_YAML[".github/workflows/ci.yaml"]
    
    CHATKIT["chatkit/"]
    CK_README["chatkit/README.md"]
    CK_BACKEND["chatkit/backend/"]
    CK_FRONTEND["chatkit/frontend/"]
    CK_PKG["chatkit/package.json"]
    CK_GIT["chatkit/.gitignore"]
    CK_ENV["chatkit/.env.example"]
    
    MANAGED["managed-chatkit/"]
    MCK_BACKEND["managed-chatkit/backend/"]
    MCK_FRONTEND["managed-chatkit/frontend/"]
    
    ROOT --> README
    ROOT --> GITHUB
    ROOT --> CHATKIT
    ROOT --> MANAGED
    
    GITHUB --> WORKFLOWS
    WORKFLOWS --> CI_YAML
    
    CHATKIT --> CK_README
    CHATKIT --> CK_BACKEND
    CHATKIT --> CK_FRONTEND
    CHATKIT --> CK_PKG
    CHATKIT --> CK_GIT
    CHATKIT --> CK_ENV
    
    MANAGED --> MCK_BACKEND
    MANAGED --> MCK_FRONTEND
```

**Sources:** [README.md:1-9](), [chatkit/README.md:1-33]()

---

## Top-Level Organization

The repository root contains two independent application directories and shared documentation:

| Directory/File | Purpose | Details |
|----------------|---------|---------|
| `README.md` | Root documentation | Describes both starter applications and links to their READMEs |
| `.github/workflows/` | CI/CD configuration | Contains `ci.yaml` for automated testing |
| `chatkit/` | Self-hosted integration | Complete application with backend, frontend, and configuration |
| `managed-chatkit/` | Managed integration | Complete application using hosted workflows |

**Sources:** [README.md:1-9]()

---

## `chatkit/` Directory Structure

The self-hosted ChatKit integration is organized as a full-stack application with independent backend and frontend implementations.

### Directory Layout

```mermaid
graph TB
    CHATKIT["chatkit/"]
    
    README["README.md"]
    PKG["package.json"]
    GIT[".gitignore"]
    ENV[".env.example"]
    
    BACKEND["backend/"]
    BE_APP["backend/app/"]
    BE_INIT["backend/app/__init__.py"]
    BE_MAIN["backend/app/main.py"]
    BE_SERVER["backend/app/server.py"]
    BE_PYPROJECT["backend/pyproject.toml"]
    BE_GIT["backend/.gitignore"]
    
    FRONTEND["frontend/"]
    FE_SRC["frontend/src/"]
    FE_MAIN["frontend/src/main.tsx"]
    FE_CONFIG["frontend/src/lib/config.ts"]
    FE_PANEL["frontend/src/components/ChatKitPanel.tsx"]
    FE_PKG["frontend/package.json"]
    FE_VITE["frontend/vite.config.ts"]
    FE_TS["frontend/tsconfig.json"]
    
    CHATKIT --> README
    CHATKIT --> PKG
    CHATKIT --> GIT
    CHATKIT --> ENV
    CHATKIT --> BACKEND
    CHATKIT --> FRONTEND
    
    BACKEND --> BE_APP
    BACKEND --> BE_PYPROJECT
    BACKEND --> BE_GIT
    BE_APP --> BE_INIT
    BE_APP --> BE_MAIN
    BE_APP --> BE_SERVER
    
    FRONTEND --> FE_SRC
    FRONTEND --> FE_PKG
    FRONTEND --> FE_VITE
    FRONTEND --> FE_TS
    FE_SRC --> FE_MAIN
    FE_SRC --> FE_CONFIG
    FE_SRC --> FE_PANEL
```

**Sources:** [chatkit/README.md:1-33](), [chatkit/.gitignore:1-4](), [chatkit/backend/.gitignore:1-10]()

### Root-Level Configuration (`chatkit/`)

| File | Purpose |
|------|---------|
| `README.md` | Application-specific documentation, setup instructions |
| `package.json` | Root package configuration, defines `npm run dev` command |
| `.gitignore` | Excludes `node_modules/` and `.env*` files (except `.env.example`) |
| `.env.example` | Template showing required environment variables |

The root `package.json` defines the `dev` script that launches both backend and frontend concurrently using `concurrently` package.

**Sources:** [chatkit/README.md:1-33](), [chatkit/.gitignore:1-4](), [chatkit/.env.example:1-3]()

### Backend Structure (`chatkit/backend/`)

The FastAPI backend is organized as a Python package:

```mermaid
graph TB
    BACKEND["chatkit/backend/"]
    
    APP_PKG["app/"]
    INIT["app/__init__.py"]
    MAIN["app/main.py"]
    SERVER["app/server.py"]
    
    PYPROJECT["pyproject.toml"]
    GITIGNORE[".gitignore"]
    
    MAIN_APP["FastAPI() application"]
    ENDPOINT["/chatkit endpoint"]
    STARTER_SERVER["StarterChatServer"]
    MEMORY_STORE["MemoryStore"]
    ASSISTANT_AGENT["assistant_agent"]
    
    BACKEND --> APP_PKG
    BACKEND --> PYPROJECT
    BACKEND --> GITIGNORE
    
    APP_PKG --> INIT
    APP_PKG --> MAIN
    APP_PKG --> SERVER
    
    MAIN --> MAIN_APP
    MAIN --> ENDPOINT
    SERVER --> STARTER_SERVER
    SERVER --> MEMORY_STORE
    SERVER --> ASSISTANT_AGENT
```

| File/Directory | Purpose | Key Contents |
|----------------|---------|--------------|
| `app/__init__.py` | Package marker | Minimal docstring |
| `app/main.py` | FastAPI entrypoint | Defines `FastAPI()` app, `/chatkit` endpoint, CORS config |
| `app/server.py` | ChatKit server logic | `StarterChatServer`, `MemoryStore`, `assistant_agent` |
| `pyproject.toml` | Python dependencies | FastAPI, uvicorn, openai, openai-chatkit |
| `.gitignore` | Python-specific ignores | `__pycache__/`, `.venv/`, `.env`, `.ruff_cache/` |

**Sources:** [chatkit/backend/.gitignore:1-10](), [chatkit/backend/app/__init__.py:1-2](), [chatkit/README.md:15-16]()

### Frontend Structure (`chatkit/frontend/`)

The Vite + React frontend follows a standard single-page application structure:

```mermaid
graph TB
    FRONTEND["chatkit/frontend/"]
    
    SRC["src/"]
    MAIN["src/main.tsx"]
    APP["src/App.tsx"]
    
    LIB["src/lib/"]
    CONFIG["src/lib/config.ts"]
    
    COMPONENTS["src/components/"]
    PANEL["src/components/ChatKitPanel.tsx"]
    
    PKG["package.json"]
    VITE["vite.config.ts"]
    TS["tsconfig.json"]
    
    FRONTEND --> SRC
    FRONTEND --> PKG
    FRONTEND --> VITE
    FRONTEND --> TS
    
    SRC --> MAIN
    SRC --> APP
    SRC --> LIB
    SRC --> COMPONENTS
    
    LIB --> CONFIG
    COMPONENTS --> PANEL
```

| File/Directory | Purpose | Key Contents |
|----------------|---------|--------------|
| `src/main.tsx` | Application entrypoint | Renders React app into DOM |
| `src/App.tsx` | Root React component | Application container |
| `src/lib/config.ts` | Configuration constants | API URL, domain key, UI settings |
| `src/components/ChatKitPanel.tsx` | Chat interface component | Main UI integration point |
| `package.json` | Frontend dependencies | React, Vite, TypeScript, ESLint |
| `vite.config.ts` | Vite build configuration | Dev server proxy to `/chatkit` |
| `tsconfig.json` | TypeScript configuration | Compiler options |

**Sources:** [chatkit/README.md:15-16, 30-32]()

---

## `managed-chatkit/` Directory Structure

The managed ChatKit integration follows an identical structure to `chatkit/` but uses hosted workflows instead of self-hosted server logic. The directory organization mirrors `chatkit/`:

```
managed-chatkit/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── (managed workflow integration)
│   ├── pyproject.toml
│   └── .gitignore
└── frontend/
    ├── src/
    │   ├── main.tsx
    │   ├── App.tsx
    │   ├── lib/config.ts
    │   └── components/ChatKitPanel.tsx
    ├── package.json
    ├── vite.config.ts
    └── tsconfig.json
```

The key difference is in the backend implementation, which integrates with hosted workflows rather than implementing `StarterChatServer` and `MemoryStore` locally. See [Managed ChatKit (4)](#4) for details on architectural differences.

**Sources:** [README.md:8-9]()

---

## Root-Level Configuration Files

The repository root contains configuration files that control build, development, and deployment behavior.

### Development & Build Configuration

| File | Purpose | Referenced By |
|------|---------|---------------|
| `package.json` | Defines dependencies, scripts, and project metadata | npm, CI workflow |
| `package-lock.json` | Locks exact dependency versions for reproducible installs | npm ci |
| `tsconfig.json` | TypeScript compiler configuration | TypeScript compiler, Next.js |
| `next.config.ts` | Next.js framework configuration | Next.js build system |
| `postcss.config.mjs` | PostCSS plugin configuration for CSS processing | Next.js build system |
| `tailwind.config.ts` | Tailwind CSS framework configuration | PostCSS, build system |
| `.eslintrc.json` | ESLint code quality rules | ESLint, CI workflow |

**Sources:** Architecture diagrams (Diagram 2, Diagram 5)

### Environment & Version Control

| File | Purpose | Tracked in Git |
|------|---------|----------------|
| `.env.example` | Template for environment variables | Yes |
| `.env.local` | Actual environment variables with secrets | No (in .gitignore) |
| `.gitignore` | Specifies intentionally untracked files | Yes |

The `.env.example` file ([.env.example:1-3]()) provides a template showing required environment variables without exposing actual secrets. Developers copy this to `.env.local` and fill in real values:

```
OPENAI_API_KEY=sk-...
NEXT_PUBLIC_CHATKIT_WORKFLOW_ID=wflow_...
```

The `.gitignore` file ([.gitignore:34-35]()) explicitly excludes all `.env*` files except `.env.example`, ensuring secrets remain local.

**Sources:** [.gitignore:33-35](), [README.md:21-35](), Architecture diagrams (Diagram 6)

---

## Build Outputs & Generated Directories

The following directories are generated during development or build processes and are excluded from version control:

| Directory | Purpose | When Generated | Gitignored |
|-----------|---------|----------------|------------|
| `node_modules/` | Installed npm packages | `npm install` or `npm ci` | Yes ([.gitignore:4]()) |
| `.next/` | Next.js build output and cache | `npm run dev` or `npm run build` | Yes ([.gitignore:17]()) |
| `out/` | Static export output (if configured) | `npm run build` with output: 'export' | Yes ([.gitignore:18]()) |
| `coverage/` | Test coverage reports | `npm run test` (if configured) | Yes ([.gitignore:14]()) |

**Sources:** [.gitignore:3-21](), [README.md:17-19, 47-50]()

---

## File Organization Patterns

### Next.js App Router Conventions

The project follows Next.js App Router file naming conventions:

```mermaid
graph TB
    subgraph "Route Definitions"
        PAGE_ROOT["app/page.tsx<br/>(Route: /)"]
        LAYOUT_ROOT["app/layout.tsx<br/>(Applies to all routes)"]
    end
    
    subgraph "API Routes"
        API_SESSION["app/api/create-session/route.ts<br/>(Route: POST /api/create-session)"]
    end
    
    subgraph "Special Files"
        GLOBALS["app/globals.css<br/>(Global styles)"]
    end
    
    LAYOUT_ROOT -.->|"Wraps"| PAGE_ROOT
    PAGE_ROOT --> APP_TSX["App.tsx<br/>(Not a route)"]
```

**Key conventions:**
- `page.tsx` - Defines a route at that directory level
- `layout.tsx` - Defines a layout that wraps all child routes
- `route.ts` in `api/` - Defines API endpoint handlers (GET, POST, etc.)
- Other `.tsx` files - Regular components, not routes

**Sources:** [app/page.tsx:1-6](), Next.js documentation

### Component Organization

Components are organized by function rather than type:

- **Primary components** (`ChatKitPanel`, `ErrorOverlay`) are in `components/`
- **Page-specific components** (`App`) are co-located with their pages in `app/`
- **Shared hooks** are in `hooks/`
- **Configuration** is in `lib/`

This structure keeps related code together while maintaining clear separation of concerns.

**Sources:** [README.md:44, 55-56](), Architecture diagrams (Diagram 3)

---

## Summary: Directory Purpose Mapping

| Directory | Primary Purpose | Key Consumers |
|-----------|----------------|---------------|
| `app/` | Routing, layouts, pages, API endpoints | Next.js App Router |
| `components/` | Reusable UI components | Pages, other components |
| `hooks/` | Custom React hooks for stateful logic | Components |
| `lib/` | Configuration, utilities, constants | All application code |
| `public/` | Static assets served at root path | HTML, CSS, components |

This organization supports the application's architecture by clearly separating routing concerns, reusable components, custom hooks, configuration, and static assets. The structure is designed for a small-to-medium application and can be extended by adding subdirectories within each major category as the codebase grows.

**Sources:** [README.md:1-61](), [.gitignore:1-43](), Architecture diagrams (all)

---

# Page: Getting Started

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [chatkit/.env.example](chatkit/.env.example)
- [chatkit/.gitignore](chatkit/.gitignore)
- [chatkit/README.md](chatkit/README.md)
- [chatkit/backend/.gitignore](chatkit/backend/.gitignore)
- [chatkit/backend/app/__init__.py](chatkit/backend/app/__init__.py)
- [chatkit/backend/scripts/run.sh](chatkit/backend/scripts/run.sh)

</details>



This document provides step-by-step instructions for setting up and running either of the two ChatKit starter applications included in this repository. It covers prerequisite software, dependency installation, environment configuration, and starting the development servers.

For an overview of the two integration patterns (self-hosted vs. managed), see [Two Integration Patterns](#1.1). For detailed architecture and implementation documentation, see [Self-Hosted ChatKit](#3) or [Managed ChatKit](#4).

## Overview

Both starter applications (`chatkit/` and `managed-chatkit/`) follow identical setup procedures. The process involves installing dependencies, configuring environment variables, and starting concurrent development servers for the backend and frontend.

**Setup Workflow**

```mermaid
graph LR
    A["Clone Repository"]
    B["Navigate to<br/>chatkit/ or<br/>managed-chatkit/"]
    C["Install Dependencies<br/>npm install"]
    D["Configure .env.local"]
    E["Start Servers<br/>npm run dev"]
    F["Access UI<br/>http://127.0.0.1:3000"]
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
```

Sources: [chatkit/README.md:1-33]()

---

## Prerequisites

The following software must be installed on your system before proceeding:

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.11 or higher | Backend FastAPI server execution |
| Node.js | 22 | Frontend Vite build and development server |
| npm | Included with Node.js | Package management for frontend and orchestration |
| Git | Any recent version | Repository cloning |
| OpenAI API Key | N/A | Authentication with OpenAI services |

**Verification Commands**

```bash
# Check Python version
python --version  # Should output Python 3.11.x or higher

# Check Node.js version
node --version    # Should output v22.x.x

# Check npm version
npm --version     # Should output 10.x.x or higher
```

Sources: [chatkit/README.md:18-26](), [chatkit/backend/scripts/run.sh:14]()

---

## Choosing a Starter Application

The repository contains two independent starter applications:

| Directory | Integration Pattern | Use Case |
|-----------|-------------------|----------|
| `chatkit/` | Self-hosted | Full control over infrastructure, all logic runs locally |
| `managed-chatkit/` | Managed workflows | Reduced operational complexity, uses hosted workflows |

For detailed comparison of these patterns, see [Two Integration Patterns](#1.1).

**All subsequent instructions apply to both applications unless explicitly noted.**

Sources: [chatkit/README.md:1-4]()

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/openai/openai-chatkit-starter-app.git
cd openai-chatkit-starter-app
```

### 2. Navigate to Target Application

Choose either:

```bash
cd chatkit/          # For self-hosted integration
```

or

```bash
cd managed-chatkit/  # For managed integration
```

### 3. Install Dependencies

From the chosen application directory, run:

```bash
npm install
```

This command performs the following operations:

**Dependency Installation Flow**

```mermaid
graph TD
    A["npm install"]
    B["Install frontend<br/>node_modules/"]
    C["Create Python venv<br/>backend/.venv/"]
    D["Install backend<br/>dependencies"]
    E["Ready for development"]
    
    A --> B
    A --> C
    C --> D
    B --> E
    D --> E
```

The `npm install` command:
1. Installs frontend dependencies specified in `package.json` into `node_modules/`
2. Creates a Python virtual environment at `backend/.venv/`
3. Installs backend dependencies from `backend/pyproject.toml` including `fastapi`, `uvicorn`, `openai`, and `openai-chatkit`

Sources: [chatkit/README.md:8-10](), [chatkit/backend/scripts/run.sh:12-20]()

---

## Environment Configuration

### Required Environment Variables

Three environment variables control the application's behavior:

| Variable | Required | Default Value | Purpose |
|----------|----------|---------------|---------|
| `OPENAI_API_KEY` | **Yes** | None | Authenticates requests to OpenAI API |
| `VITE_CHATKIT_API_URL` | No | `/chatkit` | Frontend proxy endpoint to backend |
| `VITE_CHATKIT_API_DOMAIN_KEY` | No | `domain_pk_localhost_dev` | Domain authentication key for ChatKit |

### Configuration File: `.env.local`

Create a `.env.local` file at the **repository root** (not inside `chatkit/` or `managed-chatkit/`):

```bash
# From repository root
touch .env.local
```

Add the following content:

```bash
OPENAI_API_KEY=sk-proj-your-actual-key-here
VITE_CHATKIT_API_URL=/chatkit
VITE_CHATKIT_API_DOMAIN_KEY=domain_pk_localhost_dev
```

**Environment Variable Loading**

```mermaid
graph TB
    ENV_FILE[".env.local<br/>(repository root)"]
    
    subgraph Backend["Backend Process"]
        RUN_SCRIPT["scripts/run.sh"]
        UVICORN["uvicorn app.main:app"]
        FASTAPI["FastAPI Application"]
    end
    
    subgraph Frontend["Frontend Process"]
        VITE["Vite Dev Server"]
        REACT["React Application"]
    end
    
    ENV_FILE -->|"sources<br/>OPENAI_API_KEY"| RUN_SCRIPT
    RUN_SCRIPT -->|"passes env"| UVICORN
    UVICORN --> FASTAPI
    
    ENV_FILE -->|"loads<br/>VITE_* vars"| VITE
    VITE --> REACT
```

### Environment Variable Details

**`OPENAI_API_KEY`**

Obtain an API key from the [OpenAI Platform dashboard](https://platform.openai.com/api-keys). The key must have access to chat completion models (e.g., `gpt-4o-mini`).

The backend loading mechanism checks for this variable in the following order:
1. Shell environment (`export OPENAI_API_KEY=...`)
2. `.env.local` file at repository root

See [chatkit/backend/scripts/run.sh:24-36]() for the loading implementation.

**`VITE_CHATKIT_API_URL`**

Defaults to `/chatkit`, which uses the Vite dev server's proxy to forward requests to the FastAPI backend at `http://127.0.0.1:8000/chatkit`. For production deployments, set this to the full URL of your deployed backend.

**`VITE_CHATKIT_API_DOMAIN_KEY`**

Defaults to `domain_pk_localhost_dev` for local development. For production deployments, register a domain key in the OpenAI dashboard and update this value.

### Example Configuration File

```bash
# .env.local example
OPENAI_API_KEY=sk-proj-abcd1234efgh5678ijkl9012mnop3456qrst7890uvwx
VITE_CHATKIT_API_URL=/chatkit
VITE_CHATKIT_API_DOMAIN_KEY=domain_pk_localhost_dev
```

Sources: [chatkit/README.md:18-26](), [chatkit/.env.example:1-3](), [chatkit/backend/scripts/run.sh:22-36]()

---

## Running the Application

### Start Development Servers

From the application directory (`chatkit/` or `managed-chatkit/`), run:

```bash
npm run dev
```

This single command starts both the backend and frontend concurrently.

**Development Server Architecture**

```mermaid
graph TB
    CMD["npm run dev"]
    
    subgraph Backend["Backend Server"]
        SCRIPT["scripts/run.sh"]
        VENV["Activates .venv"]
        UVICORN["uvicorn app.main:app<br/>--reload"]
        PORT8000["http://127.0.0.1:8000"]
        ENDPOINT["/chatkit endpoint"]
    end
    
    subgraph Frontend["Frontend Server"]
        VITE_CMD["vite dev"]
        PORT3000["http://127.0.0.1:3000"]
        PROXY["Proxy /chatkit<br/>→ :8000"]
    end
    
    subgraph Browser["Browser"]
        UI["React UI"]
    end
    
    CMD -->|"starts"| SCRIPT
    CMD -->|"starts"| VITE_CMD
    
    SCRIPT --> VENV
    VENV --> UVICORN
    UVICORN --> PORT8000
    PORT8000 --> ENDPOINT
    
    VITE_CMD --> PORT3000
    PORT3000 --> PROXY
    
    UI -->|"HTTP requests"| PORT3000
    PROXY -->|"proxies to"| ENDPOINT
```

### What Happens During Startup

1. **Backend initialization** [chatkit/backend/scripts/run.sh:1-40]():
   - Creates Python virtual environment at `backend/.venv/` if not present
   - Activates virtual environment
   - Installs backend dependencies in editable mode
   - Loads `OPENAI_API_KEY` from `.env.local` if not in shell environment
   - Starts `uvicorn` server on `127.0.0.1:8000` with hot-reload enabled

2. **Frontend initialization**:
   - Starts Vite development server on `127.0.0.1:3000`
   - Configures proxy to forward `/chatkit` requests to backend
   - Enables hot-module replacement for React components

### Verification

Once both servers start successfully, you should see output similar to:

```
Starting ChatKit backend on http://127.0.0.1:8000 ...
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345]

VITE v5.x.x  ready in 234 ms
➜  Local:   http://127.0.0.1:3000/
➜  Network: use --host to expose
```

### Accessing the Application

Open a web browser and navigate to:

```
http://127.0.0.1:3000
```

The ChatKit UI should load, allowing you to start a conversation with the AI assistant.

**Request Flow During Operation**

```mermaid
sequenceDiagram
    participant Browser
    participant ViteProxy as "Vite Proxy<br/>:3000/chatkit"
    participant FastAPI as "FastAPI Backend<br/>:8000/chatkit"
    participant OpenAI as "OpenAI API"
    
    Browser->>ViteProxy: "POST /chatkit"
    Note over ViteProxy: "Proxies request"
    ViteProxy->>FastAPI: "POST http://127.0.0.1:8000/chatkit"
    FastAPI->>OpenAI: "Chat completion request"
    OpenAI-->>FastAPI: "Streaming response"
    FastAPI-->>ViteProxy: "Server-sent events"
    ViteProxy-->>Browser: "Streaming response"
    Note over Browser: "UI updates in real-time"
```

Sources: [chatkit/README.md:13-16](), [chatkit/backend/scripts/run.sh:38-39]()

---

## Troubleshooting Common Issues

### Backend Fails to Start

**Symptom**: Error message `Set OPENAI_API_KEY in your environment or in .env.local`

**Solution**: Ensure `.env.local` exists at the repository root with a valid `OPENAI_API_KEY`.

**Verification**:
```bash
# From repository root
cat .env.local | grep OPENAI_API_KEY
```

### Port Already in Use

**Symptom**: `Address already in use` error for port 8000 or 3000

**Solution**: Stop the conflicting process or change the port:

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process (replace PID with actual process ID)
kill -9 <PID>
```

### Python Version Mismatch

**Symptom**: `Python 3.11 or higher is required`

**Solution**: Install Python 3.11+ and ensure it's in your PATH:

```bash
python --version  # Verify version
```

If using multiple Python versions, you may need to explicitly use `python3.11` or configure a version manager like `pyenv`.

### Dependencies Not Installing

**Symptom**: `npm install` fails or backend dependencies missing

**Solution**: 
1. Clear `node_modules/` and retry:
   ```bash
   rm -rf node_modules/
   npm install
   ```

2. Clear Python virtual environment and retry:
   ```bash
   rm -rf backend/.venv/
   npm install
   ```

Sources: [chatkit/backend/scripts/run.sh:33-36](), [chatkit/.gitignore:1-4](), [chatkit/backend/.gitignore:1-9]()

---

## Next Steps

After successfully running the application:

1. **Explore the architecture**: See [Self-Hosted ChatKit](#3) or [Managed ChatKit](#4) for detailed implementation documentation

2. **Customize the application**: See [Customization Guide](#3.5) for guidance on:
   - Replacing `MemoryStore` with persistent storage
   - Modifying UI configuration in [frontend/src/lib/config.ts]()
   - Adjusting layout in [frontend/src/components/ChatKitPanel.tsx]()

3. **Understand the request flow**: See [Request Flow & Data Model](#3.4) for a detailed trace of how messages are processed

4. **Prepare for deployment**: See [Deployment Considerations](#8) for production environment guidance

Sources: [chatkit/README.md:28-32]()

---

# Page: Installation & Prerequisites

# Installation & Prerequisites

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [chatkit/.env.example](chatkit/.env.example)
- [chatkit/.gitignore](chatkit/.gitignore)
- [chatkit/README.md](chatkit/README.md)
- [chatkit/backend/.gitignore](chatkit/backend/.gitignore)
- [chatkit/backend/app/__init__.py](chatkit/backend/app/__init__.py)
- [chatkit/backend/pyproject.toml](chatkit/backend/pyproject.toml)

</details>



This page describes the system requirements and installation steps for running either ChatKit starter application (`chatkit/` or `managed-chatkit/`). Both applications share identical prerequisites and installation procedures. This document covers software installation only; for environment configuration, see [Environment Configuration](#2.2), and for instructions on running the applications, see [Running the Application](#2.3).

## Purpose and Scope

This page provides:
- System requirements (Python and Node.js versions)
- Step-by-step installation instructions for backend and frontend dependencies
- Verification procedures to confirm successful installation

This document does **not** cover environment variable configuration, API key setup, or starting the development servers, which are addressed in subsequent sections.

---

## System Requirements

Both starter applications require the following software to be installed on your development machine:

| Component | Minimum Version | Purpose |
|-----------|----------------|---------|
| **Python** | 3.11 or higher | Backend FastAPI server and ChatKit integration |
| **Node.js** | 22 | Frontend build tooling (Vite) and package management |
| **npm** | Included with Node.js | JavaScript package manager |
| **pip** | Included with Python | Python package manager |

### Operating System Compatibility

The starter applications are platform-independent and run on:
- **Linux** (all distributions)
- **macOS** (Intel and Apple Silicon)
- **Windows** (with standard Python and Node.js installations)

**Sources:** High-level architecture diagrams, [chatkit/backend/pyproject.toml:5]()

---

## Installation Architecture Overview

```mermaid
graph TB
    subgraph Prerequisites["System Prerequisites"]
        PYTHON["Python 3.11+<br/>Interpreter"]
        NODE["Node.js 22<br/>Runtime"]
    end
    
    subgraph Backend_Install["Backend Installation"]
        VENV["Virtual Environment<br/>.venv/"]
        PIP_INSTALL["pip install<br/>from pyproject.toml"]
        BE_DEPS["Backend Dependencies<br/>fastapi, uvicorn, openai, openai-chatkit"]
    end
    
    subgraph Frontend_Install["Frontend Installation"]
        NPM_INSTALL["npm install<br/>from package.json"]
        FE_DEPS["Frontend Dependencies<br/>React, Vite, TypeScript"]
        NODE_MODULES["node_modules/"]
    end
    
    subgraph Both_Apps["Applies to Both"]
        CHATKIT["chatkit/"]
        MANAGED["managed-chatkit/"]
    end
    
    PYTHON --> VENV
    VENV --> PIP_INSTALL
    PIP_INSTALL --> BE_DEPS
    
    NODE --> NPM_INSTALL
    NPM_INSTALL --> FE_DEPS
    FE_DEPS --> NODE_MODULES
    
    BE_DEPS --> CHATKIT
    NODE_MODULES --> CHATKIT
    BE_DEPS --> MANAGED
    NODE_MODULES --> MANAGED
```

**Installation Flow**: Both applications require separate backend and frontend dependency installation. The backend uses Python's virtual environment pattern with pip, while the frontend uses Node.js with npm.

**Sources:** [chatkit/README.md:6-16](), [chatkit/backend/pyproject.toml:1-21](), high-level architecture diagrams

---

## Backend Installation

The backend is a Python application using FastAPI. Installation requires creating an isolated virtual environment and installing dependencies specified in `pyproject.toml`.

### Step 1: Navigate to Backend Directory

For the self-hosted variant:
```bash
cd chatkit/backend
```

For the managed variant:
```bash
cd managed-chatkit/backend
```

### Step 2: Create Python Virtual Environment

Create an isolated Python environment to avoid conflicts with system packages:

```bash
python -m venv .venv
```

This creates a `.venv/` directory containing the isolated Python installation.

### Step 3: Activate Virtual Environment

**Linux/macOS:**
```bash
source .venv/bin/activate
```

**Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

### Step 4: Install Backend Dependencies

With the virtual environment activated, install all required packages:

```bash
pip install -e .
```

This installs the dependencies declared in [chatkit/backend/pyproject.toml:6-11]():
- `fastapi>=0.114,<0.116` - Web framework for the API server
- `uvicorn[standard]>=0.36,<0.37` - ASGI server for running FastAPI
- `openai>=1.40` - OpenAI Python SDK for API integration
- `openai-chatkit>=1.4.0,<2` - ChatKit server library

### Step 5: Install Development Tools (Optional)

For code quality checks and type validation:

```bash
pip install -e ".[dev]"
```

This installs additional tools defined in [chatkit/backend/pyproject.toml:13-16]():
- `ruff>=0.6.4,<0.7` - Python linter and formatter

### Backend Installation Verification

Verify the installation by checking that Python can import core modules:

```bash
python -c "import fastapi, uvicorn, openai, openai_chatkit; print('Backend dependencies installed successfully')"
```

Expected output: `Backend dependencies installed successfully`

**Sources:** [chatkit/backend/pyproject.toml:1-21](), [chatkit/backend/.gitignore:4]()

---

## Frontend Installation

The frontend is a React application built with Vite. Installation uses npm to download all JavaScript dependencies.

### Step 1: Navigate to Project Root

Return to the project root directory (either `chatkit/` or `managed-chatkit/`):

```bash
cd ..  # From backend directory
```

Or navigate directly:
```bash
cd chatkit/
```

### Step 2: Install Node.js Dependencies

Install all frontend and backend orchestration dependencies:

```bash
npm install
```

This command:
1. Reads `package.json` from the project root
2. Downloads dependencies into `node_modules/`
3. Creates or updates `package-lock.json` for reproducible builds
4. Installs both production and development dependencies

### Dependency Installation Flow

```mermaid
graph LR
    NPM_CMD["npm install"]
    PKG_JSON["package.json<br/>Dependency manifest"]
    NODE_MOD["node_modules/<br/>Installed packages"]
    LOCK["package-lock.json<br/>Version lock file"]
    
    NPM_CMD --> PKG_JSON
    PKG_JSON --> NODE_MOD
    NPM_CMD --> LOCK
    
    NODE_MOD -.->|"Vite, React,<br/>TypeScript, etc."| FE_BUILD["Frontend Build Tools"]
    NODE_MOD -.->|"Concurrently"| BE_RUNNER["Backend Runner Scripts"]
```

**Package Installation**: The `npm install` command reads dependency specifications and installs all required packages, including the frontend build toolchain (Vite, React, TypeScript) and development utilities (ESLint, concurrently).

**Sources:** [chatkit/README.md:9-10](), [chatkit/.gitignore:1]()

### Frontend Installation Verification

Verify that npm successfully installed dependencies:

```bash
npm list --depth=0
```

Expected output includes packages like:
- `vite@...`
- `react@...`
- `typescript@...`
- `eslint@...`

Alternatively, verify the `node_modules/` directory exists:

```bash
ls node_modules/
```

**Sources:** [chatkit/README.md:9-10]()

---

## Installation for Both Variants

Both starter applications (`chatkit/` and `managed-chatkit/`) follow identical installation procedures. The directory structure and dependency specifications are parallel:

```mermaid
graph TB
    subgraph CHATKIT["chatkit/"]
        CK_BE["backend/<br/>pyproject.toml"]
        CK_PKG["package.json"]
        CK_VENV[".venv/"]
        CK_NM["node_modules/"]
    end
    
    subgraph MANAGED["managed-chatkit/"]
        MCK_BE["backend/<br/>pyproject.toml"]
        MCK_PKG["package.json"]
        MCK_VENV[".venv/"]
        MCK_NM["node_modules/"]
    end
    
    INSTALL_PROC["Same Installation<br/>Procedure"]
    
    INSTALL_PROC --> CK_BE
    INSTALL_PROC --> CK_PKG
    INSTALL_PROC --> MCK_BE
    INSTALL_PROC --> MCK_PKG
    
    CK_BE --> CK_VENV
    CK_PKG --> CK_NM
    MCK_BE --> MCK_VENV
    MCK_PKG --> MCK_NM
```

**Parallel Structure**: Both variants maintain identical dependency management patterns. Run the same installation commands in either `chatkit/` or `managed-chatkit/` directories.

**Sources:** High-level architecture diagrams, repository structure

---

## Complete Installation Summary

The following table summarizes the complete installation process for a single starter application:

| Step | Command | Directory | Result |
|------|---------|-----------|--------|
| 1 | `cd chatkit/backend` | Project root | Navigate to backend |
| 2 | `python -m venv .venv` | `chatkit/backend/` | Create virtual environment |
| 3 | `source .venv/bin/activate` | `chatkit/backend/` | Activate virtual environment |
| 4 | `pip install -e .` | `chatkit/backend/` | Install Python dependencies |
| 5 | `cd ..` | `chatkit/backend/` | Return to project root |
| 6 | `npm install` | `chatkit/` | Install Node.js dependencies |

After these steps, the application is ready for environment configuration (see [Environment Configuration](#2.2)) and execution (see [Running the Application](#2.3)).

**Sources:** [chatkit/README.md:8-16](), [chatkit/backend/pyproject.toml:1-21]()

---

## Dependency Files and .gitignore Patterns

Both applications exclude generated artifacts from version control:

### Backend .gitignore

[chatkit/backend/.gitignore:1-9]() excludes:
- `__pycache__/` - Python bytecode cache
- `*.py[cod]` - Compiled Python files
- `.venv/` - Virtual environment directory
- `.ruff_cache/` - Ruff linter cache
- `.pytest_cache/` - Test framework cache

### Root .gitignore

[chatkit/.gitignore:1-3]() excludes:
- `node_modules/` - Installed npm packages
- `.env*` - Environment configuration files (except `.env.example`)

These patterns ensure that installation artifacts remain local and are not committed to the repository.

**Sources:** [chatkit/backend/.gitignore:1-9](), [chatkit/.gitignore:1-3]()

---

## Next Steps

After completing installation:

1. **Configure Environment Variables**: Set up `OPENAI_API_KEY` and optional configuration in `.env.local`. See [Environment Configuration](#2.2) for details.

2. **Run the Application**: Start both backend and frontend development servers. See [Running the Application](#2.3) for instructions.

3. **Explore Dependencies**: For detailed information about all installed packages, see [Backend Dependencies](#5.1) and [Frontend Dependencies](#5.2).

**Sources:** [chatkit/README.md:18-26](), table of contents

---

# Page: Environment Configuration

# Environment Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [chatkit/.env.example](chatkit/.env.example)
- [chatkit/.gitignore](chatkit/.gitignore)
- [chatkit/README.md](chatkit/README.md)
- [chatkit/backend/.gitignore](chatkit/backend/.gitignore)
- [chatkit/backend/app/__init__.py](chatkit/backend/app/__init__.py)
- [chatkit/backend/scripts/run.sh](chatkit/backend/scripts/run.sh)

</details>



This page explains the environment configuration required for both ChatKit starter applications (`chatkit/` and `managed-chatkit/`). Both applications share the same configuration approach, using environment variables stored in `.env.local` at the repository root for API credentials and connection settings.

For information about installing dependencies, see [Installation & Prerequisites](#2.1). For information about running the configured application, see [Running the Application](#2.3).

## Overview of Configuration System

Both starter applications use a unified environment variable configuration system:

1. **Environment Variables**: API credentials and connection settings stored in `.env.local` at the repository root (not version controlled)
2. **Frontend Configuration**: Optional UI customization in `frontend/src/lib/config.ts` (version controlled)

Environment variables are split by consumer:
- Backend (Python/FastAPI): `OPENAI_API_KEY`
- Frontend (Vite/React): Variables prefixed with `VITE_`

The repository root `.env.local` file is automatically loaded by both backend and frontend during development:
- Backend: Loaded by [chatkit/backend/scripts/run.sh:24-31]()
- Frontend: Automatically loaded by Vite's environment variable system

Sources: [chatkit/README.md:18-26](), [chatkit/.env.example:1-3](), [chatkit/backend/scripts/run.sh:22-31]()

## Environment Variables Setup

### Creating the Configuration File

Each starter application directory contains a `.env.example` template. To configure either application, create `.env.local` at the **repository root**:

```bash
# From repository root
cp chatkit/.env.example .env.local
```

The `.env.local` file is excluded from version control via [chatkit/.gitignore:2]() to prevent credential leakage. You must manually populate this file with your actual values.

**Environment Variable Loading Flow**

```mermaid
graph TD
    subgraph "Repository Root"
        EXAMPLE["chatkit/.env.example<br/>Template"]
        LOCAL[".env.local<br/>Actual Credentials<br/>(gitignored)"]
    end
    
    subgraph "Backend Process"
        RUN_SH["backend/scripts/run.sh"]
        VENV[".venv activation"]
        SOURCE["source .env.local"]
        UVICORN["uvicorn app.main:app"]
    end
    
    subgraph "Frontend Process"
        VITE["vite dev server"]
        VITE_ENV["Vite env loader"]
    end
    
    subgraph "Environment Variables"
        API_KEY["OPENAI_API_KEY"]
        API_URL["VITE_CHATKIT_API_URL"]
        DOMAIN_KEY["VITE_CHATKIT_API_DOMAIN_KEY"]
    end
    
    subgraph "Consumers"
        FASTAPI["FastAPI app/main.py"]
        CONFIG["frontend/src/lib/config.ts"]
    end
    
    EXAMPLE -.->|"Copy to root"| LOCAL
    
    LOCAL --> RUN_SH
    RUN_SH --> VENV
    VENV --> SOURCE
    SOURCE --> API_KEY
    API_KEY --> FASTAPI
    
    LOCAL --> VITE
    VITE --> VITE_ENV
    VITE_ENV --> API_URL
    VITE_ENV --> DOMAIN_KEY
    API_URL --> CONFIG
    DOMAIN_KEY --> CONFIG
```

Sources: [chatkit/README.md:24-25](), [chatkit/.env.example:1-3](), [chatkit/backend/scripts/run.sh:24-31]()

### Required Environment Variables

| Variable | Consumer | Purpose | Example Format |
|----------|----------|---------|----------------|
| `OPENAI_API_KEY` | Backend (Python/FastAPI) | Authenticates with OpenAI API for chat completions | `sk-proj-...` |

#### OPENAI_API_KEY

This variable contains your OpenAI API key for accessing the OpenAI API. It is used by the FastAPI backend to authenticate chat completion requests.

**Security characteristics:**
- Never exposed to client-side code
- Required for backend to start successfully
- Validated by [chatkit/backend/scripts/run.sh:33-36]() before starting `uvicorn`

**Obtaining the key:**
1. Visit https://platform.openai.com/api-keys
2. Create a new API key
3. Copy the key starting with `sk-proj-`
4. Add to `.env.local` at repository root

**Backend loading mechanism:**

The backend startup script [chatkit/backend/scripts/run.sh:24-31]() loads environment variables from `.env.local`:

```bash
ENV_FILE="$PROJECT_ROOT/../.env.local"
if [ -z "${OPENAI_API_KEY:-}" ] && [ -f "$ENV_FILE" ]; then
  echo "Sourcing OPENAI_API_KEY from $ENV_FILE"
  set -a
  . "$ENV_FILE"
  set +a
fi
```

If `OPENAI_API_KEY` is not set, the script exits with an error message.

Sources: [chatkit/README.md:20](), [chatkit/.env.example:1](), [chatkit/backend/scripts/run.sh:24-36]()

### Optional Environment Variables

| Variable | Consumer | Default Value | Purpose |
|----------|----------|---------------|---------|
| `VITE_CHATKIT_API_URL` | Frontend (Vite/React) | `/chatkit` | Backend API endpoint URL |
| `VITE_CHATKIT_API_DOMAIN_KEY` | Frontend (Vite/React) | `domain_pk_localhost_dev` | Domain key for ChatKit authentication |

#### VITE_CHATKIT_API_URL

Specifies the URL where the frontend should send ChatKit API requests. The `VITE_` prefix makes this variable accessible to client-side Vite/React code.

**Default behavior:**
- If not set, defaults to `/chatkit` in [chatkit/frontend/src/lib/config.ts]()
- During development, Vite's proxy forwards `/chatkit` to the backend on `http://127.0.0.1:8000`
- For production deployment, set to the full backend URL (e.g., `https://api.example.com/chatkit`)

**Example configurations:**

| Environment | Value | Description |
|-------------|-------|-------------|
| Local development | `/chatkit` or omitted | Uses Vite proxy to backend |
| Production | `https://api.example.com/chatkit` | Direct backend URL |
| Custom port | `http://localhost:9000/chatkit` | Backend on non-standard port |

#### VITE_CHATKIT_API_DOMAIN_KEY

Identifies the domain for ChatKit authentication. This key is used by the ChatKit frontend library to validate requests.

**Default behavior:**
- If not set, defaults to `domain_pk_localhost_dev` in [chatkit/frontend/src/lib/config.ts]()
- The default value `domain_pk_localhost_dev` is suitable for local development only

**Production deployment:**
1. Register your production domain in the OpenAI dashboard
2. Obtain a production domain key (format: `domain_pk_...`)
3. Set `VITE_CHATKIT_API_DOMAIN_KEY` to the production key

Sources: [chatkit/README.md:21-26](), [chatkit/.env.example:2-3]()

## Frontend Configuration File

The `frontend/src/lib/config.ts` file in each starter application provides frontend configuration for connection settings and UI customization. Unlike environment variables, these files are version-controlled and represent customization points.

**Frontend Configuration Module**

```mermaid
graph TB
    subgraph "Environment Variables"
        VITE_URL["VITE_CHATKIT_API_URL"]
        VITE_DOMAIN["VITE_CHATKIT_API_DOMAIN_KEY"]
    end
    
    subgraph "config.ts"
        CONFIG_TS["frontend/src/lib/config.ts"]
        API_URL_CONST["apiUrl constant"]
        DOMAIN_KEY_CONST["domainKey constant"]
    end
    
    subgraph "React Components"
        PANEL["ChatKitPanel.tsx"]
    end
    
    VITE_URL -.->|"import.meta.env"| API_URL_CONST
    VITE_DOMAIN -.->|"import.meta.env"| DOMAIN_KEY_CONST
    
    API_URL_CONST --> CONFIG_TS
    DOMAIN_KEY_CONST --> CONFIG_TS
    
    CONFIG_TS --> PANEL
    PANEL -->|"Connects to backend"| PANEL
```

Sources: [chatkit/frontend/src/lib/config.ts](), [chatkit/README.md:30-31]()

### Configuration Points

The `config.ts` file reads environment variables via Vite's `import.meta.env` object and provides default values:

| Configuration | Environment Variable | Default | Purpose |
|---------------|---------------------|---------|---------|
| `apiUrl` | `VITE_CHATKIT_API_URL` | `/chatkit` | Backend endpoint URL |
| `domainKey` | `VITE_CHATKIT_API_DOMAIN_KEY` | `domain_pk_localhost_dev` | ChatKit domain key |

**Customization points** (as documented in [chatkit/README.md:29-32]()):

1. **Connection settings**: Modify `apiUrl` and `domainKey` in [chatkit/frontend/src/lib/config.ts]()
2. **Layout structure**: Adjust UI layout in [chatkit/frontend/src/components/ChatKitPanel.tsx]()

These configuration points allow developers to customize the frontend behavior without modifying core application logic.

Sources: [chatkit/README.md:29-32](), [chatkit/frontend/src/lib/config.ts]()

## Configuration Consumption Flow

The following diagram shows how configuration values flow from `.env.local` to both backend and frontend components during application startup and runtime.

**End-to-End Configuration Flow**

```mermaid
graph TB
    subgraph "Repository Root"
        ENV_LOCAL[".env.local<br/>OPENAI_API_KEY<br/>VITE_CHATKIT_API_URL<br/>VITE_CHATKIT_API_DOMAIN_KEY"]
    end
    
    subgraph "Backend Startup"
        RUN_SCRIPT["backend/scripts/run.sh"]
        SOURCE_ENV["source .env.local"]
        ENV_CHECK["Check OPENAI_API_KEY"]
        UVICORN_START["uvicorn app.main:app"]
    end
    
    subgraph "Backend Runtime"
        MAIN_PY["app/main.py"]
        FASTAPI_APP["FastAPI app"]
        CHATKIT_ENDPOINT["/chatkit endpoint"]
        SERVER["StarterChatServer"]
        AGENT["assistant_agent"]
        OPENAI_SDK["openai.OpenAI(api_key)"]
    end
    
    subgraph "Frontend Startup"
        VITE_CMD["vite dev"]
        VITE_LOAD["Vite env loader"]
        IMPORT_META["import.meta.env"]
    end
    
    subgraph "Frontend Runtime"
        CONFIG_TS["lib/config.ts"]
        PANEL["ChatKitPanel.tsx"]
        FETCH_CHATKIT["fetch(apiUrl)"]
    end
    
    ENV_LOCAL --> RUN_SCRIPT
    RUN_SCRIPT --> SOURCE_ENV
    SOURCE_ENV --> ENV_CHECK
    ENV_CHECK -->|"Pass"| UVICORN_START
    UVICORN_START --> MAIN_PY
    
    MAIN_PY --> FASTAPI_APP
    FASTAPI_APP --> CHATKIT_ENDPOINT
    CHATKIT_ENDPOINT --> SERVER
    SERVER --> AGENT
    AGENT --> OPENAI_SDK
    
    ENV_LOCAL --> VITE_CMD
    VITE_CMD --> VITE_LOAD
    VITE_LOAD --> IMPORT_META
    IMPORT_META --> CONFIG_TS
    CONFIG_TS --> PANEL
    PANEL --> FETCH_CHATKIT
    FETCH_CHATKIT -->|"HTTP Request"| CHATKIT_ENDPOINT
```

Sources: [chatkit/backend/scripts/run.sh:24-39](), [chatkit/frontend/src/lib/config.ts]()

## Configuration Validation

Both starter applications perform validation at startup and runtime:

### Backend Validation

The backend startup script [chatkit/backend/scripts/run.sh:33-36]() validates `OPENAI_API_KEY` before starting the server:

```bash
if [ -z "${OPENAI_API_KEY:-}" ]; then
  echo "Set OPENAI_API_KEY in your environment or in .env.local before running this script."
  exit 1
fi
```

**Validation sequence:**

```mermaid
graph LR
    START["run.sh starts"]
    CHECK{"OPENAI_API_KEY set?"}
    ERROR["Exit with error message"]
    CONTINUE["Start uvicorn"]
    
    START --> CHECK
    CHECK -->|"No"| ERROR
    CHECK -->|"Yes"| CONTINUE
```

### Frontend Validation

The frontend performs minimal validation. If `VITE_CHATKIT_API_URL` or `VITE_CHATKIT_API_DOMAIN_KEY` are not set, the application uses default values from [chatkit/frontend/src/lib/config.ts]().

**Missing configuration symptoms:**

| Missing Variable | Startup Behavior | Runtime Behavior |
|-----------------|------------------|------------------|
| `OPENAI_API_KEY` | Backend script exits with error message | N/A (blocked at startup) |
| `VITE_CHATKIT_API_URL` | Uses default `/chatkit` | May fail if backend not proxied |
| `VITE_CHATKIT_API_DOMAIN_KEY` | Uses default `domain_pk_localhost_dev` | Works for local development only |

Sources: [chatkit/backend/scripts/run.sh:33-36](), [chatkit/frontend/src/lib/config.ts]()

## Configuration Reference Table

| Variable | Source | Type | Default | Required | Consumer |
|----------|--------|------|---------|----------|----------|
| `OPENAI_API_KEY` | `.env.local` | Backend | None | Yes | Python backend, OpenAI SDK |
| `VITE_CHATKIT_API_URL` | `.env.local` | Frontend | `/chatkit` | No | `frontend/src/lib/config.ts` |
| `VITE_CHATKIT_API_DOMAIN_KEY` | `.env.local` | Frontend | `domain_pk_localhost_dev` | No | `frontend/src/lib/config.ts` |

**File locations:**
- `.env.local`: Repository root (gitignored)
- `.env.example`: [chatkit/.env.example:1-3]()
- Configuration module: [chatkit/frontend/src/lib/config.ts]()
- Backend loader: [chatkit/backend/scripts/run.sh:24-31]()

Sources: [chatkit/.env.example:1-3](), [chatkit/README.md:20-26](), [chatkit/backend/scripts/run.sh:24-36]()

## Next Steps

After completing configuration:
1. Verify `.env.local` contains valid values for all required variables
2. (Optional) Customize `lib/config.ts` constants for your use case
3. Proceed to [Running the Application](#2.3) to start the development server

For information about how these configuration values are consumed by the backend API, see [Session Creation Endpoint](#7.1). For details on how the frontend uses configuration, see [ChatKitPanel Component](#6).

---

# Page: Running the Application

# Running the Application

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [chatkit/.env.example](chatkit/.env.example)
- [chatkit/.gitignore](chatkit/.gitignore)
- [chatkit/README.md](chatkit/README.md)
- [chatkit/backend/.gitignore](chatkit/backend/.gitignore)
- [chatkit/backend/app/__init__.py](chatkit/backend/app/__init__.py)
- [chatkit/backend/scripts/run.sh](chatkit/backend/scripts/run.sh)

</details>



This document describes the commands for running the ChatKit Starter App in development and production modes. It covers the npm scripts defined in `package.json`, their underlying Next.js commands, and the expected behavior of each execution mode. For installation instructions, see [Installation](#2.1). For environment configuration, see [Configuration](#2.2).

## Command Overview

The application provides three primary npm scripts for running the application in different modes:

| Command | Script Definition | Purpose | Mode |
|---------|------------------|---------|------|
| `npm run dev` | `next dev` | Start development server with hot reload | Development |
| `npm run build` | `next build` | Create optimized production build | Build |
| `npm start` | `next start` | Serve production build | Production |

Sources: [package.json:5-9]()

## Development Mode

### Starting the Development Server

The development server is started using:

```bash
npm run dev
```

This executes the `next dev` command [package.json:6](), which starts the Next.js development server with the following characteristics:

**Server Behavior:**
- Listens on `http://localhost:3000` by default
- Enables Fast Refresh for instant feedback on code changes
- Compiles pages on-demand as they are requested
- Provides detailed error overlays in the browser for compilation and runtime errors
- Automatically recompiles when files in `app/`, `components/`, `hooks/`, or `lib/` are modified

**What Gets Loaded:**
1. **RootLayout** [app/layout.tsx]() - Loads the ChatKit script from OpenAI's CDN
2. **Home Page** [app/page.tsx]() - Renders the main App component
3. **App Component** [app/App.tsx]() - Initializes theme management and ChatKitPanel
4. **API Routes** [app/api/create-session/route.ts]() - Backend endpoint for session creation

**Development-Specific Features:**
- Source maps enabled for debugging
- Verbose error messages and stack traces
- TypeScript type checking runs alongside compilation
- ESLint warnings displayed in terminal and browser

### Development Server Flow

```mermaid
graph TD
    CMD["npm run dev"]
    NEXT["next dev command"]
    SERVER["Next.js Dev Server<br/>localhost:3000"]
    
    subgraph "On Request"
        COMPILE["Compile Page<br/>TypeScript → JavaScript"]
        BUNDLE["Bundle Dependencies<br/>React, ChatKit, etc"]
        SERVE["Serve HTML Response"]
    end
    
    subgraph "File Watching"
        WATCH["Watch File System<br/>app/, components/, lib/"]
        CHANGE["File Change Detected"]
        RECOMPILE["Recompile Module"]
        HMR["Hot Module Replacement<br/>Update Browser"]
    end
    
    subgraph "Browser"
        LOAD["Browser Loads Page"]
        EXECUTE["Execute Client Code"]
        CHATKIT["Initialize ChatKitPanel"]
        SESSION["Call /api/create-session"]
    end
    
    CMD --> NEXT
    NEXT --> SERVER
    SERVER --> COMPILE
    COMPILE --> BUNDLE
    BUNDLE --> SERVE
    SERVE --> LOAD
    LOAD --> EXECUTE
    EXECUTE --> CHATKIT
    CHATKIT --> SESSION
    
    SERVER --> WATCH
    WATCH --> CHANGE
    CHANGE --> RECOMPILE
    RECOMPILE --> HMR
    HMR --> LOAD
```

Sources: [package.json:6](), [README.md:39-43]()

### Expected Development Output

When the development server starts successfully, you will see output similar to:

```
  ▲ Next.js 15.5.4
  - Local:        http://localhost:3000
  - Ready in 1.2s
```

The terminal will display compilation logs as you navigate the application and modify files. Each page request triggers on-demand compilation of that route.

Sources: [package.json:6](), [README.md:42]()

## Production Build

### Creating an Optimized Build

The production build is created using:

```bash
npm run build
```

This executes the `next build` command [package.json:7](), which performs a full static analysis and optimization of the application.

**Build Process Steps:**

1. **Linting** - Runs ESLint checks on all TypeScript/JavaScript files
2. **Type Checking** - Validates TypeScript types across the entire codebase
3. **Compilation** - Compiles all pages and API routes ahead of time
4. **Optimization** - Minifies JavaScript, optimizes CSS, generates static assets
5. **Code Splitting** - Separates code into optimized chunks for efficient loading
6. **Static Generation** - Pre-renders static pages where possible

**Build Outputs:**

The build process generates the `.next/` directory containing:

```
.next/
├── cache/              # Build cache for incremental builds
├── server/             # Server-side code and API routes
│   ├── app/           # Compiled app routes
│   └── chunks/        # Server-side code chunks
├── static/            # Static assets with content hashes
│   ├── chunks/        # JavaScript bundles
│   └── css/           # Optimized CSS files
└── BUILD_ID           # Unique identifier for this build
```

### Production Build Pipeline

```mermaid
graph LR
    BUILD_CMD["npm run build"]
    NEXT_BUILD["next build"]
    
    subgraph "Analysis Phase"
        LINT["ESLint Check<br/>Code Quality"]
        TYPE["TypeScript Check<br/>Type Safety"]
    end
    
    subgraph "Compilation Phase"
        COMPILE["Compile Routes<br/>app/* → JavaScript"]
        API["Compile API Routes<br/>app/api/*"]
    end
    
    subgraph "Optimization Phase"
        MINIFY["Minify JavaScript<br/>Remove Whitespace/Comments"]
        CSS_OPT["Optimize CSS<br/>Tailwind + PostCSS"]
        SPLIT["Code Splitting<br/>Generate Chunks"]
    end
    
    subgraph "Output"
        NEXT_DIR[".next/ Directory<br/>Production Build"]
    end
    
    BUILD_CMD --> NEXT_BUILD
    NEXT_BUILD --> LINT
    LINT --> TYPE
    TYPE --> COMPILE
    TYPE --> API
    COMPILE --> MINIFY
    API --> MINIFY
    MINIFY --> CSS_OPT
    CSS_OPT --> SPLIT
    SPLIT --> NEXT_DIR
```

Sources: [package.json:7](), [README.md:47-50]()

**Build Configuration:**

The build process is configured by:
- **next.config.ts** [next.config.ts:3-10]() - Webpack customizations and module resolution
- **tsconfig.json** - TypeScript compiler options and path aliases
- **postcss.config.mjs** - CSS processing pipeline with Tailwind
- **package.json** - Dependencies that influence build output

Sources: [next.config.ts:1-13]()

### Build Verification

After a successful build, the output displays:

```
Route (app)                              Size     First Load JS
┌ ○ /                                    5.2 kB          95 kB
└ ○ /api/create-session                  0 B             0 B

○  (Static)  prerendered as static content
```

This summary shows:
- **Route** - Each application route
- **Size** - Route-specific JavaScript size
- **First Load JS** - Total JavaScript loaded on first visit (includes shared chunks)
- **○** - Static indicator (pre-rendered at build time)

Sources: [package.json:7](), [README.md:47-50]()

## Production Server

### Starting the Production Server

After building, start the production server using:

```bash
npm start
```

This executes the `next start` command [package.json:8](), which serves the optimized production build created by `npm run build`.

**Production Server Characteristics:**

- Serves pre-compiled, optimized code from `.next/` directory
- No hot reload or file watching
- Minimal runtime overhead
- Suitable for deployment to production environments
- Requires a successful `npm run build` to have run first

**Production vs. Development:**

| Feature | Development (`npm run dev`) | Production (`npm start`) |
|---------|---------------------------|------------------------|
| Compilation | On-demand, per request | Pre-compiled during build |
| Speed | Slower first load, fast subsequent | Fast first load |
| Error Messages | Detailed stack traces | Minimized, user-friendly |
| Source Maps | Enabled | Disabled by default |
| File Watching | Yes, with hot reload | No |
| Build Required | No | Yes (`npm run build`) |

Sources: [package.json:8](), [README.md:49-50]()

### Production Execution Flow

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant Build as "npm run build"
    participant NextDir as ".next/ Directory"
    participant Start as "npm start"
    participant Server as "Production Server<br/>localhost:3000"
    participant Browser as "Browser"
    participant API as "/api/create-session"
    
    Dev->>Build: "Execute build command"
    Build->>NextDir: "Generate optimized files"
    NextDir-->>Build: "Build complete"
    
    Dev->>Start: "Execute start command"
    Start->>NextDir: "Read compiled assets"
    Start->>Server: "Start HTTP server"
    Server-->>Dev: "Ready on localhost:3000"
    
    Browser->>Server: "GET /"
    Server->>NextDir: "Load pre-compiled page"
    NextDir-->>Server: "Return static HTML + JS"
    Server-->>Browser: "Serve optimized page"
    
    Browser->>Browser: "Execute client bundle"
    Browser->>Browser: "Initialize ChatKitPanel"
    Browser->>API: "POST /api/create-session"
    API-->>Browser: "Return session credentials"
```

Sources: [package.json:7-8](), [README.md:47-50]()

## Complete Application Lifecycle

### From Development to Production

```mermaid
graph TD
    subgraph "Installation - See 2.1"
        CLONE["Clone Repository"]
        NPM_INSTALL["npm install<br/>Install Dependencies"]
    end
    
    subgraph "Configuration - See 2.2"
        ENV_FILE["Create .env.local"]
        API_KEY["Set OPENAI_API_KEY"]
        WORKFLOW["Set NEXT_PUBLIC_CHATKIT_WORKFLOW_ID"]
    end
    
    subgraph "Development Mode"
        DEV_CMD["npm run dev"]
        DEV_SERVER["Development Server<br/>localhost:3000"]
        HOT_RELOAD["Hot Reload Enabled"]
    end
    
    subgraph "Production Build"
        BUILD_CMD["npm run build"]
        NEXT_BUILD[".next/ Directory<br/>Optimized Assets"]
    end
    
    subgraph "Production Server"
        START_CMD["npm start"]
        PROD_SERVER["Production Server<br/>localhost:3000"]
    end
    
    CLONE --> NPM_INSTALL
    NPM_INSTALL --> ENV_FILE
    ENV_FILE --> API_KEY
    API_KEY --> WORKFLOW
    
    WORKFLOW --> DEV_CMD
    DEV_CMD --> DEV_SERVER
    DEV_SERVER --> HOT_RELOAD
    
    WORKFLOW --> BUILD_CMD
    BUILD_CMD --> NEXT_BUILD
    NEXT_BUILD --> START_CMD
    START_CMD --> PROD_SERVER
```

Sources: [package.json:5-9](), [README.md:11-50]()

## Common Usage Patterns

### Local Development Workflow

1. **Initial Setup** (once):
   ```bash
   npm install
   cp .env.example .env.local
   # Edit .env.local with your credentials
   ```

2. **Daily Development**:
   ```bash
   npm run dev
   # Visit http://localhost:3000
   # Edit code, changes reflect immediately
   ```

3. **Pre-deployment Testing**:
   ```bash
   npm run build  # Verify production build succeeds
   npm start      # Test production server locally
   ```

Sources: [README.md:15-50](), [package.json:5-9]()

### Port Configuration

By default, all commands serve on port 3000. To use a different port:

```bash
# Development
PORT=3001 npm run dev

# Production
PORT=3001 npm start
```

Sources: [README.md:42]()

## Error Scenarios

### Build Failures

If `npm run build` fails, common causes include:

1. **TypeScript Errors** - Type checking failures in `.tsx` or `.ts` files
2. **ESLint Violations** - Code quality issues flagged by linting rules
3. **Missing Environment Variables** - Required NEXT_PUBLIC_* variables not set during build
4. **Dependency Issues** - Incompatible or missing packages in `node_modules/`

**Resolution**: Check the build output for specific error messages and file locations.

### Production Server Failures

If `npm start` fails with "Could not find a production build":

**Cause**: The `.next/` directory does not exist or is incomplete.

**Resolution**: Run `npm run build` before `npm start`.

Sources: [package.json:7-8]()

## Next.js Command Reference

Each npm script maps directly to a Next.js CLI command:

| npm Script | Next.js Command | Configuration File |
|-----------|----------------|-------------------|
| `npm run dev` | `next dev` | next.config.ts |
| `npm run build` | `next build` | next.config.ts |
| `npm start` | `next start` | next.config.ts |
| `npm run lint` | `eslint` | eslint.config.mjs |

The `next` CLI reads configuration from [next.config.ts:1-13](), which customizes webpack behavior and module resolution.

Sources: [package.json:5-10](), [next.config.ts:1-13]()

---

# Page: Self-Hosted ChatKit (chatkit/)

# Self-Hosted ChatKit (chatkit/)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [chatkit/.env.example](chatkit/.env.example)
- [chatkit/.gitignore](chatkit/.gitignore)
- [chatkit/README.md](chatkit/README.md)
- [chatkit/backend/.gitignore](chatkit/backend/.gitignore)
- [chatkit/backend/app/__init__.py](chatkit/backend/app/__init__.py)

</details>



This document covers the self-hosted ChatKit starter application, a reference implementation demonstrating how to build a conversational AI interface with full control over infrastructure and backend logic. The self-hosted approach requires developers to manage their own backend server, storage, and AI agent configuration.

For information about the managed integration pattern that uses hosted workflows, see [Managed ChatKit (managed-chatkit/)](#4).

**Sources:** [README.md:1-9](), [chatkit/README.md:1-33]()

---

## Purpose and Scope

The `chatkit/` directory contains a complete starter application consisting of:

- A **FastAPI backend** (`backend/`) that processes chat requests and orchestrates OpenAI API interactions
- A **Vite + React frontend** (`frontend/`) that provides the user interface
- An **in-memory storage system** for conversation history
- Integration with the `openai-chatkit` Python library for AI agent capabilities

This implementation is designed for developers who want full control over their ChatKit deployment, including the ability to customize business logic, storage mechanisms, and deployment infrastructure. The application demonstrates core concepts like streaming responses, conversation history management, and agent configuration.

**Sources:** [chatkit/README.md:1-4]()

---

## Architecture Overview

The self-hosted ChatKit application follows a client-server architecture with clear separation between the presentation layer (React frontend) and business logic layer (FastAPI backend).

### High-Level Architecture

```mermaid
graph TB
    subgraph Browser["Browser Environment"]
        User["User"]
        ReactUI["React UI Components"]
        Config["config.ts<br/>Configuration"]
    end
    
    subgraph Frontend["Frontend Layer<br/>Port 3000"]
        ViteDev["Vite Dev Server"]
        Proxy["Proxy: /chatkit → 8000"]
    end
    
    subgraph Backend["Backend Layer<br/>Port 8000"]
        FastAPIApp["main.py<br/>FastAPI Application"]
        ChatEndpoint["/chatkit Endpoint"]
        StarterServer["server.py<br/>StarterChatServer"]
        MemStore["server.py<br/>MemoryStore"]
        AssistantAgent["assistant_agent<br/>AI Configuration"]
    end
    
    subgraph External["External Services"]
        OpenAIAPI["OpenAI API"]
        ChatKitLib["openai-chatkit Library"]
    end
    
    User -->|"Interact"| ReactUI
    ReactUI -->|"HTTP Request"| ViteDev
    ViteDev -->|"Proxy"| Proxy
    Proxy -->|"POST /chatkit"| FastAPIApp
    FastAPIApp -->|"Route"| ChatEndpoint
    ChatEndpoint -->|"process()"| StarterServer
    StarterServer -->|"load_thread_items()"| MemStore
    StarterServer -->|"run_streamed()"| AssistantAgent
    AssistantAgent -->|"API Calls"| ChatKitLib
    ChatKitLib -->|"Chat Completion"| OpenAIAPI
    OpenAIAPI -->|"Stream Response"| ChatKitLib
    ChatKitLib -->|"ThreadStreamEvent"| AssistantAgent
    AssistantAgent -->|"Yield Events"| StarterServer
    StarterServer -->|"StreamingResponse"| ChatEndpoint
    ChatEndpoint -->|"HTTP Stream"| Proxy
    Proxy -->|"SSE"| ReactUI
    
    MemStore -->|"save_item()"| MemStore
```

**Sources:** [chatkit/README.md:13-16]()

---

## Directory Structure

The `chatkit/` directory is organized into distinct backend and frontend subsystems:

| Path | Description |
|------|-------------|
| `backend/` | FastAPI application and Python business logic |
| `backend/app/` | Python package containing application code |
| `backend/app/main.py` | FastAPI entrypoint and `/chatkit` endpoint |
| `backend/app/server.py` | `StarterChatServer` and `MemoryStore` implementations |
| `backend/pyproject.toml` | Python dependencies and tooling configuration |
| `frontend/` | Vite + React application |
| `frontend/src/` | React source code |
| `frontend/src/lib/config.ts` | ChatKit connection configuration |
| `frontend/src/components/ChatKitPanel.tsx` | Main UI component |
| `frontend/package.json` | Node.js dependencies and scripts |
| `frontend/vite.config.ts` | Vite build configuration with proxy setup |
| `package.json` | Root-level scripts for concurrent dev server execution |
| `.env.example` | Example environment variable configuration |

**Sources:** [chatkit/README.md:1-33](), [chatkit/.gitignore:1-4](), [chatkit/backend/.gitignore:1-9]()

---

## Backend Implementation

The backend is a FastAPI application that serves as the orchestration layer between the frontend and OpenAI's API. It manages conversation state, processes requests, and streams responses back to the client.

### Component Architecture

```mermaid
graph TB
    subgraph FastAPI["main.py - FastAPI Application"]
        App["app = FastAPI()"]
        CORSMiddleware["CORSMiddleware<br/>allow_origins=['*']"]
        ChatEndpoint["@app.post('/chatkit')<br/>def chatkit_endpoint()"]
    end
    
    subgraph Server["server.py - StarterChatServer"]
        ServerClass["class StarterChatServer"]
        ProcessMethod["def process()<br/>→ StreamingResponse"]
        RespondMethod["def respond()<br/>→ Generator"]
        Store["self.store: Store"]
        Agent["self.assistant_agent"]
    end
    
    subgraph Storage["server.py - MemoryStore"]
        MemoryClass["class MemoryStore"]
        ThreadsDict["threads: Dict[str, List]"]
        MetaDict["thread_metadata: Dict[str, ThreadMetadata]"]
        LoadMethod["def load_thread_items()<br/>→ List[ThreadItem]"]
        SaveMethod["def save_item()"]
        ListMethod["def list_thread_metadata()<br/>→ List[ThreadMetadata]"]
    end
    
    subgraph Agent["Agent Configuration"]
        AssistantAgent["assistant_agent = Agent()"]
        Instructions["instructions: str"]
        Model["model: 'gpt-4o-mini'"]
        Context["context: Dict"]
    end
    
    ChatEndpoint -->|"Instantiate"| ServerClass
    ProcessMethod -->|"Calls"| RespondMethod
    RespondMethod -->|"load_thread_items()"| LoadMethod
    RespondMethod -->|"save_item()"| SaveMethod
    RespondMethod -->|"run_streamed()"| AssistantAgent
    ServerClass -->|"Has"| Store
    ServerClass -->|"Has"| Agent
    MemoryClass -->|"Stores"| ThreadsDict
    MemoryClass -->|"Stores"| MetaDict
```

**Sources:** [chatkit/README.md:13-16](), [chatkit/backend/app/__init__.py:1-2]()

### FastAPI Entrypoint

The `main.py` file defines the FastAPI application and configures the `/chatkit` endpoint:

- **Application Setup**: Creates a FastAPI instance with CORS middleware configured to allow all origins
- **Single Endpoint**: Exposes `POST /chatkit` which accepts ChatKit request payloads
- **Server Instantiation**: Creates a `StarterChatServer` instance for each request
- **Streaming Response**: Returns a `StreamingResponse` that yields server-sent events

The endpoint signature follows the pattern: `chatkit_endpoint(payload: ChatKitRequestPayload, context: Annotated[..., Depends(auth_context)])`.

**Sources:** [chatkit/README.md:3-4](), [chatkit/README.md:15-16]()

### StarterChatServer

The `StarterChatServer` class (defined in `backend/app/server.py`) orchestrates the conversation flow:

**Key Methods:**
- `process(payload, context)` - Main entry point that validates requests and returns a streaming response
- `respond(payload, context)` - Generator function that:
  1. Loads conversation history using `store.load_thread_items(thread_id, limit=30)`
  2. Converts items to agent input format using `simple_to_agent_input()`
  3. Executes the AI agent with `assistant_agent.run_streamed(input, context)`
  4. Yields `ThreadStreamEvent` objects as JSON strings
  5. Saves the final response using `store.save_item()`

**Agent Configuration:**
The server initializes an `assistant_agent` with:
- Model: `"gpt-4o-mini"`
- Instructions: Default assistant behavior
- Streaming enabled for real-time responses

**Sources:** [chatkit/README.md:32]()

### MemoryStore

The `MemoryStore` class provides in-memory conversation storage with the following data structures:

**Internal State:**
```python
threads: Dict[str, List[ThreadItem]]  # thread_id → list of conversation items
thread_metadata: Dict[str, ThreadMetadata]  # thread_id → metadata
```

**Core Methods:**

| Method | Purpose | Parameters |
|--------|---------|------------|
| `load_thread_items()` | Retrieve conversation history | `thread_id`, `limit` (default: 30), `order` |
| `save_item()` | Persist a single conversation item | `thread_id`, `item: ThreadItem` |
| `list_thread_metadata()` | Get metadata for all threads | `order`, `limit`, `offset` |

**Pagination Logic:**
The store implements limit-based pagination. When `load_thread_items()` is called with `limit=30`, it returns the 30 most recent items in the specified order (ascending or descending).

**Production Note:**
The in-memory implementation is not suitable for production. Replace with a persistent database (PostgreSQL, MongoDB, etc.) by implementing the same interface.

**Sources:** [chatkit/README.md:32]()

---

## Frontend Implementation

The frontend is a single-page application built with Vite, React, and TypeScript that provides the user interface for the ChatKit conversation experience.

### Frontend Architecture

```mermaid
graph TB
    subgraph ViteConfig["vite.config.ts"]
        ViteApp["defineConfig()"]
        ProxyConfig["proxy: /chatkit<br/>→ http://127.0.0.1:8000"]
    end
    
    subgraph EntryPoint["main.tsx"]
        ReactRoot["ReactDOM.createRoot()"]
        AppMount["<App />"]
    end
    
    subgraph Configuration["lib/config.ts"]
        ChatKitConfig["chatKitConfig"]
        APIUrl["apiUrl: VITE_CHATKIT_API_URL"]
        DomainKey["domainKey: VITE_CHATKIT_API_DOMAIN_KEY"]
    end
    
    subgraph Components["components/"]
        App["App.tsx"]
        ChatKitPanel["ChatKitPanel.tsx<br/><ChatKitLayout>"]
    end
    
    ViteApp -->|"Configures"| ProxyConfig
    ReactRoot -->|"Mounts"| AppMount
    App -->|"Renders"| ChatKitPanel
    ChatKitPanel -->|"Uses"| ChatKitConfig
    ChatKitConfig -->|"Reads"| APIUrl
    ChatKitConfig -->|"Reads"| DomainKey
    ProxyConfig -->|"Routes requests"| Backend["Backend :8000"]
```

**Sources:** [chatkit/README.md:15-16](), [chatkit/README.md:30-31]()

### Configuration

The `frontend/src/lib/config.ts` file exports the `chatKitConfig` object that controls ChatKit connection settings:

**Environment Variables:**
- `VITE_CHATKIT_API_URL` - Backend API endpoint (defaults to `/chatkit`)
- `VITE_CHATKIT_API_DOMAIN_KEY` - Domain authentication key (defaults to `domain_pk_localhost_dev`)

**Development vs Production:**
In development, the Vite proxy routes `/chatkit` requests to `http://127.0.0.1:8000`. In production, set `VITE_CHATKIT_API_URL` to the full backend URL and `VITE_CHATKIT_API_DOMAIN_KEY` to a registered production domain key from the OpenAI dashboard.

**Sources:** [chatkit/README.md:18-26](), [chatkit/README.md:30](), [chatkit/.env.example:1-3]()

### UI Components

The primary UI component is `ChatKitPanel.tsx`, which provides the layout structure for the chat interface. This component can be customized to adjust:
- Layout dimensions and positioning
- Visual styling and theming
- Additional UI elements or controls

The component integrates with the ChatKit SDK using the configuration from `config.ts`.

**Sources:** [chatkit/README.md:31]()

---

## Request Flow and Data Model

The following diagram traces a complete request through the system, from user interaction to OpenAI response, showing the actual methods and data structures involved.

### Complete Request Sequence

```mermaid
sequenceDiagram
    participant User
    participant ReactUI as "React UI"
    participant ViteProxy as "Vite Proxy<br/>/chatkit"
    participant FastAPI as "FastAPI<br/>main.py"
    participant Server as "StarterChatServer<br/>server.py"
    participant Store as "MemoryStore<br/>server.py"
    participant Agent as "assistant_agent<br/>run_streamed()"
    participant OpenAI as "OpenAI API"
    
    User->>ReactUI: "Send message"
    ReactUI->>ViteProxy: "POST /chatkit<br/>ChatKitRequestPayload"
    ViteProxy->>FastAPI: "Forward to :8000/chatkit"
    FastAPI->>Server: "chatkit_endpoint()<br/>→ server.process()"
    
    Server->>Server: "respond() generator"
    Server->>Store: "load_thread_items(thread_id, limit=30)"
    Store-->>Server: "List[ThreadItem]"
    
    Server->>Server: "simple_to_agent_input(items)"
    Server->>Agent: "run_streamed(input, context)"
    
    Agent->>OpenAI: "Chat completion request"
    
    loop "Streaming Response"
        OpenAI-->>Agent: "Partial response chunk"
        Agent-->>Server: "yield ThreadStreamEvent"
        Server-->>FastAPI: "yield JSON event"
        FastAPI-->>ViteProxy: "StreamingResponse"
        ViteProxy-->>ReactUI: "SSE chunk"
        ReactUI-->>User: "Update UI incrementally"
    end
    
    Server->>Store: "save_item(thread_id, response_item)"
    Store-->>Server: "Saved"
    
    Server->>Server: "yield final event"
    FastAPI-->>ViteProxy: "Close stream"
    ViteProxy-->>ReactUI: "Stream complete"
```

**Sources:** [chatkit/README.md:13-16]()

### Data Structures

**ChatKitRequestPayload:**
- Contains the user's message, thread context, and request metadata
- Passed from frontend to backend via the `/chatkit` endpoint

**ThreadItem:**
- Represents a single message in the conversation history
- Stored in `MemoryStore.threads` dictionary
- Includes content, role, timestamp, and metadata

**ThreadStreamEvent:**
- Event object yielded during streaming responses
- Contains partial or complete response data
- Serialized to JSON and sent via Server-Sent Events (SSE)

**ThreadMetadata:**
- Stored in `MemoryStore.thread_metadata` dictionary
- Contains thread-level information (creation time, last updated, etc.)

**Sources:** [chatkit/README.md:32]()

---

## Environment Configuration

The application requires specific environment variables to function correctly:

### Required Variables

| Variable | Location | Purpose | Default |
|----------|----------|---------|---------|
| `OPENAI_API_KEY` | Backend | Authenticate with OpenAI API | None (required) |
| `VITE_CHATKIT_API_URL` | Frontend | Backend endpoint URL | `/chatkit` |
| `VITE_CHATKIT_API_DOMAIN_KEY` | Frontend | Domain authentication key | `domain_pk_localhost_dev` |

### Configuration Files

Create a `.env.local` file at the repository root (or in the `chatkit/` directory) with the following format:

```
OPENAI_API_KEY=sk-proj-...
VITE_CHATKIT_API_URL=/chatkit
VITE_CHATKIT_API_DOMAIN_KEY=domain_pk_localhost_dev
```

**Development vs Production:**
- **Development:** Use default values with the Vite proxy handling `/chatkit` routing
- **Production:** Set `VITE_CHATKIT_API_URL` to the full backend URL (e.g., `https://api.example.com/chatkit`) and register a production domain key in the OpenAI dashboard

**Sources:** [chatkit/README.md:18-26](), [chatkit/.env.example:1-3]()

---

## Running the Application

The starter provides a streamlined development workflow using npm scripts:

```bash
npm install    # Install dependencies for both frontend and backend
npm run dev    # Start both servers concurrently
```

### What `npm run dev` Does

1. **Backend Server:** Starts `uvicorn` on `http://127.0.0.1:8000`
   - Serves the FastAPI application from `backend/app/main.py`
   - Exposes the `/chatkit` endpoint
   
2. **Frontend Server:** Starts Vite dev server on `http://127.0.0.1:3000`
   - Serves the React application
   - Configures proxy to forward `/chatkit` requests to port 8000

3. **Access:** Navigate to `http://127.0.0.1:3000` in your browser

The concurrent execution is managed by the root-level `package.json` which coordinates both backend and frontend processes.

**Sources:** [chatkit/README.md:8-16]()

---

## Key Features

### Streaming Responses

The application implements real-time streaming using Server-Sent Events (SSE):

- The `assistant_agent.run_streamed()` method yields partial responses as they're generated
- Each chunk is wrapped in a `ThreadStreamEvent` and sent immediately to the client
- The React frontend updates the UI incrementally as chunks arrive
- This provides a responsive user experience without waiting for complete responses

### Conversation History

The system maintains conversation context by:

1. Loading the 30 most recent messages via `store.load_thread_items(thread_id, limit=30)`
2. Converting them to agent input format with `simple_to_agent_input()`
3. Including this context in the OpenAI API request
4. Persisting new responses with `store.save_item()`

This ensures the AI agent has sufficient context to provide relevant, coherent responses.

### Agent Configuration

The `assistant_agent` is configured with:
- **Model:** `gpt-4o-mini` - A cost-effective, fast model suitable for most chat applications
- **Instructions:** Defines the agent's behavior and personality
- **Context:** Runtime context passed with each request for dynamic behavior

**Sources:** [chatkit/README.md:13-16](), [chatkit/README.md:32]()

---

## Customization Points

The starter application is designed to be customized for specific use cases:

### 1. Persistent Storage

**Location:** [backend/app/server.py]()

The `MemoryStore` implementation is suitable only for development and testing. For production deployments:

1. Create a new class implementing the same interface as `MemoryStore`
2. Add persistence using PostgreSQL, MongoDB, Redis, or another database
3. Implement the required methods: `load_thread_items()`, `save_item()`, `list_thread_metadata()`
4. Replace the `MemoryStore` instantiation in `StarterChatServer`

**Example:**
```python
# Replace:
store = MemoryStore()

# With:
store = PostgresStore(connection_string=os.environ["DATABASE_URL"])
```

### 2. UI Configuration

**Location:** [frontend/src/lib/config.ts]()

Modify the `chatKitConfig` object to change:
- API endpoint URLs
- Domain keys
- Authentication settings
- ChatKit SDK options

### 3. Layout Structure

**Location:** [frontend/src/components/ChatKitPanel.tsx]()

Customize the UI layout by modifying:
- Component structure and hierarchy
- Styling and theming
- Additional UI controls or features
- Integration with other components

### 4. Agent Behavior

**Location:** [backend/app/server.py]()

Modify the `assistant_agent` configuration to change:
- Model selection (e.g., `gpt-4`, `gpt-4-turbo`)
- System instructions and personality
- Temperature and other sampling parameters
- Context preparation logic

### 5. CORS Configuration

**Location:** [backend/app/main.py]()

The default CORS middleware allows all origins (`allow_origins=["*"]`). For production, restrict this to specific domains:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Sources:** [chatkit/README.md:29-32]()

---

## Development Tools

The backend includes development tooling for code quality:

### Python Tooling

- **ruff:** Fast Python linter and formatter
  - Configuration in [backend/pyproject.toml]()
  - Run via CI/CD pipeline
  
- **mypy:** Static type checker
  - Ensures type safety across the codebase
  - Configuration in [backend/pyproject.toml]()

### Ignored Files

The `.gitignore` files exclude:
- Python bytecode (`__pycache__/`, `*.pyc`)
- Virtual environments (`.venv/`)
- Environment files (`.env`)
- Build artifacts and caches

**Sources:** [chatkit/backend/.gitignore:1-9](), [chatkit/.gitignore:1-4]()

---

## Integration with External Services

### OpenAI API

The backend communicates with OpenAI's API through the `openai-chatkit` library:

1. **Authentication:** Uses `OPENAI_API_KEY` from environment variables
2. **Chat Completion:** Sends conversation context and receives streaming responses
3. **Model:** Defaults to `gpt-4o-mini` but can be configured to any OpenAI model

### ChatKit Library

The `openai-chatkit` Python package provides:
- Agent abstraction for managing AI conversations
- Streaming utilities for real-time responses
- Thread management and event handling
- Integration with OpenAI's chat completion API

**Sources:** [chatkit/README.md:3-4](), [chatkit/.env.example:1-3]()

---

## Summary

The self-hosted ChatKit starter application provides a complete, production-ready foundation for building conversational AI applications with full control over infrastructure:

**Key Components:**
- FastAPI backend with streaming support
- React frontend with Vite build tooling
- In-memory storage (replaceable with persistent storage)
- OpenAI API integration via `openai-chatkit` library

**Ideal For:**
- Developers who need full control over backend logic
- Applications requiring custom storage or business logic
- Deployments where infrastructure management is acceptable
- Use cases with specific security or compliance requirements

For a simpler deployment model with reduced operational overhead, consider the managed ChatKit integration documented in [Managed ChatKit (managed-chatkit/)](#4).

**Sources:** [README.md:1-9](), [chatkit/README.md:1-33]()

---

# Page: Architecture Overview

# Architecture Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [chatkit/backend/app/main.py](chatkit/backend/app/main.py)
- [chatkit/backend/app/memory_store.py](chatkit/backend/app/memory_store.py)
- [chatkit/backend/app/server.py](chatkit/backend/app/server.py)

</details>



## Purpose and Scope

This document provides a high-level architectural overview of the self-hosted ChatKit starter application located in the `chatkit/` directory. It describes the core components, their relationships, and the flow of requests through the system.

The self-hosted architecture consists of two independent applications that communicate over HTTP:
- **Backend**: FastAPI application serving the `/chatkit` endpoint (port 8000)
- **Frontend**: Vite + React application providing the user interface (port 3000)

For detailed information about specific components:
- FastAPI entrypoint and endpoint configuration: see page 3.2.1
- StarterChatServer implementation: see page 3.2.2
- MemoryStore data persistence: see page 3.2.3
- AI agent configuration: see page 3.2.4
- Frontend implementation: see page 3.3
- Complete request flow and data model: see page 3.4

## Technology Stack

The self-hosted ChatKit implementation uses the following core technologies:

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend Framework** | FastAPI 0.114-0.116 | High-performance async web framework |
| **Backend Server** | Uvicorn | ASGI server for running FastAPI |
| **Backend Language** | Python 3.11+ | Primary backend language |
| **ChatKit Library** | openai-chatkit 1.4.0-2.0 | OpenAI's ChatKit server SDK |
| **OpenAI SDK** | openai ≥1.40 | OpenAI API client library |
| **Frontend Framework** | React | UI component framework |
| **Frontend Build Tool** | Vite | Fast development and build tooling |
| **Frontend Language** | TypeScript | Type-safe JavaScript |
| **Data Storage** | In-Memory (MemoryStore) | Development/demo storage implementation |

**Sources:** [chatkit/backend/app/main.py:1-36](), [chatkit/backend/app/server.py:1-68](), [chatkit/backend/app/memory_store.py:1-116]()

## Component Architecture

### Backend Components

```mermaid
graph TB
    subgraph "FastAPI Application"
        MAIN["FastAPI app<br/>chatkit/backend/app/main.py<br/>app: FastAPI"]
        ENDPOINT["/chatkit endpoint<br/>main.py:25-35<br/>chatkit_endpoint()"]
        CORS["CORSMiddleware<br/>main.py:14-20"]
    end
    
    subgraph "Server Layer"
        SERVER["StarterChatServer<br/>server.py:31-68<br/>ChatKitServer[dict]"]
        RESPOND["respond()<br/>server.py:38-67<br/>AsyncIterator[ThreadStreamEvent]"]
    end
    
    subgraph "Storage Layer"
        STORE["MemoryStore<br/>memory_store.py:14-116<br/>Store[dict]"]
        THREADS["threads: dict[str, ThreadMetadata]<br/>memory_store.py:16"]
        ITEMS["items: dict[str, list[ThreadItem]]<br/>memory_store.py:17"]
    end
    
    subgraph "AI Agent Layer"
        AGENT["assistant_agent<br/>server.py:20-28<br/>Agent[AgentContext]"]
        RUNNER["Runner.run_streamed()<br/>server.py:60-64"]
    end
    
    subgraph "External"
        OPENAI["OpenAI API<br/>gpt-4.1-mini"]
        CHATKIT_LIB["openai-chatkit<br/>Library"]
    end
    
    MAIN --> ENDPOINT
    MAIN --> CORS
    ENDPOINT --> SERVER
    SERVER --> RESPOND
    RESPOND --> STORE
    RESPOND --> AGENT
    AGENT --> RUNNER
    RUNNER --> CHATKIT_LIB
    CHATKIT_LIB --> OPENAI
    SERVER -.->|"initialized with"| STORE
    STORE --> THREADS
    STORE --> ITEMS
```

**Backend Component Details:**

| Component | File Location | Responsibility |
|-----------|--------------|----------------|
| `FastAPI app` | [chatkit/backend/app/main.py:12]() | Application entrypoint, middleware configuration |
| `chatkit_endpoint()` | [chatkit/backend/app/main.py:25-35]() | HTTP handler for `/chatkit` POST requests |
| `StarterChatServer` | [chatkit/backend/app/server.py:31-68]() | Orchestrates chat responses, inherits from `ChatKitServer[dict]` |
| `MemoryStore` | [chatkit/backend/app/memory_store.py:14-116]() | In-memory data persistence, implements `Store[dict]` interface |
| `assistant_agent` | [chatkit/backend/app/server.py:20-28]() | AI agent configuration with model and instructions |

**Sources:** [chatkit/backend/app/main.py:1-36](), [chatkit/backend/app/server.py:1-68](), [chatkit/backend/app/memory_store.py:1-116]()

### Frontend Components

The frontend is a Vite + React application that communicates with the backend via the `/chatkit` endpoint. Key configuration points include:

| Configuration | Location | Purpose |
|--------------|----------|---------|
| `config.ts` | `chatkit/frontend/src/lib/config.ts` | Connection settings and API URL |
| `ChatKitPanel.tsx` | `chatkit/frontend/src/components/ChatKitPanel.tsx` | Main chat UI component |

The frontend proxies all ChatKit requests to `http://localhost:8000/chatkit` during development. See page 3.3 for detailed frontend architecture.

**Sources:** Based on high-level system architecture diagrams

## Request Flow

### Complete Request Lifecycle

```mermaid
sequenceDiagram
    participant User
    participant Frontend as "React Frontend<br/>Port 3000"
    participant Proxy as "/chatkit<br/>Vite Proxy"
    participant Endpoint as "chatkit_endpoint()<br/>main.py:25"
    participant Server as "StarterChatServer<br/>server.py:31"
    participant Store as "MemoryStore<br/>memory_store.py:14"
    participant Agent as "assistant_agent<br/>server.py:20"
    participant Runner as "Runner.run_streamed()<br/>server.py:60"
    participant OpenAI as "OpenAI API"
    
    User->>Frontend: "Send message"
    Frontend->>Proxy: "POST /chatkit"
    Proxy->>Endpoint: "Forward request<br/>payload: bytes"
    
    Endpoint->>Server: "process(payload, context)<br/>server.py:29"
    
    Server->>Store: "load_thread_items()<br/>thread_id, limit=30<br/>memory_store.py:40-51"
    Store-->>Server: "Page[ThreadItem]<br/>Recent 30 messages"
    
    Server->>Server: "simple_to_agent_input(items)<br/>server.py:52"
    
    Server->>Runner: "run_streamed(agent, input)<br/>server.py:60-64"
    Runner->>Agent: "Execute with context"
    Agent->>OpenAI: "Chat completion request<br/>gpt-4.1-mini"
    
    loop "Streaming Response"
        OpenAI-->>Agent: "Partial response chunk"
        Agent-->>Runner: "Result stream"
        Runner-->>Server: "ThreadStreamEvent"
        Server-->>Endpoint: "StreamingResponse"
        Endpoint-->>Proxy: "text/event-stream"
        Proxy-->>Frontend: "SSE chunk"
        Frontend-->>User: "Update UI"
    end
    
    Server->>Store: "save_item()<br/>memory_store.py:58-64"
    Store-->>Server: "Persisted to memory"
```

**Request Flow Details:**

1. **Request Initiation** - User sends a message through the React frontend, which is proxied to the FastAPI backend at `http://localhost:8000/chatkit`

2. **Endpoint Processing** [chatkit/backend/app/main.py:25-35]() - The `chatkit_endpoint()` function:
   - Receives the raw request payload
   - Calls `chatkit_server.process(payload, {"request": request})`
   - Returns either a `StreamingResponse` or `JSONResponse`

3. **Server Orchestration** [chatkit/backend/app/server.py:38-67]() - The `respond()` method:
   - Loads the most recent 30 thread items using `load_thread_items(limit=MAX_RECENT_ITEMS)` [chatkit/backend/app/server.py:44-50]()
   - Reverses the items to chronological order [chatkit/backend/app/server.py:51]()
   - Converts items to agent-compatible format [chatkit/backend/app/server.py:52]()
   - Prepares `AgentContext` with thread, store, and request context [chatkit/backend/app/server.py:54-58]()

4. **AI Generation** [chatkit/backend/app/server.py:60-64]() - The system:
   - Executes `Runner.run_streamed()` with the `assistant_agent`
   - Streams results through `stream_agent_response()`
   - Yields `ThreadStreamEvent` objects back to the client

5. **Response Streaming** - Events stream back through the call stack as Server-Sent Events (SSE), updating the UI in real-time

**Sources:** [chatkit/backend/app/main.py:25-35](), [chatkit/backend/app/server.py:38-67](), [chatkit/backend/app/memory_store.py:40-51]()

## Data Storage Architecture

### MemoryStore Implementation

```mermaid
graph TB
    subgraph "MemoryStore Class"
        CLASS["MemoryStore<br/>memory_store.py:14<br/>Store[dict]"]
        THREADS_DICT["threads: dict[str, ThreadMetadata]<br/>memory_store.py:16"]
        ITEMS_DICT["items: dict[str, list[ThreadItem]]<br/>memory_store.py:17<br/>defaultdict(list)"]
    end
    
    subgraph "Thread Operations"
        LOAD_THREAD["load_thread()<br/>memory_store.py:19-22"]
        SAVE_THREAD["save_thread()<br/>memory_store.py:24-25"]
        DELETE_THREAD["delete_thread()<br/>memory_store.py:74-76"]
        LOAD_THREADS["load_threads()<br/>memory_store.py:27-38<br/>Returns Page[ThreadMetadata]"]
    end
    
    subgraph "Item Operations"
        LOAD_ITEMS["load_thread_items()<br/>memory_store.py:40-51<br/>Returns Page[ThreadItem]"]
        ADD_ITEM["add_thread_item()<br/>memory_store.py:53-56"]
        SAVE_ITEM["save_item()<br/>memory_store.py:58-64"]
        LOAD_ITEM["load_item()<br/>memory_store.py:66-72"]
        DELETE_ITEM["delete_thread_item()<br/>memory_store.py:78-83"]
    end
    
    subgraph "Pagination"
        PAGINATE["_paginate()<br/>memory_store.py:85-104<br/>Handles sorting & cursors"]
    end
    
    CLASS --> THREADS_DICT
    CLASS --> ITEMS_DICT
    
    LOAD_THREAD --> THREADS_DICT
    SAVE_THREAD --> THREADS_DICT
    DELETE_THREAD --> THREADS_DICT
    DELETE_THREAD --> ITEMS_DICT
    LOAD_THREADS --> THREADS_DICT
    LOAD_THREADS --> PAGINATE
    
    LOAD_ITEMS --> ITEMS_DICT
    LOAD_ITEMS --> PAGINATE
    ADD_ITEM --> ITEMS_DICT
    SAVE_ITEM --> ITEMS_DICT
    LOAD_ITEM --> ITEMS_DICT
    DELETE_ITEM --> ITEMS_DICT
```

**Storage Structure:**

The `MemoryStore` class [chatkit/backend/app/memory_store.py:14-116]() provides in-memory data persistence using two primary dictionaries:

| Data Structure | Type | Purpose |
|---------------|------|---------|
| `threads` | `dict[str, ThreadMetadata]` | Stores thread metadata indexed by thread ID |
| `items` | `dict[str, list[ThreadItem]]` | Stores message items for each thread, using `defaultdict(list)` |

**Key Operations:**

- **Thread Management** - `load_thread()`, `save_thread()`, `delete_thread()` operations for thread metadata
- **Item Management** - `load_thread_items()`, `add_thread_item()`, `save_item()` operations for messages
- **Pagination** - The `_paginate()` helper [chatkit/backend/app/memory_store.py:85-104]() handles cursor-based pagination with sorting
- **Context Limit** - `load_thread_items()` is called with `limit=30` [chatkit/backend/app/server.py:47]() to load recent conversation history

**Production Considerations:**

The `MemoryStore` is suitable only for development and demonstration. Production implementations should replace it with persistent storage such as PostgreSQL, MongoDB, or Redis. The `Store[dict]` interface from `openai-chatkit` provides the contract that must be implemented.

**Note:** Attachment operations [chatkit/backend/app/memory_store.py:108-115]() raise `NotImplementedError` as they are not implemented in this starter.

**Sources:** [chatkit/backend/app/memory_store.py:1-116](), [chatkit/backend/app/server.py:44-50]()

## Rendering Strategy

The application uses a **hybrid rendering approach**:

| Component | Rendering Mode | Rationale |
|-----------|---------------|-----------|
| `RootLayout` | Server Component | Static HTML structure, metadata |
| `page.tsx` | Server Component | Minimal routing logic, no state |
| `App` | Client Component | Requires React hooks and event handlers |
| `ChatKitPanel` | Client Component | Interactive chat interface with state |

This strategy optimizes for:
- **Performance**: Server Components reduce JavaScript bundle size
- **Security**: Server-side API key handling prevents credential exposure
- **Interactivity**: Client Components enable real-time chat features
- **SEO**: Server-rendered HTML improves search engine indexing

The `"use client"` directive at [app/App.tsx:1]() marks the boundary where interactivity begins. All components above this boundary in the tree are Server Components by default.

**Sources:** [app/layout.tsx:1-27](), [app/page.tsx:1-6](), [app/App.tsx:1-35]()

---

# Page: Backend Implementation

# Backend Implementation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [chatkit/backend/app/main.py](chatkit/backend/app/main.py)
- [chatkit/backend/app/memory_store.py](chatkit/backend/app/memory_store.py)
- [chatkit/backend/app/server.py](chatkit/backend/app/server.py)
- [chatkit/backend/pyproject.toml](chatkit/backend/pyproject.toml)

</details>



This document covers the backend implementation of the self-hosted ChatKit starter application. The backend is built with FastAPI and serves as the orchestration layer that processes chat requests, manages conversation state, and integrates with OpenAI's API through the `openai-chatkit` library.

For detailed documentation of specific components, see:
- Page 3.2.1 for the FastAPI entrypoint
- Page 3.2.2 for `StarterChatServer` implementation
- Page 3.2.3 for `MemoryStore` implementation
- Page 3.2.4 for AI agent integration

## Overview

The backend consists of three primary Python modules that work together to provide chat functionality:

### Architecture

```mermaid
graph TB
    subgraph Frontend["Frontend (Port 3000)"]
        UI["React UI"]
    end
    
    subgraph Backend["Backend (Port 8000)"]
        APP["FastAPI app"]
        ENDPOINT["/chatkit endpoint"]
        SERVER["StarterChatServer"]
        STORE["MemoryStore"]
        AGENT["assistant_agent"]
    end
    
    subgraph Libraries["External Libraries"]
        CHATKIT["openai-chatkit"]
        OPENAI["OpenAI API"]
    end
    
    UI -->|"POST /chatkit"| ENDPOINT
    ENDPOINT -->|"chatkit_server.process()"| SERVER
    SERVER -->|"load_thread_items()"| STORE
    SERVER -->|"Runner.run_streamed()"| AGENT
    AGENT -->|"Chat completion"| CHATKIT
    CHATKIT -->|"API calls"| OPENAI
    OPENAI -->|"Stream response"| CHATKIT
    CHATKIT -->|"ThreadStreamEvent"| SERVER
    SERVER -->|"StreamingResponse"| ENDPOINT
    ENDPOINT -->|"SSE stream"| UI
```

**Sources:** [chatkit/backend/app/main.py:1-36](), [chatkit/backend/app/server.py:1-68](), [chatkit/backend/app/memory_store.py:1-116]()

### Key Components

The backend implementation consists of three core modules:

| Module | Primary Class/Object | Purpose |
|--------|---------------------|---------|
| `main.py` | `app` (FastAPI) | HTTP server and `/chatkit` endpoint |
| `server.py` | `StarterChatServer` | Request orchestration and response streaming |
| `memory_store.py` | `MemoryStore` | In-memory conversation persistence |
| `server.py` | `assistant_agent` | AI assistant configuration |

**Sources:** [chatkit/backend/app/main.py:12](), [chatkit/backend/app/server.py:31](), [chatkit/backend/app/memory_store.py:14](), [chatkit/backend/app/server.py:20-28]()

### Technology Stack

The backend uses the following dependencies:

| Dependency | Version Constraint | Purpose |
|-----------|-------------------|---------|
| `fastapi` | `>=0.114,<0.116` | ASGI web framework |
| `uvicorn[standard]` | `>=0.36,<0.37` | ASGI server |
| `openai` | `>=1.40` | OpenAI SDK |
| `openai-chatkit` | `>=1.4.0,<2` | ChatKit server framework |

**Sources:** [chatkit/backend/pyproject.toml:6-11]()

## Component Interactions

The backend components interact in a layered architecture:

### Request Processing Flow

```mermaid
sequenceDiagram
    participant Client as "React Frontend"
    participant Endpoint as "/chatkit endpoint"
    participant Server as "StarterChatServer"
    participant Store as "MemoryStore"
    participant Agent as "assistant_agent"
    participant OpenAI as "OpenAI API"
    
    Client->>Endpoint: "POST /chatkit (payload)"
    Endpoint->>Server: "process(payload, context)"
    Server->>Store: "load_thread_items(thread_id, limit=30)"
    Store-->>Server: "Page[ThreadItem]"
    
    Server->>Server: "simple_to_agent_input(items)"
    Server->>Agent: "Runner.run_streamed(agent, input)"
    
    loop Streaming response
        Agent->>OpenAI: "Chat completion request"
        OpenAI-->>Agent: "Response chunk"
        Agent-->>Server: "ThreadStreamEvent"
        Server-->>Endpoint: "yield event"
        Endpoint-->>Client: "SSE chunk"
    end
    
    Server->>Store: "save_item(thread_id, item)"
```

**Sources:** [chatkit/backend/app/main.py:25-35](), [chatkit/backend/app/server.py:38-67](), [chatkit/backend/app/memory_store.py:40-65]()

### Data Flow Diagram

```mermaid
graph LR
    REQUEST["HTTP Request"]
    PAYLOAD["Request Payload"]
    CONTEXT["Context Dict"]
    
    THREAD["ThreadMetadata"]
    ITEMS["List[ThreadItem]"]
    INPUT["Agent Input"]
    
    EVENTS["ThreadStreamEvent"]
    RESPONSE["StreamingResponse"]
    
    REQUEST --> PAYLOAD
    REQUEST --> CONTEXT
    
    PAYLOAD --> THREAD
    THREAD -->|"load history"| ITEMS
    ITEMS -->|"convert"| INPUT
    
    INPUT -->|"run_streamed()"| EVENTS
    EVENTS -->|"yield"| RESPONSE
```

**Sources:** [chatkit/backend/app/server.py:38-67](), [chatkit/backend/app/memory_store.py:40-51]()

## Core Components

### FastAPI Application

The `app` object in [chatkit/backend/app/main.py:12]() is the ASGI application that serves the backend. It includes:

- CORS middleware configuration for cross-origin requests
- A single POST endpoint at `/chatkit`
- Integration with `StarterChatServer` for request processing

See page 3.2.1 for detailed documentation of the FastAPI entrypoint.

**Sources:** [chatkit/backend/app/main.py:1-36]()

### StarterChatServer

The `StarterChatServer` class extends `ChatKitServer` and implements the core chat logic:

- Maintains a `MemoryStore` instance for conversation persistence
- Implements the `respond()` method to handle chat interactions
- Loads recent conversation history (up to 30 items)
- Orchestrates AI agent execution and streams responses

See page 3.2.2 for detailed documentation of `StarterChatServer`.

**Sources:** [chatkit/backend/app/server.py:31-68]()

### MemoryStore

The `MemoryStore` class implements the ChatKit `Store` interface using in-memory dictionaries:

- Stores thread metadata and thread items
- Provides pagination support for loading history
- Not suitable for production (data lost on restart)
- Should be replaced with persistent storage for production use

See page 3.2.3 for detailed documentation of `MemoryStore`.

**Sources:** [chatkit/backend/app/memory_store.py:14-116]()

### AI Assistant Agent

The `assistant_agent` object is configured with:

- Model: `gpt-4.1-mini`
- Name: "Starter Assistant"
- Instructions for concise, helpful responses

See page 3.2.4 for detailed documentation of AI agent integration.

**Sources:** [chatkit/backend/app/server.py:20-28]()

## Data Structures

The backend works with several key data structures from the `openai-chatkit` library:

### Thread Structures

| Type | Purpose | Key Fields |
|------|---------|-----------|
| `ThreadMetadata` | Thread information | `id`, `created_at`, custom metadata |
| `ThreadItem` | Individual messages | `id`, `role`, `content`, `created_at` |
| `UserMessageItem` | User-authored message | Subtype of `ThreadItem` |
| `Page[T]` | Paginated results | `data`, `has_more`, `after` |

**Sources:** [chatkit/backend/app/memory_store.py:11](), [chatkit/backend/app/server.py:10]()

### Context Objects

The backend uses context dictionaries to pass request-specific information:

```mermaid
graph TB
    REQUEST["FastAPI Request"]
    CONTEXT["Context: dict[str, Any]"]
    
    REQUEST -->|"Wrapped in"| CONTEXT
    
    CONTEXT --> STORE["store.load_thread_items(context)"]
    CONTEXT --> AGENT["AgentContext(request_context)"]
    CONTEXT --> SAVE["store.save_item(context)"]
    
    AGENT --> THREAD["thread: ThreadMetadata"]
    AGENT --> STORE_REF["store: MemoryStore"]
    AGENT --> REQ_CTX["request_context: dict"]
```

The `AgentContext` type provides the agent with access to:
- Current thread metadata
- Store instance for persistence
- Original request context

**Sources:** [chatkit/backend/app/server.py:54-58](), [chatkit/backend/app/main.py:29]()

## Configuration Constants

The backend defines several configuration constants:

| Constant | Value | Purpose | Location |
|----------|-------|---------|----------|
| `MAX_RECENT_ITEMS` | `30` | History items loaded per request | [chatkit/backend/app/server.py:16]() |
| `MODEL` | `"gpt-4.1-mini"` | OpenAI model for assistant | [chatkit/backend/app/server.py:17]() |

These constants control conversation history size and AI model selection.

**Sources:** [chatkit/backend/app/server.py:16-17]()

## Streaming Response Mechanism

The backend uses Server-Sent Events (SSE) to stream AI responses:

### Streaming Flow

```mermaid
graph LR
    AGENT["Runner.run_streamed()"]
    HELPER["stream_agent_response()"]
    EVENTS["ThreadStreamEvent"]
    RESULT["StreamingResult"]
    FASTAPI["StreamingResponse"]
    
    AGENT -->|"yields events"| HELPER
    HELPER -->|"converts to"| EVENTS
    EVENTS -->|"wrapped in"| RESULT
    RESULT -->|"returned as"| FASTAPI
```

The streaming mechanism:
1. `Runner.run_streamed()` executes the agent and yields partial results
2. `stream_agent_response()` converts agent output to `ThreadStreamEvent` objects
3. Each event is yielded back through the response chain
4. FastAPI's `StreamingResponse` sends events as SSE to the client

**Sources:** [chatkit/backend/app/server.py:60-67](), [chatkit/backend/app/main.py:31-32]()

### Response Types

The `/chatkit` endpoint returns one of two response types:

| Type | Condition | Content-Type |
|------|-----------|--------------|
| `StreamingResponse` | When streaming events | `text/event-stream` |
| `Response` or `JSONResponse` | For non-streaming responses | `application/json` |

**Sources:** [chatkit/backend/app/main.py:31-35]()

## User Session Management

### Cookie-Based User Identification

The backend uses HTTP cookies to maintain persistent user identification across multiple session creation requests.

### Cookie Configuration

| Constant | Value | Purpose |
|----------|-------|---------|
| `SESSION_COOKIE_NAME` | `"chatkit_session_id"` | Cookie identifier |
| `SESSION_COOKIE_MAX_AGE` | `60 * 60 * 24 * 30` (30 days) | Cookie lifetime in seconds |

**Sources:** [app/api/create-session/route.ts:12-13]()

### User ID Resolution Process

```mermaid
graph TD
    REQUEST["Incoming Request"]
    COOKIE_HEADER["Extract Cookie header"]
    
    REQUEST --> COOKIE_HEADER
    COOKIE_HEADER --> GCV["getCookieValue()"]
    
    GCV --> CHECK_EXISTING["Check if cookie exists"]
    
    CHECK_EXISTING -->|"Cookie exists"| RETURN_EXISTING["Return existing userId<br/>sessionCookie: null"]
    
    CHECK_EXISTING -->|"No cookie"| GENERATE["Generate new userId"]
    
    GENERATE --> CRYPTO_CHECK["Check crypto.randomUUID available"]
    CRYPTO_CHECK -->|"Available"| UUID["crypto.randomUUID()"]
    CRYPTO_CHECK -->|"Not available"| FALLBACK["Math.random().toString(36).slice(2)"]
    
    UUID --> SERIALIZE["serializeSessionCookie()"]
    FALLBACK --> SERIALIZE
    
    SERIALIZE --> RETURN_NEW["Return new userId<br/>sessionCookie: serialized"]
```

The `resolveUserId` function:
1. Attempts to retrieve an existing user ID from cookies
2. If no cookie exists, generates a new user ID using `crypto.randomUUID()` (or a fallback)
3. Returns both the user ID and an optional cookie string for setting in the response

**Sources:** [app/api/create-session/route.ts:133-150]()

### Cookie Parsing

The `getCookieValue` function parses cookie headers:

```typescript
function getCookieValue(cookieHeader: string | null, name: string): string | null {
  if (!cookieHeader) {
    return null;
  }

  const cookies = cookieHeader.split(";");
  for (const cookie of cookies) {
    const [rawName, ...rest] = cookie.split("=");
    if (!rawName || rest.length === 0) { continue; }
    if (rawName.trim() === name) { return rest.join("=").trim(); }
  }
  return null;
}
```

This function:
- Splits the Cookie header by semicolons
- Iterates through each cookie
- Returns the value when the name matches
- Handles edge cases like missing values or malformed cookies

**Sources:** [app/api/create-session/route.ts:152-164]()

### Cookie Serialization

The `serializeSessionCookie` function creates secure cookie strings:

```mermaid
graph LR
    VALUE["User ID Value"]
    BASE["Base Attributes"]
    ENV["Environment Check"]
    
    VALUE --> ENCODE["encodeURIComponent()"]
    ENCODE --> NAME["chatkit_session_id=VALUE"]
    
    BASE --> PATH["Path=/"]
    BASE --> MAXAGE["Max-Age=2592000"]
    BASE --> HTTP["HttpOnly"]
    BASE --> SAME["SameSite=Lax"]
    
    ENV -->|"production"| SECURE["Secure"]
    
    NAME --> JOIN["Join with '; '"]
    PATH --> JOIN
    MAXAGE --> JOIN
    HTTP --> JOIN
    SAME --> JOIN
    SECURE --> JOIN
    
    JOIN --> COOKIE["Complete Cookie String"]
```

Cookie attributes:

| Attribute | Value | Purpose |
|-----------|-------|---------|
| Name | `chatkit_session_id` | Cookie identifier |
| Value | URL-encoded user ID | User identification |
| `Path` | `/` | Available across entire domain |
| `Max-Age` | `2592000` (30 days) | Long-lived session |
| `HttpOnly` | Set | Prevents JavaScript access (XSS protection) |
| `SameSite` | `Lax` | CSRF protection |
| `Secure` | Production only | HTTPS-only transmission |

**Sources:** [app/api/create-session/route.ts:166-179]()

### Response Cookie Handling

The `buildJsonResponse` function conditionally includes the Set-Cookie header:

```typescript
function buildJsonResponse(
  payload: unknown,
  status: number,
  headers: Record<string, string>,
  sessionCookie: string | null
): Response {
  const responseHeaders = new Headers(headers);

  if (sessionCookie) {
    responseHeaders.append("Set-Cookie", sessionCookie);
  }

  return new Response(JSON.stringify(payload), {
    status,
    headers: responseHeaders,
  });
}
```

This ensures:
- New users receive a Set-Cookie header to persist their ID
- Existing users do not receive redundant cookie updates
- All responses maintain consistent JSON formatting

**Sources:** [app/api/create-session/route.ts:181-197]()

### Security Considerations

The cookie implementation includes several security features:

1. **HttpOnly Flag**: Prevents client-side JavaScript from accessing the cookie, mitigating XSS attacks
2. **SameSite=Lax**: Provides CSRF protection while allowing top-level navigation
3. **Secure Flag (Production)**: Ensures cookies are only transmitted over HTTPS in production environments
4. **Long Expiration**: 30-day lifetime balances user convenience with security
5. **Server-Side Generation**: User IDs are generated server-side, not client-controlled

**Sources:** [app/api/create-session/route.ts:166-179]()

---

# Page: FastAPI Entrypoint

# FastAPI Entrypoint

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [chatkit/backend/app/main.py](chatkit/backend/app/main.py)

</details>



This document describes the FastAPI application entry point for the self-hosted ChatKit backend, located at [chatkit/backend/app/main.py](). This module initializes the FastAPI web server, configures CORS middleware, and exposes the `/chatkit` HTTP endpoint that accepts requests from the ChatKit web component.

**Scope**: This page focuses exclusively on the HTTP layer and FastAPI configuration. For details on how requests are processed after reaching the endpoint, see [StarterChatServer](#3.2.2). For the overall backend architecture, see [Backend Implementation](#3.2).

## Purpose and Responsibilities

The FastAPI entrypoint serves as the HTTP interface layer with the following responsibilities:

| Responsibility | Implementation |
|---------------|----------------|
| **Web Server Initialization** | Creates and configures the FastAPI application instance |
| **CORS Configuration** | Enables cross-origin requests from the frontend |
| **Request Routing** | Maps the `/chatkit` POST endpoint to the server implementation |
| **Payload Proxying** | Forwards raw request bodies to `StarterChatServer` |
| **Response Handling** | Adapts `StreamingResult` or JSON responses to appropriate HTTP formats |

Sources: [chatkit/backend/app/main.py:1-36]()

## Application Structure

```mermaid
graph TB
    subgraph main_py["main.py Module"]
        app["FastAPI app<br/>title: 'ChatKit Starter API'"]
        middleware["CORSMiddleware<br/>allow_origins: ['*']"]
        server_instance["chatkit_server<br/>StarterChatServer instance"]
        endpoint["@app.post('/chatkit')<br/>chatkit_endpoint function"]
    end
    
    app --> middleware
    app --> endpoint
    endpoint --> server_instance
    
    subgraph imports["Imports"]
        fastapi_imports["FastAPI, Request"]
        response_imports["JSONResponse, Response<br/>StreamingResponse"]
        chatkit_imports["StreamingResult"]
        server_import["StarterChatServer"]
    end
    
    imports --> main_py
```

**Diagram: FastAPI Application Initialization Structure**

The module creates a single global `FastAPI` instance and a single `StarterChatServer` instance that persists across requests. The CORS middleware is configured to allow all origins, credentials, methods, and headers, which is appropriate for local development but should be restricted in production deployments.

Sources: [chatkit/backend/app/main.py:6-22]()

## FastAPI Application Initialization

The FastAPI application is initialized at module load time with a descriptive title:

```python
app = FastAPI(title="ChatKit Starter API")
```

This creates the ASGI application that will be served by Uvicorn (see [Getting Started](#2.3) for server startup details).

Sources: [chatkit/backend/app/main.py:12]()

## CORS Middleware Configuration

The application configures permissive CORS settings to enable the frontend (running on port 3000) to communicate with the backend (running on port 8000):

```mermaid
graph LR
    request["Browser Request<br/>Origin: http://localhost:3000"]
    cors["CORSMiddleware"]
    handler["chatkit_endpoint"]
    
    request -->|"Pre-flight OPTIONS"| cors
    cors -->|"Allow: origins, methods, headers"| request
    request -->|"POST /chatkit"| cors
    cors -->|"Validate & Forward"| handler
    handler -->|"Response"| cors
    cors -->|"Add CORS Headers"| request
```

**Diagram: CORS Request Flow**

The middleware configuration at [chatkit/backend/app/main.py:14-20]() uses wildcard permissions:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `allow_origins` | `["*"]` | Accept requests from any origin |
| `allow_credentials` | `True` | Allow cookies and authentication headers |
| `allow_methods` | `["*"]` | Accept all HTTP methods |
| `allow_headers` | `["*"]` | Accept all request headers |

**Note**: This permissive configuration is suitable for local development but should be restricted to specific origins in production environments.

Sources: [chatkit/backend/app/main.py:14-20]()

## Server Instance Management

The `StarterChatServer` is instantiated once at module level:

```python
chatkit_server = StarterChatServer()
```

This singleton pattern ensures that the in-memory `MemoryStore` (see [MemoryStore](#3.2.3)) persists across requests, maintaining conversation history for the lifetime of the backend process. The server instance is shared across all concurrent requests handled by the FastAPI application.

Sources: [chatkit/backend/app/main.py:22]()

## The `/chatkit` Endpoint

The primary HTTP endpoint handles POST requests from the ChatKit web component:

```mermaid
sequenceDiagram
    participant Client as "Frontend<br/>ChatKit Component"
    participant Endpoint as "chatkit_endpoint()<br/>/chatkit POST"
    participant Server as "chatkit_server<br/>StarterChatServer"
    
    Client->>Endpoint: POST /chatkit<br/>request.body()
    Endpoint->>Endpoint: await request.body()
    Endpoint->>Server: await process(payload, context)
    
    alt StreamingResult
        Server-->>Endpoint: StreamingResult instance
        Endpoint->>Endpoint: isinstance(result, StreamingResult)
        Endpoint-->>Client: StreamingResponse<br/>media_type: text/event-stream
    else JSON with .json attribute
        Server-->>Endpoint: Object with .json property
        Endpoint->>Endpoint: hasattr(result, "json")
        Endpoint-->>Client: Response(result.json)<br/>media_type: application/json
    else Plain object
        Server-->>Endpoint: Dict or other object
        Endpoint-->>Client: JSONResponse(result)
    end
```

**Diagram: /chatkit Endpoint Request Handling Flow**

### Endpoint Implementation

The `chatkit_endpoint` function at [chatkit/backend/app/main.py:25-35]() follows this processing pattern:

1. **Extract Payload**: Reads the raw request body using `await request.body()`
2. **Process Request**: Invokes `chatkit_server.process(payload, context)` with the payload and a context dictionary containing the FastAPI `Request` object
3. **Determine Response Type**: Inspects the result to determine the appropriate HTTP response format
4. **Return Response**: Wraps the result in the appropriate FastAPI response class

### Response Type Handling

The endpoint supports three response types through conditional logic:

| Condition | Response Type | Media Type | Use Case |
|-----------|--------------|------------|----------|
| `isinstance(result, StreamingResult)` | `StreamingResponse` | `text/event-stream` | Streaming AI responses with Server-Sent Events |
| `hasattr(result, "json")` | `Response` | `application/json` | Pre-serialized JSON responses |
| Default | `JSONResponse` | `application/json` | Dict or JSON-serializable objects |

This flexible response handling allows the `StarterChatServer` to return different response types based on the request (streaming for chat completion, non-streaming for other operations).

Sources: [chatkit/backend/app/main.py:25-35]()

## Request Context

The endpoint passes a context dictionary to the server's `process` method:

```python
{"request": request}
```

This context provides the `StarterChatServer` access to the raw FastAPI `Request` object, enabling access to headers, query parameters, or other request metadata if needed. Currently, the server implementation does not utilize this context, but it provides an extension point for authentication, rate limiting, or request-specific configuration.

Sources: [chatkit/backend/app/main.py:29]()

## Type Checking and Imports

The module uses specific imports from the `fastapi` package and the `chatkit` library:

```mermaid
graph TB
    subgraph external["External Dependencies"]
        fastapi_lib["fastapi"]
        chatkit_lib["chatkit.server"]
    end
    
    subgraph main_imports["main.py Imports"]
        FastAPI["FastAPI"]
        Request["Request"]
        JSONResponse["JSONResponse"]
        Response["Response"]
        StreamingResponse["StreamingResponse"]
        CORSMiddleware["CORSMiddleware"]
        StreamingResult["StreamingResult"]
    end
    
    subgraph local_imports["Local Imports"]
        StarterChatServer["StarterChatServer<br/>from .server"]
    end
    
    fastapi_lib --> FastAPI
    fastapi_lib --> Request
    fastapi_lib --> JSONResponse
    fastapi_lib --> Response
    fastapi_lib --> StreamingResponse
    fastapi_lib --> CORSMiddleware
    
    chatkit_lib --> StreamingResult
    
    main_imports --> main_py["main.py Module"]
    local_imports --> main_py
```

**Diagram: Import Dependencies**

The type hint `Response` in the function signature at [chatkit/backend/app/main.py:26]() is the base class for FastAPI response types, allowing the function to return any of the specific response subclasses (`StreamingResponse`, `Response`, or `JSONResponse`).

Sources: [chatkit/backend/app/main.py:1-10]()

## Integration with ASGI Server

This FastAPI application is served by Uvicorn, an ASGI web server. The development server is started with the command:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The `app` variable at [chatkit/backend/app/main.py:12]() is the ASGI application that Uvicorn loads and serves. For details on starting the server, see [Running the Application](#2.3).

Sources: [chatkit/backend/app/main.py:12]()

## Error Handling

The endpoint does not implement explicit error handling; exceptions raised by `StarterChatServer.process()` will be caught by FastAPI's default exception handlers and returned as HTTP 500 responses. For production deployments, consider adding custom exception handlers to provide more specific error responses to clients.

Sources: [chatkit/backend/app/main.py:25-35]()

---

# Page: StarterChatServer

# StarterChatServer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [chatkit/backend/app/memory_store.py](chatkit/backend/app/memory_store.py)
- [chatkit/backend/app/server.py](chatkit/backend/app/server.py)

</details>



This document describes the `StarterChatServer` class, which is the core orchestration component of the self-hosted ChatKit backend. This class implements the ChatKit server interface and coordinates conversation handling, history retrieval, agent invocation, and response streaming.

For information about the underlying storage implementation, see [MemoryStore](#3.2.3). For details about the FastAPI entrypoint that uses this server, see [FastAPI Entrypoint](#3.2.1). For agent configuration details, see [AI Agent Integration](#3.2.4).

**Sources:** [chatkit/backend/app/server.py:1-68]()

## Purpose and Scope

The `StarterChatServer` class serves as the main business logic coordinator for chat interactions in the self-hosted ChatKit application. It inherits from `ChatKitServer` provided by the `openai-chatkit` library and implements the `respond` method to handle incoming user messages. The server's responsibilities include:

- Loading recent conversation history from storage
- Converting ChatKit data structures to agent-compatible format
- Invoking the AI assistant agent with proper context
- Streaming response events back to the client
- Managing the lifecycle of chat interactions

**Sources:** [chatkit/backend/app/server.py:31-68]()

## Class Structure

The `StarterChatServer` class extends `ChatKitServer[dict[str, Any]]` and maintains a single instance variable:

```mermaid
classDiagram
    class ChatKitServer~dict~ {
        <<abstract>>
        +respond() AsyncIterator
    }
    
    class StarterChatServer {
        -MemoryStore store
        +__init__()
        +respond() AsyncIterator
    }
    
    class MemoryStore {
        +load_thread_items()
        +save_thread()
        +save_item()
    }
    
    class Agent~AgentContext~ {
        +model: str
        +name: str
        +instructions: str
    }
    
    ChatKitServer~dict~ <|-- StarterChatServer
    StarterChatServer --> MemoryStore : uses
    StarterChatServer ..> Agent~AgentContext~ : invokes
```

**Sources:** [chatkit/backend/app/server.py:31-36]()

### Initialization

The constructor instantiates a `MemoryStore` and passes it to the parent `ChatKitServer` constructor:

| Line | Code Element | Description |
|------|--------------|-------------|
| 34-36 | `__init__` | Initializes `self.store` with new `MemoryStore()` instance and calls parent constructor |

**Sources:** [chatkit/backend/app/server.py:34-36]()

### Type Parameters

The class uses `dict[str, Any]` as its context type parameter. This generic context is passed through the request pipeline and made available to storage operations and agent execution.

**Sources:** [chatkit/backend/app/server.py:31]()

## Component Relationships

The following diagram shows how `StarterChatServer` interacts with other system components using actual code symbols:

```mermaid
graph TB
    FastAPI["FastAPI /chatkit endpoint<br/>main.py"]
    StarterChatServer["StarterChatServer<br/>server.py:31"]
    MemoryStore["MemoryStore<br/>memory_store.py:14"]
    assistant_agent["assistant_agent<br/>server.py:20"]
    Runner["Runner.run_streamed()<br/>agents library"]
    stream_agent_response["stream_agent_response()<br/>chatkit.agents"]
    
    FastAPI -->|"calls process()"| StarterChatServer
    StarterChatServer -->|"respond() method"| StarterChatServer
    StarterChatServer -->|"load_thread_items()"| MemoryStore
    StarterChatServer -->|"simple_to_agent_input()"| stream_agent_response
    StarterChatServer -->|"Runner.run_streamed()"| assistant_agent
    assistant_agent -->|"executes"| Runner
    Runner -->|"yields events"| stream_agent_response
    stream_agent_response -->|"ThreadStreamEvent"| StarterChatServer
    StarterChatServer -->|"yield events"| FastAPI
```

**Sources:** [chatkit/backend/app/server.py:1-68]()

## The respond Method

The `respond` method is the core orchestration function that processes incoming user messages and generates AI responses. This method is called by the ChatKit framework when a user sends a message.

### Method Signature

```python
async def respond(
    self,
    thread: ThreadMetadata,
    item: UserMessageItem | None,
    context: dict[str, Any],
) -> AsyncIterator[ThreadStreamEvent]:
```

| Parameter | Type | Purpose |
|-----------|------|---------|
| `thread` | `ThreadMetadata` | Metadata about the current conversation thread |
| `item` | `UserMessageItem \| None` | The user's message (if creating new message) |
| `context` | `dict[str, Any]` | Request context passed through the pipeline |
| Returns | `AsyncIterator[ThreadStreamEvent]` | Stream of events representing the AI response |

**Sources:** [chatkit/backend/app/server.py:38-43]()

### Execution Flow

The following sequence diagram traces the complete execution path through the `respond` method with actual method calls:

```mermaid
sequenceDiagram
    participant Caller as "ChatKitServer.process()"
    participant Server as "StarterChatServer.respond()"
    participant Store as "MemoryStore.load_thread_items()"
    participant Convert as "simple_to_agent_input()"
    participant Runner as "Runner.run_streamed()"
    participant Stream as "stream_agent_response()"
    
    Caller->>Server: "respond(thread, item, context)"
    
    Server->>Store: "load_thread_items(thread.id, after=None,<br/>limit=30, order='desc')"
    Store-->>Server: "Page[ThreadItem]"
    
    Server->>Server: "reversed(items_page.data)"
    
    Server->>Convert: "simple_to_agent_input(items)"
    Convert-->>Server: "agent_input"
    
    Server->>Server: "AgentContext(thread, store, context)"
    
    Server->>Runner: "run_streamed(assistant_agent,<br/>agent_input, agent_context)"
    Runner-->>Server: "result iterator"
    
    loop "For each event"
        Server->>Stream: "stream_agent_response(agent_context, result)"
        Stream-->>Server: "ThreadStreamEvent"
        Server-->>Caller: "yield ThreadStreamEvent"
    end
```

**Sources:** [chatkit/backend/app/server.py:38-67]()

### Step-by-Step Breakdown

#### Step 1: Load Recent History

```
items_page = await self.store.load_thread_items(
    thread.id,
    after=None,
    limit=MAX_RECENT_ITEMS,
    order="desc",
    context=context,
)
```

The method retrieves the most recent conversation items from the store. The `MAX_RECENT_ITEMS` constant (set to `30`) limits the history window to prevent context overflow. The `order="desc"` parameter loads items in reverse chronological order (newest first).

**Sources:** [chatkit/backend/app/server.py:44-50](), [chatkit/backend/app/server.py:16]()

#### Step 2: Reverse to Chronological Order

```
items = list(reversed(items_page.data))
```

Since the items are loaded in descending order but agents expect chronological order (oldest first), the list is reversed before processing.

**Sources:** [chatkit/backend/app/server.py:51]()

#### Step 3: Convert to Agent Input Format

```
agent_input = await simple_to_agent_input(items)
```

The `simple_to_agent_input` utility function from the `chatkit.agents` module converts ChatKit `ThreadItem` objects into the format expected by the agent library. This typically transforms thread items into a list of messages with roles and content.

**Sources:** [chatkit/backend/app/server.py:52](), [chatkit/backend/app/server.py:8]()

#### Step 4: Prepare Agent Context

```
agent_context = AgentContext(
    thread=thread,
    store=self.store,
    request_context=context,
)
```

An `AgentContext` object is created to provide the agent with access to thread metadata, the storage layer, and the original request context. This allows the agent to perform additional operations if needed.

**Sources:** [chatkit/backend/app/server.py:54-58](), [chatkit/backend/app/server.py:8]()

#### Step 5: Execute Agent with Streaming

```
result = Runner.run_streamed(
    assistant_agent,
    agent_input,
    context=agent_context,
)
```

The `Runner.run_streamed` method from the `agents` library executes the `assistant_agent` with the prepared input and context. This returns an asynchronous iterator that yields partial results as the AI generates its response.

**Sources:** [chatkit/backend/app/server.py:60-64]()

#### Step 6: Stream Response Events

```
async for event in stream_agent_response(agent_context, result):
    yield event
```

The `stream_agent_response` utility function converts agent execution events into `ThreadStreamEvent` objects that conform to the ChatKit protocol. These events are yielded back to the caller, which ultimately streams them to the client via Server-Sent Events (SSE).

**Sources:** [chatkit/backend/app/server.py:66-67](), [chatkit/backend/app/server.py:8]()

## Configuration Constants

Two module-level constants control the assistant's behavior:

| Constant | Value | Purpose | Location |
|----------|-------|---------|----------|
| `MAX_RECENT_ITEMS` | `30` | Maximum number of conversation items to load for context | [chatkit/backend/app/server.py:16]() |
| `MODEL` | `"gpt-4.1-mini"` | OpenAI model identifier used by the assistant | [chatkit/backend/app/server.py:17]() |

**Sources:** [chatkit/backend/app/server.py:16-17]()

## Assistant Agent Configuration

The module defines a pre-configured `assistant_agent` instance that the server uses for all conversations:

```mermaid
graph LR
    assistant_agent["assistant_agent<br/>Agent[AgentContext[dict]]"]
    
    assistant_agent -->|"model"| MODEL["'gpt-4.1-mini'"]
    assistant_agent -->|"name"| NAME["'Starter Assistant'"]
    assistant_agent -->|"instructions"| INSTRUCTIONS["'You are a concise,<br/>helpful assistant...'"]
```

The agent is configured with:
- **Model**: `gpt-4.1-mini` for efficient, cost-effective responses
- **Name**: `"Starter Assistant"` for identification
- **Instructions**: System prompt emphasizing concise, direct responses

**Sources:** [chatkit/backend/app/server.py:20-28]()

## Integration with ChatKit Framework

The `StarterChatServer` integrates with the ChatKit framework through inheritance and protocol compliance:

### Base Class Integration

By inheriting from `ChatKitServer[dict[str, Any]]`, the class gains:
- The `process` method that handles incoming HTTP requests
- Automatic thread creation and management
- Message validation and error handling
- Streaming response coordination

The server only needs to implement the `respond` method to define custom behavior.

**Sources:** [chatkit/backend/app/server.py:31](), [chatkit/backend/app/server.py:9]()

### Store Protocol

The server passes its `MemoryStore` instance to the parent `ChatKitServer` constructor, enabling the framework to:
- Create and retrieve thread metadata
- Store user messages before calling `respond`
- Save assistant responses after streaming completes
- Support pagination and thread listing operations

**Sources:** [chatkit/backend/app/server.py:35-36]()

### Event Streaming Protocol

The `respond` method's return type (`AsyncIterator[ThreadStreamEvent]`) allows the ChatKit framework to:
- Stream partial responses to clients in real-time
- Update message status as it evolves
- Handle errors and completion events
- Maintain consistency between server state and client UI

**Sources:** [chatkit/backend/app/server.py:43]()

## Import Dependencies

The `StarterChatServer` implementation relies on several key imports:

| Import | Source | Purpose |
|--------|--------|---------|
| `Runner` | `agents` | Executes agent logic with streaming support |
| `Agent` | `agents` | Agent class for defining AI assistants |
| `AgentContext` | `chatkit.agents` | Context wrapper for agent execution |
| `simple_to_agent_input` | `chatkit.agents` | Converts thread items to agent format |
| `stream_agent_response` | `chatkit.agents` | Converts agent events to ChatKit events |
| `ChatKitServer` | `chatkit.server` | Base class providing server functionality |
| `ThreadMetadata`, `ThreadStreamEvent`, `UserMessageItem` | `chatkit.types` | ChatKit data types |
| `MemoryStore` | `.memory_store` | Local storage implementation |

**Sources:** [chatkit/backend/app/server.py:1-13]()

---

# Page: MemoryStore

# MemoryStore

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [chatkit/backend/app/memory_store.py](chatkit/backend/app/memory_store.py)
- [chatkit/backend/app/server.py](chatkit/backend/app/server.py)

</details>



## Purpose and Scope

The `MemoryStore` class provides a simple in-memory implementation of the ChatKit `Store` interface for development and demonstration purposes. It stores conversation threads and thread items in Python dictionaries, allowing the self-hosted ChatKit application to maintain conversation state without requiring database infrastructure. 

**Important**: This implementation is intended for development only. For production deployments, see [Persistent Storage Migration](#8.2) for guidance on replacing this with a database-backed store.

For information about how the `StarterChatServer` uses this store to orchestrate chat responses, see [StarterChatServer](#3.2.2).

**Sources:** [chatkit/backend/app/memory_store.py:1-4]()

## Class Overview and Interface Compliance

The `MemoryStore` class implements the `Store[dict]` interface from the `chatkit.store` module. It provides async methods for managing thread metadata and thread items, along with pagination support for listing operations.

```mermaid
classDiagram
    class Store~dict~ {
        <<interface>>
        +load_thread(thread_id, context) ThreadMetadata
        +save_thread(thread, context) None
        +load_threads(limit, after, order, context) Page~ThreadMetadata~
        +load_thread_items(thread_id, after, limit, order, context) Page~ThreadItem~
        +add_thread_item(thread_id, item, context) None
        +save_item(thread_id, item, context) None
        +load_item(thread_id, item_id, context) ThreadItem
        +delete_thread(thread_id, context) None
        +delete_thread_item(thread_id, item_id, context) None
        +save_attachment(attachment, context) None
        +load_attachment(attachment_id, context) Attachment
        +delete_attachment(attachment_id, context) None
    }
    
    class MemoryStore {
        -dict~str, ThreadMetadata~ threads
        -dict~str, list~ThreadItem~~ items
        +__init__()
        +load_thread(thread_id, context) ThreadMetadata
        +save_thread(thread, context) None
        +load_threads(limit, after, order, context) Page~ThreadMetadata~
        +load_thread_items(thread_id, after, limit, order, context) Page~ThreadItem~
        +add_thread_item(thread_id, item, context) None
        +save_item(thread_id, item, context) None
        +load_item(thread_id, item_id, context) ThreadItem
        +delete_thread(thread_id, context) None
        +delete_thread_item(thread_id, item_id, context) None
        -_paginate(rows, after, limit, order, sort_key, cursor_key) Page
    }
    
    class NotFoundError {
        <<exception>>
    }
    
    Store~dict~ <|.. MemoryStore : implements
    MemoryStore ..> NotFoundError : raises
```

**Sources:** [chatkit/backend/app/memory_store.py:10-14]()

## Data Structures

The `MemoryStore` maintains two primary in-memory data structures:

| Data Structure | Type | Purpose | Initialization |
|---|---|---|---|
| `threads` | `dict[str, ThreadMetadata]` | Stores thread metadata keyed by thread ID | Empty dict |
| `items` | `dict[str, list[ThreadItem]]` | Stores lists of thread items, keyed by thread ID | `defaultdict(list)` |

The use of `defaultdict(list)` for `items` ensures that accessing a non-existent thread ID automatically creates an empty list, simplifying item append operations.

```mermaid
graph TB
    subgraph MemoryStore["MemoryStore Instance"]
        threads["threads: dict[str, ThreadMetadata]"]
        items["items: dict[str, list[ThreadItem]]"]
    end
    
    subgraph ThreadsDict["threads Dictionary"]
        thread1["'thread-123'"]
        thread2["'thread-456'"]
        metadata1["ThreadMetadata(id='thread-123', ...)"]
        metadata2["ThreadMetadata(id='thread-456', ...)"]
    end
    
    subgraph ItemsDict["items Dictionary"]
        items1["'thread-123'"]
        items2["'thread-456'"]
        itemlist1["[ThreadItem, ThreadItem, ...]"]
        itemlist2["[ThreadItem, ThreadItem, ...]"]
    end
    
    threads --> ThreadsDict
    items --> ItemsDict
    
    thread1 --> metadata1
    thread2 --> metadata2
    items1 --> itemlist1
    items2 --> itemlist2
```

**Sources:** [chatkit/backend/app/memory_store.py:15-17]()

## Thread Operations

The `MemoryStore` provides basic CRUD operations for thread metadata:

### load_thread

Retrieves thread metadata by thread ID. Raises `NotFoundError` if the thread does not exist.

```python
async def load_thread(self, thread_id: str, context: dict) -> ThreadMetadata
```

**Implementation:** Direct dictionary lookup with error handling at [chatkit/backend/app/memory_store.py:19-22]()

### save_thread

Stores or updates thread metadata. Uses the thread's `id` field as the dictionary key.

```python
async def save_thread(self, thread: ThreadMetadata, context: dict) -> None
```

**Implementation:** Simple dictionary assignment at [chatkit/backend/app/memory_store.py:24-25]()

### load_threads

Returns a paginated list of all threads, sorted by `created_at` timestamp. Supports ascending (`"asc"`) or descending (`"desc"`) order.

```python
async def load_threads(
    self, limit: int, after: str | None, order: str, context: dict
) -> Page[ThreadMetadata]
```

**Implementation:** Delegates to `_paginate` helper at [chatkit/backend/app/memory_store.py:27-38]()

### delete_thread

Removes a thread and all its associated items from both dictionaries. Uses `pop` with a default to avoid errors if the thread doesn't exist.

```python
async def delete_thread(self, thread_id: str, context: dict) -> None
```

**Implementation:** [chatkit/backend/app/memory_store.py:74-76]()

**Sources:** [chatkit/backend/app/memory_store.py:19-38](), [chatkit/backend/app/memory_store.py:74-76]()

## Thread Item Operations

Thread items represent individual messages and AI responses within a conversation thread:

### load_thread_items

Returns a paginated list of items for a specific thread, sorted by `created_at` timestamp. This is the primary method used by `StarterChatServer` to load conversation history.

```python
async def load_thread_items(
    self, thread_id: str, after: str | None, limit: int, order: str, context: dict
) -> Page[ThreadItem]
```

**Usage in StarterChatServer:** The server loads the most recent 30 items in descending order, then reverses the list to present conversation history chronologically at [chatkit/backend/app/server.py:44-51]()

**Implementation:** [chatkit/backend/app/memory_store.py:40-51]()

### add_thread_item

Appends a new item to the thread's item list. The `defaultdict` ensures the list exists even for new threads.

```python
async def add_thread_item(self, thread_id: str, item: ThreadItem, context: dict) -> None
```

**Implementation:** [chatkit/backend/app/memory_store.py:53-56]()

### save_item

Updates an existing item or appends it if not found. Performs a linear search through the thread's items to locate matching item by ID.

```python
async def save_item(self, thread_id: str, item: ThreadItem, context: dict) -> None
```

**Implementation:** [chatkit/backend/app/memory_store.py:58-64]()

### load_item

Retrieves a specific item by ID from a thread. Raises `NotFoundError` if the item is not found.

```python
async def load_item(self, thread_id: str, item_id: str, context: dict) -> ThreadItem
```

**Implementation:** [chatkit/backend/app/memory_store.py:66-72]()

### delete_thread_item

Removes a specific item from a thread by creating a new list that excludes the target item.

```python
async def delete_thread_item(self, thread_id: str, item_id: str, context: dict) -> None
```

**Implementation:** [chatkit/backend/app/memory_store.py:78-83]()

**Sources:** [chatkit/backend/app/memory_store.py:40-83](), [chatkit/backend/app/server.py:44-51]()

## Pagination Logic

The `_paginate` helper method implements cursor-based pagination for both threads and thread items. This pattern allows clients to efficiently page through large result sets.

### Pagination Algorithm

```mermaid
flowchart TD
    Start["_paginate(rows, after, limit, order, sort_key, cursor_key)"]
    Sort["Sort rows using sort_key<br/>reverse=(order == 'desc')"]
    CheckAfter{"after cursor<br/>provided?"}
    FindCursor["Find cursor position<br/>in sorted rows"]
    SetStart["start = cursor_position + 1"]
    DefaultStart["start = 0"]
    Slice["data = sorted_rows[start:start+limit]"]
    CheckMore["has_more = start + limit < len(sorted_rows)"]
    SetAfter["next_after = cursor_key(data[-1])<br/>if has_more and data"]
    ReturnPage["Return Page(data, has_more, next_after)"]
    
    Start --> Sort
    Sort --> CheckAfter
    CheckAfter -->|Yes| FindCursor
    CheckAfter -->|No| DefaultStart
    FindCursor --> SetStart
    DefaultStart --> Slice
    SetStart --> Slice
    Slice --> CheckMore
    CheckMore --> SetAfter
    SetAfter --> ReturnPage
```

### Pagination Parameters

| Parameter | Type | Purpose |
|---|---|---|
| `rows` | `list` | Complete list of items to paginate |
| `after` | `str \| None` | Cursor value from previous page (item ID) |
| `limit` | `int` | Maximum number of items to return |
| `order` | `str` | Sort order: `"asc"` or `"desc"` |
| `sort_key` | `callable` | Function to extract sort value from item |
| `cursor_key` | `callable` | Function to extract cursor value (typically ID) |

### Return Value

The method returns a `Page` object containing:

- `data`: List of items for the current page
- `has_more`: Boolean indicating if more items exist beyond this page
- `after`: Cursor value to use for fetching the next page (ID of last item in `data`)

**Sources:** [chatkit/backend/app/memory_store.py:85-104]()

## Attachment Operations

The `MemoryStore` does not implement attachment storage operations. All three attachment methods raise `NotImplementedError`:

- `save_attachment` [chatkit/backend/app/memory_store.py:108-109]()
- `load_attachment` [chatkit/backend/app/memory_store.py:111-112]()
- `delete_attachment` [chatkit/backend/app/memory_store.py:114-115]()

Applications requiring attachment support must implement these methods or use a different store implementation.

**Sources:** [chatkit/backend/app/memory_store.py:106-115]()

## Integration with StarterChatServer

The `StarterChatServer` instantiates a single `MemoryStore` instance and uses it to manage conversation state across all chat sessions.

```mermaid
sequenceDiagram
    participant Server as StarterChatServer
    participant Store as MemoryStore
    
    Note over Server: User sends message
    
    Server->>Store: load_thread_items(thread_id,<br/>after=None, limit=30,<br/>order="desc", context)
    Store-->>Server: Page[ThreadItem] (most recent 30)
    
    Note over Server: Reverse items for chronological order
    Note over Server: Convert to agent input
    Note over Server: Stream AI response
    
    Server->>Store: save_item(thread_id, response_item, context)
    Store-->>Server: None
    
    Note over Store: Response persisted in items dict
```

### Key Usage Patterns

**Initialization:** The store is created in the server's `__init__` method and passed to the parent `ChatKitServer` class at [chatkit/backend/app/server.py:34-36]()

**Loading Context:** The `respond` method loads up to `MAX_RECENT_ITEMS` (30) items in descending order to provide conversation context to the AI agent at [chatkit/backend/app/server.py:44-51]()

**Order Reversal:** Items are loaded newest-first (`order="desc"`) then reversed to present them chronologically to the agent. This approach optimizes for loading recent history efficiently.

**Persistence:** The ChatKit framework automatically persists AI responses by calling `save_item` on the store.

**Sources:** [chatkit/backend/app/server.py:16](), [chatkit/backend/app/server.py:34-36](), [chatkit/backend/app/server.py:44-51]()

## Limitations and Production Considerations

The `MemoryStore` has several critical limitations that make it unsuitable for production use:

| Limitation | Impact | Production Solution |
|---|---|---|
| **No Persistence** | All data lost on server restart | Replace with database-backed store |
| **No Concurrency Control** | Race conditions in multi-threaded environments | Use database transactions or locks |
| **Linear Search** | `O(n)` lookup performance for items | Index items by ID in database |
| **Memory Bound** | All data must fit in RAM | Use persistent storage with pagination |
| **No Attachments** | Cannot store file uploads | Implement attachment storage (e.g., S3 + DB metadata) |
| **Single Instance** | No horizontal scaling possible | Use shared database across server instances |

For production deployment guidance, see [Persistent Storage Migration](#8.2).

**Sources:** [chatkit/backend/app/memory_store.py:1-4]()

---

# Page: AI Agent Integration

# AI Agent Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [chatkit/backend/app/memory_store.py](chatkit/backend/app/memory_store.py)
- [chatkit/backend/app/server.py](chatkit/backend/app/server.py)

</details>



## Purpose and Scope

This document explains how the self-hosted ChatKit backend integrates an AI agent to generate conversational responses. It covers the `assistant_agent` configuration, context preparation from conversation history, and streaming response generation using the OpenAI Agents SDK. This agent is invoked by the `StarterChatServer.respond` method (see page 3.2.2) and uses conversation history from `MemoryStore` (see page 3.2.3).

## Agent Configuration

The AI agent is configured as a module-level constant in [chatkit/backend/app/server.py:20-28](), defining its behavior and capabilities.

### Agent Definition

```python
assistant_agent = Agent[AgentContext[dict[str, Any]]](
    model=MODEL,
    name="Starter Assistant",
    instructions=(
        "You are a concise, helpful assistant. "
        "Keep replies short and focus on directly answering "
        "the user's request."
    ),
)
```

### Configuration Parameters

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `model` | `"gpt-4.1-mini"` | The OpenAI model used for response generation (defined at [chatkit/backend/app/server.py:17]()) |
| `name` | `"Starter Assistant"` | Identifier for the agent in logs and debugging |
| `instructions` | System prompt | Defines the agent's behavior and response style |

The `MODEL` constant is set to `"gpt-4.1-mini"` at [chatkit/backend/app/server.py:17](), providing a balance between capability and cost for the starter application.

### Type Parameterization

The agent is parameterized with `AgentContext[dict[str, Any]]`, indicating it operates within a ChatKit agent context that carries a generic dictionary for request-specific data. The `AgentContext` type comes from the `chatkit.agents` module and provides access to the thread, store, and request context during agent execution.

**Sources:** [chatkit/backend/app/server.py:20-28](), [chatkit/backend/app/server.py:17]()

## Context Preparation

Before invoking the agent, the `respond` method prepares conversation context from stored history. This process involves loading recent messages, reversing their order, and converting them to agent-compatible format.

### Context Preparation Flow

**Diagram: Context Preparation Pipeline**

```mermaid
flowchart TD
    START["StarterChatServer.respond()"]
    LOAD["store.load_thread_items()"]
    REVERSE["list(reversed(items_page.data))"]
    CONVERT["simple_to_agent_input(items)"]
    CREATE["AgentContext creation"]
    AGENT["assistant_agent execution"]
    
    START --> LOAD
    LOAD --> REVERSE
    REVERSE --> CONVERT
    CONVERT --> CREATE
    CREATE --> AGENT
    
    LOAD -.->|"MAX_RECENT_ITEMS = 30"| LOAD
    LOAD -.->|"order='desc'"| LOAD
```

### Loading Recent Items

The method loads up to 30 recent conversation items at [chatkit/backend/app/server.py:44-50]():

```python
items_page = await self.store.load_thread_items(
    thread.id,
    after=None,
    limit=MAX_RECENT_ITEMS,
    order="desc",
    context=context,
)
```

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `thread.id` | Current thread identifier | Scopes the query to the active conversation |
| `after` | `None` | No pagination cursor (fetch from start) |
| `limit` | `30` | Maximum items to load (defined by `MAX_RECENT_ITEMS` at [chatkit/backend/app/server.py:16]()) |
| `order` | `"desc"` | Newest items first (reversed later for chronological order) |

### Chronological Ordering

Items are loaded in descending order (newest first) for efficient pagination, then reversed at [chatkit/backend/app/server.py:51]() to provide chronological order to the agent:

```python
items = list(reversed(items_page.data))
```

This ensures the agent processes messages in the order they were sent, which is critical for maintaining conversation coherence.

### Agent Input Conversion

The `simple_to_agent_input` function at [chatkit/backend/app/server.py:52]() converts ChatKit `ThreadItem` objects into the format expected by the Agents SDK:

```python
agent_input = await simple_to_agent_input(items)
```

This function, imported from `chatkit.agents`, transforms thread items (which may include user messages, assistant messages, and system events) into agent-compatible message structures.

### AgentContext Creation

An `AgentContext` is instantiated at [chatkit/backend/app/server.py:54-58]() to provide the agent with access to necessary resources:

**Diagram: AgentContext Structure**

```mermaid
classDiagram
    class AgentContext {
        +ThreadMetadata thread
        +MemoryStore store
        +dict request_context
    }
    
    class assistant_agent {
        run_streamed(input, context)
    }
    
    AgentContext --> assistant_agent : "passed to"
```

```python
agent_context = AgentContext(
    thread=thread,
    store=self.store,
    request_context=context,
)
```

| Field | Type | Purpose |
|-------|------|---------|
| `thread` | `ThreadMetadata` | Current thread metadata for context |
| `store` | `MemoryStore` | Store instance for persisting agent-generated items |
| `request_context` | `dict[str, Any]` | Request-specific data passed through the system |

**Sources:** [chatkit/backend/app/server.py:44-58](), [chatkit/backend/app/server.py:16]()

## Streaming Response Generation

The agent generates responses using a streaming execution model, allowing real-time updates to be sent to the client as the AI generates its reply.

### Streaming Execution

**Diagram: Streaming Response Flow**

```mermaid
sequenceDiagram
    participant Respond as "StarterChatServer.respond()"
    participant Runner as "Runner.run_streamed()"
    participant Agent as "assistant_agent"
    participant OpenAI as "OpenAI API"
    participant Stream as "stream_agent_response()"
    participant Client as "Client (via SSE)"
    
    Respond->>Runner: "run_streamed(agent, input, context)"
    Runner->>Agent: "Execute with agent_input"
    Agent->>OpenAI: "Chat completion request"
    
    loop "Streaming chunks"
        OpenAI-->>Agent: "Response chunk"
        Agent-->>Runner: "Partial result"
        Runner-->>Stream: "Agent result iterator"
        Stream-->>Respond: "ThreadStreamEvent"
        Respond-->>Client: "Event chunk"
    end
```

The streaming process is initiated at [chatkit/backend/app/server.py:60-64]():

```python
result = Runner.run_streamed(
    assistant_agent,
    agent_input,
    context=agent_context,
)
```

### Runner.run_streamed

The `Runner.run_streamed` method (from the `agents` library imported at [chatkit/backend/app/server.py:7]()) executes the agent with streaming enabled. This returns an iterator that yields partial results as the agent processes the input and receives responses from the OpenAI API.

| Parameter | Type | Purpose |
|-----------|------|---------|
| First argument | `Agent[AgentContext[dict]]` | The `assistant_agent` instance to execute |
| `agent_input` | Converted message format | Prepared conversation history and current message |
| `context` | `AgentContext` | Runtime context with thread, store, and request data |

### Event Streaming

The raw agent result stream is converted to `ThreadStreamEvent` objects at [chatkit/backend/app/server.py:66-67]():

```python
async for event in stream_agent_response(agent_context, result):
    yield event
```

The `stream_agent_response` function (imported from `chatkit.agents` at [chatkit/backend/app/server.py:8]()) transforms agent execution events into ChatKit-compatible `ThreadStreamEvent` objects. These events are yielded from the `respond` method, allowing the FastAPI endpoint to stream them to the client using Server-Sent Events (SSE).

### Event Types

The streamed events may include:

| Event Type | Purpose |
|------------|---------|
| Message delta events | Partial text content as it's generated |
| Function call events | Tool invocations if the agent uses functions |
| Completion events | Signal the end of response generation |
| Error events | Communicate failures during generation |

**Sources:** [chatkit/backend/app/server.py:60-67](), [chatkit/backend/app/server.py:7-8]()

## Integration with ChatKit Server

The agent integration operates within the broader ChatKit server architecture, connecting conversation management with AI response generation.

**Diagram: Agent Integration Architecture**

```mermaid
graph TB
    subgraph "FastAPI Application"
        ENDPOINT["/chatkit endpoint"]
    end
    
    subgraph "StarterChatServer"
        RESPOND["respond() method"]
    end
    
    subgraph "Agent Execution"
        LOAD["load_thread_items()"]
        CONVERT["simple_to_agent_input()"]
        CONTEXT["AgentContext creation"]
        RUNNER["Runner.run_streamed()"]
        STREAM["stream_agent_response()"]
    end
    
    subgraph "External Dependencies"
        STORE["MemoryStore"]
        AGENT["assistant_agent"]
        OPENAI["OpenAI API"]
    end
    
    ENDPOINT --> RESPOND
    RESPOND --> LOAD
    LOAD --> STORE
    LOAD --> CONVERT
    CONVERT --> CONTEXT
    CONTEXT --> RUNNER
    RUNNER --> AGENT
    AGENT --> OPENAI
    OPENAI -.->|"streaming"| RUNNER
    RUNNER --> STREAM
    STREAM -.->|"ThreadStreamEvent"| RESPOND
    RESPOND -.->|"yield events"| ENDPOINT
```

### Call Chain

The agent is invoked through this call chain:

1. **FastAPI Endpoint** (`/chatkit`) receives a request
2. **ChatKitServer** processes the payload (see page 3.2.1)
3. **StarterChatServer.respond** orchestrates the response (see page 3.2.2)
4. **Context Preparation** loads and converts history
5. **Runner.run_streamed** executes the `assistant_agent`
6. **stream_agent_response** converts results to `ThreadStreamEvent`
7. **FastAPI** streams events back to the client

### Data Dependencies

| Component | Purpose | Source |
|-----------|---------|--------|
| `thread` | Current conversation metadata | Passed from `ChatKitServer` |
| `self.store` | Access to conversation history | Initialized in `StarterChatServer.__init__` at [chatkit/backend/app/server.py:34-36]() |
| `context` | Request-specific data | Passed through from endpoint |

The `respond` method at [chatkit/backend/app/server.py:38-67]() serves as the orchestration point, coordinating between the store, agent, and streaming infrastructure to generate AI responses.

**Sources:** [chatkit/backend/app/server.py:31-67](), [chatkit/backend/app/server.py:1-13]()

## Customization Points

The agent integration provides several customization opportunities for developers adapting the starter application.

### Model Selection

The model can be changed by modifying the `MODEL` constant at [chatkit/backend/app/server.py:17]():

```python
MODEL = "gpt-4.1-mini"  # Change to "gpt-4o", "gpt-3.5-turbo", etc.
```

Different models offer tradeoffs between cost, speed, and capability.

### Agent Instructions

The agent's behavior is controlled by the `instructions` parameter at [chatkit/backend/app/server.py:23-27](). Modify this to change the agent's personality, response style, or task focus:

```python
instructions=(
    "You are a concise, helpful assistant. "
    "Keep replies short and focus on directly answering "
    "the user's request."
)
```

### Context Window Size

The number of recent messages provided to the agent is controlled by `MAX_RECENT_ITEMS` at [chatkit/backend/app/server.py:16]():

```python
MAX_RECENT_ITEMS = 30  # Adjust based on context requirements
```

Increasing this value provides more conversation history but increases token usage and latency. Decreasing it reduces costs but may limit the agent's ability to maintain context over longer conversations.

### Agent Capabilities

The `assistant_agent` can be extended with additional capabilities by:

1. **Adding tools/functions**: Configure the agent with function calling capabilities
2. **Implementing multi-agent systems**: Replace the single agent with orchestrated multi-agent workflows
3. **Custom processing**: Modify `simple_to_agent_input` to include additional context or preprocessing

**Sources:** [chatkit/backend/app/server.py:16-28]()

## API Request Flow Summary

```mermaid
sequenceDiagram
    participant Client as "Client Browser"
    participant Route as "POST /api/create-session"
    participant Config as "Environment & Config"
    participant OpenAI as "api.openai.com/v1/chatkit/sessions"
    
    Client->>Route: "POST request"
    Route->>Config: "Read OPENAI_API_KEY"
    Config-->>Route: "API key"
    Route->>Config: "Read CHATKIT_API_BASE"
    Config-->>Route: "Base URL or default"
    Route->>Config: "Read WORKFLOW_ID"
    Config-->>Route: "Workflow ID"
    
    Route->>OpenAI: "POST with Bearer token"
    Note over OpenAI: "Headers:<br/>- Authorization: Bearer {key}<br/>- OpenAI-Beta: chatkit_beta=v1<br/>- Content-Type: application/json<br/><br/>Body:<br/>{workflow: {id}, user}"
    
    alt Success (200)
        OpenAI-->>Route: "{client_secret, expires_after}"
        Route-->>Client: "Session credentials"
    else Error (4xx/5xx)
        OpenAI-->>Route: "Error response"
        Route->>Route: "extractUpstreamError()"
        Route->>Route: "console.error()"
        Route-->>Client: "Error details"
    else Exception
        Route->>Route: "catch block"
        Route->>Route: "console.error()"
        Route-->>Client: "{error: 'Unexpected error'}"
    end
```

**Sources:** [app/api/create-session/route.ts:15-120](), [lib/config.ts:1-6](), [.env.example:1-2]()

---

# Page: Frontend Implementation

# Frontend Implementation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [chatkit/.env.example](chatkit/.env.example)
- [chatkit/.gitignore](chatkit/.gitignore)
- [chatkit/README.md](chatkit/README.md)
- [chatkit/backend/.gitignore](chatkit/backend/.gitignore)
- [chatkit/backend/app/__init__.py](chatkit/backend/app/__init__.py)
- [chatkit/frontend/.gitignore](chatkit/frontend/.gitignore)

</details>



This page documents the frontend implementation of the self-hosted ChatKit starter application located in the `chatkit/frontend/` directory. The frontend is a single-page application built with Vite, React, and TypeScript that provides a chat interface for interacting with the ChatKit backend.

For detailed information about backend components that the frontend communicates with, see [Backend Implementation](#3.2). For specifics about the technology stack and build configuration, see [Technology Stack](#3.3.1). For configuration and customization options, see [Configuration & Customization](#3.3.2).

**Sources:** [chatkit/README.md:1-33]()

---

## Purpose and Architecture

The frontend serves as the user-facing chat interface that communicates with the FastAPI backend through a proxied `/chatkit` endpoint. The application runs on `127.0.0.1:3000` during development and uses Vite's dev server to proxy backend requests.

```mermaid
graph TB
    subgraph Browser["Browser (Port 3000)"]
        User["User Interaction"]
        ReactUI["React UI Components"]
        ConfigModule["config.ts<br/>Connection Settings"]
        ChatPanel["ChatKitPanel.tsx<br/>Main Layout"]
    end
    
    subgraph ViteDevServer["Vite Dev Server"]
        DevServer["vite dev"]
        ProxyMiddleware["/chatkit Proxy"]
    end
    
    subgraph Backend["Backend (Port 8000)"]
        FastAPIEndpoint["/chatkit Endpoint"]
    end
    
    User --> ReactUI
    ReactUI --> ConfigModule
    ReactUI --> ChatPanel
    ChatPanel --> ProxyMiddleware
    ProxyMiddleware --> FastAPIEndpoint
    DevServer -.->|"Serves"| ReactUI
    
    FastAPIEndpoint -.->|"Stream/JSON Response"| ChatPanel
```

**Diagram: Frontend Request Flow Architecture**

The frontend follows a standard React application pattern where user interactions trigger API calls through the Vite proxy, which forwards requests to the backend without requiring CORS configuration during development.

**Sources:** [chatkit/README.md:13-16]()

---

## Directory Structure

The frontend code is organized in the `chatkit/frontend/` directory with a standard Vite + React project layout:

```mermaid
graph TB
    Frontend["chatkit/frontend/"]
    
    Frontend --> SrcDir["src/"]
    Frontend --> PublicDir["public/"]
    Frontend --> ConfigFiles["Configuration Files"]
    Frontend --> IgnoreFile[".gitignore"]
    
    SrcDir --> LibDir["lib/"]
    SrcDir --> ComponentsDir["components/"]
    SrcDir --> MainEntry["main.tsx<br/>Application Entry"]
    
    LibDir --> ConfigTS["config.ts<br/>Connection Settings"]
    
    ComponentsDir --> ChatKitPanelTSX["ChatKitPanel.tsx<br/>Main Layout Component"]
    
    ConfigFiles --> PackageJSON["package.json"]
    ConfigFiles --> ViteConfig["vite.config.ts"]
    ConfigFiles --> TSConfig["tsconfig.json"]
    ConfigFiles --> ESLintConfig[".eslintrc"]
    
    IgnoreFile --> IgnoredFiles["node_modules/<br/>dist/<br/>.DS_Store<br/>.next/<br/>npm-debug.log*<br/>*.tsbuildinfo"]
```

**Diagram: Frontend Directory Structure**

The directory structure separates concerns:
- `src/lib/` contains configuration and utility modules
- `src/components/` contains React components
- Configuration files at the root manage build, type checking, and linting
- The `.gitignore` file excludes build artifacts and dependencies

**Sources:** [chatkit/README.md:30-32](), [chatkit/frontend/.gitignore:1-8]()

---

## Development Server and Build System

The frontend uses Vite as its build tool and development server. Starting the application with `npm run dev` launches both the backend and frontend servers concurrently:

| Server | Port | Purpose |
|--------|------|---------|
| FastAPI Backend | `127.0.0.1:8000` | Handles chat requests and OpenAI integration |
| Vite Frontend | `127.0.0.1:3000` | Serves React application and proxies `/chatkit` requests |

```mermaid
sequenceDiagram
    participant Dev as "npm run dev"
    participant Backend as "FastAPI<br/>127.0.0.1:8000"
    participant Frontend as "Vite Dev Server<br/>127.0.0.1:3000"
    participant Browser as "Browser"
    
    Dev->>Backend: "Start uvicorn"
    Dev->>Frontend: "Start vite dev"
    
    Note over Backend,Frontend: Both servers running concurrently
    
    Browser->>Frontend: "GET /"
    Frontend-->>Browser: "React Application"
    
    Browser->>Frontend: "POST /chatkit"
    Frontend->>Backend: "Proxy to 127.0.0.1:8000/chatkit"
    Backend-->>Frontend: "Stream Response"
    Frontend-->>Browser: "Forward Stream"
```

**Diagram: Development Server Startup and Request Flow**

The Vite development server provides hot module replacement (HMR) for rapid development iteration, while the proxy configuration eliminates the need for CORS configuration during local development.

**Sources:** [chatkit/README.md:8-16]()

---

## Proxy Configuration

The frontend communicates with the backend through a proxy at the `/chatkit` path. This proxy is configured in the Vite development server and ensures that API requests are seamlessly forwarded to the FastAPI backend.

```mermaid
graph LR
    subgraph ClientSide["Client-Side (Port 3000)"]
        ReactApp["React Application"]
        FetchCall["fetch('/chatkit', ...)"]
    end
    
    subgraph ViteProxy["Vite Proxy Layer"]
        ProxyRule["/chatkit → 127.0.0.1:8000"]
    end
    
    subgraph BackendSide["Backend (Port 8000)"]
        FastAPIApp["FastAPI Application"]
        ChatKitEndpoint["POST /chatkit"]
    end
    
    ReactApp --> FetchCall
    FetchCall --> ProxyRule
    ProxyRule --> ChatKitEndpoint
    ChatKitEndpoint --> FastAPIApp
```

**Diagram: Proxy Request Forwarding**

The proxy configuration allows the frontend to make requests to a relative path (`/chatkit`) rather than hardcoding the backend URL, which simplifies deployment configuration.

**Sources:** [chatkit/README.md:15-16]()

---

## Environment Variables

The frontend uses Vite's environment variable system, which requires all client-side variables to be prefixed with `VITE_`. Two environment variables control the frontend's connection to the backend:

| Variable | Default Value | Purpose |
|----------|---------------|---------|
| `VITE_CHATKIT_API_URL` | `/chatkit` | API endpoint URL for ChatKit requests |
| `VITE_CHATKIT_API_DOMAIN_KEY` | `domain_pk_localhost_dev` | Domain key for authentication/validation |

```mermaid
graph TB
    EnvFile[".env.local<br/>Root Directory"]
    
    EnvFile --> BackendVar["OPENAI_API_KEY<br/>(Backend Only)"]
    EnvFile --> FrontendVars["VITE_* Variables"]
    
    FrontendVars --> APIUrl["VITE_CHATKIT_API_URL"]
    FrontendVars --> DomainKey["VITE_CHATKIT_API_DOMAIN_KEY"]
    
    APIUrl --> ConfigTS["frontend/src/lib/config.ts"]
    DomainKey --> ConfigTS
    
    ConfigTS --> ReactComponents["React Components"]
    
    BackendVar --> FastAPI["FastAPI Backend"]
```

**Diagram: Environment Variable Flow**

Environment variables are loaded from `.env.local` at the repository root. The `VITE_` prefixed variables are made available to the frontend code through Vite's `import.meta.env` object and are typically accessed through the `config.ts` module.

For production deployments, `VITE_CHATKIT_API_DOMAIN_KEY` must be set to a registered domain key obtained from the OpenAI dashboard.

**Sources:** [chatkit/README.md:18-26](), [chatkit/.env.example:1-3]()

---

## Component Architecture

The frontend implements a component-based architecture using React. The main layout component is `ChatKitPanel.tsx`, which provides the overall chat interface structure.

```mermaid
graph TB
    MainTSX["main.tsx<br/>Application Entry Point"]
    
    MainTSX --> RootComponent["Root React Component"]
    
    RootComponent --> ChatKitPanelTSX["ChatKitPanel.tsx<br/>Main Layout Component"]
    
    ChatKitPanelTSX --> ConfigTS["config.ts<br/>Connection Configuration"]
    
    ConfigTS --> EnvVars["Environment Variables<br/>VITE_CHATKIT_API_URL<br/>VITE_CHATKIT_API_DOMAIN_KEY"]
    
    ChatKitPanelTSX --> ChatInterface["Chat Interface Elements"]
    ChatKitPanelTSX --> APIClient["API Communication Logic"]
    
    APIClient --> ChatKitEndpoint["/chatkit Endpoint<br/>via Proxy"]
```

**Diagram: React Component Hierarchy**

The component architecture separates concerns:
- **Configuration Layer** (`config.ts`): Centralizes connection settings and environment variable access
- **Layout Layer** (`ChatKitPanel.tsx`): Provides the main UI structure and layout
- **API Communication**: Handles HTTP requests to the `/chatkit` endpoint

**Sources:** [chatkit/README.md:29-32]()

---

## Customization Points

The frontend provides clear customization points for developers to adapt the application to their needs:

| File | Purpose | Customization Examples |
|------|---------|------------------------|
| `frontend/src/lib/config.ts` | Connection settings | API URL, domain key, timeout values |
| `frontend/src/components/ChatKitPanel.tsx` | Layout structure | UI components, styling, chat panel layout |

```mermaid
graph TB
    Developer["Developer Customization"]
    
    Developer --> UICustom["UI Customization"]
    Developer --> ConnCustom["Connection Customization"]
    
    UICustom --> ChatKitPanelTSX["ChatKitPanel.tsx<br/>Adjust layout, styling,<br/>component structure"]
    
    ConnCustom --> ConfigTS["config.ts<br/>Update API URL,<br/>domain key,<br/>connection settings"]
    
    ChatKitPanelTSX -.->|"Reads from"| ConfigTS
    
    ConfigTS --> EnvVars["Environment Variables<br/>VITE_CHATKIT_API_URL<br/>VITE_CHATKIT_API_DOMAIN_KEY"]
```

**Diagram: Frontend Customization Points**

Common customization scenarios include:
- Modifying the chat interface layout in `ChatKitPanel.tsx`
- Adjusting API connection settings in `config.ts`
- Updating environment variables for different deployment environments
- Adding additional UI components or modifying existing ones

**Sources:** [chatkit/README.md:28-32]()

---

## Build and Deployment

The frontend build process is managed by Vite and configured through `package.json` and `vite.config.ts`. Build artifacts are excluded from version control:

```mermaid
graph LR
    Source["Source Files<br/>src/**/*.tsx<br/>src/**/*.ts"]
    
    Source --> ViteBuild["vite build"]
    
    ViteBuild --> DistDir["dist/<br/>Production Build"]
    
    DistDir --> StaticAssets["Static Assets<br/>JS, CSS, HTML"]
    
    GitIgnore[".gitignore"] -.->|"Excludes"| DistDir
    GitIgnore -.->|"Excludes"| NodeModules["node_modules/"]
    GitIgnore -.->|"Excludes"| BuildArtifacts["*.tsbuildinfo<br/>npm-debug.log*"]
```

**Diagram: Build Process and Ignored Artifacts**

The `.gitignore` file ensures that build artifacts, dependencies, and temporary files are not committed to version control:
- `node_modules/` - NPM dependencies
- `dist/` - Production build output
- `.DS_Store` - macOS system files
- `*.tsbuildinfo` - TypeScript incremental build cache
- `npm-debug.log*` - NPM error logs

**Sources:** [chatkit/frontend/.gitignore:1-8]()

---

## Integration with Backend

The frontend integrates with the backend through the `/chatkit` endpoint, which is documented in detail in the Backend Implementation section. The frontend is responsible for:

1. **Configuration Management**: Loading and providing connection settings from environment variables
2. **Request Formatting**: Preparing chat requests in the format expected by the backend
3. **Response Handling**: Processing streaming responses from the ChatKit server
4. **UI Updates**: Rendering chat messages and updating the interface in real-time

For details about the backend endpoint structure and expected request/response formats, see [FastAPI Entrypoint](#3.2.1). For the complete request flow through both frontend and backend, see [Request Flow & Data Model](#3.4).

**Sources:** [chatkit/README.md:1-33]()

---

# Page: Technology Stack

# Technology Stack

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [chatkit/.env.example](chatkit/.env.example)
- [chatkit/.gitignore](chatkit/.gitignore)
- [chatkit/README.md](chatkit/README.md)
- [chatkit/backend/.gitignore](chatkit/backend/.gitignore)
- [chatkit/backend/app/__init__.py](chatkit/backend/app/__init__.py)
- [chatkit/frontend/.gitignore](chatkit/frontend/.gitignore)

</details>



## Purpose and Scope

This page documents the frontend technology stack for the self-hosted ChatKit starter application located in the `chatkit/frontend/` directory. It covers the core build tool (Vite), UI framework (React), type system (TypeScript), and supporting development tooling.

For backend technology stack information, see [Backend Dependencies](#5.1). For configuration and customization of the frontend, see [Configuration & Customization](#3.3.2).

---

## Core Technology Stack

The frontend uses a modern JavaScript toolchain optimized for developer experience and production performance:

| Technology | Version | Purpose |
|------------|---------|---------|
| Node.js | 22 | JavaScript runtime environment |
| Vite | Latest | Build tool and development server |
| React | Latest | UI framework |
| TypeScript | Latest | Type-safe JavaScript superset |
| ESLint | Latest | Code quality and style enforcement |

**Sources:** [chatkit/README.md:3-4]()

---

## Vite Build System

### Overview

Vite serves as the build tool and development server for the frontend. It provides:

- **Fast Hot Module Replacement (HMR)** for instant feedback during development
- **Optimized production builds** with code splitting and tree shaking
- **Native ESM support** for modern browser compatibility
- **Development proxy** for routing API requests to the backend

```mermaid
graph TB
    subgraph ViteDev["Vite Development Server (Port 3000)"]
        DevServer["vite serve"]
        HMR["Hot Module Replacement"]
        Proxy["Proxy Configuration"]
    end
    
    subgraph Build["Vite Build Process"]
        Rollup["Rollup Bundler"]
        OptJS["JavaScript Optimization"]
        OptCSS["CSS Optimization"]
        Assets["Static Asset Handling"]
    end
    
    subgraph Output["Build Output"]
        DistDir["dist/"]
        Index["index.html"]
        BundleJS["bundled JavaScript"]
        BundleCSS["bundled CSS"]
    end
    
    DevServer --> HMR
    DevServer --> Proxy
    Proxy -->|"/chatkit"| Backend["FastAPI Backend :8000"]
    
    Rollup --> OptJS
    Rollup --> OptCSS
    Rollup --> Assets
    
    OptJS --> DistDir
    OptCSS --> DistDir
    Assets --> DistDir
    Index --> DistDir
    BundleJS --> DistDir
    BundleCSS --> DistDir
```

**Diagram: Vite Development and Build Architecture**

**Sources:** [chatkit/README.md:13-16]()

### Development Server Configuration

The development server runs on `127.0.0.1:3000` and includes a proxy configuration for API routing:

- **Base URL:** `http://127.0.0.1:3000`
- **Proxy Path:** `/chatkit` forwards requests to the FastAPI backend
- **Target Backend:** `http://127.0.0.1:8000/chatkit`

This proxy eliminates CORS issues during local development by making the frontend and backend appear to be served from the same origin.

**Sources:** [chatkit/README.md:15-16]()

### Build Output

Production builds are written to the `dist/` directory, which contains:

```mermaid
graph LR
    DistRoot["dist/"]
    
    DistRoot --> IndexHTML["index.html"]
    DistRoot --> AssetsDir["assets/"]
    
    AssetsDir --> JSChunks["*.js (chunked bundles)"]
    AssetsDir --> CSSFiles["*.css (optimized styles)"]
    AssetsDir --> StaticAssets["images, fonts, etc."]
```

**Diagram: Build Output Structure**

The `dist/` directory is excluded from version control and should be deployed to a static hosting service or CDN.

**Sources:** [chatkit/frontend/.gitignore:2]()

---

## React Framework

React provides the component-based UI architecture. The application uses:

- **Functional components** with React Hooks for state management
- **React's concurrent rendering** for responsive UI updates
- **Component composition** for modular, reusable UI elements

### Key React Integration Points

```mermaid
graph TB
    subgraph ReactApp["React Application"]
        Root["Application Root"]
        Components["UI Components"]
        State["React State Hooks"]
    end
    
    subgraph ChatKitIntegration["ChatKit Integration"]
        ChatKitPanel["ChatKitPanel.tsx"]
        Config["config.ts"]
    end
    
    subgraph Runtime["Browser Runtime"]
        DOM["DOM Rendering"]
        Events["Event Handling"]
    end
    
    Root --> Components
    Components --> ChatKitPanel
    Config --> ChatKitPanel
    ChatKitPanel --> State
    
    State --> DOM
    Events --> State
```

**Diagram: React Application Structure**

The primary integration point is `frontend/src/components/ChatKitPanel.tsx`, which renders the chat interface and manages conversation state.

**Sources:** [chatkit/README.md:31]()

---

## TypeScript Integration

TypeScript provides static type checking for improved code quality and developer experience:

- **Type-safe API contracts** between frontend and backend
- **Enhanced IDE support** with autocomplete and inline documentation
- **Compile-time error detection** before runtime issues occur

The TypeScript configuration is managed through `tsconfig.json` and integrated directly with Vite's build process—no separate compilation step required.

**Sources:** Inferred from standard Vite+React+TypeScript project structure

---

## Development Tooling

### ESLint

ESLint enforces code quality standards and style consistency across the frontend codebase:

```mermaid
graph LR
    Code["TypeScript/JSX Files"]
    ESLint["ESLint Parser & Rules"]
    Output["Lint Results"]
    
    Code --> ESLint
    ESLint --> Output
    
    ESLint -.->|Config| ESLintRC["eslint.config.js"]
    ESLint -.->|Rules| TypeScriptPlugin["@typescript-eslint"]
    ESLint -.->|Rules| ReactPlugin["eslint-plugin-react"]
```

**Diagram: ESLint Validation Pipeline**

ESLint runs automatically in CI/CD and can be executed locally before committing code. For detailed CI/CD integration, see [Node.js Quality Checks](#6.3).

**Sources:** Inferred from CI/CD workflow documentation

### Build Artifacts

The following directories are generated during development and build processes:

| Directory | Purpose | Version Control |
|-----------|---------|-----------------|
| `node_modules/` | Installed npm dependencies | Excluded (`.gitignore`) |
| `dist/` | Production build output | Excluded (`.gitignore`) |
| `.DS_Store` | macOS metadata | Excluded (`.gitignore`) |
| `.next/` | Build cache (if present) | Excluded (`.gitignore`) |
| `*.tsbuildinfo` | TypeScript incremental build info | Excluded (`.gitignore`) |

**Sources:** [chatkit/frontend/.gitignore:1-7]()

---

## Technology Stack Diagram

The following diagram maps the frontend technology stack to specific code entities and runtime processes:

```mermaid
graph TB
    subgraph RuntimeEnv["Node.js 22 Runtime"]
        NodeExec["node executable"]
        NPM["npm package manager"]
    end
    
    subgraph BuildTools["Build Toolchain"]
        ViteExec["vite CLI"]
        ViteConfig["vite.config.ts"]
        TSCompiler["TypeScript Compiler (esbuild)"]
    end
    
    subgraph SourceCode["Source Code (src/)"]
        TSXFiles["*.tsx Components"]
        TSFiles["*.ts Modules"]
        ConfigTS["lib/config.ts"]
        ChatKitPanelTSX["components/ChatKitPanel.tsx"]
    end
    
    subgraph QualityTools["Code Quality"]
        ESLintTool["eslint CLI"]
        ESLintConfig["eslint.config.js"]
        TSConfig["tsconfig.json"]
    end
    
    subgraph Runtime["Browser Runtime"]
        ReactDOM["React DOM"]
        ViteDev["Vite Dev Server :3000"]
        ProxyMiddleware["/chatkit Proxy"]
    end
    
    NPM -->|"npm install"| NodeModules["node_modules/"]
    NPM -->|"npm run dev"| ViteExec
    NPM -->|"npm run build"| ViteExec
    NPM -->|"npm run lint"| ESLintTool
    
    ViteExec --> ViteConfig
    ViteExec --> TSCompiler
    TSCompiler --> TSConfig
    
    TSXFiles --> TSCompiler
    TSFiles --> TSCompiler
    ConfigTS --> TSCompiler
    ChatKitPanelTSX --> TSCompiler
    
    TSCompiler -->|Development| ViteDev
    TSCompiler -->|Production| DistDir["dist/"]
    
    ViteDev --> ProxyMiddleware
    ProxyMiddleware -->|Forward| Backend["FastAPI :8000"]
    ViteDev --> ReactDOM
    
    ESLintTool --> ESLintConfig
    ESLintTool --> TSXFiles
    ESLintTool --> TSFiles
```

**Diagram: Complete Frontend Technology Stack and Code Entity Mapping**

**Sources:** [chatkit/README.md:3-16](), [chatkit/frontend/.gitignore:1-7]()

---

## Environment Configuration

The frontend reads configuration from environment variables prefixed with `VITE_`:

| Variable | Default | Purpose |
|----------|---------|---------|
| `VITE_CHATKIT_API_URL` | `/chatkit` | Backend API endpoint URL |
| `VITE_CHATKIT_API_DOMAIN_KEY` | `domain_pk_localhost_dev` | ChatKit domain authentication key |

These variables are defined in `.env.local` at the repository root and are embedded into the built JavaScript bundles at build time by Vite.

**Sources:** [chatkit/README.md:21-22](), [chatkit/.env.example:2-3]()

---

## Development Workflow Integration

The frontend integrates with the overall development workflow through npm scripts:

```mermaid
graph LR
    Dev["npm run dev"]
    Build["npm run build"]
    Lint["npm run lint"]
    CI["npm ci"]
    
    Dev -->|Starts| ViteDevServer["Vite Dev Server"]
    Dev -->|Starts| BackendServer["FastAPI Backend (concurrent)"]
    
    Build -->|Generates| DistOutput["dist/ directory"]
    
    Lint -->|Runs| ESLintCheck["ESLint validation"]
    
    CI -->|Installs| CleanDeps["Clean dependencies"]
    CI -->|Used in| GHActions["GitHub Actions"]
```

**Diagram: NPM Script Integration**

The `npm run dev` command starts both the frontend and backend servers concurrently, providing a complete development environment with a single command.

**Sources:** [chatkit/README.md:8-16]()

---

## Summary

The frontend technology stack prioritizes developer experience and modern web standards:

- **Vite** provides instant feedback through HMR and fast build times
- **React** enables component-based UI development with declarative syntax
- **TypeScript** catches errors at compile time and improves code maintainability
- **ESLint** enforces consistent code style and quality standards

This stack requires Node.js 22 and integrates seamlessly with the FastAPI backend through Vite's proxy configuration during development.

**Sources:** [chatkit/README.md:1-33](), [chatkit/frontend/.gitignore:1-7](), [chatkit/.env.example:1-3]()

---

# Page: Configuration & Customization

## Customization Workflow

The typical workflow for customizing the frontend configuration:

```mermaid
graph TB
    DEV["Developer"]
    
    subgraph "Configuration Changes"
        CONFIG_EDIT["Modify config.ts<br/>Update connection settings"]
        PANEL_EDIT["Modify ChatKitPanel.tsx<br/>Adjust UI layout"]
        ENV_EDIT["Modify .env.local<br/>Set environment variables"]
    end
    
    RUN["Run: npm run dev<br/>Start development servers"]
    
    subgraph "Vite Build"
        BUILD["Vite reads .env.local"]
        BUNDLE["Build frontend bundle"]
        HMR["Hot Module Reload"]
    end
    
    BROWSER["View in Browser<br/>Immediate feedback"]
    
    DEV -->|"Edit files"| CONFIG_EDIT
    DEV -->|"Edit files"| PANEL_EDIT
    DEV -->|"Edit files"| ENV_EDIT
    
    CONFIG_EDIT --> RUN
    PANEL_EDIT --> RUN
    ENV_EDIT --> RUN
    
    RUN --> BUILD
    BUILD --> BUNDLE
    BUNDLE --> HMR
    HMR --> BROWSER
```

**Description:** Developers modify configuration files and environment variables, then run `npm run dev` to start the development servers. Vite's hot module reload provides immediate feedback for most changes without requiring a full page reload.

**Sources:** [chatkit/README.md:8-10](), [chatkit/README.md:28-32]()

## Integration with Backend Configuration

The frontend configuration must align with backend settings to establish proper communication:

**Configuration Alignment:**

| Frontend Setting | Backend Requirement | Integration Point |
|------------------|---------------------|-------------------|
| `VITE_CHATKIT_API_URL` | FastAPI `/chatkit` endpoint | HTTP connection path |
| `VITE_CHATKIT_API_DOMAIN_KEY` | Domain validation logic | Authentication |
| Port 3000 (dev) | Port 8000 (backend) | Development proxy |

The backend FastAPI application must expose the `/chatkit` endpoint (documented in section 3.2.1) at the URL specified in `VITE_CHATKIT_API_URL` for the frontend to function correctly. During development, this is handled automatically by the Vite proxy configuration.

**Sources:** [chatkit/README.md:15-16](), [chatkit/README.md:21-22]()

## Common Customization Tasks

### Changing the API Endpoint

To connect to a different backend URL:

1. Update `VITE_CHATKIT_API_URL` in `.env.local`
2. Restart the development server: `npm run dev`
3. Verify the connection in browser developer tools

### Updating the Domain Key

To use a different ChatKit domain:

1. Register a domain key in the OpenAI dashboard
2. Update `VITE_CHATKIT_API_DOMAIN_KEY` in `.env.local`
3. Restart the development server to rebuild with the new key

### Modifying the UI Layout

To adjust the chat interface layout:

1. Open `frontend/src/components/ChatKitPanel.tsx`
2. Modify component structure, styling, or behavior
3. Save the file to trigger hot module reload
4. Review changes immediately in the browser

**Sources:** [chatkit/README.md:28-32]()

## Best Practices

### Configuration Management

- **Environment Files:** Use `.env.local` for local secrets; never commit this file to version control
- **Default Values:** Provide sensible defaults in `config.ts` for optional settings
- **Type Safety:** Leverage TypeScript types to catch configuration errors at compile time
- **Documentation:** Comment configuration options to explain their purpose and valid values

### Customization Strategy

- **Incremental Changes:** Start with small modifications to understand their impact
- **Version Control:** Commit configuration changes separately from feature development
- **Testing:** Verify functionality with both development and production configurations
- **Documentation:** Document custom modifications for team members and future reference

**Sources:** [chatkit/README.md:28-32](), [chatkit/.gitignore:2-3]()

## Relationship to Other Components

The frontend configuration documented on this page coordinates with several other system components:

- **Backend Configuration (3.2.1):** The backend FastAPI application must expose the endpoint specified in `VITE_CHATKIT_API_URL`
- **Environment Variables (2.2):** Environment setup provides the values read by the configuration module
- **Request Flow (3.4):** Configuration determines the endpoint used in the complete request flow from user to backend

The frontend serves as the user-facing interface that relies on properly configured backend services and environment variables to function correctly.

**Sources:** [chatkit/README.md:15-16](), [chatkit/README.md:28-32]()
# Configuration & Customization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [chatkit/.env.example](chatkit/.env.example)
- [chatkit/.gitignore](chatkit/.gitignore)
- [chatkit/README.md](chatkit/README.md)
- [chatkit/backend/.gitignore](chatkit/backend/.gitignore)
- [chatkit/backend/app/__init__.py](chatkit/backend/app/__init__.py)

</details>



This document details the frontend configuration and customization points for the self-hosted ChatKit starter application. The frontend is built with Vite + React and provides two primary customization areas: connection settings in `frontend/src/lib/config.ts` and layout adjustments in `frontend/src/components/ChatKitPanel.tsx`.

## Purpose and Scope

The self-hosted ChatKit frontend configuration system serves to:
- Connect the frontend to the FastAPI backend via configurable endpoints
- Define authentication credentials through domain keys
- Provide customizable UI layout and components
- Separate configuration from implementation for easy modification

The configuration system reads environment variables prefixed with `VITE_` at build time and makes them available to the frontend application.

## Configuration Files

### frontend/src/lib/config.ts

This file exports configuration constants used throughout the frontend application. It primarily handles connection settings to the backend API:

**Key Configuration Values:**

| Setting | Environment Variable | Default | Purpose |
|---------|---------------------|---------|---------|
| API URL | `VITE_CHATKIT_API_URL` | `/chatkit` | Backend endpoint path for chat requests |
| Domain Key | `VITE_CHATKIT_API_DOMAIN_KEY` | `domain_pk_localhost_dev` | ChatKit authentication domain key |

The `VITE_` prefix is a Vite convention that makes environment variables available in the browser bundle at build time. Vite automatically exposes variables starting with `VITE_` to client-side code through `import.meta.env`.

**Sources:** [chatkit/README.md:21-22](), [chatkit/.env.example:2-3]()

### frontend/src/components/ChatKitPanel.tsx

This file contains the main UI layout component that integrates with the ChatKit UI library. The component:
- Renders the chat interface
- Connects to the backend using configuration from `config.ts`
- Handles user interactions and message display
- Manages the visual layout and styling

Modifications to this file enable customization of the UI layout, component arrangement, and visual presentation.

**Sources:** [chatkit/README.md:31]()

## Configuration Flow

```mermaid
graph TB
    ENV_FILE[".env.local<br/>Environment File"]
    VITE_URL["VITE_CHATKIT_API_URL"]
    VITE_KEY["VITE_CHATKIT_API_DOMAIN_KEY"]
    
    BUILD["Vite Build Process"]
    
    CONFIG["frontend/src/lib/config.ts<br/>Configuration Module"]
    
    PANEL["frontend/src/components/ChatKitPanel.tsx<br/>Main UI Component"]
    
    BACKEND["FastAPI Backend<br/>/chatkit endpoint<br/>Port 8000"]
    
    ENV_FILE -->|"Read at build time"| BUILD
    BUILD -->|"Expose as import.meta.env"| VITE_URL
    BUILD -->|"Expose as import.meta.env"| VITE_KEY
    
    VITE_URL -->|"Import"| CONFIG
    VITE_KEY -->|"Import"| CONFIG
    
    CONFIG -->|"Import constants"| PANEL
    
    PANEL -->|"HTTP POST request"| BACKEND
```

**Description:** Environment variables are read at build time by Vite and exposed through `import.meta.env`. The configuration module imports these values and exports them as constants. The `ChatKitPanel` component imports these constants to establish the backend connection.

**Sources:** [chatkit/README.md:15-16](), [chatkit/README.md:21-22](), [chatkit/README.md:30-31]()

## Environment Variable Configuration

### Development Setup

For local development, create a `.env.local` file in the `chatkit/` directory with the following variables:

```
OPENAI_API_KEY=sk-proj-...
VITE_CHATKIT_API_URL=/chatkit
VITE_CHATKIT_API_DOMAIN_KEY=domain_pk_localhost_dev
```

**Variable Details:**

| Variable | Required | Purpose |
|----------|----------|---------|
| `OPENAI_API_KEY` | Yes (backend) | OpenAI API authentication key for backend |
| `VITE_CHATKIT_API_URL` | No | Backend endpoint URL (defaults to `/chatkit`) |
| `VITE_CHATKIT_API_DOMAIN_KEY` | No | ChatKit domain key (defaults to `domain_pk_localhost_dev`) |

The `VITE_CHATKIT_API_URL` uses a relative path `/chatkit` which is automatically proxied to the FastAPI backend during development. The Vite development server forwards requests to port 8000 where the backend runs.

**Sources:** [chatkit/.env.example:1-3](), [chatkit/README.md:20-22](), [chatkit/README.md:15-16]()

### Production Setup

For production deployments, update the environment variables:

1. **Register a Domain Key:** Obtain a production domain key from the OpenAI dashboard
2. **Set Full Backend URL:** Configure `VITE_CHATKIT_API_URL` with the complete backend URL
3. **Update Domain Key:** Set `VITE_CHATKIT_API_DOMAIN_KEY` to the production key

Example production configuration:

```
VITE_CHATKIT_API_URL=https://api.yourapp.com/chatkit
VITE_CHATKIT_API_DOMAIN_KEY=domain_pk_prod_abc123xyz
```

**Sources:** [chatkit/README.md:25-26]()

## Connection Architecture

```mermaid
graph LR
    USER["User Browser"]
    
    subgraph Frontend["Frontend (Port 3000)"]
        PANEL["ChatKitPanel.tsx<br/>UI Component"]
        CONFIG["config.ts<br/>API URL & Domain Key"]
    end
    
    subgraph DevProxy["Development Proxy"]
        VITE["Vite Dev Server<br/>Proxies /chatkit"]
    end
    
    subgraph Backend["Backend (Port 8000)"]
        ENDPOINT["/chatkit endpoint<br/>FastAPI"]
        SERVER["StarterChatServer"]
    end
    
    USER -->|"User interaction"| PANEL
    CONFIG -->|"Imports config"| PANEL
    PANEL -->|"POST /chatkit"| VITE
    VITE -->|"Forwards to localhost:8000"| ENDPOINT
    ENDPOINT -->|"Process request"| SERVER
    SERVER -->|"Streaming response"| ENDPOINT
    ENDPOINT -->|"Response"| VITE
    VITE -->|"Response"| PANEL
    PANEL -->|"Display messages"| USER
```

**Description:** During development, the frontend on port 3000 makes requests to `/chatkit`. The Vite dev server proxies these requests to the FastAPI backend on port 8000. In production, the frontend connects directly to the deployed backend URL specified in `VITE_CHATKIT_API_URL`.

**Sources:** [chatkit/README.md:15-16](), [chatkit/README.md:30-32]()

## Modifying Configuration

### Changing UI Text

To modify the chat interface text, edit the static constants in [lib/config.ts:7-17]():

- **Greeting Message:** Modify `GREETING` string
- **Input Placeholder:** Modify `PLACEHOLDER_INPUT` string
- **Starter Prompts:** Add, remove, or modify objects in the `STARTER_PROMPTS` array

Example modification to add a new starter prompt:

```typescript
export const STARTER_PROMPTS: StartScreenPrompt[] = [
  {
    label: "What can you do?",
    prompt: "What can you do?",
    icon: "circle-question",
  },
  {
    label: "Tell me about OpenAI",
    prompt: "Tell me about OpenAI and its products",
    icon: "lightbulb",
  },
];
```

### Changing the Session Endpoint

To modify the session creation endpoint, update the `CREATE_SESSION_ENDPOINT` constant in [lib/config.ts:5](). Note that the corresponding API route handler must also be moved or updated in the `app/api/` directory structure.

### Changing the Workflow ID

The `WORKFLOW_ID` should not be directly modified in `lib/config.ts`. Instead, update the `NEXT_PUBLIC_CHATKIT_WORKFLOW_ID` environment variable in `.env.local`. See [Environment Variables](#8.1) for details.

## Type Definitions

The `StartScreenPrompt` type is imported from the `@openai/chatkit` package:

```typescript
import { StartScreenPrompt } from "@openai/chatkit";
```

**Source:** [lib/config.ts:1]()

This type defines the structure of prompt objects with the following properties:
- `label: string` - Display text
- `prompt: string` - Message sent when clicked
- `icon: string` - Icon identifier from ChatKit's icon set

## Configuration Access Pattern

The configuration follows a centralized import pattern where:

1. **Single Source:** All configuration constants are defined in one file (`lib/config.ts`)
2. **Named Exports:** Each constant is exported individually for selective imports
3. **Direct Imports:** Components import only the constants they need
4. **No Re-exports:** Configuration is not re-exported through intermediate modules

This pattern ensures:
- Easy tracking of configuration usage across the codebase
- Type safety for all configuration values
- Simple modification without side effects

**Sources:** [lib/config.ts:1-18](), [components/ChatKitPanel.tsx:6-11]()

---

# Page: Request Flow & Data Model

# Request Flow & Data Model

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [chatkit/backend/app/main.py](chatkit/backend/app/main.py)
- [chatkit/backend/app/memory_store.py](chatkit/backend/app/memory_store.py)
- [chatkit/backend/app/server.py](chatkit/backend/app/server.py)

</details>



## Purpose & Scope

This page documents the complete lifecycle of a chat request through the self-hosted ChatKit system, from initial HTTP request to streaming response. It covers the request processing pipeline, data retrieval and persistence mechanisms, and the core data structures used throughout the system.

For backend implementation details of individual components, see [Backend Implementation](#3.2). For frontend configuration and UI components, see [Frontend Implementation](#3.3).

---

## Request Lifecycle Overview

The following diagram traces a user message from the browser through the FastAPI backend, MemoryStore, AI agent, and back to the user as a streaming response.

```mermaid
sequenceDiagram
    participant Browser
    participant FastAPI as "FastAPI (/chatkit)"
    participant Server as "StarterChatServer"
    participant Store as "MemoryStore"
    participant Agent as "assistant_agent"
    participant OpenAI as "OpenAI API"
    
    Browser->>FastAPI: "POST /chatkit (payload)"
    FastAPI->>Server: "chatkit_server.process(payload, context)"
    
    Note over Server: "Parses payload, identifies thread_id"
    
    Server->>Store: "load_thread_items(thread_id, limit=30, order='desc')"
    Store-->>Server: "Page[ThreadItem] (last 30 messages)"
    
    Note over Server: "Reverses order, converts to agent_input"
    
    Server->>Server: "simple_to_agent_input(items)"
    Server->>Agent: "Runner.run_streamed(assistant_agent, agent_input)"
    
    Agent->>OpenAI: "Chat Completion API (gpt-4.1-mini)"
    
    loop "Streaming Response"
        OpenAI-->>Agent: "Partial response chunk"
        Agent-->>Server: "stream_agent_response() yields ThreadStreamEvent"
        Server-->>FastAPI: "ThreadStreamEvent"
        FastAPI-->>Browser: "Server-Sent Event"
    end
    
    Note over Store: "Store automatically updated by ChatKit"
```

**Sources:** [chatkit/backend/app/main.py:25-35](), [chatkit/backend/app/server.py:38-67](), [chatkit/backend/app/memory_store.py:40-51]()

---

## HTTP Request Entry Point

All chat interactions enter the system through a single FastAPI endpoint that proxies requests to the ChatKit server implementation.

### The `/chatkit` Endpoint

```mermaid
graph LR
    Request["HTTP POST /chatkit<br/>Raw payload bytes"]
    Process["chatkit_server.process()<br/>Parses payload, routes request"]
    Streaming{"Result type?"}
    SSE["StreamingResponse<br/>media_type='text/event-stream'"]
    JSON["Response or JSONResponse<br/>media_type='application/json'"]
    
    Request --> Process
    Process --> Streaming
    Streaming -->|"StreamingResult"| SSE
    Streaming -->|"Other"| JSON
```

The endpoint implementation at [chatkit/backend/app/main.py:25-35]() receives raw payload bytes from the ChatKit web component, passes them to the `StarterChatServer.process()` method, and returns either a streaming response (for chat messages) or JSON response (for other operations).

| Request Type | Response Type | Media Type |
|-------------|---------------|------------|
| User message | `StreamingResponse` | `text/event-stream` |
| Other operations | `Response` or `JSONResponse` | `application/json` |

**Sources:** [chatkit/backend/app/main.py:25-35]()

---

## Server Processing Pipeline

The `StarterChatServer` class extends `ChatKitServer` and implements the core chat processing logic through its `respond()` method.

### StarterChatServer.respond() Flow

```mermaid
graph TB
    Start["respond(thread, item, context)"]
    Load["load_thread_items()<br/>limit=MAX_RECENT_ITEMS (30)<br/>order='desc'"]
    Reverse["Reverse items to chronological order"]
    Convert["simple_to_agent_input(items)<br/>Convert ThreadItem to agent format"]
    Context["Create AgentContext<br/>thread, store, request_context"]
    Run["Runner.run_streamed()<br/>assistant_agent, agent_input, context"]
    Stream["stream_agent_response()<br/>Yields ThreadStreamEvent"]
    
    Start --> Load
    Load --> Reverse
    Reverse --> Convert
    Convert --> Context
    Context --> Run
    Run --> Stream
```

The `respond()` method at [chatkit/backend/app/server.py:38-67]() orchestrates the following steps:

1. **Load Recent History**: Retrieves up to 30 recent items from the store in descending order
2. **Reverse Order**: Reverses items to chronological order (oldest first)
3. **Convert Format**: Transforms `ThreadItem` objects to agent-compatible input format
4. **Create Context**: Packages `thread`, `store`, and `request_context` into `AgentContext`
5. **Execute Agent**: Runs the assistant agent in streaming mode
6. **Stream Events**: Yields `ThreadStreamEvent` objects as they arrive

**Sources:** [chatkit/backend/app/server.py:38-67]()

---

## Data Retrieval from MemoryStore

The `MemoryStore` class implements the `Store` interface and manages thread metadata and conversation items in memory.

### MemoryStore Data Structures

```mermaid
graph TB
    MemoryStore["MemoryStore"]
    Threads["threads: dict[str, ThreadMetadata]<br/>Key: thread_id"]
    Items["items: dict[str, list[ThreadItem]]<br/>Key: thread_id, Value: list of items"]
    
    MemoryStore --> Threads
    MemoryStore --> Items
    
    Threads --> TM1["ThreadMetadata<br/>id, created_at, etc."]
    Threads --> TM2["ThreadMetadata"]
    Items --> I1["list[ThreadItem]"]
    Items --> I2["list[ThreadItem]"]
    
    I1 --> TI1["ThreadItem (created_at, id, etc.)"]
    I1 --> TI2["ThreadItem"]
```

The store maintains two primary data structures at [chatkit/backend/app/memory_store.py:14-17]():

| Field | Type | Purpose |
|-------|------|---------|
| `threads` | `dict[str, ThreadMetadata]` | Maps thread IDs to thread metadata |
| `items` | `dict[str, list[ThreadItem]]` | Maps thread IDs to lists of conversation items |

### load_thread_items() Method

The `load_thread_items()` method at [chatkit/backend/app/memory_store.py:40-51]() implements pagination logic:

1. Retrieves the item list for the specified `thread_id`
2. Calls `_paginate()` helper with sorting and cursor parameters
3. Returns a `Page[ThreadItem]` object containing:
   - `data`: List of items for the current page
   - `has_more`: Boolean indicating if more items exist
   - `after`: Cursor for fetching the next page

The `_paginate()` helper at [chatkit/backend/app/memory_store.py:85-104]() sorts items by `created_at`, applies cursor-based pagination, and calculates the `has_more` flag.

**Sources:** [chatkit/backend/app/memory_store.py:40-51](), [chatkit/backend/app/memory_store.py:85-104]()

---

## Core Data Model

The system uses several key data types from the `chatkit.types` module to represent conversations and events.

### ThreadMetadata

Represents metadata about a conversation thread. Key fields include:

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Unique thread identifier |
| `created_at` | `datetime` | Thread creation timestamp |

**Usage:** Passed to `StarterChatServer.respond()` at [chatkit/backend/app/server.py:40-42]()

### ThreadItem

Represents a single item (message, response) in a conversation thread. Key fields include:

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Unique item identifier |
| `created_at` | `datetime` | Item creation timestamp |
| `type` | `str` | Item type (e.g., user message, agent response) |

**Usage:** Stored in `MemoryStore.items` at [chatkit/backend/app/memory_store.py:17](), paginated by `load_thread_items()`

### UserMessageItem

Subtype of `ThreadItem` representing user-submitted messages. Passed to `respond()` at [chatkit/backend/app/server.py:41]() when a new user message arrives.

### ThreadStreamEvent

Represents streaming events sent back to the client during agent response generation. These events are yielded by `stream_agent_response()` at [chatkit/backend/app/server.py:66]() and converted to Server-Sent Events by FastAPI.

### Page[T]

Generic pagination container returned by store methods. Structure:

| Field | Type | Description |
|-------|------|-------------|
| `data` | `list[T]` | Items in the current page |
| `has_more` | `bool` | Whether more items exist |
| `after` | `str \| None` | Cursor for next page |

**Sources:** [chatkit/backend/app/server.py:10](), [chatkit/backend/app/memory_store.py:11]()

---

## Agent Execution and Context

The system configures a single assistant agent that processes all user messages.

### assistant_agent Configuration

```mermaid
graph LR
    Agent["assistant_agent<br/>Agent[AgentContext]"]
    Model["model: 'gpt-4.1-mini'"]
    Name["name: 'Starter Assistant'"]
    Instructions["instructions:<br/>Concise, helpful assistant"]
    
    Agent --> Model
    Agent --> Name
    Agent --> Instructions
```

The agent is defined at [chatkit/backend/app/server.py:20-28]() with:

- **Model**: `gpt-4.1-mini` (specified in `MODEL` constant at [chatkit/backend/app/server.py:17]())
- **Name**: "Starter Assistant"
- **Instructions**: Directs the agent to provide concise, focused responses

### AgentContext

The `AgentContext` object at [chatkit/backend/app/server.py:54-58]() packages contextual information for the agent:

| Field | Type | Purpose |
|-------|------|---------|
| `thread` | `ThreadMetadata` | Current thread metadata |
| `store` | `MemoryStore` | Store instance for persistence |
| `request_context` | `dict[str, Any]` | HTTP request context from FastAPI |

**Sources:** [chatkit/backend/app/server.py:20-28](), [chatkit/backend/app/server.py:54-58]()

---

## Response Streaming Pipeline

The agent response flows back to the client as a stream of events, enabling real-time UI updates.

### Streaming Event Flow

```mermaid
graph LR
    RunnerStream["Runner.run_streamed()"]
    AgentResponse["stream_agent_response()<br/>Converts to ThreadStreamEvent"]
    ServerYield["StarterChatServer.respond()<br/>yields event"]
    ProcessStream["chatkit_server.process()<br/>returns StreamingResult"]
    FastAPI["FastAPI StreamingResponse<br/>text/event-stream"]
    Browser["Browser receives SSE"]
    
    RunnerStream --> AgentResponse
    AgentResponse --> ServerYield
    ServerYield --> ProcessStream
    ProcessStream --> FastAPI
    FastAPI --> Browser
```

The streaming pipeline at [chatkit/backend/app/server.py:60-67]():

1. `Runner.run_streamed()` executes the agent and yields incremental results
2. `stream_agent_response()` converts agent results to `ThreadStreamEvent` objects
3. `StarterChatServer.respond()` yields events to the caller
4. `ChatKitServer.process()` wraps the event stream in a `StreamingResult`
5. FastAPI's `StreamingResponse` at [chatkit/backend/app/main.py:32]() sends events as Server-Sent Events

### Server-Sent Event Format

The `StreamingResponse` uses `media_type="text/event-stream"` to deliver events in SSE format. Each `ThreadStreamEvent` is serialized and sent to the browser, where the ChatKit web component processes it to update the UI in real-time.

**Sources:** [chatkit/backend/app/server.py:60-67](), [chatkit/backend/app/main.py:31-32]()

---

## Store Persistence Operations

While the agent streams responses, the ChatKit framework automatically handles persistence to the store.

### Automatic Item Persistence

The `MemoryStore` provides two methods for persisting items:

| Method | Purpose | Implementation |
|--------|---------|----------------|
| `add_thread_item()` | Append new item to thread | [chatkit/backend/app/memory_store.py:53-56]() |
| `save_item()` | Update existing or append new | [chatkit/backend/app/memory_store.py:58-64]() |

The `save_item()` method:
1. Searches for an existing item with matching `id`
2. Updates the item in-place if found
3. Appends as new item if not found

This idempotent behavior ensures the store accurately reflects the current conversation state, even if the same item is saved multiple times during streaming.

### Thread Management

The store also manages thread metadata:

| Method | Purpose | Implementation |
|--------|---------|----------------|
| `load_thread()` | Retrieve thread metadata | [chatkit/backend/app/memory_store.py:19-22]() |
| `save_thread()` | Persist thread metadata | [chatkit/backend/app/memory_store.py:24-25]() |
| `delete_thread()` | Remove thread and all items | [chatkit/backend/app/memory_store.py:74-76]() |

**Sources:** [chatkit/backend/app/memory_store.py:19-25](), [chatkit/backend/app/memory_store.py:53-64](), [chatkit/backend/app/memory_store.py:74-76]()

---

## Complete Request Flow Summary

The table below summarizes the complete request flow with corresponding code locations:

| Step | Component | Method/Function | File Location |
|------|-----------|----------------|---------------|
| 1. Receive HTTP request | FastAPI | `chatkit_endpoint()` | [chatkit/backend/app/main.py:25-35]() |
| 2. Process payload | `StarterChatServer` | `process()` (inherited) | Called at [chatkit/backend/app/main.py:29]() |
| 3. Route to respond | `StarterChatServer` | `respond()` | [chatkit/backend/app/server.py:38-67]() |
| 4. Load conversation history | `MemoryStore` | `load_thread_items()` | [chatkit/backend/app/memory_store.py:40-51]() |
| 5. Reverse item order | `StarterChatServer` | `respond()` line 51 | [chatkit/backend/app/server.py:51]() |
| 6. Convert to agent input | `simple_to_agent_input()` | Imported function | [chatkit/backend/app/server.py:52]() |
| 7. Create agent context | `AgentContext` | Constructor | [chatkit/backend/app/server.py:54-58]() |
| 8. Execute agent | `Runner` | `run_streamed()` | [chatkit/backend/app/server.py:60-64]() |
| 9. Stream events | `stream_agent_response()` | Imported function | [chatkit/backend/app/server.py:66]() |
| 10. Return streaming response | FastAPI | `StreamingResponse()` | [chatkit/backend/app/main.py:32]() |

The maximum conversation context retrieved per request is controlled by `MAX_RECENT_ITEMS = 30` at [chatkit/backend/app/server.py:16](), ensuring the agent receives the last 30 messages for context while avoiding excessive token usage.

**Sources:** [chatkit/backend/app/main.py:25-35](), [chatkit/backend/app/server.py:16](), [chatkit/backend/app/server.py:38-67](), [chatkit/backend/app/memory_store.py:40-51]()

---

# Page: Customization Guide

# Customization Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [chatkit/.env.example](chatkit/.env.example)
- [chatkit/.gitignore](chatkit/.gitignore)
- [chatkit/README.md](chatkit/README.md)
- [chatkit/backend/.gitignore](chatkit/backend/.gitignore)
- [chatkit/backend/app/__init__.py](chatkit/backend/app/__init__.py)
- [chatkit/backend/app/memory_store.py](chatkit/backend/app/memory_store.py)
- [chatkit/backend/app/server.py](chatkit/backend/app/server.py)

</details>



This guide documents the primary customization points in the self-hosted ChatKit starter application (`chatkit/` directory). It focuses on production-readiness modifications, particularly replacing the in-memory storage implementation with a persistent database, configuring the UI, and customizing the AI agent behavior.

For information about the managed ChatKit integration pattern, see [Managed ChatKit](#4). For deployment-specific environment configuration, see [Production Environment Variables](#8.1).

## Overview of Customization Areas

The ChatKit starter application provides three primary customization categories, each targeting different system layers:

| Customization Area | Files Affected | Production Priority | Complexity |
|-------------------|---------------|---------------------|------------|
| **Storage Layer** | `backend/app/server.py`, `backend/app/memory_store.py` | **Critical** | Medium-High |
| **UI Configuration** | `frontend/src/lib/config.ts`, `frontend/src/components/ChatKitPanel.tsx` | Medium | Low |
| **Agent Behavior** | `backend/app/server.py` (lines 20-28) | Medium | Low-Medium |
| **Environment Variables** | `.env.local` | **Critical** | Low |

**Sources:** [chatkit/README.md:28-32]()

### Customization Points Diagram

```mermaid
graph TB
    subgraph Backend["Backend Customization"]
        MemoryStore["MemoryStore<br/>(memory_store.py:14-116)"]
        StarterChatServer["StarterChatServer<br/>(server.py:31-68)"]
        assistant_agent["assistant_agent<br/>(server.py:20-28)"]
    end
    
    subgraph Frontend["Frontend Customization"]
        config_ts["config.ts<br/>Connection Settings"]
        ChatKitPanel["ChatKitPanel.tsx<br/>Layout Structure"]
    end
    
    subgraph Environment["Environment Configuration"]
        OPENAI_API_KEY["OPENAI_API_KEY"]
        VITE_CHATKIT_API_URL["VITE_CHATKIT_API_URL"]
        VITE_CHATKIT_API_DOMAIN_KEY["VITE_CHATKIT_API_DOMAIN_KEY"]
    end
    
    Production[Production Deployment]
    
    MemoryStore -->|"MUST REPLACE"| Production
    StarterChatServer -->|"Uses Store"| MemoryStore
    assistant_agent -->|"Optional Tuning"| Production
    config_ts -->|"Configure Endpoints"| Production
    ChatKitPanel -->|"Optional Branding"| Production
    
    OPENAI_API_KEY -->|"Required"| Production
    VITE_CHATKIT_API_URL -->|"Set for Production"| Production
    VITE_CHATKIT_API_DOMAIN_KEY -->|"Required for Prod"| Production
```

**Sources:** [chatkit/README.md:28-32](), [chatkit/backend/app/server.py:1-68](), [chatkit/backend/app/memory_store.py:1-116]()

---

## Storage Layer Customization

### Why Replace MemoryStore

The `MemoryStore` implementation [chatkit/backend/app/memory_store.py:14-116]() is designed exclusively for development and demonstration. It stores all conversation data in Python dictionaries that exist only in process memory, resulting in:

- **Data loss on restart**: All threads and messages are lost when the backend process terminates
- **No horizontal scaling**: Each backend instance maintains separate state
- **Memory constraints**: All conversation history resides in RAM
- **No persistence**: Data cannot be queried, backed up, or migrated

**Production deployments require a persistent database implementation.**

**Sources:** [chatkit/backend/app/memory_store.py:1-4](), [chatkit/README.md:32]()

### Store Interface Requirements

The `MemoryStore` class implements the `Store[dict]` interface from the `chatkit.store` module. A production replacement must implement all abstract methods defined in this interface.

#### Required Method Implementations

```mermaid
classDiagram
    class Store {
        <<interface>>
        +load_thread(thread_id, context) ThreadMetadata
        +save_thread(thread, context) None
        +load_threads(limit, after, order, context) Page~ThreadMetadata~
        +load_thread_items(thread_id, after, limit, order, context) Page~ThreadItem~
        +add_thread_item(thread_id, item, context) None
        +save_item(thread_id, item, context) None
        +load_item(thread_id, item_id, context) ThreadItem
        +delete_thread(thread_id, context) None
        +delete_thread_item(thread_id, item_id, context) None
        +save_attachment(attachment, context) None
        +load_attachment(attachment_id, context) Attachment
        +delete_attachment(attachment_id, context) None
    }
    
    class MemoryStore {
        +threads: dict[str, ThreadMetadata]
        +items: dict[str, list[ThreadItem]]
        +_paginate(rows, after, limit, order, sort_key, cursor_key) Page
    }
    
    class ProductionStore {
        +db: DatabaseConnection
        +_execute_query(sql, params) Result
        +_paginate_sql(query, after, limit, order) Page
    }
    
    Store <|-- MemoryStore
    Store <|-- ProductionStore
```

**Sources:** [chatkit/backend/app/memory_store.py:14-116]()

#### Method Responsibilities

| Method | Purpose | Implementation Notes |
|--------|---------|---------------------|
| `load_thread` | Retrieve thread metadata by ID | Must raise `NotFoundError` if thread does not exist [chatkit/backend/app/memory_store.py:19-22]() |
| `save_thread` | Persist thread metadata | Upsert operation; overwrite existing thread [chatkit/backend/app/memory_store.py:24-25]() |
| `load_threads` | List threads with pagination | Support `after` cursor and `order` direction [chatkit/backend/app/memory_store.py:27-38]() |
| `load_thread_items` | Retrieve messages in a thread | Paginated; ordered by `created_at` [chatkit/backend/app/memory_store.py:40-51]() |
| `add_thread_item` | Append new message to thread | Insert-only operation [chatkit/backend/app/memory_store.py:53-56]() |
| `save_item` | Update existing message or insert | Upsert by `item.id` [chatkit/backend/app/memory_store.py:58-64]() |
| `delete_thread` | Remove thread and all items | Cascade delete [chatkit/backend/app/memory_store.py:74-76]() |

**Sources:** [chatkit/backend/app/memory_store.py:14-116]()

### Implementation Patterns

#### Pattern 1: Relational Database (PostgreSQL, MySQL)

For relational databases, implement two primary tables with a foreign key relationship:

**Schema Example:**

```sql
CREATE TABLE threads (
    id TEXT PRIMARY KEY,
    title TEXT,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    metadata JSONB
);

CREATE TABLE thread_items (
    id TEXT PRIMARY KEY,
    thread_id TEXT NOT NULL REFERENCES threads(id) ON DELETE CASCADE,
    item_type TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    content JSONB NOT NULL,
    INDEX idx_thread_created (thread_id, created_at)
);
```

**Implementation skeleton:**

```python
from chatkit.store import Store
from chatkit.types import ThreadMetadata, ThreadItem, Page
import asyncpg

class PostgresStore(Store[dict]):
    def __init__(self, connection_pool: asyncpg.Pool):
        self.pool = connection_pool
    
    async def load_thread(self, thread_id: str, context: dict) -> ThreadMetadata:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM threads WHERE id = $1", thread_id
            )
            if not row:
                raise NotFoundError(f"Thread {thread_id} not found")
            return self._row_to_thread_metadata(row)
    
    async def load_thread_items(
        self, thread_id: str, after: str | None, limit: int, 
        order: str, context: dict
    ) -> Page[ThreadItem]:
        # Implement SQL pagination with LIMIT and WHERE created_at > after
        ...
```

**Sources:** [chatkit/backend/app/memory_store.py:14-116]()

#### Pattern 2: Document Database (MongoDB, DynamoDB)

For document databases, store threads and items as nested or separate collections:

**Collection structure:**

```python
# threads collection
{
    "_id": "thread_abc123",
    "title": "User Conversation",
    "created_at": ISODate("2024-01-01T00:00:00Z"),
    "updated_at": ISODate("2024-01-01T00:05:00Z")
}

# thread_items collection
{
    "_id": "item_xyz789",
    "thread_id": "thread_abc123",
    "item_type": "user_message",
    "created_at": ISODate("2024-01-01T00:01:00Z"),
    "content": {...}
}
```

**Sources:** [chatkit/backend/app/memory_store.py:14-116]()

### Pagination Implementation

The `_paginate` helper method [chatkit/backend/app/memory_store.py:85-104]() demonstrates cursor-based pagination logic. Production implementations must replicate this behavior:

```mermaid
flowchart TD
    Start["load_thread_items(thread_id, after, limit, order)"]
    Query["Query database ordered by created_at"]
    HasAfter{"after cursor<br/>provided?"}
    FilterAfter["Add WHERE clause:<br/>created_at > after_timestamp"]
    ApplyLimit["Apply LIMIT limit+1"]
    Execute["Execute query"]
    CheckMore{"Result count<br/>> limit?"}
    SetHasMore["has_more = True<br/>Remove last item"]
    NoMore["has_more = False"]
    GetNextCursor["next_after = last_item.id"]
    Return["Return Page(data, has_more, after)"]
    
    Start --> Query
    Query --> HasAfter
    HasAfter -->|Yes| FilterAfter
    HasAfter -->|No| ApplyLimit
    FilterAfter --> ApplyLimit
    ApplyLimit --> Execute
    Execute --> CheckMore
    CheckMore -->|Yes| SetHasMore
    CheckMore -->|No| NoMore
    SetHasMore --> GetNextCursor
    NoMore --> Return
    GetNextCursor --> Return
```

**Key pagination requirements:**

1. **Cursor stability**: The `after` parameter is a cursor (typically an ID or timestamp) identifying where to continue pagination
2. **Ordering**: Must respect `order` parameter (`"asc"` or `"desc"`) [chatkit/backend/app/memory_store.py:94]()
3. **Limit enforcement**: Return at most `limit` items [chatkit/backend/app/memory_store.py:101]()
4. **has_more indicator**: Set to `True` if additional results exist beyond the current page [chatkit/backend/app/memory_store.py:102]()
5. **next_after cursor**: Provide cursor for the next page if `has_more` is `True` [chatkit/backend/app/memory_store.py:103]()

**Sources:** [chatkit/backend/app/memory_store.py:85-104]()

### Integrating Custom Store

After implementing your custom store, replace the `MemoryStore` instantiation in `StarterChatServer.__init__`:

**Current implementation:**

[chatkit/backend/app/server.py:34-36]()

```python
def __init__(self) -> None:
    self.store: MemoryStore = MemoryStore()
    super().__init__(self.store)
```

**Modified for PostgreSQL:**

```python
def __init__(self, db_pool: asyncpg.Pool) -> None:
    self.store: PostgresStore = PostgresStore(db_pool)
    super().__init__(self.store)
```

**Update the FastAPI application initialization** in `backend/app/main.py` to create the database connection pool and pass it to `StarterChatServer`.

**Sources:** [chatkit/backend/app/server.py:31-36]()

---

## UI Configuration

### Connection Settings (config.ts)

The frontend configuration file `frontend/src/lib/config.ts` defines the ChatKit API endpoint and domain key. While the file is not included in the provided sources, it is referenced as a customization point [chatkit/README.md:30]().

**Typical configuration structure:**

| Configuration Variable | Purpose | Default | Production Value |
|----------------------|---------|---------|------------------|
| `VITE_CHATKIT_API_URL` | Backend API endpoint | `/chatkit` (proxied) | `https://api.yourdomain.com/chatkit` |
| `VITE_CHATKIT_API_DOMAIN_KEY` | Domain authentication key | `domain_pk_localhost_dev` | Registered production key |

**Environment variable mapping:**

These values are injected at build time from environment variables:

- `VITE_CHATKIT_API_URL` [chatkit/.env.example:2]()
- `VITE_CHATKIT_API_DOMAIN_KEY` [chatkit/.env.example:3]()

**For production deployment:**
1. Register a domain key in the OpenAI dashboard
2. Set `VITE_CHATKIT_API_DOMAIN_KEY` to the registered key
3. Update `VITE_CHATKIT_API_URL` to point to your production backend

**Sources:** [chatkit/README.md:19-26](), [chatkit/.env.example:1-3]()

### Layout Customization (ChatKitPanel.tsx)

The `frontend/src/components/ChatKitPanel.tsx` component defines the layout structure of the chat interface [chatkit/README.md:31](). Common customizations include:

- **Branding**: Add logos, custom headers, or footers
- **Styling**: Modify CSS classes or theme variables
- **Layout adjustments**: Change panel positioning, sizing, or responsive behavior
- **Feature toggles**: Enable/disable UI features like attachments or message editing

**Sources:** [chatkit/README.md:31]()

---

## Agent Customization

### Modifying Assistant Behavior

The `assistant_agent` configuration [chatkit/backend/app/server.py:20-28]() defines the AI agent's model, name, and instructions.

**Current configuration:**

```python
assistant_agent = Agent[AgentContext[dict[str, Any]]](
    model=MODEL,  # "gpt-4.1-mini"
    name="Starter Assistant",
    instructions=(
        "You are a concise, helpful assistant. "
        "Keep replies short and focus on directly answering "
        "the user's request."
    ),
)
```

**Sources:** [chatkit/backend/app/server.py:20-28]()

### Customization Options

| Parameter | Current Value | Customization Purpose |
|-----------|--------------|----------------------|
| `model` | `"gpt-4.1-mini"` [chatkit/backend/app/server.py:17]() | Change to `"gpt-4-turbo"`, `"gpt-4o"`, or other OpenAI models |
| `name` | `"Starter Assistant"` | Update for branding or role identification |
| `instructions` | Concise assistant prompt | Customize agent personality, domain expertise, or behavior constraints |

**Example: Domain-specific customization**

```python
assistant_agent = Agent[AgentContext[dict[str, Any]]](
    model="gpt-4-turbo",
    name="Technical Support Assistant",
    instructions=(
        "You are a technical support specialist for XYZ product. "
        "Always ask for the user's account ID before troubleshooting. "
        "Provide step-by-step solutions with code examples when relevant. "
        "Escalate to human support if the issue involves account access."
    ),
)
```

### Context Handling

The `StarterChatServer.respond` method loads recent conversation history for context [chatkit/backend/app/server.py:44-51]():

```python
items_page = await self.store.load_thread_items(
    thread.id,
    after=None,
    limit=MAX_RECENT_ITEMS,  # 30
    order="desc",
    context=context,
)
```

**Customization:** Adjust `MAX_RECENT_ITEMS` [chatkit/backend/app/server.py:16]() based on:
- **Token budget**: More items = more tokens consumed
- **Context relevance**: Longer history may include outdated information
- **Model limits**: Ensure total context fits within model's context window

**Sources:** [chatkit/backend/app/server.py:16-68]()

---

## Environment Variables Reference

### Backend Variables

| Variable | Required | Purpose | Example |
|----------|----------|---------|---------|
| `OPENAI_API_KEY` | **Yes** | OpenAI API authentication | `sk-proj-...` [chatkit/.env.example:1]() |

**Set in:** Shell environment or `.env.local` at repository root [chatkit/README.md:24-25]()

### Frontend Variables

| Variable | Required | Purpose | Default | Production Example |
|----------|----------|---------|---------|-------------------|
| `VITE_CHATKIT_API_URL` | No | Backend API endpoint | `/chatkit` | `https://api.example.com/chatkit` |
| `VITE_CHATKIT_API_DOMAIN_KEY` | No* | Domain authentication | `domain_pk_localhost_dev` | `domain_pk_prod_abc123` |

**Note:** `VITE_CHATKIT_API_DOMAIN_KEY` is optional for local development but **required for production** [chatkit/README.md:26]().

**Sources:** [chatkit/README.md:19-26](), [chatkit/.env.example:1-3]()

---

## Customization Implementation Checklist

Use this checklist when preparing the starter application for production:

### Storage Layer
- [ ] Implement custom `Store` class with database backend
- [ ] Test all required Store interface methods
- [ ] Verify pagination logic with `after` cursors
- [ ] Implement proper error handling (raise `NotFoundError` when appropriate)
- [ ] Update `StarterChatServer.__init__` to use custom store
- [ ] Configure database connection pooling

### UI Configuration
- [ ] Update `config.ts` with production API URL
- [ ] Customize `ChatKitPanel.tsx` layout/branding (optional)
- [ ] Test frontend build with production environment variables

### Agent Configuration
- [ ] Review and customize `assistant_agent.instructions`
- [ ] Select appropriate model for use case
- [ ] Adjust `MAX_RECENT_ITEMS` based on context requirements

### Environment Variables
- [ ] Set `OPENAI_API_KEY` in production environment
- [ ] Register production domain key in OpenAI dashboard
- [ ] Set `VITE_CHATKIT_API_DOMAIN_KEY` to production key
- [ ] Configure `VITE_CHATKIT_API_URL` for production backend

### Testing
- [ ] Verify conversation persistence across backend restarts
- [ ] Test pagination with large thread histories
- [ ] Load test backend with expected concurrent users
- [ ] Verify frontend can connect to production backend

**Sources:** [chatkit/README.md:1-32](), [chatkit/backend/app/server.py:1-68](), [chatkit/backend/app/memory_store.py:1-116]()

---

# Page: Managed ChatKit (managed-chatkit/)

# Managed ChatKit (managed-chatkit/)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

This document describes the **Managed ChatKit** starter application, which demonstrates integration with ChatKit using hosted workflows. This is one of two reference implementations in the repository, offering an alternative to the self-hosted approach.

For detailed information about the self-hosted ChatKit implementation, see [Self-Hosted ChatKit](#3). For general repository structure and setup instructions, see [Overview](#1) and [Getting Started](#2).

**Sources:** [README.md:1-9]()

---

## 4.1 Overview & Hosted Workflows

### What is Managed ChatKit?

The `managed-chatkit/` directory contains a starter application that integrates with ChatKit using **hosted workflows**. Unlike the self-hosted variant, this approach offloads workflow execution and management to hosted infrastructure, reducing operational complexity for developers.

```mermaid
graph TB
    subgraph "Repository Structure"
        REPO["openai-chatkit-starter-app"]
        
        subgraph SelfHosted["chatkit/ - Self-Hosted"]
            SH_BE["Backend: Full Control<br/>Manages All Logic"]
            SH_FE["Frontend: React UI"]
        end
        
        subgraph Managed["managed-chatkit/ - Managed"]
            M_BE["Backend: Delegates to<br/>Hosted Workflows"]
            M_FE["Frontend: React UI"]
        end
    end
    
    subgraph External["External Services"]
        OPENAI["OpenAI API"]
        HOSTED["Hosted Workflow<br/>Infrastructure"]
    end
    
    REPO --> SelfHosted
    REPO --> Managed
    
    SH_BE -->|"Direct API Calls"| OPENAI
    M_BE -->|"Delegates Execution"| HOSTED
    HOSTED -->|"Manages Lifecycle"| OPENAI
    
    style SelfHosted fill:#e8f5e8
    style Managed fill:#f5e8f5
    style External fill:#e1f5ff
```

**Diagram: Integration Pattern Comparison**

**Sources:** [README.md:7-8]()

### Hosted Workflows Explained

Hosted workflows refer to a deployment model where ChatKit conversation management, state handling, and AI orchestration are handled by managed infrastructure rather than developer-maintained servers. This architectural pattern provides:

| Aspect | Self-Hosted (chatkit/) | Managed (managed-chatkit/) |
|--------|------------------------|---------------------------|
| **Infrastructure Management** | Developer responsibility | Handled by platform |
| **Conversation State** | Custom implementation (e.g., MemoryStore) | Managed persistence |
| **Workflow Execution** | Local agent orchestration | Remote hosted execution |
| **Operational Complexity** | Full control, full responsibility | Reduced operational burden |
| **Customization Flexibility** | Complete code-level control | Configuration-based customization |

**Sources:** [README.md:8]()

### Technology Stack Similarity

Despite architectural differences in workflow execution, the `managed-chatkit/` example maintains the same technology foundation as the self-hosted variant:

```mermaid
graph LR
    subgraph Backend["Backend Layer"]
        PYTHON["Python 3.11+"]
        FASTAPI["FastAPI Framework"]
        SDK["openai-chatkit SDK"]
    end
    
    subgraph Frontend["Frontend Layer"]
        NODE["Node.js 22"]
        VITE["Vite Build Tool"]
        REACT["React Framework"]
        TS["TypeScript"]
    end
    
    subgraph Integration["Integration Model"]
        HOSTED["Hosted Workflows"]
    end
    
    Backend --> Integration
    Frontend -->|"HTTP/WebSocket"| Backend
    Integration -->|"Managed Execution"| OpenAI["OpenAI API"]
```

**Diagram: Managed ChatKit Technology Stack**

**Sources:** [README.md:7-8]()

### When to Choose Managed ChatKit

The managed integration pattern is appropriate when:

- **Reduced Operations**: Team prefers to minimize infrastructure management overhead
- **Rapid Prototyping**: Quick deployment without server maintenance concerns
- **Scalability**: Automatic scaling handled by hosted infrastructure
- **Standard Workflows**: Application requirements align with platform-provided workflow patterns

Conversely, choose self-hosted ChatKit (see [Self-Hosted ChatKit](#3)) when requiring:
- Complete control over conversation logic and state management
- Custom storage backends (databases, caching layers)
- Integration with existing infrastructure
- Specific security or compliance requirements

**Sources:** [README.md:7-8]()

---

## 4.2 Architecture Differences

### Structural Organization

The `managed-chatkit/` directory follows the same structural pattern as `chatkit/`, maintaining consistency across examples:

```
managed-chatkit/
├── backend/          # FastAPI application
│   ├── app/
│   ├── pyproject.toml
│   └── requirements.txt
└── frontend/         # Vite + React UI
    ├── src/
    ├── package.json
    └── vite.config.ts
```

This parallel structure allows developers to compare implementations directly and understand the specific modifications required for hosted workflow integration.

**Sources:** [README.md:8]()

### Request Flow Comparison

The fundamental difference between self-hosted and managed approaches lies in **where workflow execution occurs**:

```mermaid
sequenceDiagram
    participant User
    participant Frontend as "React Frontend"
    participant Backend as "FastAPI Backend"
    participant Workflow as "Workflow Execution"
    participant OpenAI as "OpenAI API"
    
    Note over User,OpenAI: Self-Hosted Flow (chatkit/)
    User->>Frontend: Send message
    Frontend->>Backend: POST /chatkit
    Backend->>Backend: Local StarterChatServer
    Backend->>Backend: MemoryStore
    Backend->>Backend: Local agent execution
    Backend->>OpenAI: Direct API call
    OpenAI-->>Backend: Streaming response
    Backend-->>Frontend: Stream events
    Frontend-->>User: Display response
    
    Note over User,OpenAI: Managed Flow (managed-chatkit/)
    User->>Frontend: Send message
    Frontend->>Backend: POST /chatkit
    Backend->>Workflow: Delegate to hosted workflow
    Workflow->>Workflow: Managed state & orchestration
    Workflow->>OpenAI: Platform-managed API call
    OpenAI-->>Workflow: Streaming response
    Workflow-->>Backend: Stream events
    Backend-->>Frontend: Stream events
    Frontend-->>User: Display response
```

**Diagram: Request Flow Comparison Between Integration Patterns**

**Sources:** [README.md:7-8]()

### Component Responsibilities

The managed approach shifts several responsibilities from application code to platform infrastructure:

| Component | Self-Hosted Implementation | Managed Implementation |
|-----------|---------------------------|------------------------|
| **Conversation State** | `MemoryStore` class in [chatkit/backend/app/server.py]() | Hosted platform persistence |
| **Agent Orchestration** | `StarterChatServer.respond()` method | Hosted workflow engine |
| **API Key Management** | Application environment variables | Platform credential management |
| **Streaming Logic** | `run_streamed()` in application code | Platform streaming infrastructure |
| **Error Handling** | Custom retry/fallback logic | Platform-managed resilience |

**Sources:** [README.md:7-8]()

### Configuration Differences

While both implementations require similar environment variables for frontend configuration (see [Environment Configuration](#2.2)), the backend configuration differs:

**Common Frontend Variables:**
```
VITE_CHATKIT_API_URL=/chatkit
VITE_CHATKIT_API_DOMAIN_KEY=domain_pk_*
```

**Backend Configuration Differences:**

| Variable | Self-Hosted | Managed |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Required for direct API access | May be platform-managed |
| Workflow Identifiers | N/A | Required to specify hosted workflow |
| Platform Credentials | N/A | Required for platform authentication |

**Sources:** [README.md:7-8]()

### Development and Deployment

Both implementations share the same development workflow (see [Local Development Setup](#7.1)):

```bash
npm run dev  # Starts both backend and frontend
```

However, deployment considerations differ:

```mermaid
graph TB
    subgraph Development["Development (Both Patterns)"]
        LOCAL["npm run dev<br/>Local backend + frontend"]
    end
    
    subgraph SelfHostedDeploy["Self-Hosted Deployment"]
        SH_INFRA["Provision infrastructure<br/>Database, servers, monitoring"]
        SH_DB["Migrate from MemoryStore<br/>to persistent storage"]
        SH_SCALE["Configure scaling,<br/>load balancing"]
    end
    
    subgraph ManagedDeploy["Managed Deployment"]
        M_CONFIG["Configure workflow<br/>references"]
        M_PLATFORM["Deploy to platform<br/>infrastructure"]
        M_AUTO["Automatic scaling<br/>and management"]
    end
    
    Development --> SelfHostedDeploy
    Development --> ManagedDeploy
    
    SH_INFRA --> SH_DB --> SH_SCALE
    M_CONFIG --> M_PLATFORM --> M_AUTO
```

**Diagram: Deployment Path Comparison**

**Sources:** [README.md:7-8]()

### Code Reuse and Portability

The parallel structure between `chatkit/` and `managed-chatkit/` facilitates:

1. **Pattern Migration**: Developers can start with managed workflows and migrate to self-hosted as requirements evolve
2. **Frontend Compatibility**: UI components remain largely identical, requiring only configuration changes
3. **Learning Path**: Understanding one implementation provides foundation for the other

**Sources:** [README.md:1-9]()

---

## Integration with CI/CD

Both starter applications are validated through the same CI/CD pipeline (see [CI/CD Pipeline](#6)), ensuring code quality consistency:

- Python backend validation: syntax, linting (ruff), formatting, type checking (mypy)
- Frontend validation: dependency installation, ESLint, build verification

This unified quality assurance approach ensures both examples maintain equivalent code standards regardless of their deployment model.

**Sources:** [README.md:1-9]()

---

## Next Steps

To get started with Managed ChatKit:

1. Review [Installation & Prerequisites](#2.1) for required software versions
2. Configure environment variables as described in [Environment Configuration](#2.2)
3. Follow [Running the Application](#2.3) to start the development servers
4. For production deployment considerations, see [Deployment Considerations](#8)

To compare with the self-hosted approach in detail, see [Self-Hosted ChatKit](#3) for complete implementation documentation including `StarterChatServer`, `MemoryStore`, and agent configuration.

**Sources:** [README.md:1-9]()

---

# Page: Overview & Hosted Workflows

# Overview & Hosted Workflows

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

This page introduces the managed ChatKit integration pattern and explains the concept of hosted workflows. It describes the `managed-chatkit/` directory contents and clarifies the operational differences between managed and self-hosted integrations. For detailed architectural differences, see [Architecture Differences](#4.2). For the self-hosted integration pattern, see [Self-Hosted ChatKit](#3).

**Sources:** [README.md:1-9]()

## What are Hosted Workflows?

Hosted workflows are OpenAI-managed infrastructure components that handle agent orchestration, conversation persistence, and request processing on behalf of the application. When using hosted workflows, the application delegates conversation management responsibilities to OpenAI's infrastructure rather than implementing these components locally.

In a hosted workflow configuration:

| Component | Self-Hosted | Hosted Workflows |
|-----------|-------------|------------------|
| **Agent Orchestration** | Local `assistant_agent` instance | Managed by OpenAI infrastructure |
| **Conversation Storage** | Local `MemoryStore` implementation | Managed by OpenAI infrastructure |
| **Request Processing** | Local `StarterChatServer` | Managed workflow endpoint |
| **Infrastructure Maintenance** | Developer responsibility | OpenAI responsibility |

The managed ChatKit integration demonstrates how to connect a frontend application to hosted workflows using simplified backend integration code.

**Sources:** [README.md:8]()

## Managed ChatKit Directory Structure

```mermaid
graph TB
    subgraph ManagedChatKit["managed-chatkit/"]
        MCK_README["README.md<br/>Integration documentation"]
        
        subgraph Backend["backend/"]
            BE_APP["app/<br/>FastAPI application"]
            BE_REQ["requirements.txt<br/>Python dependencies"]
            BE_PYPROJECT["pyproject.toml<br/>Project configuration"]
        end
        
        subgraph Frontend["frontend/"]
            FE_SRC["src/<br/>React components"]
            FE_CONFIG["vite.config.ts<br/>Build configuration"]
            FE_PACKAGE["package.json<br/>Node dependencies"]
        end
    end
    
    MCK_README -.->|"documents"| Backend
    MCK_README -.->|"documents"| Frontend
    
    Backend -->|"HTTP API"| Frontend
```

**Diagram:** Managed ChatKit directory structure showing backend and frontend separation

The `managed-chatkit/` directory contains a complete starter application demonstrating hosted workflow integration. It maintains the same technology stack as the self-hosted variant (FastAPI backend, Vite/React frontend) but implements different integration logic to communicate with OpenAI's hosted infrastructure.

**Sources:** [README.md:8]()

## Operational Model Comparison

```mermaid
sequenceDiagram
    participant User
    participant Frontend as "Frontend Application"
    participant Backend as "Application Backend"
    participant HostedWF as "Hosted Workflows<br/>(OpenAI Infrastructure)"
    participant OpenAI as "OpenAI API"
    
    User->>Frontend: Send message
    Frontend->>Backend: POST request
    Backend->>Backend: Authenticate & validate
    Backend->>HostedWF: Forward to workflow endpoint
    
    Note over HostedWF: Workflow manages:<br/>- Agent orchestration<br/>- Conversation state<br/>- Response generation
    
    HostedWF->>OpenAI: Chat completion request
    
    loop Streaming Response
        OpenAI-->>HostedWF: Response chunks
        HostedWF-->>Backend: Stream events
        Backend-->>Frontend: Proxy stream
        Frontend-->>User: Update UI
    end
    
    Note over HostedWF: Conversation persisted<br/>in hosted infrastructure
```

**Diagram:** Request flow through managed ChatKit with hosted workflows

### Key Operational Differences

**Infrastructure Responsibilities:**

| Aspect | Self-Hosted | Managed (Hosted Workflows) |
|--------|-------------|----------------------------|
| **Conversation Storage** | Developer implements and maintains database | OpenAI manages persistent storage |
| **Agent State Management** | Developer manages agent lifecycle | Workflow handles agent state |
| **Scaling & Performance** | Developer provisions infrastructure | OpenAI handles scaling automatically |
| **Monitoring & Debugging** | Developer implements logging/metrics | Workflow provides built-in observability |
| **Updates & Maintenance** | Developer updates dependencies | OpenAI updates workflow infrastructure |

**Sources:** [README.md:7-8]()

## Integration Architecture

```mermaid
graph TB
    subgraph SelfHosted["Self-Hosted Pattern (chatkit/)"]
        SH_BE["FastAPI Backend"]
        SH_SERVER["StarterChatServer"]
        SH_STORE["MemoryStore"]
        SH_AGENT["assistant_agent"]
        
        SH_BE --> SH_SERVER
        SH_SERVER --> SH_STORE
        SH_SERVER --> SH_AGENT
    end
    
    subgraph Managed["Managed Pattern (managed-chatkit/)"]
        M_BE["FastAPI Backend"]
        M_CLIENT["Workflow Client"]
        
        M_BE --> M_CLIENT
    end
    
    subgraph HostedInfra["OpenAI Hosted Infrastructure"]
        WORKFLOW["Hosted Workflow"]
        WF_STORE["Managed Storage"]
        WF_AGENT["Managed Agent"]
        
        WORKFLOW --> WF_STORE
        WORKFLOW --> WF_AGENT
    end
    
    SH_AGENT -->|"Direct API calls"| OpenAI_API["OpenAI API"]
    M_CLIENT -->|"Workflow endpoint"| WORKFLOW
    WF_AGENT -->|"API calls"| OpenAI_API
```

**Diagram:** Comparison of self-hosted vs managed integration architectures showing component responsibilities

In the self-hosted pattern, the application backend implements all conversation management components (`StarterChatServer`, `MemoryStore`, `assistant_agent`). In the managed pattern, these responsibilities shift to the hosted workflow infrastructure, and the application backend only needs to implement authentication, validation, and request forwarding logic.

**Sources:** [README.md:7-8]()

## Domain Keys and Workflow Authentication

Managed ChatKit integrations use domain-specific authentication credentials to access hosted workflows:

| Environment Variable | Purpose | Example Value |
|---------------------|---------|---------------|
| `VITE_CHATKIT_API_DOMAIN_KEY` | Identifies workflow domain | `domain_pk_localhost_dev` (development) |
| `OPENAI_API_KEY` | Authenticates API access | OpenAI API key |

The domain key associates requests with a specific hosted workflow configuration. In development, applications typically use `domain_pk_localhost_dev`. Production deployments require production-specific domain keys obtained from OpenAI.

**Sources:** Based on high-level architecture diagrams

## When to Choose Managed ChatKit

### Choose Managed ChatKit When:

- **Minimal operational overhead** is required
- **Rapid prototyping** without infrastructure setup is desired
- **Automatic scaling** and maintenance are important
- **Built-in persistence** eliminates database management needs
- **Team expertise** focuses on application logic rather than infrastructure

### Choose Self-Hosted ChatKit When:

- **Complete control** over conversation storage is required
- **Custom integration logic** beyond workflow capabilities is needed
- **Data residency** or compliance requires on-premises storage
- **Existing infrastructure** is already available for conversation management
- **Cost optimization** through self-managed resources is preferred

**Sources:** [README.md:1-9]()

## Integration Code Differences

```mermaid
graph LR
    subgraph Application["Application Code"]
        APP_LOGIC["Business Logic"]
    end
    
    subgraph SelfHosted["Self-Hosted Components"]
        IMPLEMENT["Implement:<br/>- Server class<br/>- Store class<br/>- Agent configuration<br/>- Stream handling"]
    end
    
    subgraph Managed["Managed Components"]
        INTEGRATE["Integrate:<br/>- Workflow client<br/>- Authentication<br/>- Request forwarding"]
    end
    
    APP_LOGIC -->|"Self-hosted path"| IMPLEMENT
    APP_LOGIC -->|"Managed path"| INTEGRATE
    
    IMPLEMENT -.->|"More code"| DEV_TIME["Higher development effort"]
    INTEGRATE -.->|"Less code"| DEV_TIME2["Lower development effort"]
```

**Diagram:** Development effort comparison between self-hosted and managed implementations

The managed ChatKit backend requires significantly less implementation code than the self-hosted variant. Developers implement authentication and request forwarding rather than conversation management infrastructure, reducing initial development time and ongoing maintenance requirements.

**Sources:** [README.md:7-8]()

## Getting Started with Managed ChatKit

The `managed-chatkit/` directory provides a complete working example:

1. **Backend Setup**: Configure FastAPI application with workflow client integration
2. **Frontend Setup**: Connect React application to backend endpoint
3. **Environment Configuration**: Set `OPENAI_API_KEY` and `VITE_CHATKIT_API_DOMAIN_KEY`
4. **Development Server**: Run `npm run dev` to start both backend and frontend

Detailed setup instructions are provided in the managed-chatkit directory's README.

For installation and configuration details, see [Getting Started](#2). For architectural implementation details, see [Architecture Differences](#4.2).

**Sources:** [README.md:8]()

---

# Page: Architecture Differences

# Architecture Differences

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

This document details the architectural differences between the self-hosted ChatKit implementation ([chatkit/]()) and the managed ChatKit implementation ([managed-chatkit/]()). While both starter applications share identical technology stacks and similar project structures, they differ fundamentally in where conversation logic executes and how operational responsibilities are distributed.

For an overview of hosted workflows and the managed integration approach, see [Overview & Hosted Workflows](#4.1). For detailed self-hosted architecture documentation, see [Architecture Overview](#3.1).

## High-Level Architectural Comparison

The two implementations represent different operational models for ChatKit integration:

| Aspect | Self-Hosted (chatkit/) | Managed (managed-chatkit/) |
|--------|------------------------|----------------------------|
| **Conversation Logic** | Runs in developer-controlled FastAPI backend | Delegated to hosted workflows |
| **Infrastructure Responsibility** | Developer manages all services | OpenAI manages workflow execution |
| **Agent Execution** | Local `assistant_agent` instance | Hosted workflow processing |
| **Data Persistence** | Developer implements storage (MemoryStore example) | Managed by hosted infrastructure |
| **Operational Complexity** | Higher (full control) | Lower (reduced operational burden) |
| **Customization Flexibility** | Complete control over logic | Constrained to workflow configuration |

**Sources:** [README.md:1-9]()

## Component Architecture Comparison

### Self-Hosted Architecture (chatkit/)

```mermaid
graph TB
    subgraph "Developer Infrastructure"
        FE["React Frontend<br/>(Vite)"]
        BE["FastAPI Backend"]
        
        subgraph "Backend Components"
            SERVER["StarterChatServer<br/>app/server.py"]
            STORE["MemoryStore<br/>In-memory persistence"]
            AGENT["assistant_agent<br/>gpt-4o-mini"]
        end
    end
    
    subgraph "OpenAI Services"
        API["OpenAI API<br/>Chat Completions"]
        CHATKIT_LIB["openai-chatkit library"]
    end
    
    FE -->|"POST /chatkit"| BE
    BE --> SERVER
    SERVER --> STORE
    SERVER --> AGENT
    AGENT --> CHATKIT_LIB
    CHATKIT_LIB --> API
    API -->|"Streaming response"| CHATKIT_LIB
    CHATKIT_LIB -->|"Thread events"| AGENT
    AGENT --> SERVER
    SERVER -->|"HTTP response"| BE
    BE --> FE
```

In the self-hosted architecture, all conversation orchestration occurs within the developer's infrastructure. The `StarterChatServer` class loads conversation history from `MemoryStore`, prepares context for the `assistant_agent`, and streams responses through the FastAPI backend.

**Sources:** [README.md:7]()

### Managed Architecture (managed-chatkit/)

```mermaid
graph TB
    subgraph "Developer Infrastructure"
        FE_M["React Frontend<br/>(Vite)"]
        BE_M["FastAPI Backend<br/>(Minimal)"]
    end
    
    subgraph "OpenAI Hosted Infrastructure"
        WORKFLOW["Hosted Workflow<br/>Execution Environment"]
        PERSIST["Managed Persistence"]
        AGENT_M["Managed Agent<br/>Execution"]
    end
    
    subgraph "OpenAI Services"
        API_M["OpenAI API<br/>Chat Completions"]
    end
    
    FE_M -->|"POST /chatkit"| BE_M
    BE_M -->|"Workflow invocation"| WORKFLOW
    WORKFLOW --> PERSIST
    WORKFLOW --> AGENT_M
    AGENT_M --> API_M
    API_M -->|"Streaming response"| AGENT_M
    AGENT_M --> WORKFLOW
    WORKFLOW -->|"HTTP response"| BE_M
    BE_M --> FE_M
```

The managed architecture offloads conversation orchestration to hosted workflows. The developer's FastAPI backend serves primarily as a routing layer, forwarding requests to the hosted workflow environment where agent execution and persistence are handled by OpenAI infrastructure.

**Sources:** [README.md:8]()

## Key Architectural Differences

### 1. Backend Responsibility

**Self-Hosted:**
- Backend implements full `StarterChatServer` orchestration logic
- Manages `MemoryStore` for conversation persistence
- Instantiates and configures `assistant_agent` locally
- Handles streaming event conversion and response formatting
- Developer responsible for scaling, monitoring, and availability

**Managed:**
- Backend acts as thin API proxy layer
- Workflow invocation replaces local orchestration
- No local agent instantiation required
- Hosted infrastructure handles event streaming
- OpenAI responsible for workflow scaling and availability

### 2. Data Persistence Model

```mermaid
graph LR
    subgraph "Self-Hosted Pattern"
        REQ_S["Request"] --> SRV_S["StarterChatServer"]
        SRV_S --> MS["MemoryStore"]
        MS --> DD_S["Developer-Managed<br/>Data Store"]
        DD_S -->|"load_thread_items()"| MS
        MS -->|"save_item()"| DD_S
    end
    
    subgraph "Managed Pattern"
        REQ_M["Request"] --> PROXY["Backend Proxy"]
        PROXY --> WF["Hosted Workflow"]
        WF --> MP["Managed Persistence"]
        MP --> HP["OpenAI-Managed<br/>Data Store"]
        HP -->|"Automatic retrieval"| MP
        MP -->|"Automatic persistence"| HP
    end
```

**Self-Hosted:** Developer implements storage interface (example: `MemoryStore` with methods like `load_thread_items()`, `save_item()`). Production requires replacing with persistent database.

**Managed:** Persistence handled automatically by hosted infrastructure. Developer does not implement or manage storage layer directly.

**Sources:** [README.md:1-9]()

### 3. Agent Configuration and Execution

**Self-Hosted:**
- Direct instantiation of agent in backend code
- Full control over agent parameters (model, temperature, tools)
- Agent runs in developer's compute environment
- Can customize agent behavior through code modifications

**Managed:**
- Agent configured through workflow definitions
- Limited to workflow-supported configuration options
- Agent execution occurs in hosted environment
- Customization constrained to workflow API surface

### 4. Request Flow Comparison

```mermaid
sequenceDiagram
    participant U as "User"
    participant FE as "Frontend"
    
    rect rgb(240, 240, 240)
        Note over FE,BE_S: Self-Hosted Flow
        participant BE_S as "Backend"
        participant SRV as "StarterChatServer"
        participant STR as "MemoryStore"
        participant AGT as "assistant_agent"
    end
    
    rect rgb(250, 250, 250)
        Note over FE,WF: Managed Flow
        participant BE_M as "Backend Proxy"
        participant WF as "Hosted Workflow"
    end
    
    U->>FE: "Send message"
    
    Note over FE,AGT: Self-Hosted Processing
    FE->>BE_S: "POST /chatkit"
    BE_S->>SRV: "process(payload)"
    SRV->>STR: "load_thread_items()"
    STR-->>SRV: "history"
    SRV->>AGT: "run_streamed()"
    AGT-->>SRV: "stream events"
    SRV-->>BE_S: "streaming response"
    BE_S-->>FE: "SSE stream"
    
    Note over FE,WF: Managed Processing
    FE->>BE_M: "POST /chatkit"
    BE_M->>WF: "invoke workflow"
    WF-->>WF: "Load history<br/>Execute agent<br/>Persist results"
    WF-->>BE_M: "streaming response"
    BE_M-->>FE: "SSE stream"
    
    FE-->>U: "Display response"
```

The self-hosted flow requires multiple local component interactions, while the managed flow consolidates these operations within the hosted workflow environment.

**Sources:** [README.md:1-9]()

## Technology Stack Overlap and Divergence

### Shared Components

Both implementations use:

| Component | Purpose | Location |
|-----------|---------|----------|
| **FastAPI** | HTTP server framework | Backend |
| **Uvicorn** | ASGI server | Backend |
| **Vite** | Frontend build tool | Frontend |
| **React** | UI framework | Frontend |
| **TypeScript** | Frontend type safety | Frontend |
| **openai-chatkit** | ChatKit client library | Backend |

### Divergent Components

| Component | Self-Hosted | Managed |
|-----------|-------------|---------|
| **Orchestration** | `StarterChatServer` class | Hosted workflow API |
| **Persistence** | `MemoryStore` (example implementation) | Managed persistence service |
| **Agent Runtime** | Local `assistant_agent` instance | Hosted agent execution |
| **Backend Complexity** | Full server implementation | Minimal proxy layer |

**Sources:** [README.md:1-9]()

## Operational Differences

### Development and Testing

**Self-Hosted:**
- Complete local development environment
- Can debug full request flow in local IDE
- Test storage implementations locally
- Modify agent behavior without external dependencies

**Managed:**
- Local development proxies to hosted workflows
- Limited visibility into workflow execution internals
- Cannot test workflow logic locally (requires hosted environment)
- Agent behavior changes require workflow reconfiguration

### Deployment Considerations

```mermaid
graph TB
    subgraph "Self-Hosted Deployment"
        DEV_S["Developer"] -->|"Provisions"| INFRA["Infrastructure<br/>(Compute, Database)"]
        INFRA --> DEPLOY_S["Deploy Backend"]
        DEPLOY_S --> MONITOR["Monitoring & Scaling"]
        MONITOR -->|"Responsibility"| DEV_S
    end
    
    subgraph "Managed Deployment"
        DEV_M["Developer"] -->|"Configures"| WF_DEF["Workflow Definition"]
        WF_DEF --> DEPLOY_M["Deploy Backend Proxy"]
        DEPLOY_M --> HOSTED["Hosted Infrastructure<br/>(Auto-scaled)"]
        HOSTED -->|"Managed by"| OPENAI["OpenAI"]
    end
```

**Self-Hosted Deployment Requirements:**
- Provision compute infrastructure for FastAPI backend
- Configure and manage persistent database
- Implement monitoring and logging
- Handle scaling for traffic patterns
- Maintain agent runtime environment

**Managed Deployment Requirements:**
- Configure workflow definitions
- Deploy minimal backend proxy
- Monitor workflow invocations (via hosted platform)
- Reduced operational overhead

**Sources:** [README.md:1-9]()

### Customization Boundaries

**Self-Hosted Customization Points:**
- Replace `MemoryStore` with any database ([backend/app/server.py]())
- Modify `assistant_agent` configuration and tools
- Implement custom preprocessing/postprocessing logic
- Add middleware and authentication layers
- Control streaming event transformation

**Managed Customization Points:**
- Configure workflow parameters within hosted platform
- Customize frontend UI components
- Modify backend proxy routing logic
- Limited to workflow API capabilities

## Code Entity Mapping

### Self-Hosted Key Classes and Files

```mermaid
graph TB
    MAIN_S["main.py<br/>FastAPI app entrypoint"] --> ENDPOINT_S["/chatkit endpoint<br/>POST handler"]
    ENDPOINT_S --> SERVER_S["StarterChatServer<br/>server.py"]
    SERVER_S --> RESPOND["respond() method<br/>Orchestrates request"]
    
    RESPOND --> LOAD["load_thread_items()<br/>MemoryStore"]
    RESPOND --> CONVERT["simple_to_agent_input()<br/>Format conversion"]
    RESPOND --> AGENT_S["assistant_agent.run_streamed()<br/>Agent execution"]
    
    SERVER_S --> STORE_S["MemoryStore class<br/>In-memory storage"]
    STORE_S --> THREADS["_threads: Dict<br/>ThreadMetadata"]
    STORE_S --> ITEMS["_thread_items: Dict<br/>ThreadItems"]
```

**Sources:** [README.md:7]()

### Managed Key Components (Conceptual)

```mermaid
graph TB
    MAIN_M["main.py<br/>FastAPI proxy entrypoint"] --> ENDPOINT_M["/chatkit endpoint<br/>POST handler"]
    ENDPOINT_M --> PROXY["Workflow invocation<br/>HTTP client"]
    
    PROXY --> HOSTED["Hosted Workflow API"]
    HOSTED --> WF_EXEC["Workflow Execution Engine<br/>(OpenAI managed)"]
    WF_EXEC --> PERSIST_M["Managed Persistence Layer"]
    WF_EXEC --> AGENT_M["Managed Agent Runtime"]
```

The managed implementation abstracts away the `StarterChatServer`, `MemoryStore`, and local agent execution into hosted workflow services.

**Sources:** [README.md:8]()

## Decision Matrix: When to Use Each Pattern

| Scenario | Recommended Pattern | Rationale |
|----------|---------------------|-----------|
| **Prototyping and learning** | Self-Hosted | Complete visibility into implementation details |
| **Production with custom storage** | Self-Hosted | Full control over persistence layer |
| **Custom agent behaviors** | Self-Hosted | Unrestricted agent configuration and tool integration |
| **Rapid deployment** | Managed | Reduced infrastructure setup |
| **Minimal operational overhead** | Managed | No need to manage scaling and availability |
| **Compliance requirements** | Self-Hosted | Data remains in developer-controlled infrastructure |
| **Standard workflow patterns** | Managed | Leverage hosted infrastructure optimizations |

**Sources:** [README.md:1-9]()

## Summary

The architectural differences between self-hosted and managed ChatKit stem from the fundamental choice of where conversation orchestration executes:

- **Self-Hosted ([chatkit/]())**: Full-featured implementation with `StarterChatServer`, `MemoryStore`, and local `assistant_agent` execution. Provides complete control and customization at the cost of operational responsibility.

- **Managed ([managed-chatkit/]())**: Simplified implementation that delegates orchestration to hosted workflows. Reduces operational burden while constraining customization to workflow API capabilities.

Both share identical frontend and backend technology stacks (FastAPI, Vite, React), differing primarily in backend logic complexity and operational responsibility distribution.

**Sources:** [README.md:1-9]()

---

# Page: Dependencies & Package Management

# Package Management & Dependencies

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [chatkit/.env.example](chatkit/.env.example)
- [chatkit/.gitignore](chatkit/.gitignore)
- [chatkit/README.md](chatkit/README.md)
- [chatkit/backend/.gitignore](chatkit/backend/.gitignore)
- [chatkit/backend/app/__init__.py](chatkit/backend/app/__init__.py)
- [chatkit/backend/pyproject.toml](chatkit/backend/pyproject.toml)

</details>



This document describes the package management system for the OpenAI ChatKit Starter App, including the role of `package.json` and `package-lock.json`, the dependency structure, and how packages are installed and locked for reproducible builds. This page provides an overview of the dependency management system; for detailed information about specific dependency categories, see [Core Dependencies](#3.1), [Development Dependencies](#3.2), and [Optional Dependencies](#3.3). For information about how the CI/CD pipeline uses these files, see [CI/CD Pipeline](#4).

## Package Management Files

The application uses two critical files for dependency management:

| File | Purpose | Version Control |
|------|---------|----------------|
| `package.json` | Declares dependencies with version ranges | Committed to Git |
| `package-lock.json` | Locks exact versions and dependency tree | Committed to Git |

The `package.json` file [package.json:1-33]() defines the project metadata, scripts, and dependency specifications. The `package-lock.json` file [package-lock.json:1-30]() ensures that every installation produces identical dependency trees by recording exact package versions, dependency relationships, and integrity hashes.

**Sources:** [package.json:1-33](), [package-lock.json:1-6]()

## Package Metadata and Scripts

The project is identified as `openai-chatkit-starter-app` version `0.1.0` and is marked as private [package.json:2-4](). Five npm scripts are defined for development and production workflows:

```mermaid
graph LR
    subgraph "npm Scripts"
        DEV["npm run dev<br/>next dev"]
        BUILD["npm run build<br/>next build"]
        START["npm run start<br/>next start"]
        LINT["npm run lint<br/>eslint"]
    end
    
    subgraph "Outputs"
        DEV_SERVER["Development Server<br/>Port 3000"]
        BUILD_DIR[".next/<br/>Production Build"]
        PROD_SERVER["Production Server"]
        LINT_REPORT["Lint Results"]
    end
    
    DEV --> DEV_SERVER
    BUILD --> BUILD_DIR
    START --> PROD_SERVER
    LINT --> LINT_REPORT
    
    BUILD_DIR -.->|"requires"| START
```

**npm run dev**: Starts the Next.js development server with hot module replacement  
**npm run build**: Creates an optimized production build in the `.next/` directory  
**npm run start**: Serves the production build  
**npm run lint**: Runs ESLint for code quality checks

**Sources:** [package.json:5-10]()

## Dependency Categories

The project organizes dependencies into three categories, each serving distinct purposes in the development and runtime lifecycle:

```mermaid
graph TD
    subgraph "package.json Structure"
        PKG["package.json"]
        
        DEPS["dependencies<br/>Production Runtime"]
        DEV_DEPS["devDependencies<br/>Build & Development Tools"]
        OPT_DEPS["optionalDependencies<br/>Platform Optimizations"]
    end
    
    subgraph "Production Dependencies"
        NEXT["next: ^15.5.4"]
        REACT["react: ^19.2.0"]
        REACT_DOM["react-dom: ^19.2.0"]
        CHATKIT["@openai/chatkit-react: ^0"]
    end
    
    subgraph "Development Dependencies"
        TS["typescript: ^5"]
        ESLINT["eslint: ^9"]
        ESLINT_CONFIG["eslint-config-next: 15.5.4"]
        TAILWIND["tailwindcss: ^4"]
        TW_POSTCSS["@tailwindcss/postcss: ^4"]
        TYPES_NODE["@types/node: ^20"]
        TYPES_REACT["@types/react: ^19"]
    end
    
    subgraph "Optional Dependencies"
        LIGHTNING["lightningcss-linux-x64-gnu: 1.30.1"]
        OXIDE["@tailwindcss/oxide-linux-x64-gnu: 4.1.11"]
    end
    
    PKG --> DEPS
    PKG --> DEV_DEPS
    PKG --> OPT_DEPS
    
    DEPS --> NEXT
    DEPS --> REACT
    DEPS --> REACT_DOM
    DEPS --> CHATKIT
    
    DEV_DEPS --> TS
    DEV_DEPS --> ESLINT
    DEV_DEPS --> ESLINT_CONFIG
    DEV_DEPS --> TAILWIND
    DEV_DEPS --> TW_POSTCSS
    DEV_DEPS --> TYPES_NODE
    DEV_DEPS --> TYPES_REACT
    
    OPT_DEPS --> LIGHTNING
    OPT_DEPS --> OXIDE
```

### Production Dependencies

The `dependencies` section [package.json:11-16]() includes packages required at runtime:

| Package | Version | Purpose |
|---------|---------|---------|
| `next` | ^15.5.4 | React framework with server-side rendering |
| `react` | ^19.2.0 | UI library |
| `react-dom` | ^19.2.0 | React renderer for web |
| `@openai/chatkit-react` | ^0 | OpenAI ChatKit React integration |

**Sources:** [package.json:11-16]()

### Development Dependencies

The `devDependencies` section [package.json:21-31]() includes packages required only during development and build:

| Package | Version | Purpose |
|---------|---------|---------|
| `typescript` | ^5 | TypeScript compiler |
| `eslint` | ^9 | JavaScript/TypeScript linter |
| `eslint-config-next` | 15.5.4 | Next.js ESLint configuration |
| `@eslint/eslintrc` | ^3 | ESLint configuration resolver |
| `tailwindcss` | ^4 | Utility-first CSS framework |
| `@tailwindcss/postcss` | ^4 | Tailwind CSS PostCSS plugin |
| `@types/node` | ^20 | TypeScript definitions for Node.js |
| `@types/react` | ^19 | TypeScript definitions for React |
| `@types/react-dom` | ^19 | TypeScript definitions for react-dom |

**Sources:** [package.json:21-31]()

### Optional Dependencies

The `optionalDependencies` section [package.json:17-20]() includes platform-specific native binaries that improve build performance on Linux x64 systems:

| Package | Version | Purpose |
|---------|---------|---------|
| `lightningcss-linux-x64-gnu` | 1.30.1 | Fast CSS transformer (Linux x64) |
| `@tailwindcss/oxide-linux-x64-gnu` | 4.1.11 | Rust-based Tailwind engine (Linux x64) |

These dependencies are marked as optional because they are platform-specific and the build system can function without them using JavaScript-based fallbacks.

**Sources:** [package.json:17-20]()

## Version Constraint Syntax

The project uses npm's semantic versioning notation to specify acceptable version ranges:

| Prefix | Example | Meaning | Lock File Example |
|--------|---------|---------|-------------------|
| `^` (caret) | `^15.5.4` | Compatible with 15.5.4, allows minor and patch updates | [package-lock.json:12]() |
| `^` (caret) | `^0` | Allows any 0.x.x version | [package-lock.json:11]() |
| Exact | `15.5.4` | Exact version only | [package-lock.json:23]() |

The caret (`^`) allows updates that do not change the leftmost non-zero digit, enabling automatic security patches while preventing breaking changes.

**Sources:** [package.json:11-31]()

## Dependency Resolution and Locking

```mermaid
graph TB
    subgraph "Input Files"
        PKG_JSON["package.json<br/>Declares Ranges"]
    end
    
    subgraph "Resolution Process"
        NPM_INSTALL["npm install<br/>or<br/>npm ci"]
        RESOLVE["Dependency Resolver<br/>Determines Exact Versions"]
    end
    
    subgraph "Lock File"
        PKG_LOCK["package-lock.json<br/>lockfileVersion: 3<br/>Records Exact Versions<br/>Dependency Tree<br/>Integrity Hashes"]
    end
    
    subgraph "Installation"
        NODE_MODULES["node_modules/<br/>Installed Packages"]
    end
    
    PKG_JSON -->|"defines ranges"| NPM_INSTALL
    NPM_INSTALL --> RESOLVE
    RESOLVE -->|"writes/reads"| PKG_LOCK
    PKG_LOCK -->|"ensures reproducibility"| NODE_MODULES
    
    PKG_LOCK -->|"committed to Git"| PKG_LOCK
```

The `package-lock.json` uses `lockfileVersion: 3` [package-lock.json:4](), which is the format introduced in npm v7. This file contains:

1. **Exact Versions**: Each package's resolved version [package-lock.json:12-14]()
2. **Dependency Tree**: The complete nested dependency structure [package-lock.json:6-30]()
3. **Integrity Hashes**: SHA-512 checksums for package verification (e.g., [package-lock.json:35]())
4. **Registry URLs**: Source locations for each package (e.g., [package-lock.json:34]())

**Sources:** [package-lock.json:1-6]()

## Installation Process

The CI/CD pipeline and local development use different installation commands:

### CI Installation: `npm ci`

The GitHub Actions workflow [.github/workflows/ci.yml]() uses `npm ci` for clean, reproducible installations:

- Deletes existing `node_modules/` before installation
- Installs exact versions from `package-lock.json`
- Fails if `package.json` and `package-lock.json` are out of sync
- Faster than `npm install` in CI environments

### Local Development: `npm install`

For local development, `npm install`:

- Installs packages based on `package.json` ranges
- Updates `package-lock.json` if needed
- Preserves existing compatible packages in `node_modules/`

**Sources:** [package.json:1-33](), [package-lock.json:1-6]()

## Transitive Dependencies

The lock file records all transitive (indirect) dependencies. For example, the `next` package depends on numerous sub-packages:

```mermaid
graph TD
    NEXT["next@15.5.4"]
    
    ENV["@next/env@15.5.4"]
    SWC_DARWIN_ARM["@next/swc-darwin-arm64@15.5.4"]
    SWC_DARWIN_X64["@next/swc-darwin-x64@15.5.4"]
    SWC_LINUX_ARM["@next/swc-linux-arm64-gnu@15.5.4"]
    SWC_LINUX_X64["@next/swc-linux-x64-gnu@15.5.4"]
    SWC_WIN_X64["@next/swc-win32-x64-msvc@15.5.4"]
    
    NEXT --> ENV
    NEXT -.->|"optional"| SWC_DARWIN_ARM
    NEXT -.->|"optional"| SWC_DARWIN_X64
    NEXT -.->|"optional"| SWC_LINUX_ARM
    NEXT -.->|"optional"| SWC_LINUX_X64
    NEXT -.->|"optional"| SWC_WIN_X64
```

Platform-specific packages like `@next/swc-*` are marked as optional dependencies [package-lock.json:794-920]() and only install on matching platforms, reducing installation size and time.

**Sources:** [package-lock.json:778-920]()

## Native Binary Packages

Several packages include platform-specific native binaries compiled from Rust or C++. The lock file contains multiple platform variants that are conditionally installed:

| Package Family | Platforms | Purpose |
|---------------|-----------|---------|
| `@next/swc-*` | darwin-arm64, darwin-x64, linux-arm64-gnu, linux-x64-gnu, win32-x64-msvc | Next.js SWC compiler |
| `@tailwindcss/oxide-*` | darwin-arm64, darwin-x64, linux-x64-gnu, linux-arm64-gnu, win32-x64-msvc | Tailwind CSS Rust engine |
| `lightningcss-*` | linux-x64-gnu | CSS transformer |

Each variant specifies CPU architecture and operating system constraints via `cpu` and `os` fields [package-lock.json:798-805](), ensuring the correct binary is installed for the host system.

**Sources:** [package-lock.json:794-1272]()

## Integrity and Security

Every package in the lock file includes an integrity hash using the Subresource Integrity format:

```
"integrity": "sha512-27SQhYp5QryzIT5uO8hq99C69eLQ7qkzkDPsk3N+GuS2XgOgoYEeOav7Pf8Tn4drECOVDsDg8oj+/DVy8qQL2A=="
```

npm verifies these hashes during installation to ensure package contents have not been tampered with. The `resolved` field [package-lock.json:780]() specifies the registry URL where the package was originally downloaded.

**Sources:** [package-lock.json:778-783]()

## Package Count Summary

The lock file defines thousands of packages in the complete dependency tree:

| Category | Direct Count | Notes |
|----------|--------------|-------|
| Production Dependencies | 4 | Runtime-required packages |
| Development Dependencies | 9 | Build and tooling packages |
| Optional Dependencies | 2 | Platform-specific optimizations |
| Total Transitive Dependencies | ~1000+ | All nested dependencies in `node_modules/` |

This extensive tree is necessary to support the full Next.js, React, TypeScript, and Tailwind CSS ecosystem.

**Sources:** [package.json:11-31](), [package-lock.json:6-30]()

---

# Page: Backend Dependencies

# Backend Dependencies

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [chatkit/backend/pyproject.toml](chatkit/backend/pyproject.toml)

</details>



## Purpose and Scope

This document provides a comprehensive reference for all Python dependencies required by the backend components of the ChatKit starter applications. Both `chatkit/backend` and `managed-chatkit/backend` share identical dependency specifications defined in their respective `pyproject.toml` files. This page covers runtime dependencies, version constraints, and their roles in the system.

For frontend dependencies, see [Frontend Dependencies](#5.2). For development tooling (linters, formatters, type checkers), see [Development Tools](#5.3).

## Package Management Configuration

The backend uses modern Python packaging standards with `pyproject.toml` as the single source of dependency declarations. The configuration specifies both runtime dependencies and optional development dependencies.

**Key Configuration Attributes:**

| Attribute | Value | Purpose |
|-----------|-------|---------|
| `requires-python` | `>=3.11` | Minimum Python version requirement |
| `dependencies` | Core runtime packages | Required for application execution |
| `project.optional-dependencies.dev` | Development packages | Optional tools for local development |
| `build-system` | `setuptools>=68.0` | Build backend for package installation |

Sources: [chatkit/backend/pyproject.toml:1-22]()

## Runtime Dependencies

### FastAPI

**Package:** `fastapi>=0.114,<0.116`

FastAPI is the web framework powering the backend HTTP API. It provides the ASGI application, routing, request/response handling, and OpenAPI documentation generation.

**Version Constraints:**
- Minimum: 0.114 (required features for ChatKit integration)
- Maximum: <0.116 (pinned for stability and compatibility)

**Usage in Codebase:**
- `FastAPI` application instance: [chatkit/backend/app/main.py]()
- Route decorators: `@app.post("/chatkit")` 
- Request models: `Request`, `StarterChatInput`
- Response streaming: `StreamingResponse`

### Uvicorn

**Package:** `uvicorn[standard]>=0.36,<0.37`

Uvicorn is the ASGI server that runs the FastAPI application. The `[standard]` extra includes performance optimizations and additional protocol support (HTTP/2, WebSocket compression).

**Version Constraints:**
- Minimum: 0.36 (compatible with FastAPI 0.114+)
- Maximum: <0.37 (pinned for stability)
- Extra: `[standard]` includes `uvloop`, `httptools`, `websockets`, `watchfiles`

**Usage in Codebase:**
- Command-line invocation: `uvicorn app.main:app --reload`
- Development server startup: [chatkit/backend/app/main.py]()

### OpenAI Python SDK

**Package:** `openai>=1.40`

The official OpenAI Python client library provides access to OpenAI APIs, including chat completions, embeddings, and other model endpoints.

**Version Constraints:**
- Minimum: 1.40 (required for compatibility with `openai-chatkit`)
- No maximum constraint (accepts newer versions)

**Usage in Codebase:**
- Indirectly through `openai-chatkit` library
- API authentication via `OPENAI_API_KEY` environment variable

### OpenAI ChatKit

**Package:** `openai-chatkit>=1.4.0,<2`

The OpenAI ChatKit library provides high-level abstractions for building conversational AI applications, including thread management, agent runtime, and streaming support.

**Version Constraints:**
- Minimum: 1.4.0 (stable ChatKit API)
- Maximum: <2 (major version constraint to prevent breaking changes)

**Usage in Codebase:**
- `StarterChatServer` base class: [chatkit/backend/app/server.py]()
- `assistant_agent` function
- `AgentInput`, `AgentContext` types
- `simple_to_agent_input` conversion utility
- Store interface: `load_thread_items`, `save_item`

Sources: [chatkit/backend/pyproject.toml:6-11]()

## Development Dependencies

### Ruff

**Package:** `ruff>=0.6.4,<0.7`

Ruff is an extremely fast Python linter and formatter written in Rust. It replaces multiple tools (Flake8, isort, Black) with a single executable.

**Version Constraints:**
- Minimum: 0.6.4 (latest stable feature set)
- Maximum: <0.7 (pinned for consistent formatting behavior)

**Usage in CI/CD:**
- Linting: `ruff check .`
- Formatting: `ruff format --check .`
- See [Python Quality Checks](#6.2) for CI workflow integration

**Note:** While `ruff` is listed in `pyproject.toml` under `[project.optional-dependencies]`, the type checker `mypy` is not explicitly declared but is used in CI validation workflows.

Sources: [chatkit/backend/pyproject.toml:13-16]()

## Dependency Architecture

### Runtime Dependency Graph

```mermaid
graph TB
    subgraph "Application Layer"
        APP["FastAPI Application<br/>(app/main.py)"]
        SERVER["StarterChatServer<br/>(app/server.py)"]
    end
    
    subgraph "Core Dependencies"
        FASTAPI["fastapi>=0.114,<0.116"]
        UVICORN["uvicorn[standard]>=0.36,<0.37"]
        OPENAI["openai>=1.40"]
        CHATKIT["openai-chatkit>=1.4.0,<2"]
    end
    
    subgraph "External Services"
        API["OpenAI API"]
    end
    
    APP --> FASTAPI
    APP --> SERVER
    SERVER --> CHATKIT
    CHATKIT --> OPENAI
    OPENAI --> API
    UVICORN --> APP
    
    classDef appLayer fill:#f9f9f9
    classDef depLayer fill:#e8e8e8
    classDef external fill:#d8d8d8
    
    class APP,SERVER appLayer
    class FASTAPI,UVICORN,OPENAI,CHATKIT depLayer
    class API external
```

**Diagram: Backend Dependency Hierarchy**

This diagram illustrates the layered dependency structure where application code depends on framework libraries (FastAPI, ChatKit), which in turn depend on client SDKs (openai), ultimately connecting to external services.

Sources: [chatkit/backend/pyproject.toml:1-22]()

### Code Entity Mapping

```mermaid
graph LR
    subgraph "Dependencies"
        FASTAPI_PKG["fastapi"]
        CHATKIT_PKG["openai-chatkit"]
        OPENAI_PKG["openai"]
    end
    
    subgraph "Code Entities"
        FASTAPI_CLASS["FastAPI"]
        POST_DECORATOR["@app.post"]
        STREAMING["StreamingResponse"]
        
        SERVER_CLASS["StarterChatServer"]
        AGENT_FUNC["assistant_agent"]
        SIMPLE_TO_AGENT["simple_to_agent_input"]
        STORE_METHOD["load_thread_items"]
        
        OPENAI_CLIENT["OpenAI"]
    end
    
    subgraph "Files"
        MAIN["app/main.py"]
        SERVER["app/server.py"]
    end
    
    FASTAPI_PKG --> FASTAPI_CLASS
    FASTAPI_PKG --> POST_DECORATOR
    FASTAPI_PKG --> STREAMING
    
    CHATKIT_PKG --> SERVER_CLASS
    CHATKIT_PKG --> AGENT_FUNC
    CHATKIT_PKG --> SIMPLE_TO_AGENT["simple_to_agent_input"]
    CHATKIT_PKG --> STORE_METHOD
    
    OPENAI_PKG --> OPENAI_CLIENT
    
    FASTAPI_CLASS --> MAIN
    POST_DECORATOR --> MAIN
    STREAMING --> MAIN
    
    SERVER_CLASS --> SERVER
    AGENT_FUNC --> SERVER
    SIMPLE_TO_AGENT --> SERVER
    STORE_METHOD --> SERVER
```

**Diagram: Dependency to Code Entity Mapping**

This diagram maps Python packages to the specific classes, functions, and decorators imported from them, showing where each dependency's API surface is utilized in the codebase.

Sources: [chatkit/backend/pyproject.toml:6-11](), [chatkit/backend/app/main.py](), [chatkit/backend/app/server.py]()

## Build System Configuration

The build system uses `setuptools` as the PEP 517 build backend, which is the standard tool for creating installable Python packages.

**Configuration:**

| Component | Value | Purpose |
|-----------|-------|---------|
| `requires` | `setuptools>=68.0`, `wheel` | Build-time dependencies |
| `build-backend` | `setuptools.build_meta` | Build backend module path |

**Installation Methods:**

```
# Development installation (editable mode)
pip install -e .

# Development installation with dev dependencies
pip install -e ".[dev]"

# Production installation
pip install .
```

The editable installation (`-e` flag) allows code changes to take effect immediately without reinstallation, which is useful for local development.

Sources: [chatkit/backend/pyproject.toml:18-20]()

## Version Constraint Strategy

The dependency specifications follow a deliberate versioning strategy:

### Tightly Constrained Dependencies

**FastAPI and Uvicorn:**
- Use both minimum and maximum version constraints
- Strategy: Pin to known-compatible minor versions
- Rationale: Web framework stability, prevent breaking API changes

**OpenAI ChatKit:**
- Constrained to major version 1.x
- Strategy: Allow patch and minor updates within v1
- Rationale: Prevent breaking changes from v2, allow bug fixes

### Loosely Constrained Dependencies

**OpenAI SDK:**
- Only minimum version specified
- Strategy: Accept any version ≥1.40
- Rationale: Mature, stable API; ChatKit handles compatibility

### Development Tools

**Ruff:**
- Constrained to 0.6.x
- Strategy: Pin to specific minor version
- Rationale: Ensure consistent linting/formatting behavior across team

Sources: [chatkit/backend/pyproject.toml:6-16]()

## Dependency Usage Summary

| Dependency | Primary Role | Key Imports | Used In |
|------------|--------------|-------------|---------|
| `fastapi` | Web framework | `FastAPI`, `Request`, `StreamingResponse` | [app/main.py]() |
| `uvicorn` | ASGI server | Command-line only | Development server |
| `openai` | OpenAI API client | Indirect (via `openai-chatkit`) | N/A |
| `openai-chatkit` | ChatKit framework | `StarterChatServer`, `assistant_agent`, `simple_to_agent_input` | [app/server.py]() |
| `ruff` | Linter/formatter | Command-line only | CI/CD pipeline |

Sources: [chatkit/backend/pyproject.toml:1-22](), [chatkit/backend/app/main.py](), [chatkit/backend/app/server.py]()

---

# Page: Frontend Dependencies

# Frontend Dependencies

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [chatkit/.env.example](chatkit/.env.example)
- [chatkit/.gitignore](chatkit/.gitignore)
- [chatkit/README.md](chatkit/README.md)
- [chatkit/backend/.gitignore](chatkit/backend/.gitignore)
- [chatkit/backend/app/__init__.py](chatkit/backend/app/__init__.py)
- [chatkit/frontend/.gitignore](chatkit/frontend/.gitignore)

</details>



## Purpose and Scope

This page documents the Node.js dependencies and build toolchain used by the frontend applications in both `chatkit/frontend/` and `managed-chatkit/frontend/`. These starter applications share identical dependency structures and build configurations. 

For Python backend dependencies, see [Backend Dependencies](#5.1). For development-specific tooling such as ESLint configuration and linting scripts, see [Development Tools](#5.3). For a higher-level overview of the frontend technology stack and architectural decisions, see [Technology Stack](#3.3.1).

**Sources:** [chatkit/README.md:1-33]()

---

## Node.js Runtime Requirements

The frontend applications require **Node.js version 22** as specified in the CI/CD pipeline and development documentation. The package manager used is **npm**, with all installation and execution commands following standard npm conventions.

The frontend development server runs on `127.0.0.1:3000` by default, with a proxy configured to forward `/chatkit` requests to the backend at `127.0.0.1:8000`.

**Sources:** [chatkit/README.md:14-16](), CI/CD workflow configuration

---

## Core Runtime Dependencies

The frontend build toolchain centers on three primary technologies that work together to deliver a modern, type-safe React application:

| Dependency | Purpose | Role in Build Pipeline |
|------------|---------|----------------------|
| **React** | UI framework | Component rendering and state management |
| **Vite** | Build tool and dev server | Fast HMR, production bundling, asset optimization |
| **TypeScript** | Type system | Static type checking and IDE support |
| **openai-chatkit-react** | ChatKit UI components | Pre-built chat interface components |

### Dependency Relationships

```mermaid
graph TB
    subgraph "Runtime Environment"
        NODE["Node.js 22"]
    end
    
    subgraph "Build System"
        NPM["npm<br/>(Package Manager)"]
        VITE["vite<br/>(Build Tool)"]
    end
    
    subgraph "Core Framework"
        REACT["react<br/>(UI Framework)"]
        REACT_DOM["react-dom<br/>(DOM Renderer)"]
    end
    
    subgraph "Type System"
        TS["typescript<br/>(Type Checker)"]
        TS_VITE["@vitejs/plugin-react<br/>(Vite Integration)"]
    end
    
    subgraph "ChatKit Integration"
        CHATKIT_REACT["openai-chatkit-react<br/>(UI Components)"]
    end
    
    NODE --> NPM
    NPM --> VITE
    NPM --> REACT
    NPM --> TS
    NPM --> CHATKIT_REACT
    
    VITE --> TS_VITE
    VITE --> REACT
    TS_VITE --> TS
    TS_VITE --> REACT_DOM
    
    CHATKIT_REACT --> REACT
    CHATKIT_REACT --> REACT_DOM
```

**Sources:** [chatkit/README.md:3-4](), Technology Stack diagram from high-level architecture

---

## Build Toolchain Components

### Vite Build System

Vite serves as both the development server and production build tool. It provides:

- **Hot Module Replacement (HMR)**: Near-instantaneous updates during development
- **ES Module-based dev server**: Native browser module loading without bundling
- **Production bundling**: Optimized, code-split bundles using Rollup
- **Asset handling**: Processing of CSS, images, and other static assets

The Vite configuration integrates with React through `@vitejs/plugin-react`, which handles JSX transformation and React Fast Refresh during development.

### TypeScript Compilation

TypeScript provides static type checking across the frontend codebase. The build process includes:

1. **Type checking**: Validates types without emitting JavaScript (Vite handles transpilation)
2. **IDE integration**: Enables autocomplete, inline documentation, and refactoring tools
3. **Configuration**: `tsconfig.json` defines compiler options and type resolution rules

### Build Pipeline Sequence

```mermaid
sequenceDiagram
    participant DEV as "Developer"
    participant NPM as "npm"
    participant VITE as "Vite Dev Server"
    participant TS as "TypeScript"
    participant BROWSER as "Browser"
    
    DEV->>NPM: "npm install"
    NPM->>NPM: "Read package.json"
    NPM->>NPM: "Resolve dependency tree"
    NPM->>NPM: "Download to node_modules/"
    
    DEV->>NPM: "npm run dev"
    NPM->>VITE: "Start dev server"
    VITE->>TS: "Check types"
    VITE->>VITE: "Transform JSX/TSX"
    VITE->>BROWSER: "Serve at localhost:3000"
    
    loop Development Cycle
        DEV->>VITE: "Edit source file"
        VITE->>TS: "Incremental type check"
        VITE->>VITE: "Transform module"
        VITE->>BROWSER: "HMR update"
    end
```

**Sources:** [chatkit/README.md:8-16](), Vite documentation patterns

---

## Package Management

### Installation Process

Dependencies are installed using npm's standard installation workflow:

```bash
npm install
```

This command:
1. Reads `package.json` in `chatkit/frontend/` or `managed-chatkit/frontend/`
2. Resolves the dependency tree including transitive dependencies
3. Downloads packages to `node_modules/`
4. Generates or updates `package-lock.json` for reproducible builds

**Sources:** [chatkit/README.md:9]()

### Ignored Build Artifacts

The frontend `.gitignore` configuration excludes generated files and directories from version control:

| Pattern | Purpose |
|---------|---------|
| `node_modules/` | Third-party dependencies (installed via npm) |
| `dist/` | Production build output |
| `.DS_Store` | macOS metadata |
| `*.tsbuildinfo` | TypeScript incremental build cache |
| `npm-debug.log*` | npm error logs |

**Sources:** [chatkit/frontend/.gitignore:1-8]()

---

## Dependency Categories

### Production Dependencies

These packages are required at runtime and included in production bundles:

```mermaid
graph LR
    subgraph "Production Bundle"
        REACT_PKG["react"]
        REACT_DOM_PKG["react-dom"]
        CHATKIT_PKG["openai-chatkit-react"]
    end
    
    subgraph "Application Code"
        CONFIG["config.ts"]
        PANEL["ChatKitPanel.tsx"]
        MAIN["main.tsx"]
    end
    
    MAIN --> REACT_PKG
    MAIN --> REACT_DOM_PKG
    MAIN --> CHATKIT_PKG
    PANEL --> CHATKIT_PKG
    CONFIG --> CHATKIT_PKG
```

### Development Dependencies

These packages are only needed during development and build processes:

- **vite**: Development server and build tool
- **typescript**: Type checking compiler
- **@vitejs/plugin-react**: Vite plugin for React Fast Refresh and JSX
- **@types/react**: TypeScript type definitions for React
- **@types/react-dom**: TypeScript type definitions for ReactDOM
- **eslint**: Code linting (see [Development Tools](#5.3) for configuration details)

**Sources:** Technology stack analysis, [chatkit/README.md:3-4]()

---

## CI/CD Integration

The CI/CD pipeline validates frontend dependencies through automated checks:

```mermaid
graph TB
    subgraph "GitHub Actions Workflow"
        TRIGGER["Push or Pull Request"]
        NODE_JOB["Node.js Job<br/>ubuntu-latest"]
    end
    
    subgraph "Validation Steps"
        CHECKOUT["Checkout code"]
        SETUP["Setup Node.js 22"]
        INSTALL["npm ci"]
        LINT["npm run lint"]
        BUILD["npm run build"]
    end
    
    subgraph "Artifacts"
        LOCK["package-lock.json<br/>(Locked versions)"]
        DIST["dist/<br/>(Build output)"]
    end
    
    TRIGGER --> NODE_JOB
    NODE_JOB --> CHECKOUT
    CHECKOUT --> SETUP
    SETUP --> INSTALL
    INSTALL --> LINT
    LINT --> BUILD
    
    INSTALL -.->|"Uses"| LOCK
    BUILD -.->|"Generates"| DIST
```

The pipeline uses `npm ci` (clean install) rather than `npm install` to ensure reproducible builds based on `package-lock.json`. This guarantees that all environments use identical dependency versions.

**Sources:** CI/CD workflow configuration, Node.js validation pipeline

---

## Environment-Specific Configuration

Frontend dependencies interact with environment variables for configuration:

| Environment Variable | Purpose | Default Value |
|---------------------|---------|---------------|
| `VITE_CHATKIT_API_URL` | Backend API endpoint | `/chatkit` |
| `VITE_CHATKIT_API_DOMAIN_KEY` | ChatKit domain authentication | `domain_pk_localhost_dev` |

These variables are read at **build time** by Vite and embedded in the production bundle. They must be set before running `npm run build` for production deployments.

**Sources:** [chatkit/README.md:20-26](), [chatkit/.env.example:1-3]()

---

## Dependency Update Strategy

When updating dependencies:

1. **Minor updates**: Run `npm update` to update within semver ranges defined in `package.json`
2. **Major updates**: Manually update `package.json` and test thoroughly
3. **Security patches**: Use `npm audit fix` to apply security updates
4. **Lock file**: Always commit updated `package-lock.json` to maintain consistency

The CI/CD pipeline will validate any dependency changes through the full build and lint process before allowing merge to the main branch.

**Sources:** CI/CD validation workflow patterns

---

## Related Frontend Resources

Frontend dependencies support the following customization points:

- **Configuration**: `frontend/src/lib/config.ts` uses environment variables processed at build time
- **Layout components**: `frontend/src/components/ChatKitPanel.tsx` imports from `openai-chatkit-react`
- **Build output**: Production bundles are generated in `dist/` directory

For detailed information on these files and their customization, see [Configuration & Customization](#3.3.2).

**Sources:** [chatkit/README.md:29-32]()

---

# Page: Development Tools

# Development Tools

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [chatkit/backend/pyproject.toml](chatkit/backend/pyproject.toml)

</details>



## Purpose and Scope

This page documents the development tools used across both starter applications (`chatkit/` and `managed-chatkit/`) for code quality enforcement, type checking, and validation. Both projects follow identical development tooling patterns, with Python backends using `ruff` and `mypy`, and JavaScript frontends using `ESLint`.

These tools are configured as development dependencies and are invoked both locally during development and automatically in the CI/CD pipeline. For information about the CI/CD integration, see page 6. For production runtime dependencies, see pages 5.1 (Backend) and 5.2 (Frontend).

## Development Tools Overview

Both starter applications use language-specific development tools for code quality:

| Component | Tools | Purpose |
|-----------|-------|---------|
| **Backend (Python)** | `ruff`<br/>`mypy`<br/>`compileall` | Linting, formatting, type checking, syntax validation |
| **Frontend (Node.js)** | `ESLint`<br/>`Vite` | Code linting, build verification |

**Sources:** [chatkit/backend/pyproject.toml:13-16](), [.github/workflows/ci.yml:36-54](), [.github/workflows/ci.yml:81-87]()

## Development Tools Architecture

### Tool Invocation Flow

```mermaid
graph TB
    subgraph "Backend Python Tools"
        RUFF_DEP["ruff>=0.6.4,<0.7"]
        MYPY_DEP["mypy"]
        COMPILE["python -m compileall"]
    end
    
    subgraph "Frontend Node Tools"
        ESLINT["ESLint"]
        VITE_BUILD["npm run build"]
    end
    
    subgraph "Python Source [*/backend/app]"
        PY_FILES["*.py files"]
    end
    
    subgraph "Frontend Source [*/frontend/src]"
        TS_FILES["*.ts, *.tsx files"]
    end
    
    subgraph "CI Pipeline [.github/workflows/ci.yml]"
        CI_SYNTAX["Syntax check"]
        CI_LINT["Ruff lint"]
        CI_FORMAT["Ruff format"]
        CI_MYPY["mypy"]
        CI_ESLINT["npm run lint"]
        CI_BUILD["npm run build"]
    end
    
    COMPILE --> PY_FILES
    RUFF_DEP --> PY_FILES
    MYPY_DEP --> PY_FILES
    
    ESLINT --> TS_FILES
    VITE_BUILD --> TS_FILES
    
    PY_FILES --> CI_SYNTAX
    CI_SYNTAX --> CI_LINT
    CI_LINT --> CI_FORMAT
    CI_FORMAT --> CI_MYPY
    
    TS_FILES --> CI_ESLINT
    CI_ESLINT --> CI_BUILD
```

Development tools are defined in `pyproject.toml` for Python projects and invoked during CI validation. Frontend tools are installed via `npm ci` and invoked through npm scripts.

**Sources:** [chatkit/backend/pyproject.toml:13-16](), [.github/workflows/ci.yml:36-87]()

## Python Development Tools

### Ruff: Linting and Formatting

`ruff` is an extremely fast Python linter and formatter written in Rust. It is specified as a development dependency in [chatkit/backend/pyproject.toml:15]():

```
ruff>=0.6.4,<0.7
```

#### Ruff Capabilities

| Function | Command | Purpose |
|----------|---------|---------|
| **Linting** | `python -m ruff check app` | Identifies code quality issues, unused imports, and style violations |
| **Formatting** | `python -m ruff format app` | Auto-formats code to consistent style |
| **Format Check** | `python -m ruff format --check app` | Validates formatting without modifying files (CI mode) |

#### Ruff in CI Pipeline

The CI workflow executes ruff in two phases:

1. **Lint Check** ([.github/workflows/ci.yml:40-42]()):
   ```bash
   python -m ruff check app
   ```
   Validates code against linting rules.

2. **Format Check** ([.github/workflows/ci.yml:44-50]()):
   ```bash
   python -m ruff format --check app
   ```
   Ensures all code is formatted consistently. On failure, the CI provides actionable error message suggesting local fix command.

**Sources:** [chatkit/backend/pyproject.toml:15](), [.github/workflows/ci.yml:40-50]()

### mypy: Static Type Checking

`mypy` is a static type checker for Python that validates type annotations. It is installed in the CI environment ([.github/workflows/ci.yml:34]()) but not declared in `pyproject.toml` as a dev dependency, indicating it's a CI-only tool.

#### mypy Configuration

The CI runs mypy with the following command ([.github/workflows/ci.yml:52-54]()):

```bash
python -m mypy app --ignore-missing-imports
```

The `--ignore-missing-imports` flag allows type checking even when third-party libraries lack type stubs.

#### mypy Purpose

`mypy` validates that:
- Function parameters match their type annotations
- Return values match declared return types
- Variables are used consistently with their declared types
- Type annotations are correct throughout the codebase

This catches type-related bugs before runtime, improving code reliability.

**Sources:** [.github/workflows/ci.yml:34](), [.github/workflows/ci.yml:52-54]()

### Python Syntax Validation

Before running any quality tools, the CI performs basic Python syntax validation using the built-in `compileall` module ([.github/workflows/ci.yml:36-38]()):

```bash
python -m compileall app
```

This verifies that all `.py` files can be parsed successfully and contain valid Python syntax. This fast check fails quickly if there are obvious syntax errors.

**Sources:** [.github/workflows/ci.yml:36-38]()

## Node.js Development Tools

### ESLint: Frontend Code Linting

Both frontend applications (`chatkit/frontend` and `managed-chatkit/frontend`) use ESLint for JavaScript/TypeScript code quality enforcement. ESLint is invoked via npm scripts during CI validation.

#### ESLint in CI Pipeline

The CI workflow runs ESLint for both frontend projects ([.github/workflows/ci.yml:81-83]()):

```bash
npm run lint
```

This executes the `lint` script defined in each frontend's `package.json`, which typically runs ESLint against the source code to identify:
- Syntax errors
- Code style violations
- Common programming mistakes
- React-specific issues (hooks rules, etc.)

**Sources:** [.github/workflows/ci.yml:81-83]()

### Vite Build Verification

In addition to linting, the CI performs a production build test ([.github/workflows/ci.yml:85-87]()):

```bash
npm run build
```

This verifies that:
- All TypeScript code compiles successfully
- All imports resolve correctly
- The Vite bundler can generate production-ready artifacts
- No build-time errors exist

A successful build confirms the application can be deployed.

**Sources:** [.github/workflows/ci.yml:85-87]()

## CI/CD Quality Gates

### Python Quality Pipeline

```mermaid
graph LR
    subgraph "Python Projects"
        BE1["chatkit/backend"]
        BE2["managed-chatkit/backend"]
    end
    
    subgraph "Quality Gates [Sequential]"
        SYNTAX["python -m compileall app"]
        LINT["python -m ruff check app"]
        FORMAT["python -m ruff format --check app"]
        TYPECHECK["python -m mypy app --ignore-missing-imports"]
    end
    
    BE1 --> SYNTAX
    BE2 --> SYNTAX
    SYNTAX --> LINT
    LINT --> FORMAT
    FORMAT --> TYPECHECK
    
    TYPECHECK --> PASS["✓ CI Pass"]
    
    FORMAT -.-> FAIL["✗ CI Fail<br/>with fix command"]
```

The Python quality pipeline runs four sequential checks. If ruff format check fails, the CI output includes the command to run locally to fix formatting issues.

**Sources:** [.github/workflows/ci.yml:36-54]()

### Node.js Quality Pipeline

```mermaid
graph LR
    subgraph "Frontend Projects"
        FE1["chatkit/frontend"]
        FE2["managed-chatkit/frontend"]
    end
    
    subgraph "Quality Gates [Sequential]"
        INSTALL["npm ci"]
        LINT_NODE["npm run lint"]
        BUILD_NODE["npm run build"]
    end
    
    FE1 --> INSTALL
    FE2 --> INSTALL
    INSTALL --> LINT_NODE
    LINT_NODE --> BUILD_NODE
    
    BUILD_NODE --> PASS["✓ CI Pass"]
```

The frontend quality pipeline installs dependencies with `npm ci` (using lockfile), runs ESLint, and performs a production build verification.

**Sources:** [.github/workflows/ci.yml:77-87]()

## Local Development Usage

### Running Python Quality Tools Locally

Developers should run quality tools locally before committing code:

#### Install Development Dependencies

```bash
cd chatkit/backend  # or managed-chatkit/backend
python -m pip install ".[dev]"
python -m pip install mypy
```

This installs `ruff` and `mypy` ([.github/workflows/ci.yml:32-34]()).

#### Check Code Quality

```bash
# Syntax check
python -m compileall app

# Lint
python -m ruff check app

# Format check
python -m ruff format --check app

# Apply formatting (if needed)
python -m ruff format app

# Type check
python -m mypy app --ignore-missing-imports
```

Running these commands locally before pushing ensures CI will pass.

**Sources:** [.github/workflows/ci.yml:36-54]()

### Running Node.js Quality Tools Locally

For frontend development:

```bash
cd chatkit/frontend  # or managed-chatkit/frontend

# Install dependencies
npm ci

# Lint
npm run lint

# Build verification
npm run build
```

The `npm ci` command installs exact versions from `package-lock.json`, ensuring consistency with CI ([.github/workflows/ci.yml:79]()).

**Sources:** [.github/workflows/ci.yml:77-87]()

## Matrix Strategy for Multi-Project Validation

### Parallel Project Validation

```mermaid
graph TB
    subgraph "CI Trigger [push/PR]"
        TRIGGER["GitHub Actions Trigger"]
    end
    
    subgraph "Python Matrix Strategy"
        PY_MATRIX["matrix.project:<br/>- chatkit/backend<br/>- managed-chatkit/backend"]
    end
    
    subgraph "Node Matrix Strategy"
        NODE_MATRIX["matrix.project:<br/>- chatkit/frontend<br/>- managed-chatkit/frontend"]
    end
    
    subgraph "Python Jobs [Parallel]"
        PY_JOB1["chatkit/backend checks"]
        PY_JOB2["managed-chatkit/backend checks"]
    end
    
    subgraph "Node Jobs [Parallel]"
        NODE_JOB1["chatkit/frontend checks"]
        NODE_JOB2["managed-chatkit/frontend checks"]
    end
    
    TRIGGER --> PY_MATRIX
    TRIGGER --> NODE_MATRIX
    
    PY_MATRIX --> PY_JOB1
    PY_MATRIX --> PY_JOB2
    
    NODE_MATRIX --> NODE_JOB1
    NODE_MATRIX --> NODE_JOB2
```

The CI workflow uses GitHub Actions matrix strategy to validate all four projects in parallel ([.github/workflows/ci.yml:14-17]() and [.github/workflows/ci.yml:62-64]()). The `fail-fast: false` configuration ([.github/workflows/ci.yml:13](), [.github/workflows/ci.yml:60]()) ensures all projects are validated even if one fails, providing comprehensive feedback.

**Sources:** [.github/workflows/ci.yml:12-17](), [.github/workflows/ci.yml:59-64]()

## Version Constraints

Development dependencies use caret (`^`) version constraints, allowing automatic minor and patch updates:

- `typescript@^5`: Accepts versions 5.x.x
- `eslint@^9`: Accepts versions 9.x.x  
- `tailwindcss@^4`: Accepts versions 4.x.x

The exception is `eslint-config-next@15.5.4` ([package.json:28]()), which uses an exact version to match the Next.js core dependency version ([package.json:13]()), ensuring compatibility between Next.js and its ESLint configuration.

Type definition packages use caret constraints matching their corresponding runtime library versions.

**Sources:** [package.json:21-31]()

---

# Page: CI/CD Pipeline

# CI/CD Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yml](.github/workflows/ci.yml)

</details>



## Purpose and Scope

This document describes the automated CI/CD pipeline implemented using GitHub Actions that validates code quality across all four projects in the repository. The pipeline runs on every push to `main` and on all pull requests, executing parallel validation jobs for both Python backends and Node.js frontends.

For information about local development workflows and running these tools manually, see [Development Workflow](#7). For details on the specific dependencies being validated, see [Dependencies & Package Management](#5).

---

## Overview

The CI/CD pipeline is defined in [.github/workflows/ci.yml:1-88]() and implements a comprehensive validation strategy that ensures code quality standards are maintained across both integration patterns (self-hosted and managed ChatKit).

The pipeline consists of two independent job types that run in parallel:

| Job Type | Projects Validated | Primary Tools |
|----------|-------------------|---------------|
| `python` | `chatkit/backend`, `managed-chatkit/backend` | compileall, ruff, mypy |
| `node` | `chatkit/frontend`, `managed-chatkit/frontend` | ESLint, npm build |

**Key Design Decisions:**

- **Matrix Strategy**: Each job uses a matrix to validate multiple projects in parallel [.github/workflows/ci.yml:12-17]() and [.github/workflows/ci.yml:59-64]()
- **fail-fast: false**: Both jobs are configured with `fail-fast: false` [.github/workflows/ci.yml:13]() and [.github/workflows/ci.yml:60](), ensuring all projects are validated even if one fails
- **Consistent Tooling**: Both backend projects undergo identical validation steps; both frontend projects undergo identical validation steps

### CI/CD Pipeline Architecture

```mermaid
graph TB
    subgraph Triggers["Trigger Events"]
        PUSH["push to main branch"]
        PR["pull_request"]
    end
    
    subgraph PythonJobs["python job (matrix)"]
        CHATKIT_BE["chatkit/backend"]
        MANAGED_BE["managed-chatkit/backend"]
    end
    
    subgraph NodeJobs["node job (matrix)"]
        CHATKIT_FE["chatkit/frontend"]
        MANAGED_FE["managed-chatkit/frontend"]
    end
    
    subgraph PythonSteps["Python Validation Steps"]
        SETUP_PY["Setup Python 3.13"]
        INSTALL_PY["pip install .[dev] + mypy"]
        SYNTAX["python -m compileall app"]
        RUFF_LINT["python -m ruff check app"]
        RUFF_FMT["python -m ruff format --check app"]
        MYPY["python -m mypy app"]
    end
    
    subgraph NodeSteps["Node.js Validation Steps"]
        SETUP_NODE["Setup Node.js 22"]
        NPM_CI["npm ci"]
        ESLINT["npm run lint"]
        BUILD["npm run build"]
    end
    
    PUSH --> PythonJobs
    PUSH --> NodeJobs
    PR --> PythonJobs
    PR --> NodeJobs
    
    CHATKIT_BE --> PythonSteps
    MANAGED_BE --> PythonSteps
    
    CHATKIT_FE --> NodeSteps
    MANAGED_FE --> NodeSteps
    
    SETUP_PY --> INSTALL_PY --> SYNTAX --> RUFF_LINT --> RUFF_FMT --> MYPY
    SETUP_NODE --> NPM_CI --> ESLINT --> BUILD
```

**Sources:** [.github/workflows/ci.yml:1-88]()

---

## Workflow Configuration

The CI workflow is triggered by two events defined in [.github/workflows/ci.yml:3-6]():

```yaml
on:
  push:
    branches: [ main ]
  pull_request:
```

This configuration ensures that:
- All commits pushed to the `main` branch are validated
- All pull requests are validated regardless of target branch

### Matrix Strategy

Both the `python` and `node` jobs utilize GitHub Actions matrix strategy to validate multiple projects in parallel:

**Python Job Matrix** [.github/workflows/ci.yml:12-17]():
```yaml
strategy:
  fail-fast: false
  matrix:
    project:
      - chatkit/backend
      - managed-chatkit/backend
```

**Node Job Matrix** [.github/workflows/ci.yml:59-64]():
```yaml
strategy:
  fail-fast: false
  matrix:
    project:
      - managed-chatkit/frontend
      - chatkit/frontend
```

The `fail-fast: false` configuration is critical: it ensures that all matrix combinations complete even if one fails, providing comprehensive feedback on all projects in a single CI run.

### Parallel Execution Model

```mermaid
graph LR
    subgraph GitHubActions["GitHub Actions Runner"]
        WORKFLOW["ci.yml workflow"]
    end
    
    subgraph PythonMatrix["Python Job Matrix"]
        PY1["chatkit/backend<br/>Ubuntu runner"]
        PY2["managed-chatkit/backend<br/>Ubuntu runner"]
    end
    
    subgraph NodeMatrix["Node Job Matrix"]
        NODE1["managed-chatkit/frontend<br/>Ubuntu runner"]
        NODE2["chatkit/frontend<br/>Ubuntu runner"]
    end
    
    WORKFLOW --> PythonMatrix
    WORKFLOW --> NodeMatrix
    
    PY1 -.->|"Independent execution"| PY2
    NODE1 -.->|"Independent execution"| NODE2
    PythonMatrix -.->|"Parallel jobs"| NodeMatrix
```

All four projects are validated independently on separate `ubuntu-latest` runners [.github/workflows/ci.yml:11]() and [.github/workflows/ci.yml:58](), maximizing parallelization and minimizing total CI execution time.

**Sources:** [.github/workflows/ci.yml:3-17](), [.github/workflows/ci.yml:56-64]()

---

## Python Quality Checks

The Python validation pipeline implements a four-stage quality gate for both backend projects. Each project is validated in its own working directory using the `working-directory` configuration [.github/workflows/ci.yml:28]().

### Environment Setup

**Step 1: Checkout Repository** [.github/workflows/ci.yml:19-20]()
```yaml
- name: Checkout
  uses: actions/checkout@v4
```

**Step 2: Setup Python** [.github/workflows/ci.yml:22-25]()
```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: "3.13"
```

Python 3.13 is used in CI, which is compatible with the project's minimum requirement of Python 3.11+.

**Step 3: Install Dependencies** [.github/workflows/ci.yml:27-34]()
```yaml
- name: Install dependencies (${{ matrix.project }})
  working-directory: ${{ matrix.project }}
  env:
    PIP_DISABLE_PIP_VERSION_CHECK: "1"
  run: |
    python -m pip install --upgrade pip
    python -m pip install ".[dev]"
    python -m pip install mypy
```

This step:
- Upgrades `pip` to the latest version
- Installs the project in editable mode with development dependencies using `.[dev]`
- Explicitly installs `mypy` for type checking

### Validation Stages

#### Stage 1: Syntax Check

**Command** [.github/workflows/ci.yml:36-38]():
```bash
python -m compileall app
```

The `compileall` module verifies that all Python files in the `app` directory compile without syntax errors. This is the fastest check and catches basic Python syntax violations before proceeding to more expensive analysis.

#### Stage 2: Ruff Lint

**Command** [.github/workflows/ci.yml:40-42]():
```bash
python -m ruff check app
```

Ruff performs linting analysis to identify code quality issues, potential bugs, and style violations. The tool checks against a comprehensive ruleset configured in each project's `pyproject.toml`.

#### Stage 3: Ruff Format Check

**Command** [.github/workflows/ci.yml:44-50]():
```bash
python -m ruff format --check app || {
  echo "::error ::Ruff format check failed. Run 'python -m ruff format app' locally to apply formatting.";
  exit 1;
}
```

The `--check` flag verifies code formatting without modifying files. If formatting issues are detected, the job fails with a helpful error message instructing developers how to fix the issues locally.

#### Stage 4: Type Checking with mypy

**Command** [.github/workflows/ci.yml:52-54]():
```bash
python -m mypy app --ignore-missing-imports
```

The final validation stage runs static type analysis using `mypy`. The `--ignore-missing-imports` flag allows the check to proceed even when type stubs for third-party libraries are unavailable.

### Python Validation Pipeline Flow

```mermaid
flowchart TD
    START["Python job triggered<br/>(chatkit/backend or managed-chatkit/backend)"]
    CHECKOUT["actions/checkout@v4"]
    SETUP["actions/setup-python@v5<br/>Python 3.13"]
    INSTALL["pip install --upgrade pip<br/>pip install .[dev]<br/>pip install mypy"]
    
    COMPILEALL["python -m compileall app"]
    COMPILEALL_FAIL["❌ Syntax Error"]
    
    RUFF_CHECK["python -m ruff check app"]
    RUFF_CHECK_FAIL["❌ Linting Error"]
    
    RUFF_FORMAT["python -m ruff format --check app"]
    RUFF_FORMAT_FAIL["❌ Formatting Error<br/>Run 'ruff format app' locally"]
    
    MYPY["python -m mypy app --ignore-missing-imports"]
    MYPY_FAIL["❌ Type Error"]
    
    SUCCESS["✅ All checks passed"]
    
    START --> CHECKOUT --> SETUP --> INSTALL --> COMPILEALL
    COMPILEALL -->|"Syntax OK"| RUFF_CHECK
    COMPILEALL -->|"Syntax Error"| COMPILEALL_FAIL
    
    RUFF_CHECK -->|"Lint OK"| RUFF_FORMAT
    RUFF_CHECK -->|"Lint Error"| RUFF_CHECK_FAIL
    
    RUFF_FORMAT -->|"Format OK"| MYPY
    RUFF_FORMAT -->|"Format Error"| RUFF_FORMAT_FAIL
    
    MYPY -->|"Types OK"| SUCCESS
    MYPY -->|"Type Error"| MYPY_FAIL
```

**Sources:** [.github/workflows/ci.yml:8-54]()

---

## Node.js Quality Checks

The Node.js validation pipeline implements a three-stage quality gate for both frontend projects, verifying dependency installation, linting compliance, and successful build execution.

### Environment Setup

**Step 1: Checkout Repository** [.github/workflows/ci.yml:67-68]()
```yaml
- name: Checkout repository
  uses: actions/checkout@v4
```

**Step 2: Setup Node.js** [.github/workflows/ci.yml:70-75]()
```yaml
- name: Setup Node.js
  uses: actions/setup-node@v4
  with:
    node-version: 22
    cache-dependency-path: ${{ matrix.project }}/package-lock.json
    cache: "npm"
```

This step:
- Installs Node.js version 22 to match the project requirements
- Configures npm caching using the project-specific `package-lock.json` path
- Caches the global npm cache directory to accelerate subsequent runs

### Validation Stages

#### Stage 1: Install Dependencies

**Command** [.github/workflows/ci.yml:77-79]():
```bash
npm ci
```

The `npm ci` (clean install) command:
- Installs dependencies from `package-lock.json` exactly as specified
- Removes `node_modules` if it exists to ensure a clean state
- Is faster and more reliable than `npm install` in CI environments

#### Stage 2: ESLint

**Command** [.github/workflows/ci.yml:81-83]():
```bash
npm run lint
```

This command executes the `lint` script defined in each frontend's `package.json`, which runs ESLint to enforce code style and identify potential issues in TypeScript/JavaScript files.

#### Stage 3: Build Verification

**Command** [.github/workflows/ci.yml:85-87]():
```bash
npm run build
```

The final stage executes the production build process using Vite. This ensures:
- All TypeScript files compile without errors
- All imports resolve correctly
- The application can be successfully bundled for deployment

### Node.js Validation Pipeline Flow

```mermaid
flowchart TD
    START["Node job triggered<br/>(chatkit/frontend or managed-chatkit/frontend)"]
    CHECKOUT["actions/checkout@v4"]
    SETUP["actions/setup-node@v4<br/>Node.js 22<br/>npm cache enabled"]
    
    NPM_CI["npm ci<br/>(clean install from package-lock.json)"]
    NPM_CI_FAIL["❌ Dependency Installation Failed"]
    
    LINT["npm run lint<br/>(ESLint)"]
    LINT_FAIL["❌ Linting Error"]
    
    BUILD["npm run build<br/>(Vite production build)"]
    BUILD_FAIL["❌ Build Failed"]
    
    SUCCESS["✅ All checks passed"]
    
    START --> CHECKOUT --> SETUP --> NPM_CI
    NPM_CI -->|"Install OK"| LINT
    NPM_CI -->|"Install Error"| NPM_CI_FAIL
    
    LINT -->|"Lint OK"| BUILD
    LINT -->|"Lint Error"| LINT_FAIL
    
    BUILD -->|"Build OK"| SUCCESS
    BUILD -->|"Build Error"| BUILD_FAIL
```

**Sources:** [.github/workflows/ci.yml:56-88]()

---

## Summary

The CI/CD pipeline provides comprehensive validation coverage through:

| Validation Type | Projects | Tools | Purpose |
|----------------|----------|-------|---------|
| Python Quality | `chatkit/backend`, `managed-chatkit/backend` | compileall, ruff, mypy | Syntax validation, linting, formatting, type checking |
| Node.js Quality | `chatkit/frontend`, `managed-chatkit/frontend` | ESLint, Vite | Code style enforcement, build verification |

The pipeline executes automatically on all pushes to `main` and on all pull requests, with a `fail-fast: false` configuration ensuring comprehensive feedback across all four projects. This design enables rapid iteration while maintaining code quality standards across both self-hosted and managed integration patterns.

**Sources:** [.github/workflows/ci.yml:1-88]()

---

# Page: Workflow Configuration

# Workflow Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yml](.github/workflows/ci.yml)

</details>



## Purpose and Scope

This document describes the GitHub Actions CI workflow configuration defined in [.github/workflows/ci.yml:1-88](). The workflow automates code quality checks and build validation for all four projects in the repository (two Python backends and two Node.js frontends) using a parallel execution strategy. This page focuses on the workflow structure, job matrix configuration, and parallel execution model.

## Workflow Overview

The CI workflow defines two independent jobs (`python` and `node`) that execute in parallel. Each job uses a matrix strategy to run multiple project validations concurrently, resulting in four total job executions per workflow run.

**Diagram: Workflow Structure and Parallel Execution**

```mermaid
graph TB
    subgraph Triggers["Workflow Triggers"]
        PUSH["push to main"]
        PR["pull_request"]
    end
    
    subgraph PythonJob["Job: python (Matrix)"]
        PY1["Python checks<br/>chatkit/backend"]
        PY2["Python checks<br/>managed-chatkit/backend"]
    end
    
    subgraph NodeJob["Job: node (Matrix)"]
        NODE1["Node checks<br/>chatkit/frontend"]
        NODE2["Node checks<br/>managed-chatkit/frontend"]
    end
    
    PUSH --> PythonJob
    PUSH --> NodeJob
    PR --> PythonJob
    PR --> NodeJob
    
    PY1 -.->|"fail-fast: false"| PY2
    NODE1 -.->|"fail-fast: false"| NODE2
```

**Sources:** [.github/workflows/ci.yml:1-88]()
</thinking>

## Workflow Triggers

The workflow is triggered by two event types, configured in [.github/workflows/ci.yml:3-7]():

| Trigger | Configuration | Purpose |
|---------|--------------|---------|
| `push` | `branches: [ main ]` | Validates all commits pushed directly to the main branch |
| `pull_request` | No branch filter | Validates all pull requests regardless of target branch |

The `push` trigger is branch-restricted to `main` to avoid redundant runs on feature branches (which are already validated via pull requests). The `pull_request` trigger has no branch filter, meaning it runs for PRs targeting any branch.

**Sources:** [.github/workflows/ci.yml:3-7]()

## Workflow Triggers

The workflow is triggered by two event types, configured in [.github/workflows/ci.yml:3-6]():

| Trigger | Configuration | Purpose |
|---------|--------------|---------|
| `push` | `branches: [ main ]` | Validates all commits pushed directly to the main branch |
| `pull_request` | No branch filter | Validates all pull requests regardless of target branch |

The `push` trigger is branch-restricted to `main` to avoid redundant runs on feature branches (which are already validated via pull requests). The `pull_request` trigger has no branch filter, meaning it runs for PRs targeting any branch.

**Sources:** [.github/workflows/ci.yml:3-6]()

## Job Structure and Matrix Strategy

The workflow defines two jobs: `python` and `node`. Each job uses a matrix strategy to execute across multiple projects, with `fail-fast: false` ensuring all matrix combinations run even if one fails.

### Python Job Configuration

The `python` job is defined at [.github/workflows/ci.yml:9-54]() with the following structure:

| Property | Value | Description |
|----------|-------|-------------|
| Job ID | `python` | Internal identifier for the job |
| `name` | `Python checks (${{ matrix.project }})` | Dynamic name including the current matrix project |
| `runs-on` | `ubuntu-latest` | Ubuntu Linux execution environment |
| `strategy.fail-fast` | `false` | Continue running other matrix jobs even if one fails |
| `strategy.matrix.project` | `["chatkit/backend", "managed-chatkit/backend"]` | Project paths to validate |

### Node Job Configuration

The `node` job is defined at [.github/workflows/ci.yml:56-88]() with the following structure:

| Property | Value | Description |
|----------|-------|-------------|
| Job ID | `node` | Internal identifier for the job |
| `name` | `Node checks (${{ matrix.project }})` | Dynamic name including the current matrix project |
| `runs-on` | `ubuntu-latest` | Ubuntu Linux execution environment |
| `strategy.fail-fast` | `false` | Continue running other matrix jobs even if one fails |
| `strategy.matrix.project` | `["managed-chatkit/frontend", "chatkit/frontend"]` | Project paths to validate |

**Sources:** [.github/workflows/ci.yml:9-88]()

## Matrix Execution Strategy

The `fail-fast: false` configuration at [.github/workflows/ci.yml:12]() and [.github/workflows/ci.yml:59]() is critical for comprehensive validation. This setting ensures that if one project fails validation, the other projects continue to run, providing complete feedback on all validation failures in a single workflow run.

**Diagram: Matrix Expansion and Parallel Execution**

```mermaid
graph TB
    subgraph MatrixExpansion["Matrix Expansion"]
        PYTHON_MATRIX["python job<br/>matrix.project:<br/>- chatkit/backend<br/>- managed-chatkit/backend"]
        NODE_MATRIX["node job<br/>matrix.project:<br/>- managed-chatkit/frontend<br/>- chatkit/frontend"]
    end
    
    subgraph ActualJobs["Actual Job Executions (Parallel)"]
        PY_CK["python<br/>(chatkit/backend)"]
        PY_MCK["python<br/>(managed-chatkit/backend)"]
        NODE_MCK["node<br/>(managed-chatkit/frontend)"]
        NODE_CK["node<br/>(chatkit/frontend)"]
    end
    
    PYTHON_MATRIX --> PY_CK
    PYTHON_MATRIX --> PY_MCK
    NODE_MATRIX --> NODE_MCK
    NODE_MATRIX --> NODE_CK
    
    PY_CK -.->|"fail-fast: false"| PY_MCK
    NODE_MCK -.->|"fail-fast: false"| NODE_CK
```

Each matrix combination creates an independent job execution with its own runner, environment, and isolated filesystem. The jobs run in parallel subject to GitHub Actions runner availability.

**Sources:** [.github/workflows/ci.yml:9-88]()

## Python Job Steps

The `python` job executes six steps sequentially for each matrix project. All steps use `working-directory: ${{ matrix.project }}` to operate within the project-specific directory.

**Diagram: Python Job Step Flow**

```mermaid
graph TB
    START["Start Python Job"]
    
    CHECKOUT["Checkout<br/>actions/checkout@v4"]
    SETUP["Set up Python<br/>actions/setup-python@v5<br/>python-version: 3.13"]
    INSTALL["Install dependencies<br/>pip install .[dev]<br/>pip install mypy"]
    SYNTAX["Syntax check<br/>python -m compileall app"]
    LINT["Ruff lint<br/>python -m ruff check app"]
    FORMAT["Ruff format check<br/>python -m ruff format --check app"]
    MYPY["mypy<br/>python -m mypy app --ignore-missing-imports"]
    
    SUCCESS["Job Success"]
    FAIL["Job Failure"]
    
    START --> CHECKOUT
    CHECKOUT --> SETUP
    SETUP --> INSTALL
    INSTALL --> SYNTAX
    SYNTAX --> LINT
    LINT --> FORMAT
    FORMAT --> MYPY
    MYPY --> SUCCESS
    
    SYNTAX -.->|"Syntax error"| FAIL
    LINT -.->|"Lint error"| FAIL
    FORMAT -.->|"Format error"| FAIL
    MYPY -.->|"Type error"| FAIL
```

### Step 1: Checkout

[.github/workflows/ci.yml:19-20]() - Uses `actions/checkout@v4` to clone the repository to the runner workspace.

### Step 2: Set up Python

[.github/workflows/ci.yml:22-25]() - Uses `actions/setup-python@v5` to install Python 3.13.

### Step 3: Install Dependencies

[.github/workflows/ci.yml:27-34]() - Installs project dependencies within the matrix project directory:

```bash
python -m pip install --upgrade pip
python -m pip install ".[dev]"
python -m pip install mypy
```

The `PIP_DISABLE_PIP_VERSION_CHECK: "1"` environment variable suppresses pip version check warnings to keep logs clean.

### Step 4: Syntax Check

[.github/workflows/ci.yml:36-38]() - Runs `python -m compileall app` to verify Python syntax without executing code.

### Step 5: Ruff Lint

[.github/workflows/ci.yml:40-42]() - Runs `python -m ruff check app` to validate code style and detect common errors.

### Step 6: Ruff Format Check

[.github/workflows/ci.yml:44-50]() - Runs `python -m ruff format --check app` to verify code formatting. On failure, outputs an error message instructing developers to run the formatter locally.

### Step 7: mypy Type Check

[.github/workflows/ci.yml:52-54]() - Runs `python -m mypy app --ignore-missing-imports` to perform static type checking.

**Sources:** [.github/workflows/ci.yml:18-54]()

## Node Job Steps

The `node` job executes five steps sequentially for each matrix project. All steps use `working-directory: ${{ matrix.project }}` to operate within the project-specific directory.

**Diagram: Node Job Step Flow**

```mermaid
graph TB
    START["Start Node Job"]
    
    CHECKOUT["Checkout repository<br/>actions/checkout@v4"]
    SETUP["Setup Node.js<br/>actions/setup-node@v4<br/>node-version: 22<br/>cache-dependency-path: matrix.project/package-lock.json"]
    INSTALL["Install dependencies<br/>npm ci"]
    LINT["Run ESLint<br/>npm run lint"]
    BUILD["Run build<br/>npm run build"]
    
    SUCCESS["Job Success"]
    FAIL["Job Failure"]
    
    START --> CHECKOUT
    CHECKOUT --> SETUP
    SETUP --> INSTALL
    INSTALL --> LINT
    LINT --> BUILD
    BUILD --> SUCCESS
    
    INSTALL -.->|"Install error"| FAIL
    LINT -.->|"Lint error"| FAIL
    BUILD -.->|"Build error"| FAIL
```

### Step 1: Checkout Repository

[.github/workflows/ci.yml:67-68]() - Uses `actions/checkout@v4` to clone the repository to the runner workspace.

### Step 2: Setup Node.js

[.github/workflows/ci.yml:70-75]() - Uses `actions/setup-node@v4` with project-specific caching:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `node-version` | `22` | Installs Node.js version 22 |
| `cache-dependency-path` | `${{ matrix.project }}/package-lock.json` | Specifies the lock file path for cache key computation |
| `cache` | `"npm"` | Enables npm dependency caching |

The `cache-dependency-path` parameter is essential for matrix jobs because it ensures the cache key is computed from the correct project's `package-lock.json` file, not a monorepo root file.

### Step 3: Install Dependencies

[.github/workflows/ci.yml:77-79]() - Runs `npm ci` within the project directory to install exact dependency versions from `package-lock.json`.

### Step 4: Run ESLint

[.github/workflows/ci.yml:81-83]() - Executes `npm run lint` to validate code style and TypeScript correctness.

### Step 5: Run Build

[.github/workflows/ci.yml:85-87]() - Executes `npm run build` to compile TypeScript and bundle the application, verifying that the project builds successfully.

**Sources:** [.github/workflows/ci.yml:66-87]()

## Workflow Success Criteria

A workflow run succeeds only when all four matrix job executions complete successfully. The workflow fails if any job fails, but the `fail-fast: false` setting ensures all jobs run to completion regardless of failures in other jobs.

**Diagram: Workflow Status Aggregation**

```mermaid
graph TB
    subgraph Jobs["Job Executions"]
        PY_CK["python<br/>(chatkit/backend)"]
        PY_MCK["python<br/>(managed-chatkit/backend)"]
        NODE_CK["node<br/>(chatkit/frontend)"]
        NODE_MCK["node<br/>(managed-chatkit/frontend)"]
    end
    
    AGGREGATE["Aggregate Results"]
    
    SUCCESS["Workflow Success<br/>All jobs passed"]
    FAIL["Workflow Failure<br/>One or more jobs failed"]
    
    PY_CK --> AGGREGATE
    PY_MCK --> AGGREGATE
    NODE_CK --> AGGREGATE
    NODE_MCK --> AGGREGATE
    
    AGGREGATE -->|"All success"| SUCCESS
    AGGREGATE -->|"Any failure"| FAIL
```

This aggregation model provides comprehensive feedback while allowing all validations to complete, making it easier to fix multiple issues in a single iteration.

**Sources:** [.github/workflows/ci.yml:1-88]()

## Working Directory Configuration

Each step in the matrix jobs uses `working-directory: ${{ matrix.project }}` to operate within the project-specific directory. This configuration appears in:

- Python job: [.github/workflows/ci.yml:28,37,41,45,53]()
- Node job: [.github/workflows/ci.yml:78,82,86]()

The `${{ matrix.project }}` variable resolves to:
- `chatkit/backend`
- `managed-chatkit/backend`
- `chatkit/frontend`
- `managed-chatkit/frontend`

This approach allows the same step definitions to execute across different projects without code duplication.

**Sources:** [.github/workflows/ci.yml:28-86]()

## Runner Environment

Both jobs use `runs-on: ubuntu-latest` runners, which provide:

| Software | Purpose in Workflow |
|----------|---------------------|
| Git 2.x | Used by `actions/checkout@v4` to clone repository |
| Python runtime | Base Python installation, replaced by `actions/setup-python@v5` |
| Node.js runtime | Base Node.js installation, replaced by `actions/setup-node@v4` |
| Build tools (gcc, make) | Used by native npm dependencies during installation |
| pip | Python package manager for installing dependencies |
| npm | Node.js package manager for installing dependencies |

The runner provides approximately 14 GB of RAM and 2-core CPU, sufficient for building both Python and Node.js applications.

**Sources:** [.github/workflows/ci.yml:11,58]()

## Configuration File Structure

The complete workflow configuration follows GitHub Actions YAML syntax with matrix job definitions:

**Diagram: YAML Configuration Hierarchy**

```mermaid
graph TD
    ROOT["ci.yml"]
    
    NAME["name: CI"]
    ON["on:<br/>trigger configuration"]
    JOBS["jobs:<br/>job definitions"]
    
    PUSH["push:<br/>branches: [main]"]
    PR["pull_request"]
    
    PYTHON_JOB["python:<br/>Python validation"]
    NODE_JOB["node:<br/>Node.js validation"]
    
    PY_STRATEGY["strategy:<br/>fail-fast: false<br/>matrix.project: [...]"]
    PY_STEPS["steps:<br/>7 steps"]
    
    NODE_STRATEGY["strategy:<br/>fail-fast: false<br/>matrix.project: [...]"]
    NODE_STEPS["steps:<br/>5 steps"]
    
    ROOT --> NAME
    ROOT --> ON
    ROOT --> JOBS
    
    ON --> PUSH
    ON --> PR
    
    JOBS --> PYTHON_JOB
    JOBS --> NODE_JOB
    
    PYTHON_JOB --> PY_STRATEGY
    PYTHON_JOB --> PY_STEPS
    
    NODE_JOB --> NODE_STRATEGY
    NODE_JOB --> NODE_STEPS
```

The workflow file is located at [.github/workflows/ci.yml:1-88]() and follows the standard GitHub Actions directory structure where workflows must reside in `.github/workflows/` to be recognized by GitHub.

**Sources:** [.github/workflows/ci.yml:1-88]()

## Workflow Execution Time

The typical execution time for each step (approximate, based on cache availability):

| Step | Uncached Time | Cached Time |
|------|---------------|-------------|
| Checkout repository | 2-5 seconds | 2-5 seconds |
| Setup Node.js | 10-15 seconds | 3-5 seconds |
| Install dependencies | 30-60 seconds | 10-20 seconds |
| Run ESLint | 3-5 seconds | 3-5 seconds |
| Run build | 20-40 seconds | 20-40 seconds |
| **Total** | **~65-125 seconds** | **~38-75 seconds** |

The npm cache provides the most significant time savings by eliminating package downloads from the npm registry. The Node.js version cache provides minor improvements by avoiding the download and extraction of the Node.js binary.

**Sources:** [.github/workflows/ci.yml:17-30]()

---

# Page: Python Quality Checks

# Python Quality Checks

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yml](.github/workflows/ci.yml)

</details>



## Purpose and Scope

This document details the automated Python quality validation pipeline executed in the CI/CD workflow for both backend projects (`chatkit/backend` and `managed-chatkit/backend`). The pipeline runs four sequential checks to ensure code quality, style consistency, and type safety.

For information about the overall CI/CD workflow structure and job matrix configuration, see [Workflow Configuration](#6.1). For Node.js quality validation, see [Node.js Quality Checks](#6.3). For local development usage of these tools, see [Code Quality & Linting](#7.2).

**Sources:** [.github/workflows/ci.yml:9-54]()

---

## Pipeline Overview

The Python quality checks execute as a GitHub Actions job named `python` with a matrix strategy covering both backend projects. Each check must pass before proceeding to the next step, ensuring comprehensive validation.

### Sequential Validation Pipeline

```mermaid
graph TD
    Setup["Setup<br/>Python 3.13<br/>Install dependencies"]
    Syntax["Step 1: Syntax Check<br/>python -m compileall app"]
    Lint["Step 2: Ruff Lint<br/>python -m ruff check app"]
    Format["Step 3: Ruff Format<br/>python -m ruff format --check app"]
    Type["Step 4: Type Check<br/>python -m mypy app --ignore-missing-imports"]
    Success["✓ All Checks Passed"]
    Failure["✗ Pipeline Failed"]
    
    Setup --> Syntax
    Syntax -->|Pass| Lint
    Syntax -->|Fail| Failure
    Lint -->|Pass| Format
    Lint -->|Fail| Failure
    Format -->|Pass| Type
    Format -->|Fail| Failure
    Type -->|Pass| Success
    Type -->|Fail| Failure
```

**Sources:** [.github/workflows/ci.yml:36-54]()

---

## Project Matrix Configuration

The `python` job uses a matrix strategy to validate both backend projects in parallel while maintaining independent failure reporting:

| Configuration Key | Value |
|-------------------|-------|
| Job Name | `Python checks (${{ matrix.project }})` |
| Strategy | `fail-fast: false` |
| Matrix Projects | `chatkit/backend`, `managed-chatkit/backend` |
| Python Version | `3.13` |
| Runner | `ubuntu-latest` |

The `fail-fast: false` setting ensures that if one project fails validation, the other project continues executing its checks, providing comprehensive feedback across all projects.

**Sources:** [.github/workflows/ci.yml:9-25]()

---

## Step 1: Syntax Check

The first validation step uses Python's built-in `compileall` module to verify syntactic correctness of all Python source files in the `app` directory.

### Command Execution

```bash
python -m compileall app
```

### Validation Behavior

The `compileall` module:
- Recursively compiles all `.py` files in the `app` directory to bytecode
- Validates Python syntax without executing code
- Reports compilation errors with file path and line number
- Returns non-zero exit code if any file fails to compile

This check catches basic syntax errors such as:
- Indentation errors
- Invalid Python keywords
- Unclosed brackets, parentheses, or quotes
- Invalid token sequences

**Sources:** [.github/workflows/ci.yml:36-38]()

---

## Step 2: Ruff Lint

The second validation step runs Ruff's linting engine to enforce code quality rules and detect common programming errors.

### Command Execution

```bash
python -m ruff check app
```

### Linting Scope

Ruff performs static analysis on the `app` directory to identify:
- Unused imports and variables
- Undefined names
- Import order violations
- Code complexity issues
- Security vulnerabilities (e.g., hardcoded secrets)
- PEP 8 style violations
- Best practice violations

### Tool Characteristics

| Attribute | Details |
|-----------|---------|
| Implementation | Written in Rust for performance |
| Speed | 10-100x faster than traditional Python linters |
| Rule Sets | Compatible with Flake8, pycodestyle, isort, and others |
| Configuration | Defined in `pyproject.toml` or `ruff.toml` |

**Sources:** [.github/workflows/ci.yml:40-42]()

---

## Step 3: Ruff Format Check

The third validation step verifies code formatting consistency using Ruff's formatting engine in check-only mode.

### Command Execution

```bash
python -m ruff format --check app || {
  echo "::error ::Ruff format check failed. Run 'python -m ruff format app' locally to apply formatting.";
  exit 1;
}
```

### Check-Only Mode Behavior

The `--check` flag enables validation mode where Ruff:
- Analyzes code formatting without modifying files
- Compares current formatting against expected formatting
- Returns exit code 1 if formatting differences detected
- Outputs helpful error message directing developers to fix command

### Formatting Standards

```mermaid
graph LR
    Source["app/*.py<br/>Source Files"]
    Ruff["ruff format --check"]
    Compare["Compare Against<br/>Expected Format"]
    Pass["✓ Formatting<br/>Consistent"]
    Fail["✗ Formatting<br/>Inconsistent"]
    
    Source --> Ruff
    Ruff --> Compare
    Compare -->|No Differences| Pass
    Compare -->|Differences Found| Fail
    
    Fail -.->|Error Message| Fix["Run: python -m ruff format app"]
```

The error output includes GitHub Actions annotation syntax (`::error ::`) to highlight formatting failures in the Actions UI.

**Sources:** [.github/workflows/ci.yml:44-50]()

---

## Step 4: Type Check with mypy

The final validation step uses mypy to perform static type checking, ensuring type safety and catching type-related errors before runtime.

### Command Execution

```bash
python -m mypy app --ignore-missing-imports
```

### Type Checking Configuration

| Flag | Purpose |
|------|---------|
| `--ignore-missing-imports` | Suppresses errors for third-party libraries without type stubs |
| Working Directory | `${{ matrix.project }}` (e.g., `chatkit/backend`) |
| Target Directory | `app` (relative to working directory) |

### Validation Coverage

mypy analyzes:
- Function parameter types
- Return value types
- Variable type annotations
- Type compatibility in assignments
- Generic type usage
- Optional type handling

The `--ignore-missing-imports` flag prevents failures when validating code that imports libraries lacking type stubs, focusing validation on the application code itself rather than third-party dependencies.

**Sources:** [.github/workflows/ci.yml:52-54]()

---

## Dependency Installation

Before executing quality checks, the workflow installs all necessary dependencies using pip.

### Installation Commands

```bash
python -m pip install --upgrade pip
python -m pip install ".[dev]"
python -m pip install mypy
```

### Installation Flow

```mermaid
graph TD
    Upgrade["Upgrade pip"]
    DevDeps["Install Development Dependencies<br/>pip install '.[dev]'"]
    Mypy["Install mypy<br/>pip install mypy"]
    Ready["Dependencies Ready"]
    
    Upgrade --> DevDeps
    DevDeps --> Mypy
    Mypy --> Ready
    
    DevDeps -.->|Installs| Ruff["ruff<br/>(linter & formatter)"]
    DevDeps -.->|Installs| FastAPI["FastAPI<br/>(framework)"]
    DevDeps -.->|Installs| Uvicorn["uvicorn<br/>(ASGI server)"]
    DevDeps -.->|Installs| ChatKit["openai-chatkit<br/>(SDK)"]
```

The `.[dev]` syntax installs the package in editable mode along with development dependencies defined in the `[project.optional-dependencies]` section of `pyproject.toml`. mypy is installed separately as it may not be included in all project configurations.

**Sources:** [.github/workflows/ci.yml:27-34]()

---

## Execution Environment

### Environment Variables

| Variable | Value | Purpose |
|----------|-------|---------|
| `PIP_DISABLE_PIP_VERSION_CHECK` | `"1"` | Suppresses pip version warnings in CI output |

### Working Directory Context

Each quality check executes within the matrix project's working directory:

```mermaid
graph LR
    Root["Repository Root"]
    ChatKit["chatkit/backend/"]
    Managed["managed-chatkit/backend/"]
    AppDir1["app/"]
    AppDir2["app/"]
    
    Root --> ChatKit
    Root --> Managed
    ChatKit --> AppDir1
    Managed --> AppDir2
    
    AppDir1 -.->|Target| Checks1["Quality Checks"]
    AppDir2 -.->|Target| Checks2["Quality Checks"]
```

The `working-directory: ${{ matrix.project }}` directive ensures all commands execute in the correct project context, allowing relative path references like `app` to resolve properly.

**Sources:** [.github/workflows/ci.yml:28-54]()

---

## Quality Check Summary

The following table summarizes the purpose and validation scope of each quality check:

| Step | Tool | Primary Purpose | Secondary Purpose | Exit Code on Failure |
|------|------|-----------------|-------------------|---------------------|
| 1 | `compileall` | Syntax validation | Catch compilation errors | Non-zero |
| 2 | `ruff check` | Linting | Code quality & style enforcement | Non-zero |
| 3 | `ruff format --check` | Format validation | Ensure consistent formatting | 1 |
| 4 | `mypy` | Type checking | Static type safety validation | Non-zero |

Each check must pass (exit code 0) for the overall pipeline to succeed. The sequential execution ensures that basic syntax errors are caught before running more sophisticated analysis tools.

**Sources:** [.github/workflows/ci.yml:36-54]()

---

# Page: Node.js Quality Checks

# Node.js Quality Checks

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yml](.github/workflows/ci.yml)

</details>



This document details the automated Node.js quality validation pipeline executed by GitHub Actions for both frontend projects in the repository. The pipeline ensures code quality and build integrity through linting and build verification.

For information about the overall CI/CD workflow structure and triggers, see [Workflow Configuration](#6.1). For Python validation steps, see [Python Quality Checks](#6.2).

---

## Overview

The Node.js quality checks job validates both frontend projects (`chatkit/frontend` and `managed-chatkit/frontend`) in parallel. Each project undergoes three validation stages: dependency installation, ESLint linting, and production build verification. The job runs on every push to the `main` branch and on all pull requests.

**Sources:** [.github/workflows/ci.yml:56-87]()

---

## Job Configuration

The `node` job executes quality checks for frontend projects using a matrix strategy that processes both projects in parallel.

### Job Matrix

| Property | Value |
|----------|-------|
| **Job Name** | `node` |
| **Display Name** | `Node checks (${{ matrix.project }})` |
| **Runner** | `ubuntu-latest` |
| **Fail-fast** | `false` (all projects run even if one fails) |
| **Matrix Projects** | `managed-chatkit/frontend`, `chatkit/frontend` |

The `fail-fast: false` configuration ensures comprehensive feedback by running checks on all projects regardless of individual failures.

**Sources:** [.github/workflows/ci.yml:56-65]()

---

## CI Node.js Validation Pipeline

```mermaid
graph TB
    Trigger["GitHub Actions Trigger<br/>(push/PR)"]
    
    subgraph NodeJob["node job"]
        Matrix{"Matrix Strategy<br/>fail-fast: false"}
        
        subgraph Project1["managed-chatkit/frontend"]
            P1_Checkout["Checkout<br/>actions/checkout@v4"]
            P1_Setup["Setup Node.js 22<br/>actions/setup-node@v4"]
            P1_Install["npm ci"]
            P1_Lint["npm run lint<br/>(ESLint)"]
            P1_Build["npm run build"]
            
            P1_Checkout --> P1_Setup
            P1_Setup --> P1_Install
            P1_Install --> P1_Lint
            P1_Lint --> P1_Build
        end
        
        subgraph Project2["chatkit/frontend"]
            P2_Checkout["Checkout<br/>actions/checkout@v4"]
            P2_Setup["Setup Node.js 22<br/>actions/setup-node@v4"]
            P2_Install["npm ci"]
            P2_Lint["npm run lint<br/>(ESLint)"]
            P2_Build["npm run build"]
            
            P2_Checkout --> P2_Setup
            P2_Setup --> P2_Install
            P2_Install --> P2_Lint
            P2_Lint --> P2_Build
        end
    end
    
    Trigger --> Matrix
    Matrix --> Project1
    Matrix --> Project2
    
    P1_Build --> Success["CI Success"]
    P2_Build --> Success
```

**Diagram: Complete Node.js validation pipeline showing parallel execution for both frontend projects**

**Sources:** [.github/workflows/ci.yml:56-87]()

---

## Validation Steps

### Step 1: Repository Checkout

The first step checks out the repository code using GitHub's official checkout action.

```yaml
- name: Checkout repository
  uses: actions/checkout@v4
```

This step provides access to all project files required for subsequent validation steps.

**Sources:** [.github/workflows/ci.yml:67-68]()

---

### Step 2: Node.js Environment Setup

The pipeline sets up Node.js version 22 with npm caching enabled for faster subsequent runs.

```yaml
- name: Setup Node.js
  uses: actions/setup-node@v4
  with:
    node-version: 22
    cache-dependency-path: ${{ matrix.project }}/package-lock.json
    cache: "npm"
```

#### Configuration Details

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `node-version` | `22` | Matches local development requirement |
| `cache-dependency-path` | `${{ matrix.project }}/package-lock.json` | Project-specific lockfile for cache key |
| `cache` | `"npm"` | Enables npm dependency caching |

The `cache-dependency-path` parameter uses the matrix variable to reference each project's specific `package-lock.json` file, ensuring accurate cache invalidation when dependencies change.

**Sources:** [.github/workflows/ci.yml:70-76]()

---

### Step 3: Dependency Installation

Dependencies are installed using `npm ci`, which provides reproducible builds from `package-lock.json`.

```yaml
- name: Install dependencies
  working-directory: ${{ matrix.project }}
  run: npm ci
```

#### npm ci vs npm install

The pipeline uses `npm ci` instead of `npm install` for several reasons:

| `npm ci` | `npm install` |
|----------|---------------|
| Installs exact versions from lockfile | May update dependencies |
| Fails if lockfile and package.json are out of sync | Attempts to reconcile differences |
| Removes `node_modules` before installation | Incrementally updates existing modules |
| Faster for CI environments | Optimized for development |

**Sources:** [.github/workflows/ci.yml:77-79]()

---

### Step 4: ESLint Code Quality

The pipeline executes ESLint to validate code quality, style consistency, and potential errors.

```yaml
- name: Run ESLint
  working-directory: ${{ matrix.project }}
  run: npm run lint
```

This step invokes the `lint` script defined in each project's `package.json`, which typically runs ESLint with project-specific configuration. ESLint validates:

- Code style consistency
- Potential runtime errors
- React-specific best practices
- TypeScript type usage patterns

If ESLint detects violations, the step fails and provides detailed error messages indicating the file, line number, and rule violation.

**Sources:** [.github/workflows/ci.yml:81-83]()

---

### Step 5: Production Build Verification

The final validation step verifies that the project can be built successfully for production deployment.

```yaml
- name: Run build
  working-directory: ${{ matrix.project }}
  run: npm run build
```

This step executes Vite's production build process, which:

1. Compiles TypeScript to JavaScript
2. Bundles all modules and dependencies
3. Optimizes assets (minification, tree-shaking)
4. Validates import/export resolution
5. Generates production-ready static assets

Build failures indicate issues such as:
- Type errors in TypeScript code
- Missing or incorrect imports
- Invalid JSX syntax
- Configuration errors in Vite or build tooling

**Sources:** [.github/workflows/ci.yml:85-87]()

---

## Validation Flow Sequence

```mermaid
sequenceDiagram
    participant GHA as GitHub Actions
    participant Runner as Ubuntu Runner
    participant Cache as npm Cache
    participant Project as Frontend Project
    participant ESLint as ESLint Tool
    participant Vite as Vite Build
    
    GHA->>Runner: Start node job for project
    Runner->>Runner: Checkout code
    Runner->>Cache: Check npm cache key
    
    alt Cache Hit
        Cache-->>Runner: Restore node_modules
    else Cache Miss
        Runner->>Project: npm ci
        Project-->>Runner: Install dependencies
        Runner->>Cache: Cache node_modules
    end
    
    Runner->>ESLint: npm run lint
    ESLint->>Project: Parse source files
    ESLint->>Project: Apply ESLint rules
    
    alt Lint Passed
        ESLint-->>Runner: Success
    else Lint Failed
        ESLint-->>Runner: Exit 1 with errors
        Runner->>GHA: Job Failed
    end
    
    Runner->>Vite: npm run build
    Vite->>Project: Compile TypeScript
    Vite->>Project: Bundle modules
    Vite->>Project: Optimize assets
    
    alt Build Passed
        Vite-->>Runner: Generate dist/
        Runner->>GHA: Job Success
    else Build Failed
        Vite-->>Runner: Exit 1 with errors
        Runner->>GHA: Job Failed
    end
```

**Diagram: Complete execution sequence for a single frontend project validation**

**Sources:** [.github/workflows/ci.yml:56-87]()

---

## Code Entity Mapping

The following table maps conceptual validation stages to specific code entities in the CI workflow:

| Concept | Code Entity | Location |
|---------|-------------|----------|
| Node validation job | `jobs.node` | [.github/workflows/ci.yml:56]() |
| Job display name | `Node checks (${{ matrix.project }})` | [.github/workflows/ci.yml:57]() |
| Project matrix | `matrix.project` | [.github/workflows/ci.yml:62-64]() |
| managed frontend path | `managed-chatkit/frontend` | [.github/workflows/ci.yml:63]() |
| chatkit frontend path | `chatkit/frontend` | [.github/workflows/ci.yml:64]() |
| Checkout step | `uses: actions/checkout@v4` | [.github/workflows/ci.yml:68]() |
| Node setup step | `uses: actions/setup-node@v4` | [.github/workflows/ci.yml:71]() |
| Node version | `node-version: 22` | [.github/workflows/ci.yml:73]() |
| Cache configuration | `cache: "npm"` | [.github/workflows/ci.yml:75]() |
| Dependency install | `npm ci` | [.github/workflows/ci.yml:79]() |
| Lint command | `npm run lint` | [.github/workflows/ci.yml:83]() |
| Build command | `npm run build` | [.github/workflows/ci.yml:87]() |

**Sources:** [.github/workflows/ci.yml:56-87]()

---

## Working Directory Context

All Node.js validation steps execute within the context of the specific frontend project directory specified by the matrix variable.

```mermaid
graph LR
    Root["Repository Root"]
    
    subgraph ManagedProject["managed-chatkit/frontend/"]
        MCK_Package["package.json"]
        MCK_Lock["package-lock.json"]
        MCK_Source["src/"]
        MCK_Config[".eslintrc.json<br/>vite.config.ts"]
    end
    
    subgraph ChatkitProject["chatkit/frontend/"]
        CK_Package["package.json"]
        CK_Lock["package-lock.json"]
        CK_Source["src/"]
        CK_Config[".eslintrc.json<br/>vite.config.ts"]
    end
    
    Root --> ManagedProject
    Root --> ChatkitProject
    
    ManagedProject -.->|working-directory| CI_Steps["CI Steps:<br/>npm ci<br/>npm run lint<br/>npm run build"]
    ChatkitProject -.->|working-directory| CI_Steps
```

**Diagram: Working directory context for Node.js validation steps showing project-specific file access**

The `working-directory` parameter in each step ensures commands execute within the correct project context:

```yaml
working-directory: ${{ matrix.project }}
```

This parameter resolves to either `managed-chatkit/frontend` or `chatkit/frontend` depending on the matrix iteration.

**Sources:** [.github/workflows/ci.yml:78,82,86]()

---

## Failure Modes and Error Handling

The Node.js quality checks can fail at multiple stages, each providing specific diagnostic information:

### Failure Scenarios

| Stage | Failure Condition | Typical Causes |
|-------|-------------------|----------------|
| **Checkout** | Cannot access repository | Repository permissions, network issues |
| **Node Setup** | Cannot install Node.js | Invalid version specification, cache corruption |
| **npm ci** | Dependency installation fails | Missing packages, lockfile conflicts, network errors |
| **ESLint** | Linting rules violated | Code style violations, unused variables, type issues |
| **Build** | Build process fails | TypeScript errors, missing imports, configuration errors |

### Non-Blocking Failures

The `fail-fast: false` configuration ensures that failure in one project does not prevent validation of the other project. This provides comprehensive feedback on all frontend projects in a single CI run.

```yaml
strategy:
  fail-fast: false
  matrix:
    project:
      - managed-chatkit/frontend
      - chatkit/frontend
```

**Sources:** [.github/workflows/ci.yml:59-64]()

---

## Integration with Development Workflow

The Node.js quality checks enforce the same standards developers should follow locally before committing code. For local development practices, see [Code Quality & Linting](#7.2).

### Relationship to Local Development

| CI Step | Local Equivalent | Purpose Alignment |
|---------|-----------------|-------------------|
| `npm ci` | `npm install` | Dependency consistency |
| `npm run lint` | `npm run lint` | Code quality enforcement |
| `npm run build` | `npm run build` | Production readiness verification |

Developers should run `npm run lint` and `npm run build` locally before pushing to ensure CI passes.

**Sources:** [.github/workflows/ci.yml:77-87]()

---

# Page: Development Workflow

# Development Workflow

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [chatkit/.env.example](chatkit/.env.example)
- [chatkit/.gitignore](chatkit/.gitignore)
- [chatkit/README.md](chatkit/README.md)
- [chatkit/backend/.gitignore](chatkit/backend/.gitignore)
- [chatkit/backend/app/__init__.py](chatkit/backend/app/__init__.py)
- [chatkit/backend/scripts/run.sh](chatkit/backend/scripts/run.sh)

</details>



This document describes the standard development workflow for both the self-hosted and managed ChatKit starter applications. It covers local environment setup, concurrent server execution, code quality tools, and pre-commit validation procedures. For production deployment considerations, see [Deployment Considerations](#8). For detailed CI/CD pipeline documentation, see [CI/CD Pipeline](#6).

## Overview

Both `chatkit/` and `managed-chatkit/` applications follow identical development workflows. Each application consists of two components that run concurrently:

1. **FastAPI backend** - Runs on `http://127.0.0.1:8000`
2. **Vite frontend** - Runs on `http://127.0.0.1:3000` with `/chatkit` proxy

The root-level `package.json` orchestrates both processes using `npm run dev`, which executes backend and frontend start scripts in parallel.

**Sources:** [chatkit/README.md:1-33]()

---

## Local Development Setup

### Prerequisites

| Component | Required Version | Verification Command |
|-----------|-----------------|---------------------|
| Python | 3.11 or higher | `python --version` |
| Node.js | 22 | `node --version` |
| npm | Latest | `npm --version` |

**Sources:** [.github/workflows/ci.yml:24-25](), [.github/workflows/ci.yml:72-73]()

### Environment Variables

Create a `.env.local` file in the repository root with the following variables:

| Variable | Required | Default Value | Description |
|----------|----------|---------------|-------------|
| `OPENAI_API_KEY` | Yes | N/A | OpenAI API key for backend authentication |
| `VITE_CHATKIT_API_URL` | No | `/chatkit` | Frontend API endpoint URL |
| `VITE_CHATKIT_API_DOMAIN_KEY` | No | `domain_pk_localhost_dev` | Domain key for ChatKit authentication |

Example configuration:

```
OPENAI_API_KEY=sk-proj-...
VITE_CHATKIT_API_URL=http://127.0.0.1:8000/chatkit
VITE_CHATKIT_API_DOMAIN_KEY=domain_pk_local_dev
```

The backend startup script [chatkit/backend/scripts/run.sh:24-31]() automatically sources environment variables from `.env.local` if `OPENAI_API_KEY` is not already set in the shell environment.

**Sources:** [chatkit/.env.example:1-3](), [chatkit/README.md:18-26](), [chatkit/backend/scripts/run.sh:24-36]()

### Virtual Environment Setup

The Python backend requires a virtual environment for dependency isolation. The backend startup script [chatkit/backend/scripts/run.sh:12-15]() automatically creates a `.venv` directory if it does not exist:

```bash
if [ ! -d ".venv" ]; then
  echo "Creating virtual env in $PROJECT_ROOT/.venv ..."
  python -m venv .venv
fi
```

Manual virtual environment setup:

```bash
cd chatkit/backend  # or managed-chatkit/backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

The `.venv/` directory is excluded from version control via [chatkit/backend/.gitignore:4]().

**Sources:** [chatkit/backend/scripts/run.sh:12-20](), [chatkit/backend/.gitignore:4]()

### Installing Dependencies

#### Unified Installation (Recommended)

From the `chatkit/` or `managed-chatkit/` directory:

```bash
npm install
```

This command installs both frontend dependencies and Python backend dependencies through the package scripts.

#### Backend Dependencies Only

From the `chatkit/backend/` or `managed-chatkit/backend/` directory:

```bash
pip install -e .
```

This installs the backend package in editable mode, including all dependencies from `pyproject.toml`.

#### Frontend Dependencies Only

From the `chatkit/frontend/` or `managed-chatkit/frontend/` directory:

```bash
npm ci
```

The `npm ci` command performs a clean install from `package-lock.json`, ensuring reproducible builds.

**Sources:** [chatkit/README.md:8-10](), [.github/workflows/ci.yml:27-34](), [.github/workflows/ci.yml:77-79]()

### Starting the Development Servers

#### Concurrent Server Execution

From the `chatkit/` or `managed-chatkit/` directory:

```bash
npm run dev
```

This command starts both the FastAPI backend and Vite frontend concurrently. The backend listens on `127.0.0.1:8000` and the frontend listens on `127.0.0.1:3000` with a proxy configured at `/chatkit` that forwards requests to the backend.

**Sources:** [chatkit/README.md:8-16]()

#### Backend Only

Execute the backend startup script:

```bash
cd chatkit/backend
./scripts/run.sh
```

This script [chatkit/backend/scripts/run.sh:1-40]() performs the following operations:

1. Creates virtual environment if missing
2. Activates virtual environment
3. Installs dependencies in editable mode
4. Sources `OPENAI_API_KEY` from `.env.local` if not set
5. Starts uvicorn server with `--reload` flag for hot reloading

Alternatively, start uvicorn directly from within the virtual environment:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Sources:** [chatkit/backend/scripts/run.sh:1-40]()

#### Frontend Only

From the `chatkit/frontend/` or `managed-chatkit/frontend/` directory:

```bash
npm run dev
```

This starts the Vite development server with hot module replacement enabled.

**Sources:** [chatkit/README.md:8-16]()

### Development Workflow Diagram

```mermaid
graph TB
    subgraph Developer["Developer Workstation"]
        DEV_EDIT["Edit Code"]
        DEV_TEST["Test Locally"]
        DEV_COMMIT["Commit Changes"]
    end
    
    subgraph Local_Setup["Local Development Environment"]
        INSTALL["npm install<br/>(Root Directory)"]
        ENV_FILE[".env.local<br/>OPENAI_API_KEY<br/>VITE_* variables"]
        VENV[".venv/<br/>Python Virtual Environment"]
    end
    
    subgraph Concurrent_Servers["Concurrent Server Execution"]
        NPM_DEV["npm run dev"]
        BACKEND_SCRIPT["backend/scripts/run.sh"]
        UVICORN["uvicorn app.main:app<br/>127.0.0.1:8000"]
        VITE_DEV["vite dev server<br/>127.0.0.1:3000"]
    end
    
    subgraph Quality_Tools["Code Quality Tools"]
        RUFF_LINT["ruff check app"]
        RUFF_FMT["ruff format app"]
        MYPY["mypy app"]
        ESLINT["npm run lint"]
    end
    
    DEV_EDIT --> DEV_TEST
    INSTALL --> ENV_FILE
    INSTALL --> VENV
    ENV_FILE --> NPM_DEV
    VENV --> NPM_DEV
    NPM_DEV --> BACKEND_SCRIPT
    NPM_DEV --> VITE_DEV
    BACKEND_SCRIPT --> UVICORN
    DEV_TEST --> Quality_Tools
    Quality_Tools --> DEV_COMMIT
```

**Sources:** [chatkit/README.md:8-16](), [chatkit/backend/scripts/run.sh:1-40](), [.github/workflows/ci.yml:36-54](), [.github/workflows/ci.yml:81-87]()

---

## Code Quality & Linting

All code changes must pass automated quality checks before merging. The CI pipeline [.github/workflows/ci.yml:1-88]() enforces these checks on every push and pull request.

### Python Quality Tools

The backend uses three primary quality tools, all executed in the [.github/workflows/ci.yml:36-54]() CI pipeline:

#### Ruff Linter

Ruff checks for common Python errors, code style violations, and potential bugs:

```bash
python -m ruff check app
```

The linter runs against the `app/` directory in both `chatkit/backend/` and `managed-chatkit/backend/`. Configuration is managed through `pyproject.toml` in each backend directory.

**CI Step:** [.github/workflows/ci.yml:40-42]()

#### Ruff Formatter

Ruff enforces consistent code formatting:

```bash
python -m ruff format --check app
```

The `--check` flag validates formatting without modifying files. To apply formatting locally:

```bash
python -m ruff format app
```

The CI pipeline [.github/workflows/ci.yml:44-50]() fails with an explicit error message if formatting violations are detected, instructing developers to run the format command locally.

**CI Step:** [.github/workflows/ci.yml:44-50]()

#### Mypy Type Checker

Mypy validates static type annotations:

```bash
python -m mypy app --ignore-missing-imports
```

The `--ignore-missing-imports` flag allows mypy to skip untyped third-party dependencies while still validating project code.

**CI Step:** [.github/workflows/ci.yml:52-54]()

### JavaScript Quality Tools

The frontend uses ESLint for code quality and style enforcement:

```bash
npm run lint
```

This command executes ESLint against the frontend source code. The CI pipeline [.github/workflows/ci.yml:81-83]() validates both `chatkit/frontend/` and `managed-chatkit/frontend/`.

**CI Step:** [.github/workflows/ci.yml:81-83]()

### Build Verification

The CI pipeline also verifies that both frontends build successfully:

```bash
npm run build
```

This ensures that production builds will succeed before code is merged.

**CI Step:** [.github/workflows/ci.yml:85-87]()

### Pre-Commit Workflow

Before committing code, developers should run all quality checks locally:

#### Python Backend

```bash
cd chatkit/backend  # or managed-chatkit/backend
source .venv/bin/activate

# Syntax check
python -m compileall app

# Lint
python -m ruff check app

# Format
python -m ruff format app

# Type check
python -m mypy app --ignore-missing-imports
```

#### JavaScript Frontend

```bash
cd chatkit/frontend  # or managed-chatkit/frontend

# Lint
npm run lint

# Build verification
npm run build
```

**Sources:** [.github/workflows/ci.yml:36-54](), [.github/workflows/ci.yml:81-87]()

### Quality Tools Installation

Quality tools are installed as development dependencies:

#### Python

```bash
pip install -e ".[dev]"  # Installs ruff
pip install mypy
```

The `[dev]` extra includes development dependencies defined in `pyproject.toml`.

**CI Installation:** [.github/workflows/ci.yml:27-34]()

#### JavaScript

```bash
npm ci
```

This installs all dependencies including ESLint, which is configured in `package.json` and `eslint.config.js`.

**CI Installation:** [.github/workflows/ci.yml:77-79]()

### Code Quality Workflow Diagram

```mermaid
graph LR
    subgraph Local_Checks["Local Quality Checks"]
        SYNTAX["python -m compileall app"]
        LINT["ruff check app"]
        FORMAT["ruff format app"]
        TYPE["mypy app"]
        JS_LINT["npm run lint"]
        BUILD["npm run build"]
    end
    
    subgraph Git_Actions["Version Control"]
        COMMIT["git commit"]
        PUSH["git push"]
        PR["Pull Request"]
    end
    
    subgraph CI_Pipeline[".github/workflows/ci.yml"]
        CI_TRIGGER["Workflow Trigger"]
        CI_PYTHON["Python Job Matrix<br/>chatkit/backend<br/>managed-chatkit/backend"]
        CI_NODE["Node Job Matrix<br/>chatkit/frontend<br/>managed-chatkit/frontend"]
        CI_SYNTAX["Syntax Check"]
        CI_RUFF_LINT["Ruff Lint"]
        CI_RUFF_FMT["Ruff Format Check"]
        CI_MYPY["mypy Type Check"]
        CI_ESLINT["ESLint"]
        CI_BUILD["Build Verification"]
        CI_SUCCESS["✓ All Checks Pass"]
    end
    
    SYNTAX --> LINT
    LINT --> FORMAT
    FORMAT --> TYPE
    TYPE --> COMMIT
    JS_LINT --> BUILD
    BUILD --> COMMIT
    COMMIT --> PUSH
    PUSH --> PR
    PR --> CI_TRIGGER
    CI_TRIGGER --> CI_PYTHON
    CI_TRIGGER --> CI_NODE
    CI_PYTHON --> CI_SYNTAX
    CI_SYNTAX --> CI_RUFF_LINT
    CI_RUFF_LINT --> CI_RUFF_FMT
    CI_RUFF_FMT --> CI_MYPY
    CI_NODE --> CI_ESLINT
    CI_ESLINT --> CI_BUILD
    CI_MYPY --> CI_SUCCESS
    CI_BUILD --> CI_SUCCESS
```

**Sources:** [.github/workflows/ci.yml:1-88]()

---

## Common Development Commands

| Task | Command | Working Directory |
|------|---------|------------------|
| Start both servers | `npm run dev` | `chatkit/` or `managed-chatkit/` |
| Install all dependencies | `npm install` | `chatkit/` or `managed-chatkit/` |
| Backend only (script) | `./scripts/run.sh` | `chatkit/backend/` or `managed-chatkit/backend/` |
| Backend only (direct) | `uvicorn app.main:app --reload` | `chatkit/backend/` or `managed-chatkit/backend/` (in venv) |
| Frontend only | `npm run dev` | `chatkit/frontend/` or `managed-chatkit/frontend/` |
| Lint Python | `ruff check app` | `chatkit/backend/` or `managed-chatkit/backend/` (in venv) |
| Format Python | `ruff format app` | `chatkit/backend/` or `managed-chatkit/backend/` (in venv) |
| Type check Python | `mypy app --ignore-missing-imports` | `chatkit/backend/` or `managed-chatkit/backend/` (in venv) |
| Lint JavaScript | `npm run lint` | `chatkit/frontend/` or `managed-chatkit/frontend/` |
| Build frontend | `npm run build` | `chatkit/frontend/` or `managed-chatkit/frontend/` |

**Sources:** [chatkit/README.md:8-10](), [chatkit/backend/scripts/run.sh:39](), [.github/workflows/ci.yml:36-87]()

---

## File Artifacts & Cache Directories

The development workflow generates several artifacts and cache directories that should not be committed to version control:

### Python Backend Artifacts

Excluded via [chatkit/backend/.gitignore:1-9]():

| Pattern | Description |
|---------|-------------|
| `__pycache__/` | Compiled Python bytecode cache |
| `*.py[cod]` | Compiled Python files (`.pyc`, `.pyo`, `.pyd`) |
| `*.egg-info/` | Package metadata from editable installs |
| `.venv/` | Python virtual environment |
| `.env` | Local environment variables (security risk) |
| `.ruff_cache/` | Ruff linter cache |
| `.pytest_cache/` | Pytest cache directory |
| `.coverage/` | Code coverage data |
| `*.log` | Log files |

### Root-Level Artifacts

Excluded via [chatkit/.gitignore:1-3]():

| Pattern | Description |
|---------|-------------|
| `node_modules/` | npm dependencies |
| `.env*` | All environment files (except `.env.example`) |

The pattern `.env*` matches `.env`, `.env.local`, `.env.production`, etc., while `!.env.example` explicitly allows the example file to be committed.

**Sources:** [chatkit/backend/.gitignore:1-9](), [chatkit/.gitignore:1-3]()

---

## CI/CD Integration

The GitHub Actions workflow [.github/workflows/ci.yml:1-88]() runs automatically on:

- Pushes to the `main` branch [.github/workflows/ci.yml:4-5]()
- All pull requests [.github/workflows/ci.yml:6]()

### Parallel Job Execution

The CI pipeline uses job matrices to validate all four projects in parallel:

**Python Projects** [.github/workflows/ci.yml:14-17]():
- `chatkit/backend`
- `managed-chatkit/backend`

**Node.js Projects** [.github/workflows/ci.yml:61-64]():
- `chatkit/frontend`
- `managed-chatkit/frontend`

The `fail-fast: false` configuration [.github/workflows/ci.yml:13]() ensures that all projects are validated even if one fails, providing comprehensive feedback to developers.

### CI Environment

| Component | Version | Configuration |
|-----------|---------|---------------|
| Operating System | Ubuntu Latest | `runs-on: ubuntu-latest` |
| Python | 3.13 | [.github/workflows/ci.yml:24-25]() |
| Node.js | 22 | [.github/workflows/ci.yml:72-73]() |
| Package Cache | Enabled | `cache: "npm"` for Node.js [.github/workflows/ci.yml:75]() |

### CI Dependency Installation

The CI pipeline uses `PIP_DISABLE_PIP_VERSION_CHECK: "1"` [.github/workflows/ci.yml:30]() to suppress pip version warnings during dependency installation.

For detailed CI/CD pipeline documentation, see [CI/CD Pipeline](#6).

**Sources:** [.github/workflows/ci.yml:1-88]()

---

## Troubleshooting Common Issues

### Backend Fails to Start

**Symptom:** `OPENAI_API_KEY` not found error

**Solution:** Ensure `.env.local` exists in the repository root with a valid `OPENAI_API_KEY`:

```bash
echo "OPENAI_API_KEY=sk-proj-..." > .env.local
```

Alternatively, export the variable in your shell:

```bash
export OPENAI_API_KEY=sk-proj-...
```

**Source:** [chatkit/backend/scripts/run.sh:33-36]()

### Ruff Format Check Fails in CI

**Symptom:** CI pipeline fails with "Ruff format check failed"

**Solution:** Run the formatter locally and commit the changes:

```bash
cd chatkit/backend  # or managed-chatkit/backend
python -m ruff format app
git add app
git commit -m "Apply ruff formatting"
```

**Source:** [.github/workflows/ci.yml:46-50]()

### Port Already in Use

**Symptom:** Backend or frontend fails to start due to port conflict

**Solution:** Kill the existing process using the port:

```bash
# Find process using port 8000 (backend)
lsof -ti:8000 | xargs kill -9

# Find process using port 3000 (frontend)
lsof -ti:3000 | xargs kill -9
```

Alternatively, modify the port configuration in the startup scripts or `npm run dev` command.

### Virtual Environment Not Activated

**Symptom:** `ModuleNotFoundError` when running backend commands

**Solution:** Activate the virtual environment before running Python commands:

```bash
cd chatkit/backend  # or managed-chatkit/backend
source .venv/bin/activate
```

The backend startup script [chatkit/backend/scripts/run.sh:17]() automatically activates the virtual environment.

**Sources:** [chatkit/backend/scripts/run.sh:17]()

---

# Page: Local Development Setup

# Local Development Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [chatkit/.env.example](chatkit/.env.example)
- [chatkit/.gitignore](chatkit/.gitignore)
- [chatkit/README.md](chatkit/README.md)
- [chatkit/backend/.gitignore](chatkit/backend/.gitignore)
- [chatkit/backend/app/__init__.py](chatkit/backend/app/__init__.py)
- [chatkit/backend/scripts/run.sh](chatkit/backend/scripts/run.sh)

</details>



This page provides step-by-step instructions for setting up a local development environment for either the `chatkit/` or `managed-chatkit/` starter applications. It covers virtual environment creation, dependency installation, environment variable configuration, and running development servers concurrently.

For information about code quality tools and linting workflows, see [Code Quality & Linting](#7.2). For environment variable details and configuration options, see [Environment Configuration](#2.2). For production deployment considerations, see [Deployment Considerations](#8).

---

## Prerequisites

Before beginning local development setup, ensure the following software is installed on your system:

| Software | Required Version | Purpose |
|----------|-----------------|---------|
| Python | 3.11 or higher | Backend runtime environment |
| Node.js | 22.x | Frontend build toolchain and package management |
| pip | Latest | Python package installer |
| npm | Bundled with Node.js | Node package manager |

For detailed installation instructions, see [Installation & Prerequisites](#2.1).

**Sources:** [chatkit/README.md:1-33]()

---

## Development Environment Architecture

The local development environment consists of two concurrent server processes and a file-based configuration system:

```mermaid
graph TB
    subgraph Repository["Repository Root"]
        ENV_LOCAL[".env.local<br/>(Environment Variables)"]
        PACKAGE_JSON["package.json<br/>(Root Scripts)"]
    end
    
    subgraph Backend["Backend: chatkit/backend/"]
        VENV[".venv/<br/>(Virtual Environment)"]
        RUN_SH["scripts/run.sh<br/>(Startup Script)"]
        MAIN_PY["app/main.py<br/>(FastAPI Application)"]
        UVICORN["uvicorn Server<br/>127.0.0.1:8000"]
    end
    
    subgraph Frontend["Frontend: chatkit/frontend/"]
        NODE_MODULES["node_modules/<br/>(Dependencies)"]
        VITE_CONFIG["vite.config.ts<br/>(Build Configuration)"]
        VITE_SERVER["Vite Dev Server<br/>127.0.0.1:3000"]
    end
    
    PACKAGE_JSON -->|"npm run dev"| RUN_SH
    PACKAGE_JSON -->|"npm run dev"| VITE_SERVER
    ENV_LOCAL -.->|"Loads OPENAI_API_KEY"| RUN_SH
    RUN_SH -->|"Creates if missing"| VENV
    RUN_SH -->|"pip install -e ."| VENV
    RUN_SH -->|"exec uvicorn"| UVICORN
    UVICORN -->|"Serves"| MAIN_PY
    VITE_CONFIG -->|"Proxy /chatkit"| UVICORN
    VITE_SERVER -->|"Reads"| VITE_CONFIG
```

**Sources:** [chatkit/README.md:13-16](), [chatkit/backend/scripts/run.sh:1-40]()

---

## Python Virtual Environment Setup

The backend requires a Python virtual environment to isolate dependencies. The virtual environment is automatically created by the startup script if it does not already exist.

### Automatic Creation

When running `npm run dev`, the backend startup script [chatkit/backend/scripts/run.sh:12-15]() automatically creates a virtual environment at `chatkit/backend/.venv/`:

```bash
if [ ! -d ".venv" ]; then
  echo "Creating virtual env in $PROJECT_ROOT/.venv ..."
  python -m venv .venv
fi
```

### Manual Creation

To manually create a virtual environment for the backend:

```bash
cd chatkit/backend
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# .venv\Scripts\activate   # On Windows
```

The virtual environment directory `.venv/` is excluded from version control via [chatkit/backend/.gitignore:4]().

**Sources:** [chatkit/backend/scripts/run.sh:12-17](), [chatkit/backend/.gitignore:4]()

---

## Dependency Installation

### Backend Dependencies

Backend dependencies are installed automatically by the startup script using pip in editable mode. The script [chatkit/backend/scripts/run.sh:19-20]() executes:

```bash
pip install -e . >/dev/null
```

This installs the package defined in the backend's `pyproject.toml` along with all dependencies specified in the `[project.dependencies]` section. Editable mode (`-e`) allows code changes to take effect without reinstallation.

For manual installation:

```bash
cd chatkit/backend
source .venv/bin/activate
pip install -e .
```

### Frontend Dependencies

Frontend dependencies must be installed manually before first run. From the repository root:

```bash
npm install
```

This installs all packages defined in the root `package.json` and workspace configurations. Node modules are stored in `node_modules/` directories, which are excluded from version control via [chatkit/.gitignore:1]().

**Sources:** [chatkit/README.md:8-10](), [chatkit/backend/scripts/run.sh:19-20](), [chatkit/.gitignore:1]()

---

## Environment Variable Configuration

Local development requires environment variables for API authentication and service configuration. These should be stored in `.env.local` at the repository root.

### Required Variables

| Variable | Required By | Purpose | Default Value |
|----------|-------------|---------|---------------|
| `OPENAI_API_KEY` | Backend | OpenAI API authentication | None (must be set) |
| `VITE_CHATKIT_API_URL` | Frontend | Backend endpoint URL | `/chatkit` |
| `VITE_CHATKIT_API_DOMAIN_KEY` | Frontend | Domain authentication key | `domain_pk_localhost_dev` |

### Configuration File Location

Create `.env.local` at the repository root (same level as `chatkit/` and `managed-chatkit/` directories):

```
.
├── .env.local          # Environment variables file
├── chatkit/
│   ├── backend/
│   └── frontend/
└── managed-chatkit/
```

### Example Configuration

An example configuration is provided in [chatkit/.env.example:1-3]():

```bash
OPENAI_API_KEY=sk-proj-...
VITE_CHATKIT_API_URL=http://127.0.0.1:8000/chatkit
VITE_CHATKIT_API_DOMAIN_KEY=domain_pk_local_dev
```

### Variable Loading Mechanism

The backend startup script automatically loads environment variables from `.env.local` if `OPENAI_API_KEY` is not already set in the shell environment [chatkit/backend/scripts/run.sh:22-31]():

```bash
ENV_FILE="$PROJECT_ROOT/../.env.local"
if [ -z "${OPENAI_API_KEY:-}" ] && [ -f "$ENV_FILE" ]; then
  echo "Sourcing OPENAI_API_KEY from $ENV_FILE"
  set -a
  . "$ENV_FILE"
  set +a
fi
```

If `OPENAI_API_KEY` is not found, the script exits with an error [chatkit/backend/scripts/run.sh:33-36]().

**Sources:** [chatkit/README.md:18-26](), [chatkit/.env.example:1-3](), [chatkit/backend/scripts/run.sh:22-36]()

---

## Running Development Servers

### Concurrent Server Startup

The primary method for local development is the `npm run dev` command, which starts both backend and frontend servers concurrently.

From the repository root:

```bash
npm run dev
```

This command executes the root `package.json` scripts that launch:

1. **Backend**: FastAPI application via uvicorn on `127.0.0.1:8000`
2. **Frontend**: Vite development server on `127.0.0.1:3000`

The frontend is configured with a proxy at `/chatkit` that forwards requests to the backend [chatkit/README.md:15-16]().

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant NPM as npm run dev
    participant RunSH as scripts/run.sh
    participant Uvicorn as uvicorn Server
    participant Vite as Vite Server
    participant Browser as Browser

    Dev->>NPM: Execute command
    NPM->>RunSH: Start backend process
    NPM->>Vite: Start frontend process
    
    RunSH->>RunSH: Check/create .venv
    RunSH->>RunSH: pip install -e .
    RunSH->>RunSH: Load .env.local
    RunSH->>Uvicorn: exec uvicorn app.main:app
    
    Uvicorn-->>Dev: Backend ready on :8000
    Vite-->>Dev: Frontend ready on :3000
    
    Dev->>Browser: Navigate to localhost:3000
    Browser->>Vite: GET /
    Vite-->>Browser: Serve React app
    Browser->>Vite: POST /chatkit
    Vite->>Uvicorn: Proxy to :8000/chatkit
    Uvicorn-->>Vite: Response
    Vite-->>Browser: Forward response
```

**Sources:** [chatkit/README.md:8-16](), [chatkit/backend/scripts/run.sh:38-39]()

---

## Manual Server Startup

For debugging or isolated testing, backend and frontend servers can be started independently.

### Backend Only

Execute the startup script directly:

```bash
cd chatkit/backend
./scripts/run.sh
```

The script [chatkit/backend/scripts/run.sh:1-40]() performs the following operations:

1. Changes to the backend project root directory
2. Creates virtual environment if missing
3. Activates the virtual environment
4. Installs dependencies in editable mode
5. Loads environment variables from `../../.env.local`
6. Validates `OPENAI_API_KEY` presence
7. Starts uvicorn with `--reload` flag on `127.0.0.1:8000`

The `--reload` flag enables automatic server restart when code changes are detected.

### Frontend Only

Start the Vite development server:

```bash
cd chatkit/frontend
npm run dev
```

Ensure the backend is running separately, as the frontend depends on the backend API endpoint.

**Sources:** [chatkit/backend/scripts/run.sh:1-40]()

---

## Development File Structure

Understanding the file organization helps locate configuration and code during development:

```mermaid
graph TB
    subgraph Root["Repository Root"]
        ENV["(.env.local)<br/>Environment variables"]
        PKG["(package.json)<br/>Workspace scripts"]
    end
    
    subgraph Backend["chatkit/backend/"]
        VENV_DIR["(.venv/)<br/>Virtual environment<br/>AUTO-CREATED"]
        RUN_SCRIPT["(scripts/run.sh)<br/>Startup script"]
        APP_DIR["app/"]
        MAIN["app/main.py<br/>FastAPI entrypoint"]
        SERVER["app/server.py<br/>StarterChatServer"]
        PYPROJECT["pyproject.toml<br/>Dependencies"]
        GITIGNORE_BE["(.gitignore)<br/>Excludes .venv"]
    end
    
    subgraph Frontend["chatkit/frontend/"]
        NODE_DIR["(node_modules/)<br/>NPM packages<br/>AUTO-CREATED"]
        SRC["src/"]
        CONFIG["src/lib/config.ts<br/>Connection settings"]
        VITE_CFG["vite.config.ts<br/>Proxy config"]
        GITIGNORE_FE["(.gitignore)<br/>Excludes node_modules"]
    end
    
    ENV -.->|"Loaded by"| RUN_SCRIPT
    PKG -->|"Executes"| RUN_SCRIPT
    RUN_SCRIPT -->|"Creates"| VENV_DIR
    RUN_SCRIPT -->|"Starts"| MAIN
```

### Key Files for Local Development

| File Path | Purpose | Modified During Development |
|-----------|---------|----------------------------|
| `.env.local` | Environment variables | Rarely (only for API keys) |
| `chatkit/backend/.venv/` | Python virtual environment | Auto-managed |
| `chatkit/backend/scripts/run.sh` | Backend startup script | No |
| `chatkit/backend/app/main.py` | FastAPI application | Frequently |
| `chatkit/backend/app/server.py` | Chat server implementation | Frequently |
| `chatkit/frontend/src/` | React application source | Frequently |
| `chatkit/frontend/src/lib/config.ts` | Frontend configuration | Occasionally |
| `chatkit/frontend/vite.config.ts` | Build and proxy configuration | Rarely |

### Excluded Directories

The following directories are auto-generated and excluded from version control:

- `chatkit/backend/.venv/` - Python virtual environment [chatkit/backend/.gitignore:4]()
- `chatkit/backend/__pycache__/` - Python bytecode cache [chatkit/backend/.gitignore:1]()
- `chatkit/frontend/node_modules/` - NPM packages [chatkit/.gitignore:1]()
- `.env.local` and other `.env*` files (except `.env.example`) [chatkit/.gitignore:2-3]()

**Sources:** [chatkit/backend/.gitignore:1-10](), [chatkit/.gitignore:1-4](), [chatkit/backend/scripts/run.sh:7-10]()

---

## Development Server URLs

Once the development servers are running, the application can be accessed at the following URLs:

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | `http://127.0.0.1:3000` | React application UI |
| Backend API | `http://127.0.0.1:8000` | FastAPI endpoints |
| Backend Docs | `http://127.0.0.1:8000/docs` | Interactive API documentation |
| Proxied API | `http://127.0.0.1:3000/chatkit` | Frontend proxy to backend |

The frontend Vite server proxies requests to `/chatkit` through to the backend server, allowing the React application to communicate with the API without CORS issues during development [chatkit/README.md:15-16]().

**Sources:** [chatkit/README.md:15-16](), [chatkit/backend/scripts/run.sh:38]()

---

## Troubleshooting Common Setup Issues

### Missing OPENAI_API_KEY

If the backend fails to start with the error message:
```
Set OPENAI_API_KEY in your environment or in .env.local before running this script.
```

**Solution**: Create `.env.local` at the repository root and add your OpenAI API key [chatkit/backend/scripts/run.sh:33-36]().

### Virtual Environment Creation Fails

If Python virtual environment creation fails, ensure Python 3.11+ is installed and accessible via the `python` command.

**Solution**: Verify Python version with `python --version` and install Python 3.11+ if needed.

### Port Already in Use

If ports 8000 or 3000 are already in use, the servers will fail to start.

**Solution**: Stop existing processes using these ports, or modify the port configuration in [chatkit/backend/scripts/run.sh:39]() (backend) or frontend Vite configuration (frontend).

### npm install Fails

If frontend dependency installation fails, ensure Node.js 22.x is installed.

**Solution**: Verify Node.js version with `node --version` and install Node.js 22.x if needed.

**Sources:** [chatkit/backend/scripts/run.sh:33-39](), [chatkit/README.md:8-10]()

---

# Page: Code Quality & Linting

# Code Quality & Linting

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [chatkit/backend/pyproject.toml](chatkit/backend/pyproject.toml)

</details>



This page documents the code quality tools and linting mechanisms used across both Python and Node.js projects in the ChatKit starter applications. The repository maintains consistent code quality through language-specific tooling: **Ruff** and **mypy** for Python backend validation, and **ESLint** for TypeScript/React frontend validation.

For information about how these tools integrate into the CI/CD pipeline, see page 6 (CI/CD Pipeline).

---

## Overview

Both `chatkit/backend` and `managed-chatkit/backend` Python projects use the same quality toolchain, as do both frontend projects. The quality tools enforce:

| Language | Linting | Formatting | Type Checking |
|----------|---------|------------|---------------|
| Python | Ruff | Ruff | mypy |
| TypeScript/React | ESLint | ESLint (autofix) | TypeScript compiler |

**Sources:** [.github/workflows/ci.yml:36-54](), [chatkit/backend/pyproject.toml:14-16]()

---

## Python Quality Tools

The Python backend projects use modern tooling for fast, comprehensive code quality checks. All Python quality tools are specified in `pyproject.toml` and installed via the `[dev]` optional dependency group.

### Dependency Configuration

[chatkit/backend/pyproject.toml:13-16]() defines the development dependencies:

```toml
[project.optional-dependencies]
dev = [
    "ruff>=0.6.4,<0.7",
]
```

Note that `mypy` is installed separately in CI [.github/workflows/ci.yml:34]() but should be installed locally for type checking.

**Sources:** [chatkit/backend/pyproject.toml:13-16](), [.github/workflows/ci.yml:34]()

### Ruff Linting

Ruff is an extremely fast Python linter written in Rust that replaces multiple tools (Flake8, isort, pydocstyle, etc.). The CI workflow runs ruff linting via [.github/workflows/ci.yml:40-42]():

```bash
python -m ruff check app
```

This command lints all Python files in the `app/` directory, checking for:
- Code style violations
- Unused imports and variables
- Potential bugs and anti-patterns
- Import ordering issues
- Documentation style

**Sources:** [.github/workflows/ci.yml:40-42](), [chatkit/backend/pyproject.toml:14-16]()

### Ruff Formatting

Ruff also provides an opinionated code formatter (similar to Black but faster). The CI workflow checks formatting via [.github/workflows/ci.yml:44-50]():

```bash
python -m ruff format --check app
```

The `--check` flag validates that code is formatted correctly without modifying files. If formatting issues are detected, the workflow outputs a helpful error message [.github/workflows/ci.yml:48]() instructing developers to run `python -m ruff format app` locally.

**Sources:** [.github/workflows/ci.yml:44-50]()

### mypy Type Checking

mypy performs static type checking on Python code annotated with type hints. The CI workflow runs type checking via [.github/workflows/ci.yml:52-54]():

```bash
python -m mypy app --ignore-missing-imports
```

The `--ignore-missing-imports` flag suppresses errors for third-party libraries without type stubs, focusing type checking on the application code.

**Sources:** [.github/workflows/ci.yml:52-54](), [.github/workflows/ci.yml:34]()

### Python Quality Check Flow

```mermaid
graph TB
    SYNTAX["Syntax Check<br/>python -m compileall app"]
    LINT["Ruff Lint<br/>python -m ruff check app"]
    FORMAT["Ruff Format Check<br/>python -m ruff format --check app"]
    TYPE["mypy Type Check<br/>python -m mypy app --ignore-missing-imports"]
    SUCCESS["All Checks Pass"]
    FAIL["CI Failure"]
    
    SYNTAX -->|"Valid Python"| LINT
    SYNTAX -->|"Syntax Error"| FAIL
    LINT -->|"No Issues"| FORMAT
    LINT -->|"Lint Errors"| FAIL
    FORMAT -->|"Formatted"| TYPE
    FORMAT -->|"Needs Formatting"| FAIL
    TYPE -->|"Type Safe"| SUCCESS
    TYPE -->|"Type Errors"| FAIL
```

**Sources:** [.github/workflows/ci.yml:36-54]()

### Running Python Checks Locally

To run Python quality checks locally before committing:

1. **Install development dependencies:**
   ```bash
   cd chatkit/backend  # or managed-chatkit/backend
   pip install ".[dev]"
   pip install mypy
   ```

2. **Run syntax check:**
   ```bash
   python -m compileall app
   ```

3. **Run ruff linting:**
   ```bash
   python -m ruff check app
   ```

4. **Fix auto-fixable lint issues:**
   ```bash
   python -m ruff check app --fix
   ```

5. **Run ruff formatting:**
   ```bash
   python -m ruff format app
   ```

6. **Run type checking:**
   ```bash
   python -m mypy app --ignore-missing-imports
   ```

**Sources:** [.github/workflows/ci.yml:27-54](), [chatkit/backend/pyproject.toml:13-16]()

---

## Node.js Quality Tools

The frontend projects use ESLint for comprehensive linting and code quality enforcement.

### ESLint Configuration

Both frontend projects use ESLint with configurations appropriate to their frameworks. The CI workflow runs ESLint via [.github/workflows/ci.yml:81-83]():

```bash
npm run lint
```

This executes the `lint` script defined in each frontend's `package.json`.

**Sources:** [.github/workflows/ci.yml:81-83]()

### Running ESLint Locally

To run ESLint locally before committing:

1. **Install dependencies:**
   ```bash
   cd chatkit/frontend  # or managed-chatkit/frontend
   npm ci
   ```

2. **Run linting:**
   ```bash
   npm run lint
   ```

3. **Fix auto-fixable issues:**
   ```bash
   npm run lint -- --fix
   ```

**Sources:** [.github/workflows/ci.yml:77-83]()

---

## Quality Checks in CI/CD

The GitHub Actions workflow executes quality checks for all four projects (two backends, two frontends) in parallel. The workflow configuration uses a matrix strategy with `fail-fast: false` [.github/workflows/ci.yml:12-13](), ensuring all projects are validated even if one fails.

### Python Quality Pipeline

For each Python project (`chatkit/backend`, `managed-chatkit/backend`), the CI workflow [.github/workflows/ci.yml:9-54]() executes:

1. **Syntax Check** [.github/workflows/ci.yml:36-38]()
2. **Ruff Lint** [.github/workflows/ci.yml:40-42]()
3. **Ruff Format Check** [.github/workflows/ci.yml:44-50]()
4. **mypy Type Check** [.github/workflows/ci.yml:52-54]()

### Node.js Quality Pipeline

For each frontend project (`chatkit/frontend`, `managed-chatkit/frontend`), the CI workflow [.github/workflows/ci.yml:56-87]() executes:

1. **Install Dependencies** (`npm ci`) [.github/workflows/ci.yml:77-79]()
2. **ESLint Check** [.github/workflows/ci.yml:81-83]()
3. **Build Verification** [.github/workflows/ci.yml:85-87]()

For detailed information about the CI/CD pipeline configuration, see page 6 (CI/CD Pipeline).

**Sources:** [.github/workflows/ci.yml:9-87]()

---

## Development Workflow Integration

```mermaid
graph LR
    WRITE["Write Code"]
    SAVE["Save File"]
    IDE["IDE ESLint<br/>Extension"]
    LOCAL["npm run lint"]
    COMMIT["Git Commit"]
    PUSH["Git Push"]
    CI["CI Lint Check"]
    
    WRITE --> SAVE
    SAVE --> IDE
    IDE -.->|"Real-time feedback"| WRITE
    
    SAVE --> LOCAL
    LOCAL -->|"Pre-commit"| COMMIT
    
    COMMIT --> PUSH
    PUSH --> CI
    
    CI -.->|"Fails"| WRITE
```

ESLint provides multiple checkpoints:

1. **Real-time feedback**: IDE extensions (VS Code, IntelliJ) show linting errors while typing
2. **Pre-commit**: Developers can run `npm run lint` before committing
3. **CI enforcement**: [.github/workflows/ci.yml:26-27]() runs linting automatically on push and pull requests

**Sources:** [.github/workflows/ci.yml:26-27](), [package.json:9]()

---

## Dependencies

The ESLint ecosystem requires several packages defined in [package.json:21-31]():

| Package | Version | Purpose |
|---------|---------|---------|
| `eslint` | `^9` | Core ESLint engine |
| `@eslint/eslintrc` | `^3` | Backward compatibility utilities including `FlatCompat` |
| `eslint-config-next` | `15.5.4` | Next.js ESLint configurations (`next/core-web-vitals`, `next/typescript`) |

These are installed as `devDependencies` because they're only needed during development and CI builds, not in production runtime.

**Sources:** [package.json:21-31]()

---

## Configuration Maintenance

The ESLint configuration uses `FlatCompat` [eslint.config.mjs:1-10]() to maintain compatibility with Next.js's traditional configuration format while using ESLint 9's flat config system. This approach:

- Allows seamless upgrades to Next.js versions that may update ESLint configurations
- Maintains compatibility with Next.js tooling expectations
- Provides a migration path to native flat config when Next.js fully adopts it

The configuration exports a default array [eslint.config.mjs:12-25]() that ESLint 9 processes directly without requiring a `.eslintrc.*` file.

**Sources:** [eslint.config.mjs:1-26]()

---

## Summary Table

| Aspect | Implementation | Location |
|--------|----------------|----------|
| Configuration Format | ESLint 9 flat config with `FlatCompat` | [eslint.config.mjs:1-26]() |
| Extended Configs | `next/core-web-vitals`, `next/typescript` | [eslint.config.mjs:13]() |
| Local Execution | `npm run lint` | [package.json:9]() |
| CI Execution | GitHub Actions workflow step | [.github/workflows/ci.yml:26-27]() |
| Ignored Paths | Build outputs and dependencies | [eslint.config.mjs:15-21]() |
| Engine Version | ESLint 9.x | [package.json:27]() |

**Sources:** [eslint.config.mjs:1-26](), [package.json:9](), [package.json:21-31](), [.github/workflows/ci.yml:26-27]()

---

# Page: Deployment Considerations

# Deployment Considerations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [chatkit/.env.example](chatkit/.env.example)
- [chatkit/.gitignore](chatkit/.gitignore)
- [chatkit/README.md](chatkit/README.md)
- [chatkit/backend/.gitignore](chatkit/backend/.gitignore)
- [chatkit/backend/app/__init__.py](chatkit/backend/app/__init__.py)
- [chatkit/backend/app/memory_store.py](chatkit/backend/app/memory_store.py)
- [chatkit/backend/app/server.py](chatkit/backend/app/server.py)

</details>



This document provides guidance for deploying the ChatKit starter applications to production environments. It covers production build processes, environment configuration, persistent storage migration, deployment platform options, and security considerations.

Both the `chatkit/` (self-hosted) and `managed-chatkit/` (managed) variants follow the same deployment patterns, with differences noted where applicable.

For local development setup, see [Getting Started](#2). For CI/CD pipeline information, see [CI/CD Pipeline](#6).

---

## Architecture Overview

The starter applications use a two-tier architecture with independent frontend and backend components:

**Deployment Architecture Diagram**

```mermaid
graph TB
    subgraph "Client"
        BROWSER["User Browser"]
    end
    
    subgraph "Frontend_Server"
        VITE_PROD["Vite Production Build<br/>Static Assets"]
        NGINX["Web Server<br/>nginx/Apache/CDN"]
    end
    
    subgraph "Backend_Server"
        UVICORN["uvicorn ASGI Server<br/>Port 8000"]
        FASTAPI["FastAPI Application<br/>backend/app/main.py"]
        SERVER["StarterChatServer<br/>backend/app/server.py"]
        STORE["Storage Implementation<br/>MemoryStore → Production DB"]
    end
    
    subgraph "External"
        OPENAI["OpenAI API<br/>via openai-chatkit"]
    end
    
    BROWSER -->|"HTTPS"| NGINX
    NGINX -->|"Serve HTML/JS/CSS"| VITE_PROD
    NGINX -->|"Proxy /chatkit"| FASTAPI
    FASTAPI --> SERVER
    SERVER --> STORE
    SERVER -->|"openai-chatkit"| OPENAI
```

**Sources**: [chatkit/README.md:1-16](), [chatkit/backend/app/server.py:1-68]()

---

## Production Build Process

### Backend Build

The Python backend requires minimal build steps. The primary consideration is dependency installation:

```bash
# Navigate to backend directory
cd chatkit/backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install production dependencies
pip install -r requirements.txt
```

The backend does not require compilation or bundling. The FastAPI application in [chatkit/backend/app/main.py]() and supporting modules are ready to run directly.

**Backend Dependencies**:

| Package | Version Constraint | Purpose |
|---------|-------------------|---------|
| `fastapi` | `>=0.114.0,<0.117.0` | Web framework and API routing |
| `uvicorn` | `>=0.30.0,<0.31.0` | ASGI server for production |
| `openai` | `>=1.40.0` | OpenAI SDK for API access |
| `openai-chatkit` | `>=1.4.0,<2.0.0` | ChatKit server library |

**Sources**: [chatkit/backend/app/main.py](), backend requirements.txt

### Frontend Build

The Vite + React frontend requires a production build to generate optimized static assets:

```bash
# Navigate to frontend directory
cd chatkit/frontend

# Install dependencies
npm ci

# Build for production
npm run build
```

This produces a `dist/` directory containing:
- Minified JavaScript bundles with content hashing
- Optimized CSS files
- HTML entry point
- Static assets (fonts, images)

The `dist/` directory can be served by any static file server (nginx, Apache, CDN).

**Build Output Structure**:

```
frontend/dist/
├── index.html          # Entry point with injected script tags
├── assets/
│   ├── index-[hash].js    # Main JavaScript bundle
│   ├── index-[hash].css   # Compiled styles
│   └── vendor-[hash].js   # Third-party dependencies
└── vite.svg            # Static assets
```

**Sources**: [chatkit/README.md:8-10](), Vite build system

### Build Process Diagram

```mermaid
graph TD
    subgraph "Backend_Build"
        BE_SRC["Python Source<br/>backend/app/*.py"]
        BE_DEPS["requirements.txt"]
        BE_VENV["Virtual Environment<br/>.venv/"]
        BE_INSTALL["pip install"]
    end
    
    subgraph "Frontend_Build"
        FE_SRC["React/TypeScript<br/>frontend/src/**"]
        FE_DEPS["package.json"]
        FE_BUILD["npm run build<br/>Vite bundler"]
        FE_DIST["frontend/dist/<br/>Static assets"]
    end
    
    BE_DEPS --> BE_INSTALL
    BE_INSTALL --> BE_VENV
    BE_SRC --> BE_VENV
    
    FE_SRC --> FE_BUILD
    FE_DEPS --> FE_BUILD
    FE_BUILD --> FE_DIST
```

**Sources**: [chatkit/README.md:8-16](), [chatkit/backend/.gitignore:4]()

---

## Environment Configuration for Production

### Required Environment Variables

Both development and production environments require specific environment variables. Production deployments should configure these through platform-specific secret management systems.

| Variable | Required | Component | Purpose |
|----------|----------|-----------|---------|
| `OPENAI_API_KEY` | Yes | Backend | Authenticates with OpenAI API |
| `VITE_CHATKIT_API_URL` | No | Frontend | Backend API endpoint (default: `/chatkit`) |
| `VITE_CHATKIT_API_DOMAIN_KEY` | No | Frontend | Domain key for production (default: `domain_pk_localhost_dev`) |

**Sources**: [chatkit/.env.example:1-3](), [chatkit/README.md:18-26]()

### Environment Variable Configuration by Component

**Environment Variable Flow Diagram**

```mermaid
graph LR
    subgraph "Environment_Config"
        API_KEY["OPENAI_API_KEY<br/>Backend only"]
        API_URL["VITE_CHATKIT_API_URL<br/>Frontend only"]
        DOMAIN_KEY["VITE_CHATKIT_API_DOMAIN_KEY<br/>Frontend only"]
    end
    
    subgraph "Backend_Components"
        MAIN["backend/app/main.py"]
        SERVER["StarterChatServer"]
        AGENT["assistant_agent<br/>gpt-4o-mini"]
    end
    
    subgraph "Frontend_Components"
        CONFIG["frontend/src/lib/config.ts"]
        PANEL["ChatKitPanel.tsx"]
    end
    
    API_KEY -->|"os.environ"| SERVER
    SERVER --> AGENT
    API_URL --> CONFIG
    DOMAIN_KEY --> CONFIG
    CONFIG --> PANEL
```

**Sources**: [chatkit/.env.example:1-3](), [chatkit/backend/app/server.py:17-28]()

### Production Domain Key

The `VITE_CHATKIT_API_DOMAIN_KEY` must be registered in the OpenAI dashboard for production deployments:

1. Navigate to OpenAI Dashboard → ChatKit Settings
2. Register your production domain (e.g., `example.com`)
3. Copy the generated domain key (format: `domain_pk_...`)
4. Set as `VITE_CHATKIT_API_DOMAIN_KEY` environment variable

The default value `domain_pk_localhost_dev` only works for `localhost` development environments.

**Sources**: [chatkit/README.md:24-26]()

### Security Best Practices

1. **Never commit `.env` files**: The [chatkit/.gitignore:2-3]() explicitly excludes `.env*` files (except `.env.example`)

2. **Server-side only**: `OPENAI_API_KEY` is only accessible in backend Python code, never exposed to the frontend

3. **Frontend variables**: Variables prefixed with `VITE_` are embedded in the frontend bundle during build and are publicly visible. Do not include sensitive data.

4. **Platform-specific secrets management**:
   - **Docker**: Use `--env-file` flag or secrets management
   - **Kubernetes**: Use Secrets resources for `OPENAI_API_KEY`
   - **Cloud platforms**: Use native secret stores (AWS Secrets Manager, GCP Secret Manager, Azure Key Vault)

**Sources**: [chatkit/.gitignore:2-3](), [chatkit/.env.example:1-3]()

---

## Deployment Platforms

The application can be deployed to various platforms. Below are platform-specific configurations and considerations.

### Deployment Options Comparison

| Platform | Setup Complexity | Auto-scaling | Cost | Best For |
|----------|-----------------|--------------|------|----------|
| Vercel | Low | Automatic | Free tier + usage | Fastest deployment, zero config |
| Netlify | Low | Automatic | Free tier + usage | Alternative to Vercel |
| Docker | Medium | Manual/K8s | Infrastructure cost | Custom infrastructure, self-hosted |
| AWS/GCP/Azure | High | Configurable | Variable | Enterprise deployments |

### Vercel Deployment

Vercel provides the simplest deployment path for Next.js applications:

```mermaid
graph TD
    subgraph "Local_Development"
        CODE["Git Repository"]
    end
    
    subgraph "Vercel_Platform"
        IMPORT["Import Project"]
        ENV_CONFIG["Configure<br/>Environment Variables"]
        AUTO_BUILD["Automatic Build<br/>npm run build"]
        DEPLOY["Deploy to<br/>Production URL"]
    end
    
    subgraph "Production_URLs"
        PROD["Production Domain<br/>your-app.vercel.app"]
        CUSTOM["Custom Domain<br/>(optional)"]
    end
    
    CODE --> IMPORT
    IMPORT --> ENV_CONFIG
    ENV_CONFIG --> AUTO_BUILD
    AUTO_BUILD --> DEPLOY
    DEPLOY --> PROD
    PROD --> CUSTOM
```

**Deployment Steps**:

1. **Connect Repository**: Import your GitHub/GitLab repository into Vercel
2. **Configure Build**:
   - Build Command: `npm run build` (auto-detected from [package.json:7]())
   - Output Directory: `.next` (auto-detected)
   - Install Command: `npm install`
3. **Set Environment Variables**:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `NEXT_PUBLIC_CHATKIT_WORKFLOW_ID`: Your workflow ID from Agent Builder
   - `CHATKIT_API_BASE`: (Optional) Custom API endpoint
4. **Deploy**: Vercel automatically deploys on every push to main branch

**Sources**: [package.json:7](), [README.md](), Vercel Next.js deployment documentation

### Docker Deployment

For containerized deployments, create a `Dockerfile` in the project root:

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/public ./public
EXPOSE 3000
CMD ["npm", "start"]
```

**Docker Build and Run Commands**:

```bash
# Build image
docker build -t chatkit-starter-app .

# Run container with environment variables
docker run -p 3000:3000 \
  -e OPENAI_API_KEY=sk-proj-... \
  -e NEXT_PUBLIC_CHATKIT_WORKFLOW_ID=wf_... \
  chatkit-starter-app
```

The Docker configuration uses multi-stage builds to minimize image size and separates the build environment from the runtime environment.

**Sources**: [package.json:7-8](), Docker best practices for Node.js applications

### Self-Hosted with PM2

For self-hosted deployments on Linux servers:

```bash
# Install PM2 globally
npm install -g pm2

# Build the application
npm run build

# Start with PM2
pm2 start npm --name "chatkit-app" -- start

# Configure PM2 to restart on system reboot
pm2 startup
pm2 save
```

Create `ecosystem.config.js` for PM2 configuration:

```javascript
module.exports = {
  apps: [{
    name: 'chatkit-app',
    script: 'npm',
    args: 'start',
    env: {
      NODE_ENV: 'production',
      PORT: 3000
    },
    env_file: '.env.local'
  }]
}
```

**Sources**: [package.json:8](), PM2 process management documentation

---

## Production Runtime

### Starting the Production Server

After building, start the production server using the command from [package.json:8]():

```bash
npm start
```

This command executes `next start`, which:
- Serves the optimized production build from `.next/`
- Listens on port 3000 by default (configurable via `PORT` environment variable)
- Enables server-side rendering for dynamic routes
- Serves static assets with caching headers

### Production Server Architecture

```mermaid
graph TB
    subgraph "Client_Browser"
        USER["User Browser"]
    end
    
    subgraph "Next.js_Server"
        STATIC_HANDLER["Static File Handler<br/>.next/static/**"]
        SSR["Server-Side Renderer<br/>app/page.tsx"]
        API_HANDLER["API Route Handler<br/>app/api/create-session/route.ts"]
    end
    
    subgraph "External_Services"
        CDN["OpenAI CDN<br/>chatkit.js script"]
        CHATKIT_API["ChatKit API<br/>POST /v1/chatkit/sessions"]
    end
    
    USER -->|"GET /"| SSR
    USER -->|"GET /static/*"| STATIC_HANDLER
    USER -->|"POST /api/create-session"| API_HANDLER
    
    SSR -->|"Load script"| CDN
    API_HANDLER -->|"Create session"| CHATKIT_API
    CHATKIT_API -->|"client_secret"| API_HANDLER
    API_HANDLER -->|"Session credentials"| USER
```

**Sources**: [package.json:8](), [app/api/create-session/route.ts](), [app/layout.tsx]()

### Port Configuration

The default port is 3000, but can be overridden:

```bash
# Using PORT environment variable
PORT=8080 npm start

# Or in .env.local
PORT=8080
```

**Sources**: [package.json:8](), Next.js server configuration

---

## Security Best Practices

### API Key Protection

The `OPENAI_API_KEY` is the most sensitive credential in the application. It must be protected:

1. **Never commit to version control**: The `.env.example` template does not contain real keys
2. **Server-side only**: API key is only accessible in [app/api/create-session/route.ts]()
3. **No client exposure**: The key never appears in client-side bundles or network responses
4. **Rotate regularly**: Implement a key rotation policy for production environments

**Sources**: [.env.example:1](), [app/api/create-session/route.ts]()

### HTTPS Enforcement

All production deployments should enforce HTTPS to protect:
- API keys in transit to ChatKit API
- Session credentials returned from `/api/create-session`
- User chat messages and responses

Most modern deployment platforms (Vercel, Netlify) provide automatic HTTPS. For self-hosted deployments, use a reverse proxy:

```nginx
# Nginx configuration example
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

**Sources**: HTTPS best practices, reverse proxy configuration patterns

### Cookie Security

The application uses cookies for user session management in [app/api/create-session/route.ts](). In production, ensure cookies have secure attributes:

- `Secure`: Only transmitted over HTTPS
- `HttpOnly`: Not accessible via JavaScript
- `SameSite=Strict`: Prevents CSRF attacks

These attributes should be configured in the cookie creation logic.

**Sources**: [app/api/create-session/route.ts]()

### Content Security Policy

Implement Content Security Policy headers to restrict resource loading:

```javascript
// next.config.ts - add headers configuration
const config = {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: "default-src 'self'; script-src 'self' https://cdn.openai.com; connect-src 'self' https://api.openai.com"
          }
        ]
      }
    ]
  }
}
```

**Sources**: Content Security Policy documentation

---

## Post-Deployment Verification

### Health Check Endpoints

Verify deployment health by testing these endpoints:

```bash
# 1. Test home page loads
curl -I https://your-domain.com/

# 2. Test session creation API
curl -X POST https://your-domain.com/api/create-session \
  -H "Content-Type: application/json" \
  -d '{"workflow":{"id":"wf_..."}}'

# Expected: {"client_secret": "...", "expires_after": ...}
```

**Sources**: [app/api/create-session/route.ts]()

### Functional Testing Checklist

After deployment, verify the following functionality:

| Test Case | Expected Behavior | Verification Method |
|-----------|------------------|---------------------|
| Page Load | Home page renders without errors | Open in browser |
| ChatKit Script | `chatkit.js` loads from CDN | Check browser network tab |
| Session Creation | API returns `client_secret` | Browser DevTools → Network → XHR |
| Chat Initialization | Chat panel displays with greeting | Visual inspection |
| Message Send/Receive | Messages flow bidirectionally | Send test message |
| Theme Toggle | Light/dark mode switches properly | Click theme button |
| Error Handling | Errors display in ErrorOverlay | Force error condition |

**Sources**: [app/layout.tsx](), [components/ChatKitPanel.tsx](), [components/ErrorOverlay.tsx]()

### Performance Verification

Check Core Web Vitals for production performance:

```bash
# Using Lighthouse CLI
npx lighthouse https://your-domain.com --view

# Key metrics to monitor:
# - First Contentful Paint (FCP) < 1.8s
# - Largest Contentful Paint (LCP) < 2.5s
# - Cumulative Layout Shift (CLS) < 0.1
# - Time to Interactive (TTI) < 3.8s
```

The production build from `npm run build` includes optimizations that should achieve good scores.

**Sources**: [package.json:7](), Web Vitals documentation

---

## Monitoring and Troubleshooting

### Log Collection

In production, collect logs from multiple sources:

1. **Next.js Server Logs**: Capture stdout/stderr from `npm start` process
2. **API Route Logs**: Monitor [app/api/create-session/route.ts]() error responses
3. **Client-Side Errors**: Implement error tracking (Sentry, LogRocket, etc.)
4. **ChatKit Errors**: Monitor errors from ChatKitPanel error state

```javascript
// Example: Add to app/layout.tsx
window.addEventListener('error', (event) => {
  // Send to monitoring service
  console.error('Client error:', event.error);
});
```

**Sources**: [app/api/create-session/route.ts](), [components/ChatKitPanel.tsx]()

### Common Deployment Issues

| Issue | Symptom | Solution |
|-------|---------|----------|
| Missing env vars | "Configuration error" or blank page | Verify all required variables in [.env.example]() are set |
| Build failures | Deployment fails during build | Check [package.json]() dependencies match lock file |
| API authentication errors | 401/403 from ChatKit API | Verify `OPENAI_API_KEY` is valid and has ChatKit access |
| CORS errors | Network errors in browser console | Ensure `CHATKIT_API_BASE` matches actual API endpoint |
| Session creation fails | "Failed to create session" error | Check OpenAI API status and workflow ID validity |

**Sources**: [.env.example](), [package.json](), [app/api/create-session/route.ts]()

### Debugging Production Issues

Enable detailed logging without redeploying:

```bash
# Set debug environment variable
DEBUG=* npm start

# Or for specific modules
DEBUG=next:* npm start
```

For API route debugging, add temporary logging in [app/api/create-session/route.ts]():

```typescript
console.log('Environment check:', {
  hasApiKey: !!process.env.OPENAI_API_KEY,
  workflowId: process.env.NEXT_PUBLIC_CHATKIT_WORKFLOW_ID,
  apiBase: process.env.CHATKIT_API_BASE
});
```

**Sources**: [app/api/create-session/route.ts](), Next.js debugging documentation

### Rollback Strategy

If a deployment introduces critical issues:

1. **Vercel/Netlify**: Use instant rollback feature in dashboard
2. **Docker**: Revert to previous image tag
3. **Git-based**: Deploy previous commit
4. **PM2**: `pm2 reload chatkit-app --update-env`

Always maintain the previous working build artifacts for quick rollback.

**Sources**: Deployment platform rollback documentation

---

## Scaling Considerations

### Horizontal Scaling

The application is stateless and can be horizontally scaled:

```mermaid
graph TD
    subgraph "Load_Balancer"
        LB["Load Balancer<br/>HTTPS Termination"]
    end
    
    subgraph "App_Instances"
        APP1["Next.js Instance 1<br/>npm start"]
        APP2["Next.js Instance 2<br/>npm start"]
        APP3["Next.js Instance N<br/>npm start"]
    end
    
    subgraph "Shared_Services"
        OPENAI_API["OpenAI ChatKit API"]
    end
    
    LB --> APP1
    LB --> APP2
    LB --> APP3
    
    APP1 --> OPENAI_API
    APP2 --> OPENAI_API
    APP3 --> OPENAI_API
```

Each instance operates independently since session state is managed by ChatKit API, not the application server.

**Sources**: [app/api/create-session/route.ts](), stateless architecture pattern

### Performance Optimization

For high-traffic deployments:

1. **Enable CDN**: Cache static assets from `.next/static/` at edge locations
2. **API Route Caching**: Cache OpenAI API responses where appropriate
3. **Bundle Size Optimization**: Analyze bundle size with `npm run build` output
4. **Lazy Loading**: Defer non-critical JavaScript loading

**Sources**: [package.json:7](), Next.js performance optimization

### Resource Requirements

Minimum server specifications per instance:

- **CPU**: 1 vCPU (2+ recommended for concurrent users)
- **Memory**: 512MB minimum, 1GB recommended
- **Disk**: 500MB for application + dependencies
- **Network**: Reliable connection to OpenAI API endpoints

**Sources**: Next.js server requirements, Node.js performance guidelines

---

## Continuous Deployment

### Automated Deployment Pipeline

Integrate deployment with the CI workflow from [.github/workflows/ci.yml]():

```mermaid
graph LR
    subgraph "CI_Workflow"
        PUSH["Push to main"]
        LINT["npm run lint"]
        BUILD["npm run build"]
    end
    
    subgraph "CD_Workflow"
        DEPLOY_STAGING["Deploy to Staging"]
        SMOKE_TEST["Smoke Tests"]
        DEPLOY_PROD["Deploy to Production"]
    end
    
    PUSH --> LINT
    LINT --> BUILD
    BUILD -->|"Success"| DEPLOY_STAGING
    DEPLOY_STAGING --> SMOKE_TEST
    SMOKE_TEST -->|"Pass"| DEPLOY_PROD
```

**Sources**: [.github/workflows/ci.yml](), [package.json:7-9]()

### Environment Promotion Strategy

Maintain separate environments:

| Environment | Purpose | Deployment Trigger |
|-------------|---------|-------------------|
| Development | Local testing | Manual: `npm run dev` |
| Staging | Pre-production validation | Auto: Merge to `develop` branch |
| Production | Live users | Manual: Merge to `main` after approval |

Each environment should have its own `OPENAI_API_KEY` and `NEXT_PUBLIC_CHATKIT_WORKFLOW_ID` to isolate workflows.

**Sources**: [.env.example](), [package.json:6-8]()

---

## Summary

Deploying the ChatKit Starter App to production requires:

1. **Build**: Execute `npm run build` to create optimized production assets
2. **Environment**: Configure `OPENAI_API_KEY` and `NEXT_PUBLIC_CHATKIT_WORKFLOW_ID`
3. **Platform**: Choose deployment platform (Vercel, Docker, self-hosted)
4. **Security**: Enforce HTTPS, protect API keys, configure secure cookies
5. **Verification**: Test endpoints, functionality, and performance
6. **Monitoring**: Collect logs and track errors for troubleshooting

The application's stateless architecture and Next.js foundation enable straightforward deployment to various platforms with minimal configuration.

**Sources**: [package.json:7-8](), [.env.example](), [README.md:45-50]()

---

# Page: Production Environment Variables

# Production Environment Variables

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [chatkit/.env.example](chatkit/.env.example)
- [chatkit/.gitignore](chatkit/.gitignore)
- [chatkit/README.md](chatkit/README.md)
- [chatkit/backend/.gitignore](chatkit/backend/.gitignore)
- [chatkit/backend/app/__init__.py](chatkit/backend/app/__init__.py)

</details>



This document specifies the environment variables required for deploying either ChatKit starter application (`chatkit/` or `managed-chatkit/`) to production environments. It covers configuration differences between development and production, domain key registration, and security best practices.

For local development environment setup, see [Local Development Setup](#7.1). For deployment architecture decisions, see [Deployment Considerations](#8).

---

## Purpose and Scope

Environment variables control runtime configuration for both the backend (FastAPI) and frontend (Vite/React) components. Production deployments require specific values that differ from development defaults, particularly for API authentication and domain-specific security.

This document covers:
- Required and optional environment variables
- Development vs production value differences
- Domain key registration process
- Security and access control considerations
- Platform-specific deployment patterns

---

## Environment Variable Overview

The starter applications use three primary environment variables, divided between backend and frontend configurations:

| Variable | Component | Required | Default (Dev) | Production Notes |
|----------|-----------|----------|---------------|------------------|
| `OPENAI_API_KEY` | Backend | Yes | None | API key from OpenAI platform |
| `VITE_CHATKIT_API_URL` | Frontend | No | `/chatkit` | Full URL for cross-origin deployments |
| `VITE_CHATKIT_API_DOMAIN_KEY` | Frontend | No | `domain_pk_localhost_dev` | Registered domain key from OpenAI dashboard |

**Sources:** [chatkit/README.md:18-26](), [chatkit/.env.example:1-3]()

---

## Configuration Architecture

```mermaid
graph TB
    subgraph DevEnv["Development Environment"]
        DevFile[".env.local<br/>(gitignored)"]
        DevShell["Shell Environment"]
    end
    
    subgraph Runtime["Application Runtime"]
        Backend["FastAPI Backend<br/>Port 8000"]
        Frontend["Vite Frontend<br/>Port 3000"]
    end
    
    subgraph ProdEnv["Production Environment"]
        ProdPlatform["Deployment Platform<br/>(Vercel, AWS, etc)"]
        ProdSecrets["Secrets Manager"]
    end
    
    subgraph OpenAI["OpenAI Platform"]
        APIKey["API Key<br/>(OPENAI_API_KEY)"]
        DomainReg["Domain Registration<br/>(VITE_CHATKIT_API_DOMAIN_KEY)"]
    end
    
    DevFile -->|Loads| Backend
    DevFile -->|Loads| Frontend
    DevShell -->|Loads| Backend
    
    ProdPlatform -->|Injects| Backend
    ProdPlatform -->|Injects| Frontend
    ProdSecrets -->|Provides| ProdPlatform
    
    APIKey -.->|Authenticates| Backend
    DomainReg -.->|Validates| Frontend
    
    Backend -->|"OPENAI_API_KEY"| APIKey
    Frontend -->|"VITE_CHATKIT_API_DOMAIN_KEY"| DomainReg
```

**Sources:** [chatkit/README.md:24-26](), [chatkit/.gitignore:1-3]()

---

## Backend Environment Variables

### OPENAI_API_KEY (Required)

The OpenAI API key authenticates backend requests to the OpenAI API through the `openai-chatkit` library.

**Format:** `sk-proj-...` (project-scoped key)

**Development:**
```bash
# In .env.local or shell
OPENAI_API_KEY=sk-proj-abcdef123456...
```

**Production Considerations:**
- **Never commit** to version control (enforced by [chatkit/backend/.gitignore:5]() and [chatkit/.gitignore:2]())
- Use platform-specific secrets management (AWS Secrets Manager, Vercel Environment Variables, etc.)
- Rotate keys regularly following security best practices
- Use project-scoped keys to limit blast radius
- Monitor usage through OpenAI dashboard for anomalies

**Runtime Access:**
The backend loads this variable at startup. The FastAPI application does not directly access it; instead, the `openai-chatkit` library's `Agent` class uses it to authenticate API requests.

**Sources:** [chatkit/README.md:20](), [chatkit/.env.example:1](), [chatkit/backend/.gitignore:5]()

---

## Frontend Environment Variables

Frontend environment variables must be prefixed with `VITE_` to be embedded in the client bundle during the Vite build process.

### VITE_CHATKIT_API_URL (Optional)

Specifies the backend API endpoint URL. The frontend proxies ChatKit requests to this URL.

**Default:** `/chatkit` (relative path, proxied by Vite dev server)

**Development:**
```bash
# Default behavior (no explicit config needed)
VITE_CHATKIT_API_URL=/chatkit
```

**Production:**
```bash
# Separate backend deployment
VITE_CHATKIT_API_URL=https://api.example.com/chatkit

# Same-origin deployment with path prefix
VITE_CHATKIT_API_URL=/api/chatkit
```

**When to Override:**
- Backend and frontend deployed to separate domains
- Backend behind API gateway with custom path
- Multiple environments (staging, production) with different backend URLs

**Sources:** [chatkit/README.md:21](), [chatkit/.env.example:2]()

---

### VITE_CHATKIT_API_DOMAIN_KEY (Optional)

Domain-specific security key registered through the OpenAI dashboard. This key validates that the frontend is authorized to use ChatKit from the deployment domain.

**Default:** `domain_pk_localhost_dev` (development-only key)

**Development:**
```bash
# Default for local development
VITE_CHATKIT_API_DOMAIN_KEY=domain_pk_localhost_dev
```

**Production:**
```bash
# Production domain key
VITE_CHATKIT_API_DOMAIN_KEY=domain_pk_prod_abc123xyz
```

**Registration Process:**
1. Deploy frontend to production domain (e.g., `https://chat.example.com`)
2. Access OpenAI dashboard
3. Navigate to ChatKit domain registration section
4. Register domain: `chat.example.com`
5. Receive domain key: `domain_pk_prod_...`
6. Set `VITE_CHATKIT_API_DOMAIN_KEY` environment variable
7. Rebuild and redeploy frontend with new key

**Security Notes:**
- Domain keys prevent unauthorized domains from using your ChatKit integration
- Each production domain requires a separate registered key
- Development key (`domain_pk_localhost_dev`) only works on `localhost`
- Keys are public (embedded in client bundle) but domain-validated

**Sources:** [chatkit/README.md:22](), [chatkit/README.md:25-26](), [chatkit/.env.example:3]()

---

## Development vs Production Configuration Matrix

```mermaid
graph LR
    subgraph Development["Development Configuration"]
        Dev_API["OPENAI_API_KEY<br/>From .env.local"]
        Dev_URL["VITE_CHATKIT_API_URL<br/>/chatkit (default)"]
        Dev_Domain["VITE_CHATKIT_API_DOMAIN_KEY<br/>domain_pk_localhost_dev"]
    end
    
    subgraph Production["Production Configuration"]
        Prod_API["OPENAI_API_KEY<br/>From secrets manager"]
        Prod_URL["VITE_CHATKIT_API_URL<br/>https://api.domain.com/chatkit"]
        Prod_Domain["VITE_CHATKIT_API_DOMAIN_KEY<br/>domain_pk_prod_registered"]
    end
    
    Dev_API -.->|"Upgrade"| Prod_API
    Dev_URL -.->|"Customize"| Prod_URL
    Dev_Domain -.->|"Register & Replace"| Prod_Domain
```

| Aspect | Development | Production |
|--------|-------------|------------|
| **Source** | `.env.local` file (gitignored) | Platform secrets manager |
| **API Key** | Personal development key | Organization production key |
| **Backend URL** | `/chatkit` (proxied) | Full URL or path with domain |
| **Domain Key** | `domain_pk_localhost_dev` | Registered domain key |
| **Security** | Local-only, minimal risk | Secrets rotation, monitoring |
| **Build Process** | Live reload with `npm run dev` | Static build with `npm run build` |

**Sources:** [chatkit/README.md:18-26](), [chatkit/.env.example:1-3]()

---

## Environment Variable Loading Patterns

### Backend (FastAPI)

The FastAPI backend loads environment variables using Python's standard `os.environ` or libraries like `python-dotenv`:

**Loading Priority:**
1. Shell environment variables (highest priority)
2. `.env.local` file at repository root
3. Platform-injected environment variables (production)

**Example Access Pattern:**
```python
# Typical pattern (not shown in starter code)
import os

api_key = os.environ.get("OPENAI_API_KEY")
```

**Deployment Notes:**
- In production, avoid file-based `.env` loading
- Use platform-native environment variable injection
- Backend runs as long-lived process; changes require restart

**Sources:** [chatkit/README.md:24](), [chatkit/backend/.gitignore:5]()

---

### Frontend (Vite)

Vite bundles environment variables into the client JavaScript at build time. Variables must have the `VITE_` prefix.

**Build-Time Embedding:**
```mermaid
graph LR
    EnvVar["VITE_CHATKIT_API_URL<br/>Environment Variable"]
    ViteBuild["Vite Build Process"]
    Bundle["JavaScript Bundle<br/>(contains hardcoded values)"]
    
    EnvVar -->|"Read at build time"| ViteBuild
    ViteBuild -->|"Embeds as string literal"| Bundle
```

**Access Pattern:**
```typescript
// In frontend/src/lib/config.ts (typical pattern)
const apiUrl = import.meta.env.VITE_CHATKIT_API_URL || '/chatkit';
const domainKey = import.meta.env.VITE_CHATKIT_API_DOMAIN_KEY || 'domain_pk_localhost_dev';
```

**Critical Differences from Backend:**
- **Build-time only:** Changing variables requires rebuild
- **Public values:** All `VITE_` variables are visible in client bundle
- **No secrets:** Never put sensitive keys in `VITE_` variables

**Deployment Workflow:**
1. Set production environment variables on platform
2. Trigger build: `npm run build`
3. Vite reads `VITE_*` variables and embeds in bundle
4. Deploy static assets to CDN/hosting
5. Changes require full rebuild and redeploy

**Sources:** [chatkit/README.md:21-22](), [chatkit/.env.example:2-3]()

---

## Platform-Specific Configuration Examples

### Vercel

```bash
# Environment variables set in Vercel dashboard
OPENAI_API_KEY=sk-proj-xxx              # Backend (secure)
VITE_CHATKIT_API_URL=/api/chatkit       # Frontend (build-time)
VITE_CHATKIT_API_DOMAIN_KEY=domain_pk_prod_xxx  # Frontend (build-time)
```

**Vercel-Specific Notes:**
- Set backend variables as "Server" type for security
- Frontend variables automatically available at build
- Separate environment scopes (production, preview, development)

### AWS (ECS + S3/CloudFront)

**Backend (ECS Task Definition):**
```json
{
  "environment": [
    {
      "name": "OPENAI_API_KEY",
      "valueFrom": "arn:aws:secretsmanager:..."
    }
  ]
}
```

**Frontend (Build via CodeBuild):**
```yaml
# buildspec.yml
env:
  variables:
    VITE_CHATKIT_API_URL: "https://api.example.com/chatkit"
  secrets-manager:
    VITE_CHATKIT_API_DOMAIN_KEY: "prod/frontend:DOMAIN_KEY"
```

### Docker / Docker Compose

**docker-compose.yml:**
```yaml
services:
  backend:
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    env_file:
      - .env.production
  
  frontend:
    build:
      args:
        - VITE_CHATKIT_API_URL=${VITE_CHATKIT_API_URL}
        - VITE_CHATKIT_API_DOMAIN_KEY=${VITE_CHATKIT_API_DOMAIN_KEY}
```

**Sources:** [chatkit/README.md:24-26]()

---

## Security Best Practices

### API Key Management

```mermaid
graph TB
    subgraph Secure["✓ Secure Practices"]
        SecretMgr["Secrets Manager"]
        EnvInject["Runtime Injection"]
        KeyRotation["Regular Rotation"]
        AccessLogs["Monitor API Usage"]
    end
    
    subgraph Insecure["✗ Insecure Practices"]
        Commit["Commit to Git"]
        HardCode["Hardcode in Source"]
        ClientSide["Expose in Frontend"]
        SharedKey["Share Across Teams"]
    end
    
    SecretMgr -.->|"Best Practice"| EnvInject
    EnvInject -.->|"Enable"| KeyRotation
    KeyRotation -.->|"Verify"| AccessLogs
    
    Commit -.->|"Risk: Leaked Keys"| Insecure
    HardCode -.->|"Risk: No Rotation"| Insecure
    ClientSide -.->|"Risk: Public Access"| Insecure
```

**Critical Security Rules:**

1. **Never commit API keys** - Enforced by `.gitignore` patterns
2. **Backend only** - `OPENAI_API_KEY` must never reach frontend
3. **Use secrets managers** - AWS Secrets Manager, HashiCorp Vault, etc.
4. **Rotate regularly** - Implement key rotation schedule
5. **Monitor usage** - Set up alerts for unusual API consumption
6. **Least privilege** - Use project-scoped keys when possible

**Sources:** [chatkit/backend/.gitignore:5](), [chatkit/.gitignore:2]()

---

### Domain Key Security

**Domain keys are public but validated:**
- Embedded in client JavaScript bundle (visible to users)
- OpenAI validates origin domain matches registered domain
- Prevents unauthorized domains from using your integration
- Not a secret; protects against cross-origin abuse

**Registration Requirements:**
- Each production domain requires separate key
- Subdomains need separate registration
- Development key only works on `localhost`

**Sources:** [chatkit/README.md:25-26]()

---

## Validation and Troubleshooting

### Missing OPENAI_API_KEY

**Symptom:** Backend fails to start or API requests fail

**Error Pattern:**
```
Error: OpenAI API key not found
```

**Resolution:**
1. Verify key is set: `echo $OPENAI_API_KEY`
2. Check `.env.local` exists and contains key
3. Restart backend after setting variable
4. Verify key format starts with `sk-proj-` or `sk-`

---

### Incorrect VITE_CHATKIT_API_URL

**Symptom:** Frontend cannot connect to backend

**Error Pattern:**
```
Failed to fetch: ERR_CONNECTION_REFUSED
CORS policy error
```

**Resolution:**
1. Verify backend is running on expected URL
2. Check CORS configuration in backend allows origin
3. Rebuild frontend after changing variable
4. Verify proxy configuration in `vite.config.ts` (development only)

---

### Invalid VITE_CHATKIT_API_DOMAIN_KEY

**Symptom:** ChatKit initialization fails in browser

**Error Pattern:**
```
Domain key validation failed
Unauthorized domain
```

**Resolution:**
1. Verify domain key registered in OpenAI dashboard
2. Confirm deployment domain matches registered domain
3. Check for typos in domain key value
4. Rebuild and redeploy frontend
5. Use `domain_pk_localhost_dev` for local development only

**Sources:** [chatkit/README.md:25-26]()

---

## Environment Variable Checklist

Use this checklist when deploying to production:

- [ ] `OPENAI_API_KEY` set in secrets manager (backend)
- [ ] API key tested and validated with OpenAI
- [ ] Key monitoring and rotation schedule configured
- [ ] Production domain deployed and accessible
- [ ] Domain registered in OpenAI dashboard
- [ ] `VITE_CHATKIT_API_DOMAIN_KEY` obtained from registration
- [ ] `VITE_CHATKIT_API_URL` set to production backend URL
- [ ] Frontend rebuilt with production environment variables
- [ ] CORS configuration allows production frontend domain
- [ ] Test end-to-end chat flow in production
- [ ] `.env.local` and `.env` files not committed (verify `.gitignore`)
- [ ] Documentation updated with deployment-specific values

**Sources:** [chatkit/README.md:18-26](), [chatkit/.gitignore:2]()

---

## Related Documentation

- **[Environment Configuration](#2.2)** - Development environment setup and `.env.local` configuration
- **[Local Development Setup](#7.1)** - Complete local development workflow
- **[Deployment Considerations](#8)** - Overall deployment architecture decisions
- **[Persistent Storage Migration](#8.2)** - Database configuration for production deployments

---

# Page: Persistent Storage Migration

# Persistent Storage Migration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [chatkit/backend/app/memory_store.py](chatkit/backend/app/memory_store.py)
- [chatkit/backend/app/server.py](chatkit/backend/app/server.py)

</details>



## Purpose and Scope

This document provides technical guidance for replacing the in-memory `MemoryStore` implementation with a persistent database backend for production deployment of the self-hosted ChatKit application. The `MemoryStore` class is explicitly designed as a development convenience and loses all conversation data when the server restarts.

For information about the `MemoryStore` implementation details, see [MemoryStore](#3.2.3). For general deployment considerations, see [Deployment Considerations](#8). For production environment configuration, see [Production Environment Variables](#8.1).

---

## Why Migration is Required

The current `MemoryStore` implementation stores all conversation data in Python dictionaries that exist only in process memory:

```
In-Memory Storage Structure:
┌─────────────────────────────────────┐
│  MemoryStore Instance               │
│  ┌───────────────────────────────┐  │
│  │ self.threads: dict[str, ...]  │  │  ← Lost on restart
│  │ self.items: defaultdict(list) │  │  ← Lost on restart
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

**Critical limitations:**
- Data loss occurs on every server restart, crash, or deployment
- No horizontal scaling capability (each server instance has separate state)
- No data durability guarantees
- No backup or recovery mechanisms

Sources: [chatkit/backend/app/memory_store.py:1-4](), [chatkit/backend/app/memory_store.py:14-17]()

---

## Store Interface Contract

All persistent storage implementations must satisfy the `Store[TContext]` interface from the `chatkit.store` module. The `MemoryStore` demonstrates the complete interface contract:

```mermaid
graph TB
    subgraph "chatkit.store Interface"
        Store["Store[TContext]<br/>(Abstract Base)"]
    end
    
    subgraph "Current Implementation"
        MemoryStore["MemoryStore(Store[dict])"]
    end
    
    subgraph "Your Implementation"
        YourStore["YourPersistentStore(Store[dict])"]
    end
    
    Store -->|"implements"| MemoryStore
    Store -->|"must implement"| YourStore
    
    subgraph "Required Methods"
        ThreadOps["Thread Operations<br/>• load_thread<br/>• save_thread<br/>• load_threads<br/>• delete_thread"]
        ItemOps["Item Operations<br/>• load_thread_items<br/>• add_thread_item<br/>• save_item<br/>• load_item<br/>• delete_thread_item"]
        AttachOps["Attachment Operations<br/>• save_attachment<br/>• load_attachment<br/>• delete_attachment"]
    end
    
    Store -.->|"requires"| ThreadOps
    Store -.->|"requires"| ItemOps
    Store -.->|"requires"| AttachOps
```

**Complete method signature table:**

| Method | Signature | Purpose |
|--------|-----------|---------|
| `load_thread` | `async def load_thread(thread_id: str, context: TContext) -> ThreadMetadata` | Retrieve single thread metadata |
| `save_thread` | `async def save_thread(thread: ThreadMetadata, context: TContext) -> None` | Create or update thread metadata |
| `load_threads` | `async def load_threads(limit: int, after: str \| None, order: str, context: TContext) -> Page[ThreadMetadata]` | List threads with pagination |
| `delete_thread` | `async def delete_thread(thread_id: str, context: TContext) -> None` | Remove thread and associated items |
| `load_thread_items` | `async def load_thread_items(thread_id: str, after: str \| None, limit: int, order: str, context: TContext) -> Page[ThreadItem]` | List items in thread with pagination |
| `add_thread_item` | `async def add_thread_item(thread_id: str, item: ThreadItem, context: TContext) -> None` | Append new item to thread |
| `save_item` | `async def save_item(thread_id: str, item: ThreadItem, context: TContext) -> None` | Create or update thread item |
| `load_item` | `async def load_item(thread_id: str, item_id: str, context: TContext) -> ThreadItem` | Retrieve single item |
| `delete_thread_item` | `async def delete_thread_item(thread_id: str, item_id: str, context: TContext) -> None` | Remove item from thread |
| `save_attachment` | `async def save_attachment(attachment: Attachment, context: TContext) -> None` | Store attachment (optional) |
| `load_attachment` | `async def load_attachment(attachment_id: str, context: TContext) -> Attachment` | Retrieve attachment (optional) |
| `delete_attachment` | `async def delete_attachment(attachment_id: str, context: TContext) -> None` | Remove attachment (optional) |

Sources: [chatkit/backend/app/memory_store.py:14-115]()

---

## Data Model Analysis

### ThreadMetadata Structure

The `ThreadMetadata` type (from `chatkit.types`) represents conversation metadata:

```mermaid
erDiagram
    ThreadMetadata {
        string id PK "Unique thread identifier"
        datetime created_at "Creation timestamp"
        string title "Optional display title"
        dict metadata "Custom key-value data"
    }
```

**Storage considerations:**
- `id` must be indexed for efficient lookups
- `created_at` required for sorting in `load_threads` with `order="desc"` or `order="asc"`
- `metadata` field contains arbitrary JSON-serializable data

### ThreadItem Structure

The `ThreadItem` type represents individual messages or events:

```mermaid
erDiagram
    ThreadItem {
        string id PK "Unique item identifier"
        string thread_id FK "Parent thread reference"
        datetime created_at "Creation timestamp"
        string type "Item type discriminator"
        object content "Type-specific content"
    }
```

**Storage considerations:**
- Composite index on `(thread_id, created_at)` for efficient pagination
- `type` field discriminates between `UserMessageItem`, `AssistantMessageItem`, etc.
- `content` structure varies by type (requires JSON or flexible schema)

### Pagination Mechanics

The `MemoryStore._paginate` method implements cursor-based pagination:

```mermaid
sequenceDiagram
    participant Client
    participant Store
    participant DB as "Database Query"
    
    Client->>Store: load_thread_items(after=None, limit=30, order="desc")
    Store->>DB: SELECT * ORDER BY created_at DESC LIMIT 30
    DB-->>Store: [items]
    Store-->>Client: Page(data=[...], has_more=True, after="item_29_id")
    
    Client->>Store: load_thread_items(after="item_29_id", limit=30, order="desc")
    Store->>DB: SELECT * WHERE created_at < cursor_timestamp ORDER BY created_at DESC LIMIT 30
    DB-->>Store: [items]
    Store-->>Client: Page(data=[...], has_more=False, after=None)
```

The `after` parameter is an opaque cursor (typically the last item's ID). Your implementation must:
1. Sort by the appropriate key (`created_at` for items and threads)
2. Resume iteration after the cursor position
3. Return `has_more=True` if additional results exist
4. Provide the next cursor in `after` when `has_more=True`

Sources: [chatkit/backend/app/memory_store.py:85-104]()

---

## Migration Strategy Overview

```mermaid
graph LR
    subgraph "Phase 1: Preparation"
        P1["Choose Database<br/>Technology"]
        P2["Design Schema<br/>& Indexes"]
        P3["Set Up Database<br/>Infrastructure"]
    end
    
    subgraph "Phase 2: Implementation"
        I1["Create Store<br/>Subclass"]
        I2["Implement Thread<br/>Methods"]
        I3["Implement Item<br/>Methods"]
        I4["Add Connection<br/>Management"]
    end
    
    subgraph "Phase 3: Integration"
        T1["Replace MemoryStore<br/>in StarterChatServer"]
        T2["Update Configuration<br/>& Environment"]
        T3["Test All Operations<br/>End-to-End"]
    end
    
    subgraph "Phase 4: Deployment"
        D1["Run Database<br/>Migrations"]
        D2["Deploy Application<br/>with New Store"]
        D3["Monitor & Validate<br/>Production Behavior"]
    end
    
    P1 --> P2 --> P3 --> I1 --> I2 --> I3 --> I4 --> T1 --> T2 --> T3 --> D1 --> D2 --> D3
```

Sources: General migration best practices

---

## Database Technology Selection

### Comparison Matrix

| Database | Async Support | Schema Flexibility | Query Complexity | Operational Overhead | Best For |
|----------|--------------|-------------------|------------------|---------------------|----------|
| **PostgreSQL** | Excellent (`asyncpg`) | Structured + JSONB | High (SQL) | Medium | Production systems requiring ACID guarantees |
| **MongoDB** | Excellent (`motor`) | Schemaless | Medium (query DSL) | Medium | Document-heavy workloads with flexible schema |
| **SQLite** | Good (`aiosqlite`) | Structured + JSON1 | High (SQL) | Low | Development, single-instance deployments |
| **DynamoDB** | Excellent (`aioboto3`) | Key-value + attributes | Low (limited queries) | High (AWS managed) | Serverless, AWS-native deployments |

### Recommended Stack: PostgreSQL

**Rationale:**
- **Async driver ecosystem:** `asyncpg` provides high-performance async operations compatible with FastAPI's async model
- **JSONB support:** Native JSON storage for `ThreadMetadata.metadata` and flexible `ThreadItem.content`
- **Robust indexing:** Composite indexes on `(thread_id, created_at)` for efficient pagination
- **Transaction support:** ACID guarantees for consistent multi-record operations

**Python dependencies to add:**
```
asyncpg>=0.29.0
sqlalchemy[asyncio]>=2.0.0  # Optional ORM layer
```

Sources: Industry best practices for FastAPI + async database integration

---

## Implementation Steps

### Step 1: Define Database Schema

**Recommended table structure for PostgreSQL:**

```sql
-- Threads table
CREATE TABLE threads (
    id VARCHAR(255) PRIMARY KEY,
    created_at TIMESTAMP NOT NULL,
    title VARCHAR(1024),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX idx_threads_created_at ON threads(created_at DESC);

-- Thread items table
CREATE TABLE thread_items (
    id VARCHAR(255) PRIMARY KEY,
    thread_id VARCHAR(255) NOT NULL REFERENCES threads(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL,
    type VARCHAR(100) NOT NULL,
    content JSONB NOT NULL
);

CREATE INDEX idx_items_thread_created ON thread_items(thread_id, created_at DESC);
CREATE INDEX idx_items_created_at ON thread_items(created_at DESC);
```

**Key design decisions:**
- `JSONB` columns for flexible metadata and content storage
- `ON DELETE CASCADE` ensures deleting a thread removes all associated items
- Descending indexes optimize the common `order="desc"` pagination case
- `VARCHAR(255)` for IDs supports UUID and custom identifier schemes

Sources: Database schema design best practices

### Step 2: Create Store Implementation File

Create a new file `chatkit/backend/app/postgres_store.py`:

```
chatkit/backend/app/
├── __init__.py
├── main.py
├── memory_store.py          # Existing implementation
├── postgres_store.py        # New: Your persistent implementation
└── server.py
```

**Implementation outline (reference structure, not complete code):**

```python
# Structure reference - implement similar to memory_store.py:14-115
class PostgresStore(Store[dict]):
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.pool = None  # asyncpg connection pool
    
    async def initialize(self):
        # Create connection pool
        pass
    
    async def load_thread(self, thread_id: str, context: dict) -> ThreadMetadata:
        # SELECT * FROM threads WHERE id = $1
        pass
    
    async def save_thread(self, thread: ThreadMetadata, context: dict) -> None:
        # INSERT INTO threads ... ON CONFLICT (id) DO UPDATE
        pass
    
    # ... implement all other Store methods
```

Sources: [chatkit/backend/app/memory_store.py:14-36]()

### Step 3: Implement Pagination with SQL

The pagination logic in [chatkit/backend/app/memory_store.py:85-104]() must be adapted to SQL:

**In-memory approach (current):**
```python
sorted_rows = sorted(rows, key=sort_key, reverse=order == "desc")
if after:
    for idx, row in enumerate(sorted_rows):
        if cursor_key(row) == after:
            start = idx + 1
```

**SQL-based approach (your implementation):**
```sql
-- For order="desc", after is the last returned created_at timestamp
SELECT * FROM thread_items 
WHERE thread_id = $1 
  AND created_at < $2  -- Use cursor timestamp
ORDER BY created_at DESC 
LIMIT $3;

-- For order="asc"
SELECT * FROM thread_items 
WHERE thread_id = $1 
  AND created_at > $2  -- Use cursor timestamp
ORDER BY created_at ASC 
LIMIT $3;
```

**Cursor encoding strategy:**
Since `after` is an opaque string, encode both the ID and timestamp:
```python
# Encoding: "timestamp:id" for stable pagination
cursor = f"{item.created_at.isoformat()}:{item.id}"

# Decoding in query
if after:
    cursor_timestamp, cursor_id = after.split(":", 1)
    # Use in WHERE clause for reliable pagination
```

Sources: [chatkit/backend/app/memory_store.py:85-104]()

### Step 4: Update StarterChatServer Integration

Modify [chatkit/backend/app/server.py:34-36]() to use your persistent store:

**Current code:**
```python
class StarterChatServer(ChatKitServer[dict[str, Any]]):
    def __init__(self) -> None:
        self.store: MemoryStore = MemoryStore()
        super().__init__(self.store)
```

**Updated integration point:**
```python
# Import your new store implementation
from .postgres_store import PostgresStore

class StarterChatServer(ChatKitServer[dict[str, Any]]):
    def __init__(self, store: Store[dict[str, Any]]) -> None:
        self.store = store
        super().__init__(self.store)
```

**In main.py, initialize with database connection:**
```python
# Reference the initialization pattern
# Initialize PostgresStore with connection string from environment
# Pass initialized store to StarterChatServer
```

Sources: [chatkit/backend/app/server.py:31-36]()

### Step 5: Add Connection Management

**Connection pool lifecycle:**

```mermaid
sequenceDiagram
    participant App as "FastAPI Application"
    participant Store as "PostgresStore"
    participant Pool as "asyncpg Pool"
    participant DB as "PostgreSQL"
    
    App->>Store: __init__(connection_string)
    App->>Store: initialize()
    Store->>Pool: create_pool()
    Pool->>DB: Establish connections
    DB-->>Pool: Connection pool ready
    Pool-->>Store: self.pool = pool
    
    Note over App,DB: Application running, handling requests
    
    loop Each Request
        App->>Store: load_thread_items(...)
        Store->>Pool: async with pool.acquire()
        Pool->>DB: Execute query
        DB-->>Pool: Result
        Pool-->>Store: Return connection to pool
        Store-->>App: Page[ThreadItem]
    end
    
    App->>Store: shutdown()
    Store->>Pool: await pool.close()
    Pool->>DB: Close connections
```

**FastAPI lifecycle integration pattern:**
```python
# Reference pattern for adding startup/shutdown events
# Use FastAPI's lifespan context manager to:
# 1. Initialize database pool on startup
# 2. Close pool on shutdown
```

Sources: FastAPI async database integration best practices

---

## Integration Points Checklist

### Code Locations Requiring Updates

| File | Location | Change Required |
|------|----------|-----------------|
| `chatkit/backend/app/server.py` | [Line 35]() | Replace `MemoryStore()` instantiation with persistent store |
| `chatkit/backend/app/main.py` | Startup handlers | Add database initialization logic |
| `chatkit/backend/requirements.txt` | Dependencies | Add `asyncpg` or database driver |
| `.env.local` | Environment | Add `DATABASE_URL` configuration |

### Environment Variables

Add database connection configuration (see [Production Environment Variables](#8.1)):

```bash
# PostgreSQL example
DATABASE_URL=postgresql://user:password@localhost:5432/chatkit

# Connection pool settings
DB_POOL_MIN_SIZE=10
DB_POOL_MAX_SIZE=20
DB_POOL_TIMEOUT=30
```

### Migration Validation Tests

**Test matrix for verifying Store implementation:**

| Operation | Test Scenario | Expected Behavior |
|-----------|--------------|-------------------|
| `save_thread` | Create new thread | Thread persists after server restart |
| `load_thread` | Retrieve existing thread | Correct metadata returned |
| `load_thread` | Non-existent ID | `NotFoundError` raised |
| `add_thread_item` | Add message to thread | Item retrievable via `load_thread_items` |
| `load_thread_items` | Pagination with `limit=30` | Correct page returned with `has_more` |
| `load_thread_items` | Pagination with `after` cursor | Next page starts after cursor |
| `save_item` | Update existing item | Item content updated in place |
| `delete_thread` | Remove thread | Thread and all items deleted |
| `delete_thread_item` | Remove single item | Item deleted, thread remains |

Sources: [chatkit/backend/app/memory_store.py:19-83]()

---

## Performance Considerations

### Indexing Strategy

**Critical indexes for query performance:**

```sql
-- Thread listing (load_threads operation)
CREATE INDEX idx_threads_created_at ON threads(created_at DESC);

-- Item listing within thread (load_thread_items operation)
CREATE INDEX idx_items_thread_created ON thread_items(thread_id, created_at DESC);

-- Global item ordering (if needed)
CREATE INDEX idx_items_created_at ON thread_items(created_at DESC);
```

### Query Optimization Patterns

**Anti-pattern (causes full table scan):**
```sql
-- Avoid: Sorting all items then filtering
SELECT * FROM thread_items 
WHERE thread_id = $1 
ORDER BY created_at DESC;
```

**Optimal pattern:**
```sql
-- Use composite index for both filtering and sorting
SELECT * FROM thread_items 
WHERE thread_id = $1 
ORDER BY created_at DESC 
LIMIT 30;
```

### Connection Pooling Parameters

**Recommended asyncpg pool configuration:**

| Parameter | Development | Production | Rationale |
|-----------|-------------|------------|-----------|
| `min_size` | 2 | 10 | Minimum idle connections |
| `max_size` | 5 | 50 | Maximum concurrent connections |
| `max_queries` | 50000 | 50000 | Queries before connection recycling |
| `max_inactive_connection_lifetime` | 300 | 300 | Close idle connections after 5 minutes |

**Calculation guidance:**
- `max_size` should account for expected concurrent requests
- At [chatkit/backend/app/server.py:44-50](), each request acquires one connection
- FastAPI default worker count × peak concurrent requests per worker = minimum `max_size`

Sources: asyncpg documentation, database connection pooling best practices

---

## Data Migration Strategy

### Migrating Existing In-Memory Data

If transitioning from a running `MemoryStore` instance:

```mermaid
graph TB
    subgraph "Pre-Migration"
        OldStore["MemoryStore<br/>(In Production)"]
        OldData["self.threads<br/>self.items"]
    end
    
    subgraph "Migration Process"
        Extract["Extract Data<br/>to JSON/CSV"]
        Transform["Transform to<br/>SQL Schema"]
        Load["Load into<br/>Database"]
    end
    
    subgraph "Post-Migration"
        NewStore["PostgresStore<br/>(In Production)"]
        NewData["threads table<br/>thread_items table"]
    end
    
    OldStore --> OldData
    OldData --> Extract
    Extract --> Transform
    Transform --> Load
    Load --> NewData
    NewData --> NewStore
    
    Deploy["Deploy New<br/>Application Version"]
    NewStore --> Deploy
```

**Migration script pattern:**
1. Export data from running `MemoryStore` instance via API endpoint
2. Transform to SQL INSERT statements or CSV for `COPY` command
3. Load into database before deployment
4. Deploy application with `PostgresStore` implementation

### Zero-Downtime Migration

For production systems requiring continuous availability:

1. **Dual-write phase:** Write to both `MemoryStore` and new database
2. **Validation phase:** Compare results from both stores
3. **Cutover phase:** Switch to read-from-database only
4. **Cleanup phase:** Remove `MemoryStore` code

Sources: Database migration best practices

---

## Error Handling Patterns

### Database Connection Failures

**Implement retry logic with exponential backoff:**

```python
# Reference pattern for connection error handling
# Catch asyncpg.exceptions.PostgresConnectionError
# Implement exponential backoff with max retries
# Log connection failures for monitoring
```

### Transaction Management

**For operations requiring atomicity:**

```sql
BEGIN;
INSERT INTO threads (id, created_at, title, metadata) VALUES (...);
INSERT INTO thread_items (id, thread_id, created_at, type, content) VALUES (...);
COMMIT;
```

**Python async transaction pattern:**
```python
# Reference pattern for transaction handling
# Use async with connection.transaction()
# Implement proper rollback on exceptions
```

Sources: asyncpg transaction handling documentation

---

## Testing Strategy

### Unit Tests for Store Implementation

**Test file structure:**
```
chatkit/backend/tests/
├── test_postgres_store.py    # New: Test your implementation
├── test_memory_store.py       # Existing: Reference these patterns
└── fixtures/
    └── test_database.py       # Database setup/teardown
```

**Critical test scenarios:**

```mermaid
graph TB
    subgraph "Thread Tests"
        T1["Create thread<br/>save_thread"]
        T2["Load thread<br/>load_thread"]
        T3["List threads<br/>load_threads"]
        T4["Delete thread<br/>delete_thread"]
    end
    
    subgraph "Item Tests"
        I1["Add item<br/>add_thread_item"]
        I2["Load items<br/>load_thread_items"]
        I3["Paginate items<br/>with after cursor"]
        I4["Update item<br/>save_item"]
        I5["Delete item<br/>delete_thread_item"]
    end
    
    subgraph "Edge Cases"
        E1["NotFoundError<br/>for missing IDs"]
        E2["Pagination<br/>boundary conditions"]
        E3["Concurrent writes<br/>to same thread"]
        E4["Connection pool<br/>exhaustion"]
    end
    
    T1 --> T2 --> T3 --> T4
    I1 --> I2 --> I3 --> I4 --> I5
    E1 & E2 & E3 & E4
```

### Integration Tests

**Test the complete request flow with database:**
1. Start FastAPI application with `PostgresStore`
2. Send chat message via `/chatkit` endpoint (see [StarterChatServer](#3.2.2))
3. Verify message persists in database
4. Restart application
5. Verify conversation history restored correctly

Sources: Testing best practices for async Python applications

---

## Monitoring and Observability

### Key Metrics to Track

| Metric | Purpose | Alert Threshold |
|--------|---------|-----------------|
| Database connection pool utilization | Detect connection exhaustion | >80% for >5 minutes |
| Query latency (p50, p95, p99) | Identify slow queries | p95 >500ms |
| Failed query rate | Database errors | >1% of requests |
| Store operation errors | Application-level failures | Any `NotFoundError` spike |

### Logging Recommendations

**Log at strategic points:**
- Database connection pool initialization
- Query execution with timing
- Pagination cursor generation
- Store method exceptions with context

**Example log structure:**
```python
# Reference pattern for structured logging
logger.info(
    "store_operation",
    operation="load_thread_items",
    thread_id=thread_id,
    limit=limit,
    duration_ms=elapsed_time,
)
```

Sources: Production observability best practices

---

## Summary Checklist

**Before deploying your persistent store implementation:**

- [ ] All 12 Store interface methods implemented
- [ ] Database schema created with appropriate indexes
- [ ] Pagination correctly handles `after` cursor in both `asc` and `desc` order
- [ ] Connection pool configured and lifecycle managed
- [ ] `NotFoundError` raised for missing threads/items
- [ ] Environment variables documented and configured
- [ ] Unit tests verify all CRUD operations
- [ ] Integration tests verify end-to-end flow
- [ ] Migration script prepared (if migrating existing data)
- [ ] Monitoring and alerting configured
- [ ] [chatkit/backend/app/server.py:35]() updated to use new store
- [ ] Dependencies added to requirements.txt
- [ ] Documentation updated with database setup instructions

Sources: [chatkit/backend/app/memory_store.py:1-115](), [chatkit/backend/app/server.py:31-36]()